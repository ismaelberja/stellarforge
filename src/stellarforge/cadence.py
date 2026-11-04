"""Survey-window selection effects without invented astrophysical detections.

The computed observable-window fraction is a *geometrical cadence diagnostic*,
NOT detection efficiency, observational completeness, or a probability of an
actual dip or burst. A duration-d event is counted if >=k observation epochs
fall inside its hypothetical time window, without using magnitudes or errors.
This calculation is exact under the explicitly assumed uniform event-start
prior over [first observation, last observation - d].
"""
from __future__ import annotations

import math
import statistics
from collections.abc import Sequence


def clean_epochs(epochs: Sequence[float]) -> list[float]:
    values = [float(x) for x in epochs]
    if any(not math.isfinite(v) for v in values):
        raise ValueError("All timestamps must be finite")
    ordered = sorted(values)
    if len(ordered) != len(set(ordered)):
        raise ValueError("Duplicate timestamps; deduplicate through raw QC")
    return ordered


def window_coverage_fraction(epochs: Sequence[float], duration_days: float,
                             *, minimum_points: int = 2) -> float | None:
    """Exact fraction of possible start times containing k observed epochs.

    For sorted t and event [s,s+d], k consecutive points t[i..i+k-1] occur
    in the event exactly when s lies in [t[i+k-1]-d, t[i]]. Therefore the
    answer is the length of the union of these intervals, clipped to the
    possible event-start domain [t[0],t[-1]-d], divided by its length.
    Endpoints have zero measure. Handles the degenerate d==span separately.
    """
    t = clean_epochs(epochs)
    if not math.isfinite(duration_days) or duration_days <= 0:
        raise ValueError("Duration must be finite and strictly positive")
    if not isinstance(minimum_points, int) or minimum_points < 1:
        raise ValueError("minimum_points must be positive integer")
    if len(t) < minimum_points or len(t) < 2:
        return None
    span = t[-1] - t[0]
    if duration_days > span:
        return None
    if math.isclose(duration_days, span, rel_tol=1e-12, abs_tol=1e-9):
        return 1.0 if len(t) >= minimum_points else None
    start_min, start_max = t[0], t[-1] - duration_days
    intervals = []
    for idx in range(len(t) - minimum_points + 1):
        lower = max(start_min, t[idx + minimum_points - 1] - duration_days)
        upper = min(start_max, t[idx])
        if upper > lower:
            intervals.append((lower, upper))
    if not intervals:
        return 0.0
    intervals.sort()
    union = 0.0
    left, right = intervals[0]
    for a, b in intervals[1:]:
        if a <= right:
            right = max(right, b)
        else:
            union += right - left
            left, right = a, b
    union += right - left
    return min(1.0, max(0.0, union / (start_max - start_min)))


def cadence_report(epochs: Sequence[float], *, durations_days: Sequence[float] = (2, 5, 10, 20, 40),
                   season_gap_days: float = 75, minimum_points: int = 2) -> dict:
    t = clean_epochs(epochs)
    if not math.isfinite(season_gap_days) or season_gap_days <= 0:
        raise ValueError("season_gap_days must be > 0")
    if not durations_days or len(durations_days) > 50:
        raise ValueError("Specify between 1 and 50 durations")
    if len({float(d) for d in durations_days}) != len(durations_days):
        raise ValueError("Repeated event duration")
    duration_results = {}
    for duration in durations_days:
        if not math.isfinite(float(duration)) or float(duration) <= 0:
            raise ValueError("Duration must be > 0")
        duration_results[str(float(duration))] = window_coverage_fraction(
            t, float(duration), minimum_points=minimum_points)
    gaps = [b - a for a, b in zip(t, t[1:])]
    n_seasons = (1 + sum(g > season_gap_days for g in gaps)) if t else 0
    return {
        "epochs": len(t),
        "span_days": t[-1]-t[0] if len(t) > 1 else None,
        "median_gap_days": statistics.median(gaps) if gaps else None,
        "max_gap_days": max(gaps) if gaps else None,
        "season_gap_days": season_gap_days,
        "n_observing_seasons_by_gap_heuristic": n_seasons,
        "minimum_points_in_hypothetical_event": minimum_points,
        "event_duration_days_to_exact_cadence_window_fraction": duration_results,
        "quantity": "fraction_of_uniform_possible_event_start_times_containing_at_least_k_observations",
        "not_equivalent_to": ["photometric_detection_efficiency", "survey_completeness", "physical_event_rate"],
        "time_scale": "caller_specifies_single_unconverted_time_column",
        "science_claim": False,
    }