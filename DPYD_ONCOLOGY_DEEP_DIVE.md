# DPYD / Fluoropyrimidine Oncology — Deep Dive

> Generated: 2026-06-06 | For: Cancer Research Institute partnership positioning
> Status: Live in platform (workflow `fluorouracil_dpyd`, CPIC Level A)

---

## 1. The Clinical Problem (Why This Matters)

**Fluoropyrimidines (5-FU, capecitabine, tegafur) are the backbone of oncology:**
- Used in ~2 million cancer patients/year globally
- First-line for colorectal (FOLFOX/FOLFIRI), breast, head-and-neck, gastric cancers
- ~30% of all cancer patients will receive a fluoropyrimidine at some point

**The toxicity problem:**
- 10-30% of patients experience Grade 3+ severe toxicity
- 0.5-1% treatment-related mortality in unscreened populations
- DPD (dihydropyrimidine dehydrogenase) inactivates 80-90% of administered 5-FU
- DPYD gene variants cause partial or complete DPD deficiency
- Carriers receiving standard dose → severe myelosuppression, mucositis, hand-foot syndrome, neurotoxicity, death

**The equity angle (our differentiator):**
- The standard 4-variant European panel (rs3918290, rs55886062, rs67376798, rs56038477) was calibrated on European cohorts
- South Asian populations have additional enriched variants (rs2297595, population-specific haplotypes)
- A European-derived panel applied uniformly to Indian patients **underdetects carriers**
- This is precisely the data-access bias problem Anukriti is built to surface

---

## 2. Evidence Base — Key Papers

| Paper | Year | PMID | Key Finding | Relevance |
|-------|------|------|-------------|-----------|
| **CPIC Guideline (Amstutz et al.)** | 2017 | 29152729 | Activity score system: AS=2 NM, AS=1/1.5 IM (50% reduction), AS=0/0.5 PM (avoid) | Our canonical source — pinned in pgx-core |
| **Henricks et al. (Netherlands)** | 2018 | 30348537 | Prospective n=1,103: genotype-guided dosing reduced Grade≥3 toxicity from 73% to 28% in carriers, no increase in treatment-related death | **The pivotal safety trial** — first to prove prospective DPYD testing saves lives |
| **EMA Mandate** | Apr 2020 | — | Pre-treatment DPD testing now required in the EU for all systemic fluoropyrimidines | Regulatory precedent — India doesn't mandate yet but will follow |
| **MHRA/NHS England** | 2020 | — | Universal DPYD testing implemented nationally in UK | National-scale implementation proof |
| **PACIFIC-PGx (multicenter)** | 2024 | PMC11606843 | Multicenter trial of PGx-guided dosing for DPYD + UGT1A1 across multiple cancer types | Latest trial evidence, multi-gene |
| **ASCO 2025 cost data** | 2025 | (conference) | Pre-treatment DPYD genotyping significantly reduces hospitalizations and costs | Health-economic argument for adoption |
| **Hariprakash et al.** | 2018 | — | n>3,000 South Asian WGS: rs2297595 enriched, additional SAS-specific variants missed by EU panel | **Our equity wedge** — platform already cites this |
| **DPYD in non-Europeans (2024)** | 2024 | 38886557 | 4-variant EU panel inadequate for non-European patients with severe toxicity | Validates our population-aware approach |

---

## 3. What We Already Have (Platform Inventory)

### pgx-core (deterministic truth layer)
- `DPYDCaller` — star-allele detection from VCF rsID lookups
- 6 variants: `*1`, `*2A`, `*13`, `c.1679T>G`, `c.2846A>T`, `HapB3`
- Activity score → phenotype: NM (AS=2), IM (AS=1/1.5), PM (AS=0/0.5)
- CPIC recommendation levels pinned (Level A for DPYD/fluoropyrimidines)
- 30-sample 1000G fixture for regression testing

### anukriti-swarm (reasoning layer)
- Full CPIC guideline entries (NM/IM/PM × fluorouracil + capecitabine)
- Allele frequency data: 6 variants × 5 populations (gnomAD v4.0, n=9k-65k per pop)
- Knowledge graph seed: DPYD nodes + edges
- Evidence documents: CPIC fluoropyrimidines doc + SAS landscape paper
- Population reasoning agents produce ancestry-specific frequency context

### anukriti-api (gateway)
- `POST /runs` with `workflow=fluorouracil` — full swarm pipeline
- `POST /runs/from-pcr` — PCR-typed genotype ingestion (research-org pilot path!)
- Strand-orientation fix for DPYD variants
- `/population/frequency` returns real gnomAD frequencies for DPYD variants
- `/llm-context/grounded` produces validated explanations for fluorouracil runs

### anukriti-main (frontend)
- Fluorouracil is an **active** drug in the catalog (not preview)
- Wizard flow: Drug → Genome → Simulate → Results works end-to-end
- EvidenceBadge shows Level A
- AI Interpretation panel explains DPYD results with citation validation

---

## 4. Implementation Gaps & Opportunities

### A. Immediate wins (can demo to partner now)

| # | Feature | Status | Demo Value |
|---|---------|--------|-----------|
| 1 | Select fluorouracil → pick genome → simulate → get phenotype + recommendation | ✅ Live | Core demo path |
| 2 | Population-specific frequencies (SAS vs EUR carrier rates) | ✅ Live | Equity story |
| 3 | PCR ingestion API for lab-typed genotypes | ✅ Live | Integration story |
| 4 | Evidence level A badge + AI interpretation | ✅ Live | Trust/governance |
| 5 | Swarm evidence-sufficiency (refuses when evidence thin) | ✅ Live | Safety contract |

### B. High-value additions for the partnership

| # | Feature | Effort | Value for CRI |
|---|---------|--------|---------------|
| 1 | **Capecitabine as a separate drug card** | Low (1hr) | Capecitabine is the oral prodrug most Indian oncologists use; same DPYD engine, just needs a second drug entry in the catalog |
| 2 | **South Asian expanded panel** | Medium (1-2 days) | Add rs2297595 + population-specific variants beyond the EU 4-panel; cite Hariprakash. This is THE differentiator vs generic tools |
| 3 | **Phenotyping (DPD enzyme activity) integration** | Medium | Accept uracil/DHU ratio input alongside genotype; CPIC recommends this as gold-standard backstop |
| 4 | **Dose calculator** | Low-Med | Given phenotype + body surface area → recommended starting dose (50% for IM, <25% for PM, standard for NM) |
| 5 | **Toxicity risk score** | Medium | Composite score combining genotype + phenotype + clinical risk factors (age, renal function, prior toxicity) |
| 6 | **Real cohort demo** | Low | Pre-load 50-100 synthetic Indian CRC cohort with realistic DPYD genotype distribution to show population-level impact |
| 7 | **FHIR report export** | Already exists | Clinical report in FHIR R4 format for EMR integration |
| 8 | **Multi-gene oncology panel (DPYD + UGT1A1)** | Medium-High | UGT1A1*28 for irinotecan (FOLFIRI) — same patients, same pipeline. PACIFIC-PGx 2024 validates this combo |

### C. What NOT to build (out of scope for research platform)

- Clinical decision support certification (we're RUO — Research Use Only)
- Diagnostic claims or regulatory submissions
- Patient-facing reports (researcher + protocol-designer facing only)

---

## 5. Partnership Pitch Points — Cancer Research Institute

**What we bring to the table:**

1. **Population-aware infrastructure** — unlike generic PGx tools that apply European panels uniformly, we surface WHERE the evidence is thin and refuse to extrapolate
2. **South Asian DPYD coverage** — we already have the Hariprakash landscape paper wired in, gnomAD SAS frequencies, and the platform explicitly flags when the EU 4-panel may underdetect
3. **Pre-treatment screening simulation** — oncology teams can simulate what DPYD screening would look like across their patient cohort before implementing the program
4. **Deterministic + auditable** — every recommendation cites a rule ID, every refusal is named, the audit trail is downloadable. This matters for research ethics committees
5. **PCR ingestion API** — their lab already has DPYD genotyping data (TaqMan/KASP/Sanger); they can pipe it directly into our platform without re-doing anything
6. **Cost-effectiveness modeling** — ASCO 2025 data shows pre-treatment DPYD testing saves money. We can help them build their institutional business case with population-specific numbers

**What we get:**

- Real-world validation cohort (Indian CRC patients with DPYD genotypes + toxicity outcomes)
- South Asian variant discovery (novel variants their sequencing reveals)
- Clinical credibility for the platform
- Co-authored publication potential
- First signed research partnership

---

## 6. Recommended Demo Flow (for institute meeting)

```
1. /drugs → Select "Fluorouracil (5-FU)" → card highlights DPYD, CPIC 2017.1, the equity story
2. /genomes → Select a South Asian heterozygous carrier (*1/*2A) archetype
3. /simulate → One-click simulate
4. /results → See:
   - Intermediate Metabolizer phenotype
   - CPIC Strong recommendation: 50% dose reduction
   - Evidence Level A badge
   - Population equity panel: SAS evidence density
   - AI interpretation (grounded, citation-validated)
   - Swarm governance trail (rule IDs, provenance)
5. Compare: Switch to EUR population, same genotype → show how frequency context changes
6. Abstention demo: Pick a sparse-evidence scenario → swarm REFUSES with named rule
```

**Key message:** "This isn't another chatbot that hallucinates. The deterministic engine decides; the LLM explains. When evidence is thin, it refuses honestly rather than over-extrapolating. That's the safety contract an institute can trust."

---

## 7. Next Steps

1. **Today:** Add capecitabine as a second drug card (trivial — same engine)
2. **This week:** Build a pre-loaded Indian CRC cohort demo (50 samples, realistic DPYD distribution)
3. **Before meeting:** Prepare the rs2297595 expanded panel story (even if not yet implemented — show the architecture supports it)
4. **At meeting:** Run the live demo on their laptop, show PCR ingestion API, discuss integration timeline
5. **Post-meeting:** If they share a de-identified cohort, validate against their toxicity outcomes
