# StellarForge v1.21 — Science-software falsification audit

**10 November 2026. All new numerical PSF experiments are synthetic.**

Verified GitHub source artifact metadata: acquisition run 41997079598,
artifact name taurus-two-target-raw-UNVERIFIED, artifact ID 13401380025,
181,170 bytes, expired=false on 10 November, expires
2026-11-12T08:47:05Z. The original ZIP bytes were NOT examined by this
metadata check. The v1.20 manual original-data workflow has NOT been run.

New v1.21 synthetic tests cover: artifact name/expiry/timezone
validation; rejection of false real 3+2 source counts, duplicated epochs
and inconsistent profile success; deterministic training-star
leave-one-out model stability; known injected artificial secondary
profile and no mutation of input pixels; no-physical-discovery guards.

Historic v1.16 original data remain unchanged and source-grounded:
three original high-residual same-image PSF profile checks still need
independent science/mask, neighbor, WCS, sky and multi-band review.

**This report does not claim newly acquired original ZTF FITS, measured
CCD variance, a verified Gaia–ZTF physical association or a new companion.**

Next essential step: manually dispatch the v1.20 CIDA 11 workflow on
main with acquisition run ID 41997079598 before source artifact expiry,
then record the genuine aggregate outcome before final v2.0 review.

Original survey files and Gaia source pixels remain outside public Git.
