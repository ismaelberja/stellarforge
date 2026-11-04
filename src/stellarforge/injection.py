"""Calibrated *engineering* injection/recovery, not a ZTF selection function.

An injection changes only magnitude values, never the sampling times, measured
uncertainties or quality masks. Magnitude is logarithmic: positive injected
amplitude is fading (dipper-like), negative is brightening (burster-like).

For any future empirical selection function, inject onto vetted, genuine,
per-source/per-OID/per-band survey cadences, with matching data provenance.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from statistics import NormalDist
from typing import Sequence


@dataclass(frozen=True)
class Episode:
    center_time: float
    duration_days: float
    amplitude_mag: float
    direction: str = "fading"
    shape: str = "box"  # box or Gaussian with duration = FWHM

    def __post_init__(self) -> None:
        values = (self.center_time, self.duration_days, self.amplitude_mag)
        if not all(math.isfinite(x) for x in values):
            raise ValueError("Episode parameters must be finite")
        if self.duration_days <= 0 or self.amplitude_mag < 0:
            raise ValueError("Positive duration and nonnegative magnitude amplitude required")
        if self.direction not in ("fading", "brightening"):
            raise ValueError("Invalid event direction")
        if self.shape not in ("box", "gaussian"):
            raise ValueError("Unsupported event morphology")


def inject_episode(times: Sequence[float], magnitudes: Sequence[float],
                   episode: Episode) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Return injected magnitudes and per-observation delta (same input order).

    Does not add fake epochs or change raw photometric errors. This makes the
    visibility problem explicit: an event between observations is not sampled.
    """
    if len(times) != len(magnitudes) or not times:
        raise ValueError("Time and magnitude vectors must be same nonzero length")
    if any(not math.isfinite(v) for v in (*times, *magnitudes)):
        raise ValueError("Nonfinite input observation")
    sign = 1.0 if episode.direction == "fading" else -1.0
    deltas = []
    for t in times:
        dt = abs(t - episode.center_time)
        if episode.shape == "box":
            weight = 1.0 if dt <= episode.duration_days / 2 else 0.0
        else:
            weight = math.exp(-4 * math.log(2) * (dt / episode.duration_days) ** 2)
        deltas.append(sign * episode.amplitude_mag * weight)
    return tuple(y + d for y, d in zip(magnitudes, deltas)), tuple(deltas)


def wilson_interval(successes: int, trials: int, confidence: float = 0.95) -> tuple[float, float] | None:
    """Binomial Wilson-score interval: a descriptive Monte Carlo uncertainty.

    Synthetic experiments may violate iid assumptions; this is NOT a survey
    completeness confidence interval or a calibrated physical detection rate.
    """
    if isinstance(successes, bool) or isinstance(trials, bool):
        raise ValueError("Counts must be integers")
    if not isinstance(successes, int) or not isinstance(trials, int) or not 0 <= successes <= trials:
        raise ValueError("Require 0 <= successes <= trials, both integers")
    if not 0 < confidence < 1 or not math.isfinite(confidence):
        raise ValueError("Invalid confidence level")
    if trials == 0:
        return None
    z = NormalDist().inv_cdf((1 + confidence) / 2)
    phat = successes / trials
    denominator = 1 + z * z / trials
    midpoint = (phat + z * z / (2 * trials)) / denominator
    half = z * math.sqrt(phat * (1 - phat) / trials + z * z / (4 * trials * trials)) / denominator
    return max(0., midpoint-half), min(1., midpoint+half)


def exposure_coverage(times: Sequence[float], episode: Episode,
                      min_points: int = 2, fractional_depth: float = 0.5) -> dict:
    """Count observation opportunities where the injected event is measurable.

    Counts independent epochs; cannot assert real detectability or cross-survey
    timing alignment. An event with no sampled epochs is censored, not a miss.
    """
    if not isinstance(min_points, int) or min_points < 1:
        raise ValueError("min_points must be a positive integer")
    if not 0 < fractional_depth <= 1:
        raise ValueError("fractional_depth must be in (0,1]")
    if not all(math.isfinite(t) for t in times):
        raise ValueError("Nonfinite observation epoch")
    _, deltas = inject_episode(tuple(times), (0.,)*len(times), episode)
    threshold = episode.amplitude_mag * fractional_depth
    n = sum(abs(d) >= threshold and abs(d) > 0 for d in deltas)
    return {"epochs_above_fractional_depth": n,
            "at_least_minimum_epochs_sampled": n >= min_points,
            "minimum_required_epochs": min_points,
            "fractional_depth_threshold": fractional_depth}