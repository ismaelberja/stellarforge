# StellarForge v2.1.0 — reproducible scientific-software portfolio

**Software release date: 13 November 2026.** Engineering closeout built upon original-data validation performed 10–12 November 2026. This release is a **software portfolio milestone**, not a physical stellar identification, a new companion discovery or an independent instrument calibration.

## What changed since v2.0

- **Package version, CLI and software citation** now identify v2.1.0. The complete original v2.0 manifest and historical release notes are intentionally preserved separately rather than overwritten.
- A **new v2.1 offline evidence auditor** verifies historical v2.0 source counts (532 mirror members, 467 Gaia IDs, 2,212 original IRSA positional-query records, four dated older images, 16 old original source-profile fits with 13 provisional screens and three reviews) independently of later follow-up experiments.
- Authentic **FT Tau six-exposure** follow-up documentation is now linked in the first screen of the README. The six image pairs in late research are **not new distinct physical stars** and are not added to the old counts.
- Six exact original ZTF full native PSFcat and same-date science/mask image checks (all six checksum-reconciled), a χ-blind control audit across 1,095 native source catalogue records (240 with χ below the old 0.5 cutoff), four of six circular-Gaussian numeric fits (two unresolved), and six of six numerically fitted native spatial DAOPhot models (four provisional *same-source pixel* residual screens passed; two r/609 reviews).
- An original, dual-exact-identifier query to the **CDS SIMBAD** mirror maps historical **FT Tau** and Gaia DR3 **149623711269425408** to one uniquely named **V* FT Tau** external catalogue object. SIMBAD alias agreement is real evidence for the **name**, not validation that four separate ZTF ObjectIDs or their original per-exposure detections are physically the same star.
- A new [accessible six-image quantitative SVG](docs/figures/fttau-six-original-native-spatial-psf-quality-v21.svg) plots derived same-source numerical residual QA, with the **different and unchanged** PSFcat native source-quality status labelled independently. This chart does **not** depict real image pixels; the earlier AI-generated astronomy artwork remains explicitly labelled conceptual.
- New [Spanish quick-start](docs/V21_GUIA_ES.md), [ES/EN CV and LinkedIn text](docs/V21_PORTFOLIO_CV_ES_EN.md), [source taxonomy and reproduction protocol](docs/V21_REPRODUCIBILITY_AND_SCIENCE_LIMITS.md), and [visual provenance](docs/V21_VISUAL_EVIDENCE.md).

## Exact scientific limitations

The **three** original FT Tau source quality failures below native χ=0.5 **remain failed**. The original 5/8 provisional quality PASS, 3/8 FAIL and 1/4 two-night accepted pairs do not change. Original ZTF ObjectID lightcurves are not merged. The native spatial DAOPhot fit and field-centre reconstruction compare products from the **same ZTF reduction**, and checkerboard testing splits pixels within the **same image of the same source**: neither constitutes an independently calibrated different-star PSF/WCS error model. No physical Gaia–ZTF source identity, proper motion, physical stellar variability or new companion was confirmed. R2 source identity OPEN and R3 inference BLOCKED.

## Software acceptance and reproducibility

```bash
python -m pip install -e ".[test,analysis,images]"
python -m pytest -q
python scripts/audit_v21_release_manifest.py
python scripts/audit_v2_release_manifest.py # archived v2.0 historic evidence only
stellarforge --version                    # StellarForge 2.1.0
stellarforge plan-gaia --ra 70 --dec 20 --radius-deg 0.1 --max-rows 10
```

No live survey requests are required for this verification; live original-data experiments live in **separate** research GitHub Actions workflows, with derived-only receipts. On the preceding main software baseline, 1,051 automated tests passed in [Actions run 43315134009](https://github.com/ismaelberja/stellarforge/actions/runs/43315134009). The final v2.1 release is approved only after its **merged main commit** passes full GitHub Actions.

## Original data and source traceability

- [v2.0 historical immutable claim manifest](RELEASE_MANIFEST_v2.0.json) and [new v2.1 evidence manifest](RELEASE_MANIFEST_v2.1.json)
- [Six original native spatial DAOPhot PSF fits](research/taurus_variability/R2_REAL_FTTAU_SIX_NATIVE_SPATIAL_DAO_RESULTS.md), [real original-data run 43310945601](https://github.com/ismaelberja/stellarforge/actions/runs/43310945601)
- [Original external CDS SIMBAD/Gaia exact-name audit](research/taurus_variability/R2_REAL_FTTAU_SIMBAD_GAIA_EXACT_ALIAS_RESULTS.md), [original-data run 43314507016](https://github.com/ismaelberja/stellarforge/actions/runs/43314507016)
- [Scientific acceptance checklist](docs/V21_RELEASE_ACCEPTANCE_PLAN.md) and [reproducibility limitations](docs/V21_REPRODUCIBILITY_AND_SCIENCE_LIMITS.md)
- [v2.1 bilingual CV and LinkedIn statements](docs/V21_PORTFOLIO_CV_ES_EN.md)

**Author and scientific direction:** Ismael Berja Ruiz. Scientific-software implementation includes AI coding assistance and reproducible validation; research interpretations must receive independent human evaluation. No proprietary or unpublished ALMA/TFM sources and no original unredacted FITS/catalogue rows are committed in this portfolio.
