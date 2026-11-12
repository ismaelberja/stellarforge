# Taurus R2 — genuine independent-database FT Tau ↔ Gaia DR3 exact-name cross-index

**12 November 2026 · Original live CDS SIMBAD query (Harvard official mirror) completed successfully.** This is an externally curated **name/identifier association**, not an independently verified ZTF source-specific counterpart.

[Preregistered two exact identifier lookups](R2_FTTAU_SIMBAD_EXACT_GAIA_NAME_ALIAS_PREREGISTRATION.md) · [Authentic original live CDS SIMBAD run](https://github.com/ismaelberja/stellarforge/actions/runs/43314507016) · [Actual no-raw original two-query artifact](https://github.com/ismaelberja/stellarforge/actions/runs/43314507016/artifacts/13987771466) · [Permanent compact source and response-hash evidence](../../reports/taurus_variability_r2/FTTAU_SIMBAD_EXACT_GAIA_NAME_ALIAS_NO_RAW.json)

## The question tested before retrieving new external source records

Does the **historical young-star name FT Tau**, which the original 24-source Taurus research seed assumed, point in the CDS SIMBAD database to the **same externally indexed object** as exact Gaia DR3 source ID **149623711269425408**? This question is deliberately weaker than whether four unrelated ZTF ObjectIDs and six original dated per-image PSF catalogue source detections can all be verified as this physically same star.

SIMBAD TAP allows exact joins between the `ident` table of alternate identifiers and the `basic` table of catalogue objects. Two distinct preregistered exact lookup methods were run on the **same first-working, precommitted CDS official Harvard mirror**:
1. `Gaia DR3 149623711269425408` (exact Gaia identifier string).
2. Historical exact `FT Tau` or `V* FT Tau` (no fuzzy, wildcard or sky-nearest match).

No new name strings, bounding radii, source brightness, detector images or TAP mirrors were chosen in reaction to the returned data. The original primary Strasbourg CDS server had a service incident, so the source-preregistered Harvard mirror was used; there was **no need to fail over** to the second IDIA mirror.

## Actual original CDS SIMBAD outcome

| Exact original SIMBAD search | Unique SIMBAD object records | Returned main identifier | Result |
| --- | ---: | --- | --- |
| Gaia DR3 149623711269425408 | 1 | V* FT Tau | Unique |
| FT Tau / V* FT Tau historical names | 1 | V* FT Tau | Unique |

**Both independent identifier lookup paths resolve to the same underlying SIMBAD `basic.oid`**, with *exactly one* returned row each and no contradictory or competing object. SIMBAD reports object type **`Or*`**. This demonstrates **successful curated external catalogue name equivalence** between the original research label FT Tau and the exact Gaia source. It also explains the SIMBAD main identifier **V* FT Tau**, which is *not* a new variable-star discovery by StellarForge.

The simple sky separation between original SIMBAD `basic` ICRS position and exact Gaia DR3 J2016.0 ICRS position is **0.36934 arcsec**, computed purely for context. This difference has **not** been corrected to a shared observation epoch or instrument covariance, so it is not an independent astrometric match test. Published references locate FT Tau near RA 04:23:39.19, Dec +24:56:14.1 (MNRAS Taurus high-resolution companion survey, 2020), and near RA 04:23:39.20, Dec +24:56:13.9 (JWST MINDS disk survey, 2024); those name-level historical contexts are not an independent proof of ZTF source assignment.

Both successful SIMBAD TAP CSV responses have the **same raw SHA-256** `9f59f1d336ed489a41d8427b54808a7d905aa7b498be54735b4f6bc91eb1aa49`. Both were exact-name queries, but their **database rows are not independent observational measurements**: SIMBAD's Gaia alias originates from the Gaia data/reference literature, and both paths query the same curated catalogue. For the actual source data, see the documented [original archived derived-only artifact](https://github.com/ismaelberja/stellarforge/actions/runs/43314507016/artifacts/13987771466). No complete raw SIMBAD alias lists, original photometric rows or original ZTF science pixels were committed.

## What this solves — and what it does not

- **Confirmed at external naming level:** The original research assumption that Gaia DR3 149623711269425408 carries the historical name FT Tau is externally supported through SIMBAD's unique exact aliases. This was previously an assumption; it now has a reproducible exact-query source audit.
- **NOT confirmed at ZTF physical-source level:** Nothing about the SIMBAD alias lookup authenticates that all four original ZTF ObjectIDs or each of their original per-exposure PSFcat nearest-neighbour sources represent the same physical Gaia star, nor does it prove deblending, a common light curve, independent PSF noise/WCS covariance, proper motion or intrinsic variability.
- **Existing science gates remain untouched:** The three source candidates originally rejected solely for native PSF chi below 0.5 stay rejected; previous **5/8 source quality passes, 3/8 failures and only 1/4 two-night passing candidate pairs** stand. **0** original ZTF ObjectID light curves merged, **0** newly discovered variables/companions and **0** independent physical Gaia–ZTF source matches. R2 astronomical source association **OPEN**, R3 astrophysical inference **BLOCKED**.

## Data provenance

Actual live workflow: [43314507016](https://github.com/ismaelberja/stellarforge/actions/runs/43314507016); [original derived-only archived artifact 13987771466](https://github.com/ismaelberja/stellarforge/actions/runs/43314507016/artifacts/13987771466). Artifact ZIP SHA-256 `2f41af746886c50ef47f6c83787bcb424ac41d94e7cf4c9addd2d46c5d0171d7`; original derived JSON SHA-256 `899820425bdd261c25fd9470cdd755d69753e7e6b6569e1f54b72b189a6398a5`. Original Gaia 5-parameter response SHA `399b5498d8d8a8a646073dfc029895ed64902940896d1789c63833a18074b642`. Both exact original SIMBAD query signatures and response SHAs, frozen R1 seed hash and prior ZTF data summary hash are recorded in the permanent [no-raw external identity ledger](../../reports/taurus_variability_r2/FTTAU_SIMBAD_EXACT_GAIA_NAME_ALIAS_NO_RAW.json).

Primary external catalogue documentation: [CDS SIMBAD documented TAP identifier query](https://simbad.cds.unistra.fr/Pages/guide/sim-url.htx), [official Harvard hosted SIMBAD mirror](https://simbad.cfa.harvard.edu/simbad/), and [CDS mirror/service status guidance](https://cds.unistra.fr/). Literature context: [2020 Taurus high-resolution imaging survey](https://academic.oup.com/mnras/article/498/1/1382/5893335) and [2024 JWST MINDS overview](https://orbi.uliege.be/bitstream/2268/325880/1/Henning24_MINDS_overview.pdf).

**Recommended next milestone:** a v2.1 software portfolio closeout and clear scientific claims/figure audit can proceed independently. Any genuinely new physical astrophysical inference still requires separately validated cross-instrument source identity, blended-source analysis, proper source covariance and time-domain measurements; it cannot be obtained from a SIMBAD name lookup alone.
