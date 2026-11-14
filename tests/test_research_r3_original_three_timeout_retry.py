"""Synthetic tests for strictly source-frozen IRSA R3 timeout-only recovery."""
from __future__ import annotations

import copy
import csv
import io
import json
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

import pytest

from stellarforge.r3_three_timeout_recovery import (
    FROZEN_TIMEOUT_OIDS, FIRST_RUN, FIRST_ARTIFACT,
    RETRY_TIMEOUT, FIRST_RECEIPT_PATH,
    validate_three_timeouts, retry_three_original_provider_timeouts,
    run_recovery_from_repo,
)

ROOT=Path(__file__).resolve().parents[1]

def receipt():
    return json.loads((ROOT/FIRST_RECEIPT_PATH).read_text(encoding="utf8"))

def fake_csv(oid,band,n=35):
    s=io.StringIO()
    w=csv.DictWriter(s,fieldnames=["oid","fid","mjd","mag","magerr","catflags"])
    w.writeheader()
    for i in range(n):
        w.writerow({"oid":oid,"fid":1 if band=="g" else 2,"mjd":58200+12*i,
                    "mag":"16.2","magerr":"0.04","catflags":0})
    return s.getvalue().encode()

class Response:
    status=200
    headers={"Content-Type":"text/csv"}
    def __init__(self,data):self.data=data
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def read(self,amount):return self.data[:amount]

def test_original_first_run_sha_and_three_timeouts_fixed_before_retry():
    selected=validate_three_timeouts(receipt())
    assert tuple(row["ztf_oid"] for row in selected)==FROZEN_TIMEOUT_OIDS
    assert tuple(row["ztf_filter"] for row in selected)==("r","g","r")
    assert all(row["technical_label"] in ("FT Tau","CIDA 11") for row in selected)

@pytest.mark.parametrize("change",["oid","status","run","original"])
def test_cannot_retarget_original_science_source_or_rerun_success(change):
    j=receipt()
    if change=="oid":j["per_oid_results"][3]["original_frozen_ztf_oid"]="123456789"
    elif change=="status":j["per_oid_results"][3]["original_query_status"]="ORIGINAL_ZTF_EXACT_OID_CSV_PARSED_AND_QC_AUDITED"
    elif change=="run":j["original_workflow_run_id"]=11
    elif change=="original":j["per_oid_results"][0]["provisional_technical_30visit_90day_pass"]=False
    with pytest.raises(ValueError):
        validate_three_timeouts(j)

def test_serial_three_original_requests_only_same_science_gates():
    initial=receipt()
    req=[]
    def mock(request,timeout):
        assert timeout==RETRY_TIMEOUT==85
        p=parse_qs(urlsplit(request.full_url).query)
        assert p["FORMAT"]==["csv"] and p["COLLECTION"]==["ztf_dr24"]
        oid=p["ID"][0]
        req.append(oid)
        band="g" if oid=="610106300008010" else "r"
        return Response(fake_csv(oid,band))
    result=retry_three_original_provider_timeouts(initial,opener=mock)
    assert tuple(req)==FROZEN_TIMEOUT_OIDS
    assert result["previous_original_run_id"]==FIRST_RUN
    assert result["previous_original_artifact_id"]==FIRST_ARTIFACT
    assert result["n_predeclared_original_timeout_oids_requeried"]==3
    assert result["n_retrieved_valid_original_ztf_dr24_oids"]==3
    assert result["n_technical_30visit_90day_pass_oid_band_clock_series"]==3
    assert result["r3_physical_star_inference_authorized"] is False
    assert result["no_original_photometric_rows_saved_or_merged"] is True
    assert all(x["original_retry_status"]=="ORIGINAL_ZTF_EXACT_OID_CSV_PARSED_AND_QC_AUDITED" for x in result["original_retry_source_results"])
    assert all(x["n_technical_pass_series"]==1 for x in result["original_retry_source_results"])
    assert "16.2" not in json.dumps(result)

def test_original_timeouts_remain_technical_service_errors_not_negative_stars():
    def mock(request,timeout):
        raise TimeoutError("synthetic provider")
    res=retry_three_original_provider_timeouts(receipt(),opener=mock)
    assert res["n_retrieved_valid_original_ztf_dr24_oids"]==0
    assert res["provider_status_counts"]=={"ORIGINAL_PROVIDER_NETWORK_FAILURE":3}
    assert res["n_new_original_gaia_to_ztf_physical_counterparts_confirmed"]==0
    assert res["n_new_original_stellar_variables_or_companions_confirmed"]==0

def test_original_bad_photometry_does_not_gain_false_coverage():
    def mock(request,timeout):
        oid=parse_qs(urlsplit(request.full_url).query)["ID"][0]
        return Response(fake_csv(oid,"g" if oid=="610106300008010" else "r",n=3))
    result=retry_three_original_provider_timeouts(receipt(),opener=mock)
    assert result["n_retrieved_valid_original_ztf_dr24_oids"]==3
    assert result["n_technical_30visit_90day_pass_oid_band_clock_series"]==0
    assert not result["r3_physical_star_inference_authorized"]

def test_code_runner_uses_committed_first_source_receipt_not_new_selection():
    results=run_recovery_from_repo(ROOT,opener=lambda req,timeout:Response(
        fake_csv(parse_qs(urlsplit(req.full_url).query)["ID"][0],
                 "g" if "6101063" in req.full_url else "r",n=31)))
    assert results["n_predeclared_original_timeout_oids_requeried"]==3
