"""One-time live Gaia DR3-backed reference-candidate pilot on actual ZTF images.

Read original SHA-checked IRSA photometry ZIP from an authorized local artifact.
All Gaia CSVs and ZTF FITS pixels are handled in memory only. Publishes
aggregate target/reference status and position/shape proxies, not raw data.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from urllib.error import HTTPError, URLError
from zipfile import ZipFile

from stellarforge.v13_observational_review import review_irsa_artifact
from stellarforge.v15_image_pixels import fetch_fits_cutout
from stellarforge.v16_psf_repeatability import PSF_OK, fit_local_gaussian_proxy
from stellarforge.v17_field_controls import stratified_ztf_image_candidates
from stellarforge.v18_gaia_references import (
    download_reference_catalog, estimate_provisional_wcs_translation,
    parse_reference_catalog, screen_reference_on_exposure,
    select_gaia_reference_candidates, subtract_candidate_reference_translation,
)

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv"


def _target_fit(candidate: dict, *, timeout: float) -> dict:
    out = {
        "mjd": candidate["mjd"], "band": candidate["band"]
            if "band" in candidate else "from_group",
        "target_astrophysical_identity_confirmed": False,
    }
    try:
        raw = fetch_fits_cutout(candidate["url"], timeout=timeout)
        fit = fit_local_gaussian_proxy(
            raw,
            expected_ra_deg=candidate["expected_ra_deg"],
            expected_dec_deg=candidate["expected_dec_deg"],
            image_kind="science",
        )
        out["status"] = fit["status"]
        if fit["status"] in PSF_OK:
            out["fits_sha256"] = fit["fits_sha256"]
            out["gaussian_proxy_fwhm_x_arcsec"] = fit["fitted_fwhm_x_arcsec"]
            out["gaussian_proxy_fwhm_y_arcsec"] = fit["fitted_fwhm_y_arcsec"]
            out["east_wcs_minus_gaia_arcsec"] = (
                fit["fitted_centroid_east_minus_Gaia_arcsec"])
            out["north_wcs_minus_gaia_arcsec"] = (
                fit["fitted_centroid_north_minus_Gaia_arcsec"])
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
        out["status"] = "TARGET_SCIENCE_FITS_OR_FIT_FAILED"
        out["error_type"] = type(exc).__name__
        if isinstance(exc, HTTPError):
            out["http_status"] = int(exc.code)
    return out


def run(archive_path: Path, seed_path: Path, *,
        gaia_timeout: float = 30, image_timeout: float = 6,
        max_references: int = 5, science_exposures_per_target: int = 2) -> dict:
    if not 1 <= max_references <= 5 or not 1 <= science_exposures_per_target <= 2:
        raise ValueError("Reference/exposure budget exceeded")
    if not 1 <= gaia_timeout <= 60 or not 1 <= image_timeout <= 20:
        raise ValueError("Invalid remote timeout")
    original = review_irsa_artifact(archive_path, seed_path)
    with Path(seed_path).open(encoding="utf-8-sig", newline="") as handle:
        seed = {r["gaia"]: r for r in csv.DictReader(handle)}
    targets = []
    with ZipFile(archive_path) as zip_file:
        for entry in original["targets"]:
            sid = entry["gaia_dr3_source_id"]
            catalog_seed = seed[sid]
            gaia = {
                "status": "INDEPENDENT_GAIA_DR3_QUERY_FAILED",
                "n_gaia_rows": None, "candidates": [],
                "reference_star_psf_calibrated": False,
            }
            try:
                gaia_csv = download_reference_catalog(
                    float(catalog_seed["ra"]), float(catalog_seed["dec"]),
                    timeout=gaia_timeout)
                rows = parse_reference_catalog(gaia_csv)
                gaia = select_gaia_reference_candidates(
                    rows, target_id=sid,
                    target_ra_deg=float(catalog_seed["ra"]),
                    target_dec_deg=float(catalog_seed["dec"]),
                    max_references=max_references)
                gaia["gaia_tap_csv_sha256"] = hashlib.sha256(gaia_csv).hexdigest()
                gaia["source_service"] = "Gaia DR3 (ARI TAP, 210-arcsec ICRS cone)"
            except (HTTPError, URLError, TimeoutError, OSError, ValueError,
                    UnicodeError) as exc:
                gaia["error_type"] = type(exc).__name__
                if isinstance(exc, HTTPError):
                    gaia["http_status"] = int(exc.code)

            photometry = zip_file.read(f"{sid}_IRSA_RAW.csv")
            groups = stratified_ztf_image_candidates(
                photometry,
                ra_deg=float(catalog_seed["ra"]),
                dec_deg=float(catalog_seed["dec"]),
                pmra_mas_yr=float(catalog_seed["pmra"]),
                pmdec_mas_yr=float(catalog_seed["pmdec"]),
                science_per_oid=6,
                cutout_arcsec=90,
            )
            # Deliberately small pilot: first g-band OID, two dated science
            # images; other OID/filter groups remain untested at this stage.
            g_groups = [g for g in groups if g["band"] == "zg"]
            chosen = g_groups[0] if g_groups else groups[0]
            observations = []
            for candidate in [r for r in chosen["candidates"]
                              if r["kind"] == "science"][:science_exposures_per_target]:
                target_fit = _target_fit(candidate, timeout=image_timeout)
                refs = []
                if target_fit["status"] in PSF_OK:
                    for item in gaia["candidates"]:
                        refs.append(screen_reference_on_exposure(
                            item, exposure_url=candidate["url"],
                            mjd=candidate["mjd"], timeout=image_timeout))
                correction = estimate_provisional_wcs_translation(refs)
                observations.append({
                    "science_mjd": candidate["mjd"],
                    "ztf_oid": chosen["ztf_oid"],
                    "ztf_band": chosen["band"],
                    "target_image_fit": target_fit,
                    "gaia_reference_image_attempts": refs,
                    "n_reference_attempts": len(refs),
                    "n_gaia_references_with_image_model": sum(
                        r.get("status") in PSF_OK for r in refs),
                    "provisional_wcs_translation": correction,
                    "target_after_provisional_reference_translation":
                        subtract_candidate_reference_translation(target_fit, correction),
                    "independently_wcs_calibrated": False,
                })
            targets.append({
                "target": entry["target"],
                "gaia_source_id": sid,
                "photometric_raw_sha256": entry["raw_sha256"],
                "gaia_wide_field_screen": gaia,
                "n_oid_band_groups_in_original_IRSA": len(groups),
                "oid_band_groups_image_screened_this_pilot": 1,
                "science_exposures": observations,
                "gaia_ztf_astrophysical_match_confirmed": False,
            })
    obs = [o for t in targets for o in t["science_exposures"]]
    refs = [ref for o in obs for ref in o["gaia_reference_image_attempts"]]
    return {
        "schema_version": "stellarforge-v1.8-gaia-reference-candidates-no-calibration",
        "original_ztf_raw_rows_sha_checked": original["n_rows"],
        "n_original_oid_band_groups": original["n_curves"],
        "n_targets": len(targets),
        "n_gaia_wide_field_queries_completed": sum(
            t["gaia_wide_field_screen"].get("status") ==
                "GAIA_DR3_QUALITY_SCREENED_REFERENCE_CANDIDATES"
            for t in targets),
        "n_catalogue_quality_reference_candidates_selected": sum(
            len(t["gaia_wide_field_screen"]["candidates"]) for t in targets),
        "n_science_target_image_attempts": len(obs),
        "n_target_fits_with_valid_gaussian_proxy": sum(
            o["target_image_fit"]["status"] in PSF_OK for o in obs),
        "n_reference_cutouts_attempted": len(refs),
        "n_gaia_reference_image_models": sum(
            r.get("status") in PSF_OK for r in refs),
        "n_exposures_with_provisional_translation_estimate": sum(
            o["provisional_wcs_translation"]["status"] ==
                "PROVISIONAL_LOCAL_WCS_TRANSLATION_ONLY" for o in obs),
        "targets": targets,
        "n_independently_validated_wcs_calibrations": 0,
        "n_authenticated_empirical_psf_models": 0,
        "n_confirmed_gaia_ztf_astrophysical_matches": 0,
        "n_confirmed_astrophysical_companions": 0,
        "limitations": [
            "Gaia DR3 astrometric quality and isolation screen does not prove a single or PSF-pure star.",
            "Each ZTF reference cutout uses the same dated science FITS file path as the target "
            "but a different sky center; this is not the same 90-arcsec pixel cutout.",
            "A local Gaussian shape proxy is not an empirically calibrated ZTF PSF.",
            "Gaia positions are propagated using only linear 2D proper motion "
            "without annual parallax/covariance/perspective.",
            "A median offset from three reference candidate stars is a provisional translation "
            "and does not independently recalibrate full FITS WCS.",
            "The pilot samples one OID/band per target and at most two original science dates; "
            "remaining original series are not independently calibrated.",
            "Missing Gaia or ZTF imagery is an access/provenance gap, never an empty sky.",
            "High Gaia RUWE for CIDA 11 makes its target astrometric fit especially uncertain.",
            "No source identity, blending exclusion, disk class or physical variability event is proven.",
        ],
    }


def write_summary(report: dict, output: Path) -> tuple[Path, Path]:
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    jpath = output / "V18_GAIA_REFERENCE_CANDIDATES_NO_RAW.json"
    mpath = output / "V18_GAIA_REFERENCE_CANDIDATES_NO_RAW.md"
    jpath.write_text(json.dumps(report, indent=2, sort_keys=True,
                                allow_nan=False)+"\n", encoding="utf-8")
    md = [
        "# StellarForge v1.8 — Gaia reference candidates and same-ZTF-exposure image checks",
        "",
        "**Catalogue-backed reference candidates are NOT yet authenticated PSF standards, "
        "and a translation proxy is NOT a calibrated instrumental WCS.**",
        "",
        f"Original SHA-verified ZTF cone photometry: **{report['original_ztf_raw_rows_sha_checked']}** rows.",
        f"Gaia wide-field queries with selected quality references: **{report['n_gaia_wide_field_queries_completed']}/{report['n_targets']}**.",
        f"Catalogue-screened Gaia reference candidates: **{report['n_catalogue_quality_reference_candidates_selected']}**.",
        f"Real science target FITS models: **{report['n_target_fits_with_valid_gaussian_proxy']}/{report['n_science_target_image_attempts']}**.",
        f"Same-dated science ZTF reference cutouts attempted: **{report['n_reference_cutouts_attempted']}**.",
        f"Gaia catalogued reference candidates with provisional image-model fits: **{report['n_gaia_reference_image_models']}**.",
        f"Exposures with at least three usable independent references and a *provisional* translation: **{report['n_exposures_with_provisional_translation_estimate']}**.",
        "",
        "| Target | Gaia-wide-field status | Gaia references | Science target images modeled | Reference images modeled | Provisional local translations |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for t in report["targets"]:
        obs = t["science_exposures"]
        md.append(
            f"| {t['target']} | {t['gaia_wide_field_screen']['status']} | "
            f"{len(t['gaia_wide_field_screen']['candidates'])} | "
            f"{sum(o['target_image_fit']['status'] in PSF_OK for o in obs)} | "
            f"{sum(o['n_gaia_references_with_image_model'] for o in obs)} | "
            f"{sum(o['provisional_wcs_translation']['status'] == 'PROVISIONAL_LOCAL_WCS_TRANSLATION_ONLY' for o in obs)} |"
        )
    md.extend([
        "", "## Scientific limitations", "",
        "- Only one g-band ZTF OID per target was sampled in this bounded pilot.",
        "- Gaia G photometry is not interchangeable with ZTF g/r response or color/PSF calibration.",
        "- Quality-filtered catalog entries and ZTF image peaks are candidate references, "
        "not proven single-star calibrators or deblended targets.",
        "- Positional predictions use approximate 2D Gaia proper motion, not "
        "parallax and full covariance.",
        "- Even three valid reference centroids only justify a *descriptive local "
        "WCS translation proxy*, not full independent WCS/PSF calibration.",
        "- Any IRSA or Gaia HTTP/timeouts are service failures, not sky non-detections.",
        "- **0 independent Gaia-ZTF physical matches, 0 calibrated empirical PSFs, "
        "0 astrophysical companions or events confirmed.**",
        "",
    ])
    mpath.write_text("\n".join(md), encoding="utf-8")
    return jpath, mpath


def main() -> None:
    parser = argparse.ArgumentParser(description="Gaia DR3 reference-candidate ZTF same-science-exposure pilot")
    parser.add_argument("original_irsa_archive_zip", type=Path)
    parser.add_argument("--seed", type=Path, default=SEED)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "reports/generated/v1.8_gaia_references")
    parser.add_argument("--max-references", type=int, default=5)
    parser.add_argument("--exposures-per-target", type=int, default=2)
    parser.add_argument("--image-timeout", type=float, default=6)
    parser.add_argument("--gaia-timeout", type=float, default=30)
    parser.add_argument("--require-catalog", action="store_true",
                        help="Exit nonzero if no independent Gaia wide-field query succeeds")
    args = parser.parse_args()
    output = run(args.original_irsa_archive_zip, args.seed,
                 gaia_timeout=args.gaia_timeout, image_timeout=args.image_timeout,
                 max_references=args.max_references,
                 science_exposures_per_target=args.exposures_per_target)
    paths = write_summary(output, args.output)
    print(json.dumps({
        "gaia_fields_with_references": output["n_gaia_wide_field_queries_completed"],
        "gaia_reference_candidates_selected": output["n_catalogue_quality_reference_candidates_selected"],
        "ztf_reference_image_models": output["n_gaia_reference_image_models"],
        "provisional_translations": output["n_exposures_with_provisional_translation_estimate"],
        "astrophysical_identities_confirmed": 0,
        "aggregates": [str(p) for p in paths],
    }, indent=2))
    if args.require_catalog and not output["n_gaia_wide_field_queries_completed"]:
        parser.exit(2, "Independent Gaia TAP query incomplete, not evidence of empty field.\n")


if __name__ == "__main__":
    main()
