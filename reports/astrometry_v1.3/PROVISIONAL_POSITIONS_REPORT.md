# StellarForge v1.3 — Gaia/ZTF per-epoch positional screening

**Status (5 November 2026): engineering/astrometric screening completed; zero independently confirmed Gaia–ZTF identities.**

## Traceable real-data run

- Input: two official IRSA ZTF cone queries, preserved in the [5 November 2026 GitHub Actions raw artifact](https://github.com/ismaelberja/stellarforge/actions/runs/41997079598) (temporary retention).
- Analysis: [v1.3 real-input workflow](https://github.com/ismaelberja/stellarforge/actions/runs/42001059051).
- Parsed source rows: **2,212** (FT Tau 1,199; CIDA 11 1,013).
- Quality filter retained all 2,212 records under the specific `catflags & 32768` mask; this is not full scientific quality acceptance.
- Per-source comparisons use approximate Gaia DR3 **J2016.0** positions propagated to each ZTF `mjd` using published two-dimensional proper motions. **No full covariance/parallax modeling or image/blend review**.

| Cone-query target | ZTF OID | Filter | Field | QC points | Median Gaia-epoch separation (arcsec) | 95th percentile (arcsec) |
|---|---|---|---|---:|---:|---:|
| FT Tau | 1605115300003377 | g | 1605 | 70 | 0.085268 | 0.198972 |
| FT Tau | 1605215300005161 | r | 1605 | 117 | 0.088981 | 0.236029 |
| FT Tau | 609108400001155 | g | 609 | 404 | 0.092088 | 0.181941 |
| FT Tau | 609208400001969 | r | 609 | 608 | 0.084976 | 0.189142 |
| CIDA 11 | 610106300008010 | g | 610 | 397 | 0.085895 | 0.161925 |
| CIDA 11 | 610206300011997 | r | 610 | 616 | 0.062533 | 0.143534 |

The median epoch-corrected separations are all below 0.1 arcsec. **This is positional compatibility within preselected 2-arcsec search cones**, not evidence of confirmed identity. In particular, the cone search itself favors nearby ZTF detections, while neighboring stars or blended measurements could lie close to those positions.

**FT Tau:** four OIDs, with two in each band across two ZTF fields (609 and 1605). They must remain separate until cross-field identity, PSF, WCS and image blending are reviewed.

**CIDA 11:** one ZTF OID per filter in field 610. This reduces the multiplicity of candidates returned by this query but still **does not confirm** Gaia/ZTF identity.

## Data and computation safeguards

1. Original CSV byte counts, SHA-256 and official API query strings were checked against the source artifact's `PILOT_STATUS.json`.
2. The run verified the pinned local catalog Gaia source IDs and source positions (secondary Luhman 2023 mirror; publisher comparison still outstanding).
3. A row must pass photometric QC and retain a valid MJD/RA/Dec to enter the epoch-aware screen; no cross-band magnitudes are merged.
4. ZTF OID, passband, field, CCD and quadrant metadata are preserved by group.
5. No raw CSV or individual exposure-level measurements are added to Git history; only this aggregate report is published.

## Reproduce locally

```bash
python -m pip install -e '.[test,analysis]'
python -m pytest -q
python scripts/run_v13_astrometric_review.py /path/to/downloaded_IRSA_artifact.zip
```

The script writes JSON and Markdown summaries under ignored `reports/generated/v1.3_astrometry`. The original GitHub Actions raw artifact expires after seven days. For later reproduction, reacquire observations from the official IRSA API, record new hashes and check any possible survey updates.

## Open scientific review gates

- Independent image cutouts, source centroids/WCS and crowded-field/blending assessments.
- Gaia astrometric uncertainties, covariances, parallaxes and alternative nearby Gaia sources.
- Original publisher-file verification for Luhman (2023), independent disk classes, and epoch/time-system handling.
- Field-control photometry and real-cadence detection-efficiency tests before physical variability claims.

**Verified astrophysical source associations: 0. New physical event detections: 0.** The six positional groupings above are engineering diagnostics, not a scientific source catalogue.
