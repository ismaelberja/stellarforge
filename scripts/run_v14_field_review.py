"""Reproducible v1.4 independent Gaia-neighbour + ZTF image-link audit.

Consumes an official IRSA ZIP only in memory from a local, ignored path.
Never exports raw photometry or FITS pixels; conservative scientific flags.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from zipfile import ZipFile

from stellarforge.v13_observational_review import review_irsa_artifact
from stellarforge.v14_field_review import (
    audit_neighbours, fetch_gaia_csv, parse_gaia_csv,
    probe_ztf_image_header, selected_image_links,
)

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv"


def run(archive: Path, seed: Path, *, probe_images: bool = False) -> dict:
    previous = review_irsa_artifact(archive, seed)
    with Path(seed).open(encoding="utf-8-sig", newline="") as file:
        records = {r["gaia"]: r for r in csv.DictReader(file)}
    results = []
    with ZipFile(archive) as z:
        for result in previous["targets"]:
            sid = result["gaia_dr3_source_id"]
            source = records[sid]
            raw = z.read(f"{sid}_IRSA_RAW.csv")
            links = selected_image_links(
                raw, target_ra_deg=float(source["ra"]),
                target_dec_deg=float(source["dec"]),
                target_pmra=float(source["pmra"]),
                target_pmdec=float(source["pmdec"]),
            )
            gaia = None
            gaia_result = {
                "status": "QUERY_FAILED_NOT_A_NON_DETECTION",
                "target_gaia_source_verified": False,
                "image_blending_ruled_out": False,
            }
            try:
                gaia = fetch_gaia_csv(float(source["ra"]), float(source["dec"]))
                gaia_rows = parse_gaia_csv(gaia)
                gaia_result = audit_neighbours(
                    gaia_rows, target_id=sid,
                    ra_deg=float(source["ra"]), dec_deg=float(source["dec"]),
                    epoch_jyear=links["representative_gaia_screen_epoch_jyear"],
                )
                gaia_result["response_sha256"] = hashlib.sha256(gaia).hexdigest()
                gaia_result["tap_service"] = "Gaia DR3 ARI TAP, 15-arcsec ICRS cone"
                gaia_result["independent_gaia_query_completed"] = True
            except (HTTPError, URLError, TimeoutError, OSError, ValueError) as error:
                gaia_result["error_type"] = type(error).__name__
                if isinstance(error, HTTPError):
                    gaia_result["http_status"] = int(error.code)
                gaia_result["independent_gaia_query_completed"] = False
            # Probing image bytes is optional; never treat transport as review.
            if probe_images:
                for item in links["image_cutouts"]:
                    item["transport_probe"] = probe_ztf_image_header(item["image_cutout_url"])
                    if item["transport_probe"]["status"] != "FITS_HEADER_TRANSPORT_CONFIRMED":
                        item["reference_transport_probe"] = probe_ztf_image_header(
                            item["reference_cutout_url"])
            results.append({
                "target": result["target"],
                "gaia_dr3_source_id": sid,
                "gaia_neighbours": gaia_result,
                "ztf_image_review_links": links,
                "image_level_blending_review_complete": False,
                "scientific_source_identity_confirmed": False,
            })
    return {
        "schema_version": "stellarforge-v1.4-gaia-neighbors-and-image-provenance",
        "original_real_irsa_rows": previous["n_rows"],
        "original_ztf_oid_band_groups": previous["n_curves"],
        "n_targets": len(results),
        "gaia_queries_completed": sum(
            x["gaia_neighbours"].get("independent_gaia_query_completed", False)
            for x in results),
        "n_image_header_transport_verified": sum(
            item.get("transport_probe", {}).get("status") == "FITS_HEADER_TRANSPORT_CONFIRMED"
            or item.get("reference_transport_probe", {}).get("status")
            == "FITS_HEADER_TRANSPORT_CONFIRMED"
            for x in results
            for item in x["ztf_image_review_links"]["image_cutouts"]),
        "results": results,
        "n_astrophysical_identifications_confirmed": 0,
        "n_image_blends_ruled_out": 0,
        "next_gate": "Inspect actual ZTF FITS pixels and WCS alongside Gaia neighbours; "
                     "investigate PSF blending, image epochs and full astrometric covariance",
        "limitations": [
            "A Gaia-only cone search misses faint, red, unresolved and non-Gaia contaminants.",
            "Matching approximate 2D propagated positions does not prove unique identity.",
            "Only a FITS header is checked, not image pixels, WCS residuals, PSF or deblending.",
            "A missing Gaia response is a query failure, not absence of neighbours.",
            "No new astrophysical event, disk class, or measurement completeness is claimed.",
        ],
    }


def write_results(report: dict, output: Path) -> tuple[Path, Path]:
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    jf = output / "V14_GAIA_FIELD_AND_ZTF_IMAGE_AUDIT.json"
    jf.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
                  encoding="utf-8")
    lines = [
        "# StellarForge v1.4 — Gaia DR3 neighbouring sources and ZTF image access",
        "", "**NOT a final astrophysical source-identification or blend clearance.**",
        "", f"Official IRSA photometric rows previously validated: **{report['original_real_irsa_rows']}**.",
        f"Independent Gaia TAP cone queries completed: **{report['gaia_queries_completed']}/{report['n_targets']}**.",
        f"ZTF image groups with a science or reference FITS header verified: **{report['n_image_header_transport_verified']}**.",
        "",
        "| Target | Gaia query status | Gaia objects ≤2″ | ≤5″ | Nearest Gaia neighbour |",
        "|---|---|---:|---:|---|",
    ]
    for item in report["results"]:
        g = item["gaia_neighbours"]
        neighbours = g.get("nearby_sources") or []
        nearest = (
            f"{neighbours[0]['gaia_dr3_source_id']} "
            f"({neighbours[0]['separation_at_nominal_ztf_epoch_arcsec']}″)"
            if neighbours else "Not established")
        lines.append(
            f"| {item['target']} | {g['status']} | "
            f"{g.get('n_other_gaia_sources_within_2_arcsec', 'unknown')} | "
            f"{g.get('n_other_gaia_sources_within_5_arcsec', 'unknown')} | "
            f"{nearest} |")
    lines.extend([
        "", "## ZTF cutouts (links require independent image and WCS review)",
        "", "| Target | OID | Band | Field | FITS header status | Archive link |",
        "|---|---|---|---|---|---|---|",
    ])
    for item in report["results"]:
        for x in item["ztf_image_review_links"]["image_cutouts"]:
            lines.append(
                f"| {item['target']} | {x['oid']} | {x['band']} | {x['ztf_field']} | "
                f"{x.get('transport_probe', {}).get('status', 'NOT_PROBED')} | "
                f"{x.get('reference_transport_probe', {}).get('status', 'NOT_PROBED')} | "
                f"[Science]({x['image_cutout_url']}) · "
                f"[Reference]({x['reference_cutout_url']}) |")
    lines.extend([
        "", "## Scientific boundaries", "",
        "- The near-neighbour counts describe **Gaia-detected** objects only, not image-level cleanliness.",
        "- All ZTF links are selected using actual historic exposure IDs (median quality-masked MJD per OID).",
        "- FITS signature checks do **not** inspect image pixels, WCS, PSF or contamination.",
        "- Instrument-related ambiguity and unresolved contaminants remain possible.",
        "- **0 independently confirmed Gaia–ZTF identities; 0 physically classified events.**",
        "- Original third-party Luhman catalogue still requires comparison with the publisher file.",
        "",
    ])
    md = output / "V14_GAIA_FIELD_AND_ZTF_IMAGE_AUDIT.md"
    md.write_text("\n".join(lines), encoding="utf-8")
    return jf, md


def main() -> None:
    parser = argparse.ArgumentParser(description="Gaia neighbour and official ZTF FITS link audit")
    parser.add_argument("archive_zip", type=Path)
    parser.add_argument("--seed", type=Path, default=SEED)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "reports/generated/v1.4_fields")
    parser.add_argument("--probe-images", action="store_true",
                        help="Only verify remote FITS header, NOT inspect pixels")
    parser.add_argument("--require-gaia", action="store_true",
                        help="Exit nonzero if both independent Gaia cone audits are not valid")
    args = parser.parse_args()
    report = run(args.archive_zip, args.seed, probe_images=args.probe_images)
    outputs = write_results(report, args.output)
    print(json.dumps({
        "n_targets": report["n_targets"], "gaia_queries_completed": report["gaia_queries_completed"],
        "image_fits_headers_verified": report["n_image_header_transport_verified"],
        "n_confirmed_matches": report["n_astrophysical_identifications_confirmed"],
        "outputs": [str(f) for f in outputs],
    }, indent=2))
    if args.require_gaia and report["gaia_queries_completed"] < report["n_targets"]:
        parser.exit(2, "Gaia neighbour acquisition incomplete; no clean-field claim permitted.\n")


if __name__ == "__main__":
    main()
