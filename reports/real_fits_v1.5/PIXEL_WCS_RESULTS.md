# StellarForge v1.5 — Real ZTF FITS pixel and celestial WCS audit

**Execution:** [GitHub Actions v1.5 real-image run, 2026-11-05](https://github.com/ismaelberja/stellarforge/actions/runs/42029766535).  
**Scientific interpretation:** provisional image-screening result, **not a Gaia/ZTF astrophysical source crossmatch**.

## Genuine image processing result

Starting from **2,212 SHA-checked official ZTF cone-query photometric rows**, we independently selected representative science exposures (median/early/late epochs) and one reference-coadd fallback for each of six OID/passband groups. Real FITS *pixel arrays*, not merely the first 80 header bytes, were read **in memory**; each accepted image had a usable celestial WCS and a valid predicted Gaia target pixel position.

| Cone target | ZTF OID | Band | Image actually read | Central local maximum offset from WCS-propagated Gaia position | Additional above-threshold local maxima within 12″ |
|---|---|---|---|---:|---:|
| FT Tau | 1605115300003377 | g | science | 0.123″ | 0 |
| FT Tau | 1605215300005161 | r | **reference coadd** (three science-image requests failed) | 0.499″ | 0 |
| FT Tau | 609108400001155 | g | **reference coadd** (three science-image requests failed) | 0.337″ | 0 |
| FT Tau | 609208400001969 | r | science (third attempted exposure) | 0.402″ | 0 |
| CIDA 11 | 610106300008010 | g | **NO IMAGE AVAILABLE TO THE PIPELINE** (three science + reference all HTTP 503) | n/a | n/a |
| CIDA 11 | 610206300011997 | r | science | 0.403″ | 0 |

**5 of 6** OID/band groups therefore yielded a real FITS pixel/WCS screen: **3 individual science exposures and 2 reference coadds**. The pixel plate scales measured from WCS are ~1.00–1.013 arcsec/pixel. All five accepted cutouts show a Gaussian-smoothed intensity maximum within 0.5 arcsec of the predicted coordinate.

**Critical interpretation:** this is compatible with a source near the expected Gaia position. The source location was used to request the cutout, and the observed maximum may reflect an unresolved composite PSF. A high-threshold peak screen finding **zero additional maxima is not evidence that the source is single or uncontaminated**.

### What each numeric value actually means

- The image peak is the nearest **above-threshold local maximum** after Gaussian smoothing, **not** a PSF-fitted centroid or independent astrometric recalibration.
- The 0.123–0.499 arcsec offsets are from *pixel coordinates computed using the FITS header WCS* to the local maximum; they are **not** the v1.3 photometric-row positional residuals and must not be confused with them.
- Threshold: 5 × a robust MAD-based background-noise proxy; it can miss companions blended with the central point spread function or faint sources, and false maxima can arise from artifacts.
- Reference coadds blend multiple dates and can have different PSFs/astrometric systematics from the individual ZTF science exposures; **their coordinates cannot validate a single science epoch**.
- The Gaia position propagation uses **2D proper motion**, without full parallax, perspective or covariance treatment.
- The CIDA 11 g image returned HTTP 503 in all four bounded requests; this is **an archive-access limitation**, not a non-detection or an astrophysical statement.

## Integrity, security and reproducibility

- Upstream original raw light-curve byte hashes, official IRSA cone-query URL and Gaia technical seed were rechecked by v1.3 logic.
- Remote image URLs were restricted to the official IRSA ZTF science/reference archive with 45-arcsec cutouts.
- No more than 3 MB were read per candidate FITS. Headers, finite coverage, 2D shape and celestial WCS were required before image screening.
- Individual FITS images were never written to the public Git repository or uploaded as CI artifacts. The [short-lived, aggregate-only GitHub Actions artifact](https://github.com/ismaelberja/stellarforge/actions/runs/42029766535) includes WCS/peak summaries and FITS SHA-256 checksums, not image pixels.
- **373/373 software tests** passed during the live v1.5 run (all synthetic/mocked with respect to image validation). The observational image run is an additional network-dependent check.

### Reproduce with permitted inputs

```bash
python -m pip install -e '.[test,analysis,images]'
python -m pytest -q
python scripts/run_v15_image_pixels.py /path/to/original_IRSA_artifact.zip \
  --output reports/generated/v1.5_image_pixels \
  --attempts-per-curve 4 --timeout 8 --fail-if-none
```

The original IRSA photometry must be reacquired from official archive queries if the temporary historical artifact has expired; byte hashes can change if the archive dataset changes.

## Outstanding independent scientific gates

1. **Actual multi-image PSF fitting/deblending**, robust local backgrounds, noise model, saturation/mask controls and field-star calibration. Do not interpret the high-threshold "0 additional maxima" as an all-clear.
2. **Better astrometry**, with WCS calibration residuals, Gaia parallax/covariance and neighboring non-Gaia source catalogues; CIDA 11's high **Gaia RUWE = 8.57** requires special handling.
3. Alternative ZTF epoch or external image retrieval for **CIDA 11 g**, currently not image-inspected.
4. Independently verify the original Luhman publisher catalogue and source identity; establish disk classifications before physical claims.
5. Real-data variability inference, field controls, cadence and sensitivity validation only after the prior gates.

**Independent Gaia–ZTF source identifications confirmed: 0. Sources demonstrated unblended: 0. Physical event detections confirmed: 0.**
