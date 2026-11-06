# StellarForge v1.10 — Gaia-reference holdout validation (derived real ZTF images)

**6 November 2026 · Tested research-software milestone.**

## What changed

- Added a persistent, **small, SHA-provenance-backed derived ledger** of 13 Gaia-reference image-model offsets measured in four actual v1.8 ZTF science frames, preserving reproducibility when old workflow artifacts expire. **No raw ZTF pixels, light curves or Gaia TAP CSVs** are committed.
- Implemented leave-one-Gaia-reference-out (LOO) median-shift validation with separate **inclusive** and **strict** reference-image fit-quality selections.
- Recorded held-out radial disagreement median, maximum and RMS, with strict gating against reporting a target-minus-reference offset when references or the target's own image model are insufficient.
- Added adversarial provenance/quality/duplicate-source tests; **468 automated tests passed** with the real derived input.

## What the real audit found

Of four original ZTF science exposures, **three** support LOO with all fitted references; only **two** have at least three references passing the stricter Gaussian-model quality screen. FT Tau MJD 58491.184780 has LOO RMS ~**0.0758 arcsec** with three references; CIDA 11 MJD 58475.113750 has ~**0.0930 arcsec** with four. CIDA 11 MJD 58849.135984 has five inclusive image fits but just **two** strict fits, so its formerly reassuring inclusive LOO (~0.0512 arcsec) does **not** pass strict review.

The counts and methods are in [real v1.10 evidence](reports/holdout_v1.10/REAL_REFERENCE_HOLDOUT_EVIDENCE.md) and [holdout QA methodology](docs/PHASE110_REFERENCE_HOLDOUT_QA.md). Original observed-data source: [v1.8 real image measurements](https://github.com/ismaelberja/stellarforge/actions/runs/42077605987); v1.10 reproducible offline run: [GitHub Actions](https://github.com/ismaelberja/stellarforge/actions/runs/42214593233).

**Limits:** An internal reference LOO residual is not a calibrated ZTF instrument error; few stars, shared PSF/WCS biases and incomplete Gaia reference-star parallax/covariance remain. CIDA 11's very high Gaia RUWE makes source-model interpretation especially uncertain. No source IDs, isolated empirical PSFs, field astrometric WCS solutions, physical companions or variability events have been independently confirmed.
