"""Synthetic FITS/WCS validation: never download astronomical observations in tests."""
from __future__ import annotations

import csv
import io
from urllib.error import HTTPError

import numpy as np
import pytest
from astropy.io import fits
from astropy.wcs import WCS

from stellarforge.v15_image_pixels import (
    inspect_fits_cutout, fetch_fits_cutout,
    propose_image_candidates, inspect_available_image_candidates,
)


RA, DEC = 65.913324, 24.937195


def synthetic_fits(*, companion=True, no_peaks=False,
                   valid_wcs=True, target_on_edge=False):
    rng = np.random.default_rng(98)
    h, w = 64, 64
    data = rng.normal(loc=500.0, scale=5.0, size=(h, w))
    yy, xx = np.indices(data.shape)
    if not no_peaks:
        sx, sy = (1.0, 1.0) if target_on_edge else (32., 32.)
        data += 240 * np.exp(-((xx - sx)**2 + (yy - sy)**2)/(2*1.2**2))
        if companion:
            data += 120 * np.exp(-((xx - 40.)**2 + (yy - 33.)**2)/(2*1.2**2))
    hdu = fits.PrimaryHDU(data.astype(np.float32))
    if valid_wcs:
        wcs = WCS(naxis=2)
        wcs.wcs.crpix = [33.0 if not target_on_edge else 63.0, 33.0]
        wcs.wcs.cdelt = [-1/3600, 1/3600]
        wcs.wcs.crval = [RA, DEC]
        wcs.wcs.ctype = ["RA---TAN", "DEC--TAN"]
        hdu.header.update(wcs.to_header())
    raw = io.BytesIO()
    hdu.writeto(raw)
    return raw.getvalue()


def test_two_synthetic_stars_and_valid_wcs_remain_unconfirmed():
    result = inspect_fits_cutout(synthetic_fits(), expected_ra_deg=RA,
                                 expected_dec_deg=DEC)
    assert result["status"] == "PIXEL_WCS_PROVISIONAL_SCREEN_COMPLETED"
    assert result["wcs_checked"] and result["central_local_maximum_detected"]
    assert result["n_additional_local_maxima_within_12_arcsec"] >= 1
    assert result["pixel_scale_arcsec_mean"] == pytest.approx(1, abs=.01)
    assert result["central_peak_offset_arcsec"] < 1
    assert result["fits_sha256"]
    assert result["psf_fitted"] is False
    assert result["confirmed_astrophysical_match"] is False
    assert result["image_contamination_ruled_out"] is False


def test_no_peaks_does_not_become_a_clean_field():
    result = inspect_fits_cutout(
        synthetic_fits(no_peaks=True), expected_ra_deg=RA, expected_dec_deg=DEC)
    assert result["status"] == "PIXEL_WCS_PROVISIONAL_SCREEN_COMPLETED"
    assert result["central_local_maximum_detected"] is False
    assert result["image_contamination_ruled_out"] is False


def test_missing_wcs_is_rejected():
    with pytest.raises(ValueError, match="celestial WCS"):
        inspect_fits_cutout(synthetic_fits(valid_wcs=False),
                            expected_ra_deg=RA, expected_dec_deg=DEC)


def test_missing_pixels_in_image_rejected():
    img = np.full((64, 64), np.nan, dtype=float)
    hdu = fits.PrimaryHDU(img)
    w = WCS(naxis=2)
    w.wcs.crpix = [33, 33]
    w.wcs.cdelt = [-1/3600, 1/3600]
    w.wcs.crval = [RA, DEC]
    w.wcs.ctype = ["RA---TAN", "DEC--TAN"]
    hdu.header.update(w.to_header())
    stream = io.BytesIO()
    hdu.writeto(stream)
    result = inspect_fits_cutout(stream.getvalue(), expected_ra_deg=RA,
                                 expected_dec_deg=DEC)
    assert result["status"] == "IMAGE_TOO_MANY_INVALID_PIXELS"
    assert result["wcs_checked"] is False


def test_target_outside_usable_cutout_does_not_assert_detection():
    result = inspect_fits_cutout(
        synthetic_fits(target_on_edge=True),
        expected_ra_deg=RA, expected_dec_deg=DEC)
    assert result["status"] == "PREDICTED_GAIA_TARGET_OUTSIDE_USABLE_IMAGE"
    assert not result["confirmed_astrophysical_match"]


@pytest.mark.parametrize("bad_sigma", [0, 2.0, 16, float("nan")])
def test_sigma_contract(bad_sigma):
    with pytest.raises(ValueError):
        inspect_fits_cutout(synthetic_fits(), expected_ra_deg=RA,
                            expected_dec_deg=DEC, peak_sigma=bad_sigma)


def test_ztf_response_html_is_rejected_without_exposure():
    url = ("https://irsa.ipac.caltech.edu/ibe/data/ztf/products/sci/2018/0411/"
           "467847/ztf_20180411467847_000535_zr_c11_o_q3_sciimg.fits"
           "?center=65.913324,24.937195&size=45arcsec&gzip=false")
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self, n): return b"<html>failure</html>"
    with pytest.raises(ValueError):
        fetch_fits_cutout(url, opener=lambda req, timeout: Response())


@pytest.mark.parametrize("url", [
    "https://attacker.example.org/ibe/data/ztf/products/ref/anything.fits?center=12,3&size=45arcsec",
    "http://irsa.ipac.caltech.edu/ibe/data/ztf/products/ref/anything.fits?center=12,3&size=45arcsec",
    "https://irsa.ipac.caltech.edu/ibe/data/ztf/products/ref/anything.fits?center=12,3&size=300arcsec",
    "https://irsa.ipac.caltech.edu/ibe/data/ztf/products/ref/anything.fits?center=NaN,3&size=45arcsec",
])
def test_reject_bad_image_urls_before_network(url):
    with pytest.raises(ValueError):
        fetch_fits_cutout(url)


def _ztf_rows(n=15):
    output = io.StringIO()
    cols = ["oid", "mjd", "catflags", "filtercode",
            "filefracday", "field", "ccdid", "qid"]
    writer = csv.DictWriter(output, fieldnames=cols)
    writer.writeheader()
    for band, oid in (("zg", "609108400001155"), ("zr", "609208400001969")):
        for i in range(n):
            writer.writerow({
                "oid": oid, "mjd": 58330+i, "catflags": 0,
                "filtercode": band,
                "filefracday": f"201808{(i+1):02d}123456" if i<31 else "20180801123456",
                "field": "609", "ccdid": "0x8", "qid": "0x4",
            })
    return output.getvalue().encode()


def test_image_candidate_limit_and_distinct_oid_bands():
    result = propose_image_candidates(
        _ztf_rows(), target_ra_deg=RA, target_dec_deg=DEC,
        target_pmra=7.448, target_pmdec=-21.849)
    assert len(result) == 2
    for curve in result:
        assert len(curve["candidates"]) == 4
        assert curve["candidates"][-1]["kind"] == "reference_coadd"
        assert len({row["url"] for row in curve["candidates"]}) == 4
        assert curve["photometric_identity_verified"] is False


def test_fetch_errors_are_recorded_not_turned_into_non_detection():
    groups = propose_image_candidates(
        _ztf_rows(), target_ra_deg=RA, target_dec_deg=DEC,
        target_pmra=7.448, target_pmdec=-21.849)
    def unavailable(url, *, timeout):
        raise HTTPError(url, 503, "Service unavailable", hdrs=None, fp=None)
    result = inspect_available_image_candidates(
        groups, fetch=unavailable, max_attempts_per_curve=2)
    assert all(x["status"] == "NO_USABLE_FITS_PIXEL_SCREEN" for x in result)
    assert all([a["http_status"] for a in x["attempts"]] == [503, 503]
               for x in result)
    assert all(x["gaia_ztf_astrophysical_identity_confirmed"] is False
               for x in result)
