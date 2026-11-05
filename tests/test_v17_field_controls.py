"""Fully synthetic v1.7 same-field source-control and transport-budget tests."""
import csv
import io
from urllib.error import HTTPError

import numpy as np
import pytest
from astropy.io import fits
from astropy.wcs import WCS

from stellarforge.v17_field_controls import (
    inspect_image_with_same_field_controls,
    stratified_ztf_image_candidates, inspect_curve_field_controls,
)

RA, DEC = 65.913324, 24.937195


def image_fixture(*, controls=2, elongated=False, empty=False,
                  size=100, offset_px=0, bright_companion=False):
    rng = np.random.default_rng(1701)
    yy,xx = np.indices((size,size))
    base = 1200 + rng.normal(0,3, size=(size,size))
    targetx = size//2
    targety = size//2
    if not empty:
        sx = 2.7 if elongated else 1.8
        base += 500*np.exp(-.5*(((xx-(targetx+offset_px))/sx)**2
                           +((yy-targety)/1.7)**2))
        for x,y in [(20,25),(75,30),(30,73)][:controls]:
            base += 450*np.exp(-.5*(((xx-x)/1.8)**2+((yy-y)/1.7)**2))
        if bright_companion:
            base += 160*np.exp(-.5*(((xx-(targetx+6))/1.2)**2
                                +((yy-(targety+3))/1.2)**2))
    hdu = fits.PrimaryHDU(base.astype(np.float32))
    w = WCS(naxis=2)
    w.wcs.crpix = [targetx+1,targety+1]
    w.wcs.cdelt = [-1/3600,1/3600]
    w.wcs.crval = [RA, DEC]
    w.wcs.ctype = ["RA---TAN","DEC--TAN"]
    hdu.header.update(w.to_header())
    b = io.BytesIO()
    hdu.writeto(b)
    return b.getvalue()


def test_two_unclassified_controls_enable_descriptive_profile():
    result = inspect_image_with_same_field_controls(
        image_fixture(controls=2), expected_ra_deg=RA, expected_dec_deg=DEC)
    assert result["status"] == "SAME_IMAGE_RADIAL_SHAPE_COMPARISON_PROVISIONAL"
    assert result["n_usable_unclassified_controls"] >= 2
    assert result["field_psf_calibrated"] is False
    assert result["deblending_verified"] is False
    assert result["gaia_ztf_identity_confirmed"] is False
    assert len(result["control_median_ring_fractions"]) == 6
    assert result["max_abs_ring_fraction_deviation"] < 0.12
    assert result["descriptive_shape_review_flag"] is False


def test_elongated_profile_triggers_nonphysical_review():
    result = inspect_image_with_same_field_controls(
        image_fixture(controls=2,elongated=True),
        expected_ra_deg=RA, expected_dec_deg=DEC)
    assert result["status"] == "SAME_IMAGE_RADIAL_SHAPE_COMPARISON_PROVISIONAL"
    assert result["max_abs_ring_fraction_deviation"] > 0
    assert not result["astro_companion_confirmed"]


def test_no_field_controls_is_never_called_clean():
    result=inspect_image_with_same_field_controls(
        image_fixture(controls=0), expected_ra_deg=RA, expected_dec_deg=DEC)
    assert result["status"] == "INSUFFICIENT_UNVERIFIED_FIELD_CONTROLS"
    assert result["n_usable_unclassified_controls"] == 0
    assert result["field_psf_calibrated"] is False
    assert result["deblending_verified"] is False


def test_one_candidate_control_not_enough_to_claim_comparison():
    result=inspect_image_with_same_field_controls(
        image_fixture(controls=1), expected_ra_deg=RA, expected_dec_deg=DEC)
    assert result["n_usable_unclassified_controls"] == 1
    assert result["status"] == "INSUFFICIENT_UNVERIFIED_FIELD_CONTROLS"


def test_empty_field_no_target_does_not_infer_non_detection():
    result = inspect_image_with_same_field_controls(
        image_fixture(empty=True), expected_ra_deg=RA, expected_dec_deg=DEC)
    assert result["status"] == "TARGET_RADIAL_PROXY_UNUSABLE"
    assert not result["gaia_ztf_identity_confirmed"]


def test_too_small_fits_cutout_does_not_assert_no_neighbours():
    result=inspect_image_with_same_field_controls(
        image_fixture(size=40), expected_ra_deg=RA, expected_dec_deg=DEC)
    assert result["status"] == "INSUFFICIENT_FIELD_FOR_CONTROLS"
    assert not result["deblending_verified"]


def make_lightcurve(n=32):
    out=io.StringIO()
    columns=["oid","mjd","catflags","filtercode","filefracday",
             "field","ccdid","qid"]
    w=csv.DictWriter(out,fieldnames=columns)
    w.writeheader()
    for oid,band in [("1234567","zg"),("3212345","zr")]:
        for i in range(n):
            w.writerow({"oid":oid,"mjd":58300+i,"catflags":0,
                        "filtercode":band,"filefracday":f"201807{(i%28+1):02d}{i:06d}",
                        "field":"609","ccdid":"0x8","qid":"0x4"})
    return out.getvalue().encode()


def test_stratified_selection_six_unique_real_dates_and_reference():
    groups=stratified_ztf_image_candidates(
        make_lightcurve(),ra_deg=RA,dec_deg=DEC,
        pmra_mas_yr=7.448,pmdec_mas_yr=-21.849)
    assert len(groups)==2
    for group in groups:
        assert len(group["candidates"]) == 7
        sci=group["candidates"][:-1]
        assert all(x["kind"]=="science" and x["mjd"] is not None for x in sci)
        assert len({x["observation_filefracday"] for x in sci})==6
        assert all("90arcsec" in x["url"] for x in sci)
        assert group["candidates"][-1]["kind"]=="reference_coadd"
        assert group["candidates"][-1]["mjd"] is None
        assert not group["scientific_identity_verified"]


@pytest.mark.parametrize("bad", [0,7,-1])
def test_bounded_budget_rejects_excessive_requests(bad):
    with pytest.raises(ValueError):
        stratified_ztf_image_candidates(make_lightcurve(),ra_deg=RA,dec_deg=DEC,
            pmra_mas_yr=7.448,pmdec_mas_yr=-21.849,science_per_oid=bad)


def fake_curve():
    return {"ztf_oid":"1234","band":"zg","candidates":[
        {"kind":"science","mjd":59001,"url":"a","expected_ra_deg":RA,
         "expected_dec_deg":DEC},
        {"kind":"science","mjd":59020,"url":"b","expected_ra_deg":RA,
         "expected_dec_deg":DEC},
        {"kind":"science","mjd":59030,"url":"c","expected_ra_deg":RA,
         "expected_dec_deg":DEC},
        {"kind":"reference_coadd","mjd":None,"url":"ref",
         "expected_ra_deg":RA,"expected_dec_deg":DEC},
    ]}


def fake_result(raw, **kwargs):
    return {"status":"SAME_IMAGE_RADIAL_SHAPE_COMPARISON_PROVISIONAL",
            "fits_sha256":raw.decode("ascii"),
            "n_usable_unclassified_controls":2,
            "target_single_gaussian_fit":{
                "fitted_centroid_east_minus_Gaia_arcsec":.1,
                "fitted_centroid_north_minus_Gaia_arcsec":.2,
            },
            "deblending_verified":False}


def test_two_distinct_science_images_stop_requests_before_reference():
    seen=[]
    def fake_fetch(url,timeout):
        seen.append(url)
        return url.encode()
    result=inspect_curve_field_controls(
        fake_curve(),fetch=fake_fetch,inspect=fake_result)
    assert seen==["a","b"]
    assert result["n_distinct_science_images_screened"]==2
    assert result["science_repeatability_descriptive"] is True
    assert result["max_pairwise_fit_centroid_residual_difference_arcsec"]==0
    assert result["field_deblended"] is False


def test_duplicate_image_bytes_do_not_count_as_independent_science():
    def fake_fetch(url,timeout):
        return b"same-image"
    result=inspect_curve_field_controls(
        fake_curve(),fetch=fake_fetch,inspect=fake_result)
    assert result["n_distinct_science_images_screened"]==1
    assert result["science_repeatability_descriptive"] is False
    assert result["reference_coadds_excluded_from_repeatability"] is True


def test_remote_failures_try_reference_but_not_claim_empty_sky():
    def fail(url,timeout):
        raise HTTPError(url,503,"unavailable",None,None)
    result=inspect_curve_field_controls(fake_curve(),fetch=fail,science_attempts=3)
    assert all(x.get("http_status")==503 for x in result["attempts"])
    assert result["n_distinct_science_images_screened"]==0
    assert result["gaia_ztf_identity_confirmed"] is False
