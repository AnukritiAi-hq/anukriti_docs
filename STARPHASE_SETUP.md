# StarPhase Setup — CYP2D6 SV calling (Rung-2 Phase B′)

One page to go from zero to a scored CYP2D6 call in **under 30 minutes** on a
local machine or a small AWS EC2 instance. This procedure was **executed and
verified end-to-end on HG002** (2026-06-14): StarPhase called `*2/*4`, which
our ingestion seam phenotyped as **Intermediate Metabolizer (AS 1.0)** —
matching the GeT-RM truth.

> Why this doc exists: `pbstarphase` installs cleanly via conda, but the
> `pbstarphase build` step (which queries the live CPIC API) is **broken**
> against the current API — it errors with
> `invalid type: map, expected a sequence at line 1 column 0`.
> The fix is to use PacBio's **prebuilt database** instead of building one.
> That single gotcha is what this doc exists to save you.

---

## Requirements

- Linux x86-64, conda/miniconda, ~2 GB free disk, internet.
- No GPU, no sudo needed. Runs in minutes on a `t3.medium` EC2 (or any laptop).

## 1. Install StarPhase (~3 min)

```bash
conda create -y -n starphase -c bioconda -c conda-forge "pbstarphase=1.4.2"
conda activate starphase
pbstarphase --version          # -> pbstarphase 1.4.2-...
```

## 2. Get the prebuilt database — DO NOT run `pbstarphase build` (~1 min)

The live build is broken (see banner above). Download the prebuilt DB that
matches the binary version (`v1.4.x` → `data/v1.4.0/...`):

```bash
curl -sL -o pbstarphase_db.json.gz \
  https://raw.githubusercontent.com/PacificBiosciences/pb-StarPhase/main/data/v1.4.0/pbstarphase_20250515.json.gz
gunzip -kf pbstarphase_db.json.gz        # -> pbstarphase_db.json (~135 MB)
```

(For a newer binary, list `data/` in the repo and pick the matching
`pbstarphase_*.json.gz`. v2.x DBs go with v2.x binaries.)

## 3. Get a GRCh38 reference (~1 min, chr22 only is enough for CYP2D6)

Our BAMs are GRCh38 with `chr`-prefixed contigs. chr22 alone suffices:

```bash
curl -sL -o chr22.fa.gz https://hgdownload.soe.ucsc.edu/goldenPath/hg38/chromosomes/chr22.fa.gz
gunzip -kf chr22.fa.gz
samtools faidx chr22.fa        # or: python -c "import pysam; pysam.faidx('chr22.fa')"
```

## 4. Get the locus BAM (~1 min/sample, ~2 MB each)

Use the repo's region fetcher — pulls ONLY the CYP2D6 locus from the remote
GIAB BAM via its index (not the 70 GB whole genome):

```bash
cd anukriti
python scripts/fetch_giab_cyp2d6_longread.py HG002
# -> data/giab_cyp2d6/HG002_CYP2D6_GRCh38.bam (+ .bai)
```

**The SAS sample HG01190 is NOT on GIAB** — it is a 1000 Genomes line whose
long-read data lives at **ArrayExpress E-MTAB-15248 / BioProject
PRJNA1003794** (Deserranno 2025). Fetch its BAM from ENA, slice chr22
42,100,000–42,160,000 with `samtools view -b <bam> chr22:42100000-42160000`,
and index it. Same for NA19785.

## 5. Run StarPhase, CYP2D6 only (~3 min)

```bash
conda activate starphase
printf "CYP2D6\n" > include_cyp2d6.txt
pbstarphase diplotype \
  --database pbstarphase_db.json \
  --reference chr22.fa \
  --bam data/giab_cyp2d6/HG002_CYP2D6_GRCh38.bam \
  --include-set include_cyp2d6.txt \
  --output-calls data/giab_cyp2d6/HG002.starphase.json
```

Output (verified) has `gene_details.CYP2D6.simple_diplotypes[0].diplotype`,
e.g. `"*2/*4"`.

## 6. Score it (~instant)

```bash
# put one <SAMPLE>.starphase.json per sample in a folder, then:
python -m src.benchmark.cyp2d6_starphase_runner --calls-dir data/giab_cyp2d6
# wiring smoke test, no data needed:
python -m src.benchmark.cyp2d6_starphase_runner --self-check
```

The runner normalizes the StarPhase call (PharmVar nomenclature, Turner 2023),
phenotypes it through the deterministic ingestion seam, and scores it against
the SV truth set — overall / SV-only / by-population (SAS = HG01190).

---

## Notes / gotchas

- **Scoring needs truth-set samples.** HG002 is great for *running* StarPhase
  but is **not in our SV truth set**, so it produces a call, not a scored
  concordance row. The truth-set SV samples are: HG01190 (SAS), HG00156 (EUR),
  NA19317 (AFR), NA07439 (EUR), HG00337 (EUR), NA17244 (EUR), NA18545 (EAS).
  HG01190 (from ENA, step 4) is the highest-value one — SAS equity cell **and**
  one of the five GIAB-class samples StarPhase was validated on in Deserranno
  2025.
- **Version match matters:** the DB version must match the binary major/minor.
- **No VCF needed** for CYP2D6: StarPhase builds consensus haplotypes from the
  BAM directly (`No variant call files provided ... CYP2D6 ... Solving`).
- Provenance for the activity-value mapping the runner applies:
  `src/cyp2d6_sv_nomenclature.py` ← Turner 2023 (PMID 37669183).
