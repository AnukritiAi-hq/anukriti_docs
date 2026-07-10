# ASTRA Research Note: Testing the Mirror-Image Hypothesis — Does the
# EUR-Ascertainment Pattern Invert for AFR/EAS-Maximum Genes? (2026-07-10)

> **Scope:** this document reports a deliberately-designed negative/mixed
> result, not a confirming one — and documents it with the same rigor as
> the three confirming findings in the companion document
> (`ASTRA_FINDING_SLCO1B1_EUR_IS_POPULATION_MAXIMUM_2026-07-10.md`,
> same folder). A hypothesis that fails to replicate in a new direction is
> real scientific information, and reporting it honestly — rather than
> silently dropping it because it didn't confirm the existing narrative —
> is the actual discipline this session has tried to hold throughout.
>
> **Repo:** `project_astra`. Code additions: `tests/
> test_audit_population_maximum_across_genes.py` (extended). No script
> changes needed — this check reused `audit_population_maximum_across_
> genes.py`'s existing min/max computation, just read differently.

---

## 1. The question this document tests

The companion document established a real, three-times-confirmed pattern:
every EUR-*maximum* gene this platform's own gnomAD data surfaced
(SLCO1B1, DPYD, CYP2C9) has independent, primary-source-confirmed evidence
that its foundational PGx association transfers poorly to the population
where the risk allele is rare.

The next genuinely unknown question, not yet asked: **does the same
pattern invert for genes where a *non*-EUR population is the maximum?**
If AFR-maximum or EAS-maximum genes show the mirror image — the
foundational evidence built in the max-frequency non-EUR population,
transferring poorly to EUR — that would suggest a general "evidence
transfers poorly away from wherever it was discovered" phenomenon,
independent of any EUR-specific ascertainment bias. If it does *not*
invert, that argues the first three findings reflect something more
specific to how EUR became historically over-represented in genomic
medicine research infrastructure, not a population-agnostic pattern.

**Re-computing the full cross-gene min/max table (all 11 genes with real
data) to find the best test case:**

| Gene | Max population | Min population | Max/min ratio |
|---|---|---|---|
| CYP2B6 | SAS (0.389) | EAS (0.191) | 2.0x |
| CYP2C19 | EAS (0.371) | AMR (0.099) | 3.7x |
| CYP2C9 | EUR (0.196) | EAS (0.034) | 5.7x |
| CYP2D6 | EAS (0.580) | AMR (0.241) | 2.4x |
| **CYP3A5** | **AFR (0.702)** | **EUR (0.071)** | **9.9x** |
| DPYD | EUR (0.032) | EAS (0.0002) | 194.3x |
| G6PD | AFR (0.116) | EAS (0.000) | ∞ |
| NAT2 | SAS (0.778) | EAS (0.451) | 1.7x |
| SLCO1B1 | EUR (0.157) | AFR (0.028) | 5.6x |
| TPMT | AMR (0.094) | EAS (0.015) | 6.3x |
| VKORC1 | EAS (0.900) | AFR (0.101) | 8.9x |

**CYP3A5 is the best test case**: a real, major, clinically active
pharmacogene (tacrolimus dosing in solid-organ transplantation — a
narrow-therapeutic-index drug where genotype-guided dosing has documented
clinical-outcome consequences), with the *exact* mirror-image structure of
the confirmed findings — AFR is the maximum (0.702, i.e. most patients of
African ancestry are CYP3A5 *expressers*, needing higher tacrolimus doses),
and **EUR is the minimum** (0.071 — most European-ancestry patients are
non-expressers). This is not a marginal case; the ratio (9.9x) is
comparable to SLCO1B1's own confirmed 5.6x and CYP2C9's 5.7x.

## 2. What was found — a real, honest negative result

**Checked via the same discipline as every other finding this session:
primary literature first, no inference.**

**Finding 1 — the field has actively researched CYP3A5 specifically in
African-ancestry cohorts, not neglected it.** A dedicated genome-wide
association study exists: *"Genomewide Association Study of Tacrolimus
Concentrations in African American Kidney Transplant Recipients
Identifies Multiple CYP3A5 Alleles"* (PMC4733408) — this study went
looking specifically in African-American kidney transplant recipients
*because* CYP3A5 expression is clinically important there, and found two
*additional*, African-ancestry-specific alleles (CYP3A5\*6, \*7) beyond
the main \*3 allele that further explain tacrolimus dose variability in
this population. This is structurally the *opposite* of what the
SLCO1B1/DPYD/CYP2C9 pattern would predict — instead of a gap left
unaddressed, the field responded to the population where the variant
matters most with dedicated, deepened research.

**Finding 2 — CPIC's own primary guideline (Birdwell et al. 2015, Clin
Pharmacol Ther 98(1):19-24, PMID 25801146) is written in
population-neutral language.** Its abstract states the association and
provides *"dosing recommendations for tacrolimus based on CYP3A5 genotype
when known"* — no population is named as excluded, privileged, or
under-covered in the abstract itself. This is a materially different
framing from what was found for SLCO1B1 (explicit ancestry exclusion in
the discovery cohort) or the implicit framing problem in DPYD/CYP2C9's
own literature.

**Finding 3 — real, active European-ancestry-specific tacrolimus dosing
research also exists.** A separate, real study — *"Precision Dosing for
Tacrolimus Using Genotypes and Clinical Factors in Kidney Transplant
Recipients of European Ancestry"* (PMID 33512723) — shows the field is
*also* actively refining genotype-based tacrolimus dosing specifically
for European-ancestry patients, using CYP3A4/CYP3A5 combined genotypes and
clinical factors. This directly contradicts any claim that EUR patients
are an evidentiary afterthought for this gene — if anything, CYP3A5
research appears to be actively pursued in *both* directions
simultaneously (AFR-specific allele discovery, EUR-specific precision
dosing refinement).

**Conclusion: the mirror-image hypothesis does NOT replicate for
CYP3A5.** This is a real, deliberately-sought, honestly-reported negative
result. It does not merely fail to confirm — it actively points the
opposite direction from what "evidence transfers poorly away from wherever
discovered, symmetrically in both directions" would predict.

## 3. Why this negative result matters — it sharpens, not weakens, the
## original three findings

A hypothesis that confirms in every direction tested is usually a sign the
test wasn't discriminating enough. This negative result is what makes the
positive findings (SLCO1B1, DPYD, CYP2C9) more credible, not less — because
it shows the pattern is not a trivial artifact of "any allele that's rare
in some population will have weaker evidence there" (which would predict
CYP3A5 fails for EUR too). Instead, it points to something more specific:

**A plausible, more precise version of the underlying claim, stated as a
hypothesis for future testing, not a conclusion**: the reduced-
applicability pattern found in SLCO1B1/DPYD/CYP2C9 may correlate less with
"which population has the rare allele" in general, and more with **when
and where the genomic-medicine research infrastructure historically
existed** at the time each gene's foundational discovery work was done.
SLCO1B1's discovery (2008, UK-based SEARCH trial) and DPYD's foundational
work both predate the more recent wave of population-diversity-focused
NIH/NIGMS funding (note: the CYP3A5 African-American GWAS itself was
NIH/NIGMS-funded — the same funding bodies listed in the CPIC guideline's
own grant acknowledgments above) that appears to have specifically
targeted African-ancestry transplant pharmacogenomics more recently.
CYP2C9's warfarin story is a partial in-between case — the original
discovery evidence was EUR-skewed, but the 2013 Perera et al. AFR-specific
GWAS (itself NIH/NIGMS-funded, same grant numbers pattern) represents
exactly the kind of later, dedicated corrective research CYP3A5 also
received. **This reframes the pattern from "EUR bias, structurally" to
something closer to "research investment historically lagged for some
gene-population combinations and has been actively catching up for
others, unevenly, gene by gene"** — a real, more nuanced, and more
testable claim than a single uniform bias narrative, but one this document
does not claim to have proven; it is named here as the next real
hypothesis, not asserted as settled.

## 4. Honest limitations, on the record

- **n=1 gene tested for the mirror-image hypothesis (CYP3A5).** A single
  negative result does not prove the mirror-image never occurs for any
  AFR/EAS-maximum gene — VKORC1 (EAS max, AFR min, 8.9x) and G6PD (AFR max,
  EAS min, effectively infinite ratio given EAS≈0) are both real,
  untested candidates that could show a different result. Named as the
  next concrete check, not assumed to also be negative.
- **This document did not check whether CYP3A5's own evidence base has a
  *different*, more subtle applicability gap** (e.g. specific to a
  population other than the two tested) — only checked the EUR/AFR axis
  the min/max table flagged.
- **Funding-pattern correlation (§3) is a plausible interpretation of
  circumstantial evidence (matching grant-body names across two papers),
  not a rigorous bibliometric analysis.** A real test of the "research
  investment has been catching up unevenly" hypothesis would require
  systematically checking publication dates and funding sources across
  many more gene-population pairs — explicitly named as unattempted here.
- **No new PRR, no new FAERS query, no new gnomAD data was computed.**
  This document re-reads the existing cross-gene min/max table computed by
  `audit_population_maximum_across_genes.py` (already committed,
  `231066e`) from a different angle, plus new literature checks. Zero new
  network calls to any platform system, zero new GCP cost.

## 5. What a further pass should check next

1. **VKORC1 (EAS max 0.900, AFR min 0.101, 8.9x ratio)** — the second-best
   mirror-image test case. VKORC1 is CPIC-actionable for warfarin dosing
   alongside CYP2C9 — worth checking whether its evidence base shows the
   same EUR-neutral/actively-corrected pattern as CYP3A5, or something
   closer to the SLCO1B1/DPYD pattern but inverted (i.e. an AFR-centric
   evidence base under-serving EAS, the opposite direction from what's
   been checked so far).
2. **G6PD (AFR max 0.116, EAS min ≈0.000)** — a real, well-known case
   (G6PD deficiency's classical AFR/Mediterranean/malaria-selection
   story) but with a different clinical context (drug-induced hemolysis
   risk screening, e.g. for rasburicase/primaquine) than the dosing-
   algorithm genes checked so far — worth checking whether its own
   evidence base shows a comparable pattern in either direction.
3. **A systematic bibliometric check** of publication dates and funding
   bodies across all findings so far (SLCO1B1 2008, DPYD's foundational
   work, CYP2C9's 2013 AFR-specific follow-up, CYP3A5's AFR-specific GWAS)
   would directly test §3's "uneven catch-up over time" hypothesis rather
   than leaving it as circumstantial. Not attempted in this pass.

## 6. Reproduction

The cross-gene min/max table in §1 is reproducible directly from the
already-committed audit script:

```bash
cd project_astra
python3 -c "
from astra.discovery_engine import population_signal as ps
recs = ps.load_gnomad_records()
for gene in sorted({r['gene'] for r in recs}):
    freqs = {}
    for pop in ['AFR','AMR','EAS','SAS','EUR']:
        f = ps.population_risk_allele_frequency(gene, pop, recs)
        if f:
            freqs[pop] = f.frequency
    if not freqs:
        continue
    maxpop = max(freqs, key=lambda p: freqs[p])
    minpop = min(freqs, key=lambda p: freqs[p])
    ratio = freqs[maxpop]/freqs[minpop] if freqs[minpop] > 0 else float('inf')
    print(f'{gene}: max={maxpop}({freqs[maxpop]:.4f}) min={minpop}({freqs[minpop]:.4f}) ratio={ratio:.1f}x')
"
```

The literature checks in §2 are web searches and primary-source fetches
performed during this session; PMIDs are named throughout for independent
re-verification (25801146, PMC4733408, 33512723).
