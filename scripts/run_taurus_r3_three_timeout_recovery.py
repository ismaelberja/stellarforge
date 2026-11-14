"""Bounded second attempt for exact three original DR24 R3 provider timeouts.

Result is derived-only; original CSV and photometric samples are not saved.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from stellarforge.r3_three_timeout_recovery import run_recovery_from_repo

def main()->None:
    p=argparse.ArgumentParser(description="Second serial attempt only for original R3 three 40-second exact-ZTF-OID timeouts")
    p.add_argument("--root",type=Path,default=Path("."))
    p.add_argument("--output",type=Path,default=Path("reports/generated/taurus_r3_three_original_dr24_timeout_recovery_no_raw.json"))
    args=p.parse_args()
    result=run_recovery_from_repo(args.root)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf8")
    print(json.dumps({
        "phase":result["phase"],
        "retried_frozen_original_ztf_oids":result["n_predeclared_original_timeout_oids_requeried"],
        "original_ztf_DR24_source_recovered":result["n_retrieved_valid_original_ztf_dr24_oids"],
        "technical_30visit_90day_pass":result["n_technical_30visit_90day_pass_oid_band_clock_series"],
        "per_oid_outcomes":[(x["ztf_oid"],x["original_retry_status"]) for x in result["original_retry_source_results"]],
        "physical_gaia_ztf_counterparts_authenticated":result["n_new_original_gaia_to_ztf_physical_counterparts_confirmed"],
        "raw_original_csv_saved":False,
        "result_derived_only_path":str(args.output)
    },indent=2))

if __name__=="__main__":
    main()
