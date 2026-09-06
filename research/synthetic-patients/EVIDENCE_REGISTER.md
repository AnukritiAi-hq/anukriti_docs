# Evidence register and documented integration surfaces

Research checked 6 September 2026. Primary papers and official software
documentation were used. A documented API is not an executed integration: the
new external simulators and OSP model were not installed or run in this planning
pass. The existing regional prototype is the only executed generator here.

## Papers and data: source IDs used by the plan

| ID | Primary source | Material examined / reuse target |
|---|---|---|
| G01 | [Wharrie 2023, HAPNEST](https://doi.org/10.1093/bioinformatics/btad535) | Methods, evaluation, common-variant scope; population-generation baseline |
| G02 | [Caballero 2019, Ped-sim](https://doi.org/10.1371/journal.pgen.1007979) | Crossover interference, sex-specific maps and IBD comparisons |
| G03 | [Haller 2025, SimHumanity](https://doi.org/10.47248/hpgg2505040006) | Three forward-simulation models, whole-genome configuration, limitations |
| G04 | [Haptools](https://pmc.ncbi.nlm.nih.gov/articles/PMC9991497/) | Official implementation/docs also examined; admixture/phase baseline |
| G05 | [IGSR high-coverage panel](https://internationalgenome.org/data-portal/data-collections/1000genomes_30x/) | GRCh38 phased SNV/INDEL/SV resources; 3,202 participants including relatives |
| G06 | [IGSR relatedness FAQ](https://www.internationalgenome.org/faq/which-datasets-include-related-individuals/) | Original 2,504 plus 698 related individuals; family-aware partitions |
| G07 | [Arciero 2025, Himalayan genomes](https://doi.org/10.1016/j.cub.2025.06.048) | Article/author methods PDF; 87 individuals/16 populations, six Bhutanese populations |
| G08 | [EGA EGAD00001011358](https://ega-archive.org/datasets/EGAD00001011358) | Controlled-access 60-person subset; access and derivative-use terms unresolved |
| G09 | [Dorji, Bhutan PGx](https://pubmed.ncbi.nlm.nih.gov/32004143/) | Abstract: 443 samples, limited marker panel; historical calibration candidate, not DPYD evidence |
| G10 | [HapB3 causal/proxy study](https://doi.org/10.1111/cts.13699) | Incomplete linkage; preserve direct versus inferred evidence |
| G11 | [DPYD genotyping consensus, 2024](https://doi.org/10.1016/j.jmoldx.2024.05.015) | Variant coverage, causal/proxy handling; [open author PDF](https://pure.eur.nl/ws/portalfiles/portal/168131215/DPYD_Genotyping_Recommendations.pdf) |
| G12 | [Finnish DPYD exon-4 deletion](https://doi.org/10.1111/bcpt.70011) | Publisher methods/discussion: local structural variation; no frequency transfer to South Asia |
| F01 | [Offer 2014](https://pubmed.ncbi.nlm.nih.gov/24648345/) · [DOI](https://doi.org/10.1158/0008-5472.CAN-13-2482) | 80 DPYD variants; Supplementary Table S2 extraction target; local CSV is incomplete |
| F02 | [Hishinuma 2022](https://doi.org/10.3389/fphar.2022.930470) | Full methods/results, Table 4 kinetic data and assay normalization |
| F03 | [Sudo 2026](https://doi.org/10.1155/jcpt/3886738) | Seven rare variants, activity/abundance/dimerization and selected PBMC evidence |
| F04 | [Amorosi 2021, CYP2C9](https://pubmed.ncbi.nlm.nih.gov/34314704/) · [DOI](https://doi.org/10.1016/j.ajhg.2021.07.001) | Abstract, figures and code/data locations; assay-design precedent |
| F05 | [Van Kuilenburg 2012](https://pubmed.ncbi.nlm.nih.gov/22339448/) · [DOI](https://doi.org/10.1007/BF03257473) | Human variant-group PK calibration; 30 carriers/18 controls |
| P01 | [Marok 2024, 5-FU/uracil PBPK](https://doi.org/10.1002/cpt.3181) | Methods, evaluation, results/discussion; supplementary numerical extraction still required |
| P02 | [5-FU model files](https://github.com/Clinical-Pharmacy-Saarland-University/5-FU-PBPK-Model/tree/e4ba27100d17336a53c3465b873e224afa90624a) | Four actual `.pksim5` files; source states PK-Sim 9.1; model-file license unresolved |
| P03 | [Briki 2026 meta-analysis](https://pubmed.ncbi.nlm.nih.gov/42283826/) · [DOI](https://doi.org/10.1007/s00280-026-04885-x) | Abstract: 726 patients/2,332 concentrations; code and covariance availability unconfirmed |
| P04 | [Mielke 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12114802/) | Eight-compartment rxode2 model; DPYD-deficient group excluded; supplemental code needs retrieval |
| P05 | [Wang 2023 capecitabine model](https://pubmed.ncbi.nlm.nih.gov/37610618/) · [DOI](https://doi.org/10.1007/s11095-023-03585-y) | Primary abstract; executable model availability not confirmed |
| P06 | [Loer 2022 clopidogrel](https://pubmed.ncbi.nlm.nih.gov/35631502/) · [model](https://github.com/Open-Systems-Pharmacology/Clopidogrel-Model) | Prior software/genotype precedent; superseded as first drug by direct 5-FU candidate |
| V01 | [Beumer 2019 IATDMCT](https://pubmed.ncbi.nlm.nih.gov/29923599/) · [DOI](https://doi.org/10.1002/cpt.1124) | Regimen-specific 5-FU TDM guidance; research endpoint definition |
| V02 | [Fiebrich-Westra 2025](https://doi.org/10.1200/PO-25-00062) | Prospective methods: 46-hour infusion, sampling/LC-MS and cycle-specific endpoints |
| V03 | [De With 2022](https://pubmed.ncbi.nlm.nih.gov/35397172/) · [DOI](https://doi.org/10.1002/cpt.2608) | 955-person uracil study; limits on phenotype interpretation |
| V04 | [Maillard 2023](https://pubmed.ncbi.nlm.nih.gov/36104927/) · [DOI](https://doi.org/10.1111/bcp.15536) | Multilaboratory preanalytic variability and repeated classification |
| V05 | [Alpe2U 2025](https://pubmed.ncbi.nlm.nih.gov/40466468/) · [DOI](https://doi.org/10.1016/j.ejca.2025.115483) | Phenotyping/exposure tradeoff; not a universal uracil-to-DPD label |
| V06 | [Henricks 2018](https://pubmed.ncbi.nlm.nih.gov/30348537/) | Prospective genotype-guided study; comparator and endpoint definition |
| V07 | [Deenen 2016](https://pubmed.ncbi.nlm.nih.gov/26573078/) | DPYD*2A-specific study; do not misattribute its effect sizes to Henricks |
| V08 | [PREDICT-5FU](https://pmc.ncbi.nlm.nih.gov/articles/PMC12199125/) | Prospective exposure/TDM context; exposure and toxicity remain distinct |
| C01 | [CPIC pending DPYD notice, 9 July 2026](https://blog.clinpgx.org/cpic-comment-on-pending-dpyd-guideline-update/) | Read in full: causal HapB3 AV 0.75 announced, database remains 0.5 until publication |
| C02 | [Current FDA safety update](https://www.fda.gov/drugs/resources-information-approved-drugs/safety-labeling-update-capecitabine-and-fluorouracil-5-fu-risks-associated-dihydropyrimidine) | Read in full: pretreatment DPYD testing unless immediate treatment needed |
| C03 | [EMA pretreatment DPD recommendation](https://www.ema.europa.eu/en/news/ema-recommendations-dpd-testing-prior-treatment-fluorouracil-capecitabine-tegafur-and-flucytosine) | Scope-specific recommendation, not a claim of one universal European legal mandate |
| C04 | [EMA renal/uracil communication](https://www.ema.europa.eu/en/medicines/dhpc/5-fluorouracil) | Renal impairment can confound uracil-based interpretation |
| C05 | [DPWG guideline](https://pubmed.ncbi.nlm.nih.gov/31745289/) · [DOI](https://doi.org/10.1038/s41431-019-0540-0) | Separate guideline source/version; do not silently blend with CPIC |

Primary full text was unavailable on some PMC requests because of access
interstitials; accessible publisher text or PubMed records were used at the
depth stated above. Unread supplement parameters and unavailable model code are
explicit Phase 0 retrieval/reproduction tasks, not assumed assets.

## Genome simulator interfaces

**Ped-sim.** [README and examples](https://github.com/williamslab/ped-sim/blob/master/README.md),
[license](https://github.com/williamslab/ped-sim/blob/master/LICENSE). Documented
truth-mode invocation, to validate against the pinned binary in Phase 0:

```bash
ped-sim -d pedigree.def -m founders.simmap -i founders.vcf -o offspring \
  --intf nu_p_campbell.tsv --seed 42 --keep_phase --err_rate 0 --miss_rate 0
```

Founder input must be phased and complete. Defaults otherwise add error and
missingness at 1e-3 and unphase outputs. Preserve founder IDs and inherited
breakpoints using documented `--set_founders`, `--founder_ids`, `--bp` or
`--bp_all` as appropriate. Map columns carry chromosome, physical coordinate,
male cM and female cM. Supplied Bhérer maps are b37. Output gzip is not BGZF;
convert explicitly before indexing. Pin the GPLv3 implementation and map files.

**HAPNEST.** [Quickstart](https://github.com/intervene-EU-H2020/synthetic_data),
[configuration](https://github.com/intervene-EU-H2020/synthetic_data/blob/main/config.yaml),
[GPLv3 license](https://raw.githubusercontent.com/intervene-EU-H2020/synthetic_data/main/LICENSE).
The container entry points include `init`, `fetch`, `generate_geno`,
`generate_pheno`, `validate`. Copy the documented `generate_geno 1 data/config.yaml`
workflow, replacing floating images with a pinned digest. Custom population
mixtures live under `genotype_data.samples`; the documented optimizer ignores
custom population structures. Anukriti must independently validate any local
calibration. Do not use `generate_pheno` disease labels as observed 5-FU outcomes.

**Haptools.** [Documented `simgenotype` CLI](https://haptools.readthedocs.io/en/stable/commands/simgenotype.html)
uses `--model`, `--mapdir`, `--ref_vcf`, `--sample_info`, `--region`, and `--out`;
`--pop_field` retains ancestry in VCF output. Copy the repository's
`tests/data/outvcf_gen.dat`, `tests/data/map/`, `tests/data/outvcf_test.vcf.gz`,
and `tests/data/outvcf_info.tab` example structure. Pin the [MIT implementation](https://github.com/CAST-genomics/haptools).
Generic structural-event support remains a capability test, not an assumed feature.

**SimHumanity.** [Repository](https://github.com/bhaller/SimHumanity), MIT code:
`model1_foundation.slim`, `model2_demography.slim`, `model3_treeseq.slim`,
`model3_analysis.py`. The foundation script requires SLiM ≥5 and explicit
repository paths in `defineRepositoryPaths()`. The supplied whole-genome model
does not supply human adult physiology or DPYD functional parameters. Preserve
the model's demography/map/selection assumptions in every scenario manifest.

**Maps.** [stdpopsim CLI/catalog](https://popsim-consortium.github.io/stdpopsim-docs/stable/cli_arguments.html)
and [map conversion documentation](https://popsim-consortium.github.io/stdpopsim-docs/latest/development.html)
provide assembly-specific map choices. A sex-averaged GRCh38 map is not an
automatic replacement for Ped-sim's sex-specific b37 map.

## PK-Sim/OSP interfaces: candidate runtime

Initial candidate: **OSPSuite-R 12.4.3, R ≥4.4, .NET 8/rSharp**, isolated from the
Python orchestrator. Verify with [tagged DESCRIPTION](https://github.com/Open-Systems-Pharmacology/OSPSuite-R/blob/v12.4.3/DESCRIPTION)
and the [official installation page](https://www.open-systems-pharmacology.org/OSPSuite-R/).
OSPSuite-R is GPL-2; inspect all runtime and model licenses before distribution.
Worker separation is for dependency isolation, not a claim that license duties
disappear.

The [PK-Sim installation note](https://www.open-systems-pharmacology.org/OSPSuite-R/articles/PKSim-installation.html)
states that OSPSuite-R ≥12.1 includes the needed PK-Sim dependencies; older vignette
text requiring a separate desktop install is stale. The source 5-FU model is 9.1;
successful conversion to 12.4.3 is unverified and is a required reproduction gate.

| Operation | Documented interface | Source |
|---|---|---|
| Project conversion | `convertSnapshot(..., format, output=".", runSimulations=FALSE)` | [Reference](https://www.open-systems-pharmacology.org/OSPSuite-R/reference/convertSnapshot.html) |
| Snapshot execution | `runSimulationsFromSnapshot(..., output=".", RunForAllOutputs=FALSE, exportCSV=TRUE, exportPKML=FALSE, exportJSON=FALSE, exportXML=FALSE)` | [Reference](https://www.open-systems-pharmacology.org/OSPSuite-R/reference/runSimulationsFromSnapshot.html) |
| Load exported model | `loadSimulation(filePath, loadFromCache=FALSE, addToCache=TRUE, resetIds=TRUE)` | [Source](https://github.com/Open-Systems-Pharmacology/OSPSuite-R/blob/main/R/utilities-simulation.R) |
| Population generation | `createPopulation(populationCharacteristics)` | [Reference](https://www.open-systems-pharmacology.org/OSPSuite-R/reference/createPopulation.html) |
| Parameter update | `setParameterValuesByPath(parameterPaths, values, simulation, units=NULL, stopIfNotFound=TRUE)` | [Reference](https://www.open-systems-pharmacology.org/OSPSuite-R/reference/setParameterValuesByPath.html) |
| Simulation | `runSimulations(simulations, population=NULL, agingData=NULL, simulationRunOptions=NULL, silentMode=FALSE, stopIfFails=FALSE)` | [Reference](https://www.open-systems-pharmacology.org/OSPSuite-R/reference/runSimulations.html) |
| Extract output | `getOutputValues(simulationResults, quantitiesOrPaths=NULL, population=NULL, individualIds=NULL, stopIfNotFound=TRUE, addMetaData=TRUE)` | [Reference](https://www.open-systems-pharmacology.org/OSPSuite-R/reference/getOutputValues.html) |
| CSV output | `exportResultsToCSV(results, filePath)` | [Reference](https://www.open-systems-pharmacology.org/OSPSuite-R/reference/exportResultsToCSV.html) |

These are documented contracts to check against the **installed pinned release**;
some linked pages track main. The main-branch
`exportProjectToSnapshot`/`loadProjectFromSnapshot` APIs were not verified in
12.4.3; do not assume they are available in that pinned worker.
The snapshot example uses inconsistent `csv`/`pkml` argument names in one place;
follow the documented `exportCSV`/`exportPKML` signature and execute a smoke test.

Copy-ready installation smoke test from the [official simulation vignette](https://github.com/open-systems-pharmacology/ospsuite-r/blob/main/vignettes/run-simulation.Rmd):

```r
library(ospsuite)
sim <- loadSimulation(system.file("extdata", "Aciclovir.pkml", package="ospsuite"))
results <- runSimulations(simulations=sim, stopIfFails=TRUE)[[1]]
exportResultsToCSV(results, "aciclovir-smoke.csv")
```

Aciclovir tests installation only. For 5-FU, copy/convert the published project,
discover generated `.pkml` names and parameter paths, and validate outputs.
No generic API named `simulate_patient`, no presumed `DPD|Vmax` path, and no
assumed concentration/time units should enter implementation.

Read the official [population vignette](https://www.open-systems-pharmacology.org/OSPSuite-R/articles/create-run-population.html),
[population-characteristics reference](https://www.open-systems-pharmacology.org/OSPSuite-R/reference/createPopulationCharacteristics.html),
[individual vignette](https://www.open-systems-pharmacology.org/OSPSuite-R/articles/create-individual.html),
[physiology population algorithm](https://docs.open-systems-pharmacology.org/v12/working-with-pk-sim/pk-sim-documentation/pk-sim-creating-populations),
[expression profiles](https://docs.open-systems-pharmacology.org/working-with-pk-sim/pk-sim-documentation/pk-sim-expression-profile),
[administration protocols](https://docs.open-systems-pharmacology.org/v12/working-with-pk-sim/pk-sim-documentation/pk-sim-administration-protocols),
and [efficient calculation examples](https://www.open-systems-pharmacology.org/OSPSuite-R/articles/efficient-calculations.html).

Copy distributed individual parameters, preserving formula-derived quantities.
Retain output `metaData` and units; time may be minutes. Qualify failures with
`stopIfNotFound=TRUE` and `stopIfFails=TRUE`; otherwise failed runs may return
NULL. Discover dosing parameters from validated exported regimen templates.
Only after single-run correctness, adopt documented simulation batching and
check run-ID mapping and queue clearing.

## Local source contracts inspected

Paths below are relative to the shared SynthaTrial root, not this docs clone.

- `anukriti-pgx-core/anukriti_pgx_core/types.py`: `VCFVariant(ref, alt, genotype)`;
  `Diplotype.hapb3_basis`, `overspecified`, `allele_counts`, provenance.
- `anukriti-pgx-core/anukriti_pgx_core/calling/genes/dpyd.py`: `DPYDCaller().call(variants)`;
  longest-match allele counting; explicit unphased-inference limitation.
- `asl/src/asl/interpret.py`: `call_engine(assay)` and version/HapB3 capability check.
- `asl/src/asl/pipeline.py`: `build(assay)`; assay prerequisites and interpretation assembly.
- `asl/src/asl/models.py`: existing assay/test-state and interpretation types.
- `anukriti/ml/dpyd-classifier/src/train.py`, `train_v4.py`, `train_v5.py`:
  version-dependent feature sets and label-source concerns; no blanket approval.
- `anukriti/ml/data/offer_2014_dpyd_functional.csv`: partial 43-row local extraction,
  to reconcile with the source study before reuse.
- `anukriti/research/synthetic_genomes/`: executed regional prototype, archived
  unchanged code and outputs under [benchmark/](benchmark/README.md).

No imported interface is assumed to accept phased structural haplotypes merely
because its input contains a `|` genotype separator. Preserve simulation truth
separately and add any missing clinical caller capability through the core's
versioned regression process.
