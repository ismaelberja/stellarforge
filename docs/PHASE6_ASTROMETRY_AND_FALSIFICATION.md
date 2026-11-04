# Phase 6 — Astrometric provenance, field controls and falsification

**Status:** engineering milestone, not an observational result. **Date:** 2026-11-04.

## 1. Scientific purpose

Previous iterations could identify magnitude excursions, but a coherent calibration shift in the ZTF field was indistinguishable from a possible occultation/accretion event. v0.6 introduces a *review gate*: an event must have sufficient per-band evidence, not be shared by vetted nearby control stars, and have an independently reviewed astrometric source association. The output remains a candidate requiring physical review, **never a confirmed dipper or burster**.

The project is relevant to time-series anomaly detection, data-engineering integrity, false-positive management, scientific risk management and reproducible research software. It is not a machine-learning achievement yet.

## 2. Data and provenance: genuine catalogue vs artificial photometry

- Literature population: Luhman (2023), AJ 165, 37, DOI: [10.3847/1538-3881/ac9da3](https://doi.org/10.3847/1538-3881/ac9da3): 532 adopted Taurus members, 13 kinematic groups; the pinned third-party Table 2 copy carries 467 unique Gaia IDs.
- Mirror: [`themariavincent/get_targets` at `7b6a5c8...`](https://github.com/themariavincent/get_targets/blob/7b6a5c83eca81fc66e50cb4889ee35cb28861367/taurus_sources.txt); Git blob SHA-1 `fe0d5a43dbd2ca8b867901686ab223a847c649e5`. **The exact publisher-original bytes have not been compared.**
- Real data product: the **24-source technical coordinate seed**, which is not the final disk-stratified Class II/III science sample. All these targets have a Gaia position reference and listed proper motions. The reference epoch of Gaia positions is nominally J2016.0.
- **No genuine ZTF photometry** has been downloaded or measured in this environment. Example light curves and all 400 new trials are **synthetic**. We cannot infer source membership, periodicity, or real-dataset completeness from the experiments.

## 3. Preliminary astrometry — an actual catalogue-derived computation

`src/stellarforge/association.py` applies a first-order angular motion in the tangent basis. For a sky-unit vector **u**, local RA-direction **e_α**, local Dec-direction **e_δ** and Gaia convention µ_α* = µ_α cos δ, compute

```
u' = normalize( u + Δt · [µ_α* · e_α + µ_δ · e_δ] )
```

where both motion components are converted from mas/year to rad/year. Unlike simply adding coordinates, this method handles RA=0 wrap and high declinations. It is still approximate: **no parallax, radial-velocity perspective effect, covariance, or image-level astrometric solution**; exact observation epoch may not be known until the raw ZTF response is inspected.

For the 24 real Taurus catalogue targets, a deliberately illustrative change **J2016.0 → J2021.0** gives:

| Metric | Catalogue-derived value |
|---|---:|
| Targets with Gaia-referenced catalog position | 24 |
| Median angular shift | **0.112673 arcsec** |
| Minimum angular shift | 0.069258 arcsec |
| Maximum angular shift | **0.145100 arcsec** |
| Targets moving over 0.1 arcsec in five years | **17/24** |
| Actual ZTF counterparts confirmed | **0** |

These shifts have different directions; they are **not photometric changes**. The epoch 2021.0 is **an engineering example** rather than the timestamp of a measured ZTF source. The `reports/v0.6_catalog_astrometry/` directory includes the full 24-row CSV, SHA256 audit and a plot of the actual published proper-motion components. Future matching must propagate to **actual** observation epochs and account for formal astrometric error budgets.

The `screen_ztf_positional_candidates` function retains all matched OIDs and their individual bands. Multiple same-band OIDs are reported as ambiguous; different-band OIDs are **never automatically declared identical**. A unique positional candidate is still **not confirmed**.

## 4. Field-control falsification and multi-band screening

`src/stellarforge/vetting.py` treats the baseline v0.5 event detector as a *trigger generator*, then evaluates:

1. **Per-filter identities and clocks:** do not merge ZTF `oid` or time scales (MJD/HJD/HMJD); reject duplicated OID assignments across bands and non-increasing times.
2. **Independent band evidence:** separate `g` and `r` detections of the same event direction should overlap in observed time within a declared one-day tolerance. This alone is insufficient to prove astrophysical origin.
3. **Field controls:** require at least three independently vetted, same-field/same-calibration reference stars **for each relevant band**. For every control compare median magnitude inside the candidate time window with the control's median outside. A same-sign shift of at least 0.12 mag counts as a coherence warning. Two or more coherent controls comprising at least half of the usable controls trigger a veto. One affected control yields an inconclusive hold. Missing or unverifiable controls yield an inconclusive hold.
4. **Decision:** `veto_suspected_field_calibration_artifact`, `hold_controls_inconclusive`, `single_band_event_requires_followup`, `hold_astrometry_and_image_review` or `multi_band_candidate_requires_physical_review`. **No category means scientific confirmation**.

These thresholds are deliberately prototypical, not tuned on real data. Control stars may themselves vary, have non-identical exposures, or be blended. The magnitude shift test ignores subtle spatially dependent systematics and changes in uncertainty. It must eventually incorporate instrument metadata, difference-image inspection and a survey-calibrated empirical null distribution.

## 5. Stress test — synthetic, not survey performance

**400 deterministic simulations**, fixed random seed 20261104, 50 trials per scenario (`scripts/run_v06_systematics_validation.py`). The injected light curves have Gaussian noise and a 7-day 0.55-mag episode (or no event); control stars deliberately reproduce or omit a coherent 0.50-mag offset.

| Artificial condition | Raw event trigger | Passed to physical review | Instrument veto / hold |
|---|---:|---:|---|
| Both bands fade together (signal) | 50/50 | 50/50 | none |
| Both bands brighten together (signal) | 50/50 | 50/50 | none |
| Both bands + four field controls shift (calibration error) | 50/50 | **0/50** | 50/50 vetoed |
| One of four field controls shifts | 50/50 | **0/50** | 50/50 held |
| Only g-band contains event | 50/50 | 0/50 | 50/50 single-band follow-up |
| Plain white noise | 0/50 | 0/50 | none |
| No controls available | 50/50 | 0/50 | 50/50 held |
| Weak event with high Gaussian noise | 0/50 | 0/50 | missed in this test |

The synthetic results illustrate one narrow failure class. **They do not estimate real false-positive rates, recall, sensitivity or specificity of any Taurus sample**. The high-noise misses and unvetted-control holds are scientifically meaningful failure modes. Real outliers must be tested using genuine observation cadences, source crowding and field calibration statistics.

**Figure:** `reports/validation_v0.6/SYNTHETIC_V06_VETTING_COMPARISON.png`; complete machine-readable stress-test results in the matching CSV and JSON. The results remain explicitly labelled `SYNTHETIC_ONLY`.

## 6. The reproducible raw-ZTF adapter

Once a real ZTF API response has been obtained by an authorized network-enabled process:

```bash
python -m pip install -e '.[analysis,test]'
python scripts/review_ztf_raw_v06.py \
  --gaia-id 164800235906366976 \
  --ztf-file data/raw/164800235906366976_ztf.csv \
  --out reports/generated/164800235906366976_review.json
```

It reads and hashes the *supplied* raw table, performs existing CSV/IPAC quality checks and per-band/OID normalisation, estimates a nominal epoch from accepted **MJD** observations, computes a preliminary spherical position screen and emits a JSON **review manifest**. It refuses to declare an astrometric match confirmed even if only one candidate falls within a 2-arcsec cone. It records whether a matching IRSA URL+SHA sidecar exists; an arbitrary local file is not promoted to a verified observation.

To reproduce a synthetic-only unit test:

```bash
python -m pytest -q tests/test_association_pipeline.py
```

## 7. Research gates remaining

- Obtain exact publisher-origin Table 2 and verify bytes; freeze independent Class II/Class III classification, with a documented sample-selection function.
- Obtain real ZTF light curves through the official [IRSA ZTF lightcurve API](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html) and audit exposure timestamps, image cutouts, reference stars and flags.
- Use Astropy with epoch-specific astrometric covariance, parallax and proper motion, and inspect blended pairs.
- Use same-field reference stars on genuinely comparable exposures; test exposure-level calibrations and spatial systematics.
- Inject synthetic events into **real ZTF timestamps**; estimate false-positive/recovery rates with uncertainties by region, magnitude, cadence, crowding and event morphology.
- Compare carefully vetted candidates with the published variable-YSO literature. Physical interpretations require external checks.

**No GitHub/public publication has been performed in this phase.** The work remains a versioned local research deliverable.