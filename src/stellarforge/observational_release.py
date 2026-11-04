"""Traceable observational source audit; never manufactures Taurus detections.

This module can audit offline ZTF CSV files from independent sources. Direct
IRSA mode requires provenance generated during the official downloader step.
A secondary public example is *only* a parser integration test, not evidence
that the file matches the original IRSA release or a Taurus object.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

from .cadence import cadence_report
from .ztf_photometry import inspect_ztf_bytes, parse_ztf_table

API_PREFIX = "https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?"
SUPPORTED_ORIGINS = {"secondary_public_example", "direct_irsa"}


def inspect_observational_source(
    raw_file: Path, outdir: Path, *, origin: str, source_url: str,
    expected_sha256: str | None = None, min_good_epochs: int = 30,
    target_name: str | None = None, target_ra: float | None = None,
    target_dec: float | None = None,
    event_durations=(2.0, 5.0, 10.0, 20.0, 40.0),
) -> dict:
    if origin not in SUPPORTED_ORIGINS:
        raise ValueError("Unknown source origin; use secondary_public_example or direct_irsa")
    parsed = urlparse(source_url)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise ValueError("Expected a canonical HTTPS provenance URL")
    if not isinstance(min_good_epochs, int) or min_good_epochs < 1:
        raise ValueError("min_good_epochs must be positive integer")
    if (target_ra is None) != (target_dec is None):
        raise ValueError("Target RA and Dec must be supplied together")
    if origin == "secondary_public_example" and (target_name or target_ra is not None):
        raise ValueError("Secondary sample cannot be assigned to a science target")
    if origin == "direct_irsa" and not source_url.startswith(API_PREFIX):
        raise ValueError("Direct IRSA mode requires official IRSA lightcurve URL")
    if target_name is not None and origin != "direct_irsa":
        raise ValueError("Source association cannot be claimed from third party data")
    raw_file = Path(raw_file)
    if raw_file.stat().st_size > 25_000_000:
        raise ValueError("Observation file is larger than audited parser's bound")
    raw = raw_file.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None and sha != expected_sha256:
        raise ValueError("Input SHA-256 does not match the pinned observational record")
    sidecar = Path(str(raw_file) + ".provenance.json")
    if origin == "direct_irsa":
        if not sidecar.exists():
            raise ValueError("Direct IRSA input requires official downloader provenance JSON")
        meta = json.loads(sidecar.read_text(encoding="utf-8"))
        if meta.get("sha256") != sha or meta.get("url") != source_url:
            raise ValueError("IRSA provenance hash or URL mismatch")
    audit, points = inspect_ztf_bytes(
        raw, target_ra=target_ra, target_dec=target_dec, min_good_epochs=min_good_epochs,
    )
    groups = defaultdict(list)
    for point in points:
        groups[(point.oid, point.band, point.time_scale)].append(point)
    samples = []
    for key, observed in sorted(groups.items()):
        stats = cadence_report([p.time_value for p in observed], durations_days=event_durations)
        n = len(observed)
        samples.append({
            "oid": key[0], "filter": key[1], "time_column": key[2],
            "epochs": n, "mean_magnitude": sum(p.magnitude for p in observed)/n,
            "cadence": stats,
            "analysis_eligibility": "insufficient_epochs" if n < min_good_epochs else
                                    "eligible_for_provisional_diagnostics_only",
            "independent_source_association_reviewed": False,
        })
    report = {
        "version": "0.8", "generated_utc": datetime.now(timezone.utc).isoformat(),
        "input_raw_filename_not_redistributed": raw_file.name,
        "raw_sha256": sha, "source_url": source_url,
        "source_origin": origin,
        "irsa_byte_identity_independently_established": False,
        "source_validated_against_current_irsa_release": False,
        "target_name_unverified": target_name,
        "target_coordinates_provisional": [target_ra,target_dec] if target_ra is not None else None,
        "taurus_lightcurves_verified": 0,
        "data_are_synthetic": False,
        "measurements_are_secondary_if_origin_is_secondary_public_example": origin == "secondary_public_example",
        "raw_rows": audit["raw_rows"],
        "qc_accepted": audit["kept_rows"],
        "qc_rejected": audit["rejected_rows"],
        "rejections": audit["rejected_reasons"],
        "n_distinct_curves": audit.get("curve_count", 0),
        "audited_curves": audit.get("curves", []),
        "cadence_by_curve": samples,
        "physical_classification_issued": False,
        "discovery_claim": False,
        "status": ("secondary_format_integration_test_not_taurus" if origin == "secondary_public_example" else
                   "observations_ingested_crossmatch_not_yet_verified"),
        "blocked_research_gates": [
            "independently_verify_original_IRSA_bytes_and_data_release",
            "source_crossmatch_and_crowding_image_review",
            "independent_disk_labels",
            "real_cadence_injection_recovery_and_field_controls",
            "peer_reviewed_physical_interpretation",
        ],
    }
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    dest = outdir / "OBSERVATIONAL_AUDIT.json"
    dest.write_text(json.dumps(report, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    rows = ["# StellarForge v0.8 — observational integration gate", "",
            f"- **Source type:** `{origin}`", f"- **Input provenance:** {source_url}",
            f"- **Original input SHA256:** `{sha}`", "- **Taurus association verified:** **NO**",
            f"- **QC:** {audit['kept_rows']} accepted / {audit['raw_rows']} supplied observations",
            f"- **Rejection breakdown:** `{audit['rejected_reasons']}`",
            "- **Physics:** no dipper/burster classification, period, or candidate discovery.", "",
            "## Cadence geometrical diagnostic", "",
            "| OID | Band | Clock | Epochs | Gap days max. | Eligible for >=30 epoch analysis? |", "|---|---|---|---:|---:|---|",]
    for v in samples:
        gap=v['cadence']['max_gap_days']
        rows.append(f"| `{v['oid']}` | {v['filter']} | {v['time_column']} | {v['epochs']} | "
                    f"{gap:.2f}" if gap is not None else f"| `{v['oid']}` | {v['filter']} | {v['time_column']} | {v['epochs']} | n/a")
        rows[-1] += f" | {'no' if v['analysis_eligibility']=='insufficient_epochs' else 'provisional only'} |"
    rows += ["", "Cadence-only coverage measures the fraction of hypothetical uniform event-start windows containing at least two recorded epochs. It does **not** include photometric signal, noise, flags beyond QC, physical event rate or a measured detection completeness.",
             "", "**Provenance warning:** the third-party data file (when used) has not been independently matched byte-for-byte with the IRSA archive. The raw file is not redistributed."]
    (outdir / "REPORT.md").write_text("\n".join(rows)+"\n", encoding="utf-8")
    return report


def plot_observational_sample(raw_file: Path, out_file: Path, *, origin: str):
    """Chart raw & accepted quality points; never assign a physical class."""
    import matplotlib.pyplot as plt
    raw = Path(raw_file).read_bytes()
    _, points = inspect_ztf_bytes(raw, min_good_epochs=1)
    raw_rows,_ = parse_ztf_table(raw)
    fig, ax = plt.subplots(figsize=(10, 5.3))
    for (oid, band, scale) in sorted({(p.oid,p.band,p.time_scale) for p in points}):
        rows = sorted((p for p in points if (p.oid,p.band,p.time_scale)==(oid,band,scale)),
                      key=lambda p:p.time_value)
        ax.errorbar([p.time_value for p in rows], [p.magnitude for p in rows],
                    yerr=[p.magnitude_error for p in rows], fmt='o', capsize=2,
                    label=f'OID {oid}, {band} ({scale}), QC accepted')
    rejected=[r for r in raw_rows if (r.get('catflags','0').isdigit() and
                                     int(r.get('catflags','0')) & 32768)]
    for r in rejected:
        try:
            ax.scatter([float(r['mjd'])], [float(r['mag'])], marker='x', s=70,
                       label='cloud/moon flagged (bit 15)' if r is rejected[0] else None)
        except (ValueError,KeyError):
            pass
    ax.invert_yaxis()
    ax.set_xlabel('MJD (if available; otherwise separately preserved scale)')
    ax.set_ylabel('ZTF-reported magnitude')
    ax.grid(alpha=.2)
    ax.legend(fontsize=8)
    if origin == "secondary_public_example":
        ax.set_title('External ZTF-format sample — quality-control integration; NOT TAURUS')
        provenance_note='Public third-party source, original IRSA data release not independently verified; no physical classification'
    elif origin == "direct_irsa":
        ax.set_title('Official IRSA response — preliminary QC, source match UNVERIFIED')
        provenance_note='No confirmed Gaia/ZTF association; no physical classification'
    else:
        raise ValueError("Unknown observational origin")
    fig.text(.5,.015,provenance_note,ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.04,1,1))
    Path(out_file).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_file, dpi=155)
    plt.close(fig)