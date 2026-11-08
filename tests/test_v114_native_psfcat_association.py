"""v1.14 synthetic official ZTF PSF-fit FITS/DAOPhot source-quality gates."""
from __future__ import annotations

import io
from urllib.error import HTTPError
import numpy as np
import pytest
from astropy.io import fits

from stellarforge.v114_native_psfcat_association import (
    CATALOGUE_BYTES_MAX,BAD_MASK_BITS,
    official_psf_product_url,validate_original_psf_url,
    fetch_native_psf_product,parse_psf_fit_catalogue,
    screen_psf_catalogue_targets,inspect_spatial_daophot_product,
    audit_original_psf_catalogue,audit_original_spatial_psf,
)

SCIENCE=("https://irsa.ipac.caltech.edu/ibe/data/ztf/products/sci/"
         "2018/0411/467847/ztf_20180411467847_000535_zr_c11_o_q3_sciimg.fits"
         "?center=65.91332400%2C24.93719500&size=45arcsec&gzip=false")
RA=65.913324
DEC=24.937195


def prediction(sid="149623711269425408",ra=RA,dec=DEC):
    return {"source_id":sid,"geocentric_parallax_adjusted_ra_deg":ra,
            "geocentric_parallax_adjusted_dec_deg":dec}


def rows(default_flags=0):
    return [
        {"sourceid":1,"xpos":34.1,"ypos":119.2,"ra":RA,"dec":DEC,
         "flux":5000.,"sigflux":100.,"mag":-9.24,"sigmag":.0217,
         "snr":50.,"chi":1.0,"sharp":.1,"flags":default_flags},
        {"sourceid":2,"xpos":290.1,"ypos":300.2,"ra":RA+.01,"dec":DEC+.01,
         "flux":1000.,"sigflux":80.,"mag":-7.5,"sigmag":.09,
         "snr":12.5,"chi":1.1,"sharp":0.0,"flags":0},
    ]


def psfcat(source_rows=None,*,drop_column=None):
    source_rows=rows() if source_rows is None else source_rows
    names=("sourceid","xpos","ypos","ra","dec","flux","sigflux",
           "mag","sigmag","snr","chi","sharp","flags")
    cols=[]
    for col in names:
        if col==drop_column:continue
        fmt="K" if col in ("sourceid","flags") else "D"
        cols.append(fits.Column(name=col,format=fmt,
                    array=[x[col] for x in source_rows]))
    hdul=fits.HDUList([fits.PrimaryHDU(),
                       fits.BinTableHDU.from_columns(cols)])
    stream=io.BytesIO()
    hdul.writeto(stream)
    return stream.getvalue()


def test_official_full_catalogue_and_spatial_psf_url_preserves_original_exposure():
    cat=official_psf_product_url(SCIENCE,"psfcat.fits")
    dao=official_psf_product_url(SCIENCE,"sciimgdao.psf")
    assert cat.endswith("_q3_psfcat.fits")
    assert dao.endswith("_q3_sciimgdao.psf")
    assert "center=" not in cat
    validate_original_psf_url(cat,"psfcat.fits")
    validate_original_psf_url(dao,"sciimgdao.psf")


@pytest.mark.parametrize("bad",[
    SCIENCE.replace("irsa.ipac.caltech.edu","example.net"),
    SCIENCE.replace("https://","http://"),
    SCIENCE.replace("size=45arcsec","size=9000arcsec"),
    SCIENCE.replace("_sciimg.fits","_psfcat.fits"),
])
def test_original_product_bad_input_cannot_be_used(bad):
    with pytest.raises(ValueError):
        official_psf_product_url(bad,"psfcat.fits")


def test_catalogue_has_complete_native_psf_columns_and_unique_source_rows():
    p=parse_psf_fit_catalogue(psfcat())
    assert p["status"]=="ORIGINAL_ZTF_PSF_CATALOGUE_PARSED_UNVERIFIED"
    assert p["n_native_psf_catalogue_rows"]==2
    assert len(p["sha256"])==64


def test_single_clean_psf_entry_is_candidate_not_physical_crossmatch():
    c=parse_psf_fit_catalogue(psfcat())
    result=screen_psf_catalogue_targets(c,[prediction()])
    assert result["n_provisional_unique_nearest_source_candidates"]==1
    s=result["screens"][0]
    assert s["status"]=="PROVISIONAL_CATALOGUE_NEAREST_AND_PROFILE_SCREEN_PASSED"
    assert s["nearest_source_separation_arcsec"]==pytest.approx(0)
    assert s["psf_fit_profile_quality_screen_passed"] is True
    assert s["astrophysical_source_identity_confirmed"] is False
    assert s["source_local_psf_evaluated"] is False
    assert result["calibrated_ztf_detector_wcs_accuracy"] is False


def test_local_second_source_within_3arcsec_makes_source_ambiguous():
    r=rows()
    r[1]["ra"]=RA+.0004
    r[1]["dec"]=DEC
    result=screen_psf_catalogue_targets(
        parse_psf_fit_catalogue(psfcat(r)),[prediction()])
    s=result["screens"][0]
    assert s["status"]=="MULTIPLE_NATIVE_PSF_SOURCES_WITHIN_CROWDING_RADIUS_REVIEW"
    assert s["ztf_source_neighbour_within_3arcsec"] is True
    assert result["n_provisional_unique_nearest_source_candidates"]==0


@pytest.mark.parametrize("patch",[
    {"chi":3.5},{"chi":.2},{"sharp":1.5},{"sharp":-1.4},
    {"snr":2.},{"flags":256},{"flags":-1},{"flux":-5.},{"sigflux":0.},
])
def test_bad_ztf_psf_quality_profile_or_mask_bits_do_not_pass(patch):
    r=rows()
    r[0].update(patch)
    result=screen_psf_catalogue_targets(
        parse_psf_fit_catalogue(psfcat(r)),[prediction()])
    assert result["n_provisional_unique_nearest_source_candidates"]==0
    assert result["screens"][0]["status"]=="NATIVE_PSF_FIT_PROFILE_OR_FLAG_REVIEW_REQUIRED"
    assert result["independent_gaia_ztf_source_crossmatches_confirmed"]==0


def test_no_native_psf_catalog_source_within_one_arcsec_is_not_a_nondetection():
    r=screen_psf_catalogue_targets(
        parse_psf_fit_catalogue(psfcat()),
        [prediction(ra=RA+.003,dec=DEC)])
    assert r["screens"][0]["status"]=="NO_PSF_CATALOGUE_ENTRY_WITHIN_RADIUS"
    assert r["n_provisional_unique_nearest_source_candidates"]==0


def test_one_native_source_is_never_assigned_to_two_gaia_source_ids():
    r=screen_psf_catalogue_targets(
        parse_psf_fit_catalogue(psfcat()),
        [prediction("149623711269425408",ra=RA),
         prediction("149623505110996992",ra=RA+.00001)])
    assert all(x["status"]=="SAME_ZTF_PSF_SOURCE_ASSIGNED_TO_MULTIPLE_GAIA_IDS"
               for x in r["screens"])
    assert r["n_provisional_unique_nearest_source_candidates"]==0
    assert not r["screens"][0]["source_assignment_unique"]


def test_duplicate_gaia_request_is_invalid():
    with pytest.raises(ValueError,match="Duplicate Gaia"):
        screen_psf_catalogue_targets(
            parse_psf_fit_catalogue(psfcat()),[prediction(),prediction()])


def test_missing_official_psf_catalogue_columns_fails_closed():
    with pytest.raises(ValueError,match="Incomplete"):
        parse_psf_fit_catalogue(psfcat(drop_column="sharp"))


def test_duplicate_native_psf_source_identifier_fails_closed():
    r=rows()
    r[1]["sourceid"]=r[0]["sourceid"]
    with pytest.raises(ValueError,match="Duplicate"):
        parse_psf_fit_catalogue(psfcat(r))


def test_invalid_psf_catalogue_sky_position_fails_closed():
    r=rows()
    r[0]["ra"]=361.
    with pytest.raises(ValueError,match="invalid ICRS"):
        parse_psf_fit_catalogue(psfcat(r))


def test_empty_psf_catalogue_explicitly_no_verified_source():
    raw=psfcat([])
    parsed=parse_psf_fit_catalogue(raw)
    result=screen_psf_catalogue_targets(parsed,[prediction()])
    assert parsed["n_native_psf_catalogue_rows"]==0
    assert result["screens"][0]["status"]=="NO_PSF_CATALOGUE_ENTRY_WITHIN_RADIUS"


def test_uncertain_remote_catalogue_http_503_is_transport_not_nondetection():
    def fail(url,*,kind,timeout):
        raise HTTPError(url,503,"server down",None,None)
    r=audit_original_psf_catalogue(SCIENCE,[prediction()],fetch=fail)
    assert r["status"]=="ZTF_ORIGINAL_PSF_CATALOGUE_UNAVAILABLE_OR_UNUSABLE"
    assert r["http_status"]==503
    assert r["independent_gaia_ztf_source_crossmatches_confirmed"]==0


def test_full_native_psf_catalogue_fetch_good_bounds_no_raw_publish():
    def download(url,*,kind,timeout):
        assert url.endswith("_psfcat.fits")
        return psfcat()
    r=audit_original_psf_catalogue(SCIENCE,[prediction()],fetch=download)
    assert r["status"]=="ZTF_ORIGINAL_PSF_CATALOGUE_SCREEN_COMPLETED"
    assert r["n_native_original_catalogue_rows"]==2
    assert r["screens"][0]["astrophysical_source_identity_confirmed"] is False
    assert "rows" not in r


def test_daophot_spatial_model_only_has_provenance_not_spatial_evaluation():
    raw=b"DAOPhot PSF prototype\n"*12
    d=inspect_spatial_daophot_product(raw)
    assert d["status"]=="NATIVE_DAOPHOT_SPATIAL_PSF_DOWNLOADED_FORMAT_NOT_EVALUATED"
    assert d["spatial_psf_model_decoded"] is False
    assert d["source_specific_psf_evaluated"] is False
    assert len(d["sha256"])==64


def test_daophot_http_503_is_not_native_source_psf():
    def fail(url,*,kind,timeout):
        raise HTTPError(url,503,"archive busy",None,None)
    d=audit_original_spatial_psf(SCIENCE,fetch=fail)
    assert d["status"]=="NATIVE_DAOPHOT_PSF_UNAVAILABLE_OR_INVALID"
    assert d["http_status"]==503
    assert d["source_specific_psf_evaluated"] is False


def test_forged_catalogue_html_payload_rejected():
    with pytest.raises(ValueError):
        parse_psf_fit_catalogue(b"<html>Error</html>")


def test_request_rejects_redirect_to_untrusted_host():
    cat=official_psf_product_url(SCIENCE,"psfcat.fits")
    class Response:
        def __enter__(self):return self
        def __exit__(self,*args):return False
        def geturl(self):return "https://example.net/malicious"
        def read(self,n):return psfcat()
    with pytest.raises(ValueError,match="Unsafe"):
        fetch_native_psf_product(
            cat,kind="psfcat.fits",opener=lambda req,timeout:Response())


def test_big_download_cannot_be_silently_parsed():
    with pytest.raises(ValueError):
        parse_psf_fit_catalogue(b"SIMPLE  ="+b" "*CATALOGUE_BYTES_MAX)
