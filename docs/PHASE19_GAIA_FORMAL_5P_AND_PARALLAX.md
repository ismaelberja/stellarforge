# StellarForge v1.9 — Gaia DR3 formal five-parameter covariance and annual geometric parallax

**Status:** astrometric *uncertainty-model pilot* for public Gaia DR3 targets; not an independent Gaia–ZTF identity check, instrument WCS solution, or astrophysical discovery.

## Why this phase

Earlier versions used a simplified 2D proper-motion propagation of Gaia's J2016.0 positions to nominal ZTF observation dates. The v1.8 reference-candidate audit measured small provisional median coordinate offsets in real ZTF science images, but the offsets must not be interpreted without Gaia's parallax or correlated catalogue errors. In particular, the target CIDA 11 has an elevated **Gaia DR3 RUWE ≈ 8.57** and can have serious unmodeled astrometric-fit systematics.

## Exact Gaia source queries

The pilot retrieves just two exact public Gaia DR3 source IDs through `gaiadr3.gaia_source`: FT Tau **149623711269425408**, CIDA 11 **3419110734340795648**. Source IDs are validated, the CSV must return **both exact entries** and all five astrometric errors and **ten Gaia five-parameter correlation coefficients**, and missing/invalid covariance **fails closed**.

Order of the five astrometric components: \(\alpha,\delta,\varpi,\mu_{\alpha *},\mu_\delta\). Units are milliarcseconds (mas) for positions/parallax and mas/year for proper motions. The symmetric \(5\times5\) covariance is \(C_{ij}=\sigma_i\rho_{ij}\sigma_j\), with \(\rho_{ii}=1\). The ten off-diagonal correlations are retained rather than silently assuming uncorrelated astrometry. A non-positive-semidefinite correlation matrix, nonpositive errors or wrong Gaia reference epoch is rejected.

Official catalogue definition: [ESA Gaia DR3 gaia_source fields](https://gea.esac.esa.int/archive/documentation/GDR3/Gaia_archive/chap_datamodel/sec_dm_main_source_catalogue/ssec_dm_gaia_source.html).

## Numerical geometry and propagation

1. Interpret the four nominal ZTF exposure MJDs documented in the v1.8 audit as UTC **provisionally**, pending per-image timing metadata verification.
2. Obtain Earth's **ICRS barycentric position** with Astropy's offline built-in solar-system ephemeris; no JPL download is needed. [Astropy API](https://docs.astropy.org/en/stable/api/astropy.coordinates.get_body_barycentric.html).
3. Propagate Gaia catalogue position with its two-dimensional proper motion to the observation's Julian year, respecting \(\mu_{\alpha *}\). Add a **first-order geometric geocentric annual parallax shift** by subtracting the Earth barycentric vector projected onto the star's tangent plane, scaled by Gaia's *signed* trigonometric parallax.
4. Use a deterministic five-input/ two-output central-difference Jacobian of the exact implemented model and propagate Gaia's catalogue covariance as \(C_{\mathrm{east,north}}=J C_{5p} J^\mathsf{T}\). The reported east and north standard deviations are the diagonal square roots, in mas. The off-diagonal covariance is retained in aggregate JSON.
5. Explicitly compare the parallax-shifted position with **the same implementation's** linear proper-motion-only prediction to quantify the size of the annual-parallax correction.

The calculation is a **geocentric geometric screening model**. It is **not the full apparent optical sky position** and **does not include** radial velocity/perspective acceleration, relativistic aberration, atmospheric refraction, Palomar topocentric parallax, FITS WCS distortion, photometric PSF centroid systematics, survey chromatic effects or a completed uncertainty budget for ZTF. For six-parameter Gaia solutions, the module propagates the reported astrometric five-parameter submatrix but **does not model the sixth pseudocolour parameter or its effect**.

## Quality-control interpretation

The reported formal Gaia uncertainty is *only the propagated formal covariance of Gaia's fitted astrometric parameters*. A high RUWE means the underlying single-object astrometric solution may be problematic; the covariance can **underestimate the actual positional error**. Even with a low RUWE the estimated formal uncertainties do not include independent ZTF/IRSA image or PSF errors.

No Gaia catalogue position or corrected coordinate can establish that a ZTF `oid` is the same astrophysical star. No source identity, deblending, binary companion, physical motion, period or variability event is confirmed here.

## Reproduce

    python -m pip install -e '.[test,analysis,images]'
    python -m pytest -q
    python scripts/run_v19_gaia_formal.py --output reports/generated/v1.9_gaia_formal

The Gaia query is a bounded read-only query for two exact IDs. Public workflows upload **only derived summary JSON/Markdown**, and the workflow is configured as manual-only after the initial real-data validation. No third-party Gaia raw CSV or ZTF FITS pixels enter the public Git repository.

## Next scientific validation

A real **multi-star ZTF detector WCS calibration** and an empirically validated reference-star PSF/morphology model are separate scientific gates, as is full Gaia source-identity verification. CIDA 11 must be reviewed for non-single-star solutions or astrometric excess-noise sources before interpreting physical displacements. Extend the corrected Gaia positions to the six original ZTF OID/filter groups only with provenance, observation times and calibrated instrumental uncertainties.

**Scientific confirmations: 0 independent Gaia–ZTF source identities; 0 calibrated WCS/PSFs; 0 astrophysical companions or new physical variability events.**
