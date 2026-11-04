# Verification and statistical validity plan

## Data and cross-match gates

- Original membership table citation, row count, duplicated IDs and missing Gaia IDs reported.
- Right ascension wrap-around, coordinate frame and Gaia reference epoch properly handled.
- Cross-match includes proper-motion propagation and uncertainty; ambiguous alternatives cannot be silently dropped.
- Every survey's band/filter and original time convention are preserved.
- ZTF `oid`, field ID and survey quality flags must be considered; no accidental mixing of objects.
- Gaia DR3 epoch photometry not inferred from plain `gaia_source` existence.

## Time-series diagnostics

- Baseline model considers heteroscedastic photometric errors and potential correlated noise.
- Report observation count, span, season coverage, time gaps and outlier removal.
- Test null signals, variable signals and irregular cadence, not just ideal sine waves.
- Report window-function peaks, aliases, harmonics and false-alarm probability limits.
- For strong morphological claims, inspect differential behavior in simultaneous or near-simultaneous filters.
- Compare metrics to literature on independently identified objects when available.

## Machine learning validity

- Unit of split = **astrophysical source**, not point in a light curve; ensure duplicate survey views of the same star never straddle train/test.
- Avoid target leakage from preexisting Gaia variable-class labels, fields produced by the same classifier, or post-hoc literature labels that overlap evaluation.
- Maintain baseline classifiers and simple statistical scores. If no trustworthy labels, prefer unsupervised ranking with expert validation.
- Quantify top-K review precision, candidate recovery rate, false positives, stability by magnitude, cadence and stellar type; bootstrap uncertainty by source.
- Include *no selection*, no detection and inconclusive cases in denominator accounting.
- Sensitivity analysis must distinguish missing-data effects and survey footprint from astrophysical changes.

## Software testing completed in Phase 1

- 24 deterministic tests validate ICRS bounds, angular separations, RA wraparound, approximate PM unit consistency, query parameters, Gaia query metadata, URL provenance writing and download error rejection.
- Remote scientific APIs have not been exercised against the Taurus member catalogue in these tests. They use synthetic/mocked fixtures where relevant.
- No real stellar light curve has been accepted or classified at this phase.

## Reproducibility acceptance gate

A third party must be able to resolve (a) the target's literature identity, (b) input archive query, (c) raw SHA-256, (d) immutable processing config, (e) feature definition and error model, (f) model/version and held-out evaluation, (g) reported output or explicit failure.