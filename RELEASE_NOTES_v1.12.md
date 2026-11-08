# StellarForge v1.12 — Real ZTF FITS remeasurement and centroid-model sensitivity

**8 November 2026 — research-software engineering milestone.**

## What improved

The analysis returned to **the original dated ZTF `sciimg.fits` images**, using the original 2,212-row official IRSA acquisition only after SHA-256/manifest verification. A bounded pilot remeasured four target images and sixteen Gaia-reference candidate cutouts from the **same dated science FITS products**, after applying each candidate's Gaia DR3 five-parameter formal covariance and epoch-dependent annual geometric parallax.

The new approach compares **two distinct centroid estimators on the same original pixels**: the previous elliptical Gaussian plus background plane and a new sigma-clipped planar-background, positive-flux aperture centroid with morphology and noise checks. It explicitly records FITS time metadata, incomplete masks/saturation metadata and fitted-profile failures. **These are not independent observations or authenticated empirical PSF calibrations.**

## Actual observed results

The [real GitHub Actions ZTF image run](https://github.com/ismaelberja/stellarforge/actions/runs/42459615687) made **20 bounded FITS image requests**: nine HTTP 503 access failures, two incomplete local SNR/profile screens and **nine images** processed by both centroid models (three target, six Gaia reference images). Six reference models passed provisional internal agreement. Across the nine complete images, **median absolute Gaussian/aperture centroid separation was 0.116948″** — a model-sensitivity diagnostic, not an instrument astrometric uncertainty.

In one CIDA 11 exposure (MJD 58475.113750), **three** reference candidates met the dual-model check; their internal held-out disagreement was **0.072594″ using Gaussian centroids** and **0.118163″ using aperture centroids**. Other exposure groups had insufficient vetted models or archive failures. **506 automated tests passed.**

Detailed observations: [real v1.12 report](reports/real_fits_v1.12/REAL_TWO_CENTROID_MODEL_QA.md); method: [image and WCS caveats](docs/PHASE112_PIXEL_CENTROID_AND_WCS_LIMITS.md).

## What this does not show

Neither estimator independently verifies a physical Gaia–ZTF match, a clean single star, a calibrated PSF or absolute WCS precision. The reported source-position differences must not be treated as physical motions. The public archival imaging includes separately documented [ZTF `mskimg.fits` detector masks and official PSF products](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html), but v1.12 does **not** use them yet. In particular, bad pixels, saturation, unknown detector masks, variable seeing, sky-nebulosity and high Gaia RUWE for CIDA 11 remain important scientific limitations. These data do not confirm binary companions or physical variability.

## Next defensible priority

Retrieve official same-exposure bitmasks and instrument PSF products under bounded access, validate authentic isolated reference-star morphology, and establish a spatially resolved multi-star WCS/PSF error model with genuinely held-out independent references before assigning astronomical detection probabilities or incidence rates. Never silently publish raw third-party ZTF photometry or FITS pixels in Git.
