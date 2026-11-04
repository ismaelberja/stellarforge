"""Deterministically regenerate the provisional 24-row Taurus coordinate seed.

Requires original machine-readable Table 2 downloaded and byte-checked from
pinned third-party mirror. NO variability-based selection; NOT disk-stratified.
"""
from pathlib import Path
import argparse
import csv
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from stellarforge.luhman2023 import parse_membership_mrt, MIRROR_BLOB_SHA1, git_blob_sha1

FIELDS = ['gaia','two_mass_id','name','ra','dec','reference','sptype','pmra','pmdec','gmag','group','original_line']


def generate(mrt_bytes: bytes) -> list[dict[str, str]]:
    if git_blob_sha1(mrt_bytes) != MIRROR_BLOB_SHA1:
        raise ValueError('Input bytes do not match pinned Luhman 2023 mirror blob')
    data = parse_membership_mrt(mrt_bytes)
    eligible = [r for r in data['members'] if r['gaia_dr3_source_id']
                and r['position_reference'] == 'Gaia' and r['kinematic_group']
                and r['gmag'] is not None and 12 <= r['gmag'] <= 17
                and r['pmra_mas_per_year'] is not None and r['pmdec_mas_per_year'] is not None]
    groups = {}
    for item in eligible:
        groups.setdefault(item['kinematic_group'], []).append(item)
    if len(groups) != 13:
        raise ValueError('13 named groups not represented in available Gaia data')
    group_order = sorted(groups, key=lambda name:(-len(groups[name]),name))
    selected = []
    for group in group_order:
        selection = min(groups[group], key=lambda r:(abs(r['gmag'] - 13.5), r['gaia_dr3_source_id']))
        selected.append(selection)
    for group in group_order[:11]:
        candidates = [r for r in groups[group] if r['gaia_dr3_source_id'] not in
                      {s['gaia_dr3_source_id'] for s in selected}]
        selected.append(min(candidates, key=lambda r:(abs(r['gmag'] - 16.0), r['gaia_dr3_source_id'])))
    selected.sort(key=lambda r:(r['kinematic_group'],r['gmag']))
    output=[]
    for s in selected:
        def num(x, digits):return f'{x:.{digits}f}'
        output.append({
            'gaia':s['gaia_dr3_source_id'], 'two_mass_id':s['two_mass_id'] or '',
            'name':s['other_name'] or '',
            'ra':num(s['ra_deg'],6),'dec':num(s['dec_deg'],6),
            'reference':s['position_reference'],'sptype':s['adopted_spectral_type'] or '',
            'pmra':num(s['pmra_mas_per_year'],3),'pmdec':num(s['pmdec_mas_per_year'],3),
            'gmag':num(s['gmag'],3),'group':s['kinematic_group'],
            'original_line':str(s['source_line']),
        })
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True,help='Raw full MRT from pinned mirror')
    parser.add_argument('--output',type=Path,default=ROOT/'data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv')
    args=parser.parse_args()
    rows=generate(args.source.read_bytes())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS)
        writer.writeheader();writer.writerows(rows)
    print(f'Wrote {len(rows)} real catalog entries (provisional technical selection, not a scientific sample)')

if __name__=='__main__':main()