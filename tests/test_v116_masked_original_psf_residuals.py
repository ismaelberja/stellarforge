"""v1.16 synthetic original ZTF science/bitmask spatial-PSF residual tests."""
from __future__ import annotations

import io
from urllib.error import HTTPError

import numpy as np
import pytest
from astropy.io import fits
from astropy.wcs import WCS

from stellarforge.v116_masked_original_psf_residuals import (
    _masked_fit,audit_original_source_psf_residuals,
    MAX_PHASE_DISAGREEMENT_PIX,
)
from stellarforge.v115_spatial_psf import evaluate_spatial_psf_shape

RA=65.913324
DEC=24.937195
URL=("https://irsa.ipac.caltech.edu/ibe/data/ztf/products/sci/"
     "2018/0411/467847/ztf_20180411467847_000535_zr_c11_o_q3_sciimg.fits"
     "?center=65.91332400%2C24.93719500&size=45arcsec&gzip=false")


def model_parsed():
    side=47
    n=3
    tbl=np.zeros((n,side,side),dtype=float)
    return {
        "source_sha256":"a"*64,
        "detector_field_center_x":1535.5,
        "detector_field_center_y":1539.5,
        "analytic_hwhm_x_pixels":1.112774,
        "analytic_hwhm_y_pixels":.9879758,
        "gaussian_peak_amplitude_parameter":3579.729,
        "lookup_side_samples":side,
        "n_lookup_tables":n,
        "tables":tbl,
    }


def _wcs(*,x=.3,y=.4,offset=0,missing=False):
    if missing:return fits.Header()
    w=WCS(naxis=2)
    w.wcs.crpix=[36+x+offset,36+y]
    w.wcs.crval=[RA,DEC]
    w.wcs.cdelt=[-1/3600,1/3600]
    w.wcs.ctype=["RA---TAN","DEC--TAN"]
    return w.to_header()


def _fits(arr,*,wx=.3,wy=.4,wcs_shift=0,missing_wcs=False):
    b=io.BytesIO()
    fits.PrimaryHDU(arr,header=_wcs(
        x=wx,y=wy,offset=wcs_shift,missing=missing_wcs)).writeto(b)
    return b.getvalue()


def source_pair(*,bad_bit=0,mask_shift=0,sci_missing_wcs=False,
                badsky=False,flat=False,star_flux=9000,
                native_x=1535.3,native_y=1539.4):
    rng=np.random.default_rng(116)
    h,w=72,72
    yy,xx=np.indices((h,w))
    data=(1010+0.11*(xx-35)+0.05*(yy-35)+
          (0 if flat else rng.normal(0,1.6,(h,w)))).astype(float)
    psf=evaluate_spatial_psf_shape(model_parsed(),x=native_x,y=native_y,
                                   frac_x=.3,frac_y=.4)
    data[24:47,24:47]+=star_flux*psf
    if badsky:
        r=np.hypot(xx-35.3,yy-35.4)
        data[(r>=14)&(r<=22)]=float("nan")
    mask=np.zeros((h,w),dtype=np.uint16)
    mask[35,35]=bad_bit
    return (
        _fits(data.astype("float32"),missing_wcs=sci_missing_wcs),
        _fits(mask,wcs_shift=mask_shift),
    )


def measured(science,mask,*,native_x=1535.3,native_y=1539.4):
    return _masked_fit(
        science,mask,model_parsed(),
        original_psfcat_ra=RA,original_psfcat_dec=DEC,
        native_psfcat_x=native_x,native_psfcat_y=native_y)


def test_valid_realistic_single_source_masked_psf_fit_reports_holdout_noise():
    sci,mask=source_pair()
    d=measured(sci,mask)
    assert d["status"]=="PROVISIONAL_ORIGINAL_MASKED_PSF_PIXEL_RESIDUAL_SCREEN_PASSED"
    assert d["local_masked_psf_model_fit_completed"] is True
    assert d["science_and_mask_wcs_registration_within_0p05_pixel"]
    assert d["n_unmasked_fit_pixels"]>=150
    assert d["n_unmasked_sky_annulus_pixels"]>=230
    assert d["same_image_holdout_residual_rms_over_sky_noise_proxy"]<3
    assert d["fitted_native_psf_amplitude_dn_unscaled"]==pytest.approx(9000,rel=.04)
    assert not d["independently_authenticated_gaia_ztf_identity"]
    assert not d["genuine_independent_stellar_psf_control_validation"]
    assert d["checkerboard_pixels_are_same_source_image_not_independent_stars"]


@pytest.mark.parametrize("badbit",[1,4,8,16,32,64,128,256,512,1024,4096])
def test_original_masked_core_bad_pixel_or_saturation_blocks_fit(badbit):
    sci,mask=source_pair(bad_bit=badbit)
    result=measured(sci,mask)
    assert result["status"]=="SOURCE_CORE_HAS_BAD_OR_SATURATED_OR_NONFINITE_PIXELS"
    assert not result["local_masked_psf_model_fit_completed"]
    assert result["n_core_bad_mask_pixels"]==1
    if badbit==256:
        assert result["n_core_saturated_pixels"]==1


@pytest.mark.parametrize("source_marker_bit",[2,2048])
def test_ztf_extracted_source_bits_not_bad_detector_pixels(source_marker_bit):
    sci,mask=source_pair(bad_bit=source_marker_bit)
    result=measured(sci,mask)
    assert result["local_masked_psf_model_fit_completed"]
    assert result["n_masked_core_pixels"]==0


def test_mask_and_science_wcs_nonregistered_fails_before_seeing_residuals():
    sci,mask=source_pair(mask_shift=.3)
    d=measured(sci,mask)
    assert d["status"]=="SCIENCE_MASK_WCS_PIXEL_GRID_NOT_ALIGNED"
    assert not d["local_masked_psf_model_fit_completed"]


def test_missing_astrometric_wcs_fails_closed():
    sci,mask=source_pair(sci_missing_wcs=True)
    d=measured(sci,mask)
    assert d["status"]=="ORIGINAL_SCIENCE_MASK_CELESTIAL_WCS_MISSING"


def test_bad_sky_or_nonfinite_annulus_blocks_photometric_measurement():
    sci,mask=source_pair(badsky=True)
    d=measured(sci,mask)
    assert d["status"]=="INSUFFICIENT_UNMASKED_SKY_ANNULUS_PIXELS"
    assert not d["true_photometric_flux_calibration_completed"]


def test_psf_catalogue_subpixel_phase_mismatch_detected_separately():
    sci,mask=source_pair()
    d=measured(sci,mask,native_x=1535.04)
    assert d["status"]=="ORIGINAL_PSF_CATALOGUE_AND_CUTOUT_SUBPIXEL_PHASE_MISMATCH"
    assert d["native_vs_wcs_subpixel_x_difference"]>MAX_PHASE_DISAGREEMENT_PIX


def test_wrong_detector_geometry_does_not_make_fake_valid_psf():
    sci,mask=source_pair()
    d=measured(sci,mask,native_x=8000)
    assert d["status"] in (
        "ORIGINAL_SPATIAL_DAOPHOT_PSF_MODEL_UNEVALUABLE",
        "ORIGINAL_PSF_CATALOGUE_AND_CUTOUT_SUBPIXEL_PHASE_MISMATCH",
    )
    assert not d["local_masked_psf_model_fit_completed"]


def test_mismatched_fits_array_sizes_cannot_register_mask_to_science():
    sci,mask=source_pair()
    with fits.open(io.BytesIO(mask),memmap=False) as f:
        array=f[0].data[:66,:66].copy()
        hdr=f[0].header.copy()
    stream=io.BytesIO()
    fits.PrimaryHDU(array,header=hdr).writeto(stream)
    d=measured(sci,stream.getvalue())
    assert d["status"]=="ORIGINAL_SCIENCE_MASK_PIXEL_SHAPE_MISMATCH"


def test_malformed_fractional_mask_value_rejected_before_psf_fit():
    sci,mask=source_pair()
    with fits.open(io.BytesIO(mask),memmap=False) as f:
        data=np.asarray(f[0].data,dtype="float32")
        data[35,36]=.5
        h=f[0].header.copy()
    b=io.BytesIO()
    fits.PrimaryHDU(data,header=h).writeto(b)
    d=measured(sci,b.getvalue())
    assert d["status"]=="MASK_PIXEL_VALUES_INVALID"


def test_unmodeled_additional_local_source_causes_profile_review():
    sci,mask=source_pair()
    with fits.open(io.BytesIO(sci),memmap=False) as f:
        data=np.array(f[0].data,dtype="float32")
        hdr=f[0].header.copy()
    yy,xx=np.indices(data.shape)
    # Deliberately add a peak on the held-out PSF footprint.
    data+=600*np.exp(-.5*((xx-40.2)**2+(yy-37.1)**2)/1.3**2)
    b=io.BytesIO()
    fits.PrimaryHDU(data,header=hdr).writeto(b)
    d=measured(b.getvalue(),mask)
    assert d["status"]=="ORIGINAL_MASKED_PSF_PIXEL_RESIDUAL_REVIEW_REQUIRED"
    assert d["same_image_holdout_residual_rms_over_sky_noise_proxy"]>3
    assert not d["physical_variability_or_companion_confirmed"]


def test_http503_original_mask_is_transport_failure_not_astro_nondetection():
    def unavailable(url,*,kind,timeout):
        raise HTTPError(url,503,"unavailable",None,None)
    d=audit_original_source_psf_residuals(
        URL,model_parsed(),source_ra=RA,source_dec=DEC,
        native_x=1535.3,native_y=1539.4,
        fetch_mask=unavailable)
    assert d["status"]=="ORIGINAL_SCIENCE_OR_MASK_ACCESS_OR_FORMAT_FAILED"
    assert d["http_status"]==503
    assert not d["physical_variability_or_companion_confirmed"]


def test_official_access_builds_coincident_60arcsec_mask_and_science_url():
    sci,mask=source_pair()
    seen=[]
    def mfetch(url,*,kind,timeout):
        seen.append((kind,url))
        assert "_mskimg.fits?" in url
        assert "size=60arcsec" in url
        return mask
    def sfetch(url,*,timeout):
        seen.append(("science",url))
        assert "_sciimg.fits?" in url
        assert "size=60arcsec" in url
        return sci
    d=audit_original_source_psf_residuals(
        URL,model_parsed(),source_ra=RA,source_dec=DEC,
        native_x=1535.3,native_y=1539.4,
        fetch_mask=mfetch,fetch_science=sfetch)
    assert len(seen)==2
    assert d["local_masked_psf_model_fit_completed"]
    assert seen[0][1].split("_mskimg.fits")[0]==seen[1][1].split("_sciimg.fits")[0]
