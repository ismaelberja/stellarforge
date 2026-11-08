# CURRENT SCIENTIFIC AND SOFTWARE ROADMAP — StellarForge v1.12, 8 November 2026

**Completed engineering work:** 506 passing automated tests, verified 2,212 ZTF positional-cone records, real FITS/WCS checks of original science frames, independent Gaia DR3 five-parameter formal covariance and annual geometric parallax for both technical targets and eight candidate references, and now a **real-original-FITS pixel remeasurement audit with a new sky-plane-corrected aperture centroid compared against the original constrained Gaussian model**. [Read the original-image observational evidence](../reports/real_fits_v1.12/REAL_TWO_CENTROID_MODEL_QA.md).

**Key scientific finding:** two 20-request audits were completed on the same original ZTF science epochs, revealing intermittent IRSA HTTP 503 archive availability. In the **final run**, eight HTTP 503 and **12 complete dual-centroid image screens** (1 target, 11 Gaia references) produced **9 provisionally model-consistent candidate references**, with median Gaussian/aperture centroid separation **0.104720″**. The CIDA 11 MJD58475 exposure had four reference candidates with Gaussian/aperture internal LOO RMS **0.064675″ versus 0.155762″**, although the target FITS was inaccessible. The four FITS files available in both runs had identical SHA-256 bytes. These figures measure estimator/reference-sample sensitivity on shared pixels, **not calibrated instrument astrometry, source motions or independent observing epochs**. Only one of four exposure groups had enough cross-model references.

**Scientific priority for next phase:**
1. Retrieve the **official IRSA ZTF matching `mskimg.fits` bad-pixel bitmask** and native `sciimgdao.psf`, `sciimgdaopsfcent.fits` / `psfcat.fits` products for the same dated science exposure IDs, under a fixed request budget. Decode appropriate flag semantics, WCS alignment and PSF model provenance rather than assuming `sciimg.fits` by itself proves a clean detector. See [IRSA product metadata](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html).
2. Use a larger, independently vetted sample of spatially distributed Gaia/ZTF field stars, with catalogue cross-identification and physical morphology/crowding checks, to fit and test detector-dependent empirical PSF and WCS distortion. Preserve *held-out* stars not used in the model.
3. Verify ZTF header epoch/time convention and full topocentric/aberration/refraction corrections, source-specific Gaia 5D covariance and high-RUWE CIDA 11 model reliability, without confusing formal Gaia catalogue errors with actual imaging errors.
4. Extend only verified, mask-checked calibration to all original six OID/filter groups and representative independent epochs, quantifying selection/injection-recovery and alternative physical explanations before any variability/discovery claim.
5. Keep public artifacts **derived aggregate only**; never publish original ZTF light curves/FITS pixels or Gaia TAP raw catalogues without a separate verified provenance/rights review.

**Still unconfirmed:** independently authenticated Gaia–ZTF source identities, clean isolated stellar PSFs, calibrated instrumental astrometric uncertainties, newly discovered companions and physical variability events. Historical sections below are retained for audit traceability.

---

# Current research/engineering roadmap — StellarForge v1.11 (6 November 2026)

**Verified:** 484 automated tests, 2,212 real ZTF positional-cone photometric rows, 12 separate ZTF FITS science exposures across the original six OID/passband groups, eight Gaia DR3 candidate controls with 13 real FITS image-model fits, 5D formal Gaia source covariance for all ten v1.11 targets and references, and individual Earth-geocentric annual parallax corrections at four historical ZTF science epochs. [Real Gaia reference parallax sensitivity report](../reports/reference_parallax_v1.11/REAL_GAIA_REFERENCE_PARALLAX_LOO.md).

**Critical result:** Including each reference's annual parallax changes the strict internal leave-one-reference-out RMS from 0.075782″ to 0.075770″ (FT Tau) and from 0.093046″ to 0.092971″ (CIDA 11), only **0.012 / 0.075 mas**. The original reference-image disagreement therefore remains largely unexplained by this correction. Only two of four original reference-field exposures retain enough high-quality Gaussian models. These RMS values are NOT physical motion, an instrument calibration, PSF error bars or source identities.

**Next scientific gates:**
1. Obtain an independently vetted, spatially representative pool of genuine same-detector ZTF field stars; check saturation/crowding, image masks, colour and fitted PSF wings rather than trusting Gaia RUWE/brightness alone.
2. On raw FITS science exposures, independently calibrate WCS distortion, detector-dependent PSF and astrometric residuals with **held-out** reference stars not used to fit the astrometric model; estimate repeatable uncertainty budgets and correlated systematics, not simply internal scatter.
3. Verify original exposure timing, observer location and topocentric aberration/refraction/atmospheric colour effects. The Gaia v1.11 5D covariance is **catalogue-formal** and cannot automatically replace ZTF instrumental uncertainty.
4. Independently confirm Gaia–ZTF source IDs, including high-RUWE CIDA 11 (RUWE ≈ 8.57), and review field contamination/non-Gaia sources.
5. Validate the original Taurus publisher membership catalogue, disk classes, selection function and real-cadence injection/recovery before any astronomical variability/companion claim.

**Not confirmed:** isolated empirical PSFs, independently calibrated ZTF WCS, physical Gaia–ZTF source identities, newly discovered companions or astrophysical events. Retain public Git only for code and vetted derived aggregate evidence, not raw third-party photometry or FITS images.

---

# CURRENT RESEARCH/SOFTWARE ROADMAP — v1.10 (6 November 2026)

**Verified science-software milestone:** 468 automated tests; original real ZTF positional-cone photometry and FITS screen, Gaia DR3 formal 5D/annual parallax modeling for two target sources, and now a **reproducible leave-one-Gaia-reference-out image-offset quality audit** of the original v1.8 derived 13 reference fits (four dated ZTF g-band science frames). A small derived summary with the historic original aggregate SHA-256 is versioned to survive time-limited external workflow artifacts.

**Critical observation:** 3/4 frames have at least three inclusive candidate reference image models; only 2/4 retain at least three *non-flagged* Gaussian image models. FT Tau MJD58491 has holdout disagreement RMS ~0.076 arcsec, CIDA 11 MJD58475 ~0.093 arcsec. CIDA 11 MJD58849 falls from five inclusive to two strict references: **no strict holdout inference**. These values are internal disagreement, not ZTF absolute WCS calibration errors or verified source matches. [Real reference holdout evidence](../reports/holdout_v1.10/REAL_REFERENCE_HOLDOUT_EVIDENCE.md).

**Next science gates:**
1. Independently authenticate reference stars using Gaia catalogue and ZTF image morphology, saturation/crowding masks, PSF quality, color and other surveys. More stars per field, unbiased spatial sampling and vetted original science frames are needed.
2. Recompute Gaia **each reference star** position with its own full five-parameter formal covariance, annual parallax and source quality at precise FITS timing; the v1.9 model covered only the two targets.
3. Estimate an independent real detector WCS/PSF and background error budget, including correlated distortions, systematic/measurement errors, and checks outside any fit/control selection.
4. Resolve high CIDA 11 RUWE (~8.57), source multiplicity alternatives, Gaia/ZTF source identity, the publisher Taurus catalogue and real-time-domain injection/recovery before physical variability claims.
5. Keep external raw ZTF FITS/light curves and Gaia TAP CSV outside public Git; preserve only verified derived aggregates, immutable provenance and tests.

**Still unconfirmed:** physical Gaia–ZTF source identifications, isolated empirical PSFs, independently calibrated image WCS, new companions or physical variability events.

---

# CURRENT SCIENTIFIC & SOFTWARE ROADMAP — v1.9 (6 November 2026)

**Implemented and validated:** 444 offline tests; original 2,212 SHA-checked ZTF positional-cone photometry rows; 12 actual distinct ZTF science FITS observations across six OID/passband groups; eight Gaia DR3 catalogue quality-screened instrumental reference candidates with 13 real ZTF image-model fits; three provisional local median WCS shift estimates; **new v1.9 exact-source Gaia DR3 5×5 formal covariance including all ten correlations and epoch-dependent Earth-geocentric annual parallax** at four original ZTF observation dates. See [real v1.9 astrometry report](../reports/gaia_formal_v1.9/GAIA_COVARIANCE_AND_ANNUAL_PARALLAX.md).

**What is NOT validated:** independent physical Gaia–ZTF source IDs, unblended stellar PSFs, detector astrometric WCS, uncertainty-calibrated individual ZTF centroids, six-parameter pseudocolour modeling, Gaia radial velocity/perspective acceleration, observatory aberration and refraction, source multiplicity, astrophysical variability event counts.

**Next defensible steps:**
1. Authenticate instrument PSF reference stars using independent classification, detector quality flags, calibrated magnitudes, WCS accuracy and image morphology; the v1.8 candidate Gaia stars are **not yet empirically calibrated PSF standards**.
2. On actual dated science images, independently model the detector distortion and image-specific PSF/WCS/background error contributions. Combine those with **Gaia's v1.9 formal covariance** in a calibrated, uncertainty-aware comparison, never pretending the catalogue covariance includes instrument or high-RUWE source systematics.
3. Verify the ZTF exposure time-scale in raw FITS headers; account for observer velocity/aberration, parallax, full Gaia radial/perspective motion where available. Treat **CIDA 11 RUWE ≈ 8.57** as an explicit source-model reliability warning.
4. Extend only the validated method to all six ZTF OID/bands and multiple original science dates. Use controls, image masks and injection/recovery before an astronomical source identity or any real variability/companion claim.
5. Verify the publisher-original Luhman (2023) table, disk classifications and selection biases. Continue minimal public aggregate results, no raw third-party Gaia/ZTF source downloads or FITS pixel matrices in public Git.

**Science confirmations remain zero:** new physical companions, resolved blends, authenticated Gaia–ZTF sources or astrophysical variability events.

---

# Current research/engineering roadmap — v1.8, 5 November 2026

**New verified research-software milestone:** 422 automated tests; two original SHA-checked IRSA positional cone queries (2,212 rows); six ZTF OID/filter groups with two independent usable science images apiece (v1.7); **independent Gaia DR3 210-arcsec reference selection** (50 FT Tau + 250 CIDA 11 catalogue sources), **eight conservative candidate references**, 13 measured same-ZTF-science-product reference cutouts and three provisional signed WCS translation proxies (v1.8). These are **neither independently calibrated PSFs/WCS nor confirmed stellar source identities**. See the [real v1.8 report](../reports/gaia_reference_v1.8/REAL_REFERENCE_CANDIDATE_EVIDENCE.md).

**Priority next scientific work:**
1. Validate Gaia-selected candidate reference stars using catalogue cross-checks, morphology, saturation and field/filter-specific instrumental PSFs. Quality-screened Gaia entries are not guaranteed isolated ZTF PSF standards.
2. Perform independently controlled multi-source WCS distortion/shift and uncertainty calibration with robust matching, proper error propagation and full Gaia parallax, correlation and covariance terms. High CIDA 11 RUWE (about 8.57) demands scrutiny.
3. Evaluate background, detector masks, colour PSF mismatch, nebular emission and blending before claiming clean stellar measurements. Extend limited one-g-band-per-target pilot to the remaining ZTF OID/filter groups and multiple science epochs.
4. Independently verify the publisher-original Luhman (2023) membership table, disk classes and source IDs, then validate real photometric variability/selection efficiency with field stars and injection/recovery.
5. Maintain fail-closed acquisition, input SHA-256 provenance and **no publication of raw third-party Gaia/ZTF CSVs or FITS pixel arrays**. Numerical precision of offset reports is not calibrated astrophysical measurement accuracy.

No new physical companions, source crossmatches, stellar disk classifications or physical variability events are confirmed.

---

# Research/engineering roadmap — CURRENT v1.7, 5 November 2026

**Completed engineering work:** reproducible official IRSA raw transport (2,212 SHA-checked ZTF rows), provisional Gaia–ZTF positional and Gaia DR3 field screens, five image cutout screens in v1.5, preliminary Gaussian proxies in v1.6, **twelve real and distinct science FITS images (two per OID/filter) in v1.7**, all with bounded celestial WCS/shape screening, synthetic regression coverage and **400 passed tests**. Read the [v1.7 observational report](../reports/field_controls_v1.7/REAL_MULTIEPOCH_AND_CONTROL_LIMITS.md).

**New critical observation:** no v1.7 90-arcsec science frame had two usable **unclassified** same-field image control peaks, so empirical instrumental PSF calibration is NOT completed. The small pairwise centroid residual differences are only descriptive; Gaia source identity, independent WCS error and unblended photometry remain unverified.

**Priority scientific gates (all open):**
1. Authenticate one or more field stars from catalogued/imaged sources in each ZTF field; if necessary query larger official image products under a controlled request plan. Distinguish extended nebulae, galaxies, saturation and unclassified maxima; do not silently treat brightness peaks as stellar controls.
2. Estimate **empirical field-variable PSFs**, masks and source/background residuals with valid controls. A single-Gaussian target-model residual does not imply a physical companion.
3. Use the now-available independent science frames for **calibrated** multi-epoch comparisons with WCS recalibration, centroid errors, full Gaia proper-motion/parallax/covariance, realistic correlated instrument systematics and absolute time definitions.
4. Resolve CIDA 11's unusually high Gaia DR3 RUWE and alternative/non-Gaia neighboring sources. **No Gaia–ZTF physical identity confirmed.**
5. Verify the original Luhman (2023) publisher membership dataset, independent disk classifications, external field reference stars and real-cadence injection/recovery before estimating detection sensitivity, incidence or a physical event rate.

**Public repository:** GitHub can be shown on a CV now; code and findings are versioned for transparent research-software review, with individual third-party ZTF CSV and FITS pixel arrays kept outside Git. This supersedes earlier milestone roadmaps below, which remain historical.

---

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