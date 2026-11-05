## Current research/engineering roadmap — v1.6 (5 November 2026)

**Engineering milestone implemented:** 387 automated tests, acquisition of 2,212 original IRSA ZTF position-query records with source hashes, cautious per-epoch positional screening, independent Gaia DR3 15-arcsec field-neighbour checks, real FITS/WCS pixel access and single-Gaussian image-profile proxies for three FT Tau science exposures. See the [current status](PROJECT_STATUS.md), [v1.5 real FITS audit](../reports/real_fits_v1.5/PIXEL_WCS_RESULTS.md), and [v1.6 Gaussian-profile real-image audit](../reports/psf_v1.6/REAL_GAUSSIAN_FIT_REVIEW.md).

**Science gates still open (do not claim completed from a software test):**
1. Independently verify Gaia–ZTF stellar identity using realistic Gaia full astrometric uncertainties, image calibration and source alternatives; CIDA 11 has very high RUWE.
2. Compare targets with **same-field empirical PSFs**, spatially varying image backgrounds, instrumental masks and WCS residuals. A simple single-Gaussian residual is not evidence of a physical companion.
3. Obtain at least two independent and valid dated science exposures within an OID/filter. Temporary HTTP 503 archive errors must not be treated as absence of coverage; reference coadds do not count.
4. Verify the publisher's original Luhman (2023) membership table, independent disk classes and source sample selection before any occurrence-rate estimate.
5. Quantify real-cadence sensitivity with vetted comparison stars, injection/recovery and uncertainty budgets before any physical variability discovery or period/incidence claim.

**External/public code:** repo is public for software portfolio inspection. Raw photometric CSV and FITS image pixels are not committed to Git; only vetted aggregate results are added. This roadmap remains historical below so earlier phases can be understood in context.

---

## Current v0.8 milestone and next scientific gate

- v0.8 is complete as a **technical research phase**: offline secondary ZTF-format compatibility, dual-clock MJD/HJD fix, exact event-start cadence geometry, 24-source readiness ledger, and 239 passing tests. **Zero verified Taurus ZTF photometric curves and zero physical discoveries.**
- v0.9 scientific gate: retrieve original IRSA ZTF observations for FT Tau / CIDA 11, compare the pinned Luhman source table against its publisher form, perform exact observation-epoch Gaia astrometry and crowded-field review, establish independent disk labels and run true observed-cadence injections. This cannot be claimed complete from test fixtures or third-party secondary examples.

# Research & engineering roadmap — phased, not rushed

This is a *multi-stage* project. Finishing a code file is not equivalent to passing the corresponding scientific review gate. Each sprint records open questions and decisions from Ismael as scientific owner. If data access or assumptions fail, revise the protocol rather than hiding the failure.

## Stage 1 — Scope and scientific protocol [FOUNDATION COMPLETE; DATA GATE OPEN]

- [x] Choose joint goal: astronomy + employable data-engineering/ML skills.
- [x] Select Taurus young stars as the pilot population; identify independent member reference.
- [x] Verify official Gaia DataLink and ZTF API routes from archive documentation.
- [x] Write explicit scientific hypotheses, limitations and data/model ethics.
- [x] Build initial source/geometry/URL prototype with offline tests.
- [ ] Retrieve and reconcile the complete machine-readable **Luhman 2023 Table 2**; paper reports 532 adopted members, 467 Gaia DR3 entries and 412 Gaia DR3 astrometric solutions. A pinned third-party copy has now been **examined in full through the research connector**; the original publisher table and full local raw snapshot still need reconciliation.
- [x] Choose primary focus: **candidate dippers/bursters**, with rotation/periodicity as secondary.
- [x] Code the proposed 24-target disk-stratified selector; **a separate 24-object real-coordinate technical seed has now been extracted**, but no disk-class scientific roster is approved.
- [ ] Verify independent disk labels; execute the roster against the verified member table and approve a first sample with evidence.

**Exit gate:** versioned target manifest, science protocol approved, exact source provenance, no fabricated observational sample.

## Stage 2 — Real archive integration [v0.6 ASTROMETRIC SCREEN BUILT; OBSERVATION GATE STILL OPEN]

- Gaia TAP metadata and DataLink downloads, availability audit and archive-side errors.
- Single-object ZTF acquisition with per-oid/per-filter parsing, raw-cache checksums, time and magnitudes checked.
- [x] Preliminary spherical proper-motion propagation, per-band/OID centroid checks and conservative ambiguity reports (v0.6). **Not yet full Astropy covariance/parallax/image matching**.
- [ ] Full Astropy astrometric uncertainty, parallax and image-level scene checks on actual ZTF epochs.
- Service etiquette, bounded retries, timeouts and resumable ingestion. Parquet/DuckDB for processed products.

**Exit gate:** traceable raw-to-processed lineage and QC for pilot objects; measured coverage and rejection counts.

## Stage 3 — Time-series quality and exploratory science

- Per-band cleaning, photometric uncertainties, upper limits/flags, baseline variability.
- Diagnostic plots with original time system, seasonal gaps and sampling windows.
- Descriptive source population statistics with denominators and uncertainty.

**Exit gate:** data dictionary, QA report, rejected-object report, human-reviewed sample diagnostics.

## Stage 4 — Physical variability characterization [EXPLORATORY ENGINE BUILT; SCIENCE GATE OPEN]

- [x] Implement provisional weighted Lomb–Scargle diagnostics and sampling-window flags on engineering fixtures. **No real periods inferred.**
- [ ] Benchmark aliases, harmonics and correlated astrophysical noise on *real* survey sampling.
- [x] Uncertainty-aware descriptive amplitude, scatter and tail-asymmetry **proxy**.
- [ ] Quasi-periodic versus aperiodic signal diagnostics, amplitude/period uncertainty and physical timescale tests.
- Differential filter changes and optional simultaneous color–magnitude diagnostics.

**Exit gate:** period recovery reliability, feature definitions and uncertainties fully specified.

## Stage 5 — Validation and falsification [v0.6 SYNTHETIC FIELD-CONTROL VETO BUILT]

- [x] Compare simulated strong astrophysical signals with same-field coherent calibration artifacts and explicit missing-control regimes (v0.6; artificial data only).
- [ ] Literature benchmark cases, null simulations and injection/recovery on real timestamps.
- False-positive rate versus cadence, brightness and crowding; account for multiple comparisons.
- External region or survey validation when scientifically justified.

**Exit gate:** quantified detection biases; null and failure-case figures shown prominently.

## Stage 6 — Machine learning (only when warranted)

- Unsupervised baselines (robust statistics, Isolation Forest); interpretable supervised models only with trustworthy labels.
- Split by source, region and/or observing campaign appropriately. Leakage review before hyperparameter search.
- Calibrate ranking thresholds against expert-review capacity; transparent feature explanations.

**Exit gate:** meaningful improvement over the simple baseline on genuinely withheld sources and failure-analysis table.

## Stage 7 — Scientific conclusions and candidate register

- Scientific figure gallery, object-level vetting with literature, alternative physical interpretations.
- Catalogue of **candidates for follow-up**, clearly differentiated from confirmed discoveries.
- Draft internal research note / reproducibility appendix, limitations and references.

**Exit gate:** every headline claim directly traceable to evidence, source and calculation.

## Stage 8 — Portfolio-grade product

- REST API (FastAPI), an interactive light-curve viewer, candidate search, sky map and provenance panels.
- Docker, tests, static analysis, CI and deployment with realistic cost/resource safeguards.
- Onboarding documentation, methods paper-style report and honest AI-assistance disclosure.

**Exit gate:** third party can reproduce a vetted example end-to-end, understand design tradeoffs, and distinguish the research findings from demonstration features.

## Human decision checkpoints

1. Scientific focus and what would count as an astrophysically meaningful anomaly.
2. Initial vetted subsample from Taurus.
3. Quality thresholds, high-risk matching decisions and period significance.
4. Which models to compare; whether labels are truly independent.
5. Selection of any candidates to report publicly.

The purpose of these checkpoints is not to make the user write boilerplate code, but to ensure the scientific decisions genuinely represent their contribution and can be defended in research and job interviews.


## v0.5 evidence update — November 2026

- Completed in code: dry-run 24-target ZTF batch plan, provenance-verified restartable downloader, strict per-target status ledger, and preliminary uncertainty-aware fading/brightening **candidate** screen.
- Synthetic-only algorithm validation and unit testing completed; documented failure on coherent calibration offsets.
- **Blocked / not completed:** download of actual ZTF curves in this environment, astrometric source verification, Gaia DataLink epoch-photometry extraction, disk-class stratification, real-cadence injection/recovery and any measured Taurus event incidence.
- Next scientific gate: obtain 2 real ZTF sources via IRSA, audit each `oid` and image/motion match; never infer a member from proximity alone.


## Phase 9 checkpoint — 4 November 2026

- [x] Per-observation Gaia proper-motion screen against each ZTF MJD and photometric position (engineering method; no confirmed counterpart).
- [x] Explicit multi-OID ambiguity and invalid/missing epoch hold statuses.
- [x] Fail-closed two-star evidence dossiers, read-only offline dashboard and integrity-controlled file import.
- [x] Two official IRSA requests attempted, and **both failed due to environment networking**; no ZTF Taurus raw photometry downloaded.
- [x] 303 tests pass (239 inherited + 64 v0.9).
- [ ] **Blocking observational science gate:** successfully acquire and independently authenticate the official ZTF FT Tau / CIDA 11 raw tables; resolve OIDs by epoch, images and crowding; perform real-timestamp injection/recovery.
- [ ] Independently verify the publisher's Luhman (2023) table bytes and scientifically classify disks with appropriate literature.

Important: do not interpret unavailable remote data as evidence of absence of stars, variability, or survey coverage.