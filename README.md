# Anukriti Docs

> **Learning content for the Anukriti platform.** Two complementary
> courses: one engineering-depth, one friendly-intro. Pick the
> one that fits how you read best.

---

## Two courses, one platform

| Course | Style | What you get | Length |
|--------|-------|--------------|--------|
| **[Engineering course](docs/)** (this one) | Technical, detailed | Architecture, gene matching, tech-stack reasoning, request flow | 14 modules · ~2 hours |
| **[Agentic AI course](agentic-ai/)** | Friendly, story-based | Agent concepts explained via a baker and her helpers, with a "grown-up version" at the end of each module | 15 modules · ~1.5 hours |

Both cover the same platform. The engineering course goes deeper on
architecture and tech choices; the agentic-AI course goes deeper on
the multi-agent patterns, LLM safety, and the **why** of each AI
building block. Read one, read both, or bounce between them as your
interest shifts.

---

## 30-second pitch

**Anukriti is a three-repo platform that tells you whether a drug will
work for a specific person, based on their genes and ancestry —
without hallucinating.** It's built around one non-negotiable rule:
medical facts come from deterministic code running against pinned
clinical guidelines, never from an LLM guessing.

- **The real problem:** 14% of South Asians can't activate clopidogrel
  (a common heart-attack-prevention drug). Current clinical workflows
  prescribe it the same way across all populations. That's wrong for
  an entire continent.
- **Our answer:** A phenotype engine that speaks CPIC-versioned
  guidelines, a multi-agent runtime that reasons with full provenance,
  and an explicit refusal vocabulary when the evidence isn't good
  enough to say anything.

---

## Who these docs are for

| You are... | Start with |
|------------|------------|
| A new engineer joining the team | [engineering 00 → 13](docs/) in order |
| A curious learner (or teaching someone) | [agentic-ai course](agentic-ai/) — stories first |
| A clinician or geneticist evaluating us | [engineering 01](docs/01-what-is-anukriti.md) + [06](docs/06-why-deterministic.md) + [09](docs/09-evidence-and-safety.md) |
| A contributor looking for a good first PR | [engineering 00](docs/00-start-here.md) + [02](docs/02-the-three-repos.md) + [11](docs/11-hands-on.md) |
| A reviewer or investor who needs the quick shape | [engineering 01](docs/01-what-is-anukriti.md) + [04](docs/04-architecture.md) + [07](docs/07-tech-stack.md) |
| Someone who wants to understand how AI agents really work | [agentic-ai course](agentic-ai/) — 15 modules, builds up from scratch |
| Stuck on a specific term | [engineering glossary](docs/12-glossary.md) or [agentic-ai glossary](agentic-ai/glossary.md) |

Each module in either course takes about 5-10 minutes to read. The
engineering course is roughly 2 hours; the agentic-ai course is
roughly 1.5 hours.

---

## Reading order

### Engineering course (`docs/`)

```
00 Start Here                 prerequisites, how to use these docs
01 What is Anukriti           the real-world problem, mission, scope firewall
02 The Three Repos            pgx-core / anukriti / swarm — who owns what
03 Core Concepts              pharmacogenomics primer (for non-biologists)
04 Architecture               deterministic + generative, the safety invariant
05 Gene Matching              VCF → diplotype → phenotype, worked example
06 Why Deterministic          the safety argument, how we enforce it in code
07 Tech Stack                 every choice with justification
08 Population Awareness       ancestry as a first-class reasoning dimension
09 Evidence and Safety        sufficiency layer, verification, named refusals
10 How the Pieces Talk        request flow across the three repos
11 Hands-On                   docker compose up; walking through a run
12 Glossary                   terms a newcomer won't know
13 Further Reading            deep-link index into each repo
```

Modules 00-02 are orientation. Modules 03-06 are the biomedical and
architectural foundation. Modules 07-10 are the engineering substance.
Modules 11-13 are practical and reference material.

### Agentic AI course (`agentic-ai/`)

```
00 What's an Agent?                a helper who can decide things
01 Why Many Agents?                why we don't use one big brain
02 How Agents Talk                 sending notes on a paper airplane
03 Who Tells Them What to Do?      the boss who gives out chores
04 The Safety Line                 a rule no helper can break
05 Sharing a Notebook              everyone writes in the same book
06 Remembering Things              learning from last time
07 Finding Information             looking things up the smart way
08 Walking a Map                   following arrows to find a friend
08a Treating Everyone Fairly       what "population-aware" actually means
09 Using Tools                     when a helper needs a hammer
10 Checking the Work               the double-checker
11 Knowing When to Say No          when "I don't know" is the right answer
12 Watching the Agents             a movie of what just happened
13 What We've Built                the whole picture
14 Where to Go Next                finding the real files to read
```

Modules 00-04 are the foundation. Modules 05-08 are the "how agents
work together" mechanics. Modules 09-12 are safety, tools, and
observability. Modules 13-14 are the wrap-up.

You can skip around in either course after your first pass, but
first-time readers should go in order — each module assumes the
previous ones.

---

## The three repos these docs describe

| Repo | Role |
|------|------|
| [`anukriti-pgx-core`](https://github.com/AnukritiAi-hq/anukriti-pgx-core) | Deterministic biomedical truth layer. Published on PyPI. |
| [`anukriti`](https://github.com/Abm32/Synthatrial) | FastAPI product — clinical PGx reports, FHIR, drug reranker. |
| [`anukriti-swarm`](https://github.com/AnukritiAi-hq/anukriti-swarm) | Research platform — multi-agent runtime + live mission control. |

The canonical "what is the Anukriti platform" map lives at
[`anukriti-pgx-core/PLATFORM.md`](https://github.com/AnukritiAi-hq/anukriti-pgx-core/blob/main/PLATFORM.md).
These docs are the **learning path** into it.

---

## Contributing to these docs

Found a confusing passage? Open a PR. The bar is "would a new hire
understand this on first read?" — if the answer is no, fix it.
Small corrections don't need issues; larger restructures should
open one first.

Module numbers are stable — renumbering breaks links. If you add a
new module, pick a number that fits the existing flow (e.g. a new
tech-stack deep-dive becomes `07a-fastapi-choices.md`, not a
renumber of 08+).

---

## License

Apache 2.0. See [LICENSE](LICENSE).
