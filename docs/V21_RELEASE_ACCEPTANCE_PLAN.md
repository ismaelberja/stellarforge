# StellarForge v2.1 — software portfolio closeout acceptance plan

**Release-preparation date: 2026-11-13.** This is an **engineering portfolio** milestone, not a new astrophysical publication or a declaration that Taurus R2 source identity has been solved.

## Predeclared acceptance tests

1. Do **not** mutate historic v2.0 original-observation counts, manuscripts, source identifiers, 0.5–1.5 native ZTF PSF χ target gate, or old source pass/fail decisions. The original v2.0 release manifest and release notes remain available as archival versions.
2. Pin current post-v2.0 genuine original-data work by **immutable report paths and source SHA/provenance**: PR #44–49 original IRSA source ledgers, original six-image chi-blind controls (1,095 reference catalogue *records*, 240 below chi 0.5), six-source same-image analytical Gaussian (4 numeric, 2 failed), original six-image native spatial DAOPhot PSF (6 numeric, 4 provisional internal screens, 2 reviews), and original CDS SIMBAD FT Tau vs Gaia DR3 149623711269425408 unique curated alias. These are separate *reuse of dated original images and observations*, not added unique stars or independent source discoveries.
3. New `RELEASE_MANIFEST_v2.1.json` must be audited offline with exact values matched against **existing committed source-derived JSON evidence**, historical v2.0 manifest, SHA hashes, no-raw source fields and status/claim barriers; perturbing any observed value or true/false claim must fail tests. Releasing software does NOT imply physical ZTF–Gaia identity, isolated sources, new variables, companions or independent instrument WCS/PSF covariance.
4. Update package version, CLI --version/help and CITATION metadata to `2.1.0`, maintain the former `2.0.0` release evidence checker in an explicitly **archival** mode, and keep all historical tests unless explicitly migrated for the new package version.
5. Add one **genuine-data derived-only SVG** with accessible title, description and source linking to the six exact dated ZTF native spatial-model source residual QA. Distinguish *original native PSF catalog source-quality status* from *internal same-image spatial PSF residual screen* on the chart; show no original image pixels or photometry. Original conceptual artwork remains clearly labelled nonobservational.
6. Update concise README, Spanish quick-start, reproducibility and CV/LinkedIn ES+EN, link science report and original Actions runs; present actual completed engineering and ongoing open physical identification separately.
7. Offline full pytest, both v2.0 *historical evidence* and v2.1 current evidence audits, pip check, stellarforge --version, package CLI and accessible SVG chart regression must pass on final PR head and **on merged main commit** before claiming closure.

## Release boundaries

No raw ZTF FITS/catalogues or private/unpublished ALMA/TFM data in Git. Do not call Gemini/AI art a telescope image. No inflation of source counts by adding repeated six-image subsets to historic four-exposure or 16-profile totals. Do not call SIMBAD exact-name agreement independent astrophysical measurement, nor same-source pixel checkerboard validation distinct reference-star calibration. v2.1 is complete as portfolio engineering only after successful main CI; R2 physical counterpart question and R3 scientific inference may remain open.
