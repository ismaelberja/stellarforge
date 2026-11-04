import csv
import json
import numpy as np
import pytest
from stellarforge.association_pipeline import review_raw_target,_centroid
from stellarforge.association import propagate_gaia_position


def test_centroid_handles_ra_wrap():
    ra,dec=_centroid([359.9999,0.0001],[25,25])
    assert min(ra,360-ra)<1e-3
    assert dec==pytest.approx(25,abs=1e-5)


def test_pipeline_keeps_ztf_identity_unconfirmed(tmp_path):
    seed='data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv'
    with open(seed,newline='') as f:target=next(csv.DictReader(f))
    ra,dec=propagate_gaia_position(float(target['ra']),float(target['dec']),
                                   float(target['pmra']),float(target['pmdec']),2021.)
    file=tmp_path/'SYNTHETIC_TEST_ZTF.csv'
    with file.open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['oid','fid','mjd','mag','magerr','catflags','ra','dec'])
        for k in range(60):
            w.writerow(['99987',1,59214+k*.2,14+.04*np.sin(k/4),.015,0,ra,dec])
    output=tmp_path/'review.json'
    d=review_raw_target(seed,target['gaia'],file,output)
    assert d['data_status']=='SYNTHETIC_EXAMPLE_NOT_OBSERVATIONAL_DATA'
    assert d['qc']['kept_rows']==60
    assert d['position_screen']['status']=='positional_candidates_require_independent_review'
    assert not d['position_screen']['astrometric_match_verified']
    assert not d['all_associations_confirmed']
    assert json.loads(output.read_text())['raw_sha256']==d['raw_sha256']


def test_unknown_gaia_id_rejected(tmp_path):
    with pytest.raises(ValueError):
        review_raw_target('data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv','1234',
                          'examples/SYNTHETIC_ZTF_ONLY.csv',tmp_path/'out.json')