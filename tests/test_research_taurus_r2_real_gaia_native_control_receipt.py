"""Pin genuinely observed 2026-11-11 Gaia vs original ZTF control comparison.

No need to requery original survey in offline CI. The JSON source
fingerprints link to the actual completed Gaia/IRSA GitHub workflow.
"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/"research/taurus_variability/R2_REAL_GAIA_ONLY_CONTROL_OFFSET_NO_GO.md"
LEDGER=ROOT/"reports/taurus_variability_r2/GAIA_ONLY_CONTROLS_ORIGINAL_PSF_OFFSETS_NO_RAW.json"
RECEIPT=ROOT/"reports/taurus_variability_r2/GAIA_ONLY_CONTROLS_NATIVE_PSF_OFFSETS_REAL_RECEIPT.json"


def test_real_original_data_source_sha_verifiable_and_science_counts_locked():
    raw=LEDGER.read_bytes()
    d=json.loads(raw)
    r=json.loads(RECEIPT.read_text(encoding="utf8"))
    assert hashlib.sha256(raw).hexdigest()==r["original_derived_json_sha256"]
    assert r["actual_original_data_run_id"]==43063054380
    assert r["original_derived_artifact_id"]==13874706194
    assert r["original_zip_sha256"]==(
        "0c6e872f101c3a737fb2200fa2264ca4f75701fe9cc8d12d00320dbc5d77963a")
    assert r["original_gaia_7_source_response_sha256"]==(
        d["original_gaia_7_source_response_sha256"])
    assert r["original_r1_frozen_seed_sha256"]==d["frozen_r1_seed_sha256"]
    assert d["n_original_technical_gaia_targets_in_study"]==24
    assert d["n_old_historic_science_exposures"]==4
    assert d["n_unique_predeclared_gaia_only_control_ids"]==5
    assert d["n_strict_cida_gaia_only_controls"]==4
    assert d["n_relaxed_exploratory_ft_controls"]==1
    assert d["n_original_native_catalogue_exposures_evaluated"]==4
    assert d["n_exposures_with_at_least_three_accepted_strict_controls"]==1
    assert d["n_provisional_differential_target_offsets_with_all_gates"]==0
    assert d["n_new_original_ztf_science_image_pixels_downloaded"]==0
    assert d["n_independently_authenticated_physical_gaia_ztf_matches"]==0
    assert d["n_confirmed_new_astrophysical_variable_stars"]==0
    assert d["n_confirmed_companions"]==0
    assert d["original_ztf_pipeline_training_star_membership_verified"] is False
    assert d["instrument_wcs_calibration_independent"] is False
    assert d["scientific_R2_complete"] is False


def test_original_real_same_date_field_control_quality_gates_and_no_go():
    d=json.loads(LEDGER.read_text(encoding="utf8"))
    by_mjd={x["original_science_mjd"]:x for x in d["frames"]}
    assert len(by_mjd)==4
    assert set(by_mjd)=={58388.389016,58491.18478,58475.11375,58849.135984}
    n=[by_mjd[x]["control_offset_summary"][
        "n_strict_gaia_controls_with_acceptable_native_psf_and_gaia_quality"]
       for x in (58388.389016,58491.18478,58475.11375,58849.135984)]
    assert n==[0,0,4,2]
    exp=[by_mjd[x]["control_offset_summary"][
        "n_exploratory_ft_controls_with_acceptable_native_psf"]
         for x in (58388.389016,58491.18478,58475.11375,58849.135984)]
    assert exp==[1,1,0,0]
    target_ok=[by_mjd[x]["control_offset_summary"][
        "target_original_native_psf_and_gaia_quality_gate_passed"]
        for x in (58388.389016,58491.18478,58475.11375,58849.135984)]
    assert target_ok==[True,True,False,False]
    assert all(x["status"]=="PROVISIONAL_ORIGINAL_GAIA_NATIVE_CONTROL_COMPARISON_COMPLETED"
               for x in by_mjd.values())
    assert all(x["control_offset_summary"]["provisional_target_relative_offset"] is None
               for x in by_mjd.values())
    assert all(not x["control_offset_summary"]["proved_disjoint_from_original_ZTF_DAOPhot_training_stars"]
               for x in by_mjd.values())
    assert all(not x["full_physical_gaia_ztf_source_identity_verified"]
               for x in by_mjd.values())


def test_all_5_pre_registered_reference_gaia_sources_present_per_date():
    d=json.loads(LEDGER.read_text(encoding="utf8"))
    ft={"149623298952568064"}
    cida={"3419109222512317056","3419109840987851136",
          "3419157944621312896","3419111451598996992"}
    for frame in d["frames"]:
        controls=[x for x in frame["per_source_gaia_native_screen"]
                  if x["role"]=="CONTROL"]
        targets=[x for x in frame["per_source_gaia_native_screen"]
                 if x["role"]=="TARGET"]
        assert len(targets)==1
        assert {x["gaia_dr3_source_id"] for x in controls}==(
            ft if frame["original_target"]=="FT Tau" else cida)
        assert all(x["native_source_identity_is_only_provisional"] for x in controls)
    first=next(x for x in d["frames"] if x["original_science_mjd"]==58475.11375)
    assert first["per_source_gaia_native_screen"][0]["gaia_ruwe"]>8
    assert first["per_source_gaia_native_screen"][0]["screen_status"]==(
        "NATIVE_PSF_FIT_PROFILE_OR_FLAG_REVIEW_REQUIRED")


def test_no_instrument_calibration_or_physical_discovery_claimed_by_report():
    source=LEDGER.read_text(encoding="utf8")
    report=REPORT.read_text(encoding="utf8")
    receipt=RECEIPT.read_text(encoding="utf8")
    for v in ("4","2","FT Tau","CIDA 11","NO-GO","RUWE"):
        assert v in report
    assert "not a field-calibrated" in report.lower() or "not an instrument" in report.lower()
    for text in ('"n_independently_confirmed_gaia_ztf_physical_identifications": 0',
                 '"n_provisionally_valid_differential_target_offsets": 0',
                 '"scientific_r2_completed": false'):
        assert text in receipt
    for forbidden in ('"raw_fits_bytes":','"raw_gaia_table":','"raw_ztf_catalogue":'):
        assert forbidden not in source
