# ADR-0001: Research-first architecture, not an ML-first demo

**Status:** Accepted for Phase 1; re-evaluate after the first verified survey sample.

## Context

A generic 'find unusual stars' classifier is vulnerable to artefacts, selection bias and misleading validation. A visually appealing demonstration could obscure these limitations and would not stand up to scientific scrutiny.

## Decision

Use an independent literature sample, source provenance, reproducible survey adapters and diagnostic statistics before training or deploying ML. Keep the first implementation offline-first and small. No public GitHub publication until an appropriate scientific milestone is reviewed.

## Consequences

- Slower project completion, but better scientific credibility and explainability.
- Need to resolve membership tables, Gaia DataLink coverage, matching ambiguities and ZTF sky coverage.
- More defensible experience demonstrating data integration, quality assurance, astronomy domain knowledge and reproducible scientific software.