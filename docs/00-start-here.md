# Module 00 — Start Here

> You are here. This module tells you how to read the rest of the
> course and what you need to know before starting.

---

## What this course is

A 13-module learning path that takes you from "what is Anukriti?"
to "I understand the architecture well enough to contribute to it."
Each module stands on its own, but they're ordered so each one can
assume what came before.

This is **not** an API reference. It's **not** a demo walkthrough.
It's the story of why the platform looks the way it looks, and what
guarantees it makes. API references live in each repo's own
documentation (pointers in [Module 13](13-further-reading.md)).

---

## Who this is for

You don't need to be a biologist. You don't need to be a clinician.
You do need:

- **Basic programming literacy.** You've written Python, or you can
  read it. You understand what "type annotation" means.
- **Rough idea of what DNA is.** Double helix, letters A-C-G-T, genes,
  variation across people. If that sentence was new to you, skim
  [Module 03](03-core-concepts.md) slowly — that's where we build up
  the biological vocabulary.
- **Comfort with ambiguity.** Pharmacogenomics is a field where the
  truth often reads "we know this sometimes, for some people,
  conditional on ancestry." That uncertainty is the point.

If you're a clinician reading this because you want to evaluate
whether the platform is trustworthy, skip the code-level modules
on your first pass. Modules [01](01-what-is-anukriti.md),
[06](06-why-deterministic.md), and [09](09-evidence-and-safety.md)
are what you want.

---

## Prerequisites by module

Most modules have a "Prerequisites" line at the top. Here's the
summary:

| Module | Assumes you've read |
|--------|---------------------|
| 00 Start Here | (nothing) |
| 01 What is Anukriti | 00 |
| 02 The Three Repos | 01 |
| 03 Core Concepts | 01 (not 02 — biomedical prerequisites) |
| 04 Architecture | 01, 02, 03 |
| 05 Gene Matching | 03, 04 |
| 06 Why Deterministic | 04, 05 |
| 07 Tech Stack | 02, 04 |
| 08 Population Awareness | 03, 05 |
| 09 Evidence and Safety | 04, 05, 06 |
| 10 How the Pieces Talk | 02, 04, 07 |
| 11 Hands-On | 02, 04 (and Docker installed) |
| 12 Glossary | (skip around as needed) |
| 13 Further Reading | any module |

The straight 00 → 13 path satisfies every prerequisite. Branching
paths (e.g. clinician route: 00 → 01 → 06 → 09) work because those
later modules spell out what they depend on.

---

## How to read a module

Each module has this shape:

```
# Title
> One-sentence framing

## The question we're answering
What problem does this module solve?

## Concepts
The minimum vocabulary for this topic.

## How it actually works
The mechanism, with code references.

## Why we chose it this way
The alternatives we rejected, and why.

## Summary
One paragraph recap. A few "you should now understand..." bullets.

## Further reading
Pointers into the real repos.
```

Read the "Question" and "Summary" first if you want to skim. Read
"How it actually works" and "Why we chose it this way" when you
want the substance. "Concepts" is where the heavy lifting happens
for the foundation modules (03, 04, 06).

---

## Conventions in these docs

**Code in monospace.** File paths, identifiers, CLI commands.

**Emphasis on scope boundaries.** When we say "Anukriti is NOT an
EHR system," we mean it's a hard limit enforced in code via closed
enums, not a soft positioning statement. Pay attention to the
"NOT" lists — they're as informative as the "is" lists.

**Running example.** We keep returning to the same scenario:
*"A South Asian patient, CYP2C19 *2/*2 genotype, being considered
for clopidogrel."* Real clinical scenario, real population gap,
real CPIC recommendation. Every module grounds its abstraction
in this example where possible.

**Honest limitations.** We say what we don't know. We say where the
evidence is thin. If a module ends with "and we refuse to synthesize
a recommendation because the evidence is insufficient" — that's a
feature of the platform, not a gap in the docs.

---

## Where to go for help

**These docs aren't clear.** Open an issue at this repo with the
module number and the confusing passage. We want to fix documentation
debt before you go ask someone on Slack.

**The code doesn't match these docs.** Also file an issue. Docs that
drift from reality are a bigger problem than missing docs — they
actively mislead. Our commitment is that an assertion in these
modules is either true of `main` today, or it's flagged with
"(Planned)" or "(Historical)."

**You want to contribute a module.** Read the README contribution
section. The short version: module numbers are stable; new modules
get letter-suffix numbers (`07a`, `05b`) to avoid breaking links.

**Your question is about biology, not engineering.** Module
[03](03-core-concepts.md) is your friend, and
[12 Glossary](12-glossary.md) has a terms table. Beyond that, the
CPIC website (<https://cpicpgx.org>) and PharmVar (<https://pharmvar.org>)
are the canonical external resources.

**Your question is clinical.** These docs cannot answer clinical
questions. The platform itself is a research tool. For actual
clinical decisions, consult a pharmacogenomics-trained pharmacist
or clinical geneticist.

---

## Summary

You now know:

- These docs are a 13-module progressive path, not a reference.
- You need Python literacy and a willingness to learn biology as
  you go.
- Each module builds on what came before in a specific order.
- We'll keep returning to the SAS + clopidogrel example.
- "What Anukriti is NOT" is a first-class concept, enforced in code.

Next: [Module 01 — What is Anukriti](01-what-is-anukriti.md).
