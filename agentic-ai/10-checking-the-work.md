# 10 — Checking the Work

> Four helpers whose only job is: *"Is this answer actually safe to
> give to a person?"*

---

## The Story

At Anu's bakery, before any cake leaves the building, it passes
four helpers at the door:

1. **The Shape Checker.** "Does this cake *look* like a cake?
   Round? Frosted? Has the right number of tiers?" If it's
   mush, or two tiers instead of three, stop.
2. **The Existence Checker.** "Are the ingredients *actually* in
   our ingredient log? Did we really have raspberries today, or
   is the cake claiming raspberries we don't have?" If the log
   doesn't show it, stop.
3. **The Truth Checker.** "If I re-read the recipe from scratch,
   and then look at this cake, do they match? Same size? Same
   frosting? Same decorations?" If the cake doesn't match the
   recipe, stop.
4. **The Chain Checker.** "Can I trace this cake back all the
   way? Order → recipe → ingredients → baker → oven log →
   finished cake. Any gap?" If any step is missing, stop.

Only a cake that passes **all four** goes to the customer.

If any checker says "stop," the cake gets held back, and the
reason is logged. The customer gets a polite message: "Your cake
didn't pass check number 2" — so they know *why*, not just
"something went wrong."

---

## What this means for computers

Before our system emits any answer, it runs the answer through
four specialized **verification engines**. Each one does one job:

1. **Shape** — does the answer have all the required fields,
   in the right types?
2. **Existence** — do the citations the answer references
   actually resolve in our evidence cache?
3. **Truth** — if we re-run the deterministic checks from scratch,
   do we get the same answer?
4. **Chain** — is the provenance chain (narrative → recommendation
   → phenotype → rule → evidence) complete, with no gaps?

Any of the four failing is enough to block the answer. The run
returns a structured refusal with the specific rule that failed.
No partial answers leak out.

This isn't optional. This is **Stage 4** of every run in the
`SwarmRuntime`.

---

## What we built

Our four verification engines live in:

```
anukriti-swarm/core/verification/
  biomedical_claim_validator.py     (Engine 1 — Shape)
  evidence_grounding_engine.py      (Engine 2 — Existence)
  safety_constraint_engine.py       (Engine 3 — Truth)
  provenance_validator.py           (Engine 4 — Chain)
```

Four files. Four engines. Each one maps to a specific question.

### Engine 1 — `BiomedicalClaimValidator` (Shape)

Every claim in the output must have:
- A **source** (what rule produced it)
- An **evidence reference** (what paper supports it)
- An **outcome** (what the rule said)

A claim missing any of these is **shape-broken**. Block.

### Engine 2 — `EvidenceGroundingEngine` (Existence)

If the claim cites `PMID:34032273`, does that PMID actually exist
in the MCP evidence cache?

Result possibilities:
- **Grounded** — fully supported
- **Partially grounded** — some citations resolve, some don't
- **Zero grounded** — no citations resolve

Zero grounded is block-on-sight. Partial might be delivered with
a warning, depending on policy.

### Engine 3 — `SafetyConstraintEngine` (Truth)

The fun one. It re-runs the deterministic layer **from scratch**:

- Give the re-runner only the raw inputs (gene, diplotype,
  population)
- Ask it to produce a phenotype, recommendation, and activity
  score
- Compare against the claim we're about to emit

If they don't match — if the claim says "Intermediate
Metabolizer" but fresh re-derivation says "Normal Metabolizer" —
**something corrupted in between**. Block.

This engine is why we feel safe letting LLMs write narrative
over deterministic output. The narrative can't sneak in a wrong
answer, because the truth check would catch it.

### Engine 4 — `ProvenanceValidator` (Chain)

Every claim should trace back through the chain:

```
narrative → recommendation → phenotype → CPIC rule → evidence paper
```

If the chain has a gap — say, the phenotype step is missing —
this engine flags it. Incomplete provenance is a sign of
unaccountable claims. Block.

### How they compose

All four engines run. The results are combined into a
**`VerificationOutcome`** with a score (one of five tiers):

```
grounded
partially_grounded
unverified
conflicting
unsafe
```

And a **decision**:

```
deliver  (all passed)
block    (any failed)
escalate (ambiguous, human review)
```

The orchestrator respects the decision. A "block" decision means
the narrative synthesis step doesn't run. The run returns a
structured refusal.

### The 4-engine composition

```
anukriti-swarm/agents/verification/biomedical_verification_agent.py
```

This is the `BiomedicalVerificationAgent` — the facade that
composes all four engines and returns the combined outcome.

---

## Try it yourself

Run the safety demo:

```bash
python -m demos.safety_demo
```

Output summary:

```
Total scenarios: 5  delivered: 1  blocked: 4
Adversarial tests: 4/4 matched expectations
Safety engine enforced every expected constraint.
```

The 5 scenarios:

| Scenario | Outcome |
|----------|---------|
| `clean_run` | partially_grounded → **DELIVERED** |
| `conflicting_evidence_clopidogrel` | conflicting → **BLOCKED** |
| `ambiguous_genotype_phenotype_drift` | unsafe → **BLOCKED** |
| `missing_evidence_fabricated_pmids` | unverified → **BLOCKED** |
| `ancestry_edge_unknown_allele` | unverified → **BLOCKED** |

Notice: **4 of 5 scenarios are blocked, and that's the feature.**
The system catches bad outputs before they reach users.

---

## The grown-up version

> Our deterministic safety engine is a 4-engine composition that
> runs as Stage 4 of `SwarmRuntime.run()`:
>
> 1. **`BiomedicalClaimValidator`** — enforces the
>    claim-level mapping: every claim must have `source` +
>    `evidence_refs` + `rule_id` + `outcome`
> 2. **`EvidenceGroundingEngine`** — verifies every cited
>    source resolves in `MCPEvidenceCache`; emits grounded /
>    partial / zero outcomes
> 3. **`SafetyConstraintEngine`** — re-derives phenotype, CPIC
>    recommendation, allele activity from raw inputs
>    independently; blocks on drift
> 4. **`ProvenanceValidator`** — walks the full provenance
>    chain from narrative back to evidence (4 dimensions:
>    `rule_id`, `agent_attribution`, `chain_completeness`,
>    `evidence_resolvability`)
>
> Output is a `VerificationOutcome` with:
> - `.score`: 5-tier `VerificationScore` closed enum (grounded,
>   partially_grounded, unverified, conflicting, unsafe)
> - `.decision`: `deliver` / `block` / `escalate`
> - `.trace`: full `VerificationTrace` frozen 6-field record
>
> Composed by `BiomedicalVerificationAgent.verify_run()` in
> `agents/verification/`. The output is also logged to the
> `MCPVerificationLog` service (Module 09) for cross-run audit.
>
> Paired with `EscalationWorkflow` which emits concrete
> `EscalationPlan` steps (`reroute` / `request_evidence` /
> `downgrade` / `block`) the orchestrator can act on.
>
> This is distinct from the **Evidence Sufficiency Layer**
> (Module 11), which runs before synthesis and decides *whether
> to answer at all*. Verification runs after synthesis and
> decides *whether to release what was synthesized*.
>
> Full architecture in `architecture/verification-safety.md`.

---

## What you learned

Before this module: "safety engine" sounded like either magic or
vague.

Now: safety is **four specific checks, each deterministic, each
independently testable**. Shape / Existence / Truth / Chain. If
any fails, the run is blocked with a specific reason. Five-tier
scoring. Three possible decisions.

No LLM-judges-LLM. No vibes. Four concrete Python functions
reading structured inputs and producing structured outputs.

---

Next up: **[11 — Knowing When to Say No](11-knowing-when-to-say-no.md)**

Verification checks if an answer is safe to emit. But there's an
earlier question: *should we try to answer at all?* When is "I
don't know" the right answer? That's evidence sufficiency.
