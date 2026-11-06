"""v1.10: leave-one-reference-out (LOO) audit of archived ZTF/Gaia offsets.

Consumes ONLY the bounded, derived *v1.8* image-offset ledger (no raw FITS,
Gaia TAP CSV, source photometry or network). Each reference measurement was a
constrained Gaussian centroid relative to the original ZTF image WCS and a
simplified Gaia proper-motion prediction. It is not a validated astrometric
match, independent PSF model or calibrated instrument error measurement.

LOO residuals estimate internal reference disagreement, *not* a total
prediction uncertainty. Small N, correlated WCS, source selection, unmodeled
parallax (fixed only for two target IDs in v1.9), Gaia covariance, chromatic
terms, nebulosity and PSF bias must not be ignored.
"""
from __future__ import annotations

import hashlib
import json
import math
import statistics
from pathlib import Path

SCHEMA="stellarforge-v1.10-derived-v1.8-reference-offsets"
REVIEWABLE={"PSF_PROXY_PROVISIONAL_ONLY","PSF_PROXY_REVIEW_REQUIRED"}
STRICT_STATUS="PSF_PROXY_PROVISIONAL_ONLY"
REQUIRED_PROVENANCE_SHA="fb7d5c315cbef56b2551e73920c67920827d91160b4c0bd35f3fd77113166beb"
MIN_REF_LOO=3


def _finite_number(value, label: str) -> float:
    if isinstance(value,bool) or not isinstance(value,(int,float)):
        raise ValueError(f"Invalid {label}")
    x=float(value)
    if not math.isfinite(x):
        raise ValueError(f"Non-finite {label}")
    return x


def validate_derived_v18_ledger(data: dict) -> None:
    """Fail closed on malformed reference metrics, duplicate IDs or provenance."""
    if not isinstance(data,dict) or data.get("schema_version") != SCHEMA:
        raise ValueError("Unexpected derived reference-ledger schema")
    prov=data.get("provenance",{})
    if (prov.get("original_json_sha256")!=REQUIRED_PROVENANCE_SHA
            or prov.get("original_run_id")!=42077605987):
        raise ValueError("Wrong archived v1.8 source provenance")
    exposures=data.get("exposures")
    if not isinstance(exposures,list) or not 1<=len(exposures)<=40:
        raise ValueError("Unexpected number of source exposures")
    seen_exposures=set()
    for exposure in exposures:
        target=str(exposure["target_gaia_id"])
        if not target.isdigit() or not str(exposure["oid"]).isdigit():
            raise ValueError("Noncatalogue target/OID identifier")
        mjd=_finite_number(exposure["mjd"],"science MJD")
        if not 55000<=mjd<=80000 or exposure["band"] not in ("zg","zr","zi"):
            raise ValueError("Bad reference-exposure date or band")
        key=(target,exposure["oid"],exposure["band"],mjd)
        if key in seen_exposures:
            raise ValueError("Repeated ZTF exposure")
        seen_exposures.add(key)
        if exposure["target_fit_status"] not in REVIEWABLE:
            raise ValueError("Invalid target image-fit quality")
        for part in ("target_east_arcsec","target_north_arcsec"):
            _finite_number(exposure[part],part)
        refs=exposure.get("refs")
        n=exposure["n_reference_requests"]
        if not isinstance(n,int) or not 0<=n<=5:
            raise ValueError("Invalid original reference request budget")
        if not isinstance(refs,list) or len(refs)>n:
            raise ValueError("Reference count exceeds original requests")
        seen_sources=set()
        for ref in refs:
            sid=str(ref["id"])
            if not sid.isdigit() or sid==target or sid in seen_sources:
                raise ValueError("Reference Gaia ID invalid, target or duplicate")
            seen_sources.add(sid)
            if ref["status"] not in REVIEWABLE:
                raise ValueError("Only actual fitted v1.8 references may enter")
            for part in ("east","north","residual_proxy","axis_ratio"):
                _finite_number(ref[part],part)
            if (ref["residual_proxy"]<0
                    or not .5<=ref["axis_ratio"]<=5
                    or not isinstance(ref["fit_near_bound"],bool)):
                raise ValueError("Unusable reference image morphology")


def quality_filter_references(refs: list[dict], *,
                              require_clean_fit: bool) -> list[dict]:
    """Exclude poor model residuals from the strict sensitivity branch."""
    selected=[]
    for r in refs:
        if r["fit_near_bound"] or abs(r["east"])>=1.5 or abs(r["north"])>=1.5:
            continue
        if not .8<=r["axis_ratio"]<=1.8:
            continue
        if require_clean_fit and (
                r["status"]!=STRICT_STATUS or r["residual_proxy"]>=5.0):
            continue
        selected.append(r)
    return selected


def leave_one_out_translation(refs: list[dict]) -> dict:
    """LOO median in east/north, held-out angular errors; no fitted calibration.

    Uses each ID exactly once and a robust 2-D central estimate. This is a
    diagnostic of *the reference sample's consistency* within one dated FITS
    product. A 3-star LOO is especially unstable: two training stars per fold.
    """
    ids=[str(r["id"]) for r in refs]
    if len(ids)!=len(set(ids)):
        raise ValueError("LOO requires distinct Gaia source IDs")
    if len(refs)<MIN_REF_LOO:
        return {
            "status":"INSUFFICIENT_INDEPENDENT_REFERENCES_FOR_HOLDOUT",
            "n_usable_reference_models":len(refs),
            "n_training_stars_per_fold":max(len(refs)-1,0),
            "independent_ztf_wcs_solution_validated":False,
            "total_instrumental_uncertainty_calibrated":False,
        }
    cx=statistics.median([r["east"] for r in refs])
    cy=statistics.median([r["north"] for r in refs])
    loo=[]
    for heldout in refs:
        training=[r for r in refs if r["id"]!=heldout["id"]]
        ox=statistics.median([r["east"] for r in training])
        oy=statistics.median([r["north"] for r in training])
        east=heldout["east"]-ox
        north=heldout["north"]-oy
        loo.append({
            "heldout_gaia_id":str(heldout["id"]),
            "east_prediction_error_arcsec":round(east,6),
            "north_prediction_error_arcsec":round(north,6),
            "radial_prediction_disagreement_arcsec":round(math.hypot(east,north),6),
        })
    distances=[math.hypot(x["east_prediction_error_arcsec"],
                          x["north_prediction_error_arcsec"]) for x in loo]
    rms=math.sqrt(sum(v*v for v in distances)/len(distances))
    return {
        "status":("SMALL_SAMPLE_LOO_DISAGREEMENT_ONLY" if len(refs)<5
                  else "LOO_REFERENCE_DISAGREEMENT_ONLY"),
        "n_usable_reference_models":len(refs),
        "n_training_stars_per_fold":len(refs)-1,
        "median_east_reference_shift_arcsec":round(cx,6),
        "median_north_reference_shift_arcsec":round(cy,6),
        "loo_median_radial_disagreement_arcsec":round(statistics.median(distances),6),
        "loo_max_radial_disagreement_arcsec":round(max(distances),6),
        "loo_rms_radial_disagreement_arcsec":round(rms,6),
        "heldout_reference_errors":loo,
        "loo_internal_disagreement_not_instrumental_accuracy":True,
        "independent_ztf_wcs_solution_validated":False,
        "total_instrumental_uncertainty_calibrated":False,
    }


def audit_exposure(exposure: dict) -> dict:
    """Two alternate reference-quality gates, never hiding selection effects."""
    all_refs=quality_filter_references(exposure["refs"],require_clean_fit=False)
    strict_refs=quality_filter_references(exposure["refs"],require_clean_fit=True)
    loose=leave_one_out_translation(all_refs)
    strict=leave_one_out_translation(strict_refs)
    out={
        "target":exposure["target"],
        "gaia_target_source_id":exposure["target_gaia_id"],
        "ztf_oid":exposure["oid"],
        "band":exposure["band"],
        "mjd":exposure["mjd"],
        "target_image_model_status":exposure["target_fit_status"],
        "n_reference_requests_in_original_pilot":exposure["n_reference_requests"],
        "n_gaia_references_fitted_in_original_pilot":len(exposure["refs"]),
        "n_ref_models_meeting_geometry":len(all_refs),
        "n_ref_models_meeting_strict_model_residual_screen":len(strict_refs),
        "all_model_statuses_loocv":loose,
        "strict_model_status_loocv":strict,
        "full_gaia_covariance_used_for_reference_stars":False,
        "annual_parallax_corrections_applied_to_reference_stars":False,
        "gaia_ztf_astrophysical_source_identity_confirmed":False,
        "empirical_instrument_psf_calibrated":False,
        "independent_instrument_wcs_calibrated":False,
    }
    # An apparent corrected target offset is NOT quoted unless the target
    # itself passed image-profile QA and clean references passed LOO.
    if (strict["status"] not in
            ("INSUFFICIENT_INDEPENDENT_REFERENCES_FOR_HOLDOUT",)
            and exposure["target_fit_status"]==STRICT_STATUS):
        dx=exposure["target_east_arcsec"]-strict["median_east_reference_shift_arcsec"]
        dy=exposure["target_north_arcsec"]-strict["median_north_reference_shift_arcsec"]
        out["strict_reference_subtracted_target_proxy"]={
            "east_arcsec":round(dx,6),
            "north_arcsec":round(dy,6),
            "radial_arcsec":round(math.hypot(dx,dy),6),
            "is_not_astrometric_accuracy":True,
            "source_identity_confirmed":False,
        }
    else:
        out["strict_reference_subtracted_target_proxy"]={
            "status":"NOT_REPORTED_DUE_TO_TARGET_OR_REFERENCE_QUALITY_GATE",
            "source_identity_confirmed":False,
        }
    return out


def evaluate_derived_ledger(data:dict) -> dict:
    validate_derived_v18_ledger(data)
    exposures=[audit_exposure(r) for r in data["exposures"]]
    ok=lambda r:r["status"]!="INSUFFICIENT_INDEPENDENT_REFERENCES_FOR_HOLDOUT"
    return {
        "schema_version":"stellarforge-v1.10-reference-holdout-audit",
        "input_derived_v18_ledger_sha256":hashlib.sha256(
            json.dumps(data,sort_keys=True,separators=(",",":")).encode()).hexdigest(),
        "source_run_id":42077605987,
        "source_json_sha256":REQUIRED_PROVENANCE_SHA,
        "n_actual_science_exposures":len(exposures),
        "n_reference_fits_in_original_derived_evidence":sum(
            r["n_gaia_references_fitted_in_original_pilot"] for r in exposures),
        "n_exposures_with_loo_all_image_models":sum(ok(r["all_model_statuses_loocv"]) for r in exposures),
        "n_exposures_with_loo_strict_image_models":sum(ok(r["strict_model_status_loocv"]) for r in exposures),
        "n_exposures_with_strict_reference_subtracted_target_proxy":sum(
            "radial_arcsec" in r["strict_reference_subtracted_target_proxy"] for r in exposures),
        "exposures":exposures,
        "independently_calibrated_detector_wcs_solutions":0,
        "authenticated_single_star_psfs":0,
        "physical_gaia_ztf_source_associations_confirmed":0,
        "confirmed_physical_variability_events":0,
        "limitations":[
            "A leave-one-out residual on three to five catalogue-backed reference candidates is internal disagreement, NOT calibrated centroid/WCS accuracy or a Gaussian detection confidence interval.",
            "Reference candidate source identity, morphology, crowding, instrument-dependent PSF, chromatic aberration and exact ZTF time metadata are not independently verified.",
            "Each reference may share original WCS and selection biases; leave-one-out cannot remove common-mode systematic errors.",
            "The original v1.8 Gaia reference positions omitted annual parallax and full 5x5 covariance; v1.9 corrections apply to TWO target Gaia IDs only and are NOT silently attributed to reference stars.",
            "The target CIDA 11 has high RUWE; Gaia formal errors may understate non-single-star astrometric systematics.",
            "An unconverged/flagged Gaussian fit is not evidence of a companion and absence of a residual is not proof of unblended stars.",
            "The original v1.8 reference artifact was a bounded 1-OID-per-target two-epoch pilot, not a full six-OID field calibration.",
        ],
    }


def load_and_audit(path:Path) -> dict:
    # This is a small public derived summary, not a permissive generic import
    # for arbitrary (possibly private) survey files.
    if path.stat().st_size>100_000:
        raise ValueError("Derived offset ledger too large")
    data=json.loads(path.read_text(encoding="utf-8"))
    return evaluate_derived_ledger(data)
