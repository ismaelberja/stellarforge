"""Synthetic and controlled-ephemeris Gaia 5p parallax/covariance tests."""
from __future__ import annotations

import csv
import io
import math
import numpy as np
import pytest

from stellarforge.v19_gaia_covariance import (
    GAIA_COLUMNS, GAIA_CORRELATIONS, GAIA_ERRORS,
    make_target_astrometry_adql, parse_gaia_astrometry,
    five_parameter_gaia_covariance, geocentric_parallax_direction,
    earth_barycentric_au, propagate_gaia_5p_formal,
    _tangent_delta_mas,
)

FT = "149623711269425408"
CIDA = "3419110734340795648"


def row(sid=FT, *, ruwe=1.15, dec=25., plx=7.2, ra=66.,
        pmra=8., pmdec=-22., error=.1):
    result = {
        "source_id": sid, "ref_epoch": 2016.0,
        "ra": ra, "dec": dec,
        "pmra": pmra, "pmdec": pmdec, "parallax": plx,
        "ruwe": ruwe, "astrometric_params_solved": 31,
    }
    result.update({k:error for k in GAIA_ERRORS})
    result.update({k:0.0 for k in GAIA_CORRELATIONS})
    return result


def csv_rows(*rows):
    text = io.StringIO()
    writer = csv.DictWriter(text,fieldnames=GAIA_COLUMNS)
    writer.writeheader()
    for x in rows:
        writer.writerow(x)
    return text.getvalue().encode("utf-8")


def test_exact_source_adql_with_real_gaia_covariance_columns():
    adql=make_target_astrometry_adql((FT,CIDA))
    assert "FROM gaiadr3.gaia_source" in adql
    assert f"source_id IN ({FT}, {CIDA})" in adql
    assert all(name in adql for name in GAIA_COLUMNS)


@pytest.mark.parametrize("ids", [(),(FT,FT),("1",),tuple([FT]*13)])
def test_query_rejects_bad_gaia_id_inventory(ids):
    with pytest.raises(ValueError):
        make_target_astrometry_adql(ids)


def test_complete_gaia_csv_requires_exact_id_and_full_covariance_columns():
    parsed = parse_gaia_astrometry(csv_rows(row(),row(CIDA)),expected_ids=(FT,CIDA))
    assert set(parsed)=={FT,CIDA}
    assert parsed[FT]["ref_epoch"] == 2016.0
    with pytest.raises(ValueError):
        parse_gaia_astrometry(csv_rows(row()),expected_ids=(FT,CIDA))
    with pytest.raises(ValueError):
        parse_gaia_astrometry(b"<html>Gaia error</html>",expected_ids=(FT,))
    with pytest.raises(ValueError):
        parse_gaia_astrometry(b"source_id,ra\n1,2\n",expected_ids=(FT,))


def test_parser_rejects_duplicate_or_unexpected_gaia_id():
    with pytest.raises(ValueError):
        parse_gaia_astrometry(csv_rows(row(),row()),expected_ids=(FT,))
    with pytest.raises(ValueError):
        parse_gaia_astrometry(csv_rows(row(CIDA)),expected_ids=(FT,))


def test_five_dimensional_gaia_covariance_includes_all_cross_terms():
    original=row(error=.2)
    original["ra_pmra_corr"]=.5
    original["dec_parallax_corr"]=-.25
    cov=five_parameter_gaia_covariance(original)
    assert cov.shape==(5,5)
    assert np.allclose(cov,cov.T)
    assert cov[0,3] == pytest.approx(.02)
    assert cov[1,2] == pytest.approx(-.01)
    assert np.linalg.eigvalsh(cov).min()>0


@pytest.mark.parametrize("missing", ["ra_error","parallax_error","ra_dec_corr",
                                      "parallax_pmra_corr","pmra_pmdec_corr"])
def test_missing_covariance_fails_closed(missing):
    g=row()
    del g[missing]
    with pytest.raises(ValueError):
        five_parameter_gaia_covariance(g)


def test_invalid_astrometric_solution_or_epoch_cannot_yield_formal_error():
    g=row()
    g["astrometric_params_solved"]=3
    with pytest.raises(ValueError):
        five_parameter_gaia_covariance(g)
    g=row()
    g["ref_epoch"]=2015.5
    with pytest.raises(ValueError):
        five_parameter_gaia_covariance(g)


def test_indefinite_gaia_correlation_matrix_rejected():
    g=row()
    g["ra_dec_corr"]=.99
    g["ra_parallax_corr"]=.99
    g["dec_parallax_corr"]=-.99
    with pytest.raises(ValueError,match="non-positive"):
        five_parameter_gaia_covariance(g)


def test_annual_parallax_projection_has_correct_sign_and_amplitude():
    # At RA=90deg, Dec=0, Earth at +X AU, the apparent source moves EAST.
    ra,dec=geocentric_parallax_direction(
        90,0,10,0,0,2016.0,[1,0,0])
    east,north=_tangent_delta_mas(ra,dec,90,0)
    assert east == pytest.approx(10,abs=.0001)
    assert north == pytest.approx(0,abs=.0001)


def test_zero_parallax_reduces_to_legacy_linear_motion():
    from stellarforge.association import propagate_gaia_position
    ra,dec=geocentric_parallax_direction(
        66,25,0,10,-20,2019.3,[0,1,0])
    legacy=propagate_gaia_position(66,25,10,-20,2019.3)
    dx,dy=_tangent_delta_mas(ra,dec,*legacy)
    assert abs(dx)<.0001 and abs(dy)<.0001


def test_earth_builtin_ephemeris_is_finite_and_near_one_au():
    vec,epoch=earth_barycentric_au(58491.184780)
    assert vec.shape==(3,)
    assert np.linalg.norm(vec)==pytest.approx(1,abs=.03)
    assert 2018<epoch<2020


def test_full_covariance_result_is_formal_and_not_instrument_wcs():
    fit=propagate_gaia_5p_formal(row(),mjd_utc=58491.184780)
    assert fit["status"]=="FORMAL_COVARIANCE_MODEL_NOT_INSTRUMENT_CALIBRATION"
    assert fit["annual_geocentric_parallax_included"]
    assert fit["full_gaia_five_parameter_formal_covariance_propagated"]
    assert fit["formal_gaia_east_sigma_mas"]>0
    assert fit["formal_gaia_north_sigma_mas"]>0
    assert abs(fit["geocentric_annual_parallax_minus_linear_east_mas"])<8.0
    assert not fit["ztf_instrument_wcs_psf_error_budget_included"]
    assert not fit["gaia_ztf_astrophysical_source_identity_confirmed"]


def test_formal_uncertainty_grows_with_proper_motion_epoch_distance():
    base=row(error=.3,pmra=12,pmdec=-7)
    near=propagate_gaia_5p_formal(base,mjd_utc=57388.0)
    far=propagate_gaia_5p_formal(base,mjd_utc=60900.0)
    assert far["formal_gaia_east_sigma_mas"] > near["formal_gaia_east_sigma_mas"]
    assert far["formal_gaia_north_sigma_mas"] > near["formal_gaia_north_sigma_mas"]


def test_cida_high_ruwe_retains_model_but_warns_not_total_uncertainty():
    fit=propagate_gaia_5p_formal(
        row(CIDA,ruwe=8.56752),mjd_utc=58849.135984)
    assert fit["status"]=="FORMAL_COVARIANCE_MODEL_WITH_ASTROMETRIC_QUALITY_WARNING"
    assert fit["high_or_missing_ruwe_quality_warning"]
    assert fit["non_single_star_systematics_in_covariance"] is False
    assert not fit["gaia_ztf_astrophysical_source_identity_confirmed"]


def test_invalid_epoch_and_earth_vector_rejected():
    with pytest.raises(ValueError):
        earth_barycentric_au(float("nan"))
    with pytest.raises(ValueError):
        geocentric_parallax_direction(66,25,7,8,9,2019,[1,float("inf"),0])
    with pytest.raises(ValueError):
        geocentric_parallax_direction(66,25,7,8,9,2019,[0,0,0])
