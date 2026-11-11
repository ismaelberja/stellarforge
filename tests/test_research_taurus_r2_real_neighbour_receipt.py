"""Actual 2026-11-11 public Gaia/IRSA R2 source receipt anticlaim contract."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "reports/taurus_variability_r2/GAIA_NEIGHBOUR_ZTF_POSITIONAL_ORIGINAL_RESULTS_NO_RAW.json"


def test_real_24_field_results_pin_exact_science_limitations():
    x = json.loads(PATH.read_text(encoding="utf-8"))
    assert x["original_research_workflow_run_id"] == 43031689454
    assert x["source_artifact_id"] == 13861901170
    assert len(x["source_artifact_zip_sha256"]) == 64
    assert x["frozen_n_technical_gaia_candidates"] == 24
    assert x["n_original_gaia_15arcsec_neighbour_cones_parsed"] == 24
    assert x["n_original_gaia_cones_failed_or_truncated"] == 0
    assert x["n_targets_with_catalogued_gaia_neighbour_within_2arcsec"] == 0
    assert x["n_targets_with_catalogued_gaia_neighbour_within_5arcsec"] == 4
    assert x["n_original_ztf_2arcsec_positional_queries_parsed"] == 2
    assert x["n_ztf_queries_unavailable_or_unparseable"] == 22
    assert x["n_targets_with_multiple_ztf_oids_in_same_band"] == 2
    assert x["n_independently_validated_gaia_to_ztf_physical_source_matches"] == 0
    assert x["n_confirmed_new_variable_stars"] == 0
    assert x["complete_R2_source_identity_study"] is False
    assert x["failure_cause_for_22_unparseable_ztf_queries_diagnosed"] is False
    assert x["original_raw_gaia_or_ztf_csv_files_uploaded"] is False


def test_only_two_original_ztf_usable_fields_still_ambiguous():
    d = json.loads(PATH.read_text(encoding="utf-8"))
    records = d["original_ztf_parsed_cases"]
    assert len(records) == 2
    assert {row["technical_name"] for row in records} == {
        "V892 Tau", "LkHa 332/G2 A+B"}
    assert [r["n_original_ztf_raw_rows"] for r in records] == [3044, 842]
    assert [r["n_distinct_ztf_oid_band_time_groups"] for r in records] == [6, 2]
    assert all(not r["physical_counterpart_verified"] for r in records)
    assert all(r["gaia_ruwe_approx"] > 1.4 for r in records)


def test_report_explicitly_denies_negative_results_from_archive_errors():
    p = ROOT / "research/taurus_variability/R2_REAL_GAIA_NEIGHBOURS_ZTF_POSITIONS.md"
    s = p.read_text(encoding="utf-8")
    assert "22/24" in s
    assert "not" in s.lower()
    assert "not automatically" not in s or "must not" in s
    assert "not" in s.lower() and "non-variable" in s.lower()
    assert "source" in s.lower()
    assert "not a" in s.lower()
    assert "0" in s
    assert "independent" in s.lower()
