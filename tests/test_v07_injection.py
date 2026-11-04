"""Engineering fixtures only. None of these test inputs are real observations."""
import math
import numpy as np
import pytest
from stellarforge.injection import Episode, inject_episode, exposure_coverage, wilson_interval
from stellarforge.selection_function import TrialConfig, seasonal_times, simulate_trial, benchmark, save_benchmark


def test_injects_fading_without_touching_timestamps():
    t = (0., 1., 2., 3., 4.)
    y, delta = inject_episode(t, (15.,) * 5, Episode(2., 2., .5))
    assert delta == (0., .5, .5, .5, 0.)
    assert y == (15., 15.5, 15.5, 15.5, 15.)
    assert t == (0.,1.,2.,3.,4.)


def test_brightening_is_negative_magnitude_excursion():
    result,delta=inject_episode([2.], [16.], Episode(2., 1., .6, "brightening"))
    assert result[0] == pytest.approx(15.4)
    assert delta[0] == pytest.approx(-.6)


def test_gaussian_full_width_half_max():
    _, delta=inject_episode([-2., -1., 0., 1., 2.], [0.] * 5, Episode(0., 2., .8, shape="gaussian"))
    assert delta[2] == pytest.approx(.8)
    assert delta[1] == pytest.approx(.4)
    assert delta[3] == pytest.approx(.4)
    assert delta[0] < delta[1]


@pytest.mark.parametrize("episode", [
    Episode(1.,2.,.3),Episode(1.,2.,.3,'brightening','gaussian')
])
def test_zero_change_far_from_event(episode):
    _,d=inject_episode([100.,101.],[0.,0.],episode)
    assert all(abs(x)<1e-10 for x in d)


@pytest.mark.parametrize('bad',[
    (0.,0.,.3,'fading','box'),
    (0.,1.,-.2,'fading','box'),
    (float('inf'),1.,.2,'fading','box'),
    (0.,1.,.3,'neither','box'),
    (0.,1.,.3,'fading','triangle'),
])
def test_rejects_invalid_episode(bad):
    with pytest.raises(ValueError): Episode(*bad)


def test_invalid_measurements_rejected():
    with pytest.raises(ValueError): inject_episode([0.,1.],[15.],Episode(0.,1.,.5))
    with pytest.raises(ValueError): inject_episode([0.,float('nan')],[15.,15.],Episode(0.,1.,.5))
    with pytest.raises(ValueError): inject_episode([],[],Episode(0.,1.,.5))


@pytest.mark.parametrize("successes,trials", [(-1, 12),(13,12),(1,-2),(2.1,5),(True,6)])
def test_invalid_wilson_counts(successes,trials):
    with pytest.raises(ValueError):wilson_interval(successes,trials)


def test_wilson_zero_trials_and_extremes():
    assert wilson_interval(0,0) is None
    lo,hi=wilson_interval(0,50)
    assert lo==0 and 0<hi<.1
    lo,hi=wilson_interval(50,50)
    assert .9<lo<1 and hi==1
    lo,hi=wilson_interval(25,50)
    assert lo<.5<hi


def test_wilson_confidence_validation():
    for confidence in [0.,1.,float('nan')]:
        with pytest.raises(ValueError): wilson_interval(1,2,confidence)


def test_exposure_is_not_detection():
    ev=Episode(10.,2.,.4)
    miss=exposure_coverage([1.,2.,3.,20.],ev)
    seen=exposure_coverage([9.,10.,11.,20.],ev)
    assert not miss['at_least_minimum_epochs_sampled']
    assert seen['at_least_minimum_epochs_sampled']
    assert seen['epochs_above_fractional_depth']==3


def test_no_signal_has_no_exposure_coverage():
    assert exposure_coverage([9.,10.,11.],Episode(10.,2.,0.))['epochs_above_fractional_depth']==0


def test_seasonal_cadence_is_reproducible_and_gapped():
    a=seasonal_times(np.random.default_rng(1),epochs=120)
    b=seasonal_times(np.random.default_rng(1),epochs=120)
    assert np.array_equal(a,b)
    assert len(a)==120 and np.all(np.diff(a)>0)
    assert max(np.diff(a))>200


def test_simulation_recovers_strong_fading():
    trials=[simulate_trial(np.random.default_rng(i),TrialConfig(.8,15,.02)) for i in range(4)]
    assert all(r['passed_review'] for r in trials)


def test_simulation_systematics_are_vetoed():
    trials=[simulate_trial(np.random.default_rng(i),TrialConfig(.8,15,.02,kind='correlated_field_artifact')) for i in range(4)]
    assert all(x['raw_any_trigger'] and x['field_artifact_vetoed'] and not x['passed_review'] for x in trials)


def test_no_signal_not_promoted():
    trials=[simulate_trial(np.random.default_rng(i),TrialConfig(0.,15,.02,kind='constant_star')) for i in range(4)]
    assert not any(x['any_review_promotion'] for x in trials)


@pytest.mark.parametrize('cfg',[
    TrialConfig(0.,10.,.02),
    TrialConfig(.3,8.,.03,kind='correlated_field_artifact'),
])
def test_simulation_is_deterministic(cfg):
    x=simulate_trial(np.random.default_rng(89),cfg)
    y=simulate_trial(np.random.default_rng(89),cfg)
    assert x==y


def test_benchmark_is_reproducible_with_fixed_seed():
    config={'trials_per_cell':4,'seed':12345,'amplitudes':(.12,.6),'durations':(3.,10.),'noises':(.025,)}
    a=benchmark(**config)
    b=benchmark(**config)
    assert a==b
    assert a['label']=='SYNTHETIC_ONLY_ALGORITHM_STRESS_TEST'
    assert a['n_real_taurus_ztf_curves']==0
    assert a['n_total_trials']==16+60
    assert len(a['cells'])==4
    assert all('wilson_95_low' in v['review_recovery_all_attempts'] for v in a['cells'])


def test_save_benchmark_no_nan(tmp_path):
    b=benchmark(trials_per_cell=4,amplitudes=(.4,),durations=(8.,),noises=(.02,))
    files=save_benchmark(b,tmp_path)
    assert (tmp_path/'SYNTHETIC_V07_SELECTION_FUNCTION.json').exists()
    assert (tmp_path/'SYNTHETIC_V07_RECOVERY_GRID.csv').exists()
    assert 'n/a' not in (tmp_path/'SYNTHETIC_V07_SELECTION_FUNCTION.json').read_text()


def test_invalid_trial_configuration():
    for kwargs in [dict(amplitude_mag=-1,duration_days=2,noise_mag=.02),
                   dict(amplitude_mag=.3,duration_days=-2,noise_mag=.02),
                   dict(amplitude_mag=.3,duration_days=2,noise_mag=0),
                   dict(amplitude_mag=.3,duration_days=2,noise_mag=.02,kind='bad'),
                   dict(amplitude_mag=.3,duration_days=2,noise_mag=.02,direction='bad'),
                   dict(amplitude_mag=.3,duration_days=2,noise_mag=.02,kind='constant_star')]:
        with pytest.raises(ValueError): TrialConfig(**kwargs)


def test_invalid_benchmark_configuration():
    for kwargs in [dict(trials_per_cell=2),dict(trials_per_cell=101),dict(seed=-1)]:
        with pytest.raises(ValueError): benchmark(**kwargs)