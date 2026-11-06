"""v1.9: Gaia DR3 five-parameter formal covariance and annual parallax screen.

Output: *formal* propagated Gaia uncertainty under a specified simplified
barycentric -> Earth-geocentre geometry; NOT Gaia-ZTF source association,
PSF/WCS calibration, instrument noise modeling or validated total astrometry.

Astrometric vector: [alpha, delta, parallax, mu_alpha*, mu_delta].
alpha/delta errors, parallax: mas. Proper-motion errors: mas/year.
Correlations are Gaia DR3's original 5-parameter 10 pairwise coefficients.
No silent diagonal approximation is allowed for missing correlations.

This model is geocentric and first-order in parallax; Gaia radial velocity,
perspective acceleration, aberration, Earth observatory topocentric parallax,
colour/refraction and non-single-star model biases are NOT included.
"""
from __future__ import annotations

import csv
import io
import math
import hashlib
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .association import propagate_gaia_position, MAS_TO_RAD
from .coordinates import validate_icrs
from .v14_field_review import GAIA_TAP_URL

GAIA_PARAM_NAMES = ("ra", "dec", "parallax", "pmra", "pmdec")
GAIA_ERRORS = ("ra_error", "dec_error", "parallax_error",
               "pmra_error", "pmdec_error")
GAIA_CORRELATIONS = (
    "ra_dec_corr", "ra_parallax_corr", "ra_pmra_corr", "ra_pmdec_corr",
    "dec_parallax_corr", "dec_pmra_corr", "dec_pmdec_corr",
    "parallax_pmra_corr", "parallax_pmdec_corr", "pmra_pmdec_corr",
)
GAIA_COLUMNS = (
    "source_id", "ref_epoch", "ra", "dec", "parallax", "pmra", "pmdec",
    "ruwe", "astrometric_params_solved",
    *GAIA_ERRORS, *GAIA_CORRELATIONS,
)
PAIR_INDICES = (
    (0,1), (0,2), (0,3), (0,4), (1,2), (1,3), (1,4),
    (2,3), (2,4), (3,4),
)
MAS_PER_RAD = 1 / MAS_TO_RAD
MAX_TAP_BYTES = 200_000
EXPECTED_GAIA_EPOCH = 2016.0


def make_target_astrometry_adql(source_ids: tuple[str, ...]) -> str:
    """Exact Gaia source IDs only, tiny public TAP query; no sky scan."""
    if not 1 <= len(source_ids) <= 12:
        raise ValueError("Require 1..12 Gaia DR3 IDs")
    if len(set(source_ids)) != len(source_ids) or any(
        not str(i).isdigit() or not (15 <= len(str(i)) <= 20) for i in source_ids
    ):
        raise ValueError("Duplicate/invalid Gaia source ID")
    return (f"SELECT {', '.join(GAIA_COLUMNS)} FROM gaiadr3.gaia_source "
            f"WHERE source_id IN ({', '.join(source_ids)})")


def fetch_gaia_astrometry(source_ids: tuple[str, ...], *,
                          timeout_sec: float = 25.0,
                          opener=urlopen) -> bytes:
    adql = make_target_astrometry_adql(source_ids)
    if not math.isfinite(timeout_sec) or not 1 <= timeout_sec <= 60:
        raise ValueError("Invalid TAP time budget")
    form = urlencode({"REQUEST":"doQuery","LANG":"ADQL","FORMAT":"csv",
                      "QUERY":adql}).encode("ascii")
    request = Request(GAIA_TAP_URL, data=form, method="POST",
                      headers={"Content-Type":"application/x-www-form-urlencoded",
                               "User-Agent":"StellarForge/1.9 Gaia 5p covariance study"})
    with opener(request, timeout=timeout_sec) as response:
        raw = response.read(MAX_TAP_BYTES + 1)
    if not raw or len(raw)>MAX_TAP_BYTES:
        raise ValueError("Gaia TAP response empty or excessive")
    return raw


def _number(value, name, *, mandatory=True):
    if value is None or str(value).strip().lower() in ("", "nan", "null", "--"):
        if mandatory:
            raise ValueError(f"Gaia source missing {name}")
        return None
    number=float(value)
    if not math.isfinite(number):
        raise ValueError(f"Non-finite {name}")
    return number


def parse_gaia_astrometry(raw: bytes, *, expected_ids: tuple[str, ...]) -> dict:
    """Missing 5p covariance or source ID => NEVER treat as zero uncertainty."""
    if len(raw)>MAX_TAP_BYTES:
        raise ValueError("Oversized TAP payload")
    text=raw.decode("utf-8-sig")
    if text.lstrip().startswith(("<", "{")):
        raise ValueError("Gaia response is not CSV")
    lines=[s for s in text.splitlines() if s.strip() and
           not s.lstrip().startswith("#")]
    reader=csv.DictReader(io.StringIO("\n".join(lines)))
    if not reader.fieldnames or not set(GAIA_COLUMNS).issubset(reader.fieldnames):
        raise ValueError("Gaia 5-parameter covariance columns not returned")
    entries={}
    for row in reader:
        if None in row or any(row.get(k) is None for k in GAIA_COLUMNS):
            raise ValueError("Malformed Gaia data fields")
        sid=row["source_id"].strip()
        if not sid.isdigit() or sid in entries or sid not in expected_ids:
            raise ValueError("Unexpected/duplicate Gaia DR3 target ID")
        try:
            nparams=int(row["astrometric_params_solved"])
        except (TypeError, ValueError) as exc:
            raise ValueError("Bad Gaia astrometric solution flag") from exc
        entry={"source_id":sid,"astrometric_params_solved":nparams}
        for key in ("ref_epoch","ra","dec","parallax","pmra","pmdec","ruwe"):
            entry[key]=_number(row[key],key,mandatory=(key!="ruwe"))
        for key in GAIA_ERRORS:
            entry[key]=_number(row[key],key)
        for key in GAIA_CORRELATIONS:
            entry[key]=_number(row[key],key)
        entries[sid]=entry
    if set(entries)!=set(expected_ids):
        raise ValueError("Gaia TAP did not return all requested exact IDs")
    return entries


def five_parameter_gaia_covariance(gaia_row: dict):
    """Return dimensioned-mixed Gaia 5x5 covariance; positive-definite required.

    Error conventions follow Gaia alpha/dec position in mas, parallax in mas,
    mu_alpha* and mu_delta in mas/year, with their provided correlations.
    """
    import numpy as np
    if gaia_row.get("astrometric_params_solved") not in (31,95):
        raise ValueError("Not a Gaia five/six-parameter solution")
    if abs(float(gaia_row["ref_epoch"])-EXPECTED_GAIA_EPOCH)>1e-7:
        raise ValueError("Unexpected Gaia DR3 reference epoch")
    sigmas=np.asarray([_number(gaia_row.get(k),k) for k in GAIA_ERRORS],
                      dtype=float)
    if not np.all(sigmas>0):
        raise ValueError("Missing or nonpositive Gaia astrometric uncertainty")
    corr=np.eye(5,dtype=float)
    for (i,j), key in zip(PAIR_INDICES,GAIA_CORRELATIONS):
        value=_number(gaia_row.get(key),key)
        if abs(value)>1+1e-12:
            raise ValueError("Impossible Gaia correlation")
        corr[i,j]=corr[j,i]=value
    eig=np.linalg.eigvalsh(corr)
    if float(eig.min()) < -1e-8:
        raise ValueError("Inconsistent/non-positive-semidefinite Gaia correlations")
    cov=np.outer(sigmas,sigmas)*corr
    return cov


def earth_barycentric_au(mjd_utc: float):
    """Uses built-in offline Astropy ephemeris (no JPL/remote downloads)."""
    import numpy as np
    import astropy.units as u
    from astropy.time import Time
    from astropy.coordinates import get_body_barycentric, solar_system_ephemeris
    if not math.isfinite(mjd_utc) or not 54000<=mjd_utc<=80000:
        raise ValueError("Unexpected ZTF observing MJD UTC")
    t=Time(mjd_utc,format="mjd",scale="utc")
    with solar_system_ephemeris.set("builtin"):
        xyz=get_body_barycentric("earth",t).xyz.to_value(u.au)
    return np.asarray(xyz,dtype=float),float(t.jyear)


def geocentric_parallax_direction(
    ra_deg: float,dec_deg: float,parallax_mas: float,
    pmra_mas_yr: float,pmdec_mas_yr: float,jyear: float,
    earth_au,
) -> tuple[float,float]:
    """Linear PM + first-order observer displacement/annual parallax in ICRS.

    No RV/perspective, relativistic aberration or topocentric corrections.
    """
    import numpy as np
    validate_icrs(ra_deg,dec_deg)
    for v in (parallax_mas,pmra_mas_yr,pmdec_mas_yr,jyear):
        if not math.isfinite(v):
            raise ValueError("Non-finite astrometric component")
    if abs(parallax_mas)>2000:
        raise ValueError("Parallax too large for first-order screening")
    r=np.asarray(earth_au,dtype=float)
    if r.shape!=(3,) or not np.isfinite(r).all() or not .5<float(np.linalg.norm(r))<1.5:
        raise ValueError("Invalid Earth barycentric position")
    ra,dec=propagate_gaia_position(
        ra_deg,dec_deg,pmra_mas_yr,pmdec_mas_yr,jyear)
    a,d=math.radians(ra),math.radians(dec)
    n=np.array([math.cos(d)*math.cos(a),math.cos(d)*math.sin(a),math.sin(d)])
    # π is radians per AU (trig parallax); subtract sky-plane Earth vector.
    geocentric=n-(parallax_mas*MAS_TO_RAD)*(r-n*np.dot(n,r))
    geocentric=geocentric/np.linalg.norm(geocentric)
    out_ra=math.degrees(math.atan2(geocentric[1],geocentric[0]))%360
    out_dec=math.degrees(math.atan2(geocentric[2],math.hypot(
        geocentric[0],geocentric[1])))
    return out_ra,out_dec


def _tangent_delta_mas(ra1,dec1,ra2,dec2):
    """Small east/north angular offset near a common ICRS pointing."""
    dra=((ra1-ra2+180)%360)-180
    return (dra*math.cos(math.radians(dec2))*3_600_000.0,
            (dec1-dec2)*3_600_000.0)


def propagate_gaia_5p_formal(gaia_row: dict, *,
                              mjd_utc: float) -> dict:
    """Propagate Gaia's *formal* 5D covariance using numeric Jacobian.

    Coordinates are [alpha (mas angle),delta(mas),pi(mas),pmra*(mas/yr),
    pmdec(mas/yr)]. Tangent-plane [east,north] result is in mas.
    High-RUWE errors do not capture binary/orbital systematics.
    """
    import numpy as np
    cov=five_parameter_gaia_covariance(gaia_row)
    earth,jyear=earth_barycentric_au(mjd_utc)
    ra,dec=float(gaia_row["ra"]),float(gaia_row["dec"])
    validate_icrs(ra,dec)
    vec=np.array([ra,dec,float(gaia_row["parallax"]),
                  float(gaia_row["pmra"]),float(gaia_row["pmdec"])],dtype=float)
    def prediction(q):
        return geocentric_parallax_direction(
            q[0],q[1],q[2],q[3],q[4],jyear,earth)
    full=prediction(vec)
    linear=propagate_gaia_position(ra,dec,vec[3],vec[4],jyear)
    parallax_east,parallax_north=_tangent_delta_mas(*full,*linear)
    # Central differences with stable steps: 0.5 mas angle/parallax,
    # 0.1 mas/year in proper motion. These do not use raw pixel fit errors.
    step=np.array([.5/3_600_000.,.5/3_600_000.,.5,.1,.1])
    input_units=np.array([3_600_000.,3_600_000.,1.,1.,1.])
    jac=np.zeros((2,5))
    for i in range(5):
        a=vec.copy()
        b=vec.copy()
        a[i]+=step[i]
        b[i]-=step[i]
        forward=prediction(a)
        backward=prediction(b)
        east,north=_tangent_delta_mas(*forward,*backward)
        jac[:,i]=np.array([east,north])/(2*step[i]*input_units[i])
    formal=jac @ cov @ jac.T
    formal=(formal+formal.T)/2
    eig=np.linalg.eigvalsh(formal)
    if eig.min()<-1e-6 or not np.isfinite(formal).all():
        raise ValueError("Invalid propagated Gaia covariance")
    if min(formal[0,0],formal[1,1])<=0:
        raise ValueError("Degenerate propagated formal position covariance")
    ruwe=gaia_row.get("ruwe")
    warning=(ruwe is None or ruwe>1.4)
    return {
        "source_id":gaia_row["source_id"],
        "mjd_observation_utc":round(mjd_utc,6),
        "gaia_reference_epoch_jyear":EXPECTED_GAIA_EPOCH,
        "gaia_ruwe":ruwe,
        "high_or_missing_ruwe_quality_warning":warning,
        "status":("FORMAL_COVARIANCE_MODEL_WITH_ASTROMETRIC_QUALITY_WARNING"
                  if warning else "FORMAL_COVARIANCE_MODEL_NOT_INSTRUMENT_CALIBRATION"),
        "geocentric_parallax_adjusted_ra_deg":round(full[0],10),
        "geocentric_parallax_adjusted_dec_deg":round(full[1],10),
        "geocentric_annual_parallax_minus_linear_east_mas":
            round(parallax_east,5),
        "geocentric_annual_parallax_minus_linear_north_mas":
            round(parallax_north,5),
        "formal_gaia_east_sigma_mas":round(math.sqrt(formal[0,0]),5),
        "formal_gaia_north_sigma_mas":round(math.sqrt(formal[1,1]),5),
        "formal_east_north_covariance_mas2":[
            [round(float(x),6) for x in line] for line in formal],
        "full_gaia_five_parameter_formal_covariance_propagated":True,
        "builtin_earth_ephemeris_used":True,
        "annual_geocentric_parallax_included":True,
        "physical_perspective_or_radial_velocity_modeled":False,
        "non_single_star_systematics_in_covariance":False,
        "ztf_instrument_wcs_psf_error_budget_included":False,
        "gaia_ztf_astrophysical_source_identity_confirmed":False,
    }
