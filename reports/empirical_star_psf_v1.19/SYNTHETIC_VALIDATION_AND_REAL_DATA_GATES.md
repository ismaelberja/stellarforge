# StellarForge v1.19 — Synthetic empirical PSF and detector-noise gates

**Verification date:** 10 November 2026

**Evidence category: SYNTHETIC SOFTWARE TESTS ONLY.**
**NO new original ZTF FITS, Gaia TAP sources or detector images were retrieved
or independently validated in this release.**

## CI verification

The [GitHub Actions v1.19 source-and-tests branch run](https://github.com/ismaelberja/stellarforge/actions/runs/42799842210)
completed with **686/686 Python tests passing** (25 parametrized test cases
more than v1.18's 661). The CI run includes the existing observational
intake validators and the new v1.19 deterministic synthetic fixtures.
Passing CI does not mean that the v1.19 independent-star model was applied
to a real ZTF exposure.

## Functionality implemented and checked

| Testable gate | Synthetic outcome |
| --- | --- |
| Three or more distinct training stars and two or more held-out stars | Functional; rejects undersized sets |
| Cross-sample Gaia-source reuse, including an old source at a different epoch | Rejected |
| Mixed science-exposure input | Rejected |
| Source and official ZTF bitmask geometry; dangerous masked core | Validated / unsafe input rejected |
| Invalid saturated/negative/fractional/nonfinite mask values | Rejected |
| Registration residual greater than 0.08 pixel | Rejected |
| Fresh empirical pixel PSF from training-star pixels only | Functional on simulated star images |
| Model tested against whole **different** synthetic star images | Held-out residuals computed; deliberately broadened profile flagged |
| CCD Poisson source + sky + read variance in original DN units | Unit-tested |
| Empirical aperture variance inflation from correlated blank-sky windows | Distinguishes correlated from independently sampled synthetic windows |
| Public output | Count-only whitelist excludes images and Gaia IDs |

The new synthetic PSF algorithm is not trained on ZTF's original DAOPhot
spatial coefficients. This is **an independence property of the new
algorithm and synthetic training/test separation**, not authenticated
exclusion of the stars from ZTF's own historical calibration sample.

## Previously established original-data facts (unchanged)

- Four original historical FT Tau/CIDA 11 ZTF g-band frames and masks were
  studied in v1.15–v1.18.
- The official ZTF PSF training-star membership roster remains **UNKNOWN**.
- The additional FT Tau exploratory source was one distinct candidate
  with two epochs, **not two distinct stellar calibrators**.
- No independently calibrated ZTF PSF/WCS uncertainties or authenticated
  physical Gaia–ZTF crossmatches have been established.

## Blocker / next real-data gate

At least three suitably isolated, independently registered training stars
and two separate stars for holdout within the **same original exposure**,
plus reliable science/mask provenance and vetted original CCD parameters,
are needed before v1.19 can be run as genuine independent-star data
analysis. The previous validated rosters did not establish this coverage.

No new detections, physical variability, companions or source identities
are claimed, and original archive pixels remain outside the public repo.
