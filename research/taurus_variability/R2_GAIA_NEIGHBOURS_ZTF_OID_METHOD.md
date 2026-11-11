# Taurus R2 — Real Gaia-neighbour and ZTF-OID positional screening

**Method frozen 11 November 2026. This is not a physical crossmatch.**

This phase follows the [original 24-source exact Gaia DR3 ID screen](R2_REAL_GAIA_24_EXACT_ID_SCREEN.md)
(24/24 exact source records returned; 17 passed preliminary Gaia-only
quality screening; 7 had RUWE >=1.4). It expands the investigation
without allowing subjective target down-selection.

## Data provenance and selection

For each of **all 24** previously fixed and deliberately nonrepresentative
Taurus technical seed Gaia IDs:

1. Request one **15-arcsec Gaia DR3 cone** centred on the frozen
   secondary-catalogue seed J2016 coordinates using the existing
   Gaia@ARI TAP endpoint and a maximum of 200 catalogued stars.
   The Gaia source identifier must appear in the returned cone; a
   truncated query never establishes that the field is uncrowded.
2. Measure separation of **catalogued Gaia neighbours** relative
   to the exact Gaia source, propagating their Gaia proper motions to
   nominal J2021.0. Count neighbours within 2 and 5 arcseconds. This
   is **not a guaranteed blend/no-blend classification**, because
   unresolved or non-Gaia sources may still contaminate ZTF.
3. Make one bounded **official IRSA ZTF positional query** within
   2 arcsec of the original seed centre, with a *technical
   transfer-size limit* NOBS_MIN=5, not a quality criterion.
   Parse original OID/filter/time/photometric flags and keep
   all distinct lightcurve groups. Do not merge ZTF objects.
4. For MJD observations with available ZTF object positions and
   Gaia proper motion, compare the survey's reported positional
   proxy with the Gaia predicted position at each recorded epoch.
   A 2-arcsec separation gate is only an exploratory screen. It
   **omits annual parallax, a validated survey WCS, source-specific
   centroid covariance, PSF blending and source-association
   uncertainty**. One nearby ZTF OID is *still not a confirmed
   Gaia–ZTF match*. Multiple OIDs in the same band are flagged.
5. If a Gaia or IRSA query fails, the original response is malformed,
   or the bounded response exceeds the cap, report the status
   **unavailable or ambiguous**, not a lack of stellar variability.

## Reproducibility and privacy

- Script: \`python -m scripts.run_taurus_r2_counterpart_screen\`
- Reused validated parsers: \`stellarforge.v14_field_review\`,
  \`stellarforge.ztf_photometry\`, and
  \`stellarforge.association\`.
- New library: \`stellarforge.r2_counterpart_screen\`.
- The actual original archive queries are run in the
  [manually-rerunnable R2 GitHub Actions workflow](../../.github/workflows/taurus-r2-neighbors-ztf-oids.yml)
  and produce a derived, **no-raw** 24-source JSON ledger.
  Raw TAP/IRSA CSV bytes, original FITS, image pixels, original
  stellar time-series tables and any private data are excluded
  from repository commits and the output artifact.

## Scientific status and next acceptance gate

This Gaia/ZTF positional screen can **identify review priorities**,
but cannot by itself complete R2's goal of an independently verified
physical Gaia-to-ZTF source association. A final identification needs
original ZTF image/mask/PSFcat evidence at matching observing epochs,
independent reference WCS/crowding review, original literature
membership validation and uncertainty propagation. The 24 original
technical targets may not be used to estimate unbiased Taurus
population statistics.

The v2.0 engineering software portfolio remains complete, and
this is **optional research**, not a new claim of an astronomical
discovery, companion detection, source variability, or independently
calibrated instrument PSF/WCS.

## Official documentation

- [NASA/IPAC IRSA ZTF lightcurve queries](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html)
- [Gaia DR3 catalogue source definitions](https://gea.esac.esa.int/archive/documentation/GDR3/Gaia_archive/chap_datamodel/sec_dm_main_source_catalogue/ssec_dm_gaia_source.html)
