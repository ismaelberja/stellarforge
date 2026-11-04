# Phase 11 — Sample-selection bias in the Taurus technical pilot

## Scientific scope

To study dipper and burster *incidence*, a technical proof of concept cannot be treated as a population-complete study. The technical seed deliberately draws 1–2 members from each of thirteen named groups, suppressing the strong population imbalance among regions. No disk class labels have been independently confirmed. These stars cannot yet define the denominator of any empirical occurrence rate.

## Catalogue provenance

Luhman (2023), *The Astronomical Journal* **165**, 37, DOI: **10.3847/1538-3881/ac9da3**. The group totals and Gaia-ID status come from an immutable **third-party mirror** containing a fixed-width machine-readable copy. Git blob SHA-1 `fe0d5a43dbd2ca8b867901686ab223a847c649e5`; original publisher bytes are **not yet crosschecked**. The `luhman2023.py` parser requires the expected full table counts and preserves 64-bit Gaia identifiers as strings.

## Quantitative results (descriptive only)

- Adopted members: 532; Gaia DR3 IDs: 467; Gaia unavailable: 65.
- A group label is absent for 119 objects, including **64** of the **65** Gaia-ID-missing members. Thus apparent availability and group assignment are strongly associated; lack of a Gaia ID is **not** evidence against membership.
- Gaia ID with 12<=G<=17: 314. Adding an assigned named group: 289. Our 24-source seed covers 8.3% of this *eligible technical pool*, but was not randomized.
- The group-stratified seed cannot be used to infer regional disk frequency or event rates without a survey selection function.

The Wilson interval in the JSON/report is a descriptive comparison metric only; because this table is the audited working list rather than a random sample, it is not uncertainty on the total Taurus census.

## Preregistered exclusion and inclusion gates

1. A star has to be linked to a specific published Gaia source, preserving 64-bit identifiers without floating point loss.
2. Missing Gaia astrometry and unassigned group **must not** be silently equated with non-membership. Such sources remain in a separate coverage stratum.
3. Optical selection (12<=G<=17), survey-footprint overlap, temporal cadence and photometric quality must each have their own denominator.
4. Disk class and accretion indicators must come from an independent, explicitly cited study; their absence means `unknown`.
5. An IRSA ZTF cone query is a request, **not** confirmation of the Gaia counterpart. Use per-epoch astrometry and image blending checks.
6. An event is not a physical class, and a missed event is not a negative star. Injection/recovery over actual target cadences is required before occurrence statistics.
7. **Current status:** zero authenticated FT Tau or CIDA 11 ZTF source matches and zero physical candidates.

## Deliverables

- `reports/selection_bias_v1.1/MIRROR_SELECTION_AUDIT.json` for machine-readable proportions and group counts.
- `reports/selection_bias_v1.1/REPORT.md` for figures of merit and interpretation.
- Two PNG visualizations, from catalogue counts, not photometric observations.
- Unit tests and a reproducible offline runner.

## Following scientific milestones

Retrieve and byte-verify the primary paper's Table 2; then download DR24 public ZTF lightcurves for FT Tau and CIDA 11 on a network-enabled environment, retain precise query URL and SHA256, verify matching OIDs with images, and estimate detectability on *observed* cadences. This research remains private and incomplete.