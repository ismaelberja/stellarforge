"""Run exactly two Taurus historical ZTF OID-vs-positional archive checks.

Original Gaia and ZTF CSV responses only live in process memory.
Writes derived public-source catalogue identity *ambiguity* evidence.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.prepare_taurus_variability_r1 import DEFAULT_SEED
from stellarforge.r2_ztf_oid_multiplicity import review_two_original_fields

HISTORICAL=Path("data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json")

def main():
    p=argparse.ArgumentParser(description="Taurus R2 original two Gaia target/old ZTF OID comparison; NO physical source match")
    p.add_argument("--seed",type=Path,default=DEFAULT_SEED)
    p.add_argument("--historical",type=Path,default=HISTORICAL)
    p.add_argument("--output",type=Path,default=Path(
        "reports/generated/taurus_r2_original_ztf_alternative_oid_derived.json"))
    args=p.parse_args()
    report=review_two_original_fields(
        args.seed.read_bytes(),json.loads(args.historical.read_text(encoding="utf8")))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(
        report,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf8")
    for key,value in report.items():
        if key.startswith("n_") or key in ("phase","source_identity_science_R2_completed"):
            print(key,":",value)
    for f in report["fields"]:
        pos=f["positional_oid_screen"]
        hist=f["historic_oid_direct_screen"]
        print(json.dumps({
            "field":f["target"],"pos_status":pos["status"],
            "historical_direct_oid_status":hist["status"],
            "hist_oid_in_2arcsec":f["historic_oid_present_in_2arcsec_positional_query"],
            "distinct_original_ztf_oids":pos.get("n_original_distinct_ztf_oids"),
            "oid_band_groups":pos.get("n_original_oid_band_groups"),
            "same_band_oid_pairs":pos.get("n_original_oid_pairs_in_same_band"),
            "same_exposure_metadata_oid_pairs":pos.get(
                "n_same_band_oid_pairs_sharing_exact_original_exposure_metadata"),
            "historical_direct_oid_original_rows":hist.get("n_original_oid_rows"),
            "independent_gaia_ztf_physical_source_match":False,
        },sort_keys=True))
    print("No raw ZTF light curves, per-epoch magnitudes, survey pixels or Gaia original data saved.")
    print("Derived survey ObjectID ambiguity evidence:",args.output)

if __name__=="__main__":
    main()
