"""v1.19: fixed-source empirical PSF from disjoint original ZTF star images.

Science-specific source images, masks, detector positions and source catalogue
records are transient. For each candidate Gaia source ID, a *new* 23x23
empirical PSF is trained only from other source IDs of the SAME exposure;
the excluded source has never contributed pixels to its training shape.
This is separate from the native spatial DAOPhot lookup arrays.

IMPORTANT: ZTF's own underlying PSFcat celestial positions and DAOPhot source
screen may have relied on the ORIGINAL instrument PSF training sample.
Membership is still unknown. This is a distinct-source template held-out test
INSIDE StellarForge, not external absolute PSF/WCS/photometric calibration.

Original ZTF sciimg DN are not absolutely flux calibrated. Background MAD
and any strictly metadata-backed electron/DN gain give only a provisional
variance proxy, not a full correlated noise or astrometric covariance.
"""
from __future__ import annotations

import hashlib
import math
from urllib.error import HTTPError,URLError
from typing import Any

import numpy as np
from scipy.ndimage import map_coordinates,shift

from .coordinates import validate_icrs
from .v113_official_masks_psf import (
    _one_image,BAD_MASK_BITS,MASK_ALIGN_TOLERANCE_PIX,
    official_ancillary_url,fetch_ancillary_fits,
)
from .v15_image_pixels import fetch_fits_cutout
from .v18_gaia_references import retarget_same_ztf_exposure
from .v115_spatial_psf import evaluate_spatial_psf_shape

FIT_RADIUS_PIX=9.
INNER_SKY_RADIUS_PIX=14.
OUTER_SKY_RADIUS_PIX=22.
PSF_RADIUS_PIX=11
SOURCE_CORE_RADIUS_PIX=10.0
MAX_NATIVE_SUBPIXEL_PHASE_DISAGREEMENT=.22
MIN_SKY_PIXEL_COUNT=230
MIN_SOURCE_MODEL_PIXELS=240
MAX_TRAINING_SOURCE_STARS=5
MIN_DISTINCT_TRAINING_STARS=3
MIN_DISTINCT_TOTAL_STARS=4
MIN_EMPIRICAL_SOURCE_SNR_PROXY=10.
SCHEMA="v119_disjoint_source_leave_one_out_empirical_psf"
GAIN_KEY_CANDIDATES=("GAIN","CCDGAIN","EGAIN")
READNOISE_KEY_CANDIDATES=("RDNOISE","READNOIS","RON")


def header_noise_metadata(hdr:Any,*,sky_mad_dn:float)->dict:
    """Do not invent gain/read noise; record available header-only proxies.

    Sky MAD already includes instrument sky/read-noise fluctuations, so a
    documented detector gain can add only the estimated *source* Poisson
    shot-noise component. Pixel covariance, sky model and gain uncertainties
    are unknown. This cannot be called a calibrated chi-square.
    """
    if not math.isfinite(sky_mad_dn) or sky_mad_dn<=0:
        raise ValueError("Invalid annular noise proxy")
    out={
        "background_sky_mad_proxy_dn":round(sky_mad_dn,6),
        "gain_read_directly_from_original_fits_header":False,
        "read_noise_read_directly_from_original_fits_header":False,
        "calibrated_per_pixel_noise_covariance_available":False,
        "full_detector_noise_calibration_completed":False,
    }
    gain=None
    for key in GAIN_KEY_CANDIDATES:
        if key in hdr:
            try:v=float(hdr[key])
            except (TypeError,ValueError,OverflowError):continue
            if math.isfinite(v) and 0.2<=v<=20.0:
                gain=v;out["source_gain_header_keyword"]=key
                break
    if gain is not None:
        out["gain_read_directly_from_original_fits_header"]=True
        out["gain_electrons_per_dn_metadata"]=round(gain,6)
    for key in READNOISE_KEY_CANDIDATES:
        if key in hdr:
            try:v=float(hdr[key])
            except (TypeError,ValueError,OverflowError):continue
            if math.isfinite(v) and 0<=v<=50:
                out["read_noise_read_directly_from_original_fits_header"]=True
                out["read_noise_electrons_header_metadata"]=round(v,6)
                out["read_noise_header_keyword"]=key
                break
    return out


def _clip_sky_plane(data:np.ndarray,mask:np.ndarray,xx:np.ndarray,yy:np.ndarray,
                    radius:np.ndarray)->tuple[np.ndarray,float,int]:
    good=(np.isfinite(data)&~mask&(radius>=INNER_SKY_RADIUS_PIX)
          &(radius<=OUTER_SKY_RADIUS_PIX))
    if int(good.sum())<MIN_SKY_PIXEL_COUNT:
        raise ValueError("INSUFFICIENT_BACKGROUND_OR_MASKED_SKY")
    val=np.asarray(data[good],dtype=float)
    x=np.asarray(xx[good],dtype=float)
    y=np.asarray(yy[good],dtype=float)
    for _ in range(3):
        b=float(np.median(val))
        sigma=float(1.4826*np.median(np.abs(val-b)))
        if not math.isfinite(sigma) or sigma<=1e-8:
            raise ValueError("DEGENERATE_SKY_MAD")
        keep=np.abs(val-b)<=4*sigma
        if int(keep.sum())<MIN_SKY_PIXEL_COUNT:
            raise ValueError("SKY_CLIPPING_REMOVED_REQUIRED_PIXELS")
        val,x,y=val[keep],x[keep],y[keep]
    x0=float(xx.mean());y0=float(yy.mean())
    basis=np.column_stack((np.ones(len(val)),x-x0,y-y0))
    c,_,rank,_=np.linalg.lstsq(basis,val,rcond=None)
    if rank!=3 or not np.isfinite(c).all():
        raise ValueError("ILL_CONDITIONED_SKY_PLANE")
    res=val-basis@c
    noise=float(1.4826*np.median(np.abs(res-np.median(res))))
    if not 1e-8<noise<1e9:
        raise ValueError("NONFINITE_SKY_RESIDUAL_MAD")
    model=c[0]+c[1]*(xx-x0)+c[2]*(yy-y0)
    return model,noise,len(val)


def extract_original_source_stamp(
    raw_science:bytes,raw_mask:bytes, *,
    source_ra:float,source_dec:float,native_x:float,native_y:float,
    gaia_source_id:str,min_source_snr_proxy:float=MIN_EMPIRICAL_SOURCE_SNR_PROXY)->dict:
    """Read/mask source image; estimate sky from non-source pixels only.

    Align source by WCS native subpixel phase; sample a 23x23 stamp. For the
    empirical PSF *training* image, pixel phase is removed in memory by
    cubic interpolation, so measured template is centered in one output
    grid. Masks are enforced on the original fit radius before resampling.
    """
    if not str(gaia_source_id).isdigit():
        raise ValueError("Invalid preregistered Gaia candidate ID")
    validate_icrs(source_ra,source_dec)
    if not (math.isfinite(min_source_snr_proxy)
            and 2<=min_source_snr_proxy<=MIN_EMPIRICAL_SOURCE_SNR_PROXY):
        raise ValueError("Unsupported preregistered source SNR tier")
    if not (isinstance(raw_science,bytes) and isinstance(raw_mask,bytes)):
        raise ValueError("Actual original source science/mask FITS required")
    data,hdr,wcs=_one_image(raw_science)
    masks,mhdr,mwcs=_one_image(raw_mask)
    if data.shape!=masks.shape or min(data.shape)<54:
        raise ValueError("ORIGINAL_SCIENCE_MASK_DIMENSION_MISMATCH")
    if not (wcs.has_celestial and mwcs.has_celestial
            and wcs.pixel_n_dim==2 and mwcs.pixel_n_dim==2
            and wcs.world_n_dim==2 and mwcs.world_n_dim==2):
        raise ValueError("ORIGINAL_SCIENCE_MASK_WCS_MISSING")
    h,w=data.shape
    errs=[]
    for xp,yp in ((1.,1.),(w/2,h/2),(w-2.,h-2.)):
        ra,dec=wcs.pixel_to_world_values(xp,yp)
        mx,my=mwcs.world_to_pixel_values(ra,dec)
        errs.append(math.hypot(float(mx)-xp,float(my)-yp))
    if not all(math.isfinite(v) for v in errs) or max(errs)>MASK_ALIGN_TOLERANCE_PIX:
        raise ValueError("ORIGINAL_SCIENCE_MASK_WCS_MISREGISTERED")
    px,py=map(float,wcs.world_to_pixel_values(source_ra,source_dec))
    if not all(math.isfinite(v) for v in (px,py,native_x,native_y)):
        raise ValueError("SOURCE_POSITION_NOT_FINITE")
    if not 24<=px<w-24 or not 24<=py<h-24:
        raise ValueError("INSUFFICIENT_SKY_STAMP_CUTOUT")
    ix=int(round(px));iy=int(round(py))
    fx=px-ix;fy=py-iy
    nx=float(native_x)-round(float(native_x))
    ny=float(native_y)-round(float(native_y))
    phase_error=max(abs(((fx-nx+.5)%1)-.5),abs(((fy-ny+.5)%1)-.5))
    if phase_error>MAX_NATIVE_SUBPIXEL_PHASE_DISAGREEMENT:
        raise ValueError("NATIVE_PSF_CATALOGUE_WCS_PHASE_CONFLICT")
    vals=np.asarray(masks,dtype=float)
    if (not np.isfinite(vals).all() or np.any(vals<0) or np.any(vals>65535)
        or not np.all(vals==np.floor(vals))):
        raise ValueError("INVALID_ORIGINAL_MASK_BIT_VALUES")
    bad=((vals.astype(np.uint16)&BAD_MASK_BITS)!=0)
    yy,xx=np.indices(data.shape,dtype=float)
    radius=np.hypot(xx-px,yy-py)
    # Strict source training policy: full radius 10 pixels must be clean.
    source_core=radius<=SOURCE_CORE_RADIUS_PIX
    if np.any(source_core & (bad|~np.isfinite(data))):
        raise ValueError("ORIGINAL_SOURCE_HAS_MASKED_OR_NONFINITE_CORE_PIXELS")
    sky_plane,sky_sigma,n_sky=_clip_sky_plane(
        np.asarray(data,dtype=float),bad,xx,yy,radius)
    r=PSF_RADIUS_PIX
    stamp=np.asarray(data[iy-r:iy+r+1,ix-r:ix+r+1],dtype=float)
    sky=np.asarray(sky_plane[iy-r:iy+r+1,ix-r:ix+r+1],dtype=float)
    stampr=np.hypot(*np.mgrid[-r:r+1,-r:r+1])
    if stamp.shape!=(23,23):
        raise ValueError("NONSTANDARD_SOURCE_STAMP")
    support=stampr<=FIT_RADIUS_PIX
    if not np.isfinite(stamp[support]).all():
        raise ValueError("SOURCE_PIXEL_STAMP_NONFINITE")
    source=stamp-sky
    # Aperture-sum SNR is a *proxy*, not a true inverse variance flux error.
    amplitude=float(np.sum(source[support]))
    proxy=amplitude/(sky_sigma*math.sqrt(int(support.sum())))
    if not (math.isfinite(proxy) and proxy>=min_source_snr_proxy
            and amplitude>0):
        raise ValueError("SOURCE_TOO_WEAK_FOR_EMPIRICAL_PSF_TEMPLATE")
    # Shift original image sampling so source centroid lies at 11,11.
    # Keep both *unshifted* DN data and centered positive-truncated shape;
    # only the latter participates in empirical PSF training.
    grid_y,grid_x=np.indices((23,23),dtype=float)
    samp=np.vstack([(grid_y+fy).ravel(),(grid_x+fx).ravel()])
    aligned=map_coordinates(source,samp,order=3,mode="constant",cval=0).reshape(23,23)
    ylocal,xlocal=np.mgrid[-r:r+1,-r:r+1]
    fitregion=np.hypot(xlocal,ylocal)<=FIT_RADIUS_PIX
    centered=np.where(fitregion,np.clip(aligned,0,None),0.)
    total=float(centered.sum())
    if not math.isfinite(total) or total<=1e-8:
        raise ValueError("EMPTY_EMPIRICAL_SOURCE_TEMPLATE")
    centered=centered/total
    return {
        "gaia_source_id":str(gaia_source_id),
        "science_fits_sha256":hashlib.sha256(raw_science).hexdigest(),
        "mask_fits_sha256":hashlib.sha256(raw_mask).hexdigest(),
        "detector_native_x":float(native_x),
        "detector_native_y":float(native_y),
        "source_pixel_frac_x":fx,"source_pixel_frac_y":fy,
        "science_stamp_dn":stamp, # EPHEMERAL only, never exported.
        "science_stamp_sky_model_dn":sky, # EPHEMERAL only.
        "aligned_empirical_shape":centered, # EPHEMERAL only.
        "sky_sigma_mad_proxy_dn":sky_sigma,
        "n_original_sky_pixels":n_sky,
        "source_snr_proxy":proxy,
        "minimum_source_snr_proxy_tier":min_source_snr_proxy,
        "model_noise_metadata":header_noise_metadata(hdr,sky_mad_dn=sky_sigma),
        "n_unmasked_fit_pixels":int(support.sum()),
        "original_source_n_native_mask_bad_core_pixels":0,
        "original_source_detector_fits_verified":True,
        "physical_gaia_ztf_identity_authenticated":False,
    }


def fetch_original_source_stamp(
    science_url:str, *,
    source_ra:float,source_dec:float,native_x:float,native_y:float,
    gaia_source_id:str,timeout:float=6,
    min_source_snr_proxy:float=MIN_EMPIRICAL_SOURCE_SNR_PROXY,
    fetch_mask=fetch_ancillary_fits,
    fetch_science=fetch_fits_cutout)->dict:
    """One exact-date science/mask pair, never model/source pixels in output."""
    try:
        src=retarget_same_ztf_exposure(
            science_url,source_ra,source_dec,size_arcsec=60)
        msk=official_ancillary_url(src,"mskimg.fits")
        raw_m=fetch_mask(msk,kind="mskimg.fits",timeout=timeout)
        raw_s=fetch_science(src,timeout=timeout)
        return extract_original_source_stamp(
            raw_s,raw_m,source_ra=source_ra,source_dec=source_dec,
            native_x=native_x,native_y=native_y,
            gaia_source_id=gaia_source_id,
            min_source_snr_proxy=min_source_snr_proxy)
    except (HTTPError,URLError,TimeoutError,OSError,ValueError) as exc:
        d={"status":"ORIGINAL_IMAGE_MASK_OR_EMPIRICAL_TRAINING_INELIGIBLE",
           "gaia_source_id":str(gaia_source_id),
           "error_type":type(exc).__name__,
           "error_code":str(exc)[:110] if isinstance(exc,ValueError) else None,
           "physical_gaia_ztf_identity_authenticated":False}
        if isinstance(exc,HTTPError):d["http_status"]=int(exc.code)
        return d


def _fixed_shape_fit_rms(stamp:dict, shape:np.ndarray)->dict:
    """Fit source amplitude+sky on same holdout star, evaluate other pixels.

    This is a *different SOURCE ID withheld from PSF SHAPE estimation*;
    nuisance amplitude/sky solved on half its pixels as before. Neither
    shape fitting nor source selection may include the holdout's pixels.
    """
    if shape.shape!=(23,23) or not np.isfinite(shape).all():
        raise ValueError("Malformed held-out PSF model array")
    if not (abs(float(shape.sum())-1)<.001 and np.min(shape)>=0):
        raise ValueError("PSF model must be nonnegative unit sum")
    y,x=np.mgrid[-11:12,-11:12]
    use=np.hypot(x,y)<=FIT_RADIUS_PIX
    tr=use&(((x+y)%2)==0)
    ho=use&~tr
    if min(int(tr.sum()),int(ho.sum()))<100:
        raise ValueError("Too few original source residual pixels")
    d=stamp["science_stamp_dn"]
    model=np.asarray(shape,dtype=float)
    B=np.column_stack([model[tr],np.ones(int(tr.sum())),x[tr],y[tr]])
    solution,_,rank,_=np.linalg.lstsq(B,d[tr],rcond=None)
    if rank!=4 or not np.isfinite(solution).all() or float(solution[0])<=0:
        raise ValueError("Held-out source amplitude/sky model failed")
    predicted=solution[0]*model+solution[1]+solution[2]*x+solution[3]*y
    resid=np.asarray((d-predicted)[ho],dtype=float)
    raw_rms=math.sqrt(float(np.mean(resid**2)))
    sky_sigma=stamp["sky_sigma_mad_proxy_dn"]
    # Optional header-confirmed detector gain only, no invented gain.
    meta=stamp["model_noise_metadata"]
    gain=meta.get("gain_electrons_per_dn_metadata")
    # Added source shot noise is positive DN/gain; sky MAD already includes
    # sky/read noise. Not a full correlated detector covariance.
    if gain is None:
        proxy_var=np.full(int(ho.sum()),sky_sigma**2,dtype=float)
    else:
        proxy_var=sky_sigma**2+np.clip(
            solution[0]*model[ho],0,None)/float(gain)
    if not np.isfinite(proxy_var).all() or np.any(proxy_var<=0):
        raise ValueError("Impossible variance proxy")
    return {
        "same_heldout_source_image_checkerboard_rms_dn":round(raw_rms,6),
        "same_heldout_source_image_rms_over_annulus_mad":
            round(raw_rms/sky_sigma,6),
        "same_heldout_source_image_rms_over_metadata_proxy":
            round(math.sqrt(float(np.mean(resid**2/proxy_var))),6),
        "n_same_source_heldout_pixel_scores":int(ho.sum()),
        "header_gain_applied_to_optional_source_shot_noise":gain is not None,
        "nuisance_flux_amplitude_dn":round(float(solution[0]),5),
        "same_heldout_source_training_pixels_not_used_for_psf_shape":True,
        "calibrated_chi_square_or_false_companion_significance":False,
    }


def empirical_psf_leave_one_source_out(
    stamps:list[dict], *,
    native_spatial_psf:dict|None=None,
    min_training_stars:int=MIN_DISTINCT_TRAINING_STARS)->dict:
    """Cross-validate PSF *shape*, not native pipeline PSF or source identity.

    Require at least 4 distinct Gaia candidate IDs, all from the SAME
    original exposure; our caller guarantees exposure provenance. Per fold,
    the held-out source ID's image pixels NEVER enter median training PSF.
    """
    if not MIN_DISTINCT_TRAINING_STARS<=min_training_stars<=5:
        raise ValueError("Unsafe/unsupported PSF-training star budget")
    if len(stamps)>MAX_TRAINING_SOURCE_STARS+1:
        raise ValueError("Unbounded source image collection")
    valid=[x for x in stamps if x.get("original_source_detector_fits_verified")]
    ids=[str(x["gaia_source_id"]) for x in valid]
    if len(ids)!=len(set(ids)):
        raise ValueError("A star/source ID cannot appear twice within one epoch")
    if any(x.get("gaia_source_id") is None for x in stamps):
        raise ValueError("All source records require Gaia IDs")
    if len(valid)<max(MIN_DISTINCT_TOTAL_STARS,min_training_stars+1):
        return {
            "status":"INSUFFICIENT_DISTINCT_REAL_SOURCE_STARS_FOR_LOOCV",
            "n_distinct_eligible_source_stars":len(valid),
            "n_source_disjoint_psf_validation_folds":0,
            "n_source_disjoint_training_models":0,
            "zero_original_psf_training_star_membership_verified":True,
            "independent_instrument_psf_error_calibration_completed":False,
            "heldout_source_folds":[],
        }
    folds=[]
    valid=sorted(valid,key=lambda x:str(x["gaia_source_id"]))
    for holdout in valid:
        training=[s for s in valid if s["gaia_source_id"]!=holdout["gaia_source_id"]]
        training=training[:MAX_TRAINING_SOURCE_STARS]
        if len(training)<min_training_stars:
            raise ValueError("Incomplete distinct-source PSF model training")
        # Shape here is built exclusively from other original star-pixel
        # stamps and has no DAOPhot model correction coefficients.
        psf=np.median(np.stack([x["aligned_empirical_shape"] for x in training]),axis=0)
        psf=np.clip(psf,0,None)
        total=float(psf.sum())
        if not math.isfinite(total) or total<=0:
            raise ValueError("Empirical distinct-source median PSF unusable")
        psf/=total
        fx=float(holdout["source_pixel_frac_x"])
        fy=float(holdout["source_pixel_frac_y"])
        # Map common, aligned empirical shape back to withheld ORIGINAL pixel
        # center phase; keep same subpixel interpolation for each fold.
        empirical=shift(psf,shift=(fy,fx),order=3,
                        mode="constant",cval=0,prefilter=True)
        empirical=np.maximum(empirical,0.)
        empirical/=empirical.sum()
        result=_fixed_shape_fit_rms(holdout,empirical)
        fold={
            "heldout_new_gaia_candidate_source_id":holdout["gaia_source_id"],
            "n_distinct_other_star_training_sources":len(training),
            "training_source_ids":[x["gaia_source_id"] for x in training],
            "psf_pixels_built_without_heldout_source":True,
            "empirical_model_type":"MEDIAN_OF_OTHER_ALIGNED_ORIGINAL_STAR_IMAGE_SHAPES",
            "empirical_holdout_source_metrics":result,
            "native_original_ztf_psf_training_star_membership_known":False,
            "physical_gaia_ztf_identity_authenticated":False,
        }
        if native_spatial_psf is not None:
            native=evaluate_spatial_psf_shape(
                native_spatial_psf,x=float(holdout["detector_native_x"]),
                y=float(holdout["detector_native_y"]),
                frac_x=fx,frac_y=fy)
            original=_fixed_shape_fit_rms(holdout,native)
            fold["native_spatial_daophot_holdout_source_metrics"]=original
            re=result["same_heldout_source_image_rms_over_annulus_mad"]
            rn=original["same_heldout_source_image_rms_over_annulus_mad"]
            fold["empirical_to_native_holdout_rms_ratio"]=round(re/rn,6)
            fold["empirical_low_rms_not_physical_detection"]=re<rn
        folds.append(fold)
    ratios=[f["empirical_holdout_source_metrics"][
        "same_heldout_source_image_rms_over_annulus_mad"] for f in folds]
    comparison=[f["empirical_to_native_holdout_rms_ratio"] for f in folds
                if "empirical_to_native_holdout_rms_ratio" in f]
    return {
        "status":"ORIGINAL_ZTF_DISTINCT_SOURCE_PSF_SHAPE_LOOCV_COMPLETED",
        "n_distinct_eligible_source_stars":len(valid),
        "n_source_disjoint_psf_validation_folds":len(folds),
        "n_source_disjoint_training_models":len(folds),
        "median_empirical_holdout_source_rms_over_sky_mad":
            round(float(np.median(ratios)),6),
        "median_empirical_to_native_source_rms_ratio":
            round(float(np.median(comparison)),6) if comparison else None,
        "n_empirical_template_lower_residual_than_native_original_psf":
            sum(f.get("empirical_low_rms_not_physical_detection",False) for f in folds),
        "heldout_source_folds":folds,
        "original_ZTF_DAOPhot_training_star_membership_authenticated":False,
        "source_positions_inherited_from_native_ZTF_psfcat":True,
        "real_original_distinct_star_pixel_template_trained_without_holdout":True,
        "calibrated_instrument_astrometric_PSF_noise_error_model_completed":False,
        "new_physical_gaia_ztf_companion_or_variability_confirmed":False,
    }


def evaluate_other_star_empirical_psf(
    training_stamps:list[dict],heldout_stamps:list[dict], *,
    native_spatial_psf:dict,
    min_training_source_ids:int=MIN_DISTINCT_TRAINING_STARS)->dict:
    """Train once on bright prior reference stars, test NEW Gaia source IDs.

    Quality tiers are *distinct*: training requires SNR proxy >=10 and all
    source stamps mask/WCS clean; heldout previously unseen source IDs may
    have SNR proxy >=2.5 (they are NOT included in constructing the template).
    The originally preselected Gaia holdouts stay distinct, and source
    training/heldout IDs must not overlap. No DAOPhot coefficients contribute
    to empirically learned shape.
    """
    if not 3<=min_training_source_ids<=5:
        raise ValueError("Invalid number of disjoint training references")
    if len(training_stamps)>8 or len(heldout_stamps)>8:
        raise ValueError("Unbounded original star-sample pairing")
    tr=[x for x in training_stamps if x.get("original_source_detector_fits_verified")]
    te=[x for x in heldout_stamps if x.get("original_source_detector_fits_verified")]
    ids=[str(x["gaia_source_id"]) for x in tr]
    withheld=[str(x["gaia_source_id"]) for x in te]
    if len(set(ids))!=len(ids) or len(set(withheld))!=len(withheld):
        raise ValueError("Duplicate Gaia ID used across exposure source stamps")
    if set(ids)&set(withheld):
        raise ValueError("Heldout Gaia source ID leaks into training stars")
    if any(x["source_snr_proxy"]<MIN_EMPIRICAL_SOURCE_SNR_PROXY for x in tr):
        raise ValueError("Too-low-SNR reference star incorrectly entered training set")
    if len(tr)<min_training_source_ids or not te:
        return {
            "status":"INSUFFICIENT_REAL_BRIGHT_TRAINING_OR_NEW_HELDOUT_STARS",
            "n_bright_distinct_reference_training_stars":len(tr),
            "n_new_source_disjoint_heldout_stars":len(te),
            "n_new_source_disjoint_heldout_models_evaluated":0,
            "new_gaia_source_holdout_science_identity_verified":False,
            "original_psf_training_star_membership_authenticated":False,
            "evaluation_records":[],
        }
    tr=sorted(tr,key=lambda x:str(x["gaia_source_id"]))[:5]
    te=sorted(te,key=lambda x:str(x["gaia_source_id"]))
    psf=np.median(np.stack([x["aligned_empirical_shape"] for x in tr]),axis=0)
    psf=np.clip(psf,0,None)
    if not np.isfinite(psf).all() or psf.sum()<=0:
        raise ValueError("Training reference empirical PSF invalid")
    psf/=psf.sum()
    folds=[]
    for h in te:
        # Source phase is from original per-exposure ZTF source catalogue.
        empirical=shift(psf,shift=(
            float(h["source_pixel_frac_y"]),float(h["source_pixel_frac_x"])),
            order=3,mode="constant",cval=0,prefilter=True)
        empirical=np.clip(empirical,0,None)
        if not 0<empirical.sum():
            raise ValueError("Empirical PSF shifted off heldout pixel footprint")
        empirical/=empirical.sum()
        a=_fixed_shape_fit_rms(h,empirical)
        native=evaluate_spatial_psf_shape(
            native_spatial_psf,x=h["detector_native_x"],
            y=h["detector_native_y"],
            frac_x=h["source_pixel_frac_x"],
            frac_y=h["source_pixel_frac_y"])
        b=_fixed_shape_fit_rms(h,native)
        denom=b["same_heldout_source_image_rms_over_annulus_mad"]
        folds.append({
            "new_heldout_gaia_candidate_id":h["gaia_source_id"],
            "training_bright_prior_gaia_reference_ids":[s["gaia_source_id"] for s in tr],
            "n_bright_distinct_training_reference_stars":len(tr),
            "heldout_new_gaia_source_pixels_absent_from_template_training":True,
            "empirical_psf_original_star_pixels_not_native_DAOPhot_coefficients":True,
            "heldout_gaia_source_snr_proxy":round(float(h["source_snr_proxy"]),5),
            "empirical_heldout_source_metrics":a,
            "native_DAOPhot_heldout_source_metrics":b,
            "empirical_to_native_heldout_rms_ratio":round(
                a["same_heldout_source_image_rms_over_annulus_mad"]/denom,6),
            "physical_gaia_ztf_source_identity_confirmed":False,
        })
    ratios=[r["empirical_to_native_heldout_rms_ratio"] for r in folds]
    return {
        "status":"NEW_GAIA_SOURCE_DISJOINT_EMPIRICAL_PSF_TEST_COMPLETED",
        "n_bright_distinct_reference_training_stars":len(tr),
        "n_new_source_disjoint_heldout_stars":len(te),
        "n_new_source_disjoint_heldout_models_evaluated":len(folds),
        "median_empirical_to_native_heldout_rms_ratio":
            round(float(np.median(ratios)),6),
        "n_new_star_holdouts_better_empirical_than_native":sum(v<1 for v in ratios),
        "evaluation_records":folds,
        "separate_Gaia_source_IDs_used_for_training_vs_test":True,
        "original_ZTF_pipeline_DAOPhot_training_star_membership_known":False,
        "independent_physical_source_identity_WCS_PSF_calibration_completed":False,
    }
