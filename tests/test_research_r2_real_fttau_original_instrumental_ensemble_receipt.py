"""Pin genuine original IRSA ZTF native instrumental reference experiment NO-GO."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/"reports/taurus_variability_r2/FTTAU_REAL_ORIGINAL_NATIVE_TWO_FIELD_INSTRUMENTAL_ENSEMBLE_NO_RAW.json"
RECEIPT=ROOT/"reports/taurus_variability_r2/FTTAU_ORIGINAL_INSTRUMENTAL_ENSEMBLE_REAL_RUN_RECEIPT.json"
REPORT=ROOT/"research/taurus_variability/R2_REAL_FTTAU_ORIGINAL_CROSSFIELD_INSTRUMENTAL_ENSEMBLE_NO_GO.md"
PRIOR=ROOT/"reports/taurus_variability_r2/FT_TAU_TWO_ORIGINAL_ZTF_FIELDS_GR_FITS_MASK_PSF_DERIVED_NO_RAW.json"


def test_original_genuine_ztf_artifact_sha_run_reference_and_prior_exposure_hash_locked():
    original=LEDGER.read_bytes()
    d=json.loads(original)
    r=json.loads(RECEIPT.read_text("utf8"))
    assert hashlib.sha256(original).hexdigest()==r["original_derived_json_sha256"]
    assert r["original_data_workflow_run_id"]==43072549599
    assert r["original_derived_only_artifact_id"]==13880110016
    assert r["original_artifact_zip_sha256"]==(
        "565c439a32e5e5fda6a4fc2444fc71eb9f1f7d025e3d20db2a07f49a77801a70")
    assert hashlib.sha256(PRIOR.read_bytes()).hexdigest()==(
        d["prior_original_fits_evidence_sha256"])
    assert r["previous_original_four_fits_ledger_sha256"]==(
        d["prior_original_fits_evidence_sha256"])
    assert d["original_r1_seed_sha256"]==r["frozen_original_r1_24_source_seed_sha256"]


def test_four_real_original_psfcat_sha_rechecked_exactly_two_bands_and_no_calibration():
    d=json.loads(LEDGER.read_text("utf8"))
    r=json.loads(RECEIPT.read_text("utf8"))
    prior=json.loads(PRIOR.read_text("utf8"))
    original_hashes={x["selection"]["ztf_oid"]:x["native_full_catalogue_sha256"]
                     for x in prior["original_fits_mask_native_psf_exposure_results"]}
    assert d["original_nonrepresentative_taurus_gaia_seed_count"]==24
    assert d["n_fixed_ft_tau_ztf_oids"]==4
    assert d["n_original_ztf_historical_science_exposures"]==4
    assert d["n_new_original_science_exposures_selected"]==0
    assert d["n_native_original_psf_catalogues_exactly_sha_verified"]==4
    assert d["n_same_band_ensemble_internal_qc_passes"]==0
    assert d["n_same_band_ensembles_evaluated"]==2
    assert d["n_verified_external_photometric_standard_zeropoints"]==0
    assert d["n_physical_gaia_ztf_source_identities_confirmed"]==0
    assert d["n_original_ztf_oid_lightcurves_merged"]==0
    assert d["n_confirmed_new_intrinsic_ft_tau_variability_or_companions"]==0
    assert d["scientific_r2_complete"] is False
    assert {x["band"] for x in d["bands"]}=={"g","r"}
    for band in d["bands"]:
        assert band["original_field_1605_and_609_exposure_mjd_gap_days"]==.000451
        assert len(band["native_psfcat_original_data_records"])==2
        assert band["status"]=="NO_GO_UNDERPOWERED_OR_INCONSISTENT_NATIVE_ENSEMBLE"
        for entry in band["native_psfcat_original_data_records"]:
            assert original_hashes[entry["original_ztf_oid"]]==(
                entry["original_native_catalogue_sha256"])
    assert r["native_catalogue_mag_is_instrumental_not_ab"] is True
    assert r["original_fluxes_and_source_magnitudes_persisted"] is False


def test_genuine_reference_pair_counts_do_not_silently_generate_instrumental_magnitudes():
    d=json.loads(LEDGER.read_text("utf8"))
    groups={b["band"]:b for b in d["bands"]}
    assert [x["n_original_native_source_rows"] for x in groups["g"][
        "native_psfcat_original_data_records"]]==[5757,4956]
    assert [x["n_original_native_source_rows"] for x in groups["r"][
        "native_psfcat_original_data_records"]]==[8425,8375]
    assert [x["n_in_fixed_360arcsec_sky_radius"] for x in groups["g"][
        "native_psfcat_original_data_records"]]==[97,94]
    assert [x["n_in_fixed_360arcsec_sky_radius"] for x in groups["r"][
        "native_psfcat_original_data_records"]]==[153,177]
    assert [x["n_preselected_clean_uncrowded_native_candidates"] for x in groups["g"][
        "native_psfcat_original_data_records"]]==[12,12]
    assert [x["n_preselected_clean_uncrowded_native_candidates"] for x in groups["r"][
        "native_psfcat_original_data_records"]]==[28,27]
    assert groups["g"]["native_source_crossfield_ensemble"][
        "n_reciprocal_crowding_screened_geometric_pairs"]==10
    assert groups["r"]["native_source_crossfield_ensemble"][
        "n_reciprocal_crowding_screened_geometric_pairs"]==19
    for b in groups.values():
        x=b["native_source_crossfield_ensemble"]
        assert x["instrumental_offset_internally_consistent"] is False
        assert x["ensemble_median_native_mag_difference_b_minus_a"] is None
        assert x["heldout_median_relative_offset_mag"] is None
        assert x["heldout_robust_scatter_mag"] is None
        assert x["n_validation_references"]==0
        assert x["all_photometric_series_remain_unmerged"] is True
        assert x["target_itself_excluded_from_reference_ensemble"] is True
        assert x["independent_absolute_photometric_calibration"] is False
        assert x["validated_gaia_ztf_physical_source_identity"] is False


def test_public_real_gaia_native_data_have_no_original_photometric_rows_or_fits():
    s=LEDGER.read_text("utf8")
    r=RECEIPT.read_text("utf8")
    report=REPORT.read_text("utf8")
    for forbidden in ('"ra":','"dec":','"flux":','"mag":','"sigmag":',
                      '"sourceid":','"image_data":','"raw_fits":','"mjd":'):
        assert forbidden not in s
    for key in ("10","19","NO-GO","20","not", "instrumental"):
        assert key.lower() in report.lower()
    assert '"n_ztf_oid_curves_merged": 0' in r
    assert '"n_independently_verified_gaia_ztf_fttau_physical_counterparts": 0' in r
    assert '"scientific_r2_complete": false' in r
