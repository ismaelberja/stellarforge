"""Run six original ZTF fixed FT Tau pixel Gaussian diagnostics; derived only."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from scripts.prepare_taurus_variability_r1 import DEFAULT_SEED
from stellarforge.r2_fttau_six_independent_pixel_residuals import (
    run_fttau_six_original_independent_pixel_fit,
)

HIST = Path("data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json")
OID = Path("reports/taurus_variability_r2/REAL_ALTERNATIVE_ZTF_OID_ORIGINAL_RUN_RECEIPT.json")
FOUR = Path("reports/taurus_variability_r2/FT_TAU_TWO_ORIGINAL_ZTF_FIELDS_GR_FITS_MASK_PSF_DERIVED_NO_RAW.json")
EPOCH = Path("reports/taurus_variability_r2/FTTAU_MULTINIGHT_ORIGINAL_ZTF_SOURCE_AUDIT_NO_RAW.json")
FAIL = Path("reports/taurus_variability_r2/FTTAU_THREE_FROZEN_BAD_PSF_MASK_DIAGNOSIS_NO_RAW.json")
CHI = Path("reports/taurus_variability_r2/FTTAU_SIX_ORIGINAL_ZTF_CHI_BLIND_REFERENCES_NO_RAW.json")


def main():
    p = argparse.ArgumentParser(
        description="Six frozen original native PSFcat+science+mask cutouts; independent analytic Gaussian pixels")
    p.add_argument("--output", type=Path, default=Path(
        "reports/generated/r2_fttau_six_original_independent_gaussian_pixels_no_raw.json"))
    args = p.parse_args()
    bytes_by_label = {label: path.read_bytes() for label,path in (
        ("historical",HIST),("prior_oid",OID),("prior_four",FOUR),
        ("original_eight",EPOCH),("original_bad_three",FAIL),("original_chi_six",CHI))}
    entry = run_fttau_six_original_independent_pixel_fit(
        DEFAULT_SEED.read_bytes(),
        *[json.loads(bytes_by_label[label]) for label in (
            "historical","prior_oid","prior_four","original_eight",
            "original_bad_three","original_chi_six")])
    entry["frozen_previous_original_ledger_sha256"]={
        label: hashlib.sha256(value).hexdigest()
        for label,value in bytes_by_label.items()
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(entry, indent=2, sort_keys=True, allow_nan=False)+"\n",
        encoding="utf8")
    for k,v in entry.items():
        if k.startswith("n_") or k=="phase":
            print(k,v)
    for x in entry["original_six_original_image_instrumental_residuals"]:
        d=x.get("independent_original_pixel_fit") or {}
        print(x["band"],x["field"],x["epoch_role"],
              "nativeChi",x.get("native_original_nearest_source_chi"),
              "pixelStatus",d.get("status",x["original_science_mask_status"]),
              "skyNormalizedCoreRMS",d.get("source_core_rms_residual_over_sky_mad_noise_proxy"),
              "FWHMarcsec",d.get("analytic_circular_gaussian_fwhm_arcsec_proxy"))
    for x in entry["original_three_same_oid_early_late_pixel_comparisons"]:
        print(x["band"],x["field"],"late/early pixelRMS ratio",
              x["descriptive_late_over_early_gaussian_core_rms_over_sky_mad_ratio"])
    print("No original full catalogues, science FITS pixels, source identifiers or fluxes stored.")
    print("Derived-only result:",args.output)


if __name__=="__main__":
    main()
