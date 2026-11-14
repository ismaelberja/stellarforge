"""Taurus R5: bounded, critical literature and independent-science falsification.

Everything counted here is derived from *existing authentic, SHA-anchored*
original-source R2, R3 and R4 research receipts. Denominators deliberately
remain distinct: Gaia physical technical targets, individual ZTF survey
ObjectIDs, and single-epoch source-photometry rows.

The method does NOT certify Gaia↔ZTF physical identity, true stellar
lightcurves, strict source flags, independent instrumental error covariance,
survey-level variability prevalence or discovery.
"""
from __future__ import annotations

from pathlib import Path
import json

from scripts.audit_taurus_r2_24_go_no_go import audit_24_final
from scripts.audit_taurus_r3_six_original_source_receipts import audit_r3_original_six_source_receipts
from scripts.audit_taurus_r4_cadence_feasibility import audit_r4_repo

R2="reports/taurus_variability_r2/R2_FINAL_24_TECHNICAL_SOURCE_ACCESS_AND_IDENTITY_DECISION_NO_RAW.json"
R3="reports/taurus_variability_r3/R3_SIX_ORIGINAL_DR24_FIRST_REQUESTS_NO_RAW.json"
R4="reports/taurus_variability_r4/R4_REAL_ORIGINAL_ZTF_ANNUAL_COVERAGE_AND_SYNTHETIC_1DAY_EXAMPLES_NO_RAW.json"
PUBLISHER="reports/taurus_variability_r2/R2_PUBLISHER_LUHMAN2023_ORIGINAL_24_OF_24_NO_RAW.json"
SEED="data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv"
LITERATURE={
    "luhman_2023_taurus_adopted_member_catalogue":{
        "work":"A Census of the Taurus Star-forming Region and Neighboring Associations with Gaia",
        "year":2023,"doi":"10.3847/1538-3881/ac9da3",
        "reference_url":"https://doi.org/10.3847/1538-3881/ac9da3",
        "role":"Published original adopted Taurus source table: validates catalog-source provenance, not independent Gaia-ZTF physical counterpart",
        "original_data_verified_in_prior_R2":True
    },
    "mas_2026_gaia_ysos_variability":{
        "work":"Exploring the variability of young stars with Gaia DR3 light curves",
        "year":2026,"doi":"10.1051/0004-6361/202554522",
        "reference_url":"https://doi.org/10.1051/0004-6361/202554522",
        "role":"Independent prior work already develops Q-M, GLS and variability/alias methods; explicitly discusses one-day ZTF aliases. No claim of novel method or crossmatch of this particular R1 Taurus cohort",
        "original_data_verified_in_prior_R2":False
    },
    "esa_gaia_dr3_ruwe_definition":{
        "reference_url":"https://gea.esac.esa.int/archive/documentation/GDR3/Gaia_archive/chap_datamodel/sec_dm_main_source_catalogue/ssec_dm_gaia_source.html",
        "role":"RUWE is astrometric single-star-model fit diagnostic, not proof of multiplicity or a calibrated Gaia-to-ZTF physical source association"
    },
    "irsa_ztf_current_public_release":{
        "reference_url":"https://irsa.ipac.caltech.edu/Missions/ztf.html",
        "role":"Original official IRSA DR24 (2026-01-22) survey product origin. Release provenance cannot prove a specific photometry source identity"
    },
    "irsa_ztf_lightcurve_api":{
        "reference_url":"https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html",
        "role":"Exact ZTF ObjectID lightcurve query differs from a positional cone search; same position may have multiple OIDs, not unique Gaia physical stars"
    },
    "irsa_ztf_bit15_and_other_source_flags":{
        "reference_url":"https://irsa.ipac.caltech.edu/data/ZTF/docs/releases/dr06/src/dr06.html",
        "role":"catflags bit15 bad-image quality mask is only an initial QC screen; official source explains catflags=0 is stricter, so pass at bit15 alone is not perfect extraction"
    }
}
SEVERITIES=("PASS_ON_PUBLISHED_SOURCE_SCOPE","LIMITED_TO_ORIGINAL_TECHNICAL_EVIDENCE","NOT_INDEPENDENTLY_VALIDATED","ARCHIVE_ACCESS_UNRESOLVED")
GATE_NAMES=(
    "published_author_gaia_source_membership_row_verified",
    "independently_authenticated_physical_gaia_ztf_source_match",
    "independent_same_field_reference_star_psf_wcs_deblend",
    "full_photometric_source_flags_covariance_and_uncertainty_qualified",
    "true_source_specific_original_visit_times_and_magnitudes_for_periodicity",
    "same_field_magnitude_matched_non_YSO_controls",
    "independent_original_image_and_period_alias_literature_reconciliation",
    "actual_population_selection_function_representative_and_quantified",
)


def _same(d:dict,k:str,v,desc:str)->None:
    if not isinstance(d,dict) or k not in d or type(d[k]) is not type(v) or d[k]!=v:
        raise ValueError(f"{desc} {k}: changed original evidence or unsupported science")


def _rate(n:int,d:int)->dict:
    if type(n) is not int or type(d) is not int or d<=0 or not 0<=n<=d:
        raise ValueError("R5 ratio must use exact non-negative counts and a real source-specific denominator")
    return {"n":n,"N":d,"percent_descriptive_only":round(100*n/d,2)}


def build_r5_critical_falsification(root:Path)->dict:
    root=Path(root).resolve()
    # All three published source receipt audits are executable and fail closed
    # against altered source identity, era/band, attrition and synthetic claims.
    r2a=audit_24_final(root)
    r3a=audit_r3_original_six_source_receipts(root)
    r4a=audit_r4_repo(root)
    r2=json.loads((root/R2).read_text("utf8"))
    r3=json.loads((root/R3).read_text("utf8"))
    r4=json.loads((root/R4).read_text("utf8"))
    pub=json.loads((root/PUBLISHER).read_text("utf8"))
    s=r2["summary"]
    for k,v in (
        ("frozen_technical_cohort",24),
        ("exact_gaia_dr3_sources_retrieved",24),
        ("gaia_only_preliminary_source_qa_pass",17),
        ("gaia_only_source_qa_requiring_review",7),
        ("catalogued_gaia_neighbours_within_5arcsec_target_count",4),
        ("cumulative_positional_irsa_ztf_parsed_target_positions",22),
        ("irsa_target_positions_without_a_parsed_original_response",2),
        ("technical_sources_with_historical_original_science_mask_psfcat_source_images_checked",2),
        ("historical_original_source_image_frames_evaluated",4),
        ("original_journal_table_exact_gaia_ids_and_positions_verified",24),
        ("independently_authenticated_physical_gaia_ztf_counterparts",0),
        ("scientifically_r3_eligible_original_source_lightcurves",0),
        ("merged_original_ztf_objectid_lightcurves",0),
        ("confirmed_new_astrophysical_variables",0),
        ("confirmed_new_astrophysical_companions",0),
    ):_same(s,k,v,"R2 original Gaia technical cohort")
    for k,v in (
        ("original_publisher_source_table_24_rows_verified",True),
        ("full_original_24_source_table_verified_from_accepted_origin",True),
    ):_same(pub,k,v,"Luhman original publisher source")
    _same(pub["attempts"][0],"official_table_adopted_member_rows",532,"original Luhman table")
    _same(pub["attempts"][0],"official_table_gaia_source_ids",467,"original Luhman table")
    _same(r3a,"original_locally_qc_accepted_rows",591,"original R3 ZTF")
    _same(r3a,"original_masked_catflags_bit15_rows",93,"original R3 ZTF")
    _same(r3a,"original_raw_ztf_source_rows_quality_inspected",684,"original R3 ZTF")
    _same(r4a,"real_series_with_two_consecutive_365day_empty_bins",2,"original R4 cadence")
    _same(r4a,"original_true_one_day_spectral_window_measured",False,"original R4")
    _same(r4,"r4_physical_star_variability_blocked",True,"original R4 research decision")
    _same(r4,"real_spectral_window_recovered_from_exact_source_timestamps",False,"original R4 real observations are not publicly available")
    _same(r4,"source_original_context_24_gaia_id_to_ztf_physical_matches_authenticated",0,"original R4 no Gaia-ZTF source matches")
    if (len(r2["sources"])!=24 or len(r3["per_oid_results"])!=6
            or len(r4["original_real_source_observations"])!=3
            or len(r4["original_unavailable_source_OIDs"])!=3
            or any(x["original_physical_gaia_to_ztf_identity_authenticated"] for x in r2["sources"])
            or any(x["physical_gaia_to_this_ztf_oid_counterpart_authenticated"] for x in r3["per_oid_results"])):
        raise ValueError("Source denominator, source ID or physical counterpart fraud")
    if (not r2a["r3_scientific_inference_blocked"]
            or r3["r3_gaia_target_astrophysical_variability_inference_permitted"] is not False
            or any(x["measured_real_one_day_window_power"] is not None for x in
                   (*r4["original_real_source_observations"],*r4["original_unavailable_source_OIDs"]))):
        raise ValueError("A simulated window or archive pass falsely became a physical star claim")
    if (r3["original_success_qc_retained_rows"]+r3["original_success_rejected_catflags_rows"]
            !=r3["original_success_raw_rows"]):
        raise ValueError("Bit15 quality source denominator not conserved")

    # Each fraction is DESCRIPTIVE with its own scientifically distinct
    # denominator; no uncertainty interval or Taurus incidence calculation.
    numerics={
        "technical_seed_ids_vs_original_author_adopted_member_rows":_rate(24,532),
        "technical_seed_ids_vs_author_catalogue_gaia_ids":_rate(24,467),
        "gaia_only_preliminary_quality_pass_of_original_24":_rate(17,24),
        "gaia_astrometry_requires_review_of_original_24":_rate(7,24),
        "gaia_sources_with_neighbour_within_5arcsec_of_original_24":_rate(4,24),
        "gaia_positions_with_any_original_ZTF_positional_rows_of_original_24":_rate(22,24),
        "gaia_physically_identified_with_ZTF_of_original_24":_rate(0,24),
        "original_ZTF_exact_oid_dr24_source_csvs_returned_of_six_fixed_oids":_rate(3,6),
        "original_ZTF_exact_oid_server_timeouts_twice_of_six_fixed_oids":_rate(3,6),
        "original_ztf_catflags_bit15_retained_source_rows_of_684":_rate(591,684),
        "original_ztf_catflags_bit15_rejected_source_rows_of_684":_rate(93,684),
        "retrieved_original_ZTF_OID_curves_with_two_adjacent_empty_365day_bins_of_3":_rate(2,3),
    }
    if numerics["original_ztf_catflags_bit15_retained_source_rows_of_684"]["n"] + numerics[
        "original_ztf_catflags_bit15_rejected_source_rows_of_684"]["n"]!=684:
        raise ValueError("Source-level photometric quality numerator confusion")
    gates=[
        {
            "gate":"published_author_gaia_source_membership_row_verified",
            "status":"PASS_ON_PUBLISHED_SOURCE_SCOPE",
            "support":"24/24 frozen technical Gaia IDs and exact sky positions present in the original author-published Luhman (2023) adopted Taurus member table, SHA pinned",
            "not_supported":"Not a new independent physical Gaia-ZTF crossmatch or re-evaluation of every member's physical classification",
            "next_independent_evidence":"Independent stellar membership/classification only if a claim beyond original author adopted-member provenance is sought",
        },
        {
            "gate":"independently_authenticated_physical_gaia_ztf_source_match",
            "status":"NOT_INDEPENDENTLY_VALIDATED",
            "support":"R2 0/24 exact physical counterpart matches; FT Tau SIMBAD name ↔ Gaia alias is a bibliographic identifier, not an instrumental Gaia-ZTF image validation",
            "not_supported":"No original ZTF source attributed physically to any of the 24 Gaia stars, no original ZTF OID curves combined",
            "next_independent_evidence":"Epoch-propagated Gaia positions with covariance and independent source-level ZTF image/PSF reference-star crossmatch including multiple OID and blends",
        },
        {
            "gate":"independent_same_field_reference_star_psf_wcs_deblend",
            "status":"NOT_INDEPENDENTLY_VALIDATED",
            "support":"Authentic original science+mask+native PSFcat checks performed for four historical images across two technical targets; six later original FT Tau images tested numerically, but same-pipeline reference and same-image residuals only",
            "not_supported":"No calibrated independent reference-star field WCS/PSF covariance and no resolved/blend-free physical target proof",
            "next_independent_evidence":"Independent well-characterised reference stars, per-image astrometric uncertainty and source deblending validation",
        },
        {
            "gate":"full_photometric_source_flags_covariance_and_uncertainty_qualified",
            "status":"LIMITED_TO_ORIGINAL_TECHNICAL_EVIDENCE",
            "support":"Authentic original exact ZTF DR24 OIDs yielded 684 rows and 591 locally accepted under original catflags bit15 quality screen",
            "not_supported":"catflags=0 strict per-source-screen sensitivity, calibrated error covariance, colour terms, source-specific blend contamination and magnitude-matched comparator statistics untested",
            "next_independent_evidence":"Original per-epoch photometry/flags/error covariance; compare bit15-only with strict catflags=0 without retrospectively changing the preregistered primary selection",
        },
        {
            "gate":"true_source_specific_original_visit_times_and_magnitudes_for_periodicity",
            "status":"NOT_INDEPENDENTLY_VALIDATED",
            "support":"Three original OID relative 365-day bin counts and source-reported total spans, including two with consecutive within-span empty year bins",
            "not_supported":"Actual per-visit timestamps, true spectral window, actual periodogram, false alarm probability or physical star variability; R4 1-day window scores SYNTHETIC",
            "next_independent_evidence":"Original per-exposure native time axes, calibrated magnitude/error measurements and independently authenticated physical source",
        },
        {
            "gate":"same_field_magnitude_matched_non_YSO_controls",
            "status":"NOT_INDEPENDENTLY_VALIDATED",
            "support":"No same-field matched non-YSO control sample identified in the immutable R1-R4 source-level evidence",
            "not_supported":"Survey instrumental/brightness-dependent false-positive and selection-effect adjustment",
            "next_independent_evidence":"Preregister magnitude, field, source quality and cadence-matched non-YSO comparison sample with independent Gaia/ZTF physical source identities",
        },
        {
            "gate":"independent_original_image_and_period_alias_literature_reconciliation",
            "status":"NOT_INDEPENDENTLY_VALIDATED",
            "support":"Original images analysed for limited technical subset, and relevant independent published Gaia YSO Q-M GLS comparisons (Mas et al. 2026) explicitly warn of one-day aliases",
            "not_supported":"Per-source independent image-level recalibration, original actual time-series 1-day alias measurements and comparison of any authenticated FT Tau/CIDA 11 periods",
            "next_independent_evidence":"Independent source-resolved original FITS/mask/PSF reference-star validations plus fully authenticated per-epoch period/alias and published comparison",
        },
        {
            "gate":"actual_population_selection_function_representative_and_quantified",
            "status":"NOT_INDEPENDENTLY_VALIDATED",
            "support":"24 technical Gaia targets were fixed in R1 from a previous mirror and not chosen randomly; their original 24/532 and 24/467 ratios are only descriptive",
            "not_supported":"A representative Taurus sample, member completeness, physical regional variable fraction, calibrated sample selection probabilities or confidence intervals for population rates",
            "next_independent_evidence":"Independent complete parent-sample selection function, sensitivity/brightness/crowding modelling and representative sampling if population inference is ever desired",
        },
    ]
    if tuple(g["gate"] for g in gates)!=GATE_NAMES or any(g["status"] not in SEVERITIES for g in gates):
        raise ValueError("R5 frozen cross-domain scientific gate adjudication changed")
    outcomes={
        "r5_methodological_literature_and_falsification_review_complete":True,
        "r5_true_independent_physical_source_validation_pass":False,
        "original_r2_gaia_ztf_physical_counterparts_authenticated":0,
        "r5_claim_of_new_independent_instrument_calibration":False,
        "r5_claim_of_true_gaia_star_period_or_stellar_variability":False,
        "r5_same_field_comparator_controls_done":False,
        "r6_methodological_inconclusive_feasibility_report_can_be_written":True,
        "r6_authentic_new_astrophysical_variable_or_companion_discovery_claim_allowed":False,
        "r6_survey_taurus_variable_incidence_inference_allowed":False,
        "r6_final_author_critical_external_scientific_review_required_for_journal_submissions":True,
    }
    return {
        "schema_version":"stellarforge-taurus-r5-source-verified-selection-literature-falsification-adjudication-v1",
        "date_utc":"2026-11-14",
        "phase":"R5_CRITICAL_LITERATURE_AND_SELECTION_FEASIBILITY_REVIEW_DONE__INDEPENDENT_PHYSICAL_STAR_VALIDATION_NO_GO",
        "original_source_archival_pointers":{
            "r1_frozen_technical_seed":SEED,
            "r2_individual_source_screen":R2,
            "r2_original_publisher_table":PUBLISHER,
            "r3_genuine_original_source_QC":R3,
            "r4_original_source_bincount_and_SYNTHETIC_examples":R4,
            "r2_original_24_actions":43029175432,
            "r2_original_publisher_crosscheck_actions":43499836719,
            "r3_first_original_DR24_actions":43593335135,
            "r3_original_timeout_only_retry_actions":43593994009,
            "r4_original_source_derived_CI_actions":43596705130,
        },
        "external_primary_literature_and_provider_docs":LITERATURE,
        "denominator_locked_descriptive_summary_not_population_inference":numerics,
        "falsification_gates":gates,
        "final_scientific_interpretation":outcomes,
        "evidence_caveats":[
            "Luhman 2023 original author Table 2 source IDs and positions for 24/24 were checked; this does not establish a new individual physical star classification or any Gaia-to-ZTF source match.",
            "Mas et al. (2026), A&A 705 A172 already uses Gaia YSO Q-M, GLS and structure functions and discusses ZTF one-day aliases. This methodological comparison does not include a verified original FT Tau/ZTF crossmatch in this study.",
            "Gaia RUWE is a single-star astrometric solution goodness-of-fit; high RUWE marks review and is NOT proof of an astrophysical companion or a ZTF counterpart failure.",
            "Original IRSA ZTF catflags bit15 masking can leave other quality flag bits set; a 591/684 retention statistic is not an exhaustive strict catflags=0 data-quality certificate.",
            "The R1 technical cohort is non-random and nonrepresentative; 24/532, 24/467 and 2/3 are descriptive ratios, not corrected Taurus completeness or variability rates.",
            "No actual per-epoch times or calibrated source magnitudes are available in the public immutable R3/R4 derived-only receipts. R4 1-day spectral-window numeric demonstrations use imaginary timestamp allocations, not true observed source windows.",
            "Three of six original survey ObjectIDs had network timeouts twice, so their number of real observations and physical variability remain unknown, not zero or non-variable.",
            "The completed R5 work is a critical falsification / literature / selection-bias feasibility screen with a scientific NO-GO for independent physical source and stellar variability validation; this remains an open scientific dependency for positive R6 astrophysics.",
            "No raw survey FITS CCDs, original full photometry rows/individual timestamps, published article full texts or unpublished ALMA/TFM science have been copied or committed.",
        ],
    }
