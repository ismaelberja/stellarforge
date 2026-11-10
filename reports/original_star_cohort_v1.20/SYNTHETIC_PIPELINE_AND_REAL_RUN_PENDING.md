# v1.20 audit — Synthetic pipeline pass; original CIDA 11 run pending

**10 November 2026. Scientific status: IMPLEMENTED, NOT REAL-DATA-VALIDATED.**

The v1.20 automatic CI tests use synthetic Gaia sources and synthetic
original-format FITS images. They check strict Gaia-only deterministic
allocation of 4 training and 3 held-out candidates, original science/mask
WCS registration, native PSFcat fractional phase, 6141 mask-bit propagation,
rejecting saturated stellar cores, and independent whole-star empirical
model integration (without original DAOPhot coefficients). Offline mocked
runner tests ensure no real ZTF access when the Gaia cohort fails.

**No new original ZTF/Gaia field-star image acquisition has been completed
by the v1.20 manual workflow as of publishing this report.**

Earlier real-data facts carried forward, not recomputed by v1.20:
- CIDA 11 had 20 Gaia DR3 strict-quality survivors in the v1.17 cone
  audit before selecting four.
- FT Tau had zero additional strict-quality Gaia field controls in
  v1.17/v1.18; the exploratory FT Tau source in v1.18 is ONE star
  observed on two dates.
- Original 4 ZTF DAOPhot spatial models and their original field-center
  PSFs were successfully checked in v1.15; actual source pixels were
  fitted with the original PSF and mask in v1.16–v1.18.
- ZTF native PSF-building training-star list remains unauthenticated.
- Three high-residual profiles from v1.16 require further investigation;
  no astrophysical companion/detection inference is permitted.

**Next real-observation gate:** manually dispatch the GitHub workflow,
retain ONLY no-raw aggregate evidence, and independently review every
source/epoch failure status. If fewer than three training plus two
held-out original source stamps qualify per frame, stop and report
scientific incompleteness rather than choose an easier sample.

No original ZTF pixels, Gaia responses, PSFcat raw rows or empirical
PSF arrays have been committed to Git.
