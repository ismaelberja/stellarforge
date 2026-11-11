"""Live original Gaia-selected field-control offset audit, no raw data in git."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.prepare_taurus_variability_r1 import DEFAULT_SEED
from stellarforge.r2_gaia_heldout_native_offsets import run_original_field_controls

PREVIOUS = Path("data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json")

def main():
    p=argparse.ArgumentParser(
        description="Differential original Gaia/PSFcat controls for historic FT Tau/CIDA11 dates; no physical crossmatch")
    p.add_argument("--seed",type=Path,default=DEFAULT_SEED)
    p.add_argument("--historical-ledger",type=Path,default=PREVIOUS)
    p.add_argument("--output",type=Path,default=Path(
        "reports/generated/taurus_r2_real_gaia_only_control_offsets_no_raw.json"))
    a=p.parse_args()
    result=run_original_field_controls(
        a.seed.read_bytes(),json.loads(a.historical_ledger.read_text(encoding="utf8")))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n",
                        encoding="utf8")
    for k,v in result.items():
        if k.startswith("n_") or k in ("phase","scientific_R2_complete"):
            print(k,":",v)
    for frame in result["frames"]:
        summary=frame.get("control_offset_summary",{})
        print(json.dumps({
            "name":frame["original_target"],
            "mjd":frame["original_science_mjd"],
            "status":frame["status"],
            "control_stratum":summary.get("source_control_stratum"),
            "n_accepted_strict_controls":summary.get(
                "n_strict_gaia_controls_with_acceptable_native_psf_and_gaia_quality"),
            "field_gate_passed":summary.get("min_three_strict_controls_gate_passed"),
            "target_gate_passed":summary.get(
                "target_original_native_psf_and_gaia_quality_gate_passed"),
            "n_provisional_physical_gaia_ztf_matches":0,
        },sort_keys=True))
    print("No raw Gaia or original ZTF PSF catalogue rows persisted:",a.output)

if __name__=="__main__":
    main()
