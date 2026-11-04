"""Conservative g-r diagnostics for *manually reviewed* ZTF source associations.

This module does not cross-match two ZTF OIDs. The caller must explicitly
provide the two OIDs, whose common astrophysical source remains unverified
until independent astrometric and imaging review. Approximate color from
non-simultaneous epochs is only a diagnostic, not a physical extinction law.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from math import isfinite, sqrt
from statistics import median

from .ztf_photometry import PhotometricPoint


@dataclass(frozen=True)
class MatchedColor:
    g_oid: str
    r_oid: str
    g_mjd: float
    r_mjd: float
    time_separation_days: float
    color_g_minus_r_mag: float
    color_uncertainty_mag: float
    g_row: int
    r_row: int


def match_g_r_points(points: list[PhotometricPoint], *, g_oid: str,
                     r_oid: str, max_gap_days: float = 0.5,
                     time_scale: str = 'MJD') -> dict:
    """Pair near-in-time g and r rows 1:1 without interpolation or re-use.

    Dataset must have exactly one time convention for the selected curves.
    Unpaired points remain unpaired: no false color is manufactured.
    Greedy global minimum-gap pairing is deterministic and yields no reuse.
    """
    if not g_oid or not r_oid or g_oid == r_oid or not str(g_oid).isdigit() or not str(r_oid).isdigit():
        raise ValueError('Provide two distinct numeric ZTF OIDs: one g, one r')
    if time_scale not in {'MJD', 'HMJD', 'HJD'}:
        raise ValueError('Unknown time scale')
    if not isfinite(max_gap_days) or not 0 < max_gap_days <= 2:
        raise ValueError('max_gap_days must be in (0, 2]')
    selected=[p for p in points if p.oid in {g_oid,r_oid}]
    if any(p.time_scale!=time_scale for p in selected):
        raise ValueError('Mixed time conventions; no implicit conversion')
    if any(not isfinite(p.time_value) or not isfinite(p.magnitude) or
           not isfinite(p.magnitude_error) or p.magnitude_error<=0 for p in selected):
        raise ValueError('Invalid photometric measurement')
    if any(p.oid==g_oid and p.band!='g' or p.oid==r_oid and p.band!='r' for p in selected):
        raise ValueError('OID-to-band conflict; never pool unrelated curves')
    if any(p.catflags & 32768 for p in selected):
        raise ValueError('Input has cloud/moon-flagged measurements; QC first')
    g=sorted((p for p in selected if p.oid==g_oid),key=lambda p:(p.time_value,p.row_number))
    r=sorted((p for p in selected if p.oid==r_oid),key=lambda p:(p.time_value,p.row_number))
    candidates=sorted((abs(a.time_value-b.time_value),i,j) for i,a in enumerate(g)
                      for j,b in enumerate(r) if abs(a.time_value-b.time_value)<=max_gap_days)
    g_used=set();r_used=set();matches=[]
    for gap,i,j in candidates:
        if i in g_used or j in r_used:continue
        g_used.add(i);r_used.add(j)
        a,b=g[i],r[j]
        matches.append(MatchedColor(g_oid,r_oid,a.time_value,b.time_value,gap,
                                    a.magnitude-b.magnitude,
                                    sqrt(a.magnitude_error**2+b.magnitude_error**2),
                                    a.row_number,b.row_number))
    matches.sort(key=lambda x:(x.g_mjd,x.r_mjd,x.g_row,x.r_row))
    return {
        'status':'PROVISIONAL_NON_SIMULTANEOUS_COLOR_NO_SOURCE_CONFIRMATION',
        'g_oid':g_oid,'r_oid':r_oid,'time_scale':time_scale,
        'max_pair_gap_days':max_gap_days,'g_epochs':len(g),'r_epochs':len(r),
        'paired_epochs':len(matches),'unpaired_g_epochs':len(g)-len(g_used),
        'unpaired_r_epochs':len(r)-len(r_used),
        'median_g_minus_r_mag': median(m.color_g_minus_r_mag for m in matches) if matches else None,
        'median_pair_delay_days':median(m.time_separation_days for m in matches) if matches else None,
        'pairs':[asdict(m) for m in matches],
        'independently_confirmed_same_astrophysical_source':False,
        'extinction_or_accretion_classification':None,
        'required_gates':['independently_verify_both_ZTF_OIDs_identify_the_same_star',
                          'inspect_nearby_sources_and_epoch_images',
                          'model_non_simultaneity_and_color_systematics',
                          'require_independent_disk_and_accretion_diagnostics'],
    }