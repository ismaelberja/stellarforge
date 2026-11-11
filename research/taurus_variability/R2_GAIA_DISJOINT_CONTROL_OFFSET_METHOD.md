# Taurus R2 — preregistered Gaia-only source-disjoint field controls and original ZTF catalogue offsets

**Method fixed 11 November 2026, prior to the new original archive queries.**

## Motivation

After the four original ZTF `sciimg.fits` + `mskimg.fits` pairs for **FT Tau** and **CIDA 11** were successfully evaluated in [the previous R2 source-gate step](R2_REAL_FT_TAU_CIDA_11_FITS_SOURCE_GATES.md), a remaining concern is whether the proximity of the nearest original pipeline `psfcat.fits` source to Gaia is **shared by other stars in the same field**. A small, preselected Gaia-only control set can identify common signed coordinate offsets; it **cannot** independently calibrate the native ZTF WCS or prove a particular ZTF object belongs to the named physical star.

## Sources and cohorts fixed before this run

The exact **four historical original ZTF g-band exposures** (FT Tau MJD 58388.389016 and 58491.184780; CIDA 11 MJD 58475.113750 and 58849.135984) and original OIDs remain unchanged. No science date or sky region is chosen in response to measured residuals.

- **CIDA 11 strict field controls**, all originally selected from Gaia alone in [StellarForge v1.17](../../reports/new_gaia_holdouts_v1.17/REAL_DISJOINT_GAIA_CONTROL_AND_SHIFTED_SKY_RESULTS.md), before looking at current original ZTF pixels: Gaia DR3 source IDs `3419109222512317056`, `3419109840987851136`, `3419157944621312896`, `3419111451598996992`. These were excluded from the earlier v1.8 reference source list.
- **FT Tau exploratory field control**, originally selected in a *relaxed* Gaia-only v1.18 cohort because **zero stars met strict v1.17 selection limits**: `149623298952568064`. It is **one** Gaia control, not a statistically sufficient field-calibration sample, and **not comparable in selection quality to CIDA 11's strict controls**.
- Target Gaia DR3 identifiers are fixed: FT Tau `149623711269425408`; CIDA 11 `3419110734340795648`.
- The original full **seven Gaia DR3 formal 5-parameter records** are retrieved by exact source ID through Gaia@ARI TAP. This model includes approximate geocentric geometric annual parallax and correlated *formal* Gaia covariance, but does **not** include Gaia unresolved multiplicity, atmospheric/color refraction, Palomar topocentric apparent place or full telescope/instrument errors.
- ZTF source coordinates come from the **original dated native per-exposure `psfcat.fits`** catalog, fetched from the official NASA/IPAC IRSA archive, using each **exact historical OID and MJD** to reconstruct the original `field/filter/CCD/quadrant` filename.

## Fixed comparison

For the target and each preselected same-field control, use the existing conservative native ZTF PSFcat screen (nearest native source within 1 arcsec, profile/flag QC, no second local source inside the fixed crowding radius). Reject/flag missing or duplicate source IDs and original-data failures; never substitute a better-looking star after observing results.

For provisional accepted source labels only, measure the signed tangent-plane offsets **native survey catalogue position minus Gaia-predicted epoch position**, in milliarcseconds:

`east = ΔRA × cos(Dec_Gaia) × 3,600,000 mas/deg` and
`north = ΔDec × 3,600,000 mas/deg`.

Use a robust *descriptive median* per axis across **strict, low-RUWE accepted Gaia controls only**. A provisional target-minus-control differential offset is allowed **only if at least three strict Gaia-only controls pass the native PSF fit and Gaia quality filters and the target itself passes those gates**. The FT Tau relaxed exploratory single-control tier never qualifies for that correction. A high Gaia RUWE on the target (as for CIDA 11, ~8.57) blocks the corrected-target claim even with sufficient field controls.

The result is not an instrument WCS calibration, not a Gaia–ZTF posterior probability, and not a new discovery. Source-disjoint Gaia control IDs have **not** been verified as absent from the *original ZTF DAOPhot PSF training-star roster*. ZTF native PSFcat source positions and detector FITS WCS share an instrument processing system, so neither represents independent instrument astrometric truth. The original science FITS images/masks were already separately checked in the preceding R2 experiment, and this follow-up does not add any new astronomical observation epoch.

## Expected no-go contingencies

If fewer than three CIDA controls survive Gaia/native PSF QC at a given MJD, report **UNDERPOWERED** and withhold target correction. FT Tau has exactly one exploratory reference, so **no robust field correction** can be claimed. CIDA 11 may have accepted control candidates but an extremely high target RUWE; then report **TARGET_ASTROMETRY_REVIEW** instead of interpreting any residual as companion motion.

The original R1 full 24-source technical Taurus denominator is unchanged; this experiment applies to only two piloted targets. No new companions, variability amplitudes, periods, physically confirmed Gaia/ZTF identities, original Luhman publisher membership or Taurus population inference follow from this control screen.

## Reproduction

- New code: `src/stellarforge/r2_gaia_heldout_native_offsets.py`
- Entry point: `python -m scripts.run_taurus_r2_gaia_heldout_offsets`
- Live GitHub Actions: `.github/workflows/taurus-r2-gaia-heldout-native-offsets.yml`
- Original source data remain **only in ephemeral runner memory**. GitHub stores bounded *derived* per-source status and offset metadata, SHA-256 original-source fingerprints, and explicit negative scientific claims.
- Official [Gaia DR3 source catalogue](https://gea.esac.esa.int/archive/documentation/GDR3/Gaia_archive/chap_datamodel/sec_dm_main_source_catalogue/ssec_dm_gaia_source.html) and [ZTF per-field/CCD/filter catalogue source architecture](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html).

**Full R2 Gaia–ZTF physical source identification remains open.**
