# R1–R6 practical research milestones

**Latest R2 status (11 November 2026):**
[Original IRSA query diagnosis](R2_REAL_IRSA_22_FAILURE_DIAGNOSIS_RESULTS.md)
recovered **13 of 22** previously unavailable positional response
tables using the *unchanged* original IRSA query shape, for **15
of 24** cumulatively accessible technical sky positions across
the earlier and current runs. **Nine** remain unresolved (eight
timeouts, one valid zero-row response to a restricted query);
the alternate NUM_OBS=1 requests all returned HTTP 400.
The [24 exact Gaia ID query](R2_REAL_GAIA_24_EXACT_ID_SCREEN.md)
returned 24/24 sources, 17 passing provisional Gaia-only
astrometric flags. **R2 is not complete** because independently
verified Gaia-to-ZTF physical source identities, original image
crowding and publisher literature membership still remain open.
None of the access failures are astrophysical nondetections.

There are **six planned increments in total** for a modest, bounded
**independent Taurus optical-variability feasibility study**. This is
a planning estimate, not a promise of a new detection, independent
PSF calibration or journal paper.

| Phase | Work | Acceptance criterion |
| --- | --- | --- |
| **R1** | Freeze question, 24-row technical seed and selection bias/limitations before new variability results | Reproducible 24-row pre-registration with 0 verified physical crossmatches; offline tests |
| **R2** | Literature and original Gaia/ZTF source identity screens | Source-by-source association/ambiguity ledger, no silently merged OIDs |
| **R3** | Original clean survey photometry and quality controls | Per-band time-series coverage and access ledger, explicit >0 scientifically usable source count *or blocker* |
| **R4** | Periodicity, variability and comparison-star/null statistics | Authenticated source-level diagnostic figures + independent control/alias discussion |
| **R5** | Original FITS image review, reproducibility, literature novelty check | Falsification/sensitivity report, candidate/negative status honestly classified |
| **R6** | Final technical research report and public presentation | Audited methods and limitations, final figures, defensible CV/LinkedIn text; publication only if scientific originality survives review |

**R1 is software/protocol groundwork, not a new astronomical result.**
If source identification fails or IRSA access is unavailable,
the research programme can end in a documented inconclusive/negative
feasibility report. Extra investigation beyond R6 may be essential
for a publishable discovery and cannot be numbered in advance.

The v2.0 engineering portfolio is **already publishable on LinkedIn**
as Python/data engineering work. Waiting for R6 is a choice only if
the goal is to present an additional independent *science investigation*
with genuine results rather than an unfinished scientific claim.
