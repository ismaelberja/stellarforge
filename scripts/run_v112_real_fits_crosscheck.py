"""Observed-data v1.12 image-level remeasurement with full Gaia source metadata.

Reconstruct original two g-band science epochs per technical target from the
v1.3 SHA-verified original IRSA ZIP, match to the original v1.8 evidence dates,
and re-download 20 bounded ZTF cutouts from the *dated science product*:
four target FITS + three FT Tau references in two epochs + five CIDA 11
references in two epochs. No raw FITS, original photometry, or TAP CSV is
written or uploaded. Strict science gates remain false.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path
from urllib.error import HTTPError, URLError
from zipfile import ZipFile

from stellarforge.v13_observational_review import review_irsa_artifact
from stellarforge.v17_field_controls import stratified_ztf_image_candidates
from stellarforge.v19_gaia_covariance import (
    fetch_gaia_astrometry, parse_gaia_astrometry, propagate_gaia_5p_formal,
)
from stellarforge.v111_reference_parallax import (
    load_ledger, all_required_gaia_ids,
)
from stellarforge.v112_pixel_model_crosscheck import (
    analyze_real_science_reference_cutout, audit_provisional_field_references,
    SUCCESS, REVIEW,
)

ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/"data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv"
LEDGER=ROOT/"data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json"


def run(original_irsa_zip: Path, seed_path:Path=SEED, *,
        ledger_path:Path=LEDGER,
        image_timeout:float=6, gaia_timeout:float=25) -> dict:
    if (not 1<=image_timeout<=20 or not 1<=gaia_timeout<=60):
        raise ValueError("Archive request timeout outside bounded limits")
    ledger=load_ledger(ledger_path)
    original=review_irsa_artifact(original_irsa_zip,seed_path)
    expected=all_required_gaia_ids(ledger)
    gaia_csv=fetch_gaia_astrometry(expected,timeout_sec=gaia_timeout)
    entries=parse_gaia_astrometry(gaia_csv,expected_ids=expected)
    with Path(seed_path).open(newline="",encoding="utf8") as h:
        seed={str(row["gaia"]):row for row in csv.DictReader(h)}
    if len(ledger["exposures"])!=4 or len(original["targets"])!=2:
        raise ValueError("Expected exactly the four preregistered science epochs/two targets")
    prior={e["target_gaia_id"] for e in ledger["exposures"]}
    verified={t["gaia_dr3_source_id"] for t in original["targets"]}
    if prior!=verified:
        raise ValueError("Original official IRSA and derived ledger target IDs disagree")
    exposures=[]
    with ZipFile(original_irsa_zip) as archive:
        for target in original["targets"]:
            sid=target["gaia_dr3_source_id"]
            source=seed[sid]
            photometry=archive.read(f"{sid}_IRSA_RAW.csv")
            curves=stratified_ztf_image_candidates(
                photometry,
                ra_deg=float(source["ra"]),dec_deg=float(source["dec"]),
                pmra_mas_yr=float(source["pmra"]),
                pmdec_mas_yr=float(source["pmdec"]),
                science_per_oid=6,cutout_arcsec=90,
            )
            original_exposures=[e for e in ledger["exposures"]
                                if e["target_gaia_id"]==sid]
            if len(original_exposures)!=2:
                raise ValueError("Expected two original science dates for each Gaia target")
            gaia_reference_ids=sorted({
                ref["id"] for e in original_exposures for ref in e["refs"]})
            if not 1<=len(gaia_reference_ids)<=5:
                raise ValueError("Outside preregistered Gaia reference source budget")
            for orig in original_exposures:
                match=[c for curve in curves
                       if curve["ztf_oid"]==orig["oid"] and curve["band"]==orig["band"]
                       for c in curve["candidates"]
                       if c["kind"]=="science" and c["mjd"] is not None and
                       abs(c["mjd"]-orig["mjd"])<.00002]
                if len(match)!=1:
                    raise ValueError("Original v1.8 MJD not uniquely present in SHA-audited ZTF input")
                cutout=match[0]
                mjd=float(orig["mjd"])
                target_gaia=propagate_gaia_5p_formal(entries[sid],mjd_utc=mjd)
                result=analyze_real_science_reference_cutout(
                    cutout["url"],target_gaia,mjd_assumed_utc=mjd,
                    timeout=image_timeout)
                refs=[]
                for refid in gaia_reference_ids:
                    gaia=propagate_gaia_5p_formal(
                        entries[refid],mjd_utc=mjd)
                    model=analyze_real_science_reference_cutout(
                        cutout["url"],gaia,mjd_assumed_utc=mjd,
                        timeout=image_timeout)
                    refs.append(model)
                holdout=audit_provisional_field_references(refs)
                exposures.append({
                    "target_name":orig["target"],
                    "target_gaia_id":sid,
                    "source_oid":orig["oid"],
                    "source_band":orig["band"],
                    "science_mjd_assumed_utc":mjd,
                    "original_v18_target_image_fit_status":orig["target_fit_status"],
                    "original_v18_reference_image_models_fitted":len(orig["refs"]),
                    "new_gaia_5p_corrected_target_image_remeasurement":result,
                    "reference_image_remeasurements":refs,
                    "same_science_product_heldout_reference_diagnostics":holdout,
                    "target_astrophysical_identity_verified":False,
                    "real_zft_instrument_wcs_calibrated":False,
                })
    ref_reports=[r for e in exposures for r in e["reference_image_remeasurements"]]
    tar_reports=[e["new_gaia_5p_corrected_target_image_remeasurement"]
                 for e in exposures]
    done=lambda r:r.get("status") in (SUCCESS,REVIEW)
    all_reports=tar_reports+ref_reports
    estimator_disagreements=[
        r["aperture_vs_gaussian_centroid_difference_arcsec"]
        for r in all_reports if done(r) and
        r.get("aperture_vs_gaussian_centroid_difference_arcsec") is not None]
    return {
        "schema_version":"stellarforge-v1.12-real-ztf-fits-centroid-estimator-comparison",
        "original_official_irsa_raw_rows_sha_checked":original["n_rows"],
        "original_derived_v18_aggregate_sha256":ledger["provenance"][
            "original_json_sha256"],
        "gaia_dr3_exact_ids_with_5p_formal_covariance":len(expected),
        "gaia_tap_raw_response_sha256":hashlib.sha256(gaia_csv).hexdigest(),
        "n_original_science_exposures":len(exposures),
        "n_target_fits_attempted":len(tar_reports),
        "n_reference_fits_attempted":len(ref_reports),
        "n_real_fits_image_requests":len(tar_reports)+len(ref_reports),
        "n_remote_http_503_failures":sum(r.get("http_status")==503 for r in all_reports),
        "n_incomplete_pixel_screens":sum(
            r.get("status")=="APERTURE_CENTROID_SCREEN_INCOMPLETE" for r in all_reports),
        "median_two_model_centroid_disagreement_arcsec":(
            round(statistics.median(estimator_disagreements),6)
            if estimator_disagreements else None),
        "n_target_fits_with_two_centroid_models":sum(done(r) for r in tar_reports),
        "n_ref_fits_with_two_centroid_models":sum(done(r) for r in ref_reports),
        "n_references_with_provisionally_consistent_image_models":sum(
            r.get("status")==SUCCESS for r in ref_reports),
        "n_exposures_with_3plus_provisional_reference_controls":sum(
            e["same_science_product_heldout_reference_diagnostics"][
                "n_provisionally_image_model_consistent"]>=3
            for e in exposures),
        "exposures":exposures,
        "n_independently_calibrated_instrumental_WCS":0,
        "n_empirical_single_star_PSF_standards_authenticated":0,
        "n_confirmed_gaia_ztf_source_identities":0,
        "n_confirmed_companions":0,
        "n_new_physical_variability_events":0,
        "limitations":[
            "Both aperture and Gaussian centroids use the SAME original science FITS pixels, not statistically independent observations.",
            "Target and reference Gaia predicted positions include first-order Earth-geocentric annual parallax and full five-parameter formal catalogue covariance, but not an independently validated instrument error budget.",
            "No calibrated ZTF pixel bitmask/saturation classification or spatially variable empirical PSF is applied, so a passing profile is not proof of an isolated single star.",
            "FITS timing keywords are compared with the historical query MJD if available, but the absolute observatory time scale is not independently verified.",
            "The original v1.8 reference selection is a small positional Gaia candidate set; colors, crowding and non-Gaia contaminants are not independently vetted.",
            "The original ZTF photometry is a cone query and Gaia-ZTF physical source identity has not been authenticated.",
            "CIDA 11 high Gaia DR3 RUWE is a serious potential non-single-star astrometric model bias.",
            "Only 2 science exposures per target (one g-band OID each) were tested, not the complete six ZTF oid/filter data sets.",
            "Gaia/ZTF HTTP errors are transport failures, not astrophysical non-detections.",
        ],
    }


def write_outputs(report:dict, folder:Path):
    folder.mkdir(parents=True,exist_ok=True)
    j=folder/"V112_FITS_CENTROID_MODEL_CROSSCHECK_NO_RAW.json"
    m=folder/"V112_FITS_CENTROID_MODEL_CROSSCHECK_NO_RAW.md"
    j.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n",
                 encoding="utf8")
    lines=[
        "# StellarForge v1.12 — original FITS Gaussian-vs-aperture pixel model check",
        "",
        "**No physical Gaia–ZTF identity, independently calibrated WCS, vetted empirical PSF or companion detection is established.**",
        "",
        f"Original ZTF positional-query rows SHA-checked: **{report['original_official_irsa_raw_rows_sha_checked']}**.",
        f"Exact Gaia 5p solutions: **{report['gaia_dr3_exact_ids_with_5p_formal_covariance']}**.",
        f"Real FITS requests: **{report['n_real_fits_image_requests']}**.",
        f"HTTP 503 archive failures: **{report['n_remote_http_503_failures']}** (transport only, not physical non-detections).",
        f"Image pixel-screen inconclusive: **{report['n_incomplete_pixel_screens']}**.",
        f"Median Gaussian vs aperture centroid difference among complete screens: **{report['median_two_model_centroid_disagreement_arcsec']} arcsec** (model sensitivity, NOT instrument accuracy).",
        f"Target FITS with two centroid estimates: **{report['n_target_fits_with_two_centroid_models']}**.",
        f"Gaia reference FITS with two estimates: **{report['n_ref_fits_with_two_centroid_models']}**.",
        f"Model-consistent reference *candidates*: **{report['n_references_with_provisionally_consistent_image_models']}**.",
        "",
        "| Target | MJD assumed UTC | Target screen | Ref screens | Candidate controls passing both models | Candidate LOO eligible |",
        "|---|---:|---|---:|---:|---|",
    ]
    for e in report["exposures"]:
        h=e["same_science_product_heldout_reference_diagnostics"]
        g=h["gaussian_reference_internal_holdout"]
        lines.append(
            f"| {e['target_name']} | {e['science_mjd_assumed_utc']:.6f} | "
            f"{e['new_gaia_5p_corrected_target_image_remeasurement']['status']} | "
            f"{len(e['reference_image_remeasurements'])} | "
            f"{h['n_provisionally_image_model_consistent']} | "
            f"{g['status'] != 'INSUFFICIENT_INDEPENDENT_REFERENCES_FOR_HOLDOUT'} |")
    lines.extend([
        "", "## Essential caveats", "",
        "- A local positive-flux aperture moment and an elliptical Gaussian are two estimators of the **same** pixels. Agreement between them does not validate a star, astrometric accuracy or an independent detector distortion model.",
        "- The code compares original science-image nominal header WCS coordinates with Gaia five-parameter positions corrected by **geometric Earth-geocentric annual parallax**, not full topocentric apparent positions.",
        "- No complete detector bad-pixel/saturation mask, filter-dependent empirical PSF or calibrated correlated noise model is available. FITS timing metadata is checked when present but does not establish absolute time scale.",
        "- The small original Gaia reference sample is not an independently authenticated set of single, clean PSF standards. Inadequate fit profiles or remote HTTP errors are treated as failures to validate, not astrophysical absence.",
        "- Passing images and low reference LOO residuals are **not** calibrated WCS uncertainties, confirmed Gaia/ZTF identities, physical companions, or stellar variability detections.",
        "",
    ])
    m.write_text("\n".join(lines),encoding="utf8")
    return j,m


def main():
    p=argparse.ArgumentParser(description="Read-only ZTF original FITS aperture-vs-Gaussian quality pilot, Gaia 5D corrected")
    p.add_argument("original_irsa_zip",type=Path)
    p.add_argument("--seed",type=Path,default=SEED)
    p.add_argument("--ledger",type=Path,default=LEDGER)
    p.add_argument("--output",type=Path,
                   default=ROOT/"reports/generated/v1.12_fits_crosscheck")
    p.add_argument("--image-timeout",type=float,default=6)
    p.add_argument("--gaia-timeout",type=float,default=25)
    p.add_argument("--require-some-valid-images",action="store_true")
    args=p.parse_args()
    result=run(args.original_irsa_zip,args.seed,
               ledger_path=args.ledger,image_timeout=args.image_timeout,
               gaia_timeout=args.gaia_timeout)
    paths=write_outputs(result,args.output)
    print(json.dumps({
        "image_requests":result["n_real_fits_image_requests"],
        "target_image_models":result["n_target_fits_with_two_centroid_models"],
        "reference_image_models":result["n_ref_fits_with_two_centroid_models"],
        "provisionally_consistent_reference_models":
            result["n_references_with_provisionally_consistent_image_models"],
        "authenticated_psf_standards":0,
        "calibrated_instrument_wcs":0,
        "summary_files":[str(x) for x in paths],
    },indent=2))
    if args.require_some_valid_images and (
        result["n_target_fits_with_two_centroid_models"]+
        result["n_ref_fits_with_two_centroid_models"]==0):
        p.exit(2,"No usable FITS science images: archive outage is not a non-detection.\n")


if __name__=="__main__":
    main()
