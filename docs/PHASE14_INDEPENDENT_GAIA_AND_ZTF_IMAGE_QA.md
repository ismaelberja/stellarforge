# StellarForge v1.4 — Independent Gaia DR3 field screening and ZTF image access

**Engineering milestone:** independent sky-field audit, not scientific cross-identification or resolved contamination.

## Why this stage is necessary

The v1.3 Gaia/ZTF positional screen found offsets of around 0.06–0.09 arcsec for six ZTF OID-band curves returned from two pre-selected cones. This is not an unbiased identity test: another star or an unresolved blend can share an image centroid, while multiple ZTF OIDs can correspond to different fields observing the same star.

v1.4 therefore asks independent questions:

1. **Gaia DR3:** what additional Gaia-catalogued objects exist within a 15-arcsec ICRS radius of each target? How close are they to the Gaia target's nominal observed-epoch position?
2. **Astrometric solution quality:** how reliable is each Gaia source's fit, including RUWE? A high RUWE flags a potentially problematic or non-single solution, but does not prove a binary.
3. **ZTF imagery:** can an actual dated science FITS cutout, or fallback reference-coadd FITS cutout, be located via official IRSA filenames tied to the existing ZTF rows? A FITS header alone is a transport check, **not an inspection of WCS, pixels, seeing or PSF blending**.

## Verified endpoints and source definitions

- Gaia DR3 `gaiadr3.gaia_source`, accessed using [ARI TAP synchronous ADQL](https://gaia.ari.uni-heidelberg.de/help.html) with an explicitly bounded 15-arcsec query.
- [Official IRSA ZTF image query API](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_api.html) for source- and sky-position metadata.
- [Official IRSA science and reference FITS filename rules](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_metadata.html).
- [ESA Gaia DR3 documentation](https://gea.esac.esa.int/archive/documentation/GDR3/Gaia_archive/chap_datamodel/sec_dm_main_source_catalogue/ssec_dm_gaia_source.html) and [Gaia's non-single-star input criteria](https://gea.esac.esa.int/archive/documentation/GDR3/Data_analysis/chap_cu4nss/sec_cu4nss_intro/ssec_cu4nss_intro_inputfiltering.html) on astrometric indicators.

## Reproducibility

```bash
python -m pip install -e '.[test,analysis]'
python -m pytest -q

# A locally downloaded, original IRSA acquisition ZIP is required.
# Neither FITS pixels nor raw photometric CSVs will be written to the Git repo.
python scripts/run_v14_field_review.py /path/to/IRSA_raw_archive.zip \
  --probe-images --require-gaia
```

The script first verifies the original IRSA source hashes and positional query metadata using v1.3 contracts. It then queries Gaia DR3 with ADQL, saves only an aggregate neighbour table, constructs one representative **science** and **reference** FITS cutout URL per OID-band, and optionally verifies only the initial FITS header.

The published CSV source positions are approximate 2D proper-motion measurements; no full Gaia error covariance, parallax or perspective is propagated. Target membership of Gaia DR3 is separately checked by exact source ID; an unavailable Gaia response or missing target **cannot be treated as a clean field**.

## Scientific limitations

- Zero Gaia-listed neighbours within a search radius does **not** rule out unresolved doubles, red/non-Gaia sources, sub-arcsecond blends, extended nebulosity or artifacts.
- Brightness differences in Gaia G cannot directly calibrate ZTF g or r PSF contamination.
- High RUWE is a warning about astrometric fit quality, not proof of multiplicity, stellar activity, or variability.
- FITS URL construction and FITS signature success are **not** WCS/PSF/crowding review.
- Historical ZTF source data are only read inside the ephemeral workflow runner; GitHub uploads must contain only small aggregate reports, never original raw CSVs or FITS image pixels.
- No new physical event detections, disc classifications, star matches or completeness estimates are claimed.

**Next stage:** when images are accessible, explicitly download and examine FITS WCS, target and neighbour positions, candidate PSF and local backgrounds; review CIDA 11's astrometric solution and the Taurus parent-table provenance.
