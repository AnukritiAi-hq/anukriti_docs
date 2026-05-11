# Anukriti — Full Platform & Business Analysis

> **Snapshot date:** 2026-05-11
> **Scope:** anukriti-pgx-core · anukriti (product) · anukriti-swarm · anukriti_docs
> **Purpose:** honest read of where the platform is, what the idea
> actually is, the business posture, and the priority-ordered gap
> list. Written as a founding-engineer briefing, not marketing.

---

## 1. What Anukriti actually is (today)

**One-line:** Deterministic, population-aware pharmacogenomics (PGx)
reasoning infrastructure. `(drug × gene × ancestry) → research-grade
risk answer with named refusals when evidence is thin.`

**Core insight (defensible):** Most of what the field calls "AI bias
in healthcare" is **data-access bias**, not model bias. A bigger model
over Eurocentric evidence just produces *confident* wrong answers. The
solution is an architecture that treats evidence density as
first-class and refuses honestly when it's thin. That's an
**infrastructure problem**, not a model problem.

---

## 2. How it works — technical stack, end to end

### Three-repo platform (+ 1 docs repo)

| Repo | Role | State | Purpose |
|---|---|---|---|
| **anukriti-pgx-core** | Deterministic library | **PyPI v0.2.1**, stable, 51/51 tests | 13 CPIC-pinned gene callers, zero LLM, zero network I/O, zero runtime deps |
| **anukriti** (Synthatrial) | FastAPI + Streamlit product | `clinical-grade-pgx` branch, 353/1 tests | Clinical PGx reports, trial export, FHIR, drug reranker |
| **anukriti-swarm** | Research platform | `hackathon/agents-assemble-2026` branch, 234 tests, 29 demos | 9 agents, 6 MCP services, 31 tools, live mission-control UI |
| **anukriti_docs** | Learning content | Published | 14-module engineering course + 15-module agentic-AI course |

### Pipeline (what runs on a query)

```
VCF / diplotype input
   │
   ▼
Layer 1 (pgx-core) — GeneCaller → diplotype (star allele)
   │
   ▼
Layer 2 (pgx-core) — PhenotypeEngine → PM/IM/NM/RM/UM
   │
   ▼
Layer 3 (swarm) — 9 specialist agents over a closed-enum message bus
   ├── population agents (SAS/AFR/EUR) — allele freq + Hardy-Weinberg
   ├── pharmacogene agents (CYP2D6 / CYP2C19 / HLA-B)
   ├── MA-RAG retrieval (dense + population-aware + KG + diversity)
   ├── sufficiency layer (6 facets · 31 deterministic rules · 3 bias patterns)
   ├── 4 verification engines (shape · existence · truth · chain)
   └── narrative (LLM, guarded by GenerativeBoundary)
   │
   ▼
UnifiedExecutionReport (frozen · 18 fields · JSON · <2ms deterministic path)
   │
   ▼ (hackathon layer)
FHIR R5 — DetectedIssue + ClinicalImpression + Provenance
```

### Safety architecture — the real moat

- **GenerativeBoundary** — 4 runtime-forbidden LLM actions:
  `infer_phenotype`, `override_recommendation`, `bypass_verification`,
  `fabricate_claim`. These raise, not log.
- **18 closed-enum scope firewalls** across modules
- **Provenance required on every KG edge** — non-empty
  `ProvenanceStamp.source_id`
- **Every refusal cites a rule ID** (R1..R12, V1..V10, U1..U9, or a
  named bias kind)
- **Byte-identical regression contract** — 353/1 + 12/12 + locked demo
  byte counts
- **Off-by-default** — new capabilities integrate via constructor args
  defaulting to `None`, not feature flags

### Current metrics (real numbers)

- **< 2ms** e2e on deterministic path
- **< 30ms** end-to-end on the full hackathon FHIR path
- **298 tests total** — 234 swarm + 51 pgx-core + 54 hackathon (+ 353
  product biomedical suite)
- **13 genes** (11 star-allele, 2 single-rsID) + 2 product-layer shims
  (GST, HLA-B)
- **3 populations** (SAS / AFR / EUR) with real allele-frequency splits
- **CPIC 2022 + 2019** guidelines pinned; 29 provenance manifest entries

---

## 3. The idea — why it matters

**Trigger story.** 2019. South Asian uncle, post-PCI. Cardiologist
prescribes clopidogrel. Patient is CYP2C19 `*2/*2` — loss-of-function.
The drug never activates. Another cardiac event six months later.

**The gap:**

- **14% of South Asians** are CYP2C19 PMs → can't activate clopidogrel
- **~2% of Europeans** are in the same bucket
- Prescribed at the same rate across populations
- EHRs don't carry genotype, clinical decision support is Eurocentric,
  prescriber training is silent on ancestry-specific risk

**Market shape:**

- **~2M serious ADRs/year in the US**, ~100K deaths
- **$30B/year** preventable cost
- CPIC guidelines exist but adoption is fragmented, lab-testing gated,
  and Eurocentric by evidence-base construction

---

## 4. Business side — where it stands

### What exists

- Live demo: `anukriti.abhimanyurb.com`
- Published PyPI library (`anukriti-pgx-core==0.2.1`)
- AWS AI Competition Finalist
- SAMANWAYA'26 conference abstract submitted
- Hackathon submission ready (Agents Assemble 2026 — MCP Superpower
  for Prompt Opinion)
- DeepVariant collaboration pitch drafted
- Landing page deployed with full SEO + schema.org JSON-LD

### Strategic positioning (shifted 2026-05-10)

- **Reframed: "infrastructure, not a healthcare-AI model"**
- Moat is architecture shaped for federated / controlled-access data
  from day one
- **Three-tier data strategy:**
  - **Tier 1 (open):** CPIC audit acceleration, IndiGen, GenomeAsia
    Pilot — weeks
  - **Tier 2 (institutional):** All of Us Researcher Workbench,
    GenomeIndia FeED — 1–3 months
  - **Tier 3 (controlled):** H3Africa DBAC, national biobanks,
    GenomeAsia 100K consortium — quarters to years
- Honest scope firewall: **pre-trial risk reasoning**, not a clinical
  decision tool, not a trial substitute

### Customer targets identified

1. **CROs** — trial stratification via `/trial/export` (current
   beachhead)
2. **Healthcare AI platforms** — MCP Superpower (Prompt Opinion, and
   any other A2A/MCP-native platform)
3. **Researchers** — cohort-scale PGx reasoning over allele frequencies

---

## 5. What's lacking — honest gap list

### Security / hygiene ⚠️ **CRITICAL**

- **`.env` with secrets is still in git history (product repo).**
  Needs BFG scrub + credential rotation **before any public push,
  investor deck, hackathon demo URL share, or external contributor
  onboarding**.
- No documented secret-rotation playbook.

### Biomedical completeness

- **No end-to-end PharmCAT concordance run published.** Framework
  exists (CP-5), not executed. CROs will ask "is this actually
  correct?" on day one.
- **CYP2D6 CNVs are heuristic-only.** Star-5 deletion and xN
  duplications need a Cyrius / Stargazer wrapper. Biggest PGx edge
  case.
- **NAT2 / CYP2B6 multi-rsID haplotypes** skipped in callers.
- **No real VCF ingestion in the UI** — accepts pre-called diplotypes
  only.
- **No WhatsHap phasing adapter** for BAM inputs.
- **LLM output validation layer missing.** Template engine shipped,
  but no reject-on-hallucinated-entity check yet.
- **No 50-scenario expert-reviewed clinical validation dataset.**

### Engineering debt

- `api.py` ~5000 lines, `app.py` ~3800 lines. Monoliths are hostile to
  new contributors.
- Binary artifacts (`awscliv2.zip`, stray `.tbi` files) in product
  repo root.
- **22 of 29 CPIC provenance entries still `needs_audit`.**
- Ruff hard-gate covers only ~3 directories of swarm; progressive
  rollout continues.

### Business / GTM ⚠️ **BIG**

- **No commercial model.** No pricing, no contract template, no SaaS
  tier, no subscription, no paid-pilot agreement documented.
- **No customer contracts / LOIs / paid pilots.** Competition +
  hackathon finalist, but no revenue path.
- **No defined ICP beyond "CROs."** No named target accounts, no sales
  motion, no outbound playbook.
- **No regulatory strategy.** FDA SaMD? EU IVDR? CE mark?
  Research-use-only disclaimer is correct for today, but caps the
  addressable market.
- **No data partnerships signed.** Strategy doc lists H3Africa /
  GenomeIndia / All of Us as targets; zero applications in flight
  (documented).
- **No clinical advisory board.** Need practicing names — pharmacist,
  clinical pharmacologist, cardiologist.
- **No external moat proof point.** Architectural moat is real but
  needs an external validator — published concordance study, peer
  review, institutional pilot.
- **One founder visible.** No co-founder, no biomedical PhD advisor on
  the deck. Investors will ask.
- **No funding path.** Grant strategy? Pre-seed? Research-infra fund?
  Healthcare-vertical fund? Currently unclear.
- **Solana attestation was correctly demoted** — but its original
  inclusion is a canary for "solution looking for a problem" drift.
  Watch the next new capability with the same skepticism.

### Research direction

- **No cohort-scale Monte Carlo demo shipped yet** (strategy doc
  lists it as "ship now").
- **Method 4 cross-ancestry hedge** scaffolded but not wired to
  user-visible output.
- **Pre-trial risk surfacing UI** doesn't exist yet — only the export
  API.

---

## 6. What to do — priority-ordered

### Week 0 — Stop the bleed (security) ⚠️

1. **BFG `.env` scrub + rotate every previously committed credential.**
   Before ANY public push, investor deck, hackathon demo URL share.
2. Document secret management. Move to AWS Secrets Manager or
   1Password-backed env injection.

### Weeks 1–2 — Proof point (credibility)

3. **Run PharmCAT concordance end-to-end.** GeT-RM 240 samples +
   1000 Genomes (NA12878, NA19240, HG00096). Publish the table under
   `docs/validation/` with gene × sample × caller breakdown. Target
   ≥95% on common alleles. **Single highest-ROI artifact** — converts
   "nice architecture" to "verifiably correct."
4. **Ship the cohort-scale Monte Carlo demo.** 10K synthetic SAS
   patients on clopidogrel; show the 14% can't-activate distribution
   with named abstentions where evidence is thin. Screenshot →
   landing page. This is the wedge demo.
5. **Split `api.py` and `app.py`** into router / page modules.
   Contributor onboarding goes from hostile to reasonable.

### Weeks 3–4 — Distribution (GTM foundations)

6. **Write a one-page "for CRO bioinformaticians" page.** What you do
   / don't do, pricing placeholder ("pilot partnerships, contact us"),
   PharmCAT concordance link, FHIR-native export sample.
7. **Identify 20 target CROs.** Tier by size (ICON, IQVIA down to
   mid-market). 5 outbound/week with the concordance report as the
   opening artifact.
8. **Submit the hackathon.** (Already near-done.) Use the submission
   artifact as social proof on the landing page and in outbound.
9. **Apply to All of Us** as the first institutional partner. The
   relationship alone is 1–3 months of calendar — start now, run in
   parallel with sales.

### Months 2–3 — Validation (external trust)

10. **Publish a 50-scenario clinical validation dataset** +
    LLM-output validation layer. Invite 3–5 pharmacists to review.
    Put their names on the deck.
11. **Stand up a clinical advisory board.** Two or three practicing
    specialists: one pharmacist, one clinical pharmacologist, one
    cardiologist — South Asian patient-base preferred for the wedge
    story.
12. **Sign one paid pilot** (CRO, research hospital, or mid-market
    pharma informatics group). Any revenue point shifts the
    conversation more than any new feature will.
13. **File for a small research grant** (NIH STTR, Indian DBT BIRAC,
    Wellcome LEAP) while commercial dialogue is slow.

### Months 3–6 — Moat expansion

14. **CYP2D6 CNV via Cyrius wrapper.** Highest-value biomedical gap,
    roughly one month of focused work, slots into `anukriti-pgx-core`
    as a new `CNVCaller` base class.
15. **Regulatory clarity decision.** Research-use-only (current),
    SaMD, or IVDR path. Each has different product implications.
    Talk to regulatory counsel, pick one, stop drifting.
16. **H3Africa DBAC application.** Start now; 3–9 month timeline.
    African-ancestry data is the long-term differentiator.
17. **Co-founder / senior biomedical hire.** Pharmacogenomicist with
    CPIC-committee ties is the ideal profile. Pre-seed terms are
    easier with two founders.

---

## 7. The blunt take

### Strengths are real

- Architecture is genuinely differentiated and defensible.
- The story (SAS → clopidogrel) is emotional *and* factually correct.
- Code quality is above hackathon-average: 234 tests, byte-identical
  regression contract, CPIC provenance framework.
- Positioning ("infrastructure, not model") is correct and
  sophisticated — and rare in the competitive set.

### Two existential risks

1. **No commercial model yet.** Every day without a signed pilot is a
   day of runway spent on architecture polish. Ship PharmCAT
   concordance + outbound to 20 CROs in the next 30 days, or the
   architectural moat becomes an expensive hobby.
2. **Secret hygiene.** One Twitter thread about a leaked key in git
   history wipes out years of built credibility. Fix this week.

### Biggest opportunity

The hard part (the infrastructure) is already built. Competitors
trying to match the scope firewall + sufficiency layer + provenance
chain + byte-identical regression contract face six to twelve months
of refactor pain. That window is the real asset — use it to lock in
partnerships, customers, and data-access relationships. Not to keep
polishing the engine.

---

## 8. Revisit schedule

Update this document when any of the following happens:

- A paid pilot or LOI is signed
- PharmCAT concordance results are published
- A Tier-2 data partnership (All of Us / GenomeIndia) lands
- A regulatory posture decision is made (SaMD / IVDR / RUO)
- A co-founder or clinical advisory board member joins
- The competitive set shifts materially (a competitor adopts the same
  architectural discipline)

---

## Cross-references

- [anukriti-pgx-core/PLATFORM.md](https://github.com/AnukritiAi-hq/anukriti-pgx-core/blob/main/PLATFORM.md)
  — three-repo platform map
- [anukriti-pgx-core/docs/strategy.md](https://github.com/AnukritiAi-hq/anukriti-pgx-core/blob/main/docs/strategy.md)
  — moat + data-tier strategy
- [anukriti-pgx-core/PROJECT_CONTEXT.md](https://github.com/AnukritiAi-hq/anukriti-pgx-core/blob/main/PROJECT_CONTEXT.md)
  — library founder decisions D1–D11
- [anukriti/CLINICAL_GRADE_ROADMAP.md](https://github.com/Abm32/Synthatrial/blob/clinical-grade-pgx/CLINICAL_GRADE_ROADMAP.md)
  — CP-1..CP-6 tactical execution plan
- [anukriti/ROADMAP.md](https://github.com/Abm32/Synthatrial/blob/clinical-grade-pgx/ROADMAP.md)
  — product roadmap
- [anukriti-swarm/ARCHITECTURE.md](https://github.com/AnukritiAi-hq/anukriti-swarm/blob/main/ARCHITECTURE.md)
  — swarm technical architecture
- [anukriti-swarm/hackathon/SUBMISSION.md](https://github.com/AnukritiAi-hq/anukriti-swarm/blob/hackathon/agents-assemble-2026/hackathon/SUBMISSION.md)
  — Agents Assemble 2026 submission

---

*This analysis lives in `anukriti_docs` because it spans all three
repos and is a single-point-of-truth briefing for future sessions,
new contributors, and the founder's own revisits. Technical and
tactical docs live in their respective repos; strategic cross-repo
reads live here.*
