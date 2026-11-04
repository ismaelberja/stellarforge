"""24 TRUE literature-catalog Taurus positions propagated for engineering QA.

Nominal target epoch J2021.0 is a demonstration grid, NOT actual measured ZTF
exposure times. No target identity or ZTF lightcurve is confirmed by this.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import statistics
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from stellarforge.association import propagate_gaia_position
from stellarforge.coordinates import angular_separation_arcsec
from stellarforge.luhman2023 import validate_technical_seed

SEED=ROOT/'data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv'
OUT=ROOT/'reports/v0.6_catalog_astrometry'


def run(seed=SEED,out=OUT,epoch=2021.0):
    seed=Path(seed)
    validation=validate_technical_seed(seed)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    with seed.open(newline='',encoding='utf-8-sig') as f:
        rows=list(csv.DictReader(f))
    result=[]
    for r in rows:
        if r['reference']!='Gaia':
            raise ValueError('Demonstration requires a Gaia J2016.0 position reference')
        ra,dec=float(r['ra']),float(r['dec'])
        n_ra,n_dec=propagate_gaia_position(ra,dec,float(r['pmra']),float(r['pmdec']),epoch)
        offset=angular_separation_arcsec(ra,dec,n_ra,n_dec)
        result.append({'gaia_dr3_source_id':r['gaia'],'source_name':r['name'] or r['two_mass_id'],
                       'kinematic_group':r['group'],'ra_j2016_deg':f'{ra:.6f}',
                       'dec_j2016_deg':f'{dec:.6f}',
                       'pmra_star_mas_per_year':r['pmra'],'pmdec_mas_per_year':r['pmdec'],
                       'ra_propagated_nominal_deg':f'{n_ra:.9f}',
                       'dec_propagated_nominal_deg':f'{n_dec:.9f}',
                       'nominal_julian_epoch':f'{epoch:.1f}',
                       'displacement_arcsec':f'{offset:.6f}',
                       'source_line':r['original_line']})
    if len(result)!=24 or len({x['gaia_dr3_source_id'] for x in result})!=24:
        raise ValueError('Unexpected technical pilot size')
    dest=out/'TAURUS_24_NOMINAL_EPOCH_POSITIONS.csv'
    with dest.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=result[0].keys());writer.writeheader();writer.writerows(result)
    offsets=[float(x['displacement_arcsec']) for x in result]
    audit={'status':'real_literature_catalog_derived_astrometric_engineering_example',
           'n_real_taurus_catalog_entries':len(result),
           'n_gaia_position_reference':len(result),
           'catalog_seed_sha256':hashlib.sha256(seed.read_bytes()).hexdigest(),
           'source_catalog_mirror_git_blob_sha1':'fe0d5a43dbd2ca8b867901686ab223a847c649e5',
           'source_original_publisher_byte_crosscheck_completed':False,
           'reference_epoch_julian_year':2016.0,'illustrative_target_epoch_julian_year':epoch,
           'median_angular_displacement_arcsec':round(statistics.median(offsets),6),
           'max_angular_displacement_arcsec':round(max(offsets),6),
           'min_angular_displacement_arcsec':round(min(offsets),6),
           'n_above_0p1_arcsec':sum(x>.1 for x in offsets),
           'n_above_0p2_arcsec':sum(x>.2 for x in offsets),
           'ztf_observations_downloaded':0,'confirmed_crossmatches':0,
           'notes':['Epoch J2021.0 is illustrative, not the measured ZTF epoch.',
                    'These 24 are provisional Gaia-brightness-selected targets, not a frozen Class II/III sample.',
                    'Propagation ignores parallax, perspective, astrometric covariance and crowded-field biases.',
                    'Matching must ultimately use each observation epoch and image/source diagnostics.',
                    'A matching radius cannot be validated from this astrometric calculation alone.']}
    (out/'ASTROMETRIC_ENGINEERING_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    labels=[r['source_name'][:22] for r in result]
    fig,ax=plt.subplots(figsize=(10.5,7.4))
    xx=[float(r['pmra_star_mas_per_year']) for r in result]
    yy=[float(r['pmdec_mas_per_year']) for r in result]
    ax.scatter(xx,yy,s=50,alpha=.8)
    for i in range(len(result)):
        if i%4==0:ax.annotate(labels[i],(xx[i],yy[i]),xytext=(4,4),textcoords='offset points',fontsize=7)
    ax.axhline(0,linewidth=.8,color='gray',alpha=.4)
    ax.axvline(0,linewidth=.8,color='gray',alpha=.4)
    ax.set_xlabel('Gaia proper motion in RA* [mas/year]')
    ax.set_ylabel('Gaia proper motion in Dec [mas/year]')
    ax.set_title('24 real literature-catalog Taurus members | proper-motion screening\n'
                 'Illustrative J2016 -> J2021 propagation, not confirmed ZTF associations')
    ax.grid(alpha=.18)
    fig.tight_layout()
    fig.savefig(out/'TAURUS_24_PROPER_MOTIONS_REAL_CATALOG.png',dpi=170)
    plt.close(fig)
    return audit


if __name__=='__main__':
    print(json.dumps(run(),indent=2))