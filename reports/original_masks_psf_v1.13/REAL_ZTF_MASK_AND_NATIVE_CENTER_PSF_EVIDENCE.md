# StellarForge v1.13 — Real ZTF detector masks and native field-center PSF evidence

**Observed 8 November 2026: two successful read-only runs on the same four original ZTF exposures — [initial run A](https://github.com/ismaelberja/stellarforge/actions/runs/42467665500) and [repeat run B](https://github.com/ismaelberja/stellarforge/actions/runs/42468217065).**

**Scientific interpretation:** genuine original ZTF instrument files were obtained, opened and compared against matching science exposures. This is **pixel-level mask validation and native field-center PSF availability/shape screening**. It is **NOT an independent WCS uncertainty calibration, a local empirical point-spread function for a source, a verified astrophysical Gaia–ZTF crossmatch, or a new companion/variability detection**.

## Source and implementation provenance

- The same SHA-verified official IRSA/ZTF positional-query acquisition for FT Tau and CIDA 11 was recovered privately into an ephemeral runner, with **2,212 original ZTF light-curve position-query rows** checked against their original manifest. These photometric rows are not authenticated source identities.
- The source list is fixed to **ten exact Gaia DR3 IDs** (two technical targets, eight prior Gaia catalogue-backed field reference candidates) and exactly **four original dated ZTF g-band science exposures** from the immutable v1.8 derived source record (original aggregate SHA-256 `fb7d5c315cbef56b2551e73920c67920827d91160b4c0bd35f3fd77113166beb`).
- Each predicted Gaia position includes its source-specific full formal 5×5 Gaia covariance and first-order geocentric annual parallax. This is not a full topocentric apparent sky-coordinate model, nor an independent Gaia–ZTF match.
- For each of the **20 preregistered target/reference positions**, an official matching `mskimg.fits` cutout was requested; the matching `sciimg.fits` was obtained for the same dated product and sky center only if the mask fetch succeeded. Four official `sciimgdaopsfcent.fits` native field-center PSF stamps were also requested, one per original dated exposure.
- The [ZTF explanatory supplement](https://irsa.ipac.caltech.edu/data/ZTF/docs/ztf_explanatory_supplement.pdf) defines the disqualifying mask-bit template **6141** and the extracted-source information bits **2050**; `2^8 = 256` flags saturation. The [IRSA metadata guide](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html) specifies both ancillary product names and full paths.
- The real-data workflow passed **533 tests** and committed/exported only derived diagnostics and SHA-256 digests. No original FITS pixels, instrument mask arrays or raw Gaia TAP/IRSA photometric source tables were made public.

## Two-run source availability and full native-PSF inventory

The bounded workflow was **repeated once against exactly the same four original science exposure identifiers and ten Gaia IDs**; these are archive rerequests, **not eight independent observing epochs** or new astrophysical measurements.

| Verified original-product result | Run A | Run B | Unique successfully inspected over both runs |
|---|---:|---:|---:|
| Reference/target mask-science pairs attempted | 20 | 20 | 20 distinct source positions |
| WCS-aligned science+mask pairs accessible | **4** | **0** | **4** distinct Gaia reference-position cutouts |
| Mask/science HTTP 503 | 16 | **20** | Archive access failures, not sources absent |
| Target cores with a verifiable mask | 0 | 0 | **0** |
| Field-center original native PSF stamp files requested | 4 | 4 | 4 original science exposures |
| Original PSF stamps actually parsed | **2** | **2** | **4 unique native center-PSF products** |

**All four original `sciimgdaopsfcent.fits` PSF stamps were individually retrieved across the two runs**, because the two successful PSF downloads in run B were exactly the two products that returned HTTP 503 in run A. Every parsed stamp is **23 × 23 pixels**, with a fully finite image.

| Original dated field | Science MJD | Retrieved in | Positive-weighted native center PSF σx (pixels) | σy (pixels) |
|---|---:|---|---:|---:|
| FT Tau | 58388.389016 | A | 1.3705 | 1.3372 |
| FT Tau | 58491.184780 | B | 1.7788 | 1.8782 |
| CIDA 11 | 58475.113750 | B | 1.6202 | 1.4829 |
| CIDA 11 | 58849.135984 | A | 1.4397 | 1.2984 |

This is **complete file-access coverage of the four original native field-center PSF products**, but it does **not** mean the source-location PSFs have been evaluated or calibrated. The original detector-center stamps are different *dated science products*; there is no repeated successful download of the same PSF product in both runs for a byte-for-byte PSF repeatability comparison. Likewise, no original mask cutout was retrieved in both runs, so the **four mask-science successes from run A have not been independently repeated** at the pixel-byte level.

Run B's complete absence of accessible mask/science pairs is an **archive HTTP 503 service limitation**. Do not erase the four properly measured run A mask checks, and do not count 40 HTTP requests as forty new source observations. Both runs passed the entire **533-test regression suite**.

## Initial run A — exact verified findings

| Measure | Actual result |
|---|---:|
| Original ZTF positional-cone records verified | **2,212** |
| Independent original dated science exposure products | **4** |
| Predicted target/reference source-mask pair checks | **20** |
| Successful mask/science FITS with identical array dimensions and aligned celestial WCS | **4** |
| Aligned source apertures with zero ZTF disqualifying bits (6141) | **4** |
| Original target-star cores successfully mask-screened | **0** |
| Original source mask/science access HTTP 503 | **16** |
| Native center-PSF `sciimgdaopsfcent.fits` stamps requested | **4** |
| Native field-center PSF FITS parsed | **2** |
| Native PSF transport HTTP 503 | **2** |
| Regression tests passed | **533** |

**Every accessible mask belongs to a Gaia reference candidate, not to FT Tau or CIDA 11 themselves.** All four target-center mask/science requests had HTTP 503 and therefore cannot be judged clean, bad, saturated or blended from this pilot. Of the four reference-star apertures where the mask and science FITS were both accessible, each had zero disqualifying ZTF 6141 mask flags and zero bit-8 saturation flags in its nominal 4.5-pixel aperture. **This is a limited archival bad-pixel quality result only, not a clean isolated-star declaration.**

### Mask grid/sample evidence

All four successful mask+science pairs matched exactly at the sampled celestial WCS grid locations (**maximum measured grid mapping discrepancy 0 pixels**). Their nominal Gaia-predicted 4.5-pixel-radius apertures contained 62–67 pixels, zero disqualifying bits and zero bit-8 saturation flags. The surrounding annuli also had zero disqualifying bits in those four cutouts.

| Field | Original science MJD (UTC assumed) | Gaia reference mask-screened ID | Bad core pixels | Saturated core pixels |
|---|---:|---|---:|---:|
| FT Tau | 58388.389016 | 149623505110996992 | 0 | 0 |
| FT Tau | 58491.184780 | 149623505110996992 | 0 | 0 |
| FT Tau | 58491.184780 | 149625115720662528 | 0 | 0 |
| CIDA 11 | 58475.113750 | 3419111520318480128 | 0 | 0 |

**None of these four bits/shape checks validates a stellar point-spread function or the source's Gaia–ZTF physical identity.** The ZTF source marker bits 1/11 do not imply a bad detector pixel, but neither do they confirm that an apparent peak is the desired astrophysical object.

### Actual archived native center PSF stamps

In initial run A, two genuine original `sciimgdaopsfcent.fits` field-center stamps were accessible and two were HTTP 503. **The two missing ones were subsequently opened in repeat run B**; the four-product combined inventory is listed above.

| Original field | MJD | Native PSF FITS dimensions | Positive-weight second moment σx (pixels) | σy (pixels) |
|---|---:|---:|---:|---:|
| FT Tau | 58388.389016 | **23 × 23** | 1.3705 | 1.3372 |
| CIDA 11 | 58849.135984 | **23 × 23** | 1.4397 | 1.2984 |

These are simple descriptive positive-weighted **second moments of the archived science-field-center PSF stamps**. They are not fitted, source-location-dependent instrument PSFs, FWHMs, seeing at each reference source, independent sky-position errors, or a validation of optical aberration, blending, calibrated PSF photometry or spatial PSF distortion.

## Important data-quality interpretation

- **16 of 20** nominal mask/science source cutout checks failed with **HTTP 503**. Failure to retrieve an original file from IRSA is a **remote service/transport limitation**, not scientific evidence for an empty field or absent star.
- The PSF field-center stamp does **not** give the native PSF at the arbitrary target/reference positions. The official spatially varying `sciimgdao.psf` would need to be evaluated at the correct detector source position, and `psfcat.fits` could support additional verification.
- Mask bit definitions in the original ZSDS document concern detector artifacts and extracted-source markers. Their absence cannot rule out sub-PSF blending, unresolved binaries, photometric contamination, background nebulosity, colour dependence or incorrect Gaia–ZTF physical identity.
- Gaia formal five-parameter astrometric covariance does not capture instrumental ZTF WCS/PSF errors, nor necessarily the real physical position of **high-RUWE CIDA 11 (RUWE ≈ 8.57)**.
- The positional screen uses Earth-geocentric geometric annual parallax and an assumed UTC observation MJD, not exact observatory topocentric apparent position/timestamp validation.
- Only two original g-band dates per technical field were audited; no claim is made about the other ZTF OID/filter groups, the broader Taurus sample, or a new physical companion/variability event.

## Reproduction and further scientific gates

The bounded official-source workflow is [`.github/workflows/v113-official-mask-psf.yml`](../../.github/workflows/v113-official-mask-psf.yml) and uses [`scripts/run_v113_masks_native_psf.py`](../../scripts/run_v113_masks_native_psf.py) with pixel-level scientific checks implemented in [`src/stellarforge/v113_official_masks_psf.py`](../../src/stellarforge/v113_official_masks_psf.py).

Run only with the original SHA-verified IRSA acquisition ZIP in a temporary environment:

```bash
python -m pip install -e '.[test,analysis,images]'
python -m pytest -q
python scripts/run_v113_masks_native_psf.py /path/to/verified_original_IRSA_acquisition.zip \
  --image-timeout 6 --gaia-timeout 25 --require-some-instrument-products
```

Next, examine official `sciimgdao.psf` (the **spatially varying DAOPhot PSF**) and original `psfcat.fits` detections with positional cross-matching, validating true source morphology and color and independently held-out field-star astrometric errors. This is required before declaring a calibrated PSF, WCS source association, new binary companion or stellar variability detection.

**Scientific confirmation counts (both runs): 0 independently calibrated detector WCS; 0 localized empirical reference PSFs; 0 independently authenticated astrophysical Gaia–ZTF matches; 0 new physical companions/variability events.**
