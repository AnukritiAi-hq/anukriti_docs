# Papers for synthetic patients and the DPYD/DPD/5-FU engine

Retrieved/checked 6 September 2026. Start with the direct 5-FU and DPYD sources for
oncology implementation, then the genome-generation methods. See the
[full research plan](../../research/synthetic-patients/IMPLEMENTATION_PLAN.md).

## Requested genome-generation papers

1. **Wharrie et al. 2023 — HAPNEST: efficient, large-scale generation and evaluation
   of synthetic datasets for genotypes and phenotypes.** Bioinformatics 39(9),
   btad535. [DOI](https://doi.org/10.1093/bioinformatics/btad535) ·
   [saved PDF](Wharrie-2023-Bioinformatics-HAPNEST.pdf) ·
   [university source PDF](https://acris.aalto.fi/ws/portalfiles/portal/125294719/HAPNEST_efficient_large_scale_generation_and_evaluation_of_synthetic_datasets_for_genotypes_and_phenotypes.pdf) ·
   [code](https://github.com/intervene-EU-H2020/synthetic_data).
   Read genotype generation and evaluation. Article: CC BY 4.0; code: GPLv3.

2. **Caballero et al. 2019 — Crossover interference and sex-specific genetic maps
   shape identical by descent sharing in close relatives.** PLOS Genetics 15(12),
   e1007979. This is the **Ped-sim paper**.
   [DOI](https://doi.org/10.1371/journal.pgen.1007979) ·
   [saved PDF](Caballero-2019-PLOSGenetics-Ped-sim.pdf) ·
   [publisher PDF](https://journals.plos.org/plosgenetics/article/file?id=10.1371/journal.pgen.1007979&type=printable) ·
   [code](https://github.com/williamslab/ped-sim).
   Read crossover modeling, map assumptions and real-relative evaluation.
   Article: Creative Commons Attribution, as printed; code: GPLv3.

3. **Haller, Nelson, Rodrigues and Messer 2025 — SimHumanity: Using SLiM 5.0 to run
   whole-genome simulations of human evolution.** Human Population Genetics and
   Genomics 5(4):0006. Published 15 October 2025.
   [DOI](https://doi.org/10.47248/hpgg2505040006) ·
   [saved PDF](Haller-2025-HPGG-SimHumanity.pdf) ·
   [author PDF](https://benhaller.com/pubs/HallerEtAl2025.pdf) ·
   [code](https://github.com/bhaller/SimHumanity).
   Read the three model definitions and genetic-structure limitations.
   Article: CC BY 4.0; model code: MIT.

## Functional assays: CYP2C9 precedent and direct DPYD evidence

4. **Amorosi et al. 2021 — Massively parallel characterization of CYP2C9 variant
   enzyme activity and abundance.** American Journal of Human Genetics 108(9),
   1735–1751. [DOI](https://doi.org/10.1016/j.ajhg.2021.07.001) ·
   [PubMed](https://pubmed.ncbi.nlm.nih.gov/34314704/) ·
   [author-hosted PDF](https://dunham.gs.washington.edu/Amorosi.pdf) ·
   [data/code](https://github.com/dunhamlab/CYP2C9).
   Read click-seq versus VAMP-seq, orthogonal assays and data availability.
   This provides 6,142 activity and 6,370 abundance measurements; it is a design
   precedent, not a DPD parameter dataset. The author PDF is linked rather than
   mirrored because redistribution permission was not established here.

5. **Offer et al. 2014 — Comparative functional analysis of DPYD variants of
   potential clinical relevance to dihydropyrimidine dehydrogenase activity.**
   [DOI](https://doi.org/10.1158/0008-5472.CAN-13-2482) ·
   [PubMed](https://pubmed.ncbi.nlm.nih.gov/24648345/) ·
   [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC4012613/).
   Read Supplementary Table S2 and expression normalization; reconcile against
   the incomplete local extraction before using it as training evidence.

6. **Hishinuma et al. 2022 — Importance of Rare DPYD Genetic Polymorphisms for
   5-Fluorouracil Therapy in the Japanese Population.** Frontiers in Pharmacology 13,
   930470. [DOI](https://doi.org/10.3389/fphar.2022.930470) ·
   [saved PDF](Hishinuma-2022-FrontPharmacol-DPYD-Kinetics.pdf) ·
   [publisher PDF](https://www.frontiersin.org/journals/pharmacology/articles/10.3389/fphar.2022.930470/pdf).
   Read methods and Table 4 for assay-specific kinetics. Article: CC BY.

7. **Sudo et al. 2026 — Functional Analysis of DPYD Variants Associated With
   5-Fluorouracil-Based Anticancer Drug Toxicity in Cancer Patients.**
   Journal of Clinical Pharmacy and Therapeutics, 2026, 3886738.
   [Primary article](https://doi.org/10.1155/jcpt/3886738).
   Read assay conditions, dimerization and patient-PBMC comparison; preserve
   study-specific endpoints and uncertainty.

## Direct 5-FU model and clinical-measurement papers

8. **Marok et al. 2024 — Personalized Chronomodulated 5-Fluorouracil Treatment:
   A Physiologically-Based Pharmacokinetic Precision Dosing Approach for
   Optimizing Cancer Therapy.** Clinical Pharmacology & Therapeutics.
   [DOI/version of record](https://doi.org/10.1002/cpt.3181) ·
   [university page and downloadable PDF](https://wrap.warwick.ac.uk/id/eprint/182490/) ·
   [model projects](https://github.com/Clinical-Pharmacy-Saarland-University/5-FU-PBPK-Model).
   Read methods, model evaluation and supplementary study/parameter tables.
   The university identifies the article as CC BY-NC 4.0; we link the official
   copy rather than republish it in the company repository. Model-file licensing
   is a separate unresolved item; public availability alone does not settle it.

9. **Briki et al. 2026 — Model-based meta-analysis of individual patient data for
   the characterization of intravenous 5-fluorouracil population pharmacokinetics.**
   [DOI](https://doi.org/10.1007/s00280-026-04885-x) ·
   [PubMed](https://pubmed.ncbi.nlm.nih.gov/42283826/).
   Candidate reduced population-PK comparator; executable source/covariance
   availability still needs verification.

10. **Beumer et al. 2019 — IATDMCT recommendations for 5-FU therapeutic drug monitoring.**
    [DOI](https://doi.org/10.1002/cpt.1124) ·
    [PubMed](https://pubmed.ncbi.nlm.nih.gov/29923599/) ·
    [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC6309286/).
    Read regimen applicability, sampling and exposure definitions.

11. **Fiebrich-Westra et al. 2025 — Precision Treatment of Patients With GI Cancer
    Using Pre-emptive DPYD Genotyping/Phenotyping Plus Pharmacokinetic-Guided
    Dosing of 5-Fluorouracil.**
    [Primary article](https://doi.org/10.1200/PO-25-00062) ·
    [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC12160085/).
    Read the 46-hour infusion methods, concentration assay/sample handling and
    cycle-specific assessment protocol.

## PK-Sim documentation to read with the papers

- [Population generation algorithm](https://docs.open-systems-pharmacology.org/v12/working-with-pk-sim/pk-sim-documentation/pk-sim-creating-populations)
- [Expression profiles](https://docs.open-systems-pharmacology.org/working-with-pk-sim/pk-sim-documentation/pk-sim-expression-profile)
- [Administration protocols](https://docs.open-systems-pharmacology.org/v12/working-with-pk-sim/pk-sim-documentation/pk-sim-administration-protocols)
- [OSPSuite-R installation](https://www.open-systems-pharmacology.org/OSPSuite-R/)
- [Bundled PK-Sim dependencies correction](https://www.open-systems-pharmacology.org/OSPSuite-R/articles/PKSim-installation.html)
- [Run populations in R](https://www.open-systems-pharmacology.org/OSPSuite-R/articles/create-run-population.html)
- [Version/API audit and copy-ready examples](../../research/synthetic-patients/EVIDENCE_REGISTER.md)

The four saved PDFs are unmodified copies with attribution and source links
above. Their original Creative Commons terms apply; the repository's general
Apache license does not replace the articles' licenses. No author endorsement
is implied. [Download hashes and provenance](manifest.json) record the copies.
