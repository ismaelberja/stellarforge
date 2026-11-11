# Taurus R2 — real independent MAST Pan-STARRS1 DR2 source-color reference audit for FT Tau

**11 November 2026 · Genuine original independent-survey PS1 DR2 MeanObjectView catalogue retrieved. Both g/r reference-source fits pass the preregistered within-sample held-out checks. This is NOT a finished absolute calibration or an authenticated FT Tau Gaia–ZTF crossmatch.**

[Original-data GitHub Actions run 43102892830](https://github.com/ismaelberja/stellarforge/actions/runs/43102892830) ·
[Derived-only 30-day archive artifact 13892248204](https://github.com/ismaelberja/stellarforge/actions/runs/43102892830/artifacts/13892248204) ·
[Permanent original PS1/ZTF source-reference derived ledger](../../reports/taurus_variability_r2/FTTAU_REAL_ORIGINAL_MAST_PS1_DR2_EXTERNAL_SOURCE_COLOR_PILOT_NO_RAW.json) ·
[Original-data receipt, hashes and anti-discovery constraints](../../reports/taurus_variability_r2/FTTAU_EXTERNAL_PS1_DR2_GENUINE_ORIGINAL_SOURCE_PILOT_RECEIPT.json) ·
[Scientific original-data protocol frozen before new PS1 queries](R2_FTTAU_EXTERNAL_PS1_DR2_SOURCE_PREREGISTRATION.md).

## Genuine survey archive data, not synthetic inputs

This is the **first direct original external Pan-STARRS1 DR2 source-row lookup** in the FT Tau two-field reference programme, in addition to the four **same exact original NASA/IPAC ZTF FITS native PSF source catalogue products** and older source checks. A single original MAST cone query, fixed **720″**, returned **1,780 independent Pan-STARRS1 DR2 mean-source rows** with the requested original catalogued PS1 `g/r` PSF mean magnitudes, mean errors, `g-r` colours and celestial positions. Their original complete response SHA-256 was saved, but no individual source row, source ID, position or original magnitude was committed.

A prospective source-quality screening independent of observed crossfield flux differences retained **405 original PS1 reference candidates** meeting declared detection-count, g/r magnitude/error/color, sky footprint, target exclusion and catalogue crowding rules. The original two-field native ZTF PSF catalogues were reobtained and verified **4/4** against the authentic previous same-exposure SHA-256 evidence. The technical Taurus cohort remained the same **24 frozen, nonrepresentative Gaia IDs**; FT Tau is still the same original Gaia technical target. No further telescope epochs were chosen.

The same-filter ZTF field-1605/field-609 exposure pairs are separated by approximately **39 seconds** within each filter. The original **g images are from 2019** and **r images from 2018**: thus **no same-epoch g−r target colour measurement** was made, despite g/r PS1 reference colours being used to model instrumental passband differences.

## Source-level original PS1-to-ZTF cross-identification

Before inspecting any flux residual, each original ZTF native source had to be a good-quality, sky-isolated ZTF reference in both same-filter fields and pass a one-to-one reciprocal ZTF↔ZTF positional match within 0.75″. Both original ZTF entries then had to correspond to **one exact independent MAST PS1 objID** within the preregistered 0.6″ tolerance in each detector field; PS1 entries had to be free of other returned PS1 neighbours within 2″. **FT Tau itself was excluded from every calibration reference list**, and magnitudes were never used to choose positional associations.

| Original source-matching outcome | g band (2019) | r band (2018) |
| --- | ---: | ---: |
| Original ZTF-native same-band reference triples including independent PS1 DR2 source | **82** | **180** |
| Original predeclared minimum independent PS1 reference triplets | 20 | 20 |
| Training references chosen by PS1 source ID alone | 42 | 94 |
| Held-out independent catalogue source IDs | 40 | 86 |
| Both detector-field pilot PS1 colour fits and held-out QC | **PASS** | **PASS** |

These are **tentative independently cross-survey catalogued reference-star matches**, *not* a statistically validated crossmatch of the FT Tau science target. The 0.6″ maximum separation does not incorporate individual stellar proper motions, fully calibrated PSF/crowding astrometry or explicit probabilistic association likelihoods.

## Actual source-level external PS1 mean-photometry model

For each band and each original ZTF field separately, train on the predeclared PS1 source-ID training subset the model

[
 m_{m PS1,mean}^{g/r} - m_{m ZTF,native}^{g/r}
 = a + b [(g-r)_{m PS1,mean} - 0.8].
]

Here the original ZTF native magnitude is **instrumental** `−2.5log10(flux in detector DN)`. The PS1 rows are independent-source-catalogue g/r mean magnitudes, but PS1 and ZTF **do not have identical filter throughput, measurement epoch, PSF systems or systematic uncertainties**. The model is a **pilot empirical PS1-relative transform**, not a certified absolute photometric calibration.

| Genuine original-data fitted field | PS1−ZTF native intercept a (mag) | Empirical g−r slope b | Held-out median residual (mag) | Held-out robust scatter (mag) |
| --- | ---: | ---: | ---: | ---: |
| g, field 1605 | **26.19613** | −0.03648 | −0.00946 | 0.03590 |
| g, field 609 | **26.08484** | −0.05456 | +0.00127 | 0.02735 |
| r, field 1605 | **26.14535** | +0.10425 | +0.00318 | 0.02444 |
| r, field 609 | **26.14388** | +0.11878 | −0.00014 | 0.02454 |

All four fit intercepts and colour slopes are within the predeclared pilot ranges. Held-out median absolute biases remain below 0.08 mag and held-out robust scatters below 0.12 mag. The fit was **not retrained on held-out source IDs**. Original field-1605 and field-609 training references overlap each other **by design** for per-band crossfield comparison, so the fields are not independent experimental populations.

As an additional descriptive historical check, compare these new source-level empirical field intercept differences with the ZTF pipeline's prior PS1-anchored science FITS image-header `MAGZP` values:

| Inter-field difference, field 609 minus 1605 | g band | r band |
| --- | ---: | ---: |
| Newly fitted PS1 source-level intercept Δa | **−0.11129 mag** | **−0.00147 mag** |
| Original ZTF same-pipeline header ΔMAGZP | −0.087808 mag | −0.000961 mag |
| Descriptive Δa − ΔMAGZP | **−0.023482 mag** | **−0.000509 mag** |

**Do not call these differences statistically significant or insignificant:** they lack a full covariance, proper-motion/color/field/PSF error budget and a certified passband transformation. Moreover ZTF's own image calibration also uses PS1 reference stars, so an independently *queried* PS1 catalogue is not necessarily independent of the stars used in the original ZTF calibration. The new experiment improves provenance and makes source-level matched-reference colours available, but it does **not** deliver an independently validated absolute flux scale.

## Decision and next scientific gate

**PASS — original external PS1 DR2 source-row retrieval, 4/4 original ZTF native source checksum checks, 82 g/180 r triple-reference associations, and pilot colour-dependent held-out consistency tests in both bands.**

**NOT PASSED / NOT CLAIMED —** source-by-source astrophysical FT Tau physical Gaia–ZTF identification, resolved blending, independent proper-motion epoch matching, reference stability over multiple telescope nights, statistically calibrated absolute photometric zero-point uncertainty, astrophysical FT Tau variability, companion detections, combined ZTF ObjectID curves or general Taurus population incidence. All four ZTF ObjectIDs were **kept separate**.

The next defensible step is to validate **FT Tau itself** with original multi-exposure sky-centroid/PSF/deblending checks plus proper-motion-aware, independent-survey source association. For photometry, repeat with independent nights and explicitly account for PS1 vs ZTF filter curves, color terms, spatial gradients and common-systematic/standard-star covariance before applying a calibration to FT Tau or combining OIDs. The previously frozen 360″ no-go and the newly validated 720″ ZTF native instrumental pilot stay intact.

The separately complete **StellarForge v2.0 engineering portfolio remains suitable for LinkedIn**, while original astrophysical Taurus study **R2 remains open**.

## Original provenance

- Original valid external MAST PS1 DR2 source response SHA-256:
  `3038bd93cd21820dbc584e7d4081f7c279109ca36a0988fc55d279a94d29ca95`.
- Original live GitHub data run `43102892830`, 30-day artifact `13892248204`.
- Original evidence ZIP SHA-256:
  `914bfa3061867451c15d9a0fdb712f958f61f38cac9b21e7d116dd14282ea12d`.
- Original derived JSON SHA-256:
  `d9ceae81d56ccdebd7dea1cc10b15c66aab4b118d4b726dc8b7e07b98f8de17f`.
- Existing unchanged original ZTF four-FITS ledger SHA-256:
  `1be4d2a0633255a6a38e36153662221b70e891016500129801ec2ec6aeac3f5d`.
- Existing unchanged 720″ ZTF internal ensemble JSON SHA-256:
  `b0186cd85d47c32cca7e87ce8a98d8a8b27448c391822ef2bed55bf0256c2558`.
- [Official MAST Pan-STARRS1 DR2 catalogue API](https://catalogs.mast.stsci.edu/docs/panstarrs.html) and [ZTF survey data products](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_api.html).

All original external individual PS1 rows, source IDs/coordinates, original ZTF native fluxes/magnitudes and FITS pixels remained ephemeral. **No raw survey photometry was committed.**
