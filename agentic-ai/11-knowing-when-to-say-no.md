# 11 — Knowing When to Say No

> *"I don't know yet"* is a **feature**. Better than a confident
> wrong answer. And always traceable to a named rule.

---

## The Story

A customer asks Anu: *"Can you make a cake for my friend? She's
allergic to gluten, eggs, dairy, nuts, soy, and anything
processed."*

Anu could try. She could probably hack together something. But
if she's honest, she doesn't have a tested recipe for all six
allergens at once. She could make the customer sick.

So she says: *"I can't do this today. Let me explain why —
specifically: we don't have a nut-free station, and that's the
biggest risk. Would you like to come back next week when I've
sourced nut-free equipment?"*

That's **not a failure**. That's **honest competence**.

Contrast with a cake shop that takes the order anyway, feeds the
allergic friend, and the friend ends up in the hospital. That
shop is worse than Anu's. They answered when they shouldn't have.

AI systems face the same choice on every question: *do I know
enough to answer safely, or should I politely refuse and say
why?*

---

## What this means for computers

Before our system answers a question, it asks:

1. **Do we have enough evidence** to answer? (coverage)
2. **Can the evidence resolve to specific sources?** (provenance)
3. **Does the evidence agree with itself?** (conflict-free)
4. **Is the population context good enough** for this specific
   patient?

If any of these is weak, the system **refuses** — but with a
specific, named reason. Not "error." Not "I don't know." A
**structured refusal record** with a **rule ID** and a
**suggestion** for what would fix it.

We call this the **Evidence Sufficiency Layer**. It has three
rule tables with 12 + 10 + 9 = **31 rules** that decide what to
do when evidence is weak.

---

## What we built

The Evidence Sufficiency Layer lives at:

```
anukriti-swarm/core/evidence_sufficiency/
  coverage/claim_coverage.py        — 6 closed "facets"
  conflict/agent.py                  — 3 closed "conflict kinds"
  sufficiency/decision_engine.py     — the 12 R-rules
  verifier/set_level.py              — the 10 V-rules
  uncertainty/engine.py              — the 9 U-rules
  uncertainty/bias_detector.py       — 3 bias kinds
  trace.py                           — the frozen audit record
  checkpoint.py                      — the façade the orchestrator uses
```

### The 6 facets of coverage

For each answer, we check 6 **facets** of evidence:

```
ClaimEvidenceFacet:
  ALLELE          — do we have evidence about this allele?
  PHENOTYPE       — do we have a phenotype call?
  CPIC            — do we have CPIC guideline coverage?
  POPULATION      — do we have population-specific evidence?
  RECOMMENDATION  — do we have a drug recommendation?
  CONFLICT_FREE   — are all signals consistent?
```

Each facet has a **state**: `COVERED`, `UNCERTAIN`, or `MISSING`.

A full "coverage picture" is 6 facets × 3 possible states.

### The 12 R-rules (Decision rules)

The R-rules look at the coverage picture and decide **what to
do**:

```
R1   hard conflict OR conflict_free MISSING        -> BLOCK
R2   PHENOTYPE MISSING                             -> BLOCK
R3   RECOMMENDATION MISSING                        -> BLOCK
R4   provenance incomplete                         -> ABSTAIN
R5   POPULATION MISSING                            -> ESCALATE
R6   CPIC MISSING                                  -> REQUEST_MORE
R7   ALLELE MISSING                                -> REQUEST_MORE
R8   RECOMMENDATION UNCERTAIN                      -> DOWNGRADE
R9   POPULATION UNCERTAIN                          -> DOWNGRADE
R10  any other UNCERTAIN                           -> DOWNGRADE
R11  CONFLICT_FREE UNCERTAIN (soft conflict only)  -> PASS_WITH_CAVEAT
R12  all clean                                     -> SUFFICIENT
```

**Priority ordered.** R1 beats R2 beats R3 etc. First match wins.
This means every refusal cites exactly one rule.

### The 10 V-rules (Verdict rules)

The V-rules produce a **verdict** (a set-level evidence
assessment):

```
V1   named AVOID/USE invertor        -> REFUTED
V2   other hard conflict             -> CONFLICTING
V3   PHENOTYPE missing               -> INSUFFICIENT
... (V4-V9)
V10  all clean                       -> SUPPORTED
```

5 verdicts: SUPPORTED, REFUTED, INSUFFICIENT, CONFLICTING, UNCERTAIN.

### The 9 U-rules (Uncertainty rules)

The U-rules produce an **uncertainty tier**:

```
U1   hard conflict                       -> UNSAFE
U2   missing non-conflict facet          -> HIGH
... (U3-U8)
U9   otherwise                           -> LOW
```

4 tiers: UNSAFE, HIGH, MODERATE, LOW.

### The bias detector

Alongside R/V/U, the **Population Evidence Bias Detector** checks
for 3 specific bias patterns:

- **EUROCENTRIC_IMBALANCE** — target is non-EUR, but all evidence
  is from EUR
- **ANCESTRY_SCARCITY** — target allele count is less than half
  the best-represented population's
- **UNSUPPORTED_EXTRAPOLATION** — POPULATION UNCERTAIN and target
  has zero frequency data

### A refusal isn't an error — it's a record

When the system refuses, it returns a **frozen
`EvidenceSufficiencyTrace`**:

```python
trace = EvidenceSufficiencyTrace(
    claim_id="clopidogrel_sas_example",
    coverage=<6 facet states>,
    provenance=<4 provenance dimensions>,
    conflicts=(<any conflicts found>,),
    decision=SufficiencyDecision.DOWNGRADE,  # R9 fired
    verdict=EvidenceVerdict.UNCERTAIN,        # V7 fired
    uncertainty=UncertaintyScore.HIGH,        # U3+U5 fired
    bias_findings=(ANCESTRY_SCARCITY,),
    uncertainty_transitions=(...),
)
```

An auditor 6 months later can ask: *"Why was this refused?"* and
get back the exact trace with rule IDs, what was missing, what
was suggested. No reconstruction needed. No "log files lost."

### Honest refusals in action — the AFR case

One of our canonical test scenarios:

> *"Codeine + CYP2D6 + African ancestry — recommendation?"*

Expected answer: **we refuse to synthesize.**

Why? Because AFR has less published evidence for CYP2D6 than
other populations. The bias detector flags
`ANCESTRY_SCARCITY`. R9 fires (POPULATION UNCERTAIN →
DOWNGRADE). The result is a downgraded recommendation with a
pinned banner:

> *"Downgrade — ancestry scarcity in AFR for CYP2D6. Evidence
> density below threshold. Will not synthesize a strong
> recommendation."*

**We don't invent a plausible-sounding answer from EUR data.**
That's the feature. A general LLM would produce a confident
answer derived from implicit EUR priors. Our system doesn't.

The refusal is an **operating signal**, not a bug.

### Off by default

Like several of our advanced capabilities, the sufficiency layer
is **opt-in**. The flagship demos don't construct the coordinator
with the sufficiency checkpoint. They behave exactly as they did
before the sufficiency layer existed.

To turn it on:

```python
coordinator = ExecutionCoordinator(
    sufficiency_checkpoint=SufficiencyCheckpoint(),
)
```

When enabled, the checkpoint runs as **Stage 3.5** in the
orchestrator pipeline, between retrieval and verification.

---

## Try it yourself

Run the abstention demo:

```bash
python -m demos.evidence_sufficiency_abstention_demo
```

Six scenarios, six named refusals:

```
1 no phenotype        block         (R2)
2 avoid vs use clash  block         (R1 + V1)
3 broken provenance   abstain       (R4)
4 population missing  escalate      (R5)
5 AMR bias signals    downgrade     (3 bias kinds)
6 adaptive ABORT      request_more  (budget exhausted)
```

Every ✗ cites a specific rule. Compare this to "Error: unknown"
or "Sorry, couldn't find that" from a generic chatbot. Named
refusals are **informative refusals**.

---

## The grown-up version

> The **Evidence Sufficiency Layer** (`core/evidence_sufficiency/`,
> 18 files, session #6 of swarm) is the platform's deterministic
> rule-based answer-or-not gate. Three parallel rule tables
> derived from the same signals:
>
> - **12 R-rules** in `SufficiencyDecisionEngine` → 7-value
>   `SufficiencyDecision` enum (SUFFICIENT, PASS_WITH_CAVEAT,
>   DOWNGRADE, REQUEST_MORE, ESCALATE, ABSTAIN, BLOCK)
> - **10 V-rules** in `SetLevelEvidenceVerifier` → 5-value
>   `EvidenceVerdict` enum (SUPPORTED, REFUTED, INSUFFICIENT,
>   CONFLICTING, UNCERTAIN)
> - **9 U-rules** in `UncertaintyScoringEngine` → 4-tier
>   `UncertaintyScore` enum (UNSAFE, HIGH, MODERATE, LOW)
>
> Plus the `PopulationEvidenceBiasDetector` with 3 closed
> `BiasKind` values (EUROCENTRIC_IMBALANCE, ANCESTRY_SCARCITY,
> UNSUPPORTED_EXTRAPOLATION) and concrete numeric thresholds.
>
> The 14 closed enums that form this layer's scope firewall are
> listed in detail in
> [Module 09 of the engineering course](../docs/09-evidence-and-safety.md).
>
> Integration surface: `SufficiencyCheckpoint` façade
> (`core/evidence_sufficiency/checkpoint.py`). Opt-in via
> `ExecutionCoordinator(sufficiency_checkpoint=...)`. Runs as
> Step 3.5 in the orchestrator pipeline. Failure-safe —
> exceptions are caught, logged, and the pipeline continues.
>
> Every run produces a frozen `EvidenceSufficiencyTrace`
> (7-dimension audit record, replayable). Refusals cite the
> specific rule ID. Downgrades emit caveats.
>
> This layer is **distinct from the Verification Layer**
> (Module 10). Sufficiency runs *before synthesis* to decide
> whether to answer. Verification runs *after synthesis* to
> decide whether to release the answer.
>
> Full architecture in `architecture/evidence-sufficiency.md`.

---

## What you learned

Before this module: refusal from an AI felt like a failure —
*"you didn't answer."*

Now: **refusing with a named rule is often the right answer**.
Our system treats "I don't know yet" as a feature, not a bug.
Every refusal cites:

- The specific rule that fired (R1..R12, V1..V10, U1..U9)
- The facet(s) that were missing or uncertain
- A suggested remediation

The AFR + CYP2D6 downgrade isn't a bug. It's the system being
honest about what we don't know.

---

Next up: **[12 — Watching the Agents](12-watching-the-agents.md)**

Everything we've built — agents, orchestrator, boundary, context,
memory, retrieval, graph, tools, verification, sufficiency — runs
per request. How do we *watch* that run happen, and how do we
replay it later?
