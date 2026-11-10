# StellarForge v2.0 — Reproducibility and scientific limits

**Engineering portfolio release · 10 November 2026**

The project is **scientific software with historical real-data demonstrations**,
not a validated astrophysical survey detection catalogue or a research paper
claiming a newly discovered object.

## Evidence categories (do not mix)

| Evidence tier | What it means | Reference |
| --- | --- | --- |
| Original historical | Published ZTF/Gaia survey products were acquired, parsed and evaluated at the recorded original observation epochs | [v1.16 source pixel report](../reports/masked_spatial_psf_v1.16/REAL_ZTF_PIXEL_RESIDUALS_EVIDENCE.md) |
| Original archival transport | Exactly the historical two-target IRSA source ZIP previously saved by GitHub Actions was privately recovered with matching SHA-256 | [v1.22 no-raw receipt](../data/research_seed/V122_ORIGINAL_IRSA_ARTIFACT_RECEIPT_NO_RAW.json) |
| Derived and provisional | Source catalogue associations, centroids, residual ratios, Gaia reference profiles, original DAOPhot fits and risk counts; survey pipeline choices or selection biases may still affect them | [v1.17 controls](../reports/new_gaia_holdouts_v1.17/REAL_DISJOINT_GAIA_CONTROL_AND_SHIFTED_SKY_RESULTS.md) |
| Synthetic software validation | Invented Gaia/FITS/noise inputs, injected profile perturbations and mocked network responses; checks numerical implementation and defensive behavior | [v1.19 synthetic evidence](../reports/empirical_star_psf_v1.19/SYNTHETIC_VALIDATION_AND_REAL_DATA_GATES.md) |
| Missing / unconfirmed | Source-level original DAOPhot PSF training-star roster, confirmed physical Gaia/ZTF match, full CCD noise covariance, external WCS/PSF calibration, new stellar variability or companion discovery | [release manifest](../RELEASE_MANIFEST_v2.0.json) |

## Fully offline reproducibility

Install with Python 3.11 (3.10+ package requirement):

\`\`\`sh
git clone https://github.com/ismaelberja/stellarforge.git
cd stellarforge
python -m pip install -e ".[test,analysis,images]"
python -m pytest -q
python scripts/audit_v2_release_manifest.py
stellarforge --help
stellarforge plan-ztf --ra 70 --dec 20 --radius-arcsec 2
\`\`\`

The planner prints only a URL. It does **not** download ZTF products.
No original FITS or Gaia/IRSA files are required for the standard
offline  suite. GitHub Actions in
[.github/workflows/tests.yml](../.github/workflows/tests.yml) runs the
same tests without live astronomical endpoints and checks the v2.0
release claim manifest.

The prior v1.22 branch/main CI passed **752 tests** on the authentic
GitHub repository. The v2.0 checkout adds tests ensuring its public
release manifesto cannot silently change historic counts or claim
external calibration. The final version is valid only after its **own
main-branch CI** passes.

## Historical source archive: reproducible but PRIVATE

The original historical 2-target IRSA positional-query ZIP was
downloaded from GitHub Actions run **41997079598**, artifact
**13401380025** and matched SHA-256:

\`\`\`text
d54246e00d4cf343b0b062b9eb92034e51c735067274a8109e9b2c2c2a2d5167
\`\`\`

The ZIP has four original files (two source CSV responses, original
PILOT_STATUS.json and REPORT.md) and was not committed. Verify your
private copy:

\`\`\`sh
python scripts/check_v122_historic_source_zip.py /private/path/ztf-historic-source-run.zip
\`\`\`

Archive bytes matching the old GitHub artifact establish **byte
integrity of a historical data acquisition**, not survey source
identification. Original source star pixels cannot be reconstructed
from those photometric rows alone.

## Real original-image pilot: manual and separately gated

The [v1.20 original CIDA 11 empirical PSF workflow](../.github/workflows/v120-original-empirical-psf-pilot.yml)
was written to run only when **manually dispatched** (it is NOT
a normal CI job). It requires archived original photometric source
ZIP, live Gaia DR3 5-parameter astrometry and ZTF original native
PSF catalogue, science FITS and bitmasks from IRSA.

- Gaia-only quality and isolation select up to seven **predeclared**
  sources (4 training, 3 different heldout). Rejecting one after a
  ZTF PSFcat screen does not permit replacement based on observed
  performance.
- One exact original exposure needs at least **3** acceptable
  training and **2** different held-out stars with matching
  native PSFcat source profiles, WCS, mask and centering.
- The new empirical model does not use the old original DAOPhot
  PSF coefficients. It still relies on ZTF-pipeline selected
  source candidates; the original survey's actual PSF-building
  source roster is **not available** in the proven artifact.
- The original FITS recentering interpolates pixel data and
  introduces correlated noise; v1.19's simple CCD-noise
  approximation must not be labeled a verified survey error budget.
- If archive access fails, enough isolated stars are not found,
  or original science/mask images are rejected, report that
  failure—not an astronomical nondetection.
- **As of this v2.0 closure, that manual real-data run has not been
  recorded as executed.** All v1.20–v2.0 new whole-star empirical
  PSF successes remain synthetic regression evidence.

With a locally recovered private ZIP and archive network access,
the same runner may be invoked:

\`\`\`sh
python scripts/run_v120_original_empirical_psf_pilot.py /private/path/ztf-historic-source-run.zip --output reports/generated/v120_local_real_pilot
\`\`\`

Output is designed to contain aggregate counts/statuses rather
than original source IDs/pixels. The workflow has its own
explicit no-raw artifact policy.

## Numerical original-data history worth discussing

- The Luhman (2023) third-party catalogue mirror has 532 members and
  467 Gaia source IDs. Publisher-original-byte check is open.
- Two original IRSA positional-source queries returned 2,212 rows
  across six ZTF IDs. This does not prove those IDs correspond to
  the named Gaia sources.
- Four original historical g-band exposures were inspected with
  spatial DAOPhot reconstructed local PSF models. Four original
  official *center-field* PSF files agreed with model reconstructions
  as an **internal instrument consistency test**.
- Sixteen genuine source science/mask image pairs had provisional
  DAOPhot-shape amplitude+background fits; thirteen passed
  *same-image checkerboard pixel residual* quality gates and
  three need review. Checkerboard pixels are NOT different stars.
- New truly disjoint Gaia candidate sources in v1.17 were distinct
  from StellarForge's earlier selection, **not proven independent of
  the original survey PSF training sample**.

## Three v1.16 review cases remain unexplained

| Provisional original source | MJD | RMS / sky MAD | Max-positive / sky MAD |
| --- | ---: | ---: | ---: |
| FT Tau target | 58491.184780 | 1.6723 | 7.6730 |
| CIDA 11 target | 58849.135984 | 2.6341 | 11.8679 |
| CIDA 11 field reference candidate | 58849.135984 | 1.3652 | 7.8125 |

The empirical 7× positive-residual cutoff was a **descriptive
software quality criterion**, not a calibrated seven-standard-
deviation probability or companion detection.

## Final gates: science is not the same as software

**Software release complete:** source code and command line install,
bounded original-data runners, comprehensive no-network regression
tests, GitHub Actions, reproducibility paths and explicit failures.

**Science not established:** independent source cross-identification,
unbiased selection function, ZTF original training-star roster,
instrumental WCS/PSF/CCD covariance calibration, independently
confirmed variability or new companions. These need separate
observational research and peer scientific evaluation.

No user-specific confidential ALMA/TFM datasets or unpublished
collaborative astrophysical products belong in this repository.
