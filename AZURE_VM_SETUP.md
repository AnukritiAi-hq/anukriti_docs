# Azure VM Setup — Anukriti Genomics Compute Sandbox

> **Purpose:** a reproducible runbook for the long-read genomics compute box.
> The local sandbox can remote-slice GIAB BAMs (indexed), but **1000 Genomes
> samples at ENA are raw FASTQ only** — they require a full whole-genome
> minimap2 alignment before the CYP2D6 locus can be sliced. That is the
> external-compute step this VM exists for.
>
> **First job (documented below):** HG01190 (SAS) — ENA `SRR25583344` →
> minimap2 → CYP2D6 locus slice → StarPhase → score, via the existing
> `scripts/fetch_ena_cyp2d6_longread.sh`.
>
> **Audience:** any Anukriti team member. Every command is copy-pasteable.
> **Last updated:** 2026-06-14.

---

## 0. Target spec

| Resource | Value | Azure mapping |
|---|---|---|
| OS | Ubuntu 22.04 LTS | `Canonical:0001-com-ubuntu-server-jammy:22_04-lts-gen2:latest` |
| Compute | 16 vCPU, 64 GB RAM | **`Standard_D16s_v5`** (general-purpose; good price/RAM for minimap2) |
| OS/work disk | 500 GB SSD | `Premium_LRS`, 512 GB (`P20`) data disk |
| Archival | Azure Blob storage | Storage account + container, mounted via BlobFuse2 |
| Region | pick near you / data egress | examples below use `eastus` (matches anukriti-api) |

> **Cost note (₹95L credits):** a `D16s_v5` runs ~₹70–90/hr in `eastus`;
> **deallocate when idle** (`az vm deallocate`) — you pay compute only while
> running, disk + Blob are cheap. A single HG01190 run is a few hours, so the
> credit impact is negligible. Right-size down (`D8s_v5`) if 8 vCPU suffices.

Sizing rationale: minimap2 ONT alignment of a ~7.6 GB FASTQ (3.6M reads)
against GRCh38 is RAM- and CPU-bound; 16 vCPU + 64 GB comfortably holds the
genome index (~8 GB) with headroom. 500 GB holds: FASTQ (~8 GB) + reference
(~3 GB) + whole-genome sorted BAM (~30–60 GB) + slices, with room for several
samples before archiving to Blob.

---

## 1. Provision the VM (Azure CLI)

Run locally where `az` is logged in (`az login` first).

```bash
# --- variables (edit RG / names / region as needed) ---
RG=anukriti-genomics-rg
LOC=eastus
VM=anukriti-lrs-01
ADMIN=anukriti
SIZE=Standard_D16s_v5

# 1a. Resource group
az group create -n "$RG" -l "$LOC"

# 1b. The VM (Ubuntu 22.04, SSH key auth, 16 vCPU / 64 GB)
az vm create \
  -g "$RG" -n "$VM" \
  --image "Canonical:0001-com-ubuntu-server-jammy:22_04-lts-gen2:latest" \
  --size "$SIZE" \
  --admin-username "$ADMIN" \
  --generate-ssh-keys \
  --os-disk-size-gb 128 \
  --public-ip-sku Standard

# 1c. Attach a 512 GB Premium SSD data disk for the work area
az vm disk attach \
  -g "$RG" --vm-name "$VM" \
  --name "${VM}-work" --new \
  --size-gb 512 --sku Premium_LRS

# 1d. (optional) open SSH only from your IP, not the world
MYIP=$(curl -s ifconfig.me)
az vm open-port -g "$RG" -n "$VM" --port 22 --priority 1000 \
  --address-prefixes "${MYIP}/32"

# 1e. grab the public IP and SSH in
IP=$(az vm show -d -g "$RG" -n "$VM" --query publicIps -o tsv)
echo "ssh ${ADMIN}@${IP}"
```

> **Deallocate when done** (stops billing for compute; keeps disks):
> `az vm deallocate -g "$RG" -n "$VM"`  ·  restart: `az vm start -g "$RG" -n "$VM"`

---

## 2. First-boot: format + mount the work disk

On the VM (`ssh anukriti@<IP>`):

```bash
# Identify the empty data disk (usually /dev/sdc; lsblk to confirm it's the 512G one)
lsblk
sudo parted /dev/sdc --script mklabel gpt mkpart primary ext4 0% 100%
sudo mkfs.ext4 /dev/sdc1
sudo mkdir -p /mnt/work
sudo mount /dev/sdc1 /mnt/work
sudo chown -R "$USER":"$USER" /mnt/work

# persist across reboots
echo "/dev/sdc1  /mnt/work  ext4  defaults,nofail  0  2" | sudo tee -a /etc/fstab
df -h /mnt/work
```

All downloads, alignments, and BAMs live under `/mnt/work` (the 500 GB disk),
never the small OS disk.

---

## 3. Install the toolchain (conda + minimap2 + samtools + StarPhase)

```bash
# 3a. Miniconda (to /mnt/work so it's on the big disk)
cd /mnt/work
curl -sL -o miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash miniconda.sh -b -p /mnt/work/miniconda
eval "$(/mnt/work/miniconda/bin/conda shell.bash hook)"
conda init bash && source ~/.bashrc

# 3b. Alignment + slicing tools (the ENA script requires these)
conda create -y -n lrs -c bioconda -c conda-forge minimap2 samtools curl
# 3c. StarPhase (separate env, same as STARPHASE_SETUP.md)
conda create -y -n starphase -c bioconda -c conda-forge "pbstarphase=1.4.2"

# verify
conda run -n lrs minimap2 --version
conda run -n lrs samtools --version | head -1
conda run -n starphase pbstarphase --version   # 1.4.2-...
```

### 3d. StarPhase prebuilt DB (the `pbstarphase build` gotcha)

`pbstarphase build` is broken against the live CPIC API — use the prebuilt DB
(see `STARPHASE_SETUP.md`):

```bash
cd /mnt/work
curl -sL -o pbstarphase_db.json.gz \
  https://raw.githubusercontent.com/PacificBiosciences/pb-StarPhase/main/data/v1.4.0/pbstarphase_20250515.json.gz
gunzip -kf pbstarphase_db.json.gz       # -> pbstarphase_db.json (~135 MB)
```

### 3e. GRCh38 reference (FULL genome — required for whole-genome alignment)

The ENA script aligns the **whole genome**, so it needs the full GRCh38 FASTA
(chr-prefixed contigs), not the chr22-only file used for local StarPhase runs.

```bash
cd /mnt/work
# UCSC hg38 analysis set (chr-prefixed, matches our BAM contig naming)
curl -sL -o GRCh38.fa.gz \
  https://hgdownload.soe.ucsc.edu/goldenPath/hg38/bigZips/hg38.fa.gz
gunzip -kf GRCh38.fa.gz                  # -> GRCh38.fa (~3.2 GB)
conda run -n lrs samtools faidx GRCh38.fa
# chr22-only FASTA for the StarPhase step (faster to load):
conda run -n lrs samtools faidx GRCh38.fa chr22 > chr22.fa
conda run -n lrs samtools faidx chr22.fa
```

---

## 4. Mount Azure Blob storage (archival)

Whole-genome BAMs are large; archive them to Blob and keep only slices on the
VM. Mount with BlobFuse2.

```bash
# --- create the storage account + container (run locally with az, once) ---
SA=anukritigenomics$RANDOM      # must be globally unique, lowercase
az storage account create -g "$RG" -n "$SA" -l "$LOC" \
  --sku Standard_LRS --kind StorageV2 --access-tier Hot
az storage container create --account-name "$SA" -n genomics-archive
KEY=$(az storage account keys list -g "$RG" -n "$SA" --query "[0].value" -o tsv)
echo "SA=$SA"; echo "KEY=$KEY"   # note these for the VM config below
```

On the VM:

```bash
# install BlobFuse2 (Ubuntu 22.04)
wget https://packages.microsoft.com/config/ubuntu/22.04/packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb && sudo apt-get update
sudo apt-get install -y blobfuse2

# config (fill SA + KEY from the az step above)
mkdir -p /mnt/work/blobcache /mnt/work/archive
cat > /mnt/work/blobfuse.yaml <<'YAML'
allow-other: true
logging:
  level: log_warning
components:
  - libfuse
  - file_cache
  - attr_cache
  - azstorage
file_cache:
  path: /mnt/work/blobcache
azstorage:
  type: block
  account-name: REPLACE_SA
  account-key: REPLACE_KEY
  container: genomics-archive
  mode: key
YAML
sed -i "s/REPLACE_SA/$SA/; s|REPLACE_KEY|$KEY|" /mnt/work/blobfuse.yaml

blobfuse2 mount /mnt/work/archive --config-file=/mnt/work/blobfuse.yaml
df -h /mnt/work/archive          # confirm the Blob container is mounted
```

> Treat `/mnt/work/archive` as cold storage: `mv` the whole-genome sorted BAM
> there after slicing, keep the ~2 MB locus slice + the StarPhase JSON on the
> local disk for scoring.

---

## 5. First job — HG01190 (SAS) end-to-end

Clone the repo and run the existing ENA runner. This is the documented first
job; everything above exists to make it reproducible.

```bash
cd /mnt/work
git clone https://github.com/Abm32/Synthatrial.git anukriti-repo
cd anukriti-repo                 # the 'anukriti' research repo (clinical-grade-pgx branch)
git checkout clinical-grade-pgx

# run: ENA SRR25583344 (7.6 GB FASTQ) -> minimap2 -ax map-ont -> chr22 slice
conda activate lrs
THREADS=16 bash scripts/fetch_ena_cyp2d6_longread.sh /mnt/work/GRCh38.fa /mnt/work/giab_cyp2d6
# -> /mnt/work/giab_cyp2d6/HG01190_CYP2D6_GRCh38.bam (+ .bai), reads-at-locus printed
```

Then StarPhase + score (per `STARPHASE_SETUP.md`):

```bash
cd /mnt/work
printf "CYP2D6\n" > include_cyp2d6.txt
conda run -n starphase pbstarphase diplotype \
  --database pbstarphase_db.json --reference chr22.fa \
  --bam giab_cyp2d6/HG01190_CYP2D6_GRCh38.bam \
  --include-set include_cyp2d6.txt \
  --output-calls giab_cyp2d6/HG01190.starphase.json

# score against the truth set (needs pgx-core 0.6.0 in a python env)
cd anukriti-repo
pip install "anukriti-pgx-core==0.6.0"
python -m src.benchmark.cyp2d6_starphase_runner --calls-dir /mnt/work/giab_cyp2d6
# HG01190 (SAS) truth = *68+*4/*5 -> Poor Metabolizer. Expect SAS row 1.000/1.000.
```

Archive + free space:

```bash
mv /mnt/work/giab_cyp2d6/HG01190_GRCh38.sorted.bam* /mnt/work/archive/   # whole-genome BAM -> Blob
# keep the locus slice + HG01190.starphase.json locally for re-scoring
```

---

## 6. Subsequent samples (same path)

The other 1000G truth-set samples are also FASTQ-only at ENA — same runner,
new accession (edit `SRR`/sample in a copy of the script, or generalize it):

| Sample | Pop | ENA run | Truth (GeT-RM) |
|---|---|---|---|
| HG01190 | SAS | SRR25583344 | `*68+*4/*5` → PM |
| NA19785 | (1000G) | SRR25583343 | `*1/*13+*2` |
| (GIAB HG001/HG002/HG005) | — | — | use the **indexed** `fetch_giab_cyp2d6_longread.py` slicer instead (no alignment needed) |

---

## 7. Teardown / cost hygiene

```bash
# stop billing for compute (keeps disks + Blob):
az vm deallocate -g "$RG" -n "$VM"
# fully remove everything when the sandbox is no longer needed:
az group delete -n "$RG" --yes --no-wait
```

---

## Companion docs

- `STARPHASE_SETUP.md` — StarPhase install + prebuilt-DB gotcha + scoring.
- `CYP2D6_SV_PIPELINE.md` — the end-to-end engine/endpoint/benchmark map.
- `RUNG2_CYP2D6_SV_PLAN.md` — the roadmap (Phase A/B′/C).
- `GIAB_ARTIFACT_BACKUP.md` — Azure Blob backup of the validation artifacts (note: `anukriti-lrs-01` is a **resource group** there, vs. a **VM** name here).
- `anukriti/scripts/fetch_ena_cyp2d6_longread.sh` — the ENA align/slice runner.
