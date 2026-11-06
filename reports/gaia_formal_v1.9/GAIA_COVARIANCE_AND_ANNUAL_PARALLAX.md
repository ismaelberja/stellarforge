# StellarForge v1.9 — Real Gaia DR3 formal covariance and annual geometric parallax

**Observed 6 November 2026 · Verified real-data workflow:** [GitHub Actions run 42175644367](https://github.com/ismaelberja/stellarforge/actions/runs/42175644367). The workflow was independently successful with **444 automated tests** and two exact Gaia DR3 source queries.

**Scientific status:** derived geometric positional and formal covariance quantities for *Gaia catalogue sources*, **not source identities in ZTF**, a calibrated imaging WCS, PSF, deblending result, physical motion or astrophysical detection.

## Real official catalogue measurements

Gaia DR3 table `gaiadr3.gaia_source` was queried for **exact source IDs**, retaining both the five astrometric parameters with **all ten cross-correlations** and the original RUWE. The original ZTF science exposure MJDs below are taken from the documented v1.8 real-image pilot; their time scale is **assumed UTC provisionally**, not independently checked from FITS exposure metadata.

| Target (provisional ZTF association) | Gaia DR3 source ID | Gaia parallax (mas) | Gaia RUWE |
|---|---|---:|---:|
| FT Tau | 149623711269425408 | 7.68122 | 1.32659 |
| CIDA 11 | 3419110734340795648 | 5.99431 | **8.56752** |

## Annual parallax correction and formal Gaia covariance at real epochs

The table shows the first-order Earth-geocentric geometric annual parallax difference relative to an otherwise identical **linear 2D proper-motion-only** Gaia position prediction. This is not an observed ZTF displacement. All numerical uncertainties below are the propagated **formal Gaia five-parameter catalogue covariance**, not ZTF measurement error bars.

| Target | ZTF MJD (assumed UTC) | Annual shift East (mas) | Annual shift North (mas) | Gaia-only formal σ East (mas) | Gaia-only formal σ North (mas) |
|---|---:|---:|---:|---:|---:|
| FT Tau | 58388.389016 | +6.79131 | +1.31775 | 0.07261 | 0.04928 |
| FT Tau | 58491.184780 | −4.78081 | −0.44223 | 0.07005 | 0.05519 |
| CIDA 11 | 58475.113750 | −1.36208 | +0.04316 | 0.44395 | 0.27247 |
| CIDA 11 | 58849.135984 | −2.25027 | −0.04788 | 0.58458 | 0.37003 |

The signed parallax shifts change with epoch; a single constant offset is **not** a substitute for an epoch-aware position model. Some corrections of a few mas are much larger than the Gaia-only formal catalogue sigma, but **this does not mean the ZTF imaging instrument is accurate to sub-mas levels**. The provisional median ZTF/Gaia image residuals in v1.8 were of order 0.05–0.1 arcsec and lacked a full instrumental calibration.

**Special caution — CIDA 11:** Gaia's RUWE ≈ 8.57 indicates a problematic single-source astrometric solution. Its quoted formal covariance may **seriously understate real source-position/model uncertainties**, and no inference of binarity, photometric contamination or clean source identity follows from RUWE alone.

## What was actually modeled

- Public Gaia DR3 five-dimensional covariance using all ten off-diagonal correlations, with the five position/parallax/proper-motion uncertainties in the original catalogue units. Invalid/missing correlations and inconsistent non-positive-semidefinite covariance are rejected.
- Linear proper motion including Gaia's `pmra` (μα*, i.e. RA motion times cos declination), to each recorded epoch. First-order geometric Earth-centre annual parallax computed with Astropy's **built-in offline Earth barycentric ephemeris**.
- Formal two-dimensional east/north covariance via deterministic central-difference Jacobian `J C J^T`. Full numerical 2×2 covariance matrices are provided in the **aggregate-only JSON artifact**, not the raw Gaia TAP CSV.

## Unresolved systematic uncertainties

- Gaia DR3 five-parameter **formal** covariance is **not total on-sky uncertainty**, especially if the target has non-single-star motion, high RUWE, excess noise or color calibration issues.
- The model is **geometric geocentric**, not an accurate topocentric apparent coordinate including aberration, refraction, optical distortion, Gaia radial velocity/perspective or actual Palomar telescope location.
- It treats listed ZTF MJDs as UTC and has not independently checked FITS time headers or ZTF absolute timing convention at the specific exposures.
- If a Gaia 6-parameter solution is present, the propagated 5×5 astrometric submatrix excludes pseudocolour-specific modeling.
- ZTF WCS, field-dependent PSF/centroid, image noise, background, source blending and image-source association have **not** been calibrated.
- No statistically significant physical displacement, new companion, stellar class, disk variability, physical event rate or detection has been established.

## Reproduction and original sources

The code is in [`src/stellarforge/v19_gaia_covariance.py`](../../src/stellarforge/v19_gaia_covariance.py) with synthetic/offline tests and a short official-TAP pilot script [`scripts/run_v19_gaia_formal.py`](../../scripts/run_v19_gaia_formal.py). It queries only two exact Gaia DR3 IDs, needs no original ZTF FITS/CSV inputs, and publishes only derived aggregate JSON/Markdown.

Run:

    python -m pip install -e '.[test,analysis,images]'
    python -m pytest -q
    python scripts/run_v19_gaia_formal.py

- [ESA Gaia DR3 `gaia_source` schema](https://gea.esac.esa.int/archive/documentation/GDR3/Gaia_archive/chap_datamodel/sec_dm_main_source_catalogue/ssec_dm_gaia_source.html)
- [Astropy built-in Earth barycentric ephemeris documentation](https://docs.astropy.org/en/stable/api/astropy.coordinates.get_body_barycentric.html)
- [Observed v1.8 provisional reference image offsets](../gaia_reference_v1.8/REAL_REFERENCE_CANDIDATE_EVIDENCE.md)

**Confirmed Gaia–ZTF astrophysical identifications: 0. Independently calibrated ZTF WCS/PSF models: 0. New physical events or companions: 0.**
