"""Offline falsification tests for live IRSA failure classification and R2 cohort."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlparse

import pytest

from stellarforge.r2_irsa_failure_diagnosis import (
    MAX_BYTES, classify_original_response, diagnose_frozen_24,
    irsa_diagnostic_url, request_diagnostic, validate_frozen_input,
)

ROOT=Path(__file__).resolve().parents[1]
SEED=(ROOT/"data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv").read_bytes()
PLAN=json.loads((ROOT/"research/taurus_variability/R2_IRSA_DIAGNOSTIC_INPUT_NO_RAW.json").read_text(encoding="utf-8"))


def csv_fixture(n=1):
    return (
        "oid,mag,magerr,catflags,filtercode,mjd\n" +
        "".join(f"1234567,14.1,0.04,0,zg,{59000 + k}\n" for k in range(n))
    ).encode()


def outcome(name,variant):
    return {"variant":variant,"outcome":name,"returned_rows":(
        1 if name == "PARSED_TABLE_WITH_ROWS" else None)}


def test_original_archived_unresolved_sample_freezes_all_24_before_science():
    rows, unresolved=validate_frozen_input(SEED,PLAN)
    assert len(rows)==24
    assert len(unresolved)==22
    assert PLAN["source_json_sha256"]=="fea7630bee5971629d57b127d0776d756b8237cfbc088fd3f5e63d4571d99500"
    assert hashlib.sha256(SEED).hexdigest()==PLAN["r1_seed_sha256"]
    assert len(set(PLAN["previously_parsed_gaia_ids"])) == 2
    assert set(PLAN["unresolved_gaia_ids"]).isdisjoint(PLAN["previously_parsed_gaia_ids"])


def test_original_seed_or_prior_source_status_tamper_rejected():
    bogus=dict(PLAN,unresolved_gaia_ids=PLAN["unresolved_gaia_ids"][:-1])
    with pytest.raises(ValueError):
        validate_frozen_input(SEED,bogus)
    with pytest.raises(ValueError,match="seed"):
        validate_frozen_input(SEED+b"x",PLAN)


def test_official_urls_only_change_documented_query_variant():
    u1=irsa_diagnostic_url(65.9,24.9,"NOBS_MIN_5")
    u2=irsa_diagnostic_url(65.9,24.9,"NUM_OBS_1")
    a,b=parse_qs(urlparse(u1).query),parse_qs(urlparse(u2).query)
    assert a["POS"]==b["POS"]
    assert a["FORMAT"]==b["FORMAT"]==["csv"]
    assert a["NOBS_MIN"]==["5"]
    assert b["NUM_OBS"]==["1"]
    assert urlparse(u1).hostname=="irsa.ipac.caltech.edu"
    for variant in ("CUSTOM_INJECTION","ID=bad","NUM_OBS_0"):
        with pytest.raises(ValueError):
            irsa_diagnostic_url(65.9,24.9,variant)


@pytest.mark.parametrize("payload,expected",[
    (b"", "EMPTY_HTTP_BODY"),
    (b"<html><body>error 503 secret</body></html>","HTML_SERVER_RESPONSE_NOT_CSV"),
    (b"<?xml version='1.0'?><VOTABLE/>","XML_OR_VOTABLE_NOT_REQUESTED_CSV"),
    (b'{"error":"secret"}',"JSON_SERVER_RESPONSE_NOT_CSV"),
    (b"broken,invalid\nno,header\n","UNRECOGNIZED_IRSA_TABLE_SCHEMA"),
    (csv_fixture(0),"PARSED_TABLE_ZERO_ROWS"),
    (csv_fixture(2),"PARSED_TABLE_WITH_ROWS"),
])
def test_responding_archive_format_is_explicitly_classified(payload,expected):
    r=classify_original_response(payload)
    assert r["outcome"]==expected
    assert "secret" not in str(r)
    if expected=="PARSED_TABLE_WITH_ROWS":
        assert r["returned_rows"]==2


def test_bounded_response_is_not_truncated_into_a_false_empty_catalogue():
    r=classify_original_response(b"x"*(MAX_BYTES+1))
    assert r["outcome"]=="RESPONSE_TOO_LARGE_TO_VALIDATE"
    assert r["returned_rows"] is None


class Response:
    headers={"Content-Type":"text/csv; charset=UTF-8"}
    def __init__(self,body): self.body=body
    def __enter__(self): return self
    def __exit__(self,*a): return False
    def getcode(self): return 200
    def read(self,n): return self.body[:n]


def test_successful_http_response_keeps_digest_but_no_original_photometry():
    raw=csv_fixture(1)
    x=request_diagnostic(65.9,24.9,"NUM_OBS_1",
                         opener=lambda *a,**kw:Response(raw))
    assert x["http_status"]==200
    assert x["response_content_type_group"]=="CSV"
    assert x["original_response_sha256"]==hashlib.sha256(raw).hexdigest()
    assert x["outcome"]=="PARSED_TABLE_WITH_ROWS"
    assert x["returned_rows"]==1
    assert "14.1" not in str(x)
    assert "59000" not in str(x)


def test_http_provider_error_code_retained_and_body_discarded():
    def err(*a,**kw):
        raise HTTPError("http://none",503,"secret",{},None)
    result=request_diagnostic(65.9,24.9,"NOBS_MIN_5",opener=err)
    assert result["http_status"]==503
    assert result["outcome"]=="HTTP_SERVER_ERROR"
    assert "secret" not in str(result)


@pytest.mark.parametrize("previous,expected_calls,recovered",[
    ("PARSED_TABLE_WITH_ROWS",1,True),
    ("PARSED_TABLE_ZERO_ROWS",2,True),
    ("HTML_SERVER_RESPONSE_NOT_CSV",2,True),
    ("HTTP_SERVER_ERROR",1,False),
    ("HTTP_RATE_LIMIT",1,False),
    ("NETWORK_TIMEOUT",2,True),
])
def test_fallback_diagnostic_cannot_claim_physical_identity(
    previous,expected_calls,recovered
):
    count=[0]
    def requester(ra,dec,variant):
        count[0]+=1
        return outcome(previous if variant=="NOBS_MIN_5"
                       else "PARSED_TABLE_WITH_ROWS",variant)
    result=diagnose_frozen_24(SEED,PLAN,request_fn=requester)
    assert result["n_technical_targets_frozen"]==24
    assert result["n_prior_ztf_parsed_targets_not_requeried"]==2
    assert result["n_prior_ztf_unresolved_targets"]==22
    assert result["n_diagnostic_http_requests"]==22*expected_calls
    assert count[0]==22*expected_calls
    assert result["n_unresolved_targets_with_any_parsed_response_rows"]==(
        22 if recovered else 0)
    assert result["scientific_R2_complete"] is False
    assert result["all_gaia_ztf_physical_identities_confirmed"] is False
    assert result["n_confirmed_new_variable_stars"]==0
    assert len(result["rows"])==24
    assert all(not x["physical_gaia_ztf_counterpart_verified"]
               for x in result["rows"])
    assert all(not x["new_variable_star_confirmed"] for x in result["rows"])


def test_zero_row_tables_not_misrepresented_as_zero_real_variable_stars():
    def request_fn(ra,dec,variant):
        return outcome("PARSED_TABLE_ZERO_ROWS",variant)
    d=diagnose_frozen_24(SEED,PLAN,request_fn=request_fn)
    assert d["n_unresolved_targets_with_any_parsed_response_rows"]==0
    assert d["n_previously_unresolved_still_without_parsed_rows"]==22
    assert d["n_confirmed_new_variable_stars"]==0
    assert "NOT an empty sky" in " ".join(d["notes"])
