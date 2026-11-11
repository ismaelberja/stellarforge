"""Taurus R2: genuine external MAST PS1 DR2 source-level reference experiment.

Original 4 ZTF PSFcat exposures, original R1 FT Tau coordinate, and
prior 720-arcsec technical source selection are frozen. Unlike ZTF's
own PS1-anchored FITS image headers, this experiment explicitly queries
INDIVIDUAL PS1 DR2 mean source catalogue positions, magnitudes, colors
and quoted errors directly from MAST. Pilot colors, source identity,
variability and systematic errors remain provisional. Raw rows never
leave in-memory processing; do not merge FT Tau ZTF ObjectIDs.
"""
from __future__ import annotations

import csv
import hashlib
import io
import math
from collections import Counter
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .r2_fttau_crossfield_instrumental_ensemble import (
    fixed_four_exposure_pairs, original_native_catalogue_from_frozen_image,
    qualifying_original_native_sources,
)
from .r2_fttau_720_ps1_anchor import NEW_RADIUS_ARCSEC

PS1_API = "https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr2/mean.csv"
PS1_COLUMNS = (
    "objID","raMean","decMean","nDetections","ng","nr",
    "gMeanPSFMag","gMeanPSFMagErr","rMeanPSFMag","rMeanPSFMagErr",
)
PS1_PAGESIZE=5000
PS1_MAX_BYTES=8_000_000
PS1_MIN_DETECTIONS=5
PS1_MIN_GR_DETECTIONS=3
PS1_MAX_MEAN_MAG_ERROR=.05
PS1_MAG_MIN=12.
PS1_MAG_MAX=21.
PS1_COLOR_MIN=-.5
PS1_COLOR_MAX=3.5
PS1_CROWD_ARCSEC=2.
PS1_CROSSMATCH_ARCSEC=.6
N_MIN_TRIPLET_REFS=20
N_MIN_FIT_TRAIN=10
N_MIN_HELDOUT=8
MIN_TRAIN_COLOR_SPAN=.25
MAX_HELDOUT_BIAS=.08
MAX_HELDOUT_SCATTER=.12
CLIP_MIN_MAG=.10
N_ROBUST_ITERS=3
ERRORS=(HTTPError,URLError,TimeoutError,OSError,ValueError,TypeError,
        OverflowError,ArithmeticError,UnicodeError)


def external_ps1_url(ra:float,dec:float)->str:
    if not (math.isfinite(ra) and math.isfinite(dec)
            and 0<=ra<360 and -30<dec<90):
        raise ValueError("Invalid Pan-STARRS1 DR2 cone center")
    params={
        "ra":f"{ra:.10f}","dec":f"{dec:.10f}",
        "radius":f"{NEW_RADIUS_ARCSEC/3600:.8f}",
        "nDetections.gte":PS1_MIN_DETECTIONS,
        "pagesize":PS1_PAGESIZE,
        "columns":"["+",".join(PS1_COLUMNS)+"]",
    }
    return PS1_API+"?"+urlencode(params)


def fetch_external_ps1_mean_sources(ra:float,dec:float,*,timeout_sec:float=45,
                                     opener=urlopen)->bytes:
    if not math.isfinite(timeout_sec) or not 10<=timeout_sec<=60:
        raise ValueError("MAST request timeout out of bounds")
    req=Request(external_ps1_url(ra,dec),method="GET",
                headers={"User-Agent":"StellarForge/2.0 Taurus R2 original external PS1 source QC",
                         "Accept":"text/csv,text/plain"})
    with opener(req,timeout=timeout_sec) as response:
        raw=response.read(PS1_MAX_BYTES+1)
    if not raw or len(raw)>PS1_MAX_BYTES or raw.lstrip().startswith((b"<",b"{",b"[")):
        raise ValueError("MAST PS1 original response empty/oversized/non-CSV")
    return raw


def parse_ps1_original_mean(raw:bytes,*,ra0:float,dec0:float)->dict:
    """Never count an API HTTP HTML error, truncated page or untrusted row.

    Keep all returned PS1 sky positions for crowding, but select
    provisional photometrically good sources separately.
    """
    import numpy as np
    from scipy.spatial import cKDTree
    from .r2_fttau_crossfield_instrumental_ensemble import _xy_positions
    if not isinstance(raw,bytes) or not raw or len(raw)>PS1_MAX_BYTES:
        raise ValueError("No bounded original PS1 DR2 catalogue")
    try:
        decoded=raw.decode("utf-8-sig")  # Valid MAST CSV may contain a UTF-8 BOM
    except UnicodeDecodeError as exc:
        raise ValueError("Not UTF8 MAST CSV") from exc
    rows=list(csv.DictReader(io.StringIO(decoded)))
    if not rows or len(rows)>=PS1_PAGESIZE:
        raise ValueError("Original MAST PS1 table empty or potentially page-truncated")
    required={c.lower() for c in PS1_COLUMNS}
    headers={h.lower() for h in (csv.DictReader(io.StringIO(decoded)).fieldnames or [])}
    if not required.issubset(headers):
        raise ValueError("MAST PS1 returned incomplete requested columns")
    ids=[]
    positions=[]
    magnitudes=[]
    errmag=[]
    color=[]
    passed=[]
    rejects=Counter()
    for row in rows:
        d={k.lower():v for k,v in row.items() if k is not None}
        sid=str(d.get("objid") or "").strip()
        try:
            ra=float(d["ramean"]);dec=float(d["decmean"])
        except (TypeError,ValueError,OverflowError):
            raise ValueError("MAST PS1 source position unavailable")
        if not (math.isfinite(ra) and math.isfinite(dec) and 0<=ra<360
                and -90<=dec<=90 and sid.isdigit()):
            raise ValueError("Invalid original PS1 object ID / celestial position")
        ids.append(sid)
        positions.append((ra,dec))
        try:
            n=int(d["ndetections"]);ng=int(d["ng"]);nr=int(d["nr"])
            g=float(d["gmeanpsfmag"]);r=float(d["rmeanpsfmag"])
            ge=float(d["gmeanpsfmagerr"]);re=float(d["rmeanpsfmagerr"])
        except (TypeError,ValueError,OverflowError):
            # Invalid/missing PS1 photometry remains a REAL catalogued
            # neighbouring object, not automatically accepted as standard.
            rejects["incomplete_ps1_photometry"]+=1
            magnitudes.append((float("nan"),float("nan")))
            errmag.append((float("nan"),float("nan")))
            color.append(float("nan"));passed.append(False)
            continue
        magnitudes.append((g,r));errmag.append((ge,re));color.append(g-r)
        eligible=(n>=PS1_MIN_DETECTIONS and ng>=PS1_MIN_GR_DETECTIONS
                  and nr>=PS1_MIN_GR_DETECTIONS
                  and all(math.isfinite(z) for z in (g,r,ge,re))
                  and PS1_MAG_MIN<=g<=PS1_MAG_MAX
                  and PS1_MAG_MIN<=r<=PS1_MAG_MAX
                  and 0<ge<=PS1_MAX_MEAN_MAG_ERROR
                  and 0<re<=PS1_MAX_MEAN_MAG_ERROR
                  and PS1_COLOR_MIN<=g-r<=PS1_COLOR_MAX)
        if not eligible:rejects["ps1_quality_color_magnitude"]+=1
        passed.append(bool(eligible))
    if len(set(ids))!=len(ids):
        raise ValueError("PS1 DR2 duplicate objID in original source cone")
    xy=_xy_positions(np.asarray(positions)[:,0],np.asarray(positions)[:,1],ra0,dec0)
    radius=np.linalg.norm(xy,axis=1)
    dist=cKDTree(xy).query(xy,k=2)[0][:,1] if len(xy)>1 else np.array([np.inf])
    valid=(np.asarray(passed,dtype=bool)
           &(radius<=NEW_RADIUS_ARCSEC)
           &(radius>=15.)
           &(dist>=PS1_CROWD_ARCSEC))
    rejects["ps1_off_cone_or_ft_target_core"]=int(
        np.sum(np.asarray(passed)&((radius>NEW_RADIUS_ARCSEC)|(radius<15.))))
    rejects["ps1_native_neighbour_blend_screen"]=int(np.sum(
        np.asarray(passed)&(dist<PS1_CROWD_ARCSEC)))
    return {
        "original_response_SHA256":hashlib.sha256(raw).hexdigest(),
        "n_original_ps1_dr2_mean_source_rows":len(rows),
        "n_PS1_dr2_mean_rows_passing_mag_color_crowding_and_target_exclusion":int(valid.sum()),
        "rejected_source_categories":dict(sorted(rejects.items())),
        "original_ps1_source_catalogue_not_gaia_ft_physical_match":True,
        "id":np.asarray(ids,dtype=str)[valid],
        "xy":xy[valid],
        "gmag":np.asarray(magnitudes,dtype=float)[valid,0],
        "rmag":np.asarray(magnitudes,dtype=float)[valid,1],
        "gerr":np.asarray(errmag,dtype=float)[valid,0],
        "rerr":np.asarray(errmag,dtype=float)[valid,1],
        "color_gr":np.asarray(color,dtype=float)[valid],
    }


def same_band_original_ztf_ps1_triplets(native1605:dict,native609:dict,
                                        ps1:dict)->dict:
    """Only source-geometry triplets, never photometric-match selection."""
    import numpy as np
    from scipy.spatial import cKDTree
    first=native1605["xy"];second=native609["xy"];external=ps1["xy"]
    empty={
        "n_same_filter_external_PS1_unique_source_triplets":0,
        "ps1_ids":np.array([],dtype=str),
        "colors":np.empty(0),
        "ps1_gmag":np.empty(0),"ps1_rmag":np.empty(0),
        "ps1_gerr":np.empty(0),"ps1_rerr":np.empty(0),
        "m_inst_field1605":np.empty(0),"m_inst_field609":np.empty(0),
        "e_inst_field1605":np.empty(0),"e_inst_field609":np.empty(0),
    }
    if min(len(first),len(second),len(external))==0:
        return empty
    near_second=cKDTree(second)
    second_dist,second_idx=near_second.query(first,k=1)
    inverse=cKDTree(first)
    distback,backidx=inverse.query(second,k=1)
    good=np.flatnonzero((second_dist<=.75)
                        &(backidx[second_idx]==np.arange(len(first)))
                        &(distback[second_idx]<=.75))
    if not len(good):return empty
    p_nearest=cKDTree(external)
    pd,pi=p_nearest.query(first[good],k=1)
    original_second=second[second_idx[good]]
    p_to_second_dist=np.linalg.norm(external[pi]-original_second,axis=1)
    original_P_to_Zdist,original_P_to_Zidx=cKDTree(first[good]).query(external,k=1)
    selected=(pd<=PS1_CROSSMATCH_ARCSEC)&(p_to_second_dist<=PS1_CROSSMATCH_ARCSEC)
    selected&=(original_P_to_Zdist[pi]<=PS1_CROSSMATCH_ARCSEC)
    selected&=(original_P_to_Zidx[pi]==np.arange(len(good)))
    retained=good[selected]
    pindex=pi[selected]
    if len(set(ps1["id"][pindex]))!=len(pindex):
        raise ValueError("PS1 source was double-assigned to ZTF field references")
    si=second_idx[retained]
    return {
        "n_same_filter_external_PS1_unique_source_triplets":int(len(retained)),
        "ps1_ids":ps1["id"][pindex],
        "colors":ps1["color_gr"][pindex],
        "ps1_gmag":ps1["gmag"][pindex],"ps1_rmag":ps1["rmag"][pindex],
        "ps1_gerr":ps1["gerr"][pindex],"ps1_rerr":ps1["rerr"][pindex],
        "m_inst_field1605":native1605["mag"][retained],
        "m_inst_field609":native609["mag"][si],
        "e_inst_field1605":native1605["sigmag"][retained],
        "e_inst_field609":native609["sigmag"][si],
    }


def _split_indices(source_ids):
    import numpy as np
    parity=np.array([
        int.from_bytes(hashlib.sha256(x.encode()).digest()[:4],"big")%2
        for x in source_ids],dtype=int)
    if min(int((parity==0).sum()),int((parity==1).sum()))<N_MIN_HELDOUT:
        # Fixed PS1 source-ID sort fallback, independent of colors/mags.
        idx=np.argsort(source_ids)
        parity=np.zeros(len(source_ids),dtype=int)
        parity[idx[1::2]]=1
    return parity


def source_level_ps1_color_fit(triplets:dict,band:str)->dict:
    """PS1 DR2 mean photometry vs original native ZTF flux; pilot only."""
    import numpy as np
    if band not in ("g","r"):raise ValueError("Unspecified original ZTF filter")
    n=triplets["n_same_filter_external_PS1_unique_source_triplets"]
    base={
        "status":"NO_GO_INSUFFICIENT_EXTERNAL_PS1_TRIPLETS_OR_MODEL_VALIDATION",
        "n_independently_queried_PS1_unique_reference_triplets":n,
        "n_train":0,"n_heldout":0,
        "per_original_ZTF_field_fits":[],
        "both_fields_ps1_mean_color_holdout_qc_pass":False,
        "independent_PS1_source_rows_retrieved":True,
        "external_PanSTARRS_photometric_source_identification_for_FT_TAU":False,
        "full_absolute_photometric_calibration_certified":False,
        "original_ZTF_lightcurves_merged":False,
    }
    if n<N_MIN_TRIPLET_REFS:return base
    ids=triplets["ps1_ids"]
    colors=np.asarray(triplets["colors"],dtype=float)
    target=np.asarray(triplets["ps1_"+band+"mag"],dtype=float)
    target_err=np.asarray(triplets["ps1_"+band+"err"],dtype=float)
    if not(all(np.isfinite(x).all() for x in (colors,target,target_err))
           and (target_err>0).all() and len(set(ids))==n):
        return base
    parity=_split_indices(ids)
    ti=parity==0
    hi=parity==1
    ntrain,nheld=int(ti.sum()),int(hi.sum())
    if ntrain<N_MIN_FIT_TRAIN or nheld<N_MIN_HELDOUT:
        return {**base,"n_train":ntrain,"n_heldout":nheld}
    if np.ptp(colors[ti])<MIN_TRAIN_COLOR_SPAN:
        return {**base,"n_train":ntrain,"n_heldout":nheld,
                "status":"NO_GO_COLOR_BASELINE_TOO_NARROW"}
    X=np.column_stack((np.ones(n),colors-.8))
    field_results=[]
    for field in ("1605","609"):
        minst=np.asarray(triplets["m_inst_field"+field],dtype=float)
        minst_err=np.asarray(triplets["e_inst_field"+field],dtype=float)
        if not np.isfinite(minst).all() or not np.isfinite(minst_err).all():
            field_results.append({"field":field,"status":"INVALID_MAGNITUDES"})
            continue
        y=target-minst
        good=ti.copy()
        try:
            for _ in range(N_ROBUST_ITERS):
                if good.sum()<N_MIN_FIT_TRAIN:raise ValueError("Not enough fit PS1 references")
                model=np.linalg.lstsq(X[good],y[good],rcond=None)[0]
                residual=y-X@model
                mr=np.median(residual[good])
                scale=1.4826*np.median(np.abs(residual[good]-mr))
                newgood=ti & (np.abs(residual-mr)<=max(CLIP_MIN_MAG,3*scale))
                if np.array_equal(newgood,good):break
                good=newgood
            if good.sum()<N_MIN_FIT_TRAIN:raise ValueError("Not enough clipped training PS1 sources")
            model=np.linalg.lstsq(X[good],y[good],rcond=None)[0]
            rr=y[hi]-X[hi]@model
            med=float(np.median(rr))
            scatter=float(1.4826*np.median(np.abs(rr-med)))
            intercept,slope=map(float,model)
            goodfit=(15<=intercept<=35 and abs(slope)<=1.
                     and abs(med)<=MAX_HELDOUT_BIAS and scatter<=MAX_HELDOUT_SCATTER)
            field_results.append({
                "field":field,
                "status":("PS1_SOURCE_LEVEL_INTERNAL_HELDOUT_PILOT_PASS"
                          if goodfit else "NO_GO_EXTERNAL_PS1_COLOR_FIT_HELDOUT"),
                "n_train":ntrain,
                "n_train_after_clipping":int(good.sum()),
                "n_holdout":nheld,
                "reference_band":band,
                "PS1_gr_color_center":.8,
                "PS1_minus_native_instrumental_intercept_mag":round(intercept,5),
                "PS1_gr_empirical_slope_mag_per_mag":round(slope,5),
                "heldout_median_residual_mag":round(med,5),
                "heldout_robust_residual_scatter_mag":round(scatter,5),
                "median_nominal_ps1_plus_ztf_measurement_error_mag":round(
                    float(np.median(np.hypot(target_err[hi],minst_err[hi]))),5),
                "independent_ps1_source_level_reference_fitted":True,
                "full_absolute_calibration_uncertainty_certified":False,
                "formal_color_transformation_calibrated":False,
                "physical_gaia_ZTF_FT_Tau_match_confirmed":False,
            })
        except (ValueError,np.linalg.LinAlgError,FloatingPointError):
            field_results.append({"field":field,"status":"NO_GO_EXTERNAL_COLOR_FIT_NUMERIC_OR_SPARSE"})
    ok=len(field_results)==2 and all(
        x["status"]=="PS1_SOURCE_LEVEL_INTERNAL_HELDOUT_PILOT_PASS"
        for x in field_results)
    return {
        **base,"status":("PS1_EXTERNAL_SOURCE_LEVEL_PILOT_INTERNAL_HOLDOUT_PASS"
                        if ok else "NO_GO_EXTERNAL_SOURCE_LEVEL_COLOR_FIT"),
        "n_train":ntrain,"n_heldout":nheld,
        "per_original_ZTF_field_fits":field_results,
        "both_fields_ps1_mean_color_holdout_qc_pass":bool(ok),
    }


def original_external_ps1_ft_tau_study(seed:bytes,historic:dict,oid_receipt:dict,
                                       prior_original_images:dict,previous_720:dict,*,
                                       external_fetch=fetch_external_ps1_mean_sources,
                                       ztf_fetch=None)->dict:
    """ONE independent MAST PS1 query and exactly four frozen native catalogs."""
    from .v114_native_psfcat_association import fetch_native_psf_product
    native_fetch=ztf_fetch or fetch_native_psf_product
    fixed,frames=fixed_four_exposure_pairs(seed,historic,oid_receipt,prior_original_images)
    if (previous_720.get("new_sky_radius_arcsec")!=720.
            or previous_720.get("n_original_full_native_ZTF_psfcat_SHA_matched")!=4
            or previous_720.get("n_bands_internally_consistent_magnitude_offset")!=2
            or previous_720.get("n_directly_crossmatched_independent_PS1_reference_sources")!=0):
        raise ValueError("Previously frozen 720-arcsec internal-only photometry evidence changed")
    provenance={
        "status":"INDEPENDENT_MAST_PS1_DR2_SOURCE_QUERY_NOT_COMPLETED",
        "n_ps1_original_rows":0,"n_ps1_good_color_crowding_sources":0,
        "original_ps1_dr2_response_sha256":None,
    }
    external=None
    try:
        raw=external_fetch(fixed["seed_ra_deg"],fixed["seed_dec_deg"],timeout_sec=45)
        external=parse_ps1_original_mean(raw,ra0=fixed["seed_ra_deg"],
                                         dec0=fixed["seed_dec_deg"])
        provenance={
            "status":"MAST_ORIGINAL_PS1_DR2_MEAN_SOURCE_CATALOGUE_VALID",
            "n_ps1_original_rows":external["n_original_ps1_dr2_mean_source_rows"],
            "n_ps1_good_color_crowding_sources":external[
                "n_PS1_dr2_mean_rows_passing_mag_color_crowding_and_target_exclusion"],
            "original_ps1_dr2_response_sha256":external["original_response_SHA256"],
            "ps1_failed_source_quality_categories":external["rejected_source_categories"],
        }
    except ERRORS as exc:
        provenance["status"]="INDEPENDENT_PS1_ORIGINAL_CATALOGUE_UNAVAILABLE_OR_INCOMPLETE"
        provenance["error_type"]=type(exc).__name__
        if isinstance(exc,HTTPError):provenance["http_status"]=int(exc.code)

    by_band=[]
    for band in ("g","r"):
        source_status=[]
        q=[]
        for area in ("1605","609"):
            f=frames[band][area]
            out={"field":area,"original_oid":f["selection"]["ztf_oid"],
                 "original_full_native_psfcat_sha_match":False}
            try:
                cat=original_native_catalogue_from_frozen_image(
                    f,ra=fixed["seed_ra_deg"],dec=fixed["seed_dec_deg"],native_fetch=native_fetch)
                qq=qualifying_original_native_sources(
                    cat,ra0=fixed["seed_ra_deg"],dec0=fixed["seed_dec_deg"],
                    max_radius_arcsec=720.)
                q.append(qq)
                out.update({
                    "original_full_native_psfcat_sha_match":True,
                    "original_full_native_psfcat_sha256":cat["sha256"],
                    "n_clean_native_sources_within_720arcsec":qq[
                        "n_good_uncrowded_reference_candidates"],
                })
            except ERRORS as exc:
                out["status"]="ORIGINAL_ZTF_NATIVE_SOURCE_UNAVAILABLE_OR_CHANGED"
                out["error_type"]=type(exc).__name__
            source_status.append(out)
        if external is None or len(q)!=2:
            result={
                "status":"NO_GO_ORIGINAL_MAST_PS1_OR_ZTF_SOURCE_DATA_UNAVAILABLE",
                "n_independently_queried_PS1_unique_reference_triplets":0,
                "both_fields_ps1_mean_color_holdout_qc_pass":False,
                "per_original_ZTF_field_fits":[],
                "full_absolute_photometric_calibration_certified":False,
                "original_ZTF_lightcurves_merged":False,
            }
        else:
            triplets=same_band_original_ztf_ps1_triplets(q[0],q[1],external)
            result=source_level_ps1_color_fit(triplets,band)
        by_band.append({
            "band":band,
            "original_native_source_inputs":source_status,
            "independent_external_PS1_source_level_color_test":result,
            "ZTF_Gaia_target_physical_identity_confirmed":False,
            "original_ztf_oid_curves_joined":False,
        })
    return {
        "phase":"TAURUS_R2_EXTERNAL_MAST_PANSTARRS1_DR2_MEAN_SOURCE_COLOR_REFERENCE_PILOT",
        "frozen_nonrepresentative_taurus_gaia_seed_count":24,
        "fixed_original_ft_tau_ztf_oid_count":4,
        "n_new_original_ZTF_science_observation_epochs_selected":0,
        "external_PS1_DR2_original_source_query":provenance,
        "n_original_ZTF_full_native_psfcats_reverified":sum(
            f["original_full_native_psfcat_sha_match"]
            for b in by_band for f in b["original_native_source_inputs"]),
        "n_same_band_PanSTARRS_source_level_internal_pilot_passes":sum(
            b["independent_external_PS1_source_level_color_test"].get(
                "both_fields_ps1_mean_color_holdout_qc_pass",False)
            for b in by_band),
        "n_scientifically_certified_absolute_ZTF_PanSTARRS_calibrations":0,
        "n_independently_authenticated_gaia_ztf_FT_TAU_physical_counterparts":0,
        "n_merged_ztf_object_id_lightcurves":0,
        "n_confirmed_new_FT_TAU_variables_or_companions":0,
        "research_R2_full_physical_source_identity_complete":False,
        "original_r1_gaia_technical_seed_sha256":hashlib.sha256(seed).hexdigest(),
        "bands":by_band,
        "limitations":[
            "Direct independent PS1 DR2 source rows and colors may support preliminary cross-survey reference matching, but do not prove stable/nonblended standards or FT Tau physical Gaia-ZTF identity.",
            "PS1 and ZTF mean/native magnitudes have different survey filter responses and epochs; fitted gr slopes are empirical, not a calibrated photometric passband transformation or complete error model.",
            "Cross-survey astrometric matching at fixed 0.6arcsec omits epoch-dependent source proper motion, PSF blend errors and full match probability; matches are provisional.",
            "MAST cone search 5000-source cap is fail-closed; access error/empty dataset is not evidence of physical absence or stable photometry.",
            "No original source rows, sky coordinates, PS1 source IDs, raw photometry or FITS pixels are committed; only derived QC and SHA fingerprints.",
            "The four FT Tau ZTF OIDs remain unmerged; no physical variability or newly discovered astrophysical companion claim.",
        ],
    }
