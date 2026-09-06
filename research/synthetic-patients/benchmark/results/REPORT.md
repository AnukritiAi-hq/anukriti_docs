Research benchmark completed 2026-09-06. All metrics below are from the local experiment; they are not literature claims or clinical validation.

Generated artifact: **5,000 synthetic diploid regional profiles at 8,901 SNVs**. Exact exported genotype, phase, allele, sample-ID, and position round trips passed. The VCF is a BEB-reference proxy, not Bhutanese data.

The mean across four target populations and three fixed splits is:

| Method | Common-SNP AF MAE | LD r² MAE | Short-range LD MAE | Long-range LD MAE | rs3745274 AF error | rs3745274 genotype TV |
|---|---:|---:|---:|---:|---:|---:|
| independent | 0.04297 | 0.07590 | 0.16139 | 0.02795 | 0.06882 | 0.09212 |
| local_copy | 0.04239 | 0.04616 | 0.06288 | 0.03674 | 0.05653 | 0.07309 |
| regional_copy | 0.02444 | 0.02146 | 0.03221 | 0.01544 | 0.03016 | 0.06071 |
| pooled_copy | 0.02399 | 0.02119 | 0.03117 | 0.01561 | 0.02839 | 0.05590 |
| calibrated_copy | 0.03028 | 0.02441 | 0.03638 | 0.01770 | 0.04159 | 0.05647 |
| calibrated_mosaic | 0.03128 | 0.03342 | 0.05019 | 0.02401 | 0.05071 | 0.06813 |

All columns are errors; lower is better. AF is alternate-allele frequency. An AF MAE of 0.02399 is **2.399 percentage points of average frequency error**, not 97.6% patient-level accuracy. Genotype TV is total variation between the real and synthetic 0/1/2 alternate-copy distributions. LD r² describes association between variants; it is not a clinical prediction R². Short-range means at most 50 kb; long-range means more than 50 kb.

Averaging gives each of the 12 splits equal weight. The three splits reuse participants and are not independent population replications. No statistical significance or external performance guarantee is claimed. The held-out empirical distribution also has finite-sample noise.

The generated mixtures show useful structure:

- Pooled copying reduced average common-SNP AF error by 43.4% and LD error by 54.1% relative to copying from 20 local participants alone. The improvement uses additional **real regional reference information**; it is not an information gain from multiplying samples.
- Calibrated mosaics reduced LD error by 56.0% relative to independent SNP sampling, and common-SNP AF error by 26.2% relative to local copying.
- The simpler pooled and regional baselines beat both calibrated variants on average. This experiment does not support adopting the new weighting method as a general improvement.
- All mosaic regional haplotypes were different from every pooled donor across the retained sites. Every protected-block haplotype exactly matched an observed donor at the retained sites. These are structural properties, not privacy or biological-viability guarantees.
- Independent SNP sampling created unobserved protected-block combinations in every generated haplotype in these runs. It should not be the main generator for phased pharmacogene sequences.

The target populations and sample counts were:

| Target code | Local people | Other regional people | Held-out people |
|---|---:|---:|---:|
| BEB | 20 | 403 | 66 |
| CHB | 20 | 401 | 83 |
| GBR | 20 | 412 | 71 |
| YRI | 20 | 553 | 88 |

The four reference labels are BEB (Bengali in Bangladesh), CHB (Han Chinese in Beijing), GBR (British in England and Scotland), and YRI (Yoruba in Ibadan, Nigeria). Broad 1000 Genomes superpopulation membership was used only as an experimental donor-selection rule; it is not an assertion that all people within one group are genetically interchangeable.

Per-population means expose the calibration tradeoff:

| Target | Method | Common-SNP AF MAE | LD r² MAE | rs3745274 AF error |
|---|---|---:|---:|---:|
| BEB | calibrated_copy | 0.02976 | 0.02385 | 0.01812 |
| BEB | calibrated_mosaic | 0.03214 | 0.03393 | 0.03407 |
| BEB | independent | 0.04241 | 0.07962 | 0.04871 |
| BEB | local_copy | 0.04300 | 0.04611 | 0.04188 |
| BEB | pooled_copy | 0.02125 | 0.01988 | 0.01347 |
| BEB | regional_copy | 0.02124 | 0.01992 | 0.01535 |
| CHB | calibrated_copy | 0.03197 | 0.02462 | 0.03331 |
| CHB | calibrated_mosaic | 0.03196 | 0.03421 | 0.04406 |
| CHB | independent | 0.04334 | 0.08492 | 0.03368 |
| CHB | local_copy | 0.04103 | 0.04948 | 0.01870 |
| CHB | pooled_copy | 0.02857 | 0.02400 | 0.06554 |
| CHB | regional_copy | 0.02937 | 0.02457 | 0.07238 |
| GBR | calibrated_copy | 0.03274 | 0.02796 | 0.05252 |
| GBR | calibrated_mosaic | 0.03335 | 0.03770 | 0.05317 |
| GBR | independent | 0.04671 | 0.08659 | 0.07301 |
| GBR | local_copy | 0.04644 | 0.04667 | 0.06439 |
| GBR | pooled_copy | 0.02303 | 0.02323 | 0.02160 |
| GBR | regional_copy | 0.02237 | 0.02308 | 0.01623 |
| YRI | calibrated_copy | 0.02664 | 0.02120 | 0.06241 |
| YRI | calibrated_mosaic | 0.02768 | 0.02783 | 0.07153 |
| YRI | independent | 0.03942 | 0.05249 | 0.11987 |
| YRI | local_copy | 0.03910 | 0.04238 | 0.10115 |
| YRI | pooled_copy | 0.02311 | 0.01766 | 0.01295 |
| YRI | regional_copy | 0.02477 | 0.01826 | 0.01669 |

In CHB, calibration reduced rs3745274 frequency error from 0.06554 for pooled copying to 0.03331 for calibrated copying, while increasing average genome-region frequency error. This is a descriptive result from the inspected test set. It motivates a **new**, independently evaluated hypothesis about locus-specific borrowing; it does not justify tuning and claiming an improvement on these same splits.

How the experiment was controlled:

- Full source: the existing 1000 Genomes Phase 3 b37 chromosome-19 VCF, 2,504 participants. Public panel and matching tabix index came from the official release.
- The fixed source variant catalog and complete-phasing quality filter were applied before population splitting. Held-out allele frequencies and LD were not used to select training markers, weights, priors, or other parameters. This is not an independent assay-discovery validation.
- Retained 8,901 SNVs. Excluded 376 non-biallelic-SNV records and 13 otherwise-eligible SNV records at duplicate positions. No eligible record was excluded for missing/unphased calls in this region.
- The frequency evaluation used 1,016–1,674 training-common sites depending on split, rather than allowing thousands of rare or invariant sites to make the average look artificially good. LD used up to 128 training-selected common markers; undefined monomorphic held-out pairs were excluded.
- Calibration matched 48 training-common markers plus the known focus marker toward a local/reference-shrunk target. Prior strength 20 chromosome copies and ridge 0.02 were fixed before examining results.
- Mosaics use fixed 50 kb physical boundaries and preserve a predefined CYP2B6/promoter interval. Those boundaries are not empirical recombination maps; segment independence causes some LD loss.
- Splits keep both haplotypes of each real person together. IDs are disjoint, but kinship between distinct reference individuals was not screened.
- Six methods × four proxies × three seeds = 72 runs, each with 1,024 synthetic individuals. No synthetic phenotype or drug-response outcome was created.

Source and scope gaps:

- rs3745274 at GRCh37 chr19:41,512,841 G>T is present. rs2279343 at chr19:41,515,263 A>G is absent from the regional source records. Absence is not interpreted as a reference genotype.
- The benchmark evaluates retained SNV patterns, not full CYP2B6 star-allele correctness. The protected block lacks excluded variants and the missing known marker. Calling it a complete validated pharmacogene sequence would be wrong.
- Depending on split, 92–282 sites with an alternate allele in held-out people had no alternate copy in any pooled donor. No resampling algorithm recovered those absent alternate alleles.
- Structural variants, copy number, indels, HLA, sex chromosomes, mitochondria, sequencing errors, and uncertain phase need separate treatment for full PGx coverage.
- No Bhutan participant was used, and no clinical drug-selection or dosing endpoint was tested. No independence, differential privacy, or safe-release guarantee is claimed.
- This is one approximately 250 kb region. Whole-genome runtime and quality are not established by this experiment.

Artifacts and reproducibility:

- [All per-run metrics, full participant splits, feature positions, software versions, and source/code hashes](metrics.json)
- [Export manifest](export_manifest.json)
- [Generated VCF](synthetic_beb_proxy_chr19.vcf.gz)
- [Design fixed before benchmark](../DESIGN.md)
- [Runnable instructions](../README.md)

VCF SHA-256: `d094e462d7346f09c3a027c8e89beaac605e43d32c8869abcb66bb1c30c4970f`.

Next experiment: retain pooled copying as the fidelity baseline, replace fixed blocks with established map-based sampling, and assess locus-specific borrowing on newly held-out population/region combinations. For Bhutan, use local samples to calibrate a population mixture and verify it against an untouched local cohort before fitting any clinical outcome model.
