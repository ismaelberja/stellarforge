"""Bounded live official ZTF detector bitmask and native field-center PSF audit.

Use exactly four preregistered ZTF g-band science frames reconstructed from a
SHA-verified original IRSA acquisition. Each Gaia candidate and target gets
only two bounded cutouts (native mask + science image). Once per exposure,
inspect the native center-of-detector PSF stamp. Never publish source FITS or
Gaia TAP CSV; only aggregate mask statistics, product hashes and statuses.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from stellarforge.v13_observational_review import review_irsa_artifact
from stellarforge.v17_field_controls import stratified_ztf_image_candidates
from stellarforge.v19_gaia_covariance import (
    fetch_gaia_astrometry,parse_gaia_astrometry,propagate_gaia_5p_formal,
)
from stellarforge.v111_reference_parallax import (
    all_required_gaia_ids,load_ledger,
)
from stellarforge.v113_official_masks_psf import (
    audit_native_center_psf,audit_one_science_source,
)

ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/"data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv"
LEDGER=ROOT/"data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json"


def run(raw_zip:Path,seed:Path=SEED,ledger_file:Path=LEDGER,*,
        gaia_timeout:float=25,image_timeout:float=6)->dict:
    if (not 1<=gaia_timeout<=60 or not 1<=image_timeout<=20):
        raise ValueError("Invalid bounded network time budget")
    original=review_irsa_artifact(raw_zip,seed)
    ledger=load_ledger(ledger_file)
    ids=all_required_gaia_ids(ledger)
    gaia_raw=fetch_gaia_astrometry(ids,timeout_sec=gaia_timeout)
    gaia=parse_gaia_astrometry(gaia_raw,expected_ids=ids)
    with Path(seed).open(newline="",encoding="utf8") as stream:
        seed_rows={str(x["gaia"]):x for x in csv.DictReader(stream)}
    if len(original["targets"])!=2 or len(ledger["exposures"])!=4:
        raise ValueError("Unexpected non-preregistered target/epoch count")
    if {r["gaia_dr3_source_id"] for r in original["targets"]}!={e["target_gaia_id"] for e in ledger["exposures"]}:
        raise ValueError("Original IRSA targets vs fixed reference ledger do not match")
    exposures=[]
    with ZipFile(raw_zip) as archive:
        for target in original["targets"]:
            sid=target["gaia_dr3_source_id"]
            seedrow=seed_rows[sid]
            photo=archive.read(f"{sid}_IRSA_RAW.csv")
            curves=stratified_ztf_image_candidates(
                photo,ra_deg=float(seedrow["ra"]),dec_deg=float(seedrow["dec"]),
                pmra_mas_yr=float(seedrow["pmra"]),
                pmdec_mas_yr=float(seedrow["pmdec"]),
                science_per_oid=6,cutout_arcsec=90)
            planned=[e for e in ledger["exposures"] if e["target_gaia_id"]==sid]
            if len(planned)!=2:
                raise ValueError("Target lacks two original dated science frames")
            candidate_ids=sorted({x["id"] for e in planned for x in e["refs"]})
            if not 1<=len(candidate_ids)<=5:
                raise ValueError("Unexpected Gaia reference candidate count")
            for planned_frame in planned:
                candidates=[x for curve in curves
                    if curve["ztf_oid"]==planned_frame["oid"]
                    and curve["band"]==planned_frame["band"]
                    for x in curve["candidates"]
                    if x["kind"]=="science" and x["mjd"] is not None
                    and abs(x["mjd"]-planned_frame["mjd"])<.00002]
                if len(candidates)!=1:
                    raise ValueError("Original ZTF dated science image cannot be uniquely verified")
                science_url=candidates[0]["url"]
                mjd=float(planned_frame["mjd"])
                native_psf=audit_native_center_psf(
                    science_url,timeout=image_timeout)
                targets=[sid]+candidate_ids
                checked=[]
                for source_id in targets:
                    predicted=propagate_gaia_5p_formal(
                        gaia[source_id],mjd_utc=mjd)
                    ra=predicted["geocentric_parallax_adjusted_ra_deg"]
                    dec=predicted["geocentric_parallax_adjusted_dec_deg"]
                    mask=audit_one_science_source(
                        science_url,source_ra_deg=ra,source_dec_deg=dec,
                        timeout=image_timeout)
                    checked.append({
                        "gaia_source_id":source_id,
                        "is_technical_target":source_id==sid,
                        "high_or_missing_gaia_ruwe_quality_warning":predicted[
                            "high_or_missing_ruwe_quality_warning"],
                        "formal_gaia_east_sigma_mas":round(
                            predicted["formal_gaia_east_sigma_mas"],6),
                        "formal_gaia_north_sigma_mas":round(
                            predicted["formal_gaia_north_sigma_mas"],6),
                        "original_fits_mask_and_science_screen":mask,
                        "physical_gaia_ztf_identity_authenticated":False,
                    })
                exposures.append({
                    "target":planned_frame["target"],
                    "gaia_target_id":sid,
                    "ztf_oid":planned_frame["oid"],
                    "filter":planned_frame["band"],
                    "science_mjd_assumed_utc":mjd,
                    "source_mask_checks":checked,
                    "native_field_center_psf":native_psf,
                    "n_reference_candidates":len(candidate_ids),
                    "n_reference_core_masks_with_verified_wcs_alignment":sum(
                        s["original_fits_mask_and_science_screen"].get(
                            "wcs_checked_and_aligned",False) for s in checked
                        if not s["is_technical_target"]),
                    "n_reference_cores_without_ztf_disqualifying_bits":sum(
                        s["original_fits_mask_and_science_screen"].get(
                            "has_unmasked_source_core_candidate",False) for s in checked
                        if not s["is_technical_target"]),
                    "astrophysical_source_identity_confirmed":False,
                    "independent_psf_wcs_calibration_completed":False,
                })
    all_sources=[s for exp in exposures for s in exp["source_mask_checks"]]
    checks=[s["original_fits_mask_and_science_screen"] for s in all_sources]
    native=[x["native_field_center_psf"] for x in exposures]
    return {
        "schema_version":"stellarforge-v1.13-original-ztf-bitmask-and-native-center-psf",
        "original_ztf_irsa_rows_sha_verified":original["n_rows"],
        "original_v18_derived_ledger_sha256":ledger["provenance"][
            "original_json_sha256"],
        "official_gaia_dr3_5p_exact_ids":len(ids),
        "gaia_tap_response_sha256":hashlib.sha256(gaia_raw).hexdigest(),
        "n_original_dated_science_exposures":len(exposures),
        "n_native_center_psf_fits_requested":len(native),
        "n_native_center_psf_stamps_parsed":sum(
            x.get("status")=="NATIVE_CENTER_PSF_STAMP_PROVISIONALLY_PARSED"
            for x in native),
        "n_sources_with_science_and_mask_attempted":len(checks),
        "n_sources_with_matching_mask_and_science_wcs":sum(
            x.get("wcs_checked_and_aligned",False) for x in checks),
        "n_source_cores_without_disqualifying_ztf_mask_bits":sum(
            x.get("has_unmasked_source_core_candidate",False) for x in checks),
        "n_source_cores_with_disqualifying_mask_bits":sum(
            x.get("status")=="MASK_CORE_HAS_BAD_BITS_OR_NONFINITE_SCIENCE"
            for x in checks),
        "n_source_mask_or_science_transport_http_503":sum(
            x.get("http_status")==503 for x in checks),
        "n_psf_native_transport_http_503":sum(
            x.get("http_status")==503 for x in native),
        "mask_outcome_counts":dict(sorted(Counter(
            str(x.get("status","UNKNOWN")) for x in checks).items())),
        "native_center_psf_outcome_counts":dict(sorted(Counter(
            str(x.get("status","UNKNOWN")) for x in native).items())),
        "exposures":exposures,
        "n_calibrated_instrument_psf_models_at_source_positions":0,
        "n_independently_calibrated_detector_wcs":0,
        "n_confirmed_gaia_ztf_astrophysical_associations":0,
        "n_confirmed_binary_companions":0,
        "n_new_confirmed_physical_variability_events":0,
        "limitations":[
            "ZTF bitmask archival bits 6141 are official bad-pixel flags; source-identification bits 1/11 are not bad pixels. A clean nominal aperture does not imply a single isolated star or unblended astrophysical source.",
            "A mask is applied only if the original science/mask cutouts have matching shapes and celestial WCS grid mappings to within 0.05 pixel; otherwise the status is unvalidated.",
            "The official sciimgdaopsfcent.fits is a PSF at the CENTER of the native science frame; it is NOT a PSF evaluated at each technical source coordinate, a spatially varying DAOPhot table evaluation, or a field calibrated model.",
            "No original PSF-fit catalog source identity, saturation severity calibration, pixel variance array, detector WCS distortion fit or held-out astrometric reference-star uncertainties are established.",
            "Gaia 5D formal covariance and Earth-geocentric first-order annual parallax omit high-RUWE non-single-star systematics, full observatory topocentre/refraction/aberration and exact FITS timescale validation.",
            "All image/Gaia requests are bounded and short-lived. Remote HTTP 503 is an access failure, never physical non-detection.",
            "The original IRSA ZTF photometry is a position query only; it is not an independent Gaia-ZTF astrophysical source match.",
            "Raw third-party Gaia CSV/ZTF FITS pixels and original photometric rows are excluded from public Git and workflow aggregate artifacts.",
        ],
    }


def write_outputs(r:dict,folder:Path)->tuple[Path,Path]:
    folder.mkdir(parents=True,exist_ok=True)
    j=folder/"V113_ZTF_MASK_NATIVE_PSF_QA_NO_RAW.json"
    m=folder/"V113_ZTF_MASK_NATIVE_PSF_QA_NO_RAW.md"
    j.write_text(json.dumps(r,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf8")
    lines=[
        "# StellarForge v1.13 — Original ZTF detector masks and native field-center PSFs",
        "",
        "**Mask/PSF instrument-product quality audit ONLY — not source crossmatch, calibrated WCS/PSF, single-star certification, companion detection, or physical variability.**",
        "",
        f"Original IRSA photometry records SHA-audited: **{r['original_ztf_irsa_rows_sha_verified']}**.",
        f"Original science epochs: **{r['n_original_dated_science_exposures']}**.",
        f"Candidate source centers (target + Gaia references): **{r['n_sources_with_science_and_mask_attempted']}**.",
        f"Science+mask celestial WCS grid aligned: **{r['n_sources_with_matching_mask_and_science_wcs']}**.",
        f"Aligned nominal source cores with no disqualifying ZTF mask bits: **{r['n_source_cores_without_disqualifying_ztf_mask_bits']}**.",
        f"Native science field-center PSF stamps parsed: **{r['n_native_center_psf_stamps_parsed']}/{r['n_native_center_psf_fits_requested']}**.",
        f"Mask/science HTTP 503: **{r['n_source_mask_or_science_transport_http_503']}**.",
        "",
        "| Source field | Original date MJD | Source mask WCS aligned | Candidate reference unmasked cores | Native center PSF product |",
        "|---|---:|---:|---:|---|",
    ]
    for e in r["exposures"]:
        lines.append(
            f"| {e['target']} | {e['science_mjd_assumed_utc']:.6f} | "
            f"{sum(s['original_fits_mask_and_science_screen'].get('wcs_checked_and_aligned',False) for s in e['source_mask_checks'])} | "
            f"{e['n_reference_cores_without_ztf_disqualifying_bits']} | "
            f"{e['native_field_center_psf']['status']} |")
    lines.extend([
        "",
        "## Interpretation",
        "",
        "- ZTF official disqualifying mask bits: **6141**; detection marker bits 1 and 11 are not themselves detector defects. A core aperture with no disqualifying flags only passes that specific mask screen.",
        "- Same-dated ZTF mask and science cutouts must have **identical dimensions and celestial WCS grid alignment** before any mask bit is interpreted at an astronomical source location.",
        "- The official native \`sciimgdaopsfcent.fits\` is a **science-field-center** PSF stamp, **not a spatially varying PSF evaluated at these Gaia targets/references**. Its existence does not mean the instrumental PSF model is independently validated.",
        "- Detector saturation, source blending, unknown color/chromatic terms, real exposure time scale and non-Gaia neighbors remain unresolved. CIDA 11 high Gaia RUWE remains a source-model concern.",
        "- Original HTTP 503 and failed image access do **not** imply astrophysical nondetection. Only the original four preregistered science epochs were used.",
        "- No new astrophysical associations, companions, PSF-calibrated reference stars, independent instrument WCS solutions or physical variability events were confirmed.",
        "",
    ])
    m.write_text("\n".join(lines),encoding="utf8")
    return j,m


def main():
    p=argparse.ArgumentParser(description="Official original ZTF mask and native center PSF science gates")
    p.add_argument("original_irsa_zip",type=Path)
    p.add_argument("--seed",type=Path,default=SEED)
    p.add_argument("--ledger",type=Path,default=LEDGER)
    p.add_argument("--image-timeout",type=float,default=6)
    p.add_argument("--gaia-timeout",type=float,default=25)
    p.add_argument("--output",type=Path,
                   default=ROOT/"reports/generated/v1.13_masks_native_psf")
    p.add_argument("--require-some-instrument-products",action="store_true")
    args=p.parse_args()
    result=run(args.original_irsa_zip,args.seed,args.ledger,
               image_timeout=args.image_timeout,gaia_timeout=args.gaia_timeout)
    paths=write_outputs(result,args.output)
    print(json.dumps({
        "mask_source_checks":result["n_sources_with_science_and_mask_attempted"],
        "aligned_mask_science_images":result["n_sources_with_matching_mask_and_science_wcs"],
        "native_center_psfs_parsed":result["n_native_center_psf_stamps_parsed"],
        "calibrated_local_psfs":0,
        "independent_wcs_calibrations":0,
        "report_files":[str(x) for x in paths],
    },indent=2))
    if args.require_some_instrument_products and (
            result["n_sources_with_matching_mask_and_science_wcs"]+
            result["n_native_center_psf_stamps_parsed"]==0):
        p.exit(2,"No official ZTF mask/PSF instrument product validated; this is archive access failure, not astronomical non-detection.\n")


if __name__=="__main__":
    main()
