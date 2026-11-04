# Phase 8 — Observational evidence, data integrity and cadence selection effects

**Status:** internal technical research, 2026-11-04. All Taurus science counterpart claims remain blocked. **239 automated tests pass.**

## 1. Why this phase exists

A preliminary dipper/burster classifier built only with simulated input can pass hundreds of tests yet still fail when fed an archival IRSA response. A critical example: official-looking ZTF source-data tables include *both* `mjd` and `hjd`. In v0.7, the parser rejected these multi-clock records as ambiguous. v0.8 keeps them, using **MJD > HMJD > HJD** priority and checking that the other available clocks agree approximately (`HJD - MJD ≈ 2400000.5` days, plus a heliocentric correction of minutes). **No unadvertised time conversion is attempted.** MJD and heliocentrically corrected timestamps must never be mixed in a period fit.

Reference: [IRSA ZTF Lightcurve API](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html), [IRSA DR24 lightcurves tutorial](https://caltech-ipac.github.io/irsa-tutorials/ztf-lightcurves/), [ZTF release documentation](https://ztf.ipac.caltech.edu/page/dr8).

## 2. Offline third-party observational-format compatibility

From an external public GitHub source, we inspected an 8-row CSV preserving `oid`, `expid`, `hjd`, `mjd`, `mag`, `magerr`, `filtercode`, `catflags` and positional fields. It is *presented by that source as ZTF photometry*, but **we cannot independently verify equivalence with the original IRSA release**, its license or its astrophysical target. Thus this is an engineering compatibility test only — **not one of our Taurus objects**.

- Pinned location: <https://github.com/gvard/lcurvemaker/blob/6e4228493d88985da0cfe1a75415988796879a4c/data/raw/rybka2-zi1.csv>.
- GitHub file blob SHA: `0006348051b2fa73cfe62392edda963ab2d2c825`.
- Locally examined source file SHA-256: `5acb151f6e56b748ebd9ae551c4ce284d98a4299640711065a0553066cd140f2`.
- Raw records: **8**, same `oid`, filter i (`zi`). **6** records pass bit-mask QC. **2** have `catflags=32768` and are excluded.
- Among accepted epochs, maximum gap: **732.01 days**, so no claim of continuous coverage is possible. **Only six** epochs, below the 30-epoch exploratory threshold.
- No period search, dipper/burster label, source crossmatch, disk classification or discovery is issued.

Raw third-party data bytes are **not bundled** in this release; only derived aggregate results, a graphic and a source pointer with the hash are kept. Reproduction on a machine with external access is performed by downloading the exact pinned file and running `scripts/run_v08_observational_audit.py --origin secondary_public_example ...`.

## 3. Exact cadence-window opportunity measure

Suppose QC-preserved observation epochs are sorted as `t[0], ..., t[n-1]`. For a hypothetical event lasting `d` days, with event-start time `s` uniformly distributed over the interval `[t[0], t[n-1]-d]`, the event can contain at least `k` observed epochs only when **at least one block of k consecutive observations falls inside [s, s+d]**.

For a block starting at epoch i, the allowed start interval is

`[t[i+k-1]-d, t[i]] ∩ [t[0], t[n-1]-d]`.

We compute the union length of these intervals and divide by the possible event-start interval length. This is an **exact deterministic geometrical fraction** (modulo floating-point precision), not a Monte Carlo estimate. It assumes a *uniform prior on start time*, a specific duration d, independent of photometry, and does not include detection thresholds. Therefore it is **neither the occurrence rate of genuine dippers nor the empirical completeness of the photometric algorithm**. It should be interpreted only as an opportunity-to-sample benchmark. The algorithm is checked against analytically soluble examples, coordinate-origin invariance and independent numerical quadrature.

For the small external example (6 accepted epochs spanning 1,137.87 days) and a hypothetical event requiring at least two observations, the fraction of allowed event-start times with two samples is approximately 0% for duration 2 days, 0.094% for 5 days, 0.538% for 10 days, 1.44% for 20 days and 3.29% for 40 days. These values are **not** rates for Taurus or for any physical variability population.

## 4. Taurus pilot readiness ledger

A reproducible 24-row status matrix now lists target Gaia DR3 identifiers, actual catalogue coordinates and groups, separately labeled approximate epoch J2021.0 propagated positions, and illustrative IRSA query URLs. FT Tau and CIDA 11 remain the prioritized targets. This **does not establish a Gaia–ZTF counterpart** and uses no new ZTF measurements.

To graduate from `blocked_awaiting_verified_ztf_raw_lightcurves`, each target must pass:

1. Original publisher table cross-check and agreed sample selection.
2. Archival IRSA response with stable raw SHA-256, request and release ID.
3. Per-OID/passband QC without conflating MJD, HMJD and HJD, plus adequate observation counts.
4. Proper-motion propagation to **actual survey epochs**, centroids, image crowding and nearby controls.
5. Matched-epoch cross-band corroboration, field systematics checks and injection/recovery on the **real** sampling and uncertainties.
6. Human scientific review of possible physical scenarios against independent literature.

## 5. Engineering/industry transferability

Demonstrated: input-data contracts, schema drift robustness, reproducible SHA-256 provenance, deterministic analytical coverage algorithms, regression testing, explicit quality/ethics gates, conservative source attribution, astronomy-specific time-series thinking and data-product delivery.

Not yet delivered: service deployment, cloud scale tests, monitoring, ML models on authentic Taurus data, independent scientific discovery, peer-reviewed publication. These are longer-term tasks and must not be included as completed results in a CV.

## 6. How to reproduce

```bash
python -m pip install -e '.[analysis,test]'
python -m pytest -q
python scripts/build_v08_readiness.py

# Retrieve the pinned external sample outside the repository, then:
python scripts/run_v08_observational_audit.py \
  --input /path/to/rybka2-zi1.csv --output reports/generated/secondary_check \
  --origin secondary_public_example \
  --source-url 'https://github.com/gvard/lcurvemaker/blob/6e4228493d88985da0cfe1a75415988796879a4c/data/raw/rybka2-zi1.csv' \
  --expected-sha256 5acb151f6e56b748ebd9ae551c4ce284d98a4299640711065a0553066cd140f2 --plot
```

**Scientific conclusion:** No Taurus transient, class, periodicity or disk morphology has yet been verified from ZTF. This phase validates the research machinery and exposes an important source-format defect fixed before any inference.