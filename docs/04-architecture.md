# Module 04 — Architecture

> Prerequisites: [01 What is Anukriti](01-what-is-anukriti.md), [02 The Three Repos](02-the-three-repos.md), [03 Core Concepts](03-core-concepts.md)

---

## The question we're answering

The platform has an unusual shape: deterministic rules at the core,
an LLM at the edge, and a hard runtime barrier between them. Why?
And how does that barrier actually work?

---

## The core invariant

> **No medical claim leaves the system unless it came from
> deterministic rules over verified inputs.**

That's the one sentence. Everything architectural flows from it.

An LLM can write the *explanation* of a claim. An LLM cannot be the
*source* of a claim. The LLM is on the outside of the sandwich; the
deterministic layer is the filling.

---

## Deterministic-first with a generative edge

```
         Input: (drug, gene, population, genotype)
                         │
                         ▼
      ┌─────────────────────────────────────┐
      │  DETERMINISTIC CORE                 │
      │                                     │
      │  ┌─────────────────────────────┐    │
      │  │ pgx-core.PhenotypeEngine    │    │
      │  │   diplotype → phenotype     │    │
      │  │   CPIC-pinned, no LLM       │    │
      │  └─────────────┬───────────────┘    │
      │                ▼                    │
      │  ┌─────────────────────────────┐    │
      │  │ recommendation lookup       │    │
      │  │   phenotype → CPIC text     │    │
      │  └─────────────┬───────────────┘    │
      │                ▼                    │
      │  ┌─────────────────────────────┐    │
      │  │ evidence sufficiency        │    │
      │  │   6 facets · 12 R-rules     │    │
      │  └─────────────┬───────────────┘    │
      │                ▼                    │
      │  ┌─────────────────────────────┐    │
      │  │ verification                │    │
      │  │   4 safety engines          │    │
      │  └─────────────┬───────────────┘    │
      └────────────────┼────────────────────┘
                       │  ← GenerativeBoundary gate
                       ▼     (RAISES on policy violation)
         ┌─────────────────────────────┐
         │  GENERATIVE EDGE (LLM)      │
         │                             │
         │  narrative synthesis only.  │
         │  cannot infer phenotype,    │
         │  override recommendation,   │
         │  bypass verification, or    │
         │  fabricate claim.           │
         └─────────────┬───────────────┘
                       ▼
                Structured output
```

The horizontal line in the middle is the **`GenerativeBoundary`** —
a runtime enforcement mechanism, not a coding convention.

---

## The GenerativeBoundary, concretely

In `anukriti-swarm/core/orchestrator/boundary.py`:

```python
class ForbiddenAction(Enum):
    INFER_PHENOTYPE = "infer_phenotype"
    OVERRIDE_RECOMMENDATION = "override_recommendation"
    BYPASS_VERIFICATION = "bypass_verification"
    FABRICATE_CLAIM = "fabricate_claim"
```

These four actions are what an LLM-driven agent is **forbidden** to
do. If the code path around an LLM call tries to perform one of
these, the boundary raises — the run aborts, nothing leaks to a
user.

Concrete examples of boundary violations:

- **INFER_PHENOTYPE** — An LLM tries to say "a patient with *CYP2C19
  \*2/\*2 is probably a Poor Metabolizer." That's the deterministic
  engine's job. The LLM can *report* that the engine said this; it
  cannot *invent* it.
- **OVERRIDE_RECOMMENDATION** — An LLM tries to say "despite CPIC's
  Strong recommendation to avoid clopidogrel, maybe it's fine." No.
  The recommendation is frozen; the LLM can only paraphrase.
- **BYPASS_VERIFICATION** — An LLM tries to skip a verification
  step to "save time." No. Verification ran or the output doesn't
  leave the system.
- **FABRICATE_CLAIM** — An LLM invents a citation, a study, a trial.
  No. Claims without provenance are blocked.

The boundary's check isn't a warning or a log — it's an exception
that kills the run. There's no "override this once" flag. Disabling
the boundary requires a code change, which triggers review.

---

## The five runtime stages

When you submit a query to the swarm's unified runtime, here's what
actually runs (source: `anukriti-swarm/core/runtime/runtime.py`,
the `SwarmRuntime.run()` method):

| Stage | What | Where | LLM? |
|-------|------|-------|------|
| 1. Context assembly | Parse input into `SwarmExecutionContext` Pydantic record | `core/orchestrator/context_assembler.py` | no |
| 2. Orchestration | Plan (what agents to activate) → Route → Coordinate | `core/orchestrator/planner.py`, `router.py`, `coordinator.py` | **yes** (planner only, fallback is deterministic) |
| 3. Retrieval | Multi-strategy retrieval: dense, population-aware, knowledge graph, diversity selector | `retrieval/multi_strategy/`, `knowledge_graph/` | no |
| 3.5. Sufficiency | 4-layer evidence sufficiency check (optional, off by default) | `core/evidence_sufficiency/` | no |
| 4. Verification | 4 safety engines: shape, existence, truth, chain | `core/verification/` | no |
| 5. Synthesis | Narrative generation via LLM, guarded by `GenerativeBoundary` | `narrative/`, `agents/orchestrator/gemini_orchestrator.py` | **yes** (guarded) |

Observe: of 5 stages, only two use an LLM. The planner uses one to
decide *what to do* (with a deterministic fallback if the LLM is
unavailable). The synthesizer uses one to *write the explanation*
(only after deterministic checks clear).

Everything else — the actual medical decision-making — is
deterministic code.

---

## Closed enums at every boundary

The other major architectural mechanism is **closed enumerations**
at every cross-module contract. Instead of passing strings:

```python
# Fragile — a typo is runtime behaviour
report_type = "clinician_report"
```

We pass enums:

```python
# Sound — unknown values fail at construction
class BiomedicalContextType(Enum):
    POPULATION = "population"
    GENOTYPE = "genotype"
    PHARMACOGENE = "pharmacogene"
    EVIDENCE = "evidence"
    VERIFICATION = "verification"
    CONFIDENCE = "confidence"
    PROVENANCE = "provenance"
```

There are **14 closed enums in the evidence sufficiency layer alone**
(covered in Module 09). Adding a new value to an enum is a code
change — which means a PR, review, and CI — not runtime config.

The effect: **scope drift is impossible without a visible diff.** An
agent can't "become" a generic healthcare chatbot at runtime because
the context types it accepts are a closed set. Extending the set
means changing `BiomedicalContextType`, which means review.

Module 10 goes deeper on how closed enums travel across the
three-repo boundary.

---

## The three architectural rings, mapped to repos

Recall the three concentric rings from Module 01. Here's the
architectural map:

```
                                        ┌─────────────────────────────────────────────┐
                                        │                                             │
                                        │   ┌────────────────────────────────────┐    │
                                        │   │                                    │    │
                                        │   │   ┌──────────────────────────┐     │    │
                                        │   │   │                          │     │    │
                                        │   │   │    pgx-core library      │     │    │
                                        │   │   │  deterministic core      │     │    │
                                        │   │   │  - PhenotypeEngine       │     │    │
                                        │   │   │  - 13 gene callers       │     │    │
                                        │   │   │  - CPIC tables pinned    │     │    │
                                        │   │   │  - zero runtime deps     │     │    │
                                        │   │   │                          │     │    │
                                        │   │   └──────────────────────────┘     │    │
                                        │   │                                    │    │
                                        │   │       anukriti (product)           │    │
                                        │   │  - FastAPI HTTP surface            │    │
                                        │   │  - FHIR clinical export            │    │
                                        │   │  - PDF report generator            │    │
                                        │   │  - drug reranker                   │    │
                                        │   │  - shim layer over pgx-core        │    │
                                        │   │                                    │    │
                                        │   └────────────────────────────────────┘    │
                                        │                                             │
                                        │         anukriti-swarm (research)           │
                                        │   - SwarmRuntime 5-stage lifecycle          │
                                        │   - Evidence sufficiency layer              │
                                        │   - Knowledge graph + multi-hop reasoning   │
                                        │   - MCP persistence layer (6 services)      │
                                        │   - Live FastAPI backend + D3 frontend      │
                                        │   - 4 safety/verification engines           │
                                        │   - GenerativeBoundary enforcement          │
                                        │                                             │
                                        └─────────────────────────────────────────────┘
```

The innermost ring (pgx-core) is the truth layer — pure, pinned,
zero-LLM, zero-network. The outer rings add capability without
compromising the inner. You could pull pgx-core out and use it in
a completely different clinical tool; you couldn't pull the
GenerativeBoundary out of swarm without breaking everything.

---

## Why this shape and not another

Four alternatives we considered and rejected:

### Alt 1 — Pure LLM agent system (no deterministic core)

**Rejected.** A system built entirely on LLM reasoning can
occasionally be right. It cannot be consistently right, because
LLM outputs are probabilistic and sometimes just wrong. For a
pharmacogenomics platform where "wrong" means wrong recommendation
for a real patient, this is disqualifying.

### Alt 2 — Pure deterministic system (no LLM anywhere)

**Rejected, but close.** A platform with no LLM produces correct
structured output but terrible narrative. "CYP2C19 *2/*2 → PM →
avoid clopidogrel" is true but not explainable. Clinicians need to
understand the *why*. That's where narrative synthesis helps — but
only behind the GenerativeBoundary.

### Alt 3 — LLM validates LLM (judge pattern)

**Rejected.** Using an LLM to verify an LLM's output is compounded
hallucination risk. Verification must be deterministic rule-based
(our 4 safety engines, our 12 sufficiency rules, our 10 verifier
rules) so that verification failures are themselves
investigable without asking the same non-determinism that
produced the bug.

### Alt 4 — Soft scope boundaries with config flags

**Rejected.** A feature flag like `enable_general_healthcare_mode`
is a single environment-variable change away from a completely
different product running in production. We make scope a compile-
time fact via closed enums, so production behaviour matches the
code review.

---

## How off-by-default additions work

New capabilities are added via **explicit constructor arguments
defaulting to `None`**, not via feature flags. Example from
`core/orchestrator/coordinator.py`:

```python
class ExecutionCoordinator:
    def __init__(
        self,
        ...,
        sufficiency_checkpoint: SufficiencyCheckpoint | None = None,
    ):
        self.sufficiency_checkpoint = sufficiency_checkpoint

    def execute(self, ...):
        ...
        if self.sufficiency_checkpoint is not None:
            # Step 3.5 runs
            result = self.sufficiency_checkpoint.evaluate(...)
        ...
```

All existing callers construct the coordinator without the
argument. Their behavior is unchanged. Opt-in is a code change at
the call site:

```python
coordinator = ExecutionCoordinator(
    sufficiency_checkpoint=SufficiencyCheckpoint(),
)
```

**This is better than a feature flag** because:

- The default is visible in the signature (no hunting env vars).
- Switching on the feature requires editing code, which triggers review.
- Removing the feature someday is a breaking change, which
  SemVer-flags it appropriately.
- There's no "well, it was enabled in prod but disabled in staging"
  class of bug.

This same pattern is how every new layer enters the runtime.

---

## Summary

You now know:

- The **core invariant:** medical claims come from deterministic
  rules, not LLM output.
- The **`GenerativeBoundary`:** 4 forbidden actions enforced as
  runtime exceptions, not warnings.
- The **5-stage `SwarmRuntime` lifecycle:** only 2 of 5 stages use
  an LLM, and both are guarded.
- **Closed enums everywhere** make scope drift impossible without a
  visible code change.
- **Three rings map to three repos:** truth in pgx-core, product in
  anukriti, research in swarm.
- **Off-by-default via constructor args, not feature flags.**

Next: [Module 05 — Gene Matching](05-gene-matching.md). We walk
through the VCF → diplotype → phenotype pipeline in detail, with a
worked example for Priya's CYP2C19 *2/*2.
