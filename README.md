# StellarForge

**Multi-Survey Stellar Variability & Anomaly Detection Platform**  
*Private research software · Astrophysics · Python · Time-series analysis · Scientific data engineering*

## Status — work in progress

This repository is **private**, is **not a scientific publication**, and contains an **initial version-controlled development scaffold**. The **full local StellarForge v1.0 working package** is maintained separately; its older modules, reports and hundreds of tests have **not yet all been imported into this GitHub repository**.

### What is in this repository now

- Initial Python package and conservative g/r color-diagnostic module.
- Independent, explainable time pairing without mixing different source identifiers.
- Explicit uncertainty propagation and guards against crossmatching assumptions.
- Automated GitHub Actions tests for the source currently present.
- Scientific progress tracking, including required evidence before any astrophysical claims.

### Local working package (v1.0)

The private working ZIP retains versions 0.1–0.9 and a new v1.0 research phase. **320 local tests passed.** The v1.0 additions include a two-target ZTF observational intake prototype and color diagnostics. Neither successful download nor confirmed source association is claimed.

### Scientific question

Can multi-survey light curves of young stars in **Taurus**, coupled to careful source matching and calibration controls, help prioritize candidate dimming/brightening events without confusing instrumental artifacts with physical variability?

**Initial catalogue:** Luhman (2023), adopted Taurus members; preliminary technical sample of 24 sources. A secondary copy has been structurally checked, but the original publisher's bytes have not yet been independently compared.

**Pre-registered pilot:** FT Tau and CIDA 11. There are **no independently confirmed Gaia–ZTF crossmatches or physical dipper/burster detections** at present.

### What still needs independent verification

1. Obtain official IRSA ZTF g/r light curves; retain raw bytes and data-release provenance.
2. Verify source identities using per-epoch astrometry, image cutouts and field crowding.
3. Examine same-field comparison stars and cross-band behavior.
4. Quantify detection completeness using injections on actual observational cadences.
5. Expand the target sample with independently sourced disk/accretion classifications.
6. Reproduce the analysis end to end, evaluate uncertainties and publish a technical report.

A successful source-code test does **not** constitute a scientific detection or publication.

**Development:** research direction by Ismael Berja Ruiz, developed iteratively with AI coding assistance and scientific review.
