"""Synthetic-only v1.3 regression tests: no archive network or real survey data."""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from urllib.parse import urlencode
from zipfile import ZipFile

import pytest

from stellarforge.v13_observational_review import (
    review_irsa_artifact, write_provisional_review,
)

SEED = Path(__file__).resolve().parents[1] / "data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv"
GAIA_ID = "149623711269425408"
NAME = "FT Tau"
RA, DEC = 65.913324, 24.937195


def make_fixture(tmp_path, *, corrupt_hash=False, duplicate_target=False,
                 bad_host=False, bad_position=False, bad_field=False,
                 flags=False):
    fields = ["oid", "filtercode", "field", "ccdid", "qid",
              "mjd", "mag", "magerr", "catflags", "ra", "dec"]
    data = io.StringIO()
    writer = csv.DictWriter(data, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for i in range(3):
        writer.writerow({
            "oid": "609108400001155", "filtercode": "zg",
            "field": "" if bad_field else "609",
            "ccdid": "0x8", "qid": "0x4",
            "mjd": 59000 + i, "mag": 15.1 + i / 10,
            "magerr": .03, "catflags": 32768 if flags and i == 1 else 0,
            "ra": RA + .000001, "dec": DEC - .000001,
        })
    raw = data.getvalue().encode("utf8")
    url = "https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?" + urlencode({
        "POS": f"CIRCLE {RA} {DEC} 0.000555556",
        "BANDNAME": "g,r", "BAD_CATFLAGS_MASK": "32768", "FORMAT": "csv",
    })
    if bad_host:
        url = url.replace("irsa.ipac.caltech.edu", "attacker.example.net")
    entry = {
        "target": NAME, "gaia_dr3_id": GAIA_ID,
        "catalog_ra_deg": RA + (.001 if bad_position else 0),
        "catalog_dec_deg": DEC,
        "acquisition_status": "RAW_HTTP_RESPONSE_SAVED_ASSOCIATION_UNVERIFIED",
        "raw_sha256": "f" * 64 if corrupt_hash else hashlib.sha256(raw).hexdigest(),
        "raw_bytes": len(raw), "official_url": url,
        "inspection": {"rows": 3},
    }
    items = [entry, entry] if duplicate_target else [entry]
    file = tmp_path / "mock_private_zip.zip"
    with ZipFile(file, "w") as z:
        z.writestr("PILOT_STATUS.json", json.dumps({"results": items}))
        z.writestr(f"{GAIA_ID}_IRSA_RAW.csv", raw)
    return file


def test_synthetic_rows_stay_provisional_and_have_per_epoch_separations(tmp_path):
    artifact = make_fixture(tmp_path)
    result = review_irsa_artifact(artifact, SEED)
    assert result["n_targets"] == 1
    assert result["n_rows"] == 3
    assert result["n_curves"] == 1
    assert result["n_qc_accepted"] == 3
    curve = result["targets"][0]["curves"][0]
    assert curve["ztf_fields"] == ["609"]
    assert curve["status"] == "provisional_inside_radius_all_epochs"
    assert curve["median_epoch_corrected_separation_arcsec"] < 0.25
    assert result["gaia_ztf_identity_confirmations"] == 0
    assert result["physical_event_confirmations"] == 0
    paths = write_provisional_review(result, tmp_path / "summary")
    assert paths[0].is_file() and paths[1].is_file()
    assert "UNVERIFIED" not in paths[0].read_text().upper() or "unverified" in paths[1].read_text().lower()
    assert "15.1" not in paths[0].read_text()  # No individual magnitude records


@pytest.mark.parametrize("change", [
    {"corrupt_hash": True},
    {"duplicate_target": True},
    {"bad_host": True},
    {"bad_position": True},
])
def test_fails_closed_on_provenance_errors(tmp_path, change):
    with pytest.raises(ValueError):
        review_irsa_artifact(make_fixture(tmp_path, **change), SEED)


def test_masked_epoch_not_used_as_independent_position(tmp_path):
    report = review_irsa_artifact(make_fixture(tmp_path, flags=True), SEED)
    assert report["targets"][0]["n_rejected_epochs"] == 1
    curve = report["targets"][0]["curves"][0]
    assert curve["n_qc_accepted_epochs"] == 2
    assert curve["status"] == "insufficient_epoch_positions"


def test_missing_field_metadata_rejected(tmp_path):
    with pytest.raises(ValueError):
        review_irsa_artifact(make_fixture(tmp_path, bad_field=True), SEED)
