"""Pin genuine external MAST PS1 DR2/ZTF original source-color reference results.

All assertions are off-line; source inputs came from original API run.
No raw PS1 source IDs, Gaia astrometry, ZTF fluxes or FITS are stored.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT/"reports/taurus_variability_r2/FTTAU_REAL_ORIGINAL_MAST_PS1_DR2_EXTERNAL_SOURCE_COLOR_PILOT_NO_RAW.json"
RECEIPT = ROOT/"reports/taurus_variability_r2/FTTAU_EXTERNAL_PS1_DR2_GENUINE_ORIGINAL_SOURCE_PILOT_RECEIPT.json"
PRIOR = ROOT/"reports/taurus_variability_r2/FTTAU_720_REAL_NATIVE_ENSEMBLE_ZTF_PS1_PIPELINE_HEADER_NO_RAW.json"
IMAGES = ROOT/"reports/taurus_variability_r2/FT_TAU_TWO_ORIGINAL_ZTF_FIELDS_GR_FITS_MASK_PSF_DERIVED_NO_RAW.json"
REPORT = ROOT/"research/taurus_variability/R2_REAL_FTTAU_EXTERNAL_MAST_PS1_DR2_SOURCE_COLOR_RESULTS.md"

def _data():
    return json.loads(EVIDENCE.read_text(encoding="utf8"))

def _receipt():
    return json.loads(RECEIPT.read_text(encoding="utf8"))


def test_real_original_MAST_source_response_artifact_hash_and_fixed_24_taurus_seed():
    x=_data()
    r=_receipt()
    assert hashlib.sha256(EVIDENCE.read_bytes()).hexdigest()==r[
        "source_uncompressed_derived_json_sha256"]
    assert r["authentic_original_survey_workflow_run"]==43102892830
    assert r["original_derived_artifact_id"]==13892248204
    assert r["source_zip_sha256"]==(
        "914bfa3061867451c15d9a0fdb712f958f61f38cac9b21e7d116dd14282ea12d")
    assert r["original_independent_mast_PS1_DR2_raw_csv_sha256"]==x[
        "external_PS1_DR2_original_source_query"]["original_ps1_dr2_response_sha256"]
    assert x["frozen_nonrepresentative_taurus_gaia_seed_count"]==24
    assert x["fixed_original_ft_tau_ztf_oid_count"]==4
    assert x["n_new_original_ZTF_science_observation_epochs_selected"]==0
    assert x["original_r1_gaia_technical_seed_sha256"]==r[
        "unchanged_original_r1_technical_seed_sha256"]
    assert hashlib.sha256(PRIOR.read_bytes()).hexdigest()==x[
        "immutable_previous_720_reference_evidence_sha256"]
    assert hashlib.sha256(IMAGES.read_bytes()).hexdigest()==x[
        "immutable_previous_four_original_images_evidence_sha256"]


def test_real_external_ps1_1780_rows_405_preselected_and_4_verified_ztf_source_catalogues():
    x=_data()
    external=x["external_PS1_DR2_original_source_query"]
    assert external["status"]=="MAST_ORIGINAL_PS1_DR2_MEAN_SOURCE_CATALOGUE_VALID"
    assert external["n_ps1_original_rows"]==1780
    assert external["n_ps1_good_color_crowding_sources"]==405
    assert len(external["original_ps1_dr2_response_sha256"])==64
    assert x["n_original_ZTF_full_native_psfcats_reverified"]==4
    assert x["n_same_band_PanSTARRS_source_level_internal_pilot_passes"]==2
    assert x["n_scientifically_certified_absolute_ZTF_PanSTARRS_calibrations"]==0
    assert {y["band"] for y in x["bands"]}=={"g","r"}
    prior=json.loads(IMAGES.read_text(encoding="utf8"))
    hashes={a["selection"]["ztf_oid"]:a["native_full_catalogue_sha256"]
            for a in prior["original_fits_mask_native_psf_exposure_results"]}
    for band in x["bands"]:
        assert len(band["original_native_source_inputs"])==2
        for item in band["original_native_source_inputs"]:
            assert item["original_full_native_psfcat_sha_match"] is True
            assert item["original_full_native_psfcat_sha256"]==hashes[item["original_oid"]]
            assert item["field"] in ("1605","609")


def test_original_cross_survey_PS1_source_triplets_training_holdout_and_empirical_colors():
    x={a["band"]:a["independent_external_PS1_source_level_color_test"]
       for a in _data()["bands"]}
    expected={
        "g":(82,42,40,[(26.19613,-.03648,-.00946,.0359),
                      (26.08484,-.05456,.00127,.02735)]),
        "r":(180,94,86,[(26.14535,.10425,.00318,.02444),
                       (26.14388,.11878,-.00014,.02454)]),
    }
    for band,(n,train,hold,fields) in expected.items():
        b=x[band]
        assert b["status"]=="PS1_EXTERNAL_SOURCE_LEVEL_PILOT_INTERNAL_HOLDOUT_PASS"
        assert b["n_independently_queried_PS1_unique_reference_triplets"]==n
        assert b["n_train"]==train
        assert b["n_heldout"]==hold
        assert train+hold==n
        assert b["both_fields_ps1_mean_color_holdout_qc_pass"] is True
        assert len(b["per_original_ZTF_field_fits"])==2
        assert [z["field"] for z in b["per_original_ZTF_field_fits"]]==["1605","609"]
        for item,values in zip(b["per_original_ZTF_field_fits"],fields):
            intercept,slope,median,scatter=values
            assert item["PS1_minus_native_instrumental_intercept_mag"]==intercept
            assert item["PS1_gr_empirical_slope_mag_per_mag"]==slope
            assert item["heldout_median_residual_mag"]==median
            assert item["heldout_robust_residual_scatter_mag"]==scatter
            assert item["n_holdout"]==hold
            assert item["n_train"]==train
            assert item["n_train_after_clipping"]>=10
            assert item["status"]=="PS1_SOURCE_LEVEL_INTERNAL_HELDOUT_PILOT_PASS"
            assert item["full_absolute_calibration_uncertainty_certified"] is False
            assert item["formal_color_transformation_calibrated"] is False
            assert item["physical_gaia_ZTF_FT_Tau_match_confirmed"] is False
        assert b["external_PanSTARRS_photometric_source_identification_for_FT_TAU"] is False
        assert b["full_absolute_photometric_calibration_certified"] is False
        assert b["original_ZTF_lightcurves_merged"] is False


def test_both_original_external_reference_pilots_still_block_source_discovery_and_oid_merges():
    x=_data()
    r=_receipt()
    assert x["n_independently_authenticated_gaia_ztf_FT_TAU_physical_counterparts"]==0
    assert x["n_merged_ztf_object_id_lightcurves"]==0
    assert x["n_confirmed_new_FT_TAU_variables_or_companions"]==0
    assert x["research_R2_full_physical_source_identity_complete"] is False
    assert r["n_independently_certified_absolute_photometric_calibrations"]==0
    assert r["n_independently_authenticated_Gaia_ZTF_physical_matches"]==0
    assert r["n_merged_ZTF_ObjectID_lightcurves"]==0
    assert r["n_confirmed_new_FT_TAU_variables_or_companions"]==0
    assert r["r2_physical_source_identity_science_complete"] is False
    assert r["external_PanSTARRS_source_rows_and_individual_identifiers_committed"] is False
    text=EVIDENCE.read_text(encoding="utf8")
    for forbidden in ('"original_ps1_rows":','"ps1_ids":','"original_source_positions":',
                      '"ra":','"dec":','"mag":','"flux":','"raw_fits":',
                      '"individual_FT_TAU_timeseries":'):
        assert forbidden not in text
    report=REPORT.read_text(encoding="utf8")
    for token in ("1,780","405","82","180","26.19613",
                  "26.08484","26.14535","26.14388",
                  "0.03590","NOT PASSED","Gaia–ZTF"):
        assert token in report
