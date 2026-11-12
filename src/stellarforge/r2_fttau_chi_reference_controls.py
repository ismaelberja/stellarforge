"""FT Tau R2 original ZTF PSF chi reference controls, selected without chi.

Uses only the prospectively fixed 3 early/late ZTF pairs of PR44; source
population and PSF chi diagnostics are not a calibrated error model,
new stellar detection, cross-epoch identity or threshold endorsement.
"""
from __future__ import annotations

import hashlib
import math
from urllib.error import HTTPError, URLError

from .r2_ft_tau_two_field_fits import FT_GAIA, FT_OIDS, catalogue_candidates
from .r2_fttau_crossfield_instrumental_ensemble import (
    fixed_four_exposure_pairs, _xy_positions,
)
from .r2_fttau_multinight_astrometry import select_earliest_latest_independent_nights
from .r2_ztf_oid_multiplicity import fetch_historic_oid
from .r2_fttau_gaia_ps1_target_astrometry import original_target_native_candidate
from .v14_field_review import ztf_science_cutout_url
from .v114_native_psfcat_association import (
    official_psf_product_url, fetch_native_psf_product, parse_psf_fit_catalogue,
    _sep_arcsec_vectorized,
)
from .v113_official_masks_psf import BAD_MASK_BITS
from .v19_gaia_covariance import (
    fetch_gaia_astrometry, parse_gaia_astrometry, propagate_gaia_5p_formal,
)

MIN_SOURCE_CONTROLS = 20
SKY_INNER_ARCSEC = 15.0
SKY_OUTER_ARCSEC = 720.0
ISOLATION_ARCSEC = 3.0
SNR_MIN = 20.0
CHILOW = .5
CHIHIGH = 1.5
TARGET_SNR_RATIO = 2.0
FROZEN_GROUPS = (("g", "1605"), ("g", "609"), ("r", "609"))
NETWORK_ERRORS = (HTTPError, URLError, TimeoutError, OSError)


def frozen_inputs(seed: bytes, historic: dict, oid_receipt: dict,
                  previous_images: dict, epoch_ledger: dict,
                  failure_ledger: dict) -> tuple[dict, dict, list[dict]]:
    """Hard-fail any departure from six original frozen data identities."""
    target, frames = fixed_four_exposure_pairs(
        seed, historic, oid_receipt, previous_images)
    if (epoch_ledger.get("run_id") != 43270659201
            or epoch_ledger.get("n_original_ztf_catalogues_new") != 8
            or epoch_ledger.get("n_provisional_quality_passed") != 5
            or epoch_ledger.get("n_two_night_pairs_quality_passed") != 1
            or epoch_ledger.get("n_confirmed_physical_matches") != 0
            or epoch_ledger.get("n_merged_lightcurves") != 0
            or epoch_ledger.get("original_seed_sha256") != hashlib.sha256(seed).hexdigest()
            or failure_ledger.get("original_run_id") != 43273246447
            or failure_ledger.get("n_exact_original_psfcats_sha_verified") != 3
            or failure_ledger.get("previous_pass_unchanged") != 5
            or failure_ledger.get("previous_failed_unchanged") != 3
            or failure_ledger.get("scientific_r2_complete") is not False):
        raise ValueError("Prior Gaia/ZTF real-source evidence changed")
    by_key = {(x["band"], str(x["field"])): x
              for x in epoch_ledger.get("source_groups", [])}
    if set(by_key) != set(FROZEN_GROUPS) | {("r", "1605")}:
        raise ValueError("Four source groups are missing/duplicated")
    by_fail = {(x["band"], str(x["field"])): x
               for x in failure_ledger.get("source_checks", [])}
    if set(by_fail) != set(FROZEN_GROUPS):
        raise ValueError("Bad profile group identity changed")
    if by_key["r","1605"].get("native_psf_pass") != [True, True]:
        raise ValueError("Fourth excluded source group no longer valid")
    out=[]
    for band,field in FROZEN_GROUPS:
        item = by_key[band,field]
        old = by_fail[band,field]
        if item.get("native_psf_pass") != [True,False]:
            raise ValueError("Previously selected original native source profile changed")
        frozen_oid=next(x[2] for x in FT_OIDS if (x[0],x[1]) == (band,field))
        if (item["oid"]!=frozen_oid or old["mjd"]!=item["mjds"][1]
                or old["original_psfcat_sha256"]!=item["sha"][1]
                or len(item.get("sha",[]))!=2
                or len(item.get("mjds",[]))!=2):
            raise ValueError("Original observation/PSF hash/target group mismatch")
        if not all(isinstance(s,str) and len(s)==64 for s in item["sha"]):
            raise ValueError("Invalid frozen source SHA")
        out.append({
            "band":band, "field":field, "oid":frozen_oid,
            "early_mjd":item["mjds"][0],"late_mjd":item["mjds"][1],
            "original_psfcat_shas":item["sha"],
            "late_psf_chi_three_decimal":old["psf_chi"],
        })
    return target,frames,out


def descriptive_chi_distribution(chis, *, target_chi: float) -> dict:
    """No inferential stats: count and describe frozen chi-blind controls."""
    import numpy as np
    a=np.asarray(chis,dtype=float)
    if a.ndim!=1 or not np.isfinite(a).all() or np.any(a<0):
        raise ValueError("Invalid native original source chi")
    n=int(a.size)
    if n==0:
        return {
            "status":"UNDERPOWERED_CHI_BLIND_REFERENCE_CONTROLS",
            "n_reference_sources":0,"n_chi_below_0p5":0,
            "n_chi_between_0p5_and_1p5":0,"n_chi_above_1p5":0,
            "fraction_chi_below_0p5":None,
            "chi_quantiles_p10_p50_p90":None,
            "target_chi_percentile_of_control_distribution":None,
            "controls_selected_without_chi":True,
        }
    return {
        "status":("DESCRIPTIVE_REFERENCE_SAMPLE_ADEQUATE_NOT_PSF_CALIBRATION"
                  if n>=MIN_SOURCE_CONTROLS else "UNDERPOWERED_CHI_BLIND_REFERENCE_CONTROLS"),
        "n_reference_sources":n,
        "n_chi_below_0p5":int(np.count_nonzero(a<CHILOW)),
        "n_chi_between_0p5_and_1p5":int(np.count_nonzero((a>=CHILOW)&(a<=CHIHIGH))),
        "n_chi_above_1p5":int(np.count_nonzero(a>CHIHIGH)),
        "fraction_chi_below_0p5":round(float(np.mean(a<CHILOW)),6),
        "chi_quantiles_p10_p50_p90":[round(float(x),6) for x in np.quantile(a,[.1,.5,.9])],
        "target_chi_percentile_of_control_distribution":round(
            float(100*np.mean(a<=target_chi)),4),
        "controls_selected_without_chi":True,
    }


def chi_blind_local_controls(native: dict, prediction: dict) -> dict:
    """Reference controls without using chi or a prior chi-filtered sample."""
    import numpy as np
    from scipy.spatial import cKDTree

    if native.get("status")!="ORIGINAL_ZTF_PSF_CATALOGUE_PARSED_UNVERIFIED":
        raise ValueError("Expected full original PSFcat FITS source rows")
    rows=native["rows"]
    if not 2<=len(rows["ra"])<=120000:
        raise ValueError("Original native source catalogue too small/large")
    ra=float(prediction["geocentric_parallax_adjusted_ra_deg"])
    dec=float(prediction["geocentric_parallax_adjusted_dec_deg"])
    xy=_xy_positions(rows["ra"],rows["dec"],ra,dec)
    if not np.isfinite(xy).all():
        raise ValueError("Invalid native source astrometry")
    dist=np.linalg.norm(xy,axis=1)
    neighbours=cKDTree(xy).query(xy,k=2)[0][:,1]
    snr=np.asarray(rows["snr"],dtype=float)
    chi=np.asarray(rows["chi"],dtype=float)
    sharp=np.asarray(rows["sharp"],dtype=float)
    flags=np.asarray(rows["flags"],dtype=float)
    flux=np.asarray(rows["flux"],dtype=float)
    sigflux=np.asarray(rows["sigflux"],dtype=float)
    safe_flags=np.isfinite(flags)&(flags>=0)&(flags<2**30)&(flags==np.floor(flags))
    flagbits=np.zeros(len(flags),dtype=np.int64)
    flagbits[safe_flags]=flags[safe_flags].astype(np.int64)
    quality=(np.isfinite(dist)&(dist>=SKY_INNER_ARCSEC)&(dist<=SKY_OUTER_ARCSEC)
             &(neighbours>=ISOLATION_ARCSEC)&safe_flags
             &((flagbits&BAD_MASK_BITS)==0)
             &np.isfinite(snr)&(snr>=SNR_MIN)
             &np.isfinite(flux)&(flux>0)
             &np.isfinite(sigflux)&(sigflux>0)
             &np.isfinite(sharp)&(np.abs(sharp)<=.5))
    # Invalid chi recorded but never used to select a more favourable
    # population: only finite, nonnegative chi is an objectively defined value.
    invalid=int(np.count_nonzero(quality&(~np.isfinite(chi)|(chi<0))))
    measured=quality&np.isfinite(chi)&(chi>=0)
    # Pre-existing target source screen has frozen geometry/profile rule.
    target=original_target_native_candidate(native,prediction)
    target_dist=_sep_arcsec_vectorized(rows["ra"],rows["dec"],ra,dec)
    index=int(np.argmin(target_dist))
    target_chi=float(chi[index])
    target_snr=float(snr[index])
    if not math.isfinite(target_chi) or target_chi<0 or not math.isfinite(target_snr) or target_snr<=0:
        raise ValueError("Original FT Tau source chi/SNR nonfinite or invalid")
    matched=measured&(snr>=target_snr/TARGET_SNR_RATIO)&(snr<=target_snr*TARGET_SNR_RATIO)
    return {
        "target_original_chi":round(target_chi,6),
        "target_original_snr":round(target_snr,4),
        "target_original_source_status":target["status"],
        "target_native_source_nearest_gaia_arcsec":
            target["nearest_original_native_source_to_predicted_Gaia_arcsec"],
        "n_chi_invalid_in_chi_independent_eligible_controls":invalid,
        "all_chi_blind_controls":descriptive_chi_distribution(
            chi[measured],target_chi=target_chi),
        "snr_factor_two_matched_controls":descriptive_chi_distribution(
            chi[matched],target_chi=target_chi),
        "physical_gaia_ztf_source_identity_confirmed":False,
        "original_psf_chi_gate_reinterpreted_or_relaxed":False,
    }


def inspect_frozen_reference_image(frame: dict, *, fixed: dict,
                                   gaia: dict, ra0:float, dec0:float,
                                   native_fetch=fetch_native_psf_product,
                                   propagate=propagate_gaia_5p_formal,
                                   native_parse=parse_psf_fit_catalogue) -> dict:
    """Retrieve exactly one previously selected and byte-locked native catalog."""
    pred=propagate(gaia,mjd_utc=frame["mjd"])
    sci=ztf_science_cutout_url(frame,ra_center=ra0,dec_center=dec0,size_arcsec=60)
    url=official_psf_product_url(sci,"psfcat.fits")
    raw=native_fetch(url,kind="psfcat.fits",timeout=24)
    sha=hashlib.sha256(raw).hexdigest()
    if sha!=fixed:
        raise ValueError("FROZEN ORIGINAL ZTF PSFcat hash changed: hard NO-GO")
    native=native_parse(raw)
    if native.get("sha256")!=sha:
        raise ValueError("Original FITS parsing does not preserve bytes")
    cohort=chi_blind_local_controls(native,pred)
    return {
        "original_mjd":round(float(frame["mjd"]),6),
        "original_filefracday":frame["filefracday"],
        "original_full_native_psfcat_sha256":sha,
        "n_full_native_source_rows":native["n_native_psf_catalogue_rows"],
        **cohort,
    }


def run_fttau_chi_blind_original_reference_study(
        seed:bytes,historic:dict,oid_receipt:dict,
        previous_images:dict,epoch_ledger:dict,failure_ledger:dict,*,
        oid_fetch=fetch_historic_oid,
        gaia_fetch=fetch_gaia_astrometry,
        image_inspector=inspect_frozen_reference_image)->dict:
    """Run 3 frozen early+late original pairs, source selection before PSF data."""
    target,anchors,groups=frozen_inputs(
        seed,historic,oid_receipt,previous_images,epoch_ledger,failure_ledger)
    gaia_bytes=gaia_fetch((FT_GAIA,),timeout_sec=35)
    gaia=parse_gaia_astrometry(gaia_bytes,expected_ids=(FT_GAIA,))[FT_GAIA]
    out=[]
    for g in groups:
        band,field,oid=g["band"],g["field"],g["oid"]
        spec=next(x for x in FT_OIDS if x[0]==band and x[1]==field)
        meta=oid_fetch(oid,timeout_sec=35)
        table=catalogue_candidates(meta,spec)
        choice=select_earliest_latest_independent_nights(
            table["rows"],anchors[band][field]["selection"])
        selected=choice["selected_rows_ephemeral"]
        if (choice["status"]!="TWO_INDEPENDENT_NIGHTS_PRESELECTED"
                or len(selected)!=2
                or [round(x["mjd"],6) for x in selected] != [
                    g["early_mjd"],g["late_mjd"]]):
            raise ValueError("Original prospectively selected epochs changed")
        entries=[]
        for idx,source in enumerate(selected):
            entry=image_inspector(source,fixed=g["original_psfcat_shas"][idx],
                                  gaia=gaia,ra0=target["seed_ra_deg"],
                                  dec0=target["seed_dec_deg"])
            expected=(idx==0)
            status=entry["target_original_source_status"]
            is_pass=status=="PROVISIONAL_GAIA_NEAREST_ZTF_PSF_SOURCE_GEOMETRY_PASS"
            if is_pass!=expected:
                raise ValueError("Original 5/8 target quality classification changed")
            if idx==1 and abs(entry["target_original_chi"]-
                               g["late_psf_chi_three_decimal"])>.001:
                raise ValueError("Frozen rejected source chi changed")
            entries.append(entry)
        out.append({
            "band":band,"field":field,"fixed_ztf_oid":oid,
            "original_oid_metadata_response_sha256":table["raw_sha256"],
            "n_original_oid_rows":table["n_original_source_rows"],
            "frozen_earliest_latest_nights_reselected_without_psf":True,
            "original_two_epoch_reference_cohorts":entries,
            "previous_early_pass_late_fail_outcome_unchanged":True,
        })
    images=[entry for row in out for entry in row["original_two_epoch_reference_cohorts"]]
    return {
        "phase":"TAURUS_R2_ORIGINAL_FTTAU_SIX_BYTE_LOCKED_ZTF_PSF_CHI_BLIND_REFERENCE_COHORTS",
        "original_gaia_tap_sha256":hashlib.sha256(gaia_bytes).hexdigest(),
        "frozen_original_multinight_run":43270659201,
        "frozen_original_bad_psf_run":43273246447,
        "n_frozen_original_oid_strata_compared":len(out),
        "n_exact_original_native_psfcat_SHA_reverified":len(images),
        "n_original_full_native_reference_cohorts_described":len(images),
        "n_all_chi_blind_local_cohorts_with_20_or_more_sources":sum(
            x["all_chi_blind_controls"]["n_reference_sources"]>=MIN_SOURCE_CONTROLS
            for x in images),
        "n_snr_matched_chi_blind_cohorts_with_20_or_more_sources":sum(
            x["snr_factor_two_matched_controls"]["n_reference_sources"]>=MIN_SOURCE_CONTROLS
            for x in images),
        "original_fixed_same_oid_early_late_groups":out,
        "original_previous_5_of_8_pass_and_3_of_8_fail_status_changed":False,
        "n_original_ztf_oid_lightcurves_merged":0,
        "n_physical_gaia_ztf_fttau_identities_confirmed":0,
        "n_astrophysical_variability_or_companions_confirmed":0,
        "scientific_r2_identity_and_variability_completed":False,
        "limitations":[
            "Reference controls sampled from same native PSF fit pipeline, not independent astrophysical ground truth.",
            "Reference source identities do not provide cross-epoch verified physical star matches.",
            "No PSF chi calibration, source-specific error covariance or rationale to change prior frozen 0.5 threshold established.",
            "No raw original source rows, positions, magnitudes or image pixels are archived.",
            "Original Gaia-ZTF source identity, proper motion, blending and intrinsic variability remain scientifically unresolved.",
        ],
    }
