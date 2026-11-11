"""Taurus R2: same-exposure Gaia-selected source-disjoint ZTF PSFcat offsets.

The externally catalogued Gaia IDs were selected in earlier v1.17/1.18
science phases, before this pilot's current native ZTF pixel work. They
are NOT proven to have been excluded from the original ZTF DAOPhot
training set; native psfcat, its sky WCS, and image PSF are same-pipeline.

Only original, fixed FT Tau/CIDA 11 four historical g-band exposures.
No claim of independent instrumental calibration, unique physical
Gaia--ZTF source identity, or stellar variability.
"""
from __future__ import annotations

import hashlib
import math
import statistics
from collections import Counter
from urllib.error import HTTPError, URLError

from .r2_original_fits_gates import (
    validate_historic_exposures, fetch_single_exposure_metadata,
    fixed_exposure_metadata,
)
from .v14_field_review import ztf_science_cutout_url
from .v114_native_psfcat_association import (
    official_psf_product_url, fetch_native_psf_product,
    parse_psf_fit_catalogue, screen_psf_catalogue_targets,
)
from .v19_gaia_covariance import (
    fetch_gaia_astrometry, parse_gaia_astrometry, propagate_gaia_5p_formal,
)

# Exact Gaia IDs from previously published v1.17 *strict* Gaia-only
# CIDA 11 source-disjoint selection. Not instrument-training-independent.
CIDA_STRICT_CONTROLS = (
    "3419109222512317056",
    "3419109840987851136",
    "3419157944621312896",
    "3419111451598996992",
)
# Previously published v1.18 *relaxed exploratory* Gaia-only FT Tau
# source-disjoint tier; NEVER mix with the strict CIDA 11 tier.
FT_EXPLORATORY_CONTROL = ("149623298952568064",)
TARGETS = {
    "FT Tau": "149623711269425408",
    "CIDA 11": "3419110734340795648",
}
MAX_FORMAL_SOURCE_IDS = 7
MIN_STRICT_FIELD_CONTROLS = 3
ERRORS = (HTTPError, URLError, TimeoutError, OSError, ValueError, TypeError,
          OverflowError, ArithmeticError)

def registered_controls(field: str) -> tuple[str, ...]:
    if field == "FT Tau":
        return FT_EXPLORATORY_CONTROL
    if field == "CIDA 11":
        return CIDA_STRICT_CONTROLS
    raise ValueError("Field outside the frozen four-exposure study")


def gaia_native_offset_mas(prediction: dict, native: dict,
                           matched_sourceid: int) -> dict:
    """Tangential Gaia-to-original-native-catalogue offsets in mas.

    These offsets include unknown original ZTF WCS/PSF errors, source
    selection, astrometric/color biases, and Gaia non-single-star
    systematics; NOT measurement of independent instrumental WCS error.
    """
    import numpy as np

    rows = native["rows"]
    indices = np.flatnonzero(np.asarray(rows["sourceid"]) == matched_sourceid)
    if len(indices) != 1:
        raise ValueError("Cannot recover a unique original ZTF native source")
    i = int(indices[0])
    gaia_ra = float(prediction["geocentric_parallax_adjusted_ra_deg"])
    gaia_dec = float(prediction["geocentric_parallax_adjusted_dec_deg"])
    ztf_ra = float(rows["ra"][i])
    ztf_dec = float(rows["dec"][i])
    if not all(map(math.isfinite, (gaia_ra, gaia_dec, ztf_ra, ztf_dec))):
        raise ValueError("Invalid Gaia/native ZTF source coordinates")
    delta_ra = ((ztf_ra - gaia_ra + 180) % 360) - 180
    east = delta_ra * math.cos(math.radians(gaia_dec)) * 3_600_000
    north = (ztf_dec - gaia_dec) * 3_600_000
    return {
        "native_minus_gaia_east_mas": round(east, 3),
        "native_minus_gaia_north_mas": round(north, 3),
        "native_offset_angular_proxy_mas": round(math.hypot(east, north), 3),
        "original_zTF_wcs_zeropoint_independently_measured": False,
        "external_gaia_formal_errors_are_not_full_instrument_errors": True,
    }


def summarize_control_offsets(control_rows: list[dict],
                              target_row: dict) -> dict:
    """Permit descriptive medians; only >=3 strict controls warrant
    *provisional* common-field correction of a target accepted in
    original per-exposure native PSF catalogue. No crossmatch proof.
    """
    eligible = [r for r in control_rows
                if r.get("screen_status") ==
                "PROVISIONAL_CATALOGUE_NEAREST_AND_PROFILE_SCREEN_PASSED"
                and r.get("native_minus_gaia_east_mas") is not None
                and r.get("astrometric_quality_warning") is False
                and r.get("source_stratum") == "GAIA_ONLY_STRICT_CIDA_V117"]
    exploratory = [r for r in control_rows
                   if r.get("screen_status") ==
                   "PROVISIONAL_CATALOGUE_NEAREST_AND_PROFILE_SCREEN_PASSED"
                   and r.get("source_stratum") == "GAIA_ONLY_RELAXED_FT_V118"]
    offsets = eligible if eligible else exploratory
    e = [r["native_minus_gaia_east_mas"] for r in offsets]
    n = [r["native_minus_gaia_north_mas"] for r in offsets]
    median_e = statistics.median(e) if e else None
    median_n = statistics.median(n) if n else None
    tier = "STRICT_CIDA" if eligible else ("EXPLORATORY_FT" if exploratory else "NONE")
    field_gate = len(eligible) >= MIN_STRICT_FIELD_CONTROLS
    target_gate = (
        target_row.get("screen_status") ==
        "PROVISIONAL_CATALOGUE_NEAREST_AND_PROFILE_SCREEN_PASSED"
        and target_row.get("astrometric_quality_warning") is False
        and target_row.get("native_minus_gaia_east_mas") is not None)
    # Not an instrument WCS calibration, even if all strict controls pass.
    corrected = None
    if field_gate and target_gate:
        corrected = {
            "relative_native_minus_gaia_east_mas": round(
                target_row["native_minus_gaia_east_mas"] - median_e, 3),
            "relative_native_minus_gaia_north_mas": round(
                target_row["native_minus_gaia_north_mas"] - median_n, 3),
            "science_status": "PROVISIONAL_DIFFERENTIAL_TARGET_TO_GAIA_CONTROLS_ONLY",
            "independent_wcs_calibration": False,
            "physical_source_identity_confirmed": False,
        }
    return {
        "source_control_stratum":tier,
        "n_registered_control_source_ids":len(control_rows),
        "n_strict_gaia_controls_with_acceptable_native_psf_and_gaia_quality":len(eligible),
        "n_exploratory_ft_controls_with_acceptable_native_psf":len(exploratory),
        "median_control_east_offset_mas":(
            round(median_e,3) if median_e is not None else None),
        "median_control_north_offset_mas":(
            round(median_n,3) if median_n is not None else None),
        "median_control_offsets_descriptive_only":True,
        "min_three_strict_controls_gate_passed":field_gate,
        "target_original_native_psf_and_gaia_quality_gate_passed":target_gate,
        "provisional_target_relative_offset":corrected,
        "source_disjoint_from_prior_stellarforge_v18":True,
        "proved_disjoint_from_original_ZTF_DAOPhot_training_stars":False,
        "independent_instrument_WCS_or_PSF_calibration":False,
        "physical_gaia_to_ztf_source_identity_verified":False,
    }


def inspect_control_exposure(frame:dict, formal:dict, *,
                             metadata_fetch=fetch_single_exposure_metadata,
                             native_fetch=fetch_native_psf_product) -> dict:
    field = frame["target"]
    target_id = frame["target_gaia_id"]
    if TARGETS.get(field) != target_id:
        raise ValueError("Historic exposure does not belong to frozen target")
    control_ids = registered_controls(field)
    if len(control_ids) not in (1, 4):
        raise ValueError("Previously frozen Gaia-only control cohort changed")
    mjd = float(frame["mjd"])
    result = {
        "original_target":field,
        "gaia_dr3_target_id":target_id,
        "historical_ztf_oid":str(frame["oid"]),
        "original_science_mjd":round(mjd,6),
        "n_previously_frozen_gaia_only_controls":len(control_ids),
        "per_source_gaia_native_screen":[],
        "status":"NOT_EVALUATED",
        "original_zTF_pixel_images_reused_not_reacquired":True,
        "original_DAOPhot_training_star_disjointness_verified":False,
        "full_physical_gaia_ztf_source_identity_verified":False,
    }
    try:
        raw = metadata_fetch(str(frame["oid"]),mjd)
        exact = fixed_exposure_metadata(raw,oid=str(frame["oid"]),mjd=mjd)
        result["exact_original_oid_mjd_metadata_sha256"] = exact["metadata_sha256"]
        target = formal[target_id]
        ra, dec = float(target["ra"]), float(target["dec"])
        url = ztf_science_cutout_url(
            exact["row"],ra_center=ra,dec_center=dec,size_arcsec=60)
        native_url = official_psf_product_url(url,"psfcat.fits")
        native_bytes = native_fetch(native_url,kind="psfcat.fits",timeout=20)
        native = parse_psf_fit_catalogue(native_bytes)
        result["original_native_psfcat_sha256"] = native["sha256"]
        result["native_psfcat_n_sources"] = native["n_native_psf_catalogue_rows"]
        all_ids = (target_id, *control_ids)
        predictions = {
            sid:propagate_gaia_5p_formal(formal[sid],mjd_utc=mjd)
            for sid in all_ids
        }
        screen = screen_psf_catalogue_targets(native, [
            {
                "source_id":sid,
                "geocentric_parallax_adjusted_ra_deg":
                    predictions[sid]["geocentric_parallax_adjusted_ra_deg"],
                "geocentric_parallax_adjusted_dec_deg":
                    predictions[sid]["geocentric_parallax_adjusted_dec_deg"],
            }
            for sid in all_ids
        ])
        by_id = {s["gaia_source_id"]:s for s in screen["screens"]}
        for sid in all_ids:
            candidate = by_id[sid]
            role = "TARGET" if sid == target_id else "CONTROL"
            stratum = ("GAIA_ONLY_RELAXED_FT_V118" if field == "FT Tau"
                       else "GAIA_ONLY_STRICT_CIDA_V117")
            row = {
                "gaia_dr3_source_id":sid,
                "role":role,
                "source_stratum":("TECHNICAL_TARGET_V18" if role=="TARGET" else stratum),
                "gaia_ruwe":predictions[sid]["gaia_ruwe"],
                "astrometric_quality_warning":predictions[sid]["high_or_missing_ruwe_quality_warning"],
                "screen_status":candidate["status"],
                "native_ztf_sourceid":candidate.get("ztf_native_per_exposure_sourceid"),
                "nearest_native_source_offset_arcsec":candidate.get("nearest_source_separation_arcsec"),
                "native_psf_quality_profile_passed":candidate.get("psf_fit_profile_quality_screen_passed",False),
                "native_source_identity_is_only_provisional":True,
            }
            if candidate["status"]=="PROVISIONAL_CATALOGUE_NEAREST_AND_PROFILE_SCREEN_PASSED":
                row.update(gaia_native_offset_mas(
                    predictions[sid],native,candidate["ztf_native_per_exposure_sourceid"]))
            result["per_source_gaia_native_screen"].append(row)
        target_row = next(x for x in result["per_source_gaia_native_screen"]
                          if x["role"]=="TARGET")
        controls = [x for x in result["per_source_gaia_native_screen"]
                    if x["role"]=="CONTROL"]
        result["control_offset_summary"] = summarize_control_offsets(controls,target_row)
        result["status"]="PROVISIONAL_ORIGINAL_GAIA_NATIVE_CONTROL_COMPARISON_COMPLETED"
    except ERRORS as exc:
        result["status"]="ORIGINAL_GAIA_OR_ZTF_METADATA_PSF_PRODUCT_INCOMPLETE"
        result["error_type"]=type(exc).__name__
        if isinstance(exc,HTTPError):
            result["http_status"]=int(exc.code)
    return result


def run_original_field_controls(seed_bytes:bytes, historical_ledger:dict, *,
                                gaia_fetch=fetch_gaia_astrometry,
                                inspector=inspect_control_exposure)->dict:
    source, frames = validate_historic_exposures(seed_bytes,historical_ledger)
    # Validated above: two immutable targets, four fixed previous epochs.
    all_ids = tuple(sorted(set(TARGETS.values()) |
                           set(FT_EXPLORATORY_CONTROL) |
                           set(CIDA_STRICT_CONTROLS)))
    if len(all_ids)!=MAX_FORMAL_SOURCE_IDS:
        raise ValueError("Unexpected previously registered Gaia controls")
    raw_gaia = gaia_fetch(all_ids,timeout_sec=35)
    formal = parse_gaia_astrometry(raw_gaia,expected_ids=all_ids)
    results = [inspector(f,formal) for f in frames]
    return {
        "phase":"R2_FT_CIDA_PREVIOUSLY_GAIA_SELECTED_DIFFERENTIAL_CONTROL_OFFSETS",
        "original_public_source_material":"Gaia DR3 original 5p solution plus original ZTF dated PSFcat catalogs",
        "n_original_technical_gaia_targets_in_study":len(source),
        "n_old_historic_science_exposures":len(results),
        "n_unique_predeclared_gaia_only_control_ids":len(all_ids)-len(TARGETS),
        "n_strict_cida_gaia_only_controls":len(CIDA_STRICT_CONTROLS),
        "n_relaxed_exploratory_ft_controls":len(FT_EXPLORATORY_CONTROL),
        "n_original_native_catalogue_exposures_evaluated":sum(
            x["status"]=="PROVISIONAL_ORIGINAL_GAIA_NATIVE_CONTROL_COMPARISON_COMPLETED"
            for x in results),
        "n_exposures_with_at_least_three_accepted_strict_controls":sum(
            x.get("control_offset_summary",{}).get(
                "min_three_strict_controls_gate_passed",False)
            for x in results),
        "n_provisional_differential_target_offsets_with_all_gates":sum(
            bool(x.get("control_offset_summary",{}).get(
                "provisional_target_relative_offset")) for x in results),
        "n_new_original_ztf_science_image_pixels_downloaded":0,
        "n_independently_authenticated_physical_gaia_ztf_matches":0,
        "n_confirmed_new_astrophysical_variable_stars":0,
        "n_confirmed_companions":0,
        "original_ztf_pipeline_training_star_membership_verified":False,
        "instrument_wcs_calibration_independent":False,
        "scientific_R2_complete":False,
        "original_gaia_7_source_response_sha256":hashlib.sha256(raw_gaia).hexdigest(),
        "frozen_r1_seed_sha256":hashlib.sha256(seed_bytes).hexdigest(),
        "frames":results,
        "limitations":[
            "Four strict CIDA controls selected previously using Gaia-only; FT Tau sole exploratory control came from relaxed different criteria, not comparable to CIDA strict tier.",
            "Actual original ZTF PSFcat may not include an eligible source corresponding to every Gaia control; missing sources are not astrophysical nondetections.",
            "Some targets/high-RUWE sources may fail quality gates, so an arbitrary field correction must not be fabricated.",
            "Gaia-control selections are source-disjoint from historical StellarForge training, not verified excluded from ZTF's original DAOPhot PSF training.",
            "Native original ZTF PSF source coordinates share the same pipeline astrometry; differential offsets do not calibrate independent WCS error.",
            "Original FITS/mask images were already checked in preceding R2 step; no additional observational epochs or raw source images added here.",
        ]
    }
