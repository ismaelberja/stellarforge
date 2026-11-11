# Taurus R2 — original ZTF FITS + bitmask + native PSFcat crowding screen

**Actual original public astronomical data rechecked 11 November 2026.** This is a **fixed historical-exposure instrumental and positional consistency screen**, not a successful scientific Gaia–ZTF physical source identification.

[Successful actual-data GitHub Actions run](https://github.com/ismaelberja/stellarforge/actions/runs/43059114825) ·
[Original no-raw derived artifact (30-day retention)](https://github.com/ismaelberja/stellarforge/actions/runs/43059114825/artifacts/13873466036) ·
[Permanent source/exposure derived ledger](../../reports/taurus_variability_r2/FOUR_ORIGINAL_FITS_MASK_NATIVE_PSF_SOURCE_QA_NO_RAW.json) ·
[Preregistered method](R2_ORIGINAL_FITS_SOURCE_GATES_METHOD.md).

The actual original-data artifact ZIP has SHA-256
`b782de857569a3e76df19e1d3940bf0a79f204eba2b40b33de82ee121b2b9b29`.
The uncompressed original derived JSON SHA-256 is
`5d10a39bbce8c9c23183ea251bd52b254a2e347955bf0fc3f04f227c1774ba61`.
Original Gaia DR3 source-data response SHA-256:
`31ec0a7b19e424f06ea1d9d26ac930a1e633418e6285efe469d41c58c457cd99`.
The historical R1 24-star technical selection SHA-256 remains
`9cecb94704f028a981045629ad16ecb770f51bba4b6bb3bf13dda769327ff37e`.

## What the actual original astronomy survey data established

Original live queries reconstructed the **exact four previously documented historical single-exposure science filenames**, using their fixed ZTF OIDs and observation MJDs. All four original official per-exposure `psfcat.fits` full source tables were available and parsed, and all four original `sciimg.fits` source-centred cutouts were retrieved with their corresponding `mskimg.fits` cutouts of identical sky geometry.

| Check | Actual outcome |
| --- | ---: |
| Fixed original historical ZTF single-science exposure dates | **4** |
| Exact ZTF OID+MJD original metadata records recovered | **4/4** |
| Authentic native original-exposure PSF-fit source tables parsed | **4/4** |
| Original science FITS + detector bitmask pairs aligned and evaluated | **4/4** |
| Original science-image central-local-maximum candidates detected | **4/4** |
| Original native `psfcat` sources within 1″ of the Gaia-predicted technical position | **4/4** |
| Frames with a **second** native `psfcat` source within 3″ | **0/4** |
| Frames with additional bright *image* local-maxima candidates within 12″ of target | **0/4** |
| Frames with disqualifying or saturated original central-core bitmask pixels | **0/4** |
| Physically verified Gaia–ZTF source identities | **0** |
| Independently calibrated WCS, PSFs, or companion detections | **0** |
| Newly confirmed astrophysical stellar variability results | **0** |

**Neither zero extra PSFcat neighbours nor zero additional bright local maxima is proof of a single star or lack of companions.** Both methods can miss blended/faint sources; the PSFcat and celestial WCS originate in the same instrument reduction and do not independently validate source identity.

## Four actual same-exposure outcomes

| Historic field | Original ZTF MJD | Original `psfcat` rows | Nearest native survey PSF source relative to Gaia position | Image central peak relative to Gaia position | Gaia RUWE |
| --- | ---: | ---: | ---: | ---: | ---: |
| FT Tau | **58388.389016** | 3,970 | **0.07266″** | 0.52287″ | 1.3266 |
| FT Tau | **58491.184780** | 5,569 | **0.22398″** | 0.16163″ | 1.3266 |
| CIDA 11 | **58475.113750** | 5,313 | **0.23018″** | 0.46872″ | 8.5675 |
| CIDA 11 | **58849.135984** | 12,355 | **0.05950″** | 0.63753″ | 8.5675 |

The `psfcat` separation is the angular distance from Gaia's estimated geocentric parallax-corrected source position at the historical exposure date to the **nearest per-exposure ZTF pipeline catalogue entry**; this is not a covariance-normalized likelihood, unique astrophysical counterpart association, or external survey astrometric calibration.

The image peak offsets are **pixel-grid local-maxima heuristics from original science cutouts after smoothing**, not precisely measured astrometric centroids. They have substantially different numerical meanings from the catalogue distances and should **not** be subtracted from them, assigned formal uncertainties, or used as orbital/variability evidence.

For all four matched science/mask cutout pairs, the original ZTF bad-pixel mask has **zero disqualifying source-core pixels and zero saturated source-core pixels** under the project's stated bad-bit selection. This is original detector mask quality, not confirmed isolation, photometric calibration, or proof against unmasked blends.

### Scientific cautions

- CIDA 11's original Gaia DR3 **RUWE ≈8.57** is unusually high, making a simple single-source astrometric explanation particularly uncertain. It is **not** a confirmed companion detection. FT Tau's RUWE ≈1.33 also does not rule out blending.
- All four dated images were **already studied in StellarForge v1.8–v1.16**. This audit adds an explicit side-by-side **native original catalogue neighbour / same-date image-mask** gate to research R2; it does **not** expand the number of independent astronomical epochs or the original 24-source Taurus sample.
- The image+mask agreement and native PSF source proximity use **ZTF's own same-pipeline WCS**, not an independent calibration, and no source position covariance combining Gaia/Palomar topocentric/WCS systematics is obtained.
- The full ZTF source `psfcat` can omit unresolved companions or artifacts. The image local maxima are not deblended PSFs.
- Four historical images were checked **only for two of the 24 technical Taurus candidates**. Neither the new 22/24 IRSA positional source-table access nor these two image-piloted targets completes a robust 24-source Gaia–ZTF physical association.
- Independent membership verification against the original publisher Luhman (2023) catalogue remains outstanding.
- Original FITS pixels, Gaia source tables and ZTF photometric data **remained ephemeral** in the remote workflow. Only bounded derived counts and SHA/provenance have been committed.

## Assessment and the next phase of science

**R2 has made measurable progress at the actual original-image level:**
for FT Tau and CIDA 11, four historic science/bitmask pairs and native PSF catalogues have been tied to the exact original ZTF OIDs/MJDs. Native source positions and simple pixel-peak checks are instrumentally compatible with predicted Gaia directions, with no core bad-mask flags or additional bright/native catalogue peaks under the stated small radii.

**But the scientific physical Gaia–ZTF counterpart validation remains OPEN.** The next decisive work is independent same-field reference astrometry/crowding, explicit alternate ZTF OID deblending review, and independent published literature membership. Only then should R3 begin interpreting stellar lightcurve amplitudes or periods.

The engineering portfolio **StellarForge v2.0.0 remains finished and shareable**; no new variable star, companion, calibrated survey model or publishable astronomical detection is claimed from this step.

## Original provider references

- [NASA/IPAC IRSA ZTF original-science FITS / cutout and metadata API](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_api.html)
- [Official science ancillary file suffixes and product roles](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html)
- [Historical original ZTF masked spatial PSF pixel evidence](../../reports/masked_spatial_psf_v1.16/REAL_ZTF_PIXEL_RESIDUALS_EVIDENCE.md)
