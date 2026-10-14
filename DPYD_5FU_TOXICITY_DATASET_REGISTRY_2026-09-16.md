# International 5-FU / capecitabine / fluoropyrimidine toxicity dataset registry

> **Compiled:** 16 September 2026
> **Scope:** international human datasets tying DPYD genotype and/or DPD phenotype,
> dose/regimen, and fluoropyrimidine (5-FU / capecitabine / tegafur) toxicity
> (CTCAE-graded) to outcomes — cataloged for model **training** vs **external
> validation** suitability.
> **Safety boundary:** research provenance artifact. This is a data-availability
> registry, **not** a validated clinical toxicity predictor. Every availability
> claim below is tied to a cited source; where a repository accession or an
> open-access individual-patient-data (IPD) file could **not** be confirmed from
> the sources examined, that is stated as a **named refusal** (`AVAIL_UNCONFIRMED`),
> not asserted as "available."
> **Companions:** `research/synthetic-patients/EVIDENCE_REGISTER.md` (simulator /
> PBPK / functional-assay sources), `5FU_DPYD_ENGINE_CURRENT_STATE_AND_WORLDWIDE_LANDSCAPE_2026-09-13.md`
> (why the current engine is category-A starting-dose support, not category-C risk prediction),
> `DPYD_ONCOLOGY_DEEP_DIVE.md`.

---

## 0. How to read the availability column

| Status | Meaning |
|---|---|
| `OPEN_SUMMARY` | Aggregate/summary data (tables, ORs, counts) in the paper or its open supplement; **not** patient-level. |
| `OPEN_SUPPLEMENT` | Patient-level or variant-level data downloadable from the open-access supplement. |
| `REQUEST_CONSORTIUM` | Trial IPD held by a cooperative group / sponsor; obtainable only via a formal data-sharing request or platform (Vivli / CSDR / NCTN / EGA / dbGaP). |
| `AUTHOR_ONLY` | No repository; data "available on request to corresponding author" per the paper. |
| `AVAIL_UNCONFIRMED` | **Named refusal.** A dataset/trial exists and is cited, but no open file, accession, or documented request route was confirmed from sources examined this pass. |

**Discipline (matches the platform invariant):** a documented request route is
not an obtained dataset; an existing trial is not an available dataset. Do not
promote any row to "usable" without executing the retrieval/DUA step named in
§4.

---

## 1. Registry — meta-analyses and pooled IPD

| ID | Dataset / study | Trial/accession IDs | Repository / availability | Population / country | N (patients) | Variables / endpoint | Train vs validate | Evidence |
|---|---|---|---|---|---|---|---|---|
| **FUSAFE** | FUSAFE IPD meta-analysis (GPCO-UNICANCER / RNPGx) | — (IPD-MA of ≥25 studies; 15 with complete data) | `REQUEST_CONSORTIUM` — IPD held by contributing studies; pooled set not deposited as one open file. Published model is `OPEN_SUMMARY`. | Caucasian (no DPD-based dose adjustment at enrolment); multi-cohort European/N.American | **8,733** analyzed (15 studies); 641 G4–5 events (12-wk prevalence 7.3%) | DPYD *2A / D949V / *13 / HapB3 (EMA panel); clinical covariates age, sex, BMI, FP-administration schedule, concomitant anticancer drug; endpoint **grade 4–5 toxicity ≤12 wk** | **Validation anchor** (external) + published clinical+genetic model (see §3) | Meta-Analysis: White et al., FUSAFE, *Br J Cancer* 2024, PMC10912560 / PMID 38225422; protocol PDF (gustaveroussy.fr) |
| **Meulendijks-IPD-2015** | HapB3 / c.1679T>G / c.1601G>A IPD meta-analysis | — | `OPEN_SUMMARY` (per-variant HR/OR tables) | European cohorts | ~7,365 (pooled) | 4 DPYD variants vs severe FP toxicity | Validation of variant effect sizes | Meulendijks et al., *Lancet Oncol* 2015;16:1639-50; PMID 26603945 |
| **Non-Euro-SR-2024** | DPYD in non-European patients (systematic review) | PROSPERO CRD42023385227 | `OPEN_SUPPLEMENT` (Supplementary Tables XLSX: per-variant genotype counts, 28 haplotype combinations, in-silico scores) | African American, East Asian (China/Japan/Korea/Thailand), Latin American (Chile), Middle Eastern (Jordan/Lebanon/Saudi/Tunisia), South Asian (Bangladesh/India/US); 12 countries, 5 ethnic groups | **1,313** across 32 studies | 53 DPYD variants; grade ≥3 CTCAE / WHO / DLT; narrative (no meta-analysis — too heterogeneous) | **Equity coverage map** (variant catalog for panel design); not a training matrix | Chan, Zhang, Pirmohamed, *Br J Cancer* 2024;131:498-514; PMID 38884236; DOI 10.1038/s41416-024-02754-z (Open Access) |

---

## 2. Registry — individual cohorts / trials (named targets)

| ID | Dataset / study | Trial/accession IDs | Repository / availability | Population / country | N | Variables / endpoint | Train vs validate | Evidence |
|---|---|---|---|---|---|---|---|---|
| **N0147** | NCCTG/Alliance N0147 adjuvant colon (secondary PGx analyses) | NCT00079274; NCCTG N0147 | `REQUEST_CONSORTIUM` — Alliance Data Sharing policy (allianceforclinicaltrialsinoncology.org, "15 - Data Sharing", NIH-honored requests). No open IPD file. | Stage III colon; US (predominantly European ancestry) | **2,594** with complete AE data (PGx subset) | DPYD *2A, I560S, D949V, HapB3/c.1129-5923C>G; grade ≥3 5-FU AEs | **External validation** (adjuvant FOLFOX) | Lee et al., *JNCI* 2014;106:dju298 (open PDF academic.oup.com); PMID 25381393; HapB3 sub-analysis Lee 2016 JPharmacogenetics |
| **PETACC-8** | PETACC-8 adjuvant colon (DPYD secondary analysis) | EudraCT 2005-003463-23; PETACC-8 | `REQUEST_CONSORTIUM` — sponsor/EORTC-FFCD; secondary analysis published, IPD not open. | Stage III colon; Europe (FOLFOX4 ± cetuximab) | ~1,545 genotyped subset | DPYD variants; adverse events grade ≥3–4 | **External validation** | Boige et al., *JAMA Oncol* 2016;2:655-662 (jamanetwork.com fullarticle/2482915); PMID 26794347 |
| **QUASAR2** | QUASAR2 capecitabine adjuvant CRC | ISRCTN45133151 | `REQUEST_CONSORTIUM` for IPD; per-cycle CTCAE + genotype **re-used** in a 2021 GWAS (930 patients). GWAS summary `OPEN_SUMMARY` (conference). | Adjuvant CRC; UK-led | **930** genotyped (of 1,952 trial) | DPYD, TYMS, ENOSF1; **per-cycle CTCAE**, ≥grade 3 in first 2 cycles (early-onset) | **Train + validate** (per-cycle granularity; capecitabine) | Rosmarin et al., *J Clin Oncol* 2014;32:1031-9; PMID 24590654 / PMC4879695; GWAS 1768P Ann Oncol 2021 |
| **CAIRO2** | CAIRO2 advanced CRC (DPYD/capecitabine PGx: Deenen 2011) | NCT00208546; CAIRO2 (DCCG) | `REQUEST_CONSORTIUM` (DCCG). PGx analysis published; IPD not open. | Advanced CRC; Netherlands (capecitabine + oxaliplatin ± bevacizumab ± cetuximab) | 568 (Deenen 2011 PGx set) | DPYD SNPs/haplotypes incl. c.1236G>A/HapB3; capecitabine toxicity + efficacy | **External validation** (metastatic, capecitabine) | Deenen et al., *Clin Cancer Res* 2011;17:3455-68; PMID 21498394 |
| **Deenen-2016** | Prospective upfront DPYD*2A-guided dosing (safety/cost) | NCT00838370 | `AUTHOR_ONLY` / `REQUEST_CONSORTIUM` | Netherlands, multi-center | 2,038 screened; 22 *2A carriers dose-reduced | *2A only; ~50% dose reduction; grade ≥3 toxicity, cost | **Validation** of *2A → 50% dose safety | Deenen et al., *J Clin Oncol* 2016;34:227-34; PMID 26573078 |
| **Henricks-2018** | Prospective 4-variant DPYD-guided dosing (safety) | NCT02324452 (Alpe2 / prospective) | `AUTHOR_ONLY` | Netherlands, 17 hospitals | **1,103** enrolled; 85 heterozygous carriers | *2A, c.2846A>T, c.1679T>G, c.1236G>A; genotype-guided dose; grade ≥3 toxicity vs historical | **Validation** of 4-variant dosing algorithm | Henricks et al., *Lancet Oncol* 2018;19:1459-67; PMID 30348537 (open dspace.library.uu.nl) |
| **Rosmarin-QUASAR2-model** | see QUASAR2 (same trial, model form in §3) | ISRCTN45133151 | as QUASAR2 | UK | 927 (model cohort) | DPYD + TYMS 5'VNTR + clinical → capecitabine toxicity | model coefficients in paper | as QUASAR2 |

---

## 3. Registry — smaller / candidate-gene cohorts with usable structure

| ID | Dataset / study | Availability | Population / country | N | Variables / endpoint | Note |
|---|---|---|---|---|---|---|
| **Loganayagam-2013** | `OPEN_SUPPLEMENT` (BJC XLS) | UK (South-East London) | **430** (186 5-FU, 244 capecitabine; 85% CRC) | DPYD (9 variants), DPYS, TYMS 5'/3'-UTR, MTHFR, CDA; age, sex, ethnicity, GFR; **CTCAE v3 grade 3-4** (first 4 cycles), hand-foot syndrome | Best small **open-supplement training** cohort; has published logistic-regression AUC and PPV/specificity tables. See §3-eq. |
| **Schwab-2008** | `OPEN_SUMMARY` | Germany (German 5-FU Toxicity Study Group) | 683 | DPYD, TYMS, MTHFR, clinical, schedule; grade 3-4 | Classic prospective; effect sizes only |
| **Froehlich/Amstutz-2015** | `OPEN_SUMMARY` | Switzerland | 500+ | DPYD risk variants; early-onset toxicity | Swiss early-onset cohort |
| **Kanai-2023** | `OPEN_SUMMARY` | Japan (Asian) | 1, (large adjuvant cohort) | DPYD genotype vs FP toxicity — **null/poor association** in Asians | Critical **negative control**: European panel underperforms in East Asians (PMID 36524458) |
| **Nahid-2018** | `OPEN_SUMMARY` | Bangladesh | (cohort) | DPYD*2A, MTHFR C677T; grade 3-4 anaemia/neutropenia/diarrhoea (ORs 4.7–10.1) | South Asian toxicity ORs (PMID 29383650) |
| **Hariprakash-2018** | `OPEN_SUMMARY` | India (South Asian genome-scale) | integrative | DPYD variant landscape, MAFs | South Asian frequency reference (PMID 29239269) |
| **D-TORCH** | `OPEN_SUMMARY` | India (exploratory) | (cohort) | DPYD genotyping in capecitabine; grade 2 toxicity split | India prospective exploratory (Front Pharmacol 2026) |
| **South-India-single-center** | `OPEN_SUMMARY` (ASCO abstract) | India (South) | single-center | DPD deficiency in 5-FU/capecitabine | JCO 2021 e15517 |

---

## 4. Repositories checked — where NCTN/EORTC/industry IPD actually lives

| Repository | Relevance | Status for these datasets |
|---|---|---|
| **NCTN / NCI Data Archive + Alliance policy** | N0147 and US cooperative-group trials | Formal request; `REQUEST_CONSORTIUM`. Policy doc cited. |
| **Vivli** | industry-sponsored capecitabine (Xeloda/Roche) trials | Candidate route for sponsor trials; **`AVAIL_UNCONFIRMED`** — specific DPYD-annotated capecitabine trial listings not verified this pass. |
| **CSDR (ClinicalStudyDataRequest)** | Roche/other sponsor trials | Same as Vivli; `AVAIL_UNCONFIRMED`. |
| **EGA / dbGaP** | germline genotype + phenotype (controlled access) | No confirmed 5-FU-toxicity DPYD accession located this pass → **`AVAIL_UNCONFIRMED`**. (Contrast: EGA does host the Himalayan/Bhutan panel EGAD00001011358 — genome, not toxicity — per EVIDENCE_REGISTER G08.) |
| **GEO** | expression, not germline-toxicity IPD | Not the right shape; excluded. |
| **Zenodo / Dryad** | author-deposited supplements | Loganayagam-2013 and Non-Euro-SR-2024 supplements are on publisher servers, not Zenodo/Dryad; no Dryad DOI confirmed. |
| **UK Biobank** | large biobank | **Explicit gap** (Non-Euro-SR-2024): secondary-care severe FP-toxicity outcomes are **not** available in UKB. Do not assume UKB solves the toxicity-label problem. |

**Retrieval tasks (Phase-0, not assumed done):** (1) submit Alliance request for
N0147 PGx IPD; (2) search Vivli/CSDR by ISRCTN45133151 (QUASAR2) and Roche
capecitabine trial IDs and record the actual listing status; (3) download and
reconcile the Loganayagam-2013 XLS and Non-Euro-SR-2024 XLSX supplements into a
provenance-stamped local extraction (mirrors the `offer_2014_dpyd_functional.csv`
reconciliation task already logged in EVIDENCE_REGISTER F01).

---

## 5. Implementable equations (with named limits)

These are transcribed from published models. They are **research prognostic
models**, not the deterministic CPIC starting-action rule the engine ships, and
**must not** be surfaced as a patient-specific clinical prediction (category C)
without prospective validation. Each is provenance-stamped.

### 5.1 FUSAFE clinical + genetic risk (grade 4–5 ≤12 wk)

Logistic form (structure per FUSAFE, PMID 38225422). Linear predictor:

```
logit(P_G45) = β0
             + β_age·age
             + β_sex·sex            # coded per source
             + β_bmi·BMI
             + β_sched·schedule     # FP-administration schedule
             + β_conc·concomitant   # concomitant anticancer drug
             + β_DPYD·DPYD_status    # ≥1 EMA variant (*2A / D949V / *13 / HapB3)
P_G45 = 1 / (1 + exp(-logit))
```

**Named limits:** exact β coefficients are in the FUSAFE publication/supplement —
`COEFF_UNCONFIRMED` here; retrieve before any implementation. Derived in
**Caucasian, no-dose-adjustment** cohorts; **do not** extrapolate to South Asian
/ East Asian populations (Kanai-2023 shows the European variant panel associates
poorly in Asians). 12-week event prevalence 7.3% is the baseline these odds sit on.

### 5.2 Loganayagam-2013 combined model (open supplement)

AUC benchmarks from the paper (directly usable as a validation target, not a
plug-in equation without the supplement coefficients):

```
AUC(clinical only: sex, age, GFR, ancestry)                 = 0.72
AUC(+ rare DPYD variants + TYMS 5'-UTR USF sites + 3'-UTR)  = 0.74   # all patients
AUC(capecitabine subgroup, + CDA c.-92A>G)                  = 0.75
```

Deterministic rule extractable from the same paper (four rare DPYD variants
c.1905+1G>A, c.1601G>A, c.1679T>G, c.2846A>T, heterozygous/compound-het):

```
if carrier(any of {c.1905+1G>A, c.1601G>A, c.1679T>G, c.2846A>T}):
    predict grade 3-4 toxicity
# Reported combined PPV > 99%, specificity 100%, NPV 80% (n=430; all 24 carriers had G3-4)
```

**Named limits:** PPV/specificity from a single 430-patient UK cohort with only
6% carriers; specificity 100% is small-sample. Effect sizes for individual
capecitabine markers: TYMS 3'-UTR del/del OR 3.08 (1.38–6.87); MTHFR 1298CC →
hand-foot syndrome OR 9.99 (3.84–27.8); CDA c.-92A>G / c.-451C>T → grade 2-4
diarrhoea OR 2.3 (1.3–4.2) each. The authors themselves judged TYMS/MTHFR/CDA
markers **not** clinically useful in isolation (low PPV) — preserve that caveat.

### 5.3 Rosmarin/QUASAR2 capecitabine model

Structure: DPYD variants + TYMS 5'-VNTR + clinical → early per-cycle ≥grade 3
capecitabine toxicity (coefficients in paper; `COEFF_UNCONFIRMED` here). Its
per-cycle CTCAE structure is the reason QUASAR2 is tagged **train+validate**.

### 5.4 What NOT to build an equation from

- CPIC activity-score → phenotype bins and the `AVOID / REDUCE_50PCT / STANDARD`
  action are a **deterministic pinned table**, not a fitted risk equation. They
  already ship in `anukriti-pgx-core` (`DPYD_CLINICAL_ACTIONS_v2024.01.json`).
  Do not re-derive them as a regression.
- Uracil / DHU-ratio phenotype thresholds are exposure surrogates, not toxicity
  probabilities (see EVIDENCE_REGISTER V03–V05).

---

## 6. Suitability summary (train vs external validation)

| Use | Best-fit rows | Why |
|---|---|---|
| **Train** a multivariable toxicity model | Loganayagam-2013 (open supplement, has covariates + CTCAE), QUASAR2 (per-cycle, if IPD obtained) | Patient/variant-level data with clinical covariates and CTCAE endpoints |
| **External validation** (adjuvant colon) | N0147, PETACC-8 | Large, independent, grade ≥3 AE, European-ancestry adjuvant FOLFOX |
| **External validation** (capecitabine / metastatic) | CAIRO2, QUASAR2 | Capecitabine-specific toxicity |
| **Prospective dosing-algorithm anchor** | Deenen-2016, Henricks-2018 | Establish that genotype-guided 50% reduction is safe (not a risk model) |
| **Equity / non-European coverage** | Non-Euro-SR-2024, Kanai-2023 (negative), Nahid-2018, Hariprakash-2018, D-TORCH | Panel-coverage gaps; South/East Asian toxicity ORs and null-association warning |
| **Do not use as toxicity labels** | UK Biobank | Severe FP-toxicity secondary-care outcomes absent |

---

## 7. Refusals recorded (do not silently upgrade)

- `AVAIL_UNCONFIRMED`: no open EGA/dbGaP/GEO accession for a DPYD×5-FU-toxicity
  IPD set was confirmed this pass.
- `AVAIL_UNCONFIRMED`: Vivli/CSDR listing status for QUASAR2 (ISRCTN45133151) and
  Roche capecitabine trials not verified.
- `COEFF_UNCONFIRMED`: FUSAFE and Rosmarin/QUASAR2 model coefficients not
  transcribed (publication/supplement retrieval required before implementation).
- NCBI PMC/PubMed full text was gated by anti-bot interstitials for several
  sources; open-access mirrors (Nature BJC, dspace.library.uu.nl, academic.oup.com,
  jamanetwork.com) and PubMed records were used at the depth stated. Sample sizes
  drawn from abstracts/snippets are marked and should be confirmed against full
  text before publication.
