"""Six source/epoch-frozen FT Tau original native spatial DAOPhot PSF pilot.

The returned source/pixel QA is NOT an externally calibrated PSF, astrometric
identity, proper motion, lightcurve merger or discovery. Original source, FITS,
DAO coefficients, photometry and fitted instrumental amplitudes stay ephemeral.
"""
from __future__ import annotations

import hashlib
import math
from urllib.error import HTTPError, URLError

from .r2_ft_tau_two_field_fits import FT_GAIA
from .r2_fttau_six_independent_pixel_residuals import six_original_pixel_specs
from .r2_fttau_gaia_ps1_target_astrometry import original_target_native_candidate
from .v14_field_review import ztf_science_cutout_url
from .v114_native_psfcat_association import (
    official_psf_product_url, fetch_native_psf_product,
    parse_psf_fit_catalogue, _sep_arcsec_vectorized,
)
from .v113_official_masks_psf import (
    official_ancillary_url, fetch_ancillary_fits,
)
from .v115_spatial_psf import (
    parse_original_daophot_lookup, compare_reconstruction_to_official_center,
)
from .v116_masked_original_psf_residuals import _masked_fit
from .v15_image_pixels import fetch_fits_cutout
from .v19_gaia_covariance import (
    fetch_gaia_astrometry, parse_gaia_astrometry, propagate_gaia_5p_formal,
)

ERRORS=(HTTPError,URLError,TimeoutError,OSError,ValueError,
        TypeError,OverflowError,ArithmeticError,UnicodeError)
FROZEN_GAUSSIAN_PILOT_RUN=43279744985
EXPECTED_GAIA_SHA="399b5498d8d8a8a646073dfc029895ed64902940896d1789c63833a18074b642"

# The existing native masked-source pipeline returns fitted instrumental
# amplitude, background and background gradients. Persist ONLY these bounded,
# descriptive QA keys; never source photometry or raw image/catalogue values.
ALLOWED_MASKED_PSF_QA_KEYS=(
    "status",
    "local_masked_psf_model_fit_completed",
    "max_science_mask_grid_error_pixels",
    "native_psfcat_vs_wcs_subpixel_phase_max_disagreement_pixels",
    "science_and_mask_wcs_registration_within_0p05_pixel",
    "n_core_bad_mask_pixels",
    "n_core_saturated_pixels",
    "n_core_nonfinite_pixels",
    "n_masked_core_pixels",
    "n_saturated_core_pixels",
    "n_unmasked_fit_pixels",
    "n_unmasked_sky_annulus_pixels",
    "n_clean_sky_pixels",
    "n_same_image_fit_training_pixels",
    "n_same_image_checkerboard_heldout_pixels",
    "fit_masked_fraction",
    "same_image_holdout_residual_rms_over_sky_noise_proxy",
    "same_image_holdout_max_positive_residual_over_sky_noise_proxy",
    "native_vs_wcs_subpixel_x_difference",
    "native_vs_wcs_subpixel_y_difference",
)


def locked_six_original_native_spatial_specs(
    seed:bytes,historic:dict,oid:dict,four:dict,
    epoch:dict,failures:dict,chi:dict,gaussian:dict)->list[dict]:
    """Lock exactly six original image and source products to all prior runs."""
    specs=six_original_pixel_specs(seed,historic,oid,four,epoch,failures,chi)
    if (gaussian.get("original_data_github_action_run_id")!=FROZEN_GAUSSIAN_PILOT_RUN
            or gaussian.get("n_byte_verified_original_native_psfcats")!=6
            or gaussian.get("n_original_science_mask_pairs_downloaded_and_inspected")!=6
            or gaussian.get("n_valid_independent_analytic_gaussian_fits")!=4
            or gaussian.get("n_gaussian_numerical_failures")!=2
            or gaussian.get("three_original_low_chi_native_ztf_candidates_still_rejected") is not True
            or gaussian.get("gaia_ztf_target_physical_identity_confirmed") is not False
            or gaussian.get("scientific_r2_complete") is not False
            or gaussian.get("n_original_ztf_oid_lightcurves_merged")!=0):
        raise ValueError("Frozen PR47 authentic science/mask evidence changed")
    old=gaussian.get("six_immutable_original_data_exposure_derived_summary")
    if not isinstance(old,list) or len(old)!=6:
        raise ValueError("Expected six complete previously frozen original sources")
    for spec,prior in zip(specs,old):
        if (spec["band"]!=prior.get("band")
                or int(spec["field"])!=prior.get("field")
                or spec["oid"]!=prior.get("oid")
                or spec["filefracday"]!=prior.get("fracday")
                or spec["mjd"]!=prior.get("mjd")
                or spec["epoch_role"]!=prior.get("role")
                or spec["original_full_native_psfcat_sha256_expected"]!=prior.get("native_sha")
                or spec["original_target_native_chi_expected"]!=prior.get("chi")
                or len(str(prior.get("science_sha","")))!=64
                or len(str(prior.get("mask_sha","")))!=64):
            raise ValueError("Previously frozen original science/native PSF pairing altered")
        spec["original_science_cutout_sha256_expected"]=prior["science_sha"]
        spec["original_mask_cutout_sha256_expected"]=prior["mask_sha"]
        spec["prior_circular_gaussian_fit_status"]=prior["fit"]
        spec["prior_circular_gaussian_residual_rms_over_mad"]=prior["rms"]
    return specs


def sanitized_spatial_holdout(source:dict)->dict:
    """Exclude original fitted amplitude, sky, source IDs, flux and raw pixels."""
    return {
        **{key:source[key] for key in ALLOWED_MASKED_PSF_QA_KEYS if key in source},
        "native_spatial_psf_is_same_ztf_reduction_pipeline":True,
        "checkerboard_pixels_are_same_source_not_independent_stars":True,
        "physical_gaia_ztf_source_identity_confirmed":False,
        "independent_instrument_noise_psf_covariance_calibrated":False,
    }


def inspect_one_original_native_spatial_image(
        spec:dict,gaia:dict,*,
        native_fetch=fetch_native_psf_product,
        native_parse=parse_psf_fit_catalogue,
        science_fetch=fetch_fits_cutout,
        mask_fetch=fetch_ancillary_fits,
        spatial_parse=parse_original_daophot_lookup,
        center_compare=compare_reconstruction_to_official_center,
        original_pixel_fit=_masked_fit,
        propagate=propagate_gaia_5p_formal)->dict:
    """One fixed real source: exact old PSFcat/science/mask SHAs, new DAO PSF.

    Any original provenance mismatch is a HARD failure, not a replacement.
    A missing archive resource is an explicit instrument availability state.
    """
    result={
        "band":spec["band"],"field":spec["field"],
        "fixed_original_oid":spec["oid"],
        "original_mjd":spec["mjd"],
        "original_filefracday":spec["filefracday"],
        "epoch_role":spec["epoch_role"],
        "original_native_source_chi":spec["original_target_native_chi_expected"],
        "original_native_source_snr":spec["original_target_native_snr_expected"],
        "original_native_source_quality_passed_unchanged":
            spec["original_target_native_profile_pass_expected"],
        "previous_analytic_gaussian_fit_status":
            spec["prior_circular_gaussian_fit_status"],
        "previous_analytic_gaussian_rms_over_sky_mad":
            spec["prior_circular_gaussian_residual_rms_over_mad"],
        "prior_original_native_psfcat_sha256":
            spec["original_full_native_psfcat_sha256_expected"],
        "prior_original_science_cutout_sha256":
            spec["original_science_cutout_sha256_expected"],
        "prior_original_mask_cutout_sha256":
            spec["original_mask_cutout_sha256_expected"],
        "original_native_psfcat_sha256_verified":False,
        "original_science_mask_pair_sha256_verified":False,
        "spatial_dao_psf_status":"NOT_CHECKED",
        "original_field_center_stamp_status":"NOT_CHECKED",
        "spatial_model_consistency_at_field_center":None,
        "source_spatial_psf_same_image_holdout_diagnostics":None,
        "physical_gaia_ztf_counterpart_confirmed":False,
        "old_native_chi_screen_relaxed":False,
        "original_ztf_oid_curves_merged":False,
    }
    try:
        pred=propagate(gaia,mjd_utc=spec["mjd"])
        gra=float(pred["geocentric_parallax_adjusted_ra_deg"])
        gdec=float(pred["geocentric_parallax_adjusted_dec_deg"])
        sci=ztf_science_cutout_url({
            "filefracday":spec["filefracday"],
            "field":str(spec["field"]),
            "ccdid":str(spec["ccdid"]),
            "qid":str(spec["qid"]),
            "filtercode":"z"+spec["band"]},
            ra_center=gra,dec_center=gdec,size_arcsec=60)
    except ERRORS as exc:
        result["spatial_dao_psf_status"]="GAIA_OR_EXPOSURE_GEOMETRY_INVALID"
        result["gaia_geometry_error_type"]=type(exc).__name__
        return result

    try:
        url=official_psf_product_url(sci,"psfcat.fits")
        original=native_fetch(url,kind="psfcat.fits",timeout=24)
    except ERRORS as exc:
        result["spatial_dao_psf_status"]="PRIOR_NATIVE_PSF_CATALOGUE_ARCHIVE_UNAVAILABLE"
        result["native_psf_catalogue_access_error_type"]=type(exc).__name__
        return result
    sha=hashlib.sha256(original).hexdigest()
    if sha!=spec["original_full_native_psfcat_sha256_expected"]:
        raise ValueError("HARD_FAIL_PREVIOUS_ORIGINAL_FULL_ZTF_PSF_CATALOGUE_SHA_CHANGED")
    cat=native_parse(original)
    if cat.get("sha256")!=sha:
        raise ValueError("HARD_FAIL_PSF_CATALOGUE_PARSE_HASH_MISMATCH")
    candidate=original_target_native_candidate(cat,pred)
    passed=(candidate["status"]==
            "PROVISIONAL_GAIA_NEAREST_ZTF_PSF_SOURCE_GEOMETRY_PASS")
    if passed is not spec["original_target_native_profile_pass_expected"]:
        raise ValueError("HARD_FAIL_ORIGINAL_SOURCE_QUALITY_SCREEN_CHANGED")
    import numpy as np
    rows=cat["rows"]
    separations=_sep_arcsec_vectorized(rows["ra"],rows["dec"],gra,gdec)
    idx=int(np.argmin(separations))
    chi=float(rows["chi"][idx])
    snr=float(rows["snr"][idx])
    if (not math.isfinite(chi) or not math.isfinite(snr)
            or abs(chi-spec["original_target_native_chi_expected"])>.001
            or abs(snr-spec["original_target_native_snr_expected"])>.01):
        raise ValueError("HARD_FAIL_NEAREST_SOURCE_ORIGINAL_PSF_CHI_SNR_CHANGED")
    native_x=float(rows["xpos"][idx]);native_y=float(rows["ypos"][idx])
    native_ra=float(rows["ra"][idx]);native_dec=float(rows["dec"][idx])
    result["original_native_psfcat_sha256_verified"]=True
    try:
        science=science_fetch(sci,timeout=30)
        mask_url=official_ancillary_url(sci,"mskimg.fits")
        mask=mask_fetch(mask_url,kind="mskimg.fits",timeout=22)
    except ERRORS as exc:
        result["spatial_dao_psf_status"]="ORIGINAL_SCIENCE_MASK_ARCHIVE_UNAVAILABLE"
        result["original_science_mask_access_error_type"]=type(exc).__name__
        return result
    science_sha=hashlib.sha256(science).hexdigest()
    mask_sha=hashlib.sha256(mask).hexdigest()
    if (science_sha!=spec["original_science_cutout_sha256_expected"]
            or mask_sha!=spec["original_mask_cutout_sha256_expected"]):
        raise ValueError("HARD_FAIL_PREVIOUS_ORIGINAL_SCIENCE_MASK_FITS_BYTES_CHANGED")
    result["original_science_mask_pair_sha256_verified"]=True

    # Native per-exposure spatial DAOPhot model, not a newly fitted Gaussian.
    try:
        dao_url=official_psf_product_url(sci,"sciimgdao.psf")
        dao_raw=native_fetch(dao_url,kind="sciimgdao.psf",timeout=24)
        spatial=spatial_parse(dao_raw)
        if spatial.get("source_sha256")!=hashlib.sha256(dao_raw).hexdigest():
            raise ValueError("Original spatial DAO model SHA mismatch")
        result["original_spatial_dao_psf_sha256"]=spatial["source_sha256"]
        result["original_spatial_dao_n_lookup_tables"]=spatial["n_lookup_tables"]
        result["spatial_dao_psf_status"]="ORIGINAL_NATIVE_SPATIAL_DAO_PSF_PARSED"
    except ERRORS as exc:
        result["spatial_dao_psf_status"]="NATIVE_SPATIAL_PSF_ARCHIVE_UNAVAILABLE_OR_UNSUPPORTED"
        result["spatial_dao_access_or_parse_error_type"]=type(exc).__name__
        if isinstance(exc,HTTPError):
            result["spatial_dao_http_status"]=int(exc.code)
        return result

    # Original quadrant field-center PSF stamp only; not source-specific.
    try:
        center_url=official_ancillary_url(sci,"sciimgdaopsfcent.fits")
        center_raw=mask_fetch(center_url,kind="sciimgdaopsfcent.fits",timeout=22)
        result["original_native_field_center_stamp_sha256"]=hashlib.sha256(
            center_raw).hexdigest()
        review=center_compare(spatial,center_raw)
        result["original_field_center_stamp_status"]="ORIGINAL_ZTF_CENTER_STAMP_ANALYZED"
        result["spatial_model_consistency_at_field_center"]={
            k:review[k] for k in (
                "status","model_vs_official_center_cosine_similarity",
                "model_vs_official_center_normalized_l1",
                "n_native_center_stamp_pixels",
                "local_spatial_psf_calibrated")
            if k in review}
    except ERRORS as exc:
        result["original_field_center_stamp_status"]="ORIGINAL_CENTER_PSF_UNAVAILABLE_OR_INVALID"
        result["original_center_psf_error_type"]=type(exc).__name__
        if isinstance(exc,HTTPError):
            result["original_center_psf_http_status"]=int(exc.code)

    # This same-ZTF-reduction heldout pixel fit may fail; never override chi.
    try:
        qa=original_pixel_fit(
            science,mask,spatial,
            original_psfcat_ra=native_ra,
            original_psfcat_dec=native_dec,
            native_psfcat_x=native_x,
            native_psfcat_y=native_y)
        result["source_spatial_psf_same_image_holdout_diagnostics"]=sanitized_spatial_holdout(qa)
    except ERRORS as exc:
        result["source_spatial_psf_same_image_holdout_diagnostics"]={
            "status":"ORIGINAL_SOURCE_PSF_HOLDOUT_UNSUPPORTED_OR_FAILED",
            "error_type":type(exc).__name__,
            "physical_gaia_ztf_source_identity_confirmed":False,
        }
    return result


def run_six_original_native_spatial_psf(
    seed:bytes,historic:dict,oid:dict,four:dict,
    epoch:dict,failures:dict,chi:dict,gaussian:dict,*,
    gaia_fetch=fetch_gaia_astrometry,
    image_inspector=inspect_one_original_native_spatial_image)->dict:
    """Six precommitted exact original-source model diagnostics, no discovery."""
    specs=locked_six_original_native_spatial_specs(
        seed,historic,oid,four,epoch,failures,chi,gaussian)
    gaia_raw=gaia_fetch((FT_GAIA,),timeout_sec=35)
    gaia_sha=hashlib.sha256(gaia_raw).hexdigest()
    if gaia_sha!=EXPECTED_GAIA_SHA:
        raise ValueError("HARD_FAIL_ORIGINAL_GAIA_ASTROMETRY_RESPONSE_CHANGED")
    gaia=parse_gaia_astrometry(gaia_raw,expected_ids=(FT_GAIA,))[FT_GAIA]
    results=[image_inspector(s,gaia) for s in specs]
    def qa(row):return row.get("source_spatial_psf_same_image_holdout_diagnostics") or {}
    fitted=[x for x in results if qa(x).get("local_masked_psf_model_fit_completed") is True]
    pass_screen=[x for x in results if qa(x).get("status")==
                 "PROVISIONAL_ORIGINAL_MASKED_PSF_PIXEL_RESIDUAL_SCREEN_PASSED"]
    center_agree=[x for x in results if
                  (x.get("spatial_model_consistency_at_field_center") or {}).get("status")==
                  "OFFICIAL_CENTER_PSF_APPROXIMATE_MODEL_AGREEMENT"]
    return {
        "phase":"TAURUS_R2_FTTAU_SIX_FROZEN_NATIVE_SPATIALLY_VARIABLE_DAOPHOT_PSF_SAME_IMAGE_PIXEL_HOLDOUT",
        "original_exact_gaia_response_sha256":gaia_sha,
        "n_original_frozen_source_exposures":len(specs),
        "n_original_native_full_psfcat_byte_verified":sum(
            x["original_native_psfcat_sha256_verified"] for x in results),
        "n_original_science_mask_pair_byte_verified":sum(
            x["original_science_mask_pair_sha256_verified"] for x in results),
        "n_native_spatial_dao_models_parsed":sum(
            x["spatial_dao_psf_status"]=="ORIGINAL_NATIVE_SPATIAL_DAO_PSF_PARSED"
            for x in results),
        "n_original_center_stamps_analyzed":sum(
            x["original_field_center_stamp_status"]=="ORIGINAL_ZTF_CENTER_STAMP_ANALYZED"
            for x in results),
        "n_field_center_model_checks_provisionally_agree":len(center_agree),
        "n_native_spatial_psf_same_image_numeric_pixel_fits":len(fitted),
        "n_native_spatial_psf_same_image_provisional_residual_screen_passes":
            len(pass_screen),
        "original_six_exact_native_spatial_ztf_source_pixel_results":results,
        "old_native_source_quality_5_of_8_pass_3_of_8_fail_unchanged":True,
        "old_two_night_candidate_quality_pairs_1_of_4_unchanged":True,
        "n_original_ztf_oid_lightcurves_merged":0,
        "n_independently_authenticated_gaia_ztf_fttau_identities":0,
        "n_astrophysical_variables_or_companions_confirmed":0,
        "r2_physical_science_complete":False,
        "limitations":[
            "This reconstructs the ZTF pipeline's own spatially varying DAOPhot PSF, NOT an independent empirical stellar-source validation.",
            "Field-center FITS reconstruction agreement compares two products from the same reduction, not independently measured source-specific PSF uncertainty.",
            "Source mask and original WCS are pipeline-generated; exact source CCD pixel phases are validated, not independent Gaia-ZTF physical source identity.",
            "Checkerboard source pixels are not disjoint stars, true detector variance modeling or new epochs.",
            "Previous chi-lower-bound failed sources stay failed; no physical Gaia-ZTF match, no variable star, no companion, no photometric comparison.",
        ],
    }
