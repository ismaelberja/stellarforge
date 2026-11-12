"""Run six frozen FT Tau original spatial DAOPhot source pixel QA: no raw data."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from scripts.prepare_taurus_variability_r1 import DEFAULT_SEED
from stellarforge.r2_fttau_six_original_native_spatial_psf import (
    run_six_original_native_spatial_psf,
)

FILES={
    "historical":Path("data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json"),
    "prior_oid":Path("reports/taurus_variability_r2/REAL_ALTERNATIVE_ZTF_OID_ORIGINAL_RUN_RECEIPT.json"),
    "prior_four":Path("reports/taurus_variability_r2/FT_TAU_TWO_ORIGINAL_ZTF_FIELDS_GR_FITS_MASK_PSF_DERIVED_NO_RAW.json"),
    "original_eight":Path("reports/taurus_variability_r2/FTTAU_MULTINIGHT_ORIGINAL_ZTF_SOURCE_AUDIT_NO_RAW.json"),
    "original_bad_three":Path("reports/taurus_variability_r2/FTTAU_THREE_FROZEN_BAD_PSF_MASK_DIAGNOSIS_NO_RAW.json"),
    "original_chi_six":Path("reports/taurus_variability_r2/FTTAU_SIX_ORIGINAL_ZTF_CHI_BLIND_REFERENCES_NO_RAW.json"),
    "original_gaussian_six":Path("reports/taurus_variability_r2/FTTAU_SIX_ORIGINAL_ZTF_INDEPENDENT_GAUSSIAN_PIXELS_NO_RAW.json"),
}
ORDER=list(FILES)


def main()->None:
    p=argparse.ArgumentParser(description="Six exact original ZTF PSFcat+science+mask+spatial DAOPhot PSF/field-center stamp integrity and holdout QA")
    p.add_argument("--output",type=Path,default=Path(
        "reports/generated/r2_fttau_six_original_native_spatial_psf_pixel_holdout_no_raw.json"))
    args=p.parse_args()
    raw={name:path.read_bytes() for name,path in FILES.items()}
    data=run_six_original_native_spatial_psf(
        DEFAULT_SEED.read_bytes(),*[json.loads(raw[k]) for k in ORDER])
    data["previous_seven_original_ledger_sha256"]={
        name:hashlib.sha256(payload).hexdigest() for name,payload in raw.items()}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(
        json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+"\n",
        encoding="utf8")
    for k,v in data.items():
        if k.startswith("n_") or k=="phase":
            print(k,v)
    for row in data["original_six_exact_native_spatial_ztf_source_pixel_results"]:
        q=row.get("source_spatial_psf_same_image_holdout_diagnostics") or {}
        center=row.get("spatial_model_consistency_at_field_center") or {}
        print(row["band"],row["field"],row["epoch_role"],
              "old_chi",row["original_native_source_chi"],
              "model",row["spatial_dao_psf_status"],
              "center",center.get("status",row["original_field_center_stamp_status"]),
              "pixel_status",q.get("status"),
              "same_source_holdout_normalized_rms",
              q.get("same_image_holdout_residual_rms_over_sky_noise_proxy"))
    print("Raw original Gaia/source/DAO/PSF FITS catalogues, image pixels and source fluxes were never written.")
    print("Derived-only evidence:",args.output)


if __name__=="__main__":
    main()
