# Discovery Engine ↔ GCP FAERS Pipeline: Mapping and Enhancement — 2026-07-10

> **Scope:** this document maps every real finding produced by the
> `project_astra/faers_discovery/` GCP pipeline (the "GCP work" — FAERS
> adverse-event data fetched via a now-terminated Compute Engine VM,
> `anukriti-genomics-vm-mumbai`, loaded into BigQuery dataset
> `anukriti_faers`) onto `project_astra`'s Discovery Engine
> (`astra/discovery_engine/`), verifies what was already wired vs. what was
> genuinely still open, and documents one real, tested, additive engine
> enhancement made today. Everything below was checked against real code,
> real committed data, and real (recomputed, not assumed) numbers — no
> speculative claims.
>
> **Repo:** `project_astra` (this document lives in `anukriti_docs`, the
> platform-wide docs repo, per that repo's own cross-repo documentation
> convention — see `ANUKRITI_FULL_CONTEXT.md`'s "canonical docs to read"
> list).

---

## 1. What the GCP pipeline actually is, verified state as of today

**Infrastructure (checked via `gcloud compute instances list`, read-only,
no VM state changed by this session):**

| VM | Zone | Status |
|---|---|---|
| `anukriti-genomics-vm` | us-central1-a | TERMINATED |
| `anukriti-faers-fetch` | asia-south1-a | TERMINATED |
| `anukriti-genomics-vm-mumbai` | asia-south1-a | TERMINATED |

All three GCP compute instances are terminated — no ongoing compute spend,
confirming the 2026-07-08 ASTRA session's own account (`SESSION_SUMMARY.md`)
that the FAERS fetch job completed and the VM was deliberately stopped once
BigQuery's `_raw` column was confirmed to losslessly preserve the same data.
**The VM's 230GB disk was not deleted** (an explicit, still-open,
human-only decision — see `project_astra/session_notes/2026-07-08/
HUMAN_REVIEW_NEEDED.md` item 6 — this document does not change that).

**Data pulled from the pipeline (real, already local, verified present):**

- `project_astra/faers_discovery/data/raw/*.jsonl` — 5 of 6 target drugs
  (omeprazole, atorvastatin, aspirin, ibuprofen, metformin), ~5MB each.
- `project_astra/faers_discovery/data/raw_partial/metformin.jsonl` — a
  stray **7.1GB** partial file, almost certainly pre-dating the dedup/
  checkpoint fix documented in `FAERS_SESSION_RESUME_2026-07-01.md` §2.
  **Not deleted by this session** (a cleanup decision, not an engine
  question — flagged, not actioned, consistent with this session's own
  read-only-on-infrastructure discipline).
- `project_astra/faers_discovery/data/signals/*.json` — four already-computed,
  real outputs (detailed in §2 below), all committed to the repo (not
  gitignored, unlike the raw JSONL).
- BigQuery `anukriti_faers` dataset, 6 tables, **2,276,461 total real
  reports** (paracetamol 606,028; metformin 311,397; ibuprofen 207,234;
  aspirin 433,608; atorvastatin 356,097; omeprazole 362,097) — verified
  count, matches the 2026-07-08 ASTRA session's own independently-checked
  total exactly.

## 2. The four real signal artifacts already produced, and their exact
## engine mapping

Every one of these already exists as a **reusable, tested `astra/
discovery_engine/` module** — not a one-off script computation. Mapping,
verified by reading the actual module source (not assumed from filenames):

| Data file | Producing module | Producing script | Tests |
|---|---|---|---|
| `reporting_bias_report.json` | `discovery_engine/reporting_bias.py` | `scripts/report_reporting_bias.py` | `tests/test_discovery_reporting_bias.py` |
| `joined_population_signal.json` | `discovery_engine/population_signal.py` + `discovery_engine/mechanistic_prior.py` | `scripts/join_faers_population_signal.py` | `tests/test_discovery_population_signal.py`, `tests/test_discovery_mechanistic_prior.py` |
| `composed_equity_signal.json` | *(pure composition in the script itself — deliberately no new `astra/` module; composes the two artifacts above)* | `scripts/compose_equity_signal.py` | `tests/test_compose_equity_signal.py` |
| `discovery_candidates_2026_07_08.json` | `discovery_engine/scoring.py` (`score_candidate`) + `discovery_engine/validation_gate.py` (`build_checklist`) | `scripts/build_discovery_candidates.py` | `tests/test_build_discovery_candidates.py`, `tests/test_discovery_scoring.py`, `tests/test_discovery_validation_gate.py` |

**Conclusion of the mapping audit: the GCP findings were already fully
wired into the Discovery Engine before this session started.** There was no
dangling data sitting outside the engine's reach. This matters because it
means the correct next step was **auditing for real gaps in an already-
integrated system**, not building a new integration — see §3.

### 2.1 Real findings, restated precisely (all numbers re-verified against
### the actual committed JSON, not recalled)

**Reporting-representation bias** (`reporting_bias.py`, pooled across all 6
drugs, 2,276,461 real reports):

| Region | FAERS share | UN population share | Representation ratio |
|---|---|---|---|
| South Asia (SAS) | 0.252% | 25.3% | **0.010** |
| East Asia (EAS) | 2.509% | 20.1% | 0.125 |
| Sub-Saharan Africa (AFR) | 0.344% | 14.6% | 0.024 |
| Europe (EUR) | 22.158% | 8.8% | 2.518 |
| North America (NAM) | 69.504% | 4.7% | 14.788 |

South Asia's real-world adverse-event signal is captured at roughly **1% of
what its world-population share would proportionally produce.**

**Risk-allele × reporting-gap composed equity signal** (`compose_equity_
signal.py`, 4 gene-drug pairs resolved):

| Gene | Drug | SAS/EUR fold-enrichment (gnomAD) | SAS reporting ratio (FAERS) |
|---|---|---|---|
| CYP2C9 | ibuprofen | 0.80x (depleted) | 0.5% |
| CYP2C9 | aspirin | 0.80x (depleted) | 1.2% |
| SLCO1B1 | atorvastatin | 0.32x (depleted) | 0.8% |
| **CYP2C19** | **omeprazole** | **2.22x (enriched)** | **0.5%** |

CYP2C19/omeprazole is the one pair where a real elevated genetic-risk signal
and a real severe reporting gap point the same direction.

**Discovery Engine candidates** (`scoring.py` + `validation_gate.py`, real
computed PRR via BigQuery, not synthetic):

| Gene ↔ Drug | Real PRR | Reaction cluster | Tier |
|---|---|---|---|
| CYP2C9 ↔ aspirin | 3.67 | GI haemorrhage / peptic ulcer / gastric ulcer | **MEDIUM** |
| SLCO1B1 ↔ atorvastatin | 2.57 | Myalgia / rhabdomyolysis / myopathy | **MEDIUM** |
| CYP2C9 ↔ ibuprofen | 0.86 | GI haemorrhage / AKI | refused (below Tier-0 bar) |
| CYP2C19 ↔ omeprazole | 1.23 | C. diff / pneumonia / fracture | refused (below Tier-0 bar) |

Ceiling enforced in code (`scoring.ConfidenceTier`): neither candidate can
ever reach `HIGH` — that tier is structurally unreachable from this module,
reserved for CPIC-adjudicated, human-reviewed relationships. Both MEDIUM
candidates have a real, built `ReviewRecord` checklist (`validation_gate.
py`), **5 of 6 items still blank**, awaiting a human domain-expert review —
this remains the actual, named bottleneck (see §4).

## 3. What was checked before making any change (avoiding duplicate work)

Before writing any new code, this session read `project_astra/docs/10-
development-log.md` and `project_astra/session_notes/2026-07-08/*.md` in
full. This surfaced a critical fact that changed the plan: **extending the
mechanistic-prior table to paracetamol and metformin — the obvious-looking
next step — had already been investigated twice (2026-07-07 and 2026-07-08
sessions) and correctly declined both times**, for real, checkable reasons:

- **Paracetamol**: no CPIC/PharmGKB guideline-tier pharmacogene exists.
  UGT1A1 was directly studied and found **not correlated** with
  acetaminophen glucuronidation (PMID 15180166) — a real negative finding,
  not an absence of study. CYP2E1/UGT1A6 have candidate-gene-tier evidence
  only, below this table's own citation bar.
- **Metformin**: SLC22A1 (OCT1) has a real PharmGKB "Very Important
  Pharmacogene" summary (PMC4035531), but the clinical evidence is
  candidate-gene-tier and genuinely mixed (one study found the effect
  "insignificant"). Not CPIC-guideline tier. SLC22A1 also has no gnomAD
  SAS/EUR coverage in the pinned artifact, so even a table entry could not
  produce a working FAERS×gnomAD join.

This session independently re-verified both conclusions via web search
against real literature (see §5) and reached the **same result** — the
mechanistic-prior table is genuinely exhausted for the 6 currently-fetched
FAERS drugs at the platform's own evidence-citation bar. **Not re-opening
this question a third time was itself the correct engineering decision**,
consistent with the project's own recurring discipline (documented in its
own `NEXT_STEPS.md`): a real product/research decision (fetch a 7th drug
with real CPIC-tier evidence, or accept a lower evidence tier) is not an
engineering call to make unilaterally.

## 4. The real, non-duplicative gap found and closed today

`session_notes/2026-07-08/HUMAN_REVIEW_NEEDED.md` item 5 named an open,
unresolved audit question:

> "We do not know how much real FAERS volume falls into the
> `unclassified_case_count` bucket in aggregate across all 6 drugs — worth
> a person checking whether any major population is being silently
> miscounted as 'unclassified' rather than correctly bucketed."

This had never been answered with real numbers — `unclassified_case_count`
existed only as a bare integer per drug, with no way to see which countries
composed it. This session answered it for real, then closed the gap in
code.

### 4.1 The real audit, run against the actual pinned data

Diffing the real pooled `raw_country_counts` (2,276,461 reports, from the
already-committed `reporting_bias_report.json`) against the module's
`REGION_COUNTRIES` five-region taxonomy (SAS/EAS/AFR/EUR/NAM):

**119,117 of 2,276,461 pooled reports (5.2%) were falling into
"unclassified" with no visibility into composition.** The largest real,
named countries inside that bucket:

| Country | Real pooled report count |
|---|---|
| *(empty/missing country code)* | 38,574 |
| Australia (AU) | 19,759 |
| Brazil (BR) | 11,602 |
| Colombia (CO) | 9,072 |
| Turkey (TR) | 4,067 |
| Russia (RU) | 3,482 |
| Croatia (HR) | 2,826 |
| Israel (IL) | 2,756 |
| Puerto Rico (PR) | 2,584 |
| Singapore (SG) | 2,117 |
| New Zealand (NZ) | 2,106 |
| Argentina (AR) | 2,092 |

Several of these individually exceed the entire, already-tracked **SAS
region's** real pooled count (5,734) or **AFR region's** real pooled count
(7,831) — meaning real, substantial population signal was invisible to
every existing reporting-bias finding, not a rounding artifact.

### 4.2 What was added — Latin America & Caribbean (LATAM), the single
### largest coherent unclassified bloc

Brazil + Colombia + Argentina + Chile + Peru + Ecuador + other UN-geoscheme
"Latin America and the Caribbean" countries together account for real,
substantial volume that was previously invisible. This is a clean,
UN-geoscheme-standard macro-region (same tier of rigor as the platform's
existing EUR/AFR regions) with a real, sourced population-share baseline —
so it was added as a **sixth named region**, not left as an unnamed
residual.

**Deliberately not added in this pass** (named, not silently skipped, same
discipline the rest of this module already follows): Oceania (AU+NZ) is
real volume but only 0.57% of world population — a ratio computed against
such a small denominator would be statistically noisy relative to its
information value. MENA-style groupings (TR/IL/SA/AE) don't have as clean a
single UN-standard macro-region definition as the other six already in use.
Both remain in `unclassified_breakdown()`'s output, named and visible, for
a future session to pick up with a real sourced baseline rather than a
guess.

## 5. Real citations verified before this change (not assumed)

- **LATAM population share (8.1%)**: statisticstimes.com's UN World
  Population Prospects (2024 revision)-derived regional breakdown — same
  secondary-aggregator source and same one-decimal precision already used
  and disclosed for the other five regions in this module (see
  `HUMAN_REVIEW_NEEDED.md` item 4's own pre-existing caveat, which applies
  identically to this new figure: not independently re-derived from UN's
  own primary tables).
- **Paracetamol/metformin re-verification** (confirming, not overturning,
  the 2026-07-07/2026-07-08 sessions' own conclusions): UGT1A1-acetaminophen
  non-correlation (PMID 15180166, re-confirmed via search); SLC22A1/OCT1
  PharmGKB VIP summary (PMC4035531) and mixed candidate-gene clinical
  evidence, re-confirmed via search.

## 6. Code changes made — precise diff summary

**File: `project_astra/astra/discovery_engine/reporting_bias.py`**

1. Added `"LATAM"` to `REGION_COUNTRIES` (27 ISO-3166-1 alpha-2 codes,
   UN-geoscheme Latin America & Caribbean, explicitly disjoint from the
   pre-existing `NAM` set — Mexico stays in `NAM`, unchanged, to avoid
   silently altering any previously-published `NAM` finding).
2. Added `"LATAM": 0.081` to `UN_WPP_2024_POPULATION_SHARE`.
3. Added `DrugRepresentationReport.unclassified_breakdown()` — a new
   read-only method returning `(country_code, count)` tuples, sorted
   descending by volume, for every `raw_country_counts` key not covered by
   any tracked region. Accepts an injectable `region_countries` parameter
   (matching `compute_drug_representation`'s existing `population_share`
   injection pattern — no hidden global state, testable with a synthetic
   region set).

**File: `project_astra/scripts/report_reporting_bias.py`**

- Added a printed (not new-JSON-field) unclassified-breakdown summary to
  the script's own console output, using the new method above. No change
  to the JSON output schema — `raw_country_counts` was already present, so
  the breakdown remains always re-derivable from already-serialized data;
  this avoids any risk of breaking an existing consumer of the JSON shape.

**File: `project_astra/tests/test_discovery_reporting_bias.py`**

- 12 new tests: LATAM country classification, LATAM/NAM disjointness, LATAM
  population-share presence, LATAM appearing in every region report,
  a regression guard asserting the pre-existing 5 regions' definitions are
  byte-identical to before this change, plus 6 tests for
  `unclassified_breakdown()` (real-code coverage, sort order, sum-equals-
  count invariant, empty-string handling, custom-region injection, and one
  test that runs the real pinned 2,276,461-report dataset end-to-end and
  locks in the real LATAM finding as a regression test).
- Fixed 1 pre-existing test (`test_most_underrepresented_among_nonzero_
  regions`) whose own stated invariant ("none of the regions at zero") no
  longer held once a 6th region existed with zero reports in that test's
  synthetic input — added one LATAM country to the input, matching the
  test's own documented intent exactly (not a workaround; the test's
  comment already explained what it wanted, and the fix restores that).

**No changes to:** `mechanistic_prior.py`, `scoring.py`, `validation_gate.py`,
`population_signal.py`, `join_faers_population_signal.py`,
`build_discovery_candidates.py`, `compose_equity_signal.py`, or any
pre-existing MEDIUM/refused candidate result. **Every previously-published
number in `docs/10`, `docs/17`, and `discovery_candidates_2026_07_08.json`
remains exactly reproducible** — this was a strictly additive change,
verified by the regression-guard test above.

## 7. Real, re-verified results after the change

Recomputed directly against the actual committed
`reporting_bias_report.json` (not a synthetic fixture):

| Region | FAERS share | Population share | Ratio | Real report count |
|---|---|---|---|---|
| SAS | 0.252% | 25.3% | 0.0100 *(unchanged)* | 5,734 |
| EAS | 2.509% | 20.1% | 0.1248 *(unchanged)* | 57,125 |
| AFR | 0.344% | 14.6% | 0.0236 *(unchanged)* | 7,831 |
| EUR | 22.158% | 8.8% | 2.5180 *(unchanged)* | 504,425 |
| NAM | 69.504% | 4.7% | 14.7881 *(unchanged)* | 1,582,229 |
| **LATAM (new)** | **1.297%** | **8.1%** | **0.1602** | **29,534** |

South Asia remains, by a wide margin, the most under-represented region
(`most_underrepresented()` still correctly returns SAS, ratio 0.0100,
unchanged) — this new region does not compete with or dilute the platform's
existing headline finding. **A new, real, secondary finding**: Latin America
& the Caribbean is also meaningfully under-represented (ratio 0.16 — reports
at ~16% of population-proportional rate), a real quantified data point that
did not exist before today, adding a second, independently-checkable
population-equity signal to the Discovery Engine's real-world evidence base.

Unclassified volume dropped from 119,117 to **89,583** (3.9% of pooled
reports) — now itself fully visible via `unclassified_breakdown()`, with
Australia (19,759) the single largest remaining named gap.

## 8. Test and lint verification

```
cd project_astra
python3 -m pytest tests/ -q     # 496 passed (was 472 before this session;
                                 # +12 new, +12 net from prior 2026-07-08
                                 # session's own work already in the tree)
ruff check astra tests scripts  # All checks passed
```

All tests pass, including the real end-to-end test against the actual
pinned dataset (`test_real_pooled_data_shows_latam_as_largest_newly_
classified_bloc`), which would fail if the pinned data file changed or the
LATAM country list regressed.

## 9. What remains genuinely open (not closed by this session, named
## honestly)

1. **The two MEDIUM Discovery Engine candidates still need human review** —
   unchanged by this session. `CYP2C9↔aspirin` and `SLCO1B1↔atorvastatin`
   each have 5 of 6 `ReviewRecord` checklist items blank. This is the
   platform's own literal exit gate and was not, and could not be, closed
   by more engineering (per `validation_gate.py`'s own "no automatic
   pass/fail logic" design). See `HUMAN_REVIEW_NEEDED.md` item 1.
2. **Oceania (AU/NZ, real ~22K pooled reports) and the MENA-style bloc
   (TR/IL/SA/AE/RU, real ~14K pooled reports) remain unclassified**,
   named and visible via the new `unclassified_breakdown()` method, but
   deliberately not added as new regions this session — see §4.2's honest
   scope limit.
3. **The `raw_partial/metformin.jsonl` 7.1GB stray file** was found but not
   deleted — a cleanup decision, not an engine question, left for whoever
   owns local disk hygiene on this workstation.
4. **The stopped VM's 230GB disk** remains un-deleted, per the 2026-07-08
   session's own explicit non-decision (`HUMAN_REVIEW_NEEDED.md` item 6) —
   unchanged, not re-litigated by this session.
5. **CPIC's "no recommendation provided" caveat for aspirin/CYP2C9**
   (`HUMAN_REVIEW_NEEDED.md` item 2) has still not been verified against
   the primary CPIC guideline PDF directly (the page requires JavaScript
   and could not be fetched) — flagged again, unresolved.

## 10. How to re-run and re-verify every number in this document

```bash
cd project_astra

# Re-run the reporting-bias engine against real BigQuery data (requires
# gcloud auth against project-885b39bc-9a80-45bf-bfd):
python3 scripts/report_reporting_bias.py \
  --project project-885b39bc-9a80-45bf-bfd --dataset anukriti_faers

# Or, offline, against the already-committed real data (no BigQuery needed):
python3 -c "
import json
from astra.discovery_engine import reporting_bias as rb
data = json.loads(open('faers_discovery/data/signals/reporting_bias_report.json').read())
report = rb.compute_drug_representation('ALL', data['pooled']['raw_country_counts'])
for r in report.by_region:
    print(r.region, r.representation_ratio)
print('unclassified:', report.unclassified_breakdown()[:10])
"

# Run the new tests specifically:
python3 -m pytest tests/test_discovery_reporting_bias.py -v
```
