# Phase 1.15 — Original ZTF DAOPhot spatial PSF reconstruction versus native field-center FITS

**8 November 2026 · Original-data research-software method.**

## Scientific purpose

The v1.14 real ZTF survey-product pilot identified four original `sciimgdao.psf` spatially varying DAOPhot lookup-table files and four original native `psfcat.fits` binary source-extraction catalogues, and produced **16 nearest-source provisional Gaia/ZTF positional candidates** across four dated science exposures. The spatial lookup data had not been decoded, and thus no source-specific PSF had been reconstructed.

v1.15 now **parses/evaluates** native ZTF DAOPhot Gaussian-plus-lookup-table models in their genuine **full CCD-quadrant `xpos/ypos` detector coordinates**. A core validation is a comparison of independently generated center-of-field model reconstructions against the actual archived `sciimgdaopsfcent.fits` center stamp, **not** against an independently observed field-star PSF.

The [original ZTF survey-product list](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html) distinguishes the ASCII lookup-table `sciimgdao.psf` from the science-field-center FITS stamp. [Masci et al. (2019)](https://doi.org/10.1088/1538-3873/aae8ac) describes a Gaussian analytical component and spatially varying correction lookup tables. The [IRAF/DAOPhot documentation](https://iraf.readthedocs.io/en/latest/tasks/noao/digiphot/daophot/psf.html) describes analytic profiles with separately interpolated position-dependent residuals. The openly available MIT-licensed [ztforce PSF source implementation](https://github.com/Adam-Boesky/ztforce/blob/main/src/ztforce/psf.py) provided a useful independently documented reference for file-layout interpretation; this project implements its own parsing/evaluation and makes **no assertion of bit-for-bit DAOPhot interpolation equivalence**.

## The original file

The four actual original ZTF `sciimgdao.psf` files retrieved for FT Tau and CIDA 11 are each **88,465 bytes of ASCII** and start with a Gaussian analytic basis model header. Every one has:

- A lookup table of dimension **47 × 47** samples at half-image-pixel spacing.
- **Three** spatial correction tables (constant plus linear detector-position dependence).
- Two positive analytic Gaussian **half-width-at-half-maximum** axis parameters.
- Original native detector center coordinates **x = 1535.5, y = 1539.5**.
- An output model PSF footprint of **23 × 23 original image pixels** with radius 11 pixels.

For every array element on the target output footprint, the evaluator integrates the Gaussian over the pixel area rather than simply sampling a Gaussian at the pixel center. It then adds position-weighted lookup-table correction terms, using the full-detector source position relative to the original detector center. The lookup samples are interpolated with a cubic SciPy B-spline and negative model flux is clipped only as a numerical positivity safeguard; the final stamp is normalized to unit positive sum.

**Important approximation:** the SciPy cubic-spline interpolation is a good engineering proxy for, but **not guaranteed to reproduce**, the original DAOPhot bicubic lookup interpolation coefficients or special edge interpolation. The v1.15 direct center FITS test provides necessary evidence that our approximation reconstructs the archived center product, but not a validation of the model off-center on independent real star pixels.

## Actual observed-data selection

The exact historical 2,212-row official IRSA original ZTF acquisition is recovered only in an **ephemeral GitHub Actions runner** and hash-checked with its original manifest. The immutable v1.8 pilot ledger and original ZTF dates/OIDs determine **four** original g-band source exposures, one g-band ZTF OID per technical FT Tau/CIDA 11 field and two independent dates each.

The original v1.14 full `psfcat.fits` FITS catalogues are re-fetched and compared with exact ten Gaia DR3 predicted target/reference positions propagated to each historical MJD with their individual formal five-parameter covariance and first-order Earth-geocentric annual parallax. Native `psfcat.fits` `sourceid` is a **per-exposure counter**, not Gaia source ID. Only candidates that pass the original v1.14 nearest neighbor, unique-source assignment, `chi/sharp/SNR/flags` screens receive a local PSF evaluation. Poor-fitting or missing source IDs remain explicit review cases.

No original ZTF sky position, native CCD position, field-star identity, or source pairing is newly assumed true: even a low-separation catalogue neighbor is only **provisional** until an independent astrophysical crossmatch and PSF/field calibration.

## Internal model verification

For each original exposure:

1. Retrieve and parse the native original ASCII `sciimgdao.psf` spatial lookup; fail closed for unsupported analytic types/table geometry, unexpected coefficient counts, nonfinite data or invalid native detector coordinate.
2. Reconstruct the **center-of-detector** analytic-plus-correction PSF at x=1535.5/y=1539.5, with a full 23×23 normalized stamp.
3. Retrieve the original same-exposure **`sciimgdaopsfcent.fits`** stamp and compare its positive-flux normalized pixels to the independent-code predicted center. Require identical square array dimensions and finite pixel values before comparison.
4. Report cosine similarity of the two normalized PSF stamps and their normalized L1 difference. **Engineering acceptance only**: similarity at least 0.93 and L1 at most 0.50. These thresholds are explicitly *not* instrument accuracy, a physically calibrated error, or a PSF photometry uncertainty.
5. If the center check is available, evaluate local PSF shapes for every candidate ZTF native `psfcat` detector position meeting the original v1.14 quality gate. Report only dimensionality and descriptive normalized second central moments; **never raw per-source PSF pixel arrays or individual original coefficients**.

This does not optimize WCS, jointly fit physical/PSF centroid and flux to original star pixels, estimate real uncertainty or disambiguate unresolved blends.

## Verified real outcomes

The [real official ZTF/Gaia source-data workflow](https://github.com/ismaelberja/stellarforge/actions/runs/42514987086) succeeded with **590 passing tests**, all four original DAOPhot files structurally decoded, all four original official PSF center FITS images accessed, **four of four** center numerical model checks completed/accepted, and **16 original candidate source detector positions** evaluated.

[Detailed real numerical evidence, per-exposure center-similarity and source-level PSF shape ranges](../reports/spatial_daophot_v1.15/REAL_DAOPHOT_CENTER_AND_LOCAL_SHAPES.md):

| FT Tau/CIDA 11 original science MJD | Native center-model cosine | Normalized center-model L1 |
|---|---:|---:|
| 58388.389016 | 0.999999 | 0.000984 |
| 58491.184780 | 1.000000 | 0.000278 |
| 58475.113750 | 1.000000 | 0.000303 |
| 58849.135984 | 1.000000 | 0.000355 |

**These center numerical comparisons are NOT independent astrophysical tests**: the original official center PSF FITS was itself generated from the native DAOPhot field model. Extremely good model agreement is therefore evidence of consistent file parsing and reconstruction, **not** proof of source-local PSF model accuracy or contamination-free stellar profile.

## Explicit scientific limits and next phase

- No direct comparison yet between reconstructed local PSF and original, WCS-registered, saturation/bitmask-validated `sciimg.fits` source pixels or held-out stars. v1.13 had valid original masks for four candidate reference cores and **zero target cores**.
- The separate v1.14 Gaia-nearest PSFfit catalog source screens remain **candidate identifications**, not physically verified source associations. CIDA 11 Gaia DR3 RUWE ≈8.57 makes single-star formal astrometry particularly questionable.
- The variation in *reconstructed model second moments* between date/field products is not a direct measurement of observational seeing or independently calibrated source morphology.
- Full Palomar topocentric apparent sky positions, atmospheric refraction/chromatic color terms, actual FITS mid-exposure timestamp conventions, detector WCS distortions and independent field-star errors are not included in local PSF model reconstruction.
- The reproduced PSF stamp is not a forced-photometry result, a time-domain light curve, a real physical companion test or a new astronomical discovery.
- The original source files and FITS pixels are processed transiently and are **not committed or included in public GitHub Actions artifacts**; keep only source SHA-256 hashes and derived small shape/quality summaries.

**Next gate:** retrieve actual same-date `sciimg.fits` and `mskimg.fits` original source cutouts, authenticate a meaningful spatially representative sample of stellar field controls, align full-native coordinate PSFs and subpixel pixel phase to the exact image frames, fit flux and sky background, and validate *real masked pixel residuals on held-out field stars*. Only after these independent controls can one assert an instrumental PSF/WCS error model or source-matching confidence.
