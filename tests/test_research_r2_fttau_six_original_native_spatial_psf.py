"""Source-based falsification of exactly six original ZTF native DAOPhot PSFs."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from stellarforge import r2_fttau_six_original_native_spatial_psf as mod

ROOT=Path(__file__).resolve().parents[1]
NAMES=[
    "data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json",
    "reports/taurus_variability_r2/REAL_ALTERNATIVE_ZTF_OID_ORIGINAL_RUN_RECEIPT.json",
    "reports/taurus_variability_r2/FT_TAU_TWO_ORIGINAL_ZTF_FIELDS_GR_FITS_MASK_PSF_DERIVED_NO_RAW.json",
    "reports/taurus_variability_r2/FTTAU_MULTINIGHT_ORIGINAL_ZTF_SOURCE_AUDIT_NO_RAW.json",
    "reports/taurus_variability_r2/FTTAU_THREE_FROZEN_BAD_PSF_MASK_DIAGNOSIS_NO_RAW.json",
    "reports/taurus_variability_r2/FTTAU_SIX_ORIGINAL_ZTF_CHI_BLIND_REFERENCES_NO_RAW.json",
    "reports/taurus_variability_r2/FTTAU_SIX_ORIGINAL_ZTF_INDEPENDENT_GAUSSIAN_PIXELS_NO_RAW.json",
]


def input_spec():
    from scripts.prepare_taurus_variability_r1 import DEFAULT_SEED
    seed=DEFAULT_SEED.read_bytes() if DEFAULT_SEED.is_absolute() else (ROOT/DEFAULT_SEED).read_bytes()
    old=[json.loads((ROOT/x).read_text(encoding="utf8")) for x in NAMES]
    return seed,old


def test_exact_six_original_gaia_ztf_native_source_image_and_mask_sha_lock():
    seed,old=input_spec()
    items=mod.locked_six_original_native_spatial_specs(seed,*old)
    assert len(items)==6
    assert [x["epoch_role"] for x in items]==[
        "EARLY_FROZEN_CONTROL","LATE_FROZEN_CHI_FAILURE"]*3
    assert [(x["band"],x["field"]) for x in items]==[
        ("g","1605"),("g","1605"),("g","609"),("g","609"),
        ("r","609"),("r","609")]
    for x in items:
        assert len(x["original_full_native_psfcat_sha256_expected"])==64
        assert len(x["original_science_cutout_sha256_expected"])==64
        assert len(x["original_mask_cutout_sha256_expected"])==64
        assert len(x["filefracday"])==14
        assert x["prior_circular_gaussian_fit_status"]


def test_changed_native_sha_and_original_science_image_fail_closed():
    seed,old=input_spec()
    modified=copy.deepcopy(old)
    modified[-1]["six_immutable_original_data_exposure_derived_summary"][4]["science_sha"]="bad"
    with pytest.raises(ValueError,match="previously|original|pairing|altered|Original"):
        mod.locked_six_original_native_spatial_specs(seed,*modified)
    modified=copy.deepcopy(old)
    modified[-1]["n_valid_independent_analytic_gaussian_fits"]=6
    with pytest.raises(ValueError,match="Frozen"):
        mod.locked_six_original_native_spatial_specs(seed,*modified)


def test_strict_derived_only_holdout_fields_remove_raw_flux_and_background():
    qa={
        "status":"PROVISIONAL_ORIGINAL_MASKED_PSF_PIXEL_RESIDUAL_SCREEN_PASSED",
        "local_masked_psf_model_fit_completed":True,
        "same_image_holdout_residual_rms_over_sky_noise_proxy":1.45,
        "same_image_holdout_max_positive_residual_over_sky_noise_proxy":3.8,
        "n_same_image_checkerboard_heldout_pixels":119,
        "fitted_native_psf_amplitude_dn_unscaled":93453.6,
        "fitted_background_dn":35.02,
        "fitted_background_gradient_x_dn_per_pixel":1.3,
        "sourceid":12345,"raw_source_flux":54321,"pixel_array":[100,200],
    }
    out=mod.sanitized_spatial_holdout(qa)
    assert out["status"]==qa["status"]
    assert out["local_masked_psf_model_fit_completed"]
    assert out["same_image_holdout_residual_rms_over_sky_noise_proxy"]==1.45
    assert out["n_same_image_checkerboard_heldout_pixels"]==119
    for key in ("fitted_native_psf_amplitude_dn_unscaled",
                "fitted_background_dn","fitted_background_gradient_x_dn_per_pixel",
                "sourceid","raw_source_flux","pixel_array"):
        assert key not in out
    assert out["physical_gaia_ztf_source_identity_confirmed"] is False
    assert out["independent_instrument_noise_psf_covariance_calibrated"] is False


def fake_spec():
    return {
        "band":"g","field":"1605","oid":"1605115300003377",
        "original_mjd":58362.516713,"mjd":58362.516713,
        "filefracday":"20180901516678",
        "ccdid":15,"qid":3,"epoch_role":"EARLY_FROZEN_CONTROL",
        "original_target_native_chi_expected":.804,
        "original_target_native_snr_expected":43.6,
        "original_target_native_profile_pass_expected":True,
        "prior_circular_gaussian_fit_status":"INDEPENDENT_PIXEL_GAUSSIAN_NUMERIC_FIT_COMPLETE",
        "prior_circular_gaussian_residual_rms_over_mad":13.77661,
    }


def fake_native(sha):
    return {
        "sha256":sha,
        "status":"ORIGINAL_ZTF_PSF_CATALOGUE_PARSED_UNVERIFIED",
        "rows":{
            "ra":np.array([65.,65.1]),
            "dec":np.array([24.,24.1]),
            "xpos":np.array([1600.34,1500.2]),
            "ypos":np.array([1520.15,1510.1]),
            "chi":np.array([.804,1.0]),
            "snr":np.array([43.6,22.0]),
            "sharp":np.array([0.1,0.]),
            "flags":np.array([0,0],dtype=int),
            "flux":np.array([436.,220.]),
            "sigflux":np.array([10.,10.]),
        },
    }


def test_authentic_source_selection_same_image_pixel_holdout_stays_no_claim(monkeypatch):
    monkeypatch.setattr(mod,"ztf_science_cutout_url",lambda *a,**kw:"https://fake.invalid/sci")
    monkeypatch.setattr(mod,"official_psf_product_url",lambda sci,kind:kind)
    monkeypatch.setattr(mod,"official_ancillary_url",lambda sci,kind:kind)
    original=b"pseudo full native psfcat"
    sci=b"pseudo original science"
    mask=b"pseudo same-date mask"
    dao=b"pseudo original spatial dao model"
    center=b"pseudo original center PSF stamp"
    s=fake_spec()
    s["original_full_native_psfcat_sha256_expected"]=hashlib.sha256(original).hexdigest()
    s["original_science_cutout_sha256_expected"]=hashlib.sha256(sci).hexdigest()
    s["original_mask_cutout_sha256_expected"]=hashlib.sha256(mask).hexdigest()
    calls=[]
    def fetch_native(url,*,kind,timeout):
        calls.append(kind)
        return original if kind=="psfcat.fits" else dao
    def fetch_mask(url,*,kind,timeout):
        calls.append(kind)
        return mask if kind=="mskimg.fits" else center
    def native_parse(raw):
        assert raw==original
        return fake_native(hashlib.sha256(raw).hexdigest())
    def spatial_parse(raw):
        assert raw==dao
        return {"source_sha256":hashlib.sha256(raw).hexdigest(),
                "n_lookup_tables":3}
    def fit(_,__,spatial,**kwargs):
        assert kwargs["native_psfcat_x"]==1600.34
        assert kwargs["native_psfcat_y"]==1520.15
        assert kwargs["original_psfcat_ra"]==65.
        return {
            "status":"PROVISIONAL_ORIGINAL_MASKED_PSF_PIXEL_RESIDUAL_SCREEN_PASSED",
            "local_masked_psf_model_fit_completed":True,
            "same_image_holdout_residual_rms_over_sky_noise_proxy":2.1,
            "fitted_native_psf_amplitude_dn_unscaled":424242,
        }
    result=mod.inspect_one_original_native_spatial_image(
        s,gaia={},
        native_fetch=fetch_native,native_parse=native_parse,
        science_fetch=lambda *a,**kw:sci,
        mask_fetch=fetch_mask,spatial_parse=spatial_parse,
        center_compare=lambda p,r:{"status":"OFFICIAL_CENTER_PSF_APPROXIMATE_MODEL_AGREEMENT",
                                    "model_vs_official_center_cosine_similarity":.96,
                                    "model_vs_official_center_normalized_l1":.12,
                                    "local_spatial_psf_calibrated":False},
        original_pixel_fit=fit,
        propagate=lambda *a,**kw:{
            "geocentric_parallax_adjusted_ra_deg":65.,
            "geocentric_parallax_adjusted_dec_deg":24.})
    assert calls==["psfcat.fits","mskimg.fits","sciimgdao.psf","sciimgdaopsfcent.fits"]
    assert result["original_native_psfcat_sha256_verified"]
    assert result["original_science_mask_pair_sha256_verified"]
    assert result["spatial_dao_psf_status"]=="ORIGINAL_NATIVE_SPATIAL_DAO_PSF_PARSED"
    assert result["source_spatial_psf_same_image_holdout_diagnostics"]["status"].startswith("PROVISIONAL")
    assert result["source_spatial_psf_same_image_holdout_diagnostics"]["same_image_holdout_residual_rms_over_sky_noise_proxy"]==2.1
    assert "fitted_native_psf_amplitude_dn_unscaled" not in str(result)
    assert result["physical_gaia_ztf_counterpart_confirmed"] is False
    assert result["old_native_chi_screen_relaxed"] is False


def test_prior_original_native_science_sha_change_is_hard_error(monkeypatch):
    monkeypatch.setattr(mod,"ztf_science_cutout_url",lambda *a,**kw:"https://fake.invalid/sci")
    monkeypatch.setattr(mod,"official_psf_product_url",lambda sci,kind:kind)
    monkeypatch.setattr(mod,"official_ancillary_url",lambda sci,kind:kind)
    original=b"native"
    s=fake_spec()
    s["original_full_native_psfcat_sha256_expected"]=hashlib.sha256(original).hexdigest()
    s["original_science_cutout_sha256_expected"]="0"*64
    s["original_mask_cutout_sha256_expected"]="0"*64
    with pytest.raises(ValueError,match="HARD_FAIL_PREVIOUS_ORIGINAL_SCIENCE"):
        mod.inspect_one_original_native_spatial_image(
            s,{},native_fetch=lambda *a,**kw:original,
            native_parse=lambda raw:fake_native(hashlib.sha256(raw).hexdigest()),
            science_fetch=lambda *a,**kw:b"changed science",
            mask_fetch=lambda *a,**kw:b"original mask",
            propagate=lambda *a,**kw:{
                "geocentric_parallax_adjusted_ra_deg":65.,
                "geocentric_parallax_adjusted_dec_deg":24.})


def test_original_native_profile_failure_not_approved_by_spatial_residual_fitness():
    fake=mod.sanitized_spatial_holdout({
        "status":"PROVISIONAL_ORIGINAL_MASKED_PSF_PIXEL_RESIDUAL_SCREEN_PASSED",
        "local_masked_psf_model_fit_completed":True})
    assert fake["physical_gaia_ztf_source_identity_confirmed"] is False
    assert fake["independent_instrument_noise_psf_covariance_calibrated"] is False
