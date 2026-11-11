"""v1.19 real original ZTF star-disjoint empirical PSF LOOCV pilot.

For each Gaia-only preselected new candidate, require original native ZTF
PSF-fit catalogue quality, unchanged source and dated-exposure provenance,
then retrieve genuine original science+mask pixels. Only if at least FOUR
distinct Gaia candidate sources in ONE original science exposure provide
valid source image stamps, build FOUR separate empirical PSF shapes from
other-three sources and test each against its genuinely withheld star.
No native DAOPhot coefficients enter empirical PSF construction; original
DAOPhot spatial model used only as an independent-code COMPARATOR on the
same source pixels. The original ZTF source coordinates and native model
training membership are not independent, so no absolute calibration claim.

Raw NASA/IPAC survey science/mask FITS, Gaia TAP CSV, PSF catalogues and
native DAOPhot coefficients remain ephemeral. Published artifact has only
source SHA and bounded derived scalar evidence.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from urllib.error import HTTPError,URLError
from zipfile import ZipFile

import numpy as np

from stellarforge.v13_observational_review import review_irsa_artifact
from stellarforge.v17_field_controls import stratified_ztf_image_candidates
from stellarforge.v18_gaia_references import (
    download_reference_catalog,parse_reference_catalog,
)
from stellarforge.v19_gaia_covariance import (
    fetch_gaia_astrometry,parse_gaia_astrometry,propagate_gaia_5p_formal,
)
from stellarforge.v111_reference_parallax import load_ledger,all_required_gaia_ids
from stellarforge.v113_official_masks_psf import (
    official_ancillary_url,fetch_ancillary_fits,
)
from stellarforge.v114_native_psfcat_association import (
    fetch_native_psf_product,official_psf_product_url,
    parse_psf_fit_catalogue,screen_psf_catalogue_targets,
)
from stellarforge.v115_spatial_psf import (
    parse_original_daophot_lookup,compare_reconstruction_to_official_center,
)
from stellarforge.v117_disjoint_gaia_controls import select_disjoint_holdout_controls
from stellarforge.v118_original_training_log_fttau import (
    select_exploratory_ft_tau_gaia_controls,
)
from stellarforge.v119_empirical_source_psf import (
    empirical_psf_leave_one_source_out,fetch_original_source_stamp,
    evaluate_other_star_empirical_psf,
)

ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/"data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv"
LEDGER=ROOT/"data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json"
ELIGIBLE="PROVISIONAL_CATALOGUE_NEAREST_AND_PROFILE_SCREEN_PASSED"
CENTER_OK="OFFICIAL_CENTER_PSF_APPROXIMATE_MODEL_AGREEMENT"
FT_TAU="149623711269425408"
CIDA11="3419110734340795648"


def _transport(exc:Exception,status:str)->dict:
    r={"status":status,"error_type":type(exc).__name__}
    if isinstance(exc,HTTPError):r["http_status"]=int(exc.code)
    return r


def run(original_zip:Path,seed_path:Path=SEED,ledger_path:Path=LEDGER,*,
        gaia_timeout:float=25,archive_timeout:float=6)->dict:
    if not 1<=gaia_timeout<=60 or not 1<=archive_timeout<=20:
        raise ValueError("Unsafe Gaia/ZTF source archive timeouts")
    original=review_irsa_artifact(original_zip,seed_path)
    ledger=load_ledger(ledger_path)
    used_ids=set(all_required_gaia_ids(ledger))
    if (len(original["targets"])!=2 or len(ledger["exposures"])!=4
        or {e["target_gaia_id"] for e in ledger["exposures"]}!={FT_TAU,CIDA11}
        or {x["gaia_dr3_source_id"] for x in original["targets"]}!={FT_TAU,CIDA11}):
        raise ValueError("Original four ZTF science-source exposure identities changed")
    with Path(seed_path).open(newline="",encoding="utf8") as f:
        seeds={str(r["gaia"]):r for r in csv.DictReader(f)}
    selections={}
    selection_source_sha={}
    # Preregister both groups by Gaia-only criteria BEFORE accessing original
    # native PSF catalogue or source science image residuals.
    for tid in (FT_TAU,CIDA11):
        seed=seeds[tid]
        raw=download_reference_catalog(float(seed["ra"]),float(seed["dec"]),
                                       timeout=gaia_timeout)
        selection_source_sha[tid]=hashlib.sha256(raw).hexdigest()
        entries=parse_reference_catalog(raw)
        strict=select_disjoint_holdout_controls(
            entries,target_id=tid,excluded_source_ids=used_ids,
            max_controls=4)
        if tid==FT_TAU:
            explorer=select_exploratory_ft_tau_gaia_controls(
                entries,target_id=tid,excluded_source_ids=used_ids,
                max_controls=4)
        else:explorer=None
        group=explorer if explorer is not None else strict
        selections[tid]={
            "n_original_gaia_field_rows":len(entries),
            "strict_new_controls":strict,
            "exploratory_new_controls":explorer,
            "new_control_tier":"EXPLORATORY" if explorer else "STRICT_V117",
            "new_gaia_source_ids":[c["source_id"] for c in group["controls"]],
            "all_new_ids_disjoint_from_prior_ten":
                all(c["source_id"] not in used_ids for c in group["controls"]),
        }
    all_new=sorted(set(
        sid for x in selections.values() for sid in x["new_gaia_source_ids"]))
    if len(all_new)>8 or len(all_new)!=sum(
            len(x["new_gaia_source_ids"]) for x in selections.values()):
        raise ValueError("New Gaia source IDs unexpectedly overlap field selection")
    # Existing v1.8 preregistered sources are a SEPARATE BRIGHT
    # PSF-template TRAINING group; only the new v1.17/v1.18 IDs are
    # EVALUATION holdouts. Both groups are fixed before any native ZTF
    # source image pixels are inspected in this execution.
    prior_reference_ids=tuple(sorted(used_ids))
    raw_prior_gaia=fetch_gaia_astrometry(
        prior_reference_ids,timeout_sec=gaia_timeout)
    prior_gaia=parse_gaia_astrometry(
        raw_prior_gaia,expected_ids=prior_reference_ids)
    prior_gaia_sha=hashlib.sha256(raw_prior_gaia).hexdigest()
    new_gaia={}
    gaia_sha=None
    if all_new:
        raw_gaia=fetch_gaia_astrometry(all_new,timeout_sec=gaia_timeout)
        new_gaia=parse_gaia_astrometry(raw_gaia,expected_ids=all_new)
        gaia_sha=hashlib.sha256(raw_gaia).hexdigest()
    frames=[]
    with ZipFile(original_zip) as source_zip:
        for t in original["targets"]:
            tid=t["gaia_dr3_source_id"]
            sr=seeds[tid]
            curves=stratified_ztf_image_candidates(
                source_zip.read(f"{tid}_IRSA_RAW.csv"),
                ra_deg=float(sr["ra"]),dec_deg=float(sr["dec"]),
                pmra_mas_yr=float(sr["pmra"]),
                pmdec_mas_yr=float(sr["pmdec"]),
                science_per_oid=6,cutout_arcsec=90)
            dates=[e for e in ledger["exposures"] if e["target_gaia_id"]==tid]
            if len(dates)!=2:
                raise ValueError("Historical ZTF original science-date budget changed")
            for date in dates:
                matches=[c for g in curves
                    if g["ztf_oid"]==date["oid"] and g["band"]==date["band"]
                    for c in g["candidates"] if c["kind"]=="science"
                    and c["mjd"] is not None
                    and abs(float(c["mjd"])-float(date["mjd"]))<.00002]
                if len(matches)!=1:
                    raise ValueError("Original dated science exposure cannot be verified")
                science_url=matches[0]["url"]
                ids=selections[tid]["new_gaia_source_ids"]
                frame={
                    "target_field":date["target"],
                    "original_target_gaia_dr3_id":tid,
                    "original_science_mjd_assumed_utc":float(date["mjd"]),
                    "original_ztf_oid":date["oid"],
                    "original_band":date["band"],
                    "control_source_tier":selections[tid]["new_control_tier"],
                    "n_gaia_only_preselected_new_ids":len(ids),
                    "native_ztf_psfcat":{"status":"NOT_ACCESSED"},
                    "native_original_daophot":{"status":"NOT_ACCESSED"},
                    "native_center_psf_model_consistency":{"status":"NOT_ACCESSED"},
                    "original_new_star_source_fits":[],
                    "original_bright_prior_reference_training_stamps":[],
                    "native_old_reference_catalogue_screen":{
                        "status":"NOT_ACCESSED",
                    },
                    "empirical_bright_training_to_new_heldout_star_result":{
                        "status":"NOT_ATTEMPTED",
                        "n_new_source_disjoint_heldout_models_evaluated":0,
                    },
                    "empirical_star_disjoint_psf_loocv":{
                        "status":"NOT_ATTEMPTED_INSUFFICIENT_SOURCE_ELIGIBILITY",
                        "n_source_disjoint_psf_validation_folds":0,
                    },
                    "gaia_ztf_physical_source_identities_confirmed":0,
                }
                if not ids:
                    frames.append(frame);continue
                positions=[]
                for sid in ids:
                    ast=propagate_gaia_5p_formal(
                        new_gaia[sid],mjd_utc=float(date["mjd"]))
                    positions.append({
                        "source_id":sid,
                        "geocentric_parallax_adjusted_ra_deg":
                            ast["geocentric_parallax_adjusted_ra_deg"],
                        "geocentric_parallax_adjusted_dec_deg":
                            ast["geocentric_parallax_adjusted_dec_deg"],
                    })
                try:
                    rawcat=fetch_native_psf_product(
                        official_psf_product_url(science_url,"psfcat.fits"),
                        kind="psfcat.fits",timeout=archive_timeout)
                    cat=parse_psf_fit_catalogue(rawcat)
                    screen=screen_psf_catalogue_targets(cat,positions)
                    frame["native_ztf_psfcat"]={
                        "status":"ORIGINAL_PSF_SOURCE_CATALOGUE_LOADED",
                        "original_full_native_psfcat_sha256":cat["sha256"],
                        "n_native_fit_source_rows":cat["n_native_psf_catalogue_rows"],
                        "n_new_sources_screen_eligible":
                            screen["n_provisional_unique_nearest_source_candidates"],
                    }
                except (HTTPError,URLError,TimeoutError,OSError,ValueError) as exc:
                    frame["native_ztf_psfcat"]=_transport(
                        exc,"ORIGINAL_PSF_SOURCE_CATALOGUE_UNAVAILABLE")
                    frames.append(frame);continue
                eligible=[c for c in screen["screens"] if c["status"]==ELIGIBLE]
                # Prior Gaia reference IDs (excluding target) are a distinctly
                # preregistered TRAINING group. No new Gaia holdout is allowed
                # into this reference source set, even if faint holdouts
                # had high native source SNR. Exact original ZTF exposure only.
                original_prior_ids=[str(r["id"]) for r in date["refs"]]
                if not 1<=len(original_prior_ids)<=5 or not set(original_prior_ids)<=used_ids:
                    raise ValueError("Original training reference ledger changed")
                if set(original_prior_ids)&set(ids):
                    raise ValueError("Leakage of new Gaia holdout into old training stars")
                prior_predictions=[]
                for sid in original_prior_ids:
                    old_ast=propagate_gaia_5p_formal(
                        prior_gaia[sid],mjd_utc=float(date["mjd"]))
                    prior_predictions.append({
                        "source_id":sid,
                        "geocentric_parallax_adjusted_ra_deg":
                            old_ast["geocentric_parallax_adjusted_ra_deg"],
                        "geocentric_parallax_adjusted_dec_deg":
                            old_ast["geocentric_parallax_adjusted_dec_deg"],
                    })
                prior_screen=screen_psf_catalogue_targets(
                    cat,prior_predictions)
                original_training_eligible=[
                    c for c in prior_screen["screens"] if c["status"]==ELIGIBLE]
                frame["native_old_reference_catalogue_screen"]={
                    "status":"ORIGINAL_PRIOR_REFERENCE_GAIA_TRAINING_CATALOGUE_SCREENED",
                    "n_original_reference_gaia_predictions":len(original_prior_ids),
                    "n_prior_reference_native_source_candidates_eligible":
                        len(original_training_eligible),
                    "training_candidate_ids_not_new_gaia_holdout":True,
                    "original_ZTF_DAOPhot_training_roster_membership_unknown":True,
                }
                frame["original_new_star_source_fits"]=[
                    {"gaia_source_id":c["gaia_source_id"],
                     "status":c["status"],"fit_completed":False,
                     "physical_source_identity_confirmed":False}
                    for c in screen["screens"] if c["status"]!=ELIGIBLE]
                if not eligible or len(original_training_eligible)<3:
                    frame["empirical_bright_training_to_new_heldout_star_result"]={
                        "status":"INSUFFICIENT_ORIGINAL_NATIVE_REF_CATALOGUE_TRAINING_OR_NEW_TEST_STARS",
                        "n_native_eligible_training_gaia_ids":len(original_training_eligible),
                        "n_native_eligible_new_heldout_gaia_ids":len(eligible),
                        "n_new_source_disjoint_heldout_models_evaluated":0,
                        "original_DAOPhot_training_roster_membership_known":False,
                    }
                    frames.append(frame);continue
                try:
                    rawpsf=fetch_native_psf_product(
                        official_psf_product_url(science_url,"sciimgdao.psf"),
                        kind="sciimgdao.psf",timeout=archive_timeout)
                    native=parse_original_daophot_lookup(rawpsf)
                    frame["native_original_daophot"]={
                        "status":"ORIGINAL_DAOPHOT_LOADED_FOR_COMPARISON_ONLY",
                        "original_spatial_psf_sha256":native["source_sha256"],
                    }
                    rawcenter=fetch_ancillary_fits(
                        official_ancillary_url(science_url,"sciimgdaopsfcent.fits"),
                        kind="sciimgdaopsfcent.fits",timeout=archive_timeout)
                    center=compare_reconstruction_to_official_center(
                        native,rawcenter)
                    frame["native_center_psf_model_consistency"]=center
                except (HTTPError,URLError,TimeoutError,OSError,ValueError) as exc:
                    frame["native_original_daophot"]=_transport(
                        exc,"ORIGINAL_NATIVE_PSF_OR_CENTER_UNAVAILABLE")
                    frames.append(frame);continue
                if frame["native_center_psf_model_consistency"]["status"]!=CENTER_OK:
                    frame["empirical_star_disjoint_psf_loocv"]={
                        "status":"NATIVE_CENTER_CHECK_FAILED_OR_REVIEW_REQUIRED",
                        "n_source_disjoint_psf_validation_folds":0}
                    frames.append(frame);continue
                training_stamps=[]
                for c in original_training_eligible:
                    native_id=int(c["ztf_native_per_exposure_sourceid"])
                    ii=np.flatnonzero(
                        np.asarray(cat["rows"]["sourceid"],dtype=int)==native_id)
                    if len(ii)!=1:
                        raise ValueError("Nonunique old-reference native PSF sourceid")
                    i=int(ii[0])
                    a=fetch_original_source_stamp(
                        science_url,
                        source_ra=float(cat["rows"]["ra"][i]),
                        source_dec=float(cat["rows"]["dec"][i]),
                        native_x=float(cat["rows"]["xpos"][i]),
                        native_y=float(cat["rows"]["ypos"][i]),
                        gaia_source_id=c["gaia_source_id"],
                        timeout=archive_timeout)
                    if a.get("original_source_detector_fits_verified"):
                        training_stamps.append(a)
                    frame["original_bright_prior_reference_training_stamps"].append({
                        "prior_training_reference_gaia_id":c["gaia_source_id"],
                        "status":("ORIGINAL_BRIGHT_GAIA_REFERENCE_PSF_TRAINING_READY"
                                  if a.get("original_source_detector_fits_verified") else a["status"]),
                        "valid_source_template":bool(
                            a.get("original_source_detector_fits_verified")),
                        "source_snr_proxy":round(a["source_snr_proxy"],4)
                            if a.get("original_source_detector_fits_verified") else None,
                        "original_science_sha256":a.get("science_fits_sha256"),
                        "original_mask_sha256":a.get("mask_fits_sha256"),
                        "source_error_type":a.get("error_type"),
                        "source_error_code":a.get("error_code"),
                        "source_http_status":a.get("http_status"),
                        "source_is_physical_single_star_authenticated":False,
                    })
                stamps=[]
                for c in eligible:
                    native_id=int(c["ztf_native_per_exposure_sourceid"])
                    ii=np.flatnonzero(
                        np.asarray(cat["rows"]["sourceid"],dtype=int)==native_id)
                    if len(ii)!=1:
                        raise ValueError("Original ZTF per-exposure source ID lookup not unique")
                    i=int(ii[0])
                    s=fetch_original_source_stamp(
                        science_url,
                        source_ra=float(cat["rows"]["ra"][i]),
                        source_dec=float(cat["rows"]["dec"][i]),
                        native_x=float(cat["rows"]["xpos"][i]),
                        native_y=float(cat["rows"]["ypos"][i]),
                        gaia_source_id=c["gaia_source_id"],
                        timeout=archive_timeout,
                        min_source_snr_proxy=2.5)
                    if s.get("original_source_detector_fits_verified"):
                        stamps.append(s)
                    # Publish only original ZTF image SHA hashes + scalar QA,
                    # NEVER the source pixel/PSF stamp/mask matrices.
                    frame["original_new_star_source_fits"].append({
                        "gaia_source_id":c["gaia_source_id"],
                        "status":("ORIGINAL_MASKED_REAL_SOURCE_STAMP_READY"
                                  if s.get("original_source_detector_fits_verified")
                                  else s["status"]),
                        "fit_completed":bool(s.get("original_source_detector_fits_verified")),
                        "original_science_image_sha256":
                            s.get("science_fits_sha256"),
                        "original_mask_image_sha256":
                            s.get("mask_fits_sha256"),
                        "original_sky_mad_noise_proxy_dn":
                            round(s["sky_sigma_mad_proxy_dn"],6)
                            if s.get("original_source_detector_fits_verified") else None,
                        "original_sky_annulus_n_pixels":s.get("n_original_sky_pixels"),
                        "heldout_faint_source_snr_proxy":round(s["source_snr_proxy"],5)
                            if s.get("original_source_detector_fits_verified") else None,
                        "heldout_source_not_in_empirical_training_template":True,
                        "original_detector_gain_metadata_available":
                            s.get("model_noise_metadata",{}).get(
                                "gain_read_directly_from_original_fits_header",False),
                        "original_detector_readnoise_metadata_available":
                            s.get("model_noise_metadata",{}).get(
                                "read_noise_read_directly_from_original_fits_header",False),
                        "error_type":s.get("error_type"),
                        "error_code":s.get("error_code"),
                        "http_status":s.get("http_status"),
                        "physical_gaia_ztf_identity_confirmed":False,
                    })
                # Key v1.19 predeclared source-independent NEW shape
                # from PRIOR bright references, evaluated on NEW faint Gaia
                # sources. Neither model shape nor sky learning ever sees
                # pixels of the heldout Gaia evaluation IDs.
                frame["empirical_bright_training_to_new_heldout_star_result"]=(
                    evaluate_other_star_empirical_psf(
                        training_stamps,stamps,native_spatial_psf=native))
                # Optional additional strict LOOCV within new Gaia holdouts
                # only when >=4 of those heldouts independently meet the
                # original brighter SNR>=10 template criterion. Faint
                # evaluation stars are not a bright training set.
                bright_new=[v for v in stamps if v["source_snr_proxy"]>=10.]
                frame["empirical_star_disjoint_psf_loocv"]=(
                    empirical_psf_leave_one_source_out(
                        bright_new,native_spatial_psf=native))
                frames.append(frame)
    independently_tested=[x for f in frames
                          for x in f["empirical_bright_training_to_new_heldout_star_result"].get(
                              "evaluation_records",[])]
    folds=[x for f in frames for x in f["empirical_star_disjoint_psf_loocv"].get(
        "heldout_source_folds",[])]
    eligible_all=[x for f in frames for x in f["original_new_star_source_fits"]]
    fold_ratios=[x["empirical_to_native_holdout_rms_ratio"] for x in folds]
    return {
        "schema_version":"stellarforge-v1.19-original-ZTF-disjoint-star-empirical-PSF-LOOCV-with-metadata-only-CCD-noise",
        "original_IRSA_position_query_rows_SHA_verified":original["n_rows"],
        "original_immutable_v18_ledger_sha256":ledger["provenance"]["original_json_sha256"],
        "n_original_historic_science_exposures":len(frames),
        "n_preselected_new_gaia_candidate_ids":len(all_new),
        "n_disjoint_gaia_source_ids_with_real_image_stamp":len({
            s["gaia_source_id"] for s in eligible_all if s["fit_completed"]}),
        "n_original_source_science_mask_pairs_retrieved":sum(
            bool(x["fit_completed"]) for x in eligible_all),
        "n_prior_bright_reference_training_source_images_retrieved":sum(
            bool(x["valid_source_template"]) for f in frames for x in
            f["original_bright_prior_reference_training_stamps"]),
        "n_new_heldout_source_profiles_scored_with_old_bright_reference_empirical_PSF":
            len(independently_tested),
        "n_new_holdout_empirical_profiles_lower_rms_than_original_native_PSF":sum(
            x["empirical_to_native_heldout_rms_ratio"]<1
            for x in independently_tested),
        "median_new_heldout_empirical_to_native_rms_ratio":(
            round(float(np.median([
                x["empirical_to_native_heldout_rms_ratio"]
                for x in independently_tested])),6)
            if independently_tested else None),
        "n_original_FITS_heldout_folds_with_gain_header":sum(
            x["empirical_heldout_source_metrics"][
                "header_gain_applied_to_optional_source_shot_noise"]
            for x in independently_tested),
        "n_distinct_source_empirical_psf_loocv_folds_completed":len(folds),
        "n_distinct_source_empirical_psf_models_trained":len(folds),
        "n_source_folds_where_empirical_psf_has_lower_same_source_pixel_residual_than_native":sum(
            x["empirical_low_rms_not_physical_detection"] for x in folds),
        "empirical_to_native_holdout_rms_ratio_median":
            round(float(np.median(fold_ratios)),6) if folds else None,
        "n_heldout_source_folds_with_fits_header_gain_metadata":sum(
            x["empirical_holdout_source_metrics"][
                "header_gain_applied_to_optional_source_shot_noise"]
            for x in folds),
        "n_true_original_ZTF_PSF_training_star_rosters_authenticated":0,
        "n_independently_authenticated_physical_gaia_ztf_source_identities":0,
        "n_calibrated_absolute_instrument_PSF_WCS_error_models":0,
        "n_new_confirmed_stellar_binary_companions_or_physical_variability":0,
        "gaia_field_cone_original_csv_sha256":selection_source_sha,
        "new_gaia_full_formal_5d_tap_csv_sha256":gaia_sha,
        "original_old_training_reference_formal_5d_gaia_csv_sha256":
            prior_gaia_sha,
        "gaia_only_selection_before_ZTF_native_psf_data":selections,
        "original_science_exposures":frames,
        "source_stamp_status_counts":dict(sorted(
            Counter(x["status"] for x in eligible_all).items())),
        "limitations":[
            "Empirical PSF shapes are genuinely built from pixels of 3 OTHER distinct Gaia source candidate IDs in the same exposure. Each separate heldout source star's pixels were never used to construct its evaluated empirical PSF shape.",
            "The source positions and native PSFcat quality screen still depend on the ZTF original source-extraction/DAOPhot processing pipeline; source IDs were not independently authenticated as Gaia's true physical stars.",
            "Original ZTF DAOPhot model PSF training-star membership is UNKNOWN despite official processing-log audit v1.18. A new empirically reconstructed PSF is independent of native PSF coefficients, but its candidates/centroids/selection are not independent of all original ZTF instrumental procedures.",
            "Only 4–5 candidate sources at most and at most four historical original science dates, no multi-CCD or complete multi-band/long-baseline PSF field calibration. Less than four quality-controlled real source stamps means NO LOOCV test, not a false astrophysical nondetection.",
            "All nuisance flux-amplitude and background-plane fits are on half the SAME heldout source star's pixels, while the source PSF shape was learned from OTHER stars. The pixel holdout side can contain correlated error, not an independently calibrated astrometric/photometric error variance.",
            "Original science pixels are in DN; sky annulus MAD is a robust per-source noise proxy. Optional electron/DN gain and read-noise are used/reported ONLY when explicit trusted original FITS metadata exist; source shot-noise proxy is not a full pixel covariance or calibrated chi-square.",
            "Original image interpolation of shifted templates resamples CCD noise and can bias PSF shape; sky nebula, non-Gaia neighbors and unresolved systems are not independently excluded.",
            "Gaia full correlated 5D formal covariance and first-order geocentric annual parallax do not yet model Palomar topocentric mid-exposure corrections, chromatic refraction, detector WCS distortions or high RUWE CIDA 11 physical source model uncertainties.",
            "Original science/bitmask FITS, PSF catalogue source rows, DAOPhot coefficient tables, raw Gaia TAP/IRSA photometry and CCD pixel stamps stay ephemeral and outside public repo and Actions artifacts.",
        ],
    }


def write_outputs(result:dict,out:Path)->tuple[Path,Path]:
    out.mkdir(parents=True,exist_ok=True)
    j=out/"V119_ORIGINAL_DISJOINT_EMPIRICAL_PSF_LOOCV_NO_RAW.json"
    m=out/"V119_ORIGINAL_DISJOINT_EMPIRICAL_PSF_LOOCV_NO_RAW.md"
    j.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf8")
    lines=[
        "# StellarForge v1.19 — Original ZTF distinct-star empirical PSF leave-one-out",
        "",
        "**Empirical PSF built from genuine original science/bitmask pixels of *other* Gaia-candidate source IDs; cannot authenticate original ZTF DAOPhot training-star exclusion, physical crossmatches or absolute WCS/PSF precision.**",
        "",
        f"Original SHA-verified IRSA ZTF query records: **{result['original_IRSA_position_query_rows_SHA_verified']}**.",
        f"Actual historic dated ZTF science frames: **{result['n_original_historic_science_exposures']}**.",
        f"New Gaia IDs preregistered independently of ZTF residuals: **{result['n_preselected_new_gaia_candidate_ids']}**.",
        f"Genuine original source science/mask image pairs read successfully: **{result['n_original_source_science_mask_pairs_retrieved']}**.",
        f"Separate source-disjoint empirical PSF leave-one-out heldout stars/folds: **{result['n_distinct_source_empirical_psf_loocv_folds_completed']}**.",
        f"Empirical PSF folds with lower pixel residual vs original ZTF spatial DAOPhot: **{result['n_source_folds_where_empirical_psf_has_lower_same_source_pixel_residual_than_native']}**.",
        f"Median empirical/native heldout source residual RMS ratio: **{result['empirical_to_native_holdout_rms_ratio_median']}** (descriptive only).",
        f"Heldout star folds with usable original FITS header gain metadata: **{result['n_heldout_source_folds_with_fits_header_gain_metadata']}**.",
        "",
        "| Original field | Source date MJD | Selection tier | New Gaia source candidates | Actual original source cutouts | Distinct star leave-one-out folds |",
        "|---|---:|---|---:|---:|---:|",
    ]
    for f in result["original_science_exposures"]:
        folds=f["empirical_star_disjoint_psf_loocv"]
        lines.append(
            f"| {f['target_field']} | {f['original_science_mjd_assumed_utc']:.6f} | "
            f"{f['control_source_tier']} | {f['n_gaia_only_preselected_new_ids']} | "
            f"{sum(x['fit_completed'] for x in f['original_new_star_source_fits'])} | "
            f"{folds['n_source_disjoint_psf_validation_folds']} |")
    lines.extend([
        "",
        "## Scientific interpretation",
        "",
        "- Per exposure and fold, only OTHER preselected Gaia-candidate sources supply pixel shapes to the empirical PSF median. The heldout star does not participate in estimating that PSF shape. The native spatial DAOPhot model is a separately archived instrument comparator, not part of the empirical training data.",
        "- This is an actual source-ID-disjoint PSF MODEL SHAPE test within StellarForge, but source centroids/quality still came from native ZTF pipeline and original DAOPhot training-star membership remains UNKNOWN. It does NOT establish independent absolute instrument PSF/WCS errors.",
        "- Candidate Gaia-to-ZTF physical identity and source isolation have not been independently authenticated. FT Tau exploratory and CIDA 11 strict star selection are different strata and cannot be pooled for a field-wide calibration.",
        "- Original FITS science/mask pixels, Gaia TAP rows, original ZTF PSFcat and DAOPhot coefficients and original raw IRSA photometry are ephemeral. Only per-source bounded scalar residual/error proxy measurements and source hashes are public.",
        "- Detector gain/source shot noise is included only if the corresponding ORIGINAL FITS header contains a physically valid gain keyword. Otherwise only the annular sky MAD proxy is reported; correlated pixel covariance remains unknown.",
        "- No binary companions, real stellar variability, authenticated Gaia/ZTF physical IDs, calibrated absolute WCS/PSF uncertainty or survey sensitivity is inferred.",
        "",
    ])
    m.write_text("\n".join(lines)+"\n",encoding="utf8")
    return j,m


def main():
    p=argparse.ArgumentParser(description="Real original ZTF distinct-star empirical PSF shape validation")
    p.add_argument("original_irsa_zip",type=Path)
    p.add_argument("--seed",type=Path,default=SEED)
    p.add_argument("--ledger",type=Path,default=LEDGER)
    p.add_argument("--gaia-timeout",type=float,default=25)
    p.add_argument("--archive-timeout",type=float,default=6)
    p.add_argument("--output",type=Path,
                   default=ROOT/"reports/generated/v1.19_empirical_psf")
    p.add_argument("--require-one-source-disjoint-fold",action="store_true")
    a=p.parse_args()
    result=run(a.original_irsa_zip,a.seed,a.ledger,
               gaia_timeout=a.gaia_timeout,archive_timeout=a.archive_timeout)
    files=write_outputs(result,a.output)
    print(json.dumps({
        "n_actual_masked_source_stamps":result["n_original_source_science_mask_pairs_retrieved"],
        "n_bright_training_old_reference_image_stamps":
            result["n_prior_bright_reference_training_source_images_retrieved"],
        "n_new_Gaia_holdout_stars_evaluated":
            result["n_new_heldout_source_profiles_scored_with_old_bright_reference_empirical_PSF"],
        "median_new_heldout_empirical_to_native_rms":
            result["median_new_heldout_empirical_to_native_rms_ratio"],
        "n_source_disjoint_empirical_holdout_folds":result["n_distinct_source_empirical_psf_loocv_folds_completed"],
        "n_empirical_lower_residual_than_native":result["n_source_folds_where_empirical_psf_has_lower_same_source_pixel_residual_than_native"],
        "median_empirical_to_native_holdout_rms":result["empirical_to_native_holdout_rms_ratio_median"],
        "n_heldout_folds_with_original_gain_metadata":result["n_heldout_source_folds_with_fits_header_gain_metadata"],
        "instrument_absolute_wcs_psf_precision_calibrated":0,
        "new_stellar_companions_confirmed":0,
        "reports":[str(x) for x in files],
    },indent=2))
    if (a.require_one_source_disjoint_fold
        and not (result["n_distinct_source_empirical_psf_loocv_folds_completed"]
                 or result["n_new_heldout_source_profiles_scored_with_old_bright_reference_empirical_PSF"])):
        p.exit(2,"No original exposure had enough distinct bright prior Gaia source references and new Gaia heldout masked science pixels for a separately trained empirical PSF validation; no instrument calibration or astrophysical nondetection can be inferred.\n")


if __name__=="__main__":
    main()
