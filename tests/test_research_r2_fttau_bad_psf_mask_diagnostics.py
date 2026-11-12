"""Fixed-source provenance, exact frozen quality cuts and no-claim falsification."""
import hashlib
import copy
import math
import numpy as np
import pytest
from stellarforge.r2_fttau_bad_psf_mask_diagnostics import (
    FROZEN_FAILED_LATE, frozen_bad_late_exposures,
    original_nearest_native_fit_failure, inspect_one_frozen_failure,
)


def ledger():
    groups = [{
        "band": b, "field": field, "oid": oid,
        "native_psf_pass": [True, False],
        "mjds": [mjd-120, mjd],
        "sha": ["prior_early_sha", sha]
    } for b,field,oid,frac,mjd,sha in FROZEN_FAILED_LATE]
    groups.append({
        "band":"r","field":1605,"oid":"1605215300005161",
        "native_psf_pass":[True,True]
    })
    return {
        "run_id": 43270659201, "artifact_id": 13968001848,
        "n_original_ztf_catalogues_new":8,
        "n_provisional_quality_passed":5,
        "n_two_night_pairs_quality_passed":1,
        "n_confirmed_physical_matches":0,"n_merged_lightcurves":0,
        "scientific_r2_complete": False,
        "source_groups": groups,
    }


def test_exact_three_late_frozen_strata_and_byte_fingerprints():
    items=frozen_bad_late_exposures(ledger())
    assert len(items)==3
    assert [(x["band"],x["field"]) for x in items]==[
        ("g",1605),("g",609),("r",609)]
    assert all(x["native_psfcat_original_expected_sha256"] in
               [a[5] for a in FROZEN_FAILED_LATE] for x in items)
    assert all(len(x["filefracday"])==14 for x in items)


def test_upstream_checksum_and_quality_changed_fails_closed():
    base=ledger()
    for field,value in [
        ("run_id",1),("n_provisional_quality_passed",6),
        ("scientific_r2_complete",True),("n_merged_lightcurves",1),
    ]:
        bad=copy.deepcopy(base)
        bad[field]=value
        with pytest.raises(ValueError):frozen_bad_late_exposures(bad)
    bad=copy.deepcopy(base)
    bad["source_groups"][0]["sha"][1]="changed"
    with pytest.raises(ValueError):frozen_bad_late_exposures(bad)
    bad=copy.deepcopy(base)
    bad["source_groups"][0]["native_psf_pass"]=[True,True]
    with pytest.raises(ValueError):frozen_bad_late_exposures(bad)


def native(snr=4.0,chi=1.0,sharp=0.0,flags=0,flux=123.0,sigflux=12.0):
    return {"status":"ORIGINAL_ZTF_PSF_CATALOGUE_PARSED_UNVERIFIED",
            "rows":{
                "ra":np.array([65.0,65.2]),"dec":np.array([24.0,24.2]),
                "snr":np.array([snr,30]),"chi":np.array([chi,1]),
                "sharp":np.array([sharp,0]),"flags":np.array([flags,0]),
                "flux":np.array([flux,100]),"sigflux":np.array([sigflux,5])
            }}


def prediction():
    return {"geocentric_parallax_adjusted_ra_deg":65.0,
            "geocentric_parallax_adjusted_dec_deg":24.0}


@pytest.mark.parametrize("bad_kwargs,gate",[
    ({"snr":4.999},"snr_at_least_5"),
    ({"chi":.499},"chi_between_0p5_and_1p5"),
    ({"chi":1.501},"chi_between_0p5_and_1p5"),
    ({"sharp":-.501},"sharp_between_minus0p5_and_plus0p5"),
    ({"sharp":.501},"sharp_between_minus0p5_and_plus0p5"),
    ({"flags":1},"native_bad_6141_mask_bits_clear"),
    ({"flux":0},"flux_positive"),
    ({"sigflux":0},"sigflux_positive"),
])
def test_original_prospectively_frozen_psf_gate_explained(bad_kwargs,gate):
    cat=native(snr=15,**bad_kwargs)
    result=original_nearest_native_fit_failure(cat,prediction())
    assert gate in result["failed_source_level_quality_reasons"]
    assert result["original_geometry_pass_unchanged"]
    assert not result["original_profile_pass_unchanged"]
    assert result["no_source_physical_identity_or_variability_claim"]
    assert "flux" not in result
    assert "sigflux" not in result
    assert "sourceid" not in result


def test_two_independent_quality_failures_are_both_listed():
    result=original_nearest_native_fit_failure(
        native(snr=2,chi=1.7,sharp=.7,flags=1),prediction())
    assert {"snr_at_least_5","chi_between_0p5_and_1p5",
            "sharp_between_minus0p5_and_plus0p5",
            "native_bad_6141_mask_bits_clear"}.issubset(
                result["failed_source_level_quality_reasons"])


def test_good_profile_cannot_masquerade_as_original_failed_source():
    with pytest.raises(ValueError):
        original_nearest_native_fit_failure(native(snr=30),prediction())


def test_hash_mismatch_hard_fails_no_raw_or_identity_claim(monkeypatch):
    from stellarforge import r2_fttau_bad_psf_mask_diagnostics as m
    monkeypatch.setattr(m,"ztf_science_cutout_url",lambda *a,**k:"https://fake.test/science")
    monkeypatch.setattr(m,"official_psf_product_url",lambda *a,**k:"https://fake.test/psf")
    monkeypatch.setattr(m,"official_ancillary_url",lambda *a,**k:"https://fake.test/mask")
    s=frozen_bad_late_exposures(ledger())[0]
    result=inspect_one_frozen_failure(
        s, {"dummy":"gaia"},
        native_fetch=lambda *a,**k:b"wrong hash",
        science_fetch=lambda *a,**k:b"science fake",
        mask_fetch=lambda *a,**k:b"mask fake",
        predictor=lambda *a,**k:prediction(),
        image_mask_check=lambda *a,**k:{"status":"MASK_CORE_NO_DISQUALIFYING_BITS_PROVISIONAL_ONLY","wcs_checked_and_aligned":True,"n_core_bad_mask_pixels":0},
        image_pixel_check=lambda *a,**k:{"status":"CENTRAL_PEAK_FOUND","central_local_maximum_detected":True},
    )
    assert result["original_native_psf_catalogue_sha_matched"] is False
    assert result["native_diagnosis_status"]=="UNAVAILABLE_OR_INVALID"
    assert result["image_mask_diagnosis_status"]=="ORIGINAL_IMAGE_AND_MASK_ANALYSED"
    assert result["scientific_physical_gaia_ztf_source_confirmed"] is False
    assert result["original_bad_native_source_quality_changed_to_pass"] is False


def test_original_byte_match_but_clean_mask_never_upgrades_native_failure(monkeypatch):
    from stellarforge import r2_fttau_bad_psf_mask_diagnostics as m
    monkeypatch.setattr(m,"ztf_science_cutout_url",lambda *a,**k:"https://fake.test/science")
    monkeypatch.setattr(m,"official_psf_product_url",lambda *a,**k:"https://fake.test/psf")
    monkeypatch.setattr(m,"official_ancillary_url",lambda *a,**k:"https://fake.test/mask")
    raw=b"tiny original simulated"
    s=frozen_bad_late_exposures(ledger())[0]
    s["native_psfcat_original_expected_sha256"]=hashlib.sha256(raw).hexdigest()
    row=native(snr=3,chi=1.7)
    result=inspect_one_frozen_failure(
        s, {"dummy":"gaia"},
        native_fetch=lambda *a,**k:raw,
        native_parse=lambda *a:{"sha256":hashlib.sha256(raw).hexdigest(),**row},
        science_fetch=lambda *a,**k:b"science fake",
        mask_fetch=lambda *a,**k:b"mask fake",
        predictor=lambda *a,**k:prediction(),
        image_mask_check=lambda *a,**k:{"status":"MASK_CORE_NO_DISQUALIFYING_BITS_PROVISIONAL_ONLY","wcs_checked_and_aligned":True,"n_core_bad_mask_pixels":0},
        image_pixel_check=lambda *a,**k:{"status":"CENTRAL_PEAK_FOUND","central_local_maximum_detected":True},
    )
    assert result["original_native_psf_catalogue_sha_matched"]
    assert result["native_diagnosis_status"]=="FROZEN_ORIGINAL_BAD_NATIVE_PSF_DIAGNOSED"
    assert len(result["native_fit_diagnostics"]["failed_source_level_quality_reasons"])==2
    assert result["image_mask_derived_diagnostics"]["mask_or_local_peak_proves_unblended_star"] is False
    assert result["original_bad_native_source_quality_changed_to_pass"] is False
