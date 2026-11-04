# Taurus catalogue integration contract — scientific gate 1.5

This is a **data interface**, NOT an assertion that the complete adopted-members table has been downloaded. The source-of-truth is K. L. Luhman (2023), *AJ* 165, 37, DOI:10.3847/1538-3881/ac9da3, particularly **Table 2**. The paper reports **532 adopted Taurus members**, of whom **467 have Gaia DR3 entries** and **412 have Gaia DR3 parallaxes and proper motions**. A credible import must make missing Gaia metadata explicit rather than silently deleting those members.

## Source verification — required before pilot approval

1. Obtain the complete author/publisher machine-readable Table 2 from an official publisher, vetted archive or author-provided supplementary source. **Do not use a paper's visible sample rows or a positional Gaia cone as a substitute.**
2. Record exact download URL, original filename, source version/date, retrieval UTC, file SHA256, row count, citation and permitted reuse terms.
3. Independently confirm the correct **adopted-member** filtering, 532 count and the 467 Gaia DR3 references from the original data. Follow up duplicates, multiple systems, cross-identifications and missing astrometry.
4. Preserve the untouched original file in `data/raw/`, excluded from Git by `.gitignore`. Create a derived normalized CSV in a tracked schema, with a transformation script and validation report. Never silently supply default source positions, epochs or disc labels.
5. Review a stratified set of original-to-normalized rows manually, especially the members without Gaia identifiers and close multiple systems.

## Normalized table schema

Use `examples_schema.csv` as the **header-only** example. Unit tests employ synthetic records identified as SYNTHETIC, not astrophysical members.

| Field | Type | Interpretation |
|---|---|---|
| `target_id` | text, required and unique | Stable *source catalogue* identifier, not list index |
| `ra_deg`, `dec_deg` | finite degrees | ICRS RA/Dec from the stated coordinate source |
| `coord_epoch_jyear` | Julian year, required | Actual epoch of the positions; Gaia DR3 is J2016.0, **not automatically true for 2MASS/UKIDSS** |
| `membership_status` | `adopted`, `candidate`, `rejected`, `uncertain` | Derived from explicit source table membership, never a threshold on Gaia |
| `reference_id` | text, required | Identifies the reference release/table used for this row |
| `gaia_dr3_source_id` | decimal *string*, nullable | Gaia source ID. Never parse to floating point; null ≠ non-member |
| `pmra_masyr`, `pmdec_masyr` | nullable | mas/year; `pmra` includes cos(Dec) |
| `g_mag` | nullable | Gaia mean G magnitude; missing data remain missing |
| `group_name` | nullable | Published Taurus kinematic group, if independently established |
| `disk_class` | `I`, `II`, `III`, `transition`, `evolved`, `unknown` | **Independent vetted SED/disk label**, not assigned from model prediction |
| `coordinate_origin`, `notes` | nullable | Source of position and exceptions such as binaries |

We treat class II as the **pilot disk-bearing stratum** and class III as the **pilot diskless stratum**. The physical hypothesis is about candidate dips and bursts, not guaranteed disk/accretion diagnoses. Published labels such as *full*, *evolved* or *transition* require an explicitly documented mapping before they may be assigned canonical classes. If available disk classifications cannot be reconciled, the balanced pilot is **blocked** rather than filled with invented labels.

## Execution (only after genuine source data are obtained and normalized)

```bash
python -m pip install -e '.[test]'
stellarforge audit-members --input data/raw/taurus_normalized.csv --reference-url https://doi.org/10.3847/1538-3881/ac9da3 --output reports/generated/taurus_audit.json
stellarforge propose-pilot --input data/raw/taurus_normalized.csv --output reports/generated/pilot_proposal.json
stellarforge plan-gaia-batch --input data/raw/taurus_normalized.csv
```

The `--catalog-verified` flag for `propose-pilot` exists solely for use **after** a documented independent paper-to-table audit. Setting it is a human research decision, not evidence that the table is correct.

## Acceptance gate

- 532 adopted members **measured from the exact Table 2**; Gaia ID completeness reconciled with 467 paper entries; duplicates and missing data explained.
- Disk classes independently sourced and documented (or the disk-stratified pilot protocol amended and recorded).
- A provisional pilot roster is chosen **before** Gaia/ZTF variability data are inspected, using an immutable selection seed/method and reasons for exclusion.
- Original and derived files each have SHA256 and versioned provenance; manual QA sign-off recorded.

Until these pass, target-list files are proposals, never a scientifically validated sample.