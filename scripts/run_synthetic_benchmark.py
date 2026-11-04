"""Deterministic injection/recovery DEMONSTRATION using ONLY synthetic photometry.

No astronomical observation is fetched, analyzed, or redistributable from here.
This is engineering validation only; it cannot establish survey completeness.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
from stellarforge.variability import search_period, descriptive_features

TRIALS = 24
PERIOD = 5.271
SCENARIOS = {
    "irregular_high_signal": {"seasons": [(0, 100), (165, 265)], "count": 130, "sigma": .03, "amplitude": .18},
    "seasonal_gaps": {"seasons": [(0, 35), (205, 240), (410, 445)], "count": 86, "sigma": .04, "amplitude": .18},
    "sparse_low_signal": {"seasons": [(0, 60), (170, 230)], "count": 38, "sigma": .09, "amplitude": .07},
}


def synthetic_times(rng, config):
    # Fixed windows ensure that all gaps are real *simulation* gaps.
    windows = config["seasons"]
    lengths = np.array([b-a for a, b in windows], dtype=float)
    allocation = rng.multinomial(config["count"], lengths / sum(lengths))
    times = np.concatenate([rng.uniform(a, b, n) for (a, b), n in zip(windows, allocation)])
    return 59000 + np.sort(times)


def benchmark(*, trials=TRIALS):
    output = {"kind": "synthetic_injection_recovery_only", "true_period_days": PERIOD,
              "does_not_measure": ["Taurus variability", "real survey completeness", "false-alarm rate on correlated real noise"],
              "settings": {"random_seed_base": 73291, "n_trials_per_scenario": trials,
                           "period_search_range_days": [2, 14], "success_relative_period_error": 0.05},
              "scenarios": {}}
    sample = None
    for j, (name, config) in enumerate(SCENARIOS.items()):
        recovered = []; errors = []; alias_flags = []; powers=[]
        for i in range(trials):
            rng = np.random.default_rng(73291 + 10000*j + i)
            t = synthetic_times(rng, config)
            sigma = np.full(len(t), config["sigma"])
            signal = (16 + config["amplitude"] * np.sin(2*np.pi*(t-59000)/PERIOD + .15)
                      + rng.normal(0, config["sigma"], len(t)))
            outcome = search_period(t, signal, sigma, minimum_period_days=2.,
                                    maximum_period_days=14.)
            difference = abs(outcome["best_period_days"]-PERIOD) / PERIOD
            recovered.append(difference < .05)
            errors.append(difference)
            alias_flags.append(outcome["possible_sampling_alias"])
            powers.append(outcome["peak_power_normalized"])
            if j == 0 and i == 0:
                sample=(t, signal, sigma, outcome["best_period_days"])
        output["scenarios"][name] = {
            "n_trials": len(recovered), "recovered_within_5_percent": int(sum(recovered)),
            "recovery_fraction": float(np.mean(recovered)),
            "median_relative_period_error": float(np.median(errors)),
            "fraction_flagged_sampling_alias": float(np.mean(alias_flags)),
            "median_peak_power": float(np.median(powers)),
            "configuration": config,
        }
    return output, sample


def make_figure(sample, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    t, mag, err, recovered_period = sample
    fig, ax=plt.subplots(figsize=(9.3,4.2))
    ax.errorbar(t-59000, mag, yerr=err, fmt='o', markersize=2.5,
                capsize=0, alpha=.6, label="Simulated observations")
    x=np.linspace(0, max(t-59000), 1000)
    ax.plot(x, 16+.18*np.sin(2*np.pi*x/PERIOD+.15), lw=1.6, label="Injected 5.271-day signal")
    ax.set(xlabel="Simulation time (days)",ylabel="Synthetic magnitude",title="Injection/recovery: irregular cadence")
    ax.invert_yaxis();ax.legend(loc="lower right",fontsize=8)
    fig.text(.5,.5,"SYNTHETIC — NOT ASTROPHYSICAL DATA",ha="center",va="center",
             fontsize=18,rotation=25,alpha=.13,weight="bold")
    fig.tight_layout();fig.savefig(path,dpi=140);plt.close(fig)


def make_phase(sample,path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    t, mag, err, recovered_period=sample
    phase=((t-t.min()) / recovered_period) %1
    fig,ax=plt.subplots(figsize=(8,4))
    ax.errorbar(phase,mag,yerr=err,fmt='o',markersize=3,alpha=.6)
    ax.set(xlabel=f"Phase using provisional recovered period {recovered_period:.3f} d",ylabel="Synthetic magnitude",
           title="Recovery demonstration (not a Taurus observation)")
    ax.invert_yaxis()
    fig.text(.5,.55,"SYNTHETIC — NOT OBSERVED",ha="center",va="center",fontsize=19,alpha=.15,rotation=25)
    fig.tight_layout();fig.savefig(path,dpi=140);plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'examples'/'SYNTHETIC_v04_benchmark')
    parser.add_argument('--trials',type=int,default=TRIALS)
    args=parser.parse_args()
    if not 1 <= args.trials <= 200:
        parser.error('--trials must be within 1 and 200')
    args.output.mkdir(parents=True, exist_ok=True)
    result, sample=benchmark(trials=args.trials)
    (args.output/'SYNTHETIC_benchmark.json').write_text(json.dumps(result,indent=2)+'\n')
    make_figure(sample,args.output/'SYNTHETIC_irregular_lightcurve.png')
    make_phase(sample,args.output/'SYNTHETIC_phase_folded.png')
    print('WARNING: results are exclusively SYNTHETIC')
    for name, item in result['scenarios'].items():
        print(f"{name}: {item['recovered_within_5_percent']}/{item['n_trials']} recoveries within 5%")

if __name__=='__main__':
    main()