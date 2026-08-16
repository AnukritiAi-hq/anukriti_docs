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
| DPYD \*9A allele frequency, South Asian | **0.2550** | gnomAD v2.1.1 exomes, live query 2026-07-28 |
| DPYD \*9A allele frequency, European (NFE) | **0.2226** | gnomAD v2.1.1 exomes, live query 2026-07-28 |
| DPYD \*9A allele frequency, African (population maximum) | **0.4131** | gnomAD v2.1.1 exomes, live query 2026-07-28 |
| European 4-variant panel: SAS \*2A allele frequency | **0.0040** | gnomAD v4.1 joint, live query 2026-08-08 |

**The gap — stated precisely.** The CPIC 4-variant panel is calibrated on
European data, and its constituent alleles are genuinely rare in South Asian
populations (\*2A 0.0040, \*13 absent in SAS at gnomAD v4.1 sample sizes). A
South Asian patient screened on that panel is very likely to screen negative.
That is the real equity problem, and it does not require any allele to be
South-Asian-enriched.

> **Correction, 2026-08-16.** Earlier versions of this document claimed DPYD
> \*9A carrier frequency of **27% in South Indians** (citing Hariprakash 2018)
> and "1 in 4 South Indian patients." **We audited that claim and it does not
> hold.** The 27% figure was not present in any pinned frequency artifact, and
> real gnomAD data shows \*9A is *not* South-Asian-enriched (SAS 0.2550 vs EUR
> 0.2226, ratio 1.15; AFR 0.4131 is the maximum). For M166V the direction is
> actually inverted (SAS 0.0906 < EUR 0.1004). Full audit trail:
> `anukriti_docs/DPYD_SAS_OVERRIDE_AUDIT_2026-07-28.md`. We are disclosing this
> rather than quietly deleting it, because the audit is the product.

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
| Test 4 European variants only | Accept 4 core + 2 contested-evidence alleles (*9A, M166V) |
| *9A → "Normal function" (silently) | **Named uncertainty P1_SAS_DPYD_CONTESTED** — flags the open question, cites all three conflicting studies, does not fabricate a direction |
| No population context | Real gnomAD frequencies per population, live-queried with callset + date recorded |
| No audit trail | Every refusal names a rule ID, every recommendation cites PMID |
| Black-box LLM output | Deterministic engine decides; LLM only explains (GenerativeBoundary) |
| No evidence density reporting | Surfaces WHERE evidence is thin per population |

### 4C. The P1 Rule — Our Core Differentiator (Demo Slide)

**European tool path:**
```
Input:  DPYD *1/*9A, Population: South Asian
Output: Normal Metabolizer, Standard dose
        (silently assigns based on European data)
```

**Anukriti path:**
```
Input:  DPYD *1/*9A, Population: South Asian
Output: ⚠ NAMED UNCERTAINTY — Rule P1_SAS_DPYD_CONTESTED

"DPYD *9A is assigned Normal function by CPIC (confirmed against
CPIC's live allele API, 2026-07-28). It is NOT South-Asian-enriched:
gnomAD v2.1.1 SAS 0.2550 vs EUR 0.2226 (ratio 1.15); AFR 0.4131 is
the population maximum.

The South Asian clinical evidence is genuinely contested:
  · Hariprakash 2018 — M166V associated with hand-foot syndrome
    (OR 5.22, 95% CI 1.47-18.55, p=0.011, n=110); its *9A assay failed
  · Naushad 2021 — pooled Indian data, no association for either
    (*9A OR 1.03, p=0.95; M166V OR 1.54, p=0.32)
  · Atasilp 2025 — *9A / grade 3-4 neutropenia on n=2 homozygotes,
    not surviving its own multivariate analysis

Three studies, three incompatible answers, and no population-frequency
argument to fall back on. This is flagged as an open research question,
NOT converted into a dose recommendation in either direction."
```

**Why this is the differentiator.** The obvious demo would be a confident
population-aware refusal. We shipped exactly that — `U4_SAS_DPYD_OVERRIDE`,
justified by a hand-written "27% carrier frequency" — and it ran live for **52
days** blocking synthesis for South Asian patients before our own audit caught
that the number had no source. The citation was real; the number was not.

The corrected behaviour is the stronger product claim: a system that
distinguishes *contested* from *established* and refuses to manufacture
certainty in either direction. Any vendor can show you a confident answer.
Ask them what happens when the evidence disagrees with itself.

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
8. **Hariprakash 2018:** South Asian DPYD landscape. PMID:29239269. n=110 Indian GI-cancer patients (36 colon + 41 rectal) for the association analysis. Reports M166V / hand-foot syndrome OR 5.22 (95% CI 1.47–18.55, p=0.011); its \*9A assay failed. **Does not support a 27% \*9A carrier frequency** — see the 2026-08-16 correction in §1.
10. **Naushad 2021:** Pooled Indian DPYD data — no association for \*9A (OR 1.03, p=0.95) or M166V (OR 1.54, p=0.32). Cited as the counter-evidence in P1_SAS_DPYD_CONTESTED.
11. **Atasilp 2025:** Clin Med doi:10.1016/j.clinme.2025.100443. \*9A / grade 3–4 neutropenia on n=2 homozygotes; association did not survive multivariate analysis.
9. **Knikman 2023:** Survival with dose-individualized fluoropyrimidine. JCO 41:5411. PMID:37639651
