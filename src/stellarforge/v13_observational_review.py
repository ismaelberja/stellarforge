"""Offline Gaia/ZTF positional review from a SHA-verified IRSA artifact ZIP.

All positional checks are *provisional*. Gaia DR3 mirror positions and proper
motions have no full covariance, parallax or image/blend assessment here.
No confirmed Gaia/ZTF identities, physical variability or disk classes.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import statistics
from urllib.parse import urlparse
from zipfile import ZipFile

from .epoch_evidence import per_epoch_association_evidence
from .luhman2023 import validate_technical_seed
from .ztf_photometry import inspect_ztf_bytes


def _load_seed(seed_path: Path) -> dict[str, dict]:
    validate_technical_seed(seed_path)
    with seed_path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    result = {str(row["gaia"]): row for row in rows}
    if len(result) != len(rows):
        raise ValueError("Duplicate Gaia source ID in technical seed")
    return result


def _read_raw_group_metadata(raw: bytes) -> dict:
    """Read instrument group IDs, never release individual epoch records."""
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    required = {"oid", "filtercode", "field", "ccdid", "qid"}
    if not reader.fieldnames or not required.issubset(reader.fieldnames):
        raise ValueError("Missing field/CCD/quadrant metadata")
    groups = defaultdict(lambda: {"rows": 0, "fields": set(), "ccds": set(), "quads": set()})
    for row in reader:
        oid = row["oid"]
        band = row["filtercode"].lower()
        if not oid.isdigit() or band not in ("zg", "zr", "zi"):
            raise ValueError("Unexpected ZTF OID or passband")
        entry = groups[(oid, band)]
        entry["rows"] += 1
        entry["fields"].add(row["field"])
        entry["ccds"].add(row["ccdid"])
        entry["quads"].add(row["qid"])
    return {
        (oid, band): {
            "n_raw_rows": group["rows"],
            "fields": sorted(group["fields"]),
            "ccds": sorted(group["ccds"]),
            "quads": sorted(group["quads"]),
        }
        for (oid, band), group in groups.items()
    }


def review_irsa_artifact(archive_path: Path, seed_path: Path,
                         *, radius_arcsec: float = 2.0) -> dict:
    """Verify external raw bytes, then run provisional per-epoch screen.

    The source ZIP remains private/local; this function emits only aggregate
    measurements and identifiers already present in the scientific audit.
    """
    seed = _load_seed(Path(seed_path))
    archive_path = Path(archive_path)
    results = []
    with ZipFile(archive_path) as archive:
        manifest = json.loads(archive.read("PILOT_STATUS.json"))
        entries = manifest.get("results")
        if not isinstance(entries, list) or not entries:
            raise ValueError("No target records in original acquisition manifest")
        seen_targets = set()
        for entry in entries:
            gaia_id = str(entry["gaia_dr3_id"])
            if not gaia_id.isdigit() or gaia_id not in seed or gaia_id in seen_targets:
                raise ValueError("Unknown or repeated Gaia target in artifact")
            seen_targets.add(gaia_id)
            target = seed[gaia_id]
            if target["reference"] != "Gaia" or target["name"] != entry["target"]:
                raise ValueError("Seed does not agree with artifact target identity")
            if entry.get("acquisition_status") != "RAW_HTTP_RESPONSE_SAVED_ASSOCIATION_UNVERIFIED":
                raise ValueError("Artifact target did not provide a raw response")
            url = urlparse(entry.get("official_url", ""))
            if url.scheme != "https" or url.hostname != "irsa.ipac.caltech.edu" or url.path != "/cgi-bin/ZTF/nph_light_curves":
                raise ValueError("Raw response is not attributed to the official IRSA API")
            # File names come only from validated Gaia IDs, not arbitrary ZIP paths.
            raw = archive.read(f"{gaia_id}_IRSA_RAW.csv")
            sha256 = hashlib.sha256(raw).hexdigest()
            if sha256 != entry.get("raw_sha256") or len(raw) != entry.get("raw_bytes"):
                raise ValueError(f"IRSA raw SHA-256 or size does not match: {gaia_id}")
            if abs(float(target["ra"]) - float(entry["catalog_ra_deg"])) > 1e-8 or abs(
                float(target["dec"]) - float(entry["catalog_dec_deg"])
            ) > 1e-8:
                raise ValueError("Catalog position has changed since acquisition")
            stat, points = inspect_ztf_bytes(
                raw, target_ra=float(target["ra"]), target_dec=float(target["dec"]),
                radius_arcsec=radius_arcsec, min_good_epochs=3,
            )
            if stat["raw_rows"] != entry["inspection"]["rows"]:
                raise ValueError("Acquisition manifest row count mismatch")
            group_metadata = _read_raw_group_metadata(raw)
            evidence = per_epoch_association_evidence(
                points, gaia_id=gaia_id,
                ra_deg=float(target["ra"]), dec_deg=float(target["dec"]),
                pmra_star_mas_yr=float(target["pmra"]) if target["pmra"] else None,
                pmdec_mas_yr=float(target["pmdec"]) if target["pmdec"] else None,
                position_reference=target["reference"], radius_arcsec=radius_arcsec,
                min_positioned_epochs=3,
            )
            curves = []
            for curve in evidence["curves"]:
                key = (curve["oid"], "z" + curve["band"])
                if key not in group_metadata:
                    raise ValueError("Missing ZTF field metadata for an accepted curve")
                g = group_metadata[key]
                curves.append({
                    **curve,
                    "ztf_fields": g["fields"],
                    "ztf_ccds": g["ccds"],
                    "ztf_quadrants": g["quads"],
                    "n_raw_rows_for_oid_band": g["n_raw_rows"],
                    "unique_field_per_oid_band": len(g["fields"]) == 1,
                })
            candidate_count = Counter(c["band"] for c in curves)
            multiple_oid_bands = sorted(k for k, count in candidate_count.items() if count > 1)
            results.append({
                "target": entry["target"], "gaia_dr3_source_id": gaia_id,
                "raw_sha256": sha256, "official_query": entry["official_url"],
                "n_raw_rows": stat["raw_rows"], "n_accepted_epochs": stat["kept_rows"],
                "n_rejected_epochs": stat["rejected_rows"],
                "rejection_reasons": stat["rejected_reasons"],
                "n_oid_band_curves": len(curves),
                "multiple_oid_bands": multiple_oid_bands,
                "status": evidence["status"],
                "curves": curves,
                "gaia_position_epoch": "J2016.0",
                "astrometry_method": evidence["method"],
                "gaia_ztf_identity_verified": False,
                "imaging_and_blend_review_complete": False,
                "scientific_variability_confirmed": False,
            })
    return {
        "schema_version": "stellarforge-v1.3-provisional-astrometry",
        "source": "SHA256_CHECKED_OFFICIAL_IRSA_CONE_QUERY",
        "catalog": "Luhman 2023 pinned third-party mirror; publisher check pending",
        "seed_sha256": hashlib.sha256(Path(seed_path).read_bytes()).hexdigest(),
        "radius_arcsec": radius_arcsec,
        "n_targets": len(results),
        "n_rows": sum(x["n_raw_rows"] for x in results),
        "n_qc_accepted": sum(x["n_accepted_epochs"] for x in results),
        "n_curves": sum(x["n_oid_band_curves"] for x in results),
        "targets": results,
        "gaia_ztf_identity_confirmations": 0,
        "physical_event_confirmations": 0,
        "limitations": [
            "2D proper-motion propagation only; no Gaia covariance, parallax or perspective.",
            "ZTF row positions may be correlated or pipeline-derived, not independent source matches.",
            "Multiple field-specific ZTF OIDs can represent the same astronomical object.",
            "Image-cutout assessment and query of alternative Gaia neighbours are not included.",
            "No physical dipper/burster, period, disk-class or variability discovery is claimed.",
        ],
    }


def write_provisional_review(report: dict, output_dir: Path) -> tuple[Path, Path]:
    """Save aggregate JSON and Markdown; never write the original CSV bytes."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    j = output_dir / "V13_PROVISIONAL_GAIA_ZTF_ASTROMETRY.json"
    j.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    lines = [
        "# v1.3 — Provisional Gaia/ZTF positional consistency (NOT cross-matched)",
        "",
        "Official IRSA cone-query bytes checked against source SHA-256. "
        "Gaia J2016.0 positions are propagated using **2D proper motion only**. "
        "Every resulting positional consistency check is **provisional**.",
        "",
        "| Target | ZTF OID | Filter | Field | QC epochs | Median sep (arcsec) | P95 sep (arcsec) | Status |",
        "|---|---|---|---|---:|---:|---:|---|",
    ]
    for t in report["targets"]:
        for c in t["curves"]:
            med = c.get("median_epoch_corrected_separation_arcsec")
            p95 = c.get("p95_epoch_corrected_separation_arcsec")
            lines.append(
                f'| {t["target"]} | {c["oid"]} | {c["band"]} | '
                f'{",".join(c["ztf_fields"])} | {c["n_qc_accepted_epochs"]} | '
                f'{med if med is not None else "n/a"} | '
                f'{p95 if p95 is not None else "n/a"} | {c["status"]} |'
            )
    lines.extend([
        "", "## Explicit scientific boundaries", "",
        "- **Zero verified Gaia–ZTF source identities**, zero new physical events.",
        "- Similar positions do not eliminate blending, catalog contamination or ambiguities.",
        "- FT Tau may be sampled in multiple fields; OIDs must remain separated.",
        "- Full Gaia uncertainties, image checks and neighbour queries are still required.",
        "- These are descriptive per-row separations, **not a posterior probability** of identity.",
        "- Raw CSVs remain outside this repository; only aggregate results are exported.",
        "",
    ])
    md = output_dir / "V13_PROVISIONAL_GAIA_ZTF_ASTROMETRY.md"
    md.write_text("\n".join(lines), encoding="utf-8")
    return j, md
