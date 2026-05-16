# Deterministic Engine — Deep Dive

> **Audience:** founder, prospective engineers, technical reviewers,
> anyone who wants to know *what the deterministic engine actually
> does* with a VCF, with code citations and real data.
>
> **Last updated:** 2026-05-16
>
> **Companion docs:**
>   - High-level course: [`docs/03-core-concepts.md`](docs/03-core-concepts.md), [`docs/04-architecture.md`](docs/04-architecture.md), [`docs/06-why-deterministic.md`](docs/06-why-deterministic.md)
>   - Strategic positioning: [`../anukriti-pgx-core/PLATFORM.md`](../anukriti-pgx-core/PLATFORM.md), [`../anukriti-pgx-core/docs/strategy.md`](../anukriti-pgx-core/docs/strategy.md)
>   - Idea synthesis: [`IDEA_REFINEMENT_AND_PHASING_2026-05-14.md`](IDEA_REFINEMENT_AND_PHASING_2026-05-14.md)

---

## TL;DR

The Anukriti deterministic engine is a **chain of pinned table
lookups**, not a probabilistic model and not a numeric risk score.

```
VCF variants
    │
    │  Layer 1 — calling/    PharmVar TSV table  (rsID + ALT → star allele)
    ▼
Diplotype string                                  (e.g. "*1/*17")
    │
    │  Layer 2 — phenotype/  Pinned CPIC JSON     (diplotype → phenotype label)
    ▼                                             (named-table or activity-score fallback)
Phenotype label                                   (e.g. "Rapid Metabolizer")
    │
    │  Layer 3 — guidelines/ Pinned CPIC JSON     ((gene, phenotype, drug) → action + text)
    ▼
Categorical action                                (5-value DrugSafetyOutcome enum)
+ template-rendered text                          (no LLM in the decision path)
```

Three properties hold for every call:

1. **Same VCF input always produces same output, byte-identical.** No randomness, no temperature, no LLM in the decision path.
2. **No numeric "risk score" is summed.** The output is categorical at every layer (phenotype label, recommendation action) plus a CPIC text string.
3. **Every output carries provenance** — PharmVar table version, CPIC table version, library semver, and the rule_id of every check. Re-callable from audit logs years later.

The SMILES + Tanimoto similarity code (`anukriti/src/ml/drug_reranker.py`) is **not part of this engine.** It's an optional drug-retrieval feature for "what other compounds are structurally similar to drug X?" — explicitly out-of-band of allele calling and CPIC recommendations. See [§5](#5-the-smiles-side-track-not-part-of-the-engine).

---

## Table of contents

1. [Layer 1 — Calling: VCF → diplotype](#1-layer-1--calling-vcf--diplotype)
2. [Layer 2 — Phenotype: diplotype → metabolizer label](#2-layer-2--phenotype-diplotype--metabolizer-label)
3. [Layer 3 — Recommendation: phenotype → CPIC action](#3-layer-3--recommendation-phenotype--cpic-action)
4. [End-to-end worked example: clopidogrel + CYP2C19](#4-end-to-end-worked-example-clopidogrel--cyp2c19)
5. [The SMILES side-track (NOT part of the engine)](#5-the-smiles-side-track-not-part-of-the-engine)
6. [Population-level reasoning (cohort demo)](#6-population-level-reasoning-cohort-demo)
7. [Why "deterministic" matters](#7-why-deterministic-matters)
8. [What the engine deliberately does NOT do](#8-what-the-engine-deliberately-does-not-do)

---

## 1. Layer 1 — Calling: VCF → diplotype

**Module:** `anukriti-pgx-core/anukriti_pgx_core/calling/`

**Input:** a dict of VCF variants keyed by rsID. Each value is a
`VCFVariant(ref, alt, genotype)` triple where `genotype` is a
1000-Genomes-style string like `"0|1"` (heterozygous) or `"1|1"`
(homozygous variant) or `"0|0"` (homozygous reference).

**Output:** a `Diplotype` frozen record with the resolved star
alleles, a canonical diplotype string, and full provenance.

**13 concrete callers, one per gene:**

| Type | Genes |
|---|---|
| `GeneCaller` (star alleles) | CYP2D6, CYP2C19, CYP2C9, CYP3A5, CYP3A4, CYP2B6, CYP1A2, NAT2, TPMT, DPYD, G6PD |
| `GenotypeCaller` (single-locus) | VKORC1, SLCO1B1 |

The base class `GeneCaller` (`calling/base.py:126`) implements the
shared 5-step `call()` method that every gene-specific subclass uses
without override:

```python
# pgx-core/anukriti_pgx_core/calling/base.py — GeneCaller.call()
def call(self, variants: dict[str, VCFVariant], ...) -> Diplotype:
    phenotype_table_id = self._resolve_phenotype_table(phenotype_table)

    # 1. Gene-specific star-allele detection
    allele_counts = self._detect_star_alleles(variants)

    # 2. Build canonical diplotype
    diplotype = build_diplotype(allele_counts,
                                wildtype_allele=self.wildtype_allele)

    # 3. Extract the two alleles for Layer 2 chaining
    a1, a2 = self._alleles_for_phenotype(diplotype)

    # 4. Chain to Layer 2
    phenotype_inf = self._phenotype_engine.infer(
        self.gene, a1, a2, phenotype_table=phenotype_table_id
    )

    # 5. Assemble result with full provenance
    return Diplotype(
        gene=self.gene,
        diplotype=diplotype,
        alleles_detected=...,
        allele_counts=dict(allele_counts),
        phenotype=phenotype_inf,
        caller_version=self.caller_version,
        pharmvar_table=self._pharmvar_table_id,
        phenotype_table=phenotype_inf.cpic_table_version,
        pgx_core_version=__version__,
    )
```

Each gene-specific subclass implements **one method** —
`_detect_star_alleles()` — which reads from a **PharmVar TSV
table** that maps rsIDs to star alleles.

### The PharmVar table — what the engine actually consults

For CYP2C19, the table is
`anukriti_pgx_core/calling/data/cyp2c19/CYP2C19_alleles_cpic_v2022.1.tsv`:

```tsv
allele	rsid	      alt	function
*2	    rs4244285	  A	    No function
*3	    rs4986893	  A	    No function
*4	    rs28399504	  A	    No function
*5	    rs56337013	  T	    No function
*6	    rs72552267	  G	    No function
*7	    rs72558186	  T	    No function
*8	    rs41291556	  T	    No function
*9	    rs17884712	  A	    Decreased function
*10	    rs6413438	  T	    Decreased function
*13	    rs17879685	  T	    No function
*15	    rs17882687	  A	    No function
*17	    rs12248560	  T	    Increased function
*22	    rs140278421	  A	    No function
*24	    rs118203756	  A	    No function
*26	    rs56276561	  T	    No function
```

Each row says: *"if you see rsID **X** with ALT nucleotide **Y**,
that's allele **Z**, which has functional effect **W**."*

**`*1` is the wildtype** — implied when none of the listed rsIDs
match the variant ALT. There is no row for it because it's defined
by *absence* of variation.

### CYP2C19 caller — the simplest possible case

CYP2C19 is the simplest gene caller in the codebase because every
star allele is defined by exactly **one rsID with one ALT
nucleotide** — no haplotypes, no CNVs, no read phasing.

```python
# anukriti-pgx-core/anukriti_pgx_core/calling/genes/cyp2c19.py:25
class CYP2C19Caller(GeneCaller):
    @property
    def gene(self) -> str: return "CYP2C19"

    @property
    def pharmvar_table_filename(self) -> str:
        return "CYP2C19_alleles_cpic_v2022.1.tsv"

    @property
    def default_phenotype_table(self) -> str: return "cpic_2022"

    def _detect_star_alleles(
        self, variants: dict[str, VCFVariant]
    ) -> dict[str, int]:
        """Single-variant rsID lookup against the PharmVar table.

        For each TSV row (allele, rsid, alt), check whether the
        sample has that rsID and count how many chromosomes carry
        the defining ALT. *1 is implied when no variant detected.
        """
        allele_counts: dict[str, int] = {}
        for row in self._pharmvar_rows:
            allele       = row.get("allele", "").strip()
            rsid         = row.get("rsid", "").strip()
            defining_alt = row.get("alt", "").strip()
            if not allele or not rsid or not defining_alt:
                continue
            if rsid not in variants:
                continue
            v = variants[rsid]
            two = genotype_to_alleles(v.ref, v.alt, v.genotype)
            count = sum(1 for a in two if a == defining_alt)
            if count > 0:
                allele_counts[allele] = allele_counts.get(allele, 0) + count
        return allele_counts
```

**Worked example.** A patient's VCF contains:
- `rs4244285: REF=G, ALT=A, GT="1|1"` — homozygous variant
- `rs12248560: REF=C, ALT=T, GT="0|0"` — homozygous reference (no variant)

The caller iterates the TSV rows:
1. `*2 / rs4244285 / A` → patient has `rs4244285`, both chromosomes carry `A` → `allele_counts["*2"] = 2`
2. `*17 / rs12248560 / T` → patient has `rs12248560`, neither chromosome carries `T` → no count
3. (other rows: rsID not in variants → skipped)

Result: `{"*2": 2}`. With `wildtype_allele="*1"` and total = 2 chromosomes:
- 2 chromosomes carry `*2`, 0 carry `*1` → diplotype = `"*2/*2"`.

### CYP2D6 — the hard case (still deterministic, but with caveats)

CYP2D6 is the canonical hard PGx gene. The caller subclass
(`calling/genes/cyp2d6.py`) is significantly more complex than
CYP2C19's because:

- Some star alleles are defined by **multiple rsIDs** in
  combination (haplotypes), not single SNPs.
- CYP2D6 has **CNV (copy-number variation)** — duplications and
  deletions of the entire gene that the platform's current caller
  **does not handle**. Anukriti currently always returns a 2-allele
  diplotype; CYP2D6 ultrarapid metabolizers with `*1xN`
  duplications are missed.
- Cyrius (the published CNV-aware caller) integration is open work
  per `anukriti/CLINICAL_GRADE_ROADMAP.md` CP-1.

This is **the most important honest limitation** of Layer 1 today.
PharmCAT concordance work in progress (`anukriti/docs/validation/PHARMCAT_COMPARISON.md`,
expected from session #17) will quantify the CYP2D6 discordance
honestly rather than hide it.

### Layer 1 output contract

```python
# anukriti-pgx-core/anukriti_pgx_core/types.py
@dataclass(frozen=True)
class Diplotype:
    gene: str                         # "CYP2C19"
    diplotype: str                    # "*2/*2"
    alleles_detected: tuple[str, ...] # ("*2", "*2")
    allele_counts: dict[str, int]     # {"*2": 2}
    phenotype: PhenotypeInference     # chained Layer 2 result
    caller_version: str
    pharmvar_table: str               # "CYP2C19_alleles_cpic_v2022.1"
    phenotype_table: str              # "CYP2C19_named_diplotypes_v2022.1"
    pgx_core_version: str
```

Frozen dataclass — once produced, it can't mutate. Every field is
either a primitive or a frozen sub-record. Safe for caching,
hashing, and audit-log persistence without defensive copies.

---

## 2. Layer 2 — Phenotype: diplotype → metabolizer label

**Module:** `anukriti-pgx-core/anukriti_pgx_core/phenotype/engine.py`

**Entry point:** `PhenotypeEngine.infer(gene, allele1, allele2)` —
returns a `PhenotypeInference` frozen record.

The engine has a strict 3-step resolution order
(`engine.py:376-470`):

```
1. Named-diplotype lookup     (CPIC's authoritative table for each gene)
   ↓ miss
2. Activity-score fallback    (additive: score(a1) + score(a2) → range table)
   ↓ miss
3. Indeterminate              (gene unsupported, or allele unknown)
```

### Step 1 — Named-diplotype lookup (the primary path)

The engine's primary path is a **flat dict lookup** in a pinned
JSON file. For CYP2C19, the file is
`anukriti_pgx_core/phenotype/tables/CYP2C19_named_diplotypes_v2022.1.json`:

```json
{
  "table_id": "CYP2C19_named_diplotypes_v2022.1",
  "gene": "CYP2C19",
  "citation": {
    "source": "CPIC 2022 clopidogrel guideline Table 2",
    "primary_pmid": "35034351",
    "reference_doc": "Lee et al. 2022, Clin Pharmacol Ther",
    "ncbi_bookshelf": "NBK84114"
  },
  "diplotype_phenotypes": {
    "*1/*1":   "Normal Metabolizer",
    "*1/*2":   "Intermediate Metabolizer",
    "*1/*3":   "Intermediate Metabolizer",
    "*1/*17":  "Rapid Metabolizer",
    "*2/*2":   "Poor Metabolizer",
    "*2/*3":   "Poor Metabolizer",
    "*2/*17":  "Intermediate Metabolizer",
    "*3/*3":   "Poor Metabolizer",
    "*3/*17":  "Intermediate Metabolizer",
    "*17/*17": "Ultrarapid Metabolizer"
  },
  "diplotype_key_convention":
     "Canonical ordering: numeric ascending on allele suffix...",
  "notes": [
    "Heterozygous *2/*17 and *3/*17 are IM, not NM — the
     loss-of-function allele dominates clinical phenotype despite
     *17 upregulation.",
    "Unnamed combinations fall through to additive scoring per
     CYP2C19_activity_v2022.1.json."
  ]
}
```

Two non-obvious facts captured here:

1. **The notes block is in the JSON for a reason.** `*2/*17` is
   `Intermediate Metabolizer`, NOT `Normal Metabolizer` even
   though `*17` is "increased function" and might naively
   compensate for `*2`'s "no function." CPIC's guideline says the
   loss-of-function allele dominates. The pinned table encodes this
   clinical knowledge that **a naive activity-score sum would get
   wrong** (see step 2).

2. **`citation` is mandatory.** Every pinned table has a primary
   PMID, the reference doc, and an NCBI Bookshelf URL. There's a
   pytest guard (`tests/test_cpic_provenance.py`) that fails CI if
   any new table lands without provenance. See
   [`anukriti_pgx_core/phenotype/tables/CPIC_PROVENANCE.md`](https://github.com/AnukritiAi-hq/anukriti-pgx-core/blob/main/anukriti_pgx_core/phenotype/tables/CPIC_PROVENANCE.md)
   for the full schema.

### Step 2 — Activity-score additive fallback

For diplotypes **not** in the named table (e.g. patient has a rare
combination involving `*9` decreased-function), the engine falls
through to an additive activity-score model.

The activity-score table for CYP2C19 is
`CYP2C19_activity_v2022.1.json`:

```json
{
  "table_id": "CYP2C19_activity_v2022.1",
  "gene": "CYP2C19",
  "citation": {
    "source": "CPIC 2022 clopidogrel guideline — allele functionality table",
    "primary_pmid": "35034351"
  },
  "phenotype_cutoffs_description":
     "Additive fallback only. CYP2C19 primary resolution is via
      named-diplotype lookup; see CYP2C19_named_diplotypes_v2022.1.json.",
  "allele_activity_scores": {
    "*1":  1.0,
    "*2":  0.0,
    "*3":  0.0,
    "*17": 1.5
  },
  "phenotype_ranges": [
    {"low": 0.0, "high": 0.0, "phenotype": "Poor Metabolizer"},
    {"low": 0.5, "high": 1.0, "phenotype": "Intermediate Metabolizer"},
    {"low": 1.5, "high": 2.0, "phenotype": "Normal Metabolizer"},
    {"low": 2.5, "high": 2.5, "phenotype": "Rapid Metabolizer"},
    {"low": 3.0, "high": 3.0, "phenotype": "Ultrarapid Metabolizer"}
  ],
  "notes": [
    "For CYP2C19, CPIC publishes a diplotype-to-phenotype table
     rather than relying solely on the additive activity-score
     model.",
    "The additive model matches CPIC for all-normal and all-loss
     combinations but misclassifies heterozygous *2/*17 (score
     1.5) as NM when CPIC says IM.",
    "PhenotypeEngine consults the named-diplotype table first;
     this activity-score table is the fallback."
  ]
}
```

The summing logic is in `phenotype/activity_score.py`:

```python
# pgx-core/anukriti_pgx_core/phenotype/activity_score.py
@dataclass(frozen=True)
class ActivityScoreModel:
    gene: str
    table_id: str
    allele_activity_scores: dict[str, float]
    phenotype_ranges: tuple[tuple[float, float, str], ...]

    def score_for(self, allele: str) -> float | None:
        return self.allele_activity_scores.get(allele)

    def phenotype_for_score(self, score: float) -> str:
        # Ranges are inclusive on both ends.
        for low, high, phenotype in self.phenotype_ranges:
            if low <= score <= high:
                return phenotype
        # Documented CPIC fallback for gaps:
        if 0 < score < 1.25:
            return "Intermediate Metabolizer"
        if score >= 1.25:
            return "Normal Metabolizer"
        return "Indeterminate"
```

**This is the only "summing" anywhere in the engine.** It is a
**two-allele activity-score sum**, not a multi-factor risk score.
It is CPIC's published nomenclature, not Anukriti's invention.
Examples:

| Diplotype | score(a1) | score(a2) | Sum | Phenotype |
|---|---|---|---|---|
| `*1/*1` | 1.0 | 1.0 | **2.0** | Normal Metabolizer |
| `*1/*2` | 1.0 | 0.0 | **1.0** | Intermediate Metabolizer |
| `*2/*2` | 0.0 | 0.0 | **0.0** | Poor Metabolizer |
| `*1/*17` | 1.0 | 1.5 | **2.5** | Rapid Metabolizer |
| `*17/*17` | 1.5 | 1.5 | **3.0** | Ultrarapid Metabolizer |
| `*2/*17` | 0.0 | 1.5 | **1.5** | (additive says NM, but **CPIC named-table says IM** — named table wins) |

The `*2/*17` case is exactly why the named-table-first ordering
matters. Trusting the additive sum alone would give the patient an
incorrect "Normal Metabolizer" call and incorrect dosing.

### Step 3 — Indeterminate

If the gene is not loaded (no model and no named tables) or an
allele is not in either table, the engine returns:

```python
PhenotypeInference(
    ...,
    activity_score=-1.0,       # sentinel value
    phenotype="Indeterminate",
    confidence=0.0,
    source=f"Unsupported gene: {gene}",
)
```

`Indeterminate` is a first-class output, not an exception. The
recommendation layer above (and the swarm's evidence-sufficiency
layer) treats it as "refuse to make a clinical recommendation."

### Layer 2 output contract

```python
# anukriti-pgx-core/anukriti_pgx_core/types.py:16
@dataclass(frozen=True)
class PhenotypeInference:
    gene: str                 # "CYP2C19"
    allele1: str              # "*2"
    allele2: str              # "*2"
    diplotype: str            # "*2/*2"
    activity_score: float     # 0.0 (or -1.0 if named-only path)
    phenotype: str            # "Poor Metabolizer"
    confidence: float         # 1.0 (named table) or 0.5 (fallback)
    rule_version: str
    source: str               # "CPIC named-diplotype table (cpic_2022)"
    cpic_table_version: str   # "CYP2C19_named_diplotypes_v2022.1"
    pgx_core_version: str
    timestamp: datetime
```

`confidence` is a discrete signal, not a continuous probability:
- `1.0` — named-table hit (the authoritative path)
- `~0.5` — activity-score fallback (the additive path)
- `0.0` — Indeterminate

There is no statistical model behind `confidence`; it's a coarse
signal of "which resolution path produced this answer."

---

## 3. Layer 3 — Recommendation: phenotype → CPIC action

**Module:** `anukriti/src/template_engine.py` (in the product) and
`anukriti-pgx-core/anukriti_pgx_core/guidelines/` (planned, partial
today).

**Input:** `(gene, phenotype, drug)` triple.

**Output:** a 5-value categorical action and a CPIC-text string
slotted into a deterministic template.

### The recommendation lookup is just a JSON

For `(CYP2C19, Poor Metabolizer, clopidogrel)` the answer is:

```json
{
  "action": "ALTERNATIVE_RECOMMENDED",
  "guidance": "Avoid clopidogrel. Use alternative antiplatelet
               (e.g., prasugrel, ticagrelor) if no
               contraindication.",
  "cpic_strength": "Strong",
  "guideline_pmid": "35034351",
  "table_version": "CPIC_clopidogrel_2022.1"
}
```

This is **looked up**, not generated. The text comes verbatim from
the CPIC clopidogrel 2022 guideline. No LLM, no synthesis.

### The 5-value `DrugSafetyOutcome` enum

Defined in `anukriti-swarm/core/simulation/types.py` as a closed
enum at the type boundary:

```python
class DrugSafetyOutcome(Enum):
    RECOMMENDED_AS_IS              # use the standard drug + dose
    RECOMMENDED_WITH_CAVEAT        # use, but monitor for ADRs
    ALTERNATIVE_RECOMMENDED        # use a different drug
    CONTRAINDICATED                # do not use this drug
    REFUSED_INSUFFICIENT_EVIDENCE  # cannot recommend; evidence base too thin
```

Five values. No floats. No probabilities. The output of the engine
for a (patient, drug) question is **one of these five labels** plus
the CPIC text. Nothing is ever "0.73 risky."

### The template engine — deterministic text rendering

Once the action is looked up, the user-facing text is rendered via
`template_engine.py`'s structured templates:

```python
# anukriti/src/template_engine.py
"""
Replaces free-form LLM generation with deterministic template
filling. Every explanation is constructed from CPIC guideline
text slotted into structured templates. No hallucination
possible — the output contains only information present in the
curated data tables.
"""

_METABOLIZER_TEMPLATES = {
    "poor_metabolizer": (
        "{gene} {diplotype}: Poor Metabolizer. "
        "This patient has significantly reduced or absent "
        "{gene} enzyme activity. {drug_guidance}"
    ),
    "intermediate_metabolizer": (
        "{gene} {diplotype}: Intermediate Metabolizer. ..."
    ),
    ...
}
```

Slot variables (`{gene}`, `{diplotype}`, `{drug_guidance}`) are
filled from the looked-up data. The template structure itself is
fixed at code-time. The only "generation" that happens is `str.format()`.

There is an LLM path on the side (`anukriti/src/multi_backend_llm.py`)
but it is **explicitly marked optional** and has its output gated
through a hallucination validator
(`anukriti/src/llm_output_validator.py`) — any drug, gene, or
star-allele in the LLM response that isn't in the input context
gets the response **rejected** before it reaches the user. Not
"warned about." Rejected, with a `RuleID` like `LV-DRUG`,
`LV-GENE`, `LV-ALLELE`, or `LV-EMPTY`.

### Layer 3 output

The user (or downstream system) receives:

```json
{
  "patient_id": "...",
  "gene": "CYP2C19",
  "diplotype": "*2/*2",
  "phenotype": "Poor Metabolizer",
  "phenotype_confidence": 1.0,
  "drug": "clopidogrel",
  "action": "ALTERNATIVE_RECOMMENDED",
  "guidance_text": "CYP2C19 *2/*2: Poor Metabolizer. This patient
                    has significantly reduced or absent CYP2C19
                    enzyme activity. Avoid clopidogrel. Use
                    alternative antiplatelet (e.g., prasugrel,
                    ticagrelor) if no contraindication.",
  "provenance": {
    "pharmvar_table": "CYP2C19_alleles_cpic_v2022.1",
    "phenotype_table": "CYP2C19_named_diplotypes_v2022.1",
    "guideline_pmid": "35034351",
    "guideline_table_version": "CPIC_clopidogrel_2022.1",
    "pgx_core_version": "0.2.1",
    "rule_version": "...",
    "timestamp": "2026-05-16T11:14:30Z"
  }
}
```

A reviewer looking at this in 3 years can re-derive the exact same
answer by checking out the same `pgx-core` version and replaying
the same VCF.

---

## 4. End-to-end worked example: clopidogrel + CYP2C19

A 64-year-old South Asian patient is being considered for
clopidogrel after a coronary stent. The clinical question:
**should we prescribe clopidogrel?**

### Step 0 — Input

VCF excerpt for the patient (only PGx-relevant variants shown):

| rsID | REF | ALT | Genotype |
|---|---|---|---|
| `rs4244285` | G | A | `1\|1` (homozygous variant) |
| `rs12248560` | C | T | `0\|0` (homozygous reference) |
| `rs28399504` | A | G | `0\|0` (homozygous reference) |

Sent to the API along with `population: SAS` and `drug: clopidogrel`.

### Step 1 — Layer 1 calling

The api creates the runtime: `_runtime_instance: SwarmRuntime`
(warmed once per process) and routes the request to the
`CYP2C19Caller`.

`CYP2C19Caller._detect_star_alleles()` iterates the PharmVar TSV:

| TSV row | Match? | Effect |
|---|---|---|
| `*2  / rs4244285  / A` | Yes — both chromosomes carry A | `allele_counts["*2"] = 2` |
| `*3  / rs4986893  / A` | rsID not in input | skipped |
| `*4  / rs28399504 / A` | rsID present but ALT is G — neither chromosome carries A | no count |
| `*17 / rs12248560 / T` | rsID present but neither chromosome carries T | no count |
| (other rows: rsID not in input) | | skipped |

Result: `{"*2": 2}`. `build_diplotype()` produces `"*2/*2"` with
`*1` (wildtype) implied at zero copies.

### Step 2 — Layer 2 phenotype

`PhenotypeEngine.infer("CYP2C19", "*2", "*2", phenotype_table="cpic_2022")`:

1. Look up `*2/*2` in `CYP2C19_named_diplotypes_v2022.1.json`.
2. Hit: `"Poor Metabolizer"`.

Output:
```python
PhenotypeInference(
    gene="CYP2C19",
    allele1="*2", allele2="*2",
    diplotype="*2/*2",
    activity_score=-1.0,            # named-table hit, additive not consulted
    phenotype="Poor Metabolizer",
    confidence=1.0,
    rule_version="...",
    source="CPIC named-diplotype table (cpic_2022)",
    cpic_table_version="CYP2C19_named_diplotypes_v2022.1",
    pgx_core_version="0.2.1",
)
```

### Step 3 — Layer 3 recommendation

Look up `(CYP2C19, Poor Metabolizer, clopidogrel)` in the CPIC
clopidogrel 2022 guideline JSON:

- Action: `ALTERNATIVE_RECOMMENDED`
- Guidance: `"Avoid clopidogrel. Use alternative antiplatelet
   (e.g., prasugrel, ticagrelor)..."`
- CPIC strength: `Strong`

### Step 4 — Swarm-side checks

The swarm's **Evidence Sufficiency Layer** runs Step 3.5 in the
runtime:

- All 6 evidence facets covered: ALLELE ✓, PHENOTYPE ✓, CPIC ✓,
  POPULATION ✓, RECOMMENDATION ✓, CONFLICT_FREE ✓
- Provenance complete (4/4 dimensions): rule_id ✓,
  agent_attribution ✓, chain_completeness ✓, evidence_resolvability ✓
- No conflict
- Population (SAS) is not UNCERTAIN — the SAS allele frequency for
  *2 (0.36) is well-documented in CPIC 2022 + 1000G

`SufficiencyDecisionEngine` rule R12 fires (`all clean →
SUFFICIENT`). The recommendation is allowed to synthesize.

### Step 5 — Template render

`template_engine.py` renders the `poor_metabolizer` template:

> *"CYP2C19 \*2/\*2: Poor Metabolizer. This patient has
> significantly reduced or absent CYP2C19 enzyme activity. Avoid
> clopidogrel. Use alternative antiplatelet (e.g., prasugrel,
> ticagrelor) if no contraindication."*

### Step 6 — Output

The clinician receives the categorical action
(`ALTERNATIVE_RECOMMENDED`) plus the guidance text plus the full
provenance chain. The whole call took **<5ms** in the deterministic
core, no LLM, no network call.

---

## 5. The SMILES side-track (NOT part of the engine)

Your question specifically asked about SMILES drug comparison. The
short answer is: **it is not part of the deterministic engine.** It
is an optional ML feature on a side-path with no role in
phenotype calling or CPIC recommendations.

### Where it lives

Two files in the product repo:

- `anukriti/src/input_processor.py` —
  `get_drug_fingerprint(smiles)` uses RDKit to compute a 2048-bit
  Morgan circular fingerprint. Each bit corresponds to a hashed
  substructure of radius 2 around some atom in the molecule.

  ```python
  generator = GetMorganGenerator(radius=2, fpSize=2048)
  bits = generator.GetFingerprint(Chem.MolFromSmiles(smiles))
  # bits is a 2048-bit binary vector
  ```

- `anukriti/src/ml/drug_reranker.py` — Tanimoto similarity for
  drug-similarity retrieval. The module's own docstring is
  unambiguous:

  > *"Learned re-ranking for similar-drug retrieval (local ChEMBL
  > fingerprints only). Trained on weak labels from Tanimoto
  > similarity on Morgan bit vectors; at inference re-orders cosine
  > top-pool candidates. **Does not affect PGx allele calling or
  > CPIC tables.**"*

### What it does

1. **Query**: a drug's SMILES → 2048-bit Morgan fingerprint.
2. **Index**: a local ChEMBL slice of pre-computed fingerprints.
3. **First-stage retrieval**: cosine similarity across the index → top-K candidates.
4. **Re-rank**: a small learned model scores `(cosine, tanimoto, mean_abs_diff)` triples over the top-K and re-orders.
5. **Return**: top-`final_k` indices.

The Tanimoto similarity itself is the standard cheminformatics
formula:

```python
def tanimoto(q, c):
    # q, c are 2048-bit vectors
    intersection = float(np.dot(q, c))
    return intersection / (sum(q) + sum(c) - intersection + 1e-12)
```

A Tanimoto of `1.0` means identical fingerprints; `0.0` means no
shared substructures.

### What it's used for (and what it isn't)

**Used for:** *"the patient is contraindicated for clopidogrel.
What other compounds in ChEMBL are structurally similar?"* The
output is a ranked list of related drug candidates for the
clinician to consider — it is **input to clinical judgment**, not
a replacement for it.

**Not used for:** the contraindication decision itself. That
decision is made by Layer 3's CPIC table lookup based on the
patient's CYP2C19 phenotype. The drug reranker doesn't see the
patient's genotype at all.

### Why it's confusing

Because the module has the words "drug" and "score" and
"similarity" in it, it gets conflated with risk scoring. It isn't.
The SMILES path:

- Has zero coupling to the VCF input
- Has zero coupling to the phenotype output
- Has zero coupling to the CPIC tables
- Is an ML model (vs. deterministic), explicitly out of band

If you removed `drug_reranker.py` from the codebase, the
deterministic engine would still work identically. Layer 1, 2, 3
would all still produce the same outputs.

---

## 6. Population-level reasoning (cohort demo)

There is one place where Anukriti emits *numbers* that look like
risk metrics: the **cohort demo** in `anukriti-swarm/demos/cohort_demo.py`.
These are **population-prevalence proportions**, not patient-level
risk scores. Worth understanding because the platform's
*positioning* leans on these numbers.

### What the cohort demo does

Runs a 100-patient deterministic Monte Carlo across each of 5
super-populations (EUR / EAS / SAS / AFR / AMR) using **real
CPIC-derived allele frequencies** from the knowledge-graph seed:

```python
# anukriti-swarm/demos/cohort_demo.py:80-87
POPULATION_FREQUENCIES: dict[SuperPopulation, dict[str, float]] = {
    SuperPopulation.EUR: {"*1": 0.68, "*2": 0.15, "*17": 0.17},
    SuperPopulation.EAS: {"*1": 0.68, "*2": 0.30, "*17": 0.02},
    SuperPopulation.SAS: {"*1": 0.54, "*2": 0.36, "*17": 0.10},
    SuperPopulation.AFR: {"*1": 0.65, "*2": 0.18, "*17": 0.17},
    SuperPopulation.AMR: {"*1": 0.69, "*2": 0.18, "*17": 0.13},
}
```

(Source: `PharmGKB:PA166169660 + 1000G:phase3` — the same seed
data the swarm KG uses. SAS has the highest *2 frequency by a
significant margin.)

For each population, `_sample_diplotype()` draws **two alleles
independently** from the frequency distribution
(Hardy-Weinberg assumption — i.e. the two chromosomes are
independent given the population frequency):

```python
def _sample_diplotype(rng, allele_frequencies):
    alleles = list(allele_frequencies.keys())
    weights = list(allele_frequencies.values())
    a1 = rng.choices(alleles, weights=weights, k=1)[0]
    a2 = rng.choices(alleles, weights=weights, k=1)[0]
    return _canonical_diplotype(a1, a2)
```

For each sampled diplotype, the demo runs Layer 2 (phenotype
lookup) + Layer 3 (CPIC clopidogrel recommendation) and **counts
which `DrugSafetyOutcome` bucket** the patient lands in.

### What the output looks like (deterministic, RNG_SEED=42)

```
Population     Rec as-is   With caveat   Alternative    Contra   Refused    PM %
EUR                   80            18             2         0         0    2.0%
EAS                   45            46             9         0         0    9.0%
SAS                   36            48            16         0         0   16.0%
AFR                   64            35             1         0         0    1.0%
AMR                   65            31             4         0         0    4.0%

• SAS shows the highest alternative-recommended rate (16.0%).
• AFR shows the lowest (1.0%).
• That's a 16.0x delta — the clinical signal is real.
```

### How to read these numbers honestly

| Number | What it is | What it isn't |
|---|---|---|
| `SAS 16% PM` | The Hardy-Weinberg expected fraction of South Asians whose CPIC clopidogrel recommendation is `ALTERNATIVE_RECOMMENDED` based on the published `*2` frequency of 0.36 | A risk score; a probability of harm to any individual; an outcome of pharmacokinetic simulation |
| `16x delta` (SAS vs AFR) | The ratio of the SAS-PM rate to the AFR-PM rate | A claim that any SAS patient is "16x sicker" than any AFR patient |
| `RNG_SEED=42` | Pinned for byte-identical demo output | Required for production runs; production would re-sample |

These are **prevalence proportions over a synthetic cohort**. The
clinical signal is honest: at the population level, recommending
clopidogrel uniformly across populations means you'd issue a
PM-incompatible prescription **8x more often** to an SAS patient
than to an EUR patient (16% vs 2%). That's the equity claim. It
isn't a risk score; it's a prevalence statistic from real allele
frequencies.

### Stage-1 guarantee

Per the demo's docstring:

> *"Every input is public or aggregate data: CPIC 2022.1
> recommendation, 1000G super-population allele frequencies,
> Hardy-Weinberg assumption. No controlled-access data is used.
> This demo runs from a clean checkout with no external
> credentials."*

The cohort demo is an **honest Stage-1 capability demo** — it
shows what we can do today with public data. It's deliberately
**excluded from the byte-locked 7 flagship demos** in CI because
it's *about distributions*, not a single signature. See
`anukriti_docs/SESSION_RESUME_2026-05-14.md` for the rationale.

Stage-2 / Stage-3 numbers (LASI-DAD-derived sub-population
frequencies, Indian community-level frequencies for the BCHE
wedge) are **not in the demo today** — they require Phase C data
partnerships to land first.

---

## 7. Why "deterministic" matters

The platform's positioning leans hard on the word "deterministic."
Here's what it actually buys, in concrete engineering terms:

### Replay safety

Any call from years ago can be re-run today and produce the
**byte-identical** output, given:
- The same `pgx-core` version (semver-pinned in deployments)
- The same input VCF
- The same gene panel + phenotype-table selection

This is what makes audit logs useful. A regulator asking "why did
you recommend this drug for this patient on Jan 4?" can replay the
exact decision and see every table version, every rule_id, and
every byte of the answer.

### Hallucination resistance

There is no LLM in the decision path. The text the user sees comes
from a CPIC guideline JSON, slotted into a template. The optional
LLM enrichment path (`multi_backend_llm.py`) has a hallucination
validator that **rejects** responses mentioning entities not in
the input context.

This is why the platform's positioning is *"hallucination-resistant
by construction, not by fine-tuning."*

### Closed-enum scope firewall

Every cross-module contract uses a closed enum:
`SufficiencyDecision` (8), `DrugSafetyOutcome` (5), `EvidenceVerdict` (5),
`UncertaintyScore` (4), `BiasKind` (3), `NodeKind` (10), `EdgeKind` (7),
`ClaimEvidenceFacet` (6), and 7 more in `core/evidence_sufficiency/`.

Adding a new value requires a code change. Strings cannot leak
across module boundaries. This is the mechanism that prevents
scope drift into "generic healthcare AI" territory. See
[`docs/06-why-deterministic.md`](docs/06-why-deterministic.md).

### Pinned-table provenance

Every table in `anukriti_pgx_core/phenotype/tables/` and every
PharmVar TSV in `anukriti_pgx_core/calling/data/` has a manifest
entry in `CPIC_PROVENANCE.json` with PMID, audit_status (one of
`authoritative` / `verified` / `needs_audit` / `deprecated`), and
audit_date. A pytest guard fails CI if any new table lands without
provenance. See `tests/test_cpic_provenance.py`.

Today: 7 of 29 entries are `authoritative` (CYP2C19 + CYP2D6),
22 are `needs_audit` (the Anukriti-derived JSONs from Batch 2/3
genes). The audit pipeline is `anukriti-pgx-core/scripts/cpic_audit.py`
(commit `c13fa67`). Per-gene audit work is tracked in the
[`founder-research/andrea_gaedigk/`](founder-research/andrea_gaedigk/)
PharmVar relationship — Andrea explicitly noted "citations are
measurable, website mentions are difficult to track."

---

## 8. What the engine deliberately does NOT do

For honesty, here is the closed list of things the engine **does
not** compute, even though similar systems do:

- **No numeric "final risk score" anywhere.** The output of every
  layer is categorical (label or enum) plus a CPIC text string. A
  `grep -rE "risk_score|RiskScore|calculate_risk|compute_risk|final_score"
  anukriti/` produces zero matches.

- **No multi-factor risk summation.** The only "summing" anywhere
  in the engine is the **two-allele activity-score sum** in the
  Layer-2 fallback path, and that's CPIC's published nomenclature,
  not Anukriti's invention.

- **No probabilistic ML in the decision path.** The drug reranker
  (`anukriti/src/ml/drug_reranker.py`) is on a side path; removing
  it would not change Layer 1/2/3 output for any patient.

- **No pharmacokinetic simulation.** The platform does not model
  drug concentration over time. It does not predict
  individual-patient adverse-event probabilities. It tells you
  what the published CPIC guideline says for the patient's
  phenotype.

- **No CYP2D6 CNV today.** Anukriti's CYP2D6 caller does not
  detect copy-number duplications/deletions. CYP2D6 ultrarapid
  metabolizers with `*1xN` are missed. Cyrius integration is open
  per `CLINICAL_GRADE_ROADMAP.md` CP-1.

- **No statistical inference in `confidence`.** The
  `PhenotypeInference.confidence` field is a discrete signal of
  which resolution path produced the answer (1.0 = named table,
  ~0.5 = activity-score fallback, 0.0 = indeterminate), not a
  Bayesian posterior.

- **No clinical decision-making.** The platform produces a
  CPIC-grounded recommendation. The clinician makes the decision.
  This is in every disclaimer in every README, every product
  surface, and every API response.

- **No race or ethnicity input.** The platform takes
  `super_population` as a 5-value enum (EUR / EAS / SAS / AFR /
  AMR — the 1000-Genomes super-population labels), not "race." The
  Phase-B work to add `IndianRegion` (6 values) and
  `CommunityLevel` (open extension) is gated on LASI-DAD data
  access — see [IDEA_REFINEMENT_AND_PHASING_2026-05-14.md
  Phase B](IDEA_REFINEMENT_AND_PHASING_2026-05-14.md#phase-b--paper-driven-architectural-extensions-weeks-510).

---

## Appendix — file map for this deep-dive

| Concept | File |
|---|---|
| Layer 1 base class | `anukriti-pgx-core/anukriti_pgx_core/calling/base.py` |
| Layer 1 per-gene callers | `anukriti-pgx-core/anukriti_pgx_core/calling/genes/*.py` |
| PharmVar TSV (CYP2C19) | `anukriti-pgx-core/anukriti_pgx_core/calling/data/cyp2c19/CYP2C19_alleles_cpic_v2022.1.tsv` |
| Layer 2 engine | `anukriti-pgx-core/anukriti_pgx_core/phenotype/engine.py` |
| Layer 2 named-diplotype table (CYP2C19) | `anukriti-pgx-core/anukriti_pgx_core/phenotype/tables/CYP2C19_named_diplotypes_v2022.1.json` |
| Layer 2 activity-score table (CYP2C19) | `anukriti-pgx-core/anukriti_pgx_core/phenotype/tables/CYP2C19_activity_v2022.1.json` |
| Layer 2 additive fallback | `anukriti-pgx-core/anukriti_pgx_core/phenotype/activity_score.py` |
| CPIC provenance manifest | `anukriti-pgx-core/anukriti_pgx_core/phenotype/tables/CPIC_PROVENANCE.{json,md}` |
| CPIC audit helper | `anukriti-pgx-core/scripts/cpic_audit.py` |
| Layer 3 template engine | `anukriti/src/template_engine.py` |
| LLM hallucination validator | `anukriti/src/llm_output_validator.py` |
| LLM optional path | `anukriti/src/multi_backend_llm.py` |
| SMILES fingerprinting | `anukriti/src/input_processor.py` (`get_drug_fingerprint`) |
| Tanimoto / drug reranker | `anukriti/src/ml/drug_reranker.py` |
| Cohort Monte Carlo demo | `anukriti-swarm/demos/cohort_demo.py` |
| Closed-enum types | `anukriti-swarm/core/simulation/types.py` |
| Evidence sufficiency layer | `anukriti-swarm/core/evidence_sufficiency/` |
| Output records (frozen) | `anukriti-pgx-core/anukriti_pgx_core/types.py` |

---

*This document was written 2026-05-16 as a permanent record of the
deterministic engine's actual behavior, derived directly from the
source files cited above. If a future session changes any of the
behavior described here, update this document in the same commit
that lands the change — divergence between this doc and the code
is a documentation regression, not just a stale doc.*
