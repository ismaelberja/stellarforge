"""v1.18 training log and FT Tau exploratory Gaia source safeguards."""
from __future__ import annotations

import math
from urllib.error import HTTPError
import pytest

from stellarforge.v118_original_training_log_fttau import (
    official_processing_log_url,validate_processing_log_url,
    fetch_original_processing_log,audit_psf_training_log,
    audit_exposure_training_logs,
    select_exploratory_ft_tau_gaia_controls,
)

SCIENCE=("https://irsa.ipac.caltech.edu/ibe/data/ztf/products/sci/"
         "2018/0411/467847/ztf_20180411467847_000535_zr_c11_o_q3_sciimg.fits"
         "?center=65.91332400%2C24.93719500&size=45arcsec&gzip=false")
RA=65.913324
DEC=24.937195
TARGET="149623711269425408"
OLD={TARGET,"149623711269425410","149623711269425420"}


def star(sid,dx=0,dy=0,*,g=15.5,snr=100,ruwe=1.2,dup=False,solved=31,
         pmra=1.,parallax=4.):
    return {"source_id":str(sid),
        "ra":RA+dx/(3600*math.cos(math.radians(DEC))),
        "dec":DEC+dy/3600,
        "g_mag":g,"g_flux_snr":snr,"ruwe":ruwe,
        "duplicated_source":dup,"astrometric_params_solved":solved,
        "pmra":pmra,"pmdec":1.,"parallax":parallax,
        "ra_error_mas":0.6,"dec_error_mas":.6,
        "pmra_error_mas_yr":.4,"pmdec_error_mas_yr":.4}


def fresh_rows():
    return [
        star(TARGET),
        star("149623711269425410",110,90),
        star("149623711269425420",-100,-110),
        star("10001",55,65),star("10002",-55,65),
        star("10003",65,-75),star("10004",-65,-65),
        star("10005",8,11),
    ]


def test_true_original_science_logs_derivation_with_no_source_cutout_query():
    for kind in ("sciimlog.txt","log.txt"):
        u=official_processing_log_url(SCIENCE,kind)
        assert u.endswith("_"+kind)
        assert "size=" not in u
        assert "center=" not in u
        validate_processing_log_url(u,kind)


@pytest.mark.parametrize("bad",[
    SCIENCE.replace("irsa.ipac.caltech.edu","example.com"),
    SCIENCE.replace("https://","http://"),
    SCIENCE.replace("_sciimg.fits","_mskimg.fits"),
    SCIENCE.replace("size=45arcsec","size=1000arcsec"),
])
def test_unauthorized_original_source_for_log_prohibited(bad):
    with pytest.raises(ValueError):
        official_processing_log_url(bad,"sciimlog.txt")


def test_processing_log_parser_counts_psf_mentions_but_does_not_identify_stars():
    raw=b"ZTF observational process\nPSF stars selected: 170\nDAOPhot finished\nAllStar completed\n"
    d=audit_psf_training_log(raw,product="sciimlog.txt")
    assert d["n_lines_mentioning_psf_or_daophot"]>=3
    assert d["aggregate_psf_star_count_values_seen"]==[170]
    assert len(d["original_log_sha256"])==64
    assert d["original_psf_training_star_membership_recovered"] is False
    assert d["new_gaia_control_ids_confirmed_absent_from_psf_training"]==0


def test_a_named_psf_sourceid_in_log_is_still_not_gaia_identity_without_namespace():
    raw=b"DAOPHOT PSF selected sources 123456 654321\n"
    d=audit_psf_training_log(raw,product="log.txt")
    assert d["individual_training_source_id_namespace_documented"] is False
    assert d["source_membership_scientific_status"]=="NOT_VERIFIABLE_FROM_THIS_LOG"


def test_error_page_rejected_as_original_psf_log():
    with pytest.raises(ValueError):
        audit_psf_training_log(b"<html>502 upstream error</html>",product="log.txt")


def test_foreign_redirect_is_rejected_by_bounded_ztf_processing_log_download():
    class Page:
        def __enter__(self):return self
        def __exit__(self,*args):return False
        def geturl(self):return "https://example.com/secret"
        def read(self,n):return b"DAOPhot original log content"
    u=official_processing_log_url(SCIENCE,"sciimlog.txt")
    with pytest.raises(ValueError):
        fetch_original_processing_log(
            u,product="sciimlog.txt",
            opener=lambda req,timeout:Page())


def test_http503_maintains_unknown_training_star_membership_status():
    def outage(url,*,product,timeout):
        raise HTTPError(url,503,"busy",None,None)
    x=audit_exposure_training_logs(SCIENCE,fetch=outage)
    assert x["n_original_processing_logs_read"]==0
    assert x["n_official_psf_training_source_rosters_authenticated"]==0
    assert x["model_training_star_membership_established"] is False
    assert all(a["http_status"]==503 for a in x["original_log_product_results"])


def test_accessible_processing_logs_never_falsely_grant_psf_independence():
    def good(url,*,product,timeout):
        return b"ZTF PSF stars selected: 300\nDAOPhot lookup solved\n"
    x=audit_exposure_training_logs(SCIENCE,fetch=good)
    assert x["n_original_processing_logs_read"]==2
    assert x["n_official_psf_training_source_rosters_authenticated"]==0
    assert not x["model_training_star_membership_established"]


def test_exploratory_tier_selects_only_new_gaia_ids_and_covers_four_quadrants():
    s=select_exploratory_ft_tau_gaia_controls(
        fresh_rows(),target_id=TARGET,excluded_source_ids=OLD)
    assert s["n_exploratory_controls_selected"]==4
    assert s["n_control_sky_quadrants"]==4
    assert not OLD&{x["source_id"] for x in s["controls"]}
    assert not s["same_eligibility_as_original_v117_strict_controls"]
    assert all(c["tier"]=="EXPLORATORY_NOT_EQUIVALENT_TO_STRICT_V117"
               for c in s["controls"])


@pytest.mark.parametrize("change",[
    {"g":11},{"g":20},{"snr":12},{"ruwe":1.7},{"dup":True},
    {"solved":3},{"pmra":None},{"parallax":None},
])
def test_exploratory_gaia_tier_rejects_poor_quality(change):
    r=[star(TARGET),star("10001",80,60,**change),star("10002",-80,-60)]
    s=select_exploratory_ft_tau_gaia_controls(
        r,target_id=TARGET,excluded_source_ids={TARGET})
    assert "10001" not in {a["source_id"] for a in s["controls"]}
    assert "10002" in {a["source_id"] for a in s["controls"]}


def test_gaia_source_with_bad_neighbour_within_six_arcsec_is_not_isolated():
    r=fresh_rows()+[star("999999",55+2,65+1,g=21,ruwe=2)]
    s=select_exploratory_ft_tau_gaia_controls(
        r,target_id=TARGET,excluded_source_ids=OLD)
    assert "10001" not in {a["source_id"] for a in s["controls"]}
    assert s["exclusion_reasons"]["closer_than_6arcsec_Gaia_neighbour"]>=1


def test_gaia_duplicate_source_id_blocks_exploratory_source_preselection():
    with pytest.raises(ValueError,match="Duplicate"):
        select_exploratory_ft_tau_gaia_controls(
            [star(TARGET),star("1",80,60),star("1",-80,-60)],
            target_id=TARGET,excluded_source_ids={TARGET})


def test_exploratory_stratum_does_not_make_false_ztf_source_claim_for_empty_field():
    s=select_exploratory_ft_tau_gaia_controls(
        [star(TARGET)],target_id=TARGET,excluded_source_ids={TARGET})
    assert s["status"]=="NO_FT_TAU_EXPLORATORY_GAIA_CONTROLS"
    assert s["controls"]==[]
    assert s["physical_gaia_ztf_source_ids_confirmed"]==0


def test_old_target_source_is_required_in_exclusion_design():
    with pytest.raises(ValueError):
        select_exploratory_ft_tau_gaia_controls(
            fresh_rows(),target_id=TARGET,excluded_source_ids=set())


def test_missing_target_in_widecone_is_not_claimed_as_physical_nondetection():
    s=select_exploratory_ft_tau_gaia_controls(
        [star("999999",80,80)],target_id=TARGET,excluded_source_ids={TARGET})
    assert s["status"]=="FT_TAU_GAIA_TARGET_NOT_IN_INDEPENDENT_WIDE_CONE"
    assert s["n_exploratory_controls_selected"]==0
