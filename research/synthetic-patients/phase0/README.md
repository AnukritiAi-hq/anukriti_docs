# Phase 0: 5-FU source and runtime qualification

Execution started 6 September 2026. This is the qualification record for the
[implementation plan](../IMPLEMENTATION_PLAN.md#phase-0--documentation-source-acquisition-and-model-qualification),
before introducing new patient covariates or DPYD parameters.

| Record | Purpose |
|---|---|
| [Qualification report](QUALIFICATION_REPORT.md) | Status of P0.1–P0.8, executed checks and remaining gates |
| [Context of use](CONTEXT_OF_USE.md) | Published reproduction case and proposed oncology pilot, with unresolved partner inputs |
| [Source qualification](SOURCE_QUALIFICATION.md) | Model identity, reuse terms, CPIC/core snapshot and acquisition results |
| [Study reuse audit](STUDY_REUSE_AUDIT.md) | Source study overlap, fitting versus evaluation and numerical comparison rules |
| [Source registry](source_registry.json) | Exact hashes, versions, URLs and acquisition states |

The selected publication case is **Grem 2001, 5-FU 5,250 mg/m² over 72 hours**,
represented by `FU_86_G01_IV_C_Circ` in the published constant-infusion project.
The proposed **46-hour adult oncology pilot** is a later configuration requiring
the partners' regimen and measurement details. These are separate studies.

Executable work belongs to the research sandbox, under
`anukriti/research/fluorouracil_phase0/` in the shared workspace. This documentation
does not contain upstream model binaries, copied observed concentration arrays,
private participant records or an implementation of the patient engine.

An executed model is only one qualification result. Source reproduction,
modern-runtime migration, independent real-data prediction and clinical benefit
are separate outcomes with separate acceptance criteria.
