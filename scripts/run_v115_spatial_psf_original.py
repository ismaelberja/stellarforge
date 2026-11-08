"""Original-data v1.15 native ZTF DAOPhot spatial PSF reconstruction pilot.

Reconstruct the PSF at native PSF-catalogue source x/y, and compare a
separately generated reconstruction at the detector center with the official
sciimgdaopsfcent.fits stamp. Source Gaia IDs remain provisional candidate
identities; original science/mask pixels are not refit. All source records,
DAOPhot lookup tables, FITS stamp bytes and Gaia TAP rows stay ephemeral.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError,URLError
from zipfile import ZipFile

from stellarforge.v13_observational_review import review_irsa_artifact
from stellarforge.v17_field_controls import stratified_ztf_image_candidates
from stellarforge.v19_gaia_covariance import (
    fetch_gaia_astrometry,parse_gaia_astrometry,propagate_gaia_5p_formal,
)
from stellarforge.v111_reference_parallax import (
    all_required_gaia_ids,load_ledger,
)
from stellarforge.v113_official_masks_psf import (
    official_ancillary_url,fetch_ancillary_fits,
)
from stellarforge.v114_native_psfcat_association import (
    fetch_native_psf_product,official_psf_product_url,
    parse_psf_fit_catalogue,screen_psf_catalogue_targets,
)
from stellarforge.v115_spatial_psf import (
    parse_original_daophot_lookup,
    compare_reconstruction_to_official_center,
    summarize_evaluated_candidate_psfs,
)

ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/"data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv"
LEDGER=ROOT/"data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json"


def run(raw_zip:Path,seed:Path=SEED,ledger_file:Path=LEDGER,*,
        gaia_timeout:float=25,archive_timeout:float=12)->dict:
    if not (1<=gaia_timeout<=60 and 1<=archive_timeout<=25):
        raise ValueError("Unbounded source archive time limits")
    original=review_irsa_artifact(raw_zip,seed)
    ledger=load_ledger(ledger_file)
    ids=all_required_gaia_ids(ledger)
    raw_gaia=fetch_gaia_astrometry(ids,timeout_sec=gaia_timeout)
    gaia=parse_gaia_astrometry(raw_gaia,expected_ids=ids)
    with Path(seed).open(newline="",encoding="utf8") as f:
        seedrows={str(r["gaia"]):r for r in csv.DictReader(f)}
    if len(original["targets"])!=2 or len(ledger["exposures"])!=4:
        raise ValueError("Non-preregistered ZTF historical exposure count")
    if {r["gaia_dr3_source_id"] for r in original["targets"]}!={e["target_gaia_id"] for e in ledger["exposures"]}:
        raise ValueError("Original source and Gaia ledger targets differ")
    results=[]
    with ZipFile(raw_zip) as archive:
        for target in original["targets"]:
            sid=target["gaia_dr3_source_id"]
            seedrow=seedrows[sid]
            curves=stratified_ztf_image_candidates(
                archive.read(f"{sid}_IRSA_RAW.csv"),
                ra_deg=float(seedrow["ra"]),
                dec_deg=float(seedrow["dec"]),
                pmra_mas_yr=float(seedrow["pmra"]),
                pmdec_mas_yr=float(seedrow["pmdec"]),
                science_per_oid=6,cutout_arcsec=90)
            planned=[e for e in ledger["exposures"] if e["target_gaia_id"]==sid]
            if len(planned)!=2:
                raise ValueError("Expected two original science epochs per target")
            refids=sorted({x["id"] for e in planned for x in e["refs"]})
            if not 1<=len(refids)<=5:
                raise ValueError("Reference candidate count changed")
            for frame in planned:
                matches=[cand for curve in curves
                    if curve["ztf_oid"]==frame["oid"]
                    and curve["band"]==frame["band"]
                    for cand in curve["candidates"] if cand["kind"]=="science"
                    and cand["mjd"] is not None
                    and abs(cand["mjd"]-frame["mjd"])<.00002]
                if len(matches)!=1:
                    raise ValueError("Could not verify original historical science FITS ID")
                url=matches[0]["url"]
                pos=[]
                for gid in [sid]+refids:
                    ast=propagate_gaia_5p_formal(gaia[gid],mjd_utc=frame["mjd"])
                    pos.append({
                        "source_id":gid,
                        "geocentric_parallax_adjusted_ra_deg":
                            ast["geocentric_parallax_adjusted_ra_deg"],
                        "geocentric_parallax_adjusted_dec_deg":
                            ast["geocentric_parallax_adjusted_dec_deg"],
                    })
                cat={
                    "status":"ORIGINAL_ZTF_NATIVE_PSF_CATALOGUE_UNAVAILABLE",
                    "screens":[],
                }
                try:
                    raw_cat=fetch_native_psf_product(
                        official_psf_product_url(url,"psfcat.fits"),
                        kind="psfcat.fits",timeout=archive_timeout)
                    parsedcat=parse_psf_fit_catalogue(raw_cat)
                    cat=screen_psf_catalogue_targets(parsedcat,pos)
                    cat["status"]="ORIGINAL_PSF_CATALOGUE_SOURCE_SCREENS_AVAILABLE"
                    cat["native_psfcat_sha256"]=parsedcat["sha256"]
                    cat["n_native_psfcat_rows"]=parsedcat["n_native_psf_catalogue_rows"]
                except (HTTPError,URLError,TimeoutError,OSError,ValueError) as ex:
                    cat["error_type"]=type(ex).__name__
                    if isinstance(ex,HTTPError):cat["http_status"]=int(ex.code)
                center={"status":"ORIGINAL_ZTF_CENTER_PSF_FITS_UNAVAILABLE"}
                reconstructed={
                    "status":"ORIGINAL_SPATIAL_DAOPHOT_PSF_NOT_PARSED",
                    "n_evaluated_provisional_catalogue_candidate_psfs":0,
                }
                try:
                    raw_psf=fetch_native_psf_product(
                        official_psf_product_url(url,"sciimgdao.psf"),
                        kind="sciimgdao.psf",timeout=archive_timeout)
                    parsedpsf=parse_original_daophot_lookup(raw_psf)
                    center={"status":"ORIGINAL_ZTF_CENTER_PSF_FITS_UNAVAILABLE"}
                    try:
                        raw_center=fetch_ancillary_fits(
                            official_ancillary_url(url,"sciimgdaopsfcent.fits"),
                            kind="sciimgdaopsfcent.fits",timeout=archive_timeout)
                        center=compare_reconstruction_to_official_center(
                            parsedpsf,raw_center)
                    except (HTTPError,URLError,TimeoutError,OSError,ValueError) as exc:
                        center["error_type"]=type(exc).__name__
                        if isinstance(exc,HTTPError):center["http_status"]=int(exc.code)
                    reconstructed=summarize_evaluated_candidate_psfs(
                        parsedpsf,cat["screens"],center_check=center)
                    reconstructed.update({
                        "n_original_lookup_tables":parsedpsf["n_lookup_tables"],
                        "lookup_side_samples":parsedpsf["lookup_side_samples"],
                        "analytic_hwhm_x_pixels":round(parsedpsf["analytic_hwhm_x_pixels"],5),
                        "analytic_hwhm_y_pixels":round(parsedpsf["analytic_hwhm_y_pixels"],5),
                        "native_field_center_x":parsedpsf["detector_field_center_x"],
                        "native_field_center_y":parsedpsf["detector_field_center_y"],
                    })
                except (HTTPError,URLError,TimeoutError,OSError,ValueError) as exc:
                    reconstructed["error_type"]=type(exc).__name__
                    if isinstance(exc,HTTPError):
                        reconstructed["http_status"]=int(exc.code)
                results.append({
                    "target":frame["target"],
                    "gaia_target_id":sid,
                    "ztf_oid":frame["oid"],
                    "band":frame["band"],
                    "original_science_mjd_assumed_utc":float(frame["mjd"]),
                    "native_psfcat_candidate_screen":cat,
                    "native_center_fits_reconstruction_check":center,
                    "spatial_daophot_native_source_model_reconstruction":reconstructed,
                    "native_instrument_wcs_error_calibrated":False,
                    "physical_gaia_ztf_source_match_confirmed":False,
                })
    all_centre=[x["native_center_fits_reconstruction_check"] for x in results]
    all_model=[x["spatial_daophot_native_source_model_reconstruction"] for x in results]
    all_cat=[x["native_psfcat_candidate_screen"] for x in results]
    return {
        "schema_version":"stellarforge-v1.15-original-daophot-spatial-local-psf-approximate-reconstruction",
        "original_irsa_sha_checked_position_cone_rows":original["n_rows"],
        "original_v18_derived_reference_ledger_sha256":ledger["provenance"]["original_json_sha256"],
        "exact_gaia_dr3_five_parameter_source_ids":len(ids),
        "gaia_dr3_response_sha256":hashlib.sha256(raw_gaia).hexdigest(),
        "n_distinct_original_science_exposures":len(results),
        "n_original_native_daophot_spatial_psfs_decoded":sum(
            x["status"]=="ORIGINAL_NATIVE_SPATIAL_DAOPHOT_MODEL_EVALUATION_ATTEMPTED" for x in all_model),
        "n_official_field_center_psf_comparisons":sum(
            x["status"] in ("OFFICIAL_CENTER_PSF_APPROXIMATE_MODEL_AGREEMENT",
                            "OFFICIAL_CENTER_PSF_RECONSTRUCTION_DISAGREEMENT_REVIEW",
                            "NATIVE_CENTER_PSF_SHAPE_MISMATCH") for x in all_centre),
        "n_official_center_psf_model_agreements":sum(
            x["status"]=="OFFICIAL_CENTER_PSF_APPROXIMATE_MODEL_AGREEMENT" for x in all_centre),
        "n_original_psfcat_fits_tables_parsed":sum(
            x["status"]=="ORIGINAL_PSF_CATALOGUE_SOURCE_SCREENS_AVAILABLE" for x in all_cat),
        "n_gaia_ztf_positional_candidates_local_psf_shapes_evaluated":sum(
            x["n_evaluated_provisional_catalogue_candidate_psfs"] for x in all_model),
        "n_center_fits_http_503":sum(x.get("http_status")==503 for x in all_centre),
        "n_daophot_http_503":sum(x.get("http_status")==503 for x in all_model),
        "original_exposures":results,
        "n_local_psfs_independently_calibrated_on_original_sci_mask_pixels":0,
        "n_detector_wcs_solutions_heldout_calibrated":0,
        "n_authenticated_physical_gaia_ztf_source_matches":0,
        "n_new_confirmed_companions_or_variability_events":0,
        "limitations":[
            "These are approximate reconstructions of true original native ZTF spatial PSF lookup tables on catalogued detector x/y. Cubic B-spline interpolation approximates DAOPhot bicubic correction and is NOT known to exactly reproduce DAOPhot's native routine.",
            "Comparing model at CCD-field center against original center FITS validates only internal pipeline consistency, NOT an independently observed isolated empirical PSF or calibrated photometry.",
            "A source-local approximate PSF at a provisional Gaia-ZTF candidate position does not confirm physical source association, absence of blending, absolute telescope WCS accuracy or stellar flux variability.",
            "No matching original science and detector mask pixels are simultaneously fitted on held-out independent field stars; v1.13 original mask coverage was sparse.",
            "Gaia positions use formal Gaia 5D correlated covariance and first-order geocentric annual parallax, not topocentric apparent place, color/refraction/instrument systematics; CIDA 11 RUWE remains high.",
            "Original archival IRSA failures (including HTTP 503) are access failures, not astrophysical nondetections.",
            "Raw native DAOPhot coefficients, original center FITS pixels, ZTF PSFcat binary table rows and Gaia TAP CSV are kept out of public Git and workflow artifacts.",
        ],
    }


def write_reports(r:dict,out:Path):
    out.mkdir(parents=True,exist_ok=True)
    j=out/"V115_DAOPHOT_SPATIAL_PSF_CENTER_QA_NO_RAW.json"
    m=out/"V115_DAOPHOT_SPATIAL_PSF_CENTER_QA_NO_RAW.md"
    j.write_text(json.dumps(r,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf8")
    lines=[
        "# StellarForge v1.15 — Original spatial DAOPhot PSF model at actual CCD positions",
        "",
        "**This is a native PSF reconstruction/center-FITS model crosscheck, not a calibrated source-specific PSF or Gaia–ZTF astrophysical source identification.**",
        "",
        f"Original ZTF positional-query records SHA-verified: **{r['original_irsa_sha_checked_position_cone_rows']}**.",
        f"Original dated science exposures: **{r['n_distinct_original_science_exposures']}**.",
        f"Native full spatial DAOPhot files parsed: **{r['n_original_native_daophot_spatial_psfs_decoded']}**.",
        f"Original native center PSF stamps independently read & compared to reconstruction: **{r['n_official_field_center_psf_comparisons']}**.",
        f"Approximate reconstruction passes predefined center-model agreement: **{r['n_official_center_psf_model_agreements']}**.",
        f"Provisional catalogued candidate positions with approximate local PSF shapes evaluated: **{r['n_gaia_ztf_positional_candidates_local_psf_shapes_evaluated']}**.",
        "",
        "| Target field | Science MJD | Native DAOPhot source PSF parsed | Official center FITS agreement status | Local provisional candidate PSF shapes evaluated |",
        "|---|---:|---|---|---:|",
    ]
    for frame in r["original_exposures"]:
        d=frame["spatial_daophot_native_source_model_reconstruction"]
        c=frame["native_center_fits_reconstruction_check"]
        lines.append(
            f"| {frame['target']} | {frame['original_science_mjd_assumed_utc']:.6f} | "
            f"{d['status']} | {c['status']} | "
            f"{d['n_evaluated_provisional_catalogue_candidate_psfs']} |")
    lines.extend([
        "",
        "## Scientific limitations",
        "",
        "- Original ZTF DAOPhot spatially variable Gaussian+correction lookup data were read, but the reconstructed PSF uses an **approximate cubic-spline correction interpolation**, not a formally verified reproduction of DAOPhot interpolation.",
        "- The independent \`sciimgdaopsfcent.fits\` stamp comes from the **same** archival DAOPhot processing pipeline. Numerical agreement with it checks internal model/reconstruction fidelity, not independent instrument/astrophysical PSF accuracy.",
        "- Original PSF source coordinates are *native full CCD-quadrant* \`xpos/ypos\`, never the 45″ cutout-local WCS pixel coordinates.",
        "- Source candidates selected from \`psfcat.fits\` via v1.14 conservative quality gates are **not** independently authenticated physical Gaia–ZTF matches.",
        "- PSF-source model shape and center-stamp agreement do **not** measure actual centroid errors, photometric calibration, nearby unresolved contaminants or source variability.",
        "- No full original \`sciimg.fits\`/ \`mskimg.fits\` pixel-residual validation or held-out source astrometric detector WCS solution has been completed. High CIDA 11 RUWE remains a concern.",
        "- Unavailable original IRSA PSF products are transport failures, NOT astronomical nondetections. Raw Gaia/PSF original files and image pixels have not been published.",
        "",
    ])
    m.write_text("\n".join(lines),encoding="utf8")
    return j,m


def main():
    p=argparse.ArgumentParser(description="Original ZTF native DAOPhot spatial PSF reconstruction and center FITS check")
    p.add_argument("original_irsa_zip",type=Path)
    p.add_argument("--seed",type=Path,default=SEED)
    p.add_argument("--ledger",type=Path,default=LEDGER)
    p.add_argument("--gaia-timeout",type=float,default=25)
    p.add_argument("--archive-timeout",type=float,default=12)
    p.add_argument("--output",type=Path,default=ROOT/"reports/generated/v1.15_spatial_psf")
    p.add_argument("--require-some-daophot",action="store_true")
    args=p.parse_args()
    r=run(args.original_irsa_zip,args.seed,args.ledger,
          gaia_timeout=args.gaia_timeout,archive_timeout=args.archive_timeout)
    paths=write_reports(r,args.output)
    print(json.dumps({
        "native_psfs_parsed":r["n_original_native_daophot_spatial_psfs_decoded"],
        "native_center_psf_comparisons":r["n_official_field_center_psf_comparisons"],
        "native_center_psf_agreements":r["n_official_center_psf_model_agreements"],
        "provisional_catalogued_local_psfs_evaluated":r["n_gaia_ztf_positional_candidates_local_psf_shapes_evaluated"],
        "calibrated_local_psfs":0,"authenticated_source_ids":0,
        "reports":[str(x) for x in paths],
    },indent=2))
    if args.require_some_daophot and not r["n_original_native_daophot_spatial_psfs_decoded"]:
        p.exit(2,"No original spatial DAOPhot lookup model retrieved/parsed. Archive failure, not astronomical non-detection.\n")


if __name__=="__main__":
    main()
