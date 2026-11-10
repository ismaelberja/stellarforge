# Phase v1.19 — Distinct-star empirical PSF and detector-noise validation gates

**10 November 2026. Scientific software milestone, not a new ZTF observation or a discovery.**

## Scientific motivation

In v1.18 the four original historic FT Tau and CIDA 11 ZTF frames supplied
8/8 original sciimlog/log processing records. These contain PSF/DAOPhot
processing diagnostics, **but do not authenticate a complete, source-keyed
list of the stars used to build the original ZTF PSF**. The v1.18 additional FT Tau
sample contains one exploratory Gaia source fitted twice: two epochs are NOT
two independent stars. The same-image checkerboard residuals used so far do
not address independent stellar PSF generalization.

This phase introduces an entirely **separate empirical image PSF model**, built
only from explicitly declared training-star input images. It has **distinct
whole-star holdouts** and deliberately refuses samples too small to support
such a test. The v1.19 implementation DOES NOT ingest the original ZTF
DAOPhot coefficients or pass the published center PSF into the new model.

## Interface and mandatory input contracts

Module: src/stellarforge/v119_empirical_psf_noise.py

- RegisteredStar: an identified star in exactly **one science exposure**, with
  pre-registered original science-pixel cutout in DN and its matching official
  6141-bit ZTF image mask (v1.13). The parent pipeline must independently
  verify source coordinates, WCS registration and masked science/mask provenance;
  **the v1.19 module cannot authenticate a supplied array**.
- Source stamps are square, 19–35 pixels on an odd grid, within 0.08 pixel
  measured residual alignment **after** registration. This is an explicit
  prerequisite: the code does not perform detector astrometric registration.
- A minimum of **three distinct training stars and two OTHER distinct held-out
  stars in the SAME exposure** is enforced. Reusing the same Gaia source ID
  across epochs or in both groups causes rejection. Distinct IDs do not by
  themselves establish physical source identity.
- Bad/saturated core pixels, invalid masks, mismatched shapes, unbounded
  inputs, unreliable sky annuli and low source-to-sky signal are rejected.
- Each input star is sky-subtracted using a mask-clean outer annulus, normalized
  with an inner-aperture flux proxy, and given equal weight. The empirical
  PSF is a normalized, nonnegative, pixelwise training-star median.
- For **whole held-out stars**, only flux amplitude and scalar background
  are fitted; residual RMS relative to the star's own annulus MAD is reported
  as a descriptive diagnostic. This is not reduced chi-square nor an
  astrophysical source-quality or instrument-error significance estimate.

The returned PSF pixels, Gaia source IDs, and fit-level outputs are
**ephemeral**. Only public_aggregate_only can form the deliberately restricted,
counts-only public summary; never commit original survey images, candidate
identities or independently reconstructed original PSF pixel arrays.

## CCD noise: what is modeled, what is not

A *diagonal*, conditional model per pixel in detector DN^2 is

    Var(DN) = (S_DN + B_DN)/gain_(e-/DN) + (RN_e/gain_(e-/DN))^2,

for nonnegative expected **sky-subtracted** stellar S_DN, nonnegative sky
B_DN and a supplied physically correct per-exposure gain/read noise.
This formulation applies to expected bias-subtracted input in DN; it is NOT
valid if raw detector offset/bias DN is passed as stellar signal. ZTF-specific
gain/read-noise values must come from a verified, exposure-relevant source,
never invented constants.

Because resampled CCD pixels may be correlated, v1.19 also computes the
empirical aperture-level variance ratio

    Var(sum of aperture sky pixels) / sum(Var of individual sky pixels)

across >=16 externally verified distinct, nonoverlapping blank-sky
cutout windows. This can expose non-diagonal sky variability, but it is
NOT a pixel covariance matrix, a calibrated PSF-flux uncertainty, or a
universal uncertainty inflation factor. Nonoverlap, empty windows and
background stationarity are not proven by this function.

## Scientific evidence categories

| Question | v1.19 result |
| --- | --- |
| Can a new empirical model be built without DAOPhot PSF coefficients? | Implemented and synthetically testable |
| Are whole held-out stars required to differ from all training sources? | Enforced by source-ID guard |
| Can the supplied images be authenticated as true ZTF originals? | **No**, must be checked by upstream provenance |
| Were the held-out stars absent from the original ZTF pipeline PSF model? | **Unknown**; original roster still unavailable |
| Can real FT Tau/CIDA 11 data satisfy >=3+2 disjoint stars per frame today? | **Not established** on previous validated roster |
| Are physical Gaia–ZTF associations, independent PSF/WCS and CCD covariance calibrated? | **No** |
| Has an astronomy discovery been established? | **No** |

## Verification before applying to original survey observations

1. Obtain substantially more high-quality masked stars **within one exact
   original ZTF exposure**, before evaluating their residuals; fix source
   selection and training/validation membership using upstream Gaia and
   ZTF source-quality criteria (keep strict and exploratory tiers distinct).
2. Verify native image IDs, UTC exposure date, original ZTF URL, source
   center WCS, science/mask WCS offset, source-free annuli, contamination,
   and centroid registration **without using a target's held-out residual**.
3. Use independent source stars in the same CCD quadrant and filter.
   Keep all previously published ZTF original PSF training membership
   claims as **UNKNOWN**. This new empirical model is independent
   of the original model *coefficients*, but cannot establish star-list
   disjointness from the original survey calibration.
4. Derive per-exposure gain/read noise from verified detector metadata,
   accumulate nonoverlapping source-free sky windows, and compare masked
   residual distributions under a preregistered analysis.
5. Publish the date/frame-level **bounded aggregate** results and relevant
   archive hashes; original pixels and individual source data remain off Git.

All v1.19 regression checks are deterministic **synthetic-only**. They do
not constitute a real-data validation. Missing stars, failed image access
or rejected masks must not be relabeled as astronomical nondetections.

## Portfolio scope

This is a useful, conservative software-validation advance in the path
toward v2.0. The observational program remains **open**. The next phase
should attempt exposure-level integration on a fixed, larger original ZTF
reference-star sample and review the v1.16 anomalous masked residuals
without treating them as new objects.
