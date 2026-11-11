"""Offline safeguards for independently preregistered FT Tau 720" pilot."""
from __future__ import annotations

import io
import json
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest
from astropy.io import fits
from astropy.wcs import WCS

from stellarforge.r2_fttau_crossfield_instrumental_ensemble import (
    qualifying_original_native_sources,
)
from stellarforge.r2_fttau_720_ps1_anchor import (
    NEW_RADIUS_ARCSEC,
    SPATIAL_INNER_BOUND_ARCSEC,
    original_ztf_header_ps1_anchor,
    geometry_stratified_median_screen,
    ztf_pipeline_header_crossfield,
    run_ft_tau_720_ps1_reference,
)
ROOT=Path(__file__).resolve().parents[1]
SEED=(ROOT/"data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv").read_bytes()
HIST=json.loads((ROOT/"data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json").read_text("utf8"))
OID=json.loads((ROOT/"reports/taurus_variability_r2/REAL_ALTERNATIVE_ZTF_OID_ORIGINAL_RUN_RECEIPT.json").read_text("utf8"))
PRIOR=json.loads((ROOT/"reports/taurus_variability_r2/FT_TAU_TWO_ORIGINAL_ZTF_FIELDS_GR_FITS_MASK_PSF_DERIVED_NO_RAW.json").read_text("utf8"))
RA0=65.913324
DEC0=24.937195


def source_catalogue(x,y):
    x=np.asarray(x,dtype=float)
    y=np.asarray(y,dtype=float)
    n=len(x)
    mag=np.full(n,-10.,dtype=float)
    flux=10**(-mag/2.5)
    return {"status":"ORIGINAL_ZTF_PSF_CATALOGUE_PARSED_UNVERIFIED",
        "sha256":"a"*64,"n_native_psf_catalogue_rows":n,
        "rows":{
            "ra":RA0+x/(3600*np.cos(np.deg2rad(DEC0))),
            "dec":DEC0+y/3600,
            "sourceid":np.arange(1,n+1,dtype=int),
            "flux":flux,"sigflux":flux/50,
            "mag":mag,"sigmag":np.full(n,.02),
            "snr":np.full(n,50.),"chi":np.ones(n),
            "sharp":np.zeros(n),"flags":np.zeros(n,dtype=int)}}


def fake_original_cutout(*,magzp=26.4, missing=None, ncal=500,
                        infobits=0, magzprms=.02):
    w=WCS(naxis=2)
    w.wcs.crpix=[24.,24.]
    w.wcs.cdelt=[-.00028,.00028]
    w.wcs.crval=[RA0,DEC0]
    w.wcs.ctype=["RA---TAN","DEC--TAN"]
    h=w.to_header()
    h["MAGZP"]=magzp
    h["MAGZPUNC"]=.008
    h["MAGZPRMS"]=magzprms
    h["CLRCOEFF"]=.02
    h["CLRCOUNC"]=.003
    h["NMATCHES"]=ncal
    h["INFOBITS"]=infobits
    if missing:
        del h[missing]
    return fits.PrimaryHDU(np.ones((48,48),dtype=np.float32),header=h).writeto(
        io.BytesIO(),overwrite=True)


def original_fits_bytes(**kwargs):
    w=WCS(naxis=2)
    w.wcs.crpix=[24.,24.]
    w.wcs.cdelt=[-.00028,.00028]
    w.wcs.crval=[RA0,DEC0]
    w.wcs.ctype=["RA---TAN","DEC--TAN"]
    h=w.to_header()
    h["MAGZP"]=kwargs.get("magzp",26.4)
    h["MAGZPUNC"]=.008
    h["MAGZPRMS"]=kwargs.get("magzprms",.02)
    h["CLRCOEFF"]=.02
    h["CLRCOUNC"]=.003
    h["NMATCHES"]=kwargs.get("ncal",400)
    h["INFOBITS"]=kwargs.get("infobits",0)
    if kwargs.get("missing"):del h[kwargs["missing"]]
    file=io.BytesIO()
    fits.PrimaryHDU(np.ones((48,48),dtype=np.float32),header=h).writeto(file)
    return file.getvalue()


def test_new_radius_is_fixed_opt_in_and_does_not_mutate_prior_360_source_sample():
    assert NEW_RADIUS_ARCSEC==720.
    assert SPATIAL_INNER_BOUND_ARCSEC==360.
    c=source_catalogue([70,180,440,600,810],[50,50,50,50,50])
    old=qualifying_original_native_sources(c,ra0=RA0,dec0=DEC0)
    new=qualifying_original_native_sources(
        c,ra0=RA0,dec0=DEC0,max_radius_arcsec=720.)
    assert old["n_good_uncrowded_reference_candidates"]==2
    assert new["n_good_uncrowded_reference_candidates"]==4
    with pytest.raises(ValueError):
        qualifying_original_native_sources(c,ra0=RA0,dec0=DEC0,max_radius_arcsec=1000.)


def test_real_prior_four_original_exposure_selection_remains_immutable():
    assert len(PRIOR["original_fits_mask_native_psf_exposure_results"])==4
    assert {x["selection"]["ztf_oid"] for x in PRIOR[
        "original_fits_mask_native_psf_exposure_results"]}=={
        "1605115300003377","609108400001155",
        "1605215300005161","609208400001969"}


def test_spatial_profile_passes_only_when_both_annuli_have_enough_sources():
    xx=np.array([90.,120.,150.,180.,210.,240.,450.,480.,510.,540.,570.,600.])
    diff=np.array([.20,.20,.21,.19,.20,.21,.24,.25,.24,.25,.26,.24])
    m={"match_xy":np.column_stack([xx,np.zeros(len(xx))]),
       "delta_native_instrumental_mag_b_minus_a":diff}
    r=geometry_stratified_median_screen(m)
    assert r["status"]=="SPATIAL_PROFILE_DESCRIPTIVELY_WITHIN_0P10_MAG"
    assert r["n_old_inner_360arcsec_reference_pairs"]==6
    assert r["n_new_outer_360_to_720arcsec_reference_pairs"]==6
    assert r["field_wide_spatially_uniform_photometry_established"] is False
    m["delta_native_instrumental_mag_b_minus_a"][6:]+=.20
    assert geometry_stratified_median_screen(m)["status"]=="SPATIAL_GRADIENT_REVIEW"
    m["match_xy"]=m["match_xy"][:9]
    m["delta_native_instrumental_mag_b_minus_a"]=m[
        "delta_native_instrumental_mag_b_minus_a"][:9]
    assert geometry_stratified_median_screen(m)["status"]=="SPATIAL_PROFILE_UNDERPOWERED"


def test_genuine_prior_image_source_filename_required_for_archive_header():
    frame=PRIOR["original_fits_mask_native_psf_exposure_results"][0]
    r=original_ztf_header_ps1_anchor(
        frame,ra=RA0,dec=DEC0,science_fetch=lambda *args,**kwargs:original_fits_bytes())
    assert r["status"]=="PS1_ANCHORED_ZTF_PIPELINE_HEADER_PARSED"
    assert r["per_exposure_zTF_pipeline_header_values"]["MAGZP"]==26.4
    assert r["original_ps1_pipeline_header_NMATCHES"]==400
    assert r["public_ZTF_partial_ps1_match_and_zp_rms_screen_pass"] is True
    assert r["external_PS1_source_rows_queried"] is False
    assert r["independent_absolute_zeropoint_calibration_performed"] is False
    altered=json.loads(json.dumps(frame))
    altered["original_science_product_identifier"]="ztf_wrong_sciimg.fits"
    with pytest.raises(ValueError,match="filename"):
        original_ztf_header_ps1_anchor(
            altered,ra=RA0,dec=DEC0,science_fetch=lambda *args,**kwargs:original_fits_bytes())


def test_missing_calibration_header_never_fabricates_ps1_reference_solution():
    frame=PRIOR["original_fits_mask_native_psf_exposure_results"][0]
    r=original_ztf_header_ps1_anchor(
        frame,ra=RA0,dec=DEC0,science_fetch=lambda *a,**k:original_fits_bytes(missing="MAGZP"))
    assert r["status"]=="ORIGINAL_FITS_PS1_PIPELINE_HEADER_INCOMPLETE"
    assert r["per_exposure_zTF_pipeline_header_values"]["MAGZP"] is None
    assert r["public_ZTF_partial_ps1_match_and_zp_rms_screen_pass"] is False


def test_ztf_pipeline_ps1_magnitude_headers_are_not_independent_standard_stars():
    a={"per_exposure_zTF_pipeline_header_values":{"MAGZP":26.1}}
    b={"per_exposure_zTF_pipeline_header_values":{"MAGZP":26.5}}
    e={"ensemble_median_native_mag_difference_b_minus_a":-.41}
    x=ztf_pipeline_header_crossfield("g",a,b,e)
    assert x["original_zTF_ps1_pipeline_header_delta_MAGZP_field609_minus_1605"]==.4
    assert x["nominal_delta_inst_plus_pipeline_header_delta_zp"]==-.01
    assert x["direct_external_ps1_catalogue_crossmatch_performed"] is False
    assert x["color_corrected_AB_flux_calibration_performed"] is False
    assert x["physical_gaia_ztf_source_match_verified"] is False
    e["ensemble_median_native_mag_difference_b_minus_a"]=None
    assert ztf_pipeline_header_crossfield("g",a,b,e)[
        "nominal_delta_inst_plus_pipeline_header_delta_zp"] is None
    with pytest.raises(ValueError):
        ztf_pipeline_header_crossfield("i",a,b,e)


def test_full_720_pipeline_missing_original_catalogue_reports_no_false_source_detection():
    # Synthetic isolation: emulate archive download errors for all four
    # native source catalogues; still reads only prior four frozen fields.
    with patch("stellarforge.r2_fttau_720_ps1_anchor.original_native_catalogue_from_frozen_image",
               side_effect=ValueError("synthetic original SHA mismatch")):
        d=run_ft_tau_720_ps1_reference(
            SEED,HIST,OID,PRIOR,science_fetch=lambda *a,**k:original_fits_bytes())
    assert d["n_original_full_native_ZTF_psfcat_SHA_matched"]==0
    assert d["n_original_science_FITS_header_PS1_pipeline_metadata_parsed"]==4
    assert d["n_bands_internally_consistent_magnitude_offset"]==0
    assert d["n_independently_confirmed_physical_Gaia_ZTF_matches"]==0
    assert d["n_ZTF_OID_lightcurves_merged"]==0
    assert d["R2_physical_source_identity_completed"] is False
    assert all(x["native_reference_ensemble_internal_only"]["status"]==
               "ORIGINAL_SOURCE_ENSEMBLE_UNAVAILABLE" for x in d["bands"])
