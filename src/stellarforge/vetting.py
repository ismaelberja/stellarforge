"""Conservative v0.6 event vetting, using multi-band and local-field controls.

Scientific intent: screen suspicious episodes for REVIEW, not classify YSOs.
Correlated field-star excursions are an instrumental warning. Simultaneous
multi-band behavior alone is not a proof of astrophysical origin.

WARNING: controls must be independent vetted stars on comparable calibrated
exposures in the same field. This module cannot establish these associations;
they are inputs with a documented upstream quality/identity gate.
"""
from __future__ import annotations

from dataclasses import asdict,dataclass
import math
from typing import Mapping

from .events import screen_events


@dataclass(frozen=True)
class FieldControl:
    """One star, one filter, one time convention. Never merge ZTF OIDs."""
    source_id: str
    times: tuple[float, ...]
    magnitudes: tuple[float, ...]
    errors: tuple[float, ...]
    association_vetted: bool = False
    same_field_and_calibration: bool = False


def _arrays(time,mag,errors):
    import numpy as np
    t,y,e=(np.asarray(v,dtype=float) for v in (time,mag,errors))
    if not len(t) or t.ndim!=1 or y.shape!=t.shape or e.shape!=t.shape:
        raise ValueError('Times, magnitudes and errors must align')
    if any(not np.all(np.isfinite(x)) for x in (t,y,e)) or np.any(e<=0):
        raise ValueError('Invalid photometry or uncertainty')
    if np.any(np.diff(t)<=0):
        raise ValueError('Times must be strictly increasing')
    return t,y,e


def field_control_evidence(start:float,end:float,direction:str,controls:list[FieldControl],
                           *,min_controls:int=3,min_points_inside:int=2,
                           min_points_outside:int=15,amplitude_threshold_mag:float=.12,
                           time_tolerance_days:float=.75)->dict:
    """Look for the SAME SIGN of an event in neighboring independent controls.

    No controls or unvetted controls means *unknown*, never clear.
    A majority coherent response means suspected field systematic, even if
    g and r target series display the same dip/burst.
    """
    import numpy as np
    if not all(math.isfinite(v) for v in (start,end,amplitude_threshold_mag,time_tolerance_days)) or end<start:
        raise ValueError('Bad event interval or thresholds')
    if direction not in ('fading','brightening') or min_controls<3 or min_points_inside<2 or min_points_outside<4:
        raise ValueError('Invalid control-screen settings')
    if amplitude_threshold_mag<=0 or time_tolerance_days<0:
        raise ValueError('Invalid control thresholds')
    if len({c.source_id for c in controls})!=len(controls):
        raise ValueError('Duplicate field control star identifier')
    results=[]
    for control in controls:
        if not control.association_vetted or not control.same_field_and_calibration:
            results.append({'control_source':control.source_id,'status':'unvetted_control'})
            continue
        t,y,e=_arrays(control.times,control.magnitudes,control.errors)
        in_event=(t>=start-time_tolerance_days)&(t<=end+time_tolerance_days)
        outside=~in_event
        if sum(in_event)<min_points_inside or sum(outside)<min_points_outside:
            results.append({'control_source':control.source_id,'status':'insufficient_control_cadence'})
            continue
        # Median difference is robust to isolated bad measurements, but can
        # still be fooled by coherent variables or seasonally drifting zeropoints.
        shift=float(np.median(y[in_event])-np.median(y[outside]))
        signed=shift if direction=='fading' else -shift
        results.append({'control_source':control.source_id,'status':'usable',
                        'signed_event_shift_mag':round(signed,5),
                        'same_direction_systematic':bool(signed>=amplitude_threshold_mag),
                        'n_inside':int(sum(in_event)),'n_outside':int(sum(outside))})
    valid=[c for c in results if c['status']=='usable']
    n_coherent=sum(x['same_direction_systematic'] for x in valid)
    if len(valid)<min_controls:
        status='insufficient_independent_field_controls'
    elif n_coherent >= 2 and n_coherent >= math.ceil(len(valid)*.5):
        status='suspected_field_systematic_veto'
    elif n_coherent:
        status='mixed_controls_inconclusive'
    else:
        status='no_coherent_field_shift_in_tested_controls'
    return {'status':status,'n_controls_supplied':len(controls),
            'n_controls_usable':len(valid),'n_controls_same_direction':n_coherent,
            'controls':results,'no_physical_cause_inferred':True}


def _events_overlap(a:Mapping,b:Mapping,tolerance_days:float)->bool:
    return (float(a['start_time'])<=float(b['end_time'])+tolerance_days and
            float(b['start_time'])<=float(a['end_time'])+tolerance_days)


def review_multiband_event_candidates(curves:Mapping[str,Mapping],
                                     controls:Mapping[str,list[FieldControl]],
                                     *,tolerance_days:float=1.0,
                                     source_identity_status:str='unverified',
                                     min_epochs:int=30)->dict:
    """Screen per-band events, consensus and controls with conservative statuses.

    Input curves: {'g': {oid, time_scale, time, mag, magerr}, 'r': ...};
    missing bands are permitted and explicitly marked as inconclusive.
    All input times must share the same convention; no HJD/MJD arithmetic.
    A positive review status is NOT a confirmed member/dipper/burster.
    """
    if not math.isfinite(tolerance_days) or not 0<=tolerance_days<=5:
        raise ValueError('Invalid coincidence tolerance')
    if not isinstance(min_epochs,int) or min_epochs<10:
        raise ValueError('Invalid minimum epochs')
    if not curves or not set(curves)<={'g','r','i'}:
        raise ValueError('Expected one or more g/r/i curves')
    names=[str(x['oid']) for x in curves.values()]
    if len(set(names))!=len(names):
        raise ValueError('Distinct passbands require separately identified OIDs')
    scales={str(x['time_scale']).upper() for x in curves.values()}
    if len(scales)!=1 or list(scales)[0] not in ('MJD','HJD','HMJD'):
        raise ValueError('Incompatible or unknown astronomical time conventions')
    for b,ctl in controls.items():
        if b not in curves or not isinstance(ctl,list):
            raise ValueError('Controls must be keyed by target band')
    per_band={}
    event_list=[]
    for band,curve in sorted(curves.items()):
        t,y,e=_arrays(curve['time'],curve['mag'],curve['magerr'])
        result=screen_events(t,y,e,min_epochs=min_epochs)
        per_band[band]={'oid':str(curve['oid']),'screen_status':result['status'],
                        'n_epochs':len(t),'candidate_count':len(result['fading_events'])+len(result['brightening_events'])}
        for direction,key in [('fading','fading_events'),('brightening','brightening_events')]:
            for event in result[key]:
                event_list.append((band,event))
    findings=[]
    for band,event in event_list:
        companions=[{'band':otherband,'oid':str(curves[otherband]['oid']),
                     'start_time':other['start_time'],'end_time':other['end_time']}
                    for otherband,other in event_list
                    if otherband!=band and other['direction']==event['direction']
                    and _events_overlap(event,other,tolerance_days)]
        control_evidence=field_control_evidence(event['start_time'],event['end_time'],event['direction'],controls.get(band,[]))
        control_states=[control_evidence['status']]
        if companions:
            for c in companions:
                ev=next(e for b,e in event_list if b==c['band'] and e['start_time']==c['start_time']
                        and e['end_time']==c['end_time'] and e['direction']==event['direction'])
                cp=field_control_evidence(ev['start_time'],ev['end_time'],ev['direction'],controls.get(c['band'],[]))
                control_states.append(cp['status'])
        if 'suspected_field_systematic_veto' in control_states:
            priority='veto_suspected_field_calibration_artifact'
        elif any(s!='no_coherent_field_shift_in_tested_controls' for s in control_states):
            priority='hold_controls_inconclusive'
        elif not companions:
            priority='single_band_event_requires_followup'
        elif source_identity_status!='independently_vetted':
            priority='hold_astrometry_and_image_review'
        else:
            priority='multi_band_candidate_requires_physical_review'
        findings.append({'band':band,'oid':str(curves[band]['oid']),
                         'direction':event['direction'],'start_time':event['start_time'],
                         'end_time':event['end_time'],'n_trigger_epochs':event['n_epochs'],
                         'max_excursion_mag':event['max_magnitude_excursion'],
                         'independent_band_support':companions,
                         'controls':control_evidence,
                         'control_statuses_across_supporting_bands':control_states,
                         'review_priority':priority,
                         'astrophysical_origin_confirmed':False,
                         'physical_dipper_or_burster_classification':None})
    return {'method':'v0.6_multiband_field_control_vetting',
            'time_convention':next(iter(scales)),
            'source_identity_status':source_identity_status,
            'bands':per_band,'n_raw_candidate_events':len(findings),
            'findings':findings,
            'scientific_detection_count':None,
            'discovery_claim':False,
            'limitations':[
                'Shared field-calibration excursions can imitate multi-band astrophysical events.',
                'A quiet field control is not proof of source association or an astrophysical cause.',
                'Observation gaps and asynchronous bands can hide real events.',
                'Control stars must be independently vetted and observed under comparable conditions.',
                'Manual image, astrometric covariance, blending and source-identity reviews remain required.',
            ]}