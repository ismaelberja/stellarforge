"""Run deterministic, clearly SYNTHETIC v0.7 injection/recovery grid."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from stellarforge.selection_function import benchmark, save_benchmark


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=ROOT/'reports/validation_v0.7')
    p.add_argument('--trials-per-cell', type=int, default=12)
    p.add_argument('--seed', type=int, default=20261104)
    args = p.parse_args()
    result = benchmark(trials_per_cell=args.trials_per_cell, seed=args.seed)
    paths = save_benchmark(result, args.output)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    amps=sorted({x['amplitude_mag'] for x in result['cells']})
    durations=sorted({x['duration_days'] for x in result['cells']})
    noises=sorted({x['noise_mag'] for x in result['cells']})
    for noise in noises:
        values=np.array([[next(x['review_recovery_all_attempts']['fraction']
                              for x in result['cells'] if x['noise_mag']==noise
                              and x['amplitude_mag']==amp and x['duration_days']==duration)
                          for duration in durations] for amp in amps])
        fig,ax=plt.subplots(figsize=(9,5.6))
        image=ax.imshow(values,origin='lower',vmin=0,vmax=1,aspect='auto',cmap='viridis')
        for i in range(len(amps)):
            for j in range(len(durations)):
                ax.text(j,i,f'{values[i,j]:.2f}',ha='center',va='center',
                        color='white' if values[i,j]<.5 else 'black',size=10)
        ax.set_xticks(range(len(durations)),durations)
        ax.set_yticks(range(len(amps)),amps)
        ax.set_xlabel('Injected event duration (days)')
        ax.set_ylabel('Injected magnitude excursion (mag)')
        ax.set_title(f'StellarForge v0.7: synthetic review recovery, noise={noise:.3f} mag\n'
                     'ARTIFICIAL CADENCE ONLY — NOT A ZTF / TAURUS SELECTION FUNCTION')
        fig.colorbar(image,ax=ax,label='Fraction of attempts passing review gate')
        fig.tight_layout()
        fig.savefig(args.output/f'SYNTHETIC_V07_RECOVERY_NOISE_{noise:.3f}.png',dpi=165)
        plt.close(fig)
    # Rejection vs false-alarm scenarios are also synthetic, not field performance.
    labels=[]; raw=[]; review=[]; veto=[]
    for key,record in result['negative_controls'].items():
        labels.append(key.replace('_',' '))
        raw.append(record['any_raw_candidate']['fraction'])
        review.append(record['unexpected_review_priority']['fraction'])
        veto.append(record['field_artifact_vetoed']['fraction'])
    fig,ax=plt.subplots(figsize=(11,5))
    y=np.arange(len(labels)); width=.24
    ax.barh(y-width,raw,height=width,label='Raw trigger (synthetic)')
    ax.barh(y,review,height=width,label='Incorrect physical-review priority')
    ax.barh(y+width,veto,height=width,label='Artifact veto')
    ax.set_yticks(y,labels);ax.invert_yaxis()
    ax.set_xlim(0,1.06);ax.set_xlabel('Fraction of synthetic trials')
    ax.set_title('StellarForge v0.7: synthetic null and correlated-artifact challenge\n'
                 'NOT a measured survey false-positive rate')
    ax.legend(loc='lower right');ax.grid(axis='x',alpha=.15)
    fig.tight_layout()
    fig.savefig(args.output/'SYNTHETIC_V07_ARTIFACT_AND_NULL.png',dpi=165)
    plt.close(fig)
    print(json.dumps({'dataset_type':result['label'],'trials':result['n_total_trials'],
                      'outputs':paths,'real_ztf_curves':0},indent=2))

if __name__=='__main__':
    main()