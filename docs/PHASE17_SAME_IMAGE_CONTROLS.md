# StellarForge v1.7 — Unclassified same-image radial controls and ZTF image coverage

**Scientific state:** engineering method for examining instrumental image-shape consistency; not PSF calibration, source deblending, new stellar classification or Gaia–ZTF identity confirmation.

## Motivation

The v1.6 single-Gaussian-plus-plane proxy left high positive model residuals in all three accessible FT Tau science images. These residuals could arise from the real ZTF instrumental PSF, image resampling, nebulosity, artifacts or unrelated sky sources, and **cannot be interpreted as companions**. A more appropriate intermediate step is to compare the target to other image peaks in the *same exposure* before making any claims about spatial structure. The v1.6 real run also had **zero OID/filter groups with at least two usable independent science exposures**, so the sampling of external image archives needs careful extension.

## What the new code actually does

1. Reuses the original 2,212-row **SHA-verified IRSA ZTF position-query archive** for FT Tau and CIDA 11. The parent source association remains unverified.
2. For every ZTF OID/filter group, selects up to **six distinct observation filefracday values** spaced across the time-ordered, basic-quality-masked ZTF rows. Only original science-image dates can count as independent epochs. One coadded reference-image URL is retained as a fallback and is **never treated as an independent science exposure**.
3. Requests at most **90-arcsec square cutouts** from NASA/IPAC IRSA's [ZTF image API](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_api.html) using its [IBE FITS cutout interface](https://irsa.ipac.caltech.edu/ibe/cutouts.html). IRSA defines the science/reference naming conventions in its [ZTF product metadata](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html).
4. Reads original FITS pixel arrays into memory only, with the existing 3 MB file-size bound, valid 2D celestial WCS and Gaia J2016.0 position propagated to each exposure's approximate time (without full parallax or covariance).
5. Detects **unclassified brightness peaks** in the same field using a smoothed global local-maximum threshold. For a *candidate field control*, requires it to lie at least 13 pixels from the target, at least 16 pixels from an image edge, and 9 pixels from previously selected candidates. Each candidate needs a usable local annular background and finite radial flux profile.
6. Computes six normalized concentric pixel-ring flux fractions for the provisional Gaia-position target and candidate image peaks. If at least **two comparison peaks** have usable ring profiles, reports the difference from the control-ring median, with a conservative descriptive shape-review flag if the maximum absolute ring difference exceeds 0.12. **This is not a calibrated empirical ZTF PSF model.**
7. If at least two *distinct science FITS SHA-256s* from the same OID/filter yield image screens and Gaussian proxy offsets, optionally reports **descriptive** differences in their WCS-referenced centroid positions. These are **not a physical motion or astrometric consistency measurement**: WCS systematics and Gaia propagation uncertainties remain unmodeled.
8. Stops acquiring after a maximum of two accessible distinct science frames per group, or at the six-image bound. If all science attempts fail, a reference coadd may be queried once, but does not count towards independent-epoch comparison. HTTP 503/connection failures remain explicit image-access limitations.

## Strict scientific interpretation

- **A same-image control candidate is merely a brightness peak, not an authenticated star.** It may be a galaxy, artifact, nebular knot, cosmic ray, blended source, or a star with a different color/PSF. The method does not apply stellar-classification or color/magnitude matching.
- The target radial profile is centered at the Gaia-WCS-predicted location, not an independently astrometrically recalibrated centroid, and the three-to-six pixel rings are not photometric aperture calibration.
- A small target-control difference **does not prove a clean field**, and a large difference **does not prove a companion**. It only prioritizes human inspection and future empirical PSF calibration.
- Availability of two science FITS frames is necessary, **not sufficient**, for astrophysical repeatability: their zero points, image kernels, time scales, seeing, masks and astrometric systematics still need calibrated error budgets.
- A missing field control or missing image from IRSA (including HTTP 503) **does not mean an empty field or a non-detection**.
- CIDA 11's Gaia DR3 RUWE ≈ 8.57 remains an important astrometric-fit concern. Full Gaia parallax/covariance, independent neighboring-source imaging, original publisher Taurus membership verification and physical variability interpretation remain open.

## Usage and privacy

\`\`\`bash
python -m pip install -e '.[test,analysis,images]'
python -m pytest -q
python scripts/run_v17_field_controls.py /path/to/official_original_IRSA_archive.zip \
  --science-attempts 6 --timeout 5 --fail-if-no-science
\`\`\`

The original authorized photometric ZIP is required and SHA checked. No raw ZTF photometric CSV or downloaded FITS cutout is committed to public GitHub or attached as a workflow artifact. **Only aggregate numbers, diagnostics, hashes and failure statuses** are published.

## Scientific next gates

Independently authenticate the candidate field controls using source catalogues and high-quality images; match their brightness/filter and distance from field/saturated objects; model spatially variable instrumental PSFs and sky backgrounds; propagate full Gaia astrometric covariance/parallax; compare several truly independent frames with calibrated centroid uncertainties and observation-level WCS residuals; and re-run variability detection only after identifying any ZTF source physically. Until then: **zero independently confirmed new companions, zero validated deblended stars, zero physical events.**
