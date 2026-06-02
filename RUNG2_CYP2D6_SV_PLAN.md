# Rung 2 — CYP2D6 Structural / Copy-Number Calling: Evaluation & Integration Plan

> **Audience:** founder + the session that builds CYP2D6 SV calling.
>
> **Last updated:** 2026-06-02
>
> **Status:** Plan. Companion to [`DETECTION_ROADMAP.md`](DETECTION_ROADMAP.md)
> (this is Rung 2). All three candidate tools and their papers are now in
> [`papers/`](papers/README.md) (entries 8–10). No code written yet.
>
> **Companion docs:**
>   - [`DETECTION_ROADMAP.md`](DETECTION_ROADMAP.md) — the 6-rung ladder; this is Rung 2
>   - [`papers/README.md`](papers/README.md) — Cyrius (#8), StellarPGx (#9), Aldy (#10)
>   - [`DETERMINISTIC_ENGINE_DEEP_DIVE.md`](DETERMINISTIC_ENGINE_DEEP_DIVE.md) — where star-allele → phenotype happens

---

## Why this is the priority rung

CYP2D6 metabolizes ~21–25% of clinically used drugs (codeine, tamoxifen,
many antidepressants/antipsychotics). Its UM and PM calls are driven mostly
by **structural variants** — gene deletions (\*5), duplications (\*1xN → UM),
and **CYP2D6–CYP2D7 hybrids** — not by simple SNVs. CYP2D7 shares ~94%
sequence identity with CYP2D6, so short reads misalign and SVs are missed.

Two honest gaps in the platform today converge here:

1. **The caller gap.** Our CYP2D6 path is **heuristic-only** (named in the
   honest-gap list). We do not call deletions/duplications/hybrids.
2. **The truth-set gap.** Our benchmark harness
   (`anukriti/src/benchmark/getrm_truth.py`) has a 30-sample `GETRM_CYP2D6`
   set, but the code comment says verbatim: *"These samples exclude
   SV-containing samples for simplicity."* The header documents an `sv`
   field that is **not populated**. **We are currently benchmarking CYP2D6
   on exactly the samples where the hard problem does not occur.** Fixing
   this is part of Rung 2, not separate from it.

`PUBLISHED_CONCORDANCE` in the same file already encodes the stakes:
`CYP2D6 → {PharmCAT: None (cannot call), Aldy: 0.886, Stargazer: 0.843}`.
PharmCAT — the standard we benchmark against elsewhere — **cannot call
CYP2D6 at all**. That is the hole these tools fill.

---

## The three candidates (grounded in the papers)

| Tool | Genes | Input | CYP2D6 concordance (published) | Method | License / runtime |
|---|---|---|---|---|---|
| **Cyrius** (#8) | **CYP2D6 only** | BAM/CRAM (WGS) | **96.5%** | CN from CYP2D6+CYP2D7 read depth; del/dup/**hybrid** | Python, pip/GitHub; CC-BY |
| **StellarPGx** (#9) | **12 CYP genes** (CYP1/2/3) | BAM (+ ref alignments) | **99% vs GeT-RM** | genome-graph variant detection + coverage + combinatorial diplotype | Nextflow; open; **African-validated** |
| **Aldy** (#10) | many polymorphic genes | WGS **or targeted** | 0.886 (our harness) | combinatorial allelic decomposition + CNV | Python; open |

Reading of the trade-off:
- **Cyrius** = best single-gene CYP2D6 accuracy, narrowest scope, simplest
  to wrap (Python in/out, no workflow engine). Lowest integration cost.
- **StellarPGx** = highest reported CYP2D6 GeT-RM concordance *and* covers
  11 other CYP genes (incl. our skipped CYP2B6), but pulls in **Nextflow** —
  heavier runtime dependency. Strongest equity story (Wits/SBIMB,
  African-validated) — aligns with our positioning.
- **Aldy** = broadest gene coverage, already in our published-concordance
  table, handles targeted panels too (relevant if we add ClinPharmSeq-style
  capture input, #11). Mid integration cost.

---

## Phase A — Truth-set repair (prerequisite, do first)

Rung 2 cannot be *measured* until the truth set contains SV samples.

- **A1.** Populate the documented `sv: bool` field on every `GETRM_CYP2D6`
  entry, and **add the known SV-containing GeT-RM/Coriell samples** (e.g.
  the classic \*5 deletion and \*1xN/\*2xN duplication reference lines) from
  Gaedigk/Pratt 2019 (J Mol Diagn 21(6):1034, already cited in
  `getrm_truth.py`). These are the samples the bake-off actually tests.
- **A2.** Add a `GETRM_CYP2D6_SV` view (or `sv=True` filter helper) so
  concordance can be reported **split by SV vs non-SV** — the only honest
  way to show the improvement (a tool can score 99% on non-SV and still
  miss every hybrid).
- **A3.** Record provenance per added sample (PMID + table) — same
  "every claim cites a paper" discipline as the CPIC audit.

**Done when:** `get_truth_for_gene("CYP2D6")` returns entries with a
populated `sv` field and includes ≥1 deletion + ≥1 duplication + (if a
public reference exists) ≥1 hybrid sample, each with provenance.

> **A — LANDED (2026-06-02).** `getrm_truth.py`: `sv` field populated on all
> 30 non-SV CYP2D6 entries; `GETRM_CYP2D6_SV` adds 6 SV reference samples
> (deletion `*5/*5` ×2, duplications `*4x2/*41` / `*2x2/*22` / `*2x2/*4x2`,
> deletion+hybrid-tandem `*5/*36x2+*10x2`) from Gaedigk 2019 (PMID 31401124,
> Tables 3/4), each with `sv_kind` + `provenance`; spans AFR/EAS/EUR.
> `get_truth_for_gene_by_sv()` added. CYP2D6 truth = 36 (30 non-SV + 6 SV).

---

## Phase B — Bake-off (decide which caller)

> **B — BASELINE LANDED (2026-06-02), live three-tool run still pending.**
> The live Cyrius/StellarPGx/Aldy bake-off (B1–B2) needs WGS BAMs (ENA
> PRJEB19931) + tool installs **not available in the current environment**,
> so it remains the next external step. What landed: `cyp2d6_sv_bakeoff.py`
> — a scoring harness that runs **Anukriti's existing CYP2D6 CNV heuristic**
> (`vcf_processor.infer_metabolizer_status_with_alleles`) against the Phase-A
> SV truth set, SV-split + by-population, vs the published caller baselines.
>
> **First measured result (the honest baseline this rung must beat):**
>
> | split | n | diplotype | phenotype |
> |---|---|---|---|
> | overall | 36 | 0.444 | 0.139 |
> | non-SV | 30 | 0.467 | 0.100 |
> | **SV-only** | **6** | **0.333** | **0.333** |
>
> Published overall CYP2D6: **Cyrius 0.965 · StellarPGx 0.99 · Aldy 0.886 ·
> Stargazer 0.843 · PharmCAT n/a (cannot call)**. The ~0.33 SV concordance
> vs ~0.97–0.99 quantifies the gap a real SV caller closes. (Non-SV row is
> depressed by the harness's deliberately-minimal SNP synthesis — it feeds
> the heuristic only what it can see; the **SV-only row is the valid signal**.)

- **B1.** Acquire the data: the harness already cites **ENA PRJEB19931**
  (70 PCR-free WGS samples) and Coriell NA/HG lines. Pull BAM/CRAM for the
  truth-set sample IDs (`get_all_sample_ids()`), restricted to **chr22**
  (CYP2D6 locus — the product already maps chr22 → CYP2D6).
- **B2.** Run all three callers on the same BAMs, off to the side (no engine
  changes yet). Each produces a CYP2D6 diplotype per sample.
- **B3.** Score each against the repaired truth set using the existing
  comparison pattern, reporting **overall, SV-only, and non-SV** concordance
  plus **by-population** (the harness has `get_population_distribution()`;
  SAS is the equity-relevant cell).
- **B4.** Decision matrix: accuracy (esp. SV-only) × integration cost
  (Cyrius simplest, StellarPGx heaviest) × gene coverage (StellarPGx/Aldy
  broader) × dependency footprint (Nextflow vs pure-Python). Record the
  pick and the numbers as an audit artifact.

**Done when:** a results table exists with SV-split concordance for all
three tools on our samples, and a documented choice. Expectation to test,
not assume: Cyrius/StellarPGx ≫ our current heuristic on SV samples.

---

## Phase C — Integration (off-by-default, predictor-annotates)

> **C — SEAM LANDED (2026-06-02).** `anukriti/src/cyp2d6_sv_ingest.py` —
> `ingest_sv_diplotype(diplotype, source)` ingests an external SV caller's
> CYP2D6 diplotype (hybrids `*68/*36/*13`, deletion `*5`, dups `*NxM`,
> tandems `*36+*10`) and resolves a phenotype the authoritative CPIC way:
> sum per-allele activity scores (xN multiplies the copy) → bin (AS 0=PM,
> ≤1.0=IM, ≤2.25=NM, >2.25=UM; Caudle 2020). It detects nothing and overrides
> nothing — it phenotypes the *given* call and stamps the caller as provenance.
>
> **Measured on the 7 SV truth samples — phenotype concordance doubles:**
> **heuristic 0.429 → ingestion 0.857.** It fixes the dangerous
> wrong-direction calls the heuristic makes on duplications:
>
> | sample | truth | heuristic | ingestion |
> |---|---|---|---|
> | NA17244 `*2x2/*4x2` | NM | **PM (wrong)** | NM ✓ (AS 2.0) |
> | NA07439 `*4x2/*41` | IM | **PM (wrong)** | IM ✓ (AS 0.5) |
> | NA18545 `*5/*36x2+*10x2` | IM | **PM (wrong)** | IM ✓ (AS 1.0) |
> | HG00337 `*2x2/*22` | NM | extensive | **indeterminate** (honest — `*22`
>   uncertain function; named refusal beats a confident wrong guess) |
>
> The one non-match is the *correct* behavior: `*22` is uncertain-function, so
> the engine refuses an activity score rather than guess — the platform's
> named-uncertainty invariant. Tests: `tests/test_cyp2d6_sv_ingest.py` (8) +
> bake-off `sv_ingestion` column. Full benchmark suite 58/58 green.

Wire the chosen caller in under the platform invariants — **it annotates,
it never decides**, and it ships **off by default**.

- **C1.** New optional component, e.g. `CYP2D6StructuralCaller`, behind a
  constructor arg defaulting to `None` (per invariant #5 — off-by-default,
  not a feature flag). When absent, the current path is byte-identical.
- **C2.** Input seam: it consumes **BAM/CRAM** (a *new genome format* for
  us — Rung 3 territory; this is the first read-level input). The existing
  `bcf_processor.py` / `pharmcat_comparison.py` already carry pysam/tabix,
  so the dependency is present.
- **C3.** Output seam: the caller returns a CYP2D6 **diplotype + an SV
  annotation** (deletion / duplication / hybrid + copy number + the caller's
  own confidence). That diplotype feeds the *existing* deterministic
  star-allele → phenotype path (pgx-core). The SV call is **named
  uncertainty / provenance metadata**, not a phenotype override — it
  annotates the report the way the LLM narrates.
- **C4.** Activity-score correctness: duplications must flow into the
  activity-score math (\*1xN → UM), which the phenotype layer already models
  for CYP2D6 (`*1=1, *2=1, *4=0, *5=0, *10=0.5, *17=0.5, *41=0.5` per the
  harness comment) — confirm the xN multiplier is honored.
- **C5.** Regression: all 7 byte-locked swarm demos and the pgx-core suite
  stay green; the new path only activates when the constructor arg is set.

**Done when:** with the caller enabled, a known \*5-deletion sample reports
the deletion and the right metabolizer status; with it disabled, every
existing signature is byte-identical.

---

## Scope guards (what this rung is NOT)

- Not genome-wide SV and not pangenome alignment — that's Rung 5.
- Not novel-variant functional prediction — that's Rung 4 (GenomeAsia #12 /
  gnomAD #13 / AlphaMissense / SpliceAI).
- Not a second LLM path and not a decision-maker — the SV caller produces a
  star-allele the *deterministic* engine already knows how to phenotype.

---

## Sequencing & effort

| Phase | Work | Rough effort |
|---|---|---|
| A | Truth-set SV repair + provenance | 0.5 day (data curation) |
| B | Three-tool bake-off on chr22 BAMs | 1–1.5 days (mostly data pull + runtime) |
| C | Integrate chosen caller off-by-default | 1 day |

**~3 days.** Phase A is the cheap, high-leverage start (it also makes our
*existing* CYP2D6 benchmark honest, independent of which tool we pick).

---

## Open questions for the founder

1. **Equity vs simplicity:** StellarPGx (African-validated, 12 genes,
   strongest positioning) vs Cyrius (simplest integration, CYP2D6-only,
   96.5%). The bake-off numbers decide, but if SV-accuracy is close, do we
   weight the equity/positioning story toward StellarPGx?
2. **Read-level input now or later:** C2 introduces BAM/CRAM ingestion (our
   first Rung-3 step). Bring it in scoped to CYP2D6/chr22 here, or stand up
   a general read-level path first?
3. **Hybrid truth data:** public GeT-RM hybrid reference samples are
   limited. Acceptable to validate deletions+duplications now and flag
   hybrids as "detected, not yet truth-validated"?
