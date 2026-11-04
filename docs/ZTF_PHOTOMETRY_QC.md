# ZTF photometry ingestion and quality control — v0.3

**Status:** tested against synthetic engineering fixtures, **not against an authenticated real Taurus/ZTF download**. No astrophysical variability, candidate or new scientific discovery is asserted in this version.

## Authoritative interface

IRSA light-curve API: https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html

ZTF documentation explains that a single sky position can return multiple `oid` identifiers; each describes a distinct light curve, often different band/field. Relevant fields include `oid`, `mag`, `magerr`, `catflags`, `fid`, and `mjd` or `hjd`. IRSA query parameters include `POS`, `BANDNAME`, `BAD_CATFLAGS_MASK`, and `FORMAT`. The mask `32768` excludes the documented cloud/moon-related flag. Additional quality bits can be configured by the scientific lead, but must be justified and sensitivity-tested. See https://irsa.ipac.caltech.edu/data/ZTF/docs/releases/dr06/src/dr06.html.

## Data contracts and checks

1. **Read-only raw preservation:** downloaded raw bytes are not altered. A local `.provenance.json` sidecar records the query URL, time, SHA256 and size. Re-ingestion fails if the raw SHA256 no longer matches that sidecar. An asserted source URL is *not* independent proof of dataset authenticity.
2. **Accept formats:** `FORMAT=csv` (recommended for new automated acquisitions) or `FORMAT=ipac_table` (existing offline connector default). IPAC uses fixed-width columns; do **not** split data rows on whitespace.
3. **Schema gate:** must contain `oid`, `mag`, `magerr`, `catflags`, a supported band (`fid`, `filterid`, `filtercode`) and exactly one non-empty time field among `mjd`, `hmjd`, `hjd`. Invalid schema fails immediately; invalid individual rows are counted by explicit reasons.
4. **Precise IDs:** `oid` stays as a **string** so long identifiers are not rounded by floating-point parsing. Each `(oid, band, time scale)` remains its own light curve.
5. **Quality:** reject non-finite values, bad/zero magnitude uncertainties, masked `catflags`, invalid coordinates and duplicate epochs for one OID/band/scale. Outlying magnitudes are *not* clipped: true dips and bursts can be extremes.
6. **Time scale:** MJD, HMJD and HJD are kept separate and **never naively subtracted from each other**. Scientific comparison requires time-scale verification, heliocentric/barycentric corrections as relevant, and precise time reference documentation.
7. **Association gate:** target coordinates must come from an independently verified membership catalogue and be propagated to an appropriate survey epoch. A fixed-radius comparison is **provisional geometry only**. If multiple OIDs in the same band fall within the radius, the result is flagged `ambiguous_multiple_oids`. Absence of coordinates leaves `position_unverified`.
8. **Completeness:** report total raw rows, accepted rows, rejected rows by reason, observation count per curve, band, time span, robust 5th–95th percentile amplitude, and source-separation audit. The configurable `min_good_epochs=30` is an **engineering triage threshold, not a validated detection limit**.
9. **No physical inference:** the audit does not assert that changes are due to rotation, extinction or accretion, nor compute period-significance or color-accretion correlations.

## Run an explicitly artificial reproducibility demo

```bash
python -m pip install -e '.[test]'
python -m pytest -q
stellarforge inspect-ztf --input examples/SYNTHETIC_ZTF_ONLY.csv \
  --output reports/generated/ztf_synthetic_demo \
  --target-ra 65 --target-dec 25 --min-good-epochs 30
```

The input is labeled **SYNTHETIC**. Its OIDs and celestial coordinates are fictitious; it is designed to illustrate two filters, an artificial dip, corrupted flags and ambiguous nearby OIDs. It must never appear in a scientific results table. The inspected output contains `ztf_audit.json` and `photometry_good.csv`.

## Run on *authentic* data when available

```bash
# First: independently validate a real Taurus member and its coordinate epoch.
# For the given vetted position, request a public response:
stellarforge plan-ztf --ra VERIFIED_RA --dec VERIFIED_DEC --bands g r
stellarforge fetch-ztf --ra VERIFIED_RA --dec VERIFIED_DEC \
  --output data/raw/verified_target_ztf.tbl
stellarforge inspect-ztf --input data/raw/verified_target_ztf.tbl \
  --target-ra EPOCH_PROPAGATED_RA --target-dec EPOCH_PROPAGATED_DEC \
  --output reports/generated/verified_target_qc
```

The command-line interface does **not** turn a hypothetical `VERIFIED_RA` into a real coordinate; values are placeholders. `fetch-ztf` preserves the raw file and sidecar. QC results remain *provisional* until a scientifically defensible association is signed off.

## Remaining scientific acceptance conditions

- Obtain the **complete** 532-row adopted Taurus list from Luhman (2023), Table 2, and verify identity, group assignments, and 467 Gaia entries.
- Record the **independent disk classifications** for target sampling without looking at candidate light curves beforehand.
- Validate actual ZTF CSV and IPAC responses, including null handling and the release/version currently public, on a small labeled sample. Formal integration tests against the archive must be run in a network-enabled environment.
- Implement full astrometric epoch propagation and blending checks, and document survey/target selection bias.
- Only then calculate morphology metrics (Q, M), Lomb–Scargle with window-function/alias diagnostics, injection/recovery, and credible ML validation.