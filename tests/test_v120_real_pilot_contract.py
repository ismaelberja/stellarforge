"""v1.20 manual-only runner safeguards: offline mocked archive, no real HTTP."""
import csv
import hashlib
from zipfile import ZipFile

import pytest

from scripts import run_v120_original_empirical_psf_pilot as pilot


def row(sid, *, ra="70", dec="20"):
    return {"gaia": sid, "ra": ra, "dec": dec, "pmra": "0", "pmdec": "0"}


def test_manual_real_runner_fails_closed_on_insufficient_strict_gaia_stars(
    tmp_path, monkeypatch,
):
    target = pilot.TARGET_ID
    other = "149623711269425408"
    seed = tmp_path / "seed.csv"
    with seed.open("w", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=["gaia","ra","dec","pmra","pmdec"])
        writer.writeheader()
        writer.writerows([row(target), row(other)])
    archive = tmp_path / "pretend_original.zip"
    with ZipFile(archive, "w") as z:
        z.writestr("pretend.txt", "synthetic only")
    monkeypatch.setattr(pilot, "review_irsa_artifact", lambda *a: {
        "targets": [
            {"gaia_dr3_source_id": target},
            {"gaia_dr3_source_id": other},
        ],
        "n_rows": 2212})
    ledger = {
        "exposures": [
            {"target_gaia_id": target, "band": "zg"} for _ in range(2)
        ] + [{"target_gaia_id": other, "band": "zg"} for _ in range(2)]}
    monkeypatch.setattr(pilot, "load_ledger", lambda *a: ledger)
    monkeypatch.setattr(pilot, "all_required_gaia_ids",
                        lambda *a: (target, other))
    monkeypatch.setattr(pilot, "download_reference_catalog",
                        lambda *a, **kw: b"synthetic GAIA CSV")
    # Deliberately no qualifying stars; never attempt original native ZTF.
    monkeypatch.setattr(pilot, "parse_reference_catalog", lambda *a: [{
        "source_id": target, "ra": 70., "dec": 20.,
    }])
    def fail_if_requested(*a, **kw):
        raise AssertionError("Do not query native ZTF before preregistration")
    monkeypatch.setattr(pilot, "fetch_gaia_astrometry", fail_if_requested)
    monkeypatch.setattr(pilot, "fetch_native_psf_product", fail_if_requested)
    result = pilot.run(archive, seed=seed, ledger_file=tmp_path/"no_real_ledger")
    assert result["status"] == "INSUFFICIENT_STRICT_GAIA_BEFORE_ZTF_DATA"
    assert result["frames"] == []
    assert result["new_empirical_model_tested_on_real_original_ztf_pixels"] is False
    assert not result["astronomical_discovery_claimed"]


def test_markdown_only_reports_predeclared_aggregate_no_private_ids():
    r = {
        "status": "OBSERVATIONAL_ELIGIBILITY_AUDIT_ONLY",
        "frames": [{
            "mjd": 58475.11375, "n_native_train": 4,
            "n_native_holdout": 2, "n_registered_train": 3,
            "n_registered_holdout": 2,
            "empirical_psf_status": "REAL_SOURCE_MASKED_STAMP_3_PLUS_2_GATE_NOT_MET",
        }],
    }
    report = pilot.render_markdown(r)
    assert "58475.113750" in report
    assert "no independent instrument calibration" in report
    assert "train" in report
    assert "Gaia-ZTF" in report
    assert "3419110734340795648" not in report


def test_missing_original_exposure_provenance_is_rejected_prior_to_ztf(tmp_path, monkeypatch):
    archive = tmp_path / "missing.zip"
    with ZipFile(archive, "w") as z:
        z.writestr("synthetic", "not actual archive")
    monkeypatch.setattr(pilot, "review_irsa_artifact",
                        lambda *a: {"targets": [{"gaia_dr3_source_id": pilot.TARGET_ID}]})
    monkeypatch.setattr(pilot, "load_ledger", lambda *a: {"exposures": []})
    with pytest.raises(ValueError, match="provenance"):
        pilot.run(archive, seed=tmp_path/"missing.csv")
