# R3 — preregistration of **three ORIGINAL TIMEOUTS ONLY**, original unchanged six-source experiment

**14 November 2026 · Frozen before any second (recovery) DR24 request.** The [initial real six original-ZTF ObjectID pilot](../../reports/taurus_variability_r3/R3_SIX_ORIGINAL_DR24_FIRST_REQUESTS_NO_RAW.json) was run exactly once for each of the six frozen R2 survey ObjectIDs in [Actions run 43593335135](https://github.com/ismaelberja/stellarforge/actions/runs/43593335135), with a **40 s per-request limit** and two workers. It returned exact original CSV (HTTP 200) for three FT Tau working-label OIDs, but returned **`TimeoutError`** for exactly three fixed original OIDs.

This new *technical archive recovery experiment* is restricted to **only** those three originally preregistered source IDs that failed to return a response, **not selected by variability, QC quality or source positions**:

| R2 working label | Exact original ObjectID | Original frozen band | Initial reason for retry |
|---|---|---|---|
| FT Tau | `609208400001969` | r | Original timeout |
| CIDA 11 | `610106300008010` | g | Original timeout |
| CIDA 11 | `610206300011997` | r | Original timeout |

## Recovery constraints, before querying

1. **Exactly one additional original URL request per above OID**, serial order shown, using identical `FORMAT=csv&COLLECTION=ztf_dr24` in the original IRSA API, no sky cone, ObjectID replacement or release switch.
2. Allow **85 seconds per original request** sequentially to diagnose pure provider latency. This differs only in access timeout/concurrency from the first fixed investigation; it **does NOT change original R1 scientific quality gates or retrospective classifications**. No retries beyond this second request in this preregistration.
3. Apply original **`catflags & 32768` filter, 30 locally QC-accepted epochs, 90-day span**, distinct OID/filters/time systems, no clipping or per-epoch data retention, and original 365-day bins anchored to first good source-specific observation.
4. Keep original first-run results **untouched and separately citable**. If any recovery succeeds, create a clearly labelled **reconciled six-original-OID access summary** showing first-run source for the three successes and second-run source for the recovered failures. State exact run ID per row. Original official DR24 exact raw response SHA and byte count must be stored; no original raw CSV in Git.
5. If 85-second retries still fail or yield invalid CSV, classify **provider unavailable/technical uncertainty**, not astrophysical non-detection, insufficient-variability or a QC failure. Do not promote a source as physically authenticated. **R2 independent Gaia-to-ZTF source-identity remains NO-GO**, even if all six survey OIDs pass technical 30/90 coverage.
6. The newer observations are additional **original-response retrievals** of the same ObjectIDs, not new stars or a new population. Do not make new physical star, variability, companion, lightcurve merging, or cross-field photometric calibration claims.

The three initial successes were already preserved in `reports/taurus_variability_r3/R3_SIX_ORIGINAL_DR24_FIRST_REQUESTS_NO_RAW.json` before creating this preregistration. This protects against selective replacement of scientific measurements and retrospective threshold modifications.
