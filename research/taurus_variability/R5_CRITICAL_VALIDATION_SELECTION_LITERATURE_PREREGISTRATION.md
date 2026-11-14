# R5 — preregistered independent-source literature, selection-function and falsification audit

**14 November 2026 (before new R5 summary statistics, figures or release claims).** This is a bounded critical-review phase, **not** retrospective source selection or an independent physical Gaia–ZTF calibration. The aim is to determine which claims from R1–R4 remain defensible and which R6 hypotheses must be marked **not supported**.

## Frozen observed scientific inputs

Only the previously merged, original-source SHA-anchored evidence enters the R5 numerical audit:

- R1 24 technical Gaia seed, SHA-256 `9cecb94704f028a981045629ad16ecb770f51bba4b6bb3bf13dda769327ff37e`, not a random Taurus census.
- Original-author Luhman (2023) AJ 165, 37 Table 2 532 adopted members and 467 Gaia IDs; authentic original publisher retrieval and **24/24** frozen Gaia catalogue ID+position matches, *not physical ZTF identity*.
- R2 original 24 Gaia target-identity ledger, with 17/24 preliminary Gaia astrometry passes, 7/24 review, 4/24 catalogued nearby Gaia neighbours within 5 arcsec, 22/24 original IRSA positional-response successes, **0/24 independent physical source matches**, 0 merged original ZTF OID physical-star curves.
- R3 original public ZTF DR24: six **original survey ObjectIDs / two working Gaia labels**, not six independently verified stars; **three** sources yield valid CSV (684 source photometry *rows*, 591 locally QC-retained observations, 93 source flag bit15 rejected), **three** original API timeouts and identical fixed-ObjectID retry timeouts. The original `catflags & 32768` QC is **an initial quality screen**, not equivalent to `catflags=0` and not sufficient to certify total independence or accurate instrument/blend calibration.
- R4 three real ObjectID **relative** 365-day bins: two have two full consecutive zero-accepted-visit bins, one has all bins nonempty; three other ObjectIDs have **unknown coverage**, not zero. R4's 1-day mathematical window examples were built using **fully synthetic individual timestamps**. No actual ZTF per-exposure timestamps exist in public source evidence, so R4 has **not** measured actual source windows or real periods.

## Frozen independent reference set, independently looked up for scope and caveats

These are existing **publications/documentation**, not a fresh Gaia–ZTF physical star match:

1. **Luhman (2023), AJ 165, 37**, *A Census of the Taurus Star-forming Region and Neighboring Associations with Gaia*. Author-published Table 2 original verification already performed and source SHA preserved in R2. Original journal record: `https://doi.org/10.3847/1538-3881/ac9da3`, author original tabular source `https://content.cld.iop.org/journals/1538-3881/165/2/37/revision1/ajac9da3t2_mrt.txt`.
2. **Mas et al. (2026), A&A 705, A172**, *Exploring the variability of young stars with Gaia DR3 light curves*, `https://doi.org/10.1051/0004-6361/202554522`, published 19 January 2026. This study already implements Gaia YSO Q/M, GLS, selection/error controls and explicitly discusses observed ZTF **one-day aliases**, so StellarForge must **not claim novelty of Q–M, GLS or daily-alias awareness**. Its samples do not establish an R2 physical match for this particular fixed Taurus pilot; no source-level crossmatch with it is claimed.
3. **ESA Gaia DR3 source model reference**, `https://gea.esac.esa.int/archive/documentation/GDR3/Gaia_archive/chap_datamodel/sec_dm_main_source_catalogue/ssec_dm_gaia_source.html`: `ruwe` is a renormalised *single-star astrometric solution goodness-of-fit* indicator. Flagged high RUWE is *review*, neither a proof of binarity nor a calibrated matching probability.
4. **IPAC/IRSA ZTF DR24 official release portal**, `https://irsa.ipac.caltech.edu/Missions/ztf.html` (public DR24 dated 22 Jan 2026), and **official ZTF lightcurve API**, `https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html` (multiple original ZTF ObjectIDs may exist at one sky position; `ID` vs positional lookup and `COLLECTION` are different request contracts).
5. **ZTF public release HTML explanatory flags**, `https://irsa.ipac.caltech.edu/data/ZTF/docs/releases/dr06/src/dr06.html`: `catflags & 32768` removes probable overall-image quality failures; `catflags=0` is stricter and may exclude *additional source-level* issues. Do not relabel bit15-only accepted data as "perfectly clean."

Official source titles and linked URLs were reviewed against their original public descriptions; references **do not replace** original source-level instrumental/matching validation. Future access or bibliographic changes must be reviewed rather than silently replaced.

## Before executing, fix these exact calculations and denominators

- `24/532` selected technical source count vs **author adopted Taurus members**, and `24/467` vs adopted Taurus members with Gaia ID. **Descriptive exposure only**; neither is a probability sample or a representative population "completeness rate".
- `17/24`, `7/24`, `4/24`, `22/24`, `0/24`: Gaia-only flags, astrometric review, local Gaia 5-arcsec catalogue neighbour presence, ZTF original **positional-response** access, and original *independent physical match*. None of these denominators interchange.
- `3/6` original exact ZTF ObjectID source CSV access; **do not** equate six original ObjectIDs with six physical stars. `591/684` original per-epoch quality-bit15 source row **retention** and `93/684` original bit15 failures, with no unique-star count inferred.
- `2/3` actual retrieved ObjectID time series with at least two consecutive entirely empty **within-span relative 365-day bins**, **not** fraction of Taurus YSOs with temporal gaps.
- Print exact numerator, denominator, **round percentages only after exact integer-ratio validation**. Do not compute inferential confidence intervals, selection-corrected regional incidence, astrophysical variability rates, or physical binarity significance on this nonrandom sample.

## Falsification matrix and independent-science acceptance

Record source/claim severity and the **missing independent evidence** for: original adopted census provenance, Gaia single-star astrometric uncertainty, Gaia-to-ZTF per-epoch source identity, PSF/WCS/reference-star calibration/deblending, source-level photometric error/covariance, pure bit15-versus-`catflags=0` sensitivity, original observation timestamps and window aliases, source/epoch gaps and archives, comparator-star matching and target selection bias, external literature overlap/novelty.

**Hard gates, unchanged from R1:** No physically accepted target variability without validated identity, raw original time/mag/error observations for matching source/band/clock, instrument independent QA, a defined same-field non-YSO control and defensible false-alarm/window sensitivity. If missing, set `R5_INDEPENDENT_PHYSICAL_VALIDATION=NOT_MET`, `R5_CRITICAL_FEASIBILITY_REVIEW=COMPLETE`, `R6_AUTHENTIC_NEW_STELLAR_DISCOVERY_PERMITTED=false`, `R6_METHOD_FEASIBILITY_MANUSCRIPT_PERMITTED=true`, **not R5 astrophysical validation success**.

Use only offline synthetic fixtures for adversarial tests; keep public numerical results derived from original-source receipts. Include a self-contained data-derived figure that differentiates the **three different denominator types** (Gaia target IDs, survey ObjectIDs, and per-epoch survey measurements) instead of a false single attrition funnel. Link original sources, limitations and verdict. No unpublished TFM/ALMA science, raw original ZTF photometric values or original FITS CCD pixels committed.
