"""Run 24 *independent positional screens* against Gaia DR3 and IRSA ZTF.

This is not an authenticated physical counterpart crossmatch.
The original Gaia TAP and IRSA ZTF CSV responses are ephemeral.
Persist only public-source derived counts, OID labels and SHA receipts.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

from scripts.prepare_taurus_variability_r1 import (
    DEFAULT_SEED, prepare_technical_cohort,
)
from stellarforge.r2_counterpart_screen import (
    assess_r2_target, summarise_r2_screen,
)


def run(seed_bytes: bytes, *, assessor=assess_r2_target) -> dict:
    cohort = prepare_technical_cohort(seed_bytes)
    seed_rows = list(csv.DictReader(io.StringIO(
        seed_bytes.decode("utf-8-sig"))))
    if len(seed_rows) != 24 or cohort["n_preexisting_technical_candidates"] != 24:
        raise ValueError("R2 source cohort differs from frozen R1 technical seed")
    results = [assessor(row) for row in seed_rows]
    result = summarise_r2_screen(results, seed_sha256=hashlib.sha256(seed_bytes).hexdigest())
    result["research_study_id"] = cohort["study_id"]
    return result


def main():
    parser = argparse.ArgumentParser(
        description="R2 Gaia neighbour and IRSA ZTF OID positional-only screen; no physical crossmatch")
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--output", type=Path, default=Path(
        "reports/generated/taurus_r2_gaia_neighbours_ztf_oids_derived_only.json"))
    args = parser.parse_args()
    result = run(args.seed.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True,
                                      allow_nan=False)+"\n", encoding="utf-8")
    public = {k: v for k, v in result.items()
              if k.startswith("n_") or k in ("phase","full_R2_complete")}
    print(json.dumps(public, indent=2))
    print("Original survey responses remain ephemeral; saved derived report:", args.output)


if __name__ == "__main__":
    main()
