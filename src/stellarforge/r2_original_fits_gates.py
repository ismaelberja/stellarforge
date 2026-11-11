"""Taurus R2: original same-exposure ZTF FITS/mask/PSFcat crowding audit.

Exactly four *pre-existing historic* ZTF g-band exposures (FT Tau and
CIDA 11; two dates per target), previously reported by StellarForge.
Original metadata from one direct ZTF OID+MJD query per exposure reconstructs
the science-product path; no new exposure is chosen after looking at images.

This establishes only original source products, WCS/mask agreement,
native-catalogue crowding and tentative peak geometry. It does NOT
independently calibrate ZTF WCS, prove Gaia-to-ZTF physical identity,
resolve blended stars, or discover variable stars/companions.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import math
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .coordinates import angular_separation_arcsec, validate_icrs
from .v14_field_review import ztf_science_cutout_url
from .v15_image_pixels import fetch_fits_cutout, inspect_fits_cutout
from .v113_official_masks_psf import (
    official_ancillary_url, fetch_ancillary_fits, inspect_mask_against_science,
)
from .v114_native_psfcat_association import (
    official_psf_product_url, fetch_native_psf_product, parse_psf_fit_catalogue,
)
from .v19_gaia_covariance import (
    fetch_gaia_astrometry, parse_gaia_astrometry, propagate_gaia_5p_formal,
)
from .ztf_photometry import parse_ztf_table

IRSA_LC="https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves"
MAX_EXPOSURES=4
MAX_METADATA_BYTES=450_000
MJD_TOLERANCE_DAYS=0.000020
REQUIRED_FIELDS={"oid","mjd","filefracday","field","filtercode","ccdid","qid","catflags"}
ERRORS=(HTTPError,URLError,TimeoutError,OSError,ValueError,TypeError,OverflowError)

def validate_historic_exposures(seed:bytes, ledger:dict)->tuple[dict, list[dict]]:
    import csv
    import io
    rows=list(csv.DictReader(io.StringIO(seed.decode("utf-8-sig"))))
    if len(rows)!=24 or len({r["gaia"] for r in rows})!=24:
        raise ValueError("The original 24 Taurus technical sources have changed")
    original={r["gaia"]:r for r in rows}
    frames=ledger.get("exposures")
    if (not isinstance(frames,list) or len(frames)!=MAX_EXPOSURES
            or ledger.get("provenance",{}).get("original_json_sha256") !=
            "fb7d5c315cbef56b2551e73920c67920827d91160b4c0bd35f3fd77113166beb"):
        raise ValueError("Historical actual ZTF exposure ledger/provenance changed")
    expect={("149623711269425408","1605115300003377",58388.389016),
            ("149623711269425408","1605115300003377",58491.184780),
            ("3419110734340795648","610106300008010",58475.113750),
            ("3419110734340795648","610106300008010",58849.135984)}
    actual={(str(f["target_gaia_id"]),str(f["oid"]),float(f["mjd"])) for f in frames}
    if actual!=expect or any(f["band"]!="zg" for f in frames):
        raise ValueError("Cannot add/postselect an original ZTF science exposure")
    return original, frames


def metadata_request_url(oid:str,mjd:float)->str:
    if not isinstance(oid,str) or not oid.isascii() or not oid.isdigit() or not oid:
        raise ValueError("Non-original or malformed ZTF OID")
    if not math.isfinite(mjd) or not 58000<mjd<61000:
        raise ValueError("Original ZTF science date outside supported range")
    return IRSA_LC+"?"+urlencode({
        "ID":oid,"TIME":f"{mjd-.000050:.6f} {mjd+.000050:.6f}",
        "FORMAT":"csv"})


def fetch_single_exposure_metadata(oid:str,mjd:float,*,
                                   timeout:float=22,opener=urlopen)->bytes:
    if not 5<=timeout<=40:
        raise ValueError("Unbounded original metadata query")
    url=metadata_request_url(oid,mjd)
    with opener(Request(url,headers={"User-Agent":"StellarForge/2.0 Taurus R2 historic image audit",
                                  "Accept":"text/csv,text/plain"},method="GET"),
                timeout=timeout) as response:
        payload=response.read(MAX_METADATA_BYTES+1)
    if not payload or len(payload)>MAX_METADATA_BYTES:
        raise ValueError("Original direct-OID exposure metadata empty or oversized")
    return payload


def fixed_exposure_metadata(payload:bytes,*,oid:str,mjd:float)->dict:
    if not isinstance(payload,bytes) or not payload or len(payload)>MAX_METADATA_BYTES:
        raise ValueError("Invalid original metadata response")
    rows,fmt=parse_ztf_table(payload)
    if fmt!="csv":
        raise ValueError("Exact ZTF exposure metadata must be CSV")
    matches=[]
    for r in rows:
        if not REQUIRED_FIELDS.issubset(r):
            raise ValueError("Original ZTF exposure metadata fields missing")
        if str(r["oid"])!=oid:
            raise ValueError("Direct OID response contained another source")
        if str(r["filtercode"]).lower()!="zg":
            continue
        try:
            tm=float(r["mjd"])
        except (ValueError,TypeError) as exc:
            raise ValueError("Non-numeric source MJD") from exc
        if math.isfinite(tm) and abs(tm-mjd)<=MJD_TOLERANCE_DAYS:
            matches.append(r)
    if len(matches)!=1:
        raise ValueError("Exact historical original ZTF exposure must occur exactly once")
    return {
        "metadata_sha256":hashlib.sha256(payload).hexdigest(),
        "original_matching_mjd":round(float(matches[0]["mjd"]),6),
        "row":matches[0],
        "n_direct_oid_rows_in_window":len(rows),
    }


def independent_native_psfcat_neighbours(catalogue:dict, *,
                                         ra:float,dec:float)->dict:
    """Neighbour distances in original native ZTF survey PSF-fit catalogue.

    It is NOT an independent external catalogue or physical source match.
    The per-exposure native catalogue includes pipeline source positions and
    can miss unresolved blends, nebulosity and poor-quality PSF detections.
    """
    import numpy as np
    validate_icrs(ra,dec)
    if catalogue.get("status")!="ORIGINAL_ZTF_PSF_CATALOGUE_PARSED_UNVERIFIED":
        raise ValueError("Original native psfcat must have data")
    rows=catalogue["rows"]
    ras=np.asarray(rows["ra"],dtype=float)
    decs=np.asarray(rows["dec"],dtype=float)
    if ras.ndim!=1 or len(ras)!=len(decs) or not len(ras):
        raise ValueError("PSF catalogue position arrays not usable")
    # Vectorized stable separation (same per-exposure source namespace).
    from .v114_native_psfcat_association import _sep_arcsec_vectorized
    distances=_sep_arcsec_vectorized(ras,decs,ra,dec)
    nearest=np.argsort(distances)[:8]
    primary=int(nearest[0])
    min_sep=float(distances[primary])
    radii=(1.,2.,3.,5.,10.)
    counts={f"n_psfcat_rows_within_{int(r)}arcsec":int(np.sum(distances<=r))
            for r in radii}
    n_close_secondary=int(np.sum(
        (distances<=3.) & (np.arange(len(distances))!=primary)))
    nearest_survey_sourceid=int(rows["sourceid"][primary])
    valid_primary=min_sep<=1.
    if not valid_primary:
        status="NO_NEARBY_NATIVE_PSF_SOURCE_WITHIN_1ARCSEC"
    elif n_close_secondary:
        status="NATIVE_SOURCE_WITH_ADDITIONAL_3ARCSEC_PSF_CATALOGUE_NEIGHBOURS"
    else:
        status="ONE_NATIVE_PSF_CATALOGUE_CANDIDATE_NO_OTHER_WITHIN_3ARCSEC"
    return {
        "status":status,
        "nearest_native_sourceid":nearest_survey_sourceid if valid_primary else None,
        "nearest_native_psfcat_offset_arcsec":round(min_sep,5),
        **counts,
        "n_additional_native_psfcat_sources_within_3arcsec":n_close_secondary,
        "second_nearest_native_psfcat_offset_arcsec":(
            round(float(distances[nearest[1]]),5) if len(nearest)>1 else None),
        "native_psfcat_total_sources":int(len(ras)),
        "native_psfcat_sha256":catalogue["sha256"],
        "original_native_catalogue_is_not_independent_physical_crossmatch":True,
        "independently_verified_gaia_to_ztf_counterpart":False,
        "unresolved_blends_excluded":False,
    }


def inspect_fixed_original_frame(frame:dict, gaia_row:dict, *,
                                 metadata_fetch=fetch_single_exposure_metadata,
                                 native_fetch=fetch_native_psf_product,
                                 sci_fetch=fetch_fits_cutout,
                                 mask_fetch=fetch_ancillary_fits)->dict:
    """All providers original; error per step retained, no fake non-detection."""
    name=str(frame["target"])
    oid=str(frame["oid"])
    mjd=float(frame["mjd"])
    sid=str(frame["target_gaia_id"])
    record={
        "historical_target_label":name,"gaia_dr3_id":sid,
        "historic_ztf_oid":oid,"original_science_mjd":round(mjd,6),
        "historical_science_epoch_frozen":True,
        "source_physical_identity_confirmed":False,
        "native_psfcat_neighbours":"NOT_CHECKED",
        "science_mask_image":"NOT_CHECKED",
        "full_r2_physical_association_completed":False,
    }
    def fail(step,exc):
        result={"status":"ORIGINAL_ARCHIVE_REQUEST_OR_VALIDATION_FAILED",
                "error_type":type(exc).__name__}
        if isinstance(exc,HTTPError):result["http_status"]=int(exc.code)
        record[step]=result
    try:
        raw=metadata_fetch(oid,mjd)
        anchor=fixed_exposure_metadata(raw,oid=oid,mjd=mjd)
        record["original_exact_oid_metadata_sha256"]=anchor["metadata_sha256"]
        record["original_metadata"]="EXACT_HISTORIC_OID_AND_DATE_FOUND"
        pred=propagate_gaia_5p_formal(gaia_row,mjd_utc=mjd)
        record["gaia_ruwe"]=pred["gaia_ruwe"]
        record["gaia_astrometric_quality_warning"]=pred["high_or_missing_ruwe_quality_warning"]
        ra=pred["geocentric_parallax_adjusted_ra_deg"]
        dec=pred["geocentric_parallax_adjusted_dec_deg"]
        url=ztf_science_cutout_url(anchor["row"],ra_center=ra,dec_center=dec,
                                    size_arcsec=60)
        record["original_science_filename"]=url.split("/")[-1].split("?")[0]
        record["original_source_cutout_sha256_url"]=hashlib.sha256(url.encode()).hexdigest()
    except ERRORS as exc:
        fail("original_metadata",exc)
        return record
    try:
        native_url=official_psf_product_url(url,"psfcat.fits")
        raw_native=native_fetch(native_url,kind="psfcat.fits",timeout=18)
        cat=parse_psf_fit_catalogue(raw_native)
        record["native_psfcat_neighbours"]=independent_native_psfcat_neighbours(
            cat,ra=ra,dec=dec)
    except ERRORS as exc:
        fail("native_psfcat_neighbours",exc)
    try:
        mask_url=official_ancillary_url(url,"mskimg.fits")
        raw_mask=mask_fetch(mask_url,kind="mskimg.fits",timeout=16)
        raw_sci=sci_fetch(url,timeout=18)
        mask=inspect_mask_against_science(
            raw_sci,raw_mask,expected_ra_deg=ra,expected_dec_deg=dec)
        px=inspect_fits_cutout(raw_sci,expected_ra_deg=ra,expected_dec_deg=dec)
        record["science_mask_image"]={
            "science_image_status":px["status"],
            "original_science_fits_sha256":hashlib.sha256(raw_sci).hexdigest(),
            "original_mask_fits_sha256":hashlib.sha256(raw_mask).hexdigest(),
            "science_image_wcs_checked":px.get("wcs_checked",False),
            "n_additional_image_local_maxima_within_12arcsec":
                px.get("n_additional_local_maxima_within_12_arcsec"),
            "central_local_maximum_detected":px.get("central_local_maximum_detected"),
            "central_local_maximum_offset_arcsec":px.get("central_peak_offset_arcsec"),
            "original_science_mask_status":mask["status"],
            "source_core_bad_mask_pixels":mask.get("n_core_bad_mask_pixels"),
            "source_core_saturated_mask_pixels":mask.get("n_core_saturated_mask_pixels"),
            "image_mask_alignment_verified":mask.get("wcs_checked_and_aligned",False),
            "image_peaks_are_not_confirmed_companions":True,
            "physical_source_id_independently_verified":False,
            "instrument_psf_or_wcs_calibrated":False,
        }
    except ERRORS as exc:
        fail("science_mask_image",exc)
    return record


def run_fixed_fttau_cida_original_images(seed_bytes:bytes, ledger:dict, *,
                                          gaia_fetch=fetch_gaia_astrometry,
                                          frame_inspector=inspect_fixed_original_frame)->dict:
    seed,frames=validate_historic_exposures(seed_bytes,ledger)
    ids=tuple(sorted({f["target_gaia_id"] for f in frames}))
    raw=gaia_fetch(ids,timeout_sec=30)
    formal=parse_gaia_astrometry(raw,expected_ids=ids)
    result=[]
    for frame in frames:
        result.append(frame_inspector(frame,formal[frame["target_gaia_id"]]))
    return {
        "phase":"R2_FT_TAU_CIDA_11_ORIGINAL_4_FITS_MASK_NATIVE_CROWDING_NOT_PHYSICAL_CROSSMATCH",
        "source":"Original NASA/IPAC ZTF dated science FITS, corresponding bitmasks and full per-exposure native PSF source catalogues",
        "original_technical_cohort_count":24,
        "original_target_count":2,
        "historic_original_exposure_count":4,
        "n_metadata_exact_historic_exposures_found":sum(
            x["original_metadata"]=="EXACT_HISTORIC_OID_AND_DATE_FOUND" for x in result),
        "n_original_native_psfcat_crowding_evaluations":sum(
            isinstance(x["native_psfcat_neighbours"],dict) and
            x["native_psfcat_neighbours"].get("original_native_catalogue_is_not_independent_physical_crossmatch",False)
            for x in result),
        "n_original_science_mask_image_pairs_evaluated":sum(
            isinstance(x["science_mask_image"],dict) and
            x["science_mask_image"].get("original_science_mask_status","").startswith("MASK_CORE")
            for x in result),
        "n_original_frames_with_additional_native_psfcat_source_within_3arcsec":sum(
            isinstance(x["native_psfcat_neighbours"],dict) and
            x["native_psfcat_neighbours"].get("n_additional_native_psfcat_sources_within_3arcsec",0)>0
            for x in result),
        "n_independently_authenticated_gaia_ztf_physical_sources":0,
        "new_astrophysical_companions_or_variable_stars_confirmed":0,
        "four_original_frames_not_new_observation_epochs":True,
        "all_24_study_source_identifications_completed":False,
        "r2_science_completed":False,
        "gaia_original_raw_response_sha256":hashlib.sha256(raw).hexdigest(),
        "r1_frozen_seed_sha256":hashlib.sha256(seed_bytes).hexdigest(),
        "frames":result,
        "limitations":[
            "Original native ZTF psfcat is from the same reduction pipeline as the science-image FITS WCS, not an independent calibration catalogue.",
            "Gaia DR3 formal errors omit survey and non-single-star systematic terms, and no topocentric apparent positions are modelled.",
            "No physical Gaia-ZTF source identity is certified by proximity of a native source or a science-image peak.",
            "No deblending, physical companion detection, new stellar variability, survey-wide incidence or publisher Luhman membership validation is performed.",
            "Four fixed previously used original ZTF historical exposures, not newly acquired astronomical epochs.",
        ]
    }
