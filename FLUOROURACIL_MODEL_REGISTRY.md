# 5-FU / DPYD Toxicity, Exposure & Dose Model Registry

> **Status:** research registry, compiled 2026-09-16. Provenance-governed.
> **Scope:** reusable public 5-fluorouracil (5-FU) PK / TDM / PBPK / PK-PD /
> limited-sampling / dose-adjustment models worldwide, with exact code / data /
> license / access provenance and a *safe-to-implement-now* vs
> *requires-runtime-qualification* verdict per layer.
> **Platform invariant this obeys:** the deterministic layer decides; a model
> only *explains / estimates*; every claim cites a source; every refusal is
> named. **This registry does NOT authorize any clinical 5-FU dose
> prediction** — see §Refusal contract.

---

## 0. How this connects to what already ships

The engine already ships a **deterministic DPYD clinical-action tier**
(pgx-core `phenotype/clinical_action.py`, table
`DPYD_CLINICAL_ACTIONS_v2024.01.json`, CPIC guideline 100419 / PMID 29152729):
DPYD phenotype → closed enum `AVOID` / `REDUCE_50PCT` / `STANDARD` /
`INDETERMINATE`, surfaced through anukriti-api `/runs` and the frontend
`MtbReportCard`. That tier is a **genotype→starting-dose** projection.

Everything in this registry is a **different axis**: *exposure* (AUC),
*toxicity* (myelosuppression), and *concentration-guided dose adjustment* (TDM
/ MIPD). None of it overrides the deterministic phenotype call. The honest gap
these models address is the one the Tan 2026 paper quantifies and every source
here confirms: **~50% of severe 5-FU toxicity occurs in patients with no DPYD
variant**, and only ~20% of BSA-dosed patients hit the AUC 20–30 mg·h/L target.
DPYD genotyping and exposure/TDM are complementary, not substitutes.

---

## 1. Target-therapeutic window (the anchor every model shares)

- **AUC0–inf target: 20–30 mg·h/L** for infusional 5-FU (colorectal), from the
  **international consensus TDM guideline — Beumer et al. 2019, IATDMCT**,
  *Clin Pharmacol Ther* 105(3):598–613 (PMID 30618436). This is the load-
  bearing citation the modern models (Tan, Briki) target.
- Historical therapeutic-range origin: **Gamelin 1998/1999** weekly regimen,
  AUC0–8 16–24 mg·h/L (2000–3000 µg/L). Gamelin 2008 RCT (JCO, PMID 18445839)
  is the pivotal evidence that PK-guided dosing beats BSA dosing.
- Toxicity concentration thresholds (research-only): life-threatening toxicity
  associated with plasma > 6 mg/L; steep toxicity rise 3–4 mg/L (MDPI *Pharmaceuticals*
  2025, PMC-indexed).

**Registry rule:** the 20–30 mg·h/L window may be *stored as a cited constant*
(like the CPIC tables). It must NOT be turned into an automated dose
recommendation without runtime qualification (§4).

---

## 2. THE REGISTRY (source-of-truth table)

Legend — **Artifact type:** SRC = runnable source/model code · DATA = raw
patient/parameter data · PARAMS = published parameter table only (reconstruct
by hand) · APP = interactive tool.

| # | Model / source | Year | Structure & scope | Public artifact | Artifact type | License | Access status |
|---|---|---|---|---|---|---|---|
| M1 | **Tan** (Clin Pharmacokinet, DOI 10.1007/s40262-026-01645-1) | 2026 | 2-cpt **Michaelis–Menten**; covariate = BSA allometric on Vmax (exp 1.14); pooled NL cohort (n=140), FOLFOX/FOLFIRI/FOLFIRINOX/FLOT, bolus+46h & 24h/46h CI; **LSS** derived; DPYD tested, **NOT** significant | **Model code in supplementary DOCX** + **live Shiny app** `tanzy1995.shinyapps.io/5FU-shiny-app` (mrgsolve + mapbayr) | SRC + APP + PARAMS | **CC BY-NC 4.0** (OA) | **Open.** App = "research use only". |
| M2 | **Briki IPD-MBMA** (Cancer Chemother Pharmacol, DOI 10.1007/s00280-026-04885-x) | 2026 | 2-cpt **mixed** (MM Vmax/Km + linear CL); IPD meta-analysis n=726 / 2,332 conc from 3 studies; BSA→CL, sex & age→Vmax, **LBM** translation; MIPD/TDM simulation | Paper only; **data "on reasonable request"** subject to sharing agreements; **no code repo** | PARAMS (partial) | Springer proprietary (paywalled) | **Restricted.** Model = the "Briki 2024" PAGE abstract #10998 externally evaluated by M1. |
| M3 | **Marok chronomodulated PBPK** (Saarland; *Clin Pharmacol Ther* 2024, DOI 10.1002/cpt.3181) | 2024 | Whole-body **PBPK** parent-metabolite: 5-FU, uracil, 5,6-dihydro-FU, 5,6-dihydrouracil; sinusoidal **DPD circadian** functions; chronomodulated & constant-rate infusions, bolus, oral | **GitHub** `Clinical-Pharmacy-Saarland-University/5-FU-PBPK-Model` — 4× `.pksim5` files (PK-Sim v9.1) | SRC (model files) | **GPLv2** (OSP ecosystem) | **Open.** Runs in free PK-Sim/MoBi (GPLv2). |
| M4 | **OSP PBPK Model Library** | ongoing | Curated qualified PBPK substance models + evaluation reports | GitHub `Open-Systems-Pharmacology/OSP-PBPK-Model-Library` (5-FU not yet in the top-level curated list; M3 is the 5-FU model) | SRC | GPLv2 | **Open.** |
| M5 | **Arshad semi-physiological PK-PD** (Cancer Chemother Pharmacol 85:711, PMID 32152679) | 2020 | 2-cpt linear 5-FU + 1-cpt 5FUH2 metabolite; **Friberg myelosuppression** (WBC), 3 transit cpts; **linear** drug effect; cisplatin↑slope; n=30 GI, 5-day CI; DPYD/TS/MTHFR tested (not sig.) | Full **parameter tables in text**; supplementary PDF (969 kb); **no model code** | PARAMS | **CC BY 4.0** (OA) | **Open (params).** Reconstruct in NONMEM/mrgsolve by hand. |
| M6 | **Kaldate AUC-dose algorithm** (Oncologist 17:296, PMID 22382460) | 2012 | AUC↔dose relationship → **FOLFOX6 dose-adjustment nomogram** | Paper (algorithm/equations) | PARAMS | Wiley proprietary (OA on PMC) | **Open text; algorithm only.** Ancestor of M1's MIPD dose logic. |
| M7 | **Gamelin PK-guided dosing** (JCO 2008 RCT PMID 18445839; 1998 PMID 9667242; 1999 uracil ratio) | 1998–2008 | Weekly bolus/CI dose-titration algorithm to AUC0–8 target; DPD uracil/UH2 ratio predictor | Papers (algorithm + nomogram) | PARAMS | Proprietary | **Open text.** Foundational evidence, not code. |
| M8 | **van Kuilenburg Bayesian LSS** (Clin Pharmacokinet 51:163, 2012) | 2012 | 2-cpt MM; **DPYD c.1905+1G>A carriers**; single 60-min post-bolus sample → identifies DPD-deficient (PPV 96%) | Paper (params + LSS) | PARAMS | Proprietary | **Open text.** The DPYD-aware LSS. |
| M9 | **Jacob (India — CMC Vellore)** (Br J Clin Pharmacol 87:937, PMID 32592630) | 2021 | 5-FU + 5FUH2 exposure; **5-sample LSS** (bolus + 44h CI) via MLR + trapezoidal; Indian GI-cancer cohort | Paper (LSS equations) | PARAMS | Proprietary | **Open text.** The **Indian** LSS. |
| M10 | **Tamura (Japan)** (Int J Med Sci 8:406, 2011) | 2011 | Effect of **bolus** on steady-state 5-FU Css; Japanese advanced CRC | Paper | PARAMS | OA | **Open text.** Asian/Japanese cohort evidence. |
| M11 | **Older PopPK set** — Bressolle 1999 (circadian), Terret 2000 (dose/time-dependence), Mueller 2013 (gender), Woloch 2012, Etienne 1998, Sandström 2006 | 1998–2013 | 1-/2-cpt linear or MM PopPK; various covariates | Papers | PARAMS | Proprietary | **Open text.** All externally evaluated & found insufficient for a generic regimen by M1 — kept for provenance/benchmarking. |
| M12 | **My5-FU immunoassay TDM** (NICE DAR, NBK326900; Saladax) | 2014 | Not a model — nanoparticle immunoassay for measuring 5-FU to feed a TDM loop | HTA report | (assay) | Crown/OA report | **Open report.** Measurement layer, not a model. |

---

## 3. Distinguishing SOURCE CODE from DATA (critical for reuse)

- **Runnable source you can execute today (SRC):**
  - **M3 Marok PBPK** — `.pksim5` model files, GPLv2, run in free PK-Sim 9.1+.
  - **M1 Tan** — Shiny app (live) + model code in the supplement (mrgsolve).
- **Parameters only (PARAMS) — reconstruct, do not "download and run":**
  M2 (partial), M5, M6, M7, M8, M9, M10, M11. These give equations + estimates;
  reproduction is a hand build in NONMEM/mrgsolve/nlmixr and must be re-verified.
- **Raw patient data (DATA):** effectively **none are openly downloadable**.
  M1 "from corresponding author on reasonable request"; M2 "on reasonable
  request, subject to data-sharing agreements". Treat all raw-data claims as
  **request-gated, not public**.
- **Assay, not a model:** M12.

> Provenance flag: a `.pksim5` or a Shiny app is *source*; a parameter table in
> a PDF is *not a dataset and not runnable code*. Do not conflate them in any
> ingest manifest.

---

## 4. Layer-safety verdict — implement-now vs runtime-qualification

Mirrors the platform's existing discipline (deterministic tables ship; anything
that could emit a dose does not ship without qualification).

### 4a. SAFE TO IMPLEMENT NOW (deterministic, cited, non-predictive)
- **L1 — Cited-constant layer.** Store the AUC 20–30 mg·h/L target
  (Beumer 2019) and the toxicity thresholds as **pinned, cited constants**,
  exactly like `DPYD_CLINICAL_ACTIONS`. Named provenance, `needs_audit`
  until verified against the guideline PDF.
- **L2 — Registry / provenance layer.** This document itself: a machine-readable
  manifest of (model, structure, artifact type, license, access, citation).
  Pure metadata; no computation.
- **L3 — AUC classification (post-hoc, measured input only).** Given a
  *user-supplied, measured* AUC, deterministically bin it under/within/over the
  cited window and emit a closed enum (`UNDER_EXPOSED` / `ON_TARGET` /
  `OVER_EXPOSED` / `INDETERMINATE`). This reports a measurement against a cited
  range — it does **not** predict exposure or recommend a dose.
- **L4 — GPLv2 PBPK re-execution as a research artifact (M3).** Running the
  Marok `.pksim5` models in PK-Sim to *reproduce published figures* is safe and
  license-clean (GPLv2), analogous to the StarPhase/GeT-RM benchmark harness in
  the research repo. Output labelled research/benchmark, never clinical.

### 4b. REQUIRES RUNTIME QUALIFICATION (never ship un-gated)
- **Q1 — Any AUC *prediction* from covariates (a-priori dosing).** M1/M2 predict
  exposure from BSA/LBM/sex/age. Predicting an individual's AUC and, worse,
  back-calculating a dose is a clinical act. Requires: external validation on an
  independent (ideally South-Asian) cohort, prospective qualification, and a
  regulatory pathway. M1's own authors label the Shiny app **research-use-only**
  precisely for the "unclear regulatory pathway of MIPD applications."
- **Q2 — Bayesian MIPD dose adjustment (mapbayr/mrgsolve loop).** Concentration
  → individual estimate → new-dose recommendation. Highest-risk layer.
- **Q3 — Myelotoxicity prediction (M5 Friberg PK-PD).** Predicting WBC nadir /
  Tnadir to gate the next cycle is a clinical prediction; n=30 single-center,
  no external validation.
- **Q4 — Limited-sampling AUC estimation (M1/M8/M9).** An LSS *is* a dose-
  individualization instrument; its errors propagate into Q1/Q2.
- **Q5 — Cross-population extrapolation.** Every model here is EUR/NL-centric
  (M9 India, M10 Japan excepted). Applying EUR-derived Vmax/CL to a South-Asian
  patient without population qualification is exactly the confident-wrong-answer
  failure mode the platform's bias detectors exist to catch. Emit a named
  refusal (`UNSUPPORTED_EXTRAPOLATION`) rather than a number.

---

## 5. Refusal contract (what this engine will NOT do)

The engine must **refuse, with a named rule, to output a clinical 5-FU dose,
predicted AUC, predicted toxicity, or dose adjustment**, regardless of how the
request is framed, until the Q-layers are qualified. Permitted outputs:
- cited constants and the registry (L1/L2),
- classification of a *measured* AUC against a cited window (L3),
- reproduction of published research figures from GPLv2 models (L4).

Named refusals to reuse: `UNSUPPORTED_EXTRAPOLATION` (population),
`INSUFFICIENT_QUALIFICATION` (Q-layers), `MEASURED_INPUT_REQUIRED` (L3 with no
observed concentration). This is the same "the LLM explains, deterministic
rules decide, every refusal is named" invariant the DPYD tier already holds.

---

## 6. Immediate reproducible next steps (no clinical claim)
1. Encode **L1** as a pinned `FLUOROURACIL_EXPOSURE_TARGETS_v2026.json`
   (Beumer 2019 window + citations, `audit_status: needs_audit`).
2. Land **L2** as a committed machine-readable copy of §2.
3. Add **L3** as a deterministic post-hoc classifier (measured AUC → closed enum),
   with a refusal when no measured value is supplied.
4. (Research repo only) clone M3 GPLv2 `.pksim5`, reproduce a published figure,
   score as a benchmark — the exposure analogue of the CYP2D6/StarPhase harness.

## 7. Provenance / citations
- Beumer et al. 2019, *Clin Pharmacol Ther* 105:598 (PMID 30618436) — TDM guideline / AUC window.
- Tan et al. 2026, *Clin Pharmacokinet* 65:1027, DOI 10.1007/s40262-026-01645-1 — M1 (CC BY-NC 4.0).
- Briki et al. 2026, *Cancer Chemother Pharmacol* 96:63, DOI 10.1007/s00280-026-04885-x — M2.
- Marok et al. 2024, *Clin Pharmacol Ther* 115:1282, DOI 10.1002/cpt.3181 — M3 (GitHub, GPLv2).
- Arshad et al. 2020, *Cancer Chemother Pharmacol* 85:711 (PMID 32152679) — M5 (CC BY 4.0).
- Kaldate et al. 2012, *Oncologist* 17:296 (PMID 22382460) — M6.
- Gamelin et al. 2008 (PMID 18445839) / 1999 (PMID 10561167) — M7.
- van Kuilenburg et al. 2012, *Clin Pharmacokinet* 51:163 — M8.
- Jacob et al. 2021, *Br J Clin Pharmacol* 87:937 (PMID 32592630) — M9 (India).
- Tamura et al. 2011, *Int J Med Sci* 8:406 — M10 (Japan).
- Bressolle 1999 / Terret 2000 / Mueller 2013 / Woloch 2012 / Etienne 1998 — M11.
- NICE My5-FU DAR, NBK326900 — M12.
