# StellarForge v1.17 — New source-disjoint Gaia field controls and shifted-sky positional nulls

**9 November 2026 · Scientific Python and original ZTF observational reproducibility.**

## New functionality

- Gaia-only, **pre-PSF/CCD-data selection** of field control candidates from independent 210″-radius Gaia DR3 queries. Enforces deterministic source-ID exclusion of all 10 former target/reference Gaia identifiers, valid formal Gaia astrometry, conservative RUWE/brightness/flux quality, isolation from **all** Gaia sources in the wide-cone sample, and sky-quadrant spatial coverage.
- New Gaia-selected source IDs are queried for their **own full correlated five-parameter Gaia DR3 astrometry**, propagated with first-order Earth-geocentric geometric annual parallax to each exact historic original ZTF exposure. They remain positional counterpart **candidates**, not authenticated physical matches.
- For each original science date, evaluate actual original native `psfcat.fits` ZTF source-quality/profile correspondence, `sciimgdao.psf` spatial DAOPhot PSF and the original field-center stamp; eligible new objects then receive genuine same-epoch `sciimg.fits`+`mskimg.fits` WCS-aligned spatial PSF source-pixel residual screening using the v1.16 code.
- Add **preregistered fixed 25″ east/west/north/south sky-position shifts** as a small native PSF catalogue accidental-proximity-density sanity check. The null probes do NOT estimate source contamination probability.
- Enforce a minimum of three distinct Gaia source IDs per historical exposure to issue a descriptive median same-image source residual ratio; the result cannot be called a calibrated PSF/WCS error or independent PSF-training-star holdout.

## Authentic original-data result

[Successful original IRSA ZTF + Gaia workflow](https://github.com/ismaelberja/stellarforge/actions/runs/42661663983) passed **636 automated tests** and accessed the SHA-verified 2,212-row original ZTF source acquisition and fresh, distinct Gaia DR3 field catalogues.

- FT Tau: **50** Gaia entries in the 210″ cone, **zero** new quality/isolation-selected sources after explicit prior-source exclusion and fixed Gaia-only filters. **No new masked PSF source pixels fitted in FT Tau**. Do not imply that CIDA 11 field-star results generalize to FT Tau.
- CIDA 11: **250** Gaia entries, **20** new source candidates pass Gaia-only quality/isolation screening before budget, and **four** newly selected and mutually spatially distributed candidate Gaia source IDs cover all four sky quadrants. None is among the former 10 reference/target IDs.
- **Eight** new-source×original-date native PSF-catalogue candidate screens, **six** original full WCS-aligned `sciimg.fits`+`mskimg.fits` PSF pixel-source fits across two original CIDA 11 dated science exposures, **six** provisional same-image checkerboard residual QC passes. The other two source×date combinations failed the original native catalogue source quality/candidate eligibility check and were **not** fitted (not sky nondetections).
- In first CIDA 11 original science date **four** distinct new candidate sources support a descriptive source-pixel residual-noise median **0.98091**. The second date has only **two** original eligible fitted stars and correctly reports an **insufficient distinct controls** status.
- **32 fixed ±25″ shifted sky probes** across the two original CIDA 11 dates returned **zero** native PSF-catalogue sources within 1″, but the shifted probes are not independent sky objects or a formal false-match trial.
- **No** new physical Gaia–ZTF match, independently calibrated local stellar PSF, authenticated DAOPhot training-star exclusion, WCS error budget, companion or physical time-domain event is established.

[Full verifiable CIDA 11-only real field control evidence](reports/new_gaia_holdouts_v1.17/REAL_DISJOINT_GAIA_CONTROL_AND_SHIFTED_SKY_RESULTS.md) · [Gaia-only candidate selection, 25″ offsets and methodological limitations](docs/PHASE117_DISJOINT_GAIA_SOURCE_HOLDOUTS_AND_SHIFTED_SKY_NULLS.md).

**Critical independence caveat:** the four new Gaia sources are entirely absent from *StellarForge's prior v1.8–v1.16 source candidate sample* but may still be in the **ZTF original DAOPhot pipeline's PSF model training stars**, whose membership is unknown. Do not advertise this as an independent astrophysical/calibrated PSF holdout evaluation.

**Next scientific gate:** true original PSF-training star membership verification, an independent source model calibration over substantially more stars and epochs (especially FT Tau), realistic image noise/WCS errors, Gaia/ZTF authentic crossmatches and quantified false associations — without interpreting positive image residuals as astrophysical companions.

All original Gaia CSV and ZTF science, native PSF, mask, and photometry source bytes remain ephemeral; only derived aggregate results, original SHA hashes and synthetic tests are in public Git.
