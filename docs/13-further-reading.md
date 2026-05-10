# Module 13 — Further Reading

> Pointers into the real repos' architecture docs, design
> decisions, and session logs. Use this as a navigation aid after
> you've finished the modular course.

---

## anukriti-pgx-core

### Start with

- [`README.md`](https://github.com/AnukritiAi-hq/anukriti-pgx-core/blob/main/README.md)
  — outward-facing overview of what the library does
- [`PLATFORM.md`](https://github.com/AnukritiAi-hq/anukriti-pgx-core/blob/main/PLATFORM.md)
  — canonical three-repo map (the doc this course is a learning
  path into)
- [`PROJECT_CONTEXT.md`](https://github.com/AnukritiAi-hq/anukriti-pgx-core/blob/main/PROJECT_CONTEXT.md)
  — the "why" doc. D1–D11 locked founder decisions, F-series
  forward-work items, regression contract, session history

### Contribution

- [`CONTRIBUTING.md`](https://github.com/AnukritiAi-hq/anukriti-pgx-core/blob/main/CONTRIBUTING.md)
  — library-specific contribution guide
- [`SECURITY.md`](https://github.com/AnukritiAi-hq/anukriti-pgx-core/blob/main/SECURITY.md)
  — threat model + responsible disclosure policy
- [`CODE_OF_CONDUCT.md`](https://github.com/AnukritiAi-hq/anukriti-pgx-core/blob/main/CODE_OF_CONDUCT.md)
  — research-ethics commitments + Contributor Covenant 2.1

### Decisions

- [`docs/adr/README.md`](https://github.com/AnukritiAi-hq/anukriti-pgx-core/tree/main/docs/adr)
  — ADR framework (when to write, numbering, format)
- [`docs/adr/0001-founding-engineer-scope-and-deferrals.md`](https://github.com/AnukritiAi-hq/anukriti-pgx-core/blob/main/docs/adr/0001-founding-engineer-scope-and-deferrals.md)
  — platform onboarding surface + 3 explicit deferrals with
  "Revisit when" triggers

### Operations

- [`RELEASING.md`](https://github.com/AnukritiAi-hq/anukriti-pgx-core/blob/main/RELEASING.md)
  — OIDC trusted-publisher PyPI release runbook
- [`CHANGELOG.md`](https://github.com/AnukritiAi-hq/anukriti-pgx-core/blob/main/CHANGELOG.md)
  — per-version change log

### Biomedical provenance

- `CPIC_PROVENANCE.json` (in the repo) — every CPIC table with
  source URL, publication date, audit status
- `CPIC_PROVENANCE.md` — narrative companion to the JSON

---

## anukriti-swarm

### Start with

- [`README.md`](https://github.com/AnukritiAi-hq/anukriti-swarm/blob/main/README.md)
  — landing page with 30-second pitch
- [`ARCHITECTURE.md`](https://github.com/AnukritiAi-hq/anukriti-swarm/blob/main/ARCHITECTURE.md)
  — system philosophy, actual tech stack (post-2026-05-10 rewrite),
  module map, runtime flow, 6 invariants
- [`.project-status.md`](https://github.com/AnukritiAi-hq/anukriti-swarm/blob/main/.project-status.md)
  — the living session log. Each session #1 through #12 tells the
  story of one subsystem getting built

### Architecture deep-dives

Per-subsystem design docs in `architecture/`:

| Doc | Subject |
|-----|---------|
| `architecture/unified-runtime.md` | SwarmRuntime + UnifiedExecutionReport + event stream |
| `architecture/backend-api.md` | FastAPI + WebSocket + RunCache |
| `architecture/evidence-sufficiency.md` | Session #6 sufficiency layer — 4 sub-layers, 12+10+9 rules |
| `architecture/pharmacogenomic-kg.md` | KG schema + traversal + population weighting |
| `architecture/interoperability.md` | A2A envelope + bus + shared context (session #5) |
| `architecture/evaluation-framework.md` | 6 suites + stress + ancestry (session #4) |
| `architecture/observability-visualization.md` | Tracing + metrics + cinematic mode (session #3) |
| `architecture/verification-safety.md` | 4 safety engines (session #2) |
| `architecture/mcp-infrastructure.md` | 6 MCP services + 31 tools + replay |
| `architecture/gemini-orchestration.md` | Orchestrator + boundary + deterministic-first |

### Demo entry points

- `demos/showcase.py` — canonical 1-scenario demo (pinned to
  1961-byte JSON output)
- `demos/unified_demo.py` — 3-scenario full lifecycle (14+14+13 events)
- `demos/safety_demo.py` — 5 scenarios, 1 delivered, 4 blocked
- `demos/evidence_sufficiency_demo.py` — sufficiency layer in action
- `demos/evidence_sufficiency_abstention_demo.py` — 6 adversarial
  refusals with named rule IDs
- `demos/interoperability_demo.py` — A2A envelope flow
- `demos/evaluation_demo.py` — full suite sweep

### CI and quality gates

- [`.github/workflows/ci.yml`](https://github.com/AnukritiAi-hq/anukriti-swarm/blob/main/.github/workflows/ci.yml)
  — test matrix (3.11 + 3.12), linting (strangler-fig), flagship
  demo sweep
- [`pyproject.toml`](https://github.com/AnukritiAi-hq/anukriti-swarm/blob/main/pyproject.toml)
  — ruff + pytest configuration

### Docker

- `Dockerfile` — multi-stage build, python:3.12-slim-bookworm base,
  non-root UID 10001
- `docker-compose.yml` — backend + frontend + optional MongoDB
  profile

---

## anukriti (product)

### Start with

- [`README.md`](https://github.com/Abm32/Synthatrial/blob/clinical-grade-pgx/README.md)
  — product overview, FastAPI endpoints, deployment
- [`CLINICAL_GRADE_ROADMAP.md`](https://github.com/Abm32/Synthatrial/blob/clinical-grade-pgx/CLINICAL_GRADE_ROADMAP.md)
  — the 4-week roadmap context for the current `clinical-grade-pgx`
  branch

### Organization

- `docs/` — reorganized progress reports (58 files as of 2026-05-10)
- `docs/architecture/` — 5 architecture docs
- `docs/updates/` — 28 weekly/daily/status snapshots
- `docs/steering/` — curated steering docs + `archive/` for
  superseded versions

### Key source files

- `api.py`, `app.py`, `main.py` — FastAPI entry points
- `src/*_caller.py` — shim layer, delegates to pgx-core for the 12
  genes pgx-core owns; keeps GST and HLA-B special handling local
  (per pgx-core PROJECT_CONTEXT.md §D8)

---

## External references

### Clinical pharmacogenomics authorities

- **CPIC (Clinical Pharmacogenetics Implementation Consortium)** —
  https://cpicpgx.org. The authority whose guidelines the library
  pins.
- **PharmVar** — https://pharmvar.org. Canonical star-allele
  definitions.
- **PharmGKB** — https://www.pharmgkb.org. Broader pharmacogenomics
  knowledge base with gene-drug annotations.

### Population genomics

- **1000 Genomes Project** — https://www.internationalgenome.org.
  Source of super-population allele frequencies.
- **gnomAD** — https://gnomad.broadinstitute.org. Large-scale
  population genomics database.

### Biomedical identifiers

- **dbSNP** — https://www.ncbi.nlm.nih.gov/snp/. Where rsIDs come
  from.
- **PubMed** — https://pubmed.ncbi.nlm.nih.gov. Where PMID citations
  resolve.
- **ClinVar** — https://www.ncbi.nlm.nih.gov/clinvar/. Clinical
  significance of human variants.

### Standards the platform respects

- **VCF (Variant Call Format)** — https://samtools.github.io/hts-specs/VCFv4.2.pdf
- **FHIR (Fast Healthcare Interoperability Resources)** —
  https://www.hl7.org/fhir/. The product's clinical export format.
- **PROV-DM** — https://www.w3.org/TR/prov-dm/. The provenance data
  model the platform's provenance chains are shaped like.
- **MCP (Model Context Protocol)** — the evolving standard for
  context persistence across AI systems. https://modelcontextprotocol.io.

### Papers / guidelines worth knowing

The platform's 37-node knowledge graph seed is derived from:

- CPIC CYP2C19 + clopidogrel guidelines (published 2011, updated
  2022.1)
- CPIC CYP2D6 + codeine guidelines (2012, updated 2021)
- CPIC HLA-B*15:02 + carbamazepine guidelines (2013, updated 2018)
- CPIC CYP2C9 + warfarin guidelines (2011, updated 2017)
- CPIC SLCO1B1 + simvastatin guidelines (2014, updated 2022)

PMID:34032273 is the canonical CYP2C19 clopidogrel citation.

---

## How to read the session history

The swarm's `.project-status.md` documents 12 sessions of work from
2026-05-08 through 2026-05-10. Each session is a coherent unit —
one brief, multiple micro-commits, one architecture doc.

For historical archaeology:

1. Open `.project-status.md`, scroll to the session of interest.
2. Read the "⭐ Session #N" heading's summary.
3. Note the commit SHAs in the "commit table" (if present).
4. Run `git show <sha>` on a specific commit for its full body.
5. Read the linked `architecture/<subsystem>.md` for the design.

Sessions by subsystem:

- **Session #0** — pre-session. Core orchestrator, Gemini
  orchestration.
- **Session #1** — MCP verification logs, memory-aware orchestration.
- **Session #2** — Deterministic safety engine (4 verification
  engines).
- **Session #3** — Observability + visualization.
- **Session #4** — Evaluation + benchmarking framework.
- **Session #5** — Interoperability (A2A envelope, agent bus).
- **Session #6** — Evidence sufficiency layer + knowledge graph.
- **Session #7** — Unified orchestration + live backend + D3 frontend.
- **Session #8** — Test suite hardening (234 tests).
- **Session #9** — GitHub Actions CI.
- **Session #10, #11** — Progressive ruff hard-gate adoption.
- **Session #12** — Founding-engineer scale-readiness pass
  (platform docs, Docker, ADR framework).

---

## Recommended reading sequences after this course

**I want to contribute to the phenotype engine.**
1. Finish the course
2. Read `anukriti-pgx-core/PROJECT_CONTEXT.md` cover to cover
3. Read D1–D11 decisions carefully
4. Run the pgx-core regression gate
5. Pick a gene from the `CPIC_PROVENANCE.json` "needs_audit" list

**I want to add a new agent.**
1. Finish the course
2. Read `anukriti-swarm/architecture/interoperability.md`
3. Read `anukriti-swarm/architecture/unified-runtime.md`
4. Pick an existing agent (`agents/pharmacogene/`) and copy its
   structure
5. Wire into the agent bus with a new `BiomedicalContextType` —
   remember this is a closed-enum change requiring a review

**I want to add a new verification engine.**
1. Finish the course
2. Read `anukriti-swarm/architecture/verification-safety.md`
3. The 4 existing engines are the canonical examples
4. Your new engine slots into `core/verification/` as a peer

**I want to deploy the product.**
1. Read `anukriti/README.md` and
   `anukriti/CLINICAL_GRADE_ROADMAP.md`
2. Follow the existing `docker-compose.prod.yml` pattern
3. See `anukriti/.github/workflows/` for the deployment CI

---

## End of the course

You've read through 14 modules covering what Anukriti is, how the
three repos fit together, the biomedical foundations, the
deterministic architecture, the tech stack with reasoning, the
evidence sufficiency rules, and the end-to-end request flow.

You're ready to:

- Read any of the three repos' code with context
- Propose a contribution that fits the platform's scope and discipline
- Explain to a clinician or reviewer why the platform is
  trustworthy
- Identify where a new feature belongs and what it needs to preserve

If something in these docs was unclear, the whole point is to fix
it — open an issue against this repo with the module number and
the passage. Documentation debt is treated as a first-class
concern.

Welcome to the team.
