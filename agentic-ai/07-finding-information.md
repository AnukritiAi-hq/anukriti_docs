# 07 — Finding Information

> A helper doesn't guess — she **looks it up**. The trick is knowing
> when she's looked up enough.

---

## The Story

A customer asks Anu: *"Can you make a pistachio-rosewater cake?"*

Anu's never made one. She doesn't guess. She goes to the
**recipe shelf**.

She doesn't just grab the first book she sees. She has a strategy:

1. **Check the "special-ingredient" shelf first.** Pistachios and
   rosewater aren't everyday. If there's a whole book about
   unusual ingredients, start there.
2. **Check the "cake" shelf second.** Maybe a generic cake recipe
   can be adapted.
3. **Check the "regional cookbooks" third.** Persian cookbooks
   often use rosewater.

She doesn't read all three piles. She reads until she has **enough
to start**. Maybe one good recipe from shelf 1 is enough. Maybe she
needs to combine bits from shelf 1 and shelf 2. Either way, she
stops when she has what she needs.

That's what our agents do when they need information.

---

## What this means for computers

When an agent needs information to answer a question, it:

1. Has **multiple places** to look (different sources, different
   search strategies)
2. Knows a **sensible order** to look in (specific before general)
3. Knows **when to stop** (when it has enough)

The bad way: search everywhere, always, return everything.
Wasteful. Slow. Overwhelms the next agent.

The good way: search strategically, evaluate after each step, stop
when the evidence bundle is sufficient.

We call this **multi-strategy retrieval with adaptive stopping**.

---

## What we built

Our retrieval system has five distinct pieces, each with one job.

### The retrievers (the "shelves")

```
anukriti-swarm/retrieval/multi_strategy/
  biomedical_retriever.py      the abstract base class
  dense_retriever              keyword/semantic match against mock docs
  population_aware_retriever   re-ranks by ancestry relevance
  graph_retriever              walks the knowledge graph (Module 08)
```

Four retrievers, four strategies. The **abstract base class**
means they all share the same interface — any retriever can be
swapped for another without the agent knowing.

### The diversity selector

If we just concatenate results from all four retrievers, we get
duplicates. The same paper might be in three of them.

The **`EvidenceSelector`** de-duplicates and diversifies:

```
anukriti-swarm/retrieval/multi_strategy/graph_and_selector.py
```

It keeps one copy of each unique evidence record, prioritizes
diverse sources over repetitive ones.

### The adaptive controller

This is the smart bit. Instead of running all four retrievers and
handing back everything, the **`AdaptiveRetrievalController`**
runs them **one at a time**, and after each one, asks: *"Do we
have enough?"*

Its loop is roughly:

```
bundle = []
for strategy in [dense, population_aware, graph, ...]:
    new_docs = strategy.retrieve(query)
    bundle.extend(new_docs)

    if bundle_is_sufficient(bundle):
        break  # stop early!

    if budget_exhausted():
        break  # give up, but honestly
```

The sufficiency check calls into the **Evidence Sufficiency Layer**
(Module 11). So retrieval and sufficiency are tightly integrated:
retrieve, check sufficiency, maybe stop.

### The stopping controller

Even inside a single retriever, we might want to stop early. The
**`RetrievalStoppingController`** watches signals like:

- **Evidence Coverage Ratio** — how much of what we need is covered?
- **Redundancy** — are new docs adding new information, or
  repeating what we have?
- **Budget** — are we approaching a time or token limit?

It emits a closed 3-value `StopSignal` enum:

```
STOP_SUFFICIENT    — we have enough, clean stop
STOP_STAGNATING    — new docs aren't adding anything new
STOP_BUDGET        — we're out of time/tokens
```

These signals are inspired by research patterns with names like
**ECR (Evidence Coverage Ratio)** and **Stop-RAG**. If you want to
read more, those terms are where to look.

### Why this matters

A retrieval system that always pulls the maximum amount of stuff:

- Is slow
- Overwhelms the synthesizer (too much text to summarize)
- Wastes money (LLM tokens cost money)
- Misses the point of *targeted* retrieval

An adaptive system:

- Stops early when the answer is clear
- Keeps going when the answer isn't clear
- Gives up gracefully when it can't find enough
- Logs *why* it stopped (which signal fired)

---

## Try it yourself

Open:

```
anukriti-swarm/retrieval/stopping/controller.py
```

Find the `StopSignal` enum. Look at the three values. Each is
triggered by a specific condition.

Now open:

```
anukriti-swarm/retrieval/multi_strategy/adaptive_controller.py
```

Find the main loop. You'll see it running strategies one at a time
and asking for a sufficiency check after each.

Notice: there's no "do all four retrievers always" path. The
adaptive controller is the only controller. Single retrievers
still exist as building blocks; nothing forces running them
eagerly.

---

## The grown-up version

> Our retrieval pipeline uses a **multi-strategy, sufficiency-
> aware, adaptive-loop** pattern with explicit stopping controls:
>
> - **`BiomedicalRetriever`** (ABC) is the retriever contract;
>   concrete implementations include `DenseSemanticRetriever`
>   (TF-IDF today), `PopulationAwareRetriever` (signed boost
>   re-ranker over population mentions), and `GraphRetriever`
>   (wraps `MultiHopReasoner` + `PathEvidenceRetriever`, see
>   Module 08)
> - **`EvidenceSelector`** (`retrieval/multi_strategy/graph_and_selector.py`)
>   — diversity + de-duplication merger
> - **`AdaptiveRetrievalController`**
>   (`retrieval/multi_strategy/adaptive_controller.py`) — runs
>   strategies in priority order with a sufficiency gate after
>   each; can broaden strategies if initial results are insufficient
> - **`RetrievalStoppingController`** (`retrieval/stopping/controller.py`)
>   — ECR-inspired stopping policy; closed 3-value `StopSignal`
>   enum (`SUFFICIENT`, `STAGNATING`, `BUDGET_EXHAUSTED`)
>
> The stopping policy is a pure function over
> `(SufficiencyReport, iteration_count, budget_state)`. It's
> deterministic — the same inputs always produce the same
> stop signal.
>
> Population-aware re-ranking uses word-boundary regex matching
> for 3-letter population codes (EUR, EAS, SAS, AFR, AMR) to
> avoid false positives (e.g. `EAS` matching inside `increased`).
> See `core/models/population_mentions.py` for the anchor table.
>
> The pattern is related to **ReAct** (reasoning + acting loops)
> and **IRCoT** (iterative retrieval with chain-of-thought), but
> scoped to pharmacogenomic queries with closed-enum context
> types from Module 02.
>
> Full architecture in `architecture/evidence-sufficiency.md`.

---

## What you learned

Before this module: "retrieval" meant "run a search."

Now: retrieval is **strategic shelf-checking with an adaptive
stopping rule**. Multiple shelves, sensible order, stop when
sufficient, give up gracefully when stuck. Log which signal
fired so a human can audit.

No guessing. No "search everything always." Just pragmatic,
verifiable, bounded lookup.

---

Next up: **[08 — Walking a Map](08-walking-a-map.md)**

One of the retrieval strategies is "walk the knowledge graph."
What does that actually mean? Let's follow some arrows.
