# Three-Repo Integration — Deep Dive

> **Audience:** founder, prospective engineers, technical reviewers,
> anyone who wants to understand how `anukriti-pgx-core`,
> `anukriti-swarm`, and `anukriti` (+ `anukriti-api`) are wired
> together at the import level — what crosses HTTP boundaries, what
> runs in-process, where the connective tissue actually lives.
>
> **Last updated:** 2026-05-16
>
> **Companion docs:**
>   - [`DETERMINISTIC_ENGINE_DEEP_DIVE.md`](DETERMINISTIC_ENGINE_DEEP_DIVE.md) — what the engine itself computes (VCF → diplotype → phenotype → CPIC)
>   - [`EVIDENCE_SUFFICIENCY_LAYER_DEEP_DIVE.md`](EVIDENCE_SUFFICIENCY_LAYER_DEEP_DIVE.md) — how the swarm decides whether to deliver the engine's answer
>   - High-level intro: [`docs/02-the-three-repos.md`](docs/02-the-three-repos.md), [`docs/10-how-the-pieces-talk.md`](docs/10-how-the-pieces-talk.md)
>   - Stack docker-compose reference: [`anukriti-stack/README.md`](https://github.com/AnukritiAi-hq/anukriti-stack/blob/main/README.md)

---

## TL;DR

The connective tissue between the three repos is a **PyPI library**,
not an HTTP boundary:

```
anukriti-pgx-core==0.2.1   (PyPI library)
        ▲           ▲
        │           │
        │ pip install
        │           │
   ┌────┴───┐   ┌───┴────┐
   │ swarm  │   │ anukriti│   (and anukriti-api)
   └────┬───┘   └───┬────┘
        │           │
        │           │   (anukriti-api also imports
        │           ▼    from swarm via PYTHONPATH)
        │  ┌────────────────┐
        │  │  anukriti-api  │
        └─►│  (gateway)     │
           └────────────────┘
```

Three properties hold for every request:

1. **No HTTP between pgx-core, swarm, and api.** The api process imports the swarm package directly. The swarm imports pgx-core directly. All function calls are in-process Python calls, no network hops.
2. **The deterministic engine is reused via singleton.** `PhenotypeEngine()` loads the pinned JSON tables once at import time. `SwarmRuntime` is a process-wide singleton with warm KG / retrievers. New requests reuse both.
3. **The shim pattern enables incremental migration.** `anukriti-swarm/rules/phenotype_rules.py` is a 6-line re-export of `anukriti_pgx_core.PhenotypeEngine.infer`, so swarm-side consumers don't need to change during migration. When all swarm call sites import from `anukriti_pgx_core` directly, the shim can be deleted without touching them.

This document captures the import topology (with file paths), the in-process composition pattern, the end-to-end request flow with code citations, and the change-cadence rationale for the three-repo split.

---

## Table of contents

1. [The three repos and what they own](#1-the-three-repos-and-what-they-own)
2. [Why three repos (the change-cadence argument)](#2-why-three-repos-the-change-cadence-argument)
3. [The import topology](#3-the-import-topology)
4. [The shim pattern — `rules/phenotype_rules.py`](#4-the-shim-pattern--rulesphenotype_rulespy)
5. [The 17 files in the swarm that consume the engine](#5-the-17-files-in-the-swarm-that-consume-the-engine)
6. [Where `anukriti-api` fits](#6-where-anukriti-api-fits)
7. [The end-to-end request flow](#7-the-end-to-end-request-flow)
8. [The Docker image story (`anukriti-stack`)](#8-the-docker-image-story-anukriti-stack)
9. [What the swarm adds on top of the engine](#9-what-the-swarm-adds-on-top-of-the-engine)
10. [Migration note: when the shim can be deleted](#10-migration-note-when-the-shim-can-be-deleted)
11. [What this integration deliberately does NOT do](#11-what-this-integration-deliberately-does-not-do)

---

## 1. The three repos and what they own

| Repo | Role | Distribution | What it owns |
|---|---|---|---|
| **`anukriti-pgx-core`** | The deterministic engine | PyPI library (`anukriti-pgx-core==0.2.1`) | PharmVar TSVs, pinned CPIC JSON tables, `PhenotypeEngine`, 13 gene callers, activity-score logic, provenance manifest, frozen output records |
| **`anukriti-swarm`** | The multi-agent reasoning runtime | git-only (sibling repo) | `SwarmRuntime` 5-stage lifecycle, 9 specialist agents, agent bus, MCP services, evidence-sufficiency rules, KG, observability, generative-narrative boundary |
| **`anukriti`** (Synthatrial) | The clinical product | git-only (private) | Streamlit UI, FastAPI product surface, drug reranker (SMILES side-path), explanation templates, FHIR adapters, validation harness |
| **`anukriti-api`** (separate repo, not the Synthatrial product) | The Base44-facing API gateway | git-only (sibling repo) | FastAPI gateway, auth, webhooks, rate limit, frontend-shape ↔ platform-shape adapters, the 4-workflow stratification surface (`clopidogrel`, `warfarin`, `simvastatin`, planned cohort) |

`anukriti-pgx-core` ships to PyPI under tag `0.2.1`. Both the swarm
and the api **pin it as a regular dependency**, not via path or git
URL.

```bash
# anukriti-swarm/requirements.txt:
#   Published to PyPI from https://github.com/AnukritiAi-hq/anukriti-pgx-core
anukriti-pgx-core==0.2.1

# anukriti-api/requirements.txt:
#   Runtime dependencies — pinned to match anukriti-swarm.
anukriti-pgx-core==0.2.1
```

Same exact version pin in both. That guarantees the deterministic
engine is byte-identical across both the swarm process and the api
process.

The product (`anukriti`) imports from `anukriti_pgx_core` in two
files (`src/allele_caller.py`, `src/slco1b1_caller.py`) for direct
deterministic calling — but mostly delegates to the swarm via the
api gateway.

---

## 2. Why three repos (the change-cadence argument)

The three repos exist because they have **different change cadences
and different trust requirements**:

| Repo | Cadence | Who can change it | Trust requirement |
|---|---|---|---|
| `anukriti-pgx-core` | Slow (semver-pinned, every release gates 51 pytest tests + a CPIC provenance audit) | Maintainers + CPIC audit reviewers | **Highest** — every change re-validated against pinned CPIC tables; provenance manifest enforced by `tests/test_cpic_provenance.py` |
| `anukriti-swarm` | Medium (per-session commits, byte-locked demo signatures) | Engineering team | High — closed-enum scope firewall + 244 pytest tests + 7 byte-locked flagship demos |
| `anukriti` | Fast (product iteration, hackathon features) | Product team | Lower — UI changes don't need CPIC review |

Splitting them buys three concrete things:

- **A new product feature in `anukriti` can ship without re-validating CPIC tables.** The product depends on a *pinned* version of the library; the library's audit cadence is decoupled from the product's.
- **A swarm-side experiment with a new agent doesn't risk breaking the deterministic engine.** Agents are added/removed from the swarm without ever touching the library's pinned data.
- **A `pgx-core` release is a known, reviewable artifact.** When `pgx-core 0.3.0` ships with PharmVar API integration (Phase B per [`IDEA_REFINEMENT_AND_PHASING_2026-05-14.md`](IDEA_REFINEMENT_AND_PHASING_2026-05-14.md)), both the swarm and the product can pin to it independently and roll back independently.

The library being a **PyPI package** (not a path dependency, not a git submodule) is the discipline that enforces this. A path dependency to a sibling directory would silently couple the repos. PyPI gives us **versioned releases**.

---

## 3. The import topology

### `anukriti-pgx-core` — the public surface

The library's `__init__.py` declares an explicit `__all__` of
17 public symbols, organized by layer:

```python
# anukriti-pgx-core/anukriti_pgx_core/__init__.py
__all__ = [
    # Layer 2 — phenotype
    "PhenotypeEngine",
    "PhenotypeInference",
    # Layer 1 — calling (Batch 1)
    "GeneCaller",
    "CYP2C19Caller",
    "CYP2D6Caller",
    # Layer 1 — calling (Batch 2)
    "CYP1A2Caller", "CYP2B6Caller", "CYP2C9Caller",
    "CYP3A4Caller", "CYP3A5Caller",
    # Layer 1 — calling (Batch 3)
    "DPYDCaller", "G6PDCaller", "NAT2Caller", "TPMTCaller",
    # Layer 1 — calling (Batch 4: GenotypeCaller pattern)
    "GenotypeCaller", "VKORC1Caller",
    # Layer 1 — calling (Batch 5: second GenotypeCaller)
    "SLCO1B1Caller",
    # Layer 1 — shared types
    "VCFVariant", "Diplotype", "VerificationResult", "GenotypeCall",
    # Helpers (preserved for anukriti/src/allele_caller.py shim)
    "alt_dosage", "genotype_to_alleles", "build_diplotype",
    # Errors
    "PgxCoreError", "TableLoadError",
    "UnknownAlleleError", "UnsupportedGeneError",
    # Version
    "__version__", "RULE_VERSION",
]
```

The header docstring is honest about which consumers use which layer:

```
Layer 2 only (what Swarm uses):
    >>> from anukriti_pgx_core import PhenotypeEngine
    >>> engine = PhenotypeEngine()
    >>> result = engine.infer("CYP2C19", "*1", "*17")
    >>> result.phenotype
    'Rapid Metabolizer'

Layer 1 + Layer 2 chained (what Anukriti's api.py consumes):
    >>> from anukriti_pgx_core import CYP2C19Caller, VCFVariant
    >>> caller = CYP2C19Caller()
    >>> variants = {"rs12248560": VCFVariant(ref="C", alt="T", genotype="0/1")}
    >>> result = caller.call(variants)
    >>> result.diplotype, result.phenotype.phenotype
    ('*1/*17', 'Rapid Metabolizer')
```

### Who imports what

| Caller | Imports from `anukriti_pgx_core` | Imports from `core.*` (swarm) |
|---|---|---|
| `anukriti-swarm/rules/phenotype_rules.py` | `PhenotypeEngine`, `PhenotypeInference` | — |
| `anukriti/src/allele_caller.py` | helpers (`alt_dosage`, `build_diplotype`, etc.) | — |
| `anukriti/src/slco1b1_caller.py` | `SLCO1B1Caller` + types | — |
| `anukriti-api/app/adapters.py` | 5 callers + `VCFVariant` | `SwarmRuntime`, `UnifiedExecutionContext`, `InMemoryEventStream` |
| `anukriti-api/app/routers/cohort.py` | (none directly) | `SuperPopulation`, `core.simulation.*` |
| `anukriti-api/app/routers/runs.py` | (none directly) | (uses adapters indirectly) |
| `anukriti-api/app/routers/llm_context.py` | (none directly) | (uses adapters indirectly) |
| `anukriti-api/app/main.py` | (none directly) | (FastAPI app surface) |

The api process imports from **both** `anukriti_pgx_core` (the pinned
library) and `core.runtime` (the swarm package, made importable via
`PYTHONPATH=/opt/api:/opt/swarm` in `Dockerfile.api`).

---

## 4. The shim pattern — `rules/phenotype_rules.py`

This is the single most important file for understanding the
swarm/pgx-core relationship. It's 6 lines of code with a long
docstring:

```python
# anukriti-swarm/rules/phenotype_rules.py
"""Legacy phenotype-rules entry point — now a shim over anukriti-pgx-core.

History
-------
Before Phase 1 of the anukriti-pgx-core extraction, this module was the
authoritative deterministic phenotype inference layer. It held:

  - ALLELE_ACTIVITY_SCORES     dict[gene, dict[allele, score]]
  - PHENOTYPE_RANGES           dict[gene, list[tuple[low, high, phenotype]]]
  - NAMED_DIPLOTYPES           dict[gene, dict[diplotype, phenotype]]
  - infer_phenotype()          main call
  - get_activity_score()       single-allele lookup
  - PhenotypeInference         frozen dataclass

All of that logic and data now lives in the ``anukriti-pgx-core`` package:

  - ``anukriti_pgx_core.phenotype.PhenotypeEngine``
  - ``anukriti_pgx_core.types.PhenotypeInference``
  - pinned JSON tables in ``anukriti_pgx_core/phenotype/tables/``

This module stays as a thin re-export so existing swarm-side consumers
(agents/pharmacogene/base.py, core/verification/safety.py,
core/runtime/runtime.py, tests, any future imports) don't need to change
during the migration. When swarm-side call sites all import from
``anukriti_pgx_core`` directly, this file can be deleted without
touching any of them.

Behaviour is byte-identical:
  - Same ``PhenotypeInference`` return shape (with two additional
    provenance fields, ``cpic_table_version`` and ``pgx_core_version``,
    that are populated but default-empty so unpacking-style code stays
    safe).
  - Same ``rule_version`` string (``cpic_activity_score_v2``).
  - Same dispatch order (named-diplotype lookup first for CYP2C19,
    additive activity-score fallback otherwise).
"""

from __future__ import annotations

from anukriti_pgx_core import PhenotypeEngine
from anukriti_pgx_core.types import PhenotypeInference

# Singleton engine. Loading the pinned JSON tables happens once at
# import time, identical to how the old module's module-level dicts
# were populated once.
_ENGINE = PhenotypeEngine()


def infer_phenotype(gene: str, allele1: str, allele2: str) -> PhenotypeInference:
    """Deterministic phenotype inference. See PhenotypeEngine.infer."""
    return _ENGINE.infer(gene, allele1, allele2)


def get_activity_score(gene: str, allele: str) -> float | None:
    """Return the activity score for an allele, or None if unknown."""
    return _ENGINE.activity_score(gene, allele)


# Snapshot of the activity-score tables. ``safety.py`` reads this dict
# directly (membership checks on ALLELE_ACTIVITY_SCORES[gene]); keeping
# the same shape means no changes are needed there.
ALLELE_ACTIVITY_SCORES: dict[str, dict[str, float]] = (
    _ENGINE.activity_scores_snapshot()
)
```

**Why the shim exists.** Before pgx-core was extracted, the
phenotype logic lived inside the swarm. Extraction happened in a
single coordinated commit. Without the shim, every call site in the
swarm would need a simultaneous import-rewrite — risky for the
244-test pytest suite and the 7 byte-locked flagship demos. The
shim is the migration discipline: it lets the engine extraction
land cleanly while leaving the call-site rewrite as an independent
follow-up.

**The singleton instance** (`_ENGINE = PhenotypeEngine()`) loads
all pinned JSON tables **once at import time**. Every subsequent
`infer_phenotype()` call is a dict lookup with no I/O. This matches
the pre-extraction module's module-level-dict performance —
zero-overhead migration.

---

## 5. The 17 files in the swarm that consume the engine

A `grep -lE "from rules.phenotype_rules|infer_phenotype" anukriti-swarm/`
returns 17 files. The substantive ones (excluding tests, archived
docs, and CI config):

| File | What it does with the engine |
|---|---|
| `rules/phenotype_rules.py` | The shim — re-exports `PhenotypeEngine.infer` as `infer_phenotype` |
| `agents/pharmacogene/base.py` | The pharmacogene-specialist agents call `infer_phenotype(self.gene, allele1, allele2)` — line 77 of `base.py` is the only call site in this file |
| `core/verification/safety.py` | The deterministic safety engine cross-checks phenotype calls against `ALLELE_ACTIVITY_SCORES` (the snapshot exposed by the shim) |
| `core/runtime/runtime.py` | The runtime imports the engine at the appropriate stage |
| `core/orchestrator/boundary.py` | The `GenerativeBoundary` uses the engine's output to detect LLM hallucination — if the LLM claims a phenotype the engine didn't produce, the boundary raises `fabricate_claim` |
| `knowledge_graph/seed.py` | The KG seed cross-validates allele-functionality info against `ALLELE_ACTIVITY_SCORES`; the provenance check confirms agreement between the KG seed and the pinned CPIC table |
| `benchmarks/adversarial.py` | Adversarial benchmarks construct expected phenotype calls via `infer_phenotype` to compare against agent outputs |

The exact call site in `agents/pharmacogene/base.py`:

```python
# anukriti-swarm/agents/pharmacogene/base.py
from rules.phenotype_rules import PhenotypeInference, infer_phenotype
# ...
class PharmacogeneAgent:
    def __init__(self, gene: str): self.gene = gene
    # ...
    def reason(self, allele1, allele2):
        # ...
        inference = infer_phenotype(self.gene, allele1, allele2)  # line 77
        # ... use inference.phenotype, inference.activity_score, etc.
```

That single line is the bridge between "the swarm's reasoning" and
"CPIC's authoritative phenotype lookup." Everything that happens
above it is the swarm's multi-agent orchestration; everything that
happens below it is `PhenotypeEngine.infer()` in pgx-core.

---

## 6. Where `anukriti-api` fits

`anukriti-api` is the **Base44-facing FastAPI gateway** — distinct
from `anukriti` (the Synthatrial product). It exists because the
frontend's wire format is not the platform's native format. The
gateway's job is to translate between them.

### The frontend wire format

```json
// POST /runs
{
  "workflow":     "clopidogrel",
  "population":   "SAS",
  "snps": [
    {"id": "rs4244285",  "genotype": "AA"},
    {"id": "rs12248560", "genotype": "CC"}
  ],
  "cohort_size": 1
}
```

### The platform's native format

```python
UnifiedExecutionContext.new(
    drug="clopidogrel",
    gene="CYP2C19",
    population="SAS",
    genotype="*2/*2",     # ← this is a diplotype, not a wildtype-vs-variant string
)
```

### The `adapters.py` translator — the only place that knows both formats

```python
# anukriti-api/app/adapters.py
"""Adapter layer — translates Base44 frontend shape into platform-native shape.

Frontend sends:

    {
      "workflow": "clopidogrel" | "warfarin" | "simvastatin",
      "population": "AFR" | "AMR" | "EAS" | "EUR" | "SAS",
      "snps": [{"id": "rs4244285", "genotype": "AA"}, ...],
      "cohort_size": 1
    }

Platform expects:

    UnifiedExecutionContext.new(drug=..., gene=..., population=..., genotype=...)

This module is the ONLY place that knows about Base44's wire format.
Every downstream module talks the platform's native (drug, gene,
population, genotype) tuple.

The translation steps:

    1. workflow            -> (drug, gene) via WORKFLOW_TO_SCOPE
    2. snps[] + workflow   -> diplotype (e.g. "*1/*17") via call_diplotype()
                              using anukriti-pgx-core caller classes
    3. (drug, gene,        -> UnifiedExecutionContext via to_swarm_context()
        population,
        diplotype)

The runtime is reused across requests (warm KG / indexer / retrievers).
"""
from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any

# pgx-core — deterministic biomedical truth (PyPI library)
from anukriti_pgx_core import (
    CYP2C9Caller,
    CYP2C19Caller,
    SLCO1B1Caller,
    VCFVariant,
    VKORC1Caller,
)

# swarm — reasoning runtime (imported as sibling repo via PYTHONPATH)
from core.runtime import (  # type: ignore[import-not-found]
    InMemoryEventStream,
    SwarmRuntime,
    UnifiedExecutionContext,
)
```

The two import blocks above show the integration discipline in
plain code: the api process pulls deterministic truth from the
**pinned PyPI library** and the reasoning runtime from the
**sibling swarm repo** via PYTHONPATH. Same Python process, two
sources.

### The 4 workflows — mapped to (drug, gene) tuples

```python
# anukriti-api/app/adapters.py
WORKFLOW_TO_SCOPE: dict[str, tuple[str, str]] = {
    "clopidogrel": ("clopidogrel", "CYP2C19"),
    "warfarin":    ("warfarin",    "CYP2C9"),   # primary; VKORC1 in genotype
    "simvastatin": ("simvastatin", "SLCO1B1"),
}

WORKFLOW_RSIDS: dict[str, dict[str, list[str]]] = {
    "clopidogrel": {
        "required": ["rs4244285"],
        "optional": ["rs4986893", "rs12248560", "rs17884712"],
    },
    "warfarin": {
        # rs1799853 = CYP2C9*2; rs1057910 = CYP2C9*3; rs9923231 = VKORC1
        "required": ["rs1799853", "rs1057910", "rs9923231"],
        "optional": ["rs2108622", "rs28371686", "rs9332131"],
    },
    "simvastatin": {
        "required": ["rs4149056"],
        "optional": ["rs56101265"],
    },
}
```

Each workflow declares the rsIDs the frontend must supply (and
optional ones it may), the gene to pass to the runtime, and the
drug the runtime should reason about. **Adding a new workflow is
purely a code change in this module** — the frontend wire format
is unchanged, the platform is unchanged.

### The process-wide singleton runtime

```python
# anukriti-api/app/adapters.py
_runtime_lock = threading.Lock()
_runtime_instance: SwarmRuntime | None = None


def get_runtime() -> SwarmRuntime:
    """Return a process-wide SwarmRuntime; lazily warmed on first call."""
    global _runtime_instance
    if _runtime_instance is None:
        with _runtime_lock:
            if _runtime_instance is None:
                _runtime_instance = SwarmRuntime(event_stream=InMemoryEventStream())
    return _runtime_instance


def reset_runtime() -> None:
    """Test helper — drop the cached runtime so the next call rebuilds it."""
    global _runtime_instance
    with _runtime_lock:
        _runtime_instance = None
```

**Critical detail.** This is double-checked locking. The first
request to the api process triggers `_runtime_instance =
SwarmRuntime(...)` — which loads the KG, warms the retrievers,
imports pgx-core's `PhenotypeEngine` (which loads pinned JSON
tables), and registers all the agents. **Subsequent requests reuse
the same instance.** That's why the api's first request takes ~1-2
seconds (cold) but every subsequent request is sub-100ms.

`reset_runtime()` is a test helper. Production code does not call it.

---

## 7. The end-to-end request flow

For one clopidogrel + SAS clinical query coming from the frontend:

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. Frontend (anukriti_landing or Synthatrial)                       │
│                                                                      │
│    POST /runs   Authorization: Bearer ak_live_<...>                  │
│    {                                                                 │
│      "workflow": "clopidogrel", "population": "SAS",                │
│      "snps": [                                                       │
│        {"id": "rs4244285",  "genotype": "AA"},                      │
│        {"id": "rs12248560", "genotype": "CC"}                       │
│      ]                                                               │
│    }                                                                 │
└──────────────────────────────┬──────────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 2. anukriti-api  (FastAPI, port 8000)                               │
│                                                                      │
│    app/main.py:                                                      │
│      - APIKeyMiddleware authenticates the bearer token               │
│      - CORSMiddleware enforces the allowlist                         │
│                                                                      │
│    app/routers/runs.py:                                              │
│      - validates the request body                                    │
│      - delegates to adapters.py                                      │
└──────────────────────────────┬──────────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 3. adapters.call_diplotype("clopidogrel", snps)                     │
│                                                                      │
│    - WORKFLOW_TO_SCOPE["clopidogrel"] -> ("clopidogrel", "CYP2C19") │
│    - WORKFLOW_RSIDS check: rs4244285 present (required) ✓           │
│    - _build_variants_for_gene(snps, gene="CYP2C19")                 │
│      builds: {"rs4244285": VCFVariant(ref="G", alt="A",             │
│                                        genotype="1/1"),              │
│              "rs12248560": VCFVariant(ref="C", alt="T",             │
│                                        genotype="0/0")}              │
│    - CYP2C19Caller().call(variants)                                  │
│        ↓                                                             │
│      anukriti-pgx-core IN-PROCESS CALL                               │
│        ↓                                                             │
│      Layer 1: PharmVar TSV lookup → {"*2": 2}                        │
│      build_diplotype → "*2/*2"                                       │
│      Layer 2: PhenotypeEngine.infer("CYP2C19", "*2", "*2")           │
│         → CYP2C19_named_diplotypes_v2022.1.json["*2/*2"]            │
│         → "Poor Metabolizer"                                         │
│        ↓                                                             │
│      Diplotype(diplotype="*2/*2",                                    │
│                phenotype=PhenotypeInference("Poor Metabolizer",     │
│                                             confidence=1.0, ...),   │
│                pharmvar_table="CYP2C19_alleles_cpic_v2022.1",       │
│                phenotype_table="CYP2C19_named_diplotypes_v2022.1",  │
│                pgx_core_version="0.2.1")                             │
│                                                                      │
│    Total time: ~5-10ms (no I/O after engine warmed)                 │
└──────────────────────────────┬──────────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 4. adapters.to_swarm_context(req)                                   │
│                                                                      │
│    UnifiedExecutionContext.new(                                      │
│      drug="clopidogrel",                                             │
│      gene="CYP2C19",                                                 │
│      population="SAS",                                               │
│      genotype="*2/*2",                                               │
│    )                                                                 │
└──────────────────────────────┬──────────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 5. get_runtime().run(ctx)                                           │
│                                                                      │
│    SwarmRuntime singleton (warmed once at api startup) executes     │
│    the 5-stage pipeline IN-PROCESS:                                  │
│                                                                      │
│    Stage 1  orchestration                                            │
│      - GeminiOrchestrator decides which agents run                   │
│      - For (CYP2C19 + SAS + clopidogrel): pharmacogene specialist + │
│        evidence retriever + bias detector + sufficiency agent       │
│                                                                      │
│    Stage 2  retrieval                                                │
│      - DenseSemanticRetriever pulls CPIC PA166169660 + PMID:35034351│
│      - PopulationAwareRetriever attaches 1000G phase-3 frequencies  │
│      - Adaptive stopping fires when sufficiency budget is satisfied │
│                                                                      │
│    Stage 3  graph reasoning                                          │
│      - MultiHopReasoner BFS in the 37-node KG:                       │
│        CYP2C19 *2 → metabolizes → clopidogrel                        │
│        CYP2C19 *2 → higher_frequency_in → SAS (weight=0.36)         │
│      - Path bundle: 2 paths, max_hops=4                              │
│                                                                      │
│    Stage 4  sufficiency  ←  (the Evidence Sufficiency Layer)        │
│      - PharmacogeneAgent.reason(*2, *2):                             │
│           inference = infer_phenotype("CYP2C19", "*2", "*2")        │
│           ↓ (rules/phenotype_rules.py shim)                          │
│           anukriti_pgx_core.PhenotypeEngine.infer()                  │
│           ↓ "Poor Metabolizer" (confidence=1.0)                      │
│      - 6-facet coverage analysis:                                    │
│           ALLELE COVERED, PHENOTYPE COVERED, CPIC COVERED,           │
│           POPULATION COVERED, RECOMMENDATION COVERED,                │
│           CONFLICT_FREE COVERED                                      │
│      - SufficiencyDecisionEngine:                                    │
│           R12 fires → SUFFICIENT                                     │
│      - SetLevelEvidenceVerifier:                                     │
│           V10 fires → SUPPORTED                                      │
│      - UncertaintyScoringEngine:                                     │
│           U9 fires → LOW                                             │
│      - PopulationEvidenceBiasDetector:                               │
│           No bias detected (empty tuple)                             │
│      - CheckpointResult.may_synthesize = True                        │
│                                                                      │
│    Stage 5  synthesis                                                │
│      - Template engine renders deterministic explanation             │
│        (or optional LLM enrichment behind GenerativeBoundary)        │
│      - GenerativeBoundary verifies LLM didn't invent a phenotype    │
│        the engine didn't produce                                     │
│      - UnifiedExecutionReport assembled                              │
└──────────────────────────────┬──────────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 6. anukriti-api assembles the JSON response                         │
│                                                                      │
│    {                                                                 │
│      "diplotype": "*2/*2",                                           │
│      "phenotype": "Poor Metabolizer",                                │
│      "drug_action": "ALTERNATIVE_RECOMMENDED",                       │
│      "guidance_text": "Avoid clopidogrel. Use alternative...",       │
│      "sufficiency": {                                                │
│        "decision": "SUFFICIENT", "rule": "R12",                      │
│        "rationale": "R12: all facets covered, no conflict, ..."     │
│      },                                                              │
│      "verdict":     {"verdict": "SUPPORTED", "rule": "V10"},        │
│      "uncertainty": {"tier":    "LOW",       "rule": "U9"},         │
│      "provenance": {                                                  │
│        "pharmvar_table":   "CYP2C19_alleles_cpic_v2022.1",          │
│        "phenotype_table":  "CYP2C19_named_diplotypes_v2022.1",      │
│        "guideline_pmid":   "35034351",                               │
│        "pgx_core_version": "0.2.1",                                  │
│        "swarm_version":    "<git-rev>",                              │
│        "correlation_id":   "<uuid>"                                  │
│      }                                                                │
│    }                                                                 │
└──────────────────────────────┬──────────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 7. Frontend renders the answer                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Total elapsed time for a warm api process:** roughly **50-150ms**
end-to-end. The deterministic engine is microseconds; the swarm's
5 stages are the bulk; the api's overhead is negligible.

**Cold-start time** (first request after process boot): ~1-2
seconds, because `get_runtime()` triggers `SwarmRuntime(...)` which
loads the KG seed, warms retrievers, imports pgx-core (which loads
pinned JSON tables), and registers all 9 agents.

---

## 8. The Docker image story (`anukriti-stack`)

The integration claim "no HTTP between repos" is enforced at the
image-build level. From `anukriti-stack/Dockerfile.api`:

```dockerfile
# syntax=docker/dockerfile:1.7
# anukriti-api Dockerfile — built from the parent directory so both
# anukriti-api/ and anukriti-swarm/ are visible in the build context.
#
# This image fuses three sources behind one HTTP surface:
#
#   anukriti-pgx-core==0.2.1  (PyPI library, installed via requirements)
#   anukriti-swarm/           (copied into /opt/swarm and added to PYTHONPATH)
#   anukriti-api/             (copied into /opt/api and used as workdir)

# ---------- Stage 1: builder ----------
FROM python:3.12-slim-bookworm AS builder
# ...
# Install the swarm + api requirements into a single venv.
# Both pin anukriti-pgx-core==0.2.1 from PyPI.
COPY anukriti-swarm/requirements.txt /tmp/swarm-requirements.txt
COPY anukriti-api/requirements.txt   /tmp/api-requirements.txt

RUN pip install --no-cache-dir -r /tmp/swarm-requirements.txt \
                                 -r /tmp/api-requirements.txt

# ---------- Stage 2: runtime ----------
FROM python:3.12-slim-bookworm AS runtime
# ...
# Bring in the venv from the builder. No build tooling in runtime.
COPY --from=builder /opt/venv /opt/venv

# Copy both source trees (api + swarm).
COPY --chown=anukriti:anukriti anukriti-swarm /opt/swarm
COPY --chown=anukriti:anukriti anukriti-api   /opt/api

# Make the swarm package importable from anywhere via PYTHONPATH —
# this is how `from core.runtime import SwarmRuntime` resolves.
ENV PYTHONPATH="/opt/api:/opt/swarm"

WORKDIR /opt/api
USER anukriti
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

What this image actually contains at runtime:

```
/opt/venv/                  Python venv with:
                              anukriti-pgx-core==0.2.1 (from PyPI)
                              fastapi, pydantic, uvicorn (api deps)
                              pymongo, networkx, numpy (swarm deps)
                              ... all merged into one venv ...

/opt/api/                   anukriti-api source (workdir)
  app/
    main.py                 → uvicorn entry point
    adapters.py             → translates frontend shape ↔ platform shape
    routers/                → FastAPI routes
    auth.py, persistence.py, ...

/opt/swarm/                 anukriti-swarm source (importable via PYTHONPATH)
  core/                     → SwarmRuntime, agents, sufficiency layer
  rules/phenotype_rules.py  → the shim
  knowledge_graph/          → KG + reasoner
  observability/            → tracing
  ...

PYTHONPATH=/opt/api:/opt/swarm
```

When `app/main.py` boots, Python's import resolver finds:

- `from anukriti_pgx_core import ...` → resolved from `/opt/venv` (the installed PyPI library)
- `from core.runtime import SwarmRuntime` → resolved from `/opt/swarm` (the swarm source on PYTHONPATH)
- `from app.adapters import ...` → resolved from `/opt/api` (the api source, workdir)

All three resolutions are **in-process Python imports**. No HTTP.
No socket. No serialization. The api process *is* the swarm
process *is* the deterministic-engine process.

There is also a separate `swarm` service in the docker-compose
(running on port 8001) that exposes a direct FastAPI surface for
debugging and the WebSocket mission-control UI, but the **api
service does not communicate with it** — it has its own
`SwarmRuntime` singleton inside its own process.

---

## 9. What the swarm adds on top of the engine

The deterministic engine alone answers: *"For this diplotype, what
does CPIC say?"*

The swarm adds:

| Added by the swarm | What it does | Where it lives |
|---|---|---|
| **Multi-agent orchestration** | Different agents handle phenotype inference, evidence retrieval, conflict detection, narrative synthesis. Each agent is replaceable. | `agents/` (9 specialists), `core/orchestrator/coordinator.py` |
| **Evidence sufficiency gating** | Even if the engine produces a confident phenotype call, the swarm can refuse to deliver the recommendation when population evidence is thin (R5/R9), provenance is broken (R4), hard conflict is detected (R1), or eurocentric imbalance is flagged. | `core/evidence_sufficiency/` (see [`EVIDENCE_SUFFICIENCY_LAYER_DEEP_DIVE.md`](EVIDENCE_SUFFICIENCY_LAYER_DEEP_DIVE.md)) |
| **Generative narrative with hallucination boundary** | Once sufficiency clears, an LLM can render a more readable explanation. The `GenerativeBoundary` raises if the LLM tries to invent a phenotype the engine didn't produce, a recommendation override, a verification bypass, or a fabricated claim. | `core/orchestrator/boundary.py`, `narrative/` |
| **Knowledge-graph reasoning** | Bounded BFS over a 37-node, 34-edge pharmacogenomic KG (10 NodeKinds, 7 EdgeKinds). Population-aware traversal: path weights factor in `HIGHER_FREQUENCY_IN` edge weights. | `knowledge_graph/` |
| **Multi-strategy retrieval with adaptive stopping** | Dense semantic + population-aware + graph-based retrievers; ECR-style stopping controller. | `retrieval/` |
| **Observability + replay** | Every stage emits `RuntimeEvent`s. A run is fully replayable from MCP storage with the same inputs. | `observability/`, `integrations/mcp/` |
| **Evaluation framework** | 6 evaluation suites + 4 stress scenarios + 3 ancestry-conflict scenarios. | `evaluation/`, `benchmarks/` |
| **Interoperability layer** | Agent-to-agent message bus, shared biomedical context, scope firewall. | `interoperability/` |

In short: **the engine answers a single question deterministically.
The swarm answers a single question deterministically AND decides
whether the answer is safe to deliver, with a full audit trail.**

The two are designed to compose: the engine's answer is one input
the swarm reads; the swarm's decision is whether that answer reaches
the caller.

---

## 10. Migration note: when the shim can be deleted

The shim's docstring is explicit about its lifecycle:

> *"This module stays as a thin re-export so existing swarm-side
> consumers (agents/pharmacogene/base.py, core/verification/safety.py,
> core/runtime/runtime.py, tests, any future imports) don't need to
> change during the migration. **When swarm-side call sites all
> import from anukriti_pgx_core directly, this file can be deleted
> without touching any of them.**"*

Today, **5 swarm files** still import via the shim:

```bash
$ grep -rl "from rules.phenotype_rules" anukriti-swarm/ \
       --include='*.py' \
       | grep -v tests/ | grep -v __pycache__
anukriti-swarm/agents/pharmacogene/base.py
anukriti-swarm/core/verification/safety.py
anukriti-swarm/core/runtime/runtime.py
anukriti-swarm/knowledge_graph/seed.py
anukriti-swarm/benchmarks/adversarial.py
```

To remove the shim (a future session's work):

1. Replace `from rules.phenotype_rules import infer_phenotype, PhenotypeInference` with `from anukriti_pgx_core import PhenotypeEngine, PhenotypeInference` in each of the 5 files above.
2. Replace each `infer_phenotype(gene, a1, a2)` call with `_engine.infer(gene, a1, a2)` (where `_engine` is a module-level or class-level singleton).
3. Replace `from rules.phenotype_rules import ALLELE_ACTIVITY_SCORES` with `_engine.activity_scores_snapshot()`.
4. Run `pytest -q` — expect 244/244, byte-identical output.
5. Re-run all 7 byte-locked flagship demos — confirm signatures unchanged.
6. Delete `anukriti-swarm/rules/phenotype_rules.py`.
7. Delete the now-empty `anukriti-swarm/rules/` directory.

This is mechanical and low-risk. **It's not on the active roadmap
because the shim costs zero.** The migration would be done either
when:

- A `pgx-core` API change requires it (e.g. `PhenotypeEngine.infer`
  signature changes incompatibly).
- Cleanup discipline calls for it (the shim's docstring is
  semi-permanent technical debt that obscures the import topology).

The architecture spec `architecture/verification-safety.md` notes
the shim is intentional, not an oversight.

---

## 11. What this integration deliberately does NOT do

For honesty, here is the closed list of things the integration
**does not** do:

- **No HTTP boundary between pgx-core, swarm, and api.** Every call
  is in-process Python. Bandwidth, serialization, and timeout
  failure modes that exist in HTTP architectures don't exist here.

- **No microservice deployment for the engine.** The engine is a
  library. Each consumer (swarm process, api process, product
  process) has its own copy in its own venv, all pinned to the same
  version. There is no "engine service" to scale up or down
  independently.

- **No language portability of the engine.** It's Python. The
  pinned JSON tables are language-agnostic, but the engine's
  resolution logic is Python. A Rust or Go consumer would need to
  re-implement the rules — same JSON tables, different code.

- **No path dependencies.** The swarm and api **do not** depend on
  pgx-core via a path or git URL. They depend on a published PyPI
  version. This enforces the change-cadence discipline.

- **No git submodules.** The three repos are linked by a PyPI pin
  for pgx-core and a `PYTHONPATH` mount for swarm-source-into-api.
  Submodules would couple the repos in a way that breaks the
  change-cadence rationale.

- **No automatic version sync.** When pgx-core releases 0.3.0, the
  swarm and the api each need to bump their pin manually. This is
  intentional friction — a forced review point.

- **No engine override at runtime.** A deployment cannot swap the
  engine implementation via env var or YAML. Different engine
  versions are different binary artifacts (different `pip install`
  commands).

- **No shared mutable state between engine instances.** Each
  Python process has its own `_ENGINE = PhenotypeEngine()`
  singleton. Two api workers running in the same image would each
  load their own copy of the pinned JSON tables. There is no shared
  cache, no Redis, no shared memory. Per-process determinism is the
  invariant.

- **No async/await in the engine.** `PhenotypeEngine.infer()` is a
  synchronous Python function. The swarm's async work (retrieval,
  KG reasoning) wraps it in async contexts but never makes the
  engine itself async.

- **No retry, no circuit breaker, no rate limit on engine calls.**
  Engine calls don't fail (other than `UnsupportedGeneError` and
  `UnknownAlleleError`, which are deterministic given the input and
  pinned tables). Retry semantics don't apply to in-process function
  calls.

---

## Appendix — file map for this deep-dive

| Concept | File |
|---|---|
| Library public surface | `anukriti-pgx-core/anukriti_pgx_core/__init__.py` |
| Library version pin (swarm side) | `anukriti-swarm/requirements.txt` |
| Library version pin (api side) | `anukriti-api/requirements.txt` |
| Library version pin (product side) | `anukriti/requirements.txt` |
| The shim | `anukriti-swarm/rules/phenotype_rules.py` |
| Shim consumer 1 | `anukriti-swarm/agents/pharmacogene/base.py:24,77` |
| Shim consumer 2 | `anukriti-swarm/core/verification/safety.py` |
| Shim consumer 3 | `anukriti-swarm/core/runtime/runtime.py` |
| Shim consumer 4 | `anukriti-swarm/knowledge_graph/seed.py` |
| Shim consumer 5 | `anukriti-swarm/benchmarks/adversarial.py` |
| api gateway entry | `anukriti-api/app/main.py` |
| api ↔ swarm + api ↔ pgx-core adapter | `anukriti-api/app/adapters.py` |
| api workflow→scope table | `anukriti-api/app/adapters.py:36-41` (WORKFLOW_TO_SCOPE) |
| api workflow→rsIDs table | `anukriti-api/app/adapters.py:WORKFLOW_RSIDS` |
| Singleton SwarmRuntime helper | `anukriti-api/app/adapters.py:get_runtime` |
| Stack image (api + swarm fused) | `anukriti-stack/Dockerfile.api` |
| Stack docker-compose orchestration | `anukriti-stack/docker-compose.yml` |
| Stack auth bootstrap | `anukriti-stack/bootstrap.sh` |
| Engine layer-by-layer trace | [`DETERMINISTIC_ENGINE_DEEP_DIVE.md`](DETERMINISTIC_ENGINE_DEEP_DIVE.md) |
| Sufficiency rule tables | [`EVIDENCE_SUFFICIENCY_LAYER_DEEP_DIVE.md`](EVIDENCE_SUFFICIENCY_LAYER_DEEP_DIVE.md) |
| Friendly intro to the three repos | [`docs/02-the-three-repos.md`](docs/02-the-three-repos.md) |
| Friendly intro to the request flow | [`docs/10-how-the-pieces-talk.md`](docs/10-how-the-pieces-talk.md) |

---

## Cross-references

- [`DETERMINISTIC_ENGINE_DEEP_DIVE.md`](DETERMINISTIC_ENGINE_DEEP_DIVE.md) — what each library call computes
- [`EVIDENCE_SUFFICIENCY_LAYER_DEEP_DIVE.md`](EVIDENCE_SUFFICIENCY_LAYER_DEEP_DIVE.md) — how the swarm wraps the engine in safety gates
- [`IDEA_REFINEMENT_AND_PHASING_2026-05-14.md`](IDEA_REFINEMENT_AND_PHASING_2026-05-14.md) — Phase B will add new gene callers to pgx-core (BCHE for the Vysya wedge); this integration story doesn't change because the closed-enum + PyPI-pinned discipline absorbs it
- [`SESSION_RESUME_2026-05-16.md`](SESSION_RESUME_2026-05-16.md) — most recent session state, including the `anukriti-stack` first push
- [`founder-research/andrea_gaedigk/`](founder-research/andrea_gaedigk/) — Phase-C scientific outreach planning the PharmVar API integration that will land in `anukriti_pgx_core/registries/`

---

*This document was written 2026-05-16 as a permanent record of how
the three repos are wired together at the import level. Derived
directly from the source files cited in the appendix. If a future
session changes the integration shape (new repos, new HTTP
boundaries, new path dependencies, new shim layers), update this
document in the same commit that lands the change — divergence
between this doc and the code is a documentation regression, not
just a stale doc.*
