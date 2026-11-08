"""v1.16 — original ZTF science+mask pixel residuals for a native DAOPhot PSF.

This is an instrument *screen*, not photometric calibration, deblending,
an authenticated Gaia–ZTF physical match, or a source detection.

All source coordinates in the cutout are obtained from the original per-image
PSF-fit catalogue ICRS coordinate; the spatial PSF parameters are evaluated
at that same catalogue source's ORIGINAL full-quadrant x/y. Their subpixel
phases must agree, modulo native FITS 1-based/NumPy 0-based origins.

Actual archived science (DN) and mskimg bit flags are independently WCS-
aligned before a PSF is applied. A checkerboard holdout tests *pixels within
the SAME star image*, never independently observed stars or WCS precision.
Only scalar aggregates, quality flags and SHA-256 leave ephemeral memory.
"""
from __future__ import annotations

import hashlib
import math
from urllib.error import HTTPError,URLError

import numpy as np

from .coordinates import validate_icrs
from .v113_official_masks_psf import (
    _one_image, BAD_MASK_BITS, SATURATION_BIT, MASK_ALIGN_TOLERANCE_PIX,
    official_ancillary_url, fetch_ancillary_fits,
)
from .v115_spatial_psf import evaluate_spatial_psf_shape
from .v15_image_pixels import fetch_fits_cutout
from .v18_gaia_references import retarget_same_ztf_exposure

CUTOUT_SIZE_ARCSEC=60
FIT_RADIUS_PIX=9.0
SATURATION_CORE_RADIUS_PIX=4.5
SKY_INNER_RADIUS_PIX=14
SKY_OUTER_RADIUS_PIX=22
MAX_PHASE_DISAGREEMENT_PIX=.22
MAX_MASKED_FIT_FRACTION=.12
MIN_GOOD_SKY=230
MIN_GOOD_FIT_PIXELS=150
MAX_BACKGROUND_NOISE_PROXY_DN=1e9


def _base_status()->dict:
    return {
        "local_masked_psf_model_fit_completed":False,
        "independently_authenticated_gaia_ztf_identity":False,
        "independently_calibrated_astrometric_wcs":False,
        "genuine_independent_stellar_psf_control_validation":False,
        "true_photometric_flux_calibration_completed":False,
        "physical_variability_or_companion_confirmed":False,
        "checkerboard_pixels_are_same_source_image_not_independent_stars":True,
    }


def _masked_fit(science_raw:bytes,mask_raw:bytes,parsed_psf:dict, *,
                original_psfcat_ra:float,original_psfcat_dec:float,
                native_psfcat_x:float,native_psfcat_y:float)->dict:
    """Apply spatial model only if source geometry AND independent mask WCS pass.

    Fit amplitude, constant sky and two sky gradients using source-pixel
    checkerboard training pixels; report residuals on disjoint same-image
    pixels that were not used to solve those four parameters.
    """
    validate_icrs(original_psfcat_ra,original_psfcat_dec)
    sci,hs,swcs=_one_image(science_raw)
    msk,hm,mwcs=_one_image(mask_raw)
    base={**_base_status(),
          "science_fits_sha256":hashlib.sha256(science_raw).hexdigest(),
          "mask_fits_sha256":hashlib.sha256(mask_raw).hexdigest(),
          "native_psf_file_sha256":parsed_psf["source_sha256"]}
    if sci.shape!=msk.shape or min(sci.shape)<46:
        return {**base,"status":"ORIGINAL_SCIENCE_MASK_PIXEL_SHAPE_MISMATCH"}
    if not(swcs.has_celestial and mwcs.has_celestial
           and swcs.pixel_n_dim==2 and mwcs.pixel_n_dim==2
           and swcs.world_n_dim==2 and mwcs.world_n_dim==2):
        return {**base,"status":"ORIGINAL_SCIENCE_MASK_CELESTIAL_WCS_MISSING"}
    try:
        h,w=sci.shape
        mapping=[]
        for xx,yy in ((1.,1.),(w/2,h/2),(w-2.,h-2.)):
            ra,dec=swcs.pixel_to_world_values(xx,yy)
            mx,my=mwcs.world_to_pixel_values(ra,dec)
            mapping.append(math.hypot(float(mx)-xx,float(my)-yy))
        px,py=map(float,swcs.world_to_pixel_values(
            original_psfcat_ra,original_psfcat_dec))
    except (ValueError,TypeError,OverflowError,ArithmeticError):
        return {**base,"status":"SCIENCE_MASK_WCS_MAPPING_INCOMPLETE"}
    if not all(math.isfinite(q) for q in [*mapping,px,py]):
        return {**base,"status":"SCIENCE_MASK_WCS_MAPPING_NONFINITE"}
    grid_err=max(mapping)
    if grid_err>MASK_ALIGN_TOLERANCE_PIX:
        return {**base,"status":"SCIENCE_MASK_WCS_PIXEL_GRID_NOT_ALIGNED",
                "max_registration_offset_pixels":round(grid_err,6)}
    if not (24<=px<w-24 and 24<=py<h-24):
        return {**base,"status":"SOURCE_PSF_AND_SKY_STAMP_OFF_IMAGE"}
    try:
        vals=np.asarray(msk,dtype=np.float64)
    except (TypeError,ValueError,OverflowError):
        return {**base,"status":"MASK_PIXEL_VALUES_INVALID"}
    if not (np.isfinite(vals).all() and np.all(vals>=0)
            and np.all(vals<=65535) and np.all(vals==np.floor(vals))):
        return {**base,"status":"MASK_PIXEL_VALUES_INVALID"}
    masks=vals.astype(np.uint16)
    # The physical PSF catalogue uses 1-based native detector coordinates,
    # while the FITS cutout WCS returns zero-based NumPy pixel coordinates.
    # Origin shifts by an integer are harmless to the fractional phase.
    xi=int(round(px));yi=int(round(py))
    fx=float(px-xi);fy=float(py-yi)
    original_native_x=float(native_psfcat_x)
    original_native_y=float(native_psfcat_y)
    if not all(math.isfinite(v) for v in (original_native_x,original_native_y)):
        return {**base,"status":"NATIVE_DETECTOR_COORDINATES_INVALID"}
    fracx=original_native_x-round(original_native_x)
    fracy=original_native_y-round(original_native_y)
    mismatchx=abs(((fx-fracx+.5)%1)-.5)
    mismatchy=abs(((fy-fracy+.5)%1)-.5)
    if max(mismatchx,mismatchy)>MAX_PHASE_DISAGREEMENT_PIX:
        return {**base,"status":"ORIGINAL_PSF_CATALOGUE_AND_CUTOUT_SUBPIXEL_PHASE_MISMATCH",
                "native_vs_wcs_subpixel_x_difference":round(mismatchx,5),
                "native_vs_wcs_subpixel_y_difference":round(mismatchy,5)}
    try:
        model=evaluate_spatial_psf_shape(
            parsed_psf,x=original_native_x,y=original_native_y,
            frac_x=fx,frac_y=fy)
    except (ValueError,TypeError,KeyError,OverflowError):
        return {**base,"status":"ORIGINAL_SPATIAL_DAOPHOT_PSF_MODEL_UNEVALUABLE"}
    radius=model.shape[0]//2
    if radius!=11:
        return {**base,"status":"UNEXPECTED_SPATIAL_MODEL_PSF_STAMP"}
    # Sky annulus is evaluated on full cutout; retain only finite unflagged
    # science pixels. Fits in original ZTF DN, NOT calibrated magnitudes.
    yy,xx=np.indices(sci.shape,dtype=float)
    rr=np.hypot(xx-px,yy-py)
    good=np.isfinite(sci)&((masks&BAD_MASK_BITS)==0)
    annulus=(rr>=SKY_INNER_RADIUS_PIX)&(rr<=SKY_OUTER_RADIUS_PIX)
    sky=np.asarray(sci[good&annulus],dtype=float)
    if sky.size<MIN_GOOD_SKY:
        return {**base,"status":"INSUFFICIENT_UNMASKED_SKY_ANNULUS_PIXELS",
                "n_clean_sky_pixels":int(sky.size)}
    for _ in range(3):
        mid=float(np.median(sky))
        mad=float(1.4826*np.median(np.abs(sky-mid)))
        if not math.isfinite(mad) or mad<1e-8:
            return {**base,"status":"ORIGINAL_BACKGROUND_NOISE_MAD_UNUSABLE"}
        remaining=sky[np.abs(sky-mid)<=4*mad]
        if remaining.size<MIN_GOOD_SKY:
            return {**base,"status":"INSUFFICIENT_CLIPPED_CLEAN_SKY_PIXELS"}
        sky=remaining
    bg_proxy=float(np.median(sky))
    sky_sigma=float(1.4826*np.median(np.abs(sky-bg_proxy)))
    if not 1e-8<sky_sigma<MAX_BACKGROUND_NOISE_PROXY_DN:
        return {**base,"status":"ORIGINAL_BACKGROUND_NOISE_MAD_UNUSABLE"}
    # Exact cutout-local square and original detector bitmask.
    ys=slice(yi-radius,yi+radius+1)
    xs=slice(xi-radius,xi+radius+1)
    cut=np.asarray(sci[ys,xs],dtype=float)
    bad=(masks[ys,xs]&BAD_MASK_BITS)!=0
    invalid=~np.isfinite(cut)
    gy,gx=np.mgrid[-radius:radius+1,-radius:radius+1]
    rad=np.hypot(gx-fx,gy-fy)
    core=rad<=SATURATION_CORE_RADIUS_PIX
    n_bad_core=int(np.count_nonzero(bad&core))
    n_nonfinite_core=int(np.count_nonzero(invalid&core))
    saturated_core=int(np.count_nonzero(((masks[ys,xs]&SATURATION_BIT)!=0)&core))
    if n_bad_core or n_nonfinite_core:
        return {**base,"status":"SOURCE_CORE_HAS_BAD_OR_SATURATED_OR_NONFINITE_PIXELS",
                "n_core_bad_mask_pixels":n_bad_core,
                "n_core_saturated_pixels":saturated_core,
                "n_core_nonfinite_pixels":n_nonfinite_core}
    area=rad<=FIT_RADIUS_PIX
    usable=area&~bad&~invalid
    fit_frac=1-(int(usable.sum())/int(area.sum()))
    if fit_frac>MAX_MASKED_FIT_FRACTION or int(usable.sum())<MIN_GOOD_FIT_PIXELS:
        return {**base,"status":"PSF_FIT_TOO_FEW_UNMASKED_PIXELS",
                "fit_masked_fraction":round(float(fit_frac),5)}
    # Chessboard model check: fit four coefficients only on training pixels,
    # then score residuals on a separate checkerboard of SAME star image.
    tr=usable&(((gx+gy)%2)==0)
    ho=usable&~tr
    if int(tr.sum())<75 or int(ho.sum())<75:
        return {**base,"status":"INSUFFICIENT_SAME_IMAGE_HOLDOUT_PIXELS"}
    terms=np.column_stack((model[tr],np.ones(int(tr.sum())),
                           gx[tr],gy[tr]))
    try:
        coefficients,_,rank,_=np.linalg.lstsq(
            terms,cut[tr],rcond=None)
        condition=float(np.linalg.cond(terms))
    except np.linalg.LinAlgError:
        return {**base,"status":"ORIGINAL_PSF_LINEAR_FIT_SINGULAR"}
    if rank!=4 or not math.isfinite(condition) or condition>1e6:
        return {**base,"status":"ORIGINAL_PSF_LINEAR_FIT_ILL_CONDITIONED"}
    amp,b0,bx,by=map(float,coefficients)
    if not all(math.isfinite(v) for v in (amp,b0,bx,by)) or amp<=0:
        return {**base,"status":"ORIGINAL_PSF_NONPOSITIVE_OR_NONFINITE_FLUX"}
    fitted=amp*model+b0+bx*gx+by*gy
    test_res=(cut-fitted)[ho]
    train_res=(cut-fitted)[tr]
    test_rms=math.sqrt(float(np.mean(test_res**2)))
    train_rms=math.sqrt(float(np.mean(train_res**2)))
    test_norm=test_rms/sky_sigma
    peak_norm=float(np.max(test_res))/sky_sigma
    # A descriptive engineering screen; no Gaussian-noise independent
    # chi-square statistic, no photometric flux variance/no WCS uncertainty.
    adequate=(test_norm<=3. and peak_norm<=7.
              and amp/max(sky_sigma,1e-6)>=10.)
    return {
        **base,
        "status":("PROVISIONAL_ORIGINAL_MASKED_PSF_PIXEL_RESIDUAL_SCREEN_PASSED"
                  if adequate else "ORIGINAL_MASKED_PSF_PIXEL_RESIDUAL_REVIEW_REQUIRED"),
        "local_masked_psf_model_fit_completed":True,
        "science_and_mask_wcs_registration_within_0p05_pixel":True,
        "max_science_mask_grid_error_pixels":round(grid_err,7),
        "native_psfcat_vs_wcs_subpixel_phase_max_disagreement_pixels":
            round(max(mismatchx,mismatchy),6),
        "n_masked_core_pixels":n_bad_core,
        "n_saturated_core_pixels":saturated_core,
        "n_unmasked_fit_pixels":int(usable.sum()),
        "n_unmasked_sky_annulus_pixels":int(sky.size),
        "n_same_image_fit_training_pixels":int(tr.sum()),
        "n_same_image_checkerboard_heldout_pixels":int(ho.sum()),
        "fitted_native_psf_amplitude_dn_unscaled":round(amp,6),
        "fitted_background_dn":round(b0,6),
        "fitted_background_gradient_x_dn_per_pixel":round(bx,6),
        "fitted_background_gradient_y_dn_per_pixel":round(by,6),
        "independent_sky_annulus_mad_noise_proxy_dn":round(sky_sigma,6),
        "same_image_holdout_residual_rms_dn":round(test_rms,6),
        "same_image_holdout_residual_rms_over_sky_noise_proxy":round(test_norm,6),
        "same_image_holdout_max_positive_residual_over_sky_noise_proxy":
            round(peak_norm,6),
        "same_image_training_residual_rms_dn":round(train_rms,6),
        "native_psf_model_correction_not_calibrated_with_real_independent_stars":True,
    }


def audit_original_source_psf_residuals(science_url:str,parsed_psf:dict,*,
                                        source_ra:float,source_dec:float,
                                        native_x:float,native_y:float,
                                        timeout:float=6,
                                        fetch_mask=None,fetch_science=None)->dict:
    """Fetch same-exposure 60-arcsec science/mask product pair, fail closed."""
    if fetch_mask is None:fetch_mask=fetch_ancillary_fits
    if fetch_science is None:fetch_science=fetch_fits_cutout
    src=retarget_same_ztf_exposure(
        science_url,source_ra,source_dec,size_arcsec=CUTOUT_SIZE_ARCSEC)
    maskurl=official_ancillary_url(src,"mskimg.fits")
    try:
        rawmask=fetch_mask(maskurl,kind="mskimg.fits",timeout=timeout)
        rawscience=fetch_science(src,timeout=timeout)
        return _masked_fit(
            rawscience,rawmask,parsed_psf,
            original_psfcat_ra=source_ra,
            original_psfcat_dec=source_dec,
            native_psfcat_x=native_x,native_psfcat_y=native_y)
    except (HTTPError,URLError,TimeoutError,OSError,ValueError) as exc:
        out={**_base_status(),"status":"ORIGINAL_SCIENCE_OR_MASK_ACCESS_OR_FORMAT_FAILED",
             "error_type":type(exc).__name__}
        if isinstance(exc,HTTPError):out["http_status"]=int(exc.code)
        return out
