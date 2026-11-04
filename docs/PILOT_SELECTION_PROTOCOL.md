# Pilot design for disk/accretion variability — v0.2

## Confirmed focus

**Primary:** characterization of *candidate dipping and bursting* morphologies in young Taurus objects, with a physically cautious interpretation. **Secondary:** search for rotation/quasi-periodicity and sampling artifacts. A dimming event is not proof of circumstellar extinction; brightening is not proof of accretion.

## A priori selection

- Membership is defined from Luhman (2023), independently of observed variability.
- The first design proposal seeks 24 members: **12 Class II** and **12 Class III**, chosen only when source IDs, Gaia metadata, group names, and *independently vetted* disk class labels are available.
- Selection is deterministic (SHA256 source ID order within each kinematic group, then round-robin across groups). It does **not** optimize for known variability, ML scores or survey data availability.
- The 24-object size is an **engineering pilot**, not an unbiased population survey. It cannot estimate the overall Taurus dipper/burster fraction.
- Source brightness and Gaia/ZTF availability will be audited **after** selection rather than used to maximize successful detections; all missing survey coverage remains visible. The current technical pilot requires Gaia G magnitude, Gaia ID and a group to be recorded; therefore it preferentially covers cataloged sources and is not representative of all 532 Taurus members.
- If 12+12 well-supported labels cannot be found, the pilot selection should be revised by a versioned scientific decision. **Do not silently relax the criteria or fabricate missing labels.**

## Evaluation plan (not executed)

1. Confirm table identity and exclusions. Freeze selected identifiers.
2. Retrieve Gaia metadata by **exact source ID**. Compare Gaia queried entries, failures and astrometric quality, including missing epoch photometry.
3. Plan ZTF g/r queries for each target and report the available number of object identifiers and epochs, seasonal gaps, quality flags and blends.
4. Compute only robust QC metrics first. Produce diagnostic plots for all targets including non-detections.
5. Introduce physically motivated features (flux/color asymmetry, variability timescales, periods) only after per-band and survey-time conventions are reviewed.
6. Build control and injection-recovery experiments before proposing any anomaly model.

**Decision checkpoint:** Review the actual 24-object list, data coverage and at least 5 raw diagnostic light curves before broad retrieval or training ML.