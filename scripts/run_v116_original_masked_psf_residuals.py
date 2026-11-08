"""v1.16 official original ZTF science+bitmask spatial-PSF pixel residual pilot.

Only four fixed dated ZTF science exposures, ten known Gaia source IDs,
original SHA-verified ZTF IRSA positional-query photometric artifact.
Official source PSFcat, spatial DAOPhot and center PSF provenance must pass
before trying same-exposure WCS-aligned science/mask source pixels.

A fit uses a checkerboard of pixels in the SAME star image and checks
withheld other pixels. It is NOT an independent stellar/astrometric holdout,
nor photometric calibration, deblending, source physical identification,
companions or variability.
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
from stellarforge.v19_gaia_covariance import (
    fetch_gaia_astrometry,parse_gaia_astrometry,propagate_gaia_5p_formal,
)
from stellarforge.v111_reference_parallax import (
    all_required_gaia_ids,load_ledger,
)
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

ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/"data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv"
LEDGER=ROOT/"data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json"
MODEL_OK="OFFICIAL_CENTER_PSF_APPROXIMATE_MODEL_AGREEMENT"
CAT_OK="PROVISIONAL_CATALOGUE_NEAREST_AND_PROFILE_SCREEN_PASSED"
GOOD_PIXEL="PROVISIONAL_ORIGINAL_MASKED_PSF_PIXEL_RESIDUAL_SCREEN_PASSED"
REVIEW_PIXEL="ORIGINAL_MASKED_PSF_PIXEL_RESIDUAL_REVIEW_REQUIRED"


def _error_status(exc:Exception,kind:str)->dict:
    record={"status":kind,"error_type":type(exc).__name__}
    if isinstance(exc,HTTPError):
        record["http_status"]=int(exc.code)
    return record


def run(original_zip:Path,seed_file:Path=SEED,ledger_file:Path=LEDGER,*,
        gaia_timeout:float=25,archive_timeout:float=6)->dict:
    if not(1<=gaia_timeout<=60 and 1<=archive_timeout<=20):
        raise ValueError("Original NASA archive request timeout outside limits")
    original=review_irsa_artifact(original_zip,seed_file)
    ledger=load_ledger(ledger_file)
    required=all_required_gaia_ids(ledger)
    rawgaia=fetch_gaia_astrometry(required,timeout_sec=gaia_timeout)
    entries=parse_gaia_astrometry(rawgaia,expected_ids=required)
    with Path(seed_file).open(newline="",encoding="utf8") as f:
        seed={str(r["gaia"]):r for r in csv.DictReader(f)}
    if len(original["targets"])!=2 or len(ledger["exposures"])!=4:
        raise ValueError("Non-preregistered original FT Tau/CIDA 11 exposures")
    if {t["gaia_dr3_source_id"] for t in original["targets"]}!={e["target_gaia_id"] for e in ledger["exposures"]}:
        raise ValueError("Original IRSA source archive vs reference ledger ID mismatch")
    frames=[]
    with ZipFile(original_zip) as archive:
        for target in original["targets"]:
            sid=target["gaia_dr3_source_id"]
            r=seed[sid]
            curves=stratified_ztf_image_candidates(
                archive.read(f"{sid}_IRSA_RAW.csv"),
                ra_deg=float(r["ra"]),dec_deg=float(r["dec"]),
                pmra_mas_yr=float(r["pmra"]),
                pmdec_mas_yr=float(r["pmdec"]),
                science_per_oid=6,cutout_arcsec=90)
            original_dates=[e for e in ledger["exposures"] if e["target_gaia_id"]==sid]
            if len(original_dates)!=2:
                raise ValueError("Wrong historical original ZTF target date count")
            ref_ids=sorted({star["id"] for e in original_dates for star in e["refs"]})
            if not 1<=len(ref_ids)<=5:
                raise ValueError("Unexpected Gaia reference candidate budget")
            for e in original_dates:
                matches=[cand for curve in curves
                    if curve["ztf_oid"]==e["oid"] and curve["band"]==e["band"]
                    for cand in curve["candidates"]
                    if cand["kind"]=="science" and cand["mjd"] is not None
                    and abs(float(cand["mjd"])-float(e["mjd"]))<.00002]
                if len(matches)!=1:
                    raise ValueError("Original ZTF science exposure/path cannot be independently reconstructed")
                url=matches[0]["url"]
                positions=[]
                for gid in [sid]+ref_ids:
                    p=propagate_gaia_5p_formal(entries[gid],mjd_utc=float(e["mjd"]))
                    positions.append({
                        "source_id":gid,
                        "geocentric_parallax_adjusted_ra_deg":
                            p["geocentric_parallax_adjusted_ra_deg"],
                        "geocentric_parallax_adjusted_dec_deg":
                            p["geocentric_parallax_adjusted_dec_deg"],
                    })
                record={
                    "target_field":e["target"],
                    "gaia_target_source_id":sid,
                    "source_oid":e["oid"],
                    "band":e["band"],
                    "original_science_mjd_assumed_utc":float(e["mjd"]),
                    "n_gaia_source_predictions":len(positions),
                    "original_native_psfcat":{"status":"PSFCAT_NOT_AVAILABLE"},
                    "original_spatial_daophot":{"status":"DAOPHOT_NOT_AVAILABLE"},
                    "original_center_fits_check":{"status":"OFFICIAL_CENTER_NOT_AVAILABLE"},
                    "source_psf_pixel_residual_checks":[],
                    "physical_ztf_gaia_source_association_confirmed":False,
                    "instrument_absolute_wcs_uncertainty_calibrated":False,
                }
                # One official full source catalogue and one DAOPhot model per
                # original exposure. No third-party raw payload is persisted.
                try:
                    rawcat=fetch_native_psf_product(
                        official_psf_product_url(url,"psfcat.fits"),
                        kind="psfcat.fits",timeout=archive_timeout)
                    cat=parse_psf_fit_catalogue(rawcat)
                    screens=screen_psf_catalogue_targets(cat,positions)
                    record["original_native_psfcat"]={
                        "status":"PSFCAT_FITS_SOURCE_SCREEN_COMPLETED",
                        "native_psfcat_sha256":cat["sha256"],
                        "n_native_exposure_psfcat_rows":cat["n_native_psf_catalogue_rows"],
                        "n_provisional_psf_source_candidates":
                            screens["n_provisional_unique_nearest_source_candidates"],
                    }
                except (HTTPError,URLError,TimeoutError,OSError,ValueError) as exc:
                    record["original_native_psfcat"]=_error_status(
                        exc,"OFFICIAL_ORIGINAL_PSF_CATALOGUE_UNAVAILABLE")
                    frames.append(record)
                    continue
                try:
                    rawdao=fetch_native_psf_product(
                        official_psf_product_url(url,"sciimgdao.psf"),
                        kind="sciimgdao.psf",timeout=archive_timeout)
                    native=parse_original_daophot_lookup(rawdao)
                    record["original_spatial_daophot"]={
                        "status":"ORIGINAL_SPATIAL_DAOPHOT_LOOKUP_PARSED",
                        "native_daophot_sha256":native["source_sha256"],
                        "n_spatial_lookup_tables":native["n_lookup_tables"],
                        "lookup_side_samples":native["lookup_side_samples"],
                    }
                except (HTTPError,URLError,TimeoutError,OSError,ValueError) as exc:
                    record["original_spatial_daophot"]=_error_status(
                        exc,"OFFICIAL_SPATIAL_DAOPHOT_UNAVAILABLE")
                    frames.append(record)
                    continue
                try:
                    rawcenter=fetch_ancillary_fits(
                        official_ancillary_url(url,"sciimgdaopsfcent.fits"),
                        kind="sciimgdaopsfcent.fits",timeout=archive_timeout)
                    center=compare_reconstruction_to_official_center(
                        native,rawcenter)
                    record["original_center_fits_check"]=center
                except (HTTPError,URLError,TimeoutError,OSError,ValueError) as exc:
                    record["original_center_fits_check"]=_error_status(
                        exc,"OFFICIAL_FIELD_CENTER_FITS_UNAVAILABLE")
                # No real-pixel PSF model fit if even the same-pipeline
                # native center PSF shape sanity check is absent or disagrees.
                if record["original_center_fits_check"]["status"]!=MODEL_OK:
                    frames.append(record)
                    continue
                for candidate in screens["screens"]:
                    if candidate.get("status")!=CAT_OK:
                        continue
                    z=int(candidate["ztf_native_per_exposure_sourceid"])
                    idx=np.flatnonzero(np.asarray(cat["rows"]["sourceid"],dtype=int)==z)
                    if len(idx)!=1:
                        raise ValueError("Same-exposure native sourceid must be unique")
                    k=int(idx[0])
                    native_x=float(cat["rows"]["xpos"][k])
                    native_y=float(cat["rows"]["ypos"][k])
                    ra=float(cat["rows"]["ra"][k])
                    dec=float(cat["rows"]["dec"][k])
                    fit=audit_original_source_psf_residuals(
                        url,native,source_ra=ra,source_dec=dec,
                        native_x=native_x,native_y=native_y,
                        timeout=archive_timeout)
                    record["source_psf_pixel_residual_checks"].append({
                        "provisional_gaia_id":candidate["gaia_source_id"],
                        "is_technical_target":candidate["gaia_source_id"]==sid,
                        "native_ztf_per_exposure_psfcat_sourceid":z,
                        "provisional_native_catalogue_separation_arcsec":
                            candidate["nearest_source_separation_arcsec"],
                        "original_science_mask_psf_result":fit,
                        "independently_confirmed_source_identity":False,
                    })
                frames.append(record)
    all_fits=[s for e in frames for s in e["source_psf_pixel_residual_checks"]]
    fit_status=[s["original_science_mask_psf_result"] for s in all_fits]
    cent=[e["original_center_fits_check"] for e in frames]
    attempted=len(fit_status)
    valid=[s for s in fit_status if s.get("local_masked_psf_model_fit_completed")]
    return {
        "schema_version":"stellarforge-v1.16-original-masked-ztf-science-pixel-spatial-psf-residuals",
        "original_irsa_ztf_position_query_rows_sha_checked":original["n_rows"],
        "original_v18_derived_reference_ledger_sha256":ledger["provenance"]["original_json_sha256"],
        "gaia_dr3_exact_five_parameter_ids":len(required),
        "gaia_dr3_raw_tap_response_sha256":hashlib.sha256(rawgaia).hexdigest(),
        "n_independent_historical_science_exposures":len(frames),
        "n_native_psfcat_exposures_accessible":sum(
            e["original_native_psfcat"]["status"]=="PSFCAT_FITS_SOURCE_SCREEN_COMPLETED" for e in frames),
        "n_native_spatial_daophot_models_parsed":sum(
            e["original_spatial_daophot"]["status"]=="ORIGINAL_SPATIAL_DAOPHOT_LOOKUP_PARSED" for e in frames),
        "n_native_center_fits_model_checks_passed":sum(
            c["status"]==MODEL_OK for c in cent),
        "n_candidate_source_pairs_original_science_and_mask_attempted":attempted,
        "n_original_science_mask_psf_residual_fits_completed":len(valid),
        "n_provisional_residual_profile_pixel_screens_passed":sum(
            v.get("status")==GOOD_PIXEL for v in valid),
        "n_original_residual_profile_review_required":sum(
            v.get("status")==REVIEW_PIXEL for v in valid),
        "n_mask_science_remote_http503":sum(
            f.get("http_status")==503 for f in fit_status),
        "n_technical_target_residual_fits_completed":sum(
            s["is_technical_target"] and s["original_science_mask_psf_result"].get(
                "local_masked_psf_model_fit_completed",False)
            for s in all_fits),
        "n_reference_candidate_residual_fits_completed":sum(
            not s["is_technical_target"] and s["original_science_mask_psf_result"].get(
                "local_masked_psf_model_fit_completed",False)
            for s in all_fits),
        "source_residual_status_counts":dict(sorted(Counter(
            s.get("status","UNKNOWN") for s in fit_status).items())),
        "historical_exposures":frames,
        "n_independently_authenticated_gaia_ztf_physical_identities":0,
        "n_independently_validated_field_star_psfs":0,
        "n_calibrated_absolute_instrument_detector_wcs_error_models":0,
        "n_confirmed_new_binary_companions_or_physical_variability":0,
        "limitations":[
            "The model comes from the original ZTF spatial DAOPhot lookup approximation, native per-source x/y, and its center FITS from the SAME pipeline. It is not independently calibrated against known isolated stars.",
            "Source cutouts are centered on the native per-exposure ZTF psfcat RA/Dec, which is a catalogue extraction estimate, not independently authenticated as the same physical Gaia source.",
            "Original science pixel values are in DN and the fitted amplitude is an uncalibrated model DN scale. No zeropoint, exposure time, color, gain, read noise or covariance-correct calibrated stellar flux is claimed.",
            "Source and sky background model fit uses a checkerboard pixel holdout from the same star's same CCD image; it is not an independent astrophysical star/exposure validation.",
            "Bad ZTF mask pixels use the official 6141 bit template, including saturation bit 8; a clean mask does not ensure deblending, absence of nebulosity or optical source multiplicity.",
            "Native catalogue x/y fractional phase and celestial WCS science cutout position must agree within 0.22 image pixel and science/mask WCS must align within 0.05 pixel; unavailable or mismatched sources are review/fail, not sky nondetections.",
            "The sky noise is an annular MAD proxy, not a physically calibrated independent error variance; residual/noise ratios are descriptive engineering screening numbers.",
            "Some original ZTF source cutouts may fail remote HTTP 503. This is archive transport, not absence of the star on the CCD.",
            "CIDA 11 high Gaia RUWE and the lack of source-level independent false-match and local PSF photometric covariance remain unresolved.",
            "Raw survey science FITS, detector masks, original DAOPhot lookup arrays, native PSF catalogue rows, Gaia TAP tables and IRSA photometry are never placed into public Git or CI artifacts.",
        ],
    }


def write_outputs(result:dict,out:Path)->tuple[Path,Path]:
    out.mkdir(parents=True,exist_ok=True)
    j=out/"V116_ORIGINAL_SCIENCE_MASK_SPATIAL_PSF_RESIDUALS_NO_RAW.json"
    m=out/"V116_ORIGINAL_SCIENCE_MASK_SPATIAL_PSF_RESIDUALS_NO_RAW.md"
    j.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf8")
    lines=[
        "# StellarForge v1.16 — actual ZTF science+bitmask source PSF pixel residual pilot",
        "",
        "**Uncalibrated original science DN residual screen only; no physical Gaia–ZTF source identity, independently validated PSF, confirmed variability, or full detector WCS precision.**",
        "",
        f"SHA-verified original IRSA ZTF positional cone records: **{result['original_irsa_ztf_position_query_rows_sha_checked']}**.",
        f"Original four dated science exposures: **{result['n_independent_historical_science_exposures']}**.",
        f"Original ZTF native spatial DAOPhot models parsed: **{result['n_native_spatial_daophot_models_parsed']}**.",
        f"Same-pipeline native center FITS reconstruction checks passed: **{result['n_native_center_fits_model_checks_passed']}**.",
        f"Candidate source science+mask FITS requests: **{result['n_candidate_source_pairs_original_science_and_mask_attempted']}**.",
        f"Actual masked science-pixel PSF fits completed: **{result['n_original_science_mask_psf_residual_fits_completed']}**.",
        f"Provisional same-image checkerboard residual screens passed: **{result['n_provisional_residual_profile_pixel_screens_passed']}**.",
        f"Original source cutout HTTP 503: **{result['n_mask_science_remote_http503']}**.",
        "",
        "| Original field | Science MJD | Center model sanity pass | Original source mask+science requests | Completed original-pixel fits |",
        "|---|---:|---|---:|---:|",
    ]
    for e in result["historical_exposures"]:
        checks=[s["original_science_mask_psf_result"] for s in e["source_psf_pixel_residual_checks"]]
        lines.append(
            f"| {e['target_field']} | {e['original_science_mjd_assumed_utc']:.6f} | "
            f"{e['original_center_fits_check']['status']} | {len(checks)} | "
            f"{sum(bool(s.get('local_masked_psf_model_fit_completed')) for s in checks)} |")
    lines+=["","## Scientific limits","",
        "- Pixel PSF fitting uses real native original source-pixel DN and WCS-registered detector bad-pixel masks, but is NOT absolute flux calibration, physical source identification or independent star-based PSF/WCS validation.",
        "- All fitted pixels and withheld checkerboard pixels are the **same source image**; checkerboard validation probes local overfitting/scene mismatch but does not establish an independent instrument error budget.",
        "- A source lacking an original valid bitmask, saturated core, usable background, native-versus-WCS subpixel phase agreement or a good residual screen is marked as incomplete/review; not astrophysically absent.",
        "- CIDA 11 Gaia DR3 RUWE and unknown source blending/nebular gradients are unresolved. The official ZTF original science FITS units are DN (digital numbers), not calibrated magnitudes.",
        "- No raw FITS pixel cutouts/bitmasks, native PSF/DAOPhot arrays or Gaia/IRSA source tables are published.",
        "",
    ]
    m.write_text("\n".join(lines),encoding="utf8")
    return j,m


def main():
    p=argparse.ArgumentParser(description="Original ZTF masked science-pixel spatial PSF residual validation pilot")
    p.add_argument("original_irsa_zip",type=Path)
    p.add_argument("--seed",type=Path,default=SEED)
    p.add_argument("--ledger",type=Path,default=LEDGER)
    p.add_argument("--gaia-timeout",type=float,default=25)
    p.add_argument("--archive-timeout",type=float,default=6)
    p.add_argument("--output",type=Path,default=ROOT/"reports/generated/v1.16_original_masked_psf")
    p.add_argument("--require-some-real-pixel-fits",action="store_true")
    args=p.parse_args()
    r=run(args.original_irsa_zip,args.seed,args.ledger,
          gaia_timeout=args.gaia_timeout,archive_timeout=args.archive_timeout)
    paths=write_outputs(r,args.output)
    print(json.dumps({
        "attempted_original_source_pairs":r["n_candidate_source_pairs_original_science_and_mask_attempted"],
        "original_masked_psf_pixel_fits_completed":r["n_original_science_mask_psf_residual_fits_completed"],
        "provisional_same_image_residual_screens_passed":r["n_provisional_residual_profile_pixel_screens_passed"],
        "remote_503_source_pairs":r["n_mask_science_remote_http503"],
        "calibrated_psf_against_independent_stars":0,
        "confirmed_gaia_ztf_source_identities":0,
        "reports":[str(x) for x in paths],
    },indent=2))
    if args.require_some_real_pixel_fits and not r["n_original_science_mask_psf_residual_fits_completed"]:
        p.exit(2,"No original masked source pixels passed the complete fitting gates: this is missing instrumental validation, NOT sky non-detection.\n")


if __name__=="__main__":
    main()
