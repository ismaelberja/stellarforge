# Research log — decisions and observations

## Entry 0001 — project initiation, 2026-11-03

**Decision:** Build StellarForge as a combined astrophysical research program and professional scientific-computing/data-engineering showcase, not as a one-day portfolio template.

**Chosen pilot:** variability of the literature-defined Taurus young-star population; Gaia DR3 and ZTF optical time series; extension to other regions only after quantified pilot selection effects.

**Verified externally:** Luhman (2023) describes 532 adopted members; Gaia DR3 epoch photometry is obtained using DataLink for eligible sources; IRSA offers an official ZTF light-curve API and recommends scalable approaches for >~1,000 light curves. The published Gaia YSO catalogue has known sample contamination and incompleteness, making it unsuitable as unquestioned independent truth.

**Engineering result:** initial package with 24 passing offline/mock tests for coordinate checks, API planning and provenance. **Not an astronomy result.**

**Open scientific decisions:** first event morphology (rotation, dipping, bursting, general anomalies), precise pilot target roster, independent class/disc references, accepted photometric quality cuts.

**Blockers before any scientific conclusions:** exact Luhman catalogue machine-readable copy, real survey response validation, astrometric epoch matching and selection-function analysis.

## Next entry template

- Date/commit:
- Decision requested by scientific lead:
- Original dataset/version and query:
- Result (including failures/missing sources):
- Figure/evidence path:
- Validation and uncertainty:
- Next scientific decision:

## Entry 0002 — source audit and preliminary pilot selection, 2026-11-03

**Scientific direction:** dippers/bursters prioritized, with rotation/periodicity as secondary diagnostics. This is a focus on *candidate morphologies*, not physical attribution from brightness changes alone.

**Publication facts:** Luhman (2023), Table 2 contains 532 adopted members; text reports 467 Gaia DR3 entries and 412 Gaia DR3 astrometric solutions. Sample incompleteness must be explicit.

**New code:** `catalog.py` validates external curated member tables with explicit nullable Gaia IDs, coordinate epoch and references; records SHA256 and an audit. `pilot.py` constructs reproducible proposed 12+12 disk-class strata only when vetted labels and eligibility permit; it never automatically approves a science sample. `gaia_batch.py` builds exact-ID Gaia TAP queries without calling the archive.

**Verification:** 48 passing offline engineering tests, including invalid identifiers, non-finite positions, missing Gaia IDs, synthetic strata and deterministic sample proposals. All source-specific test records are clearly synthetic.

**Blocking limitation:** the complete official author/publisher machine-readable Table 2 has not been retrieved or manually reconciled. No scientifically verified Taurus target roster or real light curves exist. There is no evidence for a new dipper, burster or new period.

**Research gate:** obtain, preserve and reconcile the original Table 2; trace disk classes to an independent source; freeze the pilot before inspecting ZTF data. See `docs/CATALOG_IMPORT_CONTRACT.md` and `docs/PILOT_SELECTION_PROTOCOL.md`.

## Entry 0003 — source retrieval attempt, ZTF photometry QC, 2026-11-03

**Research finding from published literature:** Luhman (2023) confirms 532 adopted Taurus members, 467 entries in Gaia DR3 and 412 DR3 astrometric solutions; we must not silently discard members with no Gaia source ID. Cody et al. (2022) characterizes variability morphology among 99 Taurus disk-bearing K2 targets, providing reference methods for a later comparison, not ZTF outcomes.

**Acquisition status:** Retrieval of the complete publisher Table 2 was attempted through available web/public interfaces but was **not successful**. Local runtime DNS resolution is unavailable. No observed Taurus targets, coordinates or light curves have been installed. This is a formal blocker, not something to paper over with mock data.

**New engineering:** `ztf_photometry.py` accepts official IRSA CSV and IPAC-style tables; validates the essential columns; preserves OID strings, filter and time-scale distinctions; applies a documented bitwise mask; reports row-level rejections; protects against accidental outlier clipping of possible dipper/burster events; and detects two potential ZTF OIDs at a single position/band. CLI now supports offline `inspect-ztf`. File-based audits record the original content digest and fail if it differs from a saved provenance sidecar.

**Validation:** 79 automated tests pass offline, including synthetic ambiguous source matches, wraparound RA, invalid uncertainties, tabular parsing, flags, time-scale isolation, corrupted raw files and QC export. An end-to-end dry-run with synthetic observations generated a JSON report and normalized CSV. **No inference from synthetic photometry is presented as astrophysics.**

**Next scientific gate:** independent verification of the 532-member Table 2 and disk classifications, then actual ZTF data ingestion and epoch-aware matching. Read `docs/ZTF_PHOTOMETRY_QC.md` for the evidence checklist.

## Entry 0004 — real Taurus member positions and preliminary variability diagnostics, 2026-11-04

**New actual source evidence:** a full public GitHub copy of the 2023 Luhman Taurus Table 2 was inspected through the research GitHub connection. Its header identifies `ajac9da3t2_mrt.txt` and its 532 fixed-width member rows contain 467 unique Gaia DR3 IDs. Named groups: 13; records with no group value: 119. The mirror's exact immutable commit and Git blob hash are recorded. The publisher's source bytes have not been independently compared, so this is structural corroboration, **not final authoritative byte-level validation**.

**Technical roster:** 24 authentic published source positions from the pinned mirror, all Gaia-referenced, across 13 groups. This is a brightness-biased engineering sample, deliberately not the final Class II/Class III population and not used to report prevalence. A source-coordinate sky map and 24 unexecuted official ZTF URLs have been created. Local outbound archive requests are blocked, so no ZTF light curve or physical period is claimed.

**Scientific engine:** preliminary uncertainty-weighted constant-brightness diagnostics, magnitude-tail asymmetry proxy, generalized weighted Lomb–Scargle period scan, sampling-window flags, seeded white-noise permutation diagnostic, strict separation of source/filter/time convention. Explicitly does not assign morphology or physical periods.

**Simulation:** 24/24 recovered high-SNR injected 5.271-day periods; 24/24 recovered with designed seasonal gaps; **15/24** in sparse low-SNR simulations. This shows an actual failure regime rather than only positive demonstrations. Simulated cadences and white noise are not real ZTF completeness or sensitivity.

**Verification:** 109 passing unit and integration checks; sample provenance and full benchmark settings in versioned research docs.

**Next blocking scientific decision:** original publisher byte-check, external independent disk classes, actual ZTF observations, physical cross-matches and validation using real survey cadences.

## 2026-11-04 — v0.7 selection-function engineering

Created a reproducible 528-trial synthetic detection-efficiency grid, with stratification by injected amplitude, duration, photometric noise and observation opportunity; added Wilson intervals and false-alarm/artifact controls. Prepared a real-literature two-target *query plan* for FT Tau and CIDA 11. IRSA observations acquired: zero. Software test suite: 210 passed. Do not publish scientific occurrence or completeness claims from this model. See `PHASE7_INJECTION_RECOVERY_AND_OBSERVATIONAL_READINESS.md`.


### 2026-11-04 · Version 0.9 observational evidence screen

- Implemented a new epoch-by-epoch approximate Gaia/ZTF positional consistency engine and deliberate multiple-OID ambiguity gates, preserving all bands separately.
- Attempted official FT Tau and CIDA 11 ZTF requests: both failed with `URLError` due to environment network restrictions. Recorded in the new observational-evidence report. This is **not** a ZTF coverage test.
- Generated two status dossiers and an offline dashboard plus catalogue-propagation plot. No new observational signal, scientific period, source identification or physical event classification claimed.
- Ran 303 tests, all passing; added independent tests of sidecar integrity, fake IRSA URLs, ambiguous OIDs and physical-claim suppression.
- Next scientific gate remains official-source acquisition and manual image/astrometric vetting.