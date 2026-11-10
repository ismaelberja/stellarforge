# StellarForge v1.21 — Scientific falsification and release evidence

**10 November 2026. Software and methodological audit; NOT a new real ZTF observation.**

## Starting point

StellarForge v1.15–v1.18 studied genuine original ZTF DAOPhot source pixels
and masks. v1.19–v1.20 added an empirical PSF constructed with distinct
training and validation stars, but the new implementation had only
been verified with offline synthetic tests. Membership in the original
ZTF DAOPhot PSF-building star sample remains UNKNOWN. A native ZTF
PSFcat quality screen still depends on the official survey pipeline.

## 1. Urgent archive availability

The historic original IRSA positional acquisition GitHub Actions run
**41997079598** contains the artifact **taurus-two-target-raw-UNVERIFIED**.
GitHub Actions metadata was checked on 10 November: artifact ID
**13401380025**, size **181,170 bytes**, unexpired at the time checked,
with recorded expiry **12 November 2026, 08:47:05 UTC (09:47:05 CET)**.
This proves metadata availability only, NOT the raw ZIP content or survey
source integrity. The new audit rejects foreign artifact names, missing
expiry timestamps, absent sizes, naive dates and expired entries.

**Next essential action before expiry:** manually dispatch the
[v1.20 original CIDA 11 star pilot workflow](https://github.com/ismaelberja/stellarforge/actions/workflows/v120-original-empirical-psf-pilot.yml)
on branch main, retaining acquisition run ID **41997079598**.
Only that original-data workflow can test whether at least **three**
of the four preselected training and **two** of the three disjoint
held-out CIDA 11 stars satisfy original ZTF native PSF catalogue,
masked science-image and WCS registration gates within the SAME exposure.
No one may reassign the held-out stars based on observed PSF residuals.

The v1.21 connector cannot dispatch workflow runs; no unapproved
automatic push-trigger has been installed. The original real-data
workflow has **not** been executed in this phase.

## 2. Observational evidence integrity

The new audit validates bounded aggregate reports: the exact CIDA 11
field, g-band historic epochs, mutually consistent original PSFcat
eligibility counts, registered training/holdout counts and actual
whole-star model completion statuses. It fails closed if a report claims
a completed real internal empirical PSF model with fewer than 3
registered training and 2 different held-out source stamps.

A complete original-data aggregate can prove that the INTERNAL empirical
whole-star comparison was attempted or completed; it cannot authenticate
the original survey training-star roster, source physical identities,
instrumental WCS errors, CCD covariance, variability or companions.
The report is only as trustworthy as the authenticated upstream data.

## 3. Falsification tests

- **Leave-one-training-star-out:** rebuild the internal empirical
  model while excluding each training star, using unchanged whole-star
  holdouts. Report the largest residual-RMS/sky-MAD change and how often
  holdouts require review. This tests sensitivity, not source identity.
- **Artificial secondary-profile injection:** add a bounded known
  Gaussian secondary peak to a COPY of one held-out source image.
  Refit with the unchanged model and measure whether the held-out
  residual becomes worse. This is a SYNTHETIC sensitivity exercise,
  **not** a new physical companion detection or calibrated completeness.
- **Source and publication safeguards:** disjoint source IDs,
  same-exposure validation, fail-closed archive and sample metadata,
  no publication of real source pixels or candidate IDs.

## 4. Three historic high residuals still open

Numbers preserved from the [v1.16 real ZTF science report](../reports/masked_spatial_psf_v1.16/REAL_ZTF_PIXEL_RESIDUALS_EVIDENCE.md):

| Candidate | Historic MJD | Held-out pixel RMS / sky MAD | Max positive / sky MAD |
| --- | ---: | ---: | ---: |
| FT Tau target | 58491.184780 | 1.6723 | 7.6730 |
| CIDA 11 target | 58849.135984 | 2.6341 | 11.8679 |
| CIDA 11 field Gaia-reference candidate | 58849.135984 | 1.3652 | 7.8125 |

The positive 7x threshold is an engineering same-star residual quality
screen, NOT a survey-calibrated 7-sigma astrophysical signal.
PSF mismatch, crowding, nebulosity, positioning, systematics and
correlated noise are all unresolved alternatives. Nothing has been
remeasured in v1.21 and **zero new objects are confirmed**.

## 5. Release decision

A reproducible, well-documented software **v2.0 portfolio** can be
closed with these limitations, but genuine independent survey PSF/WCS
calibration and scientific discovery remain blocked by lack of external
identity, original PSF-training roster and CCD-noise verification.

Code: src/stellarforge/v121_science_falsification.py

Tests: tests/test_v121_science_falsification.py

Original observational workflow: .github/workflows/v120-original-empirical-psf-pilot.yml
