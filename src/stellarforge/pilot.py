"""Construct a provisional, explicitly non-approved Taurus pilot roster.

The balanced cohort is a *design proposal*, not a claim of a validated sample.
Source selection never uses measured variability from Gaia or ZTF.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict
import hashlib
import json
from pathlib import Path

from .catalog import Member


PILOT_QUOTAS = {"II": 12, "III": 12}


def _balance_group(records: list[Member], quantity: int) -> list[Member]:
    """Round-robin across published kinematic groups; stable within each group."""
    by_group: dict[str, list[Member]] = defaultdict(list)
    for item in records:
        by_group[item.group_name or "unclassified"].append(item)
    for group in by_group:
        by_group[group].sort(key=lambda m: (hashlib.sha256(m.target_id.encode()).hexdigest(), m.target_id))
    groups = sorted(by_group, key=lambda g: (-len(by_group[g]), g))
    selection: list[Member] = []
    while len(selection) < quantity:
        made_progress = False
        for group in groups:
            if by_group[group] and len(selection) < quantity:
                selection.append(by_group[group].pop(0))
                made_progress = True
        if not made_progress:
            break
    return selection


def propose_pilot(members: list[Member], *,
                  quotas: dict[str, int] | None = None,
                  catalog_verified: bool = False) -> dict:
    """Return explicit decisions, exclusions and proposal-only target IDs.

    `catalog_verified` must be supplied by a scientist after original-table
    verification; this function cannot certify a catalog on its own.
    """
    quotas = dict(PILOT_QUOTAS if quotas is None else quotas)
    if not quotas or any(k not in {"II", "III"} or not isinstance(v, int) or v < 1
                         for k, v in quotas.items()):
        raise ValueError("Pilot quotas must be positive integer II/III counts")
    eligible = [m for m in members
                if m.membership_status == "adopted" and m.has_gaia_id
                and m.g_mag is not None and m.group_name is not None]
    reasons = {
        "not_adopted": sum(m.membership_status != "adopted" for m in members),
        "adopted_without_gaia_id": sum(m.membership_status == "adopted" and not m.has_gaia_id for m in members),
        "adopted_with_gaia_id_missing_g_mag": sum(m.membership_status == "adopted" and m.has_gaia_id and m.g_mag is None for m in members),
        "adopted_with_gaia_and_g_mag_missing_group": sum(m.membership_status == "adopted" and m.has_gaia_id and m.g_mag is not None and m.group_name is None for m in members),
        "eligible_unknown_or_other_disk_class": sum(m.disk_class not in quotas for m in eligible),
    }
    available = Counter(m.disk_class for m in eligible)
    sufficient = all(available.get(cls, 0) >= n for cls, n in quotas.items())
    selected = []
    if sufficient:
        for disk, n in sorted(quotas.items()):
            selected.extend(_balance_group([m for m in eligible if m.disk_class == disk], n))
        selected.sort(key=lambda x: (x.disk_class, x.group_name or "", x.target_id))
    blockers = []
    if not catalog_verified:
        blockers.append("Original membership catalogue not independently verified by research lead")
    if not sufficient:
        blockers.append("Insufficient scientifically labelled eligible sources for prespecified quotas")
    return {
        "status": "proposed_pending_scientific_review" if selected else "blocked_insufficient_verified_labels",
        "may_start_observational_ingestion": bool(catalog_verified and sufficient),
        "original_catalog_reviewed_by_scientist": catalog_verified,
        "quotas_by_disk_class": quotas,
        "eligible_by_disk_class": dict(sorted(available.items())),
        "excluded_before_balancing": reasons,
        "blockers": blockers,
        "selection_made_without_variability_measurements": True,
        "selection_method": "Deterministic SHA256 within publication kinematic groups; balanced round-robin per disk class",
        "caveat": "Only a pilot; 24 targets cannot establish a population-level prevalence of dippers or bursters.",
        "targets": [asdict(m) for m in selected],
    }


def write_pilot(output: Path, proposal: dict) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(proposal, indent=2, sort_keys=True) + "\n", encoding="utf-8")