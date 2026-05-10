# Glossary

> Plain-English definitions of every agentic-AI term used in this
> course. Alphabetical.

---

## A

### A2A (agent-to-agent) communication
The pattern where agents talk to each other directly (via an
agent bus) instead of through a central controller. Covered in
[Module 02](02-how-agents-talk.md).

### AdaptiveRetrievalController
Our class (in `retrieval/multi_strategy/adaptive_controller.py`)
that runs retrieval strategies one at a time, checking
sufficiency after each. Stops early when evidence is enough.
See [Module 07](07-finding-information.md).

### Agent
A helper with a job that can **decide** things on its own. In code,
a class with a well-defined role, structured inputs, and
structured outputs. [Module 00](00-whats-an-agent.md).

### AgentContextEnvelope
The frozen Pydantic record agents send to each other via the bus.
Has a 7-field schema including a closed-enum `context_type` that
enforces scope at message-construction time. [Module 02](02-how-agents-talk.md).

### AgentMessageBus
The typed pub/sub bus where agents publish envelopes. Subscribers
register for specific `BiomedicalContextType` values. Refuses to
route mismatched envelopes. [Module 02](02-how-agents-talk.md).

### AsyncQueueEventStream
Our async implementation of the `EventStream` protocol. Used for
the live WebSocket UI — events flow from the synchronous
runtime thread through an asyncio queue to the browser.
[Module 12](12-watching-the-agents.md).

---

## B

### Bias detector
The `PopulationEvidenceBiasDetector`. Checks for 3 named bias
patterns (Eurocentric imbalance, ancestry scarcity, unsupported
extrapolation) with concrete numeric thresholds.
[Module 11](11-knowing-when-to-say-no.md).

### BiomedicalContextType
A closed 7-value enum (POPULATION, GENOTYPE, PHARMACOGENE,
EVIDENCE, VERIFICATION, CONFIDENCE, PROVENANCE) that labels every
`AgentContextEnvelope`. Acts as a scope firewall. [Module 02](02-how-agents-talk.md).

### BiomedicalVerificationAgent
The agent that composes all 4 verification engines and produces
a `VerificationOutcome`. [Module 10](10-checking-the-work.md).

### Boundary
Short for `GenerativeBoundary`. [Module 04](04-the-safety-line.md).

---

## C

### ClaimEvidenceFacet
A closed 6-value enum for coverage dimensions: ALLELE, PHENOTYPE,
CPIC, POPULATION, RECOMMENDATION, CONFLICT_FREE.
[Module 11](11-knowing-when-to-say-no.md).

### Closed enum
A Python Enum whose values are fixed at code-write time. Extending
requires modifying the code (triggers review). Used platform-wide
as a scope-firewall mechanism. See [Module 02](02-how-agents-talk.md).

### Conflict (ConflictKind / ConflictSeverity)
A disagreement between evidence sources. Three kinds:
phenotype_divergence, recommendation_divergence,
population_divergence. Two severities: hard, soft.
[Module 11](11-knowing-when-to-say-no.md).

### Context (SwarmExecutionContext)
The shared notebook — the per-run Pydantic record that agents
read from and append to. Frozen sub-records; tuple-based
append-only history. [Module 05](05-sharing-a-notebook.md).

### Coordinator (ExecutionCoordinator)
The part of the orchestrator that runs the plan step by step.
[Module 03](03-who-tells-them-what-to-do.md).

### Correlation ID
A unique identifier for each run. Propagates through every
event, envelope, and persisted record. Used for tracing and
replay.

### CPIC (Clinical Pharmacogenetics Implementation Consortium)
The clinical authority whose guidelines we pin. Every CPIC table
has a version in its filename (e.g. `v2022.1`). Not specific to
agentic AI, but central to our platform.

---

## D

### Deterministic
Code whose output depends only on its inputs — not on time,
randomness, external state, or LLM guesses. Same input → same
output, forever. The deterministic parts of our system are where
we put medical decision-making.

### Diversity selector (EvidenceSelector)
The merger that de-duplicates results from multiple retrievers
and prioritizes diverse sources. [Module 07](07-finding-information.md).

---

## E

### ECR (Evidence Coverage Ratio)
A signal used by the retrieval stopping controller. Measures how
much of the needed evidence has been retrieved so far.
[Module 07](07-finding-information.md).

### EvidenceGroundingEngine
Verification engine 2. Checks that every cited source ID resolves
in the MCP evidence cache. [Module 10](10-checking-the-work.md).

### EvidenceSufficiencyTrace
The frozen 7-dimension audit record produced by every sufficiency
evaluation. Replayable. [Module 11](11-knowing-when-to-say-no.md).

### EvidenceVerdict
A closed 5-value enum (SUPPORTED, REFUTED, INSUFFICIENT,
CONFLICTING, UNCERTAIN) produced by the 10 V-rules.
[Module 11](11-knowing-when-to-say-no.md).

### Event (RuntimeEvent)
A frozen record emitted by SwarmRuntime at stage boundaries. 12
closed event kinds. [Module 12](12-watching-the-agents.md).

### ExecutionTracer
Observability class that captures a unified 7-event-kind stream
for per-run tracing. [Module 12](12-watching-the-agents.md).

---

## F

### Fallback (LLM-with-fallback)
A pattern where an LLM call is attempted but a deterministic
alternative runs if the LLM fails or returns malformed output.
Used in our planner. [Module 03](03-who-tells-them-what-to-do.md).

### FacetCoverageState
A closed 3-value enum (COVERED, UNCERTAIN, MISSING) applied to
each of the 6 `ClaimEvidenceFacet` values.
[Module 11](11-knowing-when-to-say-no.md).

### ForbiddenAction
The 4-value closed enum enumerating what LLMs cannot do:
INFER_PHENOTYPE, OVERRIDE_RECOMMENDATION, BYPASS_VERIFICATION,
FABRICATE_CLAIM. [Module 04](04-the-safety-line.md).

### Frozen record
A Pydantic record that can't be mutated after construction.
Updates produce a new record. Used everywhere in our system for
replay-safety and audit invariance.

---

## G

### GenerativeBoundary
Our runtime safety mechanism for LLM outputs. Raises an exception
if an LLM tries to do any of the 4 forbidden actions. Cannot be
disabled at runtime. [Module 04](04-the-safety-line.md).

### GeminiOrchestrator
The facade class that wraps Planner + Router + Coordinator.
`orchestrator.run(query)` is the main entry point.
[Module 03](03-who-tells-them-what-to-do.md).

### Graph (KG, knowledge graph)
Our pharmacogenomic knowledge graph. 37 nodes, 34 edges, 10 node
kinds, 7 edge kinds. [Module 08](08-walking-a-map.md).

### Guardrail
General term for a rule enforced by the code around an LLM.
Our specific guardrail is the `GenerativeBoundary`.
[Module 04](04-the-safety-line.md).

---

## H

### Hop (multi-hop reasoning)
Following an arrow in the knowledge graph from one node to
another. A 4-hop path traverses 4 edges.
[Module 08](08-walking-a-map.md).

---

## I

### InMemoryBackend
MCP backend that stores everything in process memory. Used when
`MONGODB_URI` is unset. [Module 09](09-using-tools.md).

### IRCoT (iterative retrieval with chain-of-thought)
A research-pattern name for our multi-strategy + reasoning
pipeline. [Module 07](07-finding-information.md).

---

## L

### LLM (large language model)
A smart-brain AI that generates text. We use LLMs for narrative
synthesis and orchestration planning — both guarded.
[Module 04](04-the-safety-line.md).

---

## M

### MCP (Model Context Protocol)
The standardized tool-use protocol in our system. 6 services, 31
tools, uniform invocation via `client.invoke(...)`.
[Module 09](09-using-tools.md).

### MCPClient
The façade that routes tool calls through the registry and
records observability. [Module 09](09-using-tools.md).

### MCPExecutionMemory
One of the 6 MCP services. Stores per-run summaries.
[Module 06](06-remembering-things.md).

### MCPMemoryAdvisor
The advisor that summarizes prior runs into a digest for the
planner. Opt-in. [Module 06](06-remembering-things.md).

### MCPPersistenceHook
Auto-persists every `OrchestrationResult` across all 6 MCP
services at run end. [Module 09](09-using-tools.md).

### MCPRetrieval
Unified read-path for replay. `.replay(correlation_id)` returns a
`ReplayBundle` that can rehydrate the full execution context.
[Module 12](12-watching-the-agents.md).

### MCPToolResult
The uniform result shape for every MCP tool call.
`.ok`, `.data`, `.duration_ms`, `.error`.
[Module 09](09-using-tools.md).

### Multi-agent system (MAS)
A system composed of multiple specialist agents rather than one
monolithic AI. [Module 01](01-why-many-agents.md).

### MultiHopReasoner
The bounded-BFS walker over the knowledge graph.
[Module 08](08-walking-a-map.md).

---

## N

### Narrative synthesis
The final stage of the runtime — an LLM writes a human-readable
paragraph over the deterministic structured output. Guarded by
the `GenerativeBoundary`.

### NodeKind
The 10-value closed enum for knowledge-graph node types.
[Module 08](08-walking-a-map.md).

---

## O

### Observability
The ability to watch what an agent system is doing. In our
system, this means event streams, traces, graphs, and replay.
[Module 12](12-watching-the-agents.md).

### Off-by-default
The pattern where new capabilities integrate via a constructor
argument defaulting to `None`, not a runtime feature flag. Making
rollouts explicit and reviewable.

### Orchestrator
The boss agent — plans, routes, and coordinates. In our system,
the `GeminiOrchestrator` + its three sub-components
(`WorkflowPlanner`, `AgentRouter`, `ExecutionCoordinator`).
[Module 03](03-who-tells-them-what-to-do.md).

---

## P

### Planner (WorkflowPlanner)
The part of the orchestrator that decides what to do. Uses an
LLM with a deterministic fallback.
[Module 03](03-who-tells-them-what-to-do.md).

### PopulationEvidenceBiasDetector
The detector that flags 3 named bias patterns.
[Module 11](11-knowing-when-to-say-no.md).

### Priority-ordered rules
The pattern where rules are tested in order, first match wins.
Used for all our R / V / U rule tables.
[Module 11](11-knowing-when-to-say-no.md).

### PriorRunDigest
The summary the memory advisor gives the planner as a hint.
[Module 06](06-remembering-things.md).

### Provenance / ProvenanceStamp
The attribution chain that traces every claim back to a source.
Propagated as a tuple of stamps on every envelope.
[Module 02](02-how-agents-talk.md), [Module 09](09-using-tools.md).

### ProvenanceValidator
Verification engine 4. Checks the provenance chain for
completeness. [Module 10](10-checking-the-work.md).

---

## R

### ReAct
A research pattern — reasoning + acting loops — that our
retrieval pipeline is inspired by. [Module 07](07-finding-information.md).

### Refusal (honest refusal, named refusal)
An explicit, structured "we can't answer this" with a specific
rule ID. Our system's alternative to making up plausible-sounding
but unsupported answers. [Module 11](11-knowing-when-to-say-no.md).

### Registry (AgentRegistry, MCPToolRegistry)
A catalog of available agents (or tools). Ensures routing only
hits registered names. [Module 03](03-who-tells-them-what-to-do.md).

### Replay
Reconstructing a past run from its persisted records. Not
re-running — replaying. [Module 12](12-watching-the-agents.md).

### Retriever (BiomedicalRetriever)
The abstract base class for our retrieval strategies. Four
concrete retrievers implement it: dense, population-aware,
graph, diversity selector. [Module 07](07-finding-information.md).

### Router (AgentRouter)
Resolves plan steps to specific registered agents. Refuses
unregistered names. [Module 03](03-who-tells-them-what-to-do.md).

### R-rule
One of the 12 decision rules in the `SufficiencyDecisionEngine`.
Priority-ordered. Each produces one of 7
`SufficiencyDecision` outcomes.
[Module 11](11-knowing-when-to-say-no.md).

### RuntimeEventKind
The 12-value closed enum for events emitted during a run.
[Module 12](12-watching-the-agents.md).

---

## S

### Safety boundary
See `GenerativeBoundary`. [Module 04](04-the-safety-line.md).

### SafetyConstraintEngine
Verification engine 3. Re-derives phenotype independently and
compares against the claim. Catches drift.
[Module 10](10-checking-the-work.md).

### Scope firewall
The closed-enum-at-every-boundary pattern that makes scope drift
a compile-time / review-time event.
[Module 02](02-how-agents-talk.md), [Module 04](04-the-safety-line.md).

### SharedBiomedicalContext
The cross-agent shared state for biomedical facts (evidence
graph, verification state). 8 brief-named fields.
[Module 05](05-sharing-a-notebook.md).

### StopSignal
A closed 3-value enum emitted by the retrieval stopping
controller. SUFFICIENT, STAGNATING, BUDGET_EXHAUSTED.
[Module 07](07-finding-information.md).

### SufficiencyCheckpoint
The façade that runs all 4 sufficiency sub-layers. Integrates
into `ExecutionCoordinator` as Step 3.5, opt-in.
[Module 11](11-knowing-when-to-say-no.md).

### SufficiencyDecision
A closed 7-value enum (SUFFICIENT, PASS_WITH_CAVEAT, DOWNGRADE,
REQUEST_MORE, ESCALATE, ABSTAIN, BLOCK) produced by the 12
R-rules. [Module 11](11-knowing-when-to-say-no.md).

### SuperPopulation
A closed 5-value enum for population codes: EUR, EAS, SAS, AFR,
AMR. Derived from 1000 Genomes / gnomAD.

### SwarmExecutionContext
The per-run shared notebook. [Module 05](05-sharing-a-notebook.md).

### SwarmRuntime
The 5-stage lifecycle class. `SwarmRuntime.run(query)` is the
canonical execution entry point.
[Module 04](04-the-safety-line.md), [Module 13](13-what-weve-built.md).

---

## T

### Tool call
A standardized invocation of an MCP tool via `client.invoke(...)`.
Returns a `MCPToolResult`. [Module 09](09-using-tools.md).

### Trace (OrchestrationTrace)
The per-run record of every step that executed, with timing
information. [Module 12](12-watching-the-agents.md).

### TraceReplayer
Replays a persisted trace for debugging or demoing.
[Module 12](12-watching-the-agents.md).

---

## U

### UncertaintyScore
A closed 4-value enum (UNSAFE, HIGH, MODERATE, LOW) produced by
the 9 U-rules. [Module 11](11-knowing-when-to-say-no.md).

### UnifiedExecutionReport
The frozen 18-field record produced at the end of every run.
JSON-serializable. Persisted.

### U-rule
One of the 9 uncertainty rules in the `UncertaintyScoringEngine`.
[Module 11](11-knowing-when-to-say-no.md).

---

## V

### Verification
Post-synthesis check that an answer is safe to release. Four
engines: shape, existence, truth, chain.
[Module 10](10-checking-the-work.md).

### VerificationOutcome
The combined output of the 4 verification engines. Has a score,
a decision, and a trace. [Module 10](10-checking-the-work.md).

### VerificationScore
A closed 5-tier enum: grounded, partially_grounded, unverified,
conflicting, unsafe. [Module 10](10-checking-the-work.md).

### V-rule
One of the 10 verifier rules in the `SetLevelEvidenceVerifier`.
[Module 11](11-knowing-when-to-say-no.md).

---

## W

### WebSocket
The browser-server protocol we use for live event streaming.
`ws://host/ws/run` — the frontend subscribes and receives events
as they're emitted. [Module 12](12-watching-the-agents.md).

### WorkflowPlanner
The planner component of the orchestrator. Uses an LLM with a
deterministic fallback. [Module 03](03-who-tells-them-what-to-do.md).

---

## Back to

- [Course landing](README.md)
- [Module 00 — What's an Agent?](00-whats-an-agent.md)
- [Module 14 — Where to Go Next](14-where-to-go-next.md)
