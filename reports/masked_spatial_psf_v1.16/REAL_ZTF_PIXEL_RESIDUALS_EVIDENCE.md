# StellarForge v1.16 — Real original ZTF science+mask pixel residuals with spatial DAOPhot PSFs

**Observed-data verification: 8 November 2026.** [Successful full real-data run, 614 tests](https://github.com/ismaelberja/stellarforge/actions/runs/42518746629).

## What has actually changed

v1.15 parsed spatial DAOPhot point-spread functions (PSFs) and reconstructed approximate 23×23 PSF stamps at original native CCD-quadrant coordinates, but it had not fitted genuine stellar pixels. **v1.16 now applies those exact historical-exposure models to *real original science-image pixels* with their matching original detector bitmasks**, while leaving source identity and astrophysical interpretation strictly provisional.

All four dated original `sciimg.fits` science exposures are anchored to the verified 2,212-row original IRSA/ZTF positional-query acquisition (two epochs in FT Tau and two in CIDA 11). For each exposure, the native source `psfcat.fits` and spatial `sciimgdao.psf` are retrieved. The original center-field FITS `sciimgdaopsfcent.fits` first checks that the reconstructed DAOPhot lookup model is internally consistent. **Only then** are original 60″ `mskimg.fits` and `sciimg.fits` source-centered cutouts fetched, together, for the 16 candidates that passed the v1.14 native catalogue quality gates.

The source cutout centers come from each native `psfcat.fits` FITS source's own ICRS RA/Dec, and the spatial PSF correction is evaluated at that same catalogue source's **full detector** native `xpos/ypos`. All original Gaia identities are *only nearest positional candidate labels*, not physical source identifications.

## Actual original-data audit

The [GitHub Actions execution](https://github.com/ismaelberja/stellarforge/actions/runs/42518746629) completed with **614 automated tests passed**, four real original per-exposure native catalogues parsed, four spatial DAOPhot models parsed, and four archived native field-center PSF model sanity checks passed.

| Instrumental quantity | Actual result |
|---|---:|
| Original historical ZTF science exposure products | **4** |
| SHA-verified original IRSA positional query records | **2,212** |
| Gaia candidate × exposure PSF catalogue positions qualifying for image fitting | **16** |
| Source science/bitmask pairs requested | **16** |
| Science+bitmask pairs successfully retrieved and aligned | **16/16** |
| Actual original science-pixel PSF amplitude+background fits completed | **16/16** |
| Technical target fits | **3** (FT Tau 2, CIDA 11 1) |
| Candidate reference fits | **13** |
| Same-image held-out-pixel provisional residual screens passed | **13/16** |
| Residual-profile review required | **3/16** |
| Remote image/mask HTTP 503 | **0** |
| Core disqualifying mask-flag pixels in the sixteen successfully fitted apertures | **0** |
| New independently verified physical Gaia–ZTF source identities | **0** |
| Independently calibrated local stellar PSFs/WCS errors | **0** |

### Outcomes for the four real historical science exposures

| Field | Science MJD (start-time convention not independently established) | Source original masked PSF fits | Provisional residual screens passed | Review required |
|---|---:|---:|---:|---:|
| FT Tau | 58388.389016 | 2 | 2 | 0 |
| FT Tau | 58491.184780 | 4 | 3 | 1 (technical FT Tau target) |
| CIDA 11 | 58475.113750 | 5 | 5 | 0 (target did **not** pass original v1.14 catalogue gate and was not fitted) |
| CIDA 11 | 58849.135984 | 5 | 3 | 2 (CIDA 11 target and one reference) |
| **Total** | **Four original exposures** | **16** | **13** | **3** |

All 16 fitted original source cores had **zero original disqualifying ZTF bitmask pixels, including bit-8 saturation, in the nominal central 4.5-pixel radius**. This does not guarantee sources are isolated or unblended.

## How the actual masked pixel fit works

1. **Provenance and eligibility:** original source acquisition SHA and immutable v1.8 exposure ledger must agree on Gaia source IDs, dates, ZTF OIDs, field, band, CCD and quadrant. Gaia DR3 five-parameter *formal* covariance and first-order annual Earth-geocentric geometric parallax produce the same provisional candidate matching context as v1.15.
2. **Original mask geometry:** `mskimg.fits` and `sciimg.fits` must have the same array size and compatible two-dimensional celestial WCS pixel mapping within **0.05 pixel** at independent grid sample points. A shape match without WCS registration is not sufficient.
3. **Detector flags:** the original ZTF official bad-pixel bit template **6141** excludes anomalous and saturated detector pixels, while extracted-source marker bits 1/11 (2050) are not detector defects. Missing masks, nonfinite science pixels, malformed/negative/fractional mask values, and any central flagged/saturated pixels cause explicit rejection.
4. **Native source detector phase:** the fractional subpixel position from the original per-exposure `psfcat.fits` native `xpos/ypos` must agree with the celestial WCS position of the same source in the cutout to **within 0.22 pixel** (modulo 1-based/0-based integer origins). The actual 16 source evaluations differ by roughly **0.00007–0.00025 pixel**, which is a same-pipeline coordinate-consistency check, **not** an external WCS accuracy measurement.
5. **Independent sky annulus:** estimate a clipped local background median and robust noise *proxy* from unmasked, finite pixels in a surrounding **14–22-pixel annulus**. The minimum valid count is 230 pixels; the result is not a detector inverse-variance model.
6. **Fixed-position spatial PSF shape:** evaluate the *approximate* original spatial DAOPhot model at full CCD detector native `xpos/ypos` and the real cutout subpixel phase. Use it to fit four linear nuisance coefficients on original DN science pixels inside a 9-pixel radius: **PSF amplitude, sky constant, x-gradient and y-gradient**. The star position and PSF shape are fixed; this is not a deblending fit.
7. **Same-image withheld pixel residuals:** fit on one checkerboard partition of unmasked original image pixels and measure RMS and maximum positive residual on the **other checkerboard pixels of the exact same star, CCD exposure and sky scene**. Report them against the robust off-source annular sky MAD noise proxy. These held-out pixels are **not independent field stars, independent telescope exposures, absolute calibrated 1σ uncertainties or WCS validation**.

The engineering screen labels a source `PROVISIONAL_ORIGINAL_MASKED_PSF_PIXEL_RESIDUAL_SCREEN_PASSED` when the same-source checkerboard holdout RMS is at most **3×** its annular MAD noise proxy and its maximum positive held-out residual is at most **7×** that proxy, with adequate positive PSF amplitude and mask/WCS checks. These thresholds are **software quality-screen choices, not survey-calibrated astrophysical significance**.

**Real pixel residuals:** across all 16 completed original science-image fits, the median same-image withheld-pixel RMS/annular-noise proxy is **1.1015**, with many reference-star profiles approximately between 0.93 and 1.19. This descriptive value is not a calibrated pixel error or a measurement of absolute PSF accuracy.

### The three real review cases

| Candidate | Original science MJD | Held-out RMS/sky-noise proxy | Largest positive residual/sky-noise proxy | Interpretation |
|---|---:|---:|---:|---|
| FT Tau target | 58491.184780 | **1.6723** | **7.6730** | Maximum residual exceeds predefined 7× screen |
| CIDA 11 target | 58849.135984 | **2.6341** | **11.8679** | Maximum positive residual exceeds 7×, source astrometry high RUWE |
| Gaia reference candidate 3419111520318480128 (CIDA 11 field) | 58849.135984 | **1.3652** | **7.8125** | Maximum residual exceeds predefined 7× screen |

The residuals **do not identify their astrophysical cause**. Plausible alternatives include unmodeled spatial-PSF mismatch, background/nebulosity gradients, bad/correlated noise, unrecognized neighbors or source-position errors, in addition to unresolved blends. **They are not companion detections, confirmed variability, or confident Gaia–ZTF source identifications.**

## Additional scientific limitations

- **Instrument pixels are in Digital Numbers (DN).** The native fitted model amplitudes in this run are *not* absolute stellar physical fluxes or photometrically calibrated ZTF magnitudes. No science zeropoint, systematic color calibration, gain/Poisson noise, per-pixel inverse variance or instrument covariance has been applied. See [IRSA ZTF official release documentation](https://irsa.ipac.caltech.edu/data/ZTF/docs/releases/dr06/src/dr06.html).
- **Checkerboard pixels within one original star image are correlated** by resampling/seeing/PSF and sky modeling. The presence of a withheld pixel set does not create an independent held-out *star* sample or observational error budget.
- Both source sky coordinates and the spatial PSF native detector `xpos/ypos` originate from ZTF's same per-exposure native `psfcat.fits`. Their exceptional phase agreement tests **internal source/image coordinate consistency**, not an external telescope astrometric calibration.
- The ZTF DAOPhot correction interpolation uses a SciPy cubic B-spline approximation, not a proven bit-for-bit duplicate of the original DAOPhot bicubic routine; a model fitted on a source's own original pixels and native catalogue is not a truly independent physical PSF calibration.
- The IRSA original FITS header times refer to *start of exposure*, whereas time metadata in light-curve tables and different survey releases can use exposure-midpoint conventions. The real pilot does not independently verify exact telescope time systems, apparent-place corrections or chromatic refraction and therefore does not claim precise epoch-corrected astrometric accuracy.
- **CIDA 11 Gaia DR3 RUWE ≈8.57** remains a serious caveat in applying a nominal single-star Gaia astrometric solution, but does not on its own prove a binary companion.
- Only **four historical g-band original science exposures** were tested across the two technical fields. There has been no astrophysical light-curve/source attribution, long-term variability assessment, multi-band/multi-source sample completeness calibration or statistical population inference.

## Code, exact observed-data provenance and next scientific gate

[Original mask science-pixel fixed-PSF fit](../../src/stellarforge/v116_masked_original_psf_residuals.py) · [actual original-source live runner](../../scripts/run_v116_original_masked_psf_residuals.py) · [adversarial synthetic image/mask/WCS tests](../../tests/test_v116_masked_original_psf_residuals.py) · [successful 614-test original-data workflow](https://github.com/ismaelberja/stellarforge/actions/runs/42518746629).

**Next:** expand original science/mask sources to an independently authenticated and spatially representative field-star sample. Evaluate original spatial PSF residual profiles against **distinct stars withheld from PSF/WCS calibration**, using realistic CCD per-pixel variances and atmospheric/chromatic terms. Compare neighboring PSF-fit detections and independent survey identifications, and separately review the three flagged cases without assuming a binary or astrophysical variability.

**Scientific confirmation gate remains at zero:** no independently authenticated Gaia–ZTF physical source matches; no independently calibrated absolute detector WCS/PSF error budget; no newly confirmed binary companions or physical variability events.
