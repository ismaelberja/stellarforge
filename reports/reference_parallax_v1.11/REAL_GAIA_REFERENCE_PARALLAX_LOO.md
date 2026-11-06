# StellarForge v1.11 — Real Gaia DR3 reference-star parallax and covariance sensitivity

**Observed-data validation: 6 November 2026.** [GitHub Actions v1.11 official Gaia DR3 run](https://github.com/ismaelberja/stellarforge/actions/runs/42254052752). **484 automated tests passed.**

**Scientific boundary:** This is a **retrospective astrometric sensitivity check of provisional Gaussian FITS image offsets**, **not** an independent ZTF WCS calibration, physical Gaia–ZTF crossmatch, calibrated empirical PSF, new companion or stellar variability discovery.

## Actual input and provenance

The v1.8 real-image pilot obtained **13 fitted Gaia candidate reference images across four real dated ZTF science exposures**, plus model fits for FT Tau/CIDA 11. That small derived v1.8 evidence ledger, including original source run ID `42077605987` and original aggregate SHA-256 `fb7d5c315cbef56b2551e73920c67920827d91160b4c0bd35f3fd77113166beb`, was published in v1.10 as [a reduced reusable dataset](../../data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json). It contains measured nominal image centroid residuals and fit quality flags but **no raw ZTF FITS pixels, Gaia TAP CSV, or original photometric measurements**.

For v1.11 we independently retrieved, by **10 exact Gaia DR3 source IDs**, all five astrometric components, five formal errors, and **10 pairwise correlations**: **eight candidate references and the two targets**. All 10 catalogue entries had sufficient information to propagate the five-parameter **formal Gaia covariance** and geometric geocentric annual parallax to the original four observational MJDs, provisionally interpreted as UTC.

The official original Gaia CSV is **not** included in Git or attached artifacts. Its response SHA-256 is `688e7cfcda6f528d58bc1f92c44b86396de905eef2e28d0db4ce28d4558aa545`, allowing provenance checks without redistributing raw catalogue rows. The bounded query SHA-256 is `64a8d0a394c5c8e4ac42c8de94429aed17a46a62486d9cea02f45545b283775e`.

## Exactly what the correction does

In v1.8, an image Gaussian centroid was compared with a Gaia coordinate propagated by **linear proper motion only**. For each candidate reference, v1.11 changes **only the Gaia predicted position**, applying the individual star's epoch-dependent **first-order geometric Earth-geocentric annual parallax**. Thus, for east/north coordinates in arcseconds:

\[
\mathbf r_{\mathrm{new}} \simeq \mathbf r_{\mathrm{v1.8}} -
\frac{\boldsymbol{\Delta}_{\pi,\mathrm{Gaia}}}{1000}.
\]

It propagates the same Gaia star's full formal five-parameter covariance into the 2D tangent plane, but does **not** convert it into a calibrated ZTF instrument error, fit weight or physical source-identity confidence. **No ZTF pixels, Gaussian profile model parameters or original FITS WCS headers were re-fitted.**

The original v1.10 reference-quality screen is frozen, then leave-one-reference-out (LOO) median-shift statistics are recalculated with the corrected east/north reference residuals. The **strict** branch excludes flagged/poor-fitting Gaussian image models.

## Real reference-star parallax-sensitive results

| Target | Original ZTF MJD (UTC assumed) | Valid strict refs | Original strict LOO RMS | Gaia-parallax-adjusted strict LOO RMS | RMS change |
|---|---:|---:|---:|---:|---:|
| FT Tau | 58388.389016 | 1 | insufficient | insufficient | — |
| FT Tau | 58491.184780 | 3 | 0.075782″ | **0.075770″** | **−0.012 mas** |
| CIDA 11 | 58475.113750 | 4 | 0.093046″ | **0.092971″** | **−0.075 mas** |
| CIDA 11 | 58849.135984 | 2 | insufficient | insufficient | — |

For all 13 reference-image observations, the maximum absolute geometric annual parallax displacement of an individual reference was **0.60918 mas**, and the **median Gaia-only formal positional uncertainty** was **0.15786 mas east / 0.11637 mas north**.

The CIDA 11 MJD 58475.113750 target-minus-reference corrected residual is **(+0.064578″ east, −0.060085″ north)**, with magnitude **0.088207″**, but that is **only a nominal image/model offset after correcting predicted coordinates**, not an astrophysical motion, real calibrated centroid uncertainty, confirmed ZTF object identity, or valid target physical interpretation. The CIDA 11 target has **Gaia RUWE ≈ 8.57**, so the formal single-star Gaia covariance may substantially underestimate true astrometric-model systematic errors.

**Key conclusion:** for these particular reference candidates, Gaia parallax corrections have a **small effect on cross-validated internal reference disagreement**, far below the original ~76–93 mas LOO discrepancies. This does not establish which instrument or astrophysical effect dominates: unmodeled PSF, different references, catalogue errors, WCS distortion, spatial selection or correlated systematics all remain possible. It does, however, show that **Gaia reference-star annual parallax alone does not resolve the observed disagreement in this sample**.

## Scientific safeguards

- Every one of the eight reference stars and both target Gaia catalogue IDs has been propagated using **its own 5×5 formal Gaia covariance**, but reference Gaia quality screening is **not** a source-identity or single-star PSF authentication.
- LOO errors from three–four reference candidates measure **internal sample disagreement**, not an independently measured detector WCS accuracy, Gaussian confidence bound or externally validated instrumental noise.
- Geometric parallax was computed for an Earth-centre observer with an offline built-in ephemeris. Palomar topocentric apparent places, relativistic aberration, atmospheric refraction, optical distortions, radial-velocity perspective and exact FITS timing checks remain unmodeled.
- The revised Gaia catalogue source positions have not been used to *refit* ZTF pixels. This is explicitly a sensitivity comparison, not a new observational reduction.
- The **strict eligibility remains 2/4 exposures**; parallax must not be used to override an unacceptable Gaussian model or poor field-reference set.
- High RUWE for CIDA 11 may indicate a problematic single-star astrometric model; it does not on its own prove multiplicity.
- The v1.8 pilot covers only **one g-band ZTF OID per target**, not all six original OID/filter combinations.

## Reproducibility

Code: [Gaia parallax reference sensitivity](../../src/stellarforge/v111_reference_parallax.py), [bounded real pilot](../../scripts/run_v111_reference_parallax.py), and [test suite](../../tests/test_v111_reference_parallax.py). Run:

```bash
python -m pip install -e '.[test,analysis,images]'
python -m pytest -q
python scripts/run_v111_reference_parallax.py \
  --ledger data/research_seed/V18_DERIVED_REFERENCE_OFFSETS_NO_RAW.json \
  --output reports/generated/v1.11_reference_parallax
```

The script queries only ten exact public Gaia DR3 source IDs; it requires network access but **does not** retrieve raw ZTF/FITS data. The GitHub Actions workflow uploads only derived aggregate JSON/Markdown and source/query hashes, never the actual Gaia TAP CSV response. The temporary aggregate artifact can be downloaded from [the official run](https://github.com/ismaelberja/stellarforge/actions/runs/42254052752).

**Independent calibrated ZTF instrument WCS solutions: 0. Authenticated empirical single-star PSFs: 0. Physical Gaia–ZTF source identifications: 0. New astronomical companions/variability events: 0.**
