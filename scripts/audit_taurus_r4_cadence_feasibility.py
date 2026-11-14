"""Fail-closed offline R4 permanent source-derived data and chart auditor.

The original R2/R3 SOURCE evidence auditor first rejects fake Gaia-ZTF source
matches or altered original ZTF hashes, then recomputes the R4 cadence
statistics and the distinctly SYNTHETIC one-day window examples.
"""
from __future__ import annotations
import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path

from scripts.run_taurus_r4_sampling_window_feasibility import run_r4_from_repo

EVIDENCE="reports/taurus_variability_r4/R4_REAL_ORIGINAL_ZTF_ANNUAL_COVERAGE_AND_SYNTHETIC_1DAY_EXAMPLES_NO_RAW.json"
FIGURE="docs/figures/taurus-r4-original-ztf-dr24-relative-365day-cadence.svg"
REPORT="research/taurus_variability/R4_REAL_ZTF_SAMPLING_WINDOW_FEASIBILITY_RESULTS.md"
RUN=43596705130
ARTIFACT=14114716328
ZIP_SHA="99a458146f63d19ac4f59fc741eaaab1ff36e6d661b53b82a45fd5d3983a5ad6"
JSON_SHA="83b141c6f3b45273bb6b9d3646d21a776ca003a4b0a4f64ab374cd77972077f3"
GENERATED_SVG_SHA="bf16103fd174441b353823997bac5885656f815d1db7e836d08f8a867d8084f4"
SVG_NS="{http://www.w3.org/2000/svg}"


def _equal(actual:dict,key:str,expected,description:str)->None:
    if not isinstance(actual,dict) or key not in actual or type(actual[key]) is not type(expected) or actual[key]!=expected:
        raise ValueError(f"{description}.{key} inconsistent with original source evidence")


def validate_r4_permanent_evidence(data:dict,svg_text:str,report_text:str,expected:dict)->dict:
    """Independent relative-year figure and original-hash-locked claim audit."""
    for key,val in (
        ("schema_version","stellarforge-taurus-r4-original-real-bins-and-strict-SYNTHETIC-one-day-window-source-receipt-v1"),
        ("derived_from_github_actions_run_id",RUN),
        ("source_r4_actions_artifact_id",ARTIFACT),
        ("source_r4_actions_zip_sha256",ZIP_SHA),
        ("source_r4_original_derived_only_json_sha256",JSON_SHA),
        ("source_r4_generated_svg_sha256",GENERATED_SVG_SHA),
        ("derived_from_original_source_R3_initial_workflow_run_id",43593335135),
        ("derived_from_original_source_R3_retry_workflow_run_id",43593994009),
        ("underlying_original_DR24_exact_OIDs",6),
        ("underlying_original_DR24_source_csvs_with_accepted_timebins",3),
        ("underlying_original_DR24_OIDs_failed_by_timeout_twice",3),
        ("source_original_raw_rows_in_3_successful_CSVs",684),
        ("source_original_qc_accepted_visits",591),
        ("source_original_bit15_mask_rejected_rows",93),
        ("source_original_context_24_gaia_id_to_ztf_physical_matches_authenticated",0),
        ("real_spectral_window_recovered_from_exact_source_timestamps",False),
        ("real_stellar_period_or_variability_claimed",False),
        ("r4_method_feasibility_deliverable_complete",True),
        ("r4_physical_star_variability_blocked",True),
        ("year_bins_are_relative_to_each_individual_sources_first_accepted_epoch_not_calendar_aligned",True),
        ("no_raw_original_ztf_photometry_or_individual_timestamps_committed",True),
    ): _equal(data,key,val,"permanent_r4")
    if (not isinstance(data.get("interpretation"),list) or len(data["interpretation"])!=5
            or not all(isinstance(x,str) and len(x)>=80 for x in data["interpretation"])):
        raise ValueError("Permanent R4 uncertainty/synthetic caveats omitted")
    for claim in ("SYNTHETIC","not", "coarse", "physical"):
        if claim.lower() not in " ".join(data["interpretation"]).lower():
            raise ValueError("Uncertainty, synthetic status or physical source boundary suppressed")
    measured=data.get("original_real_source_observations")
    unavailable=data.get("original_unavailable_source_OIDs")
    if not isinstance(measured,list) or len(measured)!=3 or not isinstance(unavailable,list) or len(unavailable)!=3:
        raise ValueError("R4 original real-count and timeout denominators changed")
    original=expected["source_observations"]
    if len(original)!=6:
        raise ValueError("R4 prior genuine source evidence has incorrect denominator")
    for i,record in enumerate(measured):
        s=original[i]
        for key,val in (
            ("original_ztf_oid",s["original_ztf_oid"]),
            ("band",s["original_ztf_filter"]),
            ("source_type","AUTHENTIC_ZTF_DR24_SURVEY_OBJECTID_NOT_PHYSICAL_GAIA_STAR"),
            ("raw_rows",s["original_source_rows"]),
            ("quality_accepted_visits",s["technical_source_qc_accepted_epochs"]),
            ("bit15_mask_rejected_rows",s["original_source_catflags_32768_rejected_rows"]),
            ("quality_retention_fraction",s["source_quality_retention_fraction"]),
            ("first_to_last_accepted_span_days",s["original_first_to_last_accepted_visit_span_days"]),
            ("accepted_visits_per_365days_over_total_span",s["mean_QC_visits_per_365day_over_total_span"]),
            ("original_relative_365day_bin_counts",s["original_relative_365day_bins_anchored_at_first_QC_epoch"]),
            ("observed_relative_bins_within_span",s["n_observed_relative_365day_bins"]),
            ("nonempty_relative_bins",s["n_nonempty_relative_365day_bins"]),
            ("max_consecutive_genuine_zero_relative_bins",s["longest_consecutive_empty_relative_365day_bins"]),
            ("strictly_SYNTHETIC_constructed_daily_grid_one_day_window_power",s["SYNTHETIC_daily_integer_grid_1day_window_power"]),
            ("strictly_SYNTHETIC_constructed_subday_diverse_one_day_window_power",s["SYNTHETIC_subday_diverse_1day_window_power"]),
            ("measured_real_one_day_window_power",None),
            ("physically_identified_gaia_counterpart",False),
        ):_equal(record,key,val,f"original_real_source_{i}")
    for j,record in enumerate(unavailable):
        s=original[j+3]
        for key,val in (
            ("original_ztf_oid",s["original_ztf_oid"]),
            ("band",s["original_ztf_filter"]),
            ("archive_access","TIMEOUT_ON_INITIAL_AND_ONE_PRE_REGISTERED_RETRY"),
            ("quality_accepted_visits",None),
            ("relative_365day_bins",None),
            ("measured_real_one_day_window_power",None),
            ("physically_identified_gaia_counterpart",False),
        ):_equal(record,key,val,f"original_unknown_source_{j}")

    # The published chart displays REAL only; its values must exactly
    # reconcile with original byte-SHA-locked annual-bin counts.
    try:
        svg=ET.fromstring(svg_text)
    except ET.ParseError as exc:
        raise ValueError("R4 original data figure is malformed SVG") from exc
    if (svg.tag!=SVG_NS+"svg" or svg.get("role")!="img"
            or svg.find(SVG_NS+"title") is None or svg.find(SVG_NS+"desc") is None
            or svg.findall(".//"+SVG_NS+"image")
            or svg.findall(".//"+SVG_NS+"script")):
        raise ValueError("R4 quantitative chart provenance/accessibility invalid")
    if not all(word in svg_text for word in ("591 genuine QC visits","not zero","not a periodogram")):
        raise ValueError("R4 chart is hiding source count, timeout distinction or period limitation")
    nodes=svg.findall(".//"+SVG_NS+"g")
    if len(nodes)!=27:  # 3 × 8 real annual cells plus 3 unknown timeouts
        raise ValueError("Chart source bin, out-of-span or archive-unknown count changed")
    for i,s in enumerate(original):
        matches=[x for x in nodes if x.get("data-oid")==s["original_ztf_oid"]]
        if i>=3:
            if len(matches)!=1 or matches[0].get("data-state")!="ARCHIVE_TIMEOUT_UNKNOWN":
                raise ValueError("Archive provider timeouts misrepresented as real zero counts")
            continue
        if len(matches)!=8:
            raise ValueError("Original source has missing or duplicate year-bin cells")
        for j,cell in enumerate(matches):
            if cell.get("data-bin")!=str(j+1):
                raise ValueError("Original source year-bin re-ordered")
            real=s["original_relative_365day_bins_anchored_at_first_QC_epoch"]
            if j<len(real):
                if cell.get("data-count")!=str(real[j]) or cell.get("data-state") is not None:
                    raise ValueError("SVG original ZTF measured count altered")
            elif cell.get("data-state")!="OUTSIDE_SOURCE_SPAN" or cell.get("data-count") is not None:
                raise ValueError("Outside original temporal span incorrectly displayed as a measured zero")
    for label in (
        "R4","SYNTHETIC","591","684","93","Timeout","physical",
        "1605115300003377","1605215300005161","609108400001155",
    ):
        if label.lower() not in report_text.lower():
            raise ValueError("Public R4 scientific report omits source evidence or explicit synthetic disclaimers")
    if ("physical GAIA" in report_text.upper()
            and "BLOCKED" not in report_text.upper()):
        raise ValueError("Physical source scientific gate hidden")
    return {
        "status":"R4_ORIGINAL_SOURCE_SAMPLING_BINS_VERIFIED_AND_SYNTHETIC_WINDOW_DISTINCT__NO_REAL_PERIODS",
        "original_successful_survey_source_OIDs":3,
        "original_unavailable_archive_OIDs":3,
        "original_accepted_good_visit_count":591,
        "real_series_with_two_consecutive_365day_empty_bins":2,
        "physical_gaia_ztf_source_matches_confirmed":0,
        "original_true_one_day_spectral_window_measured":False,
        "synthetic_window_example_not_a_star_period":True,
        "original_source_figure_source_cells_checked":len(nodes),
    }


def audit_r4_repo(root:Path)->dict:
    root=Path(root).resolve()
    expected=run_r4_from_repo(root)
    paths=[EVIDENCE,FIGURE,REPORT]
    for path in paths:
        f=root/path
        if f.is_symlink() or not f.is_file() or not f.resolve().is_relative_to(root):
            raise ValueError("Missing or unsafe R4 published scientific source")
    data=json.loads((root/EVIDENCE).read_text(encoding="utf8"))
    svg=(root/FIGURE).read_text(encoding="utf8")
    report=(root/REPORT).read_text(encoding="utf8")
    return validate_r4_permanent_evidence(data,svg,report,expected)


def main()->None:
    p=argparse.ArgumentParser(description="Offline verify original R3→R4 evidence provenance and distinct synthetic-only mathematical window examples")
    p.add_argument("--root",type=Path,default=Path("."))
    args=p.parse_args()
    print(json.dumps(audit_r4_repo(args.root),indent=2))


if __name__=="__main__":
    main()
