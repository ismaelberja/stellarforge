"""Synthetic report guard: never silently relabel generated outputs as discoveries."""
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run_v06_systematics_validation import run


def test_synthetic_stress_manifest_and_veto(tmp_path):
    report=run(tmp_path,trials=10,seed=20261104)
    assert report['dataset_type']=='SYNTHETIC_ONLY'
    assert report['n_real_ZTF_lightcurves']==0
    assert report['n_synthetic_trials']==80
    d={r['scenario']:r for r in report['outcomes']}
    assert d['SYNTHETIC_achromatic_field_artifact']['instrumental_veto_fraction']==1.0
    assert d['SYNTHETIC_achromatic_field_artifact']['physical_review_priority_fraction']==0.0
    assert d['SYNTHETIC_missing_controls']['controls_on_hold_fraction']==1.0
    assert (tmp_path/'SYNTHETIC_V06_VETTING_COMPARISON.png').exists()
    assert json.loads((tmp_path/'SYNTHETIC_V06_STRESS_TEST.json').read_text())['n_confirmed_dippers'] is None


def test_synthetic_stress_refuses_oversized_workload(tmp_path):
    import pytest
    with pytest.raises(ValueError):run(tmp_path,trials=1)