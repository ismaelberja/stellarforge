"""Adversarial offline v2.1 portfolio source-evidence and visual acceptance tests.

v2.0 original receipts are preserved, v2.1 adds later fixed real-data
observations but never equates an external name alias to a ZTF physical star.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from scripts.audit_v21_release_manifest import (
    RELEASE_VERSION, PRE_RELEASE_EVIDENCE, audit_v21_release_manifest,
)
from stellarforge import __version__

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"RELEASE_MANIFEST_v2.1.json"


@pytest.fixture
def manifest():
    return json.loads(MANIFEST.read_text(encoding="utf8"))


def test_new_v21_evidence_contract_accepts_reproducible_real_source_counts(manifest):
    result=audit_v21_release_manifest(manifest,root=ROOT)
    assert result["status"]=="V21_ENGINEERING_PORTFOLIO_EVIDENCE_VERIFIED_NO_ASTROPHYSICAL_DISCOVERY"
    assert result["software_version"]==RELEASE_VERSION==__version__=="2.1.0"
    assert result["previous_v20_manifest_original_claim_counts_preserved"] is True
    assert result["n_new_six_epoch_original_source_psfcat_hashes_cross_reconciled"]==6
    assert result["n_native_spatial_same_image_provisional_residual_passes"]==4
    assert result["n_native_spatial_same_image_residual_reviews"]==2
    assert result["n_chi_blind_original_reference_catalogue_entries"]==1095
    assert result["n_chi_blind_original_reference_entries_below_prior_lower_gate"]==240
    assert result["external_name_gaia_simbad_alias_supported"] is True
    assert result["original_ztf_per_source_physical_identity_authenticated"] is False
    assert result["new_astrophysical_discovery_claimed"] is False
    assert result["n_original_evidence_paths_checked"]==len(PRE_RELEASE_EVIDENCE)==10


@pytest.mark.parametrize("field,value",[
    ("software_version","2.0.0"),
    ("release_scope","ASTROPHYSICAL_DISCOVERY"),
    ("release_date_utc","2026-11-12"),
])
def test_no_mislabelled_version_scope_or_date(manifest,field,value):
    manifest[field]=value
    with pytest.raises(ValueError):
        audit_v21_release_manifest(manifest,root=ROOT)


@pytest.mark.parametrize("section,key,value",[
    ("historical_release_baseline","prior_original_irsa_positional_rows",99999),
    ("historical_release_baseline","prior_sixteen_original_source_image_profile_fits",22),
    ("original_followup_2026_11_12","original_ztf_source_qa_failed_count",0),
    ("original_followup_2026_11_12","original_valid_two_night_source_pairs_count",4),
    ("original_followup_2026_11_12","frozen_original_ztf_exposure_count",12),
])
def test_historical_counts_and_original_source_qa_never_retroactively_improved(manifest,section,key,value):
    manifest[section][key]=value
    with pytest.raises(ValueError):
        audit_v21_release_manifest(manifest,root=ROOT)


@pytest.mark.parametrize("section,key,value",[
    ("original_chi_blind_reference","image_catalogue_rows_in_reference_cohorts",1094),
    ("original_chi_blind_reference","image_catalogue_reference_records_chi_below_0p5",0),
    ("original_analytic_gaussian_pixel_pilot","numeric_analytic_gaussian_pixel_fits",6),
    ("original_spatial_daophot_psf","same_source_spatial_psf_numeric_fits",7),
    ("original_spatial_daophot_psf","provisional_same_source_heldout_pixel_residual_passes",6),
    ("original_spatial_daophot_psf","same_source_pixel_residual_reviews_required",0),
    ("external_curated_simbad_alias","both_queries_same_unique_external_object",False),
    ("external_curated_simbad_alias","physical_gaia_to_original_ztf_counterpart_confirmed",True),
])
def test_immutable_original_ztf_and_simbad_observation_results(manifest,section,key,value):
    manifest["original_followup_2026_11_12"][section][key]=value
    with pytest.raises(ValueError):
        audit_v21_release_manifest(manifest,root=ROOT)


@pytest.mark.parametrize("claim",[
    "all_four_ztf_object_ids_authenticated_as_one_physical_gaia_star",
    "independent_gaia_to_ztf_per_epoch_physical_source_identification_confirmed",
    "independent_psf_wcs_instrumental_covariance_calibrated",
    "authentic_original_daophot_psf_training_star_roster_confirmed",
    "new_astrophysical_variability_or_companion_confirmed",
    "original_ztf_oid_lightcurves_merged",
    "r2_scientific_source_identity_finished",
    "r3_astrophysical_inference_ready",
    "new_cida11_whole_star_empirical_psf_live_pilot_completed",
    "previous_original_native_chi_gate_relaxed",
])
def test_reject_all_unverified_physical_astrophysical_discovery_claims(manifest,claim):
    manifest["science_claim_boundaries"][claim]=True
    with pytest.raises(ValueError):
        audit_v21_release_manifest(manifest,root=ROOT)


def test_preserve_simbad_curated_name_alias_but_not_claim_independent_physical_id(manifest):
    true_alias=manifest["science_claim_boundaries"]
    assert true_alias["catalogue_name_alias_verified"] is True
    assert true_alias["all_four_ztf_object_ids_authenticated_as_one_physical_gaia_star"] is False
    assert manifest["original_followup_2026_11_12"]["external_curated_simbad_alias"]["external_catalogue_main_id"]=="V* FT Tau"
    true_alias["catalogue_name_alias_verified"]=False
    with pytest.raises(ValueError):
        audit_v21_release_manifest(manifest,root=ROOT)


def test_no_private_original_source_payloads_in_release_manifest_or_charts(manifest):
    for p in manifest["release_evidence_paths"]:
        assert p.endswith((".md",".json",".svg"))
        assert not p.endswith((".fits",".csv",".zip",".parquet"))
        assert (ROOT/p).is_file()
    text=MANIFEST.read_text(encoding="utf8")
    for secret in ("raw_pixel_arrays","science_stamp_data","catalogue_rows_raw",
                   "unpublished_ALMA_FITS"):
        assert secret not in text


def test_new_original_data_derived_chart_accessible_and_source_locked(manifest):
    svgpath=ROOT/manifest["visual_evidence"]["new_real_derived_only_chart"]
    text=svgpath.read_text(encoding="utf8")
    root=ET.fromstring(text)
    assert root.tag=="{http://www.w3.org/2000/svg}svg"
    assert root.attrib.get("role")=="img"
    assert len(root.find("{http://www.w3.org/2000/svg}title").text)>30
    assert "NOT independent" in text or "not an independent" in text
    assert "Original native PSF" not in text or "χ" in text
    assert "Source:" in text
    assert "6/6" not in text or "original" in text
    assert not root.findall(".//{http://www.w3.org/2000/svg}script")
    assert not root.findall(".//{http://www.w3.org/2000/svg}image")
    receipts=json.loads((ROOT/"reports/taurus_variability_r2/FTTAU_SIX_ORIGINAL_NATIVE_SPATIAL_DAOPHOT_PSF_NO_RAW.json").read_text("utf8"))
    for row in receipts["original_six_exact_exposure_derived_only"]:
        numeric=row["same_source_checkerboard_holdout_rms_over_sky_mad"]
        assert f"{numeric:.3f}" in text
        assert row["band"] in text
    assert "4/6 internal residual screens pass" in text
    assert "2/6 require review" in text


def test_v21_online_urls_are_reference_only_and_v20_release_receipts_unchanged(manifest):
    for path in ("docs/V21_GUIA_ES.md","docs/V21_PORTFOLIO_CV_ES_EN.md",
                 "docs/V21_REPRODUCIBILITY_AND_SCIENCE_LIMITS.md",
                 "docs/V21_VISUAL_EVIDENCE.md","RELEASE_NOTES_v2.1.md",
                 "docs/V21_RELEASE_ACCEPTANCE_PLAN.md"):
        assert (ROOT/path).is_file()
    guide=(ROOT/"docs/V21_GUIA_ES.md").read_text(encoding="utf8")
    assert "no" in guide.lower() and "SIMBAD" in guide and "Gaia DR3" in guide
    notes=(ROOT/"RELEASE_NOTES_v2.1.md").read_text(encoding="utf8")
    assert "No" in notes and "2.1.0" in notes
    assert manifest["engineering_validation"]["final_v21_git_main_ci_required"] is True
