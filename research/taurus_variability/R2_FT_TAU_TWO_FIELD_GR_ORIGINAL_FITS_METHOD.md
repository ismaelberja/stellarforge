# Taurus R2 — FT Tau same-filter, two-field original ZTF science FITS/bitmask/PSFcat comparison

**Preregistered 11 November 2026 before the new original science-image request.**

## Motivation and frozen observational cohort

The [previous real original IRSA ObjectID/field study](R2_REAL_FT_TAU_CIDA_ZTF_ALTERNATIVE_OID_RESULTS.md) found **four** source-catalogue ObjectIDs within 2 arcseconds of FT Tau's original Taurus technical Gaia position: two g-band and two r-band records across two original ZTF `field/CCD/quadrant` configurations. The positional proximity of these labels is **not** a unique physical Gaia–ZTF identification, and their photometric time series must not be joined without stronger original image-level source validation.

This method freezes the four original ZTF OIDs and fields based entirely on the already published raw-survey-derived source ledger and on the unchanged **24-source Taurus R1 technical seed**. CIDA 11's previously documented unrelated two historical g-band exposures are NOT repurposed for this FT Tau field comparison.

| Filter | Original field / CCD / quadrant | Predeclared ZTF OID |
| --- | --- | --- |
| g | 1605 / 15 / 3 | `1605115300003377` |
| g | 609 / 8 / 4 | `609108400001155` |
| r | 1605 / 15 / 3 | `1605215300005161` |
| r | 609 / 8 / 4 | `609208400001969` |

The published source selection and its SHA-256 provenance MUST match the previous [R2 actual archive result receipt](../../reports/taurus_variability_r2/REAL_ALTERNATIVE_ZTF_OID_ORIGINAL_RUN_RECEIPT.json). No newly discovered, high-quality-looking ZTF OID, image epoch, filter or field is substituted.

## Fixed selection (prior to observing images)

For each original OID make **one** bounded NASA/IPAC IRSA `ID=<predefined OID>&FORMAT=csv` request, max 4 MB, max 1,500 returned original rows, 35-second timeout. Require the exact original OID, matching frozen band, ZTF field, CCD and quadrant, and valid original `filefracday`, numerical MJD and catflags. Use `catflags & 32768 == 0` solely for *technical original-exposure eligibility*, not for scientific source-quality certification. Never use magnitudes/variability, image appearance, number of neighbours, PSF-fit quality or closeness to Gaia to choose a date.

For each band separately (g and r), consider the qualified exposure metadata from the two different predeclared ZTF field/CCD groups. Choose the **unique deterministic pair** minimizing `|MJD_field1605 − MJD_field609|`; break ties by earlier observing date then original `filefracday`. Thus select **at most 4** original single-exposure science products in total, one per frozen ObjectID. Original data rows are discarded after selection.

The time difference is always recorded. **Only** a separation of at most **1 day** may be descriptively labelled close in date. A larger gap remains *NOT contemporaneous*, even when the images look similar. Neither case by itself permits combining the OID lightcurves or claiming an intrinsic source change. If any original OID does not return a usable exposure, **do not silently choose another OID/filter**. The pair is incomplete and logged as such.

## Same-exposure original image and source consistency tests

1. Retrieve the **one original Gaia DR3 FT Tau five-parameter astrometric record** by exact ID `149623711269425408` using Gaia@ARI TAP. Propagate the formal covariance/proper motion and approximate geocentric annual parallax independently to each selected original ZTF MJD. Gaia RUWE and systematic sources of error remain explicit; not a full topocentric/independent ZTF WCS calibration.
2. Construct the official dated `sciimg.fits` **60-arcsec source-centred science cutout**, then the matching `mskimg.fits` identical source-centred cutout, plus the original **full CCD-quadrant native `psfcat.fits`** from the same ZTF exposure. Never mix product dates/fields.
3. Check original image↔mask WCS, core bad/saturated ZTF mask bits, and the already validated robust bright-pixel peak screen. Independently query the authentic *native* full ZTF PSF catalogue for the nearest source and number of additional catalogued neighbours within 3 arcsec; record native profile/quality flags and relative position proxy.
4. For each band report the **difference between the two per-field native-catalogue-minus-Gaia signed east/north offsets**, but only as *descriptive* source positions. Requiring one matched source in each original per-field native catalogue is not the same as a unique physical crossmatch. No absolute uncertainty/significance is assigned because detector-specific ZTF WCS/PSF, astrophysical color and blend errors are not independently calibrated.
5. Treat original image/mask availability, PSF source quality and any close-in-time pass as **instrumental QA evidence only**. No original survey photometric table, native PSF catalogue source rows, image pixels or raw Gaia rows are committed; the workflow uploads only derived metadata, evidence SHA-256 and explicit uncertainty flags.
6. On service errors, malformed products, empty masks or missing Gaia data, record **unavailable/review-required**; never convert that status into a stellar nondetection or claim of a solitary unblended FT Tau.

## Safety and science limits

- The original images for the fixed ZTF source IDs are authentic astronomical **archival exposures**; this pipeline does not cause a telescope to make new observations. Some historical epochs may overlap prior StellarForge v1.8–v1.16 work. They are newly compared here, not *newly acquired telescope nights*.
- A low native-source offset, clean detector mask or missing bright neighbour **cannot independently prove a physical Gaia–ZTF source identity or absence of faint blended companions**; all native positions and science FITS WCS stem from the ZTF reduction pipeline.
- Cross-filter g/r observations **must never be treated as simultaneous**, even if both bands individually have close-date two-field pairs. No intrinsic source colour change, lightcurve merging or variability amplitude can be inferred.
- Source assignment, cross-field flux calibration, native ZTF PSF training-star independence, and original Luhman (2023) Taurus membership still require independent evidence.
- The original 24 technical targets were not selected as an unbiased Taurus sample. No Taurus-wide variability prevalence or new stellar companion result can follow from this two-field pilot.

## Reproduce

`python -m scripts.run_taurus_r2_ft_tau_two_field_fits`

Code: `src/stellarforge/r2_ft_tau_two_field_fits.py`, tests: `tests/test_research_taurus_r2_fttau_two_field_fits.py`, live GitHub Actions workflow: `.github/workflows/taurus-r2-fttau-two-field-original-fits.yml`.

Official [IRSA ZTF source ObjectID query and per-epoch original lightcurves](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html) and [ZTF dated science/FITS product paths and cutouts](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_api.html).

**Stage acceptance is source-level instrumental comparison, not scientifically completed R2 Gaia–ZTF physical-source identification.**
