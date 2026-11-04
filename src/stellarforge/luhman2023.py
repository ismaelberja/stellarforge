"""Read the machine-readable Luhman (2023) Taurus adopted-member table.

Metadata from the publisher's machine-readable Table 2 is mirrored at a
third-party pinned public GitHub commit. The mirror has 532 Taurus-member
rows, of which 467 have Gaia DR3 IDs. SHA-1 below is a Git *blob* checksum,
not a claim that the third-party copy has been byte-compared to the publisher.

References:
Luhman K. L. 2023, AJ, 165, 37, DOI:10.3847/1538-3881/ac9da3.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
from pathlib import Path
from urllib.request import Request, urlopen

MIRROR_COMMIT = "7b6a5c83eca81fc66e50cb4889ee35cb28861367"
MIRROR_BLOB_SHA1 = "fe0d5a43dbd2ca8b867901686ab223a847c649e5"
MIRROR_URL = ("https://raw.githubusercontent.com/themariavincent/get_targets/"
              + MIRROR_COMMIT + "/taurus_sources.txt")
RESEARCH_DOI = "10.3847/1538-3881/ac9da3"
MRT_FILENAME = "ajac9da3t2_mrt.txt"
EXPECTED_ROWS = 532
EXPECTED_GAIA_DR3 = 467


class CatalogValidationError(ValueError):
    """Explicit failure for untrusted or incomplete author-table copies."""


def git_blob_sha1(raw: bytes) -> str:
    prefix = f"blob {len(raw)}\0".encode("ascii")
    return hashlib.sha1(prefix + raw).hexdigest()


def _slice(row: str, start: int, end: int) -> str:
    """Read 1-indexed inclusive byte fields from official MRT description."""
    return row[start - 1:end].strip()


def parse_membership_mrt(raw: bytes, *, enforce_reference_counts: bool = True) -> dict:
    """Preserve 64-bit Gaia IDs as strings; inspect 360-column MRT table."""
    try:
        source = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise CatalogValidationError("Table is not UTF-8 text") from exc
    header = source[:1500]
    if "Adopted Members of Taurus" not in header or MRT_FILENAME not in header:
        raise CatalogValidationError("Wrong table: expected Luhman 2023 adopted members MRT")
    rows = []
    for lineno, line in enumerate(source.splitlines(), 1):
        if len(line) < 360:
            continue
        ra_raw = _slice(line, 83, 91)
        dec_raw = _slice(line, 93, 101)
        try:
            ra = float(ra_raw); dec = float(dec_raw)
        except ValueError:
            continue
        if not math.isfinite(ra) or not math.isfinite(dec) or not 0 <= ra < 360 or not -90 <= dec <= 90:
            raise CatalogValidationError(f"Invalid sky position on line {lineno}")
        source_id = _slice(line, 1, 19)
        if source_id and (not source_id.isdigit() or len(source_id) > 19):
            raise CatalogValidationError(f"Bad Gaia DR3 identifier on line {lineno}")
        gmag_raw = _slice(line, 297, 302)
        gmag = float(gmag_raw) if gmag_raw else None
        ref = _slice(line, 103, 109)
        row = {
            "gaia_dr3_source_id": source_id or None,
            "two_mass_id": _slice(line, 21, 37) or None,
            "other_name": _slice(line, 59, 81) or None,
            "ra_deg": ra,
            "dec_deg": dec,
            "position_reference": ref or None,
            "adopted_spectral_type": _slice(line, 169, 173) or None,
            "gmag": gmag,
            "pmra_mas_per_year": (float(_slice(line, 175, 180))
                                    if _slice(line, 175, 180) else None),
            "pmdec_mas_per_year": (float(_slice(line, 188, 194))
                                     if _slice(line, 188, 194) else None),
            "kinematic_group": _slice(line, 345, 360) or None,
            "source_line": lineno,
        }
        rows.append(row)
    if not rows:
        raise CatalogValidationError("No fixed-width Taurus rows detected")
    ids = [x["gaia_dr3_source_id"] for x in rows if x["gaia_dr3_source_id"]]
    if len(ids) != len(set(ids)):
        raise CatalogValidationError("Duplicate Gaia DR3 source IDs")
    if enforce_reference_counts and (len(rows), len(ids)) != (EXPECTED_ROWS, EXPECTED_GAIA_DR3):
        raise CatalogValidationError("Unexpected population: found " + str((len(rows), len(ids)))
                                     + "; expected (532, 467). Wrong release or truncated source?")
    return {
        "catalog_name": "Luhman 2023 Taurus adopted members — Table 2",
        "doi": RESEARCH_DOI,
        "record_count": len(rows),
        "with_gaia_dr3_source_id": len(ids),
        "without_gaia_dr3_source_id": len(rows) - len(ids),
        "distinct_named_kinematic_groups": len({x["kinematic_group"] for x in rows if x["kinematic_group"]}),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "source_git_blob_sha1": git_blob_sha1(raw),
        "members": rows,
    }


def download_pinned_mirror(output_path: Path, *, timeout_seconds: float = 50) -> dict:
    """Fetch immutable GitHub mirror and require exact pinned Git blob checksum."""
    req = Request(MIRROR_URL, headers={"User-Agent": "StellarForge-research/0.4"})
    with urlopen(req, timeout=timeout_seconds) as response:
        raw = response.read(600_000)
    if len(raw) >= 600_000:
        raise CatalogValidationError("Unexpected oversized catalog response")
    if git_blob_sha1(raw) != MIRROR_BLOB_SHA1:
        raise CatalogValidationError("Pinned GitHub mirror content checksum mismatch")
    result = parse_membership_mrt(raw)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(raw)
    audit = {key: value for key, value in result.items() if key != "members"}
    audit.update({
        "retrieval_url": MIRROR_URL,
        "mirror_commit": MIRROR_COMMIT,
        "mirror_verified_against_publisher_bytes": False,
        "original_publisher_table_crosscheck_pending": True,
    })
    Path(str(out) + ".provenance.json").write_text(json.dumps(audit, indent=2) + "\n")
    return audit


def validate_technical_seed(path: Path) -> dict:
    """Validate the provisionally extracted 24-member *coordinate* seed.

    This is NOT the prespecified Class II/Class III scientific sample.
    """
    with Path(path).open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or not {"gaia", "ra", "dec", "group", "original_line", "gmag"} <= set(reader.fieldnames):
            raise CatalogValidationError("Missing required seed columns")
        rows = list(reader)
    if len(rows) != 24:
        raise CatalogValidationError(f"Technical seed must have 24 members, got {len(rows)}")
    ids = [row["gaia"] for row in rows]
    if any(not i.isdigit() for i in ids) or len(set(ids)) != len(ids):
        raise CatalogValidationError("Duplicate or invalid Gaia IDs in seed")
    groups = {row["group"] for row in rows}
    if len(groups) != 13:
        raise CatalogValidationError(f"Seed must cover 13 named Taurus groups, got {len(groups)}")
    for row in rows:
        ra, dec, gmag = float(row["ra"]), float(row["dec"]), float(row["gmag"])
        if not (0 <= ra < 360 and -90 <= dec <= 90 and 12 <= gmag <= 17):
            raise CatalogValidationError("Invalid seed sky position or G magnitude")
        if not 160 <= int(row["original_line"]) <= 700:
            raise CatalogValidationError("Unexpected original catalog line index")
    return {"status": "technical_seed_only", "rows": len(rows), "named_groups": len(groups),
            "gaia_present": len(ids), "disk_class_strata_verified": False,
            "scientific_pilot_frozen": False,
            "source_mirror_git_blob": MIRROR_BLOB_SHA1,
            "original_publisher_crosscheck_pending": True}


def audit_seed_against_full_mrt(mrt_raw: bytes, seed: Path) -> dict:
    """Explicit byte-source comparison for the 24 positions when mirror reachable."""
    full = parse_membership_mrt(mrt_raw)
    seed_status = validate_technical_seed(seed)
    by_id = {r["gaia_dr3_source_id"]:r for r in full["members"] if r["gaia_dr3_source_id"]}
    with Path(seed).open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            src = by_id.get(row["gaia"])
            if src is None or (int(row["original_line"]) != src["source_line"]
                               or abs(float(row["ra"]) - src["ra_deg"]) > 5e-7
                               or abs(float(row["dec"]) - src["dec_deg"]) > 5e-7):
                raise CatalogValidationError("Technical seed differs from pinned source MRT")
    return {**seed_status, "seed_positions_crosschecked_against_full_mirror": True}