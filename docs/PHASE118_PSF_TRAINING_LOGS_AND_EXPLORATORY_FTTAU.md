# Phase v1.18 — Original ZTF DAOPhot PSF training-star provenance audit and FT Tau exploratory controls

**9 November 2026 · Real archival pipeline-log evidence and a separately labeled Gaia exploratory sample.**

## Why this phase exists

StellarForge v1.17 examined four Gaia DR3 source IDs that had never been part of the project's original ten-source FT Tau/CIDA 11 technical sample. Six original science+mask source-PSF pixel fits were completed in the CIDA 11 field with provisional same-source pixel-residual QA. Yet **disjoint Gaia source IDs do not establish an independent instrumental PSF calibration**, because the original ZTF pipeline may have selected any of these newly studied stars as PSF training stars. The original DAOPhot training roster's membership remained unknown.

The other issue was **selection coverage**. The strict v1.17 Gaia 210″ wide-cone screening produced **zero eligible new FT Tau controls**, although the field had 50 Gaia entries (by original report), while CIDA 11 offered 20 before a four-source budget. Reusing some of the old ten Gaia IDs would not be a true new-source control; relaxing source quality silently after viewing masked PSF residuals would compromise the comparison.

The phase therefore has two **distinct** tasks: original survey pipeline **log/provenance verification**, and a **preregistered exploratory** FT Tau Gaia-only selection that never gets misrepresented as having strict v1.17 source quality or being absent from original ZTF PSF construction.

## 1. What the ZTF public archive actually defines

The official [NASA/IPAC ZTF science image product API](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html) lists the following separate dated-science products:

- `sciimg.fits`: original science image;
- `mskimg.fits`: its detector bitmask image;
- `psfcat.fits`: catalogue of **sources measured using a fitted PSF**;
- `sciimgdao.psf`: spatially varying PSF model in native DAOPhot lookup-table format;
- `sciimgdaopsfcent.fits`: the model evaluated at the original detector field center;
- `sciimlog.txt`: instrumental image-calibration processing log;
- `log.txt`: overall real-time pipeline processing log.

The [ZTF Science Data System explanatory documentation](https://web.ipac.caltech.edu/staff/fmasci/ztf/ztf_pipelines_deliverables.pdf) describes **PSF estimation as a separate reduction stage** from subsequent detection and PSF-fit photometry. An original `psfcat.fits` `sourceid` is a *per-exposure catalogue source counter*, not a reliable training-star ID and **not a Gaia DR3 source ID**. The output catalogue can include many stars that did not contribute to PSF fitting.

An archived processing log may document model construction, failures, warnings and aggregate counts. **Such records do not in themselves establish the identity of the original fitted PSF's training stars.** Before asserting any particular Gaia DR3 object was excluded from model construction, one would require a validated source-level roster with documented detector-coordinate/source-ID namespace, exact original science-exposure provenance and sufficient completeness. Nothing is inferred by checking if a Gaia ID string appears or does not appear in a text log.

### Audit design

For each of the four historical original single-exposure science filenames previously fixed by the SHA-checked v1.8 reference ledger, replace only its original `_sciimg.fits` suffix with `_sciimlog.txt` and `_log.txt`. No cutout query is sent for textual logs. Accept **only original NASA/IPAC HTTPS product URLs**, reject untrusted domains/redirects, and bound each read to at most **2 MB**, with timeouts and strict text decoding; original raw log text remains in ephemeral runner memory.

For each original file available, publish a SHA-256 hash, file size, original log line count, count of lines mentioning PSF/DAOPhot and bounded aggregate count matches when plainly present. **Do not publish raw processing logs or unverified source-coordinate lists.**

Even an accessible and informative log returns the scientific status **`NOT_VERIFIABLE_FROM_THIS_LOG`** for PSF-training source membership unless a fully documented, validated training-star roster is available. The present code does not claim to independently authenticate such a roster; a missing log, HTTP 503 or returned archive error page is a transport/data limitation rather than evidence that a star is absent from the PSF training set.

## 2. FT Tau source preselection: preserve strict vs exploratory evidence tiers

The strict v1.17 Gaia-only selection excludes all ten previous project source IDs, requires 40″–165″ target separation, G≈13–18.5, Gaia flux SNR≥50, RUWE <1.4, ≥10″ nearest Gaia source separation, clean full five-parameter astrometry and source quality, and no duplicate sources. **It is rerun unchanged first**, and reported separately.

After v1.17 established zero eligible additional FT Tau sources, this new phase **predeclares a distinct exploratory tier before inspecting any current ZTF catalogue or pixel residual**:

| Gaia selection dimension | Unchanged v1.17 strict tier | Predeclared v1.18 exploratory tier |
|---|---|---|
| Exclusion of all original ten technical target/reference Gaia IDs | Required | **Still required** |
| Target-field separation | 40″–165″ | 20″–190″ |
| Gaia G magnitude | 13–18.5 | 12–19.2 |
| Gaia G flux over error | ≥50 | ≥30 |
| Gaia RUWE | <1.4 | <1.6; ≥0.5 |
| Distance to *every* Gaia DR3 catalogue source | ≥10″ | ≥6″ |
| Gaia duplicate-source flag and astrometric parameter solution | Clean 5/6 parameter solution | **Same** |
| Formal RA/Dec and proper-motion uncertainties | ≤3 mas, ≤3 mas/yr | **Same** |
| Representation across sky quadrants | One per occupied quadrant first | **Same** |
| Maximum selected IDs | Four per target | Four **exploratory** FT Tau IDs |

These are **deliberately different selection strata**, not comparable scientific single-star samples. Lower Gaia brightness/astrometric isolation thresholds increase the possibility of unreported neighbors, unresolved binaries, faint-source noise or Gaia/ZTF identity mistakes. Even if the exploratory sample yields excellent masked science-pixel PSF residuals, it cannot be retroactively labeled as strict or used to claim an unbiased independent calibration.

All candidate IDs, Gaia positions, RUWE and separation quality diagnostics are computed **before** examining `psfcat.fits` or source-image pixels. The independently fetched Gaia DR3 wide-cone response is hashed, and all selected Gaia source IDs are re-queried for their own complete formal five-parameter astrometric covariance and first-order geometric Earth-geocentric annual parallax at the true original image MJD.

## 3. Genuine source ZTF masked PSF diagnostics, if eligible FT Tau stars exist

Use the **same original two FT Tau historic single-exposure g-band dates** from the SHA-checked historical ZTF positional acquisition. Candidate Gaia-predicted sources must have an original native `psfcat.fits` detection within 1″ and satisfy the v1.14 conservative native source/PSF-fit screening (SNR ≥5, `chi` 0.5–1.5, `sharp` −0.5 to 0.5, original mask-derived quality flags and source ambiguity/crowding exclusion). Never count a poor, missing or marginal native source as an astrophysical non-detection.

When a candidate passes the original catalogue gate, download its genuine same-date `sciimg.fits` and `mskimg.fits` as a 60″ sky-centered source cutout, verify original science/mask WCS pixel registration ≤0.05 pixel and original detector `xpos/ypos` subpixel phase consistency ≤0.22 pixel, mask the official deleterious 6141 ZTF bit flags including saturation, and fit only amplitude plus sky plane in original source DN units using the local, fixed native spatial DAOPhot PSF reconstructed from original `sciimgdao.psf` with its 23×23 model stamp.

Only one checkerboard half of the original source pixels participates in estimating four nuisance coefficients; the other half is withheld to report RMS and positive-residual diagnostics against an annular sky MAD *noise proxy*. These **withheld pixels are not an independent stellar PSF calibration**, and the source's membership in the actual ZTF DAOPhot PSF construction sample remains unknown.

Optional ±25″ fixed shifted-sky native ZTF catalogue controls are recorded as **descriptive local source-density checks**, not a calibrated accidental-source-match rate.

## What this evidence cannot establish

- A processing-log PSF mention or aggregate count is **not** a source-by-source PSF training roster.
- Absent Gaia IDs in a text log, if any, are **not** proof that those Gaia stars were absent from the PSF model's original training set.
- The exploratory FT Tau sample is **not scientifically interchangeable** with v1.17 strict Gaia-only controls or independent clean field stars.
- A close native catalogue detection is **not** authenticated Gaia–ZTF astrophysical identity.
- A same-image PSF residual ratio is **not** independently calibrated local PSF or WCS precision, a Gaussian detection significance, a physical companion or source variability.
- Any missing 503 FITS/log response is source-access uncertainty, not an astronomical nondetection.
- Original ZTF/Gaia source files, native PSF/CCD pixel arrays, original photometry and raw logs are transient; public Git contains only validated code, synthetic tests, hashes and derived bounded numeric summaries.

## Final scientific validation gate

An actual **complete original ZTF DAOPhot training-star roster** with explicitly source-ID/CCD-coordinate-matched membership, or an **independently built PSF** from a separate, documented reference-star set, is needed to claim independent PSF model training/holdout validation. Combined with actual independently vetted Gaia/ZTF sources, representative multi-epoch/dual-filter original science pixels, realistic CCD correlated variance, proper mid-exposure apparent-place and spatial WCS calibration, this would support a final instrumental uncertainty model.

A v2.0 portfolio release can still be scientifically honest even if a private/absent survey training roster is unavailable: clearly report the limit and do not convert internal model consistency into a new astronomical discovery.
