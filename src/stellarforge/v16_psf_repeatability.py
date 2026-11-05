"""Provisional ZTF single-Gaussian shape and multi-exposure consistency diagnostics.

This is *not* empirical PSF photometry or astrophysical source identification.
A robust 2D, axis-aligned Gaussian plus local tilted background is only a
shape proxy: anisotropic wings, saturation, nebulosity, blends, WCS biases,
and source variability are not modeled. Raw FITS pixels are never exported.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import io
import math
import statistics
from urllib.error import HTTPError, URLError

from .v15_image_pixels import (
    fetch_fits_cutout, inspect_fits_cutout, propose_image_candidates,
)

PSF_OK = {"PSF_PROXY_PROVISIONAL_ONLY", "PSF_PROXY_REVIEW_REQUIRED"}


def _unverified(status: str, **facts) -> dict:
    return {
        "status": status, **facts,
        "gaia_ztf_identity_confirmed": False,
        "field_deblended": False,
        "astrophysical_companion_confirmed": False,
        "scientific_psf_calibrated": False,
    }


def fit_local_gaussian_proxy(raw: bytes, *, expected_ra_deg: float,
                             expected_dec_deg: float,
                             image_kind: str = "science") -> dict:
    """Robust local 2D Gaussian *proxy*, not ZTF photometric/PSF calibration.

    Uses an annulus for background/noise, a 7 px circular fit region, bounded
    peak center, and a planar background. Two-source comparison is NOT done.
    The center residual is relative to the archive header WCS, not external
    astrometric calibration.
    """
    if image_kind not in ("science", "reference_coadd"):
        raise ValueError("Invalid image kind")
    image_screen = inspect_fits_cutout(
        raw, expected_ra_deg=expected_ra_deg, expected_dec_deg=expected_dec_deg)
    if image_screen["status"] != "PIXEL_WCS_PROVISIONAL_SCREEN_COMPLETED":
        return _unverified(
            "V15_IMAGE_GATE_INCOMPLETE",
            source_image_status=image_screen["status"],
            image_kind=image_kind,
        )

    import numpy as np
    from astropy.io import fits
    from astropy.wcs import WCS
    from scipy.optimize import least_squares

    with fits.open(io.BytesIO(raw), memmap=False) as hdul:
        images = [h for h in hdul if getattr(h, "data", None) is not None
                  and getattr(h.data, "ndim", None) == 2]
        if len(images) != 1:
            raise ValueError("Expected a single 2D astronomical image")
        data = np.asarray(images[0].data, dtype=float).copy()
        header = images[0].header.copy()
    wcs = WCS(header)
    tx, ty = map(float, wcs.world_to_pixel_values(
        expected_ra_deg, expected_dec_deg))
    yy, xx = np.indices(data.shape)
    radius = np.hypot(xx - tx, yy - ty)
    valid = np.isfinite(data)
    annulus = valid & (radius >= 9.0) & (radius <= 15.0)
    fitmask = valid & (radius <= 7.0)
    if annulus.sum() < 75 or fitmask.sum() < 100:
        return _unverified("INSUFFICIENT_FINITE_BACKGROUND_OR_FIT_PIXELS",
                           image_kind=image_kind)
    ann = data[annulus]
    bg = float(np.median(ann))
    noise = float(1.4826 * np.median(np.abs(ann - bg)))
    if not np.isfinite(noise) or noise <= 0:
        return _unverified("UNUSABLE_LOCAL_NOISE_PROXY", image_kind=image_kind)
    core = valid & (radius <= 2.5)
    if core.sum() < 8:
        return _unverified("INSUFFICIENT_CORE_PIXELS", image_kind=image_kind)
    core_max = float(np.max(data[core]))
    amp = core_max - bg
    if amp < 5 * noise:
        return _unverified(
            "NO_SIGNIFICANT_CENTRAL_PEAK_FOR_PROXY",
            image_kind=image_kind,
            local_noise_proxy=round(noise, 6),
            central_peak_snr_proxy=round(amp / noise, 3))
    cy, cx = np.unravel_index(
        np.argmax(np.where(core, data, -np.inf)), data.shape)

    xfit = xx[fitmask].astype(float)
    yfit = yy[fitmask].astype(float)
    zfit = data[fitmask]
    pix_origin_x, pix_origin_y = tx, ty

    def gaussian_model(p, xs, ys):
        amplitude, x0, y0, sx, sy, constant, dx, dy = p
        expterm = -.5 * (
            ((xs - x0) / sx) ** 2 + ((ys - y0) / sy) ** 2)
        return (amplitude * np.exp(expterm) + constant
                + dx * (xs - pix_origin_x) + dy * (ys - pix_origin_y))

    def residuals(p):
        return (gaussian_model(p, xfit, yfit) - zfit) / noise

    # Fit may move at most 2.5 pixels from the WCS-propagated Gaia target.
    # A fitted model is *not* accepted as an independent source match.
    bounds_low = [0.0, tx - 2.5, ty - 2.5,
                  0.6, 0.6, bg - 10*noise, -2*noise, -2*noise]
    bounds_high = [max(amp * 8, 10 * noise), tx + 2.5, ty + 2.5,
                   5.0, 5.0, bg + 10*noise, 2*noise, 2*noise]
    p0 = [
        amp, float(np.clip(cx, tx-2.49, tx+2.49)),
        float(np.clip(cy, ty-2.49, ty+2.49)),
        1.5, 1.5, bg, 0., 0.
    ]
    fitted = least_squares(
        residuals, p0, bounds=(bounds_low, bounds_high),
        loss="soft_l1", f_scale=2.0, max_nfev=400)
    if not fitted.success or not np.isfinite(fitted.x).all():
        return _unverified("PSF_PROXY_FIT_NOT_CONVERGED", image_kind=image_kind)
    amplitude, x0, y0, sx, sy, local_bg, _, _ = map(float, fitted.x)
    model = gaussian_model(fitted.x, xfit, yfit)
    residual = zfit - model
    # Outer residual from radius > 2.5 px avoids primary peak mismatch,
    # but is NOT a companion detection or a realistic PSF residual model.
    outer = ((xfit - x0)**2 + (yfit - y0)**2) >= 2.5**2
    max_residual = float(np.max(residual[outer])) / noise if outer.any() else 0.
    median_abs_residual = float(np.median(np.abs(residual))) / noise
    # Obtain signed sky offset in the ICRS tangent-plane approximation.
    actual_ra, actual_dec = map(float, wcs.pixel_to_world_values(x0, y0))
    dra = ((actual_ra - expected_ra_deg + 180) % 360) - 180
    east_arcsec = dra * math.cos(math.radians(expected_dec_deg)) * 3600
    north_arcsec = (actual_dec - expected_dec_deg) * 3600
    pixel_scale = image_screen["pixel_scale_arcsec_mean"]
    fwhm_x = 2.354820045 * sx * pixel_scale
    fwhm_y = 2.354820045 * sy * pixel_scale
    axis_ratio = max(sx, sy) / min(sx, sy)
    bounds_warning = bool(min(sx, sy) <= .65 or max(sx, sy) >= 4.9
                          or abs(x0-tx) >= 2.45 or abs(y0-ty) >= 2.45)
    review = bool(max_residual >= 6 or axis_ratio >= 1.6 or bounds_warning
                  or abs(east_arcsec) >= 1.5 or abs(north_arcsec) >= 1.5)
    return _unverified(
        "PSF_PROXY_REVIEW_REQUIRED" if review else "PSF_PROXY_PROVISIONAL_ONLY",
        image_kind=image_kind,
        fits_sha256=hashlib.sha256(raw).hexdigest(),
        image_shape_pixels=list(map(int, data.shape)),
        local_background_median=round(local_bg, 6),
        local_noise_mad_proxy=round(noise, 6),
        central_peak_snr_proxy=round(amplitude / noise, 3),
        model="single_axis_aligned_elliptical_Gaussian_plus_local_plane",
        fitted_fwhm_x_arcsec=round(fwhm_x, 4),
        fitted_fwhm_y_arcsec=round(fwhm_y, 4),
        fitted_axis_ratio_proxy=round(axis_ratio, 4),
        fitted_centroid_east_minus_Gaia_arcsec=round(east_arcsec, 5),
        fitted_centroid_north_minus_Gaia_arcsec=round(north_arcsec, 5),
        fitted_centroid_distance_from_Gaia_arcsec=round(
            math.hypot(east_arcsec, north_arcsec), 5),
        median_absolute_residual_over_noise=round(median_abs_residual, 3),
        max_outer_positive_residual_over_noise=round(max_residual, 3),
        fit_n_pixels=int(fitmask.sum()),
        optimizer_success=True,
        fit_parameter_near_bound=bounds_warning,
        residual_peak_is_not_verified_companion=True,
        single_gaussian_model_is_not_independent_empirical_psf=True,
        wcs_independently_recalibrated=False,
    )


def summarize_science_repeatability(exposures: list[dict]) -> dict:
    """Only independent SCIENCE exposure summaries; NEVER count ref coadds."""
    good = [e for e in exposures
            if e.get("kind") == "science"
            and e.get("fit", {}).get("status") in PSF_OK]
    by_hash = {}
    for row in good:
        h = row["fit"]["fits_sha256"]
        by_hash.setdefault(h, row)
    distinct = list(by_hash.values())
    if len(distinct) < 2:
        return {
            "status": "INSUFFICIENT_INDEPENDENT_SCIENCE_EXPOSURES",
            "n_independent_science_images": len(distinct),
            "scientific_astrometric_consistency_confirmed": False,
        }
    east = [r["fit"]["fitted_centroid_east_minus_Gaia_arcsec"] for r in distinct]
    north = [r["fit"]["fitted_centroid_north_minus_Gaia_arcsec"] for r in distinct]
    fwhm = [(r["fit"]["fitted_fwhm_x_arcsec"] +
             r["fit"]["fitted_fwhm_y_arcsec"]) / 2 for r in distinct]
    offsets = [
        math.hypot(a["fit"]["fitted_centroid_east_minus_Gaia_arcsec"] -
                   b["fit"]["fitted_centroid_east_minus_Gaia_arcsec"],
                   a["fit"]["fitted_centroid_north_minus_Gaia_arcsec"] -
                   b["fit"]["fitted_centroid_north_minus_Gaia_arcsec"])
        for i, a in enumerate(distinct) for b in distinct[i+1:]
    ]
    mjd = [r["mjd"] for r in distinct]
    return {
        "status": "DESCRIPTIVE_REPEATABILITY_ONLY_NO_ASTROMETRIC_CALIBRATION",
        "n_independent_science_images": len(distinct),
        "mjd_span_days": round(max(mjd)-min(mjd), 4),
        "max_pairwise_signed_centroid_residual_difference_arcsec":
            round(max(offsets), 5),
        "east_residual_range_arcsec": round(max(east)-min(east), 5),
        "north_residual_range_arcsec": round(max(north)-min(north), 5),
        "median_gaussian_fwhm_proxy_arcsec": round(statistics.median(fwhm), 4),
        "observed_motion_or_single_source_confirmed": False,
        "wcs_systematics_removed": False,
        "reference_images_excluded": True,
    }


def review_oid_band_psf(curve: dict, *, timeout: float = 8.0,
                        max_attempts: int = 4,
                        fetch=fetch_fits_cutout,
                        fit=fit_local_gaussian_proxy) -> dict:
    """Review up to three independent science images, reference as fallback.

    Unlike v1.5, does not stop at first successful science observation.
    HTTP failures and incomplete image fits must remain explicit evidence gaps.
    """
    if not 1 <= max_attempts <= 4:
        raise ValueError("Attempt limit must be 1..4")
    records = []
    science_success = False
    for candidate in curve["candidates"][:max_attempts]:
        if candidate["kind"] == "reference_coadd" and science_success:
            break
        entry = {"kind": candidate["kind"],
                 "mjd": candidate["mjd"] if candidate["kind"] == "science" else None}
        try:
            raw = fetch(candidate["url"], timeout=timeout)
            fit_result = fit(
                raw, expected_ra_deg=candidate["expected_ra_deg"],
                expected_dec_deg=candidate["expected_dec_deg"],
                image_kind=candidate["kind"])
            entry["status"] = fit_result["status"]
            entry["fit"] = fit_result
            if candidate["kind"] == "science" and fit_result["status"] in PSF_OK:
                science_success = True
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            entry["status"] = "FITS_OR_MODEL_FAILED"
            entry["error_type"] = type(exc).__name__
            if isinstance(exc, HTTPError):
                entry["http_status"] = int(exc.code)
        records.append(entry)
    good = [r for r in records if r.get("fit", {}).get("status") in PSF_OK]
    science = [r for r in good if r["kind"] == "science"]
    return {
        "ztf_oid": curve["ztf_oid"],
        "band": curve["band"],
        "images_attempted": len(records),
        "images_with_provisional_psf_proxy": len(good),
        "science_images_with_psf_proxy": len(science),
        "reference_coadd_fallback": bool(
            not science and any(r["kind"] == "reference_coadd" for r in records)),
        "attempts": records,
        "repeatability": summarize_science_repeatability(records),
        "gaia_ztf_physical_identity_confirmed": False,
        "psf_deblending_verified": False,
    }
