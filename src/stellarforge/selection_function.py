"""Reproducible synthetic completeness/false-positive experiment for v0.7.

This module deliberately DOES NOT report an astrophysical completeness or
purity estimate; it tests an algorithm under declared artificial assumptions.
Future users can replace the synthetic cadences with genuine vetted ZTF epochs,
but source identity, image-level artifacts and field controls remain required.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, asdict
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from .injection import Episode, inject_episode, exposure_coverage, wilson_interval
from .vetting import FieldControl, review_multiband_event_candidates

DEFAULT_AMPLITUDES = (0.12, 0.22, 0.40, 0.65)
DEFAULT_DURATIONS = (2.0, 5.0, 10.0, 20.0)
DEFAULT_NOISE_LEVELS = (0.025, 0.07)


@dataclass(frozen=True)
class TrialConfig:
    amplitude_mag: float
    duration_days: float
    noise_mag: float
    direction: str = "fading"
    kind: str = "source_like"  # or correlated_field_artifact / constant_star

    def __post_init__(self):
        if self.kind not in ("source_like", "correlated_field_artifact", "constant_star"):
            raise ValueError("Unsupported simulation class")
        if self.direction not in ("fading", "brightening"):
            raise ValueError("Invalid direction")
        if not all(math.isfinite(v) for v in (self.amplitude_mag, self.duration_days, self.noise_mag)):
            raise ValueError("Nonfinite simulation parameter")
        if not 0 <= self.amplitude_mag <= 3 or not .5 <= self.duration_days <= 80 or not 0 < self.noise_mag <= 1:
            raise ValueError("Parameters outside conservative experiment bounds")
        if self.kind == "constant_star" and self.amplitude_mag != 0:
            raise ValueError("Constant star must have zero injected amplitude")


def seasonal_times(rng: np.random.Generator, *, epochs: int = 240,
                   start_mjd: float = 58300.,
                   n_seasons: int = 3,
                   season_length_days: float = 140.,
                   year_days: float = 365.25) -> np.ndarray:
    """Artificial ZTF-like gaps. NOT the actual ZTF sampling pattern."""
    if not 30 <= epochs <= 2000 or not 1 <= n_seasons <= 6:
        raise ValueError("Invalid cadence experiment")
    nper = [epochs // n_seasons] * n_seasons
    for j in range(epochs % n_seasons):
        nper[j] += 1
    times = np.concatenate([start_mjd + j * year_days +
                            rng.uniform(0, season_length_days, nper[j])
                            for j in range(n_seasons)])
    return np.sort(times)


def simulate_trial(rng: np.random.Generator, config: TrialConfig) -> dict:
    """Generate independent passband cadences and field controls, run v0.6 gate."""
    center = float(58300 + rng.uniform(8, 132) + 365.25 * int(rng.integers(0, 3)))
    # Build noise before injection; all source identity and control-star quality
    # gates in this artificial test are assumed to have been fulfilled.
    episode = Episode(center, config.duration_days, config.amplitude_mag,
                      direction=config.direction, shape="box")
    curves: dict[str, dict] = {}
    controls: dict[str, list[FieldControl]] = {}
    opportunities: dict[str, bool] = {}
    for band, offset in (("g", 0.), ("r", .34)):
        t = seasonal_times(rng)
        # Gamma-tailed positive uncertainties deliberately heteroscedastic.
        errors = np.clip(config.noise_mag * rng.lognormal(0, .2, len(t)), .003, 1.)
        baseline = 14.3 + offset + rng.normal(0., errors)
        # A typical source event affects both bands; a field artifact affects
        # all same-exposure control stars, but no event is physically assumed.
        if config.kind != "constant_star":
            injected, _ = inject_episode(tuple(t), tuple(baseline), episode)
            baseline = np.asarray(injected)
        opportunities[band] = exposure_coverage(tuple(t), episode)["at_least_minimum_epochs_sampled"]
        curves[band] = {"oid": "10001" if band == "g" else "10002",
                        "time_scale": "MJD", "time": t, "mag": baseline, "magerr": errors}
        control_series = []
        for star in range(4):
            noise = .018
            y = 16 + .2*star + rng.normal(0., noise, len(t))
            if config.kind == "correlated_field_artifact":
                y, _ = inject_episode(tuple(t), tuple(y), episode)
            control_series.append(FieldControl(f"{band}_simulated_control_{star}",
                                               tuple(t), tuple(y), (noise,) * len(t),
                                               association_vetted=True,
                                               same_field_and_calibration=True))
        controls[band] = control_series
    review = review_multiband_event_candidates(curves, controls,
                                               source_identity_status="independently_vetted")
    findings = review["findings"]
    exact = []
    for finding in findings:
        # A generic spurious trigger outside the true window is NOT a recovery.
        if config.kind == "constant_star":
            continue
        overlapping = (finding["start_time"] <= center + config.duration_days / 2 + 1
                       and finding["end_time"] >= center - config.duration_days / 2 - 1)
        if overlapping and finding["direction"] == config.direction:
            exact.append(finding)
    return {
        "sampled_in_both_bands": bool(all(opportunities.values())),
        "raw_any_trigger": bool(review["n_raw_candidate_events"]),
        "raw_true_window_recovered": bool(exact),
        "passed_review": any(x["review_priority"] == "multi_band_candidate_requires_physical_review"
                             for x in exact),
        "field_artifact_vetoed": any(x["review_priority"] == "veto_suspected_field_calibration_artifact"
                                      for x in exact),
        "hold_inconclusive": any(x["review_priority"] == "hold_controls_inconclusive" for x in exact),
        "unexpected_promotions": any(x["review_priority"] == "multi_band_candidate_requires_physical_review"
                                     for x in findings) if config.kind != "source_like" else False,
        "n_raw_candidates": review["n_raw_candidate_events"],
        "any_review_promotion": any(x["review_priority"] == "multi_band_candidate_requires_physical_review"
                                    for x in findings),
    }


def _metric(rows: list[dict], key: str, denominator: str | None = None) -> dict:
    included = [x for x in rows if denominator is None or x[denominator]]
    k = sum(bool(x[key]) for x in included)
    n = len(included)
    interval = wilson_interval(k, n)
    return {"successes": k, "trials": n, "fraction": round(k/n, 4) if n else None,
            "wilson_95_low": round(interval[0], 4) if interval else None,
            "wilson_95_high": round(interval[1], 4) if interval else None}


def benchmark(*, trials_per_cell: int = 12, seed: int = 20261104,
              amplitudes=DEFAULT_AMPLITUDES,
              durations=DEFAULT_DURATIONS,
              noises=DEFAULT_NOISE_LEVELS) -> dict:
    if not isinstance(trials_per_cell, int) or not 4 <= trials_per_cell <= 100:
        raise ValueError("Trials per cell must be 4..100")
    if not isinstance(seed, int) or seed < 0:
        raise ValueError("Invalid random seed")
    rng = np.random.default_rng(seed)
    results = []
    for noise in noises:
        for amp in amplitudes:
            for duration in durations:
                cfg = TrialConfig(float(amp), float(duration), float(noise))
                runs = [simulate_trial(rng, cfg) for _ in range(trials_per_cell)]
                results.append({**asdict(cfg), "n_trials": trials_per_cell,
                                "injection_exposure_opportunity": _metric(runs, "sampled_in_both_bands"),
                                "raw_trigger_given_sampled": _metric(runs, "raw_true_window_recovered",
                                                                     "sampled_in_both_bands"),
                                "review_recovery_all_attempts": _metric(runs, "passed_review"),
                                "review_recovery_given_sampled": _metric(runs, "passed_review",
                                                                          "sampled_in_both_bands"),
                                "spurious_reviews": _metric(runs, "unexpected_promotions")})
    # Explicit controls for false alarms and correlated instrumental artifacts.
    control_n = max(30, 3 * trials_per_cell)
    controls = {}
    for kind, amp in (("constant_star", 0.), ("correlated_field_artifact", .65)):
        for noise in noises:
            cfg = TrialConfig(amp, 10., float(noise), kind=kind)
            rows = [simulate_trial(rng, cfg) for _ in range(control_n)]
            controls[f"{kind}_noise_{noise}"] = {
                **asdict(cfg), "n_trials": control_n,
                "any_raw_candidate": _metric(rows, "raw_any_trigger"),
                "unexpected_review_priority": _metric(rows, "unexpected_promotions"),
                "field_artifact_vetoed": _metric(rows, "field_artifact_vetoed"),
                "hold_inconclusive": _metric(rows, "hold_inconclusive"),
            }
    return {
        "label": "SYNTHETIC_ONLY_ALGORITHM_STRESS_TEST",
        "version": "0.7", "random_seed": seed,
        "n_signal_trials": len(results) * trials_per_cell,
        "n_null_and_artifact_trials": len(controls) * control_n,
        "n_total_trials": len(results) * trials_per_cell + len(controls) * control_n,
        "simulation_definition": {
            "cadence": "synthetic, independent g/r epochs, 3x140-day seasons separated by yearly gaps",
            "noise": "heteroscedastic Gaussian errors with lognormal uncertainty distribution",
            "source_episode": "box profile, two-band achromatic magnitude offset",
            "field_artifact": "same-shift, same-epoch offsets in all field controls",
            "n_reference_stars_per_band": 4,
            "source_identity_assumed_by_construction": True,
            "recovery_definition": "correct sign, overlapping injected window, passes v0.6 review gate",
            "observational_cadence_used": False,
        },
        "cells": results,
        "negative_controls": controls,
        "n_real_taurus_ztf_curves": 0,
        "scientific_selection_function_measured": False,
        "new_discoveries_claimed": False,
        "limitations": [
            "None of the times or magnitudes originate from ZTF observations.",
            "All simulated crossmatches and reference stars are assumed vetted by construction.",
            "Idealized box events do not represent full YSO morphology or color behavior.",
            "The field artifact represents one specific mode of calibration failure.",
            "Wilson confidence intervals represent Monte Carlo counting noise, not survey selection uncertainty.",
            "Real source-specific completeness requires injection into authenticated ZTF cadences with independent artifact controls.",
        ],
    }


def save_benchmark(result: dict, outdir: Path) -> dict:
    """Write atomic JSON, CSV and figure, explicitly marked synthetic only."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    dest = outdir / "SYNTHETIC_V07_SELECTION_FUNCTION.json"
    tmp = dest.with_suffix(".json.partial")
    tmp.write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    tmp.replace(dest)
    import csv
    rows = []
    for x in result["cells"]:
        rows.append({"noise_mag": x["noise_mag"], "amplitude_mag": x["amplitude_mag"],
                     "duration_days": x["duration_days"],
                     "opportunity_fraction": x["injection_exposure_opportunity"]["fraction"],
                     "n_sampled": x["raw_trigger_given_sampled"]["trials"],
                     "raw_recovery_given_sampled": x["raw_trigger_given_sampled"]["fraction"],
                     "review_recovery_all_attempts": x["review_recovery_all_attempts"]["fraction"],
                     "review_recovery_given_sampled": x["review_recovery_given_sampled"]["fraction"],
                     "review_recovery_wilson95_low": x["review_recovery_all_attempts"]["wilson_95_low"],
                     "review_recovery_wilson95_high": x["review_recovery_all_attempts"]["wilson_95_high"]})
    with (outdir / "SYNTHETIC_V07_RECOVERY_GRID.csv").open("w", encoding="utf-8", newline="") as handle:
        w = csv.DictWriter(handle, fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    return {"json": str(dest), "csv": str(outdir / "SYNTHETIC_V07_RECOVERY_GRID.csv")}