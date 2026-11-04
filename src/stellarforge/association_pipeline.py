"""Bridge validated raw IRSA CSV -> epoch-aware Gaia positional screening.

This module deliberately produces a review manifest, not an automatic match.
Data are assessed per OID/passband; no colors or physical classification.
"""
from __future__ import annotations

from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
import statistics

from .association import mjd_to_approximate_julian_year, screen_ztf_positional_candidates
from .luhman2023 import validate_technical_seed
from .ztf_photometry import inspect_ztf_bytes


def _centroid(ra_values,dec_values):
    """Mean unit-vector direction, valid around RA=0; observational centroid proxy."""
    import math
    x=y=z=0.
    for ra,dec in zip(ra_values,dec_values):
        r,d=math.radians(ra),math.radians(dec)
        x+=math.cos(d)*math.cos(r)
        y+=math.cos(d)*math.sin(r)
        z+=math.sin(d)
    if not math.hypot(x,y):
        raise ValueError('Degenerate sky centroid')
    return math.degrees(math.atan2(y,x))%360, math.degrees(math.atan2(z,math.hypot(x,y)))


def review_raw_target(seed_path:Path,gaia_dr3_source_id:str,ztf_input_path:Path,
                      output_json:Path,*,radius_arcsec:float=2.,min_epochs:int=30)->dict:
    """Run the chain on a locally available ZTF response, no internet required.

    Raw responses without an IRSA provenance sidecar are not promoted to
    verified observations. Even with a sidecar, object identity is on hold.
    """
    seed=Path(seed_path)
    validate_technical_seed(seed)
    with seed.open(newline='',encoding='utf-8-sig') as f:
        targets=[r for r in csv.DictReader(f) if r['gaia']==str(gaia_dr3_source_id)]
    if len(targets)!=1:
        raise ValueError('Gaia identifier not in the 24-object technical seed')
    target=targets[0]
    raw_path=Path(ztf_input_path)
    raw=raw_path.read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    sidecar=Path(str(raw_path)+'.provenance.json')
    source='unverified_local_input'
    if 'SYNTHETIC' in raw_path.name.upper():
        source='SYNTHETIC_EXAMPLE_NOT_OBSERVATIONAL_DATA'
    elif sidecar.exists():
        meta=json.loads(sidecar.read_text(encoding='utf-8'))
        if meta.get('sha256')!=sha:
            raise ValueError('Raw response SHA256 mismatch')
        if str(meta.get('url','')).startswith('https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?'):
            source='IRSA_URL_AND_SHA_MATCHED_BUT_ASTROMETRY_UNVERIFIED'
    stats,points=inspect_ztf_bytes(raw,target_ra=float(target['ra']),target_dec=float(target['dec']),
                                    radius_arcsec=radius_arcsec,min_good_epochs=min_epochs)
    by_curve=defaultdict(list)
    for p in points:
        by_curve[(p.oid,p.band,p.time_scale)].append(p)
    candidates=[]
    mjds=[]
    for (oid,band,scale),obs in sorted(by_curve.items()):
        if scale!='MJD' or any(p.ra_deg is None or p.dec_deg is None for p in obs):
            continue
        ra,dec=_centroid([p.ra_deg for p in obs],[p.dec_deg for p in obs])
        candidates.append({'oid':oid,'band':band,'ra_deg':ra,'dec_deg':dec,
                           'n_good_epochs':len(obs)})
        mjds.extend(p.time_value for p in obs)
    if not mjds:
        positional={'status':'no_positioned_MJD_curves', 'astrometric_match_verified':False,
                    'note':'Cannot estimate an observation epoch without positioned MJD photometry.'}
    else:
        epoch=mjd_to_approximate_julian_year(statistics.median(mjds))
        positional=screen_ztf_positional_candidates(
            gaia_id=target['gaia'],ra_deg=float(target['ra']),dec_deg=float(target['dec']),
            pmra_star_mas_yr=float(target['pmra']) if target['pmra'] else None,
            pmdec_mas_yr=float(target['pmdec']) if target['pmdec'] else None,
            ztf_sources=candidates,ztf_epoch_year=epoch,
            position_reference=target['reference'],radius_arcsec=radius_arcsec)
    manifest={'version':'0.6','gaia_dr3_source_id':target['gaia'],
              'data_status':source,'input_name':raw_path.name,'raw_sha256':sha,
              'seed_sha256':hashlib.sha256(seed.read_bytes()).hexdigest(),
              'catalog_source_mirror_verified_against_publisher_bytes':False,
              'qc':stats,'position_screen':positional,
              'n_original_ZTF_OIDs_in_accepted_points':len({p.oid for p in points}),
              'all_associations_confirmed':False,'all_physical_classifications_confirmed':False,
              'not_a_discovery':True,
              'review_steps':['Verify original literature catalog bytes',
                              'Evaluate Gaia astrometric covariance and propagated uncertainty',
                              'Inspect ZTF image cutouts for neighbors/blending',
                              'Choose vetted comparison stars and inspect field zeropoints',
                              'Use original observation epochs and time-system conversions']}
    out=Path(output_json);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(manifest,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')
    return manifest