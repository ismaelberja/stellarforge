# Phase v1.17 — New Gaia-only source holdouts and shifted-sky ZTF positional nulls

**9 November 2026 · Scientific-validation methods for real archival ZTF data.**

## What "independence" actually means here

The v1.16 real source-image fit used **16** preselected Gaia-to-ZTF native PSF catalogue candidate source/exposure pairs from **10 previously selected Gaia DR3 objects** (two technical targets and eight reference candidates). Those actual original science+mask pairs gave **13** same-source checkerboard pixel residual screens passing the engineering thresholds, and **three** source profiles requiring further review. Checkerboard pixel withholding does **not** validate the spatial PSF on a distinct star; all pixels share the same original source/exposure.

v1.17 builds **a new source-disjoint sample** before inspecting the native ZTF PSF-fit catalogues or pixel residuals. The selection starts from **fresh, independent Gaia DR3 210″ wide-cone tables** near FT Tau and CIDA 11, excludes every Gaia DR3 source ID in the original ten-source reference/target list, and ranks quality-selected new field stars in separated sky quadrants. This is **disjoint from StellarForge's earlier sample**, but **not necessarily from the ZTF survey pipeline's original DAOPhot PSF training stars**: we do not have verified PSF-training star membership. We must not call the results a fully independent instrumental PSF validation until original training membership is audited.

## Gaia-only preregistration

The independent Gaia DR3 wide cone provides original source ID, ICRS coordinates, formal astrometric fit diagnostics, RUWE, duplicated-source flag, photometric G magnitude and SNR, proper motion, parallax and approximate full-source-neighbor geometry. All source IDs are unique and the catalogue is rejected if truncated at its 500-row cap. The technical target must be present in the fresh Gaia query. Individual control selection is completed **before** opening any original ZTF native PSF catalogue or fitting a science-pixel PSF.

- **Explicit old-source exclusion:** none of the target/twice-selected original reference Gaia source IDs can be considered new.
- **Field position:** 40″–165″ from the technical target, selected across RA/Dec sky quadrants where candidates are available.
- **Gaia G magnitude and signal:** G between 13 and 18.5 mag, Gaia flux-over-error at least 50.
- **Astrometric quality:** 0.5 ≤ RUWE <1.4, nonduplicated Gaia row with full 5- or 6-parameter astrometry, nonmissing formal parallax/proper-motion/errors; RA/Dec and proper-motion formal errors ≤3 mas and ≤3 mas/yr, respectively.
- **Isolation:** ≥10″ to **every** returned Gaia DR3 source in the original cone (including sources that themselves fail quality criteria). This is an isolation check *within Gaia*, not proof of no unresolved/non-Gaia/extragalactic neighbors.
- **Determinism and budget:** prioritize one per available sky quadrant, then quality ranking by G≈15.5 and ≈100″ target offset, at most four new sources per target field (eight new Gaia source IDs for the pilot), with transparent counts and original Gaia query SHA-256 provenance.

Original ten-source Gaia formal-covariance propagation is not reused for the **new** controls. Instead the newly selected IDs are queried from Gaia DR3 for their **own five-parameter formal correlated astrometry**, first-order Earth-geocentric parallax calculated at the actual original ZTF single-exposure MJD, and quality-checked against the native per-exposure ZTF `psfcat.fits` detections independently of the source-selection step. These are not full Palomar topocentric apparent-place solutions and cannot certify physical Gaia–ZTF identities.

## Real science image and native spatial PSF analysis

The **same four original dated single-epoch ZTF science files** anchored to the SHA-verified historical **2,212-row IRSA position-cone acquisition** are reconstructed by original date, band, ZTF OID, field, CCD and quadrant. Each frame's original full native `psfcat.fits` table and `sciimgdao.psf` DAOPhot spatial lookup are retrieved. The original native center-field `sciimgdaopsfcent.fits` stamp must agree with the decoded model at the detector center (a necessary internal reconstruction check).

New Gaia-only selected candidates are screened against the native PSF source catalogue by the existing v1.14 criteria: nearest within 1″, native per-exposure unique source counter, source SNR≥5, PSF-fit `chi` 0.5–1.5 and `sharp` −0.5..+0.5, no original ZTF deleterious bitmask intersection and no additional native catalogued PSF source within 3″. Failed catalogue screens remain **review/ineligible**, not a physical nondetection.

Only eligible candidate controls are fitted using **same-exposure original ZTF `sciimg.fits` and `mskimg.fits` cutouts**: independently WCS-registered mask/science arrays (≤0.05 pixel), source-native CCD `xpos/ypos` vs cutout subpixel phase agreement (≤0.22 pixel), 6141 disqualifying detector bit screening, fixed local DAOPhot PSF amplitude and a local linear sky plane fitted in original ZTF **DN**, with same-image checkerboard withheld-pixel residuals. Nothing here changes or reoptimizes the native spatial model on the new Gaia stars.

One source is treated as a **distinct control ID** no matter how many original exposures were used. Multiple source×epoch fits are repeated observations on *the same physical candidate* and cannot be counted as separate independent stars. A minimum of three distinct source IDs with valid original mask/PSF fits is required before reporting a descriptive median residual ratio per field/exposure; below this threshold the status is **insufficient controls**, not reliable local precision.

## Local positional null probes

Each preregistered newly selected Gaia sky prediction is displaced by **exactly ±25″ east and north**, producing four shifted positions in the same original CCD-quadrant PSF source catalogue. The audit counts ordinary native PSF catalogue sources within 1″ of a shifted location and separately counts those passing the same rough `chi/sharp/SNR/flags` source-quality profile. The negative positions are **not guaranteed to be devoid of true sources** and the shifts are deterministic rather than independently randomized. Consequently:

- This is a **local catalogue-density sanity check**, not a Bayesian false-association probability or calibrated contamination fraction.
- Zero chance shifted matches does not prove that a Gaia-to-ZTF nearest match is physical.
- A shifted match does not imply the original Gaia source ID is incorrect; it can be an unrelated ordinary ZTF source.

No source census, completeness or physical binary/variability inference is made.

## Honest scientific limitations

1. New Gaia source IDs are absent from the **StellarForge v1.16** original ten-star sample. Their membership in the ZTF original DAOPhot model training set is **unknown**. Do not claim a fully independent external instrumental PSF calibration.
2. The same original native `psfcat.fits` source extraction and approximate `sciimgdao.psf` spatial lookup model share ZTF instrumental processing. Their self-consistency alone does not estimate absolute detector PSF or WCS errors.
3. The original source's Gaia DR3 five-parameter covariance is Gaia-formal; PSF centroid, chromatic differential refraction, annual topocentric/apparent-place corrections, CCD error correlation, Gaia/ZTF shared astrometric reference biases and high RUWE CIDA 11 source systematics are not a jointly calibrated error budget.
4. The pixel-masked residual/noise metrics describe engineering model fit; their annular MAD proxy is not an independently calibrated noise variance and each checkerboard is within a single source/CCD exposure.
5. The shifted 25″ sample is not a statistically independent sky-control survey. Its hits cannot be called probabilities of false astrophysical association.
6. The four historical g-band exposures are not a representative multi-filter/multi-year variability census. They are used for **method validation**, not a new population or companion survey.
7. An archive HTTP 503, missing Gaia control, poor PSF source profile or blocked original detector mask is **missing or unusable data**, not proof of astrophysical source absence.

**Next phase:** verify whether newly studied Gaia controls were used by the native original ZTF PSF modelling program; expand samples across detector position/PSF shape, add multiple independently observed epochs and science bands, construct real CCD inverse-variance/covariance estimates and validate an externally calibrated detector WCS/PSF model on truly withheld stars. Only then consider astrophysical source identities, variabilities or substellar companions.

All original source Gaia TAP CSV, ZTF native `psfcat.fits` binary tables, original `sciimg.fits`/`mskimg.fits` pixel arrays, native spatial DAOPhot coefficients and original IRSA photometry remain in ephemeral scratch space. Public Git/Actions exports code, deterministic synthetic tests, SHA-256 source evidence and **derived scalar diagnostic summaries only**.
