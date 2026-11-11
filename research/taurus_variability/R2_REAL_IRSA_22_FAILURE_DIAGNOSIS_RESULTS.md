# Taurus R2 — Genuine IRSA source-access diagnosis and recovery

**Original survey access verified 11 November 2026. R2 physical source identity still OPEN.**

Original live public IRSA diagnostic:
[GitHub Actions run 43037800319](https://github.com/ismaelberja/stellarforge/actions/runs/43037800319);
[derived-only original GitHub artifact 13864870251](https://github.com/ismaelberja/stellarforge/actions/runs/43037800319/artifacts/13864870251)
(expiry 11 December 2026);
[preserved full no-raw 24-source ledger](../../reports/taurus_variability_r2/IRSA_22_ORIGINAL_DERIVED_DIAGNOSTIC_LEDGER.json).
The latter is checked against the full artifact's JSON SHA-256
d9fba22670cabd014a8ce1cf3ad050f075c5133035b5fa6d9e208d9b9fef2f6f.
Original ZIP SHA-256:
ba4464e422d21836d6d8a1a8421edbcd98574ed381b0e7a6ead9720dcad21081.

## What the original archive actually returned

| Original R2 source-access outcome | Sources |
| --- | ---: |
| Frozen Taurus technical Gaia IDs | **24** |
| Prior successful positional ZTF fields (not requeried here) | **2** |
| Previously unavailable/unparseable ZTF fields retested | **22** |
| Recovered with populated, parseable original ZTF positional tables | **13** |
| Still unresolved after this bounded diagnostic | **9** |
| Total with *some* parsed ZTF positional table across separate runs | **15/24** |
| Confirmed physical Gaia–ZTF matches | **0** |
| Scientifically confirmed variable stars or companions | **0** |

The 13 new parseable positional response tables contain a total of
**14,803 original table rows** across the 13 request positions.
These are raw *row counts* from returned IRSA tables, potentially
including multiple ZTF ObjectIDs/filters per sky position, **not**
14,803 independent stellar detections or quality-accepted measurements
of the named Gaia sources. No photometric variability statistics are
computed from these rows in R2.

### Per-request outcome counts — NOT per-star classifications

The real job executed **31** bounded HTTP attempts for the **22**
previously unresolved positions. These outcomes sum to 31:

| Response category | HTTP attempts |
| --- | ---: |
| Valid CSV with at least one original ZTF positional row | 13 |
| Network timeouts | 8 |
| HTTP 400 client errors on alternate count-parameter query | 9 |
| Valid CSV with zero rows under query's restriction | 1 |

**Key diagnosis:** all 13 successful newly parsed responses came
from **repeating the original NOBS_MIN=5 query shape**. Recovery
was **not** caused by a new parameter spelling. Eight targets
timed out on that original request; one returned a valid
zero-row table. The secondary NUM_OBS=1 experiment returned HTTP
400 in all nine of those cases, so it cannot be recommended as
a working alternative in this run. This does not identify why
the API rejected it: spelling, parameter semantics, server
state and validation details would require further controlled tests.
The API's public documentation lists NOBS_MIN in examples and
NUM_OBS in the parameter descriptions, so API support must be
tested empirically, not assumed.

The fact that 13 original-format requests returned data this time
demonstrates that the earlier blanket
"IRSA_QUERY_OR_PARSE_UNAVAILABLE" category was *not a stable
measure of survey coverage*. None of the original 22 failures
may be interpreted as stellar nonvariability.

### Nine remaining unresolved technical seeds (Gaia DR3 ID)

- 162259951730099968 — timeout on original request; alternate HTTP 400
- 156732977357829888 — timeout; alternate HTTP 400
- 156577881796362496 — timeout; alternate HTTP 400
- 149623711269425408 — timeout; alternate HTTP 400
- 146764465639042176 — timeout; alternate HTTP 400
- 3418414193726125184 — timeout; alternate HTTP 400
- 3314244366165299584 — timeout; alternate HTTP 400
- 3314299238667410176 — timeout; alternate HTTP 400
- 3406270362673330944 — valid **zero-row** NOBS_MIN=5 table; alternate HTTP 400

For that final source the valid zero-row response means no rows
**under that query, on that date and threshold**, not an absent
star, an empty sky or a negative variability finding. For the
eight timeouts, no original response table was interpreted.

### Additional source-identification limitations

- The 24 Gaia IDs were preselected in the nonrepresentative R1
  technical cohort, not as an unbiased Taurus source sample.
- Gaia's exact ID and provisional star-position agreement do
  not independently prove that an IRSA ZTF ObjectID belongs
  to the named physical star. **All 24 Gaia–ZTF identities
  remain scientifically unconfirmed.**
- ZTF same-position positional queries can return several OIDs
  in the same filter; field/exposure processing and blending
  must be checked before combining curves.
- No new original ZTF FITS image/mask/PSFcat astrometric or
  independent crowding investigation was performed by this
  diagnosis.
- No original provider CSVs, original source pixels, derived
  variability labels or authenticated stellar periodograms
  were committed as scientific findings.
- The 13 recovered tables passed a **table syntax/access
  check**, not the full R3 per-epoch quality filter.

## Research decision

**R2 original-data access has materially improved; R2 physical
source identification is NOT finished.** Next first diagnose
the persistent nine with a source-by-source bounded,
rate-respecting IRSA NOBS_MIN=1 / alternative access study,
never treating nonresponses as negative observations.
Then use original ZTF image/mask and independent astrometric
comparisons to identify true Gaia/IRSA counterparts before
photometric variability interpretation.

The v2.0 software-engineering portfolio remains complete.
No new astronomical discovery or journal-ready variability
result is claimed from this R2 original-data recovery.

## Sources and reproduction

- [Preregistered diagnostic method](R2_IRSA_HTTP_DIAGNOSTIC_METHOD.md)
- [Frozen original 22-source input and original R1 seed SHA](R2_IRSA_DIAGNOSTIC_INPUT_NO_RAW.json)
- [Official NASA/IPAC IRSA ZTF lightcurve API documentation](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html)
- [Original failed prior 24-field access audit](R2_REAL_GAIA_NEIGHBOURS_ZTF_POSITIONS.md)
