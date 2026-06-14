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

---

## Commit ledger (2026-06-14) — exact SHAs to resume from

All repos clean + pushed. Today's commits, newest last per repo:

| Repo | SHA | Summary |
|---|---|---|
| anukriti-pgx-core | `26e6240` | **release v0.6.0** — CYP2D6 SV ingestion (tag `v0.6.0`, on PyPI) |
| anukriti | `76339ce` | pin CYP2D6 SV nomenclature + normalizer (PharmVar 2023) |
| anukriti | `241b2e6` | StarPhase scoring runner (Phase B′) |
| anukriti | `d34ed48` | GIAB CYP2D6 long-read region fetcher |
| anukriti | `a35e4b2` | parse real StarPhase schema; HG002 verified e2e |
| anukriti | `765a43d` | HG001 GeT-RM truth + first scored row; ENA runner |
| anukriti | `f9f7d29` | consume SV modules from pgx-core 0.6.0; sandbox README |
| anukriti-api | `76c1cdd` | DPYD `clinical_action` through `/runs` |
| anukriti-api | `dbcc0ef` | **`POST /cyp2d6/sv-ingest`** endpoint (pgx-core 0.6.0) |
| anukriti-swarm | `5227f96` → `0a920a3` | pin → 0.5.0 → 0.6.0 |
| anukriti-main | `ee2c6da` | MTB-ready DPYD clinical-action card |
| anukriti_docs | `24ebaf8 … ce4f421` | papers #14–#17, plan reframe, STARPHASE_SETUP, CYP2D6_SV_PIPELINE, this resume |

## Live deployment state (end of 2026-06-14)

- **pgx-core 0.6.0** — published on PyPI ✅
- **anukriti-api** — Azure Container App revision **`anukriti-api--0000032`**,
  image `git-dbcc0ef-0a920a-fd8601-26e624`, 100% traffic. `/cyp2d6/sv-ingest`
  live in OpenAPI (auth-enforced). DPYD `clinical_action` also live.
- **anukriti-main** — Vercel, product.anukritiai.com (base44 + DPYD MTB card).
- **anukriti (research repo)** — not deployed (sandbox); CYP2D6 benchmark
  harness lives here, runs locally.

Test totals (all green): pgx-core **132** · api **134** · swarm **267** ·
anukriti SV/benchmark **46**.


---

## Addendum (later 2026-06-14) — shipped past the migration

All committed + pushed; all 8 repos clean.

| What | Where | Commit |
|---|---|---|
| **Azure redeploy** with the new endpoint | anukriti-api rev **`0000032`**, image `git-dbcc0ef-0a920a-fd8601-26e624` | (deploy) |
| `/cyp2d6/sv-ingest` **verified live** in OpenAPI (auth-enforced) | Azure | — |
| Frontend **api client wire** `api.cyp2d6.svIngest()` | anukriti-main `src/lib/api.js` | `b971c61` |
| **Paper draft v0.3** (CYP2D6/DPYD/warfarin validation) | `papers/2026-06-14-cyp2d6-dpyd-warfarin-validation-DRAFT-v0.3.md` | `47a3257` |
| **`AZURE_VM_SETUP.md`** — genomics compute sandbox runbook | anukriti_docs | `8229116` |

Decisions locked:
- **DPYD fully wired** to the frontend (MtbReportCard, live). **CYP2D6 SV has
  NO UI surface** — deliberate design task for when a long-read input flow
  exists; the api client helper is enough for now.
- **Paper draft** has an editor's fact-check note (PyPI 0.6.0 not 0.2.1;
  corrected Turner 2023 + Gaedigk citations; warfarin stat method still open).
  Tracked in `papers/`, not the gitignored `drafts/`.
- **Azure VM** = `Standard_D16s_v5` (16 vCPU/64 GB), 512 GB Premium SSD + Blob.
  First job documented: HG01190 (SRR25583344) → minimap2 → slice → StarPhase
  → score. The ENA path needs the **full** GRCh38 FASTA (whole-genome
  alignment), unlike the chr22-only local StarPhase path.

**Single open external step:** spin up the Azure VM per `AZURE_VM_SETUP.md`
and run HG01190 to fill the SAS equity row (expect 1.000/1.000). Everything
else is shipped and live.


---

## Addendum 2 (2026-06-14 ~22:10) — Azure VM provisioned + HG01190 SAS run

**Provisioned the genomics compute sandbox** (per `AZURE_VM_SETUP.md`) and ran
the first job end-to-end.

- **VM:** `anukriti-lrs-01`, `Standard_D16s_v5`, Ubuntu 22.04, **centralindia**,
  RG `anukriti-genomics-rg`, IP `20.198.83.214`. 512 GB Premium SSD at
  `/mnt/work`. SSH locked to my IP. Storage `anukritigx3533` / container
  `genomics-archive` mounted via BlobFuse2 at `/mnt/work/archive`.
- **Toolchain:** conda + `lrs` env (minimap2 2.31, samtools 1.23.1) + `starphase`
  env (pbstarphase 1.4.2) + full GRCh38 + chr22 + StarPhase prebuilt DB.
  (Gotcha hit: new conda needs `conda tos accept` for Anaconda channels.)
- **Repo on VM:** `Abm32/Synthatrial` is private → cloned failed; copied the
  ENA script + benchmark package via scp instead. Benchmark `__init__.py`
  emptied so the runner imports standalone.
- **HG01190 job:** ENA SRR25583344 (7.6 GB) → minimap2 whole-genome →
  CYP2D6 slice (373 reads) → StarPhase → score. Ran detached.

**RESULT (the SAS equity cell):**
- StarPhase: `*68+*4x2/*68+*4` → **Poor Metabolizer**
- GeT-RM truth: `*68+*4/*5` → Poor Metabolizer
- **Phenotype concordance 1.000** (correct PM); **diplotype concordance 0.000**
  (StarPhase resolved a different but all-no-function SV configuration).
  Honest result: functionally equivalent, structurally divergent. 3-sample
  table now phenotype 1.000, diplotype 0.667 (2/3).

**Housekeeping:** whole-genome BAM (7.7 GB) archived to Blob; HG01190 slice +
StarPhase JSON + score copied to `anukriti/data/giab_cyp2d6/` (gitignored).
**VM DEALLOCATED** (compute billing stopped; disks + Blob retained — restart
with `az vm start -g anukriti-genomics-rg -n anukriti-lrs-01`).

Paper updated to **v0.4** (`ededa7b`) with the real SAS result.

**Next:** AFR (NA19317) + EAS (NA18545) cells via the same VM path; warfarin
stat method; consider orthogonal confirmation of the HG01190 structural call.
To fully tear down: `az group delete -n anukriti-genomics-rg --yes`.


---

## Addendum 3 (2026-06-14 ~22:15) — AFR/EAS cells: data investigation (no run)

Investigated long-read data for the remaining truth-set ancestry cells
**before** spending VM compute. Finding: the obvious ENA sources are NOT
usable, so I did **not** run them (a run would produce no CYP2D6 coverage →
no-call, wasting compute).

| Sample | Pop | Truth | Best ENA long-read found | Verdict |
|---|---|---|---|---|
| NA19317 | AFR | `*5/*5` → PM | ERR12095532 (PRJEB66174, PromethION) | ❌ **17 reads / 56 kb** — empty/placeholder run |
| NA18545 | EAS | `*5/*36x2+*10x2` → IM | ERR14901054 (PRJEB82358, Sequel II) | ❌ **WGA, 67k reads, ~0.04× genome** — won't cover the locus |

Neither is the multi-Gb WGS long-read dataset that worked for HG01190
(SRR25583344). They are NOT in PRJNA1003794 (the Deserranno project, which
only covered HG001/HG002/HG005/HG01190/NA19785).

**Concrete follow-up path (next session):** HPRC (Human Pangenome Reference
Consortium) has PacBio HiFi + ONT WGS for 232 diverse 1000G individuals incl.
AFR/EAS ancestries — the right source for proper AFR/EAS long-read WGS.
Action: check HPRC sample list for truth-set overlap (or pick HPRC AFR/EAS
samples with published GeT-RM/PharmVar CYP2D6 truth), then run via the same
VM path. https://humanpangenome.org/hprc-data-release-2

**Current honest table:** EUR ×2 (HG001, HG002) + SAS ×1 (HG01190). AFR/EAS
cells remain open pending a proper long-read source — documented, not faked.


---

## Addendum 4 (2026-06-14 ~22:30) — HPRC overlap resolved: EAS cell runnable, AFR/EAS-SV blocked

Followed Addendum 3's pointer and **resolved the HPRC question concretely**.
Baseline first re-verified: VM `anukriti-lrs-01` **deallocated** (no compute
billing), RG `anukriti-genomics-rg` clean (no stray/duplicate resources from
the interrupted redeploy — the unexpected shutdown happened before any Azure
object was created), all active repos clean + tracking remotes.

### What I checked
Pulled the HPRC Release 2 sequencing index tables
(`human-pangenomics/hprc_intermediate_assembly` → `data_tables/sequencing_data/`)
and cross-referenced **all 232 HPRC samples** (every one has HiFi ~60x + ONT
~30x) against the GeT-RM CYP2D6 truth set in
`anukriti/src/benchmark/getrm_truth.py`. HPRC data is on the **public,
no-sign-request** bucket `s3://human-pangenomics/` — verified anonymously
listable (`aws s3 --no-sign-request ls …`), so the VM can pull it directly.

### Findings (verified against the index CSVs)

| Truth sample | Pop | CYP2D6 truth | In HPRC? | Verdict |
|---|---|---|---|---|
| **NA19317** | AFR | `*5/*5` → PM (**SV**) | ❌ not in HPRC | AFR-SV cell still blocked |
| **NA18545** | EAS | `*5/*36x2+*10x2` → IM (**SV**) | ❌ not in HPRC | EAS-SV cell still blocked |
| HG00097 | EUR | `*1/*41` → NM (non-SV) | ✅ HiFi+ONT | redundant (EUR already covered) |
| HG00099 | EUR | `*1/*4` → NM (non-SV) | ✅ HiFi+ONT | redundant (EUR already covered) |
| **NA18959** | **EAS** | `*1/*1` → NM (**non-SV**) | ✅ HiFi+ONT | **RUNNABLE — fills the EAS *ancestry* cell** |

Only **3** GeT-RM CYP2D6 truth samples overlap HPRC, and **NA18959 is the
only non-EUR overlap**. There is **no AFR overlap at all**.

### Honest read of what this gets us
- NA18959 closes the **EAS ancestry** cell, but it is a **non-SV `*1/*1`**
  case — it does **not** close an EAS *structural-variant* cell. Expectation
  is a clean `*1/*1` → Normal Metabolizer (phenotype 1.000, diplotype 1.000).
- The two genuinely-SV equity targets (NA18545 EAS, NA19317 AFR) remain
  **blocked**: not in HPRC, and (per Addendum 3) no usable public long-read
  WGS on ENA. Not faked — documented as open.

### Concrete run path (next VM session) — EAS via NA18959
New turnkey script committed: **`anukriti/scripts/fetch_hprc_cyp2d6_longread.sh`**
(mirrors the ENA HG01190 script; differences: public-S3 source via
`aws s3 --no-sign-request`, **PacBio HiFi** so minimap2 preset is `map-hifi`,
4 input FASTQs ~80 GB total streamed into one alignment).

```bash
az vm start -g anukriti-genomics-rg -n anukriti-lrs-01      # restart sandbox
# on the VM (lrs env: minimap2, samtools, awscli):
THREADS=16 ./scripts/fetch_hprc_cyp2d6_longread.sh /mnt/work/GRCh38.fa data/giab_cyp2d6
conda activate starphase
pbstarphase diplotype --database pbstarphase_db.json --reference chr22.fa \
  --bam data/giab_cyp2d6/NA18959_CYP2D6_GRCh38.bam \
  --include-set include_cyp2d6.txt \
  --output-calls data/giab_cyp2d6/NA18959.starphase.json
python -m src.benchmark.cyp2d6_starphase_runner --calls-dir data/giab_cyp2d6
az vm deallocate -g anukriti-genomics-rg -n anukriti-lrs-01  # stop billing
```
Source paths (verified live on the public bucket):
- HiFi: `s3://human-pangenomics/submissions/B25289BC-5C70-4C42-B2EC-6E742BC82EE1--AMED_HPRC_collaboration/NA18959/raw_data/PacBio_HiFi/` (4 FASTQs)
- ONT (optional 2nd-tech confirm): `s3://human-pangenomics/working/HPP/AMED/NA18959/raw_data/nanopore/`

### Remaining true blockers (for AFR + EAS-SV)
NA19317 (AFR-SV) and NA18545 (EAS-SV) need a long-read WGS source that
neither ENA nor HPRC provides. Next leads to try: AoU/1000G-ONT releases,
PharmVar-cited datasets, or substituting a *different* AFR/EAS GeT-RM **SV**
sample that does appear in HPRC's 232 (none of the current truth-set SV IDs
do — would require adding a new HPRC AFR/EAS sample with independently
published CYP2D6 SV truth to `getrm_truth.py`).

### Table state after the NA18959 run would be
EUR ×2 (HG001, HG002, both SV) + SAS ×1 (HG01190, SV) + **EAS ×1 (NA18959,
non-SV)**. AFR cell and any EAS/AFR *SV* cell remain open — honestly.

### Housekeeping noted (not done)
- Stray `HG01190.bam.bai` in the workspace root (`SynthaTrial-repo/`) —
  leftover from the HG01190 run; safe to delete.
- The orphaned parent-dir git repo at `SynthaTrial-repo/` (no remote, legacy
  wrapper showing 521 deletions) is **not** one of the active repos; left as-is.
