# StellarForge v1.7 — Two real ZTF science epochs per OID and image-field controls

**Date:** 5 November 2026. **Type:** tested scientific-software engineering milestone; no new astrophysical discoveries.

## What changed
- Added independently selected ZTF science-image exposures per OID/filter (up to six original dates, 90-arcsec cutout) and a coadd fallback that does not enter science repeatability.
- Added normalized local radial-profile comparison against isolated **unclassified intensity maxima** in each actual image, while enforcing at least two valid control candidates for a shape comparison.
- Added strict bounded archive requests, optical WCS/sky-image validation, prior photometric SHA-256 provenance, fit/transport error ledgers and duplicate-image detection.
- Added synthetic image-field and observation-selection tests; **400 automated tests passed**.
- Limited uploaded outputs to small aggregate JSON/Markdown reports, not raw FITS or ZTF photometric CSV.

## Real data
The [v1.7 live observational run](https://github.com/ismaelberja/stellarforge/actions/runs/42058770141) processed **12 independent science FITS images across all six ZTF OID-band groups** (two per group, including four CIDA 11 images). Only **14 image requests** were needed; two resulted in URLError. Nominal differences between the two WCS-referenced Gaussian proxy centroid residuals were **0.024–0.097 arcsec**, **not calibrated astrometric errors or independent Gaia-ZTF source associations**.

The 90-arcsec images had **no frame with at least two usable unclassified comparison brightness peaks**, so true empirical PSF calibration remains unavailable. Zero verified stars deblended, zero confirmed companions, zero confirmed physical variability events.

## Next scientific validation
Identify genuine same-field reference stars in a broader or catalog-authenticated image, independently calibrate instrumental WCS and empirical PSF variation, propagate full Gaia astrometry (including CIDA 11 high RUWE), and perform uncertainty-aware multi-exposure comparisons. A passing code test or small centroid residual cannot establish astrophysical source identity.

Read the [v1.7 real-image audit](reports/field_controls_v1.7/REAL_MULTIEPOCH_AND_CONTROL_LIMITS.md) and [methods/safety caveats](docs/PHASE17_SAME_IMAGE_CONTROLS.md).
