# Phase 1.12 — independent aperture-versus-Gaussian pixel centroid diagnostics

**Scientific intent:** test the sensitivity of *source image-centroid estimates* to two different algorithms on original single-exposure ZTF FITS pixels. The estimators are **not independent observations**: both share the same CCD, original header WCS, sky background, uncalibrated PSF and potential astrophysical blends.

## Official astronomical data products

An original SHA-verified **2,212-row** positional-cone ZTF/IRSA acquisition ZIP and the four original g-band source-exposure dates (v1.8 derived evidence ledger) determine the **same original ZTF `sciimg.fits` science file for each target and its candidate Gaia reference stars**. The ZTF image endpoint is the [official IRSA IBE FITS cutout service](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_api.html), using a bounded **45-arcsec cutout** centered at a Gaia astrometric prediction. No coadded reference is treated as an independent science observation.

Gaia DR3 is queried only by **ten exact catalogue identifiers**, with each star's source-specific epoch-matched geometric annual parallax and five-parameter formal covariance (including ten cross-correlation terms) derived using the existing v1.9/11 code. These coordinates are not full observatory-topocentric apparent positions and do not establish Gaia–ZTF source identity.

Original raw FITS bytes and catalogues are retained only in process memory / the temporary workflow runner and are never included in git commits, program output or GitHub artifacts. Files/URLs are checked against the exact official IRSA host, product path, observing date and FITS size. The original IRSA acquisition input is reverified byte by byte against its SHA manifest.

## Two independent algorithms, same image

The existing v1.6 bounded **elliptical Gaussian + local sky plane** provides a parametric PSF-shape *proxy* and center with an explicit residual/optimizer quality flag. The new non-parametric method uses a **sigma-clipped local tilted sky-plane fit** in an annulus 9–15 pixels around the predicted star, a positive-flux aperture centroid within 4.5 pixels, second central-moment aspect ratio, finite-pixel tests, and its own sky-noise/SNR checks.

All source quantities are converted back to a common ICRS header-WCS tangent plane. The distance between the two fitted centroids measures **dependence on model assumptions**. It is **not a physical displacement, a calibrated 1σ centroid uncertainty, a source-association likelihood, or a test on statistically independent data**.

A provisional internal image-model match requires: valid celestial WCS and original pixel array; usable sky and finite aperture; strong local flux; non-pathological aperture ratio and centroid shift; non-flagged Gaussian model; model-center agreement within **0.35 arcsec**; and no large discrepancy between original query MJD and available FITS MJD header. If any of these fail, report `INDEPENDENT_APERTURE_MODEL_REVIEW_REQUIRED` or `APERTURE_CENTROID_SCREEN_INCOMPLETE`, never an astrophysical non-detection.

The experiment retains the old reference-star candidate set and source IDs, instead of expanding post-hoc until sufficient stars are found. Within each actual science exposure, a provisional leave-one-candidate-out comparison is computed only for three or more two-model-screened candidate references. These reference candidates are **not yet verified as isolated single stars**.

## Missing instrument calibrations remain explicit

IRSA documents original-science-image companions such as [the ZTF bitmask `mskimg.fits` and native spatial PSF products](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html), including `sciimgdao.psf` and `sciimgdaopsfcent.fits`. v1.12 **does not consume those products**, so its reported FITS header `SATURATE` (when present) is at best metadata and never proves unflagged pixels. In particular, cosmic rays, bleed trails, bad-pixel/interpolation flags, saturation, spatial PSF wings and nebulosity cannot be ruled out simply because two centroids agree. Likewise, matching a FITS `MJD-OBS` or `OBSMJD` with a photometric-query MJD does not establish the precise original telescope time scale or exposure midpoint.

**CIDA 11 Gaia RUWE ≈8.57** remains a serious source-model reliability caveat even for images passing both centroid algorithms. The catalogue formal Gaia covariance cannot replace image-specific instrument PSF, sky background, WCS distortion and correlated CCD error terms.

## Real pilot: what is and is not proven

[The v1.12 real-data report](../reports/real_fits_v1.12/REAL_TWO_CENTROID_MODEL_QA.md) documents **two separate 20-request runs on the same historical ZTF science dates and source IDs**. Initial run A ([evidence](https://github.com/ismaelberja/stellarforge/actions/runs/42459615687)) returned nine HTTP 503 errors, two incomplete pixel screens and nine completed two-centroid fits; six candidate reference sources passed provisional cross-model agreement. **Final-code run B** ([evidence](https://github.com/ismaelberja/stellarforge/actions/runs/42460247095)) returned eight HTTP 503 and **twelve completed two-centroid fits** (one target and eleven reference sources), with **nine provisionally model-consistent reference candidates** and final median centroid-model separation **0.104720 arcsec**. Four overlap cutouts available in both runs had **identical FITS SHA-256 hashes**. The runs do not represent new independent sky epochs.

On **CIDA 11 MJD 58475.113750**, the final run B had **four** qualifying candidate reference stars, with leave-one-reference-out internal RMS **0.064675″ (Gaussian)** versus **0.155762″ (aperture)**. The target image of that science exposure was **inaccessible with HTTP 503** in the final run. The difference underscores dependence on image estimator and reference availability; it is **not** a validated instrument error or a source motion.

**506 automated tests passed in both workflows.** Access errors, source-quality failures and unverified timing and saturation/mask metadata remain explicit in the derived aggregate JSON.

## Reproduce with the original official acquisition ZIP

```bash
python -m pip install -e '.[test,analysis,images]'
python -m pytest -q
python scripts/run_v112_real_fits_crosscheck.py /path/to/verified_original_IRSA_acquisition.zip \
  --image-timeout 6 --gaia-timeout 25 --require-some-valid-images
```

The command requires the original official archive manifest and data bytes. If its temporary artifact has expired, the proper next step is to acquire a **new official IRSA dataset with separately versioned provenance**, not to substitute an arbitrary CSV. The small observed aggregate report is reproducible as a check of the original execution, not a replacement for raw FITS pixels.

## Next defensible science work

Obtain and decode **matching original ZTF `mskimg.fits` masks**, **real instrument PSF products** and, where feasible, source catalogs on the same dated CCD quadrant. Verify saturation, bad-pixel flags, spatial PSF/residual morphology, color-dependent differences and image time conventions. Establish an instrument-calibrated WCS by fitting and externally testing it on a larger set of **independently authenticated and spatially distributed field stars**. Use held-out sources and realistic errors rather than claiming the current small-sample internal residual is a 1σ positional accuracy.

**Unconfirmed:** zero independently authenticated Gaia–ZTF physical matches; zero calibrated empirical PSFs; zero independently calibrated detector WCS; zero newly established physical companions or variability events.
