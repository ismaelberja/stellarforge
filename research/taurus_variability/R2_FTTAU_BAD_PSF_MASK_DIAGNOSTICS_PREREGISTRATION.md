# Taurus R2 — prospectively frozen diagnostics for the three poor-quality independent-night FT Tau ZTF sources

**12 November 2026; this diagnostic protocol is committed before requesting the original ZTF PSF catalogues, science pixels or masks for this increment.**

## Provenance and target

This is a direct continuation of merged **PR #44** (authentic multi-night native source audit, workflow [43270659201](https://github.com/ismaelberja/stellarforge/actions/runs/43270659201)). FT Tau provisional technical Gaia DR3 source ID remains **149623711269425408**. The original seed, four 2018/2019 image anchors, fixed four ObjectIDs, eight newly selected independent-night epochs, native original QA criteria and their 5/8 pass / 3/8 fail outcomes **must not change**.

Previous source selection was earliest and latest eligible *non-anchor* night per fixed band/OID/field before inspecting images. Three selected **late-night** native nearest-source candidates failed exactly the frozen PSF quality criterion, despite being positionally close to Gaia. Only these three—not other dates or alternative brighter sources—are the diagnostic sample:

| Band and field | Fixed ZTF ObjectID | Frozen exact filefracday | MJD | Full original PSFcat SHA-256 |
| --- | --- | --- | ---: | --- |
| g / 1605 (CCD 15 Q3) | 1605115300003377 | `20231016393588` | 60233.393611 | `e989ec78cdef805cf8adecfb37d1f0cb1b2b3894a1892d0eb36374ccf4ca505b` |
| g / 609 (CCD 8 Q4) | 609108400001155 | `20250930441343` | 60948.441412 | `785a472396fa369080e84589bc282122e7f2f44d37059fb52efe769c8cae2ca8` |
| r / 609 (CCD 8 Q4) | 609208400001969 | `20250917414479` | 60935.414502 | `f1127a1eaf84a507b910952f5e1d35f43a55e4be0c6f9a09b272507dd8f7f043` |

The permanent PR #44 derived-only ledger `reports/taurus_variability_r2/FTTAU_MULTINIGHT_ORIGINAL_ZTF_SOURCE_AUDIT_NO_RAW.json` must match the three original SHA-256 hashes, the selected late MJD, four fixed OIDs, and earlier pass/later fail flags. On any mismatch, fail closed; do not substitute an image.

## Predeclared diagnostic questions

1. Retrieve original Gaia five-parameter astrometry by exact source ID and propagate to each frozen late MJD using the project's existing proper-motion + approximate geocentric parallax model, **without changing the Gaia solution**.
2. Re-fetch exactly the three specified original IRSA **full** `psfcat.fits` data streams; **require byte-for-byte SHA-256 equality** with the permanent ledger and table above. Never fetch a replacement catalogue to obtain a passing candidate. From the *nearest* native source to the propagated Gaia position, compute only **derived** fit/QC metrics. Give an explicit yes/no for each of the frozen tests: SNR ≥5, positive flux, positive sigflux, PSF chi in [0.5, 1.5], PSF sharp in [−0.5, 0.5], nonnegative flags and `flags & 6141 == 0`. Verify the earlier geometric screen (nearest ≤0.6 arcsec; second beyond 1 arcsec or absent). **Do not move thresholds, rewrite the earlier 5/8 result, reselect sources or label a failed catalogue an astrophysical nondetection.**
3. Independently retrieve a 60 arcsec original ZTF **science cutout** and corresponding same-exposure official **mask cutout**, centred at epoch-propagated Gaia. Reuse existing hardened FITS/WCS alignment, four-and-a-half-pixel source-core mask, saturation and local-image-peak diagnostics. Separately report bitmask defects, science image WCS/peak findings and any request/access errors. Do not interpret an unmasked image core as proof of a clean unresolved stellar source.
4. For each of the three frozen late-night candidates record whether the PSF-profile failure is explained by low SNR, flux/sigflux validity, chi/sharp, flags, or combinations. Mask science checks are **diagnostic only** and cannot turn a previously failing native PSF source into an accepted source. If image/mask service fails, state instrumental evidence unavailable, not a negative scientific observation.

## Evidence and claim restrictions

No raw full catalogue rows, single-source original photometry or fluxes, FITS image pixels or original Gaia raw table will be committed. Preserve bounded original data SHA-256 hashes, frozen selection keys, individual boolean QC gates, rounded *derived* PSF chi/sharp/SNR diagnostics, original bit masks (quality flags), image/mask WCS status and summarized source-pixel counts. Never save source catalogue source IDs or neighbor star rows. Original archive responses stay transient on GitHub Actions.

Acceptance is **a valid, auditably exact, per-failure technical diagnosis**, not a corrected detection. Regardless of image-mask outcomes: **zero confirmed Gaia–ZTF physical FT Tau matches, zero newly established variables/companions, zero merged ZTF OID light curves**, R2 scientifically OPEN and R3 variability blocked. Additional resolution/literature source identification and independent WCS/PSF covariance remain required.

Original methodologies: [Gaia DR3](https://gaia.aip.de/cms/data/gdr3/), [ZTF science archive](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_api.html), and the repo's `v113_official_masks_psf`, `v114_native_psfcat_association` and `v15_image_pixels` methods.
