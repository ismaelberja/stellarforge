# StellarForge v2.1 — reproducibility, research evidence and scientific limits

**13 November 2026 — Engineering portfolio closeout.** The current v2.1 portfolio software can be verified **without live archival access**. Original individual Gaia/ZTF source IDs are not certified as physically associated, and no astronomical discovery is claimed.

## Release categories: keep experimental denominators separate

| Category | What was actually executed / reviewed | Interpretation |
| --- | --- | --- |
| Historical original v2.0 evidence | A third-party 532-row Taurus mirror with 467 Gaia IDs; original 2,212 positional-query rows; four historical g-band science exposures, 16 older same-source profile fits (13 provisional screens, 3 review) | These are original observations/derived reports, not a representative sample or unique counterpart catalogue |
| Six fixed original FT Tau follow-ups | Six exact g/r early+late source-epoch PSFcat/science/mask checksums; all six original spatial DAOPhot models and center stamps parsed | These are existing original dated detector exposures reused in multiple experiments, **not six new sources** or an extension of the older four-exposure denominator |
| Chi-blind PSF controls | 1,095 per-image native source catalogue control **records** in six FITS source files; 240 below the previously frozen chi cutoff of 0.5 | Records can repeat across images; no independently verified physical-control-star population and no warranted change of χ≥0.5 |
| Circular analytic Gaussian pilot | Four numerical fits to six fixed original science-image cores; two constrained numeric failures | A simple Gaussian is *not* the instrument's spatially varying PSF, and residual/noise statistics are uncalibrated |
| Native ZTF DAOPhot spatial PSF | Six numerical same-source spatial-model pixel fits; four provisional same-image checkerboard residual screens passed, two r/609 images require review | Spatial PSF/field-centre products share the same pipeline; checkerboard pixels **belong to the same image of the same source**, not separate independent stars |
| External SIMBAD name-index | Two exact identifier lookups to the same CDS SIMBAD mirror returned the one same record for FT Tau and Gaia DR3 149623711269425408, main identifier V* FT Tau | Curated external catalogue name/alias correspondence only; not an independent physical association between Gaia and ZTF detections |

**Do not sum the four historical observations and six later observations into a population study, or count 1,095 source catalogue records as independently identified stars.**

## Offline setup and audits

Requires Python 3.10+; Python 3.11 used in GitHub Actions.

```bash
git clone https://github.com/ismaelberja/stellarforge.git
cd stellarforge
python -m pip install -e ".[test,analysis,images]"
python -m pytest -q
python scripts/audit_v21_release_manifest.py
python scripts/audit_v2_release_manifest.py     # historical v2.0 evidence only
stellarforge --version
stellarforge --help
stellarforge plan-gaia --ra 70 --dec 20 --radius-deg 0.1 --max-rows 10
```

Auditor v2.1 checks package/citation/README parity and literal source fields from four separate **original-data-derived-only** receipts, reconciles all six date/PSFcat/science/mask hashes, counts original reference records, and rejects unsupported independent-identity/variability/companion claims. Mutated counts, swapped image checksums, replaced source status labels, or converted false scientific claims are rejected by tests. Auditor v2.0 remains in the repository as an archival source-count evidence contract, not the present version number.

**No original downloads are necessary for the regular suite.** Live reproducibility of the individual research experiments requires network-accessible Gaia/IRSA/CDS products and the relevant dedicated GitHub Actions workflows; some original raw artifacts have time-limited retention. Only derived summaries and original byte hashes are committed publicly.

## Original-data run evidence

- [Original six native ZTF chi-blind reference study](../research/taurus_variability/R2_REAL_FTTAU_SIX_ORIGINAL_CHI_REFERENCE_RESULTS.md), run [43275404347](https://github.com/ismaelberja/stellarforge/actions/runs/43275404347)
- [Six independent analytic Gaussian original science images](../research/taurus_variability/R2_REAL_FTTAU_SIX_ORIGINAL_GAUSSIAN_PIXEL_RESULTS.md), run [43279744985](https://github.com/ismaelberja/stellarforge/actions/runs/43279744985)
- [Six original native spatial PSF source-pixel holdouts](../research/taurus_variability/R2_REAL_FTTAU_SIX_NATIVE_SPATIAL_DAO_RESULTS.md), run [43310945601](https://github.com/ismaelberja/stellarforge/actions/runs/43310945601)
- [Exact external SIMBAD vs Gaia name audit](../research/taurus_variability/R2_REAL_FTTAU_SIMBAD_GAIA_EXACT_ALIAS_RESULTS.md), run [43314507016](https://github.com/ismaelberja/stellarforge/actions/runs/43314507016)
- [v2.0 historic source receipt](../data/research_seed/V122_ORIGINAL_IRSA_ARTIFACT_RECEIPT_NO_RAW.json), original historical ZIP verified locally then withheld from Git

## What remains scientifically unresolved

The original 0.5≤native chi≤1.5 acceptance gate was frozen before the later fits. The three late low-chi source candidates remain **FAILED** on that criterion, even where a different internal spatial PSF source-pixel check passed. The old **5/8 pass, 3/8 fail** source decisions and **1/4 two-night accepted same-field/band pairs** are unchanged. Four source ObjectIDs were *not* joined into one physical target time series.

A source-specific **independent** physical Gaia-to-ZTF association requires adequate reference astrometry, exposure-matched positions and uncertainties, source crowding/deblending analysis and independent comparison to the instrument's PSF training-star roster. The externally curated SIMBAD record supports the **historical Gaia name alias**, not those additional measurements. The r/609 residual review also needs source-aware follow-up; no claimed 7-sigma detection or astrophysical variability follows from its residual/noise proxy.

The strictly preregistered **distinct whole-star empirical PSF pilot for CIDA 11** remains separate and not confirmed as genuinely executed. Original source-pixel masks and native model residuals are not independent stellar error calibration. No ALMA/TFM collaboration inputs or raw nonredistributable survey exposures are included.

## Final software acceptance criterion

The software has a stable Python CLI, source-visible scientific methods, original-data receipt tests, an accessible source-derived portfolio chart, English/Spanish onboarding, claim-by-claim evidence and CI. A v2.1 PR is only accepted as released when its **merged main SHA** has a **successful full suite**, offline v2.1 and historic v2.0 audit, and package metadata/CLI validation. A green CI gate establishes software consistency, **not** an astrophysical new-object discovery.
