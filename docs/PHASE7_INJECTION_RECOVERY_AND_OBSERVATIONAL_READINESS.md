# Phase 7 — Injection/recovery, selection effects and a real-catalog ZTF pilot

**Research-software status:** validated engineering milestone, **not a ZTF observational result**. Version: v0.7, 2026-11-04.

## Motivation and scientific question

The existence of a photometric trigger is not evidence that a variability search is complete. Cadence gaps, episodic timescales, varying measurement uncertainties, seasonal windows and field-level calibration errors define the survey selection function. Before training a classifier or counting *dippers*/*bursters*, quantify which injected episodes the algorithm can recover and which null/artifact cases it wrongly advances for review.

**This iteration evaluates a synthetic surrogate only.** There is no ZTF light-curve data in this package. Real Taurus positions and Gaia proper motions from the literature are included separately for query preparation. Never describe the synthetic detection fractions below as astronomical completeness, contamination or discovery.

## Experiment: prespecified deterministic grid

- **384 artificial source-event trials** (32 combinations x 12 random realizations): amplitudes **0.12, 0.22, 0.40 and 0.65 mag**; durations **2, 5, 10 and 20 days**; Gaussian per-observation noise scales **0.025 and 0.070 mag** (randomized heteroscedastic errors).
- **144 negative-control trials:** 72 independent constant-source trials and 72 coherent field-calibration perturbations, divided across both noise scales.
- **528 total trials**, deterministic seed `20261104`. The source and field-control cadences contain **three 140-day seasons** separated by annual gaps. Each band has independent observations; within a band, reference stars share their target's timestamps by construction.
- Event shape: simultaneous achromatic **box-shaped magnitude excursion** in both bands (or identical shift in nearby field controls for instrumental artifacts).
- Original v0.6 pipeline: per-band event trigger, independently sampled passband overlap, four separately identified field controls per band, conservative review gate. A simulated astrometric association is treated as vetted **only by construction** to isolate the screening algorithm; **this is not a real source association**.
- Recovery requires **correct sign**, overlap with the injected time interval, and passage to the `multi_band_candidate_requires_physical_review` queue. Triggers elsewhere are not counted as successful recovery.
- Two denominators are preserved: *all attempted injections* and *injections with at least two observations at half-depth in each band*. Missing the observational opportunity is not called a failure of the detector conditional on sampling.
- Fractions receive **Wilson 95% binomial intervals**; these quantify finite Monte Carlo counts but ignore correlated realizations, assumptions about the source population and uncertainties in the instrumental error model.

### Selected synthetic-only outcomes

| Noise (mag) | Injected excursion | Duration | Review-queue recovery (all attempted injections) |
|---|---|---:|---:|
| 0.025 | 0.12 mag | 10 days | 0/12, Wilson 95% [0.000, 0.243] |
| 0.025 | 0.22 mag | 10 days | 10/12, Wilson 95% [0.552, 0.953] |
| 0.025 | 0.40 mag | 20 days | 12/12, Wilson 95% [0.758, 1.000] |
| 0.070 | 0.22 mag | 10 days | 0/12, Wilson 95% [0.000, 0.243] |
| 0.070 | 0.40 mag | 20 days | 3/12, Wilson 95% [0.089, 0.532] |
| 0.070 | 0.65 mag | 20 days | 12/12, Wilson 95% [0.758, 1.000] |

**Interpretation:** the v0.5 detector's hard lower amplitude gate of **0.18 mag** makes a clean 0.12-mag injected box episode systematically unrecoverable, regardless of observational coverage. This is an explicitly demonstrated method limit, not evidence that Taurus stars lack such events. Short episodes are missed when both bands have insufficient sampled epochs; faint/noisy events also fail the heuristic significance threshold. With 12 trials per grid cell, apparent perfection (12/12) is not proof of perfect sensitivity.

### Negative controls — intentionally challenging cases

- Constant artificial stars: **0/72** trials produced any raw event trigger; **0/72** were advanced for physical review. This is an idealized white/heteroscedastic-noise null model, not a measured false-positive rate.
- Coherent field-calibration anomalies: **71/72** produced an event trigger and **71/72** were vetoed by reference-star evidence. One failed to generate a trigger; **0/72** reached physical review. Again, this only tests one defined artifact model.
- The upper Wilson 95% limit on zero observed inappropriate promotions in 72 synthetic trials is ~5%; it must not be transported to real ZTF photometric artifacts.

![Synthetic detection-efficiency grid, lower noise](../reports/validation_v0.7/SYNTHETIC_V07_RECOVERY_NOISE_0.025.png)

![Synthetic detection-efficiency grid, higher noise](../reports/validation_v0.7/SYNTHETIC_V07_RECOVERY_NOISE_0.070.png)

![Synthetic artifact and null challenge](../reports/validation_v0.7/SYNTHETIC_V07_ARTIFACT_AND_NULL.png)

The full machine-readable grid is saved to `reports/validation_v0.7/SYNTHETIC_V07_SELECTION_FUNCTION.json` and the tabular summary to `SYNTHETIC_V07_RECOVERY_GRID.csv`.

## First real-catalog two-star pilot (not yet observed)

Pre-registered coordinate seeds chosen **before inspecting any ZTF light curve**:

| Member | Gaia DR3 source ID | Catalog position (ICRS deg) | Source subgroup | Gaia G mag |
|---|---|---|---|---:|
| **FT Tau** | `149623711269425408` | RA 65.913324, Dec 24.937195 | L1524/L1529/B215 | 13.604 |
| **CIDA 11** | `3419110734340795648` | RA 76.597253, Dec 24.538792 | L1544 | 13.470 |

The positions, identifiers and magnitudes above originate from the **pinned third-party copy of Luhman (2023) adopted-member Table 2**, preserved in the existing 24-source technical seed, *not* a confirmed IRSA response. `scripts/build_v07_two_star_pilot.py` creates `reports/observational_readiness_v0.7/TWO_STAR_PILOT_NOT_EXECUTED.json` with strict request URLs, proper motions, catalog source hashes and prerequisites. Gaia positions are propagated to the **illustrative** epoch J2021.0 for engineering checks; there are no measured ZTF exposure dates yet. A 2-arcsecond cone query only produces **potential** ZTF OIDs. It must not be used as a final crossmatch.

The proposed targets represent **two distinct kinematic groups** and convenient brightnesses. Their disk classes have **not** been independently checked, so they are **not** a Class II/III scientific comparison sample. No claim of ZTF coverage or variability has been made.

### Honest status of the observational bottleneck

In this container environment, outbound HTTPS to `irsa.ipac.caltech.edu` fails DNS/network access. We attempted to retrieve a direct IRSA query through the research browser as well, but it did not return a usable table. **ZTF observation rows acquired: 0.** This is a limitation of current access, not evidence that ZTF did not observe these stars.

The proper IRSA interface is described at <https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html>. Official archive documentation explains **separate `oid` light curves**, filters, photometric uncertainties and the `catflags` bit mask. For more than roughly 1,000 targets the archive recommends its HATS workflow; our two-target initial pilot fits the conventional light-curve API.

### Real-data exit criteria before physical claims

1. Retrieve raw light curves and stable provenance (request URL, release, timestamp, original file bytes and SHA256). Audit response formats and instrument flags.
2. Keep **all** OIDs and passbands separate; propagate Gaia proper motions to actual observation epochs, compare centroids and inspect image cutouts for neighbors/crowding.
3. Identify independent, same-field reference stars on genuinely matched exposures. Avoid fabricating controls from other times or applying absolute color corrections without color estimates.
4. Repeat the injection/recovery experiment on **actual observed timestamp/error arrays**, with documented nondetections, false-alarm estimates, cadence, disk class and magnitude strata.
5. Freeze source-level training/test partitions before optimizing heuristics or training future ML models. Compare to published YSO time-domain literature; physical attribution requires corroboration.

## How to reproduce v0.7 locally

```bash
python -m pip install -e '.[analysis,test]'
python -m pytest -q
python scripts/build_v07_two_star_pilot.py
python scripts/run_v07_selection_function.py --trials-per-cell 12 --seed 20261104
```

**Release status:** internal research deliverable only; not uploaded to the owner's public GitHub. This version cannot legitimately report discovered variable stars, a trained predictive ML model or observational significance yet.