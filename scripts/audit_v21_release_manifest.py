"""StellarForge v2.1 portfolio engineering release: offline evidence contract.

Checks *existing* committed original ZTF/Gaia/SIMBAD derived-only receipts
against a versioned portfolio manifest and the immutable v2.0 baseline.
Does not access archives or independently authenticate astrophysical sources.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from stellarforge import __version__
# Direct invocation (python scripts/audit_v21_release_manifest.py) runs with
# scripts/ on sys.path, while pytest imports the scripts namespace from root.
# Preserve both interfaces without requiring an extra installed package.
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.audit_v2_release_manifest import audit_release_manifest

RELEASE_VERSION = "2.1.0"
PRIOR_VERSION = "2.0.0"
RELEASE_DATE = "2026-11-13"
SCOPE = "PUBLIC_REPRODUCIBLE_RESEARCH_SOFTWARE_PORTFOLIO_NOT_NEW_ASTROPHYSICAL_DISCOVERY"
TARGET = "149623711269425408"
PRIOR_MAIN_RUN = 43315134009
PRIOR_MAIN_TESTS = 1051
SIX_SPATIAL_RUN = 43310945601
SIMBAD_RUN = 43314507016
GAUSSIAN_RUN = 43279744985
CHI_RUN = 43275404347
ORIGINAL_GAIA_SHA = "399b5498d8d8a8a646073dfc029895ed64902940896d1789c63833a18074b642"
SVG_NS = "{http://www.w3.org/2000/svg}"
PRE_RELEASE_EVIDENCE = (
    "RELEASE_MANIFEST_v2.0.json",
    "reports/selection_bias_v1.1/REPORT.md",
    "reports/masked_spatial_psf_v1.16/REAL_ZTF_PIXEL_RESIDUALS_EVIDENCE.md",
    "reports/taurus_variability_r2/FTTAU_SIX_ORIGINAL_ZTF_CHI_BLIND_REFERENCES_NO_RAW.json",
    "reports/taurus_variability_r2/FTTAU_SIX_ORIGINAL_ZTF_INDEPENDENT_GAUSSIAN_PIXELS_NO_RAW.json",
    "reports/taurus_variability_r2/FTTAU_SIX_ORIGINAL_NATIVE_SPATIAL_DAOPHOT_PSF_NO_RAW.json",
    "reports/taurus_variability_r2/FTTAU_SIMBAD_EXACT_GAIA_NAME_ALIAS_NO_RAW.json",
    "research/taurus_variability/R2_REAL_FTTAU_SIMBAD_GAIA_EXACT_ALIAS_RESULTS.md",
    "research/taurus_variability/R2_REAL_FTTAU_SIX_NATIVE_SPATIAL_DAO_RESULTS.md",
    "docs/figures/fttau-six-original-native-spatial-psf-quality-v21.svg",
)
EXPECTED_ROOT_KEYS = frozenset((
    "schema_version", "software_version", "release_date_utc", "release_scope",
    "historical_release_baseline", "original_followup_2026_11_12",
    "engineering_validation", "science_claim_boundaries", "visual_evidence",
    "release_evidence_paths", "transparent_ai_assistance", "explicit_unresolved_science",
))
SCIENCE_FALSE_GATES = frozenset((
    "all_four_ztf_object_ids_authenticated_as_one_physical_gaia_star",
    "independent_gaia_to_ztf_per_epoch_physical_source_identification_confirmed",
    "independent_psf_wcs_instrumental_covariance_calibrated",
    "authentic_original_daophot_psf_training_star_roster_confirmed",
    "new_astrophysical_variability_or_companion_confirmed",
    "original_ztf_oid_lightcurves_merged",
    "r2_scientific_source_identity_finished",
    "r3_astrophysical_inference_ready",
    "new_cida11_whole_star_empirical_psf_live_pilot_completed",
    "previous_original_native_chi_gate_relaxed",
))


def _same(obj: dict, field: str, expected, where: str) -> None:
    if (not isinstance(obj, dict) or field not in obj
            or type(obj[field]) is not type(expected) or obj[field] != expected):
        raise ValueError(f"{where}.{field} inconsistent with original source evidence")


def _open_json(root: Path, rel: str) -> dict:
    src=root/rel
    if (not isinstance(rel,str) or Path(rel).is_absolute()
            or ".." in Path(rel).parts or src.is_symlink()
            or not src.is_file() or not src.resolve().is_relative_to(root)):
        raise ValueError("Missing/unsafe original research evidence path")
    return json.loads(src.read_text(encoding="utf-8"))


def _hash64(value: object) -> bool:
    return isinstance(value,str) and bool(re.fullmatch(r"[0-9a-f]{64}",value))


def audit_v21_release_manifest(m: dict, *, root: Path) -> dict:
    """Fail-closed static/original-derived source receipt verification, offline."""
    root=Path(root).resolve()
    if not isinstance(m,dict) or set(m)!=EXPECTED_ROOT_KEYS:
        raise ValueError("v2.1 engineering manifest has missing/additional claim fields")
    for key,expected in (
        ("schema_version","stellarforge-v2.1-engineering-portfolio-evidence-contract-v1"),
        ("software_version",RELEASE_VERSION),
        ("release_date_utc",RELEASE_DATE),
        ("release_scope",SCOPE),
    ):
        _same(m,key,expected,"manifest")
    current=(root/"pyproject.toml").read_text(encoding="utf-8")
    if (not re.search(r'(?m)^version = "2\.1\.0"$',current)
            or __version__!=RELEASE_VERSION
            or f"version: \"{RELEASE_VERSION}\"" not in (root/"CITATION.cff").read_text(encoding="utf-8")):
        raise ValueError("Current package/CLI/citation versions not v2.1.0")

    paths=m["release_evidence_paths"]
    if (not isinstance(paths,list) or paths!=list(PRE_RELEASE_EVIDENCE)
            or len(set(paths))!=len(paths)):
        raise ValueError("v2.1 original evidence links omitted or unexpected")
    for rel in paths:
        path=root/rel
        if (Path(rel).is_absolute() or ".." in Path(rel).parts or path.is_symlink()
                or not path.is_file() or not path.resolve().is_relative_to(root)):
            raise ValueError("Original evidence/source image figure missing or unsafe")
        if path.suffix.lower() in (".fits",".csv",".zip",".parquet"):
            raise ValueError("Original source payload added to public manifest")

    archived=_open_json(root,PRE_RELEASE_EVIDENCE[0])
    legacy=audit_release_manifest(archived,root=root)
    if (legacy["software_version"]!=PRIOR_VERSION
            or legacy["historical_real_source_pixel_fits"]!=16
            or legacy["historical_original_exposures"]!=4):
        raise ValueError("Retrospective v2.0 source evidence altered")
    prior=m["historical_release_baseline"]
    old_counts=archived["historical_real_evidence"]
    expected_baseline={
        "previous_release_manifest":"RELEASE_MANIFEST_v2.0.json",
        "previous_release_version":"2.0.0",
        "prior_taurus_catalogue_mirror_rows":old_counts["catalogue_mirror_rows"],
        "prior_catalogue_gaia_ids":old_counts["catalogue_gaia_id_rows"],
        "prior_original_irsa_positional_rows":old_counts["original_irsa_positional_query_rows"],
        "prior_four_historic_ztf_science_exposures":old_counts["original_ztf_science_exposures"],
        "prior_sixteen_original_source_image_profile_fits":old_counts["original_masked_psf_source_pixel_fits"],
        "prior_thirteen_provisional_pixel_screen_passes":old_counts["provisional_source_pixel_residual_quality_passes"],
        "prior_three_residual_reviews":old_counts["source_pixel_residual_review_required"],
    }
    if (not isinstance(prior,dict) or set(prior)!=set(expected_baseline)):
        raise ValueError("Historical v2.0 provenance keys changed")
    for k,v in expected_baseline.items(): _same(prior,k,v,"historical_release_baseline")

    vals=m["original_followup_2026_11_12"]
    if (not isinstance(vals,dict) or set(vals)!={
        "target_gaia_dr3_id","frozen_original_ztf_exposure_count",
        "frozen_original_same_oid_early_late_pairs",
        "original_chi_blind_reference","original_analytic_gaussian_pixel_pilot",
        "original_spatial_daophot_psf","external_curated_simbad_alias",
        "original_ztf_source_qa_provisional_pass_count",
        "original_ztf_source_qa_failed_count",
        "original_valid_two_night_source_pairs_count",
        "original_total_two_night_source_pair_groups_count"}):
        raise ValueError("v2.1 followup must be separated by distinct original-data studies")
    for k,v in (
        ("target_gaia_dr3_id",TARGET),
        ("frozen_original_ztf_exposure_count",6),
        ("frozen_original_same_oid_early_late_pairs",3),
        ("original_ztf_source_qa_provisional_pass_count",5),
        ("original_ztf_source_qa_failed_count",3),
        ("original_valid_two_night_source_pairs_count",1),
        ("original_total_two_night_source_pair_groups_count",4),
    ): _same(vals,k,v,"original_followup")

    chi_m=vals["original_chi_blind_reference"]
    g_m=vals["original_analytic_gaussian_pixel_pilot"]
    spatial_m=vals["original_spatial_daophot_psf"]
    alias_m=vals["external_curated_simbad_alias"]
    expected_source_rels=PRE_RELEASE_EVIDENCE[3:7]
    for component,rel,run in zip((chi_m,g_m,spatial_m,alias_m),expected_source_rels,
                                 (CHI_RUN,GAUSSIAN_RUN,SIX_SPATIAL_RUN,SIMBAD_RUN)):
        _same(component,"source_path",rel,"original_workflow")
        _same(component,"original_run_id",run,"original_workflow")
    chi=_open_json(root,chi_m["source_path"])
    gauss=_open_json(root,g_m["source_path"])
    spatial=_open_json(root,spatial_m["source_path"])
    alias=_open_json(root,alias_m["source_path"])

    for component,k,v in (
        (chi_m,"image_catalogue_rows_in_reference_cohorts",1095),
        (chi_m,"image_catalogue_reference_records_chi_below_0p5",240),
        (chi_m,"unique_physical_reference_stars_confirmed",False),
        (g_m,"numeric_analytic_gaussian_pixel_fits",4),
        (g_m,"constrained_optimizer_failures",2),
        (g_m,"calibrated_original_native_psf_model",False),
        (spatial_m,"original_native_psfcat_byte_verified",6),
        (spatial_m,"original_science_mask_pairs_byte_verified",6),
        (spatial_m,"original_spatial_dao_models_parsed",6),
        (spatial_m,"same_source_spatial_psf_numeric_fits",6),
        (spatial_m,"provisional_same_source_heldout_pixel_residual_passes",4),
        (spatial_m,"same_source_pixel_residual_reviews_required",2),
        (spatial_m,"independent_different_star_psf_calibration",False),
        (alias_m,"simbad_unique_exact_gaia_records",1),
        (alias_m,"simbad_unique_exact_ft_tau_name_records",1),
        (alias_m,"both_queries_same_unique_external_object",True),
        (alias_m,"external_catalogue_main_id","V* FT Tau"),
        (alias_m,"physical_gaia_to_original_ztf_counterpart_confirmed",False),
    ):_same(component,k,v,"original_workflow")
    for record,expected_run,sha_field in (
        (chi,CHI_RUN,"original_gaia_response_sha256"),
        (gauss,GAUSSIAN_RUN,"original_gaia_tap_sha256"),
        (spatial,SIX_SPATIAL_RUN,"original_gaia_response_sha256"),
        (alias,SIMBAD_RUN,"original_gaia_dr3_five_parameter_tap_sha256"),
    ):
        run=record.get("original_data_run_id",record.get("original_data_github_action_run_id",record.get("original_run_id")))
        if type(run) is not int or run!=expected_run or record.get(sha_field)!=ORIGINAL_GAIA_SHA:
            raise ValueError("External original Gaia/IRSA/CDS workflow provenance changed")
    for obj,k,v in (
        (chi,"sum_control_source_records_across_six_images",1095),
        (chi,"sum_controls_chi_below_0p5",240),
        (chi,"n_original_byte_sha_verified_ztf_full_psfcats",6),
        (gauss,"n_byte_verified_original_native_psfcats",6),
        (gauss,"n_original_science_mask_pairs_downloaded_and_inspected",6),
        (gauss,"n_valid_independent_analytic_gaussian_fits",4),
        (gauss,"n_gaussian_numerical_failures",2),
        (spatial,"original_full_native_psfcats_sha_verified",6),
        (spatial,"original_science_mask_pairs_sha_verified",6),
        (spatial,"original_native_spatial_daophot_models_parsed",6),
        (spatial,"original_native_spatial_same_source_pixel_numeric_fits",6),
        (spatial,"original_native_spatial_same_source_pixel_provisional_quality_passes",4),
        (spatial,"original_native_spatial_same_source_pixel_residual_review_required",2),
        (alias,"n_gaia_exact_identifier_unique_simbad_objects",1),
        (alias,"n_ft_tau_exact_name_unique_simbad_objects",1),
        (alias,"both_original_simbad_queries_same_external_object",True),
        (alias,"simbad_external_main_identifier","V* FT Tau"),
    ):_same(obj,k,v,"frozen_original_derived_receipt")
    for obj,k in (
        (chi,"scientific_R2_complete"),
        (gauss,"scientific_r2_complete"),
        (spatial,"scientific_r2_complete"),
        (alias,"scientific_r2_complete"),
    ):_same(obj,k,False,"original_science_not_complete")

    # Cross-check the SIX same actual original exposures, not six new
    # objects or a six-epoch expansion of the old four historical images.
    chi_rows=[(grp["band"],str(grp["field"]),ep) for grp in
              chi["original_exact_3_ztf_oid_early_late_pairs"]
              for ep in grp["epochs"]]
    gauss_rows=gauss["six_immutable_original_data_exposure_derived_summary"]
    spatial_rows=spatial["original_six_exact_exposure_derived_only"]
    if not (len(chi_rows)==len(gauss_rows)==len(spatial_rows)==6):
        raise ValueError("Six original fixed image receipts missing")
    total_n=total_low=passes=reviews=0
    for (band,field,a),g,s in zip(chi_rows,gauss_rows,spatial_rows):
        if (band!=g["band"] or field!=str(g["field"]) or band!=s["band"]
                or field!=str(s["field"]) or a["mjd"]!=g["mjd"]
                or a["mjd"]!=s["original_mjd"] or a["day"]!=g["fracday"]
                or a["day"]!=s["original_filefracday"] or a["sha"]!=g["native_sha"]
                or a["sha"]!=s["original_full_psfcat_sha256"]
                or g["science_sha"]!=s["original_science_cutout_sha256"]
                or g["mask_sha"]!=s["original_same_exposure_mask_sha256"]
                or a["chi"]!=s["original_native_nearest_source_chi"]):
            raise ValueError("Unmatched original exposure/source/PSF/science/mask receipts")
        if not all(_hash64(s[k]) for k in (
            "original_native_spatial_dao_psf_sha256",
            "original_native_field_center_psf_sha256","original_science_cutout_sha256")):
            raise ValueError("Original ZTF spatial PSF model hash malformed")
        total_n+=a["n"];total_low+=a["below"]
        internal=s["same_image_spatial_psf_residual_screen_status"]
        if internal=="PROVISIONAL_ORIGINAL_MASKED_PSF_PIXEL_RESIDUAL_SCREEN_PASSED":
            passes+=1
        elif internal=="ORIGINAL_MASKED_PSF_PIXEL_RESIDUAL_REVIEW_REQUIRED":
            reviews+=1
        else: raise ValueError("Unexpected source pixel residual status")
        if bool(s["original_native_chi_source_quality_pass_unchanged"]) is not (a["chi"]>=.5):
            raise ValueError("Retroactive source quality classification changed")
    if total_n!=1095 or total_low!=240 or (passes,reviews)!=(4,2):
        raise ValueError("Source-control count and heldout numeric results changed")

    if (alias.get("exact_gaia_dr3_source_id")!=TARGET
            or alias.get("external_curated_simbad_name_gaia_alias_supported") is not True
            or alias.get("physical_gaia_to_each_original_ztf_source_identification_confirmed") is not False
            or alias.get("original_gaia_exact_identifier_simbad_csv_sha256") !=
               alias.get("original_historical_ft_tau_name_simbad_csv_sha256")
            or not _hash64(alias.get("original_gaia_exact_identifier_simbad_csv_sha256"))):
        raise ValueError("External SIMBAD curated name alias evidence changed")
    if (not spatial.get("original_native_candidate_5_of_8_pass_3_of_8_fail_unchanged")
            or not spatial.get("original_1_of_4_quality_accepted_two_night_pairs_unchanged")
            or alias.get("n_original_ztf_oid_lightcurves_merged")!=0):
        raise ValueError("Original ZTF source science selection changed")

    boundaries=m["science_claim_boundaries"]
    if not isinstance(boundaries,dict) or set(boundaries)!=SCIENCE_FALSE_GATES|{"catalogue_name_alias_verified"}:
        raise ValueError("Scientific claim boundaries altered")
    _same(boundaries,"catalogue_name_alias_verified",True,"science_claim_boundaries")
    for key in SCIENCE_FALSE_GATES:_same(boundaries,key,False,"science_claim_boundaries")

    engineering=m["engineering_validation"]
    if not isinstance(engineering,dict) or set(engineering)!={
        "pre_v21_current_main_baseline_run_id","pre_v21_current_main_baseline_passed_tests",
        "pre_v21_baseline_has_synthetic_and_original_source_receipt_tests",
        "final_v21_git_main_ci_required",
        "current_package_offline_unit_suite_requires_no_new_live_survey_requests"}:
        raise ValueError("Engineering verification claims missing")
    for k,v in (
        ("pre_v21_current_main_baseline_run_id",PRIOR_MAIN_RUN),
        ("pre_v21_current_main_baseline_passed_tests",PRIOR_MAIN_TESTS),
        ("pre_v21_baseline_has_synthetic_and_original_source_receipt_tests",True),
        ("final_v21_git_main_ci_required",True),
        ("current_package_offline_unit_suite_requires_no_new_live_survey_requests",True),
    ):_same(engineering,k,v,"engineering_validation")

    visual=m["visual_evidence"]
    if not isinstance(visual,dict) or set(visual)!={
        "new_real_derived_only_chart","chart_depicts_original_survey_pixels",
        "chart_reuses_six_original_dated_image_derived_only_receipts",
        "conceptual_webps_are_telescope_photos"}:
        raise ValueError("v2.1 visual evidence provenance missing")
    _same(visual,"new_real_derived_only_chart",PRE_RELEASE_EVIDENCE[-1],"visual")
    for k,v in (
        ("chart_depicts_original_survey_pixels",False),
        ("chart_reuses_six_original_dated_image_derived_only_receipts",True),
        ("conceptual_webps_are_telescope_photos",False),
    ):_same(visual,k,v,"visual")
    svg=(root/visual["new_real_derived_only_chart"]).read_text(encoding="utf8")
    figure=ET.fromstring(svg)
    if (figure.tag!=SVG_NS+"svg" or figure.attrib.get("role")!="img"
            or figure.find(SVG_NS+"title") is None
            or figure.find(SVG_NS+"desc") is None
            or figure.findall(".//"+SVG_NS+"image")
            or figure.findall(".//"+SVG_NS+"script")):
        raise ValueError("Portfolio chart source/accessibility/provenance invalid")
    for row in spatial_rows:
        if f"{row['same_source_checkerboard_holdout_rms_over_sky_mad']:.3f}" not in svg:
            raise ValueError("Portfolio source chart not traceable to original six data rows")
    for word in ("NOT", "same-source", "not an independent"):
        if word.lower() not in svg.lower():
            raise ValueError("Figure fails original ZTF source science caveat")

    notes=m["explicit_unresolved_science"]
    if (not isinstance(notes,list) or len(notes)<5
            or any(not isinstance(x,str) or len(x)<35 for x in notes)):
        raise ValueError("Independently unresolved science missing")
    ai=m["transparent_ai_assistance"]
    if not isinstance(ai,str) or not ("AI" in ai and "Scientific direction" in ai):
        raise ValueError("AI-assisted software provenance omitted")
    readme=(root/"README.md").read_text(encoding="utf8")
    for term in ("StellarForge v2.1","RELEASE_MANIFEST_v2.1.json",
                 "RELEASE_MANIFEST_v2.0.json",PRE_RELEASE_EVIDENCE[-1],
                 "docs/V21_PORTFOLIO_CV_ES_EN.md","docs/V21_GUIA_ES.md"):
        if term not in readme:
            raise ValueError("Public v2.1 README missing current version/source evidence")
    return {
        "status":"V21_ENGINEERING_PORTFOLIO_EVIDENCE_VERIFIED_NO_ASTROPHYSICAL_DISCOVERY",
        "software_version":RELEASE_VERSION,
        "previous_v20_manifest_original_claim_counts_preserved":True,
        "n_new_six_epoch_original_source_psfcat_hashes_cross_reconciled":6,
        "n_native_spatial_same_image_provisional_residual_passes":passes,
        "n_native_spatial_same_image_residual_reviews":reviews,
        "n_chi_blind_original_reference_catalogue_entries":total_n,
        "n_chi_blind_original_reference_entries_below_prior_lower_gate":total_low,
        "external_name_gaia_simbad_alias_supported":True,
        "original_ztf_per_source_physical_identity_authenticated":False,
        "new_astrophysical_discovery_claimed":False,
        "n_original_evidence_paths_checked":len(paths),
        "github_final_main_ci_still_required":True,
    }


def main()->None:
    ap=argparse.ArgumentParser(description="Offline v2.1 software-only portfolio evidence contract; no original downloads")
    ap.add_argument("--manifest",type=Path,default=Path("RELEASE_MANIFEST_v2.1.json"))
    ap.add_argument("--root",type=Path,default=Path("."))
    args=ap.parse_args()
    print(json.dumps(audit_v21_release_manifest(
        json.loads(args.manifest.read_text(encoding="utf8")),
        root=args.root),indent=2))


if __name__=="__main__":
    main()
