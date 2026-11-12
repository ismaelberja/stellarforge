"""Lock authentic six-original native DAOPhot full-source PSF and image evidence."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EVID=ROOT/"reports/taurus_variability_r2/FTTAU_SIX_ORIGINAL_NATIVE_SPATIAL_DAOPHOT_PSF_NO_RAW.json"
OLD=ROOT/"reports/taurus_variability_r2/FTTAU_SIX_ORIGINAL_ZTF_INDEPENDENT_GAUSSIAN_PIXELS_NO_RAW.json"


def test_six_exact_native_spatial_psf_source_image_original_checksums_and_qa_counts():
    evidence=json.loads(EVID.read_text(encoding="utf8"))
    old=json.loads(OLD.read_text(encoding="utf8"))
    assert evidence["original_data_run_id"]==43310945601
    assert evidence["original_data_artifact_id"]==13986790868
    assert len(evidence["original_data_artifact_zip_sha256"])==64
    assert len(evidence["original_data_derived_json_sha256"])==64
    assert evidence["original_previous_ledger_sha256"]["original_gaussian_six"]==hashlib.sha256(OLD.read_bytes()).hexdigest()
    assert evidence["original_full_native_psfcats_sha_verified"]==6
    assert evidence["original_science_mask_pairs_sha_verified"]==6
    assert evidence["original_native_spatial_daophot_models_parsed"]==6
    assert evidence["original_center_psf_stamp_reconstructions_approximately_consistent"]==6
    assert evidence["original_native_spatial_same_source_pixel_numeric_fits"]==6
    assert evidence["original_native_spatial_same_source_pixel_provisional_quality_passes"]==4
    assert evidence["original_native_spatial_same_source_pixel_residual_review_required"]==2
    rows=evidence["original_six_exact_exposure_derived_only"]
    prev=old["six_immutable_original_data_exposure_derived_summary"]
    assert len(rows)==len(prev)==6
    for now,former in zip(rows,prev):
        assert (now["band"],now["field"],now["original_mjd"],now["original_filefracday"])==(
            former["band"],str(former["field"]),former["mjd"],former["fracday"])
        assert now["original_full_psfcat_sha256"]==former["native_sha"]
        assert now["original_science_cutout_sha256"]==former["science_sha"]
        assert now["original_same_exposure_mask_sha256"]==former["mask_sha"]
        assert now["original_native_nearest_source_chi"]==former["chi"]
        assert len(now["original_native_spatial_dao_psf_sha256"])==64
        assert len(now["original_native_field_center_psf_sha256"])==64
        assert now["model_vs_original_field_center_cosine_similarity"]>=.93
        assert now["model_vs_original_field_center_normalized_l1"]<=.5
        assert now["native_dao_lookup_tables"] in (1,3,6)
        assert now["same_source_checkerboard_holdout_rms_over_sky_mad"]>0
        assert now["source_specific_psf_independently_calibrated"] is False
        assert now["physical_gaia_to_ztf_ft_tau_identity_confirmed"] is False
    assert len({x["original_native_spatial_dao_psf_sha256"] for x in rows})==6
    assert len({x["original_native_field_center_psf_sha256"] for x in rows})==6


def test_all_three_original_chi_bad_sources_stay_failed_even_if_native_spatial_pixel_screen_passes():
    rows=json.loads(EVID.read_text())["original_six_exact_exposure_derived_only"]
    late=[x for x in rows if x["epoch_role"]=="LATE"]
    assert len(late)==3
    assert [x["original_native_nearest_source_chi"] for x in late]==[
        .456,.424,.383]
    assert all(x["original_native_chi_source_quality_pass_unchanged"] is False for x in late)
    assert [x["same_image_spatial_psf_residual_screen_status"] for x in late]==[
        "PROVISIONAL_ORIGINAL_MASKED_PSF_PIXEL_RESIDUAL_SCREEN_PASSED",
        "PROVISIONAL_ORIGINAL_MASKED_PSF_PIXEL_RESIDUAL_SCREEN_PASSED",
        "ORIGINAL_MASKED_PSF_PIXEL_RESIDUAL_REVIEW_REQUIRED"]
    assert rows[4]["original_native_chi_source_quality_pass_unchanged"] is True
    assert rows[4]["same_image_spatial_psf_residual_screen_status"]=="ORIGINAL_MASKED_PSF_PIXEL_RESIDUAL_REVIEW_REQUIRED"


def test_new_evidence_does_not_claim_source_identity_or_reference_star_calibration():
    d=json.loads(EVID.read_text())
    assert d["original_candidate_native_quality_statuses_changed"]==0
    assert d["original_native_candidate_5_of_8_pass_3_of_8_fail_unchanged"] is True
    assert d["original_1_of_4_quality_accepted_two_night_pairs_unchanged"] is True
    assert d["independent_instrument_noise_wcs_psf_covariance_calibrated"] is False
    assert d["independently_authenticated_physical_gaia_ztf_source_matches"]==0
    assert d["independently_confirmed_new_variables_or_companions"]==0
    assert d["merged_original_ztf_oid_lightcurves"]==0
    assert d["scientific_r2_complete"] is False
    assert d["no_original_source_catalogue_rows_or_model_coefficients_saved"] is True
    assert d["no_original_science_or_mask_pixel_data_saved"] is True
    assert d["no_raw_source_flux_or_fitted_amplitudes_saved"] is True
