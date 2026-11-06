# Phase 1.11 — Full Gaia reference-star formal covariance and annual-parallax sensitivity

**6 November 2026** · Methodological gate for a scientific Python portfolio. This phase makes **no independent WCS calibration, empirical PSF purification, or physical source-identification claims**.

## Why this matters

v1.8 measured Gaia candidate reference offsets from real ZTF science FITS images with only a 2D Gaia proper-motion reference position. v1.10 showed that these images' candidate reference centroids disagree at roughly **75–93 mas RMS**, and that only **two of four dated science exposures** have at least three Gaussian model fits passing the stricter quality criteria.

v1.9 introduced Gaia's **full formal five-parameter correlation matrix** and Earth-geocentric geometric annual parallax for the **two target Gaia DR3 IDs only**. v1.11 now applies the same calculation to **all eight candidate reference IDs and both targets**, enabling a controlled side-by-side comparison without changing the original image-model quality gates.

## Method

1. Load and validate the small **derived, no-raw-data v1.8 reference offset ledger** with its original aggregate SHA-256 and run ID. Reject duplicate source IDs, invalid dates, malformed measurements and forged source manifests.
2. Determine the set of **ten exact Gaia DR3 source IDs** (eight catalogue-backed candidate reference sources plus the FT Tau and CIDA 11 targets). Submit a bounded, read-only official Gaia DR3 TAP query for their five astrometric parameters, their five formal uncertainties, and all ten pairwise correlations. Incomplete catalogue records or malformed covariance **fail closed** rather than becoming zero-uncertainty measurements.
3. Using Astropy's built-in offline Earth barycentric ephemeris, calculate an **epoch-specific geometric geocentric annual parallax displacement** and a 2D **formal Gaia-only propagated covariance** for each star at its own ZTF science MJD, interpreted as UTC provisionally. These predicted coordinates exclude Palomar topocentric parallax, aberration, RV/perspective effects, chromatic refraction and instrument image/WCS/PSF errors.
4. For each historical Gaussian image-fit offset, apply the sign-safe subtraction: **new offset = original image centroid relative to linear Gaia PM − reference star's annual parallax shift**. Do not refit image pixels or claim an independently recalibrated image astrometric solution.
5. Repeat **strict and inclusive reference quality screens** and leave-one-reference-out internal median-shift disagreement in the *same set* of real v1.8 model measurements. Keep references flagged `PSF_PROXY_REVIEW_REQUIRED` excluded from the strict branch.
6. Treat formal Gaia positional covariances as **separate source-catalogue uncertainties**, not estimated ZTF centroid errors. They are not automatically added to instrumental noise or used as inverse-variance weights; the full instrument error model is not yet available.
7. Require a good target image-fit status plus at least three strictly screened reference models before displaying a provisional target-minus-reference residual. Even then it is explicitly **not source identity, motion, WCS accuracy or a verified event**.

## What was validated

The bounded [observational verification run](https://github.com/ismaelberja/stellarforge/actions/runs/42254052752) returned all ten official Gaia DR3 source solutions and re-evaluated the 13 real fitted candidate reference models in four original dated ZTF images; **484 regression tests passed**. Original v1.10 strict holdout RMS values of **0.075782″ (FT Tau)** and **0.093046″ (CIDA 11)** change to **0.075770″** and **0.092971″** after individual Gaia reference-star geometric annual parallax corrections: changes of **−0.012 and −0.075 mas**. The maximum reference-star annual geometric displacement in the set is **0.60918 mas**. Other exposures remain insufficient for strict LOO validation.

The detailed result and archived query/response hashes appear in [the v1.11 real-data evidence report](../reports/reference_parallax_v1.11/REAL_GAIA_REFERENCE_PARALLAX_LOO.md).

## Important interpretation

- A small change in an *internal reference holdout error* does not calibrate or improve a telescope WCS; it only indicates this particular correction has a small effect on these **selected** reference-model discrepancies.
- High Gaia RUWE for CIDA 11 (~8.57) remains problematic. The formal five-parameter covariance may significantly underestimate real non-single-star astrometric-model errors.
- Gaia catalogue-backed candidate references may themselves be unresolved binaries or blended/extended sources, and their original ZTF Gaussian models may have instrumental PSF wings or poor local backgrounds.
- Only one g-band ZTF object identifier per target is represented in these historical images, not the whole Taurus membership catalogue or even all six original ZTF OID/band groups.
- Precision of numerical formatting is not absolute astrometric accuracy; a low held-out RMS is not an independently validated observational error floor.

## Repeat

```bash
python -m pip install -e '.[test,analysis,images]'
python -m pytest -q
python scripts/run_v111_reference_parallax.py \
  --ledger data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json \
  --output reports/generated/v1.11_reference_parallax
```

The Gaia query is public and limited to ten exact IDs. Raw Gaia TAP responses, ZTF light-curve tables and FITS pixel matrices are **not** written to public Git or uploaded in CI artifacts.

## Next scientifically justified step

Return to genuine original FITS images only when enough well-characterized control stars, precise timing and masks are available to fit an **empirical, field-dependent PSF and independent multi-star distortion/WCS model**, with held-out field-star validation and a realistic systematic error budget. This can then be compared to the per-source Gaia formal covariance modeled here. Until an independent source association succeeds, no physical variability, companions or event incidences should be reported as discoveries.
