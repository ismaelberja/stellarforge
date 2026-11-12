"""Read-only, exact-byte diagnostics of the three preregistered FT Tau R2 PSF failures.

Scientific interpretation: original ZTF source quality and FITS masks ONLY.
No replacement data, physical matches, astrometric significance or variability.
"""
from __future__ import annotations

import hashlib
import math
from urllib.error import HTTPError, URLError

from .r2_ft_tau_two_field_fits import FT_GAIA
from .r2_fttau_gaia_ps1_target_astrometry import (
    original_target_native_candidate,
)
from .v19_gaia_covariance import (
    fetch_gaia_astrometry, parse_gaia_astrometry, propagate_gaia_5p_formal,
)
from .v14_field_review import ztf_science_cutout_url
from .v114_native_psfcat_association import (
    official_psf_product_url, fetch_native_psf_product,
    parse_psf_fit_catalogue, _sep_arcsec_vectorized,
)
from .v113_official_masks_psf import (
    BAD_MASK_BITS, official_ancillary_url, fetch_ancillary_fits,
    inspect_mask_against_science,
)
from .v15_image_pixels import fetch_fits_cutout, inspect_fits_cutout

ERRORS = (HTTPError, URLError, TimeoutError, OSError, ValueError,
          TypeError, OverflowError, ArithmeticError, UnicodeError)

# Fixed from the original PR44 derived artifact and preregistration;
# these selections are never changed after investigating their quality.
FROZEN_FAILED_LATE = (
    ("g", 1605, "1605115300003377", "20231016393588", 60233.393611,
     "e989ec78cdef805cf8adecfb37d1f0cb1b2b3894a1892d0eb36374ccf4ca505b"),
    ("g", 609, "609108400001155", "20250930441343", 60948.441412,
     "785a472396fa369080e84589bc282122e7f2f44d37059fb52efe769c8cae2ca8"),
    ("r", 609, "609208400001969", "20250917414479", 60935.414502,
     "f1127a1eaf84a507b910952f5e1d35f43a55e4be0c6f9a09b272507dd8f7f043"),
)


def frozen_bad_late_exposures(ledger: dict) -> list[dict]:
    """Check frozen upstream evidence; no post-hoc source/date selection."""
    if (ledger.get("run_id") != 43270659201
            or ledger.get("artifact_id") != 13968001848
            or ledger.get("n_original_ztf_catalogues_new") != 8
            or ledger.get("n_provisional_quality_passed") != 5
            or ledger.get("n_two_night_pairs_quality_passed") != 1
            or ledger.get("n_confirmed_physical_matches") != 0
            or ledger.get("n_merged_lightcurves") != 0
            or ledger.get("scientific_r2_complete") is not False):
        raise ValueError("Previous real original multi-night study changed")
    groups = ledger.get("source_groups", [])
    if len(groups) != 4:
        raise ValueError("Missing fixed four original source groups")
    by_key = {(g["band"], int(g["field"])): g for g in groups}
    if len(by_key) != 4 or set(by_key) != {
            ("g", 1605), ("g", 609), ("r", 1605), ("r", 609)}:
        raise ValueError("Malformed previous original source groups")
    passed = by_key["r", 1605]
    if passed.get("native_psf_pass") != [True, True]:
        raise ValueError("Previous accepted r/1605 study must remain unmodified")
    selected = []
    for band, field, oid, filefracday, mjd, sha in FROZEN_FAILED_LATE:
        prior = by_key[band, field]
        if (prior["oid"] != oid
                or prior.get("native_psf_pass") != [True, False]
                or prior.get("mjds", [None, None])[1] != mjd
                or prior.get("sha", [None, None])[1] != sha
                or not len(filefracday) == 14):
            raise ValueError("Frozen bad-source identity/date/native hash changed")
        ccd, qid = (15, 3) if field == 1605 else (8, 4)
        selected.append({
            "band": band, "field": field, "oid": oid,
            "filefracday": filefracday, "mjd": mjd,
            "ccdid": ccd, "qid": qid,
            "native_psfcat_original_expected_sha256": sha,
        })
    return selected


def original_nearest_native_fit_failure(native: dict, prediction: dict) -> dict:
    """Derive source-level *diagnostic* flags from the frozen nearest source.

    Identical frozen numerical cuts to PR43/44; no raw original source row,
    flux, sigflux, magnitude, source ID or other-neighbour positions saved.
    """
    import numpy as np
    if native.get("status") != "ORIGINAL_ZTF_PSF_CATALOGUE_PARSED_UNVERIFIED":
        raise ValueError("Original FITS native PSFcat required")
    rows = native["rows"]
    s = _sep_arcsec_vectorized(
        rows["ra"], rows["dec"],
        prediction["geocentric_parallax_adjusted_ra_deg"],
        prediction["geocentric_parallax_adjusted_dec_deg"])
    if len(s) == 0 or not np.isfinite(s).all():
        raise ValueError("Original native position set empty/nonfinite")
    nearest = int(np.argmin(s))
    snr = float(rows["snr"][nearest])
    chi = float(rows["chi"][nearest])
    sharp = float(rows["sharp"][nearest])
    flux = float(rows["flux"][nearest])
    sigflux = float(rows["sigflux"][nearest])
    native_flags = int(rows["flags"][nearest])
    checks = {
        "snr_at_least_5": math.isfinite(snr) and snr >= 5,
        "flux_positive": math.isfinite(flux) and flux > 0,
        "sigflux_positive": math.isfinite(sigflux) and sigflux > 0,
        "chi_between_0p5_and_1p5": math.isfinite(chi) and .5 <= chi <= 1.5,
        "sharp_between_minus0p5_and_plus0p5":
            math.isfinite(sharp) and -.5 <= sharp <= .5,
        "native_flags_nonnegative": native_flags >= 0,
        "native_bad_6141_mask_bits_clear":
            native_flags >= 0 and (native_flags & BAD_MASK_BITS) == 0,
    }
    failures = sorted(k for k, ok in checks.items() if not ok)
    former = original_target_native_candidate(native, prediction)
    if (former["status"] != "TARGET_PSF_SOURCE_AMBIGUOUS_OR_QUALITY_REVIEW"
            or not former["unique_within_fixed_0p6arcsec_second_beyond_1arcsec"]
            or not failures
            or former["selected_nearest_original_native_PSF_quality_pass"]):
        raise ValueError("Previously frozen quality-failed source classification changed")
    return {
        "status": "ORIGINAL_NEAREST_PSF_FIT_QUALITY_FAILURE_EXPLAINED",
        "original_nearest_source_separation_arcsec":
            former["nearest_original_native_source_to_predicted_Gaia_arcsec"],
        "original_second_nearest_separation_arcsec":
            former["second_nearest_original_native_source_arcsec"],
        "n_original_catalogued_sources_within_2arcsec":
            former["n_original_native_psf_sources_within_2arcsec"],
        "original_geometry_pass_unchanged": True,
        "original_profile_pass_unchanged": False,
        "source_level_frozen_quality_gates": {k: bool(v) for k, v in checks.items()},
        "failed_source_level_quality_reasons": failures,
        # These are derived selection diagnostics, not original flux/magnitude
        # source tables or astrophysically calibrated fit uncertainties.
        "nearest_source_snr_diagnostic": round(snr, 4) if math.isfinite(snr) else None,
        "nearest_source_psf_chi_diagnostic": round(chi, 4) if math.isfinite(chi) else None,
        "nearest_source_psf_sharp_diagnostic": round(sharp, 4) if math.isfinite(sharp) else None,
        "nearest_source_native_flag_word": native_flags,
        "nearest_source_disqualifying_flag_bits": (
            native_flags & BAD_MASK_BITS if native_flags >= 0 else None),
        "no_source_physical_identity_or_variability_claim": True,
    }


def inspect_one_frozen_failure(spec: dict, gaia: dict, *,
                               native_fetch=fetch_native_psf_product,
                               native_parse=parse_psf_fit_catalogue,
                               science_fetch=fetch_fits_cutout,
                               mask_fetch=fetch_ancillary_fits,
                               predictor=propagate_gaia_5p_formal,
                               image_mask_check=inspect_mask_against_science,
                               image_pixel_check=inspect_fits_cutout) -> dict:
    """Native full-source byte-locked QC, then independent science/mask."""
    out = {
        "band": spec["band"], "field": spec["field"],
        "fixed_original_oid": spec["oid"],
        "fixed_original_filefracday": spec["filefracday"],
        "fixed_original_mjd": spec["mjd"],
        "original_native_psfcat_sha256_expected":
            spec["native_psfcat_original_expected_sha256"],
        "original_native_psf_catalogue_sha_matched": False,
        "native_diagnosis_status": "UNAVAILABLE_OR_INVALID",
        "native_fit_diagnostics": None,
        "image_mask_diagnosis_status": "UNAVAILABLE_OR_INVALID",
        "image_mask_derived_diagnostics": None,
        "scientific_physical_gaia_ztf_source_confirmed": False,
        "original_bad_native_source_quality_changed_to_pass": False,
        "original_ztf_oid_lightcurves_merged": False,
    }
    try:
        prediction = predictor(gaia, mjd_utc=spec["mjd"])
        ra = prediction["geocentric_parallax_adjusted_ra_deg"]
        dec = prediction["geocentric_parallax_adjusted_dec_deg"]
        row = {
            "filefracday": spec["filefracday"],
            "field": str(spec["field"]), "filtercode": "z" + spec["band"],
            "ccdid": str(spec["ccdid"]), "qid": str(spec["qid"]),
        }
        science_url = ztf_science_cutout_url(
            row, ra_center=ra, dec_center=dec, size_arcsec=60)
    except ERRORS as exc:
        out["astrometry_or_original_selection_error_type"] = type(exc).__name__
        return out
    try:
        native_url = official_psf_product_url(science_url, "psfcat.fits")
        raw = native_fetch(native_url, kind="psfcat.fits", timeout=24)
        digest = hashlib.sha256(raw).hexdigest()
        if digest != spec["native_psfcat_original_expected_sha256"]:
            raise ValueError("Original native catalogue bytes differ from frozen prior SHA")
        native = native_parse(raw)
        if native.get("sha256") != digest:
            raise ValueError("Malformed/mismatched original native catalogue")
        out["original_native_psf_catalogue_sha_matched"] = True
        out["native_fit_diagnostics"] = original_nearest_native_fit_failure(native, prediction)
        out["native_diagnosis_status"] = "FROZEN_ORIGINAL_BAD_NATIVE_PSF_DIAGNOSED"
    except ERRORS as exc:
        out["native_failure_error_type"] = type(exc).__name__
        if isinstance(exc, HTTPError):
            out["native_failure_http_status"] = int(exc.code)

    # This independent mask audit cannot reclassify/replace a failed native PSF
    # source, even if the science cutout is clean.
    try:
        science_raw = science_fetch(science_url, timeout=30)
        mask_url = official_ancillary_url(science_url, "mskimg.fits")
        mask_raw = mask_fetch(mask_url, kind="mskimg.fits", timeout=22)
        mask = image_mask_check(
            science_raw, mask_raw, expected_ra_deg=ra, expected_dec_deg=dec)
        pixels = image_pixel_check(
            science_raw, expected_ra_deg=ra, expected_dec_deg=dec)
        out["original_science_cutout_sha256"] = hashlib.sha256(science_raw).hexdigest()
        out["original_same_exposure_mask_cutout_sha256"] = hashlib.sha256(mask_raw).hexdigest()
        out["image_mask_diagnosis_status"] = "ORIGINAL_IMAGE_AND_MASK_ANALYSED"
        out["image_mask_derived_diagnostics"] = {
            "original_mask_status": mask.get("status"),
            "original_science_pixel_status": pixels.get("status"),
            "mask_wcs_aligned": bool(mask.get("wcs_checked_and_aligned", False)),
            "n_bad_core_mask_pixels": mask.get("n_core_bad_mask_pixels"),
            "n_saturated_core_mask_pixels": mask.get("n_core_saturated_mask_pixels"),
            "n_nonfinite_core_science_pixels": mask.get("n_core_nonfinite_science_pixels"),
            "core_bad_mask_fraction": mask.get("core_bad_mask_fraction"),
            "annulus_bad_mask_fraction": mask.get("annulus_bad_mask_fraction"),
            "local_central_science_peak_detected":
                pixels.get("central_local_maximum_detected"),
            "local_additional_bright_peaks_within_12arcsec":
                pixels.get("n_additional_local_maxima_within_12_arcsec"),
            "mask_or_local_peak_proves_unblended_star": False,
        }
    except ERRORS as exc:
        out["image_mask_failure_error_type"] = type(exc).__name__
        if isinstance(exc, HTTPError):
            out["image_mask_failure_http_status"] = int(exc.code)
    return out


def run_frozen_fttau_bad_psf_diagnostics(
        ledger: dict, *,
        gaia_fetch=fetch_gaia_astrometry,
        inspector=inspect_one_frozen_failure) -> dict:
    """Only three exact failed late epochs; archive failures aren't nondetections."""
    fixed = frozen_bad_late_exposures(ledger)
    gaia = None
    original_gaia_sha = None
    error = None
    try:
        raw = gaia_fetch((FT_GAIA,), timeout_sec=35)
        original_gaia_sha = hashlib.sha256(raw).hexdigest()
        gaia = parse_gaia_astrometry(raw, expected_ids=(FT_GAIA,))[FT_GAIA]
    except ERRORS as exc:
        error = type(exc).__name__
    results = [inspector(item, gaia) for item in fixed] if gaia is not None else []
    return {
        "phase": "TAURUS_R2_FTTAU_THREE_FROZEN_ORIGINAL_NATIVE_PSF_FAIL_IMAGE_MASK_DIAGNOSIS",
        "frozen_previous_original_run_id": ledger["run_id"],
        "frozen_previous_8_native_original_catalogues": 8,
        "frozen_previous_5_native_candidates_passed": 5,
        "frozen_previous_3_late_candidates_failed": 3,
        "n_fixed_original_failed_native_sources_selected": len(fixed),
        "n_original_gaia_astrometry_records_valid": int(gaia is not None),
        "original_gaia_astrometry_response_sha256": original_gaia_sha,
        "gaia_access_error_class": error,
        "n_original_native_failed_catalogues_sha_reverified": sum(
            x["original_native_psf_catalogue_sha_matched"] for x in results),
        "n_original_native_quality_failure_reasons_diagnosed": sum(
            x["native_diagnosis_status"] == "FROZEN_ORIGINAL_BAD_NATIVE_PSF_DIAGNOSED"
            for x in results),
        "n_independent_original_image_mask_checks_completed": sum(
            x["image_mask_diagnosis_status"] == "ORIGINAL_IMAGE_AND_MASK_ANALYSED"
            for x in results),
        "frozen_failed_original_exposure_diagnostics": results,
        "n_original_ztf_lightcurves_merged": 0,
        "n_confirmed_physical_gaia_ztf_fttau_identifications": 0,
        "n_new_confirmed_variable_or_companion_stars": 0,
        "scientific_r2_identity_and_variability_complete": False,
        "limitations": [
            "This is diagnosis of prior fixed native PSF failures, never a replacement observing-date selection.",
            "Mask WCS/peak checks and PSF catalogue quality do not authenticate a unique physical stellar source.",
            "No exposure-specific calibrated instrumental covariance, high-resolution deblending or PS1 source-specific epoch-motion authentication.",
            "Original FITS sources, pixels, photometry and raw catalogue rows were transient and never archived.",
        ],
    }
