"""Taurus R2: nine-target follow-up of genuine unresolved IRSA positional requests.

All target IDs are selected *solely* from the previous original response
ledger, not from variability or results. Reattempt eight timed-out
NOBS_MIN=5 requests with a larger bounded timeout (25s); for the one
prior valid zero-row five-visit request, try the documented NOBS_MIN=1
threshold. No automatic provider hammering or retry loops.

A returned positional photometric table is NOT a physical Gaia-ZTF
crossmatch, an astrophysical detection, or an independently vetted light curve.
"""
from __future__ import annotations

from collections import Counter
import csv
import hashlib
import io
import json
import time
from pathlib import Path

from .r2_irsa_failure_diagnosis import request_diagnostic

OLD_LIVE_RUN_ID = 43037800319
OLD_FIRST_IRSA_RUN_ID = 43031689454
N_FROZEN = 24
N_PRIOR_ACCESSIBLE = 15
N_UNRESOLVED = 9

def freeze_nine_original_sources(seed_bytes: bytes, previous: dict) -> list[dict]:
    """Fail closed unless the previous 24-source ledger is self-consistent."""
    rows=list(csv.DictReader(io.StringIO(seed_bytes.decode("utf-8-sig"))))
    if len(rows)!=N_FROZEN or len({r["gaia"] for r in rows})!=N_FROZEN:
        raise ValueError("The previous 24 Gaia IDs are no longer a frozen cohort")
    if previous.get("original_r1_seed_sha256")!=hashlib.sha256(seed_bytes).hexdigest():
        raise ValueError("Original R1 seed hash mismatch")
    if previous.get("prior_original_ztf_run")!=OLD_FIRST_IRSA_RUN_ID:
        raise ValueError("Previous original-data run provenance mismatch")
    if any(previous.get(k)!=v for k,v in (
        ("n_technical_targets_frozen",24),
        ("n_prior_ztf_parsed_targets_not_requeried",2),
        ("n_prior_ztf_unresolved_targets",22),
        ("n_unresolved_targets_with_any_parsed_response_rows",13),
        ("n_previously_unresolved_still_without_parsed_rows",9),
    )):
        raise ValueError("Previous 15/24 positional source-access ledger was altered")
    prev=previous.get("rows")
    if not isinstance(prev,list) or len(prev)!=24:
        raise ValueError("Missing previous source-level survey status ledger")
    seen={}
    for p in prev:
        sid=str(p["gaia_dr3_source_id"])
        if sid in seen:
            raise ValueError("Duplicated previous Gaia ID")
        seen[sid]=p
    if set(seen)!={r["gaia"] for r in rows}:
        raise ValueError("Original source cohort changed before follow-up")
    pending=[]
    for r in rows:
        sid=r["gaia"]
        old=seen[sid]
        if old.get("prior_r2_ztf_status")=="PREVIOUSLY_PARSED_MULTIPLE_OIDS_NOT_IDENTITY_VERIFIED":
            if old.get("diagnostic_attempts") or old.get("recovered_original_positional_rows"):
                raise ValueError("Prior originally-parsed sources have altered status")
            continue
        attempts=old.get("diagnostic_attempts",[])
        if old.get("recovered_original_positional_rows"):
            if len(attempts)!=1 or attempts[0].get("outcome")!="PARSED_TABLE_WITH_ROWS":
                raise ValueError("Previously recovered original source inconsistent")
            continue
        if len(attempts)!=2 or attempts[1].get("http_status")!=400:
            raise ValueError("Unresolved source previous-IRSA status was altered")
        old_outcome=attempts[0].get("outcome")
        if old_outcome not in ("NETWORK_TIMEOUT","PARSED_TABLE_ZERO_ROWS"):
            raise ValueError("Unexpected previous initial IRSA response type")
        pending.append({
            "gaia_dr3_source_id":sid,
            "ra":float(r["ra"]),"dec":float(r["dec"]),
            "old_original_irsa_outcome":old_outcome,
            "query_variant": "NOBS_MIN_1" if old_outcome=="PARSED_TABLE_ZERO_ROWS" else "NOBS_MIN_5",
        })
    if len(pending)!=N_UNRESOLVED:
        raise ValueError("Exactly nine previously unresolved technical targets expected")
    if sum(x["query_variant"]=="NOBS_MIN_1" for x in pending)!=1:
        raise ValueError("Exactly one originally empty NOBS_MIN=5 target expected")
    return pending


def recover_nine(seed_bytes:bytes, previous:dict, *,
                 requester=request_diagnostic, pause_sec:float=1.)->dict:
    """Make <=9 bounded IRSA requests, one per pending source, no retries."""
    if not 0<=pause_sec<=3:
        raise ValueError("Request spacing must be 0..3 seconds")
    pending=freeze_nine_original_sources(seed_bytes,previous)
    out=[]
    for i, p in enumerate(pending):
        if i and pause_sec:
            time.sleep(pause_sec)
        response=requester(p["ra"],p["dec"],p["query_variant"],timeout_sec=25.)
        if not isinstance(response,dict) or response.get("variant")!=p["query_variant"]:
            raise ValueError("Request callback returned wrong query variant")
        permitted_keys={
            "variant","query_sha256","http_status","response_content_type_group",
            "original_response_sha256","response_bytes","outcome",
            "returned_rows","source_table_format",
        }
        if set(response)-permitted_keys:
            raise ValueError("Unexpected original photometry or server body in response metadata")
        result={
            "gaia_dr3_source_id":p["gaia_dr3_source_id"],
            "previous_status":p["old_original_irsa_outcome"],
            "current_original_provider_response":response,
            "parsed_positional_table_with_rows":response.get("outcome")=="PARSED_TABLE_WITH_ROWS",
            "physical_gaia_ztf_source_identity_authenticated":False,
            "observed_stellar_variability_confirmed":False,
        }
        out.append(result)
    status_counts=dict(sorted(Counter(
        q["current_original_provider_response"]["outcome"] for q in out).items()))
    new=sum(x["parsed_positional_table_with_rows"] for x in out)
    return {
        "phase":"TAURUS_R2_NINE_ORIGINAL_IRSA_REQUESTS_NOT_PHYSICAL_CROSSMATCH",
        "source_gaia_dr3_ids_frozen":N_FROZEN,
        "preexisting_parsed_ztf_sky_positions":N_PRIOR_ACCESSIBLE,
        "previously_unresolved_ztf_positions":N_UNRESOLVED,
        "n_actual_original_irsa_requests":len(out),
        "n_new_positions_with_parsed_positional_ztf_rows":new,
        "n_cumulative_positions_with_historically_parsed_ztf_rows":N_PRIOR_ACCESSIBLE+new,
        "n_still_without_any_parsed_original_ztf_response":N_UNRESOLVED-new,
        "per_request_status_counts":status_counts,
        "n_ztf_physical_counterparts_independently_verified":0,
        "n_genuine_astrophysical_variability_results_confirmed":0,
        "n_original_science_image_psf_mask_vetted":0,
        "scientific_r2_complete":False,
        "frozen_r1_sha256":hashlib.sha256(seed_bytes).hexdigest(),
        "preceding_original_irsa_diagnostic_run":OLD_LIVE_RUN_ID,
        "public_source_derived_statuses_only":True,
        "per_source":out,
        "limitations":[
            "The original 15 previously parseable source positions are historical, not newly downloaded here.",
            "Nine Gaia-seed-centred ZTF sky queries cannot establish physical Gaia/ZTF source identities.",
            "Unreturned/empty tables are not nonvariable stars or proof of an empty sky.",
            "ZTF object IDs may be multiple per band, and original FITS image/mask/PSF evidence remains unreviewed.",
            "This technical Taurus subset is nonrepresentative of the Taurus stellar population.",
        ],
    }
