"""Immutable original R3 source counts anchor all published real R4 cadence results.

These tests do not use real ZTF individual timestamps or photometry, do
not infer a physical Gaia-ZTF star identity or permit real periodograms.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts.audit_taurus_r4_cadence_feasibility import (
    EVIDENCE,FIGURE,REPORT,audit_r4_repo,validate_r4_permanent_evidence,
)
from scripts.run_taurus_r4_sampling_window_feasibility import run_r4_from_repo

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def original():
    data=json.loads((ROOT/EVIDENCE).read_text("utf8"))
    svg=(ROOT/FIGURE).read_text("utf8")
    report=(ROOT/REPORT).read_text("utf8")
    expected=run_r4_from_repo(ROOT)
    return data,svg,report,expected


def test_r4_source_locked_real_cadence_paper_receipt_validates_offline():
    a=audit_r4_repo(ROOT)
    assert a["status"]=="R4_ORIGINAL_SOURCE_SAMPLING_BINS_VERIFIED_AND_SYNTHETIC_WINDOW_DISTINCT__NO_REAL_PERIODS"
    assert a["original_successful_survey_source_OIDs"]==3
    assert a["original_unavailable_archive_OIDs"]==3
    assert a["original_accepted_good_visit_count"]==591
    assert a["real_series_with_two_consecutive_365day_empty_bins"]==2
    assert a["physical_gaia_ztf_source_matches_confirmed"]==0
    assert a["original_true_one_day_spectral_window_measured"] is False
    assert a["synthetic_window_example_not_a_star_period"] is True
    assert a["original_source_figure_source_cells_checked"]==27


@pytest.mark.parametrize("k,v",[
    ("source_r4_actions_artifact_id",0),
    ("source_r4_actions_zip_sha256","0"*64),
    ("source_r4_original_derived_only_json_sha256","0"*64),
    ("source_original_qc_accepted_visits",592),
    ("underlying_original_DR24_OIDs_failed_by_timeout_twice",0),
    ("source_original_context_24_gaia_id_to_ztf_physical_matches_authenticated",1),
    ("real_spectral_window_recovered_from_exact_source_timestamps",True),
    ("real_stellar_period_or_variability_claimed",True),
    ("r4_physical_star_variability_blocked",False),
    ("year_bins_are_relative_to_each_individual_sources_first_accepted_epoch_not_calendar_aligned",False),
])
def test_r4_source_receipt_claims_cannot_be_altered(original,k,v):
    data,svg,report,expected=original
    bad=copy.deepcopy(data)
    bad[k]=v
    with pytest.raises(ValueError):
        validate_r4_permanent_evidence(bad,svg,report,expected)


@pytest.mark.parametrize("j,k,v",[
    (0,"quality_accepted_visits",80),
    (0,"original_relative_365day_bin_counts",[23,33,0,0,10,5]),
    (0,"strictly_SYNTHETIC_constructed_daily_grid_one_day_window_power",0.5),
    (0,"strictly_SYNTHETIC_constructed_subday_diverse_one_day_window_power",0.991),
    (0,"measured_real_one_day_window_power",0.9),
    (1,"original_ztf_oid","unregistered"),
    (2,"first_to_last_accepted_span_days",100.0),
    (2,"max_consecutive_genuine_zero_relative_bins",2),
    (2,"physically_identified_gaia_counterpart",True),
])
def test_original_real_source_annual_bins_and_distinct_synthetic_scores_locked(original,j,k,v):
    data,svg,report,expected=original
    bad=copy.deepcopy(data)
    bad["original_real_source_observations"][j][k]=v
    with pytest.raises(ValueError):
        validate_r4_permanent_evidence(bad,svg,report,expected)


@pytest.mark.parametrize("j,k,v",[
    (0,"quality_accepted_visits",0),
    (0,"archive_access","NEGATIVE_STAR"),
    (1,"original_ztf_oid","12345"),
    (2,"physically_identified_gaia_counterpart",True),
])
def test_timeout_not_permitted_to_become_zero_or_verified_gaia_star(original,j,k,v):
    data,svg,report,expected=original
    bad=copy.deepcopy(data)
    bad["original_unavailable_source_OIDs"][j][k]=v
    with pytest.raises(ValueError):
        validate_r4_permanent_evidence(bad,svg,report,expected)


@pytest.mark.parametrize("old,new",[
    ('data-count="23"','data-count="24"'),
    ('data-state="ARCHIVE_TIMEOUT_UNKNOWN"','data-state="ZERO_ORIGINAL_VISITS"'),
    ('data-state="OUTSIDE_SOURCE_SPAN"','data-count="0"'),
    ('591 genuine QC visits','592 genuine QC visits'),
    ('not a periodogram','genuine FT Tau periodogram'),
])
def test_original_source_quantitative_figure_fails_on_faked_evidence(original,old,new):
    data,svg,report,expected=original
    assert old in svg
    with pytest.raises(ValueError):
        validate_r4_permanent_evidence(data,svg.replace(old,new,1),report,expected)


def test_original_source_chart_has_no_raw_telescope_pixels_external_js_or_actual_periodogram(original):
    data,svg,report,expected=original
    assert "<image" not in svg
    assert "<script" not in svg
    assert "per-epoch" not in svg.lower() or "not real per-observation timestamps" in svg
    assert "NOT synchronized calendar bins" not in svg or "not common calendar" in svg.lower()
    assert report.count("SYNTHETIC")>=4
    assert all("measured_real_one_day_window_power" in s for s in (
        data["original_real_source_observations"][0],data["original_unavailable_source_OIDs"][0]))
    assert validate_r4_permanent_evidence(data,svg,report,expected)["original_source_figure_source_cells_checked"]==27


def test_independent_r4_numerical_source_provenance_and_readme_reachable():
    assert (ROOT/"research/taurus_variability/R4_REAL_ZTF_SAMPLING_WINDOW_METHOD_PREREGISTRATION.md").is_file()
    assert (ROOT/"src/stellarforge/r4_sampling_window_feasibility.py").is_file()
    assert (ROOT/"src/stellarforge/r4_sampling_visual.py").is_file()
    assert (ROOT/"scripts/run_taurus_r4_sampling_window_feasibility.py").is_file()
    readme=(ROOT/"README.md").read_text("utf8")
    assert "R4_REAL_ZTF_SAMPLING_WINDOW_FEASIBILITY_RESULTS.md" in readme
    assert "taurus-r4-original-ztf-dr24-relative-365day-cadence.svg" in readme
