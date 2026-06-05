# Session Resume — 2026-06-05

> Pause point captured 2026-06-05 ~12:00 IST.
> Successor to `SESSION_RESUME_2026-05-26.md`.
> Resume with: "continue from SESSION_RESUME_2026-06-05.md".

Dense session: real gnomAD/SGDP frequency data wired end-to-end from
BigQuery artifacts through the swarm reasoning agents, the API gateway,
and into the live Azure deployment. Plus three EVIDENCE_LEVEL_AND_LLM_CONTEXT_PLAN
tasks shipped (T7, T8, T12) and full commit history pushed.

---

## TL;DR

Real pharmacogenomic allele frequencies (gnomAD v2.1.1 exomes,
n=8k–56k per population) now flow from pinned JSONL artifacts through
the entire stack to the live `product.anukritiai.com` frontend.
Citation validation and chemistry-grounded LLM narration are
implemented and ready for production.

| # | Workstream | Result |
|---|---|---|
| 1 | **gnomAD v2.1.1 + SGDP real frequencies** | Live on Azure; end-to-end through population agents → API → frontend |
| 2 | **T7 CitationValidator** | Shipped; C1-C5 rules, per-sentence validation |
| 3 | **T8 LLMNarrator** | Shipped; chemistry-grounded, citation-validated, GenerativeBoundary-guarded |
| 4 | **T12 POST /llm-context/grounded** | Shipped; full structured response with validation trace |
| 5 | **F-10 CYP2C9 fix verification** | Confirmed: pgx-core 0.4.0, 76/76 tests pass, 16/16 alleles correct |
| 6 | **Azure redeploy** | rev 24, image `git-2f19e60-2b2e7d-aa3c77-be156c`, ANUKRITI_REAL_FREQUENCIES=1 |

---

## Commit table — three repos, one session

| Repo | Commit | What |
|------|--------|------|
| `anukriti-swarm` | `2b2e7df` | feat(datasets): ingest real gnomAD v2.1.1 + SGDP allele frequencies via BigQuery (Jun 4) |
| `anukriti-swarm` | `5cbc617` | feat: wire real gnomAD/SGDP frequencies + T7 CitationValidator + T8 LLMNarrator |
| `anukriti-api` | `0cc3d16` | feat: real gnomAD overlay on /population/frequency + T12 /llm-context/grounded |
| `anukriti-stack` | `874a623` | feat: add ANUKRITI_REAL_FREQUENCIES env var to swarm + api services |

---

## 1. gnomAD/SGDP Real Frequency Integration

### What was done
- **Data layer** (landed Jun 4): `scripts/ingest_gnomad_frequencies.py` and
  `scripts/ingest_sgdp_frequencies.py` query BigQuery public datasets offline,
  produce pinned JSONL artifacts (136 gnomAD records, 83 SGDP records) covering
  24 CPIC Level-A PGx defining variants across 5 super-populations.
- **Reasoning layer**: `BasePopulationReasoningAgent.__init__` now accepts
  `use_gnomad=True, use_sgdp=True` kwargs (defaults False → byte-identical
  demo contract preserved).
- **Pipeline layer**: `workflows/nodes.py` and `integrations/google_adk/agents.py`
  read `ANUKRITI_REAL_FREQUENCIES=1` env var.
- **Demo**: `python -m demos.population_reasoning_demo --real` shows real data
  with provenance; without `--real` is identical to before.
- **API**: `/population/frequency` overlays real gnomAD v2.1.1 data on the
  static table when `ANUKRITI_REAL_FREQUENCIES=1`. Source field changes to
  `gnomAD v2.1.1 (BigQuery)`.
- **Deploy**: `anukriti-stack` docker-compose passes the flag to both services.
  Azure Container App has it set to `1`.

### Bug fixes during integration
- Artifact loader deduplication: gnomAD JSONL had 20 duplicate entries (exomes +
  genomes fallback) where genomes-fallback had 0.0 frequencies overwriting real
  exomes data. Fixed by keeping record with highest frequency per key.
- Overlay order: SGDP (n=22–75) was winning over gnomAD (n=8k–56k) on shared
  keys. Fixed: SGDP loads first, gnomAD loads last (later wins).

### Key numbers (real vs curated)

| Variant | Pop | Curated | Real (gnomAD v2.1.1) | Real n |
|---|---|---|---|---|
| CYP2C19*2 | SAS | 0.36 | 0.324 | 9,046 |
| CYP2C19*2 | EUR | 0.15 | 0.147 | 42,076 |
| CYP2D6*4 | EUR | 0.22 | 0.197 | 54,888 |
| CYP2D6*17 | AFR | 0.20 | 0.185 | 7,568 |
| VKORC1 A | SAS | 0.18 | 0.308 | 15,247 (SGDP) |

---

## 2. T7 — CitationValidator

**File:** `anukriti-swarm/core/runtime/citation_validator.py`

- 5 rules: C1 (uncited claim), C2 (fabricated citation), C3 (empty), C4 (malformed token), C5 (all clean)
- Per-sentence validation with `CitationValidationTrace`
- Citation token format: `[Source, ID]` (regex-matched)
- Off-by-default; opt-in via `SwarmRuntime(citation_validator=CitationValidator())`
- 244/244 swarm tests still pass

---

## 3. T8 — LLMNarrator

**File:** `anukriti-swarm/ai/narrative/llm_narrator.py`

- Imports `anukriti_chemistry.smiles` and `anukriti_chemistry.roles` (scope-firewalled: ONLY in `ai/narrative/`)
- Frozen grounding prompt: "Reason only from the data below. Every claim must cite [Source, ID]."
- Calls LLM → validates citations via T7 → fabricated citations trigger `GenerativeBoundary` violation (raises)
- Returns `LLMNarrative(text, citations, validation, chemistry_context, model, latency_ms)`
- Works with any LLM client exposing `.generate(prompt) → .text`

---

## 4. T12 — POST /llm-context/grounded

**File:** `anukriti-api/app/routers/llm_context.py` (appended)

- Request: `{"workflow", "population", "snps", "max_records"}`
- Response: `GroundedResponse` with explanation, citations, validation trace, chemistry context, evidence level
- Uses `LLMNarrator` + `CitationValidator` end-to-end
- When OpenAI key is available: calls LLM, validates, reports uncited claims
- When no key: returns structured context only (no explanation text)
- Tested end-to-end: correctly detected 1 uncited claim via C1 rule

---

## 5. F-10 / Rung-2 Status

- **F-10 (CYP2C9):** RESOLVED. pgx-core 0.4.0 shipped with regenerated CPIC table (16/16 alleles, 136/136 diplotypes correct). Swarm already bumped dep (`444aca4`). 76/76 tests pass.
- **Rung-2 (CYP2D6 SV):** Integration seam done. `anukriti/src/cyp2d6_sv_ingest.py` + 8 tests pass. Concordance 0.429→0.857. Live bake-off (Cyrius/StellarPGx/Aldy on WGS BAMs) needs external compute (69.6GB download deferred).

---

## 6. Azure Deployment

```
Image:    anukritiacr.azurecr.io/anukriti-api:git-2f19e60-2b2e7d-aa3c77-be156c
Revision: anukriti-api--0000024
Env:      ANUKRITI_REAL_FREQUENCIES=1
Health:   200 OK
```

Live probe:
```
GET /population/frequency?gene=CYP2C19&variant=rs4244285
→ source: "gnomAD v2.1.1 (BigQuery)", SAS: 0.324 (n=9046), EUR: 0.147 (n=42076)
```

---

## EVIDENCE_LEVEL_AND_LLM_CONTEXT_PLAN task status update

| Task | Status | Commit |
|------|--------|--------|
| T1 evidence_level field on PhenotypeInference | ✅ Done (0.3.0) | `2e5a121` |
| T2 drug= kwarg | ✅ Done (0.3.0) | `2e5a121` |
| T3 CPIC_RECOMMENDATION_LEVELS table | ✅ Done (0.3.0) | `2e5a121` |
| T4 swarm evidence_level → UnifiedExecutionReport | ✅ Done | `2cd068c` |
| T5 api /runs response surfaces evidence_level | ✅ Done | `aa9bbfb` |
| T6 frontend EvidenceBadge | ✅ Done | `e260546` |
| **T7 CitationValidator** | ✅ Done | `5cbc617` |
| **T8 LLMNarrator** | ✅ Done | `5cbc617` |
| T9 synthesis_mode in SwarmRuntime | 🔲 Open | — |
| T10 api POST /runs with synthesis_mode | 🔲 Open | — |
| T11 frontend AI interpretation panel | 🔲 Open | — |
| **T12 POST /llm-context/grounded** | ✅ Done | `0cc3d16` |
| T13 frontend tooltip on EvidenceBadge | ✅ Done | earlier |
| T14 sufficiency rule gene-scope facet | ✅ Done | `6fc0e97` |
| T15 DPYD/fluoropyrimidine workflow | ✅ Done | `95647db` |
| T16 frontend evidence-level filter | 🔲 Open | — |
| T17 frontend population equity panel | 🔲 Open | — |
| T18 frontend history persistence | ✅ Done (partial) | earlier |
| T19 compliance-pack evidence_level section | 🔲 Open | — |

**Score: 13/19 done** (was 8/19 before this session).

---

## What's next (priority order)

1. **T9 synthesis_mode in SwarmRuntime** — wire LLMNarrator into the 5-stage lifecycle as an opt-in Stage 5b
2. **Redeploy with T7/T8/T12** — run `redeploy.sh image` to push the LLMNarrator + CitationValidator to production
3. **anukriti-rapid-agent submission** — due June 9 (4 days). Devpost + YouTube demo remaining.
4. **T10/T11** — frontend AI interpretation panel consuming /llm-context/grounded
5. **Rung-2 live bake-off** — needs external compute for WGS BAMs

---

## How to resume

```bash
# Swarm demos (real frequencies)
cd anukriti-swarm && python -m demos.population_reasoning_demo --real

# Pipeline with real frequencies
ANUKRITI_REAL_FREQUENCIES=1 python -m demos.showcase

# Test CitationValidator
python -c "from core.runtime.citation_validator import CitationValidator; cv = CitationValidator(); print(cv.validate('X is true [CPIC, PMID:1].', {'PMID:1'}).verdict)"

# Test LLMNarrator (needs anukriti-chemistry on PYTHONPATH)
PYTHONPATH="$PYTHONPATH:../anukriti-chemistry" python -c "from ai.narrative.llm_narrator import LLMNarrator; print('ok')"

# API locally
cd anukriti-api && PYTHONPATH="../anukriti-swarm:../anukriti-chemistry" ANUKRITI_AUTH_DISABLED=1 uvicorn app.main:app --port 8000
curl -X POST localhost:8000/llm-context/grounded -H 'Content-Type: application/json' -d '{"workflow":"clopidogrel","population":"SAS"}'
```

---

## Canonical doc links

- `anukriti-pgx-core/PROJECT_CONTEXT.md` — D1-D11, F-10 (RESOLVED)
- `anukriti-swarm/.anukriti-project-context.md` — swarm session log
- `anukriti_docs/EVIDENCE_LEVEL_AND_LLM_CONTEXT_PLAN.md` — T1-T19 tracker
- `anukriti_docs/DETECTION_ROADMAP.md` — Rung 0-5 ladder
- `anukriti_docs/RUNG2_CYP2D6_SV_PLAN.md` — CYP2D6 SV integration
- `anukriti_docs/runbooks/seed-new-workflow.md` — adding new drug/gene workflows
- `ANUKRITI_FULL_CONTEXT.md` (repo root) — complete platform overview
