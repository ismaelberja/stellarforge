# StellarForge v1.19 — Empirical whole-star PSF holdout and CCD noise gates

**10 November 2026 · Synthetic-only scientific software milestone.**

## Delivered

- Implemented an internally independent empirical PSF model trained on
  >=3 **different** pre-registered source stamps from a single exposure.
- Added >=2 completely different whole-star holdout requirements, source-ID
  reuse and exposure-mixing vetoes, official deleterious ZTF pixel-mask
  handling, sky MAD/flux quality screening and strict centering constraints.
- Added an explicit diagonal CCD shot+read variance calculation in DN^2
  from caller-supplied, scientifically verified gain/read noise/sky.
- Added an empirical blank-sky aperture correlation diagnostic using
  >=16 independently identified, non-overlapping windows; it is not a
  full covariance or formal photometric uncertainty model.
- Added a public-only aggregate view that excludes private original
  pixels, identities and PSF arrays.
- Added 25 new parametrized synthetic/negative checks. **686/686
  automated tests passed** in [GitHub Actions](https://github.com/ismaelberja/stellarforge/actions/runs/42799842210).
- See [methodology](docs/PHASE119_EMPIRICAL_STAR_PSF_AND_CCD_NOISE.md),
  [Spanish guide](docs/PHASE119_GUIA_ES.md) and
  [synthetic CI report](reports/empirical_star_psf_v1.19/SYNTHETIC_VALIDATION_AND_REAL_DATA_GATES.md).

## What this does NOT establish

No original real ZTF science/mask pixel files were newly ingested during
v1.19; the independent-star empirical model has **NOT** been tested on
observations. Gaia/ZTF physical identity, original ZTF PSF-building
star membership, true detector WCS/PSF covariance, gain/read-noise
metadata and any astronomical discovery remain unverified. The underlying
DAOPhot original training roster was not recovered in v1.18.

v2.0 requires an honest software milestone: original exposure-level
larger vetted reference-star sets, truly disjoint empirical model
training/testing on real pixels, per-exposure detector noise metadata and
independent crossmatch/WCS checks. The source archive remains ephemeral;
only code, synthetic tests and bounded derived aggregates go to Git.
