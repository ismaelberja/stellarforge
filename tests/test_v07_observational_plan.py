import csv
import json
from pathlib import Path
import pytest
from stellarforge.observational_plan import make_pilot_plan, save_pilot_plan

ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/'data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv'


def test_real_taurus_seed_two_targets_and_provenance():
    result=make_pilot_plan(SEED)
    assert result['status']=='PRE_REGISTERED_CATALOG_PILOT_UNEXECUTED'
    assert result['seed_audit']['rows']==24
    assert len(result['pilot_targets'])==2
    assert [x['catalog_name'] for x in result['pilot_targets']]==['FT Tau','CIDA 11']
    assert len({x['kinematic_group'] for x in result['pilot_targets']})==2
    for t in result['pilot_targets']:
        assert t['gaia_dr3_source_id'].isdigit()
        assert t['irsa_observations_received']==0
        assert t['ztf_api_query_url'].startswith('https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?')
        assert 'BAD_CATFLAGS_MASK=32768' in t['ztf_api_query_url']
        assert t['catalog_ra_deg'] != t['illustrative_propagated_ra_deg']
        assert not t['ztf_source_association_confirmed']
    assert result['new_observational_claims']==0


@pytest.mark.parametrize('targets', [(),('FT Tau','FT Tau'),('unknown',),('x','y','z','a','b','c')])
def test_wrong_targets_rejected(targets):
    with pytest.raises(ValueError):make_pilot_plan(SEED,targets)


@pytest.mark.parametrize('radius', [-1.,0.,11.])
def test_bad_radius_rejected(radius):
    with pytest.raises(ValueError):make_pilot_plan(SEED,radius_arcsec=radius)


def test_save_read_is_repeatable(tmp_path):
    plan=make_pilot_plan(SEED)
    filename=tmp_path/'pilot.json'
    save_pilot_plan(filename,plan)
    assert json.loads(filename.read_text())==plan
    assert not (tmp_path/'pilot.json.partial').exists()


def test_seed_modified_to_other_position_source_is_rejected(tmp_path):
    with SEED.open(newline='') as f:
        r=csv.DictReader(f); rows=list(r); names=r.fieldnames
    row=next(x for x in rows if x['name']=='FT Tau')
    row['reference']='2MASS'
    target=tmp_path/'seed.csv'
    with target.open('w',newline='') as o:
        w=csv.DictWriter(o,fieldnames=names);w.writeheader();w.writerows(rows)
    with pytest.raises(ValueError): make_pilot_plan(target)