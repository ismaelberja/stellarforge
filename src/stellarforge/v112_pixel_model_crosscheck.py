"""v1.12 provisional source-shape and centroid remeasurement on actual ZTF FITS.

Two distinct methods are evaluated on the SAME pixels: the existing v1.6
Gaussian+planar-sky model, and a new plane-subtracted positive-flux aperture
centroid/moment estimator. Their agreement is a *model sensitivity* diagnostic,
NOT independently calibrated WCS/PSF, true astrometric precision, a validated
stellar source, resolved blend, or companion detection.

All original FITS pixels remain in memory and are not returned or exported.
"""
from __future__ import annotations

import hashlib
import io
import math
from urllib.error import HTTPError, URLError

from .v15_image_pixels import inspect_fits_cutout, fetch_fits_cutout
from .v16_psf_repeatability import fit_local_gaussian_proxy, PSF_OK
from .v18_gaia_references import retarget_same_ztf_exposure
from .v110_reference_holdout import leave_one_out_translation

SUCCESS = "APERTURE_GAUSSIAN_CONSISTENT_PROVISIONAL"
REVIEW = "INDEPENDENT_APERTURE_MODEL_REVIEW_REQUIRED"
INCOMPLETE = "APERTURE_CENTROID_SCREEN_INCOMPLETE"
MAX_CENTROID_DISAGREEMENT_ARCSEC = 0.35
MAX_FITS_SIDE = 400


def aperture_and_gaussian_centroid_screen(
    raw: bytes, *, expected_ra_deg: float, expected_dec_deg: float,
    mjd_assumed_utc: float, image_kind: str = "science",
) -> dict:
    """Recompute real pixels with robust tilted sky, aperture moments and Gaussian.

    Internal image-estimator sensitivity only. No original photometry, FITS,
    sky-cutout arrays, full headers, or source-image URLs are returned.
    """
    import numpy as np
    from astropy.io import fits
    from astropy.wcs import WCS

    if image_kind != "science":
        raise ValueError("Only original dated science FITS images allowed")
    if not math.isfinite(mjd_assumed_utc) or not 55000 <= mjd_assumed_utc <= 80000:
        raise ValueError("Unsupported science observation epoch")
    screened=inspect_fits_cutout(
        raw, expected_ra_deg=expected_ra_deg,
        expected_dec_deg=expected_dec_deg)
    if screened["status"] != "PIXEL_WCS_PROVISIONAL_SCREEN_COMPLETED":
        return {
            "status": INCOMPLETE, "prior_pixel_screen": screened["status"],
            "single_star_psf_authenticated": False,
            "instrument_astrometry_calibrated": False,
            "gaia_ztf_source_identity_confirmed": False,
        }
    fit=fit_local_gaussian_proxy(
        raw, expected_ra_deg=expected_ra_deg,
        expected_dec_deg=expected_dec_deg, image_kind="science")
    with fits.open(io.BytesIO(raw), memmap=False) as hdul:
        images = [h for h in hdul if getattr(h,"data",None) is not None
                  and getattr(h.data,"ndim",None)==2]
        if len(images) != 1:
            raise ValueError("FITS expected to contain exactly one 2D plane")
        data=np.asarray(images[0].data,dtype=float).copy()
        header=images[0].header.copy()
    if min(data.shape)<35 or max(data.shape)>MAX_FITS_SIDE:
        return _incomplete("INSUFFICIENT_FITS_IMAGE_EXTENT", fit)
    wcs=WCS(header)
    tx,ty=map(float,wcs.world_to_pixel_values(expected_ra_deg,expected_dec_deg))
    if not math.isfinite(tx) or not math.isfinite(ty):
        return _incomplete("INVALID_PREDICTED_WCS_PIXEL",fit)
    yy,xx=np.indices(data.shape,dtype=float)
    rr=np.hypot(xx-tx,yy-ty)
    finite=np.isfinite(data)
    ann=finite & (rr>=9) & (rr<15)
    ap=finite & (rr<=4.5)
    if int(ann.sum())<80 or int(ap.sum())<45:
        return _incomplete("INSUFFICIENT_FINITE_SKY_OR_APERTURE_PIXELS",fit)
    if np.any((rr<=4.5)&(~finite)):
        return _incomplete("NONFINITE_APERTURE_PIXEL",fit)
    basis=np.column_stack((np.ones(int(ann.sum())),
                           xx[ann]-tx,yy[ann]-ty))
    values=data[ann]
    keep=np.ones(len(values),dtype=bool)
    plane=None
    sky_sigma=None
    # Iterative sigma-clipped local sky plane fit, separate from the v1.6
    # parametric Gaussian+plane fit but sharing this same original FITS.
    for _ in range(3):
        if keep.sum()<60:
            return _incomplete("INSUFFICIENT_UNCONTAMINATED_SKY_PIXELS",fit)
        plane, *_=np.linalg.lstsq(basis[keep],values[keep],rcond=None)
        resid=values-basis@plane
        med=float(np.median(resid[keep]))
        sky_sigma=float(1.4826*np.median(np.abs(resid[keep]-med)))
        if not math.isfinite(sky_sigma) or sky_sigma<=1e-10:
            return _incomplete("BACKGROUND_NOISE_PROXY_UNDEFINED",fit)
        keep=np.abs(resid-med)<3.5*sky_sigma
    if keep.sum()<60:
        return _incomplete("SKY_SIGMA_CLIPPING_REMOVED_TOO_MUCH",fit)

    sky=plane[0]+plane[1]*(xx[ap]-tx)+plane[2]*(yy[ap]-ty)
    values_ap=data[ap]-sky
    weights=np.maximum(values_ap,0.0)
    signal=float(np.sum(weights))
    local_peak=float(np.max(values_ap))
    if not math.isfinite(signal) or signal < 35*sky_sigma or local_peak<8*sky_sigma:
        return _incomplete("APERTURE_SOURCE_SNR_PROXY_INSUFFICIENT",fit)
    xc=float(np.sum(xx[ap]*weights)/signal)
    yc=float(np.sum(yy[ap]*weights)/signal)
    dx=xx[ap]-xc
    dy=yy[ap]-yc
    mxx=float(np.sum(weights*dx*dx)/signal)
    myy=float(np.sum(weights*dy*dy)/signal)
    mxy=float(np.sum(weights*dx*dy)/signal)
    moment=np.array([[mxx,mxy],[mxy,myy]])
    eig=np.linalg.eigvalsh(moment)
    if not np.isfinite(eig).all() or eig[0]<=1e-8:
        return _incomplete("DEGENERATE_APERTURE_MORPHOLOGY_PROXY",fit)
    ratio=math.sqrt(float(eig[1]/eig[0]))
    xc_sky,yc_sky=map(float,wcs.pixel_to_world_values(xc,yc))
    dra=((xc_sky-expected_ra_deg+180)%360)-180
    aperture_east=dra*math.cos(math.radians(expected_dec_deg))*3600
    aperture_north=(yc_sky-expected_dec_deg)*3600

    image_mjd=None
    for field in ("OBSMJD","MJD-OBS","MJDOBS"):
        v=header.get(field)
        if isinstance(v,(int,float)) and math.isfinite(float(v)):
            image_mjd=float(v)
            break
    delta_mjd=(abs(image_mjd-mjd_assumed_utc) if image_mjd is not None else None)
    # Metadata congruence may refer to start vs mid-exposure and differing
    # time systems. We deliberately DO NOT certify a clock/time-scale.
    time_metadata_status=(
        "NO_INDEPENDENT_FITS_MJD_METADATA" if delta_mjd is None else
        "FITS_MJD_FAR_FROM_ORIGINAL_QUERY" if delta_mjd>0.04 else
        "FITS_MJD_NEAR_QUERY_NOT_TIMESCALE_VERIFIED")

    # Raw sciimg pixels may not have saturation or data quality masks. Never
    # treat absent SATURATE metadata as proof of no saturated pixels.
    sat=header.get("SATURATE")
    saturation_threshold_present=(isinstance(sat,(int,float))
                                 and math.isfinite(float(sat)))
    # Even with an advertised threshold, do not assume raw detector-bitmask
    # or units needed for calibrated saturation rejection are available.
    saturation_status=(
        "HEADER_THRESHOLD_ONLY_UNCALIBRATED"
        if saturation_threshold_present else
        "SATURATION_FLAG_OR_THRESHOLD_UNAVAILABLE")
    if fit["status"] in PSF_OK:
        fit_east=fit["fitted_centroid_east_minus_Gaia_arcsec"]
        fit_north=fit["fitted_centroid_north_minus_Gaia_arcsec"]
        difference=math.hypot(aperture_east-fit_east,
                              aperture_north-fit_north)
    else:
        difference=None
    good_morphology=(ratio<=2.0 and math.hypot(xc-tx,yc-ty)<2.0)
    clean_fit=fit["status"]=="PSF_PROXY_PROVISIONAL_ONLY"
    # No source identification is established even for matched centroids.
    eligible=(good_morphology and clean_fit and difference is not None
              and difference<=MAX_CENTROID_DISAGREEMENT_ARCSEC
              and time_metadata_status!="FITS_MJD_FAR_FROM_ORIGINAL_QUERY")
    return {
        "status":SUCCESS if eligible else REVIEW,
        "fits_sha256":hashlib.sha256(raw).hexdigest(),
        "image_shape_pixels":list(map(int,data.shape)),
        "mjd_query_assumed_utc":round(mjd_assumed_utc,6),
        "fits_mjd_header_value":round(image_mjd,6) if image_mjd is not None else None,
        "fits_vs_query_mjd_difference_days":(
            round(delta_mjd,6) if delta_mjd is not None else None),
        "fits_timing_metadata_status":time_metadata_status,
        "utc_time_scale_independently_validated":False,
        "saturation_screen_status":saturation_status,
        "detector_saturation_mask_implemented":False,
        "bad_pixel_mask_independently_validated":False,
        "sky_annulus_n_pixel_kept":int(keep.sum()),
        "local_background_plane_gradient_x_data_per_pixel":round(float(plane[1]),6),
        "local_background_plane_gradient_y_data_per_pixel":round(float(plane[2]),6),
        "sky_mad_noise_proxy":round(sky_sigma,6),
        "aperture_positive_flux_proxy":round(signal,5),
        "aperture_peak_snr_proxy":round(local_peak/sky_sigma,3),
        "aperture_east_minus_gaia_arcsec":round(aperture_east,6),
        "aperture_north_minus_gaia_arcsec":round(aperture_north,6),
        "aperture_centroid_pixel_shift_from_expected":round(
            math.hypot(xc-tx,yc-ty),5),
        "aperture_second_moment_axis_ratio_proxy":round(ratio,5),
        "gaussian_fit_status":fit["status"],
        "gaussian_model_outer_residual_over_noise":(
            fit.get("max_outer_positive_residual_over_noise")),
        "gaussian_fit_near_bound":fit.get("fit_parameter_near_bound"),
        "gaussian_east_minus_gaia_arcsec":(
            fit.get("fitted_centroid_east_minus_Gaia_arcsec")),
        "gaussian_north_minus_gaia_arcsec":(
            fit.get("fitted_centroid_north_minus_Gaia_arcsec")),
        "aperture_vs_gaussian_centroid_difference_arcsec":(
            round(difference,6) if difference is not None else None),
        "fit_quality_allows_provisional_internal_control":eligible,
        "aperture_and_gaussian_are_not_independent_exposures":True,
        "independent_instrument_wcs_error_calibrated":False,
        "single_star_psf_authenticated":False,
        "gaia_ztf_source_identity_confirmed":False,
        "new_astrophysical_companion_confirmed":False,
    }


def _incomplete(reason: str, fit: dict) -> dict:
    return {
        "status":INCOMPLETE,
        "reason":reason,"gaussian_fit_status":fit["status"],
        "fit_quality_allows_provisional_internal_control":False,
        "independent_instrument_wcs_error_calibrated":False,
        "single_star_psf_authenticated":False,
        "gaia_ztf_source_identity_confirmed":False,
    }


def audit_provisional_field_references(measurements: list[dict]) -> dict:
    """LOO on screenable reference *candidates* only; never a WCS solution."""
    ids=[str(x["gaia_source_id"]) for x in measurements]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate reference star in one field exposure")
    chosen=[x for x in measurements if
            x.get("status")==SUCCESS and
            x.get("fit_quality_allows_provisional_internal_control") is True]
    gauss=[
        {"id":m["gaia_source_id"],
         "east":m["gaussian_east_minus_gaia_arcsec"],
         "north":m["gaussian_north_minus_gaia_arcsec"]}
        for m in chosen]
    aperture=[
        {"id":m["gaia_source_id"],
         "east":m["aperture_east_minus_gaia_arcsec"],
         "north":m["aperture_north_minus_gaia_arcsec"]}
        for m in chosen]
    if set(x["id"] for x in gauss)!=set(x["id"] for x in aperture):
        raise ValueError("Mismatched aperture/Gaussian source sets")
    return {
        "n_reference_candidates_measured":len(measurements),
        "n_provisionally_image_model_consistent":len(chosen),
        "gaussian_reference_internal_holdout":leave_one_out_translation(gauss),
        "aperture_reference_internal_holdout":leave_one_out_translation(aperture),
        "n_scientifically_authenticated_reference_stars":0,
        "independently_calibrated_wcs":False,
        "empirical_psf_calibrated":False,
    }


def analyze_real_science_reference_cutout(
    science_url: str, source_gaia_position: dict, *,
    mjd_assumed_utc: float, timeout: float = 6.0,
    fetch=fetch_fits_cutout, inspect=aperture_and_gaussian_centroid_screen,
) -> dict:
    """Bounded same-dated ZTF product, geocentric-corrected sky centered."""
    if not source_gaia_position.get("full_gaia_five_parameter_formal_covariance_propagated"):
        raise ValueError("Source lacks complete Gaia five-parameter formal covariance")
    ra=source_gaia_position["geocentric_parallax_adjusted_ra_deg"]
    dec=source_gaia_position["geocentric_parallax_adjusted_dec_deg"]
    url=retarget_same_ztf_exposure(science_url,ra,dec,size_arcsec=45)
    report={
        "gaia_source_id":source_gaia_position["source_id"],
        "gaia_formal_east_sigma_mas":
            source_gaia_position["formal_gaia_east_sigma_mas"],
        "gaia_formal_north_sigma_mas":
            source_gaia_position["formal_gaia_north_sigma_mas"],
        "gaia_ruwe_quality_warning":
            source_gaia_position["high_or_missing_ruwe_quality_warning"],
        "science_fits_pixel_source_refitted":True,
        "gaia_ztf_source_identity_confirmed":False,
    }
    try:
        raw=fetch(url,timeout=timeout)
        result=inspect(raw,expected_ra_deg=ra,expected_dec_deg=dec,
                       mjd_assumed_utc=mjd_assumed_utc)
        report.update(result)
    except (HTTPError,URLError,TimeoutError,OSError,ValueError) as exc:
        report["status"]="ZTF_SCIENCE_FITS_ACCESS_OR_VALIDATION_FAILED"
        report["error_type"]=type(exc).__name__
        if isinstance(exc,HTTPError):
            report["http_status"]=int(exc.code)
    return report
