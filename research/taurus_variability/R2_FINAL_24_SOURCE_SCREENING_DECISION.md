# Taurus / StellarForge R2 — Final 24-source observational screening, original publisher source check and physical-identity NO-GO

**13 November 2026 · Frozen source-access and ambiguity-screening R2 deliverable.** This is the source-by-source R2 *screening adjudication*, not successful completion of the physical-source identity gate. The project remains eligible for a technically valid **feasibility study with a negative/inconclusive eligibility result**, not a new variable-star catalogue or an astrophysical publication.

**Decision:** `R2_SOURCE_ACCESS_AND_AMBIGUITY_SCREENING_COMPLETE__GAIA_ZTF_PHYSICAL_IDENTITY_NO_GO`. **No source is released to R3 physical stellar variability inference**. This is a documented scientific limitation, not an assumption that the 24 stars are physically nonvariable.

[Read the pre-registered R2 source acceptance rules](R2_24_SOURCE_FINAL_SCREEN_PREREGISTRATION.md) · [Machine-readable original-source 24-row ledger](../../reports/taurus_variability_r2/R2_FINAL_24_TECHNICAL_SOURCE_ACCESS_AND_IDENTITY_DECISION_NO_RAW.json) · [Offline claim and provenance audit](../../scripts/audit_taurus_r2_24_go_no_go.py).

## Major new original-data result: publisher’s actual Luhman (2023) Table 2 independently retrieved

For the first time in StellarForge, an actual [GitHub Actions original-publisher fetch run 43499836719](https://github.com/ismaelberja/stellarforge/actions/runs/43499836719) directly downloaded the publicly available [IOP/AAS journal machine-readable Table 2](https://content.cld.iop.org/journals/1538-3881/165/2/37/revision1/ajac9da3t2_mrt.txt) for Luhman (2023), *AJ* 165, 37 ([DOI](https://doi.org/10.3847/1538-3881/ac9da3)). The authentic HTTP 200 `text/plain` response contains **201,726 bytes**, original-source SHA-256 **`8ffd84c876afe6b6d7690f8e4ba4f97ec94f643e0e924c98f6c101b8656c0493`**. The existing strict fixed-width MRT parser read **532 adopted Taurus members**, **467** with Gaia IDs. All **24/24 frozen technical Gaia DR3 exact source IDs and their original sky positions matched** the publisher's adopted-members Table 2 to the previously predeclared precision (≤5×10⁻⁷ degrees per coordinate). No row was replaced and no target excluded. This *supersedes the previous “unverified secondary mirror” provenance issue for those 24 membership rows*.

It does **not** prove that the physical astrophysical classification of every source is immune to later literature revisions, or that their photometry belongs to corresponding IRSA/ZTF ObjectIDs. Full original publisher-vs-third-party mirror **byte identity** has not been asserted; only the original 24 IDs/positions were directly checked. The actual original table raw rows are not committed. [Permanent derived-only original publisher result](../../reports/taurus_variability_r2/R2_PUBLISHER_LUHMAN2023_ORIGINAL_24_OF_24_NO_RAW.json) · [source hash artifact 14072229650](https://github.com/ismaelberja/stellarforge/actions/runs/43499836719/artifacts/14072229650).

## Original Gaia and ZTF source-by-source decision

- **24/24** original DR3 exact Gaia source IDs retrieved; **17/24** pass preliminary Gaia-only astrometric criteria, **7/24** require RUWE/astrometric review. **0/24** have an additional *catalogued Gaia* source closer than 2″, **4/24** have a neighbour within 5″, but undetected multiplicity and source blending remain possible.
- **22/24** technical sky positions have *some* parsed **original ZTF positional-query response rows** across the previously recorded original survey calls. It is an **archive access figure**, not 22 Gaia–ZTF physical matches or scientifically QC-accepted light curves.
- **2/24** do not have populated parsed source responses: Gaia **3314244366165299584** returned an original zero-row CSV under `NOBS_MIN=5`; Gaia **3406270362673330944** ended with **HTTP 400** for `NOBS_MIN=1`. Neither is an astronomical non-detection.
- **4 historic original ZTF science/mask/PSFcat exposures** from the two FT Tau/CIDA 11 fields have genuine image-level QA, but without independently calibrated source astrometry and deblending. Across the following FT Tau study, additional original g/r dated exposures and PSF model tests add provisional technical evidence, not cross-survey authentication.
- **0/24** physically authenticated Gaia–ZTF source counterpart associations meeting all predeclared gates; **0** original ZTF ObjectID time series merged into physical target light curves, **0** confirmed new variable stars or companions.

| # | Original technical identifier | Exact Gaia DR3 source ID | Gaia-only quality | ZTF source access | Historic image QA frames | Physical ID |
|---:|---|---|---|---|---:|---|
| 01 | IRAS 04125+2902 | `164800235906366976` | Prelim. OK | ZTF: filas originales | 0 | **Pendiente** |
| 02 | XEST 16-045 | `152362491654557696` | Prelim. OK | ZTF: filas originales | 0 | **Pendiente** |
| 03 | J04314644+2506236 | `150908490604475520` | Prelim. OK | ZTF: filas originales | 0 | **Pendiente** |
| 04 | J04124068+2438157 | `150073682105601408` | Prelim. OK | ZTF: filas originales | 0 | **Pendiente** |
| 05 | J04065364+2540368 | `162259951730099968` | Prelim. OK | ZTF: filas originales | 0 | **Pendiente** |
| 06 | V892 Tau | `164513602672978304` | Revisión RUWE | ZTF: varios ObjectIDs | 0 | **Pendiente** |
| 07 | MHO 3 | `163178387536338944` | Revisión RUWE | ZTF: filas originales | 0 | **Pendiente** |
| 08 | J04590305+3003004 | `156732977357829888` | Prelim. OK | ZTF: filas originales | 0 | **Pendiente** |
| 09 | PSO J074.1999+29.2197 | `156577881796362496` | Prelim. OK | ZTF: filas originales | 0 | **Pendiente** |
| 10 | IS Tau A+B | `151125919028356352` | Revisión RUWE | ZTF: filas originales | 0 | **Pendiente** |
| 11 | J04215482+2642372 | `152280165721635968` | Prelim. OK | ZTF: filas originales | 0 | **Pendiente** |
| 12 | FT Tau | `149623711269425408` | Prelim. OK | ZTF: filas originales | 2 | **Pendiente** |
| 13 | J04390637+2334179 | `146764465639042176` | Prelim. OK | ZTF: filas originales | 0 | **Pendiente** |
| 14 | LkHa 332/G2 A+B | `148116246465275520` | Revisión RUWE | ZTF: varios ObjectIDs | 0 | **Pendiente** |
| 15 | IRAS 04385+2550 | `148289831863907840` | Revisión RUWE | ZTF: filas originales | 0 | **Pendiente** |
| 16 | J04293011+2239154 | `145886539965771648` | Prelim. OK | ZTF: filas originales | 0 | **Pendiente** |
| 17 | J04343609+2225143 | `145125987155266048` | Prelim. OK | ZTF: filas originales | 0 | **Pendiente** |
| 18 | CIDA 11 | `3419110734340795648` | Revisión RUWE | ZTF: filas originales | 2 | **Pendiente** |
| 19 | J05073903+2311068 | `3418414193726125184` | Prelim. OK | ZTF: filas originales | 0 | **Pendiente** |
| 20 | J04333278+1800436 | `3314244366165299584` | Prelim. OK | ZTF: 0 con NOBS≥5 | 0 | **Pendiente** |
| 21 | MHO 4 | `3314299238667410176` | Prelim. OK | ZTF: filas originales | 0 | **Pendiente** |
| 22 | Haro 6-37 B | `3406270362673330944` | Revisión RUWE | ZTF: error HTTP 400 | 0 | **Pendiente** |
| 23 | J04464590+1659544 | `3406269778557780224` | Prelim. OK | ZTF: filas originales | 0 | **Pendiente** |
| 24 | RX J0422.1+1934 | `48193213849576320` | Prelim. OK | ZTF: filas originales | 0 | **Pendiente** |

*The table deliberately labels every physical match as pending. An optical-source access success and a nominally “good” Gaia RUWE are not independently authenticated astrometry.*

## Exact cases requiring special care

**FT Tau** (Gaia DR3 149623711269425408). The [authentic external CDS SIMBAD exact-name check](R2_REAL_FTTAU_SIMBAD_GAIA_EXACT_ALIAS_RESULTS.md) maps FT Tau ↔ Gaia ID to the same catalogued entry *V* FT Tau*. This establishes the **curated historical name**, not the association to the four observed ZTF ObjectIDs. The original same-night g/r and different-field source ledger has **four distinct OIDs**, and the genuine frozen eight independent-night native source candidates remain **5/8 nominal quality PASS, 3/8 low-χ FAIL**. Only **1/4** frozen two-night same-OID source pairs passed both native QA gates. The separately studied six original spatial DAOPhot PSF models produced **6/6 numerical same-source fits**, with **4/6 provisional pixel-residual screen passes** and two r/609 review cases; that is *not* an independent different-star WCS/PSF calibration or proof of physical Gaia association.

**CIDA 11** (Gaia DR3 3419110734340795648). Real Gaia RUWE ≈**8.56752** requires review, with only same-pipeline original ZTF PSFcat and image QA and **two g/r ObjectIDs**. No independent physical association, calibrated source/blend model or time-domain inference is established.

**V892 Tau** and **LkHa 332/G2 A+B** have actual original *multiple OID* responses from positional queries; both have poor Gaia RUWE (≈3.55 and ≈16.30). That may be a detector/field/filter/astrometry ambiguity rather than separate physical sources. Do not merge OIDs or attribute optical variability to the Gaia targets.

## Why this is a scientifically valid R2 screening outcome, not a validated-source “PASS”

The [original R1 protocol](R1_PREREGISTERED_SCIENCE_PROTOCOL.md) explicitly accepts an unresolved/ambiguous technical cohort, as long as no missing source is silently called nonvariable. The [R1–R6 roadmap](R1_TO_R6_RESEARCH_PLAN.md) defines R2's operational deliverable as the *source-by-source association/ambiguity ledger with no unverified merges*. That **ledger now exists for all 24** and is checked against actual source-derived prior surveys and original publisher membership. However, its actual independent physical-source identity gates yield **NO-GO**: none can yet be **scientifically** assigned a Gaia-labelled ZTF stellar light curve.

This separates:
- **Completed:** 24-source access and ambiguity audit; original publisher 24/24 source membership-row IDs/positions; source provenance; explicit go/no-go decision.
- **Failed/unresolved:** independent original per-exposure physical Gaia–ZTF object identity, absolute WCS/PSF/deblend instrument calibration, complete original ZTF photometric source attribution. These do **not** become PASS because an audit is finished.
- **Allowed next:** R3 could produce a **technical no-physical-identity / data-coverage feasibility table** without linking target light curves, or R2 can be reopened only with genuinely independent high-resolution/epoch-calibrated source evidence. **Do not** calculate Gaia-target variability, periods, new companions, or population frequencies from unverified positional source data.

The software engineering release [v2.1.0](https://github.com/ismaelberja/stellarforge/releases/tag/v2.1.0) remains valid independently. This R2 scientific screening result does not alter the four-image historical v2.0 engineering release denominator or its validated source-code tests.

## Reproducibility and original evidence

```bash
python -m pytest -q
python -m scripts.audit_taurus_r2_24_go_no_go
# Live publisher-only source provenance (not required offline):
# python -m scripts.run_taurus_r2_publisher_original_crosscheck
```

- [Original exact Gaia 24-source run](https://github.com/ismaelberja/stellarforge/actions/runs/43029175432) and [derived-only per-ID RUWE + neighbour flags](../../reports/taurus_variability_r2/GAIA_24_ORIGINAL_PER_SOURCE_FLAGS_NO_RAW.json).
- [Original Gaia neighbours and the earliest 2/24 IRSA positions](https://github.com/ismaelberja/stellarforge/actions/runs/43031689454).
- [Original 22-target IRSA failure diagnosis recovering 13](https://github.com/ismaelberja/stellarforge/actions/runs/43037800319) and [nine-source final retry recovering seven](https://github.com/ismaelberja/stellarforge/actions/runs/43042786341), leaving two unresolved.
- [FT Tau four-OID original positional study](R2_REAL_FT_TAU_CIDA_ZTF_ALTERNATIVE_OID_RESULTS.md), [FT Tau original eight-night source gate](R2_REAL_FTTAU_MULTINIGHT_NATIVE_ASTROMETRY_RESULTS.md), [six-date spatial PSF study](R2_REAL_FTTAU_SIX_NATIVE_SPATIAL_DAO_RESULTS.md), [SIMBAD alias](R2_REAL_FTTAU_SIMBAD_GAIA_EXACT_ALIAS_RESULTS.md).
- [New authentic publisher source Table 2 original-data run](https://github.com/ismaelberja/stellarforge/actions/runs/43499836719). Original table bytes are never uploaded to the GitHub repository.

**Zero photometry raw rows, FITS original image pixels, private ALMA/TFM inputs or invented sources were committed in this study.** Software tests document the physical-association negative decision, not instrument correctness or new astronomical scientific discoveries.
