# Evidence Sufficiency Layer — Deep Dive

> **Audience:** founder, prospective engineers, technical reviewers,
> anyone who wants to know exactly *what gets refused, why, and by
> which rule* when the swarm's safety layer fires.
>
> **Last updated:** 2026-05-16
>
> **Companion docs:**
>   - [`DETERMINISTIC_ENGINE_DEEP_DIVE.md`](DETERMINISTIC_ENGINE_DEEP_DIVE.md) — the upstream layer (VCF → diplotype → phenotype → CPIC action) that this layer gates
>   - High-level course: [`docs/04-architecture.md`](docs/04-architecture.md), [`docs/09-evidence-and-safety.md`](docs/09-evidence-and-safety.md), [`docs/06-why-deterministic.md`](docs/06-why-deterministic.md)
>   - Architecture spec: [`../anukriti-swarm/architecture/evidence-sufficiency.md`](../anukriti-swarm/architecture/evidence-sufficiency.md) (350 lines, the design doc)

---

## TL;DR

The deterministic engine ([`DETERMINISTIC_ENGINE_DEEP_DIVE.md`](DETERMINISTIC_ENGINE_DEEP_DIVE.md)) answers *"what does CPIC say for this patient's diplotype?"*. The Evidence Sufficiency Layer (ESL) answers a different question:

> **"Is the evidence base good enough to deliver that recommendation today, given who this patient is?"**

It is a **deterministic rule stack** layered on top of the swarm's retrieval + verification pipeline:

```
6 evidence facets         (closed enum: ALLELE, PHENOTYPE, CPIC,
                           POPULATION, RECOMMENDATION, CONFLICT_FREE)
       │
       │   coverage analyzer + provenance tracker + conflict detector
       ▼
SufficiencyDecisionEngine  (12 rules: R1..R12 + opt-in M4 → 8 outcomes)
       │
       ▼
SetLevelEvidenceVerifier   (10 rules: V1..V10 → 5 verdicts)
       │
       ▼
UncertaintyScoringEngine   (9 rules: U1..U9 → 4 tiers)
       │
       ▼
BiasDetector               (3 closed bias kinds)
       │
       ▼
SufficiencyCheckpoint      (composition façade — single boolean
                            "may synthesis run?" + audit record)
```

Five things hold for every call:

1. **Every refusal names a rule.** `R5: SAS population evidence missing — escalating for ancestry review.` That rule_id is in the audit log.
2. **Every layer is a closed enum.** Adding a new evidence facet, a new sufficiency decision, a new bias kind requires a code change.
3. **Off by default.** The whole layer integrates via one constructor argument (`ExecutionCoordinator(sufficiency_checkpoint=...)`). Default is `None`. The 7 byte-locked flagship demos run unchanged.
4. **No LLM in the decision path.** No "vibes-based routing." 244/244 pytest tests pin the rule tables byte-identically.
5. **AFR scarcity is a *feature*, not a bug.** When the AFR + CYP2D6 scenario runs, the layer returns `DOWNGRADE` with `R9: AFR population support weak — confidence lowered`. That is an honest signal of evidence-base limits, surfaced as a deliberate `✗` in the demo output.

This is the second half of the platform's "deterministic" claim — where the upstream engine is deterministic about *what CPIC says*, this layer is deterministic about *whether we'll deliver it.*

---

## Table of contents

1. [Why this layer exists](#1-why-this-layer-exists)
2. [The 6 evidence facets — closed scope](#2-the-6-evidence-facets--closed-scope)
3. [Layer 1: Coverage analysis](#3-layer-1-coverage-analysis)
4. [Layer 2: Conflict detection (3 closed classes)](#4-layer-2-conflict-detection-3-closed-classes)
5. [Layer 3: Provenance tracking (4 dimensions)](#5-layer-3-provenance-tracking-4-dimensions)
6. [Layer 4: SufficiencyDecisionEngine — 12 rules → 8 outcomes](#6-layer-4-sufficiencydecisionengine--12-rules--8-outcomes)
7. [Layer 5: SetLevelEvidenceVerifier — 10 rules → 5 verdicts](#7-layer-5-setlevelevidenceverifier--10-rules--5-verdicts)
8. [Layer 6: UncertaintyScoringEngine — 9 rules → 4 tiers](#8-layer-6-uncertaintyscoringengine--9-rules--4-tiers)
9. [Layer 7: BiasDetector — 3 closed bias kinds](#9-layer-7-biasdetector--3-closed-bias-kinds)
10. [SufficiencyCheckpoint — composition façade](#10-sufficiencycheckpoint--composition-façade)
11. [End-to-end worked examples](#11-end-to-end-worked-examples)
12. [What this layer deliberately does NOT do](#12-what-this-layer-deliberately-does-not-do)

---

## 1. Why this layer exists

In every healthcare-AI product, the question that matters more than "what does the model output?" is "**when does the model refuse to output?**". The platform's positioning leans on this: *"Every refusal is named. Every escalation is traced."*

Without a deterministic refusal layer, three failure modes dominate:

- **Confident output on thin evidence.** The system says "Poor Metabolizer — avoid clopidogrel" for a population where the allele frequency is from one underpowered 1990s study. No caveat. Clinician trusts it.
- **Silent fallback to "average."** When population-specific evidence is missing, the system uses EUR-derived numbers as a default. The patient is non-EUR. Nobody is told.
- **LLM-shaped refusals.** "I'm not sure about this case" with no reason, no rule, no audit trail. Cannot be reviewed by a regulator.

The Evidence Sufficiency Layer is the **structural** answer: every refusal points at a numbered rule (`R1` through `R12`, `V1` through `V10`, `U1` through `U9`) and the rule's preconditions are visible in source code. A reviewer can audit policy changes by reading one method per engine.

This is why the layer is **deterministic** — same inputs produce the same decision byte-identically — and **off by default**. It's an opt-in extension via constructor argument, not a feature flag, and the whole layer disappears if `ExecutionCoordinator.sufficiency_checkpoint` is `None`.

Architecture spec: [`anukriti-swarm/architecture/evidence-sufficiency.md`](../anukriti-swarm/architecture/evidence-sufficiency.md) (350 lines, the design doc that maps the 30-requirement brief to source files).

---

## 2. The 6 evidence facets — closed scope

The layer's universe is six **evidence facets** required for safe pharmacogenomic synthesis. Defined in `core/evidence_sufficiency/coverage/claim_coverage.py`:

```python
class ClaimEvidenceFacet(str, Enum):
    """The six pharmacogenomic evidence facets — closed set.

    Ordered as they appear in the safety synthesis contract: you
    cannot recommend a drug before you have established allele →
    phenotype → guideline → population → recommendation, and ruled
    out conflict.
    """

    ALLELE = "allele"                    # variant attested in PharmGKB / PharmVar / PubMed
    PHENOTYPE = "phenotype"              # diplotype → phenotype mapping is CPIC-backed
    CPIC = "cpic"                        # CPIC guideline exists for this drug-gene pair
    POPULATION = "population"            # allele frequency in target super-population
    RECOMMENDATION = "recommendation"    # actionable prescribing recommendation attached
    CONFLICT_FREE = "conflict_free"      # retrieved evidence carries no contradiction
```

Each facet carries **one of three closed states**:

```python
class FacetCoverageState(str, Enum):
    COVERED = "covered"      # at least one non-conflicting evidence ref resolves
    MISSING = "missing"      # no evidence resolves
    UNCERTAIN = "uncertain"  # evidence exists but resolution is inconclusive
```

**No fourth state.** No "partial," "weak," "probable." The facet/state cross-product is `6 × 3 = 18` discrete cells. That's the entire input space the rules consume.

The closure is the scope firewall. Adding a seventh facet (e.g. `FOUNDER_EFFECT_BURDEN` for the BCHE/Vysya wedge — see [`IDEA_REFINEMENT_AND_PHASING_2026-05-14.md`](IDEA_REFINEMENT_AND_PHASING_2026-05-14.md) Phase B3) is a deliberate code change, not a runtime configuration.

---

## 3. Layer 1: Coverage analysis

**Module:** `core/evidence_sufficiency/coverage/claim_coverage.py` + `coverage/analyzer.py`

**Class:** `EvidenceCoverageAnalyzer` produces a `ClaimCoverageAnalysis` per run.

### `ClaimCoverageAnalysis` is a frozen audit record

```python
@dataclass(frozen=True)
class ClaimCoverageAnalysis:
    drug: str                     # "clopidogrel"
    gene: str                     # "CYP2C19"
    genotype: str                 # "*2/*2"
    population: SuperPopulation   # closed enum: EUR / EAS / SAS / AFR / AMR

    facet_states: Mapping[ClaimEvidenceFacet, FacetCoverageState]
    facet_evidence_refs: Mapping[ClaimEvidenceFacet, tuple[str, ...]]
    facet_reasons: Mapping[ClaimEvidenceFacet, str]

    claim_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    correlation_id: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
```

Frozen — once produced, can't mutate. Each facet has three pieces of info:
- **state** (one of 3 closed values)
- **evidence refs** (tuple of source ids that contributed: PMIDs, CPIC guideline ids, PharmGKB annotation ids)
- **reason** (free-form note)

### The `with_facet()` builder

The analyzer accumulates facets one at a time. Each call returns a **new** analysis, preserving `claim_id` + `correlation_id` + `created_at`:

```python
def with_facet(
    self,
    facet: ClaimEvidenceFacet,                # closed enum — can't smuggle
    *,
    state: FacetCoverageState,                # closed enum
    evidence_refs: tuple[str, ...] = (),
    reason: str = "",
) -> ClaimCoverageAnalysis:
    """Return a new analysis with one facet replaced."""
```

**Why frozen + builder?** The audit trail is uninterrupted. A `ClaimCoverageAnalysis` produced 3 years ago can be retrieved from MCP storage and its derived signals (`coverage_ratio`, `is_complete`, `missing_facets`, `uncertain_facets`) re-computed deterministically, without any state from the original run.

### Derived signals — pure, deterministic

```python
@property
def coverage_ratio(self) -> float:
    """Fraction of facets in COVERED state, in [0.0, 1.0]."""
    covered = sum(1 for s in self.facet_states.values()
                    if s is FacetCoverageState.COVERED)
    return round(covered / 6, 4)

@property
def is_complete(self) -> bool:
    return all(self.facet_states[f] is FacetCoverageState.COVERED
               for f in ALL_FACETS)

@property
def missing_facets(self) -> tuple[ClaimEvidenceFacet, ...]:
    """Facets whose state is MISSING, in stable iteration order."""
    return tuple(f for f in ALL_FACETS
                 if self.facet_states[f] is FacetCoverageState.MISSING)

@property
def uncertain_facets(self) -> tuple[ClaimEvidenceFacet, ...]:
    return tuple(f for f in ALL_FACETS
                 if self.facet_states[f] is FacetCoverageState.UNCERTAIN)
```

**`coverage_ratio` is a dumb count, not a weighted score.** Every facet counts equally. Policy lives in the rules engine downstream — this property is for audit, not decision-making.

### Distinction from `GroundingReport.coverage`

There's an existing `GroundingReport.coverage` field elsewhere in the swarm. The two are different:

- **`GroundingReport.coverage`** — *source-level*: "did the cited PMIDs / CPIC ids resolve in the MCP cache?"
- **`ClaimCoverageAnalysis.coverage_ratio`** — *facet-level*: "do we have evidence for each of the six required facet kinds?"

Both flow into `SufficiencyDecisionEngine`. They measure different dimensions of "evidence health."

---

## 4. Layer 2: Conflict detection (3 closed classes)

**Module:** `core/evidence_sufficiency/conflict/agent.py`

**Class:** `ConflictDetectionAgent`

Where the coverage analyzer asks *"do we have evidence?"*, the conflict detector asks *"does the evidence agree with itself?"*

Three closed conflict classes — and nothing else:

```python
class ConflictKind(str, Enum):
    PHENOTYPE_DISAGREEMENT     # same (gene, diplotype, population) → different phenotype
    RECOMMENDATION_CLASH       # same (drug, gene, phenotype) → incompatible action
    POPULATION_DIVERGENCE      # same (allele, population) → frequency Δ > tolerance


class ConflictSeverity(str, Enum):
    HARD = "hard"   # ≥1 named invertor, e.g. "AVOID" vs "USE"
    SOFT = "soft"   # numerical disagreement within tolerance
```

**Recommendation actions are also a closed enum** (the `RecommendationAction` enum in the same module): `USE`, `AVOID`, `CONSIDER_ALTERNATIVE`, `CONTRAINDICATED`. The pairwise compatibility table (which pairs are HARD clashes) is hard-coded — any pair other than `USE + CONSIDER_ALTERNATIVE` is a HARD conflict.

### Input contract

The agent reads from a uniform claim-shape the upstream pipeline already produces:

```python
detect(claims, *, tolerance=0.15) -> tuple[ConflictFinding, ...]

# Recognized claim kinds:
#   kind='phenotype'      {gene, diplotype, population, phenotype, source_id}
#   kind='recommendation' {drug, gene, phenotype, action_text, source_id}
#   kind='frequency'      {allele, population, frequency, source_id}
```

Anything else (unknown `kind` or missing keys) is **silently ignored**. The agent is deterministic about what it can read; it doesn't pretend to handle what it can't.

### Why 3 conflict classes (and not more)?

The brief deliberately scoped the agent to *pharmacogenomic* conflicts. "Sex-biased dosing" or "publication bias" are out of scope for this agent — they belong in the bias detector or are simply not the layer's concern.

The 3 classes cover the domain's actual decision-relevant disagreements: two papers disagreeing on a phenotype call, two guidelines disagreeing on a drug action, two cohorts reporting incompatible allele frequencies. Adding a fourth class is a code change — the closure prevents the agent from drifting into "any text disagreement."

---

## 5. Layer 3: Provenance tracking (4 dimensions)

**Module:** `core/evidence_sufficiency/coverage/provenance_tracker.py`

**Class:** `ProvenanceCoverageTracker`

Asks: *"is every claim's provenance chain complete and attributable?"*

Reads `MCPProvenanceStore`-shaped records and produces a `ProvenanceCoverageReport` over **4 closed attribution dimensions**:

```python
class ProvenanceDimension(str, Enum):
    RULE_ID                  # every record has a non-empty rule_id
    AGENT_ATTRIBUTION        # every record has a non-empty generating_agent
    CHAIN_COMPLETENESS       # parent_claim_id resolves within the run's records
    EVIDENCE_RESOLVABILITY   # ≥1 deterministic evidence_source per record
```

**Why this matters separately from coverage.** A run can have full facet coverage but a **broken provenance chain** — e.g. a downstream agent emitted a claim without recording its parent. The recommendation might still be correct on the facts, but the audit trail is broken. The decision engine treats this as `ABSTAIN` (R4) — synthesis is *withheld*, not blocked, because the answer might be right but **un-auditable**.

The distinction matters: BLOCK says "the answer is wrong"; ABSTAIN says "I can't show my work."

The tracker is deliberately narrow — it does not re-open documents, does not reach to MCP, consumes records the caller already has. That keeps it deterministic and unit-testable without a live MCP client.

---

## 6. Layer 4: `SufficiencyDecisionEngine` — 12 rules → 8 outcomes

**Module:** `core/evidence_sufficiency/sufficiency/decision_engine.py`

**Class:** `SufficiencyDecisionEngine` — the heart of the safety contract.

### The 8 closed decisions

```python
class SufficiencyDecision(str, Enum):
    SUFFICIENT                                    # all clean → synthesize
    PASS_WITH_CAVEAT                              # soft conflict only → synthesize with caveat
    REQUEST_MORE                                  # addressable gap → adaptive retrieval should fetch more
    DOWNGRADE                                     # weak evidence → synthesize with lowered confidence
    ESCALATE                                      # ancestry-underrepresented → human review
    ABSTAIN                                       # provenance broken → withhold (un-auditable)
    BLOCK                                         # hard conflict or core-facet missing → MUST NOT synthesize
    EXTRAPOLATION_WITH_CROSS_ANCESTRY_SUPPORT     # M4 — opt-in, off by default
```

Eight values. Five enable synthesis, three withhold/block. The `is_blocking` and `allows_synthesis` properties on `SufficiencyReport` are the boolean shortcuts the orchestrator reads.

### The 12 rules — priority order, first match wins

```
R1   CONFLICT_FREE == MISSING (hard conflict)        → BLOCK
R2   PHENOTYPE == MISSING                            → BLOCK
R3   RECOMMENDATION == MISSING                       → BLOCK
R4   provenance present AND incomplete               → ABSTAIN
R5   POPULATION == MISSING                           → ESCALATE
R6   CPIC == MISSING                                 → REQUEST_MORE
R7   ALLELE == MISSING                               → REQUEST_MORE
R8   RECOMMENDATION == UNCERTAIN                     → DOWNGRADE
M4   POPULATION UNCERTAIN + (ALLELE+PHENOTYPE+CPIC+
     RECOMMENDATION) all COVERED [opt-in]            → EXTRAPOLATION_*
R9   POPULATION == UNCERTAIN                         → DOWNGRADE
R10  any other UNCERTAIN facet                       → DOWNGRADE
R11  CONFLICT_FREE == UNCERTAIN (soft only)          → PASS_WITH_CAVEAT
R12  all COVERED, no conflict                        → SUFFICIENT
```

The implementation is one method, ~150 lines of `if` statements. From the actual file:

```python
def _apply_rules(self, coverage, provenance, findings):
    states = coverage.facet_states
    any_hard = any(f.severity is ConflictSeverity.HARD for f in findings)

    # R1 — hard conflict
    if states[ClaimEvidenceFacet.CONFLICT_FREE] is FacetCoverageState.MISSING or any_hard:
        return (SufficiencyDecision.BLOCK,
                "R1: hard conflict detected — synthesis blocked")

    # R2 — phenotype missing
    if states[ClaimEvidenceFacet.PHENOTYPE] is FacetCoverageState.MISSING:
        return (SufficiencyDecision.BLOCK,
                "R2: phenotype evidence missing — cannot synthesize recommendation")

    # ... R3 through R12 in declared order ...

    # R12 — sufficient
    return (SufficiencyDecision.SUFFICIENT,
            "R12: all facets covered, no conflict, provenance complete")
```

Each rule returns `(decision, rationale)`. The rationale **names the rule** and explains in one English sentence what fired. This is the audit string that ends up in the user-facing refusal.

### Order rationale (deliberate, documented in the source)

The source comment block on `_apply_rules` documents the ordering in plain English:

> *"BLOCK rules come first. Safety trumps everything.*
>
> *ABSTAIN comes before ESCALATE / REQUEST_MORE because we cannot trust any action (including 'ask for more') on an un-attributable pipeline — retrieval loops that can't be audited don't help.*
>
> *ESCALATE precedes REQUEST_MORE for POPULATION because an ancestry-underrepresented population is usually a data-gap retrieval can't close (we don't invent it).*
>
> *DOWNGRADE rules are specific-to-general (R8-R10). R11 is reached only if CONFLICT_FREE is the single UNCERTAIN facet.*
>
> *R12 fires iff none of R1-R11 did."*

That ordering is the **policy**. Reviewing a policy change is reading a diff against this method.

### M4 — the cross-ancestry hedge (opt-in)

Rule M4 is the eighth value of `SufficiencyDecision`, added in session #14. It fires **only when explicitly enabled**:

```python
SufficiencyDecisionEngine(allow_cross_ancestry_extrapolation=True)
```

Default behavior leaves it off. Why?

- **Existing demos depend on R9 firing for AFR + CYP2D6.** Enabling M4 always-on would change their outputs, breaking the byte-identical regression contract.
- **Cross-ancestry extrapolation is a deliberate epistemic posture** — appropriate for cohort-scale Stage-1 simulation (`demos/cohort_demo.py`) but not for single-scenario flagship demos.
- **Opt-in via constructor argument matches the platform's discipline.** Every other capability extension uses the same pattern (`ExecutionCoordinator.sufficiency_checkpoint`, `GeminiOrchestrator.memory_advisor`, `core/simulation/`). Constructor args show up in code review; feature flags hide in YAML.

Preconditions for M4:

```
POPULATION == UNCERTAIN
  AND ALLELE == COVERED
  AND PHENOTYPE == COVERED
  AND CPIC == COVERED
  AND RECOMMENDATION == COVERED
```

When M4 fires, the rationale string is:

```
M4: AFR direct population evidence thin but ALLELE + PHENOTYPE +
    CPIC + RECOMMENDATION all covered — cross-ancestry
    extrapolation hedge applied
```

A reviewer can immediately see what tradeoff was made. If they don't like it, they reject the PR that enabled the flag for that consumer.

### Output: `SufficiencyReport`

```python
@dataclass(frozen=True)
class SufficiencyReport:
    decision: SufficiencyDecision        # one of 8
    rationale: str                        # "R5: SAS population evidence missing..."
    coverage: ClaimCoverageAnalysis       # the input
    provenance: ProvenanceCoverageReport | None
    findings: tuple[ConflictFinding, ...]
    correlation_id: str
    created_at: datetime

    @property
    def is_blocking(self) -> bool:
        return self.decision in {BLOCK, ABSTAIN}

    @property
    def allows_synthesis(self) -> bool:
        return self.decision in {
            SUFFICIENT, PASS_WITH_CAVEAT, DOWNGRADE,
            EXTRAPOLATION_WITH_CROSS_ANCESTRY_SUPPORT,
        }
```

Frozen — same audit-record discipline as `ClaimCoverageAnalysis`. Persists to MCP via `to_dict()`.

---

## 7. Layer 5: `SetLevelEvidenceVerifier` — 10 rules → 5 verdicts

**Module:** `core/evidence_sufficiency/verifier/set_level.py`

**Class:** `SetLevelEvidenceVerifier`

This is the **SURE-RAG move**: judge the evidence set *jointly* rather than one claim at a time. Where the claim validator is local ("does this claim cite something?"), the set-level verifier is global ("does the bundle, taken together, support the conclusion?").

### The 5 closed verdicts

```python
class EvidenceVerdict(str, Enum):
    SUPPORTED       # all COVERED, no hard conflict, pathway non-empty when bundle supplied
    UNCERTAIN       # any UNCERTAIN facet, or empty KG path bundle
    INSUFFICIENT    # any MISSING facet (ALLELE / PHENOTYPE / CPIC / etc.)
    CONFLICTING    # hard conflict, can't pick a side
    REFUTED        # named invertor (AVOID vs USE) — we can NAME the refutation
```

`REFUTED` is the strongest negative signal. `INSUFFICIENT` is *"we don't have enough."* `CONFLICTING` is *"we have enough but it disagrees."* The distinction is meaningful for downstream synthesis.

### The 10 rules

```
V1   hard RECOMMENDATION_CLASH with named invertor (AVOID/USE)  → REFUTED
V2   any other HARD conflict                                    → CONFLICTING
V3   PHENOTYPE facet MISSING                                    → INSUFFICIENT
V4   RECOMMENDATION facet MISSING                               → INSUFFICIENT
V5   any other MISSING facet (ALLELE / CPIC / POPULATION)       → INSUFFICIENT
V6   KG path bundle supplied AND empty                          → UNCERTAIN
V7   POPULATION facet UNCERTAIN                                 → UNCERTAIN
V8   any other UNCERTAIN facet                                  → UNCERTAIN
V9   CONFLICT_FREE UNCERTAIN (soft conflict only)               → UNCERTAIN
V10  all COVERED, no HARD conflict, pathway non-empty           → SUPPORTED
```

### Why a separate verifier (alongside the decision engine)?

The decision engine routes the *next action* (BLOCK / ABSTAIN / DOWNGRADE / etc.). The verifier emits a *verdict* about the evidence bundle's standing. They answer different questions:

- *Decision engine:* "What should the system do?"
- *Verifier:* "What does the evidence set, taken jointly, say?"

Downstream consumers (the narrative layer, the explanation generator) need **both** signals. The decision engine's `REQUEST_MORE` is paired with the verifier's `INSUFFICIENT`; the engine's `SUFFICIENT` is paired with the verifier's `SUPPORTED`. Sometimes they diverge productively — `DOWNGRADE` (engine: "synthesize with lower confidence") + `UNCERTAIN` (verifier: "we are not certain") is a meaningful combination that becomes the explicit caveat in the user-facing output.

### Pathway semantics

The verifier optionally consumes a **knowledge-graph path bundle** — a tuple of `GraphPath` records from the swarm's `MultiHopReasoner` over the pharmacogenomic KG (37 nodes, 34 edges, 10 NodeKinds, 7 EdgeKinds). When the caller supplies one:

- Empty bundle → V6 fires → `UNCERTAIN`. *"Pathway reachability is a first-class signal; if you searched and found nothing, we cannot claim the pathway is supported."*
- Non-empty bundle → V10 can fire → `SUPPORTED` (when other conditions hold).

When the caller omits the bundle (`path_bundle=()`), pathway completeness is simply not a driver — V10 doesn't require it, V6 cannot fire. That keeps the verifier useful before the `GraphRetriever` body ships (it's currently a documented stub with the final public surface in place).

The verifier does **not** re-execute retrieval, does **not** run graph reasoning, and does **not** open documents. It reads what the caller has already produced and applies the table.

---

## 8. Layer 6: `UncertaintyScoringEngine` — 9 rules → 4 tiers

**Module:** `core/evidence_sufficiency/uncertainty/engine.py`

**Class:** `UncertaintyScoringEngine`

Sufficiency answers *"what should we do?"*. Verifier answers *"what does the bundle say?"*. Uncertainty answers *"how confident should we be in the conclusion we would otherwise support?"*

A run can be `SUFFICIENT` and `SUPPORTED` yet still carry `MODERATE` uncertainty because, say, the KG path bundle has only 1 path. The narrative layer reads this signal and caveats accordingly.

### The 4 closed tiers

```python
class UncertaintyScore(str, Enum):
    LOW         # high confidence — facets fully covered, no conflict, pathway observed
    MODERATE    # minor weakness — 1 uncertain non-core facet, soft conflict, thin pathway
    HIGH        # substantial weakness — ≥2 uncertain, POPULATION uncertain, empty KG bundle
    UNSAFE      # structural refutation — HARD conflict or refuted path; never synthesize
```

### The 9 rules — first match wins

```
U1   any HARD conflict finding                          → UNSAFE
U2   any MISSING facet (other than CONFLICT_FREE)       → HIGH
U3   POPULATION facet UNCERTAIN                         → HIGH
U4   KG path bundle supplied AND empty                  → HIGH
U5   ≥2 uncertain facets total                          → HIGH
U6   CONFLICT_FREE UNCERTAIN (soft conflict)            → MODERATE
U7   exactly 1 uncertain non-core facet (ALLELE/CPIC)   → MODERATE
U8   KG path bundle supplied AND only 1 path            → MODERATE
U9   otherwise                                          → LOW
```

### Action mapping

```python
class UncertaintyAction(str, Enum):
    PROCEED      # LOW or MODERATE — synthesis runs (with payload propagated)
    REQUEST_MORE # HIGH — adaptive retrieval should fetch more
    BLOCK        # UNSAFE — never synthesize
    ABSTAIN      # reserved — phase-6 orchestrator may compose with provenance state
    ESCALATE     # reserved — phase-6 orchestrator may compose
```

The mapping is `LOW → PROCEED`, `MODERATE → PROCEED`, `HIGH → REQUEST_MORE`, `UNSAFE → BLOCK`. Two reserved values (`ABSTAIN`, `ESCALATE`) exist as closed-enum values for downstream policy composition; the engine never emits them itself.

### Why separate tiers from the decision engine?

A `DOWNGRADE` decision (engine) can be paired with `LOW` or `MODERATE` uncertainty (engine: "lower confidence" + scorer: "but not by much"). A `SUFFICIENT` decision can be paired with `HIGH` uncertainty (engine: "we have everything we need" + scorer: "but the pathway is thin"). The two signals **compose** to give the narrative layer a richer caveat.

Reading both:

| Decision | Uncertainty | Narrative caveat |
|---|---|---|
| SUFFICIENT | LOW | "Strong recommendation; confidence high." |
| SUFFICIENT | MODERATE | "Recommendation supported; one factor introduces minor uncertainty." |
| DOWNGRADE | HIGH | "Recommendation provided with reduced confidence; multiple factors weaken the evidence base." |
| BLOCK | UNSAFE | Never reaches the narrative layer; refusal returned with rule_id. |

---

## 9. Layer 7: `BiasDetector` — 3 closed bias kinds

**Module:** `core/evidence_sufficiency/uncertainty/bias_detector.py`

**Class:** `PopulationEvidenceBiasDetector`

This is the most strategically important component for Anukriti's positioning. Pharmacogenomic evidence is **structurally Eurocentric** (per Martin 2017, AJHG; cited in [`PLATFORM.md`](../anukriti-pgx-core/PLATFORM.md) and [`docs/strategy.md`](../anukriti-pgx-core/docs/strategy.md)). A "population-aware" platform that doesn't *name* this skew is just a label — this detector is the mechanism that names it.

### The 3 closed bias kinds

```python
class BiasKind(str, Enum):
    EUROCENTRIC_IMBALANCE       # target non-EUR + target evidence empty + EUR evidence present
    ANCESTRY_SCARCITY           # target ancestry < threshold × max-observed (default 0.5)
    UNSUPPORTED_EXTRAPOLATION   # POPULATION UNCERTAIN + 0 frequency edges to target in KG
```

That's it. Three. Sex bias, age bias, publication bias — all out of scope for this detector. Adding a fourth is a code change.

### The findings

Each detected bias is a `BiasFinding` with kind, target population, and a numeric measurement:

```python
@dataclass(frozen=True)
class BiasFinding:
    kind: BiasKind
    target_population: SuperPopulation
    target_evidence_count: int
    reference_evidence_count: int
    ratio: float                         # 0.0 if denominator is 0
    threshold: float                     # the rule's threshold the detector applied
    reason: str                          # e.g. "AFR has 0 evidence; EUR has 14"
```

Empty tuple means no bias detected. Findings are sorted by `(kind, reason)` for stable output.

### Configurable thresholds

The detector exposes two per-call thresholds:

```python
PopulationEvidenceBiasDetector(
    scarcity_ratio=0.5,           # ancestry-scarcity threshold
    min_target_evidence=1,        # minimum evidence for "target has presence"
)
```

These are tuning knobs at the call site. **Tuning is a code change** — there's no YAML, no env var, no runtime config.

### Why this matters for the platform's positioning

> "*Population-aware*" without a deterministic bias-detection layer is a marketing claim. Population-aware *with* it is a mechanism. The detector is what makes the claim citable: when AFR + CYP2D6 fires `EUROCENTRIC_IMBALANCE`, the layer is doing the thing the platform's positioning says it does, in code, with a rule_id, in an audit log.

The connection back to founder-research: see [`founder-research/andrea_gaedigk/`](founder-research/andrea_gaedigk/) for the conversation with Andrea Gaedigk (PharmVar steward) confirming *"there is unfortunately not much info for the Indian subcontinent"* — independent third-party validation that the bias signals this detector emits are real, structural data-gaps, not a model artefact.

---

## 10. `SufficiencyCheckpoint` — composition façade

**Module:** `core/evidence_sufficiency/checkpoint.py`

**Class:** `SufficiencyCheckpoint`

This is the **single integration point** the orchestrator calls. One class, one public method (`evaluate`), returns one `CheckpointResult`.

### What it composes

```python
class SufficiencyCheckpoint:
    """Composition façade for the full ESL stack."""

    def __init__(self, *,
                 sufficiency_agent: ContextSufficiencyAgent | None = None,
                 verifier: SetLevelEvidenceVerifier | None = None,
                 uncertainty_scorer: UncertaintyScoringEngine | None = None,
                 bias_detector: PopulationEvidenceBiasDetector | None = None):
        ...

    def evaluate(self, context, claims, ...) -> CheckpointResult:
        # 1. ContextSufficiencyAgent runs:
        #      coverage analyzer  → ClaimCoverageAnalysis
        #      conflict detector  → tuple[ConflictFinding]
        #      provenance tracker → ProvenanceCoverageReport
        #      decision engine    → SufficiencyReport
        # 2. SetLevelEvidenceVerifier reads coverage + conflicts → EvidenceVerificationResult
        # 3. UncertaintyScoringEngine reads coverage + conflicts → UncertaintyReading
        # 4. PopulationEvidenceBiasDetector reads coverage → tuple[BiasFinding]
        # 5. Roll into a single EvidenceSufficiencyTrace audit record
        # 6. Decide may_synthesize from sufficiency.allows_synthesis ∧ uncertainty != UNSAFE
        ...
```

### `CheckpointResult`

```python
@dataclass(frozen=True)
class CheckpointResult:
    sufficiency: SufficiencyReport         # decision + rationale + R-rule id
    verdict: EvidenceVerificationResult    # 5-value verdict + V-rule id
    uncertainty: UncertaintyReading        # 4-tier score + U-rule id
    bias_findings: tuple[BiasFinding, ...] # 3 closed bias kinds
    trace: EvidenceSufficiencyTrace        # frozen 7-dimension audit record
    may_synthesize: bool                   # the single boolean the orchestrator reads
    correlation_id: str
```

The orchestrator reads exactly one boolean to decide whether to proceed: `may_synthesize`. Everything else is for the audit record and the narrative layer.

### Off by default — the integration contract

```python
# anukriti-swarm/core/orchestrator/coordinator.py
class ExecutionCoordinator:
    def __init__(self, *, sufficiency_checkpoint: SufficiencyCheckpoint | None = None):
        self.sufficiency_checkpoint = sufficiency_checkpoint

    def execute(self, ...):
        # Step 1-3: existing pipeline (retrieval, verification, narrative)
        # Step 3.5: Sufficiency Checkpoint — short-circuits if None
        if self.sufficiency_checkpoint is not None:
            result = self.sufficiency_checkpoint.evaluate(context, claims, ...)
            if not result.may_synthesize:
                return self._refuse(result)
            # synthesis proceeds with the audit record propagated
        # Step 4: existing synthesis
```

Default is `None`. The 7 byte-locked flagship demos construct the coordinator without the arg → zero behavior change. Opt-in is explicit:

```python
ExecutionCoordinator(sufficiency_checkpoint=SufficiencyCheckpoint())
```

This pattern is the platform's discipline. Constructor args show up in code review; feature flags hide in YAML.

---

## 11. End-to-end worked examples

The two flagship sufficiency demos in the repo demonstrate the layer concretely. Both run from a clean checkout, deterministically, with documented signatures.

### Scenario 1: `evidence_sufficiency_demo` (3 canonical scenarios)

**File:** `anukriti-swarm/demos/evidence_sufficiency_demo.py`

```
Scenario                                  Decision      Verdict      Uncertainty  Bias  Pass?
1. Clopidogrel + CYP2C19 + SAS            sufficient    supported    low          0     ✓
2. Carbamazepine + HLA-B*15:02 + EAS      sufficient    supported    low          0     ✓
3. Codeine + CYP2D6 + AFR                 downgrade     uncertain    high         0     ✗
```

The AFR ✗ is **not a bug.** It's R9 firing honestly: AFR population support for CYP2D6 is empirically weak in the seed KG, so the layer downgrades and the run is recorded as a deliberate refusal-to-synthesize-confidently, not a soft-pass.

This is the layer's value proposition rendered in one line of demo output: *"the platform refuses to fake confidence on populations where the evidence base is genuinely thin."*

### Scenario 2: `evidence_sufficiency_abstention_demo` (6 adversarial)

**File:** `anukriti-swarm/demos/evidence_sufficiency_abstention_demo.py`

```
#  Scenario                Decision       Verdict        Uncertainty  Pass?  (Rule)
1  no phenotype            block          insufficient   high         ✗      (R2)
2  avoid vs use clash      block          refuted        unsafe       ✗      (R1 + V1)
3  broken provenance       abstain        supported      low          ✗      (R4)
4  population missing      escalate       insufficient   high         ✗      (R5)
5  AMR bias signals        downgrade      uncertain      high         ✗      (3 bias kinds)
6  adaptive ABORT          request_more   n/a            n/a          ✗      (budget exhausted)
```

**All 6 ✗ are features**, not failures. Every refusal names a rule. The audit record for each one carries:
- The rule_id (R1..R12 from sufficiency, V1..V10 from verifier, U1..U9 from uncertainty)
- The rationale string
- The full coverage analysis that caused the refusal
- The conflict findings (if any)
- The provenance report (if any)
- The bias findings (if any)

A regulator can replay any refusal by checking out the same swarm version and re-running the demo. Same input always produces same refusal.

### Worked example: SAS + CYP2C19 + clopidogrel (the canonical pass case)

Continuing from the [`DETERMINISTIC_ENGINE_DEEP_DIVE.md` worked example](DETERMINISTIC_ENGINE_DEEP_DIVE.md#4-end-to-end-worked-example-clopidogrel--cyp2c19): patient is `*2/*2`, phenotype is `Poor Metabolizer`, drug is `clopidogrel`, population is `SAS`.

**Step 1 — Coverage analysis** (`EvidenceCoverageAnalyzer`)

For the canonical scenario the seed KG has all six facets:

```python
ClaimCoverageAnalysis(
    drug="clopidogrel", gene="CYP2C19", genotype="*2/*2", population=SAS,
    facet_states={
        ALLELE:        COVERED,  # *2 attested in PharmGKB:PA166104948 + PMID:35034351
        PHENOTYPE:     COVERED,  # CPIC named-diplotype table 2022.1
        CPIC:          COVERED,  # CPIC clopidogrel guideline 2022.1
        POPULATION:    COVERED,  # 1000G phase 3, SAS *2 frequency 0.36
        RECOMMENDATION: COVERED, # CPIC table-2 action mapped from PM phenotype
        CONFLICT_FREE: COVERED,  # no clashing sources detected
    },
    facet_evidence_refs={ ... },
    coverage_ratio=1.0,
    is_complete=True,
)
```

**Step 2 — Conflict detection** (`ConflictDetectionAgent.detect`)

Returns `()` — empty tuple. No phenotype-disagreement, no recommendation-clash, no population-divergence. `CONFLICT_FREE` facet stays `COVERED`.

**Step 3 — Provenance tracking** (`ProvenanceCoverageTracker`)

All 4 dimensions complete (every record has rule_id, generating_agent, parent chain, ≥1 deterministic evidence_source). `provenance.is_complete = True`.

**Step 4 — Sufficiency decision** (`SufficiencyDecisionEngine.decide`)

Walking the rule table:
- R1: `CONFLICT_FREE != MISSING` and `any_hard = False` → skip
- R2-R3: `PHENOTYPE`, `RECOMMENDATION` not MISSING → skip
- R4: `provenance.is_complete = True` → skip
- R5-R7: nothing MISSING → skip
- R8-R10: nothing UNCERTAIN → skip
- R11: `CONFLICT_FREE != UNCERTAIN` → skip
- **R12 fires**: `(SUFFICIENT, "R12: all facets covered, no conflict, provenance complete")`

**Step 5 — Set-level verifier** (`SetLevelEvidenceVerifier.verify`)

V1-V9 all skip; V10 fires: `(SUPPORTED, "V10: all covered, no hard conflict, pathway non-empty")`. (KG pathway from `*2 → CYP2C19 → metabolizes → clopidogrel` is reachable in the seed KG.)

**Step 6 — Uncertainty scoring** (`UncertaintyScoringEngine.score`)

U1-U8 all skip; U9 fires: `LOW`. Action: `PROCEED`.

**Step 7 — Bias detection** (`PopulationEvidenceBiasDetector.detect`)

Empty tuple. SAS *2 evidence is well-attested (CPIC 2022 + 1000G phase 3); no Eurocentric imbalance, no scarcity, no unsupported extrapolation.

**Step 8 — `CheckpointResult.may_synthesize = True`**. Synthesis proceeds. The narrative layer (downstream) renders the CPIC text into the user-facing recommendation.

### Worked example: AFR + CYP2D6 + codeine (the canonical refusal-with-honesty case)

Same patient profile, but population is `AFR` and gene is `CYP2D6` and drug is `codeine`.

**Step 1 — Coverage** — `POPULATION` facet is `UNCERTAIN`. The seed KG has AFR frequency edges for `*1`, `*2`, `*4`, but **no AFR-specific evidence papers** for the AFR + CYP2D6 + codeine triple. The analyzer flags `POPULATION = UNCERTAIN` with reason `"AFR-specific evidence papers not found for CYP2D6 codeine response"`.

**Step 4 — Sufficiency decision** —
- R1-R7: skip
- R8: `RECOMMENDATION != UNCERTAIN` → skip
- M4 (off by default): `allow_cross_ancestry_extrapolation = False` → skip
- **R9 fires**: `(DOWNGRADE, "R9: AFR population support weak — confidence lowered")`

**Step 6 — Uncertainty** — U3 fires: `HIGH`. Action: `REQUEST_MORE`.

**Step 8 — `may_synthesize = True` (DOWNGRADE allows synthesis)**, but with `uncertainty.tier = HIGH` propagated. The narrative layer reads both signals and renders an explicit caveat:

> *"CYP2D6 [diplotype]: Intermediate Metabolizer. The recommendation is based primarily on European-ancestry evidence; African-ancestry-specific support for this gene-drug pair is limited in our reference set, so confidence is lowered."*

If the operator wants to opt into the cross-ancestry hedge instead:

```python
SufficiencyDecisionEngine(allow_cross_ancestry_extrapolation=True)
```

Now M4 fires (preconditions all met): `(EXTRAPOLATION_WITH_CROSS_ANCESTRY_SUPPORT, "M4: AFR direct population evidence thin but ALLELE + PHENOTYPE + CPIC + RECOMMENDATION all covered — cross-ancestry extrapolation hedge applied")`. Same `may_synthesize = True`, but the rule_id and rationale string explicitly name the epistemic posture taken.

---

## 12. What this layer deliberately does NOT do

For honesty, here is the closed list of things the layer **does not** do:

- **No probability outputs.** Every layer is categorical. Sufficiency = 8 enum values. Verdict = 5 enum values. Uncertainty = 4 enum values. Bias = 3 enum values + numeric measurements with explicit thresholds. There is no "0.73 confident" output anywhere.

- **No LLM in the decision path.** Every rule fires from `if` statements over closed enums. 244 pytest tests pin the rules byte-identically. An LLM can never override a refusal; the closest the LLM gets is the optional generative narrative layer downstream of synthesis.

- **No retrieval, no graph reasoning, no document opening.** The layer reads what the upstream pipeline has already produced and applies the rule tables. This is the SURE-RAG / ECR discipline — separate "do retrieval" from "judge the bundle." If the layer needed retrieval, it would be a feedback loop that's hard to audit.

- **No clinical decision-making.** The layer says "may synthesis run?" — yes/no with a rationale. It does not say "this patient will tolerate the drug." That decision belongs to the clinician with the full chart.

- **No general-purpose contradiction reasoner.** The conflict detector covers exactly 3 pharmacogenomic classes. "Two papers worded similarly but slightly different" is not its concern.

- **No "partial coverage" gradations.** A facet is COVERED, MISSING, or UNCERTAIN. Three states, no fourth. No "60% covered" or "weak coverage." The closure is the scope firewall.

- **No automatic policy tuning.** Thresholds (`tolerance=0.15` for frequency divergence, `scarcity_ratio=0.5` for bias) are constants in the code. Changing them is a code change, with tests, with review. There is no learned policy, no Bayesian update, no online tuning.

- **No replacement for the deterministic engine.** The ESL is *gating* — it decides whether to deliver the upstream engine's output. It does not produce the output itself. Removing the ESL would not change what the engine computes; it would only remove the safety gate.

- **No automatic recovery from missing evidence.** When R5 fires (POPULATION missing), the response is `ESCALATE` — surface to human review. The layer does not "go fetch more evidence" automatically. The adaptive retrieval loop (separate module, also in `core/evidence_sufficiency/retrieval/`) can be wired in for `REQUEST_MORE` cases, but the policy decision to do so is explicit.

- **No `IndianRegion` or `CommunityLevel` today.** The 5-value `SuperPopulation` enum is the current population resolution. Phase-B work (per [`IDEA_REFINEMENT_AND_PHASING_2026-05-14.md`](IDEA_REFINEMENT_AND_PHASING_2026-05-14.md) §B1-B5) will add a 6-value `IndianRegion` enum and a `CommunityLevel` open extension point — gated on LASI-DAD data access landing first. The architecture is designed to absorb these as closed-enum extensions; the rules engines will need new rule rows but not redesign.

---

## Appendix — file map for this deep-dive

| Concept | File |
|---|---|
| 6-facet closed enum + frozen record | `anukriti-swarm/core/evidence_sufficiency/coverage/claim_coverage.py` |
| Coverage analyzer | `anukriti-swarm/core/evidence_sufficiency/coverage/analyzer.py` |
| Provenance tracker (4 dimensions) | `anukriti-swarm/core/evidence_sufficiency/coverage/provenance_tracker.py` |
| Conflict detector (3 closed classes) | `anukriti-swarm/core/evidence_sufficiency/conflict/agent.py` |
| Sufficiency decision engine (R1..R12 + M4) | `anukriti-swarm/core/evidence_sufficiency/sufficiency/decision_engine.py` |
| Context sufficiency agent (orchestration façade for phase 1) | `anukriti-swarm/core/evidence_sufficiency/sufficiency/context_agent.py` |
| Set-level verifier (V1..V10) | `anukriti-swarm/core/evidence_sufficiency/verifier/set_level.py` |
| Verdict result + closed enum | `anukriti-swarm/core/evidence_sufficiency/verifier/result.py` |
| Uncertainty engine (U1..U9) + 4-tier enum | `anukriti-swarm/core/evidence_sufficiency/uncertainty/engine.py` |
| Bias detector (3 closed kinds) | `anukriti-swarm/core/evidence_sufficiency/uncertainty/bias_detector.py` |
| Frozen 7-dim audit record | `anukriti-swarm/core/evidence_sufficiency/trace.py` |
| Composition façade | `anukriti-swarm/core/evidence_sufficiency/checkpoint.py` |
| Orchestrator integration point | `anukriti-swarm/core/orchestrator/coordinator.py` (Step 3.5) |
| Architecture spec (350 lines) | `anukriti-swarm/architecture/evidence-sufficiency.md` |
| Pharmacogenomic KG schema (10 NodeKind, 7 EdgeKind) | `anukriti-swarm/knowledge_graph/schema.py` |
| KG seed (37 nodes, 34 edges) | `anukriti-swarm/knowledge_graph/seed.py` |
| Multi-hop reasoner (BFS, population-aware) | `anukriti-swarm/knowledge_graph/reasoner.py` |
| 3-scenario canonical demo | `anukriti-swarm/demos/evidence_sufficiency_demo.py` |
| 6-scenario adversarial demo | `anukriti-swarm/demos/evidence_sufficiency_abstention_demo.py` |
| Pytest suite (244 tests, includes ESL) | `anukriti-swarm/tests/unit/test_sufficiency.py` |

---

## Cross-references

- [`DETERMINISTIC_ENGINE_DEEP_DIVE.md`](DETERMINISTIC_ENGINE_DEEP_DIVE.md) — the upstream engine this layer gates
- [`IDEA_REFINEMENT_AND_PHASING_2026-05-14.md`](IDEA_REFINEMENT_AND_PHASING_2026-05-14.md) — Phase B extensions that add new rule rows (`IndianRegion`, `FOUNDER_EFFECT_BURDEN` facet, `VARIANT_NOVELTY` state)
- [`docs/09-evidence-and-safety.md`](docs/09-evidence-and-safety.md) — friendly intro to sufficiency layer concepts
- [`docs/06-why-deterministic.md`](docs/06-why-deterministic.md) — why the platform-wide closed-enum discipline exists
- [`founder-research/andrea_gaedigk/`](founder-research/andrea_gaedigk/) — Phase-C scientific outreach validating the South Asian data-gap thesis the bias detector encodes
- [`../anukriti-swarm/architecture/evidence-sufficiency.md`](../anukriti-swarm/architecture/evidence-sufficiency.md) — full design spec, 30-requirement → file mapping

---

*This document was written 2026-05-16 as a permanent record of the
Evidence Sufficiency Layer's actual behavior, derived directly from
the source files cited in the appendix. If a future session changes
any of the rule tables described here (adding a rule, changing rule
priority, adding a facet, adding a decision value), update this
document in the same commit that lands the change — divergence
between this doc and the code is a documentation regression, not
just a stale doc.*
