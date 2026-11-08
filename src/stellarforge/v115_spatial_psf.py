"""v1.15: bounded ZTF DAOPhot spatial PSF *reconstruction* and central check.

Parses an original ASCII GAUSSIAN sciimgdao.psf lookup product (separate
from the FITS center stamp) with a pixel-integrated analytic Gaussian base,
three or six spatial correction tables sampled on a half-pixel grid.
Cubic-spline interpolation here is an approximation of DAOPhot bicubic
interpolation; comparison to the official center FITS product is mandatory.

An approximate reconstructed shape at a catalogued x/y detector position
is NOT a calibrated source-local PSF until center verification and original
image/bitmask/neighbor data allow independent residual validation.
Never exports raw PSF lookup arrays or original FITS product pixels.
"""
from __future__ import annotations

import hashlib
import io
import math
import re
from typing import Any

import numpy as np
from astropy.io import fits
from scipy.ndimage import map_coordinates
from scipy.special import erf

# Example original ZTF product has size=47 and n_tables=3. Other variants
# are accepted ONLY with an explicit bounded same-spec table count.
HEADER_BASE="GAUSSIAN"
ALLOWED_TABLE_COUNTS=(1,3,6)
MAX_PSF_GRID=101
MAX_LUT_SIZE_BYTES=4_000_000
MAX_LUT_ELEMENTS=6*MAX_PSF_GRID**2
MAX_ABS_CORRECTION_COEFFICIENT=1e9
FLOAT_SCI_RE=re.compile(r"[+-]?(?:\d+\.\d+|\d+\.|\.\d+)[eE][+-]\d{1,3}")


def parse_original_daophot_lookup(raw:bytes)->dict[str,Any]:
    if not isinstance(raw,bytes) or not 100<=len(raw)<=MAX_LUT_SIZE_BYTES:
        raise ValueError("Missing or over-budget spatial DAOPhot original product")
    try:
        text=raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("Non-ASCII DAOPHOT original lookup table") from exc
    lines=text.splitlines()
    if len(lines)<3:
        raise ValueError("Truncated DAOPhot original table")
    h=lines[0].split()
    if len(h)<9 or h[0].upper()!=HEADER_BASE:
        raise ValueError("Unknown original DAOPhot analytic model/header")
    try:
        side=int(h[1])
        ntable=int(h[3])
        amp=float(h[6])
        xc=float(h[7])
        yc=float(h[8])
        sig=[float(x) for x in lines[1].split()]
    except (ValueError,TypeError,IndexError) as exc:
        raise ValueError("Malformed native DAOPhot Gaussian header") from exc
    if (side<15 or side>MAX_PSF_GRID or side%4!=3
        or ntable not in ALLOWED_TABLE_COUNTS
        or len(sig)!=2
        or not all(math.isfinite(v) for v in (amp,xc,yc,*sig))
        or not (0<amp<1e9 and 200<xc<4000 and 200<yc<4000
                and 0.15<sig[0]<20 and 0.15<sig[1]<20)):
        raise ValueError("Unsupported/unsafe spatial PSF geometry or Gaussian parameters")
    body="\n".join(lines[2:])
    tokens=FLOAT_SCI_RE.findall(body)
    if len(tokens)!=ntable*side*side:
        raise ValueError("DAOPhot correction coefficient count does not match header")
    if FLOAT_SCI_RE.sub("",body).strip():
        raise ValueError("Unexpected content in native DAOPhot lookup table")
    vals=np.asarray([float(v) for v in tokens],dtype=np.float64)
    if (not np.isfinite(vals).all()
        or np.max(np.abs(vals))>MAX_ABS_CORRECTION_COEFFICIENT):
        raise ValueError("Nonfinite or outlier DAOPhot lookup correction")
    return {
        "header_type":HEADER_BASE,
        "source_sha256":hashlib.sha256(raw).hexdigest(),
        "n_lookup_tables":ntable,"lookup_side_samples":side,
        "analytic_hwhm_x_pixels":sig[0],
        "analytic_hwhm_y_pixels":sig[1],
        "gaussian_peak_amplitude_parameter":amp,
        "detector_field_center_x":xc,
        "detector_field_center_y":yc,
        "tables":vals.reshape(ntable,side,side),
        "spatial_basis_convention":"approximate DAOPHOT linear/quadratic normalized-detector offsets",
        "interpolation_convention":"cubic B-spline rather than independently validated DAOPHOT BICUBC",
        "science_single_star_identity_confirmed":False,
    }


def _pixel_gaussian_area(offset:np.ndarray,hwhm:float)->np.ndarray:
    # Exact analytic integral across a width-1 pixel; HWHM parameter.
    sigma=hwhm/math.sqrt(2*math.log(2))
    w=math.sqrt(2)*sigma
    return sigma*math.sqrt(math.pi/2)*(
        erf((offset+.5)/w)-erf((offset-.5)/w))


def _spatial_weights(x:float,y:float,psf:dict)->np.ndarray:
    cx=psf["detector_field_center_x"]
    cy=psf["detector_field_center_y"]
    # x/y are ORIGINAL native CCD-quadrant pipeline coordinates, not
    # cutout-local WCS pixel coordinates.
    if (not math.isfinite(x) or not math.isfinite(y)
        or not (0<x<=2*cx and 0<y<=2*cy)):
        raise ValueError("PSF requested outside bounded native detector geometry")
    dx=(x-cx)/cx
    dy=(y-cy)/cy
    weights=np.array([
        1.,dx,dy,
        1.5*dx*dx-.5,
        dx*dy,
        1.5*dy*dy-.5],dtype=float)
    return weights[:psf["n_lookup_tables"]]


def evaluate_spatial_psf_shape(parsed:dict,*,x:float,y:float,
                               frac_x:float=0,frac_y:float=0)->np.ndarray:
    """Normalized approximate spatial PSF array at actual native CCD x/y.

    No fit/no photometry, no WCS and no physical crossmatch.
    Comparison against original center PSF is an independent MODEL CHECK only.
    """
    if (not math.isfinite(frac_x) or not math.isfinite(frac_y)
        or abs(frac_x)>.5 or abs(frac_y)>.5):
        raise ValueError("Invalid within-pixel centroid offset")
    w=_spatial_weights(x,y,parsed)
    n=parsed["lookup_side_samples"]
    radius=(n-1)//4
    ygrid,xgrid=np.mgrid[-radius:radius+1,-radius:radius+1]
    xx=xgrid-frac_x
    yy=ygrid-frac_y
    gauss=(parsed["gaussian_peak_amplitude_parameter"]
           *_pixel_gaussian_area(xx,parsed["analytic_hwhm_x_pixels"])
           *_pixel_gaussian_area(yy,parsed["analytic_hwhm_y_pixels"])
           /(parsed["analytic_hwhm_x_pixels"]*parsed["analytic_hwhm_y_pixels"]))
    center=(n-1)/2
    coords=np.vstack([(2*yy+center).ravel(),(2*xx+center).ravel()])
    resid=np.zeros_like(gauss,dtype=float)
    for coeff,tab in zip(w,parsed["tables"]):
        resid+=coeff*map_coordinates(
            tab,coords,order=3,mode="constant",cval=0,prefilter=True
        ).reshape(gauss.shape)
    psf=np.where(np.hypot(xx,yy)<=radius,np.maximum(gauss+resid,0),0)
    total=float(psf.sum())
    if not math.isfinite(total) or total<=1e-20:
        raise ValueError("Reconstructed spatial PSF is zero or nonfinite")
    psf/=total
    return psf


def psf_image_shape_diagnostics(a:np.ndarray)->dict:
    img=np.asarray(a,dtype=float)
    if img.ndim!=2 or img.shape[0]!=img.shape[1] or img.shape[0]%2!=1:
        raise ValueError("PSF must be a square odd-side image")
    if not np.isfinite(img).all() or np.any(img<0):
        raise ValueError("Invalid PSF normalized shape data")
    flux=float(img.sum())
    if not .9999<=flux<=1.0001:
        raise ValueError("PSF is not normalized")
    yy,xx=np.indices(img.shape,dtype=float)
    cx=float((xx*img).sum());cy=float((yy*img).sum())
    sx=math.sqrt(float(((xx-cx)**2*img).sum()))
    sy=math.sqrt(float(((yy-cy)**2*img).sum()))
    return {
        "shape":list(map(int,img.shape)),
        "x_centroid_pixel":round(cx,4),
        "y_centroid_pixel":round(cy,4),
        "second_moment_sigma_x_pixels":round(sx,5),
        "second_moment_sigma_y_pixels":round(sy,5),
    }


def _read_original_center_psf(raw:bytes)->np.ndarray:
    if not isinstance(raw,bytes) or not 2880<=len(raw)<=3_000_000:
        raise ValueError("Invalid archived center FITS stamp bytes")
    with fits.open(io.BytesIO(raw),memmap=False) as hdul:
        images=[h for h in hdul if getattr(h,"data",None) is not None
                and getattr(h.data,"ndim",None)==2]
        if len(images)!=1:
            raise ValueError("Original center PSF FITS must have exactly one image")
        arr=np.asarray(images[0].data,dtype=float).copy()
    if arr.ndim!=2 or arr.shape[0]!=arr.shape[1] or arr.shape[0]%2!=1:
        raise ValueError("Center PSF stamp shape invalid")
    if not np.isfinite(arr).all():
        raise ValueError("Nonfinite native center PSF FITS stamp")
    arr=np.clip(arr,0,None)
    if arr.sum()<=0:
        raise ValueError("No positive original PSF FITS flux")
    return arr/arr.sum()


def compare_reconstruction_to_official_center(parsed:dict,raw_center:bytes)->dict:
    native=_read_original_center_psf(raw_center)
    predicted=evaluate_spatial_psf_shape(
        parsed,x=parsed["detector_field_center_x"],
        y=parsed["detector_field_center_y"])
    if predicted.shape!=native.shape:
        return {
            "status":"NATIVE_CENTER_PSF_SHAPE_MISMATCH",
            "predicted_shape":list(predicted.shape),
            "official_shape":list(native.shape),
            "local_spatial_psf_calibrated":False,
        }
    dot=float(np.sum(native*predicted))
    norm=math.sqrt(float(np.sum(native*native)*np.sum(predicted*predicted)))
    cosine=dot/norm if norm>0 else 0.
    l1=float(np.sum(np.abs(native-predicted)))
    # Conservative pre-registered engineering thresholds: NOT a survey
    # calibrated model error statistic or independent star-based validation.
    model_consistency=cosine>=.93 and l1<=.50
    return {
        "status":("OFFICIAL_CENTER_PSF_APPROXIMATE_MODEL_AGREEMENT"
                  if model_consistency else
                  "OFFICIAL_CENTER_PSF_RECONSTRUCTION_DISAGREEMENT_REVIEW"),
        "native_center_fits_sha256":hashlib.sha256(raw_center).hexdigest(),
        "model_vs_official_center_cosine_similarity":round(cosine,6),
        "model_vs_official_center_normalized_l1":round(l1,6),
        "n_native_center_stamp_pixels":int(native.size),
        "official_native_psf_field_center_only":True,
        "same_underlying_daophot_pipeline_not_independent_stars":True,
        "local_spatial_psf_calibrated":False,
        "independently_calibrated_detector_wcs":False,
    }


def summarize_evaluated_candidate_psfs(parsed:dict,screens:list[dict],
                                      *,center_check:dict)->dict:
    """Evaluate genuine original native detector positions in v1.14 PSF screens.

    Only 1'' unique-quality *candidates*, not independently authenticated stars.
    Never emit full original PSF pixels or coefficient tables.
    """
    if not isinstance(screens,list) or len(screens)>12:
        raise ValueError("Unexpected original candidate list")
    out=[]
    for s in screens:
        if s.get("status")!="PROVISIONAL_CATALOGUE_NEAREST_AND_PROFILE_SCREEN_PASSED":
            out.append({
                "gaia_source_id":s["gaia_source_id"],
                "status":"NOT_EVALUATED_PSF_CANDIDATE_QUALITY_REVIEW",
                "physical_identity_confirmed":False,
            })
            continue
        try:
            a=evaluate_spatial_psf_shape(
                parsed,x=float(s["ztf_native_detector_xpos_pixels"]),
                y=float(s["ztf_native_detector_ypos_pixels"]))
            shape=psf_image_shape_diagnostics(a)
            delta_x=shape["second_moment_sigma_x_pixels"]
            delta_y=shape["second_moment_sigma_y_pixels"]
            out.append({
                "gaia_source_id":s["gaia_source_id"],
                "status":"ORIGINAL_SPATIAL_PSF_SHAPE_EVALUATED_MODEL_PROVISIONAL",
                "native_zft_psf_catalog_sourceid":
                    s["ztf_native_per_exposure_sourceid"],
                **shape,
                "local_source_psf_independently_calibrated":False,
                "gaia_ztf_physical_identity_confirmed":False,
            })
        except (ValueError,TypeError,OverflowError,KeyError) as exc:
            out.append({
                "gaia_source_id":s["gaia_source_id"],
                "status":"NATIVE_PSF_SOURCE_GEOMETRY_OR_MODEL_INVALID",
                "error_type":type(exc).__name__,
                "gaia_ztf_physical_identity_confirmed":False,
            })
    return {
        "status":"ORIGINAL_NATIVE_SPATIAL_DAOPHOT_MODEL_EVALUATION_ATTEMPTED",
        "native_daophot_sha256":parsed["source_sha256"],
        "n_evaluated_provisional_catalogue_candidate_psfs":sum(
            s["status"]=="ORIGINAL_SPATIAL_PSF_SHAPE_EVALUATED_MODEL_PROVISIONAL"
            for s in out),
        "model_center_validity":center_check["status"],
        "reconstructions":out,
        "n_independently_calibrated_source_psfs":0,
        "n_authenticated_gaia_ztf_source_identities":0,
    }
