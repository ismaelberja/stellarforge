"""All inputs in this test module are SYNTHETIC engineering fixtures.
They are NOT observations of Taurus or ZTF survey source positions.
"""
import csv
import hashlib
import io
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
from stellarforge.ztf import build_ztf_url
from stellarforge.ztf_photometry import (parse_ztf_table, inspect_ztf_bytes,
                                         audit_ztf_file)

HEAD = ["oid", "fid", "mjd", "mag", "magerr", "catflags", "ra", "dec"]


def lines(items, columns=HEAD):
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=columns)
    writer.writeheader()
    writer.writerows(items)
    return stream.getvalue().encode()


def row(**kwargs):
    return dict(oid="10000000000000001", fid="1", mjd="58310.25", mag="17.2",
                magerr="0.02", catflags="0", ra="65.0", dec="25.0", **kwargs)


def mk(**kwargs):
    a = row()
    a.update(kwargs)
    return a


def test_parses_csv_preserves_large_oid_and_filter():
    observations, fmt = parse_ztf_table(lines([row()]))
    assert fmt == "csv"
    report, good = inspect_ztf_bytes(lines([row()]), target_ra=65, target_dec=25, min_good_epochs=1)
    assert good[0].oid == "10000000000000001"
    assert good[0].band == "g"
    assert good[0].time_scale == "MJD"
    assert report["curves"][0]["status"] == "provisional_for_review"
    assert report["scientific_membership_verified"] is False


def test_group_oid_band_and_flag_dedup():
    payload = lines([mk(), mk(mjd="58311", fid="2"),
                     mk(mjd="58312", oid="3"), mk(mjd="58313", catflags="32768"),
                     mk(), mk(mjd="58314", catflags="2")])
    report, good = inspect_ztf_bytes(payload, target_ra=65, target_dec=25, min_good_epochs=1)
    assert report["raw_rows"] == 6
    assert report["kept_rows"] == 4
    assert report["rejected_reasons"] == {"duplicate_epoch": 1, "masked_catflags": 1}
    assert {(p.oid, p.band) for p in good} == {("10000000000000001", "g"),
                                               ("10000000000000001", "r"), ("3", "g")}
    assert report["ambiguous_match_bands"] == ["g"]
    assert all(c["status"] == "ambiguous_multiple_oids" for c in report["curves"] if c["band"] == "g")


def test_rejects_bad_uncertainties_but_keeps_possible_dips():
    payload = lines([mk(), mk(mjd="58312", mag="19.4"),
                     mk(mjd="58313", magerr="-0.01"), mk(mjd="58314", mag="nan")])
    report, good = inspect_ztf_bytes(payload, min_good_epochs=1)
    assert len(good) == 2
    assert max(p.magnitude for p in good) == 19.4
    assert report["rejected_reasons"]["invalid_magnitude_error"] == 1
    assert report["rejected_reasons"]["invalid_photometry"] == 1
    assert report["curves"][0]["robust_amp_p95_p05_mag"] == pytest.approx(1.98)


def test_mask_is_bitwise_not_equal():
    report, good = inspect_ztf_bytes(lines([mk(catflags="32770")]), min_good_epochs=1)
    assert not good
    assert report["rejected_reasons"] == {"masked_catflags": 1}


def test_mask_can_be_configured():
    report, good = inspect_ztf_bytes(lines([mk(catflags="2")]), catflags_mask=2)
    assert len(good) == 0


@pytest.mark.parametrize("bad,reason", [
    ({"oid": "1.2"}, "invalid_oid"), ({"fid": "x"}, "unknown_filter"),
    ({"mjd": ""}, "missing_or_ambiguous_time_column"),
    ({"mjd": "inf"}, "invalid_photometry"),
    ({"mjd": "12.5"}, "invalid_epoch_range"),
    ({"mag": "-200"}, "invalid_magnitude_range"),
    ({"magerr": "0"}, "invalid_magnitude_error"),
    ({"catflags": "-1"}, "invalid_catflags"),
    ({"ra": "not-ra"}, "invalid_position"),
    ({"dec": "91"}, "invalid_position"),
])
def test_invalid_rows_audited(bad, reason):
    a = mk(**bad)
    stats, good = inspect_ztf_bytes(lines([a]), min_good_epochs=1)
    assert not good
    assert stats["rejected_reasons"][reason] == 1


def test_null_position_is_explicitly_unverified():
    stats, good = inspect_ztf_bytes(lines([mk(ra="null", dec="null")]),
                                    target_ra=65, target_dec=25, min_good_epochs=1)
    assert len(good) == 1
    assert stats["curves"][0]["position_status"] == "position_unverified"


def test_outside_radius_not_provisionally_approved():
    stats, good = inspect_ztf_bytes(lines([mk(ra="65.01", dec="25")]),
                                    target_ra=65, target_dec=25, min_good_epochs=1)
    assert stats["curves"][0]["position_status"] == "outside_provisional_radius"
    assert stats["curves"][0]["status"] == "needs_review"


def test_ra_0_wraparound():
    stats, _ = inspect_ztf_bytes(lines([mk(ra="359.9999", dec="25")]),
                                 target_ra=0, target_dec=25, radius_arcsec=1,
                                 min_good_epochs=1)
    assert stats["curves"][0]["position_status"] == "inside_provisional_radius"


def test_distinguishes_mjd_hmjd_and_hjd():
    cols = ["oid", "fid", "mjd", "hjd", "mag", "magerr", "catflags", "ra", "dec"]
    data = [{**mk(), "hjd": ""}, {**mk(oid="2", mjd=""), "hjd": "2458310.25"}]
    stats, points = inspect_ztf_bytes(lines(data, cols), min_good_epochs=1)
    assert len(points) == 2
    assert {p.time_scale for p in points} == {"MJD", "HJD"}
    assert len(stats["curves"]) == 2


def test_accepts_consistent_parallel_real_ztf_clocks_without_conversion():
    cols = ["oid", "fid", "mjd", "hjd", "mag", "magerr", "catflags", "ra", "dec"]
    data = [{**mk(), "hjd": "2458310.7542"}]
    stats, points = inspect_ztf_bytes(lines(data, cols))
    assert len(points) == 1
    assert points[0].time_scale == "MJD"
    assert points[0].time_value == 58310.25
    assert stats["raw_rows_with_multiple_time_columns"] == 1


def test_rejects_inconsistent_parallel_clocks():
    cols = ["oid", "fid", "mjd", "hjd", "mag", "magerr", "catflags", "ra", "dec"]
    stats, points = inspect_ztf_bytes(lines([{**mk(), "hjd": "2458000.25"}], cols))
    assert not points
    assert stats["rejected_reasons"] == {"inconsistent_time_columns": 1}


def test_accepts_hmjd_with_hjd_and_prefers_hmjd_when_mjd_missing():
    cols = ["oid", "fid", "hmjd", "hjd", "mag", "magerr", "catflags", "ra", "dec"]
    record = {k: v for k,v in mk().items() if k != "mjd"}
    record.update(hmjd="58310.251", hjd="2458310.751")
    stats, points = inspect_ztf_bytes(lines([record], cols))
    assert len(points) == 1
    assert points[0].time_scale == "HMJD"


def test_ipac_fixed_width_parsing():
    cols = ["oid", "fid", "mjd", "mag", "magerr", "catflags", "ra", "dec"]
    vals = ["12345678901234567", "2", "58310.25", "16.45", "0.011", "0", "65", "25"]
    widths = [max(20, len(c) + 2) for c in cols]
    header = "|" + "|".join(c.center(w) for c, w in zip(cols, widths)) + "|"
    types = "|" + "|".join("char".center(w) for w in widths) + "|"
    data = " " + " ".join(v.center(w) for v, w in zip(vals, widths)) + " "
    raw = ("\\identifier = SYNTHETIC\n" + header + "\n" + types + "\n" + data + "\n").encode()
    parsed, fmt = parse_ztf_table(raw)
    assert fmt == "ipac_table"
    assert parsed[0]["oid"] == vals[0]
    stats, pts = inspect_ztf_bytes(raw, target_ra=65, target_dec=25, min_good_epochs=1)
    assert len(pts) == 1
    assert pts[0].band == "r"


def test_bad_layout_rejected():
    with pytest.raises(ValueError):
        parse_ztf_table(b"garbage output, not a real header\n")
    with pytest.raises(ValueError):
        parse_ztf_table(b"<html>server error</html>")
    with pytest.raises(ValueError):
        parse_ztf_table(b"")


def test_missing_required_fields_raise():
    with pytest.raises(ValueError, match="Missing ZTF required columns"):
        inspect_ztf_bytes(b"oid,mjd,mag\n1,58300,16\n")


def test_reject_bad_csv_field_count():
    with pytest.raises(ValueError, match="Extra data cells"):
        parse_ztf_table(b"oid,mag\n1,2,3")


def test_empty_table_is_not_valid_curve():
    stats, pts = inspect_ztf_bytes(lines([]))
    assert stats["status"] == "no_observations"
    assert not pts


def test_insufficient_epochs_recorded_without_fabricated_variability():
    stats, _ = inspect_ztf_bytes(lines([mk()]), target_ra=65, target_dec=25, min_good_epochs=30)
    assert stats["curves"][0]["good_epochs"] == 1
    assert stats["curves"][0]["sufficient_epochs"] is False


def test_provenance_sha_matches_and_file_writes(tmp_path):
    raw = lines([mk()])
    file = tmp_path / "raw.csv"
    file.write_bytes(raw)
    sidecar = Path(str(file) + ".provenance.json")
    url = build_ztf_url(65, 25, output_format="csv")
    sidecar.write_text(json.dumps({"sha256": hashlib.sha256(raw).hexdigest(), "url": url}))
    dest = tmp_path / "normalized"
    result = audit_ztf_file(file, dest, target_ra=65, target_dec=25,
                            min_good_epochs=1)
    assert result["provenance"]["sidecar_points_to_irsa"]
    assert (dest / "photometry_good.csv").is_file()
    assert json.loads((dest / "ztf_audit.json").read_text())["raw_rows"] == 1


def test_provenance_sha_tampering_blocks_processing(tmp_path):
    file = tmp_path / "raw.csv"
    file.write_bytes(lines([mk()]))
    Path(str(file) + ".provenance.json").write_text(json.dumps({"sha256": "0" * 64}))
    with pytest.raises(ValueError, match="changed"):
        audit_ztf_file(file, tmp_path / "output")


def test_missing_provenance_does_not_claim_irsa(tmp_path):
    file = tmp_path / "manual.csv"
    file.write_bytes(lines([mk()]))
    result = audit_ztf_file(file, tmp_path / "out")
    assert result["provenance"]["sidecar_points_to_irsa"] is False


def test_query_can_request_csv_without_changing_legacy_default():
    params = parse_qs(urlsplit(build_ztf_url(65, 25, output_format="csv")).query)
    assert params["FORMAT"] == ["csv"]
    with pytest.raises(ValueError):
        build_ztf_url(65, 25, output_format="fits")


def test_no_assumptions_about_taurus_membership():
    stats, _ = inspect_ztf_bytes(lines([mk()]), target_ra=65, target_dec=25, min_good_epochs=1)
    assert not stats["scientific_membership_verified"]
    assert "Taurus" not in json.dumps(stats)