# 03 — Who Tells Them What to Do?

> The helper who looks at the order, decides what's needed, and
> hands out the chores.

---

## The Story

It's Monday morning. A big order comes in:

> "Three dozen chocolate cupcakes with sprinkles, two birthday
> cakes, and a wedding cake — by Saturday."

Nobody in Anu's bakery can do all of that alone. And if everyone
just starts doing their own thing, things will get missed. The
cakes need dough, the dough needs flour, the wedding cake needs
frosting, the frosting needs cream...

Anu walks in, reads the order, and **plans**:

1. **Dough-mixer** — start on the cupcake dough first, then the
   cake batter
2. **Oven-watcher** — clear the oven for 10am, we'll be baking
3. **Froster** — after the cupcakes cool, frost chocolate
4. **Sprinkler** — after frosting, add sprinkles
5. **Wedding cake** — tomorrow's problem, I'll plan that then

Anu writes the plan on a board so everyone can see it. Each helper
**knows what they're supposed to do, and when**.

Then Anu also does one more thing: she decides *which specific
helper* does *which specific task*. There are two frosters. Priya
frosts chocolate. Ravi frosts vanilla. Today's order is chocolate,
so it goes to Priya.

Anu is doing two jobs here:

1. **Planning** — turning one big order into a list of small
   steps
2. **Routing** — picking which helper does which step

Every multi-agent system needs someone who does these two jobs.
We call them the **orchestrator**.

---

## What this means for computers

When a question comes in to our system, like:

> "For a South Asian patient with CYP2C19 star-2 slash star-2,
> what should we say about clopidogrel?"

...we can't just send that to every agent and hope. We need to:

1. **Make a plan** — what steps are needed?
   - Step 1: Check what the CYP2C19 genes do
   - Step 2: Consider the South Asian population context
   - Step 3: Look up evidence about clopidogrel
   - Step 4: Check if we have enough evidence to answer
   - Step 5: Verify safety
   - Step 6: Write the explanation
2. **Route each step** to the right agent.
   - Step 1 → CYP2C19 agent
   - Step 2 → Population agent
   - Step 3 → Evidence agent
   - Step 4 → Sufficiency agent
   - Step 5 → Verification agent
   - Step 6 → Narrative agent
3. **Run the plan**, watching that each step finishes before the
   next one needs it.

The helper who does all of this is called the **orchestrator**,
and ours has three parts:

- **The Planner** — makes the plan
- **The Router** — picks the right agent for each step
- **The Coordinator** — runs the plan

Three small jobs, one bigger job. Just like Anu.

---

## What we built

Our orchestrator lives here:

```
anukriti-swarm/core/orchestrator/
  planner.py         makes the plan
  router.py          picks the right agent
  coordinator.py     runs the plan, watches progress
  context_assembler.py   reads the question first
```

Four files, four small jobs.

### The Planner has a superpower (and a backup)

Here's an interesting detail. The Planner is *allowed* to ask an
LLM (a smart-brain) for help making plans. The LLM is great at
understanding unusual questions and suggesting clever plans.

But what if the LLM is broken? Or too slow? Or what if it
suggests something weird?

**The Planner has a backup plan.** A deterministic (boring,
predictable) plan that always works. If the LLM is available and
its suggestion is safe, use it. Otherwise, use the backup.

This is called an **LLM-with-fallback**. We use it anywhere a
smart-brain could help but isn't trustworthy-enough to be the
only option.

### The Router is strict

The Router takes a step from the plan (like "do the CYP2C19 part")
and finds the agent that handles CYP2C19. If no such agent exists
in our catalog, the Router **refuses**. It doesn't just send the
step somewhere else and hope.

Remember Module 01 — helpers have narrow, named roles. The Router
respects that.

### The Coordinator watches

The Coordinator fires off each step, waits for it to finish, and
checks the result. If a step fails, it doesn't silently continue.
It stops, reports what failed, and lets the outer system decide
what to do.

---

## Try it yourself

Open:

```
anukriti-swarm/agents/orchestrator/gemini_orchestrator.py
```

This is the facade — the one-stop-shop that wraps the Planner +
Router + Coordinator. You'll see something like this at the top:

```python
class GeminiOrchestrator:
    def run(self, query: str) -> OrchestrationResult:
        ...
```

That's the one-line story of our orchestrator:

> "Give me a question. I'll figure out who should answer it, in
> what order, and give you back a result."

Everything else in the file is the detail of *how*.

Now look at `core/orchestrator/planner.py` and find the word
`fallback`. That's the backup plan we talked about.

---

## The grown-up version

> Orchestration in our platform is a three-stage pipeline:
>
> 1. **`WorkflowPlanner`** (`core/orchestrator/planner.py`) —
>    transforms an input query into a sequence of `PlanStep`
>    records. The planner has two paths: a Gemini-LLM-powered
>    path using structured-output prompts, and a deterministic
>    fallback that pattern-matches on the query shape. The
>    fallback is used when the LLM is unavailable, returns
>    malformed output, or times out.
> 2. **`AgentRouter`** (`core/orchestrator/router.py`) — resolves
>    each `PlanStep.agent_name` against the `AgentRegistry`. A
>    step referring to an unregistered agent raises a
>    `RoutingError`. Agent names are not free-form strings but
>    registered entries from the agent catalog.
> 3. **`ExecutionCoordinator`** (`core/orchestrator/coordinator.py`)
>    — iterates the resolved plan, invokes each agent with its
>    typed input contract, accumulates results into
>    `SwarmExecutionContext`, and produces an
>    `OrchestrationResult` or `OrchestrationError`.
>
> The facade is `GeminiOrchestrator`
> (`agents/orchestrator/gemini_orchestrator.py`). Its public API:
> `run(query)`, `compare_populations(...)`, `compare_drugs(...)`.
>
> The planner is the only place in the deterministic execution
> path where an LLM call occurs outside narrative synthesis.
> The `GenerativeBoundary` (Module 04) guards what the LLM
> output is allowed to say.

---

## What you learned

Before this module: "orchestration" sounded like magic glue.

Now: orchestration is just **plan + route + run**. A human boss
does this at every workplace. Our orchestrator does it for
agents. The plan might come from an LLM or from a boring backup,
but the shape is the same.

Anu makes a list on a whiteboard, hands out chores, and watches
that nobody's stuck. Our orchestrator does exactly that for code.

---

Next up: **[04 — The Safety Line](04-the-safety-line.md)**

But wait — if a helper is *allowed to decide* things, what stops
them from deciding to do something unsafe? Let's meet the one
rule no helper can break.
