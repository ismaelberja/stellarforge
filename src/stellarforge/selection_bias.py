"""Selection-bias diagnostics for the Luhman (2023) Taurus membership census.

The bundled group totals summarize a pinned third-party mirror with Git blob
SHA-1 fe0d5a43...; they have NOT been byte-compared to the publisher's original.
No disk classes, ZTF coverage or variability are inferred from membership.
"""
from __future__ import annotations
import csv
from math import sqrt, isfinite
from pathlib import Path

MIRROR_BLOB_SHA1 = 'fe0d5a43dbd2ca8b867901686ab223a847c649e5'
# (all adopted Taurus members, members with Gaia DR3 ID, Gaia and 12<=G<=17)
# Source: fixed-column Table 2 mirror pinned in stellarforge.luhman2023.
GROUP_REFERENCE = {
    'unassigned': (119,55,25),
    'L1489/L1498': (6,6,5),
    'L1495/B209': (71,70,47),
    'B209N': (6,6,3),
    'L1524/L1529/B215': (66,66,45),
    'L1521/B213': (28,28,20),
    'HD28354': (16,16,10),
    'TTau': (5,5,2),
    'L1551': (59,59,44),
    'L1536': (42,42,30),
    'L1527': (28,28,20),
    'L1517': (62,62,44),
    'L1558': (9,9,6),
    'L1544': (15,15,13),
}
TOTAL = 532
GAIA = 467
ELIGIBLE_12_17 = 314


def wilson_interval(successes: int, count: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if count <= 0 or successes < 0 or successes > count:
        raise ValueError('Invalid binomial observations')
    if not isfinite(z) or z <= 0:
        raise ValueError('Invalid confidence level multiplier')
    p = successes / count
    denom = 1.0 + z*z/count
    center = (p+z*z/(2*count))/denom
    width = z*sqrt(p*(1-p)/count + z*z/(4*count*count))/denom
    return (0. if successes == 0 else max(0.,center-width),
            1. if successes == count else min(1.,center+width))


def _read_seed(path: Path) -> list[dict[str,str]]:
    with Path(path).open(newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or not {'gaia','group','gmag','ra','dec','original_line'} <= set(reader.fieldnames):
            raise ValueError('Invalid technical seed schema')
        rows = list(reader)
    if len(rows) != 24:
        raise ValueError(f'Expected 24 provisional seed members; got {len(rows)}')
    seen = set()
    for x in rows:
        if not x['gaia'].isdigit() or x['gaia'] in seen:
            raise ValueError('Invalid or duplicate Gaia source ID')
        seen.add(x['gaia'])
        if x['group'] not in GROUP_REFERENCE or x['group'] == 'unassigned':
            raise ValueError('Seed has unexpected group')
        if not 12 <= float(x['gmag']) <= 17:
            raise ValueError('Seed outside documented G selection')
        if not (0 <= float(x['ra']) < 360 and -90 <= float(x['dec']) <= 90):
            raise ValueError('Invalid source position')
    return rows


def audit_seed_selection(seed_path: Path) -> dict:
    """Measure observed selection vs fixed pinned-mirror aggregates (descriptive only)."""
    if sum(a for a,_,_ in GROUP_REFERENCE.values()) != TOTAL:
        raise AssertionError('Mirror group total mismatch')
    if sum(b for _,b,_ in GROUP_REFERENCE.values()) != GAIA:
        raise AssertionError('Mirror Gaia total mismatch')
    if sum(c for _,_,c in GROUP_REFERENCE.values()) != ELIGIBLE_12_17:
        raise AssertionError('Mirror magnitude denominator mismatch')
    seed = _read_seed(seed_path)
    counts = {name:sum(x['group']==name for x in seed) for name in GROUP_REFERENCE}
    rows = []
    for group,(total,with_gaia,bright) in GROUP_REFERENCE.items():
        n = counts[group]
        if n > bright:
            raise AssertionError('Selection larger than source pool')
        rows.append({
            'group':group,'catalog_members':total,'with_gaia_id':with_gaia,
            'gaia_g12_17':bright,'technical_seed_selected':n,
            'fraction_of_eligible_pool_selected':n/bright if bright else None,
            'ratio_of_selection_share_to_eligible_share':
              (n/24)/(bright/(ELIGIBLE_12_17-GROUP_REFERENCE['unassigned'][2]))
              if group!='unassigned' and bright else None,
        })
    missing = TOTAL-GAIA
    missing_unassigned = GROUP_REFERENCE['unassigned'][0]-GROUP_REFERENCE['unassigned'][1]
    status = {
        'data_status':'SECONDARY_PINNED_MIRROR_AGGREGATES_NOT_PUBLISHER_BYTES',
        'original_publisher_file_verified':False,
        'underlying_catalog_git_blob_sha1':MIRROR_BLOB_SHA1,
        'total_members':TOTAL, 'with_gaia_id':GAIA,
        'without_gaia_id':missing,
        'gaia_fraction':GAIA/TOTAL,
        'gaia_fraction_wilson95':wilson_interval(GAIA,TOTAL),
        'gaia_missing_without_group':missing_unassigned,
        'gaia_missing_without_group_fraction':missing_unassigned/missing,
        'g12_17_gaia_total':ELIGIBLE_12_17,
        'g12_17_gaia_with_named_group':ELIGIBLE_12_17-GROUP_REFERENCE['unassigned'][2],
        'seed_members':24,'seed_group_coverage':sum(x['technical_seed_selected']>0 for x in rows),
        'fraction_of_total_catalog_in_seed':24/TOTAL,
        'fraction_of_eligible_named_groups_in_seed':24/(ELIGIBLE_12_17-GROUP_REFERENCE['unassigned'][2]),
        'seed_member_disk_classes_verified':0,
        'ztf_lightcurves_verified_for_taurus':0,
        'group_table':rows,
        'interpretation':'Selection is intentionally balanced by named group, NOT population-representative.',
    }
    return status