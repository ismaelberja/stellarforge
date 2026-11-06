# StellarForge v1.11 — Gaia reference-star formal covariance and annual parallax

**6 November 2026 · Scientific-software milestone.**

## What was implemented

- Extend earlier Gaia DR3 five-parameter correlation/covariance propagation to **all eight actual candidate reference stars** and **two target Gaia IDs** of the archived v1.8 real ZTF image pilot.
- Use the exact official Gaia DR3 10-ID TAP batch. Propagate the first-order Earth-geocentric annual parallax correction **individually for each reference on each original dated ZTF science frame**, rather than applying the target's correction to neighboring sources.
- Adjust historical WCS-referenced Gaussian centroid offsets with a sign-safe position correction **without refitting image pixels**; repeat inclusive and strict leave-one-reference-out sample consistency diagnostics. All reference quality gates remain unchanged and insufficient cases fail closed.
- Propagate the formal Gaia 5×5 covariance for each source independently; **do not mistake catalogue formal uncertainty for ZTF instrumental WCS/PSF error**.
- Protect against invalid/missing Gaia source IDs, correlation matrices, nonfinite shifts, bad source provenance, duplicate observations and false claims of astronomical discoveries. **484 automated tests passed**.

## Real-data observation

The [v1.11 real Gaia DR3 workflow](https://github.com/ismaelberja/stellarforge/actions/runs/42254052752) queried ten valid Gaia source solutions and reevaluated the original 13 reference-image models in four science exposures. Maximum geometric annual shift of an individual reference was **0.60918 mas**; median Gaia-only formal source uncertainties **0.15786 mas east / 0.11637 mas north**.

Strict internal LOO RMS changed from **0.075782″ to 0.075770″ (FT Tau)** and from **0.093046″ to 0.092971″ (CIDA 11)** after the reference-specific annual parallax correction. Those changes of **−0.012 and −0.075 mas** are small compared with the original internal disagreement. **Only 2/4 frames remain eligible** for strict holdout QA. These numbers are **not new observational instrument precision or proof of a physical source identity**.

[Real scientific evidence](reports/reference_parallax_v1.11/REAL_GAIA_REFERENCE_PARALLAX_LOO.md) · [Methods, assumptions and safeguards](docs/PHASE111_GAIA_REFERENCE_PARALLAX_AND_FORMAL_COVARIANCE.md).

## What still remains

Authentic single-star reference PSF validation, independent ZTF detector WCS/uncertainty calibration, source/blend identity, full Palomar apparent-place and FITS timing checks, high-RUWE CIDA 11 source-model review, and independent source variability validation. The archived Gaussian fits were **not** remeasured and the original IRSA target-cone photometry is not a confirmed physical crossmatch. No new physical companions or variability events claimed.
