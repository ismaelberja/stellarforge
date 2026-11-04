"""Sky coordinate quality checks for the pilot survey cross-match.

For research-grade epoch propagation, use astropy SkyCoord.apply_space_motion
with astrometric uncertainties/covariances. The function below is only a
small-angle prototype, deliberately labeled approximate.
"""
from __future__ import annotations

import math


def validate_icrs(ra_deg: float, dec_deg: float) -> None:
    if not math.isfinite(ra_deg) or not 0.0 <= ra_deg < 360.0:
        raise ValueError("ICRS right ascension must be in [0, 360) degrees")
    if not math.isfinite(dec_deg) or not -90.0 <= dec_deg <= 90.0:
        raise ValueError("ICRS declination must be in [-90, 90] degrees")


def angular_separation_arcsec(
    ra1: float, dec1: float, ra2: float, dec2: float,
) -> float:
    """Stable great-circle separation, in arcseconds, even across RA=0."""
    validate_icrs(ra1, dec1)
    validate_icrs(ra2, dec2)
    ra_a, dec_a, ra_b, dec_b = map(math.radians, (ra1, dec1, ra2, dec2))
    dra = ((ra_b - ra_a + math.pi) % (2.0 * math.pi)) - math.pi
    sine = math.sin(dra) * math.cos(dec_b)
    cosine = math.cos(dec_a) * math.sin(dec_b) - math.sin(dec_a) * math.cos(dec_b) * math.cos(dra)
    angle = math.atan2(math.hypot(sine, cosine),
                       math.sin(dec_a) * math.sin(dec_b) + math.cos(dec_a) * math.cos(dec_b) * math.cos(dra))
    return math.degrees(angle) * 3600.0


def approximate_proper_motion_position(
    ra_deg: float, dec_deg: float, pmra_mas_year: float,
    pmdec_mas_year: float, delta_years: float,
) -> tuple[float, float]:
    """Small-angle PM propagation, for engineering tests, NOT final cross-matching.

    Gaia's pmra is mu_alpha*cos(dec) in mas/year, not raw dRA/dt.
    Parallax, perspective acceleration and full astrometric covariance are
    ignored. Research-grade matching must call astropy for epoch propagation.
    """
    validate_icrs(ra_deg, dec_deg)
    for x in (pmra_mas_year, pmdec_mas_year, delta_years):
        if not math.isfinite(x):
            raise ValueError("Proper motions and time offset must be finite")
    cos_dec = math.cos(math.radians(dec_deg))
    if abs(cos_dec) < 1e-3:
        raise ValueError("Use full spherical Astropy propagation near the poles")
    delta_ra_deg = pmra_mas_year * delta_years / (3_600_000.0 * cos_dec)
    delta_dec_deg = pmdec_mas_year * delta_years / 3_600_000.0
    new_dec = dec_deg + delta_dec_deg
    if not -90 <= new_dec <= 90:
        raise ValueError("Result crosses a pole; use Astropy propagation")
    return (ra_deg + delta_ra_deg) % 360.0, new_dec