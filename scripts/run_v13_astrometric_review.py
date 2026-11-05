"""Reproduce v1.3 provisional Gaia/ZTF positional evidence from a local ZIP.

Input: a downloaded GitHub Actions artifact of actual official IRSA responses.
Output: JSON/Markdown summaries only, no raw CSV committed or uploaded.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from stellarforge.v13_observational_review import (
    review_irsa_artifact, write_provisional_review,
)

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv"


def main() -> None:
    parser = argparse.ArgumentParser(description="Provisional epoch-aware Gaia/ZTF review")
    parser.add_argument("artifact_zip", type=Path, help="Locally downloaded private IRSA artifact ZIP")
    parser.add_argument("--seed", type=Path, default=SEED)
    parser.add_argument("--output", type=Path, default=ROOT / "reports/generated/v1.3_astrometry")
    args = parser.parse_args()
    report = review_irsa_artifact(args.artifact_zip, args.seed)
    paths = write_provisional_review(report, args.output)
    print(json.dumps({
        "targets": report["n_targets"],
        "rows": report["n_rows"],
        "curves": report["n_curves"],
        "verified_crossmatches": report["gaia_ztf_identity_confirmations"],
        "outputs": [str(p) for p in paths],
    }, indent=2))


if __name__ == "__main__":
    main()
