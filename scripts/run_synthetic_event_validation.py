"""SYNTHETIC ONLY: blind injection-recovery screening and artifact stress tests.

These fixtures are not Taurus data or survey completeness estimates. A pinned
random generator and unmodified detection thresholds are used throughout.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from stellarforge.events import screen_events

SEED=20261104
N_TRIALS=60

SCENARIOS = [
    dict(id='SYNTHETIC_dense_dips', n=320, err=.02, amp=.55, event='fading', width=7),
    dict(id='SYNTHETIC_dense_bursts', n=320, err=.02, amp=.55, event='brightening', width=7),
    dict(id='SYNTHETIC_sparse_dips', n=85, err=.025, amp=.55, event='fading', width=7),
    dict(id='SYNTHETIC_low_amplitude', n=170, err=.04, amp=.24, event='fading', width=7),
    dict(id='SYNTHETIC_high_noise', n=170, err=.09, amp=.36, event='fading', width=7),
    dict(id='SYNTHETIC_white_noise_control', n=320, err=.025, amp=0, event='none', width=7),
    dict(id='SYNTHETIC_calibration_artifact', n=320, err=.02, amp=.55, event='artifact', width=7),
]


def make_trial(rng, scenario):
    n=scenario['n']
    t=np.sort(rng.uniform(0,140,n))
    err=np.full(n, scenario['err'])
    mag=14.0+rng.normal(0,scenario['err'],n)
    start=float(rng.uniform(45,88));end=start+scenario['width']
    mask=(t>=start)&(t<=end)
    if scenario['event'] in ('fading','artifact','brightening'):
        mag[mask]+=scenario['amp'] if scenario['event']!='brightening' else -scenario['amp']
    return t,mag,err,start,end


def trial_evaluation(scenario,rng):
    t,mag,err,start,end=make_trial(rng,scenario)
    screen=screen_events(t,mag,err)
    detected=screen['fading_events']+screen['brightening_events']
    actual_type=scenario['event']
    matches=[]
    for x in detected:
        true_direction='brightening' if actual_type=='brightening' else 'fading'
        if (x['direction']==true_direction and x['end_time']>=start and x['start_time']<=end):
            matches.append(x)
    return {
        'injected_observation_count':int(sum((t>=start)&(t<=end))),
        'matched':bool(matches) if actual_type not in ('none','artifact') else False,
        'spurious_any_event':bool(detected) if actual_type in ('none','artifact') else False,
        'found_event_count':len(detected),
        'm':screen['reference_statistic_M'],
    }


def run(output_dir:Path, trials=N_TRIALS,seed=SEED):
    output_dir=Path(output_dir)
    if not 10 <= trials <= 500:
        raise ValueError('Require 10–500 simulations per scenario')
    output_dir.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(seed)
    outcomes=[]
    for case in SCENARIOS:
        experiments=[trial_evaluation(case,rng) for _ in range(trials)]
        outcomes.append({
            'scenario':case['id'],'n_trials':trials,
            'synthetic_kind':case['event'],'n_epochs':case['n'],
            'measurement_uncertainty_mag':case['err'],
            'injected_excursion_mag':case['amp'],
            'injected_event_width_days':case['width'],
            'detected_fraction':round(sum(x['matched'] for x in experiments)/trials,4)
            if case['event'] in ('fading','brightening') else None,
            'false_event_fraction':round(sum(x['spurious_any_event'] for x in experiments)/trials,4)
            if case['event'] in ('none','artifact') else None,
            'median_injected_epochs':float(np.median([x['injected_observation_count'] for x in experiments])),
            'n_any_flagged':sum(x['found_event_count']>0 for x in experiments),
        })
    output={
        'dataset_type':'SYNTHETIC_ONLY_NOT_OBSERVATIONS',
        'n_trials_per_scenario':trials,
        'seed':seed,
        'algorithm':'conservative_2plus_epoch_magnitude_excursion_screen_v0.5',
        'n_total_synthetic_trials':trials*len(SCENARIOS),
        'scenarios':outcomes,
        'scientific_completeness_or_purity_estimate':None,
        'source_membership_inferred':False,
        'limitations':[
            'Synthetic white-noise injections are not real ZTF cadence/photometry.',
            'The calibration-artifact control mimics coherent bad measurements and is NOT an astrophysical signal.',
            'No physical dipper or burster classifications are produced.',
            'Noise distribution, seasonal gaps, astrophysical backgrounds and systematics are simplified.',
        ],
    }
    (output_dir/'SYNTHETIC_event_stress_test.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
    fields=list(outcomes[0])
    with (output_dir/'SYNTHETIC_event_stress_test.csv').open('w',newline='',encoding='utf-8') as h:
        w=csv.DictWriter(h,fieldnames=fields);w.writeheader();w.writerows(outcomes)

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rows=[x for x in outcomes if x['detected_fraction'] is not None]
    fig,ax=plt.subplots(figsize=(9,4.8))
    ax.barh([r['scenario'].replace('SYNTHETIC_','').replace('_',' ') for r in rows],
            [r['detected_fraction'] for r in rows])
    ax.set_xlim(0,1.02)
    ax.set_xlabel('Recovery fraction in synthetic injections')
    ax.set_title('StellarForge v0.5 | Engineering validation — synthetic only',fontweight='bold')
    ax.grid(axis='x',alpha=.22)
    fig.tight_layout()
    fig.savefig(output_dir/'SYNTHETIC_recovery.png',dpi=165)
    plt.close(fig)

    rng=np.random.default_rng(seed+1)
    case=SCENARIOS[0];t,mag,err,start,end=make_trial(rng,case)
    screen=screen_events(t,mag,err)
    fig,ax=plt.subplots(figsize=(10,4.7))
    ax.errorbar(t,mag,yerr=err,fmt='.',markersize=3,capsize=0,elinewidth=.4,label='Synthetic measurement')
    ax.axvspan(start,end,alpha=.13,label='Injected fading interval')
    for event in screen['fading_events']:
        ax.axvspan(event['start_time'],event['end_time'],alpha=.22)
    ax.invert_yaxis()
    ax.set_xlabel('Synthetic time (days)')
    ax.set_ylabel('Synthetic magnitude (mag)')
    ax.set_title('Demonstration of a detectable injection — NOT a Taurus light curve')
    ax.legend(loc='best',fontsize=8)
    ax.grid(alpha=.16)
    fig.tight_layout()
    fig.savefig(output_dir/'SYNTHETIC_example_fading.png',dpi=165)
    plt.close(fig)
    return output


if __name__=='__main__':
    data=run(ROOT/'reports'/'validation_v0.5')
    for item in data['scenarios']:
        print(f"{item['scenario']}: detected={item['detected_fraction']}, false={item['false_event_fraction']}")