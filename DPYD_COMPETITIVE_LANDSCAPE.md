# DPYD Landscape — Ongoing Research, Existing Tools & Competitive Position

> Generated: 2026-06-06 | Research scan for partnership preparation

---

## 1. Existing Tools & Platforms (Competitors)

### PharmCAT (ClinPGx / PharmGKB / Stanford)
- **What:** Open-source bioinformatics tool that extracts variants from VCF, infers haplotypes/diplotypes, maps to CPIC/DPWG recommendations
- **Strengths:** Gold-standard academic tool, used by most research groups, handles complex star-allele calling
- **Weaknesses for our use case:**
  - No population-aware refusal logic — assigns phenotype uniformly regardless of ancestry
  - No SAS-specific variant handling (no *9A refusal)
  - Command-line tool, not a clinical workflow platform
  - No evidence density reporting
  - No real-time cohort simulation
  - No audit trail with named rule IDs
- **URL:** https://pharmcat.org / https://pharmcat.clinpgx.org
- **Our edge:** PharmCAT calls *9A "Normal function" for everyone. We refuse for SAS with a named rule.

### CPIC/PharmGKB Clinical Annotations
- **What:** Reference database of gene-drug-phenotype relationships with prescribing recommendations
- **Strengths:** The canonical source; every tool including ours is built on top of CPIC
- **Weakness:** It's a database, not a decision support system. No execution engine, no population context.
- **Our edge:** We operationalize CPIC AND add population-aware overrides where CPIC is silent.

### Commercial DPD Testing Platforms
| Platform | Geography | What They Do | What They Don't Do |
|----------|-----------|--------------|-------------------|
| **Myriad (MyChoice CDx)** | US | Panel testing, reports phenotype | No population-aware refusal, no SAS variants |
| **LaCar MDx (DPYD-Seq)** | US/EU | Full DPYD gene sequencing | Lab-only, no CDS platform, no population logic |
| **ARUP Laboratories** | US | Clinical DPYD genotyping (4-variant) | Standard EU panel only |
| **Invitae** | US | Multi-gene panel including DPYD | Consumer genomics, not oncology workflow |
| **SOPHiA Genetics** | EU | Bioinformatics for labs | Lab infrastructure, not prescribing CDS |
| **Color Health** | US | Pre-emptive PGx panels | Consumer-facing, limited to EU variants |

**Key gap in ALL existing commercial tools:** None offer population-specific clinical decision support. They all use the European 4-variant panel uniformly.

### Recent Commercial Entry (June 2025)
**PR Newswire (June 2025):** A company launched "DPYD Safety" tools to "identify patients who harbor DPYD variants, streamline test-ordering workflow, and deliver actionable reports at point of care." — Still limited to the standard panel, no population-aware logic.

---

## 2. Ongoing Research & Trials (Active in 2024-2026)

### PACIFIC-PGx Trial (Multicenter, 2024)
- **Title:** "Pharmacogenetic-guided dosing for fluoropyrimidine (DPYD) and irinotecan (UGT1A1*28) chemotherapies"
- **PMC:** PMC11606843
- **Design:** Multi-gene PGx-guided dosing in real patients
- **Significance:** Validates the DPYD + UGT1A1 combination panel — exactly our roadmap (next gene to add)
- **Result:** Feasibility demonstrated; combined panel is the future of oncology PGx

### IMPACT-GI Trial (Georgetown/Stanford, 2024-2025)
- **Title:** "Implementing Pharmacogenetic Testing in Gastrointestinal Cancers"
- **PMID:** 40773711
- **Design:** Prospective, nonrandomized implementation trial; 288 patients genotyped for DPYD + UGT1A1
- **Result (ASCO 2024):** 8 of 11 DPYD variant carriers received fluoropyrimidines with dose adjustment
- **Significance:** Pragmatic implementation evidence — this is the model for what we propose to MCC

### Canada Provincial Implementation (2025)
- **PMID:** 40912527
- **What:** First Canadian province-wide DPYD testing program
- **Outcome:** Real-world clinical implementation data with outcome evaluation

### British Columbia Implementation (2023)
- **Frontiers in Pharmacology:** Full DPYD-guided dosing protocol deployed province-wide
- **Key data:** Dose table for capecitabine and 5-FU based on activity score; guideline concordance tracked

### Switzerland Implementation (2022)
- **PMID:** 35662713
- **Design:** Clinical implementation to prevent early-onset fluoropyrimidine toxicity
- **Key finding:** Testing uptake increased from 0% to >90% after institutional commitment

### Italy Uptake Study (2025)
- **PMID:** 40905546
- **Key finding:** DPYD + UGT1A1 testing adoption rose from **0% in 2019 to 97% in 2023** in Italian oncology
- **Significance:** Shows how fast adoption happens once institutional commitment is made

### D-TORCH Study (India, 2026!)
- **Frontiers in Pharmacology 2026:** "DPYD genotyping in patients receiving capecitabine: an exploratory analysis from the D-TORCH study"
- **Significance:** This is an active Indian study on DPYD + capecitabine — directly relevant to MCC partnership

---

## 3. South Asian / Indian-Specific DPYD Research

### Varma et al. 2020 (JIPMER, Puducherry) — THE KEY PAPER
- **Title:** "Genetic influence of DPYD*9A polymorphism on plasma levels of 5-fluorouracil and subsequent toxicity after oral administration of capecitabine in colorectal cancer patients of South Indian origin"
- **PMID:** 32966231
- **Institution:** JIPMER (Jawaharlal Institute of Postgraduate Medical Education & Research), Puducherry
- **Key findings:**
  - DPYD*9A carriers had significantly different 5-FU plasma levels
  - *9A polymorphism is responsible for **Grade 3/4 toxicities** in South Indians
  - Mean 5-FU levels: 267 ng/mL ± 29 at 2h, 124 ng/mL ± 22 at 3h
  - **This is the paper that validates our U4 rule**

### Varma et al. 2019 (Annals of Oncology / JIPMER)
- **Title:** "Influence of DPYD*9A, DPYD*6 and GSTP1 ile105val genetic polymorphisms on capecitabine and oxaliplatin (CAPOX) associated toxicities in CRC patients"
- **PMID:** 31653159
- **Key findings:**
  - DPYD*9A carriers at **higher risk for HFS, diarrhea, and thrombocytopenia**
  - Compared to patients with wild-type allele
  - Direct clinical evidence from Indian oncology cohort

### Hariprakash et al. 2018 (Genome-scale landscape)
- **PMID:** 29239269
- **Title:** "Pharmacogenetic landscape of DPYD variants in South Asian populations by integration of genome-scale data"
- **Key findings:**
  - n>3,000 South Asian genomes analyzed
  - rs2297595 (M166V) enriched in South Asia
  - European 4-variant panel underdetects carriers in South Asians
  - Additional clinically relevant variants described

### Medscape 2025 Clinical Review
- **Finding:** "Despite previous reports, the most prevalent variation in patients with severe adverse events was DPYD*9A" — confirming *9A is clinically significant in non-European populations

### DPYD in Non-Europeans (2024, PMID:38886557)
- **Title:** "DPYD genetic polymorphisms in non-European patients with severe fluoropyrimidine-related toxicity"
- **Key finding:** The 4 common European DPYD variants are also present in South Asian, East Asian and Middle Eastern patients, BUT additional variants are missed by the standard panel

---

## 4. Regulatory Trajectory (Where This Is Headed)

| Year | Event | Implication |
|------|-------|-------------|
| 2017 | CPIC guideline published | Foundation for clinical use |
| 2018 | Henricks prospective trial (n=1,103) | Safety proof |
| 2018 | CPIC Nov update: all IMs get 50% | Simplified dosing |
| 2020 | **EMA mandate** | EU standard of care |
| 2020 | **NHS England national rollout** | Population-scale precedent |
| 2022 | Switzerland implementation | Another country adopts |
| 2023 | British Columbia province-wide | North America moves |
| 2024 | AMP joint consensus on which variants to test | Standardization |
| 2024 | NCCN acknowledges feasibility | US warming up |
| 2025 | **FDA label update** ("consider testing") | US tipping point |
| 2025 | Italy 0%→97% adoption in 4 years | Shows adoption speed |
| 2025 | Canada first provincial program | Another jurisdiction |
| 2025 | ASCO cost-effectiveness data | Economic argument settled |
| 2026 | **India — ZERO policy** | ← **FIRST-MOVER OPPORTUNITY** |

**The trajectory is clear:** Every major jurisdiction is adopting DPYD testing. India will follow. The question is who establishes the Indian evidence base.

---

## 5. What No Existing Tool Does (Our Whitespace)

| Capability | PharmCAT | Commercial Labs | Generic CDS | **Anukriti** |
|-----------|----------|----------------|-------------|-------------|
| CPIC diplotype → phenotype | ✅ | ✅ | ✅ | ✅ |
| Activity score calculation | ✅ | ✅ | Some | ✅ |
| Dose recommendation | Via CPIC | Report PDF | Some | ✅ |
| Population-specific frequency data | ❌ | ❌ | ❌ | ✅ (gnomAD v4.0) |
| SAS-specific variant refusal (*9A) | ❌ | ❌ | ❌ | **✅ Rule U4** |
| Named refusal with rule ID | ❌ | ❌ | ❌ | **✅** |
| Evidence density per population | ❌ | ❌ | ❌ | **✅** |
| Cohort-level simulation | ❌ | ❌ | ❌ | **✅** |
| Lab PCR ingestion API | ❌ | Proprietary | ❌ | **✅** |
| Audit trail (every claim cites PMID) | ❌ | ❌ | ❌ | **✅** |
| Refuses when evidence thin | ❌ | ❌ | ❌ | **✅** |
| Multi-population comparison | ❌ | ❌ | ❌ | **✅** |
| Open/auditable (not black-box) | ✅ | ❌ | ❌ | **✅** |

---

## 6. Research Gaps We Can Fill (Publication Opportunities)

1. **"Population-aware DPYD testing in South Indian oncology"** — Run MCC cohort through our engine. If *9A carriers show toxicity that standard panel missed → publication.

2. **"DPYD*9A functional characterization in South Asian colorectal cancer"** — Pair genotype data with toxicity outcomes. Varma 2020 started this; MCC cohort validates it at scale.

3. **"Cost-effectiveness of expanded DPYD panel in Indian oncology"** — ASCO 2025 showed $36.98/patient savings with EU panel. Indian expanded panel (adding *9A) may show even more savings given 27% carrier rate.

4. **"Comparison of standard vs population-aware DPYD screening protocols"** — Head-to-head: 4-variant EU panel vs 6-variant India-adapted panel. How many carriers does each catch?

5. **"Evidence-governed clinical decision support for fluoropyrimidine prescribing"** — The platform paper describing the architecture (deterministic + named refusals + population-aware).

---

## 7. Key Insight: The Market is Moving Fast

- Italy went from 0% to 97% DPYD testing in 4 years
- The D-TORCH study (2026) shows India is already researching this
- FDA 2025 label update will cascade globally
- **If MCC implements NOW with a population-aware panel, they are:**
  - First in India with published implementation outcomes
  - First globally with SAS-specific expanded panel validation
  - Positioned for the inevitable Indian regulatory adoption
  - Co-authors on a high-impact pharmacogenomics paper

The window is open but closing. Once ICMR or CDSCO issues guidance (which they will, following EMA/FDA), every institute will scramble. First-mover has the data.
