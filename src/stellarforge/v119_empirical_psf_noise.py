"""v1.19: independent INTERNAL star-holdout PSF and bounded detector-noise tools.

These routines never use the archived DAOPhot PSF as their fitted template.
Inputs must already be same-exposure, sky-registered source stamps from
original science and WCS-aligned ZTF bitmasks, vetted upstream.
Passing an arbitrary array does not authenticate real ZTF provenance.
No claim about unknown ZTF original PSF-training membership, Gaia physical
identity, WCS calibration or discovery is made by these functions.
Original pixels, IDs and empirical PSF arrays must remain ephemeral.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np

BAD_MASK_BITS = 6141  # ZTF deleterious bits 0,2..10,12 (see v113)
MIN_TRAIN_STARS = 3
MIN_TEST_STARS = 2
MAX_REGISTERED_SUBPIXEL_OFFSET = 0.08


@dataclass(frozen=True)
class RegisteredStar:
    """One distinct star in ONE exposure, registered to a common pixel grid.

    registered_offset_xy is a checked centering error AFTER registration,
    not the raw detector fractional phase. No ID can occur in both groups.
    """

    gaia_source_id: str
    exposure_id: str
    pixels_dn: np.ndarray
    mask_bits: np.ndarray
    registered_offset_xy: tuple[float, float] = (0.0, 0.0)


def _one_star(star: RegisteredStar, shape: tuple[int, int]) -> tuple[np.ndarray, float]:
    if not isinstance(star, RegisteredStar):
        raise ValueError("Expected registered source stamp with source/exposure IDs")
    image = np.asarray(star.pixels_dn)
    mask = np.asarray(star.mask_bits)
    if image.shape != shape or mask.shape != shape:
        raise ValueError("Unregistered or differently sized source/mask stamp")
    if not np.issubdtype(image.dtype, np.number) or not np.isfinite(image).all():
        raise ValueError("Source contains invalid or nonfinite original DN")
    if not np.issubdtype(mask.dtype, np.number):
        raise ValueError("Non-numeric bitmask")
    mask_float = np.asarray(mask, dtype=np.float64)
    if (not np.isfinite(mask_float).all() or np.any(mask_float < 0)
            or np.any(mask_float > 65535)
            or not np.all(mask_float == np.floor(mask_float))):
        raise ValueError("Invalid original ZTF bitmask values")
    try:
        dx, dy = (float(v) for v in star.registered_offset_xy)
    except (TypeError, ValueError) as exc:
        raise ValueError("Missing measured registration residual") from exc
    if (not all(math.isfinite(v) for v in (dx, dy))
            or max(abs(dx), abs(dy)) > MAX_REGISTERED_SUBPIXEL_OFFSET):
        raise ValueError("Star not registered to the common PSF grid")
    img = np.asarray(image, dtype=np.float64)
    good = (mask_float.astype(np.uint16) & BAD_MASK_BITS) == 0
    yy, xx = np.indices(shape, dtype=float)
    radius = shape[0] // 2
    rr = np.hypot(xx - radius, yy - radius)
    core = rr <= 3.5
    ap = rr <= radius - 3
    ann = rr >= radius - 1
    if np.any(~good & core):
        raise ValueError("Masked/saturated original stellar core")
    if np.sum(good & ann) < 40 or np.sum(good & ap) < .9 * np.sum(ap):
        raise ValueError("Insufficient original unmasked star/sky pixels")
    sky = img[good & ann]
    sky_level = float(np.median(sky))
    sky_sigma = 1.4826 * float(np.median(np.abs(sky - sky_level)))
    if not 1e-7 < sky_sigma < 1e8:
        raise ValueError("Invalid independent sky noise proxy")
    flux = float(np.sum((img - sky_level)[good & ap]))
    if (not math.isfinite(flux) or
            flux / (sky_sigma * math.sqrt(int(np.sum(good & ap)))) < 20):
        raise ValueError("Unusable positive signal-to-sky proxy")
    normalized = np.where(good, (img - sky_level) / flux, np.nan)
    return normalized, sky_sigma


def train_and_holdout_empirical_psf(
    training: Sequence[RegisteredStar], validation: Sequence[RegisteredStar],
) -> dict:
    """Fit normalized PSF to training stars and check DIFFERENT held-out stars.

    Independent inside this new model only; provenance of source stamps and
    the original DAOPhot PSF training roster are NOT verified by this API.
    Returned images and IDs are memory-only; never publish them in Git.
    """
    train, test = list(training), list(validation)
    if len(train) < MIN_TRAIN_STARS or len(test) < MIN_TEST_STARS:
        raise ValueError("Insufficient distinct training/held-out stars")
    if len(train) + len(test) > 64:
        raise ValueError("Unbounded field-star sample")
    stars = train + test
    if any(not isinstance(s, RegisteredStar) for s in stars):
        raise ValueError("Missing registered source metadata")
    ids = [s.gaia_source_id for s in stars]
    if (any(not isinstance(i, str) or not i.isdecimal() for i in ids)
            or len(set(ids)) != len(ids)):
        raise ValueError("Duplicate or unauthenticated train/test source IDs")
    exposures = {s.exposure_id for s in stars}
    if len(exposures) != 1 or any(not isinstance(e, str) or not e for e in exposures):
        raise ValueError("Training and holdout must share one science exposure")
    shape = np.asarray(stars[0].pixels_dn).shape
    if (len(shape) != 2 or shape[0] != shape[1]
            or shape[0] % 2 != 1 or not 19 <= shape[0] <= 35):
        raise ValueError("Unsupported bounded odd-sized star PSF stamp")
    prepared = [_one_star(s, shape) for s in stars]
    stack = np.stack([x[0] for x in prepared[:len(train)]], axis=0)
    if np.any(np.sum(np.isfinite(stack), axis=0) < 2):
        raise ValueError("PSF pixels not supported by two independent training stars")
    # Equal source weight: brightest star cannot silently dominate the model.
    with np.errstate(invalid="ignore"):
        model = np.nanmedian(stack, axis=0)
    model = np.maximum(np.where(np.isfinite(model), model, 0.0), 0.0)
    total = float(np.sum(model))
    if not math.isfinite(total) or total <= 0:
        raise ValueError("Empirical PSF normalization failed")
    model /= total
    results = []
    for s, (_, sky_sigma) in zip(test, prepared[len(train):]):
        # Use every valid held-out pixel for a whole-star model comparison.
        mask = np.asarray(s.mask_bits, dtype=np.uint16)
        valid = (mask & BAD_MASK_BITS) == 0
        if int(valid.sum()) < shape[0] * shape[1] * .85:
            raise ValueError("Insufficient held-out source pixels")
        image = np.asarray(s.pixels_dn, dtype=float)
        mat = np.column_stack([model[valid], np.ones(int(valid.sum()))])
        amp, bg = np.linalg.lstsq(mat, image[valid], rcond=None)[0]
        if not math.isfinite(amp) or amp <= 0 or not math.isfinite(bg):
            raise ValueError("Invalid held-out source fit")
        residual = image[valid] - (amp * model[valid] + bg)
        rms_ratio = math.sqrt(float(np.mean(residual ** 2))) / sky_sigma
        results.append({
            "gaia_source_id": s.gaia_source_id,
            "residual_rms_over_sky_mad": round(rms_ratio, 6),
            "status": "DESCRIPTIVE_HELDOUT_PROFILE_OK" if rms_ratio <= 3.0
                      else "HELDOUT_PROFILE_REVIEW_REQUIRED",
        })
    return {
        "status": "INTERNAL_DISTINCT_STAR_PSF_HOLDOUT_COMPLETED",
        "empirical_psf": model,
        "training_source_ids": tuple(s.gaia_source_id for s in train),
        "heldout_source_ids": tuple(s.gaia_source_id for s in test),
        "n_distinct_training_stars": len(train),
        "n_distinct_heldout_stars": len(test),
        "n_heldout_profile_reviews": sum(
            v["status"] == "HELDOUT_PROFILE_REVIEW_REQUIRED" for v in results),
        "heldout_results": results,
        "uses_original_ztf_daophot_coefficients": False,
        "internal_psf_training_and_validation_star_ids_disjoint": True,
        "original_ztf_psf_training_membership_verified": False,
        "genuine_independent_ztf_wcs_or_psf_calibration": False,
        "astrophysical_source_identity_confirmed": False,
    }


def diagonal_ccd_variance_dn2(
    source_dn: np.ndarray, *, sky_dn: float,
    gain_e_per_dn: float, read_noise_e: float,
) -> np.ndarray:
    """Approximate diagonal Poisson+read variance in DN^2.

    source_dn is nonnegative expected sky-subtracted signal, NOT raw bias DN;
    sky_dn is nonnegative expected sky. Correlations are NOT included.
    """
    a = np.asarray(source_dn, dtype=float)
    if a.ndim != 2 or a.size > 35*35 or not np.isfinite(a).all():
        raise ValueError("Invalid model source DN image")
    params = (sky_dn, gain_e_per_dn, read_noise_e)
    if (not all(math.isfinite(v) for v in params) or sky_dn < 0
            or gain_e_per_dn <= 0 or read_noise_e < 0 or np.any(a < 0)):
        raise ValueError("Invalid physical CCD noise inputs")
    g = gain_e_per_dn
    return (a + sky_dn) / g + (read_noise_e / g) ** 2


def estimate_blank_sky_aperture_correlation(
    independent_windows_dn: np.ndarray, aperture: np.ndarray,
) -> dict:
    """Var(sum pixels)/sum(Var pixels), using >=16 distinct blank-sky windows.

    The caller must verify windows do not overlap, contain sources, or have
    differing backgrounds. Not a full CCD covariance or PSF-flux calibration.
    """
    windows = np.asarray(independent_windows_dn, dtype=float)
    ap = np.asarray(aperture)
    if (windows.ndim != 3 or not 16 <= windows.shape[0] <= 4096
            or windows.shape[1] > 35 or windows.shape[2] > 35
            or min(windows.shape[1:]) < 5
            or not np.isfinite(windows).all()
            or ap.shape != windows.shape[1:] or ap.dtype != np.bool_
            or not 4 <= int(ap.sum()) <= windows.shape[1] * windows.shape[2]):
        raise ValueError("Insufficient or invalid independent blank-sky windows")
    per_pixel = np.var(windows[:, ap], axis=0, ddof=1)
    indep = float(np.sum(per_pixel))
    sums = np.sum(windows[:, ap], axis=1)
    observed = float(np.var(sums, ddof=1))
    if not (math.isfinite(indep) and math.isfinite(observed)
            and indep > 0 and observed > 0):
        raise ValueError("Unidentifiable empirical aperture noise")
    return {
        "n_independent_blank_sky_windows": int(windows.shape[0]),
        "n_aperture_pixels": int(ap.sum()),
        "diagonal_aperture_variance_dn2": round(indep, 6),
        "empirical_aperture_variance_dn2": round(observed, 6),
        "empirical_variance_ratio": round(observed / indep, 6),
        "covariance_model": "aperture-level empirical only; no full CCD covariance",
        "survey_uncertainty_calibrated": False,
    }


def public_aggregate_only(result: dict) -> dict:
    """Whitelist publishable counts: never emit raw PSF, IDs or pixels."""
    if result.get("status") != "INTERNAL_DISTINCT_STAR_PSF_HOLDOUT_COMPLETED":
        raise ValueError("Incomplete empirical PSF result")
    return {
        "status": result["status"],
        "n_distinct_training_stars": result["n_distinct_training_stars"],
        "n_distinct_heldout_stars": result["n_distinct_heldout_stars"],
        "n_heldout_profile_reviews": result["n_heldout_profile_reviews"],
        "original_ztf_psf_training_membership_verified": False,
        "genuine_independent_ztf_wcs_or_psf_calibration": False,
    }
