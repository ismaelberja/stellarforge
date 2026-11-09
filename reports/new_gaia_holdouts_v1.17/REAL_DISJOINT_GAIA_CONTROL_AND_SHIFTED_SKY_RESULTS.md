# StellarForge v1.17 — Real new Gaia source-disjoint field controls and shifted-sky null observations

**9 November 2026 · Actual original Gaia DR3 + ZTF IRSA results.** [Successful source-data workflow — 636 tests](https://github.com/ismaelberja/stellarforge/actions/runs/42661663983).

## What was verified

This is the first StellarForge extension beyond the ten Gaia DR3 source identifiers originally used for FT Tau/CIDA 11 source and field-reference testing in v1.8–v1.16. A **fresh, independent Gaia DR3 210″ wide-cone query per technical target** was used to preregister new stars using **Gaia-only** information, entirely before checking original ZTF PSF source lists or original science/mask pixels. Every previously used Gaia ID was explicitly excluded, together with source-quality, all-catalogue Gaia-neighbor isolation and sky-quadrant requirements.

**Important distinction:** these new source IDs were withheld from **StellarForge's previous selection and pixel fits**, **not** shown to have been withheld from the *original ZTF pipeline's DAOPhot PSF-construction stars*. Thus the experiment provides **previously unseen field-source tests**, but it does **not** establish a truly independent external instrument PSF calibration or a confirmed physical Gaia–ZTF crossmatch.

The original ZTF science source products are exactly the same four dated g-band historical exposures used in v1.16; those are **four astronomical science epochs**, not 4 newly collected observations.

## Gaia DR3 wide-cone selection before viewing ZTF pixel data

Each of the two target fields used an original independent **210″ Gaia DR3** query with source IDs, G magnitude, signal-over-noise, RUWE, astrometric solution, parallax, proper motions, formal RA/Dec and proper-motion errors and Gaia neighbors. The reference/target source-ID union from the prior v1.8 candidate ledger contained exactly **ten IDs**. None was eligible.

| Field | Gaia DR3 rows in wide-cone table | Quality-screened, isolated candidates before budget | New Gaia-only selected source IDs | Sky-quadrants represented |
|---|---:|---:|---:|---:|
| FT Tau | **50** | **0** | **0** | 0 |
| CIDA 11 | **250** | **20** | **4** | **4** |
| **Total** | **300 Gaia source rows across two independent fields** | **20** | **4** | CIDA 11 only |

The four preregistered CIDA 11 candidate control Gaia DR3 IDs were **3419109222512317056**, **3419109840987851136**, **3419157944621312896**, **3419111451598996992**. One source was chosen from each of four sky quadrants using fixed Gaia-only ranking, after excluding the original source IDs. **The sample has no new eligible FT Tau controls at these specific criteria.** This is a scientifically material *coverage limitation*, not a non-detection of FT Tau itself. We did not lower selection thresholds after examining outcomes.

All four new Gaia source IDs were re-queried for their individual **full formal correlated five-parameter Gaia DR3 astrometric solution**, including first-order Earth-geocentric annual geometric parallax at the exact ZTF historical science epochs. This still is **not** a Palomar topocentric apparent-coordinate or instrument-distortion model.

## Real native ZTF science and masked PSF-pixel outcomes

All four new Gaia sources were screened separately against the genuine original **CIDA 11 native `psfcat.fits`** source catalogues on each of the two historic science dates. Every eligible source was fitted to the **matching original `sciimg.fits` science data in DN** with its independently WCS-aligned genuine **`mskimg.fits` bad-pixel mask**, using the original `sciimgdao.psf` spatial model evaluated at native original `xpos/ypos`, a local sky plane and distinct checkerboard pixels for the same image's fit/residual score.

| CIDA 11 original science epoch | New Gaia sources preregistered | Actual same-date original science/mask PSF-pixel fits | Same-image residual QC passes | Catalogues requiring review |
|---|---:|---:|---:|---:|
| MJD **58475.113750** | 4 | **4** | **4** | 0 |
| MJD **58849.135984** | 4 | **2** | **2** | **2** (failed native source-catalogue eligibility) |
| **CIDA 11 total** | **4 distinct Gaia IDs** | **6 source×epoch fits** | **6 provisional passes** | **2 no pixel fit** |

Both original FT Tau exposures had **zero new Gaia-only candidates under the strict quality and isolation criteria**; there were consequently no new masked-pixel fits or shifted-sky null probes there in v1.17. Earlier original FT Tau image fits remain valid *historical software evidence* but are not new, independent control-source tests.

The **actual descriptive source-pixel residual results**, measured as same-source checkerboard held-out pixel RMS divided by the robust sky annulus MAD proxy, are:

| New Gaia DR3 candidate | CIDA 11 MJD 58475.113750 | CIDA 11 MJD 58849.135984 |
|---|---:|---:|
| 3419109222512317056 | **1.010373** (passed) | **0.936249** (passed) |
| 3419109840987851136 | **0.876914** (passed) | **1.367764** (passed) |
| 3419157944621312896 | **1.092753** (passed) | Native PSF-source candidate review; no pixel fit |
| 3419111451598996992 | **0.951452** (passed) | Native PSF-source candidate review; no pixel fit |

The actual first CIDA 11 exposure had **four distinct** eligible original source-mask PSF fits and thus reached the pilot's **minimum three distinct candidate-source IDs** for a *descriptive same-image residual median*, **0.98091**. The second exposure had only **two** eligible fitted distinct source IDs; its source-control comparison correctly reports **INSUFFICIENT_DISTINCT_GAIA_CONTROL_IMAGE_FITS** and **does not publish an observational calibration median**.

All six completed pixel fits pass the original v1.16 provisional residual/noise-screen criteria. This fraction is conditional on **Gaia-only preselection, native ZTF catalogue source detection and profile-quality filters**, not a population success rate, a calibrated new instrumental PSF error or a physical/source-identity validation.

The four new source IDs are **not independently demonstrated to be true single or isolated stars**. A 10″ absence of other Gaia entries does not rule out unresolved binaries, other background stars, galaxies or nebulosity.

## Real shifted-sky positional null controls

Before seeing the ZTF native catalogues, each new Gaia projected sky position was assigned four **fixed** original CCD-shifted probes: +25″ east, −25″ east, +25″ north and −25″ north. Each is checked for a native ZTF PSF-fit catalogued source **within 1″** of the shifted location, and separately for a source meeting the native provisional PSF-quality flags.

| CIDA 11 original science exposure | Shifted sky positions | Any `psfcat` source within 1″ | Source passing native fit quality |
|---|---:|---:|---:|
| MJD 58475.113750 | **16** | **0** | **0** |
| MJD 58849.135984 | **16** | **0** | **0** |
| **Total** | **32** | **0** | **0** |

**These 32 probes do not represent 32 independent astrophysical control sources**: they are four fixed shifts of the same four Gaia source predictions at two epochs of the same field. An empty 25″ shifted sky bin is not evidence that the true Gaia/ZTF counterpart identity is independently established, and **0/32 is not a calibrated contamination fraction, binomial probability, significance or source false-match rate**. Sky shifts could overlap real unrelated stars in other data and provide only a preliminary local accidental-match-density diagnostic.

## Scientific limitations that remain

1. **Unknown original PSF-model training set.** The native per-exposure ZTF DAOPhot model may have been trained on these same *new* Gaia control stars. Their disjointness from our previous ten Gaia IDs is real, but their independence from original PSF model fitting is not established.
2. **Not an independently calibrated stellar PSF.** The native spatial model comes from ZTF's per-exposure pipeline and is fitted back to actual original pixels. A source image model fit is a real software check but does not validate the model's true source-specific error variance against independently withheld instrumental PSF training stars.
3. **Not an independently authenticated Gaia–ZTF physical source match.** Gaia formal parallax/proper-motion models, native nearest-source PSFcat detections and original CCD-phase consistency do not jointly prove the physical stellar identity.
4. **FT Tau insufficient new field stars.** The wide Gaia field had fifty sources, with none surviving the exact strict quality, brightness, offset, old-ID exclusion and isolation rules. Do not pretend that CIDA 11-only results validate both targets.
5. **Only two original CIDA 11 g-band epochs** and four new distinct Gaia candidate IDs; one date has just two analyzable stars. Not enough to determine field-wide distribution or temporal PSF calibration.
6. **Same-image pixel holdout not a source holdout from instrument training.** The source DN sky-MAD ratios remain descriptive, not independent Gaussian error/significance estimates.
7. **The new shifted-sky probes have fixed 25″ offsets and source/epoch correlation**; they are not randomized controls with a formally measured false-match rate.
8. **The three previously flagged v1.16 positive residual cases remain unexplained**, including CIDA 11 high Gaia DR3 RUWE ≈8.57, and no new physical companion/variability event is established.
9. Source raw IRSA photometry, original Gaia TAP CSV, genuine ZTF science/mask FITS pixel arrays, full native PSFcat source rows and original native spatial DAOPhot coefficients remain **outside public Git and artifact ZIPs**. Only original source SHA-256s, selected Gaia IDs and derived scalar evidence are public.

## Reproducibility and next gate

[Selection and shifted sky controls](../../src/stellarforge/v117_disjoint_gaia_controls.py) · [Live original-data runner](../../scripts/run_v117_new_field_controls.py) · [adversarial synthetic tests](../../tests/test_v117_disjoint_gaia_controls.py) · [full methods, selection invariants and limits](../../docs/PHASE117_DISJOINT_GAIA_SOURCE_HOLDOUTS_AND_SHIFTED_SKY_NULLS.md) · [successful observed-data Actions run](https://github.com/ismaelberja/stellarforge/actions/runs/42661663983).

```bash
python -m pip install -e '.[test,analysis,images]'
python -m pytest -q
python scripts/run_v117_new_field_controls.py /path/to/original_SHA_verified_IRSA_acquisition.zip \
  --max-new-controls-per-field 4 --gaia-timeout 30 --archive-timeout 6 \
  --require-new-real-fits
```

**Next:** retrieve original ZTF source PSF training-star membership (if available) and expand the parent Gaia/ZTF control sample while preserving preregistered selection and isolation constraints, including genuinely applicable **FT Tau** controls. Validate an actual **independent source holdout PSF/WCS model** with realistic covariance, proper original exposure timestamp/topocentric/color terms and robust false-match tests. Only after these steps could physical source associations, binaries or variability be responsibly discussed.

**Zero confirmed new astrophysical physical source IDs, stellar companions, independent source-PSF error calibration or physical variability events.**
