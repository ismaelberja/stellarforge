# StellarForge v1.21 — Auditoría científica y preparación de la v2.0

**Estado: pruebas nuevas de software superadas; nuevos ajustes astronómicos reales aún pendientes.**

La fase v1.21 comprueba cómo cambia nuestra PSF empírica cuando
quitamos una estrella del entrenamiento y cómo responde si añadimos
artificialmente una fuente cercana a una imagen de prueba. Estas
comprobaciones nos ayudan a detectar modelos poco robustos; **no son
detecciones de objetos reales**.

También hemos incorporado reglas automáticas para impedir que un informe
anuncie una PSF de estrellas independientes si no ha utilizado al menos
tres estrellas de entrenamiento y dos de validación de una sola exposición.

Los tres casos de residuos elevados que aparecieron en FT Tau y CIDA 11
en la v1.16 continúan sin identificar. Pueden deberse a errores
instrumentales, vecinos, fondo irregular u otras causas; no podemos
atribuirlos a compañeros ni variabilidad física.

## Paso urgente: aprovechar el archivo ZTF

GitHub confirma que el artefacto original de adquisición caduca el
**12 de noviembre de 2026 a las 09:47 (hora española peninsular)**.

En [Actions, flujo v1.20](https://github.com/ismaelberja/stellarforge/actions/workflows/v120-original-empirical-psf-pilot.yml),
elige la rama **main** y pulsa **Run workflow** manteniendo el
identificador **41997079598**. El flujo es intencionadamente manual.
Todavía no se ha ejecutado desde la v1.20.

Si conseguimos suficientes estrellas con imagen y máscara válida,
obtendremos nuevos resultados empíricos sobre píxeles originales.
Si no, documentaremos la limitación sin inventar detecciones.

La v2.0 puede ser un excelente cierre de software científico incluso
cuando la calibración independiente o una publicación astronómica
sigan necesitando investigación adicional.
