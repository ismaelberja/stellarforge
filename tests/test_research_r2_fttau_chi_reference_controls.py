"""Falsification: chi-blind source controls, fixed early/late dates, no upgraded FT Tau identity."""
import copy
import hashlib

import numpy as np
import pytest

from stellarforge import r2_fttau_chi_reference_controls as m


def test_distribution_counts_and_quantiles():
    r=m.descriptive_chi_distribution(np.array([.2,.3,.5,.6,1.5,1.6]),target_chi=.42)
    assert r["status"].startswith("UNDERPOWERED")
    assert r["n_chi_below_0p5"]==2
    assert r["n_chi_between_0p5_and_1p5"]==3
    assert r["n_chi_above_1p5"]==1
    assert r["n_reference_sources"]==6
    assert r["controls_selected_without_chi"]
    assert r["target_chi_percentile_of_control_distribution"]==pytest.approx(33.3333,abs=.0001)


def test_empty_or_invalid_original_chi_controls():
    empty=m.descriptive_chi_distribution(np.array([]),target_chi=.42)
    assert empty["n_reference_sources"]==0
    assert empty["fraction_chi_below_0p5"] is None
    for arr in ([.4,-.1],[float("nan")],[float("inf")]):
        with pytest.raises(ValueError):
            m.descriptive_chi_distribution(arr,target_chi=.45)


def native_chi_test(targetchi=.42,controlchi=None,control_snr=None):
    # 40 synthetic uncrowded native reference entries 20..410" away.
    n=40
    if controlchi is None:controlchi=np.array([.4]*20+[.8]*20)
    if control_snr is None:control_snr=np.ones(n)*30
    xpos=np.array([0]+[30+10*i for i in range(n)])
    scale=3600*np.cos(np.radians(24))
    return {
        "status":"ORIGINAL_ZTF_PSF_CATALOGUE_PARSED_UNVERIFIED",
        "sha256":"fake",
        "n_native_psf_catalogue_rows":n+1,
        "rows":{
            "ra":65+xpos/scale,"dec":np.full(n+1,24.),
            "snr":np.r_[40.,control_snr],
            "chi":np.r_[targetchi,controlchi],
            "sharp":np.zeros(n+1),"flags":np.zeros(n+1,dtype=int),
            "flux":np.ones(n+1)*200,
            "sigflux":np.ones(n+1)*5,
        },
    }


def pred():
    return {"geocentric_parallax_adjusted_ra_deg":65.0,
            "geocentric_parallax_adjusted_dec_deg":24.0}


def test_reference_cohort_selection_includes_low_chi_and_excludes_target():
    x=m.chi_blind_local_controls(native_chi_test(),pred())
    assert x["target_original_chi"]==.42
    assert x["target_original_source_status"]=="TARGET_PSF_SOURCE_AMBIGUOUS_OR_QUALITY_REVIEW"
    ref=x["all_chi_blind_controls"]
    assert ref["n_reference_sources"]==40
    assert ref["n_chi_below_0p5"]==20
    assert ref["fraction_chi_below_0p5"]==.5
    assert ref["status"].startswith("DESCRIPTIVE")
    assert x["physical_gaia_ztf_source_identity_confirmed"] is False
    assert x["original_psf_chi_gate_reinterpreted_or_relaxed"] is False


def test_chi_blind_cohort_unchanged_when_every_chi_changes():
    source=native_chi_test()
    a=m.chi_blind_local_controls(source,pred())
    varied=copy.deepcopy(source)
    varied["rows"]["chi"][1:]=np.linspace(.02,3.0,40)
    b=m.chi_blind_local_controls(varied,pred())
    assert a["all_chi_blind_controls"]["n_reference_sources"]==b["all_chi_blind_controls"]["n_reference_sources"]==40
    assert a["all_chi_blind_controls"]["fraction_chi_below_0p5"] != b["all_chi_blind_controls"]["fraction_chi_below_0p5"]


def test_reference_snr_matched_population_can_be_underpowered():
    source=native_chi_test(control_snr=np.r_[np.ones(5)*35,np.ones(35)*200])
    result=m.chi_blind_local_controls(source,pred())
    assert result["all_chi_blind_controls"]["n_reference_sources"]==40
    assert result["snr_factor_two_matched_controls"]["n_reference_sources"]==5
    assert result["snr_factor_two_matched_controls"]["status"].startswith("UNDERPOWERED")


def test_source_isolation_uses_every_source_even_excluded_flagged():
    source=native_chi_test()
    # Add one close flagged bad source that should disqualify the good local
    # reference at 30" even though the new source itself fails flag QC.
    extras={k:np.asarray([v[1]]) for k,v in source["rows"].items()}
    extras["ra"]=source["rows"]["ra"][1:2]+1/(3600*np.cos(np.radians(24)))
    extras["flags"]=np.array([6141])
    for k in source["rows"]:
        source["rows"][k]=np.r_[source["rows"][k],extras[k]]
    source["n_native_psf_catalogue_rows"]+=1
    x=m.chi_blind_local_controls(source,pred())
    assert x["all_chi_blind_controls"]["n_reference_sources"]==39


def test_bad_original_sha_is_hard_failure(monkeypatch):
    monkeypatch.setattr(m,"ztf_science_cutout_url",lambda *a,**kw:"dummy_science")
    monkeypatch.setattr(m,"official_psf_product_url",lambda *a,**kw:"dummy_native")
    frame={"filefracday":"20250930441343","field":"609","ccdid":"8",
           "qid":"4","band":"g","filtercode":"zg","mjd":60948.441412}
    with pytest.raises(ValueError,match="FROZEN ORIGINAL"):
        m.inspect_frozen_reference_image(frame,fixed="a"*64,gaia={},
            ra0=65,dec0=24,native_fetch=lambda *a,**kw:b"sha-mismatch",
            propagate=lambda *a,**kw:pred())


def test_original_pass_boundary_never_relaxed():
    source=native_chi_test(targetchi=.499999)
    r=m.chi_blind_local_controls(source,pred())
    assert r["target_original_source_status"]=="TARGET_PSF_SOURCE_AMBIGUOUS_OR_QUALITY_REVIEW"
    source=native_chi_test(targetchi=.5)
    r=m.chi_blind_local_controls(source,pred())
    assert r["target_original_source_status"]=="PROVISIONAL_GAIA_NEAREST_ZTF_PSF_SOURCE_GEOMETRY_PASS"


def test_reference_quality_independent_from_chi_but_not_flags():
    s=native_chi_test()
    s["rows"]["flags"][7]=6141
    x=m.chi_blind_local_controls(s,pred())
    assert x["all_chi_blind_controls"]["n_reference_sources"]==39
    assert x["n_chi_invalid_in_chi_independent_eligible_controls"]==0


def test_quality_invalid_chi_does_not_invent_a_nondetection():
    s=native_chi_test()
    s["rows"]["chi"][1]=float("nan")
    x=m.chi_blind_local_controls(s,pred())
    assert x["n_chi_invalid_in_chi_independent_eligible_controls"]==1
    assert x["all_chi_blind_controls"]["n_reference_sources"]==39
