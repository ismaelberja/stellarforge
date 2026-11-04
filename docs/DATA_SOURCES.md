# Data sources and provenance contract

| Source | Role | Access | Confirmed constraints |
|---|---|---|---|
| Luhman (2023), AJ 165, 37 | Independent Taurus membership | Paper tables / vetted machine-readable catalogue to be identified | 532 adopted members; not all may be represented in Gaia |
| Gaia DR3 `gaia_source` | Coordinates at reference epoch, astrometry, photometry, `has_epoch_photometry` | Gaia TAP/ADQL; `astroquery.gaia` | Main Gaia `gaia_source` is not the Gaia epoch-photometry dataset |
| Gaia DR3 Epoch Photometry | Epoch-level G/BP/RP light curves where available | Gaia DataLink; `Gaia.load_data(ids=..., retrieval_type='EPOCH_PHOTOMETRY')` | Not available for all Gaia sources; batch/service constraints apply |
| ZTF light curves | Irregular optical g/r/i variability | IRSA `nph_light_curves` light-curve API | Quality flag filtering, multiple object IDs, sky coverage, magnitude limits |
| Other catalogues (future) | Cross-check membership/rotation/disk properties | CDS/VizieR/peer-reviewed literature | Confirm independent labels and data reuse rights |

## Source registry (minimum required fields)

Store source name, citation/DOI, archive URL, release/version, row-level identifier, coordinate frame, reference epoch, query string, UTC retrieval time, SHA256, license/acknowledgment, file format, schema version, and any documented selection criteria.

## Cross-matching expectations

Gaia positions are reported in ICRS with reference epoch J2016.0. ZTF observations occur at distinct epochs; proper motion can matter for precise matching. Use `astropy.coordinates.SkyCoord.apply_space_motion()` when adequate astrometry is available; propagate uncertainties or flag them, keep source alternatives and possible blends. The v0.1 `approximate_proper_motion_position()` function is a unit-tested **engineering approximation**, explicitly unsuitable for final science results.

For ZTF, one Gaia target can yield more than one ZTF object ID; multiple IDs can correspond to different field/CCD/filter configurations. Never assume one returned row set maps perfectly to one Gaia astrophysical source without inspecting metadata and neighbouring objects.

## Working with survey-specific photometry

- Keep passbands separate, Gaia G/BP/RP distinct from ZTF g/r/i.
- Retain original `mjd`, `hjd` or other time fields, state conventions and convert using `astropy.time` with documented reference frames.
- Do not combine magnitude series directly as if absolute zero points and filter response curves were identical.
- Reject known bad ZTF epochs using the IRSA guidance (e.g. the documented `BAD_CATFLAGS_MASK=32768`), while separately testing stricter masking.
- Cache raw responses *outside Git* and record server response checksums and timestamps.

## Scale strategy

The default single-source ZTF API suffices for a small pilot. IRSA recommends HATS-based approaches for queries involving roughly more than 1,000 light curves. The architecture should support a cached per-object API backend and a scalable catalogue backend, never silently hammer a public API with unbounded parallel requests.

## Licenses and acknowledgments

Cite original scientific papers and follow Gaia and ZTF survey acknowledgment guidance and any CDS/VizieR catalogue access conditions before re-publication. No proprietary, unpublished ALMA observations or unpublished collaborative TFM data should be ingested into a public workflow.

Sources: https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html ; https://docs.astropy.org/projects/astroquery/en/latest/gaia/gaia.html ; https://gea.esac.esa.int/archive/documentation/GDR3/.