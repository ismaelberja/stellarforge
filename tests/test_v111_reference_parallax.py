"""Adversarial synthetic Gaia DR3 reference-parallax and real-derived ledger QA."""
from __future__ import annotations

from copy import deepcopy
import csv
import io
import json
import math
from pathlib import Path

import pytest

from stellarforge.v111_reference_parallax import (
    all_required_gaia_ids, _correct_one_offset, evaluate_with_gaia_catalogue,
    run_from_bytes, load_ledger,
)
from stellarforge.v19_gaia_covariance import GAIA_COLUMNS,GAIA_ERRORS,GAIA_CORRELATIONS

LEDGER=Path(__file__).resolve().parents[1]/"data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json"


@pytest.fixture
def ledger():
    return load_ledger(LEDGER)


def gaia_row(sid, *, parallax=5.0, ruwe=1.03, ref_epoch=2016.0):
    i=int(sid)
    row={"source_id":str(sid),"ref_epoch":ref_epoch,
         "ra":65.9+(i%79)/1500,"dec":24.8+(i%41)/2000,
         "parallax":parallax,"pmra":6.0,"pmdec":-11.0,"ruwe":ruwe,
         "astrometric_params_solved":31}
    row.update({k:0.2 for k in GAIA_ERRORS})
    row.update({k:0.0 for k in GAIA_CORRELATIONS})
    return row


def synthetic_catalogue(ledger, *, parallax=5.0):
    ids=all_required_gaia_ids(ledger)
    records={}
    for sid in ids:
        records[sid]=gaia_row(sid,parallax=parallax,ruwe=(
            8.56752 if sid=="3419110734340795648" else 1.03))
    return records


def csv_catalogue(rows):
    f=io.StringIO()
    writer=csv.DictWriter(f,fieldnames=GAIA_COLUMNS)
    writer.writeheader()
    for row in rows.values():
        writer.writerow(row)
    return f.getvalue().encode("utf8")


def test_exact_gaia_reference_inventory_is_eight_refs_plus_two_targets(ledger):
    ids=all_required_gaia_ids(ledger)
    assert len(ids)==10
    assert len(set(ids))==10
    assert "149623711269425408" in ids
    assert "3419110734340795648" in ids


def test_parallax_correction_sign_is_model_minus_new_prediction():
    formal={
        "annual_geocentric_parallax_included":True,
        "geocentric_annual_parallax_minus_linear_east_mas":8.0,
        "geocentric_annual_parallax_minus_linear_north_mas":-3.0,
    }
    e,n=_correct_one_offset(.100,-.020,formal)
    assert e==pytest.approx(.092)
    assert n==pytest.approx(-.017)


def test_parallax_quality_fail_closed_if_missing_or_extreme():
    formal={"annual_geocentric_parallax_included":False,
            "geocentric_annual_parallax_minus_linear_east_mas":4,
            "geocentric_annual_parallax_minus_linear_north_mas":2}
    with pytest.raises(ValueError):
        _correct_one_offset(.1,.1,formal)
    formal["annual_geocentric_parallax_included"]=True
    formal["geocentric_annual_parallax_minus_linear_east_mas"]=500
    with pytest.raises(ValueError):
        _correct_one_offset(.1,.1,formal)


def test_all_ten_synthetic_gaia_ids_propagate_into_four_real_exposures(ledger):
    result=evaluate_with_gaia_catalogue(
        ledger,synthetic_catalogue(ledger),raw_gaia_sha256="e"*64)
    assert result["n_gaia_dr3_exact_ids_with_complete_5p"]==10
    assert result["n_reference_image_models_reanalyzed"]==13
    assert result["n_real_science_exposures_reanalyzed"]==4
    assert result["n_strict_loo_eligible_exposures"]==2
    assert result["median_reference_gaia_formal_sigma_east_mas"]>0
    assert result["max_reference_geometric_annual_shift_mas"]>0
    assert result["n_independently_calibrated_instrument_wcs_solutions"]==0
    assert result["n_confirmed_gaia_ztf_source_matches"]==0
    assert result["exposures"][2]["high_or_missing_target_ruwe_warning"] is True


def test_zero_gaia_parallax_preserves_old_loo_when_all_references_same(ledger):
    result=evaluate_with_gaia_catalogue(
        ledger,synthetic_catalogue(ledger,parallax=0),raw_gaia_sha256="a"*64)
    for e in result["exposures"]:
        assert e["original_strict_loo"]==e["parallax_aware_strict_loo"]
        assert e["original_inclusive_loo"]==e["parallax_aware_inclusive_loo"]
        if e["strict_loo_rms_change_mas"] is not None:
            assert e["strict_loo_rms_change_mas"]==0


def test_strict_quality_exclusions_do_not_become_valid_after_parallax(ledger):
    result=evaluate_with_gaia_catalogue(
        ledger,synthetic_catalogue(ledger),raw_gaia_sha256="f"*64)
    ft1,ft2,ci1,ci2=result["exposures"]
    assert ft1["n_strict_model_quality"]==1
    assert ft2["n_strict_model_quality"]==3
    assert ci1["n_strict_model_quality"]==4
    assert ci2["n_strict_model_quality"]==2
    assert ci2["parallax_aware_strict_loo"]["status"]==(
        "INSUFFICIENT_INDEPENDENT_REFERENCES_FOR_HOLDOUT")
    assert ci2["strict_loo_rms_change_mas"] is None
    assert ft2["target_minus_reference_proxy"]["status"]==(
        "NOT_REPORTED_INSUFFICIENT_QUALITY_OR_TARGET_PROFILE")
    assert ci1["target_minus_reference_proxy"]["status"]==(
        "PARALLAX_AWARE_TARGET_MINUS_REFERENCE_PROXY_ONLY")


def test_missing_or_extra_catalogue_source_is_rejected(ledger):
    rows=synthetic_catalogue(ledger)
    rows.pop(next(iter(rows)))
    with pytest.raises(ValueError,match="Missing/extra"):
        evaluate_with_gaia_catalogue(ledger,rows,raw_gaia_sha256="b"*64)


@pytest.mark.parametrize("digest",["bad","F"*64,"z"*64,""])
def test_forged_hash_is_rejected(ledger,digest):
    with pytest.raises(ValueError,match="digest"):
        evaluate_with_gaia_catalogue(
            ledger,synthetic_catalogue(ledger),raw_gaia_sha256=digest)


def test_missing_gaia_parallax_or_cross_correlation_fails_closed(ledger):
    rows=synthetic_catalogue(ledger)
    rows[next(iter(rows))]["ra_pmra_corr"]=None
    with pytest.raises((ValueError,TypeError)):
        evaluate_with_gaia_catalogue(ledger,rows,raw_gaia_sha256="c"*64)


def test_original_derived_input_provenance_cannot_be_forged(ledger):
    changed=deepcopy(ledger)
    changed["provenance"]["original_json_sha256"]="0"*64
    with pytest.raises(ValueError):
        all_required_gaia_ids(changed)


def test_v19_gaia_csv_parser_is_reused_without_raw_data_publication(ledger):
    data=csv_catalogue(synthetic_catalogue(ledger))
    a=run_from_bytes(ledger,data)
    b=run_from_bytes(ledger,data)
    assert a==b
    assert a["gaia_dr3_tap_raw_response_sha256"] and len(
        a["gaia_dr3_tap_raw_response_sha256"])==64
    assert not a["exposures"][0]["gaia_ztf_physical_identity_confirmed"]


def test_gaia_observation_date_alignment_matches_original_v18_models(ledger):
    output=evaluate_with_gaia_catalogue(
        ledger,synthetic_catalogue(ledger),raw_gaia_sha256="d"*64)
    assert [r["mjd_assumed_utc"] for r in output["exposures"]]==[
        58388.389016,58491.184780,58475.113750,58849.135984]


def test_input_only_contains_bounded_derived_original_gaia_candidates(ledger):
    assert sum(len(x["refs"]) for x in ledger["exposures"])==13
    assert all(x["target_gaia_id"] not in [
        r["id"] for r in x["refs"]] for x in ledger["exposures"])
    assert LEDGER.stat().st_size<100_000
