# StellarForge v1.5.0 — Real FITS pixels, celestial WCS, and cautious peak screening

**Date:** 5 November 2026. **Type:** research-software engineering milestone.

## New features

- Added `src/stellarforge/v15_image_pixels.py`, with bounded official IRSA science/reference FITS downloads, 2D image and celestial-WCS checks, finite-pixel screening, robust background/noise proxy and explicitly provisional intensity-peak evidence.
- Added provenance-controlled `scripts/run_v15_image_pixels.py`, which verifies the previous IRSA ZTF archive hashes and compares each OID-band independently.
- Introduced synthetic FITS/WCS fixtures and checks for image-free sky, a second close peak, malformed WCS, NaN pixels, image bounds and failed remote requests.
- Updated offline GitHub Actions for the optional `images` dependency bundle; remote image audit remains manual-only.
- Published the real-data summary in [the v1.5 observational evidence report](reports/real_fits_v1.5/PIXEL_WCS_RESULTS.md).

## Actual data findings

From the two original official IRSA cone searches (2,212 photometric rows, six independent OID/filter groups), the [v1.5 real-data workflow](https://github.com/ismaelberja/stellarforge/actions/runs/42029766535) analyzed **five real FITS pixel arrays** including valid WCS: **three individual science exposures plus two reference coadds**. Four OID-band groups belong to FT Tau and one to CIDA 11. CIDA 11's g-band image could not be retrieved because all candidate URLs returned HTTP 503. In each usable cutout, one image-local maximum was found within 0.5 arcsec of the approximate Gaia-predicted position. No separate bright maxima passed the threshold within 12 arcsec; this **does not imply there are no companions or blends**.

**373 automated regression tests passed.** No real photometric or image data bytes were committed to GitHub; CI uploads aggregate reports only.

**Scientific boundary:** no independent Gaia–ZTF identity confirmation, no PSF deblending, no independent WCS astrometric recalibration, and no physical detections. High RUWE for CIDA 11 requires more detailed astrometry.

## Next target

Independent PSF/background deblending and WCS residuals across multiple science exposures, alternate archival imaging for CIDA 11 g, and Gaia covariance/parallax-aware source-position modeling.
