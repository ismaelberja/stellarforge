# StellarForge v1.22 — Recover original IRSA archive and verify pilot control flow

**10 November 2026. Archive integrity plus synthetic full-pilot software QA.**

## Delivered

- Recovered privately, before expiry, the exact 181,170-byte historic
  2026-11-05 IRSA positional-query source GitHub Actions artifact.
- Verified ZIP SHA-256 matches GitHub Actions metadata:
  `d54246e00d4cf343b0b062b9eb92034e51c735067274a8109e9b2c2c2a2d5167`.
- Added exact pinned SHA, ZIP inventory, inner-manifest and per-CSV
  bytes/hash integrity check without storing the original data in Git.
- Added full offline synthetic integration of the existing manual v1.20
  CIDA 11 original-data pipeline in both successful simulated
  4-train/3-holdout and rejected-star 3+2 eligibility scenarios.
- Prepared a Windows local execution procedure using the privately
  recovered original ZIP after GitHub artifact expiration.
- Updated scientific/Spanish documentation, roadmap, tests and release metadata.

## Scientific status

Archive bytes match the original historical workflow artifact;
this does not authenticate a physical Gaia–ZTF association.
The new end-to-end numerical PSF profiles are MOCKED and SYNTHETIC.
There is still **no confirmed new real original image PSF holdout**
from the manual live v1.20 workflow. It is not yet known whether
the strict 3-training+2-validation star cohort succeeds on any
original CIDA 11 exposure. No companions, variability or
independent ZTF WCS/PSF error calibration is announced.

One final v2.0 engineering closeout phase is planned, conditionally
two if original-data workflow or packaging issues require correction.
