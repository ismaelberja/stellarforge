"""Four predeclared FT Tau original ZTF ObjectID science+mask/PSFcat QA.

Original photometric CSV rows, survey FITS and Gaia source data are
ephemeral. Public report stores bounded derived evidence only.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.prepare_taurus_variability_r1 import DEFAULT_SEED
from stellarforge.r2_ft_tau_two_field_fits import run_ft_two_field_four_original_images

HISTORIC=Path("data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json")
PREVIOUS=Path("reports/taurus_variability_r2/REAL_ALTERNATIVE_ZTF_OID_ORIGINAL_RUN_RECEIPT.json")

def main():
    p=argparse.ArgumentParser(description="R2 FT Tau same-band g/r cross-field original science/mask/native PSFcat, not physical source crossmatch")
    p.add_argument("--seed",type=Path,default=DEFAULT_SEED)
    p.add_argument("--historical",type=Path,default=HISTORIC)
    p.add_argument("--oid-receipt",type=Path,default=PREVIOUS)
    p.add_argument("--output",type=Path,default=Path(
        "reports/generated/taurus_r2_fttau_two_field_gr_original_image_derived_no_raw.json"))
    args=p.parse_args()
    data=run_ft_two_field_four_original_images(
        args.seed.read_bytes(),
        json.loads(args.historical.read_text(encoding="utf8")),
        json.loads(args.oid_receipt.read_text(encoding="utf8")))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf8")
    for k,v in data.items():
        if k.startswith("n_") or k in ("phase","r2_physical_source_identity_science_complete"):
            print(k,":",v)
    for pair in data["crossfield_same_filter_pairs"]:
        s=pair["crossfield_instrument_summary"]
        print(json.dumps({
            "band":pair["band"],"time_gap_days":pair["selection_mjd_gap_days"],
            "within_one_day":pair["selected_within_1day"],
            "selected":pair["selection_status"],
            "both_images_masks_psf":s["both_original_science_mask_native_products_available"],
            "both_instrumental_gates_passed":s["instrumental_gates_both_passed"],
            "physical_source_identity_confirmed":False,
            "curves_merged":False,
        },sort_keys=True))
    for row in data["original_fits_mask_native_psf_exposure_results"]:
        print(json.dumps({
            "selection":row["selection"],
            "psf_status":row["native_psf_status"],
            "science_mask_status":row["science_mask_status"],
            "all_three_instrument_checks_pass":row.get("all_three_instrument_source_checks_pass",False),
            "physical_source_confirmed":False,
        },sort_keys=True))
    print("No raw image pixels, photometric tables, native catalogues or Gaia response committed.")
    print("Derived-only original data:",args.output)

if __name__=="__main__":
    main()
