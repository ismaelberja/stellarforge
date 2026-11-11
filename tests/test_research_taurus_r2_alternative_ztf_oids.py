"""R2 Gaia/ZTF original ObjectID multiplicity anti-overclaim tests (OFFLINE)."""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

from stellarforge.r2_ztf_oid_multiplicity import (
    TARGETS, validate_fixed_two_targets, historic_oid_url,
    characterize_original_ztf_oids, characterize_exact_original_oid,
    review_two_original_fields,
)

ROOT=Path(__file__).resolve().parents[1]
SEED=(ROOT/"data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv").read_bytes()
HISTORY=json.loads((ROOT/"data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json").read_text("utf-8"))
COLS=("oid","filtercode","mjd","mag","magerr","catflags",
      "ra","dec","field","ccdid","qid","filefracday")
FT_OID="1605115300003377"
OTHER="1605115300003399"


def ztf_original_rows(rows):
    output=io.StringIO()
    writer=csv.DictWriter(output,fieldnames=COLS,lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode()


def sample(oid=FT_OID,band="zg",mjd=58388.3, *,
           ra=65.913324,dec=24.937195,field="1605",ccdid="3",
           qid="2",filefracday="20180927389016"):
    return {
        "oid":oid,"filtercode":band,"mjd":str(mjd),"mag":"13.5",
        "magerr":"0.045","catflags":"0","ra":str(ra),"dec":str(dec),
        "field":field,"ccdid":ccdid,"qid":qid,"filefracday":filefracday,
    }


def sample_multiplicity():
    return ztf_original_rows([
        sample(oid=FT_OID,mjd=58388.3),
        sample(oid=FT_OID,mjd=58389.3,filefracday="20180928389016"),
        sample(oid=OTHER,mjd=58388.3),  # SAME original frame metadata
        sample(oid=OTHER,mjd=58390.3,filefracday="20180929389016"),
        sample(oid="1605115300003400",band="zr",mjd=58389.3),
    ])


def test_exact_study_cohort_two_historic_oid_ids_and_four_dates_frozen():
    fixed=validate_fixed_two_targets(SEED,HISTORY)
    assert len(fixed)==2
    assert [f["target"] for f in fixed]==["FT Tau","CIDA 11"]
    assert [(a,b,c) for a,b,c in TARGETS]==[
        ("FT Tau","149623711269425408",FT_OID),
        ("CIDA 11","3419110734340795648","610106300008010"),
    ]
    assert sorted(fixed[0]["historical_mjds"])==[58388.389016,58491.18478]
    assert sorted(fixed[1]["historical_mjds"])==[58475.11375,58849.135984]


def test_original_ztf_id_url_is_exact_and_not_a_radius_or_posthoc_query():
    url=historic_oid_url(FT_OID)
    params=parse_qs(urlparse(url).query)
    assert params=={"ID":[FT_OID],"FORMAT":["csv"]}
    assert urlparse(url).hostname=="irsa.ipac.caltech.edu"
    for invalid in ("123","1234&ID=evil","", "a"*18):
        with pytest.raises(ValueError):
            historic_oid_url(invalid)


def test_original_alternative_same_band_oids_kept_separate_even_same_exposure():
    raw=sample_multiplicity()
    target={"ra":65.913324,"dec":24.937195,"pmra":0.,"pmdec":0.}
    d=characterize_original_ztf_oids(raw,gaia_target=target)
    assert d["n_original_positional_table_rows"]==5
    assert d["n_original_distinct_ztf_oids"]==3
    assert d["n_original_oid_band_groups"]==3
    assert d["n_original_oid_pairs_in_same_band"]==1
    assert d["n_same_band_oid_pairs_sharing_exact_original_exposure_metadata"]==1
    assert d["n_quality_accepted_photometric_rows"]==5
    pairs=d["same_band_multiple_oid_review_pairs"]
    assert len(pairs)==1
    assert pairs[0]["first_ztf_oid"]==FT_OID
    assert pairs[0]["second_ztf_oid"]==OTHER
    assert pairs[0]["n_shared_identical_original_exposure_metadata_keys"]==1
    assert pairs[0]["same_physical_star_established"] is False
    assert pairs[0]["different_physical_stars_established"] is False
    assert d["all_oid_curves_kept_separate"] is True
    assert all(not item["gaia_ztf_physical_identity_confirmed"]
               for item in d["original_ztf_oid_band_groups"])


def test_without_gaia_astrometry_original_oid_still_reviewable_not_verified():
    d=characterize_original_ztf_oids(sample_multiplicity(),gaia_target=None)
    assert d["n_original_oid_pairs_in_same_band"]==1
    assert all(x["positional_proximity_screen"]=="GAIA_TARGET_NOT_RETRIEVED"
               for x in d["original_ztf_oid_band_groups"])
    assert d["all_source_identities_physical_unconfirmed"] is True


def test_without_exposure_metadata_source_ambiguity_cannot_be_ruled_out():
    a=sample(oid=FT_OID)
    b=sample(oid=OTHER)
    a["filefracday"]=""
    b["filefracday"]=""
    d=characterize_original_ztf_oids(ztf_original_rows([a,b]),gaia_target=None)
    assert d["n_ztf_oid_bands_with_missing_exposure_metadata"]==2
    assert d["n_same_band_oid_pairs_sharing_exact_original_exposure_metadata"]==0
    assert d["n_original_oid_pairs_in_same_band"]==1
    assert all(x["n_original_rows_with_incomplete_exposure_metadata"]==1
               for x in d["original_ztf_oid_band_groups"])


def test_original_exact_id_response_must_not_include_unrequested_oid():
    valid=characterize_exact_original_oid(
        ztf_original_rows([sample(oid=FT_OID)]),expected_oid=FT_OID)
    assert valid["n_original_oid_rows"]==1
    assert valid["historical_oid_bands"]==["g"]
    assert valid["historical_oid_is_physical_gaia_counterpart_verified"] is False
    with pytest.raises(ValueError,match="unrelated"):
        characterize_exact_original_oid(
            ztf_original_rows([sample(oid=OTHER)]),expected_oid=FT_OID)


def test_original_two_fields_audit_survives_gaia_network_failure_no_fabrication():
    real=validate_fixed_two_targets(SEED,HISTORY)
    by_name={r["target"]:r for r in real}
    def fake_position(ra,dec,*,radius_arcsec,timeout_sec):
        assert radius_arcsec==2.
        row=next(x for x in real if abs(x["ra"]-ra)<1e-9)
        return ztf_original_rows([
            sample(oid=row["historical_ztf_oid"],ra=ra,dec=dec)
        ])
    def fake_id(oid,*,timeout_sec):
        return ztf_original_rows([sample(oid=oid)])
    d=review_two_original_fields(
        SEED,HISTORY,
        gaia_fetch=lambda *a,**k:(_ for _ in ()).throw(OSError("offline")),
        pos_fetch=fake_position,oid_fetch=fake_id,
    )
    assert d["n_frozen_nonrepresentative_taurus_gaia_sources"]==24
    assert d["n_fixed_historic_target_fields"]==2
    assert d["n_positional_irsa_2arcsec_queries_parsed"]==2
    assert d["n_direct_original_historic_oid_queries_parsed"]==2
    assert d["n_fields_with_historic_oid_in_positional_response"]==2
    assert d["n_physical_gaia_to_ztf_object_identifications_confirmed"]==0
    assert d["n_confirmed_new_ztf_stellar_variables_or_companions"]==0
    assert d["source_identity_science_R2_completed"] is False
    assert all(not f["gaia_original_source_available"] for f in d["fields"])


def test_one_service_failure_remains_unavailable_not_a_nonvariable_star():
    fixed=validate_fixed_two_targets(SEED,HISTORY)
    d=review_two_original_fields(
        SEED,HISTORY,
        gaia_fetch=lambda *a,**k:(_ for _ in ()).throw(OSError("offline")),
        pos_fetch=lambda *a,**k:(_ for _ in ()).throw(TimeoutError("unavailable")),
        oid_fetch=lambda oid,**k:ztf_original_rows([sample(oid=oid)]),
    )
    assert d["n_positional_irsa_2arcsec_queries_parsed"]==0
    assert d["n_direct_original_historic_oid_queries_parsed"]==2
    assert d["n_fields_with_historic_oid_in_positional_response"]==0
    assert all(x["historic_oid_present_in_2arcsec_positional_query"] is None
               for x in d["fields"])
    assert all(x["positional_oid_screen"]["status"]=="IRSA_POS_OR_PARSE_FAILED"
               for x in d["fields"])
    assert d["n_confirmed_new_ztf_stellar_variables_or_companions"]==0


def test_invalid_or_oversize_irsa_table_never_counted_as_physical_match():
    for invalid in (b"<html>HTTP 503</html>",b"",b"not,valid\nx,z\n",b"a"*4_000_001):
        with pytest.raises((ValueError,UnicodeError)):
            characterize_original_ztf_oids(invalid,gaia_target=None)


def test_historic_ztf_oid_cannot_be_changed_after_original_exposures():
    edited=json.loads(json.dumps(HISTORY))
    edited["exposures"][0]["oid"]="987654321098765"
    with pytest.raises(ValueError):
        validate_fixed_two_targets(SEED,edited)
