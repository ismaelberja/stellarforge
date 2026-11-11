"""R2 live bounded Gaia DR3 exact-ID sweep for the frozen 24-object cohort.

Only derived public-source QA counts are output; original TAP CSV stays
ephemeral. A Gaia catalogue source is NOT a verified ZTF object/light curve.
This is intentionally a limited R2 Gaia-only subset, not complete R2.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path

from stellarforge.r2_gaia_identity import (
    BATCH, audit_exact_gaia_cohort, fetch_exact_gaia_ids,
)
from scripts.prepare_taurus_variability_r1 import (
    DEFAULT_SEED, prepare_technical_cohort,
)


def run(seed_bytes: bytes, *, fetcher=fetch_exact_gaia_ids) -> dict:
    prereg = prepare_technical_cohort(seed_bytes)
    if prereg["n_preexisting_technical_candidates"] != 24:
        raise ValueError("R1 cohort was not frozen")
    reader = csv.DictReader(io.StringIO(seed_bytes.decode("utf8-sig")))
    rows = list(reader)
    ids = [str(r["gaia"]).strip() for r in rows]
    original = [fetcher(tuple(ids[i:i+BATCH]))
                for i in range(0, len(ids), BATCH)]
    report = audit_exact_gaia_cohort(rows, original)
    report["r1_seed_data_sha256"] = prereg["seed_data_sha256"]
    return report


def main():
    parser = argparse.ArgumentParser(
        description="R2 bounded exact Gaia DR3 24-source no-raw study, not a ZTF source identification")
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--output", type=Path, default=Path("reports/generated/r2_gaia_only_exact_id_audit.json"))
    args = parser.parse_args()
    result = run(args.seed.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True,
                                      allow_nan=False)+"\n", encoding="utf-8")
    print("R2 Gaia DR3 LIVE exact-ID results, not Gaia/ZTF crossmatches:")
    print(json.dumps({
        "status": result["phase"],
        "n_r1_technical_candidates": result["n_r1_technical_candidates"],
        "n_gaia_dr3_exact_ids_returned": result["n_gaia_dr3_exact_ids_returned"],
        "n_gaia_dr3_exact_ids_missing": result["n_gaia_dr3_exact_ids_missing"],
        "n_gaia_preliminary_quality_flags": result["n_gaia_preliminary_quality_flags"],
        "n_gaia_ruwe_at_least_1p4": result["n_gaia_ruwe_at_least_1p4"],
        "n_confirmed_gaia_ztf_physical_associations": 0,
        "r1_seed_data_sha256": result["r1_seed_data_sha256"],
    }, indent=2))
    print(f"Public-source derived-only report: {args.output}")


if __name__ == "__main__":
    main()
