# Module 08 — Population Awareness

> Prerequisites: [03 Core Concepts](03-core-concepts.md), [05 Gene Matching](05-gene-matching.md)

---

## The question we're answering

Why does the platform treat ancestry as a first-class reasoning
input? What does "population-aware" actually change in the code?
And when ancestry data is thin, how do we refuse honestly instead
of guessing?

---

## What "population-aware" actually means here

> *"Anukriti claims to treat every population equally. How?"*

This is the question people ask first, and it deserves a direct
answer before the implementation details.

The phrase **"population-aware"** can mean three different things.
We need to be precise about which one we do, because two of them
are opposites.

### The three meanings of "equal treatment"

**Meaning 1: Same answer for everyone.**
This is what Eurocentric medicine accidentally does. Clinical
guidelines derived from EUR cohorts get applied uniformly, so
SAS, EAS, AFR, and AMR patients receive the same recommendation
as EUR patients even when the underlying biology argues for
different ones. This is the 14%-SAS-on-clopidogrel problem from
[Module 01](01-what-is-anukriti.md) — it's the problem we exist
to solve, not our goal.

**Meaning 2: Same *reasoning rigor* for everyone.**
Every population goes through the same 5-stage pipeline. Same
6 evidence facets checked. Same 4 verification engines. Same
`GenerativeBoundary`. No hidden Eurocentric fast-path that skips
checks for EUR patients. **This is our goal** — equal epistemic
rigor, not equal confidence.

**Meaning 3: Same *confidence* for every output regardless of
evidence.**
Also wrong, but in the opposite direction. A system that emits
the same confidence for every query — regardless of whether the
evidence supports the population in question — is dishonest.
Our system does the opposite: the same process produces
*different* confidence based on *actual* evidence density.

### What "equal rigor" looks like mechanically

Five concrete mechanisms make the platform population-aware.
Each one is a specific file and pattern you can inspect.

#### Mechanism 1 — Population as a first-class knowledge-graph node

The KG has a closed 10-value `NodeKind` enum
(`knowledge_graph/schema.py`). `POPULATION` is one of those kinds
— not a property stuck on other nodes, a node in its own right.
Edges of kind `HIGHER_FREQUENCY_IN` carry numeric weights.

From the seed data:

| Edge | Weight |
|------|--------|
| CYP2C19 \*2 → SAS | 0.36 |
| CYP2D6 \*4 → EUR | 0.20 |
| CYP2D6 \*17 → AFR | 0.20 |
| HLA-B \*15:02 → EAS | 0.08 |

The `MultiHopReasoner` multiplies weights along a walked path.
SAS + CYP2C19 \*2 is a 0.36-weighted edge; EUR + CYP2C19 \*2
would be 0.14. The walker produces **different weighted paths
for different populations**, even when the intermediate nodes
overlap.

#### Mechanism 2 — Population-aware retrieval re-ranker

`retrieval/multi_strategy/biomedical_retriever.py` (the
`PopulationAwareRetriever` class) applies a **signed boost**:

- Documents mentioning the target population score **higher**
- Documents mentioning a different population score **lower**
- Population-agnostic documents are unchanged

The mention-detector uses word-boundary regex for 3-letter
codes (so `EAS` doesn't match inside `increased`; see
`core/models/population_mentions.py`).

An SAS patient's retrieval surfaces Gujarati-cohort studies above
generic CPIC text; an EUR patient's retrieval inverts. **Same
candidate set, different top-ranked subset.**

#### Mechanism 3 — Population as one of 6 evidence-sufficiency facets

`core/evidence_sufficiency/coverage/claim_coverage.py` defines
the 6 facets. One of them is `POPULATION`. Each has a state:
`COVERED`, `UNCERTAIN`, or `MISSING`.

The 12-rule decision engine fires:

```
R5  POPULATION MISSING     → ESCALATE
R9  POPULATION UNCERTAIN   → DOWNGRADE
```

**We explicitly refuse to ignore whether we have
population-specific evidence.** An answer derived only from EUR
cohorts for a non-EUR patient gets downgraded — caveat attached,
not silent confidence.

#### Mechanism 4 — Named bias detection

`core/evidence_sufficiency/uncertainty/bias_detector.py` —
the `PopulationEvidenceBiasDetector` checks for three specific
patterns with concrete numeric thresholds:

| BiasKind | Trigger |
|----------|---------|
| `EUROCENTRIC_IMBALANCE` | Target is non-EUR AND target evidence count = 0 AND EUR evidence count > 0 |
| `ANCESTRY_SCARCITY` | Target allele count / max allele count < 0.5 (default) |
| `UNSUPPORTED_EXTRAPOLATION` | POPULATION facet UNCERTAIN AND target has zero KG frequency data |

A query about a Black patient on codeine (CYP2D6) surfaces
`ANCESTRY_SCARCITY` because AFR has sparse CYP2D6 evidence in our
seed. The answer is **downgraded**, not silently derived from
EUR priors. **Our honesty is proportional to actual evidence, not
proportional to the medical establishment's comfort.**

#### Mechanism 5 — Honest refusals with named rule IDs

The canonical operational test
(`demos/evidence_sufficiency_demo.py`):

> *"Codeine + CYP2D6 + African ancestry — recommendation?"*

Expected output:

```
decision:      DOWNGRADE               (R9)
verdict:       UNCERTAIN                (V7)
uncertainty:   HIGH                     (U3 + U5)
bias_findings: [ANCESTRY_SCARCITY]
```

A general-purpose LLM would happily produce a confident answer
for the same query. Ours refuses to, and cites the specific rule
that made it refuse. **This is the operational meaning of
population-awareness in our system: we refuse when evidence
doesn't support a claim for a specific population.**

### The three honest gaps

Claiming "population-aware" means being honest about where we
fall short. Three specific gaps:

#### Gap 1 — Sub-populations are not seeded

The `NodeKind.ANCESTRY` enum value exists as a populated
extension point, but has **zero nodes in the seed today**.
That means:

- SAS:GIH (Gujarati) and SAS:BEB (Bengali) reason identically
- AFR:YRI (Yoruba) and AFR:ESN (Esan) reason identically
- Clinically, these sub-populations have real allele-frequency
  differences

This is deferred-correctly, not broken. The enum value is ready
for when published evidence justifies sub-population edges.
But today, "population-aware" means "super-population-aware,"
not "patient-ancestry-aware."

#### Gap 2 — The 5-value closed enum excludes mixed ancestry

`SuperPopulation` has EUR, EAS, SAS, AFR, AMR. **That's 5
buckets for ~8 billion people.** Mixed-ancestry individuals
(who are a large and growing share of patients) don't fit
cleanly into one bucket.

Today, a clinician picks the best-match category. The honest
solution — ancestry as a mixture vector rather than a single
categorical — is not implemented. It would be a real research
project, not a small refactor.

#### Gap 3 — We name scarcity; we don't fix it

Our bias detector *names* the problem. It doesn't solve it.
Solving it requires either:

1. More diverse cohort data in the knowledge graph (an
   upstream-research problem)
2. Different reasoning modes for thin-evidence populations (e.g.
   higher-confidence related populations as a prior)

We do neither. We refuse, and we cite why we refused. That's
**epistemically honest but clinically unsatisfying** — a patient
still needs a decision, and "we can't help you" is not a
clinically useful answer. A future research direction.

### So — are we treating every population equally?

- **Equal reasoning rigor? Yes.** Every population goes through
  the same 5-stage pipeline with the same checks and the same
  boundary.
- **Equal confidence outputs? No, and this is deliberate.**
  Different populations produce different confidence tiers
  based on actual evidence density.
- **Equal clinical usefulness across populations? No, and we
  don't pretend otherwise.** A patient in an underrepresented
  population gets a less actionable answer from our system.
  That's a limitation of the evidence base we're reading, not
  one we introduce. We make it *visible* (named refusals) where
  other systems make it *invisible* (confident EUR-derived
  answers).

If a reviewer asks *"why is your answer for a SAS patient so
specific and your answer for an AFR patient just a downgrade?"*
— the honest response is: *"because the evidence density
differs by population, and we refuse to paper over that. Here's
the specific rule that fired and the specific bias we
detected."*

That's what population-aware actually means here.

*(For the friendly, story-based version of the same content, see
[agentic-ai Module 08a — Treating Everyone Fairly](../agentic-ai/08a-treating-everyone-fairly.md).)*

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
