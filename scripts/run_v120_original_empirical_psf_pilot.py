"""v1.20 manually dispatched ORIGINAL ZTF strict-star empirical PSF pilot.

Real data is loaded only into ephemeral runner memory. Original ZIP and
Gaia/IRSA products must never enter Git. No automatic recurring acquisition.
The original ZTF DAOPhot training-star roster remains unknown. A successfully
fitted *different-star empirical* PSF is not original-survey calibration.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from zipfile import ZipFile

import numpy as np

from stellarforge.v13_observational_review import review_irsa_artifact
from stellarforge.v17_field_controls import stratified_ztf_image_candidates
from stellarforge.v18_gaia_references import (
    download_reference_catalog, parse_reference_catalog,
    retarget_same_ztf_exposure,
)
from stellarforge.v19_gaia_covariance import (
    fetch_gaia_astrometry, parse_gaia_astrometry, propagate_gaia_5p_formal,
)
from stellarforge.v111_reference_parallax import load_ledger, all_required_gaia_ids
from stellarforge.v114_native_psfcat_association import (
    official_psf_product_url, fetch_native_psf_product,
    parse_psf_fit_catalogue,
)
from stellarforge.v113_official_masks_psf import (
    official_ancillary_url, fetch_ancillary_fits,
)
from stellarforge.v15_image_pixels import fetch_fits_cutout
from stellarforge.v119_empirical_psf_noise import (
    train_and_holdout_empirical_psf, public_aggregate_only,
)
from stellarforge.v120_observed_star_cohort import (
    preregister_strict_cohort, screen_fixed_cohort_native_catalogue,
    registered_star_from_masked_original_fits, public_v120_summary,
)

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv"
LEDGER = ROOT / "data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json"
TARGET_ID = "3419110734340795648"  # CIDA 11, original two g-band dates.
CAT_OK = "PROVISIONAL_CATALOGUE_NEAREST_AND_PROFILE_SCREEN_PASSED"


def _fail(exc: Exception, label: str) -> dict:
    result = {"status": label, "error_type": type(exc).__name__}
    if isinstance(exc, HTTPError):
        result["http_status"] = int(exc.code)
    return result


def run(
    original_zip: Path, seed: Path = SEED, ledger_file: Path = LEDGER, *,
    gaia_timeout: float = 30., archive_timeout: float = 8.,
) -> dict:
    if not (1 <= gaia_timeout <= 60 and 1 <= archive_timeout <= 20):
        raise ValueError("Unbounded real archive acquisition")
    original = review_irsa_artifact(original_zip, seed)
    ledger = load_ledger(ledger_file)
    if (len(ledger["exposures"]) != 4
            or {x["gaia_dr3_source_id"] for x in original["targets"]}
            != {e["target_gaia_id"] for e in ledger["exposures"]}):
        raise ValueError("Historical original target/exposure provenance mismatch")
    with Path(seed).open(newline="", encoding="utf8") as fh:
        seeds = {str(x["gaia"]): x for x in csv.DictReader(fh)}
    cid = seeds[TARGET_ID]
    raw_wide = download_reference_catalog(
        float(cid["ra"]), float(cid["dec"]), timeout=gaia_timeout)
    cone = parse_reference_catalog(raw_wide)

    # No ZTF native catalogue/pixel is accessed before these names and
    # their TRAIN vs HOLDOUT assignments are frozen from Gaia only.
    cohort = preregister_strict_cohort(
        cone, target_id=TARGET_ID,
        prior_ids=set(all_required_gaia_ids(ledger)))
    wide_hash = hashlib.sha256(raw_wide).hexdigest()
    if cohort["n_preselected_strict_sources"] != 7:
        return {
            "schema": "stellarforge-v1.20-strict-cohort-real-data-pilot",
            "status": "INSUFFICIENT_STRICT_GAIA_BEFORE_ZTF_DATA",
            "n_gaia_cone_rows": len(cone),
            "n_strict_gaia_candidate_sources": cohort["n_preselected_strict_sources"],
            "gaia_widecone_sha256": wide_hash,
            "frames": [],
            "new_empirical_model_tested_on_real_original_ztf_pixels": False,
            "original_ztf_daophot_training_star_membership_verified": False,
            "independent_instrument_psf_wcs_calibrated": False,
            "astronomical_discovery_claimed": False,
        }
    fixed_ids = tuple(
        (*cohort["training_source_ids"], *cohort["holdout_source_ids"]))
    raw_formal = fetch_gaia_astrometry(
        tuple(sorted(fixed_ids)), timeout_sec=gaia_timeout)
    formal = parse_gaia_astrometry(
        raw_formal, expected_ids=tuple(sorted(fixed_ids)))
    formal_hash = hashlib.sha256(raw_formal).hexdigest()

    exposures = [e for e in ledger["exposures"]
                 if e["target_gaia_id"] == TARGET_ID and e["band"] == "zg"]
    if len(exposures) != 2:
        raise ValueError("CIDA 11 fixed original g-band exposure ledger changed")
    frames = []
    with ZipFile(original_zip) as z:
        original_candidates = stratified_ztf_image_candidates(
            z.read(f"{TARGET_ID}_IRSA_RAW.csv"),
            ra_deg=float(cid["ra"]), dec_deg=float(cid["dec"]),
            pmra_mas_yr=float(cid["pmra"]),
            pmdec_mas_yr=float(cid["pmdec"]),
            science_per_oid=6, cutout_arcsec=90,
        )
        for exposure in exposures:
            exact = [
                c for group in original_candidates
                if (group["ztf_oid"] == exposure["oid"]
                    and group["band"] == exposure["band"])
                for c in group["candidates"]
                if (c["kind"] == "science" and c["mjd"] is not None
                    and abs(float(c["mjd"]) - float(exposure["mjd"])) < .00002)
            ]
            if len(exact) != 1:
                raise ValueError("Cannot authenticate exact original science exposure")
            original_url = exact[0]["url"]
            exposure_id = urlparse(original_url).path
            frame = {
                "field": "CIDA 11", "band": "zg",
                "mjd": float(exposure["mjd"]),
                "native_catalogue_sha256": None,
                "n_native_train": 0, "n_native_holdout": 0,
                "n_registered_train": 0, "n_registered_holdout": 0,
                "n_mask_or_registration_failures": 0,
                "image_access_failures": 0,
                "empirical_psf_status": "NOT_ATTEMPTED",
                "n_heldout_profile_reviews": 0,
            }
            # Distinct full Gaia 5p source predictions for exactly this MJD.
            positions = []
            for source_id in fixed_ids:
                propagated = propagate_gaia_5p_formal(
                    formal[source_id], mjd_utc=float(exposure["mjd"]))
                positions.append({
                    "source_id": source_id,
                    "geocentric_parallax_adjusted_ra_deg":
                        propagated["geocentric_parallax_adjusted_ra_deg"],
                    "geocentric_parallax_adjusted_dec_deg":
                        propagated["geocentric_parallax_adjusted_dec_deg"],
                })
            try:
                raw_cat = fetch_native_psf_product(
                    official_psf_product_url(original_url, "psfcat.fits"),
                    kind="psfcat.fits", timeout=archive_timeout)
                cat = parse_psf_fit_catalogue(raw_cat)
                qa = screen_fixed_cohort_native_catalogue(cat, positions, cohort)
                frame["native_catalogue_sha256"] = cat["sha256"]
                frame["n_native_train"] = qa["n_native_training_candidates"]
                frame["n_native_holdout"] = qa["n_native_holdout_candidates"]
            except (HTTPError, URLError, TimeoutError, OSError, ValueError,
                    KeyError) as exc:
                frame["empirical_psf_status"] = (
                    "ORIGINAL_NATIVE_SOURCE_CATALOGUE_UNAVAILABLE_OR_INVALID")
                frame["image_access_failures"] = 1
                frames.append(frame)
                continue
            # Group memberships remain the exact same Gaia-only fixed split.
            # Do NOT swap a failing holdout with an easy training star.
            if (frame["n_native_train"] < 3
                    or frame["n_native_holdout"] < 2):
                frame["empirical_psf_status"] = (
                    "PREREGISTERED_NATIVE_CATALOGUE_3_PLUS_2_GATE_NOT_MET")
                frames.append(frame)
                continue
            prepared = [[], []]
            screens = [qa["train_screens"], qa["holdout_screens"]]
            for group_index, group in enumerate(screens):
                for screen in group:
                    if screen["status"] != CAT_OK:
                        continue
                    native_id = int(screen["ztf_native_per_exposure_sourceid"])
                    candidates = np.flatnonzero(
                        np.asarray(cat["rows"]["sourceid"], dtype=int)
                        == native_id)
                    if len(candidates) != 1:
                        raise ValueError("Native PSFcat row uniqueness violated")
                    ix = int(candidates[0])
                    source_ra = float(cat["rows"]["ra"][ix])
                    source_dec = float(cat["rows"]["dec"][ix])
                    try:
                        src_url = retarget_same_ztf_exposure(
                            original_url, source_ra, source_dec,
                            size_arcsec=60)
                        msk_url = official_ancillary_url(
                            src_url, "mskimg.fits")
                        sci = fetch_fits_cutout(
                            src_url, timeout=archive_timeout)
                        mask = fetch_ancillary_fits(
                            msk_url, kind="mskimg.fits",
                            timeout=archive_timeout)
                    except (HTTPError, URLError, TimeoutError,
                            OSError, ValueError) as exc:
                        frame["image_access_failures"] += 1
                        continue
                    try:
                        star, _ = registered_star_from_masked_original_fits(
                            sci, mask,
                            gaia_source_id=screen["gaia_source_id"],
                            exposure_id=exposure_id,
                            native_source_ra=source_ra,
                            native_source_dec=source_dec,
                            native_detector_x=float(cat["rows"]["xpos"][ix]),
                            native_detector_y=float(cat["rows"]["ypos"][ix]),
                        )
                        prepared[group_index].append(star)
                    except (ValueError, TypeError, OverflowError,
                            np.linalg.LinAlgError):
                        frame["n_mask_or_registration_failures"] += 1
                        continue
            frame["n_registered_train"] = len(prepared[0])
            frame["n_registered_holdout"] = len(prepared[1])
            if len(prepared[0]) < 3 or len(prepared[1]) < 2:
                frame["empirical_psf_status"] = (
                    "REAL_SOURCE_MASKED_STAMP_3_PLUS_2_GATE_NOT_MET")
                frames.append(frame)
                continue
            try:
                model = train_and_holdout_empirical_psf(
                    prepared[0], prepared[1])
                public_model = public_aggregate_only(model)
                frame["empirical_psf_status"] = public_model["status"]
                frame["n_heldout_profile_reviews"] = (
                    public_model["n_heldout_profile_reviews"])
            except (ValueError, TypeError, np.linalg.LinAlgError):
                frame["empirical_psf_status"] = (
                    "REAL_EMPIRICAL_PSF_VALIDATION_INPUT_OR_FIT_REJECTED")
            frames.append(frame)
    return public_v120_summary(
        cohort=cohort, frame_summaries=frames,
        widecone_sha256=wide_hash, formal_gaia_sha256=formal_hash)


def render_markdown(results: dict) -> str:
    """Render only the whitelisted public numeric/provenance report."""
    lines = [
        "# v1.20 — Original CIDA 11 strict-source empirical PSF readiness",
        "",
        "**Real archival attempt; no independent instrument calibration.**",
        "",
        "A 4-training + 3-holdout candidate allocation was predeclared by",
        "strict Gaia-only quality and isolation screens before inspecting any",
        "ZTF native catalogue or source images. These are only provisional",
        "Gaia-to-ZTF source candidates, and the historical DAOPhot",
        "training-star membership remains UNKNOWN.",
        "",
        f"Gate: **{results['status']}**",
        "",
        "| Original MJD | Native train / holdout | Registered train / holdout | Empirical model |",
        "| --- | --- | --- | --- |",
    ]
    for x in results.get("frames", []):
        lines.append(
            f"| {x['mjd']:.6f} | "
            f"{x['n_native_train']} / {x['n_native_holdout']} | "
            f"{x['n_registered_train']} / {x['n_registered_holdout']} | "
            f"{x['empirical_psf_status']} |")
    lines += [
        "",
        "A frame can be analyzed with the empirical whole-star model only",
        "when at least 3 preregistered training stars and 2 other preregistered",
        "held-out stars have genuine science+mask source FITS passing all gates.",
        "There is no substitution after examining residuals.",
        "",
        "**Do not infer astronomical nondetections from archive failures,",
        "missing source candidates, bad pixels or rejected profiles.**",
        "A passing held-out star profile is not proof of a unique Gaia-ZTF",
        "physical match or that the star was excluded from ZTF's PSF",
        "training. The bilinear recentering correlates pixels; verified",
        "per-exposure CCD gain, read noise and covariance are not available.",
        "No companion, new star, physical variability, independent PSF/WCS",
        "uncertainty or astronomy discovery is claimed.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("original_zip", type=Path)
    ap.add_argument("--seed", type=Path, default=SEED)
    ap.add_argument("--ledger", type=Path, default=LEDGER)
    ap.add_argument("--gaia-timeout", type=float, default=30.)
    ap.add_argument("--archive-timeout", type=float, default=8.)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    results = run(
        args.original_zip, args.seed, args.ledger,
        gaia_timeout=args.gaia_timeout, archive_timeout=args.archive_timeout)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "V120_REAL_ORIGINAL_STRICT_COHORT_NO_RAW.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n",
        encoding="utf8")
    (args.output / "V120_REAL_ORIGINAL_STRICT_COHORT_NO_RAW.md").write_text(
        render_markdown(results), encoding="utf8")
    print(json.dumps({
        "status": results["status"],
        "n_frames": len(results.get("frames", [])),
        "n_real_empirical_star_psf_frames": sum(
            x.get("empirical_psf_status") ==
            "INTERNAL_DISTINCT_STAR_PSF_HOLDOUT_COMPLETED"
            for x in results.get("frames", [])),
        "original_ztf_training_roster_verified": False,
        "physical_gaia_ztf_identity_confirmed": False,
    }, indent=2))


if __name__ == "__main__":
    main()
