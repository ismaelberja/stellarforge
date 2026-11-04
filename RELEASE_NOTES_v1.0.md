# StellarForge v1.0 — first operational research pipeline (private)

- Existing v0.9 source, tests, science notes and reproducible catalogue seed retained.
- Added code supporting a **manual-only, network-enabled ZTF intake workflow**, intended to retrieve the two official IRSA light-curve responses from a private GitHub runner. No raw observations are committed to Git.
- New v1.0 triage report records exact network and evidence states; never promotes a raw HTTP response into an independently confirmed Gaia/ZTF association.
- Added the `chromaticity` g−r near-time one-to-one pairing module, with strict explicit OID and time-scale guards, propagated uncertainties and mandatory source-review gates.
- Added new automated tests for empty, ambiguous, noisy and mixed-clock scenarios.
- Still no independent original-publisher byte comparison, authenticated ZTF counterpart or real Taurus physical variability claim.

**Important:** a `1.0` engineering milestone is not the final scientific project or a publication-ready result.