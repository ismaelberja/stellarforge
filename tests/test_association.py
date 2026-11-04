"""Tests protect the *conservative* source association policy."""
import math
import pytest
from stellarforge.association import (propagate_gaia_position,screen_ztf_positional_candidates,
                                       mjd_to_approximate_julian_year)
from stellarforge.coordinates import angular_separation_arcsec


def test_propagation_zero_motion_and_ra_wrap():
    assert propagate_gaia_position(359.9999,15,0,0,2020)==pytest.approx((359.9999,15),abs=1e-10)
    ra,dec=propagate_gaia_position(359.9999,0,250,0,2026)
    assert ra<0.001 and abs(dec)<1e-5


def test_ra_star_pm_at_high_declination():
    ra,dec=propagate_gaia_position(120,60,360,0,2026)
    assert angular_separation_arcsec(120,60,ra,dec)==pytest.approx(3.6,abs=0.002)
    assert ra>120 and dec<60


def test_pm_validation():
    for kwargs in ({'to_julian_year': float('nan')},{'to_julian_year':2100},
                   {'pmra_star_mas_yr':1e5}):
        params=dict(ra_deg=30,dec_deg=10,pmra_star_mas_yr=5,pmdec_mas_yr=5,to_julian_year=2025)
        params.update(kwargs)
        with pytest.raises(ValueError):propagate_gaia_position(**params)


def test_year_conversion():
    assert mjd_to_approximate_julian_year(51544.5)==pytest.approx(2000)
    with pytest.raises(ValueError):mjd_to_approximate_julian_year(1e9)


def sample(ra=65,dec=24):
    return dict(gaia_id='162541942104406784',ra_deg=ra,dec_deg=dec,
                pmra_star_mas_yr=11,pmdec_mas_yr=-20,
                ztf_epoch_year=2021,position_reference='Gaia',radius_arcsec=2)


def source(oid='1234567',band='r',ra=65,dec=24,n=70):
    return dict(oid=oid,band=band,ra_deg=ra,dec_deg=dec,n_good_epochs=n)


def test_unique_is_never_confirmed():
    v=screen_ztf_positional_candidates(**sample(),ztf_sources=[source()])
    assert v['status']=='positional_candidates_require_independent_review'
    assert v['provisional_oid']=={'r':'1234567'}
    assert not v['astrometric_match_verified']


def test_same_band_multiple_ambiguous():
    v=screen_ztf_positional_candidates(**sample(),ztf_sources=[source(),source('2468',ra=65.0001)])
    assert v['status']=='ambiguous_multiple_oids_same_band'
    assert v['provisional_oid'] is None


def test_two_bands_not_automatically_confirmed():
    v=screen_ztf_positional_candidates(**sample(),ztf_sources=[source('121',band='r'),source('131',band='g')])
    assert not v['astrometric_match_verified']
    assert v['status']=='positional_candidates_require_independent_review'


def test_non_gaia_reference_is_unresolved():
    v=screen_ztf_positional_candidates(**{**sample(),'position_reference':'UKIDSS'},ztf_sources=[source()])
    assert v['status']=='insufficient_epoch_information'
    assert not v['candidates']


def test_no_hit_and_missing_obs():
    assert screen_ztf_positional_candidates(**sample(),ztf_sources=[source(ra=68)])['status']=='no_positional_candidate'
    assert screen_ztf_positional_candidates(**sample(),ztf_sources=[source(n=0)])['status']=='position_hit_without_usable_photometry'


def test_bad_source_rejected():
    with pytest.raises(ValueError):screen_ztf_positional_candidates(**sample(),ztf_sources=[source(),source()])
    with pytest.raises(ValueError):screen_ztf_positional_candidates(**sample(),ztf_sources=[source(band='u')])