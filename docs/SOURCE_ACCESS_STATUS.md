# MOST RECENT OFFICIAL ZTF ORIGINAL PSF PROCESSING-LOG STATUS — StellarForge v1.18, 9 November 2026

[Verified real original ZTF/Gaia workflow](https://github.com/ismaelberja/stellarforge/actions/runs/42665465964) completed **661 regression tests**, four immutable historic single-science FT Tau/CIDA 11 dates, original SHA-audited 2,212-row IRSA positional-query transport and exact v1.8 exposure ledger.

- **Original authentic reduction logs available:** **8 of 8** `sciimlog.txt` and `log.txt` files returned from official IRSA dated product paths for FT Tau MJD 58388.389016 / 58491.184780 and CIDA 11 MJD 58475.113750 / 58849.135984. Original instrumental processing logs contained **115, 115, 116, 116** lines respectively referring to PSF/DAOPhot terminology; their accompanying overall `log.txt` files contained 1 such line each. SHA-256 hashes/provenance documented in aggregate output; **raw log text never committed/published**.
- **Native PSF-training-star identity remains UNKNOWN:** **zero validated full DAOPhot PSF model-training source-ID rosters** were recovered from those original processing logs. A ZTF `psfcat.fits` list of post-fit source detections is not an instrumental model-training source roster; no new Gaia object was proved absent from original training.
- **Fresh FT Tau Gaia-only wide cone:** 50 Gaia DR3 records; unchanged prior strict quality/isolation rules still yield **0** new references. The **predeclared, separately labeled EXPLORATORY** broader G/RUWE/source-isolation/radius tier yielded **four** new Gaia DR3 candidate IDs (not previously used by StellarForge).
- **Genuine FT Tau original masked science pixels:** only **one of those four newly selected Gaia source IDs** (`149623298952568064`) passed native catalogue eligibility on both historic FT Tau g-band exposures, yielding **two** genuine original `sciimg.fits`+`mskimg.fits` masked source-PSF fits, both passing internal same-source pixel residual QC with RMS/annular sky MAD proxies **0.920302**, **0.955383**. Other **six source×epoch** original catalog candidate checks did not pass and were **not** pixel-fitted; not physical stellar nondetections.
- **Original shifted source-catalogue probes:** 32 deterministic ±25″ positions, 0 matching native PSFfit catalogue entries within 1″; these are not a calibrated chance association probability.
- **Scientific limitations:** exploratory Gaia limits are less stringent than v1.17 strict, each fit is a *same-star* different-epoch observation rather than an independent source holdout, and potential membership in the original ZTF PSF training sample is unknown. No authenticated physical Gaia–ZTF IDs, true isolated PSF calibration, absolute detector WCS error or companion/variability claims. CIDA 11 target Gaia DR3 RUWE remains high.

[Full v1.18 original survey pipeline log and FT Tau source evidence](../reports/psf_training_ft_tau_v1.18/REAL_ZTF_LOG_AUDIT_AND_EXPLORATORY_FT_TAU.md) · [Methodological PSF-training caveats and preregistered Gaia source tiers](PHASE118_PSF_TRAINING_LOGS_AND_EXPLORATORY_FTTAU.md) · [Original ZTF official ancillary processing-log definitions](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html).

---

# MOST RECENT ZTF/Gaia SOURCE ACCESS — StellarForge v1.17, 9 November 2026

[Original source-data workflow](https://github.com/ismaelberja/stellarforge/actions/runs/42661663983) passed **636 automated tests**, with SHA-verified original IRSA 2,212-row photometric acquisition (not physically confirmed target light curves) and two **fresh independent Gaia DR3 210″ cone queries**:

- **FT Tau independent Gaia wide cone:** 50 Gaia DR3 records. After excluding previously selected target/reference source IDs and applying fixed Gaia-only astrometric/photometric quality and ≥10″ all-Gaia-neighbor isolation, **zero previously unused field controls** eligible. The v1.17 run made no original native PSF/science-pixel requests for FT Tau new sources; this is a source-selection limitation, not proof of no physical FT Tau field stars.
- **CIDA 11 independent Gaia wide cone:** 250 Gaia records, 20 eligible previously unused Gaia-only stars before four-source budget, with one Gaia source selected in each quadrant. These four are absent from v1.8–v1.16 ten-source technical target/reference IDs but **not proven excluded from original ZTF native DAOPhot spatial PSF training stars**.
- **Original ZTF two CIDA 11 dated science frames:** original native `psfcat.fits` tables, spatial `sciimgdao.psf` source models and official original field-center `sciimgdaopsfcent.fits` consistency checks retrieved. Eight original source×date candidate tests were attempted; **six passed native catalogue QA and received original `sciimg.fits` + `mskimg.fits` matched pixel residual fits (six provisional same-image residual QA passes)**. Two ZTF source associations did not meet catalogue candidate/profile quality criteria, so no pixel fit was attempted.
- **Shifted-sky local accidental-match-density probes:** **32** historical-exposure × 25″ east/west/north/south positions, zero native ZTF PSFcat source detections within 1″, but these are correlated and not a formal false-association probability, a contamination rate or physical source match.
- **Full Gaia 5D formal astrometry:** all four new Gaia DR3 source IDs were queried with full exact correlated five-parameter solutions and geometric Earth-geocentric first-order annual parallax at the two original CCD science MJDs. Their source identities in ZTF remain provisional; full Palomar topocentric/mid-exposure/color effects are not yet modeled.
- **Original historical archive expiry:** the original SHA-verified ZTF position-query acquisition run `41997079598` is a time-limited GitHub Actions artifact (historical expected expiry **12 November 2026**). Reruns after expiry must reacquire the official identical science selection with newly documented source hashes instead of relying on nonexistent/guessed raw data.
- **Raw data privacy/provenance:** no original full Gaia TAP source CSV, ZTF PSFfit BINTABLE catalogue rows, original science+mask FITS pixel arrays, DAOPhot spatial coefficients or IRSA original photometric rows were committed to public Git or uploaded in aggregate-only artifacts.

**Open science checks:** original ZTF DAOPhot PSF training membership and genuinely independent stellar holdouts, new control stars for FT Tau or alternative predeclared fields, realistic pixel/WCS errors, independent Gaia/ZTF physical source identity and multiple actual dates/bands. Elevated v1.16 source image residuals and CIDA 11 high RUWE are unresolved and not proof of astrophysical companions.

[Real-data source-disjoint Gaia evidence](../reports/new_gaia_holdouts_v1.17/REAL_DISJOINT_GAIA_CONTROL_AND_SHIFTED_SKY_RESULTS.md) · [Methods and controlled sky-shift caveats](PHASE117_DISJOINT_GAIA_SOURCE_HOLDOUTS_AND_SHIFTED_SKY_NULLS.md).

---

# CURRENT OFFICIAL REAL ZTF SCIENCE/MASK + SPATIAL PSF DATA — StellarForge v1.16, 8 November 2026

The latest [real ZTF original masked source-pixel PSF workflow](https://github.com/ismaelberja/stellarforge/actions/runs/42518746629) succeeds with **614 automated tests**, original SHA-verified 2,212-row position-cone input and **four original dated single-exposure g-band science frames** for FT Tau/CIDA 11.

- **Original source spatial PSF products:** all 4 original full `psfcat.fits`, all 4 native `sciimgdao.psf` spatial DAOPhot files and all 4 official `sciimgdaopsfcent.fits` center-stamp consistency checks were accessible. Each original DAOPhot spatial PSF has a Gaussian analytic kernel plus 3×47×47 correction tables; source-local model is 23×23 original pixels, not a star-authenticated empirical PSF.
- **Actual original image science/mask data:** every one of **16/16 v1.14 provisionally selected native PSF candidate source positions** was retrieved as a matching `sciimg.fits`+ `mskimg.fits` pair using original 60″ cutouts and independent matching celestial WCS grids. All sixteen native source catalog subpixel phases agreed, all original source 4.5-pixel cores had **0 official 6141 bad/saturated pixels**, and **all 16 model amplitude + sky-plane fits** completed on original ZTF image **DN** values (not calibrated magnitudes).
- **Science pixel residuals:** original same-image checkerboard withheld pixel diagnostics: **13** provisional screens passed, **3** positive residual peaks flagged for review; median held-out RMS/robust annular sky-MAD proxy **1.1015**. These are **not independent source-star validation** or calibrated 1σ instrumental uncertainty. In this one bounded run there were **zero HTTP 503** for the 16 source requests; earlier archive access failures remain historically documented below.
- **Three unresolved real review sources:** FT Tau target MJD 58491.184780 peak residual/noise proxy 7.6730; CIDA 11 target MJD 58849.135984 11.8679; and Gaia candidate reference `3419111520318480128` in the CIDA 11 field same date 7.8125. These ratios are engineering review indicators **not source-companion, physical variability or formal-significance detections**.
- **Original source provenance and rights:** original acquisition GitHub Actions run `41997079598` SHA-manifested IRSA dataset may expire around **12 November 2026**; if unavailable, reacquire original official IRSA data with new documented SHA-256 and exact source provenance. Gaia DR3 exact ten-source formal 5D correlation/geocentric parallax cannot authenticate a physical ZTF match or account for high RUWE CIDA 11. Original raw Gaia TAP CSV, original FITS science/mask pixels, native spatial PSF coefficients and full native PSFcat source tables never enter public Git/CI artifacts.
- **Open gate:** independent Gaia/ZTF star identification, independent spatially distributed **different-star** masked PSF/WCS validation, detector correlated variance, physical crowding and matching false-positive assessment, exact original exposure timing/topocentric/chromatic systematics and full field-star instrument PSF calibration before any astrophysical discovery.

[Full actual observed source-pixel v1.16 report](../reports/masked_spatial_psf_v1.16/REAL_ZTF_PIXEL_RESIDUALS_EVIDENCE.md) · [Methods and caveats](PHASE116_ORIGINAL_MASKED_PSF_PIXEL_RESIDUALS.md) · [Official IRSA ZTF image units, matching ancillary file names and time conventions](https://irsa.ipac.caltech.edu/data/ZTF/docs/releases/dr06/src/dr06.html).

---

# CURRENT ORIGINAL ZTF SPATIAL DAOPhot PSF FILE STATUS — StellarForge v1.15, 8 November 2026

This is the latest verified access and science status. Historical records retained below.

- **Actual original PSF files:** [real observed-data run](https://github.com/ismaelberja/stellarforge/actions/runs/42514987086) retrieved and decoded **all four original 88,465-byte `sciimgdao.psf` spatial DAOPhot Gaussian+3×47×47 correction-table files**, one per original dated science exposure of FT Tau/CIDA 11, plus **all four genuine separate 23×23 `sciimgdaopsfcent.fits` native center-PSF stamps**. The original files were used in an ephemeral runner and are **not** in public Git/artifacts.
- **Model reconstruction versus original official center FITS:** same-field native center cosine similarity **0.999999–1.000000**, normalized L1 differences **0.000278–0.000984**. All four center comparisons pass internal reconstruction checks, **not independent observational/empirical PSF or telescope WCS accuracy validation**, since both products derive from the same ZTF DAOPhot processing.
- **Source-specific shape model:** original `psfcat.fits` full native catalogues also retrieved for four epochs (from historical v1.14 source pilot, total 27,207 original PSF-fit rows). **Sixteen** of twenty Gaia-target/reference × epoch positions were already provisional catalogue counterparts, and all sixteen received approximate normalized 23×23 spatial PSF *model* shapes at the original CCD native `xpos/ypos`. These are not residual-tested against same-date original star-image pixels.
- **Important approximation:** SciPy cubic B-spline correction interpolation matches official field-center reconstructions exceptionally well but is not a formally validated DAOPhot native bicubic routine at arbitrary spatial position or fractional pixel phase.
- **Original source provenance:** recovered SHA-audited official 2,212-row ZTF positional-cone dataset from historical GitHub Actions original acquisition `41997079598`, with v1.8 immutable derived reference ledger source SHA-256 `fb7d5c315cbef56b2551e73920c67920827d91160b4c0bd35f3fd77113166beb`. Original acquisition artifacts are time-limited; expected expiry **12 November 2026**. Future reruns after expiry require a new official original acquisition with its own hashes, not a substituted unverified CSV.
- **Still missing:** robust source-by-source original `sciimg.fits` and `mskimg.fits` matched pixel-mask residual tests, independently authenticated Gaia/ZTF star associations and isolated source PSFs, full-time topocentric apparent place, detector WCS distortion and held-out instrumental uncertainty calibration. Gaia CIDA 11 RUWE ~8.57 remains a strong astrophysical source-model caution. **No new confirmed variability, companions or calibrated WCS errors**.

[Observed v1.15 source-data evidence and PSF model numerical checks](../reports/spatial_daophot_v1.15/REAL_DAOPHOT_CENTER_AND_LOCAL_SHAPES.md) · [Methods and limitations](PHASE115_DAOPHOT_SPATIAL_MODEL_VALIDATION.md) · [GitHub Actions real 590-test validation](https://github.com/ismaelberja/stellarforge/actions/runs/42514987086).

---

# CURRENT OFFICIAL ZTF NATIVE PSF DATA ACCESS — StellarForge v1.14, 8 November 2026

This section is the most recent verified source status. Historical sections remain below for audit.

- **Actual original ZTF native PSF catalogues:** four full `psfcat.fits` FITS binary tables **successfully downloaded/parsed** from the official IRSA original science-exposure products (no HTTP 503 in this run): FT Tau MJD58388.389016 **3,970** entries; FT Tau MJD58491.184780 **5,569**; CIDA 11 MJD58475.113750 **5,313**; CIDA 11 MJD58849.135984 **12,355**. Total **27,207 per-exposure PSF-fit detection records**. These do not correspond to 27,207 astrophysically independently identified physical stars; they are pipeline detections in four CCD-quadrant products.
- **Gaia–ZTF provisional candidate screen:** ten exact Gaia DR3 IDs with full formal five-parameter covariance/geometric annual parallax, evaluated on twenty target/reference × exposure date combinations. **16** native catalog candidate source profiles within ≤1″ passed conservative `chi/sharp/SNR/flags` screening, **three** require low-`chi` review, **one** lacked a nearby PSF catalog entry. Median positional catalogue-to-Gaia separation for the sixteen screened candidate profiles is **0.1258465″**, not WCS precision or confirmed source identity. Actual source matches, crowding/blending and target CIDA 11 high Gaia RUWE remain open.
- **Four official spatial DAOPhot models:** all four native original `sciimgdao.psf` files were retrieved, **88,465 bytes per dated original file**; file hashes are recorded. These have **NOT** been decoded or evaluated at a star-specific native detector `xpos/ypos`. This is not a calibrated local instrumental PSF measurement. The v1.13 native center-of-science-image 23×23 FITS stamps are different products.
- **Historic original ZTF acquisition:** SHA-checked 2,212 positional-cone source rows, original GitHub Actions acquisition run `41997079598`. This transient source artifact is scheduled to expire **12 November 2026**, and data use without it requires a new official IRSA source acquisition with newly tracked hashes/provenance. Archive transport failure is never an astrophysical nondetection.
- **Official source definitions:** [NASA/IPAC IRSA ZTF science-product filenames](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html) and [ZTF Science Data System explanatory supplement §10.6 — `psfcat.fits` source columns, `chi`, `sharp`, `flags`](https://irsa.ipac.caltech.edu/data/ZTF/docs/ztf_explanatory_supplement.pdf).
- **Remaining gates:** actual source-specific DAOPhot spatial PSF decoding/evaluation, complete true `mskimg.fits` detector controls for each candidate, source identity/crowding/selection, instrumental WCS & PSF error budget with external holdouts and realistic errors; no new physical variability or companion claim. Original Gaia CSV, native ZTF FITS catalogue rows and DAOPhot bytes remain outside public Git and uploaded artifacts.

[Real v1.14 source-candidate evidence](../reports/native_psfcat_v1.14/REAL_ZTF_GAIA_PSF_CATALOGUE_EVIDENCE.md) · [Method and science limits](PHASE114_NATIVE_PSF_CATALOGUE_AND_SPATIAL_MODEL_GATE.md) · [Successful 564-test original-data workflow](https://github.com/ismaelberja/stellarforge/actions/runs/42513198605).

---

# CURRENT OFFICIAL ZTF INSTRUMENT ACCESS — StellarForge v1.13, 8 November 2026

This status supersedes older entries below, which remain for historical audit.

- **Original official ZTF IRSA pilot:** same SHA-verified 2,212-row position-query artifact, acquired in historic run `41997079598` and still accessible to a temporary GitHub Actions runner at the time of the v1.13 audit. The original 2026-11-05 raw source artifact is scheduled to expire on **12 November 2026**. Its expiry is an input reproducibility/rights-and-access issue, not evidence about astronomical sources.
- **Original `mskimg.fits` instrument bit-mask products:** 20 candidate source apertures on four original single-exposure g-band dated science images were attempted. **Four** Gaia reference-source masks were successfully retrieved along with matching science FITS pixels, and both original FITS celestial WCS grids aligned exactly at sampled locations. All four nominal 4.5-pixel apertures had **zero disqualifying 6141 mask bits and zero bit-8 saturation pixels**. **16** other source attempts were HTTP 503; **all four technical target-star cores were inaccessible**. A mask-clean aperture does not validate a single isolated Gaia–ZTF match.
- **Native `sciimgdaopsfcent.fits` products:** across two read-only passes over the same original science dates, all **four unique original science-field-center 23×23 PSF FITS stamps were accessible/parsable** (first run accessed two; rerun the other two). They represent **the field center only**, not local PSF evaluations at the four original target/reference positions, and cannot produce independent WCS uncertainties. The [repeat run](https://github.com/ismaelberja/stellarforge/actions/runs/42468217065) passed 533 tests but all **20 original mask/science pair attempts returned HTTP 503**; it did not repeat any of the four successful initial mask checks.
- **Reference data model:** exact ten Gaia DR3 source IDs with formal full five-parameter correlations and first-order Earth-geocentric annual parallax at original exposure dates, not full observatory topocentric apparent-coordinate or non-single-star solutions. CIDA 11 RUWE ≈8.57 is a strong astrometric model-quality warning.
- **Official archive definitions:** [IRSA ZTF metadata suffixes](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html) and [ZTF explanatory supplement Section 10.3, disqualifying mask bits 6141](https://irsa.ipac.caltech.edu/data/ZTF/docs/ztf_explanatory_supplement.pdf).
- **Remaining science gate:** field-dependent `sciimgdao.psf` / `psfcat.fits` per-source validation, genuine Gaia/ZTF source association, independent WCS/PSF instrumental uncertainty and real physical variability/companions. Source FITS/mask/PSF pixel bytes and raw IRSA/Gaia catalogs are never committed or exported to public artifacts.

[Actual measured v1.13 instrument mask and native PSF evidence](../reports/original_masks_psf_v1.13/REAL_ZTF_MASK_AND_NATIVE_CENTER_PSF_EVIDENCE.md).

---

# CURRENT ORIGINAL-ZTF SCIENCE IMAGE ACCESS STATUS — StellarForge v1.12, 8 November 2026

This latest section supersedes the historical entries retained below for reproducibility.

- **Official original source inventory:** the original IRSA 2,212-row raw positional-cone artifact remains retrievable and SHA-verified as of the [v1.12 real-image run](https://github.com/ismaelberja/stellarforge/actions/runs/42459615687), using original acquisition run `41997079598`. The historical original raw artifact is short-lived and scheduled to expire **12 November 2026**; a missing artifact after expiry is a provenance/access problem, not evidence about the sky.
- **Original dated ZTF pixel reanalysis:** **two separate 20-request runs** on the **same four original dated science exposures** (four target + sixteen reference candidates per run). Run A gave 9 HTTP 503, 2 incomplete pixel screens and 9 complete Gaussian/aperture profiles. **Final run B** gave **8 HTTP 503 and 12 complete profiles** (1 target, 11 references). Four overlapping successfully obtained FITS stamps had **identical SHA-256**; these are repeats of the same data, not new sky epochs. No reference coadd counted as science.
- **Scientific model comparison:** final-run median Gaussian–aperture centroid disagreement across **twelve** complete image screens was **0.104720″**; one CIDA 11 MJD 58475.113750 exposure had **four** cross-model reference candidates, with Gaussian/aperture *internal LOO disagreement* **0.064675″ / 0.155762″**. The target stamp itself returned HTTP 503 in the final run. These are **not** instrument-accuracy estimates, real physical source offsets, new exposures or calibrated PSF/WCS uncertainties.
- **Gaia DR3:** ten exact source IDs with formal full 5D covariance and annual geocentric parallax at their actual provisional UTC science MJDs. High CIDA 11 target RUWE ≈8.57 and unknown ZTF instrument noise remain explicit limitations.
- **Still missing:** independently verified source association, time-scale/observatory apparent-place calibration, official `mskimg.fits` detector masks, native `sciimgdao.psf` instrument PSFs, saturation/crowding flags and a genuine held-out field-star WCS uncertainty model. [IRSA documents the original ZTF mask and PSF products](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html).
- **No raw data publication:** original Gaia CSV, positional-query photometric rows and FITS pixel matrices are processed in ephemeral GitHub Actions only, while aggregate diagnostics and individual file hashes may be made public. Source metadata, source IDs, and derived numerical screens remain unverified astrophysical identities.

[Full v1.12 real FITS diagnostic report](../reports/real_fits_v1.12/REAL_TWO_CENTROID_MODEL_QA.md) · [v1.12 methods and missing calibration gates](PHASE112_PIXEL_CENTROID_AND_WCS_LIMITS.md).

---

# Current source/observation access — StellarForge v1.11 (6 November 2026)

This is the latest version; older notes below are historical.

- **Gaia DR3 reference astrometry:** v1.11 queried **ten exact Gaia DR3 IDs**, including the eight reference candidates measured with ZTF Gaussian profiles in v1.8 and the two target stars. Full five-parameter catalogue **formal covariance** and all ten correlations were returned for each, and individual Earth-geocentric first-order annual parallax shifts were modeled at the original exposure MJDs. [Observed 484-test Gaia run](https://github.com/ismaelberja/stellarforge/actions/runs/42254052752).
- **Reanalyzed ZTF derived image offsets:** 13 original reference models in four actual dated g-band science exposures, from [historical v1.8 official ZTF run](https://github.com/ismaelberja/stellarforge/actions/runs/42077605987) and [small public derived ledger](../data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json); no original FITS pixels re-fitted and no new ZTF raw images acquired in this phase.
- **Actual sensitivity:** after each Gaia reference's parallax correction the strict reference holdout RMS is **0.075770″ FT Tau** (vs 0.075782″ before) and **0.092971″ CIDA 11** (vs 0.093046″ before). Maximum individual reference-star geometric correction was **0.60918 mas**. Strict eligible exposure count remains 2 of 4.
- **Catalogue vs instrument:** the Gaia formal east/north source uncertainties (median **0.15786/0.11637 mas** for the 13 reference observations) are NOT ZTF detector WCS or PSF uncertainties, and do not correct shared source model or instrument calibration systematics. High CIDA 11 RUWE ~8.57 remains unresolved.
- **Source provenance:** new Gaia exact-ID TAP raw response SHA-256 `688e7cfcda6f528d58bc1f92c44b86396de905eef2e28d0db4ce28d4558aa545`; original ZTF v1.8 derived aggregate SHA-256 `fb7d5c315cbef56b2551e73920c67920827d91160b4c0bd35f3fd77113166beb`. Raw Gaia TAP records, ZTF light curves and FITS pixels are not published.
- **Research scientific gates remain open:** no independently confirmed Gaia/ZTF association, empirical PSF/wavelength control, calibrated detector astrometric errors, physical variability events or new companions. Detailed [v1.11 scientific report](../reports/reference_parallax_v1.11/REAL_GAIA_REFERENCE_PARALLAX_LOO.md).

---

# CURRENT REAL-DATA EVIDENCE AND ACCESS — v1.10 (6 November 2026)

The older milestones below remain historical and are superseded by this current status.

- v1.10 uses the real [v1.8 Gaia reference/ZTF image workflow](https://github.com/ismaelberja/stellarforge/actions/runs/42077605987), archived as a **small derived 13-reference / 4-exposure** ledger with original JSON SHA-256 `fb7d5c315cbef56b2551e73920c67920827d91160b4c0bd35f3fd77113166beb`. The reduced public [ledger](../data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json) contains no FITS pixel arrays, raw ZTF light curves or original Gaia TAP CSV.
- Actual leave-one-Gaia-reference-out diagnostics: FT Tau MJD 58491.184780 has three strict models, LOO RMS **0.075782 arcsec**; CIDA 11 MJD 58475.113750 has four strict models, LOO RMS **0.093046 arcsec**. The later CIDA 11 MJD 58849.135984 has five *inclusive* reference fits but only two strict fits — **not enough for strict LOO QA**.
- v1.9 Gaia 5D formal uncertainty/parallax applies to the two Gaia **targets**, not the historical v1.8 **reference** star positions. Internal holdout discrepancies do not establish ZTF instrument astrometric precision or physically authenticated source matches.
- The original public v1.8 external artifact expires on **12 November 2026**; derived evidence is retained, but that is not the original FITS/raw-data archive. Existing historic original ZTF raw artifacts may remain accessible until their configured GitHub Actions expiry.
- All scientific source identity, empirical PSF calibration, independent WCS/distortion and astrophysical event claims remain **UNVERIFIED**. High CIDA 11 Gaia RUWE ~8.57 requires explicit quality warnings.
- v1.10 offline evidence/test workflow: [successful 468-test validation](https://github.com/ismaelberja/stellarforge/actions/runs/42214593233), using neither remote service nor raw archive access.

---

# CURRENT GAIA/IRSA ACCESS AND ASTROMETRIC EVIDENCE — v1.9 (6 November 2026)

**This is the latest verified project status. The historical v1.8 and earlier entries below remain for provenance.**

- **Official Gaia DR3 v1.9 covariance query:** two exact IDs (FT Tau `149623711269425408`, CIDA 11 `3419110734340795648`) with all **five astrometric parameter errors and ten correlations**, Gaia RUWE and original astrometric solution metadata. Four historical ZTF science observation MJDs were used for a **geocentric first-order annual parallax** and propagated **formal Gaia-only** 2D covariance. See [real Gaia v1.9 report](../reports/gaia_formal_v1.9/GAIA_COVARIANCE_AND_ANNUAL_PARALLAX.md) and [observed workflow](https://github.com/ismaelberja/stellarforge/actions/runs/42175644367).
- **Gaia parallax corrections vs linear-motion-only source predictions:** FT Tau east +6.791 / −4.781 mas; CIDA 11 east −1.362 / −2.250 mas at two dates each. These are *not observed physical displacements*.
- **Formal Gaia-only positional uncertainty:** FT Tau east 0.070–0.073 mas, CIDA 11 east 0.444–0.585 mas, without any instrumental ZTF error component. CIDA 11 **RUWE 8.56752** seriously weakens treating the formal single-star covariance as a complete astrometric error budget.
- **IRSA empirical precursor:** 2,212 original photometric positional-cone rows, 12 original science FITS epochs across six ZTF OID/bands (v1.7), 8 Gaia catalogue reference candidates and 13 candidate ZTF image model fits (v1.8). Source matching, isolated stellar PSF and WCS distortion calibration are *not independently confirmed*.
- **Public data policy:** source Gaia TAP CSV and all original ZTF FITS pixels are used only transiently, never committed or uploaded as raw artifacts by the v1.9 workflow. The historical earlier ZTF acquisition artifacts have their own retention and must not be mistaken for a permanent raw-data archive.
- **All astrophysical source IDs / new variability events remain UNVERIFIED.** The v1.9 time scale is provisionally UTC; observer-specific apparent sky position, radial velocity/perspective and topocentric data remain unmodeled.

---

# CURRENT SOURCE AND REFERENCE ACCESS — v1.8, 5 November 2026

**This v1.8 status supersedes the historical milestones below; older results are retained with their original dated limitations.**

- Official IRSA original 2,212 positional-cone photometric rows remain SHA-checked; they are **not physically confirmed Gaia/ZTF light curves**.
- Independent wider Gaia DR3 210-arcsec TAP sources returned **50 entries around FT Tau and 250 around CIDA 11**, allowing **3 and 5 conservative candidate reference selections** after quality, RUWE, brightness and isolation tests. These are **not authenticated clean PSF stars**.
- The real [v1.8 reference-image run](https://github.com/ismaelberja/stellarforge/actions/runs/42077605987) obtained **4 real target FITS Gaussian proxy fits and 13 valid candidate reference image fits out of 16 attempted reference cutouts**, all sharing the respective dated ZTF science archive product paths.
- With >=3 different Gaia candidate IDs, **three exposures** permit a provisional median signed east/north offset: FT Tau MJD 58491.184780 (+0.08708″,+0.01267″); CIDA 11 MJD 58475.113750 (+0.05232″,+0.05436″) and MJD 58849.135984 (−0.00793″,+0.02166″). A fourth frame had only one usable reference.
- No **independently validated WCS, empirical PSF or Gaia/ZTF crossmatch** has been obtained. Linear 2D Gaia proper motion ignores full covariance/parallax. CIDA 11 Gaia RUWE ~8.57 requires caution; small nominal residuals are not accuracy claims.
- Public GitHub contains only vetted aggregate data and code, not original Gaia TAP CSV responses, original individual ZTF photometry or FITS pixel arrays. [Detailed real v1.8 report](../reports/gaia_reference_v1.8/REAL_REFERENCE_CANDIDATE_EVIDENCE.md).

---

# CURRENT SOURCE/IMAGE ACCESS — v1.7, 5 November 2026

**This section supersedes the historical v1.6 and earlier access notes below; all previous observations are kept for chronology.**

- **Official IRSA raw photometry:** two SHA-checked 2-arcsec position queries, 2,212 ZTF rows (FT Tau cone 1,199 and CIDA 11 cone 1,013), six separate OID/filter groups. These are NOT independently confirmed Gaia/ZTF matches. See the [transport audit](../reports/observational_intake_v1.2/RAW_TRANSPORT_AUDIT.md).
- **Real ZTF science images:** the v1.7 verified run [42058770141](https://github.com/ismaelberja/stellarforge/actions/runs/42058770141) read **12 individual original science FITS pixel arrays**, **two independently different FITS files per OID/band**, 8 for FT Tau and 4 for CIDA 11. Each has provisional celestial WCS/radial-profile image checks; no reference coadd was used as a science epoch. 14 remote requests: 12 success, 2 URLError.
- **Descriptive repeated-epoch proxy:** pairwise differences between the two Gaussian centroid residual vectors within each OID/filter group **0.024–0.097 arcsec**. These are *not calibrated accuracy, physical motions or verified source association*: FITS WCS astrometric residuals and Gaia parallax/covariance remain unknown.
- **Same-field controls:** 90-arcsec cutouts yielded **zero science images with >=2 acceptable unclassified comparison image peaks**. This does not establish an empty field or source cleanliness; no empirical PSF can yet be scientifically calibrated.
- **Image shape:** 11/12 simple Gaussian target fits require residual review; one is provisionally acceptable under the simple model, but no source, binary or physical event is established. High Gaia DR3 RUWE for CIDA 11 (~8.57) remains a serious astrometric-model caution.
- **Scientific confirmations: ZERO:** physical source crossmatches, validated unblended fields, new companions, and real physical variability events all remain unconfirmed.
- **Public project/provenance:** [v1.7 real-image report](../reports/field_controls_v1.7/REAL_MULTIEPOCH_AND_CONTROL_LIMITS.md) and [v1.7 method limitations](PHASE17_SAME_IMAGE_CONTROLS.md). All source photometry and FITS pixels remain outside the public Git history; CI artifacts contain aggregate-only diagnostics.

---

# CURRENT SOURCE ACCESS — v1.6, 5 November 2026

**The following current status supersedes all earlier entries below; historical notes are preserved and must not be read as the latest status.**

- **Official IRSA/ZTF raw transport: completed for two position queries.** FT Tau cone: 1,199 photometric rows across four ZTF OIDs; CIDA 11 cone: 1,013 rows across two OIDs. Original raw SHA-256 hashes are recorded in the [v1.2 transport audit](../reports/observational_intake_v1.2/RAW_TRANSPORT_AUDIT.md), and source-identity evidence in the [v1.3 provisional astrometric report](../reports/astrometry_v1.3/PROVISIONAL_POSITIONS_REPORT.md).
- **Crossmatch identity is not confirmed:** a positional IRSA cone response, even with a close ZTF catalogue position, does not independently identify a Gaia star or exclude blends.
- **Independent Gaia DR3 field checks:** two 15-arcsec TAP cone queries each returned only the target DR3 entry, but no other catalogued Gaia source is not proof that the field is uncontaminated. CIDA 11's RUWE ≈ 8.57 is a major astrometric-fit quality concern; [v1.4 report](../reports/field_review_v1.4/GAIA_NEIGHBOURS_AND_IRSA_IMAGES.md).
- **Real ZTF imaging:** v1.5 validated pixels and header WCS in five of six OID-band groups using three individual science frames and two reference coadds. This is a provisional pixel screen, not a calibrated PSF or confirmed crossmatch.
- **Image-profile fits in v1.6:** three individual FT Tau science images were modeled with a robust single-Gaussian-plus-planar-background **proxy**. All three have substantial positive model residuals; 0 curves had at least two independently usable science images for repeatability. No CIDA 11 profile fit in v1.6; many IRSA requests were HTTP 503. See [real v1.6 audit](../reports/psf_v1.6/REAL_GAUSSIAN_FIT_REVIEW.md).
- **Scientific confirmations remain zero:** 0 verified Gaia–ZTF physical source identities, 0 proven unblended sources, 0 confirmed new physical events or disk classifications. Publisher-original Taurus parent table byte comparison remains open.
- **Public repository data policy:** archived source downloads and transient FITS pixels are not committed; use the authorized original archive and its checksums for reproduction. Public GitHub Actions artifacts contain only summary diagnostics; historical acquisition artifacts have a short retention period.

---

# CURRENT ACCESS STATUS (2026-11-04, v0.8)

- **Taurus catalogue data:** 24 real, provisional coordinate records in a pinned third-party copy of the 532-member Luhman (2023) adopted-members table. The original author's/publisher's file has not been byte-compared to the third-party mirror.
- **Verified raw IRSA ZTF light curves for Taurus:** **0**. No corresponding images or control-star observations have been obtained.
- **Secondary observational-format integration test:** an unrelated third-party public ZTF-style 8-epoch CSV was inspected offline: 6 QC accepted and 2 rejected by cloud/moon bit 15 (32768). Independent identity with the actual IRSA archive has **not** been verified; those data are **not Taurus** and no stellar variability claim is made. The raw third-party file is not included in the deliverable.
- **Time-axis compatibility:** original source examples contain MJD and HJD simultaneously. v0.8 validates the astronomical offset and uses the explicitly prioritized time column without conversion to BJD_TDB.
- **Cadence-only results:** mathematically exact fractions of event start windows containing k observed epochs; they cannot substitute for real-photometry injection-recovery or astrophysical detection completeness.
- The research gates remain source provenance, original IRSA downloads, Gaia/ZTF crossmatch with image checking, independent disk classes, field controls and physically interpretable validation.

---

# CURRENT ACCESS STATUS (2026-11-04, v0.7)

- Pinned third-party **Taurus member catalog copy** structurally checked in earlier phases, 532 member entries / 467 Gaia IDs; 24 positions in the working technical seed. Original publisher-byte comparison still pending.
- The **two-object FT Tau / CIDA 11 pilot** is a request plan built from real catalog coordinates; no ZTF observation timestamps or independent disk classifications have been retrieved.
- Raw original IRSA ZTF curves accessed in this environment: **0**. The source could not be queried because HTTPS/DNS access to IRSA is not available.
- The **528-event v0.7 recovery grid uses synthetic timestamps and magnitudes only**, never real survey cadence. Its diagnostic fractions are not survey completeness or false-positive rates.
- Upstream scientific gates: original table check, actual data downloads with stable hashes, epoch-aware astrometry plus image inspection, field controls and injection/recovery on actual survey observations.

---

# CURRENT ACCESS STATUS (2026-11-04, v0.6)

- The **24-coordinate Taurus technical seed** is derived from a pinned third-party copy of Luhman (2023) Table 2 (532 members, 467 Gaia DR3 identifiers). Its **publisher-byte identity remains unchecked**.
- Real *catalogue* positions and proper motions have been used for an illustrative J2021.0 astrometric displacement calculation, **not for photometric detections**.
- Actual ZTF/IRSA light-curve rows **retrieved in this environment: 0**. An outbound request to IRSA returned a DNS-resolution failure. This remains a technical restriction, not evidence of non-detection by ZTF.
- The 400-trial v0.6 vetting challenge and all example event curves are **fully synthetic**; do not use them to claim real ZTF reliability.
- The next scientific gate is actual IRSA light curves, an observational data release and original-file hashes, per-exposure astrometry, independent control stars, and original-catalog publisher reconciliation.

---

**Historical notes (below):** earlier-phase statements are preserved for reproducibility and should NOT supersede the current status above.

# V0.4 SUPPLEMENT — source access update, 2026-11-04

The following **supersedes the v0.3 statement that no real Taurus catalogue rows were available**. Through an authorized read of a public GitHub repository, we located a third-party copy of Luhman (2023) adopted-members **Table 2** (`ajac9da3t2_mrt.txt`). Its fixed-width rows have been inspected with 532 adopted members, 467 **unique** Gaia DR3 IDs, 65 members without Gaia DR3 IDs, 13 named kinematic groups and 119 empty group values. This agrees with the published paper, but does not establish independent byte equality with the publisher's original file.

Pinned public copy: https://github.com/themariavincent/get_targets/blob/7b6a5c83eca81fc66e50cb4889ee35cb28861367/taurus_sources.txt
Git blob: `fe0d5a43dbd2ca8b867901686ab223a847c649e5`.

24 catalog coordinates have now been extracted, with published line indexes and other metadata, to `data/research_seed`. They are **real source positions** but *not* a final scientific disk-class sample. The complete raw mirror is not stored locally, because outbound DNS from the local container is disabled; a hash-checked downloader is now implemented in `src/stellarforge/luhman2023.py`. A 24-object IRSA query plan has been produced, but **no real ZTF curve has been downloaded**. Details: [Phase 4 technical report](PHASE4_FIRST_REAL_CATALOG_AND_VARIABILITY.md).

---

# Original observational catalogue retrieval — audit status, 2026-11-03

**No original Taurus member list or genuine ZTF light curves have been imported in this development environment.** This restriction remains in v0.3. Automated tests and bundled examples contain **synthetic engineering records only**.

## Bibliography checked

- Luhman, K. L. 2023, *AJ*, 165, 37, DOI:10.3847/1538-3881/ac9da3: **532 adopted Taurus members** in Table 2, **467 Gaia DR3 entries**, **412 Gaia DR3 parallax+proper-motion solutions**, **13 kinematic groups**. This publication defines our Taurus population.
- Cody, A. M., Hillenbrand, L. A. & Rebull, L. M. 2022, *AJ*, 163, 212, DOI:10.3847/1538-3881/ac5b73: published study of variability morphologies in **99 young disk-bearing Taurus members** observed by K2; comparison literature, **not independent ZTF data or proof of new detections**.
- Official ZTF photometry API https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html; flags and `oid` distinctions are corroborated by https://irsa.ipac.caltech.edu/data/ZTF/docs/releases/dr06/src/dr06.html.

## Why the observational input remains blocked

The complete **Luhman (2023) Table 2 machine-readable file** was not retrievable through the research access tools available here. Outbound DNS/networking from the local file-building environment is blocked, so the module was tested with synthetic inputs. A plausible URL, individual star names found in the paper, a Gaia positional cone search or a 532-row mock table **do not constitute** the genuine published census.

**Important:** The author provides machine-readable supporting material, but the exact verified file/release/byte checksum is still unresolved. We should not claim source retrieval or dataset completeness until we can inspect its header, actual contents and row count.

## Safe execution protocol for the next data-enabled stage

1. Secure author/publisher's machine-readable Table 2 (e.g. through the article's published tables). Preserve its original bytes, download URL and SHA256.
2. Audit the original rows, associations and paper-matching counts (532 adopted, 467 Gaia entries). Identify missing/duplicated identifiers and stars without Gaia data.
3. Normalize positions, epochs, source IDs and disk classes with a reviewed mapping; independent literature support is required for disk labels.
4. Freeze a small, prespecified disk-stratified sample **before examining variability**.
5. Download a handful of real ZTF light curves, validate exact output format on each release, then feed the downloaded files to `stellarforge inspect-ztf`.
6. Record successes, non-detections, blends, missing observations and rejected epochs; do not collapse missing and zero-variability cases.

## Result of this iteration

- Implemented an offline ZTF raw-to-normalized processing stage (CSV and fixed-width IPAC table).
- Implemented detailed per-OID/band/time-scale QC, ambiguity flags, retained outliers, and SHA256 consistency checks.
- Implemented an offline CLI command and explicit synthetic fixture to verify the program runs end to end.
- **No actual stellar measurements, light curves, morphology classifications, ML models or new candidates have been produced.**


## Update 2026-11-04: v0.9 observational evidence gate

- Retried the official IRSA ZTF light-curve API for FT Tau and CIDA 11 with `POS=CIRCLE`, two bands and the `32768` quality mask. Both requests failed at the network/DNS level (`URLError`) **without receiving observation bytes**. This says nothing about actual survey coverage.
- The first-target dossiers and static observation-readiness dashboard are in `reports/observational_gates_v0.9/` and are explicitly marked as PENDING.
- The new per-epoch astrometric screen is an approximate engineering aid; real counterpart confirmation and source/image review have not occurred.
- All 303 tests pass. Neither genuine Taurus ZTF light curves nor independent disk labels were acquired in v0.9.