# Architecture design (target system)

## Layer boundaries

1. **Catalogue registry** — membership provenance, catalogue identifiers, Gaia IDs, region/group and literature status. Immutable ingestion snapshot.
2. **Survey adapters** — Gaia TAP, Gaia DataLink, ZTF light curve REST, later HATS-based bulk path. No domain logic inside HTTP clients.
3. **Astrometry and matching** — epoch propagation, source identity, ambiguity scoring and alternative-match retention.
4. **Scientific data contracts** — original time frame, source ID, band, magnitude/flux and uncertainty, quality flags, instrument, survey and source archive.
5. **Quality controller** — schema checks, missingness, cadence/coverage, blending, false detections, error handling.
6. **Time-series science** — variability tests, Lomb–Scargle, seasonal window, period significance, multiband features, physics-focused case studies.
7. **ML and evaluation** — reference baselines, ranking and uncertainty, injection/recovery, leakage audits, external validation.
8. **Results layer** — evidence-linked candidates, metrics, figures, provenance, reproducible experiment manifests.
9. **Application** — later FastAPI endpoints + interactive front end; never trust an app screenshot as scientific evidence.

## Tooling choice rationale

- **Python** fits the scientific ecosystem and job-market expectations.
- **Astropy + Astroquery** for time/sky-coordinate standards and Gaia access.
- **NumPy + SciPy** for signal processing, **Parquet + DuckDB** for reproducible scale beyond toy CSVs.
- **pytest** and CI for regressions; **Docker** later for reproducible environments.
- **FastAPI** later for typed endpoints, with a UI only once credible scientific outputs exist.

## Engineering constraints

- Network-bound activities must be **idempotent, cacheable, resumable** and rate limited.
- No raw archive data or giant binary files in the code repository by default.
- Public pages expose provenance, exact versions, code commit and analysis configuration.
- Figure generation must be deterministic enough to compare outputs; set RNG seeds for stochastic analyses.
- Raw telescope measurements are immutable. Cleaning is versioned with reasons and counts.
- Configure API behavior explicitly. Disallow unbounded large sky cones and unvalidated URL injection.

## First-phase architecture decision

The v0.1 code deliberately contains **no classifier**, no dummy scientific plots, no fabricated target list and no speculative 'new discoveries'. The small, testable service primitives are the prerequisite to correctly handling real archive products.


### Phase 9 observability and scientific evidence layer

- `epoch_evidence.py`: approximate per-observation Gaia proper-motion trajectory vs recorded MJD/RA/Dec, separate per OID/filter/time scale; no confirmation from proximity.
- `observational_dossier.py`: source-readiness gates, immutable local input checks, manual-identity holds and standalone static HTML dashboard.
- `scripts/run_v09_pipeline.py`: two-target offline-first orchestrator; optional two official IRSA requests; failed network requests stored as failures (not astrophysical negatives), immutable raw-cache replay.
- `reports/observational_gates_v0.9/`: evidence snapshot and catalogue-derived figure; no ZTF Taurus raw photometry.