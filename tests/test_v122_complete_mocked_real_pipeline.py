"""Offline success/failure integration test of exact v1.20 real-pilot orchestration.

Every original source, native catalogue, Gaia, and FITS response is MOCKED.
Passing here validates control flow only, never genuine ZTF observations.
"""
import csv
from zipfile import ZipFile

import numpy as np
import pytest

from scripts import run_v120_original_empirical_psf_pilot as pilot
from stellarforge.v119_empirical_psf_noise import RegisteredStar
from stellarforge.v121_science_falsification import audit_v120_real_source_evidence


TARGET = "3419110734340795648"
OTHER = "149623711269425408"
IDS = tuple(str(3419111000000000001 + x) for x in range(7))
TIMES = (58475.11375, 58849.135984)


def setup_runner(tmp_path, monkeypatch, *, fail_last_two_holdouts=False):
    archive = tmp_path/"fake_original_acquisition.zip"
    with ZipFile(archive, "w") as z:
        z.writestr(f"{TARGET}_IRSA_RAW.csv", "synthetic-original-cida")
        z.writestr(f"{OTHER}_IRSA_RAW.csv", "synthetic-original-ft")
    seed = tmp_path/"synthetic_seed.csv"
    with seed.open("w", newline="") as fp:
        writer = csv.DictWriter(
            fp, fieldnames=["gaia", "ra", "dec", "pmra", "pmdec"])
        writer.writeheader()
        writer.writerows([
            {"gaia": TARGET, "ra": 70, "dec": 20, "pmra": 1, "pmdec": -1},
            {"gaia": OTHER, "ra": 70, "dec": 21, "pmra": 1, "pmdec": -1},
        ])
    exposures = [
        {"target_gaia_id": TARGET, "target": "CIDA 11", "oid": "610106300008010",
         "band": "zg", "mjd": float(time)}
        for time in TIMES
    ] + [
        {"target_gaia_id": OTHER, "target": "FT Tau", "oid": "1605115300003377",
         "band": "zg", "mjd": 58388.389016},
        {"target_gaia_id": OTHER, "target": "FT Tau", "oid": "1605115300003377",
         "band": "zg", "mjd": 58491.18478},
    ]
    monkeypatch.setattr(pilot, "review_irsa_artifact", lambda *a, **kw: {
        "targets": [{"gaia_dr3_source_id": TARGET},
                    {"gaia_dr3_source_id": OTHER}],
        "n_rows": 2212})
    monkeypatch.setattr(pilot, "load_ledger",
                        lambda *a, **kw: {"exposures": exposures})
    monkeypatch.setattr(pilot, "all_required_gaia_ids",
                        lambda *a, **kw: (TARGET, OTHER))
    monkeypatch.setattr(pilot, "download_reference_catalog",
                        lambda *a, **kw: b"synthetic Gaia wide cone")
    monkeypatch.setattr(pilot, "parse_reference_catalog", lambda *a: [])
    monkeypatch.setattr(pilot, "preregister_strict_cohort",
                        lambda *a, **kw: {
        "status": "GAIA_ONLY_STRICT_4_TRAIN_3_HOLDOUT_PREREGISTERED",
        "n_preselected_strict_sources": 7,
        "n_expected_training_sources": 4,
        "n_expected_holdout_sources": 3,
        "training_source_ids": IDS[:4], "holdout_source_ids": IDS[4:],
    })
    monkeypatch.setattr(pilot, "fetch_gaia_astrometry",
                        lambda *a, **kw: b"synthetic exact Gaia astrometry")
    monkeypatch.setattr(pilot, "parse_gaia_astrometry",
                        lambda *a, **kw: {sid: {"id":sid} for sid in IDS})
    monkeypatch.setattr(pilot, "propagate_gaia_5p_formal",
                        lambda g, **kw: {
        "geocentric_parallax_adjusted_ra_deg": 70.0,
        "geocentric_parallax_adjusted_dec_deg": 20.0})
    monkeypatch.setattr(pilot, "stratified_ztf_image_candidates",
                        lambda *a, **kw: [{
        "ztf_oid": "610106300008010", "band": "zg",
        "candidates": [
            {"kind": "science", "mjd": time,
             "url": f"https://irsa.ipac.caltech.edu/ibe/data/ztf/products/sci/synthetic_{int(time)}_sciimg.fits?center=70,20&size=60arcsec"}
            for time in TIMES],
    }])
    monkeypatch.setattr(pilot, "official_psf_product_url",
                        lambda *a, **kw: "https://synthetic.not-external.test/cat")
    monkeypatch.setattr(pilot, "fetch_native_psf_product",
                        lambda *a, **kw: b"synthetic native PSF catalogue")
    monkeypatch.setattr(pilot, "parse_psf_fit_catalogue",
                        lambda *a, **kw: {
        "sha256": "a"*64,
        "rows": {
            "sourceid": np.arange(1, 8),
            "ra": np.full(7, 70.), "dec": np.full(7, 20.),
            "xpos": np.full(7, 1500.25), "ypos": np.full(7, 1500.3),
        }})
    monkeypatch.setattr(pilot, "screen_fixed_cohort_native_catalogue",
                        lambda *a, **kw: {
        "n_native_training_candidates": 4,
        "n_native_holdout_candidates": 3,
        "train_screens": [
            {"status": pilot.CAT_OK, "gaia_source_id": sid,
             "ztf_native_per_exposure_sourceid": j+1}
            for j, sid in enumerate(IDS[:4])],
        "holdout_screens": [
            {"status": pilot.CAT_OK, "gaia_source_id": sid,
             "ztf_native_per_exposure_sourceid": j+5}
            for j, sid in enumerate(IDS[4:])],
    })
    monkeypatch.setattr(pilot, "retarget_same_ztf_exposure",
                        lambda *a, **kw: "https://synthetic.not-external.test/science")
    monkeypatch.setattr(pilot, "official_ancillary_url",
                        lambda *a, **kw: "https://synthetic.not-external.test/mask")
    monkeypatch.setattr(pilot, "fetch_fits_cutout", lambda *a, **kw: b"sci")
    monkeypatch.setattr(pilot, "fetch_ancillary_fits", lambda *a, **kw: b"mask")
    coords = np.arange(-11, 12, dtype=float)
    xx, yy = np.meshgrid(coords, coords)
    p = np.exp(-(xx**2 + yy**2) / (2*1.4**2))
    p /= p.sum()
    rng = np.random.default_rng(122)
    def star(science, mask, *, gaia_source_id, exposure_id, **kw):
        if fail_last_two_holdouts and gaia_source_id in IDS[-2:]:
            raise ValueError("Synthetic rejected mask core")
        image = 210 + 14000*p + rng.normal(0, 2, p.shape)
        return (RegisteredStar(
            gaia_source_id=gaia_source_id, exposure_id=exposure_id,
            pixels_dn=image, mask_bits=np.zeros(p.shape, dtype=np.uint16)), {})
    monkeypatch.setattr(pilot, "registered_star_from_masked_original_fits", star)
    return archive, seed


def test_complete_synthetic_original_pilot_control_flow_both_epochs(tmp_path, monkeypatch):
    path, seed = setup_runner(tmp_path, monkeypatch)
    observed = pilot.run(path, seed=seed, ledger_file=tmp_path/"mock_ledger")
    assert observed["n_original_exposures_with_empirical_whole_star_holdout_completed"] == 2
    assert len(observed["frames"]) == 2
    assert all(f["n_registered_train"] == 4 for f in observed["frames"])
    assert all(f["n_registered_holdout"] == 3 for f in observed["frames"])
    assert all(f["empirical_psf_status"] ==
               "INTERNAL_DISTINCT_STAR_PSF_HOLDOUT_COMPLETED"
               for f in observed["frames"])
    assert observed["independent_survey_psf_or_wcs_calibration_completed"] is False
    science_gate = audit_v120_real_source_evidence(observed)
    assert science_gate["n_original_frames_with_internal_distinct_star_model"] == 2
    assert science_gate["independent_original_survey_psf_calibrated"] is False
    assert not any(sid in str(observed) for sid in IDS)


def test_synthetic_original_pilot_no_replacement_after_holdout_mask_reject(
    tmp_path, monkeypatch,
):
    path, seed = setup_runner(
        tmp_path, monkeypatch, fail_last_two_holdouts=True)
    observed = pilot.run(path, seed=seed, ledger_file=tmp_path/"mock_ledger")
    assert observed["n_original_exposures_with_empirical_whole_star_holdout_completed"] == 0
    assert all(f["n_registered_train"] == 4 for f in observed["frames"])
    assert all(f["n_registered_holdout"] == 1 for f in observed["frames"])
    assert all(f["empirical_psf_status"] ==
               "REAL_SOURCE_MASKED_STAMP_3_PLUS_2_GATE_NOT_MET"
               for f in observed["frames"])
    audit = audit_v120_real_source_evidence(observed)
    assert audit["n_original_frames_with_internal_distinct_star_model"] == 0
    assert audit["new_companion_or_variability_confirmed"] is False
