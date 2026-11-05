# StellarForge v1.8 — Real Gaia DR3 reference candidates on ZTF science frames

**Evidence:** [successful real-data GitHub Actions run 42077605987](https://github.com/ismaelberja/stellarforge/actions/runs/42077605987), 5 November 2026. Accompanying short-lived aggregate-only JSON and Markdown are attached to the run. **All results are provisional engineering diagnostics, not a confirmed Gaia–ZTF source association, calibrated instrumental PSF, or complete WCS solution.**

## Provenance and independent Gaia DR3 candidate discovery

The original official IRSA/ZTF photometric acquisition was checked with its historical byte SHA-256, positional query and source-ID manifest: **2,212 raw positional-cone rows**, six OID/passband groups (FT Tau vicinity: 1,199 rows, CIDA 11 vicinity: 1,013 rows).

Two larger **210-arcsec-radius** Gaia DR3 TAP catalog queries were independently performed. All field Gaia sources were retained for isolation calculations. Quality/brightness/astrometry filters narrowed them to the following candidate references:

| Pilot target | Gaia sources returned (within 210″) | Quality-screened candidate references | Catalogued reference source IDs |
|---|---:|---:|---|
| FT Tau | 50 | 3 | 149623470751259776; 149623505110996992; 149625115720662528 |
| CIDA 11 | 250 | 5 (five-candidate budget) | 3419158043404221568; 3419111112297915264; 3419158047700527232; 3419109188152579584; 3419111520318480128 |
| **Total** | **300** | **8** | — |

The candidate requirements include **Gaia RUWE below 1.4, five/six-parameter astrometric quality, no duplicated_source flag, Gaia G magnitude 13–18.5 and isolation of at least 10 arcsec from the entire Gaia cone catalogue**. These requirements make the candidates useful for screening; they do **not** authenticate PSF purity, Gaia–ZTF source identity or lack of unresolved companions. Gaia G magnitudes are not calibrated ZTF g/r magnitudes.

## Genuine ZTF image checks from the same dated science product

The bounded pilot sampled one g-band ZTF OID per target (FT Tau OID 1605115300003377; CIDA 11 OID 610106300008010), two original independent dated science frames per target, **four real target science FITS images**, and **16 reference cutouts** from the same source FITS product paths. Each reference was centered at its Gaia-catalogue position propagated to that observation using approximate 2D proper motion. All raw Gaia TAP CSVs, original ZTF photometry and FITS pixels remained outside public Git; only image-quality/model summaries and hashes were exported.

- **4/4 target image Gaussian-proxy fits** succeeded, including fits flagged for image-model residual review.
- **13/16 Gaia reference candidate cutouts** produced usable bounded Gaussian-proxy centroid/shape results; three lacked a usable model or returned an image access failure.
- **3/4 tested science exposures** have at least three independently identified Gaia-reference candidate image fits and therefore permit a **provisional median east/north WCS translation proxy**. The other exposure had only one usable reference and **no** translation estimate.
- In all cases, **0 independent WCS calibrations**, **0 source identity confirmations**, and **0 validated empirical PSF models** are claimed.

## Provisional WCS-referenced offsets

These numbers are descriptive median offsets of quality-screened Gaia reference image Gaussian centroids relative to Gaia J2016 positions propagated by two-dimensional proper motion, using **the original (not independently calibrated) ZTF FITS WCS header**.

| Target | Target science MJD | Gaia references with usable models | Median East offset (″) | Median North offset (″) | Maximum deviation from reference median (″) |
|---|---:|---:|---:|---:|---:|
| FT Tau | 58388.389016 | 1 | — | — | insufficient |
| FT Tau | 58491.184780 | 3 | +0.08708 | +0.01267 | 0.09694 |
| CIDA 11 | 58475.113750 | 4 | +0.05232 | +0.05436 | 0.07827 |
| CIDA 11 | 58849.135984 | 5 | −0.00793 | +0.02166 | 0.06371 |

A follow-on descriptive calculation subtracts the reference median from each target's raw Gaussian fit residual. It produces target residual magnitudes of **0.09515″ (FT Tau, MJD 58491.184780)**, **0.08727″ (CIDA 11, MJD 58475.113750)** and **0.05728″ (CIDA 11, MJD 58849.135984)**. These values were derived from the archived v1.8 aggregate offsets; the routine is implemented and synthetic-tested in the v1.8 source module. **They are not independently validated astrometric accuracies or physical source displacements**, and the remaining original ZTF groups have not been checked with real references in this pilot.

In particular, **CIDA 11's own Gaia DR3 RUWE ≈ 8.57** was identified in the earlier Gaia-only audit. This indicates a potentially problematic astrometric fit and makes any physical interpretation of a small nominal centroid residual unjustified without further modeling. The selected reference candidates themselves have lower RUWE; that does not remove the target's uncertainty.

## Interpretation and limitations

- The five-candidate quota and one-band-per-target pilot do not constitute a complete field reference sample.
- Catalogue-filtered Gaia sources are **not instrumentally authenticated, isolated, single-star PSF standards**. The presence of Gaia astrometry and a local ZTF image peak does not independently verify their physical identity or deblend them.
- The fitted models are constrained single elliptical Gaussian image shape proxies with planar local backgrounds. Model residuals, PSF wings, colour effects and detector systematics remain uncalibrated.
- The derived median reference offsets are a *provisional local translation*, not a field-dependent distortion solution, an independent WCS recalibration or an astrometric uncertainty budget. High apparent precision of the reported decimals reflects numeric formatting, **not measurement precision**.
- Gaia positions are propagated only with 2D proper motion, omitting annual parallax, perspective acceleration, full position–proper motion covariance and atmospheric/chromatic systematics.
- The original input acquisition consisted of positional cone-query rows, not scientifically authenticated light curves. Only two of six ZTF OID/filter groups were included in the v1.8 image/reference pilot.
- Public IRSA service failures, insufficient reference stars and unsuccessful image fits are **not astrophysical non-detections**.

## Engineering verification

The pre-pilot v1.8 image/catalogue and uncertainty gate regression suite passed **420 automated tests**. Subsequent source additions implement the target-minus-reference diagnostic and its synthetic tests; the final GitHub Actions run on the integrated v1.8 main branch is the authoritative version-wide test count.

**Next gate:** independent empirical ZTF stellar PSF calibration, full Gaia DR3 astrometric uncertainty/parallax-aware propagation and vetted multiple-exposure WCS residuals, especially for high-RUWE CIDA 11. Only then revisit source identity, photometric variability and astrophysical models.

**Confirmed Gaia–ZTF physical identifications: 0. Independently calibrated WCS solutions: 0. Validated empirical PSFs: 0. Proven unblended stars/companions/new physical events: 0.**
