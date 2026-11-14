"""R4: all actual ZTF counts are from original immutable R3 receipts.

Synthetic schedules *never* represent original per-epoch ZTF timestamps
or physical FT Tau/CIDA 11 stellar light curves.
"""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from scripts.run_taurus_r4_sampling_window_feasibility import run_r4_from_repo
from stellarforge.r4_sampling_visual import original_zft_r4_coverage_svg
from stellarforge.r4_sampling_window_feasibility import (
    R4_STUDY_STATUS, YEAR_BIN_DAYS, FIXED_GROUPS,
    r4_technical_sampling_feasibility,
    synthetic_hypothetical_visit_offsets,
    synthetic_one_day_window_power,
)
from scripts.audit_taurus_r3_six_original_source_receipts import (
    audit_r3_original_six_source_receipts, FIRST_PATH, RETRY_PATH,
)

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def evidence():
    first=json.loads((ROOT/FIRST_PATH).read_text("utf8"))
    retry=json.loads((ROOT/RETRY_PATH).read_text("utf8"))
    gate=audit_r3_original_six_source_receipts(ROOT)
    return first,retry,gate


@pytest.fixture(scope="module")
def r4(evidence):
    return r4_technical_sampling_feasibility(*evidence)


def test_r4_pins_real_r3_observation_counts_and_no_physical_source_assertions(r4):
    assert r4["phase"]==R4_STUDY_STATUS
    assert r4["input_original_DR24_oid_count"]==6
    assert r4["real_original_ztf_OIDs_with_QC_annual_bins"]==3
    assert r4["original_ztf_OIDs_with_unavailable_server_responses"]==3
    assert r4["n_original_ztf_raw_rows_quality_screened"]==684
    assert r4["n_original_ztf_accepted_epochs"]==591
    assert r4["n_original_ztf_bit15_masked_rows"]==93
    assert r4["number_real_series_with_two_consecutive_empty_relative_year_bins"]==2
    assert r4["number_real_series_with_all_relative_year_bins_nonempty"]==1
    assert r4["observed_frequency_window_calculated_from_original_visit_timestamps"] is False
    assert r4["only_deterministic_hypothetical_synthetic_1day_window_constructed"] is True
    assert r4["original_physical_Gaia_ZTF_identifications_confirmed"]==0
    assert r4["new_variable_stars_or_companions_confirmed"]==0
    assert r4["r4_physical_stellar_variability_science_go"] is False


@pytest.mark.parametrize("source_index, oid, band, accepted, gaps, bins",[
    (0,"1605115300003377","g",70,2,[23,33,0,0,10,4]),
    (1,"1605215300005161","r",117,2,[22,49,0,0,12,11,23]),
    (2,"609108400001155","g",404,0,[61,79,80,34,46,43,51,10]),
])
def test_real_365day_bin_counts_reproduced_without_inventing_timestamps(r4,source_index,oid,band,accepted,gaps,bins):
    s=r4["source_observations"][source_index]
    assert (s["original_ztf_oid"],s["original_ztf_filter"])==(oid,band)
    assert s["technical_source_qc_accepted_epochs"]==accepted
    assert s["original_relative_365day_bins_anchored_at_first_QC_epoch"]==bins
    assert s["longest_consecutive_empty_relative_365day_bins"]==gaps
    assert sum(bins)==accepted
    assert s["mean_QC_visits_per_365day_over_total_span"]>0
    assert s["source_quality_retention_fraction"]>0.8
    assert s["original_physical_gaia_ztf_counterpart_confirmed"] is False
    assert s["scientific_stellar_period_analysis_authorized"] is False
    assert s["real_1day_spectral_window_computable_from_committed_R3_bins"] is False
    assert s["synthetic_window_scores_are_not_observed_and_not_true_bounds"] is True


def test_archival_timeouts_are_unknown_not_zero_observations(r4):
    unknown=r4["source_observations"][3:]
    assert [s["original_ztf_oid"] for s in unknown]==[v[2] for v in FIXED_GROUPS[3:]]
    assert all(s["technical_source_outcome"]=="ARCHIVE_UNAVAILABLE_TWO_PROVIDER_TIMEOUTS" for s in unknown)
    assert all(s["technical_source_qc_accepted_epochs"] is None for s in unknown)
    assert all(s["n_observed_relative_365day_bins"] is None for s in unknown)
    assert all(not s["synthetic_1day_window_example_available"] for s in unknown)


@pytest.mark.parametrize("oid,bins,span",[
    ("1605115300003377",[23,33,0,0,10,4],1870.876898),
    ("1605215300005161",[22,49,0,0,12,11,23],2528.096678),
    ("609108400001155",[61,79,80,34,46,43,51,10],2617.952292),
])
def test_two_purely_synthetic_schedules_preserve_actual_counts_and_span_but_window_differs(oid,bins,span):
    daily=synthetic_hypothetical_visit_offsets(bins,span,oid,construction="SYNTHETIC_DAILY_GRID")
    diverse=synthetic_hypothetical_visit_offsets(bins,span,oid,construction="SYNTHETIC_SUBDAY_DIVERSE")
    assert daily==synthetic_hypothetical_visit_offsets(bins,span,oid,construction="SYNTHETIC_DAILY_GRID")
    assert diverse==synthetic_hypothetical_visit_offsets(bins,span,oid,construction="SYNTHETIC_SUBDAY_DIVERSE")
    assert daily!=diverse
    for imaginary in (daily,diverse):
        assert len(imaginary)==sum(bins)
        assert imaginary[0]==0.0
        assert imaginary[-1]==span
        assert [sum(int(x//YEAR_BIN_DAYS)==k for x in imaginary)
                for k in range(len(bins))]==bins
        assert all(0<=x<=span for x in imaginary)
    power_daily=synthetic_one_day_window_power(daily)
    power_diverse=synthetic_one_day_window_power(diverse)
    assert 0<=power_daily<=1
    assert 0<=power_diverse<=1
    assert abs(power_daily-power_diverse)>0.1
    assert power_daily>0.95
    assert power_diverse<0.15


@pytest.mark.parametrize("counts,span,source,mode",[
    ([2,0,0],800,"123","SYNTHETIC_DAILY_GRID"),
    ([0,4,2],800,"123","SYNTHETIC_DAILY_GRID"),
    ([3,4],90,"123","SYNTHETIC_SUBDAY_DIVERSE"),
    ([3,-1,4],800,"123","SYNTHETIC_DAILY_GRID"),
    ([3,2.1,4],800,"123","SYNTHETIC_DAILY_GRID"),
    ([3,4],430,"not-an-oid","SYNTHETIC_DAILY_GRID"),
    ([3,4],430,"123","OBSERVED_REAL_ZTF_TIMES"),
])
def test_invalid_source_counts_synthetic_frequencies_or_fake_real_visits_fail(counts,span,source,mode):
    with pytest.raises(ValueError):
        synthetic_hypothetical_visit_offsets(counts,span,source,construction=mode)


@pytest.mark.parametrize("where,key,value",[
    ("first","original_http_success_sources",6),
    ("first","original_success_qc_retained_rows",0),
    ("first","original_gaia_to_ztf_physical_associations_confirmed",1),
    ("retry","n_recovered_original_public_dr24_source_csv",3),
    ("retry","original_recovery_workflow_run_id",0),
    ("r3","r3_physical_stellar_variability_science_eligible",True),
])
def test_source_provider_or_physical_gaia_claim_tampering_rejected(evidence,where,key,value):
    first,retry,gate=(copy.deepcopy(x) for x in evidence)
    if where=="first":first[key]=value
    elif where=="retry":retry[key]=value
    else:gate[key]=value
    with pytest.raises(ValueError):
        r4_technical_sampling_feasibility(first,retry,gate)


def test_swapped_survey_OIDs_or_time_bins_rejected(evidence):
    first,retry,gate=(copy.deepcopy(x) for x in evidence)
    first["per_oid_results"][0]["original_qc_365day_bin_counts"][2]=1
    with pytest.raises(ValueError):
        r4_technical_sampling_feasibility(first,retry,gate)
    first,retry,gate=(copy.deepcopy(x) for x in evidence)
    first["per_oid_results"][0]["original_frozen_ztf_oid"]="123456789"
    with pytest.raises(ValueError):
        r4_technical_sampling_feasibility(first,retry,gate)
    first,retry,gate=(copy.deepcopy(x) for x in evidence)
    first["per_oid_results"][4]["original_query_status"]="ORIGINAL_ZTF_EXACT_OID_CSV_PARSED_AND_QC_AUDITED"
    with pytest.raises(ValueError):
        r4_technical_sampling_feasibility(first,retry,gate)


def test_accessible_original_data_chart_is_not_synthetic_or_a_real_periodogram(r4):
    svg=original_zft_r4_coverage_svg(r4)
    root=ET.fromstring(svg)
    ns="{http://www.w3.org/2000/svg}"
    assert root.tag==ns+"svg"
    assert root.attrib.get("role")=="img"
    assert root.find(ns+"title") is not None
    assert root.find(ns+"desc") is not None
    assert not root.findall(".//"+ns+"script")
    assert not root.findall(".//"+ns+"image")
    assert "NOT synchronized calendar bins" in svg
    assert "spectral window" in svg
    assert "SYNTHETIC_DAILY_GRID" not in svg
    for s in r4["source_observations"]:
        oid=s["original_ztf_oid"]
        groups=[g for g in root.findall(".//"+ns+"g") if g.attrib.get("data-oid")==oid]
        if s["cadence_metric_computable"]:
            assert len(groups)==8
            expected=s["original_relative_365day_bins_anchored_at_first_QC_epoch"]
            assert [int(g.attrib["data-count"]) for g in groups if "data-count" in g.attrib]==expected
            assert sum(int(g.attrib["data-count"]) for g in groups if "data-count" in g.attrib)==s["technical_source_qc_accepted_epochs"]
        else:
            assert len(groups)==1
            assert groups[0].attrib["data-state"]=="ARCHIVE_TIMEOUT_UNKNOWN"


def test_actual_r3_receipt_offline_runner_produces_same_source_locked_r4(r4):
    assert run_r4_from_repo(ROOT)==r4
    assert not r4["real_star_periodogram_or_astrophysical_period_reported"]
    assert r4["original_bins_anchored_to_individual_first_good_visit_not_same_calendar_start"]
