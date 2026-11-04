"""StellarForge v0.9 offline-first two-target observational evidence pipeline.

Default: does not access network or invent observations.
With --execute: attempts exactly one official IRSA request for each target,
with provenance and SHA-256; on failure the dossier remains pending.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError, URLError

from stellarforge.batch import CacheConflict, validate_raw_cache
from stellarforge.observational_dossier import (
    build_target_dossier, write_project_evidence_dashboard,
)
from stellarforge.observational_plan import FIRST_TARGETS, make_pilot_plan, save_pilot_plan
from stellarforge.ztf import fetch_ztf_raw

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / 'data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv'


def run(*, seed: Path, output: Path, execute: bool = False,
        fetcher=fetch_ztf_raw) -> dict:
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    plan = make_pilot_plan(seed)
    save_pilot_plan(output / 'TWO_STAR_OFFICIAL_IRSA_QUERY_PLAN.json', plan)
    dossiers = []
    acquisition = []
    for target in plan['pilot_targets']:
        name, gaia_id = target['catalog_name'], target['gaia_dr3_source_id']
        raw_path = output / 'raw' / f'{gaia_id}.csv'
        attempted = False
        outcome = 'NOT_ATTEMPTED_OFFLINE_MODE'
        error_type = None
        if execute:
            # Research raw files are immutable: never silently overwrite a
            # previous response, even if the new query URL has changed.
            try:
                prior = validate_raw_cache(raw_path, target['ztf_api_query_url'])
                if prior is not None:
                    outcome = 'CACHED_RAW_RESPONSE_WITH_VERIFIED_INTEGRITY'
                else:
                    attempted = True
                    # Two targets, no aggressive polling/retries.
                    fetcher(target['ztf_api_query_url'], raw_path, timeout_sec=20)
                    outcome = 'RAW_RESPONSE_SAVED_NOT_AUTHENTICATED_OR_CROSSMATCHED'
            except (CacheConflict, HTTPError, URLError, TimeoutError,
                    ConnectionError, OSError, ValueError) as err:
                outcome = ('CACHE_CONFLICT_REQUIRES_MANUAL_INTERVENTION' if isinstance(err, CacheConflict)
                           else 'REQUEST_FAILED_NO_OBSERVATIONAL_CLAIM')
                error_type = type(err).__name__
                if isinstance(err, CacheConflict):
                    raise
        available = raw_path.exists()
        dossier = build_target_dossier(seed, name, raw_path=raw_path if available else None,
                                       output=output / f'{gaia_id}_EVIDENCE_DOSSIER.json')
        dossiers.append(dossier)
        acquisition.append({
            'gaia_dr3_source_id': gaia_id, 'target': name,
            'network_attempted': attempted,
            'result': outcome, 'exception_type': error_type,
            'raw_response_present': available,
            'response_authenticated_by_independent_evidence': False,
            'ztf_counterpart_confirmed': False,
        })
    dashboard = write_project_evidence_dashboard(dossiers,
                                                 output / 'STELLARFORGE_V09_EVIDENCE_DASHBOARD.html')
    report = {
        'version': '0.9.0',
        'data': 'Luhman (2023) 24-object technical seed, publisher-byte verification pending',
        'seed_sha256': hashlib.sha256(Path(seed).read_bytes()).hexdigest(),
        'network_mode': 'EXECUTE_TWO_QUERIES' if execute else 'OFFLINE_ONLY',
        'n_targets': len(dossiers),
        'acquisition': acquisition,
        'dossier_status': {d['target']: d['status'] for d in dossiers},
        'dashboard': dashboard,
        'ztf_official_photometry_confirmed_for_Taurus': False,
        'physical_dipper_burster_confirmations': 0,
        'next_science_gate': 'Obtain authentic official IRSA response and independently inspect image/crowding and epoch positions before classifying',
    }
    (output / 'RUN_SUMMARY.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    (output / 'README.md').write_text(
        '# StellarForge v0.9 — Observational evidence\n\n'
        'This directory is a **research-readiness artifact**, not a paper result.\n\n'
        '- `TWO_STAR_OFFICIAL_IRSA_QUERY_PLAN.json` contains official IRSA URLs.\n'
        '- `*_EVIDENCE_DOSSIER.json` documents per-target scientific gates and source provenance.\n'
        '- `STELLARFORGE_V09_EVIDENCE_DASHBOARD.html` is an offline standalone dashboard.\n'
        '- `RUN_SUMMARY.json` distinguishes network failures from no astronomical coverage.\n\n'
        'Until response bytes, ZTF OIDs, Gaia cross-match and image checks are independently verified, **no Taurus ZTF photometry or physical detections are claimed**.\n',
        encoding='utf-8'
    )
    return report


def main(argv=None):
    p = argparse.ArgumentParser(description='Build offline v0.9 evidence dossiers for FT Tau and CIDA 11')
    p.add_argument('--seed', type=Path, default=SEED)
    p.add_argument('--output', type=Path, default=ROOT/'reports/observational_gates_v0.9')
    p.add_argument('--execute', action='store_true',
                   help='Opt in to TWO official IRSA network requests; never confirms a physical source')
    options=p.parse_args(argv)
    r=run(seed=options.seed,output=options.output,execute=options.execute)
    print(json.dumps({'mode':r['network_mode'],'n_targets':r['n_targets'],
                      'dossier_status':r['dossier_status'],
                      'acquisition':r['acquisition'],
                      'physical_confirmations':r['physical_dipper_burster_confirmations']}, indent=2))


if __name__ == '__main__':
    main()