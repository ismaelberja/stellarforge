"""v2.0 regression suite for public evidence boundaries and package coherence."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import re

import pytest

from scripts.audit_v2_release_manifest import (
    audit_release_manifest, REAL_COUNTS, SOURCE_SHA, RELEASE_VERSION,
)


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def manifest():
    return json.loads((ROOT/"RELEASE_MANIFEST_v2.0.json").read_text(encoding="utf8"))


def test_final_manifest_audit_requires_supported_historical_science_scope(manifest):
    result = audit_release_manifest(manifest, root=ROOT)
    assert result["status"] == "ENGINEERING_RELEASE_EVIDENCE_CONTRACT_VERIFIED"
    assert result["software_version"] == "2.0.0"
    assert result["historical_real_source_pixel_fits"] == 16
    assert result["historical_original_exposures"] == 4
    assert result["unresolved_scientific_review_profiles"] == 3
    assert result["n_evidence_paths_checked"] == 7
    assert result["real_new_distinct_star_empirical_ztf_pilot_complete"] is False
    assert result["new_scientific_discovery_confirmed"] is False


def test_real_original_residual_pass_plus_review_counts_equal_fits(manifest):
    r = manifest["historical_real_evidence"]
    assert r["provisional_source_pixel_residual_quality_passes"] + (
        r["source_pixel_residual_review_required"]
    ) == r["original_masked_psf_source_pixel_fits"]
    assert r["original_ztf_science_exposures"] == 4
    assert r["original_daophot_center_psf_model_checks"] == 4
    assert r["scientifically_confirmed_variable_stars"] == 0
    assert r["independently_confirmed_gaia_ztf_physical_source_matches"] == 0


@pytest.mark.parametrize("field,value", [
    ("source_pixel_residual_review_required", 0),
    ("original_masked_psf_source_pixel_fits", 17),
    ("independently_confirmed_gaia_ztf_physical_source_matches", 1),
    ("scientifically_confirmed_new_companions", 1),
    ("scientifically_confirmed_variable_stars", True),
    ("original_irsa_positional_query_rows", 2213),
])
def test_real_observational_numbers_cannot_be_forged(manifest, field, value):
    manifest["historical_real_evidence"][field] = value
    with pytest.raises(ValueError, match="Real evidence"):
        audit_release_manifest(manifest, root=ROOT)


@pytest.mark.parametrize("key", [
    "original_ztf_daophot_training_source_roster_verified",
    "independent_ztf_psf_wcs_error_calibration_completed",
    "true_correlated_ccd_instrument_noise_model_calibrated",
    "native_gaia_ztf_physical_identification_authenticated",
])
def test_no_independent_instrument_science_claims_without_evidence(manifest, key):
    manifest["external_calibration"][key] = True
    with pytest.raises(ValueError, match="Unverified instrumental"):
        audit_release_manifest(manifest, root=ROOT)


@pytest.mark.parametrize("key,value", [
    ("v120_new_empirical_whole_star_real_pilot_executed", True),
    ("last_published_baseline_test_passes", 999),
    ("last_published_baseline_github_actions_run_id", 0),
])
def test_mocks_and_real_manual_survey_run_must_remain_separate(manifest,key,value):
    manifest["software_validation"][key] = value
    with pytest.raises(ValueError, match="Historical test"):
        audit_release_manifest(manifest, root=ROOT)


def test_public_recovery_digest_does_not_authenticate_source_identity(manifest):
    assert manifest["raw_original_input_recovery"]["original_zip_sha256"] == SOURCE_SHA
    assert (manifest["raw_original_input_recovery"]
            ["physical_target_identity_confirmed_by_archive_integrity"] is False)
    assert (manifest["raw_original_input_recovery"]
            ["recovered_raw_archive_committed_to_git"] is False)


def test_malformed_sha_rejects_portfolio_release(manifest):
    manifest["raw_original_input_recovery"]["original_zip_sha256"] = "0"*64
    with pytest.raises(ValueError, match="Original transport"):
        audit_release_manifest(manifest, root=ROOT)


def test_manifest_may_not_refer_to_forged_or_missing_science_evidence(manifest):
    manifest["release_evidence_paths"].append("raw/private_gaia_ZTF_FITS.fits")
    with pytest.raises(ValueError, match="evidence paths"):
        audit_release_manifest(manifest, root=ROOT)


def test_package_and_public_docs_parity_for_release(manifest):
    from stellarforge import __version__
    assert RELEASE_VERSION == manifest["software_version"] == "2.0.0"
    assert __version__ == "2.1.0"  # Current package; v2.0 is archival evidence
    readme = (ROOT/"README.md").read_text(encoding="utf8")
    assert "StellarForge v2.1" in readme
    assert "RELEASE_MANIFEST_v2.0.json" in readme
    assert "PSF" in readme
    assert "2.0.0" in readme
    assert "752" in readme
    assert "independent" in readme.lower()
    assert (ROOT/"docs/V2_PORTFOLIO_CV_ES_EN.md").is_file()
    assert (ROOT/"docs/V2_REPRODUCIBILITY_AND_SCIENCE_LIMITS.md").is_file()
    assert (ROOT/"docs/HISTORIC_README_v1.22.md").is_file()


def test_preserve_exact_previous_release_counts(manifest):
    assert REAL_COUNTS["catalogue_mirror_rows"] == 532
    assert REAL_COUNTS["catalogue_gaia_id_rows"] == 467
    assert manifest["software_validation"]["last_published_baseline_test_passes"] == 752


def test_no_raw_file_uploads_in_public_release_manifest(manifest):
    content = json.dumps(manifest)
    assert "pixels_dn" not in content
    assert "source_stamp" not in content
    assert "PSF_CATALOGUE_RAW_ROWS" not in content
    for path in manifest["release_evidence_paths"]:
        assert not path.endswith((".fits",".csv",".zip",".parquet"))
