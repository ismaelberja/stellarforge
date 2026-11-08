"""Synthetic instrument-mask/PSF QA tests; cannot assert real source identity."""
from __future__ import annotations

import io
from urllib.error import HTTPError
import numpy as np
import pytest
from astropy.io import fits
from astropy.wcs import WCS

from stellarforge.v113_official_masks_psf import (
    BAD_MASK_BITS, MASK_SOURCE_BITS, SATURATION_BIT,
    official_ancillary_url,validate_ancillary_url,fetch_ancillary_fits,
    inspect_mask_against_science,inspect_native_center_psf,
    audit_one_science_source,audit_native_center_psf,
)

RA,DEC=65.913324,24.937195
SCIENCE=("https://irsa.ipac.caltech.edu/ibe/data/ztf/products/sci/"
         "2018/0411/467847/ztf_20180411467847_000535_zr_c11_o_q3_sciimg.fits"
         "?center=65.91332400%2C24.93719500&size=45arcsec&gzip=false")


def image(*,mask=False,bad_bit=0,shift=0,with_wcs=True,nonfinite=False):
    rng=np.random.default_rng(113)
    y,x=np.indices((64,64))
    if mask:
        data=np.zeros((64,64),dtype=np.uint16)
        data[32,32]=bad_bit
    else:
        data=(500+np.exp(-.5*(((x-32)/1.7)**2+((y-32)/1.8)**2))*500+
              1.5*rng.normal(size=x.shape)).astype(np.float32)
        if nonfinite:data[32,33]=np.nan
    h=fits.PrimaryHDU(data)
    if with_wcs:
        w=WCS(naxis=2)
        w.wcs.crpix=[33+shift,33]
        w.wcs.cdelt=[-1/3600,1/3600]
        w.wcs.crval=[RA,DEC]
        w.wcs.ctype=["RA---TAN","DEC--TAN"]
        h.header.update(w.to_header())
    b=io.BytesIO()
    h.writeto(b)
    return b.getvalue()


def center_stamp(sigma=1.4,nonfinite=False):
    y,x=np.indices((25,25))
    v=np.exp(-.5*(((x-12)/sigma)**2+((y-12)/sigma)**2))
    if nonfinite:v[:,:]=float("nan")
    b=io.BytesIO()
    fits.PrimaryHDU(v.astype("float32")).writeto(b)
    return b.getvalue()


def test_product_suffixes_official_sci_path_and_per_source_cutout():
    mask=official_ancillary_url(SCIENCE,"mskimg.fits")
    psf=official_ancillary_url(SCIENCE,"sciimgdaopsfcent.fits")
    assert mask.endswith("size=45arcsec&gzip=false")
    assert "_mskimg.fits?" in mask
    assert psf.endswith("_sciimgdaopsfcent.fits")
    assert "center=" not in psf
    validate_ancillary_url(mask,"mskimg.fits")
    validate_ancillary_url(psf,"sciimgdaopsfcent.fits")


@pytest.mark.parametrize("bad",[
    SCIENCE.replace("irsa.ipac.caltech.edu","evil.example"),
    SCIENCE.replace("https://","http://"),
    SCIENCE.replace("size=45arcsec","size=1000arcsec"),
    SCIENCE.replace("_sciimg.fits","_mskimg.fits"),
])
def test_product_url_rejects_host_http_size_and_wrong_input(bad):
    with pytest.raises(ValueError):
        official_ancillary_url(bad,"mskimg.fits")


def test_ancillary_endpoint_rejects_psf_with_cutout_query():
    url=official_ancillary_url(SCIENCE,"sciimgdaopsfcent.fits")
    with pytest.raises(ValueError):
        validate_ancillary_url(url+"?center=65,25","sciimgdaopsfcent.fits")


def test_bad_mask_bits_are_official_and_source_identification_bits_not_bad():
    assert BAD_MASK_BITS==6141
    assert MASK_SOURCE_BITS==2050
    assert BAD_MASK_BITS & MASK_SOURCE_BITS == 0
    assert SATURATION_BIT==256


def test_good_mask_with_source_detection_bits_not_a_single_star_certificate():
    result=inspect_mask_against_science(
        image(),image(mask=True,bad_bit=MASK_SOURCE_BITS),
        expected_ra_deg=RA,expected_dec_deg=DEC)
    assert result["status"]=="MASK_CORE_NO_DISQUALIFYING_BITS_PROVISIONAL_ONLY"
    assert result["n_core_bad_mask_pixels"]==0
    assert result["has_wcs_aligned_mask"] is True
    assert result["mask_proves_source_single"] is False
    assert result["gaia_ztf_physical_identity_confirmed"] is False


@pytest.mark.parametrize("bad_bit",[1,4,8,32,128,256,512,1024,4096])
def test_official_bad_mask_bits_flag_core(bad_bit):
    result=inspect_mask_against_science(
        image(),image(mask=True,bad_bit=bad_bit),
        expected_ra_deg=RA,expected_dec_deg=DEC)
    assert result["status"]=="MASK_CORE_HAS_BAD_BITS_OR_NONFINITE_SCIENCE"
    assert result["n_core_bad_mask_pixels"]==1
    if bad_bit==256:assert result["n_core_saturated_mask_pixels"]==1
    assert result["instrument_wcs_uncertainty_calibrated"] is False


def test_unmatched_wcs_grid_refuses_pixel_mask_alignment():
    result=inspect_mask_against_science(
        image(),image(mask=True,shift=.25),
        expected_ra_deg=RA,expected_dec_deg=DEC)
    assert result["status"]=="MASK_SCIENCE_WCS_GRID_MISMATCH"
    assert result["worst_grid_offset_pixels"]>=.24


def test_mask_wcs_missing_fails_closed():
    result=inspect_mask_against_science(
        image(),image(mask=True,with_wcs=False),
        expected_ra_deg=RA,expected_dec_deg=DEC)
    assert result["status"]=="MASK_SCIENCE_CELESTIAL_WCS_MISSING"
    assert not result["instrument_wcs_uncertainty_calibrated"]


def test_nonfinite_science_core_invalidates_mask_quality():
    result=inspect_mask_against_science(
        image(nonfinite=True),image(mask=True),
        expected_ra_deg=RA,expected_dec_deg=DEC)
    assert result["status"]=="MASK_CORE_HAS_BAD_BITS_OR_NONFINITE_SCIENCE"
    assert result["n_core_nonfinite_science_pixels"]==1


def test_mask_science_shape_mismatch_explicit():
    rawmask=image(mask=True)
    with fits.open(io.BytesIO(rawmask)) as hdul:
        data=hdul[0].data[:,0:60].copy()
        header=hdul[0].header.copy()
    out=io.BytesIO()
    fits.PrimaryHDU(data,header=header).writeto(out)
    result=inspect_mask_against_science(
        image(),out.getvalue(),expected_ra_deg=RA,expected_dec_deg=DEC)
    assert result["status"]=="MASK_IMAGE_SHAPE_MISMATCH"


def test_native_center_psf_stamp_is_only_center_proxy():
    out=inspect_native_center_psf(center_stamp())
    assert out["status"]=="NATIVE_CENTER_PSF_STAMP_PROVISIONALLY_PARSED"
    assert out["psf_shape_pixels"]==[25,25]
    assert out["positive_weighted_sigma_x_pixels"]==pytest.approx(1.4,abs=.01)
    assert out["psf_is_science_field_center_only"] is True
    assert out["psf_evaluated_at_source_position"] is False
    assert out["source_specific_psf_calibrated"] is False


def test_native_psf_all_invalid_does_not_certify_model():
    out=inspect_native_center_psf(center_stamp(nonfinite=True))
    assert out["status"] in ("NATIVE_CENTER_PSF_INCOMPLETE",
                              "NATIVE_CENTER_PSF_NO_POSITIVE_SIGNAL")
    assert not out["source_specific_psf_calibrated"]


def test_source_gate_uses_actual_same_date_sci_and_mask_products():
    called=[]
    def get_mask(url,*,kind,timeout):
        called.append((kind,url))
        assert "_mskimg.fits?" in url
        return image(mask=True)
    def get_sci(url,*,timeout):
        called.append(("science",url))
        assert "_sciimg.fits?" in url
        return image()
    out=audit_one_science_source(
        SCIENCE,source_ra_deg=RA,source_dec_deg=DEC,
        fetch_science=get_sci,fetch_other=get_mask)
    assert out["status"]=="MASK_CORE_NO_DISQUALIFYING_BITS_PROVISIONAL_ONLY"
    assert len(called)==2
    assert out["mask_good_core_cannot_authenticate_source"]
    assert not out["instrument_wcs_uncertainty_calibrated"]


def test_http_503_is_transport_not_clear_pixel_mask():
    def fail(url,*,kind,timeout):
        raise HTTPError(url,503,"archive down",None,None)
    out=audit_one_science_source(
        SCIENCE,source_ra_deg=RA,source_dec_deg=DEC,fetch_other=fail)
    assert out["http_status"]==503
    assert out["status"]=="ORIGINAL_ZTF_MASK_OR_SCIENCE_UNAVAILABLE"
    assert "n_core_bad_mask_pixels" not in out


def test_native_psf_http_access_failure_is_not_a_psf_model():
    out=audit_native_center_psf(
        SCIENCE,fetch_other=lambda url,*,kind,timeout: (_ for _ in ()).throw(
            HTTPError(url,503,"not available",None,None)))
    assert out["status"]=="NATIVE_CENTER_PSF_ACCESS_UNAVAILABLE"
    assert out["http_status"]==503
    assert not out["source_specific_psf_calibrated"]


def test_oversize_or_fake_fits_ancillary_response_is_rejected():
    maskurl=official_ancillary_url(SCIENCE,"mskimg.fits")
    class Response:
        def __enter__(self):return self
        def __exit__(self,*args):return False
        def read(self,size):return b"<html>temporary error</html>"
    with pytest.raises(ValueError,match="Missing or oversized"):
        fetch_ancillary_fits(
            maskurl,kind="mskimg.fits",
            opener=lambda req,timeout:Response())
