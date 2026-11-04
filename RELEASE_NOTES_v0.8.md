# StellarForge v0.8 — Observational compatibility and cadence geometry

**Internal working release · 2026-11-04 · Not uploaded to GitHub.**

## What changed

1. An important multi-clock ZTF table bug was fixed: simultaneous `mjd`/`hjd` rows no longer fail, and incompatible clock offsets remain rejected.
2. New `stellarforge.cadence` calculates an **exact** observational window fraction for hypothetical episodes, without mislabeling it as detection completeness.
3. New `stellarforge.observational_release` performs offline source/format/QC/cadence auditing with SHA256 evidence and strict restrictions on labeling secondary photometry as science targets.
4. An actual *public third-party ZTF-format sample* was parsed offline: 8 rows, 6 QC accepted, 2 cloud/moon bit-flag rejected; source not independently cross-verified against original IRSA and **not Taurus**.
5. A 24-target Taurus readiness ledger records illustrative epoch-propagated positions, priority for FT Tau/CIDA 11 and the fact that 0 original Taurus curves / validated crossmatches are available.
6. New unit and integration tests for exact cadence measures, provenance rejection, cross-source data guards and scientific gate states.
7. Updated research source register, README, release metadata and explicit separation of observational/secondary/synthetic data.

**Validation:** 239 automated tests pass locally using `PYTHONPATH=src python -m pytest -q`. Supplementary report, figure and readiness CSV/JSON are included. Raw third-party observations are **not** bundled.

**Remaining tasks:** access original IRSA responses for the two pre-registered Taurus sources, cross-check original Luhman paper table against the pinned mirror, confirm positional match with images, perform real-cadence injection/recovery and physical interpretations. None can be declared complete from this working version.