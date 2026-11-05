# StellarForge v1.8 — Gaia DR3 reference candidates and ZTF science-frame checks

**Research-software milestone, 5 November 2026.** This does NOT establish a calibrated instrumental PSF, independent WCS solution, confirmed Gaia–ZTF source identity, clean field, new companion or stellar variability event.

## Motivation

The v1.7 real-image audit recovered twelve individual ZTF science FITS images (two per each of six OID/filter groups) but found **zero 90-arcsec target cutouts with two usable, unclassified comparison peaks**. An image brightness maximum does not constitute an authenticated stellar PSF standard. The next defensible step is to obtain quality-screened Gaia DR3 candidate references and attempt real image-profile measurements in the **same dated ZTF science product** as each target.

## Input/provenance

The same original ZTF photometric acquisition ZIP is verified with its official IRSA query metadata, byte counts and SHA-256 from v1.3. It contains 2,212 positional cone-query photometric rows (FT Tau: 1,199; CIDA 11: 1,013) in six groups. Source association with Gaia is still unverified.

The Gaia DR3 synchronous TAP query returns a **210-arcsec ICRS cone, capped at 500 source rows**, including low-quality and faint objects for isolation checks. Candidate reference requirements:

- Exact original Gaia DR3 target ID and target position agreement within one arcsecond; reject truncated or malformed Gaia responses.
- Candidate Gaia DR3 G magnitude 13.0–18.5 and G-flux signal-to-noise proxy above 50.
- Gaia RUWE below 1.4, no duplicated_source catalogue flag, five- or six-parameter astrometric fit, available proper motion and limited DR3 position/PM errors.
- Candidate at least 40 and at most 165 arcsec from the target, and at least 10 arcsec from **any** Gaia record returned in the same field, not just quality-filtered stars.
- Up to five reference candidates per target. A Gaia quality-screened candidate can still be a blend, contaminated star, field artifact or otherwise inappropriate ZTF calibrator.

The source columns, RUWE definitions and Gaia quality flags are documented in the [official Gaia DR3 catalogue schema](https://gea.esac.esa.int/archive/documentation/GDR3/Gaia_archive/chap_datamodel/sec_dm_main_source_catalogue/ssec_dm_gaia_source.html).

## Image checks

For a strict pilot, only **one ZTF g-band OID and at most two dated science exposures per target** are sampled. Each candidate reference's estimated location is propagated with **2D Gaia proper motion only** to the science MJD. A new 45-arcsec official IRSA/ZTF FITS cutout is requested using the *same underlying original science image path and date* as the target exposure, changing only its cutout center. These are different sky-centered cutouts of the same detector product, **not the literal same 90-arcsec target pixel window**.

The existing v1.6 robust single Gaussian plus local planar background model checks the candidate image WCS, fitted center, approximate width/axis ratio and model residual. Fits are **instrumental profile proxies**, not authenticated point spread functions, WCS recalibrations, calibrated photometry or independent physical source matches.

A **provisional local translation** is computed only with at least three distinct Gaia source IDs, a non-edge constrained Gaussian model, a nominal center within 1.5 arcsec of the expected Gaia position and agreement between the reference residual vectors within one arcsecond. The median east/north fit offset is used as a descriptive, source-identity-UNVERIFIED translation diagnostic.

An additional optional target-minus-reference residual subtracts that median from the target Gaussian WCS-referenced residual **only where the three-reference gate succeeds**. It is never labeled calibrated absolute astrometry; it excludes real Gaia parallax, perspective motion, full astrometric covariance, color-dependent refraction, ZTF distortion/PSF and field-star physical validation. CIDA 11's unusually high Gaia RUWE (~8.57) remains a serious warning.

## Real data pilot and caveats

Read [the actual v1.8 aggregate Gaia–ZTF reference report](../reports/gaia_reference_v1.8/REAL_REFERENCE_CANDIDATE_EVIDENCE.md), based on the public workflow [run 42077605987](https://github.com/ismaelberja/stellarforge/actions/runs/42077605987). It lists selected Gaia sources, real image-model counts and the remaining quality gates. The original raw catalogue CSV and all FITS pixels are excluded from public Git and action artifacts.

This does **not** perform a full per-exposure WCS distortion re-fit or calibrate an empirical spatially varying ZTF PSF. No Gaia catalogue filtering proves single-star status. Gaia G magnitude is not the ZTF g/r photometric system. Remote archive errors are access limitations, not astrophysical non-detections.

## Reproduce

    python -m pip install -e '.[test,analysis,images]'
    python -m pytest -q
    python scripts/run_v18_gaia_reference_pilot.py /path/to/verified_IRSA_input.zip --max-references 5 --exposures-per-target 2 --require-catalog

The historical official source artifact expires; after expiry, reacquire through official IRSA with a new, independently checked manifest and SHA-256 rather than pretending it is byte-identical.

## Outstanding scientific gates

1. Authenticate comparison sources beyond Gaia catalogue quality: extendedness, saturation, morphology, Gaia/ZTF colour differences and field-by-field instrument PSF.
2. Establish independent WCS distortion and realistic centroid uncertainty using validated field references and image registration (not merely a median translation).
3. Propagate Gaia full covariance/parallax, especially CIDA 11, before claiming physical motion or association.
4. Extend pilot to all original ZTF OIDs/filters, vetted reference sources and independent science epochs.
5. Verify publisher-original Taurus membership, disk classes and real-cadence sensitivity before astrophysical claims.

**Confirmed Gaia–ZTF physical identities: 0. Authenticated empirical PSF calibrations: 0. Independently calibrated WCS solutions: 0. Astrophysical companions or newly confirmed events: 0.**
