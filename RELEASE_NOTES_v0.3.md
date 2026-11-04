# StellarForge v0.3 — scientific software engineering checkpoint

**Release date:** 2026-11-03. **Internal development artifact:** this package is **not** a publicly validated research result or a GitHub publication.

## Changes since v0.2

- Added `src/stellarforge/ztf_photometry.py`, a raw-to-audited ZTF photometry processor for official IRSA-style CSV and fixed-width IPAC tables.
- Introduced 31 additional engineering tests covering the input contract, numerical/pathological values, IPAC field widths, quality masks, provenance, source ambiguity and temporal conventions (48 → **79 passing tests**).
- New `stellarforge inspect-ztf` CLI route for audit JSON + normalized accepted photometry CSV.
- Explicit separation of unique ZTF OID, passband and time-scale; preservation of long identifiers.
- Bitwise flag masking and explicit invalid-epoch rejection reasons; no suppression of potentially astrophysical dips/bursts via sigma-clipping.
- Implemented provisional geometric checks and ambiguous multiple-OID flags; no claim of a final celestial match.
- Added a clearly marked **SYNTHETIC-only** example with representative bad flags and one artificial brightening/dimming event.
- Expanded scientific data-access and quality-control documentation. No original Luhman Table 2 or real ZTF time series have been downloaded.

## Automated checks

Run from project root with Python and pytest:

```bash
python -m pip install -e '.[test]'
python -m pytest -q
```

The tests were run successfully in this development environment. No network-dependent checks were executed.

## Gate for v0.4 (NOT yet achieved)

1. Obtain the **original machine-readable** Luhman (2023) Table 2 and verify membership counts and Gaia identifiers.
2. Independently verify disk classes and choose the pilot before opening variability data.
3. Acquire authentic archived ZTF observations, inspect raw response formats, compare sky positions with rigorous epoch propagation, and quantify selection bias.
4. Archive queries, timestamps, source URLs, releases and SHA256 hashes; report target-level failures and blending.

Only after those gates can scientific light-curve analysis and morphology inference begin.