"""Prospective CDS SIMBAD dual exact-ID alias lookup for the frozen FT Tau Gaia ID.

SIMBAD aliases support only curated external naming, never an independently
authenticated ZTF source, photometric identity, proper motion or discovery.
"""
from __future__ import annotations

import csv
import hashlib
import io
import math
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .r2_ft_tau_two_field_fits import FT_GAIA, frozen_ft_tau
from .v19_gaia_covariance import fetch_gaia_astrometry, parse_gaia_astrometry

MIRRORS = (
    "https://simbad.cfa.harvard.edu/simbad/sim-tap/sync",
    "https://simbad.idia.ac.za/simbad/sim-tap/sync",
)
MAX_ORIGINAL_TAP_BYTES = 120_000
MAX_ORIGINAL_TAP_ROWS = 10
SIMBAD_REQUIRED = ("oid", "main_id", "ra", "dec", "otype")
TARGET_GAIA_IDENTIFIER = "Gaia DR3 149623711269425408"
FT_NAME_IDENTIFIERS = ("FT Tau", "V* FT Tau")
EXPECTED_GAIA_SOURCE_SHA = "399b5498d8d8a8a646073dfc029895ed64902940896d1789c63833a18074b642"

# The exact preregistered queries: no followup wildcard, name similarity,
# reverse engineered neighbour selection or untested identifier substitution.
EXACT_GAIA_ADQL = (
    "SELECT TOP 10 b.oid,b.main_id,b.ra,b.dec,b.otype "
    "FROM basic AS b JOIN ident AS i ON b.oid=i.oidref "
    "WHERE i.id='Gaia DR3 149623711269425408'"
)
EXACT_FT_NAME_ADQL = (
    "SELECT DISTINCT TOP 10 b.oid,b.main_id,b.ra,b.dec,b.otype "
    "FROM basic AS b JOIN ident AS i ON b.oid=i.oidref "
    "WHERE i.id IN ('FT Tau','V* FT Tau')"
)
ERRORS = (HTTPError, URLError, TimeoutError, OSError, ValueError,
          TypeError, OverflowError, UnicodeError, ArithmeticError)


def parse_simbad_original_csv(raw: bytes) -> dict:
    """Strictly parse original TAP CSV, keeping source rows ephemeral."""
    if not isinstance(raw, bytes) or not 15<=len(raw)<=MAX_ORIGINAL_TAP_BYTES:
        raise ValueError("SIMBAD original response missing/oversized")
    t=raw.decode("utf-8-sig")
    if t.lstrip().startswith(("<", "{", "[")) or "<html" in t.lower()[:150]:
        raise ValueError("SIMBAD original response is not TAP CSV")
    lines=[line for line in t.splitlines() if line.strip()
           and not line.lstrip().startswith("#")]
    if not lines:
        raise ValueError("SIMBAD TAP CSV no header")
    reader=csv.DictReader(io.StringIO("\n".join(lines)))
    cols=reader.fieldnames or []
    if len(cols)!=len(set(cols)) or set(cols)!=set(SIMBAD_REQUIRED):
        raise ValueError("Original SIMBAD columns differ from frozen schema")
    entries={}
    n_raw=0
    for item in reader:
        n_raw+=1
        if n_raw>MAX_ORIGINAL_TAP_ROWS or None in item:
            raise ValueError("SIMBAD original TAP result truncated/oversized")
        try:
            oid=str(item["oid"]).strip()
            main=str(item["main_id"]).strip()
            kind=str(item["otype"]).strip()
            ra=float(item["ra"])
            dec=float(item["dec"])
        except (TypeError, ValueError, KeyError) as exc:
            raise ValueError("Malformed original SIMBAD source") from exc
        if (not oid.isdigit() or not main or not kind or
                not all(math.isfinite(x) for x in (ra,dec))
                or not 0<=ra<360 or not -90<=dec<=90):
            raise ValueError("SIMBAD alias metadata invalid")
        one={"oid":oid,"main_id":main,"ra_deg":ra,
             "dec_deg":dec,"otype":kind}
        if oid in entries and one!=entries[oid]:
            raise ValueError("Same original SIMBAD identifier has conflicting metadata")
        entries[oid]=one
    return {
        "source":"ORIGINAL_CDS_SIMBAD_TAP_EXACT_IDENTIFIER",
        "raw_sha256":hashlib.sha256(raw).hexdigest(),
        "n_original_rows":n_raw,
        "n_unique_object_records":len(entries),
        "rows_ephemeral":list(entries.values()),
    }


def fetch_simbad_exact_query(url: str, query: str, *,
                             timeout_sec:float=25,opener=urlopen)->bytes:
    """Only two documented CDS official mirror endpoints, bounded responses."""
    if url not in MIRRORS or query not in (EXACT_GAIA_ADQL, EXACT_FT_NAME_ADQL):
        raise ValueError("Nonpreregistered SIMBAD endpoint/query")
    if not math.isfinite(timeout_sec) or not 1<=timeout_sec<=30:
        raise ValueError("Invalid external TAP timeout")
    post=urlencode({
        "REQUEST":"doQuery","LANG":"ADQL","FORMAT":"csv",
        "QUERY":query,"MAXREC":str(MAX_ORIGINAL_TAP_ROWS)
    }).encode("ascii")
    req=Request(url,data=post,method="POST",
                headers={"Content-Type":"application/x-www-form-urlencoded",
                         "User-Agent":"StellarForge/2.1 original SIMBAD exact FT Tau scientific alias study"})
    with opener(req,timeout=timeout_sec) as resp:
        actual=resp.geturl()
        if actual!=url:
            raise ValueError("Unexpected SIMBAD TAP redirect")
        raw=resp.read(MAX_ORIGINAL_TAP_BYTES+1)
    if not raw or len(raw)>MAX_ORIGINAL_TAP_BYTES:
        raise ValueError("Original SIMBAD response empty/oversized")
    return raw


def external_alias_equivalence(gaia:dict,name:dict,*,gaia_ra:float,
                               gaia_dec:float)->dict:
    """Classify exact SIMBAD record alias identity, not astrometric match."""
    first=gaia["rows_ephemeral"]; second=name["rows_ephemeral"]
    n1,n2=len(first),len(second)
    merged_status=(
        "SIMBAD_EXACT_NAME_AND_GAIA_ALIAS_SAME_EXTERNAL_OBJECT"
        if n1==n2==1 and first[0]["oid"]==second[0]["oid"]
        else "SIMBAD_ALIAS_AMBIGUOUS_MULTIPLE_OBJECTS"
        if n1>1 or n2>1 else "SIMBAD_ALIAS_LOOKUP_UNRESOLVED"
        if n1==0 or n2==0 else "SIMBAD_EXACT_GAIA_AND_FT_NAME_CONFLICT")
    row=first[0] if n1==1 else second[0] if n2==1 else None
    offset=None
    if row is not None:
        r1,r2,d1,d2=map(math.radians,[
            gaia_ra,row["ra_deg"],gaia_dec,row["dec_deg"]])
        a=math.sin((d2-d1)/2)**2+math.cos(d1)*math.cos(d2)*math.sin((r2-r1)/2)**2
        offset=round(math.degrees(2*math.asin(min(1,math.sqrt(max(a,0)))))*3600,5)
    return {
        "status":merged_status,
        "gaia_exact_id_n_original_simbad_rows":gaia["n_original_rows"],
        "gaia_exact_id_n_unique_simbad_objects":n1,
        "ft_tau_exact_name_n_original_simbad_rows":name["n_original_rows"],
        "ft_tau_exact_name_n_unique_simbad_objects":n2,
        "exact_external_catalogue_name_gaia_alias_verified":
            merged_status=="SIMBAD_EXACT_NAME_AND_GAIA_ALIAS_SAME_EXTERNAL_OBJECT",
        "matched_external_simbad_main_id":
            first[0]["main_id"] if merged_status=="SIMBAD_EXACT_NAME_AND_GAIA_ALIAS_SAME_EXTERNAL_OBJECT"
            else None,
        "matched_external_simbad_object_type":
            first[0]["otype"] if merged_status=="SIMBAD_EXACT_NAME_AND_GAIA_ALIAS_SAME_EXTERNAL_OBJECT"
            else None,
        "descriptive_simbad_basic_to_gaia_dr3_epoch2016_separation_arcsec":offset,
        "coordinate_epoch_and_independent_error_model_verified":False,
        "independent_physical_gaia_to_ztf_target_identity_confirmed":False,
        "external_source_is_not_new_astrophysical_detection":True,
    }


def frozen_ft_simbad_requirements(seed:bytes,historic:dict,
                                  oid_receipt:dict,prior_psf:dict)->dict:
    ft=frozen_ft_tau(seed,historic,oid_receipt)
    if (ft["gaia_id"]!=FT_GAIA or ft["name"]!="FT Tau"
            or len(ft["fixed_oids"])!=4
            or prior_psf.get("original_data_run_id")!=43310945601
            or prior_psf.get("exact_gaia_dr3_target_id")!=FT_GAIA
            or prior_psf.get("original_full_native_psfcats_sha_verified")!=6
            or prior_psf.get("original_science_mask_pairs_sha_verified")!=6
            or prior_psf.get("original_native_spatial_daophot_models_parsed")!=6
            or prior_psf.get("original_candidate_native_quality_statuses_changed")!=0
            or prior_psf.get("original_native_candidate_5_of_8_pass_3_of_8_fail_unchanged") is not True
            or prior_psf.get("original_1_of_4_quality_accepted_two_night_pairs_unchanged") is not True
            or prior_psf.get("merged_original_ztf_oid_lightcurves")!=0
            or prior_psf.get("scientific_r2_complete") is not False):
        raise ValueError("Original FT Tau Gaia-ZTF data integrity changed")
    return ft


def run_fttau_simbad_exact_external_alias(
    seed:bytes,historic:dict,oid_receipt:dict,prior_psf:dict,*,
    gaia_fetch=fetch_gaia_astrometry,
    mirror_fetch=fetch_simbad_exact_query)->dict:
    """Two independent exact identifier paths on one prechosen SIMBAD mirror."""
    ft=frozen_ft_simbad_requirements(seed,historic,oid_receipt,prior_psf)
    gbytes=gaia_fetch((FT_GAIA,),timeout_sec=35)
    gsha=hashlib.sha256(gbytes).hexdigest()
    if gsha!=EXPECTED_GAIA_SOURCE_SHA:
        raise ValueError("Original fixed Gaia DR3 5p TAP source bytes changed")
    source=parse_gaia_astrometry(gbytes,expected_ids=(FT_GAIA,))[FT_GAIA]
    study={
        "phase":"TAURUS_R2_FT_TAU_GAIA_DR3_VS_CDS_SIMBAD_TWO_EXACT_IDENTIFIER_EXTERNAL_ALIAS_AUDIT",
        "frozen_target_name":ft["name"],
        "frozen_gaia_dr3_source_id":FT_GAIA,
        "gaia_original_5p_response_sha256":gsha,
        "preceding_six_original_spatial_psf_run_id":43310945601,
        "n_frozen_previous_zft_oids":4,
        "n_prior_original_ztf_spatial_psf_exposures_unmodified":6,
        "simbad_tap_original_query_gaia_adql_sha256":
            hashlib.sha256(EXACT_GAIA_ADQL.encode()).hexdigest(),
        "simbad_tap_original_query_ft_name_adql_sha256":
            hashlib.sha256(EXACT_FT_NAME_ADQL.encode()).hexdigest(),
        "simbad_cds_mirror_endpoints_in_fixed_order":list(MIRRORS),
        "simbad_original_query_mirror":None,
        "original_cds_simbad_alias_status":"EXTERNAL_SERVICE_UNAVAILABLE",
        "simbad_original_gaia_alias_response_sha256":None,
        "simbad_original_ft_name_response_sha256":None,
        "external_catalogue_alias_evidence":None,
        "mirrors_attempted_metadata_only":[],
        "n_original_ztf_oid_lightcurves_merged":0,
        "original_source_quality_5_of_8_pass_3_of_8_fail_unchanged":True,
        "n_original_valid_two_night_source_pairs_unchanged":1,
        "n_independently_authenticated_gaia_ztf_physical_source_matches":0,
        "n_confirmed_new_variables_or_companions":0,
        "independent_wcs_psf_covariance_calibrated":False,
        "scientific_r2_complete":False,
        "limitations":[
            "SIMBAD identifier aliases are curated external name and bibliographic catalogue records, not independent original image detections.",
            "Even matching external Gaia DR3 and FT Tau SIMBAD object identifiers does not prove each original ZTF per-epoch catalog source is physically the Gaia star.",
            "Do not infer stellar variability, companions, astrometric precision, detector PSF accuracy or common-lightcurve object identity from this alias audit.",
            "Previous 0.5<=native PSF chi<=1.5 gates and all 5/8 source-quality outcomes remain frozen.",
        ],
    }
    for mirror in MIRRORS:
        try:
            one_raw=mirror_fetch(mirror,EXACT_GAIA_ADQL,timeout_sec=25)
            two_raw=mirror_fetch(mirror,EXACT_FT_NAME_ADQL,timeout_sec=25)
            one=parse_simbad_original_csv(one_raw)
            two=parse_simbad_original_csv(two_raw)
        except ERRORS as exc:
            study["mirrors_attempted_metadata_only"].append({
                "endpoint":mirror,"status":"ACCESS_OR_CSV_INVALID",
                "error_type":type(exc).__name__,
                "http_status":int(exc.code) if isinstance(exc,HTTPError) else None})
            continue
        cross=external_alias_equivalence(
            one,two,gaia_ra=source["ra"],gaia_dec=source["dec"])
        study["simbad_original_query_mirror"]=mirror
        study["original_cds_simbad_alias_status"]=cross["status"]
        study["simbad_original_gaia_alias_response_sha256"]=one["raw_sha256"]
        study["simbad_original_ft_name_response_sha256"]=two["raw_sha256"]
        study["external_catalogue_alias_evidence"]=cross
        study["mirrors_attempted_metadata_only"].append({
            "endpoint":mirror,"status":"TWO_EXACT_IDENTIFIER_CSV_QUERIES_PARSED"})
        break
    return study
