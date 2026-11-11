"""FT Tau R2 real original ZTF two-field instrumental reference ensemble.

No original FITS tables, per-source positions, original photometric
rows/magnitudes or full catalogue entries are written to disk.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scripts.prepare_taurus_variability_r1 import DEFAULT_SEED
from stellarforge.r2_fttau_crossfield_instrumental_ensemble import (
    run_ft_tau_two_field_relative_photometry,
)

HIST = Path("data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json")
OID = Path("reports/taurus_variability_r2/REAL_ALTERNATIVE_ZTF_OID_ORIGINAL_RUN_RECEIPT.json")
PREV = Path("reports/taurus_variability_r2/FT_TAU_TWO_ORIGINAL_ZTF_FIELDS_GR_FITS_MASK_PSF_DERIVED_NO_RAW.json")

def main():
    p=argparse.ArgumentParser(description="Real original native ZTF instrumental reference ensemble for FT Tau; NOT AB calibration or physical match")
    p.add_argument("--seed",type=Path,default=DEFAULT_SEED)
    p.add_argument("--historical",type=Path,default=HIST)
    p.add_argument("--oid-receipt",type=Path,default=OID)
    p.add_argument("--prior-fits",type=Path,default=PREV)
    p.add_argument("--output",type=Path,default=Path(
        "reports/generated/fttau_r2_real_crossfield_relative_instrumental_ensemble_no_raw.json"))
    args=p.parse_args()
    prior_bytes=args.prior_fits.read_bytes()
    result=run_ft_tau_two_field_relative_photometry(
        args.seed.read_bytes(),
        json.loads(args.historical.read_text(encoding="utf8")),
        json.loads(args.oid_receipt.read_text(encoding="utf8")),
        json.loads(prior_bytes))
    result["prior_original_fits_evidence_sha256"]=hashlib.sha256(prior_bytes).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n",
                           encoding="utf8")
    for k,v in result.items():
        if k.startswith("n_") or k in ("phase","scientific_r2_complete"):
            print(k,":",v)
    for group in result["bands"]:
        ensemble=group["native_source_crossfield_ensemble"]
        print(json.dumps({
            "band":group["band"],
            "status":group["status"],
            "n_matched_references":ensemble.get("n_reciprocal_crowding_screened_geometric_pairs"),
            "training_n":ensemble.get("n_training_after_fixed_robust_outlier_screen"),
            "validation_n":ensemble.get("n_validation_references"),
            "instrumental_median_delta_mag":ensemble.get(
                "ensemble_median_native_mag_difference_b_minus_a"),
            "heldout_scatter_mag":ensemble.get("heldout_robust_scatter_mag"),
            "internal_consistency_only":ensemble.get("instrumental_offset_internally_consistent",False),
            "external_photometric_calibration_complete":False,
            "gaia_to_ztf_physical_identity_verified":False,
            "ztf_oid_lightcurves_merged":False,
        },sort_keys=True))
    print("Original ZTF photometric source magnitudes, fluxes, sky positions and original pixels never saved.")
    print("Derived-only output:",args.output)

if __name__=="__main__":
    main()
