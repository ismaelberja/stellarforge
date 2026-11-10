"""v1.21 falsification, archive preflight and scientific claim gates.

Scientific claims must not be upgraded merely because a previous internal
PSF test passes. All injected images are synthetic perturbations of caller
inputs, never detections. Original ZTF observational science requires real
original source provenance and independent external validations.
"""
from __future__ import annotations

from datetime import datetime, timezone
import math
from typing import Sequence

import numpy as np

from .v119_empirical_psf_noise import RegisteredStar, train_and_holdout_empirical_psf

EXPECTED_ARTIFACT = "taurus-two-target-raw-UNVERIFIED"
MIN_TRAIN = 3
MIN_HOLD = 2
MAX_FRAMES = 4
KNOWN_VALIDITY = frozenset({
    "NOT_ATTEMPTED",
    "ORIGINAL_NATIVE_SOURCE_CATALOGUE_UNAVAILABLE_OR_INVALID",
    "PREREGISTERED_NATIVE_CATALOGUE_3_PLUS_2_GATE_NOT_MET",
    "REAL_SOURCE_MASKED_STAMP_3_PLUS_2_GATE_NOT_MET",
    "REAL_EMPIRICAL_PSF_VALIDATION_INPUT_OR_FIT_REJECTED",
    "INTERNAL_DISTINCT_STAR_PSF_HOLDOUT_COMPLETED",
})


def _utc(value: str | datetime) -> datetime:
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("Invalid artifact time metadata") from exc
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise ValueError("Artifact date requires UTC offset")
    return value.astimezone(timezone.utc)


def audit_source_artifact_metadata(artifact: dict, *, as_of: str | datetime) -> dict:
    """External GitHub Actions artifact metadata only; never downloads original ZIP.

    Availability of a ZIP is NOT verification that it contains trusted
    Gaia/ZTF data; original ZIP byte/hash and source-archive checks remain
    mandatory in the manually dispatched real-data runner.
    """
    if not isinstance(artifact, dict):
        raise ValueError("Missing artifact metadata")
    if artifact.get("name") != EXPECTED_ARTIFACT:
        raise ValueError("Unexpected original artifact name")
    expires = _utc(artifact.get("expires_at"))
    now = _utc(as_of)
    size = artifact.get("size_in_bytes")
    if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
        raise ValueError("Original artifact has missing/invalid size")
    if not isinstance(artifact.get("expired"), bool):
        raise ValueError("Original artifact lacks authoritative expiry flag")
    if not isinstance(artifact.get("id"), int) or artifact["id"] <= 0:
        raise ValueError("Original artifact identity invalid")
    alive = not artifact["expired"] and expires > now
    remaining = max(0.0, (expires - now).total_seconds()) if alive else 0.0
    return {
        "status": "ARTIFACT_METADATA_AVAILABLE_NOT_BYTES_VERIFIED" if alive
                  else "ORIGINAL_SOURCE_ARTIFACT_EXPIRED_OR_UNAVAILABLE",
        "artifact_id": artifact["id"],
        "source_file_bytes_unverified": size,
        "expires_at_utc": expires.isoformat(),
        "hours_until_metadata_expiry": round(remaining / 3600, 3),
        "source_ZIP_payload_SHA_verified": False,
        "real_ZTF_eligible_stars_verified": False,
        "real_empirical_psf_calibration_completed": False,
    }


def audit_v120_real_source_evidence(result: dict | None) -> dict:
    """Reject dishonest or incomplete original-source evidence claims.

    A claimed internal PSF held-out fit requires >=3 actual training stars
    and >=2 *different* validation-star registered stamps in one frame.
    This cannot establish calibration of the original survey PSF, WCS,
    detector covariance or astrophysical source identity.
    """
    if result is None:
        return {
            "status": "ORIGINAL_CIDA11_V120_WORKFLOW_NOT_EXECUTED",
            "n_original_frames_with_internal_distinct_star_model": 0,
            "n_original_frames_reported": 0,
            "independent_original_survey_psf_calibrated": False,
            "physical_gaia_ztf_identity_verified": False,
            "new_companion_or_variability_confirmed": False,
        }
    if not isinstance(result, dict) or not isinstance(result.get("frames"), list):
        raise ValueError("Missing real-data aggregate report")
    frames = result["frames"]
    if len(frames) > MAX_FRAMES:
        raise ValueError("Unbounded real ZTF exposure report")
    count = 0
    mjds = set()
    for f in frames:
        if not isinstance(f, dict):
            raise ValueError("Invalid original exposure record")
        if f.get("field") != "CIDA 11" or f.get("band") != "zg":
            raise ValueError("Unexpected original ZTF pilot field or band")
        mjd = f.get("mjd")
        if (not isinstance(mjd, (int, float)) or isinstance(mjd, bool)
                or not math.isfinite(mjd)
                or not 58000.0 < float(mjd) < 59000.0
                or mjd in mjds):
            raise ValueError("Invalid/duplicate historical MJD")
        mjds.add(mjd)
        for key in ("n_native_train", "n_native_holdout",
                    "n_registered_train", "n_registered_holdout",
                    "n_mask_or_registration_failures",
                    "image_access_failures", "n_heldout_profile_reviews"):
            v = f.get(key)
            if isinstance(v, bool) or not isinstance(v, int) or v < 0:
                raise ValueError("Invalid observed sample counts")
        if (f["n_native_train"] > 4 or f["n_native_holdout"] > 3
                or f["n_registered_train"] > f["n_native_train"]
                or f["n_registered_holdout"] > f["n_native_holdout"]
                or f["n_heldout_profile_reviews"] > f["n_registered_holdout"]):
            raise ValueError("Inconsistent original source eligibility counts")
        state = f.get("empirical_psf_status")
        if state not in KNOWN_VALIDITY:
            raise ValueError("Unknown original ZTF validation status")
        if state == "INTERNAL_DISTINCT_STAR_PSF_HOLDOUT_COMPLETED":
            if (f["n_registered_train"] < MIN_TRAIN
                    or f["n_registered_holdout"] < MIN_HOLD):
                raise ValueError("False positive real distinct-star PSF claim")
            count += 1
    reported = result.get("n_original_exposures_with_empirical_whole_star_holdout_completed")
    if reported is not None and (isinstance(reported, bool)
                                or not isinstance(reported, int)
                                or reported != count):
        raise ValueError("Original ZTF stated model-success count disagrees with frames")
    status = ("REAL_INTERNAL_WHOLE_STAR_TEST_REPORTED_NOT_SURVEY_CALIBRATION"
              if count else "REAL_STELLAR_PSF_VALIDATION_NOT_ESTABLISHED")
    return {
        "status": status,
        "n_original_frames_reported": len(frames),
        "n_original_frames_with_internal_distinct_star_model": count,
        "independent_original_survey_psf_calibrated": False,
        "real_ztf_detector_wcs_or_covariance_calibrated": False,
        "physical_gaia_ztf_identity_verified": False,
        "new_companion_or_variability_confirmed": False,
    }


def training_subset_stability(
    training: Sequence[RegisteredStar], validation: Sequence[RegisteredStar],
) -> dict:
    """LOO-training sensitivity on different whole stars.

    Requires >=4 distinct training stars and >=2 disjoint held-out stars
    from the SAME exposure. An unstable model is a warning; a stable model
    is NOT original-survey PSF calibration.
    """
    tr, hold = list(training), list(validation)
    if not 4 <= len(tr) <= 32 or not 2 <= len(hold) <= 16:
        raise ValueError("Need >=4 source-disjoint training and >=2 held-out stars")
    baseline = train_and_holdout_empirical_psf(tr, hold)
    base_rms = np.array(
        [s["residual_rms_over_sky_mad"] for s in baseline["heldout_results"]])
    differences = []
    review_counts = []
    for i in range(len(tr)):
        candidate = train_and_holdout_empirical_psf(tr[:i] + tr[i+1:], hold)
        rms = np.array(
            [s["residual_rms_over_sky_mad"] for s in candidate["heldout_results"]])
        differences.extend(abs(rms - base_rms).tolist())
        review_counts.append(candidate["n_heldout_profile_reviews"])
    return {
        "status": "INTERNAL_PSF_TRAINING_SUBSET_SENSITIVITY_AUDITED",
        "n_training_subset_models": len(tr),
        "n_distinct_heldout_stars": len(hold),
        "max_abs_change_heldout_rms_over_sky_mad": round(max(differences), 6),
        "max_review_count_across_subset_models": max(review_counts),
        "baseline_heldout_review_count": baseline["n_heldout_profile_reviews"],
        "uses_original_daophot_psf_parameters": False,
        "original_survey_training_star_exclusion_verified": False,
        "real_external_astrometric_or_psf_calibration": False,
        "astrophysical_discovery_claimed": False,
    }


def synthetic_blend_falsification(
    training: Sequence[RegisteredStar], validation: Sequence[RegisteredStar],
    *, extra_peak_dn: float,
    offset_x_pixels: float = 4.0,
    offset_y_pixels: float = -2.0,
    width_pixels: float = 1.5,
) -> dict:
    """Inject a *known artificial* positive secondary peak in held-out pixels.

    The model is trained on unaffected source stamps. This is a
    falsification/sensitivity experiment, NOT a companion search, not a
    physical angular separation/contrast curve or completeness calibration.
    No original pixels or source identifiers are returned.
    """
    if (not all(math.isfinite(float(x)) for x in
                (extra_peak_dn, offset_x_pixels, offset_y_pixels, width_pixels))
            or not 0 < extra_peak_dn <= 1e7
            or not 2 <= math.hypot(offset_x_pixels, offset_y_pixels) <= 8
            or not 0.7 <= width_pixels <= 3):
        raise ValueError("Invalid synthetic perturbation parameters")
    tr, hold = list(training), list(validation)
    if len(hold) < 2:
        raise ValueError("Need distinct held-out stars")
    base = train_and_holdout_empirical_psf(tr, hold)
    target = hold[0]
    src = np.asarray(target.pixels_dn, dtype=float)
    if src.ndim != 2 or src.shape[0] % 2 != 1:
        raise ValueError("Invalid source stamp")
    yy, xx = np.indices(src.shape, dtype=float)
    cx = (src.shape[1] - 1) / 2 + offset_x_pixels
    cy = (src.shape[0] - 1) / 2 + offset_y_pixels
    injection = extra_peak_dn * np.exp(
        -((xx - cx)**2 + (yy - cy)**2) / (2 * width_pixels**2))
    contaminated = RegisteredStar(
        gaia_source_id=target.gaia_source_id,
        exposure_id=target.exposure_id,
        pixels_dn=src + injection,
        mask_bits=target.mask_bits,
        registered_offset_xy=target.registered_offset_xy,
    )
    changed = train_and_holdout_empirical_psf(tr, [contaminated] + hold[1:])
    before = base["heldout_results"][0]["residual_rms_over_sky_mad"]
    after = changed["heldout_results"][0]["residual_rms_over_sky_mad"]
    return {
        "status": "SYNTHETIC_HELDOUT_BLENDED_PROFILE_SENSITIVITY_ONLY",
        "original_heldout_rms_over_sky_mad": before,
        "artificial_blend_heldout_rms_over_sky_mad": after,
        "artificial_injection_increases_residual": after > before,
        "artificial_profile_flagged_for_review":
            changed["heldout_results"][0]["status"] == "HELDOUT_PROFILE_REVIEW_REQUIRED",
        "original_pixel_inputs_unchanged": True,
        "true_astrophysical_companion_detected": False,
        "survey_completeness_or_contrast_calibrated": False,
        "original_survey_psf_training_membership_known": False,
    }


HISTORIC_THREE_REVIEW_CASES = (
    {"label": "FT Tau target", "mjd": 58491.184780,
     "same_image_rms_over_sky_mad": 1.6723,
     "largest_positive_over_sky_mad": 7.6730},
    {"label": "CIDA 11 target", "mjd": 58849.135984,
     "same_image_rms_over_sky_mad": 2.6341,
     "largest_positive_over_sky_mad": 11.8679},
    {"label": "CIDA 11 field Gaia reference candidate", "mjd": 58849.135984,
     "same_image_rms_over_sky_mad": 1.3652,
     "largest_positive_over_sky_mad": 7.8125},
)


def historic_three_residual_review_register() -> dict:
    """Frozen descriptive v1.16 original-data history, not remeasurement."""
    if not all(x["largest_positive_over_sky_mad"] > 7.0
               for x in HISTORIC_THREE_REVIEW_CASES):
        raise AssertionError("Changed original documented v1.16 review threshold")
    return {
        "status": "THREE_ORIGINAL_V116_HIGH_RESIDUAL_CASES_REMAIN_UNRESOLVED",
        "n_historic_review_profiles": 3,
        "n_physical_companions_confirmed": 0,
        "n_independent_new_source_confirmations": 0,
        "hypotheses_not_discriminated": [
            "native spatial PSF interpolation mismatch",
            "crowding or unresolved background source",
            "structured diffuse sky/nebulosity",
            "WCS/centroid or atmospheric systematics",
            "detector/sky correlated noise",
        ],
        "requires_independent_multi_epoch_multi_band_validation": True,
        "historic_values_from_v116_report_not_recomputed": True,
    }
