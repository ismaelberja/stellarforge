"""R2 source archive recovery for ONLY the nine frozen unsuccessful ZTF positions."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.prepare_taurus_variability_r1 import DEFAULT_SEED
from stellarforge.r2_nine_source_recovery import recover_nine

OLD_REPORT=Path("reports/taurus_variability_r2/IRSA_22_ORIGINAL_DERIVED_DIAGNOSTIC_LEDGER.json")


def main():
    parser=argparse.ArgumentParser(
        description="Original IRSA nine-position source access, not a physical counterpart match")
    parser.add_argument("--seed",type=Path,default=DEFAULT_SEED)
    parser.add_argument("--previous",type=Path,default=OLD_REPORT)
    parser.add_argument("--output",type=Path,default=Path("reports/generated/taurus_r2_nine_final_recovery_no_raw.json"))
    args=parser.parse_args()
    result=recover_nine(
        args.seed.read_bytes(),
        json.loads(args.previous.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(
        result,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf8")
    for key,value in result.items():
        if key.startswith("n_") or key in ("phase","scientific_r2_complete","per_request_status_counts"):
            print(key,":",value)
    print("Original raw IRSA CSV not persisted. Derived ledger:",args.output)
    print("Physical Gaia/ZTF counterpart associations confirmed: zero")


if __name__=="__main__":
    main()
