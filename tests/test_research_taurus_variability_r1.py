"""R1 pre-registration must not turn secondary catalogue rows into science claims."""
import csv
import io
from pathlib import Path

import pytest

from scripts.prepare_taurus_variability_r1 import (
    EXPECTED_SEED_ROWS, prepare_technical_cohort, STUDY_ID,
)

SEED = (Path(__file__).resolve().parents[1] /
        "data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv")


def _rewrite(modifier):
    stream = io.StringIO(SEED.read_text(encoding="utf-8"), newline="")
    source = csv.DictReader(stream)
    fields = source.fieldnames
    rows = list(source)
    modifier(rows)
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def test_real_historic_technical_seed_is_predeclared_but_not_scientifically_vetted():
    raw = SEED.read_bytes()
    data = prepare_technical_cohort(raw)
    assert data["study_id"] == STUDY_ID
    assert data["n_preexisting_technical_candidates"] == EXPECTED_SEED_ROWS
    assert data["representative_region_population"] is False
    assert data["publisher_original_catalogue_checked"] is False
    assert data["all_gaia_ztf_physical_source_associations_authenticated"] is False
    assert data["study_sample_scientifically_approved"] is False
    assert data["new_astrophysical_variable_stars_confirmed"] == 0
    assert data["source_selection_conditioned_on_ztf_variability_results"] is False
    rows = data["technical_candidates"]
    ids = [r["gaia_dr3_source_id"] for r in rows]
    assert len(ids) == len(set(ids)) == 24
    assert ids == sorted(ids)
    assert all(r["ztf_physical_source_identity_verified"] is False for r in rows)
    assert all(r["eligible_for_physical_variability_claim"] is False for r in rows)
    assert "gaia_dr3_source_id" in rows[0]
    assert "magnitude" not in str(rows[0]).lower()


def test_repeated_seed_generates_exactly_same_pre_registration():
    payload = SEED.read_bytes()
    assert prepare_technical_cohort(payload) == prepare_technical_cohort(payload)


def test_no_posthoc_star_removal_allowed():
    payload = _rewrite(lambda rows: rows.pop())
    with pytest.raises(ValueError, match="all 24"):
        prepare_technical_cohort(payload)


def test_no_posthoc_extra_star_allowed():
    def add(rows):
        new = dict(rows[-1])
        new["gaia"] = "99999999999"
        rows.append(new)
    with pytest.raises(ValueError, match="all 24"):
        prepare_technical_cohort(_rewrite(add))


def test_duplicate_ids_are_rejected():
    def duplicate(rows):
        rows[1]["gaia"] = rows[0]["gaia"]
    with pytest.raises(ValueError, match="Duplicate"):
        prepare_technical_cohort(_rewrite(duplicate))


@pytest.mark.parametrize("field,value,match", [
    ("gaia", "some-id", "Gaia ID"),
    ("reference", "estimated", "non-Gaia"),
    ("gmag", "-15", "violates"),
    ("ra", "370", "violates"),
    ("dec", "-91", "violates"),
    ("pmra", "nan", "violates"),
    ("original_line", "zero", "Malformed"),
])
def test_malformed_coordinates_or_selection_cannot_silently_pass(field,value,match):
    def alter(rows):
        rows[0][field] = value
    with pytest.raises(ValueError, match=match):
        prepare_technical_cohort(_rewrite(alter))


def test_empty_archive_not_a_negative_scientific_result():
    with pytest.raises(ValueError, match="Missing or implausible"):
        prepare_technical_cohort(b"")
