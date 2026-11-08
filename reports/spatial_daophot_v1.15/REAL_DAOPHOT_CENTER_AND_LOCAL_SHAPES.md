# StellarForge v1.15 — Real original ZTF spatial DAOPhot PSF reconstruction and official center-stamp validation

**Observed-data verification: 8 November 2026.** [Successful ZTF/Gaia original-data run, 590 tests](https://github.com/ismaelberja/stellarforge/actions/runs/42514987086).

## What is actually accomplished

For the first time in StellarForge, all **four original** `sciimgdao.psf` spatially varying DAOPhot point-spread-function (PSF) lookup files of the historic FT Tau and CIDA 11 technical pilot have been **decoded into analytic parameters and lookup correction arrays**, then evaluated at the native `xpos/ypos` detector coordinates of **16 original ZTF PSF-catalogue candidate sources**.

All four native model reconstructions were **separately compared** at their respective native science-field centers against real original, same-exposure `sciimgdaopsfcent.fits` FITS images from NASA/IPAC IRSA. They show extremely close agreement **within the shared original ZTF DAOPhot processing model**. This is a **reconstruction algorithm consistency check**, **not** independent validation of the physical local stellar PSF or a calibrated astrometric detector error model.

No original `sciimg.fits` science pixels were newly refitted, and no complete original `mskimg.fits` pixel-mask/PSF residual test was performed in this phase. **No physical Gaia–ZTF source association, instrumental WCS calibration, companion, or physical variability event is confirmed.**

## Original data provenance

- Original IRSA positional-cone pilot: **2,212** raw position-query rows checked against the original acquisition manifest and hashes. Positional queries are **not** proof of physical association with FT Tau or CIDA 11.
- Original Gaia candidates: **two technical targets + eight reference-star IDs** from Gaia DR3. Their exact five-parameter formal correlated astrometry and first-order geocentric annual geometric parallax are propagated to the dated science epochs.
- Historical science dates: **four distinct original ZTF g-band science exposures** (two per target field), matched by exact original ZTF OID, band, MJD and source product date/field/CCD/quadrant.
- The four `psfcat.fits` native per-exposure source catalogues were parsed to select up to **16 provisionally well-behaved nearest candidate** detections based on the v1.14 conservative criteria (≤1″ Gaia-to-native catalog separation, `chi/sharp/SNR/flags` quality, unique source IDs). Three other profiles required review and one original reference lacked a native source-catalog match in the screening radius.
- The four original `sciimgdao.psf` ASCII/native DAOPhot files, **each 88,465 bytes**, were fetched anew via official IRSA URLs, decoded transiently in runner memory and represented publicly only as bounded structural summaries, model moment diagnostics and SHA-256 hashes.
- Four original **23×23** `sciimgdaopsfcent.fits` field-center PSF FITS stamps were also successfully fetched and parsed. **No HTTP 503** occurred for those products in this successful pilot.
- The [full public ZTF source documentation](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html) distinguishes the DAOPhot lookup format from the center FITS PSF stamp. [Masci et al. (2019)](https://doi.org/10.1088/1538-3873/aae8ac) describes a spatially varying PSF model with a Gaussian analytic component plus correction lookup tables.

## Verified real native DAOPhot structure

All four authentic files have a `GAUSSIAN` analytic core and **three 47×47 sampled correction lookup tables** (a constant term and linear spatial corrections). Each spatial PSF is evaluated on a **23×23 image-pixel** output footprint, corresponding to a half-pixel lookup grid. The native science-field center is **(1535.5, 1539.5) original detector pixels** in each model.

The implementation integrates the Gaussian over the pixel footprint, applies spatially weighted lookup-table residual corrections with a cubic interpolation **approximation** (SciPy's cubic B-spline, which is not claimed identical to DAOPhot's original bicubic routine), clips physically negative model fluxes, and normalizes each reconstructed stamp to unit positive flux. Native ZTF `psfcat.fits` `xpos/ypos` are on the **full CCD-quadrant coordinate system**, not local sky-centered cutout pixels.

The software explicitly rejects unknown analytic kernels, malformed or truncated ASCII headers, incompatible 47-grid coefficient counts, nonfinite coefficients, invalid spatial coordinates, malformed FITS stamps and centre shape disagreement rather than synthesizing an apparently valid model.

## Real result: original center FITS comparison

The comparison is a **pixel-by-pixel normalized PSF shape reconstruction check** at the same science-field center. Both products originated from the **same ZTF instrumental pipeline**, so numerical agreement cannot be interpreted as a test on independent observations.

| Technical field | Science MJD (UTC assumed) | Native model tables | Official FITS center shape | Cosine similarity | Normalized L1 difference | Local provisional PSFs evaluated |
|---|---:|---|---|---:|---:|---:|
| FT Tau | 58388.389016 | 3 × 47 × 47 | 23 × 23 | **0.999999** | **0.000984** | 2 |
| FT Tau | 58491.184780 | 3 × 47 × 47 | 23 × 23 | **1.000000** | **0.000278** | 4 |
| CIDA 11 | 58475.113750 | 3 × 47 × 47 | 23 × 23 | **1.000000** | **0.000303** | 5 |
| CIDA 11 | 58849.135984 | 3 × 47 × 47 | 23 × 23 | **1.000000** | **0.000355** | 5 |
| **Total** | Four original exposures | **4/4 authentic models parsed** | **4/4 authentic center FITS matched** | All pass center-shape threshold | All very small | **16** |

The reported cosine similarity is a unitless normalized dot-product shape comparison; the L1 is the sum of absolute differences in images each normalized to unit positive flux. The center FITS check passed an engineering rule of cosine ≥0.93 and normalized L1 ≤0.50; these are **not ZTF-certified error bars**, nor a test of absolute astrometry or photometric flux calibration. All four checks are positive by much larger margins than that lenient criterion.

### Real source-position approximate PSF shapes

All sixteen v1.14 provisional `psfcat.fits` candidate positions supported **a 23×23 approximate local spatial PSF model** using their original `xpos/ypos` detector coordinates. The model's descriptive second-moment shape variations among these candidates are:

| Original science epoch | Provisional candidate PSFs evaluated | Range of σx (native image pixels) | Range of σy (native image pixels) |
|---|---:|---:|---:|
| FT Tau 58388.389016 | 2 | 1.4090–1.4143 | 1.3796–1.3841 |
| FT Tau 58491.184780 | 4 | 1.7770–1.7784 | 1.8808–1.8817 |
| CIDA 11 58475.113750 | 5 | 1.7075–1.7515 | 1.5681–1.6150 |
| CIDA 11 58849.135984 | 5 | 1.4568–1.4620 | 1.3099–1.3136 |

These are **descriptive second central moments of reconstructed PSF model stamps**, not directly observed local image-PSF measurements or calibrated seeing FWHMs. Changes between historical exposures may reflect true instrument/seeing/PSF modelling, but this exercise **cannot attribute them to any single physical cause**, particularly given unverified matching identities and uncertainty models.

## Scientific safeguards, interpretation and limitations

1. **Original DAOPhot interpolation is not bit-for-bit validated off center.** The cubic B-spline used for lookup correction interpolation has excellent four-field center agreement, but a spatially varying model must also be compared with the actual source-position original ZTF science pixels and verified instrument masks before declaring local PSF accuracy.
2. **Agreement is within the same pipeline.** A ZTF native center PSF FITS stamp was generated from the same underlying DAOPhot model, so 0.999999–1.000000 similarity primarily validates **our interpretation of the file and center reconstruction**, not the telescope optics or isolated star observations.
3. **Local reconstructed PSF ≠ authenticated star.** The sixteen candidate positions are nearest ZTF native PSF catalogue detections close to Gaia DR3 predictions under conservative profile screening. They are **not** independently authenticated Gaia–ZTF physical associations, guaranteed single stars, detected companions or time-domain variability events.
4. **Insufficient original detector-mask validation.** In v1.13 only four candidate reference-core masks could be checked against original science pixels and no technical target-core mask was accessible; v1.15 does **not** fix that incomplete mask/seeing/saturation/blending coverage.
5. **No calibrated WCS error budget.** The v1.15 shape model does not fit detector coordinates to Gaia positions using independent spatially distributed holdout stars, telescope time systems, parallax/topocentric corrections, chromatic refraction or PSF-source centroid residuals.
6. **CIDA 11 astrophysical caution.** Gaia DR3 RUWE ≈8.57 is much too high for assuming clean single-star astrometric modeling; it does not on its own prove a companion and cannot be repaired by reconstructing a ZTF model PSF.
7. **Reproducibility and data publication.** Original raw DAOPhot coefficient tables, the 23×23 FITS PSF pixel matrices, original ZTF source FITS rows, Gaia DR3 TAP CSV and original ZTF photometric measurements remain outside public Git and workflow artifacts. Only source identifiers, original hashes, modeled scalar shape summaries and quality statuses are public.

## Software and evidence

[Source parser and spatial PSF evaluator](../../src/stellarforge/v115_spatial_psf.py) · [actual observed-data script](../../scripts/run_v115_spatial_psf_original.py) · [unit and adversarial FITS/DAOPhot tests](../../tests/test_v115_spatial_psf.py) · [official live GitHub Actions run](https://github.com/ismaelberja/stellarforge/actions/runs/42514987086).

The real original-data workflow passed **590 automated tests**, then retrieved all four DAOPhot source files, four native PSF catalogues, and four center PSF FITS stamps, emitting an aggregate-only ZIP artifact.

## Next independently verifiable gate

Return to each original `sciimg.fits` image and matching detector `mskimg.fits` pixel flags, align them at the original full CCD source coordinates, evaluate the spatial DAOPhot model at the pixel subphase, and fit source intensity/background *at genuine independently vetted stars*. Compare **masked image residuals and held-out independent detector WCS/PSF errors**, with source crowding, signal, atmosphere, source identification and high CIDA 11 RUWE treated explicitly. At that stage, quantify the PSF model's physical measurement errors and potential false associations; **not before**.

**Open scientific gates: zero independently validated source-local empirical PSFs against real masked star images; zero held-out calibrated WCS error models; zero confirmed physical Gaia–ZTF matches; zero discovered companions or confirmed physical stellar variability.**
