# ADR-0003: Event triggers are review candidates, not dipper/burster classes

Date: 2026-11-04

**Decision:** the first event-scanning stage returns direction, timing, amplitude, measurement evidence and warnings only. The terms `fading` and `brightening` are photometric signs; astrophysical labels `dipper`, `burster`, `variable extinction` or `variable accretion` require independent evidence.

**Rationale:** synthetic stress tests include a coherent instrumental calibration-offset control; the current screen detects it as readily as a real-signal injection. Further failure modes include source contamination, atmospheric conditions, zero-point shifts, low-cadence undersampling and poor multi-filter source association.

**Risk control:** preserve raw photometry and QA flags; keep `discovery_claim=false`, `physical_cause_identified=false`; require manual review, cross-band consistency, direct image checks, proper-motion matching and real-cadence injection recovery before science catalog publication.

**Rejected alternative:** immediately train a classifier from synthetic event labels or public catalog membership. That would create pseudo-ground-truth and inflated apparent performance with no established external validation.