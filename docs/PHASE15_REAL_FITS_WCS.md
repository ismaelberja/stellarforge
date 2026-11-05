# Phase 15 — Real ZTF FITS pixel / celestial WCS review

**Engineering milestone (5 November 2026).** This stage moves beyond checking FITS transport headers. It opens small, bounded **real image cutouts** and applies an explicitly provisional image/pixel review, subject to IRSA's availability.

## Scope

Starting from the same two SHA-verified IRSA ZTF cone-query CSVs (FT Tau, CIDA 11, total **2,212 raw rows, six OID-band groups**), the program:

1. Regenerates and validates the original observational query provenance and source bytes through the v1.3 review.
2. Selects a bounded set of original science exposures **separately for each ZTF OID/filter**: median, earlier and later epoch. It also prepares a coadded reference-image fallback; a coadd is **not** falsely given the median science date.
3. Constructs the official IRSA IBE `center`, `size=45arcsec`, `gzip=false` image cutout requests from original ZTF `filefracday`, field, CCD, quadrant and passband. Follows the [ZTF product API](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_api.html) and [IBE cutout interface](https://irsa.ipac.caltech.edu/ibe/cutouts.html).
4. Reads at most **3 MB per FITS file** and validates uncompressed FITS structure, finite pixel coverage, a single 2D plane and plausible image dimensions.
5. Reads the celestial WCS through Astropy, checks that the **2D-proper-motion-predicted Gaia position** falls in the usable image interior, and checks that the plate scale is plausible.
6. Computes a median/MAD background-noise proxy, finds Gaussian-smoothed 5-sigma local maxima, and records whether one is close to the expected Gaia position and whether there are **additional possible local peaks within 12 arcsec**.
7. Writes only a small **aggregate JSON/Markdown** with status, SHA-256, WCS and peak offsets. Raw ZTF CSVs and FITS pixel arrays never enter the Git tree or uploaded artifacts.

## What the image measurements *cannot* prove

- A local maximum is not an authenticated stellar PSF or astrophysical source. It may be an image artifact, PSF substructure, cosmic ray, unresolved binary, or nebulosity.
- A single image's **header WCS is read, not independently recalibrated** against multiple reference stars; no external WCS residual estimate is claimed.
- This is **not** PSF fitting, resolved deblending, background modeling, calibrated aperture photometry, robust morphology classification or a Gaia–ZTF crossmatch.
- The propagated Gaia position currently neglects full parallax, source covariance, perspective acceleration and some time-system details; CIDA 11's **high RUWE** makes this especially important.
- Image processing succeeds only where the public IRSA cutout service returns a valid file. HTTP 503 or missing images count as **transport failures**, not non-detections.
- Successful WCS/pixel screening does **not** exclude unresolved or non-Gaia sources.
- No disk class, variability event, source-identity confidence probability, physical discovery or selection-function measurement is inferred.

## Engineering safeguards

The standalone package has synthetic FITS fixtures with known WCS, a central Gaussian point source and optionally an additional nearby peak, as well as invalid WCS, missing data, no-source images, bad URLs and remote errors. All their output claims remain provisional.

The live workflow is executed only with an original SHA-verified IRSA acquisition artifact and only uploads **non-image aggregate** reports. No personal credentials, unpublished ALMA/TFM data or full survey cutouts are added to public GitHub.

## Reproduce

```bash
python -m pip install -e '.[test,analysis,images]'
python -m pytest -q

python scripts/run_v15_image_pixels.py /path/to/original_IRSA_raw_artifact.zip \
  --output reports/generated/v1.5_image_pixels \
  --attempts-per-curve 4 --timeout 8 --fail-if-none
```

**Next scientific gates:** inspect any accessible FITS with a vetted PSF/background and WCS residual pipeline, improve Gaia astrometric propagation including uncertainty, examine published and non-Gaia neighboring sources, assess multi-image consistency, and only then reconsider astrophysical source identities. Do not promote preliminary maxima to discovered companions.
