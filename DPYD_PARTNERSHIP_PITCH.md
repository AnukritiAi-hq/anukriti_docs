# DPYD Pre-Treatment Testing — Evidence & Anukriti Implementation

> Prepared for: Cancer Research Institute Partnership Meeting
> Date: June 2026
> Status: Engine validated, deployed, live at product.anukritiai.com

---

## 1. The Problem — Numbers That Matter

| Metric | Value | Source |
|--------|-------|--------|
| Patients receiving fluoropyrimidines globally/year | >2,000,000 | Ho 2025 (PMID:39887719) |
| Severe toxicity (Grade 3+) in unscreened DPD-deficient patients | **70–80%** | CPIC 2017, Henricks 2018 |
| Treatment-related mortality in unscreened carriers | **1–2%** | CPIC 2017 (PMID:29152729) |
| Population carrying heterozygous DPYD variant | **6–9%** | Ho 2025 |
| DPYD *9A carrier frequency in South Indians | **27%** | Hariprakash 2018 |
| European 4-variant panel coverage in Indians | **<0.5%** of at-risk population | gnomAD v4.0 SAS data |

**The gap:** 1 in 4 South Indian patients on capecitabine may carry *9A. European tools assign "normal function" and move on. Standard-dose toxicity follows.

---

## 2. Clinical Evidence — What Genotype-Guided Dosing Achieves

### Henricks 2018 Prospective Trial (PMID:30348537)
- **Design:** 1,103 patients, 17 Dutch hospitals, prospective DPYD genotyping
- **Result:** Severe toxicity in *2A carriers dropped from **73% → 28%** with 50% dose reduction
- **Prior study (1,631 patients):** Severe toxicity **73% → 28%** (same magnitude, independent validation)
- **Conclusion:** Routine DPYD genotyping is feasible and improves patient safety

### CPIC 2017 Guideline (PMID:29152729)
- Meta-analysis of 7,365 patients: RR for severe toxicity:
  - *2A: **2.9×**
  - c.2846A>T: **3.0×**
  - *13: **4.4×**
  - HapB3: **1.6×**
- Activity score system: AS=2 normal, AS=1/1.5 intermediate (50% reduction), AS=0/0.5 poor (avoid)

### ASCO 2025 Cost-Effectiveness (Nguyen et al., Morris et al.)
- **Per-patient savings:** US $36.98 (avoiding hospitalization for severe AEs)
- **Hospitalization reduction:** 64% → **25%** with genotype-guided dosing
- **Test cost:** ~US $175 (2023 CMS fee) → still net positive
- **Recommendation:** Make DPYD genotyping an opt-out test
- **In India:** Test costs are lower (~₹2,000–5,000), hospitalization costs are high → economics even more compelling

### Wrongful Death Precedent
- A health system settled a wrongful death lawsuit: **$1,000,000 payment** + mandatory requirement for oncologists to inform patients about DPYD testing (Ho 2025, ref 48)

---

## 3. Regulatory Landscape

| Authority | Year | Position | India |
|-----------|------|----------|-------|
| **EMA** | Apr 2020 | **Mandatory** — test before systemic fluoropyrimidines | — |
| **MHRA/NHS England** | 2020 | **National implementation** — universal DPYD testing | — |
| **FDA** | 2025 | "Consider testing for genetic variants of DPYD" (label update) | — |
| **NCCN** | 2024 | Acknowledges feasibility; no mandate yet | — |
| **India** | — | **No policy. No guideline. No mandate.** | ← OPPORTUNITY |

**The first Indian institution to implement population-aware DPYD testing with published outcomes = first-mover advantage + publication.**

---

## 4. What Anukriti Does — And How It's Different

### 4A. What our engine does (validated 7/7 vs Ho 2025 paper)

| Diplotype | Engine Output | CPIC Recommendation | Concordance |
|-----------|--------------|---------------------|-------------|
| *1/*1 | Normal Metabolizer (AS=2) | Standard dose | ✅ |
| *1/*2A | Intermediate Metabolizer (AS=1) | 50% reduction | ✅ |
| *1/HapB3 | Intermediate Metabolizer (AS=1.5) | 50% reduction (Nov 2018) | ✅ |
| *1/c.2846A>T | Intermediate Metabolizer (AS=1.5) | 50% reduction | ✅ |
| *2A/*2A | Poor Metabolizer (AS=0) | Avoid entirely | ✅ |
| *2A/*13 | Poor Metabolizer (AS=0) | Avoid entirely | ✅ |
| *2A/HapB3 | Poor Metabolizer (AS=0.5) | Avoid (or >75% reduction) | ✅ |

Works identically for **capecitabine** (the oral prodrug most Indian oncologists prescribe).

### 4B. How we IMPROVE on existing tools

| What generic tools do | What Anukriti does differently |
|-----------------------|-------------------------------|
| Test 4 European variants only | Accept 4 core + 2 SAS-relevant (*9A, M166V) |
| *9A → "Normal function" (silently) | **Named refusal U4** for SAS patients citing 27% frequency |
| No population context | Real gnomAD v4.0 frequencies per population (n=15,308 SAS) |
| No audit trail | Every refusal names a rule ID, every recommendation cites PMID |
| Black-box LLM output | Deterministic engine decides; LLM only explains (GenerativeBoundary) |
| No evidence density reporting | Surfaces WHERE evidence is thin per population |

### 4C. The U4 Rule — Our Core Differentiator (Demo Slide)

**European tool path:**
```
Input:  DPYD *1/*9A, Population: South Asian
Output: Normal Metabolizer, Standard dose
        (silently assigns based on European data)
```

**Anukriti path:**
```
Input:  DPYD *1/*9A, Population: South Asian
Output: ⚠ REFUSAL — Rule U4_SAS_DPYD_OVERRIDE

"DPYD *9A assigned Normal function by CPIC (European data).
South Asian evidence (27% carrier frequency for *9A in South
Indian oncology cohorts) shows clinically significant toxicity
risk not captured by the European 4-variant panel.

Population-aware refusal applied — recommend DPD phenotyping
or expanded panel before standard-dose fluoropyrimidine."
```

**No other tool in the world does this.** The Ho 2025 paper itself says:
> "DPYD allele frequencies differ across race and ethnicity... each institution's patient population inclusive of race and ethnicity should be taken into consideration when selecting which DPYD variants to test."

We are the only implementation that operationalizes this statement.

---

## 5. What's Live in the Platform Today

| Capability | Status | How to access |
|-----------|--------|---------------|
| Fluorouracil workflow (CPIC Level A) | ✅ Live | /drugs → Fluorouracil → Simulate |
| Capecitabine workflow (same engine) | ✅ Live | /drugs → Capecitabine → Simulate |
| DPYD 6-variant detection (*2A, *13, c.1679T>G, c.2846A>T, HapB3, *9A) | ✅ Live | Backend pgx-core |
| M166V (rs2297595) detection | ✅ Live | Backend pgx-core |
| U4 SAS population-aware refusal | ✅ Live | Swarm runtime (SAS + *9A/M166V) |
| Real gnomAD v4.0 allele frequencies (SAS n=15,308) | ✅ Live | /population/frequency API |
| PCR ingestion API (lab genotypes → engine) | ✅ Live | POST /runs/from-pcr |
| AI interpretation with citation validation | ✅ Live | /llm-context/grounded |
| Evidence level badges (CPIC Level A) | ✅ Live | Frontend results page |
| Population evidence gaps panel | ✅ Live | Frontend results page |
| Evidence-level filter (A/B/C/D) | ✅ Live | Frontend results page |
| Audit trail (every rule named, every PMID cited) | ✅ Live | Report JSON |
| Azure-deployed API | ✅ Live | anukriti-api rev 28 |

---

## 6. What We Propose to the Institute

### Phase 1 — Validation (Weeks 1–4)
- Institute provides: 50+ de-identified DPYD genotypes from CRC/breast patients + Grade 3+ toxicity outcomes
- We run them through the engine
- Concordance check: does our phenotype call correlate with who had severe toxicity?
- If *9A carriers had toxicity that CPIC "missed" (called Normal) → that's the publication finding

### Phase 2 — Expanded Panel (Weeks 4–8)
- Add any novel variants their sequencing reveals
- Validate DPD phenotyping (uracil/DHU ratio) as a complementary input
- Build institution-specific cohort dashboard

### Phase 3 — Publication + Implementation
- Co-authored paper: "Population-aware DPYD testing in South Indian oncology: a validation study"
- First Indian institution with published DPYD implementation outcomes
- Standard-of-care protocol for their fluoropyrimidine prescriptions

---

## 7. Key Citations (For Your Meeting Deck)

1. **CPIC 2017:** Amstutz U et al. Clin Pharmacol Ther 103(2):210–216. PMID:29152729
2. **Henricks 2018:** Henricks LM et al. Lancet Oncol 19:1459–1467. PMID:30348537
3. **EMA 2020:** https://www.ema.europa.eu/en/news/ema-recommendations-dpd-testing-prior-treatment-fluorouracil-capecitabine-tegafur-flucytosine
4. **Ho 2025 Implementation Guide:** Ho JJ et al. Clin Pharmacol Ther 117(5):1194. PMID:39887719
5. **FDA 2025 Label Update:** JCO 2025. https://ascopubs.org/doi/10.1200/JCO-25-02629
6. **ASCO 2025 Cost:** Nguyen et al. + Morris et al. (Atrium Health Levine Cancer Institute)
7. **AMP 2024 Variant Recommendations:** Pratt VM et al. J Mol Diagn 26:851–863. PMID:39032821
8. **Hariprakash 2018:** South Asian DPYD landscape (n>3,000). rs2297595 enrichment.
9. **Knikman 2023:** Survival with dose-individualized fluoropyrimidine. JCO 41:5411. PMID:37639651
