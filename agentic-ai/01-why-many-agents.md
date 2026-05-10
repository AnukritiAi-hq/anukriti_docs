# 01 — Why Many Agents?

> One giant brain is slower, sloppier, and scarier than many small
> ones.

---

## The Story

Imagine Anu tried to bake alone.

By herself, Anu would have to:

- Mix dough
- Watch the oven
- Frost the cupcakes
- Add sprinkles
- Greet customers
- Take the money
- Clean the counter

If a customer walked in while Anu was elbow-deep in dough, she
might accidentally put flour on their money. If she was watching
the oven and forgot about the frosting, the frosting would melt.
One brain, too many things, everything gets mixed up.

Now imagine the real bakery. **Seven helpers**, each one with a
small, clear job:

- **Dough-mixer** — only mixes dough
- **Oven-watcher** — only watches the oven
- **Froster** (Priya) — only frosts
- **Sprinkler** — only adds sprinkles
- **Greeter** — only talks to customers
- **Cashier** — only takes money
- **Cleaner** — only cleans

Now, no one is juggling too many things. No one puts flour on
money. If the oven-watcher is busy, it doesn't slow down the
frosting. And if a helper makes a mistake, Anu knows **exactly
who** to go talk to.

Many small helpers beat one big helper. Every time.

---

## What this means for computers

A big AI brain can try to do everything. You can ask it a medical
question and it will answer. You can ask it to write a poem and it
will answer. You can ask it to check its own answer and it will
(sometimes) answer.

But when a big brain tries to do everything, three bad things
happen:

1. **It gets confused.** Answering a medical question is different
   from writing a poem. The big brain doesn't always stay in the
   right mode.
2. **It makes mistakes you can't trace.** If the answer is wrong,
   who made the mistake? The "looking things up" part? The
   "thinking" part? The "writing it down" part? They're all
   tangled together.
3. **It can't be told "no."** If you want to say "never invent a
   citation," you have to trust the big brain to listen. A big
   brain doesn't always listen.

**Many small agents** fix all three:

1. Each agent only does one thing, so it **stays in its mode**.
2. If the answer is wrong, you can **point at the specific agent**
   that messed up.
3. Each agent has **small rules it must follow**, enforced by the
   code around it. The agent can't break them even if it wanted
   to.

---

## What we built

Anukriti has a *lot* of small agents. Each one has a name and a
job. Here are the main ones:

| Helper name | What they do |
|-------------|--------------|
| **Orchestrator** | Decides who does what today (the boss) |
| **Population agent** | Knows about different ancestries (SAS, EUR, AFR, EAS, AMR) |
| **CYP2D6 agent** | Only knows about the CYP2D6 gene |
| **CYP2C19 agent** | Only knows about the CYP2C19 gene |
| **HLA-B agent** | Only knows about the HLA-B gene |
| **Evidence agent** | Looks things up in our evidence library |
| **Sufficiency agent** | Checks if we have *enough* evidence to answer |
| **Verification agent** | Double-checks every answer for safety |
| **Narrative agent** | Writes the final explanation for a human to read |

**Nine main agents.** Plus some smaller helpers they call.

Each agent lives in its own folder:

```
anukriti-swarm/
  agents/
    orchestrator/       the boss
    population/         the ancestry expert
    pharmacogene/
      cyp2d6_agent.py   the CYP2D6 specialist
      cyp2c19_agent.py  the CYP2C19 specialist
      hla_b_agent.py    the HLA-B specialist
    evidence/           the lookup helper
    verification/       the double-checker
    narrative/          the explainer
```

Each folder has small files. Nothing is a giant 2000-line
everything-agent. A new agent joining our team can walk in, find
their folder, and know what's expected of them.

---

## Try it yourself

Run this command in a terminal (if you have the swarm repo):

```bash
ls anukriti-swarm/agents/
```

You'll see the list of agents, sorted alphabetically.

Pick one folder. `cd` into it. Type `ls` again. You'll see the
file(s) that define what that agent does.

This is how you read a multi-agent system: **one folder at a
time**.

---

## The grown-up version

> Multi-agent systems (MAS) decompose a complex task into
> specialist agents. Our platform implements this as a "swarm"
> pattern with nine core specialists plus several micro-helpers.
> Each agent has:
>
> - A single-responsibility role (one `BiomedicalContextType`
>   scope)
> - A narrow, typed input contract (frozen Pydantic record
>   `AgentContextEnvelope`)
> - A narrow, typed output contract
> - A closed-enum "scope firewall" at its message-bus subscription
>   (see Module 02)
>
> Benefits over a monolithic agent:
> 1. **Isolated failure modes** — an unsafe verification output
>    doesn't contaminate retrieval logic
> 2. **Independently testable** — each agent has its own unit
>    tests in `tests/unit/`
> 3. **Reviewable scope** — adding a new capability requires a
>    new agent (visible in diff), not a bigger prompt
> 4. **Traceable attribution** — every claim in the final output
>    maps to the agent that produced it
>
> The agent catalog is maintained in `agents/registry/` with
> formal `AgentProfile` records for each specialist.

---

## What you learned

Before this module: AI = one big brain that does everything.

Now: the grown-up way to build AI for a serious job is **many
small agents**, each with one role, talking to each other in a
way you can see and check.

Our bakery has nine core helpers. Yours could have more. Or fewer.
The number isn't the point. The shape is: **small, named, specific**.

---

Next up: **[02 — How Agents Talk](02-how-agents-talk.md)**

Nine helpers in a bakery is great, but what happens when the
froster needs sprinkles from the sprinkler? They need to **talk**.
And talking between agents is a whole art on its own.
