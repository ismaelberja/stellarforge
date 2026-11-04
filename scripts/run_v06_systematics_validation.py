"""Blind-ish synthetic stress tests of a *review-priority* gate.

No genuine ZTF photometry, no real Taurus detections, no purity/completeness
claims. Artificial systematics emulate coherent zeropoint shifts in field stars.
"""
from __future__ import annotations

from collections import Counter
import csv
import json
from pathlib import Path
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from stellarforge.vetting import FieldControl, review_multiband_event_candidates

N_TRIALS=50
SEED=20261104
SCENARIOS=(
  ('SYNTHETIC_both_bands_fading', 'fading', 'none', .55, .018, True),
  ('SYNTHETIC_both_bands_brightening', 'brightening', 'none', .55, .018, True),
  ('SYNTHETIC_achromatic_field_artifact', 'fading', 'all', .55, .018, True),
  ('SYNTHETIC_one_bad_control_in_field', 'fading', 'one', .55, .018, True),
  ('SYNTHETIC_single_band_episode', 'g_only', 'none', .55, .018, True),
  ('SYNTHETIC_white_noise', 'none', 'none', 0, .018, True),
  ('SYNTHETIC_missing_controls', 'fading', 'none', .55, .018, False),
  ('SYNTHETIC_low_signal_high_noise', 'fading', 'none', .26, .09, True),
)


def trial(rng,kind,field,amp,noise,include_controls):
    start=float(rng.uniform(44,88));end=start+7
    curves={};control_bands={}
    for band,offset in [('g',0),('r',0.2)]:
        # The surveys' different passbands have asynchronous sampling.
        t=np.sort(rng.uniform(0,150,300))
        y=14+offset+rng.normal(0,noise,len(t))
        mask=(t>=start)&(t<=end)
        if kind in ('fading','g_only') and (kind!='g_only' or band=='g'):
            y[mask]+=amp
        if kind=='brightening':y[mask]-=amp
        if kind=='none':pass
        e=np.full(len(t),noise)
        curves[band]={'oid':('12' if band=='g' else '34'),
                      'time_scale':'MJD','time':t,'mag':y,'magerr':e}
        if include_controls:
            comparison=[]
            for i in range(4):
                c=15+i*.25+rng.normal(0,.015,len(t))
                if field=='all' or (field=='one' and i==0):c[mask]+=.5
                comparison.append(FieldControl(f'{band}-reference-{i}',tuple(t),tuple(c),tuple(np.full(len(t),.015)),True,True))
            control_bands[band]=comparison
    result=review_multiband_event_candidates(curves,control_bands,source_identity_status='independently_vetted')
    statuses=Counter(r['review_priority'] for r in result['findings'])
    return {'any_event':bool(result['n_raw_candidate_events']),
            'promoted':statuses['multi_band_candidate_requires_physical_review']>0,
            'vetoed':statuses['veto_suspected_field_calibration_artifact']>0,
            'hold':statuses['hold_controls_inconclusive']>0,
            'single_band':statuses['single_band_event_requires_followup']>0,
            'n_events':result['n_raw_candidate_events']}


def run(out_dir:Path, trials:int=N_TRIALS,seed:int=SEED):
    if not isinstance(trials,int) or not 10<=trials<=200:raise ValueError('10..200 trials per scenario')
    out_dir=Path(out_dir);out_dir.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(seed)
    rows=[]
    for scenario,kind,field,amp,noise,include_controls in SCENARIOS:
        r=[trial(rng,kind,field,amp,noise,include_controls) for _ in range(trials)]
        rows.append({'scenario':scenario,'n_trials':trials,'synthetic_kind':kind,
                     'field_control_state':field if include_controls else 'missing',
                     'raw_event_fraction':round(sum(x['any_event'] for x in r)/trials,3),
                     'physical_review_priority_fraction':round(sum(x['promoted'] for x in r)/trials,3),
                     'instrumental_veto_fraction':round(sum(x['vetoed'] for x in r)/trials,3),
                     'controls_on_hold_fraction':round(sum(x['hold'] for x in r)/trials,3),
                     'single_band_fraction':round(sum(x['single_band'] for x in r)/trials,3),
                     'average_events_per_trial':round(sum(x['n_events'] for x in r)/trials,2)})
    manifest={'dataset_type':'SYNTHETIC_ONLY','n_synthetic_trials':len(rows)*trials,
              'random_seed':seed,'n_trials_per_scenario':trials,'analysis_version':'0.6',
              'control_instrumental_model':'coherent_same_field_same_band_magnitude_offset',
              'outcomes':rows,'scientific_purity_or_completeness':None,
              'n_real_ZTF_lightcurves':0,'n_confirmed_dippers':None,
              'limitations':['Synthetic Gaussian noise is not a complete model of ZTF photometry',
                             'Only a single coherent calibration-artifact mechanism is injected',
                             'The reference stars are assumed independently vetted by construction',
                             'No true sky image or astrometric scene is analyzed',
                             'This is an engineering validation, not a survey selection function']}
    (out_dir/'SYNTHETIC_V06_STRESS_TEST.json').write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n')
    with (out_dir/'SYNTHETIC_V06_STRESS_TEST.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    labels=[r['scenario'].replace('SYNTHETIC_','').replace('_',' ') for r in rows]
    fig,ax=plt.subplots(figsize=(11,6.2))
    y=np.arange(len(rows));h=.38
    ax.barh(y-h/2,[r['raw_event_fraction'] for r in rows],height=h,label='Raw event trigger (before vetting)')
    ax.barh(y+h/2,[r['physical_review_priority_fraction'] for r in rows],height=h,label='Pass to physical review (after controls)')
    ax.set_yticks(y,labels);ax.invert_yaxis();ax.set_xlim(0,1.08)
    ax.set_xlabel('Fraction of entirely synthetic trials')
    ax.set_title('StellarForge v0.6 — event screening before and after field controls\nSYNTHETIC DATA ONLY — not Taurus detections')
    ax.legend(loc='lower right');ax.grid(alpha=.18,axis='x')
    fig.tight_layout()
    fig.savefig(out_dir/'SYNTHETIC_V06_VETTING_COMPARISON.png',dpi=180)
    plt.close(fig)
    return manifest


if __name__=='__main__':
    print(json.dumps(run(ROOT/'reports/validation_v0.6'),indent=2))