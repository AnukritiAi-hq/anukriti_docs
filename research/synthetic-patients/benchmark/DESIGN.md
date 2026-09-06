Experiment fixed before inspecting benchmark results, 2026-09-06.

Question: can 20 local individuals guide haplotype sampling from a larger
regional reference, and what is lost when creating new regional haplotypes?

Use GRCh37 chromosome 19 [41,400,000, 41,650,000), biallelic complete phased
SNVs from the existing 1000 Genomes Phase 3 VCF. Exclude duplicate positions.
Do not use the application's hand-curated JSONL fixture for benchmarking.

Population proxies: BEB, CHB, GBR, YRI; seeds 20260906, 20260907, 20260908.
20 local people per split. Reference: same 1000 Genomes superpopulation,
excluding the target population. Test: remaining target people. Both
haplotypes of each person stay together. Sample IDs are disjoint; relatives
across participants are not screened. These proxies do not represent Bhutan.

Compare independent SNP sampling, intact local haplotype resampling, intact
regional resampling, intact pooled resampling, calibrated pooled resampling,
and calibrated block mosaics. Fixed hyperparameters: 20 reference-prior
chromosome copies, 48 common training markers plus rs3745274, ridge 0.02,
50 kb physical blocks. No donor switch in the predefined CYP2B6/promoter
interval 41,494,958–41,524,303. This protects observed haplotypes; it is not
proof of clinical correctness and does not model natural crossover hotspots.

Generate 1,024 synthetic diploid people per method/split. Evaluate training-
common SNP frequency MAE (1–99% alternate frequency), r² MAE at 128 training-
common markers (5–95%), short/long distance LD, rs3745274 genotype distribution,
and donor-relative region/protected-block novelty. Exclude undefined held-out
monomorphic LD pairs and report the evaluated pair count. Do not select
methods or hyperparameters using held-out outcomes. Report all comparisons.

Generate a preselected illustrative export of 5,000 BEB-proxy diploid regional
genotypes using calibrated mosaics, seed 20269906 and first split. It is not
a whole-genome dataset, Bhutan cohort, clinical training set, or private release.
Round-trip verify every exported genotype and position. Record the missing
rs2279343 source marker rather than treating absence as a reference call.

No new star alleles, drug-response labels, de novo mutations, copy-number
variants, aging, selection, or clinical effects are inferred in this experiment.
