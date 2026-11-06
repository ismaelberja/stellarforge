# StellarForge — Current project status

**Version:** 1.9.0 · **Updated:** 2026-11-06 · **Engineering status:** active, tested · **Scientific status:** unverified Gaia–ZTF source associations.

## Implemented

- Full Python package, command-line utilities, tests, continuous integration and research documentation.
- 444/444 automated tests passed in GitHub Actions during the v1.9 real Gaia DR3 pilot (6 November 2026).
- Pinned secondary Taurus catalog audit: 532 adopted members, 467 Gaia identifiers; 24-object technical seed.
- Two official IRSA ZTF cone-query responses near FT Tau and CIDA 11 on 5 November 2026, totaling 2,212 rows across six distinct ZTF OIDs; integrity hashes and failures are logged.
- Reproducible SHA-checked **provisional Gaia-to-ZTF per-epoch screen** for all six OID/passbands; median positional separations ~0.063–0.092 arcsec (not independently verified identities).
- Independent Gaia DR3 TAP 15-arcsec sky-field queries around FT Tau and CIDA 11 both returned only the target Gaia source; **this does not rule out non-Gaia or unresolved contamination**.
- Gaia DR3 RUWE values: FT Tau 1.3266, CIDA 11 8.5675. The latter is an astrometric-fit quality concern, not proof of binarity.
- Official science/reference ZTF cutout links and header transport probes in v1.4 (intermittent HTTP 503).
- **v1.5 real FITS pixel screening:** 5 of 6 ZTF OID-band groups had real FITS pixels opened and celestial WCS checked (3 science frames, 2 reference coadds); all five show a local maximum within 0.5 arcsec of Gaia's approximate position.
- **v1.6 local Gaussian image-shape screening:** three FT Tau individual science images passed bounded single-Gaussian-plus-background fitting. All three have high model residuals and require further review; no CIDA 11 fits and no OID/filter with two independent usable science images in this execution. The fit is not an independently calibrated PSF.
- **v1.7 independent science exposure review:** 12 individual real FITS science images (2 distinct images per each of 6 OID/filter groups; 8 FT Tau, 4 CIDA 11) passed provisional 2D FITS/WCS + radial-profile screening; no reference coadds counted. Pairwise nominal WCS/Gaia-proxy centroid-residual differences ~0.024–0.097 arcsec, not calibrated astrometric errors.
- **v1.7 same-image field-control attempt:** 90-arcsec cutouts, but 0 of 12 frames yielded two usable unclassified comparison brightness peaks; no empirical PSF calibration or clean-source claim. 11/12 simple Gaussian profiles flagged for residual review. Source identity remains unverified.
- **v1.8 Gaia DR3-backed reference-star candidate pilot:** 210-arcsec wide-field Gaia queries returned 50 entries around FT Tau and 250 around CIDA 11; 3+5 passed quality/isolation screening. Four genuine target FITS frames and 16 candidate reference cutouts from the same science exposure paths were attempted; 13 references fitted. Three exposures permit a **provisional local offset translation** with >=3 candidate Gaia controls; no independent WCS solution, authenticated empirical PSF, or source identity is claimed.
- **v1.9 actual Gaia DR3 5×5 formal astrometric covariance and annual parallax:** independent TAP returns exact FT Tau/CIDA 11 Gaia IDs with ten correlations and five positional/parallax/PM formal errors. Four real ZTF observation MJDs evaluated with offline Earth-geocentric geometric parallax, providing signed offsets and formal Gaia-only 2D covariance; **no ZTF WCS/PSF uncertainty or physical source identity validated**. High CIDA 11 RUWE ≈ 8.57 cautions that catalogue formal errors may underestimate physical uncertainties.
- Scientific data integrity gates: distinct OIDs/bands, flag masking, hashes, time-scale handling, provisional astrometric checks and synthetic-only benchmarking.

## Not yet established

- Independent Gaia/ZTF source identity or confirmed physical variability.
- Publisher-original Taurus catalog byte verification.
- Fully authenticated stellar PSF references, independent distortion/field-WCS solution, deblending, photometric centroid/background errors, full observer/time-scale/radial-velocity modeling and non-Gaia neighbors. v1.9 propagates *Gaia's five-parameter formal covariance and first-order annual parallax* for two target sources but does not validate actual ZTF instrument errors or single-star model biases.
- Real-survey detection completeness, false-positive rate or representative disk-class sample.

## Public portfolio boundary

The repository may be viewed as *research software in development*. Do not interpret provisional code outputs, observational cone-search rows or synthetic benchmarks as claims of astrophysical discoveries. Raw third-party photometric downloads must remain outside Git until legal/provenance/reuse constraints are reviewed.

## Next scientific milestone

**Next science gate:** authenticate candidate reference-star morphology and PSF, independently calibrate detector WCS and residual error budgets against the Gaia-propagated positions, verify ZTF time headers and source identities, and review CIDA 11's non-single-star astrometric warning.

Read the [observational transport report](../reports/observational_intake_v1.2/RAW_TRANSPORT_AUDIT.md) for precise counts and caveats.

Read the [v1.3 positional screening report](../reports/astrometry_v1.3/PROVISIONAL_POSITIONS_REPORT.md) for six measured OID-band groups and limits.

Read the [v1.4 independent Gaia/IRSA audit](../reports/field_review_v1.4/GAIA_NEIGHBOURS_AND_IRSA_IMAGES.md) for actual online query evidence and limitations.

[v1.5 real FITS pixel/WCS results](../reports/real_fits_v1.5/PIXEL_WCS_RESULTS.md): five provisional image screens, **zero source identities confirmed**.

Read the [v1.6 real Gaussian-profile review](../reports/psf_v1.6/REAL_GAUSSIAN_FIT_REVIEW.md): three provisional fits, zero source identities or repeated-epoch confirmations.

Read the [v1.7 real-image multi-epoch and field-control audit](../reports/field_controls_v1.7/REAL_MULTIEPOCH_AND_CONTROL_LIMITS.md) for verified measurements and strict limitations.

Read the [v1.8 real Gaia reference-candidate audit](../reports/gaia_reference_v1.8/REAL_REFERENCE_CANDIDATE_EVIDENCE.md), where three local translation proxies are carefully separated from independently calibrated astrometry.

Read the [v1.9 real Gaia DR3 formal covariance and annual parallax audit](../reports/gaia_formal_v1.9/GAIA_COVARIANCE_AND_ANNUAL_PARALLAX.md). These are not ZTF astrometric measurement errors or astronomical source matches.
