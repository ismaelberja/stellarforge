"""Synthetic astrometric tests, NOT measured Taurus/ZTF counterpart validation."""
import math
import pytest

from stellarforge.association import propagate_gaia_position
from stellarforge.epoch_evidence import per_epoch_association_evidence
from stellarforge.ztf_photometry import PhotometricPoint

GAIA = '149623711269425408'


def point(oid='100', band='g', mjd=59000, ra=65.913324, dec=24.937195, time_scale='MJD'):
    return PhotometricPoint(str(oid), band, mjd, time_scale, 13.5, 0.03, 0, 2, ra, dec)


def run(points, **overrides):
    config = dict(gaia_id=GAIA, ra_deg=65.913324, dec_deg=24.937195,
                  pmra_star_mas_yr=7.448, pmdec_mas_yr=-21.849, radius_arcsec=2,
                  min_positioned_epochs=2)
    config.update(overrides)
    return per_epoch_association_evidence(points, **config)


def test_empty_not_discovery():
    report = run([])
    assert report['n_curves'] == 0
    assert report['status'] == 'no_good_photometry'
    assert report['astrometric_identity_confirmed'] is False


def test_taurus_in_radius_with_sparse_points():
    result = run([point(mjd=x) for x in (59000, 59001, 59002)])
    assert result['status'] == 'possible_counterparts_require_independent_review'
    assert result['n_provisionally_in_radius'] == 1
    assert result['curves'][0]['n_positioned_mjd_epochs'] == 3
    assert result['curves'][0]['p95_epoch_corrected_separation_arcsec'] < 0.2


def test_missing_positions_yields_hold():
    p = point()
    p = PhotometricPoint(p.oid,p.band,p.time_value,p.time_scale,p.magnitude,p.magnitude_error,p.catflags,p.row_number)
    result = run([p,p])
    assert result['status'] == 'no_sufficient_epoch_positions'
    assert result['curves'][0]['status'] == 'insufficient_epoch_positions'


def test_no_motion_requires_review():
    result = run([point(mjd=x) for x in (59000,59001,59002)],pmra_star_mas_yr=None)
    assert result['status'] == 'missing_Gaia_epoch_propagation'
    assert result['curves'][0]['status'] == 'no_reliable_Gaia_epoch_propagation'
    assert result['curves'][0]['median_epoch_corrected_separation_arcsec'] is None


def test_outside_all_epochs():
    result = run([point(mjd=x,ra=65.94) for x in (59000,59001,59002)])
    assert result['status'] == 'all_positioned_curves_outside_radius'
    assert result['n_provisionally_in_radius']==0


def test_mixed_epochs_not_provisional():
    result=run([point(mjd=59000),point(mjd=59001,ra=65.94)])
    assert result['status']=='variable_angular_separation_requires_review'
    assert result['curves'][0]['fraction_epochs_inside_radius']==.5


def test_two_OIDs_same_band_are_ambiguous():
    result=run([point(oid=i,mjd=t) for i in ('101','102') for t in (59000,59001,59002)])
    assert result['status']=='ambiguous_multiple_oids_same_band'
    assert result['ambiguous_bands']==['g']


def test_two_bands_stay_separate():
    result=run([point(oid='101',band='g',mjd=t) for t in (59000,59001)]
               +[point(oid='102',band='r',mjd=t) for t in (59000,59001)])
    assert len(result['curves'])==2
    assert result['ambiguous_bands']==[]
    assert result['astrometric_identity_confirmed'] is False


def test_clock_not_mjd_no_fake_conversion():
    result=run([point(mjd=x,time_scale='HJD') for x in (2459000,2459001)])
    assert result['status']=='no_sufficient_epoch_positions'
    assert result['curves'][0]['n_positioned_mjd_epochs']==0


def test_per_epoch_position_uses_propagated_not_static():
    # Extreme but valid 1 arcsec/yr PM: a static match from J2016 becomes
    # many arcseconds wrong in 2025; proper propagation recovers exact positions.
    coords=[]
    for mjd in (58000,59000,60000):
        year=2000+(mjd-51544.5)/365.25
        ra,dec=propagate_gaia_position(65.913324,24.937195,1000,-800,year)
        coords.append(point(mjd=mjd,ra=ra,dec=dec))
    result=run(coords,pmra_star_mas_yr=1000,pmdec_mas_yr=-800,radius_arcsec=1)
    c=result['curves'][0]
    assert c['median_epoch_corrected_separation_arcsec']<.0001
    assert c['median_separation_from_catalog_arcsec']>1
    assert result['status']=='possible_counterparts_require_independent_review'


def test_wrap_at_ra_zero_supported():
    p=[]
    for mjd in (59000,59001):
        yr=2000+(mjd-51544.5)/365.25
        ra,dec=propagate_gaia_position(359.99999,15,150,0,yr)
        p.append(point(mjd=mjd,ra=ra,dec=dec))
    result=run(p,ra_deg=359.99999,dec_deg=15,pmra_star_mas_yr=150,pmdec_mas_yr=0)
    assert result['n_provisionally_in_radius']==1


@pytest.mark.parametrize('bad', ['hello', '', 'a' * 20, '1.23','0'*21])
def test_invalid_gaia_id_rejected(bad):
    with pytest.raises(ValueError):
        run([],gaia_id=bad)


@pytest.mark.parametrize('radius', [0,-1,31,float('nan'),float('inf')])
def test_bad_radius_rejected(radius):
    with pytest.raises(ValueError):
        run([],radius_arcsec=radius)


@pytest.mark.parametrize('min_epochs',[0,-1,1.5,'2'])
def test_bad_min_count_rejected(min_epochs):
    with pytest.raises(ValueError):
        run([],min_positioned_epochs=min_epochs)


def test_invalid_oid_rejected():
    with pytest.raises(ValueError):
        run([point(oid='not-an-id')])


def test_invalid_band_rejected():
    with pytest.raises(ValueError):
        run([point(band='u')])


def test_invalid_epoch_fails_closed():
    with pytest.raises(ValueError):
        run([point(mjd=30000),point(mjd=30001)])


def test_invalid_dec_rejected():
    with pytest.raises(ValueError):
        run([point()],dec_deg=91)


def test_nan_motion_rejected():
    with pytest.raises(ValueError):
        run([],pmra_star_mas_yr=float('nan'))