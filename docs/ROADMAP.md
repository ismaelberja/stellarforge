# CURRENT SCIENTIFIC/ENGINEERING ROADMAP — StellarForge v1.19, 10 November 2026

**Synthetic engineering milestone:** [v1.19 empirical star-disjoint PSF and CCD-noise gate](PHASE119_EMPIRICAL_STAR_PSF_AND_CCD_NOISE.md) passed **686/686 automated synthetic and regression tests** ([CI](https://github.com/ismaelberja/stellarforge/actions/runs/42799842210)). A separate empirical PSF fit from >=3 selected training stars, evaluated against >=2 different whole held-out stars from the same exposure, is now implemented. The program includes conservative original ZTF mask, common-grid registration prerequisites and separate diagonal CCD variance/blank-sky correlation diagnostics.

**Critical limitations:** The new v1.19 code has **not yet been run on original real ZTF pixels**. We still have no authenticated per-exposure ZTF DAOPhot PSF training-star roster, no additional validated same-frame 3+2 distinct-source sample, no surveyed gain/read-noise metadata and no independent real PSF/WCS calibration. All real observational conclusions remain those of v1.18 and earlier. Do not call a source independent of original DAOPhot training merely because its Gaia ID differs from previous project inputs.

**Next real-data checkpoint (v1.20):** preregister and expand one original same-exposure FT Tau/CIDA 11 field-star cohort to >=3+2 mutually distinct, well isolated candidates; verify source identity, masks, shared registration, frame metadata and per-exposure gain/read-noise before running the new PSF comparison. Keep the three anomalous v1.16 residual fits in a separate review track and preserve synthetic/real distinction in publication. If this isn't achievable, preserve a transparent v2.0 software-only closeout without implying a calibration or a discovery.

**Estimated remaining:** 1–3 engineering phases to a defensible portfolio v2.0, conditional on tests and docs; science-grade original star-based instrumental verification remains open-ended.

---

# CURRENT SCIENTIFIC/ENGINEERING ROADMAP — StellarForge v1.18, 9 November 2026

**New real-data milestone:** the [v1.18 authentic archived ZTF PSF processing-log and FT Tau exploratory-control evidence](../reports/psf_training_ft_tau_v1.18/REAL_ZTF_LOG_AUDIT_AND_EXPLORATORY_FT_TAU.md) passed **661 automated tests** in [GitHub Actions](https://github.com/ismaelberja/stellarforge/actions/runs/42665465964). The original four dated FT Tau/CIDA 11 science frames supplied **8 of 8** original public `sciimlog.txt`+`log.txt` reduction files, with 115–116 PSF/DAOPhot-referencing lines per science-processing log, **but zero authenticated original source-specific DAOPhot PSF training-star rosters**. Fitted native `psfcat.fits` source rows are not a list of model-construction training stars.

**FT Tau sample:** a new 50-row original Gaia DR3 wide-cone fetch again yielded **zero** additional strict-quality isolated field stars under unchanged v1.17 thresholds. The separately **predeclared exploratory** Gaia quality and isolation tier selected **four** previously unused FT Tau DR3 source IDs, three sky quadrants represented. In the two historic original ZTF FT Tau g-band science epochs, only **one distinct new Gaia candidate (DR3 149623298952568064) yielded two WCS-aligned genuine science/mask source-pixel DAOPhot PSF fits**, passing provisional same-star checkerboard pixel residual QA with RMS/sky MAD ratios **0.920302** and **0.955383**. Six other source×epoch native PSF catalogue candidate screens failed eligibility/review and were not fitted. **32** fixed shifted-sky positions had zero native PSFcat detections within 1″; no source false-match probability can be inferred.

**Important limitations:** One source observed twice is **not two distinct stellar controls**, and a looser exploratory Gaia stratum is not scientifically interchangeable with the original strict clean-star sample. Genuine membership exclusion from ZTF's native PSF training remains unverified even after reading all eight public reduction logs. No physically authenticated Gaia–ZTF IDs, independently calibrated PSF/WCS errors, unblended companions or physical stellar variability has been proven.

**Prioritized next v2.0 software/science milestones:**
1. **Truly independent PSF model construction/validation:** obtain documented per-exposure original ZTF DAOPhot training-star IDs and coordinate mapping, or construct a fresh PSF from an independently registered source training set while retaining genuinely different held-out stars and explicitly modeling source selection.
2. **Original multi-epoch science source control sample:** expand beyond the four historic g-band frames and one new FT Tau exploratory Gaia star. Keep preregistered strict vs exploratory source selection tiers distinct; seek more Gaia/ZTF stars across fields, filters, detectors and sky quadrants without retrospectively tuning source-quality thresholds to desired residuals.
3. **Realistic detector pixel and WCS covariance:** gain/read-noise, Poisson sky/star variance, resampling/correlations, detector mask, spatial PSF interpolation/seeing and chromatic/refraction systematics, true exposure midpoint and Palomar topocentric apparent place. Test independently selected distinct real stellar source/epoch residuals before claiming instrumental astrometric precision.
4. **Physical source identity and residual investigation:** rigorously identify Gaia/ZTF physical crossmatches across independent datasets, assess false associations, and review the three v1.16 high-positive-residual objects at several original dates and bands. Unknown PSF/crowding/nebular effects must be excluded before any astrophysical variability or companion claim.
5. **Engineering portfolio v2.0 closeout:** versioned artifact/public source provenance, complete CI, reusable CLI/API, quality audit, unit/synthetic integration tests, user-friendly Spanish/English docs and properly bounded source ownership/copyright. A v2.0 **software** release is possible with clearly described calibration/data limitations even if no discovery is made.

**Planning estimate:** roughly **2–4 more phases after v1.18** could reasonably close a strong documented v2.0 research-software portfolio if external source/PSF validation remains tractable; science-grade instrument calibration or discovery confirmation is not guaranteed by a version number or schedule.

**Public Git remains aggregate-only**; original Gaia/IRSA source CSV, original ZTF science FITS/masks, PSF catalogue raw rows, DAOPhot coefficients and raw pipeline logs stay transient. Previous roadmap sections retained below for audit.

---

# CURRENT SCIENTIFIC ENGINEERING ROADMAP — StellarForge v1.17, 9 November 2026

**Latest real milestone:** [v1.17 new Gaia-source-disjoint original ZTF observations](../reports/new_gaia_holdouts_v1.17/REAL_DISJOINT_GAIA_CONTROL_AND_SHIFTED_SKY_RESULTS.md) with [636 automated tests passing](https://github.com/ismaelberja/stellarforge/actions/runs/42661663983). Fresh **independent Gaia DR3 210″** field-cone queries contained **50 FT Tau** and **250 CIDA 11** Gaia records. All ten previously used Gaia target/reference IDs were excluded before seeing ZTF native source profiles or science-image pixels; the preregistered Gaia-only quality, nonduplicated astrometric-source, 10″ all-Gaia-neighbor isolation, G flux/SNR and RUWE rules yielded **no FT Tau new candidates** and **20** CIDA 11 quality survivors before a four-star sky-quadrant sampling budget.

**New source test outcome:** **four genuinely new Gaia DR3 IDs** (distinct from v1.8–v1.16 targets/references) cover four sky quadrants around CIDA 11. Across **two historical original CIDA 11 g-band science exposures**, **six of eight** new source×epoch candidates yielded genuine original `sciimg.fits`+`mskimg.fits` WCS-aligned masked native PSF pixel fits. **All six passed provisional same-image held-out pixel/residual QA**. Two additional source×epoch combinations failed native ZTF catalogue source-profile eligibility, not physical sky detection. Four fits on the first CIDA 11 science date supported a descriptive same-image residual/annular-sky MAD median **0.98091**; only two passed on the second date, correctly below the three-distinct-source minimum for reporting that exposure's median. **Thirty-two deterministic ±25″ shifted-sky source proximity probes had no native ZTF PSF catalogue hit**, which is a local-density diagnostic, **not a calibrated source false-match probability**.

**Critical scientific non-independence:** new Gaia IDs were not used by earlier *StellarForge* source-pixel code, but their membership in the **actual native ZTF DAOPhot PSF-training star sample is unknown**. A source's good native PSFfit shape or original masked science-pixel residual does **not** establish a PSF validated on a star independently withheld from the original survey model construction. Gaia–ZTF physical source associations remain provisional. CIDA 11 has high Gaia RUWE; FT Tau has **zero** new selected control stars under the preregistered filters.

**Prioritized next milestones:**
1. **Verify original ZTF DAOPhot training-star membership** using true native PSF-support products if accessible, or a completely independent PSF reconstruction from distinct preselected Gaia stars. Without this, do **not** advertise v1.17 as independent instrumental PSF error calibration.
2. **FT Tau source-control sample coverage:** register new justified sampling strata or additional ZTF exposure fields/bands *before* seeing CCD residual outcomes. Distinguish quality-filter ineligibility from the astrophysical absence of stars. Preserve both sample selection counts and exclusions.
3. **Physically characterized pixel error model:** per-original exposure CCD calibration, read noise/gain/Poisson, ZTF spatial variance and correlated noise; sky nebulosity, color, saturation, masked defects, full detector phase/WCS and PSF interpolation uncertainties. Validate using genuinely distinct instrument model training/holdout stars.
4. **Independent source identification and WCS validation:** compare Gaia DR3 complete 5D covariance and non-single-star effects (CIDA 11 RUWE), original exposure midpoints and Palomar topocentric/chromatic corrections, source crowding and original native ZTF catalogue identity across distinct dates and filters. Quantify held-out field-source instrument residuals, not merely Gaia/catalog nearest offsets or same-pixel chessboard metrics.
5. **Broader observational cross-validation:** expand beyond four historical original g-band science exposures and two technical targets, inspect the three original v1.16 positive-residual source cases at distinct true epochs and filters with genuinely independent image/source evidence, and validate Taurus publisher source table and source-selection completeness. Never infer stellar/substellar companions or physical variability from unmodeled residual peaks.
6. **Reproducible project closeout:** consolidate source manifest/training provenance, versioned documentation, tests, CI, ethics and non-licensed source archive rights; release only code, synthetic test fixtures, source hashes and derived quality metrics in Git, while original ZTF/Gaia raw data remain in private temporary environments.

**Estimated remaining engineering/science milestones to a strong v2.0 portfolio release:** roughly **3–5 further phases after v1.17** if archived calibration metadata and suitable comparison stars can be obtained. This is a **project planning estimate, not an astronomical verification guarantee**; real discovery-level science could require substantially more data or remain inconclusive indefinitely.

**Zero independently authenticated Gaia–ZTF physical matches, confirmed astrophysical companions, complete external source PSF/WCS error calibrations or physical variability events.**

---

# CURRENT SCIENTIFIC/ENGINEERING ROADMAP — StellarForge v1.16, 8 November 2026

**New verified real-data milestone:** [v1.16 original ZTF masked science-pixel PSF residual evidence](../reports/masked_spatial_psf_v1.16/REAL_ZTF_PIXEL_RESIDUALS_EVIDENCE.md) confirms **614 passing tests**, original SHA-audited 2,212-row IRSA acquisition, 4/4 original PSF catalogues, 4/4 native DAOPhot models and **16/16 original science `sciimg.fits` + detector `mskimg.fits` source-pair cutouts** retrieved and WCS-registered. Original full-detector catalogue subpixel phases agree with source cutout WCS. **All sixteen** masked native spatial PSF/sky-plane DN fits completed, **thirteen** provisional same-image checkerboard residual screens pass and **three** require review for elevated positive peaks. **Zero** HTTP 503 in this successful observed-data run.

**Scientific status:** this is the first genuine same-dated source-image pixel/mask spatial-PSF residual fit, not independently calibrated stellar photometry, WCS, PSF accuracy, or Gaia–ZTF physical source association. The 13/16 pass fraction is a conditional software metric among **already prescreened candidate sources**, not an estimated astrophysical success probability or binary incidence. The positive residuals in FT Tau/CIDA 11 remain ambiguous because PSF interpolation, nebular sky, source position, correlated image noise and astrophysical blending may all produce excesses.

**Next science and software priorities:**
1. **Independent stellar field-star holdout:** select and authenticate a spatially representative sample of additional original ZTF PSF-fit detections and Gaia DR3 source IDs, independently of the four source models' existing selection; withhold **different real stars** (not just source image checkerboard pixels) from model tuning. Establish source-neighbor and false-association controls.
2. **Physical image error model and original detector masks:** use genuine `sciimg.fits` plus matching `mskimg.fits` over additional dates/bands and vetted independent stars to derive realistic pixel variance (read noise/gain, Poisson, resampling/correlation, sky-nebulosity gradients), PSF interpolation/model-position sensitivity, source saturation, crowding, cosmic rays, bad pixels and systematic chromatic effects.
3. **Held-out WCS/PSF calibration:** independently compare native ZTF detector `xpos/ypos` and Gaia catalogue positions at verified ZTF exposure midpoints/topocentric apparent places, incorporating Gaia full correlated 5D covariance, CIDA 11 high RUWE, color/refraction and spatially variable instrument distortions. Use independent stars and actual measured residual/error distributions; do not call same-image pixel holdouts absolute PSF/WCS accuracy.
4. **Three flagged real source profiles:** examine original dated FT Tau target MJD 58491.184780, CIDA 11 target MJD 58849.135984 and Gaia reference candidate `3419111520318480128` at MJD 58849.135984 in multiple independent original exposures and against real neighboring source catalogs. Do not assume a companion, variability or astrophysical anomaly.
5. Broaden beyond four original g-band science exposures to original six ZTF OID/filter groups and additional independent dates, checking original publisher Taurus sample provenance, source selection completeness and physical variability hypothesis without post-hoc cherry-picking.
6. Keep original ZTF science/mask FITS arrays, spatial DAOPhot lookup coefficients, original native `psfcat` binary tables, Gaia TAP and IRSA raw photometry transient and outside Git/Actions public artifacts; only release source code, synthetic tests, source SHA-256 and derived numerical status summaries.

**Unverified:** actual physical Gaia–ZTF source identities; independently measured source-local empirical PSF accuracy; calibrated astrometric detector WCS errors/photometric magnitudes; real stellar companions or physical time-domain variability events. Historical milestone detail is retained below.

---

# CURRENT SCIENTIFIC AND ENGINEERING ROADMAP — StellarForge v1.15, 8 November 2026

**New verified milestone:** the actual [v1.15 original ZTF DAOPhot spatial PSF reconstruction](../reports/spatial_daophot_v1.15/REAL_DAOPHOT_CENTER_AND_LOCAL_SHAPES.md) succeeded with **590 automated tests**, **4/4 original `sciimgdao.psf` ASCII native spatial lookup models decoded** and **4/4 original archived science-field-center `sciimgdaopsfcent.fits` model comparisons passed** with cosine similarity ≥0.999999 and normalized L1 0.000278–0.000984. All four native Gaussian models have **three 47×47 half-pixel lookup correction tables** and generate **23×23** approximate model PSFs. **Sixteen** provisional original `psfcat` source detector positions from v1.14 received an evaluated spatial PSF model shape.

**Interpretation:** native center FITS images are derived from the **same DAOPhot processing system** as the spatial models. Very close agreement verifies reconstruction/model-file interpretation, **NOT** independent local empirical PSF, calibrated instrumental astrometry, source identification, photometric precision, or physical variability. The numerical interpolation (SciPy cubic B-spline for DAOPhot spatial corrections) is explicitly an approximation rather than a proven bitwise-exact native DAOPhot routine. The high-RUWE CIDA 11 source and original Gaia-to-ZTF positional associations remain provisional.

**Next primary science gates:**
1. **Real pixel-residual verification:** on the original same-dated ZTF single-science `sciimg.fits` cutouts, retrieve corresponding original `mskimg.fits` pixel-mask maps, verify original detector/WCS registration and time conventions, evaluate source-local spatial PSFs including proper subpixel phase, and fit only amplitude/background to actual **independently vetted stellar field controls**. Validate residual morphology and sky-nebulosity/CCD-mask contamination, do not assume the native source counter is a physical Gaia crossmatch.
2. Independently authenticate field stars and their Gaia/ZTF physical IDs, including full catalogue quality, colour, saturation, crowding/non-Gaia neighbors, exposure metadata, and uncertainty in geocentric/topocentric apparent-place positions. Use spatially representative **held-out** stars for quantitative PSF and WCS error model validation; original field v1.13 mask coverage was just four reference cores and zero target cores.
3. Determine genuine image-level instrumental/PSF centroid and sky-background errors, with detector distortion, correlated noise, atmospheric/PSF color dependence and source-model systematics. The small holdout RMS and `psfcat` nearest-neighbor separation are **not** independently calibrated astrometric precision.
4. Extend source-verified calibration beyond only four g-band original science dates to original six ZTF OID/passband groups and independent valid epochs; validate the publisher Taurus stellar sample and injection/recovery/selection before physical variability or companion claims.
5. Keep all raw original ZTF/Gaia FITS, native DAOPhot coefficient tables, PSF-source catalog rows, source photometry and potentially copyrighted survey datasets in ephemeral controlled environments; public Git gets only code, tests, numeric aggregate evidence, source SHA-256 provenance and scientifically cautious reports.

**Not confirmed:** any independent Gaia–ZTF source identity, local source PSF validated against masked real stellar image pixels, independently held-out detector WCS/PSF uncertainty, binary companion, or physical variability event. Prior roadmap sections remain below for historical audit.

---

# CURRENT SCIENTIFIC AND ENGINEERING ROADMAP — StellarForge v1.14, 8 November 2026

**New verified milestone:** real [v1.14 native original ZTF PSF-catalogue and Gaia screening evidence](../reports/native_psfcat_v1.14/REAL_ZTF_GAIA_PSF_CATALOGUE_EVIDENCE.md), **564 automated tests passed**, and all four original `psfcat.fits` native PSF-fit FITS catalogues retrieved for two distinct dated original g-band exposures in each FT Tau/CIDA 11 technical field. The four catalogs contain **27,207 native PSF-fit detections**, and all **four native spatial `sciimgdao.psf` files** were also downloaded and SHA-provenanced. No native spatial DAOPhot model was decoded/evaluated at any source position.

**Preregistered exact-source screening:** each of twenty Gaia DR3 target/reference predicted positions was compared with the independent ZTF original native PSF-fit detection coordinates, `chi`, `sharp`, SNR and source pixel flags. **Sixteen** unique nearest ≤1″ candidates passed provisional quality screening, **three** required low-`chi` model review, **one** FT Tau reference had no nearby PSF catalog row. The sixteen provisional angular offsets are **0.032641″–0.345256″ (median 0.1258465″)**. These offsets are *not* a validated physical source crossmatch, instrumental WCS precision, companion signal, or true proper motion. The CIDA 11 astrometric high RUWE warning remains.

**Next scientifically justified work:**
1. **Decode/evaluate original ZTF `sciimgdao.psf` spatial DAOPhot lookup table** at the native CCD-quadrant `xpos/ypos` of source candidates in `psfcat.fits`. Verify exact model format, coordinate conventions, normalization and spatial terms rather than treating the field-center 23×23 image as a local PSF.
2. Use original same-dated `sciimg.fits`, `mskimg.fits` and source-specific PSF predictions to compare masked real image residuals, deblend/crowding alternatives and source-specific flux/centroid uncertainty. v1.13 aligned masks existed only for four reference-source cutouts, not targets; source catalogue `flags` do not replace full pixel-mask verification.
3. Establish true **independent** Gaia/ZTF source association on spatially distributed field stars, with catalogue source quality, astrophysical morphology, 2018–2020 position epoch, known high RUWE, color terms, actual observing-time/Palomar apparent-place corrections and non-Gaia contamination. Estimate error budget and false-match rate, not merely matching radii.
4. Build a detector WCS/PSF local astrometric model trained on some authenticated reference stars and independently tested on **separate withheld sources**, with realistic correlated PSF/WCS/systematic noise and observational metadata. Only after this gate may instrumental precision be asserted.
5. Expand to all historic six OID/filter groups and representative independent image epochs, and validate the original publisher Taurus table, source selection/injection recovery and astrophysical variability hypotheses before any population results.
6. Retain original raw Gaia TAP, ZTF positional-cone photometry, `psfcat.fits` tables, original science/mask FITS pixels and native DAOPhot bytes in ephemeral controlled environments. Public Git publishes code, reports, reproducibility hashes and **derived aggregate metrics only**.

**Unconfirmed:** independently authenticated Gaia–ZTF physical associations, actually evaluated local spatial PSFs, calibrated instrument WCS/PSF errors, discovered stellar/substellar companions or confirmed physical variability events. Historical milestones are preserved below.

---

# CURRENT SCIENTIFIC AND SOFTWARE ROADMAP — StellarForge v1.13, 8 November 2026

**Implemented and verified:** 533 automated regressions; original 2,212 ZTF positional-cone photometry rows with source hashes; genuine science FITS from original dated exposures; Gaia DR3 ten-source five-parameter formal correlated astrometry and first-order annual geocentric parallax; independent-code Gaussian/aperture centroid-model comparisons; and now **original ZTF instrument bad-pixel masks and native science-field-center PSF stamps**.

**Actual instrument result:** the [observed v1.13 ZTF mask/PSF audit](../reports/original_masks_psf_v1.13/REAL_ZTF_MASK_AND_NATIVE_CENTER_PSF_EVIDENCE.md) attempted 20 original target/reference source locations on four dated science exposures. Four Gaia candidate reference source masks and same-dated science FITS pixels were jointly accessible with exactly aligned celestial WCS mapping and no documented 6141 bad bits or saturation flags in nominal 4.5-pixel source apertures. **All 4 target source masks and 12 other reference masks were unavailable (HTTP 503)**, so target-source instrumental contamination cannot be assessed. **Across two runs on the same four historical exposures, all four distinct real 23×23 `sciimgdaopsfcent.fits` center-of-field PSF stamps were accessed and parsed** (two on each run, complementary exposure IDs). The first run validated four reference masks; **the repeat had HTTP 503 for all 20 paired mask/science attempts**, showing archive availability is unstable. These stamps are not local source-specific empirical PSF calibrations.

**Next primary research gates, in priority order:**
1. Retrieve/interpret original **spatially varying `sciimgdao.psf`** or **`psfcat.fits` source extraction catalog** at exact same-date/detector coordinates, using independent Gaia source associations and mask-valid image samples. The field-center stamp alone does not give a PSF at an arbitrary source location.
2. Establish a spatially representative source-control sample with vetted Gaia/ZTF crossmatches, detector saturation/bitmask histories, morphology, crowding and non-Gaia neighbors. Strong Gaia RUWE (~8.57 for CIDA 11) needs a separate astrometric model.
3. Fit and **independently test** a per-exposure detector WCS/PSF distortion and source centroid-error budget on held-out reference stars, including true time scale, topocentric geometry/aberration/refraction, Gaia covariance and correlated CCD/PSF bias terms.
4. Repeat on representative dates and all six original ZTF OID/filter groups; assess injection/recovery, background/nebulosity alternatives, source identity, astrophysical selection and original Taurus publisher catalogue before physical events or companion claims.
5. Publish only verified code, methods and **derived aggregates** in public Git; retain raw ZTF FITS, masks, PSF pixels, photometry and Gaia TAP CSV solely in ephemeral controlled environments.

**UNVERIFIED:** physical Gaia–ZTF source IDs, authenticated single/unblended stars, local empirical PSFs, calibrated instrumental WCS uncertainty, new stellar companions and physical variability events.

---

# CURRENT SCIENTIFIC AND SOFTWARE ROADMAP — StellarForge v1.12, 8 November 2026

**Completed engineering work:** 506 passing automated tests, verified 2,212 ZTF positional-cone records, real FITS/WCS checks of original science frames, independent Gaia DR3 five-parameter formal covariance and annual geometric parallax for both technical targets and eight candidate references, and now a **real-original-FITS pixel remeasurement audit with a new sky-plane-corrected aperture centroid compared against the original constrained Gaussian model**. [Read the original-image observational evidence](../reports/real_fits_v1.12/REAL_TWO_CENTROID_MODEL_QA.md).

**Key scientific finding:** two 20-request audits were completed on the same original ZTF science epochs, revealing intermittent IRSA HTTP 503 archive availability. In the **final run**, eight HTTP 503 and **12 complete dual-centroid image screens** (1 target, 11 Gaia references) produced **9 provisionally model-consistent candidate references**, with median Gaussian/aperture centroid separation **0.104720″**. The CIDA 11 MJD58475 exposure had four reference candidates with Gaussian/aperture internal LOO RMS **0.064675″ versus 0.155762″**, although the target FITS was inaccessible. The four FITS files available in both runs had identical SHA-256 bytes. These figures measure estimator/reference-sample sensitivity on shared pixels, **not calibrated instrument astrometry, source motions or independent observing epochs**. Only one of four exposure groups had enough cross-model references.

**Scientific priority for next phase:**
1. Retrieve the **official IRSA ZTF matching `mskimg.fits` bad-pixel bitmask** and native `sciimgdao.psf`, `sciimgdaopsfcent.fits` / `psfcat.fits` products for the same dated science exposure IDs, under a fixed request budget. Decode appropriate flag semantics, WCS alignment and PSF model provenance rather than assuming `sciimg.fits` by itself proves a clean detector. See [IRSA product metadata](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html).
2. Use a larger, independently vetted sample of spatially distributed Gaia/ZTF field stars, with catalogue cross-identification and physical morphology/crowding checks, to fit and test detector-dependent empirical PSF and WCS distortion. Preserve *held-out* stars not used in the model.
3. Verify ZTF header epoch/time convention and full topocentric/aberration/refraction corrections, source-specific Gaia 5D covariance and high-RUWE CIDA 11 model reliability, without confusing formal Gaia catalogue errors with actual imaging errors.
4. Extend only verified, mask-checked calibration to all original six OID/filter groups and representative independent epochs, quantifying selection/injection-recovery and alternative physical explanations before any variability/discovery claim.
5. Keep public artifacts **derived aggregate only**; never publish original ZTF light curves/FITS pixels or Gaia TAP raw catalogues without a separate verified provenance/rights review.

**Still unconfirmed:** independently authenticated Gaia–ZTF source identities, clean isolated stellar PSFs, calibrated instrumental astrometric uncertainties, newly discovered companions and physical variability events. Historical sections below are retained for audit traceability.

---

# Current research/engineering roadmap — StellarForge v1.11 (6 November 2026)

**Verified:** 484 automated tests, 2,212 real ZTF positional-cone photometric rows, 12 separate ZTF FITS science exposures across the original six OID/passband groups, eight Gaia DR3 candidate controls with 13 real FITS image-model fits, 5D formal Gaia source covariance for all ten v1.11 targets and references, and individual Earth-geocentric annual parallax corrections at four historical ZTF science epochs. [Real Gaia reference parallax sensitivity report](../reports/reference_parallax_v1.11/REAL_GAIA_REFERENCE_PARALLAX_LOO.md).

**Critical result:** Including each reference's annual parallax changes the strict internal leave-one-reference-out RMS from 0.075782″ to 0.075770″ (FT Tau) and from 0.093046″ to 0.092971″ (CIDA 11), only **0.012 / 0.075 mas**. The original reference-image disagreement therefore remains largely unexplained by this correction. Only two of four original reference-field exposures retain enough high-quality Gaussian models. These RMS values are NOT physical motion, an instrument calibration, PSF error bars or source identities.

**Next scientific gates:**
1. Obtain an independently vetted, spatially representative pool of genuine same-detector ZTF field stars; check saturation/crowding, image masks, colour and fitted PSF wings rather than trusting Gaia RUWE/brightness alone.
2. On raw FITS science exposures, independently calibrate WCS distortion, detector-dependent PSF and astrometric residuals with **held-out** reference stars not used to fit the astrometric model; estimate repeatable uncertainty budgets and correlated systematics, not simply internal scatter.
3. Verify original exposure timing, observer location and topocentric aberration/refraction/atmospheric colour effects. The Gaia v1.11 5D covariance is **catalogue-formal** and cannot automatically replace ZTF instrumental uncertainty.
4. Independently confirm Gaia–ZTF source IDs, including high-RUWE CIDA 11 (RUWE ≈ 8.57), and review field contamination/non-Gaia sources.
5. Validate the original Taurus publisher membership catalogue, disk classes, selection function and real-cadence injection/recovery before any astronomical variability/companion claim.

**Not confirmed:** isolated empirical PSFs, independently calibrated ZTF WCS, physical Gaia–ZTF source identities, newly discovered companions or astrophysical events. Retain public Git only for code and vetted derived aggregate evidence, not raw third-party photometry or FITS images.

---

# CURRENT RESEARCH/SOFTWARE ROADMAP — v1.10 (6 November 2026)

**Verified science-software milestone:** 468 automated tests; original real ZTF positional-cone photometry and FITS screen, Gaia DR3 formal 5D/annual parallax modeling for two target sources, and now a **reproducible leave-one-Gaia-reference-out image-offset quality audit** of the original v1.8 derived 13 reference fits (four dated ZTF g-band science frames). A small derived summary with the historic original aggregate SHA-256 is versioned to survive time-limited external workflow artifacts.

**Critical observation:** 3/4 frames have at least three inclusive candidate reference image models; only 2/4 retain at least three *non-flagged* Gaussian image models. FT Tau MJD58491 has holdout disagreement RMS ~0.076 arcsec, CIDA 11 MJD58475 ~0.093 arcsec. CIDA 11 MJD58849 falls from five inclusive to two strict references: **no strict holdout inference**. These values are internal disagreement, not ZTF absolute WCS calibration errors or verified source matches. [Real reference holdout evidence](../reports/holdout_v1.10/REAL_REFERENCE_HOLDOUT_EVIDENCE.md).

**Next science gates:**
1. Independently authenticate reference stars using Gaia catalogue and ZTF image morphology, saturation/crowding masks, PSF quality, color and other surveys. More stars per field, unbiased spatial sampling and vetted original science frames are needed.
2. Recompute Gaia **each reference star** position with its own full five-parameter formal covariance, annual parallax and source quality at precise FITS timing; the v1.9 model covered only the two targets.
3. Estimate an independent real detector WCS/PSF and background error budget, including correlated distortions, systematic/measurement errors, and checks outside any fit/control selection.
4. Resolve high CIDA 11 RUWE (~8.57), source multiplicity alternatives, Gaia/ZTF source identity, the publisher Taurus catalogue and real-time-domain injection/recovery before physical variability claims.
5. Keep external raw ZTF FITS/light curves and Gaia TAP CSV outside public Git; preserve only verified derived aggregates, immutable provenance and tests.

**Still unconfirmed:** physical Gaia–ZTF source identifications, isolated empirical PSFs, independently calibrated image WCS, new companions or physical variability events.

---

# CURRENT SCIENTIFIC & SOFTWARE ROADMAP — v1.9 (6 November 2026)

**Implemented and validated:** 444 offline tests; original 2,212 SHA-checked ZTF positional-cone photometry rows; 12 actual distinct ZTF science FITS observations across six OID/passband groups; eight Gaia DR3 catalogue quality-screened instrumental reference candidates with 13 real ZTF image-model fits; three provisional local median WCS shift estimates; **new v1.9 exact-source Gaia DR3 5×5 formal covariance including all ten correlations and epoch-dependent Earth-geocentric annual parallax** at four original ZTF observation dates. See [real v1.9 astrometry report](../reports/gaia_formal_v1.9/GAIA_COVARIANCE_AND_ANNUAL_PARALLAX.md).

**What is NOT validated:** independent physical Gaia–ZTF source IDs, unblended stellar PSFs, detector astrometric WCS, uncertainty-calibrated individual ZTF centroids, six-parameter pseudocolour modeling, Gaia radial velocity/perspective acceleration, observatory aberration and refraction, source multiplicity, astrophysical variability event counts.

**Next defensible steps:**
1. Authenticate instrument PSF reference stars using independent classification, detector quality flags, calibrated magnitudes, WCS accuracy and image morphology; the v1.8 candidate Gaia stars are **not yet empirically calibrated PSF standards**.
2. On actual dated science images, independently model the detector distortion and image-specific PSF/WCS/background error contributions. Combine those with **Gaia's v1.9 formal covariance** in a calibrated, uncertainty-aware comparison, never pretending the catalogue covariance includes instrument or high-RUWE source systematics.
3. Verify the ZTF exposure time-scale in raw FITS headers; account for observer velocity/aberration, parallax, full Gaia radial/perspective motion where available. Treat **CIDA 11 RUWE ≈ 8.57** as an explicit source-model reliability warning.
4. Extend only the validated method to all six ZTF OID/bands and multiple original science dates. Use controls, image masks and injection/recovery before an astronomical source identity or any real variability/companion claim.
5. Verify the publisher-original Luhman (2023) table, disk classifications and selection biases. Continue minimal public aggregate results, no raw third-party Gaia/ZTF source downloads or FITS pixel matrices in public Git.

**Science confirmations remain zero:** new physical companions, resolved blends, authenticated Gaia–ZTF sources or astrophysical variability events.

---

# Current research/engineering roadmap — v1.8, 5 November 2026

**New verified research-software milestone:** 422 automated tests; two original SHA-checked IRSA positional cone queries (2,212 rows); six ZTF OID/filter groups with two independent usable science images apiece (v1.7); **independent Gaia DR3 210-arcsec reference selection** (50 FT Tau + 250 CIDA 11 catalogue sources), **eight conservative candidate references**, 13 measured same-ZTF-science-product reference cutouts and three provisional signed WCS translation proxies (v1.8). These are **neither independently calibrated PSFs/WCS nor confirmed stellar source identities**. See the [real v1.8 report](../reports/gaia_reference_v1.8/REAL_REFERENCE_CANDIDATE_EVIDENCE.md).

**Priority next scientific work:**
1. Validate Gaia-selected candidate reference stars using catalogue cross-checks, morphology, saturation and field/filter-specific instrumental PSFs. Quality-screened Gaia entries are not guaranteed isolated ZTF PSF standards.
2. Perform independently controlled multi-source WCS distortion/shift and uncertainty calibration with robust matching, proper error propagation and full Gaia parallax, correlation and covariance terms. High CIDA 11 RUWE (about 8.57) demands scrutiny.
3. Evaluate background, detector masks, colour PSF mismatch, nebular emission and blending before claiming clean stellar measurements. Extend limited one-g-band-per-target pilot to the remaining ZTF OID/filter groups and multiple science epochs.
4. Independently verify the publisher-original Luhman (2023) membership table, disk classes and source IDs, then validate real photometric variability/selection efficiency with field stars and injection/recovery.
5. Maintain fail-closed acquisition, input SHA-256 provenance and **no publication of raw third-party Gaia/ZTF CSVs or FITS pixel arrays**. Numerical precision of offset reports is not calibrated astrophysical measurement accuracy.

No new physical companions, source crossmatches, stellar disk classifications or physical variability events are confirmed.

---

# Research/engineering roadmap — CURRENT v1.7, 5 November 2026

**Completed engineering work:** reproducible official IRSA raw transport (2,212 SHA-checked ZTF rows), provisional Gaia–ZTF positional and Gaia DR3 field screens, five image cutout screens in v1.5, preliminary Gaussian proxies in v1.6, **twelve real and distinct science FITS images (two per OID/filter) in v1.7**, all with bounded celestial WCS/shape screening, synthetic regression coverage and **400 passed tests**. Read the [v1.7 observational report](../reports/field_controls_v1.7/REAL_MULTIEPOCH_AND_CONTROL_LIMITS.md).

**New critical observation:** no v1.7 90-arcsec science frame had two usable **unclassified** same-field image control peaks, so empirical instrumental PSF calibration is NOT completed. The small pairwise centroid residual differences are only descriptive; Gaia source identity, independent WCS error and unblended photometry remain unverified.

**Priority scientific gates (all open):**
1. Authenticate one or more field stars from catalogued/imaged sources in each ZTF field; if necessary query larger official image products under a controlled request plan. Distinguish extended nebulae, galaxies, saturation and unclassified maxima; do not silently treat brightness peaks as stellar controls.
2. Estimate **empirical field-variable PSFs**, masks and source/background residuals with valid controls. A single-Gaussian target-model residual does not imply a physical companion.
3. Use the now-available independent science frames for **calibrated** multi-epoch comparisons with WCS recalibration, centroid errors, full Gaia proper-motion/parallax/covariance, realistic correlated instrument systematics and absolute time definitions.
4. Resolve CIDA 11's unusually high Gaia DR3 RUWE and alternative/non-Gaia neighboring sources. **No Gaia–ZTF physical identity confirmed.**
5. Verify the original Luhman (2023) publisher membership dataset, independent disk classifications, external field reference stars and real-cadence injection/recovery before estimating detection sensitivity, incidence or a physical event rate.

**Public repository:** GitHub can be shown on a CV now; code and findings are versioned for transparent research-software review, with individual third-party ZTF CSV and FITS pixel arrays kept outside Git. This supersedes earlier milestone roadmaps below, which remain historical.

---

## Current research/engineering roadmap — v1.6 (5 November 2026)

**Engineering milestone implemented:** 387 automated tests, acquisition of 2,212 original IRSA ZTF position-query records with source hashes, cautious per-epoch positional screening, independent Gaia DR3 15-arcsec field-neighbour checks, real FITS/WCS pixel access and single-Gaussian image-profile proxies for three FT Tau science exposures. See the [current status](PROJECT_STATUS.md), [v1.5 real FITS audit](../reports/real_fits_v1.5/PIXEL_WCS_RESULTS.md), and [v1.6 Gaussian-profile real-image audit](../reports/psf_v1.6/REAL_GAUSSIAN_FIT_REVIEW.md).

**Science gates still open (do not claim completed from a software test):**
1. Independently verify Gaia–ZTF stellar identity using realistic Gaia full astrometric uncertainties, image calibration and source alternatives; CIDA 11 has very high RUWE.
2. Compare targets with **same-field empirical PSFs**, spatially varying image backgrounds, instrumental masks and WCS residuals. A simple single-Gaussian residual is not evidence of a physical companion.
3. Obtain at least two independent and valid dated science exposures within an OID/filter. Temporary HTTP 503 archive errors must not be treated as absence of coverage; reference coadds do not count.
4. Verify the publisher's original Luhman (2023) membership table, independent disk classes and source sample selection before any occurrence-rate estimate.
5. Quantify real-cadence sensitivity with vetted comparison stars, injection/recovery and uncertainty budgets before any physical variability discovery or period/incidence claim.

**External/public code:** repo is public for software portfolio inspection. Raw photometric CSV and FITS image pixels are not committed to Git; only vetted aggregate results are added. This roadmap remains historical below so earlier phases can be understood in context.

---

## Current v0.8 milestone and next scientific gate

- v0.8 is complete as a **technical research phase**: offline secondary ZTF-format compatibility, dual-clock MJD/HJD fix, exact event-start cadence geometry, 24-source readiness ledger, and 239 passing tests. **Zero verified Taurus ZTF photometric curves and zero physical discoveries.**
- v0.9 scientific gate: retrieve original IRSA ZTF observations for FT Tau / CIDA 11, compare the pinned Luhman source table against its publisher form, perform exact observation-epoch Gaia astrometry and crowded-field review, establish independent disk labels and run true observed-cadence injections. This cannot be claimed complete from test fixtures or third-party secondary examples.

# Research & engineering roadmap — phased, not rushed

This is a *multi-stage* project. Finishing a code file is not equivalent to passing the corresponding scientific review gate. Each sprint records open questions and decisions from Ismael as scientific owner. If data access or assumptions fail, revise the protocol rather than hiding the failure.

## Stage 1 — Scope and scientific protocol [FOUNDATION COMPLETE; DATA GATE OPEN]

- [x] Choose joint goal: astronomy + employable data-engineering/ML skills.
- [x] Select Taurus young stars as the pilot population; identify independent member reference.
- [x] Verify official Gaia DataLink and ZTF API routes from archive documentation.
- [x] Write explicit scientific hypotheses, limitations and data/model ethics.
- [x] Build initial source/geometry/URL prototype with offline tests.
- [ ] Retrieve and reconcile the complete machine-readable **Luhman 2023 Table 2**; paper reports 532 adopted members, 467 Gaia DR3 entries and 412 Gaia DR3 astrometric solutions. A pinned third-party copy has now been **examined in full through the research connector**; the original publisher table and full local raw snapshot still need reconciliation.
- [x] Choose primary focus: **candidate dippers/bursters**, with rotation/periodicity as secondary.
- [x] Code the proposed 24-target disk-stratified selector; **a separate 24-object real-coordinate technical seed has now been extracted**, but no disk-class scientific roster is approved.
- [ ] Verify independent disk labels; execute the roster against the verified member table and approve a first sample with evidence.

**Exit gate:** versioned target manifest, science protocol approved, exact source provenance, no fabricated observational sample.

## Stage 2 — Real archive integration [v0.6 ASTROMETRIC SCREEN BUILT; OBSERVATION GATE STILL OPEN]

- Gaia TAP metadata and DataLink downloads, availability audit and archive-side errors.
- Single-object ZTF acquisition with per-oid/per-filter parsing, raw-cache checksums, time and magnitudes checked.
- [x] Preliminary spherical proper-motion propagation, per-band/OID centroid checks and conservative ambiguity reports (v0.6). **Not yet full Astropy covariance/parallax/image matching**.
- [ ] Full Astropy astrometric uncertainty, parallax and image-level scene checks on actual ZTF epochs.
- Service etiquette, bounded retries, timeouts and resumable ingestion. Parquet/DuckDB for processed products.

**Exit gate:** traceable raw-to-processed lineage and QC for pilot objects; measured coverage and rejection counts.

## Stage 3 — Time-series quality and exploratory science

- Per-band cleaning, photometric uncertainties, upper limits/flags, baseline variability.
- Diagnostic plots with original time system, seasonal gaps and sampling windows.
- Descriptive source population statistics with denominators and uncertainty.

**Exit gate:** data dictionary, QA report, rejected-object report, human-reviewed sample diagnostics.

## Stage 4 — Physical variability characterization [EXPLORATORY ENGINE BUILT; SCIENCE GATE OPEN]

- [x] Implement provisional weighted Lomb–Scargle diagnostics and sampling-window flags on engineering fixtures. **No real periods inferred.**
- [ ] Benchmark aliases, harmonics and correlated astrophysical noise on *real* survey sampling.
- [x] Uncertainty-aware descriptive amplitude, scatter and tail-asymmetry **proxy**.
- [ ] Quasi-periodic versus aperiodic signal diagnostics, amplitude/period uncertainty and physical timescale tests.
- Differential filter changes and optional simultaneous color–magnitude diagnostics.

**Exit gate:** period recovery reliability, feature definitions and uncertainties fully specified.

## Stage 5 — Validation and falsification [v0.6 SYNTHETIC FIELD-CONTROL VETO BUILT]

- [x] Compare simulated strong astrophysical signals with same-field coherent calibration artifacts and explicit missing-control regimes (v0.6; artificial data only).
- [ ] Literature benchmark cases, null simulations and injection/recovery on real timestamps.
- False-positive rate versus cadence, brightness and crowding; account for multiple comparisons.
- External region or survey validation when scientifically justified.

**Exit gate:** quantified detection biases; null and failure-case figures shown prominently.

## Stage 6 — Machine learning (only when warranted)

- Unsupervised baselines (robust statistics, Isolation Forest); interpretable supervised models only with trustworthy labels.
- Split by source, region and/or observing campaign appropriately. Leakage review before hyperparameter search.
- Calibrate ranking thresholds against expert-review capacity; transparent feature explanations.

**Exit gate:** meaningful improvement over the simple baseline on genuinely withheld sources and failure-analysis table.

## Stage 7 — Scientific conclusions and candidate register

- Scientific figure gallery, object-level vetting with literature, alternative physical interpretations.
- Catalogue of **candidates for follow-up**, clearly differentiated from confirmed discoveries.
- Draft internal research note / reproducibility appendix, limitations and references.

**Exit gate:** every headline claim directly traceable to evidence, source and calculation.

## Stage 8 — Portfolio-grade product

- REST API (FastAPI), an interactive light-curve viewer, candidate search, sky map and provenance panels.
- Docker, tests, static analysis, CI and deployment with realistic cost/resource safeguards.
- Onboarding documentation, methods paper-style report and honest AI-assistance disclosure.

**Exit gate:** third party can reproduce a vetted example end-to-end, understand design tradeoffs, and distinguish the research findings from demonstration features.

## Human decision checkpoints

1. Scientific focus and what would count as an astrophysically meaningful anomaly.
2. Initial vetted subsample from Taurus.
3. Quality thresholds, high-risk matching decisions and period significance.
4. Which models to compare; whether labels are truly independent.
5. Selection of any candidates to report publicly.

The purpose of these checkpoints is not to make the user write boilerplate code, but to ensure the scientific decisions genuinely represent their contribution and can be defended in research and job interviews.


## v0.5 evidence update — November 2026

- Completed in code: dry-run 24-target ZTF batch plan, provenance-verified restartable downloader, strict per-target status ledger, and preliminary uncertainty-aware fading/brightening **candidate** screen.
- Synthetic-only algorithm validation and unit testing completed; documented failure on coherent calibration offsets.
- **Blocked / not completed:** download of actual ZTF curves in this environment, astrometric source verification, Gaia DataLink epoch-photometry extraction, disk-class stratification, real-cadence injection/recovery and any measured Taurus event incidence.
- Next scientific gate: obtain 2 real ZTF sources via IRSA, audit each `oid` and image/motion match; never infer a member from proximity alone.


## Phase 9 checkpoint — 4 November 2026

- [x] Per-observation Gaia proper-motion screen against each ZTF MJD and photometric position (engineering method; no confirmed counterpart).
- [x] Explicit multi-OID ambiguity and invalid/missing epoch hold statuses.
- [x] Fail-closed two-star evidence dossiers, read-only offline dashboard and integrity-controlled file import.
- [x] Two official IRSA requests attempted, and **both failed due to environment networking**; no ZTF Taurus raw photometry downloaded.
- [x] 303 tests pass (239 inherited + 64 v0.9).
- [ ] **Blocking observational science gate:** successfully acquire and independently authenticate the official ZTF FT Tau / CIDA 11 raw tables; resolve OIDs by epoch, images and crowding; perform real-timestamp injection/recovery.
- [ ] Independently verify the publisher's Luhman (2023) table bytes and scientifically classify disks with appropriate literature.

Important: do not interpret unavailable remote data as evidence of absence of stars, variability, or survey coverage.