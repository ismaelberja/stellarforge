"""Bounded IRSA ZTF diagnostic for the 22 unresolved R2 technical Taurus fields.

The previous Gaia DR3 cohort is frozen at 24. This module distinguishes
HTTP errors, unavailable payloads, oversized responses, parsable zero-row
tables and genuine *returned* positional ZTF catalogue rows. It does not
infer physical Gaia-ZTF identity or absence of astronomical variability.

NO raw downloaded IRSA CSV is written, printed, uploaded or committed.
"""
from __future__ import annotations

from collections import Counter
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import socket
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .coordinates import validate_icrs
from .ztf_photometry import parse_ztf_table

ENDPOINT = "https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves"
MAX_BYTES = 2_000_000
MAX_TARGETS = 24
QUERY_VARIANTS = ("NOBS_MIN_5", "NOBS_MIN_1", "NUM_OBS_1")
VALID = ("PARSED_TABLE_WITH_ROWS", "PARSED_TABLE_ZERO_ROWS")


def validate_frozen_input(seed: bytes, plan: dict) -> tuple[list[dict], set[str]]:
    if hashlib.sha256(seed).hexdigest() != plan["r1_seed_sha256"]:
        raise ValueError("Research seed differs from R1 frozen original input")
    rows = list(csv.DictReader(io.StringIO(seed.decode("utf-8-sig"))))
    ids = [str(row["gaia"]).strip() for row in rows]
    if len(ids) != 24 or len(set(ids)) != 24:
        raise ValueError("Expected exactly the frozen R1 24-source Gaia cohort")
    pending = plan["unresolved_gaia_ids"]
    prior = plan["previously_parsed_gaia_ids"]
    if (len(pending) != 22 or len(prior) != 2
            or len(set(pending)) != 22 or len(set(prior)) != 2
            or set(pending).intersection(prior) or set(ids) != set(pending + prior)
            or plan["n_frozen_targets"] != 24
            or plan["source_run_id"] != 43031689454
            or plan["source_artifact_id"] != 13861901170):
        raise ValueError("Inconsistent original R2 22 unresolved-source plan")
    return rows, set(pending)


def irsa_diagnostic_url(ra: float, dec: float, variant: str) -> str:
    validate_icrs(ra, dec)
    if variant not in QUERY_VARIANTS:
        raise ValueError("Unsupported/query-hacking variant")
    # Exact same frozen 2-arcsec cone and location, compare only
    # documented count-constraint spellings/thresholds.
    kw = {"POS": f"CIRCLE {ra:.9f} {dec:.9f} {2/3600:.10f}",
          "FORMAT": "csv"}
    if variant in ("NOBS_MIN_5", "NOBS_MIN_1"):
        kw["NOBS_MIN"] = "5" if variant == "NOBS_MIN_5" else "1"
    else:
        kw["NUM_OBS"] = "1"         # historical unsuccessful diagnostic variant
    return ENDPOINT + "?" + urlencode(kw)


def classify_original_response(payload: bytes, *, limit: int = MAX_BYTES) -> dict:
    if not isinstance(payload, bytes):
        raise ValueError("Wrong response container")
    if not payload:
        return {"outcome": "EMPTY_HTTP_BODY", "returned_rows": None}
    if len(payload) > limit:
        return {"outcome": "RESPONSE_TOO_LARGE_TO_VALIDATE", "returned_rows": None}
    lead = payload.lstrip()[:256].lower()
    if lead.startswith(b"<!doctype html") or lead.startswith(b"<html"):
        return {"outcome": "HTML_SERVER_RESPONSE_NOT_CSV", "returned_rows": None}
    if lead.startswith(b"<?xml") or lead.startswith(b"<votable"):
        return {"outcome": "XML_OR_VOTABLE_NOT_REQUESTED_CSV", "returned_rows": None}
    if lead.startswith(b"{") or lead.startswith(b"["):
        return {"outcome": "JSON_SERVER_RESPONSE_NOT_CSV", "returned_rows": None}
    try:
        rows, format_name = parse_ztf_table(payload)
    except (UnicodeError, ValueError, TypeError, csv.Error, OverflowError):
        return {"outcome": "UNRECOGNIZED_IRSA_TABLE_SCHEMA", "returned_rows": None}
    if len(rows) > 200000:
        return {"outcome": "ROW_COUNT_CAP_EXCEEDED", "returned_rows": None}
    return {
        "outcome": "PARSED_TABLE_WITH_ROWS" if rows else "PARSED_TABLE_ZERO_ROWS",
        "returned_rows": len(rows),
        "source_table_format": format_name,
    }


def request_diagnostic(ra: float, dec: float, variant: str, *,
                       timeout_sec: float = 12.0, opener=urlopen) -> dict:
    if not math.isfinite(timeout_sec) or not 3 <= timeout_sec <= 25:
        raise ValueError("Diagnostic timeout outside permitted limits")
    url = irsa_diagnostic_url(ra, dec, variant)
    result = {
        "variant": variant,
        "query_sha256": hashlib.sha256(url.encode()).hexdigest(),
        "http_status": None,
        "response_content_type_group": "UNKNOWN",
        "original_response_sha256": None,
        "response_bytes": None,
        "outcome": "NOT_EXECUTED",
        "returned_rows": None,
    }
    try:
        request = Request(url, method="GET", headers={
            "User-Agent": "StellarForge/2.0 Taurus R2 bounded IRSA source failure diagnosis",
            "Accept": "text/csv,text/plain",
        })
        with opener(request, timeout=timeout_sec) as response:
            status = int(response.getcode() or 200)
            result["http_status"] = status
            content_type = str(response.headers.get("Content-Type", "")).lower()
            if "csv" in content_type:
                result["response_content_type_group"] = "CSV"
            elif "html" in content_type:
                result["response_content_type_group"] = "HTML"
            elif "xml" in content_type:
                result["response_content_type_group"] = "XML"
            elif "text" in content_type:
                result["response_content_type_group"] = "OTHER_TEXT"
            else:
                result["response_content_type_group"] = "OTHER_OR_MISSING"
            raw = response.read(MAX_BYTES + 1)
        result["response_bytes"] = len(raw)
        if len(raw) <= MAX_BYTES:
            result["original_response_sha256"] = hashlib.sha256(raw).hexdigest()
        result.update(classify_original_response(raw))
        return result
    except HTTPError as exc:
        code = int(exc.code)
        result["http_status"] = code
        result["outcome"] = (
            "HTTP_RATE_LIMIT" if code == 429 else
            "HTTP_SERVER_ERROR" if code >= 500 else
            "HTTP_CLIENT_ERROR")
        return result
    except (socket.timeout, TimeoutError):
        result["outcome"] = "NETWORK_TIMEOUT"
        return result
    except URLError as exc:
        if isinstance(exc.reason, (socket.timeout, TimeoutError)):
            result["outcome"] = "NETWORK_TIMEOUT"
        else:
            result["outcome"] = "NETWORK_OR_TLS_ERROR"
        return result
    except OSError:
        result["outcome"] = "NETWORK_OR_TLS_ERROR"
        return result


def diagnose_frozen_24(seed: bytes, plan: dict, *,
                       request_fn=request_diagnostic) -> dict:
    """Return complete 24-source ledger; only previously failed 22 queried.

    The two previous successful sources are preserved as prior-run records
    and explicitly NOT claimed to be new observations in this diagnostic.
    """
    rows, unresolved = validate_frozen_input(seed, plan)
    results = []
    for original in rows:
        sid = str(original["gaia"]).strip()
        row = {
            "gaia_dr3_source_id": sid,
            "prior_r2_ztf_status": (
                "PREVIOUSLY_PARSED_MULTIPLE_OIDS_NOT_IDENTITY_VERIFIED"
                if sid not in unresolved else "UNAVAILABLE_OR_UNPARSEABLE"),
            "physical_gaia_ztf_counterpart_verified": False,
            "new_variable_star_confirmed": False,
        }
        if sid in unresolved:
            ra, dec = float(original["ra"]), float(original["dec"])
            original_attempt = request_fn(ra, dec, "NOBS_MIN_5")
            attempts = [original_attempt]
            if original_attempt["outcome"] != "PARSED_TABLE_WITH_ROWS" and original_attempt["outcome"] not in (
                    "HTTP_RATE_LIMIT", "HTTP_SERVER_ERROR", "RESPONSE_TOO_LARGE_TO_VALIDATE"):
                attempts.append(request_fn(ra, dec, "NUM_OBS_1"))
            row["diagnostic_attempts"] = attempts
            row["recovered_original_positional_rows"] = any(
                x["outcome"] == "PARSED_TABLE_WITH_ROWS" for x in attempts)
            row["query_result_is_physical_source_identification"] = False
        else:
            row["diagnostic_attempts"] = []
            row["recovered_original_positional_rows"] = False
        results.append(row)
    outcomes = Counter(
        attempt["outcome"]
        for row in results for attempt in row["diagnostic_attempts"])
    recovered = sum(r["recovered_original_positional_rows"] for r in results)
    return {
        "phase": "R2_IRSA_FAILURE_DIAGNOSIS_ONLY_NOT_PHYSICAL_MATCH",
        "n_technical_targets_frozen": 24,
        "n_prior_ztf_parsed_targets_not_requeried": 2,
        "n_prior_ztf_unresolved_targets": 22,
        "n_unresolved_targets_with_any_parsed_response_rows": recovered,
        "n_previously_unresolved_still_without_parsed_rows": 22 - recovered,
        "n_diagnostic_http_requests": sum(
            len(r["diagnostic_attempts"]) for r in results),
        "status_counts_per_attempt": dict(sorted(outcomes.items())),
        "original_r1_seed_sha256": hashlib.sha256(seed).hexdigest(),
        "prior_original_ztf_run": plan["source_run_id"],
        "all_gaia_ztf_physical_identities_confirmed": False,
        "n_confirmed_new_variable_stars": 0,
        "n_new_original_science_fits_image_reviews": 0,
        "scientific_R2_complete": False,
        "rows": results,
        "notes": [
            "Previous 22 service/query failures were NOT astrophysical nondetections.",
            "A valid returned positional ZTF CSV is NOT a confirmed Gaia-to-ZTF physical source.",
            "Zero-row CSV means zero rows under that query/threshold, NOT an empty sky or nonvariable star.",
            "HTTP errors, XML/HTML/JSON, size limits and timeouts are classified separately without leaking provider response bodies.",
            "No original lightcurve rows, FITS pixels or Gaia raw TAP CSV were persisted.",
        ],
    }
