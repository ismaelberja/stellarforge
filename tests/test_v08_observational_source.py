"""Fully synthetic fixtures. No simulated data presented as real science."""
import csv
import hashlib
import io
import json
import pytest
from stellarforge.observational_release import inspect_observational_source
from stellarforge.readiness import build_readiness_ledger

SAMPLE_URL='https://example.org/secondary/ztf_demo.csv'
API='https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE+10+20+0.0005&FORMAT=CSV'


def fixture():
    buff=io.StringIO()
    w=csv.writer(buff)
    w.writerow(['oid','filtercode','mjd','hjd','mag','magerr','catflags','ra','dec'])
    for i in range(9):
        w.writerow(['22222222222222','zr',58300+i,2458300.5+i+.004,16.2+0.01*i,.03,
                    32768 if i==2 else 0,10,20])
    return buff.getvalue().encode()


def test_secondary_audit_retains_science_gate(tmp_path):
    raw=fixture();p=tmp_path/'raw.csv';p.write_bytes(raw)
    d=tmp_path/'result'
    x=inspect_observational_source(p,d,origin='secondary_public_example',source_url=SAMPLE_URL,
                                   expected_sha256=hashlib.sha256(raw).hexdigest())
    assert x['status']=='secondary_format_integration_test_not_taurus'
    assert x['raw_rows']==9 and x['qc_accepted']==8 and x['qc_rejected']==1
    assert x['rejections']=={'masked_catflags':1}
    assert x['audited_curves'][0]['band']=='r'
    assert x['audited_curves'][0]['time_scale']=='MJD'
    assert x['cadence_by_curve'][0]['analysis_eligibility']=='insufficient_epochs'
    assert x['taurus_lightcurves_verified']==0
    assert x['physical_classification_issued'] is False
    assert json.loads((d/'OBSERVATIONAL_AUDIT.json').read_text())['raw_sha256']==x['raw_sha256']


def test_detects_tampered_observational_file(tmp_path):
    p=tmp_path/'x.csv';p.write_bytes(fixture())
    with pytest.raises(ValueError,match='SHA-256'):
        inspect_observational_source(p,tmp_path/'out',origin='secondary_public_example',
                                     source_url=SAMPLE_URL,expected_sha256='0'*64)
    assert not (tmp_path/'out').exists()


def test_secondary_target_assignment_forbidden(tmp_path):
    p=tmp_path/'x.csv';p.write_bytes(fixture())
    with pytest.raises(ValueError,match='cannot be assigned'):
        inspect_observational_source(p,tmp_path/'out',origin='secondary_public_example',
                                  source_url=SAMPLE_URL,target_name='FT Tau')


def test_direct_irsa_requires_sidecar(tmp_path):
    p=tmp_path/'x.csv';p.write_bytes(fixture())
    with pytest.raises(ValueError,match='provenance'):
        inspect_observational_source(p,tmp_path/'out',origin='direct_irsa',source_url=API)


def test_direct_irsa_requires_hash_url_equivalence(tmp_path):
    p=tmp_path/'x.csv';p.write_bytes(fixture())
    (tmp_path/'x.csv.provenance.json').write_text(json.dumps({'url':API,'sha256':'wrong'}))
    with pytest.raises(ValueError,match='hash or URL mismatch'):
        inspect_observational_source(p,tmp_path/'out',origin='direct_irsa',source_url=API)


def test_direct_irsa_inspection_still_unverified_match(tmp_path):
    p=tmp_path/'x.csv';p.write_bytes(fixture())
    (tmp_path/'x.csv.provenance.json').write_text(json.dumps({'url':API,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
    x=inspect_observational_source(p,tmp_path/'out',origin='direct_irsa',source_url=API,
                                   target_name='test object',target_ra=10,target_dec=20)
    assert x['status']=='observations_ingested_crossmatch_not_yet_verified'
    assert x['taurus_lightcurves_verified']==0
    assert not x['physical_classification_issued']


@pytest.mark.parametrize('bad_url',['http://example.org/foo','ftp://a/b','https://user:pass@site/foo','abc'])
def test_untrusted_provenance_url_refused(tmp_path,bad_url):
    p=tmp_path/'x.csv';p.write_bytes(fixture())
    with pytest.raises(ValueError,match='HTTPS'):
        inspect_observational_source(p,tmp_path/'out',origin='secondary_public_example',source_url=bad_url)


def test_source_schema_gates_no_code_execution(tmp_path):
    p=tmp_path/'x.csv';p.write_text('<html>server error</html>')
    with pytest.raises(ValueError):
        inspect_observational_source(p,tmp_path/'out',origin='secondary_public_example',source_url=SAMPLE_URL)


def test_24_source_readiness_ledger(tmp_path):
    from pathlib import Path
    source=Path(__file__).parents[1]/'data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv'
    x=build_readiness_ledger(source,tmp_path/'ledger')
    assert x['technical_taurus_catalog_rows']==24
    assert x['named_kinematic_groups']==13
    assert x['ztf_observations_imported_for_taurus']==0
    assert set(x['priority_pilot_names'])=={'FT Tau','CIDA 11'}
    assert len(set(s['gaia_dr3_source_id'] for s in x['catalogue_members_for_planning_only']))==24
    assert len([s for s in x['catalogue_members_for_planning_only'] if s['pilot_priority']=='pilot_pre_registered'])==2
    assert all(not s['ztf_data_present'] and not s['source_image_crossmatch_checked'] for s in x['catalogue_members_for_planning_only'])