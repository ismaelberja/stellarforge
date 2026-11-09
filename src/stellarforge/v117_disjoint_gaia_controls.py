"""v1.17: truly disjoint candidate selection + shifted-sky positional null probes.

Disjoint from the *earlier Gaia candidate pilot* and masked source fits, NOT
necessarily disjoint from the native ZTF pipeline's own PSF-model training
stars (that training membership is not provided). No physical Gaia/ZTF source
identification, false-match probability, independent WCS precision or
astronomical discovery is inferred.

Select controls from a Gaia DR3 *independent wide-cone catalogue before
inspecting ZTF science pixels or their PSF residuals*, enforce original
reference/target-ID exclusion and 10" Gaia-neighbour isolation across the
entire returned catalogue, and cover sky quadrants where feasible.
"""
from __future__ import annotations

import math
import statistics
from typing import Any

import numpy as np

from .coordinates import angular_separation_arcsec, validate_icrs
from .v114_native_psfcat_association import _sep_arcsec_vectorized
from .v113_official_masks_psf import BAD_MASK_BITS
from .v18_gaia_references import GAIA_ROW_CAP

MAX_CONTROLS_PER_FIELD=5
SHIFTS_ARCSEC=((25.,0.),(-25.,0.),(0.,25.),(0.,-25.))
MIN_CONTROL_ISOLATION_ARCSEC=10.
MIN_TARGET_OFFSET_ARCSEC=40.
MAX_TARGET_OFFSET_ARCSEC=165.
MAX_SHIFTED_NULL_PROBES=20


def select_disjoint_holdout_controls(rows:list[dict],*,target_id:str,
                                     excluded_source_ids:set[str],
                                     max_controls:int=4)->dict:
    """Gaia-only deterministic spatial selection; no ZTF information consulted.

    The 'holdout' is from old Gaia-source candidate selection, *not* from
    the original survey pipeline's PSF building set.
    """
    if (not 1<=max_controls<=MAX_CONTROLS_PER_FIELD
        or len(rows)>=GAIA_ROW_CAP
        or not str(target_id).isdigit()
        or str(target_id) not in excluded_source_ids):
        raise ValueError("Unbounded or inconsistent Gaia holdout design")
    by_id={str(r["source_id"]):r for r in rows}
    if len(by_id)!=len(rows):
        raise ValueError("Gaia wide-cone catalogue has duplicate source IDs")
    target=by_id.get(str(target_id))
    if target is None:
        return {
            "status":"GAIA_TARGET_MISSING_FROM_WIDE_CONE",
            "n_gaia_wide_cone_sources":len(rows),
            "controls":[],
            "n_disjoint_controls_preselected":0,
            "native_ztf_psf_training_star_membership_known":False,
        }
    validate_icrs(float(target["ra"]),float(target["dec"]))
    original_ra=float(target["ra"])
    original_dec=float(target["dec"])
    rejection={
        "excluded_original_reference_or_target":0,
        "target_distance":0,"gaia_astrometric_quality":0,
        "brightness":0,"gaia_neighbour_isolation":0,
    }
    survivors=[]
    for item in rows:
        sid=str(item["source_id"])
        if sid in excluded_source_ids:
            rejection["excluded_original_reference_or_target"]+=1
            continue
        validate_icrs(float(item["ra"]),float(item["dec"]))
        sep=angular_separation_arcsec(
            original_ra,original_dec,float(item["ra"]),float(item["dec"]))
        if not MIN_TARGET_OFFSET_ARCSEC<=sep<=MAX_TARGET_OFFSET_ARCSEC:
            rejection["target_distance"]+=1
            continue
        g=item.get("g_mag")
        flux_snr=item.get("g_flux_snr")
        if (g is None or not 13<=float(g)<=18.5
            or flux_snr is None or float(flux_snr)<50):
            rejection["brightness"]+=1
            continue
        if (item.get("ruwe") is None or not .5<=float(item["ruwe"])<1.4
            or item.get("duplicated_source",True)
            or item.get("astrometric_params_solved") not in (31,95)
            or any(item.get(key) is None for key in (
                "pmra","pmdec","parallax",
                "ra_error_mas","dec_error_mas",
                "pmra_error_mas_yr","pmdec_error_mas_yr"))
            or max(float(item["ra_error_mas"]),float(item["dec_error_mas"]))>3
            or max(float(item["pmra_error_mas_yr"]),float(item["pmdec_error_mas_yr"]))>3):
            rejection["gaia_astrometric_quality"]+=1
            continue
        nearest=min((
            angular_separation_arcsec(float(item["ra"]),float(item["dec"]),
                                      float(other["ra"]),float(other["dec"]))
            for other in rows if str(other["source_id"])!=sid
        ),default=math.inf)
        if nearest<MIN_CONTROL_ISOLATION_ARCSEC:
            rejection["gaia_neighbour_isolation"]+=1
            continue
        dra=(float(item["ra"])-original_ra+180)%360-180
        east=dra*math.cos(math.radians(original_dec))
        north=float(item["dec"])-original_dec
        quadrant=int(east>=0)+2*int(north>=0)
        survivors.append({
            "source_id":sid,
            "gaia_dr3_ra_deg":round(float(item["ra"]),10),
            "gaia_dr3_dec_deg":round(float(item["dec"]),10),
            "gaia_dr3_g_mag":round(float(g),4),
            "gaia_dr3_ruwe":round(float(item["ruwe"]),4),
            "gaia_nearest_all_rows_neighbour_arcsec":round(nearest,4),
            "gaia_target_distance_arcsec":round(sep,4),
            "sky_quadrant":quadrant,
            "quality_selected_using_gaia_only":True,
            "excluded_from_v116_masked_fit_source_ids":True,
            "physical_gaia_ztf_source_identity_confirmed":False,
        })
    survivors.sort(key=lambda r:(
        abs(r["gaia_dr3_g_mag"]-15.5),
        abs(r["gaia_target_distance_arcsec"]-100),
        r["source_id"]))
    chosen=[]
    picked=set()
    # One per occupied sky quadrant first, then best remaining stars.
    for quadrant in range(4):
        candidate=next((r for r in survivors if r["sky_quadrant"]==quadrant),None)
        if candidate and len(chosen)<max_controls:
            chosen.append(candidate)
            picked.add(candidate["source_id"])
    for c in survivors:
        if len(chosen)>=max_controls:break
        if c["source_id"] not in picked:
            chosen.append(c);picked.add(c["source_id"])
    return {
        "status":("DISJOINT_GAIA_ONLY_CONTROL_SELECTION_READY" if chosen
                  else "NO_DISJOINT_GAIA_CONTROL_CANDIDATES"),
        "n_gaia_wide_cone_sources":len(rows),
        "n_quality_survivors_before_budget":len(survivors),
        "n_disjoint_controls_preselected":len(chosen),
        "n_occupied_quadrants":len({c["sky_quadrant"] for c in chosen}),
        "rejection_counts":rejection,
        "controls":chosen,
        "gaia_control_selection_independent_of_v116_pixel_residuals":True,
        "native_ztf_psf_training_star_membership_known":False,
        "stellar_sources_authenticated_by_ztf":False,
    }


def shifted_sky_null_probes(catalogue:dict,predictions:list[dict],*,
                           match_radius_arcsec:float=1.0)->dict:
    """Predefined ±25" RA/Dec offsets: descriptive shifted-position null hits.

    A shifted location can land on an actual sky source. The experiment
    probes incidental catalogue association density in the same CCD region;
    it does NOT estimate a calibrated Bayesian false-match probability.
    """
    if not 0.2<=match_radius_arcsec<=1 or not 1<=len(predictions)<=MAX_CONTROLS_PER_FIELD:
        raise ValueError("Unbounded shifted-position null design")
    if catalogue["status"]!="ORIGINAL_ZTF_PSF_CATALOGUE_PARSED_UNVERIFIED":
        return {
            "status":"NATIVE_PSF_CATALOGUE_UNAVAILABLE_FOR_SHIFTED_NULL",
            "n_shifted_sky_probes":0,"n_nearest_any_psf_source_within_radius":0,
            "n_profile_qualified_shifted_hits":0,
            "calibrated_source_false_association_probability":False,
        }
    rows=catalogue["rows"]
    ra=np.asarray(rows["ra"],dtype=float)
    dec=np.asarray(rows["dec"],dtype=float)
    results=[]
    for p in predictions:
        try:
            pr=float(p["geocentric_parallax_adjusted_ra_deg"])
            pd=float(p["geocentric_parallax_adjusted_dec_deg"])
        except (TypeError,ValueError,KeyError) as exc:
            raise ValueError("Invalid Gaia source prediction for sky null") from exc
        validate_icrs(pr,pd)
        for east,north in SHIFTS_ARCSEC:
            shifted_dec=pd+north/3600
            cosdec=math.cos(math.radians(pd))
            if abs(cosdec)<.05:
                raise ValueError("Near-pole shifted ICRS reference unsupported")
            shifted_ra=(pr+east/(3600*cosdec))%360
            if not -90<shifted_dec<90:
                raise ValueError("Sky shifted pole crossing unsupported")
            sep=_sep_arcsec_vectorized(ra,dec,shifted_ra,shifted_dec)
            if len(sep)==0:
                smallest=math.inf
                closest=None
            else:
                closest=int(np.argmin(sep))
                smallest=float(sep[closest])
            hit=smallest<=match_radius_arcsec
            psf_ok=False
            if hit:
                flags=int(rows["flags"][closest])
                chi=float(rows["chi"][closest])
                sharp=float(rows["sharp"][closest])
                snr=float(rows["snr"][closest])
                flux=float(rows["flux"][closest])
                sigflux=float(rows["sigflux"][closest])
                psf_ok=bool(
                    0<=flags and flags&BAD_MASK_BITS==0
                    and 0.5<=chi<=1.5 and -0.5<=sharp<=0.5
                    and snr>=5 and flux>0 and sigflux>0)
            results.append({
                "gaia_source_id":str(p["source_id"]),
                "shift_east_arcsec":east,
                "shift_north_arcsec":north,
                "native_psfcat_source_within_radius":bool(hit),
                "native_psfcat_profile_qualified_shifted_hit":psf_ok,
                "nearest_native_source_arcsec":
                    round(smallest,5) if math.isfinite(smallest) else None,
            })
    if len(results)>MAX_SHIFTED_NULL_PROBES:
        raise ValueError("Too many shifted-sky null probes")
    return {
        "status":"SHIFTED_SKY_CATALOGUE_DENSITY_PROBES_COMPLETED",
        "n_shifted_sky_probes":len(results),
        "n_nearest_any_psf_source_within_radius":sum(
            x["native_psfcat_source_within_radius"] for x in results),
        "n_profile_qualified_shifted_hits":sum(
            x["native_psfcat_profile_qualified_shifted_hit"] for x in results),
        "shift_offsets_are_fixed_25_arcsec_not_independent_random_sky":True,
        "shifted_offsets_may_contain_actual_unrelated_stars":True,
        "calibrated_source_false_association_probability":False,
        "probes":results,
    }


def compare_disjoint_holdouts(masked_fit_records:list[dict],
                              *,min_distinct_controls:int=3)->dict:
    """Descriptive distinct-star controls, without asserting absolute calibration."""
    if not 2<=min_distinct_controls<=5 or len(masked_fit_records)>40:
        raise ValueError("Unbounded source control comparison")
    unique={}
    for row in masked_fit_records:
        sid=str(row["gaia_source_id"])
        if not sid.isdigit() or sid in unique:
            # One per source per exposure required, by construction.
            raise ValueError("Duplicated or invalid holdout Gaia candidate ID")
        if row.get("originally_used_in_v116",True):
            raise ValueError("Control was in prior source selection")
        unique[sid]=row
    eligible=[r for r in unique.values() if r.get("fit_completed") is True
              and r.get("rms_over_sky_proxy") is not None
              and math.isfinite(float(r["rms_over_sky_proxy"]))
              and float(r["rms_over_sky_proxy"])>0]
    valid=len(eligible)>=min_distinct_controls
    return {
        "status":("DISTINCT_GAIA_CONTROL_DESCRIPTIVE_SAMPLE_READY"
                  if valid else
                  "INSUFFICIENT_DISTINCT_GAIA_CONTROL_IMAGE_FITS"),
        "n_distinct_candidate_holdouts_selected":len(unique),
        "n_distinct_candidate_holdouts_with_original_masked_pixel_fit":len(eligible),
        "median_same_image_pixel_holdout_rms_over_sky_mad_proxy":(
            round(statistics.median(float(x["rms_over_sky_proxy"]) for x in eligible),5)
            if valid else None),
        "n_original_pixel_residual_profiles_screen_passed":sum(
            bool(r.get("residual_quality_passed")) for r in eligible),
        "n_distinct_source_ids_not_used_in_original_v116_fits":len(unique),
        "native_psf_lookup_training_sample_exclusion_proven":False,
        "independent_external_instrument_psf_wcs_error_calibration_completed":False,
        "astrophysical_gaia_ztf_source_identities_confirmed":0,
    }
