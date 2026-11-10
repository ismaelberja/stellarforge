"""Adversarial synthetic and evidence-only v1.21 scientific tests."""
from datetime import datetime, timezone

import numpy as np
import pytest

from stellarforge.v119_empirical_psf_noise import RegisteredStar
from stellarforge.v121_science_falsification import (
    EXPECTED_ARTIFACT, audit_source_artifact_metadata,
    audit_v120_real_source_evidence, historic_three_residual_review_register,
    training_subset_stability, synthetic_blend_falsification,
)


def synthetic_stars(n=7, seed=121):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[-11:12, -11:12]
    p = np.exp(-(xx*xx+yy*yy)/(2*1.35**2))
    p /= p.sum()
    return [RegisteredStar(
        str(3419111000000000000+j), "one-exact-original-image-date",
        210+(14000+j*100)*p+rng.normal(0, 2, p.shape),
        np.zeros(p.shape, dtype=np.uint16),
    ) for j in range(n)]


def metadata(expired=False):
    return {
        "id": 13401380025, "name": EXPECTED_ARTIFACT,
        "size_in_bytes": 181170, "expired": expired,
        "expires_at": "2026-11-12T08:47:05Z",
    }


def sample_frame(*, n_train=4, n_hold=3,
                 status="INTERNAL_DISTINCT_STAR_PSF_HOLDOUT_COMPLETED"):
    return {
        "field": "CIDA 11", "band": "zg", "mjd": 58475.11375,
        "n_native_train": 4, "n_native_holdout": 3,
        "n_registered_train": n_train,
        "n_registered_holdout": n_hold,
        "n_mask_or_registration_failures": 0,
        "image_access_failures": 0, "n_heldout_profile_reviews": 0,
        "empirical_psf_status": status,
    }


def test_source_artifact_available_but_bytes_unverified():
    r = audit_source_artifact_metadata(metadata(), as_of="2026-11-10T10:00:00+00:00")
    assert r["status"] == "ARTIFACT_METADATA_AVAILABLE_NOT_BYTES_VERIFIED"
    assert r["hours_until_metadata_expiry"] > 0
    assert r["source_ZIP_payload_SHA_verified"] is False
    assert not r["real_empirical_psf_calibration_completed"]


@pytest.mark.parametrize("when,expired", [
    ("2026-11-13T00:00:00+00:00", False),
    ("2026-11-10T12:00:00+00:00", True),
    ("2026-11-12T08:47:05+00:00", False),
])
def test_expiration_fails_closed(when, expired):
    r = audit_source_artifact_metadata(
        metadata(expired=expired), as_of=when)
    assert r["status"] == "ORIGINAL_SOURCE_ARTIFACT_EXPIRED_OR_UNAVAILABLE"
    assert r["hours_until_metadata_expiry"] == 0


@pytest.mark.parametrize("changes", [
    {"name": "another-unverified-source"},
    {"size_in_bytes": 0},
    {"expired": "false"},
    {"id": 0},
    {"expires_at": "not a date"},
])
def test_archive_metadata_must_be_authoritative(changes):
    d = metadata()
    d.update(changes)
    with pytest.raises(ValueError):
        audit_source_artifact_metadata(d, as_of="2026-11-10T10:00:00Z")


def test_naive_local_datetime_rejected():
    with pytest.raises(ValueError, match="UTC offset"):
        audit_source_artifact_metadata(metadata(), as_of=datetime(2026, 11, 10))


def test_missing_real_original_ztf_run_cannot_imply_validated_psf():
    r = audit_v120_real_source_evidence(None)
    assert r["status"] == "ORIGINAL_CIDA11_V120_WORKFLOW_NOT_EXECUTED"
    assert r["n_original_frames_with_internal_distinct_star_model"] == 0
    assert not r["independent_original_survey_psf_calibrated"]


def test_qualified_real_3_plus_2_only_internal_profile_not_survey_calibration():
    x = audit_v120_real_source_evidence({
        "frames": [sample_frame(n_train=3, n_hold=2)],
        "n_original_exposures_with_empirical_whole_star_holdout_completed": 1,
    })
    assert x["n_original_frames_with_internal_distinct_star_model"] == 1
    assert x["status"] == "REAL_INTERNAL_WHOLE_STAR_TEST_REPORTED_NOT_SURVEY_CALIBRATION"
    assert not x["physical_gaia_ztf_identity_verified"]
    assert not x["independent_original_survey_psf_calibrated"]


@pytest.mark.parametrize("a,b", [(2, 2), (3, 1), (0, 0)])
def test_insufficient_star_counts_cannot_claim_real_holdout(a, b):
    with pytest.raises(ValueError, match="False positive"):
        audit_v120_real_source_evidence({
            "frames": [sample_frame(n_train=a, n_hold=b)],
        })


@pytest.mark.parametrize("change", [
    {"n_native_train": 5},
    {"n_native_holdout": 4},
    {"n_registered_train": 5},
    {"n_heldout_profile_reviews": 4},
    {"n_registered_holdout": -1},
    {"mjd": float("nan")},
    {"field": "FT Tau"},
    {"empirical_psf_status": "SCIENCE_CONFIRMED"},
])
def test_inconsistent_aggregates_do_not_pass_science_audit(change):
    f = sample_frame()
    f.update(change)
    with pytest.raises(ValueError):
        audit_v120_real_source_evidence({"frames": [f]})


def test_duplicate_epoch_cannot_double_count_observation():
    f = sample_frame()
    with pytest.raises(ValueError, match="MJD"):
        audit_v120_real_source_evidence({"frames": [f, f.copy()]})


def test_undeclared_success_count_rejected():
    with pytest.raises(ValueError, match="disagrees"):
        audit_v120_real_source_evidence({
            "frames": [sample_frame()],
            "n_original_exposures_with_empirical_whole_star_holdout_completed": 2,
        })


def test_training_star_leave_one_out_stability_is_descriptive_only():
    stars = synthetic_stars(7)
    result = training_subset_stability(stars[:4], stars[4:])
    assert result["n_training_subset_models"] == 4
    assert result["n_distinct_heldout_stars"] == 3
    assert result["max_abs_change_heldout_rms_over_sky_mad"] >= 0
    assert result["uses_original_daophot_psf_parameters"] is False
    assert result["real_external_astrometric_or_psf_calibration"] is False
    assert "34191110" not in str(result)


def test_stability_cannot_reuse_same_star_for_train_and_validation():
    stars = synthetic_stars(7)
    with pytest.raises(ValueError, match="Duplicate"):
        training_subset_stability(stars[:4], [stars[0], stars[5]])


def test_training_subset_check_requires_four_stars():
    stars = synthetic_stars(5)
    with pytest.raises(ValueError, match="four|>=4"):
        training_subset_stability(stars[:3], stars[3:])


def test_artificial_blend_makes_heldout_psf_residual_worse_without_modifying_input():
    stars = synthetic_stars(7)
    baseline_image = stars[4].pixels_dn.copy()
    r = synthetic_blend_falsification(
        stars[:4], stars[4:], extra_peak_dn=1000,
        offset_x_pixels=4, offset_y_pixels=-2)
    assert r["artificial_injection_increases_residual"]
    assert r["artificial_profile_flagged_for_review"]
    np.testing.assert_array_equal(stars[4].pixels_dn, baseline_image)
    assert r["original_pixel_inputs_unchanged"]
    assert not r["true_astrophysical_companion_detected"]
    assert not r["survey_completeness_or_contrast_calibrated"]
    assert "source_id" not in str(r)


@pytest.mark.parametrize("kwargs", [
    {"extra_peak_dn": -1},
    {"extra_peak_dn": 0},
    {"extra_peak_dn": 100, "offset_x_pixels": 0, "offset_y_pixels": 0},
    {"extra_peak_dn": 100, "offset_x_pixels": 20},
    {"extra_peak_dn": 100, "width_pixels": .3},
])
def test_unsafe_synthetic_blend_parameters_rejected(kwargs):
    stars = synthetic_stars(7)
    with pytest.raises(ValueError):
        synthetic_blend_falsification(stars[:4], stars[4:], **kwargs)


def test_historic_three_review_profiles_are_unresolved_not_discoveries():
    r = historic_three_residual_review_register()
    assert r["n_historic_review_profiles"] == 3
    assert r["n_physical_companions_confirmed"] == 0
    assert r["n_independent_new_source_confirmations"] == 0
    assert r["historic_values_from_v116_report_not_recomputed"]
    assert r["requires_independent_multi_epoch_multi_band_validation"]
