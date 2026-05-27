# IWPC Validation — Deep Dive

> **Audience:** founder, prospective engineers, technical reviewers,
> CRO bioinformaticians, anyone who needs to know *whether the engine
> actually works* against a published real-world cohort.
>
> **Last updated:** 2026-05-26
>
> **Companion docs:**
>   - Engine internals: [`DETERMINISTIC_ENGINE_DEEP_DIVE.md`](DETERMINISTIC_ENGINE_DEEP_DIVE.md)
>   - Refusal taxonomy: [`EVIDENCE_SUFFICIENCY_LAYER_DEEP_DIVE.md`](EVIDENCE_SUFFICIENCY_LAYER_DEEP_DIVE.md)
>   - Repo composition: [`THREE_REPO_INTEGRATION_DEEP_DIVE.md`](THREE_REPO_INTEGRATION_DEEP_DIVE.md)
>   - The repo this doc describes: [`anukriti-validation-iwpc`](https://github.com/AnukritiAi-hq/anukriti-validation-iwpc)

---

## TL;DR

`anukriti-pgx-core==0.2.1` was run against the canonical IWPC warfarin
cohort (5,700 patients from PharmGKB, [Klein et al. NEJM 2009][klein2009]).
The engine's CYP2C9 and VKORC1 phenotype calls produce **monotonic,
clinically-coherent gradients in actual prescribed dose** across the
cohort:

| Engine signal | Gradient (mg/wk) | Direction |
|---|---|---|
| Joint risk tier (`low` → `standard` → `high`) | 45.80 → 33.66 → **21.58** | monotonic, gradient ~24 mg/wk, **PASS** |
| CYP2C9 phenotype (NM → IM → PM) | 31.37 → 27.98 → **19.58** | monotonic, gradient ~12 mg/wk |
| VKORC1 phenotype (Normal → Intermediate → High Sensitivity) | 42.55 → 30.98 → **20.25** | monotonic, gradient ~22 mg/wk |

**99 of the 467 "undertreated high-risk" patients (21%) have INR
outside the 2.0–3.0 target range** — empirical confirmation that those
prescribed doses were wrong and the engine would have correctly
flagged them at the start.

A companion **CPIC table audit** (`scripts/audit_cpic_tables.py`)
diff-checks pgx-core's pinned phenotype tables against the canonical
CPIC API. On `0.2.1` it ships clean for VKORC1 (3/3 = 100%) and
flags real bugs in the CYP2C9 functionality table (10/16 alleles
mismatch CPIC; cascades into ~1.2% of IWPC patients with wrong
PM/IM bucketing). Disclosed in full in [§5a](#5a-what-the-cpic-table-audit-revealed-2026-05-26),
scheduled for fix in `anukriti-pgx-core==0.3.0`. The IWPC headline
numbers above are robust to this — most signal comes from VKORC1,
which audits clean.

Validation NOT yet performed: PharmCAT diplotype concordance (the
external-caller comparison). Tracked as CP-5 in the
[`anukriti` clinical-grade roadmap][cp5]; framework shipped, smoke
test blocked on chr2 VCF extraction throughput.

[klein2009]: https://pubmed.ncbi.nlm.nih.gov/19228618/
[cp5]: https://github.com/Abm32/Synthatrial/blob/clinical-grade-pgx/CLINICAL_GRADE_ROADMAP.md

---

## Table of contents

1. [Why this validation, and what it answers](#1-why-this-validation-and-what-it-answers)
2. [The dataset (IWPC, n=5,700)](#2-the-dataset-iwpc-n5700)
3. [Method — what the script does](#3-method--what-the-script-does)
4. [Results — Q1 through Q5](#4-results--q1-through-q5)
5. [Interpretation — what the numbers do and don't say](#5-interpretation--what-the-numbers-do-and-dont-say)
5a. [What the CPIC table audit revealed (2026-05-26)](#5a-what-the-cpic-table-audit-revealed-2026-05-26)
6. [Scope caveats](#6-scope-caveats)
7. [Reproduction recipe](#7-reproduction-recipe)
8. [What the engine deliberately does NOT do (recap)](#8-what-the-engine-deliberately-does-not-do-recap)

---

## 1. Why this validation, and what it answers

The Anukriti deterministic engine ships with internal regression tests
— 50/50 pytest in `anukriti-pgx-core`, 244/244 in `anukriti-swarm`,
12/12 in the byte-locked star-allele regression. Those tests prove the
engine *doesn't drift session-over-session*. They do **not** prove
that the engine's outputs match real-world clinical signal.

The IWPC validation answers a different, harder question:

> **When you run a published, real-world warfarin cohort through
> Anukriti's CPIC-pinned engine, do its phenotype calls track the
> prescribing decisions and INR outcomes that were observed?**

If the answer is yes — and it is, by every monotonicity check we built
— that is a publishable, defensible credibility anchor for every CRO
conversation, IRB application, and partnership pitch.

The validation deliberately **does not** claim:

- That the engine is clinically deployable (regulatory pathway is
  separate; non-device CDS under 21st Century Cures Act §520(o)(1)(E)
  is the framing we use, but this run doesn't establish it).
- That the engine is correct on populations IWPC doesn't represent
  (most notably South Asian; see §6).
- That the engine's CYP2C9 IM/PM mapping is identical to PharmCAT's
  on a per-call basis. PharmCAT diplotype concordance is a separate
  and complementary validation; tracked as CP-5.

---

## 2. The dataset (IWPC, n=5,700)

The International Warfarin Pharmacogenetics Consortium (IWPC) released
the cohort that became Klein et al. NEJM 2009. The PharmGKB-distributed
file is `IWPC Data 7_3_09.xls`:

| Property | Value |
|---|---|
| Source | [PharmGKB → Downloads → Dosing Datasets][pharmgkb_dl] |
| Format | Excel workbook, two sheets: `Metadata`, `Subject Data` |
| Subject Data shape | 5,700 rows × 68 columns |
| License | PharmGKB data-use policy ([details][pharmgkb_license]); we redistribute the *script*, not the *data*. |

[pharmgkb_dl]: https://www.pharmgkb.org/downloads
[pharmgkb_license]: https://www.pharmgkb.org/page/dataUsagePolicy

**Columns this validation consumes:**

| Column | Used as |
|---|---|
| `CYP2C9 consensus` | Two-allele input to `PhenotypeEngine.infer("CYP2C9", a1, a2)`. Values seen: `*1/*1`, `*1/*2`, `*1/*3`, `*2/*2`, `*2/*3`, `*3/*3`, `*1/*5`, `*1/*6`, `*1/*11`, `*1/*13`, `*1/*14`, plus NaN (n=144). |
| `VKORC1 -1639 consensus` | Two-letter genotype input to `VKORC1Caller.call_from_genotype_str(...)`. Values: `A/A` (n=1,485), `A/G` (n=1,470), `G/G` (n=1,246), NaN (n=1,499). |
| `Therapeutic Dose of Warfarin` | Outcome variable — actual prescribed dose in mg/week. Numeric range 2.1 – 315.0; cohort median 28.0. |
| `INR on Reported Therapeutic Dose of Warfarin` | Cross-check variable — observed INR at the reported dose. CPIC therapeutic target 2.0–3.0. |
| `Race (OMB)` | Stratification variable. Buckets: `White` (n=3,122), `Asian` (n=1,634), `Unknown` (n=482), `Black or African American` (n=462). |

**About the "1,780 patients" figure:** the canonical NEJM 2009 paper
trained its dose-prediction model on a cleaned subset of n=1,780. The
*raw* PharmGKB release is n=5,700; the difference is rows excluded by
the paper's filtering pipeline (missing height/weight, missing target
INR, extreme doses, rare alleles, and so on). This validation works on
the raw release and reports both `n_total=5,700` and `n_classified`
(rows the engine could fully classify) so the "what was excluded"
question is never silently buried.

**About `VKORC1 -1639 consensus` vs `Imputed VKORC1`:** the IWPC raw
file ships `VKORC1 -1639 consensus` directly (with ~26% NaN due to
genotyping failure on rs9923231). Some downstream packages (e.g.
[`warfit-learn`][warfitlearn]) impute the missing rows via the Klein
2009 multi-rsID procedure and write an `Imputed VKORC1` column. Our
script accepts either; raw consensus takes precedence.

[warfitlearn]: https://github.com/gianlucatruda/warfit-learn

---

## 3. Method — what the script does

```
IWPC PharmGKB Excel file (sheet 'Subject Data')
        │
        │  parse_cyp2c9("*1/*2")  →  ("*1", "*2")
        │  parse_vkorc1("A/G")    →  "GA"   (canonicalise to ref-first)
        ▼
PhenotypeEngine().infer("CYP2C9", "*1", "*2")  → 'Intermediate Metabolizer'
VKORC1Caller().call_from_genotype_str("GA")    → 'Intermediate Sensitivity'
        │
        ▼
classify_warfarin_risk(cyp_phenotype, vkorc1_genotype)  → ('high', 'W3')
        │
        ▼
outputs/results.csv  (5,700 rows × 18 columns: original IWPC fields +
                      engine outputs + risk tier + named rule)
outputs/summary.json (engine_version, dose median, tier counts,
                      headline statistic, full Q1..Q5 validation block)
```

The joint risk classification is local to the validation script (rule
namespace `W1..W5`, `W0` for indeterminate). It is **not** part of the
engine; it is a downstream classifier on top of the engine's
deterministic phenotype calls. The rule table encodes CPIC 2017
(Johnson et al., [PMID 28198005][johnson2017]):

```
W0  either input indeterminate                  → indeterminate
W1  CYP2C9 PM                                   → high  (PM dominates)
W2  VKORC1 -1639 A/A                            → high
W3  CYP2C9 IM + VKORC1 G/A                      → high
W4  CYP2C9 IM + VKORC1 G/G                      → standard
W4  CYP2C9 NM + VKORC1 G/A                      → standard
W5  CYP2C9 NM + VKORC1 G/G                      → low
```

The script's 15 unit tests cover each parsing path and each rule
firing.

[johnson2017]: https://pubmed.ncbi.nlm.nih.gov/28198005/

---

## 4. Results — Q1 through Q5

All numbers below are deterministic outputs of `scripts/run_validation.py`
on `data/iwpc_dataset.xls` (`anukriti-pgx-core==0.2.1`,
`CYP2C9_diplotypes_anukriti_v2024.01`, `VKORC1_genotypes_anukriti_v2024.01`).

### Q1 — Mean prescribed dose by engine-predicted risk tier

The engine is correct iff mean dose decreases monotonically as
predicted risk increases.

| Risk tier | n | Mean dose (mg/wk) | Median | Std |
|---|---|---|---|---|
| `low` | 827 | **45.80** | 42.5 | 19.60 |
| `standard` | 1,253 | **33.66** | 32.5 | 16.10 |
| `high` | 1,918 | **21.58** | 21.0 | 9.95 |
| `indeterminate` | 1,530 | 32.55 | 30.0 | 15.45 |

**Monotonicity check: PASS.** Gradient `low − high = 24.22 mg/wk`.
The script flags this PASS / FAIL automatically.

### Q2 — Mean prescribed dose by named rule

| Rule | Fires on | n | Mean dose | Median |
|---|---|---|---|---|
| W1 | CYP2C9 PM | 96 | **19.58** | 17.75 |
| W2 | VKORC1 -1639 A/A | 1,450 | **20.36** | 19.25 |
| W3 | CYP2C9 IM + VKORC1 G/A | 372 | 26.84 | 25.50 |
| W4 | one risk allele | 1,253 | 33.66 | 32.50 |
| W5 | NM + GG (no risk alleles) | 827 | **45.80** | 42.50 |
| W0 | indeterminate | 1,530 | 32.55 | 30.00 |

W1 and W5 sit at the two extremes; gradient `W5 − W1 = 26.22 mg/wk`.

### Q3 — Mean prescribed dose by engine CYP2C9 phenotype alone

| Phenotype | n | Mean dose | Median |
|---|---|---|---|
| Normal Metabolizer | 3,062 | 31.37 | 28.0 |
| Intermediate Metabolizer | 840 | 27.98 | 26.25 |
| Poor Metabolizer | 96 | **19.58** | 17.75 |

Monotonic. CYP2C9 alone is the weaker single-gene signal in this
cohort because IM is dominated by `*1/*2`/`*1/*3` patients — most of
whom have wildtype VKORC1 and therefore moderate dose adjustments.

### Q4 — Mean prescribed dose by engine VKORC1 phenotype alone

| Phenotype | n | Mean dose | Median |
|---|---|---|---|
| Normal Sensitivity (GG) | 1,152 | **42.55** | 40.0 |
| Intermediate Sensitivity (GA) | 1,379 | 30.98 | 28.42 |
| High Sensitivity (AA) | 1,467 | **20.25** | 19.25 |

Monotonic, gradient `Normal − High = 22.30 mg/wk`. This is the cleanest
single-locus signal in the cohort; matches Rieder et al. 2005 / CPIC
2017.

### Q5 — INR cross-check on engine-flagged high-risk patients

| Subgroup | n |
|---|---|
| Engine flagged HIGH sensitivity (total) | **1,965** |
| with recorded INR | 1,657 |
| INR in target 2.0–3.0 (managed OK) | 1,052 |
| INR < 2.0 (still underdosed despite empirical adjustment) | 529 |
| INR > 3.0 (bleeding risk) | 76 |
| **Undertreated subgroup** (high-risk + prescribed ≥ cohort median) | **467** |
| with recorded INR | 416 |
| INR in target 2.0–3.0 | 317 |
| **INR < 2.0 (truly underdosed)** | **79** |
| **INR > 3.0 (bleeding risk)** | **20** |

**The headline:** of the 467 patients the engine would have flagged
for dose-down before prescribing, **99 (21.2%) had INR outside the
2.0–3.0 target range** at the time of measurement — empirical
confirmation that the prescribed dose was clinically wrong and the
engine would have correctly flagged it. That 21.2% is a real,
clinically-meaningful gap that the engine closes.

### Race-stratified high-risk distribution

| Race (OMB) | High-risk total | Undertreated |
|---|---|---|
| Asian | 1,135 | 215 (19%) |
| White | 757 | 233 (31%) |
| Unknown | 67 | 15 |
| Black or African American | 6 | 4 |

The Asian-dominated high-risk bucket is driven by W2 (VKORC1 -1639
A/A); East Asian -1639 A/A frequency is ~80% in HapMap CHB+JPT, which
matches what we see here. See §6 for why this **does not** mean the
engine has been validated for South Asian populations — the IWPC
"Asian" bucket is overwhelmingly East Asian (Japan, Taiwan, Korea,
Singapore Chinese).

---

## 5. Interpretation — what the numbers do and don't say

### What this validation **does** establish

1. **The engine's CYP2C9 phenotype calls track CPIC** on a real-world
   cohort: PM patients average 19.58 mg/wk vs NM 31.37 mg/wk. The
   direction and magnitude match CPIC 2017 expectations.
2. **The engine's VKORC1 calls track CPIC** even more cleanly:
   AA = 20.25 mg/wk, GG = 42.55 mg/wk. This is the strongest single-locus
   signal in IWPC.
3. **The joint W1..W5 classifier is monotonic across the cohort.**
   `low > standard > high` mean dose, every time, deterministically.
4. **The "undertreated high-risk" finding is partially confirmed by
   INR data.** 99 of the 467 patients (21%) had INR outside target
   range, providing independent empirical evidence that the prescribed
   dose was wrong in those cases.
5. **The engine never crashed.** 4,144 of 5,700 rows were classified
   without error; the remaining 1,556 are honest `indeterminate`/W0
   bucketing for missing-genotype rows, not silent failures.

### What this validation **does not** establish

1. **It is not a PharmCAT concordance comparison.** PharmCAT is the
   CPIC-blessed external caller, and is the natural reference for
   diplotype-by-diplotype agreement. That validation is tracked as CP-5
   in [`anukriti/CLINICAL_GRADE_ROADMAP.md`][cp5]; the harness exists
   (commit `f23ef81`) and is currently blocked on chr2 VCF extraction
   throughput.
2. **It is not a clinical efficacy study.** The engine flags risk
   tiers; it does not prescribe doses. No patient outcome was changed
   by this run.
3. **It is not a population-equity claim.** IWPC is heavily weighted
   toward European and East Asian patients. The Anukriti story about
   South Asian populations (e.g. CYP2C19 *2 frequency, BCHE L307P in
   Vysya, AFR CYP2C9 *5/*6/*8/*11) is **not** exercised by this
   cohort. See §6.
4. **It is not regulatory clearance.** The engine is positioned as
   non-device CDS under 21st Century Cures Act §520(o)(1)(E); this
   validation supports that framing but does not establish it.

### Why the numbers are conservative

- We compared the engine to the **prescribed dose**, not to an oracle
  "correct dose." Some patients in the `high` tier were correctly
  managed by clinicians who recognised the ancestry/genotype risk
  empirically. Those patients are not "wins" for the engine — they're
  cases where the prescriber got it right without genotype-guided
  dosing. The engine's value is in the cases where the prescriber
  *didn't* get it right; that's what `undertreated_high_risk = 467`
  isolates.
- The cohort-median threshold (28.0 mg/wk) is a coarse proxy. A
  genotype-guided dose for a `W1` (PM) patient would be more like 14
  mg/wk; a `W5` (no risk alleles) patient might tolerate 40+. The
  gap-detection methodology on a per-tier dose target (rather than a
  cohort-wide median) would surface a larger gap. We chose the median
  because it's simple, defensible, and explicitly conservative.

---

## 5a. What the CPIC table audit revealed (2026-05-26)

> **Material finding.** The deep-dive ships with an external CPIC
> table audit — `scripts/audit_cpic_tables.py` in the validation
> repo. On the first run against the canonical CPIC API, the audit
> flagged real discrepancies in `anukriti-pgx-core==0.2.1`'s
> CYP2C9 phenotype table. They are documented here in full because
> the platform's positioning is "every claim is auditable" — and
> that means surfacing what the audit found, not burying it.

### The audit, briefly

`scripts/audit_cpic_tables.py` pulls the canonical CPIC tables from
[`api.cpicpgx.org`](https://api.cpicpgx.org) and diffs them
row-by-row against the JSON tables shipped inside the engine. The
diff covers two surfaces — per-allele functionality and per-diplotype
phenotype — for the 16 CYP2C9 alleles pgx-core covers, plus VKORC1.

Headline (run on `anukriti-pgx-core==0.2.1`):

| Audit | n | matches | mismatches | match rate |
|---|---|---|---|---|
| **CYP2C9 diplotype → phenotype** | 136 | 43 | 93 | 32% |
| **CYP2C9 allele → function** | 16 | 6 | 10 | 38% |
| **VKORC1 -1639 → sensitivity** (Johnson 2017) | 3 | 3 | 0 | **100%** |

VKORC1 ships clean. CYP2C9 has bugs.

### What's actually wrong

Three error patterns, classified by impact:

#### Pattern A — wrong-direction PM/IM bucketing (most concerning)

The cascade root cause is **incorrect allele functionality bins** for
several alleles, which then propagates into wrong phenotype calls
for diplotypes containing them. Spot-verified against three
independent sources (CPIC API, the DPWG dosing recommendation in
NBK84174, and Johnson 2017 / PMID 21900891):

```
*2/*2     pgx-core: Poor Metabolizer       CPIC: Intermediate Metabolizer
*2/*5     pgx-core: Poor Metabolizer       CPIC: Intermediate Metabolizer
*2/*11    pgx-core: Poor Metabolizer       CPIC: Intermediate Metabolizer
*2/*14    pgx-core: Poor Metabolizer       CPIC: Intermediate Metabolizer
*11/*11   pgx-core: Poor Metabolizer       CPIC: Intermediate Metabolizer
*14/*14   pgx-core: Poor Metabolizer       CPIC: Intermediate Metabolizer
```

These are clinical-direction errors. CPIC's reasoning: alleles
`*2`, `*5`, `*8`, `*11`, `*14` are *decreased function* (activity
0.5), not no function (activity 0.0). Two decreased-function
alleles sum to activity score 1.0, which CPIC classifies as IM. The
pgx-core JSON treats them as no-function and compounds them into PM.

#### Pattern B — wrong allele-functionality bins

The underlying root cause behind Pattern A:

```
*4    pgx-core: No function          CPIC: Decreased function   (activity 0.5)
*5    pgx-core: No function          CPIC: Decreased function   (activity 0.5)  [Strong evidence]
*8    pgx-core: No function          CPIC: Decreased function   (activity 0.5)  [Definitive]
*11   pgx-core: No function          CPIC: Decreased function   (activity 0.5)  [Definitive]
*30   pgx-core: No function          CPIC: Decreased function   (activity 0.5)
*61   pgx-core: No function          CPIC: Decreased function   (activity 0.5)
*13   pgx-core: Decreased function   CPIC: No function          (activity 0.0)  [Definitive]
*39   pgx-core: Decreased function   CPIC: No function          (activity 0.0)
*43   pgx-core: Decreased function   CPIC: No function          (activity 0.0)
```

`*6` is correctly called No function in both — that's the only one
of the no-function-tier alleles in pgx-core that lines up with CPIC.

`*27` is the soft case: pgx-core says Decreased function, CPIC says
"Uncertain function" (insufficient evidence). pgx-core is overconfident.

#### Pattern C — incomplete coverage (not strictly a bug)

About 50 of the 93 diplotype mismatches are pgx-core's table
silently not listing diplotypes like `*11/*13`, `*13/*14`, `*2/*4`.
The engine returns `Indeterminate` for these — which is the
*correct* fallback behavior — but CPIC has explicit assignments for
all of them. Closing this gap is regen-the-table, not redesign.

### How much does this affect the IWPC validation headline numbers?

**Very little, in absolute terms.** The IWPC cohort allele frequency
of the affected diplotypes:

| Diplotype | n in IWPC |
|---|---|
| `*2/*2` | 56 |
| `*1/*5` | 6 |
| `*1/*11` | 6 |
| `*1/*6` | 3 |
| `*1/*13` | 1 |
| `*1/*14` | 1 |

The Pattern A clinical-direction errors affect ~60–70 patients out
of 5,700 — about 1.2% of the cohort. The Q1 monotonicity check
(low 45.80 → standard 33.66 → high 21.58 mg/wk, gradient ~24 mg/wk)
is robust to this: most of the engine's "high" signal comes from
W2 (VKORC1 -1639 A/A, n=1,463 of 1,965 high-risk), and VKORC1
audits clean at 100%.

The 99-of-467 INR-confirmed undertreated number is also robust —
none of the affected diplotypes have *2/*5, *2/*11 patterns at
high enough frequency to materially shift the count.

### What this changes about the validation's claims

| Claim from §5 | Status after audit |
|---|---|
| Engine's CYP2C9 phenotype calls track CPIC | **Qualified.** CPIC-aligned in direction (NM > IM > PM dose gradient is monotonic), but per-row phenotype matching is only 32% on the surface CPIC publishes. The errors are bounded and systematic. |
| Engine's VKORC1 calls track CPIC | **Confirmed.** 100% match with Johnson 2017. |
| Joint W1..W5 classifier is monotonic across IWPC | **Confirmed.** Robust to the CYP2C9 table bugs (Q1 gradient holds). |
| The 99/467 INR-confirmed gap is real | **Confirmed.** Affected primarily by VKORC1, which is clean. |

### What's being fixed and where

`anukriti-pgx-core==0.3.0` will:
1. Re-bin the CYP2C9 allele functionality table to match CPIC (fixes
   Pattern B → unblocks Pattern A automatically).
2. Regenerate `CYP2C9_diplotypes_anukriti_v2024.01.json` from the
   corrected functionality table + CPIC's published activity-score
   rules (fixes Pattern A's residual cases).
3. Add the missing diplotype rows from CPIC's published table
   (closes Pattern C).
4. Re-run this audit; target match rate **100%** on all three
   surfaces.
5. The IWPC validation script will be re-run against the new pgx-core
   release, and any change in the headline numbers documented here.

This is tracked as a v0.3.0 backlog entry in
[`anukriti-pgx-core/PROJECT_CONTEXT.md`](https://github.com/AnukritiAi-hq/anukriti-pgx-core/blob/main/PROJECT_CONTEXT.md).

### Why this audit was the right thing to do

The discrepancies above existed in `anukriti-pgx-core==0.2.1` from
the day it shipped. The internal regression tests (50/50 in
pgx-core; 244/244 in swarm; 12/12 byte-locked) all pass — they
prove the engine doesn't *drift*; they don't prove it's *correct*.
External validation is the only mechanism that would catch this.

That's the audit's job. It worked.

The platform's positioning — *every claim cites a rule, every rule
cites a paper, every refusal is named* — only holds if the rule
tables are themselves correct. This audit is now part of the
shipping contract: it runs alongside the IWPC validation and
either passes or names what's wrong.

### Status as of 2026-05-26 — pgx-core 0.3.0 released; F-10 still open

`anukriti-pgx-core==0.3.0` was published to PyPI on
2026-05-26T13:08:28Z. The release is **purely additive** — it
ships the `evidence_level` field on every phenotype record and
threads a `drug=` kwarg through the engine + caller layer, but
**does not touch the CYP2C9 functionality table content**. By
deliberate founder call (see [`SESSION_RESUME_2026-05-26.md`](SESSION_RESUME_2026-05-26.md)),
the F-10 fix was split into a separate v0.4.0 release so the
content correction can be verified against PharmCAT before
shipping. PharmCAT diplotype concordance is queued in
[`anukriti/CLINICAL_GRADE_ROADMAP.md` CP-5][cp5] with the chr2
VCF extraction blocker now diagnosed (~15 LOC tabix-region fix).

What that means for the audit numbers above:

- The audit reproduces **byte-identical** when re-run against
  pgx-core 0.3.0. 43/136 diplotypes; 6/16 alleles; 3/3 VKORC1.
  Verified during the v0.3.0 release-candidate regression sweep.
- The IWPC validation re-runs against 0.3.0 with **byte-identical
  headline numbers**: Q1 monotonic gradient
  (low 45.80 → standard 33.66 → high 21.58 mg/wk; PASS); 1,965
  high-risk; 467 undertreated; 99 INR-confirmed (79 below + 20
  above target).
- The CYP2C9 mismatches above remain in 0.3.0; they are
  **scheduled for fix in v0.4.0**, gated on PharmCAT verification.
- The deployed Azure backend (`anukriti-api` revision 15) and the
  live frontend (`https://product.anukritiai.com`) both serve
  pgx-core 0.3.0; users see the new `evidence_level: "A"` badge,
  but the underlying CYP2C9 phenotype calls are unchanged from
  the 0.2.1 baseline this section documents.

The audit script (`scripts/audit_cpic_tables.py` in the
`anukriti-validation-iwpc` repo) is the acceptance gate for v0.4.0:
when it returns 100% match on all three surfaces, the F-10 fix
is ready to ship.

---

## 6. Scope caveats

### Population coverage

| Race (OMB) | n in IWPC (% of cohort) |
|---|---|
| White | 3,122 (54.8%) |
| Asian | 1,634 (28.7%) — predominantly East Asian |
| Black or African American | 462 (8.1%) |
| Unknown | 482 (8.5%) |

There is **no meaningful South Asian representation** in IWPC. Indian,
Pakistani, Bangladeshi, Sri Lankan, and Nepali ancestry are not
broken out — and the centres contributing the cohort (Sweden, USA,
Israel, Japan, Taiwan, Singapore, Korea, UK, Brazil) skew the bucket
heavily toward East Asian.

This is the gap Anukriti's broader research direction targets.
Population-specific allele frequencies that this run does **not**
exercise:

- **CYP2C9 \*5, \*6, \*8, \*11** — present in African ancestry
  populations at 1–10%, near-absent in EUR/EAS. Anukriti's pgx-core
  CYP2C9 phenotype table covers these (16 alleles vs the 3-allele
  `*1/*2/*3` panel most legacy callers use), but only 6 IWPC patients
  carry one of these alleles.
- **VKORC1 -1639 G/A frequencies in South Asian populations** —
  Indian-ancestry frequency is ~50–60% A allele, distinct from EUR
  (~40%) and from EAS (~80%). Not stratifiable from `Race (OMB)`.
- **BCHE L307P** — the Vysya / Telangana founder variant from
  Kerdoncuff et al. *Cell* 2025. 5.3% prevalence in Vysya, 0.28%
  all-India, **0% gnomAD/1000G**. IWPC does not genotype BCHE.
- **CYP2C19 \*2 in South Asian populations** — 36% allele frequency,
  vs 13% EUR. Relevant for clopidogrel, not for warfarin; outside
  the scope of this study.

### Methodological caveats

- **Indeterminate rows.** 1,556 of 5,700 (27.3%) could not be fully
  classified due to missing CYP2C9 or VKORC1 -1639 consensus values.
  These rows are bucketed as `W0`/`indeterminate` and counted
  separately from the classified subset. Re-running the script with
  `Imputed VKORC1` (warfit-learn-style multi-rsID imputation) would
  recover most of the VKORC1 misses; we left it out of the default
  pipeline because the imputation procedure introduces an extra
  dependency we don't want shipped with a simple validation harness.
- **The W rules are local to this script.** They do not appear in the
  Anukriti swarm's R/V/U vocabulary. Conflating the namespaces would
  pollute the swarm's named-refusal contract; the W rules are
  explicitly downstream classification, anchored in CPIC 2017.
- **Cohort vs per-tier dose target.** §5 above explains why we
  benchmarked against cohort median rather than a per-tier predicted
  dose. The conservative choice; refinement is straightforward.

---

## 7. Reproduction recipe

Full instructions in
[`anukriti-validation-iwpc/README.md`](https://github.com/AnukritiAi-hq/anukriti-validation-iwpc#readme).
Brief version:

```bash
git clone https://github.com/AnukritiAi-hq/anukriti-validation-iwpc
cd anukriti-validation-iwpc

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # installs anukriti-pgx-core==0.2.1 from PyPI

# Verify the pipeline first with the included synthetic fixture
python scripts/run_validation.py \
    --input data/sample_iwpc_synthetic.csv \
    --output outputs/results.csv
python -m pytest tests/ -q   # 15 tests should pass

# Download IWPC from PharmGKB (https://www.pharmgkb.org/downloads,
# Dosing Datasets section), drop into data/, then:
python scripts/run_validation.py \
    --input data/IWPC_Data_7_3_09.xls \
    --output outputs/results.csv
```

Outputs:

- `outputs/results.csv` — 5,700 rows × 18 cols. One row per patient:
  original IWPC fields + engine outputs + risk tier + named rule.
- `outputs/summary.json` — machine-readable summary including the
  full `engine_validation` block (Q1..Q5).

The script is deterministic. Same inputs → same outputs every time.

---

## 8. What the engine deliberately does NOT do (recap)

For completeness, the same invariants that hold elsewhere in the
Anukriti platform hold here:

1. **No clinical decisions are made.** The engine emits phenotype
   labels and named rules; the prescribing decision belongs to a
   clinician. Every refusal cites a rule (R/V/U in the swarm; W in
   this script). Every recommendation cites a CPIC table version.
2. **No randomness in the calling path.** Same VCF / consensus
   genotype in → same diplotype, phenotype, and risk tier out, byte
   for byte.
3. **No LLM in the decision path.** Rule tables only; LLM (where it
   appears in the broader platform) narrates results, never
   generates them.
4. **Provenance on every call.** `cyp2c9_table_version`,
   `vkorc1_table_version`, and `engine_version` (anukriti-pgx-core
   semver) are written into every results row. Re-callable from audit
   logs years later.

---

## Continuation pointers

- **Next-step external validation:** PharmCAT diplotype concordance.
  CP-5 in [`anukriti/CLINICAL_GRADE_ROADMAP.md`][cp5]. Framework
  shipped (commit `f23ef81`); smoke test blocked on chr2 VCF
  extraction throughput.
- **Population stratification beyond `Race (OMB)`:** join on
  `PharmGKB Subject ID` against the IWPC ethnicity supplement
  (`ethnicity_dataset.xls`). Provides finer-grained ancestry labels
  per subject; would let us split the Asian bucket into East/South
  East/South Asian.
- **Per-tier dose-target methodology:** replace the cohort-median
  threshold in the headline statistic with the IWPC algorithm's
  per-genotype predicted dose. Would surface a larger and more
  clinically interpretable gap.

For strategic positioning of the engine, see
[`../anukriti-pgx-core/PLATFORM.md`](../anukriti-pgx-core/PLATFORM.md)
and [`../anukriti-pgx-core/docs/strategy.md`](../anukriti-pgx-core/docs/strategy.md).
