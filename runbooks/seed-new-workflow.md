# Runbook — Adding a new pharmacogenomic workflow end-to-end

> **Last revised:** 2026-05-27 (commits `3618a7e` / `3771c62` / `cfea7ed`)
>
> **Audience:** an engineer rolling a new CPIC-actionable workflow (e.g.
> the next "after fluorouracil") through the platform from scratch into
> Azure production.

This runbook captures the **physical pipeline** every workflow takes
through the three-repo platform plus the api repo plus the frontend.
It's keyed on the fluorouracil/DPYD rollout (2026-05-26 → 2026-05-27)
which was the first new workflow added after the original three
(clopidogrel / warfarin / simvastatin) and surfaced every gap in the
process.

If you only read one section, read [§ Operational pattern for
production seed merge](#operational-pattern-for-production-seed-merge)
— it's the merge primitive that lets you ship a new workflow's data
without disturbing existing rows.

---

## TL;DR — the 9-step pipeline

A new workflow takes nine concrete steps across five repos:

| # | Repo | What |
|---|---|---|
| 1 | `anukriti-pgx-core` | Add the gene caller (`GeneCaller` subclass) + PharmVar TSV |
| 2 | `anukriti-pgx-core` | Add CPIC recommendation table entries (the `evidence_level: A/B/C/D` source) |
| 3 | `anukriti-swarm` | Add CPIC guidelines (`guidelines/cpic.py`) + KG seed (`knowledge_graph/seed.py`) + evidence docs (`retrieval/evidence/documents.py`) + runtime narrative branch |
| 4 | `anukriti-api` | Wire the workflow → adapter (`app/adapters.py`): `WORKFLOW_TO_SCOPE`, `WORKFLOW_RSIDS`, `RSID_REF_ALT`, any strand flips, the `call_diplotype` branch |
| 5 | `anukriti-pgx-core` | Extend the indexer (`scripts/index_1000g_samples.py`): add the workflow to `WORKFLOWS`, add the rsIDs to `RSID_LOCUS` |
| 6 | `anukriti-pgx-core` | Run the indexer → refresh `data/1000g_phase3_resolved.jsonl` |
| 7 | `anukriti-main` | Frontend interpreter + sample generator + workflow registry |
| 8 | `anukriti-stack` | Rebuild + redeploy api image (the JSONL is image-baked at build time) |
| 9 | `anukriti-stack` | Trigger the per-workflow merge against production Mongo |

Each step has a verification gate. None of them are optional — skipping
the strand verification on step 4 caused a clinically-dangerous
miscall on the fluorouracil rollout that took an extra session to fix.

---

## Step-by-step with verification gates

### 1. Gene caller — `anukriti-pgx-core`

Each gene with star alleles needs a `GeneCaller` subclass under
`anukriti_pgx_core/calling/genes/`. For a single-rsID gene (e.g. SLCO1B1)
use `GenotypeCaller`; for multi-rsID star alleles use the PharmVar TSV
pattern (see `dpyd.py` for the simplest example or `cyp2c19.py` for
the canonical pattern).

The PharmVar TSV (`anukriti_pgx_core/calling/data/<gene>/<gene>_alleles_anukriti_v2024.01.tsv`)
is the source of truth for which letter at which rsID **defines** each
star allele.

**Gate:** the in-tree pinned-call test pack
(`tests/test_pinned_vcf_calls.py`) covers the canonical wildtype + every
defined star allele as a heterozygote. New genes must add a section
there with at least: `*1/*1` NM, every `*1/*X` heterozygote, every
`*X/*X` homozygote that has a clinically distinct phenotype.

### 2. CPIC recommendation level — `anukriti-pgx-core`

Append the new gene-drug pair(s) to
`anukriti_pgx_core/phenotype/tables/CPIC_RECOMMENDATION_LEVELS_v2024.01.json`.
Keys are `f"{gene}|{drug}"` (canonical, lowercased drug). Each entry's
`level` becomes the `evidence_level` field on every
`PhenotypeInference` / `Diplotype` / `GenotypeCall` returned for that
pair.

**Gate:** `pip install --editable .` then run
`anukriti_pgx_core.phenotype.recommendation_level.level_for(gene, drug)`
in a REPL — must return the new level. Run the full
`pytest anukriti-pgx-core/tests/` to confirm the existing 76 tests
still pass.

### 3. Swarm reasoning layer — `anukriti-swarm`

Three coordinated edits, each in a closed-table file:

- **`guidelines/cpic.py`** — append `CPICRecommendation` entries to
  `<GENE>_GUIDELINES` (one per phenotype × drug; see `DPYD_GUIDELINES`
  for a 6-row example), then extend `ALL_GUIDELINES` to include them.
- **`knowledge_graph/seed.py`** — gene node, allele nodes (with
  `payload['gene']` and `payload['rsid']`), phenotype nodes, drug
  nodes, ADR node, guideline node, evidence-paper nodes, and edges:
  `METABOLIZES`, `CONTRAINDICATED_FOR` (per phenotype-drug pair),
  `ASSOCIATED_WITH` (allele → phenotype, drug → ADR),
  `HIGHER_FREQUENCY_IN` (one per allele × superpop with gnomAD
  weight), `SUPPORTED_BY` (anchor to evidence papers). Then extend
  the `SEED_NODES` and `SEED_EDGES` lists at the bottom of the file.
- **`retrieval/evidence/documents.py`** — at least one `BiomedicalDocument`
  per gene-drug pair tagged `genes=[<gene>]` and `drugs=[<drugs>]`. The
  `_facet_population` matcher gates docs by gene since the post-#16+1
  hardening (commit `6fc0e97`) — population keywords on a doc only
  count for runs whose `gene` matches the doc's `genes` list.

The runtime narrative branch in `core/runtime/runtime.py
::_patient_narrative` needs a `if ctx.gene == "<GENE>"` block that
maps the diplotype back to a CPIC dose recommendation.

**Gate:** `.venv/bin/python -m pytest -q` against
`anukriti-swarm/tests/` — all 244 must pass. Then the seven byte-locked
flagship demos:

```bash
for d in showcase safety_demo interoperability_demo evaluation_demo \
         evidence_sufficiency_demo evidence_sufficiency_abstention_demo \
         unified_demo; do
  .venv/bin/python -m demos.$d
done
```

All seven must exit 0; the dedicated regression contract is
`tests/integration/test_flagship_signatures.py`.

### 4. API wiring — `anukriti-api/app/adapters.py`

Three closed tables and one branch in `call_diplotype()`:

- `WORKFLOW_TO_SCOPE`: `"<workflow>": ("<workflow>", "<gene>")`
- `WORKFLOW_RSIDS`: required + optional rsID lists (use lists-of-lists
  in `required` for OR-of-list semantics — see HapB3 for the pattern)
- `RSID_REF_ALT`: `(gene, ref, alt)` per rsID **in dbSNP forward-strand
  orientation** — this is non-negotiable, see [§ Strand orientation
  invariant](#strand-orientation-invariant) below
- `_PGX_CORE_TRANSCRIPT_FLIP`: per-rsID `(pgx_ref, pgx_alt)` for any
  rsID where pgx-core's PharmVar TSV's `defining_alt` column does not
  match the dbSNP-forward letter

Then a `if workflow == "<name>":` branch in `call_diplotype()` that
constructs variants via `_build_variants_for_gene` and calls the
appropriate `<Gene>Caller(...).call(variants, drug=workflow)`.

**Gate:** test every reasonable genotype combo against
`call_diplotype()`. From the fluorouracil rollout:

```python
# Wildtype on dbSNP forward across all of the workflow's rsIDs
res = call_diplotype("<workflow>", [...REF/REF letters...])
assert res["details"]["<GENE>"]["diplotype"] == "*1/*1"
assert res["details"]["<GENE>"]["phenotype"] == "Normal Metabolizer"
```

If wildtype calls anything other than `*1/*1` Normal Metabolizer, the
strand orientation is wrong. **Stop the rollout and fix this first.**
The 1000G fixture is the only safe ground-truth here because the lab
samples should mostly be wildtype.

### 5. Indexer — `anukriti-pgx-core/scripts/index_1000g_samples.py`

Add the workflow to `WORKFLOWS` (mirroring `WORKFLOW_RSIDS` from the
api but flatten any OR-of-list entries, since the indexer extracts
each rsID independently). Add every rsID's GRCh37 chr+position to
`RSID_LOCUS` — verify against dbSNP's `NC_000001.10:g.<position>`
placement, NOT GRCh38 (the 1000G phase-3 release is GRCh37).

```python
"<workflow>": {
    "required": ["rsXXX", "rsYYY", ...],
    "optional": ["rsZZZ", ...],
},

"rsXXX": ("<chr>", <grch37_pos>),
```

**Gate:** dry-run mode against ~50 samples:

```bash
.venv/bin/python scripts/index_1000g_samples.py \
    --workflows <workflow> --dry-run --log-level INFO
```

The log should print one `[cyvcf2] region <chr>:<pos>-<pos>` line per
rsID. If it 404s on the chromosome VCF URL, the bucket release version
in `_vcf_url` may have shifted (e.g. v5b → v5a as of 2026-05-27).

### 6. Fixture refresh

The in-tree fixture (`data/1000g_phase3_resolved.jsonl`) holds 30
unique 1000G samples × every supported workflow. Refreshing it for a
new workflow:

```bash
cd anukriti-pgx-core
python -m venv .venv && .venv/bin/pip install cyvcf2 requests

.venv/bin/python scripts/index_1000g_samples.py \
    --workflows <workflow> \
    --sample-ids "$(jq -r '.sample_id' data/1000g_phase3_resolved.jsonl | sort -u | tr '\n' ',')" \
    --output /tmp/<workflow>_only.jsonl \
    --force
```

The `--sample-ids` flag (added in commit `3618a7e`) lets you scope to
the 30 fixture sample IDs without re-extracting all 2,504 phase-3
samples. Some sample IDs may not be in the 1000G phase-3 VCF (e.g.
trio parents like NA12891/NA12892); the script logs them as warnings
and skips them — net new rows is ≤ 30.

Merge the new rows into the fixture:

```python
import json
from pathlib import Path

old = [json.loads(l) for l in open("data/1000g_phase3_resolved.jsonl")]
new = [json.loads(l) for l in open("/tmp/<workflow>_only.jsonl")]
overlap = {(r["sample_id"], r["workflow"]) for r in old} & \
          {(r["sample_id"], r["workflow"]) for r in new}
assert not overlap, f"unexpected overlap: {overlap}"
combined = sorted(old + new, key=lambda r: (r["sample_id"], r["workflow"]))
with open("data/1000g_phase3_resolved.jsonl", "w") as f:
    for r in combined:
        f.write(json.dumps(r, separators=(",", ":"), sort_keys=True) + "\n")
```

**Gate:** sample distribution matches expectations:

```python
import json, collections
rows = [json.loads(l) for l in open("data/1000g_phase3_resolved.jsonl")]
print(f"total={len(rows)}, samples={len(set(r['sample_id'] for r in rows))}")
print(collections.Counter(r["workflow"] for r in rows))
print(collections.Counter(r["superpopulation"] for r in rows
                          if r["workflow"] == "<workflow>"))
```

The new workflow row count should be ≤ 30 with at least one row per
superpopulation.

### 7. Frontend — `anukriti-main/src/lib/pgxRules.js`

Add an `interpret<Workflow>` function that reads `row.<rsid>` strings,
counts no-function and decreased-function alleles, computes the
phenotype, and returns `{ call_status, phenotype, star_allele,
recommendation, ... }`. Same dbSNP-forward letter conventions as the
api.

Add `generate<Workflow>Sample()` that emits 10 SIM-XXX rows covering
the major phenotypes (NM, IM, PM, edge cases). All letters in **dbSNP
forward strand**.

Wire the workflow into `INTERPRETERS`:

```js
const INTERPRETERS = {
  ...
  <workflow>_<gene>: interpret<Workflow>,
};
```

Bump `RULE_VERSION` and add a `RULE_CHANGELOG` entry.

**Gate:** `npm run build` cleanly; manually run `interpret<Workflow>`
against `generate<Workflow>Sample()` output in a Vitest snapshot or
the workflow page in dev.

### 8. Image rebuild + redeploy — `anukriti-stack`

The `Dockerfile.api` `COPY`s `anukriti-pgx-core/data/` into
`/opt/api/data/` so the JSONL ships with the image. After committing +
pushing the pgx-core JSONL change, run:

```bash
cd anukriti-stack
./scripts/redeploy.sh image
```

The script tags the image by combined `api+swarm+core` SHA-shorts, so
each component-side change forces a new revision. The rollout waits
≤ 3 min for the new revision to take traffic and runs a `/health`
smoke at the end.

**Gate:** `./scripts/redeploy.sh status` shows the new revision active
with the expected image tag. `/health` returns 200.

### 9. Production seed merge

Container Apps' `samples_1000g` collection is already populated with
the OLD workflows; `seed_if_empty` is a no-op. The new workflow's rows
get merged in via the **`merge_missing_workflows`** path landed in api
commit `3771c62` — see [§ Operational pattern for production seed
merge](#operational-pattern-for-production-seed-merge) below.

**Gate:** the public `/samples/1000g?workflow=<workflow>&limit=3`
endpoint returns rows with the expected superpop spread.

---

## Operational pattern for production seed merge

The api ships with `samples_1000g` startup logic that runs in this
order:

1. `seed_if_empty()` — populates the collection from the JSONL only
   when empty. **No-op when there are existing rows.**
2. If `MERGE_MISSING_WORKFLOWS` env var is set (comma-separated list),
   `merge_missing_workflows(workflows=...)` runs and inserts only the
   `(sample_id, workflow)` pairs that are NOT already in the
   collection.

This split means a workflow expansion deploy is a two-step Azure flip
that never touches existing rows:

```bash
# Step A — image deploy (carries the new code + new JSONL).
# After this, seed_if_empty is no-op (collection already has rows
# from the old workflows), so the new workflow rows are NOT yet in
# Mongo even though they're in the image.
cd anukriti-stack
./scripts/redeploy.sh image

# Step B — flip the merge env var. Container Apps rolls a new
# revision whose startup runs merge_missing_workflows() for the
# named workflow(s). Existing rows are untouched; the new
# (sample_id, workflow) pairs are inserted.
./scripts/redeploy.sh env "MERGE_MISSING_WORKFLOWS=<workflow>"

# Verify
curl -sS "https://<API>/samples/1000g?workflow=<workflow>&limit=3" | jq .total
# expected: ≥ 1 (typically 27-30 with the in-tree fixture)
```

The env var is **safe to leave on indefinitely** — the merge function
is idempotent and re-running on an already-merged collection inserts
nothing. The only reason to remove it is housekeeping after every
listed workflow has been rolled.

### CLI alternative

If you'd rather not flip an env var, the same merge function is
exposed as a CLI:

```bash
docker exec -it <container> \
    python -m app.scripts.load_samples \
        --merge-missing <workflow>
```

Output: `merged N new documents`. Same idempotency guarantee.

### When to use which approach

- **Env var** when the rollout is part of a normal image deploy and
  you want the merge to happen automatically on every container start
  during the rollout window (rev 18+ in the fluorouracil rollout).
- **CLI** when you've already deployed the image and just need to
  back-fill the merge once without rolling a new revision.

The env var approach is the recommended default — it keeps the merge
in the image-deploy critical path and makes the operational state
visible in the Container App's environment configuration.

---

## Strand orientation invariant

**The single most important invariant in the entire pipeline:**

> Every layer that talks about DNA letters must do so in **dbSNP
> forward-strand orientation** (i.e. the genome plus strand, the same
> letters every PCR/TaqMan/KASP/Sanger assay and every 1000G phase-3
> VCF emits) — except for pgx-core's PharmVar TSV, which uses
> **transcript orientation**, and is bridged via the per-rsID flip
> table in `anukriti-api/app/adapters.py::_PGX_CORE_TRANSCRIPT_FLIP`.

For a gene on the genomic minus strand (DPYD is the canonical example —
chr1, minus strand), transcript-orientation letters are the
reverse-complement of dbSNP-forward letters. **This bit you on the
fluorouracil rollout** — the api adapter's `RSID_REF_ALT` for
rs55886062, rs67376798 and rs75017182 was committed in
transcript-orientation letters but documented as "dbSNP forward",
which silently inverted the polarity for any input from a 1000G VCF
or external PCR assay. HG00096 (a wildtype EUR sample) was being
called as homozygous DPYD*13 + homozygous D949V Poor Metabolizer —
a clinically dangerous miscall.

The fix lives in commit `3771c62`. The single-line check that surfaced
the bug is:

```python
# HG00096 is REF/REF on dbSNP forward across every DPYD rsID.
res = call_diplotype("<workflow>", [
    {"id": "rsXXX", "genotype": "<dbsnp_ref><dbsnp_ref>"},
    ...
])
assert res["details"]["<GENE>"]["diplotype"] == "*1/*1", \
    "wildtype miscall — strand orientation is inverted somewhere"
```

**Run this check on every new workflow.** If it fails, audit the
RSID_REF_ALT and _PGX_CORE_TRANSCRIPT_FLIP tables in
`anukriti-api/app/adapters.py` against verified dbSNP build 157
GRCh37 placements and pgx-core's PharmVar TSV `defining_alt` column.

### How to verify a per-rsID strand mapping is correct

For each rsID:

1. Get the dbSNP forward-strand REF/ALT from
   `https://www.ncbi.nlm.nih.gov/snp/<rsid>` → "Genomic Placements" →
   `NC_000001.10:g.<pos><REF>><ALT>` (the GRCh37.p13 line).
2. Look up pgx-core's `defining_alt` letter in the gene's PharmVar
   TSV (`anukriti_pgx_core/calling/data/<gene>/<gene>_alleles_anukriti_v2024.01.tsv`).
3. If `defining_alt` matches the dbSNP-forward ALT, no flip is needed —
   `RSID_REF_ALT[rsid]` should be `(gene, dbsnp_ref, dbsnp_alt)`.
4. If `defining_alt` matches the dbSNP-forward REF (i.e. the gene is
   on the minus strand and pgx-core encoded the variant on the
   transcript strand), add a `_PGX_CORE_TRANSCRIPT_FLIP[rsid]` entry
   that maps `(dbsnp_ref, dbsnp_alt) -> (defining_alt_letter,
   the_other_letter)`.

### Per-rsID summary for DPYD (recorded for posterity)

| rsID | dbSNP REF/ALT (GRCh37) | Gene strand | pgx-core defining_alt | Flip table entry |
|---|---|---|---|---|
| rs3918290   | C/T | minus | T | none (already matches) |
| rs55886062  | A/T | minus | A | `("T", "A")` |
| rs67376798  | T/A | minus | T | `("A", "T")` |
| rs56038477  | C/T | minus | C | `("T", "C")` |

The pattern: every minus-strand rsID where the dbSNP-forward ALT and
pgx-core `defining_alt` differ needs a flip table entry.

---

## Verification checklist

Run all of these before declaring a workflow ready:

- [ ] `pgx-core/tests` — full pytest pass
- [ ] `anukriti-swarm/tests` — full pytest pass (244 tests)
- [ ] All seven byte-locked flagship demos exit 0
- [ ] `anukriti-api/tests` — full pytest pass
- [ ] Wildtype call assertion against the new workflow returns
      `*1/*1` Normal Metabolizer
- [ ] Indexer dry-run produces one `[cyvcf2] region` log line per rsID
      at the expected GRCh37 chr:pos
- [ ] `data/1000g_phase3_resolved.jsonl` has the expected workflow
      sample count (≤ 30) with at least one row per superpop
- [ ] Frontend `npm run build` succeeds; `interpret<Workflow>` against
      `generate<Workflow>Sample()` produces the expected phenotype
      distribution
- [ ] Image deploy completes; `/health` returns 200
- [ ] After env-var flip, `/samples/1000g?workflow=<workflow>&limit=3`
      returns ≥ 1 row
- [ ] After env-var flip, `/genomes/index?drug=<drug>&limit=3` returns
      samples with the new workflow in `available_workflows`

---

## Reference — the fluorouracil/DPYD rollout commits

| Repo | Commit | What |
|---|---|---|
| `anukriti-swarm` | `6fc0e97` | gene-scope evidence facet + bias detector lookups |
| `anukriti-swarm` | `95647db` | DPYD/fluoropyrimidine workflow added |
| `anukriti-api` | `5c16454` | DPYD adapter wiring + PCR ingestion + /genomes/index |
| `anukriti-api` | `427198b` | harden DPYD PCR ingestion for lab cohorts |
| `anukriti-api` | `3771c62` | DPYD strand orientation correction + merge_missing_workflows |
| `anukriti-pgx-core` | `3618a7e` | indexer supports DPYD/fluorouracil + 30-sample fixture refreshed |
| `anukriti-main` | `5a7c26d` | route DPYD CSV uploads through PCR ingestion |
| `anukriti-main` | `cfea7ed` | pgxRules v1.5.2 — DPYD strand orientation correction |

Production state after rollout:

- Container App revision 18, image `anukriti-api:git-3771c62-95647d-3618a7`
- `samples_1000g`: 117 docs (90 old workflows + 27 fluorouracil)
- `MERGE_MISSING_WORKFLOWS=fluorouracil` env var still set (idempotent;
  remove on next deploy if no further fluorouracil work is queued)
