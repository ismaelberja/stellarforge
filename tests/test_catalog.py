import csv
from pathlib import Path
import pytest

from stellarforge.catalog import read_membership, audit_members, write_audit
from stellarforge.gaia_batch import exact_ids_query


BASE = {
    "target_id": "demo-source-1", "ra_deg": "65.0", "dec_deg": "25.0",
    "coord_epoch_jyear": "2016", "membership_status": "adopted",
    "reference_id": "doi:10.3847/1538-3881/ac9da3", "gaia_dr3_source_id": "3420750548559422592",
    "pmra_masyr": "12", "pmdec_masyr": "-9", "g_mag": "14.9",
    "group_name": "L1495", "disk_class": "II", "coordinate_origin": "Gaia DR3",
}


def make_csv(tmp_path, rows):
    f = tmp_path / "catalog.csv"
    with f.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(BASE))
        writer.writeheader()
        writer.writerows(rows)
    return f


def test_catalog_and_audit_missing_gaia_is_not_nonmember(tmp_path):
    with_id = dict(BASE)
    no_id = dict(BASE, target_id="b", gaia_dr3_source_id="", pmra_masyr="", pmdec_masyr="", disk_class="III")
    items = read_membership(make_csv(tmp_path, [with_id, no_id]))
    assert len(items) == 2
    a = audit_members(items)
    assert a["adopted_member_rows"] == 2
    assert a["adopted_gaia_id_present"] == 1
    assert a["adopted_gaia_id_missing"] == 1
    assert not a["matches_published_count"]
    assert a["gaia_count_matches_paper"] is None


def test_source_ids_preserved_as_strings(tmp_path):
    items = read_membership(make_csv(tmp_path, [BASE]))
    assert items[0].gaia_dr3_source_id == "3420750548559422592"
    assert "3420750548559422592" in exact_ids_query(items)
    assert "g.source_id IN" in exact_ids_query(items)


@pytest.mark.parametrize("changes", [
    {"ra_deg": "360"}, {"dec_deg": "-92"}, {"ra_deg": "nan"},
    {"coord_epoch_jyear": ""}, {"coord_epoch_jyear": "1800"},
    {"gaia_dr3_source_id": "342.0"}, {"gaia_dr3_source_id": "0"},
    {"gaia_dr3_source_id": "1 OR 1=1"}, {"gaia_dr3_source_id": "9223372036854775808"},
    {"membership_status": "proven"}, {"disk_class": "maybe disk"},
    {"g_mag": "inf"}, {"g_mag": "100"}, {"reference_id": ""},
])
def test_rejects_bad_input(tmp_path, changes):
    with pytest.raises(ValueError):
        read_membership(make_csv(tmp_path, [dict(BASE, **changes)]))


def test_duplicates_blocked(tmp_path):
    with pytest.raises(ValueError, match="Duplicate target_id"):
        read_membership(make_csv(tmp_path, [BASE, BASE]))


def test_audit_provenance(tmp_path):
    file = make_csv(tmp_path, [BASE])
    dest = tmp_path / "audit.json"
    result = write_audit(file, read_membership(file), reference_url="https://doi.org/10.3847/1538-3881/ac9da3", output=dest)
    assert len(result["provenance"]["sha256"]) == 64
    assert dest.exists()
    assert result["provenance"]["review_status"] == "requires_scientific_verification"
    with pytest.raises(ValueError):
        write_audit(file, read_membership(file), reference_url="file:///tmp/test", output=dest)


def test_source_not_loaded_as_gaia_exact_ids_when_missing(tmp_path):
    missing = dict(BASE, gaia_dr3_source_id="")
    with pytest.raises(ValueError, match="No verified Gaia"):
        exact_ids_query(read_membership(make_csv(tmp_path, [missing])))