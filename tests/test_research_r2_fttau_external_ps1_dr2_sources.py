"""Falsification and original-source provenance tests: external MAST PS1 pilot.

Synthetic tests never claim to be astronomical observations.
"""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from urllib.parse import urlparse,parse_qs

import numpy as np
import pytest

from stellarforge.r2_fttau_external_ps1 import (
    PS1_COLUMNS, PS1_PAGESIZE, external_ps1_url,
    parse_ps1_original_mean, same_band_original_ztf_ps1_triplets,
    source_level_ps1_color_fit, original_external_ps1_ft_tau_study,
    _split_indices,
)

ROOT=Path(__file__).resolve().parents[1]
SEED=(ROOT/"data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv").read_bytes()
HIST=json.loads((ROOT/"data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json").read_text("utf8"))
OID=json.loads((ROOT/"reports/taurus_variability_r2/REAL_ALTERNATIVE_ZTF_OID_ORIGINAL_RUN_RECEIPT.json").read_text("utf8"))
IMAGES=json.loads((ROOT/"reports/taurus_variability_r2/FT_TAU_TWO_ORIGINAL_ZTF_FIELDS_GR_FITS_MASK_PSF_DERIVED_NO_RAW.json").read_text("utf8"))
PREVIOUS=json.loads((ROOT/"reports/taurus_variability_r2/FTTAU_720_REAL_NATIVE_ENSEMBLE_ZTF_PS1_PIPELINE_HEADER_NO_RAW.json").read_text("utf8"))
RA0=65.913324
DEC0=24.937195


def original_ps1_synthetic_csv(n=60,*,close_dup=False):
    output=io.StringIO()
    w=csv.DictWriter(output,fieldnames=PS1_COLUMNS,lineterminator="\n")
    w.writeheader()
    for i in range(n):
        x=-340.+(i%20)*35.
        y=-240.+(i//20)*150.
        if i==n-1 and close_dup:
            x=-340.
            y=-240.+.5
        g=15.4+((i%15)/15)*1.1
        r=g-(.2+(i%11)/11*1.3)
        w.writerow({"objID":str(100000000000000000+i),"raMean":RA0+x/(3600*np.cos(np.deg2rad(DEC0))),
                    "decMean":DEC0+y/3600,"nDetections":16,
                    "ng":8,"nr":6,"gMeanPSFMag":g,
                    "gMeanPSFMagErr":.012,"rMeanPSFMag":r,
                    "rMeanPSFMagErr":.014})
    return output.getvalue().encode()


def pseudo_native(ps1,band,*,field="1605"):
    x=ps1["xy"].copy()
    if field=="609":
        x[:,0]+=.1
        x[:,1]+=.07
    mag_ps1=ps1[band+"mag"]
    color=ps1["color_gr"]
    intercept,slope=(25.1,.07) if field=="1605" else (24.9,.05)
    mag=mag_ps1-intercept-slope*(color-.8)
    mag+=.012*np.sin(np.arange(len(mag))*1.7)
    return {"xy":x,"mag":mag,
            "sigmag":np.full(len(mag),.02),
            "id":np.arange(100,len(mag)+100)}


def test_mast_query_is_independent_PS1_dr2_mean_and_fixed_untruncated():
    url=external_ps1_url(RA0,DEC0)
    x=urlparse(url)
    p=parse_qs(x.query)
    assert x.hostname=="catalogs.mast.stsci.edu"
    assert x.path=="/api/v0.1/panstarrs/dr2/mean.csv"
    assert p["radius"]==["0.20000000"]
    assert p["nDetections.gte"]==["5"]
    assert p["pagesize"]==[str(PS1_PAGESIZE)]
    assert "gMeanPSFMagErr" in p["columns"][0]
    assert "rMeanPSFMagErr" in p["columns"][0]
    with pytest.raises(ValueError):external_ps1_url(60.,-50.)
    with pytest.raises(ValueError):external_ps1_url(float("nan"),DEC0)


def test_external_original_ps1_rows_are_unique_crowding_and_quality_screened():
    ps1=parse_ps1_original_mean(original_ps1_synthetic_csv(60,close_dup=True),
                                ra0=RA0,dec0=DEC0)
    assert ps1["n_original_ps1_dr2_mean_source_rows"]==60
    assert ps1["n_PS1_dr2_mean_rows_passing_mag_color_crowding_and_target_exclusion"]==58
    assert ps1["original_ps1_source_catalogue_not_gaia_ft_physical_match"] is True
    assert ps1["original_response_SHA256"]
    assert len(set(ps1["id"]))==58


def test_external_ps1_mean_catalogue_accepts_valid_utf8_bom_without_faking_rows():
    raw=original_ps1_synthetic_csv(60)
    original=parse_ps1_original_mean(raw,ra0=RA0,dec0=DEC0)
    with_bom=parse_ps1_original_mean(b"\xef\xbb\xbf"+raw,ra0=RA0,dec0=DEC0)
    assert with_bom["n_original_ps1_dr2_mean_source_rows"]==60
    assert (with_bom["n_PS1_dr2_mean_rows_passing_mag_color_crowding_and_target_exclusion"]
            ==original["n_PS1_dr2_mean_rows_passing_mag_color_crowding_and_target_exclusion"])
    assert with_bom["original_response_SHA256"]!=original["original_response_SHA256"]


def test_external_ps1_source_geometry_recovers_distinct_original_triplets_without_photometric_selection():
    p=parse_ps1_original_mean(original_ps1_synthetic_csv(60),ra0=RA0,dec0=DEC0)
    q=same_band_original_ztf_ps1_triplets(
        pseudo_native(p,"g"),pseudo_native(p,"g",field="609"),p)
    assert q["n_same_filter_external_PS1_unique_source_triplets"]==60
    assert len(set(q["ps1_ids"]))==60
    assert np.max(np.abs(q["m_inst_field1605"]-q["m_inst_field609"]))<1
    assert np.all(np.isfinite(q["ps1_gmag"]))


def test_independent_ps1_gr_model_has_train_and_true_unseen_source_holdouts():
    p=parse_ps1_original_mean(original_ps1_synthetic_csv(60),ra0=RA0,dec0=DEC0)
    q=same_band_original_ztf_ps1_triplets(
        pseudo_native(p,"r"),pseudo_native(p,"r",field="609"),p)
    r=source_level_ps1_color_fit(q,"r")
    assert r["n_train"]>=10
    assert r["n_heldout"]>=8
    assert r["status"]=="PS1_EXTERNAL_SOURCE_LEVEL_PILOT_INTERNAL_HOLDOUT_PASS"
    assert r["both_fields_ps1_mean_color_holdout_qc_pass"] is True
    assert len(r["per_original_ZTF_field_fits"])==2
    assert r["per_original_ZTF_field_fits"][0][
        "PS1_minus_native_instrumental_intercept_mag"]==pytest.approx(25.1,abs=.035)
    assert r["per_original_ZTF_field_fits"][1][
        "PS1_minus_native_instrumental_intercept_mag"]==pytest.approx(24.9,abs=.035)
    assert r["full_absolute_photometric_calibration_certified"] is False
    assert r["external_PanSTARRS_photometric_source_identification_for_FT_TAU"] is False
    assert r["original_ZTF_lightcurves_merged"] is False


def test_post_selected_narrow_photometric_color_or_zero_external_sources_is_no_go():
    p=parse_ps1_original_mean(original_ps1_synthetic_csv(60),ra0=RA0,dec0=DEC0)
    q=same_band_original_ztf_ps1_triplets(
        pseudo_native(p,"g"),pseudo_native(p,"g",field="609"),p)
    shallow=dict(q)
    for k,v in shallow.items():
        if isinstance(v,np.ndarray):shallow[k]=v[:10]
    shallow["n_same_filter_external_PS1_unique_source_triplets"]=10
    x=source_level_ps1_color_fit(shallow,"g")
    assert x["status"].startswith("NO_GO")
    assert x["per_original_ZTF_field_fits"]==[]
    colors=dict(q)
    colors["colors"]=np.full(len(q["colors"]),.5)
    assert source_level_ps1_color_fit(colors,"g")["status"]=="NO_GO_COLOR_BASELINE_TOO_NARROW"


def test_ps1_original_API_html_truncation_missing_rows_duplicate_ids_fail_closed():
    for invalid in (
        b"<html>bad</html>",b"not,csv\nX,Y\n",b"",
        original_ps1_synthetic_csv(PS1_PAGESIZE),
    ):
        with pytest.raises(ValueError):
            parse_ps1_original_mean(invalid,ra0=RA0,dec0=DEC0)
    b=original_ps1_synthetic_csv(10).decode()
    b=b.replace("100000000000000009","100000000000000001")
    with pytest.raises(ValueError,match="duplicate"):
        parse_ps1_original_mean(b.encode(),ra0=RA0,dec0=DEC0)


def test_genuine_external_PS1_access_failure_does_not_generate_false_gaia_ztf_match():
    d=original_external_ps1_ft_tau_study(
        SEED,HIST,OID,IMAGES,PREVIOUS,
        external_fetch=lambda *a,**k:(_ for _ in ()).throw(TimeoutError("offline")),
        ztf_fetch=lambda *a,**k:(_ for _ in ()).throw(OSError("offline")))
    assert d["external_PS1_DR2_original_source_query"]["status"]==(
        "INDEPENDENT_PS1_ORIGINAL_CATALOGUE_UNAVAILABLE_OR_INCOMPLETE")
    assert d["n_original_ZTF_full_native_psfcats_reverified"]==0
    assert d["n_same_band_PanSTARRS_source_level_internal_pilot_passes"]==0
    assert d["n_independently_authenticated_gaia_ztf_FT_TAU_physical_counterparts"]==0
    assert d["n_merged_ztf_object_id_lightcurves"]==0
    assert d["research_R2_full_physical_source_identity_complete"] is False
    assert all(b["independent_external_PS1_source_level_color_test"][
        "status"]=="NO_GO_ORIGINAL_MAST_PS1_OR_ZTF_SOURCE_DATA_UNAVAILABLE"
        for b in d["bands"])


def test_old_720_results_cannot_be_mutated_to_fake_independent_ps1_crossmatch():
    changed=json.loads(json.dumps(PREVIOUS))
    changed["n_directly_crossmatched_independent_PS1_reference_sources"]=1
    with pytest.raises(ValueError,match="Previously frozen"):
        original_external_ps1_ft_tau_study(
            SEED,HIST,OID,IMAGES,changed,
            external_fetch=lambda *a,**k:b"fake",ztf_fetch=lambda *a,**k:b"fake")
