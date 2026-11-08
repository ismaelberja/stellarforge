# StellarForge v1.15 — Original ZTF spatial DAOPhot PSF lookup reconstruction and native center-FITS comparison

**8 November 2026 · Scientific Python/astronomical data-engineering milestone.**

## Implemented

- An original **ASCII ZTF `sciimgdao.psf` Gaussian-plus-spatial-lookup-table parser**, with source SHA-256 and strict header, geometry and coefficient checks. Observed **4 real native 88,465-byte model files**, each a `GAUSSIAN` analytic kernel plus **3 × 47 × 47** half-pixel sampled spatial correction arrays (constant/linear), native detector center x=1535.5, y=1539.5.
- Independent-code approximate PSF evaluation on a **23 × 23** source stamp using a pixel-integrated analytic Gaussian, normalized CCD-position polynomial lookup corrections, cubic B-spline interpolation (not claimed bitwise-equivalent to native DAOPhot bicubic), positive-only pixel content and unit-sum normalization.
- An **external file-format/model-reconstruction check** against the four **real original official `sciimgdaopsfcent.fits` science-field-center PSF stamps**, with normalized pixel cosine similarity and L1 difference. They originate from the **same** ZTF pipeline as DAOPhot, so the numerical comparison tests reconstruction compatibility, **not independent astrophysical PSF truth**.
- Reused the four actual original ZTF `psfcat.fits` source fit catalogues and formal Gaia DR3 5D/geometric annual parallax predictions from v1.14 to reconstruct model PSF shapes at all **16 provisionally selected ZTF native source detector positions**. No source identity or local real-star PSF accuracy is certified.
- Adversarial tests for unknown analytic model, malformed/partial lookup coefficients, unsupported variation order, wrong CCD coordinate, fractional pixel phase, center-image shape mismatch, rejected bad profile sources, and overconfident source/PSF calibration claims.

## Real observed-data evidence

[Actual original NASA/IPAC IRSA and Gaia pilot](https://github.com/ismaelberja/stellarforge/actions/runs/42514987086): **590 automated tests passed**, original 2,212-row source transport SHA-verified, **4/4** full native spatial DAOPhot files decoded, **4/4** independent-code center reconstructions matched genuine archived center PSF FITS stamps, and **16/16 v1.14 pre-screened candidate detector-position PSF shapes evaluated**.

| Real original science exposure | Center model cosine similarity | Normalized PSF L1 difference |
|---|---:|---:|
| FT Tau MJD58388.389016 | 0.999999 | 0.000984 |
| FT Tau MJD58491.184780 | 1.000000 | 0.000278 |
| CIDA 11 MJD58475.113750 | 1.000000 | 0.000303 |
| CIDA 11 MJD58849.135984 | 1.000000 | 0.000355 |

[Full scientific real-data report](reports/spatial_daophot_v1.15/REAL_DAOPHOT_CENTER_AND_LOCAL_SHAPES.md) · [methods, provenance and scientific limits](docs/PHASE115_DAOPHOT_SPATIAL_MODEL_VALIDATION.md).

## What is still NOT verified

The original native DAOPhot field-center FITS was itself computed from the spatial lookup model. **Excellent center agreement does not validate a PSF against an independent real star in the field**, nor independently calibrate astrometric WCS, photometric flux, Gaia/ZTF physical identity or the absence of stellar contamination.

The local source-position model PSFs still need **same-exposure original science pixels, bit masks, subpixel phase and an independently vetted/held-out field-star residual analysis** to establish real source-local PSF precision. Gaia DR3 CIDA 11 target RUWE ~8.57 remains an unresolved non-single-star model-quality caveat. No companions, physical variability or population incidence claims are made. All raw original IRSA/ZTF/Gaia/DAOPhot coefficient and image bytes remain transient; public source and artifacts contain only methods and derived summaries.

**Next gate:** observational residual validation of local PSF shapes against actual mask-checked original ZTF star pixels with independent field controls, plus detector WCS/PSF covariance/error budget from held-out Gaia stars.
