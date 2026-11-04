"""Full v0.9 orchestration tests use mocked network and synthetic CSV payloads."""
from pathlib import Path
import hashlib
import json
import sys
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from run_v09_pipeline import run, SEED


def test_offline_pilot_yields_two_dossiers(tmp_path):
    r=run(seed=SEED,output=tmp_path)
    assert r['n_targets']==2
    assert r['network_mode']=='OFFLINE_ONLY'
    assert r['dossier_status']=={'FT Tau':'OFFICIAL_IRSA_PHOTOMETRY_PENDING',
                                 'CIDA 11':'OFFICIAL_IRSA_PHOTOMETRY_PENDING'}
    assert r['physical_dipper_burster_confirmations']==0
    assert len(list(tmp_path.glob('*_EVIDENCE_DOSSIER.json')))==2
    assert (tmp_path/'STELLARFORGE_V09_EVIDENCE_DASHBOARD.html').exists()
    assert (tmp_path/'RUN_SUMMARY.json').exists()
    assert not (tmp_path/'raw').exists()


def test_execute_network_failure_does_not_claim_no_observations(tmp_path):
    seen=[]
    def fake(url,out,timeout_sec):
        seen.append(url)
        raise ConnectionError('OFFLINE test fixture')
    r=run(seed=SEED,output=tmp_path,execute=True,fetcher=fake)
    assert len(seen)==2
    assert all(row['result']=='REQUEST_FAILED_NO_OBSERVATIONAL_CLAIM' for row in r['acquisition'])
    assert all(row['exception_type']=='ConnectionError' for row in r['acquisition'])
    assert all(x=='OFFICIAL_IRSA_PHOTOMETRY_PENDING' for x in r['dossier_status'].values())
    assert r['ztf_official_photometry_confirmed_for_Taurus'] is False


def test_mocked_success_still_does_not_claim_authentication(tmp_path):
    def fake(url,out,timeout_sec):
        out.parent.mkdir(parents=True, exist_ok=True)
        content=('oid,mjd,mag,magerr,filtercode,catflags,ra,dec\n'+
                 ''.join(f'100,{59000+i},14,0.03,zg,0,65.913324,24.937195\n' for i in range(5)))
        out.write_text(content)
        meta={'sha256':hashlib.sha256(out.read_bytes()).hexdigest(), 'url':url}
        Path(str(out)+'.provenance.json').write_text(json.dumps(meta))
        return meta
    r=run(seed=SEED,output=tmp_path,execute=True,fetcher=fake)
    assert all(x['raw_response_present'] for x in r['acquisition'])
    assert r['ztf_official_photometry_confirmed_for_Taurus'] is False
    assert all(x['response_authenticated_by_independent_evidence'] is False for x in r['acquisition'])
    assert (tmp_path/'raw').is_dir()


def test_bad_seed_fails(tmp_path):
    with pytest.raises((ValueError,FileNotFoundError)):
        run(seed=tmp_path/'bad.csv',output=tmp_path/'out')


def test_result_json_has_no_spurious_detection(tmp_path):
    run(seed=SEED,output=tmp_path)
    obj=json.loads((tmp_path/'RUN_SUMMARY.json').read_text())
    assert obj['physical_dipper_burster_confirmations']==0
    assert 'network_attempted' in obj['acquisition'][0]
    assert obj['acquisition'][0]['network_attempted'] is False


def test_cached_response_never_retrieved_twice(tmp_path):
    calls=[]
    def fake(url,out,timeout_sec):
        calls.append(url)
        out.parent.mkdir(parents=True,exist_ok=True)
        raw='oid,mjd,mag,magerr,filtercode,catflags,ra,dec\n100,59000,14,0.03,zg,0,65.913324,24.937195\n'
        out.write_text(raw)
        Path(str(out)+'.provenance.json').write_text(json.dumps({'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'url':url}))
        return {'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'url':url}
    first=run(seed=SEED,output=tmp_path,execute=True,fetcher=fake)
    second=run(seed=SEED,output=tmp_path,execute=True,fetcher=fake)
    assert len(calls)==2
    assert not any(x['network_attempted'] for x in second['acquisition'])
    assert all(x['result']=='CACHED_RAW_RESPONSE_WITH_VERIFIED_INTEGRITY' for x in second['acquisition'])


def test_cache_hash_tamper_rejects_overwrite(tmp_path):
    def fake(url,out,timeout_sec):
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text('oid,mjd,mag,magerr,filtercode,catflags,ra,dec\n100,59000,14,0.03,zg,0,65.913324,24.937195\n')
        Path(str(out)+'.provenance.json').write_text(json.dumps({'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'url':url}))
        return {'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'url':url}
    run(seed=SEED,output=tmp_path,execute=True,fetcher=fake)
    original=tmp_path/'raw'/'149623711269425408.csv'
    original.write_text(original.read_text().replace('14,','15,'))
    with pytest.raises(Exception,match='cached provenance'):
        run(seed=SEED,output=tmp_path,execute=True,fetcher=fake)
    assert '15,' in original.read_text()