# StellarForge v1.22 status update — 10 November 2026

**Archive provenance recovered:** exact original private 181,170-byte IRSA photometry source ZIP from GitHub Actions run 41997079598, byte SHA matches Actions metadata, original source files **not committed**. **752/752 synthetic/offline automated tests passed** at code/test milestone, adding exact ZIP digest/manifest checks and two complete mocked 4+3 runner pathways (successful synthetic whole-star PSF and failure due to too few masked held-out stars). **The manual v1.20 real ZTF source-pixel run has NOT been executed.** No physical Gaia–ZTF source identification or independently calibrated survey PSF/WCS/noise, new companions or variability claimed. [Audit](PHASE122_HISTORIC_SOURCE_RECOVERY_AND_REAL_PILOT_GATES.md).

---

# StellarForge v1.21 — scientific QA update (10 November 2026)

**743/743 synthetic/offline CI tests passed.** The added scientific audit checks time-sensitive original IRSA artifact metadata, guards against impossible 3+2 original-data model success claims, and stress-tests the empirical PSF with left-out training stars and artificially injected source blends. The original data artifact expires **12 November 2026 08:47:05 UTC**. The manual v1.20 original-data workflow remains **unrun** and no real independent instrument calibration, new astronomical detection or companion has been verified. [Methodology](PHASE121_FALSIFICATION_PROVENANCE_AND_RELEASE_GATES.md).

---

# StellarForge v1.20 status update — 10 November 2026

**Software IMPLEMENTED; synthetic/offline CI passed (708 checks).** Strict CIDA 11 Gaia field star-cohort 4+3 preregistration, original masked ZTF source stamp co-registration, native source quality gates and a **manual-only** real original-data pilot are now available. **The manual workflow has NOT yet run**, so there are no newly validated real empirical PSF holdout results. Original DAOPhot source-level PSF training roster, physical Gaia/ZTF identities and CCD/WCS calibration remain unknown. [v1.20 method](PHASE120_ORIGINAL_REGISTERED_STAR_COHORT.md).

---

# StellarForge v1.19 status update — 10 November 2026

**Implemented and CI-verified, SYNTHETIC-ONLY:** a fresh empirical PSF model with distinct whole-star train/test source-ID split, conservative registered original mask input contracts and CCD noise/correlated aperture diagnostics. **686/686** automation cases passed; [CI](https://github.com/ismaelberja/stellarforge/actions/runs/42799842210). Original ZTF PSF star-training membership remains unknown; no actual new real-data instrumental/astrophysical validation is claimed. See [v1.19 methods](PHASE119_EMPIRICAL_STAR_PSF_AND_CCD_NOISE.md).

---

# StellarForge — Current project status

**Version:** 1.18.0 · **Updated:** 2026-11-09 · **Engineering status:** active, tested · **Scientific status:** unverified Gaia–ZTF source associations.

## Implemented

- Full Python package, command-line utilities, tests, continuous integration and research documentation.
- 661/661 automated tests passed in the v1.18 original official eight ZTF instrument processing-log and FT Tau exploratory Gaia source-masked-pixel real-data pilot (9 November 2026), using the same four historic dated original science exposures.
- Pinned secondary Taurus catalog audit: 532 adopted members, 467 Gaia identifiers; 24-object technical seed.
- Two official IRSA ZTF cone-query responses near FT Tau and CIDA 11 on 5 November 2026, totaling 2,212 rows across six distinct ZTF OIDs; integrity hashes and failures are logged.
- Reproducible SHA-checked **provisional Gaia-to-ZTF per-epoch screen** for all six OID/passbands; median positional separations ~0.063–0.092 arcsec (not independently verified identities).
- Independent Gaia DR3 TAP 15-arcsec sky-field queries around FT Tau and CIDA 11 both returned only the target Gaia source; **this does not rule out non-Gaia or unresolved contamination**.
- Gaia DR3 RUWE values: FT Tau 1.3266, CIDA 11 8.5675. The latter is an astrometric-fit quality concern, not proof of binarity.
- Official science/reference ZTF cutout links and header transport probes in v1.4 (intermittent HTTP 503).
- **v1.5 real FITS pixel screening:** 5 of 6 ZTF OID-band groups had real FITS pixels opened and celestial WCS checked (3 science frames, 2 reference coadds); all five show a local maximum within 0.5 arcsec of Gaia's approximate position.
- **v1.6 local Gaussian image-shape screening:** three FT Tau individual science images passed bounded single-Gaussian-plus-background fitting. All three have high model residuals and require further review; no CIDA 11 fits and no OID/filter with two independent usable science images in this execution. The fit is not an independently calibrated PSF.
- **v1.7 independent science exposure review:** 12 individual real FITS science images (2 distinct images per each of 6 OID/filter groups; 8 FT Tau, 4 CIDA 11) passed provisional 2D FITS/WCS + radial-profile screening; no reference coadds counted. Pairwise nominal WCS/Gaia-proxy centroid-residual differences ~0.024–0.097 arcsec, not calibrated astrometric errors.
- **v1.7 same-image field-control attempt:** 90-arcsec cutouts, but 0 of 12 frames yielded two usable unclassified comparison brightness peaks; no empirical PSF calibration or clean-source claim. 11/12 simple Gaussian profiles flagged for residual review. Source identity remains unverified.
- **v1.8 Gaia DR3-backed reference-star candidate pilot:** 210-arcsec wide-field Gaia queries returned 50 entries around FT Tau and 250 around CIDA 11; 3+5 passed quality/isolation screening. Four genuine target FITS frames and 16 candidate reference cutouts from the same science exposure paths were attempted; 13 references fitted. Three exposures permit a **provisional local offset translation** with >=3 candidate Gaia controls; no independent WCS solution, authenticated empirical PSF, or source identity is claimed.
- **v1.9 actual Gaia DR3 5×5 formal astrometric covariance and annual parallax:** independent TAP returns exact FT Tau/CIDA 11 Gaia IDs with ten correlations and five positional/parallax/PM formal errors. Four real ZTF observation MJDs evaluated with offline Earth-geocentric geometric parallax, providing signed offsets and formal Gaia-only 2D covariance; **no ZTF WCS/PSF uncertainty or physical source identity validated**. High CIDA 11 RUWE ≈ 8.57 cautions that catalogue formal errors may underestimate physical uncertainties.
- **v1.10 reference holdout evidence:** preserved 13 actual derived Gaia candidate image-model offsets from four ZTF science frames with the SHA-256 of original v1.8 aggregate; independent reference-exclusion tests show 3 inclusive and only 2 strict exposures with enough stars. FT Tau MJD58491 LOO RMS ~0.076 arcsec, CIDA 11 MJD58475 ~0.093 arcsec; these are *internal disagreement* not calibrated detector astrometric errors. CIDA 11 MJD58849 has five inclusive but only two strict references.
- **v1.11 corrected reference-star Gaia model:** actual official Gaia DR3 five-parameter formal covariance and annual geometric parallax propagated for 8 candidate references plus 2 target source IDs at their actual ZTF exposure dates. Thirteen old real Gaussian image-model offsets re-evaluated without refitting FITS pixels. Strict LOO RMS changes are only −0.012 mas (FT Tau) and −0.075 mas (CIDA 11), with the same 2/4 exposure eligibility. These are **internal disagreement metrics, not calibrated instrument errors**.
- **v1.12 real original science FITS remeasurement:** ran **two 20-request audits on the same four dated ZTF science frames**, with source-specific Gaia 5D formal covariance and geometric annual parallax. Initial run: 9 HTTP 503, 2 inconclusive screens, 9 complete two-estimator fits. **Final run:** 8 HTTP 503 and **12 complete two-centroid FITS models** (1 target + 11 references), 9 provisional model-consistent candidate references; **only one of four exposure groups** had >=3 controls. Final-run median inter-model separation 0.104720″ across 12 fits; CIDA 11 MJD58475 internal heldout disagreement 0.064675″ (Gaussian) versus 0.155762″ (aperture), **not instrumental WCS errors**. Four overlapping identical FITS byte hashes confirm data consistency where both runs obtained the cutouts. Masks/empirical PSFs still not used.
- **v1.13 original ZTF instrument products verified:** 20 target/reference candidate locations screened for matching official `mskimg.fits` bad-pixel maps and same-dated original `sciimg.fits` pixel grids with 0.05-pixel WCS registration tolerance. **Four reference candidates** yielded valid, aligned science+mask products, with zero disqualifying 6141 bad-mask bits and zero saturation-bit flags in their 4.5-pixel nominal Gaia apertures; **all 4 target-mask checks and 12 other reference checks returned HTTP 503**. Two native 23×23 center PSFs parsed on initial run A; two **different, complementary** original 23×23 center-PSF products parsed on rerun B, providing **all four unique original center-PSF stamps across both runs**. Run B had HTTP 503 on **all 20** science/mask attempts; only the four first-run reference masks remain verifiably screened. Zero source-specific native PSFs, authenticated matches or calibrated WCS errors; source marker bits 1/11 are not bad pixels.
- **v1.14 official native ZTF PSF source fit catalogues:** 4 actual original `psfcat.fits` BINTABLE catalogues parsed (3,970 + 5,569 + 5,313 + 12,355 = 27,207 per-exposure detections), 20 Gaia target/reference predicted source positions screened using original PSF `chi`/`sharp`/SNR/`flags` and ≤1″. **16/20** provisional unique nearby source fit candidates pass, three have `chi<0.5` and require quality review, one historical FT Tau reference has no catalog entry within local search; target passes 3/4 technical epochs, references 13/16. Four original spatial DAOPhot `sciimgdao.psf` files retrieved and source-hashed but **not decoded or evaluated at any source position**. No WCS-calibrated precision, authenticated source identity or discovery.
- **v1.15 original native spatial ZTF DAOPhot PSF models actually reconstructed:** all four 88,465-byte original `sciimgdao.psf` files decoded (GAUSSIAN + 3 × 47 × 47 half-pixel lookup correction arrays), each evaluated on a 23 × 23 original image pixel PSF stamp. All **four numerical model reconstructions at the detector center** closely reproduce their corresponding native `sciimgdaopsfcent.fits` FITS stamp (cosine 0.999999–1.0, L1 0.000278–0.000984), while **16/16** original v1.14 provisional `psfcat` candidate-source detector positions now have an evaluated approximate local *model* PSF shape. **No original source-local real image pixels/masks fit**, independent source-PSF calibration, astrophysical identity or WCS uncertainty claimed. Cubic B-spline lookup interpolation is not proven identical to original DAOPhot.
- **v1.16 real original masked ZTF source pixel residual analysis:** all **16/16** original `sciimg.fits`+`mskimg.fits` paired source cutouts successfully retrieved and independently WCS-aligned, with compatible source native catalogue detector subpixel phases and **zero original 6141 bad/saturation pixels** in all 16 nominal star cores. Fitted fixed original native spatial DAOPhot PSF amplitude in DN plus a sky plane to checkerboard training pixels of each same source image, then evaluated *different pixels of the same star* (not independent stellar controls). **13/16** selected source fits passed internal provisional residual/noise screens; **3/16** have high positive residual peaks and remain review-required (one FT Tau target at MJD58491, one CIDA 11 target and one CIDA 11 reference at MJD58849). Median held-out pixel RMS/sky MAD proxy ~1.1015. No external WCS/PSF error, astrophysical Gaia/ZTF identity or physical companion/variability confirmed.
- **v1.17 new Gaia-source-disjoint field-star tests:** two fresh original Gaia DR3 210″ wide-cone tables had FT Tau **50 rows** and CIDA 11 **250 rows**. Excluding all **10** v1.16 technical target/reference Gaia IDs before looking at ZTF PSF residuals, strict Gaia-quality/isolation filters yielded **0** new FT Tau controls and **20** potential CIDA 11 Gaia-only stars before budget. Four newly selected CIDA 11 Gaia IDs (one per sky quadrant) delivered **6/8** original CIDA 11 `sciimg.fits`+`mskimg.fits` masked source-pixel PSF fits on 2 dates, **6/6** passing provisional same-image residual QA. Two other ZTF native catalogue checks remained review/ineligible. **32** fixed ±25″ shifted sky positions had **0** PSFcat sources within 1″; not a calibrated false-match rate. Original ZTF DAOPhot training-star membership of those 4 new Gaia IDs is **unknown**, so no independently calibrated PSF/WCS or Gaia/ZTF physical match proven.
- **v1.18 original PSF training provenance audit:** all **8/8 official `sciimlog.txt`/`log.txt` ZTF processing logs** accessible for four historical original science exposures; 115–116 PSF/DAOPhot-referencing lines per `sciimlog` in original logs, but **zero source-keyed, independently authenticated DAOPhot PSF-training star rosters**. A PSFfit source catalogue is not the PSF construction source list. **FT Tau strict new source controls remain 0** on a fresh 50-row Gaia cone. A *separate*, preregistered broader exploratory Gaia tier yielded **four new FT Tau candidate Gaia IDs**, of which **one distinct source** was eligible for original WCS-aligned masked `sciimg.fits`+`mskimg.fits` spatial PSF fits in **two** historical dates (RMS/annular sky MAD proxy 0.9203 and 0.9554, both provisional same-image QA passes). The other six source×date native ZTF PSF-fit catalogue screens were ineligible/review. **32** shifted 25″ probes gave zero native catalogue matches, not a physical chance association rate. No independent PSF training holdout, absolute WCS precision or astrophysical discovery.
- Scientific data integrity gates: distinct OIDs/bands, flag masking, hashes, time-scale handling, provisional astrometric checks and synthetic-only benchmarking.

## Not yet established

- Independent Gaia/ZTF source identity or confirmed physical variability.
- Publisher-original Taurus catalog byte verification.
- Fully authenticated stellar PSF references, independent distortion/field-WCS solution, deblending, photometric centroid/background errors, full observer/time-scale/radial-velocity modeling and non-Gaia neighbors. v1.9 propagates *Gaia's five-parameter formal covariance and first-order annual parallax* for two target sources but does not validate actual ZTF instrument errors or single-star model biases.
- Real-survey detection completeness, false-positive rate or representative disk-class sample.

## Public portfolio boundary

The repository may be viewed as *research software in development*. Do not interpret provisional code outputs, observational cone-search rows or synthetic benchmarks as claims of astrophysical discoveries. Raw third-party photometric downloads must remain outside Git until legal/provenance/reuse constraints are reviewed.

## Next scientific milestone

**Next science gate:** find a true per-exposure source-keyed original ZTF DAOPhot PSF-training-star roster (not recovered from the eight archived logs), or rebuild a PSF independently with a documented training/control split. Preserve separate v1.17 strict and v1.18 exploratory Gaia quality tiers, enlarge real FT Tau source/epoch/filter coverage and calibrate physical CCD noise, WCS residuals and Gaia/ZTF identity before astrophysical claims.

Read the [observational transport report](../reports/observational_intake_v1.2/RAW_TRANSPORT_AUDIT.md) for precise counts and caveats.

Read the [v1.3 positional screening report](../reports/astrometry_v1.3/PROVISIONAL_POSITIONS_REPORT.md) for six measured OID-band groups and limits.

Read the [v1.4 independent Gaia/IRSA audit](../reports/field_review_v1.4/GAIA_NEIGHBOURS_AND_IRSA_IMAGES.md) for actual online query evidence and limitations.

[v1.5 real FITS pixel/WCS results](../reports/real_fits_v1.5/PIXEL_WCS_RESULTS.md): five provisional image screens, **zero source identities confirmed**.

Read the [v1.6 real Gaussian-profile review](../reports/psf_v1.6/REAL_GAUSSIAN_FIT_REVIEW.md): three provisional fits, zero source identities or repeated-epoch confirmations.

Read the [v1.7 real-image multi-epoch and field-control audit](../reports/field_controls_v1.7/REAL_MULTIEPOCH_AND_CONTROL_LIMITS.md) for verified measurements and strict limitations.

Read the [v1.8 real Gaia reference-candidate audit](../reports/gaia_reference_v1.8/REAL_REFERENCE_CANDIDATE_EVIDENCE.md), where three local translation proxies are carefully separated from independently calibrated astrometry.

Read the [v1.9 real Gaia DR3 formal covariance and annual parallax audit](../reports/gaia_formal_v1.9/GAIA_COVARIANCE_AND_ANNUAL_PARALLAX.md). These are not ZTF astrometric measurement errors or astronomical source matches.

See the [v1.10 real Gaia-reference holdout report](../reports/holdout_v1.10/REAL_REFERENCE_HOLDOUT_EVIDENCE.md) and [reproducible reduced derived ledger](../data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json).

Read the [v1.11 real Gaia reference parallax/formal covariance sensitivity results](../reports/reference_parallax_v1.11/REAL_GAIA_REFERENCE_PARALLAX_LOO.md). All physical source identity and observational precision claims remain open.

[Real observed-data v1.12 aperture-versus-Gaussian reference model evidence](../reports/real_fits_v1.12/REAL_TWO_CENTROID_MODEL_QA.md) · [Scientific methods and limitations](PHASE112_PIXEL_CENTROID_AND_WCS_LIMITS.md).

[Actual v1.13 original ZTF mask/center PSF evidence](../reports/original_masks_psf_v1.13/REAL_ZTF_MASK_AND_NATIVE_CENTER_PSF_EVIDENCE.md) · [Official instrument mask methods and scientific limits](PHASE113_OFFICIAL_ZTF_MASK_AND_NATIVE_CENTER_PSF.md). The 533 regression tests passed without advancing any physical discovery claim.

[Detailed v1.14 real PSF catalogue candidate evidence](../reports/native_psfcat_v1.14/REAL_ZTF_GAIA_PSF_CATALOGUE_EVIDENCE.md) · [source crossmatch and native DAOPhot spatial PSF methodological limits](PHASE114_NATIVE_PSF_CATALOGUE_AND_SPATIAL_MODEL_GATE.md).

[Real original v1.15 spatial DAOPhot model/FITS-center comparison](../reports/spatial_daophot_v1.15/REAL_DAOPHOT_CENTER_AND_LOCAL_SHAPES.md) · [DAOPhot format/method/limitations](PHASE115_DAOPHOT_SPATIAL_MODEL_VALIDATION.md).

[Real v1.16 ZTF source science/mask pixel residual evidence](../reports/masked_spatial_psf_v1.16/REAL_ZTF_PIXEL_RESIDUALS_EVIDENCE.md) · [methods and scientific caveats](PHASE116_ORIGINAL_MASKED_PSF_PIXEL_RESIDUALS.md).

[Real v1.17 previously unused Gaia field-source PSF and shifted sky control evidence](../reports/new_gaia_holdouts_v1.17/REAL_DISJOINT_GAIA_CONTROL_AND_SHIFTED_SKY_RESULTS.md) · [methodological limits and preregistration](PHASE117_DISJOINT_GAIA_SOURCE_HOLDOUTS_AND_SHIFTED_SKY_NULLS.md).

[Authentic original ZTF processing logs and FT Tau source fit report v1.18](../reports/psf_training_ft_tau_v1.18/REAL_ZTF_LOG_AUDIT_AND_EXPLORATORY_FT_TAU.md) · [method and sample-quality distinctions](PHASE118_PSF_TRAINING_LOGS_AND_EXPLORATORY_FTTAU.md).
