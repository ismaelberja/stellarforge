# StellarForge v0.6 — Synthetic instrument-control challenge

**Do not cite these as astronomical detections.** No genuine ZTF photometry was used in this experiment.

The previous magnitude-excursion trigger can flag a real-looking fade when the entire field suffers a simultaneous zeropoint shift. This v0.6 challenge injects coherent artifacts into 4 field comparison stars to test whether independent controls can veto false candidates.

- **400 deterministic synthetic trials**, 50 per experimental condition.
- **50/50** strong both-band simulated fading episodes and **50/50** simulated brightenings were prioritized for *physical review* under artificial quiet-field conditions.
- **50/50** coherent calibration offsets were flagged as raw events, but **0/50** remained eligible for physical review after the field-control veto.
- **50/50** events with one affected control and **50/50** events with missing controls were held as inconclusive; they were not silently accepted.
- **0/50** plain Gaussian-noise controls triggered; **0/50** deliberately weak high-noise injections were recovered.
- A lone g-band episode is preserved as a single-band follow-up target, not a physical class.

These results **do not** establish expected sensitivity or false-alarm rates on real ZTF. The model of instrumental effects is intentionally simplified. Real survey cadences, crowding, source misidentification, irregular calibration and correlated astrophysical variability remain unevaluated.

See the detailed [CSV](SYNTHETIC_V06_STRESS_TEST.csv), [JSON](SYNTHETIC_V06_STRESS_TEST.json), [figure](SYNTHETIC_V06_VETTING_COMPARISON.png) and [scientific methods](../../docs/PHASE6_ASTROMETRY_AND_FALSIFICATION.md).