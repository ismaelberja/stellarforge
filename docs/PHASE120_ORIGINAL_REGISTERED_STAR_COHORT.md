# Phase v1.20 — A preregistered strict whole-star PSF pilot on original ZTF frames

**10 November 2026 · Scientific code and original-data runnable workflow.**
**CI is synthetic/offline only until the manual real-data workflow is dispatched.**

## What was built

StellarForge v1.19 implemented an empirical model from at least 3 training
stars tested against at least 2 different whole held-out star images, without
using ZTF's original spatial DAOPhot coefficients. Its source inputs had to
be externally registered; no full original ZTF data had yet been passed
through the new pipeline.

v1.20 adds the **real-data acquisition, source registration and fixed-cohort
eligibility layer** for the two dated original g-band **CIDA 11** exposures.
CIDA 11 is chosen before source residual inspection because the v1.17
independent Gaia wide-cone audit found 20 Gaia sources that survived the
unchanged strict control selection before a four-star budget, compared with
zero newly eligible strict FT Tau references. This does not guarantee that
enough genuine original source/mask FITS will be available or pass QC.

### Preregistered split (Gaia-only, before ZTF access)

The v1.17 strict-quality candidate selector remains unchanged:
- Gaia G magnitude 13–18.5, G flux SNR >=50 and RUWE 0.5–1.4;
- five-/six-parameter astrometry, sane formal errors, no Gaia duplicated flag;
- >=10 arcsec from **every** Gaia catalogue source in the original cone;
- 40–165 arcsec from target, and exclusions of the original ten
  technical Gaia source IDs.
- deterministic quadrant-first and quality ordering.

The existing selector has an immutable per-call five-star maximum. v1.20
selects those five **before opening any ZTF archive catalogue**, then calls
the same selector a second time with those five IDs additionally excluded,
retaining all original Gaia cone rows for nearest-neighbour screening.
The resulting seven candidate IDs are allocated **four training + three
whole-star holdout** in a fixed Gaia-only order. No failed star can be
replaced using the other group after native PSFcat checks or pixel residual
inspection. A target absent from the cone, a capped survey response, or
fewer than seven candidates is a scientific *eligibility failure*, not
a non-detection.

### Genuine original ZTF image and mask registration

A manually dispatched workflow retrieves the original SHA-audited
IRSA position-query artifact and reconstructs **exactly** the two historical
CIDA 11 science URLs (fixed ZTF OID, filter and MJD). The runner fetches:
- exact Gaia DR3 five-parameter covariance and exposure-date prediction
  for the seven preselected IDs;
- the original per-exposure ZTF PSF-fitting catalogue
  ("psfcat.fits") for a conservative **candidate identification/QC gate**;
- original same-science-exposure 60-arcsec "sciimg.fits" and "mskimg.fits"
  source-centered cutouts for native-catalogue-qualified stars.

The new registered-stamp extractor verifies source/mask celestial WCS
and grid agreement <=0.05 pixel, compares ZTF native detector-coordinate
subpixel phase with the science-cutout WCS (<=0.22 pixel), and rejects
invalid, saturated or dangerous core mask pixels. It bilinearly evaluates
each original DN cutout around the native catalogue source coordinate
on a common 23x23 grid, propagating a **dilated detector defect mask**
to interpolation-adjacent pixels. It also checks a **local flux-centroid
symmetry proxy** (<=0.08 pixel), which is a descriptive registration
quality gate, **not** an independently calibrated WCS residual.

The v1.19 empirical model is called only if >=3 of the **four
preregistered training** sources and >=2 of the **three preregistered
held-out** sources survive all native profile, mask, registration and
image-availability screens within the same science exposure.

### Important selection and noise caveats

The original ZTF PSFcat screening uses ZTF's **own fitted-source
profile chi/sharp/SNR/flags**, so eligible samples are *not* independent
of all ZTF survey reduction or PSF-selection effects. The newly built
empirical model uses **no original DAOPhot PSF coefficients** and tests
entirely distinct images, but the survey's original PSF-building training
star roster is still **unknown**. A new model's internal star split is
not proof of independent survey calibrator exclusion.

Recentered pixels undergo bilinear interpolation and have correlated
noise. The v1.19 diagonal CCD variance and sky-correlation tools cannot
be assigned a physical uncertainty without **verified exposure-specific
gain/read noise**, representative source-free sky samples and a validated
resampling covariance treatment. Therefore this phase does not produce
calibrated photometry, formal WCS/PSF precision, source identification or
astronomical discoveries.

### The three old high-residual profiles

v1.16 reported three elevated residual profiles among 16 original source
fits. They remain flagged for future *multi-exposure/filter*, image-mask,
neighbor/crowding, diffuse/background and original WCS evaluation.
They are **not** claimed to be new stars, companion objects or variable
detections. v1.20 does not rerun them because the strict CIDA empirical
pilot is a separate, prespecified control task.

## Reproducibility and CI

- Core strict sample and registered pixel code:
  src/stellarforge/v120_observed_star_cohort.py
- Manual original-data CLI:
  scripts/run_v120_original_empirical_psf_pilot.py
- Original-data workflow (NOT triggered by CI):
  .github/workflows/v120-original-empirical-psf-pilot.yml
- All regression/synthetic FITS, WCS and archive isolation tests:
  tests/test_v120_observed_star_cohort.py and
  tests/test_v120_real_pilot_contract.py
- Real-data aggregate output (when manually run):
  "V120_REAL_ORIGINAL_STRICT_COHORT_NO_RAW.json" and ".md".

The live workflow **must be dispatched manually** via GitHub Actions
after review. At phase publication it has not been run: the only
validated v1.20 executions are **synthetic CI regressions**. Raw Gaia
responses, source catalogues, science/mask FITS, source IDs, fitted
empirical PSFs and original observation pixels are never committed or
uploaded as workflow artifacts; only bounded counts/statuses and
SHA-256 source-product digests may be uploaded.

## Decision / next step

If the manual real-data workflow obtains >=3 genuine training and
>=2 different held-out stars **per exposure**, evaluate descriptive
source-level residuals and compare the original predeclared groups.
Otherwise publish the exact eligibility/availability blocker,
not an invented independent PSF calibration. Any publication-grade
instrumental error budget or physical Gaia–ZTF identity requires
substantial external survey validation beyond this milestone.
