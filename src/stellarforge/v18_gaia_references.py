"""Gaia-DR3 *catalogue-backed candidate* controls for real ZTF science FITS.

IMPORTANT: Gaia membership + positional agreement is not independent proof of
a clean star, ZTF crossmatch or empirical PSF. A provisional 2D translation
from >=3 independent sources is NOT an independently calibrated ZTF WCS.
All FITS images and raw Gaia CSV remain in memory; export aggregates only.
"""
from __future__ import annotations

import csv
import hashlib
import io
import math
import statistics
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from urllib.request import Request, urlopen

from .association import propagate_gaia_position, mjd_to_approximate_julian_year
from .coordinates import angular_separation_arcsec, validate_icrs
from .v14_field_review import GAIA_TAP_URL
from .v15_image_pixels import _validate_official_cutout, fetch_fits_cutout
from .v16_psf_repeatability import fit_local_gaussian_proxy, PSF_OK

GAIA_COLUMNS_V18 = (
    "source_id", "ra", "dec", "pmra", "pmdec", "parallax",
    "phot_g_mean_mag", "phot_g_mean_flux_over_error", "ruwe",
    "duplicated_source", "astrometric_params_solved",
    "ra_error", "dec_error", "pmra_error", "pmdec_error",
)
GAIA_ROW_CAP = 500
GAIA_QUERY_RADIUS_ARCSEC = 210.0
MAX_REFERENCES_PER_TARGET = 5


def reference_adql(ra_deg: float, dec_deg: float, *, radius_arcsec: float = 210.0) -> str:
    """Independent, bounded Gaia DR3 query; include faint sources for isolation."""
    validate_icrs(ra_deg, dec_deg)
    if not math.isfinite(radius_arcsec) or not 90 <= radius_arcsec <= 240:
        raise ValueError("Gaia cone radius must be between 90 and 240 arcsec")
    return (
        f"SELECT TOP {GAIA_ROW_CAP} {', '.join(GAIA_COLUMNS_V18)} "
        "FROM gaiadr3.gaia_source "
        "WHERE 1=CONTAINS(POINT('ICRS',ra,dec),"
        f"CIRCLE('ICRS',{ra_deg:.10f},{dec_deg:.10f},"
        f"{radius_arcsec / 3600:.12f}))"
    )


def download_reference_catalog(ra_deg: float, dec_deg: float, *,
                               timeout: float = 30.0, opener=urlopen) -> bytes:
    if not math.isfinite(timeout) or not 1 <= timeout <= 60:
        raise ValueError("Gaia TAP timeout outside bounds")
    adql = reference_adql(ra_deg, dec_deg)
    form = urlencode({
        "REQUEST": "doQuery", "LANG": "ADQL",
        "FORMAT": "csv", "QUERY": adql,
    }).encode("ascii")
    request = Request(
        GAIA_TAP_URL, data=form, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded",
                 "User-Agent": "StellarForge/1.8 Gaia DR3 PSF candidate validation"},
    )
    with opener(request, timeout=timeout) as resp:
        raw = resp.read(1_000_001)
    if not raw or len(raw) > 1_000_000:
        raise ValueError("Gaia catalog response absent or too large")
    return raw


def _nonfinite_to_none(value):
    if value is None or str(value).strip().lower() in ("", "--", "null", "nan"):
        return None
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("Non-finite Gaia number")
    return number


def parse_reference_catalog(raw: bytes) -> list[dict]:
    text = raw.decode("utf-8-sig")
    if text.lstrip().startswith(("<", "{")):
        raise ValueError("Gaia TAP response is not a CSV result")
    lines = [s for s in text.splitlines() if s.strip() and not s.lstrip().startswith("#")]
    reader = csv.DictReader(io.StringIO("\n".join(lines)))
    if not reader.fieldnames or not set(GAIA_COLUMNS_V18).issubset(reader.fieldnames):
        raise ValueError("Gaia DR3 response lacks required source-quality fields")
    result = []
    seen = set()
    for row in reader:
        if None in row:
            raise ValueError("Malformed Gaia CSV field count")
        source_id = row["source_id"].strip()
        if not source_id.isdigit() or source_id in seen:
            raise ValueError("Gaia source ID invalid or repeated")
        seen.add(source_id)
        ra, dec = _nonfinite_to_none(row["ra"]), _nonfinite_to_none(row["dec"])
        if ra is None or dec is None:
            raise ValueError("Gaia source position absent")
        validate_icrs(ra, dec)
        duplicate = row["duplicated_source"].strip().lower()
        if duplicate not in ("true", "false", "0", "1", "t", "f"):
            raise ValueError("Unexpected Gaia duplicated_source representation")
        params = row["astrometric_params_solved"].strip()
        if not params.isdigit():
            raise ValueError("Malformed Gaia astrometric parameter flag")
        result.append({
            "source_id": source_id, "ra": ra, "dec": dec,
            "pmra": _nonfinite_to_none(row["pmra"]),
            "pmdec": _nonfinite_to_none(row["pmdec"]),
            "parallax": _nonfinite_to_none(row["parallax"]),
            "g_mag": _nonfinite_to_none(row["phot_g_mean_mag"]),
            "g_flux_snr": _nonfinite_to_none(row["phot_g_mean_flux_over_error"]),
            "ruwe": _nonfinite_to_none(row["ruwe"]),
            "duplicated_source": duplicate in ("true", "1", "t"),
            "astrometric_params_solved": int(params),
            "ra_error_mas": _nonfinite_to_none(row["ra_error"]),
            "dec_error_mas": _nonfinite_to_none(row["dec_error"]),
            "pmra_error_mas_yr": _nonfinite_to_none(row["pmra_error"]),
            "pmdec_error_mas_yr": _nonfinite_to_none(row["pmdec_error"]),
        })
    return result


def select_gaia_reference_candidates(rows: list[dict], *, target_id: str,
                                     target_ra_deg: float, target_dec_deg: float,
                                     max_references: int = 5) -> dict:
    """Require catalog quality + angular isolation; no proof of stellar purity.

    Isolation uses all returned Gaia sources, not only quality-filtered ones.
    A capped query, missing target, or sparse field must fail closed.
    """
    validate_icrs(target_ra_deg, target_dec_deg)
    if not str(target_id).isdigit() or not 1 <= max_references <= MAX_REFERENCES_PER_TARGET:
        raise ValueError("Invalid Gaia target or reference count")
    if len(rows) >= GAIA_ROW_CAP:
        return {"status": "GAIA_TAP_RESULT_TRUNCATED", "n_gaia_rows": len(rows),
                "candidates": [], "reference_star_psf_calibrated": False}
    target = next((r for r in rows if r["source_id"] == str(target_id)), None)
    if target is None or angular_separation_arcsec(
        target["ra"], target["dec"], target_ra_deg, target_dec_deg) > 1.0:
        return {"status": "TARGET_GAIA_DR3_NOT_VERIFIED_IN_WIDE_CONE",
                "n_gaia_rows": len(rows), "candidates": [],
                "reference_star_psf_calibrated": False}
    kept = []
    quality_counts = {"ruwe_or_astrometry": 0, "brightness": 0,
                      "too_close_to_target": 0, "neighbor_isolation": 0}
    for item in rows:
        if item["source_id"] == str(target_id):
            continue
        sep = angular_separation_arcsec(
            target["ra"], target["dec"], item["ra"], item["dec"])
        if not 40 <= sep <= 165:
            quality_counts["too_close_to_target"] += 1
            continue
        mag = item["g_mag"]
        if mag is None or not 13 <= mag <= 18.5 or (
                item["g_flux_snr"] is None or item["g_flux_snr"] < 50):
            quality_counts["brightness"] += 1
            continue
        if (item["ruwe"] is None or item["ruwe"] >= 1.4
                or item["duplicated_source"]
                or item["astrometric_params_solved"] not in (31, 95)
                or any(item.get(k) is None for k in (
                    "pmra", "pmdec", "ra_error_mas", "dec_error_mas",
                    "pmra_error_mas_yr", "pmdec_error_mas_yr"))
                or max(item["ra_error_mas"], item["dec_error_mas"]) > 3
                or max(item["pmra_error_mas_yr"], item["pmdec_error_mas_yr"]) > 3):
            quality_counts["ruwe_or_astrometry"] += 1
            continue
        # Include even poor-quality Gaia detections as isolation warnings.
        nearest = min(
            (angular_separation_arcsec(item["ra"], item["dec"], other["ra"], other["dec"])
             for other in rows if other["source_id"] != item["source_id"]),
            default=float("inf"))
        if nearest < 10:
            quality_counts["neighbor_isolation"] += 1
            continue
        kept.append({
            "source_id": item["source_id"],
            "ra": item["ra"], "dec": item["dec"],
            "pmra": item["pmra"], "pmdec": item["pmdec"],
            "parallax_mas": item["parallax"],
            "g_mag": item["g_mag"], "ruwe": item["ruwe"],
            "nearest_gaia_neighbor_arcsec": round(nearest, 4),
            "distance_from_target_arcsec": round(sep, 4),
            "catalogue_backed_only": True,
            "independent_ztf_identity_verified": False,
            "source_is_proven_single": False,
        })
    # Prefer bright, positionally nearby catalogue references, avoiding
    # saturated sources and distant field corner extrapolation.
    kept.sort(key=lambda r: (abs(r["g_mag"]-15.5),
                             r["distance_from_target_arcsec"]))
    return {
        "status": ("GAIA_DR3_QUALITY_SCREENED_REFERENCE_CANDIDATES"
                   if kept else "NO_QUALITY_SCREENED_GAIA_REFERENCES"),
        "n_gaia_rows": len(rows),
        "n_candidates_before_budget": len(kept),
        "n_candidates_selected": min(max_references,len(kept)),
        "candidates": kept[:max_references],
        "quality_screen_rejection_counts": quality_counts,
        "reference_star_psf_calibrated": False,
        "no_non_gaia_neighbors_confirmed": False,
    }


def retarget_same_ztf_exposure(science_url: str, ra_deg: float,
                               dec_deg: float, *, size_arcsec: float = 45) -> str:
    """Preserve official ZTF FITS product path and change only cutout center."""
    _validate_official_cutout(science_url)
    validate_icrs(ra_deg, dec_deg)
    if not math.isfinite(size_arcsec) or not 30 <= size_arcsec <= 60:
        raise ValueError("Gaia reference cutout must be 30..60 arcsec")
    url = urlparse(science_url)
    if not url.path.startswith("/ibe/data/ztf/products/sci/"):
        raise ValueError("Only a dated ZTF science exposure can anchor a reference")
    query = parse_qs(url.query)
    if query.get("gzip") not in (None, ["false"]):
        raise ValueError("Unexpected image compression convention")
    params = urlencode({"center": f"{ra_deg:.8f},{dec_deg:.8f}",
                        "size": f"{size_arcsec:g}arcsec", "gzip": "false"})
    out = urlunparse(("https", "irsa.ipac.caltech.edu",
                      url.path, "", params, ""))
    _validate_official_cutout(out)
    return out


def screen_reference_on_exposure(gaia_ref: dict, *, exposure_url: str,
                                 mjd: float, timeout: float = 6.0,
                                 fetch=fetch_fits_cutout,
                                 fit=fit_local_gaussian_proxy) -> dict:
    """Check a candidate Gaia DR3 position in the *same dated ZTF product*.

    This is a candidate positional/shape check, not an independent proof of
    a stellar reference, target crossmatch or source deblending.
    """
    sky_epoch = mjd_to_approximate_julian_year(mjd)
    ra, dec = propagate_gaia_position(
        gaia_ref["ra"], gaia_ref["dec"],
        gaia_ref["pmra"], gaia_ref["pmdec"], sky_epoch)
    url = retarget_same_ztf_exposure(exposure_url, ra, dec)
    record = {
        "gaia_dr3_source_id": gaia_ref["source_id"],
        "g_mag": gaia_ref["g_mag"],
        "ruwe": gaia_ref["ruwe"],
        "nearest_gaia_neighbor_arcsec": gaia_ref["nearest_gaia_neighbor_arcsec"],
        "reference_is_catalogue_backed_not_psf_authenticated": True,
        "astrophysical_match_confirmed": False,
    }
    try:
        raw = fetch(url, timeout=timeout)
        measurement = fit(raw, expected_ra_deg=ra, expected_dec_deg=dec,
                          image_kind="science")
        record["status"] = measurement["status"]
        if measurement["status"] in PSF_OK:
            record.update({
                "fits_sha256": measurement["fits_sha256"],
                "gaussian_proxy_fwhm_x_arcsec": measurement["fitted_fwhm_x_arcsec"],
                "gaussian_proxy_fwhm_y_arcsec": measurement["fitted_fwhm_y_arcsec"],
                "gaussian_proxy_axis_ratio": measurement["fitted_axis_ratio_proxy"],
                "east_wcs_minus_gaia_arcsec":
                    measurement["fitted_centroid_east_minus_Gaia_arcsec"],
                "north_wcs_minus_gaia_arcsec":
                    measurement["fitted_centroid_north_minus_Gaia_arcsec"],
                "centroid_offset_arcsec":
                    measurement["fitted_centroid_distance_from_Gaia_arcsec"],
                "model_outer_residual_noise_proxy":
                    measurement["max_outer_positive_residual_over_noise"],
                "fit_near_bound": measurement["fit_parameter_near_bound"],
            })
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
        record["status"] = "ZTF_REFERENCE_CUTOUT_OR_FIT_FAILED"
        record["error_type"] = type(exc).__name__
        if isinstance(exc, HTTPError):
            record["http_status"] = int(exc.code)
    return record


def estimate_provisional_wcs_translation(refs: list[dict], *,
                                         min_independent: int = 3) -> dict:
    """Compute robust *translation proxy*, never a physical WCS calibration.

    One per distinct Gaia source ID, only reasonable profile/position records,
    and a maximum 1 arcsecond spread around the robust median.
    Excludes the target from the offset sample by construction.
    """
    if min_independent < 3:
        raise ValueError("At least three distinct reference sources required")
    accepted = {}
    for r in refs:
        if (r.get("status") not in PSF_OK
                or r.get("centroid_offset_arcsec", float("inf")) >= 1.5
                or r.get("fit_near_bound", True)
                or not .8 <= r.get("gaussian_proxy_axis_ratio", float("inf")) <= 1.8
                or not 1.1 <= r.get("gaussian_proxy_fwhm_x_arcsec", float("inf")) <= 8
                or not 1.1 <= r.get("gaussian_proxy_fwhm_y_arcsec", float("inf")) <= 8
                or not str(r.get("gaia_dr3_source_id", "")).isdigit()):
            continue
        sid = r["gaia_dr3_source_id"]
        if sid not in accepted:
            accepted[sid] = r
    valid = list(accepted.values())
    if len(valid) < min_independent:
        return {
            "status": "INSUFFICIENT_INDEPENDENT_IMAGE_VALIDATED_GAIA_CANDIDATES",
            "n_reference_candidates_usable": len(valid),
            "independent_wcs_calibration_completed": False,
            "gaia_ztf_target_identity_confirmed": False,
        }
    east = [float(r["east_wcs_minus_gaia_arcsec"]) for r in valid]
    north = [float(r["north_wcs_minus_gaia_arcsec"]) for r in valid]
    med_e = statistics.median(east)
    med_n = statistics.median(north)
    offsets = [math.hypot(a-med_e,b-med_n) for a,b in zip(east,north)]
    if max(offsets) > 1.0:
        return {
            "status": "GAIA_REFERENCE_OFFSETS_DISAGREE_OVER_1_ARCSEC",
            "n_reference_candidates_usable": len(valid),
            "max_reference_offset_from_median_arcsec": round(max(offsets),5),
            "independent_wcs_calibration_completed": False,
            "gaia_ztf_target_identity_confirmed": False,
        }
    return {
        "status": "PROVISIONAL_LOCAL_WCS_TRANSLATION_ONLY",
        "n_reference_candidates_usable": len(valid),
        "median_east_residual_arcsec": round(med_e,5),
        "median_north_residual_arcsec": round(med_n,5),
        "max_reference_residual_from_median_arcsec": round(max(offsets),5),
        "gaia_reference_ids_used": sorted(accepted),
        "independent_wcs_calibration_completed": False,
        "instrumental_psf_calibrated": False,
        "gaia_ztf_target_identity_confirmed": False,
        "full_astrometric_covariance_included": False,
    }


def subtract_candidate_reference_translation(target_fit: dict,
                                             translation: dict) -> dict:
    """Diagnostic target-minus-reference median offset, NOT calibrated astrometry.

    Only computes when both independent reference count and shape/center
    screening succeeded. Gaia full astrometric uncertainties and target/source
    identity are not established. Must not be interpreted as proper motion.
    """
    if (target_fit.get("status") not in PSF_OK
            or translation.get("status") != "PROVISIONAL_LOCAL_WCS_TRANSLATION_ONLY"
            or translation.get("n_reference_candidates_usable", 0) < 3):
        return {
            "status": "REFERENCE_TRANSLATION_OR_TARGET_FIT_INCOMPLETE",
            "independent_astrometry_calibrated": False,
            "target_source_identity_confirmed": False,
        }
    east = (float(target_fit["east_wcs_minus_gaia_arcsec"])
            - float(translation["median_east_residual_arcsec"]))
    north = (float(target_fit["north_wcs_minus_gaia_arcsec"])
             - float(translation["median_north_residual_arcsec"]))
    if not (math.isfinite(east) and math.isfinite(north)):
        raise ValueError("Non-finite reference-minus-target residual")
    return {
        "status": "PROVISIONAL_TARGET_MINUS_GAIA_REFERENCES_ONLY",
        "east_residual_arcsec": round(east, 5),
        "north_residual_arcsec": round(north, 5),
        "radial_residual_arcsec": round(math.hypot(east,north),5),
        "independent_astrometry_calibrated": False,
        "target_source_identity_confirmed": False,
        "full_Gaia_astrometric_covariance_propagated": False,
    }
