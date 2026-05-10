# Module 07 — Tech Stack

> Prerequisites: [02 The Three Repos](02-the-three-repos.md), [04 Architecture](04-architecture.md)

---

## The question we're answering

Every technology choice in the platform was a decision between
alternatives. Which did we pick, and why? What's actually in use vs.
declared-but-unused? Where are we deliberately boring, and where did
we pay a cost for a specific capability?

---

## The honest inventory

Let's walk the actual dependency manifests. These are real files on
`main` today.

### `anukriti-pgx-core` — zero runtime dependencies

`pyproject.toml`:

```toml
[project]
dependencies = []

[project.optional-dependencies]
service = ["fastapi", "uvicorn"]  # future HTTP surface
dev = ["pytest", "ruff", "mypy", ...]
```

**That's it.** The biomedical truth layer uses only the Python
standard library. When you `pip install anukriti-pgx-core`, you get
one package, no transitive deps.

Why: see [Module 06](06-why-deterministic.md). Zero-dep is a safety
property — no third party can smuggle in randomness, network I/O, or
LLM calls via a transitive upgrade.

### `anukriti-swarm` — the research platform

`requirements.txt`:

```python
# Core
pydantic==2.7.1
fastapi==0.111.0
uvicorn==0.29.0
websockets==15.0.1

# AI/ML
langchain==0.2.1            # ← DECLARED BUT UNUSED
openai==1.30.1
anthropic==0.25.8

# Data
pandas==2.2.2
numpy==1.26.4

# Vector Store
qdrant-client==1.9.1        # ← DECLARED BUT UNUSED

# MCP persistence
pymongo==4.17.0

# Dev
pytest==8.2.0
ruff==0.4.4
mypy==1.10.0

# pgx-core, pinned exactly
anukriti-pgx-core==0.2.1
```

Two of these are **orphans** — `langchain` and `qdrant-client`.
Zero Python files import them. They're historical declarations from
an earlier design phase that didn't ship. A follow-up cleanup PR
will remove them.

The actual in-use stack is what we walk next.

---

## Why each choice — in plain language

### Python 3.11+

**Chosen for:** frozen dataclasses, `typing.Self`, better generics,
3.11's speedup over 3.10.

**Considered:** TypeScript / Rust for the deterministic core.

**Rejected because:** Python is the lingua franca of bioinformatics
and clinical ML. Every pharmacogenomics engineer we'd want to hire
already knows it. Rust would be safer still, but the hiring pool is
narrower and the ecosystem (CPIC tools, variant-call parsing) is
Python-dominant.

### Pydantic (v2)

**Used for:** every cross-module data contract in swarm. Frozen
records for `SwarmExecutionContext`, `UnifiedExecutionReport`,
`AgentContextEnvelope`, every verification trace.

**Why v2 specifically:** 10× faster than v1 for large validation
workloads, better handling of `Literal` types (we use these for
closed enums), and `@computed_field` for derived properties.

**Why not dataclasses directly:** Pydantic gives us runtime
validation with essentially no performance cost in v2. For a
platform that wants closed enums and frozen records to be a
first-class concept, Pydantic's built-in validation is the right
layer — we don't re-invent type-safe constructors.

**Why not attrs:** attrs is fine but doesn't give us JSON
serialization, schema generation, or closed-enum `Literal`
validation out of the box. Pydantic is a better fit for a data-
exchange-heavy codebase.

### FastAPI

**Used for:** the swarm backend (`backend/app.py`), which serves
`/api/run`, `/api/scenarios`, `/api/snapshot/*`, `/api/replay/*`,
and `/ws/run` for live WebSocket event streaming.

**Why:** FastAPI + Pydantic is the obvious stack for a
Pydantic-heavy application. ASGI support means WebSockets work
natively. The auto-generated OpenAPI spec is free.

**Considered:** Flask + flask-pydantic, Django Rest Framework,
Starlette directly, aiohttp.

**Rejected because:**
- Flask is synchronous by default; our WebSocket stream benefits
  from async.
- DRF has a lot of ceremony for a research-grade API.
- Starlette directly would force us to rebuild half of FastAPI.
- aiohttp is good but not Pydantic-native; we'd manually wire
  validation everywhere.

### Uvicorn

**Used for:** ASGI server for the FastAPI app. Production-grade in
its own right; pairs with FastAPI without adaptation.

**Why not gunicorn:** gunicorn can run Uvicorn workers, and we'd
add it for production deployment. For research-platform single-
process demos, pure uvicorn is simpler.

### WebSockets (via `websockets` + FastAPI)

**Used for:** `/ws/run` endpoint in `backend/ws/run.py`. Streams
`RuntimeEvent` records from the in-progress `SwarmRuntime` run to
the frontend live, per-event.

**Why this matters:** the frontend (D3 mission-control UI) can
update per-stage — "orchestrator activated," "retrieval completed,"
"sufficiency checkpoint passed" — as the backend emits events. Not
a batched final report.

**Considered:** Server-Sent Events (SSE), long-polling.

**Rejected because:**
- SSE is one-way (server→client); WebSockets let the client cancel
  or interact if we need to. Also SSE doesn't handle proxy
  buffering as well.
- Long-polling is a worse SSE.

### LLM providers — google-genai (primary), openai (fallback), anthropic

**Used for:** narrative synthesis (Module 06) and orchestration
planning (Module 04).

**Why multiple:** provider fallback. The primary is Gemini (via
`google-genai`) because of its long context window and cost profile
at the scale we run. OpenAI is the fallback when Gemini is
rate-limited or unavailable. Anthropic is declared but mostly
unused today — future option.

**Multi-provider wrapper:** `ai/gemini/client.py` implements a small
adapter layer. All three providers return the same
`CompletionResult` shape. Calling code doesn't know or care which
provider actually ran.

### pymongo

**Used for:** the MCP (Model Context Protocol) persistence layer.
Six services write run summaries, traces, contexts, provenance
chains, evidence cache, and verification logs to MongoDB.

**Why MongoDB:** the MCP model is document-oriented. Each run is
a single logical document with nested subrecords (evidence,
provenance, traces). A document store is the natural fit. An SQL
database would require JOINs across 6 tables per query; Mongo does
it in one document read.

**Why not DuckDB / SQLite for local:** we have both. The MCP layer
has an in-memory `InMemoryBackend` that gets used when
`MONGODB_URI` is unset. DuckDB would be a third backend and we've
not needed it.

**Why not Postgres with JSON columns:** Postgres-with-JSON-columns
is MongoDB with extra steps. For document-shaped data, just use
a document store.

### D3.js (vendored v7.9.0)

**Used for:** the live mission-control UI's force-directed
knowledge-graph visualization. When a user hits "run scenario," the
frontend shows the 10 closed `NodeKind`s as colored nodes and the
7 `EdgeKind`s as directed arrows, updating live as the runtime
traverses paths.

**Why D3 and not React:** we don't have a React codebase. The
frontend is vanilla JS + HTML + CSS. D3 is vendored as a single 280
KB file — no npm, no build step, no webpack config. Other panels
(evidence sufficiency, trace log, provenance chain) are built with
plain DOM manipulation.

**Why vanilla JS:** two reasons.
1. The frontend is an instrumentation surface for the runtime, not
   a product UX. Vanilla JS keeps the dependency graph of the
   research platform minimal — no second language to install, no
   bundler step.
2. A research-grade UI benefits from being hackable — anyone
   reading the HTML/JS can tweak it without running `npm install`.

**Considered:** React, Vue, Svelte, Observable (which is D3-based).

**Rejected because:** every framework choice adds ~100 MB of
transitive dependencies and a build step. D3-only gives us the
force simulation, drag interactions, and color scales that justify
a frontend library; we don't need anything else.

### Docker (multi-stage)

**Used for:** one-command demo startup in `anukriti-swarm`.
`docker compose up --build` starts:
- `swarm-backend` (FastAPI + uvicorn on :8000)
- `swarm-frontend` (Python http.server serving the static UI on :3000)
- `swarm-mongo` (optional via `--profile mongo` — MongoDB 7.0)

**Why multi-stage:** the builder stage compiles deps into
`/opt/venv`; the runtime stage copies only the venv, keeping the
image under 500 MB. Non-root UID 10001 for runtime safety.

**Why Python http.server for the frontend:** no build step. The
static files are served directly. For production, you'd swap in
nginx — but for a research demo, stdlib's http.server is honest.

### ruff

**Used for:** linting + formatting. Replaces `black`, `isort`,
`flake8`, partially replaces `pylint`.

**Why:** ruff is 100-1000× faster than the old Python linting
stack. For a pre-commit workflow and CI, that speed is actually
usable (sub-second on the full codebase). The strangler-fig
adoption model (hard-gate on some dirs, informational on the rest)
lets us adopt without a huge upfront debt paydown.

### mypy

**Declared in `requirements.txt`, not yet in CI.** See
`anukriti-pgx-core/docs/adr/0001-founding-engineer-scope-and-deferrals.md`
— mypy-as-gate is deferred until ruff hard-gate reaches ≥60% of
the codebase. Running two cleanup campaigns in parallel splits
attention.

### pytest

**Used for:** 234 tests in swarm, 51 in pgx-core, ~353 in anukriti.
Standard Python test runner. Nothing unusual.

**Why not unittest:** pytest's fixtures + parameterize idioms are
cleaner for the table-driven test style we use heavily (every R-rule,
V-rule, U-rule test is parameterized).

---

## The pieces we DON'T use, and why

### No LangChain / LangGraph

Declared in `requirements.txt` but **zero imports**. A followup PR
will remove.

Why no LangChain: our agent framework is hand-rolled in
`agents/orchestrator/` and `core/orchestrator/`. The `ExecutionCoordinator`
is a small state machine over Pydantic records. LangChain's
abstractions (LLMChain, AgentExecutor, ReAct) add layers without
solving problems we have — we already know what stages run; we
already have structured inputs; we already have closed-enum
contracts. Bringing LangChain in would hide the clarity behind a
framework.

### No Qdrant / Chroma / Pinecone (vector DB)

Declared `qdrant-client` but unused. Our retrieval layer uses
TF-IDF against in-tree mock documents (`retrieval/indexing/
embeddings.py`). For a research platform demonstrating the
architecture, TF-IDF is sufficient; for scale, we'd swap in a real
vector store via the `BiomedicalRetriever` ABC — a one-file swap,
not an architectural change.

The orphan `qdrant-client` declaration is from when we started
integrating Qdrant; it stalled; we kept the dep line. Removal is a
cleanup PR.

### No GraphQL

Reviewed once. Rejected because FastAPI's auto-generated REST
spec + Pydantic schemas give us the typed API contract we'd want
from GraphQL, without the N+1 query issues or the client-side
complexity. If future consumers want GraphQL, we'd add it as a
parallel surface, not replace REST.

### No Celery / Redis Queue

Runs are synchronous and sub-second (deterministic path is <2ms,
LLM narrative is ~400ms). A job queue would be overkill. If we
add long-running async jobs in the future (e.g. full cohort
analysis), then yes.

### No Kubernetes-native framework

Today's platform runs in Docker Compose on a single host. When we
scale to multi-tenant or multi-region, we'll containerize into
Kubernetes with Helm charts. We're not there yet; adopting K8s
pre-emptively would be premature.

---

## What's deliberately "boring"

A platform with a medical-safety mandate benefits from boring,
widely-understood technology at the boundary layers. Where we chose
boring:

- **Python for the library.** Not a hot new language.
- **Pydantic for data contracts.** The obvious Python choice.
- **FastAPI for HTTP.** The obvious Python web framework today.
- **Conventional Commits for git.** Standard, tooling exists.
- **MongoDB for documents.** Standard document DB.
- **Docker for packaging.** Standard containerization.
- **Apache 2.0 license.** Standard permissive license.

"Boring" at the edges lets us spend weirdness budget on the
interesting parts: the `GenerativeBoundary`, the closed-enum scope
firewall, the 14 closed enums in the sufficiency layer, the
byte-identical regression contract.

---

## What's deliberately unusual

- **Zero runtime deps in the library.** Unusual. Justified by the
  safety invariants (Module 06).
- **Closed enums for every cross-module contract.** Unusual. Most
  Python codebases use strings. Closed enums are what make scope
  firewalls work at review time.
- **14 closed enums in one layer.** Unusual. The evidence sufficiency
  layer alone has 14 enums covering facets, states, decisions,
  verdicts, bias kinds, node/edge kinds. This is the cost of
  keeping a "not a generic RAG framework" scope guarantee.
- **Byte-identical regression testing across three repos.** Unusual.
  Most projects accept some output drift as long as semantic tests
  pass. We chose byte-identity because for a biomedical truth layer,
  any drift that isn't documented is suspicious.
- **Off-by-default via constructor args, not feature flags.** Unusual.
  Most production Python uses env-var flags. We chose constructor
  args because they're visible in code review and can't be toggled
  post-deploy.

Each "unusual" choice has a specific reason that ties back to the
core invariant from Module 04: **no medical claim leaves the system
unless it came from deterministic rules.**

---

## Summary

You now know:

- **pgx-core has zero runtime deps.** Safety property.
- **Swarm's real stack:** Python 3.11, Pydantic v2, FastAPI,
  WebSockets, pymongo, Gemini/OpenAI/Anthropic, vanilla JS + D3.
- **Two orphan deps** (`langchain`, `qdrant-client`) are declared
  but unused; scheduled for cleanup.
- **We chose boring at the edges** (Python, FastAPI, Mongo, Docker)
  to spend weirdness budget on the safety-critical middle (closed
  enums, regression contracts, `GenerativeBoundary`).
- **What we don't use is as informative as what we do.** No
  LangChain — we have our own orchestrator. No vector DB — TF-IDF
  suffices for research scale. No K8s — Docker Compose suffices
  until multi-tenant.

Next: [Module 08 — Population Awareness](08-population-awareness.md).
Why is ancestry a first-class reasoning dimension?
