# Frontend → Backend cutover plan (Option 3)

> **Scope:** Move cohort generation off the client and onto the audited
> server engine, so the frontend stops being a parallel source of truth
> for the AF tables and CPIC rules. Companion to the 2026-05-17 PR that
> killed the fake "Fetch from AWS Open Data" UI on the simulation page
> (`anukriti-main` commit `5d9e00e`).
>
> **Status:** Not started. This document is the agreed plan, not a
> change log.
>
> **Author:** founding-engineer call, 2026-05-17.
>
> **Companions:**
>   - `THREE_REPO_INTEGRATION_DEEP_DIVE.md` — current import topology
>   - `IDEA_REFINEMENT_AND_PHASING_2026-05-14.md` — strategic context
>   - frontend `src/lib/thousandGenomes.js` — the AF table being deprecated
>   - backend `anukriti-api/app/routers/cohort.py` — the endpoint that will replace it

---

## Why

Today the Anukriti platform has two sources of truth for population
allele frequencies and CPIC rule version:

1. `anukriti-pgx-core==0.2.1` — the audited PyPI library, pinned in
   both `anukriti-swarm/requirements.txt` and
   `anukriti-api/requirements.txt`. Provenance manifest enforced by
   `tests/test_cpic_provenance.py`. **This is the canonical source.**
2. `anukriti-main/src/lib/thousandGenomes.js` — a hand-typed JS dict
   labelled `AF_TABLE_VERSION = "pgx-core-mirror_phase3_v1.2"` plus a
   client-side Hardy-Weinberg sampler. **This is a client snapshot
   and a divergence risk.**

When `pgx-core` ships 0.3.0 (Phase B in the IDEA_REFINEMENT plan —
adds BCHE for the Vysya wedge), the JS table will not have the new
allele frequencies. The user-visible symptom: Compare/Sensitivity
disagrees with Run, the LLM-explainer cites a phenotype the engine
doesn't produce, and the Generative Boundary fires `fabricate_claim`
inside `core/orchestrator/boundary.py`. We will spend 1–2 hours
chasing the bug before realising it's a stale JS dict.

The cutover removes the JS dict from the request path. Compare,
Sensitivity, History, Templates, and Run all consume the same
backend `/cohort/generate` response. One CPIC version pin. One audit
chain.

The cutover was deferred from the 2026-05-17 PR because:
- The deployed `/cohort/generate` returns a diplotype-level shape
  (`{patient_id, diplotype, phenotype, outcome}`), but the frontend
  Results page renders rsID columns (`rs4244285: "GA"`, …) and runs
  its own `runSimulation()` over them. Reshaping the response and
  reshaping the consumers is a fan-out across 8 files.
- Without server-side response caching, dragging the slider in
  `SensitivityTab.jsx` would issue 30 cohort POSTs per second per
  user. The cohort response is fully deterministic (the seed is in
  the input), so caching is trivial — but it's not done yet.

---

## Phases

### Phase 1 — backend: response cache + extended response shape

Single PR on `anukriti-api`. ~3 hours.

#### 1a. Response cache keyed on `(workflow, population, n, seed)`

`POST /cohort/generate` is fully deterministic — same body, same
output, every time. Cache the JSON response in-process (LRU, capped
at e.g. 256 entries) and serve from cache on hit.

```python
# anukriti-api/app/routers/cohort.py
from functools import lru_cache
from hashlib import sha256

def _cohort_cache_key(body: CohortGenerateBody) -> str:
    raw = f"{body.workflow}|{body.population}|{body.n}|{body.seed}"
    return sha256(raw.encode()).hexdigest()[:16]

# Cache the rendered JSON dict. lru_cache is fine for in-process —
# Container Apps replicas are independent processes anyway, and a
# 256-entry cap holds ~64 KB.
@lru_cache(maxsize=256)
def _generate_cached(key: str, body_json: str) -> dict:
    body = CohortGenerateBody.model_validate_json(body_json)
    return _generate_cohort_uncached(body)

@router.post("/cohort/generate")
async def generate(body: CohortGenerateBody) -> dict:
    return _generate_cached(_cohort_cache_key(body), body.model_dump_json())
```

Add an `ETag` header so the browser's HTTP cache short-circuits the
roundtrip entirely on repeat requests.

Acceptance:
- 10× POST with identical body → 1 generation, 9 cache hits.
- Different `seed` → different cache entries.
- Smoke test: dragging the SensitivityTab slider after this lands,
  watch logs — only the first generate per `(workflow,pop,n,seed)`
  shows up.

#### 1b. Extend response with rsID-level genotypes

The current response carries diplotype + phenotype + outcome. Add
an optional `rsid_genotypes: dict[str, str] | None` field per
patient — e.g. `{"rs4244285": "GA", "rs12248560": "CC"}` — populated
when the request asks for it via a query param `?include_rsids=1`.

This lets the frontend keep its rsID-columned Results table while
still reading phenotypes from the audited engine. It's an additive
change — existing consumers (no `?include_rsids`) get the same
response they get today.

Acceptance:
- Existing `tests/test_runs_smoke.py` passes byte-identical (omit
  the new field unless requested).
- New test: `?include_rsids=1` returns rsID dict per patient,
  shaped to match what the pgx-core caller's variant-resolution
  produced for that diplotype.

#### 1c. New tests

- `test_cohort_cache.py` — same body twice, second response served
  from cache (assert via a cache-instrumented `_generate_uncached`
  that records call count).
- `test_cohort_rsid.py` — `?include_rsids=1` populates the field;
  default request doesn't.

Verified end-to-end against production by running
`./scripts/redeploy.sh image` from `anukriti-stack/` after the PR
merges, then probing both endpoints from `localhost:5173` per the
DEPLOYMENT.md cheat sheet.

### Phase 2 — frontend: route Simulation.jsx through `/cohort/generate`

Single PR on `anukriti-main`. ~4 hours.

#### 2a. New helper: `lib/cohortClient.js`

```js
import { api } from "@/lib/api";

const BACKEND_WORKFLOW = {
  clopidogrel_cyp2c19: "clopidogrel",
  warfarin_cyp2c9_vkorc1: "warfarin",
  simvastatin_slco1b1: "simvastatin",
};

export async function generateCohort({ workflow, superpopulation, sampleSize, seed = 42 }) {
  const data = await api.cohort.generate({
    workflow: BACKEND_WORKFLOW[workflow] ?? workflow,
    population: superpopulation,
    n: sampleSize,
    seed,
  });

  // Reshape patients → row format the existing pgxRules / Results
  // table consumes. Phenotype + outcome come straight from the
  // server; rsID columns come from the new ?include_rsids field.
  return data.patients.map((p) => ({
    patient_id: p.patient_id,
    diplotype: p.diplotype,
    phenotype: p.phenotype,
    drug_action: p.outcome,        // backend canonical name
    ancestry_group: superpopulation,
    workflow,
    ...(p.rsid_genotypes || {}),    // rsID columns when included
    _source: "backend",
  }));
}
```

#### 2b. Replace `generateFromAwsSelector()` call sites in the request path

These call sites move to `cohortClient.generateCohort()`:

- `src/pages/Simulation.jsx` — `handleAwsGenerate()` and `runDemo()`.
- `src/lib/SimulationContext.jsx` — `generateCohort()` helper.

Compare/Sensitivity/Templates/Benchmarks may stay on the local
generator initially (they only matter once `pgx-core` 0.3.0 ships
new alleles); see Phase 3.

#### 2c. Stop running `runSimulation()` over backend rows

When a row carries `_source === "backend"`, its `phenotype` already
came from the audited engine — don't re-run client-side rules over
it. Update `Results.jsx` to short-circuit when `_source === "backend"`.

Acceptance:
- `npm run build` clean.
- Run-from-Simulation flow: phenotypes shown match
  `/cohort/generate` responses (curl probe + UI screenshot).
- `runSimulation()` is still called for CSV-upload flows (no
  `_source` set) — that path is unchanged.

#### 2d. Mark `runSimulation()` as deprecated in `pgxRules.js`

Add a docstring noting:
- It's used only for the CSV-upload path and for History/Templates
  replay where `_source !== "backend"`.
- Do not call it for any new feature.
- Long-term it goes away when the backend can also accept a
  CSV-upload (pre-resolved snps[]) request.

### Phase 3 — frontend: migrate Compare / Sensitivity / Templates / Benchmarks

Single PR on `anukriti-main`. ~3 hours.

These pages all call `generateFromAwsSelector` for in-memory
cohorts. They're not on the request path today, so they're allowed
to drift behind. After the cache lands (Phase 1a), the cost of
calling the backend on every slider tick becomes acceptable.

- `Compare.jsx` — A/B cohorts → two `cohortClient.generateCohort`
  calls.
- `SensitivityTab.jsx` — slider regenerates → cached on the server.
  Add a brief debounce (200 ms) on top of the cache to be polite.
- `Templates.jsx` — load saved template → `cohortClient.generateCohort`.
- `Benchmarks.jsx` — three call sites, all migrate.
- `History.jsx` — replay-by-config path migrates; replay-from-
  stored-rows path is unchanged.

### Phase 4 — delete the JS AF table

Single PR on `anukriti-main`. ~30 min, low risk after Phases 1–3.

- Delete `src/lib/thousandGenomes.js`'s `AF_TABLE`, `VARIANT_BASES`,
  `SNP_SEED_OFFSET`, `lcg`, `diploidFromAF`, `sampleSNP`,
  `generateRow`, `generateFromAwsSelector`. Keep
  `SUPERPOPULATIONS`, `SAMPLE_SIZES`, `CHROMOSOME_SETS`,
  `AF_TABLE_VERSION` as UI metadata.
- Delete `runSimulation()` from `pgxRules.js`. The `INTERPRETERS`
  dict, `interpretClopidogrel/Warfarin/Simvastatin` and the
  generators (`generateClopidogrelSample` etc.) all go too.
- The `INPUT_SCHEMA_VERSION` and `RULE_VERSION` constants stay —
  they're surfaced in the audit page footer.

After this PR, the frontend has no PGx logic of its own. The
positioning claim "the engine is the API, full stop" becomes true.

---

## Acceptance criteria for the whole cutover

When all four phases land:

1. **No client-side phenotype derivation.** Grep
   `runSimulation\|interpretClopidogrel\|interpretWarfarin\|interpretSimvastatin`
   in `anukriti-main/src/` — zero hits.
2. **No client-side AF tables.** Grep `AF_TABLE\|sampleSNP\|generateRow`
   — zero hits.
3. **All cohort generation goes through `api.cohort.generate(...)`.**
   The Sources panel offers two options: CSV Upload (user-supplied
   pre-resolved snps[]) and Synthetic cohort (server-generated).
4. **The synthetic-cohort UI shows the canonical `pgx-core` version.**
   `metadata.data_source_version` reads e.g. `pgx-core==0.3.0` (the
   server reports it), not a client-side mirror string.
5. **Running the same simulation in Compare and Run yields identical
   results.** Both paths fetch from the same cached
   `/cohort/generate` response.

---

## Order of operations

| Step | Repo | Effort | Blocks |
|---|---|---|---|
| 1a — response cache | `anukriti-api` | 1 hr | nothing |
| 1b — rsID-level response | `anukriti-api` | 1.5 hr | 2b |
| 1c — tests | `anukriti-api` | 30 min | merge |
| `redeploy.sh image` | `anukriti-stack` | 5 min | 2a |
| 2a — `cohortClient.js` | `anukriti-main` | 30 min | 2b |
| 2b — wire Simulation.jsx | `anukriti-main` | 1 hr | 2c |
| 2c — short-circuit Results | `anukriti-main` | 1 hr | 2d |
| 2d — deprecate `runSimulation` | `anukriti-main` | 15 min | merge |
| Phase 3 — migrate other pages | `anukriti-main` | 3 hr | Phase 4 |
| Phase 4 — delete JS table | `anukriti-main` | 30 min | done |

Phases 1 and 2 must land in the same session window — running
Phase 1 alone is harmless; running Phase 2 without Phase 1's cache
risks a Sensitivity-slider DDoS during a demo.

Phase 3 can land any time after Phase 2 is verified. Phase 4 is
the cleanup once nothing else imports the deprecated symbols.

---

## Out of scope for this plan

- **Backend cohort persistence.** `/cohort/generate` today is
  stateless — the cache is in-process. If we want shareable cohort
  permalinks, that's MongoDB-backed and a separate decision.
- **Rate-limiting cohort generation per API key.** Current limits
  apply to all routes uniformly; a per-route override (e.g. cohort
  is cheap-after-cache, run is expensive) is a separate change.
- **Mongo Atlas network tightening.** Tracked in DEPLOYMENT.md
  "What the Azure deploy does NOT include".
- **CYP2D6 CNV calling.** Tracked in
  `anukriti/CLINICAL_GRADE_ROADMAP.md` CP-1.

---

*Update this document in the same commit that lands each phase. When
all phases are done, mark Status as 'Complete' and link to the four
landed commits.*
