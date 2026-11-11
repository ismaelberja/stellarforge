"""Lock genuine R2 IRSA run evidence without claiming physical source identities."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/"reports/taurus_variability_r2/IRSA_22_ORIGINAL_DERIVED_DIAGNOSTIC_LEDGER.json"
RECEIPT=ROOT/"reports/taurus_variability_r2/IRSA_22_ORIGINAL_FAILURE_DIAGNOSTIC_RECEIPT_NO_RAW.json"
PLAN=ROOT/"research/taurus_variability/R2_IRSA_DIAGNOSTIC_INPUT_NO_RAW.json"


def test_authentic_irsa_derivation_has_sha256_and_frozen_24_targets():
    source=REPORT.read_bytes()
    entry=json.loads(source)
    receipt=json.loads(RECEIPT.read_text(encoding="utf8"))
    plan=json.loads(PLAN.read_text(encoding="utf8"))
    assert hashlib.sha256(source).hexdigest()==(
        receipt["full_24_row_original_derived_json_sha256"])
    assert receipt["original_live_actions_run"]==43037800319
    assert receipt["github_artifact_id"]==13864870251
    assert receipt["n_frozen_technical_gaia_sources"]==24
    assert entry["n_technical_targets_frozen"]==24
    assert len(entry["rows"])==24
    assert entry["original_r1_seed_sha256"]==plan["r1_seed_sha256"]
    assert len({r["gaia_dr3_source_id"] for r in entry["rows"]})==24
    assert {r["gaia_dr3_source_id"] for r in entry["rows"]}==(
        set(plan["unresolved_gaia_ids"]) |
        set(plan["previously_parsed_gaia_ids"]))


def test_real_diagnostic_outcomes_are_not_fake_stellar_variability():
    x=json.loads(REPORT.read_text(encoding="utf8"))
    receipt=json.loads(RECEIPT.read_text(encoding="utf8"))
    assert x["n_prior_ztf_parsed_targets_not_requeried"]==2
    assert x["n_prior_ztf_unresolved_targets"]==22
    assert x["n_unresolved_targets_with_any_parsed_response_rows"]==13
    assert x["n_previously_unresolved_still_without_parsed_rows"]==9
    assert x["n_diagnostic_http_requests"]==31
    assert x["status_counts_per_attempt"]=={
        "HTTP_CLIENT_ERROR":9,"NETWORK_TIMEOUT":8,
        "PARSED_TABLE_WITH_ROWS":13,"PARSED_TABLE_ZERO_ROWS":1}
    assert receipt["n_total_ztf_sky_fields_with_parsed_data_across_separate_runs"]==15
    assert receipt["n_new_original_ztf_positional_table_rows_across_13_queries"]==14803
    assert x["all_gaia_ztf_physical_identities_confirmed"] is False
    assert x["n_confirmed_new_variable_stars"]==0
    assert x["scientific_R2_complete"] is False
    assert all(r["physical_gaia_ztf_counterpart_verified"] is False
               for r in x["rows"])


def test_original_irsa_parameter_did_the_recovery_alternate_failed():
    x=json.loads(REPORT.read_text(encoding="utf8"))
    successes=[]
    timeouts=[]
    zero_rows=[]
    for r in x["rows"]:
        attempts=r["diagnostic_attempts"]
        if r["prior_r2_ztf_status"]=="PREVIOUSLY_PARSED_MULTIPLE_OIDS_NOT_IDENTITY_VERIFIED":
            assert attempts==[]
            continue
        if r["recovered_original_positional_rows"]:
            assert len(attempts)==1
            assert attempts[0]["variant"]=="NOBS_MIN_5"
            assert attempts[0]["outcome"]=="PARSED_TABLE_WITH_ROWS"
            assert attempts[0]["http_status"]==200
            successes.append(r)
        else:
            assert len(attempts)==2
            assert attempts[1]["variant"]=="NUM_OBS_1"
            assert attempts[1]["outcome"]=="HTTP_CLIENT_ERROR"
            assert attempts[1]["http_status"]==400
            if attempts[0]["outcome"]=="NETWORK_TIMEOUT":
                timeouts.append(r)
            else:
                assert attempts[0]["outcome"]=="PARSED_TABLE_ZERO_ROWS"
                zero_rows.append(r)
    assert (len(successes),len(timeouts),len(zero_rows))==(13,8,1)
    assert sum(r["diagnostic_attempts"][0]["returned_rows"]
               for r in successes)==14803


def test_no_original_ztf_csv_data_leaked_and_statuses_visible_in_report():
    j=REPORT.read_text(encoding="utf8")
    d=RECEIPT.read_text(encoding="utf8")
    method=(ROOT/"research/taurus_variability/R2_REAL_IRSA_22_FAILURE_DIAGNOSIS_RESULTS.md").read_text(encoding="utf8")
    for s in ("43037800319","13","22","9","14,803","NOBS_MIN=5","NUM_OBS=1","HTTP 400"):
        assert s in method
    assert "R2" in method and "NOT" in method and "nonvariability" in method
    assert '"mjd":' not in j
    assert '"mag":' not in j
    assert '"flux":' not in j
    assert '"raw_csv":' not in j
    assert '"mjd":' not in d
    assert '"new_variable_stars_confirmed": 0' in d
