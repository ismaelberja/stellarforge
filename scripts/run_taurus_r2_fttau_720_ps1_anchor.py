"""Actual FT Tau original four ZTF catalogues and FITS PS1-header reference QA.

All original source rows, fluxes, sky coords and survey pixels stay in
ephemeral GitHub Actions memory. Only source-bounded derived QC saved.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scripts.prepare_taurus_variability_r1 import DEFAULT_SEED
from stellarforge.r2_fttau_720_ps1_anchor import run_ft_tau_720_ps1_reference

HIST=Path("data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json")
OID=Path("reports/taurus_variability_r2/REAL_ALTERNATIVE_ZTF_OID_ORIGINAL_RUN_RECEIPT.json")
PREV=Path("reports/taurus_variability_r2/FT_TAU_TWO_ORIGINAL_ZTF_FIELDS_GR_FITS_MASK_PSF_DERIVED_NO_RAW.json")
NO_GO=Path("reports/taurus_variability_r2/FTTAU_REAL_ORIGINAL_NATIVE_TWO_FIELD_INSTRUMENTAL_ENSEMBLE_NO_RAW.json")

def main():
    p=argparse.ArgumentParser(description="FT Tau 720-arcsec native ZTF PSF source controls with PS1-anchored pipeline FITS headers, NOT physical match")
    p.add_argument("--seed",type=Path,default=DEFAULT_SEED)
    p.add_argument("--historical",type=Path,default=HIST)
    p.add_argument("--oid-receipt",type=Path,default=OID)
    p.add_argument("--prior-images",type=Path,default=PREV)
    p.add_argument("--prior-360-no-go",type=Path,default=NO_GO)
    p.add_argument("--output",type=Path,default=Path(
        "reports/generated/fttau_r2_720_real_native_reference_ps1_pipeline_header_derived_only.json"))
    a=p.parse_args()
    old=json.loads(a.prior_360_no_go.read_text("utf8"))
    if (old.get("n_native_original_psf_catalogues_exactly_sha_verified")!=4
            or old.get("n_same_band_ensemble_internal_qc_passes")!=0
            or [b["native_source_crossfield_ensemble"].get(
                "n_reciprocal_crowding_screened_geometric_pairs")
                for b in old["bands"]] !=[10,19]):
        raise ValueError("Prior original predeclared 360-arcsec negative study changed")
    prior_bytes=a.prior_images.read_bytes()
    old_bytes=a.prior_360_no_go.read_bytes()
    output=run_ft_tau_720_ps1_reference(
        a.seed.read_bytes(),
        json.loads(a.historical.read_text("utf8")),
        json.loads(a.oid_receipt.read_text("utf8")),
        json.loads(prior_bytes))
    output["four_original_FITS_source_evidence_sha256"]=hashlib.sha256(prior_bytes).hexdigest()
    output["immutable_360arcsec_underpowered_previous_evidence_sha256"]=hashlib.sha256(old_bytes).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(output,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf8")
    for key,v in output.items():
        if key.startswith("n_") or key in ("phase","R2_physical_source_identity_completed"):
            print(key,":",v)
    for b in output["bands"]:
        ens=b["native_reference_ensemble_internal_only"]
        print(json.dumps({
            "band":b["band"],
            "controls_reciprocal_matched":ens.get("n_reciprocal_crowding_screened_geometric_pairs"),
            "internal_ensemble_status":ens["status"],
            "delta_inst_mag":ens.get("ensemble_median_native_mag_difference_b_minus_a"),
            "heldout_median_mag":ens.get("heldout_median_relative_offset_mag"),
            "spatial":b["inner_vs_outer_spatial_trend"]["status"],
            "pipeline_header_zeropoint_delta":b[
                "ZTF_own_PS1_anchored_FITS_header_comparison"].get(
                    "original_zTF_ps1_pipeline_header_delta_MAGZP_field609_minus_1605"),
            "independent_PS1_source_calibration":False,
            "physical_Gaia_ZTF_identity":False,
            "curves_joined":False,
        },sort_keys=True))
    print("Only derived QA data saved; original source magnitudes, FITS pixels and PS1 source rows unavailable/not committed:",a.output)

if __name__=="__main__":
    main()
