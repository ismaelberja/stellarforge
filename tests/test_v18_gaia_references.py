"""Synthetic-only Gaia DR3 isolated reference candidate and WCS proxy tests."""
from __future__ import annotations

import csv
import io
from urllib.parse import urlparse, parse_qs
from urllib.error import HTTPError

import pytest

from stellarforge.v18_gaia_references import (
    GAIA_COLUMNS_V18, reference_adql, parse_reference_catalog,
    select_gaia_reference_candidates, retarget_same_ztf_exposure,
    screen_reference_on_exposure, estimate_provisional_wcs_translation,
)

RA, DEC = 65.913324, 24.937195
TARGET = "149623711269425408"
SCI_URL = (
    "https://irsa.ipac.caltech.edu/ibe/data/ztf/products/sci/2018/0731/"
    "489120/ztf_20180731489120_000609_zg_c08_o_q4_sciimg.fits"
    "?center=65.91332400%2C24.93719500&size=90arcsec&gzip=false"
)


def source(sid, *, east_arcsec=0.0, north_arcsec=0.0,
           g=15.3, ruwe=1.0, duplicate=False, snr=300.0,
           solved=31, pmra=2.0, pmdec=-5.0):
    import math
    return {
        "source_id": str(sid),
        "ra": RA + east_arcsec/(3600*math.cos(math.radians(DEC))),
        "dec": DEC + north_arcsec/3600,
        "pmra": pmra, "pmdec": pmdec, "parallax": 1.1,
        "phot_g_mean_mag": g,
        "phot_g_mean_flux_over_error": snr,
        "ruwe": ruwe, "duplicated_source": duplicate,
        "astrometric_params_solved": solved,
        "ra_error": 0.3, "dec_error": 0.5,
        "pmra_error": 0.15, "pmdec_error": 0.15,
    }


def catalog(**kwargs):
    rows = [
        source(TARGET, g=13.6),
        source(111111111111111111, east_arcsec=70),
        source(222222222222222222, north_arcsec=110, g=16.1),
        source(333333333333333333, east_arcsec=-100, g=17.0),
    ]
    rows.extend(kwargs.get("extras", []))
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=GAIA_COLUMNS_V18)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return out.getvalue().encode()


def test_extended_adql_uses_bounded_gaia_dr3_real_columns():
    query = reference_adql(RA, DEC)
    assert "SELECT TOP 500" in query
    assert "gaiadr3.gaia_source" in query
    assert "ruwe, duplicated_source, astrometric_params_solved" in query
    assert "CIRCLE('ICRS',65.9133240000,24.9371950000" in query


@pytest.mark.parametrize("radius", [-1, 0, 50, 241, float("nan")])
def test_adql_rejects_bad_radius(radius):
    with pytest.raises(ValueError):
        reference_adql(RA, DEC, radius_arcsec=radius)


def test_reference_csv_parses_identity_and_gaia_quality_fields():
    rows = parse_reference_catalog(catalog())
    assert len(rows) == 4
    assert rows[0]["source_id"] == TARGET
    assert rows[0]["ruwe"] == 1.0
    assert rows[1]["g_flux_snr"] == 300.0
    assert not rows[1]["duplicated_source"]


def test_tap_rejects_html_csv_missing_columns_and_duplicate_source_ids():
    with pytest.raises(ValueError):
        parse_reference_catalog(b"<html>temporary unavailable</html>")
    with pytest.raises(ValueError):
        parse_reference_catalog(b"ra,dec\n65.3,24.9\n")
    rows = catalog().decode().splitlines()
    with pytest.raises(ValueError):
        parse_reference_catalog(("\n".join(rows+[rows[1]])+"\n").encode())


def test_three_isolated_gaia_quality_candidates_are_catalogue_only():
    rows=parse_reference_catalog(catalog())
    selection=select_gaia_reference_candidates(
        rows,target_id=TARGET,target_ra_deg=RA,target_dec_deg=DEC)
    assert selection["n_candidates_selected"] == 3
    assert selection["status"] == "GAIA_DR3_QUALITY_SCREENED_REFERENCE_CANDIDATES"
    assert all(ref["catalogue_backed_only"] for ref in selection["candidates"])
    assert all(not ref["source_is_proven_single"] for ref in selection["candidates"])
    assert not selection["reference_star_psf_calibrated"]


def test_nearby_gaia_detection_blocks_apparently_good_reference():
    near=source(999999999999999999, east_arcsec=73, g=19.7)
    rows=parse_reference_catalog(catalog(extras=[near]))
    selected=select_gaia_reference_candidates(
        rows,target_id=TARGET,target_ra_deg=RA,target_dec_deg=DEC)
    selected_ids={x["source_id"] for x in selected["candidates"]}
    assert "111111111111111111" not in selected_ids
    assert selected["quality_screen_rejection_counts"]["neighbor_isolation"] >= 1


def test_high_ruwe_duplicated_and_faint_candidates_do_not_pass():
    extras=[
        source(444444444444444444,north_arcsec=-80,ruwe=8.6),
        source(555555555555555555,east_arcsec=140,duplicate=True),
        source(666666666666666666,north_arcsec=160,g=19.5),
    ]
    rows=parse_reference_catalog(catalog(extras=extras))
    out=select_gaia_reference_candidates(
        rows,target_id=TARGET,target_ra_deg=RA,target_dec_deg=DEC)
    assert out["n_candidates_selected"]==3
    assert out["quality_screen_rejection_counts"]["ruwe_or_astrometry"]==2
    assert out["quality_screen_rejection_counts"]["brightness"]==1


def test_missing_target_and_truncated_query_fail_closed():
    rows=parse_reference_catalog(catalog())
    missing=select_gaia_reference_candidates(
        rows[1:],target_id=TARGET,target_ra_deg=RA,target_dec_deg=DEC)
    assert missing["status"]=="TARGET_GAIA_DR3_NOT_VERIFIED_IN_WIDE_CONE"
    assert not missing["candidates"]
    huge=rows*125
    result=select_gaia_reference_candidates(
        huge,target_id=TARGET,target_ra_deg=RA,target_dec_deg=DEC)
    assert result["status"]=="GAIA_TAP_RESULT_TRUNCATED"
    assert not result["candidates"]


def test_reference_url_preserves_actual_ztf_exposure_path():
    url=retarget_same_ztf_exposure(SCI_URL, RA+.02, DEC-.02)
    original=urlparse(SCI_URL)
    newer=urlparse(url)
    assert original.path==newer.path
    assert parse_qs(newer.query)["center"][0] != parse_qs(original.query)["center"][0]
    assert parse_qs(newer.query)["size"]==["45arcsec"]
    assert parse_qs(newer.query)["gzip"]==["false"]


def test_reference_url_rejects_wrong_archive_and_reference_coadd():
    with pytest.raises(ValueError):
        retarget_same_ztf_exposure(SCI_URL.replace("irsa.ipac.caltech.edu",
                                                   "attacker.example"),RA,DEC)
    with pytest.raises(ValueError):
        retarget_same_ztf_exposure(
            SCI_URL.replace("/products/sci/","/products/ref/"),RA,DEC)


def mock_fit(raw, **kwargs):
    assert kwargs["image_kind"]=="science"
    return {
        "status":"PSF_PROXY_PROVISIONAL_ONLY",
        "fits_sha256":"a"*64,
        "fitted_fwhm_x_arcsec":3.1,
        "fitted_fwhm_y_arcsec":2.9,
        "fitted_axis_ratio_proxy":1.08,
        "fitted_centroid_east_minus_Gaia_arcsec":.12,
        "fitted_centroid_north_minus_Gaia_arcsec":-.04,
        "fitted_centroid_distance_from_Gaia_arcsec":.12649,
        "max_outer_positive_residual_over_noise":8,
        "fit_parameter_near_bound":False,
    }


def test_reference_image_fits_remain_unverified():
    item=select_gaia_reference_candidates(
        parse_reference_catalog(catalog()),target_id=TARGET,
        target_ra_deg=RA,target_dec_deg=DEC)["candidates"][0]
    result=screen_reference_on_exposure(
        item,exposure_url=SCI_URL,mjd=59000,
        fetch=lambda url,timeout:b"synthetic-bytes",fit=mock_fit)
    assert result["status"]=="PSF_PROXY_PROVISIONAL_ONLY"
    assert result["east_wcs_minus_gaia_arcsec"]==.12
    assert not result["astrophysical_match_confirmed"]


def test_reference_http_503_is_transport_not_missing_star():
    item=select_gaia_reference_candidates(
        parse_reference_catalog(catalog()),target_id=TARGET,
        target_ra_deg=RA,target_dec_deg=DEC)["candidates"][0]
    def fail(url,timeout):
        raise HTTPError(url,503,"archive maintenance",None,None)
    result=screen_reference_on_exposure(item,exposure_url=SCI_URL,
                                         mjd=59000,fetch=fail)
    assert result["status"]=="ZTF_REFERENCE_CUTOUT_OR_FIT_FAILED"
    assert result["http_status"]==503
    assert not result["astrophysical_match_confirmed"]


def measurement(sid, east=.1, north=.02, *, bad=False):
    return {
        "gaia_dr3_source_id":str(sid),
        "status":"PSF_PROXY_PROVISIONAL_ONLY",
        "centroid_offset_arcsec":abs(east)+abs(north),
        "fit_near_bound":bad,
        "gaussian_proxy_axis_ratio":1.1,
        "gaussian_proxy_fwhm_x_arcsec":3,
        "gaussian_proxy_fwhm_y_arcsec":3.1,
        "east_wcs_minus_gaia_arcsec":east,
        "north_wcs_minus_gaia_arcsec":north,
    }


def test_three_distinct_reference_candidates_define_only_translation_proxy():
    result=estimate_provisional_wcs_translation([
        measurement("11",.12,.01),
        measurement("22",.10,.02),
        measurement("33",.11,-.02),
    ])
    assert result["status"]=="PROVISIONAL_LOCAL_WCS_TRANSLATION_ONLY"
    assert result["n_reference_candidates_usable"]==3
    assert result["median_east_residual_arcsec"]==.11
    assert result["gaia_reference_ids_used"]==["11","22","33"]
    assert not result["independent_wcs_calibration_completed"]
    assert not result["gaia_ztf_target_identity_confirmed"]


def test_duplicate_gaia_ids_not_independent_and_bad_fit_not_used():
    rows=[
        measurement("11"), measurement("11"), measurement("22"),
        measurement("33",bad=True),
    ]
    result=estimate_provisional_wcs_translation(rows)
    assert result["status"]=="INSUFFICIENT_INDEPENDENT_IMAGE_VALIDATED_GAIA_CANDIDATES"
    assert result["n_reference_candidates_usable"]==2


def test_reference_disagreement_does_not_report_derived_translation():
    out=estimate_provisional_wcs_translation([
        measurement("11",.1,0),
        measurement("22",.2,0),
        measurement("33",1.4,0),
    ])
    assert out["status"]=="GAIA_REFERENCE_OFFSETS_DISAGREE_OVER_1_ARCSEC"
    assert not out["independent_wcs_calibration_completed"]
    assert "median_east_residual_arcsec" not in out


def test_two_references_never_count_as_independent_wcs():
    out=estimate_provisional_wcs_translation([
        measurement("11"),measurement("22"),
    ])
    assert out["status"]=="INSUFFICIENT_INDEPENDENT_IMAGE_VALIDATED_GAIA_CANDIDATES"
    assert not out["independent_wcs_calibration_completed"]
