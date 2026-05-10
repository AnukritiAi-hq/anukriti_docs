# 04 — The Safety Line

> A rule no helper can break. Not "should not." **Cannot.**

---

## The Story

Anu's bakery has **one iron rule**. It's written in huge letters
on the wall:

> *"NEVER TASTE THE BATTER WITH RAW EGGS IN IT."*

Everyone knows it. Everyone agrees with it. But sometimes a new
helper forgets. A cupcake smells delicious. They stick a finger
in the batter to taste...

So Anu doesn't just *tell* the helpers the rule. She makes a
**special cabinet** where the raw egg batter goes. The cabinet
has a lock. Only cooked batter (from the oven) can come out the
other side.

If a helper wants to taste batter, they can only reach into the
"cooked" side. They *cannot physically get* raw batter, even if
they wanted to.

The rule isn't trusted to the helpers. The rule is **built into
the kitchen**.

That's the right way to handle a safety rule you really, really
mean.

---

## What this means for computers

When you use an AI, there are some things the AI should never do:

- Invent a medicine that doesn't exist
- Pretend it ran a check when it didn't
- Say "this gene does X" when it really means "I guess this gene
  does X"
- Make up a study or paper

You could try to write rules in the prompt: "Please don't invent
citations. Please don't guess."

But AIs are like new helpers tasting batter. **Sometimes they
forget.** Sometimes they decide the rule doesn't apply this one
time.

So we don't trust rules to the AI. We build the rules into the
**code around** the AI.

When the AI tries to do something forbidden, the code notices and
**stops everything**. The answer never reaches the user. There's
no "override this once" button. Changing the rule requires
changing the code (which means a human sees the change).

We call this a **safety boundary** or a **guardrail**.

---

## What we built

Our safety boundary has a name: **`GenerativeBoundary`**.

It lives here:

```
anukriti-swarm/core/orchestrator/boundary.py
```

And it knows exactly four things that are forbidden:

```python
class ForbiddenAction(Enum):
    INFER_PHENOTYPE         = "infer_phenotype"
    OVERRIDE_RECOMMENDATION = "override_recommendation"
    BYPASS_VERIFICATION     = "bypass_verification"
    FABRICATE_CLAIM         = "fabricate_claim"
```

Those four. That's the whole list.

### What each one means (in 6-year-old):

**INFER_PHENOTYPE** — "Figure out what the gene does."

> The LLM is NOT allowed to say things like "this person is
> probably a poor metabolizer." That's the job of the pharmacogene
> agent, which follows real CPIC rules. The LLM can *report* what
> the pharmacogene agent said. It cannot *decide* it itself.

**OVERRIDE_RECOMMENDATION** — "Change what the doctor-book says."

> The CPIC book says "avoid clopidogrel for poor metabolizers."
> The LLM is NOT allowed to say "well, maybe it's fine actually."
> The recommendation is locked. The LLM can *explain* it. It
> cannot *change* it.

**BYPASS_VERIFICATION** — "Skip the double-check."

> The verification agent runs after every answer. The LLM is NOT
> allowed to skip it "to save time." The double-check either
> runs, or the answer doesn't come out. No exceptions.

**FABRICATE_CLAIM** — "Make up a study or citation."

> The LLM is NOT allowed to cite PubMed IDs it just invented, or
> guidelines that don't exist. Every citation must come from the
> evidence cache. If the LLM tries to add a made-up citation,
> verification catches it.

### How the boundary enforces these

The boundary isn't a warning. It's not a log message that says
"hmm, that looked wrong."

When the LLM tries to do one of the four things, the code
**raises an exception**. A run that tries to bypass verification
**stops right there**. Nothing reaches the user. No partial
answer. No "here's what we got before we caught the problem."

In Python, this looks like:

```python
class BoundaryViolation(Exception):
    ...

if action in FORBIDDEN:
    raise BoundaryViolation(f"Agent tried to {action}")
```

Exceptions aren't just logged — they **halt the program**. The
raw egg batter cabinet is locked.

### You can't unlock it at runtime

There is no `DISABLE_BOUNDARY=true` environment variable. No
feature flag. No "just this once" mode.

If you want the boundary to allow a fifth forbidden action — or
remove one of the existing four — **you have to change the code**
in `boundary.py`. That change shows up in a pull request. A
reviewer has to approve it. And the review makes it very hard
for the change to sneak in unnoticed.

We call this "compile-time safety" or "make the rule impossible
to break at runtime." It's one of the most important patterns in
our whole system.

---

## Try it yourself

Open the boundary file:

```
anukriti-swarm/core/orchestrator/boundary.py
```

Find the `ForbiddenAction` enum — the four-value list.

Now imagine you wanted to add a fifth forbidden action, like
"SUGGEST_OFF_LABEL_USE." What would you change?

You'd have to:

1. Add `SUGGEST_OFF_LABEL_USE = "suggest_off_label_use"` to the
   enum
2. Add the check in the functions that use the boundary
3. Add tests in `tests/unit/test_boundary.py`
4. Open a PR
5. Get a reviewer to approve it
6. Merge

Notice how many steps? That's on purpose. **Changing safety
rules should be hard.** It's not bureaucracy — it's what keeps
the rules real.

---

## The grown-up version

> The `GenerativeBoundary` class (`core/orchestrator/boundary.py`)
> is our platform's compile-time safety mechanism for LLM outputs.
> It encodes four forbidden actions as a closed `ForbiddenAction`
> enum:
>
> - `INFER_PHENOTYPE` — LLMs cannot produce phenotype calls;
>   those originate in the deterministic `PhenotypeEngine` in
>   `anukriti-pgx-core`
> - `OVERRIDE_RECOMMENDATION` — LLMs cannot modify CPIC
>   recommendations; they can only paraphrase them in narrative
> - `BYPASS_VERIFICATION` — LLM-emitted outputs cannot skip the
>   4-engine verification layer (shape / existence / truth /
>   chain, see Module 10)
> - `FABRICATE_CLAIM` — LLMs cannot introduce claims without a
>   backing provenance stamp resolvable in the MCP evidence cache
>
> Violations raise `BoundaryViolation` exceptions that halt the
> run. There is no runtime override — extending or modifying the
> forbidden-action set requires a code change, which requires PR
> review.
>
> The boundary is paired with two consumers:
> `boundary.guard_synthesis()` wraps the narrative-generation
> call; `boundary.guard_planning()` wraps the planner's LLM call.
> Custom allow-lists can be declared per-call site (see
> `tests/unit/test_boundary.py` for 32 tests covering the enum,
> the assert_allowed/is_allowed helpers, custom allow-lists,
> and the guard_synthesis verification gate).
>
> This pattern is an instance of **design-time safety**: the
> contract is enforced by the code shape, not by the AI's
> cooperation or by runtime configuration.

---

## What you learned

Before this module: "AI safety" sounded like wishful thinking or
prompt engineering.

Now: real safety means **building the rules into the code** so the
AI cannot violate them even if it tries. We have four forbidden
actions. Each one is a specific Python check. Each one raises an
exception. None of them can be disabled at runtime.

The raw-egg cabinet is locked. The helpers don't need to remember
the rule. The kitchen remembers it for them.

---

Next up: **[05 — Sharing a Notebook](05-sharing-a-notebook.md)**

Nine helpers working on the same order all need to know what's
been done so far. One agent adds a fact; the next agent needs to
see it. How do we share state without everyone stepping on each
other?
