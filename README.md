# StellarForge

**Scientific Python · Time-series analysis · Data engineering · Reproducible research**

[![Python tests](https://github.com/ismaelberja/stellarforge/actions/workflows/tests.yml/badge.svg)](https://github.com/ismaelberja/stellarforge/actions/workflows/tests.yml)
[![Project status](https://img.shields.io/badge/status-active%20research-blue)](docs/PROJECT_STATUS.md)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)

StellarForge is an evolving scientific-software project for **processing multi-survey astronomy data and investigating stellar variability**. It focuses on traceable data ingestion, observation-quality controls, irregular time-series analysis, and carefully qualified source associations.

**Created and scientifically directed by Ismael Berja Ruiz**, with AI-assisted software development and human review of scientific methodology.

> **Research status (v1.13, November 2026):** Working code, official ZTF *position-query responses* and reproducible Gaia/ZTF positional and independent Gaia-field screening are available. The Gaia–ZTF astrophysical identities and any physical variability events **have not been independently confirmed**. This is a software/research portfolio project, **not an announcement of an astronomical discovery**.

## At a glance

| Engineering result | Verified scope |
|---|---|
| **533 automated tests passed** | GitHub Actions v1.13 official ZTF detector mask and native field-center PSF pilot (8 November 2026) |
| **2,212 real photometric rows retrieved** | Two official IRSA cone searches around published positions for FT Tau and CIDA 11, **not yet authenticated as those stars** |
| **Six ZTF object identifiers** | Kept separate by source ID, filter and field rather than blended |
| **Two independent Gaia DR3 15″ field audits** | No *additional catalogued Gaia* sources returned near either target; unresolved companions are not excluded |
| **Real FITS pixel/WCS screening** | Five of six ZTF OID-band groups were screened in v1.5; no identity or blend clearance claimed |
| **Multi-epoch real-image evidence** | 12 individual ZTF science FITS images processed in v1.7, two distinct epochs in every OID/band group; no calibrated source identity |
| **Gaia-backed ZTF reference pilot (v1.8)** | 8 catalogue-screened Gaia reference candidates, 13 real FITS reference-image model fits; provisional local translations in 3 exposures, no full WCS calibration |
| **Formal Gaia 5D uncertainty + annual parallax (v1.9)** | All ten Gaia cross-correlations propagated at four actual observation dates for two DR3 sources; not a ZTF astrometric error budget |
| **Gaia reference-image holdout QA (v1.10)** | 13 archived real reference models, four science exposures; 3 inclusive / 2 strict holdout-eligible; no calibrated WCS |
| **Per-reference annual parallax + Gaia 5D formal covariance (v1.11)** | 8 candidate Gaia references plus two targets, 13 original image-model offsets reassessed: minor LOO RMS changes but still no independently calibrated ZTF WCS |
| **Original science FITS image remeasurement (v1.12)** | Two 20-request runs on the same epochs: initial 9 complete fits/9 HTTP 503; finalized 12 complete fits (1 target, 11 references), 9 provisionally model-consistent references, 8 HTTP 503; no calibrated instrument PSF/WCS |
| **Official ZTF bad-pixel masks and native center PSFs (v1.13)** | 20 source positions screened: four reference-source masks WCS-aligned to genuine science FITS with no 6141 disqualifying core bits, 16 HTTP 503; 2 of 4 real 23x23 science-field-center PSF stamps parsed, neither target mask validated |
| **532 Taurus catalog members audited** | Pinned third-party Luhman (2023) Table 2 mirror; original publisher-file comparison pending |
| **24-star technical pilot** | Real published coordinates, not a representative or disk-classified scientific population |

The official requests and SHA-256 checksums are documented in the [v1.2 observational transport audit](reports/observational_intake_v1.2/RAW_TRANSPORT_AUDIT.md). The [v1.3 provisional astrometric report](reports/astrometry_v1.3/PROVISIONAL_POSITIONS_REPORT.md) finds median epoch-corrected Gaia/ZTF position separations of 0.063–0.092 arcsec across six curves, **without confirming any astrophysical source identity**. **Raw ZTF downloads and private research artifacts are not committed to Git.**

## v1.13 — official ZTF detector masks and native field-center PSF products

The real-data workflow now reads original NASA/IPAC ZTF **`mskimg.fits` detector bad-pixel masks** paired with the **same dated `sciimg.fits` cutout**, requiring identical pixel shapes and **independently checked celestial WCS grid registration** before interpreting pixel flags. The official disqualifying bit template is **6141**; extracted-source markers (bits 1 and 11) are not detector-defect flags. It also parses original **`sciimgdaopsfcent.fits` field-center PSF stamps** (not local star-specific PSFs), without placing raw FITS arrays in the public repository.

The [official observed-data pilot](reports/original_masks_psf_v1.13/REAL_ZTF_MASK_AND_NATIVE_CENTER_PSF_EVIDENCE.md) attempted **20 preregistered technical target/reference centers** on four original science frames. **Four reference candidate cores** had both accessible, WCS-aligned original science+mask cutouts with **zero documented disqualifying core bits or saturated pixels**; **16 other source-pair requests returned HTTP 503**. **No target-star mask was successfully retrieved**. Two real **23×23** native field-center PSF stamps were parsed; the two others were unavailable. **533 automated tests pass**.

These are real **instrument-product quality screens**, not evidence that the underlying source is isolated, a local PSF/photometric calibration is complete, or Gaia–ZTF source identity and WCS precision have been independently established. [Full scientific caveats and official ZTF bit definitions](docs/PHASE113_OFFICIAL_ZTF_MASK_AND_NATIVE_CENTER_PSF.md).

## v1.12 — original ZTF science FITS pixel-level centroid model sensitivity

The new v1.12 workflow returns to **original dated `sciimg.fits` pixels** and computes two genuinely different centroid algorithms on the **same** FITS image: the previous constrained elliptical Gaussian, plus a new independent-code **sigma-clipped sky-plane / positive-flux aperture centroid** with moment-shape, signal, time-header and explicit saturation-mask limitations. Predicted target/reference locations use each source's formal Gaia 5D model and its annual geometric parallax, but **source identities are still unconfirmed**.

The [real ZTF image audit](reports/real_fits_v1.12/REAL_TWO_CENTROID_MODEL_QA.md) contains **two successful 20-request runs on exactly the same historical exposures**, so they are **not 40 independent astronomical observations**. In the final-code run, eight cutouts returned **HTTP 503**, while **12 images produced both centroid models** (one target and 11 Gaia reference candidates); **nine reference candidates** passed provisional internal model agreement. The median separation of estimators in those 12 images was **0.104720″**, **model sensitivity, not absolute astrometric accuracy**. In a CIDA 11 frame with four provisional candidate references, internal held-out disagreement was **0.064675″ (Gaussian) versus 0.155762″ (aperture)**; **the target cutout was inaccessible** in this final run. The initial run produced different access counts (nine complete fits, nine HTTP 503, two inconclusive pixel screens), and the four overlapping successfully downloaded FITS files had matching byte SHA-256. Only **one of four exposure groups** had three or more cross-model references in either run.

**506 automated tests passed**. This milestone demonstrates that making a scientifically defendable statement about detector WCS/PSF and physical variability requires **official ZTF bad-pixel masks and instrument PSF products, plus genuine held-out field-star calibration**, not merely a small Gaussian centroid residual.

[Methods and explicit scientific limits](docs/PHASE112_PIXEL_CENTROID_AND_WCS_LIMITS.md). No raw original FITS pixels or ZTF light curves are in the public Git history.

## v1.11 — reference-star-specific Gaia annual parallax and formal covariance

Rather than applying Gaia corrections only to FT Tau and CIDA 11, v1.11 **queries all eight Gaia DR3 candidate reference stars plus the two target Gaia sources** and applies each star's **own epoch-dependent geometric annual parallax** to the original derived real ZTF image-model residuals. Its Gaia five-parameter formal source uncertainty includes **all ten catalogue correlations**; the original image pixels are not refitted and the source identities remain unverified.

The result is scientifically informative: the reference holdout RMS changes from **0.075782″ to 0.075770″ (FT Tau)** and **0.093046″ to 0.092971″ (CIDA 11)**, after respective changes of merely **0.012 and 0.075 mas**. These shifts are **much smaller than** the internal ~76–93 mas reference disagreement, and the same **two of four exposures** satisfy strict reference model quality. This is **not** a validated ZTF WCS accuracy, PSF error or discovery. **484 automated tests pass**.

[Official Gaia DR3 source-by-source results](reports/reference_parallax_v1.11/REAL_GAIA_REFERENCE_PARALLAX_LOO.md) · [Methods and limitations](docs/PHASE111_GAIA_REFERENCE_PARALLAX_AND_FORMAL_COVARIANCE.md).

## v1.10 — held-out Gaia candidate reference consistency

The v1.10 audit **reuses 13 genuine derived Gaia-reference image model fits from four original ZTF science exposures**, now preserved in a small SHA-provenance-checked public dataset so that short-lived GitHub artifacts cannot break reproducibility. Without re-downloading FITS images, **leave-one-reference-out** median-shift diagnostics test how much the nominal image offset changes when a reference is withheld, with explicit **strict vs inclusive PSF-model review gates**.

**Three of four exposures** have three or more inclusive fitted references; **only two** still have enough references after excluding flagged Gaussian image models. One later CIDA 11 frame drops from five references to two and **cannot** support the stricter check. The holdout disagreement is roughly **0.076 arcsec for FT Tau** and **0.093 arcsec for one CIDA 11 frame**, but these values are **not independently calibrated ZTF WCS/PSF uncertainty**, and no Gaia–ZTF identity or physical motion is confirmed.

[Actual v1.10 holdout findings](reports/holdout_v1.10/REAL_REFERENCE_HOLDOUT_EVIDENCE.md) · [Methods and limitations](docs/PHASE110_REFERENCE_HOLDOUT_QA.md) · **468 passing tests**.

## v1.9 — Gaia five-parameter covariance and annual parallax

The independent public Gaia DR3 source query now retrieves **all five astrometric parameters, their formal uncertainties and all ten pairwise correlations** for the FT Tau and CIDA 11 pilot. A bounded Astropy calculation adds **epoch-dependent geometric annual parallax** to the existing proper-motion model, propagates the **full 5×5 Gaia formal covariance** and explicitly flags the limitations of the high-RUWE CIDA 11 astrometric fit.

For four real ZTF exposure MJDs, the annual east correction ranges from **+6.79 to −4.78 mas for FT Tau** and **−1.36 to −2.25 mas for CIDA 11**; these are corrections to the **Gaia-predicted catalogue position**, not measured ZTF motions. Gaia-only formal east sigmas are ~0.07 mas for FT Tau and ~0.44–0.58 mas for CIDA 11. **Instrumental WCS/PSF and source identity have not been validated**, and the CIDA 11 covariance may substantially underestimate its real astrometric uncertainty.

[Full real v1.9 scientific evidence](reports/gaia_formal_v1.9/GAIA_COVARIANCE_AND_ANNUAL_PARALLAX.md) | [Explicit mathematical assumptions](docs/PHASE19_GAIA_FORMAL_5P_AND_PARALLAX.md) | **444 passing automated tests**.

## v1.8 — Gaia DR3 reference candidates and genuine ZTF FITS image checks

Rather than treating unclassified image brightness peaks as PSF standards, the v1.8 pilot uses **independent Gaia DR3 quality-screened candidate references**. Wider Gaia TAP cones around FT Tau and CIDA 11 returned 50 and 250 catalogue entries, of which **3 and 5 candidates** met conservative brightness, RUWE, astrometric and isolation requirements. For a limited one-g-band-per-target pilot, the program retrieved **four target FITS science frames** and attempted 16 **same-exposure, differently centered** Gaia candidate cutouts, successfully modeling 13 reference images.

Three target exposures had at least three usable independent candidate references, permitting **preliminary local east/north offset translations** (not independently calibrated full WCS). A fourth had only one suitable reference and is explicitly inconclusive. We now have **422 passing tests**; original raw FITS pixels and third-party catalogue CSVs remain outside Git. CIDA 11's high Gaia RUWE and full Gaia parallax/covariance are still unresolved.

[Read the real v1.8 candidate-reference and offset evidence](reports/gaia_reference_v1.8/REAL_REFERENCE_CANDIDATE_EVIDENCE.md) and [methods/scientific safeguards](docs/PHASE18_GAIA_REFERENCE_STAR_CANDIDATES.md). **Gaia candidates do not establish clean stellar PSFs, confirmed source identity or physical variability.**

## v1.7 — repeated science exposures and same-image shape controls

The [v1.7 real ZTF FITS audit](reports/field_controls_v1.7/REAL_MULTIEPOCH_AND_CONTROL_LIMITS.md) has now **processed 12 individual science frames** from six distinct ZTF OID/filter groups — **two independent FITS SHA-256s for each group**, including two g-band and two r-band CIDA 11 science images. This moves beyond the unavailable repeatability of v1.6. Observed *WCS-referenced Gaussian proxy centroid-residual differences* across each two-frame pair are **0.024–0.097 arcsec**, but **these are not independent astrometric accuracies, validated source matches, physical motions or discoveries**.

An initial 90-arcsec **same-image radial profile control** survey found **no images with at least two usable comparison brightness peaks**. Such peaks would themselves need catalog authentication before they could become stellar PSF standards; the current field does **not** support empirical PSF calibration or a claim of absent blending. The new implementation includes bounded requests, independent science-epoch deduplication, source-hash checks and **400 automated passing tests**. All raw FITS/CSV bytes are excluded from the public repository.

## v1.6 — quantitative image-profile proxies and repeatability gates

StellarForge now attempts a bounded robust fit of **one elliptical 2D Gaussian plus a tilted local background** to actual ZTF science cutouts. It reports provisional image-profile widths, signed centroid offsets and model residuals. A separate module checks whether **two or more distinct science frames** of the same ZTF OID and filter can be compared without mixing reference-image coadds.

- **Three FT Tau science images were successfully fitted** in the live v1.6 audit; all showed sizable positive residuals under the deliberately simple Gaussian model and are marked **review required**, not as new companions or astrophysical detections.
- **No CIDA 11 science frame was fitted** during the v1.6 acquisition because of intermittent archive access, and **zero OID/filter groups** had two independent usable science images. Multi-epoch repeatability therefore remains unmeasured.
- **387 automated tests passed**, including fully synthetic fit, WCS, residual and independent-exposure safeguards.
- Raw ZTF FITS pixels remain **in memory only**; the public GitHub repository publishes aggregate diagnostics, not original image or photometric records.

[Read the v1.6 quantitative shape audit](reports/psf_v1.6/REAL_GAUSSIAN_FIT_REVIEW.md) and [its methods and limitations](docs/PHASE16_PSF_PROXY_AND_REPEATED_SCIENCE_EXPOSURES.md). **A Gaussian model is not a calibrated ZTF PSF and its residuals are not evidence of a binary.**

## v1.5 — real FITS pixels and WCS screening

StellarForge now opens small **real ZTF FITS image cutouts** in memory (rather than inspecting only their transport headers), validates celestial WCS and checks local intensity maxima near the **provisional** Gaia-predicted target coordinates.

- **5/6 OID/filter groups successfully image-screened**: four for FT Tau and one for CIDA 11 (three actual science exposures and two reference-image coadds).
- Five local maxima within **0.50 arcsec** of the predicted coordinate, with **no additional maxima above the specific threshold** within 12 arcsec. This is *not a PSF fit* and does **not** prove that the sources are uncontaminated or physically matched.
- The CIDA 11 g cutout could not be downloaded (HTTP 503). Missing archive access is not a ZTF non-detection.
- **373 tests passed**, with synthetic FITS and WCS corner-case coverage. Original raw FITS pixels remain outside the public Git history.

[Read the full v1.5 real-image evidence and limitations](reports/real_fits_v1.5/PIXEL_WCS_RESULTS.md). The next stage must independently assess PSF shape, deblending, Gaia astrometric uncertainty and imaging alternatives.

## v1.4 — independent Gaia field and ZTF image checks

The independent public Gaia DR3 TAP cone searches for **FT Tau** and **CIDA 11** each returned only the intended Gaia source within 15 arcsec. This does **not** certify an uncontaminated field: unresolved binaries, faint or red sources, nebulosity and blends can escape the catalog search. CIDA 11 has an unusually high **Gaia RUWE = 8.57**, so its astrometry requires special attention.

StellarForge now builds **official ZTF science and reference FITS cutout links from the actual historical exposure metadata** and checks FITS transport without publishing image pixels. The IRSA service intermittently returned HTTP 503; only FITS *headers* were inspected, not images or PSFs.

- [v1.4 independent Gaia and FITS access results](reports/field_review_v1.4/GAIA_NEIGHBOURS_AND_IRSA_IMAGES.md)
- [v1.4 methods and limits](docs/PHASE14_INDEPENDENT_GAIA_AND_ZTF_IMAGE_QA.md)
- [Observed live Gaia/IRSA field audit](https://github.com/ismaelberja/stellarforge/actions/runs/42004372822)

**All source identity, contamination and physical-event claims remain unverified.**

## What the software does

- **Survey-aware data acquisition:** build and validate Gaia DR3 and IRSA/ZTF requests; record query provenance, hashes, response errors and evidence-gate status.
- **Photometric quality control:** retain photometric errors, instrumental flags, original time conventions, passbands and distinct ZTF `oid` identifiers.
- **Time-series analysis:** uncertainty-aware summary statistics, provisional Lomb–Scargle searches, window/alias diagnostics and exact cadence-coverage calculations.
- **Candidate screening and falsification:** heuristic excursions, chromatic diagnostics, source-identity cautions and simulated instrumental-control tests.
- **Reproducible engineering:** Python package, command-line interface, unit/integration tests, GitHub Actions and versioned scientific limitations.

### Processing architecture

```mermaid
flowchart LR
    A[Published catalogs: Taurus / Gaia] --> B[Source registry & positional checks]
    C[ZTF / IRSA official API] --> D[Raw response + SHA-256 provenance]
    B --> E[Source-identity review gates]
    D --> E
    E --> F[Photometric QC by OID and band]
    F --> G[Time-series & cadence diagnostics]
    G --> H[Synthetic validation and evidence report]
    H --> I[Human-reviewed scientific interpretation]
```

**Important:** The pipeline does not automatically certify Gaia–ZTF associations, disk classes, or physical dipper/burster events.

## Run it locally

Requirements: **Python 3.10+** and Git.

```bash
git clone https://github.com/ismaelberja/stellarforge.git
cd stellarforge
python -m pip install -e '.[test,analysis]'
python -m pytest -q

# Offline examples — no external archive access required
stellarforge plan-ztf --ra 65 --dec 25 --radius-arcsec 2 --bands g r
python scripts/run_v11_selection_bias.py
```

The planning coordinates are an **engineering example**, not an authenticated science target. Generated plots and analysis outputs may be written to local ignored folders. Live data access is optional; respect archive usage policies.

To reproduce the **v1.2 observational intake** privately:

```bash
python scripts/ci_observational_pilot.py reports/generated/local_irsa_pilot --fail-if-empty
```

This performs two pre-registered requests to the official IRSA endpoint, saves raw responses **locally in ignored directories**, and marks all source identities as unverified. Do not upload raw files until reuse permissions, provenance and associations have been checked.

## Scientific integrity and limitations

- Taurus membership is based on **Luhman (2023)**, *AJ*, 165, 37 ([DOI](https://doi.org/10.3847/1538-3881/ac9da3)). The working table is a pinned **third-party mirror**, not yet independently matched against the publisher's file.
- Official ZTF observations were downloaded via positional searches, but **search results are not confirmed counterparts**. FT Tau yields multiple ZTF IDs per band/field, requiring image-level blending assessment.
- Benchmarks labeled **SYNTHETIC** are engineering exercises, not measured real-survey sensitivity, accuracy or false-positive rates.
- No astrophysical event rate, disk-class frequency or new source discovery is claimed. Relevant remaining checks include image review, full astrometric uncertainties, independent labels and injection/recovery with actual observing cadences.
- Human scientific interpretation and responsible survey citation are required before any paper or astrophysical classification.

## Project documentation

- [Current status and next milestones](docs/PROJECT_STATUS.md)
- [v1.13 real original ZTF detector mask and native PSF evidence](reports/original_masks_psf_v1.13/REAL_ZTF_MASK_AND_NATIVE_CENTER_PSF_EVIDENCE.md)
- [v1.12 original science FITS Gaussian-vs-aperture real image quality audit](reports/real_fits_v1.12/REAL_TWO_CENTROID_MODEL_QA.md)
- [v1.11 real Gaia reference parallax and formal covariance sensitivity](reports/reference_parallax_v1.11/REAL_GAIA_REFERENCE_PARALLAX_LOO.md)
- [v1.10 real reference-star holdout evidence](reports/holdout_v1.10/REAL_REFERENCE_HOLDOUT_EVIDENCE.md)
- [v1.9 official Gaia five-parameter covariance and annual parallax](reports/gaia_formal_v1.9/GAIA_COVARIANCE_AND_ANNUAL_PARALLAX.md)
- [v1.8 Gaia DR3 reference-candidate and ZTF same-exposure audit](reports/gaia_reference_v1.8/REAL_REFERENCE_CANDIDATE_EVIDENCE.md)
- [v1.7 real-image science-epoch and same-field control evidence](reports/field_controls_v1.7/REAL_MULTIEPOCH_AND_CONTROL_LIMITS.md)
- [v1.6 real Gaussian profile and repeatability audit](reports/psf_v1.6/REAL_GAUSSIAN_FIT_REVIEW.md)
- [v1.5 real FITS pixel and WCS audit](reports/real_fits_v1.5/PIXEL_WCS_RESULTS.md)
- [v1.4 Gaia-neighbour and ZTF image-access audit](reports/field_review_v1.4/GAIA_NEIGHBOURS_AND_IRSA_IMAGES.md)
- [v1.3 per-epoch provisional astrometric report](reports/astrometry_v1.3/PROVISIONAL_POSITIONS_REPORT.md)
- [v1.2 IRSA data transport audit](reports/observational_intake_v1.2/RAW_TRANSPORT_AUDIT.md)
- [Data sources, citations and limitations](docs/DATA_SOURCES.md)
- [Validation plan](docs/VALIDATION.md)
- [Spanish getting-started guide](EMPEZAR_AQUI.md)
- [Engineering and scientific history](RESEARCH_HISTORY.md)
- [v1.13 release notes](RELEASE_NOTES_v1.13.md)
- [v1.12 release notes](RELEASE_NOTES_v1.12.md)
- [v1.11 release notes](RELEASE_NOTES_v1.11.md)
- [v1.10 release notes](RELEASE_NOTES_v1.10.md)
- [v1.9 release notes](RELEASE_NOTES_v1.9.md)
- [v1.8 release notes](RELEASE_NOTES_v1.8.md)
- [v1.7 release notes](RELEASE_NOTES_v1.7.md)
- [v1.6 release notes](RELEASE_NOTES_v1.6.md)
- [v1.4 release notes](RELEASE_NOTES_v1.4.md)
- [Contribution guidelines](CONTRIBUTING.md)

## Roadmap

1. **Next — native spatial PSF and source cross-identification:** the v1.13 archive screens now use original `mskimg.fits` bit flags and science-field-center `sciimgdaopsfcent.fits` stamps; validate ZTF `sciimgdao.psf` spatial PSF or `psfcat.fits` at independently authenticated source detector coordinates, with representative field controls and held-out WCS/PSF error budgets. Archive 503 responses and high CIDA 11 RUWE remain critical limitations.
2. **Observational validation:** real-cadence injection/recovery, field-star controls, uncertainty budgets and documented false positives.
3. **Scientific reporting:** independently reviewed candidate dossiers, reproducible figures and optional interactive tools.

To reproduce the v1.3 provisional screen, run `python scripts/run_v13_astrometric_review.py /path/to/IRSA_artifact.zip`. It emits summary files into an ignored directory and never adds individual ZTF measurements to Git.

The repository will continue to improve through incremental versions, tests and reviewed pull requests.

**Code reuse:** Public visibility is for transparent portfolio review. No reuse license has been selected yet; permissions are not granted automatically by publication. Original survey/catalog data remain subject to their respective citation and usage policies.
