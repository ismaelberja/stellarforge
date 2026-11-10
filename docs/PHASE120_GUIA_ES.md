# StellarForge v1.20 — Guía en español

**Estado: código y pruebas verificadas; ejecución astronómica real pendiente.**

## ¿Qué hemos mejorado?

Hasta la v1.19 podíamos construir una PSF empírica con estrellas distintas,
pero solo lo habíamos probado con ejemplos sintéticos.

En la v1.20 añadimos una vía para trabajar con las **imágenes originales
de ZTF de CIDA 11**, sin inventar estrellas ni modificar los filtros después
de ver los resultados.

1. Consultamos Gaia DR3 y seleccionamos de manera estricta siete
   estrellas candidatas: **cuatro para construir** la nueva PSF y
   **tres diferentes para comprobarla**. La asignación se decide
   *antes* de examinar las imágenes de ZTF.
2. Comprobamos su posible correspondencia en el catálogo instrumental
   original y rechazamos fuentes con problemas de calidad o confusión.
3. Descargamos, cuando están disponibles, las imágenes FITS y sus
   máscaras oficiales correspondientes a **la misma exposición**.
4. Comprobamos WCS, centrado, saturación y píxeles defectuosos y
   construimos una estampa estelar común de 23 × 23 píxeles.
5. **Solo si hay al menos tres estrellas de entrenamiento y dos de
   validación válidas**, se ejecuta el modelo empírico de la v1.19.
   No se sustituyen estrellas rechazadas por otras después de ver
   sus residuos.

Las pruebas automáticas utilizan datos sintéticos y verifican también
que el programa se niega a realizar afirmaciones científicas cuando
la información disponible no es suficiente.

## Limitaciones

La PSF empírica propia no utiliza los coeficientes DAOPhot originales,
pero seguimos sin saber qué estrellas utilizó ZTF para construir su
modelo oficial. Tampoco están confirmadas la identidad física Gaia–ZTF,
la precisión absoluta WCS ni las incertidumbres de CCD completas.
El remuestreo de píxeles genera correlaciones que requieren estudiar
el ruido instrumental con más información.

Los tres perfiles de residuos elevados de la v1.16 continúan pendientes
de revisión. **No hay nuevos descubrimientos astronómicos confirmados.**

## Cómo ejecutar la prueba con datos reales

En GitHub, entra en **Actions** y selecciona el flujo
**"v1.20 Real CIDA 11 strict 4+3 empirical PSF original ZTF pilot (NO RAW)"**.
Usa **Run workflow** con la rama "main" y el identificador original
de adquisición por defecto, si el artefacto original sigue disponible.

Este flujo debe ejecutarse **manualmente**. Si los archivos de archivo
ya no están disponibles o algunas imágenes fallan, el programa lo
registrará como limitación de datos, **no como ausencia de estrellas**.
El informe del propio flujo y su artefacto temporal solo contienen
estadísticas agregadas y huellas SHA-256, nunca los FITS originales.

Código y metodología: docs/PHASE120_ORIGINAL_REGISTERED_STAR_COHORT.md
