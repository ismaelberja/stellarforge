"""Reproducible, survey-aware photometric variability *diagnostics*.

Input is the normalized, QC-accepted v0.3 photometry format. This module
never infers astrophysical membership, physical mechanism, or a discovery.

A Lomb--Scargle peak is a period *candidate*, not a statistically established
rotation period. Empirical permutations are a white-noise diagnostic only:
correlated noise, seasonal sampling and multiple testing are not modeled.
"""
from __future__ import annotations

from collections import defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path


def _science_libs():
    try:
        import numpy as np
        from scipy.signal import lombscargle
    except ImportError as exc:
        raise RuntimeError("Install optional scientific dependencies: pip install -e '.[science]'") from exc
    return np, lombscargle


def _percentile(values, q, np):
    return float(np.percentile(values, q))


def descriptive_features(t, mag, magerr) -> dict:
    """Descriptive features of exactly one OID / band / time convention.

    The tail index is defined here, not claimed to reproduce a published
    morphology metric. Positive: extended faint (higher-magnitude) tail;
    negative: extended bright tail. It is NOT a dipper/burster diagnosis.
    """
    np, _ = _science_libs()
    t, mag, magerr = (np.asarray(x, dtype=float) for x in (t, mag, magerr))
    if len(t) != len(mag) or len(t) != len(magerr) or not len(t):
        raise ValueError("times/magnitudes/errors must have identical nonzero length")
    if not np.all(np.isfinite(t)) or not np.all(np.isfinite(mag)):
        raise ValueError("Non-finite photometry")
    if not np.all(np.isfinite(magerr)) or np.any(magerr <= 0):
        raise ValueError("Nonpositive or invalid magnitude errors")
    if len(np.unique(t)) != len(t):
        raise ValueError("Duplicate time epochs require prior QC")
    weights = 1.0 / magerr**2
    weighted_mean = float(np.sum(weights * mag) / np.sum(weights))
    chi2 = float(np.sum(weights * (mag - weighted_mean)**2))
    median = float(np.median(mag))
    q05, q10, q90, q95 = (_percentile(mag, q, np) for q in (5, 10, 90, 95))
    observed_std = float(np.std(mag, ddof=1)) if len(mag) > 1 else 0.0
    median_err = float(np.median(magerr))
    span = float(np.ptp(t))
    tail_span = q90 - q10
    return {
        "n_epochs": int(len(t)),
        "span_days": span,
        "weighted_mean_mag": weighted_mean,
        "median_mag": median,
        "median_magerr": median_err,
        "reduced_chi2_constant": chi2 / (len(mag) - 1) if len(mag) > 1 else None,
        "mag_std": observed_std,
        "robust_amplitude_p95_p05_mag": q95 - q05,
        "mag_mad": float(np.median(np.abs(mag - median))),
        "normalized_intrinsic_variance_proxy": float(max(0.0, observed_std**2 - float(np.mean(magerr**2)))),
        "tail_asymmetry_mag": float((q90 + q10 - 2 * median) / tail_span) if tail_span > 0 else None,
        "photometric_variability_diagnosis": "unassigned",
    }


def _period_grid(times, minimum_period_days: float, maximum_period_days: float, oversample: int, np):
    if not (math.isfinite(minimum_period_days) and math.isfinite(maximum_period_days)):
        raise ValueError("Periods must be finite")
    if not 0.2 <= minimum_period_days < maximum_period_days <= 2000:
        raise ValueError("Period range must be within [0.2, 2000] days and ordered")
    if not isinstance(oversample, int) or not 1 <= oversample <= 10:
        raise ValueError("oversample must be between 1 and 10")
    span = float(np.ptp(times))
    if span < 2 * maximum_period_days:
        raise ValueError("Time baseline must span at least twice the maximum trial period")
    lower_freq, upper_freq = 1.0 / maximum_period_days, 1.0 / minimum_period_days
    nfreq = max(300, int(math.ceil(oversample * span * (upper_freq - lower_freq))) + 1)
    if nfreq > 16000:
        raise ValueError("Trial frequency grid exceeds 16,000; reduce period range/oversampling")
    return np.linspace(lower_freq, upper_freq, nfreq)


def sampling_window(times, frequency, np):
    """Power of the *observation timestamps* (not photometric variability).

    Spectral window is normalized by N^2; a large value indicates
    cadence-driven alias sensitivity. Chunked to bound memory use.
    """
    reduced_time = np.asarray(times, dtype=float) - min(times)
    output = np.empty(len(frequency), dtype=float)
    n = len(reduced_time)
    for start in range(0, len(frequency), 512):
        stop = start + 512
        phase = np.outer(frequency[start:stop], reduced_time)
        output[start:stop] = np.abs(np.exp(2j * np.pi * phase).sum(axis=1))**2 / n**2
    return output


def search_period(t, mag, magerr, *, minimum_period_days=0.5,
                  maximum_period_days=30.0, oversample=3,
                  permutations=0, random_seed=2026) -> dict:
    """Weighted floating-mean LS and exploratory fixed-cadence null sampling.

    The returned permutation exceedance is a *diagnostic only*, NOT a
    publication-grade FAP. Permutation assumes time-independent errors.
    """
    np, lombscargle = _science_libs()
    t, y, err = (np.asarray(x, dtype=float) for x in (t, mag, magerr))
    _ = descriptive_features(t, y, err)
    if len(t) < 30:
        raise ValueError("At least 30 unique epochs are required")
    if not isinstance(permutations, int) or not 0 <= permutations <= 200:
        raise ValueError("permutations must be between 0 and 200")
    frequencies = _period_grid(t, minimum_period_days, maximum_period_days, oversample, np)
    shifted_t = t - float(np.min(t))
    omega = frequencies * (2 * np.pi)
    power = lombscargle(shifted_t, y, omega, weights=1/err**2,
                        floating_mean=True, normalize=True)
    if not np.all(np.isfinite(power)):
        raise ValueError("Periodogram returned non-finite power")
    idx = int(np.argmax(power))
    peak_freq = float(frequencies[idx]); peak_power = float(power[idx])
    window = sampling_window(shifted_t, frequencies, np)
    window_at_peak = float(window[idx])
    cadence_alias = min(abs(peak_freq - k) for k in (1, 2, 3, 4, 5)) < max(0.01, 1/float(np.ptp(t)))
    strong_window = window_at_peak > 0.12
    null_exceedance = None
    if permutations:
        rng = np.random.default_rng(random_seed)
        exceed = 0
        for _ in range(permutations):
            # Preserve pairs (mag, error) as they may be heteroscedastic.
            shuffled = rng.permutation(len(y))
            nullpower = lombscargle(shifted_t, y[shuffled], omega,
                                    weights=1/err[shuffled]**2,
                                    floating_mean=True, normalize=True)
            exceed += bool(float(np.max(nullpower)) >= peak_power)
        null_exceedance = (exceed + 1) / (permutations + 1)
    return {
        "method": "scipy_lombscargle_weighted_floating_mean",
        "best_period_days": 1.0 / peak_freq,
        "peak_power_normalized": peak_power,
        "freq_range_cycles_per_day": [float(frequencies[0]), float(frequencies[-1])],
        "frequency_grid_points": int(len(frequencies)),
        "sampling_window_power_at_peak": window_at_peak,
        "possible_daily_alias": bool(cadence_alias),
        "possible_sampling_alias": bool(cadence_alias or strong_window),
        "permutation_trials": permutations,
        "permutation_peak_exceedance_white_noise_diagnostic": null_exceedance,
        "formal_false_alarm_probability": None,
        "physical_period_confirmed": False,
        "note": "Peak is provisional; inspect phase folding, the window function, harmonics, red noise, seasons and independent literature.",
    }


def _read_normalized(path: Path):
    """Reject malformed/ambiguous normalized inputs before feature extraction."""
    accepted = {"oid", "band", "time_value", "time_scale", "magnitude", "magnitude_error", "catflags"}
    groups = defaultdict(list)
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not accepted <= set(reader.fieldnames):
            raise ValueError("Missing normalized ZTF columns; run inspect-ztf first")
        for row in reader:
            if None in row:
                raise ValueError("Bad normalized CSV cell count")
            oid, band, scale = row["oid"], row["band"], row["time_scale"]
            if not oid.isdigit() or band not in ("g", "r", "i") or scale not in ("MJD", "HJD", "HMJD"):
                raise ValueError("Invalid normalized source / filter / time scale")
            if int(row["catflags"]) & 32768:
                raise ValueError("Masked source points remain in normalized input")
            try:
                t, mag, err = (float(row[field]) for field in ("time_value", "magnitude", "magnitude_error"))
            except (ValueError, TypeError) as exc:
                raise ValueError("Invalid numeric normalized photometry") from exc
            if not all(map(math.isfinite, (t, mag, err))) or err <= 0:
                raise ValueError("Non-finite or nonpositive normalized photometry")
            groups[(oid, band, scale)].append((t, mag, err))
    if not groups:
        raise ValueError("No QC-accepted photometry found")
    return groups


def analyze_normalized_file(path: Path, output: Path, *, min_good_epochs=30,
                            min_period=0.5, max_period=30.0, permutations=0) -> dict:
    """Generate per-curve features; never merge OIDs, passbands, or time scales."""
    if not 1 <= min_good_epochs <= 100000:
        raise ValueError("Invalid minimum epoch requirement")
    groups = _read_normalized(path)
    source_bytes = Path(path).read_bytes()
    result = {
        "input_basename": Path(path).name,
        "input_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "data_type": "unverified_source_association",
        "scientific_membership_verified": False,
        "astrophysical_classifications_produced": False,
        "curves": [],
    }
    for (oid, band, scale), points in sorted(groups.items()):
        times, mags, errors = zip(*sorted(points))
        item = {"oid": oid, "band": band, "time_scale": scale,
                "source_association": "unverified", "number_of_QC_accepted_epochs": len(points)}
        if len(points) < min_good_epochs:
            item["status"] = "insufficient_epochs"
        else:
            item["features"] = descriptive_features(times, mags, errors)
            try:
                item["period"] = search_period(times, mags, errors,
                                               minimum_period_days=min_period,
                                               maximum_period_days=max_period,
                                               permutations=permutations)
                item["status"] = "provisional_variability_diagnostics"
            except ValueError as exc:
                item["period"] = None
                item["status"] = "period_search_ineligible"
                item["reason"] = str(exc)
        result["curves"].append(item)
    result["n_curves"] = len(result["curves"])
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return result