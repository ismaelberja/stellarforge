"""Offline ZTF observational integration. Does not download or infer membership."""
import argparse
import json
from pathlib import Path
from stellarforge.observational_release import inspect_observational_source, plot_observational_sample


def main(argv=None):
    p=argparse.ArgumentParser(description='Offline observational QC + cadence evidence gate')
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--origin',choices=['secondary_public_example','direct_irsa'],required=True)
    p.add_argument('--source-url',required=True)
    p.add_argument('--expected-sha256')
    p.add_argument('--target-name')
    p.add_argument('--target-ra',type=float)
    p.add_argument('--target-dec',type=float)
    p.add_argument('--plot',action='store_true')
    args=p.parse_args(argv)
    result=inspect_observational_source(args.input,args.output,origin=args.origin,
        source_url=args.source_url,expected_sha256=args.expected_sha256,
        target_name=args.target_name,target_ra=args.target_ra,target_dec=args.target_dec)
    if args.plot and result['raw_rows']:
        plot_observational_sample(args.input,args.output/'OBSERVATIONAL_SAMPLE_NOT_TAURUS.png',origin=args.origin)
    print(json.dumps({k:result[k] for k in ('status','raw_rows','qc_accepted','qc_rejected',
                                             'taurus_lightcurves_verified','physical_classification_issued')},indent=2))


if __name__ == '__main__':
    main()