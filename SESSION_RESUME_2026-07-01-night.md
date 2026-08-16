# Session Resume — 2026-07-01 (night)

> Captured 2026-07-01 ~22:39 IST. Successor to the 2026-07-01 (later)
> "CPIC gene-drug panel" entry already in `docs/10-development-log.md`.
> Resume with: "continue project_astra from SESSION_RESUME_2026-07-01-night.md".

This file is the single thing to read to pick back up tomorrow. Everything in
it is verified against real command output tonight, not recalled from memory.

---

## TL;DR

| # | Workstream | Result |
|---|---|---|
| 1 | Real-World Evidence Corroboration Engine | `reason/corroboration.py` — checks graph vs. FAERS-shaped signals |
| 2 | Evidence Accumulation Trajectory Engine | `reason/accumulation.py` — first engine to read `GraphStore.history()` |
| 3 | Fragility + Trajectory → Promotion composition | `promote/candidates.py` extended, zero new cross-module imports |
| 4 | FAERS bulk acquisition | **owned by a separate, parallel session** — still in flight, do not touch |

**Tests: 182 passed, 0 failed** (verified via `python -m pytest` moments ago).
**Lint: `ruff check astra tests scripts` — all checks passed.**
**Git: working tree clean except `faers_discovery/` (untracked, not ours — see below). All commits pushed to `origin/main`.**

---

## What shipped tonight (in order)

### 1. Real-World Evidence Corroboration Engine — commit `549fd9f`

`astra/reason/corroboration.py` — ASTRA's fifth reasoning engine, and the
first that checks the graph against something **outside** the literature
corpus. Takes a `RealWorldSignal` (drug, reaction, case count, PRR — the
standard FAERS-shaped disproportionality-analysis convention) and cross-checks
it against the graph's own `CAUSES`/`CORRELATES` edges:

- **Corroboration** — signal agrees with an existing literature edge.
- **Divergence** — two named kinds: `UNEXPECTED_REAL_WORLD_SIGNAL` (a real
  signal with no literature claim at all) or
  `LITERATURE_CLAIM_UNSUPPORTED_BY_REAL_WORLD_DATA` (literature claims it,
  real-world surveillance doesn't show it at a checkable volume).
- **RefusedSignal** — below case-volume/PRR thresholds, refused outright,
  never silently treated as either agreeing or disagreeing.

**Zero import coupling to `faers_discovery/`** by design — takes a plain
`list[RealWorldSignal]`, works with illustrative examples today, will work
unchanged with real FAERS data once that pipeline delivers.

Real corpus verification: `SLCO1B1 --causes--> simvastatin` (myopathy, OR 4.5)
corroborates against a plausible real-world signal; `DPYD --causes-->
fluorouracil` (severe toxicity, HR 2.8) demonstrates the honest
"unsupported by real-world data" divergence path.

**A real bug caught by real-corpus testing, not synthetic fixtures**: first
draft matched reaction text against the wrong field (`edge.target_id_node`
instead of `edge.condition_context`). The real-corpus test failed
immediately and exposed it — fixed before commit.

Wired into `scripts/discover.py` via a new `--signals <path>` flag (off by
default).

### 2. Evidence Accumulation Trajectory Engine — commit `ca9b3a5`

`astra/reason/accumulation.py` — the sixth engine, and the first to read
`GraphStore.history()` — a non-destructive, append-only sequence of every
confidence value an edge has ever had, built into storage since Phase 0 and
never once read by any `reason/` module until tonight.

Classifies each edge's real confidence-accumulation history into a closed
`TrajectoryShape`: `SINGLE_STEP`, `INSUFFICIENT_HISTORY`, `CONVERGING`
(deltas shrinking, healthy), `ACCELERATING` (latest delta bigger than the
last — a disproportionately strong new source just landed), `STALLED`
(evidence landing without moving confidence).

**Important design correction made before writing any scoring logic**:
first instinct was time-based velocity (confidence change per unit wall-clock
time). Checked against the real graph first — every edge in a single-batch
ingest has history rows separated by milliseconds, so wall-clock velocity
would be meaningless noise. Reframed to **step-based** trajectory (per
evidence-addition, not per unit time) — real, available today, doesn't need
elapsed time at all.

**Real finding on the first real run**: `CYP2D6 --encodes--> CYP2D6(enzyme)`
— the single most-cited edge in the whole graph (7 CPIC guideline sources) —
classifies **STALLED**. Its 7th citation moved confidence by 0.0028, an order
of magnitude below the 6th's 0.0043. The edge that looks most "established"
from any snapshot view is, by its own accumulation curve, long past the point
where more citations add statistical confidence rather than just structural
corroboration. No snapshot-based engine (i.e. every other engine) could have
found this.

Wired into `scripts/discover.py` automatically (no flag needed, runs
alongside fragility/promotion).

### 3. Composition: fragility + trajectory → promotion review — commit `bbc5f65`

Rather than build a seventh standalone engine, composed two existing ones.
`astra/promote/candidates.py`'s `PromotionCandidate` gained an optional
`trajectory_shape` field, threaded through `build_promotion_candidates()`
exactly the way `fragility_index` already was — **zero new imports** between
`promote/`, `reason/fragility.py`, and `reason/accumulation.py`; composition
happens only in the caller (`scripts/discover.py`), per this module's own
established discipline.

**Real composed output** (`scripts/discover.py --cpic`): the graph's one
actual promotion candidate today, `CYP2D6 --metabolizes--> Codeine`, now
reports `confidence=0.851 fragility_index=1 trajectory=single_step` on one
line — a reviewer sees single-source + one-step-from-DISPUTED +
never-corroborated-by-a-second-source together, instead of cross-referencing
three separate report sections.

---

## Full engine roster (6 total, all in `astra/reason/` + 1 in `astra/promote/`)

| Engine | File | Question it answers |
|---|---|---|
| Contradiction | `reason/contradiction.py` | What disagrees (same entities/relation, opposite polarity, context-disambiguated)? |
| Gaps | `reason/gaps.py` | What's missing (2-hop A→B→C with no direct A→C)? |
| Convergence | `reason/convergence.py` | What combines (multiple quantified effect sizes on the same outcome)? |
| Fragility | `reason/fragility.py` | How much should we trust what we have (min sources to flip to DISPUTED)? |
| **Corroboration** (new tonight) | `reason/corroboration.py` | Does the real world agree with the literature? |
| **Accumulation** (new tonight) | `reason/accumulation.py` | What's the *shape* of the confidence curve, not just its current value? |
| Promotion | `promote/candidates.py` | Which findings have a defined path into the curated swarm graph? (composes fragility + accumulation as of tonight) |

All are pure, deterministic, read-only, LLM-free, network-free — matching the
"deterministic layer first" discipline the whole platform holds.

---

## faers_discovery/ — NOT MINE, DO NOT TOUCH WITHOUT CHECKING

`project_astra/faers_discovery/` is **owned by a separate, parallel agent
session**, explicitly told to me: *"the gcp world is being run separate agent
chat."* I have not written, edited, or committed anything in it, and neither
should tomorrow's session without first confirming its state with whoever is
running that side.

**State as of 22:38 IST tonight:**
- Real `fetch_faers.py` runs on a **remote GCP VM**
  (`anukriti-genomics-vm-mumbai`, zone `asia-south1-a`).
- Downloading openFDA FAERS adverse-event data: 1211 partitions since 2016,
  ~83GB total, filtering to 6 target drugs (paracetamol, metformin,
  ibuprofen, aspirin, atorvastatin, omeprazole).
- Results are periodically `scp`'d back from the VM into
  `faers_discovery/data/raw/*.jsonl` via an IAP tunnel.
- **3 of 6 drug files landed so far** (aspirin ~1.06GB, atorvastatin ~1.02GB,
  ibuprofen ~1.33GB and still growing as of the last check). paracetamol,
  metformin, omeprazole not yet present.
- Log (`faers_discovery/logs/fetch_faers.log`) was still showing partition
  ~39/1211 as of the last read — this is a **long-running job**, likely still
  far from done tomorrow morning too.

**When it's ready**: `reason/corroboration.py`'s `RealWorldSignal` is the
target shape to convert real FAERS case data into (drug, reaction, case
count, a PRR-style disproportionality statistic). That conversion is a small
adapter script, not a change to the corroboration engine itself. Do not
build that adapter blind — check the other session's actual output schema
first once the files are complete.

---

## What's next (priority order, my own recommendation from tonight)

1. **Still the actual bottleneck, unchanged across every session today: the
   Phase-0 human review gate (`docs/11-phase0-closeout.md`) has never been
   exercised.** Six reasoning engines (plus composition) now exist, all
   verified against a 20-paper corpus no domain expert has signed off on.
   This is an hour of human time, not more engineering — walk
   `scripts/inspect_graph.py`'s output against the checklist in that doc and
   record a decision in its "Review outcome" table. Everything downstream
   (Phase 1 live ingestion, in particular) is blocked on this, not on more
   code.
2. **Cross-engine consistency audit** (the idea I was mid-pitch on when this
   session ended): six engines were each verified against the real corpus in
   isolation tonight, but nobody has checked whether their *outputs* are
   mutually consistent — e.g. does an edge fragility calls robust ever get
   contradicted by convergence math, does a gap-engine's top-ranked gap rest
   on an edge accumulation already flagged STALLED? This is a legitimate new
   angle (self-critique across engines, not within one), not yet started.
3. **FAERS adapter** — blocked on the other session's pipeline completing;
   check its state first before writing anything.
4. **Outside project_astra, still open from earlier today** (per the
   SynthaTrial-repo-wide context, not this repo specifically): HF token
   rotation (flagged HIGH priority 2026-06-18, still unconfirmed done) and
   the CYP2C9 classifier's pre-push checklist in the `anukriti` repo
   (`clinical-grade-pgx` branch, 3 unpushed commits as of the last read).

---

## How to resume (verified commands)

```bash
cd project_astra

# Confirm clean state + test count
git log --oneline -8
git status --short              # should show only faers_discovery/ untracked
python -m pytest -q             # 182 passed
ruff check astra tests scripts  # All checks passed!

# See the real composed output (confidence + fragility + trajectory)
python scripts/discover.py --cpic
rm -f data/discovery/report_*.json   # generated reports are gitignored, clean up after inspecting

# Read the full detailed record of tonight's 3 entries (newest first):
head -240 docs/10-development-log.md
```

---

## Canonical doc links

- `docs/10-development-log.md` — the full, detailed record (what/why/decisions/
  tests/next) for every entry referenced above, in reverse-chronological order.
- `docs/11-phase0-closeout.md` — the human review checklist that is still the
  actual bottleneck (see "What's next" #1).
- `docs/06-anukriti-integration.md` — the firewall + promotion-contract doc
  `promote/candidates.py` implements.
- `docs/00-context.md` / `docs/01-architecture.md` — vision + the 10-layer
  architecture, for orienting any new engine idea against what's already
  specified vs. what would be new scope.
