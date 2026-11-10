# StellarForge v1.19 — Guía breve en español

**Estado:** herramienta científica implementada; comprobaciones
sintéticas automatizadas. **Todavía no es una validación independiente
de observaciones originales de ZTF.**

## ¿Qué mejora?

La v1.18 mostró que los registros de ZTF no permiten conocer con
certeza qué estrellas se utilizaron para entrenar su PSF original.
Por eso no podemos llamar «independientes» a las nuevas estrellas
simplemente porque tengan identificadores Gaia distintos.

La v1.19 incorpora:

1. **PSF empírica propia:** construye un modelo a partir de las imágenes
   de al menos tres estrellas de entrenamiento.
2. **Validación con estrellas diferentes:** exige al menos otras dos
   estrellas distintas, de la **misma exposición**, que no participan en
   el entrenamiento. Rechaza duplicados y mezclas de exposiciones.
3. **Máscaras oficiales:** descarta estampas con píxeles centrales
   saturados o defectuosos y exige un alineamiento previo muy preciso.
4. **Ruido del detector:** calcula la componente diagonal aproximada
   de ruido de fotones y lectura, expresada en DN²; añade una estimación
   exploratoria de correlación de ruido usando regiones independientes
   de cielo vacío.

El código no utiliza la PSF oficial de ZTF para entrenar el modelo
empírico. **Pero esa independencia del algoritmo no demuestra que
las estrellas estén excluidas del entrenamiento original de ZTF.**

## Qué falta

Los controles anteriores no aportan todavía suficientes estrellas
distintas por exposición para verificar esta metodología con los datos
reales. Necesitamos seleccionar más estrellas, comprobar la identidad,
el centrado, los píxeles, el detector, la ganancia y el ruido de lectura
de cada exposición. Los modelos de error WCS y la contaminación siguen
pendientes.

No se han descubierto objetos ni se han medido magnitudes calibradas
nuevas. Los ejemplos y pruebas de esta fase son **sintéticos**.

## Archivos

- Código: src/stellarforge/v119_empirical_psf_noise.py
- Pruebas: tests/test_v119_empirical_psf_noise.py
- Metodología detallada: docs/PHASE119_EMPIRICAL_STAR_PSF_AND_CCD_NOISE.md
- Informe: reports/empirical_star_psf_v1.19/SYNTHETIC_VALIDATION_AND_REAL_DATA_GATES.md

Los archivos astronómicos originales y las imágenes de PSF no se
publican en GitHub.
