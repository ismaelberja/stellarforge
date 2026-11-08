# StellarForge v1.12 — Real original ZTF FITS: Gaussian versus aperture-centroid screening

**Observed 8 November 2026 · [Successful original-FITS/real-Gaia workflow](https://github.com/ismaelberja/stellarforge/actions/runs/42459615687).**

**Status:** diagnostic comparison of **two image centroid estimators applied to the same original pixels**, not a validated Gaia–ZTF crossmatch, empirical ZTF PSF, independent WCS calibration or physical discovery. In this version we deliberately **do not infer an instrumental astrometric accuracy** from agreement between estimators.

## Input and verified provenance

- The original official IRSA/ZTF photometric artifact was downloaded **to an ephemeral GitHub Actions runner only** and rechecked against the original acquisition manifest: **2,212 real positional-cone photometric rows** for FT Tau and CIDA 11. These are **not independent physical source identifications**.
- Four originally selected g-band ZTF dated science exposures were reconstructed from their source filefracday, field, CCD/quadrant, and band. Their dates and OIDs were cross-checked against the immutable v1.8 derived ledger, SHA-256 `fb7d5c315cbef56b2551e73920c67920827d91160b4c0bd35f3fd77113166beb`.
- A bounded official Gaia DR3 exact-source query recovered **10 complete five-parameter catalogue solutions** (two targets plus eight candidate references), with full formal astrometric correlations and epoch-dependent **first-order geometric Earth-geocentric annual parallax**.
- **20 actual official ZTF science-image FITS cutouts were requested**: four target image stamps and 16 candidate reference stamps. The *same dated ZTF science FITS product path* was reused within each exposure, but centered separately for every Gaia source. Each request is bounded to **45″** and uses the original ZTF exposure, not a coadded reference.
- Raw Gaia TAP CSV, ZTF photometric tables and all FITS pixel arrays were kept in temporary runner memory. The Git repository and published workflow artifact contain **only aggregate source identifiers, source fit status, diagnostic numbers, provenance checksums and scientific caveats**.

The exact dated ZTF science filenames and their associated instrument products are described in the [official IRSA ZTF metadata documentation](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html) and [ZTF image API](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_api.html).

## Pixel-level remeasurement algorithm

Each candidate source's Gaia DR3 position is propagated using the same formal five-parameter model as v1.11, now including its **own** annual geometric parallax. The predicted ICRS sky location selects a small square cutout from the original dated `sciimg.fits` detector product.

On the **same original real FITS pixels**, two different centroid descriptions are evaluated:

1. The existing bounded **elliptical Gaussian + tilted sky plane** fit from v1.6, with image residual/noise and optimizer-bound flags.
2. A new, independently coded **sigma-clipped planar local sky fit**, using sky annulus radii 9–15 pixels and an interior **positive-flux circular aperture radius 4.5 pixels** to calculate a flux-weighted centroid and approximate second-moment axis-ratio proxy.

The difference between the two predicted ICRS centroid positions is reported as **image-model sensitivity**, not independent observational repeatability. The same original image, WCS and astrophysical scene are shared; the result cannot prove calibration quality or exclude contamination.

A source is marked `APERTURE_GAUSSIAN_CONSISTENT_PROVISIONAL` only with a converged, non-flagged Gaussian model, usable finite sky/aperture pixels, a significant local peak, plausible aperture morphology, two estimator positions within 0.35″, and no obvious discrepancy with FITS MJD metadata. **This pass is not a stellar PSF-quality certificate.** Individual source quality failures are retained rather than overwritten by a field-level median.

The FITS header's `OBSMJD`/`MJD-OBS` values, if present, are checked for rough agreement with the original query MJD (within ~0.04 day). This does **not** independently validate UTC/time system or the exposure timestamp definition.

Critically, **no calibrated `mskimg.fits` bitmask, saturation flag calibration, instrumental pixel variance/PSF model, filter-colour residual model, or independently registered sky solution is yet used**. The official [IRSA ZTF product list](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html) also provides `mskimg.fits`, `psfcat.fits` and `sciimgdao.psf` / `sciimgdaopsfcent.fits` associated with each science exposure. Those are logical next primary-survey resources to validate rather than simulate instrumental models.

## Real results (source counts, including archive failures)

**Twenty** actual original science cutout requests resulted in:

- **9 HTTP 503** (service transport errors, **not physical non-detections**);
- **2 inconclusive aperture screens** (insufficient signal/model check);
- **9 usable two-centroid image screens**: **3 targets** and **6 reference candidates**.
- Of the six reference two-model screens, **all six met the defined provisional internal image-estimator agreement gate**. This does not independently authenticate a single clean star or calibrate detector WCS.

The **median aperture-versus-Gaussian centroid separation was 0.116948″ across nine completed two-model screens**. The range was 0.040506–0.184142″. This is not a source positional error or standard error; it is an estimator/model-dependence diagnostic on the same pixels.

| Technical target | Original science MJD | Target screen | Gaia candidate references screened with both models | Internal-consistent reference candidates |
|---|---:|---|---:|---:|
| FT Tau | 58388.389016 | HTTP 503 | 2 | 2 |
| FT Tau | 58491.184780 | Model review required | 0 | 0 |
| CIDA 11 | 58475.113750 | Provisional two-model agreement | 3 | 3 |
| CIDA 11 | 58849.135984 | Model review required | 1 | 1 |

Only **one of four science exposures** now has at least three model-consistent candidate references: **CIDA 11, MJD 58475.113750**, with three references.

For those **same three references** in the one usable CIDA 11 exposure, the internal leave-one-reference-out disagreement RMS is:
- **0.072594″ with the Gaussian centroid estimator**;
- **0.118163″ with the aperture centroid estimator**.

These are two different **sample-internal** held-out disagreement scores from the **same original observations**. Their difference is more evidence of sensitivity to image-centroid modeling, rather than an objectively better or worse absolute astrometric calibration. A fitted WCS and formal WCS error budget have **not** been established.

## Cross-version interpretation

The v1.10 and v1.11 analyses had two historically eligible reference sets under the original single-Gaussian quality filter. The v1.12 pixel analysis applies a different, **stricter dual-estimator and live-archive-availability gate** and finds only one qualifying exposure; consequently, the counts are **not directly interchangeable**. Archive HTTP 503 also prevents some exposure/source comparisons; missing data must remain explicitly unavailable.

The 0.116948″ median *Gaussian/aperture difference* is not a calibrated error or a physical source offset, and it must not be directly compared to the v1.11 annual-parallax correction as if all represented estimates of the same physical measurement uncertainty.

The FT Tau MJD 58388 target HTTP 503 is transport failure only. Two other target stamps need model review. CIDA 11's **Gaia DR3 RUWE ≈8.57** still raises concerns that its single-source astrometric solution does not fully describe the physical source. Even the best-screened CIDA 11 image has **no independent Gaia–ZTF source identity confirmation**.

## Software validation and provenance

The real observed-data workflow completed successfully on GitHub Actions with **506 automated tests passed**, together with the source-archive and Gaia-ID integrity checks. The source runs on an ephemeral runner, records HTTP errors and SHA-256 for available FITS downloads, and uploads an **aggregate-only report** (not source pixels).

- [Methods and image quality safeguards](../../docs/PHASE112_PIXEL_CENTROID_AND_WCS_LIMITS.md)
- [Source code](../../src/stellarforge/v112_pixel_model_crosscheck.py)
- [Real-data execution script](../../scripts/run_v112_real_fits_crosscheck.py)
- [Real-data GitHub Actions evidence](https://github.com/ismaelberja/stellarforge/actions/runs/42459615687)

**Scientific gate status: 0 independently calibrated detector WCS solutions; 0 verified empirical single-star PSFs; 0 confirmed Gaia–ZTF physical source identities; 0 new companions; 0 physical variability detections.**

## Next scientific phase

Work with original dated **ZTF `mskimg.fits` bad-pixel/flag masks and official `sciimgdao.psf` or `sciimgdaopsfcent.fits` instrument products** (documented by IRSA) under a small controlled archive request budget. Independently validate point-like reference-source morphology/contamination and a calibrated PSF/WCS error model on enough held-out stars, explicitly accounting for FITS observation epochs, detector biases and Gaia covariance. Only then can one begin to assess physical variability or source identification.
