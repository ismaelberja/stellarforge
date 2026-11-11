"""Diagnose 22 archived IRSA source queries, keeping all original 24 targets.

Safe to rerun explicitly; the output is derived provider-status metadata
only. This program DOES perform bounded original public IRSA requests.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.prepare_taurus_variability_r1 import DEFAULT_SEED
from stellarforge.r2_irsa_failure_diagnosis import diagnose_frozen_24

DEFAULT_PLAN = Path("research/taurus_variability/R2_IRSA_DIAGNOSTIC_INPUT_NO_RAW.json")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="R2 actual IRSA transport/schema diagnosis; not a physical source match")
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--output", type=Path,
                        default=Path("reports/generated/taurus_r2_irsa_diagnostic_no_raw.json"))
    args = parser.parse_args()
    result = diagnose_frozen_24(
        args.seed.read_bytes(),
        json.loads(args.plan.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(
        result, indent=2, sort_keys=True, allow_nan=False)+"\n", encoding="utf-8")
    for k, v in result.items():
        if k.startswith("n_") or k == "phase" or k == "status_counts_per_attempt":
            print(k, ":", v)
    print("Derived evidence file:", args.output)
    print("Physical Gaia-ZTF matches: 0 (none established).")


if __name__ == "__main__":
    main()
