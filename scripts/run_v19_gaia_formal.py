"""Public Gaia DR3 5D formal-covariance and geocentric-parallax audit.

No raw Gaia TAP CSV or third-party ZTF FITS is written to Git. Two exact Gaia
DR3 source IDs, and a very small set of documented real ZTF observation MJDs
from the v1.8 report, are used for an astrometric uncertainty *pilot* only.
ZTF astrometric source identities and instrumental errors remain unverified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from stellarforge.v19_gaia_covariance import (
    fetch_gaia_astrometry, make_target_astrometry_adql,
    parse_gaia_astrometry, propagate_gaia_5p_formal,
)

ROOT=Path(__file__).resolve().parents[1]
TARGET_EPOCHS={
    "149623711269425408":{
        "name":"FT Tau positional pilot",
        "mjd_utc_assumed":[58388.389016,58491.184780],
    },
    "3419110734340795648":{
        "name":"CIDA 11 positional pilot",
        "mjd_utc_assumed":[58475.113750,58849.135984],
    },
}


def run(*,timeout:float=25.0) -> dict:
    source_ids=tuple(TARGET_EPOCHS)
    # Validate exact source-ID selection before external access.
    adql=make_target_astrometry_adql(source_ids)
    raw=fetch_gaia_astrometry(source_ids,timeout_sec=timeout)
    entries=parse_gaia_astrometry(raw,expected_ids=source_ids)
    targets=[]
    for sid,context in TARGET_EPOCHS.items():
        row=entries[sid]
        estimates=[]
        for mjd in context["mjd_utc_assumed"]:
            estimates.append(propagate_gaia_5p_formal(row,mjd_utc=mjd))
        targets.append({
            "target_name":context["name"],
            "gaia_dr3_source_id":sid,
            "gaia_reference_epoch_jyear":row["ref_epoch"],
            "gaia_ruwe":row["ruwe"],
            "gaia_parallax_mas":row["parallax"],
            "gaia_pmra_star_mas_per_year":row["pmra"],
            "gaia_pmdec_mas_per_year":row["pmdec"],
            "astrometric_model_solved_parameters":row["astrometric_params_solved"],
            "formal_5p_uncertainty_and_geocentric_parallax_epochs":estimates,
            "source_identity_with_ZTF_verified":False,
            "ZTF_WCS_or_PSF_calibrated":False,
        })
    return {
        "schema_version":"stellarforge-v1.9-formal-Gaia-5x5-parallax-pilot",
        "source_service":"Gaia DR3 gaiadr3.gaia_source via ARI TAP sync",
        "query_sha256":hashlib.sha256(adql.encode("utf-8")).hexdigest(),
        "raw_gaia_response_sha256":hashlib.sha256(raw).hexdigest(),
        "n_requested_exact_Gaia_ids":len(source_ids),
        "n_Gaia_ids_with_complete_formal_covariance":len(entries),
        "n_ztf_epoch_times_evaluated":sum(len(t["formal_5p_uncertainty_and_geocentric_parallax_epochs"]) for t in targets),
        "time_convention_note":"Original ZTF observation MJDs provisionally treated as UTC; exact image time-scale metadata not independently cross-validated",
        "reference_frame":"Gaia DR3 ICRS J2016.0; geocentric parallax shift with Astropy builtin Earth barycentric ephemeris",
        "model_scope":"formal Gaia five-parameter covariance and first-order geometric annual parallax; NOT astronomical source confirmation",
        "targets":targets,
        "n_Gaia_ZTF_astrophysical_identities_confirmed":0,
        "n_independent_instrumental_WCS_solutions":0,
        "n_empirical_PSFs_calibrated":0,
        "n_new_physical_events_confirmed":0,
        "caveats":[
            "Gaia five-parameter catalogue formal covariance does NOT include ZTF WCS centroid errors, seeing, PSF, background or blending systematics.",
            "CIDA 11 high RUWE is a serious indication that Gaia's formal 5x5 covariance can understate actual astrometric-model uncertainty.",
            "Geometric annual parallax is first order with Earth-centre observer using built-in offline ephemeris; no aberration, atmospheric refraction, topocentric parallax or perspective RV motion.",
            "For Gaia six-parameter solutions, the extracted five-dimensional astrometric submatrix excludes pseudo-colour parameter itself.",
            "An original ZTF positional cone query is not an independent Gaia/ZTF source association.",
            "No raw Gaia TAP rows, ZTF FITS image pixels or third-party raw light curves are published.",
        ],
    }


def write_summary(result:dict,out:Path):
    out.mkdir(parents=True,exist_ok=True)
    pjson=out/"V19_GAIA_FORMAL_PARALLAX_NO_RAW.json"
    pmd=out/"V19_GAIA_FORMAL_PARALLAX_NO_RAW.md"
    pjson.write_text(json.dumps(result,indent=2,sort_keys=True,
                                allow_nan=False)+"\n",encoding="utf-8")
    lines=[
        "# StellarForge v1.9 — Actual Gaia DR3 formal 5D uncertainty and annual geometric parallax",
        "",
        "**Formal Gaia-only results: not validated Gaia/ZTF source identity and NOT an independently calibrated ZTF WCS.**",
        "",
        f"Exact Gaia DR3 IDs returned with complete 5-parameter covariance: **{result['n_Gaia_ids_with_complete_formal_covariance']}**.",
        f"Original ZTF observation times evaluated (provisionally UTC): **{result['n_ztf_epoch_times_evaluated']}**.",
        "",
        "| Source | MJD (assumed UTC) | Gaia RUWE | Parallax east (mas) | Parallax north (mas) | Gaia formal east sigma (mas) | Gaia formal north sigma (mas) |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for target in result["targets"]:
        for row in target["formal_5p_uncertainty_and_geocentric_parallax_epochs"]:
            lines.append(
                f"| {target['target_name']} | {row['mjd_observation_utc']:.6f} | "
                f"{target['gaia_ruwe']:.3f} | "
                f"{row['geocentric_annual_parallax_minus_linear_east_mas']:+.3f} | "
                f"{row['geocentric_annual_parallax_minus_linear_north_mas']:+.3f} | "
                f"{row['formal_gaia_east_sigma_mas']:.3f} | "
                f"{row['formal_gaia_north_sigma_mas']:.3f} |")
    lines.extend([
        "",
        "## Important interpretation",
        "",
        "- These are formal propagated **Gaia-only** five-parameter uncertainties and a first-order Earth-geocentric parallax shift, **not the error bars of an observed ZTF image centroid**.",
        "- CIDA 11's large Gaia RUWE requires a separate physical/astrometric model; formal uncertainties can be **severely underestimated** for a poor single-star solution.",
        "- The calculation excludes radial-velocity perspective motion, aberration, Earth observatory/topocentric geometry, instrument PSF/WCS and full ZTF time-scale verification.",
        "- Input field selection is based on known positional-cone Gaia IDs, not a verified crossmatch to a ZTF light curve.",
        "- No source identity, clean field, independent full WCS recalibration, period, companion or physical variability event is established.",
        "",
        "Full machine-readable Gaia 2D formal covariance matrices are kept in the aggregate JSON, not raw source catalogue data.",
        "",
    ])
    pmd.write_text("\n".join(lines),encoding="utf-8")
    return pjson,pmd


def main():
    p=argparse.ArgumentParser(description="One bounded public Gaia DR3 full-5p covariance and geometric parallax query")
    p.add_argument("--output",type=Path,default=ROOT/"reports/generated/v1.9_gaia_formal")
    p.add_argument("--timeout",type=float,default=25)
    args=p.parse_args()
    data=run(timeout=args.timeout)
    paths=write_summary(data,args.output)
    print(json.dumps({
        "n_gaia_targets":data["n_Gaia_ids_with_complete_formal_covariance"],
        "n_epoch_screens":data["n_ztf_epoch_times_evaluated"],
        "confirmed_source_matches":0,
        "output_files":[str(p) for p in paths],
    },indent=2))


if __name__=="__main__":
    main()
