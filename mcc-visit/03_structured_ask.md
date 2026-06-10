# Structured Ask — MCC Visit

> Keep this open during the conversation. The ask is **tiered**: lead with the
> relationship and the data, not the technology. Each tier is a clean stopping
> point — if MCC says yes to Tier 1, you have a pilot.

---

## The frame (open with this)

> "You already have the hard part — real Indian patients, DPYD-tested, with
> toxicity outcomes. I have an engine that turns that into a genotype-to-
> toxicity map and finds the patients your current panel might have missed.
> I'm not asking you to validate a finished product — I'm asking you to be the
> clinical evidence partner. You own the clinical interpretation; I own the
> reproducible analysis."

---

## Tier 0 — Relationship & intent (always)

- [ ] Confirm the **right point(s) of contact**: oncologist + clinical
      pharmacist + whoever owns the DPYD PCR data.
- [ ] Confirm MCC's **interest in a collaboration** (not a sale): joint
      analysis, MCC as lead clinical institution.
- [ ] Capture the **MCC point-of-contact email** (for the PilotLead record).
- [ ] Agree the **honesty boundary**: this is a research tool; it does not
      prescribe; no PHI leaves MCC.

## Tier 1 — The data ask (the real goal of this visit)

Ask for an **anonymized spreadsheet**, one row per patient:

- [ ] `anonymized_patient_id` (no names/MRNs/identifiers)
- [ ] `cancer_type` (colorectal, head & neck, breast, gastric, …)
- [ ] `fluoropyrimidine_drug` (5-FU / capecitabine / tegafur / regimen)
- [ ] **DPYD assay method** — exact real-time PCR kit/platform
- [ ] **The exact variants tested** — rsIDs and/or cDNA names (this is the
      single most important item — we need MCC's precise 7-variant panel)
- [ ] `genotype per variant` (CC/CT/TT or positive/negative)
- [ ] `toxicity grade` (CTCAE preferred) + `toxicity type`
- [ ] Strongly preferred: `starting dose`, `dose reductions/interruptions`,
      `cycles received`, `toxicity onset cycle/date`

**The one question to land:**
> "How many of your ~400–500 patients had **Grade 3+ toxicity while negative
> on all panel variants**?"

## Tier 2 — Scope the analysis & publication

- [ ] Agree **Phase 1** deliverable: per-patient concordance table + the
      four-quadrant breakdown (PCR±  ×  toxicity±).
- [ ] Agree handling of **PCR-negative / toxicity-positive** patients
      (Phase 2): NGS if it exists, or propose targeted DPYD sequencing on that
      subset + matched controls only — **not** everyone.
- [ ] Float the **publication** and authorship/ownership split (MCC = clinical
      lead and cohort context; Anukriti = analytical pipeline + audit trail +
      population-evidence stratification).

## Tier 3 — Logistics & governance

- [ ] Who signs off on data sharing? (PI / ethics committee / institutional
      review) — hand them `05_data_sharing_mou_outline.md`.
- [ ] Data transfer method (encrypted, anonymized; secure channel).
- [ ] Timeline: Phase 1 in ~4–6 weeks from data handoff.
- [ ] Next concrete step + owner + date.

---

## What we are NOT asking for

- ❌ Raw patient identifiers or PHI.
- ❌ Raw sequence files (summaries/calls only).
- ❌ MCC to endorse or "validate" the product.
- ❌ Any change to their current clinical workflow during the pilot.

## Leave-behind checklist

- [ ] Hand over `02_one_pager_leave_behind.md` (printed).
- [ ] Capture contact email → fill into `01_pilot_lead_record.json` → paste to portal.
- [ ] Log the visit via `06_audit_log_entry.json`.
- [ ] Send a same-day thank-you with the Tier-1 spreadsheet template attached.
