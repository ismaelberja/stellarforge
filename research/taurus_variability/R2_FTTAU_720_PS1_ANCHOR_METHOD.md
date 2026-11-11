# Taurus R2 — independent new preregistration: expand FT Tau native ZTF field to 720″ and inspect PS1-anchored image headers

**Frozen 11 November 2026, before the new original-data run.** This is a **new experimental increment**, not a retroactive lowering of the failed [360″ original reference-ensemble threshold](R2_REAL_FTTAU_ORIGINAL_CROSSFIELD_INSTRUMENTAL_ENSEMBLE_NO_GO.md).

## Hypothesis and fixed data

A wider **720-arcsecond sky-radius** ZTF native PSF catalogue reference ensemble may provide the **≥20** same-filter reciprocal star pairs required by the original 360″ preregistration. Same four FT Tau original ZTF g/r ObjectIDs and historical exact MJD exposures, original source SHA-256s and unchanged 24-source nonrepresentative Taurus R1 seed:

| Band | Field 1605 / CCD15 / Q3 | Field 609 / CCD8 / Q4 |
| --- | --- | --- |
| g | ZTF `1605115300003377`, MJD 58806.385197 | `609108400001155`, MJD 58806.385648 |
| r | ZTF `1605215300005161`, MJD 58425.306065 | `609208400001969`, MJD 58425.306516 |

Within each band, the exposures are ~39 seconds apart. **Between bands** the observations were **a year apart**, so no g/r color or flux variability is inferred.

Exactly **four original full native `psfcat.fits`** catalogues are re-fetched and byte-SHA-matched against the previous genuine archive run. Exactly **four source-centred original `sciimg.fits` 60″ cutouts**, for the *same underlying four historical exposure product filenames*, are requested to inspect the ZTF pipeline's *previously PS1-anchored* per-exposure photometric solution in the FITS headers. No newly selected telescope observing date, filter, science field or source is permitted.

## Preregistered matching, unchanged thresholds and checks

- Change **only** the reference footprint from radius 360″ to **720″** on the same full native catalogues; keep 15″ exclusion around FT Tau (target not a calibrator), 3″ local neighbour separation against **all** detected sources, SNR ≥20, `sigmag ≤0.08`, the same PSF `chi` and `sharp` and ZTF instrument quality flags, source-flux consistency and reciprocal **0.75″** same-band neighbour matching.
- Keep the **existing** minimum **20** unique reciprocal reference pairs. Keep exactly the pre-registered deterministic position-hash training/heldout split (with geometry-only fallback), minimum 10 training and 8 validation, fixed 3×MAD clipping (min 0.08 mag), training and holdout scatter ≤0.15 mag and heldout median |bias| ≤0.07 mag. If underpowered or inconsistent, **NO-GO**, not a new result inferred by changing thresholds.
- For the wider 720″ ensemble also report two coarse source-position strata: original inner ≤360″ and new annulus (360″,720″]. If both have at least **6** sources, measure their *descriptive* median native instrumental `Δmag(field609−field1605)` difference and flag **SPATIAL_GRADIENT_REVIEW** if >**0.10 mag**, even if split-heldout internal consistency otherwise passes. If either stratum has fewer than 6, report `SPATIAL_PROFILE_UNDERPOWERED`, and do not claim field-wide spatial uniformity.
- The wider-area median is only a **native instrumental** ZTF PSF flux comparison, `mag_inst = −2.5 log10(flux in DN)`; do not use it as an absolute calibrated magnitude or merge the OID time series.

## ZTF-pipeline PS1 calibration cross-check

For exactly the same four original science-file filenames, inspect the FITS image plane header without storing raw pixels. Record only finite bounded scalar header values `MAGZP`, `MAGZPUNC`, `MAGZPRMS`, `CLRCOEFF`, `CLRCOUNC`, and `NMATCHES` (actual PS1 photometric calibrator count). Require an authentic FITS science image and matching original exposure identity, with no new images selected. Use these **only as an archival external-PS1-anchored pipeline-calibration diagnostic**. ZTF's calibration used PS1 stars but the retrieved header was computed by the **same ZTF reduction**, so it is **not independent source-by-source PS1 catalogue matching, true absolute validation, or an independently calibrated instrumental error budget**.

For each band, record descriptive `MAGZP(field609) − MAGZP(field1605)`. If an internal ensemble median is fit, report the descriptive **difference between raw native instrumental cross-field median and opposite MAGZP difference** (`Δmag_inst + ΔMAGZP`), explicitly **WITHOUT color corrections** and without statistical consistency/sigma testing; the two are not independent because the ZTF pipeline calibration may use overlapping sources. If header terms are absent or implausible, record that status, and **never fabricate a photometric zero point**.

## Acceptance and no-claims contract

The new increment is successfully *executed* when all original SHA-locked source tables and corresponding science FITS headers are retrieved or their failures are explicitly documented, and the 720″ native two-band reference counts and any eligible internal validation results are permanently recorded. **A PASS, if one occurs, means only internally consistent same-band instrumental field offsets**, not an astrophysically correct flux calibration, PS1 source-level validation or physical Gaia–ZTF source association.

The four OID light curves remain **unmerged**, no field-level true absolute photometric zeropoints are certified, no original publisher Taurus membership has been verified, and no new FT Tau variable star/companion or population inference is claimed. R2 science remains open.

## Reproducibility

- New code: `src/stellarforge/r2_fttau_720_ps1_anchor.py`
- Runner: `python -m scripts.run_taurus_r2_fttau_720_ps1_anchor`
- Original-data workflow: `.github/workflows/taurus-r2-fttau-720-ps1-anchor.yml`
- [Official ZTF science metadata and product naming](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html)
- [ZTF Data Processing / official MAGZP, color-coefficient, PS1 calibrator definitions](https://web.ipac.caltech.edu/staff/fmasci/ztf/ztf_pipelines_deliverables.pdf)
- [ZTF public release cautions on quadrant-dependent calibration and quality](https://ztf.ipac.caltech.edu/page/dr8)

**This new study preserves, and does not reinterpret, the 10-g / 19-r 360″ preregistered NO-GO.**
