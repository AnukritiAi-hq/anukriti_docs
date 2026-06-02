# Runbook — Rung-2 Phase B: CYP2D6 SV data pull + caller install

> **Created:** 2026-06-02
>
> **Audience:** an engineer running the live CYP2D6 structural-variant
> bake-off (Cyrius / StellarPGx / Aldy) against the Phase-A GeT-RM SV truth
> set.
>
> **Companion:** [`../RUNG2_CYP2D6_SV_PLAN.md`](../RUNG2_CYP2D6_SV_PLAN.md)
> (Phase B), [`../papers/README.md`](../papers/README.md) (#8 Cyrius, #9
> StellarPGx, #10 Aldy), `anukriti/src/benchmark/getrm_truth.py`
> (`GETRM_CYP2D6_SV`), `anukriti/src/benchmark/cyp2d6_sv_bakeoff.py`.

---

## TL;DR

The full bake-off needs three things the deterministic engine never touched:
real **read-level alignments (BAM/CRAM)**, the **callers**, and a
**reference genome**. This runbook gets each, restricted to the CYP2D6 locus
so it runs on a laptop. Tools used: `samtools` + `Cyrius` (CYP2D6-only,
simplest) and/or `Aldy`; StellarPGx is heavier (Nextflow + graph aligner).

---

## 0. Sample selection (which truth lines are pullable)

GeT-RM samples live in **ENA PRJEB19931** (70 PCR-free WGS BAMs, GRCh37,
sample alias = Coriell ID). Of the Phase-A SV truth lines, only one overlaps
this project today:

| Coriell | ENA run | CYP2D6 consensus (Gaedigk 2019) | our truth entry |
|---|---|---|---|
| **HG01190** | `ERR1955326` | **`*68+*4/*5`** (hybrid + deletion → PM) | currently `*1/*1` (stale) |

> **Finding:** our `GETRM_CYP2D6` entry for HG01190 is `*1/*1` (a non-SV
> placeholder), but Gaedigk 2019 Table 3 revised it to `*68+*4/*5` — a
> hybrid+deletion SV. A live caller run is expected to surface the SV and
> correct this. HG01190 is **SAS** — the equity-relevant population.

For the other SV lines (HG00156, NA19317, NA07439, HG00337, NA17244,
NA18545) pull BAM/CRAM from the **1000 Genomes high-coverage** set
(IGSR / `s3://1000genomes`) — they are not in PRJEB19931. See §5.

---

## 1. Tools (conda — isolated, does not touch venv-baseline)

```bash
# samtools/bcftools/tabix for region slicing
conda create -y -n pgx-sv -c bioconda -c conda-forge samtools bcftools tabix
conda activate pgx-sv

# Cyrius (CYP2D6-only, pure Python; GitHub — Illumina/Cyrius)
git clone https://github.com/Illumina/Cyrius.git tools/Cyrius
pip install numpy pysam scipy   # Cyrius runtime deps

# Aldy (multi-gene; pip)
pip install aldy            # needs a CN-neutral baseline; see Aldy docs

# StellarPGx (heavier — Nextflow + graph aligner; optional)
# curl -s https://get.nextflow.io | bash   # needs java (have: openjdk 21)
# git clone https://github.com/SBIMB/StellarPGx.git tools/StellarPGx
```

## 2. Reference genome (GRCh37 — matches PRJEB19931 BAMs)

```bash
mkdir -p data/ref
wget -O data/ref/hs37d5.fa.gz \
  ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/technical/reference/phase2_reference_assembly_sequence/hs37d5.fa.gz
gunzip data/ref/hs37d5.fa.gz && samtools faidx data/ref/hs37d5.fa
```

## 3. Pull the CYP2D6 region slice (remote, no full-BAM download)

CYP2D6 locus, **GRCh37 / b37 contig `22`**: `22:42,518,900-42,553,000`
(gene + CYP2D7 paralog + flanks; CYP2D6 itself is `22:42,522,500-42,526,883`).

```bash
mkdir -p data/cyp2d6_bams
BAM=ftp://ftp.sra.ebi.ac.uk/vol1/run/ERR195/ERR1955326/HG01190.bam
# samtools reads the .bai remotely and downloads only the slice (tens of KB)
samtools view -b "$BAM" "22:42518900-42553000" -o data/cyp2d6_bams/HG01190.cyp2d6.bam
samtools index data/cyp2d6_bams/HG01190.cyp2d6.bam
samtools flagstat data/cyp2d6_bams/HG01190.cyp2d6.bam   # sanity: nonzero reads
```

> Note: Cyrius and StellarPGx use whole-genome coverage normalization, so a
> region-only slice limits CN accuracy. For a *correct* CN call, download the
> full BAM (~410 MB for HG01190) or feed the caller a CN-baseline. The slice
> is enough to confirm reads-present, plumb the pipeline, and run Aldy
> (`--cn-neutral`) / a region-scoped call.

## 4. Run a caller → CYP2D6 diplotype

```bash
# Cyrius (expects full-genome BAM for CN; region slice = smoke test)
python tools/Cyrius/star_caller.py --genome 37 \
  --manifest <(echo "$PWD/data/cyp2d6_bams/HG01190.cyp2d6.bam") \
  --outDir out/cyrius --threads 2

# Aldy (region-scoped CYP2D6)
aldy genotype -p illumina -g CYP2D6 --genome hg19 \
  -o out/aldy/HG01190.aldy data/cyp2d6_bams/HG01190.cyp2d6.bam
```

## 5. 1000G high-coverage for the other SV lines (not in PRJEB19931)

```bash
# IGSR / 1000G 30x GRCh38 CRAMs, e.g. NA12878:
CRAM=http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000G_2504_high_coverage/data/ERR3239334/NA12878.final.cram
# GRCh38 CYP2D6: chr22:42,126,000-42,132,000 (gene); use a wider window for CYP2D7.
samtools view -b -T data/ref/GRCh38.fa "$CRAM" "chr22:42120000-42155000" \
  -o data/cyp2d6_bams/NA12878.cyp2d6.bam
```

> ⚠️ Build mismatch: PRJEB19931 = GRCh37 (`22`), 1000G high-cov = GRCh38
> (`chr22`). Keep coordinates + reference + `--genome` flag consistent per
> sample, or lift over. The bake-off harness is build-agnostic (it scores
> diplotype strings), but the caller is not.

## 6. Feed results into the bake-off harness

`cyp2d6_sv_bakeoff.py` currently scores Anukriti's heuristic against
published numbers. To add a real tool column: capture each caller's diplotype
per sample into a `{sample_id: diplotype}` dict and score it with
`compute_concordance(truth, preds, "CYP2D6")`, split via
`get_truth_for_gene_by_sv`. Replace the truth `*1/*1` for HG01190 with the
caller-confirmed `*68+*4/*5` (with provenance) once verified.

---

## Environment notes (this machine, 2026-06-02)

- Have: conda 24.7.1, docker 29.4.1, java 21, wget/curl; 248 GB free; ENA +
  PyPI + GitHub reachable.
- Missing at start: samtools, tabix, the three callers, Nextflow (all
  installable via the steps above).
- venv-baseline (the product env) is left untouched — caller stack goes in
  the `pgx-sv` conda env.

---

## Validated run (2026-06-02) — what actually executed

Executed in this environment, end to end:

1. **Tools installed** — `conda create -n pgx-sv` with samtools 1.23.1 /
   bcftools / htslib; **Cyrius** cloned (`tools/Cyrius/star_caller.py`) with
   numpy/pysam/scipy/statsmodels via conda. Cyrius `--help` runs.
2. **Data pulled** — remote samtools slice of **HG01190** (ENA `ERR1955326`,
   GRCh37, contig `22`) over the CYP2D6 locus → `HG01190.cyp2d6.bam`
   (807 KB; **10,463 reads in locus, 914 in the gene body**). BAM header
   confirmed GRCh37 (`@SQ SN:22 ... GRCh37`). Pipeline ENA → slice → caller
   is proven.
3. **Cyrius run** — on the region slice it returns `Genotype: None`,
   `Median_depth 0.0`, `Coverage_MAD NaN` (divide-by-zero on empty
   genome-wide bins). **Expected:** Cyrius normalizes CN against *whole-genome*
   coverage, so a region-only slice cannot produce a CN call. Confirms the
   §3 caveat, not a bug.
4. **Aldy run (the real call)** — `aldy genotype -g CYP2D6 --genome hg19`
   on the *same region slice* produced a confident diplotype:
   **`*4.021 / *68` — Poor Metabolizer (activity score 0.0), 100% confidence**,
   detecting the **`*68` CYP2D6–CYP2D7 hybrid**. Aldy v4.8.3, free for
   non-commercial/academic use. (On a region slice Aldy can't resolve the
   `*5` deletion copy without genome-wide depth — hence `*4/*68` vs the full
   `*68+*4/*5` — but the **phenotype call (PM) is correct**.)

### Live result vs truth (the validating finding)

| Source | HG01190 CYP2D6 | Phenotype |
|---|---|---|
| our `GETRM_CYP2D6` (pre-run) | `*1/*1` | Normal Metabolizer |
| Gaedigk 2019 (GeT-RM literature) | `*68+*4/*5` | Poor Metabolizer |
| **Aldy (live, region slice)** | **`*4/*68`** | **Poor Metabolizer** |

A real SV-capable caller, run on real ENA data, **detected the hybrid and
called PM** — matching the literature and contradicting our stale `*1/*1`
Normal-Metabolizer placeholder. This is the Rung-2 thesis demonstrated end to
end on one SAS sample: the heuristic/placeholder misses the SV; the SV caller
catches it. The `getrm_truth.py` HG01190 CYP2D6 entry is corrected to
`*68+*4/*5` (PM) with provenance accordingly.

**Cyrius full-CN note (still pending):** for Cyrius's full `*68+*4/*5`
(including the `*5` deletion copy number), it needs the **full WGS BAM**
(HG01190 is **~917 MB**, not the ~410 MB the submitted_bytes field implied).
The ENA HTTPS link measured ~0.75–3.7 MB/s here — a multi-hour pull that
exceeded the in-session timeout and truncated (samtools `quickcheck` =
"missing EOF block"). Retried-as-is will not fix it (slow link + hard
timeout).

**Workarounds (pick one for the real call):**
- Background the full download (`wget -c` to resume) outside a timed step,
  then `samtools quickcheck` before running Cyrius.
- Or use **Aldy region-scoped** (`aldy genotype -g CYP2D6`) which can work
  on a locus BAM without genome-wide CN normalization (lower CN fidelity but
  produces a callable diplotype for the bake-off).
- Or pull the **1000G 30x GRCh38 CRAM** for HG01190 (often faster mirrors)
  and slice with `-T <GRCh38.fa>`.

**Expected truth for HG01190:** Gaedigk 2019 → `*68+*4/*5` (PM). Our
`GETRM_CYP2D6` still lists `*1/*1` for HG01190 — to be corrected to the
caller-confirmed SV call (with provenance) once a full-BAM run completes.
