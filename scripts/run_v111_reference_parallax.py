"""Real Gaia DR3 formal-astrometry sensitivity of archived ZTF reference offsets.

Official Gaia DR3 exact-ID query (8 refs + 2 pilot targets), not a cone scan.
Original derived image-fit ledger is SHA-checked and versioned; no raw Gaia
catalogue response, ZTF photometry or FITS image bytes are published.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from stellarforge.v19_gaia_covariance import fetch_gaia_astrometry
from stellarforge.v111_reference_parallax import (
    all_required_gaia_ids, load_ledger, run_from_bytes,
)

ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/"data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json"


def run(ledger_path:Path,timeout_sec:float=25) -> dict:
    ledger=load_ledger(ledger_path)
    ids=all_required_gaia_ids(ledger)
    raw=fetch_gaia_astrometry(ids,timeout_sec=timeout_sec)
    return run_from_bytes(ledger,raw)


def write_summary(report:dict,folder:Path) -> tuple[Path,Path]:
    folder.mkdir(parents=True,exist_ok=True)
    j=folder/"V111_REFERENCE_GAIA_PARALLAX_NO_RAW.json"
    m=folder/"V111_REFERENCE_GAIA_PARALLAX_NO_RAW.md"
    j.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n",
                 encoding="utf-8")
    lines=[
        "# StellarForge v1.11 — Gaia 5D formal/parallax sensitivity of real ZTF reference images",
        "",
        "**Actual Gaia DR3 exact-ID catalogue solutions; old real ZTF image-fit offsets.** "
        "No independent ZTF WCS or PSF calibration, no verified source identities.",
        "",
        f"Gaia source IDs with full 5D astrometry: **{report['n_gaia_dr3_exact_ids_with_complete_5p']}**.",
        f"Actual ZTF science exposures re-analyzed: **{report['n_real_science_exposures_reanalyzed']}**.",
        f"Original fitted reference-image models corrected: **{report['n_reference_image_models_reanalyzed']}**.",
        f"Strict reference LOO-eligible exposures: **{report['n_strict_loo_eligible_exposures']}**.",
        "",
        "| Target | MJD (assumed UTC) | Strict refs | Before LOO RMS (arcsec) | Parallax-aware LOO RMS (arcsec) | Difference (mas) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for e in report["exposures"]:
        old=e["original_strict_loo"].get("loo_rms_radial_disagreement_arcsec")
        new=e["parallax_aware_strict_loo"].get("loo_rms_radial_disagreement_arcsec")
        nold="insufficient" if old is None else f"{old:.6f}"
        nnew="insufficient" if new is None else f"{new:.6f}"
        d=e["strict_loo_rms_change_mas"]
        change="not evaluable" if d is None else f"{d:+.4f}"
        lines.append(
            f"| {e['target']} | {e['mjd_assumed_utc']:.6f} | "
            f"{e['n_strict_model_quality']} | {nold} | {nnew} | {change} |")
    lines.extend([
        "",
        "## Scientific interpretation",
        "",
        "- Each old Gaussian reference residual is corrected by **subtracting** "
        "that specific Gaia object's first-order Earth-geocentric annual parallax "
        "predicted displacement relative to linear proper motion. The original "
        "ZTF FITS image pixels and Gaussian fit are **NOT** remeasured.",
        "- For each original reference, all five Gaia DR3 astrometric formal errors "
        "and ten pairwise correlations are propagated to the matching MJD. "
        "They remain **Gaia-only formal source-position errors**.",
        "- A change in internal LOO disagreement does **not** demonstrate that "
        "ZTF instrumental image/WCS calibration, source matching or PSF improved.",
        "- Strict candidate quality selection, missing-reference failures, "
        "source multiplicity and CIDA 11 high Gaia RUWE remain unchanged.",
        "- Original observation MJD is provisionally interpreted as UTC. No "
        "telescope topocentre, aberration, instrument centroid errors, seeing, "
        "field-dependent PSF, verified Gaia–ZTF physical identification or "
        "stellar variability events are included.",
        "- Only derived JSON/Markdown aggregate quantities are published; no raw "
        "Gaia TAP CSV, original ZTF photometry or FITS pixel arrays.",
        "",
    ])
    m.write_text("\n".join(lines),encoding="utf-8")
    return j,m


def main():
    p=argparse.ArgumentParser(description="Gaia DR3 reference parallax/full-formal 5D uncertainty audit")
    p.add_argument("--ledger",type=Path,default=LEDGER)
    p.add_argument("--output",type=Path,
                   default=ROOT/"reports/generated/v1.11_reference_parallax")
    p.add_argument("--timeout",type=float,default=25)
    args=p.parse_args()
    result=run(args.ledger,timeout_sec=args.timeout)
    paths=write_summary(result,args.output)
    print(json.dumps({
        "gaia_sources":result["n_gaia_dr3_exact_ids_with_complete_5p"],
        "reference_models":result["n_reference_image_models_reanalyzed"],
        "strict_loo_exposures":result["n_strict_loo_eligible_exposures"],
        "instrument_wcs_calibrations":0,
        "paths":[str(x) for x in paths],
    },indent=2))


if __name__=="__main__":
    main()
