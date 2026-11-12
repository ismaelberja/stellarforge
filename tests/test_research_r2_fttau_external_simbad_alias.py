"""Reproducibility and fail-closed SIMBAD FT Tau exact Gaia name semantics."""
import hashlib
import json
from pathlib import Path

import pytest

from stellarforge import r2_fttau_external_simbad_alias as m

ROOT=Path(__file__).resolve().parents[1]

def csv_blob(oid="123456",main="FT Tau",ra="65.91331",dec="24.93721",otype="TT*"):
    return ("oid,main_id,ra,dec,otype\n"
            +f"{oid},{main},{ra},{dec},{otype}\n").encode("utf-8")

def test_exact_simbad_original_csv_parse_preserves_source_identity():
    a=m.parse_simbad_original_csv(csv_blob())
    assert a["n_original_rows"]==1
    assert a["n_unique_object_records"]==1
    assert a["raw_sha256"]==hashlib.sha256(csv_blob()).hexdigest()
    assert a["rows_ephemeral"][0]["oid"]=="123456"
    assert a["rows_ephemeral"][0]["ra_deg"]==65.91331

def test_gaia_name_same_external_simbad_oid_establishes_only_curated_alias():
    a=m.parse_simbad_original_csv(csv_blob())
    b=m.parse_simbad_original_csv(csv_blob(main="V* FT Tau"))
    x=m.external_alias_equivalence(a,b,gaia_ra=65.91331,gaia_dec=24.93721)
    assert x["status"]=="SIMBAD_EXACT_NAME_AND_GAIA_ALIAS_SAME_EXTERNAL_OBJECT"
    assert x["exact_external_catalogue_name_gaia_alias_verified"] is True
    assert x["independent_physical_gaia_to_ztf_target_identity_confirmed"] is False
    assert x["coordinate_epoch_and_independent_error_model_verified"] is False

def test_conflicting_or_missing_external_aliases_never_claim_gaia_ztf():
    gaia=m.parse_simbad_original_csv(csv_blob(oid="123"))
    conflict=m.parse_simbad_original_csv(csv_blob(oid="456"))
    miss=m.parse_simbad_original_csv(b"oid,main_id,ra,dec,otype\n")
    for name,status in (
        (conflict,"SIMBAD_EXACT_GAIA_AND_FT_NAME_CONFLICT"),
        (miss,"SIMBAD_ALIAS_LOOKUP_UNRESOLVED"),
    ):
        x=m.external_alias_equivalence(gaia,name,gaia_ra=65,gaia_dec=24)
        assert x["status"]==status
        assert x["exact_external_catalogue_name_gaia_alias_verified"] is False
        assert x["independent_physical_gaia_to_ztf_target_identity_confirmed"] is False

def test_ambiguous_simbad_original_duplicate_onsky_sources_never_promote_identity():
    multi=b"oid,main_id,ra,dec,otype\n123,FT Tau,65.913,24.937,TT*\n456,FT Tau,65.913,24.938,TT*\n"
    a=m.parse_simbad_original_csv(multi)
    b=m.parse_simbad_original_csv(csv_blob(oid="123"))
    x=m.external_alias_equivalence(a,b,gaia_ra=65,gaia_dec=24)
    assert x["status"]=="SIMBAD_ALIAS_AMBIGUOUS_MULTIPLE_OBJECTS"
    assert x["exact_external_catalogue_name_gaia_alias_verified"] is False

def test_invalid_html_and_malformed_original_simbad_response_fail_closed():
    for blob in (
        b"<html>Simbad unavailable</html>",
        b"oid,main_id,ra,dec,otype\n1,FT Tau,nan,24,TT*\n",
        b"oid,main_id,ra,dec,otype\n1,FT Tau,65,92,TT*\n",
        b"oid,ra,dec\n",
        b"oid,main_id,ra,dec,otype\n-1,FT Tau,65,24,TT*\n",
    ):
        with pytest.raises(ValueError):
            m.parse_simbad_original_csv(blob)

def test_only_exact_preregistered_queries_and_endpoints_are_allowed():
    assert "149623711269425408" in m.EXACT_GAIA_ADQL
    assert "'FT Tau'" in m.EXACT_FT_NAME_ADQL
    assert m.MIRRORS==(
        "https://simbad.cfa.harvard.edu/simbad/sim-tap/sync",
        "https://simbad.idia.ac.za/simbad/sim-tap/sync")
    with pytest.raises(ValueError):
        m.fetch_simbad_exact_query("https://example.org",m.EXACT_GAIA_ADQL)
    with pytest.raises(ValueError):
        m.fetch_simbad_exact_query(m.MIRRORS[0],"SELECT * FROM basic")

def test_frozen_r1_seed_and_six_original_ztf_exposures_are_unaltered():
    from scripts.prepare_taurus_variability_r1 import DEFAULT_SEED
    def js(path):return json.loads((ROOT/path).read_text("utf-8"))
    ft=m.frozen_ft_simbad_requirements(
        DEFAULT_SEED.read_bytes(),
        js("data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json"),
        js("reports/taurus_variability_r2/REAL_ALTERNATIVE_ZTF_OID_ORIGINAL_RUN_RECEIPT.json"),
        js("reports/taurus_variability_r2/FTTAU_SIX_ORIGINAL_NATIVE_SPATIAL_DAOPHOT_PSF_NO_RAW.json"))
    assert ft["name"]=="FT Tau"
    assert ft["gaia_id"]==m.FT_GAIA
    assert len(ft["fixed_oids"])==4
