# Taurus R2 — four fixed historical ZTF science exposures: original FITS/mask/native-PSF source gates

**Protocol fixed before the new original-image workflow, 11 November 2026.**

## Why this is the next appropriate experiment

IRSA's original ZTF positional source tables have been retrieved
for 22/24 *nonrepresentative* Taurus technical Gaia source positions.
However, a positional table **is not proof of the same physical
Gaia/ZTF source**. Two historic Gaia IDs, **FT Tau** (149623711269425408)
and **CIDA 11** (3419110734340795648), already have four original
single-epoch ZTF `zg` science products documented in StellarForge
v1.8–v1.16. They therefore provide a reproducible, pre-existing
observational validation pilot without selecting new sources based
on their lightcurve variability.

| Original technical field | Historic ZTF OID | Original science MJD |
| --- | --- | ---: |
| FT Tau | 1605115300003377 | 58388.389016 |
| FT Tau | 1605115300003377 | 58491.184780 |
| CIDA 11 | 610106300008010 | 58475.113750 |
| CIDA 11 | 610106300008010 | 58849.135984 |

These are the **same four previous original ZTF exposures**,
**not newly acquired astronomical science epochs**, and the study's
original 24-source denominator does not change.

## Hard experimental protocol

1. Verify SHA-referenced v1.8 original source/exposure ledger.
   Request each original, fixed ZTF OID with a **tight MJD window** and
   require precisely one original matching `filefracday`,
   field, band, CCD and quadrant; never substitute another epoch
   because it happens to look cleaner. The direct ID/TIME query
   is provided by [IRSA's official ZTF API](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html).
2. Retrieve **two exact Gaia DR3 source IDs** with their original
   formal five-parameter covariance. Propagate the source-specific
   Gaussian formal position to each original observation date
   using the established first-order geocentric parallax model.
   High RUWE, unresolved multiplicity, unknown telescope topocentric
   apparent place and instrument WCS errors remain distinct warnings.
3. Using the authentic ZTF exposure metadata, reconstruct each
   official dated `sciimg.fits` **60-arcsec cutout** at the Gaia
   predicted coordinates. Retrieve the matching `mskimg.fits`
   same-geometry cutout. Validate image and mask WCS alignment
   and native core bitmask quality, and independently within the
   original science pixels count nearby bright local-maxima
   candidates using the existing well-documented smoothing heuristic.
   A nearby maximum **is not automatically a companion**.
4. Fetch the original dated **full native `psfcat.fits` source table**.
   This catalog is produced by **the same ZTF processing pipeline**,
   not an independent external star catalogue. Count native catalogue
   records within fixed **1/2/3/5/10 arcsec** of the Gaia-predicted
   position, and record the nearest and second-nearest native rows
   and potential additional sources within 3 arcsec. A clean catalog
   or mask does **not** prove the sky source is isolated.
5. If original direct-ID metadata, FITS, bitmask, psfcat, Gaia
   or WCS fail, use explicit **INCOMPLETE/REVIEW** statuses.
   No missing data can ever be treated as a stellar nondetection
   or a confirmation of zero source neighbours.
6. Keep original raw FITS and TAP/IRSA source tables in memory on
   GitHub Actions. Save **only** source-bounded derived evidence
   including SHA-256 payload fingerprints, exposure identifiers,
   local catalogue-neighbour counts, WCS/mask statuses and warnings.

## Scientific interpretation

This stage is a **four-exposure instrumental/positional consistency
screen**, **not independent physical Gaia-to-ZTF identity
authentication** or an astrophysical discovery. The original native
`psfcat` and FITS headers share ZTF's internal WCS and PSF
processing, so agreeing positions and pixels cannot establish
a statistically independent WCS calibration. An unresolved faint
neighbour may remain invisible in Gaia and `psfcat`, and multiple
ZTF ObjectIDs cannot be safely merged from this work.

No Taurus-wide variability frequency, periodicity, newly discovered
companion, new source identity, or independent PSF calibration
is claimed. **R2 will remain incomplete until additional
independent cross-checks and original Luhman literature membership
verification are performed.** R3 science variability studies still
require bona fide source identity, sound quality filtering, and
separate time systems/bands.

[Previous original 22/24 IRSA source-access milestone](R2_REAL_NINE_IRSA_SOURCE_RECOVERY.md) ·
[Previous four-exposure original ZTF masked source work](../../reports/masked_spatial_psf_v1.16/REAL_ZTF_PIXEL_RESIDUALS_EVIDENCE.md) ·
[ZTF official science and ancillary product file paths](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html).
