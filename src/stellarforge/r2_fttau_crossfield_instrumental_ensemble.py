"""Taurus R2: provisional same-filter FT Tau cross-field PSFcat photometry.

Original native ZTF *_psfcat.fits 'mag' is INSTRUMENTAL:
  mag = -2.5 log10(flux in detector DN).
It is NOT a PS1/AB-calibrated magnitude. This independent R2 study
compares same-band, 39-second-apart exposures using an ensemble of
tentatively unique, uncrowded and source-disjoint native catalogue rows.

We deliberately never use FT Tau as a reference, merge OIDs/curves,
or call the derived instrumental offset an absolute zeropoint.
No external standard-star color/PS1 calibration or independent physical
Gaia--ZTF source identification is achieved.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import math
from urllib.error import HTTPError, URLError

from .r2_ft_tau_two_field_fits import FT_GAIA, FT_OIDS, frozen_ft_tau
from .v14_field_review import ztf_science_cutout_url
from .v114_native_psfcat_association import (
    official_psf_product_url, fetch_native_psf_product, parse_psf_fit_catalogue,
)
from .v113_official_masks_psf import BAD_MASK_BITS

MAX_CENTER_DISTANCE_ARCSEC = 360.0
TARGET_EXCLUSION_ARCSEC = 15.
MIN_LOCAL_SEPARATION_ARCSEC = 3.
MAX_PAIR_SOURCE_SEPARATION_ARCSEC = .75
MAX_SIGMAG = .08
MIN_SNR = 20.
MIN_PAIR_REFS = 20
MIN_TRAIN_REFS = 10
MIN_VALIDATION_REFS = 8
MAX_INTERNAL_SCATTER_MAG = .15
MAX_HELDOUT_MEDIAN_ABS_MAG = .07
MIN_POSITIVE_FLUX = 0.
MAX_SOURCE_ROWS_INSPECTED = 120_000
NETWORK_ERRORS = (HTTPError, URLError, TimeoutError, OSError, ValueError,
                  TypeError, OverflowError, ArithmeticError)


def fixed_four_exposure_pairs(seed: bytes, historic: dict,
                              previous_oid: dict, prior_fits: dict) -> tuple[dict,dict]:
    """Only use the exact four previously inspected original g/r sources.

    This is NOT a new science-image selection. An archive change cannot
    redirect the matching experiment to newly convenient exposures.
    """
    ft = frozen_ft_tau(seed, historic, previous_oid)
    if prior_fits.get("original_24_source_seed_sha256") != hashlib.sha256(seed).hexdigest():
        raise ValueError("Original R1 24-source seed SHA changed")
    if (prior_fits.get("n_selected_original_single_science_exposures") != 4
            or prior_fits.get("n_original_image_mask_pairs_checked") != 4
            or prior_fits.get("n_original_native_psfcats_parsed") != 4
            or prior_fits.get("n_selected_original_images_with_all_instrument_checks_passed") != 4
            or prior_fits.get("n_independently_verified_ft_gaia_ztf_physical_crossmatches") != 0
            or prior_fits.get("n_reconciled_or_combined_ztf_lightcurves") != 0):
        raise ValueError("Previous four original image+PSFcat QA evidence differs")
    rows = prior_fits.get("original_fits_mask_native_psf_exposure_results", [])
    if not isinstance(rows,list) or len(rows) != 4:
        raise ValueError("Missing four preselected real-exposure source records")
    by_band: dict[str,dict[str,dict]] = {"g":{},"r":{}}
    expected = {
        ("g","1605"):("1605115300003377",58806.385197,1605,15,3),
        ("g","609"):("609108400001155",58806.385648,609,8,4),
        ("r","1605"):("1605215300005161",58425.306065,1605,15,3),
        ("r","609"):("609208400001969",58425.306516,609,8,4),
    }
    for item in rows:
        sel = item.get("selection",{})
        band = sel.get("band")
        o, mjd, field, ccd, q = expected.get(
            (band,str(sel.get("original_field_ccd_quadrant",[None])[0])),(None,None,None,None,None))
        if o is None or sel.get("ztf_oid") != o or sel.get("original_mjd") != mjd:
            raise ValueError("Previously selected original FT Tau exposure changed")
        if sel.get("original_field_ccd_quadrant") != [field,ccd,q]:
            raise ValueError("Original field/CCD/quadrant selection altered")
        if not isinstance(sel.get("original_filefracday"),str) or len(sel["original_filefracday"])!=14:
            raise ValueError("Invalid original ZTF exposure time key")
        if (item.get("all_three_instrument_source_checks_pass") is not True
                or not isinstance(item.get("native_full_catalogue_sha256"),str)
                or len(item["native_full_catalogue_sha256"]) != 64):
            raise ValueError("Original science-mask-PSFcat quality gate not satisfied")
        area = "1605" if field==1605 else "609"
        if area in by_band[band]:
            raise ValueError("Duplicate original cross-field source frame")
        by_band[band][area] = item
    if any(set(d)!={"1605","609"} for d in by_band.values()):
        raise ValueError("Incomplete exactly four original FT Tau field/band exposure set")
    pairs=prior_fits.get("crossfield_same_filter_pairs",[])
    if len(pairs)!=2 or {x["band"] for x in pairs}!={"g","r"}:
        raise ValueError("Changed crossfield original-image pair selection")
    for p in pairs:
        if not p.get("selected_within_1day") or p.get("selection_mjd_gap_days") != .000451:
            raise ValueError("This original same-night pair provenance changed")
    return ft,by_band


def original_native_catalogue_from_frozen_image(frame: dict, *,
                                                ra:float,dec:float,
                                                native_fetch=fetch_native_psf_product) -> dict:
    """Read and hash-verify EXACTLY same ZTF original psfcat as prior R2.
    
    Entire pixel/image files were independently audited by preceding R2;
    no need to download them again just to estimate instrumental
    source-catalogue flux comparisons.
    """
    sel=frame["selection"]
    f,ccd,q=sel["original_field_ccd_quadrant"]
    row={"filefracday":sel["original_filefracday"],"field":str(f),
         "ccdid":str(ccd),"qid":str(q),"filtercode":"z"+sel["band"]}
    sci=ztf_science_cutout_url(row,ra_center=ra,dec_center=dec,size_arcsec=60)
    url=official_psf_product_url(sci,"psfcat.fits")
    raw=native_fetch(url,kind="psfcat.fits",timeout=24)
    digest=hashlib.sha256(raw).hexdigest()
    if digest != frame["native_full_catalogue_sha256"]:
        raise ValueError("Reobtained native original FITS PSFcat differs from previously checked original exposure SHA-256")
    parsed=parse_psf_fit_catalogue(raw)
    if parsed.get("sha256")!=digest:
        raise ValueError("Original ZTF native PSF catalogue hash verification failed")
    return parsed


def _xy_positions(ra_deg,dec_deg,ra0_deg,dec0_deg):
    """Local tangent-plane RA*cos(dec) and Dec, ARCSECONDS (small field)."""
    import numpy as np
    ra=np.asarray(ra_deg,dtype=float)
    dec=np.asarray(dec_deg,dtype=float)
    dra=(ra-ra0_deg+180.)%360.-180.
    return np.column_stack((dra*np.cos(np.deg2rad(dec0_deg))*3600.,
                            (dec-dec0_deg)*3600.))


def qualifying_original_native_sources(cat:dict,*,ra0:float,dec0:float)->dict:
    """Apply FIXED flag, PSF-fit profile and local geometric cuts.

    Never choose control candidates based on their cross-field magnitude
    differences. All original instrumental magnitudes remain ephemeral.
    """
    import numpy as np
    from scipy.spatial import cKDTree
    if cat.get("status")!="ORIGINAL_ZTF_PSF_CATALOGUE_PARSED_UNVERIFIED":
        raise ValueError("Must be original parsed native ZTF full source catalogue")
    rows=cat["rows"]
    n=len(rows["ra"])
    if n==0 or n>MAX_SOURCE_ROWS_INSPECTED:
        raise ValueError("Empty/oversized original ZTF PSFcat")
    xy=_xy_positions(rows["ra"],rows["dec"],ra0,dec0)
    radius=np.linalg.norm(xy,axis=1)
    infield=np.isfinite(radius)&(radius<=MAX_CENTER_DISTANCE_ARCSEC)
    excluded=np.isfinite(radius)&(radius<TARGET_EXCLUSION_ARCSEC)
    with np.errstate(divide="ignore",invalid="ignore",over="ignore"):
        flags=np.asarray(rows["flags"],dtype=float)
        flux=np.asarray(rows["flux"],dtype=float)
        errflux=np.asarray(rows["sigflux"],dtype=float)
        mag=np.asarray(rows["mag"],dtype=float)
        sigmag=np.asarray(rows["sigmag"],dtype=float)
        snr=np.asarray(rows["snr"],dtype=float)
        chi=np.asarray(rows["chi"],dtype=float)
        sharp=np.asarray(rows["sharp"],dtype=float)
        valid=np.isfinite(flags)&(flags>=0)&(flags==np.floor(flags))
        valid &= np.isfinite(flux)&(flux>MIN_POSITIVE_FLUX)
        valid &= np.isfinite(errflux)&(errflux>0)
        valid &= np.isfinite(mag)&np.isfinite(sigmag)&(sigmag>0)&(sigmag<=MAX_SIGMAG)
        valid &= np.isfinite(snr)&(snr>=MIN_SNR)
        valid &= np.isfinite(chi)&(chi>=.5)&(chi<=1.5)
        valid &= np.isfinite(sharp)&(np.abs(sharp)<=.5)
        valid &= np.abs(mag+2.5*np.log10(np.maximum(flux,1e-100)))<.10
        valid &= np.abs(snr-flux/np.maximum(errflux,1e-100))<=np.maximum(1.,.1*snr)
    intflags=np.zeros(n,dtype=np.int64)
    intflags[np.where(np.isfinite(flags)&(flags>=0)&(flags<2**30))]=flags[
        np.where(np.isfinite(flags)&(flags>=0)&(flags<2**30))].astype(np.int64)
    valid &= (intflags & BAD_MASK_BITS)==0
    # Detect local crowding against *all* detected catalog rows, NOT only
    # quality-passed sources (otherwise nearby bad-fit sources disappear).
    neighbour_dist=cKDTree(xy).query(xy,k=2)[0][:,1]
    isolated=neighbour_dist>=MIN_LOCAL_SEPARATION_ARCSEC
    good=infield&~excluded&valid&isolated
    return {
        "n_catalogue_rows":n,
        "n_within_sky_radius":int(infield.sum()),
        "n_ft_tau_core_excluded":int(excluded.sum()),
        "n_good_uncrowded_reference_candidates":int(good.sum()),
        "xy":xy[good],
        "mag":mag[good],
        "sigmag":sigmag[good],
        "id":np.asarray(rows["sourceid"])[good],
    }


def original_crossfield_reference_pairs(a:dict,b:dict)->dict:
    """Reciprocal nearest-neighbour match, no repeated original PSF source.

    Match based ONLY on sky geometry, native fit/flag quality, and
    crowding -- NOT photometric agreement. Astrometric source matching
    remains provisional, same-pipeline, not an external Gaia crossmatch.
    """
    import numpy as np
    from scipy.spatial import cKDTree
    aa=a["xy"]
    bb=b["xy"]
    if not len(aa) or not len(bb):
        return {"n_reciprocal_sky_matches":0,"n_unique_geometric_pairs":0,
                "delta_native_instrumental_mag_b_minus_a":np.empty(0),
                "nominal_pair_sigma_mag":np.empty(0),"match_xy":np.empty((0,2))}
    an=cKDTree(bb)
    bn=cKDTree(aa)
    abdist,ab=an.query(aa,k=1)
    badist,ba=bn.query(bb,k=1)
    keep=np.flatnonzero(
        (abdist<=MAX_PAIR_SOURCE_SEPARATION_ARCSEC)
        & (ba[ab]==np.arange(len(aa)))
        & (badist[ab]<=MAX_PAIR_SOURCE_SEPARATION_ARCSEC))
    other=ab[keep]
    if len(np.unique(other))!=len(other):
        raise ValueError("Non-unique bidirectional source pair")
    # Potential residual duplicated source sky positions cannot be silently
    # used as independent calibrators.
    return {
        "n_reciprocal_sky_matches":int(len(keep)),
        "n_unique_geometric_pairs":int(len(keep)),
        "delta_native_instrumental_mag_b_minus_a":(
            np.asarray(b["mag"])[other]-np.asarray(a["mag"])[keep]),
        "nominal_pair_sigma_mag":np.hypot(
            np.asarray(a["sigmag"])[keep],np.asarray(b["sigmag"])[other]),
        "match_xy":np.asarray(a["xy"])[keep],
    }


def internal_relative_offset_qc(matched:dict)->dict:
    """Controlled split-half internal validation of a relative instrumental offset.

    A magnitude difference between 39-second exposures for an ensemble of
    common near-constant stars approximates a relative *instrumental* shift.
    It does not establish external PS1 AB calibration or correct FT Tau itself.
    """
    import numpy as np
    dif=np.asarray(matched["delta_native_instrumental_mag_b_minus_a"],dtype=float)
    unc=np.asarray(matched["nominal_pair_sigma_mag"],dtype=float)
    xy=np.asarray(matched["match_xy"],dtype=float)
    n=len(dif)
    base={
        "status":"NO_GO_UNDERPOWERED_OR_INCONSISTENT_NATIVE_ENSEMBLE",
        "native_photometry_units":"instrumental magnitude = -2.5 log10(flux in DN)",
        "n_reciprocal_crowding_screened_geometric_pairs":n,
        "n_training_references":0,
        "n_validation_references":0,
        "ensemble_median_native_mag_difference_b_minus_a":None,
        "heldout_median_relative_offset_mag":None,
        "heldout_robust_scatter_mag":None,
        "instrumental_offset_internally_consistent":False,
        "independent_absolute_photometric_calibration":False,
        "validated_gaia_ztf_physical_source_identity":False,
        "all_photometric_series_remain_unmerged":True,
        "target_itself_excluded_from_reference_ensemble":True,
        "original_ztf_flux_reference_stability_independently_verified":False,
    }
    if n < MIN_PAIR_REFS:
        return base
    if not(np.isfinite(dif).all() and np.isfinite(unc).all() and (unc>0).all()
           and xy.shape==(n,2) and np.isfinite(xy).all()):
        return base
    # Geometry-only reproducible split independent of any photometry.
    # Use relative sky coordinates rounded to 10 mas; SHA-256 parity.
    parity=np.array([
        int.from_bytes(hashlib.sha256(
            (f"{int(round(row[0]*100))},{int(round(row[1]*100))}").encode()
        ).digest()[:4],"big")%2
        for row in xy],dtype=int)
    # If unlikely hash imbalance occurs, deterministically alternate by
    # sorted sky position WITHOUT inspecting flux.
    if min(int((parity==0).sum()),int((parity==1).sum()))<MIN_VALIDATION_REFS:
        idx=np.lexsort((xy[:,1],xy[:,0]))
        parity=np.zeros(n,dtype=int)
        parity[idx[1::2]]=1
    train=dif[parity==0]
    hold=dif[parity==1]
    if len(train)<MIN_TRAIN_REFS or len(hold)<MIN_VALIDATION_REFS:
        return {**base,"n_training_references":len(train),
                "n_validation_references":len(hold)}
    initial=float(np.median(train))
    sigma0=1.4826*float(np.median(np.abs(train-initial)))
    thresh=max(.08,3*sigma0)
    good_train=np.abs(train-initial)<=thresh
    fit=train[good_train]
    if len(fit)<MIN_TRAIN_REFS:
        return {**base,"n_training_references":len(fit),
                "n_validation_references":len(hold)}
    shift=float(np.median(fit))
    fit_scatter=1.4826*float(np.median(np.abs(fit-shift)))
    residual=hold-shift
    hold_median=float(np.median(residual))
    hold_scatter=1.4826*float(np.median(np.abs(residual-hold_median)))
    # This split and scatter are INTERNAL checks only. Calibration against
    # external standards and systematic/colour error budget is still open.
    ok=(fit_scatter<=MAX_INTERNAL_SCATTER_MAG
        and hold_scatter<=MAX_INTERNAL_SCATTER_MAG
        and abs(hold_median)<=MAX_HELDOUT_MEDIAN_ABS_MAG)
    return {
        **base,
        "status":("INTERNAL_ENSEMBLE_CONSISTENCY_PASS_NOT_EXTERNAL_CALIBRATION"
                  if ok else "NO_GO_ENSEMBLE_SCATTER_OR_HELDOUT_BIAS"),
        "n_training_references":int(len(train)),
        "n_training_after_fixed_robust_outlier_screen":int(len(fit)),
        "n_validation_references":int(len(hold)),
        "n_training_outliers_rejected":int(len(train)-len(fit)),
        "ensemble_median_native_mag_difference_b_minus_a":round(shift,5),
        "train_robust_scatter_mag":round(fit_scatter,5),
        "heldout_median_relative_offset_mag":round(hold_median,5),
        "heldout_robust_scatter_mag":round(hold_scatter,5),
        "nominal_median_pair_photometric_sigma_mag":round(float(np.median(unc)),5),
        "instrumental_offset_internally_consistent":bool(ok),
        "independent_absolute_photometric_calibration":False,
        "validated_gaia_ztf_physical_source_identity":False,
        "all_photometric_series_remain_unmerged":True,
    }


def run_ft_tau_two_field_relative_photometry(seed:bytes,historic:dict,prior_oid:dict,
                                              prior_images:dict,*,
                                              native_fetch=fetch_native_psf_product)->dict:
    fixed,by_band=fixed_four_exposure_pairs(seed,historic,prior_oid,prior_images)
    per_band=[]
    for band in ("g","r"):
        source_meta=[]
        chosen=[]
        try:
            for area in ("1605","609"):
                frame=by_band[band][area]
                c=original_native_catalogue_from_frozen_image(
                    frame,ra=fixed["seed_ra_deg"],dec=fixed["seed_dec_deg"],
                    native_fetch=native_fetch)
                q=qualifying_original_native_sources(
                    c,ra0=fixed["seed_ra_deg"],dec0=fixed["seed_dec_deg"])
                source_meta.append({
                    "original_ztf_oid":frame["selection"]["ztf_oid"],
                    "original_source_field":area,
                    "original_mjd":frame["selection"]["original_mjd"],
                    "original_native_catalogue_sha256":c["sha256"],
                    "n_original_native_source_rows":q["n_catalogue_rows"],
                    "n_in_fixed_360arcsec_sky_radius":q["n_within_sky_radius"],
                    "n_excluded_ft_tau_core":q["n_ft_tau_core_excluded"],
                    "n_preselected_clean_uncrowded_native_candidates":
                        q["n_good_uncrowded_reference_candidates"],
                })
                chosen.append(q)
            matching=original_crossfield_reference_pairs(*chosen)
            qc=internal_relative_offset_qc(matching)
            result_status=qc["status"]
        except NETWORK_ERRORS as exc:
            qc={
                "status":"ORIGINAL_NATIVE_PSF_SOURCE_DATA_UNAVAILABLE_OR_CHANGED",
                "error_type":type(exc).__name__,
                "instrumental_offset_internally_consistent":False,
                "independent_absolute_photometric_calibration":False,
                "validated_gaia_ztf_physical_source_identity":False,
                "all_photometric_series_remain_unmerged":True,
                "target_itself_excluded_from_reference_ensemble":True,
            }
            if isinstance(exc,HTTPError):
                qc["http_status"]=int(exc.code)
            result_status=qc["status"]
        per_band.append({
            "band":band,
            "original_field_1605_and_609_exposure_mjd_gap_days":.000451,
            "native_psfcat_original_data_records":source_meta,
            "native_source_crossfield_ensemble":qc,
            "status":result_status,
            "ref_photometric_stability_not_externally_certified":True,
            "not_a_crossfilter_photometric_calibration":True,
            "physical_ft_tau_gaia_ztf_crossmatch_authenticated":False,
            "ft_tau_ztf_original_lightcurves_combined":False,
        })
    return {
        "phase":"TAURUS_R2_FTTAU_ORIGINAL_SAME_FILTER_TWO_FIELD_NATIVE_INSTRUMENTAL_ENSEMBLE",
        "original_nonrepresentative_taurus_gaia_seed_count":24,
        "n_fixed_ft_tau_ztf_oids":4,
        "n_original_ztf_historical_science_exposures":4,
        "n_new_original_science_exposures_selected":0,
        "n_native_original_psf_catalogues_exactly_sha_verified":sum(
            len(x["native_psfcat_original_data_records"]) for x in per_band),
        "n_same_band_ensemble_internal_qc_passes":sum(
            x["native_source_crossfield_ensemble"].get(
                "instrumental_offset_internally_consistent",False)
            for x in per_band),
        "n_same_band_ensembles_evaluated":sum(
            x["native_source_crossfield_ensemble"]["status"] not in
            ("ORIGINAL_NATIVE_PSF_SOURCE_DATA_UNAVAILABLE_OR_CHANGED",)
            for x in per_band),
        "n_verified_external_photometric_standard_zeropoints":0,
        "n_physical_gaia_ztf_source_identities_confirmed":0,
        "n_original_ztf_oid_lightcurves_merged":0,
        "n_confirmed_new_intrinsic_ft_tau_variability_or_companions":0,
        "scientific_r2_complete":False,
        "original_r1_seed_sha256":hashlib.sha256(seed).hexdigest(),
        "prior_original_fits_evidence_sha256":None,  # populated by runner
        "bands":per_band,
        "limitations":[
            "Original ZTF native PSFcat mag is instrumental -2.5log10(DN flux), not PS1/AB calibrated; median difference is not a physical magnitude calibration.",
            "Cross-field source matching uses same ZTF pipeline WCS rather than independently authenticated Gaia/PS1 standards; false matches are possible.",
            "Field ensemble only has one 39-second original exposure per detector field per band; no multi-night stable-star reference validation.",
            "Outlier clipping does not prove all surviving reference stars have fixed intrinsic flux, consistent color or lack of blended neighbours.",
            "External photometric zero-point, colour terms and propagation of systematic uncertainties, cross-field detector dependence and astrophysical source attribution remain unverified.",
            "Even when internally consistent, NEVER automatically merge the four historical ZTF OID lightcurves or claim FT Tau variability.",
        ],
    }
