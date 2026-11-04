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