# Evidence Level + LLM-Grounded Explain — Multi-Repo Plan

> **Audience:** founder + every engineering session that touches this feature.
>
> **Last updated:** 2026-05-26
>
> **Status:** Plan landed 2026-05-26. **8 of 19 tasks shipped end-to-end** in the same session (T1–T6 + T13 + T15 + T18 partial). pgx-core 0.3.0 published to PyPI; Azure backend redeployed to revision 15; live frontend serves engine-truth `evidence_level: "A"` badges. **11 tasks remain** — see the [What landed 2026-05-26](#what-landed-2026-05-26) section below for the precise shipped-vs-open breakdown. Remaining work fits ~3 follow-up sessions (most of the heavy plumbing is done).
>
> **Companion docs:**
>   - [`IWPC_VALIDATION_DEEP_DIVE.md`](IWPC_VALIDATION_DEEP_DIVE.md) — engine validation; §5a is what `evidence_level` makes auditable in the UI
>   - [`DETERMINISTIC_ENGINE_DEEP_DIVE.md`](DETERMINISTIC_ENGINE_DEEP_DIVE.md) — where the CPIC level data lives
>   - [`THREE_REPO_INTEGRATION_DEEP_DIVE.md`](THREE_REPO_INTEGRATION_DEEP_DIVE.md) — why the LLM endpoint goes through swarm, not directly into api

---

## TL;DR

Anna's spec asked for two user-facing changes:

1. A visual evidence-level badge (CPIC A / B / C) on every recommendation
2. An `/api/v1/llm-context` endpoint that returns a grounded, citation-checked LLM explanation

This plan resolves three architectural questions that the spec leaves
implicit, and sequences the work across `anukriti-pgx-core`,
`anukriti-swarm`, `anukriti-api`, and `anukriti-main` so each session
has clear scope.

**The three resolved questions:**

| Question | Answer |
|---|---|
| Where does the LLM endpoint live? | HTTP shape lives in `anukriti-api`, but the LLM call itself lives in `anukriti-swarm` (it must go through `GenerativeBoundary`, not bypass it) |
| Where does `CitationValidator` live? | `anukriti-swarm/core/runtime/`, alongside `GenerativeBoundary` — closed-enum verdicts, named refusals, fits the existing R/V/U pattern |
| Which "evidence level" does the badge show? | CPIC per-recommendation level (A/B/C/D) — what clinicians look at first; published per gene-drug pair on cpicpgx.org and accessible via the CPIC API |

**Sequencing:** pgx-core v0.3.0 → swarm CitationValidator + LLMNarrator → anukriti-api endpoint → anukriti-main UI. The frontend `<EvidenceBadge>` component is the only piece that ships in parallel because it just renders a literal level prop.

---

## What landed 2026-05-26

This plan was written and partially executed in the same session.
The status of every task is captured below — refer to this section
before starting any remaining work.

| Task | Status | Commit / artefact |
|---|---|---|
| **T1** Pin CPIC recommendation-level table | ✅ shipped | `anukriti-pgx-core` `2e5a121` (CPIC_RECOMMENDATION_LEVELS_v2024.01.json, 25 pairs all level A) |
| **T2** Add `evidence_level` field to public dataclasses | ✅ shipped | `anukriti-pgx-core` `2e5a121` (PhenotypeInference / Diplotype / GenotypeCall) |
| **T3** Resolver `recommendation_level.py` | ✅ shipped | `anukriti-pgx-core` `2e5a121` (level_for + details_for, never raises) |
| **T4** Wire `drug=` kwarg through engine + callers | ✅ shipped | `anukriti-pgx-core` `2e5a121` |
| **T5** Tests | ✅ shipped | `anukriti-pgx-core` `2e5a121` (76/76 pass; was 50/50) |
| **T6** v0.3.0 release ceremony | ✅ shipped | tag `v0.3.0`; PyPI published 2026-05-26T13:08:28Z |
| **T7** `CitationValidator` in swarm `core/runtime/` | ⏳ open | — |
| **T8** `LLMNarrator` in swarm `ai/narrative/` | ⏳ open | — |
| **T9** `SwarmRuntime` synthesis_mode wiring | ⏳ open | — |
| **T10** unit tests for T7+T8+T9 | ⏳ open | — |
| **T11** `demos/llm_grounded_demo.py` | ⏳ open | — |
| **T12** `POST /api/v1/llm-context` endpoint | ⏳ open | (blocked on T7–T9) |
| **T13** Surface `evidence_level` on `/runs` response | ✅ shipped | `anukriti-api` `93d7a59` (per-patient path) + `4170a07` (cohort `/from-samples` path); also fixed a pre-existing latent attribute-error bug in the simvastatin/warfarin paths |
| **T14** Smoke tests for T12 | ⏳ open | (blocked on T12) |
| **T15** `<EvidenceBadge>` component | ✅ shipped | `anukriti-main` `3d56b56` (initial), `87937a2` (consume row.evidence_level), `6132628` (retire helper — truth-from-engine) |
| **T16** `<EvidenceTooltip>` "How do we know this?" | ⏳ open | — |
| **T17** `<LlmExplanationPanel>` with citations | ⏳ open | (blocked on T12) |
| **T18** Wire `<EvidenceBadge>` into all result-displaying surfaces | 🟡 partial | Wired into `<ResultsTable>` only. Still pending: Simulation.jsx, TrialDecisionCard.jsx, ConfidencePanel.jsx (each is a 2-line addition) |
| **T19** Vitest snapshots | ⏳ open | — |

**End-to-end live trace verified** (the full chain from CPIC API
snapshot → engine → caller → adapter → api response → frontend
row mapper → `<EvidenceBadge>`):

```
api.cpicpgx.org/v1/pair
   → CPIC_RECOMMENDATION_LEVELS_v2024.01.json
   → PhenotypeEngine.infer(drug='clopidogrel')
   → CYP2C19Caller(...).call(snps, drug='clopidogrel')
   → call_diplotype('clopidogrel', snps)  [adapter]
   → /runs/from-samples response.samples[i].evidence_level = 'A'
   → SimulationContext row mapper
   → <ResultsTable> reads row.evidence_level
   → <EvidenceBadge level="A" />  renders "A · Strong Evidence"
```

Probe the live api with `POST /runs/from-samples
{"workflow":"clopidogrel","sample_ids":["NA12891"]}` to verify;
the response payload's `samples[0].evidence_level` will be `"A"`.

**Companion deploys**:

- PyPI: `anukriti-pgx-core==0.3.0` published from tag `v0.3.0`
- Azure Container App `anukriti-api` revision 15 active with image
  `git-4170a07-2cd068-2e5a12`
- Vercel: `https://product.anukritiai.com` rebuilt with the new
  bundle `index-Dm__d9Na.js` containing `EvidenceBadge`

**What remained out of scope today** (deferred deliberately):

- F-10 CYP2C9 functionality table fix → v0.4.0 (held until
  PharmCAT verification per CP-5 in `anukriti/CLINICAL_GRADE_ROADMAP.md`)
- The `anukriti-chemistry` library was bootstrapped (commit
  `4a2252c`); its swarm integration depends on T8 (`LLMNarrator`)
- T7–T12, T14, T16, T17, T19 — sequential or T12-blocked

The full session narrative including these deferrals is in
[`SESSION_RESUME_2026-05-26.md`](SESSION_RESUME_2026-05-26.md).

---

## Table of contents

0. [What landed 2026-05-26](#what-landed-2026-05-26)
1. [What Anna asked for](#1-what-anna-asked-for)
2. [Three architectural questions, resolved](#2-three-architectural-questions-resolved)
3. [Per-repo task breakdown](#3-per-repo-task-breakdown)
4. [Sequencing — what blocks what](#4-sequencing--what-blocks-what)
5. [Acceptance criteria per task](#5-acceptance-criteria-per-task)
6. [Effort estimate per task](#6-effort-estimate-per-task)
7. [How this slots into the existing v0.3.0 + CP-5 + F-10 work](#7-how-this-slots-into-the-existing-v030--cp-5--f-10-work)
8. [What ships in this session vs the next 5 sessions](#8-what-ships-in-this-session-vs-the-next-5-sessions)

---

## 1. What Anna asked for

### Backend (her spec said `anukriti-api`)

1. **`POST /api/v1/llm-context`** — receives patient SNPs + drug/workflow,
   queries the variant DB for relevant records, formats a structured
   context block, calls Claude/OpenAI with a grounding prompt, runs a
   citation-validation layer, returns LLM explanation + citations +
   evidence levels + uncited-claim flags.
2. **Add `evidence_level` to all recommendation payloads** — every
   endpoint returning a CPIC recommendation surfaces:
   ```json
   {
     "recommendation": "...",
     "evidence_level": "A",
     "cpic_version": "2023",
     "pmid": "12345678"
   }
   ```

### Frontend (`anukriti-main`)

3. **`<EvidenceBadge level="A" />`** — coloured badge on every
   recommendation: A green / B yellow / C orange / D grey.
4. **LLM explanation panel with inline citations** — clicking
   "Explain" calls `/api/v1/llm-context`, renders the explanation
   with `[CPIC 2023, PMID:12345]` style citations, flags any
   uncited claim with a yellow warning.
5. **"How do we know this?" tooltip** — info icon on each
   recommendation card; on hover/click shows evidence level + CPIC
   version + PMID + population the frequency data came from.

---

## 2. Three architectural questions, resolved

### Q1 — Where does the LLM endpoint live?

Anna's spec said `anukriti-api`. That's right for the HTTP surface;
it's wrong for the LLM call itself. Reasoning:

- The platform's central invariant is **"no LLM in the decision path"**.
  `anukriti-swarm/core/orchestrator/boundary.py::GenerativeBoundary`
  enforces this in code with four forbidden actions: `infer_phenotype`,
  `override_recommendation`, `bypass_verification`, `fabricate_claim`.
  Every existing LLM call routes through it.
- Adding the LLM call directly into `anukriti-api` would create a
  **second LLM path that bypasses the boundary**. That contradicts the
  invariant, which is the platform's main differentiator vs.
  generic-RAG products.
- The swarm already has `ai/narrative/generator.py::NarrativeGenerator`
  (Stage 5 of `SwarmRuntime.run()`), guarded by `GenerativeBoundary`.
  This is where the LLM call belongs — the api just calls into it
  with a new `synthesis_mode="llm_grounded"` opt-in flag.

**Decision:** the api endpoint adapts the request shape and calls
`SwarmRuntime.run()` with the new mode. The LLM call, the grounding
prompt, the citation validator, the boundary enforcement — all live
in swarm.

### Q2 — Where does `CitationValidator` live?

Anna described it as "step 4 of the endpoint": before displaying any
LLM response, check that every claim cites a provided record. This is
a post-synthesis safety check and naturally lives next to
`GenerativeBoundary` in `anukriti-swarm/core/runtime/`.

The validator follows the existing R/V/U named-refusal pattern:

- **Closed-enum verdicts**: `ALL_CITED`, `MISSING_CITATIONS`,
  `FABRICATED_CITATION`, `EMPTY_RESPONSE`, `MALFORMED`
- **Named refusal IDs**: `C1` through `C5` (mirroring the existing
  `R1..R12`, `V1..V10`, `U1..U9` rule taxonomies)
- **Frozen `CitationValidationTrace`**: auditable record per call
  (input record set, sentences, per-sentence verdict, missing-citation
  list, final verdict)

**Decision:** `CitationValidator` lives at
`anukriti-swarm/core/runtime/citation_validator.py`. Trace shape mirrors
the existing `EvidenceSufficiencyTrace`. Off-by-default; opt-in via
`SwarmRuntime(citation_validator=CitationValidator())`.

### Q3 — Which "evidence level" does the badge show?

CPIC publishes evidence at three different granularities, all real:

1. **Per-allele functionality strength** — Definitive / Strong /
   Moderate / Limited / Uncertain. Already pulled into the validation
   repo: `data/cpic_canonical/cpic_cyp2c9_alleles.json`. Captures
   how confident CPIC is about each allele's *function call*.
2. **Per-recommendation CPIC level** — A / B / C / D. Published per
   gene-drug pair on
   [cpicpgx.org/genes-drugs](https://cpicpgx.org/genes-drugs).
   Captures how *clinically actionable* the gene-drug interaction is.
3. **Per-PhenotypeInference confidence** — already in pgx-core's
   dataclass as a float; caller-internal.

Anna's spec ("Level A → green, Strong Evidence") is unambiguously **#2 —
per-recommendation CPIC level**. That's what clinicians look at first.

**Decision:** the typed `evidence_level` field on
`PhenotypeInference` (and on `final_recommendation` in the api response
payload) is the per-recommendation CPIC level. The other two stay
where they are; per-allele strength surfaces in the "How do we know
this?" tooltip alongside the level.

**Sourcing:** the CPIC API endpoint
`https://api.cpicpgx.org/v1/recommendation` returns a `strength` field
on each recommendation row. We snapshot it once and pin it as a JSON
table in `anukriti_pgx_core/phenotype/tables/CPIC_RECOMMENDATION_LEVELS_v2024.json`.

**All three workflows currently shipped are CPIC level A:**

| Workflow | Genes | Level | Source |
|---|---|---|---|
| Clopidogrel | CYP2C19 | **A** | CPIC 2022 (PMID 35034351) |
| Warfarin | CYP2C9 + VKORC1 | **A** | CPIC 2017 (PMID 28198005) |
| Simvastatin | SLCO1B1 | **A** | CPIC 2022 statins guideline |

Future-shipped workflows (codeine/CYP2D6, carbamazepine/HLA-B*15:02,
fluoropyrimidines/DPYD) are also Level A — the badge can default to
A for the foreseeable workflow set, and gracefully render any level
when the data is plumbed end-to-end.

---

## 3. Per-repo task breakdown

### `anukriti-pgx-core` (v0.3.0 — same release as F-10 CYP2C9 fix)

Repo: [`AnukritiAi-hq/anukriti-pgx-core`](https://github.com/AnukritiAi-hq/anukriti-pgx-core)

**T1. Pin a CPIC recommendation-level table.**

- File: `anukriti_pgx_core/phenotype/tables/CPIC_RECOMMENDATION_LEVELS_v2024.json`
- Source: `https://api.cpicpgx.org/v1/recommendation`
- Schema: `{ "<gene>__<drug>": { "level": "A"|"B"|"C"|"D", "cpic_version": "...", "pmid": "...", "guideline_url": "..." } }`
- Add provenance entry to `CPIC_PROVENANCE.json`.

**T2. Add `evidence_level` field to public dataclasses.**

- File: `anukriti_pgx_core/types.py`
- `PhenotypeInference.evidence_level: str = ""` (defaults to empty
  string for safety; populated when a drug context is provided).
- `Diplotype.evidence_level: str = ""` (passes through from the chained
  `PhenotypeInference`).
- `GenotypeCall.evidence_level: str = ""` (same).
- Frozen dataclass; new field is **additive only**, no semver bump
  required for existing callers.

**T3. Resolver: `phenotype/recommendation_level.py`.**

- New module: `anukriti_pgx_core/phenotype/recommendation_level.py`
- One function: `level_for(gene: str, drug: str | None) -> str`
- Returns `"A"` / `"B"` / `"C"` / `"D"` / `""` (empty for unknown
  gene-drug pair; never raises).
- Loads the JSON table once, lazily.

**T4. Wire `evidence_level` into engine output paths.**

- `phenotype/engine.py` — `PhenotypeEngine.infer(gene, a1, a2,
  drug=None)` accepts an optional `drug` kwarg; populates
  `evidence_level` on the returned `PhenotypeInference`.
- `calling/base.py` — `GeneCaller.call(variants, drug=None)` and
  `GenotypeCaller.call(variants, drug=None)` accept the same kwarg,
  pass it through to the chained phenotype call.
- All existing call sites that don't pass `drug=` get the empty-string
  default — fully backwards-compatible.

**T5. Tests.**

- `tests/test_recommendation_level.py` — 5 cases covering CYP2C19+clopidogrel
  (A), CYP2C9+VKORC1+warfarin (A), SLCO1B1+simvastatin (A), unknown
  gene (empty), unknown drug for known gene (empty).
- Update `tests/test_pinned_star_alleles.py` regression cases to
  pass `drug=` and assert `evidence_level == "A"` for the three
  shipped workflows.

**T6. Release v0.3.0.**

- Bumps: `version.py`, `pyproject.toml`, `CHANGELOG.md` `[Unreleased]` → `[0.3.0]`.
- Same release also lands the **F-10 CYP2C9 fix** ([`anukriti-pgx-core/PROJECT_CONTEXT.md` F-10](https://github.com/AnukritiAi-hq/anukriti-pgx-core/blob/main/PROJECT_CONTEXT.md)).
- Tag → push → OIDC publishes to PyPI.
- Re-run the IWPC validation against `anukriti-pgx-core==0.3.0`;
  expect Q1 monotonicity unchanged, audit match rates 100%, and the
  IWPC results CSV now carries an `evidence_level` column populated
  with `A` for warfarin rows.

---

### `anukriti-swarm`

Repo: [`AnukritiAi-hq/anukriti-swarm`](https://github.com/AnukritiAi-hq/anukriti-swarm)

**T7. `CitationValidator` — new module.**

- File: `core/runtime/citation_validator.py`
- Closed-enum `CitationVerdict`: `ALL_CITED`, `MISSING_CITATIONS`,
  `FABRICATED_CITATION`, `EMPTY_RESPONSE`, `MALFORMED`.
- Closed-enum `CitationRule`: `C1` (uncited claim), `C2` (citation
  not in provided record set), `C3` (empty response), `C4` (malformed
  citation token), `C5` (all clean).
- Public method: `validate(text: str, evidence_records:
  list[EvidenceRecord]) -> CitationValidationTrace`.
- Trace shape mirrors `EvidenceSufficiencyTrace`: per-sentence verdict,
  full audit-log ready.
- Closed parsing rules — claim sentence ends in `.`, `?`, or `!`;
  citation token format `[<source>, <id>]`. Anything else → `C4`.

**T8. `LLMNarrator` — opt-in, grounded path.**

- New module: `ai/narrative/llm_narrator.py`
- Takes a `RetrievalResult` (already exists in
  `retrieval/evidence/synthesizer.py`), formats the structured
  context block, calls Claude or Gemini with the grounding prompt,
  returns an `LLMNarrative(text, citations, validation_trace)`.
- The grounding prompt is a frozen template literal:
  *"Reason only from the data below. Every claim must end with
  a citation in the form `[<source>, <id>]` referencing one of
  the provided records. Do not introduce drugs, genes, or
  recommendations not present in the data."*
- Wraps the LLM call in `GenerativeBoundary.guard_synthesis`
  (existing); fabricated-claim raises propagate.

**T9. `SwarmRuntime` integration.**

- File: `core/runtime/runtime.py`
- New optional kwarg `synthesis_mode: Literal["template", "llm_grounded"]
  = "template"`.
- When `"llm_grounded"`: route Stage 5 through `LLMNarrator` instead
  of the deterministic `NarrativeGenerator`. `CitationValidator` runs
  post-synthesis. Validation failure → fall back to deterministic
  narrative + named-refusal `C1`/`C2` in the trace.
- Off-by-default; preserves all 7 byte-locked flagship demo signatures.

**T10. Tests.**

- `tests/unit/test_citation_validator.py` — every C-rule fires on
  the right input. Edge cases: zero claims, all claims uncited,
  citation pointing to a record not in the set, malformed token.
- `tests/unit/test_llm_narrator.py` — uses a mock LLM client (the
  real Claude/Gemini call only runs in integration tests opt-in
  via env var).
- `tests/integration/test_swarm_runtime_llm_grounded.py` — full
  Stage 5 lifecycle; flagship signature regression on `template`
  mode unchanged (byte-identical).

**T11. New named-refusal demo.**

- `demos/llm_grounded_demo.py` — runs the full lifecycle with an
  intentionally-fabricated LLM response, shows the C2 refusal firing
  and falling back to deterministic narrative.

---

### `anukriti-api`

Repo: `AnukritiAi-hq/anukriti-api`

**T12. New endpoint `POST /api/v1/llm-context`.**

- File: `app/routers/llm_context.py` (new router; mounted from `app/main.py`)
- Request shape:
  ```json
  {
    "workflow": "clopidogrel",
    "population": "SAS",
    "snps": [{"id": "rs4244285", "genotype": "AA"}, ...],
    "max_records": 20
  }
  ```
- Response shape:
  ```json
  {
    "run_id": "run_...",
    "explanation": "...",
    "citations": [
      {"token": "[CPIC, PMID:35034351]", "record_id": "...", "source": "CPIC", "url": "..."}
    ],
    "evidence_level": "A",
    "cpic_version": "2022.1",
    "validation": {"verdict": "ALL_CITED", "uncited_claims": []}
  }
  ```
- Internally: build a `UnifiedExecutionContext`, call
  `SwarmRuntime.run()` with `synthesis_mode="llm_grounded"`, project
  the `LLMNarrative` output to the response shape.
- Auth: same `Authorization: Bearer <api_key>` middleware as `/runs`.
- Rate limit: same `slowapi` config as `/runs`; `/api/v1/llm-context`
  is more expensive (LLM call) so set a tighter per-key quota.

**T13. Surface `evidence_level` on `/runs` response.**

- File: `app/routers/runs.py` line ~440-450 (the per-sample row builder).
- After `phenotype = details[primary_gene]["phenotype"] if primary_gene else None`,
  add `evidence_level = details[primary_gene].get("evidence_level", "")`.
- Add to per-sample row dict.
- Backwards-compatible: existing consumers that don't read the field
  still work.

**T14. Tests.**

- `tests/test_llm_context_smoke.py` — end-to-end with mocked LLM client
  (no real Claude/Gemini call); asserts validation-trace shape and
  citation fields.
- `tests/test_runs_smoke.py` — extend existing test to assert
  `evidence_level` appears in `/runs` response per-sample rows.

---

### `anukriti-main`

Repo: [`Abm32/anukriti-main`](https://github.com/Abm32/anukriti-main) (the Base44 frontend)

**T15. `<EvidenceBadge level="A" />` component (this session).**

- File: `src/components/shared/EvidenceBadge.jsx`
- Stateless. Takes `level: "A"|"B"|"C"|"D"|""` and `size?: "sm"|"md"`.
- Renders a Radix-styled badge with Tailwind classes:
  - A → green (bg-green-100 text-green-800 border-green-300), label "Strong Evidence"
  - B → yellow (bg-yellow-100 text-yellow-800 border-yellow-300), label "Moderate Evidence"
  - C → orange (bg-orange-100 text-orange-800 border-orange-300), label "Limited Evidence"
  - D → grey (bg-gray-100 text-gray-700 border-gray-300), label "No Recommendation"
  - Empty / null → renders nothing (graceful degradation when payload
    doesn't yet carry the field).
- Uses existing `lucide-react` icon `<Award>` for A, `<ShieldCheck>` for
  B, `<AlertCircle>` for C.
- No prop validation libraries — match existing component style
  (the project uses inline JSDoc).

**T16. `<EvidenceTooltip>` — "How do we know this?".**

- File: `src/components/shared/EvidenceTooltip.jsx`
- Uses existing `@radix-ui/react-tooltip`.
- Props: `level`, `cpicVersion`, `pmid`, `population`, `pharmvarTable`.
- Renders an `<Info>` icon; on hover/click shows a card with all
  four fields + a "Read CPIC guideline" link.

**T17. `<LlmExplanationPanel>` — replaces or augments existing `<LlmExplainer>`.**

- File: `src/components/results/LlmExplanationPanel.jsx`
- Already exists as `<LlmExplainer>` — extend with citation rendering.
- Props: `runId`, `workflow`, `snps`, `population`.
- Calls `POST /api/v1/llm-context` via existing `lib/api.js`.
- Renders the `explanation` text with citation tokens transformed into
  inline link badges (`<sup className="...">[CPIC, PMID:35034351]</sup>`).
- Shows uncited claims with a yellow `<AlertTriangle>` warning flag.
- Loading state via existing `<Skeleton>` Radix primitive.
- Error state shows the named-refusal rule ID (`C1`..`C5`) when
  validation fails.

**T18. Wire `<EvidenceBadge>` into result-displaying surfaces.**

- `src/pages/Results.jsx` — render `<EvidenceBadge level={result.evidence_level || "A"} />`
  next to the recommendation text in `<ResultsTable>` rows. Default
  to `"A"` for the three shipped workflows so the visual is correct
  before the api/pgx-core work lands.
- `src/pages/Simulation.jsx` — same pattern in the per-cohort
  recommendation card.
- `src/components/results/TrialDecisionCard.jsx` — top-right badge.
- `src/components/results/ConfidencePanel.jsx` — pair with the
  existing confidence display.

**T19. Tests.**

- `src/components/shared/__tests__/EvidenceBadge.test.jsx` — Vitest +
  React Testing Library. Render each level, assert the right colour
  class and label appear; assert empty / null prop renders nothing.
- Stretch: snapshot test for the LLM panel with mocked `/api/v1/llm-context`
  response.

---

## 4. Sequencing — what blocks what

```
┌──────────────────────────────────────────┐
│  pgx-core v0.3.0                         │
│  ─ T1 CPIC level table                   │
│  ─ T2 evidence_level field on dataclasses│
│  ─ T3 resolver                           │
│  ─ T4 engine wiring                      │
│  ─ T5 tests                              │
│  ─ T6 release to PyPI                    │
│  ─ (also fixes F-10 CYP2C9 bugs)         │
└─────────────┬────────────────────────────┘
              │  blocks T13, T14
              ▼
┌──────────────────────────────────────────┐    ┌──────────────────────────────┐
│  swarm — LLM grounded path               │    │  anukriti-main (parallel)    │
│  ─ T7  CitationValidator                 │    │  ─ T15 <EvidenceBadge>       │
│  ─ T8  LLMNarrator                       │    │  ─ T18 wire into Results     │
│  ─ T9  SwarmRuntime synthesis_mode       │    │       (uses default "A"      │
│  ─ T10 tests                             │    │        until api carries it) │
│  ─ T11 demo                              │    └──────────────────────────────┘
└─────────────┬────────────────────────────┘
              │  blocks T12 (the api endpoint
              │           internally calls swarm)
              ▼
┌──────────────────────────────────────────┐
│  anukriti-api                            │
│  ─ T12 POST /api/v1/llm-context          │
│  ─ T13 evidence_level on /runs response  │
│  ─ T14 tests                             │
└─────────────┬────────────────────────────┘
              │  unblocks T16, T17
              ▼
┌──────────────────────────────────────────┐
│  anukriti-main (post-api)                │
│  ─ T16 <EvidenceTooltip>                 │
│  ─ T17 <LlmExplanationPanel> (extends    │
│        existing <LlmExplainer>)          │
│  ─ T19 tests                             │
└──────────────────────────────────────────┘
```

`<EvidenceBadge>` (T15) ships in parallel because it just renders a
literal level prop. It works correctly today by defaulting to `"A"`
for the three shipped workflows; once T13 lands, it picks up the
real value from the api payload automatically.

Everything else is sequential. The api endpoint (T12) is the
**second-to-last** piece, not the first — Anna's "start with the
backend" instinct is right that the badge depends on payload data,
but pgx-core has to surface that data first.

---

## 5. Acceptance criteria per task

Each task ships with a concrete done definition. Same shape as the
existing `F-10` and `CP-5` entries elsewhere on the platform.

| Task | Done when |
|---|---|
| T1 | `CPIC_RECOMMENDATION_LEVELS_v2024.json` exists with at least the 5 currently-shipped workflows; provenance entry in `CPIC_PROVENANCE.json` |
| T2 | `PhenotypeInference`, `Diplotype`, `GenotypeCall` carry `evidence_level: str = ""`; existing `pytest` in pgx-core green |
| T3 | `level_for("CYP2C19", "clopidogrel") == "A"`; unknown pair returns `""` not raises |
| T4 | `engine.infer("CYP2C9", "*1", "*1", drug="warfarin").evidence_level == "A"` |
| T5 | 5 new test cases pass; existing 50/50 tests still pass |
| T6 | `pip install anukriti-pgx-core==0.3.0` works; IWPC validation re-runs cleanly; CPIC audit returns 100% match (closes F-10 + this work in one release) |
| T7 | `CitationValidator.validate("X is true [CPIC, PMID:1].", [r1])` returns `ALL_CITED`; uncited claim returns `MISSING_CITATIONS` + named rule `C1` |
| T8 | `LLMNarrator.narrate(retrieval_result)` returns `LLMNarrative` with non-empty text + citations; mock-LLM test green |
| T9 | `SwarmRuntime(synthesis_mode="llm_grounded").run(ctx)` returns a `UnifiedExecutionReport` with the LLM narrative and the validation trace; `synthesis_mode="template"` regression byte-identical to existing 7 flagship demos |
| T10 | New tests pass; 244 → ~260 pytest count; no flagship regression |
| T11 | `demos/llm_grounded_demo.py` runs, shows C2 refusal + fallback |
| T12 | `curl POST /api/v1/llm-context -d ...` returns the documented shape; LLM-mocked smoke test green |
| T13 | `/runs` per-sample rows carry `evidence_level: "A"` for the three shipped workflows |
| T14 | `pytest tests/test_llm_context_smoke.py` green |
| T15 | `<EvidenceBadge level="A" />` renders green + "Strong Evidence" |
| T16 | `<EvidenceTooltip>` renders all four fields + the CPIC link |
| T17 | Citation tokens render as inline link badges; uncited claims show yellow warning; failure shows named refusal C-rule |
| T18 | At least 4 result-displaying surfaces wired |
| T19 | Vitest passes |

---

## 6. Effort estimate per task

| Repo | Task | Effort | Cumulative |
|---|---|---|---|
| pgx-core | T1–T6 (incl. F-10 fix) | 1.5 days | 1.5 days |
| swarm | T7 CitationValidator | 0.5 day | 2.0 days |
| swarm | T8 LLMNarrator | 0.5 day | 2.5 days |
| swarm | T9 SwarmRuntime mode | 0.5 day | 3.0 days |
| swarm | T10 tests + T11 demo | 0.5 day | 3.5 days |
| api | T12 + T13 + T14 | 0.5 day | 4.0 days |
| frontend | T15 EvidenceBadge | 1 hour | (in parallel) |
| frontend | T16 EvidenceTooltip | 0.5 day | 4.5 days |
| frontend | T17 LlmExplanationPanel | 0.5 day | 5.0 days |
| frontend | T18 wire-in sweep | 1 hour | 5.0 days |
| frontend | T19 tests | 0.5 day | 5.5 days |

**Total: 5.5 days of focused work** across 4 repos, 5 sessions if the
splits are clean (pgx-core → swarm × 2 → api → frontend × 2).

---

## 7. How this slots into the existing v0.3.0 + CP-5 + F-10 work

Three pieces of work are now scheduled for `anukriti-pgx-core==0.3.0`:

1. **F-10** ([backlog](https://github.com/AnukritiAi-hq/anukriti-pgx-core/blob/main/PROJECT_CONTEXT.md#f-10--fix-cyp2c9-phenotype-table-to-match-canonical-cpic-v030-open)) — fix the CYP2C9 functionality table to match canonical CPIC; close the audit findings disclosed in [`IWPC_VALIDATION_DEEP_DIVE.md` §5a](IWPC_VALIDATION_DEEP_DIVE.md#5a-what-the-cpic-table-audit-revealed-2026-05-26).
2. **T1–T5** (this plan) — add `evidence_level` field + CPIC level
   table + resolver + engine wiring + tests.
3. **T6** (this plan) — release v0.3.0.

These ship together as one release. The acceptance gate is the
combined IWPC re-validation (Q1 monotonic, 99/467 still robust) +
CPIC audit (100% match on all three surfaces) + per-sample
`evidence_level == "A"` for the three shipped workflows.

CP-5 (PharmCAT concordance) ([roadmap](https://github.com/Abm32/Synthatrial/blob/clinical-grade-pgx/CLINICAL_GRADE_ROADMAP.md))
is independent of this work and stays on its own track.

---

## 8. What ships in this session vs the next 5 sessions

**This session (2026-05-26):**

- ✅ This plan doc
- ✅ T15 — `<EvidenceBadge>` component in `anukriti-main`
- ✅ T18 (partial) — wired into `Results.jsx` so the design intent is
  visible

**Next 5 sessions:**

| Session | Repo | Tasks |
|---|---|---|
| #1 | pgx-core | T1–T6 + F-10 (= v0.3.0 release; IWPC re-validation; audit re-run) |
| #2 | swarm | T7 CitationValidator + T10 tests |
| #3 | swarm | T8 LLMNarrator + T9 SwarmRuntime synthesis_mode + T11 demo |
| #4 | api | T12 endpoint + T13 evidence_level passthrough + T14 tests |
| #5 | frontend | T16 EvidenceTooltip + T17 LlmExplanationPanel + T18 sweep + T19 tests |

Each session is one repo's worth of clearly-scoped work, reproducible
from the task definitions and acceptance criteria above.

---

## Continuation pointers

- For the engine bug list this plan's v0.3.0 release closes:
  [`anukriti-pgx-core/PROJECT_CONTEXT.md` F-10](https://github.com/AnukritiAi-hq/anukriti-pgx-core/blob/main/PROJECT_CONTEXT.md#f-10--fix-cyp2c9-phenotype-table-to-match-canonical-cpic-v030-open)
- For the validation methodology this plan extends:
  [`IWPC_VALIDATION_DEEP_DIVE.md` §5a](IWPC_VALIDATION_DEEP_DIVE.md#5a-what-the-cpic-table-audit-revealed-2026-05-26)
- For the GenerativeBoundary contract this plan extends:
  [`EVIDENCE_SUFFICIENCY_LAYER_DEEP_DIVE.md`](EVIDENCE_SUFFICIENCY_LAYER_DEEP_DIVE.md)
- For platform-wide architecture context:
  [`anukriti-pgx-core/PLATFORM.md`](https://github.com/AnukritiAi-hq/anukriti-pgx-core/blob/main/PLATFORM.md)
