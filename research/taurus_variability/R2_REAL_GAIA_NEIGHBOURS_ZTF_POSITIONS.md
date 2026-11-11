# R2 — Actual original Gaia-neighbour and IRSA ZTF source-position results

**11 November 2026. Actual live survey catalogue requests, not independent astronomical crossmatches.**

**Historical snapshot:** the 2/24 IRSA result below is
the **earlier** original-data run, not the latest source-access
coverage. A [later controlled requery](R2_REAL_IRSA_22_FAILURE_DIAGNOSIS_RESULTS.md)
recovered 13 additional previously unresolved original-format
tables (15/24 cumulatively accessible; 9 still unresolved) without
confirming any Gaia–ZTF physical source identity.



- [Original completed Gaia+ZTF archive run](https://github.com/ismaelberja/stellarforge/actions/runs/43031689454)
- [Original 30-day derived-only 24-source artifact](https://github.com/ismaelberja/stellarforge/actions/runs/43031689454/artifacts/13861901170)
- [Pinned summary receipt, no raw survey data](../../reports/taurus_variability_r2/GAIA_NEIGHBOUR_ZTF_POSITIONAL_ORIGINAL_RESULTS_NO_RAW.json)
- [Method preregistered before live responses](R2_GAIA_NEIGHBOURS_ZTF_OID_METHOD.md)

The 24 preselected, **nonrepresentative** Taurus technical candidates
remain unchanged. Original R1 technical seed SHA-256:
\`9cecb94704f028a981045629ad16ecb770f51bba4b6bb3bf13dda769327ff37e\`.

## Authentic catalog query outcomes

| Test on original public source data | Actual result |
| --- | ---: |
| Frozen technical Gaia candidates processed | **24/24** |
| Gaia DR3 neighbourhood cones queried and parsed (15″) | **24/24** |
| Gaia neighbourhood cones failed or hit row cap | **0** |
| Candidate targets with another *catalogued Gaia* source within 2″ | **0/24** |
| Candidate targets with another *catalogued Gaia* source within 5″ | **4/24** |
| IRSA/ZTF 2″ positional queries with original CSV successfully parsed | **2/24** |
| IRSA/ZTF queries failed or returned unparseable/unavailable content | **22/24** |
| Parsed source positions with more than one ZTF OID in a given band | **2/2** |
| Confirmed physical Gaia–ZTF associations | **0** |
| Newly confirmed stellar variables or companions | **0** |

**Do not interpret the 22 unresolved ZTF queries as empty light curves
or non-variable stars.** The initial script groups request errors,
timeouts, response-size failures and unparseable formats into one
\`IRSA_QUERY_OR_PARSE_UNAVAILABLE\` status. Their precise individual
failure causes were **not diagnosed in this run**. They require a
separate bounded request/format audit and possibly re-fetching
rather than being silently excluded from any science sample.

Likewise, absence of a *Gaia catalogue neighbour* within 2″ does
**not** exclude unresolved sources, wavelength-dependent companions
or contamination from unlisted objects. The 15″ Gaia query and
approximate proper-motion propagation to J2021.0 do not independently
validate ZTF image blending.

## Original IRSA responses usable for positional review

| Technical seed target | Gaia DR3 ID | Original ZTF photometry rows | OID/filter/time groups | Potentially ambiguous bands | Gaia RUWE |
| --- | --- | ---: | ---: | --- | ---: |
| V892 Tau | 164513602672978304 | 3,044 | 6 (3 g, 3 r) | g and r | ~3.55 |
| LkHa 332/G2 A+B | 148116246465275520 | 842 | 2 (both r) | r | ~16.30 |

The original ZTF API returned multiple **ObjectIDs** with
survey-reported positional proxies within 2″ of the Gaia
proper-motion-predicted direction. This does **not** imply those
ObjectIDs represent different physical stars; ZTF field,
detector or survey processing may assign different OIDs to
observations of the same physical source. Conversely, it
does **not** establish a unique Gaia–ZTF association, so **we
must not concatenate the OID curves or claim physical variability**.

Both objects also have markedly elevated Gaia RUWE, indicating
that a simple single-source astrometric interpretation requires
special caution; RUWE alone is not a binary-star or companion
detection. The ZTF data are real original API rows, **not**
authenticated light curves of V892 Tau or LkHa 332/G2 A+B
until independent image, crowding and crossmatch review.

## What the original-data run does *not* include

- No new Gaia-to-ZTF **physical source** identification.
- No checking of exact ZTF original science-image pixels, original
  PSFcat training-star list, native bad-pixel masks or independent
  astrometric reference solution during this particular R2 job.
- No independently verified memberships from the original
  publisher machine-readable Taurus membership catalogue.
- No statistical inference of young-star variability prevalence
  from 24 preselected bright Taurus technical candidates.
- No new companions, periodicities, physical mechanisms or
  instrumental PSF/WCS calibrations claimed.
- No raw TAP/IRSA CSV bytes committed or uploaded;
  only anonymization-independent *public catalogue*
  per-source derived statuses and SHA-256 digests.

## Follow-on decision: finish R2, don't jump to unverified R3

1. **Diagnose the 22 unresolved ZTF requests** by bounded
   HTTP status and content-type/size categories. Distinguish
   genuine empty archival catalogues, source-access failures,
   temporary service errors, malformed output and genuine
   technical response-size limits. Re-run only with explicit
   provenance and rate limits; preserve the fixed 24 denominator.
2. Independently verify original Luhman (2023) member-row
   provenance and per-source Gaia quality/close neighbours.
3. For actual candidate OIDs, inspect original same-exposure
   ZTF images, native PSFcat, bitmasks and neighbour/catalogue
   astrometry at the **proper observation epoch**. Use independent
   reference controls; ZTF internal catalogue position alone
   must not authenticate a counterpart.
4. Freeze the identity/ambiguity ledger before R3 photometric
   variability features or periodograms. If no unique source
   association survives, report a method/selection failure
   instead of a scientific nondetection.

**Science progress: R2 observational positional substage completed,
full R2 physical source authentication still OPEN.**
Software portfolio v2.0.0 remains an already completed project.

## Provider methods

- [IRSA official ZTF positional-lightcurve API](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html):
  one sky query may return multiple distinct OIDs.
- [Gaia DR3 official source-id and astrometric datamodel](https://gea.esac.esa.int/archive/documentation/GDR3/Gaia_archive/chap_datamodel/sec_dm_main_source_catalogue/ssec_dm_gaia_source.html):
  a source identifier is unique within a data release, not a
  cross-survey astrophysical identity proof.
