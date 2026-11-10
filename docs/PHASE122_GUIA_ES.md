# StellarForge v1.22 — Archivo ZTF recuperado y plan hacia v2.0

**Fecha: 10 de noviembre de 2026**

Hemos recuperado la copia exacta del ZIP original que se utilizó
en la primera adquisición de curvas de luz de ZTF. Ocupa **181.170 bytes**
y su SHA-256 coincide con el publicado por GitHub Actions. No es
una nueva observación astronómica: son las dos respuestas originales
a búsquedas posicionales de FT Tau y CIDA 11.

**Importante:** descarga el ZIP privado facilitado en ChatGPT y
guárdalo en tu ordenador o almacenamiento privado. **No lo subas
a un commit ni lo incluyas en el repositorio público.**

## Qué añade esta fase

Hemos creado un programa que comprueba que el ZIP no se ha modificado
y que sus archivos coinciden con el manifiesto original.

También hemos hecho dos ensayos completos sin conexión externa sobre
el flujo de la v1.20:

- Prueba con suficientes estrellas sintéticas: cuatro de
  entrenamiento y tres de validación, dos exposiciones.
- Prueba con estrellas rechazadas por la máscara: el programa
  se detiene y no rellena automáticamente las que faltan.

Esto demuestra que el código coordina el procedimiento, **no
que hayamos calibrado todavía la PSF instrumental real de ZTF**.

## Opción A: ejecutar GitHub Actions antes de caducar

Abre el [flujo v1.20 de GitHub](https://github.com/ismaelberja/stellarforge/actions/workflows/v120-original-empirical-psf-pilot.yml).
Pulsa **Run workflow**, elige `main` y conserva
el identificador de origen **41997079598**.
El artefacto del que descarga los datos caduca el
**12/11/2026 a las 09:47:05 (hora peninsular española)**.

No se ha lanzado ese flujo en esta fase porque la conexión disponible
no proporciona la acción para ejecutarlo directamente.

## Opción B: ejecución local en Windows con el ZIP recuperado

Con Python 3.11 instalado, en PowerShell:

```powershell
git clone https://github.com/ismaelberja/stellarforge.git
cd stellarforge
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test,analysis,images]"
.\.venv\Scripts\python.exe scripts/check_v122_historic_source_zip.py "C:\RUTA\ztf-historic-source-run.zip"
.\.venv\Scripts\python.exe scripts/run_v120_original_empirical_psf_pilot.py "C:\RUTA\ztf-historic-source-run.zip" --output reports/generated/v1.22_original_cohort
```

Sustituye `C:RUTA` por la ruta donde hayas guardado el ZIP.
La segunda ejecución seguirá necesitando conexión a los servidores
de Gaia e IRSA para descargar imágenes y máscaras originales.

Los resultados reales serán válidos **solo** si los informes
indican cuántas estrellas distintas superan todos los filtros,
sus errores y los motivos de rechazo. Un ajuste de PSF empírica
no demuestra por sí solo identificación física ni precisión
instrumental calibrada.

## ¿Cuántas iteraciones faltan?

**Una fase de cierre v2.0**, si podemos registrar el resultado
real del piloto o documentar claramente que no hay suficientes
datos disponibles y realizar la auditoría final del portfolio.

**Dos**, si durante ese intento aparecen problemas técnicos
que necesitan corregirse antes de cerrar. Un descubrimiento
astrofísico no se puede garantizar con un número fijo de fases.

LinkedIn continúa sin cambios.
