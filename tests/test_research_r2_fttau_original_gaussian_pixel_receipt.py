"""Evidence-locked genuine six original ZTF pixel study, preserve NO-GO status."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EVID=ROOT/"reports/taurus_variability_r2/FTTAU_SIX_ORIGINAL_ZTF_INDEPENDENT_GAUSSIAN_PIXELS_NO_RAW.json"
CHI=ROOT/"reports/taurus_variability_r2/FTTAU_SIX_ORIGINAL_ZTF_CHI_BLIND_REFERENCES_NO_RAW.json"
BAD=ROOT/"reports/taurus_variability_r2/FTTAU_THREE_FROZEN_BAD_PSF_MASK_DIAGNOSIS_NO_RAW.json"


def load(path):
    return json.loads(path.read_text(encoding="utf8"))


def test_six_original_image_no_raw_observation_receipts_match_previous_file_sha():
    d=load(EVID)
    old=load(CHI)
    assert d["original_data_github_action_run_id"]==43279744985
    assert d["original_data_github_artifact_id"]==13970994224
    assert len(d["artifact_zip_sha256"])==64
    assert len(d["derived_original_json_sha256"])==64
    assert d["immutable_previous_ledger_sha256"]["original_chi_six"]==hashlib.sha256(CHI.read_bytes()).hexdigest()
    assert d["immutable_previous_ledger_sha256"]["original_bad_three"]==hashlib.sha256(BAD.read_bytes()).hexdigest()
    assert d["n_byte_verified_original_native_psfcats"]==6
    assert d["n_original_science_mask_pairs_downloaded_and_inspected"]==6
    assert d["n_valid_independent_analytic_gaussian_fits"]==4
    assert d["n_gaussian_numerical_failures"]==2
    assert d["n_two_epoch_pairs_with_both_numeric_gaussian_fits"]==1
    rows=d["six_immutable_original_data_exposure_derived_summary"]
    assert len(rows)==6
    groups=old["original_exact_3_ztf_oid_early_late_pairs"]
    for row,g,i in zip(rows,[g for g in groups for _ in (0,1)], [0,1]*3):
        prior=g["epochs"][i]
        assert row["band"]==g["band"] and row["field"]==g["field"]
        assert row["oid"]==g["oid"]
        assert (row["mjd"],row["fracday"],row["native_sha"],row["chi"])==(
            prior["mjd"],prior["day"],prior["sha"],prior["chi"])
        assert all(len(row[x])==64 for x in ("native_sha","science_sha","mask_sha"))
        assert row["core"]>=40 and row["sky"]>=75
    assert len({x["science_sha"] for x in rows})==6
    assert len({x["mask_sha"] for x in rows})==6


def test_previous_original_late_source_image_masks_remain_byte_identical():
    d=load(EVID)
    old={(x["band"],x["field"]):x for x in load(BAD)["source_checks"]}
    late=[x for x in d["six_immutable_original_data_exposure_derived_summary"]
          if x["role"]=="LATE_FROZEN_CHI_FAILURE"]
    assert len(late)==3
    assert [round(x["chi"],3) for x in late]==[.456,.424,.383]
    for source in late:
        prior=old[source["band"],source["field"]]
        assert source["science_sha"]==prior["original_science_cutout_sha256"]
        assert source["mask_sha"]==prior["original_mask_cutout_sha256"]


def test_four_numerical_fits_and_two_explicit_unresolved_not_astrophysics():
    d=load(EVID)
    rows=d["six_immutable_original_data_exposure_derived_summary"]
    accepted=[r for r in rows if r["fit"]=="INDEPENDENT_PIXEL_GAUSSIAN_NUMERIC_FIT_COMPLETE"]
    missing=[r for r in rows if r["fit"]=="BOUNDED_ANALYTIC_GAUSSIAN_OPTIMIZER_FAILED"]
    assert len(accepted)==4 and len(missing)==2
    assert [(r["band"],r["field"]) for r in missing]==[("g",609),("r",609)]
    assert all(r["role"]=="LATE_FROZEN_CHI_FAILURE" for r in missing)
    assert all(r["rms"] is None and r["fwhm"] is None
               and r["centroid_arcsec"] is None for r in missing)
    assert all(r["rms"]>1 and r["fwhm"]>0 and r["median_abs"]>0
               for r in accepted)
    assert d["valid_pair_g_1605_late_over_early_gaussian_rms_ratio"]==1.19234


def test_r2_original_quality_and_research_nonclaims_stay_frozen():
    d=load(EVID)
    assert d["original_5_of_8_pass_3_of_8_fail_1_of_4_pairs_unchanged"] is True
    assert d["three_original_low_chi_native_ztf_candidates_still_rejected"] is True
    assert d["gaussian_pixel_model_is_original_native_ztf_psf"] is False
    assert d["gaussian_residual_is_independently_calibrated_reduced_chi_square"] is False
    assert d["external_psf_model_validation_complete"] is False
    assert d["gaia_ztf_target_physical_identity_confirmed"] is False
    assert d["new_astrophysical_variables_or_companions"]==0
    assert d["n_original_ztf_oid_lightcurves_merged"]==0
    assert d["scientific_r2_complete"] is False
