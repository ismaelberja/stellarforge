"""v1.7 real same-image shape-control and ZTF science-exposure recovery audit.

This takes the original SHA-validated IRSA cone-search ZIP. All FITS pixels,
original photometry and source cutouts remain ephemeral; the public output is
strictly aggregate and *never* certifies a Gaia-ZTF star, binary or clean PSF.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from zipfile import ZipFile

from stellarforge.v13_observational_review import review_irsa_artifact
from stellarforge.v17_field_controls import (
    inspect_curve_field_controls, stratified_ztf_image_candidates,
)

ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/"data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv"


def run(original_archive: Path, seed_path: Path, *,
        science_attempts: int = 6, timeout: float = 6.0) -> dict:
    if not 1<=science_attempts<=6 or not 1<=timeout<=25:
        raise ValueError("Archive request count or timeout out of bounds")
    verified=review_irsa_artifact(original_archive,seed_path)
    with seed_path.open(newline="",encoding="utf-8-sig") as h:
        seed={row["gaia"]:row for row in csv.DictReader(h)}
    targets=[]
    with ZipFile(original_archive) as archive:
        for row in verified["targets"]:
            source=seed[row["gaia_dr3_source_id"]]
            original=archive.read(f'{row["gaia_dr3_source_id"]}_IRSA_RAW.csv')
            candidate_groups=stratified_ztf_image_candidates(
                original,
                ra_deg=float(source["ra"]),dec_deg=float(source["dec"]),
                pmra_mas_yr=float(source["pmra"]),
                pmdec_mas_yr=float(source["pmdec"]),
                science_per_oid=science_attempts,
                cutout_arcsec=90.0,
            )
            audited=[inspect_curve_field_controls(
                group,science_attempts=science_attempts,
                timeout=timeout) for group in candidate_groups]
            targets.append({
                "target":row["target"],
                "gaia_dr3_source_id":row["gaia_dr3_source_id"],
                "official_irsa_sha256":row["raw_sha256"],
                "OID_band_groups":audited,
                "source_identity_confirmed":False,
            })
    curves=[curve for t in targets for curve in t["OID_band_groups"]]
    attempts=[r for c in curves for r in c["attempts"]]
    science=[r for r in attempts if r["kind"]=="science" and
             r.get("field_audit",{}).get("fits_sha256")]
    coadds=[r for r in attempts if r["kind"]=="reference_coadd" and
            r.get("field_audit",{}).get("fits_sha256")]
    with_controls=[r for r in science if r["field_audit"][
                   "n_usable_unclassified_controls"]>=2]
    repeated=[c for c in curves if c["science_repeatability_descriptive"]]
    return {
        "schema_version":"stellarforge-v1.7-unclassified-field-controls",
        "input_irsa_rows_SHA_checked":verified["n_rows"],
        "n_targets":len(targets),
        "n_oid_band_groups":len(curves),
        "n_image_access_attempts":len(attempts),
        "n_science_FITS_with_usable_radial_screen":len(science),
        "n_reference_coadds_with_radial_screen":len(coadds),
        "n_science_images_with_two_or_more_UNCLASSIFIED_field_peaks":
            len(with_controls),
        "n_curves_with_two_distinct_usable_science_exposures":len(repeated),
        "max_science_attempts_per_oid":science_attempts,
        "cutout_size_arcsec":90,
        "targets":targets,
        "validated_ZTF_Gaia_astrophysical_identifications":0,
        "confirmed_deblended_stars":0,
        "confirmed_stellar_companions":0,
        "new_physical_events_confirmed":0,
        "limitations":[
            "Image control candidates are brightness maxima, not catalogued stars.",
            "Same-image normalized ring profiles are descriptive shape proxies, "
            "not empirical calibrated PSFs or instrumental contamination models.",
            "No automatic deblending or rigorous flux/centroid uncertainty calibration.",
            "Repeated science-image centroids rely on original header WCS and "
            "approximate Gaia 2D proper-motion propagation (parallax/covariance omitted).",
            "Coadded references are not independent science exposures.",
            "Archive HTTP failures are not astrophysical non-detections.",
            "CIDA 11 Gaia RUWE about 8.57 requires independent astrometric caution.",
            "No Gaussian model residual is an astronomical companion detection.",
        ],
    }


def write_summary(result:dict, out:Path):
    out.mkdir(parents=True,exist_ok=True)
    j=out/"V17_FIELD_CONTROLS_AGGREGATE_NO_RAW.json"
    m=out/"V17_FIELD_CONTROLS_AGGREGATE_NO_RAW.md"
    j.write_text(json.dumps(result,indent=2,sort_keys=True,
                            allow_nan=False)+"\n",encoding="utf-8")
    lines=[
        "# StellarForge v1.7 — Same-image source-shape controls and science frame access",
        "",
        "**These are unclassified image peaks and provisional radial profiles, NOT "
        "validated stellar PSFs, Gaia/ZTF source identities or blending exclusions.**",
        "",
        f"Original official IRSA rows SHA-checked: **{result['input_irsa_rows_SHA_checked']}**.",
        f"Remote ZTF image requests: **{result['n_image_access_attempts']}**.",
        f"Individual science image radial screens: **{result['n_science_FITS_with_usable_radial_screen']}**.",
        f"Science screens with >=2 candidate same-image controls: **{result['n_science_images_with_two_or_more_UNCLASSIFIED_field_peaks']}**.",
        f"OID/band groups with >=2 different usable science frames: **{result['n_curves_with_two_distinct_usable_science_exposures']}**.",
        "",
        "| Query target | OID | Filter | Distinct science images | Science images with >=2 unclassified controls | Descriptive repeatability |",
        "|---|---|---|---:|---:|---|",
    ]
    for target in result["targets"]:
        for curve in target["OID_band_groups"]:
            lines.append(
                f"| {target['target']} | {curve['ztf_oid']} | {curve['band']} | "
                f"{curve['n_distinct_science_images_screened']} | "
                f"{curve['n_science_images_with_2plus_field_controls']} | "
                f"{curve['science_repeatability_descriptive']} |")
    lines.extend([
        "", "## Interpretation guardrails", "",
        "- Candidate controls are isolated **image intensity peaks**, never independently "
        "authenticated stars or a vetted instrument PSF. No magnitude calibration.",
        "- Radial profile fractions compare the target to local peaks with similar image "
        "conditions but **cannot rule out unresolved companions or extended emission**.",
        "- An absent control or valid image is a data-quality/access limitation, "
        "not proof of an empty sky field.",
        "- Multiple ZTF dated science exposures count independently only with distinct "
        "FITS SHA-256s and successful provisional checks. Reference coadds do not count.",
        "- Differences between fitted centroids are descriptive and include unmodeled "
        "Gaia parallax/covariance and FITS header WCS systematics.",
        "- **0 confirmed astrophysical crossmatches, 0 clean/unblended field guarantees, "
        "0 discovered companions, 0 physical variability events.**",
        "",
    ])
    m.write_text("\n".join(lines),encoding="utf-8")
    return j,m


def main():
    parser=argparse.ArgumentParser(description="Fail-closed ZTF field-control and repeatable-frame audit")
    parser.add_argument("original_irsa_zip",type=Path)
    parser.add_argument("--seed",type=Path,default=SEED)
    parser.add_argument("--output",type=Path,
                        default=ROOT/"reports/generated/v1.7_controls")
    parser.add_argument("--science-attempts",type=int,default=6)
    parser.add_argument("--timeout",type=float,default=6.0)
    parser.add_argument("--fail-if-no-science",action="store_true")
    args=parser.parse_args()
    report=run(args.original_irsa_zip,args.seed,
               science_attempts=args.science_attempts,timeout=args.timeout)
    paths=write_summary(report,args.output)
    print(json.dumps({
        "original_rows":report["input_irsa_rows_SHA_checked"],
        "science_frames_screened":report["n_science_FITS_with_usable_radial_screen"],
        "frames_with_unclassified_same_field_controls":
            report["n_science_images_with_two_or_more_UNCLASSIFIED_field_peaks"],
        "oid_bands_with_repeat_science_frames":
            report["n_curves_with_two_distinct_usable_science_exposures"],
        "confirmed_astro_matches":0,
        "report_paths":[str(x) for x in paths],
    },indent=2))
    if args.fail_if_no_science and report["n_science_FITS_with_usable_radial_screen"]==0:
        parser.exit(2,"Archive supplied no usable science cutouts: no non-detection implied.\n")


if __name__=="__main__":
    main()
