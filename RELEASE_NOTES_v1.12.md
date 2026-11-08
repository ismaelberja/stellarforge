# StellarForge v1.12 — Real ZTF FITS remeasurement and centroid-model sensitivity

**8 November 2026 — research-software engineering milestone.**

## What improved

The analysis returned to **the original dated ZTF `sciimg.fits` images**, using the original 2,212-row official IRSA acquisition only after SHA-256/manifest verification. A bounded pilot remeasured four target images and sixteen Gaia-reference candidate cutouts from the **same dated science FITS products**, after applying each candidate's Gaia DR3 five-parameter formal covariance and epoch-dependent annual geometric parallax.

The new approach compares **two distinct centroid estimators on the same original pixels**: the previous elliptical Gaussian plus background plane and a new sigma-clipped planar-background, positive-flux aperture centroid with morphology and noise checks. It explicitly records FITS time metadata, incomplete masks/saturation metadata and fitted-profile failures. **These are not independent observations or authenticated empirical PSF calibrations.**

## Actual observed results

Two real observed-data workflows — [initial run A](https://github.com/ismaelberja/stellarforge/actions/runs/42459615687) and [final-code run B](https://github.com/ismaelberja/stellarforge/actions/runs/42460247095) — each made **20 bounded FITS image requests on the exact same original science dates**; they are not 40 independent observations. Run A: 9 HTTP 503, 2 inconclusive profile screens, **9 complete image fits** and 6 provisionally consistent reference models. **Final run B:** 8 HTTP 503, **12 complete dual-estimator image fits** (1 target, 11 references), **9 provisionally consistent reference models** and median absolute Gaussian/aperture centroid difference **0.104720″**. Four image cutouts available in both runs had identical FITS SHA-256 hashes.

For CIDA 11 MJD 58475.113750, run B had **four** provisional candidate reference images and internal LOO disagreement **0.064675″ with Gaussian centroids** vs **0.155762″ with aperture centroids**. Its target cutout returned HTTP 503, so no new target position is claimed. Across all four historical exposure groups only one had >=3 consistent references in either run. **506 automated tests passed in both workflows.**

Detailed observations: [real v1.12 report](reports/real_fits_v1.12/REAL_TWO_CENTROID_MODEL_QA.md); method: [image and WCS caveats](docs/PHASE112_PIXEL_CENTROID_AND_WCS_LIMITS.md).

## What this does not show

Neither estimator independently verifies a physical Gaia–ZTF match, a clean single star, a calibrated PSF or absolute WCS precision. The reported source-position differences must not be treated as physical motions. The public archival imaging includes separately documented [ZTF `mskimg.fits` detector masks and official PSF products](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html), but v1.12 does **not** use them yet. In particular, bad pixels, saturation, unknown detector masks, variable seeing, sky-nebulosity and high Gaia RUWE for CIDA 11 remain important scientific limitations. These data do not confirm binary companions or physical variability.

## Next defensible priority

Retrieve official same-exposure bitmasks and instrument PSF products under bounded access, validate authentic isolated reference-star morphology, and establish a spatially resolved multi-star WCS/PSF error model with genuinely held-out independent references before assigning astronomical detection probabilities or incidence rates. Never silently publish raw third-party ZTF photometry or FITS pixels in Git.
