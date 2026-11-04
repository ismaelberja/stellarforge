"""All observations used here are synthetic; never infer astronomical discoveries."""
import numpy as np
import pytest
from stellarforge.vetting import FieldControl,field_control_evidence,review_multiband_event_candidates


def make(seed=32,mode='fading',amp=.55):
    rng=np.random.default_rng(seed)
    t=np.arange(0,100,0.5)
    y=14+rng.normal(0,.014,len(t))
    if mode=='fading':y[(t>=35)&(t<=38)]+=amp
    if mode=='brightening':y[(t>=35)&(t<=38)]-=amp
    return t,y,np.full(len(t),.014)


def cur(oid='1001',mode='fading',seed=42):
    t,y,e=make(seed,mode)
    return {'oid':oid,'time_scale':'MJD','time':t,'mag':y,'magerr':e}


def refs(shift='none',seed=3):
    result=[]
    for i in range(4):
        t,y,e=make(seed+i,'none')
        if shift=='fading':y[(t>=35)&(t<=38)]+=.50
        if shift=='brightening':y[(t>=35)&(t<=38)]-=.50
        result.append(FieldControl(f'control-{i}',tuple(t),tuple(y),tuple(e),True,True))
    return result


def run(kind='fading',controls_kind='none',with_r=True,verified=True):
    curves={'g':cur('1001',kind)}
    controls={'g':refs(controls_kind)}
    if with_r:
        curves['r']=cur('2001',kind,seed=52)
        controls['r']=refs(controls_kind,seed=17)
    return review_multiband_event_candidates(curves,controls,
                    source_identity_status='independently_vetted' if verified else 'unverified')


def test_true_dual_band_candidate_is_not_physical_confirmation():
    x=run()
    assert x['n_raw_candidate_events']==2
    assert {v['review_priority'] for v in x['findings']}=={'multi_band_candidate_requires_physical_review'}
    assert all(not v['astrophysical_origin_confirmed'] for v in x['findings'])
    assert x['scientific_detection_count'] is None


def test_shared_calibration_artifact_vetoed_even_if_dual_band():
    x=run(controls_kind='fading')
    assert x['n_raw_candidate_events']==2
    assert {v['review_priority'] for v in x['findings']}=={'veto_suspected_field_calibration_artifact'}


def test_no_controls_cannot_pass():
    x=review_multiband_event_candidates({'g':cur(),'r':cur('2001',seed=52)},{},source_identity_status='independently_vetted')
    assert {v['review_priority'] for v in x['findings']}=={'hold_controls_inconclusive'}


def test_single_band_requires_followup():
    x=run(with_r=False)
    assert x['findings'][0]['review_priority']=='single_band_event_requires_followup'


def test_source_unverified_stays_on_hold():
    x=run(verified=False)
    assert {v['review_priority'] for v in x['findings']}=={'hold_astrometry_and_image_review'}


def test_noise_has_no_events():
    x=run(kind='none')
    assert x['n_raw_candidate_events']==0


def test_independent_band_has_no_event():
    x=review_multiband_event_candidates({'g':cur(),'r':cur('2001','none')},{'g':refs(),'r':refs()},source_identity_status='independently_vetted')
    assert x['n_raw_candidate_events']==1
    assert x['findings'][0]['review_priority']=='single_band_event_requires_followup'


def test_wrong_direction_field_controls_do_not_veto():
    x=run(controls_kind='brightening')
    assert {v['review_priority'] for v in x['findings']}=={'multi_band_candidate_requires_physical_review'}


def test_unvetted_controls_not_trusted():
    control=refs()
    bad=[FieldControl(c.source_id,c.times,c.magnitudes,c.errors,False,False) for c in control]
    e=field_control_evidence(35,38,'fading',bad)
    assert e['status']=='insufficient_independent_field_controls'


def test_duplicate_control_rejected():
    c=refs()[0]
    with pytest.raises(ValueError):field_control_evidence(35,38,'fading',[c,c])


def test_mismatched_time_conventions_rejected():
    second=cur('2001');second['time_scale']='HJD'
    with pytest.raises(ValueError):review_multiband_event_candidates({'g':cur(),'r':second},{})


def test_same_oid_cross_filter_rejected():
    with pytest.raises(ValueError):review_multiband_event_candidates({'g':cur(),'r':cur('1001')},{})


def test_nonmonotonic_bad_photometry():
    c=cur();c['time']=c['time'][::-1]
    with pytest.raises(ValueError):review_multiband_event_candidates({'g':c},{})


def test_invalid_tolerance():
    with pytest.raises(ValueError):review_multiband_event_candidates({'g':cur()},{},tolerance_days=-1)