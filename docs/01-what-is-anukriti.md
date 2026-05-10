# Module 01 — What is Anukriti

> Prerequisites: [00 Start Here](00-start-here.md)

---

## The question we're answering

Why does this project exist? What problem does it solve, and what
problem does it **refuse** to solve?

---

## The problem, in one statistic

**14% of South Asians cannot activate clopidogrel.**

Clopidogrel is one of the most prescribed drugs on earth. It prevents
heart attacks in people who've already had cardiac events. It works by
getting converted, inside the body, into an active form — and that
conversion depends on an enzyme called CYP2C19.

If you have two non-functional copies of the *CYP2C19* gene, the
conversion doesn't happen. The drug is inert for you. You think
you're on cardioprotection; you actually have no protection at all.

The rate of this genotype varies enormously by ancestry:

| Population | *CYP2C19 \*2/\*2* (Poor Metabolizer) |
|------------|--------------------------------------|
| European (EUR) | ~2% |
| East Asian (EAS) | ~12% |
| **South Asian (SAS)** | **~14%** |
| African (AFR) | ~4% |

Clinical guidelines from CPIC (Clinical Pharmacogenetics
Implementation Consortium) recommend alternative antiplatelet drugs
— prasugrel or ticagrelor — for poor metabolizers. **That guideline
has existed since 2011.** Yet most prescribing workflows still treat
all populations the same way.

That's the gap Anukriti exists to close.

---

## The mission

> *Population-aware pharmacogenomic risk analysis before clinical trials.*

Three words matter in that sentence:

- **Population-aware.** Ancestry isn't metadata on a patient record;
  it's a first-class input to reasoning. Same gene, same drug,
  different population, different answer. We'll unpack this in
  [Module 08](08-population-awareness.md).
- **Pharmacogenomic.** We reason about drug-gene interactions using
  published, versioned clinical guidelines (CPIC primarily). Not
  invented relationships. Not LLM guesses. Not "what a chatbot
  thinks." Pinned tables from a real clinical authority.
- **Before clinical trials.** The platform is positioned upstream of
  the clinic — helping researchers stratify trial populations,
  helping drug-development teams see which genotypes to enrich or
  exclude, helping clinicians *prepare* for a pharmacogenomic
  decision. **Not making the decision itself.**

---

## What Anukriti is

At the core, Anukriti is a **deterministic phenotype engine** —
code that takes:

```
{gene, allele_1, allele_2}      e.g. ("CYP2C19", "*2", "*2")
```

...and produces:

```
{phenotype, activity_score, cpic_table_version, recommendation}
```

...every single time, for the same input, with an explicit CPIC
guideline citation.

Wrapped around that engine is a multi-agent reasoning system that
can answer richer questions: *"Given this genotype, this population,
this drug, and this available evidence, what should we conclude —
and if nothing, why not?"*

And wrapped around that is a FastAPI product plus a live
mission-control UI that makes the whole thing inspectable.

You'll meet each of these layers in the next few modules. For now,
the mental model is **three concentric rings**:

```
        ┌─────────────────────────────────────────┐
        │  Research platform (anukriti-swarm)     │
        │  multi-agent reasoning, live UI         │
        │                                         │
        │   ┌─────────────────────────────────┐   │
        │   │  Clinical product (anukriti)    │   │
        │   │  FastAPI app, FHIR, reports     │   │
        │   │                                 │   │
        │   │   ┌─────────────────────────┐   │   │
        │   │   │ Library (pgx-core)      │   │   │
        │   │   │ deterministic engine    │   │   │
        │   │   │ CPIC-pinned rules       │   │   │
        │   │   └─────────────────────────┘   │   │
        │   └─────────────────────────────────┘   │
        └─────────────────────────────────────────┘
```

The innermost ring is the truth layer. Everything else is
composition on top.

---

## What Anukriti is NOT

This list is as important as the "what it is" list. We enforce these
boundaries in code via closed enums and scope firewalls — see
[Module 04](04-architecture.md) and [Module 10](10-how-the-pieces-talk.md).

- **Not a chatbot.** There's no free-form conversational interface.
  You submit a structured query; you get a structured response.
- **Not an EHR system.** We don't store patient records. We don't
  track appointments. We don't replace clinical-workflow software.
- **Not a generic RAG framework.** The retrievers are
  pharmacogenomics-specific. Closed-enum context types reject
  off-scope queries at the type boundary.
- **Not a clinical decision-making tool.** We produce evidence
  summaries and risk stratifications. A clinician decides.
- **Not an LLM-as-judge system.** Verification uses deterministic
  rule tables, not LLM evaluation of other LLM outputs.
- **Not a GraphRAG engine.** We have a knowledge graph, but it's
  pharmacogenomics-specific with 10 closed node kinds and 7 closed
  edge kinds. It's not a general-purpose graph.

Every one of these "not" statements has cost us features we
could plausibly have added. Every one is a deliberate choice to
stay narrow — because **broader scope means more places for
hallucinations to sneak in.**

---

## The running example

You'll see this scenario throughout the docs:

> *Priya is a 58-year-old woman of South Asian descent. She's just
> had a cardiac event and her cardiologist is considering clopidogrel
> as part of her secondary-prevention regimen. Her genome-sequencing
> report shows CYP2C19 \*2/\*2 — both copies of the gene carry the
> \*2 variant.*

Anukriti's pipeline for Priya:

1. **Genotype → phenotype.** CYP2C19 \*2/\*2 → activity score 0.0
   → Poor Metabolizer. (Module 05.)
2. **Phenotype + drug + population → recommendation.** CPIC 2022.1
   says: *"Avoid clopidogrel; use prasugrel or ticagrelor instead."*
   Evidence level: Strong. Citation: PMID:34032273. (Module 06.)
3. **Population context.** SAS has ~14% frequency for this
   genotype. The recommendation is strengthened (not weakened) by
   ancestry. (Module 08.)
4. **Evidence sufficiency check.** Coverage of 6 facets (allele,
   phenotype, CPIC, population, recommendation, conflict-free) all
   green. Decision: SUFFICIENT. (Module 09.)
5. **Verification.** 4 safety engines pass (shape, existence, truth,
   chain). Provenance chain is complete. (Module 09.)
6. **Narrative synthesis.** An LLM writes the explanation, but
   only after every deterministic check has cleared, and the
   `GenerativeBoundary` prevents it from inventing new facts.
   (Module 04.)

That's the happy path. We'll also walk through cases where the
platform **refuses** to synthesize — honest abstentions when the
evidence isn't good enough. (Module 08 covers the AFR + CYP2D6
scenario, which is a real-world evidence gap, not a bug.)

---

## Why the platform exists

Beyond the specific clopidogrel example, Anukriti is an
infrastructure bet on a claim:

> **Medical claims made by software must be traceable to
> deterministic rules over verified inputs.**

An LLM that "knows" clopidogrel is contraindicated for CYP2C19 \*2/\*2
is not good enough. An LLM that *sometimes* invents a drug-gene
interaction that doesn't exist is unacceptable — and every LLM
sometimes does this.

The alternative is to put the medical truth layer in code, pin it
to published clinical guidelines by version, and let LLMs only
write narrative *after* the deterministic layer has reached a
conclusion. That's the shape of Anukriti.

[Module 04](04-architecture.md) is where we build out this
architecture in detail. [Module 06](06-why-deterministic.md) is
where we go deep on the safety argument.

---

## Summary

You now know:

- **The problem:** population-blind pharmacogenomics fails real
  patients, e.g. 14% of South Asians on clopidogrel.
- **The mission:** population-aware, deterministic, pre-trial risk
  analysis — not clinical decision-making.
- **The shape:** three concentric rings — library, product, research
  platform — each replaceable, all built on one deterministic core.
- **The scope firewall:** everything Anukriti is NOT, enforced in
  code.
- **The running example:** Priya, CYP2C19 \*2/\*2, SAS, clopidogrel.

Next: [Module 02 — The Three Repos](02-the-three-repos.md).
