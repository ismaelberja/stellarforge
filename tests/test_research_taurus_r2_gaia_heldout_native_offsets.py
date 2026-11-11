"""Offline falsification tests for R2 previously Gaia-only field controls."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from stellarforge.r2_gaia_heldout_native_offsets import (
    CIDA_STRICT_CONTROLS, FT_EXPLORATORY_CONTROL, TARGETS,
    registered_controls,gaia_native_offset_mas,
    summarize_control_offsets,
)
from stellarforge.r2_original_fits_gates import validate_historic_exposures

ROOT=Path(__file__).resolve().parents[1]
SEED=(ROOT/"data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv").read_bytes()
LEDGER=json.loads((ROOT/"data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json").read_text(encoding="utf8"))


def ctrl(sid:str,e:float,n:float,*,strict=True,good=True,ruwe=False):
    return {
        "gaia_dr3_source_id":sid,
        "role":"CONTROL",
        "source_stratum":(
            "GAIA_ONLY_STRICT_CIDA_V117" if strict else
            "GAIA_ONLY_RELAXED_FT_V118"),
        "native_minus_gaia_east_mas":e,
        "native_minus_gaia_north_mas":n,
        "screen_status":(
            "PROVISIONAL_CATALOGUE_NEAREST_AND_PROFILE_SCREEN_PASSED"
            if good else "NATIVE_PSF_FIT_PROFILE_OR_FLAG_REVIEW_REQUIRED"),
        "astrometric_quality_warning":ruwe,
    }


def target(*,quality=True,warning=False,e=250,n=90):
    return {
        "role":"TARGET",
        "screen_status":(
            "PROVISIONAL_CATALOGUE_NEAREST_AND_PROFILE_SCREEN_PASSED"
            if quality else "NO_PSF_CATALOGUE_ENTRY_WITHIN_RADIUS"),
        "astrometric_quality_warning":warning,
        "native_minus_gaia_east_mas":e,
        "native_minus_gaia_north_mas":n,
    }


def test_previously_registered_gaia_controls_not_postselected():
    assert len(CIDA_STRICT_CONTROLS)==4
    assert CIDA_STRICT_CONTROLS==(
        "3419109222512317056","3419109840987851136",
        "3419157944621312896","3419111451598996992")
    assert FT_EXPLORATORY_CONTROL==("149623298952568064",)
    assert TARGETS=={
        "FT Tau":"149623711269425408",
        "CIDA 11":"3419110734340795648"}
    assert set(CIDA_STRICT_CONTROLS).isdisjoint(TARGETS.values())
    assert set(FT_EXPLORATORY_CONTROL).isdisjoint(TARGETS.values())
    assert registered_controls("FT Tau")==FT_EXPLORATORY_CONTROL
    assert registered_controls("CIDA 11")==CIDA_STRICT_CONTROLS
    with pytest.raises(ValueError):
        registered_controls("a more convenient field")


def test_four_historical_preexisting_exposures_in_frozen_technical_24():
    sources, frames=validate_historic_exposures(SEED,LEDGER)
    assert len(sources)==24
    assert len(frames)==4
    assert {f["target"] for f in frames}==set(TARGETS)
    assert all(f["target_gaia_id"]==TARGETS[f["target"]] for f in frames)


def test_gaia_and_native_original_catalogue_signed_angular_offsets():
    prediction={
        "geocentric_parallax_adjusted_ra_deg":65.0,
        "geocentric_parallax_adjusted_dec_deg":0.0,
    }
    native={"rows":{
        "sourceid":np.array([100,101],dtype=np.int64),
        "ra":np.array([65.+.2/3600.,65.+5/3600.]),
        "dec":np.array([.1/3600.,0.]),
    }}
    r=gaia_native_offset_mas(prediction,native,100)
    assert r["native_minus_gaia_east_mas"]==pytest.approx(200,abs=.01)
    assert r["native_minus_gaia_north_mas"]==pytest.approx(100,abs=.01)
    assert r["native_offset_angular_proxy_mas"]==pytest.approx(223.607,abs=.01)
    assert r["original_zTF_wcs_zeropoint_independently_measured"] is False


def test_duplicated_native_source_id_never_yields_a_unique_counterpart():
    p={"geocentric_parallax_adjusted_ra_deg":65.0,
       "geocentric_parallax_adjusted_dec_deg":0.0}
    n={"rows":{"sourceid":np.array([1,1]),"ra":np.array([65.,65.]),
               "dec":np.array([0.,0.])}}
    with pytest.raises(ValueError,match="unique"):
        gaia_native_offset_mas(p,n,1)


def test_three_strict_controls_allow_only_provisional_differential_offset():
    a=[ctrl(CIDA_STRICT_CONTROLS[i],v,v/2)
       for i,v in enumerate((100,200,400,900))]
    a[-1]["screen_status"]="NATIVE_PSF_FIT_PROFILE_OR_FLAG_REVIEW_REQUIRED"
    result=summarize_control_offsets(a,target(e=260,n=90))
    assert result["n_strict_gaia_controls_with_acceptable_native_psf_and_gaia_quality"]==3
    assert result["min_three_strict_controls_gate_passed"] is True
    assert result["median_control_east_offset_mas"]==200
    assert result["median_control_north_offset_mas"]==100
    rel=result["provisional_target_relative_offset"]
    assert rel["relative_native_minus_gaia_east_mas"]==60
    assert rel["relative_native_minus_gaia_north_mas"]==-10
    assert rel["physical_source_identity_confirmed"] is False
    assert result["independent_instrument_WCS_or_PSF_calibration"] is False
    assert result["proved_disjoint_from_original_ZTF_DAOPhot_training_stars"] is False


def test_only_two_strict_controls_insufficient_no_forced_field_correction():
    a=[ctrl(CIDA_STRICT_CONTROLS[i],v,0)
       for i,v in enumerate((100,300))]
    x=summarize_control_offsets(a,target())
    assert x["min_three_strict_controls_gate_passed"] is False
    assert x["median_control_east_offset_mas"]==200
    assert x["provisional_target_relative_offset"] is None


def test_ftau_only_one_relaxed_control_cannot_calibrate_ztf_field():
    a=[ctrl(FT_EXPLORATORY_CONTROL[0],100,-100,strict=False)]
    r=summarize_control_offsets(a,target())
    assert r["source_control_stratum"]=="EXPLORATORY_FT"
    assert r["n_exploratory_ft_controls_with_acceptable_native_psf"]==1
    assert r["n_strict_gaia_controls_with_acceptable_native_psf_and_gaia_quality"]==0
    assert r["min_three_strict_controls_gate_passed"] is False
    assert r["provisional_target_relative_offset"] is None


def test_high_ruwe_target_blocks_strict_three_control_difference():
    a=[ctrl(sid,i*100,0) for i,sid in enumerate(CIDA_STRICT_CONTROLS[:3])]
    r=summarize_control_offsets(a,target(warning=True))
    assert r["min_three_strict_controls_gate_passed"] is True
    assert r["target_original_native_psf_and_gaia_quality_gate_passed"] is False
    assert r["provisional_target_relative_offset"] is None


def test_bad_ruwe_control_does_not_add_as_good_strict_reference():
    a=[ctrl(sid,100,100,ruwe=(i==2))
       for i,sid in enumerate(CIDA_STRICT_CONTROLS[:3])]
    x=summarize_control_offsets(a,target())
    assert x["n_strict_gaia_controls_with_acceptable_native_psf_and_gaia_quality"]==2
    assert x["provisional_target_relative_offset"] is None


def test_no_trustworthy_controls_mean_no_median_and_no_science_claims():
    a=[ctrl(sid,50,100,good=False) for sid in CIDA_STRICT_CONTROLS]
    r=summarize_control_offsets(a,target())
    assert r["source_control_stratum"]=="NONE"
    assert r["median_control_east_offset_mas"] is None
    assert r["median_control_north_offset_mas"] is None
    assert r["physical_gaia_to_ztf_source_identity_verified"] is False
    assert r["provisional_target_relative_offset"] is None
