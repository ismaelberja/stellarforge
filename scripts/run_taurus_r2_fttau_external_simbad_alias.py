"""Original exact Gaia DR3 / SIMBAD FT Tau naming-audit runner."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from scripts.prepare_taurus_variability_r1 import DEFAULT_SEED
from stellarforge.r2_fttau_external_simbad_alias import run_fttau_simbad_exact_external_alias

HIST=Path("data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json")
OID=Path("reports/taurus_variability_r2/REAL_ALTERNATIVE_ZTF_OID_ORIGINAL_RUN_RECEIPT.json")
PSF=Path("reports/taurus_variability_r2/FTTAU_SIX_ORIGINAL_NATIVE_SPATIAL_DAOPHOT_PSF_NO_RAW.json")


def main():
    p=argparse.ArgumentParser(description="Exact external CDS SIMBAD identifiers: FT Tau vs Gaia DR3 149623711269425408; no original ZTF source acceptance")
    p.add_argument("--output",type=Path,default=Path(
        "reports/generated/r2_fttau_original_simbad_gaia_alias_no_raw.json"))
    a=p.parse_args()
    seed=DEFAULT_SEED.read_bytes()
    raw={name:path.read_bytes() for name,path in (
        ("historical_24_seed",HIST),("frozen_original_ztf_oid",OID),
        ("frozen_six_native_ztf_psf",PSF))}
    result=run_fttau_simbad_exact_external_alias(
        seed,*[json.loads(raw[k]) for k in raw])
    result["frozen_r1_original_seed_sha256"]=hashlib.sha256(seed).hexdigest()
    result["frozen_prior_derived_ledgers_sha256"]={
        k:hashlib.sha256(b).hexdigest() for k,b in raw.items()}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    print("phase",result["phase"])
    print("original_cds_simbad_alias_status",result["original_cds_simbad_alias_status"])
    print("CDS_sim_b_mirror",result["simbad_original_query_mirror"])
    print("two_exact_tap_responses",result["simbad_original_gaia_alias_response_sha256"] is not None,
          result["simbad_original_ft_name_response_sha256"] is not None)
    if result["external_catalogue_alias_evidence"] is not None:
        print("external_alias_summary",result["external_catalogue_alias_evidence"])
    for x in result["mirrors_attempted_metadata_only"]:print("mirror_attempt",x)
    print("independently_authenticated_ZTF_source_counterparts",result["n_independently_authenticated_gaia_ztf_physical_source_matches"])
    print("Derived-only output",a.output)


if __name__=="__main__":
    main()
