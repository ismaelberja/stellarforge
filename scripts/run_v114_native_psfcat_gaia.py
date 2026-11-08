"""Read-only native ZTF PSF catalogue and DAOPhot product pilot.

Historical same-four-dated-science-frame pilot, checked against original
manifested IRSA ZIP (2,212 position-cone entries) and v1.8 derived ledger.
This adds *catalogued* PSF detections/quality screens, not real local PSF
evaluation or a final Gaia-ZTF physical crossmatch.

Only aggregate source/quality flags, source count, error codes and FITS/file
hashes are released. Raw PSF catalog rows, DAOPhot model bytes and Gaia/IRSA
source records are not saved.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from stellarforge.v13_observational_review import review_irsa_artifact
from stellarforge.v17_field_controls import stratified_ztf_image_candidates
from stellarforge.v19_gaia_covariance import (
    fetch_gaia_astrometry,parse_gaia_astrometry,propagate_gaia_5p_formal,
)
from stellarforge.v111_reference_parallax import load_ledger,all_required_gaia_ids
from stellarforge.v114_native_psfcat_association import (
    audit_original_psf_catalogue,audit_original_spatial_psf,
)

ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/"data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv"
LEDGER=ROOT/"data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json"


def run(original_irsa_zip:Path,seed:Path=SEED,ledger_path:Path=LEDGER,*,
        gaia_timeout:float=25,archive_timeout:float=12)->dict:
    if not (1<=gaia_timeout<=60 and 1<=archive_timeout<=25):
        raise ValueError("Unbounded official archive timeouts")
    original=review_irsa_artifact(original_irsa_zip,seed)
    ledger=load_ledger(ledger_path)
    exact=all_required_gaia_ids(ledger)
    raw_gaia=fetch_gaia_astrometry(exact,timeout_sec=gaia_timeout)
    gaia=parse_gaia_astrometry(raw_gaia,expected_ids=exact)
    with Path(seed).open(newline="",encoding="utf-8") as handle:
        seed_rows={str(r["gaia"]):r for r in csv.DictReader(handle)}
    if len(original["targets"])!=2 or len(ledger["exposures"])!=4:
        raise ValueError("Wrong preregistered ZTF original science count")
    if ({t["gaia_dr3_source_id"] for t in original["targets"]} !=
        {e["target_gaia_id"] for e in ledger["exposures"]}):
        raise ValueError("Real ZTF original acquisition target IDs disagree")
    frames=[]
    with ZipFile(original_irsa_zip) as archive:
        for target in original["targets"]:
            targetid=target["gaia_dr3_source_id"]
            row=seed_rows[targetid]
            curves=stratified_ztf_image_candidates(
                archive.read(f"{targetid}_IRSA_RAW.csv"),
                ra_deg=float(row["ra"]),dec_deg=float(row["dec"]),
                pmra_mas_yr=float(row["pmra"]),
                pmdec_mas_yr=float(row["pmdec"]),
                science_per_oid=6,cutout_arcsec=90,
            )
            planned=[e for e in ledger["exposures"]
                     if e["target_gaia_id"]==targetid]
            if len(planned)!=2:
                raise ValueError("Missing two preregistered exposures per target")
            refs=sorted({r["id"] for e in planned for r in e["refs"]})
            if not 1<=len(refs)<=5:
                raise ValueError("Invalid reference source count")
            for e in planned:
                candidates=[r for c in curves if c["ztf_oid"]==e["oid"]
                            and c["band"]==e["band"]
                            for r in c["candidates"] if r["kind"]=="science"
                            and r["mjd"] is not None and abs(r["mjd"]-e["mjd"])<.00002]
                if len(candidates)!=1:
                    raise ValueError("Can't reconstruct exact original science exposure")
                science_url=candidates[0]["url"]
                mjd=float(e["mjd"])
                ids=[targetid]+refs
                predicted=[]
                for sid in ids:
                    astrometry=propagate_gaia_5p_formal(
                        gaia[sid],mjd_utc=mjd)
                    predicted.append({
                        "source_id":sid,
                        "geocentric_parallax_adjusted_ra_deg":astrometry[
                            "geocentric_parallax_adjusted_ra_deg"],
                        "geocentric_parallax_adjusted_dec_deg":astrometry[
                            "geocentric_parallax_adjusted_dec_deg"],
                    })
                psfcat=audit_original_psf_catalogue(
                    science_url,predicted,timeout=archive_timeout)
                dao=audit_original_spatial_psf(
                    science_url,timeout=archive_timeout)
                frames.append({
                    "target":e["target"],
                    "target_gaia_source_id":targetid,
                    "ztf_oid":e["oid"],
                    "band":e["band"],
                    "original_science_mjd_assumed_utc":mjd,
                    "n_gaia_candidate_predictions":len(predicted),
                    "native_psf_catalogue_candidate_screens":psfcat,
                    "native_spatial_daophot_file_provenance":dao,
                    "n_independent_astrophysical_gaia_ztf_source_identities":0,
                    "n_native_source_position_specific_psf_calibrations":0,
                })
    catalog=[e["native_psf_catalogue_candidate_screens"] for e in frames]
    dao=[e["native_spatial_daophot_file_provenance"] for e in frames]
    successes=[c for c in catalog
               if c["status"]=="ZTF_ORIGINAL_PSF_CATALOGUE_SCREEN_COMPLETED"]
    screens=[s for c in successes for s in c["screens"]]
    return {
        "schema_version":"stellarforge-v1.14-original-psf-fit-catalogue-and-daophot-source-review",
        "original_irsa_position_cone_rows_sha_verified":original["n_rows"],
        "original_v18_source_ledger_sha256":ledger["provenance"][
            "original_json_sha256"],
        "exact_gaia_dr3_formal_five_parameter_source_ids":len(exact),
        "gaia_raw_tap_response_sha256":hashlib.sha256(raw_gaia).hexdigest(),
        "n_actual_original_science_exposures":len(frames),
        "n_official_native_psfcat_products_requested":len(catalog),
        "n_official_native_psfcat_products_parsed":len(successes),
        "n_native_spatial_daophot_products_requested":len(dao),
        "n_native_spatial_daophot_files_downloaded":sum(
            x.get("status")=="NATIVE_DAOPHOT_SPATIAL_PSF_DOWNLOADED_FORMAT_NOT_EVALUATED"
            for x in dao),
        "n_gaia_predictions_in_original_four_exposures":sum(
            e["n_gaia_candidate_predictions"] for e in frames),
        "n_gaia_predictions_screened_against_native_psfcat":len(screens),
        "n_provisional_unique_nearest_psfcat_candidates":sum(
            c["n_provisional_unique_nearest_source_candidates"] for c in successes),
        "n_catalogue_psf_profile_or_flag_review_required":sum(
            s.get("status")=="NATIVE_PSF_FIT_PROFILE_OR_FLAG_REVIEW_REQUIRED" for s in screens),
        "n_catalogued_source_crowding_review":sum(
            s.get("status")=="MULTIPLE_NATIVE_PSF_SOURCES_WITHIN_CROWDING_RADIUS_REVIEW" for s in screens),
        "n_psfcat_503_errors":sum(x.get("http_status")==503 for x in catalog),
        "n_daophot_503_errors":sum(x.get("http_status")==503 for x in dao),
        "psfcat_outcomes":dict(sorted(Counter(x["status"] for x in catalog).items())),
        "daophot_outcomes":dict(sorted(Counter(x["status"] for x in dao).items())),
        "frames":frames,
        "n_confirmed_astrophysical_gaia_ztf_source_crossmatches":0,
        "n_evaluated_source_position_psfs":0,
        "n_independently_calibrated_detector_wcs_solutions":0,
        "n_new_confirmed_binaries_or_companions":0,
        "n_confirmed_physical_variability_events":0,
        "limitations":[
            "PSF-fit catalog nearest candidates at <=1 arcsec are only spatial candidates, NOT established Gaia-ZTF source identities. The source position is Gaia propagated with formal 5D covariance and geocentric annual parallax, not full telescope apparent place.",
            "Official native ZTF PSF chi/shape/flags and nearby sources are PSF catalogue fit quality screens, not an independent authentication of an unblended single star.",
            "The sourceid in psfcat.fits is per-exposure sequential native catalogue counter, NOT Gaia source_id or multi-epoch ZTF oid.",
            "The native spatially varying sciimgdao.psf file was not decoded/evaluated as a PSF at an individual source detector coordinate. This needs verified DAOPhot format and calibrated comparison.",
            "Catalogue matches use native PSF-fit RA/Dec as published and are not a held-out absolute detector WCS reconstruction or calibrated astrometric uncertainty.",
            "The original independent ZTF 6141 source mask screen was available for only four reference cutouts and zero original target cutouts in the earlier v1.13 pilot; catalog flags do not substitute for mask alignment.",
            "Original ZTF sky epoch metadata and the Gaia-to-ZTF physical match are still unverified; CIDA 11 target has large Gaia RUWE and potential non-single-star systematic position error.",
            "IRSA HTTP 503 is archive transport failure and does not imply a non-detection. The 4 science frames are historic original exposures, not a representative survey sample.",
            "All raw Gaia TAP CSV, original IRSA photometric tables, ZTF PSF FITS binary tables and native DAOPhot lookup data remain outside public Git and aggregate artifacts.",
        ],
    }


def write_outputs(r:dict,outdir:Path)->tuple[Path,Path]:
    outdir.mkdir(parents=True,exist_ok=True)
    j=outdir/"V114_NATIVE_PSF_CATALOGUE_GAIA_SCREEN_NO_RAW.json"
    m=outdir/"V114_NATIVE_PSF_CATALOGUE_GAIA_SCREEN_NO_RAW.md"
    j.write_text(json.dumps(r,indent=2,sort_keys=True,allow_nan=False)+"\n",
                 encoding="utf-8")
    lines=[
        "# StellarForge v1.14 — ZTF native PSF catalogue candidate cross-identification",
        "",
        "**Only source-candidate/quality screening; no authenticated Gaia–ZTF source, source-specific spatial PSF, validated instrument WCS, companion or physical variability.**",
        "",
        f"Original IRSA positional-query records SHA-audited: **{r['original_irsa_position_cone_rows_sha_verified']}**.",
        f"Original independent dated science exposures: **{r['n_actual_original_science_exposures']}**.",
        f"Native ZTF full \`psfcat.fits\` catalogues parsed: **{r['n_official_native_psfcat_products_parsed']}/{r['n_official_native_psfcat_products_requested']}**.",
        f"Spatially varying \`sciimgdao.psf\` native files downloaded (not decoded): **{r['n_native_spatial_daophot_files_downloaded']}/{r['n_native_spatial_daophot_products_requested']}**.",
        f"Gaia target/reference predictions inspected within available psfcat products: **{r['n_gaia_predictions_screened_against_native_psfcat']}**.",
        f"Provisional unique nearest PSF catalog candidates passing conservative profile/flag screen: **{r['n_provisional_unique_nearest_psfcat_candidates']}**.",
        f"Native PSF catalogue HTTP 503: **{r['n_psfcat_503_errors']}**; DAOPhot HTTP 503: **{r['n_daophot_503_errors']}**.",
        "",
        "| Technical field | Science MJD | PSF native FITS catalog status | Gaia positions in that catalog | Provisional unique candidate screens | DAOPhot spatial file status |",
        "|---|---:|---|---:|---:|---|",
    ]
    for e in r["frames"]:
        c=e["native_psf_catalogue_candidate_screens"]
        d=e["native_spatial_daophot_file_provenance"]
        lines.append(
            f"| {e['target']} | {e['original_science_mjd_assumed_utc']:.6f} | "
            f"{c['status']} | {len(c.get('screens',[]))} | "
            f"{c.get('n_provisional_unique_nearest_source_candidates',0)} | "
            f"{d['status']} |")
    lines.extend([
        "",
        "## Scientific boundaries and review",
        "",
        "- Catalogue fields follow official ZTF ZSDS §10.6: \`sourceid, xpos, ypos, ra, dec, flux, sigflux, mag, sigmag, snr, chi, sharp, flags\`. The sourceid counts sources **within that exposure**, not a Gaia DR3 ID, ZTF lightcurve ID or proven physical association.",
        "- A catalogued counterpart must lie within **1 arcsec** of Gaia's predicted coordinate, pass PSF chi **0.5–1.5**, sharp **−0.5 to +0.5**, SNR >=5, and have no ZTF **6141 disqualifying mask bits** or catalog edge flag −1. A second catalogued source within **3 arcsec** flags possible crowding. These are conservative screening choices, not survey-calibrated match probabilities.",
        "- An unavailable catalogue, HTTP 503, low SNR, poor chi/sharp, no 1-arcsec candidate or multiple native sources is **not** an astrophysical nondetection and does not prove a source physically exists or does not exist.",
        "- The official spatial \`sciimgdao.psf\` product is inspected **only for native file provenance and size**, not decoded or evaluated at a source position. The v1.13 center-of-field PSF stamp is likewise not the spatial source PSF.",
        "- The exact Gaia 5D formal covariance is Gaia-only; CIDA 11 high RUWE indicates possible real model systematics. No complete telescope WCS error model, observer topocentric corrections, PSF crowding completeness or physical source identification.",
        "- All original ZTF native catalog, DAOPhot and Gaia table bytes are processed in memory on an ephemeral runner. The public report is derived aggregate evidence only.",
        "",
    ])
    m.write_text("\n".join(lines),encoding="utf-8")
    return j,m


def main():
    p=argparse.ArgumentParser(description="Original same-date ZTF PSF native source catalog and DAOPhot file read-only pilot")
    p.add_argument("original_irsa_zip",type=Path)
    p.add_argument("--seed",type=Path,default=SEED)
    p.add_argument("--ledger",type=Path,default=LEDGER)
    p.add_argument("--gaia-timeout",type=float,default=25)
    p.add_argument("--archive-timeout",type=float,default=12)
    p.add_argument("--output",type=Path,
                   default=ROOT/"reports/generated/v1.14_native_psfcat")
    p.add_argument("--require-some-native-products",action="store_true")
    args=p.parse_args()
    r=run(args.original_irsa_zip,args.seed,args.ledger,
          gaia_timeout=args.gaia_timeout,archive_timeout=args.archive_timeout)
    paths=write_outputs(r,args.output)
    print(json.dumps({
        "n_official_psf_catalogues_parsed":r["n_official_native_psfcat_products_parsed"],
        "n_native_spatial_daophot_files_downloaded":r["n_native_spatial_daophot_files_downloaded"],
        "n_provisional_unique_psfcat_candidates":r["n_provisional_unique_nearest_psfcat_candidates"],
        "n_source_psf_models_calibrated":0,
        "n_authenticated_astrophysical_source_ids":0,
        "reports":[str(x) for x in paths],
    },indent=2))
    if (args.require_some_native_products
        and r["n_official_native_psfcat_products_parsed"]+
        r["n_native_spatial_daophot_files_downloaded"]==0):
        p.exit(2,"No original native ZTF PSF product retrieved; archive transport failure not sky nondetection.\n")


if __name__=="__main__":
    main()
