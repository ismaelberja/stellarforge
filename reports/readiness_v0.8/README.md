# StellarForge v0.8 — Taurus observational readiness

**24 real catalogue sources planned, 0 validated ZTF source associations.**

The positions and Gaia DR3 identifiers are genuine catalogue entries from a pinned third-party copy of Luhman (2023); the original publisher bytes are not cross-checked.
These are not disk-class labels and there are no new detections.

## The two pre-registered pilot sources

| Source | Gaia DR3 | Query state | Identity state |
|---|---|---|---|
| FT Tau | `149623711269425408` | Not executed | Unverified |
| CIDA 11 | `3419110734340795648` | Not executed | Unverified |

## Next evidence thresholds

1. Retrieve publisher original Taurus table and cross-check members/identifiers.
2. Download raw g/r curves for the two pilot targets using the official API; keep responses and SHA256.
3. Run QC and time-convention checks on all OIDs, not on a guessed single match.
4. Propagate Gaia position to actual observation epochs; inspect PSF/crowding and neighbouring sources.
5. Perform matched-field controls, cadence-driven injections, and report negative results.
6. Only then consider physical interpretation or candidate review.

**Status:** study setup, not an astronomical discovery.