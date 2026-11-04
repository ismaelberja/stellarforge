"""Scientific selection gates; no observation or object-identity claims."""
from pathlib import Path
import csv
import pytest
from stellarforge.selection_bias import GROUP_REFERENCE, audit_seed_selection, wilson_interval

ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/'data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv'


def test_full_reference_counts_and_gaia_missing_group():
    r=audit_seed_selection(SEED)
    assert r['total_members']==532
    assert r['with_gaia_id']==467
    assert r['without_gaia_id']==65
    assert r['gaia_missing_without_group']==64
    assert r['seed_group_coverage']==13
    assert r['g12_17_gaia_with_named_group']==289
    assert r['original_publisher_file_verified'] is False
    assert r['ztf_lightcurves_verified_for_taurus']==0
    assert r['seed_member_disk_classes_verified']==0


def test_reference_group_consistency_and_unassigned():
    assert sum(x[0] for x in GROUP_REFERENCE.values())==532
    assert sum(x[1] for x in GROUP_REFERENCE.values())==467
    assert sum(x[2] for x in GROUP_REFERENCE.values())==314
    assert GROUP_REFERENCE['unassigned'] == (119,55,25)


def test_wilson_interval_edge_cases():
    assert wilson_interval(0,10)[0] == 0
    assert wilson_interval(10,10)[1] == 1
    low,high=wilson_interval(467,532)
    assert low < 467/532 < high
    with pytest.raises(ValueError):wilson_interval(11,10)
    with pytest.raises(ValueError):wilson_interval(0,0)


def test_magnitude_out_of_range_rejected(tmp_path):
    rows=list(csv.DictReader(SEED.open(newline='',encoding='utf-8')))
    rows[0]['gmag']='6.5'
    dest=tmp_path/'bad.csv'
    with dest.open('w',newline='',encoding='utf-8') as fh:
        writer=csv.DictWriter(fh,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
    with pytest.raises(ValueError,match='outside documented'):audit_seed_selection(dest)


def test_duplicate_id_rejected(tmp_path):
    with SEED.open(newline='',encoding='utf-8') as f: rows=list(csv.DictReader(f))
    rows[1]['gaia']=rows[0]['gaia']
    dest=tmp_path/'bad.csv'
    with dest.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
    with pytest.raises(ValueError,match='duplicate'):audit_seed_selection(dest)