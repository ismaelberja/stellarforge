# StellarForge v1.20 — Preregistered original ZTF star-cohort pipeline

**10 November 2026. Validated scientific software, NOT yet a new real-data result.**

## Delivered

- Deterministic **strict Gaia-only** seven-source CIDA 11 cohort,
  allocated **4 empirical PSF training / 3 distinct whole-star holdouts**
  before opening any original ZTF source catalogue or pixels.
- Exact original ZTF dated-exposure reconstruction and conservative
  "psfcat.fits" source quality checks, with fixed group assignment.
- Same-exposure original source FITS/bitmask extraction with
  science/mask celestial WCS, native detector phase, saturation,
  bilinear interpolation and post-registration centroid-proxy gates.
- Integration with the v1.19 different-star empirical PSF model only
  if at least **3/4 predeclared training** and **2/3 predeclared
  held-out** stars survive all original image eligibility tests.
- A manual-only original Gaia/IRSA GitHub Actions workflow and
  public-count/hash-only reports; no automatic real archive activity.
- Synthetic and adversarial FITS/WCS, duplicate, mask, source-selection,
  and original-data workflow fail-closed tests.
- English scientific protocol, Spanish instructions and updated
  repository status/roadmap.

## Evidence and limitations

The automated GitHub Actions regression suite is **synthetic/offline**.
**The manual v1.20 original-data workflow has NOT yet run**, so no
real same-exposure 3+2 holdout result is claimed for this release.
v1.18 original DAOPhot training-star rosters remain unknown; ZTF
native PSF-fit source-selection introduces dependencies on original
pipeline source profiles. Bilinear interpolation correlates pixels,
and detector gain/read-noise/covariance need verified external
instrument metadata. No calibrated PSF/WCS precision, confirmed
physical Gaia/ZTF match, companion or physical stellar variability
is established.

Methodology: docs/PHASE120_ORIGINAL_REGISTERED_STAR_COHORT.md

Spanish guide: docs/PHASE120_GUIA_ES.md

Manual workflow: .github/workflows/v120-original-empirical-psf-pilot.yml
