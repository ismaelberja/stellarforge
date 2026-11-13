# Taurus R2 — 24-source closure protocol (pre-audit, 13 November 2026)

**Question:** Has the preregistered, nonrepresentative 24-source Taurus technical cohort accumulated enough independent evidence for a reproducible **Gaia DR3 → physical ZTF source** attribution, sufficient to hand individual bands/ObjectIDs to R3? If not, report a conclusive **R2 eligibility-screen NO-GO** with exact reasons, not invented source matches or negative variability.

## Frozen inputs, denominators and provenance

- The 24 original technical Gaia IDs from `data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv`; cohort SHA-256 `9cecb94704f028a981045629ad16ecb770f51bba4b6bb3bf13dda769327ff37e`. No astrometric/variability-based reselection.
- Original Gaia exact-ID 24-source run [43029175432](https://github.com/ismaelberja/stellarforge/actions/runs/43029175432), source-derived ZIP SHA-256 `cebb49029dd33fc6a369db2af0e8c5324af32895355748c8bb998b7bc2325a82`, individual per-source no-raw Gaia flags from that original artifact.
- Gaia 15″ neighbor and two initial ZTF positional-query source run [43031689454](https://github.com/ismaelberja/stellarforge/actions/runs/43031689454), source-derived ZIP SHA-256 `8a3028ebfc9575f1599074ae9addbfc118e19dea836e915af58a1cbbe23bc3f8`, individual no-raw neighbor counts. **No Gaia catalogue source within 2″** is not high-resolution image deblending.
- Original 22 failed-position diagnosis run [43037800319](https://github.com/ismaelberja/stellarforge/actions/runs/43037800319), immutable 24-member per-request ledger; follow-up exactly nine fixed remaining positions [43042786341](https://github.com/ismaelberja/stellarforge/actions/runs/43042786341), immutable per-request ledger. **22/24** have *at least one original positional CSV with rows*, **two** are unresolved (zero rows under NOBS_MIN=5 vs HTTP 400 under NOBS_MIN=1). Never sum positional CSV *rows* as astrophysical stars.
- FT Tau real 4 historical and six later fixed original g/r ZTF images, original PSFcat/science/mask; CDS SIMBAD historical name ↔ Gaia DR3 149623711269425408 exact alias, same-database lookup not an independently calibrated astrometric source measurement.
- Publisher original Luhman (2023) AJ 165 37 Table 2 byte comparison and individual physical memberships **unverified** unless an independently retrieved official machine-readable table validates exact original Gaia IDs / individual rows. Do not infer from paper abstract 532.
- The original 0.5 ≤ native χ ≤ 1.5 source acceptance and 5/8 PASS, 3/8 FAIL, 1/4 passing early/late source pair decisions remain frozen. No post-hoc source/epoch or χ gate changes.

## Fail-closed per-source labels

1. `IRSA_POSITIONAL_ROWS_AVAILABLE_NO_IDENTITY` only when the corresponding original provider call recorded parsed ZTF rows on at least one historical run. Multiple original OIDs/filters remain unmerged. A populated positional cone is *not* an authenticated physical Gaia–ZTF counterpart.
2. `NO_ROWS_AT_NOBS_MIN_5` when an original provider CSV returned zero under that exact query restriction; it does **not** prove an empty sky or non-variable star.
3. `HTTP_ERROR_AT_NOBS_MIN_1` when the last provider query failed with HTTP 400; no survey non-detection claim follows.
4. `GAIA_ASTROMETRY_REVIEW` when the original Gaia RUWE is ≥1.4 or exact-ID preliminary Gaia-only source-astrometry gate failed. No physical binary interpretation.
5. `INDEPENDENT_GAIA_ZTF_IDENTITY_NOT_AUTHENTICATED` remains true for every source lacking independently calibrated source-level positional/PSF/deblend proof. A SIMBAD alias, nearest same-pipeline ZTF source, or unreviewed original FITS is not sufficient.
6. `R3_PHYSICAL_SOURCE_TIMESERIES_ELIGIBLE` requires an independently reviewed physical Gaia–ZTF association, corresponding original ObjectID/band, acceptable image-level original QA and 30 accepted observations over ≥90 days under R1. Never infer this from access counts; until independently verified, **zero are released**.

## Acceptance of R2 study deliverable

A complete deterministic **24-row accession + ambiguity + source-quality ledger**, immutable links to original study sources, explicit per-source blockers, exact aggregate reconciliations and falsification tests constitute **R2 screening adjudication complete**; **they do not constitute R2 positive source-identity success**. Allowed final decision: `R2_SCREEN_ADJUDICATED_NO_GO_FOR_PHYSICAL_COUNTERPARTS` while `physical_source_identification_complete=false` and `R3_go=false`.

If 0 sources satisfy independent original physical identity gates, **do not** perform R3 periodograms or make new variability claims; instead a methodologically valid R2 negative/ambiguous feasibility report can be used later in R6, or reopen R2 only when genuinely new independent evidence appears. Original publisher retrieval failure or missing instrument covariance is a documented blocker, not a fabricated result.

No raw Gaia, ZTF, PS1 source tables, original CCD FITS pixels, private/unpublished ALMA/TFM data or ZTF source fluxes are committed in this phase. Use publicly traceable derived-only no-raw evidence; keep astronomical claims conservative.
