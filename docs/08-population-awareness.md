# Module 08 — Population Awareness

> Prerequisites: [03 Core Concepts](03-core-concepts.md), [05 Gene Matching](05-gene-matching.md)

---

## The question we're answering

Why does the platform treat ancestry as a first-class reasoning
input? What does "population-aware" actually change in the code?
And when ancestry data is thin, how do we refuse honestly instead
of guessing?

---

## Why ancestry matters — the clinical argument

From Module 01: 14% of South Asians vs. 2% of Europeans are *CYP2C19
\*2/\*2* Poor Metabolizers. A global clinical guideline that doesn't
account for this will under-warn SAS patients and over-warn EUR
patients. That's the gap.

But there's a second reason population matters that's more subtle.
**Allele frequencies from one population don't predict a patient's
genotype.** If 36% of SAS individuals carry the *CYP2C19 \*2*
allele, that doesn't mean any given SAS patient is at risk — they
might be wildtype. **Population data sets the prior; the patient's
actual genotype sets the posterior.**

So the platform uses population in two distinct ways:

1. **As a population-risk lens** — "what fraction of this population
   has clinically actionable genotypes for this drug?" Relevant for
   trial stratification, public-health reasoning, resource
   allocation.
2. **As a context for the individual** — "given this patient's
   genotype AND their ancestry, what's the evidence density for
   making a claim?" Relevant for clinical recommendations.

Both uses depend on treating population as data, not metadata.

---

## Super-populations and the closed enum

From `anukriti-swarm/core/models/population.py`:

```python
class SuperPopulation(str, Enum):
    EUR = "EUR"  # European
    EAS = "EAS"  # East Asian
    SAS = "SAS"  # South Asian
    AFR = "AFR"  # African
    AMR = "AMR"  # Admixed American
```

Five super-populations, from 1000 Genomes / gnomAD. This is the
same closed-enum pattern from Module 06 — you can't pass
`"caucasian"` or `"latino"` or `"mixed"` at a module boundary.
Pydantic rejects.

Why such a small set? These are the super-populations with rich,
publicly curated allele-frequency data. Sub-populations (e.g.
SAS:GIH for Gujarati in Houston, AFR:YRI for Yoruba in Nigeria)
exist as future extension points in the knowledge graph, but
today's reasoning layer collapses to super-population.

---

## Population as a knowledge-graph node kind

Recall from Module 06: the knowledge graph has 10 closed
`NodeKind`s and 7 closed `EdgeKind`s. **`POPULATION` is one of
those node kinds.** It's not a property *of* other nodes — it's a
node in its own right.

The 10 node kinds from `knowledge_graph/schema.py`:

```python
class NodeKind(str, Enum):
    POPULATION = "population"          # ← first-class
    ANCESTRY = "ancestry"              # (sub-population, unused in seed)
    GENE = "gene"
    VARIANT = "variant"                # (rsID-level, unused in seed)
    ALLELE = "allele"
    PHENOTYPE = "phenotype"
    DRUG = "drug"
    ADVERSE_REACTION = "adverse_reaction"
    GUIDELINE = "guideline"
    EVIDENCE_PAPER = "evidence_paper"
```

And the 7 edge kinds:

```python
class EdgeKind(str, Enum):
    METABOLIZES = "metabolizes"
    CONTRAINDICATED_FOR = "contraindicated_for"
    ASSOCIATED_WITH = "associated_with"
    HIGHER_FREQUENCY_IN = "higher_frequency_in"   # ← population edge
    SUPPORTED_BY = "supported_by"
    CONFLICTS_WITH = "conflicts_with"
    GUIDELINE_RECOMMENDS = "guideline_recommends"
```

The `HIGHER_FREQUENCY_IN` edge is how allele-to-population
relationships are encoded. Each edge has a **weight** — the actual
frequency. So `CYP2C19 *2 --HIGHER_FREQUENCY_IN (weight=0.36)--> SAS`
is a real KG edge.

### The flagship signal: the *CYP2C19 \*2 → SAS* edge

From the seed data (`knowledge_graph/seed.py`):

| Edge | Weight |
|------|--------|
| CYP2C19 *2 → SAS | 0.36 |
| CYP2D6 *4 → EUR | 0.20 |
| CYP2D6 *17 → AFR | 0.20 |
| HLA-B *15:02 → EAS | 0.08 |

These aren't string tags. They're weighted edges that the
multi-hop reasoner traverses. When a query asks "does this
population have elevated risk for this gene-drug combination?" the
reasoner walks the graph: `population → HIGHER_FREQUENCY_IN edges
→ alleles → ASSOCIATED_WITH → phenotypes → CONTRAINDICATED_FOR →
drugs`.

---

## Population-aware retrieval

In `retrieval/multi_strategy/biomedical_retriever.py`:

```python
class PopulationAwareRetriever(BiomedicalRetriever):
    """
    Re-ranks retrieved documents by population relevance.
    Applies a signed boost — documents mentioning the target
    population score higher; documents mentioning a non-target
    population score lower.
    """
```

How it actually works:

1. A dense retriever does the first pass, returning candidate
   documents by TF-IDF similarity to the query.
2. The population-aware re-ranker reads each document's mentions
   of population anchors (`"south asian"`, `"SAS"`, `"EUR"`, etc.)
   using `core/models/population_mentions.py`.
3. Each document's score is adjusted: +boost if it mentions the
   target population, -boost if it mentions a different population,
   no change if population-agnostic.
4. Ranked list is returned.

**Subtle detail:** the 3-letter population codes (`EUR`, `EAS`,
`SAS`, `AFR`, `AMR`) need word-boundary matching. A naïve
substring match would flag `"increased"` as an EAS mention because
`"eas"` is a substring. The word-boundary regex (`\beas\b`) fixes
this. Longer strings like `"south asian"` use substring matching
since they're unambiguous. See
`anukriti-swarm/PROJECT_CONTEXT.md`-equivalent history for the
specific bug and fix.

---

## Population as evidence weighting

When the evidence sufficiency layer (next module) checks whether
we have enough evidence for a claim, **population coverage is one of
the 6 facets**:

```
Claim coverage facets:
  1. ALLELE            — do we have evidence about this allele?
  2. PHENOTYPE         — do we have a phenotype call?
  3. CPIC              — do we have CPIC guideline coverage?
  4. POPULATION        — do we have population-specific evidence? ← HERE
  5. RECOMMENDATION    — do we have a drug recommendation?
  6. CONFLICT_FREE     — are all signals consistent?
```

If the query is about a SAS patient but all the evidence is from
EUR cohorts, the `POPULATION` facet is flagged as missing or
uncertain, and the sufficiency decision engine (12 R-rules,
Module 09) routes accordingly.

---

## Bias detection — three named patterns

From `core/evidence_sufficiency/uncertainty/bias_detector.py`:

```python
class BiasKind(str, Enum):
    EUROCENTRIC_IMBALANCE = "eurocentric_imbalance"
    ANCESTRY_SCARCITY = "ancestry_scarcity"
    UNSUPPORTED_EXTRAPOLATION = "unsupported_extrapolation"
```

Three bias kinds, each with a concrete numeric threshold. Not
"the model thinks this might be biased" — actual tests.

### EUROCENTRIC_IMBALANCE

**Triggered when:** target population is non-EUR AND target
evidence count = 0 AND EUR evidence count > 0.

**In English:** "We're being asked about a non-European patient,
but all the evidence we retrieved is from European cohorts."

**Example:** A query about CYP2C19 clopidogrel for a SAS patient
returns 12 evidence documents — all from UK Biobank EUR cohorts.
SAS is non-EUR; SAS evidence count is 0; EUR evidence count is 12.
`EUROCENTRIC_IMBALANCE` flagged.

### ANCESTRY_SCARCITY

**Triggered when:** target allele count / max allele count < 0.5
(default threshold, configurable per-call).

**In English:** "The target population has less than half the
allele-frequency data of the best-represented population."

**Example:** CYP2D6 *4 has EUR data covering 50 cohort studies and
AFR data covering 3. Ratio = 3/50 = 0.06. Scarcity flagged.

### UNSUPPORTED_EXTRAPOLATION

**Triggered when:** POPULATION facet is uncertain AND target has
zero KG frequency data.

**In English:** "Not only is the evidence for this population thin,
but we don't even have frequency data in the knowledge graph to
know what the prior should be. We're extrapolating blind."

**Example:** A query about an indigenous Pacific Islander
population. Our super-population closed enum doesn't include it;
our KG has no frequency edges for it; the retrieval layer finds
EUR-ish proxies. `UNSUPPORTED_EXTRAPOLATION` flagged.

---

## The AFR + CYP2D6 case — an honest refusal

One of the canonical test scenarios (`demos/evidence_sufficiency_
demo.py`):

> *Codeine + CYP2D6 + African ancestry — what should we recommend?*

The expected answer: **we refuse to synthesize.** Reasons:

1. CYP2D6 has genuine population-scarcity in published evidence for
   AFR populations specifically (the seed knowledge graph reflects
   this reality).
2. `PopulationEvidenceBiasDetector` flags `ANCESTRY_SCARCITY`.
3. Evidence sufficiency routes to `DOWNGRADE` — the recommendation
   gets a reduced-confidence tier with a named-rule refusal.
4. The output surfaces: "Downgrade — ancestry scarcity in AFR for
   CYP2D6. Evidence density below threshold. Will not synthesize a
   strong recommendation."

The output **doesn't invent a plausible-sounding answer from EUR
data**. That's the feature. Refusing is correct behavior when the
evidence doesn't support a claim — and "refusing" here doesn't mean
"error" — it means emitting a structured refusal record with:

- The specific rule ID that triggered (`ANCESTRY_SCARCITY`)
- The facet that's insufficient (`POPULATION`)
- A pointer to the graph nodes/edges that are missing
- A suggested remediation ("retrieve more AFR-specific evidence
  and re-run")

Compare this to a general-purpose LLM responding to the same query:
it will almost certainly produce a confident-sounding recommendation
derived from implicit EUR priors. **That confidence is the bug.**
Honest ancestry-aware systems must sometimes say "no answer yet."

---

## Sub-populations — why they're deferred

The KG schema has a `NodeKind.ANCESTRY` kind that's unused in the
current seed (0 nodes). It exists as a **populated extension point**.

Why not seeded today:
- Sub-population allele-frequency data exists (1000 Genomes has
  SAS:GIH, SAS:BEB, etc.), but its clinical-outcome literature is
  sparse at the sub-population level.
- Adding sub-population nodes without evidence edges would claim
  resolution we don't have.

Why kept as an extension point:
- When the literature catches up, adding SAS:GIH as an ANCESTRY
  node + HIGHER_FREQUENCY_IN edges from alleles is a
  `knowledge_graph/seed.py` edit. No caller changes.
- Having the `NodeKind.ANCESTRY` enum value means we don't need an
  enum migration to add the feature. The shape is ready.

This is deferred-correctly — we don't stub in data we don't have,
and we don't bake in a data model that can't grow.

---

## How population flows through the whole pipeline

Bringing it together:

```
Query: (drug=clopidogrel, gene=CYP2C19, population=SAS, genotype=*2/*2)

 Stage 1. Context assembly
   → SwarmExecutionContext.population = SuperPopulation.SAS

 Stage 2. Orchestration
   → router activates: pharmacogene agent + population agent

 Stage 3. Retrieval
   → PopulationAwareRetriever boosts SAS-tagged docs
   → KG reasoner walks:
        SAS --HIGHER_FREQUENCY_IN--> CYP2C19 *2 (weight 0.36)
        CYP2C19 *2 --ASSOCIATED_WITH--> Poor Metabolizer
        Poor Metabolizer --CONTRAINDICATED_FOR--> clopidogrel

 Stage 3.5. Sufficiency check
   → POPULATION facet: COVERED (SAS-specific KG edge exists)
   → all 6 facets clean → SufficiencyDecision.SUFFICIENT
   → BiasDetector checks:
        EUROCENTRIC_IMBALANCE — no (SAS evidence present)
        ANCESTRY_SCARCITY — no (SAS is well-represented for CYP2C19)
        UNSUPPORTED_EXTRAPOLATION — no (KG has frequency data)
     → 0 bias findings

 Stage 4. Verification
   → 4 engines pass: shape, existence, truth, chain

 Stage 5. Synthesis
   → narrative generated, guarded by GenerativeBoundary
   → output includes population context: "Given South Asian
     ancestry (CYP2C19 *2 frequency: 36%), the loss-of-function
     genotype is expected to affect drug metabolism..."
```

Population is in the input, the retrieval layer, the knowledge
graph, the sufficiency check, the bias detector, and the
explanation. It's not a label attached to the output — it's
reasoning infrastructure from step 1.

---

## Summary

You now know:

- **Population is a first-class `NodeKind`** in the knowledge graph,
  with weighted `HIGHER_FREQUENCY_IN` edges to alleles.
- **`SuperPopulation` is a 5-value closed enum** — EUR, EAS, SAS,
  AFR, AMR.
- **Population-aware retrieval** re-ranks documents by target-
  population mentions, with word-boundary matching for 3-letter
  codes.
- **`BiasKind` is a 3-value closed enum** with concrete numeric
  thresholds: Eurocentric imbalance, ancestry scarcity, unsupported
  extrapolation.
- **The AFR + CYP2D6 refusal** is a feature — honest abstention
  when the evidence doesn't support a strong claim.
- **Sub-populations are a populated extension point**, not seeded
  today because the evidence isn't mature.

Next: [Module 09 — Evidence and Safety](09-evidence-and-safety.md).
The full sufficiency layer, its 12 R-rules, 10 V-rules, 9 U-rules,
and 4 verification engines.
