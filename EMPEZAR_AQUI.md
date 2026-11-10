# StellarForge v2.0 — Empezar aquí

**Versión 2.0.0 · 10 de noviembre de 2026**

StellarForge es un proyecto personal de **Python, ciencia de datos y
análisis astronómico reproducible**. Investiga procedimientos de
tratamiento de datos de Gaia DR3 y ZTF/IRSA: series temporales,
calidad de observaciones, astrometría, imágenes FITS y modelos PSF.

**Autor y dirección científica:** Ismael Berja Ruiz. El código incluye
asistencia de IA, pruebas automatizadas y criterios científicos
explícitos que requieren validación humana.

## Estado final del proyecto

**Ingeniería de software: versión 2.0 cerrada para GitHub y CV.**

Se han estudiado datos astronómicos reales: un catálogo espejo de
532 miembros de Taurus, dos consultas posicionales con
2.212 registros originales y cuatro imágenes científicas
históricas ZTF. Se completaron 16 ajustes de PSF a imágenes/máscaras
originales; 13 perfiles superaron pruebas *provisionales* de residuos
y 3 siguen pendientes de investigación.

**No hemos confirmado nuevas estrellas, compañeros, variaciones físicas
de brillo ni una calibración PSF/WCS instrumental independiente.**
La técnica nueva que utiliza estrellas completamente distintas
para entrenamiento y validación tiene pruebas de software
simuladas, pero aún no una ejecución real autenticada del piloto
de CIDA 11.

Para consultar el alcance exacto de cada resultado:
[Informe de evidencia v2.0](RELEASE_MANIFEST_v2.0.json) y
[documento científico detallado](docs/V2_REPRODUCIBILITY_AND_SCIENCE_LIMITS.md).

## Probar StellarForge

Requiere Python 3.10 o posterior (se recomienda Python 3.11).

En Linux o macOS:

\`\`\`bash
git clone https://github.com/ismaelberja/stellarforge.git
cd stellarforge
python -m pip install -e ".[test,analysis,images]"
python -m pytest -q
python scripts/audit_v2_release_manifest.py
stellarforge --help
\`\`\`

En Windows (PowerShell):

\`\`\`powershell
git clone https://github.com/ismaelberja/stellarforge.git
cd stellarforge
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test,analysis,images]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/audit_v2_release_manifest.py
\`\`\`

La suite automática es local y **no realiza consultas externas**.
Puedes ver su estado actualizado en [GitHub Actions](https://github.com/ismaelberja/stellarforge/actions/workflows/tests.yml).

## Para el currículum y las entrevistas

Aquí están las descripciones cortas listas para usar:
[Textos en español e inglés](docs/V2_PORTFOLIO_CV_ES_EN.md).
No se ha modificado LinkedIn.

## Si quieres continuar la investigación real

El siguiente experimento científico sería ejecutar
[manualmente el piloto v1.20](.github/workflows/v120-original-empirical-psf-pilot.yml)
para comprobar la PSF propia sobre diferentes estrellas
del mismo fotograma original ZTF de CIDA 11.

El ZIP de las consultas posicionales originales se recuperó
antes de caducar su artefacto de GitHub y debe conservarse
**en privado**, no dentro del repositorio. El programa
de comprobación de integridad se describe en
[la guía de reproducibilidad](docs/V2_REPRODUCIBILITY_AND_SCIENCE_LIMITS.md).

**Para el portfolio ya no queda ninguna iteración obligatoria.**
Para una publicación científica, la validación astrofísica
sigue abierta, sin un número prefijado de iteraciones.

Documentación histórica original completa:
[Guía anterior v1.22](docs/HISTORIC_EMPEZAR_AQUI_v1.22.md).
