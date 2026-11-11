"""Predeclare a *technical*, source-identity-unverified Taurus cohort.

R1 study setup only: no survey access, no physical Gaia/ZTF crossmatch,
no variability classification or results. All original 24 previously
selected technical seed rows are retained *before* inspecting variability.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path

DEFAULT_SEED = Path("data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv")
STUDY_ID = "stellarforge-taurus-variability-r1"
REQUIRED_FIELDS = {"gaia", "ra", "dec", "gmag", "pmra", "pmdec",
                   "reference", "group", "original_line"}
EXPECTED_SEED_ROWS = 24


def prepare_technical_cohort(payload: bytes) -> dict:
    """Generate deterministic *unverified* candidate IDs from a frozen seed.

    The labels 'technical' and 'pending identity check' are intentional:
    a positional ZTF query alone cannot authenticate a Gaia source.
    """
    if not isinstance(payload, bytes) or not (100 < len(payload) < 100_000):
        raise ValueError("Missing or implausible technical seed CSV")
    try:
        text = payload.decode("utf-8-sig")
        table = csv.DictReader(io.StringIO(text, newline=""))
        fields = table.fieldnames
        if not fields or not REQUIRED_FIELDS.issubset(fields) or len(fields) != len(set(fields)):
            raise ValueError("Missing or duplicate technical seed columns")
        rows = list(table)
    except (UnicodeDecodeError, csv.Error) as exc:
        raise ValueError("Cannot parse technical seed CSV") from exc
    if len(rows) != EXPECTED_SEED_ROWS:
        raise ValueError("Technical cohort must retain all 24 previously chosen rows")
    ids = set()
    selected = []
    for row in rows:
        if None in row:
            raise ValueError("Unexpected extra CSV cells")
        sid = str(row["gaia"]).strip()
        if not sid.isascii() or not sid.isdigit() or not 1 <= len(sid) <= 19:
            raise ValueError("Invalid Gaia ID in technical seed")
        if sid in ids:
            raise ValueError("Duplicate Gaia ID; cannot double-count stars")
        ids.add(sid)
        if row["reference"].strip() != "Gaia":
            raise ValueError("Unreviewed non-Gaia coordinate source")
        try:
            ra, dec, g, pmra, pmdec = (
                float(row[k]) for k in ("ra", "dec", "gmag", "pmra", "pmdec"))
            original_line = int(row["original_line"])
        except (ValueError, TypeError) as exc:
            raise ValueError("Malformed technical seed photometry/coordinates") from exc
        if (not all(math.isfinite(v) for v in (ra, dec, g, pmra, pmdec))
                or not (0 <= ra < 360 and -90 <= dec <= 90)
                or not (12 <= g <= 17) or original_line < 1):
            raise ValueError("Technical seed row violates source screening contract")
        selected.append({
            "gaia_dr3_source_id": sid,
            "technical_seed_original_line": original_line,
            "technical_group": str(row["group"]).strip(),
            "catalogue_counterpart_authenticated": False,
            "ztf_physical_source_identity_verified": False,
            "eligible_for_physical_variability_claim": False,
        })
    selected.sort(key=lambda r: r["gaia_dr3_source_id"])
    return {
        "study_id": STUDY_ID,
        "phase": "R1_PRE_REGISTERED_TECHNICAL_COHORT",
        "seed_data_sha256": hashlib.sha256(payload).hexdigest(),
        "seed_description": "24-source pre-existing nonrepresentative Taurus technical pilot from secondary Luhman (2023) mirror",
        "n_preexisting_technical_candidates": len(selected),
        "source_selection_conditioned_on_ztf_variability_results": False,
        "representative_region_population": False,
        "publisher_original_catalogue_checked": False,
        "all_gaia_ztf_physical_source_associations_authenticated": False,
        "study_sample_scientifically_approved": False,
        "new_astrophysical_variable_stars_confirmed": 0,
        "next_decision": "Independently verify literature membership, Gaia-to-ZTF identity, crowding, epoch/filter/quality and reference controls before unblinding variability results",
        "technical_candidates": selected,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare Taurus variability R1 technical pre-registration; no network and no scientific source validation")
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--output", type=Path, default=Path("reports/generated/taurus_variability_r1_predeclared.json"))
    args = parser.parse_args()
    result = prepare_technical_cohort(args.seed.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"{result['phase']}: {result['n_preexisting_technical_candidates']} "
          "historical candidate Gaia IDs; 0 physical source identities authenticated")
    print(f"Manifest: {args.output}")


if __name__ == "__main__":
    main()
