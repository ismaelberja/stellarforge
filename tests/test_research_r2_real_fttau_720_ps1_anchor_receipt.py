"""Pin authentic original 720" FT Tau ZTF-PS1 header and instrumental QC evidence.

The original-data workflow, not this test, queried original ZTF data.
These offline assertions fail when real observed provenance, numeric counts
or strict NO PHYSICAL GAIA/ZTF IDENTIFICATION policy is overwritten.
"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/"reports/taurus_variability_r2/FTTAU_720_REAL_NATIVE_ENSEMBLE_ZTF_PS1_PIPELINE_HEADER_NO_RAW.json"
RECEIPT=ROOT/"reports/taurus_variability_r2/FTTAU_720_REAL_REFERENCE_ENSEMBLE_PS1_HEADER_RUN_RECEIPT.json"
OLD=ROOT/"reports/taurus_variability_r2/FTTAU_REAL_ORIGINAL_NATIVE_TWO_FIELD_INSTRUMENTAL_ENSEMBLE_NO_RAW.json"
PRIOR=ROOT/"reports/taurus_variability_r2/FT_TAU_TWO_ORIGINAL_ZTF_FIELDS_GR_FITS_MASK_PSF_DERIVED_NO_RAW.json"
REPORT=ROOT/"research/taurus_variability/R2_REAL_FTTAU_720_ORIGINAL_INSTRUMENTAL_ENSEMBLE_PS1_HEADER_RESULTS.md"


def data():
    return json.loads(EVIDENCE.read_text("utf8"))


def test_authentic_original_zip_json_four_science_hashes_and_immutable_negative_study():
    d=data()
    p=json.loads(RECEIPT.read_text("utf8"))
    assert hashlib.sha256(EVIDENCE.read_bytes()).hexdigest()==p["original_derived_json_sha256"]
    assert p["original_data_workflow_run_id"]==43091456449
    assert p["original_derived_artifact_id"]==13888443072
    assert p["original_artifact_zip_sha256"]==(
        "123a4d5cc906e56a430874e1dace957d94337da76581cd3da14afd4c221c154d")
    assert hashlib.sha256(OLD.read_bytes()).hexdigest()==(
        d["immutable_360arcsec_underpowered_previous_evidence_sha256"])
    assert hashlib.sha256(PRIOR.read_bytes()).hexdigest()==(
        d["four_original_FITS_source_evidence_sha256"])
    assert d["original_R1_seed_sha256"]==p["original_24_seed_sha256"]
    assert d["predefined_study_technical_taurus_cohort_size"]==24
    assert d["prior_fixed_360arcsec_results_untouched"] is True
    assert d["prior_failed_sky_radius_arcsec"]==360
    assert d["new_sky_radius_arcsec"]==720


def test_original_native_catalogue_shas_and_new_720_reference_counts_were_genuine():
    d=data()
    prior=json.loads(PRIOR.read_text("utf8"))
    sha={f["selection"]["ztf_oid"]:f["native_full_catalogue_sha256"]
         for f in prior["original_fits_mask_native_psf_exposure_results"]}
    assert d["ft_tau_original_ztf_oid_exposure_count"]==4
    assert d["new_original_telescope_observation_epochs_selected"]==0
    assert d["n_original_full_native_ZTF_psfcat_SHA_matched"]==4
    assert d["n_original_science_FITS_header_PS1_pipeline_metadata_parsed"]==4
    assert d["n_bands_internally_consistent_magnitude_offset"]==2
    assert d["n_bands_internal_qc_and_descriptive_spatial_screen_pass"]==2
    byband={x["band"]:x for x in d["bands"]}
    assert set(byband)=={"g","r"}
    for band in byband.values():
        assert len(band["original_FT_TAU_two_fixed_fields"])==2
        for item in band["original_FT_TAU_two_fixed_fields"]:
            assert item["full_native_psfcat_original_hash_verified"] is True
            assert sha[item["original_fixed_ztf_oid"]]==(
                item["original_native_full_psfcat_sha256"])
            assert item["original_gaia_target_in_reference_ensemble"] is False
    assert [x["n_clean_uncrowded_sources_selected_before_crossfield_matching"]
            for x in byband["g"]["original_FT_TAU_two_fixed_fields"]]==[106,116]
    assert [x["n_clean_uncrowded_sources_selected_before_crossfield_matching"]
            for x in byband["r"]["original_FT_TAU_two_fixed_fields"]]==[244,222]


def test_real_split_holdout_and_old_inner_vs_new_outer_science_qc():
    b={x["band"]:x for x in data()["bands"]}
    want={
        "g":(84,51,33,.118,-.014,.01927,10,74,.0055),
        "r":(186,96,90,-.004,.006,.01927,19,167,-.001),
    }
    for band,x in b.items():
        n,train,hold,offset,hmed,hscat,inner,outer,smed=want[band]
        e=x["native_reference_ensemble_internal_only"]
        s=x["inner_vs_outer_spatial_trend"]
        assert e["n_reciprocal_crowding_screened_geometric_pairs"]==n
        assert e["n_training_references"]==train
        assert e["n_validation_references"]==hold
        assert e["ensemble_median_native_mag_difference_b_minus_a"]==offset
        assert e["heldout_median_relative_offset_mag"]==hmed
        assert e["heldout_robust_scatter_mag"]==hscat
        assert e["status"]=="INTERNAL_ENSEMBLE_CONSISTENCY_PASS_NOT_EXTERNAL_CALIBRATION"
        assert e["instrumental_offset_internally_consistent"] is True
        assert e["independent_absolute_photometric_calibration"] is False
        assert e["validated_gaia_ztf_physical_source_identity"] is False
        assert e["all_photometric_series_remain_unmerged"] is True
        assert s["status"]=="SPATIAL_PROFILE_DESCRIPTIVELY_WITHIN_0P10_MAG"
        assert s["n_old_inner_360arcsec_reference_pairs"]==inner
        assert s["n_new_outer_360_to_720arcsec_reference_pairs"]==outer
        assert s["spatial_median_delta_inst_mags_inner_minus_outer"]==smed
        assert s["field_wide_spatially_uniform_photometry_established"] is False
        assert x["internally_consistent_and_no_detected_large_spatial_gradient"] is True
        assert x["original_ztf_lightcurves_merged"] is False


def test_real_original_FITS_PS1_header_keywords_are_pipeline_not_independent_ps1_crossmatches():
    d=data()
    band={x["band"]:x for x in d["bands"]}
    observed={
        ("g","1605"):(26.215597,.038748,1223,-.036286),
        ("g","609"):(26.127789,.037959,1092,-.060615),
        ("r","1605"):(26.099472,.022096,1300,.063890),
        ("r","609"):(26.098511,.022618,1176,.068839),
    }
    for filt,b in band.items():
        for f in b["original_FT_TAU_two_fixed_fields"]:
            header=f["original_science_header"]
            key=(filt,f["original_field"])
            z,r,n,c=observed[key]
            assert header["status"]=="PS1_ANCHORED_ZTF_PIPELINE_HEADER_PARSED"
            assert header["per_exposure_zTF_pipeline_header_values"]["MAGZP"]==z
            assert header["per_exposure_zTF_pipeline_header_values"]["MAGZPRMS"]==r
            assert header["per_exposure_zTF_pipeline_header_values"]["CLRCOEFF"]==c
            assert header["original_ps1_pipeline_header_NMATCHES"]==n
            assert header["original_info_bits"]==0
            assert header["public_ZTF_partial_ps1_match_and_zp_rms_screen_pass"] is True
            assert header["external_PS1_source_rows_queried"] is False
            assert header["independent_absolute_zeropoint_calibration_performed"] is False
            assert header["full_ZTF_exposure_quality_certified"] is False
        cmp=b["ZTF_own_PS1_anchored_FITS_header_comparison"]
        assert cmp["status"]=="DESCRIPTIVE_ZTF_OWN_PS1_ANCHORED_PIPELINE_HEADER_COMPARISON"
        assert cmp["direct_external_ps1_catalogue_crossmatch_performed"] is False
        assert cmp["color_corrected_AB_flux_calibration_performed"] is False
        assert cmp["physical_gaia_ztf_source_match_verified"] is False
    assert band["g"]["ZTF_own_PS1_anchored_FITS_header_comparison"][
        "nominal_delta_inst_plus_pipeline_header_delta_zp"]==.030192
    assert band["r"]["ZTF_own_PS1_anchored_FITS_header_comparison"][
        "nominal_delta_inst_plus_pipeline_header_delta_zp"]==-.004961


def test_original_source_physical_non_discovery_and_no_raw_ztf_photometry_contract():
    d=data()
    p=json.loads(RECEIPT.read_text("utf8"))
    assert d["n_directly_crossmatched_independent_PS1_reference_sources"]==0
    assert d["n_independently_certified_absolute_photometric_zeropoints"]==0
    assert d["n_independently_confirmed_physical_Gaia_ZTF_matches"]==0
    assert d["n_ZTF_OID_lightcurves_merged"]==0
    assert d["n_intrinsic_FT_TAU_variability_or_companion_detections"]==0
    assert d["R2_physical_source_identity_completed"] is False
    assert p["n_external_PS1_AB_color_calibrations"]==0
    assert p["scientific_R2_physical_identity_completed"] is False
    assert p["original_raw_FITS_or_original_source_photometry_committed"] is False
    text=EVIDENCE.read_text("utf8")
    for forbidden in ('"mag":','"sigmag":','"flux":','"original_source_rows":',
                      '"ra":','"dec":','"fits_image_array":'):
        assert forbidden not in text
    paper=REPORT.read_text("utf8")
    for token in ("84","186","0.118","0.030192","0.004961",
                  "not", "PS1", "NOT COMPLETED", "zero"):
        assert token.lower() in paper.lower()
