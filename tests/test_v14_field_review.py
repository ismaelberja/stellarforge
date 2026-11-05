"""Offline v1.4 contract tests; all Gaia and IRSA rows are synthetic fixtures."""
import csv
import io
from urllib.parse import parse_qs, urlparse

import pytest

from stellarforge.v14_field_review import (
    audit_neighbours, make_gaia_adql, parse_gaia_csv,
    selected_image_links, ztf_science_cutout_url, ztf_reference_cutout_url,
)


def gaia_table():
    out = io.StringIO()
    cols = [
        "source_id", "ra", "dec", "pmra", "pmdec", "parallax",
        "phot_g_mean_mag", "ruwe", "ra_error", "dec_error",
    ]
    writer = csv.DictWriter(out, fieldnames=cols)
    writer.writeheader()
    writer.writerow({
        "source_id": "149623711269425408", "ra": "65.913324",
        "dec": "24.937195", "pmra": "7.448", "pmdec": "-21.849",
        "parallax": "7.9", "phot_g_mean_mag": "13.6",
        "ruwe": "1.05", "ra_error": "0.1", "dec_error": "0.1",
    })
    writer.writerow({
        "source_id": "99999", "ra": "65.913650",
        "dec": "24.937195", "pmra": "", "pmdec": "",
        "parallax": "", "phot_g_mean_mag": "16.3",
        "ruwe": "", "ra_error": "1.1", "dec_error": "1.2",
    })
    writer.writerow({
        "source_id": "88888", "ra": "65.915500",
        "dec": "24.937195", "pmra": "-3", "pmdec": "1",
        "parallax": "0.8", "phot_g_mean_mag": "18.0",
        "ruwe": "1.2", "ra_error": "0.2", "dec_error": "0.2",
    })
    return out.getvalue().encode()


def exposure_row(**kwargs):
    base = {
        "filefracday": "20180731489120",
        "field": "609", "filtercode": "zg",
        "ccdid": "0x8", "qid": "0x4",
        "oid": "609108400001155",
        "mjd": "58330.4891204", "catflags": "0",
    }
    base.update(kwargs)
    return base


def lightcurve_csv():
    out = io.StringIO()
    cols = list(exposure_row())
    wr = csv.DictWriter(out, fieldnames=cols)
    wr.writeheader()
    wr.writerow(exposure_row())
    wr.writerow(exposure_row(filefracday="20180803467384",
                             mjd="58333.4673843", catflags="32768"))
    wr.writerow(exposure_row(filefracday="20180804467384",
                             mjd="58334.4673843"))
    wr.writerow(exposure_row(filtercode="zr", oid="609208400001969",
                             mjd="58335.4891204"))
    return out.getvalue().encode()


def test_adql_is_bounded_to_real_cone():
    query = make_gaia_adql(65.913324, 24.937195)
    assert "SELECT TOP 200" in query
    assert "gaiadr3.gaia_source" in query
    assert "CIRCLE('ICRS',65.9133240000,24.9371950000" in query
    for bad in (-1, 0, 31, float("nan")):
        with pytest.raises(ValueError):
            make_gaia_adql(65.913324, 24.937195, bad)


def test_csv_reader_handles_nullable_values_without_inventing_pm():
    parsed = parse_gaia_csv(gaia_table())
    assert len(parsed) == 3
    assert parsed[1]["pmra"] is None
    assert parsed[0]["source_id"] == "149623711269425408"
    assert parsed[0]["phot_g_mean_mag"] == 13.6


@pytest.mark.parametrize("invalid", [
    b"<VOTABLE/>", b"error,message\nfailed,no\n",
    b"source_id,ra,dec\n1,1,2\n",
])
def test_gaia_rejects_unrecognized_reply(invalid):
    with pytest.raises(ValueError):
        parse_gaia_csv(invalid)


def test_gaia_neighbor_screen_never_declares_blending_clean():
    rows = parse_gaia_csv(gaia_table())
    d = audit_neighbours(
        rows, target_id="149623711269425408",
        ra_deg=65.913324, dec_deg=24.937195, epoch_jyear=2021.1,
    )
    assert d["target_gaia_source_verified"]
    assert d["n_other_gaia_sources_within_2_arcsec"] == 1
    assert d["n_other_gaia_sources_within_5_arcsec"] == 1
    assert d["n_other_gaia_sources_within_15_arcsec"] == 2
    assert d["nearby_sources"][0]["two_dimensional_pm_available"] is False
    assert d["nearby_sources"][0]["delta_g_neighbour_minus_target"] == 2.7
    assert not d["image_blending_ruled_out"]
    assert not d["unresolved_or_non_gaia_contaminants_excluded"]
    assert not d["target_ruwe_exceeds_1p4_quality_screen"]


def test_missing_target_does_not_mean_empty_field():
    d = audit_neighbours(
        parse_gaia_csv(gaia_table())[1:],
        target_id="149623711269425408",
        ra_deg=65.913324, dec_deg=24.937195, epoch_jyear=2021.0,
    )
    assert d["status"] == "TARGET_NOT_IN_RETURNED_GAIA_CONE"
    assert not d["image_blending_ruled_out"]


def test_ztf_science_url_expands_hex_ccd_quadrant_correctly():
    url = ztf_science_cutout_url(
        exposure_row(), ra_center=65.913324, dec_center=24.937195)
    assert "/2018/0731/489120/" in url
    assert "ztf_20180731489120_000609_zg_c08_o_q4_sciimg.fits" in url
    args = parse_qs(urlparse(url).query)
    assert args["center"] == ["65.91332400,24.93719500"]
    assert args["size"] == ["45arcsec"]
    assert args["gzip"] == ["false"]


def test_reference_url_uses_official_field_path():
    url = ztf_reference_cutout_url(
        exposure_row(), ra_center=65.913324, dec_center=24.937195)
    assert "/ref/000/field000609/zg/ccd08/q4/" in url
    assert "ztf_000609_zg_c08_q4_refimg.fits" in url
    assert "45arcsec" in url


def test_bad_ruwe_is_not_itself_proof_of_a_companion():
    rows = parse_gaia_csv(gaia_table())
    rows[0]["ruwe"] = 8.5
    out = audit_neighbours(
        rows, target_id="149623711269425408",
        ra_deg=65.913324, dec_deg=24.937195, epoch_jyear=2021.0,
    )
    assert out["target_ruwe_exceeds_1p4_quality_screen"]
    assert not out["image_blending_ruled_out"]


@pytest.mark.parametrize("row", [
    exposure_row(filefracday="../something"),
    exposure_row(filtercode="u"),
    exposure_row(ccdid="0x00"),
    exposure_row(qid="0xff"),
    exposure_row(field="../private"),
])
def test_bad_exposure_metadata_rejected(row):
    with pytest.raises(ValueError):
        ztf_science_cutout_url(row, ra_center=65.913324, dec_center=24.937195)


def test_links_keep_independent_oid_bands_and_mask_bad_data():
    result = selected_image_links(
        lightcurve_csv(), target_ra_deg=65.913324,
        target_dec_deg=24.937195, target_pmra=7.448,
        target_pmdec=-21.849)
    assert result["n_selected_cutouts"] == 2
    assert result["image_blending_verified_clean"] is False
    assert {x["band"] for x in result["image_cutouts"]} == {"zg", "zr"}
    assert all(not x["image_fits_retrieved"] for x in result["image_cutouts"])
    assert all("/products/ref/" in x["reference_cutout_url"] for x in result["image_cutouts"])


def test_all_masked_points_fail_closed():
    reader = csv.DictReader(io.StringIO(lightcurve_csv().decode()))
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=reader.fieldnames)
    writer.writeheader()
    for row in reader:
        row["catflags"] = "32768"
        writer.writerow(row)
    with pytest.raises(ValueError):
        selected_image_links(output.getvalue().encode(),
                             target_ra_deg=65.913324, target_dec_deg=24.937195,
                             target_pmra=7.448, target_pmdec=-21.849)
