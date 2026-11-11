# Taurus R2 — FT Tau cross-field original instrumental photometry: preregistered ensemble

**Protocol frozen 11 November 2026, before the new source ensemble is measured.**

## Scientific question

Does an ensemble of native ZTF PSF-fit catalogued sources overlapping two **original near-simultaneous** ZTF detector fields show an internally consistent *instrumental-magnitude* difference for **FT Tau's two already frozen pairs** (g/2019-11-19 and r/2018-11-03)? If there are too few clean, uniquely matchable sources, or the ensemble has high scatter, report **NO-GO**. Even a consistency PASS is **not absolute photometric calibration** or a physical Gaia–ZTF source match.

The primary `psfcat.fits` source column `mag` is **instrumental** `−2.5 log10(flux in DN)`, as stated by the ZTF Science Data System explanatory supplement (PSF-fit source table §10.6). It is not an externally calibrated Pan-STARRS/AB magnitude. An *instrumental* magnitude offset between two observations can be described without claiming calibrated source brightness. ZTF single-epoch photometric processing uses detector-dependent zero points and colour terms, and the ZTF lightcurve service also includes separate matchfile-relative refinements. These systems cannot silently be equated.

## Frozen genuine original data (no new exposure selection)

The [previous four-original-image R2 evidence](R2_REAL_FT_TAU_TWO_FIELD_GR_FITS_MASK_PSF_RESULTS.md) selected the dates **before** inspecting the original images, based on the minimum same-band MJD gap across detector fields, with **0.000451 d ≈ 39 s** per band:

| Band | Field 1605 / CCD15 / Q3 source OID and MJD | Field 609 / CCD8 / Q4 source OID and MJD |
| --- | --- | --- |
| g | `1605115300003377` — 58806.385197 | `609108400001155` — 58806.385648 |
| r | `1605215300005161` — 58425.306065 | `609208400001969` — 58425.306516 |

These are **the exact four historical ZTF single-exposure native PSF-fit catalogues** already validated against authentic original image/mask records. This phase re-downloads **only four original full native PSFcat catalogues** and enforces exact SHA-256 equality to the preceding R2's original product fingerprints. **No additional images or observation epochs are chosen**. If an archived original product differs by SHA, stop/report unavailable, do not substitute a different OID/night/field.

## Source geometry and photometric cuts fixed before looking at ensemble measurements

The field of view is a circle of radius **360″ around the original FT Tau Gaia technical seed position**. **FT Tau itself is excluded** from the comparison ensemble within **15″**. Select candidate native source catalogue rows satisfying:

- Finite original flux DN, positive quoted flux uncertainty, finite per-source instrumental magnitude and `sigmag` in (0, **0.08 mag**]; `SNR ≥ 20`; consistency of reported native magnitude with `−2.5 log10(flux DN)` within **0.10 mag**.
- Original PSF source quality `chi` between 0.5 and 1.5, `sharp` between −0.5 and 0.5; nonnegative native flags not containing the defined bad-mask bits. These are instrumental screens, **not proof of stellar isolation or static intrinsic flux**.
- At least **3″** from *every other detected source row in the same exposure*, including those with bad photometric flags.
- Across the two original exposures **in the same filter only**, accept source candidates with **mutual reciprocal nearest-neighbour assignment within 0.75″** using the original ZTF PSFcat ICRS sky positions. No two source IDs may enter the ensemble through one native source. Those ICRS positions share the same ZTF reduction/WCS pipeline; **they are not independent external source crossmatches**.
- Require at least **20** geometric matched reference pairs to evaluate an internal calibration. Divide them deterministically into a training and holdout set using **sky-coordinate hash parity, without using flux/magnitude** (with a fixed geometric fallback split if severely imbalanced). Require at least **10** fit and **8** independent-within-this-pair held-out *catalogue reference sources*. This is not independent telescope or instrument training.
- Compute `Δm_inst = m_inst(field609) − m_inst(field1605)` separately for g and r. Train a median on the training stars with a fixed 3×MAD robust outlier rule (minimum clipping threshold 0.08 mag). Validate on held-out star IDs without refitting: training and holdout robust dispersion must each be ≤ **0.15 mag** and median heldout signed residual ≤ **0.07 mag**. Report accepted/failed status, original reference counts, descriptive median instrumental shift, internal robust dispersion and nominal per-source measurement sigma; **do not claim true systematic calibration error or astrophysical target magnitude**.
- If missing/underpowered/inconsistent, record **NO-GO**; never pretend missing controls are nonvariable or a clean match.

These numerical thresholds are **predeclared pilot engineering screens**, **not validated astrophysical standards**. Stars separated by 39 seconds are *probably* comparatively stable for many ordinary sources, but flare stars, saturation, unresolved blends, field-selection effects and incorrect source matches remain possible. The clipping/holdout validation cannot prove astrophysical stability, sample independence or full calibration.

## What this stage can and cannot establish

It **can** test whether a limited local ensemble of cross-field native ZTF PSF sources gives internally consistent descriptive magnitudes in two original 39-second same-filter pairs. No external Pan-STARRS or Gaia colour calibration, rigorous airmass/transparency model, reference-star literature stability, absolute flux units or per-exposure instrument zeropoint uncertainties are established. Differently calibrated native `mag`, ZTF survey light-curve `mag`, and Gaia's photometry **must not be treated as the same measurement system**.

It **cannot** establish physical FT Tau source identity, instrument-wide photometric zero points, a robust flux calibration for every source, calibration across 2018 r and 2019 g, absence of blended stars or astrophysical companions, or a scientifically interpretable FT Tau variability amplitude. **No source OID lightcurves are merged** even if both internal ensemble checks pass. The 24-object Taurus research technical cohort remains nonrepresentative; original publisher membership remains to be checked.

Only original source catalogues are loaded transiently into the GitHub Actions runner, and **only bounded derived ensemble statistics and original input SHA-256s** are published. No original raw magnitudes, fluxes, per-source positions, sky IDs or FITS pixels are committed.

## Reproduce

- Code: `src/stellarforge/r2_fttau_crossfield_instrumental_ensemble.py`
- Entrypoint: `python -m scripts.run_taurus_r2_fttau_crossfield_ensemble`
- Workflow: `.github/workflows/taurus-r2-fttau-crossfield-ensemble.yml`
- Sources: [ZTF Data Processing, Products, and Archive (Masci et al. 2019)](https://doi.org/10.1088/1538-3873/aae8ac), [official ZTF Science Data System Explanatory Supplement](https://irsa.ipac.caltech.edu/data/ZTF/docs/releases/ztf_explanatory_supplement.pdf) (source-level instrumental magnitude definitions), and [original NASA/IPAC ZTF survey products](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_api.html).

**This is an instrumental reproducibility screen within R2, not R2 physical crossmatch completion.**
