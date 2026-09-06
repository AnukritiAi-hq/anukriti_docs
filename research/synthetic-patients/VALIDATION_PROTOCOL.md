# Validation protocol for the DPYD/DPD/5-FU synthetic-patient engine

Status: proposed protocol, 6 September 2026. Clinical partners and the statistician
must lock the endpoint, setting, and analysis before evaluating local performance.
This document specifies the engineering and scientific checks to implement; it
does not claim the new engine has passed them.

## Primary intended use and estimands

The first target is an adult infusional 5-FU **exposure simulation and research
planning** engine. Primary technical outcome: predicted concentration-time
behavior and exposure against independent real measurements. Clinical toxicity
is a later endpoint requiring observed outcomes, regimen-specific attribution,
and adequate events. General genome realism is an intermediate check.

Separate three questions:

1. Does the generated cohort reproduce relevant genomic and physiological
   distributions in the target population?
2. Does the genotype/function/physiology model predict real 5-FU exposure?
3. Does adding synthetic data improve a specified predictor or research decision
   on new real people compared with simpler baselines?

A positive answer to one question does not answer the other two. A generator
that passes linkage metrics can still produce poor exposure predictions; an
exposure model may still fail to predict clinical toxicity.

## Partitions and leakage prevention

Build splits **before** fitting founders, local mixture weights, physiological
distributions, imputation, variant-effect models, or drug models. Group real
participants by family/relatedness and keep all visits/cycles within one split.
For external evaluation, hold out a site, time interval, or population with a
documented recruitment frame. Keep a final local test partition inaccessible to
model-selection code until the analysis is frozen.

For functional prediction, additionally group duplicate variant/haplotype records,
protein positions where appropriate, and source assays/studies. The same measured
variant appearing in ClinVar, a publication, and an internal table is not three
independent training examples. Check overlap between protein-model pretraining,
functional-assay training and the claimed external benchmark when ascertainable.

Track a provenance DAG from each generated individual back to founders, fitted
cohort parameters, outcome-training records, and calibration studies. Split
integrity checks operate on those ancestors. Splitting generated siblings after
generation is invalid. A public reference panel can also overlap a local cohort;
audit identifiers and relatedness where lawful and feasible.

Use real development data for tuning; do not use held-out frequency or LD to choose
donors and then call the same target data independent validation. The historical
CYP2B6 experiment used a fixed source catalog and person-level splits but did not
screen cross-person kinship; it remains a feasibility benchmark.

## Gate G0: data and reproducibility

Pass conditions:

- Every source, reference assembly, map, clinical table, functional measurement,
  software binary, and model file has a version/hash and permitted-use status.
- A small documented execution example runs using the exact pinned release.
- Units, coordinate conventions, transcript versions, and missingness states
  round-trip without loss.
- Source access failures remain visible. Required unavailable data do not produce
  silently substituted populations, normal genotypes, or normal DPD values.
- A fresh environment reproduces fixed-seed deterministic records; numerical ODE
  results agree within declared solver/version tolerances.

## Gate G1: genetic validity

Check Mendelian transmission using truth pedigrees, sex-specific maps, and
separate ascertainment/noise. Measure recombination-count/position distributions,
IBD/kinship, phase-switch error, allele/haplotype frequencies, site-frequency
spectrum, LD decay, multivariant phase, heterozygosity, and runs of homozygosity.
Evaluate per subgroup and pharmacogene, including rare variants separately.

Use CPIC/PharmVar/assay truth definitions as versioned interpretation inputs,
not as proof that all biologically possible haplotypes have been cataloged.
Explicit DPYD fixtures include causal/proxy HapB3 discordance, cis/trans compound
variants, phased common-plus-actionable variants, unknown splice variants,
exon-level deletion, whole-gene deletion, duplication, uncertain breakpoints,
untested loci, and no-calls. Unsupported structure must be retained and flagged.

Baselines: independent-SNP sampling; local haplotype resampling; pooled regional
resampling; map-based copying; explicit pedigree generation; and any proposed
local calibration. Report all methods, including when a simpler baseline wins.
Assess within-gene and across-gene dependence instead of combining independently
generated genes and assuming they form one valid ancestry mosaic.

Acceptance for software invariants is exact: no unexplained Mendelian violations
in the zero-mutation/no-error mode; no missing-to-reference conversions; no
unsupported event silently dropped. Distributional tolerances must be set using
real-vs-real resampling variability and the intended use, not arbitrary universal
LD or frequency thresholds. Report finite-sample uncertainty and rare-site counts.

## Gate G2: physiology and parameter validity

Compare marginal and joint distributions with source and local observations:
age/size, renal/liver state, organ scaling, covariate correlations, disease and
regimen composition. Verify that OSP constraints are satisfied and that
conditional distributions reflect the target oncology cohort rather than generic
healthy volunteers. Record exclusions and rejected draws.

For each DPD parameter bridge, check dimensions, assay normalization, kinetic
identifiability, posterior predictive behavior, and prior sensitivity. Keep
abundance and catalytic activity separate. A guideline category cannot be
converted directly into tissue `Vmax` without an explicit evaluated bridge.
Compare genotype-only, phenotype-only, combined and covariate-only models.

Baseline uracil/DPD measurements require their collection context. Include renal
function, time of day and preanalytics in the measurement model where supported.
For endogenous uracil, changes in production and clearance can be confounded;
do not assume one concentration uniquely identifies DPD capacity.

## Gate G3: published 5-FU model reproduction

First reproduce the released model's stated training and test scenarios in its
original environment or a verified conversion. Then run the same scenarios in
the selected current worker. Model-file availability alone is not reproduction.
Compare predicted curves and numerical outputs before introducing local ancestry
or novel functional parameters.

Required checks: mass balance with explicitly accounted metabolism/elimination,
nonnegative concentrations, bolus and infusion event timing, dose and time unit
conversion, solver tolerance convergence, and exact AUC interval definition.
Verify expected sensitivity to DPD changes within the model's supported range.
Near-zero DPD must not cause an implicit divide-by-zero or unjustified linear
dose scaling. Saturation, alternative elimination, and model domain matter.

The published 2024 5-FU/uracil model is the first reproduction candidate;
see [model sources and API audit](EVIDENCE_REGISTER.md). Reproducing it establishes
implementation fidelity to that model, not local clinical validity. Treat its
chronomodulated dosing experiments as research scenarios; do not deploy their
suggested schedules as patient recommendations.

## Gate G4: real local exposure prediction

Predefine:

- Eligible population, cancer/regimen, administration route/duration, cycle,
  prior treatment, and contemporaneous co-medication.
- Prediction time: before treatment, after baseline phenotyping, or after the
  first concentration measurement. These are different tasks.
- Reference assay, analytes, sampling times, assay errors/quantification limits,
  specimen processing and storage, delivery/pump records, and missingness policy.
- Whether evaluation is concentration prediction, observed/model-estimated AUC,
  or target attainment. If AUC is estimated using a model, specify that estimator
  and avoid validating a model against AUC calculated by the same fitted model.

Compare against the reproduced unmodified published PBPK model, a conventional
population-PK baseline, a covariate-only model, and genotype-guided priors where
applicable. For a post-concentration task, compare with an appropriately fitted
TDM/Bayesian updating baseline using the same measurement information.

Metrics: concentration prediction error and bias, dose-normalized and raw
exposure where meaningful, AUC error, interval coverage/width, predictive checks,
calibration by relevant subgroup, extreme-exposure misses, abstention/extrapolation
rates, and solver failures. Account for censoring below quantification limits;
do not replace all such measurements with zero.

Infusional AUC targets must come from a regimen-applicable source and local
protocol. Published 20–30 mg·h/L ranges are not universal across bolus schedules
or capecitabine. Do not silently collapse 20–29 and 20–30 definitions from
different protocols. Store the exact source, units and applicable interval.

Clinical acceptance margins and required precision are fixed with the team before
the locked evaluation. Use participant/family-level resampling and an external
site/time validation where possible; thousands of synthetic rows cannot increase
the number of independent observed test participants.

## Gate G5: synthetic-data utility

For a specified exposure or outcome model, compare:

1. Real local training data only.
2. Real local + permitted regional real data or transfer learning.
3. Standard balancing/reweighting or resampling.
4. Real + genotype-only synthetic augmentation.
5. Real + mechanistically labeled synthetic augmentation.
6. Train-on-synthetic/test-on-real, where scientifically meaningful.

Vary real sample size and synthetic augmentation ratio on development partitions.
Use matched covariates, endpoint definitions, model-selection budgets and real
test sets. Report whether gains come from new real references, task supervision,
regularization or sampling—not simply a larger nominal cohort. Include an
ablation of local calibration, physiology, measured function, DPD variability,
and model discrepancy.

Test collapse and harm: loss of rare variants, erased subgroup differences,
overconfident intervals, memorized founders, distorted LD, and negative transfer.
Do not select a generator solely because a classifier cannot distinguish its
outputs from real data. A discriminator is one diagnostic, not clinical utility.

## Gate G6: observed toxicity and prospective evaluation

After exposure evaluation, define each toxicity endpoint with term, grade, grading
system/version, assessment window, baseline abnormality, competing therapy and
follow-up completeness. First-cycle grade ≥3 adverse events, neutropenia,
mucositis/diarrhea, hospitalization, treatment interruption and death are distinct
outcomes. Any composite requires a prespecified definition.

DPD-mediated systemic exposure is one contributor. Tumor pharmacodynamics,
anabolism/target pathways, radiation, irinotecan/oxaliplatin and other treatments
can change the outcome. Do not infer an individual's tumor response from a host
germline genotype or assign a toxicity grade solely from an AUC threshold.

Use clinically interpretable absolute-risk calibration and discrimination,
subgroup confidence intervals, decision consequences, and comparison with the
actual clinical workflow. A prospective observational/shadow evaluation precedes
any study where model output changes care. Enrollment, consent, site approvals,
clinical accountability and sample size are parts of that study protocol, not
assumed completed by software development.

## Sample size, uncertainty and reporting

Compute sample requirements from endpoint variability, expected effect, clinically
acceptable error, rare-variant prevalence, subgroup representation, family
clustering and follow-up. Do not promise that 20, 100, or any arbitrary number of
local people validates all tasks. The prior 20-person benchmark was chosen for a
small-data simulation experiment.

Report epistemic uncertainty, patient variability, assay error, and Monte Carlo
error separately where estimable. Use ensembles/posterior predictive cohorts and
report sensitivity to plausible founder, physiology, and function models.
For enriched rare scenarios, retain sampling weights and do not derive prevalence
from raw generated counts.

Release a model card and evaluation report stating completed gates, target
population/regimen, observed test size, uncertainty, excluded settings, known
failures, data/model licenses, and version hashes. Synthetic data privacy and
relatedness checks are required before a public local-donor-derived release;
passing the historical public-reference prototype does not establish that result.
