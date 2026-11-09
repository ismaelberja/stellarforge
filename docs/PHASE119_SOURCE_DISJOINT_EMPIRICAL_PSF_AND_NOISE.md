# Phase 1.19 — New empirical ZTF PSF trained from different original stars and tested on separate Gaia candidates

**9 November 2026 · Survey-original masked CCD science images, Gaia DR3 and source-level cross-validation.**

## Scientific objective

In v1.15–v1.18 the project decoded native ZTF DAOPhot PSFs and fitted the resulting spatial model to original ZTF science pixels with original bitmasks. However, the **native PSF originates from the same survey pipeline that produced the native source positions and source catalogue**, and its **original training-star roster is not verifiable from eight public ZTF processing logs**. Thus good original-image residuals alone are not independent validation of the instrument PSF.

v1.19 deliberately goes a step beyond that internal survey model: **constructs an entirely NEW empirical 23×23 PSF from original image pixels of bright, Gaia-identified candidate reference stars**, without reading native spatial DAOPhot PSF correction coefficients during construction. It then compares that template on *different, new Gaia source IDs* that were selected before any current ZTF source-residual analysis.

**Scientific distinction:** the empirical PSF *shape training* and *stellar source evaluation* have **disjoint Gaia source IDs and images**, but all original source sky/detector positions remain tied to the same ZTF native source extraction/catalogue and its unknown historical instrument PSF training set. This is therefore a **StellarForge-internal genuine distinct-source cross-validation of an independently reconstructed PSF shape**, *not* an independently calibrated ZTF telescope PSF, absolute WCS error, authenticated Gaia–ZTF physical identity or astronomical discovery.

## Preselected, role-separated star samples

We do **not** change stellar eligibility criteria post hoc to make a residual score pass. A first v1.19 pilot attempted to use the four v1.17 *new* Gaia CIDA 11 sources for **both** training and leave-one-source-out validation, excluding the heldout source in every fold. This pilot found that 3/4 source images were **too faint for the conservative template-training aperture SNR proxy ≥10** at the first CIDA 11 epoch; only one high-SNR training image passed, preventing a scientifically credible 3-training/1-heldout experiment. The failure and its original archived aggregate report remain separately accessible in the original GitHub Actions execution, not silently reported as a successful fit.

The **revised, source-disjoint role separation** retains that conservative bright-training threshold and fixes two separate source groups *before interpreting new source-image residuals*:

1. **PSF training stars:** the **original v1.8 preregistered Gaia reference IDs** for the exact historical ZTF exposure, excluding the high-RUWE technical target. These old reference candidate IDs are separately queried for their full formal Gaia 5D covariance and first-order Earth-geocentric annual parallax. They must pass native ZTF per-exposure source quality, crowding, original bad-pixel mask/sky/WCS checks and **original pixel-image integrated aperture SNR/noise proxy ≥10**. The native ZTF `psfcat.fits` source association remains provisional, despite the Gaia IDs.
2. **New heldout evaluation stars:** source IDs **not in the original ten Gaia v1.8–v1.16 target/reference IDs**, selected as in **v1.17 CIDA 11 strict Gaia-only** sampling (four quadrants) and **v1.18 FT Tau explicitly exploratory Gaia-only** sampling (distinct quality tier, not interchangeable with strict stars). The original ZTF catalogue quality and actual science/mask checks still apply, but the **test source can be fainter, with an aperture SNR/noise proxy ≥2.5**, because its pixel shape is NEVER used to construct the empirical PSF. It is evaluated, not trusted to define the training shape.

A training source ID **cannot equal** a new heldout source ID, even at a different epoch. Every exposure is processed independently and must have **at least three distinct bright, valid old-reference training stars** and **at least one valid new evaluation candidate** to yield a source-disjoint empirical PSF comparison. If a field/date does not meet this predeclared minimum, publish `INSUFFICIENT_REAL_BRIGHT_TRAINING_OR_NEW_HELDOUT_STARS`, **not a calibrated model or astrophysical absence claim**.

A secondary stricter within-new-Gaia **leave-one-source-out** trial requires at least **four** new **bright** eligible stars in *the same exposure*; if unavailable, report it as insufficient. We do **not** treat the same source at multiple epochs as independent stars in either validation design.

## How the true original source-image empirical PSF is constructed

Each eligible training candidate has its own original NASA/IPAC science product `sciimg.fits` and corresponding original `mskimg.fits` cutout, requested at the original PSF-fit source `ra/dec` within the **same dated ZTF science exposure** used for every other training/test source in that comparison.

Before using source pixels:
- Verify original science/mask FITS are actual 2D images and celestial WCS coordinates agree within **0.05 pixel** across representative field positions.
- Require native ZTF PSFfit catalogue **full CCD-quadrant** `xpos/ypos` fractional pixel phase to match the cutout-local WCS subpixel phase within **0.22 pixel**; do not equate the original full native coordinates with 0-based cutout pixel coordinates.
- Require an unmasked, finite, unsaturated original source core within 10 pixels using the **official ZTF disqualifying detector bitmask 6141** (including saturation), not source-marker bits.
- Fit a local sky **plane** from ≥230 finite unmasked sky pixels in an annulus at radius 14–22 pixels, clipping repeated 4× robust MAD outliers; retain original raw **Digital Number (DN)** units, not calibrated flux.
- Extract the original **23×23** source stamp, subtract that independent sky plane, align the source image to integer pixel-center phase with a cubic interpolation of real source pixels, truncate the bright training shape to a 9-pixel-radius region and normalize its positive counts to unit sum. Nonpositive, masked, low-SNR, malformed/WCS-misaligned or insufficient-sky sources are **excluded with explicit reason codes**.

The empirical PSF template is a **nonnegative median of normalized 23×23 pixel arrays of at least three different bright old Gaia source IDs**, renormalized to unit sum. The original spatial DAOPhot lookup table is not consulted to determine this empirical PSF. The template is shifted back to each heldout star's native original science-pixel subphase to compare like with like.

## What is truly withheld and how it is tested

The **new evaluation source** has supplied **zero pixels to construction of its empirical PSF shape**. Original native ZTF source position/candidate matching and original Gaia survey selection remain pipeline-coupled and provisional. At each heldout star, independently fit *only* four nuisance coefficients: stellar PSF amplitude (A) in raw DN and a local linear sky plane (b_0+b_x x+b_y y).

On the heldout star **itself**, solve amplitude/sky nuisance coefficients using one checkerboard subset of unmasked, finite source pixels; calculate RMS residuals on the other same-source pixel subset. Perform the identical nuisance fit, fitting radius, source masking, pixel parity and background treatment for the **native same-date spatial DAOPhot source PSF** reconstructed at the same heldout native detector location. Compare the two models by
[
  q=rac{mathrm{RMS}_{m empirical,heldout}/sigma_{m sky,MAD}}
          {mathrm{RMS}_{m native,heldout}/sigma_{m sky,MAD}}
   =rac{mathrm{RMS}_{m empirical,heldout}}
          {mathrm{RMS}_{m native,heldout}} .
]
A lower (q) indicates a lower **descriptive image-pixel residual under this specific fit**, not a statistically significant astrophysical preference, calibrated PSF accuracy, confirmed source identity, or guaranteed source-specific photometric improvement.

When the same field has multiple exposures, models are rebuilt separately using original source images from each exposure. Differences across dates are not treated as independent star samples; each repeated Gaia ID remains a repeated measure on the same candidate source.

## CCD pixel-noise model: what is and is not known

The old pixel analyses normalized residuals by a **robust annular sky MAD proxy**. v1.19 adds a controlled, **metadata-only gain sensitivity**:

- Extract gain in **electrons per DN** only if one of the original FITS header keywords `GAIN`, `CCDGAIN`, or `EGAIN` exists with a finite, physically plausible numerical value (0.2–20).
- Record original read-noise only if a valid FITS keyword `RDNOISE`, `READNOIS` or `RON` exists; neither gain nor read noise is guessed or copied from an unrelated exposure.
- The annular MAD contains sky/read-noise fluctuations, so a model with documented gain may add the *incremental positive stellar source Poisson variance* in DN² ((max(A P,0)/g)) to the measured sky MAD². Read-noise metadata is not double-counted on top of a sky noise estimate that already includes read noise. Without documented gain, no source-shot-noise term is imputed.
- The resulting optional per-pixel variance is still a **proxy, not a calibrated inverse covariance**: original image resampling correlates pixels; gain uncertainties, background systematics, time/colour, sky-nebulosity variation and source blending are unknown. **No χ² calibrated confidence interval, WCS precision or false-detection significance** can be derived.

## Scientific evidence and next milestone

The original four historic ZTF science frames, 2,212-row manifest-checked IRSA position-cone photometry, two fresh 210″ Gaia DR3 wide cones, old and new Gaia exact 5D formal covariance queries, native `psfcat.fits`, `sciimgdao.psf` and center-FITS source provenance and original science/mask pairs all remain **ephemeral**. Code, synthetic/adversarial tests and derived source SHA-256 and scalar source-quality/PSF residual metrics alone may appear in public Git and GitHub Actions.

This process proves a better **software-level source-disjoint model evaluation design**. It still cannot prove any star was excluded from the *original historical ZTF PSF-building star sample*, or that its Gaia ID is the true physical source. The original DR3 CIDA 11 target high RUWE (≈8.57), possible unresolved neighbors and nebular background remain concerns. Results of the real observed-data run are reported separately rather than inferred from synthetic performance.

**Next:** build a robust multi-exposure/multiband empirical reference PSF under explicit training/holdout source lineage, quantify correlated CCD noise and celestial WCS errors on externally validated true stellar matches, and test historical residual-review objects against independent source images. This scientific-software project can be complete as a reproducible portfolio with clearly disclosed instrumental data limitations even if no astrophysical discovery is confirmed.
