# StellarForge v2.1 — CV, LinkedIn and interview-ready text (ES / EN)

**Project:** [StellarForge (GitHub)](https://github.com/ismaelberja/stellarforge)  
**Discipline:** Scientific Python · Data Analysis · Data Engineering · Astrophysics · Reproducible Research  
**Author / scientific direction:** Ismael Berja Ruiz

These descriptions describe an actual **research-software engineering project**, NOT a scientifically verified discovery. The v2.1 manifest and linked original ZTF and CDS data reports support the specific technical claims.

## Español — CV (breve, orientado a Data Analyst / Data Scientist)

**StellarForge | Python científico, análisis de datos y automatización**

Desarrollo de un pipeline de análisis astronómico reproducible con datos de Gaia DR3 y ZTF/IRSA. Implementación de controles de calidad, trazabilidad SHA-256, procesamiento de imágenes FITS/WCS y máscaras, reconstrucción de modelos PSF, validación de resultados y pruebas automatizadas con GitHub Actions. Integración de auditorías sobre observaciones reales y documentación explícita de las incertidumbres científicas. [Repositorio](https://github.com/ismaelberja/stellarforge).

## English — CV (recommended default)

**StellarForge | Scientific Python, Data Analysis & CI/CD**

Developed a reproducible Python pipeline for Gaia DR3 and ZTF/IRSA astronomical data, with provenance-aware ingestion, quality control, original FITS/WCS and image-mask checks, spatial PSF modelling, derived-only scientific evidence, automated regression tests and GitHub Actions. Conducted original-data instrumental QA and carefully separated verified software outcomes from unresolved astrophysical source identification. [GitHub](https://github.com/ismaelberja/stellarforge).

## Español — descripción de proyecto para LinkedIn

StellarForge es mi proyecto personal de desarrollo de software científico y análisis de datos astronómicos. He diseñado un pipeline modular en Python para trabajar con catálogos y observaciones reales de Gaia DR3 y ZTF/IRSA, incluyendo validación de datos, trazabilidad, análisis temporal, imágenes FITS, coordenadas WCS, máscaras y modelos PSF.

En el estudio de FT Tau comprobé seis exposiciones originales de ZTF con sus productos instrumentales y obtuve seis ajustes numéricos con modelos PSF espaciales; cuatro superaron controles internos provisionales y dos siguen pendientes de revisión. También contrasté mediante consultas exactas a SIMBAD la equivalencia entre el nombre histórico FT Tau y su identificador Gaia DR3. El proyecto dispone de pruebas automáticas en GitHub Actions y documentación reproducible.

**Alcance:** se trata de un proyecto de software y metodología científica. No afirmo haber descubierto nuevas estrellas, variabilidad o compañeras, ni haber demostrado una asociación física Gaia–ZTF.

Repositorio: https://github.com/ismaelberja/stellarforge

## English — LinkedIn project description

StellarForge is my independent scientific-software and data-analysis project. I built a modular Python research workflow for Gaia DR3 and ZTF/IRSA catalogues, observation quality gates, time-series diagnostics, original FITS/WCS images and masks, spatial DAOPhot PSF modelling, SHA-256 provenance and GitHub Actions regression testing.

As part of the FT Tau research case study, I audited six previously selected original ZTF exposures and applied their native spatial PSF models. All six produced numerical source-image fits; four passed provisional same-image residual checks and two were flagged for review. Exact CDS SIMBAD identifier queries also verified the curated name-level association between FT Tau and its Gaia DR3 identifier.

This is a reproducible research-software portfolio, not an independently confirmed stellar variability or companion discovery.

Project: https://github.com/ismaelberja/stellarforge

## Cómo explicarlo en una entrevista

**Problema:** los datos científicos no llegan perfectamente etiquetados; una asociación por cercanía o una consulta HTTP correcta no garantiza que se trate de la fuente física que creemos. La calidad depende de las máscaras, el ruido instrumental, la selección y las fechas.

**Mi solución:** arquitectura por módulos, filtros explícitos, modelos PSF, auditorías SHA-256, pruebas que fallan ante datos contradictorios y separación entre observación real, ensayo sintético y ciencia todavía no validada.

**Evidencia:** catálogo espejo de 532 fuentes; 2.212 registros de consultas posicionales originales; 16 perfiles históricos y un estudio posterior de seis imágenes FT Tau reales; seis modelos espaciales PSF con cuatro controles internos provisionales superados; identificación de nombre FT Tau ↔ Gaia en SIMBAD. **Estos conjuntos de observaciones no deben sumarse como estrellas únicas**.

**Límite:** SIMBAD confirma el alias histórico, no que todos los ZTF ObjectIDs representen físicamente la estrella Gaia. Los experimentos PSF reutilizan el pipeline instrumental ZTF; no calibran de forma independiente la incertidumbre completa.

## Fuentes para comprobar las afirmaciones

- [Manifiesto v2.1](../RELEASE_MANIFEST_v2.1.json)
- [Análisis con PSF espaciales originales](../research/taurus_variability/R2_REAL_FTTAU_SIX_NATIVE_SPATIAL_DAO_RESULTS.md)
- [Equivalencia exacta FT Tau ↔ Gaia en SIMBAD](../research/taurus_variability/R2_REAL_FTTAU_SIMBAD_GAIA_EXACT_ALIAS_RESULTS.md)
- [Resultados históricos de PSF v1.16](../reports/masked_spatial_psf_v1.16/REAL_ZTF_PIXEL_RESIDUALS_EVIDENCE.md)
- [Documentación de limitaciones y pruebas](V21_REPRODUCIBILITY_AND_SCIENCE_LIMITS.md)

**No se ha publicado ni modificado automáticamente ningún perfil personal de LinkedIn, CV o solicitud laboral.** Los textos son propuestas para revisión.
