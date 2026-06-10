# Anukriti × Malabar Cancer Centre
## Catching fluoropyrimidine toxicity before the first dose

*One-page leave-behind · DPYD safety engine · 2026*

---

### The clinical problem

5-FU and capecitabine are catabolised by the **DPD enzyme** (gene *DPYD*).
Patients with DPYD variants clear the drug slowly, so it accumulates to toxic
levels — causing severe, sometimes fatal mucositis, diarrhoea,
myelosuppression, and hand-foot syndrome. Pre-treatment DPYD genotyping
identifies these patients **before the first dose**, so the starting dose can
be reduced or the drug avoided.

The catch: the variants on standard panels were defined largely in **European**
cohorts. **South Asian** patients carry variants that those panels may miss —
so a "negative" result is not always a safe result.

---

### What Anukriti is (and is not)

**Anukriti is a safety engine for fluoropyrimidines.**
Input: a patient's DPYD genotype (from PCR *or* NGS).
Output: a DPD-activity / metabolizer phenotype + a fluoropyrimidine
**toxicity-risk and starting-dose** signal, with the **evidence level** and the
**citation** behind every call.

| Anukriti answers | Anukriti does **not** answer |
|---|---|
| Will this patient clear 5-FU/capecitabine normally? | Will this tumour respond to 5-FU? |
| Should the starting dose be reduced or the drug avoided? | Any tumour-biology / efficacy question |
| Which variants are actionable, and how strong is the evidence? | It does **not** prescribe — outputs are research artifacts |

**Deterministic first. The rules decide; the AI only explains.** Every
phenotype call comes from CPIC-pinned rule tables (not a language model), with
full provenance. When evidence for a population is thin, the system **refuses
honestly with a named reason** rather than guessing.

---

### Why MCC, why now

MCC already holds something most institutions don't: a **real-world Indian
oncology cohort** — DPYD-tested patients **with toxicity follow-up**. That is
exactly the data that turns genotype frequency into **clinical evidence**.

**The question we can answer together:**
> Among MCC's DPYD-tested patients, how many had **Grade 3+ toxicity while
> testing negative on all current panel variants?**

Every such patient is a **missed-risk case** — and potential evidence that the
panel should include South-Asian variants.

---

### What MCC gets

- A per-patient **concordance table**: predicted risk vs observed toxicity.
- A count of **panel-negative, toxicity-positive** patients (the discovery group).
- An assessment of whether MCC's **7-variant panel is sufficient**, with
  specific South-Asian candidate variants to consider.
- A **reproducible, audit-logged analytical pipeline** — and a path to a joint
  publication: *"DPYD variant spectrum and fluoropyrimidine toxicity in an
  Indian oncology cohort."* **MCC leads the clinical interpretation.**

### What we ask (starting point)

An **anonymized spreadsheet** — one row per patient: cancer type,
fluoropyrimidine drug, the exact DPYD variants tested + genotypes, and toxicity
grade/type/timing. **No names, MRNs, or identifiers. No raw sequences.**

---

**Founder:** Abhimanyu R B · AWS AIdeas finalist (top 50)
**Contact:** [email / phone] · **Platform:** product.anukritiai.com
*Anukriti is a research tool, not a clinical decision-support system. It does not replace clinical judgment.*
