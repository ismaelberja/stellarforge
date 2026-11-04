# StellarForge v1.1 — selection-bias and research cohort design (private)

- Integrated 24-target technical pilot diagnostics with independently computed counts from a pinned secondary 2023 Taurus table mirror.
- Added `src/stellarforge/selection_bias.py`, reproducible research script, a machine-readable selection audit, and two figures based on catalogue information.
- Confirmed 532 adopted members, 467 with Gaia IDs, 65 without; 64/65 Gaia-missing also lack a named group in the pinned mirror.
- Identified 314 Gaia-identified members with 12<=G<=17 and 289 with the additional group criterion. Pilot selection: 24/289 and covers 13 named groups.
- Included tests for integrity, duplicate IDs, invalid brightness and descriptive Wilson interval edge cases.
- **325 tests passed locally.**
- **No official Taurus ZTF light curve or physical dipper/burster classification confirmed.**
- **Primary publisher bytes still not independently compared** with mirrored Table 2; a pinned mirror is not a new observational measurement.