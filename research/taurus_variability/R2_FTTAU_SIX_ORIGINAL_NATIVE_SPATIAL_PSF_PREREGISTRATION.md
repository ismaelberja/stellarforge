# Taurus R2 — prospectively frozen original native DAOPhot spatial PSF pixel-screen experiment

**12 November 2026 — protocol committed before new original ZTF spatial PSF retrieval and source-pixel fitting.**

## Primary aim, scope and evidentiary requirements

The first-principles circular analytic Gaussian six-epoch experiment (merged PR #47) produced four finite Gaussian fits and two numerical failures; none calibrated ZTF's actual instrument PSF/noise. The next **fixed-source, original-data instrumental** comparison will evaluate ZTF's **own per-exposure spatially varying DAOPhot PSF** at the original nearest native PSF source position, using the original native source catalogue, original science image and detector mask, all with their SHA-256 provenance locked to the PR #44–47 original ledgers.

The six source exposures are prospectively frozen and ordered:
1. original g field 1605 early/late,
2. original g field 609 early/late,
3. original r field 609 early/late.

Original ZTF OIDs, 14-digit filefracday, band, field, CCD and quadrant, MJDs, full original native PSFcat file hashes, original source chi and SNR values, **and the six original science/mask cutout hashes** are the values in `reports/taurus_variability_r2/FTTAU_SIX_ORIGINAL_ZTF_INDEPENDENT_GAUSSIAN_PIXELS_NO_RAW.json`. They must also reconcile with the prior original PR #44/#45/#46 evidence through `six_original_pixel_specs`. Any mismatch is a **HARD FAIL**, not a new observation, and no replacement dates/sources are allowed. The excluded r1605 stratum remains excluded. The single original Gaia DR3 target source ID remains 149623711269425408; retrieve the exact original five-parameter source and propagate to every observation epoch using the existing approximate geocentric-parallax routine.

## New original archive data and preregistered method

For every one of the same six exact dated exposures:

1. Re-fetch and byte-SHA verify the full native ZTF `psfcat.fits`. Recover the geometrically nearest (NOT best-fitting) original source to the Gaia-propagated position, apply original unchanged 0.6″ nearest and >1″ second-nearest conditions and the **previously frozen quality status**. Verify exact original nearest source chi/SNR (tolerance 0.001 and 0.01 respectively). Do not drop previously failed low-chi sources.
2. Re-fetch the exact original 60″ science FITS cutout and same-cutout mask centred at Gaia-propagated coordinates, **byte-SHA verify both against the permanent PR #47 original science/mask evidence**. This is not a new or more favourable exposure.
3. Fetch the original dated native DAOPhot spatial model `sciimgdao.psf` and the original **science-quadrant field-centre** stamp `sciimgdaopsfcent.fits`. SHA both product responses. Decode using the existing strictly bounded `v115_spatial_psf.parse_original_daophot_lookup`. Cross-check the reconstructed model against the original **field-centre** stamp using existing cosine similarity >=0.93 and normalized L1<=0.50 engineering diagnostic. Do not claim this independently calibrates the source-specific spatial model; both files come from the same ZTF pipeline. Preserve original access/decode failures as unavailable/unsupported, no model substitution.
4. On the same original science/mask cutout, apply the original spatial model at the fixed nearest source's genuine per-exposure **native CCD x/y** and native source ICRS position, as implemented by `v116_masked_original_psf_residuals._masked_fit`. It guards celestial science/mask WCS, original detector native-vs-FITS subpixel phases <=0.22 px, bad mask/saturation, enough unmasked data, source profile model, and same-source checkerboard pixel holdout. Use its **pre-existing** 9-pixel fit radius, 14–22-pixel sky annulus, >=150 valid source-fit pixels, >=230 good sky pixels, positive fitted model amplitude and original held-out normalized residual thresholds (RMS<=3, max positive<=7). **Do not retune any PSF spatial reconstruction or mask/noise/holdout cutoffs** after viewing the six images.
5. Emit only original product SHAs, stage availability/validity, existing model consistency QA, native target original chi/SNR *diagnostics*, source- and held-out-pixel **derived** residual statistics, mask counts and status labels. Exclude all original source IDs, other source positions, native catalogue raw rows, original science pixels, original PSF tables/coefficients, all original instrumental fit amplitudes, sky DN values or original photometry from persistent JSON. Explicitly count successful numeric spatial-model pixel fits and the subset satisfying the pre-existing heldout engineering gate; quantify differences with the earlier independent Gaussian experiment **only as a different-model technical comparison** because their fit radii, background and noise definitions differ. Do not divide the two residual statistics or claim a calibrated improvement.

## Mandatory interpretation constraints

A native spatial PSF model and the original PSFcat source were produced by the same image-reduction pipeline and are **NOT an independent validated different-star empirical PSF calibration**. A good original native model checkerboard pixel residual result is not a physical Gaia–ZTF source match, independent astrometry/WCS error, companion detection, variability measurement or reason to retrospectively accept the three originally chi-low source-quality failures. Original 5/8 passes, 3/8 failures and only 1/4 fully passing independent-night pairs remain frozen. No ZTF ObjectID light curves merged. R2 **open** and R3 astrophysical inference blocked regardless of workflow success.

Original archive suffixes (official): https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html ; ZTF pipeline original DAOPhot spatially varying source PSF: https://irsa.ipac.caltech.edu/data/ZTF/docs/ztf_pipelines_deliverables.pdf .

Acceptance of this increment: exact six original source/PSF/science/mask checksums and an honest per-frame spatial model QA with instrument limitations, not an astronomical discovery or threshold change.
