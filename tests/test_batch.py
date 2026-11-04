"""All remote acquisition tests are mocked; no IRSA network traffic."""
import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
import pytest

from stellarforge.batch import CacheConflict, download_one, load_seed, run_batch, target_request, validate_raw_cache

SEED = Path(__file__).resolve().parents[1] / 'data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv'


def test_seed_and_request_have_real_provenance_not_verified_match():
    records = load_seed(SEED)
    assert len(records)==24
    req=target_request(records[0],2)
    assert 'irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?' in req['url']
    assert req['gaia_dr3_source_id']==records[0]['gaia']
    assert req['epoch_correction_applied'] is False
    assert req['astrometric_match_verified'] is False


def test_dry_run_is_safe_and_reproducible(tmp_path):
    res=run_batch(SEED,tmp_path,execute=False)
    assert res['n_targets_in_batch']==24
    assert res['counts']=={'not_executed':24}
    assert res['ztf_target_associations_confirmed']==0
    assert res['observational_discoveries']==0
    assert not (tmp_path/'raw').exists()
    assert json.loads((tmp_path/'BATCH_MANIFEST.json').read_text())['queries'][0]['status']=='not_executed'


def test_limit_prevents_accidental_large_batches(tmp_path):
    with pytest.raises(ValueError):run_batch(SEED,tmp_path,max_targets=200)
    with pytest.raises(ValueError):run_batch(SEED,tmp_path,radius_arcsec=400)
    with pytest.raises(ValueError):run_batch(SEED,tmp_path,pause_between_s=-5)


def make_fake_fetcher(calls, raw=None):
    if raw is None:
        raw=('oid,filtercode,mjd,mag,magerr,catflags,ra,dec\n'
             '999,zr,59000,14.5,0.03,0,63.928341,29.166539\n'
             '999,zr,59003,14.4,0.03,0,63.928341,29.166539\n').encode()
    def fetcher(url, path, *, timeout_sec):
        calls.append(url)
        path.write_bytes(raw)
        data={'url':url,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'content_type':'text/csv'}
        Path(str(path)+'.provenance.json').write_text(json.dumps(data))
        return data
    return fetcher


def test_mocked_download_and_audit_does_not_claim_match(tmp_path):
    calls=[]
    out=run_batch(SEED,tmp_path,execute=True,max_targets=1,fetcher=make_fake_fetcher(calls),pause_between_s=0)
    assert len(calls)==1
    item=out['queries'][0]
    assert item['status']=='unverified_source_association'
    assert item['raw_rows']==2 and item['qc_accepted_rows']==2
    assert item['n_separate_ztf_curves']==1
    assert item['epoch_correction_applied'] is False
    assert out['ztf_target_associations_confirmed']==0


def test_resume_uses_verified_cache(tmp_path):
    calls=[]
    fetcher=make_fake_fetcher(calls)
    run_batch(SEED,tmp_path,execute=True,max_targets=1,fetcher=fetcher,pause_between_s=0)
    second=run_batch(SEED,tmp_path,execute=True,max_targets=1,fetcher=fetcher,pause_between_s=0)
    assert len(calls)==1
    assert second['queries'][0]['retrieval_status']=='cached_verified'


def test_corrupt_cache_rejected_never_overwritten(tmp_path):
    calls=[]
    fetcher=make_fake_fetcher(calls)
    run_batch(SEED,tmp_path,execute=True,max_targets=1,fetcher=fetcher,pause_between_s=0)
    path=next((tmp_path/'raw').glob('*_ztf.csv'))
    path.write_bytes(path.read_bytes()+b'corrupt')
    result=run_batch(SEED,tmp_path,execute=True,max_targets=1,fetcher=fetcher,pause_between_s=0)
    assert result['queries'][0]['status']=='cache_conflict_requires_manual_review'
    assert len(calls)==1


def test_unpaired_cache_conflict(tmp_path):
    p=tmp_path/'data.csv';p.write_text('csv')
    with pytest.raises(CacheConflict):validate_raw_cache(p,'https://irsa.ipac.caltech.edu/a')


def test_transient_error_retry(tmp_path):
    calls=[];actual=make_fake_fetcher(calls)
    state={'n':0}
    def flakey(url,path,*,timeout_sec):
        state['n']+=1
        if state['n']==1:raise URLError('temporary network error')
        return actual(url,path,timeout_sec=timeout_sec)
    row=target_request(load_seed(SEED)[0],2)
    meta,status=download_one(row,tmp_path/'source.csv',fetcher=flakey,delay_s=0,sleep=lambda x:None)
    assert status=='downloaded' and state['n']==2


def test_reject_nonretryable_http_403(tmp_path):
    def reject(url,path,*,timeout_sec):
        raise HTTPError(url,403,'Forbidden',hdrs={},fp=None)
    row=target_request(load_seed(SEED)[0],2)
    with pytest.raises(HTTPError):
        download_one(row,tmp_path/'file.csv',fetcher=reject,delay_s=0,sleep=lambda x:None)


def test_one_failed_target_does_not_cancel_batch(tmp_path):
    def reject(url,path,*,timeout_sec):
        raise HTTPError(url,403,'Forbidden',hdrs={},fp=None)
    result=run_batch(SEED,tmp_path,execute=True,max_targets=2,fetcher=reject,pause_between_s=0,sleep=lambda x:None)
    assert result['counts']=={'download_or_qc_failed':2}
    assert result['queries'][0]['error_class']=='HTTPError'
    assert (tmp_path/'BATCH_MANIFEST.json').is_file()


def test_provenance_wrong_url_conflict(tmp_path):
    calls=[]
    fetcher=make_fake_fetcher(calls)
    row=target_request(load_seed(SEED)[0],2)
    download_one(row,tmp_path/'source.csv',fetcher=fetcher,delay_s=0)
    with pytest.raises(CacheConflict):validate_raw_cache(tmp_path/'source.csv','https://irsa.ipac.caltech.edu/different')