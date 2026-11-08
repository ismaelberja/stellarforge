# StellarForge v1.13 — Official ZTF detector bitmask and native field-center PSF quality gates

**8 November 2026.** Focus: original ZTF single-exposure *instrumental data products*, not new star discoveries.

## Basis in original ZTF documentation

The [NASA/IPAC IRSA ZTF metadata specification](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html) explicitly lists, alongside each dated `sciimg.fits` primary science product, the `mskimg.fits` pixel bit-mask image, the `sciimgdaopsfcent.fits` point-spread-function **field-center image**, the `sciimgdao.psf` **spatially varying DAOPhot PSF table** and the `psfcat.fits` **PSF-fit source catalog**.

The [ZTF Science Data System explanatory supplement, Section 10.3](https://irsa.ipac.caltech.edu/data/ZTF/docs/ztf_explanatory_supplement.pdf) defines bit flags in the `mskimg.fits` product, including **saturation (bit 8 = 256)**, dead pixels (bit 9 = 512), NAN markers (bit 10 = 1024), aircraft/satellite tracks, response defects, bright-source ghosts/halos, rad-hit spikes and related anomalies. A mask bit *identifying a detected source* (bit 1 = 2 or bit 11 = 2048) is not a detector-defect flag; IRSA's documented disqualifying-bit mask is **6141**, with independent source marker mask **2050**.

**A source aperture with zero of the 6141 disqualifying mask bits is not proof the source is unblended, genuinely stellar, correctly associated to Gaia, or free of PSF wings or astrophysical structure.** It passes one *instrumental bad-pixel* screen only.

## Controlled source selection

Reuse exactly the four preregistered original dated ZTF science image exposures (two technical targets FT Tau and CIDA 11, one original g-band ZTF OID per field, two dates each) from the SHA-verified 2,212-row original IRSA positional-cone artifact and the immutable v1.8 reference-candidate offset ledger.

A bounded official Gaia DR3 exact-source-ID query returns the complete five-parameter formal covariance for **two targets plus eight reference candidates**, and each star's own first-order **geocentric geometric annual parallax** is propagated to the matching image MJD. This model is not a full Palomar topocentric apparent place: high RUWE CIDA 11, radial velocity, perspective acceleration, atmospheric dispersion, aberration, timing metadata and non-single-star systematics remain unresolved.

Every candidate source uses the **same original dated ZTF exposure product path**, but its sky-centered original `sciimg.fits` and matching `mskimg.fits` square cutouts are retrieved separately. The workflow also attempts **one original `sciimgdaopsfcent.fits` PSF stamp per distinct science exposure**, without star-position cutout parameters.

The full budget is **20 science-mask candidate pair attempts plus four native PSF-center stamp attempts** across four dated exposures (at most 44 image-product HTTP requests if every mask is accessible; a mask transport failure skips the paired science fetch). Only the original official IRSA HTTPS `/ibe/data/ztf/products/sci/` product paths are accepted, request sizes are capped, and no redirection to arbitrary products is allowed by the source URL validator.

## Mask-science grid verification

**Critical prerequisite:** an ancillary mask must be applied to pixel-level science data **only when its FITS sky geometry is compatible** with the science image. The audit requires:

1. Exactly one 2D original science image and one 2D original mask cutout, within bounded byte/pixel dimensions.
2. Same pixel-array dimensions and valid two-dimensional celestial WCS in both FITS headers.
3. The sky coordinates of representative science pixel locations must return to **the same pixel positions in the mask WCS within 0.05 pixel**. If the products lack compatible cutout WCS, their pixels are **not** treated as aligned by merely having the same shape.
4. Finite, integral, non-negative original bit-mask values in 0–65535. Reject malformed FITS, nonfinite/fractional/negative mask values and any missing/ambiguous mask image.
5. Evaluate the nominal Gaia-predicted circular aperture of radius **4.5 science pixels** and surrounding sky annulus 9–15 pixels. Count invalid science pixels, ZTF 6141 anomaly-bit pixels, bit-8 saturated pixels and bad annulus pixels; retain the aligned mask's SHA-256 and exact statuses.
6. If the mask is unavailable, its WCS differs, the aperture lies off the cutout, or any mask value cannot be interpreted, do **not** report a good/unmasked source core. HTTP 503 is archive transport evidence, **not a physical source nondetection**.

This is *not* full photometric QA: no source-specific PSF subtraction, detector variance or uncertainty map, zero-point calibration, color correction, independent cross-identification, deblending, or calibration of unknown bitmask semantics beyond the documented ZSDS definition.

## What the native PSF test does

The native ZTF `sciimgdaopsfcent.fits` is specifically a **PSF image evaluated at the center of the science image**, not a star-specific PSF at the technical target or Gaia reference-star coordinates. This phase checks only the original FITS format/shape, finite fraction, positive content and simple second moments of that field-center PSF stamp.

**The DAOPhot spatial PSF `sciimgdao.psf` is a different product.** Its evaluation at the exact Gaia reference/target image position with appropriate detector coordinates and sky/colour/mask validation is a separate scientific step. The center-stamp shape is **not fitted to individual stars** and cannot establish WCS errors or stellar identity.

## Provenance and publication

Read-only source access uses the official Gaia TAP and NASA/IPAC IRSA archive. The original IRSA catalog bytes are revalidated against their exact acquisition manifest and SHA-256; ancillary raw FITS are used exclusively in memory on the temporary CI runner. Public Git and the GitHub Actions artifact contain **only derived counts, source IDs, FITS/SHA-256 digests, outcome codes, quality flags and scientific limitations**, not original raw photometry, raw Gaia TAP CSV, FITS pixel arrays or complete FITS headers.

The public workflow is manual-only after two completed observed-data pilots on the same original science exposures, preventing repeated unattended archive traffic or misleading nondetection claims during HTTP outages. The initial run validated four paired reference masks and two native field-center PSFs. A repeat retrieved the **other two original field-center PSF products** but encountered HTTP 503 for all twenty paired masks/science cutouts; the four initial mask checks cannot be independently reverified from that rerun. The [real evidence report](../reports/original_masks_psf_v1.13/REAL_ZTF_MASK_AND_NATIVE_CENTER_PSF_EVIDENCE.md) preserves the two runs separately rather than counting their requests as new science epochs.

## Scientific thresholds and next gate

Even if some WCS-aligned source cores have no disqualifying ZTF mask bits and a native field-center PSF stamp can be parsed, the following remain **UNVERIFIED**:

- Astrophysical Gaia–ZTF source identity and physical variability.
- Absence of blends, non-Gaia neighbors, stellar multiplicity or PSF wings.
- Local empirical source PSFs and calibrated detector photometry.
- Detector field distortion and independently held-out, systematic-error-inclusive WCS uncertainty.
- Full topocentric apparent-place and trustworthy ZTF timescale/quality calibration.
- Any new substellar/binary companion or physical event.

**Next step:** validate genuine source-specific PSF `sciimgdao.psf` or `psfcat.fits` outputs using original detector coordinates, independent Gaia field-star associations and held-out source tests, combining actual CCD bitmask contamination with correlated WCS/PSF uncertainty models. Do not present a mask-clean nominal core or field-center PSF as a source association or an astronomical discovery.
