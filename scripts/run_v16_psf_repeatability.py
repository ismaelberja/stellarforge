"""Real ZTF multi-exposure PSF-proxy and repeatability ledger.

Input: SHA-verified official IRSA photometric ZIP acquired previously.
Remote ZTF FITS files are never written to disk; only aggregate measurements
and failure statuses are exported. Physical source identity is NEVER inferred.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from zipfile import ZipFile

from stellarforge.v13_observational_review import review_irsa_artifact
from stellarforge.v15_image_pixels import propose_image_candidates
from stellarforge.v16_psf_repeatability import review_oid_band_psf

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv"


def run(artifact_zip: Path, seed_path: Path, *, timeout: float = 8.0) -> dict:
    original = review_irsa_artifact(artifact_zip, seed_path)
    with Path(seed_path).open(encoding="utf-8-sig", newline="") as handle:
        seed = {r["gaia"]: r for r in csv.DictReader(handle)}
    results = []
    with ZipFile(artifact_zip) as archive:
        for target in original["targets"]:
            gaia_id = target["gaia_dr3_source_id"]
            row = seed[gaia_id]
            raw = archive.read(f"{gaia_id}_IRSA_RAW.csv")
            groups = propose_image_candidates(
                raw, target_ra_deg=float(row["ra"]),
                target_dec_deg=float(row["dec"]),
                target_pmra=float(row["pmra"]),
                target_pmdec=float(row["pmdec"]),
                max_science_per_curve=3,
            )
            checked = [review_oid_band_psf(g, timeout=timeout) for g in groups]
            results.append({
                "target": target["target"],
                "gaia_dr3_source_id": gaia_id,
                "source_ztf_raw_sha256": target["raw_sha256"],
                "astrometric_quality_caution": (
                    "Gaia DR3 RUWE about 8.57, full astrometry not validated"
                    if gaia_id == "3419110734340795648"
                    else "Gaia position propagation omits covariance and parallax"
                ),
                "oid_band_review": checked,
                "confirmed_source_identity": False,
            })
    curves = [c for x in results for c in x["oid_band_review"]]
    attempts = [a for c in curves for a in c["attempts"]]
    fitted = [a for a in attempts if a.get("fit", {}).get("status") in (
        "PSF_PROXY_PROVISIONAL_ONLY", "PSF_PROXY_REVIEW_REQUIRED")]
    science = [a for a in fitted if a["kind"] == "science"]
    repeats = [c for c in curves
               if c["repeatability"]["n_independent_science_images"] >= 2]
    return {
        "schema_version": "stellarforge-v1.6-provisional-Gaussian-PSF-repeatability",
        "upstream_ztf_raw_rows": original["n_rows"],
        "n_targets": len(results),
        "n_oid_band_curves": len(curves),
        "n_ztf_image_requests_attempted": len(attempts),
        "n_valid_single_gaussian_proxy_images": len(fitted),
        "n_individual_science_images_fit": len(science),
        "n_reference_coadds_fit": len(fitted)-len(science),
        "n_curves_with_two_or_more_independent_science_fits": len(repeats),
        "n_fit_residual_or_shape_review_flags": sum(
            a["fit"]["status"] == "PSF_PROXY_REVIEW_REQUIRED" for a in fitted),
        "targets": results,
        "n_verified_gaia_ztf_astrophysical_matches": 0,
        "n_sources_shown_to_be_single_and_unblended": 0,
        "n_new_physical_events_confirmed": 0,
        "limitations": [
            "Axis-aligned elliptical Gaussian plus local linear background is a proxy, "
            "not a vetted empirical ZTF point spread function.",
            "WCS and 2D Gaia proper-motion propagation were not independently recalibrated; "
            "full parallax and covariance are excluded.",
            "Independent science images are compared only within the same ZTF OID/band; "
            "reference-image coadds are excluded from repeatability.",
            "Shape/residual flags are not evidence of an astrophysical companion.",
            "Lack of shape anomalies is not evidence of no blending.",
            "HTTP 503 and archive timeouts do not mean no observation was made.",
            "Original individual FITS and raw ZTF photometry remain outside Git.",
        ],
    }


def write_summary(data: dict, directory: Path) -> tuple[Path, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "V16_PSF_PROXY_AND_REPEATABILITY.json"
    md_path = directory / "V16_PSF_PROXY_AND_REPEATABILITY.md"
    json_path.write_text(json.dumps(data, indent=2, allow_nan=False,
                                    sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# StellarForge v1.6 — Real-image Gaussian profile proxy and repeatability",
        "", "**NOT validated ZTF PSF photometry or confirmed Gaia/ZTF source identities.**",
        "", f"SHA-checked ZTF cone-query rows: **{data['upstream_ztf_raw_rows']}**.",
        f"Images successfully fitted with a single Gaussian proxy: **{data['n_valid_single_gaussian_proxy_images']}**.",
        f"Individual science exposures: **{data['n_individual_science_images_fit']}**.",
        f"Reference coadd image fits: **{data['n_reference_coadds_fit']}**.",
        f"OID/band groups with at least 2 distinct fitted science images: **{data['n_curves_with_two_or_more_independent_science_fits']}**.",
        "",
        "| Target | OID | Filter | Science fits | Reference fits | Shape/residual flags | Independent science repeatability |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    for t in data["targets"]:
        for c in t["oid_band_review"]:
            fits = [a for a in c["attempts"] if a.get("fit", {}).get("status")
                    in ("PSF_PROXY_PROVISIONAL_ONLY", "PSF_PROXY_REVIEW_REQUIRED")]
            sci = sum(x["kind"] == "science" for x in fits)
            flags = sum(x["fit"]["status"] == "PSF_PROXY_REVIEW_REQUIRED"
                        for x in fits)
            lines.append(
                f"| {t['target']} | {c['ztf_oid']} | {c['band']} | "
                f"{sci} | {len(fits)-sci} | {flags} | "
                f"{c['repeatability']['status']} |")
    lines.extend([
        "", "## Scientific boundaries", "",
        "- Gaussian width, elongation, centroid offsets and positive residuals are "
        "**screening proxies**, not a full PSF or photometric calibration.",
        "- Coadded reference frames are excluded from independent science-epoch comparisons.",
        "- Repeatability is descriptive: zero-point/WCS/PSF systematics are not removed.",
        "- A high fit residual is not proof of a binary or other companion.",
        "- A low fit residual does not rule out unresolved blending or nebulosity.",
        "- CIDA 11's high Gaia RUWE requires full astrometric uncertainty review.",
        "- **Zero confirmed independent Gaia–ZTF identities, zero verified unblended stars, "
        "zero newly confirmed physical variability events.**",
        "",
    ])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Provisional real ZTF image PSF-proxy review")
    parser.add_argument("artifact_zip", type=Path)
    parser.add_argument("--seed", type=Path, default=SEED)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "reports/generated/v1.6_psf")
    parser.add_argument("--timeout", type=float, default=8.0)
    parser.add_argument("--fail-if-no-fit", action="store_true")
    args = parser.parse_args()
    result = run(args.artifact_zip, args.seed, timeout=args.timeout)
    outputs = write_summary(result, args.output)
    print(json.dumps({
        "images_with_provisional_gaussian_fit": result["n_valid_single_gaussian_proxy_images"],
        "science_exposures_fit": result["n_individual_science_images_fit"],
        "reference_coadds_fit": result["n_reference_coadds_fit"],
        "curves_with_repeatability_evidence": result["n_curves_with_two_or_more_independent_science_fits"],
        "verified_source_identifications": 0,
        "outputs": [str(o) for o in outputs],
    }, indent=2))
    if args.fail_if_no_fit and result["n_valid_single_gaussian_proxy_images"] == 0:
        parser.exit(2, "No usable real ZTF PSF proxy fit; not an astronomical non-detection.\n")


if __name__ == "__main__":
    main()
