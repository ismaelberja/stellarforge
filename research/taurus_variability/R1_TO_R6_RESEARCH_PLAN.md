# R1–R6 practical research milestones

**12 November 2026 ZTF original same-epoch independent analytic pixel-model NO-GO:** [Six real authentic native PSFcat SHA-matched ZTF science/mask images and their independent bounded circular-Gaussian fits](R2_REAL_FTTAU_SIX_ORIGINAL_GAUSSIAN_PIXEL_RESULTS.md). All six original masks and science images agree, 4/6 Gaussian fits return finite profiles, 2/6 fail as constrained; residual/noise proxy is high in all four finite models. This does not calibrate the spatially varying native ZTF PSF, validate target identity or justify relaxing the original chi gate. R2 remains OPEN.



**12 November 2026 real original FT Tau chi-blind sensitivity control:** [Six original ZTF native full PSFcat images, 1,095 original source control records](R2_REAL_FTTAU_SIX_ORIGINAL_CHI_REFERENCE_RESULTS.md), 240 below chi 0.5. This diagnoses potential selection sensitivity of the frozen chi lower cutoff, not a legitimate retrospective correction or independent source-match proof. R2 physical identity OPEN and R3 still blocked.



**New 12 November 2026 original FT Tau frozen-failure source diagnostics:**
[Three original late-night failed PSF catalogues, exact image masks and original source fits](R2_REAL_FTTAU_THREE_BAD_PSF_MASK_RESULTS.md).
Each of the three previous fixed late-night source candidates fails *only*
the unchanged native χ≥0.5 profile condition (χ=0.456, 0.424, 0.383).
Three original full native PSF catalogues are SHA-reverified and
three original science/mask FITS checks completed; all image source cores
are free of disqualifying mask bits. This is technical source-fit
diagnosis, not evidence that the PSF χ threshold should be relaxed:
the original 5/8 eligible sources and only 1/4 acceptable new night
pairs remain unchanged, and R2 physical identity is **OPEN**.

**Latest observational R2 progress (11 November 2026):**
[the original IRSA nine-position follow-up](R2_REAL_NINE_IRSA_SOURCE_RECOVERY.md)
recovered **seven** additional previously inaccessible ZTF positional
response tables. Across documented runs, the archive has returned
parseable positional data for **22 of 24** fixed technical Taurus sky
positions. The other two remain unresolved: one zero-row response
under NOBS_MIN=5, and one HTTP 400 when trying NOBS_MIN=1.
The Gaia DR3 original exact-ID query returned 24/24 Gaia source IDs;
17 passed preliminary Gaia-only astrometric flags.

**New same-date original image-level source screening:**
[FT Tau and CIDA 11 authentic science+mask FITS and native PSFcat
analysis](R2_REAL_FT_TAU_CIDA_11_FITS_SOURCE_GATES.md)
successfully checked **4/4** fixed historic ZTF exposures for
instrumental mask/WCS consistency and nearest native PSF source
neighbourhood. The four images are not new astronomy epochs.
Zero additional native catalogue sources within 3″ and zero flagged
central core mask pixels are **not proof of an isolated, physical
Gaia/ZTF source**.

**Latest R2 original Gaia-only reference validation:**
[Real Gaia DR3/reference source vs original ZTF PSFcat offset study](R2_REAL_GAIA_ONLY_CONTROL_OFFSET_NO_GO.md)
reused the **four previously fixed historical ZTF image dates**
and **five Gaia-only source-disjoint field controls**. On the two
CIDA 11 dates, respectively four and two strict controls passed;
on FT Tau, only one exploratory control passed per date.
**No** target+field pair passed all combined predeclared gates
for differential astrometry (CIDA target high RUWE/PSF quality,
FT Tau insufficient strict references). **R2 target correction NO-GO**
is an original-data conclusion, **not** a confirmed physical
Gaia–ZTF match, variable star, WCS calibration or non-detection.

**Latest FT Tau / CIDA 11 original ZTF ObjectID follow-up:**
[Two-field, six-OID genuine original catalogue results](R2_REAL_FT_TAU_CIDA_ZTF_ALTERNATIVE_OID_RESULTS.md)
found **four OIDs around FT Tau** (two g and two r, across
**two original field/CCD/quadrant combinations**) and **two around
CIDA 11** (one g, one r in the same field).
Two separate same-band FT Tau OID pairs require original-image
cross-field verification before curves can be combined.
Both historical g-band source OIDs were returned by original direct-ID
queries and by the 2-arcsec positional queries. This is **catalogue
access and provenance**, **not** proof of one physical Gaia/ZTF
source, scientific variability, companions or source deblending.

**Latest FT Tau original g/r two-field FITS/mask/PSFcat research pilot:**
[Four authentic selected original-source images, two same-filter
cross-field near-simultaneous pairs](R2_REAL_FT_TAU_TWO_FIELD_GR_FITS_MASK_PSF_RESULTS.md)
were selected strictly from the four previously identified OIDs,
based on minimum cross-field MJD gap, before image inspection.
**4/4** true original science FITS, detector masks and native PSF
catalogues passed the predeclared provisional source-level
instrumental QA. Each g and r pair is separated by **~39 s**
across the two detector fields, but the g and r bands were observed
in **different years**. Native source offset differences
(**13.568/79.473 mas for g/r**) are *not independently calibrated
field errors or physical source offsets*.
**Zero** authentic physical Gaia–ZTF FT Tau associations
or cross-field merged source lightcurves are claimed.

**Latest authentic FT Tau same-band reference-star ensemble:**
[Four real original g/r ZTF native PSF catalogues and underpowered
cross-field photometric comparison](R2_REAL_FTTAU_ORIGINAL_CROSSFIELD_INSTRUMENTAL_ENSEMBLE_NO_GO.md)
reverified exact original archival file hashes and compared
reciprocal-position matched, isolated native reference sources
within a fixed 360″ radius, excluding FT Tau itself.
Only **10 matched g-band reference pairs** and
**19 r-band pairs** survived original instrumental
PSF/flag/isolation QC, below the preregistered **20-source**
minimum for train+holdout validation. Therefore both bands
are explicit **NO-GO**; no instrumental magnitude offset
is fitted and no cross-field ZTF ObjectIDs are merged.
The ZTF PSFcat magnitudes are *instrumental detector
magnitudes*, not external AB/PS1 calibration.

**Newest R2 predeclared 720″ native reference / PS1-anchored original ZTF-header experiment:**
[Original-data 84 g / 186 r matched reference pair study](R2_REAL_FTTAU_720_ORIGINAL_INSTRUMENTAL_ENSEMBLE_PS1_HEADER_RESULTS.md)
reused the **four exact original historical image products**,
verifying their native PSFcat SHA-256s, and used a newly
predeclared **720″ radius** rather than changing the prior
360″ **NO-GO** after observing its 10/19 reference samples.
**84 g** and **186 r** source pairs passed the unchanged
20-pair threshold; independently split within-sample
training/holdout *instrumental-magnitude* and coarse
spatial-screen criteria passed in both bands. Original ZTF
FITS photometric header metadata fitted using PS1 calibrator
stars was also checked for 4/4 fixed science exposures.
The median ZTF instrumental shifts (field 609–1605) are
**+0.118 mag in g** and **−0.004 mag in r**, not color-corrected
AB magnitudes. ZTF PS1-anchored image header solutions
are *same-pipeline* outputs, not independently retrieved
PS1 source-row calibrations. **Zero** physical Gaia–ZTF
counterparts or confirmed intrinsic FT Tau variations;
**no crossfield OID lightcurves merged**.

**New R2 independently retrieved original MAST PS1 DR2
reference-star pilot (11 November 2026):**
[Actual external source-level colour-reference result](R2_REAL_FTTAU_EXTERNAL_MAST_PS1_DR2_SOURCE_COLOR_RESULTS.md)
retrieved **1,780 PS1 DR2 mean-source rows** from the
independent original MAST survey catalogue (405 met the
fixed quality/crowding/color controls). All four original
ZTF-native source FITS catalogues were SHA-reverified.
**82 unique matched PS1/ZTF/ZTF reference triplets in g**
and **180 in r** passed positional/quality criteria.
Source-ID-determined training/holdout empirical
`PS1 mean − native ZTF instrumental magnitude` fits
with PS1 `g-r` colours passed in all four original fields:
held-out scatters ~0.024–0.036 mag. This confirms a useful
**technical cross-survey matched-reference pilot**, not
fully calibrated astrophysical photometry or an
independently authenticated physical Gaia–ZTF FT Tau
target. PS1 supplied standards to the original ZTF
processing, so external source-row retrieval does not
imply statistical independence from its historical
pipeline calibration. No source OIDs were merged.

**New R2 original FT Tau source-target astrometry and ambiguity control
(12 November 2026):**
[Exact Gaia J2016 5p covariance/proper-motion to four original
ZTF observations, with independent external PS1 source references](R2_REAL_FTTAU_GAIA_PS1_ZTF_TARGET_ASTROMETRY_RESULTS.md)
obtained **4/4** real same-exposure ZTF native PSF source
candidates each **0.035–0.069″** from Gaia's
epoch-propagated geocentric-parallax and proper-motion
prediction. A complete 1,780-source PS1 DR2 mean
catalogue (raw response SHA changed vs previous pilot,
explicitly documented) contains **one** mean catalogue source
within 1″ of the original Gaia J2016 reference
position. With the previously fixed **82 g/180 r**
ZTF/ZTF/PS1 source-disjoint reference triples, both
same-filter fields pass predeclared held-out *positional*
consistency controls. These are **catalogue source-screening
indicators**, NOT independently calibrated epoch-corrected
ZTF WCS/source deblending, valid physical association,
proper-motion measurement, or new variable star. Source
OIDs remain unmerged.

**R2 is NOT complete:** Gaia–ZTF source physical identity,
independent externally calibrated astrometry/deblending (including
the remaining 22 technical targets) and original publisher Taurus
membership remain unverified.
Neither missing IRSA responses nor provisional positional matches
establish astronomical nonvariability or real detections.

There are **six planned increments in total** for a modest, bounded
**independent Taurus optical-variability feasibility study**. This is
a planning estimate, not a promise of a new detection, independent
PSF calibration or journal paper.

| Phase | Work | Acceptance criterion |
| --- | --- | --- |
| **R1** | Freeze question, 24-row technical seed and selection bias/limitations before new variability results | Reproducible 24-row pre-registration with 0 verified physical crossmatches; offline tests |
| **R2** | Literature and original Gaia/ZTF source identity screens | Source-by-source association/ambiguity ledger, no silently merged OIDs |
| **R3** | Original clean survey photometry and quality controls | Per-band time-series coverage and access ledger, explicit >0 scientifically usable source count *or blocker* |
| **R4** | Periodicity, variability and comparison-star/null statistics | Authenticated source-level diagnostic figures + independent control/alias discussion |
| **R5** | Original FITS image review, reproducibility, literature novelty check | Falsification/sensitivity report, candidate/negative status honestly classified |
| **R6** | Final technical research report and public presentation | Audited methods and limitations, final figures, defensible CV/LinkedIn text; publication only if scientific originality survives review |

**R1 is software/protocol groundwork, not a new astronomical result.**
If source identification fails or IRSA access is unavailable,
the research programme can end in a documented inconclusive/negative
feasibility report. Extra investigation beyond R6 may be essential
for a publishable discovery and cannot be numbered in advance.

The v2.0 engineering portfolio is **already publishable on LinkedIn**
as Python/data engineering work. Waiting for R6 is a choice only if
the goal is to present an additional independent *science investigation*
with genuine results rather than an unfinished scientific claim.
