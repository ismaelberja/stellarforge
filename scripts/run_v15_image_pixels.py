"""v1.5: evidence-gated FITS pixel/WCS inspection using official ZTF data.

Local inputs are the original SHA-checked IRSA acquisition archive. Remote FITS
cutouts are handled solely in memory and never written to Git or uploaded as
artifacts. Output contains aggregate flags, hashes, and candidate peak offsets
only: these do not establish source identity or image cleanliness.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from zipfile import ZipFile

from stellarforge.v13_observational_review import review_irsa_artifact
from stellarforge.v15_image_pixels import (
    inspect_available_image_candidates, propose_image_candidates,
)

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv"


def run(archive_path: Path, seed_path: Path, *, timeout_sec: float = 8.0,
        attempts_per_curve: int = 4) -> dict:
    upstream = review_irsa_artifact(archive_path, seed_path)
    with Path(seed_path).open(newline="", encoding="utf-8-sig") as source:
        seed = {r["gaia"]: r for r in csv.DictReader(source)}
    targets = []
    with ZipFile(archive_path) as z:
        for item in upstream["targets"]:
            sid = item["gaia_dr3_source_id"]
            target = seed[sid]
            raw = z.read(f"{sid}_IRSA_RAW.csv")
            groups = propose_image_candidates(
                raw,
                target_ra_deg=float(target["ra"]),
                target_dec_deg=float(target["dec"]),
                target_pmra=float(target["pmra"]),
                target_pmdec=float(target["pmdec"]),
            )
            curves = inspect_available_image_candidates(
                groups, timeout=timeout_sec,
                max_attempts_per_curve=attempts_per_curve)
            targets.append({
                "target": item["target"],
                "gaia_dr3_source_id": sid,
                "raw_irsa_sha256": item["raw_sha256"],
                "gaia_astrometry_warning": (
                    "CIDA11_HIGH_RUWE_SOURCE_ID_REQUIRES_INDEPENDENT_REVIEW"
                    if sid == "3419110734340795648" else
                    "GAIA_FULL_COVARIANCE_STILL_UNVERIFIED"),
                "curves": curves,
                "astrophysical_source_identity_confirmed": False,
                "blending_ruled_out": False,
            })
    all_curves = [curve for t in targets for curve in t["curves"]]
    return {
        "schema_version": "stellarforge-v1.5-real-fits-pixels-wcs-provisional",
        "original_irsa_cone_rows": upstream["n_rows"],
        "n_targets": len(targets),
        "n_oid_band_curves": len(all_curves),
        "n_curves_with_valid_wcs_and_pixels": sum(
            c["status"] == "PIXEL_WCS_PROVISIONAL_SCREEN_COMPLETED"
            for c in all_curves),
        "n_curves_without_usable_image": sum(
            c["status"] == "NO_USABLE_FITS_PIXEL_SCREEN"
            for c in all_curves),
        "targets": targets,
        "confirmed_gaia_ztf_source_identifications": 0,
        "confirmed_unblended_fields": 0,
        "confirmed_astro_variability_events": 0,
        "limitations": [
            "The official IRSA acquisition was a positional cone, not an independently "
            "authenticated Gaia/ZTF crossmatch.",
            "Astrometric screening uses Gaia 2D proper motion only, no full covariance/parallax.",
            "Local maxima in pixel images are heuristic; they are not verified companions.",
            "PSF fitting, image deblending, background modeling, WCS recalibration and "
            "multi-exposure consensus remain incomplete.",
            "Representative single-exposure and reference coadd images may be unavailable "
            "or show non-Gaia contaminants.",
            "Any image access error is transport ambiguity, not absence of ZTF coverage.",
        ],
    }


def write_aggregate(report: dict, output_dir: Path) -> tuple[Path, Path]:
    folder = Path(output_dir)
    folder.mkdir(parents=True, exist_ok=True)
    output_json = folder / "V15_PIXEL_WCS_AUDIT_NO_RAW.json"
    output_json.write_text(json.dumps(report, indent=2, sort_keys=True,
                                      allow_nan=False) + "\n", encoding="utf-8")
    lines = [
        "# StellarForge v1.5 — Real ZTF FITS pixels and celestial WCS",
        "",
        "**Scientific identity and image cleanliness remain unverified.**",
        "",
        f"SHA-checked IRSA photometric rows: **{report['original_irsa_cone_rows']}**.",
        f"OID/passband groups: **{report['n_oid_band_curves']}**.",
        f"Groups with valid FITS pixels and celestial WCS analysed: **{report['n_curves_with_valid_wcs_and_pixels']}**.",
        "",
        "| Target | OID | Band | Image outcome | FITS attempts | Central local maximum | Additional maxima ≤12″ |",
        "|---|---|---|---|---:|---|---:|",
    ]
    for target in report["targets"]:
        for curve in target["curves"]:
            pix = curve["pixel_screen"] or {}
            lines.append(
                f"| {target['target']} | {curve['ztf_oid']} | {curve['band']} | "
                f"{curve['status']} | {len(curve['attempts'])} | "
                f"{pix.get('central_local_maximum_detected', 'n/a')} | "
                f"{pix.get('n_additional_local_maxima_within_12_arcsec', 'n/a')} |"
            )
    lines.extend([
        "",
        "## Read this conservatively",
        "",
        "- **A FITS image is now opened and its WCS evaluated where the archive responds**, "
        "but this does not authenticate its Gaia/ZTF source association.",
        "- A central local maximum is not a verified star; nearby local maxima may arise "
        "from PSF structure, noise, cosmic rays or nebulosity.",
        "- No source deblending, independent WCS recalibration, completeness or validated "
        "PSF model has been performed.",
        "- Missing files or HTTP 503 are recorded as transport failures, **not negative "
        "sky or contamination evidence**.",
        "- CIDA 11 has high Gaia RUWE in the independent v1.4 TAP audit and deserves "
        "separate astrometric scrutiny.",
        "- The report stores only derived aggregates and image SHA-256; raw FITS pixel "
        "matrices and original ZTF photometry are not uploaded.",
        "- **Confirmed Gaia/ZTF identities: 0. Confirmed astrophysical events: 0.**",
        "",
    ])
    output_md = folder / "V15_PIXEL_WCS_AUDIT_NO_RAW.md"
    output_md.write_text("\n".join(lines), encoding="utf-8")
    return output_json, output_md


def main() -> None:
    p = argparse.ArgumentParser(description="Science-gated actual ZTF FITS pixel and WCS review")
    p.add_argument("irsa_artifact_zip", type=Path)
    p.add_argument("--seed", type=Path, default=SEED)
    p.add_argument("--output", type=Path,
                   default=ROOT / "reports/generated/v1.5_image_pixels")
    p.add_argument("--timeout", type=float, default=8.0)
    p.add_argument("--attempts-per-curve", type=int, default=4)
    p.add_argument("--fail-if-none", action="store_true",
                   help="Exit nonzero if no real image could be analysed")
    a = p.parse_args()
    result = run(a.irsa_artifact_zip, a.seed, timeout_sec=a.timeout,
                 attempts_per_curve=a.attempts_per_curve)
    output = write_aggregate(result, a.output)
    print(json.dumps({
        "n_targets": result["n_targets"],
        "n_oid_band_curves": result["n_oid_band_curves"],
        "n_curves_with_real_pixel_wcs_checks": result["n_curves_with_valid_wcs_and_pixels"],
        "n_confirmed_astrophysical_identifications": 0,
        "aggregates": [str(x) for x in output],
    }, indent=2))
    if a.fail_if_none and result["n_curves_with_valid_wcs_and_pixels"] == 0:
        p.exit(2, "No real FITS image returned useful pixels+WCS. Not a non-detection.\n")


if __name__ == "__main__":
    main()
