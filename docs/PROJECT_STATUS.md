# StellarForge — Current project status

**Version:** 1.3.0 · **Updated:** 2026-11-05 · **Engineering status:** active, tested · **Scientific status:** unverified Gaia–ZTF source associations.

## Implemented

- Full Python package, command-line utilities, tests, continuous integration and research documentation.
- 337/337 automated tests passed in GitHub Actions on the v1.3 development branch (5 November 2026).
- Pinned secondary Taurus catalog audit: 532 adopted members, 467 Gaia identifiers; 24-object technical seed.
- Two official IRSA ZTF cone-query responses near FT Tau and CIDA 11 on 5 November 2026, totaling 2,212 rows across six distinct ZTF OIDs; integrity hashes and failures are logged.
- Reproducible SHA-checked **provisional Gaia-to-ZTF per-epoch screen** for all six OID/passbands; median positional separations ~0.063–0.092 arcsec (not independently verified identities).
- Scientific data integrity gates: distinct OIDs/bands, flag masking, hashes, time-scale handling, provisional astrometric checks and synthetic-only benchmarking.

## Not yet established

- Independent Gaia/ZTF source identity or confirmed physical variability.
- Publisher-original Taurus catalog byte verification.
- Images, full covariance/parallax, crowded-field alternatives and field-star controls for these ZTF sources.
- Real-survey detection completeness, false-positive rate or representative disk-class sample.

## Public portfolio boundary

The repository may be viewed as *research software in development*. Do not interpret provisional code outputs, observational cone-search rows or synthetic benchmarks as claims of astrophysical discoveries. Raw third-party photometric downloads must remain outside Git until legal/provenance/reuse constraints are reviewed.

## Next scientific milestone

**Next science gate:** independent ZTF image, centroid, crowding and Gaia-neighbour review, followed by full covariance/parallax-aware astrometry. v1.3 provides the preliminary per-epoch positional evidence, not confirmed matches.

Read the [observational transport report](../reports/observational_intake_v1.2/RAW_TRANSPORT_AUDIT.md) for precise counts and caveats.

Read the [v1.3 positional screening report](../reports/astrometry_v1.3/PROVISIONAL_POSITIONS_REPORT.md) for six measured OID-band groups and limits.
