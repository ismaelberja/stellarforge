# ADR-0002: Archive cone search does not imply an identified Gaia source

Date: 2026-11-04

**Decision:** every response returned by an IRSA cone query must remain marked `unverified_source_association`, even when the positional separation is within the provisional radius. No downstream code may automatically assign a confirmed Taurus membership to a ZTF `oid` based only on this cone query.

**Rationale:** the 24 technical seed positions derive from a historical compiled census with potentially differing positional reference epochs. Gaia DR3 positions and proper motions must be propagated to ZTF observation dates; source table coordinates, resolution, blends and crowded field conditions require additional attention. Multiple ZTF `oid` values or separate filters must never be coadded without resolving identity.

**Cost:** some candidates will remain inconclusive, and the workflow needs image/source-level vetting.

**Audit:** `BATCH_MANIFEST.json`, per-target raw SHA256 sidecars, per-curve QC audit and source-match status fields.

**Future reversal criterion:** a tested, explicitly documented astrometric matching procedure with positional uncertainties, epoch propagation, ambiguity classes and image inspection evidence may promote a subset to `matched_vetted`.