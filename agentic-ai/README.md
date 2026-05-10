# Agentic AI — A Friendly Course

> A course that explains **how AI agents work** using simple words,
> everyday stories, and real code from the Anukriti platform.
>
> Written so a curious 6-year-old can follow along, but with a
> "grown-up version" at the end of each module so anyone can
> graduate to the real docs.

---

## What "agentic AI" means (in 10 seconds)

You know how a *video* is just many pictures shown quickly?

**Agentic AI** is just "many small smart helpers" working together,
each doing one job, talking to each other, and checking each
other's work — instead of one giant AI trying to do everything
alone.

Our project, **Anukriti**, is built this way. We have many small
smart helpers. Each one has a name and a job. Together they answer
a hard question: *"Will this medicine work for this person?"*

This course explains **how we built them**, one idea at a time.

---

## Who this course is for

- **A curious 6-year-old** — someone who likes stories and wants to
  know how computers think. Each module has a story.
- **A student** — someone learning about AI who wants to see a real
  system, not a toy example.
- **A new engineer on our team** — someone who's heard the words
  "agent" and "orchestrator" and wants to know what they really
  mean in our code.
- **A parent or teacher** — someone reading these modules aloud
  with a child, or using them to explain AI to a class.

---

## How to read a module

Every module has the same shape. It's like a little book chapter:

```
1. The Story              A short story with no computer stuff
2. What this means for computers   The story mapped to code
3. What we built          The real thing in our project
4. Try it yourself        One small thing to play with
5. The grown-up version   One paragraph with the real technical name
```

Read part 1 to feel the idea. Read parts 2 and 3 to see the idea
in our project. Part 4 is for doing. Part 5 is there if you want
to know what grown-ups call it.

You can skip part 5 completely and still understand everything.
You can read *only* part 5 if you're a busy engineer and already
know the idea.

---

## The modules (in reading order)

```
00  What's an Agent?                a helper who can decide things
01  Why Many Agents?                why we don't use one big brain
02  How Agents Talk                 sending notes on a paper airplane
03  Who Tells Them What to Do?      the boss who gives out chores
04  The Safety Line                 a rule no helper can break
05  Sharing a Notebook              everyone writes in the same book
06  Remembering Things              learning from last time
07  Finding Information             looking things up the smart way
08  Walking a Map                   following arrows to find a friend
09  Using Tools                     when a helper needs a hammer
10  Checking the Work               the double-checker
11  Knowing When to Say No          when "I don't know" is the right answer
12  Watching the Agents             a movie of what just happened
13  What We've Built                the whole picture
14  Where to Go Next                finding the real files to read
```

Plus a [Glossary](glossary.md) that explains every word a grown-up
might say.

---

## Meet Anu, the baker

Almost every module has a little story about **Anu, who runs a
bakery**. Anu's bakery is a lot like our AI system.

- Anu doesn't bake alone. She has **helpers** — one for dough, one
  for frosting, one who watches the oven, one who tastes everything.
- The helpers have to **talk to each other** without getting in the
  way.
- There's a **boss** who decides who does what today.
- There are **rules** nobody is allowed to break (like "no tasting
  raw eggs").
- Sometimes a helper **doesn't know something** and has to look it
  up in a book.
- At the end of the day, Anu **writes down** what happened so
  tomorrow's bakery can do better.

That's what our AI system does too. Just with questions about
medicine instead of cakes.

---

## A note to the grown-ups

The project this course describes is **Anukriti** — a three-repo
platform for population-aware pharmacogenomic reasoning. The
"agentic AI" parts live mostly in
[`anukriti-swarm`](https://github.com/AnukritiAi-hq/anukriti-swarm).

If you want the engineer-level view of the same platform, see the
main [`anukriti_docs`](../README.md) course (14 modules covering
architecture, gene matching, deterministic safety, tech stack). This
course is the **agentic-AI-specific** companion — it explains the
multi-agent, LLM-orchestration, tool-use, and verification patterns
in simple language, with concrete pointers to our code.

Concepts covered (with their formal names, for search):

- **Agents** and **agent roles**
- **Multi-agent systems** (swarm pattern)
- **Agent-to-agent (A2A) communication**
- **Orchestration** (planner / router / coordinator)
- **LLM guardrails** (our `GenerativeBoundary`)
- **Shared execution context**
- **Agent memory** (episodic + cross-run)
- **Retrieval-augmented generation (RAG)**, multi-strategy
- **Knowledge graph reasoning**, multi-hop
- **Tool use** via the **Model Context Protocol (MCP)**
- **Verification engines**, evidence grounding, safety constraints
- **Evidence sufficiency**, honest refusals with rule IDs
- **Observability and replay**

Every module ties a concept to at least one real file or class in
the swarm codebase. Readers who finish this course should be able
to open the swarm repo and recognize what they're looking at.

---

## Let's start

Begin with **[00 — What's an Agent?](00-whats-an-agent.md)**

If you get stuck, jump to the [Glossary](glossary.md).

If you want to build something with these ideas, skip to
**[14 — Where to Go Next](14-where-to-go-next.md)**.
