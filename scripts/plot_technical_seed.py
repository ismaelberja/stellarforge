"""Plot REAL Luhman-mirror positions from the provisional 24-object seed.

These are actual catalog coordinates, not synthetic sky points; they remain
third-party MIRROR metadata until independently checked against publisher table.
"""
import csv
from pathlib import Path
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,default=ROOT/'data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv')
    parser.add_argument('--output',type=Path,default=ROOT/'reports/TAURUS_24_PRELIMINARY_SKY_POSITIONS.png')
    args=parser.parse_args()
    with args.input.open(newline='',encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    fig,ax=plt.subplots(figsize=(10.2,6.3))
    groups=sorted({row['group'] for row in rows})
    for group in groups:
        subset=[row for row in rows if row['group']==group]
        ax.scatter([float(s['ra']) for s in subset], [float(s['dec']) for s in subset], s=37,label=group,alpha=.84)
    ax.set(xlabel='ICRS right ascension (degrees)',ylabel='ICRS declination (degrees)',
           title='Provisional 24 Taurus positions — Luhman (2023) public table mirror')
    ax.invert_xaxis()
    ax.grid(alpha=.22)
    ax.legend(title='Kinematic group',fontsize=7,loc='center left',bbox_to_anchor=(1.0,.5))
    fig.text(.44,.03,'NOT A FINAL SCIENTIFIC SAMPLE · Mirror copy not byte-checked against publisher',
             ha='center',fontsize=8)
    fig.tight_layout(rect=(0,.045,.78,1))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(args.output,dpi=155)
    print(args.output)

if __name__=='__main__':main()