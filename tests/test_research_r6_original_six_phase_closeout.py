"""Research R6 closeout: original R2–R5 data must survive, no new stellar claims.

All fake values here are explicitly synthetic adversarial input mutations, not
external observed Gaia/ZTF source data.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts.audit_taurus_r6_final_scientific_closeout import (
    BASELINE,R6_LEDGER,R6_PREREG,R6_REPORT,
    EXPECTED_PHASES,SOURCE_META,DENOMINATORS,EXACT_RESULTS,
    SOURCE_FIGURES,audit_r6_repo,verify_r6_research_closeout,
)
from scripts.run_taurus_r4_sampling_window_feasibility import run_r4_from_repo
from stellarforge.r5_critical_falsification import build_r5_critical_falsification

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def evidence():
    document=json.loads((ROOT/R6_LEDGER).read_text("utf8"))
    report=(ROOT/R6_REPORT).read_text("utf8")
    prereg=(ROOT/R6_PREREG).read_text("utf8")
    return document,report,prereg,run_r4_from_repo(ROOT),build_r5_critical_falsification(ROOT)


def validate(evidence, changed=None, new_report=None, new_prereg=None):
    doc,report,prereg,r4,r5=evidence
    return verify_r6_research_closeout(
        doc if changed is None else changed,
        report if new_report is None else new_report,
        prereg if new_prereg is None else new_prereg,
        r4,r5
    )


def test_source_audited_scientific_r1_to_r6_feasibility_closeout():
    z=audit_r6_repo(ROOT)
    assert z["status"]=="R6_FINAL_ORIGINAL_DATA_RESEARCH_METHODS_CLOSEOUT_AUDITED__PHYSICAL_GAIA_ZTF_ASTROPHYSICS_INCONCLUSIVE"
    assert z["r1_to_r6_research_phase_decisions"]==6
    assert z["r5_to_r6_independent_scientific_gates_verified"]==8
    assert z["actual_original_gaia_source_ids_in_author_table"]==24
    assert z["original_physical_gaia_to_ztf_matches_authenticated"]==0
    assert z["original_fixed_ztf_oid_successful_CSVs"]==3
    assert z["original_ztf_survey_photometric_rows_bit15_accepted"]==591
    assert z["original_ztf_OIDs_with_two_original_server_timeouts"]==3
    assert z["true_original_physical_stellar_periods_reported"]==0
    assert z["astrophysical_discovery_claimed"] is False
    assert z["journal_peer_review_or_publication_claimed"] is False
    assert z["engineering_software_v2_1_unchanged"] is True


def test_R6_6_research_phases_are_separate_from_6_ZTF_survey_objects(evidence):
    d=evidence[0]
    assert [s["phase"] for s in d["phase_research_final_decisions"]]==[
        "R1","R2","R3","R4","R5","R6"
    ]
    assert len(d["r3_frozen_six_survey_OID_results"])==6
    assert d["distinct_scope_denominators"]==DENOMINATORS
    assert d["upstream_authenticated_original_evidence"]==SOURCE_META
    assert d["original_results"]==EXACT_RESULTS
    assert d["r6_source_R5_integrated_baseline_main_sha"]==BASELINE
    assert "PARTIAL" in d["phase_research_final_decisions"][2]["methodological_deliverable_closure_status"]
    assert not any(s["independent_physical_Gaia_ZTF_astrophysical_claim_permitted"]
                   for s in d["phase_research_final_decisions"])


@pytest.mark.parametrize("location,key,value",[
    ("original_results","independently_authenticated_physical_Gaia_to_ZTF_counterparts",1),
    ("original_results","original_ZTF_source_rows_retained_by_catflags_bit15_only",684),
    ("original_results","original_ZTF_DR24_exact_OID_requests_timed_out_twice",0),
    ("original_results","genuine_original_ZTF_one_day_spectral_window_measured",True),
    ("original_results","reported_new_physical_variable_star",True),
    ("original_results","reported_Taurus_variable_population_fraction",True),
    ("original_results","actual_per_epoch_original_source_times_committed_to_repository",True),
    ("distinct_scope_denominators","frozen_technical_Gaia_target_source_IDs",6),
    ("distinct_scope_denominators","original_ZTF_per_epoch_photometric_source_rows_in_retrieved_DR24_CSVs",591),
    ("upstream_authenticated_original_evidence","original_Luhman_AJ_2023_mrt_response_sha256","0"*64),
    ("upstream_authenticated_original_evidence","r5_original_scientific_review_main_commit","0"*40),
])
def test_source_claim_inflation_or_wrong_denominator_blocked(evidence,location,key,value):
    bad=copy.deepcopy(evidence[0])
    bad[location][key]=value
    with pytest.raises(ValueError):
        validate(evidence,bad)


@pytest.mark.parametrize("index,key,value",[
    (0,"original_bit15_QC_retained_visits",79),
    (0,"original_source_photometry_rows",100),
    (0,"source_relative_original_QC_365day_bin_counts",[23,33,0,0,10,5]),
    (1,"original_QC_first_to_last_time_span_days",90.0),
    (2,"physically_authenticated_counterpart_Gaia_ID","149623711269425408"),
    (2,"real_physical_stellar_lightcurve_and_period_claim",True),
    (3,"original_source_CSV_access","HTTP_200_EXACT_ORIGINAL_DR24_OID_CSV"),
    (3,"original_bit15_QC_retained_visits",0),
    (4,"original_source_photometry_rows",0),
    (5,"native_original_band","g"),
])
def test_original_ZTF_OIDs_cannot_become_synthetic_stars_or_zero_archive_visits(evidence,index,key,value):
    bad=copy.deepcopy(evidence[0])
    bad["r3_frozen_six_survey_OID_results"][index][key]=value
    with pytest.raises(ValueError):
        validate(evidence,bad)


@pytest.mark.parametrize("index,key,value",[
    (0,"phase","R4"),
    (1,"methodological_deliverable_closure_status","R2_PHYSICAL_IDENTIFICATION_SOLVED"),
    (2,"methodological_deliverable_closure_status","COMPLETED_ALL_SIX_ORIGINAL_ZTF_CSV"),
    (3,"independent_physical_Gaia_ZTF_astrophysical_claim_permitted",True),
    (4,"source_specific_primary_report","research/taurus_variability/R2_FINAL_24_SOURCE_SCREENING_DECISION.md"),
    (5,"methodological_deliverable_closure_status","R6_PEER_REVIEWED_NEW_VARIABLE"),
])
def test_six_original_research_phase_decisions_immutable(evidence,index,key,value):
    bad=copy.deepcopy(evidence[0])
    bad["phase_research_final_decisions"][index][key]=value
    with pytest.raises(ValueError):
        validate(evidence,bad)


@pytest.mark.parametrize("idx,key,value",[
    (0,"status","NOT_INDEPENDENTLY_VALIDATED"),
    (1,"status","PASS_ON_PUBLISHED_SOURCE_SCOPE"),
    (2,"status","PASS_ON_PUBLISHED_SOURCE_SCOPE"),
    (3,"status","PASS_ON_PUBLISHED_SOURCE_SCOPE"),
    (4,"status","PASS_ON_PUBLISHED_SOURCE_SCOPE"),
    (5,"status","PASS_ON_PUBLISHED_SOURCE_SCOPE"),
    (7,"status","PASS_ON_PUBLISHED_SOURCE_SCOPE"),
])
def test_r6_no_independent_physical_science_inferred_from_original_luhman_catalogue_pass(evidence,idx,key,value):
    bad=copy.deepcopy(evidence[0])
    bad["r5_scientific_independent_gate_verdicts"][idx][key]=value
    with pytest.raises(ValueError):
        validate(evidence,bad)


@pytest.mark.parametrize("k,value",[
    ("overall_methodological_research_program_R1_to_R6_closed_with_explicit_limitations",False),
    ("overall_physical_Gaia_ZTF_source_stellar_variability_scientifically_validated",True),
    ("original_source_epochs_FITS_pixels_or_private_ALMA_TFM_committed",True),
    ("journal_publication_or_peer_review_claimed",True),
    ("novel_astronomical_discovery_claimed",True),
    ("final_result_category","NEW_TAURUS_VARIABLES"),
])
def test_final_stellar_science_no_go_and_not_peer_reviewed(evidence,k,value):
    bad=copy.deepcopy(evidence[0])
    bad[k]=value
    with pytest.raises(ValueError):
        validate(evidence,bad)


@pytest.mark.parametrize("deleted",[
    "## Abstract","## Resumen en español",
    "## 2. Materials, provenance and methods","## 3. Results",
    "## 4. Discussion and limitations","## 5. Conclusions",
    "24/24","0/24","591","SYNTHETIC",
    "10.3847/1538-3881/ac9da3","10.1051/0004-6361/202554522",
    "not a peer-reviewed",
])
def test_final_manuscript_cannot_hide_essential_science_or_literature(evidence,deleted):
    report=evidence[1]
    assert deleted.lower() in report.lower()
    with pytest.raises(ValueError):
        validate(evidence,new_report=report.replace(deleted,""))


def test_original_source_real_figures_and_all_phase_links_are_repository_files(evidence):
    d=evidence[0]
    assert d["real_source_derived_figures"]==list(SOURCE_FIGURES)
    for path in (*SOURCE_FIGURES,*[p["source_specific_primary_report"] for p in d["phase_research_final_decisions"]]):
        assert (ROOT/path).is_file()
    assert "R6_FINAL_SCIENTIFIC_FEASIBILITY_MANUSCRIPT.md" in (ROOT/"README.md").read_text("utf8")
    assert "R6_PORTFOLIO_ES_EN.md" in (ROOT/"EMPEZAR_AQUI.md").read_text("utf8")
    assert "R6_FINAL_SCIENTIFIC_FEASIBILITY_MANUSCRIPT.md" in (
        ROOT/"research/taurus_variability/R1_TO_R6_RESEARCH_PLAN.md").read_text("utf8")


def test_frozen_research_baseline_no_false_future_R6_merge_revision(evidence):
    d=evidence[0]
    assert len(d["r6_source_R5_integrated_baseline_main_sha"])==40
    assert "05340f6fea6c524e2067d578ed49efdacb9945f5" in evidence[1]
    assert "eventual" in evidence[1].lower()
    assert d["journal_publication_or_peer_review_claimed"] is False
    assert validate(evidence)["astrophysical_discovery_claimed"] is False
