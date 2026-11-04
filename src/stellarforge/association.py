"""Epoch-aware positional screening for Gaia <-> ZTF sources.

The numerical propagation follows the Gaia convention mu_alpha* = d(alpha)/dt cos(delta).
It keeps the motion tangent to a sphere and renormalizes the resulting vector.
Perspective acceleration, parallax, full covariance, multiplicity and the image
PSF are NOT accounted for. A unique candidate is not a verified association.

ZTF centroid positions are expected from QC'd photometry or a vetted objects
catalog. Never attach a Gaia ID to a ZTF OID based on cone proximity alone.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Mapping

from .coordinates import angular_separation_arcsec, validate_icrs

MAS_TO_RAD = math.pi / (180 * 3600 * 1000)
GAIA_DR3_EPOCH = 2016.0


@dataclass(frozen=True)
class PositionalCandidate:
    oid: str
    band: str
    separation_arcsec: float
    n_good_epochs: int
    within_search_radius: bool


def propagate_gaia_position(ra_deg: float, dec_deg: float,
                            pmra_star_mas_yr: float, pmdec_mas_yr: float,
                            to_julian_year: float,
                            from_julian_year: float = GAIA_DR3_EPOCH) -> tuple[float, float]:
    """Approximate 2D proper-motion propagation on sphere; not a full astrometric solution."""
    validate_icrs(ra_deg, dec_deg)
    for v in (pmra_star_mas_yr, pmdec_mas_yr, to_julian_year, from_julian_year):
        if not math.isfinite(v):
            raise ValueError('Non-finite epoch or proper motion')
    years = to_julian_year - from_julian_year
    if abs(years) > 50 or max(abs(pmra_star_mas_yr), abs(pmdec_mas_yr)) > 10_000:
        raise ValueError('Motion or temporal extrapolation too large for approximate propagator')
    ra = math.radians(ra_deg)
    dec = math.radians(dec_deg)
    c, s = math.cos(dec), math.sin(dec)
    ca, sa = math.cos(ra), math.sin(ra)
    unit = (c*ca, c*sa, s)
    east = (-sa, ca, 0.0)
    north = (-s*ca, -s*sa, c)
    dra = pmra_star_mas_yr * MAS_TO_RAD * years
    ddec = pmdec_mas_yr * MAS_TO_RAD * years
    vector = tuple(unit[i] + dra*east[i] + ddec*north[i] for i in range(3))
    norm = math.sqrt(sum(v*v for v in vector))
    x,y,z = (v/norm for v in vector)
    return math.degrees(math.atan2(y,x)) % 360, math.degrees(math.atan2(z, math.hypot(x,y)))


def mjd_to_approximate_julian_year(mjd: float) -> float:
    """MJD->Julian-year approximation for screening only, NOT a time-scale conversion."""
    if not math.isfinite(mjd) or not 45_000 <= mjd <= 80_000:
        raise ValueError('Unexpected MJD range')
    return 2000.0 + (mjd-51544.5)/365.25


def screen_ztf_positional_candidates(gaia_id: str, ra_deg: float, dec_deg: float,
                                     pmra_star_mas_yr: float | None,
                                     pmdec_mas_yr: float | None,
                                     ztf_sources: list[Mapping],
                                     *, ztf_epoch_year: float | None,
                                     position_reference: str = 'Gaia',
                                     radius_arcsec: float = 2.0,
                                     ambiguity_margin_arcsec: float = 1.0) -> dict:
    """Report one-to-many positional ambiguity without ever confirming identity.

    All candidate OIDs are retained, including those outside the acceptance
    radius. A unique positional candidate is *only* eligible for later
    image/crowding, epoch, and photometric consistency reviews.
    """
    if not str(gaia_id).isdigit() or not (0 < len(str(gaia_id)) <= 19):
        raise ValueError('Bad Gaia DR3 source ID')
    validate_icrs(ra_deg,dec_deg)
    if not math.isfinite(radius_arcsec) or not 0 < radius_arcsec <= 30:
        raise ValueError('Invalid positional search radius')
    if not math.isfinite(ambiguity_margin_arcsec) or ambiguity_margin_arcsec < 0:
        raise ValueError('Invalid ambiguity margin')
    result = {'gaia_dr3_source_id': str(gaia_id), 'catalog_position_reference': position_reference,
              'search_radius_arcsec': radius_arcsec,
              'astrometric_match_verified': False,
              'full_astrometric_covariance_propagated': False,
              'parallax_and_perspective_included': False,
              'status': 'not_evaluated', 'candidates': [], 'provisional_oid': None,
              'requires_image_and_catalog_review': True,
              'ztf_epoch_julian_year': ztf_epoch_year}
    if position_reference != 'Gaia' or pmra_star_mas_yr is None or pmdec_mas_yr is None or ztf_epoch_year is None:
        result['status']='insufficient_epoch_information'
        return result
    ra_new,dec_new=propagate_gaia_position(ra_deg,dec_deg,pmra_star_mas_yr,pmdec_mas_yr,ztf_epoch_year)
    result.update({'ra_propagated_deg':ra_new, 'dec_propagated_deg':dec_new,
                   'epoch_propagation_used': 'approximate_tangent_vector_on_sphere'})
    seen=set()
    for source in ztf_sources:
        oid=str(source['oid'])
        band=str(source['band']).lower()
        if not oid.isdigit() or not oid or band not in ('g','r','i'):
            raise ValueError('Invalid ZTF object or passband')
        key=(oid,band)
        if key in seen:raise ValueError('Duplicate OID/band centroid')
        seen.add(key)
        r,d=float(source['ra_deg']),float(source['dec_deg'])
        validate_icrs(r,d)
        good=int(source['n_good_epochs'])
        if good<0:raise ValueError('Negative accepted-epoch count')
        sep=angular_separation_arcsec(ra_new,dec_new,r,d)
        result['candidates'].append(asdict(PositionalCandidate(oid,band,round(sep,6),good,sep<=radius_arcsec)))
    result['candidates'].sort(key=lambda c:(c['separation_arcsec'],c['band'],c['oid']))
    within=[x for x in result['candidates'] if x['within_search_radius']]
    if not within:
        result['status']='no_positional_candidate'
    elif any(x['n_good_epochs'] < 1 for x in within):
        result['status']='position_hit_without_usable_photometry'
    else:
        # Different band OIDs may correspond to one star, but cannot be
        # declared uniquely associated by these coordinates alone.
        by_band={b:[x for x in within if x['band']==b] for b in ('g','r','i')}
        if any(len(x)>1 for x in by_band.values()):
            result['status']='ambiguous_multiple_oids_same_band'
        elif len(within)>=2 and max(x['separation_arcsec'] for x in within)-min(x['separation_arcsec'] for x in within)>ambiguity_margin_arcsec:
            # Proximity across different bands is not proof of same source.
            result['status']='possible_blend_or_band_centroid_disagreement'
        else:
            result['status']='positional_candidates_require_independent_review'
            result['provisional_oid']= {x['band']:x['oid'] for x in within}
    return result