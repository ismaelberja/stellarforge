# R2 — Original IRSA ZTF source-access diagnosis (22 unresolved fields)

**Registered 11 November 2026, before this diagnostic's live-query results were examined.**

## Why

The [previous original Gaia/IRSA R2 run](R2_REAL_GAIA_NEIGHBOURS_ZTF_POSITIONS.md)
returned 24/24 Gaia DR3 neighbourhood cones but only 2/24
interpretable ZTF positional lightcurve responses. The other
**22 failures were not astrophysical nondetections**; the earlier
runner combined transport failures and invalid/oversized responses
into one unavailable status.

The original 24-object study denominator and the 22 previously
unresolved source IDs are frozen in
[R2_IRSA_DIAGNOSTIC_INPUT_NO_RAW.json](R2_IRSA_DIAGNOSTIC_INPUT_NO_RAW.json),
cross-referenced to original Actions run 43031689454, artifact
13861901170, archived JSON SHA-256 and R1 seed SHA-256.

## Preregistered diagnostic

Only the previously unresolved 22 source positions are queried;
the two previously parsable fields remain prior-run records in
the same full 24-row ledger. No target is selected using source
variability, periodograms or the new query outcomes.

**Query A:** exact prior 2-arcsec POS=CIRCLE centre with
FORMAT=csv and NOBS_MIN=5.

**Query B:** only if A does not provide a populated valid table,
and A did not hit a rate limit, HTTP 5xx or size cap:
the same 2-arcsec centre and FORMAT=csv, with NUM_OBS=1.

A valid zero-row response from A triggers B because a five-visit
requirement can exclude sparse observations. No zero-row table
or HTTP 404 can be interpreted as astrophysical nonvariability.

Both NOBS_MIN (in the examples) and NUM_OBS (in the parameter
reference) appear in the
[official IRSA API documentation](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html).
This experiment checks their actual behaviour in the selected
original Taurus fields. **It does not assume either spelling is wrong.**

One bounded 2 MB read and 12-second timeout per attempt; query
URL SHA-256 and provider status/type are recorded. No server
error text, original CSV rows, FITS pixels or entire photometric
source data are saved to Git or a public artifact.

Possible results: HTTP_CLIENT_ERROR, HTTP_RATE_LIMIT,
HTTP_SERVER_ERROR, NETWORK_TIMEOUT, NETWORK_OR_TLS_ERROR,
HTML_SERVER_RESPONSE_NOT_CSV,
XML_OR_VOTABLE_NOT_REQUESTED_CSV,
JSON_SERVER_RESPONSE_NOT_CSV, UNRECOGNIZED_IRSA_TABLE_SCHEMA,
RESPONSE_TOO_LARGE_TO_VALIDATE, EMPTY_HTTP_BODY,
PARSED_TABLE_ZERO_ROWS, PARSED_TABLE_WITH_ROWS.

The [bounded live GitHub Actions workflow](../../.github/workflows/taurus-r2-irsa-diagnosis.yml)
produces a no-raw 24-source derived result ledger, with
a 30-day artifact retention.

## What is not proven

A parseable ZTF positional query is NOT a confirmed Gaia–ZTF
physical star association; neither is it independent WCS/PSF
image calibration. Empty responses do not demonstrate an empty
sky or a physically nonvariable star. Several OIDs inside 2
arcseconds may arise from distinct ZTF fields or source blending
and cannot be merged without image-level evaluation.

**R2 science remains open** pending independent Gaia/ZTF identity,
original image/mask crowding and literature membership checks.
The completed v2.0 scientific-software portfolio is unaffected.
