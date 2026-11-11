"""Offline R2 FT Tau two-field original FITS/PSFcat selection and anti-claims."""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from stellarforge.r2_ft_tau_two_field_fits import (
    FT_GAIA, FT_OIDS, catalogue_candidates, frozen_ft_tau,
    select_two_field_same_band_pair, _sanitized_selection,
    describe_same_filter_crossfield, run_ft_two_field_four_original_images,
)
from stellarforge.v14_field_review import ztf_science_cutout_url

ROOT=Path(__file__).resolve().parents[1]
SEED=(ROOT/"data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv").read_bytes()
HIST=json.loads((ROOT/"data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json").read_text("utf8"))
RECEIPT=json.loads((ROOT/"reports/taurus_variability_r2/REAL_ALTERNATIVE_ZTF_OID_ORIGINAL_RUN_RECEIPT.json").read_text("utf8"))

HEADER=("oid","filtercode","mjd","mag","magerr","catflags","field","ccdid","qid","filefracday")
def original_csv(spec, mjds, *, flags=None, field=None):
    band, area, oid, fieldid, ccdid, qid=spec
    f=io.StringIO()
    w=csv.DictWriter(f,fieldnames=HEADER,lineterminator="\n")
    w.writeheader()
    for i,mjd in enumerate(mjds):
        w.writerow({"oid":oid,"filtercode":"z"+band,"mjd":str(mjd),
                    "mag":"13.21","magerr":"0.04",
                    "catflags":str((flags or [0]*len(mjds))[i]),
                    "field":str(fieldid if field is None else field),
                    "ccdid":hex(ccdid),"qid":hex(qid),
                    "filefracday":str(20180000000000+i).zfill(14)})
    return f.getvalue().encode()

def photometry_data(a, b, c, d):
    return {s[2]: original_csv(s, mjds)
            for s,mjds in zip(FT_OIDS,(a,b,c,d))}


def test_fixed_24_gaia_targets_and_four_known_original_ztf_field_oids():
    frozen=frozen_ft_tau(SEED,HIST,RECEIPT)
    assert frozen["name"]=="FT Tau"
    assert frozen["gaia_id"]==FT_GAIA
    assert frozen["fixed_oids"]==FT_OIDS
    assert len(frozen["fixed_oids"])==4
    assert {x[0] for x in FT_OIDS}=={"g","r"}
    assert {x[1] for x in FT_OIDS}=={"1605","609"}


@pytest.mark.parametrize("change",["oid","field","source","run"])
def test_frozen_previously_published_source_odids_are_not_postselected(change):
    doc=json.loads(json.dumps(RECEIPT))
    if change=="oid":
        doc["ft_tau"]["r_ztf_oids"][1]="12400000"
    elif change=="field":
        doc["ft_tau"]["original_survey_fields"]=["fake"]
    elif change=="source":
        doc["ft_tau"]["gaia_dr3_source_id"]="100000000000000"
    elif change=="run":
        doc["live_original_survey_run_id"]=1
    with pytest.raises(ValueError):
        frozen_ft_tau(SEED,HIST,doc)


def test_original_ztf_catalogue_only_counts_eligible_single_epoch_source_metadata():
    s=FT_OIDS[0]
    data=original_csv(s,[58400,58401,58402,58403],flags=[0,32768,0,0])
    audit=catalogue_candidates(data,s)
    assert audit["n_original_source_rows"]==4
    # Metadata key unique by filefracday, no photometry quality cherrypicking.
    assert audit["n_eligible_distinct_science_exposures"]==3
    assert audit["n_rejected_rows_by_predeclared_technical_reason"]=={"masked_catflags":1}
    assert [x["mjd"] for x in audit["rows"]]==[58400,58402,58403]
    assert audit["raw_sha256"]
    selection=_sanitized_selection(audit["rows"][0])
    assert selection["ztf_oid"]==s[2]
    assert "mag" not in json.dumps(selection)
    assert "catflags" not in json.dumps(selection)


def test_untrusted_oid_or_detector_metadata_is_never_used_for_original_fits():
    s=FT_OIDS[0]
    other=list(s);other[2]="1605115300003333"
    with pytest.raises(ValueError,match="another ObjectID"):
        catalogue_candidates(original_csv(tuple(other),[58400]),s)
    with pytest.raises(ValueError,match="detector provenance"):
        catalogue_candidates(original_csv(s,[58400],field=613),s)
    with pytest.raises(ValueError,match="other-than-frozen filter"):
        wrong=list(s);wrong[0]="r"
        catalogue_candidates(original_csv(tuple(wrong),[58400]),s)


def test_closest_epoch_pair_is_deterministic_without_mag_data_selection():
    a=catalogue_candidates(original_csv(FT_OIDS[0],[58400.0,58420.0]),FT_OIDS[0])["rows"]
    b=catalogue_candidates(original_csv(FT_OIDS[1],[58402.0,58420.3]),FT_OIDS[1])["rows"]
    sel=select_two_field_same_band_pair(a,b)
    assert sel["status"]=="SELECTED_WITHIN_ONE_DAY_DIFFERENT_FIELD"
    assert sel["within_one_day"] is True
    assert sel["delta_mjd_days"]==pytest.approx(0.3)
    assert sel["first"]["mjd"]==58420.0
    assert sel["second"]["mjd"]==58420.3
    far=select_two_field_same_band_pair(
        a,catalogue_candidates(original_csv(FT_OIDS[1],[58439.0]),FT_OIDS[1])["rows"])
    assert far["status"]=="SELECTED_BUT_NOT_CONCURRENT_DIFFERENT_FIELD"
    assert far["within_one_day"] is False
    assert far["delta_mjd_days"]==19.0


def test_not_enough_data_or_two_different_bands_never_forces_crossfield_pair():
    a=catalogue_candidates(original_csv(FT_OIDS[0],[58400.0]),FT_OIDS[0])["rows"]
    r=catalogue_candidates(original_csv(FT_OIDS[2],[58400.1]),FT_OIDS[2])["rows"]
    assert select_two_field_same_band_pair(a,[])["status"]==(
        "MISSING_ORIGINAL_EXPOSURE_FOR_ONE_FIELD")
    with pytest.raises(ValueError,match="Cannot compare g and r"):
        select_two_field_same_band_pair(a,r)


def test_original_science_url_from_fixed_catalogue_has_expected_filter_field_date():
    row=catalogue_candidates(original_csv(FT_OIDS[2],[58400.0]),FT_OIDS[2])["rows"][0]
    url=ztf_science_cutout_url(row,ra_center=65.91332,dec_center=24.93720,size_arcsec=60)
    assert "_001605_zr_c15_o_q3_sciimg.fits" in url
    assert "center=" in url and "size=60arcsec" in url


def test_same_field_native_catalogue_offsets_are_only_descriptive_not_calibration():
    a={
        "all_three_instrument_source_checks_pass":True,
        "science_sha256":"x","mask_sha256":"y","native_full_catalogue_sha256":"z",
        "original_native_source_position_offset_mas":{
            "native_minus_gaia_east_mas":100,
            "native_minus_gaia_north_mas":-40},
    }
    b={
        "all_three_instrument_source_checks_pass":True,
        "science_sha256":"a","mask_sha256":"b","native_full_catalogue_sha256":"c",
        "original_native_source_position_offset_mas":{
            "native_minus_gaia_east_mas":-100,
            "native_minus_gaia_north_mas":50},
    }
    sel={"delta_mjd_days":.02,"within_one_day":True}
    v=describe_same_filter_crossfield(a,b,sel)
    assert v["instrumental_gates_both_passed"] is True
    assert v["native_catalogue_field_to_field_offset_difference_mas"]["east_mas"]==-200
    assert v["native_catalogue_field_to_field_offset_difference_mas"]["north_mas"]==90
    assert v["differential_astrometry_independently_calibrated"] is False
    assert v["crossfield_oid_physical_identity_authenticated"] is False
    assert v["crossfield_lightcurves_merged"] is False


def test_original_gaia_archive_unavailable_still_reports_no_fictitious_source_match():
    docs=photometry_data([58400],[58400.1],[58401],[58401.1])
    x=run_ft_two_field_four_original_images(
        SEED,HIST,RECEIPT,
        gaia_fetch=lambda *a,**k:(_ for _ in ()).throw(TimeoutError("t")),
        oid_fetch=lambda oid,**k:docs[oid],
    )
    assert x["n_original_direct_oid_csv_tables_valid"]==4
    assert x["n_mjd_closest_same_band_crossfield_pairs_selected"]==2
    assert x["n_selected_original_single_science_exposures"]==0
    assert x["n_original_image_mask_pairs_checked"]==0
    assert x["n_independently_verified_ft_gaia_ztf_physical_crossmatches"]==0
    assert x["n_reconciled_or_combined_ztf_lightcurves"]==0
    assert x["r2_physical_source_identity_science_complete"] is False


def test_synthetic_gaia_stub_original_images_are_never_leaked_or_claimed_real():
    docs=photometry_data([58400],[58400.15],[58402],[58402.2])
    def fake_inspector(row,gaia):
        return {"selection":_sanitized_selection(row),
                "all_three_instrument_source_checks_pass":False,
                "original_ztf_source_identity_verified":False,
                "new_source_variability_confirmed":False}
    with patch("stellarforge.r2_ft_tau_two_field_fits.parse_gaia_astrometry",
               return_value={FT_GAIA:{"source_id":FT_GAIA}}):
        x=run_ft_two_field_four_original_images(
            SEED,HIST,RECEIPT,
            gaia_fetch=lambda *a,**k:b"synthetic fixture NOT external Gaia",
            oid_fetch=lambda oid,**k:docs[oid],
            image_inspector=fake_inspector)
    assert x["n_selected_original_single_science_exposures"]==4
    assert x["n_original_image_mask_pairs_checked"]==0
    assert x["n_original_native_psfcats_parsed"]==0
    assert all(not g["crossfield_instrument_summary"]["instrumental_gates_both_passed"]
               for g in x["crossfield_same_filter_pairs"])
    assert x["n_independently_verified_ft_gaia_ztf_physical_crossmatches"]==0
    assert x["n_confirmed_new_astro_variables_or_companions"]==0
