# 06 — Remembering Things

> The shared notebook from yesterday is still on the shelf. Today's
> helpers can read it.

---

## The Story

Last Saturday, Anu got a strange order:

> "Three dozen chocolate-chili cupcakes for a themed birthday
> party."

The bakery had never made chocolate-chili before. The helpers
figured it out as they went. They wrote everything in their
notebook.

This Saturday, a similar order comes in:

> "Four dozen chocolate-chili cupcakes for another themed party."

Anu doesn't start from scratch. She pulls out **last Saturday's
notebook** and reads:

> *"Chili powder ratio: 1 teaspoon per dozen. Anything more was
> too spicy. Bake 2 extra minutes — the chili makes the batter
> thicker."*

Now this Saturday's bakery has a **hint** before they even start.
They still do the work. They still write their own notebook. But
the hint saves them time and prevents old mistakes.

That's memory.

---

## What this means for computers

Every time our system answers a question, it fills in a notebook
(the `SwarmExecutionContext` from Module 05). When the run ends,
the notebook isn't thrown away — it's **saved**.

Later, when a similar question comes in, we can:

1. **Find old notebooks** that match this question (by gene,
   drug, population)
2. **Read them**, looking for a hint about what worked or didn't
3. **Pass the hint** to the orchestrator *before* it plans
4. **Run the new question** with the benefit of experience

Without memory:
- Every question starts from zero
- Same questions run the same computation over and over
- We never learn which plans failed

With memory:
- Similar questions start with a hint
- Repeated questions are faster
- Old failures are visible so we don't repeat them

---

## What we built

Our memory has three layers:

### Layer 1: The notebook of the moment
(Covered in Module 05 — `SwarmExecutionContext`.) This is just
the current run. Ephemeral, in RAM.

### Layer 2: The written-down notebooks
Every completed run gets persisted — saved to MongoDB (or
in-memory if MongoDB isn't configured). Six kinds of
records per run:

- A **summary** (gene, drug, population, outcome)
- A **trace** of all the steps that ran
- A **context** snapshot (the full notebook)
- A **provenance chain** (every claim's evidence)
- An **evidence cache** (the papers used)
- A **verification log** (what was checked)

All six go to MCP (Model Context Protocol) services. Module 09
covers MCP as a tool-use protocol; here we use it as a
persistence layer.

### Layer 3: The smart memory assistant

The interesting piece. It's called **`MCPMemoryAdvisor`**.

When a new question comes in, the Advisor:

1. Looks up **past runs** with the same (gene, drug, population)
2. Summarizes them into a **digest** — "last 3 similar runs
   agreed on Poor Metabolizer, recommended prasugrel"
3. Hands the digest to the **Planner** (from Module 03) as a
   hint

The Planner doesn't have to use the hint. But it's there. And
the fact that we consulted memory is logged as a
`memory.consult` step in the run's trace, so if anyone audits
the decision, they can see "yes, this run looked at prior
runs before planning."

### Why this matters

Two reasons to have memory:

1. **Speed and consistency.** If we've seen this (gene, drug,
   population) before and the answer is stable, repeated
   queries should behave consistently. Memory makes that
   trivial.

2. **Detecting drift.** If the 10th run on the same question
   suddenly disagrees with the first 9, that's a red flag.
   Memory lets us notice. Without it, we'd silently drift.

The memory advisor lives here:

```
anukriti-swarm/integrations/mcp/memory_advisor.py
```

And the memory service it reads from:

```
anukriti-swarm/integrations/mcp/memory.py
```

---

## Try it yourself

Run a scenario twice. If you have the swarm repo set up, try:

```bash
# With MongoDB running, so runs persist
docker compose --profile mongo up -d

# Run a scenario
python -m demos.mcp_infrastructure_demo

# Look at what got persisted
docker exec -it anukriti-swarm-mongo mongosh anukriti_swarm
> db.memory.find()
```

You'll see records of past runs, each keyed by correlation ID.
If you run the demo again, a new record joins the list. The
Memory Advisor would find both when asked.

If you don't have MongoDB, the demo still works — with the
in-memory backend, memory is kept for the lifetime of the
process and thrown away when it exits.

---

## The grown-up version

> Memory in our platform is a three-layer construct:
>
> 1. **`SwarmExecutionContext`** — per-run state (Module 05)
> 2. **MCP persistence services** — 6 services (memory, traces,
>    context, provenance, evidence, verification) backed by
>    MongoDB or `InMemoryBackend`
> 3. **`MCPMemoryAdvisor`** — a read-path wrapper that summarizes
>    prior runs into a `PriorRunDigest` for the `WorkflowPlanner`
>
> The memory advisor is an opt-in feature of `GeminiOrchestrator`:
>
> ```python
> orchestrator = GeminiOrchestrator(memory_advisor=MCPMemoryAdvisor(client))
> ```
>
> Without the argument, the orchestrator operates stateless
> (backward compatibility is preserved). With it, every run
> consults memory before planning and emits a `memory.consult`
> step in the trace.
>
> The digest includes:
> - Count of matching prior runs
> - Concordance: do prior runs agree? (stable / divergent / insufficient)
> - A planning-hint string the Planner can include in its prompt
>
> The digest is **hinting**, not **deciding** — the Planner is
> free to ignore it. The GenerativeBoundary (Module 04) still
> applies; the Advisor can't smuggle in a recommendation that
> wasn't derived deterministically.
>
> The pattern is related to but distinct from **episodic memory**
> in cognitive architectures — we replay specific prior episodes,
> not aggregate statistics.

---

## What you learned

Before this module: an AI "learning from past interactions"
sounded vague.

Now: memory is specifically **past runs, persisted, summarized,
hinted to future runs**. Not magical learning. Just a library of
old notebooks that a smart assistant reads on the way in.

The key part: memory is *advisory*, not *authoritative*. The
orchestrator can ignore it. The boundary still applies. We
never let memory smuggle in an answer that didn't go through
proper deterministic channels.

---

Next up: **[07 — Finding Information](07-finding-information.md)**

Memory helps with questions we've seen before. What about new
questions? The agent needs to **look things up**. That's
retrieval, and it has more depth than "search for a keyword."
