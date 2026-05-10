# Module 06 — Why Deterministic

> Prerequisites: [04 Architecture](04-architecture.md), [05 Gene Matching](05-gene-matching.md)

---

## The question we're answering

Why go to such lengths to keep the medical decision layer
deterministic? An LLM knows CPIC guidelines — why not just ask it?
What exactly would go wrong, and how does the platform prevent it?

---

## The problem with asking an LLM

Put this prompt to any modern LLM:

> "A patient with CYP2C19 *2/*2 genotype is being considered for
> clopidogrel. What should the clinician do?"

You'll get a well-worded response that usually includes:
- The correct phenotype (Poor Metabolizer)
- The correct recommendation (avoid clopidogrel)
- A plausible-sounding explanation
- Possibly a citation (which may or may not exist)

Most of the time, the LLM will be right. **The problem is the tail
of the distribution.** Some fraction of the time — maybe 1%, maybe
5%, maybe 0.1% depending on the model and the phrasing — the LLM
will:

1. Invert the recommendation ("clopidogrel is preferred for PMs")
2. Cite a study that doesn't exist (hallucinated PMID)
3. Use an outdated guideline (CPIC has updated since training cutoff)
4. Mix up the gene's role (treat clopidogrel like a non-prodrug)
5. Generate a subtle off-by-one in the dose recommendation

For a non-medical question, a 99% right rate is fantastic. For a
medical recommendation that could affect a real patient's cardiac
outcome, **a 99% right rate means 1% of patients harmed.**

And the 1% isn't evenly distributed. Population-adjacent queries
(where the LLM has less training data) fail more. Edge cases
(rare variants, uncommon drugs) fail more. The tail risk is real
and concentrated on exactly the cases where getting it right
matters most.

---

## The deterministic alternative

Replace "ask the LLM" with "look up the answer in a pinned,
versioned table":

```python
# Pseudocode — what pgx-core actually does
def recommend(gene: str, diplotype: str, drug: str) -> Recommendation:
    phenotype = infer_phenotype(gene, diplotype)     # pinned CPIC table
    guideline = load_guideline(gene, drug)           # pinned JSON
    return guideline.lookup(phenotype)                # deterministic dict access
```

This function is:

- **Deterministic.** Same inputs produce the same output. Forever.
- **Traceable.** The JSON file has a version number in its filename
  (`CYP2C19_named_diplotypes_v2022.1.json`). You can ask "what
  guideline produced this recommendation?" and get an exact
  citation.
- **Auditable.** The guideline text is in the repo. You can read it.
  You can diff it against CPIC's official publication.
- **Reviewable.** A PR that changes the guideline is a visible diff.
  A reviewer can compare old vs. new and sign off (or not).

The cost is that **the library doesn't "know" anything about
clopidogrel beyond what's in the pinned table**. You can't ask it a
novel question. That's a feature, not a bug — novel questions are
where LLMs hallucinate.

---

## What the library enforces

`anukriti-pgx-core` has four hard invariants at the code level:

### 1. Zero runtime dependencies

Open `anukriti-pgx-core/pyproject.toml` — the `[project].dependencies`
list is empty. The library uses only the Python standard library.

Why this matters: no third-party package can introduce an LLM call,
a network request, or non-deterministic behavior through a
transitive dependency. The dependency graph is one node.

### 2. No randomness, no clock, no entropy

Search the codebase for `random`, `secrets`, `time.time()`,
`datetime.now()`, `uuid.uuid4()`. These appear nowhere in the
biomedical call paths. A phenotype inference that depends on the
clock is a bug.

Why this matters: determinism means reproducibility. If you run the
same diplotype through the engine in 2024 and again in 2028, you
get the same result (assuming the same pinned table version).
Audit trails work because the past is retrievable.

### 3. No network I/O

No `requests`, no `httpx`, no `urllib.request` in the biomedical
paths. The library never reaches out. All CPIC tables are checked
into the repo.

Why this matters: offline operation. Reproducibility when external
services are down. No data exfiltration risk. No surprises from a
CPIC website change.

### 4. Closed-enum return types

The phenotype strings are a closed set: `{PM, IM, NM, RM, UM}`.
Adding a new phenotype category requires modifying the enum, which
is a PR. An engine run can't produce "Possible Intermediate
Metabolizer" or "Likely Rapid" or some LLM-like softening.

Why this matters: downstream consumers (anukriti, anukriti-swarm)
can have exhaustive `match` statements over phenotype outcomes.
The compiler/type checker catches missing cases at review time, not
runtime.

---

## CPIC table versioning — the pinning discipline

Every CPIC table in the library has a version-suffixed filename:

```
anukriti_pgx_core/phenotype/tables/
├── CYP2C19_named_diplotypes_v2022.1.json
├── CYP2D6_activity_table_v2019_CPIC.json
├── CYP2D6_named_diplotypes_v2019.json
├── ...
```

When CPIC releases a new version of a guideline, the workflow is:

1. **Add the new file** (`CYP2C19_named_diplotypes_v2024.1.json`),
   not replace the old one.
2. **Point the engine at the new file** via an explicit constant
   in `phenotype/engine.py`.
3. **Run the regression gate.** Do any of the 12 pinned star-allele
   cases change? Do any of the 51 pgx-core tests fail? Do the
   1961-byte demo outputs drift?
4. **If yes:** document the change in `CHANGELOG.md` with the CPIC
   publication URL and date. The change becomes a deliberate minor
   version bump (e.g. 0.2.1 → 0.3.0).
5. **If no (byte-identical):** patch version bump, changelog entry
   says "no behavioral change."

The old file stays in the tree. Why? Because a downstream consumer
pinned to a specific pgx-core version expects the *specific*
guideline behavior. If they upgrade, they review. If they don't
upgrade, their reproducibility is protected.

Every table also has an entry in `CPIC_PROVENANCE.json` with:

- `source_url` — the CPIC publication URL
- `publication_date` — when CPIC published it
- `audit_status` — `authoritative` / `verified` / `needs_audit` /
  `deprecated`
- `audit_date` — when a human last checked this table against CPIC
- `audited_by` — who checked it
- `divergences` — any documented cases where the library doesn't
  mirror CPIC exactly (rare; always justified)

---

## The regression contract, again

From Module 02, but here's why it's in *this* module:

Byte-identical regression testing is **how we operationalize
determinism**. If a code change — any code change, even one
that "shouldn't" affect phenotype output — causes a single byte
of downstream drift, we know something changed.

The regression gate runs:

- pgx-core pytest: 51/51 green
- anukriti biomedical tests: 353/1 (1 unrelated)
- swarm `test_star_allele_regression`: 12/12 + benchmark AGREE
- swarm showcase demo: JSON export exactly 1961 bytes
- swarm safety demo: 1 delivered / 4 blocked
- swarm interoperability demo: 24 envelopes / 24 provenance / 6 rejected
- swarm evaluation demo: 52/61 suite / 4/4 stress / 3/3 ancestry

If any signature drifts, the PR doesn't merge without discussion.
This is the structural analog of "no flaky tests allowed" for a
biomedical truth layer.

---

## What about the LLM we DO use?

Pure-deterministic has its limits. Two places the platform still
uses an LLM:

### 1. Narrative synthesis (the explanation)

After the deterministic layer has decided "PM, avoid clopidogrel,
use prasugrel, Strong / High," an LLM writes the readable paragraph
that explains this to a clinician or patient.

The LLM is constrained:
- It operates on the *structured output* of the deterministic layer.
- It cannot invent new facts — if it tries, the `GenerativeBoundary`
  raises.
- It cites the same citations the deterministic layer produced.
- A verification pass checks that every factual claim in the
  narrative traces back to a structured input.

This is safe because the LLM is *paraphrasing*, not *deciding*.

### 2. Orchestration planning (what agents to activate)

The planner uses an LLM to decide "for this query, which agents
should I activate, in what order?" If the LLM is unavailable or
returns malformed output, a deterministic fallback planner takes
over.

The worst an LLM mistake can do here is run more agents than
necessary (inefficient but safe) or skip an agent (which downstream
verification catches — a missing retrieval result doesn't pass
sufficiency).

Neither of these uses lets the LLM make a medical claim. Both are
guarded by deterministic checks downstream.

---

## Closed enums as a scope firewall

This was introduced in Module 04; here's why it's a *deterministic*
safety mechanism, not just a typing one.

Consider a hypothetical RAG system where context types are strings:

```python
# A contributor adds a new context type to support a feature
context_type = "general_healthcare_question"
```

At runtime, the agent receives this and routes it to... whatever
agent has the longest matching string similarity. Maybe a
pharmacogene agent because "healthcare" is in its description.
That agent produces an answer outside its competence. The answer
gets emitted. Nobody noticed.

Now consider the closed-enum version:

```python
class BiomedicalContextType(Enum):
    POPULATION = "population"
    GENOTYPE = "genotype"
    ... (7 values, enumerated)

context_type = "general_healthcare_question"  # TypeError at construction
```

The new "general" context type doesn't match the enum. Pydantic
raises. The code doesn't deploy. A human notices.

**The closed enum is a deterministic rejection mechanism for
out-of-scope inputs.** It's not about typing for typing's sake —
it's about making scope drift a compile-time / review-time event,
not a runtime event.

There are 14 such closed enums in the evidence sufficiency layer
alone (Module 09 enumerates them). Together, they form a type-level
scope firewall that a contributor cannot accidentally punch a hole
in — every hole requires a visible enum modification.

---

## Summary

You now know:

- **The LLM tail risk** is what deterministic layers exist to avoid.
- **pgx-core has four hard invariants:** zero deps, no randomness,
  no network I/O, closed-enum returns. Each is a deliberate safety
  property.
- **CPIC tables are pinned by version in filenames.** Old versions
  stay in the tree for reproducibility. Changes are explicit.
- **Byte-identical regression testing** is how we detect unintended
  behavior drift across the three repos.
- **LLMs are still used** — but only for narrative paraphrasing and
  orchestration planning, both guarded by deterministic verification.
- **Closed enums** are a scope firewall that rejects out-of-scope
  inputs at construction time, not runtime.

Next: [Module 07 — Tech Stack](07-tech-stack.md). We go through
every technology choice and the reasoning behind it.
