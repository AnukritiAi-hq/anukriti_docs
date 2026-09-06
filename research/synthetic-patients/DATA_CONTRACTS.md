# Synthetic-patient engine: proposed data contracts

Status: implementation design, 6 September 2026. These are proposed Anukriti
interfaces, not claims about existing third-party APIs. The first release models
adult systemic 5-FU exposure through host DPYD/DPD biology. Clinical toxicity is
a separately validated endpoint.

## Storage and identity

Use versioned JSON manifests, phased VCF/BCF for variants, and Parquet tables for
patients, parameters, measurements, and simulation output. Keep large cohorts
in controlled artifact storage; Git holds code, schemas, small public fixtures,
and hashes. Start with filesystem execution and a local job runner. Add a
database or distributed scheduler only after measured requirements justify it.

Every record includes `schema_version`, `record_id`, `origin`, `source_ids`,
`created_at`, `generator_version`, and `manifest_id`. `origin` is one of
`observed`, `simulated`, `curated_rule`, or `model_prediction`. A record derived
from an observed participant is not relabeled as independently observed.
Synthetic IDs use a separate namespace and never imitate site patient IDs.

Use three linked identities: `genome_id`, `virtual_patient_id`, and
`scenario_id`. One genome can have several plausible physiology realizations;
one virtual patient can receive several research regimens. This hierarchy must
remain visible in exports and statistical resampling.

## Required objects

| Object | Required content | Invariant |
|---|---|---|
| `SourceManifest` | Source accession/URL, release, SHA-256, assembly, assay, consent/use restrictions, population sampling, access status | Public catalog visibility never implies permission to use underlying individual data |
| `SplitManifest` | Participant and family groups, site/time split, reference donors, development/validation/locked-test IDs, variant-study split | Every descendant and transformation inherits its source partition |
| `FounderPanel` | Phased records, sample metadata, phase-set confidence, relatedness, coverage mask, source populations | Missing, filtered, and untested loci remain distinguishable |
| `PopulationSpec` | Target population definition, subgroups, mixture uncertainty, ascertainment, recruitment frame, relatedness/mating assumptions | Nationality is not a complete ancestry specification |
| `GenomeTruth` | Maternal/paternal segments, donor ancestry, breakpoints, per-haplotype SNVs/indels/SVs, pedigree, phase | Multiple changes on one homologue are not counted as independent chromosomes |
| `AssayObservation` | Panel definition, coverage, read/call quality, missingness, phase resolution, measured CNV | Derived from truth through a separate observation model |
| `PGxInterpretation` | Exact core version/tables, diplotype, evidence, HapB3 basis, unresolved phase/SV, source assay | An interpretation cannot silently exceed its assay or caller capability |
| `FunctionalEvidence` | Variant/haplotype, protein/transcript, substrate, system, activity/abundance/kinetics, units, uncertainty, citation | Laboratory activity, protein abundance, clinical function, and human clearance are different fields |
| `PhysiologyState` | Age, model-supported sex category, size/composition, organ state, labs, disease/regimen covariates, time | Physiology variables retain joint dependencies and evidence provenance |
| `DPDParameterDraw` | Tissue, abundance/activity distribution, kinetic parameters, circadian parameters, evidence/model version | Guideline activity score is not substituted for a continuous clearance multiplier |
| `TreatmentScenario` | Route, cycle, actual administered dose, schedule, infusion events, co-medication, hypothetical/observed status | Bolus, infusion, and oral prodrug regimens are separate configurations |
| `SimulationResult` | Concentration-time curves, analytes, AUC interval, units, parameter draw, solver status, uncertainty | Simulated exposure never becomes an observed toxicity label |
| `ObservedExposureMeasurement` | Site-held patient, cycle and administration IDs; analyte/matrix; collection time; concentration/units; assay, censoring and specimen quality | Measured concentrations remain separate from model predictions and concentration-derived AUC estimates |
| `ObservedOutcome` | Site-held patient ID, assessment window, toxicity term/grade/version, labs, hospitalization, dose changes | No synthetic or model-imputed outcome enters the locked observed test set |
| `EvaluationReport` | Intended use, splits, baselines, metrics, intervals, exclusions, missingness, failure counts | Negative results and abstentions stay in denominator accounting |

## Genome and assay details

Choose GRCh38 as the target assembly for the new engine unless Phase 0 documents
a justified source constraint. Existing b37 prototype results remain b37.
`assembly`, reference FASTA hash, contig naming, reference strand, and genetic-map
build are mandatory. Coordinates are canonical VCF 1-based positions; intervals
in BED adapters are explicitly 0-based half-open. Conversion happens once at a
typed boundary and is round-trip tested. No bare coordinate is accepted.

Variant identity is assembly + contig + position + REF + ALT, with rsID and HGVS
as annotations. Transcript and protein accessions include versions. Normalize
indels against the pinned FASTA; handle split multiallelic records without losing
genotype indices or phase. Validate REF after any liftover. A failed or ambiguous
conversion is retained as a failed conversion, not a reference call.

Haplotype records include `phase_set`, `phase_evidence`, `phase_confidence`, and
`copy_index`. Structural events carry event type, breakpoints and uncertainty,
orientation, affected exons, copy number, source evidence, and haplotype
assignment or an explicit unknown assignment. Exon deletion and whole-gene
deletion are distinct. A representation that cannot express an event must fail
capability checking before clinical interpretation.

For DPYD retain causal `rs75017182` and proxy `rs56038477` separately. Fixtures
must represent causal only, proxy only with causal untested, proxy with causal
tested negative, both in cis, both in trans, and phase unresolved. Never enforce
their co-occurrence as a universal biological rule. Follow the existing core's
`hapb3_basis` provenance while recognizing its current unphased inference.
See [component research](COMPONENT_RESEARCH.md) and [integration plan](IMPLEMENTATION_PLAN.md).

The observation model has explicit `not_tested`, `tested_reference`,
`tested_alternate`, `no_call`, and `ambiguous` states. The existing ASL enum is
not assumed to represent every new state; adapt or extend it deliberately.
Genotype errors, missingness, phase errors, and panel censoring are applied only
after a truth genome exists. Save both objects and their mapping.

## Functional evidence and the DPD bridge

Store each assay result separately, even when two studies measure the same
variant. Required fields include gene/protein, construct background, expressed
alleles, substrate and concentration range, cofactor conditions, expression
system, tissue/cell type, abundance normalization, replicates, mean/dispersion,
detection limits, curve-fitting method, and source table/row. Where data are
unavailable, use a null plus a reason; do not invent a standard deviation.

Distinguish `relative_activity`, `protein_abundance`, `Km`, `Vmax`, `CLint`,
`clinical_function_class`, `guideline_activity_score`, and
`estimated_in_vivo_DPD_capacity`. Experimental `Vmax` normalized per assay
protein is not a whole-liver `Vmax`. An explicit scaling model and uncertainty
must connect them. The converter requires dimensional consistency and refuses
missing reference quantities.

Compound heterozygotes and variants in cis require a haplotype-aware model.
Simple additivity is a named baseline, not an asserted property of the DPD
dimer. Splice variants require expression/splicing evidence; a missense assay
does not cover them. Increased activity is representable without forcing every
measurement into three guideline categories.

`DPDParameterDraw` separates posterior uncertainty shared across a population
from patient variability. Record `population_draw_id`, `patient_draw_id`, and
`assay_model_id`; draw uncertain population parameters once per virtual cohort
and patient deviations conditionally within that cohort. Generating more
patients reduces simulation noise but does not collapse the posterior uncertainty
supported by a small real cohort.

## Physiology and treatments

Minimum physiology fields: age in years; model-supported physiological sex
parameter with source; height cm; weight kg; body-surface-area method; creatinine
and units; renal-function estimate and formula; bilirubin, albumin and liver
measures with units; relevant blood counts; cancer/site/stage; performance
status; baseline uracil and dihydrouracil where measured; blood-draw clock time;
fasting/sample handling; and current co-medication. Preserve missingness and the
method used to sample an unavailable covariate.

Use joint conditional models, not independent uniform draws of weight, height,
age, organ volumes, organ blood flow, renal function, and disease burden. Do not
sample a creatinine and an unrelated eGFR independently. Record OSP-derived
anatomy as derived data. Do not add an arbitrary ancestry multiplier to DPD.

`TreatmentScenario` stores dose basis (`mg`, `mg/m2`, etc.), the conversion inputs,
route, start time, planned duration, delivered duration, interruption events,
bolus events, cycle number, and actual rather than merely prescribed delivery
where observed. Integration units are explicit. The first configuration is
adult IV infusional 5-FU; a 46-hour schedule is a configurable candidate pending
partner confirmation. Bolus and oral capecitabine are separate validation strata.

Medication records need drug identity, active ingredients, dose/time, and
start/stop dates. Record both pharmacokinetic interaction candidates and
co-treatments that can cause overlapping toxicity. A 5-FU concentration model
alone cannot attribute all neutropenia in a combination regimen to 5-FU.

## Real exposure measurements

`ObservedExposureMeasurement` links to patient, cycle and actual administration
records. Require analyte and specimen matrix; collection timestamp with timezone;
elapsed time since administration start and, where applicable, end; measured
concentration with units; LLOQ/ULOQ and censoring status; assay method/version;
specimen collection, processing, storage and stability metadata; quality flags;
and laboratory/source identifiers. Missing metadata retain an explicit reason.
Below-quantification values are censored measurements, not zero concentrations.

Store concentration-derived AUC separately, with integration interval, units,
input measurement IDs, estimator/version, uncertainty and any model assumptions.
An AUC calculated from sparse concentrations is an estimate; retain whether it
uses numerical integration, a steady-state approximation, or a fitted PK model.
An AUC estimated using the candidate simulation model cannot serve as independent
ground truth for validating that same model. Retain raw measured concentrations
as the primary external measurement endpoint.

## Outputs and capability states

Return a versioned capability state: `GENOME_BENCHMARK_ONLY`,
`EXPOSURE_SIMULATION`, `LOCALLY_EVALUATED_EXPOSURE`, or
`OBSERVED_OUTCOME_MODEL_EVALUATED`. These are proposed internal states, not
regulatory certifications. Any recommendation capability requires a separately
defined clinical-validation and deployment process.

Outputs include plasma 5-FU and available modeled metabolites, units, concentration
times, specified-window AUC, prediction intervals, source regimen, parameter-draw
IDs, solver failures, extrapolation flags, and model discrepancy. A concentration
outside a chosen research target interval is a simulated exposure event; it is
not a grade-3 toxicity event.

Both naturalistic and deliberately enriched cohorts carry sampling probabilities
and population weights. Case-enriched data can test software and model behavior;
its unweighted prevalence must not be presented as national incidence.

The published docs and prototype contain only public reference-derived data.
Future local participant data, consent documents, and identifier mappings remain
in the approved site environment. Remote execution accepts bounded manifests
and artifact handles, not arbitrary model paths, shell commands, or unbounded
simulation counts.
