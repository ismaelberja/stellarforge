"""Taurus R2 closure: original 24 Gaia IDs, publisher and ZTF evidence strictness."""
from __future__ import annotations

import copy
import csv
import hashlib
import json
from pathlib import Path

import pytest

from scripts.audit_taurus_r2_24_go_no_go import (
    SEED_SHA, PUBLISHER_SHA, SOURCES, audit_24_final,
)
from scripts.run_taurus_r2_publisher_original_crosscheck import (
    original_publisher_check, COHORT_SHA, OFFICIAL_URLS,
)

ROOT=Path(__file__).resolve().parents[1]


def test_r2_final_source_closure_go_no_go_offline():
    v=audit_24_final(ROOT)
    assert v["status"]=="R2_24_SOURCE_SCREENING_ADJUDICATED_NO_GO_PHYSICAL_IDENTITY_OPEN"
    assert v["n_frozen_luhman_gaia_sources_with_original_publisher_rows_verified"]==24
    assert v["n_gaia_original_source_ids_retrieved"]==24
    assert v["n_original_ztf_positional_query_positions_with_rows"]==22
    assert v["n_ztf_provider_unresolved_positions"]==2
    assert v["n_independent_gaia_ztf_physical_sources_authenticated"]==0
    assert v["n_r3_physical_variability_eligible"]==0
    assert v["r2_source_identity_gate_success"] is False
    assert v["r2_source_access_and_ambiguity_screen_report_complete"] is True
    assert v["r3_scientific_inference_blocked"] is True


def test_exact_original_publisher_sha_reconciled_from_github_actions_receipt():
    publisher=json.loads((ROOT/SOURCES["publisher"]).read_text("utf8"))
    assert publisher["original_data_workflow_run_id"]==43499836719
    assert publisher["original_derived_only_artifact_id"]==14072229650
    assert publisher["accepted_origin"]=="PUBLISHER_IOP_SUPPLEMENT"
    assert publisher["attempts"][0]["response_sha256"]==PUBLISHER_SHA
    assert publisher["attempts"][0]["frozen_24_exact_gaia_ids_matched"]==24
    assert publisher["attempts"][0]["frozen_24_original_positions_matched"]==24
    assert publisher["raw_original_journal_mrt_committed"] is False
    assert publisher["third_party_pinned_mirror_full_byte_identity_compared"] is False
    assert "raw" not in publisher.get("accepted_origin","").lower()


def test_original_24_sources_exactly_once_and_seven_gaia_astrometry_reviews():
    frozen=(ROOT/SOURCES["seed"]).read_bytes()
    assert hashlib.sha256(frozen).hexdigest()==SEED_SHA==COHORT_SHA
    original=list(csv.DictReader(frozen.decode("utf-8-sig").splitlines()))
    d=json.loads((ROOT/SOURCES["ledger"]).read_text("utf8"))
    sources=d["sources"]
    assert len(sources)==len(original)==24
    assert [z["gaia_dr3_source_id"] for z in sources]==[z["gaia"] for z in original]
    assert len([s for s in sources if s["gaia_astrometry_review_required"]])==7
    assert len([s for s in sources if s["gaia_original_neighbours_within_5arcsec"]>0])==4
    assert all(s["gaia_original_neighbours_within_2arcsec"]==0 for s in sources)


def test_two_original_archive_failures_not_relabelled_as_nonvariable():
    d=json.loads((ROOT/SOURCES["ledger"]).read_text("utf8"))
    z={r["gaia_dr3_source_id"]:r for r in d["sources"]}
    assert z["3314244366165299584"]["ztf_original_position_query_access"]=="NO_ROWS_AT_NOBS_MIN_5_NOT_NONDETECTION"
    assert z["3406270362673330944"]["ztf_original_position_query_access"]=="HTTP_400_NOBS_MIN_1_ARCHIVE_UNRESOLVED"
    assert all(z[k]["ztf_last_original_positional_rows"] is None for k in
               ["3314244366165299584","3406270362673330944"])
    assert sum("PARSED" in row["ztf_original_position_query_access"] for row in d["sources"])==22


def test_no_gaia_ztf_physical_match_inferred_from_fttau_original_alias():
    d=json.loads((ROOT/SOURCES["ledger"]).read_text("utf8"))
    ft=next(z for z in d["sources"] if z["gaia_dr3_source_id"]=="149623711269425408")
    assert ft["simbad_fttau_historical_name_gaia_dr3_curated_alias_verified"] is True
    assert ft["original_number_distinct_ztf_oids_when_reviewed"]==4
    assert ft["fttau_original_native_psf_source_quality_5_of_8_passed"]==5
    assert ft["fttau_original_native_two_night_pairs_1_of_4_passed"]==1
    assert ft["original_physical_gaia_to_ztf_identity_authenticated"] is False
    assert ft["r3_physical_variability_scientific_analysis_eligible"] is False
    assert all(not s["original_physical_gaia_to_ztf_identity_authenticated"]
               for s in d["sources"])
    assert d["r3_physical_stellar_variability_analysis_authorized"] is False


@pytest.mark.parametrize("bad_key,bad_value",[
    ("r2_physical_source_identity_success",True),
    ("r2_scientific_identity_gate_not_met",False),
    ("r3_physical_stellar_variability_analysis_authorized",True),
    ("old_fttau_three_low_native_chi_source_quality_failures_unmodified",False),
    ("original_publisher_luhman2023_mrt_sha256","0"*64),
])
def test_false_new_source_identity_claims_are_rejected_offline(tmp_path,bad_key,bad_value):
    # Isolate only the final decision JSON while original proof inputs
    # remain the same; no original raw data uploaded or network required.
    d=json.loads((ROOT/SOURCES["ledger"]).read_text("utf8"))
    d[bad_key]=bad_value
    path=(tmp_path/SOURCES["ledger"])
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(d),encoding="utf8")
    # Build a tiny synthetic root containing all other original evidence
    # paths. Directory and symlink traversal are rejected by the auditor.
    for key,rel in SOURCES.items():
        if key=="ledger": continue
        dest=tmp_path/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes((ROOT/rel).read_bytes())
    with pytest.raises(ValueError):
        audit_24_final(tmp_path)


@pytest.mark.parametrize("field,value",[
    ("scientifically_r3_eligible_original_source_lightcurves",1),
    ("cumulative_positional_irsa_ztf_parsed_target_positions",24),
    ("irsa_target_positions_without_a_parsed_original_response",0),
    ("original_journal_table_exact_gaia_ids_and_positions_verified",23),
])
def test_final_24_original_source_denominators_cannot_be_inflated(tmp_path,field,value):
    for rel in SOURCES.values():
        dest=tmp_path/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes((ROOT/rel).read_bytes())
    path=tmp_path/SOURCES["ledger"]
    d=json.loads(path.read_text("utf8"))
    d["summary"][field]=value
    path.write_text(json.dumps(d),encoding="utf8")
    with pytest.raises(ValueError):
        audit_24_final(tmp_path)


def test_mocked_publisher_original_catalogue_unavailable_fail_closed():
    seed=(ROOT/SOURCES["seed"]).read_bytes()
    calls=[]
    def probe(url):
        calls.append(url)
        return None,{"outcome":"NETWORK_OR_TIMEOUT","exception_type":"TimeoutError"}
    result=original_publisher_check(seed,probe=probe)
    assert len(calls)==len(OFFICIAL_URLS)==4
    assert result["full_original_24_source_table_verified_from_accepted_origin"] is False
    assert result["original_publisher_source_table_24_rows_verified"] is False
    assert result["accepted_origin"] is None
    assert result["n_ztf_gaia_physical_source_associations_established_by_membership"]==0
    assert len(result["attempts"])==4


def test_publisher_source_bad_frozen_seed_sha_is_rejected_without_queries():
    seed=(ROOT/SOURCES["seed"]).read_bytes()
    with pytest.raises(ValueError,match="SHA"):
        original_publisher_check(seed+b"\n",probe=lambda url:None)


def test_original_source_ledger_has_no_raw_fits_or_private_ztf_rows():
    d=json.loads((ROOT/SOURCES["ledger"]).read_text("utf8"))
    assert d["summary"]["original_journal_table_exact_gaia_ids_and_positions_verified"]==24
    for p in d["original_source_evidence_paths"]:
        assert p.endswith(".json")
        assert (ROOT/p).is_file()
    for row in d["sources"]:
        assert "new_variable_star_confirmed" not in row
        assert "flux" not in row
        assert "pixels" not in row
        assert "magnitude_time_series" not in row
    assert not d["r2_physical_source_identity_success"]
