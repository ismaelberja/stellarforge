"""Execute independent original MAST PS1 DR2 source-level FT Tau reference QC.

The previous 720" reference ensemble and original 4 archival exposure
products are frozen; original PS1+ZTF rows remain ephemeral and are
NEVER committed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scripts.prepare_taurus_variability_r1 import DEFAULT_SEED
from stellarforge.r2_fttau_external_ps1 import original_external_ps1_ft_tau_study

HIST=Path("data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json")
OID=Path("reports/taurus_variability_r2/REAL_ALTERNATIVE_ZTF_OID_ORIGINAL_RUN_RECEIPT.json")
FITS=Path("reports/taurus_variability_r2/FT_TAU_TWO_ORIGINAL_ZTF_FIELDS_GR_FITS_MASK_PSF_DERIVED_NO_RAW.json")
PREV=Path("reports/taurus_variability_r2/FTTAU_720_REAL_NATIVE_ENSEMBLE_ZTF_PS1_PIPELINE_HEADER_NO_RAW.json")

def main():
    p=argparse.ArgumentParser(description="FT Tau original Pan-STARRS1 DR2 source-level g/r colors versus ZTF native instrumental reference ensemble")
    p.add_argument("--seed",type=Path,default=DEFAULT_SEED)
    p.add_argument("--historical",type=Path,default=HIST)
    p.add_argument("--oid-receipt",type=Path,default=OID)
    p.add_argument("--original-images",type=Path,default=FITS)
    p.add_argument("--previous-720",type=Path,default=PREV)
    p.add_argument("--output",type=Path,default=Path(
        "reports/generated/taurus_r2_fttau_external_PS1_DR2_source_color_pilot_derived_no_raw.json"))
    args=p.parse_args()
    oldbytes=args.previous_720.read_bytes()
    imagebytes=args.original_images.read_bytes()
    d=original_external_ps1_ft_tau_study(
        args.seed.read_bytes(),json.loads(args.historical.read_text("utf8")),
        json.loads(args.oid_receipt.read_text("utf8")),
        json.loads(imagebytes),json.loads(oldbytes))
    d["immutable_previous_720_reference_evidence_sha256"]=hashlib.sha256(oldbytes).hexdigest()
    d["immutable_previous_four_original_images_evidence_sha256"]=hashlib.sha256(imagebytes).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(d,indent=2,sort_keys=True,allow_nan=False)+"\n",
                           encoding="utf8")
    print("original PS1 status:",d["external_PS1_DR2_original_source_query"]["status"])
    print("original PS1 source total:",d["external_PS1_DR2_original_source_query"]["n_ps1_original_rows"])
    print("good independent PS1 references:",d["external_PS1_DR2_original_source_query"]["n_ps1_good_color_crowding_sources"])
    print("original SHA-verifed ZTF catalogues:",d["n_original_ZTF_full_native_psfcats_reverified"])
    print("external PS1 g/r pilot internal holdout passes:",d["n_same_band_PanSTARRS_source_level_internal_pilot_passes"])
    for band in d["bands"]:
        fit=band["independent_external_PS1_source_level_color_test"]
        print(json.dumps({
            "band":band["band"],
            "status":fit["status"],
            "n_independent_PS1_crossmatched_triplets":fit.get("n_independently_queried_PS1_unique_reference_triplets"),
            "n_training":fit.get("n_train"),"n_heldout":fit.get("n_heldout"),
            "field_fits":fit.get("per_original_ZTF_field_fits"),
            "confirmed_physical_ft_tau_source":False,
            "lightcurves_joined":False,
        },sort_keys=True))
    print("NO PS1/ZTF original per-source rows, coordinates, fluxes or individual source IDs persisted:",args.output)

if __name__=="__main__":
    main()
