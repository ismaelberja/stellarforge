"""Bounded, independently modelled original ZTF science-pixel diagnostics for FT Tau.

Exact six frozen native-PSF catalogue exposures, paired original science/mask
cutouts and epoch-propagated Gaia positions. An analytic Gaussian pixel fit is
NOT a native ZTF PSF fit or independent astrophysical source authentication.
"""
from __future__ import annotations

import hashlib
import math
from urllib.error import HTTPError, URLError

from .r2_ft_tau_two_field_fits import FT_GAIA
from .r2_fttau_chi_reference_controls import FROZEN_GROUPS, frozen_inputs
from .r2_fttau_gaia_ps1_target_astrometry import original_target_native_candidate
from .v14_field_review import ztf_science_cutout_url
from .v114_native_psfcat_association import (
    official_psf_product_url, fetch_native_psf_product,
    parse_psf_fit_catalogue,
)
from .v113_official_masks_psf import (
    BAD_MASK_BITS, _one_image, official_ancillary_url, fetch_ancillary_fits,
    inspect_mask_against_science,
)
from .v15_image_pixels import fetch_fits_cutout
from .v19_gaia_covariance import (
    fetch_gaia_astrometry, parse_gaia_astrometry, propagate_gaia_5p_formal,
)

CORE_PIXELS = 4.5
ANNULUS_INNER_PIXELS = 9.0
ANNULUS_OUTER_PIXELS = 15.0
MIN_CORE = 40
MIN_ANNULUS = 75
MAX_CENTRE_OFFSET = 2.0
MIN_GAUSS_SIGMA = .6
MAX_GAUSS_SIGMA = 4.5
MAX_FIT_EVALS = 300
FWHM_FACTOR = 2.354820045
NOISE_MAD_FACTOR = 1.4826
NOISE_FLOOR = 1e-10
ERRORS = (HTTPError, URLError, TimeoutError, OSError, ValueError,
          TypeError, OverflowError, ArithmeticError, UnicodeError)


def six_original_pixel_specs(seed: bytes, historic: dict, oid: dict,
                             frozen_four: dict, epoch: dict, failures: dict,
                             chi_ledger: dict) -> list[dict]:
    """Hard-lock six original frame/MJD/PSF SHAs to older live experiment.

    Earlier date selection was preregistered and verified by an original
    observational run; this function NEVER tries to select a replacement.
    """
    _, _, fixed = frozen_inputs(
        seed, historic, oid, frozen_four, epoch, failures)
    if (chi_ledger.get("original_data_run_id") != 43275404347
            or chi_ledger.get("n_original_byte_sha_verified_ztf_full_psfcats") != 6
            or chi_ledger.get("original_previous_5_of_8_quality_passes_unchanged") is not True
            or chi_ledger.get("original_valid_two_night_pairs_1_of_4_unchanged") is not True
            or chi_ledger.get("prospective_original_target_quality_gate_unchanged") is not True
            or chi_ledger.get("scientific_R2_complete") is not False
            or chi_ledger.get("n_physical_gaia_ztf_identities_confirmed") != 0
            or chi_ledger.get("n_original_ztf_oid_lightcurves_merged") != 0):
        raise ValueError("Frozen six-original-image chi-blind real study changed")
    rows = chi_ledger.get("original_exact_3_ztf_oid_early_late_pairs", [])
    if len(rows) != 3:
        raise ValueError("Six earlier original image source rows missing")
    by = {(x["band"], str(x["field"])): x for x in rows}
    if set(by) != set(FROZEN_GROUPS):
        raise ValueError("Original six-source image group identity changed")
    checked = []
    for f in fixed:
        key = (f["band"], f["field"])
        old = by[key]
        if old.get("oid") != f["oid"] or len(old.get("epochs", [])) != 2:
            raise ValueError("Frozen original ZTF OID grouping changed")
        for index, item in enumerate(old["epochs"]):
            if (item.get("mjd") != (f["early_mjd"] if index == 0 else f["late_mjd"])
                    or item.get("sha") != f["original_psfcat_shas"][index]
                    or not isinstance(item.get("day"), str)
                    or len(item["day"]) != 14 or not item["day"].isdigit()
                    or not math.isfinite(float(item["chi"]))
                    or not math.isfinite(float(item["snr"]))):
                raise ValueError("Original ZTF image date/full PSF SHA/target chi changed")
            passing = .5 <= float(item["chi"]) <= 1.5
            if passing != (index == 0):
                raise ValueError("Prior original native PSF quality classification changed")
            checked.append({
                "band": f["band"], "field": f["field"], "oid": f["oid"],
                "filefracday": item["day"], "mjd": item["mjd"],
                "ccdid": 15 if f["field"] == "1605" else 8,
                "qid": 3 if f["field"] == "1605" else 4,
                "original_full_native_psfcat_sha256_expected": item["sha"],
                "original_target_native_chi_expected": item["chi"],
                "original_target_native_snr_expected": item["snr"],
                "original_target_native_profile_pass_expected": index == 0,
                "epoch_role": "EARLY_FROZEN_CONTROL" if index == 0 else "LATE_FROZEN_CHI_FAILURE",
            })
    if len(checked) != 6:
        raise ValueError("Original six fixed source images incomplete")
    return checked


def independent_masked_gaussian_pixel_fit(science: bytes, mask: bytes, *,
                                          ra: float, dec: float) -> dict:
    """Fixed source core, independent analytic Gaussian and sky-MAD residual.

    Fitted amplitude and raw sky pixel values never leave this routine.
    The residual / annulus MAD is NOT the archive PSF chi or calibrated chi2.
    """
    import numpy as np
    from scipy.optimize import least_squares
    from astropy.wcs.utils import proj_plane_pixel_scales

    original_mask = inspect_mask_against_science(
        science, mask, expected_ra_deg=ra, expected_dec_deg=dec)
    out = {
        "status": "PIXEL_GAUSSIAN_UNRESOLVED",
        "source_mask_status": original_mask.get("status"),
        "source_mask_wcs_aligned": bool(original_mask.get("wcs_checked_and_aligned", False)),
        "n_source_core_bad_mask_pixels": original_mask.get("n_core_bad_mask_pixels"),
        "n_source_core_saturated_mask_pixels": original_mask.get("n_core_saturated_mask_pixels"),
        "n_source_core_nonfinite_pixels": original_mask.get("n_core_nonfinite_science_pixels"),
        "n_source_annulus_bad_mask_pixels": original_mask.get("n_annulus_bad_mask_pixels"),
        "fit_is_not_original_ztf_native_psf": True,
        "residual_is_not_calibrated_reduced_chi_square": True,
        "physical_gaia_ztf_identity_confirmed": False,
        "independent_wcs_psf_covariance_validated": False,
        "companion_or_variability_detected": False,
    }
    if original_mask.get("status") != "MASK_CORE_NO_DISQUALIFYING_BITS_PROVISIONAL_ONLY":
        return {**out, "status": "ORIGINAL_MASK_WCS_OR_CORE_INSUFFICIENT"}
    image, _, wcs = _one_image(science)
    flags, _, _ = _one_image(mask)
    image = np.asarray(image, dtype=np.float64)
    flags = np.asarray(flags, dtype=np.uint16)
    gx, gy = map(float, wcs.world_to_pixel_values(ra, dec))
    scales = np.asarray(proj_plane_pixel_scales(wcs), dtype=np.float64) * 3600.
    if (not np.isfinite([gx, gy]).all()
            or not np.isfinite(scales).all()
            or not np.all((scales > .2) & (scales < 5.))):
        return {**out, "status": "ORIGINAL_CELESTIAL_WCS_OR_PLATE_SCALE_UNUSABLE"}
    scale = float(np.mean(scales))
    yy, xx = np.indices(image.shape, dtype=np.float64)
    radius = np.hypot(xx - gx, yy - gy)
    bad = ((flags & BAD_MASK_BITS) != 0) | ~np.isfinite(image)
    core = (radius <= CORE_PIXELS) & ~bad
    annulus = (radius >= ANNULUS_INNER_PIXELS) & (radius <= ANNULUS_OUTER_PIXELS) & ~bad
    ncore, nann = int(core.sum()), int(annulus.sum())
    out["n_independent_gaussian_core_pixels"] = ncore
    out["n_independent_gaussian_sky_annulus_pixels"] = nann
    if ncore < MIN_CORE or nann < MIN_ANNULUS:
        return {**out, "status": "INSUFFICIENT_ORIGINAL_CORE_OR_ANNULUS_PIXELS"}
    sky_data = image[annulus]
    sky_med = float(np.median(sky_data))
    sky_sigma = float(NOISE_MAD_FACTOR * np.median(np.abs(sky_data - sky_med)))
    if not math.isfinite(sky_sigma) or sky_sigma <= NOISE_FLOOR:
        return {**out, "status": "ORIGINAL_SKY_MAD_NOISE_PROXY_INVALID"}
    near = core & (radius <= 2.5)
    if not np.any(near):
        return {**out, "status": "ORIGINAL_SOURCE_PEAK_INITIALIZER_UNAVAILABLE"}
    peak = np.max(image[near])
    if not math.isfinite(float(peak)) or peak <= sky_med:
        return {**out, "status": "ORIGINAL_TARGET_POSITIVE_PIXEL_PEAK_MISSING"}
    all_xy = np.column_stack((xx[near], yy[near]))
    start_xy = all_xy[int(np.argmax(image[near]))]
    x0, y0 = float(start_xy[0]), float(start_xy[1])
    # Preserve strict interior bounds even for a pixel selected at ~2.5 px.
    x0 = min(max(x0, gx - MAX_CENTRE_OFFSET + 1e-5), gx + MAX_CENTRE_OFFSET - 1e-5)
    y0 = min(max(y0, gy - MAX_CENTRE_OFFSET + 1e-5), gy + MAX_CENTRE_OFFSET - 1e-5)
    cx, cy = xx[core], yy[core]
    values = image[core]
    def normalized_pixel_residual(p):
        amp, mx, my, sigma = p
        model = sky_med + amp * np.exp(-.5 * ((cx-mx)**2+(cy-my)**2) / sigma**2)
        return (values-model)/sky_sigma
    start = np.array([float(peak-sky_med), x0, y0, 1.5])
    try:
        fit = least_squares(
            normalized_pixel_residual, start,
            bounds=([0., gx-MAX_CENTRE_OFFSET, gy-MAX_CENTRE_OFFSET,
                     MIN_GAUSS_SIGMA],
                    [np.inf, gx+MAX_CENTRE_OFFSET, gy+MAX_CENTRE_OFFSET,
                     MAX_GAUSS_SIGMA]),
            loss="soft_l1", f_scale=1., max_nfev=MAX_FIT_EVALS)
    except (ValueError, OverflowError, FloatingPointError):
        return {**out, "status": "BOUNDED_ANALYTIC_GAUSSIAN_OPTIMIZER_FAILED"}
    if not fit.success or not np.isfinite(fit.x).all():
        return {**out, "status": "BOUNDED_ANALYTIC_GAUSSIAN_OPTIMIZER_FAILED"}
    amp, fx, fy, fs = map(float, fit.x)
    at_bound = (amp <= 1e-9
                or fs <= MIN_GAUSS_SIGMA + .02
                or fs >= MAX_GAUSS_SIGMA - .02
                or abs(fx-gx) >= MAX_CENTRE_OFFSET-.05
                or abs(fy-gy) >= MAX_CENTRE_OFFSET-.05)
    residual = normalized_pixel_residual(fit.x)
    if not np.isfinite(residual).all():
        return {**out, "status": "NONFINITE_INDEPENDENT_PIXEL_RESIDUAL"}
    return {
        **out,
        "status": ("BOUNDED_GAUSSIAN_AT_PARAMETER_LIMIT_DESCRIPTIVE_ONLY"
                   if at_bound else "INDEPENDENT_PIXEL_GAUSSIAN_NUMERIC_FIT_COMPLETE"),
        "n_independent_gaussian_core_pixels": ncore,
        "n_independent_gaussian_sky_annulus_pixels": nann,
        "original_science_wcs_plate_scale_arcsec_per_pixel_proxy": round(scale, 5),
        "source_core_rms_residual_over_sky_mad_noise_proxy":
            round(float(np.sqrt(np.mean(residual**2))), 5),
        "source_core_median_absolute_residual_over_sky_mad_noise_proxy":
            round(float(np.median(np.abs(residual))), 5),
        "analytic_circular_gaussian_fwhm_arcsec_proxy":
            round(float(FWHM_FACTOR * fs * scale), 5),
        "analytic_gaussian_centroid_minus_gaia_arcsec_proxy":
            round(float(math.hypot(fx-gx,fy-gy)*scale), 5),
        "fitted_parameters_touch_predeclared_bounds": bool(at_bound),
        "no_independent_source_profile_covariance": True,
    }


def inspect_frozen_original_image(spec: dict, gaia: dict, *,
                                  native_fetch=fetch_native_psf_product,
                                  science_fetch=fetch_fits_cutout,
                                  mask_fetch=fetch_ancillary_fits,
                                  native_parse=parse_psf_fit_catalogue,
                                  gaia_propagate=propagate_gaia_5p_formal,
                                  pixel_inspector=independent_masked_gaussian_pixel_fit,
                                  prior_failed_frame: dict | None = None) -> dict:
    """No date/source replacement; hash-locked full native first, then pixels."""
    out = {
        "band": spec["band"], "field": spec["field"], "fixed_oid": spec["oid"],
        "original_mjd": spec["mjd"], "original_filefracday": spec["filefracday"],
        "epoch_role": spec["epoch_role"],
        "original_native_psfcat_expected_sha256":
            spec["original_full_native_psfcat_sha256_expected"],
        "native_sha256_verified": False,
        "native_original_candidate_quality_pass_unchanged": None,
        "original_science_mask_status": "NOT_CHECKED",
        "independent_original_pixel_fit": None,
        "scientific_physical_source_identity_confirmed": False,
        "previous_native_psf_chi_threshold_relaxed": False,
        "original_ztf_oid_lightcurves_merged": False,
    }
    prediction = gaia_propagate(gaia, mjd_utc=spec["mjd"])
    ra,dec=(prediction["geocentric_parallax_adjusted_ra_deg"],
            prediction["geocentric_parallax_adjusted_dec_deg"])
    row={
        "filefracday":spec["filefracday"],
        "field":str(spec["field"]),"ccdid":str(spec["ccdid"]),"qid":str(spec["qid"]),
        "filtercode":"z"+spec["band"],
    }
    science_url=ztf_science_cutout_url(
        row,ra_center=ra,dec_center=dec,size_arcsec=60)
    native_url=official_psf_product_url(science_url,"psfcat.fits")
    try:
        native_raw=native_fetch(native_url,kind="psfcat.fits",timeout=24)
    except ERRORS as exc:
        out["original_science_mask_status"]="NATIVE_ZTF_PSF_UNAVAILABLE"
        out["native_access_error_type"]=type(exc).__name__
        return out
    sha=hashlib.sha256(native_raw).hexdigest()
    if sha!=spec["original_full_native_psfcat_sha256_expected"]:
        raise ValueError("HARD_FAIL_DIFFERENT_ORIGINAL_FULL_NATIVE_PSF_CATALOGUE_SHA")
    native=native_parse(native_raw)
    if native.get("sha256")!=sha:
        raise ValueError("HARD_FAIL_NATIVE_ORIGINAL_PSF_PARSE_SHA_MISMATCH")
    out["native_sha256_verified"]=True
    target=original_target_native_candidate(native,prediction)
    accept=(target["status"]=="PROVISIONAL_GAIA_NEAREST_ZTF_PSF_SOURCE_GEOMETRY_PASS")
    if accept is not spec["original_target_native_profile_pass_expected"]:
        raise ValueError("HARD_FAIL_FROZEN_ORIGINAL_PSF_TARGET_SCREEN_CHANGED")
    from .v114_native_psfcat_association import _sep_arcsec_vectorized
    import numpy as np
    distances=_sep_arcsec_vectorized(native["rows"]["ra"],native["rows"]["dec"],ra,dec)
    nearest=int(np.argmin(distances))
    chi=float(native["rows"]["chi"][nearest])
    snr=float(native["rows"]["snr"][nearest])
    if (abs(chi-spec["original_target_native_chi_expected"])>1e-3
            or abs(snr-spec["original_target_native_snr_expected"])>.01):
        raise ValueError("HARD_FAIL_ORIGINAL_NATIVE_TARGET_FIT_METRICS_CHANGED")
    out["native_original_candidate_quality_pass_unchanged"]=accept
    out["native_original_nearest_source_chi"]=round(chi,5)
    out["native_original_nearest_source_snr"]=round(snr,4)
    try:
        science=science_fetch(science_url,timeout=30)
        mask_url=official_ancillary_url(science_url,"mskimg.fits")
        mask=mask_fetch(mask_url,kind="mskimg.fits",timeout=22)
    except ERRORS as exc:
        out["original_science_mask_status"]="ORIGINAL_IMAGE_OR_MASK_UNAVAILABLE"
        out["original_image_or_mask_error_type"]=type(exc).__name__
        return out
    science_sha=hashlib.sha256(science).hexdigest()
    mask_sha=hashlib.sha256(mask).hexdigest()
    if prior_failed_frame is not None:
        if (science_sha!=prior_failed_frame["original_science_cutout_sha256"]
                or mask_sha!=prior_failed_frame["original_mask_cutout_sha256"]):
            raise ValueError("HARD_FAIL_PREVIOUS_PR45_ORIGINAL_SCIENCE_MASK_BYTES_CHANGED")
    out["original_science_cutout_sha256"]=science_sha
    out["original_mask_cutout_sha256"]=mask_sha
    try:
        diag=pixel_inspector(science,mask,ra=ra,dec=dec)
    except ERRORS as exc:
        out["original_science_mask_status"]="ORIGINAL_IMAGE_PIXEL_INSPECTION_FAILED"
        out["original_pixel_inspection_error_type"]=type(exc).__name__
        return out
    out["independent_original_pixel_fit"]=diag
    out["original_science_mask_status"]="ORIGINAL_DATED_SCIENCE_MASK_PIXEL_AUDIT_COMPLETED"
    return out


def run_fttau_six_original_independent_pixel_fit(
        seed:bytes,historic:dict,oid:dict,prior_four:dict,
        epoch:dict,failures:dict,chi_ledger:dict, *,
        gaia_fetch=fetch_gaia_astrometry,
        inspector=inspect_frozen_original_image) -> dict:
    """Six originally selected epochs, Gaia original source, no new selection."""
    fixed=six_original_pixel_specs(
        seed,historic,oid,prior_four,epoch,failures,chi_ledger)
    raw=gaia_fetch((FT_GAIA,),timeout_sec=35)
    gaia=parse_gaia_astrometry(raw,expected_ids=(FT_GAIA,))[FT_GAIA]
    previous={(x["band"],str(x["field"])):x
              for x in failures.get("source_checks",[])}
    out=[]
    for spec in fixed:
        old=(previous[spec["band"],spec["field"]]
             if spec["epoch_role"]=="LATE_FROZEN_CHI_FAILURE" else None)
        result=inspector(spec,gaia,prior_failed_frame=old)
        out.append(result)
    groups=[]
    for band,field in FROZEN_GROUPS:
        early=next(x for x in out if (x["band"],x["field"],x["epoch_role"]) ==
                   (band,field,"EARLY_FROZEN_CONTROL"))
        late=next(x for x in out if (x["band"],x["field"],x["epoch_role"]) ==
                  (band,field,"LATE_FROZEN_CHI_FAILURE"))
        a=early.get("independent_original_pixel_fit") or {}
        b=late.get("independent_original_pixel_fit") or {}
        complete=(a.get("status")=="INDEPENDENT_PIXEL_GAUSSIAN_NUMERIC_FIT_COMPLETE"
                  and b.get("status")=="INDEPENDENT_PIXEL_GAUSSIAN_NUMERIC_FIT_COMPLETE")
        first=a.get("source_core_rms_residual_over_sky_mad_noise_proxy")
        second=b.get("source_core_rms_residual_over_sky_mad_noise_proxy")
        groups.append({
            "band":band,"field":field,
            "frozen_early_native_candidate_pass_late_native_candidate_fail":True,
            "paired_independent_pixel_diagnostics_both_numeric":complete,
            "descriptive_late_over_early_gaussian_core_rms_over_sky_mad_ratio":
                round(second/first,5) if (complete and first and second is not None) else None,
            "ratio_is_not_stellar_variability_or_instrument_chi_calibration":True,
        })
    return {
        "phase":"TAURUS_R2_FTTAU_SIX_FROZEN_ORIGINAL_ZTF_SCIENCE_PIXELS_INDEPENDENT_ANALYTIC_GAUSSIAN_RESIDUAL_AUDIT",
        "original_exact_gaia_tap_sha256":hashlib.sha256(raw).hexdigest(),
        "n_exact_original_native_full_psf_catalogues_sha_verified":
            sum(x["native_sha256_verified"] for x in out),
        "n_original_science_mask_pairs_retrieved_and_inspected":
            sum(x["original_science_mask_status"]==
                "ORIGINAL_DATED_SCIENCE_MASK_PIXEL_AUDIT_COMPLETED" for x in out),
        "n_independent_fixed_analytic_gaussian_numeric_fits":sum(
            (x.get("independent_original_pixel_fit") or {}).get("status")==
            "INDEPENDENT_PIXEL_GAUSSIAN_NUMERIC_FIT_COMPLETE" for x in out),
        "n_original_matched_early_late_numeric_fit_pairs":
            sum(x["paired_independent_pixel_diagnostics_both_numeric"] for x in groups),
        "n_frozen_original_images_selected_prior_to_any_pixel_fit":len(fixed),
        "original_previous_5_of_8_native_passes_3_of_8_fails_preserved":True,
        "original_previous_1_of_4_two_night_source_pairs_preserved":True,
        "original_six_original_image_instrumental_residuals":out,
        "original_three_same_oid_early_late_pixel_comparisons":groups,
        "n_original_ztf_oid_lightcurves_merged":0,
        "n_physical_fttau_gaia_ztf_counterparts_confirmed":0,
        "n_astrophysical_variables_or_companions_confirmed":0,
        "scientific_r2_complete":False,
        "limitations":[
            "Separate 2D circular Gaussian analytic pixel fit does not validate original ZTF spatially variable PSF or reduce to the same chi statistic.",
            "Images and fit share original ZTF reduction and original WCS; this is not independent survey astrometry or an external stellar control.",
            "Sky-MAD noise proxy and model difference are not calibrated source/instrument WCS-PSF covariance.",
            "Different dated exposures have varying seeing and sky/CCD backgrounds; their ratio is not astrophysical source variability.",
            "Original native candidate quality rejections remain rejected; no physical Gaia-ZTF source identity or high-resolution deblending.",
        ],
    }
