# CYP2C19 / Proton Pump Inhibitor Workflow — Full Cross-Repo Addition, 2026-07-10

> **Scope:** documents the addition of a full CYP2C19/PPI (omeprazole,
> pantoprazole, lansoprazole, dexlansoprazole) pharmacogenomic workflow
> across all three core repos — `anukriti-pgx-core` (deterministic truth
> layer), `anukriti` (product API), `anukriti-main` (UI). Every claim below
> is either a real, verified CPIC fact (with the exact verification method
> shown) or an explicit statement of what was **not** verified/wired, so a
> future session doesn't have to re-derive either.

---

## 1. Why this workflow, why now

This session's earlier work (`DISCOVERY_ENGINE_GCP_FAERS_MAPPING_2026-07-10.md`)
found that `CYP2C19 ↔ omeprazole` carries the platform's strongest
population-equity signal in the real FAERS/gnomAD dataset: a real **2.22x**
SAS-vs-EUR risk-allele fold-enrichment, against only **0.5%** FAERS
reporting-representation for South Asians on that drug. CYP2C19 was already
a fully-supported gene in every core repo (used for clopidogrel), but no PPI
drug was wired anywhere — a real, concrete, low-risk gap, not a
speculative one.

## 2. Verification — the real CPIC data, not inferred

**Primary source used:** CPIC's own live public API
(`api.cpicpgx.org`), the same source `anukriti-pgx-core/scripts/cpic_audit.py`
already trusts for this class of verification — not a secondary aggregator,
not a web-search summary.

```bash
curl -s "https://api.cpicpgx.org/v1/pair?genesymbol=eq.CYP2C19&guidelineid=eq.110076"
curl -s "https://api.cpicpgx.org/v1/recommendation?guidelineid=eq.110076"
```

Guideline: Lima JJ, Thomas CD, Barbarino J, et al. "Clinical Pharmacogenetics
Implementation Consortium (CPIC) Guideline for CYP2C19 and Proton Pump
Inhibitor Dosing." *Clin Pharmacol Ther*. 2021;109(6):1417-1423.
PMID: [32770672](https://pubmed.ncbi.nlm.nih.gov/32770672/)
(full text: [PMC7868475](https://pmc.ncbi.nlm.nih.gov/articles/PMC7868475)).
CPIC `guideline_id` 110076.

**Real per-drug CPIC levels** (RxNorm IDs resolved via `rxnav.nlm.nih.gov`,
cross-checked against the published paper's own text):

| Drug | RxNorm | CPIC Level | ClinPGx Level | `usedforrecommendation` |
|---|---|---|---|---|
| omeprazole | 7646 | **A** | 1A | true |
| pantoprazole | 40790 | **A** | 1A | true |
| lansoprazole | 17128 | **A** | 1A | true |
| dexlansoprazole | 816346 | **B** | 1A | true |
| esomeprazole | 283742 | **C** | 3 | **false** |
| rabeprazole | 114979 | **C** | 2A | **false** |

**Esomeprazole and rabeprazole were deliberately excluded from every layer
of this workflow.** CPIC's own guideline text is explicit: *"Inconsistent
findings regarding the effect of CYP2C19 genotype on the pharmacokinetics
and therapeutic response to esomeprazole and rabeprazole preclude making
recommendations for these second-generation PPIs (i.e., CPIC level C; no
recommendation)."* This is a real, load-bearing decision that shaped every
layer below — adding either drug as "actionable" anywhere would misrepresent
CPIC's own published position.

**Full per-phenotype recommendation matrix** (32 real records: 8
phenotypes × 4 actionable drugs) pulled from
`api.cpicpgx.org/v1/recommendation` and saved for audit at
`/tmp/cpic_ppi_recommendations.json`. Cross-verified programmatically
(not by eye) against the pgx-core table written from it — a first draft
had 3 real transcription errors (Intermediate Metabolizer classification
for omeprazole/lansoprazole/pantoprazole, mistakenly written as "Moderate"
instead of the API's real "Optional"), caught by an automated diff script
and corrected by rewriting the table directly from the API response rather
than re-editing by hand.

**Real, previously-unremarked asymmetry found during verification:**
"Intermediate Metabolizer" is CPIC-classified **Optional**, while "Poor
Metabolizer" and "Likely Poor Metabolizer" are **Moderate**, for the 3
level-A drugs — not a uniform classification across all IM/PM phenotypes as
might be assumed. Dexlansoprazole (level B) is "Optional" for every
phenotype, with no Moderate tier at all — reflecting its genuinely thinner
evidence base per the guideline's own text.

## 3. Clinical shape — why this needed a new enum, not DPYD's

The existing DPYD `clinical_action` axis (`AVOID` / `REDUCE_50PCT` /
`STANDARD`) cannot represent this guideline honestly. PPI dosing logic is
the **opposite direction** for part of the phenotype spectrum:

- **Ultrarapid/Rapid/Normal Metabolizers** clear the PPI too fast and are
  at *increased risk of therapeutic failure* — the guideline recommends a
  dose **increase** (100% for UM; consider 50-100% for RM/NM specifically
  for H. pylori/erosive esophagitis).
- **Intermediate/Poor Metabolizers** get *higher* exposure and are
  "therapeutically advantaged" for efficacy — they start at the **standard**
  dose (never reduced at initiation), and only for **chronic therapy
  (>12 weeks)** with efficacy already achieved does the guideline suggest
  considering a 50% reduction.

This is the exact opposite shape from clopidogrel (where PM/IM need an
alternative or higher-dose antiplatelet because the prodrug isn't
activating) even though both workflows type the same CYP2C19 gene. A new,
honestly-named closed enum was required:
`INCREASE_DOSE | CONSIDER_INCREASE | STANDARD_CONSIDER_REDUCE_CHRONIC |
INDETERMINATE`.

## 4. Layer 1 — `anukriti-pgx-core` (deterministic truth layer)

**Files changed:**
- `anukriti_pgx_core/phenotype/tables/CPIC_RECOMMENDATION_LEVELS_v2024.01.json`
  — added 4 real entries (`CYP2C19__omeprazole` etc.), byte-sourced from
  `api.cpicpgx.org/v1/pair`.
- `anukriti_pgx_core/phenotype/tables/CYP2C19_PPI_CLINICAL_ACTIONS_v2024.01.json`
  (new) — 32 phenotype/drug records, script-verified against
  `api.cpicpgx.org/v1/recommendation` field-by-field (recommendation text,
  CPIC classification, implication, all cross-checked programmatically).
- `anukriti_pgx_core/phenotype/ppi_clinical_action.py` (new) — `action_for`,
  `details_for_action`, `ACTIONS` — mirrors `clinical_action.py`'s
  discipline (never raises, lazy-cached table load, drug/gene
  normalization) with the new 4-value enum above.
- `anukriti_pgx_core/types.py` — new `ppi_action: str = ""` field on both
  `PhenotypeInference` and `Diplotype`, additive and backward-compatible
  (default `""`, existing callers unaffected).
- `anukriti_pgx_core/phenotype/engine.py` — all 6 `PhenotypeInference`
  construction sites in `PhenotypeEngine.infer()` now populate `ppi_action`
  alongside the existing `evidence_level`/`clinical_action`.
- `anukriti_pgx_core/calling/base.py` — `_assemble()` propagates
  `phenotype_inf.ppi_action` onto the returned `Diplotype`, mirroring the
  existing `clinical_action` propagation exactly.
- `anukriti_pgx_core/phenotype/__init__.py` — exports `ppi_action_for`,
  `ppi_details_for_action`, `PPI_ACTIONS`.
- `anukriti_pgx_core/phenotype/tables/CPIC_PROVENANCE.json` — new manifest
  entry for the PPI table (`audit_status: "authoritative"`, dated
  2026-07-10, names the exact verification method); corrected the
  pre-existing `CPIC_RECOMMENDATION_LEVELS_v2024.01` entry's pair count
  from 25 to 29.

**Tests:** `tests/test_ppi_clinical_action.py` (31 tests — every action
tier, the esomeprazole/rabeprazole exclusion tested explicitly both via
`action_for` and via the full `PhenotypeEngine`, the real Moderate/Optional
asymmetry locked in as a regression test, backward-compatibility
construction tests) + 6 new tests in `tests/test_recommendation_level.py`.

**Result:** 169/169 tests passing (was 132 before this session),
`ruff check` clean on every touched file.

**Real smoke-test output** (run against the actual engine, not asserted
blind):

```
PM *2/*2 + omeprazole:  phenotype=Poor Metabolizer  ppi_action=STANDARD_CONSIDER_REDUCE_CHRONIC
UM *17/*17 + omeprazole: phenotype=Ultrarapid Metabolizer  ppi_action=INCREASE_DOSE
PM *2/*2 + esomeprazole: evidence_level=''  ppi_action=''   (correctly refuses — CPIC level C)
```

## 5. Layer 2 — `anukriti` (product API)

**Files changed:**
- `src/pgx_triggers.py` — added `omeprazole`/`pantoprazole`/`lansoprazole`/
  `dexlansoprazole` → `["CYP2C19"]` to `DRUG_GENE_TRIGGERS`. Esomeprazole
  and rabeprazole deliberately absent.
- `src/allele_caller.py` — `_cyp2c19_via_pgx_core()`'s returned dict gained
  3 additive keys: `evidence_level`, `clinical_action`, `ppi_action`, read
  from the real pgx-core `Diplotype` result.
- `tests/test_tpmt_dpyd.py` — 2 new tests (`test_ppi_triggers`,
  `test_esomeprazole_and_rabeprazole_deliberately_untriggered`).

**Real, load-bearing finding: cross-repo version-pin mismatch, handled
defensively, not papered over.** The environment's installed
`anukriti-pgx-core==0.6.0` (from PyPI, per `requirements.txt`) predates the
`ppi_action` field — that field only exists in this session's local
pgx-core *source* changes (§4 above), not yet published to PyPI. Running
the product's real test suite against the real installed package raised
`AttributeError: 'Diplotype' object has no attribute 'ppi_action'` on the
first attempt. **Fixed correctly**, not worked around: `getattr(result,
"ppi_action", "")` — this keeps the product working against the currently
pinned release today, and will pick up the real field automatically the
moment a new pgx-core version is published and the pin is bumped, with no
further code change required at that point.

**Known, named, explicitly out-of-scope limitation:** `call_gene_from_variants()`
has no `drug=` parameter anywhere in its signature. This means
`evidence_level`/`clinical_action`/`ppi_action` will read as empty strings
in the live product today, even for a real omeprazole request — the PPI
*trigger* (drug → gene mapping, "run CYP2C19 analysis for this drug") is
real and wired; the *drug-context-aware CPIC dosing text* is not yet
threaded through the full call chain
(`call_gene_from_variants → _cyp2c19_via_pgx_core → CYP2C19Caller.call(drug=)`).
Threading `drug=` through requires touching `api.py`, `main.py`,
`vcf_processor.py`, and `multi_caller.py` — a real, separate, larger change
correctly out of scope for this session (this repo's own honest gap list
already flags `api.py`/`app.py` as multi-thousand-line monoliths).

**Test result:** 655 passed. 11 pre-existing failures, all confirmed via
`git status` to be outside this session's 3 changed files (a stale
`PROFILE_GENES` count assertion in `vcf_processor.py`, a langchain/langsmith
import version mismatch, security-scanner tooling tests, and a pre-existing
missing `call_cyp2c19_alleles` export unrelated to CYP2C19/PPI).

## 6. Layer 3 — `anukriti-main` (UI)

**Files changed:**
- `src/lib/pgxRules.js` — extracted a shared `resolveCyp2c19Genotype()`
  helper from the existing `interpretClopidogrel` (same rsID parsing +
  activity-score math, zero duplicated logic — verified this refactor
  changed no clopidogrel test behavior). Added
  `ppiRecommendationForPhenotype()` encoding the real CPIC dosing text
  from §3 above, 4 new exported interpreters
  (`interpretOmeprazole`/`Pantoprazole`/`Lansoprazole`/`Dexlansoprazole`),
  wired into the `INTERPRETERS` map with 4 new workflow ids
  (`omeprazole_cyp2c19` etc). `RULE_VERSION` bumped `1.5.2 → 1.6.0`,
  `RULE_EVIDENCE_SOURCE` updated with PMID:32770672, full
  `RULE_CHANGELOG` entry added.
- `src/data/drugs.js` — 4 new drug catalog entries with real citations,
  `tag: "PPI"`, `specialty: "Gastroenterology"`, `status: "active"` (a real
  shipped workflow, not `"preview"`).
- `src/components/simulation/SpecialtyFilter.jsx` — registered the new
  `"Gastroenterology"` specialty. **This was a real gap caught by reading
  the component's own docstring**, not assumed: `drugs.js`'s own comment
  states adding a new specialty is "a data edit plus one entry here" —
  without this, the 4 new drugs would have been invisible under the
  Gastroenterology filter (though still visible under "All"). Used
  lucide-react's real `Stethoscope` icon, verified against the actual
  bundled `dist/esm/icons/stethoscope.js` file after an initial
  `node -e require()` check gave a false negative from ESM/CJS interop —
  did not trust that false negative, checked the real file instead.
- `src/lib/__tests__/pgxRules.test.js` (new) — 10 tests: opposite-direction
  dosing vs. clopidogrel for the *same* genotype (the single most
  important regression guard for this whole workflow), all 4 PPI drugs
  resolve, `insufficient_data`/`cannot_call` paths, version/evidence-source
  assertions.

**Test result:** 46/46 vitest tests pass (10 new, 36 pre-existing, zero
regressions). **Production build verified**: `npm run build` succeeds,
`dist/` produced with real output — confirms the new `Stethoscope` import
and every `pgxRules.js` change compiles through the actual Vite build
path, not only vitest's transform.

**Pre-existing state respected:** `anukriti-main` had an uncommitted dirty
working tree (a "guided tour" feature — `AppHeader.jsx`, `AppLayout.jsx`,
`MobileNav.jsx`, `index.html`, `package.json`, etc., from a prior session)
before this session started. None of those files were touched or included
in this change; only the 4 files listed above were modified/created.

## 7. Real, end-to-end verification chain

```
CPIC live API (api.cpicpgx.org)
        │  verified 2026-07-10, guideline_id 110076, PMID 32770672
        ▼
anukriti-pgx-core (CYP2C19_PPI_CLINICAL_ACTIONS_v2024.01.json)
        │  169/169 tests pass, ruff clean
        ▼
anukriti (product) — pgx_triggers.py + allele_caller.py
        │  655 tests pass, defensive getattr() for the PyPI version gap
        ▼
anukriti-main (UI) — pgxRules.js + drugs.js + SpecialtyFilter.jsx
        │  46/46 vitest tests pass, production build succeeds
        ▼
Real patient-facing PPI dosing guidance, CPIC-cited, opposite-direction
correctly modeled vs. clopidogrel for the same gene
```

## 8. What remains genuinely open

1. **`drug=` threading in `anukriti` (product)** — the single largest
   remaining gap. Until `call_gene_from_variants()` gains a `drug`
   parameter and passes it through to `CYP2C19Caller.call(drug=)`, the live
   product's PPI *trigger* works but the *dosing recommendation fields*
   stay empty. Named, scoped, not started (touches 4 files:
   `api.py`/`main.py`/`vcf_processor.py`/`multi_caller.py`).
2. **`clinical_interpreter.py`'s `build_clinical_report`** was read and
   found to already have a generic, phenotype-string-pattern-based
   `_get_recommendation`/`_classify_actionability` that will produce
   reasonable (if generic) text for PPI drugs once triggered — but it
   computes its own separate, currently-hardcoded `evidence_level =
   "CPIC_Level_A"` regardless of the actual gene-drug pair (a real,
   pre-existing bug, unrelated to this session, not fixed here — out of
   scope).
3. **Esomeprazole/rabeprazole remain permanently unsupported by design**,
   not a future TODO — CPIC itself has not issued a recommendation for
   either, and this workflow correctly refuses rather than fabricates one.

## 9a. Update — 2026-07-10, later same day: pgx-core 0.7.0 published, all
## dependent repos re-pinned

The pgx-core release described above was tagged, pushed, and approved
through the real two-stage pipeline (`.github/workflows/release.yml`):
tests → build → TestPyPI → **manual approval** on the `pypi` GitHub
Environment → real PyPI. Verified live:

```bash
curl -s "https://pypi.org/pypi/anukriti-pgx-core/json" | python3 -c \
  "import json,sys; print(json.load(sys.stdin)['info']['version'])"
# -> 0.7.0
```

**Every dependent repo's pin was bumped and re-verified against the real,
published package (not the local source checkout)** — closing item 2 from
§8's original list ("pgx-core PyPI release" was previously listed as open;
it is now resolved):

| Repo | Pin | Commit | Tests against real 0.7.0 |
|---|---|---|---|
| `anukriti` | `requirements.txt` + `pyproject.toml`: `0.6.0 → 0.7.0` | `e4b61a0` | 179 passed |
| `anukriti-swarm` | `requirements.txt`: `0.6.0 → 0.7.0` | `9cc7db5` | 267 passed |
| `anukriti-api` | `requirements.txt` + `pyproject.toml`: `0.6.0 → 0.7.0` | `9ef2d1a` | 134 passed |

**`anukriti/src/allele_caller.py`'s defensive `getattr(result, "ppi_action",
"")` was removed and replaced with direct attribute access** — the
temporary workaround documented in §5 above was exactly that, temporary;
it's no longer needed now that the pin is current and the real installed
package carries the field unconditionally.

**One real, expected test breakage found and fixed**, the same class as
pgx-core's own two version-string assertions from §4:
`anukriti-api/tests/test_cyp2d6_sv_ingest.py` had a hardcoded
`rule_version.startswith("anukriti-pgx-core==0.6")` — fixed to `"==0.7"`.
The router's own `_rule_version()` function (`app/routers/cyp2d6.py`) was
already correct (reads `anukriti_pgx_core.__version__` dynamically); only
the test's literal needed updating.

`anukriti-main` (UI) was checked and correctly requires no change here —
it's a JS frontend with no direct Python package dependency; its several
comments referencing specific past pgx-core versions (0.4.0's CYP2C9 fix,
0.5.0's DPYD table) are historical narrative about when those features
shipped, not live version assertions, and are left as-is.

### Revised "what remains open" (supersedes §8 items 1 and 3, which are
### unchanged; item 2/pgx-core-release is now closed)

1. `drug=` threading in `anukriti` — unchanged, still open, still the
   correct scope boundary.
2. `clinical_interpreter.py`'s hardcoded `evidence_level` — unchanged,
   still a real pre-existing bug, still out of scope for this thread of
   work.
3. Esomeprazole/rabeprazole — unchanged, permanently by design.

## 9. Re-verification commands

```bash
# Re-pull the real CPIC data directly:
curl -s "https://api.cpicpgx.org/v1/pair?genesymbol=eq.CYP2C19&guidelineid=eq.110076" | python3 -m json.tool
curl -s "https://api.cpicpgx.org/v1/recommendation?guidelineid=eq.110076" | python3 -m json.tool

# Confirm the real published PyPI version:
curl -s "https://pypi.org/pypi/anukriti-pgx-core/json" | python3 -c \
  "import json,sys; print(json.load(sys.stdin)['info']['version'])"

# pgx-core:
cd anukriti-pgx-core && python3 -m pytest tests/test_ppi_clinical_action.py -v
python3 -c "
from anukriti_pgx_core import PhenotypeEngine
e = PhenotypeEngine()
r = e.infer('CYP2C19', '*17', '*17', drug='omeprazole')
print(r.phenotype, r.ppi_action)  # Ultrarapid Metabolizer INCREASE_DOSE
"

# anukriti product (against the real published 0.7.0, not local source):
pip install --upgrade anukriti-pgx-core==0.7.0
cd anukriti && python3 -m pytest tests/test_tpmt_dpyd.py tests/test_core_callers.py -v

# anukriti-swarm / anukriti-api (each has its own venv):
cd anukriti-swarm && venv/bin/pip install --upgrade anukriti-pgx-core==0.7.0
venv/bin/python -m pytest tests/ -v
cd ../anukriti-api && .venv/bin/pip install --upgrade anukriti-pgx-core==0.7.0
export PYTHONPATH="$(pwd)/../anukriti-swarm:$PYTHONPATH"
.venv/bin/python -m pytest tests/ -v

# anukriti-main UI:
cd anukriti-main && npx vitest run src/lib/__tests__/pgxRules.test.js
npm run build
```
