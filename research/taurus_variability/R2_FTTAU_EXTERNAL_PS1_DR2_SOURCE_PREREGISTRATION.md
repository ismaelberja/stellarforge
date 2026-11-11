# Taurus R2 — prospective independent Pan-STARRS1 DR2 source-level reference test

**Protocol frozen before new MAST Pan-STARRS1 API access, 11 November 2026.**

This is a separate, prospective test after the successful [FT Tau 720″ original ZTF instrumental two-field QC](R2_REAL_FTTAU_720_ORIGINAL_INSTRUMENTAL_ENSEMBLE_PS1_HEADER_RESULTS.md). It does **not** retroactively change the unsuccessful 360″ experiment, the successful 720″ internal experiment, or the original four ZTF exposure selection. In particular, ZTF's PS1-anchored FITS-header photometric solution is **not** independent Pan-STARRS1 source-level calibration: this new test will fetch the independent **MAST Pan-STARRS1 DR2 MeanObjectView** source rows.

## Frozen sample

Exactly the same four FT Tau original archival `psfcat.fits` (g/r in ZTF fields 1605/CCD15/Q3 and 609/CCD8/Q4), with previous original byte SHA-256 verified *before* any new PS1 matching. The FT Tau technical target `Gaia DR3 149623711269425408` and original 24-object nonrepresentative Taurus R1 technical seed are unchanged. The fixed g and r same-filter field pairs are each ~39 s apart; **g in November 2019, r in November 2018, never crossfilter simultaneous**.

## New independent data request and fixed source selection

One official **MAST Pan-STARRS1 DR2 mean-source cone** at the original R1 FT Tau seed coordinates, radius exactly **0.2 degrees / 720″**, with `nDetections.gte=5` and columns: `objID,raMean,decMean,nDetections,ng,nr,gMeanPSFMag,gMeanPSFMagErr,rMeanPSFMag,rMeanPSFMagErr`. Use `pagesize=5000`, 45-second timeout, 8-MB byte cap, no retries on the basis of results; if **5000 rows or more** are returned, reject as potentially truncated rather than silently interpreting as a complete sample. PS1 positions are a separate survey and do not share ZTF's image reduction. They may nonetheless differ by epoch/proper motion and catalog errors; source matching remains an error-prone approximation.

For source selection fixed before inspection:
- Keep finite PS1 positions in the 720″ cone and **exclude 15″ around FT Tau**.
- Require `nDetections≥5`, `ng≥3`, `nr≥3`; valid mean PSF g and r magnitudes in **[12,21]** with each catalogue mean uncertainty in (0, **0.05 mag**]; color `−0.5≤g−r≤3.5`. Treat these as pilot QC, not official unblended-star / proper-motion / variability certification.
- Retain the preceding ZTF per-exposure native instrumental source flags/SNR/PSF `chi,sharp`, 15″ target exclusion, 3″ isolation and full 720″ radius exactly. For **each same-filter pair**, ZTF sources must be reciprocal nearest neighbours within **0.75″**. For each such pair, match the *field-1605 ZTF position* to a **unique mutual nearest** PS1 source within **0.6″**, and also require the field-609 source to be within **0.6″** of **the exact same independent PS1 objID**. Any conflicting, double-assigned, PS1-blended or absent source is excluded; **never** choose replacements on the basis of photometric agreement.
- The PS1 reference itself must be isolated from any other **returned** PS1 MeanObjectView entry within **2″**, assessed using **all returned positions**, not only PS1 photometrically accepted stars. This does not rule out noncatalogued/faint blends.
- Require **≥20 distinct matched ZTF-ZTF-PS1 source triplets per band**; at least 10 training / 8 holdout sources after deterministic original PS1 `objID` hash parity split (geometry-only fallback), with fixed 3×MAD clipping minimum 0.10 mag. Do not lower thresholds after results.

## New independent PS1 source photometric model and gates

For each band and *each original ZTF field independently*, fit the source-level comparison
`y = m_PS1(band, mean PSF) − m_ZTF_native_instrumental = intercept + slope × [(g−r)_PS1 − 0.8]`,
using robust 3×MAD clipped **least-squares** on the training subset, max **3 iterations**, fixed lower clip 0.10 mag. This intercept is an **empirical PS1-relative ZTF instrumental offset for these selected reference stars** and time/field; the fitted slope is a **descriptive color dependence**, *not* an official ZTF `CLRCOEFF` or an independently certified absolute magnitude zero point.

Validate on the held-out unique PS1 source IDs **without refitting**. Predefined pilot screens: |heldout median residual|≤**0.08 mag**, heldout robust scatter≤**0.12 mag**, fitted slope within [−1,+1] mag/mag, intercept within [15,35] mag, and ≥10 fit training stars. Report nominal photometric uncertainty and descriptive median residuals without treating the PS1 sources as intrinsically stable over every ZTF season. Report both per-field fits and the descriptive crossfield difference; if a band fails one field or has too few PS1 unique triplets, it is **NO-GO**, not stellar nondetection. No true error covariance, color-dependent atmosphere/PSF, PS1-ZTF filter transmission transformation or external standard-star variability is certified.

Separately compare the PS1-derived intercept to each **original ZTF FITS PS1-anchored `MAGZP`** for *diagnostic context only*. PS1 and ZTF filters differ, the ZTF reduction already uses PS1 references and ZTF pipeline image ZP itself is not an independent calibration; no statistical-significance test on intercept differences is declared without a full error model.

**Never use FT Tau itself as a calibrator; never automatically merge any of four ZTF ObjectIDs or declare physically confirmed Gaia–ZTF FT Tau identity/variability/companions.**

## Error handling, reproducibility, honest stops

If MAST original PS1 DR2 data are missing, incomplete, rejected, limited or HTTP-unavailable, report **INDEPENDENT_PS1_CATALOGUE_UNAVAILABLE/INCOMPLETE**. Preserve an authenticated original catalog SHA and source counts only when genuine original data are obtained. Original PS1/ZTF rows, source IDs, exact coordinates, fluxes and photometric time series must remain ephemeral on the GitHub Actions runner; publish **derived counts, statistical summaries, original-input SHA hashes, and detailed anti-claim flags**.

Code: `src/stellarforge/r2_fttau_external_ps1.py`; runner: `scripts/run_taurus_r2_fttau_external_ps1.py`; GitHub Actions: `.github/workflows/taurus-r2-fttau-external-ps1.yml`.

MAST [official Pan-STARRS1 catalog API documentation](https://catalogs.mast.stsci.edu/docs/panstarrs.html) (DR2 MeanObjectView columns, radius **degrees**, `pagesize`/possible truncation).

**Scientific R2 source-identification and any FT Tau astrophysical variability discovery remain OPEN whether this preliminary independent survey photometry check succeeds or fails.**
