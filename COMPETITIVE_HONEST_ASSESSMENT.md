# Competitive Analysis — Honest Assessment

> Generated: 2026-06-06 | Critical evaluation — no sugarcoating

---

## TLDR: Who Could Kill Us

**PGxAI (Palo Alto)** is the closest threat. They have funding, EHR integrations, and are building AI-powered PGx across multiple therapeutic areas. If they add population-aware logic for South Asia, they'd have everything we have plus commercial scale.

**But today, nobody does what our U4 rule does.** That's a narrow, defensible wedge — not a moat.

---

## 1. Direct Competitors — Ranked by Threat Level

### 🔴 HIGH THREAT: PGxAI (Palo Alto, CA)

| Factor | Assessment |
|--------|-----------|
| **What they do** | AI-powered PGx platform. EHR integration (Epic, Cerner, Allscripts). Real-time CDS alerts. Multi-gene, multi-therapeutic area. |
| **Funding** | Published in Mayo Clinic Proceedings (2025). Saudi Arabia partnership. Appears well-funded. |
| **DPYD coverage** | Yes — they cover oncology as a therapeutic area |
| **Population-aware?** | They mention "multi-omics" and "real-world evidence" but **no evidence of ancestry-specific refusal logic** |
| **Their edge over us** | EHR integration, commercial contracts, multi-gene panels, CRO/pharma partnerships, reimbursable (CPT codes) |
| **Our edge over them** | Population-aware refusal (U4 rule), SAS-specific variant handling, deterministic + auditable (not black-box AI), open architecture |
| **Honest risk** | If PGxAI decides to target the Indian market and adds population-specific logic, we're competing against a funded US startup with commercial scale |

### 🔴 HIGH THREAT: OneOme / RightMed (Co-founded by Mayo Clinic)

| Factor | Assessment |
|--------|-----------|
| **What they do** | RightMed® Oncology panel — covers DPYD. Full PGx service: test + CDS + clinician education + billing |
| **DPYD specifically** | RightMed Oncology is "uniquely designed to help oncologists decrease the risk of chemotherapy-induced toxicity" |
| **Scale** | Mayo Clinic co-founded. 4-5 day turnaround. Established in US health systems. |
| **Population-aware?** | No evidence. Standard panel. |
| **Their edge** | Established commercial product, Mayo brand, lab + software bundle, reimbursement solved |
| **Our edge** | Population-specific logic, India focus, research platform (not just a report generator), SAS variant coverage |
| **Honest risk** | They're a mature commercial product. We're a research platform. Different stage, but if they enter India they'd have brand advantage. |

### 🟡 MEDIUM THREAT: Helix (San Mateo, CA)

| Factor | Assessment |
|--------|-----------|
| **What they do** | Just launched (May 2025) a DPYD-specific PGx test. Leader in population-scale genomics. |
| **News** | "Helix Expands Pharmacogenomic Test Portfolio to Support Safer Cancer and Alzheimer's Treatments" |
| **Scale** | Massive genomic database (millions of exomes). Health system partnerships. |
| **Population-aware?** | They have population-scale data but no evidence of population-specific CDS logic |
| **Their edge** | Massive data scale, established US lab network, just entered DPYD space |
| **Our edge** | They're a testing lab, not a decision support platform. No SAS-specific logic. |
| **Honest risk** | They could add CDS downstream. But their business model is lab services, not software. |

### 🟡 MEDIUM THREAT: Applied DNA Sciences (ADNAS) / TR8

| Factor | Assessment |
|--------|-----------|
| **What they do** | TR8 PGx test — 120-target panel with 33+ genes including DPYD. NY State DoH approved LDT. |
| **Positioning** | Explicitly positioning for "pre-emptive testing for safety of 5-FU-based cancer therapeutics" (April 2025) |
| **Population-aware?** | No evidence |
| **Their edge** | Broad panel (120 targets), regulatory approval in NY |
| **Our edge** | They're a lab test, not a platform. No CDS, no population logic. |

### 🟡 MEDIUM THREAT: Yourgene Health / Novacyt

| Factor | Assessment |
|--------|-----------|
| **What they do** | Just launched (May 2026) "Insight DPYD assay" — genetic test aligned with updated guidelines |
| **Geography** | UK/EU |
| **Population-aware?** | No |
| **Honest risk** | Lab assay, not a CDS platform. Not competing on the same layer. |

### 🟢 LOW THREAT: PharmCAT (Academic / Open Source)

| Factor | Assessment |
|--------|-----------|
| **What they do** | Gold-standard open-source tool for VCF → diplotype → recommendation |
| **Strengths** | Canonical, widely cited, well-maintained |
| **Weakness** | CLI tool, no CDS, no population-aware logic, no refusal rules, no real-time platform |
| **Relationship** | Complementary, not competitor. We could integrate PharmCAT for concordance validation. |

### 🟢 LOW THREAT: India PGx (MedGenome, Yoda Diagnostics)

| Factor | Assessment |
|--------|-----------|
| **MedGenome** | Indian genomics lab offering PGx panels. Testing service, not CDS platform. |
| **Yoda Diagnostics** | Hyderabad — PGx testing for cardiovascular panel. Not oncology-focused. |
| **Gap** | Neither has population-aware CDS. Neither targets DPYD specifically for Indian oncology. |
| **Risk** | Low. They're labs. We're a decision platform. Different layer. |

---

## 2. Honest Self-Assessment — Where We're Weak

### What competitors have that we DON'T:

| Capability | Who Has It | We Have It? |
|-----------|-----------|-------------|
| EHR integration (Epic/Cerner) | PGxAI, OneOme | ❌ No |
| CPT code reimbursement | OneOme, Helix, ADNAS | ❌ No |
| CLIA-certified lab | OneOme, Helix, ADNAS | ❌ No |
| Established health system contracts | PGxAI, OneOme | ❌ No |
| Multi-gene panel (33+ genes) | ADNAS, OneOme | ❌ (we have 5 workflows) |
| Commercial revenue | PGxAI, OneOme, Helix | ❌ No |
| Regulatory clearance (FDA/CE) | None for PGx CDS specifically | ❌ N/A |
| Team size (>10 engineers) | PGxAI, OneOme, Helix | ❌ Solo founder |
| Published clinical validation study | Henricks (indirectly) | ❌ Not yet |
| Real patient data | All labs | ❌ Not yet |

### What we have that NOBODY else does:

| Capability | Significance |
|-----------|-------------|
| Population-aware refusal (U4 rule) | **Only platform that refuses for SAS + *9A instead of silently passing** |
| Named rule IDs on every output | **Auditable in a way no other platform is** |
| SAS-specific DPYD variant handling | **Nobody else has *9A/M166V as actionable for South Asians** |
| Evidence density per population | **Nobody else surfaces where evidence is thin** |
| Deterministic + LLM explanation | **Nobody else separates "decides" from "explains"** |
| Open architecture (not black-box) | PharmCAT is open too, but no platform layer |
| Cohort-level simulation | Unique (labs do one patient at a time) |

---

## 3. Critical Honest Questions

### Q: "Are we just an academic toy?"
**Partially yes.** We don't have:
- A single real patient run through the system
- A commercial contract
- A regulatory clearance
- A CLIA lab partner

**But:** We have something none of them have — the architecture for population-aware PGx that's auditable and refuses honestly. That's a wedge, not a product yet.

### Q: "Can PGxAI just add what we do?"
**Yes, technically.** Adding a population-aware override rule is ~50 lines of code. Their barrier isn't technical — it's:
1. They don't have the South Asian clinical evidence wired in (Varma 2020, Hariprakash 2018)
2. They don't have the incentive (their market is US health systems, not India)
3. Their architecture is AI-first (LLM inference) not deterministic-first (rule tables). Adding a hard refusal that overrides their AI would require architectural change.

### Q: "Can OneOme just add Indian variants?"
**Yes, easily.** They'd need to:
1. Add *9A to their panel (trivial)
2. Add a CDS alert for SAS population (requires they capture ancestry)
3. Validate with Indian cohort

They haven't because India isn't their market (US health systems, reimbursement-driven). If ICMR mandates testing, they might enter. We need to be established before that.

### Q: "What's our actual moat?"
**Honest answer:** Our moat is thin. It's:
1. **Speed to Indian market** — first-mover with validated Indian cohort data
2. **Architecture** — deterministic-first with named refusals (hard to retrofit into AI-first systems)
3. **Relationship** — if we get the MCC partnership and publish, we're the cited reference
4. **South Asian evidence** — we've wired in papers nobody else has bothered with

**The moat gets deeper only if we get real patient data and publish.**

---

## 4. What Kills Us (Existential Risks)

1. **PGxAI or OneOme decides to target India** — they have resources, brand, and commercial scale
2. **MedGenome adds a CDS layer** — they already have Indian genomics data at scale
3. **ICMR/CDSCO issues a guideline that just says "use the EU 4-variant panel"** — our population-aware angle becomes irrelevant
4. **We never get real patient data** — stays as a demo forever, no publication, no validation
5. **Solo founder risk** — if Abhimanyu gets distracted/overwhelmed, everything stops

---

## 5. Strategy Implications

### The only path that works:
1. **Get real patient data from MCC THIS MONTH** — that's the moat-deepener
2. **Publish FAST** — first paper with Indian DPYD implementation outcomes = permanent citation
3. **Don't try to be OneOme** — we're not a lab, not a commercial PGx panel company
4. **Position as the research platform for population-aware PGx** — academic institutions are the customer, not health systems (yet)
5. **UGT1A1 next** — PACIFIC-PGx validates the multi-gene approach. Same patients (FOLFIRI = irinotecan + 5-FU). Same institute. Same partnership.

### What to say in the meeting:
> "We're not competing with Helix or OneOme on lab testing. We're building the evidence layer that tells you WHICH variants matter for YOUR population. The EU panel misses 27% of your at-risk patients. We catch them. Help us prove it with your cohort, and that's a Lancet Oncology paper."
