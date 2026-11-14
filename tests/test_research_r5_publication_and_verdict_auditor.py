"""R5 publication, original-source denominator figure, prior-work references and NO-GO guardrails."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts.audit_taurus_r5_critical_falsification import (
    R5_REPORT,R5_LEDGER,R5_FIGURE,audit_r5_repo,validate_r5_published_result,
)
from stellarforge.r5_critical_falsification import build_r5_critical_falsification

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def pub():
    expected=build_r5_critical_falsification(ROOT)
    final=json.loads((ROOT/R5_LEDGER).read_text("utf8"))
    svg=(ROOT/R5_FIGURE).read_text("utf8")
    report=(ROOT/R5_REPORT).read_text("utf8")
    return final,svg,report,expected


def test_R5_original_sources_exact_and_full_8_gate_acceptance_fail_closed():
    actual=audit_r5_repo(ROOT)
    assert actual["status"]=="R5_CRITICAL_SELECTION_AND_PRIOR_LITERATURE_AUDITED__GAIA_ZTF_PHYSICAL_SOURCE_VALIDATION_NOT_MET"
    assert actual["source_ratio_count"]==12
    assert actual["noninterchangeable_gaia_ztf_epoch_denominators"]==[24,6,684]
    assert actual["original_publisher_gaia_ids_verified"]==24
    assert actual["original_DR24_source_rows_bit15_accepted"]==591
    assert actual["source_fig_original_count_panels_verified"]==3
    assert actual["scientific_acceptance_gates_documented"]==8
    assert actual["independent_physical_gaia_to_ztf_counterparts_confirmed"]==0
    assert actual["physical_source_variability_not_inferred"] is True
    assert actual["r6_inconclusive_methods_report_suitable_for_completion"] is True
    assert actual["new_asterisk_astrophysical_discovery_claimed"] is False


def test_R5_permanent_source_references_and_science_gate_order_exact(pub):
    final,svg,report,expected=pub
    result=validate_r5_published_result(final,svg,report,expected)
    assert result["source_ratio_count"]==12
    assert result["scientific_acceptance_gates_documented"]==8
    assert len(final["external_official_literature_urls"])==6
    assert len(final["physical_scientific_acceptance_gates"])==8
    assert "catflags = 0" in report
    assert "Mas et al." in report
    assert "24/532" in report
    assert "24/467" in report
    assert "0/24" in report
    assert "true" not in str(final["interpretation_flags"]["r5_independent_physical_gaia_ztf_source_validation_passed"]).lower()


@pytest.mark.parametrize("key,value",[
    ("r5_review_verdict","R5_NEW_VARIABLE_DISCOVERED"),
    ("source_claims_are_original_source_derived_only",False),
    ("individual_ZTF_original_measurements_or_times_committed",True),
    ("unpublished_private_ALMA_TFM_data_committed",True),
])
def test_unverified_stellar_claim_or_raw_data_rejected(pub,key,value):
    final,svg,report,expected=pub
    changed=copy.deepcopy(final)
    changed[key]=value
    with pytest.raises(ValueError):
        validate_r5_published_result(changed,svg,report,expected)


@pytest.mark.parametrize("key,value",[
    ("r5_independent_physical_gaia_ztf_source_validation_passed",True),
    ("observational_source_specific_physical_variability_established",True),
    ("r6_new_stellar_variable_or_companion_claim_allowed",True),
    ("r6_taurus_population_variable_incidence_report_allowed",True),
    ("r6_conservative_methodological_inconclusive_report_allowed",False),
    ("real_one_day_ztf_spectral_window_measured",True),
    ("original_bit15_mask_implies_catflags_strict_zero",True),
    ("true_original_provider_timeout_implies_zero_real_source_visits",True),
])
def test_scientifically_unqualified_result_field_is_blocked(pub,key,value):
    final,svg,report,expected=pub
    changed=copy.deepcopy(final)
    changed["interpretation_flags"][key]=value
    with pytest.raises(ValueError):
        validate_r5_published_result(changed,svg,report,expected)


@pytest.mark.parametrize("idx,key,value",[
    (0,"denominator",24),
    (0,"numerator",25),
    (0,"percent_descriptive_only",100),
    (6,"numerator",1),
    (7,"numerator",6),
    (9,"numerator",684),
    (11,"denominator",24),
])
def test_gaia_oid_and_epoch_ratios_cannot_be_interchanged(pub,idx,key,value):
    final,svg,report,expected=pub
    changed=copy.deepcopy(final)
    changed["ratios_descriptive_not_population"][idx][key]=value
    with pytest.raises(ValueError):
        validate_r5_published_result(changed,svg,report,expected)


@pytest.mark.parametrize("idx,key,value",[
    (0,"status","NOT_INDEPENDENTLY_VALIDATED"),
    (1,"status","PASS_ON_PUBLISHED_SOURCE_SCOPE"),
    (2,"status","PASS_ON_PUBLISHED_SOURCE_SCOPE"),
    (3,"status","PASS_ON_PUBLISHED_SOURCE_SCOPE"),
    (5,"status","PASS_ON_PUBLISHED_SOURCE_SCOPE"),
    (7,"status","PASS_ON_PUBLISHED_SOURCE_SCOPE"),
])
def test_falsification_gates_cannot_be_promoted_without_new_independent_data(pub,idx,key,value):
    final,svg,report,expected=pub
    changed=copy.deepcopy(final)
    changed["physical_scientific_acceptance_gates"][idx][key]=value
    with pytest.raises(ValueError):
        validate_r5_published_result(changed,svg,report,expected)


@pytest.mark.parametrize("old,new",[
    ('data-denominator="24"','data-denominator="684"'),
    ('data-panel="2"','data-panel="1"'),
    ('data-count="591"','data-count="684"'),
    ('data-count="0"','data-count="1"'),
    ('data-base="684"','data-base="6"'),
    ('NOT VERIFIED','NEW VARIABLE STAR FOUND'),
    ('never a single attrition funnel','unqualified sample funnel'),
])
def test_original_R5_source_figure_rejects_wrong_denominator_or_fictitious_stellar_identity(pub,old,new):
    final,svg,report,expected=pub
    assert old in svg
    with pytest.raises(ValueError):
        validate_r5_published_result(final,svg.replace(old,new,1),report,expected)


def test_original_external_literature_does_not_supply_new_physical_source_matches(pub):
    final,svg,report,expected=pub
    for key in range(6):
        assert final["external_official_literature_urls"][key]["independently_authenticates_physical_gaia_ztf_source"] is False
    changed=copy.deepcopy(final)
    changed["external_official_literature_urls"][1]["independently_authenticates_physical_gaia_ztf_source"]=True
    with pytest.raises(ValueError):
        validate_r5_published_result(changed,svg,report,expected)


@pytest.mark.parametrize("missing",[
    "24/532","22/24","591/684","93/684","2/3",
    "catflags = 0","Mas et al.","one-day","R6",
])
def test_original_method_report_is_not_allowed_to_hide_scientific_limitations(pub,missing):
    final,svg,report,expected=pub
    assert missing in report
    with pytest.raises(ValueError):
        validate_r5_published_result(final,svg,report.replace(missing,""),expected)
