"""Mathematical tests use SYNTHETIC sample times only, not Taurus observations."""
import math
import pytest
from stellarforge.cadence import clean_epochs, window_coverage_fraction, cadence_report


def approximate_fraction(ts,d,k,grid=12000):
    ts=sorted(ts)
    lo,hi=ts[0],ts[-1]-d
    total=0
    for j in range(grid):
        start=lo+(hi-lo)*(j+.5)/grid
        total+=sum(start<=x<=start+d for x in ts)>=k
    return total/grid


@pytest.mark.parametrize('t,d,k,expected',[ 
    ([0,1,2,3],1.5,2,1/3),
    ([0,1,2,3],1.5,3,0),
    ([0,1,2,3],2.5,2,1),
    ([0,1,2,3],.9,2,0),
    ([0,1,2,3],3,2,1),
    ([0,1,2,3],2.2,3,0),
])
def test_analytically_solved_cases(t,d,k,expected):
    assert window_coverage_fraction(t,d,minimum_points=k)==pytest.approx(expected,abs=1e-9)


def test_matches_independent_numerical_quadrature():
    ts=[0,.1,2.0,2.2,2.5,5,10,11,11.1,22.0,32,32.5]
    for d,k in [(1,2),(2,3),(6,2),(14,3)]:
        assert window_coverage_fraction(ts,d,minimum_points=k)==pytest.approx(
            approximate_fraction(ts,d,k),abs=.001)


def test_invariant_to_time_origin():
    t=[.01,1.3,9.8,10.1,25.5]
    assert window_coverage_fraction(t,5)==pytest.approx(window_coverage_fraction([x+59000 for x in t],5))


def test_seasons_and_sparse_input():
    r=cadence_report([0,1,2,80,80.5,170],durations_days=[5,10])
    assert r['n_observing_seasons_by_gap_heuristic']==3
    assert r['max_gap_days']==pytest.approx(89.5)
    assert r['event_duration_days_to_exact_cadence_window_fraction']['5.0']>=0
    assert cadence_report([1],durations_days=[2])['event_duration_days_to_exact_cadence_window_fraction']['2.0'] is None


@pytest.mark.parametrize('bad',[-1,0,float('nan'),float('inf')])
def test_invalid_duration_refused(bad):
    with pytest.raises(ValueError):window_coverage_fraction([0,1,2],bad)


def test_input_restrictions():
    with pytest.raises(ValueError):clean_epochs([0,1,1])
    with pytest.raises(ValueError):clean_epochs([0,float('nan')])
    with pytest.raises(ValueError):window_coverage_fraction([0,1,2],1,minimum_points=0)
    with pytest.raises(ValueError):cadence_report([0,1],durations_days=[1,1])
    with pytest.raises(ValueError):cadence_report([0,1],season_gap_days=-1)


def test_never_measures_actual_photometric_detection():
    r=cadence_report([0,2,3,18,19,30],durations_days=[2,5,15])
    assert not r['science_claim']
    assert 'survey_completeness' in r['not_equivalent_to']
    assert all((x is None or 0<=x<=1) for x in r['event_duration_days_to_exact_cadence_window_fraction'].values())