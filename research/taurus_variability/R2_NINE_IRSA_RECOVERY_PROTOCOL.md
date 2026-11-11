# Taurus R2 — nine unresolved original ZTF source positions

**Protocol defined 11 November 2026, before the new live responses.**

The earlier [22-source IRSA access investigation](R2_REAL_IRSA_22_FAILURE_DIAGNOSIS_RESULTS.md) successfully retrieved **13** of the **22** previously unavailable 2-arcsec ZTF positional response tables with the *same* original `NOBS_MIN=5` query. The initial run had two other successful positions, leaving **9** access-unresolved positions among the 24 frozen, nonrepresentative Taurus technical candidates.

## Frozen selection and request rationale

The nine original Gaia DR3 source IDs are **derived mechanically**, with a strict source-level validation, from the existing [original 24-row derived response ledger](../../reports/taurus_variability_r2/IRSA_22_ORIGINAL_DERIVED_DIAGNOSTIC_LEDGER.json). No stars are included or excluded based on their apparent photometric variation, periodogram, temperature or disk classification.

Of those nine:

- **8** previously timed out using the original `POS=CIRCLE`, radius 2 arcsec, `FORMAT=csv`, `NOBS_MIN=5` query with a 12-second timeout. Retest **once**, with the identical URL but 25-second timeout.
- **1** previously returned a valid 0-row response under `NOBS_MIN=5`. Retest **once**, at the identical position with `NOBS_MIN=1` to investigate whether the original minimum-observations cutoff filtered out a low-coverage catalogued object.
- The `NUM_OBS=1` alternate returned HTTP 400 for all nine previous positions. **It is intentionally not repeated**. The public IRSA API documentation lists `NOBS_MIN` in examples and the parameter summary, although `NUM_OBS` is also present in the parameter reference.

The workflow issues **at most 9** provider requests, with up to 25 seconds each and at least 1 second between successive requests. It uses a fixed 2 MB response limit, requires parseable original table syntax for a positive access outcome and retains original response SHA-256 digests and HTTP metadata where available. If all nine still fail, all nine remain **unresolved**, not astrophysical non-detections.

## Allowed and forbidden claims

Allowed: a **real ZTF positional source table** was obtained and passed a schema check; number of rows returned; a query timed out; an empty table was returned **under that specific filter**.

Forbidden without additional independent evidence: Gaia-to-ZTF **physical** source identity, the absence of a Taurus star, nonvariability, new periodicities, new companions, the absence of blends or a population incidence estimate. A single sky position may yield multiple ZTF OIDs or filters, and public ZTF sky positions alone cannot resolve the physical match.

Even successful retrieval for 24/24 positional fields would **not complete R2**: the originally required source-by-source FITS/mask/PSF, independent astrometry, source blending, Gaia parallax and original literature membership vetting remain outstanding.

## Reproducible source and original evidence

- Study code: `src/stellarforge/r2_nine_source_recovery.py`
- Execution: `python -m scripts.run_taurus_r2_nine_source_recovery`
- Github Actions: `.github/workflows/taurus-r2-nine-recovery.yml`
- [ZTF lightcurve API and coordinate-query parameters](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html)
- Original old [31-request diagnostic workflow run](https://github.com/ismaelberja/stellarforge/actions/runs/43037800319)

Only **derived per-request metadata** is public; no original IRSA CSV, original FITS pixels or verified new stellar variable objects are committed.
