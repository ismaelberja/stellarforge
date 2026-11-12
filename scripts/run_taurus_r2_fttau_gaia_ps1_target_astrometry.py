"""FT Tau R2: exact four native original source centroids vs Gaia & external PS1.

All original survey data transient; archive only derived quality metadata.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scripts.prepare_taurus_variability_r1 import DEFAULT_SEED
from stellarforge.r2_fttau_gaia_ps1_target_astrometry import (
    run_ft_tau_gaia_ps1_ztf_target_astrometry,
)

HIST=Path("data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json")
OID=Path("reports/taurus_variability_r2/REAL_ALTERNATIVE_ZTF_OID_ORIGINAL_RUN_RECEIPT.json")
FITS=Path("reports/taurus_variability_r2/FT_TAU_TWO_ORIGINAL_ZTF_FIELDS_GR_FITS_MASK_PSF_DERIVED_NO_RAW.json")
PRIOR720=Path("reports/taurus_variability_r2/FTTAU_720_REAL_NATIVE_ENSEMBLE_ZTF_PS1_PIPELINE_HEADER_NO_RAW.json")
PREV=Path("reports/taurus_variability_r2/FTTAU_REAL_ORIGINAL_MAST_PS1_DR2_EXTERNAL_SOURCE_COLOR_PILOT_NO_RAW.json")

def main():
    p=argparse.ArgumentParser(description="R2 original Gaia FT Tau motion, independent PS1 field controls and four original ZTF target source positions; NOT a physical identification")
    p.add_argument("--seed",type=Path,default=DEFAULT_SEED)
    p.add_argument("--historical",type=Path,default=HIST)
    p.add_argument("--oid-receipt",type=Path,default=OID)
    p.add_argument("--prior-images",type=Path,default=FITS)
    p.add_argument("--prior-720",type=Path,default=PRIOR720)
    p.add_argument("--prior-external-ps1",type=Path,default=PREV)
    p.add_argument("--output",type=Path,default=Path(
        "reports/generated/taurus_r2_fttau_gaia_ps1_ztf_target_original_astrometry_no_raw.json"))
    a=p.parse_args()
    prior_images=a.prior_images.read_bytes()
    prior_720=a.prior_720.read_bytes()
    prior_external=a.prior_external_ps1.read_bytes()
    derived=run_ft_tau_gaia_ps1_ztf_target_astrometry(
        a.seed.read_bytes(),
        json.loads(a.historical.read_text("utf8")),
        json.loads(a.oid_receipt.read_text("utf8")),
        json.loads(prior_images),
        json.loads(prior_720),
        json.loads(prior_external))
    derived["prior_original_four_images_ledger_sha256"]=hashlib.sha256(prior_images).hexdigest()
    derived["prior_original_720_reference_ledger_sha256"]=hashlib.sha256(prior_720).hexdigest()
    derived["prior_original_external_ps1_source_ledger_sha256"]=hashlib.sha256(prior_external).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(derived,sort_keys=True,indent=2,allow_nan=False)+"\n",
                        encoding="utf8")
    for k,v in derived.items():
        if k.startswith("n_") or k in ("phase","scientific_R2_full_physical_source_identity_completed"):
            print(k,":",v)
    for b in derived["original_same_band_reference_astrometry"]:
        r=b["source_reference_alignment"]
        print(json.dumps({
            "band":b["band"],
            "external_PS1_ZTF_ZTF_reference_triples":r["n_original_unique_external_ps1_ztf_ztf_triplets"],
            "internal_reference_holdout_pass":r["both_fields_heldout_internal_geometry_pass"],
            "same_filter_target_status":b["target_same_band_field_pair_summary"]["status"],
            "physical_target_Gaia_ZTF_identity_confirmed":False,
            "source_oid_lightcurves_merged":False,
        },sort_keys=True))
    for row in derived["original_four_exposure_target_candidate_details"]:
        t=row["target_native_candidate"]
        print(json.dumps({
            "band":row["band"],"field":row["field"],
            "native_original_source_status":t["status"],
            "nearest_arcsec":t.get("nearest_original_native_source_to_predicted_Gaia_arcsec"),
            "second_arcsec":t.get("second_nearest_original_native_source_arcsec"),
            "external_reference_relative_status":row["descriptive_PS1_reference_adjusted_target"]["status"],
            "physical_identity_verified":False,
        },sort_keys=True))
    print("No original PS1 source IDs, positions, ZTF/native photometry, Gaia table or FITS image saved.")
    print("Derived-only record:",a.output)

if __name__=="__main__":
    main()
