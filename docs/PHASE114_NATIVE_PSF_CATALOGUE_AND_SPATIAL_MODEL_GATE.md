# StellarForge v1.14 — ZTF native PSF catalogue cross-identification and spatial PSF provenance

**8 November 2026.** This milestone investigates source *candidates* directly in the original, per-science-exposure ZTF `psfcat.fits` catalogues. It does **not** claim authenticated Gaia–ZTF physical crossmatches, a localized spatial PSF model, instrument astrometric precision, or a new astronomical discovery.

## Official evidence and source definitions

The [IRSA ZTF metadata product specification](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html) documents two relevant original products alongside each dated `sciimg.fits` exposure: `psfcat.fits` — the **native PSF-fitting source catalogue**, and `sciimgdao.psf` — the **spatially varying DAOPhot lookup-table PSF model**. They are different from the `sciimgdaopsfcent.fits` image stamp **at the center of the detector field** retrieved in v1.13.

The official [ZTF Science Data System explanatory supplement, v5.0 (10 June 2020), §10.6](https://irsa.ipac.caltech.edu/data/ZTF/docs/ztf_explanatory_supplement.pdf) explicitly defines native `psfcat.fits` source table columns: `sourceid` (a source counter **within a native image**), `xpos/ypos` in original CCD-quadrant coordinates, `ra/dec` in degrees, `flux/sigflux`, `mag/sigmag`, `snr`, `chi`, `sharp`, and `flags`.

- `chi` approximately describes the source's model residual RMS compared with noise; a source with `chi` much larger than one is a poor PSF fit.
- `sharp` describes a PSF-shape difference: large positive values can indicate extension; strongly negative values can indicate sharp pixel artifacts.
- `flags=-1` indicates a source near the detector edge. Other flag values encode bitwise-OR of `mskimg.fits` bits in a small patch centered on the extraction; the separate official [ZTF mask-bit policy](PHASE113_OFFICIAL_ZTF_MASK_AND_NATIVE_CENTER_PSF.md) identifies **6141** as deleterious-bit template, distinct from source-detection marker bits.
- A source may have a good profile and still be blended, falsely identified, or part of an unrelated background object. A `sourceid` is **not** Gaia DR3 `source_id` and not a stable ZTF light-curve OID across independent exposures.

## Source list, product provenance and network controls

Reuse exactly the same four preregistered original dated ZTF science exposures and ten Gaia DR3 exact IDs from the original SHA-verified **2,212-row** IRSA positional-cone acquisition and immutable v1.8 derived candidate-reference ledger. The positions are propagated individually using the full formal five-parameter covariance and first-order **Earth-geocentric annual geometric parallax**, **not** a full Palomar topocentric apparent-place model. Original FITS timing, independent Gaia–ZTF identity and high CIDA 11 RUWE remain explicit uncertainties.

Build the original `psfcat.fits` and `sciimgdao.psf` URLs **by replacing only the suffix of the original dated official ZTF science image product**, preserving original date, field, filter, CCD and quadrant. Download complete native products **without a square-image cutout query** — the official PSF catalogue and spatial DAOPhot table are not star-centered FITS pixel cutouts. Reject unsupported hosts, protocols, redirects, product classes and paths; cap native FITS table to 48 MiB and DAOPhot source to 4 MiB with explicit time budgets.

The native PSF catalogue is parsed with Astropy FITS binary table support; the module requires a single unambiguous binary table with all §10.6 columns, distinct integer `sourceid` values, finite valid ICRS/nonnonsense coordinates and at most 120,000 native rows. Malformed catalogue data must be recorded as unavailable/invalid, **not** silently converted to astronomical nondetections.

No native per-source FITS rows, Gaia TAP CSV or original IRSA/ZTF photometry are written to Git or uploaded in the workflow artifact; only source IDs, bounded nearest-source separation and PSF-quality diagnostics, original source/product hashes and errors are published.

## Proposed source-candidate and fit-quality gates

For each Gaia candidate at the dated ZTF exposure:

1. Search in the same original ZTF native `psfcat.fits` catalogue. Consider the nearest native PSF source a **possible positional association** only when separation is **at most 1.0 arcsec**, not a confirmed astrophysical identity or calibrated posterior probability. Catalogue entries within 5″ help detect possible nearby PSF-fit sources.
2. Apply conservative *screening* (not ZSDS-certified physical acceptance) thresholds: `0.5 <= chi <= 1.5`, `-0.5 <= sharp <= 0.5`, native PSF SNR at least 5, positive fitted flux/error, no bad mask-bit intersection with **6141** and no detector edge `flags=-1`.
3. If a **second PSF catalogue source is within 3 arcsec** of the candidate, report a possible *crowded-source review* instead of an unblended single star. It cannot exclude undetected/unresolved neighbors.
4. A native sequential source ID may never be provisionally accepted as the unambiguous counterpart to **two different Gaia DR3 source IDs in one exposure**. Flag the duplicate assignment for manual investigation.
5. If a catalogue file is unavailable with HTTP 503, a source is missing at the chosen radius, or model flags fail, label it **unavailable or provisional review**. These conditions are not proofs of an astrophysical nondetection, source independence, a binary, or physical variability.

The thresholds are intentionally conservative diagnostic filters; the actual completeness, false-match rate, instrumental PSF residual distribution, population/brightness/color dependence and source selection bias are **not quantified** by this small pilot.

## Native spatial PSF format limitation

The companion official `sciimgdao.psf` is a spatially varying DAOPhot lookup-table product. Merely downloading it and recording a SHA-256/byte count **does not** establish that its format has been decoded or that the PSF has been evaluated at the native `xpos/ypos` of the target/ref stars. This phase therefore reports only its availability and provenance. No local PSF image, calibrated PSF photometry, astrophysical blend clearance, or spatial WCS residual is derived from the raw DAOPhot bytes.

**Future substantive gate:** verify the exact DAOPhot format and evaluate a position-dependent PSF at original native CCD-quadrant coordinates for sufficiently numerous and independently authenticated field stars. Validate the reconstructed spatial PSF against same-date original `sciimg.fits` and `mskimg.fits` pixels and catalog residuals on held-out stars.

## What the results must *not* imply

- A 1″ positional nearest neighbor in a catalogue is not a confirmed physical Gaia–ZTF crossmatch.
- Absence from `psfcat.fits` is not necessarily absence on the sky; source catalogues have detection limits, masking biases, seeing and blending.
- `chi`, `sharp` and flags are pipeline diagnostics; they cannot on their own establish a clean PSF, absolute WCS error or physical multiplicity.
- The predicted Gaia positions are catalogue-formal, not complete instrument/error-physics astrometry. CIDA 11 target RUWE ≈8.57 remains problematic.
- A downloaded `sciimgdao.psf` file, like the v1.13 field-center stamp, is not a successfully *evaluated source-local* PSF.
- Every archive HTTP 503 is transport uncertainty, never astronomical absence.
- No physical light-curve event, companion discovery, science selection fraction or astrophysical association should be claimed.

## Reproduce

```bash
python -m pip install -e '.[test,analysis,images]'
python -m pytest -q
python scripts/run_v114_native_psfcat_gaia.py /path/to/verified_original_IRSA_acquisition.zip \
  --gaia-timeout 25 --archive-timeout 12 --require-some-native-products
```

The original SHA-verified survey data ZIP must be available in a temporary local location or recovered from the original acquisition run while its artifact is valid. Source products accessed through official IRSA are bounded and kept ephemeral. The resulting JSON/Markdown are the **only public artifact output**.
