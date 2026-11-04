"""Run conservative ZTF raw-file QC and epoch-aware Gaia review; no data invented."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from stellarforge.association_pipeline import review_raw_target

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--gaia-id',required=True)
    p.add_argument('--ztf-file',required=True,type=Path)
    p.add_argument('--seed',type=Path,default=ROOT/'data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv')
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    d=review_raw_target(a.seed,a.gaia_id,a.ztf_file,a.out)
    print(json.dumps({'data_status':d['data_status'],
                      'n_curves':d['qc']['curve_count'],
                      'position_status':d['position_screen']['status'],
                      'all_associations_confirmed':False},indent=2))