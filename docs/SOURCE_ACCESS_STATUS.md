# CURRENT REAL-DATA EVIDENCE AND ACCESS — v1.10 (6 November 2026)

The older milestones below remain historical and are superseded by this current status.

- v1.10 uses the real [v1.8 Gaia reference/ZTF image workflow](https://github.com/ismaelberja/stellarforge/actions/runs/42077605987), archived as a **small derived 13-reference / 4-exposure** ledger with original JSON SHA-256 `fb7d5c315cbef56b2551e73920c67920827d91160b4c0bd35f3fd77113166beb`. The reduced public [ledger](../data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json) contains no FITS pixel arrays, raw ZTF light curves or original Gaia TAP CSV.
- Actual leave-one-Gaia-reference-out diagnostics: FT Tau MJD 58491.184780 has three strict models, LOO RMS **0.075782 arcsec**; CIDA 11 MJD 58475.113750 has four strict models, LOO RMS **0.093046 arcsec**. The later CIDA 11 MJD 58849.135984 has five *inclusive* reference fits but only two strict fits — **not enough for strict LOO QA**.
- v1.9 Gaia 5D formal uncertainty/parallax applies to the two Gaia **targets**, not the historical v1.8 **reference** star positions. Internal holdout discrepancies do not establish ZTF instrument astrometric precision or physically authenticated source matches.
- The original public v1.8 external artifact expires on **12 November 2026**; derived evidence is retained, but that is not the original FITS/raw-data archive. Existing historic original ZTF raw artifacts may remain accessible until their configured GitHub Actions expiry.
- All scientific source identity, empirical PSF calibration, independent WCS/distortion and astrophysical event claims remain **UNVERIFIED**. High CIDA 11 Gaia RUWE ~8.57 requires explicit quality warnings.
- v1.10 offline evidence/test workflow: [successful 468-test validation](https://github.com/ismaelberja/stellarforge/actions/runs/42214593233), using neither remote service nor raw archive access.

---

# CURRENT GAIA/IRSA ACCESS AND ASTROMETRIC EVIDENCE — v1.9 (6 November 2026)

**This is the latest verified project status. The historical v1.8 and earlier entries below remain for provenance.**

- **Official Gaia DR3 v1.9 covariance query:** two exact IDs (FT Tau `149623711269425408`, CIDA 11 `3419110734340795648`) with all **five astrometric parameter errors and ten correlations**, Gaia RUWE and original astrometric solution metadata. Four historical ZTF science observation MJDs were used for a **geocentric first-order annual parallax** and propagated **formal Gaia-only** 2D covariance. See [real Gaia v1.9 report](../reports/gaia_formal_v1.9/GAIA_COVARIANCE_AND_ANNUAL_PARALLAX.md) and [observed workflow](https://github.com/ismaelberja/stellarforge/actions/runs/42175644367).
- **Gaia parallax corrections vs linear-motion-only source predictions:** FT Tau east +6.791 / −4.781 mas; CIDA 11 east −1.362 / −2.250 mas at two dates each. These are *not observed physical displacements*.
- **Formal Gaia-only positional uncertainty:** FT Tau east 0.070–0.073 mas, CIDA 11 east 0.444–0.585 mas, without any instrumental ZTF error component. CIDA 11 **RUWE 8.56752** seriously weakens treating the formal single-star covariance as a complete astrometric error budget.
- **IRSA empirical precursor:** 2,212 original photometric positional-cone rows, 12 original science FITS epochs across six ZTF OID/bands (v1.7), 8 Gaia catalogue reference candidates and 13 candidate ZTF image model fits (v1.8). Source matching, isolated stellar PSF and WCS distortion calibration are *not independently confirmed*.
- **Public data policy:** source Gaia TAP CSV and all original ZTF FITS pixels are used only transiently, never committed or uploaded as raw artifacts by the v1.9 workflow. The historical earlier ZTF acquisition artifacts have their own retention and must not be mistaken for a permanent raw-data archive.
- **All astrophysical source IDs / new variability events remain UNVERIFIED.** The v1.9 time scale is provisionally UTC; observer-specific apparent sky position, radial velocity/perspective and topocentric data remain unmodeled.

---

# CURRENT SOURCE AND REFERENCE ACCESS — v1.8, 5 November 2026

**This v1.8 status supersedes the historical milestones below; older results are retained with their original dated limitations.**

- Official IRSA original 2,212 positional-cone photometric rows remain SHA-checked; they are **not physically confirmed Gaia/ZTF light curves**.
- Independent wider Gaia DR3 210-arcsec TAP sources returned **50 entries around FT Tau and 250 around CIDA 11**, allowing **3 and 5 conservative candidate reference selections** after quality, RUWE, brightness and isolation tests. These are **not authenticated clean PSF stars**.
- The real [v1.8 reference-image run](https://github.com/ismaelberja/stellarforge/actions/runs/42077605987) obtained **4 real target FITS Gaussian proxy fits and 13 valid candidate reference image fits out of 16 attempted reference cutouts**, all sharing the respective dated ZTF science archive product paths.
- With >=3 different Gaia candidate IDs, **three exposures** permit a provisional median signed east/north offset: FT Tau MJD 58491.184780 (+0.08708″,+0.01267″); CIDA 11 MJD 58475.113750 (+0.05232″,+0.05436″) and MJD 58849.135984 (−0.00793″,+0.02166″). A fourth frame had only one usable reference.
- No **independently validated WCS, empirical PSF or Gaia/ZTF crossmatch** has been obtained. Linear 2D Gaia proper motion ignores full covariance/parallax. CIDA 11 Gaia RUWE ~8.57 requires caution; small nominal residuals are not accuracy claims.
- Public GitHub contains only vetted aggregate data and code, not original Gaia TAP CSV responses, original individual ZTF photometry or FITS pixel arrays. [Detailed real v1.8 report](../reports/gaia_reference_v1.8/REAL_REFERENCE_CANDIDATE_EVIDENCE.md).

---

# CURRENT SOURCE/IMAGE ACCESS — v1.7, 5 November 2026

**This section supersedes the historical v1.6 and earlier access notes below; all previous observations are kept for chronology.**

- **Official IRSA raw photometry:** two SHA-checked 2-arcsec position queries, 2,212 ZTF rows (FT Tau cone 1,199 and CIDA 11 cone 1,013), six separate OID/filter groups. These are NOT independently confirmed Gaia/ZTF matches. See the [transport audit](../reports/observational_intake_v1.2/RAW_TRANSPORT_AUDIT.md).
- **Real ZTF science images:** the v1.7 verified run [42058770141](https://github.com/ismaelberja/stellarforge/actions/runs/42058770141) read **12 individual original science FITS pixel arrays**, **two independently different FITS files per OID/band**, 8 for FT Tau and 4 for CIDA 11. Each has provisional celestial WCS/radial-profile image checks; no reference coadd was used as a science epoch. 14 remote requests: 12 success, 2 URLError.
- **Descriptive repeated-epoch proxy:** pairwise differences between the two Gaussian centroid residual vectors within each OID/filter group **0.024–0.097 arcsec**. These are *not calibrated accuracy, physical motions or verified source association*: FITS WCS astrometric residuals and Gaia parallax/covariance remain unknown.
- **Same-field controls:** 90-arcsec cutouts yielded **zero science images with >=2 acceptable unclassified comparison image peaks**. This does not establish an empty field or source cleanliness; no empirical PSF can yet be scientifically calibrated.
- **Image shape:** 11/12 simple Gaussian target fits require residual review; one is provisionally acceptable under the simple model, but no source, binary or physical event is established. High Gaia DR3 RUWE for CIDA 11 (~8.57) remains a serious astrometric-model caution.
- **Scientific confirmations: ZERO:** physical source crossmatches, validated unblended fields, new companions, and real physical variability events all remain unconfirmed.
- **Public project/provenance:** [v1.7 real-image report](../reports/field_controls_v1.7/REAL_MULTIEPOCH_AND_CONTROL_LIMITS.md) and [v1.7 method limitations](PHASE17_SAME_IMAGE_CONTROLS.md). All source photometry and FITS pixels remain outside the public Git history; CI artifacts contain aggregate-only diagnostics.

---

# CURRENT SOURCE ACCESS — v1.6, 5 November 2026

**The following current status supersedes all earlier entries below; historical notes are preserved and must not be read as the latest status.**

- **Official IRSA/ZTF raw transport: completed for two position queries.** FT Tau cone: 1,199 photometric rows across four ZTF OIDs; CIDA 11 cone: 1,013 rows across two OIDs. Original raw SHA-256 hashes are recorded in the [v1.2 transport audit](../reports/observational_intake_v1.2/RAW_TRANSPORT_AUDIT.md), and source-identity evidence in the [v1.3 provisional astrometric report](../reports/astrometry_v1.3/PROVISIONAL_POSITIONS_REPORT.md).
- **Crossmatch identity is not confirmed:** a positional IRSA cone response, even with a close ZTF catalogue position, does not independently identify a Gaia star or exclude blends.
- **Independent Gaia DR3 field checks:** two 15-arcsec TAP cone queries each returned only the target DR3 entry, but no other catalogued Gaia source is not proof that the field is uncontaminated. CIDA 11's RUWE ≈ 8.57 is a major astrometric-fit quality concern; [v1.4 report](../reports/field_review_v1.4/GAIA_NEIGHBOURS_AND_IRSA_IMAGES.md).
- **Real ZTF imaging:** v1.5 validated pixels and header WCS in five of six OID-band groups using three individual science frames and two reference coadds. This is a provisional pixel screen, not a calibrated PSF or confirmed crossmatch.
- **Image-profile fits in v1.6:** three individual FT Tau science images were modeled with a robust single-Gaussian-plus-planar-background **proxy**. All three have substantial positive model residuals; 0 curves had at least two independently usable science images for repeatability. No CIDA 11 profile fit in v1.6; many IRSA requests were HTTP 503. See [real v1.6 audit](../reports/psf_v1.6/REAL_GAUSSIAN_FIT_REVIEW.md).
- **Scientific confirmations remain zero:** 0 verified Gaia–ZTF physical source identities, 0 proven unblended sources, 0 confirmed new physical events or disk classifications. Publisher-original Taurus parent table byte comparison remains open.
- **Public repository data policy:** archived source downloads and transient FITS pixels are not committed; use the authorized original archive and its checksums for reproduction. Public GitHub Actions artifacts contain only summary diagnostics; historical acquisition artifacts have a short retention period.

---

# CURRENT ACCESS STATUS (2026-11-04, v0.8)

- **Taurus catalogue data:** 24 real, provisional coordinate records in a pinned third-party copy of the 532-member Luhman (2023) adopted-members table. The original author's/publisher's file has not been byte-compared to the third-party mirror.
- **Verified raw IRSA ZTF light curves for Taurus:** **0**. No corresponding images or control-star observations have been obtained.
- **Secondary observational-format integration test:** an unrelated third-party public ZTF-style 8-epoch CSV was inspected offline: 6 QC accepted and 2 rejected by cloud/moon bit 15 (32768). Independent identity with the actual IRSA archive has **not** been verified; those data are **not Taurus** and no stellar variability claim is made. The raw third-party file is not included in the deliverable.
- **Time-axis compatibility:** original source examples contain MJD and HJD simultaneously. v0.8 validates the astronomical offset and uses the explicitly prioritized time column without conversion to BJD_TDB.
- **Cadence-only results:** mathematically exact fractions of event start windows containing k observed epochs; they cannot substitute for real-photometry injection-recovery or astrophysical detection completeness.
- The research gates remain source provenance, original IRSA downloads, Gaia/ZTF crossmatch with image checking, independent disk classes, field controls and physically interpretable validation.

---

# CURRENT ACCESS STATUS (2026-11-04, v0.7)

- Pinned third-party **Taurus member catalog copy** structurally checked in earlier phases, 532 member entries / 467 Gaia IDs; 24 positions in the working technical seed. Original publisher-byte comparison still pending.
- The **two-object FT Tau / CIDA 11 pilot** is a request plan built from real catalog coordinates; no ZTF observation timestamps or independent disk classifications have been retrieved.
- Raw original IRSA ZTF curves accessed in this environment: **0**. The source could not be queried because HTTPS/DNS access to IRSA is not available.
- The **528-event v0.7 recovery grid uses synthetic timestamps and magnitudes only**, never real survey cadence. Its diagnostic fractions are not survey completeness or false-positive rates.
- Upstream scientific gates: original table check, actual data downloads with stable hashes, epoch-aware astrometry plus image inspection, field controls and injection/recovery on actual survey observations.

---

# CURRENT ACCESS STATUS (2026-11-04, v0.6)

- The **24-coordinate Taurus technical seed** is derived from a pinned third-party copy of Luhman (2023) Table 2 (532 members, 467 Gaia DR3 identifiers). Its **publisher-byte identity remains unchecked**.
- Real *catalogue* positions and proper motions have been used for an illustrative J2021.0 astrometric displacement calculation, **not for photometric detections**.
- Actual ZTF/IRSA light-curve rows **retrieved in this environment: 0**. An outbound request to IRSA returned a DNS-resolution failure. This remains a technical restriction, not evidence of non-detection by ZTF.
- The 400-trial v0.6 vetting challenge and all example event curves are **fully synthetic**; do not use them to claim real ZTF reliability.
- The next scientific gate is actual IRSA light curves, an observational data release and original-file hashes, per-exposure astrometry, independent control stars, and original-catalog publisher reconciliation.

---

**Historical notes (below):** earlier-phase statements are preserved for reproducibility and should NOT supersede the current status above.

# V0.4 SUPPLEMENT — source access update, 2026-11-04

The following **supersedes the v0.3 statement that no real Taurus catalogue rows were available**. Through an authorized read of a public GitHub repository, we located a third-party copy of Luhman (2023) adopted-members **Table 2** (`ajac9da3t2_mrt.txt`). Its fixed-width rows have been inspected with 532 adopted members, 467 **unique** Gaia DR3 IDs, 65 members without Gaia DR3 IDs, 13 named kinematic groups and 119 empty group values. This agrees with the published paper, but does not establish independent byte equality with the publisher's original file.

Pinned public copy: https://github.com/themariavincent/get_targets/blob/7b6a5c83eca81fc66e50cb4889ee35cb28861367/taurus_sources.txt
Git blob: `fe0d5a43dbd2ca8b867901686ab223a847c649e5`.

24 catalog coordinates have now been extracted, with published line indexes and other metadata, to `data/research_seed`. They are **real source positions** but *not* a final scientific disk-class sample. The complete raw mirror is not stored locally, because outbound DNS from the local container is disabled; a hash-checked downloader is now implemented in `src/stellarforge/luhman2023.py`. A 24-object IRSA query plan has been produced, but **no real ZTF curve has been downloaded**. Details: [Phase 4 technical report](PHASE4_FIRST_REAL_CATALOG_AND_VARIABILITY.md).

---

# Original observational catalogue retrieval — audit status, 2026-11-03

**No original Taurus member list or genuine ZTF light curves have been imported in this development environment.** This restriction remains in v0.3. Automated tests and bundled examples contain **synthetic engineering records only**.

## Bibliography checked

- Luhman, K. L. 2023, *AJ*, 165, 37, DOI:10.3847/1538-3881/ac9da3: **532 adopted Taurus members** in Table 2, **467 Gaia DR3 entries**, **412 Gaia DR3 parallax+proper-motion solutions**, **13 kinematic groups**. This publication defines our Taurus population.
- Cody, A. M., Hillenbrand, L. A. & Rebull, L. M. 2022, *AJ*, 163, 212, DOI:10.3847/1538-3881/ac5b73: published study of variability morphologies in **99 young disk-bearing Taurus members** observed by K2; comparison literature, **not independent ZTF data or proof of new detections**.
- Official ZTF photometry API https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html; flags and `oid` distinctions are corroborated by https://irsa.ipac.caltech.edu/data/ZTF/docs/releases/dr06/src/dr06.html.

## Why the observational input remains blocked

The complete **Luhman (2023) Table 2 machine-readable file** was not retrievable through the research access tools available here. Outbound DNS/networking from the local file-building environment is blocked, so the module was tested with synthetic inputs. A plausible URL, individual star names found in the paper, a Gaia positional cone search or a 532-row mock table **do not constitute** the genuine published census.

**Important:** The author provides machine-readable supporting material, but the exact verified file/release/byte checksum is still unresolved. We should not claim source retrieval or dataset completeness until we can inspect its header, actual contents and row count.

## Safe execution protocol for the next data-enabled stage

1. Secure author/publisher's machine-readable Table 2 (e.g. through the article's published tables). Preserve its original bytes, download URL and SHA256.
2. Audit the original rows, associations and paper-matching counts (532 adopted, 467 Gaia entries). Identify missing/duplicated identifiers and stars without Gaia data.
3. Normalize positions, epochs, source IDs and disk classes with a reviewed mapping; independent literature support is required for disk labels.
4. Freeze a small, prespecified disk-stratified sample **before examining variability**.
5. Download a handful of real ZTF light curves, validate exact output format on each release, then feed the downloaded files to `stellarforge inspect-ztf`.
6. Record successes, non-detections, blends, missing observations and rejected epochs; do not collapse missing and zero-variability cases.

## Result of this iteration

- Implemented an offline ZTF raw-to-normalized processing stage (CSV and fixed-width IPAC table).
- Implemented detailed per-OID/band/time-scale QC, ambiguity flags, retained outliers, and SHA256 consistency checks.
- Implemented an offline CLI command and explicit synthetic fixture to verify the program runs end to end.
- **No actual stellar measurements, light curves, morphology classifications, ML models or new candidates have been produced.**


## Update 2026-11-04: v0.9 observational evidence gate

- Retried the official IRSA ZTF light-curve API for FT Tau and CIDA 11 with `POS=CIRCLE`, two bands and the `32768` quality mask. Both requests failed at the network/DNS level (`URLError`) **without receiving observation bytes**. This says nothing about actual survey coverage.
- The first-target dossiers and static observation-readiness dashboard are in `reports/observational_gates_v0.9/` and are explicitly marked as PENDING.
- The new per-epoch astrometric screen is an approximate engineering aid; real counterpart confirmation and source/image review have not occurred.
- All 303 tests pass. Neither genuine Taurus ZTF light curves nor independent disk labels were acquired in v0.9.