# 14 — Where to Go Next

> The course is done. Here's how to actually **use** what you just
> learned.

---

## If you want to read the code

Clone the swarm repo and open these files, in this order:

```
1. anukriti-swarm/core/orchestrator/context.py
   The shape of a run's "notebook." Everything flows through this.

2. anukriti-swarm/core/runtime/runtime.py
   SwarmRuntime.run() — the 5-stage lifecycle in ~500 lines.
   This is the central executable loop.

3. anukriti-swarm/core/orchestrator/boundary.py
   GenerativeBoundary — Module 04 incarnate. Small file,
   outsized importance.

4. anukriti-swarm/agents/pharmacogene/cyp2c19_agent.py
   One concrete agent. Simple enough to read top-to-bottom.

5. anukriti-swarm/interoperability/shared_context/envelope.py
   AgentContextEnvelope + BiomedicalContextType — Module 02.
```

After these five, you've seen the core of the system. Everything
else is elaboration.

---

## If you want to run things

Three levels of "running," from fastest to deepest:

### Level 1 — just watch (2 minutes)

```bash
git clone https://github.com/AnukritiAi-hq/anukriti-swarm.git
cd anukriti-swarm
docker compose up --build
```

Open `http://localhost:3000/pages/index.html`, click "Activate
Swarm," watch the D3 visualization animate as events stream
in live.

### Level 2 — run demos (10 minutes)

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# One scenario
python -m demos.showcase

# Three scenarios with sufficiency checkpoint
python -m demos.unified_demo

# Six adversarial refusals — all named rule IDs
python -m demos.evidence_sufficiency_abstention_demo
```

The output of each demo is pinned in CI. If yours matches the
pinned signature, your clone is clean.

### Level 3 — modify and re-run (an hour)

Open `demos/unified_demo.py`. Find the scenarios. Change Priya's
genotype from `*2/*2` to `*1/*17`. Re-run.

Expected changes:
- Phenotype becomes "Ultrarapid Metabolizer" (activity 2.5)
- Recommendation text changes (different CPIC row)
- KG path visualization changes (*17 instead of *2)
- JSON export bytes change — intentionally, because the output is
  different

You've just experienced how **one input change propagates through
all 5 stages** deterministically.

---

## First contributions (good first issues)

In rough order of difficulty:

### Easy: documentation

- Find a passage in any module (this course or the main
  `anukriti_docs`) that confused you. Open an issue or a PR to
  fix it.
- Add a short Python snippet to a module that demonstrates a
  concept.
- Write a new glossary entry (see [`glossary.md`](glossary.md)
  — always room for more terms).

### Medium: linting and cleanup

The swarm's ruff hard-gate is being adopted progressively
(session #11 of the main docs). Pick a directory from the
continuation list:

```
1. interoperability/     (session #5, tight scope)
2. core/orchestrator/    (session #0, older but well-documented)
3. knowledge_graph/      (session #6 sibling)
```

Run `ruff check <dir>` and fix the findings. Then propose
adding that directory to the CI hard gate. Small, low-risk,
highly visible contribution.

### Medium: add a benchmark scenario

Open `anukriti-swarm/benchmarks/scenarios.py`. Scenarios are
(gene, drug, population) triples with expected outputs. Add a
new one — say, a warfarin + CYP2C9 + EAS case. Run the benchmark
suite to see if the system agrees.

### Advanced: a new agent

Follow the pattern in `agents/pharmacogene/cyp2c19_agent.py`.
Create an agent for a gene we don't cover yet (SLCO1B1 is a
candidate — we have calling but no full agent). You'll need:

- A new file `agents/pharmacogene/slco1b1_agent.py`
- Registration in `agents/registry/`
- Unit tests in `tests/unit/`
- A scope addition to `BiomedicalContextType` if the agent
  emits a new context kind (this requires review)

---

## If you want to go broader

### The main engineering course

Our **[main `anukriti_docs` course](../README.md)** covers the
same platform from an engineering angle — architecture,
determinism, gene matching, tech stack, evidence sufficiency,
request flow. 14 modules. Longer and more technical than this
course.

Read that if you want to:
- Understand the three-repo platform (pgx-core + anukriti + swarm)
- Go deep on deterministic gene matching
- See the full tech-stack reasoning
- Read the full request flow at engineering depth

### Research pointers

Concepts in this course map to the following research directions.
If you want to go deep on the theory, here's where to start:

- **Multi-agent systems (MAS)** — search "agent-based software
  engineering" and "swarm intelligence"
- **ReAct (reasoning + acting)** — Yao et al., "ReAct: Synergizing
  Reasoning and Acting in Language Models" (2022)
- **RAG (retrieval-augmented generation)** — Lewis et al., "RAG
  for knowledge-intensive NLP tasks" (2020)
- **GraphRAG** — Edge et al., "GraphRAG: A Graph-Based
  Retrieval-Augmented Generation Approach" (2024)
- **Model Context Protocol (MCP)** — the evolving standard at
  https://modelcontextprotocol.io
- **SURE-RAG (evidence verification)** — Yoran et al., "Making
  Retrieval-Augmented Language Models Robust to Irrelevant
  Context" (2023)
- **Stop-RAG (adaptive stopping)** — various 2024 papers on
  sufficiency-gated retrieval loops

These are the papers whose patterns we implemented in
pharmacogenomic-specific form. Our system isn't the first to
do any of these — but it's one of the few doing them all
together for a high-stakes medical domain.

---

## Where to get help

- **Something in the course is unclear** — open an issue on
  this repo (`anukriti_docs`) with the module number.
- **The code doesn't match what a module says** — also an issue,
  with as much detail as you can share. This is a doc-drift bug.
- **You want to discuss a design** — the platform's ADRs live in
  `anukriti-pgx-core/docs/adr/`. Open an issue that references
  an existing ADR or proposes a new one.
- **Clinical / biomedical questions** — these docs don't answer
  them. Consult a pharmacogenomics-trained pharmacist or
  clinical geneticist. CPIC (<https://cpicpgx.org>) is the
  authoritative public resource.

---

## A final thought

Agentic AI, done carefully, is **not** about giving more power to
a single AI brain. It's about building a **system of small,
named, specialized, checkable pieces** — each of which a human
can read, understand, test, and audit.

Our platform has:
- 9 core specialist agents
- 14 closed enums in the scope-firewall layer
- 12 + 10 + 9 = 31 rules in the sufficiency / verifier /
  uncertainty tables
- 6 MCP services with 31 tools
- 4 verification engines
- 234 unit tests
- 29 runnable demos
- 12 closed runtime event kinds
- 4 forbidden LLM actions

**Every one of these is a small, specific, readable piece of
code.** None of them is magic. None of them is a black box.

If you take one thing away from this course: **AI that matters
is AI you can read**.

---

Thanks for taking the course. Go build something honest.

---

Jump back to: [README](README.md) · [Glossary](glossary.md)
