"""R5 independent-literature context and selection/claim falsification (offline).

All original source evidence is re-audited against frozen R2–R4 receipts.
The report is derived-only: independent astronomical instrument and physical
cross-identification remain NOT achieved.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from stellarforge.r5_critical_falsification import build_r5_critical_falsification
from stellarforge.r5_evidence_denominators_visual import r5_independent_denominator_svg


def main()->None:
    p=argparse.ArgumentParser(description="R5 defensible original-source literature and selection critical audit, not physical-source validation")
    p.add_argument("--root",type=Path,default=Path("."))
    p.add_argument("--json",type=Path,default=Path("reports/generated/taurus_r5_selection_critical_falsification_no_raw.json"))
    p.add_argument("--svg",type=Path,default=Path("reports/generated/taurus_r5_distinct_source_denominators.svg"))
    args=p.parse_args()
    result=build_r5_critical_falsification(args.root)
    svg=r5_independent_denominator_svg(result)
    args.json.parent.mkdir(parents=True,exist_ok=True)
    args.svg.parent.mkdir(parents=True,exist_ok=True)
    args.json.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf8")
    args.svg.write_text(svg,encoding="utf8")
    print(json.dumps({
        "r5_status":result["phase"],
        "different_observational_denominators":{
            "gaia_original_targets":24,
            "ztf_survey_objectids":6,
            "original_source_epoch_photometric_rows":684,
        },
        "gaia_catalogue_author_rows_verified":24,
        "original_ZTF_OIDs_with_received_source_CSV":3,
        "original_epoch_source_rows_bit15_accepted":591,
        "physical_Gaia_ZTF_source_matches":0,
        "R5_critical_literature_selection_review_complete":result["final_scientific_interpretation"]["r5_methodological_literature_and_falsification_review_complete"],
        "R5_independent_physical_scientific_validation_passed":result["final_scientific_interpretation"]["r5_true_independent_physical_source_validation_pass"],
        "R6_evidence_based_methodological_report_possible":result["final_scientific_interpretation"]["r6_methodological_inconclusive_feasibility_report_can_be_written"],
        "R6_new_physical_asterisk_discovery_claim_allowed":result["final_scientific_interpretation"]["r6_authentic_new_astrophysical_variable_or_companion_discovery_claim_allowed"],
        "out_json_no_raw":str(args.json),"out_svg_genuine_counts_separate_denominators":str(args.svg)
    },indent=2))


if __name__=="__main__":
    main()
