"""Standalone, read-only two-target IRSA pilot for private GitHub Actions.

The downloaded photometry is unverified source-association evidence, *not*
proof that a Gaia Taurus member is variable. No raw observations enter Git.
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API = 'https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves'
TARGETS = (
    ('FT Tau', '149623711269425408', 65.913324, 24.937195),
    ('CIDA 11', '3419110734340795648', 76.597253, 24.538792),
)
REQUIRED = {'oid','mjd','mag','magerr','catflags','filtercode'}


def make_url(ra: float, dec: float, radius_arcsec: float = 2.) -> str:
    if not 0 <= ra < 360 or not -90 <= dec <= 90 or not .1 <= radius_arcsec <= 10:
        raise ValueError('Invalid pre-registered target coordinates/radius')
    params = {
        'POS': f'CIRCLE {ra:.6f} {dec:.6f} {radius_arcsec/3600:.9f}',
        'BANDNAME':'g,r', 'BAD_CATFLAGS_MASK':'32768', 'FORMAT':'csv',
    }
    return API+'?'+urlencode(params)


def inspect_response(raw: bytes) -> dict:
    """Only summarize raw format and photometric QC, never source identity."""
    if len(raw)>20_000_000 or not raw.strip():
        raise ValueError('Empty/oversized response')
    text=raw.decode('utf-8-sig')
    if text.lstrip().startswith(('<', '{')):
        raise ValueError('HTML, XML or JSON response, not ZTF CSV')
    rows=list(csv.DictReader(io.StringIO(text)))
    if not rows:
        # A header-only response is not evidence that the star is non-variable.
        return {'rows':0,'qc_accepted':0,'distinct_oid_bands':[],
                'status':'NO_ROWS_RETURNED_COVERAGE_UNKNOWN'}
    names=set(rows[0]);missing=REQUIRED-names
    if missing:raise ValueError('Missing photometry fields: '+','.join(sorted(missing)))
    accepted=0;groups=set();rejected=0
    for row in rows:
        try:
            oid=str(row['oid']).strip();band=str(row['filtercode']).strip()
            mjd=float(row['mjd']);mag=float(row['mag']);err=float(row['magerr'])
            flags=int(row['catflags'])
            if (not oid.isdigit() or band not in {'zg','zr','zi','g','r','i'}
                or not (math.isfinite(mjd) and math.isfinite(mag) and math.isfinite(err))
                or not 40000<mjd<90000 or not 0<err<10 or flags&32768):
                rejected+=1;continue
            groups.add((oid,band));accepted+=1
        except (KeyError,TypeError,ValueError):
            rejected+=1
    return {'rows':len(rows),'qc_accepted':accepted,'qc_rejected':rejected,
            'distinct_oid_bands':[{'oid':x,'band':y} for x,y in sorted(groups)],
            'status':'RAW_FORMAT_QC_ONLY_SOURCE_ASSOCIATION_UNVERIFIED'}


def run(outdir: Path, fetcher=None) -> dict:
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    fetcher = fetcher or _fetch
    outcomes=[]
    for name,gaia_id,ra,dec in TARGETS:
        url=make_url(ra,dec)
        info={'target':name,'gaia_dr3_id':gaia_id,'catalog_ra_deg':ra,
              'catalog_dec_deg':dec,'official_url':url,
              'official_source_association_confirmed':False,
              'astrophysical_variability_claimed':False}
        try:
            raw=fetcher(url)
            info['inspection']=inspect_response(raw)
            p=outdir/f'{gaia_id}_IRSA_RAW.csv'
            p.write_bytes(raw)
            info['raw_sha256']=hashlib.sha256(raw).hexdigest()
            info['raw_bytes']=len(raw)
            info['acquisition_status']='RAW_HTTP_RESPONSE_SAVED_ASSOCIATION_UNVERIFIED'
        except Exception as exc:
            # No raw payload, no assertion of missing sky coverage.
            info['acquisition_status']='REQUEST_FAILED_OR_FORMAT_UNVERIFIED'
            info['exception_type']=type(exc).__name__
        outcomes.append(info)
    audit={'schema_version':'stellarforge-pilot-1.0',
           'catalog':'Luhman 2023 secondary mirror; original publisher comparison pending',
           'raw_photometry_responses':sum('raw_sha256'in v for v in outcomes),
           'verified_gaia_ztf_crossmatches':0,'physical_detections':0,
           'source_release_independently_authenticated':False,
           'results':outcomes}
    (outdir/'PILOT_STATUS.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    md=['# StellarForge — private IRSA acquisition pilot','',
        '> This is an intake experiment, not a stellar-variability discovery.','',
        '| Target | Status | Accepted points | ZTF OID-band groups |',
        '|---|---|---:|---:|']
    for x in outcomes:
        meta=x.get('inspection',{})
        md.append(f'| {x["target"]} | {x["acquisition_status"]} | '
                  f'{meta.get("qc_accepted","n/a")} | '
                  f'{len(meta.get("distinct_oid_bands",[]))} |')
    md += ['','**All OIDs and physical interpretations remain unverified.**',
           'Raw data are stored only in the private CI artifact, not in Git history.','']
    (outdir/'REPORT.md').write_text('\n'.join(md),encoding='utf-8')
    return audit


def _fetch(url):
    req=Request(url,headers={'User-Agent':'StellarForge-Private-Pilot/1.0 (academic research; 2 queries)'})
    with urlopen(req,timeout=60) as resp:
        raw=resp.read(20_000_001)
    if len(raw)>20_000_000:raise ValueError('Response too large')
    return raw


if __name__=='__main__':
    dest=Path(sys.argv[1]) if len(sys.argv)>1 else Path('reports/generated/irsa_pilot')
    x=run(dest)
    print(json.dumps({'raw_responses':x['raw_photometry_responses'],
                      'targets':[(a['target'],a['acquisition_status']) for a in x['results']]},indent=2))