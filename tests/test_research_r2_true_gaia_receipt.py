"""Pin the verified R2 Gaia-only 24-source original-data summary in Git."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "reports/taurus_variability_r2/GAIA_24_EXACT_ID_RESULTS_NO_RAW.json"


def test_true_gaia_dr3_r2_qa_does_not_claim_original_ztf_matches():
    d = json.loads(RECEIPT.read_text(encoding="utf8"))
    assert d["observation_date_utc"] == "2026-11-11"
    assert d["original_github_actions_run_id"] == 43029175432
    assert d["number_of_predeclared_technical_candidates"] == 24
    assert d["number_exact_gaia_dr3_source_ids_returned"] == 24
    assert d["number_not_returned_by_gaia"] == 0
    assert d["number_gaia_preliminary_astrometric_quality_flags_passed"] == 17
    assert d["number_gaia_ruwe_greater_equal_1p4"] == 7
    assert d["independently_confirmed_physical_gaia_ztf_associations"] == 0
    assert d["original_ztf_science_image_neighbour_and_crowding_reviews_in_this_run"] == 0
    assert d["individually_vetted_literature_taurus_memberships"] == 0
    assert d["confirmed_new_astrophysical_variable_stars"] == 0
    assert d["r2_full_identity_completed"] is False
    assert d["original_gaia_tap_csv_committed"] is False
    assert "GAIA_EXACT_CATALOGUE_ID_SCREEN_ONLY" in d["scope"]


def test_r2_original_archive_result_has_reproducible_trace_and_warning():
    text = (ROOT / "research/taurus_variability/R2_REAL_GAIA_24_EXACT_ID_SCREEN.md").read_text(encoding="utf8")
    assert "43029175432" in text
    assert "24/24" in text
    assert "**17**" in text
    assert "**7**" in text
    assert "PARTIAL" in text
    assert "not an association" in text.lower() or "not a physical" in text.lower() or "not a verified" in text.lower() or "not an" in text.lower()
    assert "No raw Gaia TAP CSV" in text
    assert "not a" in text.lower()
