# R2 — First real Gaia DR3 exact-ID screen for 24 Taurus technical candidates

**11 November 2026 · Original official catalogue query, but NOT source matching with ZTF.**

[Live successful GitHub Actions Gaia query run](https://github.com/ismaelberja/stellarforge/actions/runs/43029175432) ·
[original derived-only audit artifact](https://github.com/ismaelberja/stellarforge/actions/runs/43029175432/artifacts/13858887859) (short-lived; 7-day retention) ·
[JSON aggregate no-raw research receipt](../../reports/taurus_variability_r2/GAIA_24_EXACT_ID_RESULTS_NO_RAW.json)

## Results from genuine original Gaia DR3 records

The previously frozen, **nonrepresentative 24-source** Taurus
technical cohort was queried as **two batches of 12 exact Gaia DR3
source IDs** using `gaiadr3.gaia_source` through Gaia@ARI TAP.
No search position was added and no Gaia IDs were selected after
examining observational variability.

| Tested step | Actual result |
| --- | ---: |
| Frozen Gaia candidate IDs | **24** |
| Exact source IDs found in original Gaia DR3 | **24/24** |
| No Gaia record for supplied source ID | **0** |
| Passed a preliminary **Gaia-only** astrometric QA screen | **17** |
| Gaia RUWE ≥ 1.4, therefore deserves review | **7** |
| Physical Gaia-to-ZTF identity established | **0** |
| Individually verified literature Taurus memberships | **0** |
| Original ZTF science-image crowding reviews in **this** R2 job | **0** |
| New astronomically confirmed variables or companions | **0** |

The 17 preliminary flags require: valid Gaia 5-/6-parameter
astrometry, both proper motion coordinates, RUWE below 1.4,
`duplicated_source=false`, and a J2016 catalogue position less
than one arcsecond from the original pre-existing **secondary-mirror
technical seed coordinate**. This is NOT a physical counterpart
identification or ZTF WCS/PSF calibration. The 7 with high RUWE
should be reviewed, **not automatically excluded as nonmembers**.
High RUWE is common in problematic astrometric solutions and can
have several astrophysical/instrumental causes.

**Important historical context:** previously verified individual
Gaia DR3 results (separate run) already flagged CIDA 11 with
RUWE **8.56752**, while FT Tau had RUWE **1.32659**.
These do not establish the two historical ZTF positional light curves
as physically belonging to those stars; see
[v1.9 prior real Gaia covariance report](../../reports/gaia_formal_v1.9/GAIA_COVARIANCE_AND_ANNUAL_PARALLAX.md).

## Scientific interpretation

- An exact `source_id` in Gaia is a **catalogue source record**,
  not an association with a ZTF `oid`.
- This R2 run made **no** queries to original IRSA ZTF lightcurve,
  detector PSFcat, science FITS or mask images. Those are needed for
  per-source **independent identity/crowding** assessment.
- The catalogue copy serving as the original 24-object technical
  seed remains a secondary Luhman (2023) mirror; its publisher
  source-byte and individual membership interpretations are pending.
- R1 cohort is deliberately magnitude/group preselected and
  nonrepresentative: these 24 cannot yield a regional Taurus
  variability incidence fraction.
- No raw Gaia TAP CSV or original pixel files were committed.
  Only derived counts/source QA were uploaded to short-lived
  GitHub Actions artifacts.

## Next mandatory R2 source-identification work

1. Independently check **all 24** literature memberships and
   Gaia neighbours in a consistent astrometric epoch.
2. Retrieve corresponding IRSA ZTF **OID and band source positions**,
   at matching observation dates; check for multiple/conflicting
   ZTF OIDs near each Gaia source and obvious blends.
3. Inspect original ZTF science FITS/PSFcat/bitmasks and compare
   predicted Gaia positions with **independent** reference-star
   coordinates or quality assessments. Do not infer physical identity
   from nearest-position matches or same-pipeline WCS alone.
4. Write a 24-row ledger with statuses:
   `PHYSICAL_SOURCE_IDENTITY_PENDING`,
   `AMBIGUOUS_ZTF_OID`,
   `INSUFFICIENT_ZTF_IMAGE_EVIDENCE`,
   `PHYSICAL_SOURCE_IDENTITY_REVIEWED_WITH_LIMITS`.
   A status is justified only by original evidence and independent
   scientific review, not by having passed the Gaia-only QA screen.

**R2 science status: PARTIAL.** Exact Gaia DR3 source retrieval
successfully completed for all 24, but no star yet passes all
independent Gaia–ZTF physical association gates. This does not
block the already completed v2.0 software portfolio.
