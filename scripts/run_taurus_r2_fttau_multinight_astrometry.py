"""CLI: genuine additional-night FT Tau original ZTF target-source check.

Only derived observations are saved; raw IRSA/Gaia sources stay in memory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scripts.prepare_taurus_variability_r1 import DEFAULT_SEED
from stellarforge.r2_fttau_multinight_astrometry import (
    run_fttau_multinight_native_astrometry,
)

HIST = Path("data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json")
OID = Path("reports/taurus_variability_r2/REAL_ALTERNATIVE_ZTF_OID_ORIGINAL_RUN_RECEIPT.json")
FITS = Path("reports/taurus_variability_r2/FT_TAU_TWO_ORIGINAL_ZTF_FIELDS_GR_FITS_MASK_PSF_DERIVED_NO_RAW.json")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="R2 FT Tau deterministic independent-night original native ZTF PSFcat audit")
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--historical", type=Path, default=HIST)
    parser.add_argument("--oid-receipt", type=Path, default=OID)
    parser.add_argument("--prior-images", type=Path, default=FITS)
    parser.add_argument("--output", type=Path, default=Path(
        "reports/generated/r2_fttau_multinight_native_psf_no_raw.json"))
    a = parser.parse_args()
    prior_raw = a.prior_images.read_bytes()
    result = run_fttau_multinight_native_astrometry(
        a.seed.read_bytes(), json.loads(a.historical.read_text(encoding="utf8")),
        json.loads(a.oid_receipt.read_text(encoding="utf8")),
        json.loads(prior_raw))
    result["frozen_prior_original_images_receipt_sha256"] = hashlib.sha256(
        prior_raw).hexdigest()
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf8")
    for key, value in result.items():
        if key.startswith("n_") or key in ("phase", "scientific_R2_complete"):
            print(key, value)
    for group in result["original_fixed_oid_strata"]:
        print(group["band"], group["field"], group["image_selection_status"],
              (group["paired_epoch_summary"] or {}).get("status", "NO_PAIR"))
    print("No original source catalogues, Gaia table, lightcurves or image pixels saved.")
    print("Derived-only evidence:", a.output)


if __name__ == "__main__":
    main()
