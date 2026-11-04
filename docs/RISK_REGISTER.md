# Scientific and technical risk register

| Risk | Consequence | Mitigation | Current state |
|---|---|---|---|
| Literature membership incompletely digitized | Sample selection cannot be reproduced | Locate exact member table, retain table release and Gaia IDs, manually audit disagreements | Open |
| Gaia epoch photometry missing | Biased Gaia+ZTF subset | Report coverage vs whole reference sample; model availability independently | Known |
| Gaia–ZTF cross-match ambiguous | False variability / wrong source | Epoch propagation, astrometric error budget, blend checks, alternative matches | Open |
| ZTF `oid` fragmentation / flag issues | Artifactual variability | Keep oid/band/CCD metadata; inspect masked/unmasked results | Known |
| Irregular sampling and aliasing | False periods | Window-function plots, injection/recovery and independent comparisons | Open |
| Labels contaminated or trained on same survey signal | Inflated ML accuracy | Independent reference groups; source-level splits and provenance ledger | Known |
| Small true positive set | Wide confidence intervals | Bootstrap per source, conservative claims, expert object review | Open |
| Extinction / distance / disk bias | Misleading physical classification | Compare matched subsets and model selection effects | Open |
| Archive limits and changing endpoints | Unreliable downloads | Cache, bounded retries, versioned source manifest and HATS path for bulk ZTF | Open |
| Over-engineering before science | Beautiful UI but no research contribution | Gate ML/UI on pilot diagnostic evidence and useful science questions | Preventive |
| Overclaiming new discoveries | Reputational/scientific damage | Candidate statuses + literature cross-check + manual validation | Preventive |
| AI-generated code not understood | Cannot defend work at interview or in research | Human review, tests, annotated decisions, transparent assistance statement | Preventive |

## v0.5 additional risks (2026-11-04)

- **Coherent photometric calibration artifact (critical):** every trial of our deliberately synthetic coherent-offset control triggered the event screen. Require cross-band/source/image checks, exposure-level quality metrics and injection into real cadence before declaring any astrophysical episodes.
- **Transport and selection (high):** current environment cannot query IRSA; available ZTF observations for the 24-source seed are not yet known. Treat missing data as missing; never backfill with simulated curves.
- **Catalog reference epochs (high):** the Luhman compiled coordinates have heterogeneous provenance. Gaia DR3 motions must be considered before final ZTF OID cross-identification. Approximate geometry is not a scientific match.
- **Survey selection and sample representativeness (high):** the 24-source seed was chosen to exercise software across groups and magnitudes, not to estimate class fractions or scientific completeness. No disk-based sampling design is implemented yet.
- **Benchmark extrapolation (high):** 420 trials use synthetic irregular timestamps, not genuine ZTF time windows. Neither observed completeness nor physical false-positive probability can be claimed from them.


### v0.9: offline data retrieval and false source authentication

- **Official archive inaccessible:** the two IRSA requests failed with `URLError`. Mitigation: retain source URLs, exception classes and raw-data absence; do not infer non-observation or astrophysical null detections.
- **Forged local provenance:** a manually written hash manifest does not cryptographically prove download from IRSA. Mitigation: distinguish integrity from authenticity in every dossier, never auto-confirm an `oid`.
- **Wrong counterpart due to averaged epochs:** using a single centroid at an approximate global epoch can hide positional inconsistency across measurements. Mitigation: per-MJD Gaia propagation and OID-by-band status; still require image/blending review and covariance.
- **Cache overwrite risk:** blindly re-downloading could destroy original raw evidence. Mitigation: v0.9 uses content-hash and request-URL validation before any attempt to fetch into an existing path.