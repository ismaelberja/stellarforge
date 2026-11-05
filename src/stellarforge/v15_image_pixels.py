"""Conservative pixel-level inspection of *real* small ZTF FITS cutouts.

This is an engineering screening tool, not a source association algorithm.
A local maximum, even at the Gaia-predicted coordinate, cannot confirm that
Gaia and ZTF refer to the same star, nor does an empty image rule out blends.
Only aggregate derived diagnostics leave the ephemeral processing environment.

The image-specific optional dependencies (NumPy, SciPy, Astropy) are imported
inside the functions, so the base CLI and other project tests remain light.
"""
from __future__ import annotations

from collections import defaultdict
import csv
import hashlib
import io
import math
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

from .association import mjd_to_approximate_julian_year, propagate_gaia_position
from .v14_field_review import ztf_science_cutout_url, ztf_reference_cutout_url

MAX_FITS_BYTES = 3_000_000
MIN_FINITE_FRACTION = 0.80
MAX_IMAGE_SIDE = 400
IMAGE_HOST = "irsa.ipac.caltech.edu"


def _validate_official_cutout(url: str) -> None:
    parsed = urlparse(url)
    if (parsed.scheme != "https" or parsed.hostname != IMAGE_HOST
            or parsed.username is not None or parsed.password is not None
            or parsed.port not in (None, 443)
            or not parsed.path.endswith(".fits")
            or not (parsed.path.startswith("/ibe/data/ztf/products/sci/")
                    or parsed.path.startswith("/ibe/data/ztf/products/ref/"))):
        raise ValueError("Only official ZTF science/reference FITS cutouts are allowed")
    query = parse_qs(parsed.query)
    center, size = query.get("center"), query.get("size")
    if not center or not size or len(center) != 1 or len(size) != 1:
        raise ValueError("Missing unambiguous sky center or cutout size")
    from .coordinates import validate_icrs
    try:
        ra, dec = map(float, center[0].split(","))
        width = float(size[0].removesuffix("arcsec"))
    except (ValueError, TypeError) as exc:
        raise ValueError("Malformed cutout center or size") from exc
    validate_icrs(ra, dec)
    if not size[0].endswith("arcsec") or not 20 <= width <= 90:
        raise ValueError("Unexpected cutout dimensions")


def fetch_fits_cutout(url: str, *, timeout: float = 12.0,
                      opener=urlopen) -> bytes:
    """Read at most 3 MB; no local FITS file is ever written by this module."""
    _validate_official_cutout(url)
    if not math.isfinite(timeout) or not 1 <= timeout <= 45:
        raise ValueError("Image request timeout must be between 1 and 45 s")
    req = Request(url, headers={
        "User-Agent": "StellarForge/1.5 bounded science FITS pixel audit",
        "Accept": "application/fits,application/octet-stream",
    })
    with opener(req, timeout=timeout) as response:
        raw = response.read(MAX_FITS_BYTES + 1)
    if len(raw) > MAX_FITS_BYTES or len(raw) < 2880:
        raise ValueError("Missing or excessive FITS payload")
    if not raw.startswith(b"SIMPLE  =") and not raw.startswith(b"XTENSION"):
        raise ValueError("Remote service did not return an uncompressed FITS file")
    return raw


def inspect_fits_cutout(raw: bytes, *, expected_ra_deg: float,
                        expected_dec_deg: float,
                        peak_sigma: float = 5.0) -> dict:
    """WCS + robust local-maxima screening of a bounded 2D FITS image.

    Gaussian smoothing and a median-based noise proxy identify *candidate*
    maxima only; no PSF fitting, source deblending, aperture flux calibration,
    or astrophysical classification is attempted. Every success is provisional.
    """
    import numpy as np
    from astropy.io import fits
    from astropy.wcs import WCS
    from astropy.wcs.utils import proj_plane_pixel_scales
    from scipy.ndimage import gaussian_filter, maximum_filter

    from .coordinates import validate_icrs

    validate_icrs(expected_ra_deg, expected_dec_deg)
    if not math.isfinite(peak_sigma) or not 3 <= peak_sigma <= 15:
        raise ValueError("Peak detection sigma outside safe range")
    if not 2880 <= len(raw) <= MAX_FITS_BYTES:
        raise ValueError("Invalid FITS payload size")

    with fits.open(io.BytesIO(raw), memmap=False, ignore_missing_simple=False) as hdul:
        candidates = [
            h for h in hdul
            if getattr(h, "data", None) is not None
            and getattr(h.data, "ndim", None) == 2
        ]
        if len(candidates) != 1:
            raise ValueError("Expected exactly one 2D FITS image plane")
        hdu = candidates[0]
        data = np.asarray(hdu.data, dtype=np.float64)
        hdr = hdu.header.copy()
    if data.ndim != 2 or min(data.shape) < 20 or max(data.shape) > MAX_IMAGE_SIDE:
        raise ValueError("FITS cutout dimensions outside 20..400 pixels")
    finite = np.isfinite(data)
    good_fraction = float(finite.mean())
    if good_fraction < MIN_FINITE_FRACTION:
        return {
            "status": "IMAGE_TOO_MANY_INVALID_PIXELS",
            "finite_pixel_fraction": round(good_fraction, 5),
            "wcs_checked": False,
            "deblending_completed": False,
            "confirmed_astrophysical_match": False,
        }
    wcs = WCS(hdr)
    if not wcs.has_celestial or wcs.pixel_n_dim != 2 or wcs.world_n_dim != 2:
        raise ValueError("Missing valid 2D celestial WCS")
    x, y = map(float, wcs.world_to_pixel_values(expected_ra_deg, expected_dec_deg))
    scales = np.asarray(proj_plane_pixel_scales(wcs), dtype=float) * 3600.0
    if not all(math.isfinite(v) and 0.2 < v < 5.0 for v in scales):
        raise ValueError("Implausible plate scale for a ZTF science cutout")
    height, width = data.shape
    if not (math.isfinite(x) and math.isfinite(y)
            and 3 <= x < width - 3 and 3 <= y < height - 3):
        return {
            "status": "PREDICTED_GAIA_TARGET_OUTSIDE_USABLE_IMAGE",
            "image_width_pixels": width,
            "image_height_pixels": height,
            "wcs_checked": True,
            "deblending_completed": False,
            "confirmed_astrophysical_match": False,
        }
    median = float(np.nanmedian(data))
    mad = float(np.nanmedian(np.abs(data[finite] - median)))
    rms_proxy = 1.4826 * mad
    if not math.isfinite(rms_proxy) or rms_proxy <= 1e-10:
        return {
            "status": "PIXEL_NOISE_PROXY_UNUSABLE",
            "wcs_checked": True,
            "deblending_completed": False,
            "confirmed_astrophysical_match": False,
        }
    filled = np.where(finite, data, median)
    blurred = gaussian_filter(filled, sigma=1.0)
    threshold = median + peak_sigma * rms_proxy
    maxima = (blurred == maximum_filter(blurred, size=5)) & (blurred > threshold)
    maxima[:3, :] = False
    maxima[-3:, :] = False
    maxima[:, :3] = False
    maxima[:, -3:] = False
    iy, ix = np.nonzero(maxima)
    pixscale = float(np.mean(scales))
    peaks = sorted(
        (
            {"x": int(px), "y": int(py),
             "offset_arcsec": math.hypot(px - x, py - y) * pixscale,
             "peak_height_proxy_sigma": (float(blurred[py, px]) - median) / rms_proxy}
            for px, py in zip(ix, iy)
        ),
        key=lambda p: p["offset_arcsec"],
    )
    central = peaks[0] if peaks and peaks[0]["offset_arcsec"] <= 2.5 * pixscale else None
    max_radius = min(12.0, min(height, width) * pixscale / 2)
    nearby_maxima = [
        p for p in peaks
        if p["offset_arcsec"] > 2.5 * pixscale
        and p["offset_arcsec"] <= max_radius
    ]
    return {
        "status": "PIXEL_WCS_PROVISIONAL_SCREEN_COMPLETED",
        "fits_sha256": hashlib.sha256(raw).hexdigest(),
        "image_width_pixels": int(width),
        "image_height_pixels": int(height),
        "finite_pixel_fraction": round(good_fraction, 5),
        "wcs_checked": True,
        "wcs_target_x_pixel": round(x, 4),
        "wcs_target_y_pixel": round(y, 4),
        "pixel_scale_arcsec_mean": round(pixscale, 5),
        "median_background_proxy": round(median, 6),
        "robust_noise_proxy": round(rms_proxy, 6),
        "n_local_maxima_above_threshold": len(peaks),
        "central_local_maximum_detected": central is not None,
        "central_peak_offset_arcsec": (
            round(central["offset_arcsec"], 5) if central else None),
        "n_additional_local_maxima_within_12_arcsec": len(nearby_maxima),
        "additional_maximum_offsets_arcsec": [
            round(p["offset_arcsec"], 3) for p in nearby_maxima[:10]],
        "maxima_are_not_confirmed_companions": True,
        "deblending_completed": False,
        "psf_fitted": False,
        "confirmed_astrophysical_match": False,
        "image_contamination_ruled_out": False,
        "limitations": [
            "Smoothing and local maxima are heuristics; close companions are unresolved.",
            "The WCS is trusted as provided, not independently astrometrically recalibrated.",
            "No PSF model, masking of cosmic rays or extended nebulosity, aperture photometry, "
            "or source multiplicity inference is included.",
            "Gaia 2D proper motion omits parallax/covariance; an apparent image peak "
            "cannot prove Gaia/ZTF identity.",
        ],
    }


def propose_image_candidates(ztf_csv: bytes, *,
                             target_ra_deg: float, target_dec_deg: float,
                             target_pmra: float, target_pmdec: float,
                             max_science_per_curve: int = 3) -> list[dict]:
    """Bounded independent OID-band image attempts: median, early and late."""
    if max_science_per_curve not in (1, 2, 3):
        raise ValueError("Max science exposures per curve must be 1..3")
    from .coordinates import validate_icrs
    validate_icrs(target_ra_deg, target_dec_deg)
    rows = csv.DictReader(io.StringIO(ztf_csv.decode("utf-8-sig")))
    required = {"oid", "mjd", "catflags", "filtercode", "filefracday",
                "field", "ccdid", "qid"}
    if not rows.fieldnames or not required.issubset(rows.fieldnames):
        raise ValueError("Missing ZTF image-index columns")
    groups = defaultdict(list)
    for row in rows:
        if not row["oid"].isdigit() or row["filtercode"] not in ("zg", "zr", "zi"):
            raise ValueError("Invalid OID/band in ZTF image index")
        mjd = float(row["mjd"])
        mjd_to_approximate_julian_year(mjd)
        if int(row["catflags"]) & 32768:
            continue
        groups[(row["oid"], row["filtercode"])].append((mjd, row))
    result = []
    for (oid, band), sequence in sorted(groups.items()):
        sequence.sort(key=lambda a: a[0])
        if not sequence:
            continue
        indexes = [len(sequence) // 2, len(sequence) // 5,
                   len(sequence) * 4 // 5][:max_science_per_curve]
        chosen = []
        seen = set()
        for index in indexes:
            mjd, row = sequence[index]
            stamp = row["filefracday"]
            if stamp in seen:
                continue
            seen.add(stamp)
            jyear = mjd_to_approximate_julian_year(mjd)
            ra, dec = propagate_gaia_position(
                target_ra_deg, target_dec_deg, target_pmra, target_pmdec, jyear)
            chosen.append({
                "kind": "science",
                "ztf_oid": oid, "band": band,
                "mjd": round(mjd, 6),
                "url": ztf_science_cutout_url(
                    row, ra_center=ra, dec_center=dec),
                "expected_ra_deg": ra, "expected_dec_deg": dec,
            })
        # A coadded reference is not an independent science exposure.
        # Construct separately, with same observation-field metadata.
        if chosen:
            mjd, row = sequence[len(sequence) // 2]
            ra, dec = propagate_gaia_position(
                target_ra_deg, target_dec_deg, target_pmra, target_pmdec,
                mjd_to_approximate_julian_year(mjd))
            chosen.append({
                "kind": "reference_coadd",
                "ztf_oid": oid, "band": band,
                "mjd": None,  # coadd aggregates exposures; not assigned midpoint date
                "url": ztf_reference_cutout_url(
                    row, ra_center=ra, dec_center=dec),
                "expected_ra_deg": ra, "expected_dec_deg": dec,
            })
        result.append({
            "ztf_oid": oid, "band": band,
            "candidates": chosen,
            "photometric_identity_verified": False,
        })
    return result


def inspect_available_image_candidates(candidates: list[dict], *,
                                       timeout: float = 8.0,
                                       max_attempts_per_curve: int = 4,
                                       fetch=fetch_fits_cutout,
                                       inspect=inspect_fits_cutout) -> list[dict]:
    """Stop at first complete image WCS screen, otherwise retain failure ledger."""
    if not 1 <= max_attempts_per_curve <= 4:
        raise ValueError("Attempts must be in [1,4]")
    results = []
    for curve in candidates:
        attempts = []
        completed = None
        for candidate in curve["candidates"][:max_attempts_per_curve]:
            record = {"kind": candidate["kind"]}
            try:
                raw = fetch(candidate["url"], timeout=timeout)
                outcome = inspect(
                    raw, expected_ra_deg=candidate["expected_ra_deg"],
                    expected_dec_deg=candidate["expected_dec_deg"])
                record["status"] = outcome["status"]
                record["diagnostics"] = outcome
                if outcome["status"] == "PIXEL_WCS_PROVISIONAL_SCREEN_COMPLETED":
                    completed = outcome
            except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
                record["status"] = "IMAGE_ACCESS_OR_FITS_VALIDATION_FAILED"
                record["error_type"] = type(exc).__name__
                if isinstance(exc, HTTPError):
                    record["http_status"] = int(exc.code)
            attempts.append(record)
            if completed is not None:
                break
        results.append({
            "ztf_oid": curve["ztf_oid"], "band": curve["band"],
            "attempts": attempts,
            "status": "PIXEL_WCS_PROVISIONAL_SCREEN_COMPLETED" if completed else
                      "NO_USABLE_FITS_PIXEL_SCREEN",
            "pixel_screen": completed,
            "image_psf_deblending_completed": False,
            "gaia_ztf_astrophysical_identity_confirmed": False,
        })
    return results
