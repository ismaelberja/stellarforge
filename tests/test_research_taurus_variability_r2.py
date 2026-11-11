"""R2: exact-ID Gaia DR3 source screening and anticlaim tests (NO NETWORK)."""
import csv
import io
from pathlib import Path

import pytest

from scripts.run_taurus_variability_r2_exact_gaia import run
from stellarforge.r2_gaia_identity import (
    COLUMNS, audit_exact_gaia_cohort, exact_id_adql,
    parse_exact_gaia_ids, offline_declaration,
)

SEED = (Path(__file__).resolve().parents[1] /
        "data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv")
ROWS = list(csv.DictReader(io.StringIO(SEED.read_text(encoding="utf8"))))
assert len(ROWS) == 24
IDS = [r["gaia"] for r in ROWS]


def make_csv(rows, *, custom=None):
    data = []
    for i, r in enumerate(rows):
        sid = r["gaia"]
        item = {
            "source_id": sid, "ref_epoch": "2016.0",
            "ra": r["ra"], "dec": r["dec"],
            "pmra": r["pmra"], "pmdec": r["pmdec"],
            "parallax": "7.5", "ruwe": "1.10",
            "duplicated_source": "false",
            "astrometric_params_solved": "31",
            "phot_g_mean_mag": r["gmag"],
        }
        if custom:
            custom(item,i)
        data.append(item)
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(data)
    return stream.getvalue().encode()


def synthetic_fetch(ids):
    return make_csv([r for r in ROWS if r["gaia"] in ids])


def test_r2_all_historic_gaia_ids_return_but_no_physical_ztf_match():
    out = run(SEED.read_bytes(), fetcher=synthetic_fetch)
    assert out["n_r1_technical_candidates"] == 24
    assert out["n_gaia_dr3_exact_ids_returned"] == 24
    assert out["n_gaia_preliminary_quality_flags"] == 24
    assert out["n_gaia_dr3_exact_ids_missing"] == 0
    assert out["n_confirmed_gaia_ztf_physical_associations"] == 0
    assert out["n_independently_vetted_taurus_memberships"] == 0
    assert out["full_r2_independent_source_identification_completed"] is False
    assert all(row["eligible_for_r3_physical_variability_analysis"] is False
               for row in out["results"])
    assert all(row["gaia_ztf_physical_source_identity"] == "NOT_VERIFIED"
               for row in out["results"])
    assert all(row["ztf_oid_association"] == "NOT_CHECKED"
               for row in out["results"])
    assert len(out["gaia_raw_response_sha256_no_raw_committed"]) == 2


def test_high_ruwe_and_duplicate_gaia_statuses_warn_not_classify_stars():
    def marked(item, i):
        if item["source_id"] == IDS[0]:
            item["ruwe"] = "8.57"
        if item["source_id"] == IDS[1]:
            item["duplicated_source"] = "true"
    p = [make_csv(ROWS[:12], custom=marked), make_csv(ROWS[12:])]
    out = audit_exact_gaia_cohort(ROWS,p)
    assert out["n_gaia_ruwe_at_least_1p4"] == 1
    assert out["n_gaia_preliminary_quality_flags"] == 22
    assert out["n_confirmed_new_ztf_variable_stars"] == 0


def test_missing_exact_gaia_id_is_not_counted_as_nonvariable_or_negative():
    p = [make_csv(ROWS[:11]),make_csv(ROWS[12:])]
    out = audit_exact_gaia_cohort(ROWS,p)
    assert out["n_gaia_dr3_exact_ids_missing"] == 1
    missing = next(x for x in out["results"]
                   if x["gaia_dr3_source_id"] == IDS[11])
    assert missing["gaia_exact_source_status"] == "NOT_RETURNED_BY_GAIA_TAP"
    assert missing["eligible_for_r3_physical_variability_analysis"] is False
    assert out["n_confirmed_gaia_ztf_physical_associations"] == 0


def test_invalid_gaia_tap_response_cannot_be_promoted_to_real_science():
    ids = tuple(IDS[:12])
    for broken in (b"<html>HTTP error</html>", b"", b"wrong,header\nfoo,bar\n"):
        with pytest.raises(ValueError):
            parse_exact_gaia_ids(broken,ids)


def test_source_ids_unique_and_exact_query_not_cone_search():
    query = exact_id_adql(tuple(IDS[:12]))
    assert "WHERE source_id IN (" in query
    assert "gaia_source" in query
    assert "CONTAINS" not in query
    assert all(s in query for s in IDS[:12])
    for invalid in ((IDS[0],IDS[0]), tuple(), (IDS[0],"1 OR 1=1")):
        with pytest.raises(ValueError):
            exact_id_adql(invalid)


def test_gaia_reply_cannot_include_an_unrequested_source():
    ids = tuple(IDS[:12])
    extra = make_csv(ROWS[12:13])
    with pytest.raises(ValueError,match="Unexpected"):
        parse_exact_gaia_ids(extra,ids)


def test_gaia_reply_duplicate_rows_rejected():
    ids = tuple(IDS[:12])
    payload = make_csv([ROWS[0],ROWS[0]])
    with pytest.raises(ValueError,match="duplicated"):
        parse_exact_gaia_ids(payload,ids)


@pytest.mark.parametrize("key,value", [
    ("ref_epoch", "2015.0"), ("duplicated_source", "maybe"),
    ("ra", "400"), ("ruwe", "infinity"),
    ("astrometric_params_solved", "unknown"),
])
def test_invalid_gaia_scientific_rows_fails_closed(key,value):
    def tamper(item,i):
        if i == 0:
            item[key] = value
    with pytest.raises(ValueError):
        parse_exact_gaia_ids(make_csv(ROWS[:12],custom=tamper),tuple(IDS[:12]))


def test_no_network_means_undetermined_not_a_real_positive_observation():
    placeholder = offline_declaration(ROWS)
    assert placeholder["is_original_gaia_data"] is False
    assert placeholder["n_confirmed_gaia_ztf_physical_associations"] == 0
    assert "PENDING" in placeholder["phase"]


def test_no_shrinking_technical_cohort_to_look_better():
    with pytest.raises(ValueError,match="complete"):
        audit_exact_gaia_cohort(ROWS[:23],
                               [make_csv(ROWS[:12]),make_csv(ROWS[12:])])
