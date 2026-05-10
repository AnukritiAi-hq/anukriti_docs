# 12 — Watching the Agents

> A little movie of what just happened, so you can see every step
> — and replay it later.

---

## The Story

At the end of a busy day, Anu sits down with her notebook and
does something important: she **reads back what happened**.

- 9:00am: dough-mixer started cupcake batter
- 9:15am: oven-watcher preheated the oven
- 10:30am: cupcakes came out, looked perfect
- 11:45am: Priya started frosting
- 12:10pm: the sprinkler noticed the frosting was too soft
- 12:15pm: froster switched to a stiffer recipe
- 1:00pm: customer picked up their order

Anu sees *exactly* what happened, in order, with timestamps. If a
customer complains tomorrow — "my cupcakes had too much frosting"
— she can go back to 11:45am and see exactly what the froster did.

If she wants to run a *replay* — "redo today's cupcakes again to
practice" — she has all the steps written down.

This is what we do with our AI runs. Every run emits a little
movie.

---

## What this means for computers

When an agent does something, we **record** it. Not just the final
answer. Every step:

- Agent activated
- Retrieval started
- Knowledge graph traversal completed
- Sufficiency checkpoint fired
- Verification check passed
- Narrative started
- Run completed

Each of these is an **event**. Events are **frozen** records with
timestamps. They form a stream. A client can **subscribe** to the
stream and watch the run happen in real time.

Later, the full event stream can be **replayed**. Not re-run —
replayed. The frames were captured; we play them back.

This kind of watching-and-replaying is called **observability**,
and it's one of the things that makes agent systems operable
instead of magical.

---

## What we built

Our observability layer has several pieces:

### Events — the building block

Events are frozen records:

```python
@dataclass(frozen=True)
class RuntimeEvent:
    kind: RuntimeEventKind
    correlation_id: str
    timestamp: datetime
    payload: Mapping[str, Any]
```

There are **12 kinds** (a closed enum, like everything else):

```
RUN_STARTED
ORCHESTRATOR_ACTIVATED
AGENT_ACTIVATED
RETRIEVAL_STARTED
RETRIEVAL_COMPLETED
KG_TRAVERSAL_STARTED
KG_TRAVERSAL_COMPLETED
SUFFICIENCY_CHECKED
VERIFICATION_CHECKED
SYNTHESIS_STARTED
SYNTHESIS_COMPLETED
RUN_COMPLETED
```

The code lives at:

```
anukriti-swarm/core/runtime/events.py
```

### Event streams — where events flow

There's an abstract `EventStream` protocol:

```python
class EventStream(Protocol):
    def emit(self, event: RuntimeEvent) -> None: ...
    def close(self) -> None: ...
```

Two implementations:

- **`InMemoryEventStream`** — for demos and tests. Events are
  collected in a list.
- **`AsyncQueueEventStream`** — for the live FastAPI WebSocket.
  Events flow through an asyncio queue to the browser.

The **`SwarmRuntime`** doesn't know which stream it's talking to.
It just calls `stream.emit(event)` and continues.

### The execution tracer

Beyond events, there's a richer per-run trace:

```
anukriti-swarm/observability/tracing/
  execution_tracer.py       records every step with latency
  timing_profiler.py        measures stage-by-stage timing
  agent_activity_monitor.py tracks utilization and failure rate
```

At the end of a run, you can ask:

- How long did retrieval take?
- Which agents were active?
- Which agents collaborated?
- What was the failure rate?
- How many tokens were used?

This is analytics for your agents.

### The execution graph

You can turn a trace into a visual graph:

```
anukriti-swarm/observability/visualization/
  workflow_graph_builder.py   builds the graph
  swarm_execution_graph.py    the graph data structure
  trace_visualizer.py         renders graphs to CLI / JSON
```

For the live UI, the graph gets rendered with D3 (a JavaScript
library) as a **force-directed knowledge-graph animation** —
you can literally watch the agent network activate.

### Replay — re-reading the movie

Because every run's full event stream plus full
`SwarmExecutionContext` is persisted to MCP (Module 09), you can
replay any past run:

```python
bundle = MCPRetrieval(client).replay(correlation_id="abc123")
context = bundle.restore_context()
# `context` is a fully rehydrated SwarmExecutionContext
```

This is not a re-run. It's a replay. The original events are
shown again in order. The original state is reconstructed.

For debugging, auditing, and demoing past runs, this is
essential. An auditor six months later can ask "why did this run
downgrade?" and get a byte-for-byte answer.

### The failure analyzer

Finally, when something goes wrong:

```
anukriti-swarm/observability/failure_analyzer.py
```

Given a failed run, it identifies:

- Where in the pipeline the failure occurred
- What preceded the failure
- Which agent was responsible
- What state was present at the time

Compare this to "the AI gave a weird answer." With failure
analysis, you know *exactly* where it went wrong.

---

## Try it yourself

Run the orchestration visualization demo:

```bash
python -m demos.orchestration_visualization_demo
```

Output summary:

```
30 events · 22 nodes · 18 edges · 2950 tokens
Execution traced. Graph built. Visuals rendered.
```

You'll see:

- The event log with timestamps
- A text-rendered graph
- Per-agent activity metrics
- JSON export of the full trace

You can diff two such runs to see what changed. You can export the
JSON and reload it later. The run is fully inspectable.

For a fancier live view, bring up the backend + frontend
(`docker compose up`), open the mission-control UI at
`http://localhost:3000/pages/index.html`, and click "Activate
Swarm." Events stream in live over WebSocket and render into
panels.

---

## The grown-up version

> Our observability layer consists of:
>
> - **12 closed `RuntimeEventKind` values** emitted by
>   `SwarmRuntime` at stage boundaries
> - **`EventStream` protocol** with `InMemoryEventStream` (for
>   tests/demos) and `AsyncQueueEventStream` (for WebSocket
>   streaming)
> - **`ExecutionTracer`** — unified 7-event-kind stream for
>   per-run tracing
> - **`TimingProfiler`** — per-stage latency + token usage
> - **`AgentActivityMonitor`** — agent utilization, failure rate,
>   collaboration graph
> - **`WorkflowGraphBuilder`** + **`SwarmExecutionGraph`** —
>   structured graph data for visualization
> - **`TraceVisualizer`** — renders graphs to CLI, JSON, or D3
>   force-directed viz
> - **`TraceReplayer`** + **`FailureAnalyzer`** — replay and
>   post-mortem analysis
> - **`CinematicPlayer`** — presentation-mode playback for demos
>
> Every flagship run emits an exact number of events (pinned in
> tests):
> - `showcase` demo: 7 events
> - `unified_demo`: 14+14+13 = 41 total events across 3 scenarios
> - `safety_demo`: 5 events (5 scenarios × multiple stages)
>
> Byte-identical output on re-run (except non-deterministic
> narrative text, which is still bounded by
> `GenerativeBoundary`).
>
> For the live UI, `AsyncQueueEventStream` bridges the
> synchronous runtime thread to the async WebSocket; events flow
> via `loop.call_soon_threadsafe`, preserving low-latency
> delivery (~1ms per event).
>
> Full architecture in
> `architecture/observability-visualization.md`.

---

## What you learned

Before this module: agent behaviour felt like a black box.

Now: every run emits a structured, frozen, replayable event
stream. 12 event kinds. Two stream implementations. Full trace,
graph, replay, failure analysis. A run is not magic — it's
**a sequence of 14 events** (or however many) that you can read
in order, diff against another run, replay later, or watch live.

Anu's day-end notebook, but for AI.

---

Next up: **[13 — What We've Built](13-what-weve-built.md)**

We've covered every major piece. Time to put them together and
watch one full request flow from start to finish.
