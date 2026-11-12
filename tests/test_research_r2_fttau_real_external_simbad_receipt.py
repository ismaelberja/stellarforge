"""Lock authentic original exact FT Tau/Gaia SIMBAD alias and NO-ZTF science inference."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

EVID=Path(__file__).resolve().parents[1]/"reports/taurus_variability_r2/FTTAU_SIMBAD_EXACT_GAIA_NAME_ALIAS_NO_RAW.json"
PSF=Path(__file__).resolve().parents[1]/"reports/taurus_variability_r2/FTTAU_SIX_ORIGINAL_NATIVE_SPATIAL_DAOPHOT_PSF_NO_RAW.json"


def test_authentic_simbad_exact_gaia_and_ft_names_resolve_uniquely_to_same_external_object():
    d=json.loads(EVID.read_text(encoding="utf8"))
    assert d["original_run_id"]==43314507016
    assert d["original_derived_only_artifact_id"]==13987771466
    assert d["exact_gaia_dr3_source_id"]=="149623711269425408"
    assert d["original_cds_simbad_mirror"]=="https://simbad.cfa.harvard.edu/simbad/sim-tap/sync"
    assert d["preferred_mirror_attempt_success"] is True
    assert d["second_mirror_queried"] is False
    assert d["n_gaia_exact_identifier_unique_simbad_objects"]==1
    assert d["n_ft_tau_exact_name_unique_simbad_objects"]==1
    assert d["both_original_simbad_queries_same_external_object"] is True
    assert d["external_curated_simbad_name_gaia_alias_supported"] is True
    assert d["simbad_external_main_identifier"]=="V* FT Tau"
    assert d["simbad_external_object_type"]=="Or*"
    assert d["simbad_basic_position_to_gaia_DR3_epoch2016_unpropagated_arcsec"]==0.36934
    assert d["position_epoch_and_source_error_model_independently_validated"] is False


def test_original_dual_cds_tap_and_previous_ztf_evidence_source_sha256_locked():
    d=json.loads(EVID.read_text(encoding="utf8"))
    assert d["original_gaia_exact_identifier_simbad_csv_sha256"]==d[
        "original_historical_ft_tau_name_simbad_csv_sha256"]
    assert len(d["original_gaia_exact_identifier_simbad_csv_sha256"])==64
    assert d["gaia_query_adql_sha256"]=="c35b9670ce5b3b8c51d08dec6d96df3d0cf1addaa36675704728fe087e66acc4"
    assert d["name_query_adql_sha256"]=="01cc32806c80ed156c6b71009fa9f4f5fd5c159d782aab4e41b3d1cd98c85e5f"
    assert d["original_gaia_dr3_five_parameter_tap_sha256"]=="399b5498d8d8a8a646073dfc029895ed64902940896d1789c63833a18074b642"
    assert d["frozen_prior_derived_ledgers_sha256"]["frozen_six_native_ztf_psf"]==hashlib.sha256(
        PSF.read_bytes()).hexdigest()
    assert len(d["original_derived_json_sha256"])==64
    assert len(d["original_derived_only_artifact_zip_sha256"])==64


def test_simbad_alias_does_not_upgrade_any_scientific_gaia_ztf_identity_or_variability():
    d=json.loads(EVID.read_text(encoding="utf8"))
    assert d["physical_gaia_to_each_original_ztf_source_identification_confirmed"] is False
    assert d["previous_original_4_ztf_oids_unchanged"] is True
    assert d["previous_original_5_of_8_source_qa_pass_3_of_8_fail_unchanged"] is True
    assert d["previous_original_1_of_4_quality_passing_two_night_source_pairs_unchanged"] is True
    assert d["previous_original_native_low_chi_rejections_relaxed"] is False
    assert d["n_original_ztf_oid_lightcurves_merged"]==0
    assert d["n_new_astrophysical_variable_or_companions"]==0
    assert d["scientific_r2_complete"] is False
    assert len(d["limitations"])>=4
