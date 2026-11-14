"""All test CSV rows are SYNTHETIC: not genuine ZTF measurements.

The live R3 experiment separately queries official IRSA DR24 only AFTER the
fixed original R2 ObjectID and 30-visit/90-day preregistration is committed.
"""
from __future__ import annotations

import copy
import csv
import io
import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

import pytest

from stellarforge.r3_original_oid_coverage import (
    COLLECTION, FIXED_GROUPS, R3_PASS, R3_FAIL,
    MAX_BYTES, MIN_QC_VISITS, MIN_BASELINE_DAYS,
    original_exact_oid_url, validate_frozen_source_groups,
    technical_coverage_from_original_bytes, r3_six_original_oid_qc,
    run_six_from_frozen_repo,
)

ROOT=Path(__file__).resolve().parents[1]
R2_OID=ROOT/"reports/taurus_variability_r2/REAL_TWO_FIELDS_ORIGINAL_IRSA_ALTERNATE_OBJECTIDS_NO_RAW.json"
R2_DECISION=ROOT/"reports/taurus_variability_r2/R2_FINAL_24_TECHNICAL_SOURCE_ACCESS_AND_IDENTITY_DECISION_NO_RAW.json"


def setup_ledgers():
    return json.loads(R2_OID.read_text("utf8")), json.loads(R2_DECISION.read_text("utf8"))


def make_synthetic(oid, band, n=41, day=10, flagged_last=True, clock="mjd"):
    buff=io.StringIO()
    columns=["oid","fid",clock,"mag","magerr","catflags","ra","dec"]
    writer=csv.DictWriter(buff,fieldnames=columns)
    writer.writeheader()
    for i in range(n):
        writer.writerow({"oid":oid,"fid":"1" if band=="g" else "2",
                        clock:round((58300+i*day) + (2400000.5 if clock=="hjd" else 0),6),
                        "mag":"16.5","magerr":"0.025",
                        "catflags":"32768" if flagged_last and i==n-1 else "0",
                        "ra":"65.0","dec":"25.0"})
    return buff.getvalue().encode()


class FakeResponse:
    status=200
    headers={"Content-Type":"text/csv"}
    def __init__(self, data):self.data=data
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def read(self,n):return self.data[:n]


def test_six_original_oid_selection_requires_exact_r2_order_and_gaia_identity_no_go():
    oid,decision=setup_ledgers()
    sel=validate_frozen_source_groups(oid,decision)
    assert len(sel)==6
    assert tuple((x["technical_label"],x["original_gaia_context_id"],x["ztf_oid"],
                  x["ztf_filter"],x["r2_historical_positional_response_rows"])
                 for x in sel)==FIXED_GROUPS
    assert decision["summary"]["independently_authenticated_physical_gaia_ztf_counterparts"]==0
    changed=copy.deepcopy(oid)
    changed["fields"][0]["positional_oid_screen"]["original_ztf_oid_band_groups"][0]["ztf_oid"]="9999999999"
    with pytest.raises(ValueError,match="selection differs"):
        validate_frozen_source_groups(changed,decision)
    changed=copy.deepcopy(decision)
    changed["r3_physical_stellar_variability_analysis_authorized"]=True
    with pytest.raises(ValueError,match="Original 24-source"):
        validate_frozen_source_groups(oid,changed)


def test_exact_original_irsa_query_cannot_contain_position_or_unlisted_oid():
    for name,id,oid,band,n in FIXED_GROUPS:
        u=original_exact_oid_url(oid)
        assert u.startswith("https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?")
        params=parse_qs(urlsplit(u).query)
        assert params=={"ID":[oid],"FORMAT":["csv"],"COLLECTION":[COLLECTION]}
        assert "POS" not in params
    with pytest.raises(ValueError):
        original_exact_oid_url("12345678")


def test_qc_on_synthetic_single_oid_genuine_r1_technical_thresholds():
    oid=FIXED_GROUPS[0][2]
    doc=technical_coverage_from_original_bytes(make_synthetic(oid,"g"),oid=oid,band="g")
    assert doc["status"]=="ORIGINAL_ZTF_EXACT_OID_CSV_PARSED_AND_QC_AUDITED"
    assert doc["raw_original_rows"]==41
    assert doc["qc_accepted_rows"]==40
    assert doc["qc_rejections"]=={"masked_catflags":1}
    assert doc["n_technical_coverage_pass_series"]==1
    assert len(doc["per_oid_band_time_system"])==1
    curve=doc["per_oid_band_time_system"][0]
    assert curve["time_system_as_reported"]=="MJD"
    assert curve["n_locally_qc_accepted_epochs"]==40
    assert curve["time_span_days"]==390
    assert curve["at_least_30_qc_accepted_epochs"]
    assert curve["at_least_90day_baseline"]
    assert curve["technical_oid_coverage_status"]==R3_PASS
    assert curve["physical_gaia_ztf_source_authenticated"] is False
    assert curve["stellar_variability_analysis_authorized"] is False
    assert sum(curve["epochs_per_365day_bin_from_first_accepted_visit"])==40


def test_two_independent_eligibility_gates_30_visits_and_90days():
    oid=FIXED_GROUPS[0][2]
    short=technical_coverage_from_original_bytes(make_synthetic(oid,"g",n=41,day=1,flagged_last=False),oid=oid,band="g")
    assert short["per_oid_band_time_system"][0]["at_least_30_qc_accepted_epochs"] is True
    assert short["per_oid_band_time_system"][0]["at_least_90day_baseline"] is False
    assert short["per_oid_band_time_system"][0]["technical_oid_coverage_status"]==R3_FAIL
    sparse=technical_coverage_from_original_bytes(make_synthetic(oid,"g",n=7,day=40,flagged_last=False),oid=oid,band="g")
    assert sparse["per_oid_band_time_system"][0]["at_least_30_qc_accepted_epochs"] is False
    assert sparse["per_oid_band_time_system"][0]["at_least_90day_baseline"] is True
    assert sparse["per_oid_band_time_system"][0]["technical_oid_coverage_status"]==R3_FAIL


def test_exact_oid_and_band_mismatch_fails_closed_instead_of_merging():
    oid=FIXED_GROUPS[0][2]
    with pytest.raises(ValueError,match="unrequested ObjectID"):
        technical_coverage_from_original_bytes(make_synthetic("123456789012345","g"),oid=oid,band="g")
    with pytest.raises(ValueError,match="filter changed"):
        technical_coverage_from_original_bytes(make_synthetic(oid,"r"),oid=oid,band="g")
    with pytest.raises(ValueError):
        technical_coverage_from_original_bytes(b"<html>ERROR</html>",oid=oid,band="g")
    with pytest.raises(ValueError):
        technical_coverage_from_original_bytes(b"x"*(MAX_BYTES+1),oid=oid,band="g")


def test_hjd_is_not_silently_converted_to_mjd_or_matched_to_star():
    oid=FIXED_GROUPS[0][2]
    q=technical_coverage_from_original_bytes(make_synthetic(oid,"g",clock="hjd"),oid=oid,band="g")
    assert q["per_oid_band_time_system"][0]["time_system_as_reported"]=="HJD"
    assert q["per_oid_band_time_system"][0]["technical_oid_coverage_status"]==R3_PASS


def test_live_orchestration_fake_six_original_responses_no_raw_photometry_persisted():
    oid,decision=setup_ledgers()
    ids={row[2]:row for row in FIXED_GROUPS}
    requests=[]
    def mock(req,timeout):
        assert timeout==40
        parsed=parse_qs(urlsplit(req.full_url).query)
        expected_oid=parsed["ID"][0]
        requests.append(expected_oid)
        row=ids[expected_oid]
        return FakeResponse(make_synthetic(expected_oid,row[3]))
    result=r3_six_original_oid_qc(oid,decision,opener=mock,workers=1)
    assert requests==[x[2] for x in FIXED_GROUPS]
    assert result["n_predeclared_exact_original_ztf_oids_requested"]==6
    assert result["n_original_archive_csv_with_rows_and_valid_qc"]==6
    assert result["n_original_rows_seen_in_valid_exact_oid_csv"]==246
    assert result["n_original_rows_locally_qc_accepted_in_valid_exact_oid_csv"]==240
    assert result["n_qc_accepted_independent_oid_band_clock_technical_coverage_pass"]==6
    assert result["n_physically_eligible_R3_stellar_lightcurves"]==0
    assert result["r3_physical_star_variability_science_go"] is False
    assert result["original_raw_ztf_lightcurve_pixels_photometry_saved_to_disk"] is False
    assert len(result["source_observations"])==6
    assert all(x["original_physical_gaia_ztf_target_source_authenticated"] is False for x in result["source_observations"])
    serialized=json.dumps(result)
    assert "16.5" not in serialized
    assert "per_epoch_magnitudes" not in serialized
    assert "raw_photometry" not in serialized or "raw_photometry_rows_or_magnitudes_saved" in serialized


def test_provider_http_failure_is_source_specific_not_an_astrophysical_nondetection():
    oid,decision=setup_ledgers()
    def mock(req,timeout):
        u=parse_qs(urlsplit(req.full_url).query)["ID"][0]
        if u==FIXED_GROUPS[0][2]:
            raise HTTPError(req.full_url,400,"synthetic request refused",{},None)
        return FakeResponse(make_synthetic(u,next(r[3] for r in FIXED_GROUPS if r[2]==u)))
    z=r3_six_original_oid_qc(oid,decision,opener=mock,workers=2)
    assert z["n_original_archive_csv_with_rows_and_valid_qc"]==5
    assert z["source_observations"][0]["original_archive_query_status"]=="ORIGINAL_PROVIDER_HTTP_ERROR"
    assert z["source_observations"][0]["http_status"]==400
    assert z["n_physically_authenticated_gaia_ztf_sources"]==0
    assert z["n_qc_accepted_independent_oid_band_clock_technical_coverage_pass"]==5


def test_all_network_failures_do_not_create_fake_negative_nonvariables():
    oid,decision=setup_ledgers()
    def mock(req,timeout):
        raise TimeoutError("synthetic offline timeout")
    z=r3_six_original_oid_qc(oid,decision,opener=mock,workers=1)
    assert z["phase"]=="R3_ORIGINAL_ARCHIVE_PILOT_BLOCKED_ALL_SIX_EXACT_OIDS"
    assert z["n_original_archive_csv_with_rows_and_valid_qc"]==0
    assert z["n_qc_accepted_independent_oid_band_clock_technical_coverage_pass"]==0
    assert len(z["source_observations"])==6
    assert z["technical_original_response_status_counts"]=={"ORIGINAL_PROVIDER_NETWORK_FAILURE":6}
    assert z["r3_physical_star_variability_science_go"] is False


def test_repository_runner_synthetic_opener_only_offline():
    ids={x[2]:x for x in FIXED_GROUPS}
    def mock(req,timeout):
        oid=parse_qs(urlsplit(req.full_url).query)["ID"][0]
        return FakeResponse(make_synthetic(oid,ids[oid][3],n=31,day=4))
    output=run_six_from_frozen_repo(ROOT,opener=mock)
    assert len(output["source_observations"])==6
    assert output["n_qc_accepted_independent_oid_band_clock_technical_coverage_pass"]==6
