# 00 — What's an Agent?

> A helper who can **decide things** on their own.

---

## The Story

Anu has a new helper at her bakery. Her name is **Priya**.

Priya's job is simple: **frost the cupcakes**.

But Priya isn't a machine that always frosts the same way. Priya
*looks* at each cupcake. If it's a chocolate cupcake, she uses
chocolate frosting. If it's a vanilla cupcake, she uses vanilla
frosting. If it's a birthday cupcake, she adds sprinkles.

Priya doesn't ask Anu every time. Priya has a job, and Priya has
**rules she knows**. She *decides* — by herself — what to do next.

If you ever find yourself thinking "Priya doesn't just *do*
something, Priya *chooses* something," then you've understood what
an agent is.

---

## What this means for computers

In computer code, most helpers are like a toaster. You put bread in,
and it gives you toast. It never chooses. It always does the same
thing.

An **agent** is a different kind of helper. An agent:

1. **Has a job** — one specific thing it's supposed to do
2. **Looks at what's in front of it** — the cupcake, the question,
   the piece of information
3. **Decides** — based on rules it knows, or based on asking a
   smart brain (an LLM) for help
4. **Does** the thing it decided

A toaster follows one path. An agent picks its path.

---

## What we built

In our project **Anukriti**, we have a helper called the
**Pharmacogene Agent**.

Its job is to answer one question: *"What does this person's gene
do to this medicine?"*

When a question comes in like:

> *"For a person with CYP2C19 star-2 slash star-2, does
> clopidogrel work?"*

the Pharmacogene Agent:

1. **Looks at the genes** — "Oh, CYP2C19, I know that one."
2. **Looks up the star alleles** — "Star-2, star-2. Both broken."
3. **Decides** — "This person has a 'Poor Metabolizer' phenotype."
4. **Writes down what it decided, and why.**

It doesn't ask a human. It doesn't ask an LLM. It **knows its job**
and does it.

Other agents have harder jobs — some of them *do* ask LLMs for
help. But every agent in our system has the same shape: a job, a
way of looking, a way of deciding, and a way of writing down what
it did.

You can see the pharmacogene agents in code at:

```
anukriti-swarm/agents/pharmacogene/
```

Three files, three agents — one for CYP2D6, one for CYP2C19, one
for HLA-B. Each one is the same pattern: look, decide, write down.

---

## Try it yourself

If you have the swarm repo cloned, open this file:

```
anukriti-swarm/agents/pharmacogene/cyp2c19_agent.py
```

Don't worry about understanding all the code. Just look for:

- The word `def` — this is how Python says "a job starts here"
- The word `return` — this is how a helper says "I'm done, here's
  my answer"

Count how many times `def` appears. That's roughly how many small
jobs this one agent can do. (Even small agents have several
sub-jobs — like Priya has "frost," "check color," "add sprinkles"
all inside her bigger job.)

---

## The grown-up version

> An **agent** in our system is a class with a well-defined role,
> a structured input contract (a frozen Pydantic record), and a
> structured output contract. Agents are composed at runtime by
> the orchestrator (Module 03) and communicate via the agent bus
> (Module 02). Every agent must preserve the scope firewall — it
> cannot emit outputs outside its declared `BiomedicalContextType`
> enum value, which is checked at message-construction time.
>
> A typical agent:
> - Accepts an `AgentContextEnvelope` with a specific context type
> - Runs its deterministic logic (rule tables, lookups) and/or
>   calls an LLM guarded by the `GenerativeBoundary`
> - Emits one or more envelopes with its results, stamped with
>   provenance
>
> See `agents/base.py` for the base agent interface, and
> `agents/pharmacogene/` for the CYP2D6 / CYP2C19 / HLA-B
> specialists.

---

## What you learned

Before this module: an "AI agent" sounded mysterious.

Now: an agent is just a **helper with a job who can decide**. Not
magic. Not a robot that wakes up and does whatever it wants. A
small piece of code with clear rules, clear inputs, clear outputs,
and room to *choose* the right answer for each specific thing it
sees.

---

Next up: **[01 — Why Many Agents?](01-why-many-agents.md)**

If one agent can decide things, why don't we just build one
really smart agent and call it a day? Anu and her bakery will
help us understand why.
