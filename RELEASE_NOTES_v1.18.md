# StellarForge v1.18 — Verified original ZTF PSF reduction logs and FT Tau exploratory masked field-source controls

**9 November 2026. Engineering/observational milestone.**

## Technical advance

The project now retrieves authentic original **`sciimlog.txt` and `log.txt` archived processing logs** for the four historical dated ZTF g-band science exposures already studied in FT Tau and CIDA 11. Its hardened original IRSA HTTPS/product parser reads logs only from the exact same original dated science pathname, caps log bytes/timeouts, rejects untrusted redirects, archives **only SHA-256 and bounded derived metrics**, and explicitly distinguishes **a general reference to PSF processing from a documented source-level PSF-training star roster**.

**Real archival result:** **8 of 8** original ZTF processing logs retrieved and parsed, with 115–116 PSF/DAOPhot-referencing lines per original `sciimlog.txt`; no original full DAOPhot PSF-training star source-ID roster could be authenticated. A ZTF `psfcat.fits` native source counter identifies later **PSF-fitted catalogue detections**, not which stars trained the original PSF. No Gaia source ID has therefore been independently certified as excluded from the original ZTF model.

The other advance is a predeclared, separate **exploratory** Gaia DR3 FT Tau source-quality tier after v1.17 strict Gaia quality/isolation screening returned zero new FT Tau controls. **Strict conditions are rerun unchanged and remain zero** on the fresh 50-source Gaia wide cone; the exploratory tier is wider in G magnitude, RUWE, Gaia-isolation and target offset (criteria published before any current ZTF pixel fitting), never claimed equivalent to the original strict controls.

- **Four previously unused Gaia DR3 FT Tau source IDs** selected by the exploratory fixed Gaia-only design; none was among the ten v1.8–v1.16 technical target/reference IDs.
- Of **eight original source×epoch native PSFfit candidate screens**, one new Gaia ID **149623298952568064** was eligible and fitted on **both** historical original FT Tau ZTF science exposures. The model was applied to genuine WCS-aligned original **`sciimg.fits` + `mskimg.fits` source pixels**, fitted in uncalibrated detector DN with fixed spatial DAOPhot PSF/sky plane.
- Two original masked PSF image fits passed provisional SAME-IMAGE held-out-pixel residual screening (RMS/sky MAD **0.920302** at original MJD 58388.389016, **0.955383** at MJD 58491.184780); **one distinct source, two epochs**, not two independently withheld PSF-training stars. Six candidate×epoch positions remained native catalogue ineligible/review; no star absence inferred.
- **Thirty-two** preregistered fixed ±25″ shifted sky/source-catalog positional checks returned **zero** ZTF PSFfit sources within 1″, a descriptive local match-density check, not a probability.
- The [official real original-data GitHub Actions execution](https://github.com/ismaelberja/stellarforge/actions/runs/42665465964) passed **661 synthetic and integration tests** and retrieved all 8 original logs without 503.

[Detailed original survey PSF-training audit and FT Tau results](reports/psf_training_ft_tau_v1.18/REAL_ZTF_LOG_AUDIT_AND_EXPLORATORY_FT_TAU.md) · [Exact observational methodology and strict/exploratory source quality tiers](docs/PHASE118_PSF_TRAINING_LOGS_AND_EXPLORATORY_FTTAU.md).

## Scientific limitations

A readable archived processing log is **not** a proof of independent original PSF training-star exclusion; ZTF source catalogue entries do not provide a complete model-training roster. The new FT Tau sample uses **explicitly less stringent exploratory** Gaia selection, could contain blends/crowding or real background contaminants, and has only **one distinct** original source with two masked-pixel fits. The PSF shape and source position derive from the original ZTF pipeline; the checkerboard validation excludes only **other pixels of the same source image**, not stars withheld from original DAOPhot PSF construction. No independent local PSF/WCS or astrophysical crossmatch calibration, physical variability, binary, companion or survey selection efficiency is claimed.

Original ZTF/Gaia photometry, raw pipeline logs, FITS science/mask detector pixels, `psfcat` binary table contents and DAOPhot coefficients remain transient; published files contain code, synthetic tests, source hashes and derived quality metrics only. The live external archive workflow is manual-only following its real-data pilot.

**Next:** seek a genuine original ZTF PSF-building star support roster or independently refit a PSF from a demonstrably separate sample; gain more FT Tau and CIDA 11 source/date/filter coverage, perform realistic correlated CCD noise and WCS error validation, then close a transparent scientific-software v2.0 without overstating astrophysical conclusions.
