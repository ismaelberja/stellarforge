# Taurus R2 — real original Gaia-only reference stars against same-epoch ZTF native PSF positions

**11 November 2026 · Authentic Gaia DR3 + NASA/IPAC original ZTF catalogue data, no new astronomical science epochs.**

[Actual successful original-data run](https://github.com/ismaelberja/stellarforge/actions/runs/43063054380) ·
[Original 30-day no-raw evidence artifact](https://github.com/ismaelberja/stellarforge/actions/runs/43063054380/artifacts/13874706194) ·
[Permanent 4-exposure, 7-Gaia-source derived-only result](../../reports/taurus_variability_r2/GAIA_ONLY_CONTROLS_ORIGINAL_PSF_OFFSETS_NO_RAW.json) ·
[Method predeclared before examining observations](R2_GAIA_DISJOINT_CONTROL_OFFSET_METHOD.md)

The original complete **24-source nonrepresentative technical Taurus cohort** is unchanged. This step examines precisely **two original field targets (FT Tau and CIDA 11)** and their previously selected **five Gaia-only reference candidates** in the **same four historical ZTF original g-band science exposures** studied in earlier StellarForge releases. The original FITS/mask checks were [completed separately in the previous R2 step](R2_REAL_FT_TAU_CIDA_11_FITS_SOURCE_GATES.md). This follow-up did not download new science image pixels and did not add new observing dates.

## What was actually found

| Authentic original data control | Verified result |
| --- | ---: |
| Exact Gaia DR3 full five-parameter catalogue records | **7/7** |
| Distinct Gaia-only control stars fixed before this analysis | **5** |
| Strict CIDA 11 Gaia-only controls, from v1.17 | **4** |
| Exploratory FT Tau Gaia-only control, from v1.18 | **1** |
| Exact dated original ZTF `psfcat.fits` catalogues evaluated | **4/4** |
| Exposures with at least 3 acceptable **strict** references | **1/4** |
| Exposures where the target *also* passes all target/reference astrometric and native-source gates | **0/4** |
| Eligible scientifically provisional **differential target-minus-reference offsets** | **0** |
| Independently confirmed physical Gaia–ZTF matches | **0** |
| New variable stars or companions confirmed | **0** |

The **one field with four accepted strict Gaia-selected controls is the earlier CIDA 11 exposure**, but the target itself did not pass the native PSF fit profile screen and has Gaia RUWE 8.56752. Thus the control field cannot be used to manufacture a valid target offset. In the second CIDA 11 exposure only two strict control sources pass the native PSF screen; the target has high RUWE. FT Tau's only control belongs to a separately labelled **relaxed exploratory** quality tier, so it cannot meet the three-strict-control threshold in either exposure.

### By original dated exposure

| Field | Original g-band ZTF MJD | Gaia-only field controls accepted | Reference quality stratum | Descriptive native-minus-Gaia reference median (east, north) | Safe field+target correction? |
| --- | ---: | ---: | --- | --- | --- |
| FT Tau | 58388.389016 | 1 | Exploratory, relaxed | (−30.145, −152.528) mas | **No — only one exploratory reference** |
| FT Tau | 58491.184780 | 1 | Exploratory, relaxed | (+27.626, +322.071) mas | **No — only one exploratory reference** |
| CIDA 11 | 58475.113750 | **4** | Strict Gaia-only | (−171.029, +172.358) mas | **No — target PSF QC / high RUWE** |
| CIDA 11 | 58849.135984 | **2** | Strict Gaia-only | (+6.257, +21.739) mas | **No — insufficient strict controls / high RUWE** |

These medians are **descriptive offsets of survey-native catalogue source coordinates relative to epoch-predicted Gaia source coordinates**. They are *not* calibrated telescope WCS corrections, measured orbital motion, or statistical uncertainties. In particular, the two epochs can have **different accepted control subsets**. It would be incorrect to compare their median changes as if the sample and error model were identical or to apply them to the science target without passing the predeclared gates.

#### Per-source quality review

FT Tau's native candidate passes the provisional original `psfcat` fit/profile flags on both dates; its separate sole exploratory Gaia control also passes on both dates. This shows an **illustrative target/control positional comparison**, not a field-calibrated WCS residual.

For CIDA 11, all four strict Gaia-only controls pass the native candidate profile gate on MJD 58475.113750, but the technical target is **NATIVE_PSF_FIT_PROFILE_OR_FLAG_REVIEW_REQUIRED**. At MJD 58849.135984 the target is a provisional native source candidate, while two of the four strict controls are **NATIVE_PSF_FIT_PROFILE_OR_FLAG_REVIEW_REQUIRED**. Its Gaia RUWE ≈8.57 makes the target's underlying single-source formal astrometric model especially uncertain at both dates. An elevated RUWE is **not** evidence of a newly discovered companion.

The original native ZTF full PSF-fit catalogue row counts remain 3,970 and 5,569 for FT Tau and 5,313 and 12,355 for CIDA 11, reflecting the exact same historic science exposures as earlier phases.

## What this experiment *does not* prove

- Gaia original source identifiers were selected independently of the **current StellarForge R2 pixel fitting** and excluded from the initial v1.8 StellarForge reference-star list. However, it has **not** been shown that the original ZTF DAOPhot PSF-building process excluded those stars. They are **not a verified ZTF instrument-training-independent validation set**.
- Gaia's externally measured sky positions are genuinely separate observations from ZTF, but the selected *ZTF* native `psfcat` positions come from ZTF's **own same-exposure processing and WCS model**. They cannot by themselves calibrate an independent astrometric uncertainty or discover a physical Gaia–ZTF counterpart.
- The three-strict-control threshold is a **conservative study eligibility rule**, not a universal measurement of required reference-star count or a published instrument astrometry standard. Failing it is **underpowered or review-required**, not a stellar nondetection.
- The FT Tau exploratory tier has relaxed original Gaia selection criteria; it cannot be silently relabelled as strict and has just one comparison star.
- The CIDA 11 target's high Gaia RUWE and rejected native profile on one epoch mean the apparent target offset must **not** be corrected or attributed to orbital motion, variability or a physical companion.
- The 22/24 original IRSA sky positions accessible across prior live runs remain **positional catalogue access** only. No authentic Gaia–ZTF physical associations are obtained from this seven-source control experiment.
- Original publisher Luhman (2023) Taurus membership-row provenance and independently deblended alternate ZTF OIDs remain pending. No general Taurus population variability incidence can be computed.

## Research decision

**This R2 subtest is complete, and its result is a scientifically useful NO-GO for applying a validated differential target offset to the four historic images.** The failure is not a coding failure or a stellar nondetection: it identifies precisely insufficient/heterogeneous reference quality for FT Tau and questionable CIDA 11 target astrometry/fit eligibility.

**R2 physical source identity remains open.** The next meaningful validation is to audit alternative same-position ZTF ObjectIDs and their field/filter provenance and to seek an independent externally calibrated reference/crowding model (or add genuinely suitable pre-registered Gaia controls and original ZTF epochs before inspecting outcomes). Do not claim a Gaia–ZTF physical match, new stellar variability, new companion or independently calibrated ZTF astrometry without passing new predefined evidence gates.

The finished **StellarForge v2.0 software portfolio is unchanged**.

## Provenance

Original workflow: `43063054380`, derived-only GitHub artifact: `13874706194`;
original ZIP SHA-256:
`0c6e872f101c3a737fb2200fa2264ca4f75701fe9cc8d12d00320dbc5d77963a`;
uncompressed original JSON SHA-256:
`4b0d430309b0f368eca39a2b6027373192b822dc2358b6402019ab1d9e113413`;
original full Gaia DR3 source-response SHA-256:
`004068827dd1eff677ef7443f3fe54bd096ee9a22e3d52c2b10ac644b2977c46`.

For comparison: [original Gaia-only heldout-star results v1.17](../../reports/new_gaia_holdouts_v1.17/REAL_DISJOINT_GAIA_CONTROL_AND_SHIFTED_SKY_RESULTS.md), [FT Tau relaxed source tier v1.18](../../reports/psf_training_ft_tau_v1.18/REAL_ZTF_LOG_AUDIT_AND_EXPLORATORY_FT_TAU.md) and [official ZTF source-processing cautions](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html).
