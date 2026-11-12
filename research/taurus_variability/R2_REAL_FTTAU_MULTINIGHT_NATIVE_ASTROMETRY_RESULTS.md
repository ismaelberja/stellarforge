# Taurus R2 — authentic FT Tau independent-night original ZTF source-position audit

**12 November 2026. Genuine Gaia/ZTF archive data; prospectively fixed image selection. FT Tau physical identity remains UNCONFIRMED.**

[Pre-registered protocol](R2_FTTAU_MULTINIGHT_NATIVE_ASTROMETRY_PREREGISTRATION.md) · [Successful genuine-data workflow](https://github.com/ismaelberja/stellarforge/actions/runs/43270659201) · [Temporary full derived-only JSON artifact](https://github.com/ismaelberja/stellarforge/actions/runs/43270659201/artifacts/13968001848) · [Permanent derived-only source ledger](../../reports/taurus_variability_r2/FTTAU_MULTINIGHT_ORIGINAL_ZTF_SOURCE_AUDIT_NO_RAW.json).

## Results

The original exact Gaia DR3 FT Tau source and all four fixed original IRSA ZTF ObjectID response tables were queried. Four historical anchor exposures were retained intact and excluded from new-image selection. For each of the four original band/field strata, the earliest and latest eligible **other** UTC observing nights were prospectively selected without examining source positions or image PSF quality. All 8 newly selected original native full ZTF PSF catalogues were recovered and parsed, with original byte SHA-256 fingerprints. Dates are separated by 1871–2618 days, above the frozen 30-day minimum.

| Fixed original filter/field | Earliest original MJD | Latest original MJD | Separation (days) | Nearest ZTF source to propagated Gaia: early/late (arcsec) | Frozen native PSF quality early/late |
| --- | ---: | ---: | ---: | --- | --- |
| g / 1605 | 58362.516713 | 60233.393611 | 1870.876898 | 0.107051 / 0.133039 | PASS / **FAIL** |
| g / 609 | 58330.489120 | 60948.441412 | 2617.952292 | 0.104200 / 0.095188 | PASS / **FAIL** |
| r / 1605 | 58356.394352 | 60884.483322 | 2528.088970 | 0.050280 / 0.121756 | **PASS / PASS** |
| r / 609 | 58321.487465 | 60935.414502 | 2613.927037 | 0.103144 / 0.053047 | PASS / **FAIL** |

**Summary:** Gaia original source 1/1; original fixed ZTF OID metadata 4/4; new native original full PSF catalogs 8/8; **5/8 provisional nearest native source candidates passed the original frozen PSF quality gate**; **1/4 earliest/latest same-band/field pairs passed both source quality gates**. All eight have one *catalogued* nearest source inside 0.6 arcsec and no second catalogued source inside 2 arcsec, but three **late-night** nearest sources fail the independent PSF quality condition. Failure is not evidence of astrophysical non-detection. No better-looking replacement dates were chosen.

For the single accepted two-epoch source-quality pair, **r field 1605**, late-minus-early residual of native ZTF minus epoch-propagated Gaia is **−0.007987 arcsec east** and **+0.122107 arcsec north** across 2528.088970 days. These descriptive catalogue residuals are **not an independently calibrated source motion, a significance measurement or a confirmed physical Gaia–ZTF match**. Individual ZTF field/WCS/PSF covariance, PS1 stellar epochs/motions and high-resolution deblending are not available.

## Scope and next experiment

The multi-night survey supports **positional feasibility only**, with important quality failures. Do not merge the four original ZTF ObjectID light curves. **Zero physical FT Tau Gaia–ZTF counterparts authenticated, zero new variable stars or companions, R2 astrophysical validation OPEN and R3 variability inference blocked.** The software-engineering portfolio v2.0 remains independently finished.

Next: investigate the *three fixed late-night native PSF quality failures*, using original image masks and per-source PSF-fit diagnostics without relaxing thresholds or reselecting epochs. Independently authenticate physical identity/deblending with a literature source or higher-resolution imaging.

## Provenance

Authentic workflow [43270659201](https://github.com/ismaelberja/stellarforge/actions/runs/43270659201), derived-only artifact [13968001848](https://github.com/ismaelberja/stellarforge/actions/runs/43270659201/artifacts/13968001848); artifact ZIP SHA-256 `72437d4449d4e65993b202c5f02d7d819ce000052ebcb167ce03ba498367ebe2`, extracted no-raw JSON SHA-256 `f8d44d7edb47a0392b342cea0127a40fe022726cc8b63254ec53817a3bc4f24b`; original Gaia response SHA-256 `399b5498d8d8a8a646073dfc029895ed64902940896d1789c63833a18074b642`. Raw PSF source rows, raw catalogue data, image pixels, source photometry and time series were never committed.
