"""Adversarial original DAOPhot ASCII spatial PSF reconstruction/center tests."""
from __future__ import annotations

import io
import numpy as np
import pytest
from astropy.io import fits

from stellarforge.v115_spatial_psf import (
    parse_original_daophot_lookup,evaluate_spatial_psf_shape,
    psf_image_shape_diagnostics,compare_reconstruction_to_official_center,
    summarize_evaluated_candidate_psfs,
)


def simulated_daophot(*,n=47,count=3,first=.0,
                      malformed=False,amp=3579.729,model="GAUSSIAN"):
    hdr=f" {model}   {n}    2    {count}    0   14.305       {amp}   1535.5   1539.5\n"
    hdr+="  1.112774E+00 9.879758E-01\n"
    values=np.zeros((count,n,n))
    if first!=0:
        yy,xx=np.indices((n,n))
        values[1]=(xx-(n-1)/2)*first
        values[2]=(yy-(n-1)/2)*first
    body=""
    for i,v in enumerate(values.ravel()):
        body+=f"{v:14.6E}"
        if (i+1)%6==0:body+="\n"
    if malformed:body+="CORRUPT TOKEN\n"
    return (hdr+body).encode("ascii")


def _center_fits(img):
    b=io.BytesIO()
    fits.PrimaryHDU(np.asarray(img,dtype="float32")).writeto(b)
    return b.getvalue()


def test_parse_ztf_expected_gaussian_47_by_47_three_lut_structure():
    result=parse_original_daophot_lookup(simulated_daophot())
    assert result["header_type"]=="GAUSSIAN"
    assert result["lookup_side_samples"]==47
    assert result["n_lookup_tables"]==3
    assert result["tables"].shape==(3,47,47)
    assert result["analytic_hwhm_x_pixels"]==pytest.approx(1.112774)
    assert len(result["source_sha256"])==64
    assert not result["science_single_star_identity_confirmed"]


def test_approximate_center_psf_23_square_normalized_positive():
    p=parse_original_daophot_lookup(simulated_daophot())
    a=evaluate_spatial_psf_shape(p,x=1535.5,y=1539.5)
    assert a.shape==(23,23)
    assert a.sum()==pytest.approx(1)
    assert np.min(a)>=0
    diag=psf_image_shape_diagnostics(a)
    assert diag["shape"]==[23,23]
    assert diag["x_centroid_pixel"]==pytest.approx(11,abs=.1)


def test_half_pixel_phase_is_accepted_and_changes_shape():
    p=parse_original_daophot_lookup(simulated_daophot())
    a=evaluate_spatial_psf_shape(p,x=1535.5,y=1539.5,frac_x=0)
    b=evaluate_spatial_psf_shape(p,x=1535.5,y=1539.5,frac_x=.4)
    assert np.abs(a-b).sum()>.02
    assert b.sum()==pytest.approx(1)


def test_position_dependent_correction_can_change_source_psf():
    p=parse_original_daophot_lookup(simulated_daophot(first=.035))
    central=evaluate_spatial_psf_shape(p,x=1535.5,y=1539.5)
    out=evaluate_spatial_psf_shape(p,x=2650,y=2100)
    assert not np.allclose(out,central)
    assert np.abs(out-central).sum()>.002


def test_conservative_official_center_psf_check_passes_identical_synthetic_data():
    p=parse_original_daophot_lookup(simulated_daophot())
    a=evaluate_spatial_psf_shape(p,x=1535.5,y=1539.5)
    s=compare_reconstruction_to_official_center(p,_center_fits(a))
    assert s["status"]=="OFFICIAL_CENTER_PSF_APPROXIMATE_MODEL_AGREEMENT"
    assert s["model_vs_official_center_cosine_similarity"]==pytest.approx(1,abs=1e-5)
    assert s["model_vs_official_center_normalized_l1"]==pytest.approx(0,abs=1e-5)
    assert not s["local_spatial_psf_calibrated"]


def test_center_check_fails_different_model_shapes_without_calibration_claim():
    p=parse_original_daophot_lookup(simulated_daophot())
    native=np.zeros((23,23))
    native[11,3]=1
    r=compare_reconstruction_to_official_center(p,_center_fits(native))
    assert r["status"]=="OFFICIAL_CENTER_PSF_RECONSTRUCTION_DISAGREEMENT_REVIEW"
    assert not r["independently_calibrated_detector_wcs"]


def test_center_fits_shape_mismatch_blocks_approximated_psf_validation():
    p=parse_original_daophot_lookup(simulated_daophot())
    r=compare_reconstruction_to_official_center(p,_center_fits(np.ones((25,25))))
    assert r["status"]=="NATIVE_CENTER_PSF_SHAPE_MISMATCH"
    assert r["official_shape"]==[25,25]


@pytest.mark.parametrize("opts",[
    {"n":49},
    {"n":114},
    {"count":2},
    {"count":8},
    {"amp":0},
    {"model":"MOFFAT"},
    {"malformed":True},
])
def test_invalid_or_unimplemented_lookup_does_not_silently_parse(opts):
    with pytest.raises(ValueError):
        parse_original_daophot_lookup(simulated_daophot(**opts))


def test_bad_coefficient_number_corrupted_model_rejected():
    raw=simulated_daophot()
    raw=raw.replace(b"0.000000E+00",b"NaN",1)
    with pytest.raises(ValueError):
        parse_original_daophot_lookup(raw)


def test_truncated_native_file_cannot_produce_credible_psf():
    with pytest.raises(ValueError):
        parse_original_daophot_lookup(simulated_daophot()[:150])


@pytest.mark.parametrize("x,y",[
    (float("nan"),1539.5),(0,1540),(1535.5,-1),
    (6000,1539.5),(1535.5,7000),
])
def test_native_detector_geometry_must_be_finite_and_bounded(x,y):
    p=parse_original_daophot_lookup(simulated_daophot())
    with pytest.raises(ValueError):
        evaluate_spatial_psf_shape(p,x=x,y=y)


@pytest.mark.parametrize("fraction",[float("nan"),.51,-.51])
def test_invalid_subpixel_phase_fail_closed(fraction):
    p=parse_original_daophot_lookup(simulated_daophot())
    with pytest.raises(ValueError):
        evaluate_spatial_psf_shape(p,x=1535.5,y=1539.5,frac_x=fraction)


def test_unverified_gaia_candidate_does_not_prove_calibrated_local_psf():
    p=parse_original_daophot_lookup(simulated_daophot())
    cent=compare_reconstruction_to_official_center(
        p,_center_fits(evaluate_spatial_psf_shape(p,x=1535.5,y=1539.5)))
    screens=[
        {"gaia_source_id":"123",
         "status":"PROVISIONAL_CATALOGUE_NEAREST_AND_PROFILE_SCREEN_PASSED",
         "ztf_native_detector_xpos_pixels":1511.,
         "ztf_native_detector_ypos_pixels":1641.,
         "ztf_native_per_exposure_sourceid":34},
        {"gaia_source_id":"124","status":"NATIVE_PSF_FIT_PROFILE_OR_FLAG_REVIEW_REQUIRED"},
    ]
    out=summarize_evaluated_candidate_psfs(p,screens,center_check=cent)
    assert out["n_evaluated_provisional_catalogue_candidate_psfs"]==1
    assert out["reconstructions"][0]["shape"]==[23,23]
    assert out["reconstructions"][1]["status"]=="NOT_EVALUATED_PSF_CANDIDATE_QUALITY_REVIEW"
    assert out["n_independently_calibrated_source_psfs"]==0
    assert out["n_authenticated_gaia_ztf_source_identities"]==0


def test_failed_center_model_does_not_turn_into_authenticated_local_psf():
    p=parse_original_daophot_lookup(simulated_daophot())
    bad={"status":"OFFICIAL_CENTER_PSF_RECONSTRUCTION_DISAGREEMENT_REVIEW"}
    out=summarize_evaluated_candidate_psfs(
        p,[{"gaia_source_id":"123",
        "status":"PROVISIONAL_CATALOGUE_NEAREST_AND_PROFILE_SCREEN_PASSED",
        "ztf_native_detector_xpos_pixels":1511.,
        "ztf_native_detector_ypos_pixels":1641.,
        "ztf_native_per_exposure_sourceid":34}],center_check=bad)
    assert out["n_evaluated_provisional_catalogue_candidate_psfs"]==1
    assert out["model_center_validity"].endswith("REVIEW")
    assert out["n_independently_calibrated_source_psfs"]==0
