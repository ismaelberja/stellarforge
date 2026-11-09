"""Real ZTF original processing-log audit and preregistered FT Tau exploratory controls.

Official logs may be absent or offer only aggregate PSF information; they
cannot establish source-level DAOPhot training star membership unless an
identifiable roster is independently verified (this runner cannot do that).
An exploratory Gaia control tier is documented separately from strict v1.17.

Only 4 original historical science exposures, SHA-verified IRSA photometry
ZIP, and fresh Gaia DR3 cone/formal astrometry. No raw survey files released.
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
from stellarforge.v116_masked_original_psf_residuals import (
    audit_original_source_psf_residuals,
)
from stellarforge.v117_disjoint_gaia_controls import (
    select_disjoint_holdout_controls,shifted_sky_null_probes,
    compare_disjoint_holdouts,
)
from stellarforge.v118_original_training_log_fttau import (
    audit_exposure_training_logs,select_exploratory_ft_tau_gaia_controls,
)

ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/"data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv"
LEDGER=ROOT/"data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json"
NATIVE_OK="PROVISIONAL_CATALOGUE_NEAREST_AND_PROFILE_SCREEN_PASSED"
CENTER_OK="OFFICIAL_CENTER_PSF_APPROXIMATE_MODEL_AGREEMENT"
PIXEL_OK="PROVISIONAL_ORIGINAL_MASKED_PSF_PIXEL_RESIDUAL_SCREEN_PASSED"


def _fail(exc,prefix):
    d={"status":prefix,"error_type":type(exc).__name__}
    if isinstance(exc,HTTPError):d["http_status"]=int(exc.code)
    return d


def run(original_zip:Path,seed_path:Path=SEED,ledger_path:Path=LEDGER,*,
        gaia_timeout:float=25,archive_timeout:float=6)->dict:
    if not (1<=gaia_timeout<=60 and 1<=archive_timeout<=20):
        raise ValueError("Unbounded Gaia/IRSA original source timeouts")
    original=review_irsa_artifact(original_zip,seed_path)
    ledger=load_ledger(ledger_path)
    excluded=set(all_required_gaia_ids(ledger))
    if len(original["targets"])!=2 or len(ledger["exposures"])!=4:
        raise ValueError("Historical survey source target/exposure roster changed")
    if ({x["gaia_dr3_source_id"] for x in original["targets"]} !=
        {e["target_gaia_id"] for e in ledger["exposures"]}):
        raise ValueError("Original ZTF source vs immutable Gaia exposure ledger mismatch")
    with Path(seed_path).open(newline="",encoding="utf8") as handle:
        seeds={str(r["gaia"]):r for r in csv.DictReader(handle)}
    ft_id=next(x["gaia_dr3_source_id"] for x in original["targets"]
               if x["gaia_dr3_source_id"]=="149623711269425408")
    ft=seeds[ft_id]
    fresh_gaia=download_reference_catalog(float(ft["ra"]),float(ft["dec"]),
                                          timeout=gaia_timeout)
    gaia_rows=parse_reference_catalog(fresh_gaia)
    strict=select_disjoint_holdout_controls(
        gaia_rows,target_id=ft_id,excluded_source_ids=excluded,
        max_controls=4)
    exploratory=select_exploratory_ft_tau_gaia_controls(
        gaia_rows,target_id=ft_id,excluded_source_ids=excluded,
        max_controls=4)
    new_ids=tuple(sorted(c["source_id"] for c in exploratory["controls"]))
    if excluded&set(new_ids):
        raise ValueError("Original target/reference used in new exploratory control")
    new_gaia={}
    gaia_hash=None
    if new_ids:
        raw_astrometry=fetch_gaia_astrometry(new_ids,timeout_sec=gaia_timeout)
        new_gaia=parse_gaia_astrometry(raw_astrometry,expected_ids=new_ids)
        gaia_hash=hashlib.sha256(raw_astrometry).hexdigest()
    frames=[]
    with ZipFile(original_zip) as archive:
        for target in original["targets"]:
            targetid=target["gaia_dr3_source_id"]
            row=seeds[targetid]
            curves=stratified_ztf_image_candidates(
                archive.read(f"{targetid}_IRSA_RAW.csv"),
                ra_deg=float(row["ra"]),dec_deg=float(row["dec"]),
                pmra_mas_yr=float(row["pmra"]),pmdec_mas_yr=float(row["pmdec"]),
                science_per_oid=6,cutout_arcsec=90)
            planned=[e for e in ledger["exposures"]
                     if e["target_gaia_id"]==targetid]
            if len(planned)!=2:
                raise ValueError("Expected two historical g-band science epochs per field")
            for e in planned:
                candidates=[cand for c in curves
                    if c["ztf_oid"]==e["oid"] and c["band"]==e["band"]
                    for cand in c["candidates"] if cand["kind"]=="science"
                    and cand["mjd"] is not None
                    and abs(float(cand["mjd"])-float(e["mjd"]))<.00002]
                if len(candidates)!=1:
                    raise ValueError("Cannot reconstruct exact original dated ZTF exposure")
                science=candidates[0]["url"]
                logs=audit_exposure_training_logs(
                    science,timeout=archive_timeout)
                result={
                    "target":e["target"],"target_gaia_id":targetid,
                    "source_oid":e["oid"],"band":e["band"],
                    "original_science_mjd_assumed_utc":float(e["mjd"]),
                    "original_survey_processing_log_audit":logs,
                    "exploratory_ft_tau_analysis_performed":targetid==ft_id,
                    "native_psfcat_result":{"status":"NOT_REQUESTED"},
                    "native_daophot_result":{"status":"NOT_REQUESTED"},
                    "same_pipeline_center_psf_result":{"status":"NOT_REQUESTED"},
                    "exploratory_gaia_source_original_masked_psf_checks":[],
                    "sky_shift_null":{"status":"NOT_REQUESTED"},
                    "original_psf_training_source_roster_validated":False,
                }
                if targetid!=ft_id or not new_ids:
                    frames.append(result);continue
                positions=[]
                for sid in new_ids:
                    p=propagate_gaia_5p_formal(
                        new_gaia[sid],mjd_utc=float(e["mjd"]))
                    positions.append({
                        "source_id":sid,
                        "geocentric_parallax_adjusted_ra_deg":
                            p["geocentric_parallax_adjusted_ra_deg"],
                        "geocentric_parallax_adjusted_dec_deg":
                            p["geocentric_parallax_adjusted_dec_deg"]})
                try:
                    raw_cat=fetch_native_psf_product(
                        official_psf_product_url(science,"psfcat.fits"),
                        kind="psfcat.fits",timeout=archive_timeout)
                    cat=parse_psf_fit_catalogue(raw_cat)
                    screens=screen_psf_catalogue_targets(cat,positions)
                    result["native_psfcat_result"]={
                        "status":"ORIGINAL_NATIVE_PSF_CATALOGUE_SCREEN_COMPLETED",
                        "psfcat_sha256":cat["sha256"],
                        "n_original_psf_catalogue_rows":
                            cat["n_native_psf_catalogue_rows"],
                        "n_exploratory_native_source_candidate_profiles_passed":
                            screens["n_provisional_unique_nearest_source_candidates"]}
                    result["sky_shift_null"]=shifted_sky_null_probes(
                        cat,positions)
                except (HTTPError,URLError,TimeoutError,OSError,ValueError) as exc:
                    result["native_psfcat_result"]=_fail(
                        exc,"ORIGINAL_NATIVE_PSF_CATALOGUE_UNAVAILABLE_OR_UNUSABLE")
                    frames.append(result);continue
                try:
                    raw_psf=fetch_native_psf_product(
                        official_psf_product_url(science,"sciimgdao.psf"),
                        kind="sciimgdao.psf",timeout=archive_timeout)
                    psf=parse_original_daophot_lookup(raw_psf)
                    result["native_daophot_result"]={
                        "status":"ORIGINAL_NATIVE_SPATIAL_DAOPHOT_PARSED",
                        "native_daophot_sha256":psf["source_sha256"]}
                    raw_center=fetch_ancillary_fits(
                        official_ancillary_url(science,"sciimgdaopsfcent.fits"),
                        kind="sciimgdaopsfcent.fits",timeout=archive_timeout)
                    result["same_pipeline_center_psf_result"]=(
                        compare_reconstruction_to_official_center(psf,raw_center))
                except (HTTPError,URLError,TimeoutError,OSError,ValueError) as exc:
                    result["native_daophot_result"]=_fail(
                        exc,"ORIGINAL_SPATIAL_DAOPHOT_OR_CENTER_FITS_UNAVAILABLE")
                    frames.append(result);continue
                if result["same_pipeline_center_psf_result"]["status"]!=CENTER_OK:
                    frames.append(result);continue
                for c in screens["screens"]:
                    if c["status"]!=NATIVE_OK:
                        result["exploratory_gaia_source_original_masked_psf_checks"].append({
                            "gaia_source_id":c["gaia_source_id"],
                            "tier":"EXPLORATORY_NOT_EQUIVALENT_TO_V117_STRICT",
                            "status":c["status"],
                            "fit_completed":False,
                            "originally_used_in_v116":False,
                            "physical_source_identity_confirmed":False})
                        continue
                    native_id=int(c["ztf_native_per_exposure_sourceid"])
                    idx=np.flatnonzero(np.asarray(cat["rows"]["sourceid"],dtype=int)==native_id)
                    if len(idx)!=1:
                        raise ValueError("Native per-exposure source ID not unique")
                    k=int(idx[0])
                    fit=audit_original_source_psf_residuals(
                        science,psf,
                        source_ra=float(cat["rows"]["ra"][k]),
                        source_dec=float(cat["rows"]["dec"][k]),
                        native_x=float(cat["rows"]["xpos"][k]),
                        native_y=float(cat["rows"]["ypos"][k]),
                        timeout=archive_timeout)
                    result["exploratory_gaia_source_original_masked_psf_checks"].append({
                        "gaia_source_id":c["gaia_source_id"],
                        "tier":"EXPLORATORY_NOT_EQUIVALENT_TO_V117_STRICT",
                        "status":fit["status"],
                        "fit_completed":bool(fit["local_masked_psf_model_fit_completed"]),
                        "originally_used_in_v116":False,
                        "residual_quality_passed":fit["status"]==PIXEL_OK,
                        "rms_over_sky_proxy":fit.get(
                            "same_image_holdout_residual_rms_over_sky_noise_proxy"),
                        "pixel_residual_diagnostics":fit,
                        "physical_source_identity_confirmed":False})
                frames.append(result)
    checks=[x for e in frames for x in e[
        "exploratory_gaia_source_original_masked_psf_checks"]]
    fitted=[x for x in checks if x.get("fit_completed")]
    all_logs=[l for e in frames
              for l in e["original_survey_processing_log_audit"][
                  "original_log_product_results"]]
    return {
        "schema_version":"stellarforge-v1.18-original-ztf-psf-training-log-and-exploratory-ft-tau-Gaia-source-quality",
        "original_IRSA_position_query_rows_SHA_verified":original["n_rows"],
        "original_reference_ledger_sha256":ledger["provenance"]["original_json_sha256"],
        "n_original_science_exposure_log_sets_audited":len(frames),
        "n_official_processing_log_product_requests":len(all_logs),
        "n_official_processing_logs_read":sum(
            l["status"]=="ORIGINAL_ZTF_PROCESSING_LOG_READ_PSF_TRAINING_IDS_NOT_VERIFIABLE"
            for l in all_logs),
        "n_official_processing_log_http503":sum(
            l.get("http_status")==503 for l in all_logs),
        "official_processing_log_status_counts":dict(sorted(
            Counter(l["status"] for l in all_logs).items())),
        "n_original_psf_training_star_membership_rosters_recovered":0,
        "n_gaia_controls_independently_proven_excluded_from_original_psf_training":0,
        "n_gaia_ft_tau_widecone_rows":len(gaia_rows),
        "n_ft_tau_strict_v117_disjoint_controls_on_fresh_query":
            strict["n_disjoint_controls_preselected"],
        "n_ft_tau_exploratory_gaia_source_candidates_preselected":
            exploratory["n_exploratory_controls_selected"],
        "n_ft_tau_exploratory_new_distinct_gaia_source_ids_fitted":len({
            x["gaia_source_id"] for x in fitted}),
        "n_ft_tau_exploratory_source_epoch_psf_pixel_fits_completed":len(fitted),
        "n_ft_tau_exploratory_same_image_pixel_residual_qa_passes":sum(
            bool(x["residual_quality_passed"]) for x in fitted),
        "n_ft_tau_exploratory_source_epoch_catalogue_or_pixel_qa_review":sum(
            not x.get("fit_completed") or not x.get("residual_quality_passed")
            for x in checks),
        "n_ft_tau_fixed_shift_sky_null_probes":sum(
            e["sky_shift_null"].get("n_shifted_sky_probes",0) for e in frames),
        "n_ft_tau_fixed_shift_sky_null_native_catalogue_hits":sum(
            e["sky_shift_null"].get("n_nearest_any_psf_source_within_radius",0)
            for e in frames),
        "gaia_ft_tau_original_widecone_csv_sha256":hashlib.sha256(fresh_gaia).hexdigest(),
        "gaia_new_exact_formal_5d_response_sha256":gaia_hash,
        "ft_tau_v117_strict_new_source_selection":strict,
        "ft_tau_declared_exploratory_gaia_source_selection":exploratory,
        "original_science_exposure_results":frames,
        "independently_calibrated_source_psfs":0,
        "independently_calibrated_wcs_error_budgets":0,
        "confirmed_physical_gaia_ztf_source_identities":0,
        "confirmed_physical_companions_or_variability":0,
        "limitations":[
            "Archived sciimlog.txt/log.txt are per-exposure instrumental processing logs. Even when logs mention PSF or numbers of training stars, their full source-level DAOPhot training-star ID roster is not verified by this parser. Zero PSF-training-set membership exclusions have been proven.",
            "FT Tau exploratory Gaia controls follow predeclared wider G/RUWE/neighbor and distance thresholds after prior strict zero-control result, but they were selected before inspecting the present ZTF science pixels. They are NOT identical in cleanliness to v1.17 strict-tier controls.",
            "No Gaia widecone astrophysical isolation test can exclude unresolved sources, non-Gaia stars or variable nebular background. ZTF nearest psfcat association is still a provisional crossmatch.",
            "Original ZTF source native psfcat and DAOPhot are from the SAME instrumental pipeline, whose PSF training stars may include any new exploratory Gaia candidate.",
            "Real source image fits use original WCS-aligned sciimg.fits+mskimg.fits DN pixels and internally held-out checkerboard pixels of the SAME source. They are not independent calibrated PSF/WCS, photometric magnitudes or evidence of physical source identity.",
            "Fixed ±25arcsec shifted sky positions only probe local catalogue density, not a calibrated false association rate.",
            "The original Gaia DR3 propagated 5D covariance and geocentric annual parallax do not model Palomar topocentric apparent-place, telescope PSF/CCD WCS calibration or known high RUWE of CIDA 11.",
            "Missing logs, PSFcatalog sources, masked image pixels or HTTP 503 mean unavailable data, not astrophysical nondetections.",
            "Raw Gaia DR3 CSV, ZTF source/PSFcat FITS science/mask pixels, DAOPhot lookup coefficients, original IRSA photometry and raw ZTF processing logs are not uploaded or published.",
        ],
    }


def write_outputs(r:dict,out:Path):
    out.mkdir(parents=True,exist_ok=True)
    j=out/"V118_ZTF_LOG_TRAINING_AUDIT_AND_FT_TAU_EXPLORATORY_NO_RAW.json"
    m=out/"V118_ZTF_LOG_TRAINING_AUDIT_AND_FT_TAU_EXPLORATORY_NO_RAW.md"
    j.write_text(json.dumps(r,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf8")
    lines=[
        "# StellarForge v1.18 — Real original ZTF pipeline logs and FT Tau exploratory Gaia field",
        "",
        "**Native original ZTF DAOPhot training-star membership is NOT authenticated by processing-log mention or Gaia source selection; no independent star-PSF/WCS calibration or astrophysical discovery.**",
        "",
        f"Original SHA-verified IRSA/ZTF positional-query rows: **{r['original_IRSA_position_query_rows_SHA_verified']}**.",
        f"Exact historic original dated ZTF science exposure log sets: **{r['n_original_science_exposure_log_sets_audited']}**.",
        f"Original public processing logs read: **{r['n_official_processing_logs_read']}/{r['n_official_processing_log_product_requests']}**.",
        "**Original DAOPhot PSF training-star source-ID rosters verified: 0.**",
        f"FT Tau Gaia original wide-cone rows: **{r['n_gaia_ft_tau_widecone_rows']}**.",
        f"FT Tau v1.17 STRICT eligible new Gaia source IDs (fresh query): **{r['n_ft_tau_strict_v117_disjoint_controls_on_fresh_query']}**.",
        f"FT Tau PREDECLARED EXPLORATORY eligible new Gaia source IDs: **{r['n_ft_tau_exploratory_gaia_source_candidates_preselected']}**.",
        f"FT Tau exploratory original masked source×date PSF pixel fits: **{r['n_ft_tau_exploratory_source_epoch_psf_pixel_fits_completed']}**.",
        f"FT Tau exploratory same-image residual QA passes: **{r['n_ft_tau_exploratory_same_image_pixel_residual_qa_passes']}**.",
        f"FT Tau deterministic sky-shift catalogue probes: **{r['n_ft_tau_fixed_shift_sky_null_probes']}**, native source hits **{r['n_ft_tau_fixed_shift_sky_null_native_catalogue_hits']}** (not a calibrated chance-association rate).",
        "",
        "| Original source field | Science MJD | Log products read | Exploratory FT Tau source PSF pixel fits |",
        "|---|---:|---:|---:|",
    ]
    for e in r["original_science_exposure_results"]:
        p=e["original_survey_processing_log_audit"]
        fits=e["exploratory_gaia_source_original_masked_psf_checks"]
        lines.append(
            f"| {e['target']} | {e['original_science_mjd_assumed_utc']:.6f} | "
            f"{p['n_original_processing_logs_read']}/2 | "
            f"{sum(bool(x.get('fit_completed')) for x in fits)} |")
    lines.extend([
        "",
        "## Interpretation",
        "",
        "- The official ZTF imaging pipeline first estimates a DAOPhot PSF and later produces PSF-fit source catalogues; the archive's \`psfcat.fits\` output does not identify which sources trained the original PSF. The original \`sciimlog.txt\` and \`log.txt\` processing logs may contain stage counts but cannot by themselves certify the complete training-star ID roster without a documented identifier namespace.",
        "- FT Tau exploratory controls use **different, wider** Gaia-only quality/geometry criteria from the original strict v1.17 controls. They were specified before examining current ZTF pixel residuals, not presented as strict controls or confirmed physically isolated stars.",
        "- Every fit to genuine original ZTF science/mask source DN pixels is an internally held-out SAME-IMAGE diagnostic, not an independently calibrated stellar PSF or an authenticated Gaia–ZTF physical match.",
        "- No astrophysical companion, binary or physical variability result is inferred from any pixel residual; the 3 earlier residual-review sources remain under investigation.",
        "",
    ])
    m.write_text("\n".join(lines),encoding="utf8")
    return j,m


def main():
    p=argparse.ArgumentParser(description="Read original ZTF pipeline logs and preregister FT Tau exploratory Gaia source PSF checks")
    p.add_argument("original_irsa_zip",type=Path)
    p.add_argument("--seed",type=Path,default=SEED)
    p.add_argument("--ledger",type=Path,default=LEDGER)
    p.add_argument("--gaia-timeout",type=float,default=25)
    p.add_argument("--archive-timeout",type=float,default=6)
    p.add_argument("--output",type=Path,default=ROOT/"reports/generated/v1.18_original_psf_training")
    a=p.parse_args()
    r=run(a.original_irsa_zip,a.seed,a.ledger,
          gaia_timeout=a.gaia_timeout,archive_timeout=a.archive_timeout)
    paths=write_outputs(r,a.output)
    print(json.dumps({
        "official_processing_logs_read":r["n_official_processing_logs_read"],
        "original_psf_training_star_rosters_authenticated":0,
        "ft_tau_strict_new_controls":r["n_ft_tau_strict_v117_disjoint_controls_on_fresh_query"],
        "ft_tau_exploratory_new_controls":r["n_ft_tau_exploratory_gaia_source_candidates_preselected"],
        "ft_tau_exploratory_real_masked_pixel_fits":r["n_ft_tau_exploratory_source_epoch_psf_pixel_fits_completed"],
        "calibrated_instrument_psf_or_wcs_errors":0,
        "reports":[str(x) for x in paths],
    },indent=2))


if __name__=="__main__":
    main()
