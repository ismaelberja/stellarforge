"""v1.17 synthetic disjoint stellar Gaia controls and shifted-sky nulls."""
from __future__ import annotations

import math

import numpy as np
import pytest

from stellarforge.v117_disjoint_gaia_controls import (
    select_disjoint_holdout_controls, shifted_sky_null_probes,
    compare_disjoint_holdouts, SHIFTS_ARCSEC,
)

RA=65.913324
DEC=24.937195
TARGET="149623711269425408"
EXCLUDED={TARGET,"149623711269425410","149623711269425420"}


def star(sid,dx=0,dy=0,*,g=15.5,ruwe=1.1,parallax=3.0,
         duplicate=False,solved=31):
    return {
        "source_id":str(sid),
        "ra":RA+dx/(3600*math.cos(math.radians(DEC))),
        "dec":DEC+dy/3600,
        "g_mag":g,"g_flux_snr":125,"ruwe":ruwe,
        "duplicated_source":duplicate,"astrometric_params_solved":solved,
        "pmra":2.,"pmdec":-1.,"parallax":parallax,
        "ra_error_mas":.5,"dec_error_mas":.5,
        "pmra_error_mas_yr":.2,"pmdec_error_mas_yr":.2,
    }


def field():
    return [
        star(TARGET),
        star("149623711269425410",80,70),
        star("149623711269425420",-80,-70),
        star("501",95,95), star("502",-95,95),
        star("503",100,-105),star("504",-90,-100),
        star("505",140,0),
    ]


def test_new_gaia_controls_are_selected_prior_to_using_any_ztf_data():
    s=select_disjoint_holdout_controls(
        field(),target_id=TARGET,excluded_source_ids=EXCLUDED,
        max_controls=4)
    assert s["status"]=="DISJOINT_GAIA_ONLY_CONTROL_SELECTION_READY"
    assert s["n_disjoint_controls_preselected"]==4
    assert {x["source_id"] for x in s["controls"]}=={"501","502","503","504"}
    assert not {x["source_id"] for x in s["controls"]}&EXCLUDED
    assert s["n_occupied_quadrants"]==4
    assert s["gaia_control_selection_independent_of_v116_pixel_residuals"]
    assert not s["native_ztf_psf_training_star_membership_known"]


def test_gaia_reference_exclusions_are_enforced_not_just_source_target():
    s=select_disjoint_holdout_controls(
        field(),target_id=TARGET,excluded_source_ids=EXCLUDED,
        max_controls=5)
    assert not {x["source_id"] for x in s["controls"]}&EXCLUDED
    assert s["rejection_counts"]["excluded_original_reference_or_target"]==3


def test_neighbor_isolation_counts_every_gaia_source_even_if_quality_rejected():
    rows=field()
    rows.append(star("999",97,96,ruwe=2.5))
    s=select_disjoint_holdout_controls(
        rows,target_id=TARGET,excluded_source_ids=EXCLUDED)
    assert "501" not in {x["source_id"] for x in s["controls"]}
    assert s["rejection_counts"]["gaia_neighbour_isolation"]>=1


@pytest.mark.parametrize("bad",[
    {"ruwe":1.8},{"duplicate":True},{"solved":3},
    {"g":12},{"g":19},{"parallax":None},
])
def test_quality_screens_dont_turn_catalogue_bad_controls_into_holdout_stars(bad):
    rows=[star(TARGET),star("601",95,80,**bad),star("602",-90,-95)]
    s=select_disjoint_holdout_controls(
        rows,target_id=TARGET,excluded_source_ids={TARGET})
    assert "601" not in {x["source_id"] for x in s["controls"]}
    assert "602" in {x["source_id"] for x in s["controls"]}


def test_no_available_disjoint_holdout_fails_closed_not_just_reuses_old_controls():
    s=select_disjoint_holdout_controls(
        [star(TARGET),star("149623711269425410",100,60)],
        target_id=TARGET,excluded_source_ids=EXCLUDED)
    assert s["status"]=="NO_DISJOINT_GAIA_CONTROL_CANDIDATES"
    assert s["n_disjoint_controls_preselected"]==0


def test_absent_target_or_truncated_wide_cone_is_not_independently_verified():
    s=select_disjoint_holdout_controls(
        [star("601",90,90)],target_id=TARGET,excluded_source_ids={TARGET})
    assert s["status"]=="GAIA_TARGET_MISSING_FROM_WIDE_CONE"
    with pytest.raises(ValueError):
        select_disjoint_holdout_controls(
            [star(TARGET)]*500,target_id=TARGET,excluded_source_ids={TARGET})


def test_gaia_duplicate_source_ids_are_rejected():
    with pytest.raises(ValueError,match="duplicate"):
        select_disjoint_holdout_controls(
            [star(TARGET),star("601",80,90),star("601",-80,90)],
            target_id=TARGET,excluded_source_ids={TARGET})


def nativecat(ra_deg=None,dec_deg=None,*,n=1,flags=0,chi=1.0):
    r=np.array([RA if ra_deg is None else ra_deg]*n)
    d=np.array([DEC if dec_deg is None else dec_deg]*n)
    return {
        "status":"ORIGINAL_ZTF_PSF_CATALOGUE_PARSED_UNVERIFIED",
        "rows":{
            "ra":r,"dec":d,
            "flags":np.array([flags]*n),"chi":np.array([chi]*n),
            "sharp":np.array([0.0]*n),"snr":np.array([40.0]*n),
            "flux":np.array([500.]*n),"sigflux":np.array([25.]*n),
        },
    }


def prediction(sid="601",ra=RA,dec=DEC):
    return {
        "source_id":sid,
        "geocentric_parallax_adjusted_ra_deg":ra,
        "geocentric_parallax_adjusted_dec_deg":dec,
    }


def test_four_predefined_25arcsec_shifted_sky_probes_are_not_null_probabilities():
    s=shifted_sky_null_probes(nativecat(),[prediction()])
    assert len(SHIFTS_ARCSEC)==4
    assert s["n_shifted_sky_probes"]==4
    assert s["n_nearest_any_psf_source_within_radius"]==0
    assert s["n_profile_qualified_shifted_hits"]==0
    assert not s["calibrated_source_false_association_probability"]
    assert s["shifted_offsets_may_contain_actual_unrelated_stars"]


def test_real_native_psf_source_at_25arcsec_shift_is_reported_not_fake_physical_match():
    lon=RA+25/(3600*math.cos(math.radians(DEC)))
    s=shifted_sky_null_probes(nativecat(ra_deg=lon),[prediction()])
    assert s["n_nearest_any_psf_source_within_radius"]==1
    assert s["n_profile_qualified_shifted_hits"]==1
    assert not s["calibrated_source_false_association_probability"]


@pytest.mark.parametrize("patch",[
    {"flags":256},{"flags":-1},{"chi":2.0},
])
def test_shifted_sky_probes_quality_does_not_turn_bad_catalogue_hit_into_clean_profile(patch):
    lon=RA+25/(3600*math.cos(math.radians(DEC)))
    s=shifted_sky_null_probes(nativecat(ra_deg=lon,**patch),[prediction()])
    assert s["n_nearest_any_psf_source_within_radius"]==1
    assert s["n_profile_qualified_shifted_hits"]==0


def test_missing_catalogue_never_counts_shifted_null_as_sky_nondetection():
    s=shifted_sky_null_probes({"status":"UNAVAILABLE"},[prediction()])
    assert s["status"]=="NATIVE_PSF_CATALOGUE_UNAVAILABLE_FOR_SHIFTED_NULL"
    assert s["n_shifted_sky_probes"]==0


def test_shifted_sky_probe_budget_enforced():
    with pytest.raises(ValueError):
        shifted_sky_null_probes(nativecat(),[prediction(str(i)) for i in range(6)])


def test_disjoint_source_pixel_results_do_not_claim_independent_psf_training():
    x=[
        {"gaia_source_id":"601","fit_completed":True,"rms_over_sky_proxy":1.2,
         "residual_quality_passed":True,"originally_used_in_v116":False},
        {"gaia_source_id":"602","fit_completed":True,"rms_over_sky_proxy":1.5,
         "residual_quality_passed":False,"originally_used_in_v116":False},
        {"gaia_source_id":"603","fit_completed":True,"rms_over_sky_proxy":.95,
         "residual_quality_passed":True,"originally_used_in_v116":False},
    ]
    s=compare_disjoint_holdouts(x)
    assert s["status"]=="DISTINCT_GAIA_CONTROL_DESCRIPTIVE_SAMPLE_READY"
    assert s["median_same_image_pixel_holdout_rms_over_sky_mad_proxy"]==pytest.approx(1.2)
    assert s["n_original_pixel_residual_profiles_screen_passed"]==2
    assert s["n_distinct_source_ids_not_used_in_original_v116_fits"]==3
    assert not s["native_psf_lookup_training_sample_exclusion_proven"]
    assert not s["independent_external_instrument_psf_wcs_error_calibration_completed"]


def test_only_two_actual_holdouts_cannot_be_treated_as_validated_distribution():
    s=compare_disjoint_holdouts([
        {"gaia_source_id":"601","fit_completed":True,"rms_over_sky_proxy":1.1,"originally_used_in_v116":False},
        {"gaia_source_id":"602","fit_completed":True,"rms_over_sky_proxy":1.3,"originally_used_in_v116":False},
    ])
    assert s["status"]=="INSUFFICIENT_DISTINCT_GAIA_CONTROL_IMAGE_FITS"
    assert s["median_same_image_pixel_holdout_rms_over_sky_mad_proxy"] is None


def test_reuse_old_source_id_or_duplicate_fails_closed():
    with pytest.raises(ValueError):
        compare_disjoint_holdouts([{"gaia_source_id":"601","originally_used_in_v116":True}])
    with pytest.raises(ValueError):
        compare_disjoint_holdouts([
            {"gaia_source_id":"601","originally_used_in_v116":False},
            {"gaia_source_id":"601","originally_used_in_v116":False},
        ])
