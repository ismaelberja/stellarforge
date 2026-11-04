# StellarForge v0.5 — **SYNTHETIC ONLY** benchmark results

**Not observed stars. Not Taurus dipper or burster discoveries.** This table summarizes simulations of artificial photometric light curves and control artifacts.

| Synthetic scenario | Recoveries / trials | Spurious flags / trials |
|---|---:|---:|
| dense dips | 60/60 | not a control |
| dense bursts | 60/60 | not a control |
| sparse dips | 53/60 | not a control |
| low amplitude | 55/60 | not a control |
| high noise | 2/60 | not a control |
| white noise control | not an injection | 0/60 |
| calibration artifact | not an injection | 60/60 |

**Interpretation:** The synthetic high-noise case suffers a sharp drop in recovery. The deliberately coherent calibration artifact is flagged in every test, demonstrating that the present statistical screen alone **cannot** distinguish instrumental offsets from real stellar behaviour. The white-noise control is insufficient to establish a realistic survey false-positive rate.

## Methods and reproducibility

- Fixed random seed `20261104`; 60 trials per case, seven cases (420 trials).
- Each trial draws an irregular uniform sampling schedule in a 140-day span; only one true or artifact interval is injected.
- The event detector parameters are unchanged between scenarios (0.18 mag minimum excursion, 4-sigma proxy, minimum two observations within four days).
- The apparent quality for injected signals does not extrapolate to real ZTF curves with seasonal gaps, blending, calibration shifts, and heterogeneous cadence.
- All methods and explicit limitations are described in `docs/PHASE5_BATCH_AND_EVENTS.md`.

![Synthetic recovery by scenario](SYNTHETIC_recovery.png)

![Synthetic example of fading injection](SYNTHETIC_example_fading.png)