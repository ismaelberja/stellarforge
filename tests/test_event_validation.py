"""Regression tests for deterministic, exclusively SYNTHETIC experiments."""
import importlib.util
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'scripts'/'run_synthetic_event_validation.py'
spec=importlib.util.spec_from_file_location('synthetic_event_validation',SCRIPT)
bench=importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)


def test_low_amplitude_is_injected_exactly_once():
    rng1=np.random.default_rng(2026)
    rng2=np.random.default_rng(2026)
    base=dict(id='SYNTHETIC_noise', n=170, err=.04, amp=0, event='none', width=7)
    signal=dict(base,id='SYNTHETIC_injected',event='fading',amp=.24)
    t0,y0,e0,start0,end0=bench.make_trial(rng1,base)
    t1,y1,e1,start1,end1=bench.make_trial(rng2,signal)
    assert np.allclose(t0,t1)
    assert start0==start1 and end0==end1
    mask=(t0>=start0)&(t0<=end0)
    assert mask.any()
    assert np.allclose((y1-y0)[mask],.24)
    assert np.allclose((y1-y0)[~mask],0)


def test_benchmark_is_deterministic_and_clearly_labeled(tmp_path):
    result=bench.run(tmp_path, trials=10, seed=20261104)
    assert result['dataset_type']=='SYNTHETIC_ONLY_NOT_OBSERVATIONS'
    assert result['n_total_synthetic_trials']==70
    assert result['scientific_completeness_or_purity_estimate'] is None
    assert len(result['scenarios'])==7
    assert (tmp_path/'SYNTHETIC_recovery.png').stat().st_size>5000
    assert (tmp_path/'SYNTHETIC_example_fading.png').stat().st_size>5000