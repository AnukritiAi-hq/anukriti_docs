# Module 12 — Glossary

> A reference of terms used throughout these docs. Alphabetical.

---

## A

### activity score
A numeric per-allele value (typically 0.0 for loss-of-function, 1.0
for reference, 1.5 for gain-of-function) that sums across the two
alleles of a diplotype. The sum maps to a phenotype bin under the
"additive" inference path. See [Module 03](03-core-concepts.md).

### ADR (Architecture Decision Record)
A short document capturing a non-obvious architectural decision,
its alternatives, consequences, and a "Revisit when" trigger. The
platform's ADRs live in `anukriti-pgx-core/docs/adr/`.

### AFR
Super-population code: African ancestry. One of 5 values in the
`SuperPopulation` closed enum.

### allele
A specific version of a gene — the sequence a particular copy
carries. Pharmacogenomics uses "star alleles" (e.g. `*1`, `*2`,
`*17`) as a naming convention. Each person has two alleles per gene,
one from each parent.

### AMR
Super-population code: Admixed American (Latino) ancestry.

### ancestry
The population of origin a person traces their genome to.
Operationalized in the platform as a 5-value `SuperPopulation` enum
(EUR, EAS, SAS, AFR, AMR). Sub-populations exist as a future
extension point but are not seeded today.

### anukriti
The product repo — a FastAPI application producing clinical
pharmacogenomics reports. Consumes `anukriti-pgx-core` via PyPI pin.

### anukriti-pgx-core
The library repo — the deterministic biomedical truth layer,
published on PyPI.

### anukriti-swarm
The research-platform repo — multi-agent runtime, knowledge graph,
live mission-control UI.

---

## B

### bias (BiasKind)
One of 3 named patterns the platform detects: Eurocentric imbalance,
ancestry scarcity, unsupported extrapolation. Each has a concrete
numeric threshold. See [Module 08](08-population-awareness.md).

### byte-identical regression
The testing discipline where downstream outputs are pinned to exact
byte counts (e.g. "JSON export: 1961 bytes") to detect any silent
behavior drift. See [Module 06](06-why-deterministic.md).

---

## C

### clopidogrel
An antiplatelet drug used in cardiovascular secondary prevention.
Its metabolism is affected by CYP2C19 variants. The canonical
"population-blind prescribing fails patients" example in these
docs.

### closed enum
A Python Enum with a fixed, enumerated set of values. Extending the
set requires code modification. Used platform-wide as a scope
firewall — cross-module contracts never accept free-form strings.
See [Module 06](06-why-deterministic.md).

### ConflictKind
A closed 3-value enum for evidence conflicts:
`PHENOTYPE_DIVERGENCE`, `RECOMMENDATION_DIVERGENCE`,
`POPULATION_DIVERGENCE`. See [Module 09](09-evidence-and-safety.md).

### ConflictSeverity
A closed 2-value enum: `HARD`, `SOFT`. Hard conflicts block; soft
conflicts trigger caveats.

### correlation_id
A unique identifier attached to every run. Propagates through every
event, every persisted record, every envelope. Used for replay and
auditing.

### CPIC (Clinical Pharmacogenetics Implementation Consortium)
The clinical authority whose pharmacogenomics guidelines the
platform pins. Tables are versioned by filename (e.g.
`CYP2C19_named_diplotypes_v2022.1.json`). See [Module 03](03-core-concepts.md)
and [Module 06](06-why-deterministic.md).

### CPIC_PROVENANCE.json
The manifest in pgx-core listing every CPIC table with its source
URL, publication date, audit status, and any documented divergences.

### CYP (Cytochrome P450)
A family of enzymes that metabolize drugs. The platform covers
several CYP genes (CYP2D6, CYP2C19, CYP2C9, CYP3A4, CYP3A5, CYP1A2,
CYP2B6).

---

## D

### D3
A JavaScript visualization library, version 7.9.0, vendored as a
single file in the swarm frontend. Used only for the force-directed
knowledge-graph visualization.

### diplotype
The pair of star alleles a person has for a given gene. Written as
`*A/*B` in numeric-suffix order (e.g. `*2/*17`). Input to the
PhenotypeEngine.

### drug response
The clinical outcome of taking a drug — efficacy, adverse reactions,
required dose adjustments. Pharmacogenomics predicts variation in
drug response from genetic variation.

---

## E

### EAS
Super-population code: East Asian ancestry.

### EdgeKind
The 7-value closed enum for knowledge-graph edge types:
METABOLIZES, CONTRAINDICATED_FOR, ASSOCIATED_WITH,
HIGHER_FREQUENCY_IN, SUPPORTED_BY, CONFLICTS_WITH,
GUIDELINE_RECOMMENDS. See [Module 08](08-population-awareness.md).

### envelope (AgentContextEnvelope)
The frozen 7-field record agents exchange on the message bus.
Carries a closed-enum context type for scope enforcement. See
[Module 10](10-how-the-pieces-talk.md).

### EUR
Super-population code: European ancestry.

### EvidenceSufficiencyTrace
The frozen 7-dimension audit record every sufficiency evaluation
produces. Replayable. See [Module 09](09-evidence-and-safety.md).

### EvidenceVerdict
The closed 5-value enum for set-level verdicts: SUPPORTED, REFUTED,
INSUFFICIENT, CONFLICTING, UNCERTAIN. Produced by the 10-rule
SetLevelEvidenceVerifier.

---

## F

### facet (ClaimEvidenceFacet)
One of 6 closed-enum evidence dimensions checked by the sufficiency
layer: ALLELE, PHENOTYPE, CPIC, POPULATION, RECOMMENDATION,
CONFLICT_FREE. Each has a FacetCoverageState.

### FacetCoverageState
Closed 3-value enum: COVERED, UNCERTAIN, MISSING.

### FastAPI
The HTTP framework for the swarm backend. Paired with Pydantic for
request/response validation.

### frozen (as in frozen dataclass / frozen Pydantic record)
A record whose fields cannot be modified after construction.
Updates produce a new record instance. Required for
replay-safety and audit invariance.

---

## G

### gene
A stretch of DNA coding for a protein. Humans have about 20,000.
Pharmacogenes are the subset whose variants have documented
clinical effect on drug response.

### GeneCaller
The abstract base class in pgx-core for star-allele gene callers
(CYP family genes). Input: VCF variant map. Output: Diplotype.

### GenerativeBoundary
The runtime enforcement mechanism around LLM outputs. Raises a
`BoundaryViolation` exception if an LLM tries to infer phenotype,
override recommendation, bypass verification, or fabricate a claim.
See [Module 04](04-architecture.md).

### GenotypeCaller
The abstract base class in pgx-core for single-rsID callers (VKORC1,
SLCO1B1). Used for genes not defined by star alleles.

---

## H

### hallucination
An LLM generating plausible-sounding but incorrect content — e.g.
inventing a citation, misremembering a recommendation, or asserting
a gene-drug relationship that doesn't exist. The platform's core
design goal is to prevent hallucinations from reaching users.

---

## I

### IM (Intermediate Metabolizer)
One of 5 phenotype categories. Reduced enzyme activity.

### InMemoryBackend
The fallback MCP backend that writes records to in-process memory.
Used when `MONGODB_URI` is unset. See [Module 10](10-how-the-pieces-talk.md).

---

## K

### knowledge graph (KG)
The pharmacogenomic KG in swarm — 37 nodes, 34 edges, 10 closed
NodeKinds, 7 closed EdgeKinds. Traversed by the MultiHopReasoner
during retrieval. See [Module 08](08-population-awareness.md).

---

## L

### LLM (Large Language Model)
The platform uses LLMs only for narrative synthesis (Stage 5) and
orchestration planning (Stage 2). Both guarded by the
GenerativeBoundary. See [Module 04](04-architecture.md).

---

## M

### MCP (Model Context Protocol)
The persistence layer in swarm. 6 services, 31 tools, backed by
MongoDB or in-memory. See [Module 10](10-how-the-pieces-talk.md).

### MongoDB
The document database the MCP layer uses for persistence. Optional;
in-memory fallback works without it.

### MultiHopReasoner
The bounded-BFS traversal engine over the KG. Population-aware
(traverses HIGHER_FREQUENCY_IN edges), conflict-aware (skips
CONFLICTS_WITH edges), max-hop-limited. See [Module 08](08-population-awareness.md).

---

## N

### named-diplotype lookup
The phenotype-inference path that consults an explicit CPIC table
entry for a specific diplotype (e.g. "*2/*17 → IM"). Wins over
additive-score calculation when present. See [Module 05](05-gene-matching.md).

### NM (Normal Metabolizer)
One of 5 phenotype categories. Typical enzyme activity.

### NodeKind
The 10-value closed enum for knowledge-graph node types: POPULATION,
ANCESTRY, GENE, VARIANT, ALLELE, PHENOTYPE, DRUG, ADVERSE_REACTION,
GUIDELINE, EVIDENCE_PAPER.

---

## P

### PharmVar
The canonical external registry for pharmacogene star-allele
definitions. https://pharmvar.org.

### phenotype
A categorical label for enzyme activity: PM, IM, NM, RM, UM.
Produced by the PhenotypeEngine from a diplotype.

### PhenotypeEngine
The pgx-core class that translates diplotypes to phenotypes.
Deterministic, CPIC-pinned, no LLM, no randomness. See [Module 05](05-gene-matching.md).

### pgx-core
Short for `anukriti-pgx-core`, the library repo.

### pharmacogene
A gene whose variants affect drug response in a clinically
documented way. The platform covers 13 today.

### pharmacogenomics (PGx)
The discipline studying variation in drug response as a function of
genetic variation.

### PM (Poor Metabolizer)
One of 5 phenotype categories. Very low enzyme activity.

### population
See super-population.

### provenance
The chain of sources and attributions backing a claim. Propagated
through the platform as `ProvenanceStamp` records on every envelope.
See [Module 10](10-how-the-pieces-talk.md).

### Pydantic
The Python data-validation library used for all cross-module
contracts in swarm. Version 2.

---

## R

### regression contract
The commitment that pgx-core changes preserve byte-identical
downstream outputs. Documented targets include specific byte counts
for demo JSON exports. See [Module 02](02-the-three-repos.md).

### RM (Rapid Metabolizer)
One of 5 phenotype categories. Increased enzyme activity.

### rsID
A stable identifier for a SNP (e.g. `rs4244285`) issued by dbSNP.

### ruff
The Python linter/formatter. Adopted progressively via the
"strangler-fig" hard-gate promotion model — directories get
hard-gated one cleanup PR at a time.

### RuntimeEvent / RuntimeEventKind
The 12-value closed enum for the live event stream emitted by
SwarmRuntime during a run. See [Module 10](10-how-the-pieces-talk.md).

### R-rule
One of the 12 decision rules in the sufficiency decision engine
(R1 through R12). Each produces one of 7 `SufficiencyDecision`
outcomes. See [Module 09](09-evidence-and-safety.md).

---

## S

### SAS
Super-population code: South Asian ancestry.

### scope firewall
The platform's enforcement mechanism against feature drift. Closed
enums at every cross-module boundary reject out-of-scope inputs at
construction time, not runtime. See [Module 06](06-why-deterministic.md).

### SNP (single nucleotide polymorphism)
A variant at a single DNA position. Identified by rsID.

### star allele
The pharmacogenomics-specific naming convention for gene variants
in the CYP family (e.g. `*1`, `*2`, `*17`). Defined by one or more
rsID positions.

### SufficiencyDecision
The closed 7-value enum produced by the 12-rule decision engine:
SUFFICIENT, PASS_WITH_CAVEAT, DOWNGRADE, REQUEST_MORE, ESCALATE,
ABSTAIN, BLOCK.

### super-population
One of 5 coarse ancestry groupings: EUR, EAS, SAS, AFR, AMR.
From 1000 Genomes / gnomAD. Operationalized as
`SuperPopulation` closed enum.

### SwarmRuntime
The 5-stage lifecycle class that orchestrates a single run in
swarm. Emits RuntimeEvents as it progresses. See [Module 04](04-architecture.md).

---

## U

### U-rule
One of the 9 uncertainty-scoring rules (U1 through U9). Produces
a UncertaintyScore tier. See [Module 09](09-evidence-and-safety.md).

### UM (Ultrarapid Metabolizer)
One of 5 phenotype categories. Very high enzyme activity.

### UncertaintyScore
The closed 4-value enum: LOW, MODERATE, HIGH, UNSAFE.

---

## V

### VCF (Variant Call Format)
The standard file format for genome-sequencing output. Tab-separated,
one row per variant position. Parsed by pgx-core gene callers.
See [Module 03](03-core-concepts.md).

### VerificationScore
The 5-tier closed enum: grounded, partially_grounded, unverified,
conflicting, unsafe. Produced by the 4 verification engines.

### V-rule
One of the 10 verifier rules (V1 through V10) in the
SetLevelEvidenceVerifier. Produces an EvidenceVerdict. See [Module 09](09-evidence-and-safety.md).

---

## W

### wildtype
The reference version of an allele. Typically `*1` in the
CYP family's naming convention.
