# R2 — Original IRSA nine-source access recovery

**11 November 2026 · original ZTF public archive source data, not authenticated Gaia–ZTF counterparts.**

[Actual completed live GitHub Actions run](https://github.com/ismaelberja/stellarforge/actions/runs/43042786341) ·
[Original 30-day derived-only artifact](https://github.com/ismaelberja/stellarforge/actions/runs/43042786341/artifacts/13866785881) ·
[Full nine-source per-request derived ledger](../../reports/taurus_variability_r2/IRSA_NINE_ORIGINAL_RESPONSE_SOURCE_LEDGER_NO_RAW.json) ·
[Immutable provenance receipt](../../reports/taurus_variability_r2/IRSA_NINE_ORIGINAL_RESPONSE_RECEIPT_NO_RAW.json).

The original study sample remains the **24 nonrepresentative Taurus technical Gaia DR3 IDs**, fixed before analysis. All nine re-queried source positions were determined from the archived previous [22-source diagnostic](R2_REAL_IRSA_22_FAILURE_DIAGNOSIS_RESULTS.md), not from any apparent variability.

## Actual results

| Distinct Gaia technical source-position access status | Sources |
| --- | ---: |
| Fixed Taurus technical sources | **24** |
| IRSA ZTF positions with previously parseable original tables (older runs) | **15** |
| Previously unsuccessful source positions retested once | **9** |
| Newly recovered parseable original ZTF positional tables | **7** |
| **Cumulative positions with original ZTF positional responses across separate runs** | **22/24** |
| Original source positions remaining without a populated parseable table | **2** |
| Scientifically confirmed physical Gaia–ZTF source matches | **0** |
| New stellar variability results confirmed | **0** |

The seven newly recovered original tables contain **11,058 rows**, summed across the seven sky-position requests. This number represents *original survey table rows*, **not** the number of different astrophysical stars, scientifically quality-accepted epochs or uniquely identified Gaia counterparts.

### Per-source original archive outcomes

| Original Gaia DR3 seed ID | Query result | Rows in returned table |
| --- | --- | ---: |
| 162259951730099968 | Parsed original CSV, NOBS_MIN=5 | 1,795 |
| 156732977357829888 | Parsed original CSV, NOBS_MIN=5 | 2,962 |
| 156577881796362496 | Parsed original CSV, NOBS_MIN=5 | 992 |
| 149623711269425408 | Parsed original CSV, NOBS_MIN=5 | 1,442 |
| 146764465639042176 | Parsed original CSV, NOBS_MIN=5 | 1,376 |
| 3418414193726125184 | Parsed original CSV, NOBS_MIN=5 | 1,412 |
| 3314244366165299584 | Valid zero-row table, NOBS_MIN=5 | 0 |
| 3314299238667410176 | Parsed original CSV, NOBS_MIN=5 | 1,079 |
| 3406270362673330944 | HTTP 400 on NOBS_MIN=1 | Unknown |

**The two unresolved cases are not nonvariable Taurus stars.** The first returns no rows **under the specific ZTF query and five-epoch requirement**. The second returns an HTTP protocol/client error when testing the lower NOBS_MIN=1 restriction. Neither supplies a defensible physical source light curve for this new study phase.

Notably, all seven new successes used the **same original-format `NOBS_MIN=5` query as the initial access study**, now allowed to run with a modest 25-second timeout. The remaining zero/HTTP400 outcomes should be addressed separately (for example via source IDs in the official catalog, original images or provider clarification), without fabricating a ZTF detection.

## Explicit astrophysical limitations

- These are **Gaia-seed-centred 2-arcsec ZTF positional queries**, not verified matches to the same astrophysical objects. The presence of a populated table does **not** prove that any particular ZTF OID belongs to the target Gaia ID.
- Multiple original ZTF OIDs/filters/time conventions must remain **separate**, without automatically concatenating light curves or attributing variability to Gaia stars.
- Gaia survey astrometric RUWE, neighbouring catalogued sources and proper-motion propagation are helpful **preliminary** checks, not original-image validation.
- The original ZTF science FITS frames, masks, PSFcat, independent WCS and crowding review **were not executed** during this nine-position access run.
- Original publisher Luhman Taurus membership verification is still pending. The technical 24-source seed is nonrepresentative, so these observations cannot measure a Taurus-wide variable-star fraction.
- No raw original ZTF CSV, private IRSA response bodies or observational image pixels were committed; the GitHub evidence contains source-access status, response SHA-256 and original row counts only.

## Scientific decision and next step

**Source access is now 22/24, but R2 physical source identity is still open.** Further retries alone no longer provide the strongest scientific gain. Prioritise **independent original ZTF FITS image/mask and nearest-neighbour astrometric checks** for a small, predeclared subset of the 22 retrieved positions (including the already documented FT Tau and CIDA 11 historical original science-image cases) and verify the original Luhman membership records. The two unresolved access cases remain in the study denominator and should be reported as missing/ambiguous, never as scientifically nonvariable.

The software portfolio StellarForge v2.0 remains complete. This independent research continues with **zero confirmed new physical Gaia–ZTF source associations, zero new variable stars and zero companion discoveries**.

## Reproducibility

- [Preregistered nine-source follow-up protocol](R2_NINE_IRSA_RECOVERY_PROTOCOL.md)
- [Previous original 15/24 source-access results](R2_REAL_IRSA_22_FAILURE_DIAGNOSIS_RESULTS.md)
- [Official IRSA ZTF lightcurve API](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html)
