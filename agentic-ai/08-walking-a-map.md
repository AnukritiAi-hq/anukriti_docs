# 08 — Walking a Map

> Sometimes the answer isn't in one place. You have to **follow
> arrows** from one fact to the next.

---

## The Story

You're in Anu's bakery and you need to find out: "Who has the spare
key to the back door?"

Nobody tells you directly. But there are **clues on the wall**:

- By the fridge: *"The manager has the spare key."*
- Next to the coatroom: *"The manager today is whoever is
  wearing the blue apron."*
- On the schedule: *"Today's blue apron = Priya."*

To get from the question to the answer, you have to walk the
clues in order: **back key → manager → blue apron → Priya**.

One clue on its own doesn't tell you what you need. But each clue
**points to the next clue**. Three steps, one answer.

This is **walking a map**. Or, in fancier terms: **multi-hop
reasoning**.

---

## What this means for computers

A lot of medical knowledge is **connected by pointers**, not
stored in one sentence.

Consider this question:

> "For someone with South Asian ancestry, on clopidogrel — are
> there drug-gene interactions we should worry about?"

The answer isn't written down anywhere as one sentence. But
connected facts exist:

1. **South Asian population** → has higher frequency of →
   **CYP2C19 star-2 allele**
2. **CYP2C19 star-2** → associated with → **Poor Metabolizer
   phenotype**
3. **Poor Metabolizer** → contraindicated for → **clopidogrel**

Walking those three arrows, we arrive at: *"Yes, South Asians
on clopidogrel have elevated risk due to CYP2C19 \*2 frequency."*

Each single fact is small. The **connected walk** is the answer.

We call this a **knowledge graph**. Nodes are facts (populations,
genes, alleles, drugs, phenotypes). Edges are the arrows
connecting them.

---

## What we built

Our **pharmacogenomic knowledge graph** lives at:

```
anukriti-swarm/knowledge_graph/
  schema.py         defines the kinds of nodes and edges
  seed.py           the actual facts we know (37 nodes, 34 edges)
  graph.py          the in-memory graph structure
  builder.py        helpers to build and query the graph
  reasoner.py       the multi-hop walker
```

### The nodes

There are **10 kinds of nodes** (and it's a closed list — like
Module 02's closed enum):

```
POPULATION       (SAS, EUR, AFR, EAS, AMR)
ANCESTRY         (sub-populations — extension point)
GENE             (CYP2C19, CYP2D6, HLA-B, ...)
VARIANT          (rsIDs — extension point)
ALLELE           (*1, *2, *17, ...)
PHENOTYPE        (PM, IM, NM, RM, UM)
DRUG             (clopidogrel, codeine, ...)
ADVERSE_REACTION (serious skin reactions, etc.)
GUIDELINE        (CPIC 2022.1, etc.)
EVIDENCE_PAPER   (PMID:34032273, etc.)
```

### The edges

There are **7 kinds of edges** between them:

```
METABOLIZES              gene --> drug
CONTRAINDICATED_FOR      phenotype --> drug
ASSOCIATED_WITH          allele --> phenotype
HIGHER_FREQUENCY_IN      allele --> population  (WEIGHTED — the %)
SUPPORTED_BY             any node --> evidence paper
CONFLICTS_WITH           two facts that disagree
GUIDELINE_RECOMMENDS     guideline --> action
```

### The walker

The walker is called **`MultiHopReasoner`**:

```
anukriti-swarm/knowledge_graph/reasoner.py
```

Given a starting node (say, "South Asian population") and a
target kind (say, "drug"), the walker does a **bounded breadth-
first search**:

1. Start at South Asian
2. Follow every edge to its neighbor nodes
3. From each of those, follow every edge to *their* neighbors
4. Keep going up to 4 hops (we set a limit)
5. Collect every path that reaches a drug node

Along the way, three things happen:

- **Population weights multiply along the path.** So a 36%-frequency
  edge × a strong-association edge gives a combined path weight.
- **Cycles are skipped** — the walker never revisits a node it's
  already visited on the current path.
- **Conflict edges are skipped entirely** — if two sub-paths
  disagree (CONFLICTS_WITH), the walker avoids that route.

The walker returns a list of **ranked paths** — each one telling
a little story from the population all the way to the drug.

### Why this matters for an AI agent

Without the knowledge graph, an LLM answering our question would
have to:

- Know all the facts
- Know how they connect
- Make up the connection if it's not in training data

With the knowledge graph:

- The facts are structured, not buried in prose
- The connections are explicit edges
- The walker is deterministic — same start + same target = same
  paths
- The paths are citable — we can show "here's the exact chain of
  evidence"

An LLM may still *narrate* the result, but it does so over **real
walked paths**, not imagined ones. No hallucinated connections.

---

## Try it yourself

Look at the seed file:

```
anukriti-swarm/knowledge_graph/seed.py
```

It's a list of nodes and edges — literally a spreadsheet in code
form. You can count them: 37 nodes, 34 edges.

Find the edge for `CYP2C19 *2 → HIGHER_FREQUENCY_IN → SAS`. It
has a weight of `0.36` — the 36% frequency we've been talking
about.

Now look at the reasoner:

```
anukriti-swarm/knowledge_graph/reasoner.py
```

Find the `max_hops` parameter. That's the bound — how far the
walker will go. Default is 4.

Why limit? Because without a limit, a graph walker can wander
forever. And 4 hops is enough for most pharmacogenomic questions.

---

## The grown-up version

> The **pharmacogenomic knowledge graph (KG)** in our platform is
> an in-memory adjacency graph with:
>
> - **10 closed `NodeKind` values** (POPULATION, ANCESTRY, GENE,
>   VARIANT, ALLELE, PHENOTYPE, DRUG, ADVERSE_REACTION, GUIDELINE,
>   EVIDENCE_PAPER)
> - **7 closed `EdgeKind` values** (METABOLIZES,
>   CONTRAINDICATED_FOR, ASSOCIATED_WITH, HIGHER_FREQUENCY_IN
>   [weighted], SUPPORTED_BY, CONFLICTS_WITH, GUIDELINE_RECOMMENDS)
> - **37 seed nodes and 34 seed edges** derived from in-tree CPIC
>   tables and rule files (no external ontology imports)
>
> `MultiHopReasoner` implements a bounded BFS traversal
> (`max_hops=4` default) with:
>
> - Cycle prevention via visited-set per path
> - Deterministic ordering (path weights are products of
>   HIGHER_FREQUENCY_IN edge weights)
> - Optional `min_pop_frequency` pruning
> - `CONFLICTS_WITH` edge skip for conflict avoidance
>
> Every edge requires a non-empty `ProvenanceStamp.source_id` —
> edges cannot be added without attribution. This is the same
> scope-firewall discipline used elsewhere (closed enums, frozen
> records, no freeform content).
>
> `PathEvidenceRetriever` converts a walked path into the
> evidence documents that support it, hydrating each
> `SUPPORTED_BY` edge into full evidence records from the MCP
> evidence cache.
>
> The pattern is a specific implementation of **graph-based
> retrieval-augmented generation (GraphRAG)** — but scoped to
> the pharmacogenomic domain and constrained by closed enums.
> Full architecture in `architecture/pharmacogenomic-kg.md`.

---

## What you learned

Before this module: "knowledge graph" sounded like a buzzword.

Now: a knowledge graph is a bunch of facts (nodes) connected by
arrows (edges). Walking a few arrows in a row lets you derive
things that no single fact states directly.

Our walker is bounded (4 hops max), avoids cycles, follows
weights, and skips known conflicts. Every edge has a source
citation. No hallucination — just arrows you can see and follow.

---

Next up: **[08a — Treating Everyone Fairly](08a-treating-everyone-fairly.md)**

Walking a knowledge-graph map already touched on populations.
Before we move on to tools, let's dig into the deeper question:
what does it actually mean for our system to treat every
population equally?

Then after that: **[09 — Using Tools](09-using-tools.md)**

Sometimes an agent needs to do something that isn't code it was
born with. Save a file. Look up a paper. Write to a database.
That's tool use, and it has its own shape.
