# StellarForge v1.2 — Authentic IRSA transport, UNVERIFIED astronomical identities

**Date:** 2026-11-05 UTC. **Status:** live observational data intake succeeded; Gaia–ZTF identity and physical interpretation remain unverified.

## Traceable provenance

- Official endpoint: [IRSA ZTF-LC-API](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html).
- Exact live acquisition: [private workflow run 41995960368](https://github.com/ismaelberja/stellarforge/actions/runs/41995960368).
- Unmodified artifact: [raw CSV and audit ZIP (private, 7-day retention)](https://github.com/ismaelberja/stellarforge/actions/runs/41995960368/artifacts/13400322367). Do **not** commit raw photometric data to Git.
- The earlier [run 41866054392](https://github.com/ismaelberja/stellarforge/actions/runs/41866054392) failed with two HTTPError exceptions. The successful run uses the **same scientific query parameters**, so the cause of the earlier failure is not established; v1.2 added diagnostics and conservative failure reporting.
- Source catalog coordinates are from the pinned **secondary** mirror of Luhman (2023) Table 2. Publisher-original verification is still pending.

## Raw intake summary

| Search center (Gaia DR3 ID) | Returned rows | Distinct OIDs | g rows | r rows | MJD coverage | Rows with nonzero catflags |
|---|---:|---:|---:|---:|---|---:|
| FT Tau (149623711269425408) | 1199 | 4 | 474 | 725 | 58321.487–60948.441 | 9 |
| CIDA 11 (3419110734340795648) | 1013 | 2 | 397 | 616 | 58206.160–60968.381 | 12 |
| **Total** | **2212** | **6** | **871** | **1341** | — | **21** |

All 2,212 returned rows passed the *limited transport format/QC* filter, which excludes \`catflags & 32768\`. The 21 nonzero \`catflags\` values were 256; their physical/instrumental meaning must be handled separately. This is **not** a guarantee of publishable photometry.

| Search | ZTF OID | Filter | Rows | Field |
|---|---|---|---:|---:|
| FT Tau | 1605115300003377 | zg | 70 | 1605 |
| FT Tau | 1605215300005161 | zr | 117 | 1605 |
| FT Tau | 609108400001155 | zg | 404 | 609 |
| FT Tau | 609208400001969 | zr | 608 | 609 |
| CIDA 11 | 610106300008010 | zg | 397 | 610 |
| CIDA 11 | 610206300011997 | zr | 616 | 610 |

**Integrity of raw responses (SHA-256):**

- FT Tau \`149623711269425408_IRSA_RAW.csv\` (309,004 bytes): \`869686595e54767ebde9967342b8af7088e2119f4890264df249d2cf37e7c262\`.
- CIDA 11 \`3419110734340795648_IRSA_RAW.csv\` (260,796 bytes): \`ae1e676b891c7759286f29023a733ef5e126bb26a4d7ddf1d2d2551cc69187ee\`.

The reported hashes have been recomputed from the downloaded artifact and match its \`PILOT_STATUS.json\`. The artifact ZIP itself is distinct from each raw CSV and carries its own digest in GitHub Actions.

## Interpretation boundaries

1. These are **real measurements returned from official position-cone queries**. They cannot yet be independently assigned to the named Gaia stars.
2. FT Tau returns two OIDs per filter in two ZTF fields. Do not merge field-specific OIDs blindly or interpret this as four distinct astrophysical objects.
3. CIDA 11 returns one OID per filter; this alone does not establish unambiguous astrophysical identity.
4. Independent image/blend review, per-epoch Gaia position checks, original catalog verification and field controls are still required.
5. No dipper/burster candidates, physical periods, disk classes or occurrence rates have been validated.

**Next gate:** process the raw CSV privately with source-identity review and epoch-aware astrometry, preserve OIDs separately and create provisional light-curve diagnostics with explicit unverified labels.