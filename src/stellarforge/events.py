"""Conservative, explainable *candidate-event* screening for ZTF photometry.

The method operates on one QC-accepted OID, filter, time convention at a time.
It never assigns an astrophysical cause or a confirmed dipper/burster label.

M follows a documented magnitude-tail convention inspired by Cody et al. (2014):
positive values mean fading episodes; negative values, brightening episodes.
References: Cody et al. 2014, AJ 147, 82; Bredall et al. 2020, MNRAS 496, 3257.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
import csv
import hashlib
import json
import math
from pathlib import Path


@dataclass(frozen=True)
class EventCandidate:
    direction: str  # 'fading' or 'brightening', never physical mechanism
    start_time: float
    end_time: float
    duration_lower_bound_days: float
    n_epochs: int
    max_magnitude_excursion: float
    peak_significance_proxy: float
    integrated_excursion_mag_days_proxy: float | None
    row_numbers: tuple[int, ...]


def _libraries():
    try:
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("Install project analysis dependencies: pip install -e '.[analysis]'") from exc
    return np


def _validated_arrays(t, mag, err, np):
    t, mag, err = (np.asarray(x, dtype=float) for x in (t, mag, err))
    if any(x.ndim != 1 for x in (t, mag, err)) or not len(t) or len(t) != len(mag) or len(t) != len(err):
        raise ValueError("Time, magnitude and error must be aligned one-dimensional arrays")
    if not all(np.all(np.isfinite(a)) for a in (t, mag, err)) or np.any(err <= 0):
        raise ValueError("Missing/invalid observation or photometric uncertainty")
    order = np.argsort(t, kind="mergesort")
    t, mag, err = (v[order] for v in (t, mag, err))
    if np.any(np.diff(t) <= 0):
        raise ValueError("Duplicate/non-increasing epochs; run photometric QC first")
    return t, mag, err


def magnitude_asymmetry_m(magnitudes) -> float | None:
    """Magnitude-tail asymmetry M: positive=fading; negative=brightening.

    We use the arithmetic mean of the lowest and highest *10 percent* of data
    (20% combined), subtract the median and divide by the overall population
    RMS. This choice is explicit because M tails vary across publications.
    No clipping of potential astrophysical events is applied.
    """
    np = _libraries()
    y = np.asarray(magnitudes, dtype=float)
    if y.ndim != 1 or len(y) < 20 or not np.all(np.isfinite(y)):
        return None
    std = float(np.std(y))
    if std <= 1e-12:
        return None
    k = max(1, int(math.ceil(.10 * len(y))))
    yy = np.sort(y)
    extremes_mean = float(np.mean(np.r_[yy[:k], yy[-k:]]))
    return float((extremes_mean - np.median(yy)) / std)


def _run_candidates(indices, times, mags, sigma, median, noise, direction, gap):
    np = _libraries()
    events = []
    runs = []
    for index in indices:
        if not runs or float(times[index] - times[runs[-1][-1]]) > gap:
            runs.append([int(index)])
        else:
            runs[-1].append(int(index))
    for run in runs:
        if len(run) < 2:  # single-epoch spikes are not event candidates
            continue
        values = np.asarray([abs(float(mags[i] - median)) for i in run])
        peak_i = int(np.argmax(values))
        duration = float(times[run[-1]] - times[run[0]])
        # Trapezoidal value is *not* physical energy; unobserved gaps remain.
        integral = (float(np.trapezoid(values, times[run])) if hasattr(np, "trapezoid")
                    else float(np.trapz(values, times[run])))
        events.append(EventCandidate(
            direction=direction,
            start_time=float(times[run[0]]),
            end_time=float(times[run[-1]]),
            duration_lower_bound_days=duration,
            n_epochs=len(run),
            max_magnitude_excursion=float(np.max(values)),
            peak_significance_proxy=float(np.max(sigma[run])),
            integrated_excursion_mag_days_proxy=integral,
            row_numbers=tuple(run),
        ))
    return events


def screen_events(t, mag, err, *, min_epochs=30, min_amplitude_mag=.18,
                  significance_threshold=4.0, max_gap_days=4.0) -> dict:
    """Flag *possible* magnitude excursions, preserving uncertainties/cadence.

    A point is a trigger when its absolute excursion from median exceeds BOTH
    an amplitude floor and a significance proxy using local measurement error
    plus robust scatter. Two neighboring trigger observations within gap days
    are needed. This heuristic is deliberately conservative; correlated noise,
    sampling bias, blending and systematic offsets are not characterized.
    """
    np = _libraries()
    for name, val in (("min_amplitude_mag", min_amplitude_mag),
                      ("significance_threshold", significance_threshold),
                      ("max_gap_days", max_gap_days)):
        if not math.isfinite(val) or val <= 0:
            raise ValueError(f"{name} must be finite positive")
    if not isinstance(min_epochs, int) or min_epochs < 10:
        raise ValueError("min_epochs must be >= 10")
    t, y, err = _validated_arrays(t, mag, err, np)
    result = {
        "method": "conservative_2plus_epoch_magnitude_excursion_screen_v0.5",
        "magnitude_direction": "fading is higher magnitude; brightening is lower magnitude",
        "n_epochs": len(t),
        "time_span_days": float(t[-1] - t[0]),
        "min_epoch_requirement": min_epochs,
        "fading_events": [], "brightening_events": [],
        "morphology_label": "unassigned",
        "physical_cause_identified": False,
        "reference_statistic_M": magnitude_asymmetry_m(y),
        "candidate_M_thresholds_illustrative_only": [-0.25, 0.25],
        "discovery_claim": False,
    }
    if len(t) < min_epochs:
        result["status"] = "insufficient_epochs"
        return result
    med = float(np.median(y))
    mad_sigma = float(1.4826 * np.median(np.abs(y - med)))
    # Robust scatter includes physical variability and is not white noise.
    noise = max(mad_sigma, float(np.median(err)))
    denom = np.sqrt(err**2 + noise**2)
    significance = np.abs(y - med) / denom
    large = np.abs(y - med) >= min_amplitude_mag
    trusted = large & (significance >= significance_threshold)
    fading = np.nonzero(trusted & (y > med))[0]
    bright = np.nonzero(trusted & (y < med))[0]
    dips = _run_candidates(fading, t, y, significance, med, noise, "fading", max_gap_days)
    bursts = _run_candidates(bright, t, y, significance, med, noise, "brightening", max_gap_days)
    result.update({
        "status": "exploratory_event_screen_completed",
        "median_mag": med,
        "median_measurement_error": float(np.median(err)),
        "robust_scatter_proxy": noise,
        "n_fading_trigger_epochs": len(fading),
        "n_brightening_trigger_epochs": len(bright),
        "n_fading_event_candidates": len(dips),
        "n_brightening_event_candidates": len(bursts),
        "fading_events": [asdict(x) for x in dips],
        "brightening_events": [asdict(x) for x in bursts],
        "limitations": [
            "This is not a Cody Q-M classification or a physical dipper/burster label.",
            "Two points can share an instrumental systematic or calibration offset.",
            "Without independent scene/source/astrometry review the ZTF OID is unverified.",
            "Event duration is an observed lower bound, not continuous event length.",
            "Significance is a heuristic proxy, not a calibrated false-alarm probability.",
            "Sensitivity drops for high-noise, rapidly repeating or high-duty-cycle events.",
        ],
    })
    return result


def screen_normalized_file(input_path: Path, output: Path, *, min_epochs=30) -> dict:
    """Group by OID, band, time scale; record input hash and per-curve outcomes."""
    from .variability import _read_normalized
    input_path = Path(input_path)
    raw = input_path.read_bytes()
    groups = _read_normalized(input_path)
    dataset_type = "SYNTHETIC_fixture" if "SYNTHETIC" in input_path.as_posix().upper() else "unverified_observational_file"
    rows = []
    for (oid, band, time_scale), points in sorted(groups.items()):
        t, mag, err = zip(*points)
        result = screen_events(t, mag, err, min_epochs=min_epochs)
        rows.append({"oid": oid, "band": band, "time_scale": time_scale,
                     "source_association": "unverified", **result})
    payload = {
        "dataset_type": dataset_type,
        "input_name": input_path.name,
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "n_curves": len(rows),
        "curves": rows,
        "scientific_detection_count": None,
        "confirmed_dipper_or_burster_count": None,
        "note": "All event candidates require independent identity, image, calibration and physical review.",
    }
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return payload