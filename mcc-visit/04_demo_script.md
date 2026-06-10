# Demo Script — DPYD / 5-FU Flow

> A tight, ~8–10 minute live walkthrough for the MCC visit. Goal: show that
> Anukriti ingests **PCR input (not just VCF)**, classifies DPYD deterministically,
> and refuses honestly on thin evidence — using a case that mirrors MCC's own data.
>
> Product: `product.anukritiai.com` (frontend) → `anukriti-api` backend.
> The PCR path is `POST /runs/from-pcr` (frontend: `api.runs.fromPcr`). Have a
> backup screen-recording in case of venue Wi-Fi.

---

## Before you start (setup, 1 min)

- [ ] Laptop on charger; product.anukritiai.com loaded and logged in.
- [ ] Backup: offline screen-recording of the full flow on the desktop.
- [ ] Backup-backup: screenshots in this folder if live demo fails.
- [ ] Open with the one-liner, not the UI:
  > "Let me show you what happens when a DPYD PCR result goes in — using a case
  > that looks like yours."

---

## Act 1 — The input is *their* input (2 min)

**Talking point:** MCC tests on real-time PCR, not NGS. Show that the engine
accepts structured PCR calls directly — no sequencing pipeline required.

1. Go to the simulation / new-run surface → choose the **fluoropyrimidine
   (5-FU / capecitabine)** workflow.
2. Enter a **PCR-style genotype** for DPYD, e.g.:
   - `DPYD c.1905+1G>A (rs3918290, *2A)` → **heterozygous**
3. Point out: "This is exactly the shape of a PCR call sheet — variant +
   genotype. No VCF, no FASTQ."

> If they ask 'what if it's a variant not on our panel?' — that's Act 3. Park it.

## Act 2 — Deterministic classification + evidence level (3 min)

**Talking point:** The rules decide; the AI only explains. Every call is
CPIC-pinned with provenance.

1. Run it. Show the result:
   - **Phenotype:** Intermediate Metabolizer (heterozygous no-function allele).
   - **Recommendation signal:** reduce starting dose / titrate — **with CPIC
     evidence level (A)** and the **citation** shown inline.
2. Highlight the **Evidence Badge / tooltip** — the level comes from the engine,
   not a guess.
3. (Optional) Show the **plain-English explanation panel** — note it routes
   through the **grounded** backend (`/llm-context/grounded`): deterministic
   narrative first, and if the LLM can't be citation-validated, its text is
   **dropped** and a named fallback stands. "It cannot invent a recommendation."

> Key line: "Notice it told you *why*, cited the guideline, and showed how
> strong the evidence is. That audit trail is the product."

## Act 3 — The honest refusal (the differentiator, 3 min)

**Talking point:** This is the part that matters for MCC's cohort.

1. Enter a **South-Asian candidate variant** that is *not* CPIC-core, e.g.:
   - `DPYD c.85T>C (rs1801265, *9A)` → heterozygous, or `M166V (rs2297595)`.
2. Show the engine **does not over-claim**: it labels the call
   **"research evidence / outcome-correlation needed"** rather than asserting a
   confident phenotype — a **named** reason, not silence.
3. Land the pitch:
   > "For your panel-negative toxicity patients, this is the point. The engine
   > won't pretend to know. But your outcome data can **resolve** whether *9A or
   > M166V actually matters in an Indian cohort — and if it does, we upgrade the
   > rule, with your data as the evidence. That's the paper."

## Act 4 — From one patient to the cohort (1–2 min)

**Talking point:** Scale the single-patient view to MCC's ~400–500.

1. Show the cohort / from-samples view (or describe it): the same engine runs
   over a whole spreadsheet and produces the four-quadrant table:
   - PCR-positive + Grade 3+ toxicity
   - PCR-positive + no toxicity
   - **PCR-negative + Grade 3+ toxicity** ← the discovery group
   - PCR-negative + no toxicity
2. Close:
   > "Send me an anonymized spreadsheet and this is what comes back — per
   > patient and for the whole cohort. No PHI, no raw sequences. You stay the
   > clinical lead."

---

## If asked, answer crisply

| Question | Answer |
|---|---|
| "Is this FDA/CDSCO approved?" | "No — it's a research tool, not a clinical decision-support system. It informs research and panel design; it doesn't prescribe." |
| "Do you store our patient data?" | "Anonymized summaries only — no names, no raw sequences. Details in the MOU outline I'll leave with you." |
| "Does it work without NGS?" | "Yes — PCR calls go straight in. NGS only matters later, for the panel-negative toxicity subset." |
| "What's it built on?" | "A CPIC-pinned deterministic engine (`anukriti-pgx-core`) for the calls; the AI layer only narrates and is blocked from inventing recommendations." |

## Do NOT

- ❌ Claim actionability for *9A / *4 / *5 / *6 / M166V. Show the refusal instead.
- ❌ Show dosing as a prescription. It's a research signal.
- ❌ Use any real MCC patient data in the live demo — use the synthetic case.
