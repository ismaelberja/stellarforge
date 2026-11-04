"""StellarForge v1.0: run the two pre-registered IRSA queries in an isolated job.

Default is OFFLINE. --execute opts into TWO official queries, retaining raw
bytes and sidecars locally. Reports are *evidence triage*, not detections.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from run_v09_pipeline import run, SEED, ROOT


def execute_pilot(*, output: Path, execute: bool = False, seed: Path = SEED,
                  runner=run) -> dict:
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    result=runner(seed=seed,output=output,execute=execute)
    summary={
        'schema_version':'1.0.0',
        'generated_utc':datetime.now(timezone.utc).isoformat(),
        'source_catalog_sha256':hashlib.sha256(Path(seed).read_bytes()).hexdigest(),
        'network_requested':execute,
        'number_of_targets':len(result['acquisition']),
        'raw_responses_present':sum(x['raw_response_present'] for x in result['acquisition']),
        'official_irsa_source_independently_authenticated':False,
        'gaia_ztf_associations_independently_verified':0,
        'physical_dipper_or_burster_confirmations':0,
        'individual_target_outcomes':result['acquisition'],
        'scientific_publication_ready':False,
        'required_next_review':[
            'Compare catalog mirror against publisher source bytes',
            'Independently authenticate and assess IRSA photometric responses',
            'Review ambiguous ZTF OIDs and image-level crowding',
            'Inspect multi-band behavior and field-star controls',
            'Quantify injection-recovery on actual observing cadences',
        ],
    }
    (output/'V10_TRIAGE.json').write_text(json.dumps(summary,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')
    report=['# StellarForge 1.0 — observational pilot intake', '',
            f'- **Network requests enabled:** {execute}',
            f'- **Raw ZTF response files available:** {summary["raw_responses_present"]} / {summary["number_of_targets"]}',
            '- **Independently verified Gaia–ZTF associations:** 0',
            '- **Confirmed astrophysical events:** 0', '',
            '| Target | Outcome | Raw data supplied |', '|---|---|---|']
    for x in summary['individual_target_outcomes']:
        report.append(f'| {x["target"]} | `{x["result"]}` | {"Yes" if x["raw_response_present"] else "No"} |')
    report += ['', '## Interpretation', '',
               'A raw HTTP response and its self-reported SHA-256 alone are not independent',
               'source authentication or evidence that the light curve belongs to the claimed',
               'Taurus member. The analysis stops at observational intake.', '',
               'All raw photometric bytes must remain outside Git; a private CI artifact may',
               'be used for internal examination. No physical classification is made.', '']
    (output/'V10_INTAKE_REPORT.md').write_text('\n'.join(report),encoding='utf-8')
    return summary


def main():
    p=argparse.ArgumentParser(description='Execute the 2-target StellarForge observational pilot')
    p.add_argument('--execute',action='store_true',help='Opt in to the 2 IRSA requests')
    p.add_argument('--output',type=Path,default=ROOT/'reports/generated/v1.0_pilot')
    p.add_argument('--seed',type=Path,default=SEED)
    opts=p.parse_args()
    r=execute_pilot(output=opts.output,execute=opts.execute,seed=opts.seed)
    print(json.dumps({'network_requested':r['network_requested'],
                      'raw_responses_present':r['raw_responses_present'],
                      'individual_target_outcomes':r['individual_target_outcomes']},indent=2))

if __name__=='__main__':main()