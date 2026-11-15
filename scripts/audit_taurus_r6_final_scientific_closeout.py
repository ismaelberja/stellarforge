"""Strict offline scientific R1–R6 research closeout auditor.

Audit the full original source evidence chain and the standalone research
manuscript without pretending software CI is independent Gaia↔ZTF physical
source calibration or peer review.

No raw original ZTF photometry, original FITS, external publication table
or unpublished/private ALMA/TFM data are downloaded or distributed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.audit_taurus_r2_24_go_no_go import audit_24_final
from scripts.audit_taurus_r3_six_original_source_receipts import audit_r3_original_six_source_receipts
from scripts.audit_taurus_r4_cadence_feasibility import audit_r4_repo
from scripts.audit_taurus_r5_critical_falsification import audit_r5_repo
from scripts.run_taurus_r4_sampling_window_feasibility import run_r4_from_repo
from stellarforge.r5_critical_falsification import build_r5_critical_falsification

R6_LEDGER="reports/taurus_variability_r6/R6_FINAL_ORIGINAL_SOURCE_RESEARCH_CLOSEOUT_NO_RAW.json"
R6_REPORT="research/taurus_variability/R6_FINAL_SCIENTIFIC_FEASIBILITY_MANUSCRIPT.md"
R6_PREREG="research/taurus_variability/R6_FINAL_RESEARCH_CLOSEOUT_PREREGISTRATION.md"
BASELINE="05340f6fea6c524e2067d578ed49efdacb9945f5"
SOURCE_SHA="9cecb94704f028a981045629ad16ecb770f51bba4b6bb3bf13dda769327ff37e"
ORIGINAL_PUBLISHER_SHA="8ffd84c876afe6b6d7690f8e4ba4f97ec94f643e0e924c98f6c101b8656c0493"
SOURCE_META={
    "frozen_R1_nonrandom_24_seed_sha256":SOURCE_SHA,
    "original_Luhman_AJ_2023_mrt_response_sha256":ORIGINAL_PUBLISHER_SHA,
    "original_Luhman_publisher_actions_run_id":43499836719,
    "r3_original_DR24_first_exact_OID_actions_run_id":43593335135,
    "r3_original_DR24_first_artifact_zip_sha256":"6e9e1cdbba946d9f7c5036e74a42917bb4011530dfec1d289b4b30c47f393049",
    "r3_original_DR24_timeout_only_retry_actions_run_id":43593994009,
    "r3_original_DR24_retry_artifact_zip_sha256":"69f37df9f57c2dc49e4636740fb74c8c429d67e3d250b92201696edd26d89104",
    "r4_original_source_derived_actions_run_id":43596705130,
    "r4_original_cadence_artifact_zip_sha256":"99a458146f63d19ac4f59fc741eaaab1ff36e6d661b53b82a45fd5d3983a5ad6",
    "r5_original_scientific_review_main_actions_run_id":43610495397,
    "r5_original_scientific_review_main_commit":BASELINE,
}
DENOMINATORS={
    "original_author_adopted_taurus_member_rows":532,
    "original_author_adopted_taurus_members_with_Gaia_ID":467,
    "frozen_technical_Gaia_target_source_IDs":24,
    "individually_frozen_original_ZTF_survey_ObjectIDs_in_R3":6,
    "original_ZTF_per_epoch_photometric_source_rows_in_retrieved_DR24_CSVs":684,
}
EXACT_RESULTS={
    "exact_publisher_member_row_Gaia_id_and_sky_position_matches":24,
    "preliminary_Gaia_astrometric_screen_pass_sources":17,
    "Gaia_astrometric_review_sources":7,
    "Gaia_sources_with_neighbour_within_5arcsec":4,
    "original_ZTF_positional_response_target_positions_with_parsed_rows":22,
    "original_ZTF_positional_response_unresolved_target_positions":2,
    "independently_authenticated_physical_Gaia_to_ZTF_counterparts":0,
    "original_ZTF_DR24_exact_OID_CSV_source_responses":3,
    "original_ZTF_DR24_exact_OID_requests_timed_out_twice":3,
    "original_ZTF_DR24_source_rows_from_successful_CSVs":684,
    "original_ZTF_source_rows_retained_by_catflags_bit15_only":591,
    "original_ZTF_source_rows_excluded_by_catflags_bit15_only":93,
    "original_ZTF_successful_survey_OID_with_two_consecutive_empty_source_relative_365day_bins":2,
    "original_ZTF_successful_survey_OID_with_all_source_relative_365day_bins_nonempty":1,
    "original_ZTF_OID_series_with_30_good_visit_90day_technical_access_pass":3,
    "original_ZTF_OID_series_with_authenticated_physical_Gaia_stellar_period":0,
    "original_ZTF_ObjectID_curves_merged_to_one_physical_Gaia_star":0,
    "actual_per_epoch_original_source_times_committed_to_repository":False,
    "genuine_original_ZTF_one_day_spectral_window_measured":False,
    "synthetic_example_1day_window_is_real_astro_observation":False,
    "reported_Taurus_variable_population_fraction":False,
    "reported_new_physical_variable_star":False,
    "reported_new_stellar_companion":False,
}
EXPECTED_PHASES=(
    ("R1","COMPLETED_FROZEN_NONRANDOM_24_SOURCE_SEED",
     "research/taurus_variability/R1_PREREGISTERED_SCIENCE_PROTOCOL.md"),
    ("R2","COMPLETED_SOURCE_ACCESS_AND_AMBIGUITY_SCREEN__IDENTITY_NO_GO",
     "research/taurus_variability/R2_FINAL_24_SOURCE_SCREENING_DECISION.md"),
    ("R3","PARTIAL_ORIGINAL_DR24_OID_ACCESS_AUDITED_AND_CLOSED",
     "research/taurus_variability/R3_REAL_SIX_ORIGINAL_ZTF_DR24_QC_RESULTS.md"),
    ("R4","COMPLETED_TECHNICAL_CADENCE_SCREEN__ASTROPHYSICAL_PERIODS_NOT_MEASURED",
     "research/taurus_variability/R4_REAL_ZTF_SAMPLING_WINDOW_FEASIBILITY_RESULTS.md"),
    ("R5","COMPLETED_LITERATURE_SELECTION_AND_EIGHT_GATE_FALSIFICATION__SOURCE_IDENTITY_NO_GO",
     "research/taurus_variability/R5_FINAL_CRITICAL_VALIDATION_AND_SELECTION_RESULTS.md"),
    ("R6","COMPLETED_MANUSCRIPT_STYLE_FEASIBILITY_CLOSEOUT__NO_ASTROPHYSICAL_DISCOVERY",
     R6_REPORT),
)
SOURCE_FIGURES=(
    "docs/figures/taurus-r4-original-ztf-dr24-relative-365day-cadence.svg",
    "docs/figures/taurus-r5-original-source-denominators-no-funnel.svg",
)
SOURCE_LITERATURE=(
    ("K. L. Luhman",2023,"10.3847/1538-3881/ac9da3","165","37"),
    ("C. Mas et al.",2026,"10.1051/0004-6361/202554522","705","A172"),
)


def _equal(d:dict,key:str,expected,source:str)->None:
    if not isinstance(d,dict) or key not in d or type(d[key]) is not type(expected) or d[key]!=expected:
        raise ValueError(f"{source}.{key}: original-source observation or scientific claim unsupported")


def verify_r6_research_closeout(document:dict,manuscript:str,prereg:str,
                               prior_r4:dict,prior_r5:dict)->dict:
    """Validate six separate method outcomes and all scientific NO-GO claims."""
    for k,v in (
        ("schema_version","stellarforge-taurus-r6-final-methodological-observational-feasibility-no-raw-v1"),
        ("date_utc","2026-11-15"),
        ("author","Ismael Berja Ruiz"),
        ("research_note_type","PUBLIC_REPOSITORY_MANUSCRIPT_NOT_PEER_REVIEWED_NOT_ARXIV_NOT_JOURNAL_PUBLISHED"),
        ("r6_source_R5_integrated_baseline_main_sha",BASELINE),
        ("software_engineering_release","2.1.0"),
        ("r6_preregistered_before_results",R6_PREREG),
        ("r6_final_manuscript",R6_REPORT),
        ("r6_source_audit_script","scripts/audit_taurus_r6_final_scientific_closeout.py"),
    ):_equal(document,k,v,"r6_manifest")
    if (not isinstance(document.get("research_title"),str)
            or not document["research_title"].startswith("StellarForge / Taurus R1–R6")):
        raise ValueError("R6 final paper/technical study title was altered")
    for parent,ground in (
        ("upstream_authenticated_original_evidence",SOURCE_META),
        ("distinct_scope_denominators",DENOMINATORS),
        ("original_results",EXACT_RESULTS),
    ):
        data=document.get(parent)
        if not isinstance(data,dict) or set(data)!=set(ground):
            raise ValueError("R6 original source evidence keys changed")
        for k,v in ground.items():_equal(data,k,v,parent)
    if len(document.get("phase_research_final_decisions",[]))!=6:
        raise ValueError("R6 conclusion missing one of R1–R6 stages")
    for row,(phase,status,source_file) in zip(document["phase_research_final_decisions"],EXPECTED_PHASES):
        if set(row)!={"phase","methodological_deliverable_closure_status",
                      "independent_physical_Gaia_ZTF_astrophysical_claim_permitted",
                      "research_scope_and_result","source_specific_primary_report"}:
            raise ValueError("Scientific R1-R6 phase changed or injected unsupported field")
        for k,v in (
            ("phase",phase),
            ("methodological_deliverable_closure_status",status),
            ("source_specific_primary_report",source_file),
            ("independent_physical_Gaia_ZTF_astrophysical_claim_permitted",False),
        ):_equal(row,k,v,phase)
        if not isinstance(row["research_scope_and_result"],str) or len(row["research_scope_and_result"])<50:
            raise ValueError("R6 phase summary no longer identifies scientific limitation")
    # Preserve original R3 partial provenance against genuine R4 no-raw rows.
    r6_rows=document.get("r3_frozen_six_survey_OID_results")
    orig=prior_r4["source_observations"]
    if not isinstance(r6_rows,list) or len(r6_rows)!=6 or len(orig)!=6:
        raise ValueError("R3 six OIDs and original R4 source evidence are not identical")
    for item,ref in zip(r6_rows,orig):
        for k,v in (
            ("original_ZTF_survey_ObjectID",ref["original_ztf_oid"]),
            ("native_original_band",ref["original_ztf_filter"]),
            ("physically_authenticated_counterpart_Gaia_ID",None),
            ("real_physical_stellar_lightcurve_and_period_claim",False),
        ):_equal(item,k,v,"R6_original_ZTF_OID")
        if ref["cadence_metric_computable"]:
            compare=(
                ("original_source_CSV_access","HTTP_200_EXACT_ORIGINAL_DR24_OID_CSV"),
                ("original_source_photometry_rows",ref["original_source_rows"]),
                ("original_bit15_QC_retained_visits",ref["technical_source_qc_accepted_epochs"]),
                ("original_bit15_rejected_visits",ref["original_source_catflags_32768_rejected_rows"]),
                ("original_QC_first_to_last_time_span_days",ref["original_first_to_last_accepted_visit_span_days"]),
                ("source_relative_original_QC_365day_bin_counts",ref["original_relative_365day_bins_anchored_at_first_QC_epoch"]),
            )
        else:
            compare=(
                ("original_source_CSV_access","TWO_ARCHIVE_PROVIDER_TIMEOUTS_UNRESOLVED"),
                ("original_source_photometry_rows",None),
                ("original_bit15_QC_retained_visits",None),
                ("original_bit15_rejected_visits",None),
                ("original_QC_first_to_last_time_span_days",None),
                ("source_relative_original_QC_365day_bin_counts",None),
            )
        for k,v in compare:_equal(item,k,v,"R6_original_ZTF_OID")
        if set(item)!={
            "original_ZTF_survey_ObjectID","native_original_band",
            "original_source_CSV_access","original_source_photometry_rows",
            "original_bit15_QC_retained_visits","original_bit15_rejected_visits",
            "original_QC_first_to_last_time_span_days",
            "source_relative_original_QC_365day_bin_counts",
            "physically_authenticated_counterpart_Gaia_ID",
            "real_physical_stellar_lightcurve_and_period_claim"
        }:
            raise ValueError("Original source summary contains unauthorized physical/lightcurve claims")
    gates=document.get("r5_scientific_independent_gate_verdicts")
    other_gates=prior_r5["falsification_gates"]
    if not isinstance(gates,list) or len(gates)!=8:
        raise ValueError("Eight independently requested R5/R6 scientific gates omitted")
    for a,b in zip(gates,other_gates):
        if set(a)!={"gate","status"}:
            raise ValueError("Original physical-star gate result altered")
        _equal(a,"gate",b["gate"],"R6_original_R5_gate")
        _equal(a,"status",b["status"],"R6_original_R5_gate")
    if document.get("real_source_derived_figures")!=list(SOURCE_FIGURES):
        raise ValueError("R6 real-source figures missing or replaced with synthetic graphics")
    refs=document.get("primary_original_prior_scientific_literature")
    if not isinstance(refs,list) or len(refs)!=2:
        raise ValueError("R6 cited original prior papers are missing")
    for article,(author,year,doi,vol,no) in zip(refs,SOURCE_LITERATURE):
        for k,v in (
            ("author",author),("year",year),("doi",doi),("volume",vol),("article",no),
        ):_equal(article,k,v,"original_scientific_reference")
        if not isinstance(article.get("work"),str) or len(article["work"])<25:
            raise ValueError("R6 primary literature title not identified")
    for k,v in (
        ("overall_methodological_research_program_R1_to_R6_closed_with_explicit_limitations",True),
        ("overall_physical_Gaia_ZTF_source_stellar_variability_scientifically_validated",False),
        ("overall_archival_data_provenance_and_software_consistency_automatically_auditable",True),
        ("original_source_epochs_FITS_pixels_or_private_ALMA_TFM_committed",False),
        ("author_external_scientific_review_needed_before_journal_submission",True),
        ("journal_publication_or_peer_review_claimed",False),
        ("final_result_category","INCONCLUSIVE_ASTROPHYSICAL_TARGET_VARIABILITY__COMPLETED_ORIGINAL_DATA_OBSERVATIONAL_FEASIBILITY_STUDY"),
        ("novel_astronomical_discovery_claimed",False),
    ):_equal(document,k,v,"R6_manuscript_and_science_verdict")
    if "NO-GO" not in prereg or BASELINE not in prereg:
        raise ValueError("Final R6 scientific no-go/commit frozen acceptance protocol missing")
    required_sections=(
        "## Abstract","## Resumen en español",
        "## 1. Context, question and scope",
        "## 2. Materials, provenance and methods",
        "## 3. Results","## 4. Discussion and limitations",
        "## 5. Conclusions","## Data availability, evidence freeze and reproducibility",
        "### References",
    )
    for section in required_sections:
        if section not in manuscript:
            raise ValueError(f"Standalone R6 manuscript missing section: {section}")
    required_content=(
        "24/24","17/24","7/24","22/24","0/24","532","467",
        "684","591","93","3/6","2/3",
        "catflags & 32768","catflags=0","Timeout twice",
        "SYNTHETIC","not a peer-reviewed","Mas et al.",
        "10.3847/1538-3881/ac9da3",
        "10.1051/0004-6361/202554522",
        SOURCE_SHA,ORIGINAL_PUBLISHER_SHA,BASELINE,
        SOURCE_FIGURES[0],SOURCE_FIGURES[1],
        "R6_FINAL_ORIGINAL_SOURCE_RESEARCH_CLOSEOUT_NO_RAW.json",
        "original publisher","original ZTF",
    )
    for item in required_content:
        if item.lower() not in manuscript.lower():
            raise ValueError(f"R6 scientific manuscript lacks an original claim/source caveat: {item}")
    if len(manuscript)<13000:
        raise ValueError("Final R6 report too small for independently reviewable scientific method")
    if (document["original_results"]["original_ZTF_source_rows_retained_by_catflags_bit15_only"]
            + document["original_results"]["original_ZTF_source_rows_excluded_by_catflags_bit15_only"]
            != document["distinct_scope_denominators"]["original_ZTF_per_epoch_photometric_source_rows_in_retrieved_DR24_CSVs"]):
        raise ValueError("Bit15-rejected source epochs do not reconcile to original raw photometry")
    return {
        "status":"R6_FINAL_ORIGINAL_DATA_RESEARCH_METHODS_CLOSEOUT_AUDITED__PHYSICAL_GAIA_ZTF_ASTROPHYSICS_INCONCLUSIVE",
        "r1_to_r6_research_phase_decisions":len(EXPECTED_PHASES),
        "r5_to_r6_independent_scientific_gates_verified":len(gates),
        "actual_original_gaia_source_ids_in_author_table":24,
        "original_physical_gaia_to_ztf_matches_authenticated":0,
        "original_fixed_ztf_oid_successful_CSVs":3,
        "original_ztf_survey_photometric_rows_bit15_accepted":591,
        "original_ztf_OIDs_with_two_original_server_timeouts":3,
        "true_original_physical_stellar_periods_reported":0,
        "original_source_derivatives_figures_used":len(SOURCE_FIGURES),
        "final_research_manuscript_factual_evidence_locked":True,
        "astrophysical_discovery_claimed":False,
        "journal_peer_review_or_publication_claimed":False,
        "engineering_software_v2_1_unchanged":True,
    }


def audit_r6_repo(root:Path)->dict:
    root=Path(root).resolve()
    # Independent previous evidence fails shut if upstream values are mutated.
    old_r2=audit_24_final(root)
    old_r3=audit_r3_original_six_source_receipts(root)
    old_r4=audit_r4_repo(root)
    old_r5=audit_r5_repo(root)
    if (old_r2["n_independent_gaia_ztf_physical_sources_authenticated"]!=0
            or old_r3["original_physical_gaia_ztf_sources_authenticated"]!=0
            or old_r4["original_true_one_day_spectral_window_measured"] is not False
            or old_r5["independent_physical_gaia_to_ztf_counterparts_confirmed"]!=0):
        raise ValueError("Original source truth changed in R2, R3, R4 or R5")
    for rel in (R6_LEDGER,R6_REPORT,R6_PREREG,*SOURCE_FIGURES):
        p=root/rel
        if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(root):
            raise ValueError(f"R6 registered source document is missing, unsafe or modified: {rel}")
    j=json.loads((root/R6_LEDGER).read_text("utf8"))
    report=(root/R6_REPORT).read_text("utf8")
    prereg=(root/R6_PREREG).read_text("utf8")
    return verify_r6_research_closeout(
        j,report,prereg,
        run_r4_from_repo(root),
        build_r5_critical_falsification(root),
    )


def main()->None:
    p=argparse.ArgumentParser(description="Offline independently re-audit R1–R6 original-source scientific feasibility and honest physical-source NO-GO")
    p.add_argument("--root",type=Path,default=Path("."))
    args=p.parse_args()
    print(json.dumps(audit_r6_repo(args.root),indent=2))


if __name__=="__main__":
    main()
