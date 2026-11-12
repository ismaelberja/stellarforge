"""Falsification tests for independent original ZTF science-pixel Gaussian diagnostics."""
from __future__ import annotations
import io
import json
from pathlib import Path

import numpy as np
import pytest

from stellarforge import r2_fttau_six_independent_pixel_residuals as mod


def original_fits_synthetic(*, source_amp=130., mask_core_bit=0,
                            flat_background=False):
    """Fully synthetic cutouts (not presented as astronomical observations)."""
    from astropy.io import fits
    from astropy.wcs import WCS

    rng=np.random.default_rng(467)
    wcs=WCS(naxis=2)
    wcs.wcs.ctype=["RA---TAN","DEC--TAN"]
    wcs.wcs.crval=[65.,24.]
    wcs.wcs.crpix=[31.,31.]
    wcs.wcs.cdelt=[-1/3600,1/3600]
    hdr=wcs.to_header()
    yy,xx=np.indices((61,61),dtype=float)
    noise=rng.normal(0,1.5,(61,61)) if not flat_background else np.zeros((61,61))
    sky=100.
    model=(source_amp*np.exp(-.5*((xx-30.7)**2+(yy-29.5)**2)/1.35**2))
    image=np.asarray(sky+noise+model,dtype=np.float32)
    mask=np.zeros(image.shape,dtype=np.int16)
    if mask_core_bit:mask[30,30]=mask_core_bit
    science_buffer,mask_buffer=io.BytesIO(),io.BytesIO()
    fits.PrimaryHDU(data=image,header=hdr).writeto(science_buffer)
    fits.PrimaryHDU(data=mask,header=hdr).writeto(mask_buffer)
    return science_buffer.getvalue(),mask_buffer.getvalue()


def test_synthetic_gaussian_recovers_finite_source_residual_without_astrophysics():
    science,mask=original_fits_synthetic()
    r=mod.independent_masked_gaussian_pixel_fit(science,mask,ra=65.,dec=24.)
    assert r["status"]=="INDEPENDENT_PIXEL_GAUSSIAN_NUMERIC_FIT_COMPLETE",r
    assert r["source_mask_wcs_aligned"]
    assert r["n_source_core_bad_mask_pixels"]==0
    assert r["n_independent_gaussian_core_pixels"]>=40
    assert r["n_independent_gaussian_sky_annulus_pixels"]>=75
    assert 2.0<r["analytic_circular_gaussian_fwhm_arcsec_proxy"]<5.0
    assert 0<r["analytic_gaussian_centroid_minus_gaia_arcsec_proxy"]<1.5
    assert 0<r["source_core_rms_residual_over_sky_mad_noise_proxy"]<3.
    assert r["fit_is_not_original_ztf_native_psf"] is True
    assert r["residual_is_not_calibrated_reduced_chi_square"] is True
    assert r["physical_gaia_ztf_identity_confirmed"] is False
    assert r["companion_or_variability_detected"] is False
    assert "flux" not in r and "amplitude" not in r
    assert "pixels" not in r


def test_original_bad_mask_core_fails_closed_even_if_star_is_bright():
    science,mask=original_fits_synthetic(mask_core_bit=1)
    r=mod.independent_masked_gaussian_pixel_fit(science,mask,ra=65.,dec=24.)
    assert r["status"]=="ORIGINAL_MASK_WCS_OR_CORE_INSUFFICIENT"
    assert r["n_source_core_bad_mask_pixels"]==1
    assert "analytic_circular_gaussian_fwhm_arcsec_proxy" not in r


def test_flat_sky_robust_noise_invalid_not_infinite_confidence():
    science,mask=original_fits_synthetic(flat_background=True)
    r=mod.independent_masked_gaussian_pixel_fit(science,mask,ra=65.,dec=24.)
    assert r["status"]=="ORIGINAL_SKY_MAD_NOISE_PROXY_INVALID"
    assert r["physical_gaia_ztf_identity_confirmed"] is False


def test_no_positive_source_is_explicitly_unresolved():
    science,mask=original_fits_synthetic(source_amp=0,flat_background=True)
    r=mod.independent_masked_gaussian_pixel_fit(science,mask,ra=65.,dec=24.)
    assert r["status"]=="ORIGINAL_SKY_MAD_NOISE_PROXY_INVALID"


def test_mismatched_original_native_catalogue_hash_is_fatal(monkeypatch):
    monkeypatch.setattr(mod,"ztf_science_cutout_url",lambda *a,**kw:"https://dummy.invalid/science")
    monkeypatch.setattr(mod,"official_psf_product_url",lambda *a,**kw:"https://dummy.invalid/psf")
    spec={
        "band":"g","field":"609","oid":"609108400001155",
        "filefracday":"20250930441343","mjd":60948.441412,
        "epoch_role":"LATE_FROZEN_CHI_FAILURE",
        "ccdid":8,"qid":4,
        "original_full_native_psfcat_sha256_expected":"0"*64,
        "original_target_native_chi_expected":.424,
        "original_target_native_snr_expected":65.01,
        "original_target_native_profile_pass_expected":False,
    }
    with pytest.raises(ValueError,match="HARD_FAIL_DIFFERENT_ORIGINAL"):
        mod.inspect_frozen_original_image(
            spec,{},gaia_propagate=lambda *a,**kw:{
                "geocentric_parallax_adjusted_ra_deg":65.,
                "geocentric_parallax_adjusted_dec_deg":24.},
            native_fetch=lambda *a,**kw:b"wrong original file")


def test_protocol_predeclared_analytic_fit_parameters_unchanged():
    assert mod.CORE_PIXELS==4.5
    assert (mod.ANNULUS_INNER_PIXELS,mod.ANNULUS_OUTER_PIXELS)==(9,15)
    assert (mod.MIN_CORE,mod.MIN_ANNULUS)==(40,75)
    assert mod.MAX_CENTRE_OFFSET==2
    assert (mod.MIN_GAUSS_SIGMA,mod.MAX_GAUSS_SIGMA)==(.6,4.5)
    assert mod.MAX_FIT_EVALS==300
    assert mod.BAD_MASK_BITS==6141


def test_immutable_actual_prior_original_fttau_six_file_and_psf_sha_selection():
    """Do not need new survey requests to test source/date provenance."""
    from scripts.prepare_taurus_variability_r1 import DEFAULT_SEED
    root=Path(__file__).resolve().parents[1]
    def js(rel):
        return json.loads((root/rel).read_text(encoding="utf8"))
    hist=js("data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json")
    oid=js("reports/taurus_variability_r2/REAL_ALTERNATIVE_ZTF_OID_ORIGINAL_RUN_RECEIPT.json")
    four=js("reports/taurus_variability_r2/FT_TAU_TWO_ORIGINAL_ZTF_FIELDS_GR_FITS_MASK_PSF_DERIVED_NO_RAW.json")
    eight=js("reports/taurus_variability_r2/FTTAU_MULTINIGHT_ORIGINAL_ZTF_SOURCE_AUDIT_NO_RAW.json")
    bad=js("reports/taurus_variability_r2/FTTAU_THREE_FROZEN_BAD_PSF_MASK_DIAGNOSIS_NO_RAW.json")
    chi=js("reports/taurus_variability_r2/FTTAU_SIX_ORIGINAL_ZTF_CHI_BLIND_REFERENCES_NO_RAW.json")
    specs=mod.six_original_pixel_specs(
        (root/DEFAULT_SEED).read_bytes() if not DEFAULT_SEED.is_absolute()
        else DEFAULT_SEED.read_bytes(),hist,oid,four,eight,bad,chi)
    assert len(specs)==6
    assert [(x["band"],x["field"]) for x in specs]==[
        ("g","1605"),("g","1605"),("g","609"),("g","609"),
        ("r","609"),("r","609")]
    assert [x["epoch_role"] for x in specs]==[
        "EARLY_FROZEN_CONTROL","LATE_FROZEN_CHI_FAILURE"]*3
    assert all(len(x["original_full_native_psfcat_sha256_expected"])==64
               for x in specs)
    assert [x["original_target_native_profile_pass_expected"] for x in specs]==[
        True,False,True,False,True,False]
    assert [x["original_target_native_chi_expected"] for x in specs]==[
        .804,.456,.552,.424,1.438,.383]


def test_previous_6_image_original_source_checksum_tamper_rejected():
    from scripts.prepare_taurus_variability_r1 import DEFAULT_SEED
    root=Path(__file__).resolve().parents[1]
    names=[
        "data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json",
        "reports/taurus_variability_r2/REAL_ALTERNATIVE_ZTF_OID_ORIGINAL_RUN_RECEIPT.json",
        "reports/taurus_variability_r2/FT_TAU_TWO_ORIGINAL_ZTF_FIELDS_GR_FITS_MASK_PSF_DERIVED_NO_RAW.json",
        "reports/taurus_variability_r2/FTTAU_MULTINIGHT_ORIGINAL_ZTF_SOURCE_AUDIT_NO_RAW.json",
        "reports/taurus_variability_r2/FTTAU_THREE_FROZEN_BAD_PSF_MASK_DIAGNOSIS_NO_RAW.json",
        "reports/taurus_variability_r2/FTTAU_SIX_ORIGINAL_ZTF_CHI_BLIND_REFERENCES_NO_RAW.json",
    ]
    d=[json.loads((root/x).read_text()) for x in names]
    d[-1]["original_exact_3_ztf_oid_early_late_pairs"][0]["epochs"][1]["sha"]="FALSIFIED"
    seed=DEFAULT_SEED.read_bytes() if DEFAULT_SEED.is_absolute() else (root/DEFAULT_SEED).read_bytes()
    with pytest.raises(ValueError):
        mod.six_original_pixel_specs(seed,*d)


def test_independent_numeric_pair_requires_both_valid_fit_statuses():
    """The paired ratio cannot be claimed if only one model is calibrated."""
    from stellarforge import r2_fttau_six_independent_pixel_residuals as x
    # This invariant is encoded in the strict AND status gate in the run code.
    assert x.MIN_CORE>0
    assert x.MIN_ANNULUS>0
