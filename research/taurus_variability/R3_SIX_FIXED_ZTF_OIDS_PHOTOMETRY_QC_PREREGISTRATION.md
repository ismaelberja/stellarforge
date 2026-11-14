# Taurus R3 — preregistered six-ObjectID original ZTF photometric technical coverage pilot

**14 November 2026, before any new R3 raw photometry response.**

## Precise purpose

Measure archive **lightcurve availability, good-epoch counts, time span, cadence/season bins and fixed-quality rejections** for the six ZTF ObjectIDs already identified in the [frozen original R2 exact-ObjectID ledger](../../reports/taurus_variability_r2/REAL_TWO_FIELDS_ORIGINAL_IRSA_ALTERNATE_OBJECTIDS_NO_RAW.json). This is a *survey technical coverage feasibility audit*, **not** a physical Gaia↔ZTF crossmatch, verified stellar light curve, periodogram, astrophysical variability result, new variable star/companion, or publication.

No ObjectID or epoch is selected because of its observed variability. Both named Taurus technical Gaia targets remain **UNVERIFIED physically** against ZTF, and their Original OIDs cannot be merged across survey field/filter.

## Six immutable inputs (from R2, not chosen after R3 data review)

| Technical label | Gaia DR3 (for lookup context only) | Frozen ZTF ObjectID | Native band | R2 old original positional-query rows |
|---|---|---|---|---:|
| FT Tau | 149623711269425408 | `1605115300003377` | g | 79 |
| FT Tau | 149623711269425408 | `1605215300005161` | r | 137 |
| FT Tau | 149623711269425408 | `609108400001155` | g | 468 |
| FT Tau | 149623711269425408 | `609208400001969` | r | 758 |
| CIDA 11 | 3419110734340795648 | `610106300008010` | g | 469 |
| CIDA 11 | 3419110734340795648 | `610206300011997` | r | 737 |

The old R2 positional queries were made at a previous time and potentially different public collection. These old row counts **must NOT be used as a new R3 observation or asserted equal to newly fetched exact-ID DR24 rows**. The two star labels are *original R2 working names*, not scientifically certified physical ObjectID identifications.

## Original-data protocol, frozen before R3 archive queries

1. At most **one official original IRSA ZTF-LC-API GET per exact ObjectID** at the official URL `https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves`, with `ID=<frozen>`, `FORMAT=csv`, and explicitly fixed public collection `COLLECTION=ztf_dr24`. **No** positional cone, no alternative OID, no 2026 release switching if unavailable, no fallback to another collection, no source/detector re-identification. The latest public release as currently shown by IRSA is DR24 (22 January 2026). [IRSA original API](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html) · [IRSA ZTF release list](https://irsa.ipac.caltech.edu/Missions/ztf.html).
2. Limit each response to **4 MiB**, timeout **40 s per request**, cap six original requests, use max **two concurrent workers**. Record full request URL, HTTP status, response Content-Type group, response length, original raw byte SHA-256 and specific source error types in **derived-only** artifacts. Never commit raw original ZTF CSV, original per-epoch magnitudes, individual observation timestamps, source RA/DEC, CCD images, or private/nonpublic data.
3. Use existing `stellarforge.ztf_photometry.inspect_ztf_bytes` / `parse_ztf_table` without any target coordinate in order to avoid pseudo-match or fixed-position approximation; require **one exact ObjectID per response**, correct preregistered filter per ObjectID and no mixed physical-source merges.
4. Pre-existing local photometric mask: reject any observation if `catflags & 32768 != 0`; reject invalid/nonfinite magnitude, magnitude error, epoch, filter, ID, inconsistent clocks or exact duplicate OID/band/clock/epoch according to existing parser. **No sigma clipping and no data-driven magnitude/amplitude selection**. The ZTF catflags bit-15 screen handles poor image quality; it does not prove no blending, full noise covariance, true source identity or valid photometric calibration.
5. Original R1 eligibility thresholds **each independent OID/band/clock series**: **at least 30 locally QC-retained visits** and **time span ≥90 days**, both required. Record failures separately; do not approve faint source observations merely because the provider returned 30 raw rows. No secondary quality criteria added after viewing the data. Preserve distinct MJD, HMJD and HJD axes as reported; no time-system conversion, no cross-clock aggregation.
6. For simple coverage illustration, group a fixed OID/band/clock series into **365-day bins anchored to its first retained observation**; record counts and number of nonempty bins but not the underlying individual epochs. This is an *engineering cadence proxy*, not season-by-calendar or astrophysical periodicity detection. Aggregate per-object raw/QC and masked rejections only, no photometric amplitude/dispersion, colour, period, source physical classification.
7. If any original API response errors, returns unexpected content, more than one OID/filter, lacks required columns or no qualifying visits, **record NO-GO for that source, never substitute a different response or infer a negative astrophysical detection**. Results with the technical count/span thresholds met receive only `TECHNICAL_OID_PHOTOMETRY_COVERAGE_PASS__PHYSICAL_TARGET_IDENTITY_UNVERIFIED` and cannot be promoted to `R3_PHYSICAL_GAIA_STAR_VARIABILITY_ELIGIBLE`. The R2 24-source independent physical identity NO-GO remains true for all.
8. Exact R1 technical nonrepresentative denominator remains **24 Gaia seed rows**, but this *focused* R3 original photometry pilot covers **only six original ZTF OIDs / two Gaia working labels** chosen before R3 review. Neither the six OIDs nor their observations represent an unbiased Taurus population sample. No variation rate, new companion, physical stellar period or newly calibrated source uncertainties will be claimed.

## Expected reproducible deliverables

- One original-data GitHub Actions job and temporary derived-only artifact.
- One permanent SHA-linked **six-row** no-raw source/coverage/rejections ledger and full **per-OID technical coverage report**, rejecting any scientifically unsupported identity claims.
- Synthetic + source-receipt strict regression tests, and one offline post-merge main CI confirmation. If all six original source queries fail, publish the original-provider failure ledger and classify the pilot explicitly **INCOMPLETE/ARCHIVE_BLOCKED**, not as six nonvariable stars.
- **R3 status:** technical pilot only. R3 physical Taurus stellar-variability inference remains blocked until independent source matching passes R2 physical-identity gates.

*Frozen at initial branch creation: no R3 live archive response inspected yet.*
