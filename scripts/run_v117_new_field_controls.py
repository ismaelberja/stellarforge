"""Real four-exposure v1.17 new Gaia-source control and shifted-sky null pilot.

The source controls here are completely disjoint by Gaia DR3 ID from the
v1.8--v1.16 original 10-object control pool, selected from Gaia alone before
examining ZTF pixels/PSF residuals. They are NOT proven disjoint from the
ZTF pipeline's own original spatial DAOPhot training stars: unknown.

All raw source data and original original Gaia/IRSA catalogues stay in the
ephemeral runner; only bounded derived scalar reports leave the process.
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
from stellarforge.v111_reference_parallax import (
    load_ledger,all_required_gaia_ids,
)
from stellarforge.v114_native_psfcat_association import (
    fetch_native_psf_product,official_psf_product_url,
    parse_psf_fit_catalogue,screen_psf_catalogue_targets,
)
from stellarforge.v115_spatial_psf import (
    parse_original_daophot_lookup,
    compare_reconstruction_to_official_center,
)
from stellarforge.v113_official_masks_psf import (
    official_ancillary_url,fetch_ancillary_fits,
)
from stellarforge.v116_masked_original_psf_residuals import (
    audit_original_source_psf_residuals,
)
from stellarforge.v117_disjoint_gaia_controls import (
    select_disjoint_holdout_controls,shifted_sky_null_probes,
    compare_disjoint_holdouts,
)

ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/"data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv"
LEDGER=ROOT/"data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json"
CAT_OK="PROVISIONAL_CATALOGUE_NEAREST_AND_PROFILE_SCREEN_PASSED"
CENTER_OK="OFFICIAL_CENTER_PSF_APPROXIMATE_MODEL_AGREEMENT"
MASKED_PASS="PROVISIONAL_ORIGINAL_MASKED_PSF_PIXEL_RESIDUAL_SCREEN_PASSED"


def _failure(exc:Exception,prefix:str)->dict:
    out={"status":prefix,"error_type":type(exc).__name__}
    if isinstance(exc,HTTPError):out["http_status"]=int(exc.code)
    return out


def run(raw_zip:Path,seed:Path=SEED,ledger_file:Path=LEDGER,*,
        gaia_timeout:float=25,archive_timeout:float=6,
        max_new_controls_per_field:int=4)->dict:
    if not 1<=gaia_timeout<=60 or not 1<=archive_timeout<=20:
        raise ValueError("Archive timeouts out of safe range")
    if not 1<=max_new_controls_per_field<=5:
        raise ValueError("Disjoint Gaia source request budget out of bounds")
    original=review_irsa_artifact(raw_zip,seed)
    ledger=load_ledger(ledger_file)
    used_ids=set(all_required_gaia_ids(ledger))
    if len(original["targets"])!=2 or len(ledger["exposures"])!=4:
        raise ValueError("Changed source provenance / technical frame count")
    if {t["gaia_dr3_source_id"] for t in original["targets"]}!={e["target_gaia_id"] for e in ledger["exposures"]}:
        raise ValueError("Original target Gaia IDs inconsistent with ledger")
    with Path(seed).open(newline="",encoding="utf8") as fh:
        original_seed={str(r["gaia"]):r for r in csv.DictReader(fh)}
    selected={}
    original_wide_gaia_hashes={}
    # IMPORTANT: preregister all NEW candidates from Gaia only before
    # opening any native ZTF PSF/source catalog.
    for target in original["targets"]:
        tid=target["gaia_dr3_source_id"]
        seedrow=original_seed[tid]
        raw=download_reference_catalog(
            float(seedrow["ra"]),float(seedrow["dec"]),
            timeout=gaia_timeout)
        original_wide_gaia_hashes[tid]=hashlib.sha256(raw).hexdigest()
        rows=parse_reference_catalog(raw)
        s=select_disjoint_holdout_controls(
            rows,target_id=tid,excluded_source_ids=used_ids,
            max_controls=max_new_controls_per_field)
        selected[tid]=s
    new_ids=tuple(sorted({
        x["source_id"] for s in selected.values() for x in s["controls"]
    }))
    if used_ids&set(new_ids):
        raise ValueError("New holdout Gaia source was previously selected")
    # Full Gaia formal astrometry + geometric parallax for new candidates,
    # exactly as previously done in v1.16. Never infer correlations.
    gaia={}
    gaia_hash=None
    if new_ids:
        raw_gaia=fetch_gaia_astrometry(new_ids,timeout_sec=gaia_timeout)
        gaia=parse_gaia_astrometry(raw_gaia,expected_ids=new_ids)
        gaia_hash=hashlib.sha256(raw_gaia).hexdigest()
    frames=[]
    with ZipFile(raw_zip) as archive:
        for target in original["targets"]:
            tid=target["gaia_dr3_source_id"]
            ss=original_seed[tid]
            curves=stratified_ztf_image_candidates(
                archive.read(f"{tid}_IRSA_RAW.csv"),
                ra_deg=float(ss["ra"]),dec_deg=float(ss["dec"]),
                pmra_mas_yr=float(ss["pmra"]),
                pmdec_mas_yr=float(ss["pmdec"]),
                science_per_oid=6,cutout_arcsec=90)
            planned=[x for x in ledger["exposures"] if x["target_gaia_id"]==tid]
            if len(planned)!=2:
                raise ValueError("Original target must have two science dates")
            new=selected[tid]["controls"]
            for exposure in planned:
                candidates=[cand for curve in curves
                    if curve["ztf_oid"]==exposure["oid"]
                    and curve["band"]==exposure["band"]
                    for cand in curve["candidates"]
                    if cand["kind"]=="science"
                    and cand["mjd"] is not None
                    and abs(cand["mjd"]-exposure["mjd"])<.00002]
                if len(candidates)!=1:
                    raise ValueError("Exact original science exposure not reconstructed")
                url=candidates[0]["url"]
                record={
                    "target_field":exposure["target"],
                    "original_target_gaia_id":tid,
                    "original_science_mjd_assumed_utc":float(exposure["mjd"]),
                    "ztf_oid":exposure["oid"],
                    "band":exposure["band"],
                    "n_new_gaia_only_preselected_source_ids":len(new),
                    "official_native_psfcat":{"status":"CATALOGUE_NOT_ACCESSED"},
                    "official_spatial_daophot":{"status":"NATIVE_SPATIAL_PSF_NOT_ACCESSED"},
                    "original_center_psf_check":{"status":"CENTER_STAMP_NOT_ACCESSED"},
                    "shifted_sky_positional_null":{"status":"SHIFTED_NULL_NOT_AVAILABLE"},
                    "disjoint_source_pixel_checks":[],
                    "source_control_comparison":{
                        "status":"DISJOINT_FIELD_STAR_TEST_NOT_COMPLETED",
                        "independent_external_instrument_psf_wcs_error_calibration_completed":False,
                    },
                    "n_independent_astrophysical_source_matches":0,
                }
                if not new:
                    frames.append(record)
                    continue
                predictions=[]
                for c in new:
                    row=propagate_gaia_5p_formal(
                        gaia[c["source_id"]],mjd_utc=float(exposure["mjd"]))
                    predictions.append({
                        "source_id":c["source_id"],
                        "geocentric_parallax_adjusted_ra_deg":
                            row["geocentric_parallax_adjusted_ra_deg"],
                        "geocentric_parallax_adjusted_dec_deg":
                            row["geocentric_parallax_adjusted_dec_deg"],
                    })
                try:
                    raw_cat=fetch_native_psf_product(
                        official_psf_product_url(url,"psfcat.fits"),
                        kind="psfcat.fits",timeout=archive_timeout)
                    cat=parse_psf_fit_catalogue(raw_cat)
                    screen=screen_psf_catalogue_targets(cat,predictions)
                    record["official_native_psfcat"]={
                        "status":"ORIGINAL_NATIVE_ZTF_PSF_SOURCE_CATALOGUE_LOADED",
                        "psfcat_sha256":cat["sha256"],
                        "n_catalogue_psf_fit_rows":cat["n_native_psf_catalogue_rows"],
                        "n_disjoint_gaia_sources_with_native_fit_candidates":
                            screen["n_provisional_unique_nearest_source_candidates"],
                    }
                    null=shifted_sky_null_probes(cat,predictions)
                    record["shifted_sky_positional_null"]=null
                except (HTTPError,URLError,TimeoutError,OSError,ValueError) as exc:
                    record["official_native_psfcat"]=_failure(exc,"NATIVE_ZTF_CATALOGUE_UNAVAILABLE")
                    frames.append(record)
                    continue
                try:
                    raw_psf=fetch_native_psf_product(
                        official_psf_product_url(url,"sciimgdao.psf"),
                        kind="sciimgdao.psf",timeout=archive_timeout)
                    psf=parse_original_daophot_lookup(raw_psf)
                    record["official_spatial_daophot"]={
                        "status":"NATIVE_SPATIAL_DAOPHOT_LOOKUP_LOADED",
                        "daophot_sha256":psf["source_sha256"],
                    }
                    raw_center=fetch_ancillary_fits(
                        official_ancillary_url(url,"sciimgdaopsfcent.fits"),
                        kind="sciimgdaopsfcent.fits",timeout=archive_timeout)
                    center=compare_reconstruction_to_official_center(psf,raw_center)
                    record["original_center_psf_check"]=center
                except (HTTPError,URLError,TimeoutError,OSError,ValueError) as exc:
                    record["official_spatial_daophot"]=_failure(exc,"NATIVE_SPATIAL_DAOPHOT_OR_CENTER_UNAVAILABLE")
                    frames.append(record)
                    continue
                if record["original_center_psf_check"]["status"]!=CENTER_OK:
                    frames.append(record)
                    continue
                # Fit only the formerly EXCLUDED Gaia source set. Do not use
                # success/failure to change preselected Gaia source identities.
                for candidate in screen["screens"]:
                    if candidate["status"]!=CAT_OK:
                        record["disjoint_source_pixel_checks"].append({
                            "gaia_source_id":candidate["gaia_source_id"],
                            "status":"PROVISIONAL_ZTF_ASSOCIATION_OR_SOURCE_PROFILE_REVIEW",
                            "catalogue_screen_status":candidate["status"],
                            "originally_used_in_v116":False,
                            "fit_completed":False,
                            "gaia_ztf_physical_identity_confirmed":False,
                        })
                        continue
                    oid=int(candidate["ztf_native_per_exposure_sourceid"])
                    match=np.flatnonzero(np.asarray(cat["rows"]["sourceid"],dtype=int)==oid)
                    if len(match)!=1:
                        raise ValueError("Invalid unique PSFcat sourceid lookup")
                    i=int(match[0])
                    pixel=audit_original_source_psf_residuals(
                        url,psf,
                        source_ra=float(cat["rows"]["ra"][i]),
                        source_dec=float(cat["rows"]["dec"][i]),
                        native_x=float(cat["rows"]["xpos"][i]),
                        native_y=float(cat["rows"]["ypos"][i]),
                        timeout=archive_timeout)
                    record["disjoint_source_pixel_checks"].append({
                        "gaia_source_id":candidate["gaia_source_id"],
                        "status":pixel["status"],
                        "catalogue_screen_status":candidate["status"],
                        "originally_used_in_v116":False,
                        "fit_completed":bool(pixel["local_masked_psf_model_fit_completed"]),
                        "residual_quality_passed":pixel["status"]==MASKED_PASS,
                        "rms_over_sky_proxy":pixel.get(
                            "same_image_holdout_residual_rms_over_sky_noise_proxy"),
                        "max_positive_residual_over_sky_proxy":pixel.get(
                            "same_image_holdout_max_positive_residual_over_sky_noise_proxy"),
                        "original_masked_psf_pixel_evidence":pixel,
                        "gaia_ztf_physical_identity_confirmed":False,
                    })
                record["source_control_comparison"]=compare_disjoint_holdouts(
                    record["disjoint_source_pixel_checks"],
                    min_distinct_controls=3)
                frames.append(record)
    checks=[x for e in frames for x in e["disjoint_source_pixel_checks"]]
    pixels=[x for x in checks if x.get("fit_completed")]
    passed=[x for x in pixels if x.get("residual_quality_passed")]
    nulls=[e["shifted_sky_positional_null"] for e in frames
           if e["shifted_sky_positional_null"]["status"]=="SHIFTED_SKY_CATALOGUE_DENSITY_PROBES_COMPLETED"]
    n_actual_distinct_sources=len({x["gaia_source_id"] for x in pixels})
    selected_ids={x["source_id"] for sel in selected.values() for x in sel["controls"]}
    return {
        "schema_version":"stellarforge-v1.17-Gaia-disjoint-holdout-original-ZTF-masked-PSF-and-shifted-sky-null",
        "original_irsa_position_cone_rows_SHA_verified":original["n_rows"],
        "original_reference_ledger_source_sha256":ledger["provenance"]["original_json_sha256"],
        "n_historic_original_science_exposure_epochs":len(frames),
        "n_original_prior_technical_gaia_source_ids_excluded":len(used_ids),
        "n_new_disjoint_gaia_control_ids_preselected":len(selected_ids),
        "n_new_distinct_gaia_ids_with_original_ztf_masked_pixel_fit":n_actual_distinct_sources,
        "n_new_gaia_candidate_exposure_pairs":sum(
            e["n_new_gaia_only_preselected_source_ids"] for e in frames),
        "n_new_disjoint_gaia_original_pixel_fits_completed":len(pixels),
        "n_new_disjoint_gaia_same_image_residual_profiles_passed":len(passed),
        "n_new_disjoint_gaia_pixel_profile_reviews":sum(
            x["fit_completed"] and not x["residual_quality_passed"] for x in checks),
        "n_shifted_sky_positional_null_probes":sum(
            x["n_shifted_sky_probes"] for x in nulls),
        "n_shifted_sky_null_any_psf_source_hits":sum(
            x["n_nearest_any_psf_source_within_radius"] for x in nulls),
        "n_shifted_sky_null_quality_screened_psf_source_hits":sum(
            x["n_profile_qualified_shifted_hits"] for x in nulls),
        "n_true_independent_star_PSF_model_training_exclusions_verified":0,
        "n_calibrated_external_absolute_WCS_PSF_error_budgets":0,
        "n_authenticated_physical_Gaia_ZTF_source_identifications":0,
        "n_new_confirmed_binary_companions_or_physical_variability":0,
        "wide_cone_gaia_dr3_source_hashes":original_wide_gaia_hashes,
        "new_exact_gaia_five_parameter_response_sha256":gaia_hash,
        "gaia_only_preselected_fields":selected,
        "historic_exposure_results":frames,
        "pixel_fit_status_counts":dict(sorted(Counter(x["status"] for x in checks).items())),
        "limitations":[
            "New Gaia controls were excluded by source_id from all ten prior technical target/reference source IDs before examining ZTF image pixels. This is a disjoint PRIOR SOURCE-SET validation, not proof they were not used in original ZTF native DAOPhot model training.",
            "Gaia DR3 wide-cone screening uses g magnitude, RUWE, duplicated source, formal solution and isolation among all returned nearby Gaia stars; no quality criterion excludes unresolved, non-Gaia or extragalactic contaminants.",
            "Original per-exposure native ZTF psfcat source nearest-neighbor match <=1 arcsec and original PSF profile flags remain provisional. Independently authenticated physical Gaia/ZTF source identities still zero.",
            "The shifted-sky ±25arcsec positions are catalogue-density diagnostics, not independently generated negative controls or Bayesian/source contamination rate calibration; random shifted sky can land on true unrelated stars.",
            "Sky annulus, source mask and actual CCD science DN amplitudes are descriptive pixel quality and same-source checkerboard residuals; not independent instrument PSF/WCS calibration or absolute photometric magnitudes.",
            "The native spatial PSF model is interpolated approximately and retains unknown source training membership. Heldout Gaia IDs must not be called independently withheld PSF-construction sources.",
            "Zero/no eligible controls or archive HTTP 503 are insufficient observational access/quality, not physical absence of stars. High CIDA 11 RUWE remains an unresolved astrophysical source-model quality caveat.",
            "Original ZTF science FITS/mask pixels, native ZTF psfcat rows and DAOPhot lookup coefficients, Gaia original TAP CSV and IRSA raw photometry remain ephemeral and outside public Git and published artifacts.",
        ],
    }


def write_outputs(r:dict,dest:Path)->tuple[Path,Path]:
    dest.mkdir(parents=True,exist_ok=True)
    j=dest/"V117_NEW_GAIA_DISJOINT_SOURCE_CONTROLS_NO_RAW.json"
    m=dest/"V117_NEW_GAIA_DISJOINT_SOURCE_CONTROLS_NO_RAW.md"
    j.write_text(json.dumps(r,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf8")
    lines=[
        "# StellarForge v1.17 — New disjoint Gaia field controls and ZTF positional nulls",
        "",
        "**The new Gaia source IDs were not among the ten original v1.16 target/reference sources, but may have been in the ZTF pipeline's original PSF training set. No independent PSF/WCS calibration, physical Gaia/ZTF ID or companion discovery.**",
        "",
        f"SHA-audited original IRSA ZTF positional-cone rows: **{r['original_irsa_position_cone_rows_SHA_verified']}**.",
        f"Original dated science exposure epochs: **{r['n_historic_original_science_exposure_epochs']}**.",
        f"Previous technical source IDs explicitly excluded: **{r['n_original_prior_technical_gaia_source_ids_excluded']}**.",
        f"New Gaia-only preselected distinct source IDs: **{r['n_new_disjoint_gaia_control_ids_preselected']}**.",
        f"New source/exposure candidates: **{r['n_new_gaia_candidate_exposure_pairs']}**.",
        f"New distinct Gaia source IDs with actual original masked ZTF PSF pixel fits: **{r['n_new_distinct_gaia_ids_with_original_ztf_masked_pixel_fit']}**.",
        f"New source/exposure original masked PSF pixel fits completed: **{r['n_new_disjoint_gaia_original_pixel_fits_completed']}**.",
        f"New source/exposure same-image residual QA profiles passed: **{r['n_new_disjoint_gaia_same_image_residual_profiles_passed']}**.",
        f"Shifted-sky fixed ±25arcsec PSFcat null probes: **{r['n_shifted_sky_positional_null_probes']}**; any matching native catalogue source **{r['n_shifted_sky_null_any_psf_source_hits']}**, passing quality flags **{r['n_shifted_sky_null_quality_screened_psf_source_hits']}**.",
        "",
        "| Original field | ZTF science MJD | Gaia control preselection | Native PSF+mask pixel fits | Same-image residual QA passes | Shifted sky source hits/probes |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for e in r["historic_exposure_results"]:
        a=e["disjoint_source_pixel_checks"]
        null=e["shifted_sky_positional_null"]
        lines.append(
            f"| {e['target_field']} | {e['original_science_mjd_assumed_utc']:.6f} | "
            f"{e['n_new_gaia_only_preselected_source_ids']} | "
            f"{sum(bool(x.get('fit_completed')) for x in a)} | "
            f"{sum(bool(x.get('residual_quality_passed')) for x in a)} | "
            f"{null.get('n_nearest_any_psf_source_within_radius',0)}/{null.get('n_shifted_sky_probes',0)} |")
    lines.extend([
        "",
        "## What this does and does NOT validate",
        "",
        "- The new stars are selected based on an **independent Gaia DR3 wide-cone query**, original-quality criteria, all-Gaia-neighbor isolation and detector-field sky quadrants. All originally selected target/reference Gaia IDs are excluded BEFORE looking at native ZTF source fits and real image residuals.",
        "- A source's original ZTF PSF spatial model may have included that star among its original **survey pipeline training stars**. This membership cannot be recovered or excluded by merely withholding it from StellarForge's analysis. A claim of fully independent instrumental PSF-star validation is scientifically unsupported.",
        "- Exact formal Gaia 5D covariance and first-order geocentric geometric annual parallax are used, but Gaia/ZTF crossmatches remain **nearest-neighbor catalogue candidates** subject to multiplicity, crowding, color, timing and high-RUWE concerns.",
        "- A fixed 25arcsec coordinate shift samples the local frequency of nearby native ZTF sources; shifted positions may coincidentally contain unrelated real stars. No false-match probability or formal Bayesian source identity is calibrated.",
        "- Real masks remove bad ZTF detector pixels (official 6141 policy), PSF model DN amplitude and sky plane are fitted with checkerboard pixel holdouts of the *same image*. Pixel residual/noise ratios are NOT independent stellar PSF calibration or statistically calibrated significance.",
        "- Original survey source FITS, full native PSF catalogs, spatial PSF lookup tables, Gaia TAP CSV and IRSA photometry are processed transiently and are not committed or uploaded.",
    ])
    m.write_text("\n".join(lines)+"\n",encoding="utf8")
    return j,m


def main():
    p=argparse.ArgumentParser(description="Actual new disjoint Gaia controls, original masked ZTF PSFs and shifted catalogue sky nulls")
    p.add_argument("original_irsa_zip",type=Path)
    p.add_argument("--seed",type=Path,default=SEED)
    p.add_argument("--ledger",type=Path,default=LEDGER)
    p.add_argument("--gaia-timeout",type=float,default=25)
    p.add_argument("--archive-timeout",type=float,default=6)
    p.add_argument("--max-new-controls-per-field",type=int,default=4)
    p.add_argument("--output",type=Path,default=ROOT/"reports/generated/v1.17_disjoint_gaia")
    p.add_argument("--require-new-real-fits",action="store_true")
    a=p.parse_args()
    report=run(a.original_irsa_zip,a.seed,a.ledger,
               gaia_timeout=a.gaia_timeout,archive_timeout=a.archive_timeout,
               max_new_controls_per_field=a.max_new_controls_per_field)
    paths=write_outputs(report,a.output)
    print(json.dumps({
        "n_new_distinct_gaia_controls":report["n_new_disjoint_gaia_control_ids_preselected"],
        "n_new_original_masked_pixel_fits":report["n_new_disjoint_gaia_original_pixel_fits_completed"],
        "n_new_same_image_QA_passed":report["n_new_disjoint_gaia_same_image_residual_profiles_passed"],
        "shifted_sky_probes":report["n_shifted_sky_positional_null_probes"],
        "shifted_sky_native_catalogue_hits":report["n_shifted_sky_null_any_psf_source_hits"],
        "authenticated_physical_source_identities":0,
        "original_psf_model_training_star_membership_verified":0,
        "reports":[str(x) for x in paths],
    },indent=2))
    if a.require_new_real_fits and not report["n_new_disjoint_gaia_original_pixel_fits_completed"]:
        p.exit(2,"No independently preselected new Gaia control source yielded complete original masked ZTF pixels; this is NOT an astrophysical nondetection.\n")


if __name__=="__main__":
    main()
