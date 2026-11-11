"""Nine-source original IRSA retry scope: never cherry-pick a science result."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import pytest

from stellarforge.r2_nine_source_recovery import freeze_nine_original_sources,recover_nine

ROOT=Path(__file__).resolve().parents[1]
SEED=(ROOT/"data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv").read_bytes()
PREV=json.loads((ROOT/"reports/taurus_variability_r2/IRSA_22_ORIGINAL_DERIVED_DIAGNOSTIC_LEDGER.json").read_text(encoding="utf8"))


def fake_response(ra,dec,variant,timeout_sec):
    assert timeout_sec==25.
    return {
        "variant":variant,"outcome":"PARSED_TABLE_WITH_ROWS",
        "returned_rows":16,"http_status":200,
        "query_sha256":"a"*64,"original_response_sha256":"b"*64,
        "response_bytes":1024,"response_content_type_group":"CSV",
        "source_table_format":"csv",
    }


def test_real_prior_24_source_receipt_freezes_exact_nine_failed_objects():
    pending=freeze_nine_original_sources(SEED,PREV)
    assert len(pending)==9
    assert {p["gaia_dr3_source_id"] for p in pending}=={
        "162259951730099968","156732977357829888",
        "156577881796362496","149623711269425408",
        "146764465639042176","3418414193726125184",
        "3314244366165299584","3314299238667410176",
        "3406270362673330944",
    }
    zero=[p for p in pending if p["query_variant"]=="NOBS_MIN_1"]
    assert [p["gaia_dr3_source_id"] for p in zero]==["3406270362673330944"]
    assert all(p["query_variant"]=="NOBS_MIN_5" for p in pending
               if p["gaia_dr3_source_id"]!=zero[0]["gaia_dr3_source_id"])


def test_no_new_source_accepted_and_no_claim_of_physical_identity():
    result=recover_nine(SEED,PREV,requester=fake_response,pause_sec=0)
    assert result["n_actual_original_irsa_requests"]==9
    assert result["n_new_positions_with_parsed_positional_ztf_rows"]==9
    assert result["n_cumulative_positions_with_historically_parsed_ztf_rows"]==24
    assert result["n_ztf_physical_counterparts_independently_verified"]==0
    assert result["n_genuine_astrophysical_variability_results_confirmed"]==0
    assert result["n_original_science_image_psf_mask_vetted"]==0
    assert result["scientific_r2_complete"] is False
    assert all(not q["physical_gaia_ztf_source_identity_authenticated"] for q in result["per_source"])
    assert all(not q["observed_stellar_variability_confirmed"] for q in result["per_source"])


def test_recovery_record_protects_timed_out_sources_from_nondetection_claim():
    def unavailable(ra,dec,variant,timeout_sec):
        return {"variant":variant,"outcome":"NETWORK_TIMEOUT",
                "returned_rows":None,"http_status":None}
    result=recover_nine(SEED,PREV,requester=unavailable,pause_sec=0)
    assert result["n_new_positions_with_parsed_positional_ztf_rows"]==0
    assert result["n_still_without_any_parsed_original_ztf_response"]==9
    assert result["per_request_status_counts"]=={"NETWORK_TIMEOUT":9}
    assert result["scientific_r2_complete"] is False


def test_valid_empty_ztf_table_still_not_astrophysical_negative_result():
    def empty(ra,dec,variant,timeout_sec):
        return {"variant":variant,"outcome":"PARSED_TABLE_ZERO_ROWS",
                "returned_rows":0,"http_status":200}
    result=recover_nine(SEED,PREV,requester=empty,pause_sec=0)
    assert result["n_still_without_any_parsed_original_ztf_response"]==9
    assert result["n_genuine_astrophysical_variability_results_confirmed"]==0
    assert result["n_ztf_physical_counterparts_independently_verified"]==0


@pytest.mark.parametrize("tamper",["fewer","duplicate","identity","bad_previous"])
def test_frozen_prior_source_cohort_tampering_fails_closed(tamper):
    obj=json.loads(json.dumps(PREV))
    if tamper=="fewer":
        obj["rows"].pop()
    elif tamper=="duplicate":
        obj["rows"][1]["gaia_dr3_source_id"]=obj["rows"][0]["gaia_dr3_source_id"]
    elif tamper=="identity":
        obj["rows"][0]["gaia_dr3_source_id"]="1111111111111111111"
    else:
        obj["n_previously_unresolved_still_without_parsed_rows"]=0
    with pytest.raises(ValueError):
        freeze_nine_original_sources(SEED,obj)


def test_reject_raw_photometry_leak_in_client_response():
    def malicious(ra,dec,variant,timeout_sec):
        r=fake_response(ra,dec,variant,timeout_sec)
        r["mjd"]=59000.
        return r
    with pytest.raises(ValueError,match="Unexpected original photometry"):
        recover_nine(SEED,PREV,requester=malicious,pause_sec=0)


def test_wrong_variant_raises_and_no_silent_fallback_to_unsupported_num_obs():
    def wrong(ra,dec,variant,timeout_sec):
        r=fake_response(ra,dec,variant,timeout_sec)
        r["variant"]="NUM_OBS_1"
        return r
    with pytest.raises(ValueError,match="wrong query variant"):
        recover_nine(SEED,PREV,requester=wrong,pause_sec=0)


def test_original_irsa_provenance_seed_matches_genuine_frozen_csv():
    assert PREV["original_r1_seed_sha256"]==hashlib.sha256(SEED).hexdigest()


def test_nobs_min_one_is_the_documented_supported_variant():
    from stellarforge.r2_irsa_failure_diagnosis import irsa_diagnostic_url
    from urllib.parse import parse_qs,urlparse
    url=irsa_diagnostic_url(65.913324,24.937195,"NOBS_MIN_1")
    pars=parse_qs(urlparse(url).query)
    assert pars["NOBS_MIN"]==["1"]
    assert "NUM_OBS" not in pars
    assert pars["FORMAT"]==["csv"]
