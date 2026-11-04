import csv
import hashlib
import json
from pathlib import Path

import pytest

from stellarforge.observational_dossier import (
    build_target_dossier, describe_payload_provenance, write_project_evidence_dashboard,
)

ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/'data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv'


def test_missing_data_must_remain_unknown(tmp_path):
    out=tmp_path/'dossier.json'
    d=build_target_dossier(SEED,'FT Tau',output=out)
    assert d['status']=='OFFICIAL_IRSA_PHOTOMETRY_PENDING'
    assert d['raw_photometry'] is None
    assert d['IRSA_actual_coverage_known'] is False
    assert d['scientific_detection_count'] is None
    assert d['physical_classification'] is None
    assert d['ztf_counterpart_confirmed'] is False
    assert json.loads(out.read_text())['status']==d['status']


def test_both_pre_registered_targets_exist():
    for name in ('FT Tau','CIDA 11'):
        d=build_target_dossier(SEED,name)
        assert d['gaia_dr3_source_id'].isdigit()
        assert 'POS=CIRCLE+' in d['official_query_url']
        assert d['catalog_mirror_has_publisher_byte_comparison'] is False
        assert not any(d['research_gates'].values())


def test_unrecognized_name_rejected():
    with pytest.raises(ValueError):
        build_target_dossier(SEED,'NOT_A_TAURUS_TARGET')


@pytest.mark.parametrize('radius', [-2,0,10.01,float('nan')])
def test_invalid_search_radius(radius):
    with pytest.raises(ValueError):
        build_target_dossier(SEED,'FT Tau',radius_arcsec=radius)


@pytest.mark.parametrize('min_epochs',[0,2,3.5,'30'])
def test_invalid_minimum_epochs(min_epochs):
    with pytest.raises(ValueError):
        build_target_dossier(SEED,'FT Tau',min_good_epochs=min_epochs)


def make_raw(tmp_path, n=5, *, oid='123', ra=65.913324, dec=24.937195, flagged=0):
    f=tmp_path/'candidate.csv'
    head='oid,mjd,mag,magerr,filtercode,catflags,ra,dec\n'
    records=''.join(f'{oid},{59000+i},13.5,0.02,zg,{flagged},{ra},{dec}\n' for i in range(n))
    f.write_text(head+records)
    return f


def test_manual_unattributed_file_not_irsa(tmp_path):
    f=make_raw(tmp_path,40)
    d=build_target_dossier(SEED,'FT Tau',raw_path=f)
    assert d['status']=='LOCAL_PHOTOMETRY_NOT_AUTHENTICATED_AS_IRSA'
    assert d['raw_photometry']['qc_accepted']==40
    assert d['epoch_astrometry']['n_provisionally_in_radius']==1
    assert d['scientific_detection_count'] is None


def test_all_flagged_records_still_not_negative_detection(tmp_path):
    f=make_raw(tmp_path,n=10,flagged=32768)
    d=build_target_dossier(SEED,'FT Tau',raw_path=f)
    assert d['status']=='NO_USABLE_POINTS_IN_PROVIDED_RAW_RESPONSE'
    assert d['raw_photometry']['qc_rejected']==10
    assert d['IRSA_actual_coverage_known'] is False
    assert d['scientific_detection_count'] is None


def write_claim(f,url,**overrides):
    data={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'url':url,
          'status':'unvalidated_raw_response'}
    data.update(overrides)
    Path(str(f)+'.provenance.json').write_text(json.dumps(data))


def test_sidecar_same_sha_not_independent_authentication(tmp_path):
    f=make_raw(tmp_path,n=35)
    write_claim(f,'https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?ID=123')
    d=build_target_dossier(SEED,'FT Tau',raw_path=f)
    assert d['status']=='RAW_PRELIMINARY_QC_PASSED_IDENTITY_REVIEW_REQUIRED'
    assert not d['raw_photometry']['provenance']['independently_authenticated_as_IRSA']
    assert not d['research_gates']['official_IRSA_response_acquired_and_authenticated']
    assert not d['ztf_counterpart_confirmed']


def test_too_few_epoch_hold(tmp_path):
    f=make_raw(tmp_path,n=8)
    write_claim(f,'https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?ID=123')
    d=build_target_dossier(SEED,'FT Tau',raw_path=f)
    assert d['status']=='INSUFFICIENT_EPOCHS_FOR_PRELIMINARY_ANALYSIS'


def test_multiple_oids_same_band_hold(tmp_path):
    f=tmp_path/'ambiguous.csv'
    f.write_text('oid,mjd,mag,magerr,filtercode,catflags,ra,dec\n'+
                ''.join(f'{oid},{59000+i},13.5,0.02,zg,0,65.913324,24.937195\n'
                        for oid in ('101','102') for i in range(32)))
    write_claim(f,'https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE+65+24+.001')
    d=build_target_dossier(SEED,'FT Tau',raw_path=f)
    assert d['status']=='AMBIGUOUS_MULTIPLE_OIDS_REQUIRE_MANUAL_REVIEW'
    assert d['epoch_astrometry']['ambiguous_bands']==['g']


def test_sha_tampering_fails_closed(tmp_path):
    f=make_raw(tmp_path)
    write_claim(f,'https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?ID=123')
    f.write_text(f.read_text().replace('13.5','13.6'))
    with pytest.raises(ValueError,match='SHA256'):
        describe_payload_provenance(f)


@pytest.mark.parametrize('url', [
    'https://attacker.example/cgi-bin/ZTF/nph_light_curves?ID=123',
    'http://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?ID=123',
    'https://irsa.ipac.caltech.edu.attacker.example/cgi-bin/ZTF/nph_light_curves?ID=123',
    'https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves_bad?ID=123',
    'https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves',
])
def test_fake_irsa_claim_not_trusted(tmp_path,url):
    f=make_raw(tmp_path)
    write_claim(f,url)
    assert describe_payload_provenance(f)['status']=='NON_OFFICIAL_OR_UNATTRIBUTED_SOURCE'


def test_raw_empty_rejected(tmp_path):
    f=tmp_path/'empty.csv';f.write_bytes(b'')
    with pytest.raises(ValueError):
        describe_payload_provenance(f)


def test_empty_irsa_urls_not_source_proof(tmp_path):
    f=make_raw(tmp_path)
    write_claim(f,'https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?ID=123')
    a=describe_payload_provenance(f)
    assert a['status']=='IRSA_URL_CLAIM_WITH_INTEGRITY_CHECK_NOT_AUTHENTICATED'
    assert a['independently_authenticated_as_IRSA'] is False


def test_dashboard_does_not_claim_scientific_detections(tmp_path):
    a=build_target_dossier(SEED,'FT Tau')
    b=build_target_dossier(SEED,'CIDA 11')
    p=tmp_path/'report.html'
    report=write_project_evidence_dashboard([a,b],p)
    html=p.read_text()
    assert '<!doctype html>' in html
    assert 'Official IRSA query' in html
    assert 'FT Tau' in html and 'CIDA 11' in html
    assert report['astrophysical_detections_claimed']==0
    assert 'No official ZTF light curve is treated as acquired' in html


def test_dashboard_duplicate_gaia_rejected(tmp_path):
    d=build_target_dossier(SEED,'FT Tau')
    with pytest.raises(ValueError):
        write_project_evidence_dashboard([d,d],tmp_path/'bad.html')


def test_dashboard_html_escape_prevents_markup_injection(tmp_path):
    d=build_target_dossier(SEED,'FT Tau')
    d['target']='<script>alert(1)</script>'
    p=tmp_path/'safe.html'
    write_project_evidence_dashboard([d],p)
    assert '<script>' not in p.read_text()
    assert '&lt;script&gt;' in p.read_text()