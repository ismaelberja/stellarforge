"""Taurus R2: original IRSA ZTF ObjectID/field/filter ambiguity review.

Exactly two pre-existing *historic* target fields, FT Tau and CIDA 11,
within the unchanged 24-member Taurus technical Gaia cohort. For each
field issue one original 2-arcsec POS query (NOBS_MIN=5) and one exact
historical ZTF ObjectID query (no after-the-fact OID selection).

IRSA ZTF ObjectIDs are *survey labels*, not unique physical stellar IDs
across every field/CCD/quadrant/filter; never merge OIDs by sky proximity.
An overlap in reported sky position, date range, detector metadata or
even exposure IDs DOES NOT prove an individual Gaia star's identity.

All original IRSA light-curve rows and Gaia responses stay ephemeral.
Persist derived per-OID/filter/field and ambiguity summaries only.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import itertools
import math
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .r2_original_fits_gates import validate_historic_exposures
from .r2_counterpart_screen import (
    fetch_ztf_positional, screen_ztf_angular_oids, ZTF_RADIUS_ARCSEC,
)
from .v19_gaia_covariance import fetch_gaia_astrometry, parse_gaia_astrometry
from .ztf_photometry import BANDS, inspect_ztf_bytes, parse_ztf_table

IRSA_URL = "https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves"
MAX_DIRECT_BYTES = 4_000_000
MAX_GROUPS = 30
MAX_RAW_ROWS = 45_000
TARGETS = (
    ("FT Tau", "149623711269425408", "1605115300003377"),
    ("CIDA 11", "3419110734340795648", "610106300008010"),
)
ERRORS = (HTTPError, URLError, TimeoutError, OSError, ValueError,
          TypeError, OverflowError, UnicodeError)

def validate_fixed_two_targets(seed_bytes: bytes, ledger: dict) -> list[dict]:
    """Never select target fields, IDs or dates using observed light curves."""
    original, frames = validate_historic_exposures(seed_bytes, ledger)
    selected = []
    for name, gaia_id, historical_oid in TARGETS:
        row = original.get(gaia_id)
        if row is None or row["name"] != name:
            raise ValueError("Historic target is no longer in the unchanged R1 cohort")
        historic = [x for x in frames if x["target"] == name]
        if (len(historic) != 2 or
                any(x["target_gaia_id"] != gaia_id or
                    x["oid"] != historical_oid or x["band"] != "zg"
                    for x in historic)):
            raise ValueError("The pre-existing historical ZTF ObjectID has changed")
        selected.append({"target": name, "gaia_id": gaia_id,
                         "historical_ztf_oid": historical_oid,
                         "ra": float(row["ra"]), "dec": float(row["dec"]),
                         "historical_mjds": sorted(float(x["mjd"]) for x in historic)})
    return selected


def historic_oid_url(oid: str) -> str:
    """Exactly one fixed known ZTF ObjectID, not a source discovery query."""
    if not isinstance(oid, str) or not oid.isascii() or not oid.isdigit() or not 10 <= len(oid) <= 19:
        raise ValueError("Invalid historic ZTF object identifier")
    return IRSA_URL + "?" + urlencode({"ID": oid, "FORMAT": "csv"})


def fetch_historic_oid(oid: str, *, timeout_sec: float = 35.0,
                       opener=urlopen) -> bytes:
    if not math.isfinite(timeout_sec) or not 5 <= timeout_sec <= 45:
        raise ValueError("Original ZTF ObjectID request timeout unbounded")
    request = Request(
        historic_oid_url(oid), method="GET",
        headers={"User-Agent": "StellarForge/2.0 Taurus R2 fixed historical ZTF OID audit",
                 "Accept": "text/csv,text/plain"})
    with opener(request, timeout=timeout_sec) as response:
        payload = response.read(MAX_DIRECT_BYTES + 1)
    if not payload or len(payload) > MAX_DIRECT_BYTES:
        raise ValueError("Original exact-ObjectID response empty or oversized")
    if payload.lstrip().startswith((b"<", b"{", b"[")):
        raise ValueError("Original exact-ObjectID response is not CSV")
    return payload


def _meta_exposure_key(row: dict, band: str) -> tuple[str, ...] | None:
    """Exact original survey CCD/exposure metadata, not a physical star ID."""
    keys = ("filefracday", "field", "ccdid", "qid")
    parts = tuple(str(row.get(k) or "").strip() for k in keys)
    if any(not x for x in parts):
        return None
    return (*parts, band)


def _row_band(row: dict) -> str | None:
    raw = str(row.get("filtercode") or row.get("fid") or row.get("filterid") or "").lower()
    return BANDS.get(raw)


def _row_oid(row: dict) -> str:
    oid = str(row.get("oid") or "").strip()
    if not oid.isascii() or not oid.isdigit() or not oid:
        raise ValueError("Malformed original survey ObjectID")
    return oid


def characterize_original_ztf_oids(raw: bytes, *, gaia_target: dict | None) -> dict:
    """Group original positional survey rows and identify ambiguous OID sets.

    No original magnitude/flux, time series or pixel data in output.
    Source-centred sky positions, if present, are just ZTF catalogue
    position proxies and compared using approximate Gaia proper motion.
    """
    if not isinstance(raw, bytes) or not raw or len(raw) > 4_000_000:
        raise ValueError("Original ZTF positional response invalid or oversized")
    records, fmt = parse_ztf_table(raw)
    if fmt != "csv" or not records or len(records) > MAX_RAW_ROWS:
        raise ValueError("Original source rows not a populated bounded CSV")
    audit, points = inspect_ztf_bytes(raw, min_good_epochs=1)
    screen = screen_ztf_angular_oids(raw, gaia_target)
    screens = {(x["ztf_oid"], x["ztf_band"], x["original_time_type"]): x
               for x in screen["candidates"]}
    groups: dict[tuple[str, str], dict] = {}
    for row in records:
        oid = _row_oid(row)
        band = _row_band(row)
        if band is None:
            raise ValueError("Unrecognized ZTF filter band in original metadata")
        key = (oid, band)
        if key not in groups:
            groups[key] = {"oid": oid, "band": band,
                           "n_original_raw_table_rows": 0,
                           "native_field_ccd_quadrant_labels": set(),
                           "exposure_keys": set(), "n_rows_missing_exposure_metadata": 0}
        g = groups[key]
        g["n_original_raw_table_rows"] += 1
        loc = tuple(str(row.get(k) or "").strip() for k in ("field", "ccdid", "qid"))
        if all(loc):
            g["native_field_ccd_quadrant_labels"].add("/".join(loc))
        ekey = _meta_exposure_key(row, band)
        if ekey is not None:
            g["exposure_keys"].add(ekey)
        else:
            g["n_rows_missing_exposure_metadata"] += 1
    if len(groups) > MAX_GROUPS:
        raise ValueError("Too many source ObjectID/filter groups in fixed 2-arcsec query")

    good = Counter((p.oid, p.band) for p in points)
    out = []
    for (oid, band), g in sorted(groups.items()):
        position_screens = [x for (soid, sband, _), x in screens.items()
                            if soid == oid and sband == band]
        if len(position_screens) > 1:
            # Do not silently combine distinct time-system conventions.
            pos_status = "MULTIPLE_UNMIXED_TIME_SYSTEMS"
            median_sep = None
        elif len(position_screens) == 1:
            pos_status = position_screens[0]["position_screen"]
            median_sep = position_screens[0]["separation_gaia_vs_survey_catalogue_median_arcsec"]
        else:
            pos_status = "NO_QUALITY_ACCEPTED_EPOCHS"
            median_sep = None
        out.append({
            "ztf_oid": oid, "band": band,
            "n_original_raw_table_rows": g["n_original_raw_table_rows"],
            "n_quality_accepted_epoch_rows": good[(oid, band)],
            "n_unique_original_field_ccd_quadrant_combinations": len(
                g["native_field_ccd_quadrant_labels"]),
            "original_field_ccd_quadrant_labels": sorted(
                g["native_field_ccd_quadrant_labels"])[:16],
            "n_original_rows_with_incomplete_exposure_metadata":
                g["n_rows_missing_exposure_metadata"],
            "n_distinct_metadata_identified_survey_exposures":
                len(g["exposure_keys"]),
            "positional_proximity_screen": pos_status,
            "median_original_survey_pos_vs_approx_Gaia_arcsec": median_sep,
            "gaia_ztf_physical_identity_confirmed": False,
        })
    # Same-band different-ObjectID overlap: stronger evidence of technical
    # ambiguity than angular proximity, but NOT proof of two physical stars.
    pairs = []
    for band in sorted({k[1] for k in groups}):
        selected = [(key, g) for key, g in sorted(groups.items())
                    if key[1] == band]
        for (key_a, a), (key_b, b) in itertools.combinations(selected, 2):
            common = a["exposure_keys"] & b["exposure_keys"]
            pairs.append({
                "band":band,
                "first_ztf_oid":key_a[0],
                "second_ztf_oid":key_b[0],
                "n_shared_identical_original_exposure_metadata_keys": len(common),
                "both_oids_same_band":"AMBIGUOUS_SOURCE_ASSOCIATION_NOT_MERGEABLE",
                "same_physical_star_established":False,
                "different_physical_stars_established":False,
            })
    return {
        "status":"ORIGINAL_ZTF_2ARCSEC_OID_FIELD_METADATA_PARSED",
        "original_irsa_raw_sha256_not_saved":hashlib.sha256(raw).hexdigest(),
        "n_original_positional_table_rows":len(records),
        "n_quality_accepted_photometric_rows":audit["kept_rows"],
        "n_original_distinct_ztf_oids":len({oid for oid, band in groups}),
        "n_original_oid_band_groups":len(out),
        "n_original_oid_pairs_in_same_band":len(pairs),
        "n_same_band_oid_pairs_sharing_exact_original_exposure_metadata":sum(
            x["n_shared_identical_original_exposure_metadata_keys"] > 0
            for x in pairs),
        "n_ztf_oid_bands_with_missing_exposure_metadata":sum(
            x["n_original_rows_with_incomplete_exposure_metadata"] > 0
            for x in out),
        "original_ztf_oid_band_groups":out,
        "same_band_multiple_oid_review_pairs":pairs,
        "all_source_identities_physical_unconfirmed":True,
        "all_oid_curves_kept_separate":True,
        "raw_photometric_rows_persisted":False,
    }


def characterize_exact_original_oid(raw: bytes, *, expected_oid: str) -> dict:
    if not isinstance(raw, bytes) or not raw or len(raw) > MAX_DIRECT_BYTES:
        raise ValueError("Bad exact historic object response")
    rows, fmt = parse_ztf_table(raw)
    if fmt != "csv":
        raise ValueError("Historic ObjectID response not CSV")
    if any(_row_oid(x) != expected_oid for x in rows):
        raise ValueError("Direct historic OID response returned unrelated ObjectID")
    return {
        "status":"ORIGINAL_HISTORIC_OID_DIRECT_IRSA_QUERY_PARSED",
        "historical_original_ztf_oid":expected_oid,
        "n_original_oid_rows":len(rows),
        "n_historic_oid_bands":len({b for x in rows if (b := _row_band(x))}),
        "historical_oid_bands":sorted({b for x in rows if (b := _row_band(x))}),
        "original_historic_direct_raw_sha256_no_rows_committed":hashlib.sha256(raw).hexdigest(),
        "historical_oid_is_physical_gaia_counterpart_verified":False,
    }


def review_two_original_fields(seed: bytes, historic_ledger: dict, *,
                               gaia_fetch=fetch_gaia_astrometry,
                               pos_fetch=fetch_ztf_positional,
                               oid_fetch=fetch_historic_oid) -> dict:
    targets = validate_fixed_two_targets(seed, historic_ledger)
    ids = tuple(t["gaia_id"] for t in targets)
    gaia = {}
    original_gaia_sha = None
    try:
        raw_gaia = gaia_fetch(ids, timeout_sec=35)
        original_gaia_sha = hashlib.sha256(raw_gaia).hexdigest()
        gaia = parse_gaia_astrometry(raw_gaia, expected_ids=ids)
    except ERRORS:
        # Still audit IRSA source labels, but never invent a position comparison.
        gaia = {}
    result=[]
    for t in targets:
        field = {
            "target":t["target"],"gaia_dr3_id":t["gaia_id"],
            "historic_original_ztf_oid":t["historical_ztf_oid"],
            "historic_original_image_mjds":t["historical_mjds"],
            "gaia_original_source_available":t["gaia_id"] in gaia,
            "original_gaia_ztf_physical_identity_confirmed":False,
            "scientific_variability_confirmed":False,
            "positional_oid_screen":{"status":"NOT_QUERIED"},
            "historic_oid_direct_screen":{"status":"NOT_QUERIED"},
        }
        try:
            raw = pos_fetch(t["ra"],t["dec"],radius_arcsec=ZTF_RADIUS_ARCSEC,
                            timeout_sec=35)
            field["positional_oid_screen"] = characterize_original_ztf_oids(
                raw,gaia_target=gaia.get(t["gaia_id"]))
        except ERRORS as exc:
            state={"status":"IRSA_POS_OR_PARSE_FAILED",
                   "error_type":type(exc).__name__}
            if isinstance(exc,HTTPError):state["http_status"]=int(exc.code)
            field["positional_oid_screen"]=state
        try:
            raw = oid_fetch(t["historical_ztf_oid"],timeout_sec=35)
            field["historic_oid_direct_screen"]=characterize_exact_original_oid(
                raw,expected_oid=t["historical_ztf_oid"])
        except ERRORS as exc:
            state={"status":"IRSA_EXACT_OID_OR_PARSE_FAILED",
                   "error_type":type(exc).__name__}
            if isinstance(exc,HTTPError):state["http_status"]=int(exc.code)
            field["historic_oid_direct_screen"]=state
        s=field["positional_oid_screen"]
        field["historic_oid_present_in_2arcsec_positional_query"]=(
            any(x["ztf_oid"]==t["historical_ztf_oid"]
                for x in s.get("original_ztf_oid_band_groups",[]))
            if s["status"]=="ORIGINAL_ZTF_2ARCSEC_OID_FIELD_METADATA_PARSED"
            else None)
        result.append(field)
    npos=sum(x["positional_oid_screen"]["status"]==
             "ORIGINAL_ZTF_2ARCSEC_OID_FIELD_METADATA_PARSED" for x in result)
    nhist=sum(x["historic_oid_direct_screen"]["status"]==
              "ORIGINAL_HISTORIC_OID_DIRECT_IRSA_QUERY_PARSED" for x in result)
    return {
        "phase":"TAURUS_R2_REAL_ZTF_ALTERNATE_OBJECTID_FILTER_FIELD_SCREEN_NOT_PHYSICAL_IDENTITY",
        "n_frozen_nonrepresentative_taurus_gaia_sources":24,
        "n_fixed_historic_target_fields":2,
        "n_historic_ztf_science_epochs_added":0,
        "n_new_original_ztf_science_fits_or_mask_products_fetched":0,
        "n_positional_irsa_2arcsec_queries_parsed":npos,
        "n_direct_original_historic_oid_queries_parsed":nhist,
        "n_fields_with_multiple_original_ztf_oids_same_band":sum(
            x["positional_oid_screen"].get("n_original_oid_pairs_in_same_band",0)>0
            for x in result),
        "n_fields_with_historic_oid_in_positional_response":sum(
            x["historic_oid_present_in_2arcsec_positional_query"] is True
            for x in result),
        "n_original_ztf_oid_groups_reviewed":sum(
            x["positional_oid_screen"].get("n_original_oid_band_groups",0)
            for x in result),
        "n_physical_gaia_to_ztf_object_identifications_confirmed":0,
        "n_confirmed_new_ztf_stellar_variables_or_companions":0,
        "source_identity_science_R2_completed":False,
        "original_gaia_dr3_exact_two_id_response_sha256":original_gaia_sha,
        "original_r1_seed_sha256":hashlib.sha256(seed).hexdigest(),
        "fields":result,
        "limitations":[
            "A 2-arcsec sky query is not a unique physical counterpart crossmatch.",
            "Distinct OIDs even within one band can be different pipeline field/CCD/quadrant labels, blended stars or artifacts. Never merge their curves by proximity alone.",
            "Original survey catalogue sky positions are based on ZTF's own WCS. Gaia approximate proper-motion screen omits full parallax and instrument covariance; not independent physical identity proof.",
            "No original ZTF pixel deblending or external imaging/catalogue crossmatch is performed in this source-label exercise.",
            "Original four FT Tau/CIDA 11 FITS+mask epochs were audited previously; no new astronomical science epochs are added.",
            "No original literature Taurus memberships or new intrinsic stellar variability discovered.",
        ],
    }
