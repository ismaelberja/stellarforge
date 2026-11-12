"""Run original Gaia and six exact native ZTF PSFcats, archive no raw rows."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from scripts.prepare_taurus_variability_r1 import DEFAULT_SEED
from stellarforge.r2_fttau_chi_reference_controls import run_fttau_chi_blind_original_reference_study

HIST=Path("data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json")
OID=Path("reports/taurus_variability_r2/REAL_ALTERNATIVE_ZTF_OID_ORIGINAL_RUN_RECEIPT.json")
FITS=Path("reports/taurus_variability_r2/FT_TAU_TWO_ORIGINAL_ZTF_FIELDS_GR_FITS_MASK_PSF_DERIVED_NO_RAW.json")
EPOCH=Path("reports/taurus_variability_r2/FTTAU_MULTINIGHT_ORIGINAL_ZTF_SOURCE_AUDIT_NO_RAW.json")
BAD=Path("reports/taurus_variability_r2/FTTAU_THREE_FROZEN_BAD_PSF_MASK_DIAGNOSIS_NO_RAW.json")

def main():
    p=argparse.ArgumentParser(description="Source-chi-blind original six fixed FT Tau native PSF reference cohorts")
    p.add_argument("--output",type=Path,default=Path(
        "reports/generated/r2_fttau_six_original_chi_blind_reference_cohorts_no_raw.json"))
    a=p.parse_args()
    epoch_bytes,bad_bytes=EPOCH.read_bytes(),BAD.read_bytes()
    result=run_fttau_chi_blind_original_reference_study(
        DEFAULT_SEED.read_bytes(),json.loads(HIST.read_text("utf8")),
        json.loads(OID.read_text("utf8")),json.loads(FITS.read_text("utf8")),
        json.loads(epoch_bytes),json.loads(bad_bytes))
    result["frozen_original_multinight_ledger_sha256"]=hashlib.sha256(epoch_bytes).hexdigest()
    result["frozen_original_bad_psf_ledger_sha256"]=hashlib.sha256(bad_bytes).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf8")
    for key,val in result.items():
        if key.startswith("n_") or key=="phase":print(key,val)
    for row in result["original_fixed_same_oid_early_late_groups"]:
        for i,x in enumerate(row["original_two_epoch_reference_cohorts"]):
            a=x["all_chi_blind_controls"]
            m=x["snr_factor_two_matched_controls"]
            print(row["band"],row["field"],["EARLY","LATE"][i],
                  "target_chi",x["target_original_chi"],
                  "all_controls",a["n_reference_sources"],
                  "fraction_below_old_0p5",a["fraction_chi_below_0p5"],
                  "snr_matched_controls",m["n_reference_sources"],
                  "snr_matched_fraction_below",m["fraction_chi_below_0p5"])
    print("No original catalogues, photometry, source IDs or FITS image pixels saved.")
    print("Derived output:",a.output)

if __name__=="__main__":main()
