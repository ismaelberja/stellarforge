# StellarForge v1.8 — Gaia DR3 catalogue-backed controls on real ZTF exposures

**Date:** 5 November 2026. **Research/software status:** engineering improvement, not an independent Gaia–ZTF crossmatch or astrophysical discovery.

## Implemented

- Added an independent 210-arcsec Gaia DR3 TAP cone query for each technical Taurus target, with a strict 500-row cap and rejection of malformed/incomplete catalogues.
- Screened Gaia candidates for isolation from **all** nearby Gaia sources, Gaia G-band brightness/flux signal-to-noise, RUWE, duplicated-source flags and 5/6-parameter astrometric quality.
- Retargeted **the same dated original ZTF science FITS product** to the Gaia candidate's approximate epoch-propagated position, with no raw FITS/image publication.
- Used the prior robust Gaussian image shape proxy to obtain provisional control-star candidate centroid/width and residual diagnostics.
- Added a fail-closed *median reference-offset translation proxy* requiring at least three different Gaia IDs; and a strictly labelled target-minus-reference diagnostic. Neither is a full/independent WCS solution.
- Added synthetic tests for Gaia TAP input validation, quality isolation, transport failures, deduplication, reference count and false astrophysical claims. **422 automated tests passed** in the v1.8 development branch.
- Documented the method and real results in [the v1.8 methods note](docs/PHASE18_GAIA_REFERENCE_STAR_CANDIDATES.md) and [observational report](reports/gaia_reference_v1.8/REAL_REFERENCE_CANDIDATE_EVIDENCE.md).

## Observational audit

[GitHub Actions real-data run 42077605987](https://github.com/ismaelberja/stellarforge/actions/runs/42077605987) queried 50 Gaia DR3 entries around FT Tau and 250 around CIDA 11, selecting **3 and 5 quality-screened reference candidates**, respectively. Four ZTF target science cutouts and 16 Gaia-reference cutouts were attempted; the four target images and **13/16 candidate reference image models** were successfully fitted. **Three exposures had sufficient references for provisional local east/north WCS translation**, without any independent calibration claim.

**Scientific boundary:** these are catalogue-backed *candidate* references, not authenticated clean stellar PSFs. CIDA 11's own high RUWE remains unresolved. No full Gaia parallax/covariance, field distortion recalibration, independent source association, PSF deblending, companions or physical variability events can be claimed.

## Next

Validate true isolated stellar reference PSFs and colour/filter-dependent image calibration, propagate full Gaia uncertainties, and extend carefully to all six ZTF OID/filter groups and multiple epochs with reproducible uncertainty budgets. No raw original third-party ZTF photometry, Gaia TAP response or FITS images are committed.
