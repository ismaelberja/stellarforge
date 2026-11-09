# StellarForge — Empezar aquí

**Proyecto científico y de ingeniería de datos en Python** · versión de desarrollo **v1.18** · noviembre de 2026.

StellarForge está pensado para analizar variabilidad estelar con datos de distintos archivos astronómicos. Es un proyecto personal de investigación y software en desarrollo, útil también para demostrar capacidades de ingeniería de datos, análisis temporal y calidad del código.

**Autor y dirección científica:** Ismael Berja Ruiz. El desarrollo incluye apoyo de herramientas de IA; los resultados científicos requieren validación humana.

## ¿Qué está realmente conseguido?

- **661 pruebas automáticas superadas** en GitHub Actions.
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

- **Máscaras de píxeles y PSF oficial de ZTF (v1.13):** por primera vez se han descargado y cotejado los mapas reales `mskimg.fits` con las imágenes científicas originales, comprobando que la geometría WCS coincide antes de interpretar los píxeles. De 20 posiciones de fuentes objetivo/referencia, cuatro referencias tenían máscara e imagen accesibles y alineadas, sin bits problemáticos ni saturación en la apertura examinada. Las otras dieciséis fallaron por HTTP 503, incluidos los dos objetivos. En una segunda ejecución se pudieron abrir los otros dos modelos oficiales de PSF del **centro del campo**, de modo que **ya disponemos de los cuatro productos originales** (23×23 píxeles cada uno) correspondientes a las cuatro exposiciones históricas. La segunda ejecución tuvo HTTP 503 en todas las máscaras; seguimos teniendo cuatro máscaras válidas solo de la primera. **No son PSF específicas de cada estrella ni permiten confirmar ausencia de mezclas, identidad estelar o calibración astrométrica.**

- **Catálogos originales de ajustes PSF de ZTF (v1.14):** descargados y analizados los **cuatro catálogos oficiales `psfcat.fits`** de nuestras cuatro exposiciones originales. Contienen **27.207 detecciones instrumentales**. Se han comparado **20 posiciones previstas por Gaia** con las posiciones, banderas y calidad del ajuste PSF de ZTF: **16 candidatas superan los controles provisionales** (tres posiciones de los objetivos y trece de referencias), otras tres requieren revisar la calidad de `chi`, y una no aparece en el catálogo dentro del radio de búsqueda. Las separaciones de las 16 candidatas van de **0,033″ a 0,345″**, mediana **0,126″**; **no son precisiones astrométricas calibradas ni identificaciones físicas confirmadas**. También se han recuperado los **cuatro archivos de PSF espacial `sciimgdao.psf`**, pero aún no se han descodificado ni evaluado en la posición de cada estrella.

- **Reconstrucción espacial real de la PSF ZTF (v1.15):** descodificados los **cuatro archivos oficiales `sciimgdao.psf`** de las exposiciones estudiadas. Cada uno contiene una base gaussiana y **tres tablas de corrección espacial de 47×47 muestras**. Nuestro algoritmo calcula un modelo PSF de **23×23 píxeles** en las coordenadas originales del detector, y sus reconstrucciones en el centro coinciden muy bien con las **cuatro imágenes PSF oficiales de ZTF** (similitud de forma ≥0,999999). Se han evaluado modelos de PSF locales para las **16 fuentes candidatas** aceptadas provisionalmente en la v1.14. **Esto demuestra consistencia en el formato y la reconstrucción; no verifica todavía que esos modelos ajusten bien las estrellas reales, que estén aisladas o que Gaia/ZTF correspondan físicamente a la misma fuente.** Faltan los residuos sobre imágenes científicas originales con máscaras válidas y una calibración WCS independiente.

- **Ajustes PSF sobre píxeles científicos originales de ZTF (v1.16):** hemos pasado de reconstruir únicamente las PSF de ZTF a **ajustarlas directamente a las imágenes reales `sciimg.fits`, usando las máscaras de píxeles `mskimg.fits` correspondientes**. Se recuperaron los **16 pares originales de imagen y máscara**, se comprobó su geometría WCS y la fase subpíxel del detector, y se ajustó la amplitud de la PSF espacial con un plano de fondo en unidades DN. **Los 16 ajustes se completaron**; **13 superan una comprobación provisional de residuos** y **3 necesitan revisión** (un objetivo FT Tau, un objetivo CIDA 11 y una posible estrella de referencia). La comparación se realiza dejando fuera algunos píxeles de la **misma imagen**, no estrellas independientes. **No demuestra que las asociaciones Gaia–ZTF sean físicamente correctas, que las estrellas estén aisladas ni que los residuos indiquen un compañero o variabilidad.** Falta una calibración WCS/PSF con estrellas externas realmente independientes.

- **Nuevas estrellas de control Gaia no utilizadas antes (v1.17):** consultamos de nuevo Gaia DR3 en los campos de FT Tau y CIDA 11 y excluimos expresamente los **10 identificadores de fuentes Gaia** que usábamos hasta la versión anterior. **FT Tau no ofreció ninguna nueva candidata** que superase simultáneamente los filtros estrictos de calidad, brillo y aislamiento, mientras que en **CIDA 11 seleccionamos cuatro fuentes nuevas**, distribuidas por cuatro zonas del campo, **sin mirar previamente sus residuos en ZTF**. En las dos exposiciones originales de CIDA 11, **seis de ocho combinaciones fuente/fecha se pudieron ajustar a imágenes y máscaras científicas reales**, y las seis superaron el control provisional de residuos dentro de la misma imagen; otras dos no superaron el filtro del catálogo ZTF y no se ajustaron. En **32 posiciones desplazadas artificialmente 25″** no apareció ninguna coincidencia en el catálogo PSF dentro del radio de 1″. **Esto no es una tasa de falsas asociaciones ni una calibración instrumental independiente:** no sabemos si estas cuatro estrellas formaban parte del entrenamiento de la PSF original de ZTF. Es una extensión verificable a fuentes diferentes de nuestra muestra inicial, con resultados limitados a CIDA 11.

- **Registros originales de construcción de la PSF y controles de FT Tau (v1.18):** hemos recuperado los **ocho archivos oficiales de procesamiento `sciimlog.txt` y `log.txt`** de las cuatro exposiciones ZTF anteriores. Contienen referencias al cálculo de la PSF, **pero no permiten certificar qué fuentes exactas se utilizaron para entrenarla**. La calidad estricta de referencias Gaia sigue dejando **cero fuentes nuevas elegibles en FT Tau**. En un nivel de exploración separado, con límites de brillo, RUWE, aislamiento y distancia declarados antes de ver las imágenes, han aparecido **cuatro candidatas nuevas**. Solo **una fuente Gaia** ha permitido **dos ajustes** a las imágenes científicas y máscaras originales, uno por fecha, con dos controles provisionales de residuos superados (RMS/ruido MAD **0,920 y 0,955**); las otras seis combinaciones de fuente/fecha no superaron los filtros previos ZTF. También se probaron 32 posiciones desplazadas ±25″ sin coincidencias, lo que **no es una tasa de falsas asociaciones calibrada**. El nuevo nivel exploratorio es menos estricto y **no demuestra estrellas físicamente aisladas ni ajenas al entrenamiento instrumental original**.

**No hay nuevas detecciones astrofísicas confirmadas.** Quedan pendientes la revisión de imágenes, las asociaciones Gaia–ZTF y la validación científica de cualquier episodio.

## Cómo comprobar que funciona

Necesitas Python 3.10 o superior y Git.

```bash
git clone https://github.com/ismaelberja/stellarforge.git
cd stellarforge
python -m pip install -e '.[test,analysis,images]'
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
- [Registros originales de entrenamiento PSF y controles exploratorios de FT Tau v1.18](reports/psf_training_ft_tau_v1.18/REAL_ZTF_LOG_AUDIT_AND_EXPLORATORY_FT_TAU.md).
- [Nuevas referencias Gaia y controles de posiciones desplazadas v1.17](reports/new_gaia_holdouts_v1.17/REAL_DISJOINT_GAIA_CONTROL_AND_SHIFTED_SKY_RESULTS.md).
- [Residuos reales sobre píxeles de ZTF con PSF espacial y máscaras v1.16](reports/masked_spatial_psf_v1.16/REAL_ZTF_PIXEL_RESIDUALS_EVIDENCE.md).
- [Reconstrucción espacial DAOPhot y contraste real de PSF ZTF v1.15](reports/spatial_daophot_v1.15/REAL_DAOPHOT_CENTER_AND_LOCAL_SHAPES.md).
- [Catálogos originales PSF y asociaciones candidatas Gaia–ZTF v1.14](reports/native_psfcat_v1.14/REAL_ZTF_GAIA_PSF_CATALOGUE_EVIDENCE.md).
- [Máscaras de ZTF y PSF nativa real v1.13](reports/original_masks_psf_v1.13/REAL_ZTF_MASK_AND_NATIVE_CENTER_PSF_EVIDENCE.md).
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

El siguiente paso científico será **obtener una lista documentada de estrellas utilizadas por la PSF original de ZTF o crear una PSF independiente con referencias estelares verificadas y reservadas para su validación**. La auditoría de los ocho registros de procesamiento confirma que los datos disponibles no permiten demostrar qué fuentes pertenecían al entrenamiento. En FT Tau solo una fuente adicional del nivel exploratorio ha dado dos ajustes de imagen útiles, de modo que todavía faltan suficientes controles independientes, más fechas y bandas, y un modelo realista de errores CCD y WCS. Tendremos que estudiar también fondo nebular, mezclas y el posible origen instrumental de los tres casos con residuos altos. Revisaremos también las tres fuentes con residuos elevados antes de plantear ninguna interpretación astrofísica. Los catálogos nativos ya están recuperados, pero todavía no demuestran identidad física, ausencia de mezclas ni errores astrométricos calibrados. Después habrá que validar la identidad de las fuentes y estudiar el elevado RUWE de CIDA 11. El proyecto puede seguir evolucionando aunque el código esté disponible públicamente.
