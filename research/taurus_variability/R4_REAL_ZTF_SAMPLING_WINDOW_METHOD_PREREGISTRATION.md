# Taurus R4 — preregistration of original-ZTF sampling completeness and 1-day window non-identifiability

**14 November 2026; frozen before the R4 analysis, figures, or calculated synthetic window scores are produced.**

## R4 study question

Given the **three authentic, source-specific, ZTF DR24 original ObjectID photometric series** that yielded CSV in the preregistered R3 first experiment, what can and **cannot** be inferred about instrumental time sampling from the **only publicly committed derived statistics**: per-ObjectID accepted epoch count, total time span, `catflags & 32768` quality rejections, and **365-day-bin counts anchored to each ObjectID's *own first accepted observation***? Are the original R1 technical 30-good-visit/90-day gates sufficient to rule out serious cadence blind spots? (They are not necessarily sufficient.)

R2 established **0/24 independently verified physical Gaia–ZTF source associations**, so this is a technical archive/sampling-method feasibility audit, **not** stellar time-series scientific R4, a periodogram of real FT Tau, a stellar variability detection, or a new companion.

## Frozen sources / immutable receipt

Read only `reports/taurus_variability_r3/R3_SIX_ORIGINAL_DR24_FIRST_REQUESTS_NO_RAW.json` and `reports/taurus_variability_r3/R3_THREE_ORIGINAL_DR24_TIMEOUT_RETRY_NO_RAW.json`; their exact original-response hashes, source/ObjectID/band labels, 684 original rows, 591 retained and 93 bit-15 flags are authenticated by `python -m scripts.audit_taurus_r3_six_original_source_receipts`. All three unavailable survey ObjectIDs were actually retried once in a separate prospectively registered original-archive request; both original attempts timed out, and they must stay **unavailable**, never be counted as `0 epochs`.

The three original **successful** technical survey ObjectIDs, which must remain separate: `1605115300003377` (g), `1605215300005161` (r), and `609108400001155` (g). The three failures are `609208400001969` (r), `610106300008010` (g), `610206300011997` (r). They are **not six independent astrophysical stars**; their R2 Gaia technical working labels are not independently authenticated physical associations.

## Fixed calculations (no parameter tuning)

1. For each genuine returned ObjectID, compute exact **total accepted visits**, **QC retention fraction** = accepted / original received, `365*accepted/span_days` for descriptive accepted-visits-per-365d, the total number of **nonempty bins / number of genuine 365-day bins** and the **longest consecutive run of zero-count bins**. For each nonempty bin, preserve its authentic original count. Do not invent exact visit dates, seasonal calendars, sky positions or photometric magnitudes from these coarse bins. Bins are **anchored separately to each source**, not to common calendar-year dates.
2. Display a self-contained **original-derived** quantitative SVG with **exact source-specific bin counts** for all three accepted ZTF ObjectIDs, and mark the remaining three original requests as **timeout / no response**. Any bins **beyond a source's recorded total span** are `NOT IN OBSERVED SPAN`, **not zero accepted visits**. Each genuine empty bin **inside a recorded span** is shown as `0`.
3. Demonstrate the **under-identification of an exact 1-day spectral-window statistic** from yearly bin totals using two deterministic purely **SYNTHETIC schedules**, both with precisely the same per-bin counts and the exact original **overall span**:
    - `SYNTHETIC_DAILY_GRID`: first sample at time 0, last at the original measured span; all other hypothetical observations assigned to **distinct integer-day offsets** within each original nonempty relative 365-day bin, spaced as widely as possible.
    - `SYNTHETIC_SUBDAY_DIVERSE`: first sample at time 0, last at original span; all other hypothetical observations drawn reproducibly from **continuous fractional-day offsets** within their same original bin using Python `random.Random` seeded from SHA-256(original survey ObjectID + `/r4/subday/v1`). The exact seed algorithm/version is fixed now. This is a **demonstration**, not a statistically representative telescope sampling model.
    - For each synthetic construction compute `|N^{-1} Σ exp(2π i t / 1 day)|²` at **exactly 1.000000 day**, and round to **six decimal places** for reporting. This is a mathematical spectral-window example on **invented schedules**, **not** the true spectral window of ZTF, evidence of a real 1-day stellar period, a false-alarm probability, a frequency search, or rigorous upper/lower bounds.
4. Validate the synthetic schedules preserve **each exact authentic bin count**, the **genuine first/last time span**, fixed order of relative bins and the original source count. Clearly label all simulated timings and window powers `SYNTHETIC`. Do **not** include invented timestamps in the public source report, and do not include source photometry, dates, original raw CSV, original FITS, or private ALMA/TFM data.
5. Fail closed if immutable R3 receipts or physical R2 no-go are changed, one source is silently promoted to a physical star, timeouts are converted to zero detections, a synthetic schedule is reported as an actual measured periodogram or a different 1-day test frequency is substituted. Add offline direct CLI audit and regression tests.

## Scientific acceptance

**Completable R4 deliverable:** observationally grounded 365-day-bin coverage and source quality limitations for all six originally frozen ObjectIDs (three measured coverage series and three explicitly missing original responses), a reproducible proof-by-construction that coarse bins **do not uniquely identify** even the 1-day sampling-window statistic, an accessible data-provenance figure, unit/adversarial tests, and a report that keeps **R4 true astrophysical variability BLOCKED**.

A scientifically accepted positive R4 FT Tau/CIDA 11 period/variability claim would require the independent Gaia–ZTF physical counterpart and accurate **original individual visit timestamps and photometric uncertainties**. None is available publicly in these frozen R3 derived-only ledgers, and no new original archive request is justified by this pre-registered R4 experiment.

**This R4 method result can be used in R5 to independently audit selection effects/uncertainties and in R6 as an explicitly inconclusive scientific feasibility finding, without making an astrophysical discovery claim.**
