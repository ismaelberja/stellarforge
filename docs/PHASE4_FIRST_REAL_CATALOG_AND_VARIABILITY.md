# StellarForge v0.4 — first real Taurus catalog data + time-series diagnostic engine

**Status:** technical research milestone, **not** observational astrophysical results.
**Date:** 2026-11-04. **Approval:** research design still open; **not uploaded to the user's GitHub**.

## 1. Source acquisition: what we actually verified

A public GitHub copy of the machine-readable **Luhman (2023) Table 2, *Adopted Members of Taurus*** has been located and read via the connected GitHub research interface:

- Article: K. L. Luhman, *AJ* **165**, 37 (2023); DOI [10.3847/1538-3881/ac9da3](https://doi.org/10.3847/1538-3881/ac9da3).
- Machine-readable table identity in its header: `ajac9da3t2_mrt.txt`.
- Public mirror: [`themariavincent/get_targets/taurus_sources.txt`](https://github.com/themariavincent/get_targets/blob/7b6a5c83eca81fc66e50cb4889ee35cb28861367/taurus_sources.txt).
- Git commit pinned: `7b6a5c83eca81fc66e50cb4889ee35cb28861367`.
- Source Git blob SHA-1: `fe0d5a43dbd2ca8b867901686ab223a847c649e5`.
- Lines examined in the mirror: **694**, including header and description.
- Fixed-width adopted-member records: **532**; Gaia DR3 IDs: **467 distinct**, **65 members with no Gaia ID**.
- Named kinematic groups in the table: **13**; **119 members do not have an assigned named group** in that column. These counts are not estimates of ZTF coverage.

The 532 and 467 counts agree with the paper. That is a *structural validation* of the copy, **not** independent byte-for-byte comparison against the publisher's original machine-readable download. The entire 532-row raw catalog has **not** been materialized in the local package: the development container cannot perform outbound DNS requests, although the research connector can read the public GitHub copy. The downloader now exists and enforces the immutable Git blob checksum when run in a network-enabled environment.

## 2. Actual astronomical coordinates added

`data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv` contains **24 genuine catalog rows copied from that versioned source**, retaining Gaia IDs as strings, 2MASS identifiers, RA, Dec, spectral type, original table line number, Gaia G magnitude, proper motion and the published kinematic-group label. The positions are **real source metadata**, not synthetic fixture data.

### How these rows were chosen (provisional engineering sample)

1. Keep the *adopted member* records with nonempty Gaia ID, `Ref-Pos=Gaia`, a named kinematic group, nonempty proper motions and **12 ≤ G ≤ 17 mag**.
2. Choose **one** member per named kinematic group, minimizing `|G−13.5|`; ties break on Gaia source ID string.
3. From the **11 groups with the largest eligible membership**, choose one additional distinct member minimizing `|G−16.0|` with the same tie-break.
4. Sort the 24 final records by group and magnitude.

Thus all **13** named groups have at least one coordinate, while 11 have two. This is deliberately **not a representative demographic or disk-class sample**, and the magnitude cuts bias coverage. It is only a technical acquisition roster. It **does not replace** the proposed scientifically frozen, 12-Class-II + 12-Class-III study sample; the published disk-class data are still needed. Groups and selection can be reviewed before the actual science pilot is frozen.

A real-coordinate sky plot is in `reports/TAURUS_24_PRELIMINARY_SKY_POSITIONS.png` (marked *provisional*), without any fake photometric measurements.

## 3. Planned real ZTF queries — not downloaded

`reports/TAURUS_24_ZTF_QUERY_PLAN.csv` contains **24 valid IRSA positional query URLs** generated from the coordinates above. Each keeps the Gaia ID and source catalog line. URL parameters select g/r bands and reject the IRSA-recommended bad catflags bit 32768. All rows explicitly state `not_requested` and `epoch_propagation=required_before_final_crossmatch`.

**Why not claim a cross-match?** The Gaia coordinates have a reference epoch and ZTF can return multiple `oid` objects at one position. Full propagation using Astropy, proximity to neighbors, pixel crowding, passbands, aliasing and instrument quality must be checked first. A positional request or a successful download alone is **not evidence of unique source association**.

## 4. Time-series engine implemented

`src/stellarforge/variability.py` now computes, **per ZTF `oid` + band + time convention**:

- Weighted mean magnitude and reduced χ² against a constant-magnitude baseline.
- Median photometric error, standard deviation, robust 5th–95th percentile amplitude, median absolute deviation, excess-variance **proxy**.
- Explicitly defined brightness-tail asymmetry proxy: a **positive** value means an extended faint tail in **magnitudes**, negative means an extended bright tail. This is **not** a published Cody morphology index and does not prove extinction/accretion.
- A **floating-mean, weighted Lomb–Scargle** period scan using SciPy; period-range and time-baseline validation; timestamp spectral-window diagnostics; warnings around possible daily aliases.
- Optional seeded white-noise permutations of magnitudes and their errors. Reported exceedance is **not a calibrated false-alarm probability** and is not valid for red-noise significance or multiple-testing corrections.
- Explicit `physical_period_confirmed=false` and `photometric_variability_diagnosis=unassigned`.

To run exploratory features on any correctly QC-accepted normalized ZTF file:

```bash
python -m pip install -e '.[science,test]'
stellarforge inspect-ztf --input /path/to/raw_IRSA.csv --output reports/generated/qc
stellarforge analyze-ztf --input reports/generated/qc/photometry_good.csv \
  --output reports/generated/variability.json --min-period 0.5 --max-period 30
```

The project includes a demonstration against **synthetic** normalized ZTF fixtures only. No real ZTF measurements or period claims are published in this version.

## 5. Injection/recovery benchmark — explicitly synthetic

Executed with `python scripts/run_synthetic_benchmark.py --trials 24`. A known **5.271-day sinusoidal signal** is injected into simulated irregular observations; no real telescope data are used.

| Simulated cadence/noise regime | Period recovered within 5% | Meaning |
|---|---:|---|
| Irregular observations, high signal | **24/24** | Functional algorithm sanity check |
| Seasonal gaps, moderate signal | **24/24** | Synthetic robustness to the *chosen* seasonal windows |
| Sparse observations, low signal | **15/24** | **37.5% failures** in this low-SNR configuration |

The benchmark is limited to this toy signal shape, Gaussian noise and chosen cadence generator. **It does not establish sensitivity to real dippers, bursters, quasiperiodic signals or ZTF observational systematics.** Results are in `examples/SYNTHETIC_v04_benchmark/SYNTHETIC_benchmark.json`; every example figure is watermarked *SYNTHETIC*.

## 6. Gate for the next research milestone

Before choosing objects for physical interpretation or claiming source variability:

1. Acquire the publisher's machine-readable Table 2 and compare it to the pinned public mirror; keep the 532-row raw source with a SHA-256 provenance record.
2. Verify disk classes from an independent published catalog. Freeze a **scientific**, not technical, disk-stratified pilot before inspecting photometry.
3. Download several IRSA light-curve responses through an internet-enabled runner, inspect their true format and preserve raw-byte hashes, query parameters, flags and all returned object IDs, including nondetections.
4. Propagate source positions to relevant epochs and independently review ambiguous/close matches.
5. Run diagnostics on real cadences, then quantify false peaks and injection/recovery with realistic correlated variability, seasonal aliasing, multiple-test corrections and external known periods.
6. Only after those checks consider morphology labels, anomaly scoring and the eventual web application.

**This is a substantive engineering and source-provenance advancement, not a detection paper or a completed research platform.**