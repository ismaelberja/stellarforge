"""Entirely synthetic v1.6 PSF proxy tests; never assert binary/source identity."""
from __future__ import annotations

import io
from urllib.error import HTTPError

import numpy as np
import pytest
from astropy.io import fits
from astropy.wcs import WCS

from stellarforge.v16_psf_repeatability import (
    fit_local_gaussian_proxy, review_oid_band_psf,
    summarize_science_repeatability,
)

RA, DEC = 65.913324, 24.937195


def synthetic_image(*, snr=100., sigma_x=1.6, sigma_y=1.8,
                    second=False, gradient=0., no_wcs=False,
                    bad_pixels=False):
    rng = np.random.default_rng(1616)
    y, x = np.indices((64, 64), dtype=float)
    data = (1000 + gradient*(x-32) + 2*rng.normal(size=x.shape)
            + snr * 2 * np.exp(-.5 * (((x-32)/sigma_x)**2 +
                                     ((y-32)/sigma_y)**2)))
    if second:
        data += 100*np.exp(-.5 * (((x-37)/1.3)**2 + ((y-34)/1.3)**2))
    if bad_pixels:
        data[:] = np.nan
    hdu = fits.PrimaryHDU(data.astype("float32"))
    if not no_wcs:
        w = WCS(naxis=2)
        w.wcs.crpix = [33, 33]
        w.wcs.cdelt = [-1/3600, 1/3600]
        w.wcs.crval = [RA, DEC]
        w.wcs.ctype = ["RA---TAN", "DEC--TAN"]
        hdu.header.update(w.to_header())
    stream = io.BytesIO()
    hdu.writeto(stream)
    return stream.getvalue()


def test_noisy_gaussian_psf_fwhm_and_signed_offset_recovery():
    out = fit_local_gaussian_proxy(
        synthetic_image(snr=170), expected_ra_deg=RA, expected_dec_deg=DEC)
    assert out["status"] in (
        "PSF_PROXY_PROVISIONAL_ONLY", "PSF_PROXY_REVIEW_REQUIRED")
    assert out["central_peak_snr_proxy"] > 20
    assert out["fitted_fwhm_x_arcsec"] == pytest.approx(2.35482*1.6, abs=.6)
    assert out["fitted_fwhm_y_arcsec"] == pytest.approx(2.35482*1.8, abs=.6)
    assert out["fitted_centroid_distance_from_Gaia_arcsec"] < 0.4
    assert not out["scientific_psf_calibrated"]
    assert not out["field_deblended"]


def test_gradient_is_a_modelled_nuisance_but_not_a_physical_result():
    out = fit_local_gaussian_proxy(
        synthetic_image(snr=170,gradient=.3), expected_ra_deg=RA,
        expected_dec_deg=DEC)
    assert out["status"] in (
        "PSF_PROXY_PROVISIONAL_ONLY", "PSF_PROXY_REVIEW_REQUIRED")
    assert out["median_absolute_residual_over_noise"] < 3
    assert out["gaia_ztf_identity_confirmed"] is False


def test_secondary_source_nearby_never_promoted_to_companion():
    out = fit_local_gaussian_proxy(
        synthetic_image(snr=170, second=True),
        expected_ra_deg=RA, expected_dec_deg=DEC)
    assert out["status"] in (
        "PSF_PROXY_PROVISIONAL_ONLY", "PSF_PROXY_REVIEW_REQUIRED")
    assert not out["astrophysical_companion_confirmed"]
    assert out["max_outer_positive_residual_over_noise"] > 3


def test_weak_central_signal_not_fitted():
    out = fit_local_gaussian_proxy(
        synthetic_image(snr=1.0), expected_ra_deg=RA, expected_dec_deg=DEC)
    assert out["status"] == "NO_SIGNIFICANT_CENTRAL_PEAK_FOR_PROXY"
    assert not out["gaia_ztf_identity_confirmed"]


def test_invalid_pixels_fail_closed():
    out = fit_local_gaussian_proxy(
        synthetic_image(bad_pixels=True), expected_ra_deg=RA,
        expected_dec_deg=DEC)
    assert out["status"] == "V15_IMAGE_GATE_INCOMPLETE"
    assert not out["field_deblended"]


def test_absent_wcs_rejected():
    with pytest.raises(ValueError):
        fit_local_gaussian_proxy(
            synthetic_image(no_wcs=True),
            expected_ra_deg=RA, expected_dec_deg=DEC)


@pytest.mark.parametrize("kind", ["synthetic", "unspecified", "other"])
def test_bad_image_kind_rejected(kind):
    with pytest.raises(ValueError, match="Invalid image kind"):
        fit_local_gaussian_proxy(
            synthetic_image(), expected_ra_deg=RA,
            expected_dec_deg=DEC, image_kind=kind)


def mock_psf(name, east=0.1, north=0.2, fwhm=3.2):
    return {
        "status": "PSF_PROXY_PROVISIONAL_ONLY",
        "fits_sha256": name,
        "fitted_centroid_east_minus_Gaia_arcsec": east,
        "fitted_centroid_north_minus_Gaia_arcsec": north,
        "fitted_fwhm_x_arcsec": fwhm,
        "fitted_fwhm_y_arcsec": fwhm,
        "gaia_ztf_identity_confirmed": False,
    }


def test_repeatability_requires_two_distinct_science_frames():
    data = [
        {"kind":"science", "mjd":58330, "fit": mock_psf("same")},
        {"kind":"science", "mjd":58340, "fit": mock_psf("same")},
        {"kind":"reference_coadd", "mjd":None, "fit": mock_psf("ref")},
    ]
    s = summarize_science_repeatability(data)
    assert s["n_independent_science_images"] == 1
    assert s["status"] == "INSUFFICIENT_INDEPENDENT_SCIENCE_EXPOSURES"


def test_signed_tangent_offset_repeatability_quantified_not_verified():
    samples = [
        {"kind":"science", "mjd":59000, "fit": mock_psf("a",.1,.2,3)},
        {"kind":"science", "mjd":59020, "fit": mock_psf("b",.4,.6,4)},
        {"kind":"reference_coadd","mjd":None,"fit": mock_psf("c",7,7,10)},
    ]
    result = summarize_science_repeatability(samples)
    assert result["n_independent_science_images"] == 2
    assert result["max_pairwise_signed_centroid_residual_difference_arcsec"] == .5
    assert result["mjd_span_days"] == 20
    assert result["median_gaussian_fwhm_proxy_arcsec"] == 3.5
    assert result["reference_images_excluded"] is True
    assert result["scientific_astrometric_consistency_confirmed"] is False


def one_curve():
    return {
        "ztf_oid": "609108400001155", "band": "zg",
        "candidates": [
            {"kind":"science", "mjd":59000, "url":"u1",
             "expected_ra_deg":RA, "expected_dec_deg":DEC},
            {"kind":"science", "mjd":59001, "url":"u2",
             "expected_ra_deg":RA, "expected_dec_deg":DEC},
            {"kind":"science", "mjd":59002, "url":"u3",
             "expected_ra_deg":RA, "expected_dec_deg":DEC},
            {"kind":"reference_coadd", "mjd":None, "url":"u4",
             "expected_ra_deg":RA, "expected_dec_deg":DEC},
        ],
    }


def test_multiple_science_frames_retained_not_stopping_on_first_fit():
    def get(url, timeout):
        return url.encode("ascii")
    def fit(raw, **_):
        name=raw.decode()
        return mock_psf(name, .1 if name=="u1" else .2, .3)
    out = review_oid_band_psf(one_curve(), fetch=get, fit=fit)
    assert out["images_attempted"] == 3
    assert out["science_images_with_psf_proxy"] == 3
    assert out["repeatability"]["n_independent_science_images"] == 3
    assert out["reference_coadd_fallback"] is False
    assert out["gaia_ztf_physical_identity_confirmed"] is False


def test_reference_only_after_science_transport_failures():
    def get(url, timeout):
        if url!="u4":
            raise HTTPError(url, 503, "temporarily unavailable", None, None)
        return b"reference"
    out=review_oid_band_psf(
        one_curve(), fetch=get, fit=lambda raw, **_: mock_psf("ref"))
    assert out["images_attempted"] == 4
    assert out["science_images_with_psf_proxy"] == 0
    assert out["images_with_provisional_psf_proxy"] == 1
    assert out["reference_coadd_fallback"] is True
    assert out["repeatability"]["status"] == (
        "INSUFFICIENT_INDEPENDENT_SCIENCE_EXPOSURES")
    assert not out["psf_deblending_verified"]


def test_transport_error_status_preserved():
    def unavailable(url, timeout):
        raise HTTPError(url, 503, "Unavail", None, None)
    out=review_oid_band_psf(one_curve(), fetch=unavailable)
    assert out["images_with_provisional_psf_proxy"] == 0
    assert all(x["status"] == "FITS_OR_MODEL_FAILED" for x in out["attempts"])
    assert all(x["http_status"] == 503 for x in out["attempts"])
    assert not out["psf_deblending_verified"]
