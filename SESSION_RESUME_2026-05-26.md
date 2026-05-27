# Session Resume — 2026-05-26

> Pause point captured at end of 2026-05-26 21:30 IST session.
> Successor to `SESSION_RESUME_2026-05-16.md`.
> Resume tomorrow with: "continue from SESSION_RESUME_2026-05-26.md".

This is the canonical "what happened today, where things stand, how
to pick up next" doc for a long, dense session. Eight repos got
production-grade work; one new library was bootstrapped and
released; a public pgx-core release shipped to PyPI; the Azure
backend went through two redeploy cycles; the live frontend was
rewired to consume engine truth instead of a hardcoded helper.

---

## TL;DR

Eight workstreams shipped. Five of them are end-to-end live in
production, with the verified wire-trace running from a pinned
CPIC table snapshot through to a coloured badge on a real-user-
facing webpage.

| # | Workstream | Result |
|---|---|---|
| 1 | **IWPC external-cohort validation** (n=5,700) | Live; 99 of 467 INR-confirmed undertreated patients |
| 2 | **CPIC table audit** + open-findings disclosure | Live; F-10 documented for v0.4.0 |
| 3 | **anukriti-pgx-core 0.3.0** release | Published to PyPI |
| 4 | **`evidence_level` field surfaced end-to-end** | Live in api response + frontend badge |
| 5 | **anukriti-chemistry v0.1.0** library | Init pushed; not yet on PyPI by design |
| 6 | **Azure Container App redeploy** (rev 14, then rev 15) | rev 15 active, healthy, serving 0.3.0 |
| 7 | **Multi-repo plan** for evidence_level + LLM-context | Documented, T1–T6 + T13 + T15 + T18(p) shipped |
| 8 | **EvidenceBadge frontend** + truth-from-engine refactor | Merged to main, helper retired, pass-through verified live |

The going-live story now reads end-to-end with commit hashes for
every claim.

---

## Commit table — eight repos, one day

| Repo | Commit | What |
|------|--------|------|
| `anukriti-pgx-core` | `2e5a121` | v0.3.0: evidence_level field + drug= kwarg + CPIC level table (additive, backwards-compatible) |
| `anukriti-pgx-core` | `58b0ebd` | F-10 v0.3.0/v0.4.0 backlog entry; "Open bugs" section flipped from "None critical" to honest disclosure |
| `anukriti-validation-iwpc` | `795bccc` → `e993a34` → `b981d7d` | Init + Q1–Q5 engine-vs-cohort validation block + CPIC audit script + IWPC §5a disclosure |
| `anukriti_docs` | `0716421` → `3c179ef` → `67203bc` | IWPC_VALIDATION_DEEP_DIVE + audit findings §5a + EVIDENCE_LEVEL_AND_LLM_CONTEXT_PLAN |
| `anukriti_landing` | `5c47c4f` | Trust card open-findings posture |
| `anukriti-chemistry` | `4a2252c` | Init: deterministic SMILES + isomer role table + RDKit-optional stereo |
| `anukriti-api` | `aa9bbfb` | Pin bump 0.2.1 → 0.3.0 |
| `anukriti-swarm` | `2cd068c` | Pin bump 0.2.1 → 0.3.0 |
| `anukriti-stack` | `5755e8c` | Dockerfile.api pin-comment update |
| `anukriti-api` | `93d7a59` | T13: wire `drug=` through `call_diplotype` adapter (also fixed pre-existing simvastatin/warfarin attribute-error bug) |
| `anukriti-api` | `4170a07` | Surface `evidence_level` on `/runs/from-samples` per_sample_rows |
| `anukriti-main` | `3d56b56` | EvidenceBadge component + workflow→level helper (feature branch) |
| `anukriti-main` | `59954f5` | Merge feat/evidence-badge to main |
| `anukriti-main` | `87937a2` | SimulationContext + ResultsTable consume row.evidence_level |
| `anukriti-main` | `6132628` | Retire `evidenceLevel.js` helper (truth-from-engine) |
| `anukriti` (Synthatrial) | `527a4db` | CP-5 PharmCAT unblock plan in CLINICAL_GRADE_ROADMAP |
| `anukriti-swarm` | `2f3cb0c` | Project-context refresh (sessions #1–#16 + post-#16 hotfix) |

Total: 17 commits across 8 repos.

---

## What's live where

### PyPI

- `anukriti-pgx-core==0.3.0` (uploaded `2026-05-26T13:08:28Z`)
- `pip install anukriti-pgx-core` resolves to 0.3.0
- The CPIC level table, `evidence_level` field on
  `PhenotypeInference`/`Diplotype`/`GenotypeCall`, and the optional
  `drug=` kwarg on `PhenotypeEngine.infer()` and the calling layer
  are all public

### Azure Container App

- App: `anukriti-api` in resource group `anukriti-rg`, region `eastus`
- Active revision: `anukriti-api--0000015` (deployed
  `2026-05-26T15:39:13Z`)
- Image: `anukritiacr.azurecr.io/anukriti-api:git-4170a07-2cd068-2e5a12`
  (image tag encodes the api commit SHA, swarm SHA, pgx-core SHA)
- Hostname: `anukriti-api.agreeablegrass-25e88475.eastus.azurecontainerapps.io`
- `/health` returns 200; `MongoRunStore` connected; auth-enabled true
- Live wire-trace verified: NA12891 + clopidogrel returns
  `evidence_level: "A"`, diplotype `*1/*17`, phenotype `Rapid
  Metabolizer`

### Vercel frontend

- Domain: `https://product.anukritiai.com`
- Bundle: `index-Dm__d9Na.js` (changed from pre-merge `index-2engmIN9.js`)
- Last-modified: `2026-05-26T15:57:59Z`
- Bundle contains `"Strong Evidence"` and `"Moderate Evidence"`
  strings — confirms the `EvidenceBadge` component is in production
- Auto-deploy hook updated mid-session by founder; rebuilt cleanly

### GitHub repos

| Repo | Branch | HEAD |
|------|--------|------|
| `anukriti-pgx-core` | main | `2e5a121` (v0.3.0 release commit; tag `v0.3.0` pushed) |
| `anukriti-validation-iwpc` | main | `b981d7d` |
| `anukriti_docs` | main | `67203bc` (this commit will move it) |
| `anukriti_landing` | main | `5c47c4f` |
| `anukriti-chemistry` | main | `4a2252c` |
| `anukriti-api` | main | `4170a07` |
| `anukriti-swarm` | main | `2cd068c` |
| `anukriti-stack` | main | `5755e8c` |
| `anukriti-main` | main | `6132628` |
| `anukriti` (Synthatrial) | clinical-grade-pgx | `527a4db` |

---

## The verified end-to-end wire trace

This is the most important diagram from today. It's the going-live
trail — every claim has a commit hash and a verifiable artefact.

```
PubChem REST API + CPIC API (api.cpicpgx.org/v1/pair)
   │
   │  snapshot 2026-05-26T...
   ▼
CPIC_RECOMMENDATION_LEVELS_v2024.01.json
   pinned in anukriti-pgx-core/anukriti_pgx_core/phenotype/tables/
   25 gene-drug pairs, all level A (the 6 shipped + 19 expansion)
   │
   │  released to PyPI as anukriti-pgx-core==0.3.0
   ▼
PhenotypeEngine.infer(gene, a1, a2, drug='clopidogrel')
   reads the table via phenotype.recommendation_level.level_for()
   populates result.evidence_level = 'A'
   │
   │  consumed by
   ▼
CYP2C19Caller(...).call(snps, drug='clopidogrel')   (T13 wiring)
   threads drug= into the chained PhenotypeInference
   surfaces result.evidence_level = 'A' on the Diplotype output
   │
   │  consumed by
   ▼
api.app.adapters.call_diplotype('clopidogrel', snps)
   returns details.CYP2C19.evidence_level = 'A'
   commit anukriti-api 93d7a59
   │
   │  consumed by
   ▼
api.app.routers.runs (POST /runs and /runs/from-samples)
   per_sample_rows[i].evidence_level = 'A'
   commit anukriti-api 4170a07
   │
   │  ★ VERIFIED LIVE ON AZURE rev 15:
   │  POST /runs/from-samples {workflow:clopidogrel, sample_ids:[NA12891]}
   │  → response.samples[0].evidence_level = 'A'
   ▼
HTTP response over the wire
   │
   │  consumed by
   ▼
anukriti-main lib/api.js → SimulationContext.startRunFromSamples
   row mapper preserves evidence_level (commit 87937a2)
   │
   │  consumed by
   ▼
<ResultsTable> reads row.evidence_level only
   (workflow→level helper deleted in commit 6132628)
   │
   │  consumed by
   ▼
<EvidenceBadge level="A" />
   renders green pill: "A · Strong Evidence"
   │
   │  ★ VERIFIED LIVE ON product.anukritiai.com:
   │  bundle index-Dm__d9Na.js contains "Strong Evidence" string
```

If anything in this chain breaks, the badge stops rendering and the
api responses lose the field. Both ends have integration tests +
the audit script can reproduce the engine layer verdict offline.

---

## What landed in detail

### Workstream 1 — IWPC external-cohort validation

**Goal**: ship a publishable validation study for the deterministic
engine against a published real-world cohort.

**Built**: [`anukriti-validation-iwpc`][repo-iwpc] standalone repo.
- 5,700 IWPC patients × CYP2C9 + VKORC1 phenotype calls
- Q1 monotonic gradient (low 45.80 → standard 33.66 → high 21.58
  mg/wk; gradient ~24 mg/wk; **PASS**)
- 467 high-risk patients prescribed ≥ cohort median dose
- **99 of those 467 (21%) had INR outside the 2.0–3.0 target range**
  — empirical confirmation those doses were clinically wrong

**Published in**: [`IWPC_VALIDATION_DEEP_DIVE.md`][doc-iwpc]
(committed earlier in session; no changes today except the §5a
audit-disclosure subsection added in `3c179ef`).

[repo-iwpc]: https://github.com/AnukritiAi-hq/anukriti-validation-iwpc
[doc-iwpc]: ./IWPC_VALIDATION_DEEP_DIVE.md

### Workstream 2 — CPIC table audit + open-findings disclosure

**Goal**: external validation that the engine's pinned phenotype
tables match canonical CPIC.

**Built**: `scripts/audit_cpic_tables.py` in `anukriti-validation-iwpc`.
- Pulls canonical CPIC tables from `api.cpicpgx.org`
- Diffs row-by-row against pgx-core's pinned JSON
- Surfaces three patterns of mismatch:
  - **Pattern A**: wrong-direction PM/IM bucketing (clinical-direction
    error; e.g. `*2/*2` is called PM in v0.2.1 but CPIC says IM)
  - **Pattern B**: wrong allele-functionality bins for 10 of 16
    CYP2C9 alleles (the cascade root cause)
  - **Pattern C**: ~50 diplotype rows missing entirely (engine
    returns `Indeterminate`; correct fallback, just incomplete)

**Audit headline (run on `anukriti-pgx-core==0.2.1`)**:

| Surface | matches |
|---|---|
| VKORC1 -1639 → sensitivity (Johnson 2017) | 3 / 3 (100%) |
| CYP2C9 allele → function (canonical CPIC) | 6 / 16 (38%) |
| CYP2C9 diplotype → phenotype (canonical CPIC) | 43 / 136 (32%) |

**Real-world impact**: ~70 of 5,700 IWPC patients (~1.2%) get wrong
PM/IM bucketing. The IWPC headline numbers (Q1 monotonic, 99/467
INR-confirmed) are robust because most signal comes from VKORC1,
which audits clean.

**Disclosed in**: `IWPC_VALIDATION_DEEP_DIVE.md` §5a (commit
`3c179ef`) and pgx-core `PROJECT_CONTEXT.md` F-10 (commit
`58b0ebd`).

**Founder call**: this is exactly what an audit is supposed to
surface. Disclose openly, schedule the fix in v0.4.0 (held until
PharmCAT verification — the right way to validate a content
correction). The platform's positioning is "every claim cites a
rule, every rule cites a paper, every refusal is named." That
positioning only holds if the rule tables are themselves correct.
The audit found the bugs. We name them. We fix them in v0.4.0.

### Workstream 3 — anukriti-pgx-core v0.3.0 release

**Goal**: publish an additive release that ships
`evidence_level` to consumers without changing any phenotype
values (F-10 fix held for v0.4.0).

**Implemented**:
- T1: pinned `CPIC_RECOMMENDATION_LEVELS_v2024.01.json` (25 pairs,
  all level A)
- T2: `evidence_level: str = ""` on three frozen dataclasses
- T3: `phenotype.recommendation_level` module with `level_for()` +
  `details_for()`
- T4: optional `drug=None` kwarg threaded through
  `PhenotypeEngine.infer()`, `GeneCaller.call()`, and three
  `GenotypeCaller` entry points
- T5: 25 new tests (76/76 total, up from 50)
- T6a: version bump 0.2.1 → 0.3.0; CHANGELOG `[0.3.0]` entry
- T6b: regression sweep against IWPC validation pipeline
  reproduces every headline number byte-identical

**Released**: tag `v0.3.0` pushed; OIDC trusted-publisher workflow
ran TestPyPI → manual approval → live PyPI publish.

**Verified**: `pip install anukriti-pgx-core==0.3.0` resolves.

**Compatibility**: every existing v0.2.1 consumer that doesn't
pass `drug=` continues to work unchanged. `evidence_level` defaults
to `""`. Pin-bumps are safe and don't change phenotype calls.

### Workstream 4 — `evidence_level` end-to-end

**Goal**: surface the new engine field on every recommendation
shown to a clinician.

**Implemented across three repos**:
- `anukriti-api/app/adapters.py` (T13, commit `93d7a59`):
  `call_diplotype(workflow, snps)` now passes `drug=workflow`
  through to the engine and surfaces `details[gene].evidence_level`.
  Same commit also fixed a **pre-existing latent bug** in the
  simvastatin and warfarin paths: they referenced
  `result.diplotype` and `result.phenotype.phenotype` on
  `GenotypeCall` records, which would have AttributeError'd if any
  user ever POSTed `/runs` with workflow=warfarin or simvastatin.
  The `/cohort/generate` path used different wiring so it never
  fired. Now both paths work.
- `anukriti-api/app/routers/runs.py` (commit `4170a07`):
  `/runs/from-samples` per_sample_rows builder now includes
  `evidence_level` per row.
- `anukriti-main/src/lib/SimulationContext.jsx` (commit `87937a2`):
  row mapper preserves `evidence_level` from the api response.
- `anukriti-main/src/components/results/ResultsTable.jsx` (commits
  `87937a2` and `6132628`): badge condition now reads
  `row.evidence_level` only.
- `anukriti-main/src/lib/evidenceLevel.js` (commit `6132628`):
  **DELETED**. The hardcoded workflow→level helper was a temporary
  bridge. The api now ships truth from the engine.

**Verified live**: `POST /runs/from-samples` with NA12891 +
clopidogrel returns `evidence_level: "A"` over the wire.

### Workstream 5 — anukriti-chemistry v0.1.0

**Goal**: build the deterministic chemistry primitives the future
LLMNarrator (T8 of the plan) will consume.

**Built**: [`anukriti-chemistry`][repo-chem] standalone repo.
- `smiles` — drug-name → SMILES from pinned PubChem snapshot
  (20 drugs from CPIC_RECOMMENDATION_LEVELS_v2024.01)
- `roles` — pinned active/toxic/inactive isomer role table for
  6 drugs (warfarin, clopidogrel, simvastatin, codeine,
  carbamazepine, phenytoin) with PMID citations
- `stereo` — RDKit-backed stereoisomer enumerator, gated behind
  `pip install anukriti-chemistry[rdkit]` optional extra
- 35 test cases across 4 files
- Closed-enum types (`IsomerRole`, `StereoConfiguration`) +
  frozen dataclasses (`StereoIsomer`, `AtomConfiguration`,
  `DrugRoleEntry`)

**Scope firewall** documented in `__init__.py`: this library
produces structured data for the LLM narration / explanation
layer ONLY. It MUST NOT be imported by any deterministic-engine
module (`anukriti-pgx-core`, swarm pharmacogene/runtime/sufficiency/
orchestrator). Importing chemistry data into the deterministic
phenotype path would break the platform's central invariant.

**Released**: GitHub only (`AnukritiAi-hq/anukriti-chemistry @ 4a2252c`).
**Not yet on PyPI** — by design. PyPI publish waits until
`anukriti-swarm/ai/narrative/LLMNarrator` (T8) consumes the library
in real use, so we can verify the API surface is right before
locking it on PyPI. Same discipline that worked for pgx-core.

[repo-chem]: https://github.com/AnukritiAi-hq/anukriti-chemistry

### Workstream 6 — Azure Container App redeploy

**Goal**: get the new engine into production.

**Two redeploys today**:

| Rev | Image | Commits in image | Active from |
|-----|-------|-----------------|-------------|
| 14 | `git-aa9bbfb-2cd068-2e5a12` | api (pin bump only), swarm (pin bump only), pgx-core 0.3.0 | 2026-05-26T14:51:50Z |
| 15 | `git-4170a07-2cd068-2e5a12` | api (T13 + per_sample_rows fix), swarm (pin bump), pgx-core 0.3.0 | 2026-05-26T15:39:13Z |

Both deploys ran via `anukriti-stack/scripts/redeploy.sh image`
which: `az acr login` → `docker build` (parent dir as context) →
`docker push` (`:git-<sha-tuple>` + `:latest`) → `az containerapp
update --image` → wait for new revision → smoke `/health`. ~5
minutes per cycle.

Smoke passed both times. Container Apps does atomic revision
swaps; failed deploys roll back automatically.

### Workstream 7 — Multi-repo plan

**Goal**: make the next 5 sessions' work executable without
re-deciding architecture every time.

**Built**: `anukriti_docs/EVIDENCE_LEVEL_AND_LLM_CONTEXT_PLAN.md`
(commit `67203bc`). 19 tasks across 4 repos with sequencing
diagram, acceptance criteria, and effort estimates.

**Resolved three architectural questions Anna's spec left implicit**:
1. The LLM endpoint shape lives in `anukriti-api`, but the LLM
   call itself lives in `anukriti-swarm` — must go through
   `GenerativeBoundary`, not bypass it.
2. `CitationValidator` lives at `anukriti-swarm/core/runtime/`
   alongside `GenerativeBoundary`. Closed-enum verdicts
   (ALL_CITED, MISSING_CITATIONS, FABRICATED_CITATION,
   EMPTY_RESPONSE, MALFORMED), named refusal rules C1..C5
   mirroring the existing R/V/U pattern.
3. The badge value is the per-recommendation CPIC level (A/B/C/D),
   the clinical-actionability score from cpicpgx.org/genes-drugs.
   NOT per-allele functionality strength and NOT per-PhenotypeInference
   confidence.

### Workstream 8 — EvidenceBadge frontend

**Goal**: visible CPIC level on every recommendation.

**Built**: `<EvidenceBadge level="A" />` in `anukriti-main/src/
components/shared/EvidenceBadge.jsx` (commit `3d56b56`). Stateless
component, renders coloured pill (A green / B yellow / C orange /
D grey) with lucide-react icons. Empty/null level renders nothing
(graceful degradation).

**Wire-up evolution**:
1. Initial commit (3d56b56): badge takes `level` prop; `Results.jsx`
   passes a hardcoded workflow→level helper value (the temporary
   bridge).
2. Pass-through commit (87937a2): badge prefers `row.evidence_level`
   from the api, falls back to the prop.
3. Cleanup commit (6132628): helper file deleted; badge reads
   `row.evidence_level` only.

The fallback chain was deliberately preserved across two commits
so any rollback would land in a still-working state.

---

## What's NOT yet shipped (open backlog, ordered by priority)

### v0.4.0 of anukriti-pgx-core (high priority, scheduled)

The F-10 CYP2C9 functionality table fix:
- Re-bin 10 alleles (`*4`, `*5`, `*8`, `*11`, `*30`, `*61` from
  no-fn → decreased-fn; `*13`, `*39`, `*43` from decreased-fn →
  no-fn; `*27` overconfidence cleanup)
- Regenerate `CYP2C9_diplotypes_anukriti_v2024.01.json`
- Add the missing diplotype rows from CPIC's table
- Re-run audit; target 100% match on all three surfaces
- Re-run IWPC validation; document any change in headline numbers
- Tag v0.4.0; OIDC publish to PyPI
- Bump consumer pins; redeploy api

**Acceptance gate**: PharmCAT diplotype concordance against the
published CPIC table (CP-5 in the anukriti repo) before shipping.
That's the right external validation for a content correction
that changes phenotype values clinically (e.g. `*2/*2` flipping
PM → IM).

**Effort estimate**: ~half a day for the table work, ~half a
day for the PharmCAT smoke test once unblocked.

### CP-5 PharmCAT concordance (medium, queued)

Documented in `anukriti/CLINICAL_GRADE_ROADMAP.md` (commit
`527a4db`). The chr2 VCF extraction throughput blocker is
diagnosed:

- Root cause: `extract_sample_variants()` at
  `src/benchmark/pharmcat_comparison.py:191` does line-by-line
  gzip iteration over a 1.2GB chr2 VCF
- Fix: ~15 LOC switch to `pysam.TabixFile.fetch(chrom, start, end)`
  (1000G phase 3 ships `.tbi` indices alongside `.vcf.gz`)
- Prerequisites: 1000G phase 3 VCFs for chr1, chr2, chr6, chr10,
  chr12, chr16, chr22 + tabix indices; PharmCAT Docker image;
  pyliftover (already in reqs); pysam (one-line install)

**Effort estimate**: ~half a day, single session, prerequisites
verified at session start.

### EVIDENCE_LEVEL_AND_LLM_CONTEXT_PLAN open tasks (lower)

11 of the 19 planned tasks are still open. Sequencing:

- **T7** CitationValidator in `anukriti-swarm/core/runtime/`
- **T8** LLMNarrator in `anukriti-swarm/ai/narrative/`
- **T9** SwarmRuntime synthesis_mode wiring
- **T10** unit tests for T7+T8+T9
- **T11** llm_grounded_demo
- **T12** `POST /api/v1/llm-context` endpoint in `anukriti-api`
- **T14** smoke tests for T12
- **T16** `<EvidenceTooltip>` "How do we know this?"
- **T17** `<LlmExplanationPanel>` with citations
- **T18** wire EvidenceBadge into Simulation/TrialDecisionCard/
  ConfidencePanel (partial — wired into Results.jsx only)
- **T19** Vitest snapshots

These don't block today's going-live. They're feature additions
on top of what now ships.

### anukriti-chemistry → swarm integration (post-v0.4.0)

Once anukriti-pgx-core 0.4.0 ships and CitationValidator + LLMNarrator
land in swarm, anukriti-chemistry can be added as a swarm dependency
(`pip install anukriti-chemistry[rdkit]`) consumed by LLMNarrator
to feed structured chemistry context into the grounding prompt.
At that point we tag anukriti-chemistry v1.0.0 and publish to PyPI.

---

## Resume points for the next session

If you're picking this up tomorrow or later, read this file first,
then:

### Smallest next step (~30 min)

Wire `<EvidenceBadge>` into the remaining frontend surfaces (T18
completion):
- `anukriti-main/src/pages/Simulation.jsx` per-cohort recommendation
  card
- `anukriti-main/src/components/results/TrialDecisionCard.jsx`
  top-right header badge
- `anukriti-main/src/components/results/ConfidencePanel.jsx`
  paired with the existing confidence display

Each is a 2-line addition (`import` + JSX usage). The component is
already battle-tested in `<ResultsTable>`; row data already carries
`evidence_level`.

### Next-priority engineering (half day)

F-10 CYP2C9 table fix → v0.4.0 release. Acceptance criteria are
documented in `anukriti-pgx-core/PROJECT_CONTEXT.md` F-10. The
audit script (`scripts/audit_cpic_tables.py` in the validation
repo) is the gate — when it returns 100% match, v0.4.0 is ready.

### Next-priority validation (half day)

CP-5 PharmCAT concordance, after fixing the tabix throughput issue.
Documented in `anukriti/CLINICAL_GRADE_ROADMAP.md`. Once it runs,
update `anukriti_docs/IWPC_VALIDATION_DEEP_DIVE.md §5a` with the
PharmCAT cross-validation result.

### Going-live demo path (right now)

1. Open https://product.anukritiai.com
2. Run a clopidogrel cohort (any 1000G samples)
3. Look at the Results table — every recommended row carries a
   green "A · Strong Evidence" badge
4. Hover the badge → tooltip shows "CPIC Level A — Strong Evidence"

The badge value traces back through commit hashes to the CPIC
table snapshot pinned in pgx-core 0.3.0, which traces back to
`api.cpicpgx.org/v1/pair`.

---

## Companion docs to read in order

For a complete picture of the platform after today, in reading
order:

1. **`anukriti-pgx-core/PLATFORM.md`** — the canonical three-repo map
2. **`anukriti_docs/IWPC_VALIDATION_DEEP_DIVE.md`** — engine validation
   + §5a CPIC audit findings
3. **`anukriti_docs/EVIDENCE_LEVEL_AND_LLM_CONTEXT_PLAN.md`** — the
   multi-repo plan (T1–T19); see post-2026-05-26 status annotations
4. **`anukriti-pgx-core/PROJECT_CONTEXT.md`** F-10 — the v0.4.0
   backlog item that closes the audit findings
5. **`anukriti/CLINICAL_GRADE_ROADMAP.md`** CP-5 — the PharmCAT
   concordance unblock plan
6. **`anukriti-chemistry/README.md`** — the new sibling library
7. **`anukriti-validation-iwpc/README.md`** — the standalone
   validation harness

---

## What this session is for the platform

Today moved Anukriti from "deterministic engine + audit-grade
documentation" to "deterministic engine + audit-grade documentation
+ deployed end-to-end with truth-from-engine surfacing on a real
user-facing webpage." That's the difference between "interesting
research artefact" and "credible CRO conversation."

The audit-disclosure posture (CPIC table audit, F-10 backlog,
two-release split) is the most important thing built today. It
turns the platform's central positioning — *every claim cites a
rule, every rule cites a paper, every refusal is named* — into a
defensible operational discipline rather than a marketing slogan.

Next session, the remaining work is mechanical: F-10 fix → v0.4.0
release → PharmCAT concordance → fold the EvidenceBadge into the
remaining frontend surfaces. Each piece is small. The hard
architectural decisions are all made.
