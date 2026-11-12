# Taurus R2 — authentic six original ZTF spatial DAOPhot PSF source-pixel holdout results

**Original-data execution 12 November 2026.** First instrument-aware spatial PSF audit after PR #47's over-simplified independent circular Gaussian gave only 4/6 numeric fits. This increment has **6/6 original native DAOPhot spatial PSF models, 6/6 field-center PSF stamps and 6/6 genuine original science+mask+PSFcat exposures**, verified against original file checksums. The results are native instrument screening, **not** independent astrophysical source authentication.

[Preregistration, committed before original PSF-model data access](R2_FTTAU_SIX_ORIGINAL_NATIVE_SPATIAL_PSF_PREREGISTRATION.md) · [Successful genuine ZTF live workflow](https://github.com/ismaelberja/stellarforge/actions/runs/43310945601) · [Original derived-only data artifact](https://github.com/ismaelberja/stellarforge/actions/runs/43310945601/artifacts/13986790868) · [Permanent no-raw provenance and results ledger](../../reports/taurus_variability_r2/FTTAU_SIX_ORIGINAL_NATIVE_SPATIAL_DAOPHOT_PSF_NO_RAW.json)

## Fixed design and actual original data

These are **exactly** the six previously fixed source dates from three g/r FT Tau ZTF ObjectIDs (g1605/g609/r609, each earliest/last eligible independent night selected before any image inspection in PR #44). Each old full native `psfcat.fits` SHA-256, original 60-arcsec science cutout SHA, mask cutout SHA, MJD, `filefracday`, original PSFcat nearest-source chi and SNR was rechecked byte-for-byte against the permanent PR #47 source evidence; original Gaia DR3 exact FT Tau ID **149623711269425408** was also re-fetched and matched its original source response SHA.

New original instrument products were fetched from official IRSA for all six dates: the source-CCD-dependent spatial `sciimgdao.psf` lookup table and the **field-center-only** native `sciimgdaopsfcent.fits` stamp. The existing parser reconstructed each native spatial model and compared it with the **same-reduction** field-center reference PSF. **6/6** models matched the original center PSF under the existing engineering thresholds, with cosine similarity 1.000000 and normalized L1 differences about 0.00029–0.00058. This demonstrates internal reconstruction consistency between two original pipeline products, **not** independent calibration against physical stars.

For each image we selected only the source **nearest** to Gaia-propagated coordinates in the exact original PSFcat, preserving the frozen original source chi criterion. Evaluated the actual native spatial DAOPhot model at that source's **original full-quadrant detector x/y**, not a cutout-local substitute. Applied existing `v116_masked_original_psf_residuals._masked_fit`: stringent source/catalogue WCS subpixel phase, detector masks, 9-pixel source fit, sky-annulus MAD, linear PSF amplitude/sky gradient fit on checkerboard training pixels and normalized held-out residuals on **other pixels of the same star image**. No controls against genuinely independent reference stars or external WCS covariance were performed in this step.

## Six authentic results

| Fixed original source observation | Original native chi and source-quality | New spatial model numeric fit | Same-source held-out RMS / sky-MAD noise | Pre-existing same-source residual screen |
| --- | --- | --- | ---: | --- |
| g field1605 · early MJD 58362.516713 | 0.804, native PASS | Completed | **2.365183** | Provisional pass |
| g field1605 · late MJD 60233.393611 | **0.456, native FAIL** | Completed | **2.103996** | Provisional pass; native FAIL unchanged |
| g field609 · early MJD 58330.489120 | 0.552, native PASS | Completed | **1.680895** | Provisional pass |
| g field609 · late MJD 60948.441412 | **0.424, native FAIL** | Completed | **1.644827** | Provisional pass; native FAIL unchanged |
| r field609 · early MJD 58321.487465 | 1.438, native PASS | Completed | **4.485939** | Review required |
| r field609 · late MJD 60935.414502 | **0.383, native FAIL** | Completed | **9.420394** | Review required |

### Engineering acceptance and scientific caveat

All **6/6** original source-specific spatial-model numeric pixel fits completed, vs **4/6** finite fits from the preceding independently coded *circular Gaussian*. Of these six actual same-image residual checks, **4/6** satisfied the pre-existing engineering screen (held-out RMS<=3, max positive residual<=7, amplitude/noise>=10); **2/6 r609 frames** require further review for large residuals. This is a useful observation that the previously unable-to-fit g609 and r609 late images can be numerically fitted with the instrument's original spatially varying PSF, but **does not justify claiming scientific source-quality recovery for either**.

The real 6/6 native model-vs-field-center matches are an **internal reproduction** of the same archived reduction; even a provisional held-out-pixel pass is only a *same-image* diagnostic. Earlier analytic Gaussian residual/noise values and these native spatial PSF values have different support regions, sky/background estimation and optimization objectives: **do not compute performance ratios across the two methods** or claim independent model superiority. The r609 high native PSF residuals must remain reported even though the old early r609 native source passed chi. ZTF documents spatially varying PSF estimates in the original DAOPhot product (see [IRSA original file types](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html) and [original pipeline source model](https://irsa.ipac.caltech.edu/data/ZTF/docs/ztf_pipelines_deliverables.pdf)).

## Research status: native PSF feasibility improved; physical source question OPEN

Exactly **zero** of the three previously rejected late original source candidates have been promoted to an accepted source under the old native chi lower-bound 0.5: 5/8 original source candidates PASS, 3/8 FAIL, and only 1/4 original independent-night candidate pairs pass both frames. **No physical Gaia–ZTF FT Tau source association, independent per-source WCS/PSF noise covariance, cross-instrument deblending, astrophysical proper motion, true variability or companion has been demonstrated**, and no original ZTF ObjectID light curves were merged. R2 science **OPEN**, R3 time-domain astrophysics **BLOCKED**.

## Byte-level original provenance

[Actual original-data Actions run](https://github.com/ismaelberja/stellarforge/actions/runs/43310945601) · [original derived-only artifact 13986790868](https://github.com/ismaelberja/stellarforge/actions/runs/43310945601/artifacts/13986790868), archive ZIP SHA-256 `4ab7e8deaea63156b964c79382b7adfe1775cf0dac66b933dfc22553214c3364`, source derived JSON SHA-256 `6b91c969613f88b59303ecdeaace5e61096cab4a5b90b8d4dffecfec180c80d2`. Gaia exact source response SHA `399b5498d8d8a8a646073dfc029895ed64902940896d1789c63833a18074b642`. Permanent per-date original **four-product hashes**, derived residuals and strict retained no-source-identity claims: [evidence ledger](../../reports/taurus_variability_r2/FTTAU_SIX_ORIGINAL_NATIVE_SPATIAL_DAOPHOT_PSF_NO_RAW.json). Original catalogue rows, fluxes, source IDs, PSF tables/coefficients and raw FITS image pixels were not committed.

**Next independent science action:** external authenticated FT Tau stellar identification or truly independent reference-star/instrumental covariance calibration. Without external validation, this successful same-pipeline modelling does not turn the manuscript into a verified discovery. A separate **software engineering v2.1 portfolio freeze/review** can proceed independently of this open astrophysics question.
