# StellarForge — Current project status

**Version:** 1.13.0 · **Updated:** 2026-11-08 · **Engineering status:** active, tested · **Scientific status:** unverified Gaia–ZTF source associations.

## Implemented

- Full Python package, command-line utilities, tests, continuous integration and research documentation.
- 533/533 automated tests passed in GitHub Actions during the v1.13 actual original ZTF mask/PSF pilot (8 November 2026).
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
- **v1.13 original ZTF instrument products verified:** 20 target/reference candidate locations screened for matching official `mskimg.fits` bad-pixel maps and same-dated original `sciimg.fits` pixel grids with 0.05-pixel WCS registration tolerance. **Four reference candidates** yielded valid, aligned science+mask products, with zero disqualifying 6141 bad-mask bits and zero saturation-bit flags in their 4.5-pixel nominal Gaia apertures; **all 4 target-mask checks and 12 other reference checks returned HTTP 503**. Two real 23×23 `sciimgdaopsfcent.fits` science-field-center PSF stamps parsed (2 other HTTP 503). Zero source-specific native PSFs, authenticated matches or calibrated WCS errors; source marker bits 1/11 are not bad pixels.
- Scientific data integrity gates: distinct OIDs/bands, flag masking, hashes, time-scale handling, provisional astrometric checks and synthetic-only benchmarking.

## Not yet established

- Independent Gaia/ZTF source identity or confirmed physical variability.
- Publisher-original Taurus catalog byte verification.
- Fully authenticated stellar PSF references, independent distortion/field-WCS solution, deblending, photometric centroid/background errors, full observer/time-scale/radial-velocity modeling and non-Gaia neighbors. v1.9 propagates *Gaia's five-parameter formal covariance and first-order annual parallax* for two target sources but does not validate actual ZTF instrument errors or single-star model biases.
- Real-survey detection completeness, false-positive rate or representative disk-class sample.

## Public portfolio boundary

The repository may be viewed as *research software in development*. Do not interpret provisional code outputs, observational cone-search rows or synthetic benchmarks as claims of astrophysical discoveries. Raw third-party photometric downloads must remain outside Git until legal/provenance/reuse constraints are reviewed.

## Next scientific milestone

**Next science gate:** retrieve matching official ZTF science `mskimg.fits` pixel masks and native empirical PSF products; verify contamination/saturation/time metadata and independently authenticate field stars before attempting WCS distortion, PSF photometry or realistic image-centroid error budgets. v1.12 Gaussian/aperture agreement measures model sensitivity, not calibrated telescope precision.

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
