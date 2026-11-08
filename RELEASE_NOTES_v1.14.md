# StellarForge v1.14 — Official original ZTF PSF-fit catalogue and spatial DAOPhot source candidate audit

**8 November 2026 · Observed-data scientific Python milestone.**

## Engineering changes

- Downloaded and parsed **four full original ZTF `psfcat.fits` native single-exposure PSF-fit FITS catalogues** under official IRSA path, strict HTTPS/host/suffix checks, bounded payload sizes and complete field/CCD/QID provenance.
- Applied separately propagated **Gaia DR3 exact 5D correlated formal astrometry and Earth-geocentric annual parallax** to two technical targets and eight originally selected reference candidates at four original exposure MJDs.
- Implemented conservative nearest-native-PSF-source candidate quality screens on official `sourceid, xpos, ypos, ra, dec, flux, sigflux, snr, chi, sharp, flags`: ≤1″ provisional sky separation, SNR≥5, `chi` 0.5–1.5, `sharp` −0.5..+0.5, and no documented ZTF 6141 disqualifying flags; block ambiguous duplicate source-ID assignments and review catalogued neighboring PSF detections within 3″.
- Retrieved and SHA-checked all four original **`sciimgdao.psf` spatial DAOPhot model lookup files**. **These are not yet decoded or evaluated** at the individual original native detector coordinates, so no local PSF calibration is claimed.
- Added malformed FITS, source reuse/ambiguity, poor profile/flags, no counterpart, empty catalogue, forged host/redirect, oversized file and HTTP503 safeguards. Raw ZTF native FITS catalogs/DAOPhot and Gaia CSV remain transient; public output is a small derived audit only.

## Live original-data results

[Official observed-data GitHub Actions run](https://github.com/ismaelberja/stellarforge/actions/runs/42513198605) passed **564 automated tests** and successfully parsed **four native catalogues totaling 27,207 PSF-fit extraction records**, with **20 Gaia target/reference position checks** on the same four historic dated science exposures.

- **16 of 20** provisional native PSF source candidates passed conservative positional, shape and flag screens; this comprises **three of four target positions** and **13 of 16 reference-position checks**.
- **Three** candidate PSF fits had `chi < 0.5` and require quality review; **one** historical FT Tau reference had no native PSF catalogue entry near the requested position.
- Separations for the 16 provisional positions ranged **0.032641″–0.345256″**, median **0.1258465″**. The separation is NOT calibrated WCS precision or a verified physical source displacement.
- **Four of four** original full `sciimgdao.psf` DAOPhot spatial products downloaded, each 88,465 bytes, **not decoded** or checked as a local PSF. No PSF catalogue/archive HTTP503 occurred in this bounded run.
- No second catalogue PSF source appeared within the 3″ crowding radius for the nearest matched candidates, but **this does not eliminate unresolved or unreported contaminants**.

Read the [detailed original ZTF science evidence](reports/native_psfcat_v1.14/REAL_ZTF_GAIA_PSF_CATALOGUE_EVIDENCE.md) and [method and limitations](docs/PHASE114_NATIVE_PSF_CATALOGUE_AND_SPATIAL_MODEL_GATE.md).

## Scientific integrity and next gate

A `psfcat` source counter is **per exposure**, not Gaia's source ID nor a multi-epoch ZTF source identity. A native PSF fit near a Gaia-predicted location is not a physical crossmatch or a clean single-star certification. The ESA Gaia DR3 CIDA 11 target retains high RUWE ≈8.57; astrometric-model and instrument systematics are not included in the tiny Gaia-only formal covariance. Pixel masks, WCS distortion, differential colour, real source crowding and source identity remain open.

**Next gate:** decode and evaluate the actual DAOPhot spatially varying original PSF file on native CCD-quadrant coordinates (`xpos/ypos`), cross-check against same-exposure FITS science pixels and mask bits, and establish independent held-out reference-star astrometric/photometric uncertainty. Until then: **0 authenticated Gaia–ZTF source identities, 0 calibrated local PSFs, 0 independent detector WCS error budgets, 0 newly confirmed physical companions or variability events.**
