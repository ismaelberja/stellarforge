"""R5 adversarial selection / external-literature science scope tests.

Every numerical R5 source ratio must stay attached to its correct Gaia
target / ZTF ObjectID / per-exposure photometry denominator.
"""
from __future__ import annotations
import copy
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest
import stellarforge.r5_critical_falsification as r5
from stellarforge.r5_critical_falsification import (
    LITERATURE, GATE_NAMES, SEVERITIES, _rate, build_r5_critical_falsification,
)
from stellarforge.r5_evidence_denominators_visual import r5_independent_denominator_svg

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def actual():
    return build_r5_critical_falsification(ROOT)


def test_all_prior_original_R2_R3_R4_reconciliations_and_r5_evidence(aCtual=None):
    j=build_r5_critical_falsification(ROOT)
    assert j["phase"]=="R5_CRITICAL_LITERATURE_AND_SELECTION_FEASIBILITY_REVIEW_DONE__INDEPENDENT_PHYSICAL_STAR_VALIDATION_NO_GO"
    assert j["schema_version"]=="stellarforge-taurus-r5-source-verified-selection-literature-falsification-adjudication-v1"
    assert j["date_utc"]=="2026-11-14"
    assert j["final_scientific_interpretation"]["r5_methodological_literature_and_falsification_review_complete"] is True
    assert j["final_scientific_interpretation"]["r5_true_independent_physical_source_validation_pass"] is False
    assert j["final_scientific_interpretation"]["r6_authentic_new_astrophysical_variable_or_companion_discovery_claim_allowed"] is False
    assert j["final_scientific_interpretation"]["r6_methodological_inconclusive_feasibility_report_can_be_written"] is True


@pytest.mark.parametrize("key,num,den",[
    ("technical_seed_ids_vs_original_author_adopted_member_rows",24,532),
    ("technical_seed_ids_vs_author_catalogue_gaia_ids",24,467),
    ("gaia_only_preliminary_quality_pass_of_original_24",17,24),
    ("gaia_astrometry_requires_review_of_original_24",7,24),
    ("gaia_sources_with_neighbour_within_5arcsec_of_original_24",4,24),
    ("gaia_positions_with_any_original_ZTF_positional_rows_of_original_24",22,24),
    ("gaia_physically_identified_with_ZTF_of_original_24",0,24),
    ("original_ZTF_exact_oid_dr24_source_csvs_returned_of_six_fixed_oids",3,6),
    ("original_ZTF_exact_oid_server_timeouts_twice_of_six_fixed_oids",3,6),
    ("original_ztf_catflags_bit15_retained_source_rows_of_684",591,684),
    ("original_ztf_catflags_bit15_rejected_source_rows_of_684",93,684),
    ("retrieved_original_ZTF_OID_curves_with_two_adjacent_empty_365day_bins_of_3",2,3),
])
def test_distinct_original_denominator_ledger_correctly_labelled(actual,key,num,den):
    j=actual["denominator_locked_descriptive_summary_not_population_inference"][key]
    assert j=={"n":num,"N":den,"percent_descriptive_only":round(100*num/den,2)}
    assert j["percent_descriptive_only"]<=100


@pytest.mark.parametrize("n,N",[
    (-1,24),(25,24),(24,0),(591,3),(23,0),(1.5,24),(2,4.5),
    (True,24),(0,False),
])
def test_false_population_denominators_prohibited(n,N):
    with pytest.raises(ValueError):
        _rate(n,N)


def test_preregistered_independent_source_gates_included_and_statuses_conservative(actual):
    gs=actual["falsification_gates"]
    assert len(gs)==8
    assert tuple(g["gate"] for g in gs)==GATE_NAMES
    assert all(g["status"] in SEVERITIES for g in gs)
    assert [g["status"] for g in gs]==[
        "PASS_ON_PUBLISHED_SOURCE_SCOPE",
        "NOT_INDEPENDENTLY_VALIDATED",
        "NOT_INDEPENDENTLY_VALIDATED",
        "LIMITED_TO_ORIGINAL_TECHNICAL_EVIDENCE",
        "NOT_INDEPENDENTLY_VALIDATED",
        "NOT_INDEPENDENTLY_VALIDATED",
        "NOT_INDEPENDENTLY_VALIDATED",
        "NOT_INDEPENDENTLY_VALIDATED",
    ]
    assert all(g["support"] and g["not_supported"] and g["next_independent_evidence"] for g in gs)
    assert all("discovery" not in g["status"].lower() for g in gs)


def test_official_primary_literature_provenance_scope_exact_and_non_claiming(actual):
    refs=actual["external_primary_literature_and_provider_docs"]
    assert refs==LITERATURE
    assert refs["luhman_2023_taurus_adopted_member_catalogue"]["doi"]=="10.3847/1538-3881/ac9da3"
    assert refs["mas_2026_gaia_ysos_variability"]["doi"]=="10.1051/0004-6361/202554522"
    assert "one-day" in refs["mas_2026_gaia_ysos_variability"]["role"]
    assert refs["esa_gaia_dr3_ruwe_definition"]["reference_url"].startswith("https://gea.esac.esa.int/")
    assert "bit15" in refs["irsa_ztf_bit15_and_other_source_flags"]["role"]
    assert "catflags=0" in refs["irsa_ztf_bit15_and_other_source_flags"]["role"]
    assert all(x["reference_url"].startswith("https://") for x in refs.values())
    assert all("physical" in x["role"].lower() or "source" in x["role"].lower() or "not" in x["role"].lower() for x in refs.values())


def test_source_fig_is_accessible_non_funnel_three_distinct_original_denominators(actual):
    svg=r5_independent_denominator_svg(actual)
    root=ET.fromstring(svg)
    ns="{http://www.w3.org/2000/svg}"
    assert root.tag==ns+"svg" and root.attrib["role"]=="img"
    assert root.find(ns+"title") is not None and root.find(ns+"desc") is not None
    assert not root.findall(".//"+ns+"script")
    assert not root.findall(".//"+ns+"image")
    groups=[g for g in root.findall(".//"+ns+"g") if g.get("data-panel")]
    assert [g.get("data-denominator") for g in groups]==["24","6","684"]
    observed_rows=root.findall(".//"+ns+"g")
    metrics=[g for g in observed_rows if "data-metric" in g.attrib]
    assert len(metrics)==5+4+3
    assert sum(g.get("data-metric")=="Physical ZTF matches" and g.get("data-count")=="0" for g in metrics)==1
    assert sum(g.get("data-metric")=="Gaia counterparts" and g.get("data-count")=="0" for g in metrics)==1
    assert sum(g.get("data-metric")=="Bit15 accepted" and g.get("data-count")=="591" and g.get("data-base")=="684" for g in metrics)==1
    assert "NOT VERIFIED" in svg
    assert "not a sequential source-survival funnel" in svg.lower()


@pytest.mark.parametrize("key,n,N",[
    ("gaia_positions_with_any_original_ZTF_positional_rows_of_original_24",23,24),
    ("gaia_physically_identified_with_ZTF_of_original_24",1,24),
    ("original_ZTF_exact_oid_dr24_source_csvs_returned_of_six_fixed_oids",4,6),
    ("original_ztf_catflags_bit15_retained_source_rows_of_684",684,684),
    ("original_ztf_catflags_bit15_rejected_source_rows_of_684",0,684),
])
def test_figure_fails_if_source_number_of_matches_or_photometry_changes(actual,key,n,N):
    bad=copy.deepcopy(actual)
    bad["denominator_locked_descriptive_summary_not_population_inference"][key]={"n":n,"N":N,"percent_descriptive_only":round(100*n/N,2)}
    with pytest.raises(ValueError):
        r5_independent_denominator_svg(bad)


@pytest.mark.parametrize("filename,key,value",[
    ("r2","independently_authenticated_physical_gaia_ztf_counterparts",1),
    ("r2","original_journal_table_exact_gaia_ids_and_positions_verified",23),
    ("r2","gaia_only_source_qa_requiring_review",0),
    ("r3","original_success_qc_retained_rows",684),
    ("r3","r3_gaia_target_astrophysical_variability_inference_permitted",True),
    ("r4","real_spectral_window_recovered_from_exact_source_timestamps",True),
    ("r4","source_original_context_24_gaia_id_to_ztf_physical_matches_authenticated",1),
    ("publisher","full_original_24_source_table_verified_from_accepted_origin",False),
])
def test_fake_astrophysical_claim_or_original_source_count_rejected_with_priors_mocked(tmp_path,monkeypatch,filename,key,value):
    files={"r2":r5.R2,"r3":r5.R3,"r4":r5.R4,"publisher":r5.PUBLISHER}
    for path in files.values():
        dest=tmp_path/path
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes((ROOT/path).read_bytes())
    # Reuse genuine original R2/R3/R4 source auditor results, replacing
    # only ONE source of the NEW R5 post-audited reading: the prior auditors
    # themselves have their own adversarial source-tampering tests.
    monkeypatch.setattr(r5,"audit_24_final",lambda root: {"r3_scientific_inference_blocked":True})
    monkeypatch.setattr(r5,"audit_r3_six_original_source_receipts",lambda root:{
        "original_locally_qc_accepted_rows":591,
        "original_masked_catflags_bit15_rows":93,
        "original_raw_ztf_source_rows_quality_inspected":684,
    })
    monkeypatch.setattr(r5,"audit_r4_repo",lambda root:{
        "real_series_with_two_consecutive_365day_empty_bins":2,
        "original_true_one_day_spectral_window_measured":False,
    })
    dest=tmp_path/files[filename]
    obj=json.loads(dest.read_text("utf8"))
    if filename=="r2":
        obj["summary"][key]=value
    else:
        obj[key]=value
    dest.write_text(json.dumps(obj),encoding="utf8")
    with pytest.raises(ValueError):
        r5.build_r5_critical_falsification(tmp_path)


def test_public_references_and_preregistration_are_locally_documented():
    assert (ROOT/"research/taurus_variability/R5_CRITICAL_VALIDATION_SELECTION_LITERATURE_PREREGISTRATION.md").is_file()
    assert (ROOT/"research/taurus_variability/R5_FINAL_CRITICAL_VALIDATION_AND_SELECTION_RESULTS.md").is_file()
    assert (ROOT/"scripts/run_taurus_r5_critical_falsification.py").is_file()
