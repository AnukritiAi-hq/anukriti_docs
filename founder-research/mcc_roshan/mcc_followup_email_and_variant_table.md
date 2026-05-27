# Sendable MCC Follow-Up — DPYD Variant Table + PCR Workflow

Subject: DPYD / 5-FU toxicity: variant table and PCR workflow for MCC collaboration

Dear Dr. Roshan,

Thank you for the conversation today. Your question helped clarify the exact clinical use case.

Anukriti is not predicting whether 5-FU will kill the tumor. That is a tumor-response / efficacy question and depends on somatic tumor biology. What Anukriti answers is the patient-safety question:

> Given this patient's germline DPYD result, can they safely metabolize fluoropyrimidines such as 5-FU, capecitabine, or tegafur, or is there elevated risk of severe toxicity?

This means MCC does not need to move to NGS before collaborating. Your current real-time PCR data is enough for Phase 1. We can ingest the PCR variant calls directly as structured genotypes.

## What Anukriti can do with MCC's current PCR data

For each anonymized patient:

1. Read the 7 DPYD PCR variant calls.
2. Map them to DPYD diplotype / DPD activity class.
3. Return metabolizer phenotype: normal, intermediate, or poor.
4. Attach fluoropyrimidine safety guidance: standard dose, dose reduction, or avoid/switch depending on diplotype.
5. Compare prediction against MCC's observed toxicity outcome.
6. Flag patients who had Grade 3+ toxicity despite testing negative on the current PCR panel.

That last group is the most important discovery group, because it may contain Indian-specific or currently under-tested variants.

## DPYD variants with strongest current clinical actionability

| Variant | rsID | Function | Interpretation |
|---|---:|---|---|
| DPYD *2A / c.1905+1G>A | rs3918290 | No function | Strong toxicity risk. Heterozygotes usually need reduced starting dose; compound/homozygous patients may need avoidance. |
| DPYD *13 / c.1679T>G / p.I560S | rs55886062 | No function | Strong toxicity risk. |
| c.2846A>T / p.D949V | rs67376798 | Decreased function | Intermediate metabolizer risk; commonly dose-reduced. |
| HapB3: c.1236G>A tag / c.1129-5923C>G causal | rs56038477 / rs75017182 | Decreased function | Intermediate metabolizer risk; commonly dose-reduced. |

These are the core CPIC / European implementation variants and are already handled by Anukriti.

## Indian / South Asian variants to compare against MCC's panel

| Variant | rsID | Name | Current interpretation |
|---|---:|---|---|
| c.1905+1G>A | rs3918290 | *2A | Actionable; reported in South Asian severe-toxicity literature. |
| c.85T>C / p.C29R | rs1801265 | *9A | Important conflict. Guidelines often treat as normal/uncertain, but Indian/East Asian studies repeatedly report it in toxicity cohorts. MCC outcome data can resolve whether it matters locally. |
| c.496A>G / p.M166V | rs2297595 | M166V | Reported in South Asian severe-toxicity cohorts; needs MCC outcome correlation. |
| c.1627A>G / p.I543V | rs1801159 | *5 | Reported in South Asian/East Asian cohorts; guideline actionability remains mixed. |
| c.1601G>A / p.S534N | rs1801158 | *4 | Reported in Indian cohorts; needs outcome correlation. |
| c.2194G>A / p.V732I | rs1801160 | *6 | Reported in South Asian cohorts; evidence mixed. |
| c.2846A>T | rs67376798 | D949V | Actionable; please confirm whether this is in MCC's 7-variant PCR panel. |
| HapB3 causal/tag | rs75017182 / rs56038477 | HapB3 | Actionable; please confirm whether MCC tests the causal variant, the tag SNP, or neither. |

## Data requested for Level 2

An anonymized spreadsheet is enough. Suggested columns:

| Column | Example |
|---|---|
| anonymized_patient_id | MCC_001 |
| cancer_type | colorectal / head and neck / breast / gastric |
| drug | 5-FU / capecitabine / tegafur |
| regimen | FOLFOX / CAPOX / etc. |
| DPYD PCR kit or assay | platform name |
| exact 7 variants tested | rsIDs or cDNA names |
| genotype per variant | CC/CT/TT or positive/negative |
| starting dose | mg/m2 or local dose field |
| dose reduction/interruption | yes/no + details |
| cycles completed | number |
| toxicity grade | CTCAE grade preferred |
| toxicity type | diarrhea, mucositis, neutropenia, myelosuppression, hand-foot syndrome, etc. |
| toxicity cycle/onset | cycle 1, cycle 2, etc. |
| clinician attribution | fluoropyrimidine-related / uncertain / other |
| NGS available | yes/no |

The key number I would like to calculate first:

> How many patients had Grade 3 or higher toxicity while negative for all 7 variants in the current PCR panel?

If that number is non-zero, those cases are the discovery set. We can compare them against toxicity-negative controls and decide whether targeted DPYD sequencing or NGS on only that subset is warranted.

## Proposed collaboration output

MCC can lead the clinical study. Anukriti can provide the analytical engine and reproducible audit trail.

Possible paper:

> DPYD variant spectrum and fluoropyrimidine toxicity in an Indian oncology cohort.

Initial deliverables from Anukriti:

1. Patient-level DPYD phenotype table.
2. Predicted-risk vs observed-toxicity concordance table.
3. Variant-by-variant frequency and toxicity association table.
4. List of PCR-negative but toxicity-positive patients for possible sequencing follow-up.
5. Evidence labels separating CPIC-actionable variants from Indian candidate variants requiring local validation.

Best,
Abhimanyu

## Internal Notes: Evidence Anchors

- CPIC / fluoropyrimidines: *2A rs3918290, *13 rs55886062, c.2846A>T rs67376798, HapB3 rs75017182/rs56038477.
- Non-European systematic review: one of the four European variants, c.1905+1G>A, appears in South Asian severe-toxicity cases; c.557A>G has stronger African-ancestry evidence.
- South Asian studies listed in Chan/Zhang/Pirmohamed include Indian cohorts with c.85T>C/*9A, c.496A>G/M166V, c.1601G>A/*4, c.1627A>G/*5, c.1905+1G>A/*2A, c.2194G>A/*6.
- Functional/clinical ambiguity remains for *9A, *4, *5, *6, and M166V. Do not call them CPIC-actionable without MCC outcome support.
