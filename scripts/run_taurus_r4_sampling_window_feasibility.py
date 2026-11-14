"""Offline observational ZTF 365-day sampling and SYNTHETIC cadence aliases.

Validates the immutable R2/R3 original-source science gates first; makes no
archive calls and writes no real individual observation times/magnitudes.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from scripts.audit_taurus_r3_six_original_source_receipts import (
    audit_r3_original_six_source_receipts, FIRST_PATH, RETRY_PATH,
)
from stellarforge.r4_sampling_window_feasibility import r4_technical_sampling_feasibility
from stellarforge.r4_sampling_visual import original_zft_r4_coverage_svg


def run_r4_from_repo(root:Path)->dict:
    root=Path(root)
    valid_r3=audit_r3_original_six_source_receipts(root)
    first=json.loads((root/FIRST_PATH).read_text(encoding="utf8"))
    retry=json.loads((root/RETRY_PATH).read_text(encoding="utf8"))
    return r4_technical_sampling_feasibility(first,retry,valid_r3)


def main()->None:
    p=argparse.ArgumentParser(description="Purely offline source-derived ZTF cadence constraints + explicitly synthetic alternative windows")
    p.add_argument("--root",type=Path,default=Path("."))
    p.add_argument("--json",type=Path,default=Path("reports/generated/taurus_r4_real_365day_bins_and_SYNTHETIC_window_no_raw.json"))
    p.add_argument("--svg",type=Path,default=Path("reports/generated/taurus_r4_real_365day_bins_only.svg"))
    args=p.parse_args()
    report=run_r4_from_repo(args.root)
    args.json.parent.mkdir(parents=True,exist_ok=True)
    args.svg.parent.mkdir(parents=True,exist_ok=True)
    args.json.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf8")
    args.svg.write_text(original_zft_r4_coverage_svg(report),encoding="utf8")
    print(json.dumps({
        "status":report["phase"],
        "original_real_ztf_OIDs_with_accepted_365day_bins":report["real_original_ztf_OIDs_with_QC_annual_bins"],
        "original_archive_timeouts_unknown_not_zero":report["original_ztf_OIDs_with_unavailable_server_responses"],
        "original_good_visits":report["n_original_ztf_accepted_epochs"],
        "source_technical_sampling_gaps_and_synthetic_examples":[{
            "oid":x["original_ztf_oid"],
            "cadence_observed":x["cadence_metric_computable"],
            "real_empty_365day_bins":x["n_empty_relative_365day_bins"],
            "SYNTHETIC_daily_1day_window":x.get("SYNTHETIC_daily_integer_grid_1day_window_power"),
            "SYNTHETIC_subday_1day_window":x.get("SYNTHETIC_subday_diverse_1day_window_power"),
        } for x in report["source_observations"]],
        "real_ztf_spectral_window_calculated":report["observed_frequency_window_calculated_from_original_visit_timestamps"],
        "physical_gaia_ztf_identifications":report["original_physical_Gaia_ZTF_identifications_confirmed"],
        "json_no_raw":str(args.json),
        "svg_original_aggregate_counts_only":str(args.svg),
    },indent=2))


if __name__=="__main__":
    main()
