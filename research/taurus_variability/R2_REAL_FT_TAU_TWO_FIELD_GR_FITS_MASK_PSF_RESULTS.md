# Taurus R2 — FT Tau original two-field g/r science FITS, masks and native PSFcat

**11 November 2026 · Genuine original NASA/IPAC ZTF archive science products; Gaia DR3 astrometry. R2 physical source identity remains OPEN.**

[Successfully executed original-data workflow](https://github.com/ismaelberja/stellarforge/actions/runs/43069170818) ·
[Original 30-day derived-only artifact](https://github.com/ismaelberja/stellarforge/actions/runs/43069170818/artifacts/13875884723) ·
[Permanent derived four-image source evidence](../../reports/taurus_variability_r2/FT_TAU_TWO_ORIGINAL_ZTF_FIELDS_GR_FITS_MASK_PSF_DERIVED_NO_RAW.json) ·
[Methodology preregistered before new original image data were examined](R2_FT_TAU_TWO_FIELD_GR_ORIGINAL_FITS_METHOD.md).

The original full **24-object nonrepresentative Taurus technical Gaia seed is unchanged**. FT Tau remains Gaia DR3 `149623711269425408`. Four ZTF ObjectIDs and two field/CCD/quadrant configurations were fixed from the [preceding actual-data R2 study](R2_REAL_FT_TAU_CIDA_ZTF_ALTERNATIVE_OID_RESULTS.md), not chosen based on image brightness or whether a field offset appears favourable.

## Verifiable original archive results

| Real archive experiment / predetermined quality gate | Measured result |
| --- | ---: |
| Original ZTF direct-ObjectID g/r source tables requested/parsed | **4/4** |
| Same-band two-field minimum-MJD-gap original exposure pairs selected | **2/2** |
| Different original dated single-science exposures selected | **4** |
| Authentic original ZTF 60″ science-image FITS cutouts and matching detector bitmasks verified | **4/4** |
| Authentic same-date native full ZTF `psfcat.fits` catalogues retrieved and parsed | **4/4** |
| Original source instrument QA (PSF-fit source profile, science peak, native mask core) passed | **4/4** |
| Two-field same-band instrumental quality comparisons available | **2/2** |
| Secondary *catalogued* native PSF sources within 3″ of the Gaia predicted location | **0** in these four frames |
| Additional *bright* local pixel maxima within 12″ under this one smoothing heuristic | **0** in these four frames |
| Flagged detector pixels in the checked source core | **0** in these four masks |
| Independently authenticated **physical Gaia–ZTF source matches** | **0** |
| Joined light curves or validated new variable-star/companion results | **0** |

The 4 original direct-OID tables returned 79 + 468 + 137 + 758 = **1,442 original survey photometry rows** across four fixed ObjectIDs, but this run used them to choose time-nearby **original image exposure metadata**, not to infer photometric variability. The predeclared technical `catflags & 32768 == 0` selection yielded respectively **70, 404, 117 and 608 eligible original exposures**; these are not science-quality-vetted stellar lightcurves.

### Four original images and same-filter near-simultaneous field pairs

| Filter | Original survey field / CCD / quadrant | Fixed ZTF OID | Selected original MJD | Date (UTC) | Nearest original native PSFcat source vs Gaia | Core mask |
| --- | --- | --- | ---: | --- | ---: | --- |
| g | 1605 / 15 / 3 | `1605115300003377` | **58806.385197** | 2019-11-19 | **0.056791″** | clear under chosen bad-bit rule |
| g | 609 / 8 / 4 | `609108400001155` | **58806.385648** | 2019-11-19 | **0.069015″** | clear under chosen bad-bit rule |
| r | 1605 / 15 / 3 | `1605215300005161` | **58425.306065** | 2018-11-03 | **0.035434″** | clear under chosen bad-bit rule |
| r | 609 / 8 / 4 | `609208400001969` | **58425.306516** | 2018-11-03 | **0.063244″** | clear under chosen bad-bit rule |

Both same-band two-field pairs have a predeclared minimum original MJD separation of **0.000451 days ≈38.97 seconds**, so each band has an unusually close-in-time cross-field comparison. The g pair and r pair are **over a year apart**, so *cross-filter g versus r cannot be called contemporaneous*, and none of the OID lightcurves has been merged.

### Same-band two-field original catalogue positional differences

For each selected original exposure, the native ZTF PSFcat catalogued source position was compared with FT Tau's **approximate Gaia DR3 five-parameter propagated position**, including geocentric annual parallax. The following is the **difference of ZTF-native-minus-Gaia coordinate offsets** between field 609 and field 1605:

| Same-filter cross-field pair | East difference (mas) | North difference (mas) | Vector norm (mas) | Time gap |
| --- | ---: | ---: | ---: | ---: |
| g | +9.467 | +9.720 | **13.568** | ~38.97 s |
| r | +76.060 | +23.040 | **79.473** | ~38.97 s |

**These values are descriptive detector-pipeline positional differences, not independent instrumental WCS uncertainty estimates or statistically significant astrophysical offsets.** Both PSFcat source coordinates inherit ZTF's native same-pipeline WCS, and the true catalog-source association, blend systematics, colour dependence and native centroid error budget have not been independently verified. Do not compare g (2019) and r (2018) as if they measured physical source motion.

All four original FITS mask checks found aligned science/mask celestial WCS and no bad/saturation bits in the fixed Gaia-centred core. The faint/blended-neighbour non-detection power of this method is **not calibrated**: no *additional bright local maximum* within 12″ or *additional native source catalogue row* within 3″ does **not** prove FT Tau is isolated, physically single or free of contamination.

The central image-local-maximum offsets were **0.25131″**, **0.38518″**, **0.41884″** and **0.37733″** for g/1605, g/609, r/1605 and r/609. These are pixel-grid smoothing/peak-location diagnostics, **not** independent high-precision astrometric centroids or orbital measurements. FT Tau Gaia DR3 RUWE ≈1.3266 passes the project's provisional 1.4 warning rule, but a good RUWE alone cannot prove the source is unblended.

## Research decision

**Instrumental source-screening milestone: PASS for 4/4 original cross-field images. Astrophysical source-identification gate: still OPEN.**

This is more informative than the previous pure catalogue ObjectID comparison: for each of FT Tau's two same-band ObjectID pairs, an observation from both ZTF detector-field configurations exists on almost the **same observing minute** with original science pixels, mask and PSF source-catalogue checks meeting the predefined technical gates. The study now has a reproducible **input dataset for future rigorous differential source/photometric calibration**, but has **not** established that all four ObjectIDs refer to the same unique physical Gaia source, nor measured an independently calibrated WCS or uniform cross-field magnitude zeropoint.

Before making one physical FT Tau lightcurve, compare original per-exposure calibrated reference sources/independent astrometry, inspect **blending and background in the same-night sky cutouts** and estimate detector-dependent g-to-g/r-to-r flux zeropoints and uncertainties. Verify the original Taurus membership published by Luhman, catalogue/CCD-specific failures and contemporaneous independent multi-survey identifiers. A robust *no-merge until independently justified* rule stays in force.

No new astronomy discovery, variable star, physical companion, target-period amplitude or Taurus-wide population inference is claimed. **R2 continues; software-engineering StellarForge v2.0.0 remains complete.**

## Original archive receipts and reproduction

- Real original-data GitHub Actions run: `43069170818`.
- Derived-only 30-day GitHub artifact: `13875884723`; original ZIP SHA-256: `494b754ea9bf77e7467144c4291f8a7842075c6bdcf238d45ceb4a7e306390e6`.
- Authentic uncompressed derived JSON SHA-256: `1be4d2a0633255a6a38e36153662221b70e891016500129801ec2ec6aeac3f5d`.
- Original one-Gaia-source TAP response SHA-256: `399b5498d8d8a8a646073dfc029895ed64902940896d1789c63833a18074b642`.
- Fixed 24-source Taurus R1 original seed SHA-256: `9cecb94704f028a981045629ad16ecb770f51bba4b6bb3bf13dda769327ff37e`.
- Code: `src/stellarforge/r2_ft_tau_two_field_fits.py`; runner: `python -m scripts.run_taurus_r2_ft_tau_two_field_fits`.
- Official IRSA APIs: [original ZTF lightcurves/ID](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html), [science-image/FITS cutouts](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_api.html) and [matching mask/PSF catalogue product types](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html).

Raw original FITS pixels, survey flux/magnitude time-series rows, source PSFcat tables and Gaia TAP responses were **not committed**; only derived, source-bounded checks and fingerprints remain available.
