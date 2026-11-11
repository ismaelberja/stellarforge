"""Regression checks for *actual* 4 original ZTF FITS/PSFcat/bitmask R2 evidence.

The astrophysical image measurements are not simulated by this test.
The test only pins the original-data workflow result and its science
limits and fails if source identity/variability status is inflated.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/"reports/taurus_variability_r2/FOUR_ORIGINAL_FITS_MASK_NATIVE_PSF_SOURCE_QA_NO_RAW.json"
RECEIPT=ROOT/"reports/taurus_variability_r2/FOUR_ORIGINAL_FITS_SOURCE_QA_REAL_RUN_RECEIPT.json"


def test_actual_original_fits_evidence_matches_verifiable_actions_receipt():
    raw=EVIDENCE.read_bytes()
    d=json.loads(raw)
    receipt=json.loads(RECEIPT.read_text(encoding="utf8"))
    assert hashlib.sha256(raw).hexdigest()==receipt["original_derived_json_sha256"]
    assert receipt["actual_live_original_data_workflow_id"]==43059114825
    assert receipt["gh_original_derived_only_artifact_id"]==13873466036
    assert receipt["gh_zip_sha256"]==(
        "b782de857569a3e76df19e1d3940bf0a79f204eba2b40b33de82ee121b2b9b29")
    assert d["gaia_original_raw_response_sha256"]==(
        receipt["original_gaia_tap_response_sha256"])
    assert d["r1_frozen_seed_sha256"]==(
        receipt["original_r1_frozen_24_seed_sha256"])


def test_four_original_data_exposures_are_real_but_not_new_gaia_ztf_identities():
    x=json.loads(EVIDENCE.read_text(encoding="utf8"))
    assert x["original_technical_cohort_count"]==24
    assert x["historic_original_exposure_count"]==4
    assert x["original_target_count"]==2
    assert x["n_metadata_exact_historic_exposures_found"]==4
    assert x["n_original_native_psfcat_crowding_evaluations"]==4
    assert x["n_original_science_mask_image_pairs_evaluated"]==4
    assert x["n_original_frames_with_additional_native_psfcat_source_within_3arcsec"]==0
    assert x["n_independently_authenticated_gaia_ztf_physical_sources"]==0
    assert x["new_astrophysical_companions_or_variable_stars_confirmed"]==0
    assert x["four_original_frames_not_new_observation_epochs"] is True
    assert x["r2_science_completed"] is False
    assert x["all_24_study_source_identifications_completed"] is False
    rows=x["frames"]
    assert len(rows)==4
    assert {(r["gaia_dr3_id"],r["original_science_mjd"]) for r in rows}=={
        ("149623711269425408",58388.389016),
        ("149623711269425408",58491.184780),
        ("3419110734340795648",58475.11375),
        ("3419110734340795648",58849.135984),
    }
    assert all(r["original_metadata"]=="EXACT_HISTORIC_OID_AND_DATE_FOUND" for r in rows)
    assert all(not r["source_physical_identity_confirmed"] for r in rows)
    assert all(not r["full_r2_physical_association_completed"] for r in rows)


def test_original_native_source_distances_and_masks_are_explicitly_provisional():
    frames=json.loads(EVIDENCE.read_text(encoding="utf8"))["frames"]
    by_date={r["original_science_mjd"]:r for r in frames}
    assert [by_date[m]["native_psfcat_neighbours"]["native_psfcat_total_sources"] for m in
            (58388.389016,58491.18478,58475.11375,58849.135984)]==[
            3970,5569,5313,12355]
    for r in frames:
        cat=r["native_psfcat_neighbours"]
        img=r["science_mask_image"]
        assert cat["status"]=="ONE_NATIVE_PSF_CATALOGUE_CANDIDATE_NO_OTHER_WITHIN_3ARCSEC"
        assert cat["n_psfcat_rows_within_1arcsec"]==1
        assert cat["n_additional_native_psfcat_sources_within_3arcsec"]==0
        assert cat["original_native_catalogue_is_not_independent_physical_crossmatch"]
        assert cat["unresolved_blends_excluded"] is False
        assert cat["independently_verified_gaia_to_ztf_counterpart"] is False
        assert img["science_image_status"]=="PIXEL_WCS_PROVISIONAL_SCREEN_COMPLETED"
        assert img["original_science_mask_status"]=="MASK_CORE_NO_DISQUALIFYING_BITS_PROVISIONAL_ONLY"
        assert img["image_mask_alignment_verified"] is True
        assert img["central_local_maximum_detected"] is True
        assert img["n_additional_image_local_maxima_within_12arcsec"]==0
        assert img["source_core_bad_mask_pixels"]==0
        assert img["source_core_saturated_mask_pixels"]==0
        assert img["physical_source_id_independently_verified"] is False
        assert img["instrument_psf_or_wcs_calibrated"] is False


def test_original_data_per_exposure_ruwe_warning_persists():
    data=json.loads(EVIDENCE.read_text(encoding="utf8"))
    cida=[r for r in data["frames"] if r["historical_target_label"]=="CIDA 11"]
    ft=[r for r in data["frames"] if r["historical_target_label"]=="FT Tau"]
    assert len(ft)==len(cida)==2
    assert all(r["gaia_astrometric_quality_warning"] for r in cida)
    assert all(r["gaia_ruwe"]>8 for r in cida)
    assert all(not r["gaia_astrometric_quality_warning"] for r in ft)
    assert all(1<r["gaia_ruwe"]<1.4 for r in ft)


def test_no_raw_fits_or_new_companion_claim_sneaks_into_public_receipt():
    raw=EVIDENCE.read_text(encoding="utf8")
    receipt=RECEIPT.read_text(encoding="utf8")
    report=(ROOT/"research/taurus_variability/R2_REAL_FT_TAU_CIDA_11_FITS_SOURCE_GATES.md").read_text(encoding="utf8")
    assert '"fits_pixels":' not in raw
    assert '"original_raw_csv":' not in raw
    assert '"raw_fits_data":' not in raw
    assert '"n_confirmed_physical_gaia_ztf_associations": 0' in receipt
    assert '"n_confirmed_new_companions": 0' in receipt
    assert "not proof" in report.lower()
    assert "0/4" in report
    assert "original" in report.lower()
