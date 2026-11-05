# StellarForge v1.6 — Real ZTF FITS Gaussian-shape proxy results

**Execution date:** 5 November 2026.  
**Provenance:** [real IRSA image analysis run](https://github.com/ismaelberja/stellarforge/actions/runs/42033819374) using earlier official photometric acquisition and SHA-256 checks.  
**Scientific status:** provisional image-shape diagnostics; **NO independently verified Gaia–ZTF source identities or companion detections.**

## Real observations and fit outcomes

We revisited the six ZTF OID/filter groups around FT Tau and CIDA 11 using the prior **2,212-row official IRSA cone-query dataset**. We sampled median, earlier and later science exposures per group; reference coadds were attempted only if science images could not be modeled. Across 21 HTTP image attempts, 3 distinct individual science FITS files passed image/WCS checks and produced a bounded local Gaussian proxy.

| Query target | ZTF OID | Filter | FITS image date MJD | FWHM x / y proxy (arcsec) | Fitted center offset from Gaia predicted position (arcsec) | Max positive outer residual / local MAD-noise proxy | Provisional model status |
|---|---|---|---:|---|---:|---:|---|
| FT Tau | 1605115300003377 | g | 58760.427234 | 2.529 / 2.482 | 0.0626 | 21.45 | REVIEW_REQUIRED |
| FT Tau | 1605215300005161 | r | 58725.510613 | 1.857 / 1.987 | 0.0218 | 60.52 | REVIEW_REQUIRED |
| FT Tau | 609208400001969 | r | 60151.473368 | 2.581 / 1.783 | 0.0753 | 44.13 | REVIEW_REQUIRED |
| FT Tau | 609108400001155 | g | — | — | — | — | NO_USABLE_IMAGE |
| CIDA 11 | 610106300008010 | g | — | — | — | — | NO_USABLE_IMAGE |
| CIDA 11 | 610206300011997 | r | — | — | — | — | NO_USABLE_IMAGE |

The apparent FWHM and centroid offsets come from **a single axis-aligned elliptical Gaussian plus planar background fit**, not an independently calibrated ZTF PSF. The center offsets are relative to the image's existing header WCS and a simplified Gaia 2D proper-motion prediction; no full parallax, covariance, WCS recalibration or independent source identification was performed.

The noise denominator is a local annular median-absolute-deviation estimate, **not** a propagated CCD photon/read-noise variance. Thus residual/noise values of 21–61 are **model-mismatch screening quantities**, not astrophysical detection significances or evidence of a binary. All three images are explicitly flagged for further review because a simple Gaussian leaves strong positive outer residuals. Genuine high-SNR stellar PSFs can have wings and structure poorly modeled by a single Gaussian.

## Independent repeated images: absent

- **0/6 OID/filter groups** yielded two or more separate usable science FITS models.
- **0 independent multi-epoch repeatability measurements** can legitimately be reported. Reference coadds are not treated as independent dated science exposures.
- **CIDA 11:** no real image was successfully modeled in this v1.6 execution. Prior v1.5 did access one r-band image, but this does not establish a repeatable independent series. The Gaia DR3 RUWE of about **8.57** is still a substantial astrometric-quality caution, not proof of multiplicity.

## Error and uncertainty accounting

- 21 bounded image attempts were made: 3 successful single-science Gaussian models and 18 unsuccessful requests, chiefly **HTTP 503** with one **URLError**.
- The archive's temporary failures are **technical access failures**, not source non-detections.
- The underlying position cone is preselected around the Gaia catalog coordinate. An image source near the requested center is therefore **not** an independently confirmed Gaia/ZTF association.
- A Gaussian shape proxy cannot rule out unresolved binaries, nebulosity, PSF wings, field-dependent artifacts, blends, saturation, or nearby sources absent from Gaia.
- Science WCS header astrometry and Gaia proper-motion propagation have not been independently recalibrated or assigned a realistic uncertainty distribution.
- Publisher-original comparison of the Taurus membership table and independent disk-class labels remain pending.

## Reproducibility and protected inputs

The code lives in [the v1.6 module](../../src/stellarforge/v16_psf_repeatability.py), with a [runner](../../scripts/run_v16_psf_repeatability.py) and offline synthetic PSF/WCS tests. The original IRSA raw photometry bytes and transient FITS pixels are **never committed or uploaded**. The GitHub Actions result artifact includes only derived metrics and error statuses.

\`\`\`bash
python -m pip install -e '.[test,analysis,images]'
python -m pytest -q
python scripts/run_v16_psf_repeatability.py /path/to/authorized_original_IRSA_artifact.zip \
  --output reports/generated/v1.6_psf --timeout 8 --fail-if-no-fit
\`\`\`

**387 automated tests passed**, in addition to the live image attempt.

## Next scientific gate

Rather than treating model residual peaks as astronomical companions, compare the target to **independent same-field stellar PSF profiles**, model spatially varying wings, examine ZTF quality/mask maps, and obtain at least two independently usable science frames per OID. For CIDA 11, explore alternate authenticated archive access or later allowed retries rather than interpreting HTTP 503 as absent data. Incorporate Gaia covariance/parallax and independent image astrometry before making source-identity or physical-variability claims.

**Confirmed Gaia–ZTF source identities: 0. Scientifically verified unblended targets: 0. Confirmed physical variability events: 0.**
