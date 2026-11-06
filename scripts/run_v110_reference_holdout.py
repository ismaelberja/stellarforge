"""Reproducible reference held-out-disagreement report from public v1.8 aggregates.

No public network access, source acquisition, raw FITS bytes or original
Gaia/IRSA catalogue rows are required. All derived inputs and original JSON
SHA-256 provenance are kept under version control for future reproduction.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from stellarforge.v110_reference_holdout import load_and_audit

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/"data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json"


def write_outputs(report:dict, folder:Path) -> tuple[Path,Path]:
    folder.mkdir(parents=True,exist_ok=True)
    json_path=folder/"V110_REFERENCE_HOLDOUT_NO_RAW.json"
    md_path=folder/"V110_REFERENCE_HOLDOUT_NO_RAW.md"
    json_path.write_text(
        json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n",
        encoding="utf-8")
    lines=[
        "# StellarForge v1.10 — Real derived Gaia/ZTF reference holdout QA",
        "",
        "**This is an internal reference-sample disagreement audit, NOT an "
        "independently calibrated WCS/PSF, ZTF instrument uncertainty, or "
        "Gaia–ZTF astrophysical source match.**",
        "",
        "Source: v1.8 derived 13 reference-image model fits in 4 actual ZTF "
        "science exposures; original run https://github.com/ismaelberja/"
        "stellarforge/actions/runs/42077605987",
        "",
        f"Actual exposures evaluated: **{report['n_actual_science_exposures']}**.",
        f"Reference models in original archive: **{report['n_reference_fits_in_original_derived_evidence']}**.",
        f"Exposures with 3+ reference models (inclusive): **{report['n_exposures_with_loo_all_image_models']}**.",
        f"Exposures with 3+ clean model fits (strict): **{report['n_exposures_with_loo_strict_image_models']}**.",
        "",
        "| Target | MJD | All refs | Strict refs | Inclusive LOO RMS (arcsec) | Strict LOO RMS (arcsec) | Strict target offset reported? |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for e in report["exposures"]:
        l=e["all_model_statuses_loocv"]
        s=e["strict_model_status_loocv"]
        lnum=f"{l['loo_rms_radial_disagreement_arcsec']:.5f}" if "loo_rms_radial_disagreement_arcsec" in l else "insufficient"
        snum=f"{s['loo_rms_radial_disagreement_arcsec']:.5f}" if "loo_rms_radial_disagreement_arcsec" in s else "insufficient"
        reported="radial_arcsec" in e["strict_reference_subtracted_target_proxy"]
        lines.append(
            f"| {e['target']} | {e['mjd']:.6f} | {l['n_usable_reference_models']} | "
            f"{s['n_usable_reference_models']} | {lnum} | {snum} | {reported} |")
    lines.extend([
        "",
        "## Scientific interpretation and limitations",
        "",
        "- LOO predicts each **withheld** Gaia candidate's nominal WCS-referenced "
        "Gaussian centroid offset using the other candidates in the same "
        "original ZTF science product. It is independent of the held-out "
        "reference *within the fixed reference set*, but **not independent "
        "of shared image WCS systematics, catalogue selection or biases**.",
        "- A three-star LOO fold trains on just two stars. Its residual RMS "
        "is **not a calibrated astrometric 1σ error or confidence interval**.",
        "- A strict pass requires non-flagged image Gaussian fits, low "
        "residual proxy (<5), plausible shape and no edge-bound optimizer.",
        "- The original reference Gaia positions omitted annual parallax "
        "and formal full 5×5 covariance (v1.9 modeled these for TWO TARGET "
        "sources only). Do not silently interpret these offsets as "
        "v1.9-corrected reference measurements.",
        "- CIDA 11 target Gaia RUWE ≈8.57 means its physical positional "
        "uncertainty may far exceed its formal single-star catalogue error.",
        "- Zero proven isolated reference stars, zero instrument error "
        "budget, zero Gaia/ZTF physical identity confirmations and zero "
        "physical variability events established.",
        "",
    ])
    md_path.write_text("\n".join(lines),encoding="utf-8")
    return json_path,md_path


def main():
    parser=argparse.ArgumentParser(
        description="Offline v1.10 actual derived ZTF reference-image LOO validation")
    parser.add_argument("--input",type=Path,default=INPUT)
    parser.add_argument("--output",type=Path,
                        default=ROOT/"reports/generated/v1.10_reference_holdout")
    args=parser.parse_args()
    report=load_and_audit(args.input)
    paths=write_outputs(report,args.output)
    print(json.dumps({
        "n_exposures":report["n_actual_science_exposures"],
        "n_reference_models":report["n_reference_fits_in_original_derived_evidence"],
        "n_inclusive_holdout":report["n_exposures_with_loo_all_image_models"],
        "n_strict_holdout":report["n_exposures_with_loo_strict_image_models"],
        "n_calibrated_instrument_wcs_solutions":0,
        "outputs":[str(p) for p in paths],
    },indent=2))


if __name__=="__main__":
    main()
