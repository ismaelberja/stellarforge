# StellarForge v1.16 — Real original ZTF science pixels, detector bitmasks and native spatial-PSF residuals

**8 November 2026 · Scientific Python and observational data-processing milestone.**

## What is new

v1.16 takes the four native spatial ZTF DAOPhot lookup models decoded in v1.15 and **fits them to the original ZTF `sciimg.fits` science-image pixels, applying WCS-aligned original `mskimg.fits` detector masks** for every one of the sixteen v1.14 provisionally source-associated native PSF catalogue candidates.

Each original single-exposure source science+mask pair is tied to exactly the same original dated science file, ZTF native per-exposure `psfcat.fits` `ra/dec` and **full detector** `xpos/ypos` (not local cropped pixel indexes). Before fitting, the code verifies original science/mask two-dimensional celestial WCS mapping to within **0.05 pixel**, native-versus-cutout subpixel phase consistency to within **0.22 pixel**, original bitwise disqualifying/saturation pixels (official ZTF 6141 policy) and adequate unmasked source/sky coverage.

The **native source PSF shape remains fixed**. Fit its amplitude (uncalibrated original digital numbers, DN) and a linear local sky plane to one checkerboard half of the same star image, then evaluate residuals on the other **same-source image pixels**, normalizing against an annular robust MAD noise proxy. This **does not independently calibrate a true stellar PSF, authenticate a physical Gaia–ZTF crossmatch, measure source flux in calibrated magnitudes, or establish detector WCS precision**.

## Real original observation data

[GitHub Actions observed-data run](https://github.com/ismaelberja/stellarforge/actions/runs/42518746629): **614 automated tests passed**, original 2,212-row SHA-audited IRSA intake verified, original four native `psfcat.fits` catalogues, four DAOPhot spatial lookup models and four native field-center PSF sanity checks completed, and **16/16 genuine original science+detector mask source-pair PSF pixel fits** completed without remote HTTP 503.

- **13/16** selected original source image fits met the predefined provisional same-image withheld-pixel residual quality thresholds; **3/16** require review.
- The technical target subset completed **three** original science pixel fits (FT Tau 2, CIDA 11 1), with two target fits flagged for residual review (FT Tau MJD58491.184780 and CIDA 11 MJD58849.135984).
- An additional Gaia candidate reference source **3419111520318480128** in the CIDA 11 field at MJD58849.135984 was flagged for residual review.
- Those three sources showed maximum positive residuals of **7.6730**, **11.8679** and **7.8125**, respectively, measured **relative to a robust annular sky-noise proxy**, not as independent statistical significance or companion SNR.
- Median same-image withheld-pixel RMS/annulus noise proxy across sixteen source fits: **1.1015**.
- All 16 fitted original PSF source cores have zero bad/saturated detector mask pixels within their 4.5-pixel apertures. That fact does not prove physical isolation, absence of blending or source identity.

[Full source-by-source numerical evidence](reports/masked_spatial_psf_v1.16/REAL_ZTF_PIXEL_RESIDUALS_EVIDENCE.md) · [Methods, mask-bit semantics and open science gates](docs/PHASE116_ORIGINAL_MASKED_PSF_PIXEL_RESIDUALS.md).

## Scope and remaining uncertainties

The source sky coordinates and spatial PSF native detector positions both originate from the **same ZTF PSF-fit source catalogue**. This is a genuine original CCD pixel validation of a fixed PSF model, but not independent Gaia/ZTF astrophysical identification or an instrumental WCS error budget. Each withheld checkerboard pixel is in the **same star image**, not a different star or epoch. The PSF lookup interpolation is an approximation, and the fitted amplitudes are not calibrated magnitudes (ZTF pixel units are DN). The original Gaia DR3 RUWE for CIDA 11 is ≈8.57, and the per-source background/crowding/model mismatch may explain review flags. No source companion or physical variability has been detected or confirmed.

All raw IRSA/ZTF photometry, original science/mask FITS pixel bytes, native PSF catalogue rows and DAOPhot lookup coefficients and raw Gaia TAP CSV remain temporary, **not in the Git repository or public Actions artifacts**. User-facing docs and release notes include only verifiable numerical scalar summaries.

## Next defensible phase

Independently authenticate and spatially distribute a larger set of ZTF/Gaia single-star controls, **withhold distinct field stars (rather than just pixels) from the model and evaluation**, and assess actual source-local PSF residuals plus sky/CCD correlated noise, native WCS/chromatic terms and astrophysical false-match rate. Revisit the three flagged review sources using independent dates, bands, nearby neighbors and robust background alternatives before even entertaining a physical companion/variability claim.

**Unverified scientific achievements remain at zero:** independently authenticated Gaia–ZTF physical matches, independently calibrated local field-star PSFs, full detector WCS uncertainty models, and confirmed companions/physical stellar variability.
