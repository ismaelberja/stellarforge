# SYNTHETIC benchmark only — NO real astronomical data

Generated with `python scripts/run_synthetic_benchmark.py --trials 24` and fixed seeds.

- `SYNTHETIC_benchmark.json`: simulated injected-sinusoid recovery (period 5.271 days); 24 trials in each of 3 noise/cadence regimes.
- `SYNTHETIC_irregular_lightcurve.png`: simulated observation-time plot, explicitly watermarked synthetic.
- `SYNTHETIC_phase_folded.png`: simulated phase-folded light curve, explicitly watermarked synthetic.
- `SYNTHETIC_features.json`: exploratory output of the v0.3 *synthetic* normalized photometry fixture; all astrophysical classifications remain unassigned.

These tests do not measure the sensitivity of the method on ZTF, Gaia or astrophysical processes. They are software-method validations only.