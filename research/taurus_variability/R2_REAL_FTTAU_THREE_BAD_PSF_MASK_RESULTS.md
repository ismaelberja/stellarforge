# Taurus R2 — authentic diagnosis of three frozen FT Tau original ZTF PSF-fit failures

**12 November 2026. Actual ZTF original science/mask pixels and full native source catalogues, original Gaia DR3 astrometry. Technical explanation obtained; physical Gaia–ZTF FT Tau identity remains UNCONFIRMED.**

[Pre-data preregistration](R2_FTTAU_BAD_PSF_MASK_DIAGNOSTICS_PREREGISTRATION.md) · [Genuine original-data workflow 43273246447](https://github.com/ismaelberja/stellarforge/actions/runs/43273246447) · [Unmodified prior eight-epoch original study](R2_REAL_FTTAU_MULTINIGHT_NATIVE_ASTROMETRY_RESULTS.md) · [Original derived-only 30-day artifact](https://github.com/ismaelberja/stellarforge/actions/runs/43273246447/artifacts/13968173951) · [Permanent no-raw summary](../../reports/taurus_variability_r2/FTTAU_THREE_FROZEN_BAD_PSF_MASK_DIAGNOSIS_NO_RAW.json).

## Three original PSF failures have a single technical explanation

PR #44 prospectively selected eight original dated ZTF full native PSF catalogues across fixed g/r OID/fields and independent early/late nights. Five passed and three late-night source candidates failed the original frozen source-profile gate. The three were **not** substituted or postselected in this new study. Their original full native `psfcat.fits` SHA-256 bytes were fetched again and matched the preceding original audit **3/3**. The exact Gaia DR3 source original five-parameter record was also retrieved and propagated to each original MJD.

| Exact frozen original exposure | Nearest source to epoch-propagated Gaia | Native PSF SNR | PSF chi χ | PSF sharp | Native flags | Frozen PSF quality |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| g / field 1605 · MJD 60233.393611 | 0.133039″ | 49.80 | **0.456** | −0.033 | 0 | **FAIL: χ below 0.5** |
| g / field 609 · MJD 60948.441412 | 0.095188″ | 65.01 | **0.424** | −0.002 | 0 | **FAIL: χ below 0.5** |
| r / field 609 · MJD 60935.414502 | 0.053047″ | 43.43 | **0.383** | −0.013 | 0 | **FAIL: χ below 0.5** |

All three candidates pass the original positional uniqueness criterion (nearest ≤0.6″, second nearest >1″, exactly one catalogued source within 2″). All also pass the predeclared **SNR ≥5, positive source flux, positive source sigflux, sharpness −0.5 to +0.5, nonnegative native flags, and no flagged BAD_MASK_BITS=6141** tests. The **sole** reason each one fails is that its original native PSF chi lies **below the preregistered lower bound of 0.5**, not above the upper 1.5 bound.

These quality failures do not imply the star was missing from the images. The original pipeline’s low chi values are not enough to tell whether the fit, source-specific uncertainty estimation or the previously imposed quality screen is responsible. No threshold was altered, and the original PR #44 5/8 PASS, 3/8 FAIL classification remains completely unchanged.

## Same-date original science and source-mask FITS checks

The original 60-arcsec ZTF science and matching mask cutouts were independently obtained and checked at the epoch-propagated Gaia positions, for **all three exact preselected exposures**, with complete original data SHA-256 fingerprints.

| Original exposure | Source-core disqualifying mask pixels | Saturated core pixels | Nonfinite core science pixels | Central pixel peak | Additional bright local maxima inside 12″ |
| --- | ---: | ---: | ---: | --- | ---: |
| g / 1605 | 0 | 0 | 0 | yes | 0 |
| g / 609 | 0 | 0 | 0 | yes | 0 |
| r / 609 | 0 | 0 | 0 | yes | 0 |

In all three instances the mask and science WCS aligned, the bad-mask fraction was zero in both source core and surrounding annulus, and the conservative local-peak heuristic detected a central source. **This is an instrumental image/mask observation only.** A clean source mask cannot prove a source is unblended, detect companions below the native image resolution, certify individual-source PSF error covariance, or authenticate a unique physical Gaia–ZTF match. The central-peak check is not a replacement source-quality rule.

## Scientific interpretation and decision

**Passed:** exactly three frozen original catalogues byte-for-byte independently reverified, three individually explained PSF source-fit quality failures, and three same-dated original science/mask/WCS inspections completed with no disqualifying core-mask pixels.

**Still NOT passed:** all three original native profile gates (chi below frozen 0.5); reliable original exposure-specific ZTF WCS/PSF covariance; independent source deblending; epoch-corrected PS1 individual-source astrometry; publisher/literature physical FT Tau source authentication.

**No** previously rejected original observations were promoted to scientifically accepted target candidates. **Zero verified physical Gaia–ZTF FT Tau source identifications, zero original ObjectID light curves merged, zero confirmed new astrophysical variables or companions.** R2 astrophysical identification remains OPEN; R3 variability inference is still blocked. Software engineering v2.0 remains independently ready for CV/LinkedIn.

## Reproducible original evidence and next recommended control

- Live original-data run [43273246447](https://github.com/ismaelberja/stellarforge/actions/runs/43273246447), successful with **3/3 original native SHA rechecks and 3/3 original image/mask checks**. Original-only derived ZIP [13968173951](https://github.com/ismaelberja/stellarforge/actions/runs/43273246447/artifacts/13968173951): SHA-256 `2a92b995fb6180b2e2c11d1882e7c3e7b5cf6023c85858678cea4e2d785ef047`; derived JSON SHA-256 `219c5b992670cf48eeb85c9484f7e9ae3b684d1e63ebac4c3d889bc6f39c8cc8`.
- [Original source quality report and permanent compact evidence ledger](../../reports/taurus_variability_r2/FTTAU_THREE_FROZEN_BAD_PSF_MASK_DIAGNOSIS_NO_RAW.json); source and image hashes retained, not source catalogues or FITS images.

**Next experiment:** a *prospectively documented sensitivity and external-instrument validation study* of what the existing χ≥0.5 choice means in these real PSF catalogues, ideally using independent stellar control sources, original per-source PSF uncertainty calibration, and source-specific deblending. Do **not** relax the original threshold retroactively, and continue to treat all three as failed under the original selection until independently justified.
