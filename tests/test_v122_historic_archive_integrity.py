"""v1.22 synthetic ZIP fixtures, no original real Gaia/ZTF data in Git."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

import pytest
from scripts.check_v122_historic_source_zip import (
    inspect_archive, PINNED_ORIGINAL_ACTIONS_ZIP_SHA256, EXPECTED_NAMES,
)


IDS = ("149623711269425408", "3419110734340795648")


def fixture_archive(path, *, altered=None, extra=None, link=False):
    raw = {i: f"synthetic raw group {i}\n".encode() for i in IDS}
    manifest = {
        "raw_photometry_responses": 2,
        "verified_gaia_ztf_crossmatches": 0,
        "source_release_independently_authenticated": False,
        "results": [
            {"gaia_dr3_id": i, "raw_bytes": len(raw[i]),
             "raw_sha256": hashlib.sha256(raw[i]).hexdigest()}
            for i in IDS
        ]
    }
    if altered is not None:
        altered(manifest, raw)
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as z:
        for i in IDS:
            z.writestr(f"{i}_IRSA_RAW.csv", raw[i])
        z.writestr("PILOT_STATUS.json", json.dumps(manifest))
        z.writestr("REPORT.md", "Synthetic test only; no real data.\n")
        if extra is not None:
            z.writestr(extra, "extra forbidden original member")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_source_digest_is_exact_github_actions_transport_not_an_identity_claim(tmp_path):
    p = tmp_path/"fixture.zip"
    digest = fixture_archive(p)
    result = inspect_archive(p, expected_sha256=digest)
    assert result["n_archive_members"] == 4
    assert result["n_original_raw_photometry_responses"] == 2
    assert result["n_physical_gaia_ztf_source_crossmatches_confirmed"] == 0
    assert result["scientific_fits_or_empirical_psf_stars_validated"] is False
    assert set(EXPECTED_NAMES) == {
        "PILOT_STATUS.json", "REPORT.md",
        f"{IDS[0]}_IRSA_RAW.csv", f"{IDS[1]}_IRSA_RAW.csv"
    }
    assert PINNED_ORIGINAL_ACTIONS_ZIP_SHA256 != digest
    assert not any(i in str(result) for i in IDS)


def test_tampered_original_zip_rejected_by_pinned_digest(tmp_path):
    p = tmp_path/"fixture.zip"
    fixture_archive(p)
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        inspect_archive(p)


def test_manifest_mismatch_rejected_even_when_outer_zip_digest_matches(tmp_path):
    p = tmp_path/"fixture.zip"
    def altered(manifest, raw):
        manifest["results"][0]["raw_bytes"] += 1
    digest = fixture_archive(p, altered=altered)
    with pytest.raises(ValueError, match="CSV bytes mismatch"):
        inspect_archive(p, expected_sha256=digest)


def test_unauthenticated_source_metadata_cannot_be_rewritten_to_true(tmp_path):
    p = tmp_path/"fixture.zip"
    def altered(manifest, raw):
        manifest["source_release_independently_authenticated"] = True
    digest = fixture_archive(p, altered=altered)
    with pytest.raises(ValueError, match="source metadata changed"):
        inspect_archive(p, expected_sha256=digest)


def test_an_extra_file_or_path_traversal_member_blocks_public_provenance(tmp_path):
    for name in ("new_catalog.fits", "../other_raw.fits"):
        p = tmp_path/"fixture.zip"
        digest = fixture_archive(p, extra=name)
        with pytest.raises(ValueError, match="file inventory changed"):
            inspect_archive(p, expected_sha256=digest)


def test_invalid_hash_input_is_not_ignored(tmp_path):
    p = tmp_path/"fixture.zip"
    fixture_archive(p)
    for digest in ("", "not-the-original-digest", "G"*64):
        with pytest.raises(ValueError, match="trusted 64-digit"):
            inspect_archive(p, expected_sha256=digest)


def test_missing_original_file_fails_closed(tmp_path):
    with pytest.raises(ValueError, match="absent"):
        inspect_archive(tmp_path/"does_not_exist.zip")
