# StellarForge — Phase 9: Per-Epoch Astrometry and Observational Evidence Gates

**Internal research and engineering report · v0.9.0 · 4 November 2026**  
**Scientific focus:** literature-confirmed Taurus membership, unverified ZTF source identity, no new astronomical classifications.

## 1. Why this work was necessary

A cone search is not an astrophysical source identification. The Zwicky Transient Facility (ZTF) returns photometric time series identified by separate `oid` values, potentially more than one per requested coordinate and band. A single catalogue position can differ from the actual stellar position at the observing epoch because of proper motion. This is important even if the displacement is small relative to a normal extraction radius. Weak blends, crowded fields, bad observations, and inconsistencies between epochs may create spurious variability or incorrect labels.

v0.8 produced a robust file parser and a coarse per-curve check, but the existing source-association workflow compared source centroids against a **single representative epoch**, derived from a median MJD. v0.9 adds a separate **point-by-point astrometric consistency screen**. Every photometric row with a valid ZTF position and MJD is compared to a Gaia position propagated to that *same* epoch. No time-system conversion is hidden.

The project remains a research platform. Positional agreement remains insufficient for confirmation without Gaia uncertainties, parallax, crowding/image analysis and independent source checks.

## 2. Target identity and sample

The technical seed comprises 24 sources extracted from a pinned third-party mirror of the **adopted Taurus members** in Luhman (2023), Table 2. The public copy has the expected 532 adopted members and 467 unique Gaia DR3 IDs, but its bytes have **not** been independently matched against the publisher's table. It is a provisional literature-data source, not an independently validated scientific sample. Disk classifications and astrophysical variability are not assumed.

The first two named targets are:

| Source | Gaia DR3 source ID | What is available | Outstanding |
|---|---|---|---|
| **FT Tau** | `149623711269425408` | Catalogue position, proper motion, an official API request plan | Successful official ZTF raw response, OID identity, image vetting, disk source |
| **CIDA 11** | `3419110734340795648` | Catalogue position, proper motion, an official API request plan | The same evidence gates |

The technical target selection is intentionally small; it is not a statistically representative study of stellar dipping frequency.

## 3. Photometric acquisition and failures

A real IRSA public-light-curve query was **attempted separately for both sources** on 4 November 2026. Both calls raised `URLError` because the runtime could not resolve/connect to the official IRSA host. The outcome is logged in `reports/observational_gates_v0.9/RUN_SUMMARY.json`.

**Crucial:** failure to fetch data does not mean that ZTF never observed the target. The database coverage and existence of a counterpart remain **unknown**. No local observation record is substituted or inferred from the catalogue coordinate.

The query conforms to the public ZTF Lightcurve API, with `POS=CIRCLE`, `BANDNAME=g,r`, `BAD_CATFLAGS_MASK=32768`, and `FORMAT=csv`. Its full URL is retained in the query plan and target dossiers. If access becomes possible in a future research environment, `python scripts/run_v09_pipeline.py --execute` will perform exactly two requests, store raw responses with SHA-256 sidecars and re-run the evidence gates. A returned `oid` will not be marked as a confirmed match.

**Primary API documentation:** <https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html>  
**ZTF archive:** <https://irsa.ipac.caltech.edu/Missions/ztf.html>

### Ethical provenance distinction

- Original catalogue coordinate: **literature value in a pinned public mirror**; original-publisher byte comparison pending.
- Local ZTF CSV plus a SHA-256 sidecar: **integrity-checked local content**, not authenticated as coming from IRSA by the sidecar alone.
- Raw HTTP response from IRSA: evidence of acquisition, but still not a verified match to a Taurus member.
- Multiple `oid` values: never merge them automatically to improve apparent cadence or event significance.
- A ZTF light curve from a third-party repository used in v0.8 is **not** a Taurus light curve and is not reused as one in v0.9.

## 4. Per-epoch association method

For each accepted observation with MJD, an RA/Dec estimate and band and object identifiers:

1. Parse the original row without changing its time convention, identifying `oid`, filter, time, RA, Dec and quality flags.
2. Convert MJD to an **approximate** Julian year for **astrometric screening only**, without using it as a precision photometric time conversion.
3. Propagate the Gaia unit-vector position from J2016.0 using the published `μ_α*` and `μ_δ` for this epoch.
4. Compute the spherical great-circle separation of the propagated position and the recorded ZTF row position.
5. Keep the raw catalogue-coordinate separation for comparison, plus median and 95th-percentile epoch-corrected separations for each `oid` / band / time-system group.
6. Flag `outside_radius_all_epochs`, `mixed_inside_outside_radius`, `insufficient_epoch_positions`, or `provisional_inside_radius_all_epochs` as descriptive categories.
7. If multiple `oid` objects pass in the same band, raise an explicit `ambiguous_multiple_oids_same_band` warning. **No category confirms astrophysical identity**.

This is a **2D first-order proper-motion approximation**, not a full Gaia propagation. It does not incorporate parallactic displacement, full astrometric covariance, perspective acceleration, uncertainty from ZTF astrometry, or PSF-level deblending. An apparent zero separation in a synthetic test is not an empirical precision claim.

## 5. Evidence hierarchy and dossier status

The new `observational_dossier.py` layer reports independently for each target:

- The literature catalogue coordinate and its current evidence level.
- An official IRSA URL, whether a network request occurred and whether a raw response file exists.
- Hash integrity of a provided local file; **whether it only claims** to originate from IRSA.
- Per-curve photometric QC, candidate `oid` counts and missing/noisy/flagged data.
- Per-epoch astrometric screening, possible multiple-OID ambiguity and limitations.
- Pending independent checks: original catalogue, raw official provenance, Gaia/IRSA identity, image blending, same-field controls and physical follow-up.

A local file may be labelled `RAW_PRELIMINARY_QC_PASSED_IDENTITY_REVIEW_REQUIRED`, **not** 'verified ZTF Taurus star'. Only an independent human-led scientific review of real data and source identity can advance it. A missing response is `OFFICIAL_IRSA_PHOTOMETRY_PENDING`, **never** 'not variable' or 'no ZTF coverage'.

A static standalone HTML evidence dashboard has been generated. It can be viewed offline and shows source gates and the official query links, not observational findings. This is intentionally useful both for scientific traceability and for software-engineering demonstrations of fail-closed data pipelines.

## 6. Verification and tests

**303 automated Python tests pass** in the v0.9 project (239 inherited and 64 new tests).

The new tests cover:

- Exact preservation of Gaia source IDs (no floating-point conversion).
- Per-row epoch propagation, including RA wrap and high proper-motion artificial cases.
- OIDs in separate bands, multiple competing OIDs in the same band, missing coordinates and unavailable time conventions.
- Invalid epochs, radius limits, malformed IDs and bad proper motions.
- Missing raw files, SHA-256 mismatches and malicious lookalike 'IRSA' URL claims.
- Exactly two mock network requests; network errors do not create false 'no coverage' claims.
- Local-only and mocked successful raw acquisition without false source authentication.
- HTML injection safety in the dashboard, uniqueness of target IDs and no claimed new discoveries.

**No synthetic validation case is evidence of a real astronomical detection.**

Reproducible commands:

```bash
python -m pip install -e '.[analysis,test]'
python -m pytest -q
python scripts/run_v09_pipeline.py  # offline, creates two pending dossiers
python scripts/plot_v09_catalog_motion.py
# Only on a machine with network access, explicitly enabled:
python scripts/run_v09_pipeline.py --execute
```

## 7. What would make the next phase scientifically significant

1. Retrieve official raw ZTF tables for FT Tau and CIDA 11 with successful HTTPS requests, storing immutable raw data and versioned source metadata.
2. Split returned data by `oid`, passband, and actual observation clock; preserve flags and rejected points.
3. Use the per-epoch screen and inspect relevant ZTF science-image cutouts and Gaia neighbors; verify that the light curve belongs to the intended source, especially in blended regions.
4. Select at least three truly independent, non-variable, same-field comparison sources with genuinely comparable exposure/calibration conditions.
5. Repeat injection/recovery on the **actual observed epochs and uncertainties**; report completeness separately across amplitude and duration.
6. Check object-specific literature and external surveys before inferring disk occultation, accretion or any new classification.
7. Only then consider expanding to 24 members and beyond; assess selection bias, multiple testing and systematic drift.

**Status:** Research engineering advanced; true Taurus ZTF observational validation still blocked by network access. No new astrophysical classification or published discovery.