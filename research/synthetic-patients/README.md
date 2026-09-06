# Synthetic patients: DPYD/DPD/5-FU first

This collection preserves the synthetic-genome findings and sets out the
implementation plan for an Anukriti synthetic-patient engine with oncology
collaborators. The first pathway is **DPYD → DPD → adult infusional 5-FU
exposure**. The planned engine is not implemented or clinically validated.

Research date: 6 September 2026. The earlier general PGx proposal is retained as
history; the current plan prioritizes direct DPYD functional studies and a
published 5-FU model over the previous CYP2C19/clopidogrel pilot suggestion.

| Read | Purpose |
|---|---|
| [Full implementation plan](IMPLEMENTATION_PLAN.md) | Phases 0–10, dependencies, concrete tasks, source references, acceptance criteria, estimates and first session |
| [Component research](COMPONENT_RESEARCH.md) | Founder data, inheritance, adult physiology, DPYD function, 5-FU modeling and clinical evaluation |
| [Data contracts](DATA_CONTRACTS.md) | Genome/patient/scenario records, phase/SV, assay coverage, units, evidence classes and provenance |
| [Validation protocol](VALIDATION_PROTOCOL.md) | Genetic fidelity, model reproduction, real exposure, synthetic utility and later toxicity endpoints |
| [Evidence/API register](EVIDENCE_REGISTER.md) | Primary sources, exact documented APIs, source locations and unresolved access/version questions |
| [Paper collection](../../papers/synthetic-patients/README.md) | HAPNEST, Ped-sim, SimHumanity, CYP2C9, direct DPYD and 5-FU papers |
| [Historical initial research](historical/2026-09-06-initial-research.md) | Original synthetic-genome feasibility and small-population analysis |
| [Historical experiment follow-up](historical/2026-09-06-feasibility-and-experiment.md) | Constructive follow-up and initial hybrid-engine proposal |
| [Executed prototype](benchmark/README.md) | Archived source, tests, design and generated public-reference data |
| [Benchmark results](benchmark/results/REPORT.md) | All 72 runs; pooled copying beat the proposed calibration on average |

The archived experiment generated 5,000 synthetic diploid regional profiles at
8,901 sites around CYP2B6, with exact genotype export verification. It is an
approximately 250 kb b37 benchmark using public reference donors, not a DPYD or
Bhutan clinical cohort. Its six tests and source/output hashes are preserved.

The new plan adds three findings that change the implementation order:

- A direct 5-FU/uracil PBPK model and actual project files exist; reproduce those
  before attaching local patient parameters.
- Direct DPYD functional studies provide activity and kinetic data. Preserve
  assay disagreements and calibrate a quantitative DPD bridge against human
  observations.
- DPYD causal/proxy variants, cis/trans phase and exon deletions need explicit
  treatment. The existing caller's provenance is useful but its phase capability
  cannot be inferred from the presence of phased input strings.

The next execution step is **Phase 0 qualification**: confirm the clinical
context, pin sources and runtime, execute documented examples and reproduce one
published 5-FU case. The default adult infusion setting remains a planning
assumption pending confirmation of the partner regimen.

Historical source code and VCF bytes are unchanged. Markdown links were relocated
for this docs repository and archive notes added where original workspace paths
would otherwise be misleading. No private oncology participant data are included.
