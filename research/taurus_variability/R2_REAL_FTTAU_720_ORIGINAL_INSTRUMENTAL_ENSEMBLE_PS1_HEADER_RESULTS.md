# Taurus R2 — real FT Tau 720″ original ZTF reference ensemble and PS1-anchored FITS headers

**Original data run 11 November 2026 · technical internal photometric consistency PASS in g and r. Independent source-level photometric calibration and Gaia–ZTF physical identity remain OPEN.**

[Successful authentic original-data workflow](https://github.com/ismaelberja/stellarforge/actions/runs/43091456449) ·
[Original 30-day derived-only artifact](https://github.com/ismaelberja/stellarforge/actions/runs/43091456449/artifacts/13888443072) ·
[Permanent exact original-data summary](../../reports/taurus_variability_r2/FTTAU_720_REAL_NATIVE_ENSEMBLE_ZTF_PS1_PIPELINE_HEADER_NO_RAW.json) ·
[New study method frozen before this run](R2_FTTAU_720_PS1_ANCHOR_METHOD.md) ·
[The original unchanged 360″ no-go](R2_REAL_FTTAU_ORIGINAL_CROSSFIELD_INSTRUMENTAL_ENSEMBLE_NO_GO.md).

## What was done with real original astronomical survey products

Reused the **exact same four historical FT Tau ZTF single-exposure ObjectIDs** (two g and two r; original field 1605/CCD15/Q3 versus 609/CCD8/Q4), approximately **39 seconds between the two fields within each same filter**. The g exposures are dated **19 November 2019**, the r exposures **3 November 2018**, so g/r color changes **cannot** be inferred. None of the 24 original nonrepresentative Taurus technical Gaia source IDs changed.

Re-retrieved all **4 full original per-exposure `psfcat.fits`** catalogues and verified every original file SHA-256 against the previous authentic observational evidence. Retrieved the **four same-file original `sciimg.fits` 60″ cutouts** for ZTF's PS1-anchored instrumental photometric metadata (`MAGZP`, `MAGZPUNC`, `MAGZPRMS`, `CLRCOEFF`, `CLRCOUNC`, `NMATCHES`, `INFOBITS`). All 4 original headers were parsed and met the partial public ZTF source-pipeline PS1 match-count, ZP RMS and image bad-bit screens. The FITS headers are **ZTF pipeline measurements informed by Pan-STARRS1 standards**, not an independently queried PS1 catalogue.

This is a **new pre-registered 720″ reference experiment**, not a lowering of the previous 360″ experiment's fail-closed threshold. All photometric quality cuts, 15″ target exclusion, 3″ nearest-source separation, ≤0.75″ reciprocal two-field positional matching, **20-minimum reference pairs**, geometry-only split train/holdout, 3×MAD robust clipping and original scatter/heldout criteria were retained. The 720″ field was also compared between the original inner 360″ and a new 360–720″ annulus to screen for broad spatial offsets.

## Real source screening and internal photometric results

| Original source-control measure | **g band (2019)** | **r band (2018)** |
| --- | ---: | ---: |
| Full native ZTF PSF catalogue sources: field 1605 / 609 | 5,757 / 4,956 | 8,425 / 8,375 |
| Sources within new 720″ radius, field 1605 / 609 | 578 / 578 | 917 / 947 |
| Clean candidate references after all original per-field QC, field 1605 / 609 | 106 / 116 | 244 / 222 |
| Same-band reciprocal, unique, QC-filtered reference pairs | **84** | **186** |
| Reference pairs in old inner 360″ / new outer 360–720″ | 10 / 74 | 19 / 167 |
| Training reference stars before outlier screen | 51 | 96 |
| Training reference stars surviving fixed robust screen | 51 | 94 |
| Held-out reference stars | 33 | 90 |
| Median native instrumental `Δmag(609−1605)` | **+0.1180 mag** | **−0.0040 mag** |
| Robust training scatter | 0.02669 mag | 0.01705 mag |
| Held-out median signed residual | −0.01400 mag | +0.00600 mag |
| Robust held-out scatter | 0.01927 mag | 0.01927 mag |
| Inner−outer descriptive median difference | +0.0055 mag | −0.0010 mag |
| Preregistered internal ensemble fit / holdout / broad spatial screen | **PASS** | **PASS** |

**Interpretation:** compared to the previous radius-360″ pre-registered **10 g / 19 r NO-GO**, the new 720″ experiment finds sufficient distinct, tentatively matched native ZTF reference entries for the existing 20-star gate to run in each band. The split-sample held-out residuals and simple inner/outer radial median differences meet the fixed internal QA thresholds. The +0.118/−0.004 mag values are **raw ZTF instrumental catalogue offsets**, not target astrophysical magnitudes, absolute flux calibrations, newly measured physical variability or certified CCD photometric zero points. The model omits individual reference colors, robust long-term stability and detailed positional dependence beyond the two preregistered radial strata.

## PS1-anchored archival pipeline photometric header check

Original FITS keywords for the **same four previously fixed original exposures**:

| Original same-band field | Original `MAGZP` | `MAGZPRMS` | `NMATCHES` (PS1 photometric calibrators) | `CLRCOEFF` | Image `INFOBITS` |
| --- | ---: | ---: | ---: | ---: | ---: |
| g / 1605 | 26.215597 | 0.038748 | 1,223 | −0.036286 | 0 |
| g / 609 | 26.127789 | 0.037959 | 1,092 | −0.060615 | 0 |
| r / 1605 | 26.099472 | 0.022096 | 1,300 | +0.063890 | 0 |
| r / 609 | 26.098511 | 0.022618 | 1,176 | +0.068839 | 0 |

| Descriptive comparison (original field 609 minus 1605) | g | r |
| --- | ---: | ---: |
| Native `Δmag_inst` from internally matched ensemble | +0.118000 mag | −0.004000 mag |
| ZTF's own PS1-anchored original header `ΔMAGZP` | −0.087808 mag | −0.000961 mag |
| **Uncorrected `Δmag_inst + ΔMAGZP`** | **+0.030192 mag** | **−0.004961 mag** |

These raw residuals may be affected by **source color, ZTF's fitted `CLRCOEFF`, stellar selection and field-dependent PSF calibration**; no measured PS1 color index was used, and the full `ZPCLRCOV`/zeropoint systematic covariance was not propagated. The instrumental ensemble and ZTF's own image ZP both arise from the **same ZTF processing pipeline**, despite its use of external PS1 calibrator stars. Therefore this table is a **descriptive cross-check only**, **not an independent external PS1-source photometric calibration**, an uncertainty-normalized difference, or evidence of source-identification significance.

## Scientific acceptance and remaining critical gates

- **Instrumental engineering/archival validation:** 4/4 SHA-verified original full PSF catalogues, 4/4 original PS1-anchored science FITS photometric headers, **2/2 internal reference ensembles/holdout/radial screens PASS** at the new preregistered 720″ radius.
- **Astrophysical flux-calibration and source-ID validation:** still **NOT COMPLETED**. This run independently queried **zero actual PS1 individual source rows**, did not measure their source-level reference colours, did not calibrate a full CCD spatial/color/airmass error model, did not prove reference stars unblended or stable over multiple nights, and did not recover a unique physical Gaia–ZTF FT Tau source.
- **Original FT Tau source variability, companions, confirmed membership, source photometric zero points and merged ObjectIDs:** **zero** claimed or produced; the g (2019) and r (2018) data are on separate epochs and photometric systems. The four original ZTF OID curves remain **separate** and must not be interpreted as one physical time series from this step.

**Next decisive experiment:** physically crossmatch a predeclared set of native same-field original ZTF reference sources with **actual independently retrieved individual PS1 DR2 source rows** and colors (or another genuinely independent survey), verify unique matches/blending and solve/validate color-dependent residuals with a full systematic error budget. Repeat across more independent nights before attempting an astrophysical FT Tau lightcurve.

StellarForge **v2.0 engineering/portfolio software remains finished and ready for LinkedIn**. The separately pursued research **R2 physical Gaia–ZTF association remains open** and there is no claimed astronomical discovery.

## Original data receipt

Original GitHub Actions workflow run `43091456449`, artifact `13888443072`;
artifact ZIP SHA-256:
`123a4d5cc906e56a430874e1dace957d94337da76581cd3da14afd4c221c154d`;
derived JSON SHA-256:
`b0186cd85d47c32cca7e87ce8a98d8a8b27448c391822ef2bed55bf0256c2558`.
The four original 24-source-seed and four original FITS/PSFcat file hashes are pinned in the committed no-raw result and prior scientific evidence.

[Original PS1-anchored ZTF FITS header calibration definitions](https://web.ipac.caltech.edu/staff/fmasci/ztf/ztf_pipelines_deliverables.pdf) ·
[ZTF release native per-quadrant photometric calibration cautions](https://ztf.ipac.caltech.edu/page/dr8).

Original source magnitudes, fluxes, raw per-source sky positions, Gaia response tables and original science FITS pixels **were not committed**.
