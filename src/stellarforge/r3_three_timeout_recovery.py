"""One serial DR24 access-only retry for three previously timed-out R3 OIDs.

No source/epoch/QC threshold change, original CSV saved nowhere.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .r3_original_oid_coverage import (
    COLLECTION, FIXED_GROUPS, MAX_BYTES, original_exact_oid_url,
    technical_coverage_from_original_bytes,
)

FIRST_RUN = 43593335135
FIRST_ARTIFACT = 14113496602
FIRST_ZIP_SHA256 = "6e9e1cdbba946d9f7c5036e74a42917bb4011530dfec1d289b4b30c47f393049"
FIRST_RECEIPT_PATH = Path("reports/taurus_variability_r3/R3_SIX_ORIGINAL_DR24_FIRST_REQUESTS_NO_RAW.json")
FROZEN_TIMEOUT_OIDS = ("609208400001969", "610106300008010", "610206300011997")
RETRY_TIMEOUT = 85.0


def validate_three_timeouts(original_first_ledger:dict)->tuple[dict,...]:
    if (original_first_ledger.get("original_workflow_run_id")!=FIRST_RUN
            or original_first_ledger.get("original_derived_only_artifact_id")!=FIRST_ARTIFACT
            or original_first_ledger.get("original_derived_only_artifact_zip_sha256")!=FIRST_ZIP_SHA256
            or original_first_ledger.get("original_exact_requests")!=6
            or original_first_ledger.get("timeout_seconds")!=40
            or original_first_ledger.get("original_http_success_sources")!=3
            or original_first_ledger.get("original_timeout_sources")!=3
            or original_first_ledger.get("original_gaia_to_ztf_physical_associations_confirmed")!=0):
        raise ValueError("Original first-run physical-source or provenance contract is inconsistent")
    items=original_first_ledger.get("per_oid_results")
    if not isinstance(items,list) or len(items)!=len(FIXED_GROUPS):
        raise ValueError("Original six R2 sources must be present once in frozen order")
    picked=[]
    for item,(label,gaia,oid,band,_) in zip(items,FIXED_GROUPS):
        if (item.get("original_technical_label")!=label
                or item.get("gaia_id_reference_not_a_physical_match")!=gaia
                or item.get("original_frozen_ztf_oid")!=oid
                or item.get("original_frozen_filter")!=band
                or item.get("physical_gaia_to_this_ztf_oid_counterpart_authenticated") is not False):
            raise ValueError("First-run original R2 cohort was manipulated")
        if oid in FROZEN_TIMEOUT_OIDS:
            if (item.get("original_query_status")!="ORIGINAL_PROVIDER_NETWORK_FAILURE"
                    or item.get("original_error_type")!="TimeoutError"
                    or item.get("original_response_sha256") is not None
                    or item.get("provisional_technical_30visit_90day_pass") is not False):
                raise ValueError("New retry source was not a first-run provider timeout")
            picked.append({"technical_label":label,"original_gaia_context_id":gaia,
                           "ztf_oid":oid,"ztf_filter":band})
        else:
            if (item.get("original_query_status")!="ORIGINAL_ZTF_EXACT_OID_CSV_PARSED_AND_QC_AUDITED"
                    or item.get("provisional_technical_30visit_90day_pass") is not True
                    or not isinstance(item.get("original_response_sha256"),str)):
                raise ValueError("Successful original ZTF source was retroactively replaced")
    if tuple(p["ztf_oid"] for p in picked)!=FROZEN_TIMEOUT_OIDS:
        raise ValueError("Exact three originally timed-out source OIDs were altered")
    return tuple(picked)


def _one_original_retry(record:dict, *, opener=urlopen)->dict:
    oid=record["ztf_oid"]
    url=original_exact_oid_url(oid)
    base={**record,"original_exact_oid_query_url":url,
          "retry_follows_original_source_timeout_run":FIRST_RUN,
          "original_public_ztf_collection":COLLECTION,
          "original_retry_timeout_seconds":RETRY_TIMEOUT,
          "original_provider_raw_source_data_saved":False,
          "gaia_ztf_physical_source_authenticated":False,
          "physical_target_variability_inference_allowed":False,
          "oid_curves_merged":False}
    request=Request(url, method="GET",headers={
        "Accept":"text/csv,text/plain",
        "User-Agent":"StellarForge/2.1 original IRSA DR24 R3 fixed timeout-only recovery"
    })
    try:
        with opener(request,timeout=RETRY_TIMEOUT) as response:
            status=response.status
            ctype=str(response.headers.get("Content-Type","")).split(";")[0].strip().lower()
            raw=response.read(MAX_BYTES+1)
    except HTTPError as error:
        return {**base,"original_retry_status":"ORIGINAL_PROVIDER_HTTP_ERROR",
                "http_status":error.code,"n_technical_pass_series":0}
    except (URLError,TimeoutError,OSError) as error:
        return {**base,"original_retry_status":"ORIGINAL_PROVIDER_NETWORK_FAILURE",
                "original_error_type":type(error).__name__,"n_technical_pass_series":0}
    if len(raw)>MAX_BYTES:
        return {**base,"original_retry_status":"ORIGINAL_RESPONSE_EXCEEDS_FROZEN_BYTE_CAP",
                "http_status":status,"response_content_type":ctype,"n_technical_pass_series":0}
    meta={"http_status":status,"response_content_type":ctype,
          "original_response_bytes":len(raw),
          "original_response_sha256":hashlib.sha256(raw).hexdigest()}
    if not raw:
        return {**base,"original_retry_status":"ORIGINAL_PROVIDER_EMPTY_RESPONSE",
                **meta,"n_technical_pass_series":0}
    try:
        result=technical_coverage_from_original_bytes(raw,oid=oid,band=record["ztf_filter"])
    except (KeyError,ValueError,TypeError,OverflowError,UnicodeError) as error:
        return {**base,**meta,"original_retry_status":"ORIGINAL_PROVIDER_RESPONSE_INVALID_FOR_FROZEN_QC",
                "error_type":type(error).__name__,"n_technical_pass_series":0}
    return {**base,**meta,"original_retry_status":result.pop("status"),**result,
            "n_technical_pass_series":result["n_technical_coverage_pass_series"]}


def retry_three_original_provider_timeouts(first:dict, *, opener=urlopen)->dict:
    records=validate_three_timeouts(first)
    results=[_one_original_retry(r,opener=opener) for r in records]
    n_ok=sum(r["original_retry_status"]=="ORIGINAL_ZTF_EXACT_OID_CSV_PARSED_AND_QC_AUDITED" for r in results)
    n_technical=sum(r["n_technical_pass_series"] for r in results)
    return {
        "schema_version":"stellarforge-taurus-r3-three-fixed-original-timeouts-only-recovery-no-raw-v1",
        "phase":"R3_ORIGINAL_DR24_EXACT_OID_TIMEOUT_ONLY_RECOVERY__NO_PHYSICAL_GAIA_MATCH",
        "previous_original_run_id":FIRST_RUN,
        "previous_original_artifact_id":FIRST_ARTIFACT,
        "previous_original_artifact_zip_sha256":FIRST_ZIP_SHA256,
        "n_predeclared_original_timeout_oids_requeried":3,
        "n_retrieved_valid_original_ztf_dr24_oids":n_ok,
        "n_technical_30visit_90day_pass_oid_band_clock_series":n_technical,
        "n_new_original_gaia_to_ztf_physical_counterparts_confirmed":0,
        "n_new_original_stellar_variables_or_companions_confirmed":0,
        "r3_physical_star_inference_authorized":False,
        "no_new_original_ztf_objectid_selection":True,
        "no_original_photometric_rows_saved_or_merged":True,
        "provider_status_counts":dict(sorted(Counter(r["original_retry_status"] for r in results).items())),
        "original_retry_source_results":results,
        "caveats":[
            "This separate, prospective access-only study retries exclusively the three original exact DR24 ObjectIDs that timed out in the first six-source run; no original previously successful source is re-queried.",
            "No scientific/photometric R1 thresholds or original source/epoch/field/band decisions are changed. Different network timeout/concurrency is explicitly recorded.",
            "Access failures or a parser rejection are not astrophysical non-detections or poor-quality photometry.",
            "Technical source ObjectID coverage is not physical FT Tau or CIDA 11 source identification; all R2 physical Gaia-ZTF matches remain unproven.",
            "No raw ZTF photometry, per-epoch time/magnitude, stellar lightcurves, original pixels or new astrophysical variability measurements are persisted."
        ]
    }


def run_recovery_from_repo(root:Path, *, opener=urlopen)->dict:
    initial=json.loads((Path(root)/FIRST_RECEIPT_PATH).read_text(encoding="utf8"))
    return retry_three_original_provider_timeouts(initial,opener=opener)
