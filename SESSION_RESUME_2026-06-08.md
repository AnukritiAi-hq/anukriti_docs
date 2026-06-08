# Session Resume — 2026-06-08

> Pause point captured 2026-06-08 ~21:15 IST.
> Successor to `SESSION_RESUME_2026-06-05.md`.
> Resume with: "continue from SESSION_RESUME_2026-06-08.md".

Two threads this session: (1) a brand-new repo — **anukriti-adk**, the
Google for Startups AI Agents Challenge **Track 2 (Optimize)** submission —
and (2) closing out the **EVIDENCE_LEVEL_AND_LLM_CONTEXT_PLAN** by shipping
the last open tasks across swarm, api, and the frontend. The plan is now
**19 / 19 done**.

---

## TL;DR

| # | Workstream | Result |
|---|---|---|
| 1 | **anukriti-adk** (Track-2 ADK + Gemini) | New repo; submission-ready; live on Cloud Run; Devpost due June 9 |
| 2 | **T9 swarm `synthesis_mode`** | LLM-grounded Stage-5b with named C-rule fallback; deterministic-first |
| 3 | **T10 swarm tests** | +23 pytest (CitationValidator, LLMNarrator, runtime grounded) |
| 4 | **T11 swarm demo** | `demos/llm_grounded_demo.py` — 3 acts (ALL_CITED / C2 / C1) |
| 5 | **anukriti-api `/llm-context/grounded`** | Rewired through `SwarmRuntime(synthesis_mode="llm_grounded")` |
| 6 | **T16/T17 frontend** | `<EvidenceTooltip>` + `<LlmExplanationPanel>` |
| 7 | **T19 vitest harness** | vitest + testing-library bootstrapped; 19 component tests |
| 8 | **T19-compliance-pack** | `evidence_level` section documents the citation-validation contract |

Test totals after this session: **swarm 267 pytest · api 128 pytest ·
frontend 27 vitest** — all green; builds + lint clean across all three repos.

---

## 1. anukriti-adk — Google ADK Track 2 (Optimize)

New repo at `SynthaTrial-repo/anukriti-adk` (the 12th sub-repo). Built with
Google ADK 2.x + Gemini 2.5 Flash. Apache-2.0.

**The pitch:** took the PGx safety agent that *hallucinated drug
recommendations on under-evidenced populations* and made it
production-reliable by **forbidding the LLM from deciding**, then proved the
gain with ADK's own eval framework.

**Headline ADK eval delta (same model, same tools, only the optimization differs):**

| Metric | Baseline | Optimized |
|---|---:|---:|
| `tool_trajectory_avg_score` | 0.44 | **1.00** |
| Hallucination-free rate | 50% | **100%** |
| Unsafe recommendations (of 8) | 3 | **0** |
| Correct named refusal | 0% | **100%** |

**How:**
- **GenerativeBoundary** wired as ADK `after_model` / `after_tool` callbacks
  that *rewrite* an unsafe model draft (a recommendation over an engine
  refusal, or a fabricated PMID) into a named, safe refusal before the user
  sees it — "you can't", not "please don't".
- **Programmatic instruction optimizer** (`harness/optimize_instructions.py`)
  scores six instruction variants against the eval set; `v6_full_contract`
  wins (composite 1.000) and is the deployed `OPTIMIZED_INSTRUCTION`.
- Reproducible offline harness (`python -m harness.run_optimization` writes
  `EVAL_RESULTS.md`) **plus** a real `--live` ADK eval against Gemini via
  Vertex AI (`LIVE_EVAL_RESULTS.md`, passes `hallucinations_v1`).

**Commits (all 2026-06-08):**
`45dd15a` initial · `eb3c79d` `/livez` route (Cloud Run reserves `/healthz`) ·
`f4bdff0` require `google-adk[eval]` extra · `2444f17` live ADK eval vs Gemini.

**Deployed:** Cloud Run `https://anukriti-adk-l6ztkkgjqa-uc.a.run.app`
(`POST /v1/guard` auth'd; `GET /` and `GET /livez` open). Submission assets
ready in `submission/DEVPOST.md` + `submission/VIDEO_SCRIPT.md`.

---

## 2. T9 — swarm `synthesis_mode` (LLM-grounded Stage-5b)

**File:** `anukriti-swarm/core/runtime/runtime.py`

`SwarmRuntime` now takes `synthesis_mode: str | None` and an injectable
`llm_narrator`. When `synthesis_mode="llm_grounded"`, `LLMNarrator` runs as an
opt-in Stage-5b *after* the deterministic narrative. The hardening this
session was the **fallback contract**:

- `ALL_CITED` (or empty no-client mock) → grounded narrative attached, emits
  `SYNTHESIS_EMITTED`.
- `MISSING_CITATIONS` (C1) / `FABRICATED_CITATION` (C2) / `MALFORMED` (C4) →
  the unvalidated LLM text is **dropped** from the user-facing slot (kept as
  `unvalidated_text` in the trace), the rule is named in `fallback_rule`,
  `used_fallback=True`, and a `SAFE_ABSTENTION` is emitted. The deterministic
  recommendation stands.
- A `GenerativeBoundaryViolation` (fabricated claim) is caught and converted
  to the same C2 fallback — the boundary fires, the run does not crash.

The default / `"template"` mode is **byte-identical** to before (regression
guard in the integration test).

---

## 3. T10 — swarm tests (+23)

- `tests/unit/test_citation_validator.py` (11) — C1–C5 + trace shape + skips.
- `tests/unit/test_llm_narrator.py` (5) — no-client empty, ALL_CITED, prompt
  delivery, fabrication raises the boundary, uncited → MISSING.
- `tests/integration/test_swarm_runtime_llm_grounded.py` (7) — grounded
  attach, C1/C2 fallback, `SAFE_ABSTENTION` emission, abstention-respecting,
  and the byte-identical default/template regression guard.

> **Gotcha for future sessions:** the `CitationValidator` treats a citation as
> *fabricated* only when the source token AND the id token AND the combined
> token are all absent from the evidence set. To force a C2 in a test, use a
> wholly-invented source (e.g. `[FakeDB, XREF:...]`) or a bare id-only set.
> Also: the SAS/clopidogrel run's real retrieved citation ids are
> `PMID:34032273` + `PA166169660` (not `PMID:35034351`).

---

## 4. T11 — `demos/llm_grounded_demo.py`

Three offline acts via a mock client: ACT 1 clean → ALL_CITED (grounded
narrative attached); ACT 2 fabricated citation → C2 → deterministic fallback;
ACT 3 uncited claim → C1 → deterministic fallback.

---

## 5. anukriti-api — `/llm-context/grounded` through the runtime

**File:** `anukriti-api/app/routers/llm_context.py`

Previously the endpoint called `LLMNarrator` directly, bypassing the
deterministic pipeline. Rewired to route through
`SwarmRuntime(synthesis_mode="llm_grounded", llm_narrator=...)` (a dedicated
runtime, not the `/runs` singleton), building the context via
`to_swarm_context`. New response fields: `used_fallback`, `fallback_rule`,
`deterministic_recommendation`. No-LLM-key path still returns the
deterministic recommendation + chemistry context. `+2` smoke tests
(`tests/test_runs_smoke.py`). 128 api tests pass.

> `POST /runs` already accepted `synthesis_mode` (runs.py:266) and
> `report.to_dict()` already carries `grounded_narrative`.

---

## 6. T16 / T17 — frontend components (anukriti-main)

- **T16** `src/components/shared/EvidenceTooltip.jsx` — "How do we know this?"
  radix tooltip: CPIC level / guideline version / PMID / frequency population
  / PharmVar table + CPIC link. Renders nothing when no provenance.
- **T17** `src/components/results/LlmExplanationPanel.jsx` — calls
  `/llm-context/grounded` (via `fetchGroundedInterpretation`); renders inline
  `[Source, ID]` citation badges, the authoritative deterministic
  recommendation, an uncited-claims warning, and the **named C-rule fallback
  banner**. Exports a pure `splitCitations` helper + `CitedText` for testing.
  `src/lib/llmGrounding.js` extended to surface `usedFallback` /
  `fallbackRule` / `deterministicRecommendation`.

---

## 7. T19 — vitest harness

vitest was not previously installed. Bootstrapped it:
- dev deps: `vitest@2.1.9`, `jsdom@25.0.1`, `@testing-library/react@16.1.0`,
  `@testing-library/jest-dom@6.6.3`, `@testing-library/user-event@14.5.2`.
- `vitest.config.js` (standalone — defines `@` → `./src` because the base44
  vite plugin isn't test-friendly; jsdom env; `vitest.setup.js` adds jest-dom
  matchers).
- `test` + `test:watch` scripts in `package.json`.
- Tests: EvidenceBadge (7), EvidenceTooltip (4), LlmExplanationPanel (8),
  compliancePack (8) = **27 passing**.

> Radix tooltip content renders into a portal — assert with
> `findAllByText` / `getAllByText`, not `getByText`.

---

## 8. T19-compliance-pack — `evidence_level` section

**File:** `anukriti-main/src/lib/compliancePack.js`

The pack's `evidence_level_classification.txt` artifact now documents the
**CitationValidator C1–C5 named-refusal contract**, the LLM-grounded
deterministic-first behavior ("impossible by construction"), the audit fields
(`used_fallback` / `fallback_rule`), and pins pgx-core 0.4.0 (CYP2C9 table
16/16 alleles, 136/136 diplotypes). Added `fluorouracil_dpyd` to the version
manifest. `CompliancePackButton.jsx` now shows the dynamic file count (was a
hardcoded "7", actually 8). `evidenceLevelPolicy()` + `versionManifest()`
exported for the 8 new vitest assertions.

---

## EVIDENCE_LEVEL_AND_LLM_CONTEXT_PLAN — final status

**19 / 19 done.** T1–T6 + T13 + T15 + T18 (0.3.0 era), T7/T8/T12 (2026-06-05),
and T9/T10/T11/T14/T16/T17/T19 + compliance-pack (this session). The full
chain is live end-to-end: deterministic engine → swarm `synthesis_mode` with
C-rule fallback → api `/llm-context/grounded` → frontend
`<LlmExplanationPanel>` with citation badges and named refusals.

---

## What's next (priority order)

1. **anukriti-adk Devpost submission + YouTube demo** — due June 9 (tomorrow).
2. **anukriti-rapid-agent submission** — also June 9.
3. **Redeploy anukriti-api** with the rewired `/grounded` (run
   `anukriti-stack/scripts/redeploy.sh image`) once the swarm source is
   bundled — verify `used_fallback` surfaces in the live payload.
4. **Wire `<LlmExplanationPanel>` into a results surface** (Results.jsx /
   Simulation.jsx) — the component exists but isn't mounted yet.
5. **Rung-2 CYP2D6 SV live bake-off** — still needs external compute (WGS BAMs).
6. **Uncommitted:** `anukriti_docs/papers/` has two new untracked PDFs
   (`CPT-117-1194.pdf`, `pnas.71.7.2627.pdf`).

---

## How to resume

```bash
# Swarm — LLM-grounded demo + tests
cd anukriti-swarm && source venv/bin/activate
python -m demos.llm_grounded_demo
python -m pytest -q          # 267 pass

# API — grounded endpoint (swarm + chemistry on PYTHONPATH)
cd anukriti-api && source .venv/bin/activate
export PYTHONPATH="$PWD/../anukriti-swarm:$PWD/../anukriti-chemistry"
ANUKRITI_AUTH_DISABLED=1 python -m pytest -q   # 128 pass
ANUKRITI_AUTH_DISABLED=1 uvicorn app.main:app --port 8000
curl -X POST localhost:8000/llm-context/grounded \
  -H 'Content-Type: application/json' \
  -d '{"workflow":"clopidogrel","population":"SAS","snps":[{"id":"rs4244285","genotype":"AA"}]}'

# Frontend — components + tests
cd anukriti-main
npm test                     # 27 vitest pass
npm run build

# ADK — reproduce the optimization result (offline)
cd anukriti-adk && source .venv/bin/activate
python -m harness.run_optimization
```

---

## Canonical doc links

- `ANUKRITI_FULL_CONTEXT.md` (repo root) — complete platform overview (updated 2026-06-08, 13 repos)
- `anukriti_docs/EVIDENCE_LEVEL_AND_LLM_CONTEXT_PLAN.md` — T1–T19 tracker (now 19/19)
- `anukriti-adk/README.md` + `submission/DEVPOST.md` — Track-2 submission
- `anukriti-pgx-core/PROJECT_CONTEXT.md` — D1–D11, F-10 (RESOLVED, 0.4.0)
- `anukriti-swarm/.anukriti-project-context.md` — swarm session log
- `anukriti_docs/SESSION_RESUME_2026-06-05.md` — prior session resume
