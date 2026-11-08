"""v1.14: official ZTF single-exposure PSF-fit catalogue crossmatch screening.

The native ZTF *_psfcat.fits table contains sourceid/xpos/ypos, RA/Dec,
flux/sigflux, SNR, PSF chi, PSF sharpness and mask-derived flags (ZSDS §10.6).
These are SOURCE CANDIDATES, not astrophysical Gaia/ZTF identifications.
A close match can be blended/unresolved, pipeline-selected, or spurious.

The separate *_sciimgdao.psf instrument product is DAOPhot spatially varying
PSF lookup-table data; this code only inspects its availability/provenance.
No source-position PSF evaluation, source identity, calibrated WCS or
individual CCD source error budget is claimed.

Only original same-dated official IRSA science products, bounded network
sizes, full FITS files read transiently in-memory. Aggregate derived QA only.
"""
from __future__ import annotations

import hashlib
import io
import math
from urllib.error import HTTPError,URLError
from urllib.parse import urlparse,urlunparse
from urllib.request import Request,urlopen

from .v15_image_pixels import _validate_official_cutout
from .coordinates import validate_icrs
from .v113_official_masks_psf import BAD_MASK_BITS

SUFFIXES=("psfcat.fits","sciimgdao.psf")
CATALOGUE_BYTES_MAX=48*1024*1024
SPATIAL_PSF_BYTES_MAX=4*1024*1024
MAX_CATALOGUE_ROWS=120_000
MAX_SOURCE_REQUESTS_PER_EXPOSURE=7
MAX_SEARCH_RADIUS_ARCSEC=5.
MATCH_RADIUS_ARCSEC=1.0
CROWDING_RADIUS_ARCSEC=3.0
REQUIRED_COLUMNS=(
    "sourceid","xpos","ypos","ra","dec","flux","sigflux",
    "mag","sigmag","snr","chi","sharp","flags",
)


def official_psf_product_url(science_url:str,kind:str)->str:
    """Derive original exposure's full native PSF catalog/DAO product URL."""
    _validate_official_cutout(science_url)
    if kind not in SUFFIXES:
        raise ValueError("Not an official permitted PSF auxiliary product")
    p=urlparse(science_url)
    if not p.path.startswith("/ibe/data/ztf/products/sci/") or not p.path.endswith("_sciimg.fits"):
        raise ValueError("Original dated ZTF science product required")
    return urlunparse(p._replace(
        path=p.path.removesuffix("_sciimg.fits")+"_"+kind,
        query="",fragment=""))


def validate_original_psf_url(url:str,kind:str)->None:
    if kind not in SUFFIXES:
        raise ValueError("Unexpected PSF product kind")
    u=urlparse(url)
    if (u.scheme!="https" or u.hostname!="irsa.ipac.caltech.edu"
        or u.username is not None or u.password is not None or u.port not in (None,443)
        or u.query or u.fragment
        or not u.path.startswith("/ibe/data/ztf/products/sci/")
        or not u.path.endswith("_"+kind)):
        raise ValueError("Unsafe/nonofficial ZTF ancillary PSF URL")
    base=urlunparse(u._replace(
        path=u.path.removesuffix("_"+kind)+"_sciimg.fits",
        query="center=65.91332400%2C24.93719500&size=45arcsec&gzip=false"))
    _validate_official_cutout(base)


def fetch_native_psf_product(url:str,*,kind:str,timeout:float=12,opener=urlopen)->bytes:
    validate_original_psf_url(url,kind)
    if not math.isfinite(timeout) or not 1<=timeout<=25:
        raise ValueError("Bad network timeout")
    cap=CATALOGUE_BYTES_MAX if kind=="psfcat.fits" else SPATIAL_PSF_BYTES_MAX
    req=Request(url,headers={
        "User-Agent":"StellarForge/1.14 official ZTF native PSF catalog QA",
        "Accept":"application/fits,application/octet-stream",
    })
    with opener(req,timeout=timeout) as reply:
        # A redirect to an unrelated host must never leak this workflow's data.
        final=getattr(reply,"geturl",lambda:url)()
        validate_original_psf_url(final,kind)
        raw=reply.read(cap+1)
    if not 128<=len(raw)<=cap:
        raise ValueError("Empty or excessive official native PSF payload")
    if raw.lstrip().lower().startswith((b"<html",b"<!doctype",b"<?xml",b"{")):
        raise ValueError("Archive response is markup, not native PSF data")
    if kind=="psfcat.fits" and not raw.startswith(b"SIMPLE  ="):
        raise ValueError("PSF fit catalog response is not FITS")
    return raw


def _finite_scalar(x,field:str):
    try:
        n=float(x)
    except (TypeError,ValueError,OverflowError) as exc:
        raise ValueError(f"Invalid {field}") from exc
    if not math.isfinite(n):
        raise ValueError(f"Nonfinite {field}")
    return n


def parse_psf_fit_catalogue(raw:bytes)->dict:
    """Read full official native CCD-quadrant catalog; emit no raw rows.

    Catalogue positions are on the detector's native CCD-quadrant and in its
    own RA/Dec astrometric solution. No per-source physical identity is
    inferred from those coordinates.
    """
    from astropy.io import fits
    import numpy as np
    if not isinstance(raw,bytes) or not 2880<=len(raw)<=CATALOGUE_BYTES_MAX:
        raise ValueError("Unexpected ZTF psfcat FITS bytes")
    if not raw.startswith(b"SIMPLE  ="):
        raise ValueError("Missing FITS signature")
    with fits.open(io.BytesIO(raw),memmap=False) as hdu:
        tables=[h for h in hdu if isinstance(h,fits.BinTableHDU)]
        if len(tables)!=1:
            raise ValueError("Ambiguous/missing PSF-fit binary table")
        tbl=tables[0]
        names={name.lower():name for name in (tbl.columns.names or [])}
        if not set(REQUIRED_COLUMNS).issubset(names):
            raise ValueError("Incomplete ZTF official §10.6 PSF-fit column set")
        n=len(tbl.data)
        if n>MAX_CATALOGUE_ROWS:
            raise ValueError("PSF catalogue row budget exceeded")
        if n<1:
            return {
                "status":"PSF_CATALOGUE_EMPTY_NO_SOURCE_IDENTITY_INFERENCE",
                "sha256":hashlib.sha256(raw).hexdigest(),
                "n_native_psf_catalogue_rows":0,
                "rows":[],
            }
        values={k:np.asarray(tbl.data[names[k]]).copy() for k in REQUIRED_COLUMNS}
    # These fields must be numerical scalar columns, not FITS vector or
    # variable-length arrays. Reject whole malformed source tables.
    for key,arr in values.items():
        if arr.shape!=(n,) or not np.issubdtype(arr.dtype,np.number):
            raise ValueError(f"Invalid ZTF native PSF column shape/type: {key}")
    ids=np.asarray(values["sourceid"],dtype=np.float64)
    if (not np.isfinite(ids).all() or np.any(ids<0)
        or np.any(ids!=np.floor(ids)) or len(set(ids.tolist()))!=n):
        raise ValueError("Duplicate/nonintegral ZTF per-exposure PSF sourceid")
    # RA/Dec and native pixel coordinates are mandatory. A malformed table
    # cannot be treated as a set of nondetections.
    for key in ("ra","dec","xpos","ypos"):
        vals=np.asarray(values[key],dtype=float)
        if not np.isfinite(vals).all():
            raise ValueError("Nonfinite source sky/native CCD coordinates")
    ra=np.asarray(values["ra"],dtype=float)
    dec=np.asarray(values["dec"],dtype=float)
    if (np.any(ra<0) or np.any(ra>=360)
        or np.any(dec < -90) or np.any(dec>90)):
        raise ValueError("Catalogue contains invalid ICRS coordinates")
    return {
        "status":"ORIGINAL_ZTF_PSF_CATALOGUE_PARSED_UNVERIFIED",
        "sha256":hashlib.sha256(raw).hexdigest(),
        "n_native_psf_catalogue_rows":int(n),
        "rows":values,
    }


def _sep_arcsec_vectorized(ra_deg,dec_deg,target_ra,target_dec):
    import numpy as np
    # Stable great-circle haversine for tiny angular separations, RA wrap.
    rr=np.radians(ra_deg)
    dd=np.radians(dec_deg)
    ra=math.radians(target_ra)
    de=math.radians(target_dec)
    a=np.sin((dd-de)/2)**2+np.cos(dd)*math.cos(de)*np.sin((rr-ra)/2)**2
    return np.degrees(2*np.arcsin(np.sqrt(np.clip(a,0,1))))*3600.


def screen_psf_catalogue_targets(catalogue:dict,gaia_predictions:list[dict],
                                  *,radius_arcsec:float=MATCH_RADIUS_ARCSEC)->dict:
    """Nearest/second-nearest source and PSF-profile QC, no crossmatch claim.

    Explicitly blocks reuse of the same pipeline sourceid by separate Gaia
    sources in the same CCD/exposure, and flags adjacent catalogued sources.
    """
    import numpy as np
    if not .2<=radius_arcsec<=2 or not 1<=len(gaia_predictions)<=MAX_SOURCE_REQUESTS_PER_EXPOSURE:
        raise ValueError("Unbounded matching radius or source count")
    ids=[str(p["source_id"]) for p in gaia_predictions]
    if len(set(ids))!=len(ids):
        raise ValueError("Duplicate Gaia candidate ID in one ZTF exposure")
    for sid in ids:
        if not sid.isdigit():
            raise ValueError("Invalid Gaia source identifier")
    rows=catalogue["rows"]
    if catalogue["status"]=="PSF_CATALOGUE_EMPTY_NO_SOURCE_IDENTITY_INFERENCE":
        return {
            "n_candidate_predictions":len(ids),
            "screens":[{"gaia_source_id":sid,"status":"NO_PSF_CATALOGUE_ENTRY_WITHIN_RADIUS",
                        "catalogue_download_succeeded":True,
                        "astrophysical_source_identity_confirmed":False}
                       for sid in ids],
            "n_provisional_unique_nearest_source_candidates":0,
            "independent_gaia_ztf_source_crossmatches_confirmed":0,
        }
    if catalogue["status"]!="ORIGINAL_ZTF_PSF_CATALOGUE_PARSED_UNVERIFIED":
        raise ValueError("Native catalogue is not parsed")
    out=[]
    for p in gaia_predictions:
        ra=_finite_scalar(p["geocentric_parallax_adjusted_ra_deg"],"Gaia RA")
        dec=_finite_scalar(p["geocentric_parallax_adjusted_dec_deg"],"Gaia Dec")
        validate_icrs(ra,dec)
        sep=_sep_arcsec_vectorized(rows["ra"],rows["dec"],ra,dec)
        close=np.flatnonzero(sep<=MAX_SEARCH_RADIUS_ARCSEC)
        ordered=close[np.argsort(sep[close])] if len(close) else close
        if not len(ordered) or float(sep[ordered[0]])>radius_arcsec:
            out.append({
                "gaia_source_id":str(p["source_id"]),
                "status":"NO_PSF_CATALOGUE_ENTRY_WITHIN_RADIUS",
                "nearest_within_5arcsec_arcsec":(
                    round(float(sep[ordered[0]]),6) if len(ordered) else None),
                "catalogue_download_succeeded":True,
                "astrophysical_source_identity_confirmed":False,
            })
            continue
        i=int(ordered[0])
        second=float(sep[ordered[1]]) if len(ordered)>1 else None
        flags=int(rows["flags"][i])
        snr=_finite_scalar(rows["snr"][i],"PSF catalogue SNR")
        chi=_finite_scalar(rows["chi"][i],"PSF catalogue chi")
        sharp=_finite_scalar(rows["sharp"][i],"PSF catalogue sharp")
        flux=_finite_scalar(rows["flux"][i],"PSF catalogue flux")
        sigflux=_finite_scalar(rows["sigflux"][i],"PSF catalogue flux error")
        good_flags=flags>=0 and flags & BAD_MASK_BITS == 0
        profile_ok=(0.5<=chi<=1.5 and -0.5<=sharp<=0.5
                    and snr>=5 and flux>0 and sigflux>0
                    and good_flags)
        crowded=(second is not None and second<=CROWDING_RADIUS_ARCSEC)
        status=(
            "MULTIPLE_NATIVE_PSF_SOURCES_WITHIN_CROWDING_RADIUS_REVIEW"
            if crowded else
            "NATIVE_PSF_FIT_PROFILE_OR_FLAG_REVIEW_REQUIRED"
            if not profile_ok else
            "PROVISIONAL_CATALOGUE_NEAREST_AND_PROFILE_SCREEN_PASSED")
        out.append({
            "gaia_source_id":str(p["source_id"]),
            "status":status,
            "ztf_native_per_exposure_sourceid":int(rows["sourceid"][i]),
            "nearest_source_separation_arcsec":round(float(sep[i]),6),
            "second_nearest_within_5arcsec_arcsec":(
                round(second,6) if second is not None else None),
            "ztf_source_neighbour_within_3arcsec":crowded,
            "ztf_native_psf_chi":round(chi,5),
            "ztf_native_psf_sharp":round(sharp,5),
            "ztf_native_psf_snr":round(snr,5),
            "ztf_catalogue_pixel_quality_flags":flags,
            "ztf_native_detector_xpos_pixels":round(float(rows["xpos"][i]),4),
            "ztf_native_detector_ypos_pixels":round(float(rows["ypos"][i]),4),
            "psf_fit_profile_quality_screen_passed":profile_ok,
            "astrophysical_source_identity_confirmed":False,
            "source_local_psf_evaluated":False,
        })
    by_native={}
    for s in out:
        z=s.get("ztf_native_per_exposure_sourceid")
        if z is not None:
            by_native.setdefault(z,[]).append(s)
    duplicates={key for key,group in by_native.items() if len(group)>1}
    for s in out:
        if s.get("ztf_native_per_exposure_sourceid") in duplicates:
            s["status"]="SAME_ZTF_PSF_SOURCE_ASSIGNED_TO_MULTIPLE_GAIA_IDS"
            s["source_assignment_unique"]=False
        else:
            s["source_assignment_unique"]=True
    accepted=sum(x["status"]=="PROVISIONAL_CATALOGUE_NEAREST_AND_PROFILE_SCREEN_PASSED" for x in out)
    return {
        "n_candidate_predictions":len(ids),
        "screens":out,
        "n_provisional_unique_nearest_source_candidates":accepted,
        "n_target_candidates_with_nearby_psf_catalogue_sources":sum(
            bool(x.get("ztf_source_neighbour_within_3arcsec")) for x in out),
        "independent_gaia_ztf_source_crossmatches_confirmed":0,
        "source_psf_physical_single_star_verified":False,
        "calibrated_ztf_detector_wcs_accuracy":False,
    }


def inspect_spatial_daophot_product(raw:bytes)->dict:
    """Bounded provenance-only header/shape inspection; not spatial PSF model."""
    if not isinstance(raw,bytes) or not 128<=len(raw)<=SPATIAL_PSF_BYTES_MAX:
        raise ValueError("Invalid native DAOPhot product bytes")
    if raw.lstrip().lower().startswith((b"<html",b"<!doctype",b"<?xml",b"{")):
        raise ValueError("HTML/JSON not a native DAOPhot source")
    head=raw[:384]
    binary_fraction=sum(not (b in (9,10,13) or 32<=b<=126) for b in head)/len(head)
    return {
        "status":"NATIVE_DAOPHOT_SPATIAL_PSF_DOWNLOADED_FORMAT_NOT_EVALUATED",
        "sha256":hashlib.sha256(raw).hexdigest(),
        "file_bytes":len(raw),
        "initial_384_byte_nonprintable_fraction":round(binary_fraction,4),
        "spatial_psf_model_decoded":False,
        "source_specific_psf_evaluated":False,
        "empirical_psf_at_gaia_reference_positions_calibrated":False,
    }


def audit_original_psf_catalogue(science_url:str,predictions:list[dict],*,
                                  timeout:float=12,fetch=fetch_native_psf_product)->dict:
    url=official_psf_product_url(science_url,"psfcat.fits")
    try:
        raw=fetch(url,kind="psfcat.fits",timeout=timeout)
        parsed=parse_psf_fit_catalogue(raw)
        screens=screen_psf_catalogue_targets(parsed,predictions)
        return {
            "status":"ZTF_ORIGINAL_PSF_CATALOGUE_SCREEN_COMPLETED",
            "psfcat_sha256":parsed["sha256"],
            "n_native_original_catalogue_rows":parsed["n_native_psf_catalogue_rows"],
            **screens,
        }
    except (HTTPError,URLError,TimeoutError,OSError,ValueError) as exc:
        result={
            "status":"ZTF_ORIGINAL_PSF_CATALOGUE_UNAVAILABLE_OR_UNUSABLE",
            "error_type":type(exc).__name__,
            "n_candidate_predictions":len(predictions),
            "independent_gaia_ztf_source_crossmatches_confirmed":0,
        }
        if isinstance(exc,HTTPError):result["http_status"]=int(exc.code)
        return result


def audit_original_spatial_psf(science_url:str,*,timeout:float=12,
                               fetch=fetch_native_psf_product)->dict:
    url=official_psf_product_url(science_url,"sciimgdao.psf")
    try:
        raw=fetch(url,kind="sciimgdao.psf",timeout=timeout)
        return inspect_spatial_daophot_product(raw)
    except (HTTPError,URLError,TimeoutError,OSError,ValueError) as exc:
        result={
            "status":"NATIVE_DAOPHOT_PSF_UNAVAILABLE_OR_INVALID",
            "error_type":type(exc).__name__,
            "source_specific_psf_evaluated":False,
        }
        if isinstance(exc,HTTPError):result["http_status"]=int(exc.code)
        return result
