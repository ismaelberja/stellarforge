# StellarForge v1.19 — Empirical PSF source-disjoint validation pilot status (NO RAW)

**9 November 2026 · Explicitly data-limited engineering release.**

## Verified software implementation

The v1.19 source code provides an original ZTF **23×23-pixel empirical PSF model reconstructed only from genuine science-image pixels** of previously selected Gaia reference-star candidates, with original detector WCS and bitmask screening, robust local sky subtraction and source-pixel subphase alignment. Crucially, **no ZTF native spatial DAOPhot correction lookup coefficient enters the empirical PSF construction**. A distinct set of *new* Gaia candidate source IDs — not in the original ten-star FT Tau/CIDA 11 target/reference list — are designated as **heldout evaluation sources**, whose pixels never influence their tested PSF shape.

The same heldout star's original source-pixel model amplitude and sky plane are fitted on one checkerboard parity and residuals measured on the other; the operation is repeated for the native original same-date DAOPhot PSF for a *fair within-source engineering comparison*. This is a **model-shape training/test source split in StellarForge**, not proof of independence from the original ZTF PSF-making pipeline, which supplied source positions and may have trained with the same catalogued stars.

An optional FITS-header-gain-based source shot-noise sensitivity exists. **No gain, read noise or correlated detector error is invented**; absent original physically valid metadata, the output remains only a robust sky-annulus MAD noise proxy and no calibrated WCS/PSF error or chi-square probability is asserted.

## Original observed-data diagnostic, first pilot (NOT final design validation)

The [initial live original-source pilot](https://github.com/ismaelberja/stellarforge/actions/runs/42670364122) **passed 683 synthetic/integration/regression tests** before its original-data stage, then retrieved the original per-exposure ZTF native `psfcat.fits` catalogues for all four historical ZTF technical exposures. It screened the original four new v1.17 CIDA 11 Gaia field source IDs for using the same new Gaia candidate group as 3-training/1-heldout empirical PSF source pixels. This failed the **preregistered high-SNR template training criterion ≥10**, giving these actual outcomes:

| Original science field and date | New Gaia-only source IDs preselected | Native ZTF PSFcat eligible | New Gaia original masked PSF shape stamps passing bright-training criterion | New-source-only PSF LOOCV folds |
|---|---:|---:|---:|---:|
| FT Tau MJD58388.389016 | 4 exploratory | 1 | Not requested (insufficient native eligible new sources) | **0** |
| FT Tau MJD58491.184780 | 4 exploratory | 1 | Not requested (insufficient native eligible new sources) | **0** |
| CIDA 11 MJD58475.113750 | 4 strict | 4 | **1**; three had insufficient integrated source SNR proxy | **0** |
| CIDA 11 MJD58849.135984 | 4 strict | 2 | Not requested (insufficient native eligible new sources) | **0** |

**This failure is the scientifically correct result for the original new-Gaia-only high-SNR training design.** It is **not** an astronomical nondetection, evidence that a source is absent, or justification for relaxing the bright-template threshold retrospectively. The original first-pilot aggregate-only JSON/Markdown is preserved in the workflow artifact and supplied separately; original source FITS pixels, Gaia TAP/IRSA raw data and native PSF products remain unpublished.

## Revised source-disjoint design: software tested, live original run not yet verified

The v1.19 revised design prevents training-set leakage by using **two genuinely separate source-ID roles**, fixed before evaluating any original pixel residual in the revised attempt:

- **Bright TRAINING:** historical preregistered Gaia field *reference* candidate IDs from the v1.8 original exposure ledger, excluding each technical target and all new Gaia heldout IDs. Each template-building original source must pass original ZTF native PSF-fit catalogue source quality, sky/WCS, bad-pixel masks and **integrated image aperture SNR/sky-noise proxy ≥10**. **At least three distinct bright training sources** from the same original dated exposure are mandatory.
- **New HELDOUT EVALUATION:** v1.17 Gaia-only new strictly quality-selected CIDA 11 source IDs or separately preregistered exploratory v1.18 FT Tau Gaia source IDs. These IDs cannot overlap any original training reference ID. Because they **never contribute PSF shape pixels**, a source may be fainter (**minimum same-exposure original-image SNR proxy ≥2.5**), but requires a valid original native PSF candidate, original WCS-aligned detector mask and positive source amplitude. The exploratory FT Tau and strict CIDA 11 quality tiers are kept separate.
- At each heldout source, compute the same original-image nuisance fit and withheld-pixel residuals for the new old-reference-trained empirical PSF and the native DAOPhot model. Report their **relative residual RMS ratio** without calling it absolute instrument precision, variability, a companion or formal statistical significance.

The implementation and revised adversarial tests (source-group leakage, faint heldout, high SNR training, WCS phase, masks, 503, header gain, insufficient data) were verified by [GitHub pull request #23 CI, **689 tests passing**](https://github.com/ismaelberja/stellarforge/actions/runs/42673356714).

**The revised real original-data pilot remains NOT EXECUTED/NOT VERIFIED**: subsequent GitHub Actions runs [42673081415](https://github.com/ismaelberja/stellarforge/actions/runs/42673081415) and [42673711595](https://github.com/ismaelberja/stellarforge/actions/runs/42673711595) reached failure status **without any jobs actually being instantiated**, so they contain no observed source images or result artifacts and must not be described as genuine failed astronomical fits or as confirmed successful data analysis. No observed Gaia-heldout residual comparison of the revised empirical model is reported in this release.

**Important distinctions:** The first pilot's missing three bright source-image stamps are *insufficient training quality*, whereas the later runs' lack of jobs is *unexecuted infrastructure*. Neither is astrophysical nondetection. The initial pilot's **683 passing tests** and final PR's **689 passing tests** apply to their respective code versions; the final code's 689 passing tests do not constitute an observed-data result.

## Open science gate

The original ZTF DAOPhot training-source roster is **unknown even after reading eight original source processing logs in v1.18**. No source has been independently authenticated as a physical Gaia–ZTF counterpart or certified as an isolated single star. A PSF created from different source image pixels is independent from the heldout source within *StellarForge's shape training*; it is not wholly independent of upstream ZTF source centroids, survey selection and native instrument calibration.

The remaining observational requirements are: a successful original-data rerun of the revised training/heldout grouping; access to genuinely independent or newly reconstructed native PSF calibration stars; realistic CCD inverse-covariance and source-color/refraction/WCS calibration; and independent matched real observations for the three high-positive-residual v1.16 sources, before any astrophysical claim.

**Scientific confirmations achieved in v1.19: zero new physical Gaia–ZTF source IDs, zero fully calibrated telescope PSFs/WCS errors, zero stellar companions and zero physical variability events.**

[Method and quality-role split](../../docs/PHASE119_SOURCE_DISJOINT_EMPIRICAL_PSF_AND_NOISE.md) · [Empirical source-PSF implementation](../../src/stellarforge/v119_empirical_source_psf.py) · [Real source-data runner](../../scripts/run_v119_real_empirical_source_psf.py) · [Synthetic regressions](../../tests/test_v119_empirical_source_psf.py).
