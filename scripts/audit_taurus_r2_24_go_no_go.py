"""Fail-closed, fully offline audit of the 24-source Taurus R2 decision ledger.

Reads previously committed original provider no-raw receipts and the frozen
24-source R1 seed. Does not fetch new Gaia/ZTF/Luhman data or interpret a
positional cone, matched name or nominal source-centroid as a physical star.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

SEED_SHA="9cecb94704f028a981045629ad16ecb770f51bba4b6bb3bf13dda769327ff37e"
PUBLISHER_SHA="8ffd84c876afe6b6d7690f8e4ba4f97ec94f643e0e924c98f6c101b8656c0493"
FT="149623711269425408"
CIDA="3419110734340795648"
NO_ROWS="3314244366165299584"
HTTP_400="3406270362673330944"
SOURCES={
    "seed":"data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv",
    "gaia":"reports/taurus_variability_r2/GAIA_24_ORIGINAL_PER_SOURCE_FLAGS_NO_RAW.json",
    "initial":"reports/taurus_variability_r2/GAIA_NEIGHBOUR_ZTF_POSITIONAL_ORIGINAL_RESULTS_NO_RAW.json",
    "diagnostic":"reports/taurus_variability_r2/IRSA_22_ORIGINAL_DERIVED_DIAGNOSTIC_LEDGER.json",
    "nine":"reports/taurus_variability_r2/IRSA_NINE_ORIGINAL_RESPONSE_SOURCE_LEDGER_NO_RAW.json",
    "oid":"reports/taurus_variability_r2/REAL_TWO_FIELDS_ORIGINAL_IRSA_ALTERNATE_OBJECTIDS_NO_RAW.json",
    "frames":"reports/taurus_variability_r2/FOUR_ORIGINAL_FITS_MASK_NATIVE_PSF_SOURCE_QA_NO_RAW.json",
    "alias":"reports/taurus_variability_r2/FTTAU_SIMBAD_EXACT_GAIA_NAME_ALIAS_NO_RAW.json",
    "nights":"reports/taurus_variability_r2/FTTAU_MULTINIGHT_ORIGINAL_ZTF_SOURCE_AUDIT_NO_RAW.json",
    "publisher":"reports/taurus_variability_r2/R2_PUBLISHER_LUHMAN2023_ORIGINAL_24_OF_24_NO_RAW.json",
    "ledger":"reports/taurus_variability_r2/R2_FINAL_24_TECHNICAL_SOURCE_ACCESS_AND_IDENTITY_DECISION_NO_RAW.json",
}
EXPECTED={
    "frozen_technical_cohort":24,"exact_gaia_dr3_sources_retrieved":24,
    "gaia_only_preliminary_source_qa_pass":17,"gaia_only_source_qa_requiring_review":7,
    "catalogued_gaia_neighbours_within_2arcsec_target_count":0,
    "catalogued_gaia_neighbours_within_5arcsec_target_count":4,
    "cumulative_positional_irsa_ztf_parsed_target_positions":22,
    "irsa_target_positions_without_a_parsed_original_response":2,
    "original_irsa_zero_row_under_nobsmin5":1,
    "original_irsa_http400_under_nobsmin1":1,
    "technical_sources_with_historical_original_science_mask_psfcat_source_images_checked":2,
    "historical_original_source_image_frames_evaluated":4,
    "technical_sources_with_external_curated_simbad_name_gaia_alias":1,
    "independently_authenticated_physical_gaia_ztf_counterparts":0,
    "scientifically_r3_eligible_original_source_lightcurves":0,
    "merged_original_ztf_objectid_lightcurves":0,
    "confirmed_new_astrophysical_variables":0,
    "confirmed_new_astrophysical_companions":0,
    "original_journal_table_exact_gaia_ids_and_positions_verified":24,
}


def _same(obj:dict,key:str,value,where:str)->None:
    if not isinstance(obj,dict) or key not in obj or type(obj[key]) is not type(value) or obj[key]!=value:
        raise ValueError(f"{where}.{key}: inconsistent with original source-derived evidence")


def _read(root:Path,rel:str)->dict:
    path=(root/rel)
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root):
        raise ValueError(f"Original evidence missing or unsafe: {rel}")
    return json.loads(path.read_text(encoding="utf8"))


def audit_24_final(root:Path)->dict:
    root=Path(root).resolve()
    raw=(root/SOURCES["seed"]).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SEED_SHA:
        raise ValueError("R1 frozen 24-row technical seed was changed")
    seed=list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    if len(seed)!=24 or len({r["gaia"] for r in seed})!=24:
        raise ValueError("R1 sample cardinality/IDs changed")
    evidence={k:_read(root,v) for k,v in SOURCES.items() if k!="seed"}
    G,A,B,C,O,F,S,M,P,L=[evidence[k] for k in ("gaia","initial","diagnostic","nine","oid","frames","alias","nights","publisher","ledger")]

    if (G["r1_frozen_seed_sha256"]!=SEED_SHA
            or A["original_r1_seed_sha256"]!=SEED_SHA
            or B["original_r1_seed_sha256"]!=SEED_SHA
            or C["frozen_r1_sha256"]!=SEED_SHA
            or P["frozen_cohort_sha256"]!=SEED_SHA
            or L["r1_technical_seed_sha256"]!=SEED_SHA):
        raise ValueError("One of the independent original-source cohort SHA receipts was changed")

    # 2026-11-13: genuine publisher original machine-readable Table 2
    # was retrieved on a real Actions runner. Its raw bytes deliberately
    # are NOT in Git; this checks the derived archived byte-source receipt.
    if (P.get("accepted_origin")!="PUBLISHER_IOP_SUPPLEMENT"
            or P.get("original_data_workflow_run_id")!=43499836719
            or P.get("original_derived_only_artifact_id")!=14072229650
            or P.get("full_original_24_source_table_verified_from_accepted_origin") is not True
            or P.get("original_publisher_source_table_24_rows_verified") is not True
            or len(P.get("attempts",[]))!=1):
        raise ValueError("Original publisher-source validation has no authentic receipt")
    official=P["attempts"][0]
    for key,value in (("http_status",200),("bytes",201726),
                      ("response_sha256",PUBLISHER_SHA),
                      ("official_table_adopted_member_rows",532),
                      ("official_table_gaia_source_ids",467),
                      ("frozen_24_exact_gaia_ids_matched",24),
                      ("frozen_24_original_positions_matched",24),
                      ("individual_24_literature_rows_original_source_vetted",True)):
        _same(official,key,value,"publisher_original_receipt")
    if (official.get("frozen_24_gaia_ids_missing_in_source")!=[]
            or official.get("frozen_24_gaia_ids_with_position_discrepancy")!=[]
            or P.get("n_original_source_tabular_rows_committed_to_git")!=0
            or P.get("n_ztf_gaia_physical_source_associations_established_by_membership")!=0
            or P.get("original_derived_only_artifact_zip_sha256")!="07dc278fa694f2985e68a988965dfe8a6cce8e1fc00d025c264a1c87d51d879e"):
        raise ValueError("Publisher membership rows not verified or source science overstated")
    for key,val in (
        ("original_publisher_luhman2023_mrt_sha256",PUBLISHER_SHA),
        ("original_publisher_luhman2023_table2_members",532),
        ("original_publisher_luhman2023_table2_gaia_ids",467),
        ("original_publisher_24_rows_gaia_id_and_position_check_passed",True),
        ("original_publisher_mirror_byte_for_byte_identity_compared",False),
        ("r2_physical_source_identity_success",False),
        ("r2_scientific_identity_gate_not_met",True),
        ("r2_closed_as_feasibility_no_go_not_as_physical_source_discovery",True),
        ("r3_physical_stellar_variability_analysis_authorized",False),
        ("no_ztf_original_objectid_curves_merged",True),
        ("old_fttau_three_low_native_chi_source_quality_failures_unmodified",True),
    ): _same(L,key,val,"R2_main_decision")
    if (L.get("schema_version")!="stellarforge-taurus-r2-frozen-24-source-screening-go-no-go-original-derived-v1"
            or L.get("r2_24_source_access_and_ambiguity_ledger_complete") is not True
            or L.get("phase_status")!="R2_SOURCE_ACCESS_AND_AMBIGUITY_SCREENING_ADJUDICATED__PHYSICAL_GAIA_ZTF_MATCH_UNPROVEN"):
        raise ValueError("R2 screening status missing or mislabelled")

    if set(L["summary"])!=set(EXPECTED):
        raise ValueError("Missing or extra R2 source summary claim fields")
    for key,val in EXPECTED.items():_same(L["summary"],key,val,"R2_24_source_counts")
    # Every previously collected source must survive unchanged and
    # retain one of: original two, 13 diagnosed, 7 recovered or 2 blocked.
    gm={z["gaia_dr3_source_id"]:z for z in G["source_rows"]}
    ai={z["gaia_dr3_source_id"]:z for z in A["original_ztf_parsed_cases"]}
    bi={z["gaia_dr3_source_id"]:z for z in B["rows"]}
    ci={z["gaia_dr3_source_id"]:z for z in C["per_source"]}
    oi={z["gaia_dr3_id"]:z for z in O["fields"]}
    rows=L.get("sources")
    if (not isinstance(rows,list) or len(rows)!=24
            or len(gm)!=24 or len(bi)!=24 or len(ci)!=9 or len(ai)!=2
            or len(oi)!=2):
        raise ValueError("Original source cohorts or final per-source ledger not 24/24")
    if {z["gaia_dr3_source_id"] for z in rows}!={z["gaia"] for z in seed}:
        raise ValueError("R2 ledger Gaia source IDs are not the frozen R1 cohort")

    n_access=n_qa=n_bad_gaia=n_neighbor5=n_img=n_img_sources=n_alias=0
    n_norows=n_http=0
    for i,(src,out) in enumerate(zip(seed,rows),1):
        id=src["gaia"]
        g=gm[id]
        if id!=out.get("gaia_dr3_source_id") or out.get("technical_target_index")!=i:
            raise ValueError("Per-source output re-ordered or substituted")
        for key,expected in (
            ("technical_name",src["name"] or None),
            ("two_mass_id",src["two_mass_id"] or None),
            ("technical_seed_group",src["group"]),
            ("technical_seed_original_mirror_line",int(src["original_line"])),
            ("gaia_exact_dr3_record_retrieved",True),
            ("gaia_original_ruwe_rounded_5dp",g["original_gaia_ruwe_5dp"]),
            ("gaia_original_preliminary_astrometry_qa_pass",g["original_gaia_only_preliminary_astrometry_flag_pass"]),
            ("gaia_original_neighbours_within_2arcsec",g["original_gaia_neighbours_within_2arcsec"]),
            ("gaia_original_neighbours_within_5arcsec",g["original_gaia_neighbours_within_5arcsec"]),
            ("gaia_astrometry_review_required",not g["original_gaia_only_preliminary_astrometry_flag_pass"]),
            ("original_publisher_membership_independently_verified",True),
            ("original_journal_table_adopted_member_gaia_id_and_position_verified",True),
            ("physical_membership_independently_reassessed_from_multiple_literature_sources",False),
            ("original_physical_gaia_to_ztf_identity_authenticated",False),
            ("r3_physical_variability_scientific_analysis_eligible",False),
            ("independent_ztf_wcs_psf_covariance_calibration_complete",False),
        ): _same(out,key,expected,f"source_{id}")
        if id not in bi:
            raise ValueError("Prior original 24-target diagnostic source deleted")
        old=ai.get(id);last=ci.get(id);diag=bi[id];oid=oi.get(id)
        if old:
            st="PARSED_ORIGINAL_POSITIONAL_ROWS_WITH_MULTIPLE_OIDS"
            n=old["n_original_ztf_raw_rows"]; run=43031689454
            p=SOURCES["initial"];outcome="PARSED_TABLE_WITH_ROWS"
        elif last and last["parsed_positional_table_with_rows"]:
            st="PARSED_ORIGINAL_POSITIONAL_ROWS_UNAUTHENTICATED"
            n=last["current_original_provider_response"]["returned_rows"];run=43042786341
            p=SOURCES["nine"];outcome="PARSED_TABLE_WITH_ROWS"
        elif diag["recovered_original_positional_rows"]:
            st="PARSED_ORIGINAL_POSITIONAL_ROWS_UNAUTHENTICATED"
            cand=[a for a in diag["diagnostic_attempts"] if a["outcome"]=="PARSED_TABLE_WITH_ROWS"]
            if len(cand)!=1: raise ValueError("Original source provider duplicate success")
            n=cand[0]["returned_rows"];run=43037800319
            p=SOURCES["diagnostic"];outcome="PARSED_TABLE_WITH_ROWS"
        elif last:
            n=None;run=43042786341;p=SOURCES["nine"]
            outcome=last["current_original_provider_response"]["outcome"]
            if outcome=="PARSED_TABLE_ZERO_ROWS" and id==NO_ROWS:
                st="NO_ROWS_AT_NOBS_MIN_5_NOT_NONDETECTION";n_norows+=1
            elif outcome=="HTTP_CLIENT_ERROR" and id==HTTP_400:
                st="HTTP_400_NOBS_MIN_1_ARCHIVE_UNRESOLVED";n_http+=1
            else: raise ValueError("Unexpected original IRSA missing source outcome")
        else:raise ValueError("Unclassified ZTF original source input "+id)
        for key,expected in (
            ("ztf_original_position_query_access",st),
            ("ztf_last_original_positional_rows",n),
            ("ztf_last_source_run_id",run),
            ("ztf_last_source_report",p),
            ("ztf_original_provider_outcome",outcome),
        ):_same(out,key,expected,f"IRSA_source_{id}")
        if n is not None:n_access+=1
        images=sum(z["gaia_dr3_id"]==id for z in F["frames"])
        _same(out,"historical_original_science_mask_psfcat_images_checked",images,f"imaged_source_{id}")
        if images:n_img_sources+=1;n_img+=images
        oid_count=(oid["positional_oid_screen"]["n_original_distinct_ztf_oids"]
                   if oid else old["n_distinct_ztf_oid_band_time_groups"] if old else None)
        multiple=(oid["positional_oid_screen"]["n_original_oid_pairs_in_same_band"]>0
                  if oid else bool(old["ambiguous_bands"]) if old else None)
        for key,val in (
            ("original_number_distinct_ztf_oids_when_reviewed",oid_count),
            ("original_multiple_oids_in_same_band_known",multiple),
            ("simbad_fttau_historical_name_gaia_dr3_curated_alias_verified",id==FT),
            ("fttau_original_native_psf_source_quality_5_of_8_passed",5 if id==FT else None),
            ("fttau_original_native_two_night_pairs_1_of_4_passed",1 if id==FT else None),
        ):_same(out,key,val,f"source_instrument_{id}")
        decision=("ARCHIVE_ACCESS_NOT_ESTABLISHED" if n is None else
                  "MULTIPLE_OID_OR_INSTRUMENTAL_SOURCE_AMBIGUITY_OPEN" if oid or old else
                  "PHYSICAL_IDENTITY_NOT_AUTHENTICATED")
        _same(out,"source_decision",decision,f"R2_final_{id}")
        blockers=out.get("next_evidence_needed")
        if (not isinstance(blockers,list) or not any(
                "Independent per-exposure Gaia/ZTF" in s for s in blockers)):
            raise ValueError("Per-source physical-source uncertainties improperly hidden")
        n_qa+=bool(g["original_gaia_only_preliminary_astrometry_flag_pass"])
        n_bad_gaia+=not g["original_gaia_only_preliminary_astrometry_flag_pass"]
        n_neighbor5+=g["original_gaia_neighbours_within_5arcsec"]>0
        n_alias+=id==FT
    if (n_access,n_norows,n_http,n_qa,n_bad_gaia,n_neighbor5,n_img,n_img_sources,n_alias)!=(22,1,1,17,7,4,4,2,1):
        raise ValueError("R2 original-data denominator/count reconciliation failed")
    if (S.get("exact_gaia_dr3_source_id")!=FT
            or S.get("external_curated_simbad_name_gaia_alias_supported") is not True
            or M.get("n_original_ztf_catalogues_new")!=8
            or M.get("n_provisional_quality_passed")!=5
            or M.get("n_two_night_pairs_quality_passed")!=1
            or O["fields"][0].get("gaia_dr3_id")!=FT
            or O["fields"][1].get("gaia_dr3_id")!=CIDA):
        raise ValueError("Original SIMBAD alias, native source QA or OID evidence altered")
    if (P.get("original_derived_only_json_sha256")!="3bf45b38745cdea664f82da74912c8c059f0b58897b02eefe86bde182cf319e9"
            or P.get("raw_original_journal_mrt_committed") is not False
            or P.get("third_party_pinned_mirror_full_byte_identity_compared") is not False):
        raise ValueError("Publisher original-source audit provenance was rewritten")
    return {
        "status":"R2_24_SOURCE_SCREENING_ADJUDICATED_NO_GO_PHYSICAL_IDENTITY_OPEN",
        "n_frozen_luhman_gaia_sources_with_original_publisher_rows_verified":24,
        "n_gaia_original_source_ids_retrieved":24,
        "n_original_ztf_positional_query_positions_with_rows":22,
        "n_ztf_provider_unresolved_positions":2,
        "n_independent_gaia_ztf_physical_sources_authenticated":0,
        "n_r3_physical_variability_eligible":0,
        "r2_source_identity_gate_success":False,
        "r2_source_access_and_ambiguity_screen_report_complete":True,
        "r3_scientific_inference_blocked":True,
        "independent_new_astrophysical_discovery_claimed":False,
    }


def main()->None:
    p=argparse.ArgumentParser(description="Fully offline original-publisher and source-locked Taurus R2 24-source GO/NO-GO evidence audit")
    p.add_argument("--root",type=Path,default=Path("."))
    args=p.parse_args()
    print(json.dumps(audit_24_final(args.root),indent=2))


if __name__=="__main__":
    main()
