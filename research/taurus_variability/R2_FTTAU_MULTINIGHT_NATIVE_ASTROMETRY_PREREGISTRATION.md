# Taurus R2 — preregistration: FT Tau independent-night native ZTF source positions

**12 November 2026. Protocol committed before the new original-data multi-night job.**

## Aim and fixed identity

Extend the completed four-image Gaia/PS1/ZTF original source-position study (PR #43) without selecting new images based on whether they appear to align with Gaia. FT Tau is the existing provisional technical target, with **Gaia DR3 149623711269425408**, and the original **24-source nonrepresentative Taurus seed** remains unchanged. The four original ZTF ObjectIDs and the previously frozen original g/r field 1605 CCD15 Q3 / field 609 CCD8 Q4 exposures are unchanged. This is **not** a new source discovery or a proven physical Gaia–ZTF counterpart.

## Prospective deterministic new-epoch selection

1. Retrieve the exact four original IRSA ZTF ObjectID CSV tables (same frozen OIDs, bands, CCDs, field and quadrants), applying the existing metadata validity and 32768 catflags rejection. Preserve original source table SHA-256, eligible-row counts and rejection summaries, but never commit raw rows, source magnitudes, or light curves.
2. For **each of the four fixed band/field/OID strata separately**, remove only the exact one original exposure already used by PR #43. Group the remaining eligible exposures by integer MJD (UTC observing dates), retaining the **earliest MJD per UTC night**. Before looking at any image, choose the first and last night chronologically; both must differ by **at least 30.0 days**. If not, mark the stratum UNDERPOWERED. Do not replace unavailable/poor-quality frames or choose image epochs based on source offsets, brightness, PSF fit, seeing or visual appearance.
3. At most **eight new original native full ZTF psfcat.fits files** (two dates × four fixed strata). Recover by the same official ZTF image-product URL derivation as the previous real original study, hash each original byte stream and parse the native PSF catalogue transiently in memory. The prior four catalogues are not replaced, and may be used only as documented historical controls.
4. Fetch the exact Gaia DR3 5-parameter FT Tau record and formal covariance; propagate from Gaia J2016.0 to the selected MJD with the **existing approximate geocentric-parallax method**. For each preselected ZTF catalog, apply the existing *fixed* nearest-source radius 0.6 arcsec, second-source separation >1 arcsec and native PSF flag/chi/sharp/SNR screens without substitutions.
5. Describe, per stratum, the early and late native-minus-predicted-Gaia sky offsets and their **difference in east/north arcseconds**, only when both preselected original catalogue candidates pass. Record actual temporal baseline. Even if two frames agree, this is **not an independently calibrated proper-motion detection** or a statistically significant physical association. Per-frame astrometric covariance, reference-star corrections, PS1 source-specific mean epochs, blending and source-population completeness are not available in this stage.

## Failure, interpretation and outputs

- A failed original server request is an observational **UNAVAILABLE** or **UNRESOLVED**, never an astrophysical nondetection. An underpowered stratum stays underpowered, even if nearby unchosen exposures exist.
- Record only source hashes, fixed OIDs, observational MJDs, total/eligible counts, derived nearest/second-nearest source separations, native-minus-Gaia offsets, quality flags, error types and limitations. Do not archive raw catalogue rows, positions of other stars, images, magnitudes or time series.
- An exact-archive metadata payload SHA change is explicitly noted as an independently retrieved snapshot, not a byte-identical repeat.
- Preserve **zero confirmed physical Gaia–ZTF counterparts**, **zero merged OID light curves**, **zero confirmed new variables/companions**. R2 remains open and R3 astrophysical variability inference remains blocked. Multi-epoch agreement is necessary evidence toward stronger source identification, not sufficient proof.

Deliverables: reproducible method in src/stellarforge/r2_fttau_multinight_astrometry.py, command-line runner, tests and original-data GitHub Actions experiment. Original MAST/PS1 DR2 geometry and the 2018/2019 four-image positional results remain unchanged.

Original instrument conventions: [ZTF science products](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_api.html), [Gaia DR3 original source astrometry](https://gaia.aip.de/cms/data/gdr3/).

**Predefined acceptance:** correctly selected real independent nights and honest source-candidate status reporting; *not* declaration of FT Tau physical identity or new variability.