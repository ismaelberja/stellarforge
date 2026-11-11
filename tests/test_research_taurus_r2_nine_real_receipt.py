"""Pin exact genuine nine-source IRSA original archive results, not false discoveries."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/"reports/taurus_variability_r2/IRSA_NINE_ORIGINAL_RESPONSE_SOURCE_LEDGER_NO_RAW.json"
RECEIPT=ROOT/"reports/taurus_variability_r2/IRSA_NINE_ORIGINAL_RESPONSE_RECEIPT_NO_RAW.json"
REPORT=ROOT/"research/taurus_variability/R2_REAL_NINE_IRSA_SOURCE_RECOVERY.md"
OLD=ROOT/"reports/taurus_variability_r2/IRSA_22_ORIGINAL_DERIVED_DIAGNOSTIC_LEDGER.json"


def test_original_data_ledger_bytes_have_real_actions_source_digest():
    receipt=json.loads(RECEIPT.read_text(encoding="utf8"))
    ledger=json.loads(LEDGER.read_text(encoding="utf8"))
    assert hashlib.sha256(LEDGER.read_bytes()).hexdigest()==(
        receipt["original_source_json_sha256"])
    assert receipt["original_run_id"]==43042786341
    assert receipt["original_github_actions_artifact_id"]==13866785881
    assert receipt["original_zip_sha256"]=="34890a91f9f86004967726e61c6f69cc7443a9d45828f07387fe51b22feb4674"
    assert ledger["frozen_r1_sha256"]==receipt["frozen_r1_seed_sha256"]
    assert ledger["preceding_original_irsa_diagnostic_run"]==43037800319
    assert len(ledger["per_source"])==9
    previous=json.loads(OLD.read_text(encoding="utf8"))
    old_unresolved={
        x["gaia_dr3_source_id"] for x in previous["rows"]
        if x["prior_r2_ztf_status"]=="UNAVAILABLE_OR_UNPARSEABLE"
        and not x["recovered_original_positional_rows"]
    }
    assert old_unresolved=={r["gaia_dr3_source_id"] for r in ledger["per_source"]}


def test_real_original_irsa_source_access_advanced_from_15_to_22_not_24():
    receipt=json.loads(RECEIPT.read_text(encoding="utf8"))
    ledger=json.loads(LEDGER.read_text(encoding="utf8"))
    assert ledger["source_gaia_dr3_ids_frozen"]==24
    assert ledger["preexisting_parsed_ztf_sky_positions"]==15
    assert ledger["n_actual_original_irsa_requests"]==9
    assert ledger["n_new_positions_with_parsed_positional_ztf_rows"]==7
    assert ledger["n_cumulative_positions_with_historically_parsed_ztf_rows"]==22
    assert ledger["n_still_without_any_parsed_original_ztf_response"]==2
    assert ledger["per_request_status_counts"]=={
        "PARSED_TABLE_WITH_ROWS":7,"PARSED_TABLE_ZERO_ROWS":1,
        "HTTP_CLIENT_ERROR":1}
    assert receipt["n_ztf_positions_with_original_parsable_tables_across_runs"]==22
    assert receipt["n_remaining_unresolved"]==2
    assert sum(r["current_original_provider_response"].get("returned_rows") or 0
               for r in ledger["per_source"])==11058


def test_two_specific_unresolved_gaia_ids_were_not_classified_as_nonvariables():
    ledger=json.loads(LEDGER.read_text(encoding="utf8"))
    unavailable={r["gaia_dr3_source_id"]:r["current_original_provider_response"]
                 for r in ledger["per_source"]
                 if not r["parsed_positional_table_with_rows"]}
    assert set(unavailable)=={
        "3314244366165299584","3406270362673330944"}
    assert unavailable["3314244366165299584"]["outcome"]=="PARSED_TABLE_ZERO_ROWS"
    assert unavailable["3406270362673330944"]["outcome"]=="HTTP_CLIENT_ERROR"
    assert unavailable["3406270362673330944"]["http_status"]==400
    assert all(not r["physical_gaia_ztf_source_identity_authenticated"]
               for r in ledger["per_source"])
    assert all(not r["observed_stellar_variability_confirmed"]
               for r in ledger["per_source"])
    assert ledger["n_ztf_physical_counterparts_independently_verified"]==0
    assert ledger["n_genuine_astrophysical_variability_results_confirmed"]==0
    assert ledger["n_original_science_image_psf_mask_vetted"]==0
    assert ledger["scientific_r2_complete"] is False
    assert ledger["public_source_derived_statuses_only"] is True


def test_readme_and_report_maintain_scientific_data_scope_without_raw():
    readme=(ROOT/"README.md").read_text(encoding="utf8")
    method=REPORT.read_text(encoding="utf8")
    for msg in ("22 of 24","zero physical Gaia–ZTF","FITS"):
        assert msg in readme
    for msg in ("22/24","11,058","zero-row","HTTP 400"):
        assert msg in method
    source=LEDGER.read_text(encoding="utf8")
    assert '"mjd":' not in source
    assert '"mag":' not in source
    assert '"raw_csv":' not in source
