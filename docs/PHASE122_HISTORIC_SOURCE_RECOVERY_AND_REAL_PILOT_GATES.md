# StellarForge v1.22 — Recovering the exact historic ZTF source archive

**10 November 2026. Real original archival SOURCE bytes recovered and matched
to GitHub Actions SHA-256; new PSF science tests are still simulated.**

## Historical source archive preserved privately

Original source: GitHub Actions run **41997079598**,
artifact **13401380025**, name
`taurus-two-target-raw-UNVERIFIED` in the public StellarForge
repository. This is the original **two-target IRSA ZTF positional-lightcurve
query** artifact, NOT the original dated ZTF CCD science FITS exposures.

The 181,170-byte ZIP was downloaded directly from the GitHub Actions
artifact before its reported expiry on **12 November 2026 at 08:47:05 UTC**.
The retrieved ZIP's SHA-256 independently matched the digest supplied in
the GitHub Actions artifact metadata:

    d54246e00d4cf343b0b062b9eb92034e51c735067274a8109e9b2c2c2a2d5167

The exact content inventory is four members: two original IRSA CSV
query responses, one original PILOT_STATUS.json acquisition manifest
and one original REPORT.md. The raw files remained **outside Git**.
The recovered ZIP was supplied privately as a conversation download
and should be retained by the project owner in secure local storage.

**The file integrity check establishes byte-for-byte provenance of the
recovered GitHub Actions artifact.** It does NOT independently verify
the physical identification of Gaia with any ZTF light curve,
PSF, stellar variability or astrophysical discovery.

The new standard-library
`scripts/check_v122_historic_source_zip.py` utility verifies:
- a pinned SHA-256 equal to the original GitHub artifact metadata;
- complete exact four-file ZIP inventory, absence of extra files
  and paths, size limits and archive CRC;
- source IDs, two response fields and anti-overclaim flags in the
  original acquisition manifest;
- individual CSV raw-byte counts and hashes against that manifest;
- no original survey bytes in output (only status, counts and SHA).

The verifier is intentionally **read-only** and its CLI does not
allow overriding the pinned original digest. For regression tests only,
an alternative expected SHA can be injected into the Python function
with wholly synthetic fabricated ZIPs.

## v1.20 full original-data runner control-flow tests

The pre-existing real original CIDA 11 science runner could not
previously prove its *positive* end-to-end execution in CI, because
earlier mocked tests concentrated on missing cohorts and the
v1.19/v1.20 individual synthetic image validators.

Two new **fully mocked, no-network** integration paths have now been
added:

1. A synthetic original artifact, exact two fake exposure dates,
   fake source PSF catalogue and mock original science/mask FITS
   are supplied. An actual v1.19 empirical model is run on **4
   distinct training + 3 distinct held-out simulated stars** per
   date. The real runner's public report marks two internal
   whole-star models completed but explicitly denies an
   independent original ZTF survey calibration or discovery.
2. Two of three synthetic held-out stars are deliberately
   rejected by mock mask checks. No replacement is performed and
   the runner correctly marks the **3+2 real-source eligibility
   gate not met** even though four training sources remain.

This proves that the *software pipeline* can be exercised through
the normal run() entry point, that the outer reporting status
is internally consistent, and that synthetic failure does not
become a false physical nondetection. The simulations are
**not real PSF measurements**.

## What is still missing

The actual v1.20 manually dispatched original image workflow has
**not been executed** in this release. It must acquire Gaia DR3
live astrometry, exact original dated ZTF `psfcat.fits`
catalogues and **new science+mask FITS cutouts**. The recovered
photometric ZIP alone cannot replace those live image requests.

The unexpired GitHub artifact can be used with the manual
[Actions workflow](https://github.com/ismaelberja/stellarforge/actions/workflows/v120-original-empirical-psf-pilot.yml)
before GitHub expires it. After expiry, the recovered **private
local ZIP** can be used as the first positional-source argument to
`scripts/run_v120_original_empirical_psf_pilot.py`;
this still needs network access to ESA Gaia DR3 TAP and IRSA ZTF
image services when actually run.

Do NOT reinterpret an internal different-star holdout fit as
external ZTF DAOPhot training-star independence. The original
PSF-training star roster, physical Gaia–ZTF association, WCS
accuracy and complete correlated CCD uncertainty calibration
remain unverified. The three real v1.16 anomalous residual
profiles remain unresolved.

## Final engineering roadmap

One further release review should suffice for a defensible **v2.0
software portfolio** if manual evidence is recorded as a validated
real result or an explicit scientifically defensible blocker.
Any independent scientific publication requires additional
validation without a predetermined iteration count.

This version contains no raw archival data, science FITS,
Gaia catalogues or original stellar pixel stamp files in Git.
