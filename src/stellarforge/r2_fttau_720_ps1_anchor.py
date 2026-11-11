"""New preregistered Taurus R2 FT Tau original 720" field and PS1-header pilot.

This is NOT a revision of the genuine 360" 10-g/19-r NO-GO.
The earlier four ZTF original exposure/OID pairs and native PSFcat
payload SHA hashes must match exactly. Source magnitudes and original
FITS pixels are held in-memory only; no photometric lightcurves merged.

ZTF native PSFcat mag = -2.5log10(DN flux), instrumental, not AB.
ZTF science FITS MAGZP/NMATCHES/CLRCOEFF are *pipeline*
PS1-anchored calibration metadata, NOT a new independent direct PS1
catalogue query, a physical Gaia/ZTF crossmatch or certified calibration.
"""
from __future__ import annotations

import hashlib
import io
import math
from urllib.error import HTTPError, URLError

from .r2_fttau_crossfield_instrumental_ensemble import (
    fixed_four_exposure_pairs, original_native_catalogue_from_frozen_image,
    qualifying_original_native_sources, original_crossfield_reference_pairs,
    internal_relative_offset_qc,
)
from .v14_field_review import ztf_science_cutout_url
from .v15_image_pixels import fetch_fits_cutout

NEW_RADIUS_ARCSEC = 720.
SPATIAL_INNER_BOUND_ARCSEC = 360.
MIN_SPATIAL_STRATUM_PAIRS = 6
MAX_SPATIAL_MEDIAN_DIFFERENCE_MAG = .10
ERRORS = (HTTPError,URLError,TimeoutError,OSError,ValueError,
          TypeError,OverflowError,ArithmeticError)


def original_ztf_header_ps1_anchor(frame:dict,*, ra:float,dec:float,
                                   science_fetch=fetch_fits_cutout)->dict:
    """Read only bounded ZTF archive FITS header summary; raw pixels ephemeral.

    A returned 60" cutout is not guaranteed byte-identical to prior
    source-centred cutout; verify SAME underlying full science filename
    and previously frozen OID/CCD/quadrant/MJD instead.
    """
    from astropy.io import fits
    from astropy.wcs import WCS

    sel=frame["selection"]
    field,ccd,qid=sel["original_field_ccd_quadrant"]
    row={"filefracday":sel["original_filefracday"],"field":str(field),
         "ccdid":str(ccd),"qid":str(qid),"filtercode":"z"+sel["band"]}
    url=ztf_science_cutout_url(row,ra_center=ra,dec_center=dec,size_arcsec=60)
    filename=url.split("/")[-1].split("?")[0]
    if filename != frame["original_science_product_identifier"]:
        raise ValueError("Original prior science image filename is different")
    payload=science_fetch(url,timeout=24)
    if not isinstance(payload,bytes) or not payload.startswith(b"SIMPLE  ="):
        raise ValueError("Original ZTF FITS header absent")
    with fits.open(io.BytesIO(payload),memmap=False) as hdul:
        hs=[h for h in hdul if getattr(getattr(h,"data",None),"ndim",0)==2]
        if len(hs)!=1:
            raise ValueError("Not exactly one original science image")
        header=hs[0].header.copy()
    wcs=WCS(header)
    if not wcs.has_celestial or wcs.pixel_n_dim!=2:
        raise ValueError("Original FITS celestial WCS missing")
    rx,ry=wcs.world_to_pixel_values(ra,dec)
    if not all(math.isfinite(x) for x in (rx,ry)):
        raise ValueError("Original FITS coordinate mapping invalid")
    scalars={}
    for key in ("MAGZP","MAGZPUNC","MAGZPRMS","CLRCOEFF","CLRCOUNC"):
        value=header.get(key)
        try:
            v=float(value)
        except (TypeError,ValueError,OverflowError):
            v=None
        scalars[key]=round(v,7) if v is not None and math.isfinite(v) else None
    try:
        nmatches=int(header.get("NMATCHES"))
        if nmatches<0 or nmatches>50000: nmatches=None
    except (ValueError,TypeError,OverflowError):
        nmatches=None
    try:
        infobits=int(header.get("INFOBITS"))
        if infobits<0:infobits=None
    except (ValueError,TypeError,OverflowError):
        infobits=None
    required=(scalars["MAGZP"] is not None and 15<=scalars["MAGZP"]<=35
              and scalars["MAGZPUNC"] is not None and 0<=scalars["MAGZPUNC"]<=.5
              and scalars["MAGZPRMS"] is not None and 0<=scalars["MAGZPRMS"]<=1
              and scalars["CLRCOEFF"] is not None and abs(scalars["CLRCOEFF"])<=2
              and scalars["CLRCOUNC"] is not None and 0<=scalars["CLRCOUNC"]<=.5
              and nmatches is not None)
    # Public ZTF DR recommendations use per-band min PS1 calib samples and
    # ZP RMS, plus other criteria. This is a partial official-quality screen.
    band=sel["band"]
    min_ps1=80 if band=="g" else 120
    max_rms=.06 if band=="g" else .05
    partial_qc=bool(required and nmatches>=min_ps1
                    and scalars["MAGZPRMS"]<=max_rms
                    and (infobits is None or (infobits&(1<<25))==0))
    return {
        "status":("PS1_ANCHORED_ZTF_PIPELINE_HEADER_PARSED" if required
                  else "ORIGINAL_FITS_PS1_PIPELINE_HEADER_INCOMPLETE"),
        "original_science_filename":filename,
        "source_cutout_fits_sha256":hashlib.sha256(payload).hexdigest(),
        "source_cutout_sha_may_differ_from_prior_different_center":True,
        "per_exposure_zTF_pipeline_header_values":scalars,
        "original_ps1_pipeline_header_NMATCHES":nmatches,
        "original_info_bits":infobits,
        "public_ZTF_partial_ps1_match_and_zp_rms_screen_pass":partial_qc,
        "full_ZTF_exposure_quality_certified":False,
        "external_PS1_source_rows_queried":False,
        "independent_absolute_zeropoint_calibration_performed":False,
        "stellar_source_astrophysical_identity_verified":False,
    }


def geometry_stratified_median_screen(matched:dict)->dict:
    """Check inner-versus-new-annulus source offset trend WITHOUT replanning."""
    import numpy as np
    delta=np.asarray(matched["delta_native_instrumental_mag_b_minus_a"],dtype=float)
    xy=np.asarray(matched["match_xy"],dtype=float)
    if xy.shape!=(len(delta),2) or not(np.isfinite(delta).all() and np.isfinite(xy).all()):
        raise ValueError("Invalid matched original native control geometry")
    radii=np.linalg.norm(xy,axis=1)
    inner=delta[radii<=SPATIAL_INNER_BOUND_ARCSEC]
    outer=delta[(radii>SPATIAL_INNER_BOUND_ARCSEC)&(radii<=NEW_RADIUS_ARCSEC)]
    base={
        "n_old_inner_360arcsec_reference_pairs":int(len(inner)),
        "n_new_outer_360_to_720arcsec_reference_pairs":int(len(outer)),
        "spatial_median_delta_inst_mags_inner_minus_outer":None,
        "n_min_each_spatial_stratum":MIN_SPATIAL_STRATUM_PAIRS,
        "field_wide_spatially_uniform_photometry_established":False,
        "not_independent_instrument_photometric_calibration":True,
    }
    if min(len(inner),len(outer))<MIN_SPATIAL_STRATUM_PAIRS:
        return {**base,"status":"SPATIAL_PROFILE_UNDERPOWERED"}
    diff=float(np.median(inner)-np.median(outer))
    return {
        **base,
        "status":("SPATIAL_PROFILE_DESCRIPTIVELY_WITHIN_0P10_MAG" if
                  abs(diff)<=MAX_SPATIAL_MEDIAN_DIFFERENCE_MAG
                  else "SPATIAL_GRADIENT_REVIEW"),
        "spatial_median_delta_inst_mags_inner_minus_outer":round(diff,5),
    }


def ztf_pipeline_header_crossfield(band:str,a:dict,b:dict,ensemble:dict)->dict:
    """Never interpret PS1-anchored ZTF headers as an independent PS1 fit."""
    if band not in ("g","r"):
        raise ValueError("Only prior same-band g/r original pairs")
    a0=a.get("per_exposure_zTF_pipeline_header_values",{}).get("MAGZP")
    b0=b.get("per_exposure_zTF_pipeline_header_values",{}).get("MAGZP")
    if a0 is None or b0 is None:
        return {
            "status":"ORIGINAL_PIPELINE_PS1_ZEROPOINT_METADATA_UNAVAILABLE",
            "original_zTF_ps1_pipeline_header_delta_MAGZP_field609_minus_1605":None,
            "nominal_delta_inst_plus_pipeline_header_delta_zp":None,
            "direct_external_ps1_catalogue_crossmatch_performed":False,
            "color_corrected_AB_flux_calibration_performed":False,
        }
    delta=round(b0-a0,6)
    inst=ensemble.get("ensemble_median_native_mag_difference_b_minus_a")
    return {
        "status":"DESCRIPTIVE_ZTF_OWN_PS1_ANCHORED_PIPELINE_HEADER_COMPARISON",
        "original_zTF_ps1_pipeline_header_delta_MAGZP_field609_minus_1605":delta,
        "nominal_delta_inst_plus_pipeline_header_delta_zp":(
            round(delta+inst,6) if inst is not None else None),
        "instrumental_mags_and_pipeline_zeropoints_not_independent":True,
        "missing_PS1_color_terms_and_calibration_covariance":True,
        "direct_external_ps1_catalogue_crossmatch_performed":False,
        "color_corrected_AB_flux_calibration_performed":False,
        "physical_gaia_ztf_source_match_verified":False,
    }


def run_ft_tau_720_ps1_reference(seed:bytes,historic:dict,
                                 prior_oid:dict,prior_images:dict,*,
                                 native_fetch=None,
                                 science_fetch=None)->dict:
    """Original real survey four PSFcat + four FITS headers; no raw persistence."""
    from .v114_native_psfcat_association import fetch_native_psf_product
    from .v15_image_pixels import fetch_fits_cutout
    native_fetch=native_fetch or fetch_native_psf_product
    science_fetch=science_fetch or fetch_fits_cutout
    fixed,by_band=fixed_four_exposure_pairs(seed,historic,prior_oid,prior_images)
    per_band=[]
    for band in ("g","r"):
        native=[]
        headers=[]
        selection=[]
        qcs=[]
        for field in ("1605","609"):
            frame=by_band[band][field]
            sel=frame["selection"]
            state={
                "original_fixed_ztf_oid":sel["ztf_oid"],
                "original_field":field,
                "original_mjd":sel["original_mjd"],
                "original_gaia_target_in_reference_ensemble":False,
                "full_native_psfcat_original_hash_verified":False,
            }
            try:
                cat=original_native_catalogue_from_frozen_image(
                    frame,ra=fixed["seed_ra_deg"],dec=fixed["seed_dec_deg"],
                    native_fetch=native_fetch)
                q=qualifying_original_native_sources(
                    cat,ra0=fixed["seed_ra_deg"],dec0=fixed["seed_dec_deg"],
                    max_radius_arcsec=NEW_RADIUS_ARCSEC)
                state.update({
                    "full_native_psfcat_original_hash_verified":True,
                    "original_native_full_psfcat_sha256":cat["sha256"],
                    "n_original_catalogue_rows":q["n_catalogue_rows"],
                    "n_within_fixed_720arcsec":q["n_within_sky_radius"],
                    "n_original_within_15arcsec_fttau_target_exclusion":q["n_ft_tau_core_excluded"],
                    "n_clean_uncrowded_sources_selected_before_crossfield_matching":
                        q["n_good_uncrowded_reference_candidates"],
                })
                qcs.append(q)
            except ERRORS as exc:
                state["native_status"]="ORIGINAL_NATIVE_SOURCE_UNAVAILABLE_OR_SHA_MISMATCH"
                state["native_error_type"]=type(exc).__name__
            try:
                h=original_ztf_header_ps1_anchor(
                    frame,ra=fixed["seed_ra_deg"],dec=fixed["seed_dec_deg"],
                    science_fetch=science_fetch)
                state["original_science_header"]=h
            except ERRORS as exc:
                state["original_science_header"]={
                    "status":"ORIGINAL_SCIENCE_FITS_HEADER_UNAVAILABLE",
                    "error_type":type(exc).__name__,
                    "external_PS1_source_rows_queried":False,
                    "independent_absolute_zeropoint_calibration_performed":False,
                }
            selection.append(state)
        if len(qcs)==2:
            matches=original_crossfield_reference_pairs(*qcs)
            internal=internal_relative_offset_qc(matches)
            spatial=geometry_stratified_median_screen(matches)
        else:
            internal={
                "status":"ORIGINAL_SOURCE_ENSEMBLE_UNAVAILABLE",
                "instrumental_offset_internally_consistent":False,
                "ensemble_median_native_mag_difference_b_minus_a":None,
                "all_photometric_series_remain_unmerged":True,
            }
            spatial={"status":"ORIGINAL_SOURCE_ENSEMBLE_UNAVAILABLE",
                     "field_wide_spatially_uniform_photometry_established":False}
        h0=selection[0].get("original_science_header",{})
        h1=selection[1].get("original_science_header",{})
        cross=ztf_pipeline_header_crossfield(band,h0,h1,internal)
        # Widening a source catalogue changes error and color/selection
        # budget. This is not an independently calibrated science result.
        per_band.append({
            "band":band,
            "original_FT_TAU_two_fixed_fields":selection,
            "same_filter_preaudited_original_39_second_pair":True,
            "native_reference_ensemble_internal_only":internal,
            "inner_vs_outer_spatial_trend":spatial,
            "ZTF_own_PS1_anchored_FITS_header_comparison":cross,
            "internally_consistent_and_no_detected_large_spatial_gradient":bool(
                internal.get("instrumental_offset_internally_consistent",False)
                and spatial.get("status")=="SPATIAL_PROFILE_DESCRIPTIVELY_WITHIN_0P10_MAG"),
            "external_independent_PS1_catalogue_matches_verified":0,
            "physically_verified_ft_tau_gaia_ztf_source":False,
            "original_ztf_lightcurves_merged":False,
        })
    return {
        "phase":"R2_FTTAU_NEW_720_ARCSEC_ORIGINAL_NATIVE_ENSEMBLE_AND_ZTF_OWN_PS1_HEADER_PILOT",
        "predefined_study_technical_taurus_cohort_size":24,
        "ft_tau_original_ztf_oid_exposure_count":4,
        "new_original_telescope_observation_epochs_selected":0,
        "new_sky_radius_arcsec":NEW_RADIUS_ARCSEC,
        "prior_failed_sky_radius_arcsec":360,
        "prior_fixed_360arcsec_results_untouched":True,
        "n_original_full_native_ZTF_psfcat_SHA_matched":sum(
            x["full_native_psfcat_original_hash_verified"]
            for band in per_band for x in band["original_FT_TAU_two_fixed_fields"]),
        "n_original_science_FITS_header_PS1_pipeline_metadata_parsed":sum(
            x["original_science_header"].get("status")==
            "PS1_ANCHORED_ZTF_PIPELINE_HEADER_PARSED"
            for band in per_band for x in band["original_FT_TAU_two_fixed_fields"]),
        "n_bands_internally_consistent_magnitude_offset":sum(
            x["native_reference_ensemble_internal_only"].get(
                "instrumental_offset_internally_consistent",False)
            for x in per_band),
        "n_bands_internal_qc_and_descriptive_spatial_screen_pass":sum(
            x["internally_consistent_and_no_detected_large_spatial_gradient"]
            for x in per_band),
        "n_directly_crossmatched_independent_PS1_reference_sources":0,
        "n_independently_certified_absolute_photometric_zeropoints":0,
        "n_independently_confirmed_physical_Gaia_ZTF_matches":0,
        "n_ZTF_OID_lightcurves_merged":0,
        "n_intrinsic_FT_TAU_variability_or_companion_detections":0,
        "R2_physical_source_identity_completed":False,
        "original_R1_seed_sha256":hashlib.sha256(seed).hexdigest(),
        "bands":per_band,
        "limitations":[
            "This is an independently pre-registered 720-arcsec enlargement, not reanalysis of the previous 360-arcsec preregistered underpowered no-go.",
            "Even if at least 20 same-filter ZTF native references survive, split heldout QA and inner/outer spatial checks are not an independent calibration against Pan-STARRS1 source rows.",
            "ZTF science-header MAGZP and NMATCHES originate from the same ZTF PS1-anchored reduction, not an independently fitted external PS1 catalogue crossmatch.",
            "No per-reference original PS1 g/r colors, color-corrected AB flux uncertainty, Gaia source-level physical match, repeat-night stability or uniform detector calibration.",
            "No original ZTF OID lightcurve can be merged and no new FT Tau intrinsic variability, companion or Taurus membership claim follows.",
        ],
    }
