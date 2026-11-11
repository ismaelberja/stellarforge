# Taurus R2 — authentic original FT Tau two-field instrumental reference ensemble: NO-GO

**11 November 2026 · Real ZTF original per-exposure PSF-fit catalogues from NASA/IPAC IRSA.** This step tests an internally consistent relative magnitude scale, not physically calibrated AB/PS1 magnitudes.

[Authentic original-data GitHub Actions run](https://github.com/ismaelberja/stellarforge/actions/runs/43072549599) ·
[Original 30-day derived-only evidence artifact](https://github.com/ismaelberja/stellarforge/actions/runs/43072549599/artifacts/13880110016) ·
[Permanent original source-level derived NO-GO ledger](../../reports/taurus_variability_r2/FTTAU_REAL_ORIGINAL_NATIVE_TWO_FIELD_INSTRUMENTAL_ENSEMBLE_NO_RAW.json) ·
[Predeclared study thresholds and selection rules](R2_FTTAU_CROSSFIELD_INSTRUMENTAL_ENSEMBLE_METHOD.md)

## Authentic original telescope survey data

Four previously selected true ZTF PSF-fit catalogues (`psfcat.fits`) from FT Tau's two original field/CCD/quadrant groups in each of g and r were downloaded again and their SHA-256 content compared against the **preceding authentic original FITS+mask source-QA ledger**. All **4/4 matched the earlier original native PSFcat file hashes exactly**. No new science exposure was selected, no fresh original science-image pixels were needed, and no historical observing night was added.

The same-band two-detector-field exposure pairs were preselected using **minimum original MJD gap**, 0.000451 days (approximately 39 s) each. The **g pair is from 19 November 2019** and the **r pair is from 3 November 2018**. Comparisons across g and r are **not contemporaneous**.

### Actual source-selection funnel and result

| Authentic original native data | g field 1605 | g field 609 | r field 1605 | r field 609 |
| --- | ---: | ---: | ---: | ---: |
| Total original native PSF catalogue entries | 5,757 | 4,956 | 8,425 | 8,375 |
| Entries within fixed 360″ sky radius of FT Tau | 97 | 94 | 153 | 177 |
| Catalogue entries inside excluded 15″ FT Tau core | 2 | 1 | 1 | 2 |
| Candidate references surviving all independent-per-exposure source-quality, flag, SNR and local-crowding cuts | **12** | **12** | **28** | **27** |

After reciprocal, one-to-one source-position matching within 0.75″ *between* the two same-band field catalogues:

| Predetermined quality gate | **g** | **r** |
| --- | ---: | ---: |
| Genuine matched, positionally plausible, source-disjoint instrumental reference pairs | **10** | **19** |
| Preregistered minimum number of matched controls | **20** | **20** |
| Preregistered split training and held-out validation possible | **No** | **No** |
| Descriptive calibrated/inter-field instrumental median published | **Not calculated** | **Not calculated** |
| Internal reference-ensemble consistency gate | **NO-GO, UNDERPOWERED** | **NO-GO, UNDERPOWERED** |
| Independently verified physical Gaia–ZTF FT Tau association | **0** | **0** |
| Corrected or merged ZTF ObjectID source lightcurves | **0** | **0** |

The instrument-native `mag` column is defined as **`−2.5 log10(flux [DN])`** in the official ZTF Data System (ZSDS) supplementary source-catalogue documentation. It is *instrumental*, not an absolute Pan-STARRS1-calibrated/AB magnitude. The new analysis deliberately does **not** treat it as such.

**Interpretation:** the original two-field same-band overlap contains some plausible, fairly isolated stars under fixed selection rules. But **10 (g) and 19 (r) are below the preregistered 20-control threshold**, so the held-out internal offset-validation experiment was not attempted, even for the nearly sufficient r band. Neither a field magnitude correction nor its uncertainty should be invented by reducing that threshold after seeing actual data.

## Scientific limitations and prevention of false positives

- Native source positions, PSF shape and photometry are from the **same ZTF processing pipeline** in two field/CCD groups. A reciprocal 0.75″ sky match is **not** an independently authenticated cross-survey source association; some matches may be blended or wrong.
- FT Tau was deliberately **excluded within 15″** from the reference pool. The derived reference counts do not measure its astrophysical brightness and do not establish whether any of FT Tau's four ZTF OIDs refer to the same physical source.
- The fixed screening uses `SNR ≥20`, quoted `sigmag ≤0.08` mag, native PSF `chi` between 0.5 and 1.5, `|sharp|≤0.5`, the original ZTF disqualifying mask bits, at least 3″ separation from any other catalogued native source, and a 360″ field radius. A non-detection or rejection by these rules is **not** an astrophysical absence of a reference star.
- No instrumental colour calibration, Pan-STARRS1 standard-star photometric solution, ZTF official image header zero-point uncertainty, field-to-field colour transfer or reference-star intrinsic stability programme was carried out. Even a larger field/reference sample would still need independent external checks.
- Cross-filter g (2019) vs r (2018) cannot support simultaneous colours, true FT Tau variability, new companions or stellar motion estimates.
- Independent publisher Taurus membership verification and source-by-source physical Gaia–ZTF matching remain incomplete. The Taurus technical sample remains **24 deliberately nonrepresentative Gaia IDs**, not a population survey.

## Technical decision and next suitable experiment

**R2 instrumental reference-ensemble validation: NO-GO due to insufficient controls under original preregistration.** All four genuine source catalogues were verifiable and the source matching mathematics/tests ran correctly; scientific validation failed the **sample-size** condition and was therefore conservatively withheld.

An optional, independently preregistered next experiment may use a *wider sky radius* and/or more original historical dates, with carefully documented overlap geometry, spatial/colour dependence and independent stable reference-star identification. This would be a **new study increment**, not a post-hoc modification of this negative experiment, and still must not automatically merge FT Tau lightcurves. A stronger approach should also inspect original ZTF FITS photometric header quality/zeropoints and an **external** PS1/Gaia reference calibration and publish a meaningful systematic error budget.

The complete StellarForge v2.0 engineering software remains finished and shareable. **The Taurus astrophysical R2 source-association research continues**, with zero independently verified physical Gaia–ZTF associations or new astrophysical variability discoveries.

## Reproducibility and original source material

- Original survey run `43072549599`, artifact `13880110016`; original ZIP SHA-256 `565c439a32e5e5fda6a4fc2444fc71eb9f1f7d025e3d20db2a07f49a77801a70`.
- Original derived JSON SHA-256 `97bb5c77b9b290bf5238ca125e2c7e205606e6417ebe2b0bc23954541e6dee51`.
- Historical full original four-image evidence SHA-256 `1be4d2a0633255a6a38e36153662221b70e891016500129801ec2ec6aeac3f5d`.
- Code: `src/stellarforge/r2_fttau_crossfield_instrumental_ensemble.py`; runner `python -m scripts.run_taurus_r2_fttau_crossfield_ensemble`.
- [Masci et al., ZTF Data Processing, Products and Archive (2019)](https://doi.org/10.1088/1538-3873/aae8ac) and [NASA/IPAC official ZTF science data products](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_api.html).

**No original native PSF source magnitudes, source positions, raw FITS pixels, full telescope catalogues or individual source fluxes were committed**; the original-data provider's per-source data remain ephemeral in the GitHub Actions execution.
