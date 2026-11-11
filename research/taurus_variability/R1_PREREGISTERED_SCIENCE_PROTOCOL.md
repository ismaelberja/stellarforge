# StellarForge / Taurus — independent optical-variability study

**Research phase R1 · 11 November 2026 · PRE-REGISTERED TECHNICAL COHORT ONLY**

**Release separation:** StellarForge v2.0.0 is already finished as a software
portfolio. This is a distinct optional **astronomical study**, not a change
to the verified engineering-release claims.

## Research question

> Can the optical variability of a small, predeclared set of
> literature-associated Taurus young-star candidates be characterised
> reproducibly from public Gaia DR3 and ZTF light curves, while
> accounting for source association, survey sampling and observational
> uncertainty?

This is a **feasibility and methodological comparison study**, not a
predeclared hunt for new companions, new stars, or a robust Taurus-wide
variability incidence. A scientifically interesting *null* or a
methodological limitation is a legitimate outcome.

The independent 2026 work by Mas et al., A&A 705, A172,
[DOI: 10.1051/0004-6361/202554522](https://doi.org/10.1051/0004-6361/202554522)
applies Q–M variability morphology tools, GLS and structure functions
to Gaia DR3 young-star samples. **Its findings and any relevant
Taurus/ZTF studies must be compared before claiming novelty.**
No result derived by StellarForge is original solely because the
Python code was written independently.

## Frozen initial technical cohort

**All 24 pre-existing** secondary-Luhman-mirror technical seed
rows in
`data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv`
are included without looking at variability amplitude, period,
periodogram or morphology. This is *not* a newly chosen
scientific sample: the seed was previously constructed using
magnitude and group criteria and is deliberately **nonrepresentative**.
The publisher-original catalogue has not been byte-matched and
individual Taurus memberships are not automatically authenticated.

The R1 script builds a deterministic, signed-hash manifest of
the entire 24-row cohort, preserving Gaia source IDs and
the original literature-mirror row. It states explicitly that
**zero Gaia/ZTF physical source matches and zero new variable stars
are confirmed** in R1. It must not down-select on periodogram
strength or visual appearance.

```bash
python scripts/prepare_taurus_variability_r1.py
```

Output (ignored by Git because no new real source inputs should be
committed): `reports/generated/taurus_variability_r1_predeclared.json`.

## Acceptance gates for next phases (no invented completion)

1. **R2: Identity & eligibility.** Verify exact publisher literature
   membership, applicable Gaia DR3 astrometry (including high-RUWE,
   multiplicity and nearby source risks), per-epoch proper-motion
   propagation, exact ZTF OID/band identity, and *independent* image
   and catalogue crowding checks. A nearest position within a cone
   is NOT sufficient. Unresolved cases count as **ambiguous**,
   not negative or variable.
2. **R3: Original photometry and quality.** Retain per-object, band
   and time-system separation; capture query URL, archive release,
   byte digest, original flags, photometric uncertainty, number
   of observations, seasonal coverage and failed requests. The
   initial eligibility screen for a single OID/band is **at least
   30 QC-accepted visits** and a **90-day baseline**, fixed
   before reviewing target variability. Report all target-level
   rejections and exposure/date gaps; never mix HMJD/HJD/MJD.
   These limits are *pilot choices*, not universal science rules.
3. **R4: Variability controls.** Measure amplitude, robust scatter,
   error-weighted chi-squared, period candidates, cadence window
   function and season-by-season sensitivity. Build same-field
   magnitude-matched non-YSO controls when physically identifiable;
   compare ZTF filters when possible. False-alarm/permutation
   results do not automatically model red-noise correlations.
   Do **not** assign dipper, burster or spot modulation from a
   single automatic score.
4. **R5: Independent validation & literature.** For each reported
   target, review original FITS/masks, crowding, blended PSFs,
   alternative OIDs, periodic aliases and any Gaia variability
   evidence. Compare relevant published results, quantify
   selection effects and uncertainty, generate authentic figures
   from recorded datasets, and attempt falsification. If no
   source survives, publish only a transparent feasibility/negative
   report and do not report a Taurus population rate.
5. **R6: Final research outcome.** Freeze exact code commit,
   archive provenance, acceptance/rejection ledger, real figures,
   uncertainty tables, limitations and a concise manuscript-style
   report. A journal submission is optional and requires a
   scientifically meaningful novel contribution and external
   scientific critical review. No guarantee of publication.
   The finished study may be described honestly on LinkedIn as
   an *independent observational feasibility research project* even
   if it ends with inconclusive results.

### Scientific reporting labels

Allowed: `TECHNICAL_CANDIDATE`,
`PHYSICAL_SOURCE_IDENTITY_PENDING`,
`QC_ACCEPTED_PHOTOMETRY_ONLY`,
`PERIOD_CANDIDATE_REQUIRES_REVIEW`,
`INDEPENDENTLY_REVIEWED_VARIABILITY`,
`INSUFFICIENT_DATA`, `AMBIGUOUS_SOURCE`,
`ARCHIVE_UNAVAILABLE`.

Not allowed without additional evidence: `NEW_VARIABLE_STAR_FOUND`,
`COMPANION_DETECTED`, `TAURUS_VARIABLE_FRACTION_MEASURED`,
`INDEPENDENT_ZTF_PSF_CALIBRATED`.

## Inputs & reproducibility

- Luhman (2023), AJ 165, 37, DOI
  [10.3847/1538-3881/ac9da3](https://doi.org/10.3847/1538-3881/ac9da3)
  (currently a pinned third-party mirror; publisher check pending).
- [Official Gaia DR3 archive](https://gea.esac.esa.int/archive/).
- [Official ZTF/IRSA lightcurve API](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html)
  and [survey image metadata](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_api.html).
  Multiple ZTF object IDs can occur at one sky position; do not
  merge them without a validated source interpretation.
- Mas et al. (2026), A&A 705, A172 (variability morphology
  comparison; does not validate this exact technical pilot).

**As of this R1 phase:** no independently reverified physical
Gaia-to-ZTF association or new variability analysis is recorded.
No astronomical scientific paper is claimed.
