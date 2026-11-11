"""Synthetic, offline R2 Gaia-neighbour and original ZTF OID screen contracts.

No actual Gaia/IRSA requests during CI. A successful positional result
MUST remain scientifically unconfirmed pending original image and independent
astrometric/crowding review.
"""
from __future__ import annotations

import csv
import io
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

from scripts.run_taurus_r2_counterpart_screen import run
from stellarforge.r2_counterpart_screen import (
    assess_r2_target, fetch_ztf_positional, summarise_r2_screen,
    ztf_positional_url,
)
from stellarforge.v14_field_review import GAIA_COLUMNS

ROOT = Path(__file__).resolve().parents[1]
SEED = (ROOT / "data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv").read_bytes()
ROWS = list(csv.DictReader(io.StringIO(SEED.decode("utf-8"))))


def csv_bytes(names, rows):
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=names, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode()


def fake_gaia(seed, *, neighbour=False):
    ra = float(seed["ra"])
    dec = float(seed["dec"])
    row = {
        "source_id": seed["gaia"], "ra": ra, "dec": dec,
        "pmra": "0", "pmdec": "0", "parallax": "7",
        "phot_g_mean_mag": "14", "ruwe": "1.1",
        "ra_error": "0.1", "dec_error": "0.1",
    }
    data = [row]
    if neighbour:
        data.append(dict(row, source_id="341911100000000001",
                         ra=ra + 1.3/3600))
    return csv_bytes(GAIA_COLUMNS, data)


def fake_ztf(seed, *, multiple=False, positions=True):
    data = []
    ra = float(seed["ra"])
    dec = float(seed["dec"])
    for oid in (["123456789", "234567890"] if multiple else ["123456789"]):
        for i in range(6):
            data.append({
                "oid": oid, "filtercode": "zg", "mjd": 58900+i*2,
                "mag": 14 + 0.01*i, "magerr": 0.03,
                "catflags": 0,
                "ra": ra if positions else "",
                "dec": dec if positions else "",
            })
    return csv_bytes(
        ["oid","filtercode","mjd","mag","magerr","catflags","ra","dec"], data)


def assessor(seed, *, neighbour=False, multiple=False, positions=True):
    return assess_r2_target(
        seed,
        gaia_fetch=lambda ra,dec,**kw: fake_gaia(seed,neighbour=neighbour),
        ztf_fetch=lambda ra,dec,**kw: fake_ztf(
            seed,multiple=multiple,positions=positions),
    )


def test_two_realistic_synthetic_cones_still_leave_identity_unverified():
    row = assessor(ROWS[0],neighbour=True,multiple=True)
    assert row["gaia_catalogue_neighbours_status"] == "GAIA_NEIGHBOUR_SCREEN_NOT_IMAGE_VALIDATION"
    assert row["gaia_neighbours_within_2arcsec"] == 1
    assert row["ztf_positional_query_status"] == "ORIGINAL_IRSA_RESPONSE_INSPECTED"
    assert row["ztf_oid_band_groups"] == 2
    assert row["ztf_oid_band_groups_near_gaia"] == 2
    assert row["ztf_ambiguous_bands"] == ["g"]
    assert all(x["position_screen"] == "AMBIGUOUS_MULTIPLE_ZTF_OIDS_SAME_BAND"
               for x in row["ztf_candidate_oids_per_band"])
    assert all(x["physical_source_identity_confirmed"] is False
               for x in row["ztf_candidate_oids_per_band"])
    assert row["full_r2_identity_completed"] is False


def test_one_survey_oid_is_only_a_provisional_candidate():
    row = assessor(ROWS[0])
    assert row["ztf_oid_band_groups"] == 1
    assert row["ztf_ambiguous_bands"] == []
    assert row["ztf_candidate_oids_per_band"][0]["position_screen"] == "WITHIN_PROVISIONAL_2_ARCSEC_RADIUS"
    assert row["gaia_ztf_physical_identity_status"] == "PENDING_INDEPENDENT_ORIGINAL_FITS_AND_CROSSMATCH"


def test_missing_survey_object_position_is_not_interpreted_as_negative():
    row = assessor(ROWS[0],positions=False)
    assert row["ztf_positional_query_status"] == "ORIGINAL_IRSA_RESPONSE_INSPECTED"
    assert row["ztf_candidate_oids_per_band"][0]["position_screen"] == "ZTF_OBJECT_POSITION_MISSING"
    assert row["ztf_oid_band_groups_near_gaia"] == 0
    assert row["new_variable_star_confirmed"] is False


def test_gaia_service_unavailable_does_not_claim_survey_source():
    row = assess_r2_target(
        ROWS[0],
        gaia_fetch=lambda *a,**k: (_ for _ in ()).throw(OSError("offline")),
        ztf_fetch=lambda *a,**k: fake_ztf(ROWS[0]))
    assert row["gaia_catalogue_neighbours_status"] == "GAIA_QUERY_OR_PARSE_UNAVAILABLE"
    assert row["ztf_positional_query_status"] == "ORIGINAL_IRSA_RESPONSE_INSPECTED"
    assert row["ztf_candidate_oids_per_band"][0]["position_screen"] == "GAIA_TARGET_NOT_RETRIEVED"
    assert row["gaia_ztf_physical_identity_status"].startswith("PENDING")


def test_irsa_service_unavailable_cannot_be_called_nonvariable():
    row = assess_r2_target(
        ROWS[0],
        gaia_fetch=lambda *a,**k: fake_gaia(ROWS[0]),
        ztf_fetch=lambda *a,**k: (_ for _ in ()).throw(OSError("offline")))
    assert row["ztf_positional_query_status"] == "IRSA_QUERY_OR_PARSE_UNAVAILABLE"
    assert row["ztf_original_rows"] is None
    assert row["new_variable_star_confirmed"] is False


def test_gaia_only_neighbours_not_an_independent_blending_assessment():
    r = assessor(ROWS[0],neighbour=False)
    assert r["gaia_neighbours_within_2arcsec"] == 0
    assert r["full_r2_identity_completed"] is False
    assert "PENDING" in r["gaia_ztf_physical_identity_status"]


def test_exactly_24_predeclared_candidates_preserved_under_mixed_failures():
    def mixed(seed):
        k = ROWS.index(seed)
        if k % 4 == 0:
            return assess_r2_target(
                seed,
                gaia_fetch=lambda *a,**kw: (_ for _ in ()).throw(OSError("no_gaia")),
                ztf_fetch=lambda *a,**kw: fake_ztf(seed))
        if k % 4 == 1:
            return assess_r2_target(
                seed,gaia_fetch=lambda *a,**kw: fake_gaia(seed),
                ztf_fetch=lambda *a,**kw: (_ for _ in ()).throw(OSError("no_ztf")))
        return assessor(seed,multiple=k%4==2)
    result = run(SEED,assessor=mixed)
    assert result["n_frozen_technical_candidates"] == 24
    assert len(result["individual_targets"]) == 24
    assert result["n_gaia_catalogue_cones_failed_or_truncated"] == 6
    assert result["n_ztf_irsa_cones_failed_or_unparseable"] == 6
    assert result["n_sources_with_multiple_ztf_oids_in_a_band"] == 6
    assert result["n_independently_authenticated_gaia_ztf_physical_identities"] == 0
    assert result["scientifically_vetted_24_source_YSO_sample"] is False
    assert result["full_R2_complete"] is False


def test_positional_query_url_official_bounded_not_direct_object_id_lookup():
    url = ztf_positional_url(65.913324, 24.937195)
    p = urlparse(url)
    q = parse_qs(p.query)
    assert p.hostname == "irsa.ipac.caltech.edu"
    assert p.path == "/cgi-bin/ZTF/nph_light_curves"
    assert q["POS"][0].startswith("CIRCLE 65.913324")
    assert q["NOBS_MIN"] == ["5"]
    assert q["FORMAT"] == ["csv"]
    assert "ID" not in q
    with pytest.raises(ValueError):
        ztf_positional_url(65.9,24.9,radius_arcsec=15)


def test_irsa_html_or_oversize_cannot_be_promoted_to_source():
    for bad in (b"<html>500</html>", b"", b"{" + b"error": + b"}"):
        def bogus(*a,**kw):
            return bad
        row = assess_r2_target(ROWS[0],
                               gaia_fetch=lambda *a,**kw: fake_gaia(ROWS[0]),
                               ztf_fetch=bogus)
        assert row["ztf_positional_query_status"] == "IRSA_QUERY_OR_PARSE_UNAVAILABLE"
        assert row["full_r2_identity_completed"] is False


def test_aggregate_requires_all_original_preselected_targets():
    x = [assessor(ROWS[0]) for _ in range(24)]
    with pytest.raises(ValueError, match="duplicate"):
        summarise_r2_screen(x, seed_sha256="fake")
    with pytest.raises(ValueError, match="all frozen 24"):
        summarise_r2_screen(x[:23],seed_sha256="fake")
