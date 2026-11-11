"""Offline safeguards for original FT Tau native ZTF cross-field instrumental mags.

All input is synthetic for math tests; authentic archive run is separate.
"""
import json
from pathlib import Path

import numpy as np
import pytest

from stellarforge.r2_fttau_crossfield_instrumental_ensemble import (
    fixed_four_exposure_pairs, qualifying_original_native_sources,
    original_crossfield_reference_pairs, internal_relative_offset_qc,
    MIN_PAIR_REFS, original_native_catalogue_from_frozen_image,
)

ROOT=Path(__file__).resolve().parents[1]
SEED=(ROOT/"data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv").read_bytes()
HIST=json.loads((ROOT/"data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json").read_text("utf8"))
OID=json.loads((ROOT/"reports/taurus_variability_r2/REAL_ALTERNATIVE_ZTF_OID_ORIGINAL_RUN_RECEIPT.json").read_text("utf8"))
PRIOR=json.loads((ROOT/"reports/taurus_variability_r2/FT_TAU_TWO_ORIGINAL_ZTF_FIELDS_GR_FITS_MASK_PSF_DERIVED_NO_RAW.json").read_text("utf8"))
RA0=65.913324
DEC0=24.937195


def fake_native_catalogue(x,y,*,shift_mag=0.,offset_ra=0.,bad_index=None):
    x=np.asarray(x,dtype=float)
    y=np.asarray(y,dtype=float)
    n=len(x)
    # Actual native PSFcat mag = -2.5 log10(DN flux).
    # Instrumental offsets are by construction unrelated to sky RA/Dec.
    base_mag=-10.2-.01*np.arange(n)%1.2
    mag=base_mag+shift_mag
    flux=10**(-mag/2.5)
    flags=np.zeros(n,dtype=np.int32)
    if bad_index is not None:
        flags[bad_index]=1  # ZTF BAD_MASK_BITS includes bit 0; bit 15 is not in this QA veto
    return {
        "status":"ORIGINAL_ZTF_PSF_CATALOGUE_PARSED_UNVERIFIED",
        "sha256":"a"*64,
        "n_native_psf_catalogue_rows":n,
        "rows":{
            "ra":RA0+(x+offset_ra)/(3600*np.cos(np.deg2rad(DEC0))),
            "dec":DEC0+y/3600,
            "sourceid":np.arange(1,n+1,dtype=np.int64),
            "flux":flux,
            "sigflux":flux/50,
            "mag":mag,
            "sigmag":np.full(n,.022),
            "snr":np.full(n,50.),
            "chi":np.full(n,1.),
            "sharp":np.zeros(n),
            "flags":flags,
        },
    }


def synthetic_ensemble(n=50,*,delta=.21,scatter=.02):
    # Geometrically distinct reference sources, excluding target <15 arcsec.
    x=np.linspace(-320,320,n)
    y=np.sin(np.linspace(0,7,n))*100
    aa=fake_native_catalogue(x,y)
    bb=fake_native_catalogue(x,y,offset_ra=.08,shift_mag=delta)
    bb["rows"]["mag"]+=np.sin(np.arange(n)*1.4)*scatter
    bb["rows"]["flux"]=10**(-bb["rows"]["mag"]/2.5)
    a=qualifying_original_native_sources(aa,ra0=RA0,dec0=DEC0)
    b=qualifying_original_native_sources(bb,ra0=RA0,dec0=DEC0)
    return original_crossfield_reference_pairs(a,b)


def test_real_previous_four_original_fit_sources_and_field_data_frozen():
    fixed,frames=fixed_four_exposure_pairs(SEED,HIST,OID,PRIOR)
    assert fixed["gaia_id"]=="149623711269425408"
    assert set(frames)=={"g","r"}
    assert all(set(v)=={"1605","609"} for v in frames.values())
    assert frames["g"]["1605"]["selection"]["original_mjd"]==58806.385197
    assert frames["g"]["609"]["selection"]["original_mjd"]==58806.385648
    assert frames["r"]["1605"]["selection"]["original_mjd"]==58425.306065
    assert frames["r"]["609"]["selection"]["original_mjd"]==58425.306516


@pytest.mark.parametrize("tamper",["missing","additional","source","bad_source","oid","night","sha"])
def test_real_previous_original_source_evidence_cannot_be_cherry_picked(tamper):
    d=json.loads(json.dumps(PRIOR))
    if tamper=="missing":d["original_fits_mask_native_psf_exposure_results"].pop()
    if tamper=="additional":
        d["original_fits_mask_native_psf_exposure_results"].append(
            d["original_fits_mask_native_psf_exposure_results"][0])
    if tamper=="source":
        d["n_independently_verified_ft_gaia_ztf_physical_crossmatches"]=1
    if tamper=="bad_source":
        d["original_fits_mask_native_psf_exposure_results"][0][
            "all_three_instrument_source_checks_pass"]=False
    if tamper=="oid":
        d["original_fits_mask_native_psf_exposure_results"][0]["selection"]["ztf_oid"]="other"
    if tamper=="night":
        d["crossfield_same_filter_pairs"][0]["selection_mjd_gap_days"]=5
    if tamper=="sha":
        d["original_fits_mask_native_psf_exposure_results"][0]["native_full_catalogue_sha256"]=""
    with pytest.raises(ValueError):
        fixed_four_exposure_pairs(SEED,HIST,OID,d)


def test_native_psfcat_source_quality_crowding_and_target_exclusion():
    # Target near center is explicitly excluded; 3 arcsec pair is
    # borderline crowded and rejects both; source with flags rejected.
    x=[0,30,32,95,150,220,301]
    y=[0,0,0,0,0,0,0]
    c=fake_native_catalogue(x,y,bad_index=5)
    p=qualifying_original_native_sources(c,ra0=RA0,dec0=DEC0)
    assert p["n_catalogue_rows"]==7
    assert p["n_ft_tau_core_excluded"]==1
    assert p["n_good_uncrowded_reference_candidates"]==3
    assert all(np.linalg.norm(point)>15 for point in p["xy"])
    assert all(np.isfinite(p["mag"]))


def test_synthetic_two_original_native_catalogues_reciprocal_matches_and_offset():
    m=synthetic_ensemble(n=55,delta=.21,scatter=.015)
    assert m["n_unique_geometric_pairs"]>=MIN_PAIR_REFS
    result=internal_relative_offset_qc(m)
    assert result["instrumental_offset_internally_consistent"] is True
    assert result["ensemble_median_native_mag_difference_b_minus_a"]==pytest.approx(.21,abs=.03)
    assert abs(result["heldout_median_relative_offset_mag"])<.05
    assert result["n_training_references"]>=10
    assert result["n_validation_references"]>=8
    assert result["independent_absolute_photometric_calibration"] is False
    assert result["validated_gaia_ztf_physical_source_identity"] is False
    assert result["all_photometric_series_remain_unmerged"] is True


def test_no_reciprocal_sources_underpowered_never_prove_no_ztf_star():
    a=fake_native_catalogue([40,75],[40,75])
    b=fake_native_catalogue([-70,-100],[40,75])
    m=original_crossfield_reference_pairs(
        qualifying_original_native_sources(a,ra0=RA0,dec0=DEC0),
        qualifying_original_native_sources(b,ra0=RA0,dec0=DEC0))
    assert m["n_reciprocal_sky_matches"]==0
    result=internal_relative_offset_qc(m)
    assert result["instrumental_offset_internally_consistent"] is False
    assert result["ensemble_median_native_mag_difference_b_minus_a"] is None


def test_large_scatter_safely_blocks_relative_instrumental_calibration():
    m=synthetic_ensemble(n=60,scatter=.9)
    out=internal_relative_offset_qc(m)
    assert out["instrumental_offset_internally_consistent"] is False
    assert out["status"].startswith("NO_GO")
    assert out["all_photometric_series_remain_unmerged"] is True


def test_original_catalogue_sha_mismatch_fails_closed_without_archive_fabrication():
    from unittest.mock import patch
    frame=PRIOR["original_fits_mask_native_psf_exposure_results"][0]
    with patch("stellarforge.r2_fttau_crossfield_instrumental_ensemble.parse_psf_fit_catalogue",
               return_value={"sha256":"b"*64}):
        with pytest.raises(ValueError,match="differs"):
            original_native_catalogue_from_frozen_image(
                frame,ra=RA0,dec=DEC0,
                native_fetch=lambda *a,**k:b"synthetic FITS not real")
