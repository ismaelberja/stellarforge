"""Immutable original-data FT Tau Gaia/PS1/ZTF target-astrometry evidence lock."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"reports/taurus_variability_r2/FTTAU_GAIA_PS1_ZTF_FOUR_ORIGINAL_TARGET_ASTROMETRY_NO_RAW.json"
RECEIPT=ROOT/"reports/taurus_variability_r2/FTTAU_REAL_GAIA_PS1_ZTF_TARGET_ASTROMETRY_RUN_RECEIPT.json"
REPORT=ROOT/"research/taurus_variability/R2_REAL_FTTAU_GAIA_PS1_ZTF_TARGET_ASTROMETRY_RESULTS.md"
ORIGINAL=ROOT/"reports/taurus_variability_r2/FT_TAU_TWO_ORIGINAL_ZTF_FIELDS_GR_FITS_MASK_PSF_DERIVED_NO_RAW.json"
EXTERNAL=ROOT/"reports/taurus_variability_r2/FTTAU_REAL_ORIGINAL_MAST_PS1_DR2_EXTERNAL_SOURCE_COLOR_PILOT_NO_RAW.json"

def _load():
    return json.loads(DATA.read_text("utf8"))

def test_original_archive_SHA_and_fixed_observational_inputs():
    r=json.loads(RECEIPT.read_text("utf8"))
    d=_load()
    assert hashlib.sha256(DATA.read_bytes()).hexdigest()==r["original_derived_no_raw_json_sha256"]
    assert r["original_archive_workflow_run_id"]==43188238685
    assert r["original_derived_artifact_id"]==13929113546
    assert r["original_artifact_zip_sha256"]==(
        "c84a32e4ecbdc8de7cb178bb92797ed48db5cd793b80e5cd7a8c21129e611666")
    assert d["original_gaia_TAP_response_sha256"]==r["original_gaia_five_parameter_csv_sha256"]
    assert d["original_external_PS1_MAST_response_sha256"]==r["original_new_MAST_PS1_mean_csv_sha256"]
    assert d["prior_original_four_images_ledger_sha256"]==hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()
    assert d["prior_original_external_ps1_source_ledger_sha256"]==hashlib.sha256(EXTERNAL.read_bytes()).hexdigest()
    assert d["frozen_nonrepresentative_taurus_technical_seed_size"]==24
    assert d["gaia_ft_tau_original_source_id"]=="149623711269425408"


def test_ps1_new_archive_snapshot_is_explicitly_flagged_not_an_identical_repeat():
    r=json.loads(RECEIPT.read_text("utf8"))
    d=_load()
    assert d["original_external_PS1_response_status"]==(
        "COMPLETE_ORIGINAL_MAST_PS1_RESPONSE_SHA_CHANGED_REVIEW")
    assert d["original_external_PS1_sha_equal_previous_snapshot"] is False
    assert d["original_external_PS1_MAST_response_sha256"]!=(
        d["original_external_PS1_previous_snapshot_sha256"])
    assert d["n_original_PS1_mean_rows_valid"]==1780
    assert d["n_original_gaia_5p_records_verified"]==1
    assert d["n_original_native_ztf_PSFcat_SHA_verified"]==4
    assert r["original_MAST_PS1_snapshot_sha_equal_previous"] is False
    assert r["PS1_source_epoch_and_own_proper_motion_validated"] is False
    assert r["independent_ZTF_WCS_full_systematic_error_budget_validated"] is False


def test_four_original_ztf_target_candidates_have_true_gaia_position_proximity_and_still_no_verified_identity():
    d=_load()
    prior=json.loads(ORIGINAL.read_text("utf8"))
    expected_sha={x["selection"]["ztf_oid"]:x["native_full_catalogue_sha256"]
                  for x in prior["original_fits_mask_native_psf_exposure_results"]}
    assert d["fixed_original_ztf_exposures"]==4
    assert d["n_original_target_exposures_with_provisional_native_source_candidate"]==4
    assert d["n_same_filter_pairs_with_two_provisional_target_candidates"]==2
    frames=d["original_four_exposure_target_candidate_details"]
    assert len(frames)==4
    measured={
        ("g","1605"):(.056791,12.397513,-.035503,.006418),
        ("g","609"):(.069015,46.446880,.000734,.035893),
        ("r","1605"):(.035434,20.317638,-.004080,.009709),
        ("r","609"):(.063244,10.221781,.011431,.036079),
    }
    for f in frames:
        k=(f["band"],f["field"])
        first,second,east,north=measured[k]
        t=f["target_native_candidate"]
        assert f["original_PSF_catalogue_SHA256_verified"] is True
        assert f["original_full_native_PSF_catalogue_sha256"]==expected_sha[
            f["ztf_original_oid"]]
        assert f["gaia_original_5p_motion_and_parallax_model_available"] is True
        assert t["status"]=="PROVISIONAL_GAIA_NEAREST_ZTF_PSF_SOURCE_GEOMETRY_PASS"
        assert t["n_original_native_psf_sources_within_2arcsec"]==1
        assert t["nearest_original_native_source_to_predicted_Gaia_arcsec"]==first
        assert t["second_nearest_original_native_source_arcsec"]==second
        assert t["selected_nearest_original_native_PSF_quality_pass"] is True
        assert t["unique_within_fixed_0p6arcsec_second_beyond_1arcsec"] is True
        assert t["confirmed_physical_gaia_ztf_target"] is False
        assert f["gaia_astrometric_quality_warning"] is False
        a=f["descriptive_PS1_reference_adjusted_target"]
        assert a["status"]==(
            "DESCRIPTIVE_PS1_REFERENCE_RELATIVE_TARGET_OFFSET_NOT_PHYSICAL_IDENTITY")
        assert a["external_reference_adjusted_target_east_arcsec"]==east
        assert a["external_reference_adjusted_target_north_arcsec"]==north
        assert a["independent_instrument_wcs_solution"] is False
        assert a["source_physical_gaia_ztf_identity_confirmed"] is False


def test_real_PanSTARRS_reference_astrometry_holdout_and_neighbour_counts():
    d=_load()
    near=d["original_MAST_PS1_target_source_ambiguity"]
    assert near["n_all_original_ps1_mean_source_positions_reviewed"]==1780
    assert near["independent_catalogue_source_ambiguity_excluded"] is False
    positions=near["original_target_neighborhood"]
    assert positions["gaia_J2016_reference_epoch"][
        "nearest_original_ps1_mean_position_offset_arcsec"]==.05612
    assert positions["r_original_ztf_epoch_gaia_propagated"][
        "nearest_original_ps1_mean_position_offset_arcsec"]==.119173
    assert positions["g_original_ztf_epoch_gaia_propagated"][
        "nearest_original_ps1_mean_position_offset_arcsec"]==.142935
    for v in positions.values():
        assert v["n_original_ps1_sources_within_1arcsec"]==1
        assert v["n_original_ps1_sources_within_3arcsec"]==1
        assert v["ps1_astrometric_epoch_and_source_pm_unknown"] is True
        assert v["gaia_to_ztf_ps1_physical_target_source_id_confirmed"] is False
    assert d["n_bands_reference_astrometry_holdout_internal_passes"]==2
    band={x["band"]:x for x in d["original_same_band_reference_astrometry"]}
    assert set(band)=={"g","r"}
    for name,count,train,hold,east,north in (
        ("g",82,42,40,.036237,.029475),
        ("r",180,94,86,.015511,.026370),
    ):
        ref=band[name]["source_reference_alignment"]
        assert ref["n_original_unique_external_ps1_ztf_ztf_triplets"]==count
        assert ref["n_training_reference_stars"]==train
        assert ref["n_heldout_reference_stars"]==hold
        assert ref["both_fields_heldout_internal_geometry_pass"] is True
        assert ref["status"]==(
            "INTERNAL_PS1_REFERENCE_GEOMETRY_HELDOUT_PASS_NOT_WCS_CERTIFICATION")
        for f in ref["fields"].values():
            assert f["heldout_reference_geometry_internal_qc_pass"] is True
            assert f["scientifically_complete_wcs_calibration"] is False
            assert f["heldout_east_robust_scatter_arcsec"]<=.15
            assert f["heldout_north_robust_scatter_arcsec"]<=.15
        s=band[name]["target_same_band_field_pair_summary"]
        assert s["original_field609_minus1605_relative_east_arcsec"]==east
        assert s["original_field609_minus1605_relative_north_arcsec"]==north
        assert s["physical_gaia_ztf_FT_TAU_target_match_confirmed"] is False
        assert s["independent_epoch_corrected_wcs_and_PS1_source_pm_measured"] is False


def test_published_source_evidence_is_no_raw_no_oids_combined_and_no_discovery():
    d=_load()
    receipt=json.loads(RECEIPT.read_text("utf8"))
    assert d["n_confirmed_physical_gaia_to_ztf_ft_tau_source_identities"]==0
    assert d["n_zTF_ft_tau_OID_lightcurves_merged"]==0
    assert d["n_new_confirmed_variable_or_companion_stars"]==0
    assert d["scientific_R2_full_physical_source_identity_completed"] is False
    assert receipt["n_authenticated_physical_Gaia_ZTF_FT_TAU_counterparts"]==0
    assert receipt["n_merged_FT_TAU_ZTF_oid_lightcurves"]==0
    assert receipt["R2_original_source_physical_identity_science_completed"] is False
    s=DATA.read_text("utf8")
    for forbidden in ('"ps1_ids":','"original_gaia_raw_rows":',
                      '"native_source_ids":','"original_mag":','"source_flux":',
                      '"full_fits_pixels":','"original_csv_response":'):
        assert forbidden not in s
    doc=REPORT.read_text("utf8")
    for token in ("0.056791","0.069015","0.035434","0.063244",
                  "0.056120","1,780","82","180",
                  "SHA-256","UNCONFIRMED","NOT"):
        assert token in doc
