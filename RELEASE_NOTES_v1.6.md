# StellarForge v1.6 — provisional Gaussian image-profile diagnostics

**Date:** 5 November 2026  
**Research/software status:** tested engineering milestone; astrophysical source identity not yet verified.

## Improvements
- Added a bounded robust single-Gaussian-plus-plane fit for real ZTF FITS image pixels, distinct from the v1.5 simple local maxima screen.
- Added per-image model width (two axes), axis ratio, fitted centroid residual against propagated Gaia position, local-noise and positive model-residual diagnostics.
- Added per-OID/filter repeated science-image comparison **only** if two or more distinct valid science FITS files exist. Reference-image coadds never count as independent science epochs.
- Added fully synthetic tests for Gaussian recovery, missing/weak signal, bad WCS, nearby residual peaks, archive failures and science-only repeatability.
- Continued restricting public GitHub uploads to aggregate JSON/Markdown; original photometric CSV and FITS pixels remain ephemeral.

## Real data audit
Using official IRSA inputs for FT Tau and CIDA 11 (2,212 raw photometric rows in six OID/filter groups), [the v1.6 run](https://github.com/ismaelberja/stellarforge/actions/runs/42033819374) obtained **three individual FT Tau science-image Gaussian proxy fits**. Each exhibited positive residual structure requiring follow-up under this deliberately simple model; this is **not evidence of a companion, binarity or stellar variability**. No CIDA 11 image was modeled in this iteration. 17 of 21 image requests returned HTTP 503, one returned URLError; **zero OID/filter groups have two independent science fits**, so multi-epoch consistency cannot yet be measured.

[Real-image Gaussian shape report](reports/psf_v1.6/REAL_GAUSSIAN_FIT_REVIEW.md) | [Methods and limitations](docs/PHASE16_PSF_PROXY_AND_REPEATED_SCIENCE_EXPOSURES.md)

**Engineering quality:** 387 automated regression tests passed.

## Unresolved
Full empirical PSF calibration, WCS recalibration, photon/read-noise and saturation treatment, Gaia astrometric covariance/parallax, non-Gaia contaminants, genuine multi-epoch science consistency, and independent original Taurus catalogue comparison. **No verified Gaia–ZTF crossmatch or astrophysical event.**
