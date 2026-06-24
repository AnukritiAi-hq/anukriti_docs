# CYP2D6 Structural-Variant Pipeline (end-to-end)

> **Status:** live as of 2026-06-14. Engine shipped in **anukriti-pgx-core
> 0.6.0** (on PyPI); endpoint shipped in **anukriti-api** (`POST
> /cyp2d6/sv-ingest`); benchmark/validation lives in the **anukriti**
> research repo.
>
> This is the canonical, single-page map of the CYP2D6 SV work: what it is,
> why it exists, where each piece lives, and how to run it. Companions:
> [`RUNG2_CYP2D6_SV_PLAN.md`](RUNG2_CYP2D6_SV_PLAN.md) (the plan/roadmap) and
> [`STARPHASE_SETUP.md`](STARPHASE_SETUP.md) (the StarPhase run recipe).

---

## 1. Why this exists

CYP2D6 metabolizes ~21–25% of clinically used drugs (codeine, tamoxifen,
many antidepressants/antipsychotics). Its Ultrarapid and Poor Metabolizer
calls are driven mostly by **structural variants (SVs)** — whole-gene
deletions (`*5`), duplications (`*1xN` → UM), and CYP2D6–CYP2D7 **hybrids**
(`*36`, `*68`, `*13`) — not by simple SNVs. Because CYP2D7 shares ~94%
sequence with CYP2D6, short reads misalign and SVs are missed.

Two honest gaps motivated the work:

1. **Caller gap** — Anukriti's legacy CYP2D6 path was heuristic-only and
   mis-called SV samples (≈0.33 concordance on SV-only). PharmCAT, the
   standard benchmarked elsewhere, **cannot call CYP2D6 at all**.
2. **Truth-set gap** — the benchmark previously excluded SV samples "for
   simplicity," so CYP2D6 was being scored on exactly the cases where the
   hard problem doesn't occur.

The fix is **not** to build a new SV detector. It is to **ingest** an
external SV caller's diplotype deterministically and phenotype it the
authoritative CPIC way — keeping the platform invariant *"the LLM explains;
deterministic rules decide,"* and *"every refusal is named."*

---

## 2. The three layers (where each piece lives)

```
  external SV caller            anukriti-pgx-core 0.6.0            anukriti-api
  (StarPhase/Cyrius/   ──▶  phenotype.cyp2d6_sv_nomenclature  ──▶  POST /cyp2d6/
   StellarPGx/Aldy)         phenotype.cyp2d6_sv_ingest             sv-ingest
   emits a diplotype        normalize → activity sum → CPIC bin    (deterministic
                                                                    HTTP surface)
                                   ▲
                                   │ validated against
                            anukriti (research repo)
                            StarPhase runner + GIAB/ENA fetchers
                            scored vs GeT-RM truth set
```

### Layer A — the engine (anukriti-pgx-core 0.6.0, on PyPI)

Two modules under `anukriti_pgx_core/phenotype/`:

- **`cyp2d6_sv_nomenclature.py`** — PharmVar-pinned per-allele CPIC
  activity values + `normalize_diplotype()`. Values transcribed from the
  PharmVar CYP2D6 SV tutorial (Turner 2023, *Clin Pharmacol Ther* 114:1220;
  PMID 37669183). `*5` deletion = 0; hybrids `*13`/`*36`/`*68` = 0;
  duplications inherit per-copy function; `*41` = 0.25 (CPIC Mar-2023
  downgrade); `*22`/`*146` = uncertain (no score). The normalizer
  canonicalizes the varied strings callers emit (gene prefix, unicode `×`,
  suballele suffixes, tandem `+`, `xN`).
- **`cyp2d6_sv_ingest.py`** — `ingest_sv_diplotype(diplotype, source)` →
  `SVPhenotypeCall`. Normalizes, sums per-allele activity values (`xN`
  multiplies; `+` joins a tandem), bins per **Caudle 2020**
  (AS 0 → PM, ≤1.0 → IM, ≤2.25 → NM, >2.25 → UM). **Detects nothing,
  decides nothing, never raises.**

Public surface (top level): `ingest_sv_diplotype`, `normalize_diplotype`,
`SVPhenotypeCall`, `phenotype_from_activity_score`.

```python
>>> from anukriti_pgx_core import ingest_sv_diplotype
>>> ingest_sv_diplotype("*68+*4/*5", "StarPhase").phenotype
'Poor Metabolizer'
```

### Layer B — the HTTP endpoint (anukriti-api)

`app/routers/cyp2d6.py` → **`POST /cyp2d6/sv-ingest`**. A thin, deterministic
wrapper over the engine call. No LLM, no DB.

Request:
```json
{ "diplotype": "*68+*4/*5", "source": "StarPhase" }
```
Response:
```json
{
  "diplotype": "*68+*4/*5",
  "activity_score": 0.0,
  "phenotype": "Poor Metabolizer",
  "source": "StarPhase",
  "note": "CPIC activity score 0.0 via StarPhase (external SV call, normalized '*68+*4/*5')",
  "rule_version": "anukriti-pgx-core==0.6.0"
}
```

**Named-refusal contract:** unknown/uncertain alleles (`*22`, `*146`) and
unspecified copy counts (`*2xN`) return `phenotype: "indeterminate"`,
`activity_score: null`, and a `note` explaining the refusal — never a guess.

### Layer C — validation / benchmark (anukriti research repo)

Not a served path — kept for paper/benchmark reproducibility:
- `src/benchmark/cyp2d6_starphase_runner.py` — parse StarPhase output →
  normalize → ingest → score vs the SV truth set (SV-split + by-population).
- `scripts/fetch_giab_cyp2d6_longread.py` — remote index-slice of the
  CYP2D6 locus from GIAB HiFi BAMs (~2 MB/sample, no whole-genome pull).
- `scripts/fetch_ena_cyp2d6_longread.sh` — ENA → minimap2 → slice for the
  1000G samples (HG01190 SAS), which are FASTQ-only at ENA.
- `src/benchmark/getrm_truth.py` — GeT-RM consensus truth (Gaedigk 2019).

These import the engine from pgx-core 0.6.0; they no longer carry a copy.

---

## 3. The validated result

StarPhase 1.4.2 was run end-to-end on GIAB samples; calls fed through the
engine and scored against GeT-RM truth:

| Sample | Pop | StarPhase call | Engine phenotype | GeT-RM truth | Match |
|---|---|---|---|---|---|
| HG001 / NA12878 | EUR | `*3/*68+*4` | Poor Metabolizer | `*3/*68+*4` PM | ✅ 1.000 / 1.000 |
| HG002 | — | `*2/*4` | Intermediate Metabolizer | (not in truth set) | runs ✓ |

HG001 is a **hybrid-tandem SV** — exactly the case the legacy heuristic
mis-calls — and the StarPhase → normalize → ingest chain scored it
perfectly. The SAS equity cell (HG01190) is one ENA align/slice away (see
`STARPHASE_SETUP.md` → ENA quirk).

---

## 4. The 0.6.0 migration (2026-06-14)

The CYP2D6 SV logic was first prototyped in the **anukriti** research repo,
then migrated into **pgx-core 0.6.0** so it ships as part of the versioned,
PyPI-published engine (the same place star-allele calling, phenotype
inference, and the DPYD clinical-action tier live).

| Repo | Change |
|---|---|
| **anukriti-pgx-core** | `0.5.0 → 0.6.0`: moved both SV modules into `phenotype/`, +27 tests (132 total), published to PyPI |
| **anukriti-api** | pin `→ 0.6.0`; new `POST /cyp2d6/sv-ingest` router; +6 tests (134 total) |
| **anukriti-swarm** | pin `→ 0.6.0` (additive; 267 tests pass) |
| **anukriti** (research) | pin `→ 0.6.0`; removed the duplicate SV modules; repointed imports; README reframed as the research/benchmark sandbox |

Migration was **parity-preserving** — no phenotype-call values changed, and
HG001 still scores 1.000/1.000 after the move.

---

## 5. How to run

```bash
# Engine (anywhere, from PyPI):
pip install "anukriti-pgx-core==0.6.0"
python -c "from anukriti_pgx_core import ingest_sv_diplotype; \
print(ingest_sv_diplotype('*68+*4/*5','StarPhase').phenotype)"   # Poor Metabolizer

# Endpoint (anukriti-api, local):
ANUKRITI_AUTH_DISABLED=1 uvicorn app.main:app --port 8000
curl -X POST localhost:8000/cyp2d6/sv-ingest \
  -H 'Content-Type: application/json' \
  -d '{"diplotype":"*68+*4/*5","source":"StarPhase"}'

# Benchmark (anukriti research repo) — see STARPHASE_SETUP.md for StarPhase:
python -m src.benchmark.cyp2d6_starphase_runner --calls-dir data/giab_cyp2d6
```

---

## 6. Provenance / citations

- **PharmVar CYP2D6 SV tutorial** — Turner et al. 2023, *Clin Pharmacol
  Ther* 114(6):1220–1237 (PMID 37669183). Activity values + nomenclature.
  → `papers/Turner-2023-CPT-PharmVar-Tutorial-CYP2D6-Structural-Variation.pdf`
- **CPIC activity-score → phenotype bins** — Caudle et al. 2020, *Clin
  Transl Sci* 13:116.
- **GeT-RM consensus truth** — Gaedigk et al. 2019, *J Mol Diagn* 21:1034
  (PMID 31401124).
- **StarPhase** — Holt et al. 2024 (bioRxiv 2024.12.10.627527).
- **Method papers** — StarPhase (#14), TAS-LRS Gan 2025 (#15), ONT-AS
  Deserranno 2025 (#16) in [`papers/README.md`](papers/README.md).

---

## 7. Archived artifacts

The validation artifacts produced by Layer C (BAM slices, StarPhase JSON
calls, score files, pinned StarPhase reference DB) are backed up to Azure Blob
Storage for permanent paper references. Full manifest + per-file URLs +
reproduce/verify procedure: [`GIAB_ARTIFACT_BACKUP.md`](GIAB_ARTIFACT_BACKUP.md).
