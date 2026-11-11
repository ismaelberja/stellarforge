# Taurus R2 — preregistered alternative ZTF ObjectID / detector-field review

**Protocol defined 11 November 2026, before inspecting the new original IRSA responses.**

## Research question

For **FT Tau** and **CIDA 11**, how many distinct *original survey ZTF ObjectIDs* are found within a fixed 2-arcsecond circle of the previously frozen Gaia technical positions? Do they occur in different filters, `field/CCD/quadrant` combinations, or the same original exposure metadata? Does each previously documented **historic ZTF OID** also appear in the positional request?

This review investigates the **source-association ambiguity** preventing meaningful target-identified photometric analysis. It is not a demonstration of unique physical Gaia–ZTF identity and does not merge light curves.

## Frozen sample and authentic previous evidence

The full earlier **24-source nonrepresentative Taurus technical R1 seed** is preserved. Exactly two established historical source names/IDs (not chosen by new lightcurve results):

| Source | Gaia DR3 exact source ID | Existing historical ZTF OID | Previously used g-band science MJDs |
| --- | --- | --- | --- |
| FT Tau | `149623711269425408` | `1605115300003377` | 58388.389016, 58491.184780 |
| CIDA 11 | `3419110734340795648` | `610106300008010` | 58475.113750, 58849.135984 |

These historic original image OIDs/MJDs were already frozen and independently checked using authentic original ZTF science FITS, matching detector masks and native PSFcat in [R2 prior original-image source-gate evidence](R2_REAL_FT_TAU_CIDA_11_FITS_SOURCE_GATES.md). Recent Gaia-only field-reference tests still lacked a valid independently calibrated target correction; see [R2 four-exposure control no-go](R2_REAL_GAIA_ONLY_CONTROL_OFFSET_NO_GO.md).

## Exactly predeclared requests

For each target, independently request:

1. **One** bounded original public NASA/IPAC IRSA ZTF positional query, centered on the **unchanged original R1 technical Gaia-seed coordinate**, with `POS=CIRCLE RA DEC 2/3600`, `FORMAT=csv`, `NOBS_MIN=5`. The latter is an *access filter*, NOT a scientific threshold or minimum variability sampling.
2. **One** bounded exact `ID=<historic OID>&FORMAT=csv` original ZTF survey object request, even when the positional request was unavailable or did not contain the historic OID. This prevents a false conclusion from one failed or limited-radius positional request. No replacement OID is chosen after seeing the results.
3. One original Gaia DR3 exact two-source astrometry request, solely for approximate proper-motion sky-position comparison where returned. A complete independent Gaia/ZTF astrometric error model and calibrated WCS are **not** available here.

Fixed 2-arcsecond positional radius; each ZTF request has a **35-second** timeout and **4 MB** response-byte limit. Total at most **four ZTF requests + one two-source Gaia request**. No retries or wider circles after observing outcomes. A failed/unparseable result is preserved as **unavailable**, never treated as absence of the star or its variability.

## Fixed evidence and ambiguity categories

- Retain *each* original ZTF ObjectID, filter and time-system label separately. The existing ZTF parser applies a stated original `catflags` QC mask before counting *quality-accepted* rows; report **raw original survey row counts separately**.
- From original per-epoch rows, record only **derived per-OID/filter counts**, original `field/CCD/quadrant` combinations, count of available `filefracday/field/CCD/quadrant` exposure identifiers, and whether different OIDs in the **same band** share an exact original exposure metadata key. Original per-epoch magnitudes, individual timestamps and full source catalogue rows must **not** be saved.
- Mark all *same-band multi-OID* pairs as **ambiguous and not automatically mergeable**. If two OIDs share an exposure metadata key, this is a stronger technical flag to inspect the image/crowding later, not proof of two real stars. If field/CCD/quadrant differ, that alone is also not proof both represent one star.
- Original survey sky positions, if present, are compared approximately with Gaia using source proper motion, but the propagated model omits full parallax and colour/WCS uncertainties. This is **not** an externally calibrated likelihood or proof of a physically matched Gaia source.
- The historic direct-ID response can establish that original ZTF catalogue rows **were available** for the frozen OID. Even if the same OID also appears in the 2-arcsecond positional request, this still cannot by itself authenticate the target's physical Gaia–ZTF crossmatch.
- The four original historical science FITS images were already checked in prior R2. This step **downloads zero additional astronomy images**, performs no deblending or independent recalibration, and adds no new observing epochs.

## Stop and acceptance rules

**Accept as technical source-label progress:** both original query types are reported for each fixed target; an OID/filter/detector-field ambiguity ledger is generated with explicit provider errors or quality limitations, original source bytes SHA-256 and no-raw provenance.

**Do not claim:** that two distinct OIDs prove different stars, that similar OIDs/fields identify one physical Gaia star, any new optical variable or companion, any physical association certainty, validated population-wide Taurus variability, independent ZTF WCS calibration, or independently verified original publisher Taurus membership. Only after later *independent* original-image/source-deblending, multi-survey astrometric and literature validation may source-level astronomical variability become interpretable.

## Code and reproducibility

- `src/stellarforge/r2_ztf_oid_multiplicity.py`
- `scripts/run_taurus_r2_ztf_alternative_oids.py`
- `.github/workflows/taurus-r2-ztf-alternative-oids.yml`
- [IRSA's official ZTF lightcurve API documents positional search, direct-ID lookup and multiple ObjectIDs per position](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html).

**R2 scientific physical-source identification remains open.** The separately completed StellarForge v2.0 software portfolio is unchanged.
