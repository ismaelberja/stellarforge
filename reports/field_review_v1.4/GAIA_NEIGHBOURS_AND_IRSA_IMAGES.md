# StellarForge v1.4 — Independent Gaia neighbour and ZTF image-access audit

**Status: validated engineering diagnostics; source identity and image deblending remain OPEN.**  
Analysis date: **2026-11-05**, using the official Gaia DR3 TAP service and previously SHA-verified IRSA/ZTF observations.

## What was independently queried

A 15-arcsec ICRS cone around each original Taurus technical-seed position was queried against `gaiadr3.gaia_source`. Both queries returned the exact target Gaia DR3 source ID and **no other Gaia-catalogued sources** within that radius. This is a report of *Gaia DR3 detections*, not a proof of absent field stars or image blends.

| Gaia cross-check | FT Tau | CIDA 11 |
|---|---:|---:|
| Gaia DR3 source ID | 149623711269425408 | 3419110734340795648 |
| Gaia DR3 sources in 15-arcsec cone (including target) | 1 | 1 |
| Other catalogued Gaia DR3 sources within 15 arcsec | 0 | 0 |
| Other Gaia sources within 5 arcsec | 0 | 0 |
| Gaia G magnitude | 13.604074 | 13.469673 |
| Gaia parallax (mas) | 7.68122 | 5.99431 |
| **RUWE** | **1.32659** | **8.56752** |
| Independent image/blend review | Not performed | Not performed |

CIDA 11's elevated RUWE is a **significant astrometric-fit quality warning**, not conclusive evidence of binarity or photometric contamination. Gaia's DR3 non-single-star documentation mentions values substantially above approximately 1.4 as potentially indicating non-single or problematic fits. Further independent constraints are needed.

## Direct ZTF FITS cutout access (transport only)

Six dated ZTF science cutout URLs were generated from actual ZTF CSV exposure metadata, with the exact field, CCD, quadrant, filter and filefracday information, and Gaia's position propagated to each sampled date. The script reads at most the first FITS header block and **does not examine WCS, image pixels, PSF or local background**. Official reference-image FITS URLs are also constructed and probed if the science URL fails.

Two distinct executions confirmed that archive availability is variable and cannot be interpreted as sky coverage:

| Public GitHub CI run | Gaia fields queried | Science FITS headers verified | Other science URL outcomes |
|---|---:|---:|---|
| [First attempt (42003721186)](https://github.com/ismaelberja/stellarforge/actions/runs/42003721186) | 2/2 | 1/6 | Five HTTP 503 failures |
| [Second attempt (42004372822)](https://github.com/ismaelberja/stellarforge/actions/runs/42004372822) | 2/2 | 2/6 | Four HTTP 503 failures |

In the second execution the **FT Tau field 1605** sample science FITS headers were reachable for the `g` and `r` OID-band groups; FT Tau field 609 and both CIDA 11 samples returned HTTP 503. Four corresponding reference-image fallback URLs also returned HTTP 503. The earlier execution had verified a *different* FT Tau field 609 science header, so **these errors do not establish missing images**.

- Source queries: [IRSA ZTF API](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_api.html).
- Image file naming: [official IRSA ZTF metadata documentation](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html).
- Gaia astrometric-fit interpretation: [ESA Gaia DR3 non-single-star processing notes](https://gea.esac.esa.int/archive/documentation/GDR3/Data_analysis/chap_cu4nss/sec_cu4nss_intro/ssec_cu4nss_intro_inputfiltering.html).
- Complete detector metadata and public cutout URLs: archived **aggregate-only JSON/Markdown**, linked by the [second GitHub run](https://github.com/ismaelberja/stellarforge/actions/runs/42004372822). No raw FITS or individual observation table is committed.

## Reproduce

```bash
python -m pip install -e '.[test,analysis]'
python -m pytest -q
python scripts/run_v14_field_review.py /path/to/original_IRSA_artifact.zip --probe-images --require-gaia
```

The original IRSA photometric artifact must be obtained from an authorized source, or regenerated from the documented original queries with new SHA-256. Aggregate reports are saved in ignored `reports/generated/v1.4_fields`. The workflow never uploads raw ZTF CSV or FITS pixels. All external API failures are explicitly recorded and do not become no-neighbour/no-observation claims.

## Open scientific gates

1. Retrieve and visually inspect valid **science or reference FITS image pixels**, their WCS and local point-spread functions.
2. Assess unresolved/non-Gaia sources, nebulosity, adjacent-source contamination and field-specific OIDs (particularly FT Tau).
3. Reassess **CIDA 11's high Gaia RUWE**, Gaia astrometric covariance and possible non-single-source solutions before relying on a simple propagation model.
4. Independently verify the original publisher Taurus membership table and any source's disk class.
5. Run field-control and actual-cadence variability tests only after source identity and quality are settled.

**Independently confirmed Gaia–ZTF matches: 0. Physical variability events confirmed: 0. Image contamination ruled out: 0.**
