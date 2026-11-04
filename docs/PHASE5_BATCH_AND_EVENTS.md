# Phase 5 — Reproducible ZTF acquisition and candidate-event screening

**Version:** 0.5 | **Status:** technical development and synthetic validation; **not** Taurus variability science.

## Scientific question

Can we implement an auditable, small-sample workflow that (i) requests public ZTF photometry for literature-identified Taurus positions without confusing catalog identity and IRSA cone-search proximity; (ii) filters survey-quality problems; and (iii) flags potentially interesting fading or brightening **episodes**, subject to later physical and instrumental validation?

## Source population

The technical target coordinates are the 24-row subset extracted in v0.4 from a version-pinned third-party GitHub copy of the machine-readable adopted-members table in Luhman (2023, AJ, 165, 37, DOI: 10.3847/1538-3881/ac9da3). The source copy has 532 members, 467 Gaia DR3 IDs and 13 named kinematic groups. The mirror has not been byte-compared to the publisher's original.

**These 24 targets are a technical selection, NOT a complete, random or disk-stratified science sample.** Their use in a pilot does not estimate the Taurus population's dipper/burster incidence. Independent disk classes have not been attached.

## Acquisition gates

- `stellarforge batch-ztf`: **dry run by default**. Produces `BATCH_MANIFEST.json` with 24 official IRSA query URLs and provenance.
- `--execute`: opt-in retrieval only. Uses bounded retries, a pause between requests, and an immutable SHA-256-verified raw-response cache; output labels remain `unverified_source_association`.
- Every target query uses a small 2-arcsec cone on its catalog position, g/r passbands and `BAD_CATFLAGS_MASK=32768`. This is an **acquisition search**, not astrometric identification: Gaia motion from its reference epoch to each ZTF epoch still needs to be propagated, and nearby candidates/images need inspection.
- IRSA returns multiple `oid` entries per cone when relevant. v0.3 separates `oid`, band and time convention and reports ambiguities rather than merging them.
- No single ZTF magnitude is directly compared to Gaia G/BP/RP: zero points and bandpasses differ.
- A failed service response or a missing target is recorded, not replaced with simulated data.

**IRSA documentation:** https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html (CSV/IPAC return, `BAD_CATFLAGS_MASK`, `oid`, query format). ZTF catalog DOI: https://doi.org/10.26131/IRSA598.

## Exploratory episode screen

Let \(m_i\) be observed magnitude (higher means fainter), \(\sigma_i\) the measurement uncertainty and \(\tilde m\) the median. Define a robust scatter floor from MAD and the median uncertainty. A measurement is flagged if its deviation exceeds both an amplitude threshold (default **0.18 mag**) and a **4-sigma proxy** using the local uncertainty and robust scatter. An episode requires **at least two flagged observations of the same sign** within a maximum gap of **4 days**.

- **Positive excursion** (higher magnitude) = fading *candidate*; not confirmed dust extinction.
- **Negative excursion** (lower magnitude) = brightening *candidate*; not confirmed accretion.
- A one-observation spike is recorded as a trigger but is **not** promoted to an episode.
- Results include the start/end times, observed lower-bound duration, number of epochs and maximum measured excursion. Integrated excursion is an observational heuristic, **not radiated energy**.
- A magnitude asymmetry statistic `M` is calculated with a clearly specified 10%-tail convention, inspired by Cody et al. (2014). This is **not** by itself a physical classification; Cody-style `Q` is left for a separate, fully validated module.

References to distinguish candidate photometry from physical interpretation:
- Cody et al. (2014), *AJ*, 147, 82, a morphology scheme for young-star light curves.
- Bredall et al. (2020), *MNRAS*, 496, 3257, ASAS-SN dippers in Lupus: https://academic.oup.com/mnras/article/496/3/3257/5855495.
- Froebrich et al. (2022), *MNRAS*, 514, 2736: https://academic.oup.com/mnras/article/514/2/2736/6595342.

## What the current validation **actually** demonstrates

The `scripts/run_synthetic_event_validation.py` script performs **60 deterministic simulation trials in each of seven scenarios** (420 trials). See `reports/validation_v0.5/SYNTHETIC_event_stress_test.json` and the accompanying charts. It varies injected fading/brightening, sparse sampling, amplitude, noise, a pure white-noise control and a deliberately bad instrumental-calibration control.

**This is a coding/algorithm stress test with artificial signals and cadences.** It does not measure a scientific completeness or purity for Taurus and cannot establish the number of real dippers or bursters.

Crucially, a coherent offset of several synthetic measurements triggers the detector even though it is instrumental. This is a useful demonstrated failure mode, **not a stellar discovery**. No actual ZTF photometry was downloaded in this environment because outgoing network access to IRSA was unavailable.

## Required next phase before any astrophysical claim

1. Execute a small set of real IRSA queries in a network-enabled environment; preserve complete service responses, request metadata, checksums and failure logs.
2. Inspect survey images and carry proper-motion-propagated cross-identification per target/epoch, with a documented ambiguity policy.
3. Establish independent IR excess/disk membership classification and remove unsafe blending/crowding cases.
4. Verify candidate events across filters/independent cameras when feasible and quantify residual instrumental false-positive rate.
5. Inject synthetic events **into the real observation cadences**, not just toy uniform random timestamps; benchmark amplitude/duration completeness and selection biases.
6. Only then freeze a science sample and publish descriptive incidence statistics and literature-based cases.

**Decision gate:** no confirmed dipper/burster labels, catalog paper, model training, or public-facing discovery claims until steps 1–5 have evidence.