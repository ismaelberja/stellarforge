# Phase 16 — Gaussian shape proxies and multi-exposure repeatability

**Scientific label: engineering/provisional, not a confirmed Gaia–ZTF crossmatch, PSF calibration, companion or physical variability event.**

## Why a v1.6 gate is needed

v1.5 directly inspected five actual FITS cutouts and found local brightness maxima near the nominal Gaia-propagated coordinates. A smoothed local maximum does not establish a single astronomical source, and comparing reference coadds to individual epochs can hide image-specific systematics. v1.6 adds quantitative *shape proxies* and compares independent science exposures only **within the same original ZTF OID and filter**.

## Implemented method

1. Retrieve at most **three separately dated science cutouts per OID/band**, and a reference coadd only if no useful science image is obtained. Each cutout is capped at 3 MB and is read **in memory**, never committed or uploaded.
2. Verify the original 2,212-row official IRSA acquisition and source SHA-256 via the v1.3 provenance contracts.
3. Run the v1.5 2D FITS/WCS validity screen. Use Gaia J2016.0 approximate two-dimensional proper motion to predict the location at the individual science MJD, without claiming covariance/parallax modeling.
4. Estimate a **local background and noise proxy** from the pixel annulus at 9–15 px. Require sufficient finite pixels and a central peak above five times the local median-absolute-deviation-based noise proxy.
5. Fit a **single axis-aligned elliptical Gaussian plus locally tilted planar background** within seven pixels. The robust optimizer constrains the apparent center to 2.5 pixels of the predicted sky coordinate and the Gaussian sigma to 0.6–5 pixels. A positive residual, elongated profile or parameter near a bound triggers a review flag.
6. Record fitted FWHM along the two pixel axes, axis ratio, peak amplitude/noise proxy, model residuals and signed east/north offsets relative to the input WCS-predicted Gaia location. **These are not calibrated ZTF PSF measurements or independent stellar centroids.**
7. When **at least two distinct original science image SHA-256s** within an OID/filter have valid fits, calculate descriptive image-to-image differences in their signed WCS residuals and approximate Gaussian FWHM. Reference-image coadds never contribute to the multiple-science-exposure denominator.
8. Return the full error/status ledger, never silently promoting remote HTTP 503 failures or poor PSF fits to evidence of absent variability or astrophysical sources.

## Why the limitations matter

- **PSF proxy != PSF fit for discovery**: an axis-aligned Gaussian cannot fully model the ZTF instrumental PSF, wings, variations over the detector, saturation, charge bleeding, nebulosity or unresolved binaries.
- **Local model residual != new companion:** a positive pixel residual may reflect PSF mismatch, photon noise, cosmic rays or irregular sky background.
- **Repeatable residual != independently confirmed source identity:** images share instrument and calibration systematics, and Gaia propagation omits full covariance, parallax and perspective acceleration.
- ZTF reference coadds have different noise and PSF characteristics and are **not independent dated science images**. They remain separate.
- A fitted source with low residuals does **not** rule out unresolved contamination.
- **CIDA 11's Gaia DR3 RUWE ~8.57** makes its simple astrometric propagation particularly uncertain and warrants individual review.
- The source table currently uses a pinned third-party Taurus mirror; comparison with the publisher original is still pending. No independent disk classes or actual variable-star classifications are claimed.

## Reproduce using an original official IRSA artifact

\`\`\`bash
python -m pip install -e '.[test,analysis,images]'
python -m pytest -q
python scripts/run_v16_psf_repeatability.py /path/to/official_IRSA_raw_archive.zip \\
  --output reports/generated/v1.6_psf --timeout 8 --fail-if-no-fit
\`\`\`

The raw ZIP must contain the real archived files and their provenance ledger. The public GitHub workflow uses ephemeral runner storage and uploads **JSON/Markdown aggregate diagnostics only**, never source CSVs, FITS pixels, login credentials or unpublished collaborative data.

## Next scientific work

Use independently calibrated stellar PSFs, real local background and detector mask maps, spatially resolved field-star controls, PSF subtraction, multi-epoch source/neighbor image registration, Gaia full astrometry and systematic error budgets. The higher-threshold aim is a **scientifically defensible source identity and blending audit**, not just a passing software test.
