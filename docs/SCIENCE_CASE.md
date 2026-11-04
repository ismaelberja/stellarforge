# Science case — protocol v0.1

## Main research question

For a membership sample fixed **independently of measured variability**, what combinations of survey-aware light-curve properties discriminate commonly encountered behaviors in young stars, and which objects remain unusual after accounting for sky coverage, cadence, uncertainties and contamination?

## Pilot population and target selection

- **Region**: Taurus molecular-cloud complex, not an arbitrary rectangular cone used as membership criterion.
- **Source catalogue**: 532 adopted Taurus members from Luhman (2023), *AJ* 165, 37 (DOI 10.3847/1538-3881/ac9da3).
- **Population caution**: not every adopted member has a Gaia DR3 source ID or astrometry; not every Gaia source has public DR3 epoch photometry; not every member has sufficient ZTF detections. Do **not** equate 532 to the eventual analysis set size.
- **Contaminants/controls**: nearby Gaia field stars matched as closely as practicable in magnitude, sky footprint and cadence; their status is *control*, not proof they are old/non-variable.
- **Extension only after pilot**: other young regions to evaluate external generalization; not allowed to choose them solely to optimize an ML metric.

## Hypotheses (to be revised with scientific collaborator)

**H1 — measurable variability modes.** A subset of usable Taurus light curves shows variability inconsistent with a constant brightness model when assessed with uncertainty-aware tests and red-noise/cadence controls.

**H2 — physically motivated photometric features.** Period, distribution asymmetry, color-magnitude slope and timescale-based features can distinguish *candidate* rotational/spotted, dipping/extinction or bursting/accretion behavior more effectively than amplitude alone. These are not unique physical diagnostics.

**H3 — anomaly detection with calibrated false alarms.** A source-level anomaly ranking, evaluated with injected signals and expert-checked reference cases, can recover intentionally unusual signal patterns without treating noise, blends or seasonal aliases as discoveries.

**H4 — multi-survey utility.** Conditional on data availability and comparable observation windows, adding independent Gaia information to ZTF-only features improves confidence or interpretability for a documented subset. Because Gaia/ZTF sampling and bands differ, the improvement must be tested rather than assumed.

## Minimum scientific analysis plan

1. Freeze the membership table, provenance, data fields and catalogue version. Preserve original source identifiers.
2. Join Gaia metadata by verified source ID where possible. Record presence and quality flags, not only successful joins.
3. Obtain ZTF light curves for a deliberately small member subset first; distinguish ZTF `oid` objects and filters. Inspect multiple matches, seasonal gaps and blending.
4. Standardize times explicitly. Preserve MJD/HJD/BJD and original reference conventions rather than assuming they are interchangeable.
5. Filter documented survey flags; record the fraction rejected, completeness, per-band magnitude errors and coverage duration.
6. Fit a robust constant-brightness baseline. Identify non-variable/insufficiently sampled cases rather than forcing all into categories.
7. Apply period search (Astropy Lomb–Scargle and, if justified, non-sinusoidal methods); assess window-function peaks and harmonics.
8. Compute amplitude, quantiles, skewness, asymmetry/dipper and burster indices, variability time scales and color behavior with proper band/window awareness.
9. Validate: known period comparisons, injected signals in actual cadences, null simulations, multiple-testing control and object-by-object diagnostic plots.
10. Only then compare interpretable anomaly models; assess source-level splits, instrument and season covariates, and expert-review burden.

## Claims we will *not* make from a classifier alone

- A new YSO, planet, accretion burst or occulting disk has been discovered.
- A Gaia–ZTF cross-match within a small fixed radius is unambiguously correct.
- A light-curve morphology uniquely identifies the physical mechanism.
- A high internal ML score guarantees transfer to another region/survey.
- The absence of photometric variability disproves stellar youth.

## Output evidence requirements

Each candidate report will show: verified source identity, survey/filters, N good measurements, temporal span, individual photometric uncertainties, original quality flags, cross-match alternatives, variability statistics, period/window diagnostics, model confidence, competing explanations and cited literature. Reports must provide access to the exact feature and data selection used.

## Relevant published work

- Luhman (2023), DOI 10.3847/1538-3881/ac9da3 — Taurus membership and kinematic group structure.
- Roquette et al. (2026), DOI 10.1051/0004-6361/202554522 — Gaia DR3 young-star variability analysis (must not copy its results as new findings).
- Gaia DR3 variable-YSO validation, A&A 674 A21 — strong selection effects, incomplete/contaminated labels.