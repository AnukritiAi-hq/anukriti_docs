# Module 03 — Core Concepts

> Prerequisites: [01 What is Anukriti](01-what-is-anukriti.md)
>
> This is the biomedical primer. If you already work in
> pharmacogenomics, skim for notation and skip to [Module 04](04-architecture.md).

---

## The question we're answering

What minimum biology and clinical-pharmacology vocabulary do you
need to read the rest of the course?

---

## The chain from DNA to drug response

Here's the 30-second version of everything in this module:

```
DNA    ──→    gene    ──→    protein    ──→    enzyme activity    ──→    drug response

 ↑             ↑                ↑                    ↑                        ↑
 A,C,G,T      ~20,000 of        made from            how fast does            does the drug
 sequence     them in humans    the gene's           this enzyme convert      work, not work,
              each has          recipe               substances (including    or hurt?
              variants                                drugs)
```

The first two arrows are biology. The third is biochemistry. The
fourth is pharmacology. Pharmacogenomics is the discipline that
says **your personal variants in the first arrow predict the last
arrow**.

---

## Genes and variants

A **gene** is a stretch of DNA that codes for a protein. Humans have
around 20,000 genes. We all carry two copies of each gene — one from
each parent.

A **variant** is a place in the DNA where humans differ from each
other. The most common kind is a **single nucleotide polymorphism**
(SNP, pronounced "snip") — one letter is different. At position X
in gene Y, most people have a C; some people have a T. The C version
and the T version may produce proteins that behave differently.

**Variants are identified by `rsID`s.** These are stable
identifiers assigned by dbSNP (a NIH database) — e.g.
`rs4244285`. That particular variant sits inside the CYP2C19 gene.

**Each person has two copies of every gene**, so any variant has
two readings — one per copy. Notation:

- `rs4244285: C/C` — both copies have C (homozygous for C)
- `rs4244285: C/T` — one C, one T (heterozygous)
- `rs4244285: T/T` — both have T (homozygous for T)

---

## What's a "pharmacogene"?

A **pharmacogene** is a gene whose variants have a documented
clinical effect on how a drug works. Not every gene is a
pharmacogene. Of the 20,000 human genes, only a few dozen are
clinically actionable for specific drugs.

The platform's focus is on a specific set of 13 pharmacogenes:

| Gene | Encodes | Relevant for |
|------|---------|-------------|
| CYP2D6, CYP2C19, CYP2C9, CYP3A4, CYP3A5 | Cytochrome P450 enzymes | Many drugs (antidepressants, antiplatelets, anticoagulants, opioids) |
| CYP1A2, CYP2B6 | More P450s | Antipsychotics, antiretrovirals |
| DPYD | Dihydropyrimidine dehydrogenase | Fluoropyrimidine chemotherapy |
| TPMT | Thiopurine S-methyltransferase | Thiopurine drugs |
| NAT2 | N-acetyltransferase 2 | Isoniazid (TB treatment) |
| G6PD | Glucose-6-phosphate dehydrogenase | Oxidative-stress drugs |
| VKORC1 | Vitamin K epoxide reductase | Warfarin |
| SLCO1B1 | Drug transporter | Statins |

Most of these are "enzyme activity" genes — they determine how fast
you metabolize (convert) a drug into its active form or clear it
from the body. Some are "transporter" genes — they determine whether
the drug gets into cells where it needs to act.

---

## Star alleles — the CYP family's naming system

Here's where pharmacogenomics gets its own notation.

The CYP (Cytochrome P450) family of genes uses a system called
**star alleles**. An "allele" is a specific version of a gene. Star
alleles are named with an asterisk and a number:

```
CYP2C19 *1       ← the "reference" or "wild-type" allele
CYP2C19 *2       ← an allele with a specific variant (rs4244285: G→A)
CYP2C19 *3       ← a different variant
CYP2C19 *17      ← a variant that INCREASES activity
```

Each star allele is defined by one or more specific variants
(rsIDs). The star-allele name is a **short alias** for "this
particular combination of variants at these rsID positions."

Because each person has two gene copies, their **diplotype** is
written:

```
*1/*1     — both copies are reference  (wild-type)
*1/*2     — one reference, one *2
*2/*2     — both *2
*1/*17    — one reference, one *17 (one gain-of-function copy)
```

The **diplotype** is the quantity the phenotype engine takes as
input.

PharmVar (<https://pharmvar.org>) is the canonical registry — which
rsIDs define which star alleles, maintained by a scientific
consortium.

### One subtlety: ordering

Star alleles are ordered by a specific convention (numeric-suffix
ordering: `*2/*17`, not `*17/*2`). This matters because the
phenotype lookup table is keyed on the ordered diplotype.
pgx-core handles this correctly; some legacy tooling doesn't,
which is discussed in pgx-core's `PROJECT_CONTEXT.md` §D2.

---

## From diplotype to phenotype

Two systems for translating a diplotype into a clinical label:

### System 1: The activity score

Each allele has a numeric activity:

| Allele | Activity |
|--------|----------|
| *1 (reference) | 1.0 |
| *2 (loss of function) | 0.0 |
| *17 (gain of function) | 1.5 |

A diplotype's **activity score** is the sum of the two alleles'
activities. The activity score maps to a **phenotype bin**:

| Activity score | Phenotype |
|----------------|-----------|
| 0.0 | Poor Metabolizer (PM) |
| 0.25–1.25 | Intermediate Metabolizer (IM) |
| 1.25–2.25 | Normal Metabolizer (NM) |
| 2.25+ | Rapid or Ultrarapid Metabolizer (RM/UM) |

So `CYP2C19 *2/*2` → 0.0 + 0.0 → 0.0 → **PM**.
And `CYP2C19 *1/*17` → 1.0 + 1.5 → 2.5 → **UM** or **RM** (depends
on the specific cutoff).

### System 2: Named-diplotype table lookup

For some genes, CPIC publishes an explicit table: "if the diplotype
is *X/*Y, the phenotype is Z." This is used where the additive
model would produce the wrong answer. Example:

- CYP2C19 *2/*17: additive score is 1.0 (NM boundary). But CPIC
  2022 Table 2 explicitly assigns this diplotype to **IM** because
  loss-of-function dominates over gain-of-function. Named-diplotype
  lookup wins.

The pgx-core engine **prefers named-diplotype table lookup**, and
falls back to the additive model only when no named entry exists.

### The categorical result

The phenotype is one of:

| Abbrev. | Name | What it means |
|---------|------|---------------|
| PM | Poor Metabolizer | Very low enzyme activity |
| IM | Intermediate Metabolizer | Reduced activity |
| NM | Normal Metabolizer | Typical activity |
| RM | Rapid Metabolizer | Increased activity |
| UM | Ultrarapid Metabolizer | Very high activity |

For a drug that is **active as prescribed** (like most drugs), PMs
are at higher risk of side effects (too much drug hanging around),
UMs are at risk of therapeutic failure (drug cleared too fast).

For a drug that is a **prodrug** (needs conversion, like
clopidogrel), the logic inverts: PMs can't activate the drug;
UMs may get too much activation too fast.

---

## CPIC and guideline versioning

**CPIC** (Clinical Pharmacogenetics Implementation Consortium) is a
joint project of the NIH and the Pharmacogenomics Knowledgebase.
Their deliverable is a set of published, peer-reviewed guidelines:

> "For patients with CYP2C19 Poor Metabolizer phenotype receiving
> clopidogrel, consider prasugrel or ticagrelor instead. Strength
> of recommendation: Strong. Level of evidence: High."

That's the kind of statement CPIC issues. Every guideline has:

- A **genotype/phenotype → recommendation** mapping
- A **strength classification** (Strong, Moderate, Optional)
- A **level of evidence** classification
- A **publication date** and **table version**

CPIC guidelines are updated periodically as new evidence emerges.
Example: CPIC 2019 restandardized the activity-score ranges for
CYP2D6, causing score 1.5 to move from IM range to NM range.

**This is why pgx-core pins CPIC tables by version.** A file named
`CYP2C19_named_diplotypes_v2022.1.json` is the 2022.1 version of
that table. A new CPIC release becomes a new file with a new
version; the old file stays in the tree for historical reproducibility.
Versions don't silently overwrite each other.

See [Module 06](06-why-deterministic.md) for the "why" on this
obsessive versioning discipline.

---

## VCF files — how genotype data comes in

A **VCF** (Variant Call Format) file is the standard output of
genome sequencing pipelines. It's a tab-separated file where each
row represents one variant position:

```
#CHROM  POS      ID           REF  ALT  ...  SAMPLE1
10      94842866 rs4244285    G    A    ...  1/1
10      94852738 rs4986893    G    A    ...  0/0
22      42126611 rs3892097    C    T    ...  0/1
...
```

Read the columns as:

- `#CHROM` — the chromosome (10, 22, etc.)
- `POS` — the base-pair position on that chromosome
- `ID` — the rsID (the SNP identifier)
- `REF` — the reference-genome nucleotide at this position
- `ALT` — the variant nucleotide (the "other" letter seen)
- `SAMPLE1` — this particular sample's genotype: `0/0` means
  homozygous reference, `1/1` means homozygous variant, `0/1` or
  `1/0` means heterozygous

So `rs4244285: 1/1` means both copies of the gene carry the
`ALT` allele (`A`), not the reference `G`. Translating to
pharmacogenomics: `CYP2C19 *2/*2`.

**The "VCF → diplotype" translation is exactly what the pgx-core
gene callers do.** Module 05 walks through this in detail.

---

## Populations and ancestry

Variant frequencies differ across populations:

| rsID | EUR | EAS | SAS | AFR |
|------|-----|-----|-----|-----|
| rs4244285 (CYP2C19 *2) | 14% | 30% | 36% | 17% |
| rs4149056 (SLCO1B1 *5) | 15% | 1% | 10% | 1% |
| rs1057910 (CYP2C9 *3) | 7% | 3% | 11% | 1% |

These population codes come from the **1000 Genomes Project** and
**gnomAD**:

- **EUR** — European ancestry
- **EAS** — East Asian ancestry
- **SAS** — South Asian ancestry
- **AFR** — African ancestry
- **AMR** — Admixed American ancestry (Latino)

These are **super-populations**. Each has sub-populations (e.g.
SAS-GIH for Gujarati Indians in Houston). The platform mostly
operates at the super-population level because that's where public
frequency data is richest.

### Why ancestry matters clinically

If 36% of a South Asian population carries *CYP2C19 \*2*, the
probability that a random SAS patient has *CYP2C19 \*2/\*2* (both
copies) is ~13% — roughly the "14%" statistic from Module 01.

Population-blind clinical guidelines effectively assume Eurocentric
variant frequencies. They're right for the 14% EUR carrier rate and
wrong for the 36% SAS rate. That's the gap that justifies making
ancestry a first-class input.

We'll revisit population reasoning in depth in [Module 08](08-population-awareness.md).

---

## A vocabulary checkpoint

If these terms feel alien, go back and re-skim. If they feel
manageable, you're ready for Module 04.

- **gene**, **allele**, **variant**, **rsID**
- **diplotype**, **star allele**, **activity score**
- **phenotype** — PM / IM / NM / RM / UM
- **CPIC**, **PharmVar**
- **VCF**, **REF**, **ALT**, **genotype field** (0/0, 0/1, 1/1)
- **super-population** — EUR, EAS, SAS, AFR, AMR

Full definitions are in [Module 12 Glossary](12-glossary.md).

---

## Summary

You now know:

- **Genes have variants** identified by rsIDs; each person has two
  copies, yielding genotype combinations.
- **Star alleles** are a pharmacogenomics-specific naming scheme for
  combinations of variants within CYP genes.
- **Diplotype → phenotype** is the core translation, done either by
  additive activity score or by named-diplotype table lookup.
- **CPIC** is the clinical authority whose guidelines we pin by
  version.
- **VCF files** are the standard input format; pgx-core callers
  translate them to star alleles.
- **Population frequencies vary** by ancestry; population-blind
  guidelines produce Eurocentric results.

Next: [Module 04 — Architecture](04-architecture.md). We return to
engineering, with the biomedical vocabulary ready.
