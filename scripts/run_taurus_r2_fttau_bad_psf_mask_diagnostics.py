"""Command-line exact three original bad-source FT Tau PSF/image/mask diagnosis."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from stellarforge.r2_fttau_bad_psf_mask_diagnostics import (
    run_frozen_fttau_bad_psf_diagnostics,
)

PR44 = Path("reports/taurus_variability_r2/FTTAU_MULTINIGHT_ORIGINAL_ZTF_SOURCE_AUDIT_NO_RAW.json")

def main() -> None:
    p = argparse.ArgumentParser(description="Read-only FT Tau exactly three frozen late-night PSF failures")
    p.add_argument("--prior", type=Path, default=PR44)
    p.add_argument("--output", type=Path, default=Path(
        "reports/generated/r2_fttau_three_original_bad_psf_mask_diagnostics_no_raw.json"))
    a = p.parse_args()
    raw = a.prior.read_bytes()
    output = run_frozen_fttau_bad_psf_diagnostics(json.loads(raw))
    output["frozen_previous_original_multinight_ledger_sha256"] = hashlib.sha256(raw).hexdigest()
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(output, indent=2, sort_keys=True, allow_nan=False)+"\n",
                        encoding="utf8")
    for key,val in output.items():
        if key.startswith("n_") or key.startswith("phase"):
            print(key, val)
    for entry in output["frozen_failed_original_exposure_diagnostics"]:
        why = (entry.get("native_fit_diagnostics") or {}).get(
            "failed_source_level_quality_reasons")
        mask = (entry.get("image_mask_derived_diagnostics") or {}).get("original_mask_status")
        print(entry["band"], entry["field"], entry["native_diagnosis_status"],
              "failed_source_gates",why,"science_mask",mask)
    print("No original raw Gaia/ZTF source rows, FITS pixels or flux data saved.")
    print("Derived evidence only:",a.output)

if __name__ == "__main__":
    main()
