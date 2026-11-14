"""One bounded original ZTF DR24 technical coverage audit of six frozen R2 OIDs.

No original CSV, per-epoch photometry or source pixels are persisted.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from stellarforge.r3_original_oid_coverage import run_six_from_frozen_repo

def main()->None:
    p=argparse.ArgumentParser(description="Real ZTF original DR24 exact-six-ObjectID photometric technical QC, not physical source association")
    p.add_argument("--root",type=Path,default=Path("."))
    p.add_argument("--output",type=Path,default=Path("reports/generated/taurus_r3_six_original_oid_technical_qc_no_raw.json"))
    args=p.parse_args()
    result=run_six_from_frozen_repo(args.root)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf8")
    print(json.dumps({
        "phase":result["phase"],
        "original_ztf_fixed_objectids":result["n_predeclared_exact_original_ztf_oids_requested"],
        "valid_original_dr24_exact_oid_source_tables":result["n_original_archive_csv_with_rows_and_valid_qc"],
        "technical_30visit_90day_accepted_series":result["n_qc_accepted_independent_oid_band_clock_technical_coverage_pass"],
        "individual_source_request_outcomes":[(r["ztf_oid"],r["original_archive_query_status"]) for r in result["source_observations"]],
        "original_gaia_to_ztf_physical_star_matches":result["n_physically_authenticated_gaia_ztf_sources"],
        "r3_astrophysical_time_series_inference_allowed":result["r3_physical_star_variability_science_go"],
        "permanent_original_ztf_raw_photometry_saved":False,
        "derived_only_result_path":str(args.output),
    },indent=2))

if __name__=="__main__":
    main()
