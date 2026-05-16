# Anukriti — Idea Refinement & Revised Technical Phasing

> **Date:** 2026-05-14
> **Scope:** anukriti-pgx-core · anukriti (product) · anukriti-swarm + 6 research papers
> **Audience:** founder + future engineering sessions
> **Purpose:** translate paper findings into concrete idea revisions and a revised technical roadmap

---

## TL;DR — what changes

The core thesis is **validated and sharpened** by the new papers. Three things change:

1. **The wedge expands.** Stop selling "South Asian + clopidogrel" as the only flagship. The Kerdoncuff 2025 Cell paper hands us a second, equally compelling story — **BCHE L307P / anesthesia muscle paralysis**, enriched in the Vysya community of Andhra Pradesh/Telangana at 0.28%, **completely absent outside South Asia**. Sharper than the clopidogrel story because the variant doesn't exist in gnomAD — it's invisible to every existing PGx system. Anukriti can see it. No competitor can.

2. **The architecture needs a sub-population layer.** 5 super-populations (EUR/EAS/SAS/AFR/AMR) is provably too coarse. Kerdoncuff shows 6 distinct Indian regions with measurably different ancestry profiles, and founder effects mean **community-level (jati / endogamous group) frequencies matter more than super-population frequencies for recessive-PM prediction**. The KG `SuperPopulation` enum needs a sibling `IndianRegion` enum (6 values) and an open `CommunityLevel` extension point.

3. **Zack 2026 (npj Digital Medicine) is the most important paper for positioning.** They built an agentic AI for *generating* CPIC guidelines (91.9% extraction, 9.0/10 expert score, beat GPT-5/Claude/Grok). This is **not a competitor — it's a complement.** They produce guidelines; Anukriti applies them with population-aware sufficiency gating. Position the two as an upstream/downstream pair. Reach out for a partnership.

The technical phasing puts **PharmCAT concordance** ahead of everything else, then **Indian sub-population layer** (new), then **founder-effect / variant-novelty extensions** (new), then existing roadmap items.

---

## Part 1 — Zack et al. 2026 (npj Digital Medicine)

*Agentic AI for PGx recommendation generation*

**What they built:** A 3-stage pipeline by PGxAI Inc. (Palo Alto):

- **Stage 1 — Acquisition:** retrieves full-text biomedical literature + FDA drug labels
- **Stage 2 — Evidence extraction:** LLM extracts 35 binary fields per article (study design, sample size, genotype distribution, statistical significance, etc.). 91.9% accuracy across 22 articles, 2310 binary judgments by 3 expert annotators
- **Stage 3 — Recommendation generation:** LLM synthesizes phenotype-specific dosing recommendations (CPIC-style) from structured evidence

**Headline numbers:** 9.0/10 expert score, beats GPT-5 (7.8), Claude, Grok. 0.83 pairwise win rate vs CPIC reference. Outperforms GPT-5 specifically because GPT-5 over-generates (invents specific dosages when CPIC says "no recommendation").

**Honest competitor framing:**

| Dimension | Zack 2026 (PGxAI Inc.) | Anukriti |
|---|---|---|
| **Output unit** | Guidelines (one per gene-drug pair) | Patient-level / cohort-level risk reports |
| **Scope** | Replaces / supports CPIC curation panel | Applies CPIC guidelines population-aware |
| **Key technique** | LLM extraction + generation | Closed-enum rule tables + KG + sufficiency gating |
| **Population dimension** | Acknowledged gap ("limited population coverage") | First-class reasoning input |
| **Refusal behavior** | Returns "no recommendation" when evidence is thin | Names specific rule ID (R1..R12, V1..V10, U1..U9) |
| **Determinism** | LLM-driven (probabilistic outputs) | Deterministic core + guarded LLM edge |
| **Customer** | CPIC committee, hospital labs, pharma curation | CROs, research platforms, federated-data partners |

**What this means for Anukriti:**

- **They are upstream, we are downstream.** Their output (a structured guideline draft) is *exactly* what feeds into our `guidelines/cpic.py`. We don't compete; we consume. A partnership is the right framing.
- **Their explicit gap is our explicit moat.** They write: *"limited coverage of gene-drug pairs and population contexts."* Anukriti's evidence-sufficiency layer + 18 closed-enum scope firewalls + GenerativeBoundary is the architecture they don't have because they're solving a different problem.
- **GPT-5 over-generation is an Anukriti talking point.** Zack 2026 shows GPT-5 invents specific dosages where CPIC says "no recommendation." Anukriti's `GenerativeBoundary` forbids exactly this (`fabricate_claim` is one of the 4 raise-on-violation actions). We have direct evidence that this is a real failure mode of leading LLMs in this domain.
- **Their evaluation framework is borrowable.** 24-recommendation blinded expert evaluation, 0–10 scale, pairwise CPIC concordance. We should adopt the same protocol for our own validation work — it's now the published bar.

**Action items:**

- Cite Zack 2026 in Anukriti's positioning doc as upstream-complement
- Reach out to PGxAI Inc. (`mz@pgx.ai`) for a "they generate, we apply" partnership conversation
- Adopt their 24-recommendation blinded evaluation protocol for our PharmCAT concordance write-up
- Add a "vs GPT-5 over-generation" demo scenario to `comparison_demo`

---

*Continues in subsequent sections — Kerdoncuff 2025 (the Indian wedge), Martin 2017 (academic foundation), Moorjani 2013 + Narasimhan 2019 (population structure), Poplin 2018 (DeepVariant integration), revised technical phasing, and partnership/data-access targets.*

## Part 2 — Kerdoncuff et al. 2025 (Cell)

*50,000 years of Indian evolutionary history — impact on health and disease variation*

**What they built:** Whole-genome sequences of 2,762 individuals from LASI-DAD (Longitudinal Aging Study in India - Diagnostic Assessment of Dementia), age 60+, from 18 states/UTs. **73.2 million autosomal variants.** Sequenced at MedGenome (Bangalore), processed at UPenn. Co-led by Priya Moorjani (UC Berkeley).

**The numbers that matter for Anukriti:**

| Finding | Number | What it means |
|---|---|---|
| **Variants absent from 1000G + gnomAD** | **24M SNVs + 2.2M indels** | Anukriti's KG (sourced from gnomAD) is missing ~33% of Indian variant space |
| **Indian regional groupings** | 6 (North/West/Central/South/Northeast/East) | Our `SuperPopulation.SAS` is too coarse — need 6-way regional split |
| **Languages represented** | ~26 | Indo-European 74%, Dravidian 25% — ancestry tracks linguistic family |
| **Communities represented** | ST 4%, SC 18%, OBC 44%, others 34% | Caste/jati endogamy is a measurable ancestry signal |
| **HBD (homozygosity-by-descent) variation** | High in AHG-related ancestry | Founder effects → elevated homozygous-deleterious-variant burden |
| **BCHE L307P frequency** | 0.28% in LASI-DAD; 8 of 15 carriers in Telangana | Anesthesia muscle-paralysis risk variant **invisible to gnomAD** |
| **Pathogenic ClinVar variants** | 214 | HBB, GJB2, CFTR, PAH, BCHE — recessive-disease-relevant |

**The big architectural implication — founder effects break Hardy-Weinberg:**

Founder effects + endogamy in Indian communities means homozygosity rates are non-Hardy-Weinberg. Our Stage-1 cohort demo (session #14, 100-patient Monte Carlo) currently uses Hardy-Weinberg for diplotype sampling. **For Indian populations specifically, HW underestimates homozygous-PM frequencies in endogamous communities.**

This is a measurable, citeable correction. With HW: 14% SAS-PM for CYP2C19. With founder-effect-corrected HBD assumptions in a high-endogamy community: probably 16–18%. That's a more honest number — and the kind of nuance that takes a research-grade platform from "interesting" to "credible."

**The new wedge story — BCHE L307P:**

> A 64-year-old Vysya woman from Telangana presents for elective cholecystectomy. The anesthesiologist administers succinylcholine for muscle relaxation. She develops prolonged paralysis lasting hours. The cause is BCHE L307P — present in 0.28% of LASI-DAD, enriched in the Vysya community, **absent from gnomAD entirely**. No existing PGx system flags it because it doesn't exist in their reference databases. Anukriti's variant-novelty layer flags it as "population-specific deleterious variant; founder-effect frequency 0.28% in LASI-DAD."

This is a stronger story than CYP2C19 + clopidogrel because:

1. The variant is invisible to competitors
2. The clinical impact is acute and severe (not "increased cardiac event risk over years")
3. The community/regional specificity (Vysya / Andhra Pradesh / Telangana) is exactly the granularity Anukriti's architecture is built for
4. It's directly cited in a top-tier 2025 paper

**Action items:**

- Add `IndianRegion` closed enum with 6 values (NORTH, WEST, CENTRAL, SOUTH, NORTHEAST, EAST)
- Add `CommunityLevel` open extension (ST/SC/OBC + 26 language groups documented in LASI-DAD)
- Add **founder-effect signal** as a new evidence facet in the sufficiency layer (`FOUNDER_EFFECT_BURDEN`)
- Add **variant-novelty layer** — a state in evidence sufficiency for "variant in input but absent from reference databases (gnomAD/1000G)"
- Replace cohort demo's HW-only assumption with **`HBDInformedSampling`** (3rd value in existing `CohortSamplingMethod` enum)
- Add a BCHE / anesthesia / Vysya scenario to the flagship trio demo
- Apply for LASI-DAD data access (Jinkook Lee at USC; co-PI Aparajit Ballav Dey at AIIMS Delhi)

---

*Continues — Martin 2017, population-structure papers, DeepVariant, technical phasing.*

## Part 3 — Martin et al. 2017 (AJHG)

*Polygenic risk prediction across populations — the academic foundation*

**What they showed:** Polygenic risk scores derived from European GWAS are biased when applied to non-Europeans. The bias direction is **unpredictable** — could be higher, lower, or intermediate. Even when choosing the same causal variants and heritability, biases occur. **>50% accuracy drop** in non-EUR populations for schizophrenia PRS. Coalescent-simulation framework (msprime) parameterized by Gravel et al. demographic model.

Eimear Kenny (Mount Sinai) is the corresponding author — same Eimear Kenny who leads the Pangenome Reference Consortium.

**Why this matters for Anukriti:**

This is the canonical academic reference for our core thesis. Our positioning currently leans on the 14% / 2% clopidogrel statistic. **Add Martin 2017 as the population-genetics-level proof** in every positioning doc — it's the formal academic citation behind "EUR-trained models don't transfer."

**Specific technical takeaway — Method 1 is now grounded:**

Session #14 added "Method 4 — cross-ancestry extrapolation hedge" as a sufficiency-decision opt-in. Method 1 (principled cross-ancestry borrowing — hierarchical Bayesian PRS with ancestry-stratified partial pooling) was deferred until Tier 2 data lands.

**Martin 2017's coalescent simulation framework is the methodological scaffolding for Method 1.** We can prototype Method 1 against Martin's simulated populations *before* getting Tier 2 access. This unlocks an 18-month deferral.

**Action items:**

- Add Martin 2017 citation to `PLATFORM.md`, `docs/strategy.md`, all positioning copy
- Prototype Method 1 against Martin's coalescent framework using msprime (no real-data dependency)
- Add a scenario to `evaluation_demo` reproducing Martin's >50% PRS-accuracy-drop for a PGx use case (CYP2D6, multi-allele dosing) — visible "we measure and refuse" demo
- Reach out to Eimear Kenny / Alicia Martin for academic-advisor conversations (Mount Sinai is the natural research home)

---

## Part 4 — Moorjani 2013 (AJHG) + Narasimhan 2019 (Science)

*Indian population structure — anthropological foundation for the new architecture*

**Combined finding:** ANI/ASI mixture happened 1,900–4,200 years ago. ANI = Steppe pastoralist + Indus Periphery. ASI = Indus Periphery + Ancient Hunter-Gatherer (AHG). After mixture: shift to endogamy (consanguineous marriage common, between-group marriage rare). **This endogamy is what creates the founder-effect HBD that Kerdoncuff 2025 measures at scale.**

**Architectural takeaway:**

Indian population structure isn't a single "SAS" cline — it's a **2D structure**:

- Axis 1: ANI/ASI ancestry proportion (geographic gradient north-to-south)
- Axis 2: founder-event severity (community-level endogamy intensity)

Both axes measurably affect pharmacogenomic risk. Our current model has neither axis. The Kerdoncuff 2025 LASI-DAD data has both, with sample-level resolution.

**Action items:**

- Document the ANI/ASI 2D structure in `architecture/pharmacogenomic-kg.md` as the anthropological basis for `IndianRegion` + `CommunityLevel`
- Add Moorjani 2013 + Narasimhan 2019 to academic foundation section of strategy doc

---

## Part 5 — Poplin et al. 2018 (Nature Biotechnology)

*DeepVariant — the upstream caller*

**What it is:** Google/Verily's CNN-based variant caller. Replaces GATK's hand-crafted statistical models with deep learning over read-pileup images. F1 = 99.95% (SNP), 98.98% (indel). >50% fewer errors than next-best algorithm on NA24385.

**Why it's in our reading list:** It's the upstream layer to Anukriti. Anukriti consumes called variants; DeepVariant is the most accurate caller on the market. Our session notes mention a "DeepVariant collaboration pitch drafted."

**Strategic takeaway — the 3-layer compose pitch:**

- **DeepVariant** = high-accuracy variant calling (signal layer)
- **anukriti-pgx-core** = deterministic phenotype calling (interpretation layer)
- **anukriti-swarm** = population-aware reasoning + evidence sufficiency (decision layer)

The three layers compose end-to-end with no overlap. That's the pitch — *"we extend DeepVariant's accuracy story into the population-aware decision layer."*

**Action items:**

- Frame DeepVariant collaboration around 3-layer compose, not feature-overlap
- Run DeepVariant on LASI-DAD samples (when access lands) as Stage-2 deliverable — natural co-publication

---

## Part 6 — The sharpened thesis (post-paper-synthesis)

> **Pharmacogenomic safety equity is a sub-continental, community-level resolution problem — not a "bigger model on diverse data" problem.**
>
> Kerdoncuff 2025 shows 24 million Indian variants are absent from the reference databases every existing PGx system uses. Founder effects in endogamous communities mean homozygous-PM rates aren't predictable from Hardy-Weinberg over super-population frequencies — they require HBD-informed reasoning. The architecture to handle this — closed-enum scope firewalls, evidence sufficiency gating, founder-effect signals, variant-novelty layers — is what Anukriti is. The data needed to populate it is what LASI-DAD, GenomeIndia, and All of Us provide. The downstream consumers — CROs running trials in India, pharma designing global drug labels, hospital systems implementing PGx — are who we sell to.

This thesis is stronger than the previous one because it has:

- A specific numeric scale (24M Indian variants invisible to existing systems)
- A sub-population resolution claim (community-level, not super-population)
- A methodological claim (founder-effect-informed sampling, not Hardy-Weinberg)
- A second wedge story (BCHE / Vysya, not just clopidogrel / SAS)
- Academic citations for every claim (Martin 2017, Kerdoncuff 2025, Moorjani 2013, Narasimhan 2019)

---

*Continues — revised technical phasing, partnership/data-access targets, prioritized backlog.*

## Part 7 — Revised Technical Phasing

The phasing is reordered around two principles: **(1) ship the credibility artifact first** (PharmCAT concordance — already on the existing roadmap), **(2) ship paper-driven extensions before chasing more breadth.**

### Phase A — Credibility (Weeks 1–4) ⚠️ HIGHEST ROI

Goal: convert "nice architecture" to "verifiably correct PGx infrastructure." No new architecture; ship the missing proof points.

| # | Task | Repo | Why |
|---|---|---|---|
| A1 | **`.env` BFG scrub + credential rotation** | `anukriti` | Security blocker. Must precede any public push. ~1 day. |
| A2 | **PharmCAT concordance run + writeup** | `anukriti-pgx-core` + `anukriti_docs/validation/` | GeT-RM 240 + 1000G samples (NA12878/NA19240/HG00096). Gene × sample × caller breakdown. Target ≥95% on common alleles. **Single highest-ROI artifact** — converts architecture into evidence. |
| A3 | **24-recommendation blinded expert eval** (Zack 2026 protocol) | `anukriti-swarm/evaluation/` | Adopt the Zack 2026 evaluation framework as our published bar. 0–10 expert score across 24 recommendations, 3 reviewers, pairwise CPIC concordance. |
| A4 | **Paper-citation pass on positioning docs** | `anukriti-pgx-core/PLATFORM.md` + `docs/strategy.md` + landing | Add Martin 2017, Kerdoncuff 2025, Moorjani 2013, Narasimhan 2019, Zack 2026 citations everywhere claims are made. Convert positioning from "we believe" to "the literature says." |
| A5 | **Split `api.py` and `app.py`** | `anukriti` | Contributor onboarding goes from hostile to reasonable. Already on roadmap. |

**Exit criterion:** PharmCAT concordance table shipped, blinded expert-eval results shipped, every positioning claim has a footnote.

---

*Continues — Phase B (paper-driven extensions), Phase C (data partnerships), Phase D (longer horizon), partnership/contact list.*

### Phase B — Paper-driven architectural extensions (Weeks 5–10)

Goal: make the architecture do what the papers say it should do. Each item is a closed-enum or scope-firewall extension consistent with the existing off-by-default discipline.

| # | Task | Repo | Source paper |
|---|---|---|---|
| B1 | **`IndianRegion` closed enum** (6 values: NORTH/WEST/CENTRAL/SOUTH/NORTHEAST/EAST) | `anukriti-swarm/core/models/population.py` + KG schema | Kerdoncuff 2025 |
| B2 | **`CommunityLevel` open extension point** in KG schema (initial seed: ST/SC/OBC labels + 26 LASI-DAD language groups) | `anukriti-swarm/knowledge_graph/schema.py` | Kerdoncuff 2025 |
| B3 | **`FOUNDER_EFFECT_BURDEN` evidence facet** — 7th value in `ClaimEvidenceFacet` enum + corresponding state in coverage analyzer | `anukriti-swarm/core/evidence_sufficiency/` | Kerdoncuff 2025 + Moorjani 2013 |
| B4 | **`VARIANT_NOVELTY` state in evidence sufficiency** — closed enum: `IN_GNOMAD` / `IN_1000G_ONLY` / `NOVEL_TO_REFERENCE` / `POPULATION_PRIVATE`. New rule (R13?) routes `NOVEL_TO_REFERENCE` to `ESCALATE` instead of generic missing-evidence flow | `anukriti-swarm/core/evidence_sufficiency/` | Kerdoncuff 2025 (24M variants absent from gnomAD) |
| B5 | **`HBDInformedSampling` cohort-sampling method** — 3rd value in existing `CohortSamplingMethod` enum, parameterized by community-level HBD score | `anukriti-swarm/core/simulation/` | Kerdoncuff 2025 + Moorjani 2013 |
| B6 | **BCHE / anesthesia / Vysya scenario** in flagship trio demo | `anukriti-swarm/demos/flagship_trio.py` | Kerdoncuff 2025 |
| B7 | **Method 1 prototype** (hierarchical Bayesian PRS with ancestry-stratified partial pooling) against msprime coalescent simulations | `anukriti-swarm/research/method_1_cross_ancestry/` | Martin 2017 |
| B8 | **GPT-5 over-generation comparison demo** — show our `GenerativeBoundary` blocking the same fabricate-claim failure mode Zack 2026 documents | `anukriti-swarm/demos/comparison_demo.py` | Zack 2026 |
| B9 | **Adopt Zack 2026's evaluation protocol** as the canonical eval — 24 recommendations, 3 reviewers, blinded scoring, pairwise CPIC concordance | `anukriti-swarm/evaluation/` | Zack 2026 |

**Exit criterion:** the architecture has a citeable paper for every new closed enum and a runnable demo for every new wedge example.

**Discipline:** every item lands as a small reviewable PR following the existing session pattern (closed-enum first, off-by-default integration via constructor arg, byte-identical regression for the existing 7 flagship demos).

---

*Continues — Phase C (data partnerships), Phase D (longer horizon), partnership/contact list.*

### Phase C — Data partnerships (Months 2–6, run in parallel with B)

Goal: convert the architecture into a federated-data consumer. These are calendar-bound (application reviews take months), so start now and run in parallel with code work.

| # | Target | Action | Owner | Timeline |
|---|---|---|---|---|
| C1 | **LASI-DAD** (Kerdoncuff 2025 cohort) | Outreach to Jinkook Lee (USC), co-PI Aparajit Ballav Dey (AIIMS Delhi), correspondence Priya Moorjani (Berkeley) | Founder | 1–3 months |
| C2 | **All of Us Researcher Workbench** | Institutional application; tier-2 controlled-access | Founder + institutional sponsor | 2–4 months |
| C3 | **GenomeIndia (FeED)** | Application + data-access agreement | Founder | 3–6 months |
| C4 | **PGxAI Inc.** (Zack 2026 authors) | "We apply, you generate" partnership conversation — `mz@pgx.ai` | Founder | Cold outreach, ~weeks |
| C5 | **DeepVariant / Verily** | Existing pitch — reframe around 3-layer compose (signal/interpretation/decision) | Founder | Re-engage existing thread |
| C6 | **Eimear Kenny / Alicia Martin** (Mount Sinai) | Academic-advisor conversation; Mount Sinai is the natural research home for the population-aware-PGx work | Founder | Cold outreach, ~weeks |
| C7 | **H3Africa DBAC** | Long-term application (African ancestry is the long-term differentiator) | Founder | 3–9 months |

Each application is documented in `anukriti-pgx-core/docs/research-partnerships.md` with status, contact, application URL, and next-action date. **Update that doc whenever a status changes.**

---

### Phase D — Longer horizon (Months 6–12)

Items that depend on Phase C unlocking:

| Item | Depends on |
|---|---|
| **Method 1 with real data** (replace msprime simulations with All of Us / GenomeIndia / LASI-DAD) | C2 / C3 / C1 |
| **Run DeepVariant on LASI-DAD** as Stage-2 proof point + co-publication | C1 + C5 |
| **Community-level frequency tables** populated from LASI-DAD into the KG | C1 |
| **Per-region (6-way India) Hardy-Weinberg vs HBD-corrected comparison** publishable result | C1 |
| **CYP2D6 CNV via Cyrius wrapper** (existing roadmap, not paper-driven) | none |
| **Regulatory posture decision** (RUO / SaMD / IVDR) | independent calendar |

---

*Continues — partnership/contact list, prioritized backlog summary.*

## Part 8 — Outreach contact list (consolidated)

| Contact | Role | Repo connection | Why reach out | Status |
|---|---|---|---|---|
| **Mike Zack** (`mz@pgx.ai`, PGxAI Inc.) | Lead author, Zack 2026 npj DM | Upstream complement (guideline generation) | Partnership: their guidelines feed into our `guidelines/cpic.py` | not yet |
| **Priya Moorjani** (`moorjani@berkeley.edu`, UC Berkeley) | Senior + corresponding, Kerdoncuff 2025 + Moorjani 2013 | Owner of LASI-DAD analysis + Indian population genetics canonical work | LASI-DAD data access + scientific advisor | not yet |
| **Jinkook Lee** (`jinkookl@usc.edu`, USC) | Senior, Kerdoncuff 2025 | LASI-DAD PI on the US side | LASI-DAD data access | not yet |
| **Aparajit Ballav Dey** (`abdey@hotmail.com`, AIIMS Delhi) | Senior, Kerdoncuff 2025 | LASI-DAD PI on the India side | LASI-DAD data access + Indian institutional partnership | not yet |
| **Eimear Kenny** (Mount Sinai, Icahn School of Medicine) | Corresponding, Martin 2017 + Pangenome 2023 | Population-aware GWAS canonical author, Pangenome lead | Academic advisor; Mount Sinai = natural research home | not yet |
| **Alicia Martin** (`armartin@mgh.harvard.edu`, Broad/MGH) | Lead author, Martin 2017 | Method 1 (cross-ancestry borrowing) methodological reference | Methodological collaboration on Method 1 prototype | not yet |
| **Mark DePristo / DeepVariant team** (Verily) | Senior, Poplin 2018 | Upstream variant caller | 3-layer compose pitch (signal → interpretation → decision) | not yet |
| **Andrea Gaedigk** (`agaedigk@cmh.edu`, Children's Mercy KC / PharmVar) | PharmVar steward, StarTRAC 2025 + pharmacoequity 2023 | Nomenclature ground truth for `anukriti-pgx-core/anukriti_pgx_core/calling/` | Implementer alignment + South Asian data pointers | ✅ initial exchange done 2026-05-15 — see [`partnerships/01-Gaedigk-PharmVar-implementer-alignment.md`](partnerships/01-Gaedigk-PharmVar-implementer-alignment.md) |
| **Andrew Somogyi** (`andrew.somogyi@adelaide.edu.au`, Univ. of Adelaide) | Referred by Gaedigk as a connector who "may be able to direct to other people" | Possible bridge to South Asian PGx authors | South Asian-focused PGx pointers — **highest-priority of the three Gaedigk referrals** | queued |
| **Chonlaphat Sukasem** (`chonlaphat.suk@mahidol.ac.th`, Mahidol University) | Referred by Gaedigk; Thai PGx work | Adjacent-region (SEA) PGx, methodologically transferable | Thai PGx + adjacent-region triangulation | queued |
| **Martin Kennedy** (`martin.kennedy@otago.ac.nz`, Univ. of Otago) | Referred by Gaedigk; native New Zealander PGx | Methodological reference for population-specific allele characterization done at small-team scale | Methodological reference for under-represented-population PGx | queued |

---

## Part 9 — Next 30 days, prioritized

If everything else is dropped, do these 5 things in order:

1. **Week 1: `.env` BFG scrub + credential rotation** (A1) — security blocker, ~1 day
2. **Weeks 1–2: PharmCAT concordance run** (A2) — single highest-ROI artifact, converts architecture into evidence
3. **Week 2: Outreach emails to PGxAI Inc., LASI-DAD team, Mount Sinai** (C1, C4, C6) — calendar-bound, cannot wait
4. **Weeks 2–3: Citation pass on positioning docs** (A4) — cheap, makes the architecture defensible
5. **Weeks 3–4: BCHE/Vysya scenario in flagship demo** (B6) — visible new wedge, no architectural risk; uses existing flagship-demo pattern

Everything else (Indian sub-population layer, founder-effect facet, variant-novelty layer, Method 1 prototype) is Phase B and starts after these 5 land.

---

## Cross-references

- `anukriti_docs/PLATFORM_ANALYSIS_2026-05-11.md` — pre-paper-synthesis platform analysis (this doc supersedes its "what to do" section)
- `anukriti-swarm/.project-status.md` — living session log; next session's #15 work should be Phase A items
- `anukriti-pgx-core/docs/research-partnerships.md` — running status of Phase C items
- `anukriti_docs/papers/README.md` — paper index (this doc cites all 6 papers there)
- `anukriti-pgx-core/docs/strategy.md` — moat + 3-tier data strategy (this doc updates it with paper citations)

---

*This document is the single source of truth for "how the papers change the idea and the build order." Update when (a) a paper is added/removed from the reading list, (b) a phase item completes, (c) an outreach contact yields a response, (d) a deferred item gets unblocked.*
