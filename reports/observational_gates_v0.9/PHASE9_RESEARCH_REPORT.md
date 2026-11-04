# StellarForge v0.9 — Observational Evidence Gate

**Date:** 4 November 2026  
**Targets:** FT Tau and CIDA 11 (Taurus)  
**Phase status:** successful engineering / **observational data blocked**

## What was attempted

Two direct, independent queries were attempted against the [official IRSA ZTF Lightcurve API](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html). Requests contain source coordinates derived from the literature's Taurus member table, a 2-arcsec cone, g/r filters and `BAD_CATFLAGS_MASK=32768`. Both requests failed at the **network** layer (`URLError`) before any photometric table was returned.

**This is neither evidence of non-coverage nor evidence that these stars are constant or non-variable.** Both target dossiers retain `OFFICIAL_IRSA_PHOTOMETRY_PENDING`.

## New code

1. Per-row epoch-aware proper-motion propagation of Gaia DR3 coordinates to ZTF MJD dates.
2. OID-filter-time separation and audit of each possible counterpart independently.
3. Median, 95th-percentile and inside-cone fraction of per-epoch angular separations.
4. Conservatively defined same-band multiple-counterpart and mixed-position warnings.
5. Integrity-checking of local raw inputs, official-host claim screening and evidence-status separation.
6. Fail-closed, machine-readable dossiers and offline HTML dashboard for the pilot stars.
7. Reproducible, resumable source acquisition without overwriting existing hash-checked raw files.

## Scientific interpretation

The figure `TAURUS_TWO_STARS_CATALOG_PROPAGATION.png` contains **calculated trajectories from published catalogue positions and proper motions**, not ZTF detections. Every point represents a nominal position at an illustrative epoch. No parallax/covariance/image blending correction has been applied.

Tests that use artificial photometric rows are software unit tests, not physical detections. No period, dipper, burster, disk class, candidate membership reassignment or incidence fraction has been derived from genuine ZTF light curves in this phase.

## Test result

**303 tests passed** (239 v0.8 tests + 64 v0.9 tests). The new tests include high proper-motion source shifts, RA wraparound, crowded multiple OIDs, malformed time/ID inputs, checksum corruption, fake IRSA URL claims, failed/empty acquisitions and no-overwrite cache protection.

## Files to review

- `RUN_SUMMARY.json` — official retrieval attempt outcome, with exception class.
- `TWO_STAR_OFFICIAL_IRSA_QUERY_PLAN.json` — reproducible official URLs and catalogue coordinates.
- `149623711269425408_EVIDENCE_DOSSIER.json` — FT Tau.
- `3419110734340795648_EVIDENCE_DOSSIER.json` — CIDA 11.
- `STELLARFORGE_V09_EVIDENCE_DASHBOARD.html` — static HTML evidence dashboard.
- `TAURUS_TWO_STARS_CATALOG_PROPAGATION.png` — catalogue proper-motion predictions.
- `docs/PHASE9_PER_EPOCH_ASTROMETRY_AND_EVIDENCE_GATES.md` — complete methods and limitations.

## Next phase

Obtain official ZTF photometry with successful source verification. Only then perform actual-image contamination checks, robust OID selection, multiband event analysis and recovery tests on real cadences. Keep the prototype unpublished pending verifiable scientific results.