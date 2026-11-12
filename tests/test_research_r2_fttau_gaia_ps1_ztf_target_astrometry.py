"""Falsifiable R2 source-level FT Tau astrometry controls (synthetic only)."""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path

import numpy as np
import pytest

from stellarforge.r2_fttau_gaia_ps1_target_astrometry import (
    full_original_ps1_near_target, original_reference_triple_astrometry,
    heldout_astrometric_reference_offsets, original_target_native_candidate,
    target_differential_reference_summary,
    run_ft_tau_gaia_ps1_ztf_target_astrometry,
)

ROOT=Path(__file__).resolve().parents[1]
SEED=(ROOT/"data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv").read_bytes()
HIST=json.loads((ROOT/"data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json").read_text("utf8"))
OID=json.loads((ROOT/"reports/taurus_variability_r2/REAL_ALTERNATIVE_ZTF_OID_ORIGINAL_RUN_RECEIPT.json").read_text("utf8"))
IMAGES=json.loads((ROOT/"reports/taurus_variability_r2/FT_TAU_TWO_ORIGINAL_ZTF_FIELDS_GR_FITS_MASK_PSF_DERIVED_NO_RAW.json").read_text("utf8"))
PRIOR720=json.loads((ROOT/"reports/taurus_variability_r2/FTTAU_720_REAL_NATIVE_ENSEMBLE_ZTF_PS1_PIPELINE_HEADER_NO_RAW.json").read_text("utf8"))
PREV_EXTERNAL=json.loads((ROOT/"reports/taurus_variability_r2/FTTAU_REAL_ORIGINAL_MAST_PS1_DR2_EXTERNAL_SOURCE_COLOR_PILOT_NO_RAW.json").read_text("utf8"))
RA0=65.913324
DEC0=24.937195


def test_source_reference_motion_screen_has_separate_train_and_heldout_star_ids():
    n=60
    x=np.linspace(-290,290,n)
    y=140*np.sin(np.arange(n))
    ps1=np.column_stack((x,y))
    ztf_a=ps1+np.array([.055,-.027])
    ztf_b=ps1+np.array([-.023,.042])
    # Independent reference stars have unrelated psf source IDs across fields.
    refa={"xy":ztf_a,"id":np.arange(100,100+n)}
    refb={"xy":ztf_b,"id":np.arange(300,300+n)}
    external={"xy":ps1,"id":np.array([str(100000000000+i) for i in range(n)])}
    triple=original_reference_triple_astrometry(refa,refb,external)
    assert triple["n_unique_source_triplets"]==n
    assert len(set(triple["ps1_ids"]))==n
    r=heldout_astrometric_reference_offsets(triple)
    assert r["both_fields_heldout_internal_geometry_pass"] is True
    assert r["n_training_reference_stars"]>=10
    assert r["n_heldout_reference_stars"]>=8
    assert r["fields"]["1605"][
        "median_original_ztf_minus_ps1_reference_training_east_arcsec"]==pytest.approx(.055,abs=.0001)
    assert r["fields"]["609"][
        "median_original_ztf_minus_ps1_reference_training_north_arcsec"]==pytest.approx(.042,abs=.0001)
    assert r["full_instrument_wcs_uncertainty_calibrated"] is False
    assert r["target_gaia_ztf_physical_identity_authenticated"] is False


def test_nonunique_or_inconsistent_original_catalogue_references_fail_closed():
    x=np.linspace(-260,260,30)
    refa={"xy":np.column_stack((x,np.zeros_like(x)))}
    refb={"xy":np.column_stack((x+.04,np.full_like(x,.05)))}
    ext={"xy":np.column_stack((x,np.zeros_like(x))),
         "id":np.array([str(i) for i in range(30)])}
    triples=original_reference_triple_astrometry(refa,refb,ext)
    assert triples["n_unique_source_triplets"]==30
    noisy={**triples,"field_609_xy_arcsec":triples[
        "field_609_xy_arcsec"].copy()}
    noisy["field_609_xy_arcsec"][:,0]+=np.array([0,.2,-.2]*10)
    result=heldout_astrometric_reference_offsets(noisy)
    assert result["both_fields_heldout_internal_geometry_pass"] is False
    assert result["status"].startswith("NO_GO_")
    under={**triples,"n_unique_source_triplets":10}
    assert heldout_astrometric_reference_offsets(under)["status"].startswith("NO_GO_")


def test_native_target_nearest_PSF_quality_and_close_second_source_cannot_prove_identity():
    # Positions differ by 0.03, 1.8, 6 arcsec around predicted Gaia.
    predicted={"geocentric_parallax_adjusted_ra_deg":RA0,
               "geocentric_parallax_adjusted_dec_deg":DEC0}
    x=np.array([.03,1.8,6.])
    y=np.array([.04,0.,0.])
    r={"ra":RA0+x/(3600*np.cos(np.deg2rad(DEC0))),
       "dec":DEC0+y/3600,
       "flags":np.array([0,0,0],dtype=int),
       "snr":np.array([50.,40.,30.]),
       "flux":np.array([5000.,4000.,2000.]),
       "sigflux":np.array([100.,100.,100.]),
       "chi":np.ones(3),"sharp":np.zeros(3)}
    cat={"status":"ORIGINAL_ZTF_PSF_CATALOGUE_PARSED_UNVERIFIED","rows":r}
    q=original_target_native_candidate(cat,predicted)
    assert q["status"]=="PROVISIONAL_GAIA_NEAREST_ZTF_PSF_SOURCE_GEOMETRY_PASS"
    assert q["n_original_native_psf_sources_within_2arcsec"]==2
    assert q["nearest_original_native_source_to_predicted_Gaia_arcsec"]==pytest.approx(.05,abs=.00001)
    assert q["second_nearest_original_native_source_arcsec"]==pytest.approx(1.8,abs=.00001)
    assert q["confirmed_physical_gaia_ztf_target"] is False
    r["ra"][1]=RA0+.6/(3600*np.cos(np.deg2rad(DEC0)))
    bad=original_target_native_candidate(cat,predicted)
    assert bad["status"]=="TARGET_PSF_SOURCE_AMBIGUOUS_OR_QUALITY_REVIEW"
    r["ra"][1]=RA0+1.8/(3600*np.cos(np.deg2rad(DEC0)))
    r["flags"][0]=1
    flagged=original_target_native_candidate(cat,predicted)
    assert flagged["selected_nearest_original_native_PSF_quality_pass"] is False


def test_reference_corrected_target_offset_never_establishes_physical_match():
    q={
        "status":"PROVISIONAL_GAIA_NEAREST_ZTF_PSF_SOURCE_GEOMETRY_PASS",
        "original_native_minus_propagated_gaia_east_arcsec":.065,
        "original_native_minus_propagated_gaia_north_arcsec":-.023,
    }
    good={
        "both_fields_heldout_internal_geometry_pass":True,
        "fields":{"1605":{
            "heldout_reference_geometry_internal_qc_pass":True,
            "median_original_ztf_minus_ps1_reference_training_east_arcsec":.055,
            "median_original_ztf_minus_ps1_reference_training_north_arcsec":-.020,
        }},
    }
    result=target_differential_reference_summary(q,good,"1605")
    assert result["external_reference_adjusted_target_east_arcsec"]==pytest.approx(.01)
    assert result["external_reference_adjusted_target_north_arcsec"]==pytest.approx(-.003)
    assert result["source_physical_gaia_ztf_identity_confirmed"] is False
    assert result["independent_instrument_wcs_solution"] is False
    assert target_differential_reference_summary(
        {**q,"status":"TARGET_PSF_SOURCE_AMBIGUOUS_OR_QUALITY_REVIEW"},
        good,"1605")["external_reference_adjusted_target_east_arcsec"] is None


def test_all_mean_ps1_positions_are_checked_near_target_including_bad_reference_sources():
    # Two original PS1 sources near target, one third far outside 3".
    cols=("objID","raMean","decMean")
    stream=io.StringIO()
    w=csv.DictWriter(stream,fieldnames=cols,lineterminator="\n")
    w.writeheader()
    for i,x in enumerate((.18,2.2,20.)):
        w.writerow({"objID":str(100000000+i),
                    "raMean":RA0+x/(3600*np.cos(np.deg2rad(DEC0))),
                    "decMean":DEC0})
    raw=stream.getvalue().encode()
    gaia={"ra":RA0,"dec":DEC0}
    pred={"geocentric_parallax_adjusted_ra_deg":RA0,
          "geocentric_parallax_adjusted_dec_deg":DEC0}
    original=full_original_ps1_near_target(raw,gaia,{
        "g":{"1605":pred,"609":pred},"r":{"1605":pred,"609":pred}
    })
    q=original["original_target_neighborhood"]["gaia_J2016_reference_epoch"]
    assert q["n_original_ps1_sources_within_1arcsec"]==1
    assert q["n_original_ps1_sources_within_3arcsec"]==2
    assert q["nearest_original_ps1_mean_position_offset_arcsec"]==pytest.approx(.18,abs=.00001)
    assert q["ps1_astrometric_epoch_and_source_pm_unknown"] is True
    assert original["independent_catalogue_source_ambiguity_excluded"] is False


def test_original_gaia_ps1_native_service_errors_never_become_stellar_nondetection():
    def unavailable(*args,**kwargs):
        raise TimeoutError("Synthetic archive outage, not astronomical nondetection")
    data=run_ft_tau_gaia_ps1_ztf_target_astrometry(
        SEED,HIST,OID,IMAGES,PRIOR720,PREV_EXTERNAL,
        gaia_fetch=unavailable,ps1_fetch=unavailable,native_fetch=unavailable)
    assert data["n_original_gaia_5p_records_verified"]==0
    assert data["original_external_PS1_response_status"]==(
        "ORIGINAL_MAST_PS1_UNAVAILABLE_OR_INVALID")
    assert data["n_original_native_ztf_PSFcat_SHA_verified"]==0
    assert data["n_original_target_exposures_with_provisional_native_source_candidate"]==0
    assert data["n_confirmed_physical_gaia_to_ztf_ft_tau_source_identities"]==0
    assert data["n_zTF_ft_tau_OID_lightcurves_merged"]==0
    assert data["scientific_R2_full_physical_source_identity_completed"] is False


def test_new_valid_independent_MAST_snapshot_reports_changed_sha_not_same_source_version():
    from stellarforge.r2_fttau_external_ps1 import PS1_COLUMNS

    content=io.StringIO()
    w=csv.DictWriter(content,fieldnames=PS1_COLUMNS,lineterminator="\n")
    w.writeheader()
    for i in range(30):
        east=35.0+10*(i%10)
        north=-40.+40*(i//10)
        g=15.+.05*i
        w.writerow({
            "objID":str(12345000000+i),
            "raMean":RA0+east/(3600*np.cos(np.deg2rad(DEC0))),
            "decMean":DEC0+north/3600,
            "nDetections":10,"ng":6,"nr":5,
            "gMeanPSFMag":g,"gMeanPSFMagErr":.02,
            "rMeanPSFMag":g-.7,"rMeanPSFMagErr":.02,
        })
    ps1_raw=content.getvalue().encode()
    def unavailable(*a,**k):
        raise TimeoutError("Synthetic offline GAIA/ZTF outages")
    data=run_ft_tau_gaia_ps1_ztf_target_astrometry(
        SEED,HIST,OID,IMAGES,PRIOR720,PREV_EXTERNAL,
        gaia_fetch=unavailable,
        ps1_fetch=lambda *a,**k:ps1_raw,
        native_fetch=unavailable)
    assert data["original_external_PS1_response_status"]==(
        "COMPLETE_ORIGINAL_MAST_PS1_RESPONSE_SHA_CHANGED_REVIEW")
    assert data["original_external_PS1_sha_equal_previous_snapshot"] is False
    assert data["n_original_PS1_mean_rows_valid"]==30
    assert data["n_original_native_ztf_PSFcat_SHA_verified"]==0
    assert data["n_confirmed_physical_gaia_to_ztf_ft_tau_source_identities"]==0
    assert data["n_zTF_ft_tau_OID_lightcurves_merged"]==0


def test_changes_to_previous_2026_original_source_evidence_not_accepted():
    altered=json.loads(json.dumps(PREV_EXTERNAL))
    altered["n_same_band_PanSTARRS_source_level_internal_pilot_passes"]=0
    with pytest.raises(ValueError,match="not frozen"):
        run_ft_tau_gaia_ps1_ztf_target_astrometry(
            SEED,HIST,OID,IMAGES,PRIOR720,altered,
            gaia_fetch=lambda *a,**k:b"not original",
            ps1_fetch=lambda *a,**k:b"not original",
            native_fetch=lambda *a,**k:b"not original")
