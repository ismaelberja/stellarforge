# Taurus R2 — actual original ZTF ObjectID, filter and detector-field ambiguity

**11 November 2026 · Original public IRSA/ZTF catalogue responses. Source identification remains UNCONFIRMED.**

[Original successful live research run](https://github.com/ismaelberja/stellarforge/actions/runs/43066226324) ·
[Original 30-day derived-only artifact](https://github.com/ismaelberja/stellarforge/actions/runs/43066226324/artifacts/13875728278) ·
[Permanent complete derived OID/filter/detector field ledger](../../reports/taurus_variability_r2/REAL_TWO_FIELDS_ORIGINAL_IRSA_ALTERNATE_OBJECTIDS_NO_RAW.json) ·
[Predeclared method, written before new original data queries](R2_ZTF_ALTERNATIVE_OID_METHOD.md).

This study keeps the previously fixed **24 nonrepresentative technical Taurus Gaia source IDs**, but reviews exactly two old historical fields (FT Tau and CIDA 11). The exact historical ZTF science exposure OIDs/MJDs and prior four FITS/mask image reviews are unchanged. No new science FITS pixels were downloaded and no new observation epoch was claimed.

## Original archive retrieval and quality checks

| Original survey source-label screen | Real outcome |
| --- | ---: |
| Original Gaia DR3 exact target records returned | **2/2** |
| IRSA 2-arcsec POS+NOBS_MIN=5 positional original ZTF tables parsed | **2/2** |
| Original historical ZTF ObjectIDs queried directly by ID and parsed | **2/2** |
| Total original rows within the two positional survey requests | **2,648** |
| Rows surviving basic original photometric flags/duplicate QC | **2,212** |
| Distinct original ZTF ObjectIDs across two fields | **6** |
| Original OID/filter groups kept strictly separate | **6** |
| Historical original OIDs present in corresponding 2-arcsec positional tables | **2/2** |
| Fields containing distinct ZTF OIDs **within the same band** | **1/2 (FT Tau)** |
| Distinct same-band OID pairs that share identical field/CCD/quadrant/exposure metadata | **0** |
| Independently authenticated physical Gaia–ZTF matches | **0** |
| Confirmed new variability or companion discoveries | **0** |

These are counts of *original returned survey rows*, not independently identified stellar sources or validated photometric timeseries of the Gaia objects. Historical direct-ID queries returned 79 (FT Tau) and 469 (CIDA 11) original rows; these **overlap** the positional tables and must **not** be added to 2,648 as extra independent detections.

## FT Tau: four survey ObjectIDs, two spatially overlapping ZTF detector regions

Gaia DR3 technical target `149623711269425408`; historical g-band ZTF OID `1605115300003377`. The raw original **2-arcsec sky query** returned **1,442** photometric rows, of which **1,199** passed the basic lightcurve-ingestion quality/flag and duplicate-epoch filter.

| Original ZTF OID | Band | Original table rows | QC-accepted rows | Native field / CCD / quadrant | Median native sky-position proxy offset from Gaia* |
| --- | --- | ---: | ---: | --- | ---: |
| 1605115300003377 | g | 79 | 70 | 1605 / 0xf / 0x3 | 0.08542″ |
| 1605215300005161 | r | 137 | 117 | 1605 / 0xf / 0x3 | 0.09020″ |
| 609108400001155 | g | 468 | 404 | 609 / 0x8 / 0x4 | 0.09337″ |
| 609208400001969 | r | 758 | 608 | 609 / 0x8 / 0x4 | 0.08613″ |

**Interpretation:** two different ZTF fields/CCD/quadrants (1605/f/3 and 609/8/4) each report separate g and r ObjectIDs near the same Gaia technical position. This creates **two same-band OID pairs** requiring explicit cross-field source-association review:

- g: `1605115300003377` vs `609108400001155`.
- r: `1605215300005161` vs `609208400001969`.

In the actual original metadata **neither pair shares an identical same-exposure `filefracday/field/CCD/quadrant/filter` key**. That is expected for source records from different field/CCD areas, but it **does not prove** that each pair represents one physical star. Their small positional separations and sky overlap are clues, **not a unique crossmatch**, because ZTF catalogue coordinates inherit its own WCS and blending/PSF model.

**Do not merge any of the four OID curves yet.** Their observed date ranges, independent Gaia astrometry, source crowding, colour effects and detector-specific photometric offsets must be assessed before measuring a single FT Tau lightcurve or periodicity.

## CIDA 11: one g and one r ObjectID on the same native detector field

Gaia DR3 technical target `3419110734340795648`; historical ZTF g-band OID `610106300008010`. The raw original **2-arcsec sky query** returned **1,206** rows, of which **1,013** pass the current technical ingestion QC.

| Original ZTF OID | Band | Original table rows | QC-accepted rows | Native field / CCD / quadrant | Median native sky-position proxy offset from Gaia* |
| --- | --- | ---: | ---: | --- | ---: |
| 610106300008010 | g | 469 | 397 | 610 / 0x6 / 0x3 | 0.08578″ |
| 610206300011997 | r | 737 | 616 | 610 / 0x6 / 0x3 | 0.06198″ |

No second ZTF OID appears **in the same band** under the specific 2-arcsec and minimum-5-observation query restrictions. This **does not** exclude additional nearby faint, blended, sparse-observation or uncatalogued sources. Both returned OIDs use the same original `field/CCD/quadrant` metadata, but **different bands** cannot be treated as identical physics without original image/astrometric and source-quality checks.

CIDA 11's Gaia RUWE remains approximately **8.57**, and the previous four-image original PSFcat/reference audit failed to produce a valid target correction. This strongly limits confidence in a simple single-star physical Gaia–ZTF association or a clean source-level lightcurve assignment.

## Why this is not an astronomy discovery

The `n_quality_accepted` counts are **technical ingestion checks** (original catflags/duplicate epochs), not calibrated science-ready photometry. The approximate Gaia-vs-ZTF positional offsets marked by an asterisk are per-epoch, approximate proper-motion comparisons against **survey-reported positions**, with **no calibrated ZTF centroid uncertainties, annual parallax in this particular screen, or cross-field error budget**. They must not be interpreted as independent astrometric residuals or statistically significant detections.

A single physical star can be labelled by multiple ZTF OIDs across fields; conversely, contaminated or blended detections may also produce nearby OIDs. **Same-position and same-band evidence cannot resolve that dichotomy without independent review.** The original FITS, bitmasks and native PSFcat already reviewed for the historic g-band exposures do not provide fresh image-level deblending of **both** FT Tau fields and filters. No new genuine Gaia–ZTF physical match is claimed.

The high-RUWE CIDA 11 target remains especially review-required. Publisher-original Luhman (2023) membership-row provenance remains outstanding. The 24-source subset is deliberately nonrepresentative and cannot yield a Taurus-wide variability incidence estimate.

## Next science gate

1. **FT Tau:** collect predeclared same-season, same-filter original FITS/PSFcat/bitmasks from **both field/CCD/quadrant groups**, then compare independent reference-star astrometry and native source crowding. Do not concatenate g/g or r/r OIDs before calibration and deblending review.
2. **CIDA 11:** explicitly screen g and r independently for contamination and astrometric compatibility, while accommodating the high Gaia RUWE and unresolved multiple-star/systematic hypotheses.
3. Verify the original publisher membership source rows and observational selection; only then decide which source/time-band groups can proceed to science-quality R3 lightcurve analysis.

**R2 technical ZTF ObjectID enumeration is completed for these two fields, while R2 physical Gaia–ZTF source identification remains incomplete.** StellarForge v2.0 software was finished before this research continuation.

## Provenance and independent reproduction

Original live workflow `43066226324`; original derived-only artifact `13875728278`;
artifact ZIP SHA-256 `e607eaf67de0d4915ff56e46300b99cc66d10dde6b37ad1b8580a32c6e236612`;
uncompressed original derived JSON SHA-256
`b526e4471cec595d91cb456b5ba3a4daa9608fc81e98c811cd37944537bef1d4`;
Gaia original source-retrieval response SHA-256
`31ec0a7b19e424f06ea1d9d26ac930a1e633418e6285efe469d41c58c457cd99`.
Original R1 24-source CSV SHA-256
`9cecb94704f028a981045629ad16ecb770f51bba4b6bb3bf13dda769327ff37e`.

Official [IRSA ZTF Lightcurve Queries](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html): multiple lightcurves and ObjectIDs may correspond to a single sky position, and positional constraints and direct-ID queries are independent access methods.
