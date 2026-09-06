Archive note, 6 September 2026: this directory preserves the executed sandbox
prototype and its public-reference outputs. The source code and VCF are unchanged.
The commands below use paths from the original shared SynthaTrial workspace;
from this docs clone, run `python experiment.py --help` in this directory and
provide the source VCF, index, panel, cache and output paths explicitly.

This is a working research prototype for generating **phased regional human
genotypes** from public reference haplotypes. It does not generate complete
human genome sequences or validated drug-response outcomes.

The experiment uses 2,504 real 1000 Genomes participants as its source catalog
and retains 8,901 complete, biallelic SNVs in GRCh37 chromosome 19,
41,400,000–41,649,999. The region includes CYP2B6. Each target-population split
uses only 20 local people plus other populations in the same reference
superpopulation. The remaining target people are held out from all fitting.

Read [DESIGN.md](DESIGN.md) for the design fixed before results and
[results/REPORT.md](results/REPORT.md) for all six methods and limitations.

The main findings are that haplotype copying substantially improves LD
preservation over independent SNP sampling, and that **simple pooled donor
sampling outperformed our calibrated variants on average in this experiment**.
This is an engineering feasibility result, not a new clinical discovery.

The illustrative export contains 5,000 synthetic diploid profiles, each at
8,901 SNVs, using the preselected BEB proxy / calibrated-mosaic configuration:

- [Phased synthetic VCF](results/synthetic_beb_proxy_chr19.vcf.gz)
- [Tabix index](results/synthetic_beb_proxy_chr19.vcf.gz.tbi)
- [Export provenance](results/export_manifest.json)
- [All 72 benchmark runs, splits, versions, hashes](results/metrics.json)

BEB is a 1000 Genomes population label, **not a Bhutan cohort**. None of the
generated samples are identified as real people. Whole observed haplotype
blocks are reused, however, so synthetic identifiers do not establish privacy.
Do not publish local/private donor-derived data without a separate disclosure
assessment.

`simulation.py` implements donor resampling, entropy-regularized frequency
calibration, protected-block mosaics, and a separate two-parent meiosis
function. The latter accepts maternal and paternal genetic maps in Morgans,
models Poisson crossovers, and passes Mendelian-inheritance tests. It is not
the algorithm used to produce the mosaic VCF. `experiment.py` handles source
quality filters, person-level splits, metrics, export, and exact GT round-trip
verification. No Anukriti production engine or clinical table is changed.

To reproduce from the SynthaTrial root, use Python with numpy, scipy, pysam,
and pytest. The recorded run used Python 3.12.4, numpy 2.5.1, scipy 1.17.0,
and pysam 0.23.3. The existing Conda environment supplies these packages.
The complete variant matrix cache remains in `/tmp`; it can be regenerated.
Public source hashes and URLs are recorded in `metrics.json`.

```bash
mkdir -p /tmp/anukriti-synthetic-generation-2026-09-06
curl -fsS https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/integrated_call_samples_v3.20130502.ALL.panel \
  -o /tmp/anukriti-synthetic-generation-2026-09-06/1000g_samples.panel
curl -fsS https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr19.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz.tbi \
  -o /tmp/anukriti-synthetic-generation-2026-09-06/chr19.vcf.gz.tbi

/home/abhimanyu/miniconda3/bin/python -m pytest -c /dev/null \
  anukriti/research/synthetic_genomes/test_simulation.py -q

OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
/home/abhimanyu/miniconda3/bin/python \
  anukriti/research/synthetic_genomes/experiment.py \
  --vcf anukriti/ALL.chr19.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz \
  --index /tmp/anukriti-synthetic-generation-2026-09-06/chr19.vcf.gz.tbi \
  --panel /tmp/anukriti-synthetic-generation-2026-09-06/1000g_samples.panel \
  --cache /tmp/anukriti-synthetic-generation-2026-09-06/chr19_region.npz
```

The source chromosome VCF was already present locally. If it is absent, its
official download URL is in the results provenance. Generated outputs are
replaced on rerun; use `--out` to preserve a previous run separately.

The 5,000-person export was preselected for illustrating new mosaic
combinations; it is **not** the best-performing method selected by this
benchmark. For a fidelity-first follow-up, carry forward the pooled-copy
baseline and test map-based recombination against it on new held-out data.
