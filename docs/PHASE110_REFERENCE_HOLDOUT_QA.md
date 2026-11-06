# StellarForge v1.10 — held-out Gaia reference profile consistency

**Purpose:** Evaluate whether the local median offsets used in the v1.8 ZTF/Gaia reference-image pilot are stable when an individual reference is excluded. **This is a quality/sensitivity test, not a calibrated ZTF WCS solution, physical Gaia–ZTF source association or new scientific discovery.**

## Evidence and provenance

- Source: [v1.8 real ZTF image/Gaia reference run](https://github.com/ismaelberja/stellarforge/actions/runs/42077605987), four actual g-band science exposures in FT Tau and CIDA 11 fields, 16 reference cutout requests and **13 fitted reference image models**.
- The original v1.8 aggregate JSON SHA-256: `fb7d5c315cbef56b2551e73920c67920827d91160b4c0bd35f3fd77113166beb`.
- Because short-lived GitHub Actions source artifacts expire, a small **derived, loss-reduced reference-offset evidence ledger** is versioned at [data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json](../data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json). It retains the actual source IDs, science exposure MJDs, nominal east/north offsets and Gaussian model-review flags required for this study, **not original FITS pixel matrices, Gaia TAP CSVs or raw photometric light curves**.
- No new network download or astro-source identifier was invented in this milestone; the code runs entirely offline. The fixed provenance SHA of the original v1.8 artifact must match.

## Method

For each dated ZTF science exposure, compute two independent **selection sensitivity branches** over original Gaia DR3 catalogue-backed reference *candidates*:

1. **Inclusive image-model branch:** retain both `PSF_PROXY_PROVISIONAL_ONLY` and `PSF_PROXY_REVIEW_REQUIRED` measurements, excluding invalid model bounds and pathological axis ratios. This shows the influence of problematic Gaussian models rather than silently suppressing them.
2. **Strict image-model branch:** require `PSF_PROXY_PROVISIONAL_ONLY`, a residual-noise proxy below five, no fit at an optimizer bound and plausible axis ratio. These are engineering gates, **not authentication that a source is an uncontaminated single star**.

Within each branch, require **at least three distinct Gaia reference IDs**. Estimate a median *east/north* translation from all eligible references, then perform **leave-one-reference-out cross-validation**: for each reference, compute a median east/north translation from the *remaining* candidates and compare it with the withheld reference's nominal WCS residual vector. Report the median, maximum and RMS of the held-out 2D difference magnitudes. With three references, each fit fold has only **two training sources**; this can be extremely unstable and **does not constitute an externally calibrated 1σ astrometric error**.

For a provisional **target-minus-reference offset**, require both three or more eligible references in the strict branch and a non-flagged target Gaussian image fit. Otherwise the result remains withheld as not justified by available model quality. Even the retained offset is *not* a physical proper motion, PSF-based companion measurement or Gaia–ZTF source-identity confirmation.

## Important limitation relative to v1.9

v1.9 improved **the two target Gaia DR3 sources'** formal five-parameter covariance propagation and geometric annual parallax. The original Gaia-reference cutouts in v1.8 were still centered on **2D proper-motion-only** positions, so their older measured residuals cannot be retroactively claimed to include full reference-star parallax and covariance. That requires recalculating each reference on original dated images with complete catalogue astrometry and separately calibrated image errors.

## Interpretation and next scientific gates

- A small held-out residual is just **internal agreement among candidate reference measurements**, potentially all biased by the same WCS header, instrumental PSF or unmodeled Gaia/CIDA 11 physics. It does not validate an actual instrument astrometric error budget.
- Gaussian fit residuals may come from seeing-dependent ZTF PSF wings, saturation, nebulosity or unrelated contaminants; a flagged fit alone is not evidence of a binary.
- The v1.8 original pilot sampled **one g-band OID per target and two dated frames**. The full six-OID project and representative time baseline require separate analysis.
- CIDA 11's **RUWE ≈ 8.57** remains a fundamental caution regarding the single-star astrometric solution; Gaia formal uncertainties from v1.9 may substantially underestimate the astrophysical model discrepancy.
- To move beyond provisional measurements, authenticate reference stars with independent source information and detector masks, model a field-dependent empirical PSF, recalculate Gaia reference positions including parallax and covariance, and estimate independently validated per-exposure WCS residuals across a genuinely representative field.

## Reproduce offline

```bash
python -m pip install -e '.[test,analysis,images]'
python -m pytest -q
python scripts/run_v110_reference_holdout.py \
  --input data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json \
  --output reports/generated/v1.10_reference_holdout
```

**No independent astronomical Gaia–ZTF identities, empirical ZTF PSF calibrations, independently validated WCS uncertainties, new physical companions or variability events are claimed.**
