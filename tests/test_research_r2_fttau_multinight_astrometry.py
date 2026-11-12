"""Falsification tests: blind date selection and no astrophysical overclaims."""
from __future__ import annotations

import pytest

from stellarforge.r2_fttau_multinight_astrometry import (
    MIN_SEPARATION_DAYS, select_earliest_latest_independent_nights,
    summarize_original_epoch_pair, inspect_preselected_original_epoch,
)


def anchor():
    return {
        "band": "g", "ztf_oid": "1605115300003377",
        "original_field_ccd_quadrant": [1605, 15, 3],
        "original_filefracday": "20191119000000",
    }


def row(day, key, *, band="g", oid="1605115300003377"):
    return {
        "mjd": day, "filefracday": key, "band": band, "oid": oid,
        "field": "1605", "ccdid": "15", "qid": "3",
        "filtercode": "zg",
    }


def test_earliest_latest_uses_distinct_utc_nights_not_best_offsets():
    original = [
        row(58806.38, "20191119000000"),  # historical anchor omitted
        row(58701.3, "20190806000001"),
        row(58701.2, "20190806000000"),  # earlier SAME night
        row(58740.1, "20190914000000"),
        row(58910.2, "20200302000000"),
    ]
    result = select_earliest_latest_independent_nights(original, anchor())
    assert result["status"] == "TWO_INDEPENDENT_NIGHTS_PRESELECTED"
    assert result["n_eligible_nonanchor_exposures"] == 4
    assert result["n_distinct_nonanchor_utc_nights"] == 3
    selected = result["selected_rows_ephemeral"]
    assert [x["filefracday"] for x in selected] == [
        "20190806000000", "20200302000000"]
    assert selected[0]["mjd"] == 58701.2
    assert selected[1]["mjd"] == 58910.2
    assert result["original_four_exposure_anchor_excluded"]


def test_underpowered_does_not_replace_or_invent_nights():
    result = select_earliest_latest_independent_nights([
        row(58701.2, "20190806000000"),
        row(58707.3, "20190812000000")], anchor())
    assert MIN_SEPARATION_DAYS == 30
    assert result["status"] == "UNDERPOWERED_NONANCHOR_INDEPENDENT_NIGHTS"
    assert result["selected_rows_ephemeral"] == []


def test_same_night_twice_is_one_night_and_no_pair():
    result = select_earliest_latest_independent_nights([
        row(58701.01, "20190806000000"),
        row(58701.45, "20190806100000")], anchor())
    assert result["n_distinct_nonanchor_utc_nights"] == 1
    assert result["selected_rows_ephemeral"] == []


def test_malformed_oid_or_field_is_hard_error():
    with pytest.raises(ValueError):
        select_earliest_latest_independent_nights([
            row(58701.2, "20190806000000", oid="1234567890123")], anchor())
    with pytest.raises(ValueError):
        select_earliest_latest_independent_nights([
            row(58701.2, "20190806000000", band="r")], anchor())


def test_no_rows_is_explicitly_underpowered():
    result = select_earliest_latest_independent_nights([], anchor())
    assert result["status"] == "UNDERPOWERED_NONANCHOR_INDEPENDENT_NIGHTS"
    assert result["n_distinct_nonanchor_utc_nights"] == 0


def test_good_two_epochs_are_descriptive_only():
    a = {"status": "ORIGINAL_ZTF_NATIVE_PSF_SOURCE_SCREEN_COMPLETE",
         "native_source_candidate": {
             "status": "PROVISIONAL_GAIA_NEAREST_ZTF_PSF_SOURCE_GEOMETRY_PASS",
             "original_native_minus_propagated_gaia_east_arcsec": .012,
             "original_native_minus_propagated_gaia_north_arcsec": .045}}
    b = {"status": "ORIGINAL_ZTF_NATIVE_PSF_SOURCE_SCREEN_COMPLETE",
         "native_source_candidate": {
             "status": "PROVISIONAL_GAIA_NEAREST_ZTF_PSF_SOURCE_GEOMETRY_PASS",
             "original_native_minus_propagated_gaia_east_arcsec": -.009,
             "original_native_minus_propagated_gaia_north_arcsec": .015}}
    out = summarize_original_epoch_pair(a, b, 41)
    assert out["status"] == "TWO_PROVISIONAL_SOURCE_POSITIONS_NOT_PHYSICAL_ID"
    assert out["late_minus_early_native_minus_gaia_east_arcsec"] == -.021
    assert out["late_minus_early_native_minus_gaia_north_arcsec"] == -.03
    assert out["independent_astrophysical_proper_motion_detected"] is False
    assert out["confirmed_physical_gaia_ztf_target"] is False


def test_quality_failure_forces_unresolved_no_difference():
    early = {"status": "ORIGINAL_ZTF_NATIVE_PSF_SOURCE_SCREEN_COMPLETE",
             "native_source_candidate": {"status": "TARGET_PSF_SOURCE_AMBIGUOUS_OR_QUALITY_REVIEW"}}
    late = {"status": "ORIGINAL_ZTF_NATIVE_PSF_SOURCE_SCREEN_COMPLETE",
            "native_source_candidate": {
                "status": "PROVISIONAL_GAIA_NEAREST_ZTF_PSF_SOURCE_GEOMETRY_PASS"}}
    out = summarize_original_epoch_pair(early, late, 100)
    assert out["status"].startswith("UNRESOLVED")
    assert out["late_minus_early_native_minus_gaia_east_arcsec"] is None


def test_inspection_does_not_expose_raw_catalogue_rows(monkeypatch):
    from stellarforge import r2_fttau_multinight_astrometry as mod
    original_url = "https://irsa.ipac.caltech.edu/ibe/data/ztf/products/sci/test_sciimg.fits"
    monkeypatch.setattr(mod, "ztf_science_cutout_url", lambda *args, **kw: original_url)
    monkeypatch.setattr(mod, "official_psf_product_url",
                        lambda *args, **kw: "https://irsa.ipac.caltech.edu/source_psfcat.fits")
    raw = b"FAKE FITS"
    import hashlib
    seen = []
    def fake_fetch(url, *, kind, timeout):
        seen.append(kind)
        return raw
    def fake_parser(original):
        return {"sha256": hashlib.sha256(original).hexdigest(),
                "n_native_psf_catalogue_rows": 3, "rows": {"secret": "not persisted"}}
    def fake_screen(parsed, pred):
        assert parsed["rows"] == {"secret": "not persisted"}
        return {"status": "TARGET_PSF_SOURCE_AMBIGUOUS_OR_QUALITY_REVIEW",
                "confirmed_physical_gaia_ztf_target": False}
    result = inspect_preselected_original_epoch(
        row(58910.2, "20200302000000"), {"fake": "gaia"}, ra_center=1, dec_center=1,
        native_fetch=fake_fetch, native_parse=fake_parser,
        gaia_propagate=lambda gaia, mjd_utc: {"mjd": mjd_utc},
        source_screen=fake_screen)
    assert seen == ["psfcat.fits"]
    assert result["status"] == "ORIGINAL_ZTF_NATIVE_PSF_SOURCE_SCREEN_COMPLETE"
    assert "rows" not in result and "secret" not in str(result)
    assert result["n_original_native_psf_catalogue_rows"] == 3
    assert result["confirmed_physical_gaia_ztf_target"] is False
