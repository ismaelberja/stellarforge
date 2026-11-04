# ZTF small-batch runbook (v0.5)

## Before any network request

- The supplied 24-row membership subset is the **technical coordinate seed**, not a scientifically representative Taurus sample.
- Read IRSA's API policy and avoid large-scale polling through the single-object API. For >1,000 light curves, evaluate its HATS bulk catalogue as IRSA recommends.
- Run with an empty `reports/generated` directory or an existing **valid** manifest. Cached source bytes and request URLs are checked; mismatches stop that target.

## Offline query plan (safe by default)

```bash
python -m pip install -e '.[analysis,test]'
stellarforge batch-ztf --seed data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv --output reports/generated/ztf_batch
```

Expected: `mode = dry_run_no_requests`, `24` planned queries, `0` downloads and `0` verified ZTF matches. A completed dry-run manifest for this code revision is included at `reports/v0.5_ztf_dry_run/BATCH_MANIFEST.json`.

## Optional online acquisition, only in a network-enabled environment

```bash
stellarforge batch-ztf --seed data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv \
  --output reports/generated/ztf_batch --max-targets 2 --execute
```

Start with **two** technical targets and manually inspect their returned `oid` values, passbands, sky position, flags and downloaded images before increasing the batch. Raw CSV and `.provenance.json` files are stored under `raw/`. Normalized QC, audit and counts are stored per Gaia ID under `qc/`.

Result states:

- `not_executed`: dry-run only.
- `unverified_source_association`: downloaded and schema/QC-processed but source identification **not** established.
- `no_ztf_observations`: valid empty table, no observations.
- `download_or_qc_failed`: HTTP/network/schema problem; consult logs and retry responsibly.
- `cache_conflict_requires_manual_review`: source data or URL changed after recorded retrieval; never silently overwritten.

A repeated run uses an existing raw file only when its matching source URL and SHA256 in the provenance sidecar agree. This establishes **byte identity**, not astrophysical correctness.

## Exploratory event screening (requires actual normalized QC file)

```bash
stellarforge screen-events --input reports/generated/ztf_batch/qc/<GAIA_SOURCE_ID>/photometry_good.csv \
  --output reports/generated/ztf_batch/events_<GAIA_SOURCE_ID>.json
```

Inspect all returned `oid`, `band` and time-scale groups independently. Event candidates are only **review queue entries**. No automated physical classification is authorized at this stage.

## Operating constraints

- Single-target service uses public data only; do not use proprietary login credentials.
- Access is rate-limited by a 0.5-second minimum inter-target pause by default, bounded retries for transient errors, and a maximum of 100 targets per invocation.
- Raw data in `data/raw` or `reports/generated` should not be pushed publicly without checking source licensing, publisher conditions and privacy/attribution.
- DO NOT use the `SYNTHETIC` example outputs to report genuine stellar discoveries.