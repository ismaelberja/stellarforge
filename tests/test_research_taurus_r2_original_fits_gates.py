"""Strict, offline R2 original ZTF science exposure + native PSFcat gates.

No original Gaia/IRSA network requests and no fabricated real observations
in unit tests. Live original-data evidence is in a separate Actions job.
"""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from urllib.parse import parse_qs,urlparse

import numpy as np
import pytest

from stellarforge.r2_original_fits_gates import (
    fixed_exposure_metadata,independent_native_psfcat_neighbours,
    metadata_request_url,validate_historic_exposures,
    inspect_fixed_original_frame,
)
ROOT=Path(__file__).resolve().parents[1]
SEED=(ROOT/"data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv").read_bytes()
LEDGER=json.loads((ROOT/"data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json").read_text(encoding="utf8"))


def fake_metadata(row,*,duplicate=False):
    header=["oid","mjd","filefracday","field","filtercode","ccdid","qid","catflags"]
    buf=io.StringIO()
    out=csv.DictWriter(buf,fieldnames=header,lineterminator="\n")
    out.writeheader()
    out.writerow(row)
    if duplicate:out.writerow(row)
    return buf.getvalue().encode()


def fixture_original_row(oid="1605115300003377",mjd="58388.389016"):
    return {"oid":oid,"mjd":mjd,"filefracday":"20180927389016",
            "field":"1605","filtercode":"zg","ccdid":"0x1","qid":"0x1","catflags":"0"}


def fake_native(ra,dec,offset_arcsec=(.4,)):
    n=len(offset_arcsec)
    return {
        "status":"ORIGINAL_ZTF_PSF_CATALOGUE_PARSED_UNVERIFIED",
        "sha256":"a"*64,
        "n_native_psf_catalogue_rows":n,
        "rows":{
            "ra":np.asarray([ra+x/(3600*np.cos(np.radians(dec)))
                             for x in offset_arcsec],dtype=float),
            "dec":np.asarray([dec]*n,dtype=float),
            "sourceid":np.asarray(list(range(1,n+1)),dtype=int),
        }
    }


def test_frozen_real_original_24_cohort_exact_two_targets_four_epochs():
    src,frames=validate_historic_exposures(SEED,LEDGER)
    assert len(src)==24
    assert len(frames)==4
    assert {f["target"] for f in frames}=={"FT Tau","CIDA 11"}
    assert {f["band"] for f in frames}=={"zg"}
    assert {f["target_gaia_id"] for f in frames}=={
        "149623711269425408","3419110734340795648"}
    assert {round(float(f["mjd"]),6) for f in frames}=={
        58388.389016,58491.184780,58475.113750,58849.135984}


@pytest.mark.parametrize("tamper",["one_frame_missing","extra_frame","new_gaia_id","new_mjd","new_band","old_provenance"])
def test_cannot_select_or_substitute_new_science_exposure_after_review(tamper):
    d=json.loads(json.dumps(LEDGER))
    if tamper=="one_frame_missing":d["exposures"].pop()
    if tamper=="extra_frame":d["exposures"].append(dict(d["exposures"][0]))
    if tamper=="new_gaia_id":d["exposures"][0]["target_gaia_id"]="1111111111111111111"
    if tamper=="new_mjd":d["exposures"][0]["mjd"]=58999.999
    if tamper=="new_band":d["exposures"][0]["band"]="zr"
    if tamper=="old_provenance":d["provenance"]["original_json_sha256"]="0"*64
    with pytest.raises(ValueError):
        validate_historic_exposures(SEED,d)


def test_exact_oid_and_time_url_is_restricted_original_not_sky_cherry_pick():
    u=metadata_request_url("1605115300003377",58388.389016)
    query=parse_qs(urlparse(u).query)
    assert urlparse(u).hostname=="irsa.ipac.caltech.edu"
    assert query["ID"]==["1605115300003377"]
    assert query["FORMAT"]==["csv"]
    assert "POS" not in query
    assert "TIME" in query
    assert len(query["TIME"][0].split())==2
    with pytest.raises(ValueError):
        metadata_request_url("1605115300003377 OR 1",58388.389016)
    with pytest.raises(ValueError):
        metadata_request_url("1605115300003377",float("nan"))


def test_original_one_exact_historic_exposure_required():
    old=fixture_original_row()
    expected=fixed_exposure_metadata(fake_metadata(old),
                                     oid=old["oid"],mjd=float(old["mjd"]))
    assert expected["n_direct_oid_rows_in_window"]==1
    assert expected["row"]["filefracday"]=="20180927389016"
    with pytest.raises(ValueError,match="exactly once"):
        fixed_exposure_metadata(fake_metadata(old,duplicate=True),
                               oid=old["oid"],mjd=float(old["mjd"]))
    with pytest.raises(ValueError,match="Direct OID"):
        fixed_exposure_metadata(fake_metadata(old),oid="111111",mjd=float(old["mjd"]))
    changed=dict(old,mjd="58999.000")
    with pytest.raises(ValueError,match="exactly once"):
        fixed_exposure_metadata(fake_metadata(changed),oid=old["oid"],mjd=float(old["mjd"]))


def test_catalogue_second_source_within_3arcsec_is_review_not_companion():
    obj=independent_native_psfcat_neighbours(
        fake_native(65.0,24.0,(0.2,1.5,6.)),ra=65.0,dec=24.0)
    assert obj["status"]=="NATIVE_SOURCE_WITH_ADDITIONAL_3ARCSEC_PSF_CATALOGUE_NEIGHBOURS"
    assert obj["n_psfcat_rows_within_3arcsec"]==2
    assert obj["n_additional_native_psfcat_sources_within_3arcsec"]==1
    assert obj["nearest_native_psfcat_offset_arcsec"]==pytest.approx(.2,abs=.00002)
    assert obj["independently_verified_gaia_to_ztf_counterpart"] is False
    assert obj["unresolved_blends_excluded"] is False


def test_one_native_catalogue_entry_is_not_independently_calibrated():
    obj=independent_native_psfcat_neighbours(
        fake_native(65.,24.,(.4,7.)),ra=65.,dec=24.)
    assert obj["status"]=="ONE_NATIVE_PSF_CATALOGUE_CANDIDATE_NO_OTHER_WITHIN_3ARCSEC"
    assert obj["n_psfcat_rows_within_1arcsec"]==1
    assert obj["n_additional_native_psfcat_sources_within_3arcsec"]==0
    assert obj["original_native_catalogue_is_not_independent_physical_crossmatch"] is True


def test_no_nearby_native_catalogue_row_is_not_stellar_nondetection():
    obj=independent_native_psfcat_neighbours(
        fake_native(65.,24.,(2.5,6.)),ra=65.,dec=24.)
    assert obj["status"]=="NO_NEARBY_NATIVE_PSF_SOURCE_WITHIN_1ARCSEC"
    assert obj["nearest_native_sourceid"] is None
    assert obj["n_psfcat_rows_within_3arcsec"]==1
    assert obj["independently_verified_gaia_to_ztf_counterpart"] is False


def test_partial_failure_never_claims_a_real_gaia_ztf_physical_match():
    f=LEDGER["exposures"][0]
    target={"source_id":f["target_gaia_id"],"ruwe":1.2}
    result=inspect_fixed_original_frame(
        f,target,metadata_fetch=lambda oid,mjd:b"<html>503 error</html>")
    assert result["original_metadata"]["status"]=="ORIGINAL_ARCHIVE_REQUEST_OR_VALIDATION_FAILED"
    assert result["native_psfcat_neighbours"]=="NOT_CHECKED"
    assert result["science_mask_image"]=="NOT_CHECKED"
    assert result["source_physical_identity_confirmed"] is False
    assert result["full_r2_physical_association_completed"] is False
