# StellarForge v1.10 — Real held-out Gaia-reference offset evidence

**Date:** 6 November 2026. **Actual derived observations:** original [v1.8 ZTF/Gaia image-analysis run](https://github.com/ismaelberja/stellarforge/actions/runs/42077605987); offline holdout reanalysis in [v1.10 GitHub Actions](https://github.com/ismaelberja/stellarforge/actions/runs/42214593233).

**Scientific interpretation: these are sample-internal nominal centroid-offset disagreements, NOT independently calibrated instrument WCS errors, physical source motions, confirmed Gaia–ZTF identities or astronomical discoveries.**

## Original real-image provenance

Four ZTF science exposures from one g-band ZTF OID around each target (FT Tau and CIDA 11), with 16 original candidate reference cutout requests and **13 Gaussian centroid model fits**. The original v1.8 aggregate JSON SHA-256 is `fb7d5c315cbef56b2551e73920c67920827d91160b4c0bd35f3fd77113166beb`. A loss-reduced derived measurement ledger is kept at [data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json](../../data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json), so this reanalysis is reproducible even after the short-lived original workflow artifact expires. It has no raw Gaia TAP CSV, raw ZTF photometry or FITS image pixels.

The v1.10 run passed **468 automated tests** and reanalyzed the real archived derived offsets without new network calls.

## Leave-one-reference-out results

Each candidate reference has an original 2D Gaussian profile centroid deviation from the nominal Gaia position propagated with **linear proper motion only** and the uncalibrated ZTF FITS header WCS. The leave-one-out (LOO) statistic compares one withheld reference residual vector with the median of the remaining reference vectors in the *same science exposure*. A set of three references has just two stars left to train each fold.

Two branches are evaluated: **inclusive** keeps reference models flagged `PSF_PROXY_REVIEW_REQUIRED` (subject to fit-bounds/shape checks); **strict** excludes those flagged models and large residual proxies, so that the result cannot be made falsely robust by poor-fitting profiles.

| Target | MJD | Inclusive fitted references | Strict fitted references | Inclusive LOO RMS (arcsec) | Strict LOO RMS (arcsec) | Strict target residual eligible |
|---|---:|---:|---:|---:|---:|---|
| FT Tau | 58388.389016 | 1 | 1 | insufficient | insufficient | No |
| FT Tau | 58491.184780 | 3 | 3 | 0.075782 | 0.075782 | No: target Gaussian fit itself flagged for review |
| CIDA 11 | 58475.113750 | 4 | 4 | 0.093046 | 0.093046 | Provisional diagnostic only |
| CIDA 11 | 58849.135984 | 5 | **2** | 0.051244 | **insufficient** | No: target and three reference fits flagged for review |

**Interpretation:** although the original v1.8 inclusive medians had at least three reference models in three of four exposures, **only two exposures** retain at least three reference fits after stricter profile-quality filtering. A nominal LOO RMS as small as 0.051 arcsec on CIDA 11's later exposure **cannot** be promoted to a robust instrument error because its strict reference sample has only two accepted models.

The first CIDA 11 science exposure (MJD 58475.113750) permits a **provisional target-minus-strict-reference median offset** of +0.06332 arcsec east and −0.060045 arcsec north, radial magnitude **0.087263 arcsec**, but that is **not** source motion, a Gaia–ZTF crossmatch, nor a validated astrometric residual uncertainty. The original target Gaia DR3 RUWE ≈8.57 is a major warning that the single-star model itself may be unreliable.

## What the numbers do NOT establish

- The LOO residual is **internal disagreement among selected candidate reference stars**. Shared WCS/PSF distortion, catalogue selection, imperfect model centroids or Gaia astrometric systematics can bias all the references together.
- The LOO RMS is **not** a statistical 1σ bound, uncertainty of a fitted target center, instrument error floor, source-association probability or calibrated confidence interval. Three or four references are too few for a stable spatially varying field WCS solution.
- The v1.8 reference candidates are not independently confirmed to be single, isolated ZTF stars; a good Gaia RUWE and a Gaussian image-fit centroid cannot prove absence of blending.
- v1.9 modeled **the two targets'** annual parallax and full five-parameter formal Gaia covariance. The historical v1.8 *reference star image positions* were based on linear Gaia proper-motion only, so these old derived reference offsets have **not** been retroactively parallax/covariance corrected.
- Telescope-specific observatory location, aberration, chromatic refraction, instrumental PSF, saturation, detector masks, full WCS distortion solution, all six ZTF object/passband groups, absolute timing and physical source identity remain open scientific gates.

## Reproducibility

Offline, using only the small versioned derived evidence file:

```bash
python -m pip install -e '.[test,analysis,images]'
python -m pytest -q
python scripts/run_v110_reference_holdout.py \
  --input data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json \
  --output reports/generated/v1.10_reference_holdout
```

All 468 automated tests passed in the [observational reanalysis workflow](https://github.com/ismaelberja/stellarforge/actions/runs/42214593233). The workflow uploads aggregate-only JSON/Markdown for transparent inspection, never original Gaia/ZTF FITS images or photometry.

**Next methodological gate:** obtain enough independently verified single-star image controls to estimate image-specific PSF/WCS residuals and uncertainties, apply full Gaia parallax/covariance to those *same reference stars* at the actual exposure epochs, verify FITS timing and compare independent field-star residuals. Do not claim physical variability until source identities and observational error models are validated.

**Independent calibrated ZTF WCS solutions: 0. Authenticated stellar empirical PSFs: 0. Confirmed physical Gaia–ZTF associations: 0. New astrophysical companions/events: 0.**
