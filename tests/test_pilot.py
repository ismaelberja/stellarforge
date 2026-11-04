import csv
from pathlib import Path
import pytest
from stellarforge.catalog import read_membership
from stellarforge.pilot import propose_pilot, _balance_group, write_pilot


def fixture(tmp_path, *, ii=12, iii=12, unknown=0):
    f = tmp_path / "demo.csv"
    header = ["target_id", "ra_deg", "dec_deg", "coord_epoch_jyear", "membership_status", "reference_id", "gaia_dr3_source_id", "g_mag", "group_name", "disk_class"]
    rows = []
    for cls, count in [("II", ii), ("III", iii), ("unknown", unknown)]:
        for i in range(count):
            n = len(rows) + 1
            rows.append({"target_id": f"SYNTHETIC_{cls}_{i}", "ra_deg": 60 + n / 100,
                         "dec_deg": 25, "coord_epoch_jyear": 2016,
                         "membership_status": "adopted", "reference_id": "synthetic-only",
                         "gaia_dr3_source_id": str(1000000000000000000 + n),
                         "g_mag": 12 + (n % 10), "group_name": "group_" + str(n % 3),
                         "disk_class": cls})
    with f.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)
    return read_membership(f)


def test_pilot_no_certification_without_review(tmp_path):
    members = fixture(tmp_path)
    x = propose_pilot(members)
    assert len(x["targets"]) == 24
    assert x["status"] == "proposed_pending_scientific_review"
    assert not x["may_start_observational_ingestion"]
    assert sum(t["disk_class"] == "II" for t in x["targets"]) == 12
    assert sum(t["disk_class"] == "III" for t in x["targets"]) == 12
    assert x["selection_made_without_variability_measurements"]


def test_selection_reproducible_and_stratified(tmp_path):
    m = fixture(tmp_path, ii=24, iii=24)
    a = propose_pilot(m)
    b = propose_pilot(list(reversed(m)))
    assert [t["target_id"] for t in a["targets"]] == [t["target_id"] for t in b["targets"]]
    assert len(set(t["group_name"] for t in a["targets"])) == 3


def test_incomplete_labels_block_sample(tmp_path):
    m = fixture(tmp_path, ii=20, iii=6, unknown=10)
    p = propose_pilot(m, catalog_verified=False)
    assert p["targets"] == []
    assert p["status"] == "blocked_insufficient_verified_labels"
    assert not p["may_start_observational_ingestion"]
    assert len(p["blockers"]) == 2


def test_verified_flag_is_explicit_but_not_inferred(tmp_path):
    m = fixture(tmp_path)
    p = propose_pilot(m, catalog_verified=True)
    assert p["may_start_observational_ingestion"]
    f = tmp_path / "proposal.json"
    write_pilot(f, p)
    assert f.is_file()


def test_bad_quota(tmp_path):
    with pytest.raises(ValueError):
        propose_pilot(fixture(tmp_path), quotas={"II": 0})
    with pytest.raises(ValueError):
        propose_pilot(fixture(tmp_path), quotas={"fake": 12})