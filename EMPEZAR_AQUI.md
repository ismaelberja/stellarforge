# StellarForge — Empezar aquí

**Proyecto científico y de ingeniería de datos en Python** · versión de desarrollo **v1.12** · noviembre de 2026.

StellarForge está pensado para analizar variabilidad estelar con datos de distintos archivos astronómicos. Es un proyecto personal de investigación y software en desarrollo, útil también para demostrar capacidades de ingeniería de datos, análisis temporal y calidad del código.

**Autor y dirección científica:** Ismael Berja Ruiz. El desarrollo incluye apoyo de herramientas de IA; los resultados científicos requieren validación humana.

## ¿Qué está realmente conseguido?

- **506 pruebas automáticas superadas** en GitHub Actions.
- Análisis del catálogo de Taurus: **532 miembros** en una copia pública de la tabla de Luhman (2023), de los que **467 tienen identificador Gaia DR3**. Falta cotejar el archivo con el original del editor.
- Muestra técnica de **24 estrellas** seleccionadas por propiedades del catálogo, **no representativa estadísticamente**.
- Descarga de **2.212 registros fotométricos reales** mediante dos consultas oficiales de IRSA/ZTF cerca de FT Tau y CIDA 11. Son resultados de una búsqueda posicional, **no curvas atribuidas definitivamente a estas estrellas**.
- Procesamiento, filtros de calidad, trazabilidad SHA-256, identificación de distintos OIDs, análisis temporal y simulaciones de validación.
- **Análisis posicional preliminar de los seis identificadores ZTF**: separaciones medianas con Gaia corregidas por movimiento propio de aproximadamente 0,063 a 0,092 segundos de arco; todavía no demuestra identidad estelar.
- **Dos consultas independientes a Gaia DR3**: no aparecen otras fuentes catalogadas dentro de 15″ de FT Tau o CIDA 11, pero no se descartan fuentes ocultas o mezclas. CIDA 11 presenta RUWE elevado (8,57), lo que requiere revisar su solución astrométrica.
- **Análisis real de imágenes FITS de ZTF (v1.5)**: procesadas cinco de seis series por identificador y banda, con comprobaciones WCS y de máximos locales. No se ha realizado aún una validación física de fuentes ni una separación rigurosa de estrellas mezcladas.
- **Ajuste preliminar de perfiles de imágenes (v1.6):** analizadas tres imágenes científicas de FT Tau mediante un modelo gaussiano y un fondo local. Los tres ajustes presentan residuos que deben revisarse. Todavía no hay dos imágenes independientes utilizables de una misma serie para comprobar su estabilidad temporal ni nuevos hallazgos físicos confirmados.
- **Revisión de imágenes y épocas (v1.7):** procesadas doce imágenes FITS científicas reales, dos observaciones diferentes en cada una de las seis series ZTF de FT Tau y CIDA 11. Las diferencias de posición obtenidas son preliminares y no demuestran identidad estelar. La búsqueda de controles en las imágenes de 90″ no encontró suficientes fuentes de comparación válidas para calibrar la PSF; los resultados científicos siguen pendientes de validación.

- **Comprobación de referencias Gaia en imágenes ZTF (v1.8):** dos consultas amplias a Gaia DR3 han permitido seleccionar ocho posibles fuentes de control (tres cerca de FT Tau y cinco cerca de CIDA 11). Se han realizado trece ajustes válidos de imagen de referencia, con tres estimaciones preliminares del desplazamiento local WCS. Todavía no equivalen a calibración astrométrica independiente ni validación de estrellas aisladas.

- **Astrometría formal Gaia y paralaje anual (v1.9):** recogidos todos los errores y correlaciones de los cinco parámetros astrométricos de FT Tau y CIDA 11, y calculada la corrección de paralaje con la posición terrestre para cuatro fechas reales. Los desplazamientos anuales son de unos pocos milisegundos de arco, pero las incertidumbres calculadas son **solo las formales de Gaia**, sin errores de ZTF. El elevado RUWE de CIDA 11 sigue impidiendo interpretar su posición como una solución simple y plenamente fiable.

- **Validación cruzada de referencias en imágenes reales (v1.10):** reanalizados 13 ajustes derivados de imágenes ZTF, con dos criterios de calidad y una prueba que excluye cada estrella de referencia por turnos. Tres de cuatro exposiciones admiten la revisión con todos los ajustes, pero solo dos con referencias de mejor calidad. Los desacuerdos internos (~0,076″ en FT Tau y ~0,093″ en una imagen de CIDA 11) **no** equivalen a errores astrométricos instrumentales calibrados.

- **Paralaje e incertidumbre formal de cada estrella de referencia (v1.11):** consultadas diez fuentes Gaia DR3 (ocho referencias y dos objetivos) y recalculados 13 ajustes derivados de imágenes ZTF reales. Las correcciones de paralaje cambian muy poco el desacuerdo entre referencias, apenas 0,012 mas en FT Tau y 0,075 mas en CIDA 11; dos de cuatro exposiciones siguen superando el control de calidad estricto. No es una calibración instrumental de WCS ni una detección nueva.

- **Reanálisis de píxeles FITS reales (v1.12):** sobre las imágenes originales de ZTF se han comparado dos métodos distintos para localizar el centro de las fuentes: un ajuste gaussiano y un centroide de apertura con corrección del fondo. Se hicieron dos comprobaciones de 20 solicitudes sobre **las mismas imágenes históricas** (no son cuarenta exposiciones independientes). La primera obtuvo 9 ajustes completos y 9 errores HTTP 503; la ejecución definitiva obtuvo **12 ajustes completos** (un objetivo y once referencias), con 8 errores HTTP 503. Nueve posibles referencias mostraron concordancia provisional entre modelos, con separación mediana de **0,105″** entre ambos métodos: **es sensibilidad al método, no precisión astrométrica calibrada**. Solo una exposición tuvo referencias suficientes: en CIDA 11, el desacuerdo interno de las cuatro referencias fue **0,065″** con gaussiana y **0,156″** por apertura; la imagen del objetivo no estuvo disponible en esa segunda ejecución. Quedan pendientes los mapas oficiales de máscaras y la PSF instrumental de ZTF.

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
- [Resultados de píxeles FITS y comparación de centroides v1.12](reports/real_fits_v1.12/REAL_TWO_CENTROID_MODEL_QA.md).
- [Correcciones Gaia por paralaje de las referencias v1.11](reports/reference_parallax_v1.11/REAL_GAIA_REFERENCE_PARALLAX_LOO.md).
- [Validación cruzada real de referencias v1.10](reports/holdout_v1.10/REAL_REFERENCE_HOLDOUT_EVIDENCE.md).
- [Informe de paralaje anual e incertidumbre astrométrica v1.9](reports/gaia_formal_v1.9/GAIA_COVARIANCE_AND_ANNUAL_PARALLAX.md).
- [Auditoría Gaia y referencias de imagen v1.8](reports/gaia_reference_v1.8/REAL_REFERENCE_CANDIDATE_EVIDENCE.md).
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

El siguiente paso científico será **descargar y analizar las máscaras de píxeles y los modelos oficiales de PSF de ZTF** de las mismas exposiciones, para identificar saturación, píxeles defectuosos, mezclas y efectos instrumentales. Después habrá que construir una calibración WCS con suficientes referencias de campo realmente verificadas y estimar las incertidumbres sin confundirlas con la concordancia entre dos métodos sobre la misma imagen. Después habrá que validar la identidad de las fuentes y estudiar el elevado RUWE de CIDA 11. El proyecto puede seguir evolucionando aunque el código esté disponible públicamente.
