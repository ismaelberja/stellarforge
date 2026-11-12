# Taurus R2 — authentic six-original-ZTF-image FT Tau PSF chi-blind reference sensitivity

**12 November 2026. Original Gaia DR3 source, three frozen same-OID early/late ZTF image pairs, six byte-verified full native original PSF catalogues. Existing source-quality rules unchanged.**

[Precommitted protocol](R2_FTTAU_CHI_CONTROL_REFERENCE_PREREGISTRATION.md) · [Original-data workflow 43275404347](https://github.com/ismaelberja/stellarforge/actions/runs/43275404347) · [Derived-only archive artifact](https://github.com/ismaelberja/stellarforge/actions/runs/43275404347/artifacts/13970027074) · [Permanent no-raw evidence](../../reports/taurus_variability_r2/FTTAU_SIX_ORIGINAL_ZTF_CHI_BLIND_REFERENCES_NO_RAW.json)

## Preregistered question

PR #45 confirmed that the three preselected late-night FT Tau source candidates failed **only** the earlier frozen native PSF chi lower bound 0.5. Does chi below 0.5 also occur in other native PSF catalogue sources on the **same** dated detector exposures when references are selected without using chi?

For each six original source catalogues, references were selected prospectively within 15–720 arcsec of epoch-propagated Gaia, with ≥3 arcsec isolation from every catalogued detection, positive flux and flux uncertainty, SNR≥20, good flags and |sharp|≤0.5. Crucially the selection had **no chi lower or upper cutoff**. A secondary SNR-matched subset required control SNR within a factor of two of the target source SNR. The full, original six file SHA hashes matched the original PR #44 source ledger. The original dates were not reselected after seeing data. No original source rows or pixels were committed.

## Actual original catalogue controls and chi

| Frozen original exposure | FT Tau native chi | All chi-blind controls | chi below 0.5 | SNR-matched chi below 0.5 | Control median chi |
| --- | ---: | ---: | ---: | ---: | ---: |
| g / field 1605, early MJD 58362.516713 | 0.804 (original PASS) | 108 | 38/108 (35.19%) | 34/98 (34.69%) | 0.6205 |
| g / field 1605, late MJD 60233.393611 | **0.456 (original FAIL)** | 160 | 38/160 (23.75%) | 35/133 (26.32%) | 0.6310 |
| g / field 609, early MJD 58330.489120 | 0.552 (original PASS) | 94 | 25/94 (26.60%) | 18/63 (28.57%) | 0.6335 |
| g / field 609, late MJD 60948.441412 | **0.424 (original FAIL)** | 196 | 23/196 (11.73%) | 15/131 (11.45%) | 0.8070 |
| r / field 609, early MJD 58321.487465 | 1.438 (original PASS) | 239 | 20/239 (8.37%) | 16/196 (8.16%) | 0.9720 |
| r / field 609, late MJD 60935.414502 | **0.383 (original FAIL)** | 298 | 96/298 (32.21%) | 94/269 (34.94%) | 0.6205 |

**Authentic original-source totals:** 6/6 full PSF catalogs byte-SHA reverified; 6/6 independent-of-chi source samples and 6/6 target-SNR-matched source samples have ≥20 entries. **1,095 source catalogue records** satisfy the chi-blind control rule across the six observations, and **240 records** have original chi below 0.5. This pooled count is NOT a fraction of independent uniquely identified physical stars: some objects may appear in more than one exposure.

The three late-night rejected target sources fall at approximately the **16.25th, 8.16th, and 13.09th percentiles** of the corresponding native chi-blind control distributions. Native chi below the old source cut is therefore not unique to the FT Tau candidate and selecting only chi≥0.5 demonstrably excludes some otherwise good-flag and high-SNR native source detections in these detector images.

## Important interpretation

This is an **observational selection sensitivity audit**, not an independent measurement of the optimal chi threshold. The same original ZTF pipeline fitted both target and reference positions, so the source controls are not statistically independent instrument calibration and may include blends or nonstellar detections. The original ZTF documentation describes chi as a residual/noise fit statistic; do not assume a universal reduced chi-squared rule or an established instrumental noise error model ([ZSDS pipelines and products](https://irsa.ipac.caltech.edu/data/ZTF/docs/ztf_pipelines_deliverables.pdf), [official image/PSFcat product interface](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html)).

**No source previously failed is promoted to an accepted astrophysical target.** Previous R2 studies' 5/8 original target candidate passes, 3/8 failures and only 1/4 valid two-night groups remain unchanged. Physical Gaia–ZTF FT Tau identity, deblending, WCS/PSF source covariance, authentic proper motion and intrinsic variability remain scientifically unresolved. **Zero confirmed physical Gaia–ZTF FT Tau matches, zero merged OID light curves, zero new companions or variable stars. R2 OPEN; R3 blocked.**

## Permanent genuine-data provenance and next scientific gate

[Successful original-data run](https://github.com/ismaelberja/stellarforge/actions/runs/43275404347); [authentic derived-only artifact](https://github.com/ismaelberja/stellarforge/actions/runs/43275404347/artifacts/13970027074); ZIP SHA-256 **2c8b2b01dc4ad5ee5e9536fcfa4d1b7d94c2a187c40c8ad9f66f102d8c9dbc09**; original derived JSON SHA-256 **ade85d70b57e007fe71d83ec7ecffc6f35aff3357468751abd83e403267beb98**; original Gaia response SHA-256 **399b5498d8d8a8a646073dfc029895ed64902940896d1789c63833a18074b642**. Per-source reference raw rows, IDs and original source photometry were not archived. [Six original file hashes, exact dates, counts, medians and target percentiles](../../reports/taurus_variability_r2/FTTAU_SIX_ORIGINAL_ZTF_CHI_BLIND_REFERENCES_NO_RAW.json) are preserved.

**Recommended next increment:** independently characterize PSF chi/noise using original reduction products, vetted source controls or higher resolution original observations, and separately validate FT Tau physical identity/deblending. Keep the old chi gate frozen unless a new independently justified *prospective* qualification study approves a different gate.
