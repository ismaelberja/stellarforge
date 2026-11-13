"""v2.0: offline, fail-closed software-evidence manifest audit.

This audits the archived v2.0 evidence baseline even if package v2.1
is installed. It is NOT a replacement for an
independent astronomical, original archive or GitHub Actions CI audit.
It intentionally refuses any positive new science or calibration claim.
Original FITS, Gaia/IRSA source tables and stellar PSFs are not accessed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from stellarforge import __version__

RELEASE_VERSION = "2.0.0"
SOURCE_SHA = "d54246e00d4cf343b0b062b9eb92034e51c735067274a8109e9b2c2c2a2d5167"
REAL_COUNTS = {
    "catalogue_mirror_rows": 532,
    "catalogue_gaia_id_rows": 467,
    "original_irsa_positional_query_rows": 2212,
    "original_ztf_science_exposures": 4,
    "original_daophot_center_psf_model_checks": 4,
    "original_masked_psf_source_pixel_fits": 16,
    "provisional_source_pixel_residual_quality_passes": 13,
    "source_pixel_residual_review_required": 3,
    "independently_confirmed_gaia_ztf_physical_source_matches": 0,
    "scientifically_confirmed_variable_stars": 0,
    "scientifically_confirmed_new_companions": 0,
}
EXTERNAL_BLOCKERS = (
    "original_ztf_daophot_training_source_roster_verified",
    "independent_ztf_psf_wcs_error_calibration_completed",
    "true_correlated_ccd_instrument_noise_model_calibrated",
    "source_aware_scientific_variability_confirmed",
    "native_gaia_ztf_physical_identification_authenticated",
)
EXPECTED_PATHS = {
    "reports/selection_bias_v1.1/REPORT.md",
    "reports/observational_intake_v1.2/RAW_TRANSPORT_AUDIT.md",
    "reports/spatial_daophot_v1.15/REAL_DAOPHOT_CENTER_AND_LOCAL_SHAPES.md",
    "reports/masked_spatial_psf_v1.16/REAL_ZTF_PIXEL_RESIDUALS_EVIDENCE.md",
    "reports/new_gaia_holdouts_v1.17/REAL_DISJOINT_GAIA_CONTROL_AND_SHIFTED_SKY_RESULTS.md",
    "reports/recovered_archive_v1.22/ARCHIVE_INTEGRITY_AND_MOCKED_PILOT_AUDIT.md",
    "data/research_seed/V122_ORIGINAL_IRSA_ARTIFACT_RECEIPT_NO_RAW.json",
}
EXPECTED_KEYS = {
    "schema_version", "software_version", "release_date_utc", "release_scope",
    "evidence_type", "historical_real_evidence",
    "raw_original_input_recovery", "software_validation",
    "external_calibration", "release_evidence_paths",
    "unresolved_scientific_work", "transparent_software_assistance",
}


def _exact(mapping: dict, expected: dict, description: str) -> None:
    if (not isinstance(mapping, dict) or set(mapping) != set(expected)
            or any(type(mapping[k]) is not type(v) or mapping[k] != v
                   for k, v in expected.items())):
        raise ValueError(f"{description} differs from authenticated historical claims")


def audit_release_manifest(manifest: dict, *, root: Path) -> dict:
    """Verify bounded facts, project files and critical caveats for portfolio."""
    if not isinstance(manifest, dict) or set(manifest) != EXPECTED_KEYS:
        raise ValueError("Unexpected v2.0 release manifest fields")
    if (manifest["schema_version"] != "stellarforge-v2.0-software-evidence-manifest-v1"
            or manifest["software_version"] != RELEASE_VERSION
            or manifest["release_scope"] !=
            "ENGINEERING_PORTFOLIO_RELEASE_WITH_UNCONFIRMED_ASTRONOMICAL_SOURCE_IDENTITIES"
            or manifest["evidence_type"] !=
            "SEPARATE_REAL_HISTORICAL_DATA_FROM_SYNTHETIC_TESTS"):
        raise ValueError("Manifest does not describe an engineering-only v2.0 release")
    if not re.fullmatch(r"20\d{2}-\d{2}-\d{2}", str(manifest["release_date_utc"])):
        raise ValueError("Release date is malformed")
    _exact(manifest["historical_real_evidence"], REAL_COUNTS, "Real evidence counts")
    raw = manifest["raw_original_input_recovery"]
    _exact(raw, {
        "source_artifact_workflow_run_id": 41997079598,
        "source_artifact_id": 13401380025,
        "original_zip_sha256": SOURCE_SHA,
        "recovered_raw_archive_committed_to_git": False,
        "archived_bytes_integrity_matched_original_actions_metadata": True,
        "physical_target_identity_confirmed_by_archive_integrity": False,
    }, "Original transport recovery")

    verified = manifest["software_validation"]
    _exact(verified, {
        "last_published_baseline_github_actions_run_id": 42809011151,
        "last_published_baseline_test_passes": 752,
        "baseline_tests_includes_synthetic_simulated_scientific_cases": True,
        "original_masked_ztf_science_pixel_fits_recorded_in_older_versions": True,
        "v120_new_empirical_whole_star_real_pilot_executed": False,
        "v120_new_empirical_whole_star_pilot_synthetic_end_to_end_test_passed": True,
        "all_released_source_code_ci_gate": "CI must pass on final main merge commit",
    }, "Historical test evidence")

    external = manifest["external_calibration"]
    if set(external) != set(EXTERNAL_BLOCKERS) or any(
        external[k] is not False for k in EXTERNAL_BLOCKERS
    ):
        raise ValueError("Unverified instrumental/science claims cannot be true")
    tasks = manifest["unresolved_scientific_work"]
    if (not isinstance(tasks, list) or len(tasks) < 4
            or len(tasks) > 10 or any(
                not isinstance(s, str) or len(s) < 30 for s in tasks)):
        raise ValueError("Scientific limitations are missing from release")
    if not isinstance(manifest["transparent_software_assistance"], str):
        raise ValueError("Software provenance transparency is required")

    evidence = manifest["release_evidence_paths"]
    if (not isinstance(evidence, list) or len(evidence) != len(EXPECTED_PATHS)
            or len(set(evidence)) != len(evidence)
            or set(evidence) != EXPECTED_PATHS):
        raise ValueError("Incomplete or extra science evidence paths")
    base = Path(root).resolve()
    for path in evidence:
        file = base / path
        if (file.is_symlink() or not file.is_file()
                or not file.resolve().is_relative_to(base)):
            raise ValueError("Required source evidence is missing or not local")

    receipt = json.loads((
        base / "data/research_seed/V122_ORIGINAL_IRSA_ARTIFACT_RECEIPT_NO_RAW.json"
    ).read_text(encoding="utf8"))
    if (receipt.get("recovered_original_zip_sha256") != SOURCE_SHA
            or receipt.get("raw_source_data_committed_to_git") is not False
            or receipt.get("original_source_query_physical_identity_verified") is not False):
        raise ValueError("Original scientific source receipt is inconsistent")

    project_text = (base / "pyproject.toml").read_text(encoding="utf8")
    current_version_match = re.search(r'(?m)^version = "([^"]+)"$', project_text)
    if (not current_version_match
            or current_version_match.group(1) != __version__
            or __version__ not in ("2.0.0", "2.1.0")):
        raise ValueError("Source package and release versions disagree")
    return {
        "status": "ENGINEERING_RELEASE_EVIDENCE_CONTRACT_VERIFIED",
        "software_version": RELEASE_VERSION,
        "historical_real_source_pixel_fits": REAL_COUNTS["original_masked_psf_source_pixel_fits"],
        "historical_original_exposures": REAL_COUNTS["original_ztf_science_exposures"],
        "unresolved_scientific_review_profiles": REAL_COUNTS["source_pixel_residual_review_required"],
        "n_evidence_paths_checked": len(EXPECTED_PATHS),
        "release_ci_still_must_pass_on_final_main": True,
        "real_new_distinct_star_empirical_ztf_pilot_complete": False,
        "new_scientific_discovery_confirmed": False,
        "external_instrument_psf_wcs_calibration_verified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Offline v2.0 software evidence consistency check, no live astronomy")
    parser.add_argument(
        "--manifest", type=Path, default=Path("RELEASE_MANIFEST_v2.0.json"))
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    doc = json.loads(args.manifest.read_text(encoding="utf8"))
    print(json.dumps(audit_release_manifest(doc, root=args.root), indent=2))


if __name__ == "__main__":
    main()
