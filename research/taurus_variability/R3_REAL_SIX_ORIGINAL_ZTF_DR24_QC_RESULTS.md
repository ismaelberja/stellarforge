# StellarForge / Taurus R3 — original ZTF DR24 six-ObjectID photometry and archive coverage

**14 November 2026.** Two genuinely executed, prospectively registered original NASA/IPAC IRSA ZTF lightcurve API experiments. This is an **incomplete original archive-access / technical time-series feasibility pilot**, NOT a validated Gaia–ZTF physical-source match, physical stellar lightcurve analysis, time-domain variability detection, periodogram or new astronomical object.

[Initial six-ObjectID pre-registration](R3_SIX_FIXED_ZTF_OIDS_PHOTOMETRY_QC_PREREGISTRATION.md) · [Three original-timeout-only recovery preregistration](R3_THREE_ORIGINAL_ZTF_TIMEOUTS_RETRY_PREREGISTRATION.md) · [first original data Actions run 43593335135](https://github.com/ismaelberja/stellarforge/actions/runs/43593335135) · [second original provider-only retry run 43593994009](https://github.com/ismaelberja/stellarforge/actions/runs/43593994009).

## Scientific boundary

The old [R2 24-source identity study](R2_FINAL_24_SOURCE_SCREENING_DECISION.md) completed an observational catalogue/source-access and ambiguity audit with **0/24 independently authenticated physical Gaia↔ZTF counterparts**, although the **24/24 original Luhman member-list Gaia IDs and positions** have been validated with the published original author MRT table. The original R1 cohort is deliberately nonrepresentative.

R3 cannot yet label any ZTF ObjectID data as the light curve of a specific Gaia young star. The six **fixed** original ObjectIDs below are labelled *FT Tau / CIDA 11 survey-position candidates for navigation only*; they must remain separate by original survey ObjectID, filter and reported time system. No original ZTF curves are merged and no astrophysical variability statistics are computed.

## Original DR24 public source experiment: what the survey really returned

Each original query was issued once using fixed `ID=<original_oid>&FORMAT=csv&COLLECTION=ztf_dr24` (no sky cone). The first live GitHub Actions experiment ran two bounded workers (40-second per-request timeout). **Exactly three FT Tau-context original ObjectIDs returned valid genuine HTTP 200 CSVs** and were independently filtered in memory with the already existing bit-15 image/photometry quality flag `catflags & 32768`; the other three timed out. One further prospectively documented **serial-only** exact-ID retry with longer **85-second** per request also timed out for all three, with no provider response body. These were server-access failures, not astronomical nondetections or data-quality failures.

| Frozen R2 source label | Exact original ZTF ObjectID | Filter | Genuine DR24 original CSV rows | QC-accepted visits | Bit-15 rejected | Time span (days) | R1 technical ≥30 visits and ≥90 days |
|---|---|---|---:|---:|---:|---:|---|
| FT Tau (not physically authenticated) | `1605115300003377` | g | **79** | **70** | 9 | **1,870.876898** | **PASS — survey ObjectID only** |
| FT Tau (not physically authenticated) | `1605215300005161` | r | **137** | **117** | 20 | **2,528.096678** | **PASS — survey ObjectID only** |
| FT Tau (not physically authenticated) | `609108400001155` | g | **468** | **404** | 64 | **2,617.952292** | **PASS — survey ObjectID only** |
| FT Tau (not physically authenticated) | `609208400001969` | r | Timeout twice | Not assessed | Not assessed | Not assessed | **ARCHIVE UNAVAILABLE** |
| CIDA 11 (not physically authenticated) | `610106300008010` | g | Timeout twice | Not assessed | Not assessed | Not assessed | **ARCHIVE UNAVAILABLE** |
| CIDA 11 (not physically authenticated) | `610206300011997` | r | Timeout twice | Not assessed | Not assessed | Not assessed | **ARCHIVE UNAVAILABLE** |

**Real original photometric data inspected in memory:** **684** original source rows, **591** retained after the unmodified source-quality bit-15 mask, **93** rejected for original `catflags & 32768`. The three returned source series all used reported **MJD**, handled separately with no clock conversion or photometric magnitude clipping. Their observational spans exceeded 90 days. Per-source 365-day bins anchored at each first QC-accepted original measurement were, respectively:

- `1605115300003377` (g): **23, 33, 0, 0, 10, 4** visits; 4 nonempty bins.
- `1605215300005161` (r): **22, 49, 0, 0, 12, 11, 23** visits; 5 nonempty bins.
- `609108400001155` (g): **61, 79, 80, 34, 46, 43, 51, 10** visits; 8 nonempty bins.

The two explicit zero-count gaps in the first and second OID illustrate strong cadence irregularity. These are fixed technical source data coverage counts, **not seasonal periodicity, intrinsic variability, missing astrophysical stars, or calibrated measurement noise**. The two ~2,600-day baselines do not imply every yearly bin is populated.

## Reproducible original provenance

| Evidence | Original checksum / source |
|---|---|
| First exact six-OID run, 40 s per source | [Actions 43593335135](https://github.com/ismaelberja/stellarforge/actions/runs/43593335135), [artifact 14113496602](https://github.com/ismaelberja/stellarforge/actions/runs/43593335135/artifacts/14113496602) · ZIP SHA-256 `6e9e1cdbba946d9f7c5036e74a42917bb4011530dfec1d289b4b30c47f393049` |
| Immutable first six-OID derived-only receipt | [R3 first exact-source no-raw JSON](../../reports/taurus_variability_r3/R3_SIX_ORIGINAL_DR24_FIRST_REQUESTS_NO_RAW.json) · original artifact source-JSON SHA-256 `3d9e864d2028c5040f4c7bd2860d8991fd51e7e22a4f8185029982467d4852ec` |
| Three original timeout-only retries (serial, 85 s each) | [Actions 43593994009](https://github.com/ismaelberja/stellarforge/actions/runs/43593994009), [artifact 14113996740](https://github.com/ismaelberja/stellarforge/actions/runs/43593994009/artifacts/14113996740) · ZIP SHA-256 `69f37df9f57c2dc49e4636740fb74c8c429d67e3d250b92201696edd26d89104` |
| Immutable three-timeout derived-only receipt | [R3 second original attempt no-raw JSON](../../reports/taurus_variability_r3/R3_THREE_ORIGINAL_DR24_TIMEOUT_RETRY_NO_RAW.json) · original artifact source-JSON SHA-256 `3de1c4028cf138d450a06ad48062952bd0b439aad4b4602f0815629df8998ebb` |
| Exact original data response bytes | g1605 79-row: `64916a8825f14f1f39dbf16aaf3e404d04cab5c0ab5a258b7d53973f0cf0af87`; r1605 137-row: `617c76349d0ed00c34e0cbcbcae92a51916970a114725d2e36413a94eefcefbf`; g609 468-row: `391b35a3232341f0c1f9701522cb52aced730d4a9098da9d3ae6c40f2d6d8004` |

The exact g1605 returned CSV SHA matches the earlier genuine R2 direct-ObjectID archive response, supporting byte-level reproducibility, **not** an independent new physical star measurement. Original full raw ZTF tables, individual timestamps, source positions, per-epoch photometric magnitudes and source FITS pixels were never uploaded or committed; only aggregated counts and SHA digests are public. Temporary original artifact links expire under normal GitHub retention; permanent no-raw receipts remain available in this repository.

## Status and best next science task toward R4–R6

- **Completed:** original live access for six preselected ObjectIDs with explicit response/no-response outcomes; 3 authentic source CSVs quality-tested using R1 `30 visits / 90 days`; per-ObjectID, per-filter source count, coverage gaps, unmodified quality-screen exclusions, source byte hashes, and reproducible synthetic and no-raw receipt regressions.
- **Not complete:** all six original ObjectIDs successfully fetched in this specific DR24 pilot; physical Gaia–ZTF identity of any target; per-source independent WCS/PSF/instrumental covariance and blend accounting; scientifically accepted original stellar ZTF time series.
- **Next decision:** do not repeat blind large archive requests. Pursue a genuinely independent published/high-resolution astrometric source/deblend association for at least one pre-registered ObjectID, or—if still unavailable—write an explicitly **methodological R4/R5 negative-feasibility report** and finish R6 honestly without a variable-star claim. The original 24-source nonrepresentative cohort cannot be used for variability incidence rates, and the six-object technical pilot cannot be renamed as a new six-star sample.

The ZTF DR24 original official API and data quality bit-15 filter are documented by [IRSA lightcurve program interface](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html) and the [IRSA public ZTF DR24 release portal](https://irsa.ipac.caltech.edu/Missions/ztf.html). These sources document protocol/flags, **not** the astrophysical interpretation of these specific original stars.

```bash
python -m pytest -q
python -m scripts.audit_taurus_r3_six_original_source_receipts
# The following are separate networked original-data experiments and are
# NOT needed for offline scientific evidence verification:
# python -m scripts.run_taurus_r3_original_six_oid_qc
# python -m scripts.run_taurus_r3_three_timeout_recovery
```
