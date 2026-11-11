"""R2 FT Tau: predeclared original g/r same-filter cross-field FITS QA.

The four ZTF ObjectIDs and their two detector areas were fixed in
the earlier genuine original-IRSA source-label experiment. We pick
ONE original single-science exposure for EACH of four ZTF OIDs, by
minimising the same-band cross-field separation in observation MJD.
Selection uses ONLY original time, metadata and a fixed catalog flag
mask; never science-image appearance, flux, apparent variability,
PSF-fit success or agreement with Gaia.

This cannot independently authenticate Gaia--ZTF physical identity.
Different OIDs are never merged, even when image/source positions
are similar. Raw original FITS, masks, PSF catalogues and photometry
exist only in GitHub Actions process memory.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import math
import re
from urllib.error import HTTPError, URLError

from .r2_original_fits_gates import (
    validate_historic_exposures, independent_native_psfcat_neighbours,
)
from .r2_ztf_oid_multiplicity import fetch_historic_oid
from .ztf_photometry import parse_ztf_table
from .v14_field_review import ztf_science_cutout_url
from .v15_image_pixels import fetch_fits_cutout, inspect_fits_cutout
from .v113_official_masks_psf import (
    official_ancillary_url, fetch_ancillary_fits, inspect_mask_against_science,
)
from .v114_native_psfcat_association import (
    official_psf_product_url, fetch_native_psf_product,
    parse_psf_fit_catalogue, screen_psf_catalogue_targets,
)
from .v19_gaia_covariance import (
    fetch_gaia_astrometry, parse_gaia_astrometry, propagate_gaia_5p_formal,
)
from .r2_gaia_heldout_native_offsets import gaia_native_offset_mas

FT_GAIA = "149623711269425408"
MAX_ORIGINAL_PER_OID = 1500
MAX_IMAGE_SELECTIONS = 4
BAD_CATFLAGS_MASK = 32768
NEAR_SIMULTANEOUS_DAYS = 1.0
FT_OIDS = (
    ("g", "1605", "1605115300003377", 1605, 15, 3),
    ("g", "609", "609108400001155", 609, 8, 4),
    ("r", "1605", "1605215300005161", 1605, 15, 3),
    ("r", "609", "609208400001969", 609, 8, 4),
)
NETWORK_FAILURES = (HTTPError, URLError, TimeoutError, OSError, ValueError,
                    TypeError, OverflowError, UnicodeError, ArithmeticError)


def frozen_ft_tau(seed: bytes, historic: dict, prior_oid_receipt: dict) -> dict:
    """Strictly preserve previous source/field assumptions and 24-source R1 seed."""
    records, frames = validate_historic_exposures(seed, historic)
    ft = records.get(FT_GAIA)
    if not ft or ft.get("name") != "FT Tau":
        raise ValueError("Original R1 Gaia FT Tau source not present")
    original = [r for r in frames if r["target"] == "FT Tau"]
    if len(original) != 2 or {x["oid"] for x in original} != {"1605115300003377"}:
        raise ValueError("Original two FT Tau historical FITS anchors changed")
    if prior_oid_receipt.get("live_original_survey_run_id") != 43066226324:
        raise ValueError("This is not the preexisting original OID audit receipt")
    p = prior_oid_receipt.get("ft_tau", {})
    if (p.get("gaia_dr3_source_id") != FT_GAIA
            or p.get("n_ztf_original_survey_oids") != 4
            or set(p.get("g_ztf_oids", [])) != {x[2] for x in FT_OIDS if x[0] == "g"}
            or set(p.get("r_ztf_oids", [])) != {x[2] for x in FT_OIDS if x[0] == "r"}
            or set(p.get("original_survey_fields", [])) != {
                "1605/0xf/0x3", "609/0x8/0x4"
            }):
        raise ValueError("Original FT Tau field/filter/OID provenance changed")
    return {"name": "FT Tau", "gaia_id": FT_GAIA,
            "seed_ra_deg": float(ft["ra"]), "seed_dec_deg": float(ft["dec"]),
            "fixed_oids": FT_OIDS}


def _decode_int(value: object) -> int:
    try:
        return int(str(value).strip(), 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("Invalid original survey CCD or quadrant") from exc


def catalogue_candidates(raw: bytes, spec: tuple) -> dict:
    """Validate a fixed ZTF original-ID response and select eligible metadata.

    No science-image information is used here. Returned 'rows' must never
    be persisted. It contains raw source magnitude/photometry fields.
    """
    band, field_name, oid, field_no, ccd, qid = spec
    if not isinstance(raw, bytes) or not raw or len(raw) > 4_000_000:
        raise ValueError("Missing/oversized authentic original ZTF table")
    rows, fmt = parse_ztf_table(raw)
    if fmt != "csv" or not rows or len(rows) > MAX_ORIGINAL_PER_OID:
        raise ValueError("Direct original OID table unparseable or over source cap")
    candidates: dict[tuple[str, int, int, int, str], dict] = {}
    rejected = Counter()
    for row in rows:
        if str(row.get("oid", "")).strip() != oid:
            raise ValueError("Original requested ObjectID returned another ObjectID")
        if str(row.get("filtercode", "")).strip().lower() != "z" + band:
            raise ValueError("Fixed historical ObjectID returned other-than-frozen filter")
        try:
            if (int(str(row.get("field"))) != field_no
                    or _decode_int(row.get("ccdid")) != ccd
                    or _decode_int(row.get("qid")) != qid):
                raise ValueError("Original ObjectID detector provenance disagrees")
        except (TypeError, ValueError) as exc:
            raise ValueError("Original ObjectID detector provenance invalid") from exc
        fracday = str(row.get("filefracday") or "").strip()
        if not re.fullmatch(r"\d{14}", fracday):
            rejected["bad_original_exposure_key"] += 1
            continue
        try:
            mjd = float(row["mjd"])
            catflags = int(str(row["catflags"]).strip())
        except (TypeError, ValueError, OverflowError):
            rejected["bad_time_or_flags"] += 1
            continue
        if not math.isfinite(mjd) or not 57500 < mjd < 63000:
            rejected["bad_epoch_range"] += 1
            continue
        if catflags < 0 or catflags & BAD_CATFLAGS_MASK:
            rejected["masked_catflags"] += 1
            continue
        key = (fracday, field_no, ccd, qid, band)
        datum = {"oid": oid, "band": band, "native_field": field_name,
                 "mjd": mjd, "filefracday": fracday, "field": str(field_no),
                 "filtercode": "z" + band, "ccdid": str(ccd),
                 "qid": str(qid)}
        if key not in candidates or mjd < candidates[key]["mjd"]:
            candidates[key] = datum
    ordered = sorted(candidates.values(), key=lambda x: (x["mjd"], x["filefracday"]))
    return {
        "source": "ORIGINAL_OFFICIAL_IRSA_EXACT_ZTF_OBJECTID",
        "oid": oid, "band": band, "native_field": field_name,
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "n_original_source_rows": len(rows),
        "n_eligible_distinct_science_exposures": len(ordered),
        "n_rejected_rows_by_predeclared_technical_reason": dict(sorted(rejected.items())),
        "rows": ordered,  # EPHEMERAL; do not write directly into evidence!
    }


def select_two_field_same_band_pair(first: list[dict], second: list[dict]) -> dict:
    """A deterministic least-time-gap pair, not a photometric-quality selection.

    The result is descriptive only; gaps >1 day explicitly prohibit
    claims of quasi-simultaneous same-band source comparisons.
    """
    if not first or not second:
        return {"status": "MISSING_ORIGINAL_EXPOSURE_FOR_ONE_FIELD",
                "first": None, "second": None, "delta_mjd_days": None,
                "within_one_day": False}
    if any(x["band"] != first[0]["band"] for x in first) or any(
            x["band"] != second[0]["band"] for x in second):
        raise ValueError("Mixed survey filters in one fixed-band exposure set")
    if first[0]["band"] != second[0]["band"]:
        raise ValueError("Cannot compare g and r survey original exposures as one band")
    pair = min(
        ((a, b) for a in first for b in second),
        key=lambda ab: (
            abs(ab[0]["mjd"]-ab[1]["mjd"]),
            min(ab[0]["mjd"], ab[1]["mjd"]),
            ab[0]["filefracday"], ab[1]["filefracday"],
        ))
    delta = abs(pair[0]["mjd"]-pair[1]["mjd"])
    return {
        "status": ("SELECTED_WITHIN_ONE_DAY_DIFFERENT_FIELD" if delta <= NEAR_SIMULTANEOUS_DAYS
                   else "SELECTED_BUT_NOT_CONCURRENT_DIFFERENT_FIELD"),
        "first": pair[0], "second": pair[1],
        "delta_mjd_days": round(delta, 6),
        "within_one_day": delta <= NEAR_SIMULTANEOUS_DAYS,
    }


def _sanitized_selection(row: dict | None) -> dict | None:
    if row is None:
        return None
    return {
        "ztf_oid": row["oid"], "band": row["band"],
        "original_field_ccd_quadrant": [
            int(row["field"]), int(row["ccdid"]), int(row["qid"])],
        "original_filefracday": row["filefracday"],
        "original_mjd": round(row["mjd"], 6),
    }


def inspect_selected_original_fits(row: dict, gaia_source: dict, *,
                                   science_fetch=fetch_fits_cutout,
                                   mask_fetch=fetch_ancillary_fits,
                                   native_fetch=fetch_native_psf_product) -> dict:
    """Same-exposure science+mask+native-PSFcat, independent failures explicit."""
    out = {
        "selection": _sanitized_selection(row),
        "native_psf_status": "NOT_CHECKED",
        "science_mask_status": "NOT_CHECKED",
        "original_ztf_source_identity_verified": False,
        "new_source_variability_confirmed": False,
        "source_blend_excluded": False,
        "external_astrometry_calibration_complete": False,
    }
    try:
        mjd = row["mjd"]
        predicted = propagate_gaia_5p_formal(gaia_source, mjd_utc=mjd)
        ra = predicted["geocentric_parallax_adjusted_ra_deg"]
        dec = predicted["geocentric_parallax_adjusted_dec_deg"]
        out["gaia_ruwe"] = predicted["gaia_ruwe"]
        out["gaia_quality_warning"] = predicted["high_or_missing_ruwe_quality_warning"]
        science_url = ztf_science_cutout_url(
            row, ra_center=ra, dec_center=dec, size_arcsec=60)
        out["original_science_product_identifier"] = science_url.split("/")[-1].split("?")[0]
        out["original_cutout_query_sha256"] = hashlib.sha256(science_url.encode()).hexdigest()
    except NETWORK_FAILURES as exc:
        out["selection_or_astrometry_error_type"] = type(exc).__name__
        return out

    try:
        psf_url = official_psf_product_url(science_url, "psfcat.fits")
        native_bytes = native_fetch(psf_url, kind="psfcat.fits", timeout=22)
        native = parse_psf_fit_catalogue(native_bytes)
        nn = independent_native_psfcat_neighbours(native, ra=ra, dec=dec)
        candidate = screen_psf_catalogue_targets(native, [{
            "source_id": FT_GAIA,
            "geocentric_parallax_adjusted_ra_deg": ra,
            "geocentric_parallax_adjusted_dec_deg": dec,
        }])["screens"][0]
        out["native_psf_status"] = candidate["status"]
        out["native_full_catalogue_sha256"] = native["sha256"]
        out["native_source_catalogue_n_rows"] = native["n_native_psf_catalogue_rows"]
        out["native_nearest_gaia_offset_arcsec"] = candidate.get(
            "nearest_source_separation_arcsec")
        out["native_second_source_within_5arcsec_offset"] = candidate.get(
            "second_nearest_within_5arcsec_arcsec")
        out["native_secondary_sources_within_3arcsec"] = nn.get(
            "n_additional_native_psfcat_sources_within_3arcsec")
        out["native_source_quality_passed"] = (
            candidate["status"] ==
            "PROVISIONAL_CATALOGUE_NEAREST_AND_PROFILE_SCREEN_PASSED")
        if candidate.get("ztf_native_per_exposure_sourceid") is not None:
            out["original_native_source_position_offset_mas"] = gaia_native_offset_mas(
                predicted, native, candidate["ztf_native_per_exposure_sourceid"])
    except NETWORK_FAILURES as exc:
        out["native_psf_status"] = "ORIGINAL_NATIVE_PSF_CATALOGUE_UNAVAILABLE_OR_UNPARSABLE"
        out["native_psf_error_type"] = type(exc).__name__
        if isinstance(exc, HTTPError):
            out["native_psf_http_status"] = int(exc.code)

    try:
        science_bytes = science_fetch(science_url, timeout=30)
        mask_url = official_ancillary_url(science_url, "mskimg.fits")
        mask_bytes = mask_fetch(mask_url, kind="mskimg.fits", timeout=22)
        mask = inspect_mask_against_science(
            science_bytes, mask_bytes, expected_ra_deg=ra, expected_dec_deg=dec)
        image = inspect_fits_cutout(
            science_bytes, expected_ra_deg=ra, expected_dec_deg=dec)
        out["science_mask_status"] = mask["status"]
        out["science_sha256"] = hashlib.sha256(science_bytes).hexdigest()
        out["mask_sha256"] = hashlib.sha256(mask_bytes).hexdigest()
        out["science_pixel_status"] = image["status"]
        out["science_central_peak_found"] = image.get(
            "central_local_maximum_detected")
        out["science_central_peak_offset_arcsec"] = image.get(
            "central_peak_offset_arcsec")
        out["science_additional_bright_peaks_within_12arcsec"] = image.get(
            "n_additional_local_maxima_within_12_arcsec")
        out["mask_image_wcs_aligned"] = mask.get("wcs_checked_and_aligned", False)
        out["mask_core_bad_pixels"] = mask.get("n_core_bad_mask_pixels")
        out["mask_core_saturated_pixels"] = mask.get("n_core_saturated_mask_pixels")
        out["mask_annulus_bad_pixel_fraction"] = mask.get(
            "annulus_bad_mask_fraction")
        out["original_image_is_not_a_new_survey_epoch"] = True
    except NETWORK_FAILURES as exc:
        out["science_mask_status"] = "ORIGINAL_SCIENCE_MASK_IMAGE_UNAVAILABLE_OR_UNPARSABLE"
        out["science_mask_error_type"] = type(exc).__name__
        if isinstance(exc, HTTPError):
            out["science_mask_http_status"] = int(exc.code)

    out["all_three_instrument_source_checks_pass"] = bool(
        out.get("native_source_quality_passed", False)
        and out.get("mask_image_wcs_aligned", False)
        and out.get("mask_core_bad_pixels") == 0
        and out.get("mask_core_saturated_pixels") == 0
        and out.get("science_central_peak_found") is True
    )
    # Still no independent physical Gaia--ZTF identity.
    return out


def describe_same_filter_crossfield(first: dict | None, second: dict | None,
                                    selection: dict) -> dict:
    """Descriptive native ZTF-vs-Gaia offsets only, NEVER WCS calibration."""
    result = {
        "time_gap_days": selection["delta_mjd_days"],
        "same_night_within_one_day": selection["within_one_day"],
        "both_original_science_mask_native_products_available": False,
        "instrumental_gates_both_passed": False,
        "native_catalogue_field_to_field_offset_difference_mas": None,
        "differential_astrometry_independently_calibrated": False,
        "crossfield_oid_physical_identity_authenticated": False,
        "crossfield_lightcurves_merged": False,
    }
    if first is None or second is None:
        return result
    a = first.get("original_native_source_position_offset_mas")
    b = second.get("original_native_source_position_offset_mas")
    if a and b:
        de = b["native_minus_gaia_east_mas"] - a["native_minus_gaia_east_mas"]
        dn = b["native_minus_gaia_north_mas"] - a["native_minus_gaia_north_mas"]
        result["native_catalogue_field_to_field_offset_difference_mas"] = {
            "east_mas": round(de, 3), "north_mas": round(dn, 3),
            "angular_proxy_mas": round(math.hypot(de, dn), 3),
            "source": "same-pipeline native ZTF positions vs externally modelled Gaia",
            "is_measurement_of_independent_field_calibration": False,
            "cannot_establish_gaia_ztf_counterpart": True,
        }
    good = all(x.get("science_sha256") and x.get("mask_sha256")
               and x.get("native_full_catalogue_sha256") for x in (first, second))
    result["both_original_science_mask_native_products_available"] = bool(good)
    result["instrumental_gates_both_passed"] = bool(
        good and first.get("all_three_instrument_source_checks_pass")
        and second.get("all_three_instrument_source_checks_pass"))
    # E.g. 0.05 arcsec is not significant without independent WCS covariance.
    return result


def run_ft_two_field_four_original_images(seed: bytes, historic: dict,
                                          prior_oid_receipt: dict, *,
                                          gaia_fetch=fetch_gaia_astrometry,
                                          oid_fetch=fetch_historic_oid,
                                          image_inspector=inspect_selected_original_fits) -> dict:
    fixed = frozen_ft_tau(seed, historic, prior_oid_receipt)
    sha = hashlib.sha256(seed).hexdigest()
    gaia = None
    gaia_sha = None
    try:
        raw_gaia = gaia_fetch((FT_GAIA,), timeout_sec=35)
        gaia = parse_gaia_astrometry(raw_gaia, expected_ids=(FT_GAIA,))[FT_GAIA]
        gaia_sha = hashlib.sha256(raw_gaia).hexdigest()
    except NETWORK_FAILURES:
        pass

    eligible = {}
    metadata = {}
    for spec in fixed["fixed_oids"]:
        band, field_label, oid, _, _, _ = spec
        group_key = (band, field_label)
        try:
            raw = oid_fetch(oid, timeout_sec=35)
            audit = catalogue_candidates(raw, spec)
            eligible[group_key] = audit["rows"]
            metadata[group_key] = {
                "original_oid": oid, "band": band, "native_field": field_label,
                "original_response_status": "ORIGINAL_DIRECT_OID_METADATA_VALID",
                "original_raw_csv_sha256": audit["raw_sha256"],
                "n_original_rows": audit["n_original_source_rows"],
                "n_eligible_distinct_original_science_exposures":
                    audit["n_eligible_distinct_science_exposures"],
                "rejected_original_rows": audit["n_rejected_rows_by_predeclared_technical_reason"],
            }
        except NETWORK_FAILURES as exc:
            eligible[group_key] = []
            metadata[group_key] = {
                "original_oid": oid, "band": band, "native_field": field_label,
                "original_response_status": "DIRECT_ORIGINAL_OID_UNAVAILABLE_OR_INVALID",
                "error_type": type(exc).__name__,
            }
            if isinstance(exc, HTTPError):
                metadata[group_key]["http_status"] = int(exc.code)

    frames = []
    pairs = []
    for band in ("g", "r"):
        choice = select_two_field_same_band_pair(
            eligible[(band, "1605")], eligible[(band, "609")])
        pair_out = {
            "band": band, "selection_status": choice["status"],
            "selected_original_exposures": [
                _sanitized_selection(choice["first"]),
                _sanitized_selection(choice["second"])],
            "selection_mjd_gap_days": choice["delta_mjd_days"],
            "selected_within_1day": choice["within_one_day"],
            "quality_or_brightness_was_not_used_to_select_survey_images": True,
        }
        inspected = []
        for row in (choice["first"], choice["second"]):
            if row is None:
                inspected.append(None)
            elif gaia is None:
                inspected.append({
                    "selection": _sanitized_selection(row),
                    "status": "ORIGINAL_GAIA_FORMAL_POSITION_UNAVAILABLE",
                    "original_ztf_source_identity_verified": False,
                })
            else:
                inspected.append(image_inspector(row, gaia))
                frames.append(inspected[-1])
        pair_out["crossfield_instrument_summary"] = describe_same_filter_crossfield(
            inspected[0], inspected[1], choice)
        pairs.append(pair_out)

    n_good = sum(x.get("all_three_instrument_source_checks_pass", False)
                 for x in frames)
    return {
        "phase": "TAURUS_R2_FTTAU_TWO_ORIGINAL_FIELDS_TWO_BANDS_FITS_MASK_PSF_QA_NOT_PHYSICAL_CROSSMATCH",
        "fixed_original_r1_nonrepresentative_gaia_target_count": 24,
        "selected_physical_target_name": "FT Tau",
        "selected_gaia_dr3_exact_source_id": FT_GAIA,
        "fixed_original_ztf_distinct_oids": 4,
        "n_original_direct_oid_metadata_requests": 4,
        "n_original_direct_oid_csv_tables_valid": sum(
            x["original_response_status"] == "ORIGINAL_DIRECT_OID_METADATA_VALID"
            for x in metadata.values()),
        "n_mjd_closest_same_band_crossfield_pairs_selected": sum(
            x["selection_status"].startswith("SELECTED_") for x in pairs),
        "n_selected_original_single_science_exposures": len(frames),
        "n_selected_original_images_with_all_instrument_checks_passed": n_good,
        "n_original_image_mask_pairs_checked": sum(
            bool(x.get("science_sha256") and x.get("mask_sha256")) for x in frames),
        "n_original_native_psfcats_parsed": sum(
            bool(x.get("native_full_catalogue_sha256")) for x in frames),
        "n_pairs_with_instrumental_gates_both_passed": sum(
            x["crossfield_instrument_summary"]["instrumental_gates_both_passed"]
            for x in pairs),
        "n_independently_verified_ft_gaia_ztf_physical_crossmatches": 0,
        "n_reconciled_or_combined_ztf_lightcurves": 0,
        "n_confirmed_new_astro_variables_or_companions": 0,
        "r2_physical_source_identity_science_complete": False,
        "original_gaia_source_response_sha256": gaia_sha,
        "original_24_source_seed_sha256": sha,
        "source_oid_metadata": [
            metadata[(band, field)] for band, field, *_ in FT_OIDS],
        "crossfield_same_filter_pairs": pairs,
        "original_fits_mask_native_psf_exposure_results": frames,
        "limitations": [
            "One exposure per pre-registered original ZTF OID, selected solely by min inter-field MJD gap; if gap >1d these are not same-night observations.",
            "Nearest survey PSF source, raw science peak and clean mask cannot prove physical Gaia/ZTF identity or exclude fainter/blended sources.",
            "Native ZTF PSF catalogue coordinates and FITS WCS share instrument astrometry; cross-field differences are descriptive with uncalibrated errors.",
            "No direct astrophysical variability or colour result can be calculated by comparing non-simultaneous g/r exposures or multiple unmerged ZTF ObjectIDs.",
            "The four older historical FT Tau/CIDA FITS image controls remain; these are selected original survey exposures, not newly observed telescope nights.",
            "Original Luhman Taurus source membership and independent image deblending still pending.",
        ],
    }
