# 09 — Using Tools

> When a helper needs something bigger than their own hands — a
> hammer, a scale, a phone — they follow a standard way to use it.

---

## The Story

One day, Anu gets a giant 40-pound bag of flour. She can't lift it
alone. But the bakery has a **rolling cart**.

To use the cart, anyone in the bakery follows the same steps:

1. **Take the cart** from its parking spot
2. **Use it** for the task (wheel the flour from the loading dock)
3. **Clean it** if it got dirty
4. **Put it back** in the parking spot

Every helper — Anu, Priya, Ravi — uses the cart the same way. If
a new helper joins the bakery, they learn the cart protocol once
and it works forever.

Nobody invents their own cart-using method. Nobody carries the
cart away to their own corner. The **protocol is shared**.

That's how tool use works for AI agents too. A standard,
predictable way to call a tool, get a result back, and log what
happened.

---

## What this means for computers

Agents in our system sometimes need to do things that aren't
Python-in-their-own-file:

- Save a record to a database
- Look up a paper's full text
- Load an old run's state for replay
- Check whether a specific PMID is in our evidence cache
- Record which verification checks passed

We could give each agent its own way of doing these things. Agent
A has its own database code. Agent B has its own. They all
slightly differ.

The better way: define **tools** that anyone can call. One
database-writer tool. One evidence-lookup tool. One trace-writer
tool. Every agent uses the same tools the same way.

We want:

1. **One agreed-on protocol** for describing tools ("here's what
   I take as input, here's what I return")
2. **One registry** where all tools live
3. **One way to call a tool** that all agents follow
4. **Observability for free** — every tool call is logged with
   timing, success/failure, arguments

We call this the **Model Context Protocol**, or **MCP**.

---

## What we built

Our MCP layer lives here:

```
anukriti-swarm/integrations/mcp/
  client.py            the client that calls tools
  registry.py          where all tools are registered
  models.py            the tool-call and tool-result record types
  backends/            where the persisted data goes (Mongo or in-memory)
  memory.py            \
  trace_store.py        \   6 services
  context_manager.py     ├── 31 tools
  provenance.py         /
  evidence.py          /
  verification_log.py /
```

### The six services

Each service is a group of related tools:

| Service | What it does | Tools |
|---------|--------------|-------|
| `MCPExecutionMemory` | Summaries of past runs | 5 |
| `MCPTraceStore` | Full orchestration traces | 4 |
| `MCPContextManager` | Snapshot/restore execution context | 5 |
| `MCPProvenanceStore` | PROV-DM structured claim chains | 6 |
| `MCPEvidenceCache` | Biomedical evidence papers | 6 |
| `MCPVerificationLog` | Per-check audit records | 5 |

Total: **31 tools** across **6 services**.

### A tool call has one shape

Every tool call uses this shape:

```python
result = client.invoke(
    tool_name="memory.store",
    arguments={"correlation_id": "abc123", "summary": {...}},
    correlation_id="abc123",
    called_by="pharmacogene_agent",
    origin=MCPOrigin.AGENT,
)

# result is always:
result.ok          # bool
result.data        # the return value
result.duration_ms # how long it took
result.error       # if not ok, what went wrong
```

Every call. Same shape. The calling agent doesn't care which
service the tool lives in or what backend (Mongo or memory) is
behind it. It just calls `client.invoke(...)` and gets a
`MCPToolResult` back.

### Observability for free

Because every call goes through the same `client.invoke(...)`
path, the client can record:

- Which tool was called
- By whom
- When
- How long it took
- Whether it succeeded

At any time, you can ask: *"what have tools been doing?"*

```python
snapshot = client.snapshot()
# Returns per-tool call volume, avg latency, success rate
```

This is free instrumentation. The agents don't have to add
logging. The tools don't have to add logging. The client does it
once, for everyone.

### Swappable backends

The `InMemoryBackend` and `MongoBackend` both implement the same
`StorageBackend` protocol. Switching between them is a matter of
unsetting an environment variable — the code doesn't change.

For demos and dev: in-memory. For production: MongoDB Atlas. The
agents don't know which one they're talking to.

### A concrete tool

Example: the `memory.store` tool. Its job is to save a run
summary.

The tool is registered once in `memory.py`:

```python
registry.register(
    name="memory.store",
    handler=self._tool_store,
    schema={
        "correlation_id": str,
        "summary": dict,
    },
)
```

An agent calls it:

```python
client.invoke("memory.store", {"correlation_id": cid, "summary": {...}})
```

The registry looks up the handler, validates the arguments
against the schema, runs the handler, wraps the result in a
`MCPToolResult`, and records the observability data.

Agents don't know this is happening. They just call
`client.invoke(...)` and get back a result.

---

## Try it yourself

Look at one service:

```
anukriti-swarm/integrations/mcp/memory.py
```

Find `__post_init__`. That's where the service registers all its
tools with the registry. Count how many `registry.register(...)`
calls there are — that's how many tools this service offers.
For memory, it's 5.

Now look at the client:

```
anukriti-swarm/integrations/mcp/client.py
```

Find `invoke`. Notice how it doesn't know anything about the
specific tool. It looks up the handler, records the call, runs
it, wraps the result. Generic. Same for every tool.

This is what "standardized protocol" means — one invocation path,
31 tools, 6 services, same shape everywhere.

---

## The grown-up version

> Our MCP (Model Context Protocol) layer is a production-shaped
> tool-use and persistence surface for the swarm agents. Six
> services are attached to a shared `MCPClient` and
> `MCPToolRegistry`:
>
> | Service | Collection | Tools |
> |---------|------------|-------|
> | `MCPExecutionMemory` | `memory` | 5 |
> | `MCPTraceStore` | `traces` | 4 |
> | `MCPContextManager` | `contexts` | 5 |
> | `MCPProvenanceStore` | `provenance` | 6 (PROV-DM shape) |
> | `MCPEvidenceCache` | `evidence` | 6 |
> | `MCPVerificationLog` | `verification_logs` | 5 |
>
> Every tool call goes through `client.invoke(tool_name, args, ...)`,
> returning an `MCPToolResult` with `.ok`, `.data`, `.duration_ms`,
> `.error`, and full observability (per-tool call volume, avg
> latency, success rate) via `client.snapshot()`.
>
> The backend is swappable — `InMemoryBackend` for dev/demo,
> `MongoBackend` for production (with live MongoDB Atlas
> verified). Backend selection is automatic based on the
> `MONGODB_URI` environment variable.
>
> The layer also ships two composable utilities:
>
> - **`MCPPersistenceHook`** — auto-persists every
>   `OrchestrationResult` across all 6 services at run end
> - **`MCPRetrieval`** — unified read-path for replay;
>   `MCPRetrieval.replay(correlation_id)` returns a
>   `ReplayBundle` that can rehydrate the full
>   `SwarmExecutionContext`
>
> This is the tool-use backbone for every agent in the system,
> and the persistence substrate for memory (Module 06) and
> observability (Module 12).
>
> Full architecture in `architecture/mcp-infrastructure.md`.

---

## What you learned

Before this module: tool use sounded like "agents call APIs
somehow."

Now: tool use in our system is **31 concrete tools across 6
services, all called through one standardized invocation path
with observability baked in**. Agents don't invent tool calls
— they use the registered tools. Results come back in a uniform
shape. Swapping backends is a config change, not a code change.

Everybody's rolling cart protocol. Once, learned once, used
everywhere.

---

Next up: **[10 — Checking the Work](10-checking-the-work.md)**

All nine agents have contributed. The notebook is full. Before
we hand anything to a human, who double-checks?
