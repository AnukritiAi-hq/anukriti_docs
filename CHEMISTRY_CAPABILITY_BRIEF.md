# anukriti-chemistry — Capability Brief (Honest Edition)

> Generated: 2026-06-06
> Purpose: An honest account of what the chemistry layer genuinely does,
> where molecular-species precision is clinically real, and where it is NOT.
> No overreach — a researcher should be able to read this and find nothing to dispute.

---

## 1. What This Library Actually Is

A small, deterministic Python library (`anukriti-chemistry`, v0.1.0) that
produces **structured chemistry grounding context for the LLM narration
layer only**. It does NOT make clinical decisions, predict binding, or
influence phenotype calling.

Three capabilities, all opt-in, all "never raise":

| Module | What it does | Clinical basis |
|--------|-------------|----------------|
| `smiles` | drug name → SMILES (pinned PubChem snapshot) | Structure reference |
| `roles` | per-enantiomer active/inactive/toxic role | Where chirality is clinically real |
| `activation` | prodrug activation / clearance pathway | Which species the PGx enzyme acts on |
| `stereo` | RDKit stereoisomer enumeration (opt-in) | Structural enumeration |

---

## 2. The Core Claim (What We Can Honestly Say)

> **Most PGx tools treat a drug as a single entity. Anukriti reasons at the
> level of the specific molecular species that the enzyme acts on.**

This is true and defensible. It manifests in two ways:

### A. Per-enantiomer precision (the `roles` module)
For chiral drugs where the enantiomers behave differently, we carry the
per-enantiomer pharmacological role with PMID citations.

### B. Pathway-species precision (the `activation` module)
For prodrugs and drugs with PGx-relevant clearance, we carry the metabolic
pathway so the explanation can name the exact species that accumulates or
fails to form.

**Both are narration-quality differentiators, not decision differentiators.**
The deterministic phenotype call never changes based on chemistry data
(scope firewall). The chemistry layer makes the *explanation* precise.

---

## 3. Where Molecular Precision Is CLINICALLY REAL

### Per-enantiomer (chirality matters):

| Drug | The precision | Why it matters | Status |
|------|--------------|----------------|--------|
| **Warfarin** | S-warfarin 3-5× more potent than R; CYP2C9 metabolizes S specifically | A CYP2C9 PM accumulates *S-warfarin* → bleeding | ✅ Curated |
| **Clopidogrel** | Only S-enantiomer is the active prodrug; R is inert | CYP2C19 activates the S-form to its thiol | ✅ Curated |

### Pathway-species (which molecule the enzyme acts on):

| Drug | The precision | Why it matters | Status |
|------|--------------|----------------|--------|
| **Capecitabine** | 3-step bioactivation → 5-FU; DPD clears the *active* 5-FU | DPYD-deficient patient can't clear active species → accumulation | ✅ Curated |
| **Fluorouracil** | Administered active; DPD clears it | Same DPYD clearance story, no activation step | ✅ Curated |
| **Clopidogrel** | CYP2C19 *activates* the prodrug (inverse of DPYD) | PM never forms active thiol → drug fails | ✅ Curated |

**The clopidogrel/capecitabine contrast is the killer teaching example:**
- Capecitabine: PGx gene controls **clearance** → deficiency = active drug accumulates (toxicity)
- Clopidogrel: PGx gene controls **activation** → deficiency = drug never works (failure)

Same architecture, opposite clinical consequence. Naming the molecular
species is what makes the distinction precise.

---

## 4. Where Molecular Precision Is NOT Applicable (Honest Limits)

### For the DPYD/fluoropyrimidine workflow — chirality is IRRELEVANT:
- **5-FU is achiral** — no stereocenters, no enantiomer story
- **Capecitabine's stereocenters are fixed** — single marketed form, not a clinical choice
- The clinical variance is **100% in the enzyme (DPD), not the molecule**

**So for the DPYD pitch, do NOT lead with isomer/chirality precision.**
The DPYD differentiator is the **U4 population-aware refusal**, not chemistry.
What chemistry adds to DPYD is the **pathway-species grounding** (capecitabine
→ 5-FU → DPD), which is genuinely useful but is about metabolism, not chirality.

### What we deliberately DO NOT claim:
| Claim we could make | Why we DON'T |
|--------------------|--------------|
| "We predict polymorph bioavailability" | Polymorphism (e.g. Ritonavir Form I/II) is a formulation/crystal issue, not PGx. We don't model crystal structures. |
| "We predict binding affinity" | That's docking/virtual screening. Out of scope. RDKit conformers queued for v0.2 but not for clinical claims. |
| "We assign roles for all drugs" | 14 of 20 drugs return UNKNOWN. We refuse to fabricate. |
| "Chemistry influences the phenotype call" | Scope firewall — it never does. LLM explains, deterministic rules decide. |

---

## 5. The Polymorphism Question (Addressed Honestly)

Polymorphism — same molecule, different crystal packing → different
bioavailability — is a **real phenomenon** (the 1998 Ritonavir
disappearing-polymorph recall is the textbook case; we have that paper in
`anukriti_docs/papers/Ritonavir_Conformational_Polymorphism.pdf`).

**But it is NOT a pharmacogenomic phenomenon:**
- It doesn't interact with gene variants
- It's a manufacturing/formulation issue
- Predicting it requires crystal-structure modelling we don't do

**Honest position:** We use Ritonavir polymorphism as a *teaching example* of
why molecular-level precision matters in pharmacology. We do NOT claim to
predict polymorphs. Conflating the two would be the kind of overreach a
reviewer catches immediately.

---

## 6. Scope Firewall (The Safety Architecture)

Chemistry data MUST NOT be imported by:
- `anukriti-pgx-core` (deterministic truth layer)
- `anukriti-swarm/agents/pharmacogene/` (phenotype calling)
- `anukriti-swarm/core/runtime/` (the lifecycle)
- `anukriti-swarm/core/evidence_sufficiency/` (R/V/U rules)
- `anukriti-swarm/core/orchestrator/` (GenerativeBoundary)

Legitimate consumers:
- `anukriti-swarm/ai/narrative/` (LLMNarrator — Stage 5b)
- `anukriti-swarm/retrieval/evidence/`

**Central invariant:** *No LLM-shaped data may influence deterministic
phenotype calling.* Chemistry context is explanation, not truth.

---

## 7. Curation Roadmap (What's Real vs Planned)

### Curated today (v0.1.0):
- **Roles:** warfarin, clopidogrel, simvastatin, codeine, carbamazepine, phenytoin (6 drugs)
- **Pathways:** capecitabine, fluorouracil, clopidogrel (3 drugs)

### Honest gaps (return UNKNOWN/None):
- 14 drugs in SMILES snapshot have no curated role
- Most drugs have no curated pathway

### v1.1 candidates (genuine, citable cases):
| Drug | Why it's a real case |
|------|---------------------|
| **codeine** | CYP2D6 bioactivation to morphine — prodrug story like clopidogrel |
| **tamoxifen** | CYP2D6 bioactivation to endoxifen — oncology prodrug story |
| **azathioprine/mercaptopurine** | TPMT/NUDT15 clearance — clearance story like DPYD |
| **thalidomide** | S=teratogenic, R=therapeutic, interconvert in vivo — the classic chirality-tragedy case |
| **esomeprazole** | Pure S-enantiomer of omeprazole, marketed separately, CYP2C19-metabolized |

---

## 8. How to Position This (For the Meeting)

### DO say:
> "For chiral drugs, we carry the per-enantiomer role with PMID citations.
> For prodrugs, we carry the activation pathway. So when we explain why a
> CYP2C19 poor metabolizer fails clopidogrel, we name the exact step —
> the active thiol never forms. And when we explain DPYD toxicity, we name
> the exact species — active 5-FU accumulates because DPD can't clear it.
> Grounded, cited, not generic. And the chemistry never touches the
> deterministic call — it only makes the explanation precise."

### DON'T say:
- "We predict polymorphs" (we don't)
- "Chemistry improves our DPYD accuracy" (it doesn't — U4 does that)
- "We model binding/docking" (out of scope)

### The honest one-liner:
> **"We reason about the molecular species the enzyme acts on, not just the
> drug name — but only where the literature supports it, and never in a way
> that influences the deterministic decision."**

---

## 9. Bottom Line

The chemistry layer is a **genuine, narrow, defensible** capability:
- Real for warfarin/clopidogrel chirality and capecitabine/5-FU pathways
- NOT a chirality story for DPYD (the enzyme matters, not the molecule)
- NOT a polymorph predictor
- A narration-quality differentiator, not a decision differentiator
- Honest by default (UNKNOWN/None rather than fabrication)

It strengthens the platform's "deterministic decides, LLM explains" story
by making the explanation chemically precise — without overreaching into
claims we can't back.
