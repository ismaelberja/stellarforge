# StellarForge v0.7 — Selection-function prototype and two-target ZTF pilot

**Internal research delivery:** 2026-11-04. Not published on GitHub. The project is not finished.

## Added

- `src/stellarforge/injection.py`: deterministic time-domain episode injection with explicit magnitude sign conventions, non-observation censoring and Wilson score intervals.
- `src/stellarforge/selection_function.py`: reproducible synthetic injection/recovery grid built on the existing v0.6 multi-band source/field-control review gate.
- `src/stellarforge/observational_plan.py`: verifiable **real-catalog positions** for FT Tau and CIDA 11, recorded separately from unexecuted IRSA requests.
- `scripts/run_v07_selection_function.py`: full grid outputs (JSON, CSV and 3 labeled figures).
- `scripts/build_v07_two_star_pilot.py`: two-source query manifest with original catalog provenance and scientific gates.
- `tests/test_v07_injection.py`, `tests/test_v07_observational_plan.py`: new scientific-engineering regression coverage.
- [Full phase-7 research analysis](docs/PHASE7_INJECTION_RECOVERY_AND_OBSERVATIONAL_READINESS.md).

## Validation

- **210 automated tests passed** (170 from v0.6 plus 40 additional v0.7 test cases).
- **528 total synthetic experiments**, comprising 384 injected-event and 144 null/artifact trials.
- Provenance and status labels distinguish **real Taurus catalog information** from **entirely synthetic observations**.
- The hard 0.18-mag trigger floor, observation-window censoring and reference-star veto are explicitly documented, with Wilson 95% intervals for small trial counts.

## Outstanding science blockers

- Direct IRSA ZTF raw photometry and image cutouts remain inaccessible in this environment: **0 genuinely observed ZTF rows downloaded**.
- Publisher-byte reconciliation of the pinned Luhman (2023) member-table mirror remains pending.
- No independent disk classifications or astrophysical morphology classifications have been assigned.
- The use of illustrative J2021.0 astrometry is an engineering demonstration, **not** an observed-epoch crossmatch.

## Recommended next scientific phase

Acquire two genuine IRSA light curves, inspect source identity, and adapt the injection/recovery code to vetted **real** cadences and error bars before introducing physical labels or training ML models.