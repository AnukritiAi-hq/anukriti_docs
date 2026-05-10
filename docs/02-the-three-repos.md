# Module 02 — The Three Repos

> Prerequisites: [01 What is Anukriti](01-what-is-anukriti.md)

---

## The question we're answering

Why are there three repos and not one monorepo? Who owns what?
Which repo does a given change belong in?

---

## The three repos at a glance

| Repo | Role | Git host | Release model |
|------|------|----------|---------------|
| [`anukriti-pgx-core`](https://github.com/AnukritiAi-hq/anukriti-pgx-core) | **Library** — deterministic biomedical truth layer | AnukritiAi-hq | SemVer on PyPI |
| [`anukriti`](https://github.com/Abm32/Synthatrial) | **Product** — FastAPI clinical app | Abm32 | Rolling branch (`clinical-grade-pgx`) |
| [`anukriti-swarm`](https://github.com/AnukritiAi-hq/anukriti-swarm) | **Research platform** — multi-agent runtime | AnukritiAi-hq | Rolling `main` |

They sit on your dev machine like this, independent checkouts:

```
<your-workspace>/
├── anukriti-pgx-core/      library (cloned from PyPI source on GitHub)
├── anukriti/               product (clone from Abm32/Synthatrial)
└── anukriti-swarm/         research platform
```

No submodules. No monorepo. Three plain git repos.

---

## Why three repos, not one monorepo?

The three artifacts have genuinely different audiences, release
cadences, and failure modes. Collapsing them into one repo would
force a single release discipline on three things that need
different ones.

### Different audiences

- **pgx-core** ships on PyPI and is consumed by anyone who needs a
  Python pharmacogenomics engine — not just the Anukriti platform.
  Its audience is "any Python developer working in PGx."
- **anukriti** is the clinical product. Its audience is clinicians,
  trial designers, and operations teams who will deploy the FastAPI
  app. They don't care about the library internals; they care about
  the HTTP API and report formats.
- **anukriti-swarm** is the research platform — multi-agent
  orchestration, live UI, experimentation. Its audience is research
  engineers and agent-framework enthusiasts who want to see what a
  production-shaped evidence-governed system looks like.

A monorepo would drag the clinical product's deployment constraints
onto the research platform's experimentation pace, and vice versa.

### Different release cadences

- **pgx-core** releases maybe once a month (CPIC guideline updates,
  new gene callers). Every release is SemVer'd. Consumers pin exact
  versions.
- **anukriti** ships continuously on a branch, deploying to staging
  on every merge. No PyPI release.
- **anukriti-swarm** commits multiple times per day during active
  sessions (you'll see sessions #1-#12 in its status log). It's a
  research codebase; pace is speed, not stability.

### Different failure modes

- If **pgx-core** ships a bug, the downstream blast radius is
  massive — every consumer's regression breaks. Its CI is strict
  (51 pytest + downstream regression gate) because it must be.
- If **anukriti** ships a bug, the product has an outage. Roll back
  the branch.
- If **anukriti-swarm** ships a bug in a research demo, you tweak
  and re-run. Nothing ships to a user.

**The scope of "this changed, therefore that must be re-verified" is
scoped per repo.** That's the design.

---

## How they connect

The three repos aren't independent — they share a common truth
layer. pgx-core is the root. anukriti and anukriti-swarm both
consume it via a **pinned PyPI dependency**.

```
                ┌──────────────────────────────────────┐
                │   anukriti-pgx-core (library)        │
                │   ─ PhenotypeEngine                  │
                │   ─ 13 gene callers                  │
                │   ─ CPIC provenance manifest         │
                │   ─ zero runtime deps                │
                │   ─ no LLM, no randomness            │
                └──────────┬───────────────┬───────────┘
                           │               │
                           │  both consume │
                           │  via pinned   │
                           │  PyPI version │
                           │  (0.2.1)      │
                           ▼               ▼
                ┌─────────────────┐  ┌─────────────────┐
                │ anukriti        │  │ anukriti-swarm  │
                │ (product)       │  │ (research)      │
                │                 │  │                 │
                │ shim layer:     │  │ thin re-export: │
                │ src/*_caller.py │  │ rules/phenotype │
                │ delegates to    │  │ _rules.py       │
                │ pgx-core        │  │ passes through  │
                └─────────────────┘  └─────────────────┘
```

**What "pinned PyPI dependency" means:** both consumer repos have
`anukriti-pgx-core==0.2.1` in their `requirements.txt`. Not
`>=0.2.0`. Exactly `0.2.1`. A new pgx-core release doesn't flow
downstream automatically — a human has to update the pin in a
deliberate PR, run the regression gate, and merge.

**Why pinned exactly, not a range?** Because pgx-core is the
biomedical truth layer. A minor release could theoretically change
a phenotype call (new CPIC table version, corrected edge case). We
want that change to be a deliberate event, not an accidental
transitive upgrade.

---

## Who owns what — a rule of thumb

| If your change affects... | It belongs in... |
|---------------------------|------------------|
| How *a gene* gets called from a VCF | pgx-core |
| How a phenotype maps to a drug recommendation | pgx-core |
| CPIC table versions, allele definitions, provenance | pgx-core |
| FastAPI endpoints, FHIR export, PDF report templates | anukriti |
| Drug reranking logic for *clinical consumption* | anukriti |
| Multi-agent orchestration, agent-to-agent messaging | anukriti-swarm |
| Evidence sufficiency rules, verification engines | anukriti-swarm |
| Knowledge graph, retrieval controllers, MCP persistence | anukriti-swarm |
| Live mission-control UI, D3 visualizations | anukriti-swarm |

If you're not sure, ask: *"Would a third Python user who isn't on
our platform want this?"* If yes, it's probably pgx-core.
*"Would a clinician submitting a report want this?"* Probably
anukriti. *"Is this research instrumentation?"* Probably swarm.

---

## What goes in which — worked examples

### Example 1: Adding a new gene caller (e.g. UGT1A1)

**Where:** pgx-core.

**Why:** The `GeneCaller` pattern is defined there. A new caller
changes the universal biomedical logic; both consumers should get
it at once (via the next version bump). It's not "the anukriti
product's UGT1A1" or "the swarm's UGT1A1" — it's the *UGT1A1
genotype-to-phenotype contract*, which is the library's concern.

### Example 2: Adding a new clinical report field (e.g. CPIC recommendation strength)

**Where:** anukriti (product).

**Why:** How the report renders is product concern. The underlying
data (the recommendation strength) already comes from pgx-core via
the existing recommendation API.

### Example 3: A new verification engine that cross-checks recommendations

**Where:** anukriti-swarm.

**Why:** Verification is a research-platform concern. The outputs
of these engines aren't part of the library's public contract —
they're instrumentation over what the library produces. If a
verification engine matures into something every consumer needs, it
*could* later move to pgx-core. Starting in swarm is lower risk.

### Example 4: Population-aware allele frequency data

**Where:** anukriti-swarm (today) or pgx-core (tomorrow).

**Why:** Today, population frequency data lives in swarm because
it's used for research-grade reasoning. Long term, it might make
sense to move into pgx-core as a new layer — "Layer 3" after
calling and phenotype. This kind of migration is what
`anukriti-pgx-core/PROJECT_CONTEXT.md` §F-5 discusses openly.

---

## The regression contract between repos

Because pgx-core's outputs are consumed by the other two, **every
change to pgx-core must preserve byte-identical outputs downstream
unless a behavior change is documented.**

Specifically, `anukriti-pgx-core/PROJECT_CONTEXT.md` pins these
targets:

| Consumer | Expected output signature |
|----------|---------------------------|
| anukriti biomedical test suite | 353 pass / 1 pre-existing fail |
| anukriti-swarm pinned regression | 12/12 pass + benchmark AGREE |
| swarm `showcase` demo | JSON export **1961 bytes** |
| swarm `safety_demo` | 1 delivered / 4 blocked |
| swarm `interoperability_demo` | 24 envelopes / 24 provenance / 6 scope-rejected |
| swarm `evaluation_demo` | 52/61 suite · 4/4 stress · 3/3 ancestry |
| pgx-core own pytest | 51/51 green |

Before merging any pgx-core PR, you run a script that checks all of
these. The regression contract is what keeps three-repo coordination
from becoming a "breaking downstream" nightmare.

Full regression-gate commands are in `anukriti-pgx-core/PROJECT_CONTEXT.md`.

---

## Why not submodules?

Submodules couple git history across repos. A bump to pgx-core
becomes a commit in the parent repo pointing at a new pgx-core SHA.
That's conceptually fine, but it conflates two different operations
(library release + downstream adoption) into one artifact.

A PyPI pin is cleaner:

- The pin is a **version**, not a SHA. Human-readable.
- The pin is updated by a **deliberate PR**, not a submodule pointer bump.
- The release mechanism (`RELEASING.md`, OIDC trusted publisher) is
  the same for external consumers as it is for anukriti/swarm. No
  two-class system where internal consumers get "just submodule it"
  and external consumers get "check PyPI."
- Cloning any one repo doesn't require fetching the others.

Submodules are a good solution when repos share history. These three
don't — they share a *contract*, not a history.

---

## Why this shape is good for scale

A platform that hires 5-10 more engineers needs to let them work
without stepping on each other. Three repos gives:

- **Parallel streams of work.** The product team can ship a new FHIR
  export while the research team refactors the agent bus, without a
  single rebase conflict.
- **Isolated blast radius.** A bug in the swarm UI doesn't block a
  product deployment. A bug in pgx-core blocks both — which is
  appropriate, because that's the truth layer, and we want humans in
  the loop for truth-layer changes.
- **Clean ownership.** "Who owns the phenotype engine?" is pgx-core.
  Not ambiguous.
- **External contribution paths.** External pharmacogenomics
  contributors can PR pgx-core without needing to understand the
  FastAPI product or the agent framework. Low barrier to entry at
  the point that matters most.

---

## Summary

You now know:

- **Three repos, not one:** because three artifacts have different
  audiences, release cadences, and failure modes.
- **pgx-core is the root:** library on PyPI, consumed by pinned
  version.
- **Rule of thumb for "where does this change go?":** ask who
  benefits and what's the release cadence.
- **Regression contract:** pgx-core changes must preserve downstream
  signatures byte-identically.
- **Not submodules:** versions beat SHAs for release discipline.

Next: [Module 03 — Core Concepts](03-core-concepts.md). We take a
break from the engineering story to build up the biomedical
vocabulary we'll need from Module 04 onward.
