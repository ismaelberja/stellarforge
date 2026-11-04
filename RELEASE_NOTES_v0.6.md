# StellarForge v0.6 — Epoch-aware review and instrumental falsification

**Release type:** internal research development only (not a public GitHub release). **Date:** 2026-11-04.

## Implemented

- Spherical proper-motion source position estimate from nominal Gaia J2016.0 to a target epoch, correctly respecting the µ_α* convention and RA wrap.
- All-OID / all-filter positional ambiguity screen, with explicit **unverified** statuses, no silent winner assignment.
- Offline adapter integrating original ZTF CSV/IPAC ingestion, per-OID quality control, epoch screening and hashed review reports.
- Explainable event-review policy: independent bands + **>=3 vetted same-field reference stars**; coherent field shifts rejected or flagged, missing controls held.
- Real literature-catalog engineering example: J2021.0 nominal propagated coordinates and Gaia proper-motion plot for **24 genuine catalogue-source rows** (mirror publisher-byte crosscheck still pending).
- **400 synthetic adversarial trials** across eight scenarios including coherent instrument offsets, band-only events, no controls, high noise and white noise. See v0.6 scientific report.
- Added three test modules plus integration review tests. **170 pytest tests passing** in this environment.

## Deliberately *not* claimed

- No real ZTF data retrieved in this environment, so **no** novel objects, periodicity measurements, verified cross-identifications or new scientific sample selection.
- The J2021 epoch is illustrative, **not a time measured by ZTF for each star**.
- Artificial control-star passing is not evidence of performance on realistic variable-star backgrounds or ZTF systematics.
- No trained astrophysical ML model, dashboard or physical disk-accretion inference has been performed.

## Reproduction

```bash
python -m pip install -e '.[analysis,test]'
python -m pytest -q
python scripts/build_v06_astrometry_audit.py
python scripts/run_v06_systematics_validation.py
```

Documentation: [`docs/PHASE6_ASTROMETRY_AND_FALSIFICATION.md`](docs/PHASE6_ASTROMETRY_AND_FALSIFICATION.md).