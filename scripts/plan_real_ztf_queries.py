"""Build ZTF download *plans* for provisional Taurus positions; no HTTP calls.

Every coordinate comes from the 24-line public Luhman table mirror extract.
No coordinate in this manifest is declared a secure ZTF cross-match. The
Gaia catalog epoch is J2016.0; real source identification must propagate
position to observation epoch and review neighboring candidates.
"""
from pathlib import Path
import argparse
import csv
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from stellarforge.ztf import build_ztf_url
from stellarforge.luhman2023 import validate_technical_seed

COLS=['gaia_dr3_source_id','two_mass_id','name','group','ra_deg_source','dec_deg_source',
      'gmag','position_reference','source_original_line','query_radius_arcsec','query_url',
      'retrieval_status','epoch_propagation','ztf_identity_review']


def build_manifest(src: Path, radius_arcsec: float = 2.0):
    validate_technical_seed(src)
    with src.open(newline='',encoding='utf-8') as f:
        targets=list(csv.DictReader(f))
    output=[]
    for row in targets:
        url=build_ztf_url(float(row['ra']),float(row['dec']),radius_arcsec,
                          ('g','r'),32768,'csv')
        output.append({
            'gaia_dr3_source_id':row['gaia'], 'two_mass_id':row['two_mass_id'],
            'name':row['name'], 'group':row['group'],
            'ra_deg_source':row['ra'],'dec_deg_source':row['dec'],'gmag':row['gmag'],
            'position_reference':row['reference'],'source_original_line':row['original_line'],
            'query_radius_arcsec':radius_arcsec,'query_url':url,
            'retrieval_status':'not_requested',
            'epoch_propagation':'required_before_final_crossmatch',
            'ztf_identity_review':'required; multiple OIDs may exist',
        })
    return output


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,default=ROOT/'data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv')
    p.add_argument('--output',type=Path,default=ROOT/'reports/TAURUS_24_ZTF_QUERY_PLAN.csv')
    p.add_argument('--radius-arcsec',type=float,default=2.)
    args=p.parse_args()
    result=build_manifest(args.input,args.radius_arcsec)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=COLS);writer.writeheader();writer.writerows(result)
    print(f"Planned {len(result)} real-position ZTF cone queries; 0 requests made, 0 matches asserted")

if __name__=='__main__':main()