# MCC / Dr. Roshan — Research Conversation Notes
Role: Oncology clinician / research-center collaborator
Date: May 27, 2026
Platform: Call
Primary wedge: DPYD / fluoropyrimidine toxicity in Indian oncology patients

## Key Insight

MCC is not asking for a generic Anukriti demo. They are asking a concrete clinical question:

> "Given our 400-500 DPYD-tested patients and toxicity follow-up, which DPYD variants predict fluoropyrimidine toxicity, and which of those are outside our current PCR panel?"

That reframes the market message. The partner does not first care about VCFs, agents, or infrastructure. They care about whether Anukriti can turn an existing real-time PCR dataset into a genotype-to-toxicity map that helps MCC identify missed-risk patients and publish Indian evidence.

## What MCC Has

| Asset | Detail | Product implication |
|---|---|---|
| DPYD-tested patient cohort | Around 400-500 patients | Enough for a first Indian institutional validation analysis, especially if toxicity outcomes are already curated. |
| Test modality | Real-time PCR, not NGS | Anukriti must support structured PCR input directly; VCF cannot be required. |
| Panel | 7 known DPYD polymorphisms | We need MCC's exact 7 rsIDs/cDNA names before analysis. |
| Outcomes | Toxicity follow-up over 7 months to 1 year | This is the highest-value field; genotype without outcome is frequency, genotype plus outcome is clinical evidence. |
| Clinical concern | DPYD positivity relatively low | The key value may be finding toxicity-positive, PCR-panel-negative cases. |

## The Language to Use

### The shortest explanation

Anukriti is a safety engine for fluoropyrimidines. It takes a patient's DPYD test result and answers:

> "Is this patient likely to clear 5-FU/capecitabine normally, or should the dose be reduced/avoided because toxicity risk is high?"

It does not answer:

> "Will this tumor respond to 5-FU?"

That is a different question based on tumor biology and somatic mutations.

### Better clinical wording

- **Input:** germline DPYD genotype from PCR or NGS.
- **Output:** DPD activity class / metabolizer phenotype.
- **Clinical use:** fluoropyrimidine toxicity risk stratification and starting-dose guidance.
- **Not claimed:** tumor response prediction or chemotherapy efficacy prediction.

## What MCC Gets From Anukriti

For each anonymized patient:

| Input from MCC | Anukriti output |
|---|---|
| Patient ID | Stable anonymized analysis row |
| 7 DPYD PCR calls | Normal/intermediate/poor DPD metabolizer phenotype |
| Drug exposure: 5-FU, capecitabine, tegafur | Drug-specific fluoropyrimidine safety recommendation |
| Toxicity outcome: grade, type, timing | Concordance table: predicted-risk vs observed toxicity |
| Dose changes / cycles if available | Audit flag for confounding by dose reduction or interruptions |

For the cohort:

- How many patients were high/intermediate risk by current CPIC variants.
- How many had Grade 3+ toxicity despite being negative on MCC's current PCR panel.
- Which Indian/South Asian candidate variants are plausible explanations for the panel-negative toxicity cases.
- Whether MCC's 7-variant panel is sufficient, or whether it should add/triage variants.
- A publication-ready table: variant, frequency, toxicity association, actionability level, and evidence source.

## Variant Answer for MCC

### Variants Anukriti treats as clearly actionable today

These are the CPIC / European implementation core and should be treated as the strongest current clinical signal.

| Variant | rsID | Effect | Anukriti phenotype impact | Usual action |
|---|---:|---|---|---|
| DPYD *2A / c.1905+1G>A | rs3918290 | No function | Heterozygote -> IM; homozygote/compound -> PM | Reduce dose or avoid, depending diplotype |
| DPYD *13 / c.1679T>G / p.I560S | rs55886062 | No function | Heterozygote -> IM; compound/homozygote -> PM | Reduce dose or avoid, depending diplotype |
| c.2846A>T / p.D949V | rs67376798 | Decreased function | Usually IM if heterozygous | Start ~50% dose reduction, titrate |
| HapB3 tag c.1236G>A / causal c.1129-5923C>G | rs56038477 / rs75017182 | Decreased function | Usually IM if heterozygous | Start ~50% dose reduction, titrate |

### Indian / South Asian variants MCC should map

These are not all equally actionable. The point is to compare MCC's tested variants and toxicity outcomes against this list.

| Variant | rsID | Also called | What we should tell MCC |
|---|---:|---|---|
| c.1905+1G>A | rs3918290 | *2A | Confirmed in South Asian severe-toxicity literature and actionable in Anukriti. |
| c.85T>C / p.C29R | rs1801265 | *9A | Key conflict. Anukriti/CPIC currently treats as normal function, but Indian/East Asian toxicity studies repeatedly report it. MCC outcomes can resolve whether it matters in their cohort. |
| c.496A>G / p.M166V | rs2297595 | M166V | Reported in South Asian severe-toxicity cohorts; actionability depends on outcome association and haplotype context. |
| c.1627A>G / p.I543V | rs1801159 | *5 | Reported in South Asian and East Asian cohorts; often treated as uncertain/normal in guidelines. Needs MCC outcome correlation. |
| c.1601G>A / p.S534N | rs1801158 | *4 | Reported in Indian cohorts; guideline actionability is not strong enough alone. Needs outcome correlation. |
| c.2194G>A / p.V732I | rs1801160 | *6 | Reported in South Asian cohorts; evidence mixed. Needs outcome correlation. |
| c.2846A>T | rs67376798 | D949V | Actionable CPIC variant; check whether MCC includes it in the 7-PCR panel. |
| HapB3 causal/tag | rs75017182 / rs56038477 | HapB3 | Actionable CPIC variant; check whether MCC tests causal SNP, tag SNP, or neither. |
| c.557A>G / p.Y186C | rs115232898 | Y186C | Stronger evidence in African-ancestry toxicity; useful as a non-European example, not the first Indian add-on. |
| c.704G>A / p.R235Q | not confirmed here | R235Q | Reported in an Indian-origin severe-toxicity case; treat as discovery/NGS candidate, not panel-ready. |

## Honest Current Product Boundary

Anukriti's engine currently has strong direct actionability for the CPIC core DPYD variants. For *9A, *4, *5, *6, and M166V, the correct behavior is not to overclaim. The correct behavior is:

1. Ingest MCC's PCR calls.
2. Run current Anukriti classification.
3. Label the non-core Indian candidate variants as "research evidence / outcome-correlation needed."
4. Compare against observed Grade 3+ toxicity.
5. Upgrade or reject candidate variants only if MCC's outcome data supports it.

This is a strength, not a weakness. It makes MCC the clinical evidence partner rather than asking them to simply validate a finished black box.

## Level 2 Data Ask

Ask MCC for an anonymized spreadsheet with one row per patient:

| Field | Required? | Notes |
|---|---|---|
| anonymized_patient_id | Yes | No names, MRNs, phone numbers, direct identifiers. |
| cancer_type | Yes | Colorectal, head and neck, breast, gastric, etc. |
| fluoropyrimidine_drug | Yes | 5-FU, capecitabine, tegafur, combination regimen. |
| DPYD assay method | Yes | Real-time PCR kit/platform and exact panel. |
| DPYD variants tested | Yes | Exact 7 variants: rsID and/or cDNA name. |
| genotype per variant | Yes | e.g. CC/CT/TT or positive/negative. |
| starting dose | Strongly preferred | Required to interpret toxicity correctly. |
| dose reductions / interruptions | Strongly preferred | Separates genotype risk from dose-management effects. |
| cycles received | Strongly preferred | Toxicity timing context. |
| toxicity grade | Yes | CTCAE grade preferred. |
| toxicity type | Yes | Diarrhea, mucositis, neutropenia, myelosuppression, hand-foot syndrome, etc. |
| toxicity onset date/cycle | Preferred | Helps identify early fluoropyrimidine toxicity. |
| toxicity attribution | Preferred | Clinician judgment: fluoropyrimidine-related or confounded. |
| NGS available? | Optional | Especially for PCR-negative Grade 3+ toxicity cases. |

## Highest-Value Analysis

The central table for MCC:

| Group | Count | Meaning |
|---|---:|---|
| PCR-positive + Grade 3+ toxicity | n | Current panel is catching real risk. |
| PCR-positive + no Grade 3+ toxicity | n | Dose adjustment may be working, or variant penetrance is incomplete. |
| PCR-negative + Grade 3+ toxicity | n | Discovery group; possible missed Indian variants or non-DPYD causes. |
| PCR-negative + no Grade 3+ toxicity | n | Baseline comparison group. |

The most important Level 2 question:

> "Among your 400-500 patients, how many had Grade 3 or higher toxicity while negative for all 7 variants?"

If this number is non-zero, Anukriti can propose NGS or targeted sequencing only on those patients and matched controls, not on everyone.

## Proposed Collaboration Framing

MCC is lead clinical institution. Anukriti is the analytical engine.

Phase 1:

- MCC sends anonymized PCR + toxicity spreadsheet.
- Anukriti runs deterministic classification.
- Joint review of discordant cases.

Phase 2:

- Focus on PCR-negative, toxicity-positive patients.
- If NGS exists, map DPYD variants outside the current panel.
- If NGS does not exist, propose targeted DPYD sequencing for discovery subset.

Phase 3:

- Paper: "DPYD variant spectrum and fluoropyrimidine toxicity in an Indian oncology cohort."
- MCC owns clinical interpretation and cohort context.
- Anukriti provides reproducible analytical pipeline, audit trail, and population-evidence stratification.

## References to Use

- CPIC fluoropyrimidine / DPYD guideline and 2018 update: core variants and dose guidance.
- Chan, Zhang, Pirmohamed 2024 systematic review of non-European DPYD variants in severe fluoropyrimidine toxicity.
- Hariprakash et al. 2018 South Asian DPYD pharmacogenetic landscape.
- Offer et al. 2013 / related functional work for *9A, *4, *5, *6, M166V ambiguity.

