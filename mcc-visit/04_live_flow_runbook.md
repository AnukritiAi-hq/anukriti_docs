# Live Flow — Running MCC's Real DPYD Genotypes Through Anukriti

> This is **not a demo**. It is the real production path for putting MCC's own
> lab output through the engine. No mock data, no staged cases — MCC's actual
> PCR/Sanger calls go in, real CPIC-pinned phenotypes and named refusals come
> out. This matters because it is healthcare: what you show must be what runs.
>
> Production API: `anukriti-api` (Azure) — `POST /runs/from-pcr`.
> Frontend: `product.anukritiai.com` → `api.runs.fromPcr`.
> Workflow wired for PCR ingestion today: **`fluorouracil` (DPYD) only**.

---

## What is genuinely real (and what isn't yet)

**Real / production:**
- `POST /runs/from-pcr` ingests **actual lab DPYD output** — TaqMan / KASP /
  Sanger — in three accepted shapes (per-rsID dbSNP genotypes, star-allele
  diplotype text, or per-variant HGVS + zygosity). No VCF/NGS required.
- The engine is **deterministic** (`anukriti-pgx-core`, CPIC-pinned). Same
  input → same phenotype, every time, with table provenance.
- **Named refusals** are real: inputs missing required markers, or non-core
  variants without sufficient evidence, return a **named reason**, not a guess.
- **No PHI crosses the wire or is stored** — only typed genotype letters and
  the lab-supplied patient id. (The endpoint is intentionally public for this
  reason; confirm this posture is acceptable to MCC's governance.)

**Honest limits (state these plainly):**
- PCR ingestion is wired for **DPYD/fluoropyrimidine only** today. Other drugs
  must use a different path. Don't imply broader coverage.
- Non-core South-Asian variants (*9A/rs1801265, *4/rs1801158, *5/rs1801159,
  *6/rs1801160, M166V/rs2297595) are **not over-claimed** — the engine labels
  them "outcome-correlation needed." That is by design.
- It is a **research tool, not a clinical decision-support system**. It does
  not prescribe.

---

## The real input MCC needs to provide

MCC's existing genotyping output, per patient, in **any one** of these shapes
(the API normalises all three):

1. **Per-rsID (most common from TaqMan/KASP):**
   ```json
   { "rs3918290": "CT", "rs67376798": "AA", "rs55886062": "TT" }
   ```
2. **Diplotype text (from a lab star-allele caller):**
   `"*1/*2A"`, `"*2A/c.2846A>T"`, `"HapB3/HapB3"`
3. **Per-variant HGVS + zygosity (Sanger style):**
   ```json
   [ { "hgvs": "c.1905+1G>A", "genotype": "heterozygous" } ]
   ```

> The single most important thing to capture at the visit: **MCC's exact panel
> — the precise rsIDs / cDNA names of all variants their PCR assay reports.**
> The engine validates that the required DPYD markers are present and names
> exactly which are missing if not.

---

## Running it for real (two ways)

### A. Through the product UI (what MCC sees)
1. `product.anukritiai.com` → fluoropyrimidine (5-FU / capecitabine) workflow,
   PCR-input path.
2. Paste/enter the patient's **real** genotype call in one of the three shapes.
3. Run → the Results table shows the **real** phenotype, drug-action signal,
   CPIC **evidence level**, citation, and any **named refusal**.

### B. Directly against the production API (what you can show a technical reviewer)
This is the actual request the UI makes — run it live from a terminal so MCC
sees there is no smoke and mirrors. Use a **real, consented, anonymized** MCC
patient, or MCC's own positive-control sample:

```bash
curl -X POST "$ANUKRITI_API/runs/from-pcr" \
  -H "Content-Type: application/json" \
  -d '{
        "workflow": "fluorouracil",
        "population": "SAS",
        "patients": [
          { "patient_id": "MCC-<anon-id>",
            "rsids": { "rs3918290": "CT", "rs67376798": "AA",
                       "rs55886062": "TT", "rs56038477": "GG" } }
        ]
      }'
```
The response is the **real** per-patient phenotype + per-diplotype
`UnifiedExecutionReport` the frontend renders. (`$ANUKRITI_API` = the Azure
endpoint in `anukriti-main/src/lib/api.js`.)

> Use SAS (South Asian) as the population so the population-aware evidence
> layer reasons in the correct ancestry context for MCC's cohort.

---

## Reading the real result (how to talk through it)

For each patient the engine returns:
- **Phenotype** — Normal / Intermediate / Poor Metaboliser (DPD activity),
  derived deterministically from the diplotype.
- **Drug-action signal** — the CPIC fluoropyrimidine guidance for that
  phenotype, with **evidence level (A–D)** and the **citation**.
- **Named refusal (if any)** — e.g. a required marker missing, or a non-core
  variant flagged "outcome-correlation needed." The reason is explicit.

Say it straight:
> "This is the actual engine on an actual genotype. It tells you the phenotype,
> the guideline-backed action, how strong the evidence is, and — when it doesn't
> know — it says so with a reason. Nothing here is invented."

---

## The cohort run (the real pilot deliverable)

The same endpoint accepts **the whole cohort** in one call (`patients: [...]`,
one entry per patient). Running MCC's anonymized ~400–500-patient spreadsheet
produces the real four-quadrant breakdown:

| Group | Meaning |
|---|---|
| PCR-positive + Grade 3+ toxicity | Panel is catching real risk |
| PCR-positive + no toxicity | Dose management working, or incomplete penetrance |
| **PCR-negative + Grade 3+ toxicity** | **Missed-risk discovery group** — the core finding |
| PCR-negative + no toxicity | Baseline comparison |

This is the real output to promise MCC — produced by the same production
endpoint, on their data, with an audit trail.

---

## Pre-visit checklist (so the live run actually works)

- [ ] Confirm `GET $ANUKRITI_API/health` returns OK from the venue network the
      morning of the visit.
- [ ] Have a **real consented anonymized** MCC sample (or MCC's own
      positive-control genotype) ready — do **not** fabricate one.
- [ ] Confirm MCC's exact panel rsIDs so the input maps cleanly.
- [ ] If venue Wi-Fi is unreliable, agree to run it **on MCC's own machine /
      network** so they see it on infrastructure they trust.
- [ ] Re-confirm the **no-PHI / public-endpoint** posture is acceptable to MCC
      governance before sending any patient genotype, even anonymized.
