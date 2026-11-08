# StellarForge v1.14 — Original ZTF native PSF catalogue and DAOPhot spatial-model source evidence

**Observed 8 November 2026 · [Actual live original ZTF/Gaia FITS catalogue and DAOPhot run](https://github.com/ismaelberja/stellarforge/actions/runs/42513198605)**

**Scientific interpretation:** this milestone directly screens *original per-exposure ZTF PSF-fit catalogue detections* against Gaia-predicted candidate coordinates. It does **not** independently authenticate a Gaia–ZTF physical source association or local empirical PSF, calibrate the ZTF detector WCS, or discover a new companion/variability event. Native spatial DAOPhot PSF files were retrieved but are not yet decoded/evaluated at source coordinates.

## Real-data provenance and public archive products

- The same original SHA-checked IRSA/ZTF 2,212-row positional-query acquisition for FT Tau/CIDA 11 was verified against its original archive manifest and the immutable v1.8 reduced reference-offset ledger (source SHA-256 `fb7d5c315cbef56b2551e73920c67920827d91160b4c0bd35f3fd77113166beb`).
- **Four original, distinct dated ZTF single-science-exposure files** were reused: two g-band dates in each target field, from the historic exact ZTF `filefracday/field/filter/CCD/quadrant` identifiers. These are **four original astrophysical exposure epochs** and are not newly observed images.
- Full native `psfcat.fits` PSF-fit source catalogues were retrieved **for all four** original science exposure products, following the official IRSA ZTF [filename pattern](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html). No image-style cutout parameters were attached to full PSF catalogue URLs.
- Exact ten-source Gaia DR3 five-parameter **formal** astrometric solutions (two targets and eight originally selected reference candidates) were propagated individually at each science MJD with first-order Earth-geocentric geometric annual parallax; this does not include full telescope apparent-place corrections nor non-single-star systematics.
- Four native `sciimgdao.psf` **spatially varying DAOPhot lookup-table products** were retrieved, one per original science exposure. Their byte hashes and sizes are recorded. These files are not yet interpreted or evaluated at any specific native detector position.
- Original FITS table rows, DAOPhot PSF coefficients, raw Gaia TAP CSV and IRSA photometric measurements remain in memory on the ephemeral workflow runner and **were not committed or published**. Public outputs are derived bounded quality/candidate summaries only.

The [ZTF Science Data System explanatory supplement, §10.6](https://irsa.ipac.caltech.edu/data/ZTF/docs/ztf_explanatory_supplement.pdf) defines the native PSF-fit column names and their scientific interpretation. See the [methodology and hard scientific limitations](../../docs/PHASE114_NATIVE_PSF_CATALOGUE_AND_SPATIAL_MODEL_GATE.md).

## Verified live findings

The workflow [ran successfully](https://github.com/ismaelberja/stellarforge/actions/runs/42513198605), including **564 automated tests passed**, and downloaded all **four full official native `psfcat.fits` FITS binary source tables** plus all **four companion `sciimgdao.psf` files**, with zero HTTP 503 in these eight bounded product requests.

| Technical field | Original science MJD (assumed UTC) | Native PSF-fit catalog rows | Gaia positions screened | Candidate profiles passed | DAOPhot spatial file |
|---|---:|---:|---:|---:|---|
| FT Tau | 58388.389016 | **3,970** | 4 | **2** (target + 1 reference) | Retrieved; format not decoded |
| FT Tau | 58491.184780 | **5,569** | 4 | **4** (target + 3 references) | Retrieved; format not decoded |
| CIDA 11 | 58475.113750 | **5,313** | 6 | **5** (five references; target profile under review) | Retrieved; format not decoded |
| CIDA 11 | 58849.135984 | **12,355** | 6 | **5** (target + 4 references) | Retrieved; format not decoded |
| **Total** | Four real epochs | **27,207** native catalogue rows | **20** Gaia positions across exposures | **16** provisional candidates | **4/4 retrieved** |

The four spatial DAOPhot products are each **88,465 bytes** in this dataset. Their common byte length is not proof that the actual spatial PSF models are identical, and the present pipeline does not decode them or compare their coefficients.

### Classification of the 20 target/reference predictions

- **16/20 provisional unique native catalogue candidates** within 1″ of the predicted Gaia location and passing the chosen PSF-fit profile, SNR, and pixel-flag screens.
- **Three candidates** have native `chi` below the chosen conservative lower threshold of **0.5** (approximately 0.349, 0.460, and 0.384 respectively). These are **quality review flags**, not proof of a bad/starless image, binary, or astrophysical contamination.
- **One FT Tau reference** in the earliest studied exposure had no nearby native PSF-fit catalog entry within the chosen 1″ acceptance radius (indeed no source within the 5″ local survey used by this screen). This is a catalogue-detection limitation, **not a physical non-detection**.
- Across these nearest detected native catalogue candidates, published `flags=0` and no *additional catalogued native PSF source* within 3″ were observed. **Neither fact excludes sub-resolution blends, missing catalogue sources, bright-star PSF wings or an incorrect Gaia–ZTF association.**
- The **16 provisionally screened separations** run from **0.032641″ to 0.345256″**, with a **median 0.1258465″**. These are *offsets between two catalogue position estimators under a provisional matching hypothesis*, **not** validated absolute instrumental astrometric accuracy or proper motion.

**Target-specific caution:** the 2 original FT Tau target dates and 1 of 2 CIDA 11 target dates pass the provisional native PSF source candidate/profile filters. The earlier CIDA 11 target is in its exposure's PSF-fit catalog, with nominal separation **0.230183″** and native `chi≈0.460`, but falls below the engineering profile-quality threshold; it **must remain review-required, not treated as a confirmed match or physical non-detection**. Gaia DR3 RUWE for CIDA 11 ≈8.57 remains a serious non-single-star astrometric model caveat.

## Method and non-independence

The original ZTF native PSF catalogue is generated by ZTF's instrumental pipeline, while Gaia DR3 positions come from a separate astrometric catalog. This adds a distinct **catalogue-level positional and PSF-quality cross-check**, but there may be shared underlying astrometric reference/calibration inputs, correlated PSF/extraction and selection effects. Therefore, this screen is not an independently validated physical source association.

A candidate must fall within **1.0″** of the source-specific Gaia-propagated position and satisfy **0.5 ≤ chi ≤ 1.5**, **−0.5 ≤ sharp ≤ 0.5**, PSF-fit **SNR ≥5**, positive flux and positive fitted flux uncertainty, and **zero intersection with the ZTF 6141 disqualifying mask bits**. A second ZTF PSF-fit source within **3″** triggers crowding review; assigning one per-exposure `sourceid` to two Gaia IDs is explicitly prohibited.

These are **engineering thresholds for conservative screening, not ZTF-certified astrophysical counterpart probabilities, a completeness estimate or a 1σ WCS error**.

The exact per-exposure `psfcat` `sourceid` is a sequential extraction counter, **not a Gaia source identifier or a stable ZTF multi-epoch OID**. The `xpos/ypos` fields are in the original native CCD-quadrant coordinate system, while the `ra/dec` fields are the source catalog's reported sky-coordinate solution. No independent WCS/distortion fit or detector-coordinate residual validation has been carried out on withheld field stars.

The ZTF `sciimgdao.psf` is a **spatially varying DAOPhot lookup-table file**, *not* a FITS image of the local PSF. Downloading and hashing the file does not suffice to evaluate its PSF at the original source native detector coordinates. This real remaining scientific gate is intentionally left open.

## Connection to previous real-image phases

- v1.12 compared two independent-code centroid methods on *the same original science FITS pixels*, observing method-dependent offsets and intermittent archive HTTP 503. v1.14 adds **actual original ZTF per-exposure PSF-fit catalogues**, not additional independent telescope images.
- v1.13 checked genuine original **pixel bitmask** `mskimg.fits` cutouts for four available reference-source stamps. Those checks were too sparse for all targets; native PSF catalogue `flags` are useful but do **not replace** per-source original mask and science-pixel WCS alignment.
- This phase successfully acquired all eight native per-exposure PSF auxiliary products without HTTP 503, but that does **not** retroactively validate unavailable `sciimg.fits` or `mskimg.fits` cutouts on the target source centers.
- The positional IRSA photometric cone queries of the historical project remain unconfirmed as FT Tau/CIDA 11 physical light curves; a PSF catalog detection near a Gaia coordinate is positive *screening evidence*, not independent proof of physical identity.

## Reproducibility and next scientific gate

Source implementations: [v1.14 source-candidate PSF code](../../src/stellarforge/v114_native_psfcat_association.py), [verified live survey runner](../../scripts/run_v114_native_psfcat_gaia.py), [synthetic adversarial regression suite](../../tests/test_v114_native_psfcat_association.py), and [manual-only-after-pilot GitHub Actions](../../.github/workflows/v114-original-psfcat.yml).

```bash
python -m pip install -e '.[test,analysis,images]'
python -m pytest -q
python scripts/run_v114_native_psfcat_gaia.py /path/to/original_SHA_verified_IRSA_artifact.zip \
  --gaia-timeout 25 --archive-timeout 12 --require-some-native-products
```

To proceed to **an actual spatially evaluated PSF** at a Gaia reference/target location, validate and decode the original DAOPhot lookup-table spatial format, evaluate on the original native CCD-quadrant `xpos/ypos` coordinate system, cross-check against original `sciimg.fits` and `mskimg.fits` detector pixels and source-neighbor residuals, and estimate instrumental error against separate held-out stars. Source physical identity requires independent evidence and a realistic false-match model.

**Scientific claims still at zero:** authenticated Gaia–ZTF physical source associations; validated local spatial PSFs; independently calibrated detector WCS error budgets; discovered companions; confirmed physical source-variability events.
