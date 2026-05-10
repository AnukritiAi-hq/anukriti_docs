# Module 10 — How the Pieces Talk

> Prerequisites: [02 The Three Repos](02-the-three-repos.md), [04 Architecture](04-architecture.md), [07 Tech Stack](07-tech-stack.md)

---

## The question we're answering

A query lands at the swarm's API. How does it flow across three
repos, through multiple agents, into the knowledge graph, back out,
and finally emit a structured response? What are the actual wire
formats? How is scope enforced at every hop?

---

## The full request flow

```
Client ─────────────▶  swarm backend            (FastAPI + websockets)
                            │
                            │  (1) validate query
                            │  (2) instantiate SwarmRuntime
                            ▼
                       SwarmRuntime.run()
                            │
           ┌────────────────┼────────────────┐
           ▼                ▼                ▼
     Stage 1: assemble   Stage 2: orchestrate
                            │
                            │  agent-to-agent via
                            │  AgentMessageBus +
                            │  AgentContextEnvelope
                            ▼
                       agents/orchestrator/ + agents/pharmacogene/ +
                       agents/evidence/ + agents/verification/
                            │
                            │  agents call rules/phenotype_rules.py
                            │  which re-exports
                            │  anukriti_pgx_core.PhenotypeEngine
                            ▼
                       pgx-core (library)
                            │  deterministic phenotype call
                            ▼
                       returns frozen Pydantic record
                            │
                            ▼
                       Stage 3: retrieval (multi-strategy + KG walk)
                            ▼
                       Stage 3.5: sufficiency checkpoint (opt-in)
                            ▼
                       Stage 4: verification (4 safety engines)
                            ▼
                       Stage 5: narrative synthesis (LLM, guarded)
                            │
                            ▼
                       UnifiedExecutionReport
                            │
                            │  persisted via MCP layer
                            │  to MongoDB (or in-memory)
                            ▼
                       Client ◀──────── response (JSON) +
                                        live event stream
                                        via /ws/run
```

Three repos touched in one request:

1. **swarm** — routes, orchestrates, reasons, verifies, synthesizes
2. **pgx-core** — deterministic phenotype inference (called as a
   Python import, not a network call)
3. **anukriti** — not in this flow, but the product would call the
   swarm's `/api/run` endpoint if it wanted the research platform's
   richer reasoning

The product (anukriti) and the research platform (swarm) don't
directly call each other today — they're independent consumers of
pgx-core. Future integration is tracked in the pgx-core
`PROJECT_CONTEXT.md` forward-work items.

---

## The agent envelope — wire format for A2A

When agents talk to each other, they pass frozen Pydantic records
called `AgentContextEnvelope`. From
`anukriti-swarm/interoperability/shared_context/envelope.py`:

```python
class BiomedicalContextType(str, Enum):
    POPULATION = "population"
    GENOTYPE = "genotype"
    PHARMACOGENE = "pharmacogene"
    EVIDENCE = "evidence"
    VERIFICATION = "verification"
    CONFIDENCE = "confidence"
    PROVENANCE = "provenance"

@dataclass(frozen=True)
class AgentContextEnvelope:
    correlation_id: str
    source_agent: str
    target_agent: str
    context_type: BiomedicalContextType   # ← closed enum — scope firewall
    payload: Mapping[str, Any]
    timestamp: datetime
    provenance_chain: tuple[ProvenanceStamp, ...]
```

**The `context_type` is a closed 7-value enum.** An agent cannot
receive a message with `context_type = "clinical_workflow"` or
`context_type = "general_question"` — Pydantic rejects at
construction.

This is the scope firewall from Module 06, applied at the inter-
agent boundary. Even if a contributor adds a new agent that tries
to emit a generic context type, the message fails to construct.

---

## The agent bus — no direct calls

Agents don't call each other directly. From
`interoperability/agent_bus/bus.py`:

```python
class AgentMessageBus:
    def publish(self, envelope: AgentContextEnvelope) -> None: ...
    def subscribe(
        self,
        agent_name: str,
        context_type: BiomedicalContextType,   # scoped subscription
        handler: Callable,
    ) -> None: ...
```

Subscribers specify **which closed-enum context type** they handle.
A pharmacogene agent subscribes to `PHARMACOGENE` envelopes. A
population agent subscribes to `POPULATION` envelopes. Mismatched
routing is rejected at the bus layer — the bus won't route a
`POPULATION` envelope to a pharmacogene agent.

The bus keeps a log of every envelope for observability. Every
delivery produces an activation log with source, target,
context_type, and a provenance stamp.

---

## Provenance propagation

Every envelope carries its `provenance_chain`:

```python
@dataclass(frozen=True)
class ProvenanceStamp:
    source_id: str             # e.g. "PMID:34032273" or "CPIC:2022.1-CYP2C19"
    source_kind: str           # "evidence_paper" | "cpic_guideline" | "agent_output"
    attribution: str           # which agent/module produced this
    timestamp: datetime
```

When Agent A produces output, it stamps it with its provenance.
When Agent B consumes that output to produce its own, B **appends**
its stamp to A's chain. So by the time the narrative synthesizer
sees data, the chain shows: `evidence paper → pharmacogene agent
→ verification agent → synthesis agent`.

This is what the `ProvenanceValidator` (engine 4 in Module 09)
checks — is the chain continuous from narrative back to evidence?
If a step is missing, verification blocks.

---

## MCP — persistence surface for the platform

**MCP** stands for Model Context Protocol. In this platform, it's
the layer that persists everything a run produces. Six services
from `integrations/mcp/`:

| Service | Collection | Role |
|---------|------------|------|
| `MCPExecutionMemory` | `memory` | Run summaries (gene, drug, population, outcome) |
| `MCPTraceStore` | `traces` | Full `OrchestrationTrace` records |
| `MCPContextManager` | `contexts` | Serialized `SwarmExecutionContext` snapshots |
| `MCPProvenanceStore` | `provenance` | PROV-DM structured claim chains |
| `MCPEvidenceCache` | `evidence` | Biomedical papers, indexed by gene |
| `MCPVerificationLog` | `verification_logs` | Per-check audit records |

Each service registers tools on a shared `MCPToolRegistry`. **31 tools
across 6 services today.** Each tool is an MCP-standard call with a
closed JSON schema.

### MongoDB or in-memory

The backend is swappable. If `MONGODB_URI` is set, MCP writes to
real MongoDB. If unset, `InMemoryBackend` kicks in — no DB needed
for dev/demo.

### Why MCP specifically

MCP gives us a standard pattern across persistence concerns:

- One shared client, multiple typed services
- Built-in observability (per-tool call latency, volume, errors)
- Clean mocking (swap the backend for testing)
- Replay: `MCPRetrieval.replay(correlation_id)` reconstructs a full
  `SwarmExecutionContext` from persisted records

**Replay** is the key value. A run from 3 months ago can be
re-executed with its original inputs, byte-for-byte, because every
input and intermediate was persisted.

---

## The WebSocket event stream

While a run executes, the backend emits `RuntimeEvent`s over
`/ws/run`. From `anukriti-swarm/core/runtime/events.py`:

```python
class RuntimeEventKind(str, Enum):
    RUN_STARTED = "run_started"
    ORCHESTRATOR_ACTIVATED = "orchestrator_activated"
    AGENT_ACTIVATED = "agent_activated"
    RETRIEVAL_STARTED = "retrieval_started"
    RETRIEVAL_COMPLETED = "retrieval_completed"
    KG_TRAVERSAL_STARTED = "kg_traversal_started"
    KG_TRAVERSAL_COMPLETED = "kg_traversal_completed"
    SUFFICIENCY_CHECKED = "sufficiency_checked"
    VERIFICATION_CHECKED = "verification_checked"
    SYNTHESIS_STARTED = "synthesis_started"
    SYNTHESIS_COMPLETED = "synthesis_completed"
    RUN_COMPLETED = "run_completed"
```

**12 closed event kinds.** The frontend binds each kind to a
specific panel — e.g. `KG_TRAVERSAL_COMPLETED` triggers an update
to the D3 force graph. No freeform event types; adding a new panel
requires adding a new event kind here and a handler there —
compile-time / review-time, not runtime.

A typical Priya run produces 14 events. The AFR abstention produces
13 (synthesis is skipped). Both numbers are pinned in demo
regression tests.

---

## The runtime event as a reusable primitive

`RuntimeEvent` is frozen and JSON-serializable:

```python
@dataclass(frozen=True)
class RuntimeEvent:
    kind: RuntimeEventKind
    correlation_id: str
    timestamp: datetime
    payload: Mapping[str, Any]
```

`EventStream` is an abstract protocol:

```python
class EventStream(Protocol):
    def emit(self, event: RuntimeEvent) -> None: ...
    def close(self) -> None: ...
```

Two implementations:
- `InMemoryEventStream` — for demos and tests
- `AsyncQueueEventStream` — for the FastAPI WebSocket bridge

The runtime doesn't know or care which one it has. This is the
seam between "synchronous 5ms runtime" and "async per-request
WebSocket streaming." A worker thread runs the runtime; the main
event loop drains the queue and sends to the client. See the
commit history in swarm's `.project-status.md` (session #7 phase 2
commit `6b2f0c4`) for the bug fix where we nearly had an
event-loop-hang.

---

## Request flow concrete: Priya's run

Now let's walk the full sequence for Priya:

```
1. Client POST /api/run
     body: {
       "scenario_id": "clopidogrel_sas",
       "drug": "clopidogrel",
       "gene": "CYP2C19",
       "population": "SAS",
       "genotype": "*2/*2"
     }

2. Backend validates with Pydantic (closed-enum checks)
     → SuperPopulation.SAS, Drug closed enum, etc.

3. Backend instantiates SwarmRuntime(event_stream=AsyncQueueEventStream())
     → emit RUN_STARTED

4. SwarmRuntime.run() begins
     → Stage 1: ContextAssembler → SwarmExecutionContext
     → emit ORCHESTRATOR_ACTIVATED

5. Stage 2: planner → router → coordinator
     → plan: [pharmacogene_agent, population_agent,
              evidence_retrieval, verification]
     → emit AGENT_ACTIVATED ×3 (one per agent)

6. pharmacogene_agent receives AgentContextEnvelope
     context_type=PHARMACOGENE
     → imports rules.phenotype_rules
     → calls anukriti_pgx_core.PhenotypeEngine.infer("CYP2C19", "*2", "*2")
     → returns PhenotypeInference(
         phenotype="Poor Metabolizer",
         activity_score=0.0,
         cpic_table_version="2022.1",
         inference_path="named_diplotype"
       )
     → publishes new envelope: context_type=PHENOTYPE

7. population_agent receives envelope
     context_type=POPULATION
     → looks up CYP2C19 *2 frequency in SAS: 0.36
     → publishes envelope: context_type=EVIDENCE

8. emit RETRIEVAL_STARTED
     → PopulationAwareRetriever re-ranks docs for SAS
     → MultiHopReasoner walks KG paths
     → emit KG_TRAVERSAL_COMPLETED with path list
     → emit RETRIEVAL_COMPLETED

9. (opt-in, if sufficiency_checkpoint != None)
     Stage 3.5: sufficiency evaluation
     → all facets COVERED, no conflicts
     → SufficiencyDecision.SUFFICIENT
     → emit SUFFICIENCY_CHECKED

10. Stage 4: verification
     → 4 safety engines (shape, existence, truth, chain)
     → all pass
     → emit VERIFICATION_CHECKED

11. Stage 5: synthesis
     → emit SYNTHESIS_STARTED
     → narrative agent calls Gemini with structured claim
     → GenerativeBoundary validates LLM output — no forbidden actions
     → emit SYNTHESIS_COMPLETED

12. Emit RUN_COMPLETED
     → UnifiedExecutionReport returned
     → MCPPersistenceHook saves: memory, trace, context, provenance,
       evidence, verification_log

13. Client receives:
     (a) event stream closes
     (b) final JSON report via HTTP response
```

14 events total. Same shape every time. Byte-identical output for
byte-identical input (modulo LLM narrative text, which is
non-deterministic but stays within the GenerativeBoundary).

---

## Closed enums across the whole flow

Count the closed enums we've touched in one request:

| Layer | Enum | Size |
|-------|------|------|
| Input | `SuperPopulation` | 5 |
| Bus | `BiomedicalContextType` | 7 |
| KG | `NodeKind` | 10 |
| KG | `EdgeKind` | 7 |
| Coverage | `ClaimEvidenceFacet` | 6 |
| Coverage | `FacetCoverageState` | 3 |
| Provenance | `ProvenanceDimension` | 4 |
| Conflict | `ConflictKind` | 3 |
| Conflict | `ConflictSeverity` | 2 |
| Recommendation | `RecommendationAction` | 5 |
| Sufficiency | `SufficiencyDecision` | 7 |
| Verdict | `EvidenceVerdict` | 5 |
| Uncertainty | `UncertaintyScore` | 4 |
| Uncertainty | `UncertaintyAction` | 5 |
| Bias | `BiasKind` | 3 |
| Stop signals | `StopSignal` | 3 |
| Events | `RuntimeEventKind` | 12 |
| Boundary | `ForbiddenAction` | 4 |

**Eighteen closed enums in one request flow.** Each is a hard
scope boundary. A drifting value at any of these points raises at
construction, not at runtime. The platform's scope firewall is not
a document — it's 18 code-level locks.

---

## Summary

You now know:

- **One request touches swarm (network-facing) and pgx-core (library
  import).** anukriti is a parallel product, not in this path.
- **Agents communicate via `AgentContextEnvelope`** over
  `AgentMessageBus`, scoped by a closed 7-value
  `BiomedicalContextType`.
- **Provenance propagates** as `ProvenanceStamp` chains, appended at
  every agent hop.
- **MCP persistence** — 6 services, 31 tools, backed by MongoDB or
  in-memory, enabling full replay.
- **WebSocket event stream** — 12 closed `RuntimeEventKind` values,
  emitted per stage, rendered live on the mission-control UI.
- **18 closed enums** are exercised in one request. The scope
  firewall is operational, not aspirational.

Next: [Module 11 — Hands-On](11-hands-on.md). We actually run it.
