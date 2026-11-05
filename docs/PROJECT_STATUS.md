# StellarForge — Current project status

**Version:** 1.7.0 · **Updated:** 2026-11-05 · **Engineering status:** active, tested · **Scientific status:** unverified Gaia–ZTF source associations.

## Implemented

- Full Python package, command-line utilities, tests, continuous integration and research documentation.
- 400/400 automated tests passed in GitHub Actions on the v1.7 research branch (5 November 2026).
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
- Scientific data integrity gates: distinct OIDs/bands, flag masking, hashes, time-scale handling, provisional astrometric checks and synthetic-only benchmarking.

## Not yet established

- Independent Gaia/ZTF source identity or confirmed physical variability.
- Publisher-original Taurus catalog byte verification.
- Empirical calibrated same-field ZTF PSF models, authenticated field controls, deblending and uncertainty-calibrated backgrounds, independently recalibrated FITS WCS, full Gaia covariance/parallax and non-Gaia neighbours. Two independent science frames per OID/filter now exist for descriptive comparison but do NOT establish physical astrometric consistency.
- Real-survey detection completeness, false-positive rate or representative disk-class sample.

## Public portfolio boundary

The repository may be viewed as *research software in development*. Do not interpret provisional code outputs, observational cone-search rows or synthetic benchmarks as claims of astrophysical discoveries. Raw third-party photometric downloads must remain outside Git until legal/provenance/reuse constraints are reviewed.

## Next scientific milestone

**Next science gate:** identify and authenticate stellar field controls (none currently meet the two-control screen), calibrate genuine ZTF PSF/WCS and error budgets using the 12 recovered science images, and validate Gaia full astrometry and CIDA 11 high RUWE.

Read the [observational transport report](../reports/observational_intake_v1.2/RAW_TRANSPORT_AUDIT.md) for precise counts and caveats.

Read the [v1.3 positional screening report](../reports/astrometry_v1.3/PROVISIONAL_POSITIONS_REPORT.md) for six measured OID-band groups and limits.

Read the [v1.4 independent Gaia/IRSA audit](../reports/field_review_v1.4/GAIA_NEIGHBOURS_AND_IRSA_IMAGES.md) for actual online query evidence and limitations.

[v1.5 real FITS pixel/WCS results](../reports/real_fits_v1.5/PIXEL_WCS_RESULTS.md): five provisional image screens, **zero source identities confirmed**.

Read the [v1.6 real Gaussian-profile review](../reports/psf_v1.6/REAL_GAUSSIAN_FIT_REVIEW.md): three provisional fits, zero source identities or repeated-epoch confirmations.

Read the [v1.7 real-image multi-epoch and field-control audit](../reports/field_controls_v1.7/REAL_MULTIEPOCH_AND_CONTROL_LIMITS.md) for verified measurements and strict limitations.
