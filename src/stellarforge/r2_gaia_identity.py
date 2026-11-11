"""Taurus R2: bounded exact-ID Gaia DR3 astrometric *catalogue* audit.

Original source IDs come exclusively from frozen R1 technical cohort.
Only real Gaia DR3 exact source-ID catalogue matches can be counted.
A matching Gaia catalogue entry (even isolated, low RUWE, good parallax)
is NEVER proof of physical identity with any ZTF ObjectID or of youth.

Raw TAP CSV is ephemeral, not written to Git. A no-raw derived ledger
still includes public Gaia IDs for traceability. Survey images and
Gaia-neighbour completeness are deliberately outside this phase.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .coordinates import angular_separation_arcsec, validate_icrs

TAP_URL = "https://gaia.ari.uni-heidelberg.de/tap/sync"
COLUMNS = ("source_id", "ref_epoch", "ra", "dec", "pmra", "pmdec",
           "parallax", "ruwe", "duplicated_source",
           "astrometric_params_solved", "phot_g_mean_mag")
BATCH = 12
MAX_BYTES = 250_000


def exact_id_adql(ids: tuple[str, ...]) -> str:
    """No arbitrary Gaia cone scan, only 1–12 fixed DR3 source IDs."""
    if not 1 <= len(ids) <= BATCH or len(set(ids)) != len(ids):
        raise ValueError("Gaia exact-ID batch must be unique and contain 1..12 IDs")
    if any(not isinstance(s, str) or not s.isascii() or
           not s.isdigit() or not 15 <= len(s) <= 20 for s in ids):
        raise ValueError("Invalid Gaia DR3 source ID")
    return (f"SELECT {', '.join(COLUMNS)} FROM gaiadr3.gaia_source "
            f"WHERE source_id IN ({', '.join(ids)})")


def fetch_exact_gaia_ids(ids: tuple[str, ...], *,
                         timeout_sec: float = 30.0, opener=urlopen) -> bytes:
    adql = exact_id_adql(ids)
    if not math.isfinite(timeout_sec) or not 5 <= timeout_sec <= 90:
        raise ValueError("Invalid TAP budget")
    form = urlencode({"REQUEST": "doQuery", "LANG": "ADQL",
                      "FORMAT": "csv", "QUERY": adql}).encode("ascii")
    req = Request(TAP_URL, data=form,
                  headers={"Content-Type": "application/x-www-form-urlencoded",
                           "User-Agent": "StellarForge/2.0 R2 original DR3 exact-IDs"},
                  method="POST")
    with opener(req, timeout=timeout_sec) as response:
        payload = response.read(MAX_BYTES + 1)
    if not payload or len(payload) > MAX_BYTES:
        raise ValueError("Gaia TAP exact-ID response empty/oversize")
    return payload


def _finite_or_none(raw: str | None) -> float | None:
    if raw is None or str(raw).strip().lower() in ("", "null", "nan", "--"):
        return None
    v = float(raw)
    if not math.isfinite(v):
        raise ValueError("Gaia catalogue contains non-finite scientific value")
    return v


def parse_exact_gaia_ids(payload: bytes, expected: tuple[str, ...]) -> dict[str, dict]:
    """Reject malformed/irrelevant data; absence of an ID is an explicit row gap."""
    if not isinstance(payload, bytes) or len(payload) > MAX_BYTES:
        raise ValueError("Bad Gaia CSV payload")
    text = payload.decode("utf-8-sig")
    if text.lstrip().startswith(("<", "{")):
        raise ValueError("Gaia endpoint returned HTML/XML/JSON, not CSV")
    lines = [line for line in text.splitlines()
             if line.strip() and not line.lstrip().startswith("#")]
    reader = csv.DictReader(io.StringIO("\n".join(lines)))
    if (not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames)
            or not set(COLUMNS).issubset(reader.fieldnames)):
        raise ValueError("Gaia TAP exact-ID CSV schema mismatch")
    observed = {}
    for row in reader:
        if None in row or any(row.get(k) is None for k in COLUMNS):
            raise ValueError("Broken Gaia CSV row")
        sid = row["source_id"].strip()
        if sid not in expected or sid in observed:
            raise ValueError("Unexpected or duplicated Gaia source ID returned")
        position = (_finite_or_none(row["ra"]), _finite_or_none(row["dec"]))
        if any(v is None for v in position):
            raise ValueError("Gaia position not available for exact ID")
        validate_icrs(*position)
        epoch = _finite_or_none(row["ref_epoch"])
        if epoch is None or abs(epoch - 2016.0) > 1.e-4:
            raise ValueError("Unexpected Gaia DR3 reference epoch")
        flag = row["duplicated_source"].strip().lower()
        if flag not in ("true","false","t","f","1","0"):
            raise ValueError("Unknown Gaia duplicated_source flag")
        try:
            solved = int(row["astrometric_params_solved"])
        except (ValueError, TypeError) as exc:
            raise ValueError("Malformed Gaia astrometric solution flag") from exc
        observed[sid] = {
            "ra": position[0], "dec": position[1], "ref_epoch": epoch,
            "pmra": _finite_or_none(row["pmra"]),
            "pmdec": _finite_or_none(row["pmdec"]),
            "parallax": _finite_or_none(row["parallax"]),
            "ruwe": _finite_or_none(row["ruwe"]),
            "phot_g_mean_mag": _finite_or_none(row["phot_g_mean_mag"]),
            "duplicated_source": flag in ("true", "t", "1"),
            "astrometric_params_solved": solved,
        }
    return observed


def audit_exact_gaia_cohort(seed_rows: list[dict], responses: list[bytes]) -> dict:
    """Derive a transparent *Gaia-only* status for every predeclared target.

    Independent image/PSF/crowding and original ZTF OID checks remain pending.
    Position discrepancy is descriptive, not independently calibrated.
    """
    if len(seed_rows) != 24 or len(responses) != 2:
        raise ValueError("The complete R1 24-source cohort and two batches are mandatory")
    ids = [str(r["gaia"]).strip() for r in seed_rows]
    if len(set(ids)) != 24:
        raise ValueError("Duplicate Gaia IDs in R1 cohort")
    parts = [tuple(ids[i:i+BATCH]) for i in range(0, len(ids), BATCH)]
    query_hashes = [hashlib.sha256(exact_id_adql(p).encode()).hexdigest() for p in parts]
    raw_hashes = [hashlib.sha256(raw).hexdigest() for raw in responses]
    matches = {}
    for ids_batch, raw in zip(parts, responses):
        entries = parse_exact_gaia_ids(raw, ids_batch)
        if any(s in matches for s in entries):
            raise ValueError("Repeated Gaia ID across TAP responses")
        matches.update(entries)
    results = []
    for row in seed_rows:
        sid = str(row["gaia"]).strip()
        original_ra = float(row["ra"])
        original_dec = float(row["dec"])
        validate_icrs(original_ra, original_dec)
        m = matches.get(sid)
        if m is None:
            results.append({
                "gaia_dr3_source_id": sid,
                "gaia_exact_source_status": "NOT_RETURNED_BY_GAIA_TAP",
                "gaia_ruwe": None,
                "gaia_catalogue_position_to_seed_arcsec": None,
                "gaia_astrometry_preliminary_quality_flag": False,
                "gaia_ztf_physical_source_identity": "NOT_VERIFIED",
                "gaia_neighbour_crowding": "NOT_CHECKED",
                "ztf_oid_association": "NOT_CHECKED",
                "eligible_for_r3_physical_variability_analysis": False,
            })
            continue
        sep = angular_separation_arcsec(original_ra, original_dec,
                                        m["ra"], m["dec"])
        # A practical review gate, NOT instrument calibration or a physical
        # crossmatch. Discrepancy may reflect seed epoch/model differences.
        quality = (
            m["astrometric_params_solved"] in (31, 95)
            and m["pmra"] is not None and m["pmdec"] is not None
            and m["ruwe"] is not None and m["ruwe"] < 1.4
            and not m["duplicated_source"]
            and sep < 1.0
        )
        results.append({
            "gaia_dr3_source_id": sid,
            "gaia_exact_source_status": "EXACT_DR3_SOURCE_RETURNED",
            "gaia_ruwe": round(m["ruwe"], 5) if m["ruwe"] is not None else None,
            "gaia_catalogue_position_to_seed_arcsec": round(sep, 5),
            "gaia_astrometry_preliminary_quality_flag": bool(quality),
            "gaia_astrometric_params_solved": m["astrometric_params_solved"],
            "gaia_duplicated_source": m["duplicated_source"],
            "gaia_ztf_physical_source_identity": "NOT_VERIFIED",
            "gaia_neighbour_crowding": "NOT_CHECKED",
            "ztf_oid_association": "NOT_CHECKED",
            "eligible_for_r3_physical_variability_analysis": False,
        })
    return {
        "phase": "TAURUS_R2_GAIA_DR3_ONLY__ZTF_PHYSICAL_ASSOCIATION_PENDING",
        "source": "gaiadr3.gaia_source via Gaia@ARI TAP / exact predeclared IDs",
        "n_r1_technical_candidates": 24,
        "gaia_exact_id_query_sha256": query_hashes,
        "gaia_raw_response_sha256_no_raw_committed": raw_hashes,
        "n_gaia_dr3_exact_ids_returned": len(matches),
        "n_gaia_dr3_exact_ids_missing": 24-len(matches),
        "n_gaia_preliminary_quality_flags": sum(
            s["gaia_astrometry_preliminary_quality_flag"] for s in results),
        "n_gaia_ruwe_at_least_1p4": sum(
            s["gaia_ruwe"] is not None and s["gaia_ruwe"] >= 1.4 for s in results),
        "n_confirmed_gaia_ztf_physical_associations": 0,
        "n_independently_vetted_taurus_memberships": 0,
        "n_confirmed_new_ztf_variable_stars": 0,
        "n_original_ztf_image_crowding_reviews_in_r2": 0,
        "publisher_original_source_rows_independently_crosschecked": False,
        "full_r2_independent_source_identification_completed": False,
        "results": results,
        "limitations": [
            "Exact Gaia DR3 source IDs establish catalogue records, not genuine ZTF OID crossmatches.",
            "Gaia RUWE, duplicate flags and a J2016 catalogue position do not prove physical youth, isolation, source singleness or PSF purity.",
            "One-arcsec source-to-secondary-mirror reference comparison is descriptive, not calibrated astrometry.",
            "Original ZTF images, masks, PSFcat source identities, neighbours, and actual light curves were not fetched in this Gaia-only query.",
            "R3 photometry cannot be classified scientifically before independent source identity and crowding review.",
        ],
    }


def offline_declaration(seed_rows: list[dict]) -> dict:
    """A placeholder is never returned as a successful Gaia lookup."""
    if len(seed_rows) != 24:
        raise ValueError("Expected complete seed")
    return {
        "phase": "R2_NO_GAIA_NETWORK_ATTEMPT__ALL_SOURCE_IDENTITIES_PENDING",
        "n_r1_technical_candidates": 24,
        "n_confirmed_gaia_ztf_physical_associations": 0,
        "is_original_gaia_data": False,
    }
