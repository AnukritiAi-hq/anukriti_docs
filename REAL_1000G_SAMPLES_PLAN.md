# Real 1000 Genomes samples mode — implementation plan

> **Scope:** Add a third VCF source to the simulation page —
> **"1000 Genomes samples (real)"** — backed by genotypes pre-resolved
> once from `s3://1000genomes/release/20130502/` and stored in MongoDB.
> Two new backend endpoints. One new frontend panel. The existing
> synthetic-cohort and CSV-upload flows are unchanged.
>
> **Status:** Plan agreed (founder call, 2026-05-17). Not started.
>
> **Companions:**
>   - `FRONTEND_BACKEND_CUTOVER_PLAN.md` — the broader cohort-on-server plan; this is its first wedge
>   - `IDEA_REFINEMENT_AND_PHASING_2026-05-14.md` Phase A — the strategic anchor (PharmCAT concordance, real-data credibility)
>   - `SESSION_RESUME_2026-05-16.md` Task A2 — the PharmCAT extraction work that shares this primitive
>   - `THREE_REPO_INTEGRATION_DEEP_DIVE.md` — repo topology this plan respects
>   - `anukriti/src/benchmark/pharmcat_comparison.py:191` — `extract_sample_variants()` exists; this plan generalises it

---

## Why this exists

> *"Where does the data come from?"* is the first technical-DD
> question. Today the answer is: synthetic Hardy-Weinberg over
> published frequencies. This adds a path where the answer is:
> **sample HG00125, ITU sub-population, 1000 Genomes Project
> Consortium, Nature 2015**.

Founder argument: synthetic is the right path for fast iteration
(slider-drag in Compare, weekly-refreshed allele tables). Real
samples are the right path for the credibility moment in front of
a CRO scientific lead or an investor. **Both flows ship; both are
honestly labelled.**

Same indexing primitive feeds the PharmCAT concordance run that's
been blocked since session #16, so this clears two debts.

## What ships

| Surface | Change |
|---|---|
| Frontend `VcfSourceSelector` | Third option: **"1000 Genomes samples (real)"**. |
| Frontend new component `RealSamplesPanel.jsx` | Filter by superpop → choose `random N samples` OR paste sample-IDs → preview list → run. |
| Frontend `Results` metadata | Selected sample IDs surfaced (e.g. "Run on: HG00096, HG00097, HG00099, …"). |
| Backend new endpoint `GET /samples/1000g` | Paginated list with population/superpop/workflow filters. |
| Backend new endpoint `POST /runs/from-samples` | `{workflow, sample_ids[]}` → `UnifiedExecutionReport` shape, same as `/runs`. |
| Backend new MongoDB collection `samples_1000g` | One doc per (sample_id, workflow) — pre-resolved genotypes. ~30 KB total. |
| Indexing job `anukriti-pgx-core/scripts/index_1000g_samples.py` | Resolves all 2,504 × workflow-rsIDs once; dumps `data/1000g_phase3_resolved.jsonl`. Idempotent. |
| Loader script `anukriti-api/app/scripts/load_samples.py` | Loads the JSONL artifact into MongoDB. Run on container startup if collection is empty. |
| Tests | `test_samples_endpoint.py`, `test_runs_from_samples.py` — 8 cases combined. |
| `DemoKit.jsx` | Demo script gains a real-samples ACT — credibility framing. |

**Out of scope** (deferred): user VCF upload (Option C); per-request `bcftools` extraction (Option B); the user-supplied VCF-engine URL the founder mentioned for a separate problem.

---

## Data shape

### MongoDB collection — `samples_1000g`

One document per (sample_id, workflow) pair. **2,504 samples × 3 workflows = 7,512 documents.** Each ~250 bytes → ~1.9 MB total. Trivially fits in any Mongo plan.

```js
{
  _id: ObjectId(...),
  sample_id: "HG00096",                    // canonical 1000G ID
  population: "GBR",                       // 26-pop code
  superpopulation: "EUR",                  // 5-superpop code
  sex: "male",                             // from 1000G pedigree
  workflow: "clopidogrel",                 // {clopidogrel, warfarin, simvastatin}
  rsid_genotypes: {                        // pre-resolved alts
    "rs4244285":  "GG",
    "rs4986893":  "GG",
    "rs12248560": "CT",
    "rs17884712": "GG",
  },
  source: {
    release: "20130502",                   // 1000G phase-3 release timestamp
    vcf_files: ["ALL.chr10.phase3_..."],   // which chr-VCFs this sample's row was extracted from
    indexed_at: "2026-05-18T09:00:00Z",
    indexer_version: "1.0.0",
    pgx_core_version: "0.2.1",
  },
}
```

Indexes: `{sample_id: 1, workflow: 1}` unique, `{superpopulation: 1, workflow: 1}`, `{population: 1, workflow: 1}`.

### Backend endpoint contracts

#### `GET /samples/1000g`

Query params:
| Param | Type | Notes |
|---|---|---|
| `workflow` | string | required — `clopidogrel|warfarin|simvastatin` |
| `superpopulation` | string | optional — `AFR|AMR|EAS|EUR|SAS` |
| `population` | string | optional — 26-pop code (`GIH`, `ITU`, …) |
| `limit` | int | default 100, max 500 |
| `offset` | int | default 0 |
| `random` | int | optional — if set, returns N random samples instead of paginated; ignores `limit`/`offset` |

Response (200):
```json
{
  "workflow": "clopidogrel",
  "filter": { "superpopulation": "SAS" },
  "total": 489,
  "returned": 50,
  "samples": [
    {
      "sample_id": "HG00125",
      "population": "GIH",
      "superpopulation": "SAS",
      "sex": "male",
      "rsid_genotypes": { "rs4244285": "GA", "rs4986893": "GG", ... }
    },
    ...
  ]
}
```

Auth: **public** as of the simulation-public-by-default policy
(2026-05-17, see `anukriti-api d9db971` and
[`anukriti-stack/DEPLOYMENT.md`](https://github.com/AnukritiAi-hq/anukriti-stack/blob/main/DEPLOYMENT.md#auth-policy-public-reads--cohort-runs--private-user-owned-state)
"Auth policy" section). The 1000 Genomes data is public research
data, and the per-key rate limit is bypassed for non-billable
public routes; abuse is bounded by Container Apps default scaling
and IP rate-limiting can be added in front of the api when needed.

#### `POST /runs/from-samples`

Body:
```json
{ "workflow": "clopidogrel", "sample_ids": ["HG00125", "HG00126", "NA20502"] }
```

Behaviour:
1. Look up each `(sample_id, workflow)` in the collection.
2. For each found sample, build a row identical to what the synthetic generator produces (rsID columns + ancestry_group + patient_id == sample_id).
3. Run the swarm runtime over the cohort exactly like `/runs` does today (re-using `get_runtime()` singleton from `app/adapters.py`).
4. Return `UnifiedExecutionReport`-shaped response, but augmented with:
   ```json
   {
     ...,
     "data_source": {
       "type": "1000g_real",
       "release": "20130502",
       "sample_count": 50,
       "sample_ids": ["HG00125", ...],
       "missing_sample_ids": []        // populated if any IDs weren't found
     }
   }
   ```

Auth: **public** (same policy as `GET /samples/1000g` above).
Invalid keys are silently ignored on public routes — stale
localStorage tokens never break the demo flow.

Errors:
- `400 invalid_workflow` — bad workflow.
- `400 too_many_samples` — len > 500.
- `400 no_samples_found` — every requested ID missing.
- `404 partial_match` — when ≥1 IDs missing AND `strict=true` query param set (default false).

### Frontend wire format (no change)

The frontend's `api.runs.create()` body shape is unchanged. `api.runs.fromSamples()` is a new method on the same client:

```js
api.runs.fromSamples({ workflow, sample_ids })   // POST /runs/from-samples
api.samples.list1000g({ workflow, superpopulation, random })  // GET /samples/1000g
```

---

## Indexing job design

### Where it lives

`anukriti-pgx-core/scripts/index_1000g_samples.py` — pgx-core is the right home because:
- The rsID definitions are pgx-core's domain (it owns `WORKFLOW_RSIDS` semantics, even if the api also has a copy for adapter validation).
- The job is run-once-per-pgx-core-release; tying the indexer version to pgx-core version makes the cadence cohere.
- Other consumers (anukriti, anukriti-stack benchmarks) can import from it.

### Inputs

```python
# anukriti-pgx-core/scripts/index_1000g_samples.py

WORKFLOW_RSIDS = {              # mirror of api/adapters.py — single-source TBD
    "clopidogrel": {"rs4244285", "rs4986893", "rs12248560", "rs17884712"},
    "warfarin":    {"rs1799853", "rs1057910", "rs9923231",
                    "rs2108622", "rs28371686", "rs9332131"},
    "simvastatin": {"rs4149056", "rs56101265"},
}

# rsID → (chromosome, GRCh37 position) — needed for tabix region extraction
RSID_LOCUS = {
    "rs4244285":   ("10", 96541616),
    "rs4986893":   ("10", 96540410),
    "rs12248560":  ("10", 96522463),
    "rs17884712":  ("10", 96602623),
    "rs1799853":   ("10", 96702047),
    "rs1057910":   ("10", 96741053),
    "rs28371686":  ("10", 96741058),  # CYP2C9*5
    "rs9332131":   ("10", 96741066),  # CYP2C9*6
    "rs9923231":   ("16", 31107689),
    "rs2108622":   ("19", 15990431),
    "rs4149056":   ("12", 21331549),
    "rs56101265":  ("12", 21331568),
}

# 1000G phase-3 release URLs — public AWS Open Data
# https://registry.opendata.aws/1000-genomes/
PHASE3_VCF_URLS = {
    "10": "http://1000genomes.s3.amazonaws.com/release/20130502/ALL.chr10.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz",
    "12": "http://1000genomes.s3.amazonaws.com/release/20130502/ALL.chr12.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz",
    "16": "http://1000genomes.s3.amazonaws.com/release/20130502/ALL.chr16.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz",
    "19": "http://1000genomes.s3.amazonaws.com/release/20130502/ALL.chr19.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz",
}

# Pedigree (sample_id → population, superpopulation, sex) — small file, downloaded once
PEDIGREE_URL = "http://1000genomes.s3.amazonaws.com/release/20130502/integrated_call_samples_v3.20130502.ALL.panel"
```

### Algorithm

```
1. Download integrated_call_samples_v3.20130502.ALL.panel  (~80 KB).
   Build sample_id → {population, superpopulation, sex} dict.
   Result: 2,504 samples.

2. For each chromosome (10, 12, 16, 19):
   a. For each rsID on that chromosome:
      bcftools view -r {chrom}:{pos}-{pos} {PHASE3_VCF_URL[chrom]} | \
        bcftools query -f '%ID\t%CHROM\t%POS\t%REF\t%ALT[\t%SAMPLE=%GT]\n'
      (or use pyvcf2 / cyvcf2 directly for cleaner Python; see deps section)
   b. Each row yields ref, alt, and per-sample genotype string ('0|0', '0|1', '1|1').
   c. Translate to nucleotide pair: ref+ref / ref+alt / alt+alt.

3. Collate per (sample_id, workflow):
   For each sample, for each workflow, gather the resolved genotypes for
   that workflow's rsIDs. Skip samples with any required-rsID missing
   (rare — all phase-3 samples should have every common rsID).

4. Write data/1000g_phase3_resolved.jsonl — one JSON-line per
   (sample_id, workflow) document. ~7,500 lines. Idempotent — same input,
   byte-identical output.

5. Print summary:
   2,504 samples loaded
   Per workflow:
     clopidogrel: 2,504 / 2,504 fully resolved
     warfarin:    2,500 / 2,504 (4 missing rs28371686 — decisively rare in 1000G)
     simvastatin: 2,504 / 2,504
```

### Dependencies

- **`bcftools` 1.18+** — required system binary. **Or** `cyvcf2` + `pysam` Python wheels. The Python route is more portable (no system install needed in the Container Apps image), so default to it.
- **`requests`** for the pedigree download.
- **No AWS credentials needed** — bucket is public-anonymous.

### Where it runs

- **Locally first** (or on a workstation with `bcftools`/`cyvcf2`) by the founder, once per pgx-core release, **with the resulting JSONL committed to the repo** (`anukriti-pgx-core/data/1000g_phase3_resolved.jsonl`, ~2 MB gzipped).
- The Container Apps image already has the JSONL (because pgx-core's `data/` ships in the wheel). On first boot, the loader script seeds MongoDB if `samples_1000g` is empty.
- **The job is not on the request path.** No AWS calls happen at run-time. The container app talks only to MongoDB Atlas + (Vellum/Gemini, for the LLM-explainer).

This is critical: it means the production deploy doesn't need network egress to `s3://1000genomes/`, doesn't need `bcftools` in the runtime image, doesn't have a cold-start hit on first user.

### Idempotency

The job writes to `data/1000g_phase3_resolved.jsonl.tmp`, validates row count and SHA256, then atomic-renames to the final path. Re-running with the same pgx-core version produces a byte-identical file. The `--force` flag re-extracts even if the output exists.

---

## Frontend UX

### `VcfSourceSelector` — third card

```text
┌─────────────────────────────────────────────────────┐
│ ⬆  Upload CSV                          [Quick path] │
│    Upload your own cohort CSV or load demo data.    │
├─────────────────────────────────────────────────────┤
│ 🗄️  Synthetic cohort (1000G phase-3 frequencies)    │
│    [Synthetic]                                      │
│    Generate rows locally from published allele      │
│    frequencies. No external service is called.      │
├─────────────────────────────────────────────────────┤
│ 🧬  1000 Genomes samples (real)        [Real data]  │
│    Pre-resolved genotypes from 2,504 phase-3        │
│    samples. Source: 1000 Genomes Project, Nature    │
│    2015 (PMID:26432245).                            │
└─────────────────────────────────────────────────────┘
```

### `RealSamplesPanel.jsx` (new)

Three things stacked:
1. **Filter row** — superpopulation dropdown (`AFR/AMR/EAS/EUR/SAS`), live count badge from `GET /samples/1000g?workflow=…&superpop=…&limit=0` (returns just the total).
2. **Sample-selection mode toggle** — two buttons:
   - **"Random N samples"** — number input (default 50, max 500) + Generate button → calls `GET /samples/1000g?random=N` → preview shows the IDs.
   - **"Pick by ID"** — multiline text input where the user pastes/types `HG00096, HG00097, NA12878` → preview shows resolved + missing.
3. **Preview list** — collapsible card showing the sample IDs that will be sent (with population badge per row, max 50 rows visible, "show all N" expander).

When the user clicks **Run Deterministic Simulation**, the page calls `api.runs.fromSamples({ workflow, sample_ids })`. The result is identical-shaped to a synthetic-cohort run (so `Results.jsx` doesn't need changes), but with two surfaces:

- A new badge on the metadata row: **"Real 1000 Genomes phase-3"** (green, distinct from the synthetic badge).
- The metadata block lists the sample IDs (collapsed by default behind a "Selected samples (N)" expander).

### `Results.jsx` metadata changes

Add one row to the metadata block:
- "Sample IDs" (only shown when `metadata.data_source_type === "1000g_real"`): a clickable expander showing all selected IDs with population badges.

### `Audit.jsx` — extend with `data_source.release` field

When `data_source.release === "20130502"`, surface it as a new InfoRow alongside the existing data-source-version row.

---

## Demo script changes (`DemoKit.jsx`)

Add ACT 1.5 between the synthetic cohort intro and the results page walkthrough:

```text
[0:25] Switch source to "1000 Genomes samples (real)" → SAS → 50 random.
       Show the preview list. "These are real 1000 Genomes phase-3
       samples from the South Asian sub-cohort. HG00125 is GIH,
       HG00513 is BEB. Pre-resolved against the AWS Open Data release."

[0:35] Run. Show the same poor-metabolizer rate (~14% on real SAS
       samples). "Identical conclusion, no synthetic frequencies
       in the loop. Sample IDs are auditable; anyone can re-run this."
```

3-minute demo and judge-FAQ entries get matching updates.

---

## Backend implementation (`anukriti-api`)

### File map

```
anukriti-api/
  app/
    routers/
      samples.py            ← new — GET /samples/1000g
      runs.py               ← extend — POST /runs/from-samples
    persistence.py          ← extend — get_samples_store()
    scripts/
      load_samples.py       ← new — JSONL → MongoDB seeder
    main.py                 ← extend — register samples router; wire startup loader
  tests/
    test_samples_endpoint.py    ← new
    test_runs_from_samples.py   ← new
data/
  1000g_phase3_resolved.jsonl   ← committed artifact from pgx-core indexing
```

### Startup loader

```python
# app/main.py — inside lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    samples = get_samples_store()
    if samples.count() == 0:
        loaded = load_samples_from_jsonl(
            Path(os.environ.get("SAMPLES_JSONL_PATH", "/opt/api/data/1000g_phase3_resolved.jsonl"))
        )
        logger.info(f"Loaded {loaded} 1000G samples into Mongo")
    yield
```

Idempotent: if `samples.count() > 0`, the loader is skipped. Re-seeding requires `--force` on a separate management command (out of scope this PR).

### Performance

- `GET /samples/1000g?random=50&superpop=SAS&workflow=clopidogrel`: a single `aggregate([{$match: {...}}, {$sample: {size: 50}}])` query — ~5 ms.
- `POST /runs/from-samples` with 50 sample IDs: 1 batch find (~2 ms) + the existing `runtime.run(ctx)` per-patient loop. Same time as today's synthetic /runs.

No new caching needed.

---

## Testing

| Test | Asserts |
|---|---|
| `test_index_1000g_samples` (pgx-core) | Job is idempotent: SHA256 of output matches across runs. Spot-check 3 known samples (HG00096 EUR, HG00513 SAS, NA19625 AFR) for known rs4244285 alleles per dbSNP. |
| `test_load_samples` (api) | Empty Mongo → seed → 7,512 docs present, all indexed. Re-run → no duplicates. |
| `test_samples_endpoint::list_basic` | `GET /samples/1000g?workflow=clopidogrel` returns 200, paginated. |
| `test_samples_endpoint::filter_superpop` | `superpop=SAS` returns ~489 docs (1000G phase-3 SAS count). |
| `test_samples_endpoint::random` | `random=50` returns 50 distinct samples. |
| `test_samples_endpoint::missing_workflow` | `workflow=foo` → 400 invalid_workflow. |
| `test_runs_from_samples::happy_path` | Real samples → 200, report shape matches `/runs`, `data_source.type=="1000g_real"`. |
| `test_runs_from_samples::partial_missing` | 2 valid + 1 fake ID → 200 with `missing_sample_ids: ["FAKE"]` and `sample_count: 2`. |
| `test_runs_from_samples::all_missing` | Only fake IDs → 400 `no_samples_found`. |
| `test_runs_from_samples::too_many` | 600 IDs → 400 `too_many_samples`. |

Frontend has no unit tests today (eslint-only); manual smoke-test on the picker. Add a Cypress run in a follow-up.

---

## Deferred risks (call out, don't fix today)

| Risk | Severity | Plan |
|---|---|---|
| **CYP2D6 not modeled** — the four real-sample workflows don't include CYP2D6 because pgx-core's CYP2D6 caller doesn't handle CNVs (Cyrius wrapper is open work). | Medium credibility — investors may ask about CYP2D6. | Document in DemoKit.jsx FAQ; same answer as today. Real-samples mode will support CYP2D6 when CP-1 lands. |
| **AFR sub-population coverage gap.** AFR superpop is well-represented (n=661) but specific founder communities (e.g. Yoruba in Vysya context) need separate cohorts. | Low for this feature — orthogonal to BCHE Vysya which is a separate dataset. | The honest framing is: "1000G phase-3 covers the five superpopulations. Founder-community variants like BCHE L307P need targeted resampling — that's a Phase B task tracked separately." |
| **Sample-ID PII concerns** — 1000 Genomes IDs are *de-identified by the consortium*. They are public, published in Nature 2015, Table S1. Showing them in the UI is fine. | Zero. | Cite the public release and Nature 2015 paper in the source-card description. |
| **Mongo Atlas tightening** — currently `0.0.0.0/0`. Adding the samples collection doesn't change the picture; same risk as the `runs` collection today. | Already tracked in DEPLOYMENT.md "What the Azure deploy does NOT include". | Defer to existing tracking. |
| **Stale data risk** — 1000G phase-3 hasn't been updated since 2013. Newer phase-4-equivalent releases (e.g. NYGC high-coverage 2020) have better Indian-subcontinent coverage. | Low — phase-3 is the canonical reference for PGx benchmarking; CPIC tables are pinned to it. | Note in DemoKit FAQ. Newer releases are a Phase B addition, not a blocker. |

---

## Order of operations

| Step | Repo | Effort | Blocks |
|---|---|---|---|
| 1. Indexing job written | `anukriti-pgx-core` | 3 hr | Step 2 |
| 2. Run job locally → `data/1000g_phase3_resolved.jsonl` produced + committed | `anukriti-pgx-core` | 1 hr (extraction time) + 30 min spot-check | Step 3 |
| 3. Backend loader + `/samples/1000g` + `/runs/from-samples` + tests | `anukriti-api` | 4 hr | Step 4 |
| 4. Backend redeploy | `anukriti-stack` | 5 min | Step 5 |
| 5. Frontend `RealSamplesPanel` + wire-up + demo script | `anukriti-main` | 4 hr | done |

**~13 hours of focused work.** Realistic to land in 2 working days with verification time.

The riskiest step is **Step 2** — needs `bcftools` or `cyvcf2`+`pysam` on the founder's local machine. If neither is available, fall back to `pip install cyvcf2` (works on macOS / Linux without system deps thanks to bundled htslib).

---

## Acceptance criteria

When this lands:

1. `GET /samples/1000g?workflow=clopidogrel&superpop=SAS&random=50` returns 50 real samples in <50ms.
2. `POST /runs/from-samples {workflow:"clopidogrel", sample_ids:["HG00125","HG00513"]}` returns a `UnifiedExecutionReport` with `data_source.type == "1000g_real"`.
3. Frontend `/simulate` has three source options. Picking "1000 Genomes samples (real)" → SAS → 50 → Run produces a results page with the green "Real 1000 Genomes phase-3" badge and a "Selected samples (50)" expander listing HG00125, HG00513, etc.
4. The Audit page surfaces `data_source.release == "20130502"`.
5. `npm run build` clean. `pytest -q` clean in both pgx-core and api repos.
6. Investor demo script loads in <30s end-to-end.

---

## What this DOESN'T do (next-feature parking lot)

- **User VCF upload** — different problem, separate plan when we're ready.
- **Custom VCF-engine URL** (the founder's separate problem) — when that engine exists, it slots into the same `RealSamplesPanel`/`/runs/from-samples` shape with `data_source.type == "custom_vcf_engine"`. Architecture is deliberately extensible.
- **Cohort sharing / permalinks for real-sample runs** — the existing `/runs/{id}` permalink path works once a run exists; nothing to add.
- **CYP2D6** — doesn't get added here; it gets added when pgx-core's CNV caller does (CP-1).

---

*Update this document in the same commit that lands each step. When all
steps are done, mark Status as 'Complete' and link to the four landed
commits across the three repos.*
