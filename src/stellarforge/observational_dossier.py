"""Version 0.9: evidence-gated offline dossier for real Taurus catalogue targets.

Dossiers report only what has been observed and independently checked. Absence
of an IRSA response is NOT no sky coverage, and a local provenance file is NOT
proof of origin. Synthetic and third-party photometry never become Taurus data.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from html import escape
import hashlib
import json
import math
from pathlib import Path
from urllib.parse import urlsplit

from .epoch_evidence import per_epoch_association_evidence
from .luhman2023 import validate_technical_seed
from .ztf import BASE_URL, build_ztf_url
from .ztf_photometry import inspect_ztf_bytes


def _atomic_json(path: Path, obj: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".partial")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def _target(seed: Path, name: str) -> dict:
    validate_technical_seed(seed)
    with Path(seed).open(newline="", encoding="utf-8-sig") as h:
        matched = [row for row in csv.DictReader(h) if row["name"] == name]
    if len(matched) != 1:
        raise ValueError("Expected exactly one named target in approved technical seed")
    if matched[0]["reference"] != "Gaia":
        raise ValueError("Source coordinate reference is not Gaia")
    return matched[0]


def describe_payload_provenance(raw_path: Path) -> dict:
    """Inspect locally supplied file metadata, never promote to authenticated IRSA.

    A sidecar is user-writable and can only establish internal consistency.
    Official provenance needs acquisition log/network validation (future gate).
    """
    raw_path = Path(raw_path)
    raw = raw_path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if not raw:
        raise ValueError("Empty photometric response")
    sidecar = Path(str(raw_path) + ".provenance.json")
    if not sidecar.exists():
        status, meta = "LOCAL_FILE_WITHOUT_PROVENANCE", {}
    else:
        meta = json.loads(sidecar.read_text(encoding="utf-8"))
        if meta.get("sha256") != digest:
            raise ValueError("Photometric response SHA256 differs from sidecar")
        url = str(meta.get("url", ""))
        urlparts = urlsplit(url)
        official_url = (urlparts.scheme == "https" and
                        urlparts.netloc == "irsa.ipac.caltech.edu" and
                        urlparts.path == urlsplit(BASE_URL).path and bool(urlparts.query))
        status = ("IRSA_URL_CLAIM_WITH_INTEGRITY_CHECK_NOT_AUTHENTICATED"
                  if official_url else "NON_OFFICIAL_OR_UNATTRIBUTED_SOURCE")
    return {
        "status": status, "raw_sha256": digest, "raw_bytes": len(raw),
        "source_url_claim": str(meta.get("url", "")) if meta else None,
        "sidecar_present": sidecar.exists(),
        "sidecar_integrity_validated": bool(meta),
        "independently_authenticated_as_IRSA": False,
        "raw_is_authoritatively_associated_with_Taurus_star": False,
    }


def build_target_dossier(
    seed: Path, target_name: str, *, raw_path: Path | None = None,
    output: Path | None = None, radius_arcsec: float = 2.0,
    min_good_epochs: int = 30,
) -> dict:
    """Build a *preliminary* target evidence dossier, without physical labels.

    Missing file -> no observed data, never a negative scientific detection.
    If a raw file is provided, still requires manual validation of its target.
    """
    seed = Path(seed)
    r = _target(seed, target_name)
    if not math.isfinite(radius_arcsec) or not 0 < radius_arcsec <= 10:
        raise ValueError("Invalid pilot radius")
    if not isinstance(min_good_epochs, int) or min_good_epochs < 5:
        raise ValueError("Expected at least five epochs for provisional analysis")
    ra, dec = float(r["ra"]), float(r["dec"])
    source_id = str(r["gaia"])
    dossier = {
        "schema_version": "0.9.0",
        "target": target_name, "gaia_dr3_source_id": source_id,
        "kinematic_group": r["group"], "catalog_ra_deg": ra, "catalog_dec_deg": dec,
        "catalog_mirror_has_publisher_byte_comparison": False,
        "technical_seed_sha256": hashlib.sha256(seed.read_bytes()).hexdigest(),
        "official_query_url": build_ztf_url(ra, dec, radius_arcsec=radius_arcsec,
                                             bands=("g", "r"), output_format="csv"),
        "official_irsa_download_success": False,
        "IRSA_actual_coverage_known": False,
        "ztf_counterpart_confirmed": False,
        "physical_classification": None,
        "scientific_detection_count": None,
        "research_gates": {
            "publisher_source_bytes_verified": False,
            "official_IRSA_response_acquired_and_authenticated": False,
            "astrometry_independently_vetted": False,
            "field_controls_independently_vetted": False,
            "images_checked_for_blends": False,
            "period_or_event_verified_from_real_curve": False,
        },
    }
    if raw_path is None:
        dossier.update({
            "status": "OFFICIAL_IRSA_PHOTOMETRY_PENDING",
            "raw_photometry": None,
            "epoch_astrometry": None,
            "next_action": "Execute documented IRSA query when network is available; verify raw response and separate each OID/filter",
        })
    else:
        raw_path = Path(raw_path)
        provenance = describe_payload_provenance(raw_path)
        raw = raw_path.read_bytes()
        qc, points = inspect_ztf_bytes(raw, target_ra=ra, target_dec=dec,
                                       radius_arcsec=radius_arcsec,
                                       min_good_epochs=min_good_epochs)
        astrometry = per_epoch_association_evidence(
            points, gaia_id=source_id, ra_deg=ra, dec_deg=dec,
            pmra_star_mas_yr=float(r["pmra"]) if r["pmra"] else None,
            pmdec_mas_yr=float(r["pmdec"]) if r["pmdec"] else None,
            position_reference=r["reference"], radius_arcsec=radius_arcsec,
        )
        # No local payload may bypass manual source association and literature gates.
        if not points:
            status = "NO_USABLE_POINTS_IN_PROVIDED_RAW_RESPONSE"
        elif provenance["status"] != "IRSA_URL_CLAIM_WITH_INTEGRITY_CHECK_NOT_AUTHENTICATED":
            status = "LOCAL_PHOTOMETRY_NOT_AUTHENTICATED_AS_IRSA"
        elif astrometry["status"] == "ambiguous_multiple_oids_same_band":
            status = "AMBIGUOUS_MULTIPLE_OIDS_REQUIRE_MANUAL_REVIEW"
        elif max((c["good_epochs"] for c in qc["curves"]), default=0) < min_good_epochs:
            status = "INSUFFICIENT_EPOCHS_FOR_PRELIMINARY_ANALYSIS"
        else:
            status = "RAW_PRELIMINARY_QC_PASSED_IDENTITY_REVIEW_REQUIRED"
        dossier.update({
            "status": status,
            "raw_photometry": {
                "provenance": provenance,
                "raw_rows": qc["raw_rows"], "qc_accepted": qc["kept_rows"],
                "qc_rejected": qc["rejected_rows"], "rejected_reasons": qc["rejected_reasons"],
                "n_distinct_oids": len({p.oid for p in points}),
                "curve_summaries": qc["curves"],
            },
            "epoch_astrometry": astrometry,
            "next_action": "Verify official raw source and manually inspect ZTF images, crowding, OID uniqueness and field controls before any physical claim",
        })
    if output is not None:
        _atomic_json(Path(output), dossier)
    return dossier


def write_project_evidence_dashboard(dossiers: list[dict], output: Path) -> dict:
    """Create a static no-JavaScript HTML evidence dashboard, not a research result."""
    if not dossiers or len({d["gaia_dr3_source_id"] for d in dossiers}) != len(dossiers):
        raise ValueError("Unique targets required")
    generated = datetime.now(timezone.utc).isoformat()
    rows = []
    for d in dossiers:
        q = escape(d["official_query_url"], quote=True)
        name = escape(d["target"])
        rows.append(
            f"<tr><td><strong>{name}</strong><small>Gaia {escape(d['gaia_dr3_source_id'])}</small></td>"
            f"<td>{escape(d['kinematic_group'])}</td>"
            f"<td><span class='pending'>{escape(d['status'])}</span></td>"
            f"<td>{'—' if d['raw_photometry'] is None else d['raw_photometry']['qc_accepted']}</td>"
            f"<td><a href='{q}' rel='noopener noreferrer'>Official IRSA query</a></td></tr>"
        )
    style = """body{font-family:Inter,system-ui,sans-serif;background:#0d1629;color:#ecf3ff;margin:0}
    main{max-width:1120px;margin:auto;padding:38px 24px 70px}.eyebrow{text-transform:uppercase;letter-spacing:.17em;color:#7acbd1}
    h1{font-size:clamp(2rem,4vw,3.25rem);margin:12px 0}p{line-height:1.6;color:#b8c7da;max-width:880px}
    .metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin:28px 0}
    .metric{padding:22px;border-radius:12px;border:1px solid #36506e;background:#18253c}
    .metric b{display:block;font-size:2rem}.metric span{color:#b8c7da}
    table{width:100%;border-collapse:collapse;background:#162239;border:1px solid #36506e}
    th,td{padding:15px;text-align:left;border-bottom:1px solid #354963}th{color:#a8c4da;font-size:.85rem}
    td small{display:block;color:#9cb0c8;margin-top:5px}.pending{font-size:.78rem;color:#ffd28a;overflow-wrap:anywhere}
    a{color:#79d9db}footer{margin-top:25px;color:#93a8c4;font-size:.88rem}
    .banner{border-left:3px solid #ffbe60;padding:14px 22px;background:#252939;margin:24px 0}
    """
    page = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
    <title>StellarForge — Observational evidence dashboard v0.9</title><style>{style}</style></head><body><main>
    <div class='eyebrow'>StellarForge / Research Operations / 0.9</div><h1>Observational Evidence</h1>
    <p>Young stars in Taurus · Source association, real-data readiness and provenance · This dashboard reports evidence maturity, not newly discovered astronomy.</p>
    <div class='metrics'><div class='metric'><b>{len(dossiers)}</b><span>Catalogue targets in this pilot</span></div>
    <div class='metric'><b>{sum(d['raw_photometry'] is not None for d in dossiers)}</b><span>Raw files provided</span></div>
    <div class='metric'><b>0</b><span>Independently confirmed new astrophysical detections</span></div></div>
    <div class='banner'><strong>Data integrity notice:</strong> No official ZTF light curve is treated as acquired unless raw bytes are present. No positional coincidence is called an independently verified association. This is a research-readiness artifact.</div>
    <h2>Two-target pilot</h2><table><thead><tr><th>Target</th><th>Catalogue group</th><th>Evidence status</th><th>QC epochs</th><th>Next source</th></tr></thead><tbody>
    {''.join(rows)}</tbody></table><footer>Generated {escape(generated)} UTC · Luhman (2023) catalogue mirror unverified against publisher bytes · ZTF IRSA API URLs retained.</footer>
    </main></body></html>"""
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding="utf-8")
    return {"file": str(output), "targets": len(dossiers),
            "raw_file_count": sum(d["raw_photometry"] is not None for d in dossiers),
            "astrophysical_detections_claimed": 0}