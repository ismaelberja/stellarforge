# Phase 10 — private observational pilot, reproducible acquisition and g−r diagnostics

## Research objective

1. Run the two pre-registered ZTF API requests for **FT Tau** and **CIDA 11** from a network-enabled, isolated runner.
2. Store immutable raw response bytes and local SHA-256 provenance; keep raw data out of git history.
3. Produce per-object evidence dossiers and a triage ledger, explicitly distinguishing unavailable data from non-detections.
4. Before invoking any physical interpretation, inspect source identity and imaging, then test g−r variability using only near-simultaneous, separately identified bands.

## Official source

IRSA documents the endpoint `https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves`, with `POS=CIRCLE`, `BANDNAME=g,r`, `FORMAT=csv`, and `BAD_CATFLAGS_MASK=32768`. Its response may contain *multiple ZTF OIDs* for one cone. The nearest OID must not automatically be treated as the Gaia member. See [official API documentation](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html).

## GitHub Actions research handoff

The **manual** `StellarForge — official ZTF two-target observational pilot` workflow runs only when requested. It installs the project, executes all tests, calls the two official queries (no broad scraping), creates raw files only in an isolated runner, and uploads a *private workflow artifact* for offline human/scientific review. Its result is never auto-committed as a discovery. `GITHUB_TOKEN` has read-only repository permissions; raw response payloads are excluded from Git.

Even successful HTTPS + SHA-256 does **not** independently authenticate a telescope dataset or establish a source cross-match. The manuscript-level gates remain open. Respect IRSA operational limits; the pipeline makes only two requests per run with no retry storm.

## Multi-band diagnostics

`match_g_r_points` accepts **two explicitly specified and distinct ZTF OIDs** and requires a common specified time convention. It constructs one-to-one g/r pairs within a user-specified separation and propagates the magnitude uncertainty as:

`σ(g−r)=sqrt(σ_g² + σ_r²)`.

No interpolation or cross-source pooling is performed. Outputs are *approximate, non-simultaneous color differences*, never proof of extinction, accretion or disk inclination. Source identity, calibration systematics, image examination and independent disk indicators must be vetted before deriving physical classes.

## Scope and limits

- Gaia catalogue mirror has not been byte-verified against publisher original.
- Neither ZTF OID nor Gaia counterpart is authenticated simply by a cone search.
- No confirmed Taurus dippers/bursters or scientific detections are claimed.
- Injection and recovery numbers from v0.7 are **synthetic**, not real survey selection functions.
- The scientific reviewer must inspect `V10_TRIAGE.json`, dossiers, multi-band evidence, control stars and images before any candidate is reported.