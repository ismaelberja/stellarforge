"""Lock the actual six ZTF original-source chi-blind evidence and non-claims."""
import json
from pathlib import Path

EVIDENCE = (Path(__file__).resolve().parents[1] /
    "reports/taurus_variability_r2/FTTAU_SIX_ORIGINAL_ZTF_CHI_BLIND_REFERENCES_NO_RAW.json")


def test_real_original_ztf_chi_blind_six_frame_source_counts_and_fixed_gates():
    evidence=json.loads(EVIDENCE.read_text(encoding="utf8"))
    assert evidence["original_data_run_id"]==43275404347
    assert evidence["artifact_id"]==13970027074
    assert evidence["n_original_byte_sha_verified_ztf_full_psfcats"]==6
    assert evidence["n_per_image_controls_adequate_20_or_more"]==6
    assert evidence["n_per_image_snr_matched_controls_adequate_20_or_more"]==6
    assert evidence["control_selection_excludes_chi_threshold"] is True
    assert evidence["prospective_original_target_quality_gate_unchanged"] is True
    assert evidence["original_previous_5_of_8_quality_passes_unchanged"] is True
    assert evidence["original_valid_two_night_pairs_1_of_4_unchanged"] is True
    groups=evidence["original_exact_3_ztf_oid_early_late_pairs"]
    assert [(x["band"],x["field"]) for x in groups]==[
        ("g",1605),("g",609),("r",609)]
    pairs=[x for g in groups for x in g["epochs"]]
    assert len(pairs)==6
    assert [x["n"] for x in pairs]==[108,160,94,196,239,298]
    assert [x["below"] for x in pairs]==[38,38,25,23,20,96]
    assert [x["matched_n"] for x in pairs]==[98,133,63,131,196,269]
    assert [x["matched_below"] for x in pairs]==[34,35,18,15,16,94]
    assert sum(x["n"] for x in pairs)==evidence["sum_control_source_records_across_six_images"]==1095
    assert sum(x["below"] for x in pairs)==evidence["sum_controls_chi_below_0p5"]==240
    assert all(0<=x["below"]<=x["n"] for x in pairs)
    assert all(0<=x["matched_below"]<=x["matched_n"] for x in pairs)
    assert all(len(x["sha"])==64 for x in pairs)
    assert all(len(x["day"])==14 and x["day"].isdigit() for x in pairs)
    assert all(0.5 <= g["epochs"][0]["chi"] <= 1.5 for g in groups)
    assert all(g["epochs"][1]["chi"]<0.5 for g in groups)
    assert evidence["n_physical_gaia_ztf_identities_confirmed"]==0
    assert evidence["n_new_variable_or_companion_stars"]==0
    assert evidence["n_original_ztf_oid_lightcurves_merged"]==0
    assert evidence["scientific_R2_complete"] is False


def test_six_original_control_receipt_has_a_real_archive_and_same_ztf_pipeline_scope():
    d=json.loads(EVIDENCE.read_text("utf8"))
    assert len(d["artifact_zip_sha256"])==64
    assert len(d["derived_only_original_json_sha256"])==64
    assert len(d["original_gaia_response_sha256"])==64
    assert d["original_gaia_response_sha256"]=="399b5498d8d8a8a646073dfc029895ed64902940896d1789c63833a18074b642"
    assert "same" in " ".join(d["limitations"]).lower()
    assert d["scientific_R2_complete"] is False
