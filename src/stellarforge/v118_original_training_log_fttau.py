"""v1.18 — official ZTF PSF-construction log audit and exploratory Gaia controls.

Native per-epoch psfcat.fits is a *fitted source* catalogue, not the set of
stars used to BUILD the DAOPhot PSF. The archived sciimlog.txt and log.txt
are quality/operations logs. We can audit their existence and PSF summary
records, but cannot certify candidate exclusion from the original PSF
training set unless an explicitly source-keyed, independently validated
training-star roster exists. This code NEVER invents such a roster.

The separate FT Tau exploratory control stratum is declared up front for
the current phase to investigate a previously observed lack of controls;
it is NOT silently treated as equivalent to the v1.17 strict cut.
"""
from __future__ import annotations

import hashlib
import math
import re
from urllib.parse import urlparse,urlunparse
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

from .coordinates import validate_icrs,angular_separation_arcsec
from .v15_image_pixels import _validate_official_cutout
from .v18_gaia_references import GAIA_ROW_CAP

ALLOWED_LOGS=("sciimlog.txt","log.txt")
MAX_LOG_BYTES=2_000_000
LOG_TIMEOUT_MAX=25
# Bounded processing-log flags only. Raw processing text never stored.
PATTERN_PSF=re.compile(r"\b(?:psf|daophot|allstar|pstselect|psfstars?|nstars?)\b",re.I)
PATTERN_COUNT=re.compile(
    r"\b(?:n(?:um(?:ber)?)?[\s_-]*psf[\s_-]*stars?|psf[\s_-]*stars?[\s_-]*(?:used|selected|total|count|n))"
    r"\s*[:=]\s*(\d{1,7})\b",re.I
)
MAX_EXPLORATORY_CONTROLS=4
EXPLORATORY_MIN_TARGET_DISTANCE=20.
EXPLORATORY_MAX_TARGET_DISTANCE=190.
EXPLORATORY_MIN_GAIA_SEPARATION=6.


def official_processing_log_url(science_url:str,product:str)->str:
    _validate_official_cutout(science_url)
    if product not in ALLOWED_LOGS:
        raise ValueError("Unsupported ZTF original-processing log")
    p=urlparse(science_url)
    if (p.query.count("center")!=1 or
        not p.path.startswith("/ibe/data/ztf/products/sci/")
        or not p.path.endswith("_sciimg.fits")):
        raise ValueError("Original dated ZTF science exposure required")
    return urlunparse(p._replace(
        path=p.path.removesuffix("_sciimg.fits")+"_"+product,
        query="",fragment=""))


def validate_processing_log_url(url:str,product:str):
    if product not in ALLOWED_LOGS:
        raise ValueError("Unsupported original log")
    p=urlparse(url)
    if (p.scheme!="https" or p.hostname!="irsa.ipac.caltech.edu"
        or p.username is not None or p.password is not None
        or p.port not in (None,443) or p.query or p.fragment
        or not p.path.startswith("/ibe/data/ztf/products/sci/")
        or not p.path.endswith("_"+product)):
        raise ValueError("Non-official ZTF processing log")
    # Revalidate the original science path using a known bounded query.
    src=urlunparse(p._replace(
        path=p.path.removesuffix("_"+product)+"_sciimg.fits",
        query="center=65.913324%2C24.937195&size=45arcsec&gzip=false"))
    _validate_official_cutout(src)


def fetch_original_processing_log(url:str,*,product:str,
                                  timeout:float=7,opener=urlopen)->bytes:
    validate_processing_log_url(url,product)
    if not math.isfinite(timeout) or not 1<=timeout<=LOG_TIMEOUT_MAX:
        raise ValueError("Unbounded logging archive timeout")
    req=Request(url,headers={
        "User-Agent":"StellarForge/1.18 bounded original PSF source-training log audit",
        "Accept":"text/plain,application/octet-stream"})
    with opener(req,timeout=timeout) as reply:
        final=getattr(reply,"geturl",lambda:url)()
        validate_processing_log_url(final,product)
        raw=reply.read(MAX_LOG_BYTES+1)
    if not 12<=len(raw)<=MAX_LOG_BYTES:
        raise ValueError("Missing or overbudget original processing log")
    return raw


def audit_psf_training_log(raw:bytes,*,product:str)->dict:
    """Inspect original pipeline log, never call source membership 'known'.

    Aggregate source counts are not training-star identities. Even a list of
    numbers labelled 'PSF' cannot be equated with Gaia or psfcat IDs without
    documented source-ID namespace and an actual roster validation.
    """
    if product not in ALLOWED_LOGS:
        raise ValueError("Unsupported PSF log type")
    if not isinstance(raw,bytes) or not 12<=len(raw)<=MAX_LOG_BYTES:
        raise ValueError("Malformed pipeline log bytes")
    try:
        decoded=raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("Original processing log not UTF-8") from exc
    if decoded.lstrip().lower().startswith(("<html","<!doctype","<?xml","{","[")):
        raise ValueError("Official log returned an error page, not text")
    if any(ord(c)==0 for c in decoded):
        raise ValueError("Binary payload is not an original text log")
    lines=decoded.splitlines()
    if len(lines)>250_000:
        raise ValueError("Unbounded original log line budget")
    matching=[l for l in lines if PATTERN_PSF.search(l)]
    counts=[]
    for line in matching:
        for m in PATTERN_COUNT.finditer(line):
            n=int(m.group(1))
            if n<=100_000:counts.append(n)
    return {
        "status":"ORIGINAL_ZTF_PROCESSING_LOG_READ_PSF_TRAINING_IDS_NOT_VERIFIABLE",
        "original_log_product":product,
        "original_log_sha256":hashlib.sha256(raw).hexdigest(),
        "original_log_bytes":len(raw),
        "n_original_log_lines":len(lines),
        "n_lines_mentioning_psf_or_daophot":len(matching),
        "n_aggregate_psf_star_counts_seen":len(counts),
        "aggregate_psf_star_count_values_seen":sorted(set(counts))[:12],
        "individual_training_source_id_namespace_documented":False,
        "original_psf_training_star_membership_recovered":False,
        "new_gaia_control_ids_confirmed_absent_from_psf_training":0,
        "psf_fit_catalog_source_ids_do_not_identify_psf_training_star_roster":True,
        "source_membership_scientific_status":"NOT_VERIFIABLE_FROM_THIS_LOG",
    }


def audit_exposure_training_logs(science_url:str,*,timeout:float=7,
                                 fetch=fetch_original_processing_log)->dict:
    out=[]
    for kind in ALLOWED_LOGS:
        url=official_processing_log_url(science_url,kind)
        try:
            raw=fetch(url,product=kind,timeout=timeout)
            out.append(audit_psf_training_log(raw,product=kind))
        except (HTTPError,URLError,TimeoutError,OSError,ValueError) as exc:
            e={"status":"OFFICIAL_ZTF_PROCESSING_LOG_UNAVAILABLE_OR_INVALID",
               "original_log_product":kind,
               "error_type":type(exc).__name__,
               "original_psf_training_star_membership_recovered":False}
            if isinstance(exc,HTTPError):e["http_status"]=int(exc.code)
            out.append(e)
    return {
        "status":"ORIGINAL_PSF_TRAINING_LOG_AUDIT_COMPLETED_WITH_UNRESOLVED_MEMBERSHIP",
        "original_log_product_results":out,
        "n_original_processing_logs_read":sum(
            e["status"]=="ORIGINAL_ZTF_PROCESSING_LOG_READ_PSF_TRAINING_IDS_NOT_VERIFIABLE"
            for e in out),
        "n_official_psf_training_source_rosters_authenticated":0,
        "n_new_gaia_sources_proven_excluded_from_native_zft_training":0,
        "model_training_star_membership_established":False,
    }


def select_exploratory_ft_tau_gaia_controls(rows:list[dict],*,target_id:str,
                                             excluded_source_ids:set[str],
                                             max_controls:int=4)->dict:
    """Preregistered diagnostic tier for sparse field, NOT 'strict' v1.17.

    Previously stricter Gaia v1.17 controls were exhausted. Relative to that
    tier, this is EXPLORATORY: target distance 20–190'', G 12–19.2, Gaia SNR
    >=30, RUWE <1.6 and 6'' Gaia source separation (not 10''). All selected
    objects remain unverified ZTF and non-isolated astrophysically.
    """
    if (not str(target_id).isdigit() or target_id not in excluded_source_ids
        or not 1<=max_controls<=MAX_EXPLORATORY_CONTROLS
        or len(rows)>=GAIA_ROW_CAP):
        raise ValueError("Invalid Gaia exploratory preselection/design")
    by_id={str(r["source_id"]):r for r in rows}
    if len(by_id)!=len(rows):
        raise ValueError("Duplicate Gaia source ID")
    target=by_id.get(str(target_id))
    if target is None:
        return {
            "status":"FT_TAU_GAIA_TARGET_NOT_IN_INDEPENDENT_WIDE_CONE",
            "n_gaia_original_rows":len(rows),
            "controls":[],"n_exploratory_controls_selected":0,
            "same_eligibility_as_original_v117_strict_controls":False}
    t_ra=float(target["ra"]);t_dec=float(target["dec"])
    validate_icrs(t_ra,t_dec)
    exclusions={
        "already_used_source_id":0,"outside_exploratory_target_range":0,
        "brightness_or_signal":0,"ruwe_or_astrometry":0,
        "closer_than_6arcsec_Gaia_neighbour":0}
    good=[]
    for r in rows:
        sid=str(r["source_id"])
        if sid in excluded_source_ids:
            exclusions["already_used_source_id"]+=1;continue
        ra=float(r["ra"]);dec=float(r["dec"]);validate_icrs(ra,dec)
        sep=angular_separation_arcsec(t_ra,t_dec,ra,dec)
        if not EXPLORATORY_MIN_TARGET_DISTANCE<=sep<=EXPLORATORY_MAX_TARGET_DISTANCE:
            exclusions["outside_exploratory_target_range"]+=1;continue
        mag=r.get("g_mag");snr=r.get("g_flux_snr")
        if mag is None or snr is None or not 12<=float(mag)<=19.2 or float(snr)<30:
            exclusions["brightness_or_signal"]+=1;continue
        if (r.get("ruwe") is None or not 0.5<=float(r["ruwe"])<1.6
            or r.get("duplicated_source") is not False
            or r.get("astrometric_params_solved") not in (31,95)
            or any(r.get(k) is None for k in (
                "pmra","pmdec","parallax","ra_error_mas",
                "dec_error_mas","pmra_error_mas_yr","pmdec_error_mas_yr"))
            or max(float(r["ra_error_mas"]),float(r["dec_error_mas"]))>3
            or max(float(r["pmra_error_mas_yr"]),float(r["pmdec_error_mas_yr"]))>3):
            exclusions["ruwe_or_astrometry"]+=1;continue
        nearby=min((
            angular_separation_arcsec(
                ra,dec,float(o["ra"]),float(o["dec"]))
            for o in rows if str(o["source_id"])!=sid
        ),default=math.inf)
        if nearby<EXPLORATORY_MIN_GAIA_SEPARATION:
            exclusions["closer_than_6arcsec_Gaia_neighbour"]+=1;continue
        dra=(ra-t_ra+180)%360-180
        east=dra*math.cos(math.radians(t_dec))
        north=dec-t_dec
        quadrant=int(east>=0)+2*int(north>=0)
        good.append({
            "source_id":sid,"gaia_g_mag":round(float(mag),4),
            "ruwe":round(float(r["ruwe"]),4),
            "gaia_nearest_neighbour_arcsec":round(nearby,4),
            "gaia_target_separation_arcsec":round(sep,4),
            "sky_quadrant":quadrant,
            "tier":"EXPLORATORY_NOT_EQUIVALENT_TO_STRICT_V117",
            "physical_source_single_star_confirmed":False,
            "independent_zft_gaia_crossmatch_confirmed":False,
        })
    good.sort(key=lambda s:(
        abs(s["gaia_g_mag"]-15.5),
        abs(s["gaia_target_separation_arcsec"]-100),s["source_id"]))
    chosen=[];seen=set()
    for quadrant in range(4):
        best=next((x for x in good if x["sky_quadrant"]==quadrant),None)
        if best and len(chosen)<max_controls:
            chosen.append(best);seen.add(best["source_id"])
    for x in good:
        if len(chosen)>=max_controls:break
        if x["source_id"] not in seen:
            chosen.append(x);seen.add(x["source_id"])
    return {
        "status":("GAIA_FT_TAU_EXPLORATORY_CONTROLS_PRESELECTED" if chosen
                  else "NO_FT_TAU_EXPLORATORY_GAIA_CONTROLS"),
        "n_gaia_original_rows":len(rows),
        "n_exploratory_candidates_before_budget":len(good),
        "n_exploratory_controls_selected":len(chosen),
        "n_control_sky_quadrants":len(set(x["sky_quadrant"] for x in chosen)),
        "exclusion_reasons":exclusions,
        "controls":chosen,
        "exploratory_tier_decided_before_ztf_psf_pixel_inspection":True,
        "same_eligibility_as_original_v117_strict_controls":False,
        "original_psf_training_exclusion_confirmed":False,
        "physical_gaia_ztf_source_ids_confirmed":0,
    }
