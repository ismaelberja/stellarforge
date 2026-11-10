# StellarForge v2.0.0 — Engineering portfolio release

**Date: 10 November 2026**

## Scope

A research-grade **software engineering deliverable** showcasing
astronomy data ingestion, data quality, reproducibility and
transparent scientific validation. It is **not** a survey-science
release, a new companion discovery or an independent PSF calibration.

## Release changes

- A compact and accessible main README, with the complete historical
  42-kB v1.22 README preserved at docs/HISTORIC_README_v1.22.md.
- An explicit no-raw, versioned `RELEASE_MANIFEST_v2.0.json`
  tracking which counts derive from real original observations,
  which are synthetic tests, and which astrophysical claims
  remain unconfirmed.
- Offline fail-closed release evidence checker and adversarial tests
  that reject altered science counts, missing provenance and
  unsupported independent calibration/discovery claims.
- Complete reproducibility/runbook and a Spanish onboarding guide.
- Concise, evidence-grounded CV/LinkedIn-ready text in ES/EN
  (no external profile updates).
- Normalized CLI wording, package version 2.0.0, traceable release
  metadata, and GitHub CI gates.
- Original SHA-checked IRSA source files remain private and excluded
  from Git. No proprietary unpublished ALMA/TFM sources are added.

## Historical real scientific engineering evidence retained

- 532 Taurus members in secondary Luhman (2023) catalogue mirror;
  467 Gaia identifiers; a selected nonrepresentative 24-target seed.
- 2,212 original IRSA positional photometry rows; six separate
  ZTF OIDs across two technical target fields.
- Four historical original g-band science exposures, four
  original spatial DAOPhot model central-profile checks.
- 16 original masked science-image PSF model fits; 13
  provisional same-source checkerboard residual screens passed,
  3 flagged for noncommittal investigation.
- Historic original two-target IRSA ZIP retained privately
  with hash matching GitHub Actions metadata.

These do NOT prove physical Gaia/ZTF source identity, independent
absolute WCS/PSF instrument calibration, physical stellar
variability or new companions.

## Software verification

v1.22 main branch: **752 tests passed** in GitHub Actions
run https://github.com/ismaelberja/stellarforge/actions/runs/42809011151.

v2.0 adds release-claim consistency tests. The release is accepted
only after its own final-commit main CI also passes. Synthetic
pass counts do not measure physical survey-model correctness.

## Open science after software release

The original strict seven-star CIDA 11 whole-star empirical PSF
live pilot has **not been run**. Original ZTF DAOPhot PSF-model
training-star roster, independent source matches, exposure
CCD-noise/WCS calibration and the three v1.16 high residuals
remain open research tasks.

A software portfolio can be complete while an astrophysical
research hypothesis is still inconclusive.

## Navigation

- README.md
- EMPEZAR_AQUI.md
- docs/V2_GUIA_ES.md
- docs/V2_REPRODUCIBILITY_AND_SCIENCE_LIMITS.md
- docs/V2_PORTFOLIO_CV_ES_EN.md
- RELEASE_MANIFEST_v2.0.json
- docs/HISTORIC_README_v1.22.md
