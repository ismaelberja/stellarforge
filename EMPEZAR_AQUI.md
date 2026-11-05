# StellarForge — Empezar aquí

**Proyecto científico y de ingeniería de datos en Python** · versión de desarrollo **v1.7** · noviembre de 2026.

StellarForge está pensado para analizar variabilidad estelar con datos de distintos archivos astronómicos. Es un proyecto personal de investigación y software en desarrollo, útil también para demostrar capacidades de ingeniería de datos, análisis temporal y calidad del código.

**Autor y dirección científica:** Ismael Berja Ruiz. El desarrollo incluye apoyo de herramientas de IA; los resultados científicos requieren validación humana.

## ¿Qué está realmente conseguido?

- **400 pruebas automáticas superadas** en GitHub Actions.
- Análisis del catálogo de Taurus: **532 miembros** en una copia pública de la tabla de Luhman (2023), de los que **467 tienen identificador Gaia DR3**. Falta cotejar el archivo con el original del editor.
- Muestra técnica de **24 estrellas** seleccionadas por propiedades del catálogo, **no representativa estadísticamente**.
- Descarga de **2.212 registros fotométricos reales** mediante dos consultas oficiales de IRSA/ZTF cerca de FT Tau y CIDA 11. Son resultados de una búsqueda posicional, **no curvas atribuidas definitivamente a estas estrellas**.
- Procesamiento, filtros de calidad, trazabilidad SHA-256, identificación de distintos OIDs, análisis temporal y simulaciones de validación.
- **Análisis posicional preliminar de los seis identificadores ZTF**: separaciones medianas con Gaia corregidas por movimiento propio de aproximadamente 0,063 a 0,092 segundos de arco; todavía no demuestra identidad estelar.
- **Dos consultas independientes a Gaia DR3**: no aparecen otras fuentes catalogadas dentro de 15″ de FT Tau o CIDA 11, pero no se descartan fuentes ocultas o mezclas. CIDA 11 presenta RUWE elevado (8,57), lo que requiere revisar su solución astrométrica.
- **Análisis real de imágenes FITS de ZTF (v1.5)**: procesadas cinco de seis series por identificador y banda, con comprobaciones WCS y de máximos locales. No se ha realizado aún una validación física de fuentes ni una separación rigurosa de estrellas mezcladas.
- **Ajuste preliminar de perfiles de imágenes (v1.6):** analizadas tres imágenes científicas de FT Tau mediante un modelo gaussiano y un fondo local. Los tres ajustes presentan residuos que deben revisarse. Todavía no hay dos imágenes independientes utilizables de una misma serie para comprobar su estabilidad temporal ni nuevos hallazgos físicos confirmados.
- **Revisión de imágenes y épocas (v1.7):** procesadas doce imágenes FITS científicas reales, dos observaciones diferentes en cada una de las seis series ZTF de FT Tau y CIDA 11. Las diferencias de posición obtenidas son preliminares y no demuestran identidad estelar. La búsqueda de controles en las imágenes de 90″ no encontró suficientes fuentes de comparación válidas para calibrar la PSF; los resultados científicos siguen pendientes de validación.

**No hay nuevas detecciones astrofísicas confirmadas.** Quedan pendientes la revisión de imágenes, las asociaciones Gaia–ZTF y la validación científica de cualquier episodio.

## Cómo comprobar que funciona

Necesitas Python 3.10 o superior y Git.

```bash
git clone https://github.com/ismaelberja/stellarforge.git
cd stellarforge
python -m pip install -e '.[test,analysis]'
python -m pytest -q
```

Puedes explorar los ejemplos locales sin descargar datos:

```bash
stellarforge plan-ztf --ra 65 --dec 25 --radius-arcsec 2 --bands g r
python scripts/run_v11_selection_bias.py
```

Los valores de la primera instrucción son coordenadas de demostración técnica, no una identificación de un objeto de Taurus.

## Dónde encontrar los resultados

- [README principal (inglés)](README.md): presentación resumida para empresas e investigadores.
- [Informe de las doce imágenes y controles de campo v1.7](reports/field_controls_v1.7/REAL_MULTIEPOCH_AND_CONTROL_LIMITS.md).
- [Informe de perfiles gaussianos y repetibilidad v1.6](reports/psf_v1.6/REAL_GAUSSIAN_FIT_REVIEW.md).
- [Informe real de píxeles FITS y WCS v1.5](reports/real_fits_v1.5/PIXEL_WCS_RESULTS.md).
- [Informe de fuentes vecinas e imágenes v1.4](reports/field_review_v1.4/GAIA_NEIGHBOURS_AND_IRSA_IMAGES.md).
- [Informe de posiciones preliminares v1.3](reports/astrometry_v1.3/PROVISIONAL_POSITIONS_REPORT.md).
- [Informe de adquisición v1.2](reports/observational_intake_v1.2/RAW_TRANSPORT_AUDIT.md): datos auténticos y advertencias científicas.
- [Documentación de fuentes y procedencia](docs/DATA_SOURCES.md).
- [Plan de verificación científica](docs/VALIDATION.md).
- [Historial de desarrollo](RESEARCH_HISTORY.md).

Los datos originales descargados no se incluyen en este repositorio. La visibilidad pública de GitHub no equivale a una licencia de reutilización del código ni de los datos.

## Próximo objetivo

El siguiente paso científico será **identificar estrellas de control auténticas** y calibrar el modelo instrumental PSF y las incertidumbres WCS usando las doce imágenes ya obtenidas. También habrá que comprobar la identidad física de las fuentes y el elevado RUWE de CIDA 11. El proyecto puede seguir evolucionando aunque el código esté disponible públicamente.
