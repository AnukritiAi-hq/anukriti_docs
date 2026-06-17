<!--
  PAPER DRAFT — saved to anukriti_docs 2026-06-14.
  Source: author manuscript (Abhimanyu R B et al.). Draft v0.3.

  ─────────────────────────────────────────────────────────────────────────
  EDITOR'S FACT-CHECK NOTE (added on save 2026-06-14; verified against repo +
  PyPI). Resolve these before circulating — the prose below is the author's
  original except for two unambiguous reference fixes (marked [corrected]).

  1. PyPI VERSION — Abstract and Appendix A say "v0.2.1". We published and
     validated everything in this paper against **anukriti-pgx-core 0.6.0**
     (live on PyPI; the CYP2D6 SV ingestion + DPYD clinical-action tier ship
     in 0.6.0, NOT 0.2.1). FIX both occurrences to 0.6.0.
  2. Turner 2023 (ref #1) — journal is **Clin Pharmacol Ther 114(6):1220-1237**
     (PMID 37669183), not "Pharmacogenomics J". [corrected inline]
  3. Gaedigk GeT-RM (ref #6) — the GeT-RM CYP2D6 consensus (Table 3) is
     **Gaedigk et al. 2019, J Mol Diagn 21:1034, PMID 31401124** (PMCID
     PMC6854474). The PMID 29134954 in the draft is a different PharmVar
     paper. [corrected inline]
  4. CYP2D6 coords — Methods 2.4 says "chr22:42,126,499-42,130,865"; our code
     uses core 42,126,499-42,130,810 and slices the wider 42,100,000-
     42,160,000 window (to capture CYP2D7 + flanking depth). Recommend
     stating the slice window, not just the core end coordinate.
  5. Production API URL — Appendix A lists product.anukritiai.com as the
     "Production API". That host serves the anukriti-main FRONTEND (Vercel).
     The production API is anukriti-api on Azure Container Apps
     (anukriti-api.agreeablegrass-25e88475.eastus.azurecontainerapps.io),
     now serving POST /cyp2d6/sv-ingest (rev 0000032). Consider adding it.
  6. RESOLVED (v0.7): the warfarin statistical method (Methods 2.7) is
     specified AND the numeric results are now in Results 3.1 —
     Kruskal-Wallis H = 1442.79, df = 2, p < 0.001; Spearman rho = -0.601
     (95% CI -0.621 to -0.580), n = 3,998 determinate-tier dosed patients.
     Computed by anukriti-validation-iwpc/scripts/warfarin_stats.py on the
     real IWPC cohort (PharmGKB PA165291444).

  Verified-correct as written: commit SHAs (d34ed48, a35e4b2, 765a43d,
  0d7275b, 13c1e29 all exist); HG001/HG002 concordance; HG005 exclusion
  rationale; NA12878 SV-blind-entry removal; ENA SRR25583344 + the
  align-first requirement; StarPhase prebuilt-DB gotcha.
  ─────────────────────────────────────────────────────────────────────────
-->

# Deterministic, Population-Aware Pharmacogenomics Screening: Validation of the Anukriti Engine on CYP2D6, DPYD, and Warfarin Cohorts

**Authors:** Abhimanyu R B¹, Aagneye Syam¹, Johan George¹, Atul Alexander¹, Deepak Roshan V G²

¹ Anukriti AI, Kerala, India
² Department of Molecular Biology, Malabar Cancer Centre, Kannur, Kerala, India

**Corresponding author:** Abhimanyu R B — abhimanyu@anukritiai.com

**Status:** Draft v0.8 — June 17, 2026.
**Update (v0.7):** Warfarin numeric statistics computed on the real IWPC
cohort and added to Results 3.1 — Kruskal-Wallis H = 1442.79, df = 2,
p < 0.001; Spearman ρ = −0.601 (95% CI −0.621 to −0.580), n = 3,998. Runner:
`anukriti-validation-iwpc/scripts/warfarin_stats.py`.
**Update (v0.6):** Warfarin statistical method specified in Methods 2.7
(Kruskal-Wallis for group differences + Spearman rank correlation for
dose-tier association; non-normal dose distributions; p < 0.05), replacing
the prior "[method to be confirmed]" placeholder.
**Update (v0.5):** Limitations (§4.5) revised to the verified state — AFR
(NA19317) and EAS (NA18545) structural-variant cells confirmed absent from
both accessible ENA long-read projects and the HPRC Release 2 cohort (only
non-EUR overlap is NA18959, a non-SV EAS sample). These cells are now framed
as a genuine public-data gap rather than a pending rerun.
**Update (v0.4):** HG01190 (SAS) completed on the Azure genomics VM
(SRR25583344 → minimap2 → CYP2D6 slice → StarPhase). Result: **phenotype
concordance 1.000 (Poor Metabolizer, correct), diplotype concordance 0.000**
— StarPhase resolved a different but functionally-equivalent all-no-function
SV configuration (`*68+*4x2/*68+*4`) versus the GeT-RM truth (`*68+*4/*5`).
The SAS equity cell is now populated; the warfarin statistical method is
specified (Methods 2.7) and its numeric results are in Results 3.1.
Remaining open: the AFR/EAS structural-variant cells (public-data gap).

---

## Abstract

Pharmacogenomic (PGx) screening has the potential to prevent drug-induced harm at scale, yet its clinical adoption remains constrained by two persistent gaps: the absence of deterministic, auditable infrastructure for regulatory-grade deployment, and systematic underrepresentation of non-European ancestry populations in validation datasets. Here we present Anukriti, a deterministic pharmacogenomics engine that processes patient genome files to assign star allele diplotypes, metabolizer phenotypes, and CPIC-graded drug recommendations with full provenance tracing across 16 genes and 38+ drugs. Every output cites a versioned guideline, a PharmVar allele definition, and a population frequency source; evidence-insufficient cases are handled through a taxonomy of 31 named refusal rules rather than defaulting to standard assumptions.

We report validation across three domains. First, application to the International Warfarin Pharmacogenomics Consortium dataset (n=5,700) demonstrated that engine-assigned CYP2C9/VKORC1 risk tiers correlated with physician-prescribed stable warfarin doses without access to dose information at inference time; 467 patients (8.2%) were identified as warranting clinical action under CPIC guidelines. Second, DPYD variant calling against the four CPIC Level A actionable variants — with zygosity-based 5-fluorouracil dose guidance and an extended Indian subcontinent variant panel — produced MTB-ready clinical outputs traceable to CPIC and ClinVar evidence grades. Third, CYP2D6 structural variant diplotyping using StarPhase 1.4.2 on GIAB/GeT-RM long-read reference samples achieved diplotype and phenotype concordance of 1.000 on two verified samples (HG002: *2/*4 → IM; HG001/NA12878: *3/*68+*4 → PM), with the hybrid-tandem SV genotype in HG001 — the class of case most likely to fail short-read heuristics — called correctly. A South Asian ancestry sample (HG01190) was subsequently completed on a cloud genomics VM via whole-genome long-read alignment: StarPhase resolved an all-no-function CYP2D6 structural configuration (*68+*4x2/*68+*4) yielding the correct Poor Metabolizer phenotype (phenotype concordance 1.000), though differing from the GeT-RM consensus diplotype (*68+*4/*5) at the structural level — a functionally-equivalent disagreement that illustrates both the value and the current limits of automated SV diplotyping for the equity-critical SAS cell.

Together, these results establish that deterministic, population-aware PGx screening is computationally tractable and clinically interpretable across ancestry groups historically excluded from PGx reference panels. The Anukriti engine is available as an open-source Python library (anukriti-pgx-core, PyPI v0.2.1) and as a production API, providing accessible infrastructure for pre-trial cohort stratification and clinical pharmacogenomics research.

**Keywords:** pharmacogenomics, CYP2D6, DPYD, warfarin, deterministic clinical decision support, population equity, named refusals, CPIC, structural variants, South Asian genomics

---

## 1. Introduction

Pharmacogenomics (PGx) — the study of how genetic variation influences drug response — has been recognized as a cornerstone of precision medicine for over two decades. The Clinical Pharmacogenomics Implementation Consortium (CPIC) has systematically translated pharmacogenomic evidence into actionable clinical guidelines, covering gene-drug pairs across oncology, cardiology, psychiatry, and infectious disease. Despite this progress, the operationalization of PGx at the point of clinical decision-making remains limited, particularly in the context of drug development and pre-trial patient stratification.

A critical and underappreciated barrier is population representativeness. The majority of pharmacogenomic reference data, allele frequency databases, and clinical validation studies have been conducted in populations of European ancestry. Variants of high clinical significance in South Asian, African, and East Asian populations — including DPYD variants prevalent in Indian cohorts and CYP2D6 structural variants common in African ancestry samples — remain poorly characterized in deployed clinical tools. This Eurocentric bias introduces systematic risk: patients from underrepresented populations may be enrolled in trials for which their genetic profiles would have predicted toxicity or non-response, had the screening infrastructure existed to detect it.

Existing computational approaches to PGx screening fall into two broad categories. Rule-based systems such as PharmCAT apply CPIC guidelines deterministically but lack population-aware allele frequency reasoning and do not define explicit refusal conditions for evidence-insufficient cases. Machine learning approaches, including recent LLM-augmented platforms, offer flexible input handling but sacrifice the auditability and reproducibility required for regulatory-grade clinical use — every output must trace to a versioned guideline, not a probability distribution.

Here we describe Anukriti, a deterministic pharmacogenomics infrastructure platform designed to address both limitations. The Anukriti engine processes patient genome files (VCF or BAM), assigns star allele diplotypes and metabolizer phenotypes across 16 genes, and maps each result to CPIC-graded drug recommendations with full provenance — citing guideline version, PMID, and population frequency source for every output. Critically, the engine implements a taxonomy of 31 named refusal rules (R1–R12, V1–V10, U1–U9) that explicitly flag evidence-insufficient cases rather than defaulting to a standard recommendation, preserving the integrity of the clinical decision trail.

We report validation of the engine across three domains: warfarin dose prediction using the International Warfarin Pharmacogenomics Consortium (IWPC) dataset (n=5,700), DPYD-guided 5-fluorouracil safety screening benchmarked against CPIC Level A actionable variants, and CYP2D6 structural variant diplotyping benchmarked against GIAB/GeT-RM reference samples using StarPhase 1.4.2 on long-read data. Together, these validations demonstrate that deterministic, population-aware PGx screening is computationally tractable, clinically interpretable, and equitable across ancestry groups — including South Asian populations historically excluded from PGx reference panels.

---

## 2. Methods

### 2.1 Reference Allele Activity Values

CYP2D6 allele activity values were transcribed verbatim from the PharmVar CYP2D6 SV tutorial (Turner et al. 2023, PMID 37669183) and pinned as a provenance-stamped source table (`cyp2d6_sv_nomenclature.py`). Activity values follow CPIC guidelines, including the March 2023 downgrade of *41 from 0.5 to 0.25. Alleles with uncertain function (*22, *146) are explicitly refused scoring and flagged with a named refusal rather than assigned a default value.

### 2.2 Diplotype Normalization

Raw diplotype strings from external callers were normalized prior to phenotype assignment: CYP2D6 prefix stripping, unicode multiplication sign unification (×→x), suballele suffix collapsing (*4.001→*4), and whitespace removal in tandem alleles. Normalization was implemented in `normalize_diplotype()` and validated against 22 paper-cited test cases.

### 2.3 Structural Variant Truth Set

The truth set was constructed from GIAB/GeT-RM reference samples with authoritative CYP2D6 diplotype calls. Truth diplotypes were sourced exclusively from published GeT-RM consensus data (Gaedigk et al. 2019, Table 3) and Deserranno et al. 2025 to prevent fabrication of reference calls. HG005 (NA24631) was excluded from the scored truth set as no GeT-RM CYP2D6 consensus exists for this sample; Deserranno et al. 2025 marks it N/A.

HG01190 (South Asian, SAS) represents the primary population-equity evaluation cell; its truth diplotype (*68+*4/*5 → Poor Metabolizer) is established and its long-read data is hosted at ENA (SRR25583344, E-MTAB-15248) as unaligned whole-genome ONT FASTQ (~7.6 GB). The remote index-slice technique used for GIAB samples cannot be applied to unindexed FASTQ; a full minimap2 alignment to GRCh38 is required prior to locus extraction. This procedure is documented and turnkey in `scripts/fetch_ena_cyp2d6_longread.sh`.

### 2.4 StarPhase Benchmarking

CYP2D6 diplotype calls were generated using StarPhase 1.4.2 (Holt et al. 2024, PacBio) from targeted long-read sequencing data. StarPhase produces consensus haplotypes directly from BAM input without a separate variant-calling step, collapsing the multi-tool short-read pipeline into a single tool. Output diplotypes were passed through the normalization layer and scored against the truth set using `cyp2d6_starphase_runner.py`.

**Implementation note:** The `pbstarphase build` command (which queries the live CPIC API to construct the reference database) is broken in StarPhase 1.4.2 due to an upstream CPIC API response format change (invalid type: map, expected a sequence). All analyses used the prebuilt PacBio reference database shipped with the repository (`data/v1.4.0/pbstarphase_20250515.json.gz`). This does not affect diplotype calling accuracy; the prebuilt database reflects CPIC allele definitions as of May 2025.

Long-read BAM files for GIAB samples were retrieved using a remote region-slicer (`fetch_giab_cyp2d6_longread.py`), targeting the CYP2D6 locus (chr22:42,126,499–42,130,810 core; 42,100,000–42,160,000 slice window, GRCh38) to minimize data transfer. HG001 locus BAM comprised 273 reads, 1.7 MB, retrieved in approximately 15 seconds.

### 2.5 Phenotype Assignment and Concordance

Activity scores were summed per diplotype and mapped to CPIC metabolizer phenotype bins (Poor/Intermediate/Normal/Rapid/Ultrarapid Metabolizer). Concordance was computed as the fraction of samples where the called phenotype matched the truth phenotype. Uncertain-function alleles were excluded from the concordance denominator and reported separately as named refusals. A pre-existing SV-blind truth entry for NA12878 (*1/*1, Normal Metabolizer — the heuristic call) was removed from the truth set and replaced with the authoritative GeT-RM SV diplotype (*3/*68+*4, Poor Metabolizer) to prevent artifactual concordance inflation.

### 2.6 DPYD Variant Calling and Clinical Action Tiers

DPYD variant calling targeted the four CPIC Level A actionable variants (rs3918290, rs55886062, rs67376798, rs56038477/rs75017182) plus five Indian subcontinent variants of interest (rs1801265, rs2297595, rs1801159, rs1801158, rs1801160). Zygosity was determined for each variant and mapped to a clinical action tier: homozygous high-risk → contraindicate 5-fluorouracil; heterozygous → 50% dose reduction; homozygous reference → standard dosing. ClinVar pathogenicity annotations were integrated for variants below CPIC evidence grade, with named refusals applied per rules R7–R9.

### 2.7 Warfarin Cohort Analysis

The IWPC dataset (n=5,700, publicly available) was processed through the Anukriti CYP2C9/VKORC1 calling pipeline. Each patient was assigned a risk tier (high sensitivity, standard, reduced sensitivity) based on diplotype. Risk tiers were compared against physician-prescribed stable warfarin doses without dose information available at inference time. Correlation between engine-assigned risk tiers and stable warfarin dose was assessed using Kruskal-Wallis test for group differences and Spearman rank correlation for dose-tier association. Warfarin dose distributions were not assumed to be normal. Significance threshold was set at p < 0.05.

---

## 3. Results

### 3.1 Warfarin Dose Prediction — IWPC Cohort (n=5,700)

To validate the engine's clinical risk stratification, we applied the Anukriti CYP2C9/VKORC1 calling pipeline to the IWPC warfarin dataset (n=5,700 patients across 9 countries). Each patient was assigned a metabolizer phenotype and mapped to a CPIC-graded dose recommendation tier (standard dose, reduced dose, high sensitivity). Risk tiers were compared against physician-prescribed stable warfarin doses without the engine having access to dose information at inference time.

Engine-assigned risk tiers correlated significantly with prescribed dose across the cohort. Among the 3,998 patients with both a determinate risk tier and a recorded stable dose (172 lacked a dose; the remainder were assigned an indeterminate tier owing to missing genotype data and excluded from the association analysis), median prescribed warfarin dose decreased monotonically across tiers: low-sensitivity 42.5, standard 32.5, and high-sensitivity 21.0 mg/week. A Kruskal-Wallis test confirmed a significant difference in dose distribution across the three tiers (H = 1442.79, df = 2, p < 0.001), and Spearman rank correlation between ordinal risk tier (low < standard < high sensitivity) and prescribed dose was ρ = −0.601 (95% CI −0.621 to −0.580, p < 0.001; n = 3,998) — a moderate-to-strong negative association in the expected direction, i.e. higher-sensitivity tiers received lower prescribed doses, consistent with established PGx-guided dosing expectations. Of the full 5,700 patients processed, 467 (8.2%) were assigned a risk tier that would have warranted clinical action under CPIC guidelines — representing patients who may have been enrolled in a standard-dose trial arm without PGx screening.

Named refusals were issued for patients with missing genotype data or ambiguous diplotypes, consistent with refusal rules V1–V3 (missing variant data) and U1–U2 (ambiguous phasing). Refusal rates by ancestry group are reported in Supplementary Table 1.

### 3.2 DPYD Variant Calling and 5-Fluorouracil Safety Screening

DPYD variant calling was validated against the four CPIC Level A actionable variants: rs3918290 (*2A), rs55886062 (*13), rs67376798 (c.2846A>T), and the HapB3 composite (rs56038477/rs75017182). Zygosity-based clinical action tiers were assigned deterministically: homozygous carriers of *2A or *13 were flagged for 5-fluorouracil contraindication; heterozygous carriers were assigned a 50% dose reduction recommendation, consistent with CPIC guidelines (Henricks et al. 2018, PMID 29152729).

Indian subcontinent variants of interest — rs1801265 (*9A), rs2297595 (M166V), rs1801159 (*5), rs1801158 (*4), rs1801160 (*6) — were included in the variant panel and reported with population frequency annotations from the SAS super-population reference. ClinVar pathogenicity annotations were integrated for variants not yet assigned CPIC evidence grades, with explicit uncertainty flags applied per refusal rules R7–R9 (insufficient evidence tier).

Clinical output was formatted for Molecular Tumour Board (MTB) submission, including variant identifier, zygosity, phenotype, CPIC recommendation, evidence grade, and provenance stamp (guideline version + PMID).

### 3.3 CYP2D6 Structural Variant Benchmarking — GIAB/GeT-RM Reference Samples

**Concordance results:**

| Sample | Population | Reads / size | StarPhase call | GeT-RM truth | Diplotype concordance | Phenotype concordance |
|--------|-----------|-------------|---------------|-------------|----------------------|-----------------------|
| HG002 | Ashkenazi Jewish | 45 reads | *2/*4 | *2.001/*4.014 | ✅ 1.000 | ✅ IM |
| HG001 (NA12878) | CEU (EUR) | 273 reads / 1.7 MB | *3/*68+*4 | *3/*68+*4 | ✅ 1.000 | ✅ PM |
| HG01190 | SAS | 373 reads | *68+*4x2/*68+*4 | *68+*4/*5 → PM | ✗ 0.000 (diff. SV config) | ✅ PM (1.000) |
| *22 carrier | — | — | — | uncertain function | REFUSED (U4) | named refusal ✅ |
| HG005 (NA24631) | Chinese | — | not scored | no GeT-RM consensus | excluded | excluded |

**Overall (3 scored samples): phenotype concordance 1.000; diplotype concordance 0.667 (2/3)**
*(HG002 + HG001 match diplotype + phenotype; HG01190 matches phenotype (PM) but StarPhase resolved a different all-no-function SV configuration than the GeT-RM diplotype. *22 refusal correct by design; HG005 excluded — no GeT-RM consensus.)*

The most significant result is HG001 (NA12878). This sample carries a hybrid-tandem structural variant diplotype (*3/*68+*4) — a configuration that the legacy short-read heuristic scored at 0.333 (SV-blind, calling *1/*1 Normal Metabolizer). StarPhase called the full SV diplotype correctly, resolving to Poor Metabolizer, matching the authoritative Gaedigk et al. 2019 GeT-RM truth. The locus slice was retrieved in 15 seconds (273 reads, 1.7 MB); StarPhase and scoring ran in minutes. This demonstrates that hybrid-tandem SV cases — the class most likely to fail short-read callers — are handled correctly by the StarPhase → normalize → ingest chain.

A pre-existing SV-blind truth entry for NA12878 (*1/*1, Normal Metabolizer) was identified and removed from the truth set during this analysis; the replacement with the authoritative SV diplotype is documented in commit 765a43d. HG005 was excluded after a full scan of Gaedigk et al. 2019 Tables 3 and 4 confirmed no GeT-RM CYP2D6 consensus for NA24631.

The South Asian equity cell (HG01190) was completed on a dedicated Azure genomics VM (Standard_D16s_v5, Ubuntu 22.04): the ENA FASTQ (SRR25583344, ~7.6 GB) was aligned whole-genome to GRCh38 with minimap2 (-ax map-ont), the CYP2D6 locus sliced (373 reads), and StarPhase run. StarPhase called *68+*4x2/*68+*4 — a tandem-duplication configuration of two all-no-function alleles — resolving to **Poor Metabolizer**, which **matches the GeT-RM phenotype** (truth *68+*4/*5 → PM). The two diplotypes disagree at the structural level (StarPhase placed the *68+*4 hybrid-tandem on both haplotypes rather than opposite a *5 deletion), so diplotype concordance for this sample is 0.000 while phenotype concordance is 1.000. Because all constituent alleles in both the called and the truth diplotype are no-function (*68 = 0, *4 = 0, *5 = 0), the clinically actionable output — Poor Metabolizer, warranting CYP2D6-substrate avoidance — is identical. This is an honest and instructive result: for the equity-critical SAS sample, automated SV diplotyping reached the correct clinical phenotype but not the exact structural call, underscoring that phenotype-level concordance and diplotype-level concordance are distinct metrics and that the former is the clinically decisive one. It also flags structural-call divergence on complex hybrid-tandem/deletion configurations as a target for caller refinement and orthogonal confirmation.

---

## 4. Discussion

### 4.1 Deterministic Infrastructure as a Regulatory Primitive

The results demonstrate that pharmacogenomics screening can be implemented deterministically — without probabilistic inference — across three clinically distinct gene-drug pairs, while maintaining full auditability at the variant, diplotype, phenotype, and recommendation layers. Each output produced by the Anukriti engine traces to a versioned CPIC guideline, a PharmVar allele definition, and a population frequency source, satisfying the provenance requirements of 21 CFR Part 11 audit trails and FHIR R5 clinical data exchange standards.

This stands in contrast to ML-augmented PGx platforms, which offer flexible input handling at the cost of output reproducibility. For clinical trial use — where a sponsor must be able to defend every enrollment decision to a regulator — deterministic infrastructure is not a design preference but a compliance requirement. The named refusal taxonomy (31 rules across R, V, and U series) formalizes the boundary between actionable evidence and insufficient evidence, a distinction that probabilistic systems cannot make cleanly.

### 4.2 Hybrid-Tandem SV Resolution as a Clinical Safety Requirement

The HG001 result warrants specific discussion. NA12878 is one of the most widely used reference samples in genomics, and its CYP2D6 genotype (*3/*68+*4) represents a class of hybrid-tandem structural variant that is systematically miscalled by short-read heuristic approaches. A tool that calls NA12878 as *1/*1 Normal Metabolizer — the SV-blind answer — would classify this patient as requiring no dose adjustment, when in fact the correct phenotype is Poor Metabolizer, warranting significant drug avoidance or dose reduction for CYP2D6-substrate drugs.

This is not a theoretical failure mode. Short-read WGS pipelines without dedicated SV callers, and legacy heuristic engines without star-allele-aware normalization, will systematically produce this error on SV-containing samples. The StarPhase → normalize → ingest chain resolves it correctly. In a pre-trial screening context, the difference between Normal Metabolizer and Poor Metabolizer for a CYP2D6 substrate drug (codeine, tramadol, tamoxifen) is the difference between enrolling and not enrolling a patient at elevated toxicity risk.

### 4.3 Population Equity as a First-Class Design Constraint

The inclusion of HG01190 (South Asian ancestry) as an explicit validation cell reflects a deliberate design principle: population representativeness is not a post-hoc audit but an input constraint. The SAS super-population covers approximately 1.9 billion people — the largest single ancestry group on Earth — yet remains systematically underrepresented in published PGx validation studies. The DPYD variant panel presented here includes five Indian subcontinent variants not covered by the standard four-variant CPIC panel, each with SAS-specific population frequency annotations.

The Eurocentric bias in existing PGx infrastructure has direct clinical consequences. A tool validated only on EUR ancestry samples will systematically misclassify SAS patients — either over-flagging benign variants as pathogenic or, more dangerously, missing population-enriched risk variants entirely. Anukriti addresses this by treating ancestry as a closed enum input — one of five CPIC super-populations with sub-population granularity — rather than optional metadata.

### 4.4 Honest Refusals as a Clinical Safety Feature

The named refusal on the *22 uncertain-function allele (rule U4) illustrates a core design principle: the engine will not fabricate clinical certainty. Assigning *22 an activity score would require inference beyond the evidence; the named refusal communicates this explicitly — the variant was detected, the evidence is insufficient, and the rule governing that refusal is documented and version-controlled.

This contrasts with tools that default uncertain cases to a normal metabolizer assumption — a practice that creates the appearance of completeness at the cost of patient safety. In a pre-trial screening context, a false normal is more dangerous than a flagged uncertainty.

### 4.5 Limitations and Future Directions

The CYP2D6 SV benchmarking now covers three scored samples (HG002, HG001, and the SAS cell HG01190). HG01190 reached the correct Poor Metabolizer phenotype but diverged from the GeT-RM consensus at the structural-diplotype level (a functionally-equivalent all-no-function configuration); confirming the exact structural call would require orthogonal long-range validation. The two structural-variant truth samples that would extend the table to African and East Asian ancestry — AFR: NA19317 (*5/*5 → Poor Metabolizer) and EAS: NA18545 (*5/*36x2+*10x2 → Intermediate Metabolizer), both gene-deletion/hybrid genotypes from Gaedigk et al. 2019 — have no usable public whole-genome long-read data available. The only ENA ONT/PacBio runs located for them are an empty PromethION run (NA19317, 17 reads) and a low-coverage whole-genome-amplified PacBio run (NA18545, ~0.04× genome), neither of which yields CYP2D6 locus coverage. We further verified that neither sample is included in the Human Pangenome Reference Consortium (HPRC) Release 2 long-read cohort (232 diverse 1000 Genomes individuals, each with ~60× PacBio HiFi and ~30× Oxford Nanopore): cross-referencing the full HPRC sequencing index against the GeT-RM CYP2D6 truth set, only one non-European truth sample overlaps the cohort (NA18959, EAS, *1/*1 → Normal Metabolizer), and it is a non-structural-variant genotype that does not exercise the SV-resolution capability under evaluation. Consequently, the AFR and EAS structural-variant cells remain a genuine gap in the cross-ancestry SV concordance table — not a deferred rerun of the present pipeline, but a limitation imposed by the absence of suitable public long-read reference data for these specific structural-variant truth samples. Closing them would require either a future public long-read release covering NA19317/NA18545, or the adoption of alternative AFR/EAS samples that carry both an independently published CYP2D6 structural-variant truth call and accessible whole-genome long-read data. The IWPC warfarin cohort, while large (n=5,700), is skewed toward European and East Asian ancestry; SAS representation is limited. Population frequency data for genes beyond CYP2D6 and CYP2C19 remain to be populated from IndiGen and gnomAD SAS subsets.

Future work will expand the gene panel to 25+ drugs optimized for South Asian populations, integrate ClinVar pathogenicity tiers for variants below CPIC evidence grade, validate the MTB-ready output format in a prospective clinical setting at Malabar Cancer Centre, and extend the cross-ancestry concordance table to African and East Asian structural-variant cells as suitable public long-read reference data for those samples becomes available.

---

## References

1. Turner AJ et al. PharmVar Tutorial on CYP2D6 Structural Variation Testing and Recommendations on Reporting. *Clin Pharmacol Ther.* 2023;114(6):1220-1237. PMID 37669183. [corrected — was listed as Pharmacogenomics J]
2. Henricks LM et al. DPYD genotype-guided dose individualisation of fluoropyrimidine therapy in patients with cancer. *Lancet Oncol.* 2018. PMID 29152729.
3. Holt JM et al. StarPhase: a diplotyper for pharmacogenomic genes. *bioRxiv.* 2024.
4. Deserranno K et al. Benchmarking long-read CYP2D6 structural variant calling. *Front Pharmacol.* 2025.
5. Gan W et al. Targeted adaptive sampling for pharmacogenomic gene panels. *medRxiv.* 2025.
6. Gaedigk A et al. Characterization of Reference Materials for Genetic Testing of CYP2D6 Alleles: A GeT-RM Collaborative Project. *J Mol Diagn.* 2019;21(6):1034-1052. PMID 31401124. [corrected — was listed as PMID 29134954; this is the GeT-RM CYP2D6 consensus, Table 3]
7. The International Warfarin Pharmacogenomics Consortium. Estimation of the warfarin dose with clinical and pharmacogenomic data. *NEJM.* 2009. PMID 19228618.
8. CPIC Guidelines. cpicpgx.org. Accessed June 2026.
9. PharmVar. pharmvar.org. Accessed June 2026.

---

## Acknowledgements

The authors thank Dr. Deepak Roshan V G (Malabar Cancer Centre) for clinical input on DPYD oncology workflows and MTB output requirements, Andrea Gaedigk (Children's Mercy Kansas City / PharmVar) and Andrew Somogyi (IUPHAR) for expert guidance on pharmacogenomics nomenclature standards, and the GIAB consortium for public release of reference sample datasets. NA12878 GeT-RM truth data was sourced from Gaedigk et al. 2019 Table 3.

---

## Appendix A — Data Availability and Reproducibility

- anukriti-pgx-core: https://pypi.org/project/anukriti-pgx-core/ (**v0.6.0** — CYP2D6 SV ingestion + DPYD clinical-action tier; v0.2.1 in the earlier draft was incorrect)
- Production API: https://anukriti-api.agreeablegrass-25e88475.eastus.azurecontainerapps.io (Azure Container Apps, rev 0000032; `POST /cyp2d6/sv-ingest` live). Frontend: https://product.anukritiai.com (Vercel)
- GIAB long-read region slicer: `fetch_giab_cyp2d6_longread.py` (commit d34ed48)
- ENA FASTQ alignment runner: `scripts/fetch_ena_cyp2d6_longread.sh` (HG01190, SRR25583344, minimap2 -ax map-ont)
- StarPhase setup procedure: `STARPHASE_SETUP.md` (commit 13c1e29, anukriti_docs repo)
- StarPhase runner + scorer: `cyp2d6_starphase_runner.py` (commit a35e4b2)
- StarPhase version: 1.4.2 | Reference DB: pbstarphase_20250515.json.gz (prebuilt, v1.4.0)
- Archived validation artifacts (BAM slices, StarPhase JSON calls, score files, pinned reference DB): Azure Blob Storage container `giab-cyp2d6-artifacts` (account `anukritilrs79730`, RG `anukriti-lrs-01`, `centralindia`), base URL `https://anukritilrs79730.blob.core.windows.net/giab-cyp2d6-artifacts/`. Backup procedure + per-file manifest: `GIAB_ARTIFACT_BACKUP.md` (anukriti_docs). Container is private; reviewer access via read-only SAS or DOI mirror on request.
- Citable data deposit (StarPhase call JSONs, score, checksums, scoring script): Zenodo **https://doi.org/10.5281/zenodo.20727790** (CC-BY-4.0; BAM/BAI excluded — see source accessions below)
- Public validation repository (scoring script + StarPhase outputs + provenance): **https://github.com/AnukritiAi-hq/anukriti-validation** (Apache 2.0)
- Source read data (excluded from the deposit/repo): HG01190 — ENA `SRR25583344` (ArrayExpress `E-MTAB-15248`); HG001/HG002 — GIAB FTP (`https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/`)

---

## Appendix B — Commit Log (CYP2D6 Rung-2)

| Commit | Repo | Description |
|--------|------|-------------|
| d34ed48 | anukriti | fetch_giab_cyp2d6_longread.py — remote region slicer, HG002 verified |
| a35e4b2 | anukriti | StarPhase gene_details schema parser; HG002 e2e verified; 46 tests pass |
| 765a43d | anukriti | HG001 truth (*3/*68+*4 → PM, Gaedigk 2019); ENA runner script; NA12878 SV-blind entry removed; 46 tests pass |
| 0d7275b | anukriti_docs | STARPHASE_SETUP.md — verified <30-min procedure with prebuilt-DB gotcha |
| 13c1e29 | anukriti_docs | STARPHASE_SETUP.md updated: HG001 result + ENA quirk documented |
| 26e6240 | anukriti-pgx-core | release v0.6.0 — CYP2D6 SV ingestion migrated into the engine (PyPI) |
| dbcc0ef | anukriti-api | POST /cyp2d6/sv-ingest endpoint (deterministic, pgx-core 0.6.0) |

---

*Document status: Draft v0.8 | June 17, 2026*
*HG01190 SAS cell completed on Azure VM (phenotype 1.000 / diplotype divergent). Remaining blank: warfarin statistical method confirmation.*
*Three-sample cross-ancestry concordance table populated (EUR ×2, SAS ×1). AFR (NA19317) and EAS (NA18545) structural-variant cells remain open: verified absent from both accessible ENA long-read projects and the HPRC Release 2 cohort — a genuine public-data gap, not a pending rerun.*
