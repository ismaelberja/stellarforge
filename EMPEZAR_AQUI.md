# ACTUALIZACIÓN 04/11/2026 — STELLARFORGE v0.9

**Seguimos sin subirlo a GitHub. Esta es una entrega interna y no se ha presentado ningún descubrimiento astronómico.**

- Se han añadido controles de asociación posicional **Gaia–ZTF por cada época observada**, separando todos los identificadores `oid` y bandas fotométricas. Es un control geométrico aproximado, no una identificación independiente confirmada.
- Se han creado **dos expedientes de evidencia**, para **FT Tau** y **CIDA 11**, más un panel HTML autónomo para registrar los requisitos científicos pendientes.
- Se intentaron **dos descargas del archivo oficial IRSA**. Ambas fallaron por un problema de red (`URLError`) del entorno de ejecución. **No se ha obtenido fotometría ZTF oficial de Taurus** ni hay evidencia negativa sobre cobertura observacional.
- Se ha generado una nueva figura de propagación de movimientos propios con parámetros **reales del catálogo**, sin añadir posiciones ZTF inventadas.
- **303 pruebas automáticas pasan**. Se conservan los 239 tests previos y se añaden 64 pruebas nuevas para asociaciones, errores, procedencia e integración.
- Documentación: `docs/PHASE9_PER_EPOCH_ASTROMETRY_AND_EVIDENCE_GATES.md` y `reports/observational_gates_v0.9/`.

**No necesitas hacer nada ahora.** Para dar el siguiente salto científico será imprescindible conseguir las curvas de luz oficiales y revisar manualmente sus asociaciones y posibles contaminaciones.

---

# STELLARFORGE v0.8 — SIGUIENTE FASE ENTREGADA

**Seguimos en investigación privada; no se ha subido nada a GitHub.** No tienes que instalar nada.

Novedades principales:

- **239 pruebas superadas** y ampliación de la compatibilidad con los archivos de ZTF que contienen MJD y HJD a la vez, sin mezclar las escalas temporales.
- **Primer control de compatibilidad con fotometría publicada en un repositorio público**, etiquetada claramente como **muestra secundaria fuera de Taurus**: 8 filas, 6 válidas tras el filtro y 2 descartadas por el indicador `32768`. **No está cotejada directamente con IRSA**, así que no sirve para concluir nada sobre una estrella.
- **Medida geométrica exacta de la cobertura temporal**, con límites explícitos; no confundir con eficiencia de detección fotométrica.
- **Registro de preparación de las 24 fuentes de Taurus**, con prioridad para FT Tau y CIDA 11. No se ha obtenido ninguna curva real verificada de esos dos objetos.

**Lectura recomendada:** `docs/PHASE8_OBSERVATIONAL_EVIDENCE_AND_CADENCE.md`, `reports/observational_format_v0.8/REPORT.md`, `reports/readiness_v0.8/README.md` y `RELEASE_NOTES_v0.8.md`.

El paso más importante que falta sigue siendo descargar respuestas originales de IRSA para las estrellas de Taurus y verificar el emparejamiento astrométrico e instrumental. **No hay descubrimientos científicos confirmados.**

---

# STELLARFORGE v0.6 — NOVEDADES (04/11/2026)

**Seguimos en desarrollo privado y por etapas; este paquete no se ha publicado en GitHub.**

- **Posiciones reales, no fotometría ZTF real:** hemos propagado hasta la época nominal J2021.0 los movimientos propios de 24 estrellas de Taurus de la copia fijada de la Tabla 2 de Luhman (2023). Mediana de desplazamiento angular **0,113 segundos de arco** y máximo **0,145 segundos de arco**. Estas cifras proceden del catálogo y de un cálculo aproximado, no de observaciones nuevas.
- **Cotejo Gaia/ZTF:** nuevo auditor que trata varias contrapartidas OID y filtros por separado; nunca declara una correspondencia confirmada sin revisión adicional de imágenes/astrometría.
- **Control de falsas alarmas:** un detector de episodios debe buscar coincidencia temporal entre bandas y comprobar estrellas de control de campo. Si estas muestran cambios del mismo signo, el evento queda vetado como posible problema instrumental; si faltan controles, queda pendiente.
- **400 ensayos sintéticos nuevos:** la simulación de 50 fallos instrumentales que engañaban al primer detector se descarta por completo tras los controles de campo. Esto NO implica que conozcamos la tasa real de falsos positivos en ZTF.
- **170 pruebas automáticas superadas** en esta versión. Véase `docs/PHASE6_ASTROMETRY_AND_FALSIFICATION.md`.
- **Pendiente:** fotometría real de ZTF (0 curvas importadas), etiquetas independientes de disco, cotejo de la tabla original del editor y validación manual de fuentes.

Archivos recomendados: `README.md`, `reports/v0.6_catalog_astrometry/`, `reports/validation_v0.6/`, `RELEASE_NOTES_v0.6.md`.

---

# ACTUALIZACIÓN 04/11/2026 — STELLARFORGE v0.5

Esta versión añade un gestor de consultas ZTF por lotes (24 posiciones reales de Taurus, **sin descargas ejecutadas**) y un detector experimental de episodios de oscurecimiento/brillo. El proyecto **NO** ha descubierto ni confirmado dippers/bursters: sus pruebas nuevas utilizan señales **sintéticas**. La simulación detecta un problema relevante: errores de calibración coherentes pueden imitar episodios reales; se exigirán cotejo de imágenes, astrometría y filtros antes de una interpretación física.

Consulta `docs/PHASE5_BATCH_AND_EVENTS.md`, `docs/BATCH_RUNBOOK.md` y `RELEASE_NOTES_v0.5.md` para reproducir y entender limitaciones. **StellarForge no se ha subido a GitHub.** No tienes que instalar nada ni preparar datos en este momento.

---

# StellarForge v0.4 — Ya estamos trabajando con posiciones reales de Taurus

Este proyecto sigue **en desarrollo** y no se ha subido al GitHub público del investigador.

## Avance científico más importante

Se ha localizado y revisado una copia pública de la **Tabla 2 de Luhman (2023)**, que recopila miembros de Taurus. En ella se han contado **532 estrellas**, **467 identificadores Gaia DR3 distintos** y **65 miembros sin identificador Gaia**; coincide con las cifras del artículo.

La tabla está en un repositorio público de terceros y no se ha cotejado todavía byte a byte con el archivo del editor. Por tanto, **no decimos que la procedencia definitiva esté cerrada**. Se conserva el enlace a la versión exacta y su identificador de integridad Git.

A partir de esa copia se han seleccionado **24 estrellas reales** de **13 grupos cinemáticos**, utilizando posiciones, magnitudes y movimientos propios publicados. La selección todavía es **técnica y provisional**: no sabemos sus etiquetas independientes de disco Clase II/III ni sus curvas ZTF verificadas. Puedes consultar el CSV en `data/research_seed/` y el mapa real de posiciones en `reports/`.

## Avance de ingeniería y procesamiento

Se ha desarrollado un módulo para estudiar series temporales fotométricas: dispersión y amplitud, análisis de incertidumbres, búsqueda de periodicidad Lomb–Scargle, comprobaciones de alias temporal y exportación auditable. Nunca asigna automáticamente el tipo *dipper*, *burster* ni una detección física definitiva.

**109 pruebas automáticas superadas.** Además, se han realizado **72 simulaciones de recuperación de periodos**, con una señal artificial conocida (24 ensayos por régimen). El programa ha recuperado 24/24 casos de alto contraste, 24/24 casos con huecos estacionales y **15/24 casos de ruido alto y muestreo escaso**. Estos números son puramente de laboratorio y **no representan datos reales de ZTF**.

## Qué NO está hecho

- No hemos descargado fotometría ZTF real en este entorno. Se han generado **24 URLs de consulta**, sin ejecutarlas.
- No hay muestra científica definitiva con discos verificados.
- No tenemos periodos astrofísicos identificados, candidatos confirmados ni un modelo de IA entrenado.
- No hay ningún nuevo repositorio GitHub publicado.

## ¿Tienes que hacer algo?

**No.** Para esta fase no necesitas instalar nada ni subir archivos. Las decisiones sobre muestra científica, física e interpretaciones seguirán contigo, pero la programación y pruebas técnicas se han realizado aquí.

## Documentación principal

- `docs/PHASE4_FIRST_REAL_CATALOG_AND_VARIABILITY.md` — documentación científica de esta versión.
- `docs/SOURCE_ACCESS_STATUS.md` — fuentes y limitaciones de acceso.
- `reports/TAURUS_MIRROR_STRUCTURAL_AUDIT.json` — recuentos del catálogo.
- `reports/TAURUS_24_PRELIMINARY_SKY_POSITIONS.png` — mapa con posiciones reales, selección provisional.
- `examples/SYNTHETIC_v04_benchmark/` — pruebas y gráficos **claramente sintéticos**.
- `README.md` — presentación y guía técnica en inglés.

**Próximo objetivo:** contraste con la tabla del editor y las etiquetas de disco, prueba de las primeras respuestas ZTF auténticas y verificación astrométrica de las asociaciones antes de cualquier interpretación.