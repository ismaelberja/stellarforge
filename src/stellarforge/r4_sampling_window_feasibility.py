"""R4: observationally grounded *technical* ZTF cadence feasibility only.

True per-visit timestamps / real instrumental spectral windows are NOT
available in the frozen, no-raw R3 scientific evidence. This module only
counts authentic source-level original 365-day bins and makes an explicit
proof by construction using TWO wholly SYNTHETIC observing schedules
consistent with those same coarse bins and first-to-last time span.

No photometry, true source-epoch timing, real stellar period, physical
Gaia-ZTF source authentication, or astrophysical FAP is inferred.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import math
import random

from .r3_original_oid_coverage import FIXED_GROUPS, COLLECTION

YEAR_BIN_DAYS = 365.0
SYNTHETIC_TEST_PERIOD_DAYS = 1.0
VALID_REPORTED_CLOCK = "MJD"
FIRST_RUN = 43593335135
RETRY_RUN = 43593994009
FIRST_SHA = "6e9e1cdbba946d9f7c5036e74a42917bb4011530dfec1d289b4b30c47f393049"
RETRY_SHA = "69f37df9f57c2dc49e4636740fb74c8c429d67e3d250b92201696edd26d89104"

R4_STUDY_STATUS = "R4_OBSERVED_ZTF_BINS_AND_SYNTHETIC_WINDOW_NON_IDENTIFIABILITY__NOT_PHYSICAL_STELLAR_VARIABILITY"


def _expect(actual:object, expected:object, msg:str)->None:
    if type(actual) is not type(expected) or actual != expected:
        raise ValueError(msg)


def _nonempty_bins(ids:list[int])->int:
    return sum(v>0 for v in ids)


def _longest_zero_bins(ids:list[int])->int:
    longest=run=0
    for v in ids:
        if v==0:
            run+=1
            longest=max(run,longest)
        else:
            run=0
    return longest


def synthetic_hypothetical_visit_offsets(
    original_365_day_bin_counts:list[int], original_time_span_days:float,
    original_oid:str, *, construction:str,
)->tuple[float,...]:
    """Return *invented* days relative to first visit, not real source epochs.

    Both variants exactly reproduce each input 365-day-bin count and the
    exact first-to-last span. A dense integer-day grid gives strong
    artificial 1-day coherence; source-seeded fractional-day points often
    give very different coherence. Neither is an observed ZTF schedule.
    """
    if construction not in ("SYNTHETIC_DAILY_GRID", "SYNTHETIC_SUBDAY_DIVERSE"):
        raise ValueError("Undefined synthetic construction")
    if (not isinstance(original_365_day_bin_counts,list)
            or not original_365_day_bin_counts
            or any(type(v) is not int or v<0 or v>365
                   for v in original_365_day_bin_counts)):
        raise ValueError("Synthetic construction requires bounded nonnegative integer bin counts")
    n=sum(original_365_day_bin_counts)
    span=float(original_time_span_days)
    if (n<2 or not math.isfinite(span) or span<=0
            or original_365_day_bin_counts[0]==0
            or original_365_day_bin_counts[-1]==0
            or not (YEAR_BIN_DAYS*(len(original_365_day_bin_counts)-1)<=span
                    <YEAR_BIN_DAYS*len(original_365_day_bin_counts))):
        raise ValueError("Synthetic sample counts / original span are not mutually consistent")
    if not isinstance(original_oid,str) or not original_oid.isascii() or not original_oid.isdigit():
        raise ValueError("Synthetic schedule needs frozen original survey ObjectID")
    seed=int.from_bytes(
        hashlib.sha256((original_oid+"/r4/subday/v1").encode("utf8")).digest()[:8],
        "big"
    )
    rng=random.Random(seed)
    times=[]
    for i,original_n in enumerate(original_365_day_bin_counts):
        if original_n==0:
            continue
        low=YEAR_BIN_DAYS*i
        high=min(YEAR_BIN_DAYS*(i+1),span)
        # The observed total span forces a sample exactly at 0 and span.
        pinned=[0.0] if i==0 else []
        if i==len(original_365_day_bin_counts)-1:
            pinned.append(span)
        to_synthesize=original_n-len(pinned)
        if to_synthesize<0 or high<=low:
            raise ValueError("Pinnable original schedule geometry invalid")
        if construction=="SYNTHETIC_DAILY_GRID":
            integer_days=list(range(math.floor(low)+1, math.ceil(high)))
            if len(integer_days)<to_synthesize:
                raise ValueError("Not enough independent integer offsets for hypothetical daily-grid sampling")
            # Spread the synthetic days through the occupied bin without
            # manufacturing any original per-epoch timestamps.
            chosen=[
                integer_days[((2*k+1)*len(integer_days))//(2*to_synthesize)]
                for k in range(to_synthesize)
            ] if to_synthesize else []
            if len(chosen)!=len(set(chosen)):
                raise ValueError("Synthetic grid duplicated a date")
            new=[float(x) for x in chosen]
        else:
            # Different sub-day phases produce a different hypothetical
            # 1-day spectral window. This is *not* a statistical FAP.
            new=[low + (high-low)*(.000001 + .999998*rng.random())
                 for _ in range(to_synthesize)]
        times.extend([*pinned,*new])
    times.sort()
    if len(times)!=n or times[0]!=0.0 or times[-1]!=span:
        raise ValueError("Synthetic schedule failed to reproduce original total count/span")
    actual=Counter(min(int(x//YEAR_BIN_DAYS),len(original_365_day_bin_counts)-1)
                   for x in times)
    if [actual.get(i,0) for i in range(len(original_365_day_bin_counts))]!=original_365_day_bin_counts:
        raise ValueError("Synthetic schedule failed to reproduce original per-bin counts")
    return tuple(times)


def synthetic_one_day_window_power(times:tuple[float,...])->float:
    """Synthetic |N^-1 sum exp(2pi*i*t/1.0 day)|^2; NEVER observed."""
    if len(times)<2 or not all(math.isfinite(t) for t in times):
        raise ValueError("Invalid synthetic test schedule")
    re=math.fsum(math.cos(math.tau*t/SYNTHETIC_TEST_PERIOD_DAYS) for t in times)/len(times)
    im=math.fsum(math.sin(math.tau*t/SYNTHETIC_TEST_PERIOD_DAYS) for t in times)/len(times)
    power=re*re+im*im
    if not 0<=power<=1+1e-10:
        raise ValueError("Synthetic window power out of theoretical range")
    return max(0.0,min(1.0,power))


def r4_technical_sampling_feasibility(
    r3_first:dict, r3_retry:dict, r3_source_audit:dict,
)->dict:
    """No original remote source calls: evidence derived from frozen R3 receipts."""
    if (not isinstance(r3_first,dict) or not isinstance(r3_retry,dict)
            or not isinstance(r3_source_audit,dict)):
        raise ValueError("Original source evidence objects required")
    for obj,k,v in (
        (r3_first,"original_workflow_run_id",FIRST_RUN),
        (r3_first,"original_derived_only_artifact_zip_sha256",FIRST_SHA),
        (r3_first,"original_exact_requests",6),
        (r3_first,"original_http_success_sources",3),
        (r3_first,"original_timeout_sources",3),
        (r3_first,"original_success_raw_rows",684),
        (r3_first,"original_success_qc_retained_rows",591),
        (r3_first,"original_success_rejected_catflags_rows",93),
        (r3_first,"query_public_collection",COLLECTION),
        (r3_first,"original_gaia_to_ztf_physical_associations_confirmed",0),
        (r3_retry,"original_recovery_workflow_run_id",RETRY_RUN),
        (r3_retry,"original_recovery_artifact_zip_sha256",RETRY_SHA),
        (r3_retry,"n_recovered_original_public_dr24_source_csv",0),
        (r3_retry,"all_second_retries_original_ztf_provider_timeout_not_scientific_non_detection",True),
        (r3_retry,"original_gaia_to_ztf_physical_counterparts_authenticated",0),
        (r3_source_audit,"status","R3_ORIGINAL_SIX_OID_TECHNICAL_PHOTOMETRY_AUDIT_PARTIAL__ORIGINAL_PROVIDER_TIMEOUTS_NO_PHYSICAL_SOURCE_MATCH"),
        (r3_source_audit,"original_dr24_exact_oid_source_csv_successful",3),
        (r3_source_audit,"original_locally_qc_accepted_rows",591),
        (r3_source_audit,"original_physical_gaia_ztf_sources_authenticated",0),
        (r3_source_audit,"r3_physical_stellar_variability_science_eligible",False),
    ):
        _expect(obj.get(k),v,f"Original source evidence or physical identity claim changed: {k}")
    first_rows=r3_first.get("per_oid_results")
    retry_rows=r3_retry.get("original_timeout_rows")
    if (not isinstance(first_rows,list) or len(first_rows)!=6
            or not isinstance(retry_rows,list) or len(retry_rows)!=3):
        raise ValueError("Exact six original source IDs and three original timeout confirmations required")
    output=[]
    for i,(name,gaia,oid,band,original_r2_rows) in enumerate(FIXED_GROUPS):
        item=first_rows[i]
        for key,val in (
            ("original_technical_label",name),
            ("gaia_id_reference_not_a_physical_match",gaia),
            ("original_frozen_ztf_oid",oid),
            ("original_frozen_filter",band),
            ("physical_gaia_to_this_ztf_oid_counterpart_authenticated",False),
        ):
            _expect(item.get(key),val,"R4 original R3 identity/order/group changed")
        base={
            "original_ztf_oid":oid,
            "original_ztf_filter":band,
            "technical_r2_gaia_context_id_NOT_physically_identified":gaia,
            "previous_original_R3_first_run_id":FIRST_RUN,
            "original_physical_gaia_ztf_counterpart_confirmed":False,
            "scientific_stellar_period_analysis_authorized":False,
        }
        if i>=3:
            rr=retry_rows[i-3]
            for k,v in (
                ("oid",oid),("band",band),
                ("original_first_outcome","TimeoutError"),
                ("original_second_outcome","TimeoutError"),
                ("second_original_response_sha256",None),
            ):
                _expect(rr.get(k),v,"Original DR24 retry request status changed")
            _expect(item.get("original_query_status"),"ORIGINAL_PROVIDER_NETWORK_FAILURE",
                    "Original ZTF unavailable source made available after the fact")
            _expect(item.get("original_error_type"),"TimeoutError",
                    "Original ZTF provider outage was relabelled")
            output.append({
                **base,
                "technical_source_outcome":"ARCHIVE_UNAVAILABLE_TWO_PROVIDER_TIMEOUTS",
                "technical_source_qc_accepted_epochs":None,
                "n_observed_relative_365day_bins":None,
                "n_empty_relative_365day_bins":None,
                "cadence_metric_computable":False,
                "synthetic_1day_window_example_available":False,
                "original_retry_run_id":RETRY_RUN,
            })
            continue
        _expect(item.get("original_query_status"),"ORIGINAL_ZTF_EXACT_OID_CSV_PARSED_AND_QC_AUDITED",
                "Original R3 source CSV unavailable")
        _expect(item.get("original_time_system"),VALID_REPORTED_CLOCK,
                "Reported original time system unexpectedly changed")
        _expect(item.get("provisional_technical_30visit_90day_pass"),True,
                "Original R3 technical source gate was retroactively rejected")
        b=item.get("original_qc_365day_bin_counts")
        n=item.get("original_local_qc_accepted_rows")
        raw=item.get("original_provider_raw_rows")
        masked=item.get("original_local_catflags_32768_masked_rows")
        span=item.get("original_qc_time_span_days")
        if (not isinstance(b,list) or not b
                or any(type(k) is not int or k<0 for k in b)
                or not isinstance(n,int) or not isinstance(raw,int)
                or not isinstance(masked,int) or n<30 or span<90
                or sum(b)!=n or raw!=n+masked or raw!=original_r2_rows):
            raise ValueError("Original source/quality/bin count or fixed R1 thresholds inconsistent")
        daily=synthetic_hypothetical_visit_offsets(b,span,oid,construction="SYNTHETIC_DAILY_GRID")
        diverse=synthetic_hypothetical_visit_offsets(b,span,oid,construction="SYNTHETIC_SUBDAY_DIVERSE")
        p_daily=round(synthetic_one_day_window_power(daily),6)
        p_diverse=round(synthetic_one_day_window_power(diverse),6)
        output.append({
            **base,
            "technical_source_outcome":"ORIGINAL_SOURCE_DR24_QC_ACCEPTED_SAMPLING_BINS__NOT_GAIA_STAR",
            "original_source_rows":raw,
            "technical_source_qc_accepted_epochs":n,
            "original_source_catflags_32768_rejected_rows":masked,
            "source_quality_retention_fraction":round(n/raw,6),
            "original_first_to_last_accepted_visit_span_days":span,
            "mean_QC_visits_per_365day_over_total_span":round(YEAR_BIN_DAYS*n/span,3),
            "time_system_as_reported":VALID_REPORTED_CLOCK,
            "original_relative_365day_bins_anchored_at_first_QC_epoch":b,
            "n_observed_relative_365day_bins":len(b),
            "n_nonempty_relative_365day_bins":_nonempty_bins(b),
            "n_empty_relative_365day_bins":len(b)-_nonempty_bins(b),
            "longest_consecutive_empty_relative_365day_bins":_longest_zero_bins(b),
            "all_30QC_90day_original_R1_technical_gates_passed":True,
            "cadence_metric_computable":True,
            "real_1day_spectral_window_computable_from_committed_R3_bins":False,
            "synthetic_1day_window_example_available":True,
            "SYNTHETIC_daily_integer_grid_1day_window_power":p_daily,
            "SYNTHETIC_subday_diverse_1day_window_power":p_diverse,
            "SYNTHETIC_example_window_power_difference_abs":round(abs(p_daily-p_diverse),6),
            "synthetic_schedules_preserve_same_original_per_bin_counts_and_total_span":True,
            "synthetic_window_scores_are_not_observed_and_not_true_bounds":True,
        })
    if sum(z["cadence_metric_computable"] for z in output)!=3:
        raise ValueError("Unexpected number of original source coverage records")
    if (sum(z.get("technical_source_qc_accepted_epochs") or 0 for z in output)!=591
            or sum(z.get("original_source_rows") or 0 for z in output)!=684
            or sum(z.get("n_empty_relative_365day_bins") or 0 for z in output)!=4
            or sum((z.get("longest_consecutive_empty_relative_365day_bins") or 0)>=2 for z in output)!=2):
        raise ValueError("R4 original source coverage measures do not reconcile")
    return {
        "schema_version":"stellarforge-taurus-r4-original-ztf-annualbin-coverage-synthetic-window-nonidentifiability-no-raw-v1",
        "phase":R4_STUDY_STATUS,
        "derived_only_from_r3_original_first_run_id":FIRST_RUN,
        "derived_only_from_r3_original_retry_run_id":RETRY_RUN,
        "input_original_DR24_oid_count":6,
        "real_original_ztf_OIDs_with_QC_annual_bins":3,
        "original_ztf_OIDs_with_unavailable_server_responses":3,
        "n_original_ztf_raw_rows_quality_screened":684,
        "n_original_ztf_accepted_epochs":591,
        "n_original_ztf_bit15_masked_rows":93,
        "number_real_series_with_two_consecutive_empty_relative_year_bins":2,
        "number_real_series_with_all_relative_year_bins_nonempty":1,
        "observed_frequency_window_calculated_from_original_visit_timestamps":False,
        "only_deterministic_hypothetical_synthetic_1day_window_constructed":True,
        "synthetic_test_frequency_cycles_per_day":1.0,
        "original_physical_Gaia_ZTF_identifications_confirmed":0,
        "original_ZTF_ObjectID_lightcurves_merged":0,
        "new_variable_stars_or_companions_confirmed":0,
        "real_star_periodogram_or_astrophysical_period_reported":False,
        "r4_physical_stellar_variability_science_go":False,
        "technical_methodical_cadence_feasibility_completed":True,
        "original_source_365day_bin_zero_is_not_archive_timeout":True,
        "original_bins_anchored_to_individual_first_good_visit_not_same_calendar_start":True,
        "source_observations":output,
        "limitations":[
            "These 365-day bin counts are derived from genuine original DR24 survey responses but original visit timestamps are not publicly committed. Two entire relative 365-day bins contain zero original QC-accepted visits in each of two returned source OIDs; the third has positive visits in every within-span bin.",
            "Technical OID/photometric quality passes do not authenticate physical FT Tau or CIDA 11 Gaia-ZTF source associations. The 24 original technical Gaia members and 6 survey OIDs are not a representative six-star population sample.",
            "The *SYNTHETIC* two schedules per OID are mathematical examples built with imaginary observation times; their 1-day spectral-window numbers are not measured periodograms, inferred false-alarm probabilities, estimates of red noise, strict bounds, or astrophysical variability evidence.",
            "An exact astrophysical spectral window or periodicity requires original genuine individual visit timestamps and the independent real Gaia-to-ZTF source association. Coarse year-bin counts cannot recover either.",
            "The other three original ObjectIDs timed out twice at the original survey API, so their data existence, cadence, quality and period properties remain unknown; timeout must never be reinterpreted as zero visits or nonvariable stars.",
            "No original ZTF source-table bytes, per-epoch photometry, exact original timestamps, telescope pixels or unpublished/private ALMA collaboration data are introduced in R4.",
        ],
    }
