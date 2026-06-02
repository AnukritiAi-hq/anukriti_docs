# Detection & Classification Roadmap — How Deep Can We Go Into the Genome

> **Audience:** founder + any session extending the calling/detection layer.
>
> **Last updated:** 2026-06-02
>
> **Purpose:** answer three questions concretely — (1) how *micro* can our
> detection get, (2) what variant classes can we call and classify and to
> what confidence level, (3) which genome formats can we ingest. Every rung
> is mapped to the paper(s)/tool(s) that enable it and whether they are
> **open** or **paywalled / buy**.
>
> **Companion docs:**
>   - [`papers/README.md`](papers/README.md) — the curated bibliography this extends
>   - [`DETERMINISTIC_ENGINE_DEEP_DIVE.md`](DETERMINISTIC_ENGINE_DEEP_DIVE.md) — what the calling/phenotype layers do today
>   - [`IWPC_VALIDATION_DEEP_DIVE.md`](IWPC_VALIDATION_DEEP_DIVE.md) — §5a CPIC audit (the "audit is the contract" posture)

---

## TL;DR

- Today the engine is **genotype-in, not signal-in**: pgx-core Layer 1
  consumes an rsID→genotype map (SNVs extracted from a VCF) and resolves
  star-alleles for 13 genes. We do **not** call variants from reads, do
  **not** detect structural variants (CYP2D6 CNVs are heuristic-only), and
  skip multi-rsID haplotypes (NAT2 / CYP2B6).
- The path "deeper" is a 6-rung ladder (Rung 0 = today → Rung 5 = pangenome
  graph + genome-wide SV).
- **Access reality (verified 2026-06-02):** almost every tool that unlocks
  the next rungs is **fully open access** — PyPGx, Cyrius, Aldy, StellarPGx,
  GeT-RM, GenomeAsia100K, VEP, CADD. Only two primary papers sit behind
  publisher paywalls (**AlphaMissense** = Science, **SpliceAI** = Cell), and
  **both ship open precomputed data + open code/reimplementation**, so a
  purchase is *nice-to-have for the methods text, not required to build*.

---

## 1. The detection ladder (Rung 0 → Rung 5)

| Rung | Capability | What it detects | Confidence ceiling | Status |
|---|---|---|---|---|
| **0** | **Known SNV → star-allele → phenotype** | Single-nucleotide variants at known rsIDs; star-allele diplotype; CPIC PM/IM/NM/RM/UM | Deterministic, CPIC-pinned, evidence_level A–D | **Shipped** (13 genes) |
| **1** | **Full diplotype calling from VCF** | Multi-rsID haplotypes (NAT2, CYP2B6); proper named-allele matching incl. indels | Tool-concordant (PharmCAT/PyPGx-aligned) | Partial — multi-rsID skipped today |
| **2** | **Structural / copy-number on CYP2D6** | Gene deletions (\*5), duplications (\*1xN→UM), **CYP2D6–CYP2D7 hybrids** | Cyrius 96.5% concordance (vs 84–86.8% today's heuristics) | **Heuristic-only today** — biggest single PGx accuracy win |
| **3** | **Call variants from reads (BAM/CRAM)** | SNVs + small indels discovered from pileups, not pre-called VCF | DeepVariant ≥ GATK best-practices | Not started — prerequisite for novel-variant work |
| **4** | **Novel / population-private variant classification** | Variants absent from gnomAD/1000G (the Kerdoncuff frontier: ~24M SNVs + ~2.2M indels) + functional-effect call | VEP consequence + CADD/AlphaMissense/SpliceAI score | Not started — the true India-specific differentiator |
| **5** | **Genome-wide SV + pangenome-graph alignment** | Large SVs short-read misses; graph-aware calls | minigraph-cactus / long-read | Longer horizon |

**Why Rung 2 is the priority:** CYP2D6 metabolizes ~21–25% of clinically
used drugs; its UM/PM calls are driven by exactly the deletions /
duplications / CYP2D7 hybrids we currently approximate. It is the highest
accuracy-per-effort jump and closes a named gap in our honest-gap list.

**Why Rung 4 is the moat:** classifying a *novel* variant's effect — not
just looking it up — is what no existing PGx system does for South Asian
populations. This is where the Kerdoncuff / GenomeAsia variant catalogs
meet functional predictors. It is also where the "every claim cites a rule,
every rule cites a paper" posture must extend to "every novel-variant call
cites a predictor + its score + its calibration."

---

## 2. What we can classify, and to what level

| Variant class | Detect today? | Rung to reach it | Classification output |
|---|---|---|---|
| SNV at known rsID | ✅ | 0 | star-allele → phenotype + CPIC level |
| Small indel (known) | partial | 1 | named-allele match |
| Multi-rsID haplotype (NAT2, CYP2B6) | ❌ | 1 | full diplotype |
| Gene deletion / duplication (CNV) | heuristic | 2 | \*5, \*1xN, activity-score adjust |
| CYP2D6–CYP2D7 hybrid | ❌ | 2 | hybrid allele call |
| Novel SNV/indel (not in dbSNP/gnomAD) | ❌ | 3→4 | consequence + pathogenicity/splice score |
| Population-private variant (India-specific) | ❌ | 4 | freq vs GenomeAsia/Kerdoncuff + predicted effect |
| Large/genome-wide SV | ❌ | 5 | graph-aware SV call |

Confidence framing per rung must stay inside the existing evidence
discipline: deterministic call where a rule table exists (Rungs 0–2), and
**named-uncertainty** (predicted, not asserted) for anything resolved by a
statistical/ML predictor (Rungs 3–5). A predicted effect is never allowed
to enter the decision path — it annotates, the way the LLM narrates.

---

## 3. Genome-format support matrix

| Format | Have today | Add at rung | Why |
|---|---|---|---|
| VCF / VCF.gz (tabix) | ✅ | — | current ingestion |
| GRCh37 + GRCh38 + liftover | ✅ | — | `pharmcat_comparison.py` |
| 1000G phase-3 panel | ✅ | — | reference allele freqs |
| **gVCF** | ❌ | 1–3 | reference-confidence blocks → "absence of variant is informative" (Huddart) + DeepVariant-native |
| **BCF** (binary VCF) | stub (`bcf_processor.py`) | 1 | scale; finish the existing stub |
| **BAM / CRAM** (reads) | ❌ | 3 | read-level calling + SV evidence |
| **PharmCAT JSON** | read-only (benchmark) | 1 | interchange w/ the de-facto standard |
| **PharmVar allele-definition** | ❌ | 1–2 | canonical star-allele source (Gaedigk contact) |
| **PLINK2 pgen** | ❌ | 4 | cohort-scale frequency / PRS |
| **GFA / pangenome graph + graph-VCF** | ❌ | 5 | graph-aware alignment |
| **FHIR Genomics** | partial (FHIR R4 export) | any | clinical interchange |

---

## 4. Papers / tools needed per rung — open vs. paywalled

> **Access verified 2026-06-02 via literature search.** "Open" = freely
> readable (PMC / CC / publisher OA). "Paywalled" = primary paper behind a
> publisher subscription. Tool license noted separately where it matters
> (commercial-use restrictions can apply even when the paper is free).

### Rung 1 — full diplotype calling

| Item | Ref | Access | Note |
|---|---|---|---|
| PharmCAT | Sangkuhl/Whirl-Carrillo 2020 (CPT) | **Open** | de-facto standard; we already benchmark against it |
| PharmVar nomenclature | Gaedigk et al. (PharmVar consortium) | **Open** | canonical star-allele definitions; founder has a PharmVar contact |
| GeT-RM reference materials | Pratt 2010 (JMD, PMC2962854); Pratt 2016 (137 RMs/28 genes, CDC stacks); Gaedigk/Pratt 2019 CYP2D6 (JMD 21(6):1034, PMC6854474) | **Open** | Coriell cell lines = our benchmark truth set; `getrm_truth.py` already exists |

### Rung 2 — CYP2D6 structural / CNV (priority)

| Item | Ref | Access | Note |
|---|---|---|---|
| **Cyrius** | Chen et al. 2021, *Pharmacogenomics J* 21:251 (PMC7997805) | **Open** (CC-BY) | 96.5% CYP2D6 concordance; del/dup + CYP2D6–CYP2D7 hybrids; GitHub Illumina/Cyrius |
| **PyPGx** | Sherman, Claw & Lee 2024, *Sci Reps* 14:22774 (PMC11445439) | **Open** (CC-BY) | ML SV detection (del/dup/hybrid) across 58 pharmacogenes; NGS + SNP-array + long-read; PyPI + ReadTheDocs |
| **Aldy** | Numanagić et al. 2018, *Nat Commun* 9:828; Aldy 4 (2023) *Genome Res* 33:61 | **Open** | allelic decomposition + CNV + novel-allele detection |
| **StellarPGx** | Twesigomwe et al. 2021 (PMC, *Clin Transl Sci* / Front) | **Open** | Nextflow, **genome-graph** variant detection, **African-genome validated** — closest tool to our equity angle |
| *Audit artifact* | Front Pharmacol 2025, doi 10.3389/fphar.2025.1584658 | **Open** | 19.4% of GeT-RM diplotypes outdated across Aldy/PyPGx/StellarPGx — a ready-made "audit is the contract" artifact |
| *Review* | Twesigomwe 2025, *Annu Rev Genomics Hum Genet* 26:321 | check | diverse-population PGx review |

### Rung 3 — variant calling from reads

| Item | Ref | Access | Note |
|---|---|---|---|
| **DeepVariant** | Poplin et al. 2018, *Nat Biotech* | **In repo** | already in `papers/`; CNN pileup caller; outputs gVCF |

### Rung 4 — novel-variant functional classification (the moat)

| Item | Ref | Access | Note |
|---|---|---|---|
| **GenomeAsia 100K** | Nature 2019, 576(7785):106–111 (PMC7054211) | **Open** | 1,739 WGS / 219 groups / 64 Asian countries; founder effects; South Asian allele freqs |
| **Kerdoncuff 2025** | *Cell* 188(13):3389–3404 | **In repo** | India WGS variant catalog; ~24M SNVs + ~2.2M indels absent from gnomAD/1000G |
| **gnomAD** | Karczewski 2020, Nature | **Open** | global freq baseline + LoF constraint methodology |
| **VEP** | McLaren 2016, Genome Biol | **Open** | variant-consequence annotation |
| **CADD** | Rentzsch 2019, NAR | **Open** | deleteriousness score |
| **AlphaMissense** | Cheng et al. 2023, *Science* adg7492 (PMID 37733863) | **Paywalled** (Science) — *predictions DB open* | predicts 71M missense; **predictions CC-BY-NC-SA (non-commercial)**, model code Apache. Buy the paper only for the methods text |
| **SpliceAI** | Jaganathan et al. 2019, *Cell* 176(3) (PMID 30661751) | **Paywalled** (Cell) — *scores + reimpl open* | splice-effect predictor; tool GPLv3 + CC-BY-NC; precomputed scores open; **OpenSpliceAI** (JHU) is a fully-open reimplementation |

### Rung 5 — genome-wide SV + pangenome

| Item | Ref | Access | Note |
|---|---|---|---|
| Human Pangenome Reference | Liao et al. 2023, Nature; Hickey 2023 (minigraph-cactus) | **Open** | summary already in `papers/human-pangenome-reference-2023.md` |

---

## 5. The "please buy" list — short and honest

After verification, the genuinely-paywalled primary papers are only:

1. **AlphaMissense** — Cheng 2023, *Science*. *Optional.* The 71M-variant
   prediction database is openly downloadable (CC-BY-NC-SA) and the model
   code is Apache-licensed — we can use the predictions for Rung 4 without
   the paper. Buy only if we want the methods/calibration text for our own
   citation-grade write-up. **Note the non-commercial license** on the
   predictions before any commercial deployment.
2. **SpliceAI** — Jaganathan 2019, *Cell*. *Optional.* Precomputed scores
   are open and **OpenSpliceAI** (JHU, PyTorch) is a fully-open
   reimplementation we can run/retrain freely. Buy only for the methods text.

**Everything else on every rung is open access** and I can pull
summaries/methods directly. So the net "you need to pay" answer is: *very
little — at most these two, and even then only for the prose, not the data.*

---

## 6. Recommended sequencing

1. **Rung 2 first (CYP2D6 SV/CNV)** — biggest accuracy win, closes a named
   gap, all tools open. Evaluate Cyrius vs PyPGx vs StellarPGx against the
   GeT-RM Coriell truth set (we have `getrm_truth.py`), pick one, integrate
   behind the off-by-default constructor-arg pattern.
2. **Rung 1 cleanup** (NAT2 / CYP2B6 multi-rsID) — same toolchain, falls
   out of the Rung-2 caller choice.
3. **Rung 3** (DeepVariant / gVCF ingestion) — unlocks read-level input.
4. **Rung 4** (novel-variant classification over GenomeAsia + Kerdoncuff
   catalogs with VEP + CADD + AlphaMissense/SpliceAI predictions) — the moat.
5. **Rung 5** (pangenome) — longer horizon.

Each integration follows platform invariants: predictors **annotate**, they
never enter the decision path; every predicted call carries its score,
source, and calibration as named uncertainty; new capability ships
off-by-default via constructor args.
