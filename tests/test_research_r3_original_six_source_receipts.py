"""Offline original-data source receipt tests — NOT synthetic astrophysical claims.

Genuine raw IRSA response payloads are NOT present in this repo. These tests
validate preserved original response hashes, fixed 6 OIDs, QoS failure
honesty, instrumental mask thresholds and R2 no-physical-identity gate.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.audit_taurus_r3_six_original_source_receipts import (
    FIRST_PATH, RETRY_PATH, R2_PATH, R2_OID_PATH,
    audit_r3_original_six_source_receipts,
)

ROOT=Path(__file__).resolve().parents[1]
INPUTS=(FIRST_PATH, RETRY_PATH, R2_PATH, R2_OID_PATH)


def test_real_original_r3_provider_responses_reconcile_and_no_gaia_variability_claim():
    j=audit_r3_original_six_source_receipts(ROOT)
    assert j["status"].startswith("R3_ORIGINAL_SIX_OID_TECHNICAL_PHOTOMETRY_AUDIT_PARTIAL")
    assert j["original_frozen_ztf_objectids_studied"]==6
    assert j["original_dr24_exact_oid_source_csv_successful"]==3
    assert j["original_dr24_source_requests_unavailable_after_one_retry"]==3
    assert j["original_raw_ztf_source_rows_quality_inspected"]==684
    assert j["original_locally_qc_accepted_rows"]==591
    assert j["original_masked_catflags_bit15_rows"]==93
    assert j["original_independent_oid_band_clock_30visit_90day_pass"]==3
    assert j["original_physical_gaia_ztf_sources_authenticated"]==0
    assert j["r3_physical_stellar_variability_science_eligible"] is False
    assert j["genuine_new_astrophysical_variability_or_companion_detected"] is False


def test_original_provider_source_first_and_second_are_separate_immutable_evidence():
    first=json.loads((ROOT/FIRST_PATH).read_text("utf8"))
    second=json.loads((ROOT/RETRY_PATH).read_text("utf8"))
    assert first["original_workflow_run_id"]==43593335135
    assert second["original_recovery_workflow_run_id"]==43593994009
    assert first["original_derived_only_source_json_sha256"]=="3d9e864d2028c5040f4c7bd2860d8991fd51e7e22a4f8185029982467d4852ec"
    assert second["original_recovery_derived_only_json_sha256"]=="3de1c4028cf138d450a06ad48062952bd0b439aad4b4602f0815629df8998ebb"
    assert sum(x["original_provider_raw_rows"] for x in first["per_oid_results"] if x.get("original_response_sha256"))==684
    assert sum(x["original_local_qc_accepted_rows"] for x in first["per_oid_results"] if x.get("original_response_sha256"))==591
    assert all(r["original_first_outcome"]==r["original_second_outcome"]=="TimeoutError" for r in second["original_timeout_rows"])
    assert second["n_recovered_original_public_dr24_source_csv"]==0
    assert second["all_second_retries_original_ztf_provider_timeout_not_scientific_non_detection"] is True


@pytest.mark.parametrize("where,section,key,value",[
    ("first",None,"technical_oid_30visit_90day_pass_count",6),
    ("first",None,"original_success_qc_retained_rows",0),
    ("first",0,"original_response_sha256","0"*64),
    ("first",0,"original_local_catflags_32768_masked_rows",1),
    ("first",0,"original_qc_time_span_days",90.0),
    ("first",0,"original_archive_query_url","https://example.com"),
    ("first",3,"original_query_status","ORIGINAL_ZTF_EXACT_OID_CSV_PARSED_AND_QC_AUDITED"),
    ("first",3,"provisional_technical_30visit_90day_pass",True),
    ("retry",None,"n_recovered_original_public_dr24_source_csv",3),
    ("retry",0,"original_second_outcome","HTTP 200"),
    ("retry",0,"second_original_response_sha256","9"*64),
    ("retry",1,"oid","unknown"),
    ("r2",None,"r2_physical_source_identity_success",True),
])
def test_false_r3_technical_success_or_physical_gaia_identity_is_rejected(tmp_path,where,section,key,value):
    for path in INPUTS:
        target=tmp_path/path
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((ROOT/path).read_bytes())
    path=tmp_path/({"first":FIRST_PATH,"retry":RETRY_PATH,"r2":R2_PATH}[where])
    d=json.loads(path.read_text("utf8"))
    if section is None:
        d[key]=value
    else:
        d["per_oid_results" if where=="first" else "original_timeout_rows"][section][key]=value
    path.write_text(json.dumps(d),encoding="utf8")
    with pytest.raises(ValueError):
        audit_r3_original_six_source_receipts(tmp_path)


def test_original_cadence_bins_are_derived_only_not_new_stellar_periodicity():
    initial=json.loads((ROOT/FIRST_PATH).read_text("utf8"))
    successful=[x for x in initial["per_oid_results"] if x["provisional_technical_30visit_90day_pass"]]
    assert len(successful)==3
    for r in successful:
        assert r["original_time_system"]=="MJD"
        assert r["original_qc_time_span_days"]>=90
        assert sum(r["original_qc_365day_bin_counts"])==r["original_local_qc_accepted_rows"]
        assert r["original_local_qc_accepted_rows"]>=30
        assert r["physical_gaia_to_this_ztf_oid_counterpart_authenticated"] is False
    assert [x["original_frozen_ztf_oid"] for x in successful]==[
        "1605115300003377","1605215300005161","609108400001155"
    ]


def test_public_r3_science_report_does_not_declare_gaia_stellar_variability():
    text=(ROOT/"research/taurus_variability/R3_REAL_SIX_ORIGINAL_ZTF_DR24_QC_RESULTS.md").read_text("utf8")
    for word in ("684","591","93","Timeout","FT Tau","CIDA 11","DR24","NO","R2"):
        assert word.lower() in text.lower()
    assert "physical Gaia" in text or "Gaia–ZTF" in text
    assert "R3" in text and "30" in text and "90" in text
    assert (ROOT/"research/taurus_variability/R3_SIX_FIXED_ZTF_OIDS_PHOTOMETRY_QC_PREREGISTRATION.md").is_file()
    assert (ROOT/"research/taurus_variability/R3_THREE_ORIGINAL_ZTF_TIMEOUTS_RETRY_PREREGISTRATION.md").is_file()
