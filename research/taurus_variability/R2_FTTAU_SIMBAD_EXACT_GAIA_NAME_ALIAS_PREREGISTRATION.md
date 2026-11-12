# Taurus R2 — prospectively registered FT Tau / Gaia DR3 SIMBAD alias audit

**12 November 2026. This protocol is committed before the first external SIMBAD query.**

## Fixed target and exact queries

Historical R1 target is FT Tau, Gaia DR3 source **149623711269425408**. Freeze original 24-source seed, four ZTF OIDs and all six PSFcat/science/mask observations in PR #44–48. No new original ZTF source quality selection, no original chi threshold change and no ZTF OID merging.

Use SIMBAD (CDS) TAP database with ident.oidref=basic.oid. Original native exact TAP ADQL queries are:

1. By Gaia name: `SELECT TOP 10 b.oid,b.main_id,b.ra,b.dec,b.otype FROM basic AS b JOIN ident AS i ON b.oid=i.oidref WHERE i.id='Gaia DR3 149623711269425408'`.
2. By historical name: `SELECT DISTINCT TOP 10 b.oid,b.main_id,b.ra,b.dec,b.otype FROM basic AS b JOIN ident AS i ON b.oid=i.oidref WHERE i.id IN ('FT Tau','V* FT Tau')`.

Strict positive alias equivalence requires exactly one unique SIMBAD oid for each independent exact-identifier query, and the OIDs equal. Empty results -> UNRESOLVED; multiple rows with different oid -> AMBIGUOUS; unique unequal oid -> CONFLICT. This is a curated independent-database **alias cross-index**, not source-specific physical Gaia–ZTF identification; SIMBAD's Gaia alias itself ultimately originates from Gaia data.

The CDS Strasbourg main site may be degraded during the November 2026 cybersecurity incident. The mirror priority is prospectively frozen: 1) https://simbad.cfa.harvard.edu/simbad/sim-tap/sync (CDS CfA mirror, archival holdings through 2026-10-14), 2) https://simbad.idia.ac.za/simbad/sim-tap/sync (CDS IDIA mirror). Run both identifiers on the SAME first functioning mirror. If inaccessible on both, status EXTERNAL_SERVICE_UNAVAILABLE, not an astrophysical nonmatch. Do not mix two mirrors or choose new alias strings after seeing outcomes.

HTTP POST only: REQUEST=doQuery, LANG=ADQL, FORMAT=csv, QUERY=the exact frozen statement, MAXREC=10, bounded original response ≤120,000 bytes and 25-second request timeout. Return must be CSV with exactly oid,main_id,ra,dec,otype; reject HTML/XML/error/truncated replies and malformed, nonfinite coordinates or object IDs. Return SHA-256, query SHA, endpoint, unique object counts and no-raw derived object metadata only. Never persist original source rows or full lists of aliases. The optional SIMBAD-basic vs Gaia DR3 (epoch 2016.0) sky separation is descriptive only: SIMBAD coordinates are not proven epoch-aligned or independently calibrated, and no numerical cutoff for identity is adopted.

Source historic context (not independent Gaia–ZTF proof): literature FT Tau near 04h23m39.19s +24°56′14.1″ in 2020 Taurus high-resolution companion survey and near 04h23m39.20s +24°56′13.9″ in 2024 JWST MINDS survey. These values do not create an added target-match filter.

## Frozen scientific boundaries

No independently authenticated physical Gaia–ZTF counterpart, high-resolution source deblending, 3-D astrometry, calibrated PSF/WCS covariance, new variable/companion or merged lightcurve is established by catalogue aliases. Previous original target source 5/8 accepted, 3/8 failed and 1/4 both-night passing pairs remain. R2 original ZTF source identity OPEN, R3 astrophysical claims BLOCKED even if external FT Tau/Gaia names are synonyms.

Official SIMBAD service URL protocol: https://simbad.cds.unistra.fr/Pages/guide/sim-url.htx ; TAP table join examples https://docs.astropy.org/projects/astroquery/en/stable/simbad/simbad.html ; CDS mirror guidance https://cds.unistra.fr/ .