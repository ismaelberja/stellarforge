"""FT Tau R2: frozen Gaia motion, external PS1 source and four ZTF centroids.

This pilot checks genuine original source-position consistency and
reproducibility, NOT independent instrument calibration or a proven
physical Gaia-to-ZTF stellar identity. Original PS1 and native ZTF
source rows remain in-memory and never enter committed evidence.
"""
from __future__ import annotations

import csv
import hashlib
import io
import math
from urllib.error import HTTPError, URLError

from .r2_fttau_crossfield_instrumental_ensemble import (
    fixed_four_exposure_pairs, original_native_catalogue_from_frozen_image,
    qualifying_original_native_sources, _xy_positions,
)
from .r2_fttau_external_ps1 import (
    fetch_external_ps1_mean_sources, parse_ps1_original_mean,
    _split_indices, PS1_MAX_BYTES, PS1_PAGESIZE,
)
from .v19_gaia_covariance import (
    fetch_gaia_astrometry, parse_gaia_astrometry, propagate_gaia_5p_formal,
)
from .v113_official_masks_psf import BAD_MASK_BITS
from .r2_ft_tau_two_field_fits import FT_GAIA

# Fixed before this study queried new original archive sources.
ZTF_PAIR_MAX_ARCSEC = .75
PS1_TRIPLET_MAX_ARCSEC = .6
FT_TARGET_MAX_ARCSEC = .6
FT_TARGET_SECOND_MIN_ARCSEC = 1.
FT_NEIGHBOUR_SEARCH_ARCSEC = 2.
EXTERNAL_TARGET_PS1_SEARCH_ARCSEC = 3.
MIN_TRAIN = 10
MIN_HOLDOUT = 8
MIN_REFERENCE_TRIPLES = 20
MAX_HELDOUT_MEDIAN_ABS_ARCSEC = .10
MAX_HELDOUT_ROBUST_SCATTER_ARCSEC = .15
NETWORK_ERRORS = (HTTPError,URLError,TimeoutError,OSError,ValueError,
                  TypeError,OverflowError,ArithmeticError,UnicodeError)


def _sky_offset_arcsec(ra, dec, center_ra, center_dec):
    """Signed ICRS tangent-plane offsets with RA wrap and cos(Dec)."""
    return _xy_positions([ra],[dec],center_ra,center_dec)[0]


def full_original_ps1_near_target(raw:bytes, gaia_row:dict,
                                  predictions:dict[str,dict])->dict:
    """Include PS1 photometrically excluded sources near target, nDet>=5.

    This additional target check NEVER reuses the 15" excluded
    calibration references as a physically verified target match.
    PS1 mean RA/Dec have no modelled per-source observation epoch.
    """
    import numpy as np
    if not isinstance(raw, bytes) or not raw or len(raw)>PS1_MAX_BYTES:
        raise ValueError("Invalid original MAST PS1 source bytes")
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    if not reader.fieldnames or not {"objID","raMean","decMean"}.issubset(reader.fieldnames):
        raise ValueError("PS1 target-ambiguity source coordinates missing")
    coords=[]
    ids=set()
    for row in reader:
        sid=str(row["objID"]).strip()
        if sid in ids or not sid.isdigit():
            raise ValueError("Duplicate or invalid PS1 source within original cone")
        ids.add(sid)
        try:
            ra=float(row["raMean"])
            dec=float(row["decMean"])
        except (TypeError,ValueError):
            raise ValueError("Unparseable original PS1 target-neighbour coordinate")
        if not all(map(math.isfinite,(ra,dec))) or not 0<=ra<360 or not -90<=dec<=90:
            raise ValueError("Invalid original PS1 source sky coordinates")
        coords.append((ra,dec))
        if len(coords)>=PS1_PAGESIZE:
            raise ValueError("Original PS1 cone may be truncated")
    if not coords:
        raise ValueError("No PS1 original rows")
    ra=np.array([x[0] for x in coords])
    dec=np.array([x[1] for x in coords])
    checks={
        "gaia_J2016_reference_epoch":(float(gaia_row["ra"]),float(gaia_row["dec"])),
    }
    for band,prediction in predictions.items():
        # A single same-filter reference field's position is sufficient
        # to compare Gaia's epoch difference for a conservative PS1
        # ambiguity screen, not a PS1 proper-motion solution.
        p=prediction["1605"]
        checks[f"{band}_original_ztf_epoch_gaia_propagated"]=(
            p["geocentric_parallax_adjusted_ra_deg"],
            p["geocentric_parallax_adjusted_dec_deg"],
        )
    out={}
    for epoch,(gra,gdec) in checks.items():
        delta=_xy_positions(ra,dec,gra,gdec)
        sep=np.linalg.norm(delta,axis=1)
        vals=np.sort(sep)
        out[epoch]={
            "nearest_original_ps1_mean_position_offset_arcsec":round(float(vals[0]),6),
            "second_original_ps1_mean_position_offset_arcsec":(
                round(float(vals[1]),6) if len(vals)>1 else None),
            "n_original_ps1_sources_within_1arcsec":int(np.sum(sep<=1.)),
            "n_original_ps1_sources_within_3arcsec":int(np.sum(
                sep<=EXTERNAL_TARGET_PS1_SEARCH_ARCSEC)),
            "ps1_astrometric_epoch_and_source_pm_unknown":True,
            "may_omit_PS1_sources_with_lt5_mean_detections":True,
            "gaia_to_ztf_ps1_physical_target_source_id_confirmed":False,
        }
    return {
        "n_all_original_ps1_mean_source_positions_reviewed":len(coords),
        "original_target_neighborhood":out,
        "independent_catalogue_source_ambiguity_excluded":False,
        "ps1_mean_epoch_or_proper_motion_propagated":False,
    }


def original_reference_triple_astrometry(ref_a:dict,ref_b:dict,ps1:dict)->dict:
    """Original ZTF/ZTF/PS1 mutual source identities, source geometry only.

    Strictly same uniqueness/tolerances as the previously preregistered
    external PS1 color-source reference pilot. Do not select based on
    positional residuals or magnitudes.
    """
    import numpy as np
    from scipy.spatial import cKDTree

    a=np.asarray(ref_a["xy"],dtype=float)
    b=np.asarray(ref_b["xy"],dtype=float)
    p=np.asarray(ps1["xy"],dtype=float)
    empty={
        "n_unique_source_triplets":0,"ps1_ids":np.array([],dtype=str),
        "field_1605_xy_arcsec":np.empty((0,2)),
        "field_609_xy_arcsec":np.empty((0,2)),
        "ps1_mean_xy_arcsec":np.empty((0,2)),
    }
    if min(len(a),len(b),len(p))==0:
        return empty
    ad,ai=cKDTree(b).query(a)
    bd,bi=cKDTree(a).query(b)
    idx=np.arange(len(a))
    same=np.flatnonzero((ad<=ZTF_PAIR_MAX_ARCSEC)
                        &(bi[ai]==idx)&(bd[ai]<=ZTF_PAIR_MAX_ARCSEC))
    if len(same)==0:return empty
    pd,pi=cKDTree(p).query(a[same])
    second=b[ai[same]]
    ds=np.linalg.norm(p[pi]-second,axis=1)
    back,backidx=cKDTree(a[same]).query(p)
    keep=(pd<=PS1_TRIPLET_MAX_ARCSEC)&(ds<=PS1_TRIPLET_MAX_ARCSEC)
    keep&=(back[pi]<=PS1_TRIPLET_MAX_ARCSEC)
    keep&=(backidx[pi]==np.arange(len(same)))
    retained=same[keep]
    pidx=pi[keep]
    sid=ps1["id"][pidx]
    if len(set(sid))!=len(sid):
        raise ValueError("Duplicate independent PS1 source in native reference triplets")
    return {
        "n_unique_source_triplets":int(len(retained)),
        "ps1_ids":sid,
        "field_1605_xy_arcsec":a[retained],
        "field_609_xy_arcsec":b[ai[retained]],
        "ps1_mean_xy_arcsec":p[pidx],
    }


def heldout_astrometric_reference_offsets(triples:dict)->dict:
    """Holdout *instrumental catalogue alignment*, not a WCS covariance.

    PS1 source mean epoch, source PM, PSF blending and Gaia target
    systematics are missing; a small residual does not authenticate
    Gaia/ZTF physical identity.
    """
    import numpy as np
    n=triples["n_unique_source_triplets"]
    base={
        "status":"NO_GO_UNDERPOWERED_OR_INCONSISTENT_REFERENCE_ASTROMETRY",
        "n_original_unique_external_ps1_ztf_ztf_triplets":n,
        "n_training_reference_stars":0,
        "n_heldout_reference_stars":0,
        "fields":{},
        "both_fields_heldout_internal_geometry_pass":False,
        "independent_external_PS1_source_positions_used":True,
        "target_gaia_ztf_physical_identity_authenticated":False,
        "full_instrument_wcs_uncertainty_calibrated":False,
    }
    if n<MIN_REFERENCE_TRIPLES:return base
    ids=triples["ps1_ids"]
    if len(set(ids))!=n:
        raise ValueError("Nonunique external source IDs in PS1 astrometric controls")
    train=_split_indices(ids)==0
    held=~train
    if train.sum()<MIN_TRAIN or held.sum()<MIN_HOLDOUT:return base
    ps1=np.asarray(triples["ps1_mean_xy_arcsec"],dtype=float)
    results={}
    for field in ("1605","609"):
        ztf=np.asarray(triples["field_"+field+"_xy_arcsec"],dtype=float)
        if ztf.shape!=ps1.shape or not np.isfinite(ztf).all() or not np.isfinite(ps1).all():
            raise ValueError("Nonfinite or malformed reference original sky positions")
        e=ztf-ps1
        reference=np.median(e[train],axis=0)
        residual=e[held]-reference
        med=np.median(residual,axis=0)
        scatter=1.4826*np.median(np.abs(residual-med),axis=0)
        ok=(np.all(np.abs(med)<=MAX_HELDOUT_MEDIAN_ABS_ARCSEC)
            and np.all(scatter<=MAX_HELDOUT_ROBUST_SCATTER_ARCSEC))
        results[field]={
            "median_original_ztf_minus_ps1_reference_training_east_arcsec":round(float(reference[0]),6),
            "median_original_ztf_minus_ps1_reference_training_north_arcsec":round(float(reference[1]),6),
            "heldout_east_median_arcsec":round(float(med[0]),6),
            "heldout_north_median_arcsec":round(float(med[1]),6),
            "heldout_east_robust_scatter_arcsec":round(float(scatter[0]),6),
            "heldout_north_robust_scatter_arcsec":round(float(scatter[1]),6),
            "heldout_reference_geometry_internal_qc_pass":bool(ok),
            "ps1_reference_source_astrometric_epochs_unchanged":False,
            "scientifically_complete_wcs_calibration":False,
        }
    allpass=all(x["heldout_reference_geometry_internal_qc_pass"]
                for x in results.values())
    return {
        **base,
        "status":("INTERNAL_PS1_REFERENCE_GEOMETRY_HELDOUT_PASS_NOT_WCS_CERTIFICATION"
                  if allpass else "NO_GO_REFERENCE_GEOMETRIC_SCATTER_OR_HELDOUT_OFFSET"),
        "n_training_reference_stars":int(train.sum()),
        "n_heldout_reference_stars":int(held.sum()),
        "fields":results,
        "both_fields_heldout_internal_geometry_pass":bool(allpass),
    }


def original_target_native_candidate(native:dict, pred:dict)->dict:
    """Four fixed original exposures: one nearest, independent quality flags.

    Do not claim a physical star merely from angular proximity to Gaia.
    """
    import numpy as np
    from .v114_native_psfcat_association import _sep_arcsec_vectorized
    rows=native["rows"]
    if native["status"]!="ORIGINAL_ZTF_PSF_CATALOGUE_PARSED_UNVERIFIED":
        raise ValueError("Missing original native ZTF source positions")
    sep=_sep_arcsec_vectorized(rows["ra"],rows["dec"],
                              pred["geocentric_parallax_adjusted_ra_deg"],
                              pred["geocentric_parallax_adjusted_dec_deg"])
    order=np.argsort(sep)
    if len(order)==0:
        raise ValueError("Original native catalogue empty")
    first=int(order[0])
    nearest=float(sep[first])
    second=float(sep[int(order[1])]) if len(order)>1 else None
    close=int(np.sum(sep<=FT_NEIGHBOUR_SEARCH_ARCSEC))
    selected=(nearest<=FT_TARGET_MAX_ARCSEC
              and (second is None or second>FT_TARGET_SECOND_MIN_ARCSEC))
    snr=float(rows["snr"][first])
    flux=float(rows["flux"][first])
    sigflux=float(rows["sigflux"][first])
    chi=float(rows["chi"][first])
    sharp=float(rows["sharp"][first])
    flags=int(rows["flags"][first])
    profile=(snr>=5 and flux>0 and sigflux>0
             and .5<=chi<=1.5 and -.5<=sharp<=.5
             and flags>=0 and (flags&BAD_MASK_BITS)==0)
    offset=_sky_offset_arcsec(float(rows["ra"][first]),float(rows["dec"][first]),
                              pred["geocentric_parallax_adjusted_ra_deg"],
                              pred["geocentric_parallax_adjusted_dec_deg"])
    good=bool(selected and profile)
    return {
        "status":("PROVISIONAL_GAIA_NEAREST_ZTF_PSF_SOURCE_GEOMETRY_PASS"
                  if good else "TARGET_PSF_SOURCE_AMBIGUOUS_OR_QUALITY_REVIEW"),
        "n_original_native_psf_sources_within_2arcsec":close,
        "nearest_original_native_source_to_predicted_Gaia_arcsec":round(nearest,6),
        "second_nearest_original_native_source_arcsec":(
            round(second,6) if second is not None else None),
        "selected_nearest_original_native_PSF_quality_pass":bool(profile),
        "unique_within_fixed_0p6arcsec_second_beyond_1arcsec":bool(selected),
        "original_native_minus_propagated_gaia_east_arcsec":round(float(offset[0]),6),
        "original_native_minus_propagated_gaia_north_arcsec":round(float(offset[1]),6),
        "instrument_wcs_and_psf_errors_not_in_gaia_formal_covariance":True,
        "confirmed_physical_gaia_ztf_target":False,
    }


def target_differential_reference_summary(target:dict,reference:dict,field:str)->dict:
    """Descriptive PS1-relative native target residual; never a PM solution."""
    out={
        "status":"NO_GO_TARGET_OR_REFERENCE_REQUIRED",
        "external_reference_adjusted_target_east_arcsec":None,
        "external_reference_adjusted_target_north_arcsec":None,
        "independent_instrument_wcs_solution":False,
        "source_physical_gaia_ztf_identity_confirmed":False,
    }
    if (target.get("status")!="PROVISIONAL_GAIA_NEAREST_ZTF_PSF_SOURCE_GEOMETRY_PASS"
        or not reference.get("both_fields_heldout_internal_geometry_pass")):
        return out
    field_ref=reference.get("fields",{}).get(field)
    if not field_ref or not field_ref.get("heldout_reference_geometry_internal_qc_pass"):
        return out
    east=(target["original_native_minus_propagated_gaia_east_arcsec"]-
          field_ref["median_original_ztf_minus_ps1_reference_training_east_arcsec"])
    north=(target["original_native_minus_propagated_gaia_north_arcsec"]-
           field_ref["median_original_ztf_minus_ps1_reference_training_north_arcsec"])
    return {
        **out,
        "status":"DESCRIPTIVE_PS1_REFERENCE_RELATIVE_TARGET_OFFSET_NOT_PHYSICAL_IDENTITY",
        "external_reference_adjusted_target_east_arcsec":round(east,6),
        "external_reference_adjusted_target_north_arcsec":round(north,6),
    }


def run_ft_tau_gaia_ps1_ztf_target_astrometry(
        seed:bytes,historic:dict,oid_receipt:dict,prior_images:dict,
        prior_720:dict,prior_external:dict,*,
        gaia_fetch=fetch_gaia_astrometry,
        ps1_fetch=fetch_external_ps1_mean_sources,
        native_fetch=None)->dict:
    """Run actual four target frames against original Gaia + independent PS1."""
    from .v114_native_psfcat_association import fetch_native_psf_product
    native_fetch=native_fetch or fetch_native_psf_product
    fixed,frames=fixed_four_exposure_pairs(seed,historic,oid_receipt,prior_images)
    if (prior_720.get("new_sky_radius_arcsec")!=720
        or prior_720.get("n_original_full_native_ZTF_psfcat_SHA_matched")!=4
        or prior_external.get("n_original_ZTF_full_native_psfcats_reverified")!=4
        or prior_external.get("n_same_band_PanSTARRS_source_level_internal_pilot_passes")!=2
        or prior_external.get("external_PS1_DR2_original_source_query",{}).get("n_ps1_original_rows")!=1780):
        raise ValueError("Prior original external astrometry reference evidence not frozen")
    gaia=None
    gaia_sha=None
    try:
        gaia_raw=gaia_fetch((FT_GAIA,),timeout_sec=35)
        gaia=parse_gaia_astrometry(gaia_raw,expected_ids=(FT_GAIA,))[FT_GAIA]
        gaia_sha=hashlib.sha256(gaia_raw).hexdigest()
    except NETWORK_ERRORS:
        pass
    ps1=None
    ps1_sha=None
    source_status="ORIGINAL_MAST_PS1_SOURCE_MISSING"
    p_all=None
    try:
        original=ps1_fetch(fixed["seed_ra_deg"],fixed["seed_dec_deg"],timeout_sec=45)
        ps1=parse_ps1_original_mean(original,ra0=fixed["seed_ra_deg"],
                                   dec0=fixed["seed_dec_deg"])
        ps1_sha=hashlib.sha256(original).hexdigest()
        expected=prior_external["external_PS1_DR2_original_source_query"][
            "original_ps1_dr2_response_sha256"]
        if ps1_sha!=expected:
            raise ValueError("Previously genuine external PS1 catalogue raw SHA changed")
        source_status="ORIGINAL_MAST_PS1_SHA_IDENTICAL_TO_PREVIOUS"
    except NETWORK_ERRORS:
        ps1=None
        ps1_sha=None
        original=None
        source_status="ORIGINAL_MAST_PS1_UNAVAILABLE_OR_CHANGED"

    preds={}
    for band in ("g","r"):
        preds[band]={}
        for field in ("1605","609"):
            if gaia is None:
                preds[band][field]=None
                continue
            mjd=frames[band][field]["selection"]["original_mjd"]
            try:
                preds[band][field]=propagate_gaia_5p_formal(gaia,mjd_utc=mjd)
            except NETWORK_ERRORS:
                preds[band][field]=None
    if gaia is not None and ps1 is not None and all(
        preds[band][field] is not None for band in ("g","r") for field in ("1605","609")
    ):
        target_ps1=full_original_ps1_near_target(original,gaia,preds)
    else:
        target_ps1={
            "status":"ORIGINAL_GAIA_OR_PS1_SOURCE_NEIGHBOUR_CHECK_UNAVAILABLE",
            "ps1_mean_epoch_or_proper_motion_propagated":False,
            "independent_catalogue_source_ambiguity_excluded":False,
        }

    allband=[]
    for band in ("g","r"):
        native={}
        reference_inputs={}
        target_inputs={}
        for field in ("1605","609"):
            frame=frames[band][field]
            pred=preds[band][field]
            entry={
                "field":field,"band":band,"original_mjd":frame["selection"]["original_mjd"],
                "ztf_original_oid":frame["selection"]["ztf_oid"],
                "original_PSF_catalogue_SHA256_verified":False,
                "gaia_original_5p_motion_and_parallax_model_available":pred is not None,
            }
            if pred is not None:
                entry["gaia_full_formal_east_sigma_mas"]=pred["formal_gaia_east_sigma_mas"]
                entry["gaia_full_formal_north_sigma_mas"]=pred["formal_gaia_north_sigma_mas"]
                entry["gaia_ruwe"]=pred["gaia_ruwe"]
                entry["gaia_astrometric_quality_warning"]=pred[
                    "high_or_missing_ruwe_quality_warning"]
                entry["gaia_geocentric_parallax_minus_linear_east_mas"]=pred[
                    "geocentric_annual_parallax_minus_linear_east_mas"]
                entry["gaia_geocentric_parallax_minus_linear_north_mas"]=pred[
                    "geocentric_annual_parallax_minus_linear_north_mas"]
            try:
                cat=original_native_catalogue_from_frozen_image(
                    frame,ra=fixed["seed_ra_deg"],dec=fixed["seed_dec_deg"],
                    native_fetch=native_fetch)
                native[field]=cat
                entry["original_PSF_catalogue_SHA256_verified"]=True
                entry["original_full_native_PSF_catalogue_sha256"]=cat["sha256"]
                if ps1 is not None:
                    reference_inputs[field]=qualifying_original_native_sources(
                        cat,ra0=fixed["seed_ra_deg"],dec0=fixed["seed_dec_deg"],
                        max_radius_arcsec=720.)
                if pred is not None:
                    target_inputs[field]=original_target_native_candidate(cat,pred)
                else:
                    target_inputs[field]={"status":"ORIGINAL_GAIA_ASTROMETRY_UNAVAILABLE",
                                          "confirmed_physical_gaia_ztf_target":False}
            except NETWORK_ERRORS as exc:
                entry["error_type"]=type(exc).__name__
                target_inputs[field]={"status":"ORIGINAL_NATIVE_PSF_CATALOGUE_UNAVAILABLE",
                                      "confirmed_physical_gaia_ztf_target":False}
            entry["target_native_candidate"]=target_inputs[field]
            allband.append(entry)
        if ps1 is not None and len(reference_inputs)==2:
            try:
                triples=original_reference_triple_astrometry(
                    reference_inputs["1605"],reference_inputs["609"],ps1)
                reference=heldout_astrometric_reference_offsets(triples)
            except NETWORK_ERRORS as exc:
                reference={
                    "status":"ORIGINAL_SOURCE_REFERENCE_ALIGNMENT_UNAVAILABLE",
                    "error_type":type(exc).__name__,
                    "n_original_unique_external_ps1_ztf_ztf_triplets":0,
                    "both_fields_heldout_internal_geometry_pass":False,
                    "fields":{},
                }
        else:
            reference={
                "status":"ORIGINAL_SOURCE_REFERENCE_ALIGNMENT_UNAVAILABLE",
                "n_original_unique_external_ps1_ztf_ztf_triplets":0,
                "both_fields_heldout_internal_geometry_pass":False,
                "fields":{},
            }
        entries=[x for x in allband if x["band"]==band]
        for ent in entries:
            ent["descriptive_PS1_reference_adjusted_target"]=target_differential_reference_summary(
                ent["target_native_candidate"],reference,ent["field"])
        measured=[
            x["descriptive_PS1_reference_adjusted_target"] for x in entries]
        available=all(
            x["status"]=="DESCRIPTIVE_PS1_REFERENCE_RELATIVE_TARGET_OFFSET_NOT_PHYSICAL_IDENTITY"
            for x in measured)
        same_filter_pair={
            "status":("PROVISIONAL_TWO_FIELD_RELATIVE_OFFSET_AVAILABLE_NOT_PM_OR_PHYSICAL_MATCH"
                      if available else "UNRESOLVED_SAME_BAND_TARGET_OR_EXTERNAL_REFERENCE"),
            "same_filter_original_exposure_gap_seconds_approx":38.97,
            "original_field609_minus1605_relative_east_arcsec":(
                round(measured[1]["external_reference_adjusted_target_east_arcsec"]-
                      measured[0]["external_reference_adjusted_target_east_arcsec"],6)
                if available else None),
            "original_field609_minus1605_relative_north_arcsec":(
                round(measured[1]["external_reference_adjusted_target_north_arcsec"]-
                      measured[0]["external_reference_adjusted_target_north_arcsec"],6)
                if available else None),
            "independent_epoch_corrected_wcs_and_PS1_source_pm_measured":False,
            "physical_gaia_ztf_FT_TAU_target_match_confirmed":False,
        }
        allband_ref={"band":band,"source_reference_alignment":reference,
                     "target_same_band_field_pair_summary":same_filter_pair}
        if "bands" not in locals(): bands=[]
        bands.append(allband_ref)

    return {
        "phase":"TAURUS_R2_GAIA_FT_TAU_MOTION_PS1_MEAN_REFERENCE_AND_FOUR_NATIVE_ZTF_SOURCE_CANDIDATES",
        "frozen_nonrepresentative_taurus_technical_seed_size":24,
        "gaia_ft_tau_original_source_id":FT_GAIA,
        "fixed_original_ztf_exposures":4,
        "n_original_gaia_5p_records_verified":int(gaia is not None),
        "original_gaia_TAP_response_sha256":gaia_sha,
        "original_external_PS1_response_status":source_status,
        "original_external_PS1_MAST_response_sha256":ps1_sha,
        "n_original_PS1_mean_rows_valid":(
            ps1["n_original_ps1_dr2_mean_source_rows"] if ps1 is not None else 0),
        "n_original_native_ztf_PSFcat_SHA_verified":sum(
            x["original_PSF_catalogue_SHA256_verified"] for x in allband),
        "n_original_target_exposures_with_provisional_native_source_candidate":sum(
            x["target_native_candidate"].get("status")==
            "PROVISIONAL_GAIA_NEAREST_ZTF_PSF_SOURCE_GEOMETRY_PASS"
            for x in allband),
        "n_same_filter_pairs_with_two_provisional_target_candidates":sum(
            all(x["target_native_candidate"].get("status")==
                "PROVISIONAL_GAIA_NEAREST_ZTF_PSF_SOURCE_GEOMETRY_PASS"
                for x in allband if x["band"]==b) for b in ("g","r")),
        "n_bands_reference_astrometry_holdout_internal_passes":sum(
            b["source_reference_alignment"].get(
                "both_fields_heldout_internal_geometry_pass",False)
            for b in bands),
        "n_same_band_target_pair_descriptive_external_relative_offsets_available":sum(
            b["target_same_band_field_pair_summary"]["status"].startswith("PROVISIONAL_")
            for b in bands),
        "n_confirmed_physical_gaia_to_ztf_ft_tau_source_identities":0,
        "n_zTF_ft_tau_OID_lightcurves_merged":0,
        "n_new_confirmed_variable_or_companion_stars":0,
        "scientific_R2_full_physical_source_identity_completed":False,
        "original_technical_seed_sha256":hashlib.sha256(seed).hexdigest(),
        "original_MAST_PS1_target_source_ambiguity":target_ps1,
        "original_four_exposure_target_candidate_details":allband,
        "original_same_band_reference_astrometry":bands,
        "limitations":[
            "Gaia DR3 J2016.0 formal covariance and mean motion include modelled geocentric parallax; original ZTF per-frame instrument WCS source errors, PS1 mean epoch/PM, topocentric offsets and unknown systematics are not included.",
            "PS1/ZTF reference source overlap is a source-level independent-catalogue positional screen; its holdout medians do not constitute a calibrated epoch-corrected external WCS or independent target physical identity.",
            "The target PS1 neighbour search uses only PS1 DR2 mean source catalogue entries with at least five detections and lacks PS1 source-specific epoch-corrected positions or proof of unique target PS1 counterpart.",
            "Gaia target nearest-original-native-PSF positions across g/r can be provisional despite unresolved/background stellar structure, unknown centroid errors, different epochs and filter effects.",
            "No source OID lightcurves were merged and no astrophysical variability, companion or Taurus population discovery is inferred.",
        ],
    }
