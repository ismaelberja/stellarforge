# Taurus R2 — real FT Tau Gaia DR3 proper-motion, original ZTF PSF centroids and PS1 reference astrometry

**12 November 2026 · Authentic Gaia exact-source astrometry, four SHA-verified original ZTF PSF catalogues and an independently retrieved Pan-STARRS1 DR2 source catalogue. Technical source-geometry controls PASS; physical Gaia–ZTF source identity remains UNCONFIRMED.**

[Actual original Gaia/PS1/ZTF archive run 43188238685](https://github.com/ismaelberja/stellarforge/actions/runs/43188238685) ·
[Derived-only 30-day original-data artifact](https://github.com/ismaelberja/stellarforge/actions/runs/43188238685/artifacts/13929113546) ·
[Permanent original-data no-raw astrometry evidence](../../reports/taurus_variability_r2/FTTAU_GAIA_PS1_ZTF_FOUR_ORIGINAL_TARGET_ASTROMETRY_NO_RAW.json) ·
[Precommitted scientific protocol](R2_FTTAU_GAIA_PS1_ZTF_TARGET_ASTROMETRY_PREREGISTRATION.md).

## Original data and source selection

FT Tau remains original provisional technical Gaia DR3 **149623711269425408** from the unchanged **24-source nonrepresentative Taurus seed**. Gaia's exact-ID five-parameter astrometry and full 5×5 formal covariance were recovered from the original Gaia@ARI TAP response (SHA-256 `399b5498d8d8a8a646073dfc029895ed64902940896d1789c63833a18074b642`). The model propagates the J2016.0 Gaia source to the four **previously preselected ZTF observation MJDs**, accounting for source proper motion and an approximate **geocentric annual parallax**.

The original **four FT Tau ZTF full `psfcat.fits`** detector-field catalogue bytes matched exactly the previously audited original-science-source file hashes, with no replacement or new observing epoch. Each of the two g-field and two r-field exposures was separated by ~**39 s within each band**. However, g observations date to **2019-11-19**, and r observations to **2018-11-03**; no simultaneous cross-filter color or genuine inter-year proper-motion measurement is established from these four astrometric records.

A new original MAST source query returned **1,780 Pan-STARRS1 DR2 mean source records**. **Important provenance caveat:** the original raw CSV SHA-256 (`d50248c88891095e33b0e8d6b30596d027bda244e1c4e4785b594c67f4bd1b74`) **differs** from the original SHA recorded in the previous PS1 color pilot (`3038bd93cd21820dbc584e7d4081f7c279109ca36a0988fc55d279a94d29ca95`). The same full 1,780-row count and original fixed API request were used, but the study did **not** establish that individual rows are byte-identical or rule out source reordering/version differences. The new complete, valid catalogue is therefore explicitly flagged `COMPLETE_ORIGINAL_MAST_PS1_RESPONSE_SHA_CHANGED_REVIEW`, **not** represented as identical to the older response. No target ID conclusions depend on silently substituting historical source rows.

## Four real FT Tau ZTF original catalogued source candidates

For each original exposure and **before examining source fit results**, the source nearest to the Gaia five-parameter propagated position was considered at a fixed 0.6″ radius, with the next nearest original native PSFcat row required beyond 1″ and original PSF flag/profile/SNR checks required:

| Original FT Tau exposure | Nearest native ZTF PSF source vs epoch-propagated Gaia | Second nearest native PSF source | Native PSF sources inside 2″ | Provisional single candidate |
| --- | ---: | ---: | ---: | --- |
| g / ZTF field 1605 | **0.056791″** | 12.397513″ | 1 | yes |
| g / ZTF field 609 | **0.069015″** | 46.446880″ | 1 | yes |
| r / ZTF field 1605 | **0.035434″** | 20.317638″ | 1 | yes |
| r / ZTF field 609 | **0.063244″** | 10.221781″ | 1 | yes |

All **4/4 original native PSF-catalogue target candidates** pass these frozen local-geometry and PSF-profile technical checks, and both near-simultaneous **same-filter** two-field pairs contain two such sources. This is **NOT confirmation of a unique physical Gaia–ZTF FT Tau star**. The original native ZTF source catalogue can omit faint, closely blended, non-detected or optically anomalous objects. The previous FITS mask/bright-peak heuristic passed, but it also did not independently measure blend completeness.

## Independent PS1 mean-source neighbourhood of FT Tau

The original **1,780 PS1 DR2 mean-source rows**, including catalogue rows that were unsuitable as photometric calibrators, were checked for their static catalogue sky positions near Gaia's J2016.0 source and the Gaia prediction at the 2018/2019 original ZTF observation dates:

| Gaia coordinate used as centre | Nearest original PS1 DR2 mean-position separation | Number of PS1 rows inside 1″ | Rows inside 3″ |
| --- | ---: | ---: | ---: |
| Gaia J2016.0 source reference position | **0.056120″** | 1 | 1 |
| Gaia predicted at r-band 2018 exposures | **0.119173″** | 1 | 1 |
| Gaia predicted at g-band 2019 exposures | **0.142935″** | 1 | 1 |

The next PS1 catalogue entry is more than **16″** from these positions. These observations provide *source-isolation evidence only down to the unknown PS1 catalogue detection, resolution and deblending limits*. Crucially the PS1 DR2 mean-source request selects sources with **at least five detections**, and their per-source PS1 mean astrometric epochs and proper motions were **not** obtained. Thus this cannot determine whether the nearby PS1 mean position is the *same physical moving Gaia target* at the original ZTF epoch.

## Reference-star positional offsets from original independent catalogue rows

The source-position experiment reused only the independently queried, single-PS1-ID-matched, source-disjoint **82 g-band** and **180 r-band** original ZTF1605/ZTF609/PS1 reference source triplets. FT Tau itself was excluded by the original 15″ target-core rule. For each original ZTF field separately the median difference `native ZTF sky position − PS1 DR2 mean sky position` was fitted using source IDs fixed to the training group, and the geometry was compared on **held-out PS1 source IDs** not used for the median:

| Same-filter reference controls | g | r |
| --- | ---: | ---: |
| Genuine source-disjoint PS1/ZTF/ZTF triplets | 82 | 180 |
| Training references | 42 | 94 |
| Held-out references | 40 | 86 |
| Field 1605 / 609 reference held-out geometry gates | **PASS / PASS** | **PASS / PASS** |
| Held-out robust east-coordinate scatter, field 1605 / 609 | 0.056941″ / 0.054868″ | 0.047319″ / 0.044260″ |
| Held-out robust north-coordinate scatter, field 1605 / 609 | 0.043987″ / 0.044450″ | 0.030950″ / 0.032023″ |

All reference held-out signed median offsets are under the predeclared 0.10″ gate and each of the two coordinate robust scatter measures under 0.15″. **This does not deliver an independently calibrated instrument WCS error budget**: PS1 mean epoch/proper-motion differences, field variation, catalogued-source nonstellar blends, native ZTF centroid errors, source filtering and shared source-calibration selection effects remain unresolved.

For the FT Tau native candidates, subtracting each field's *training reference median* gives **descriptive differential offsets from epoch-propagated Gaia**:

| Original exposure | Reference-relative east offset | Reference-relative north offset |
| --- | ---: | ---: |
| g 1605 | −0.035503″ | +0.006418″ |
| g 609 | +0.000734″ | +0.035893″ |
| r 1605 | −0.004080″ | +0.009709″ |
| r 609 | +0.011431″ | +0.036079″ |

The cross-field differences of these reference-relative target offsets for pairs only **39 seconds apart** are **(+0.036237″, +0.029475″)** in g, and **(+0.015511″, +0.026370″)** in r, field609 minus field1605. These are *catalogue-level descriptive* differences: without independent uncertainty covariance and PS1 source epoch/PM calibration they must **not** be turned into significances, measured motion, or validated physical crossmatches.

## Scientific decision and remaining blockers

**PASS — genuine source-level original Gaia and ZTF exact-file retrieval, 4/4 provisional FT Tau native PSF source-position/quality checks, full valid independently fetched 1,780-row PS1 snapshot with explicitly changed raw SHA, 82-g and 180-r external reference-source triples, and both-band held-out reference-geometry consistency.**

**R2 physical FT Tau identity remains OPEN.** No source is independently authenticated as a unique physical Gaia-to-ZTF FT Tau stellar counterpart. No independently calibrated stellar target source position with complete WCS/crowding/PSF uncertainty, no PS1 source proper motion or reference epoch propagated to the original ZTF exposures, no certified FT Tau photo-variability, no new companion and **no merging of four ZTF ObjectID lightcurves**.

The next rigorous increment should retrieve **actual independently dated multi-epoch astrometric measurements of a targeted PS1 or Gaia counterpart**, original high-angular-resolution imaging/PSF deblending, and check the original Luhman Taurus identification. An additional **multi-night original ZTF source-centroid** comparison would help distinguish a fixed target source from source confusion but should not be used to retroactively choose a convenient observing sample. Until a physical match and complete uncertainty budget are established, **R3 astrophysical lightcurve inference remains blocked**.

StellarForge software engineering **v2.0 remains complete and fit for an honest CV/LinkedIn portfolio description**; the observational feasibility pilot continues separately.

## Original-data provenance

- Real original Gaia/PS1/ZTF data run `43188238685`; derived-only artifact `13929113546`.
- Original artifact ZIP SHA-256 `c84a32e4ecbdc8de7cb178bb92797ed48db5cd793b80e5cd7a8c21129e611666`.
- Original derived JSON SHA-256 `12616b85f160495846ba6804fe4a1ff45d36128b694a7f59946623e8b397533d`.
- New independently retrieved MAST PS1 source response SHA-256 `d50248c88891095e33b0e8d6b30596d027bda244e1c4e4785b594c67f4bd1b74`.
- Gaia exact-source formal-record CSV original SHA-256 `399b5498d8d8a8a646073dfc029895ed64902940896d1789c63833a18074b642`.
- Original no-raw scientific input ledger  repo previous FT Tau FITS, PS1 heldout, R1 seed source footprints, source values in the permanent artifact.
- [Gaia DR3 epoch J2016.0 and astrometry provenance](https://gaia.aip.de/cms/data/gdr3/) · [MAST PS1 DR2 catalogue](https://catalogs.mast.stsci.edu/docs/panstarrs.html) · [official original ZTF science source products](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_api.html).

No original Gaia/PS1 source tables, per-star source positions/IDs, native raw magnitude rows or science FITS pixels were committed; only derived anonymous source-position offsets, reference medians, counts, provenance hashes and explicit astrophysical limitations are retained.
