"""v1.13 official ZTF bad-pixel mask and native PSF product quality gates.

The IRSA ZTF science exposure has matching ancillary "_mskimg.fits" bitmasks
and "_sciimgdaopsfcent.fits" *field-center* PSF stamps. These are archival
instrument products, NOT source-specific empirical PSF calibrations. The mask
and science cutouts must have the same shape, celestial WCS, and checked
world/pixel geometry before science pixels can be flagged safely.

Only bounded official IRSA HTTPS URLs and <3MB memory buffers are processed.
No raw original pixels, raw catalogue data, or original FITS headers leave the
runner. ZTF mask disqualifying bits follow the ZTF ZSDS supplement: 6141
(deleterious bits 0,2..10,12); bit 1 and bit 11 identify extracted sources.
"""
from __future__ import annotations

import hashlib
import io
import math
from urllib.error import HTTPError,URLError
from urllib.parse import parse_qs,urlparse,urlunparse
from urllib.request import Request,urlopen

from .v15_image_pixels import _validate_official_cutout, MAX_FITS_BYTES

BAD_MASK_BITS=6141
MASK_SOURCE_BITS=(1<<1)|(1<<11)
SATURATION_BIT=(1<<8)
MAX_MASKED_PIXEL_FRACTION=0.01
MAX_PSF_BYTES=3_000_000
VALID_PRODUCT_SUFFIXES=("mskimg.fits","sciimgdaopsfcent.fits")
MASK_ALIGN_TOLERANCE_PIX=0.05


def official_ancillary_url(science_url:str,product:str)->str:
    """Keep exact dated official science exposure, never arbitrary URLs."""
    _validate_official_cutout(science_url)
    parsed=urlparse(science_url)
    if not parsed.path.endswith("_sciimg.fits"):
        raise ValueError("Need the original dated ZTF sciimg product")
    if not parsed.path.startswith("/ibe/data/ztf/products/sci/"):
        raise ValueError("Original science exposure only")
    if product not in VALID_PRODUCT_SUFFIXES:
        raise ValueError("Unsupported ZTF ancillary product")
    suffix=("_"+product)
    path=parsed.path.removesuffix("_sciimg.fits")+suffix
    if product=="mskimg.fits":
        return urlunparse(parsed._replace(path=path))
    # The native science-frame-center PSF stamp is a different spatial
    # product: do NOT request a star-position cutout or claim it is local.
    return urlunparse(parsed._replace(path=path,query="",fragment=""))


def validate_ancillary_url(url:str,kind:str)->None:
    if kind not in VALID_PRODUCT_SUFFIXES:
        raise ValueError("Unsupported ancillary product")
    x=urlparse(url)
    if (x.scheme!="https" or x.hostname!="irsa.ipac.caltech.edu"
        or x.username is not None or x.password is not None
        or x.port not in (None,443) or x.fragment
        or not x.path.startswith("/ibe/data/ztf/products/sci/")
        or not x.path.endswith("_"+kind)):
        raise ValueError("Not a supported official dated ZTF ancillary product")
    if kind=="mskimg.fits":
        # Reuse hardened first-party sciimg cutout validator for the
        # identical spatial center, size and HTTPS host restrictions.
        sci=urlunparse(x._replace(
            path=x.path.removesuffix("_mskimg.fits")+"_sciimg.fits"))
        _validate_official_cutout(sci)
    elif x.query:
        raise ValueError("Field-center PSF stamp must not use cutout params")


def fetch_ancillary_fits(url:str,*,kind:str,timeout:float=7,opener=urlopen)->bytes:
    validate_ancillary_url(url,kind)
    if not math.isfinite(timeout) or not 1<=timeout<=25:
        raise ValueError("Unsafe request time budget")
    req=Request(url,headers={
        "User-Agent":"StellarForge/1.13 official ZTF ancillary scientific QA",
        "Accept":"application/fits,application/octet-stream",
    })
    with opener(req,timeout=timeout) as response:
        b=response.read(MAX_PSF_BYTES+1)
    if len(b)>MAX_PSF_BYTES or len(b)<2880:
        raise ValueError("Missing or oversized FITS image payload")
    if not (b.startswith(b"SIMPLE  =") or b.startswith(b"XTENSION")):
        raise ValueError("Ancillary response is not a FITS image")
    return b


def _one_image(raw:bytes):
    import numpy as np
    from astropy.io import fits
    from astropy.wcs import WCS
    if not isinstance(raw,bytes) or not 2880<=len(raw)<=MAX_FITS_BYTES:
        raise ValueError("Invalid FITS image payload")
    with fits.open(io.BytesIO(raw),memmap=False) as hdul:
        images=[h for h in hdul if getattr(h,"data",None) is not None
                and getattr(h.data,"ndim",None)==2]
        if len(images)!=1:
            raise ValueError("Need one unambiguous 2D FITS image")
        hdu=images[0]
        data=np.asarray(hdu.data)
        hdr=hdu.header.copy()
    if min(data.shape)<5 or max(data.shape)>400:
        raise ValueError("Unexpected FITS cutout/stamp dimensions")
    return data,hdr,WCS(hdr)


def inspect_mask_against_science(science_raw:bytes,mask_raw:bytes,*,
                                 expected_ra_deg:float,
                                 expected_dec_deg:float)->dict:
    """Check WCS alignment before identifying mask bits in a source aperture.

    Count archival ZTF bits. Zero BAD bits is NOT proof of an isolated single
    stellar source, because bit masks and native PSF may omit blending.
    """
    import numpy as np
    from .coordinates import validate_icrs
    validate_icrs(expected_ra_deg,expected_dec_deg)
    img,ih,iwcs=_one_image(science_raw)
    mask,mh,mwcs=_one_image(mask_raw)
    result={
        "mask_sha256":hashlib.sha256(mask_raw).hexdigest(),
        "science_sha256":hashlib.sha256(science_raw).hexdigest(),
        "mask_good_core_cannot_authenticate_source":True,
        "gaia_ztf_physical_identity_confirmed":False,
        "instrument_wcs_uncertainty_calibrated":False,
        "native_local_psf_validated":False,
    }
    if img.shape!=mask.shape:
        return {**result,"status":"MASK_IMAGE_SHAPE_MISMATCH",
                "science_shape":list(map(int,img.shape)),
                "mask_shape":list(map(int,mask.shape))}
    if not (iwcs.has_celestial and mwcs.has_celestial
            and iwcs.pixel_n_dim==2 and mwcs.pixel_n_dim==2
            and iwcs.world_n_dim==2 and mwcs.world_n_dim==2):
        return {**result,"status":"MASK_SCIENCE_CELESTIAL_WCS_MISSING"}
    h,w=img.shape
    sample=[(.5,.5),(w/2,h/2),(w-1.5,h-1.5)]
    try:
        err=[]
        for xp,yp in sample:
            ra,dec=iwcs.pixel_to_world_values(xp,yp)
            mx,my=mwcs.world_to_pixel_values(ra,dec)
            err.append(math.hypot(float(mx)-xp,float(my)-yp))
        if not all(math.isfinite(x) for x in err):
            raise ValueError("Nonfinite mask WCS alignment")
        px,py=map(float,iwcs.world_to_pixel_values(
            expected_ra_deg,expected_dec_deg))
    except (ValueError,TypeError,ArithmeticError) as exc:
        return {**result,"status":"MASK_SCIENCE_WCS_MAPPING_FAILED",
                "exception_type":type(exc).__name__}
    offset=max(err)
    if offset>MASK_ALIGN_TOLERANCE_PIX:
        return {**result,"status":"MASK_SCIENCE_WCS_GRID_MISMATCH",
                "worst_grid_offset_pixels":round(offset,6)}
    if not(5<=px<w-5 and 5<=py<h-5):
        return {**result,"status":"MASK_SOURCE_APERTURE_OUTSIDE_VALID_IMAGE"}
    # FITS product's bit mask may be signed raw data or floating depending on
    # transport; fail closed instead of coercing fractions or negative values.
    try:
        arr=np.asarray(mask,dtype=np.float64)
    except (ValueError,TypeError,OverflowError):
        return {**result,"status":"MASK_VALUE_TYPE_NOT_SUPPORTED"}
    if (not np.isfinite(arr).all() or np.any(arr<0)
            or np.any(arr>65535) or np.any(arr!=np.floor(arr))):
        return {**result,"status":"MASK_VALUES_INVALID_FOR_ZTF_BIT_DEFINITIONS"}
    bmask=arr.astype(np.uint16)
    yy,xx=np.indices(img.shape,dtype=float)
    radius=np.hypot(xx-px,yy-py)
    core=radius<=4.5
    annulus=(radius>=9)&(radius<=15)
    ncore=int(core.sum())
    nann=int(annulus.sum())
    if ncore<40 or nann<75:
        return {**result,"status":"MASK_APERTURE_OR_SKY_ANNULUS_INSUFFICIENT"}
    core_bad=(bmask[core]&BAD_MASK_BITS)!=0
    ann_bad=(bmask[annulus]&BAD_MASK_BITS)!=0
    bad_count=int(core_bad.sum())
    sat_count=int(((bmask[core]&SATURATION_BIT)!=0).sum())
    core_nan=int((~np.isfinite(img[core])).sum())
    bad_frac=bad_count/ncore
    status=("MASK_CORE_HAS_BAD_BITS_OR_NONFINITE_SCIENCE"
            if bad_count or core_nan else "MASK_CORE_NO_DISQUALIFYING_BITS_PROVISIONAL_ONLY")
    return {
        **result,"status":status,
        "wcs_checked_and_aligned":True,
        "mask_science_max_sample_grid_offset_pixels":round(offset,6),
        "mask_bad_bits_rule":BAD_MASK_BITS,
        "source_signal_bits_excluded_from_bad":MASK_SOURCE_BITS,
        "n_core_pixels":ncore,"n_core_bad_mask_pixels":bad_count,
        "n_core_saturated_mask_pixels":sat_count,
        "n_core_nonfinite_science_pixels":core_nan,
        "core_bad_mask_fraction":round(bad_frac,6),
        "n_annulus_pixels":nann,
        "n_annulus_bad_mask_pixels":int(ann_bad.sum()),
        "annulus_bad_mask_fraction":round(float(ann_bad.mean()),6),
        "has_wcs_aligned_mask":True,
        "has_unmasked_source_core_candidate":status.startswith("MASK_CORE_NO_"),
        "mask_proves_no_blending":False,
        "mask_proves_source_single":False,
    }


def inspect_native_center_psf(raw:bytes)->dict:
    """QA only the native field-center PSF *stamp* existence/shape.

    Native science-field center != model evaluated at an individual reference.
    Never infer a source-specific local PSF or instrument WCS calibration.
    """
    import numpy as np
    try:
        data,header,wcs=_one_image(raw)
    except (ValueError,TypeError,OSError) as exc:
        return {"status":"NATIVE_CENTER_PSF_FITS_INVALID",
                "error_type":type(exc).__name__,
                "source_specific_psf_calibrated":False}
    a=np.asarray(data,dtype=float)
    valid=np.isfinite(a)
    if min(a.shape)<7 or float(valid.mean())<.9:
        return {"status":"NATIVE_CENTER_PSF_INCOMPLETE",
                "source_specific_psf_calibrated":False}
    cleaned=np.where(valid,np.maximum(a,0),0)
    signal=float(cleaned.sum())
    if not math.isfinite(signal) or signal<=0 or float(cleaned.max())<=0:
        return {"status":"NATIVE_CENTER_PSF_NO_POSITIVE_SIGNAL",
                "source_specific_psf_calibrated":False}
    y,x=np.indices(a.shape,dtype=float)
    cx=float((x*cleaned).sum()/signal)
    cy=float((y*cleaned).sum()/signal)
    mxx=float((((x-cx)**2)*cleaned).sum()/signal)
    myy=float((((y-cy)**2)*cleaned).sum()/signal)
    if not all(math.isfinite(v) for v in (cx,cy,mxx,myy)):
        return {"status":"NATIVE_CENTER_PSF_MOMENTS_INVALID",
                "source_specific_psf_calibrated":False}
    return {
        "status":"NATIVE_CENTER_PSF_STAMP_PROVISIONALLY_PARSED",
        "fits_sha256":hashlib.sha256(raw).hexdigest(),
        "psf_shape_pixels":list(map(int,a.shape)),
        "finite_fraction":round(float(valid.mean()),5),
        "positive_weighted_x_centroid":round(cx,4),
        "positive_weighted_y_centroid":round(cy,4),
        "positive_weighted_sigma_x_pixels":round(math.sqrt(max(mxx,0)),4),
        "positive_weighted_sigma_y_pixels":round(math.sqrt(max(myy,0)),4),
        "psf_is_science_field_center_only":True,
        "psf_evaluated_at_source_position":False,
        "source_specific_psf_calibrated":False,
        "independent_astrometric_wcs_calibrated":False,
    }


def audit_one_science_source(science_url:str,*,source_ra_deg:float,
                            source_dec_deg:float,timeout:float=7,
                            fetch_science=None,fetch_other=None)->dict:
    """Retrieve official mask and science stamp with equal cutout geometry."""
    from .v18_gaia_references import retarget_same_ztf_exposure
    from .v15_image_pixels import fetch_fits_cutout
    # The URL is always derived from an exact historical science product.
    stamp_url=retarget_same_ztf_exposure(
        science_url,source_ra_deg,source_dec_deg,size_arcsec=45)
    mask_url=official_ancillary_url(stamp_url,"mskimg.fits")
    if fetch_science is None:fetch_science=fetch_fits_cutout
    if fetch_other is None:fetch_other=fetch_ancillary_fits
    report={"status":"MASK_AND_SCIENCE_NOT_BOTH_AVAILABLE",
            "scientific_source_identity_confirmed":False}
    try:
        rawmask=fetch_other(mask_url,kind="mskimg.fits",timeout=timeout)
        rawscience=fetch_science(stamp_url,timeout=timeout)
        screen=inspect_mask_against_science(
            rawscience,rawmask,expected_ra_deg=source_ra_deg,
            expected_dec_deg=source_dec_deg)
        report.update(screen)
    except (HTTPError,URLError,TimeoutError,OSError,ValueError) as exc:
        report["status"]="ORIGINAL_ZTF_MASK_OR_SCIENCE_UNAVAILABLE"
        report["error_type"]=type(exc).__name__
        if isinstance(exc,HTTPError):
            report["http_status"]=int(exc.code)
    return report


def audit_native_center_psf(science_url:str,*,timeout:float=7,
                            fetch_other=None)->dict:
    """Native official PSF center FITS, once per distinct dated exposure."""
    if fetch_other is None:fetch_other=fetch_ancillary_fits
    url=official_ancillary_url(science_url,"sciimgdaopsfcent.fits")
    try:
        raw=fetch_other(url,kind="sciimgdaopsfcent.fits",timeout=timeout)
        return inspect_native_center_psf(raw)
    except (HTTPError,URLError,TimeoutError,OSError,ValueError) as exc:
        result={"status":"NATIVE_CENTER_PSF_ACCESS_UNAVAILABLE",
                "error_type":type(exc).__name__,
                "source_specific_psf_calibrated":False}
        if isinstance(exc,HTTPError):result["http_status"]=int(exc.code)
        return result
