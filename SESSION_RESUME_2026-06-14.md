# Session Resume — 2026-06-14

> Captured 2026-06-14 ~18:00 IST. Successor to
> `SESSION_RESUME_2026-06-13.md` (DPYD clinical-action tier).
> Resume with: "continue from SESSION_RESUME_2026-06-14.md".

Two threads this session: (1) the **CYP2D6 structural-variant pipeline** —
built, validated end-to-end against StarPhase on real GIAB long-read data,
then **migrated into pgx-core 0.6.0** (published to PyPI) and exposed via a
new **anukriti-api endpoint**; and (2) clarifying + cleaning the platform's
two-stack architecture (the `anukriti` research repo vs the `anukriti-api`
production backend).

---

## TL;DR

| # | Workstream | Result |
|---|---|---|
| 1 | CYP2D6 SV engine | `cyp2d6_sv_nomenclature` + `cyp2d6_sv_ingest` → **pgx-core 0.6.0** (PyPI) |
| 2 | StarPhase validation | HG001 `*3/*68+*4` → PM, **1.000/1.000** vs GeT-RM (real GIAB HiFi) |
| 3 | API endpoint | **`POST /cyp2d6/sv-ingest`** in anukriti-api (deterministic, named-refusal) |
| 4 | Dep bumps | api + swarm pinned → pgx-core 0.6.0 |
| 5 | Repo cleanup | `anukriti` repo: removed duplicate SV modules, reframed as research sandbox |
| 6 | Docs | `CYP2D6_SV_PIPELINE.md`, `STARPHASE_SETUP.md`, Rung-2 plan, papers #14–#17 |

Test totals: **pgx-core 132 · api 134 · swarm 267 · anukriti SV/benchmark 46** —
all green.

---

## 1. The CYP2D6 SV pipeline (the main thread)

See [`CYP2D6_SV_PIPELINE.md`](CYP2D6_SV_PIPELINE.md) for the canonical map.
Briefly:

- **Why:** CYP2D6 (~21–25% of drugs) is driven by SVs (deletions/dups/
  hybrids), which the legacy heuristic mis-calls (~0.33 SV concordance) and
  PharmCAT can't call at all. The fix is to **ingest** an external SV
  caller's diplotype deterministically, not build a new detector.
- **Engine (pgx-core 0.6.0):** `ingest_sv_diplotype(diplotype, source)`
  normalizes to PharmVar form, sums per-allele CPIC activity values
  (PharmVar tutorial Turner 2023), bins per Caudle 2020. Named refusal on
  uncertain/unknown alleles + unspecified copy counts.
- **Validation:** installed StarPhase 1.4.2 via conda, sliced the CYP2D6
  locus from GIAB HiFi BAMs remotely (~2 MB/sample via the BAM index — no
  whole-genome pull), ran StarPhase, scored vs GeT-RM. **HG001/NA12878
  hybrid-tandem `*3/*68+*4` → Poor Metabolizer, exact match (1.000/1.000).**

### Validation gotchas worth remembering

- **`pbstarphase build` is broken** against the live CPIC API
  (`invalid type: map…`). Use the **prebuilt DB** from the pb-StarPhase repo
  `data/v1.4.0/pbstarphase_20250515.json.gz`. (Documented in STARPHASE_SETUP.md.)
- **HG01190 (SAS) is NOT on GIAB** — it's a 1000G line; long-read data is
  raw FASTQ-only at **ENA SRR25583344** (ArrayExpress E-MTAB-15248). No
  index → can't remote-slice → must download 7.6 GB + minimap2-align whole
  genome first. Turnkey script: `anukriti/scripts/fetch_ena_cyp2d6_longread.sh`.
- **HG005 has no GeT-RM consensus** (absent from Gaedigk 2019 Tables 3/4) —
  deliberately NOT added to the truth set (would fabricate truth).
- **Data bug found + fixed:** the base truth set had NA12878 = `*1/*1`
  Normal Metabolizer (SV-blind, wrong); removed in favor of the
  authoritative `*3/*68+*4` PM. Truth counts now: overall 36, SV 8, non-SV 28.

---

## 2. pgx-core 0.6.0 — published

`b3e4fec` (0.5.0) → migration commit `26e6240` → tag `v0.6.0` → release.yml
(trusted publishing: tests 3.11/3.12 → build → TestPyPI → manual approval →
PyPI). **Live on PyPI; install + `ingest_sv_diplotype` verified.**

- New: `phenotype/cyp2d6_sv_nomenclature.py`, `phenotype/cyp2d6_sv_ingest.py`.
- Public surface exported at package top level.
- +27 tests (132 total). Additive; no existing phenotype-call values changed.

---

## 3. anukriti-api — `POST /cyp2d6/sv-ingest`

`app/routers/cyp2d6.py` — `SvIngestBody{diplotype, source}` →
`SvIngestResponse{diplotype, activity_score, phenotype, source, note,
rule_version}`. Deterministic; calls `anukriti_pgx_core.ingest_sv_diplotype`.
Wired into `main.py`. +6 tests (134 total). pin → 0.6.0.

> **Not yet redeployed to Azure.** The live revision (0000031) predates this
> endpoint. Redeploy via `anukriti-stack/scripts/redeploy.sh image` to ship it.

---

## 4. Architecture clarification (the second thread)

The platform has **two stacks sharing pgx-core**, which is easy to confuse:

- **Production:** `anukriti-main` (Vercel) → `anukriti-api` (Azure) →
  fuses pgx-core + swarm + chemistry. **This is the backend.**
- **Research/origin:** the **`anukriti`** repo (FastAPI + Streamlit) — the
  *ancestor* the engine was extracted from (locked by
  `test_anukriti_parity.py` in pgx-core). Now **not deployed live**; reframed
  as the research/benchmark sandbox. Today's CYP2D6 benchmark harness lives
  here.

The clean line is: **engine → pgx-core · backend → anukriti-api · this repo →
reproducibility.** The 0.6.0 migration moved the engine logic to the right
side of that line.

---

## What's next (priority order)

1. **Redeploy anukriti-api** with `/cyp2d6/sv-ingest` (Azure, via
   `anukriti-stack/scripts/redeploy.sh image`); verify the endpoint live.
2. **Wire the SAS cell:** run `fetch_ena_cyp2d6_longread.sh` on EC2/local to
   produce HG01190's slice → StarPhase → score (closes the equity row).
3. Optionally surface CYP2D6 SV calls in the frontend (anukriti-main).

---

## How to resume

```bash
# Engine (PyPI):
pip install "anukriti-pgx-core==0.6.0"

# API endpoint:
cd anukriti-api && source .venv/bin/activate
export PYTHONPATH="$PWD/../anukriti-swarm:$PWD/../anukriti-chemistry"
ANUKRITI_AUTH_DISABLED=1 python -m pytest -q           # 134 pass
ANUKRITI_AUTH_DISABLED=1 uvicorn app.main:app --port 8000
curl -X POST localhost:8000/cyp2d6/sv-ingest \
  -d '{"diplotype":"*68+*4/*5","source":"StarPhase"}'  # Poor Metabolizer

# Benchmark + StarPhase: see STARPHASE_SETUP.md
```

---

## Canonical doc links

- `CYP2D6_SV_PIPELINE.md` — the end-to-end map (engine + endpoint + benchmark)
- `STARPHASE_SETUP.md` — verified <30-min StarPhase run procedure + ENA quirk
- `RUNG2_CYP2D6_SV_PLAN.md` — the plan/roadmap (Phase A/B′/C)
- `papers/README.md` — method papers #14–#17 (StarPhase, TAS-LRS, ONT-AS, PharmVar)
- `SESSION_RESUME_2026-06-13.md` — prior session (DPYD clinical-action tier)
