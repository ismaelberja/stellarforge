"""R5 permanent critical-study claim audit, fail-closed to original R2/R3/R4.

No remote science queries and no physical Gaia-ZTF counterpart certification.
The 24 Gaia IDs, 6 ZTF original ObjectIDs and 684 original per-exposure
source rows must never be shown as one astrometric match/variability funnel.
"""
from __future__ import annotations
import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path

from stellarforge.r5_critical_falsification import (
    LITERATURE,build_r5_critical_falsification,
)

R5_REPORT="research/taurus_variability/R5_FINAL_CRITICAL_VALIDATION_AND_SELECTION_RESULTS.md"
R5_LEDGER="reports/taurus_variability_r5/R5_CRITICAL_VALIDATION_AND_SELECTION_DECISION_NO_RAW.json"
R5_FIGURE="docs/figures/taurus-r5-original-source-denominators-no-funnel.svg"
R5_PREREG="research/taurus_variability/R5_CRITICAL_VALIDATION_SELECTION_LITERATURE_PREREGISTRATION.md"
SVG_NS="{http://www.w3.org/2000/svg}"
REQUIRED_R5_OUTCOMES={
    "original_published_author_catalogue_provenance_24_of_24_verified":True,
    "r5_literature_and_selection_critical_audit_complete":True,
    "r5_independent_physical_gaia_ztf_source_validation_passed":False,
    "observational_source_specific_physical_variability_established":False,
    "original_ztf_oid_lightcurves_merged":False,
    "original_same_field_magnitude_matched_controls_scientifically_established":False,
    "real_one_day_ztf_spectral_window_measured":False,
    "original_bit15_mask_implies_catflags_strict_zero":False,
    "true_original_provider_timeout_implies_zero_real_source_visits":False,
    "r6_conservative_methodological_inconclusive_report_allowed":True,
    "r6_new_stellar_variable_or_companion_claim_allowed":False,
    "r6_taurus_population_variable_incidence_report_allowed":False,
    "journal_scientific_claims_require_external_critical_expert_review":True,
}
EXPECTED_GROUPS=(
    (24, (
        ("Published adopted IDs",24),("Prelim Gaia QC",17),
        ("Astrometry review",7),("ZTF positional response",22),
        ("Physical ZTF matches",0),
    )),
    (6,(
        ("Original fixed ObjectIDs",6),("DR24 CSV received",3),
        ("Archive timeouts",3),("Gaia counterparts",0),
    )),
    (684,(
        ("Original ZTF rows",684),("Bit15-QC accepted",591),
        ("Bit15-flagged",93),
    )),
)


def _eq(d:dict,k:str,value,scope:str)->None:
    if not isinstance(d,dict) or k not in d or type(d[k]) is not type(value) or d[k]!=value:
        raise ValueError(f"{scope}.{k}: claim is not supported by immutable source-receipt evidence")


def validate_r5_published_result(final:dict,svg_content:str,report_content:str,expected:dict)->dict:
    _eq(final,"schema_version",
        "stellarforge-taurus-r5-pinned-critical-science-selection-verdict-derived-original-R2-R3-R4-v1","R5_record")
    _eq(final,"date_utc","2026-11-14","R5_record")
    _eq(final,"r5_review_verdict",
        "R5_LITERATURE_SELECTION_FALSIFICATION_METHODOLOGY_COMPLETED__INDEPENDENT_PHYSICAL_GAIA_ZTF_VALIDATION_NOT_MET","R5_record")
    _eq(final,"r5_preregistration",R5_PREREG,"R5_record")
    _eq(final,"r5_scientific_results",R5_REPORT,"R5_record")
    original=final.get("original_source_evidence_references")
    for key,val in (
        ("r1_seed_sha256","9cecb94704f028a981045629ad16ecb770f51bba4b6bb3bf13dda769327ff37e"),
        ("r2_publisher_original_table_sha256","8ffd84c876afe6b6d7690f8e4ba4f97ec94f643e0e924c98f6c101b8656c0493"),
        ("r2_original_publisher_actions",43499836719),
        ("r3_original_first_actions",43593335135),
        ("r3_original_first_artifact_zip_sha256","6e9e1cdbba946d9f7c5036e74a42917bb4011530dfec1d289b4b30c47f393049"),
        ("r3_original_timeout_retry_actions",43593994009),
        ("r3_original_retry_artifact_zip_sha256","69f37df9f57c2dc49e4636740fb74c8c429d67e3d250b92201696edd26d89104"),
        ("r4_original_source_cadence_actions",43596705130),
        ("r4_original_analysis_artifact_zip_sha256","99a458146f63d19ac4f59fc741eaaab1ff36e6d661b53b82a45fd5d3983a5ad6"),
    ):_eq(original,key,val,"R1_to_R4_original_provenance")
    ratios=final.get("ratios_descriptive_not_population")
    source_ratios=expected["denominator_locked_descriptive_summary_not_population_inference"]
    if not isinstance(ratios,list) or len(ratios)!=len(source_ratios):
        raise ValueError("12 different original-source denominator claims must remain distinguishable")
    if [x.get("metric") for x in ratios]!=list(source_ratios):
        raise ValueError("New metric order or spurious source denominator introduced")
    for r in ratios:
        orig=source_ratios[r["metric"]]
        if set(r)!={"metric","numerator","denominator","percent_descriptive_only"}:
            raise ValueError("R5 denominator row has invented source fields")
        for key,v in (
            ("numerator",orig["n"]),("denominator",orig["N"]),
            ("percent_descriptive_only",orig["percent_descriptive_only"]),
        ):
            if key=="percent_descriptive_only":
                # JSON represents exact zero percent as either 0 or 0.0;
                # only the numeric value is significant, not its wire type.
                if type(r.get(key)) not in (int,float) or float(r[key])!=float(v):
                    raise ValueError("Published original-source descriptive percentage changed")
            else:
                _eq(r,key,v,"R5 independent original source ratio")
    gates=final.get("physical_scientific_acceptance_gates")
    expected_gates=expected["falsification_gates"]
    if not isinstance(gates,list) or len(gates)!=8:
        raise ValueError("R5 original 8 scientific falsification gates incomplete")
    for got,evidence in zip(gates,expected_gates):
        if set(got)!={"gate","status","reason"}:
            raise ValueError("R5 physical/source gate has new unsupported fields")
        _eq(got,"gate",evidence["gate"],"R5 scientific source gate")
        _eq(got,"status",evidence["status"],"R5 scientific source gate")
        reason=got["reason"]
        if not isinstance(reason,str) or len(reason)<45:
            raise ValueError("R5 critical scientific gate missing source-scoped uncertainty reason")
    refs=final.get("external_official_literature_urls")
    if not isinstance(refs,list) or len(refs)!=len(LITERATURE):
        raise ValueError("R5 original literature references were deleted")
    for got,(key,value) in zip(refs,LITERATURE.items()):
        if set(got)!={"id","url","independently_authenticates_physical_gaia_ztf_source"}:
            raise ValueError("R5 literature reference evidence type overstated")
        _eq(got,"id",key,"R5 literature")
        _eq(got,"url",value["reference_url"],"R5 literature")
        _eq(got,"independently_authenticates_physical_gaia_ztf_source",False,"R5 literature")
    flags=final.get("interpretation_flags")
    if flags is None or set(flags)!=set(REQUIRED_R5_OUTCOMES):
        raise ValueError("R5 science / R6 eligibility fields missing or added")
    for k,v in REQUIRED_R5_OUTCOMES.items():_eq(flags,k,v,"R5 scientific outcome")
    _eq(final,"source_claims_are_original_source_derived_only",True,"R5 no-raw")
    _eq(final,"individual_ZTF_original_measurements_or_times_committed",False,"R5 no-raw")
    _eq(final,"unpublished_private_ALMA_TFM_data_committed",False,"R5 no-raw")
    if ("NO-GO" not in final.get("conclusion","")
            or "no new astrophysical" not in final["conclusion"].lower()):
        raise ValueError("R5 requires explicit negative physical-source scientific verdict")
    try:
        fig=ET.fromstring(svg_content)
    except ET.ParseError as exc:
        raise ValueError("R5 public SVG figure is not well formed") from exc
    if (fig.tag!=SVG_NS+"svg" or fig.get("role")!="img"
            or fig.find(SVG_NS+"title") is None
            or fig.find(SVG_NS+"desc") is None
            or fig.findall(".//"+SVG_NS+"image")
            or fig.findall(".//"+SVG_NS+"script")):
        raise ValueError("R5 real original source denominator figure is not accessible/transparent")
    panels=[g for g in fig.findall(".//"+SVG_NS+"g") if g.get("data-panel")]
    if len(panels)!=3:
        raise ValueError("R5 source denominators must remain three separate data panels")
    for i,(panel,(N,source_rows)) in enumerate(zip(panels,EXPECTED_GROUPS),1):
        if panel.get("data-panel")!=str(i) or panel.get("data-denominator")!=str(N):
            raise ValueError("R5 Gaia, original ZTF ObjectID, and photometry source counts mixed in figure")
        cells=[x for x in panel.findall(".//"+SVG_NS+"g") if x.get("data-metric")]
        if len(cells)!=len(source_rows):
            raise ValueError("R5 quantitative source ratio figure has missing or invented bars")
        for g,(label,n) in zip(cells,source_rows):
            if g.get("data-metric")!=label or g.get("data-count")!=str(n) or g.get("data-base")!=str(N):
                raise ValueError("R5 original science figure source numerator/denominator changed")
    if not all(x in svg_content for x in ("never a single attrition funnel","NOT VERIFIED","0 authenticated Gaia")):
        raise ValueError("R5 figure lacks population, source-identity and scientific caveats")
    required_report=[
        "Luhman","Mas et al.","24/532","24/467","17/24","7/24",
        "22/24","0/24","3/6","591/684","93/684","2/3",
        "catflags = 0","source","nonrandom","R6",
        "NOT VERIFIED","R5","DOI","one-day",
    ]
    for word in required_report:
        if word.lower() not in report_content.lower():
            raise ValueError(f"R5 manuscript report omitted essential falsification context: {word}")
    if any(x.lower() not in report_content.lower() for x in
           ("https://doi.org/10.1051/0004-6361/202554522",
            "https://doi.org/10.3847/1538-3881/ac9da3",
            "https://irsa.ipac.caltech.edu/")):
        raise ValueError("R5 real source literature attribution removed")
    return {
        "status":"R5_CRITICAL_SELECTION_AND_PRIOR_LITERATURE_AUDITED__GAIA_ZTF_PHYSICAL_SOURCE_VALIDATION_NOT_MET",
        "source_ratio_count":len(ratios),
        "noninterchangeable_gaia_ztf_epoch_denominators":[24,6,684],
        "original_publisher_gaia_ids_verified":24,
        "original_DR24_source_rows_bit15_accepted":591,
        "source_fig_original_count_panels_verified":len(panels),
        "scientific_acceptance_gates_documented":len(gates),
        "independent_physical_gaia_to_ztf_counterparts_confirmed":0,
        "physical_source_variability_not_inferred":True,
        "r6_inconclusive_methods_report_suitable_for_completion":True,
        "new_asterisk_astrophysical_discovery_claimed":False,
    }


def audit_r5_repo(root:Path)->dict:
    root=Path(root).resolve()
    expected=build_r5_critical_falsification(root)
    for path in (R5_REPORT,R5_LEDGER,R5_FIGURE,R5_PREREG):
        full=root/path
        if full.is_symlink() or not full.is_file() or not full.resolve().is_relative_to(root):
            raise ValueError("R5 source publication or pre-registered protocol missing/unsafe")
    content=json.loads((root/R5_LEDGER).read_text(encoding="utf8"))
    svg=(root/R5_FIGURE).read_text(encoding="utf8")
    report=(root/R5_REPORT).read_text(encoding="utf8")
    return validate_r5_published_result(content,svg,report,expected)


def main()->None:
    p=argparse.ArgumentParser(description="Re-audit original Gaia/ZTF source R2→R5 evidence, nonrandom sample and 8-gate negative physical-science verdict offline")
    p.add_argument("--root",type=Path,default=Path("."))
    args=p.parse_args()
    print(json.dumps(audit_r5_repo(args.root),indent=2))


if __name__=="__main__":
    main()
