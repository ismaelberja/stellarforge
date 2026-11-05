# StellarForge v1.4.0 — Independent Gaia neighbourhoods and ZTF image availability

**Research software milestone, not an astrophysical discovery.** Date: 5 November 2026.

## Engineering additions

- Independently query Gaia DR3 via a 15-arcsec TAP cone around each preregistered Taurus position, retaining exact Gaia source IDs, G magnitudes, parallaxes, RUWE and optional proper motions.
- Audit Gaia-catalogued neighbours at a representative ZTF observation epoch, with explicit row limits and fail-closed target-ID checks.
- Construct official ZTF **science and reference FITS cutout URLs** from the actual per-exposure `filefracday`, field, CCD, quadrant and band (including hex-coded CCD/quad identifiers).
- Optionally probe only the first FITS header bytes. Remote error 503, HTML or unavailable services are reported as **transport failures**, never non-detections.
- Reuse SHA-verified original IRSA acquisition ZIP, keep individual photometric records and FITS pixels outside the public Git history and publish only aggregate data.
- Add synthetic regression tests for near neighbours, malformed API outputs, off-domain FITS links, instrument metadata and scientific interpretation safeguards.

## Real observed-field findings

See [v1.4 Gaia/IRSA aggregate report](reports/field_review_v1.4/GAIA_NEIGHBOURS_AND_IRSA_IMAGES.md). Both Gaia searches found the respective Gaia DR3 target and no additional **Gaia-detected** source inside 15 arcsec. CIDA 11 has **RUWE 8.57**, raising a substantial astrometric-fit concern requiring independent study. Of six requested ZTF image groups, direct FITS header verification succeeded for **two in the latest attempt** and failed for four owing to HTTP 503. The previous attempt succeeded for a different group; the archive is intermittently unavailable.

**Limitations:** no ZTF images were visually inspected; no WCS, PSF, unresolved companions or field contamination analysis completed; no Gaia/ZTF identities independently confirmed. The pinned Taurus parent catalogue still requires byte comparison with publisher original.

## Engineering verification

The [public GitHub Actions workflow](https://github.com/ismaelberja/stellarforge/actions/workflows/tests.yml) runs the repository's offline unit/integration tests. Remote Gaia and IRSA verification workflows run manually to avoid unsolicited remote queries and uploads of raw scientific responses.
