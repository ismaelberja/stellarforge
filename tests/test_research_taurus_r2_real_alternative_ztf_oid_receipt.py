"""Lock the genuine FT Tau/CIDA11 two-field ZTF alternate OID run and limits."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/"reports/taurus_variability_r2/REAL_TWO_FIELDS_ORIGINAL_IRSA_ALTERNATE_OBJECTIDS_NO_RAW.json"
RECEIPT=ROOT/"reports/taurus_variability_r2/REAL_ALTERNATIVE_ZTF_OID_ORIGINAL_RUN_RECEIPT.json"
REPORT=ROOT/"research/taurus_variability/R2_REAL_FT_TAU_CIDA_ZTF_ALTERNATIVE_OID_RESULTS.md"

def test_original_gaia_ztf_source_artifact_sha_and_counts():
    j=json.loads(LEDGER.read_text("utf8"))
    r=json.loads(RECEIPT.read_text("utf8"))
    assert hashlib.sha256(LEDGER.read_bytes()).hexdigest()==r["original_json_sha256"]
    assert r["live_original_survey_run_id"]==43066226324
    assert r["original_derived_artifact_id"]==13875728278
    assert r["original_artifact_zip_sha256"]==(
        "e607eaf67de0d4915ff56e46300b99cc66d10dde6b37ad1b8580a32c6e236612")
    assert r["gaia_dr3_original_source_response_sha256"]==(
        j["original_gaia_dr3_exact_two_id_response_sha256"])
    assert j["n_frozen_nonrepresentative_taurus_gaia_sources"]==24
    assert j["n_fixed_historic_target_fields"]==2
    assert j["n_positional_irsa_2arcsec_queries_parsed"]==2
    assert j["n_direct_original_historic_oid_queries_parsed"]==2
    assert j["n_original_ztf_oid_groups_reviewed"]==6
    assert j["n_fields_with_multiple_original_ztf_oids_same_band"]==1
    assert j["n_fields_with_historic_oid_in_positional_response"]==2
    assert j["n_historic_ztf_science_epochs_added"]==0
    assert j["n_new_original_ztf_science_fits_or_mask_products_fetched"]==0
    assert j["source_identity_science_R2_completed"] is False
    assert j["n_physical_gaia_to_ztf_object_identifications_confirmed"]==0
    assert j["n_confirmed_new_ztf_stellar_variables_or_companions"]==0


def test_genuine_ft_tau_has_two_same_band_oid_pairs_across_two_fields():
    j=json.loads(LEDGER.read_text("utf8"))
    r=json.loads(RECEIPT.read_text("utf8"))
    ft=j["fields"][0]
    assert ft["target"]=="FT Tau"
    assert ft["gaia_dr3_id"]=="149623711269425408"
    assert ft["historic_original_ztf_oid"]=="1605115300003377"
    assert ft["historic_oid_present_in_2arcsec_positional_query"] is True
    p=ft["positional_oid_screen"]
    assert p["n_original_positional_table_rows"]==1442
    assert p["n_quality_accepted_photometric_rows"]==1199
    assert p["n_original_distinct_ztf_oids"]==4
    assert p["n_original_oid_band_groups"]==4
    assert p["n_original_oid_pairs_in_same_band"]==2
    assert p["n_same_band_oid_pairs_sharing_exact_original_exposure_metadata"]==0
    assert r["ft_tau"]["g_ztf_oids"]==[
        "1605115300003377","609108400001155"]
    assert r["ft_tau"]["r_ztf_oids"]==[
        "1605215300005161","609208400001969"]
    assert {tuple(x["original_field_ccd_quadrant_labels"])
            for x in p["original_ztf_oid_band_groups"]}=={
                ("1605/0xf/0x3",),("609/0x8/0x4",)}
    assert all(not x["same_physical_star_established"]
               and not x["different_physical_stars_established"]
               for x in p["same_band_multiple_oid_review_pairs"])
    assert ft["historic_oid_direct_screen"]["n_original_oid_rows"]==79


def test_genuine_cida11_has_g_and_r_only_under_this_original_query():
    j=json.loads(LEDGER.read_text("utf8"))
    r=json.loads(RECEIPT.read_text("utf8"))
    c=j["fields"][1]
    assert c["target"]=="CIDA 11"
    assert c["gaia_dr3_id"]=="3419110734340795648"
    assert c["historic_original_ztf_oid"]=="610106300008010"
    assert c["historic_oid_present_in_2arcsec_positional_query"] is True
    p=c["positional_oid_screen"]
    assert p["n_original_positional_table_rows"]==1206
    assert p["n_quality_accepted_photometric_rows"]==1013
    assert p["n_original_distinct_ztf_oids"]==2
    assert p["n_original_oid_pairs_in_same_band"]==0
    assert {tuple(x["original_field_ccd_quadrant_labels"])
            for x in p["original_ztf_oid_band_groups"]}=={
                ("610/0x6/0x3",)}
    assert r["cida11"]["g_ztf_oids"]==["610106300008010"]
    assert r["cida11"]["r_ztf_oids"]==["610206300011997"]
    assert c["historic_oid_direct_screen"]["n_original_oid_rows"]==469
    assert r["cida11"]["gaia_dr3_high_ruwe_warning"] is True


def test_original_frozen_science_nondiscovery_protection_and_counts():
    j=json.loads(LEDGER.read_text("utf8"))
    r=json.loads(RECEIPT.read_text("utf8"))
    groups=[g for f in j["fields"]
            for g in f["positional_oid_screen"]["original_ztf_oid_band_groups"]]
    assert len(groups)==6
    assert sum(g["n_original_raw_table_rows"] for g in groups)==2648
    assert sum(g["n_quality_accepted_epoch_rows"] for g in groups)==2212
    assert all(not g["gaia_ztf_physical_identity_confirmed"] for g in groups)
    assert all(f["gaia_original_source_available"] for f in j["fields"])
    assert all(not f["original_gaia_ztf_physical_identity_confirmed"]
               and not f["scientific_variability_confirmed"]
               for f in j["fields"])
    assert r["n_independently_validated_gaia_ztf_physical_sources"]==0
    assert r["n_new_confirmed_variable_stars"]==0
    assert r["n_new_confirmed_companions"]==0
    assert r["r2_scientific_physical_source_identification_completed"] is False
    assert r["raw_ztf_photometry_or_gaia_table_saved"] is False
    s=LEDGER.read_text("utf8")
    for forbidden in ('"mag":','"magerr":','"mjd":','"fits_data":',
                      '"original_full_csv":','"flux":'):
        assert forbidden not in s


def test_literature_report_stays_explicit_about_crowding_and_oid_ambiguity():
    s=REPORT.read_text("utf8")
    for token in ("1,442","1,206","2,648","2,212",
                  "1605115300003377","609108400001155",
                  "1605215300005161","609208400001969",
                  "610106300008010","610206300011997"):
        assert token in s
    assert "**Do not merge" in s
    assert "**R2 technical" in s
    assert "0" in s
    assert "RUWE" in s
