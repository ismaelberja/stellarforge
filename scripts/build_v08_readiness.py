"""Prepare the 24-source real-catalogue research gates offline."""
import argparse
from pathlib import Path
from stellarforge.readiness import build_readiness_ledger


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--seed',type=Path,default=Path('data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv'))
    p.add_argument('--out',type=Path,default=Path('reports/readiness_v0.8'))
    args=p.parse_args(argv)
    result=build_readiness_ledger(args.seed,args.out)
    print(f"Real catalog sources planned: {result['technical_taurus_catalog_rows']}; "
          f"Taurus ZTF associations confirmed: {result['targets_with_verified_ztf_source_associations']}")

if __name__=='__main__':main()