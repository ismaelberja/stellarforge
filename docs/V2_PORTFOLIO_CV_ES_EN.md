# StellarForge v2.0 — CV and interview wording (ES/EN)

These descriptions refer to the software project, not to new
astrophysical discoveries. The technical claims below are grounded
in the v2.0 evidence manifest, original ZTF reports and offline CI.

## Versión corta para el CV — Español

**StellarForge | Python, análisis de datos astronómicos y CI/CD**
[GitHub: ismaelberja/stellarforge](https://github.com/ismaelberja/stellarforge)

Desarrollo de una plataforma Python reproducible para procesar datos
de Gaia DR3 y ZTF/IRSA, con controles de calidad de series temporales,
FITS/WCS, modelos PSF y trazabilidad SHA-256. Auditoría de
2.212 registros observacionales obtenidos mediante consultas posicionales,
análisis de 16 ajustes de PSF a imágenes originales y
pruebas automatizadas en GitHub Actions.

## English CV (default version)

**StellarForge | Scientific Python, Data Analytics & CI/CD**
[GitHub: ismaelberja/stellarforge](https://github.com/ismaelberja/stellarforge)

Built a reproducible Python research pipeline for Gaia DR3 and
ZTF/IRSA data, including time-series quality control, FITS/WCS image
checks, PSF modelling, SHA-256 provenance and automated GitHub Actions
testing. Audited 2,212 records from original positional survey
queries and analysed 16 original ZTF masked-image PSF fits,
with clearly documented scientific limitations.

## Version for Data Analyst / Data Science interviews

**ES:** Diseñé un pipeline de tratamiento de datos científicos
que separa la adquisición, limpieza, validación de esquemas,
trazabilidad, extracción de características y pruebas
automatizadas. Implementé controles para no confundir datos
incompletos o fallos HTTP con resultados científicos negativos.
La validación se documenta por niveles: datos observados,
resultados provisionales y ensayos sintéticos.

**EN:** Designed a modular scientific data-processing pipeline
with explicit ingestion, quality gates, reproducible provenance,
feature analysis and automated regression tests. Built controls
that distinguish missing data and failed archive requests from
genuine observational outcomes, keeping real-survey results
separate from synthetic model validation.

## Interview talking points

1. **Problem:** astronomical archives have uncertain source identities,
   inconsistent quality and nonuniform sampling. A successful HTTP request
   does not prove that a light curve belongs to the intended star.
2. **Your contribution:** reproducible ingestion, source/epoch separation,
   original FITS/WCS/PSF checks, defensive tests, CI and
   scientifically honest result qualification.
3. **Hard engineering choice:** preserve ambiguous Gaia/ZTF assignments
   instead of treating nearest-position matches as ground truth; use
   training/held-out **different whole stars** for the new empirical
   PSF design but don't claim that it has already calibrated real ZTF.
4. **Evidence:** 532-source catalogue mirror, 2,212 original
   positional-query records, four historical g-band image exposures,
   16 original masked PSF source fits and a large offline test suite.
5. **Limitation:** no independently confirmed astrophysical source
   variability, companions or final instrument PSF/WCS error budget.
   Being transparent about this is part of scientific integrity.

## Links to supporting evidence

- [v2.0 main repository](https://github.com/ismaelberja/stellarforge)
- [v2.0 claim-by-claim evidence manifest](../RELEASE_MANIFEST_v2.0.json)
- [Original v1.16 masked ZTF source-pixel evidence](../reports/masked_spatial_psf_v1.16/REAL_ZTF_PIXEL_RESIDUALS_EVIDENCE.md)
- [v2.0 reproducibility and scientific limits](V2_REPRODUCIBILITY_AND_SCIENCE_LIMITS.md)

**No profile, job application or LinkedIn post is updated by this
file; the text is provided solely for reuse when desired.**
