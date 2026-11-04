"""A machine-readable observational gate: missing data never becomes zero variability."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from .luhman2023 import validate_technical_seed
from .observational_plan import FIRST_TARGETS
from .ztf import build_ztf_url
from .association import propagate_gaia_position


def build_readiness_ledger(seed_file: Path, output_dir: Path) -> dict:
    seed_file = Path(seed_file)
    quality = validate_technical_seed(seed_file)
    with seed_file.open(encoding="utf-8-sig", newline="") as f:
        sources = list(csv.DictReader(f))
    names = {str(s['name']) for s in sources}
    if not set(FIRST_TARGETS) <= names:
        raise ValueError("Pre-registered target names missing from 24-star seed")
    target_rows=[]
    for x in sources:
        if x['reference'] != 'Gaia':
            raise ValueError("Unexpected position reference for two-star protocol")
        ra,dec = float(x['ra']),float(x['dec'])
        pr,pd = propagate_gaia_position(ra, dec,float(x['pmra']),float(x['pmdec']),2021.0)
        is_pilot=x['name'] in FIRST_TARGETS
        target_rows.append({
            'gaia_dr3_source_id': x['gaia'],
            'catalog_name': x['name'] or x.get('mass') or x.get('two_mass_id', '') or 'unnamed_catalog_member',
            'catalogue_line': int(x['original_line']),
            'kinematic_group': x['group'],
            'pilot_priority': 'pilot_pre_registered' if is_pilot else 'not_current_pilot',
            'catalog_ra_deg':ra, 'catalog_dec_deg':dec,
            'approx_epoch_2021_ra_deg':pr, 'approx_epoch_2021_dec_deg':pd,
            'query_url_illustrative_epoch_2021':build_ztf_url(pr,pd,radius_arcsec=2.0,
                                      bands=('g','r'),output_format='csv'),
            'ztf_api_query_executed':False,
            'ztf_data_present':False,
            'source_image_crossmatch_checked':False,
            'disk_class_independently_checked':False,
            'real_cadence_selection_function_measured':False,
            'event_candidate_claim':False,
            'readiness':'blocked_awaiting_verified_ztf_raw_lightcurves',
        })
    report={
        'version':'0.8',
        'technical_taurus_catalog_rows':len(target_rows),
        'named_kinematic_groups':len({s['group'] for s in sources}),
        'catalogue_structural_validation':quality,
        'seed_sha256':hashlib.sha256(seed_file.read_bytes()).hexdigest(),
        'publisher_mirror_byte_identity_verified':False,
        'science_target_groups_not_confused_with_disk_classes':True,
        'ztf_observations_imported_for_taurus':0,
        'targets_with_verified_ztf_source_associations':0,
        'priority_pilot_names':list(FIRST_TARGETS),
        'catalogue_members_for_planning_only':target_rows,
        'not_evidence_for_discoveries':True,
    }
    output=Path(output_dir)
    output.mkdir(parents=True,exist_ok=True)
    (output/'TAURUS_READINESS_LEDGER.json').write_text(json.dumps(report,indent=2,
                  allow_nan=False)+'\n',encoding='utf-8')
    with (output/'TAURUS_READINESS_LEDGER.csv').open('w',encoding='utf-8',newline='') as f:
        fieldnames=list(target_rows[0])
        writer=csv.DictWriter(f,fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(target_rows)
    lines=[
        '# StellarForge v0.8 — Taurus observational readiness', '',
        f'**{len(target_rows)} real catalogue sources planned, 0 validated ZTF source associations.**', '',
        'The positions and Gaia DR3 identifiers are genuine catalogue entries from a pinned third-party copy of Luhman (2023); the original publisher bytes are not cross-checked.',
        'These are not disk-class labels and there are no new detections.', '',
        '## The two pre-registered pilot sources', '',
        '| Source | Gaia DR3 | Query state | Identity state |', '|---|---|---|---|',
    ]
    for row in target_rows:
        if row['pilot_priority']=='pilot_pre_registered':
            lines.append(f"| {row['catalog_name']} | `{row['gaia_dr3_source_id']}` | Not executed | Unverified |")
    lines += ['', '## Next evidence thresholds', '',
        '1. Retrieve publisher original Taurus table and cross-check members/identifiers.',
        '2. Download raw g/r curves for the two pilot targets using the official API; keep responses and SHA256.',
        '3. Run QC and time-convention checks on all OIDs, not on a guessed single match.',
        '4. Propagate Gaia position to actual observation epochs; inspect PSF/crowding and neighbouring sources.',
        '5. Perform matched-field controls, cadence-driven injections, and report negative results.',
        '6. Only then consider physical interpretation or candidate review.', '',
        '**Status:** study setup, not an astronomical discovery.',
    ]
    (output/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return report