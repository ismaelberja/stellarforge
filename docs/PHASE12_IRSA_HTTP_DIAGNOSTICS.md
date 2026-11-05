# Phase 12 — HTTP diagnostics for the private two-target ZTF pilot

**State: engineering intake diagnostic, NOT an observational result.**

## Evidence baseline

On 2026-11-04, [GitHub Actions run 41866054392](https://github.com/ismaelberja/stellarforge/actions/runs/41866054392) finished as a successful *program execution*, even though the archived `PILOT_STATUS.json` recorded **0 / 2 raw photometric responses**. Both FT Tau and CIDA 11 raised `HTTPError`. That earlier audit did **not** capture the numeric HTTP code, so the exact remote failure was unknown. The independent Python regression run [41867264721](https://github.com/ismaelberja/stellarforge/actions/runs/41867264721) passed 325 tests.

## Change introduced in this diagnostic phase

- Capture the numeric HTTP status and a conservative failure category for *each* target without storing potentially sensitive HTTP error bodies.
- Differentiate HTTP failures, transport failures and rejected CSV formats. No exception is interpreted as "no sky coverage".
- Verify required ZTF columns even for a header-only CSV. A response without expected headers is **not** accepted as a legitimate zero-row light curve.
- The CI intake run uses `--fail-if-empty`. When neither of the pre-registered queries produces a valid-format raw response, the workflow exits nonzero, yet the audit files are still uploaded (7-day retention) and the summary is displayed.
- Existing photometric QC preserves distinct ZTF OIDs and passbands. These checks do not independently authenticate the source identity.

The official [IRSA ZTF lightcurve API](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html) documents `POS=CIRCLE ...`, `BANDNAME=g,r`, `BAD_CATFLAGS_MASK=32768` and `FORMAT=CSV`. HTTP diagnostics must be reviewed before changing the search radius or query scientific criteria.

## Reproduction

Run offline regression tests:

```bash
python -m pip install -e '.[test,analysis]'
python -m pytest -q
```

Manual live intake (two IRSA queries; no simulated sources and no login):

```bash
python scripts/ci_observational_pilot.py reports/generated/private_irsa_pilot --fail-if-empty
```

Output:
- `PILOT_STATUS.json`: server status, request URLs, target IDs, raw hashes when available, explicit unverified gates.
- `REPORT.md`: per-target intake summary.
- `*_IRSA_RAW.csv`: only for acceptable raw CSV responses; keep outside Git and never publish without review.

## Scientific completion gates still outstanding

1. Confirm IRSA access and retain a valid response or a fully classified remote error for both targets.
2. Validate the publisher-original Luhman (2023) Table 2 against the pinned third-party mirror.
3. Verify astrometric Gaia–ZTF associations, epochs, field blending and each candidate OID using images.
4. Audit time conventions, quality flags and observational cadences without mixing passbands or identities.
5. Perform injection/recovery on **real** cadences before estimating astrophysical detection efficiency.

**No verified Taurus ZTF light curves or physical dipper/burster discoveries are claimed at this stage.**
