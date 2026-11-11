"""Pin actual original four FT Tau g/r two-field ZTF FITS QA as *non-discovery*."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/"reports/taurus_variability_r2/FT_TAU_TWO_ORIGINAL_ZTF_FIELDS_GR_FITS_MASK_PSF_DERIVED_NO_RAW.json"
RECEIPT=ROOT/"reports/taurus_variability_r2/FT_TAU_TWO_ORIGINAL_FIELDS_GR_FITS_REAL_RUN_RECEIPT.json"
REPORT=ROOT/"research/taurus_variability/R2_REAL_FT_TAU_TWO_FIELD_GR_FITS_MASK_PSF_RESULTS.md"


def test_archival_source_artifact_original_sha_and_gaia_input_are_unmodified():
    original=LEDGER.read_bytes()
    p=json.loads(RECEIPT.read_text("utf8"))
    r=json.loads(original)
    assert hashlib.sha256(original).hexdigest()==p["original_derived_json_sha256"]
    assert p["original_live_workflow_run_id"]==43069170818
    assert p["source_artifact_id"]==13875884723
    assert p["source_artifact_zip_sha256"]==(
        "494b754ea9bf77e7467144c4291f8a7842075c6bdcf238d45ceb4a7e306390e6")
    assert p["original_gaia_tap_response_sha256"]==r["original_gaia_source_response_sha256"]
    assert p["frozen_r1_seed_sha256"]==r["original_24_source_seed_sha256"]
    assert r["fixed_original_r1_nonrepresentative_gaia_target_count"]==24
    assert r["selected_gaia_dr3_exact_source_id"]=="149623711269425408"


def test_all_four_genuine_original_source_images_and_masks_pass_predeclared_qc():
    d=json.loads(LEDGER.read_text("utf8"))
    assert d["fixed_original_ztf_distinct_oids"]==4
    assert d["n_original_direct_oid_metadata_requests"]==4
    assert d["n_original_direct_oid_csv_tables_valid"]==4
    assert d["n_mjd_closest_same_band_crossfield_pairs_selected"]==2
    assert d["n_selected_original_single_science_exposures"]==4
    assert d["n_selected_original_images_with_all_instrument_checks_passed"]==4
    assert d["n_original_image_mask_pairs_checked"]==4
    assert d["n_original_native_psfcats_parsed"]==4
    assert d["n_pairs_with_instrumental_gates_both_passed"]==2
    assert d["n_independently_verified_ft_gaia_ztf_physical_crossmatches"]==0
    assert d["n_reconciled_or_combined_ztf_lightcurves"]==0
    assert d["n_confirmed_new_astro_variables_or_companions"]==0
    assert d["r2_physical_source_identity_science_complete"] is False
    assert len(d["original_fits_mask_native_psf_exposure_results"])==4
    assert sum(x["n_original_rows"] for x in d["source_oid_metadata"])==1442
    assert sum(x["n_eligible_distinct_original_science_exposures"]
               for x in d["source_oid_metadata"])==1199


def test_g_and_r_two_field_pairs_have_original_39_second_separations_but_are_not_crossband_simultaneous():
    d=json.loads(LEDGER.read_text("utf8"))
    p=json.loads(RECEIPT.read_text("utf8"))
    pairs={a["band"]:a for a in d["crossfield_same_filter_pairs"]}
    assert set(pairs)=={"g","r"}
    assert p["cross_filter_g_and_r_contemporaneous"] is False
    expected={
        "g":[(1605,15,3,58806.385197,"1605115300003377"),
             (609,8,4,58806.385648,"609108400001155")],
        "r":[(1605,15,3,58425.306065,"1605215300005161"),
             (609,8,4,58425.306516,"609208400001969")],
    }
    for band,pair in pairs.items():
        assert pair["selection_status"]=="SELECTED_WITHIN_ONE_DAY_DIFFERENT_FIELD"
        assert pair["selected_within_1day"] is True
        assert pair["selection_mjd_gap_days"]==0.000451
        assert pair["quality_or_brightness_was_not_used_to_select_survey_images"] is True
        selected=pair["selected_original_exposures"]
        assert len(selected)==2
        assert [
            (*x["original_field_ccd_quadrant"],x["original_mjd"],x["ztf_oid"])
            for x in selected]==expected[band]
        comparison=pair["crossfield_instrument_summary"]
        assert comparison["both_original_science_mask_native_products_available"] is True
        assert comparison["instrumental_gates_both_passed"] is True
        assert comparison["crossfield_oid_physical_identity_authenticated"] is False
        assert comparison["crossfield_lightcurves_merged"] is False
        assert comparison["differential_astrometry_independently_calibrated"] is False
    assert pairs["g"]["crossfield_instrument_summary"][
        "native_catalogue_field_to_field_offset_difference_mas"]["angular_proxy_mas"]==13.568
    assert pairs["r"]["crossfield_instrument_summary"][
        "native_catalogue_field_to_field_offset_difference_mas"]["angular_proxy_mas"]==79.473


def test_all_original_instrumental_mask_neighbour_and_peak_checks_are_unambiguously_provisional():
    rows=json.loads(LEDGER.read_text("utf8"))[
        "original_fits_mask_native_psf_exposure_results"]
    assert len(rows)==4
    assert [x["native_nearest_gaia_offset_arcsec"] for x in rows]==[
        .056791,.069015,.035434,.063244]
    assert [x["science_central_peak_offset_arcsec"] for x in rows]==[
        .25131,.38518,.41884,.37733]
    for x in rows:
        assert x["all_three_instrument_source_checks_pass"] is True
        assert x["native_psf_status"]==(
            "PROVISIONAL_CATALOGUE_NEAREST_AND_PROFILE_SCREEN_PASSED")
        assert x["science_mask_status"]==(
            "MASK_CORE_NO_DISQUALIFYING_BITS_PROVISIONAL_ONLY")
        assert x["science_pixel_status"]=="PIXEL_WCS_PROVISIONAL_SCREEN_COMPLETED"
        assert x["mask_image_wcs_aligned"] is True
        assert x["mask_core_bad_pixels"]==0
        assert x["mask_core_saturated_pixels"]==0
        assert x["native_secondary_sources_within_3arcsec"]==0
        assert x["science_additional_bright_peaks_within_12arcsec"]==0
        assert x["native_source_quality_passed"] is True
        assert x["science_central_peak_found"] is True
        assert x["gaia_quality_warning"] is False
        assert 1.3 < x["gaia_ruwe"] < 1.4
        assert len(x["science_sha256"])==64
        assert len(x["mask_sha256"])==64
        assert len(x["native_full_catalogue_sha256"])==64
        assert x["original_ztf_source_identity_verified"] is False
        assert x["external_astrometry_calibration_complete"] is False
        assert x["source_blend_excluded"] is False
        assert x["new_source_variability_confirmed"] is False
        assert x["original_image_is_not_a_new_survey_epoch"] is True


def test_no_ztf_raw_fits_magnitudes_or_source_timeseries_leak_to_public_original_evidence():
    s=LEDGER.read_text("utf8")
    r=RECEIPT.read_text("utf8")
    report=REPORT.read_text("utf8")
    for invalid in ('"raw_fits":','"original_photometry_rows":','"mag":',
                    '"magerr":','"flux":','"science_pixel_values":'):
        assert invalid not in s
    for excerpt in ("0.000451","13.568","79.473","g","r",
                    "not independently", "not", "24-object"):
        assert excerpt.lower() in report.lower()
    assert '"n_physical_gaia_ztf_matches_independently_authenticated": 0' in r
    assert '"n_ztf_oid_lightcurves_merged": 0' in r
    assert '"r2_science_source_identity_completed": false' in r
