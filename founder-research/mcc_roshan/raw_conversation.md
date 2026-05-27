# MCC / Dr. Roshan — Raw Conversation Notes

Date: 2026-05-27
Context: Founder discovery call with research-center oncology clinician.
Topic: DPYD testing, 5-FU toxicity, PCR-vs-NGS workflow, and MCC collaboration.

## Call Transcript — Key Exchanges

### Opening

Abhimanyu introduced Anukriti as a deterministic pharmacogenomics engine that runs before clinical drug trials or treatment decisions to identify patients at genetic risk from specific drugs. Primary focus for MCC: DPYD and fluoropyrimidine toxicity.

### MCC's current setup

Dr. Roshan said MCC currently uses real-time PCR for DPYD testing, not NGS. They test 7 known polymorphisms per patient. They have tested around 400-500 patients so far. DPYD positivity is relatively low in their cohort. Toxicity data is collected over roughly 7 months to 1 year per patient because true drug-dependent toxicity needs treatment follow-up and dose-context review.

His assistant asked about VCF files and whether NGS covers DPYD.

### NGS vs PCR

Abhimanyu clarified:

- NGS reads the broader DPYD gene and can catch known plus novel variants.
- PCR targets known positions; it is fast, cheaper, and already in MCC's workflow.
- Anukriti does not require VCF input for MCC. Real-time PCR variant calls can be ingested directly as structured present/absent or genotype calls.
- The same engine can handle NGS-derived VCF later if MCC moves in that direction.

### Drug toxicity vs drug effectiveness

Dr. Roshan asked whether the output is drug intoxication/toxicity or whether the drug works.

Abhimanyu clarified:

- Anukriti answers the safety/toxicity question: can the patient's body safely process 5-FU, capecitabine, or tegafur?
- Drug effectiveness is different: will the tumor respond to the drug? That depends on tumor biology and somatic mutations, not only germline DPYD.
- Anukriti is the safety gate before or alongside the efficacy decision.

Abhimanyu also said he comes from an engineering background, so his wording may not be clinically precise. Dr. Roshan replied that this is why they are speaking in layman terms: MCC wants to understand what has been built and then help attach the correct clinical terminology. The input and output are different: a drug can be effective against cancer and still toxic to the patient.

### What Dr. Roshan was actually asking

He has 400-500 patients. MCC tested DPYD. Some patients developed toxicity and some did not. He wants to know:

> Which specific DPYD variants in Anukriti's data predict toxicity, and are those inside or outside MCC's current 7-variant PCR panel?

This is a clinical mapping question, not primarily a technology question.

### Indian vs non-Indian DPYD variants

Dr. Roshan asked for the full list of DPYD variants identified in Indian and non-Indian populations so MCC can map against their existing data. If Anukriti provides the variant list, MCC can compare it to their own PCR panel and check whether toxicity-positive patients have variants outside their current assay.

He specifically raised the possibility that NGS may find additional DPYD mutations, but emphasized that toxicity outcome labeling takes months because patients receive treatment, may have dose changes, and need proper follow-up to determine whether toxicity is truly drug-dependent.

### Why DPYD was chosen

Abhimanyu gave three reasons:

1. Risk is catastrophic: poor metabolizers can die, not just experience ordinary side effects.
2. Intervention is simple: reduce dose or switch drug.
3. This is not standard practice across India, leaving a real implementation gap.

### South Asian data gap

Abhimanyu disclosed that South Asian DPYD frequency and outcome-linked evidence is thin. Anukriti should not return Eurocentric confident answers when the evidence is not transferable. MCC's 400-500 patient cohort with outcome data could become one of the most important Indian DPYD genotype-to-toxicity datasets.

### How Anukriti processes PCR data

PCR output -> structured variant call table -> Anukriti maps to diplotype -> metabolizer phenotype -> CPIC dose recommendation plus population/evidence flag plus audit trail.

No new equipment is needed at MCC. VCF is not required for the first collaboration phase.

### Collaboration proposed

MCC shares anonymized PCR variant calls and toxicity outcome data for 400-500 patients. Anukriti classifies all patients and cross-references genotype calls with toxicity outcomes.

Possible result: Indian DPYD variant-to-toxicity frequency paper, with MCC as lead clinical institution and Anukriti as analytical engine.

### Outcome

Level 1 complete. Dr. Roshan was receptive to collaboration. Follow-up needed the same day:

- DPYD variant table.
- PCR integration workflow.
- Clear description of what MCC gets from Anukriti.
- Level 2 meeting ask.

## Follow-up question to answer

The most important number to get at Level 2:

> How many of the 400-500 patients developed Grade 3+ toxicity despite testing negative on all 7 DPYD variants in MCC's current PCR panel?

That number is the discovery signal. If it is non-zero, those cases may contain Indian-specific or under-tested variants that standard panels miss. NGS on that subset is the paper.
