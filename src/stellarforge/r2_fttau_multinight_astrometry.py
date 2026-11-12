"""Preregistered additional-night FT Tau original ZTF native-source pilot.

Fixed OIDs and dated image selection precede inspection of new PSF sources.
No photometry, physical counterpart, or proper motion detection is claimed.
"""
from __future__ import annotations

import hashlib
import math
from urllib.error import HTTPError, URLError

from .r2_ft_tau_two_field_fits import (
    FT_GAIA, FT_OIDS, _sanitized_selection, catalogue_candidates,
)
from .r2_fttau_crossfield_instrumental_ensemble import fixed_four_exposure_pairs
from .r2_fttau_gaia_ps1_target_astrometry import original_target_native_candidate
from .r2_ztf_oid_multiplicity import fetch_historic_oid
from .v14_field_review import ztf_science_cutout_url
from .v114_native_psfcat_association import (
    official_psf_product_url, fetch_native_psf_product, parse_psf_fit_catalogue,
)
from .v19_gaia_covariance import (
    fetch_gaia_astrometry, parse_gaia_astrometry, propagate_gaia_5p_formal,
)

MIN_SEPARATION_DAYS = 30.0
MAX_NEW_IMAGES = 8
ERRORS = (HTTPError, URLError, TimeoutError, OSError, ValueError,
          TypeError, OverflowError, ArithmeticError, UnicodeError)


def select_earliest_latest_independent_nights(rows: list[dict],
                                              anchor: dict) -> dict:
    """Select first and last eligible non-anchor UTC night, before image QA.

    Each input row was already filtered by the frozen OID metadata checker.
    A full date is integer MJD (MJD midnight UTC), not rounded time.
    Avoids picking favourable source residuals and duplicate same-night data.
    """
    if anchor is None or not isinstance(anchor, dict):
        raise ValueError("Frozen original exposure anchor required")
    band = anchor["band"]
    oid = anchor["ztf_oid"]
    field, ccd, quadrant = anchor["original_field_ccd_quadrant"]
    excluded_key = anchor["original_filefracday"]
    if not isinstance(excluded_key, str) or len(excluded_key) != 14:
        raise ValueError("Malformed frozen original anchor")
    clean = []
    for row in rows:
        if (row["band"] != band or row["oid"] != oid
            or int(row["field"]) != field
            or int(row["ccdid"]) != ccd or int(row["qid"]) != quadrant):
            raise ValueError("Original OID stratum changed during multi-night selection")
        mjd = float(row["mjd"])
        if not math.isfinite(mjd):
            raise ValueError("Nonfinite original exposure MJD")
        if row["filefracday"] != excluded_key:
            clean.append(row)
    ordered = sorted(clean, key=lambda x: (float(x["mjd"]), x["filefracday"]))
    by_night = {}
    for row in ordered:
        night = math.floor(float(row["mjd"]))
        if night not in by_night:
            by_night[night] = row
    nights = sorted(by_night)
    span = (by_night[nights[-1]]["mjd"]-by_night[nights[0]]["mjd"]
            if len(nights) >= 2 else None)
    enough = span is not None and span >= MIN_SEPARATION_DAYS
    selected = ([by_night[nights[0]], by_night[nights[-1]]] if enough else [])
    return {
        "status": ("TWO_INDEPENDENT_NIGHTS_PRESELECTED"
                   if enough else "UNDERPOWERED_NONANCHOR_INDEPENDENT_NIGHTS"),
        "n_eligible_nonanchor_exposures": len(ordered),
        "n_distinct_nonanchor_utc_nights": len(nights),
        "earliest_latest_candidate_baseline_days":
            round(float(span), 6) if span is not None else None,
        "selected_rows_ephemeral": selected,
        "earliest_latest_not_image_quality_selected": True,
        "original_four_exposure_anchor_excluded": True,
    }


def inspect_preselected_original_epoch(row: dict, gaia: dict,
                                       *, ra_center: float, dec_center: float,
                                       native_fetch=fetch_native_psf_product,
                                       native_parse=parse_psf_fit_catalogue,
                                       gaia_propagate=propagate_gaia_5p_formal,
                                       source_screen=original_target_native_candidate) -> dict:
    """Inspect only the prospectively selected original catalog; never reselect."""
    sel = _sanitized_selection(row)
    out = {
        "selection": sel,
        "status": "ORIGINAL_NATIVE_ZTF_PSF_UNAVAILABLE_OR_INVALID",
        "native_psfcat_sha256": None,
        "native_source_candidate": None,
        "confirmed_physical_gaia_ztf_target": False,
    }
    try:
        prediction = gaia_propagate(gaia, mjd_utc=row["mjd"])
        url = ztf_science_cutout_url(
            row, ra_center=ra_center, dec_center=dec_center, size_arcsec=60)
        product = official_psf_product_url(url, "psfcat.fits")
        original = native_fetch(product, kind="psfcat.fits", timeout=24)
        sha = hashlib.sha256(original).hexdigest()
        parsed = native_parse(original)
        if parsed.get("sha256") != sha:
            raise ValueError("Native original PSFcat SHA invalid")
        out["native_psfcat_sha256"] = sha
        out["n_original_native_psf_catalogue_rows"] = parsed.get(
            "n_native_psf_catalogue_rows")
        out["native_source_candidate"] = source_screen(parsed, prediction)
        out["status"] = "ORIGINAL_ZTF_NATIVE_PSF_SOURCE_SCREEN_COMPLETE"
    except ERRORS as exc:
        out["error_type"] = type(exc).__name__
        if isinstance(exc, HTTPError):
            out["http_status"] = int(exc.code)
    return out


def summarize_original_epoch_pair(early: dict, late: dict,
                                  baseline_days: float) -> dict:
    """Descriptive native-Gaia differences, never a fitted proper motion."""
    valid_status = "PROVISIONAL_GAIA_NEAREST_ZTF_PSF_SOURCE_GEOMETRY_PASS"
    a = early.get("native_source_candidate") or {}
    b = late.get("native_source_candidate") or {}
    both = (early.get("status") == "ORIGINAL_ZTF_NATIVE_PSF_SOURCE_SCREEN_COMPLETE"
            and late.get("status") == "ORIGINAL_ZTF_NATIVE_PSF_SOURCE_SCREEN_COMPLETE"
            and a.get("status") == valid_status and b.get("status") == valid_status)
    return {
        "status": ("TWO_PROVISIONAL_SOURCE_POSITIONS_NOT_PHYSICAL_ID"
                   if both else "UNRESOLVED_EPOCH_SOURCE_QUALITY_OR_AVAILABILITY"),
        "original_ztf_observation_baseline_days": round(float(baseline_days), 6),
        "late_minus_early_native_minus_gaia_east_arcsec": (
            round(b["original_native_minus_propagated_gaia_east_arcsec"] -
                  a["original_native_minus_propagated_gaia_east_arcsec"], 6)
            if both else None),
        "late_minus_early_native_minus_gaia_north_arcsec": (
            round(b["original_native_minus_propagated_gaia_north_arcsec"] -
                  a["original_native_minus_propagated_gaia_north_arcsec"], 6)
            if both else None),
        "independent_wcs_psf_covariance_established": False,
        "independent_astrophysical_proper_motion_detected": False,
        "confirmed_physical_gaia_ztf_target": False,
    }


def run_fttau_multinight_native_astrometry(
        seed: bytes, historic: dict, oid_receipt: dict,
        prior_images: dict, *,
        oid_fetch=fetch_historic_oid,
        gaia_fetch=fetch_gaia_astrometry,
        image_inspector=inspect_preselected_original_epoch) -> dict:
    """Original-data pilot: at most 8 dates, all selected before image access."""
    fixed, frozen = fixed_four_exposure_pairs(
        seed, historic, oid_receipt, prior_images)
    gaia, gaia_hash, gaia_error = None, None, None
    try:
        raw = gaia_fetch((FT_GAIA,), timeout_sec=35)
        gaia_hash = hashlib.sha256(raw).hexdigest()
        gaia = parse_gaia_astrometry(raw, expected_ids=(FT_GAIA,))[FT_GAIA]
    except ERRORS as exc:
        gaia_error = type(exc).__name__

    groups = []
    for band, field, oid, _, _, _ in FT_OIDS:
        anchor = frozen[band][field]["selection"]
        group = {
            "band": band, "field": field, "fixed_ztf_oid": oid,
            "source_status": "ORIGINAL_IRSA_METADATA_UNAVAILABLE",
            "image_selection_status": "NOT_SELECTED",
            "selected_original_exposures": [],
            "original_oid_response_sha256": None,
            "inspection": [],
            "paired_epoch_summary": None,
        }
        try:
            source = oid_fetch(oid, timeout_sec=35)
            candidates = catalogue_candidates(
                source, (band, field, oid, int(field),
                         15 if field == "1605" else 8,
                         3 if field == "1605" else 4))
            group["source_status"] = "ORIGINAL_IRSA_METADATA_VALID"
            group["original_oid_response_sha256"] = candidates["raw_sha256"]
            group["n_original_source_rows"] = candidates["n_original_source_rows"]
            group["n_metadata_eligible_exposures"] = candidates[
                "n_eligible_distinct_science_exposures"]
            group["metadata_rejected_rows"] = candidates[
                "n_rejected_rows_by_predeclared_technical_reason"]
            choice = select_earliest_latest_independent_nights(
                candidates["rows"], anchor)
            group["image_selection_status"] = choice["status"]
            group["n_eligible_nonanchor_exposures"] = choice[
                "n_eligible_nonanchor_exposures"]
            group["n_distinct_nonanchor_utc_nights"] = choice[
                "n_distinct_nonanchor_utc_nights"]
            group["earliest_latest_candidate_baseline_days"] = choice[
                "earliest_latest_candidate_baseline_days"]
            selected = choice["selected_rows_ephemeral"]
            group["selected_original_exposures"] = [
                _sanitized_selection(x) for x in selected]
            if selected and gaia is not None:
                group["inspection"] = [
                    image_inspector(
                        row, gaia, ra_center=fixed["seed_ra_deg"],
                        dec_center=fixed["seed_dec_deg"])
                    for row in selected]
                group["paired_epoch_summary"] = summarize_original_epoch_pair(
                    group["inspection"][0], group["inspection"][1],
                    float(selected[1]["mjd"]-selected[0]["mjd"]))
            elif selected:
                group["image_selection_status"] = (
                    "PRESELECTED_BUT_GAIA_ORIGINAL_ASTROMETRY_UNAVAILABLE")
        except ERRORS as exc:
            group["source_status"] = "ORIGINAL_IRSA_METADATA_INVALID_OR_UNAVAILABLE"
            group["error_type"] = type(exc).__name__
            if isinstance(exc, HTTPError):
                group["http_status"] = int(exc.code)
        groups.append(group)
    inspected = [x for g in groups for x in g["inspection"]]
    return {
        "phase": "TAURUS_R2_FTTAU_PROSPECTIVE_INDEPENDENT_NIGHT_NATIVE_PSF_ASTROMETRY",
        "fixed_gaia_ft_tau_dr3_source_id": FT_GAIA,
        "frozen_nonrepresentative_taurus_seed_size": 24,
        "original_technical_seed_sha256": hashlib.sha256(seed).hexdigest(),
        "frozen_previous_four_exposures_unmodified": True,
        "original_gaia_source_response_sha256": gaia_hash,
        "original_gaia_availability_error": gaia_error,
        "n_original_gaia_source_records_parsed": int(gaia is not None),
        "n_fixed_original_ztf_oids_queried": 4,
        "n_valid_original_oid_metadata_tables": sum(
            x["source_status"] == "ORIGINAL_IRSA_METADATA_VALID" for x in groups),
        "n_new_independent_original_exposures_preselected": sum(
            len(x["selected_original_exposures"]) for x in groups),
        "n_new_native_psf_catalogues_parsed": sum(
            x["status"] == "ORIGINAL_ZTF_NATIVE_PSF_SOURCE_SCREEN_COMPLETE"
            for x in inspected),
        "n_new_provisional_native_gaia_nearest_candidates": sum(
            (x.get("native_source_candidate") or {}).get("status") ==
            "PROVISIONAL_GAIA_NEAREST_ZTF_PSF_SOURCE_GEOMETRY_PASS"
            for x in inspected),
        "n_independent_night_pairs_with_two_provisional_candidates": sum(
            (g["paired_epoch_summary"] or {}).get("status") ==
            "TWO_PROVISIONAL_SOURCE_POSITIONS_NOT_PHYSICAL_ID"
            for g in groups),
        "n_confirmed_physical_gaia_to_ztf_ft_tau_identities": 0,
        "n_new_confirmed_variable_or_companion_stars": 0,
        "n_merged_original_ztf_oid_lightcurves": 0,
        "scientific_R2_complete": False,
        "original_fixed_oid_strata": groups,
        "limitations": [
            "Two new epochs per original field/filter are selected only by earliest/latest original OID metadata and at least 30 days of separation, not by favourable images.",
            "Original native ZTF source positions and Gaia approximate geocentric propagation have no independent exposure-level calibrated WCS or PSF covariance.",
            "PSF source catalogue proximity misses unresolved blends and sources below catalogue detection limits; no original high-resolution image deblending performed.",
            "The original PS1/MAST mean epoch and individual stellar proper motions remain unresolved for a separate physical association test.",
            "Multi-night agreement cannot authenticate physical Gaia/ZTF FT Tau identity or independent proper-motion detection, and no photometric variability is claimed.",
        ],
    }
