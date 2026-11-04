# StellarForge v0.9 — Release notes

**Internal development release (not published on GitHub).**

- Added `epoch_evidence.py`: per-observation MJD propagation of Gaia DR3 proper motions, per-`oid`/band separations, all-epochs/mixed-epochs status and same-band candidate ambiguity checks.
- Added `observational_dossier.py`: evidence-gated source reports, strict local checksum checks, IRSA URL lookalike rejection, explicit unresolved scientific gates and safe offline HTML dashboard.
- Added `scripts/run_v09_pipeline.py`: reproducible two-source FT Tau/CIDA 11 acquisition attempts and offline dossier generation. `--execute` makes at most two official IRSA requests and logs network exceptions without inventing observations.
- Added `scripts/plot_v09_catalog_motion.py`: 2018–2024 predicted sky-motion tracks using **published catalogue proper motions**. These are calculated catalogue positions, **not** ZTF measurements.
- Tested both official IRSA requests from the current environment; both failed with a network `URLError`. No Taurus light curve has been acquired or authenticated.
- New `reports/observational_gates_v0.9/`: two target dossiers, the official URL query plan, source acquisition summary, standalone evidence dashboard and an astrometry figure.
- **303 Python tests passed (64 tests added to 239 v0.8 tests).** No physical dipper/burster labels or discoveries.

**Scientific limitations:** Third-party Luhman Table 2 mirror has not been byte-compared with the publisher's archive. The positional model lacks parallax and covariance; ZTF images and independent control stars remain outstanding. The evidence dashboard is readiness monitoring, not a scientific result.

Read [`docs/PHASE9_PER_EPOCH_ASTROMETRY_AND_EVIDENCE_GATES.md`](docs/PHASE9_PER_EPOCH_ASTROMETRY_AND_EVIDENCE_GATES.md) for detailed scientific methodology and next steps.