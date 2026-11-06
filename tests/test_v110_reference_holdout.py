"""Synthetic adversarial + immutable real-derived reference ledger regression."""
from __future__ import annotations

from copy import deepcopy
import json
import math
from pathlib import Path

import pytest

from stellarforge.v110_reference_holdout import (
    SCHEMA, REQUIRED_PROVENANCE_SHA, validate_derived_v18_ledger,
    leave_one_out_translation, quality_filter_references,
    audit_exposure, evaluate_derived_ledger, load_and_audit,
)

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/"data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json"


@pytest.fixture
def original():
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def sample_ref(sid, east=.1, north=.02, *, flagged=False):
    return {
        "id":str(sid), "east":east, "north":north,
        "status":"PSF_PROXY_REVIEW_REQUIRED" if flagged else
                 "PSF_PROXY_PROVISIONAL_ONLY",
        "residual_proxy":8.1 if flagged else 2.1,
        "axis_ratio":1.1, "fit_near_bound":False,
    }


def test_immutable_real_provenance_and_original_inventory(original):
    assert original["schema_version"]==SCHEMA
    assert original["provenance"]["original_run_id"]==42077605987
    assert original["provenance"]["original_json_sha256"]==REQUIRED_PROVENANCE_SHA
    validate_derived_v18_ledger(original)
    assert len(original["exposures"])==4
    assert sum(len(x["refs"]) for x in original["exposures"])==13
    assert sum(x["n_reference_requests"] for x in original["exposures"])==16


def test_real_four_exposure_holdout_pass_and_strict_sensitivity(original):
    result=evaluate_derived_ledger(original)
    assert result["n_reference_fits_in_original_derived_evidence"]==13
    assert result["n_exposures_with_loo_all_image_models"]==3
    assert result["n_exposures_with_loo_strict_image_models"]==2
    assert result["n_exposures_with_strict_reference_subtracted_target_proxy"]==1
    assert result["independently_calibrated_detector_wcs_solutions"]==0
    assert result["authenticated_single_star_psfs"]==0
    assert result["physical_gaia_ztf_source_associations_confirmed"]==0


def test_real_ft_tau_second_exposure_holdout_is_unstable_not_precise(original):
    result=audit_exposure(original["exposures"][1])
    all_=result["all_model_statuses_loocv"]
    strict=result["strict_model_status_loocv"]
    assert all_["n_usable_reference_models"]==3
    assert strict["n_usable_reference_models"]==3
    assert all_["loo_rms_radial_disagreement_arcsec"]==pytest.approx(.075782,abs=.000002)
    assert all_["loo_max_radial_disagreement_arcsec"]==pytest.approx(.099156,abs=.000002)
    assert all_["status"]=="SMALL_SAMPLE_LOO_DISAGREEMENT_ONLY"
    assert "radial_arcsec" not in result["strict_reference_subtracted_target_proxy"]


def test_real_cida_first_exposure_has_four_strict_ref_holdouts(original):
    result=audit_exposure(original["exposures"][2])
    cv=result["strict_model_status_loocv"]
    assert cv["n_usable_reference_models"]==4
    assert cv["loo_rms_radial_disagreement_arcsec"]==pytest.approx(.093046,abs=.000002)
    assert cv["loo_max_radial_disagreement_arcsec"]==pytest.approx(.115728,abs=.000002)
    assert result["strict_reference_subtracted_target_proxy"]["is_not_astrometric_accuracy"]


def test_real_cida_later_exposure_all_vs_strict_changes_conclusion(original):
    result=audit_exposure(original["exposures"][3])
    assert result["all_model_statuses_loocv"]["n_usable_reference_models"]==5
    assert result["strict_model_status_loocv"]["n_usable_reference_models"]==2
    assert result["strict_model_status_loocv"]["status"]==(
        "INSUFFICIENT_INDEPENDENT_REFERENCES_FOR_HOLDOUT")
    assert result["all_model_statuses_loocv"]["loo_rms_radial_disagreement_arcsec"]==(
        pytest.approx(.051244,abs=.000002))
    assert result["strict_reference_subtracted_target_proxy"]["status"]==(
        "NOT_REPORTED_DUE_TO_TARGET_OR_REFERENCE_QUALITY_GATE")


@pytest.mark.parametrize("field,value",[
    ("schema_version","wrong"),
    ("provenance",{"original_json_sha256":"wrong","original_run_id":1}),
    ("exposures",[]),
])
def test_forged_or_invalid_ledger_fails_closed(original,field,value):
    bad=deepcopy(original)
    bad[field]=value
    with pytest.raises(ValueError):
        validate_derived_v18_ledger(bad)


def test_duplicate_frame_is_rejected(original):
    bad=deepcopy(original)
    bad["exposures"].append(deepcopy(bad["exposures"][0]))
    with pytest.raises(ValueError,match="Repeated ZTF exposure"):
        validate_derived_v18_ledger(bad)


def test_duplicate_gaia_candidate_not_counted_twice(original):
    bad=deepcopy(original)
    bad["exposures"][1]["refs"][1]["id"]=bad["exposures"][1]["refs"][0]["id"]
    with pytest.raises(ValueError):
        validate_derived_v18_ledger(bad)


def test_reference_cannot_be_its_own_gaia_target(original):
    bad=deepcopy(original)
    bad["exposures"][1]["refs"][0]["id"]=bad["exposures"][1]["target_gaia_id"]
    with pytest.raises(ValueError):
        validate_derived_v18_ledger(bad)


@pytest.mark.parametrize("bad",[float("nan"),float("inf"),"NaN",True])
def test_nonfinite_and_bad_types_are_rejected(original,bad):
    modified=deepcopy(original)
    modified["exposures"][2]["refs"][0]["east"]=bad
    with pytest.raises(ValueError):
        validate_derived_v18_ledger(modified)


def test_more_fits_than_original_requests_is_rejected(original):
    modified=deepcopy(original)
    modified["exposures"][2]["n_reference_requests"]=2
    with pytest.raises(ValueError):
        validate_derived_v18_ledger(modified)


def test_holdout_does_not_use_itself_for_prediction():
    references=[
        sample_ref("11",.10,0),sample_ref("22",.11,0),
        sample_ref("33",.50,0)
    ]
    result=leave_one_out_translation(references)
    left=[r for r in result["heldout_reference_errors"]
          if r["heldout_gaia_id"]=="33"][0]
    assert left["east_prediction_error_arcsec"]==pytest.approx(.395)
    assert result["loo_max_radial_disagreement_arcsec"]>=.395
    assert not result["independent_ztf_wcs_solution_validated"]


@pytest.mark.parametrize("n",[0,1,2])
def test_holdout_minimum_three_independent_references(n):
    result=leave_one_out_translation([sample_ref(str(i+1)) for i in range(n)])
    assert result["status"]=="INSUFFICIENT_INDEPENDENT_REFERENCES_FOR_HOLDOUT"
    assert "loo_rms_radial_disagreement_arcsec" not in result


def test_duplicate_ids_rejected_in_holdout_even_with_valid_looking_offsets():
    with pytest.raises(ValueError,match="distinct"):
        leave_one_out_translation([sample_ref("11"),sample_ref("11"),sample_ref("12")])


def test_flagged_gaussian_profiles_excluded_by_strict_screen():
    refs=[sample_ref("11"),sample_ref("22",flagged=True),
          sample_ref("33"),sample_ref("44",flagged=True)]
    assert len(quality_filter_references(refs,require_clean_fit=True))==2
    assert len(quality_filter_references(refs,require_clean_fit=False))==4


def test_references_near_optimizer_bound_excluded_in_both_screens():
    refs=[sample_ref("11")]
    refs[0]["fit_near_bound"]=True
    assert not quality_filter_references(refs,require_clean_fit=True)
    assert not quality_filter_references(refs,require_clean_fit=False)


def test_read_only_standalone_ledger_analysis_is_reproducible():
    a=load_and_audit(EVIDENCE)
    b=load_and_audit(EVIDENCE)
    assert a==b
    assert a["input_derived_v18_ledger_sha256"]
    assert all(not r["gaia_ztf_astrophysical_source_identity_confirmed"]
               for r in a["exposures"])
