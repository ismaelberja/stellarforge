"""Normalize and audit an independently curated young-star membership table.

The input is a *researcher-verified transcription* of a published catalogue.
This module never infers youth or member status from position, brightness or Gaia.
No paper-level membership counts are inferred from a synthetic fixture.
"""
from __future__ import annotations

from collections import Counter
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Iterable

from .coordinates import validate_icrs

REQUIRED_COLUMNS = (
    "target_id", "ra_deg", "dec_deg", "coord_epoch_jyear",
    "membership_status", "reference_id",
)
OPTIONAL_COLUMNS = (
    "gaia_dr3_source_id", "pmra_masyr", "pmdec_masyr",
    "g_mag", "group_name", "disk_class", "coordinate_origin", "notes",
)
ALLOWED_STATUS = {"adopted", "candidate", "rejected", "uncertain"}
ALLOWED_DISK = {"I", "II", "III", "transition", "evolved", "unknown"}
_MAX_GAIA = 2**63 - 1


@dataclass(frozen=True)
class Member:
    target_id: str
    ra_deg: float
    dec_deg: float
    coord_epoch_jyear: float
    membership_status: str
    reference_id: str
    gaia_dr3_source_id: str | None = None
    pmra_masyr: float | None = None
    pmdec_masyr: float | None = None
    g_mag: float | None = None
    group_name: str | None = None
    disk_class: str = "unknown"
    coordinate_origin: str | None = None
    notes: str | None = None

    @property
    def has_gaia_id(self) -> bool:
        return self.gaia_dr3_source_id is not None

    @property
    def has_pm(self) -> bool:
        return self.pmra_masyr is not None and self.pmdec_masyr is not None


def _optional_num(s: str | None, name: str) -> float | None:
    if s is None or not s.strip():
        return None
    try:
        n = float(s)
    except ValueError as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not math.isfinite(n):
        raise ValueError(f"{name} must be finite")
    return n


def _gaia_id(s: str | None) -> str | None:
    if s is None or not s.strip():
        return None
    value = s.strip()
    if not re.fullmatch(r"[1-9][0-9]{0,18}", value) or int(value) > _MAX_GAIA:
        raise ValueError("Gaia DR3 source ID must be an unsigned decimal string < 2^63")
    return value  # Never convert to floating point: 64-bit identifiers lose precision.


def _parse(row: dict[str, str]) -> Member:
    def string(key: str) -> str:
        return (row.get(key) or "").strip()
    target = string("target_id")
    reference = string("reference_id")
    status = string("membership_status").lower()
    if not target or not reference:
        raise ValueError("target_id and reference_id cannot be empty")
    if status not in ALLOWED_STATUS:
        raise ValueError(f"Invalid membership_status: {status!r}")
    ra = _optional_num(string("ra_deg"), "ra_deg")
    dec = _optional_num(string("dec_deg"), "dec_deg")
    epoch = _optional_num(string("coord_epoch_jyear"), "coord_epoch_jyear")
    if ra is None or dec is None or epoch is None:
        raise ValueError("Position and coordinate reference epoch are mandatory")
    validate_icrs(ra, dec)
    if not 1900 <= epoch <= 2100:
        raise ValueError("coord_epoch_jyear must be in [1900, 2100]")
    pmra = _optional_num(string("pmra_masyr"), "pmra_masyr")
    pmdec = _optional_num(string("pmdec_masyr"), "pmdec_masyr")
    g = _optional_num(string("g_mag"), "g_mag")
    if g is not None and not -5 <= g <= 35:
        raise ValueError("g_mag is outside physically plausible catalog range")
    disk = string("disk_class") or "unknown"
    if disk not in ALLOWED_DISK:
        raise ValueError(f"Invalid disk_class: {disk!r}; do not guess from colors")
    return Member(
        target_id=target, ra_deg=ra, dec_deg=dec, coord_epoch_jyear=epoch,
        membership_status=status, reference_id=reference,
        gaia_dr3_source_id=_gaia_id(string("gaia_dr3_source_id")),
        pmra_masyr=pmra, pmdec_masyr=pmdec, g_mag=g,
        group_name=string("group_name") or None, disk_class=disk,
        coordinate_origin=string("coordinate_origin") or None,
        notes=string("notes") or None,
    )


def read_membership(path: Path) -> list[Member]:
    """Load researcher-curated CSV; fail loudly on ambiguous or malformed records."""
    path = Path(path)
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        header = reader.fieldnames or []
        if len(header) != len(set(header)):
            raise ValueError("Duplicate CSV header names")
        missing = set(REQUIRED_COLUMNS) - set(header)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")
        entries = []
        seen: set[str] = set()
        for lineno, row in enumerate(reader, start=2):
            try:
                if None in row:
                    raise ValueError("Extra CSV fields; wrong delimiter or broken quoting")
                member = _parse(row)
                if member.target_id in seen:
                    raise ValueError(f"Duplicate target_id {member.target_id!r}")
            except ValueError as exc:
                raise ValueError(f"{path.name}:{lineno}: {exc}") from exc
            seen.add(member.target_id)
            entries.append(member)
    return entries


def audit_members(members: Iterable[Member], *,
                  expected_literature_members: int = 532) -> dict:
    """Compare observed input to literature expectations without claiming completeness."""
    xs = list(members)
    adopted = [m for m in xs if m.membership_status == "adopted"]
    has_gaia = [m for m in adopted if m.has_gaia_id]
    duplicate_gaia_ids = [id_ for id_, n in Counter(
        m.gaia_dr3_source_id for m in has_gaia
    ).items() if n > 1]
    return {
        "input_rows": len(xs),
        "adopted_member_rows": len(adopted),
        "published_adopted_member_count": expected_literature_members,
        "matches_published_count": len(adopted) == expected_literature_members,
        "adopted_gaia_id_present": len(has_gaia),
        "adopted_gaia_id_missing": len(adopted) - len(has_gaia),
        "published_gaia_dr3_entries": 467,
        "gaia_count_matches_paper": len(has_gaia) == 467 if len(adopted) == 532 else None,
        "adopted_pm_both_available": sum(m.has_pm for m in adopted),
        "adopted_g_mag_available": sum(m.g_mag is not None for m in adopted),
        "adopted_disk_class_counts": dict(sorted(Counter(m.disk_class for m in adopted).items())),
        "adopted_group_counts": dict(sorted(Counter(m.group_name or "unclassified" for m in adopted).items())),
        "duplicate_gaia_ids": sorted(duplicate_gaia_ids),
        "notes": [
            "532 and 467 are literature numbers, not counts measured in StellarForge.",
            "A Gaia ID missing from a Taurus member is not evidence of non-membership.",
            "Gaia ID count agreement is necessary but not sufficient to validate catalog identity.",
            "Gaia IDs must be checked against Luhman (2023) Table 2, not inferred by cone search.",
        ],
    }


def write_audit(path: Path, members: list[Member], *, reference_url: str,
                output: Path, expected_count: int = 532) -> dict:
    if not reference_url.startswith("https://"):
        raise ValueError("Reference URL must be a cited HTTPS source")
    raw = Path(path).read_bytes()
    result = audit_members(members, expected_literature_members=expected_count)
    result["provenance"] = {
        "source_url": reference_url,
        "original_filename": Path(path).name,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "retrieved_or_processed_utc": datetime.now(timezone.utc).isoformat(),
        "review_status": "requires_scientific_verification",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result