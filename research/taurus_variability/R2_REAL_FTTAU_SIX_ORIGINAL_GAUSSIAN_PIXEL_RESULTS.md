# Taurus R2 — six authentic original ZTF FT Tau science+mask pixel Gaussian residual audit

**12 November 2026. Genuine original data, prospectively fixed source positions, no source re-selection or astrophysical discovery.**

[Precommitted pixel-analysis protocol](R2_FTTAU_SIX_EPOCH_INDEPENDENT_GAUSSIAN_PIXELS_PREREGISTRATION.md) · [Original-data workflow 43279744985](https://github.com/ismaelberja/stellarforge/actions/runs/43279744985) · [Genuine derived-only archive artifact](https://github.com/ismaelberja/stellarforge/actions/runs/43279744985/artifacts/13970994224) · [Permanent source evidence ledger](../../reports/taurus_variability_r2/FTTAU_SIX_ORIGINAL_ZTF_INDEPENDENT_GAUSSIAN_PIXELS_NO_RAW.json)

## Question and exact input provenance

Following the successful six-original-image chi-independent control study (PR #46), this experiment **did not** choose new observational dates. It retained precisely the three previously selected same-OID source pairs for **g field 1605, g field 609 and r field 609**; three early sources had passed the original native PSF quality screens, and three late-night sources had **failed solely because original native chi was below the prospectively frozen 0.5 cutoff**.

In this increment, the original full native `psfcat.fits` source catalogue was fetched again for all six frames and matched its earlier original full-file SHA-256, and the corresponding **six original 60 arcsec ZTF science FITS cutouts plus six exact same-exposure masks** were independently acquired. The three previous late original science and mask SHA-256 values also matched PR #45 exactly. Gaia DR3 original five-parameter FT Tau astrometry was fetched by exact source ID, with the existing approximate geocentric propagation. No source or image was replaced when any subsequent pixel fit had difficulty.

## Pre-frozen independent analytic pixel method

At epoch-propagated Gaia, run the prior hardened original ZTF WCS+mask validation, then use only unmasked original science pixels within a **4.5 pixel radius core** and a **9–15 pixel annulus** for the fixed sky-median and 1.4826 MAD sky-noise proxy. Fit a **positive-amplitude circular analytic Gaussian** with centroid constrained to ±2 pixels and sigma in [0.6,4.5] pixel, using bounded robust least-squares (max 300 evaluations). The result is an *independently coded simple image pixel-profile residual*, not ZTF's native spatially varying PSF, not the catalogue chi, and not an external instrument/WCS/PSF-noise calibration. Raw source pixels, original catalogues, FITS data, photometry and per-exposure source IDs were kept transient and not committed.

## Genuine six-frame original science/mask results

| Fixed filter/field, epoch | Original native PSF chi | Science & mask core | Gaussian numeric fit | Core RMS residual / annulus MAD noise proxy | Analytic Gaussian FWHM proxy |
| --- | ---: | --- | --- | ---: | ---: |
| g/1605 · early MJD 58362.516713 | 0.804 (native PASS) | Good, 0 core bad/saturated | **Numeric fit** | 13.77661 | 2.43475 arcsec |
| g/1605 · late MJD 60233.393611 | **0.456 (native FAIL)** | Good, 0 core bad/saturated | **Numeric fit** | 16.42642 | 2.12753 arcsec |
| g/609 · early MJD 58330.489120 | 0.552 (native PASS) | Good, 0 core bad/saturated | **Numeric fit** | 8.57701 | 2.24884 arcsec |
| g/609 · late MJD 60948.441412 | **0.424 (native FAIL)** | Good, 0 core bad/saturated | **Optimizer failed** | Not estimated | Not estimated |
| r/609 · early MJD 58321.487465 | 1.438 (native PASS) | Good, 0 core bad/saturated | **Numeric fit** | 18.95466 | 2.56295 arcsec |
| r/609 · late MJD 60935.414502 | **0.383 (native FAIL)** | Good, 0 core bad/saturated | **Optimizer failed** | Not estimated | Not estimated |

**Observed authentic data:** 6/6 original PSFcat SHA verified; **6/6** exact dated original science+mask FITS pairs accessed, celestial-WCS aligned with **zero** disqualifying source-core mask pixels, zero saturated core pixels and no nonfinite core science pixel; all six source annuli were free of BAD_MASK_BITS. Exactly **4/6** independently coded bounded Gaussian optimizations produced numeric fits and **2/6** did **not** converge to a valid solution under the predeclared procedure. Two failures are explicitly **unresolved analytic-model results**, not missing sources and not evidence of a new companion.

Only the g/1605 early and late epochs both produced numeric Gaussian results; their **descriptive late/early core RMS-over-sky-noise ratio is 1.19234**. Do not interpret this as a stellar magnitude change, source flux variability, a statistical significance test or original ZTF native chi. For the g/609 and r/609 source pairs no two-epoch Gaussian residual ratio is reported because their late fit is unresolved. All four finite residual RMS/sky-MAD ratios are **well above 1**, including three sources that passed the native PSF chi screen. This highlights the limitations of a simple circular Gaussian and a sky-MAD-only noise proxy for these real science images, rather than validating or disproving the native ZTF PSF's reported uncertainty model.

## Scientific verdict: instrumental pilot completed; independent PSF validation NOT achieved

This study is a **valid provenance-locked software/observational diagnostic with an honest partial numerical result**, but it does **not** independently establish source-level PSF/WCS covariance or provide the basis for changing the pre-frozen original PSF chi gate. A simple Gaussian is not the ZTF instrument's spatial PSF and different dated images have different atmospheric seeing and sky conditions. Two low-chi frames cannot be compared at all under the pre-specified fit; future methods must be **separately preregistered**, not tuned to force these to pass after observing the outcomes.

The original PR #44/#45 5/8 provisional native source quality passes, 3/8 failures and only 1/4 quality-passing two-night source pairs are **unchanged**. **Zero independently verified physical Gaia–ZTF FT Tau identifications, zero merged OID light curves, zero confirmed new astrophysical variables/companions or proper motions.** R2 scientific source association remains **OPEN**, R3 astrophysical inference **blocked**.

## Reproduction and next independent validation

[Actual original-data run](https://github.com/ismaelberja/stellarforge/actions/runs/43279744985) · [Derived-only original artifact 13970994224](https://github.com/ismaelberja/stellarforge/actions/runs/43279744985/artifacts/13970994224). Archive ZIP SHA-256 **136dde77990e5472f5dfcd21a1f8f5cd78d8810ee07e8b89420a22fd291d42d9**; derived original JSON SHA-256 **b7b80bf4cd48f0a30c260f4cd1f87af3353232f0e70487c2ede95292254496e9**; original Gaia source response SHA-256 **399b5498d8d8a8a646073dfc029895ed64902940896d1789c63833a18074b642**. The permanent [six original images' original hashes and bounded diagnostics](../../reports/taurus_variability_r2/FTTAU_SIX_ORIGINAL_ZTF_INDEPENDENT_GAUSSIAN_PIXELS_NO_RAW.json) have been retained without original pixels or source rows.

**Proposed separately preregistered next step:** instrument-aware PSF residual modelling or authenticated reference-star / external high-resolution association checks, including a rigorous, independent understanding of source-specific noise and WCS errors; keep original source rejection gates unchanged.
