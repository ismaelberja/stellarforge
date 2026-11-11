# StellarForge v2.0 — Guía final para entender el proyecto

**Versión 2.0.0 · 10 de noviembre de 2026**

StellarForge es un proyecto personal de **Python, análisis de datos
astronómicos e ingeniería de software reproducible**, relacionado con
Gaia DR3 y ZTF. La versión 2.0 se cierra como proyecto técnico
de portfolio, **no como un descubrimiento astronómico**.

## Qué hace

Lee y comprueba catálogos, prepara consultas de Gaia/IRSA,
procesa observaciones de series temporales, examina coordenadas
WCS e imágenes FITS originales y evalúa perfiles PSF. Registra
la procedencia de los datos, rechaza entradas problemáticas y
separa observaciones reales de simulaciones.

**Resultados reales previos:** 2.212 registros de dos consultas
posicionales IRSA; cuatro exposiciones originales ZTF estudiadas;
dieciséis ajustes de PSF a imágenes/máscaras reales, de los que
trece pasan controles provisionales y tres necesitan revisión.
Esto no significa que hayamos identificado inequívocamente
las fuentes ni sus fenómenos físicos.

**Nuevas herramientas empíricas:** se ha desarrollado la
comparación de una PSF hecha con varias estrellas frente a
otras estrellas distintas. La prueba completa con los FITS
originales de CIDA 11 **sigue sin ejecutarse**; las pruebas
nuevas utilizan datos simulados.

## Imágenes en GitHub

La portada del README contiene dos ilustraciones astronómicas
generadas con IA para facilitar la presentación del proyecto.
**No son fotografías de observaciones reales ni perfiles PSF
medidos.** En particular, las estrellas, coordenadas y curvas de
la segunda ilustración son decorativas.

Los **gráficos científicos auténticos**, con cifras trazables a
los informes originales, aparecen por separado en el README:
532 miembros de Taurus (467 con identificador Gaia DR3),
y 16 ajustes de PSF a imágenes ZTF originales (13 controles
provisionales superados, 3 pendientes de revisión).

[Ver las imágenes y sus fuentes](V2_VISUAL_EVIDENCE.md).

## Cómo comprobar el proyecto

Con Python 3.11 y Git instalados:

```powershell
git clone https://github.com/ismaelberja/stellarforge.git
cd stellarforge
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test,analysis,images]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/audit_v2_release_manifest.py
.\.venv\Scripts\stellarforge.exe --help
```

También puedes abrir la página **Actions** de GitHub para
consultar las pruebas automáticas de la versión.

Para comprobar que no se ha modificado el ZIP privado original
de ZTF recuperado en la v1.22:

```powershell
.\.venv\Scripts\python.exe scripts/check_v122_historic_source_zip.py "C:\RUTA\ztf-historic-source-run.zip"
```

El ZIP recuperado **no se sube al repositorio público**.
Hay que sustituir C:\RUTA por la carpeta donde se guardó.

## Qué significa para tu currículum

Puedes presentar StellarForge como un proyecto de
**Python / análisis de datos / automatización / datos científicos**,
destacando trazabilidad, pruebas, trabajo con datos reales
y rigor al diferenciar incertidumbre de resultados comprobados.

No conviene decir que se han descubierto nuevas estrellas,
que se ha confirmado la variabilidad de una fuente concreta
ni que la PSF de ZTF está completamente calibrada: esos
resultados no están demostrados.

Aquí tienes los textos listos para el CV:
[CV y portfolio en español e inglés](V2_PORTFOLIO_CV_ES_EN.md).

## Qué queda después de la versión 2.0

**Para un proyecto de GitHub/CV: ninguna iteración imprescindible.**
Si quieres seguir investigando, el siguiente trabajo científico
es ejecutar el piloto manual v1.20 con los FITS originales y
analizar el número de estrellas realmente aprovechables.
Es una fase de investigación abierta, independiente del
cierre de software v2.0.

Puedes continuar usando el repositorio y mejorarlo en
cualquier momento. No se ha editado tu perfil de LinkedIn.
