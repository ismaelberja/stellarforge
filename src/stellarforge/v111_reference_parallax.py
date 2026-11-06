"""v1.11: offline re-screen legacy Gaia-reference ZTF offsets with true DR3 5p.

Uses *original* v1.8 derived Gaussian centroids, not new FITS pixels. For a
Gaia reference measured against its LINEAR proper-motion predicted position:

    residual(parallax) ~ residual(linear) - geometric_annual_parallax_shift

The minus sign is essential (centroid minus newly propagated Gaia position).
The reference offsets' Gaussian centroids and original ZTF WCS are unchanged.
Gaia 5x5 formal covariance is reported separately: it is NOT a new estimate
of actual instrumental WCS error or evidence of Gaia-ZTF source identity.
"""
from __future__ import annotations

import hashlib
import json
import math
import statistics
from pathlib import Path

from .v110_reference_holdout import (
    validate_derived_v18_ledger, quality_filter_references,
    leave_one_out_translation, STRICT_STATUS,
)
from .v19_gaia_covariance import (
    parse_gaia_astrometry, propagate_gaia_5p_formal,
    make_target_astrometry_adql,
)

MAX_SOURCE_IDS = 12
MAX_CORRECTION_MAS = 250.0


def all_required_gaia_ids(ledger: dict) -> tuple[str, ...]:
    validate_derived_v18_ledger(ledger)
    ids=set()
    for e in ledger["exposures"]:
        ids.add(str(e["target_gaia_id"]))
        ids.update(str(r["id"]) for r in e["refs"])
    if not 1<=len(ids)<=MAX_SOURCE_IDS:
        raise ValueError("Unexpected number of exact Gaia source IDs")
    return tuple(sorted(ids))


def _correct_one_offset(original_east_arcsec:float, original_north_arcsec:float,
                        formal:dict) -> tuple[float,float]:
    if not formal.get("annual_geocentric_parallax_included",False):
        raise ValueError("Missing Gaia parallax propagation")
    pe=float(formal["geocentric_annual_parallax_minus_linear_east_mas"])
    pn=float(formal["geocentric_annual_parallax_minus_linear_north_mas"])
    if not all(math.isfinite(v) for v in
               (pe,pn,original_east_arcsec,original_north_arcsec)):
        raise ValueError("Nonfinite Gaia correction")
    if math.hypot(pe,pn)>MAX_CORRECTION_MAS:
        raise ValueError("Suspiciously large annual Gaia parallax displacement")
    return original_east_arcsec-pe/1000, original_north_arcsec-pn/1000


def evaluate_with_gaia_catalogue(ledger:dict, gaia_entries:dict,
                                  *,raw_gaia_sha256:str) -> dict:
    """Reassess each original candidate offset with its own Gaia 5D solution.

    No reference becomes physically 'verified' via catalogue astrometry.
    Strict/inclusive quality sample is frozen to the original v1.8 fit status.
    If any expected Gaia source is missing or its full covariance is invalid,
    fail *before* publishing partial results.
    """
    ids=all_required_gaia_ids(ledger)
    if set(gaia_entries)!=set(ids):
        raise ValueError("Missing/extra Gaia sources in correction batch")
    if not isinstance(raw_gaia_sha256,str) or len(raw_gaia_sha256)!=64 or any(
        c not in "0123456789abcdef" for c in raw_gaia_sha256):
        raise ValueError("Invalid Gaia raw-response digest")
    corrected=[]
    n_orig_refs=0
    n_recalculated_refs=0
    formal_east=[]
    formal_north=[]
    max_shift=0.0
    for e in ledger["exposures"]:
        mjd=e["mjd"]
        tar=propagate_gaia_5p_formal(gaia_entries[e["target_gaia_id"]],
                                      mjd_utc=mjd)
        tar_e,tar_n=_correct_one_offset(
            e["target_east_arcsec"],e["target_north_arcsec"],tar)
        candidate_models=[]
        for ref in e["refs"]:
            solution=propagate_gaia_5p_formal(gaia_entries[ref["id"]],
                                              mjd_utc=mjd)
            new_e,new_n=_correct_one_offset(ref["east"],ref["north"],solution)
            ref_model={**ref,"east":new_e,"north":new_n}
            candidate_models.append(ref_model)
            n_orig_refs+=1
            n_recalculated_refs+=1
            formal_east.append(solution["formal_gaia_east_sigma_mas"])
            formal_north.append(solution["formal_gaia_north_sigma_mas"])
            max_shift=max(max_shift,math.hypot(
                solution["geocentric_annual_parallax_minus_linear_east_mas"],
                solution["geocentric_annual_parallax_minus_linear_north_mas"]))
        corrected_inclusive=quality_filter_references(
            candidate_models,require_clean_fit=False)
        corrected_strict=quality_filter_references(
            candidate_models,require_clean_fit=True)
        original_inclusive=quality_filter_references(
            e["refs"],require_clean_fit=False)
        original_strict=quality_filter_references(
            e["refs"],require_clean_fit=True)
        orig_all=leave_one_out_translation(original_inclusive)
        orig_strict=leave_one_out_translation(original_strict)
        new_all=leave_one_out_translation(corrected_inclusive)
        new_strict=leave_one_out_translation(corrected_strict)
        if (len(corrected_inclusive)!=len(original_inclusive) or
            len(corrected_strict)!=len(original_strict)):
            raise ValueError("Unexpected reference selection change")
        rms_before=orig_strict.get("loo_rms_radial_disagreement_arcsec")
        rms_after=new_strict.get("loo_rms_radial_disagreement_arcsec")
        strict_delta=(
            round((rms_after-rms_before)*1000,4)
            if rms_before is not None and rms_after is not None else None)
        target_proxy={
            "status":"NOT_REPORTED_INSUFFICIENT_QUALITY_OR_TARGET_PROFILE",
            "source_identity_confirmed":False,
        }
        if (rms_after is not None and
                e["target_fit_status"]==STRICT_STATUS):
            dx=tar_e-new_strict["median_east_reference_shift_arcsec"]
            dy=tar_n-new_strict["median_north_reference_shift_arcsec"]
            target_proxy={
                "status":"PARALLAX_AWARE_TARGET_MINUS_REFERENCE_PROXY_ONLY",
                "east_arcsec":round(dx,6),"north_arcsec":round(dy,6),
                "radial_arcsec":round(math.hypot(dx,dy),6),
                "source_identity_confirmed":False,
                "calibrated_wcs_residual":False,
            }
        corrected.append({
            "target":e["target"],
            "gaia_target_id":e["target_gaia_id"],
            "ztf_oid":e["oid"],"filter":e["band"],"mjd_assumed_utc":mjd,
            "n_original_model_fits":len(e["refs"]),
            "n_inclusive_model_quality":len(original_inclusive),
            "n_strict_model_quality":len(original_strict),
            "target_image_fit_status":e["target_fit_status"],
            "original_inclusive_loo":orig_all,
            "parallax_aware_inclusive_loo":new_all,
            "original_strict_loo":orig_strict,
            "parallax_aware_strict_loo":new_strict,
            "strict_loo_rms_change_mas":strict_delta,
            "target_geometric_parallax_east_mas":
                tar["geocentric_annual_parallax_minus_linear_east_mas"],
            "target_geometric_parallax_north_mas":
                tar["geocentric_annual_parallax_minus_linear_north_mas"],
            "target_formal_gaia_east_sigma_mas":
                tar["formal_gaia_east_sigma_mas"],
            "target_formal_gaia_north_sigma_mas":
                tar["formal_gaia_north_sigma_mas"],
            "high_or_missing_target_ruwe_warning":
                tar["high_or_missing_ruwe_quality_warning"],
            "reference_gaia_formal_east_sigmas_mas": [
                propagate_gaia_5p_formal(gaia_entries[ref["id"]],mjd_utc=mjd)[
                    "formal_gaia_east_sigma_mas"] for ref in e["refs"]
            ],
            "target_minus_reference_proxy":target_proxy,
            "v18_gaussian_centroids_or_raw_ztf_pixels_refitted":False,
            "geometric_not_topocentric_parallax":True,
            "reference_astrometry_independent_of_ztf_instrument":True,
            "instrumental_wcs_error_budget_validated":False,
            "gaia_ztf_physical_identity_confirmed":False,
        })
    return {
        "schema_version":"stellarforge-v1.11-reference-gaia-5p-parallax-holdout",
        "source_v18_run_id":42077605987,
        "source_original_v18_aggregate_sha256":
            ledger["provenance"]["original_json_sha256"],
        "gaia_dr3_tap_raw_response_sha256":raw_gaia_sha256,
        "gaia_adql_sha256":hashlib.sha256(
            make_target_astrometry_adql(ids).encode()).hexdigest(),
        "n_gaia_dr3_exact_ids_with_complete_5p":len(ids),
        "n_real_science_exposures_reanalyzed":len(corrected),
        "n_reference_image_models_reanalyzed":n_recalculated_refs,
        "n_reference_observations_original":n_orig_refs,
        "max_reference_geometric_annual_shift_mas":round(max_shift,5),
        "median_reference_gaia_formal_sigma_east_mas":round(
            statistics.median(formal_east),5),
        "median_reference_gaia_formal_sigma_north_mas":round(
            statistics.median(formal_north),5),
        "n_strict_loo_eligible_exposures":sum(
            e["strict_loo_rms_change_mas"] is not None for e in corrected),
        "exposures":corrected,
        "n_independently_calibrated_instrument_wcs_solutions":0,
        "n_authenticated_single_star_empirical_psfs":0,
        "n_confirmed_gaia_ztf_source_matches":0,
        "n_confirmed_astrophysical_companions":0,
        "n_confirmed_physical_variability_events":0,
        "limitations":[
            "An archived 2018-2020 Gaussian image fit is not refit; only its nominal Gaia-position subtrahend is changed for each original reference and target.",
            "The Gaia catalogue 5x5 covariance is propagated for each of the eight candidate references and two targets; it excludes ZTF centroid PSF/WCS instrument noise and common-mode systematics.",
            "For each archived reference, the linear-motion Gaia prediction is replaced by first-order Earth-geocentric annual geometric parallax; not a full Palomar topocentric apparent correction.",
            "Formal source parameter uncertainties are NOT mathematically attached as measurement weights or converted into a calibrated astrometric error floor.",
            "Absolute FITS time metadata has not been independently validated and historical MJD is assumed UTC.",
            "Reference Gaia IDs/ztf peaks, morphology, blending and high-RUWE target astrophysical motion are not independently verified.",
            "LOO median offsets use only 3-5 selected candidate stars; shared WCS/PSF systematics and selection bias are not detected by LOO.",
            "A change in LOO disagreement after parallax correction does not prove that the instrumental WCS has improved.",
        ],
    }


def run_from_bytes(ledger:dict,raw_gaia_csv:bytes) -> dict:
    ids=all_required_gaia_ids(ledger)
    entries=parse_gaia_astrometry(raw_gaia_csv,expected_ids=ids)
    return evaluate_with_gaia_catalogue(
        ledger,entries,raw_gaia_sha256=hashlib.sha256(raw_gaia_csv).hexdigest())


def load_ledger(path:Path):
    if path.stat().st_size>100_000:
        raise ValueError("Too large derived historical reference file")
    data=json.loads(path.read_text(encoding="utf-8"))
    validate_derived_v18_ledger(data)
    return data
