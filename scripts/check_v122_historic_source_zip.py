"""v1.22: offline archive-integrity gate for the original historic IRSA source ZIP.

This verifies that the privately retained four-file GitHub Actions artifact
matches a pinned 2026-11-05 acquisition digest and its internal manifest.
This is a *transport/provenance* check, NOT physical Gaia/ZTF crossmatch,
original survey PSF training-star membership, or new astronomy discovery.

Do NOT commit or upload the original ZIP, source CSVs, or original FITS
to the public repository. Only bounded source SHA/count/status aggregates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
from zipfile import ZipFile, BadZipFile

PINNED_ORIGINAL_ACTIONS_ZIP_SHA256 = (
    "d54246e00d4cf343b0b062b9eb92034e51c735067274a8109e9b2c2c2a2d5167"
)
ORIGINAL_RUN_ID = 41997079598
ORIGINAL_ARTIFACT_ID = 13401380025
EXPECTED_NAMES = frozenset({
    "PILOT_STATUS.json", "REPORT.md",
    "149623711269425408_IRSA_RAW.csv",
    "3419110734340795648_IRSA_RAW.csv",
})
MAX_ARCHIVE_BYTES = 2_000_000
MAX_UNCOMPRESSED_BYTES = 2_000_000


def inspect_archive(path: Path, *, expected_sha256: str =
                    PINNED_ORIGINAL_ACTIONS_ZIP_SHA256) -> dict:
    """Fail closed on tampering, truncated ZIP and alien extra members.

    expected_sha256 injection is for offline synthetic fixture tests. The
    CLI always uses the pinned GitHub Actions original acquisition digest.
    The archive is never copied or returned by this function.
    """
    path = Path(path)
    if (not isinstance(expected_sha256, str)
            or len(expected_sha256) != 64
            or any(c not in "0123456789abcdef" for c in expected_sha256)):
        raise ValueError("Missing trusted 64-digit SHA256 acquisition digest")
    if (not path.is_file() or path.is_symlink()
            or not 200 < path.stat().st_size <= MAX_ARCHIVE_BYTES):
        raise ValueError("Original source ZIP absent or implausible")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != expected_sha256:
        raise ValueError("Original GitHub Actions source archive SHA256 mismatch")

    try:
        with ZipFile(path) as archive:
            infos = archive.infolist()
            names = [item.filename for item in infos]
            if (len(infos) != len(EXPECTED_NAMES)
                    or set(names) != EXPECTED_NAMES
                    or len(set(names)) != len(names)):
                raise ValueError("Original historic ZTF acquisition file inventory changed")
            if (sum(i.file_size for i in infos) > MAX_UNCOMPRESSED_BYTES
                    or any(i.is_dir() or i.file_size < 1
                           or i.file_size > MAX_UNCOMPRESSED_BYTES
                           or stat.S_ISLNK(i.external_attr >> 16)
                           for i in infos)):
                raise ValueError("Original source ZIP is oversized or contains links")
            payload = json.loads(archive.read("PILOT_STATUS.json"))
            if (not isinstance(payload, dict)
                    or payload.get("raw_photometry_responses") != 2
                    or payload.get("verified_gaia_ztf_crossmatches") != 0
                    or payload.get("source_release_independently_authenticated") is not False):
                raise ValueError("Original survey source metadata changed")
            rows = payload.get("results")
            if not isinstance(rows, list) or len(rows) != 2:
                raise ValueError("Original acquisition manifest must contain two targets")
            seen = set()
            for row in rows:
                if not isinstance(row, dict):
                    raise ValueError("Invalid original acquisition record")
                sid = str(row.get("gaia_dr3_id", ""))
                if (sid in seen or not sid.isdigit()
                        or f"{sid}_IRSA_RAW.csv" not in EXPECTED_NAMES):
                    raise ValueError("Unexpected or repeated historical source")
                seen.add(sid)
                raw = archive.read(f"{sid}_IRSA_RAW.csv")
                if (len(raw) != row.get("raw_bytes")
                        or hashlib.sha256(raw).hexdigest() != row.get("raw_sha256")):
                    raise ValueError("Original CSV bytes mismatch acquisition manifest")
            if archive.testzip() is not None:
                raise ValueError("Original ZIP CRC mismatch")
    except (BadZipFile, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Malformed or incomplete historic IRSA original ZIP") from exc

    return {
        "status": "HISTORICAL_SOURCE_ARCHIVE_BYTE_INTEGRITY_VERIFIED",
        "original_github_actions_run_id": ORIGINAL_RUN_ID,
        "original_github_actions_artifact_id": ORIGINAL_ARTIFACT_ID,
        "zip_sha256": digest,
        "n_original_raw_photometry_responses": 2,
        "n_archive_members": len(EXPECTED_NAMES),
        "n_physical_gaia_ztf_source_crossmatches_confirmed": 0,
        "original_survey_psf_training_star_membership_known": False,
        "scientific_fits_or_empirical_psf_stars_validated": False,
        "file_recovery_does_not_verify_physical_source_identity": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only pinned archive digest check")
    parser.add_argument("historic_zip", type=Path)
    args = parser.parse_args()
    print(json.dumps(inspect_archive(args.historic_zip),
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
