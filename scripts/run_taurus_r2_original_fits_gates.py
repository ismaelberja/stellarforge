"""Live R2 fixed-historical science+mask FITS and native PSF neighbour review.

Runs on GitHub Actions against official Gaia DR3/IRSA ZTF public archives.
Raw FITS, ZTF original photometric tables, and Gaia original responses
remain ephemeral. Public output contains derived non-discovery QA only.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.prepare_taurus_variability_r1 import DEFAULT_SEED
from stellarforge.r2_original_fits_gates import run_fixed_fttau_cida_original_images

LEDGER=Path("data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json")


def main():
    parser=argparse.ArgumentParser(
        description="Review exactly 4 historical ZTF g-band FT Tau/CIDA11 original FITS+mask and native PSFcat, no physical identity")
    parser.add_argument("--seed",type=Path,default=DEFAULT_SEED)
    parser.add_argument("--ledger",type=Path,default=LEDGER)
    parser.add_argument("--output",type=Path,default=Path(
        "reports/generated/taurus_r2_ft_tau_cida11_original_fits_derived.json"))
    args=parser.parse_args()
    result=run_fixed_fttau_cida_original_images(
        args.seed.read_bytes(),
        json.loads(args.ledger.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(
        result,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    for k,v in result.items():
        if k.startswith("n_") or k in ("phase","r2_science_completed",
                                     "historic_original_exposure_count"):
            print(k,":",v)
    for record in result["frames"]:
        psf=record["native_psfcat_neighbours"]
        mask=record["science_mask_image"]
        print(json.dumps({
            "field":record["historical_target_label"],
            "mjd":record["original_science_mjd"],
            "metadata_status":(record["original_metadata"] if isinstance(
                record["original_metadata"],str) else record["original_metadata"]["status"]),
            "native_psf_status":psf if isinstance(psf,str) else psf.get("status"),
            "native_psf_additional_within_3arcsec":(
                psf.get("n_additional_native_psfcat_sources_within_3arcsec")
                if isinstance(psf,dict) else None),
            "original_image_mask_status":mask if isinstance(mask,str) else (
                mask.get("original_science_mask_status") or mask.get("status")),
            "physical_gaia_ztf_counterpart_confirmed":False,
        },sort_keys=True))
    print("No original survey pixel images, full source rows or raw Gaia DR3 tables written.")
    print("Derived-only report:",args.output)


if __name__=="__main__":
    main()
