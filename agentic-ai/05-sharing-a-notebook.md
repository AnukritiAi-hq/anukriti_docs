# 05 — Sharing a Notebook

> Nine helpers, one order, one shared book. Everyone writes in it.
> Nobody erases anyone else's writing.

---

## The Story

When a big order comes in, the bakery helpers each do their part
— but what did each one decide?

The dough-mixer adds: *"Made 3 dozen chocolate batter, 10:15am."*
The oven-watcher adds: *"Started bake, 10:45am. 350°F."*
The froster adds: *"Frosting chocolate, 11:30am. Used dark
chocolate."*
The sprinkler adds: *"Added rainbow sprinkles, 11:45am."*

Each helper writes their own line. Nobody erases anybody else.
By the end of the day, there's a **complete record** of what
happened, in order.

Why is this important?

1. **The next helper needs to know.** The froster can't start
   without knowing the cupcakes are cool. The sprinkler can't
   start without frosting.
2. **If something goes wrong, we can check.** "Why did the cake
   burn?" Look at the notebook. "Oven-watcher started at 10:45,
   never checked after that. Oven at 400°F instead of 350."
   There's the answer.
3. **Tomorrow we can learn.** "What did we do for last week's
   wedding cake?" Go look.

One shared notebook. Everyone writes. Nobody erases. Everything
has a timestamp.

---

## What this means for computers

When nine agents work on the same question, they each have
something to contribute:

- The pharmacogene agent: *"CYP2C19 star-2 slash star-2 means
  Poor Metabolizer."*
- The population agent: *"This allele has 36% frequency in South
  Asian populations."*
- The evidence agent: *"Found CPIC guideline PMID 34032273."*
- The verification agent: *"All four safety checks passed."*

Each agent adds a fact. Later agents need the earlier facts to do
their job.

The bad way: **pass facts around in messages**. Every message has
to include all the history. Messages get huge. Agents have to
remember to include everything. Bugs creep in.

The good way: **one shared object** that everyone can read and
add to. Each agent's additions are visible to the next agent.
Nobody has to carry history in their messages.

But we have to be careful: **nobody should be able to erase what
someone else wrote**. Facts, once added, stay added. The notebook
is *append-only*.

---

## What we built

Our shared notebook is called the **`SwarmExecutionContext`**.

It lives at:

```
anukriti-swarm/core/orchestrator/context.py
```

It's a Pydantic object (think: a clearly-labeled box of fields)
that gets passed around the pipeline. Each stage of the run can
read it, and can add to specific fields.

Here's roughly what it looks like:

```python
class SwarmExecutionContext(BaseModel):
    correlation_id: str
    query: str
    population: SuperPopulation | None
    gene: str | None
    diplotype: str | None

    # Phases complete (append-only list)
    activated_agents: tuple[str, ...]

    # Each agent's output
    phenotype_inference: PhenotypeInference | None
    population_context: PopulationContext | None
    evidence_bundle: EvidenceBundle | None
    verification_outcome: VerificationOutcome | None

    # Accumulated errors (append-only)
    errors: tuple[str, ...]

    # Trace of what happened (append-only)
    trace: OrchestrationTrace
```

Two things to notice:

1. **Some fields start as `None` and get filled in.** That's how
   each agent contributes. The pharmacogene agent sets
   `phenotype_inference`; the evidence agent sets
   `evidence_bundle`; etc.
2. **Some fields are `tuple[..., ...]`** instead of `list[..., ...]`.
   Tuples can't be edited in place. To "add" to a tuple, you make
   a new tuple with the old items plus the new one. This is how
   we make sure nobody accidentally erases earlier writing.

In plainer English: it's a **frozen, append-only** notebook. Each
helper can add a page. Nobody can tear out a page.

### There's a second notebook for shared biomedical facts

Alongside the execution context, there's a
**`SharedBiomedicalContext`** for facts that aren't tied to one
specific run. Things like:

- The current evidence graph (what papers support what claims)
- The verification state (which checks have passed)
- Cross-agent provenance stamps

It lives at:

```
anukriti-swarm/interoperability/shared_context/biomedical.py
```

Two notebooks. One for "this run." One for "the state of what
we believe." Both append-only.

---

## Try it yourself

Open:

```
anukriti-swarm/core/orchestrator/context.py
```

Look at the `SwarmExecutionContext` class. Count the fields.
That's the shape of one run's notebook.

Notice which fields are **tuples** (like `activated_agents`) and
which are **frozen records** (like `phenotype_inference`). Neither
can be mutated in place. If you wanted to add an agent to
`activated_agents`, you'd write:

```python
context = context.copy(update={
    "activated_agents": (*context.activated_agents, "new_agent")
})
```

That spread-into-new-tuple pattern is everywhere in our code. Get
used to it. It's how we make sure facts don't get silently
changed.

---

## The grown-up version

> Our platform maintains two shared-state objects across a run:
>
> - **`SwarmExecutionContext`** (`core/orchestrator/context.py`)
>   — the per-run mutable-but-structured state container. Pydantic
>   model with ~15 named fields. Tuples (not lists) enforce
>   append-only semantics for accumulation fields like
>   `activated_agents`, `errors`, and the underlying
>   `OrchestrationTrace.steps`.
> - **`SharedBiomedicalContext`**
>   (`interoperability/shared_context/biomedical.py`) — the
>   cross-agent biomedical state. An 8-field record with evidence
>   and verification graphs that span multiple agents in one run.
>   Co-evolved alongside the `AgentContextEnvelope` (Module 02).
>
> Both objects implement the **shared mutable state** pattern for
> multi-agent coordination, with three discipline rules:
>
> 1. **Append-only accumulators** — tuples for history, never lists
> 2. **Frozen sub-records** — every payload field (phenotype,
>    population, evidence) is itself a frozen Pydantic record
> 3. **Update via `.copy(update=...)`** — no in-place mutation
>
> The pattern is similar to the reducer pattern in functional
> state management (Redux, Elm architecture): state flows through
> a sequence of agents, each of which produces a new version of
> the state based on the old one and its own contribution.
>
> A full `SwarmExecutionContext` is persisted at the end of each
> run via `MCPContextManager` (Module 06) so a run can be
> replayed later.

---

## What you learned

Before this module: "shared state" between agents sounded
dangerous — like they'd step on each other.

Now: shared state is fine *if* nobody can erase history.
Append-only. Frozen records. Copy-to-update. These three rules
together make multi-agent coordination sane.

Our bakery's notebook is a stack of pages. Each helper adds their
page. The pages are glued in. Tomorrow we can replay the whole day.

---

Next up: **[06 — Remembering Things](06-remembering-things.md)**

One day's notebook is great. But what about **learning from
yesterday's notebook** — or from a notebook written six months
ago? That's memory, and memory across runs is a different beast.
