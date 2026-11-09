# StellarForge v1.18 — Real original ZTF pipeline PSF-log audit and FT Tau exploratory source tests

**Observed 9 November 2026.** [Authentic original-data GitHub Actions run, 661 tests passed](https://github.com/ismaelberja/stellarforge/actions/runs/42665465964).

## Why this evidence matters

Two unresolved questions from v1.17 motivated this phase. First, although **four genuinely new Gaia DR3 source IDs were tested in CIDA 11**, we could not show that the original ZTF instrument's DAOPhot model excluded them from its own PSF-training-star set. A new star in *StellarForge* is **not automatically independent of the survey PSF model**. Second, the original strict source quality and isolation limits left **zero additional FT Tau stars**, so the previously successful CIDA 11 source tests could not validate FT Tau.

v1.18 now obtains **all eight publicly archived, per-original-exposure ZTF instrumental pipeline processing logs** and explicitly checks their evidential limits, while separately preregistering a **Gaia-only exploratory FT Tau** sampling tier before any new ZTF CCD/source-pixel inspection. Both tasks are real, reproduced on the same original four dated ZTF science frames. None authenticates an astrophysical Gaia–ZTF identity or new binary/variability event.

## Actual public original survey processing logs

Exactly four original dated science frames from the SHA-verified **2,212-record NASA/IPAC IRSA positional-cone dataset** are selected using unchanged original ZTF OIDs, band, date/field/CCD/quadrant metadata, plus the immutable v1.8 source ledger.

For each original `sciimg.fits` science product the code derives the official `sciimlog.txt` (instrument processing) and `log.txt` (overall pipeline processing) path, without any cutout query. All requests use official IRSA HTTPS, bounded file/time reads, original SHA-256 source provenance and redirect/HTML/data validation. Raw log text is **not** committed or published.

| Original technical field | Original science MJD | `sciimlog.txt` readable | `log.txt` readable | Processing lines referring to PSF/DAOPhot in `sciimlog.txt` | Explicit full training-star ID roster authenticated |
|---|---:|---|---|---:|---:|
| FT Tau | 58388.389016 | Yes | Yes | **115** | **No** |
| FT Tau | 58491.184780 | Yes | Yes | **115** | **No** |
| CIDA 11 | 58475.113750 | Yes | Yes | **116** | **No** |
| CIDA 11 | 58849.135984 | Yes | Yes | **116** | **No** |
| **Total** | Four real exposures | **4/4** | **4/4** | **462** | **0** |

The additional `log.txt` files each have one line mentioning PSF/DAOPhot under the deliberately bounded pattern search. No aggregate PSF-training-star count matched the narrow count-expression parser in the available original records. **This does not prove the archive lacks all useful PSF reduction detail**; it means the current audit could not authenticate a complete source-keyed training-star roster or its source-ID coordinate namespace.

**Crucial distinction:** ZTF's `psfcat.fits` contains sources measured *after* a PSF model is estimated; it is not a declaration of which source positions were used to build the PSF. A star absent from a raw log text search, and even a processing count, do **not** prove it was excluded from the original PSF model. The source training membership status therefore remains **NOT_VERIFIABLE_FROM_THIS_LOG** on **all four** actual original science exposures. <https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html>

## FT Tau: strict unchanged criteria vs separately labeled exploratory Gaia tier

A fresh original Gaia DR3 wide-cone query returned **50 Gaia records** within 210″ of FT Tau; all ten original technical target/reference Gaia source IDs are excluded. The fixed **v1.17 strict Gaia-only rules still select zero new stars**, confirming the original sample-coverage limitation under those criteria.

A *separate, explicitly exploratory* Gaia-only source tier was declared **before viewing any current ZTF native PSF or science-image pixel results**, with target separation 20″–190″, Gaia G magnitude 12–19.2, G flux-over-error ≥30, RUWE 0.5–1.6 and separation ≥6″ to every returned Gaia DR3 source, while retaining the clean astrometric 5/6-parameter solution, nonduplication and original source-ID exclusion requirements.

This **lower quality/isolation threshold is not equivalent to the strict CIDA 11 v1.17 source sample**, nor an independently authenticated set of isolated empirical PSF stars.

Four original Gaia-only FT Tau exploratory candidates were selected with the new fixed source-quality/sky-quadrant rule:

| New Gaia DR3 source ID | Gaia G magnitude | Gaia RUWE | Nearest other Gaia source | Offset from FT Tau | ZTF native-source pixel evidence |
|---|---:|---:|---:|---:|---|
| **149623298952568064** | 17.7420 | 0.9596 | 9.766″ | 144.66″ | **Original masked PSF fits in both original science epochs** |
| 149626524469932160 | 18.5131 | 1.0180 | 20.375″ | 122.96″ | No native PSF-catalog entry within 1″ in either epoch |
| 149626696268631424 | 18.2840 | 0.9495 | 8.585″ | 102.91″ | Native PSFfit catalogue `chi/sharp/flags` gate review in both epochs |
| 149626902427531520 | 18.4059 | 1.0188 | 32.938″ | 185.05″ | No candidate in the earlier epoch; native quality gate review in the later epoch |

The four Gaia-only candidates occupy three sky quadrants, not a complete four-quadrant FT Tau calibration map. Those listed offsets/isolations describe catalogue positions and cannot certify sources are astrophysically single or uncontaminated.

## Genuine original ZTF mask+science PSF fits

The two historical FT Tau science epochs passed original native `psfcat.fits` loading, four-source candidate screening, original `sciimgdao.psf` spatial model decoding, and original `sciimgdaopsfcent.fits` same-pipeline field-center PSF reconstruction sanity checks.

The one new eligible FT Tau exploratory Gaia source was matched **provisionally** to one original native ZTF PSFfit source in each epoch and underwent the same v1.16 genuine `sciimg.fits` + `mskimg.fits` WCS-aligned masked source-pixel model fit with original spatial DAOPhot PSF, native per-exposure detector `xpos/ypos`, sky-plane nuisance coefficients and same-source checkerboard pixel residuals.

| FT Tau original science epoch | Gaia source ID | Original masked PSF fit | Same-source held-out residual RMS / sky MAD noise proxy | Provisional same-source residual screen |
|---|---|---|---:|---|
| MJD 58388.389016 | 149623298952568064 | Complete | **0.920302** | Pass |
| MJD 58491.184780 | 149623298952568064 | Complete | **0.955383** | Pass |

**Two completed image fits = one distinct Gaia candidate source observed at two epochs**, not two independently withheld stars. Both diagnostic ratios compare different pixels of the same star image with the local annular MAD-noise proxy and are not calibrated instrumental PSF error, photometric magnitudes or independently verified physical source identity.

The remaining **six of eight** FT Tau exploratory candidate×epoch cases were native catalogue proximity or fit-quality review/ineligible outcomes and **were not fitted to original source pixels**; they are not astrophysical nondetections.

## Shifted-position density controls and run robustness

The four exploratory Gaia positions were each offset ±25″ along east/west/north/south in both FT Tau original science epochs, producing **32** preregistered local native PSF-catalogue positional probes. All **32/32** had **no** native PSFcat source within 1″. As in v1.17 these are correlated, deterministic and can contain unrelated true stars under different sky conditions; **0/32 is not a calibrated chance-association probability or proof of physical Gaia–ZTF identity**.

The full [original-data execution](https://github.com/ismaelberja/stellarforge/actions/runs/42665465964) passed **661 automated tests**, accessed **8/8 official textual processing products** with no HTTP 503, read the 50-row FT Tau Gaia field, regenerated four original ZTF product paths, completed both original FT Tau masked-pixel PSF fits on the same new source, and emitted SHA-controlled derived-only JSON/Markdown reports. The original raw ZTF text logs, FITS images, science masks, PSFcat rows, DAOPhot coefficient arrays, Gaia original CSV and IRSA source photometric measurements remain outside public Git and public Actions artifacts.

## Scientific outcome and next essential gate

**Achieved:** a verified method to audit source-specific original reduction logs without inventing PSF training membership, plus a new real FT Tau exploratory-source example with two same-source masked image PSF fits.

**Not achieved:** a validated original DAOPhot training-star roster, a genuinely *training-independent* PSF held-out star sample, FT Tau field-wide clean-star calibration, a calibrated ZTF detector WCS/PSF uncertainty, authenticated physical Gaia–ZTF source matches or any new astronomical companion/variability discovery. The three original v1.16 high-positive-residual review cases remain unresolved. The high Gaia RUWE for CIDA 11 remains an independent astrophysical source-model caveat.

**Next:** try to identify original ZTF PSF-building support files or reconstruct a genuinely independent PSF from separately documented Gaia reference stars; secure wider original science epochs/filters and a physically motivated pixel noise model before measuring external WCS/PSF errors. Preserve transparent strict/exploratory sample strata and sample-selection limitations. If original training-star membership is unavailable, close the v2.0 *software portfolio* with an explicit science limitation rather than implying independent instrumental calibration.

[Method and preregistered Gaia tier](../../docs/PHASE118_PSF_TRAINING_LOGS_AND_EXPLORATORY_FTTAU.md) · [Source-code log and selection guards](../../src/stellarforge/v118_original_training_log_fttau.py) · [Original science/Gaia runner](../../scripts/run_v118_original_ztf_psf_training_audit.py) · [Synthetic adversarial tests](../../tests/test_v118_original_training_log_fttau.py).
