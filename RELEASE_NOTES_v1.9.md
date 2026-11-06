# StellarForge v1.9 — correlated Gaia DR3 astrometry and seasonal parallax

**Date:** 6 November 2026 · **Research software milestone**, not a physical discovery.

## Engineering additions

- Queries the **two exact Gaia DR3 source IDs** of the FT Tau and CIDA 11 pilot with five astrometric parameters, all five formal errors and **all ten correlation coefficients**; rejects missing or inconsistent covariances.
- Models epoch-specific geometric **annual parallax** relative to the old linear proper-motion-only approximation, using Astropy's offline Earth barycentric position.
- Propagates the full 5×5 *formal Gaia* covariance into a 2×2 east/north formal covariance by a numerical Jacobian. Explicitly warns when RUWE exceeds 1.4 and maintains the absence of any ZTF WCS/PSF error budget.
- Adds fully offline regression cases for correlation propagation, invalid covariance, Earth geometry, wrong data/IDs, high RUWE and epoch dependence.
- Publishes only compact aggregate science results. **444 automated tests passed** in the observed-data workflow.

## Verified Gaia DR3 pilot findings

The [v1.9 real-data run](https://github.com/ismaelberja/stellarforge/actions/runs/42175644367) evaluated the four original ZTF observation MJDs recorded by v1.8: FT Tau corrections relative to pure proper-motion positions range between **+6.791 and −4.781 mas east**, while CIDA 11 corrections for the two tested epochs are **−1.362 and −2.250 mas east**. Gaia-only formal east-coordinate uncertainties were around **0.07 mas** for FT Tau and **0.44–0.58 mas** for CIDA 11. These numbers are not calibrated ZTF astrometric uncertainties or proof of source identity.

The earlier CIDA 11 Gaia RUWE was confirmed as **8.56752**; a high RUWE renders the formal covariance particularly unsafe as a total physical error estimate.

[Detailed real results](reports/gaia_formal_v1.9/GAIA_COVARIANCE_AND_ANNUAL_PARALLAX.md) | [Methods and caveats](docs/PHASE19_GAIA_FORMAL_5P_AND_PARALLAX.md)

## Still unresolved

Physical Gaia–ZTF source association, independent instrument/field WCS calibration, empirical PSF and blending models, full 6p pseudo-colour/radial velocity cases, topocentric aberration/refraction, image time-scale verification, original publisher Taurus catalogue and all new astrophysical variability claims.

**No new companions, clean stars or astrophysical events confirmed.**
