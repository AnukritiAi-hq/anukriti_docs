# Session Resume — 2026-06-13

> Pause point captured 2026-06-13, finalized 2026-06-14 ~14:50 IST.
> Successor to `SESSION_RESUME_2026-06-08.md`.
> Resume with: "continue from SESSION_RESUME_2026-06-13.md".

One thread this session: shipping the **DPYD clinical-action tier** for
fluoropyrimidines (5-fluorouracil / capecitabine) end-to-end — a
deterministic projection of the CPIC DPYD phenotype onto a closed
clinical-action enum, surfaced from the engine through the API and into a
Molecular Tumour Board (MTB) report card in the frontend.

---

## TL;DR

| # | Workstream | Result |
|---|---|---|
| 1 | **pgx-core 0.5.0** — DPYD clinical-action tier | New `clinical_action` module + pinned table; `clinical_action` field on records |
| 2 | **anukriti-api** — thread `clinical_action` through `/runs` | adapters.py + runs.py (from-samples & from-pcr); pin bump |
| 3 | **anukriti-main** — MTB-ready DPYD card | New `MtbReportCard.jsx` + `dpydClinicalAction()` helper; mounted in overview |
| 4 | **anukriti-swarm** — pin bump | requirements.txt 0.4.1 → 0.5.0 (additive, no source changes) |

Test totals after this session: **pgx-core 105 pytest · swarm 267 pytest ·
api 128 pytest · frontend 36 vitest** — all green; frontend build clean.

---

## The clinical-action enum

CPIC 2017 guideline + Nov 2018 update (PMID 29152729). The Nov 2018 update
collapsed the AS=1.0 and AS=1.5 dose-reduction recommendations into a single
50%-starting-dose bucket.

| DPYD phenotype | Activity score | Action | Meaning |
|---|---|---|---|
| Poor Metabolizer | 0 – 0.5 | **`AVOID`** | Contraindicate fluoropyrimidines; pick an alternative not metabolised by DPD |
| Intermediate Metabolizer | 1.0 – 1.5 | **`REDUCE_50PCT`** | 50% starting dose, then titrate by toxicity / TDM |
| Normal Metabolizer | 2.0 | **`STANDARD`** | Label dosing |
| (unresolved / no drug context) | — | `INDETERMINATE` / `""` | No deterministic action |

**Core design principle (holds at every layer):** the action tier is a
*deterministic projection* of the phenotype, it **never overrides** it. The
homozygous-vs-heterozygous distinction the clinic cares about
(contraindicate vs 50% dose-reduce) is already carried by the phenotype call:
homozygous / compound-heterozygous no-function diplotypes resolve to **Poor
Metabolizer**; single no-function or decreased-function alleles to
**Intermediate Metabolizer**. The action tier just reads that phenotype.
`HapB3/HapB3` (homozygous *decreased*-function) stays Intermediate →
`REDUCE_50PCT`, not `AVOID`.

This axis is distinct from `recommendation_level` (CPIC A/B/C/D evidence
*strength*). Evidence level says "how sure is CPIC about acting here";
clinical action says "what is the act".

---

## 1. anukriti-pgx-core 0.5.0 — committed `b3e4fec`

**New module** `anukriti_pgx_core/phenotype/clinical_action.py`:
- `action_for(gene, phenotype, drug) -> str` — closed enum or `""`.
- `details_for_action(...) -> dict` — full record (action, activity-score
  range, recommendation, dose_adjustment, citations) for the MTB block / audit.
- `ACTIONS = ("AVOID", "REDUCE_50PCT", "STANDARD", "INDETERMINATE")`.
- Lazy, locked, cached table load. **Never raises** — it's on the hot
  `PhenotypeEngine.infer` path. Unknown gene/drug/phenotype → `""`.
- Drug + gene normalisation identical to `recommendation_level`
  (`5-fluorouracil` / `5_fluorouracil` resolve consistently).

**New pinned table** `phenotype/tables/DPYD_CLINICAL_ACTIONS_v2024.01.json`:
- Keyed `DPYD__fluorouracil` and `DPYD__capecitabine`, both `cpic_level: A`,
  `guideline_id 100419`, citation PMID 29152729.
- Provenance entry added (`type: cpic_clinical_actions`,
  `audit_status: needs_audit`).

**New field** `clinical_action: str = ""` on `PhenotypeInference` and
`Diplotype`. Populated only when `infer()` / `GeneCaller.call()` is given
`drug=` context **and** a phenotype→action mapping exists. Backwards-compatible.

**No phenotype-call values changed.** Additive release; zero blast radius.
105 pytest pass (29 new in `tests/test_clinical_action.py`).
CHANGELOG + version.py history updated.

## 2. anukriti-api — committed `76c1cdd`

Threaded `clinical_action` end-to-end:
- `app/adapters.py` — `call_diplotype` emits `result.clinical_action` on the
  diplotype detail block.
- `app/routers/runs.py` — carries `clinical_action` into the per-sample rows
  of **both** `/runs/from-samples` and `/runs/from-pcr` (`""` when no
  mapping / no primary gene).
- `requirements.txt` — `anukriti-pgx-core 0.4.1 → 0.5.0`.
- `tests/test_runs_smoke.py` — +1 assertion: heterozygous `*1/*2A` →
  `REDUCE_50PCT` (the heterozygous half of the clinical distinction proven
  through the API; the homozygous `*2A/*2A → AVOID` path is covered in
  pgx-core's `test_clinical_action.py` + the `call_diplotype` adapter).

128 api tests pass. (Test env: `PYTHONPATH=$PWD/../anukriti-swarm:$PWD/../anukriti-chemistry`,
`ANUKRITI_AUTH_DISABLED=1`.)

## 3. anukriti-main — committed `69a969f`

- **New** `src/components/results/MtbReportCard.jsx` — MTB-ready DPYD /
  fluoropyrimidine block. Per sample: diplotype, derived zygosity, CPIC
  phenotype, CPIC level, and a closed-enum action badge (AVOID / REDUCE 50% /
  STANDARD) with a cohort tally in the header. Renders **only** for DPYD
  workflows (`fluorouracil`, `fluorouracil_dpyd`, `capecitabine`,
  `capecitabine_dpyd`) with at least one called sample; returns `null`
  otherwise. Reads `r.clinical_action` from the backend, falling back to the
  local `dpydClinicalAction()` helper.
- `src/lib/pgxRules.js` — new exported `dpydClinicalAction(phenotype)` helper
  (single source mirrored from `clinical_action.py`); `interpretFluorouracil`
  now emits `clinical_action` + `evidence_level: "A"`.
- `src/components/results/ResultsTabs.jsx` — `<MtbReportCard>` mounted in the
  overview tab (after `PlainEnglishSummary`, before `TrialDecisionCard`).

+9 vitest (36 total green). Build clean. `dist/` is gitignored.

## 4. anukriti-swarm — committed `5227f96`

`requirements.txt` pin `anukriti-pgx-core 0.4.1 → 0.5.0`. Additive release;
**no swarm source changes needed**. Installed venv already at 0.5.0.
267 pytest pass.

---

## What's next (priority order)

1. **Redeploy anukriti-api** with the rewired `/llm-context/grounded`
   (carryover from Jun 8) **and** now the `clinical_action` field — run
   `anukriti-stack/scripts/redeploy.sh image` once the swarm source is
   bundled. Verify both `used_fallback` and `clinical_action` surface in the
   live payload.
2. **Audit the DPYD clinical-action table** — `audit_status: needs_audit`.
   Verify the pinned values against the live CPIC API generesult for
   guideline 100419 and flip to `verified` (mirrors what was done for CYP2C9
   in 0.4.0 / F-10).
3. **Rung-2 CYP2D6 SV live bake-off** — still needs external compute (WGS
   BAMs). See `anukriti_docs/RUNG2_CYP2D6_SV_PLAN.md`.
4. **Uncommitted (from Jun 8):** `anukriti_docs/papers/` has untracked PDFs.

---

## How to resume

```bash
# pgx-core — clinical-action tier tests
cd anukriti-pgx-core && source .venv/bin/activate
python -m pytest -q                          # 105 pass
python -c "from anukriti_pgx_core.phenotype.clinical_action import action_for; \
print(action_for('DPYD','Poor Metabolizer','fluorouracil'))"   # AVOID

# API — clinical_action through /runs (swarm + chemistry on PYTHONPATH)
cd anukriti-api && source .venv/bin/activate
export PYTHONPATH="$PWD/../anukriti-swarm:$PWD/../anukriti-chemistry"
ANUKRITI_AUTH_DISABLED=1 python -m pytest -q   # 128 pass

# Frontend — MTB card + tests
cd anukriti-main
npx vitest run                               # 36 pass
npm run build

# Swarm — regression after the pin bump
cd anukriti-swarm && source venv/bin/activate
python -m pytest -q                          # 267 pass
```

---

## Canonical doc links

- `ANUKRITI_FULL_CONTEXT.md` (repo root) — complete platform overview
- `anukriti-pgx-core/CHANGELOG.md` — 0.5.0 DPYD clinical-action tier entry
- `anukriti_docs/DPYD_ONCOLOGY_DEEP_DIVE.md` — DPYD/fluoropyrimidine domain context
- `anukriti_docs/RUNG2_CYP2D6_SV_PLAN.md` — the CYP2D6 SV bake-off plan
- `anukriti_docs/SESSION_RESUME_2026-06-08.md` — prior session resume
