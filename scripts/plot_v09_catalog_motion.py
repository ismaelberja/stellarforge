"""Astrometric displacement from real catalogue parameters (NO ZTF detections)."""
from __future__ import annotations

import csv
from pathlib import Path
import math

from stellarforge.association import propagate_gaia_position
from stellarforge.observational_plan import FIRST_TARGETS

ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/'data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv'


def draw(output:Path=ROOT/'reports/observational_gates_v0.9/TAURUS_TWO_STARS_CATALOG_PROPAGATION.png') -> Path:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    with SEED.open(newline='',encoding='utf-8-sig') as h:
        data={r['name']:r for r in csv.DictReader(h) if r['name'] in FIRST_TARGETS}
    fig, axs=plt.subplots(1,2,figsize=(11,5.0))
    years=[2018+i*.2 for i in range(31)]
    for ax,name in zip(axs,FIRST_TARGETS):
        row=data[name]
        ra,dec,pmra,pmdec=(float(row[k]) for k in ('ra','dec','pmra','pmdec'))
        xx=[];yy=[]
        for yr in years:
            r,d=propagate_gaia_position(ra,dec,pmra,pmdec,yr)
            dra=((r-ra+180)%360-180)*3600*math.cos(math.radians(dec))
            ddec=(d-dec)*3600
            xx.append(dra);yy.append(ddec)
        ax.plot(xx,yy,lw=2.3,label='Gaia-propagated nominal path')
        ax.scatter([xx[0],xx[-1]],[yy[0],yy[-1]],s=35,zorder=4)
        ax.annotate('2018',xy=(xx[0],yy[0]),xytext=(5,10),textcoords='offset points')
        ax.annotate('2024',xy=(xx[-1],yy[-1]),xytext=(8,9),textcoords='offset points')
        ax.scatter([0],[0],marker='+',s=80,label='Catalogue reference J2016.0')
        ax.set_title(f'{name} · Gaia DR3 {row["gaia"]}',fontsize=10)
        ax.set_xlabel('ΔRA cos(Dec) from catalogue (arcsec)')
        ax.set_ylabel('ΔDec from catalogue (arcsec)')
        ax.set_aspect('equal',adjustable='datalim')
        ax.grid(alpha=.25)
        ax.legend(fontsize=7,loc='best')
    fig.suptitle('Taurus technical seed: motion-only catalogue propagation · NOT ZTF observations',fontsize=12)
    fig.text(.5,.014,'Approximate 2D Gaia proper-motion predictions; no parallax, covariance, image review or verified counterpart.',ha='center',fontsize=8)
    fig.tight_layout(rect=(0,.045,1,.94))
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(output,dpi=170)
    plt.close(fig)
    return output

if __name__=='__main__':
    print(draw())