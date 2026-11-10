"""v1.20: preregister a same-exposure strict Gaia cohort and make ZTF stamps.

This stage does NOT independently authenticate Gaia-ZTF physical identities,
original DAOPhot PSF training-star membership, PSF/WCS calibration, or
detector covariance. A real run requires original dated archive products.
The training/validation split is fixed by Gaia-only criteria BEFORE any
ZTF catalogue screening or masked image residual is inspected.
"""
from __future__ import annotations

import hashlib
import math
from typing import Any

import numpy as np
from scipy.ndimage import binary_dilation, map_coordinates

from .coordinates import validate_icrs
from .v113_official_masks_psf import (
    BAD_MASK_BITS, MASK_ALIGN_TOLERANCE_PIX, _one_image,
)
from .v114_native_psfcat_association import screen_psf_catalogue_targets
from .v116_masked_original_psf_residuals import MAX_PHASE_DISAGREEMENT_PIX
from .v117_disjoint_gaia_controls import select_disjoint_holdout_controls
from .v119_empirical_psf_noise import RegisteredStar

TRAIN_COUNT = 4
HOLDOUT_COUNT = 3
COHORT_SIZE = TRAIN_COUNT + HOLDOUT_COUNT
STAMP_RADIUS = 11
MIN_BORDER = 17
MAX_CENTROID_PROXY_OFFSET = 0.08


def preregister_strict_cohort(
    gaia_rows: list[dict], *, target_id: str, prior_ids: set[str],
) -> dict:
    """Two-pass extension of unchanged v1.17 strict Gaia-only selection.

    Existing v1.17 selector has a five-source budget. The second pass
    excludes the first five while preserving ALL original Gaia source rows
    for isolation. This retains the strict quality criteria and sky balance.
    """
    excluded = {str(v) for v in prior_ids}
    if target_id not in excluded:
        raise ValueError("The historical target must already be excluded")
    first = select_disjoint_holdout_controls(
        gaia_rows, target_id=target_id,
        excluded_source_ids=excluded, max_controls=5,
    )
    first5 = first["controls"]
    selected = list(first5)
    if len(first5) == 5:
        second = select_disjoint_holdout_controls(
            gaia_rows, target_id=target_id,
            excluded_source_ids=excluded | {s["source_id"] for s in first5},
            max_controls=2,
        )
        selected.extend(second["controls"])
    ids = [x["source_id"] for x in selected]
    if len(ids) != len(set(ids)) or excluded.intersection(ids):
        raise ValueError("Gaia preregistered cohort shares prior/duplicate IDs")
    ready = len(ids) == COHORT_SIZE
    # The IDs remain in temporary in-memory analysis only, never Git artifacts.
    return {
        "status": ("GAIA_ONLY_STRICT_4_TRAIN_3_HOLDOUT_PREREGISTERED"
                   if ready else "INSUFFICIENT_STRICT_GAIA_ONLY_COHORT"),
        "n_gaia_wide_cone_rows": len(gaia_rows),
        "n_preselected_strict_sources": len(ids),
        "n_expected_training_sources": TRAIN_COUNT if ready else 0,
        "n_expected_holdout_sources": HOLDOUT_COUNT if ready else 0,
        "training_source_ids": tuple(ids[:TRAIN_COUNT]) if ready else (),
        "holdout_source_ids": tuple(ids[TRAIN_COUNT:]) if ready else (),
        "selection_fixed_before_native_ztf_catalogue_and_pixels": True,
        "all_gaia_neighbours_in_original_cone_used_for_isolation": True,
        "original_ztf_psf_training_star_membership_verified": False,
        "astrophysical_gaia_ztf_identity_verified": False,
    }


def screen_fixed_cohort_native_catalogue(
    cat: dict, positions: list[dict], cohort: dict,
) -> dict:
    """Apply the original native PSFcat gate without reassigning groups.

    Returned original IDs and native positions are transient; publish only
    aggregate counts. No source rejected in one group can be replaced by a
    source from the other group after seeing a PSF fit.
    """
    if cohort["status"] != "GAIA_ONLY_STRICT_4_TRAIN_3_HOLDOUT_PREREGISTERED":
        raise ValueError("Gaia-only preregistration is not complete")
    ids = tuple(str(x["source_id"]) for x in positions)
    expected = (*cohort["training_source_ids"], *cohort["holdout_source_ids"])
    if len(ids) != COHORT_SIZE or set(ids) != set(expected):
        raise ValueError("Native source positions not from fixed Gaia cohort")
    screened = screen_psf_catalogue_targets(cat, positions)
    by_id = {s["gaia_source_id"]: s for s in screened["screens"]}
    if len(by_id) != COHORT_SIZE:
        raise ValueError("Native source screen not one-to-one")
    status = "PROVISIONAL_CATALOGUE_NEAREST_AND_PROFILE_SCREEN_PASSED"
    train = [by_id[s] for s in cohort["training_source_ids"]]
    hold = [by_id[s] for s in cohort["holdout_source_ids"]]
    return {
        "status": "NATIVE_PSF_CATALOGUE_SOURCE_GATE_CHECKED",
        "train_screens": train,
        "holdout_screens": hold,
        "n_native_training_candidates": sum(s["status"] == status for s in train),
        "n_native_holdout_candidates": sum(s["status"] == status for s in hold),
        "source_group_assignment_unchanged_after_screen": True,
        "native_ztf_survey_psf_training_membership_known": False,
        "source_identity_authenticated": False,
    }


def registered_star_from_masked_original_fits(
    science_raw: bytes, mask_raw: bytes, *, gaia_source_id: str,
    exposure_id: str, native_source_ra: float, native_source_dec: float,
    native_detector_x: float, native_detector_y: float,
) -> tuple[RegisteredStar, dict[str, Any]]:
    """Build an aligned 23x23 stamp from original source and mask cutouts.

    Verifies same-grid science/mask WCS and native catalogue fractional
    detector phase, conservatively flags interpolation around ANY bad pixel,
    and checks a *data-dependent image centering proxy*. Does not verify
    WCS absolute accuracy; detector pixel interpolation introduces covariance.
    """
    if not (str(gaia_source_id).isdigit()
            and isinstance(exposure_id, str) and 8 < len(exposure_id) < 320):
        raise ValueError("Unidentified candidate or original science exposure")
    validate_icrs(float(native_source_ra), float(native_source_dec))
    sci, _, swcs = _one_image(science_raw)
    msk, _, mwcs = _one_image(mask_raw)
    if sci.shape != msk.shape or min(sci.shape) < 46:
        raise ValueError("Science and detector mask shapes disagree")
    if not (swcs.has_celestial and mwcs.has_celestial
            and swcs.pixel_n_dim == 2 and mwcs.pixel_n_dim == 2
            and swcs.world_n_dim == 2 and mwcs.world_n_dim == 2):
        raise ValueError("Original science/mask celestial WCS missing")
    h, w = sci.shape
    errors = []
    for x, y in ((1., 1.), (w / 2, h / 2), (w - 2., h - 2.)):
        ra, dec = swcs.pixel_to_world_values(x, y)
        mx, my = mwcs.world_to_pixel_values(ra, dec)
        errors.append(float(math.hypot(mx - x, my - y)))
    px, py = map(float, swcs.world_to_pixel_values(
        native_source_ra, native_source_dec))
    if not all(math.isfinite(z) for z in (*errors, px, py)):
        raise ValueError("Nonfinite science or mask WCS registration")
    max_error = max(errors)
    if max_error > MASK_ALIGN_TOLERANCE_PIX:
        raise ValueError("Science and mask original WCS are misregistered")
    if not (MIN_BORDER <= px < w - MIN_BORDER
            and MIN_BORDER <= py < h - MIN_BORDER):
        raise ValueError("Original source too near science stamp border")
    nx, ny = float(native_detector_x), float(native_detector_y)
    if not all(math.isfinite(x) for x in (nx, ny)):
        raise ValueError("Original native detector position unavailable")
    fx, fy = px - round(px), py - round(py)
    sx, sy = nx - round(nx), ny - round(ny)
    mismatch = max(
        abs(((fx - sx + .5) % 1) - .5),
        abs(((fy - sy + .5) % 1) - .5),
    )
    if mismatch > MAX_PHASE_DISAGREEMENT_PIX:
        raise ValueError("Original ZTF PSFcat vs science WCS pixel phase mismatch")
    maskf = np.asarray(msk, dtype=np.float64)
    if (not np.isfinite(maskf).all() or np.any(maskf < 0)
            or np.any(maskf > 65535)
            or not np.all(maskf == np.floor(maskf))):
        raise ValueError("Noninteger or invalid official detector pixel masks")
    msk16 = maskf.astype(np.uint16)
    bad = ((msk16 & BAD_MASK_BITS) != 0) | ~np.isfinite(sci)
    # Reject any potential contribution from an invalid source pixel to a
    # bilinear interpolation; conservatively expand bad-pixel footprints.
    dilated_bad = binary_dilation(bad, structure=np.ones((3, 3), bool))
    yy, xx = np.mgrid[-STAMP_RADIUS:STAMP_RADIUS+1,
                      -STAMP_RADIUS:STAMP_RADIUS+1]
    coords = np.vstack(((py + yy).ravel(), (px + xx).ravel()))
    safe = np.where(np.isfinite(sci), np.asarray(sci, dtype=float), 0.)
    stamp = map_coordinates(
        safe, coords, order=1, mode="nearest").reshape(xx.shape)
    flag = map_coordinates(
        dilated_bad.astype(np.float64), coords, order=0,
        mode="nearest").reshape(xx.shape)
    mask_stamp = np.where(flag > .5, BAD_MASK_BITS, 0).astype(np.uint16)

    # This is an empirical local symmetry/centroid quality proxy, NOT an
    # independently calibrated astrometric WCS residual.
    r = np.hypot(xx, yy)
    skyvals = stamp[(r >= 10) & (mask_stamp == 0)]
    if skyvals.size < 40:
        raise ValueError("No usable sky pixels after registered interpolation")
    sky = float(np.median(skyvals))
    core = (r <= 3.5) & (mask_stamp == 0)
    if np.any((r <= 3.5) & (mask_stamp != 0)):
        raise ValueError("Masked/saturated registered stellar core")
    weight = np.where(core, np.maximum(stamp - sky, 0.), 0.)
    total = float(weight.sum())
    if not math.isfinite(total) or total <= 0:
        raise ValueError("Registered source center not measurable")
    cx = float(np.sum(weight * xx) / total)
    cy = float(np.sum(weight * yy) / total)
    if max(abs(cx), abs(cy)) > MAX_CENTROID_PROXY_OFFSET:
        raise ValueError("Registered source centroid proxy exceeds quality gate")
    star = RegisteredStar(
        gaia_source_id=str(gaia_source_id),
        exposure_id=exposure_id, pixels_dn=stamp, mask_bits=mask_stamp,
        registered_offset_xy=(cx, cy),
    )
    return star, {
        "science_fits_sha256": hashlib.sha256(science_raw).hexdigest(),
        "mask_fits_sha256": hashlib.sha256(mask_raw).hexdigest(),
        "max_mask_science_wcs_offset_pixels": round(max_error, 6),
        "native_psfcat_phase_max_difference_pixels": round(mismatch, 6),
        "registered_centroid_proxy_max_abs_offset_pixels":
            round(max(abs(cx), abs(cy)), 6),
        "interpolated_pixels_are_correlated": True,
        "native_source_identity_independently_authenticated": False,
        "original_daophot_training_star_exclusion_verified": False,
    }


def public_v120_summary(*, cohort: dict, frame_summaries: list[dict],
                        widecone_sha256: str, formal_gaia_sha256: str) -> dict:
    """Publish only observed aggregate counts and SHA provenance.

    Never serialize the private Gaia candidate IDs, native catalogue rows,
    original pixel stamps or empirical PSF arrays.
    """
    if len(frame_summaries) > 4 or any(
        set(x) - {
            "field", "band", "mjd", "native_catalogue_sha256",
            "n_native_train", "n_native_holdout", "n_registered_train",
            "n_registered_holdout", "n_mask_or_registration_failures",
            "empirical_psf_status", "n_heldout_profile_reviews",
            "image_access_failures",
        } for x in frame_summaries
    ):
        raise ValueError("Unapproved public original survey payload")
    if any(len(s) != 64 or any(ch not in "0123456789abcdef" for ch in s)
           for s in (widecone_sha256, formal_gaia_sha256)):
        raise ValueError("Invalid source provenance digest")
    completed = sum(
        x.get("empirical_psf_status") ==
        "INTERNAL_DISTINCT_STAR_PSF_HOLDOUT_COMPLETED"
        for x in frame_summaries
    )
    return {
        "schema": "stellarforge-v1.20-real-original-disjoint-star-readiness",
        "status": ("REAL_IMAGE_INTERNAL_STAR_HOLDOUT_SCREEN_NOT_CALIBRATION"
                   if completed else "OBSERVATIONAL_ELIGIBILITY_AUDIT_ONLY"),
        "n_original_exposures_with_empirical_whole_star_holdout_completed": completed,
        "n_preregistered_gaia_only_strict_sources":
            cohort["n_preselected_strict_sources"],
        "n_predeclared_training_sources": cohort["n_expected_training_sources"],
        "n_predeclared_heldout_sources": cohort["n_expected_holdout_sources"],
        "gaia_widecone_sha256": widecone_sha256,
        "formal_gaia_sha256": formal_gaia_sha256,
        "frames": frame_summaries,
        "original_ztf_daophot_psf_training_membership_verified": False,
        "physical_gaia_ztf_identity_confirmed": False,
        "independent_survey_psf_or_wcs_calibration_completed": False,
        "real_ccd_full_covariance_model_calibrated": False,
        "astronomical_discovery_claimed": False,
    }
