from dataclasses import replace
import pytest
from stellarforge.chromaticity import match_g_r_points
from stellarforge.ztf_photometry import PhotometricPoint


def pt(oid,band,t,mag,err=.05,row=1,scale='MJD',flags=0):
    return PhotometricPoint(oid,band,t,scale,mag,err,flags,row)


def test_pair_color_error_propagation():
    v=match_g_r_points([pt('11','g',59000.,15,.3),pt('22','r',59000.1,14,.4)],g_oid='11',r_oid='22')
    assert v['paired_epochs']==1
    assert v['pairs'][0]['color_g_minus_r_mag']==1.
    assert v['pairs'][0]['color_uncertainty_mag']==pytest.approx(.5)
    assert v['independently_confirmed_same_astrophysical_source'] is False
    assert v['extinction_or_accretion_classification'] is None


def test_one_to_one_no_photometry_reuse():
    v=match_g_r_points([pt('11','g',59000.,15),pt('11','g',59000.05,15,row=2),pt('22','r',59000.02,14)],g_oid='11',r_oid='22')
    assert v['paired_epochs']==1
    assert v['unpaired_g_epochs']==1


def test_absent_band_does_not_infer_color():
    v=match_g_r_points([pt('11','g',59000,15)],g_oid='11',r_oid='22')
    assert v['paired_epochs']==0
    assert v['median_g_minus_r_mag'] is None


def test_nonoverlapping_epochs_no_interpolation():
    v=match_g_r_points([pt('11','g',59000,15),pt('22','r',59005,14)],g_oid='11',r_oid='22')
    assert v['paired_epochs']==0


def test_reject_mixed_time_scales():
    with pytest.raises(ValueError,match='Mixed time'):
        match_g_r_points([pt('11','g',59000,15),pt('22','r',59000,14,scale='HJD')],g_oid='11',r_oid='22')


def test_reject_ambiguous_oid():
    with pytest.raises(ValueError,match='distinct'):
        match_g_r_points([],g_oid='11',r_oid='11')


def test_reject_unsafe_photometry():
    with pytest.raises(ValueError,match='flagged'):
        match_g_r_points([pt('11','g',59000,15,flags=32768)],g_oid='11',r_oid='22')


def test_refuse_oid_band_collision():
    with pytest.raises(ValueError,match='conflict'):
        match_g_r_points([pt('11','r',59000,15)],g_oid='11',r_oid='22')


def test_global_nearest_priority():
    v=match_g_r_points([pt('11','g',59000,15),pt('11','g',59000.2,15,row=2),
                        pt('22','r',59000.15,14)],g_oid='11',r_oid='22')
    assert v['pairs'][0]['g_mjd']==59000.2


def test_bound_on_time_gap():
    with pytest.raises(ValueError,match='max_gap'):
        match_g_r_points([],g_oid='11',r_oid='22',max_gap_days=3)