"""R3 technical coverage for six frozen original FT Tau / CIDA 11 ZTF ObjectIDs.

Does not establish a physical Gaia-to-ZTF source match, target variability,
stellar class or cross-filter/field lightcurve merge.

Original responses remain IN MEMORY; only bounded per-ObjectID summaries,
response digests and failure types may be persisted.
"""
from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import math
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, parse_qs
from urllib.request import Request, urlopen

from .ztf_photometry import BANDS, inspect_ztf_bytes, parse_ztf_table

ORIGINAL_R2_PATH = Path("reports/taurus_variability_r2/REAL_TWO_FIELDS_ORIGINAL_IRSA_ALTERNATE_OBJECTIDS_NO_RAW.json")
ORIGINAL_R2_DECISION_PATH = Path("reports/taurus_variability_r2/R2_FINAL_24_TECHNICAL_SOURCE_ACCESS_AND_IDENTITY_DECISION_NO_RAW.json")
R1_SEED_SHA = "9cecb94704f028a981045629ad16ecb770f51bba4b6bb3bf13dda769327ff37e"
IRSA_URL = "https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves"
COLLECTION = "ztf_dr24"
MAX_BYTES = 4 * 1024 * 1024
TIMEOUT = 40.0
QC_CATFLAGS_MASK = 32768
MIN_QC_VISITS = 30
MIN_BASELINE_DAYS = 90.0
COVERAGE_BIN_DAYS = 365.0
FIXED_GROUPS = (
    ("FT Tau", "149623711269425408", "1605115300003377", "g", 79),
    ("FT Tau", "149623711269425408", "1605215300005161", "r", 137),
    ("FT Tau", "149623711269425408", "609108400001155", "g", 468),
    ("FT Tau", "149623711269425408", "609208400001969", "r", 758),
    ("CIDA 11", "3419110734340795648", "610106300008010", "g", 469),
    ("CIDA 11", "3419110734340795648", "610206300011997", "r", 737),
)
R3_PASS = "TECHNICAL_OID_PHOTOMETRY_COVERAGE_PASS__PHYSICAL_TARGET_IDENTITY_UNVERIFIED"
R3_FAIL = "TECHNICAL_OID_PHOTOMETRY_COVERAGE_INSUFFICIENT__PHYSICAL_TARGET_IDENTITY_UNVERIFIED"


def validate_frozen_source_groups(r2_oid_ledger: dict, r2_decision_ledger: dict) -> list[dict]:
    """Require the previous real source ID/band/metadata, 24-target R2 NO-GO."""
    if (r2_decision_ledger.get("r1_technical_seed_sha256") != R1_SEED_SHA
            or r2_decision_ledger.get("r2_physical_source_identity_success") is not False
            or r2_decision_ledger.get("r3_physical_stellar_variability_analysis_authorized") is not False
            or r2_decision_ledger.get("summary", {}).get("independently_authenticated_physical_gaia_ztf_counterparts") != 0
            or r2_decision_ledger.get("summary", {}).get("original_journal_table_exact_gaia_ids_and_positions_verified") != 24):
        raise ValueError("Original 24-source R2 scientific/source-provenance status changed")
    fields = r2_oid_ledger.get("fields")
    if not isinstance(fields, list) or len(fields) != 2:
        raise ValueError("R2 original ObjectID fields not exactly the two frozen targets")
    actual = []
    for field in fields:
        name, id = field["target"], field["gaia_dr3_id"]
        if field.get("original_gaia_ztf_physical_identity_confirmed") is not False:
            raise ValueError("R2 source physical identity was silently changed")
        entry = field["positional_oid_screen"]
        if (entry.get("all_source_identities_physical_unconfirmed") is not True
                or entry.get("all_oid_curves_kept_separate") is not True):
            raise ValueError("R2 original ZTF ObjectIDs are not held separate")
        for g in entry["original_ztf_oid_band_groups"]:
            if g.get("gaia_ztf_physical_identity_confirmed") is not False:
                raise ValueError("R2 original per-OID source identity invalid")
            actual.append((name, id, g["ztf_oid"], g["band"], g["n_original_raw_table_rows"]))
    if tuple(actual) != FIXED_GROUPS:
        raise ValueError("R3 source selection differs from the six preregistered original R2 OIDs")
    return [
        {"technical_label": name, "original_gaia_context_id": gaia,
         "ztf_oid": oid, "ztf_filter": band, "r2_historical_positional_response_rows": n}
        for name, gaia, oid, band, n in FIXED_GROUPS
    ]


def original_exact_oid_url(oid: str) -> str:
    if oid not in {x[2] for x in FIXED_GROUPS}:
        raise ValueError("Unregistered original R2 ObjectID requested")
    url = IRSA_URL + "?" + urlencode({"ID": oid, "FORMAT": "csv", "COLLECTION": COLLECTION})
    parts = urlsplit(url)
    params = parse_qs(parts.query)
    if (parts.scheme != "https" or parts.hostname != "irsa.ipac.caltech.edu"
            or params != {"ID":[oid], "FORMAT":["csv"], "COLLECTION":[COLLECTION]}):
        raise ValueError("Unexpected original archive query")
    return url


def _request_original_exact_oid(oid: str, *, opener=urlopen) -> tuple[bytes | None, dict]:
    url=original_exact_oid_url(oid)
    req=Request(url, method="GET", headers={
        "Accept": "text/csv,text/plain", "User-Agent": "StellarForge/2.1 research R3 fixed-source original-ZTF-QC"
    })
    try:
        with opener(req, timeout=TIMEOUT) as response:
            status=response.status
            ctype=str(response.headers.get("Content-Type","")).split(";")[0].strip().lower()
            raw=response.read(MAX_BYTES+1)
    except HTTPError as ex:
        return None,{"status":"ORIGINAL_PROVIDER_HTTP_ERROR","http_status":ex.code}
    except (URLError,TimeoutError,OSError) as ex:
        return None,{"status":"ORIGINAL_PROVIDER_NETWORK_FAILURE","error_type":type(ex).__name__}
    if len(raw) > MAX_BYTES:
        return None,{"status":"ORIGINAL_RESPONSE_EXCEEDS_FROZEN_BYTE_CAP","http_status":status,
                     "response_size_over_cap":True,"response_content_type":ctype}
    result={"http_status":status,"response_content_type":ctype,
            "original_response_bytes":len(raw),
            "original_response_sha256":hashlib.sha256(raw).hexdigest()}
    if not raw:
        return None,{"status":"ORIGINAL_PROVIDER_EMPTY_RESPONSE",**result}
    return raw,result


def technical_coverage_from_original_bytes(raw: bytes, *, oid: str, band: str) -> dict:
    """Only report original OID/band/clock counts, spans, quality rejections."""
    if not isinstance(raw,bytes) or not raw or len(raw)>MAX_BYTES:
        raise ValueError("Original R3 payload empty or over predeclared byte cap")
    rows, format_name = parse_ztf_table(raw)
    if format_name != "csv":
        raise ValueError("Exact original ObjectID query returned non-CSV rows")
    if not rows:
        return {"status":"ORIGINAL_SOURCE_EMPTY_VALID_CSV","raw_original_rows":0,
                "qc_accepted_rows":0,"rejected_rows":0,"qc_rejections":{},
                "per_oid_band_time_system":[],"n_technical_coverage_pass_series":0}
    for row in rows:
        val = str(row.get("oid","")).strip()
        raw_band = str(row.get("filtercode") or row.get("fid") or row.get("filterid") or "").lower()
        if val != oid:
            raise ValueError("Exact original OID API returned an unrequested ObjectID")
        if BANDS.get(raw_band) != band:
            raise ValueError("Original OID filter changed relative to R2 frozen native band")
    # This existing quality checker does NOT equate source positions or
    # magnitude time-domain features to physical Gaia star variability.
    audit, points = inspect_ztf_bytes(raw, catflags_mask=QC_CATFLAGS_MASK,
                                      min_good_epochs=MIN_QC_VISITS)
    if audit["source_format"]!="csv" or audit["raw_rows"]!=len(rows):
        raise ValueError("Original ZTF CSV parse/QC drift")
    grouped={}
    for point in points:
        if (point.oid,point.band)!=(oid,band):
            raise ValueError("Quality checker changed original OID/band")
        grouped.setdefault(point.time_scale,[]).append(point.time_value)
    series=[]
    passes=0
    for scale in sorted(grouped):
        times=sorted(grouped[scale])
        n=len(times)
        span=times[-1]-times[0]
        if not math.isfinite(span) or span < 0:
            raise ValueError("Invalid original ZTF time span")
        bins=Counter(int((t-times[0])/COVERAGE_BIN_DAYS) for t in times)
        count_bins=[bins.get(i,0) for i in range(max(bins)+1)]
        qc_ok=n>=MIN_QC_VISITS and span>=MIN_BASELINE_DAYS
        passes+=int(qc_ok)
        series.append({
            "ztf_oid":oid,"band":band,"time_system_as_reported":scale,
            "n_locally_qc_accepted_epochs":n,
            "time_span_days":round(span,6),
            "n_original_365day_bins_in_coverage_window":len(count_bins),
            "n_nonempty_365day_bins":len(bins),
            "epochs_per_365day_bin_from_first_accepted_visit":count_bins,
            "at_least_30_qc_accepted_epochs":n>=MIN_QC_VISITS,
            "at_least_90day_baseline":span>=MIN_BASELINE_DAYS,
            "technical_oid_coverage_status":R3_PASS if qc_ok else R3_FAIL,
            "physical_gaia_ztf_source_authenticated":False,
            "stellar_variability_analysis_authorized":False,
        })
    return {
        "status":"ORIGINAL_ZTF_EXACT_OID_CSV_PARSED_AND_QC_AUDITED",
        "raw_original_rows":audit["raw_rows"],
        "qc_accepted_rows":audit["kept_rows"],
        "rejected_rows":audit["rejected_rows"],
        "qc_rejections":audit["rejected_reasons"],
        "n_original_rows_with_multiple_time_columns":audit["raw_rows_with_multiple_time_columns"],
        "n_distinct_oid_band_time_system_series":len(series),
        "per_oid_band_time_system":series,
        "n_technical_coverage_pass_series":passes,
    }


def _run_one(frozen: dict, *, opener=urlopen) -> dict:
    oid=frozen["ztf_oid"]
    url=original_exact_oid_url(oid)
    base={
        **frozen,
        "original_exact_oid_query_url":url,
        "archive_collection_explicit":COLLECTION,
        "local_catflags_reject_mask":QC_CATFLAGS_MASK,
        "minimum_locally_qc_accepted_epochs":MIN_QC_VISITS,
        "minimum_time_baseline_days":MIN_BASELINE_DAYS,
        "original_physical_gaia_ztf_target_source_authenticated":False,
        "r3_original_gaia_star_variability_science_authorized":False,
        "raw_photometry_rows_or_magnitudes_saved":False,
        "original_ztf_oid_curves_merged":False,
    }
    payload, response=_request_original_exact_oid(oid,opener=opener)
    if payload is None:
        return {**base,"original_archive_query_status":response.pop("status"),**response,
                "n_technical_coverage_pass_series":0}
    try:
        checked=technical_coverage_from_original_bytes(payload,oid=oid,band=frozen["ztf_filter"])
        return {**base,"original_archive_query_status":checked.pop("status"),
                **response,**checked}
    except (ValueError,KeyError,TypeError,OverflowError,UnicodeError) as ex:
        # Derived only. No original bad-content echo or per-row payloads.
        return {**base,"original_archive_query_status":"ORIGINAL_PROVIDER_RESPONSE_INVALID_FOR_FROZEN_QC",
                **response,"parser_error_type":type(ex).__name__,
                "n_technical_coverage_pass_series":0}


def r3_six_original_oid_qc(r2_oid_ledger: dict, r2_decision_ledger: dict,
                           *, opener=urlopen, workers:int=2)->dict:
    if workers not in (1,2):
        raise ValueError("At most two concurrent original IRSA requests")
    groups=validate_frozen_source_groups(r2_oid_ledger,r2_decision_ledger)
    # Fixed ordering from R2. No data-driven selection of OIDs/epochs.
    with ThreadPoolExecutor(max_workers=workers) as pool:
        rows=list(pool.map(lambda g: _run_one(g,opener=opener),groups))
    c=Counter(z["original_archive_query_status"] for z in rows)
    passes=sum(z["n_technical_coverage_pass_series"] for z in rows)
    clean=sum(z.get("qc_accepted_rows",0) for z in rows)
    raw=sum(z.get("raw_original_rows",0) for z in rows)
    success=sum(z["original_archive_query_status"]=="ORIGINAL_ZTF_EXACT_OID_CSV_PARSED_AND_QC_AUDITED" for z in rows)
    if success==0:
        status="R3_ORIGINAL_ARCHIVE_PILOT_BLOCKED_ALL_SIX_EXACT_OIDS"
    else:
        status="R3_TECHNICAL_OID_COVERAGE_AUDITED__PHYSICAL_GAIA_ZTF_MATCHES_UNVERIFIED"
    return {
        "schema_version":"stellarforge-taurus-r3-six-fixed-original-oid-photometry-technical-qc-no-raw-v1",
        "phase":status,
        "r1_frozen_seed_sha256":R1_SEED_SHA,
        "r2_original_source_ledger_path":str(ORIGINAL_R2_PATH),
        "r2_original_24_source_identity_decision_path":str(ORIGINAL_R2_DECISION_PATH),
        "original_ztf_api_base":IRSA_URL,
        "public_original_collection":COLLECTION,
        "n_predeclared_exact_original_ztf_oids_requested":len(groups),
        "n_original_archive_csv_with_rows_and_valid_qc":success,
        "n_original_rows_seen_in_valid_exact_oid_csv":raw,
        "n_original_rows_locally_qc_accepted_in_valid_exact_oid_csv":clean,
        "n_qc_accepted_independent_oid_band_clock_technical_coverage_pass":passes,
        "technical_original_response_status_counts":dict(sorted(c.items())),
        "n_physically_authenticated_gaia_ztf_sources":0,
        "n_physically_eligible_R3_stellar_lightcurves":0,
        "n_original_ztf_oid_curves_merged":0,
        "n_new_astrophysical_variables_or_companions_confirmed":0,
        "r2_physical_source_identity_blocker_still_open":True,
        "r3_physical_star_variability_science_go":False,
        "original_raw_ztf_lightcurve_pixels_photometry_saved_to_disk":False,
        "original_source_filters_or_oids_selected_using_variability":False,
        "fixed_quality_and_eligibility_thresholds":{
            "bad_catflags_bitmask":QC_CATFLAGS_MASK,
            "min_good_epochs":MIN_QC_VISITS,
            "min_baseline_days":MIN_BASELINE_DAYS,
            "time_bins_days_from_first_accepted_visit":COVERAGE_BIN_DAYS,
            "uncorrected_clocks_kept_separate":True,
        },
        "source_observations":rows,
        "caveats":[
            "This is a real-data archive/ObjectID TECHNICAL COVERAGE audit, not Gaia-star photometry or independent physical Gaia-to-ZTF source authentication.",
            "Each of six ObjectIDs was selected before observing new R3 photometric rows, based on an original R2 source/ObjectID ledger, and never merged across fields or bands.",
            "Original R2 positional query row counts and new exact-ObjectID DR24 queries are not automatically identical due to different query kinds, provenance and collection.",
            "catflags & 32768 and the 30 visits/90 day threshold address only preliminary time-series technical sufficiency, not error covariance, crowded/blended sources, calibration or literature novelty.",
            "365-day bins are an instrument coverage diagnostic anchored to the first retained epoch in each distinct native time system; they are not calendrical observing seasons or periodicities.",
            "The 24 Gaia technical cohort remains nonrepresentative; the six original OIDs only cover two technical source-labels and cannot measure a regional incidence rate.",
            "No periodograms, star-related intrinsic variability measurements or astronomical discoveries are claimed, and no original photometric magnitude, per-exposure observation time or raw source image is saved.",
        ],
    }


def run_six_from_frozen_repo(root:Path, *, opener=urlopen)->dict:
    root=Path(root)
    original=json.loads((root/ORIGINAL_R2_PATH).read_text(encoding="utf8"))
    decision=json.loads((root/ORIGINAL_R2_DECISION_PATH).read_text(encoding="utf8"))
    return r3_six_original_oid_qc(original,decision,opener=opener)
