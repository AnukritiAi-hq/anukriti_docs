# Module 09 — Evidence and Safety

> Prerequisites: [04 Architecture](04-architecture.md), [05 Gene Matching](05-gene-matching.md), [06 Why Deterministic](06-why-deterministic.md)

---

## The question we're answering

Between "the phenotype engine produced a call" and "the narrative
synthesizer emits a paragraph," there are two distinct quality
gates — the **Evidence Sufficiency Layer** (decides whether we have
enough to say anything) and the **Verification Layer** (checks the
structural integrity of what we say). How do they work? What are
the specific rules? And what does a refusal actually look like?

---

## Two distinct gates, not one

First, disambiguate. The two layers answer different questions:

| Layer | Question | Gate type | Where |
|-------|----------|-----------|-------|
| **Evidence Sufficiency** | Is there enough evidence to make a claim at all? | Pre-emptive | `core/evidence_sufficiency/` |
| **Verification** | Does the claim we're about to emit structurally check out? | Post-hoc | `core/verification/` |

Sufficiency runs **before** synthesis. If sufficiency fails, there
is no claim to verify — we emit a refusal.

Verification runs **after** the deterministic layer has produced a
claim, but **before** it gets sent to the LLM narrative synthesizer.
If verification fails, we refuse to let the narrative step run.

Both are deterministic rule tables. Neither uses an LLM.

---

## The Evidence Sufficiency Layer, top-down

Four sub-layers, all composable, all closed-enum-gated:

### 1. Coverage analyzer — 6 closed facets

From `core/evidence_sufficiency/coverage/claim_coverage.py`:

```python
class ClaimEvidenceFacet(str, Enum):
    ALLELE = "allele"
    PHENOTYPE = "phenotype"
    CPIC = "cpic"
    POPULATION = "population"
    RECOMMENDATION = "recommendation"
    CONFLICT_FREE = "conflict_free"

class FacetCoverageState(str, Enum):
    COVERED = "covered"
    UNCERTAIN = "uncertain"
    MISSING = "missing"
```

For a given claim, each of the 6 facets gets a state (COVERED,
UNCERTAIN, MISSING). The `ClaimCoverageAnalysis` is a frozen
record containing these 6 states plus metadata.

### 2. Provenance tracker — 4 dimensions

From `core/evidence_sufficiency/coverage/provenance_tracker.py`:

```python
class ProvenanceDimension(str, Enum):
    SOURCE_ATTRIBUTION = "source_attribution"
    CHAIN_COMPLETENESS = "chain_completeness"
    EVIDENCE_RESOLVABILITY = "evidence_resolvability"
    TEMPORAL_CURRENCY = "temporal_currency"
```

For each claim, 4 provenance dimensions are audited. Did every
source in the claim resolve? Did the provenance chain complete from
narrative back down to CPIC rule? Are sources temporally current?

### 3. Conflict detector — 3 conflict kinds

From `core/evidence_sufficiency/conflict/agent.py`:

```python
class ConflictKind(str, Enum):
    PHENOTYPE_DIVERGENCE = "phenotype_divergence"
    RECOMMENDATION_DIVERGENCE = "recommendation_divergence"
    POPULATION_DIVERGENCE = "population_divergence"

class ConflictSeverity(str, Enum):
    HARD = "hard"
    SOFT = "soft"
```

If two independent evidence sources disagree on a phenotype call, or
recommend opposite drugs, or come from divergent populations, that's
a conflict. Hard conflicts (e.g. one says AVOID, another says USE)
block. Soft conflicts (both AVOID but different strength
classifications) trigger a caveat.

### 4. Sufficiency decision engine — 12 R-rules

Now we compose the signals from the three sub-layers above and
produce one of 7 decisions. Source:
`core/evidence_sufficiency/sufficiency/decision_engine.py`:

```python
class SufficiencyDecision(str, Enum):
    SUFFICIENT = "sufficient"
    PASS_WITH_CAVEAT = "pass_with_caveat"
    DOWNGRADE = "downgrade"
    REQUEST_MORE = "request_more"
    ESCALATE = "escalate"
    ABSTAIN = "abstain"
    BLOCK = "block"
```

The 12-rule table:

```
R1  hard conflict, or CONFLICT_FREE facet MISSING      → BLOCK
R2  PHENOTYPE facet MISSING                            → BLOCK
R3  RECOMMENDATION facet MISSING                       → BLOCK
R4  provenance incomplete                              → ABSTAIN
R5  POPULATION facet MISSING                           → ESCALATE
R6  CPIC facet MISSING                                 → REQUEST_MORE
R7  ALLELE facet MISSING                               → REQUEST_MORE
R8  RECOMMENDATION facet UNCERTAIN                     → DOWNGRADE
R9  POPULATION facet UNCERTAIN                         → DOWNGRADE
R10 any other facet UNCERTAIN                          → DOWNGRADE
R11 CONFLICT_FREE UNCERTAIN (soft conflict only)       → PASS_WITH_CAVEAT
R12 all facets COVERED, all provenance complete        → SUFFICIENT
```

Rules are **priority-ordered**. R1 beats R2 beats R3, etc. First
match wins. This makes the outcome deterministic and auditable —
every refusal cites its rule ID.

**Why 12 rules and not some other number:** they cover the cross
product of {6 facets × {MISSING, UNCERTAIN}} plus conflict states
plus provenance. Collapsed into a minimal set. Each rule has a
real-world scenario behind it.

---

## The Verification Layer — 10 V-rules

From `core/evidence_sufficiency/verifier/set_level.py`, after
sufficiency clears:

```python
class EvidenceVerdict(str, Enum):
    SUPPORTED = "supported"
    REFUTED = "refuted"
    INSUFFICIENT = "insufficient"
    CONFLICTING = "conflicting"
    UNCERTAIN = "uncertain"
```

10 V-rules produce one of these 5 verdicts:

```
V1  named AVOID vs USE inversion                 → REFUTED
V2  other hard conflict                          → CONFLICTING
V3  PHENOTYPE facet MISSING                      → INSUFFICIENT
V4  RECOMMENDATION facet MISSING                 → INSUFFICIENT
V5  other facet MISSING                          → INSUFFICIENT
V6  empty KG path bundle                         → UNCERTAIN
V7  POPULATION facet UNCERTAIN                   → UNCERTAIN
V8  other facet UNCERTAIN                        → UNCERTAIN
V9  CONFLICT_FREE UNCERTAIN                      → UNCERTAIN
V10 all facets COVERED, all paths non-empty      → SUPPORTED
```

These rules overlap with the R-rules but answer a different
question. R-rules say "what should we DO with this?" V-rules say
"what is the set-level VERDICT?"

**V1 is the most specific.** If the claim is "AVOID clopidogrel"
but the refuting evidence is a specific study saying "USE
clopidogrel for this genotype," we emit REFUTED with the specific
inversion named. We don't say "conflicting" and let the user guess
which side.

---

## The Uncertainty Scoring Engine — 9 U-rules

From `core/evidence_sufficiency/uncertainty/engine.py`:

```python
class UncertaintyScore(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    UNSAFE = "unsafe"

class UncertaintyAction(str, Enum):
    PROCEED = "proceed"
    REQUEST_MORE = "request_more"
    BLOCK = "block"
    ESCALATE = "escalate"
    DOWNGRADE = "downgrade"
```

The 9 U-rules produce a tier:

```
U1  hard conflict                     → UNSAFE
U2  missing non-conflict facet        → HIGH
U3  POPULATION facet UNCERTAIN        → HIGH
U4  empty KG path bundle              → HIGH
U5  ≥2 UNCERTAIN facets               → HIGH
U6  CONFLICT_FREE UNCERTAIN           → MODERATE
U7  exactly 1 non-core UNCERTAIN      → MODERATE
U8  KG path bundle with 1 path        → MODERATE
U9  otherwise                         → LOW
```

Tier-to-action mapping:

| Uncertainty | Action |
|-------------|--------|
| UNSAFE | BLOCK |
| HIGH | REQUEST_MORE |
| MODERATE | PROCEED (with caveat) |
| LOW | PROCEED |

**Why three parallel rule tables (R, V, U)?** Because they serve
three different consumers:

- **R-rules** serve the orchestrator deciding what to do next.
- **V-rules** serve downstream consumers wanting a set-level verdict.
- **U-rules** serve the calibration layer producing uncertainty-tier
  outputs.

Same underlying signals, three different views.

---

## The 4 Verification Engines (distinct from sufficiency)

Separate from the sufficiency/verifier above, there's a set of 4
**safety verification engines** (from `core/verification/`, session
#2 work) that run in Stage 4 of the runtime. They check:

### Engine 1: BiomedicalClaimValidator — shape

> "Does every claim in the output map to a source, a rule, and an
> outcome?"

No claim is allowed to be shape-incomplete. A claim like "patient
is a Poor Metabolizer" without a pointer to the rule that produced
it is a fabrication risk. Blocked.

### Engine 2: EvidenceGroundingEngine — existence

> "Do the source IDs that this claim cites actually exist in the
> evidence cache?"

If a claim cites PMID:34032273, that PMID must resolve in the MCP
evidence cache. Unresolved citations are blocked.

### Engine 3: SafetyConstraintEngine — truth

> "If I re-derive the phenotype / recommendation from the raw
> genotype independently, do I get the same answer as the claim
> says?"

This is the check against silent drift. If the claim says
"Intermediate Metabolizer" but re-running the phenotype engine says
"Normal Metabolizer" — block.

### Engine 4: ProvenanceValidator — chain

> "Does the provenance chain run from narrative all the way down to
> evidence without gaps?"

The chain: `narrative → recommendation → phenotype → CPIC rule →
evidence paper`. Every link must be present and traversable. If the
phenotype step is missing, block.

Together these 4 engines produce a `VerificationScore` with 5 tiers
(grounded / partially_grounded / unverified / conflicting / unsafe)
and a decision to deliver / block.

---

## What a refusal looks like, concretely

Say a query comes in for which the sufficiency layer fails on R1
(hard conflict). The output isn't an error — it's a structured
refusal:

```json
{
  "correlation_id": "a986dec2746f",
  "decision": "block",
  "rule_id": "R1",
  "rule_description": "hard conflict, or CONFLICT_FREE facet MISSING",
  "facet_report": {
    "allele": "COVERED",
    "phenotype": "COVERED",
    "cpic": "COVERED",
    "population": "COVERED",
    "recommendation": "COVERED",
    "conflict_free": "MISSING"
  },
  "conflicts": [
    {
      "kind": "recommendation_divergence",
      "severity": "hard",
      "sources": ["PMID:34032273", "PMID:28123456"]
    }
  ],
  "suggested_remediation": "Resolve conflicting recommendation sources",
  "provenance_chain": {...}
}
```

The refusal is **a full audit record**. A clinician or downstream
system can see:

- Exactly which rule triggered (R1)
- What facets were covered vs. missing
- What specific conflict was detected and between which sources
- What the suggested remediation is
- The full provenance chain up to the refusal point

Compare to a generic "I don't know" or a system that confidently
synthesizes. The named refusal is *more* informative than a
confident answer that might be wrong, because downstream
automation can route on the rule ID.

---

## The EvidenceSufficiencyTrace — frozen audit record

Every run produces an `EvidenceSufficiencyTrace` (from
`core/evidence_sufficiency/trace.py`) — a frozen Pydantic record
with 7 dimensions:

```python
@dataclass(frozen=True)
class EvidenceSufficiencyTrace:
    claim_id: str
    coverage: ClaimCoverageAnalysis       # 6 facets + states
    provenance: ProvenanceCoverageReport  # 4 dimensions
    conflicts: tuple[ConflictFinding, ...]
    decision: SufficiencyDecision         # R-rule outcome
    verdict: EvidenceVerdict              # V-rule outcome
    uncertainty: UncertaintyScore          # U-rule outcome
    uncertainty_transitions: tuple[...]    # if tier changed during run
```

Frozen means: updates create a new instance preserving `claim_id`.
This gives replay-safety. The trace is persisted to MongoDB via the
MCP layer (Module 10).

A clinician 6 months after the run can ask: "why was this claim
refused?" and get back the exact trace with rule IDs, missing
facets, and conflict sources. No reconstruction needed.

---

## The sufficiency checkpoint as an opt-in

From Module 04: new capabilities are added via constructor args.
The sufficiency checkpoint is the canonical example.

`ExecutionCoordinator.__init__` accepts a
`sufficiency_checkpoint: SufficiencyCheckpoint | None = None`.
When set, a new "Step 3.5" runs between retrieval and verification:

```python
if self.sufficiency_checkpoint is not None:
    result = self.sufficiency_checkpoint.evaluate(...)
    if result.decision in (BLOCK, ABSTAIN, ESCALATE):
        return self._emit_refusal(result)
    elif result.decision in (DOWNGRADE, PASS_WITH_CAVEAT):
        context.attach_caveats(result.caveats)
    # SUFFICIENT and REQUEST_MORE continue to verification
```

The flagship demos don't construct the coordinator with this
argument — their behavior is unchanged from pre-sufficiency-layer
times. This is the off-by-default invariant in action. New
capabilities never break old signatures.

---

## Running example — Priya's clean path

Priya (SAS, CYP2C19 *2/*2, clopidogrel) goes through the sufficiency
layer:

```
Facets:          allele=COVERED, phenotype=COVERED, cpic=COVERED,
                 population=COVERED, recommendation=COVERED,
                 conflict_free=COVERED
Provenance:      all 4 dimensions OK
Conflicts:       none

R-rule fires: R12 → SUFFICIENT
V-rule fires: V10 → SUPPORTED
U-rule fires: U9 (none of U1-U8 matched) → LOW uncertainty
BiasDetector: 0 findings

Result: proceed to verification → verification passes → narrative
synthesized → output delivered.

Correlation ID: a986dec2746f
Gate: ✓
```

Contrast with the AFR + CYP2D6 case:

```
Facets:          allele=COVERED, phenotype=COVERED, cpic=COVERED,
                 population=UNCERTAIN, recommendation=UNCERTAIN,
                 conflict_free=COVERED
Provenance:      OK

R-rule fires: R9 (POPULATION UNCERTAIN) → DOWNGRADE
V-rule fires: V7 (POPULATION UNCERTAIN) → UNCERTAIN
U-rule fires: U3 + U5 → HIGH uncertainty
BiasDetector: ANCESTRY_SCARCITY finding

Result: downgrade. Recommendation strength reduced. Narrative
emitted with pinned refusal banner. Refusal cites R9 + V7 + U3 +
ANCESTRY_SCARCITY.

Gate: ✗ (downgrade, not clean pass)
```

Both outputs are structurally valid. The second is an honest
abstention; the first is a clean claim.

---

## Summary

You now know:

- **Two gates:** sufficiency (pre-synthesis) and verification
  (post-synthesis, pre-narrative).
- **4 sub-layers** in sufficiency: coverage (6 facets), provenance
  (4 dimensions), conflict (3 kinds × 2 severities), decision (12 R-rules).
- **3 parallel rule tables:** R-rules (decision), V-rules (verdict),
  U-rules (uncertainty). Same signals, three views for different
  consumers.
- **4 verification engines:** shape, existence, truth, chain.
- **Refusals are structured records** — named rule IDs, coverage
  reports, remediation suggestions. Not "error: unknown."
- **Frozen `EvidenceSufficiencyTrace`** is the auditable artifact.
- **Off-by-default** via `ExecutionCoordinator(sufficiency_checkpoint=...)`.

Next: [Module 10 — How the Pieces Talk](10-how-the-pieces-talk.md).
Request flow across the three repos, the agent envelope protocol,
and the MCP persistence surface.
