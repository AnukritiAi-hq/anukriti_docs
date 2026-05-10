# 13 — What We've Built

> Thirteen modules, one system. Let's watch it all work for one
> question, from start to finish.

---

## The recap

You've now met every part of our AI system:

| Module | Thing |
|--------|-------|
| 00 | An **agent** is a helper that decides |
| 01 | We use **many specialist agents**, not one big one |
| 02 | Agents talk via **labeled envelopes on a bus** |
| 03 | The **orchestrator** plans and routes |
| 04 | The **GenerativeBoundary** stops forbidden actions |
| 05 | Everyone writes in the **shared notebook** |
| 06 | **Memory** lets past runs advise new ones |
| 07 | **Retrieval** uses multi-strategy adaptive lookup |
| 08 | The **knowledge graph** connects facts by arrows |
| 09 | **MCP tools** provide a standard protocol |
| 10 | **Verification** runs 4 safety engines on every answer |
| 11 | **Sufficiency** refuses honestly when evidence is thin |
| 12 | **Observability** records everything for replay |

One system. Let's trace one full run through all thirteen parts.

---

## The question

Priya (no, a different Priya — the patient from Module 01, not the
frosting helper) is South Asian. Her genotype shows CYP2C19
star-2 slash star-2. Her doctor is thinking about prescribing
clopidogrel.

The query to our system:

> *drug: clopidogrel*
> *gene: CYP2C19*
> *population: SAS*
> *genotype: \*2/\*2*

---

## The flow, end to end

### Step 1: The request lands

The frontend sends a `POST /api/run` to the backend. FastAPI
receives the JSON, validates it against a Pydantic record, and
confirms:

- `drug`: "clopidogrel" ✓
- `gene`: "CYP2C19" ✓
- `population`: validated as `SuperPopulation.SAS` (closed enum)
- `genotype`: "*2/*2"

**Validation alone** catches misspelled populations or invalid
drug strings before any agent runs.

### Step 2: SwarmRuntime starts

The backend instantiates a `SwarmRuntime` with an
`AsyncQueueEventStream` (so the frontend can watch live over
WebSocket).

→ Event emitted: `RUN_STARTED`

### Step 3: Context assembly (Stage 1)

The `ContextAssembler` creates a `SwarmExecutionContext`:

```python
SwarmExecutionContext(
    correlation_id="a986dec2746f",
    query=...,
    population=SuperPopulation.SAS,
    gene="CYP2C19",
    diplotype="*2/*2",
    phenotype_inference=None,     # to be filled
    evidence_bundle=None,         # to be filled
    verification_outcome=None,    # to be filled
    activated_agents=(),          # append-only
    errors=(),                    # append-only
    trace=OrchestrationTrace(...),
)
```

### Step 4: Memory consultation (if enabled)

The `MCPMemoryAdvisor` looks up past runs with the same (gene,
drug, population). It finds three prior runs — all agreed on Poor
Metabolizer with a "prasugrel or ticagrelor" recommendation.

→ Trace step: `memory.consult` with a `PriorRunDigest`

The Planner now has a hint: *"last 3 similar runs gave a clean
PM + prasugrel result."*

### Step 5: Orchestration (Stage 2)

The **Planner** (LLM + deterministic fallback) proposes a plan:

```
1. pharmacogene_agent (CYP2C19) — derive phenotype
2. population_agent (SAS) — get frequency context
3. evidence_agent — retrieve CPIC docs + PubMed citations
4. sufficiency_checkpoint — check if we can answer
5. verification_agent — 4-engine safety check
6. narrative_agent — write the explanation (guarded)
```

The **Router** resolves each step against the `AgentRegistry`.
The **Coordinator** kicks off the plan.

→ Events emitted: `ORCHESTRATOR_ACTIVATED`, `AGENT_ACTIVATED`
for each of the three specialist agents in sequence.

### Step 6: Pharmacogene agent fires

The CYP2C19 agent:
1. Receives `AgentContextEnvelope` with `context_type = PHARMACOGENE`
2. Looks up `*2/*2` in the CPIC 2022.1 named-diplotype table
3. Finds: "Poor Metabolizer, activity score 0.0"
4. Emits an envelope with `context_type = GENOTYPE` carrying the
   phenotype call + `ProvenanceStamp(source_id="CPIC:2022.1")`

### Step 7: Population agent fires

The SAS population agent:
1. Receives an envelope with `context_type = POPULATION`
2. Looks up CYP2C19 *2 frequency in SAS: 0.36
3. Emits an envelope with `context_type = POPULATION` carrying
   the frequency + bias-check status

### Step 8: Evidence retrieval (Stage 3)

The **AdaptiveRetrievalController** runs:

1. `DenseSemanticRetriever` finds 8 candidate docs
2. `PopulationAwareRetriever` re-ranks for SAS boost
3. After re-ranking: sufficiency check — *do we have enough?*
4. If yes, stop. If no, run the graph retriever next.

For Priya's scenario, the first two retrievers produce enough
(CPIC guideline + primary clopidogrel paper PMID:34032273).

→ Events: `RETRIEVAL_STARTED`, `RETRIEVAL_COMPLETED`

### Step 9: Knowledge graph walk

The **`MultiHopReasoner`** walks the KG from SAS to clopidogrel:

```
SAS --HIGHER_FREQUENCY_IN (0.36)--> CYP2C19 *2
CYP2C19 *2 --ASSOCIATED_WITH--> Poor Metabolizer
Poor Metabolizer --CONTRAINDICATED_FOR--> clopidogrel
```

Three hops, one path, weight 0.36 × 1.0 × 1.0 = 0.36.

→ Events: `KG_TRAVERSAL_STARTED`, `KG_TRAVERSAL_COMPLETED`

### Step 10: Sufficiency checkpoint (Stage 3.5)

The **`SufficiencyCheckpoint`** evaluates:

- ALLELE: COVERED
- PHENOTYPE: COVERED
- CPIC: COVERED
- POPULATION: COVERED
- RECOMMENDATION: COVERED
- CONFLICT_FREE: COVERED

All six green. Provenance: all four dimensions pass. No conflicts.

- R-rule: **R12 fires** → `SufficiencyDecision.SUFFICIENT`
- V-rule: V10 fires → `EvidenceVerdict.SUPPORTED`
- U-rule: U9 (none of U1-U8 matched) → `UncertaintyScore.LOW`
- Bias detector: 0 findings

→ Event: `SUFFICIENCY_CHECKED`

### Step 11: Verification (Stage 4)

The **`BiomedicalVerificationAgent`** runs all 4 engines:

1. Shape: all claims have source + evidence_ref + rule_id ✓
2. Existence: PMID:34032273 resolves in evidence cache ✓
3. Truth: re-derived phenotype matches the claim ✓
4. Chain: provenance complete narrative→rec→phenotype→rule→evidence ✓

Outcome: `grounded`, decision: `deliver`.

→ Event: `VERIFICATION_CHECKED`

### Step 12: Synthesis (Stage 5)

The **Narrative agent** (guarded by `GenerativeBoundary`) calls
Gemini with a structured prompt containing:

- The deterministic phenotype call
- The population context
- The CPIC recommendation text (verbatim)
- The citations

It writes a readable paragraph:

> *"For a South Asian patient with CYP2C19 \*2/\*2 genotype (Poor
> Metabolizer), CPIC 2022.1 strongly recommends avoiding
> clopidogrel. Alternative antiplatelet agents such as prasugrel
> or ticagrelor are preferred. In South Asian populations, the
> CYP2C19 \*2 allele has a frequency of ~36%, making this an
> important population-specific consideration. Source: CPIC
> guideline, PMID:34032273."*

The GenerativeBoundary validates: no phenotype inferred, no
recommendation overridden, no verification bypassed, no claim
fabricated. All four checks green.

→ Events: `SYNTHESIS_STARTED`, `SYNTHESIS_COMPLETED`

### Step 13: Run completes

The **`UnifiedExecutionReport`** is assembled:

```python
UnifiedExecutionReport(
    correlation_id="a986dec2746f",
    drug="clopidogrel",
    gene="CYP2C19",
    population=SuperPopulation.SAS,
    diplotype="*2/*2",
    phenotype="Poor Metabolizer",
    recommendation_text="Avoid clopidogrel. Use prasugrel or...",
    citations=["CPIC:2022.1", "PMID:34032273"],
    sufficiency_decision=SufficiencyDecision.SUFFICIENT,
    verification_score=VerificationScore.grounded,
    uncertainty=UncertaintyScore.LOW,
    narrative="For a South Asian patient...",
    total_events=14,
    latency_ms=1.2,
    # ...18 fields total, all frozen
)
```

→ Event: `RUN_COMPLETED`

### Step 14: Persistence

**`MCPPersistenceHook`** writes the full run to MongoDB (or
in-memory):

- Memory summary
- Trace
- Context snapshot
- Provenance chain
- Evidence records
- Verification logs

A future memory lookup on this same (gene, drug, population) will
find this run.

### Step 15: Response

Backend sends the final JSON over HTTP. The WebSocket has already
streamed all 14 events live. Frontend shows:

- Green sufficiency banner: ✓
- Phenotype card: Poor Metabolizer
- CPIC recommendation card
- Citations with resolvable links
- KG visualization showing the 3-hop path
- Trace timeline with timestamps

---

## What happened, in one picture

```
Query → assemble → memory-consult → plan → route → run pipeline:
                                           │
            ┌──────────────────────────────┼──────────────────────────┐
            │                              │                          │
            ▼                              ▼                          ▼
     pharmacogene                   population                   evidence retrieval
     (CYP2C19 → PM)                 (SAS, 36%)                   (docs + KG walk)
            │                              │                          │
            └──────────────┬───────────────┴──────────────────────────┘
                           ▼
                    sufficiency checkpoint (6 facets green, R12 → SUFFICIENT)
                           │
                           ▼
                    verification (4 engines pass)
                           │
                           ▼
                    narrative synthesis (guarded by GenerativeBoundary)
                           │
                           ▼
                    UnifiedExecutionReport
                           │
                           ▼
                    MCP persistence + WebSocket response
```

**14 events. ~1.2 ms deterministic + ~400 ms LLM narrative.** Full
audit trail. Replayable.

---

## Why this shape is special

You've seen that **every decision in this run was traceable**.

- The phenotype call came from CPIC:2022.1 (named diplotype table)
- The frequency came from the SAS seed in the knowledge graph
- The recommendation text came verbatim from the CPIC guideline
- The narrative was paraphrased under the GenerativeBoundary
- Every verification step either ran or the run blocked
- Every event was persisted

There is no step where a component said "I just think so." There
is no step where an LLM invented a fact. There is no step where
sufficiency was skipped.

That's the platform. That's what agentic AI, done carefully for
a high-stakes domain, looks like.

---

## If Priya were African-American and the gene were CYP2D6

Different story. The `PopulationEvidenceBiasDetector` would fire
`ANCESTRY_SCARCITY`. The sufficiency decision would be
`DOWNGRADE` (R9: POPULATION UNCERTAIN). The verdict would be
`UNCERTAIN` (V7). The uncertainty tier would be HIGH. The
narrative would include a pinned refusal banner.

The system would **not** emit a confident answer. It would
**honestly say**: *"we don't have enough AFR-specific evidence
for CYP2D6 to make a strong recommendation."*

Same pipeline. Different outcome. **The outcome is the right
one for the evidence.**

---

## What you learned

Before this module: the pieces felt separate.

Now: they fit. Orchestration plans which agents run. Agents
contribute to a shared notebook. Retrieval fetches evidence
adaptively. The graph walks paths. Tools provide a standard
protocol. Sufficiency decides whether to answer. Verification
decides whether to emit. Boundary enforces LLM safety. Memory
advises. Observability watches. Replay reconstructs.

Every piece has **one job**. Every piece is **replaceable**. Every
piece has **tests**. Every decision is **logged and traceable**.

This is how we get to AI you can trust with decisions that
affect real people.

---

Next up: **[14 — Where to Go Next](14-where-to-go-next.md)**

The course is done. You understand the system. Now — what files
should you actually open, and what would be a good first thing
to build?
