# StellarForge v0.5 — Restartable ZTF batch ingest + candidate event screening

**Status: Research and engineering milestone, not astrophysical results.**

## Added

1. `stellarforge.batch`: versioned 24-target batch query ledger; immutable SHA256 cache validation; status for every requested target; retry policy; bounded batch and rate delay; dry-run default.
2. `stellarforge.events`: uncertainty- and cadence-aware exploratory fading/brightening event candidate screening (one OID/band/time convention at a time); explicit sign of magnitude; candidate metadata, conservative trigger thresholds and no confirmed physical labels.
3. `scripts/run_synthetic_event_validation.py`: deterministic 420-trial injection/recovery plus white-noise and instrumental systematic controls, quantitative JSON/CSV/PNG reports.
4. `docs/PHASE5_BATCH_AND_EVENTS.md`, `docs/BATCH_RUNBOOK.md`: honest scientific limitations, instrument/source association gates, documented operational runbook and citations.
5. Additional unit tests for input safety, event detectability, noise sensitivity, cache conflicts, transient retries and safe dry-run semantics.

## Current hard limits

- No real ZTF light curves have been fetched by the v0.5 code in this environment; external archive network access failed.
- No confirmed dippers, bursters, periods or scientific false-positive rate.
- The 24 rows are real literature-derived **coordinate positions** from a pinned **third-party** mirror, not a disk-stratified final Taurus science sample.
- Precise epoch-propagated cross-matching, image verification and independent disk indicators are outstanding.
- Synthetic calibration artifacts trigger the event detector; automated results are not publication-grade classifications.

## Reproduce

```bash
python -m pip install -e '.[analysis,test]'
python -m pytest -q
stellarforge batch-ztf --output reports/generated/ztf_batch
python scripts/run_synthetic_event_validation.py
```

No GitHub publication has been performed for StellarForge.