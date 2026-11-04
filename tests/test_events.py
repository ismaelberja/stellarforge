"""Synthetic fixtures for morphology screening — NOT real Taurus findings."""
import csv
import json
import numpy as np
import pytest

from stellarforge.events import magnitude_asymmetry_m, screen_events, screen_normalized_file


def synthetic(seed=77, kind="noise"):
    rng = np.random.default_rng(seed)
    t = np.sort(rng.uniform(0, 125, 260))
    y = 14.3 + rng.normal(0, .015, size=len(t))
    e = np.full(len(t), .012)
    if kind == "dipper":
        y[(t >= 31) & (t <= 37)] += .52
    if kind == "burster":
        y[(t >= 73) & (t <= 79)] -= .56
    return t, y, e


def test_no_events_in_plain_noise():
    a = screen_events(*synthetic())
    assert a["status"] == "exploratory_event_screen_completed"
    assert not a["fading_events"] and not a["brightening_events"]
    assert a["physical_cause_identified"] is False


def test_fading_episode_candidate_and_sign_of_m():
    a = screen_events(*synthetic(kind="dipper"))
    assert len(a["fading_events"]) == 1
    event = a["fading_events"][0]
    assert 31 <= event["start_time"] <= event["end_time"] <= 37
    assert event["n_epochs"] >= 2
    assert event["max_magnitude_excursion"] > .4
    assert event["direction"] == "fading"
    assert a["reference_statistic_M"] > .2
    assert a["discovery_claim"] is False


def test_brightening_episode_candidate_and_sign_of_m():
    a = screen_events(*synthetic(kind="burster"))
    assert len(a["brightening_events"]) == 1
    assert a["brightening_events"][0]["max_magnitude_excursion"] > .4
    assert a["reference_statistic_M"] < -.2
    assert not a["fading_events"]


def test_short_one_point_event_rejected():
    t, y, e = synthetic()
    y[50] -= .5
    r = screen_events(t, y, e)
    assert r["n_brightening_event_candidates"] == 0
    assert r["n_brightening_trigger_epochs"] == 1


def test_consecutive_events_separated_by_cadence_gap():
    rng = np.random.default_rng(4)
    t = np.sort(np.r_[np.arange(0, 35, .5), np.arange(90, 125, .5)])
    y = rng.normal(14, .012, len(t))
    e = np.full(len(t), .01)
    y[(t >= 12) & (t <= 14)] += .5
    y[(t >= 103) & (t <= 105)] += .5
    a = screen_events(t, y, e)
    assert len(a["fading_events"]) == 2


def test_high_errors_suppress_claims():
    t, y, e = synthetic(kind="dipper")
    e.fill(.4)
    r = screen_events(t, y, e)
    assert r["n_fading_event_candidates"] == 0


def test_too_few_epochs_report_inconclusive():
    t, y, e = synthetic()
    a = screen_events(t[:21], y[:21], e[:21], min_epochs=30)
    assert a["status"] == "insufficient_epochs"
    assert a["reference_statistic_M"] is not None
    assert a["fading_events"] == []


@pytest.mark.parametrize("wrong", [
    ([1.0, 1.0, 2.0], [15, 15, 15], [.1]*3),
    ([1, 2, 3], [14, float("nan"), 14], [.1]*3),
    ([1, 2, 3], [14, 14, 14], [.1, -1, .1]),
    ([1, 2], [14], [.1, .1]),
])
def test_malformed_photometry_rejected(wrong):
    with pytest.raises(ValueError):
        screen_events(*wrong)


@pytest.mark.parametrize("arg,value", [
    ("significance_threshold", 0),
    ("significance_threshold", float("nan")),
    ("max_gap_days", -1),
    ("min_amplitude_mag", 0),
    ("min_epochs", 2),
])
def test_invalid_parameters_rejected(arg, value):
    kw = {arg:value}
    with pytest.raises(ValueError):
        screen_events(*synthetic(), **kw)


def test_constant_curve_m_undefined():
    assert magnitude_asymmetry_m([11]*40) is None


def test_m_valid_signs_and_missingness():
    assert magnitude_asymmetry_m([14]*29+[15]*6) > 0
    assert magnitude_asymmetry_m([14]*29+[13]*6) < 0
    assert magnitude_asymmetry_m([14]*15) is None


def test_normalized_input_not_cross_band_combined(tmp_path):
    source = tmp_path / "SYNTHETIC_a.csv"
    t,y,e=synthetic(kind="dipper")
    fields=["oid","band","time_value","time_scale","magnitude","magnitude_error","catflags"]
    with source.open("w",newline="") as h:
        w=csv.DictWriter(h,fieldnames=fields);w.writeheader()
        for idx,(ti,yi,ei) in enumerate(zip(t,y,e)):
            w.writerow({"oid":"98765","band":"g","time_value":ti,"time_scale":"MJD","magnitude":yi,"magnitude_error":ei,"catflags":0})
            w.writerow({"oid":"98765","band":"r","time_value":ti+.0001,"time_scale":"MJD","magnitude":14.0,"magnitude_error":ei,"catflags":0})
    output=tmp_path/'events.json'
    results=screen_normalized_file(source,output)
    assert results['n_curves']==2
    assert results['dataset_type']=='SYNTHETIC_fixture'
    g,r=results['curves']
    assert g['band']=='g' and r['band']=='r'
    assert g['n_fading_event_candidates']==1
    assert r['n_fading_event_candidates']==0
    assert results['confirmed_dipper_or_burster_count'] is None
    assert json.loads(output.read_text())['input_sha256']==results['input_sha256']