# Phase 1.16 — Real original ZTF masked science-pixel PSF residual evaluation

**8 November 2026 — original scientific detector data and source-quality checks.**

## Original science goal and reproducibility

v1.15 showed that four original ZTF `sciimgdao.psf` spatial DAOPhot Gaussian-plus-lookup models could be reconstructed at their native field centers to match four `sciimgdaopsfcent.fits` native center stamps. Those center stamps were themselves derived from the **same ZTF pipeline model**, so this agreement was an internal file/model reconstruction check, not proof that the source-local instrumental PSFs describe actual observed stars.

The v1.16 advance is the first time **the reconstructed spatial PSF is fitted to source pixels from the *real original dated science exposure*, while masking defects/saturation with the matching `mskimg.fits` detector image**. The investigation still deliberately refrains from asserting a genuine physical Gaia/ZTF source match, calibrated PSF photometry, independent WCS precision or new astrophysical discoveries.

Official data products are documented in [NASA/IPAC IRSA's ZTF metadata](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html). [IRSA data-release documentation](https://irsa.ipac.caltech.edu/data/ZTF/docs/releases/dr06/src/dr06.html) states that science image products are in **digital numbers (DN)**, and explains that the file FITS time tags and light-curve timing conventions must be interpreted carefully; this pilot does not independently check the exact exposure midpoint/topocentric apparent positions. The [ZSDS explanatory supplement section 10.3](https://web.ipac.caltech.edu/staff/fmasci/ztf/ztf_pipelines_deliverables.pdf) specifies **6141** as the mask bits indicating potentially unusable detector pixels, while extracted-source marker bits 1/11 are not bad pixels.

### Fixed original observed data

- The historical original positional-cone IRSA source ZIP (2,212 rows) is rechecked against the original acquisition SHA manifest before use. It is processed only in an ephemeral GitHub Actions runner and is **not** a physically confirmed FT Tau/CIDA 11 photometric time series.
- Four original dated ZTF g-band single exposures are reconstructed uniquely from immutable source/product metadata and the v1.8 SHA-verified reference ledger (two dates for FT Tau, two for CIDA 11).
- Ten exact Gaia DR3 source IDs (two technical targets and eight provisional field reference candidate IDs) use their five-parameter formal correlation/covariance and first-order geometric Earth-geocentric annual parallax at each original science MJD. **CIDA 11's high RUWE ≈8.57** remains a significant single-star astrometry caveat.
- Four original per-exposure full native `psfcat.fits` tables and `sciimgdao.psf` lookup models plus original `sciimgdaopsfcent.fits` center stamps must be successfully opened and checked for consistency. Only the **sixteen** catalogued native source candidates passing v1.14's conservative nearest-source/profile/flags criteria are eligible for fitting original image pixels.

### Image and PSF registration, prior to any fit

Every source cutout is centered on the ICRS coordinates directly read from its own original ZTF per-exposure `psfcat.fits` row. Original `sciimg.fits` and `mskimg.fits` are downloaded separately as **60-arcsec square cutouts** from exactly the same dated ZTF science source filename, changing only the scientific product suffix and keeping center/size fixed.

- Both science and mask FITS must contain exactly one two-dimensional original image, with the **same array shape** and valid celestial WCS. The mapped science-vs-mask celestial pixel grids must agree to within **0.05 detector pixels**, not merely share similar header values.
- The nominal source-centered **4.5-pixel-radius original core** must not contain any nonfinite science pixels or any original detector disqualifying mask bits **6141** (saturated bit 8 included). Those bits are not inferred from flux or source catalog quality.
- Original source `psfcat` native detector `xpos/ypos` fractional pixel phase is compared to the cutout WCS position of that **same native ZTF PSF-fit source**, modulo the integer origin change (native FITS convention vs zero-based NumPy). Any phase mismatch exceeding **0.22 pixel** fails closed. The sixteen actual source checks showed absolute phase differences approximately **0.00007–0.00025 pixel**, a same-pipeline geometry check, not independent sky-coordinate accuracy.
- The full source model is evaluated at the native detector `xpos/ypos` using the original native DAOPhot Gaussian-plus-spatial-correction table, a pixel-integrated analytic Gaussian and cubic B-spline interpolation approximation, with source subpixel phase from the correctly mapped same-date science image. The approximation is **not proven identical to native DAOPhot bicubic reconstruction at off-center positions**.

### Background, pixel fitting and residuals

Define a **14–22-pixel annular sky region** around the original native catalogue source coordinate, excluding masked/nonfinite pixels. Repeated 4-MAD clipping estimates a robust local sky-noise scale, with at least **230 surviving sky pixels**. This is **not** the detector gain/read-noise/Poisson variance model or a photometric error budget.

Within a **9-pixel fit radius**, require an unsaturated, unmasked source core, sufficient clean fit pixels (at least 150) and at most 12% masked fit-radius pixels. Keep original image **DN** data; do **not** convert these to calibrated magnitude or flux physical units.

Fit only four linear coefficients using NumPy least squares:
[
I(x,y)=A,P(x,y)+b_0+b_x x+b_y y+arepsilon(x,y),
]
where (P) is a **fixed** already reconstructed unit-sum spatial PSF shape, (A) is an uncalibrated amplitude in image DN, (b_0) is a local sky intercept and (b_x,b_y) are sky-plane gradients. A large ill-conditioned linear fit or nonpositive amplitude is rejected. **No centroid position or PSF shape is optimized; no second star is fitted or subtracted; this is not deblending.**

The linear coefficients are fitted on one checkerboard partition of usable image pixels and residuals are measured on the other parity's excluded pixels. The holdout set is a **different set of detector pixels but is part of the exact same star, observation, telescope, native pipeline and background field**; it is *not an independent astronomical source, epoch or independent PSF calibration*.

Define diagnostic ratios (not confidence intervals):
[
R_{m RMS}=rac{sqrt{mathrm{mean}(I-widehat I)^2},_{m same-image heldout}}{sigma_{m annulus,MAD}},qquad
R_{m peak}=rac{max(I-widehat I),_{m same-image heldout}}{sigma_{m annulus,MAD}}.
]
The **engineering-only** provisional residual profile screen requires (R_{m RMS}leq 3), (R_{m peak}leq 7), positive PSF amplitude and the original science/mask/geometry/PSF model checks. These are **not survey-calibrated formal-significance thresholds**, false-detection probabilities, independently verified source quality, calibrated photometry or WCS accuracy.

### Actual observed-data results

[The original masked ZTF image workflow](https://github.com/ismaelberja/stellarforge/actions/runs/42518746629) completed **614 automated tests**, four native DAOPhot center-FITS checks and **all sixteen exact eligible original source image/mask fits**, with no HTTP 503 in this run:

- **Three** actual technical target fits and **thirteen** reference-candidate original source fits completed, each with WCS-aligned science/mask images and zero disqualifying flags in the central source aperture.
- **Thirteen** same-source checkerboard residual profiles passed the provisional engineering screen.
- **Three** had peaks exceeding the predefined **7× annular sky-MAD proxy**, requiring review: FT Tau target at MJD58491.184780, CIDA 11 target at MJD58849.135984, and a CIDA 11 field reference candidate at MJD58849.135984.
- The median same-image held-out pixel-RMS/annular noise proxy was **1.1015**. The geometry phase differences were below 0.0003 image pixel, but these are not absolute external WCS precision measurements.
- No independent stellar PSF-star validation or physical binary/companion/variability determination has been achieved, despite the availability of genuine original detector data.

Full source-by-source counts and numerical review cases are in [the real v1.16 report](../reports/masked_spatial_psf_v1.16/REAL_ZTF_PIXEL_RESIDUALS_EVIDENCE.md).

## Essential integrity constraints

1. A 7–12× positive residual relative to a robust annular sky noise proxy is **not automatically a source companion**; it may be detector PSF interpolation mismatch, background nebulosity, low-level bad/correlated noise, native PSFcat centroid/model error, or a neighboring/unresolved contaminant. No astrophysical classification is made.
2. The source position comes from the ZTF native source fit catalogue and the model comes from that same ZTF pipeline; the small pixel-phase difference and low residuals are **internally self-consistent** but not independent Gaia–ZTF cross-identification or absolute WCS calibration.
3. All sources remained previously selected conditional on Gaia proximity, PSF native `chi/sharp/SNR/flags`, position and low crowding; the fraction 13/16 is a **diagnostic fraction among pre-selected candidates**, not a physically complete success rate, survey efficiency or binary incidence.
4. The Gaia formal 5D model and annual geocentric parallax do not include instrument PSF/WCS correlations, true Palomar topocentric apparent positions, color corrections, high RUWE non-single-star motion or ZTF original image time-scale uncertainty.
5. The code never publishes original ZTF `sciimg.fits`/ `mskimg.fits` pixels, original Gaia TAP CSV, original ZTF PSF catalog rows or DAOPhot coefficient arrays. Only verified small derived counts, source labels, quality metrics and SHA-256 hashes are uploaded in GitHub Actions.

## Reproduce and next science gate

```bash
python -m pip install -e '.[test,analysis,images]'
python -m pytest -q
python scripts/run_v116_original_masked_psf_residuals.py /path/to/original_SHA_verified_IRSA_acquisition.zip \
  --gaia-timeout 25 --archive-timeout 6 --require-some-real-pixel-fits
```

**Next phase:** build a **spatially representative and independently authenticated field-star control set**, including multiple holdout stars *not involved in selection or fitting*, original source crowding/neighbor information, and more than four historical exposure epochs and bands. Quantify the real image PSF residual distribution and false-association rate using independent sky-coordinate/PSF calibrations, topocentric/time/color corrections and physical CCD variance models. Separately review the three flagged peaks with additional real independent epochs and sources, without any companion claim.

**Remaining scientific confirmations: zero genuine Gaia–ZTF source identities authenticated; zero independent calibrated local stellar PSFs; zero independent absolute WCS uncertainty models; zero confirmed companions, physical events or variability.**
