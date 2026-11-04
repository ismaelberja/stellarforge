"""Reproducible numerical and science-guardrail tests for v0.4."""
import csv
import json
import math
from pathlib import Path
import pytest

np = pytest.importorskip('numpy')
pytest.importorskip('scipy')
from stellarforge.variability import (
    descriptive_features, search_period, sampling_window, analyze_normalized_file,
)


def series(n=120, seed=8, period=4.7, amplitude=0.17):
    rng = np.random.default_rng(seed)
    t = 59000 + np.sort(rng.uniform(0, 110, n))
    err = np.full(n, 0.03)
    y = 15.6 + amplitude * np.sin(2*np.pi*(t-59000)/period) + rng.normal(0, .03, n)
    return t, y, err


def test_weighted_constant_source_small_reduced_chi2():
    t = np.arange(100, dtype=float) + 58000
    y = np.full(100, 15.)
    err = np.full(100, .05)
    out = descriptive_features(t, y, err)
    assert out['reduced_chi2_constant'] == 0
    assert out['robust_amplitude_p95_p05_mag'] == 0
    assert out['tail_asymmetry_mag'] is None
    assert out['photometric_variability_diagnosis'] == 'unassigned'


def test_weighted_statistics_and_scatter_are_finite():
    t, y, err = series()
    out = descriptive_features(t, y, err)
    assert out['n_epochs'] == 120
    assert out['span_days'] > 100
    assert out['reduced_chi2_constant'] > 5
    assert out['normalized_intrinsic_variance_proxy'] > 0
    assert 0.1 < out['robust_amplitude_p95_p05_mag'] < 1


def test_asymmetry_suggests_brightening_or_dimming_but_does_not_label():
    t = 58000 + np.arange(100.)
    err = np.full(100, .05)
    baseline = np.full(100, 16.)
    fade = baseline.copy(); fade[::5] += 1.
    brighten = baseline.copy(); brighten[::5] -= 1.
    assert descriptive_features(t, fade, err)['tail_asymmetry_mag'] > .6
    assert descriptive_features(t, brighten, err)['tail_asymmetry_mag'] < -.6
    assert descriptive_features(t, fade, err)['photometric_variability_diagnosis'] == 'unassigned'


def test_recovery_of_injected_period():
    t, y, err = series()
    out = search_period(t, y, err, minimum_period_days=2., maximum_period_days=10.)
    assert out['physical_period_confirmed'] is False
    assert out['formal_false_alarm_probability'] is None
    assert abs(out['best_period_days'] - 4.7) / 4.7 < 0.03
    assert out['peak_power_normalized'] > .3
    assert out['frequency_grid_points'] >= 300


def test_permutation_diagnostic_is_not_a_formal_fap():
    t,y,e=series(95)
    out=search_period(t,y,e,minimum_period_days=2,maximum_period_days=10,permutations=10,random_seed=99)
    assert out['permutation_trials'] == 10
    assert 0 < out['permutation_peak_exceedance_white_noise_diagnostic'] <= 1
    assert out['formal_false_alarm_probability'] is None


def test_sampling_window_matches_mathematical_definition():
    t=np.array([0.,1.,2.,3.]); frequencies=np.array([1.,.25])
    power=sampling_window(t, frequencies,np)
    assert power[0] == pytest.approx(1.)
    assert power[1] == pytest.approx(0., abs=1e-12)


@pytest.mark.parametrize('minimum,maximum',[(5,5),(0.1,2),(1,2001),(40,2)])
def test_invalid_period_ranges_rejected(minimum,maximum):
    t,y,e=series()
    with pytest.raises(ValueError):
        search_period(t,y,e,minimum_period_days=minimum,maximum_period_days=maximum)


def test_baseline_too_short_rejected():
    t,y,e=series(90)
    with pytest.raises(ValueError,match='twice'):
        search_period(t,y,e,maximum_period_days=100)


def test_very_dense_grid_rejected():
    t,y,e=series(100)
    t=np.linspace(59000, 99000, 100)
    with pytest.raises(ValueError,match='16,000'):
        search_period(t,y,e,minimum_period_days=.2,maximum_period_days=30)


def test_invalid_photometry_rejected():
    t,y,e=series()
    with pytest.raises(ValueError):
        descriptive_features(t,y,np.zeros(len(e)))
    t2=t.copy();t2[4]=t2[0]
    with pytest.raises(ValueError):
        descriptive_features(t2,y,e)
    y2=y.copy();y2[0]=np.nan
    with pytest.raises(ValueError):
        descriptive_features(t,y2,e)


def test_real_like_normalized_file_never_infers_physics(tmp_path):
    t,y,e=series()
    input_path=tmp_path/'normalized.csv'
    cols=['oid','band','time_value','time_scale','magnitude','magnitude_error','catflags']
    with input_path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
        for i in range(len(t)):
            w.writerow(dict(oid='123456789012345',band='r',time_value=t[i],time_scale='MJD',magnitude=y[i],magnitude_error=e[i],catflags=0))
        for i in range(8):
            w.writerow(dict(oid='876543210987654',band='g',time_value=58000+i*2,time_scale='MJD',magnitude=17,magnitude_error=.02,catflags=0))
    out=tmp_path/'out.json'
    audit=analyze_normalized_file(input_path,out,min_period=2,max_period=10)
    assert out.is_file()
    assert json.loads(out.read_text()) == audit
    assert audit['scientific_membership_verified'] is False
    assert audit['astrophysical_classifications_produced'] is False
    assert len(audit['curves']) == 2
    assert audit['curves'][0]['status'] == 'provisional_variability_diagnostics'
    assert audit['curves'][1]['status'] == 'insufficient_epochs'
    assert audit['curves'][0]['period']['physical_period_confirmed'] is False


def test_separate_object_id_filter_and_time_scales(tmp_path):
    input_path=tmp_path/'normal.csv'
    with input_path.open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['oid','band','time_value','time_scale','magnitude','magnitude_error','catflags'])
        for oid,band,scale in [('101','g','MJD'),('101','r','MJD'),('101','g','HJD'),('202','g','MJD')]:
            for i in range(4):w.writerow([oid,band,58000+i,scale,15,.05,0])
    out=analyze_normalized_file(input_path,tmp_path/'audit.json')
    assert out['n_curves']==4
    assert all(curve['status']=='insufficient_epochs' for curve in out['curves'])


def test_normalized_file_with_flagged_epoch_fails_closed(tmp_path):
    p=tmp_path/'input.csv'
    p.write_text('oid,band,time_value,time_scale,magnitude,magnitude_error,catflags\n1,g,59000,MJD,15,.01,32768\n')
    with pytest.raises(ValueError,match='Masked'):
        analyze_normalized_file(p,tmp_path/'output.json')


def test_normalized_file_with_missing_columns_fails_closed(tmp_path):
    p=tmp_path/'input.csv';p.write_text('oid,band,magnitude\n1,g,15\n')
    with pytest.raises(ValueError,match='Missing normalized'):
        analyze_normalized_file(p,tmp_path/'out.json')


def test_irregular_noisy_and_no_lightcurve_fabrication(tmp_path):
    fixture=Path(__file__).resolve().parents[1] / 'examples' / 'SYNTHETIC_output' / 'photometry_good.csv'
    out=analyze_normalized_file(fixture,tmp_path/'realistic.json',min_period=2,max_period=20)
    assert out['n_curves'] == 3
    assert out['data_type'] == 'unverified_source_association'
    assert all('source_association' in entry and entry['source_association'] == 'unverified' for entry in out['curves'])
    assert all('physical_period_confirmed' not in entry or not entry['physical_period_confirmed'] for entry in out['curves'])