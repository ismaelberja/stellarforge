# StellarForge v1.13 — genuine ZTF detector mask and native center-PSF audit

**8 November 2026 · Verified public research-software milestone.**

## New capability

This phase retrieves the **official ZTF `mskimg.fits` science-exposure detector bitmasks** and **`sciimgdaopsfcent.fits` native field-center PSF stamps**, matching original dated `sciimg.fits` images from the same official IRSA source acquisition. The code validates **exact FITS image dimensions and independent celestial WCS pixel alignment within 0.05 pixel** before interpreting a mask at a source coordinate. The official ZTF bad-pixel mask **6141** is applied; detection bits 1 and 11 are retained as nondefect source markers. The same source-specific formal Gaia 5D covariance and epoch-dependent geocentric parallax from earlier versions predicts where to screen.

## Official observed pilot

[Original real mask/PSF audit](https://github.com/ismaelberja/stellarforge/actions/runs/42467665500): **533 automated tests passed**. Of twenty target/reference candidate source locations, **four** original science+mask FITS pairs were both accessible and aligned, with **zero official disqualifying ZTF mask bits or saturated pixels** in those four reference-source apertures. All four accessible mask screens were Gaia candidate reference stars; **neither target-star core was successfully retrieved**. The other sixteen source pairs were unavailable (HTTP 503).

Two of four original `sciimgdaopsfcent.fits` field-center PSF products were readable, both 23×23 pixels, with finite positive moment profiles. These are **PSF stamps at science-field center** and **not local empirical PSFs at FT Tau/CIDA 11**. Neither their presence nor mask-clean reference apertures independently validates source identities, clean/unblended single stars, any WCS error budget or astrophysical events.

[Full verifiable real mask/PSF report](reports/original_masks_psf_v1.13/REAL_ZTF_MASK_AND_NATIVE_CENTER_PSF_EVIDENCE.md) · [Methods, bit semantics and limits](docs/PHASE113_OFFICIAL_ZTF_MASK_AND_NATIVE_CENTER_PSF.md).

## Remaining scientific gates

One must obtain source-specific native `sciimgdao.psf` spatial PSF or `psfcat.fits` information, establish authentic Gaia–ZTF identification and a well-characterized spatially distributed field-star sample, validate detector and source crowding/saturation and exposure time models, and then cross-validate instrumental WCS/PSF error terms on held-out stars. **Zero confirmed new companions, physical variability events, independently calibrated WCS solutions or authenticated isolated single-star empirical PSFs.**

This project's public Git contains code, tests and derived aggregate evidence only; original third-party Gaia/IRSA raw source data and FITS pixel arrays are not added.
