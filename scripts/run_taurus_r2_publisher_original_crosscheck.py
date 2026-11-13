"""One bounded real publisher/CDS MRT check against the frozen Taurus R1 cohort.

Official journal-source URL attempts and CDS archival copy are separate
evidence tiers. Raw retrieved source table never uploaded or committed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from stellarforge.luhman2023 import parse_membership_mrt

COHORT_SHA="9cecb94704f028a981045629ad16ecb770f51bba4b6bb3bf13dda769327ff37e"
OFFICIAL_URLS=(
    ("PUBLISHER_IOP_SUPPLEMENT","https://content.cld.iop.org/journals/1538-3881/165/2/37/revision1/ajac9da3t2_mrt.txt"),
    ("PUBLISHER_IOPSCIENCE_SUPPDATA","https://iopscience.iop.org/1538-3881/165/2/37/suppdata/ajac9da3t2_mrt.txt"),
    ("CDS_ARCHIVAL_TABLE","https://cdsarc.cds.unistra.fr/ftp/J/AJ/165/37/table2.dat"),
    ("CDS_ARCHIVAL_MRT","https://cdsarc.cds.unistra.fr/ftp/J/AJ/165/37/ajac9da3t2_mrt.txt"),
)
MAX_BYTES=500_000


def provider_probe(url: str, timeout_seconds: float=10)->tuple[bytes|None,dict]:
    req=Request(url,headers={"User-Agent":"StellarForge-research/2.1 (source-provenance-only)"})
    try:
        with urlopen(req, timeout=timeout_seconds) as response:
            code=response.status
            ctype=str(response.headers.get("Content-Type","")).split(";")[0].strip().lower()
            raw=response.read(MAX_BYTES+1)
    except HTTPError as error:
        return None, {"outcome":"HTTP_ERROR","http_status":error.code}
    except (URLError,TimeoutError,OSError) as error:
        return None, {"outcome":"NETWORK_OR_TIMEOUT","exception_type":type(error).__name__}
    if len(raw)>MAX_BYTES:
        return None, {"outcome":"RESPONSE_TOO_LARGE","bytes_above_limit":True}
    if not raw:
        return None, {"outcome":"EMPTY_RESPONSE","http_status":code}
    return raw,{"outcome":"RETRIEVED_FOR_VALIDATION","http_status":code,
                "response_content_type":ctype,"bytes":len(raw),
                "response_sha256":hashlib.sha256(raw).hexdigest()}


def original_publisher_check(seed_raw:bytes, *, probe=provider_probe)->dict:
    if hashlib.sha256(seed_raw).hexdigest()!=COHORT_SHA:
        raise ValueError("Frozen R1 seed bytes SHA differs: refusing source relabelling")
    seed=list(csv.DictReader(seed_raw.decode("utf-8-sig").splitlines()))
    ids=[row["gaia"] for row in seed]
    if len(seed)!=24 or len(set(ids))!=24:
        raise ValueError("Invalid frozen 24-source R1 cohort")

    attempts=[]
    match=None
    for kind,url in OFFICIAL_URLS:
        raw,trace=probe(url)
        record={"source_tier":kind,"url":url,**trace}
        if raw is None:
            attempts.append(record)
            continue
        try:
            parsed=parse_membership_mrt(raw)
            byid={m["gaia_dr3_source_id"]:m for m in parsed["members"]}
            matching_ids=0
            matching_pos=0
            conflicting_ids=[]
            conflicting_pos=[]
            for row in seed:
                candidate=byid.get(row["gaia"])
                if candidate is None:
                    conflicting_ids.append(row["gaia"])
                    continue
                matching_ids+=1
                if (abs(candidate["ra_deg"]-float(row["ra"]))<=5e-7 and
                        abs(candidate["dec_deg"]-float(row["dec"]))<=5e-7):
                    matching_pos+=1
                else:
                    conflicting_pos.append(row["gaia"])
            record.update({
                "original_table_parsed":True,
                "official_table_adopted_member_rows":parsed["record_count"],
                "official_table_gaia_source_ids":parsed["with_gaia_dr3_source_id"],
                "frozen_24_exact_gaia_ids_matched":matching_ids,
                "frozen_24_original_positions_matched":matching_pos,
                "frozen_24_gaia_ids_missing_in_source":conflicting_ids,
                "frozen_24_gaia_ids_with_position_discrepancy":conflicting_pos,
                "individual_24_literature_rows_original_source_vetted":matching_ids==matching_pos==24,
            })
            if matching_ids==matching_pos==24:
                match=kind
                attempts.append(record)
                break
        except (UnicodeError,ValueError,KeyError) as err:
            record.update({"original_table_parsed":False,
                           "parser_error_type":type(err).__name__})
        attempts.append(record)
    return {
        "schema_version":"stellarforge-taurus-r2-original-2023-publisher-table-attempt-no-raw-v1",
        "phase":"R2_SOURCE_MEMBERSHIP_ORIGINAL_PUBLISHER_BYTE_SOURCE_CHECK",
        "frozen_cohort_sha256":COHORT_SHA,
        "original_publisher_source_table_24_rows_verified":match is not None and match.startswith("PUBLISHER_"),
        "cds_archive_source_table_24_rows_verified":match=="CDS_ARCHIVAL_TABLE" or match=="CDS_ARCHIVAL_MRT",
        "full_original_24_source_table_verified_from_accepted_origin":match is not None,
        "accepted_origin":match,
        "attempts":attempts,
        "n_original_source_tabular_rows_committed_to_git":0,
        "n_ztf_gaia_physical_source_associations_established_by_membership":0,
        "interpretation":"Membership catalog source provenance only; even successful published Table 2 match does not authenticate any ZTF physical source or astrometric instrument covariance."
    }


def main()->None:
    parser=argparse.ArgumentParser(description="Fetch at most four explicit official publisher/CDS Luhman 2023 MRT URLs; NO raw table publication")
    parser.add_argument("--seed",type=Path,default=Path("data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv"))
    parser.add_argument("--output",type=Path,default=Path("reports/generated/r2_publisher_original_table_no_raw.json"))
    args=parser.parse_args()
    result=original_publisher_check(args.seed.read_bytes())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps({"membership_original_24_verified":result["full_original_24_source_table_verified_from_accepted_origin"],
                      "accepted_origin":result["accepted_origin"],
                      "per_endpoint_outcomes":[(x["source_tier"],x["outcome"]) for x in result["attempts"]],
                      "output_path":str(args.output)},indent=2))


if __name__=="__main__":
    main()
