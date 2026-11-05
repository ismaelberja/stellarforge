# StellarForge v1.7 — Real ZTF same-image control search and two-epoch consistency

**Observed on 5 November 2026 in [GitHub Actions run #42058770141](https://github.com/ismaelberja/stellarforge/actions/runs/42058770141).**

**Scientific state:** engineering/observational diagnostics only. None of the six ZTF OID/band groupings is independently certified as a Gaia star, no scene is certified as unblended, and no physical companion or variability event is confirmed.

## Source provenance and real FITS acquisition

Two original SHA-verified official IRSA ZTF positional cone queries contain **2,212 photometric rows** around FT Tau and CIDA 11. They remain *positional candidate responses*, not independently authenticated stellar light curves.

This v1.7 run used **90-arcsec square FITS cutouts** and **stratified science-exposure choices** within each of six original ZTF OID/passband groups. Of **14 remote image requests**, **12 individual science FITS images** passed the provisional 2D celestial WCS and normalized radial-profile screens; two failed with **URLError**, rather than astrophysical non-detections. Every group now has **two distinct SHA-verified science FITS files**, and no reference coadd needed to be substituted.

The images were processed **only in ephemeral runner memory**; their pixels were not added to Git or published in artifacts. The [temporary aggregate-only artifact](https://github.com/ismaelberja/stellarforge/actions/runs/42058770141) contains detailed FITS SHA-256, WCS/shape status and errors, not raw images or raw photometry.

## Descriptive per-OID two-frame comparison

The quoted positional differences compare **two Gaussian-proxy centroid offsets relative to each FITS header WCS and its nominal Gaia-propagated coordinate**, not independently remeasured source motions. The methods use the existing simplified 2D Gaia proper-motion propagation and do **not** incorporate full parallax/covariance or field-star WCS calibration.

| Cone target | ZTF OID | Band / ZTF field | FITS science frames | Time separation (days) | Difference between nominal WCS residual vectors (arcsec) |
|---|---|---|---:|---:|---:|
| FT Tau | 1605115300003377 | g / 1605 | 2 | 102.80 | 0.03552 |
| FT Tau | 1605215300005161 | r / 1605 | 2 | 306.12 | 0.04810 |
| FT Tau | 609108400001155 | g / 609 | 2 | 704.97 | 0.05452 |
| FT Tau | 609208400001969 | r / 609 | 2 | 440.92 | 0.02351 |
| CIDA 11 | 610106300008010 | g / 610 | 2 | 332.10 | 0.09672 |
| CIDA 11 | 610206300011997 | r / 610 | 2 | 413.88 | 0.07017 |

**Interpretation:** the measured *relative residual-vector differences* are between approximately **0.024″ and 0.097″**, but these are not astrometric accuracy estimates, calibrated physical proper motions, or confirmation that a ZTF identifier belongs to the Gaia source. Correlated WCS errors, PSF bias and a constrained Gaussian optimizer may lead to deceptively small residuals.

## Same-field image-shape controls: limitation identified

The 90-arcsec cutouts were independently searched for bright, separated **unclassified image maxima** at least 13 pixels from the target. Each control would require isolated location, valid local annular background and a normalized six-ring radial profile. A target-to-control descriptive shape comparison requires **at least two valid candidate peaks in the same frame**.

| Result | FT Tau | CIDA 11 | Total |
|---|---:|---:|---:|
| Valid science-image radial screens | 8 | 4 | **12** |
| Frames containing >=2 usable unclassified field peaks | 0 | 0 | **0** |
| Frames with precisely one usable unclassified field peak | 0 | 4 | 4 |
| Frames with no usable unclassified field peaks | 8 | 0 | 8 |

**A zero count of usable control peaks does not imply an empty sky field.** These are relatively small, selected science cutouts, the test is deliberately strict, and some faint/unresolved sources or nebular features could remain unseen. No empirical PSF calibration or confirmed blending exclusion was therefore possible in v1.7.

The auxiliary single-Gaussian-plus-plane proxy produced **11 fits flagged for PSF residual review and 1 provisional fit** (the latter on CIDA 11 g). A large residual can result from an ordinary ZTF stellar PSF differing from a Gaussian. Neither a bad nor good Gaussian fit proves the existence or absence of companions.

## What has actually improved since v1.6

- v1.6 produced **three FT Tau individual science-image Gaussian proxy fits**, zero independent repeated science series, and no successful CIDA 11 image fits.
- v1.7 produced **twelve individual science-image screens**, four FT Tau pairs and two CIDA 11 pairs, without relying on coadds. This enables **descriptive two-epoch calculations**, but it **does not** establish calibrated multi-epoch astrometric stability.
- Expanded view to 90″ to search candidate same-field controls, documenting the precise reason the empirical PSF calibration remains **not feasible** under current strict controls.
- No original ZTF CSV or FITS pixel matrix was committed to the public repository.

## Validation and remaining scientific gates

**400 of 400 synthetic/offline unit and integration tests** passed in the real-data run, together with the separate SHA-checked observational analysis.

Still required:
1. Independent Gaia–ZTF source identity and epoch-dependent WCS recalibration against *authenticated comparison stars*; CIDA 11 has Gaia RUWE approximately **8.57**.
2. Authentic same-field stellar controls (potentially wider images, source catalogs, larger sample and photometric quality filters), field-dependent empirical ZTF PSF modeling and detector masks.
3. Full source/background/PSF deblending and uncertainty propagation, with image registration and multi-epoch calibration before any interpretation of positional differences.
4. Original publisher Taurus catalog comparison and independent disk class confirmation before physical variability or selection-function inference.
5. Cautious archive request scheduling and retries; errors from remote services are not negative observational evidence.

**Confirmed Gaia–ZTF physical source matches: 0. Verified unblended targets: 0. Physical new variability events: 0.**

## Reproduction

Install the optional test, analysis and image dependencies, run the offline regression tests, then invoke:

    python scripts/run_v17_field_controls.py /path/to/official_original_IRSA_photometry.zip --science-attempts 6 --timeout 5 --fail-if-no-science

For the exact ZTF image URL patterns, consult the [official IRSA ZTF API documentation](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_api.html). The archived original acquisition artifact is temporary; if unavailable, reacquire observations through the official API and generate a new versioned provenance/hashes ledger rather than substituting undocumented data.
