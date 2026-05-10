# Module 11 — Hands-On

> Prerequisites: [02 The Three Repos](02-the-three-repos.md), [04 Architecture](04-architecture.md). Docker installed.

---

## The question we're answering

You've read about the platform. Now let's run it. In this module
you'll bring up the swarm demo, inspect a live run, and identify
where to poke first.

---

## Prereqs

- **Docker.** `docker --version` should work. Any recent version is
  fine; the Dockerfile targets 20+.
- **docker compose.** `docker compose version` should work (note:
  `docker compose`, space, not `docker-compose`).
- **Git and ~1 GB of disk.** The Docker image is ~500 MB.
- **(Optional) Python 3.11+** if you want to run demos without
  Docker.

---

## Path A: Docker (recommended first run)

```bash
# Clone the research platform
git clone https://github.com/AnukritiAi-hq/anukriti-swarm.git
cd anukriti-swarm

# Build and bring up the stack
docker compose up --build
```

This starts two containers:

- **`anukriti-swarm-backend`** on `http://localhost:8000` —
  FastAPI + WebSocket
- **`anukriti-swarm-frontend`** on `http://localhost:3000` —
  static UI (vanilla JS + D3)

First build is ~2 minutes (pip install for all deps). Subsequent
builds are fast (Docker caches the venv layer).

### Check it's running

```bash
curl http://localhost:8000/api/health
```

Expected:

```json
{"status":"ok","service":"anukriti-swarm","version":"0.1.0","cache_size":0}
```

### Open the frontend

Browse to `http://localhost:3000/pages/index.html`. You'll see:

- **Header:** "Anukriti Swarm — AI mission control for genomic
  intelligence." Green `● live` badge if backend is reachable;
  yellow `● offline` with a static mock otherwise.
- **Scenario picker:** dropdown with the three canonical scenarios:
  - Clopidogrel + CYP2C19 + South Asian (Priya)
  - Carbamazepine + HLA-B*15:02 + East Asian
  - Codeine + CYP2D6 + African ancestry
- **Activate Swarm** button — click to run the selected scenario.
- **Run Flagship Trio** — runs all three side-by-side.

### Click "Activate Swarm" with Priya's scenario

Watch the UI panels update in real time as events arrive over the
WebSocket:

1. **Live Execution Timeline** — each stage appears as a line; stages
   highlight as they fire.
2. **Knowledge Graph Explorer** — D3 force-directed graph renders
   as the MultiHopReasoner traverses paths.
3. **Evidence Sufficiency Panel** — 4 metrics grid updates
   (coverage ratio, missing facets, uncertain facets, decision).
4. **Population Intelligence View** — allele-frequency bars + any
   bias findings.
5. **Deterministic Governance View** — rule families with their
   specific hits.
6. **Safe Abstention Mode (if triggered)** — pinned red banner with
   the rule ID that caused the refusal.

For Priya, you should see ~14 events end-to-end, all panels populated,
no abstention banner, JSON export of ~1961 bytes.

For the AFR scenario, you'll see ~13 events, a red abstention banner
citing `ANCESTRY_SCARCITY`, and an Evidence Gap Analysis view.

### Optional: add MongoDB persistence

```bash
docker compose --profile mongo up --build
```

Adds a `swarm-mongo` container on `:27017`. Set in `.env`:

```
MONGODB_URI=mongodb://swarm-mongo:27017
MONGODB_DB=anukriti_swarm
```

Restart the backend container. Now every run is persisted, and
`/api/snapshot/{correlation_id}` returns the full replay bundle.

---

## Path B: Without Docker

```bash
git clone https://github.com/AnukritiAi-hq/anukriti-swarm.git
cd anukriti-swarm

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run a one-shot demo
python -m demos.showcase
```

Expected output (the byte-identical regression signature):

```
...
Pipeline: PASS | 7 stages | 1.2ms total
...
JSON export: 1961 bytes
...
```

### Key demos to walk through

```bash
python -m demos.showcase                            # canonical 1-scenario
python -m demos.unified_demo                        # 3-scenario full lifecycle
python -m demos.safety_demo                         # 5 scenarios: 1 delivered, 4 blocked
python -m demos.interoperability_demo               # 3 scenarios, A2A envelope flow
python -m demos.evaluation_demo                     # 52/61 suite · 4/4 stress · 3/3 ancestry
python -m demos.evidence_sufficiency_demo           # 3 scenarios with sufficiency layer
python -m demos.evidence_sufficiency_abstention_demo # 6 adversarial refusals
```

Each prints a header, the scenarios, a signature footer. All 7 are
regression-tested; any drift in their output is a CI failure.

### Running the backend locally (no Docker)

```bash
# Backend
uvicorn backend.app:app --host 127.0.0.1 --port 8000

# In a separate terminal, frontend
cd frontend && python -m http.server 3000
```

Then browse `http://localhost:3000/pages/index.html`. Same UI as
Path A.

---

## What a healthy run looks like (Priya, clean path)

```
$ python -m demos.unified_demo

Scenario: Clopidogrel + CYP2C19 + South Asian
  ─ SwarmRuntime.run() begins
  ─ Stage 1: context assembled
  ─ Stage 2: orchestrator activated → planner → router → coordinator
  ─   pharmacogene_agent activated
  ─   population_agent activated
  ─   evidence_retrieval activated
  ─ Stage 3: retrieval (12 docs, 4 KG paths)
  ─ Stage 3.5: sufficiency → SUFFICIENT
  ─ Stage 4: verification → all 4 engines pass
  ─ Stage 5: synthesis → narrative emitted
  → Decision: sufficient | Verdict: supported | Uncertainty: low
  → Events: 14 | Gate: ✓

Scenario: Carbamazepine + HLA-B*15:02 + East Asian
  → Decision: sufficient | Verdict: supported | Uncertainty: low
  → Events: 14 | Gate: ✓

Scenario: Codeine + CYP2D6 + African ancestry
  → Decision: downgrade | Verdict: uncertain | Uncertainty: high
  → Events: 13 | Gate: ✗ (R9: POPULATION uncertain)

Total RuntimeEvents across all runs: 41
```

This is the exact output the test suite pins. Any character
difference is a regression signal.

---

## What to poke first

### 1. Change Priya's genotype

In the scenario picker, or in `demos/unified_demo.py`:

```python
# Change from *2/*2 to *1/*17 and observe
{
    "scenario_id": "clopidogrel_sas",
    ...
    "genotype": "*1/*17",
}
```

Expected: phenotype becomes "Ultrarapid Metabolizer" (activity 2.5),
CPIC recommendation switches to a different guidance (may still use
clopidogrel but with caveats). The KG path from your genotype to
the drug changes visibly in the D3 graph.

### 2. Break the generative boundary

Find the verification step's output payload in the console. Try
manually constructing a call to the narrative agent that asks it
to infer a phenotype from scratch (bypassing the deterministic
engine). You should see a `BoundaryViolation` raised with
`ForbiddenAction.INFER_PHENOTYPE`.

### 3. Run the abstention demo

```bash
python -m demos.evidence_sufficiency_abstention_demo
```

Six adversarial scenarios, six refusals, each citing a specific
rule ID. Read the output carefully — the refusal format is itself
a teaching artifact.

### 4. Inspect the MCP persistence

With Mongo running and a few runs in the bank:

```bash
docker exec -it anukriti-swarm-mongo mongosh anukriti_swarm
> db.memory.find().limit(5)
> db.provenance.find({correlation_id: "a986dec2746f"})
```

You'll see the run summaries, the provenance chains,
everything queryable.

### 5. Trigger the ruff hard-gate on a cleanup PR

```bash
# Lint one of the not-yet-hard-gated directories
ruff check interoperability/     # 15-20 findings expected
ruff check core/orchestrator/    # more findings
```

Pick a small directory, fix all the findings, and propose adding
it to the CI hard gate in `.github/workflows/ci.yml`. This is
the good-first-PR path (see session #11 in `.project-status.md`).

---

## Running pgx-core standalone

If you want to play with just the deterministic library:

```bash
pip install anukriti-pgx-core==0.2.1
```

```python
from anukriti_pgx_core import PhenotypeEngine

engine = PhenotypeEngine()
result = engine.infer("CYP2C19", "*2", "*17")
print(result.phenotype)              # Intermediate Metabolizer
print(result.activity_score)         # 1.0
print(result.cpic_table_version)     # 2022.1
print(result.inference_path)         # named_diplotype

# Try variations
for diplotype in [("*1", "*1"), ("*2", "*2"), ("*1", "*17"), ("*17", "*17")]:
    r = engine.infer("CYP2C19", *diplotype)
    print(f"{diplotype} → {r.phenotype} (score {r.activity_score})")
```

Pure deterministic function. No network needed. No LLM keys.

---

## Where to go next

Once the demo is running and you've modified a few inputs:

1. **Read the swarm's `.project-status.md`** — per-session history,
   each session #1 through #12 tells the story of one subsystem
   getting built. Great for understanding "why is this here?"
   questions.
2. **Read pgx-core's `PROJECT_CONTEXT.md`** — the canonical "why"
   doc, with D1-D11 founder decisions.
3. **Read `anukriti-pgx-core/docs/adr/`** — non-obvious decisions
   with "Revisit when" triggers. Good for understanding what the
   platform has *decided not* to do.
4. **Pick a good-first-issue:**
   - Clean an undirty directory for ruff hard-gate adoption
   - Remove the `langchain` and `qdrant-client` orphan deps
   - Add a new gene caller (follow the `GeneCaller` pattern)
   - Write a benchmark scenario in `benchmarks/scenarios.py`

---

## Troubleshooting

### "docker compose" command not found

Make sure you have Docker 20+ (which bundles compose). On Linux,
older compose-as-separate-binary (`docker-compose`) also works.

### Build fails with "no space left on device"

The image is ~500 MB; pip cache and the 1000 Genomes bundled data
(in anukriti) are much larger. `docker system prune` frees space.

### Backend health check returns 503

The container started but uvicorn hasn't warmed up yet. Wait 10s,
re-curl. The healthcheck definition is in `Dockerfile` — 30s
interval, 10s start period.

### Frontend shows "offline"

The backend isn't reachable from the browser. Most common cause:
running on a remote machine where :8000 isn't exposed to your
local network. Use `ssh -L 8000:localhost:8000 -L
3000:localhost:3000 <remote>` to tunnel.

### Tests fail on your local clone

Run `pytest tests/unit/` first (fast). Then `pytest
tests/integration/` (slower, includes subprocess-invoked demo
regression). If the subprocess tests fail, check that the demos
themselves run standalone.

### Demo output has a different byte count than expected

You may have a local modification that's affecting output. `git
status` to check. The regression signatures are pinned to a clean
checkout of `main`.

---

## Summary

You now know:

- `docker compose up` brings up the full stack in ~2 minutes.
- The frontend is live mission control; panels update per-event
  via WebSocket.
- Regression signatures (1961 bytes, 14 events for Priya, 13 for
  AFR) are pinned to catch any drift.
- Poking the system productively: change a genotype, trigger a
  refusal, inspect MCP, lint a directory.
- pgx-core works standalone via `pip install`.

Next: [Module 12 — Glossary](12-glossary.md) for the vocabulary
table, then [Module 13 — Further Reading](13-further-reading.md)
for the deep-link index into each repo.
