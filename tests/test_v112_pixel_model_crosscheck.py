"""Synthetic FITS and adversarial quality-gate tests for real image remeasurement."""
from __future__ import annotations

import io
from urllib.error import HTTPError
import numpy as np
import pytest
from astropy.io import fits
from astropy.wcs import WCS

from stellarforge.v112_pixel_model_crosscheck import (
    aperture_and_gaussian_centroid_screen,
    analyze_real_science_reference_cutout,
    audit_provisional_field_references,
    SUCCESS, REVIEW, INCOMPLETE,
)

RA,DEC=65.913324,24.937195


def _fits(*,snr=200,sigma_x=1.7,sigma_y=1.8,gradient=.25,
          add_neighbor=False,missing_pixels=False,mjd_header=59000.,
          missing_wcs=False,saturation=None):
    rng=np.random.default_rng(1212)
    y,x=np.indices((64,64),dtype=float)
    data=(1000+gradient*(x-32)+2*rng.normal(size=x.shape)
          +snr*2*np.exp(-.5*(((x-32)/sigma_x)**2+((y-32)/sigma_y)**2)))
    if add_neighbor:
        data+=250*np.exp(-.5*(((x-37)/1.3)**2+((y-34)/1.3)**2))
    if missing_pixels:
        data[32,33]=float("nan")
    hdu=fits.PrimaryHDU(data.astype("float32"))
    if not missing_wcs:
        w=WCS(naxis=2)
        w.wcs.crpix=[33,33]
        w.wcs.cdelt=[-1/3600,1/3600]
        w.wcs.crval=[RA,DEC]
        w.wcs.ctype=["RA---TAN","DEC--TAN"]
        hdu.header.update(w.to_header())
    if mjd_header is not None:
        hdu.header["MJD-OBS"]=mjd_header
    if saturation is not None:
        hdu.header["SATURATE"]=saturation
    handle=io.BytesIO()
    hdu.writeto(handle)
    return handle.getvalue()


def _screen(**kwargs):
    return aperture_and_gaussian_centroid_screen(
        _fits(**kwargs),expected_ra_deg=RA,expected_dec_deg=DEC,
        mjd_assumed_utc=59000)


def test_clean_synthetic_source_agrees_without_claiming_stellar_identity():
    result=_screen()
    assert result["status"]==SUCCESS
    assert result["aperture_vs_gaussian_centroid_difference_arcsec"]<.25
    assert result["aperture_peak_snr_proxy"]>15
    assert result["aperture_second_moment_axis_ratio_proxy"]<2
    assert result["fits_timing_metadata_status"]=="FITS_MJD_NEAR_QUERY_NOT_TIMESCALE_VERIFIED"
    assert result["saturation_screen_status"]=="SATURATION_FLAG_OR_THRESHOLD_UNAVAILABLE"
    assert result["detector_saturation_mask_implemented"] is False
    assert result["gaia_ztf_source_identity_confirmed"] is False
    assert result["single_star_psf_authenticated"] is False
    assert result["independent_instrument_wcs_error_calibrated"] is False


def test_background_plane_is_fitted_separately_from_gaussian_sky():
    result=_screen(gradient=1.2)
    assert result["status"] in (SUCCESS,REVIEW)
    assert result["local_background_plane_gradient_x_data_per_pixel"]==pytest.approx(
        1.2,abs=.2)
    assert result["sky_annulus_n_pixel_kept"]>=60
    assert not result["independent_instrument_wcs_error_calibrated"]


def test_bad_or_biased_gaussian_source_is_flagged_not_companion():
    result=_screen(add_neighbor=True)
    assert result["status"] in (REVIEW,INCOMPLETE)
    assert result.get("new_astrophysical_companion_confirmed",False) is False
    assert result.get("gaia_ztf_source_identity_confirmed",False) is False


def test_bad_core_pixels_fail_closed():
    result=_screen(missing_pixels=True)
    assert result["status"]==INCOMPLETE
    assert result["reason"]=="NONFINITE_APERTURE_PIXEL"


def test_wrong_mjd_header_is_not_reinterpreted_as_empty_sky():
    result=_screen(mjd_header=59001)
    assert result["fits_timing_metadata_status"]=="FITS_MJD_FAR_FROM_ORIGINAL_QUERY"
    assert result["status"]==REVIEW
    assert not result["fit_quality_allows_provisional_internal_control"]


def test_missing_observation_time_header_keeps_utc_unverified():
    result=_screen(mjd_header=None)
    assert result["fits_timing_metadata_status"]=="NO_INDEPENDENT_FITS_MJD_METADATA"
    assert result["utc_time_scale_independently_validated"] is False


def test_saturation_threshold_is_metadata_only_not_bitmask():
    result=_screen(saturation=20000)
    assert result["saturation_screen_status"]=="HEADER_THRESHOLD_ONLY_UNCALIBRATED"
    assert result["detector_saturation_mask_implemented"] is False


def test_missing_wcs_raises_instead_of_inventing_position():
    with pytest.raises(ValueError):
        _screen(missing_wcs=True)


def test_weak_central_source_does_not_imply_no_physical_star():
    result=_screen(snr=0.3)
    assert result["status"]==INCOMPLETE
    assert not result["single_star_psf_authenticated"]


@pytest.mark.parametrize("kind",["reference_coadd","synthetic",""])
def test_original_science_image_gate(kind):
    with pytest.raises(ValueError,match="original dated science"):
        aperture_and_gaussian_centroid_screen(
            _fits(),expected_ra_deg=RA,expected_dec_deg=DEC,
            mjd_assumed_utc=59000,image_kind=kind)


@pytest.mark.parametrize("date",[0,54000,float("nan"),80001])
def test_observation_date_bounds_fail_closed(date):
    with pytest.raises(ValueError):
        aperture_and_gaussian_centroid_screen(
            _fits(),expected_ra_deg=RA,expected_dec_deg=DEC,
            mjd_assumed_utc=date)


def _m(sid,east=.1,north=.1,*,status=SUCCESS):
    return {"gaia_source_id":sid,
            "status":status,
            "fit_quality_allows_provisional_internal_control":status==SUCCESS,
            "gaussian_east_minus_gaia_arcsec":east,
            "gaussian_north_minus_gaia_arcsec":north,
            "aperture_east_minus_gaia_arcsec":east+.02,
            "aperture_north_minus_gaia_arcsec":north-.01}


def test_reference_holdout_uses_same_ids_and_marks_uncertainty_not_calibrated():
    s=audit_provisional_field_references([
        _m("101",.11,.08),_m("102",.14,.05),_m("103",.08,.11)])
    assert s["n_provisionally_image_model_consistent"]==3
    assert s["gaussian_reference_internal_holdout"]["n_usable_reference_models"]==3
    assert s["aperture_reference_internal_holdout"]["n_usable_reference_models"]==3
    assert not s["independently_calibrated_wcs"]


def test_reference_holdout_rejects_duplicates_and_poor_profiles():
    with pytest.raises(ValueError,match="Duplicate"):
        audit_provisional_field_references([_m("101"),_m("101")])
    s=audit_provisional_field_references([
        _m("101"),_m("102",status=REVIEW),_m("103")])
    assert s["n_provisionally_image_model_consistent"]==2
    assert s["gaussian_reference_internal_holdout"]["status"]==(
        "INSUFFICIENT_INDEPENDENT_REFERENCES_FOR_HOLDOUT")


EXPOSURE=("https://irsa.ipac.caltech.edu/ibe/data/ztf/products/sci/"
          "2018/0731/489120/ztf_20180731489120_000609_zg_c08_o_q4_sciimg.fits"
          "?center=65.91332400%2C24.93719500&size=90arcsec&gzip=false")


def _gaia():
    return {"source_id":"149623505110996992",
            "full_gaia_five_parameter_formal_covariance_propagated":True,
            "geocentric_parallax_adjusted_ra_deg":RA,
            "geocentric_parallax_adjusted_dec_deg":DEC,
            "formal_gaia_east_sigma_mas":.2,
            "formal_gaia_north_sigma_mas":.1,
            "high_or_missing_ruwe_quality_warning":False}


def test_real_science_reference_client_only_fetches_official_cutout():
    attempts=[]
    def fetch(url,*,timeout):
        attempts.append(url)
        assert url.startswith("https://irsa.ipac.caltech.edu/ibe/data/ztf/products/sci/")
        assert "size=45arcsec" in url
        return _fits()
    result=analyze_real_science_reference_cutout(
        EXPOSURE,_gaia(),mjd_assumed_utc=59000,fetch=fetch)
    assert len(attempts)==1
    assert result["status"]==SUCCESS
    assert result["science_fits_pixel_source_refitted"]
    assert not result["gaia_ztf_source_identity_confirmed"]


def test_missing_full_gaia_correlation_rejected_before_network():
    bad=_gaia()
    bad["full_gaia_five_parameter_formal_covariance_propagated"]=False
    with pytest.raises(ValueError):
        analyze_real_science_reference_cutout(
            EXPOSURE,bad,mjd_assumed_utc=59000,
            fetch=lambda *_:pytest.fail("would fetch"))


def test_remote_http_503_is_transport_not_source_nondetection():
    def fail(url,*,timeout):
        raise HTTPError(url,503,"archive down",None,None)
    out=analyze_real_science_reference_cutout(
        EXPOSURE,_gaia(),mjd_assumed_utc=59000,fetch=fail)
    assert out["status"]=="ZTF_SCIENCE_FITS_ACCESS_OR_VALIDATION_FAILED"
    assert out["http_status"]==503
    assert out["science_fits_pixel_source_refitted"] is False
    assert out["gaia_ztf_source_identity_confirmed"] is False


def test_outside_official_ztf_host_blocked_before_fetch():
    with pytest.raises(ValueError):
        analyze_real_science_reference_cutout(
            EXPOSURE.replace("irsa.ipac.caltech.edu","bad.example"),
            _gaia(),mjd_assumed_utc=59000)
