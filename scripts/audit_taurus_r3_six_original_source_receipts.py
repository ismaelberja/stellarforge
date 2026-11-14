"""Fully offline, fail-closed auditor for both *authentic* R3 DR24 source runs.

The three original raw CSVs were inspected in-memory in real GitHub Actions,
and only byte hashes, masks, QC counts and time-coverage bins are committed.
Three nonresponses were retried once and remain provider timeouts, NOT
astrophysical non-detections. Zero Gaia↔ZTF physical source identifications.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from stellarforge.r3_original_oid_coverage import (
    FIXED_GROUPS, COLLECTION, QC_CATFLAGS_MASK, MIN_QC_VISITS,
    MIN_BASELINE_DAYS, original_exact_oid_url,
)

R2_PATH="reports/taurus_variability_r2/R2_FINAL_24_TECHNICAL_SOURCE_ACCESS_AND_IDENTITY_DECISION_NO_RAW.json"
R2_OID_PATH="reports/taurus_variability_r2/REAL_TWO_FIELDS_ORIGINAL_IRSA_ALTERNATE_OBJECTIDS_NO_RAW.json"
FIRST_PATH="reports/taurus_variability_r3/R3_SIX_ORIGINAL_DR24_FIRST_REQUESTS_NO_RAW.json"
RETRY_PATH="reports/taurus_variability_r3/R3_THREE_ORIGINAL_DR24_TIMEOUT_RETRY_NO_RAW.json"
FIRST_ZIP_SHA="6e9e1cdbba946d9f7c5036e74a42917bb4011530dfec1d289b4b30c47f393049"
RETRY_ZIP_SHA="69f37df9f57c2dc49e4636740fb74c8c429d67e3d250b92201696edd26d89104"
FIRST_JSON_SHA="3d9e864d2028c5040f4c7bd2860d8991fd51e7e22a4f8185029982467d4852ec"
RETRY_JSON_SHA="3de1c4028cf138d450a06ad48062952bd0b439aad4b4602f0815629df8998ebb"
ORIGINAL_FIRST_RESULTS=(
    (79,70,9,1870.876898,(23,33,0,0,10,4),
      "64916a8825f14f1f39dbf16aaf3e404d04cab5c0ab5a258b7d53973f0cf0af87",20724),
    (137,117,20,2528.096678,(22,49,0,0,12,11,23),
      "617c76349d0ed00c34e0cbcbcae92a51916970a114725d2e36413a94eefcefbf",35736),
    (468,404,64,2617.952292,(61,79,80,34,46,43,51,10),
      "391b35a3232341f0c1f9701522cb52aced730d4a9098da9d3ae6c40f2d6d8004",121356),
)


def _same(v:dict,key:str,expected,where:str)->None:
    if not isinstance(v,dict) or key not in v or type(v[key]) is not type(expected) or v[key]!=expected:
        raise ValueError(f"{where}.{key}: inconsistent with original pre-registered source receipt")


def _read(root:Path,rel:str)->dict:
    f=root/rel
    if (f.is_symlink() or not f.is_file() or not f.resolve().is_relative_to(root)):
        raise ValueError("Source ledger missing or path unsafe")
    return json.loads(f.read_text(encoding="utf8"))


def audit_r3_original_six_source_receipts(root:Path)->dict:
    root=Path(root).resolve()
    old=_read(root,R2_PATH);old_oids=_read(root,R2_OID_PATH)
    first=_read(root,FIRST_PATH);retry=_read(root,RETRY_PATH)
    if (old.get("r2_physical_source_identity_success") is not False
            or old.get("r3_physical_stellar_variability_analysis_authorized") is not False
            or old.get("summary",{}).get("independently_authenticated_physical_gaia_ztf_counterparts")!=0):
        raise ValueError("R2 physical Gaia-ZTF identity became falsely authenticated")
    exact=[]
    for f in old_oids["fields"]:
        for x in f["positional_oid_screen"]["original_ztf_oid_band_groups"]:
            exact.append((f["target"],f["gaia_dr3_id"],x["ztf_oid"],x["band"],x["n_original_raw_table_rows"]))
    if tuple(exact)!=FIXED_GROUPS:
        raise ValueError("Original R2 fixed six source ObjectIDs/bands were changed")

    for k,v in (
        ("schema_version","stellarforge-taurus-r3-original-six-ztf-DR24-initial-derived-only-source-receipt-v1"),
        ("original_workflow_run_id",43593335135),
        ("original_derived_only_artifact_id",14113496602),
        ("original_derived_only_artifact_zip_sha256",FIRST_ZIP_SHA),
        ("original_derived_only_source_json_sha256",FIRST_JSON_SHA),
        ("original_exact_requests",6),("timeout_seconds",40),
        ("original_http_success_sources",3),("original_timeout_sources",3),
        ("original_success_raw_rows",684),("original_success_qc_retained_rows",591),
        ("original_success_rejected_catflags_rows",93),
        ("technical_oid_30visit_90day_pass_count",3),
        ("original_gaia_to_ztf_physical_associations_confirmed",0),
        ("original_oid_curves_merged",0),
        ("r3_gaia_target_astrophysical_variability_inference_permitted",False),
        ("query_public_collection",COLLECTION),
    ):_same(first,k,v,"initial_original_R3")
    for k,v in (
        ("schema_version","stellarforge-taurus-r3-three-original-timeouts-retry-source-verified-no-raw-v1"),
        ("original_recovery_workflow_run_id",43593994009),
        ("original_recovery_artifact_id",14113996740),
        ("original_recovery_artifact_zip_sha256",RETRY_ZIP_SHA),
        ("original_recovery_derived_only_json_sha256",RETRY_JSON_SHA),
        ("original_first_run_id",43593335135),
        ("original_first_derived_only_artifact_id",14113496602),
        ("original_first_artifact_zip_sha256",FIRST_ZIP_SHA),
        ("archive_collection",COLLECTION),
        ("original_retry_timeout_seconds",85),
        ("requests_serial",True),
        ("total_retried_original_ztf_oids",3),
        ("n_recovered_original_public_dr24_source_csv",0),
        ("n_fresh_technical_30visit_90day_pass",0),
        ("all_second_retries_original_ztf_provider_timeout_not_scientific_non_detection",True),
        ("original_ztf_source_reselection_or_quality_gate_change",False),
        ("original_gaia_to_ztf_physical_counterparts_authenticated",0),
        ("original_ztf_oid_lightcurves_merged",0),
        ("astrophysical_star_variability_or_companion_claimed",False),
        ("raw_original_photometric_source_rows_persisted",False),
    ):_same(retry,k,v,"original_timeout_recovery")
    first_rows=first.get("per_oid_results")
    timeouts=retry.get("original_timeout_rows")
    if not isinstance(first_rows,list) or len(first_rows)!=6 or not isinstance(timeouts,list) or len(timeouts)!=3:
        raise ValueError("Original six source results / exact three timeout groups missing")
    for i,(src,(name,gaia,oid,band,old_n)) in enumerate(zip(first_rows,FIXED_GROUPS)):
        for k,v in (
            ("original_technical_label",name),("gaia_id_reference_not_a_physical_match",gaia),
            ("original_frozen_ztf_oid",oid),("original_frozen_filter",band),
            ("original_archive_query_url",original_exact_oid_url(oid)),
            ("physical_gaia_to_this_ztf_oid_counterpart_authenticated",False),
        ): _same(src,k,v,f"source_{oid}")
        if i<3:
            raw,good,masked,span,bins,sha,nbytes=ORIGINAL_FIRST_RESULTS[i]
            for k,v in (
                ("original_query_status","ORIGINAL_ZTF_EXACT_OID_CSV_PARSED_AND_QC_AUDITED"),
                ("original_response_sha256",sha),("original_response_bytes",nbytes),
                ("original_provider_raw_rows",raw),("original_local_qc_accepted_rows",good),
                ("original_local_catflags_32768_masked_rows",masked),
                ("original_time_system","MJD"),("original_qc_time_span_days",span),
                ("original_qc_365day_bin_counts",list(bins)),
                ("provisional_technical_30visit_90day_pass",True),
            ): _same(src,k,v,f"first_original_oid_{oid}")
            if raw!=old_n or good+masked!=raw or sum(bins)!=good:
                raise ValueError("Original DR24 source mask/CADENCE count inconsistent with R2 source")
        else:
            for k,v in (
                ("original_query_status","ORIGINAL_PROVIDER_NETWORK_FAILURE"),
                ("original_error_type","TimeoutError"),
                ("original_response_sha256",None),
                ("provisional_technical_30visit_90day_pass",False),
            ): _same(src,k,v,f"first_original_timeout_{oid}")
            other=timeouts[i-3]
            for k,v in (
                ("label",name),("gaia_id_label_not_physical_identity",gaia),
                ("oid",oid),("band",band),
                ("original_first_outcome","TimeoutError"),("original_second_outcome","TimeoutError"),
                ("original_request_url",original_exact_oid_url(oid)),
                ("second_original_response_sha256",None),
            ): _same(other,k,v,f"retry_original_timeout_{oid}")
    if (first.get("original_http_success_sources")+
            retry.get("n_recovered_original_public_dr24_source_csv")!=3):
        raise ValueError("R3 original source technical coverage falsely inflated")
    return {
        "status":"R3_ORIGINAL_SIX_OID_TECHNICAL_PHOTOMETRY_AUDIT_PARTIAL__ORIGINAL_PROVIDER_TIMEOUTS_NO_PHYSICAL_SOURCE_MATCH",
        "original_frozen_ztf_objectids_studied":6,
        "original_dr24_exact_oid_source_csv_successful":3,
        "original_dr24_source_requests_unavailable_after_one_retry":3,
        "original_raw_ztf_source_rows_quality_inspected":684,
        "original_locally_qc_accepted_rows":591,
        "original_masked_catflags_bit15_rows":93,
        "original_independent_oid_band_clock_30visit_90day_pass":3,
        "original_physical_gaia_ztf_sources_authenticated":0,
        "original_ztf_oid_curves_merged":0,
        "r3_physical_stellar_variability_science_eligible":False,
        "genuine_new_astrophysical_variability_or_companion_detected":False,
    }


def main()->None:
    p=argparse.ArgumentParser(description="Offline original R3 six-objectid DR24 source receipt audit; no archive requests")
    p.add_argument("--root",type=Path,default=Path("."))
    args=p.parse_args()
    print(json.dumps(audit_r3_original_six_source_receipts(args.root),indent=2))

if __name__=="__main__":
    main()
