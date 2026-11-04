"""Audited and restartable ZTF 24-target pilot acquisition.

Default is offline planning. Network access is opt-in via --execute, conservative,
and intended for small-scale (<=100 targets) public IRSA ZTF light-curve calls.
Each target is a Luhman 2023 *coordinate seed*, NOT a confirmed ZTF match.
"""
from __future__ import annotations

from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from urllib.error import HTTPError, URLError

from .luhman2023 import validate_technical_seed, MIRROR_BLOB_SHA1
from .ztf import build_ztf_url, fetch_ztf_raw
from .ztf_photometry import audit_ztf_file


class CacheConflict(ValueError):
    """Stored raw response does not match its original request or recorded SHA."""


def load_seed(seed_path: Path) -> list[dict]:
    validate_technical_seed(seed_path)
    with Path(seed_path).open(newline="", encoding="utf-8-sig") as h:
        return list(csv.DictReader(h))


def target_request(row: dict, radius_arcsec: float) -> dict:
    """Construct traceable query without pretending to propagate the Gaia epoch."""
    sid = str(row["gaia"])
    if not sid.isdigit() or len(sid) > 19:
        raise ValueError("Invalid Gaia target identifier")
    ra, dec = float(row["ra"]), float(row["dec"])
    return {
        "gaia_dr3_source_id": sid,
        "source_name": row.get("name", ""),
        "kinematic_group": row["group"],
        "ra_catalog_deg": ra,
        "dec_catalog_deg": dec,
        "source_gaia_reference_epoch": "J2016.0 if Gaia; source catalog is heterogeneous",
        "source_position_reference": row["reference"],
        "proper_motion_mas_per_year_ra_star": row.get("pmra", ""),
        "proper_motion_mas_per_year_dec": row.get("pmdec", ""),
        "catalog_source_line": int(row["original_line"]),
        "radius_arcsec": radius_arcsec,
        "url": build_ztf_url(ra, dec, radius_arcsec=radius_arcsec,
                             bands=("g", "r"), bad_catflags_mask=32768, output_format="csv"),
        "astrometric_match_verified": False,
        "epoch_correction_applied": False,
        "catalog_match_requires_propagation_and_image_review": True,
    }


def validate_raw_cache(raw_file: Path, url: str) -> dict | None:
    """A cache without matching provenance is an error, never evidence."""
    metadata_file = Path(str(raw_file) + ".provenance.json")
    if not raw_file.exists() and not metadata_file.exists():
        return None
    if not raw_file.exists() or not metadata_file.exists():
        raise CacheConflict("Raw table or provenance missing from partial cache")
    try:
        metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise CacheConflict("Corrupt cached metadata") from exc
    raw = raw_file.read_bytes()
    if metadata.get("url") != url or metadata.get("sha256") != hashlib.sha256(raw).hexdigest():
        raise CacheConflict("Request URL or data SHA256 differs from cached provenance")
    return metadata


def download_one(query: dict, output_path: Path, *, fetcher=fetch_ztf_raw,
                 max_attempts: int = 3, delay_s: float = 1.0,
                 sleep=time.sleep) -> tuple[dict, str]:
    """Retry transient errors; do not retry 4xx except 429; no silent overwrite."""
    if not 1 <= max_attempts <= 5 or not 0 <= delay_s <= 30:
        raise ValueError("Unsafe retry configuration")
    previous = validate_raw_cache(output_path, query["url"])
    if previous is not None:
        return previous, "cached_verified"
    for attempt in range(max_attempts):
        try:
            meta = fetcher(query["url"], output_path, timeout_sec=50)
            if meta["sha256"] != hashlib.sha256(output_path.read_bytes()).hexdigest():
                raise CacheConflict("Fetcher returned incorrect data SHA")
            return meta, "downloaded"
        except CacheConflict:
            raise
        except HTTPError as exc:
            if exc.code != 429 and 400 <= exc.code < 500:
                raise
            if attempt == max_attempts - 1:
                raise
        except (TimeoutError, URLError, OSError):
            if attempt == max_attempts - 1:
                raise
        sleep(delay_s * 2**attempt)
    raise RuntimeError("unreachable retry state")


def run_batch(seed: Path, out_dir: Path, *, execute=False, radius_arcsec=2.0,
              max_targets=24, fetcher=fetch_ztf_raw, pause_between_s=0.5,
              sleep=time.sleep) -> dict:
    """Run small IRSA batch, per-target failures contained; atomic JSON ledger.

    A dry run creates only the query plan, no untrusted fake observations.
    Each target remains 'unverified_association' even when downloaded and QC'd.
    """
    if not isinstance(max_targets, int) or not 1 <= max_targets <= 100:
        raise ValueError("Allowed batch size is 1..100")
    if not 0 < radius_arcsec <= 10 or not 0 <= pause_between_s <= 30:
        raise ValueError("Invalid cone radius or polite-request delay")
    seed = Path(seed)
    rows = load_seed(seed)[:max_targets]
    result_dir = Path(out_dir)
    result_dir.mkdir(parents=True, exist_ok=True)
    source_hash = hashlib.sha256(seed.read_bytes()).hexdigest()
    manifest = {
        "version": "0.5", "plan_created_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "execute_online" if execute else "dry_run_no_requests",
        "catalog": "Luhman 2023 Taurus adopted members, pinned third-party mirror",
        "mirror_git_blob_sha1": MIRROR_BLOB_SHA1,
        "catalog_seed_sha256": source_hash,
        "publisher_byte_crosscheck_completed": False,
        "observational_discoveries": 0,
        "ztf_target_associations_confirmed": 0,
        "queries": [],
    }
    for i, row in enumerate(rows):
        query = target_request(row, radius_arcsec)
        entry = {**query, "status": "not_executed" if not execute else "queued"}
        if execute:
            path = result_dir / "raw" / f"{query['gaia_dr3_source_id']}_ztf.csv"
            path.parent.mkdir(parents=True, exist_ok=True)
            try:
                meta, from_status = download_one(query, path, fetcher=fetcher, sleep=sleep)
                entry["retrieval_status"] = from_status
                entry["response_sha256"] = meta["sha256"]
                entry["response_bytes"] = meta["bytes"]
                audit = audit_ztf_file(path, result_dir / "qc" / query["gaia_dr3_source_id"],
                                       target_ra=query["ra_catalog_deg"],
                                       target_dec=query["dec_catalog_deg"],
                                       radius_arcsec=radius_arcsec, min_good_epochs=30)
                entry["raw_rows"] = audit["raw_rows"]
                entry["qc_accepted_rows"] = audit["kept_rows"]
                entry["n_separate_ztf_curves"] = audit.get("curve_count", 0)
                entry["n_ambiguous_bands"] = len(audit.get("ambiguous_match_bands", []))
                entry["status"] = "no_ztf_observations" if not audit["raw_rows"] else "unverified_source_association"
            except CacheConflict as exc:
                entry["status"] = "cache_conflict_requires_manual_review"
                entry["error_class"] = type(exc).__name__
            except (HTTPError, URLError, TimeoutError, OSError, ValueError, UnicodeError, KeyError) as exc:
                entry["status"] = "download_or_qc_failed"
                entry["error_class"] = type(exc).__name__
                # Exclude potentially sensitive or gigantic URLs from generic error details.
            if i < len(rows) - 1:
                sleep(pause_between_s)
        manifest["queries"].append(entry)
    manifest["n_targets_in_batch"] = len(rows)
    manifest["counts"] = dict(sorted(Counter(x["status"] for x in manifest["queries"]).items()))
    destination = result_dir / "BATCH_MANIFEST.json"
    temp = destination.with_suffix(".json.partial")
    temp.write_text(json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    temp.replace(destination)
    return manifest