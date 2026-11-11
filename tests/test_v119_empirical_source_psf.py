"""v1.19 synthetic source-disjoint empirical PSF/variance tests."""
from __future__ import annotations

import io
import math

import numpy as np
import pytest
from astropy.io import fits
from astropy.wcs import WCS

from stellarforge.v119_empirical_source_psf import (
    extract_original_source_stamp,fetch_original_source_stamp,
    empirical_psf_leave_one_source_out,header_noise_metadata,
    evaluate_other_star_empirical_psf,_fixed_shape_fit_rms,
)
from stellarforge.v115_spatial_psf import evaluate_spatial_psf_shape

RA=76.597253
DEC=24.538792
SCIENCE=("https://irsa.ipac.caltech.edu/ibe/data/ztf/products/sci/"
         "2018/0411/467847/ztf_20180411467847_000535_zr_c11_o_q3_sciimg.fits"
         "?center=76.59725300%2C24.53879200&size=45arcsec&gzip=false")


def fake_daophot():
    return {
        "source_sha256":"a"*64,
        "detector_field_center_x":1535.5,
        "detector_field_center_y":1539.5,
        "analytic_hwhm_x_pixels":1.112774,
        "analytic_hwhm_y_pixels":.9879758,
        "gaussian_peak_amplitude_parameter":3579.729,
        "lookup_side_samples":47,
        "n_lookup_tables":3,
        "tables":np.zeros((3,47,47),dtype=float),
    }


def original_stamp_image(gaia_id="10001",*,seed=18,phase_x=.3,phase_y=.4,
                         native_x=1535.3,native_y=1539.4,
                         gain=None,bad_pixel=False,shift_mask=0.0,
                         other_star=False,amplitude=12000.,extra_noise=2.0):
    rng=np.random.default_rng(seed)
    n=72
    y,x=np.indices((n,n))
    data=1000+.12*(x-35)+.08*(y-35)+rng.normal(0,extra_noise,(n,n))
    yy,xx=np.mgrid[-11:12,-11:12]
    # An original synthetic PSF that need not be a Gaussian native model.
    radius_sq=(xx-phase_x)**2+(yy-phase_y)**2
    image_psf=(np.exp(-radius_sq/(2*1.7**2))
               +.04*np.exp(-((xx-2.5-phase_x)**2+
                             (yy+.4-phase_y)**2)/(2*.9**2)))
    image_psf/=np.sum(image_psf)
    data[24:47,24:47]+=amplitude*image_psf
    if other_star:
        data+=400*np.exp(-((x-40)**2+(y-37)**2)/(2*.8**2))
    msk=np.zeros((n,n),dtype="uint16")
    if bad_pixel:msk[35,35]=256
    w=WCS(naxis=2)
    w.wcs.crpix=[36+phase_x,36+phase_y]
    w.wcs.crval=[RA,DEC]
    w.wcs.cdelt=[-1/3600,1/3600]
    w.wcs.ctype=["RA---TAN","DEC--TAN"]
    hdr=w.to_header()
    if gain is not None:hdr["GAIN"]=gain
    def encode(a,header):
        buff=io.BytesIO()
        fits.PrimaryHDU(a,header=header).writeto(buff)
        return buff.getvalue()
    mhdr=hdr.copy()
    mhdr["CRPIX1"]=mhdr["CRPIX1"]+shift_mask
    return (
        encode(data.astype("float32"),hdr),
        encode(msk,mhdr),
    )


def extracted(gaia_id="10001",*,seed=18,min_source_snr_proxy=10.,**opts):
    s,m=original_stamp_image(gaia_id,seed=seed,**opts)
    return extract_original_source_stamp(
        s,m,source_ra=RA,source_dec=DEC,
        native_x=opts.get("native_x",1535.3),
        native_y=opts.get("native_y",1539.4),
        gaia_source_id=gaia_id,
        min_source_snr_proxy=min_source_snr_proxy,
    )


def test_true_masked_source_pixels_yield_normalized_empirical_shape():
    s=extracted()
    assert s["aligned_empirical_shape"].shape==(23,23)
    assert s["aligned_empirical_shape"].sum()==pytest.approx(1)
    assert np.min(s["aligned_empirical_shape"])>=0
    assert s["source_snr_proxy"]>=10
    assert s["n_original_sky_pixels"]>=230
    assert s["n_original_sky_pixels"]<1000
    assert s["science_fits_sha256"]!=s["mask_fits_sha256"]
    assert not s["physical_gaia_ztf_identity_authenticated"]


def test_four_distinct_source_images_construct_four_true_source_disjoint_folds():
    stamps=[extracted(str(10000+i),seed=10+i) for i in range(4)]
    result=empirical_psf_leave_one_source_out(
        stamps,native_spatial_psf=fake_daophot())
    assert result["status"]=="ORIGINAL_ZTF_DISTINCT_SOURCE_PSF_SHAPE_LOOCV_COMPLETED"
    assert result["n_distinct_eligible_source_stars"]==4
    assert result["n_source_disjoint_psf_validation_folds"]==4
    assert result["n_source_disjoint_training_models"]==4
    for fold in result["heldout_source_folds"]:
        assert fold["n_distinct_other_star_training_sources"]==3
        assert fold["heldout_new_gaia_candidate_source_id"] not in fold["training_source_ids"]
        assert fold["psf_pixels_built_without_heldout_source"]
        assert fold["empirical_holdout_source_metrics"][
            "same_heldout_source_image_checkerboard_rms_dn"]>0
        assert fold["native_spatial_daophot_holdout_source_metrics"][
            "same_heldout_source_image_checkerboard_rms_dn"]>0
    assert result["original_ZTF_DAOPhot_training_star_membership_authenticated"] is False
    assert result["new_physical_gaia_ztf_companion_or_variability_confirmed"] is False
    assert result["source_positions_inherited_from_native_ZTF_psfcat"]


@pytest.mark.parametrize("n",[0,1,2,3])
def test_insufficient_new_distinct_source_ids_not_mislabeled_independent_psf(n):
    stamps=[extracted(str(1000+i),seed=50+i) for i in range(n)]
    r=empirical_psf_leave_one_source_out(
        stamps,native_spatial_psf=fake_daophot())
    assert r["status"]=="INSUFFICIENT_DISTINCT_REAL_SOURCE_STARS_FOR_LOOCV"
    assert r["n_source_disjoint_psf_validation_folds"]==0
    assert not r["independent_instrument_psf_error_calibration_completed"]


def test_duplicate_gaia_id_cannot_leak_star_pixels_across_training_holdout():
    stamps=[extracted("10001",seed=1),extracted("10001",seed=2),
            extracted("10003",seed=3),extracted("10004",seed=4)]
    with pytest.raises(ValueError,match="twice"):
        empirical_psf_leave_one_source_out(stamps)


def test_heldout_faint_or_bad_source_not_used_to_build_empirical_template():
    a=[extracted(str(100+i),seed=10+i) for i in range(3)]
    r=empirical_psf_leave_one_source_out(a+[{"gaia_source_id":"999",
        "status":"ORIGINAL_IMAGE_MASK_OR_EMPIRICAL_TRAINING_INELIGIBLE"}])
    assert r["status"]=="INSUFFICIENT_DISTINCT_REAL_SOURCE_STARS_FOR_LOOCV"


def test_original_saturated_bad_pixel_prevents_source_template_training():
    s,m=original_stamp_image(bad_pixel=True)
    with pytest.raises(ValueError,match="MASKED"):
        extract_original_source_stamp(
            s,m,source_ra=RA,source_dec=DEC,native_x=1535.3,
            native_y=1539.4,gaia_source_id="123")


def test_original_science_mask_wcs_offset_rejected_before_template_creation():
    s,m=original_stamp_image(shift_mask=.15)
    with pytest.raises(ValueError,match="MISREGISTERED"):
        extract_original_source_stamp(s,m,source_ra=RA,source_dec=DEC,
                                      native_x=1535.3,native_y=1539.4,
                                      gaia_source_id="123")


def test_native_source_fractional_phase_mismatch_fails_closed():
    s,m=original_stamp_image()
    with pytest.raises(ValueError,match="PHASE_CONFLICT"):
        extract_original_source_stamp(s,m,source_ra=RA,source_dec=DEC,
                                      native_x=1535.04,native_y=1539.4,
                                      gaia_source_id="123")


def test_low_snr_star_disallowed_from_training():
    s,m=original_stamp_image(amplitude=30,extra_noise=3)
    with pytest.raises(ValueError,match="TOO_WEAK"):
        extract_original_source_stamp(s,m,source_ra=RA,source_dec=DEC,
                                      native_x=1535.3,native_y=1539.4,
                                      gaia_source_id="123")


def test_noise_proxy_uses_original_fits_gain_only_when_header_present():
    without=header_noise_metadata({},sky_mad_dn=2.1)
    assert without["gain_read_directly_from_original_fits_header"] is False
    assert without["calibrated_per_pixel_noise_covariance_available"] is False
    with_gain=header_noise_metadata(
        {"GAIN":1.45,"RDNOISE":6.},
        sky_mad_dn=2.1)
    assert with_gain["gain_electrons_per_dn_metadata"]==pytest.approx(1.45)
    assert with_gain["read_noise_electrons_header_metadata"]==pytest.approx(6)
    assert with_gain["full_detector_noise_calibration_completed"] is False


@pytest.mark.parametrize("gain",[-1,0,1e4,"not a number",float("nan")])
def test_unphysical_header_gain_is_never_invented(gain):
    x=header_noise_metadata({"GAIN":gain},sky_mad_dn=1.2)
    assert not x["gain_read_directly_from_original_fits_header"]


def test_realistic_gain_metadata_changes_optional_var_proxy_not_full_error():
    stamps=[extracted(str(1000+i),seed=i+10,gain=1.5) for i in range(4)]
    r=empirical_psf_leave_one_source_out(stamps)
    assert r["n_source_disjoint_psf_validation_folds"]==4
    assert all(
        x["empirical_holdout_source_metrics"]["header_gain_applied_to_optional_source_shot_noise"]
        for x in r["heldout_source_folds"])


def test_no_default_photometric_gain_fabricated_for_missing_header():
    s=extracted()
    psf=s["aligned_empirical_shape"]
    x=_fixed_shape_fit_rms(s,psf)
    assert x["header_gain_applied_to_optional_source_shot_noise"] is False
    assert not x["calibrated_chi_square_or_false_companion_significance"]


def test_original_archive_503_kept_as_access_problem_not_companion():
    from urllib.error import HTTPError
    def missing(url,*,kind,timeout):
        raise HTTPError(url,503,"busy",None,None)
    record=fetch_original_source_stamp(
        SCIENCE,source_ra=RA,source_dec=DEC,
        native_x=1535.3,native_y=1539.4,
        gaia_source_id="3419109222512317056",
        fetch_mask=missing)
    assert record["status"]=="ORIGINAL_IMAGE_MASK_OR_EMPIRICAL_TRAINING_INELIGIBLE"
    assert record["http_status"]==503
    assert not record["physical_gaia_ztf_identity_authenticated"]


def test_original_fits_source_cutout_retained_date_and_path_for_both_products():
    source,mask=original_stamp_image()
    seen=[]
    def m(url,*,kind,timeout):
        assert "_mskimg.fits?" in url
        assert "size=60arcsec" in url
        seen.append(url)
        return mask
    def s(url,*,timeout):
        assert "_sciimg.fits?" in url
        seen.append(url)
        return source
    out=fetch_original_source_stamp(
        SCIENCE,source_ra=RA,source_dec=DEC,
        native_x=1535.3,native_y=1539.4,
        gaia_source_id="3419109222512317056",
        fetch_mask=m,fetch_science=s)
    assert out["original_source_detector_fits_verified"]
    assert len(seen)==2
    assert seen[0].split("_mskimg.fits")[0]==seen[1].split("_sciimg.fits")[0]



def test_bright_old_reference_template_on_two_different_preselected_faint_gaia_stars():
    training=[extracted(str(4000+i),seed=20+i,amplitude=19000)
              for i in range(4)]
    holds=[extracted(str(9000+i),seed=60+i,amplitude=1700,extra_noise=20,
                     min_source_snr_proxy=2.5)
           for i in range(2)]
    r=evaluate_other_star_empirical_psf(
        training,holds,native_spatial_psf=fake_daophot())
    assert r["status"]=="NEW_GAIA_SOURCE_DISJOINT_EMPIRICAL_PSF_TEST_COMPLETED"
    assert r["n_bright_distinct_reference_training_stars"]==4
    assert r["n_new_source_disjoint_heldout_stars"]==2
    assert r["n_new_source_disjoint_heldout_models_evaluated"]==2
    for q in r["evaluation_records"]:
        assert q["new_heldout_gaia_candidate_id"] not in q[
            "training_bright_prior_gaia_reference_ids"]
        assert q["heldout_new_gaia_source_pixels_absent_from_template_training"]
        assert q["empirical_psf_original_star_pixels_not_native_DAOPhot_coefficients"]
    assert not r["original_ZTF_pipeline_DAOPhot_training_star_membership_known"]


def test_wider_heldout_faint_source_tier_never_enters_bright_empirical_training():
    s,m=original_stamp_image(amplitude=1700,extra_noise=20)
    h=extract_original_source_stamp(
        s,m,source_ra=RA,source_dec=DEC,native_x=1535.3,native_y=1539.4,
        gaia_source_id="9990001",min_source_snr_proxy=2.5)
    assert h["original_source_detector_fits_verified"]
    assert h["source_snr_proxy"]>=2.5
    assert h["source_snr_proxy"]<10
    with pytest.raises(ValueError,match="Too-low-SNR"):
        evaluate_other_star_empirical_psf(
            [h,extracted("1001"),extracted("1002"),extracted("1003")],
            [extracted("9001",amplitude=1800,extra_noise=20,
                       min_source_snr_proxy=2.5)],
            native_spatial_psf=fake_daophot())


def test_source_id_overlap_between_training_and_heldout_is_rejected_even_if_good_images():
    src=extracted("1111")
    with pytest.raises(ValueError,match="leaks"):
        evaluate_other_star_empirical_psf(
            [src,extracted("1112"),extracted("1113")],
            [src],native_spatial_psf=fake_daophot())


def test_two_bright_reference_stars_plus_faint_new_gaia_is_insufficient():
    r=evaluate_other_star_empirical_psf(
        [extracted("101"),extracted("102")],
        [extracted("9001",amplitude=1700)],
        native_spatial_psf=fake_daophot())
    assert r["status"]=="INSUFFICIENT_REAL_BRIGHT_TRAINING_OR_NEW_HELDOUT_STARS"
    assert r["n_new_source_disjoint_heldout_models_evaluated"]==0


def test_faint_heldout_source_cannot_be_omitted_without_reporting_missing_evidence():
    r=evaluate_other_star_empirical_psf(
        [extracted("101"),extracted("102"),extracted("103")],
        [{"gaia_source_id":"9001","status":"ORIGINAL_IMAGE_MASK_OR_EMPIRICAL_TRAINING_INELIGIBLE"}],
        native_spatial_psf=fake_daophot())
    assert r["status"]=="INSUFFICIENT_REAL_BRIGHT_TRAINING_OR_NEW_HELDOUT_STARS"
    assert r["n_new_source_disjoint_heldout_models_evaluated"]==0


def test_explicit_bright_training_threshold_is_not_silently_lowered():
    s,m=original_stamp_image(amplitude=1700,extra_noise=20)
    with pytest.raises(ValueError,match="TOO_WEAK"):
        extract_original_source_stamp(
            s,m,source_ra=RA,source_dec=DEC,native_x=1535.3,native_y=1539.4,
            gaia_source_id="9990001")
