# Clinality Deep Research — the Claim Survives Rescoring, the Novelty Is
# Narrower Than Drafted, and the Bottleneck Has One Real Route (2026-08-16)

> **Purpose.** Two research passes plus an independent verification pass on the
> finding in `PANEL_CLINALITY_AUDIT_2026-08-16.md`: that pharmacogene alleles
> show frequency clines *within* the South Asian super-population, and that the
> direction of each cline is predictable from the allele's continental ancestry
> skew.
>
> **Method.** Pass 1: four parallel literature/data searches (novelty, cohorts,
> statistical methods, clinical stakes). Pass 2: adversarial re-search aimed at
> four specific threats identified by pass 1. Then one computation run locally
> against the pinned panel data.
>
> **Headline.** The audit's own most serious named limitation — that the NW→SE
> ordering was hand-assigned and a different defensible ordering "might give
> different z values" — is now **closed by measurement, in the finding's
> favour**. Rescored by measured ANI ancestry proportion, **zero of 13 alleles
> change direction and the rank correlation of z-scores is exactly 1.00.**
> Separately, the novelty claim must shrink: two of the four things the audit
> treats as new are prior art, and one contains an arithmetic error.
>
> Every number below is either from a cited paper or computed locally by
> `project_astra/scripts/verify_ani_rescore.py`. Where a claim could not be
> verified, it says so.

---

## 0. Findings up front

| # | Finding | Consequence |
|---|---|---|
| F1 | **The ordering limitation is closed.** ANI-rescored: 0/13 direction flips, Spearman ρ = 1.000 between the two scorings. | The strongest available attack on the finding fails. Promote from limitation to robustness result. |
| F2 | **Super-population masking is prior art.** Zhou & Lauschke already published "extensive variation within superpopulations with up to tenfold differences between geographically adjacent populations" (PMID 36855170). | The generalisable claim drafted in `POPULATION_DATA_STRATEGY` §7 is *not* novel as stated. Must be narrowed. |
| F3 | **What survives as novel** is the *predictive* claim: cline direction is forecastable a priori from log₂(EAS/EUR). No prior art found, and **GenomeIndia S13 confirms the gap** — it has both the North-South cline and the pharmacogenes, in the same supplement, and never joins them (§10). | This is the paper's contribution. Lead with it. |
| F4 | **The audit's Bonferroni sentence is wrong.** It reports one-sided p but the shipped code computes two-sided. On two-sided p, only CYP2D6 \*10 survives on the ordinal axis — not two alleles. | Correction required in `PANEL_CLINALITY_AUDIT_2026-08-16.md`. See §3.1. |
| F5 | **Independent clinical corroboration exists.** Nahar 2013: CYP2C9 \*2 at 0.05 in North Indians vs 0.006 in South Indians, n=291, p<0.001. | An out-of-sample, different-technology confirmation of the \*2 cline. Cite it. |
| F6 | **A serious complication.** Within-Pakistan ethnic variation in CYP2C9 \*2 (Baloch 0.160 vs Pathan 0.032, ~5×) is as large as the entire NW→SE cline (~2.9×). | PJL is an ethnic sample, not a geographic average. Must be disclosed. |
| F7 | **The bottleneck has one real route**, and it is data, not statistics: LASI-DAD (n=2,762, 18 states, no PGx paper published) via NIAGADS. | Named, obtainable, first-mover. §5. |
| F8 | **Shrinkage cannot rescue rare alleles.** Partial pooling improves point estimates but *reduces* apparent between-population differences. It cannot manufacture power. | Do not ship empirical Bayes as a fix for the 7/20 untestable alleles. §4.3. |

---

## 1. The verification that matters: rescoring the axis

### 1.1 What was tested

`PANEL_CLINALITY_AUDIT_2026-08-16.md` §8 names this limitation:

> *"The NW→SE scoring is ordinal and hand-assigned (0,1,2,3,4 for PJL, GIH, ITU,
> STU, BEB). It encodes a geographic prior. A different defensible ordering — by
> measured ANI/ASI ancestry proportion rather than by longitude — might give
> different z values. This should be checked against Moorjani 2013 /
> Narasimhan 2019 ancestry estimates."*

That check is now run. The ancestry estimates come from **Sengupta et al. 2016,
*Genome Biology and Evolution* 8(11):3460-3470, Table 2** (K=5, majority
subgroups), which resolves ANI proportion per 1000 Genomes SAS population:

| Population | ANI | ASI | AAA | **ATB** | A&N |
|---|---|---|---|---|---|
| PJL | 0.837 | 0.054 | 0.052 | 0.050 | 0.007 |
| GIH | 0.807 | 0.071 | 0.085 | 0.031 | 0.005 |
| ITU | 0.649 | 0.170 | 0.165 | 0.010 | 0.005 |
| STU | 0.610 | 0.193 | 0.178 | 0.012 | 0.007 |
| BEB | 0.557 | 0.123 | 0.172 | **0.140** | 0.008 |

Two facts fall out immediately, and both help:

1. **ANI rank order is identical to the hand-assigned geographic order.** The
   audit's "geographic prior" was not an arbitrary choice — it coincides exactly
   with an independently measured ancestry gradient.
2. **BEB carries ATB (East-Asian-related) ancestry at 0.140, against ≤0.050 for
   every other SAS population.** This is the mechanism §5 of the panel audit
   inferred but could not name: there is a real East Asian ancestry component at
   the southeast end, which is *why* an EAS-skewed allele rises toward Bengal.

### 1.2 The result

Rerunning Cochran-Armitage with scores set to −ANI proportion instead of
ordinal rank (`scripts/verify_ani_rescore.py`, reads the pinned
`sas_clinality_panel.json`, no network):

| Gene | Allele | alt obs | z (ordinal) | z (ANI) | z (ATB) | flips? |
|---|---|---|---|---|---|---|
| **CYP2D6** | **\*10** | 165 | **+3.91** | **+3.63** | +3.18 | no |
| **DPYD** | **HapB3** | 18 | **−2.68** | **−2.92** | −1.68 | no |
| CYP2C9 | \*2 | 36 | −2.50 | −2.64 | −0.56 | no |
| NAT2 | \*5 | 356 | −1.72 | −1.64 | +1.22 | no |
| CYP2D6 | \*4 | 109 | +1.64 | +1.44 | +0.65 | no |
| NAT2 | \*7 | 68 | +1.37 | +1.30 | +0.92 | no |
| NAT2 | \*6 | 365 | −1.20 | −1.27 | −2.40 | no |
| SLCO1B1 | \*5 | 41 | +0.70 | +1.26 | −0.50 | no |
| CYP2C19 | \*2 | 364 | +0.70 | +0.98 | −1.19 | no |
| CYP2C19 | \*3 | 11 | +0.66 | +0.55 | +1.54 | no |
| TPMT | \*3C | 16 | +0.55 | +0.42 | +1.07 | no |
| CYP2C9 | \*3 | 108 | −0.17 | −0.41 | −0.08 | no |
| CYP2B6 | \*6 | 387 | −0.01 | −0.21 | −0.38 | no |

**Direction flips: 0/13. Spearman ρ between the two z vectors: 1.0000.**

The two strongest clines *strengthen* slightly under ancestry scoring
(HapB3 −2.68 → −2.92; \*2 −2.50 → −2.64), and CYP2D6 \*10 weakens slightly
(+3.91 → +3.63) while remaining the strongest by a wide margin.

**Interpretation.** Cochran-Armitage with scores set to a covariate is
algebraically the score test for H₀: β=0 in a binomial regression on that
covariate. So this is not a cosmetic re-run: it is the direct test of whether
the geographic prior was doing the inferential work. It was not. The result is
the same because longitude and ANI proportion are the same axis in this region.

**The honest caveat:** ρ = 1.000 is partly *because* the two scorings are nearly
collinear (ANI rank = geographic rank). This test proves the result is not an
artifact of the specific ordinal spacing, and that the axis has an independent
ancestry interpretation. It does not prove the axis is *causal*, and it cannot —
five populations cannot separate ancestry from geography when the two coincide.

### 1.3 The ATB column is a third, weaker axis

Scoring by ATB proportion alone (which is essentially a BEB-vs-rest contrast)
retains the CYP2D6 \*10 signal (z = +3.18) but destroys CYP2C9 \*2 (−2.50 →
−0.56). This is informative: \*10's gradient is substantially carried by BEB's
East Asian component, whereas \*2's gradient is a genuine ANI gradient that ATB
does not explain. **Two different clines with two different mechanisms**, which
is a better result than one uniform pattern — it makes the ancestry account
falsifiable per allele rather than global.

---

## 2. Novelty: narrower than drafted

### 2.1 What is prior art

**Super-population heterogeneity is published.** Zhou & Lauschke, PMID 36855170
— the very paper the CYP2C9 audit cites for the \*2 pattern — states in its own
abstract:

> *"Our data show extensive variation within superpopulations with up to tenfold
> differences between geographically adjacent populations in Malaysia, Thailand
> and Vietnam."*

So `POPULATION_DATA_STRATEGY_2026-08-16.md` §7's framing — "super-populations
hide clines (true but unfalsifiable as stated)" — is worse than unfalsifiable.
It is **already published**, by the paper we cite. This must be corrected.

**Also prior art:**
- Sub-population PGx frequency reporting for GIH and ITU specifically: PeerJ
  2021 (PMC8590392), "Genetic diversity of Very Important Pharmacogenes in two
  South-Asian populations."
- Country-level PGx frequency aggregation: PharmFreq (~6M individuals, 137
  countries), and PharmCAT across UK Biobank biogeographic groups (PMID
  37757824).
- Community-level PGx structure in India: Kerdoncuff 2025, *Cell*
  188(13):3389-3404 — BCHE L307P 0.28% India-wide vs 5.3% in Telangana Vysya.
- Race/ethnicity mislabelling in PGx: PMID 31308725.
- North-vs-South Indian CYP2C9 \*2 difference: **Nahar 2013** (see §3.2).

### 2.2 A published near-negative result, assessed

**Nizamuddin et al. 2021 (PMID 33536773)** is the most threatening paper found.
It analysed 1,278 individuals from 36 Indian populations and concluded:

> *"The allelic/genotypic frequency does not correlate with geographical location
> or linguistic affiliation…"* and *"we did not find any correlation with
> geographical distance."*

**Verdict: does not contradict, for three checkable reasons.**

1. **It is about CYP2C9 \*3, not \*2.** Their Sanger primers targeted \*3. \*2
   appears only in 10 of 210 NGS samples, described as a rare putative
   functional variant, and was **not** subjected to geographic analysis.
2. **No formal directional test was run.** The "no correlation" claim rests on
   visual inspection of a Kriging surface. No trend test, no latitude
   regression, no p-value is reported for geography.
3. **Our own data agrees with them about \*3.** CYP2C9 \*3 is the *flattest*
   allele on our panel (z = −0.17, p = 0.86). We independently reproduce their
   negative result for the allele they actually tested.

**But it carries a real warning.** Their 36 endogamous caste/tribal samples show
CYP2C9 \*3 ranging from 0% (Bhil, Gujarat) to 16% (Baiswar, UP) — both
Indo-European speakers. Endogamy-driven heterogeneity within a region is large
enough to obliterate a smooth cline. Our 5 pooled 1000G populations average over
castes, which is why we see a gradient they could not. That is a defensible
methodological difference, **not** a refutation of them — and it means our
result is about pooled linguistic-geographic strata, not about castes.

### 2.3 The narrowest defensible novel claim

Prior art covers: *that* within-super-population variation exists; *that* it
matters clinically; *that* CYP2C9 \*2 declines from Europe across South Asia.

No prior art was found for the **predictive** form:

> **An allele's within-super-population frequency gradient is predictable in
> advance from the log-ratio of its frequencies in the continental ancestry
> sources of that gradient.** Tested by Cochran-Armitage on ancestry-scored
> subpopulations: r = 0.554 between log₂(EAS/EUR) and trend z, 10/13 directions
> correct (binomial p = 0.046), and all four alleles with a significant trend
> fall in the agreeing set.

This is a *rule that tells you which alleles need subpopulation resolution
before you spend money resolving them.* That is the useful and, as far as two
research passes can establish, unpublished part. Two supporting novelties:
the Cochran-Armitage repurposing for cline detection, and the negative result
that fold-spread fails against a sampling null.

**Scoop risk: RESOLVED — read directly, 2026-08-16.** GenomeIndia's flagship
supplement (`GI_Flagship_Supplementary_Final_22Jan`, 215 pp, 38 MB) was
downloaded and text-extracted. **Section S13, "Landscape of pharmacogenomic
variations in GI populations" (pp. 178–188), does not scoop the predictive
claim, and confirms the descriptive premise.** Detail in §11.

---

## 3. Two corrections to our own documents

### 3.1 The Bonferroni claim is wrong (one-sided vs two-sided)

`PANEL_CLINALITY_AUDIT_2026-08-16.md` §4 tabulates **one-sided p** and claims:

> *"CYP2D6 \*10 (z = +3.91, p = 0.00005) and DPYD HapB3 (z = −2.68, p = 0.0037)
> both beat it and both survive Bonferroni correction across 13 tests, which
> \*2 (p = 0.0062 vs α = 0.0038) does not."*

But the shipped function `frequency_divergence.trend_p_value()` computes
**two-sided** p, and documents why:

> *"Two-sided rather than one-sided: the panel audit found clines running in
> both directions … so pre-committing to a direction is not honest for a
> general-purpose function."*

The code is right and the document is wrong. On two-sided p (α = 0.00385):

| Allele | z | one-sided p | two-sided p | survives Bonferroni? |
|---|---|---|---|---|
| CYP2D6 \*10 | +3.91 | 0.00005 | **0.00009** | yes |
| DPYD HapB3 | −2.68 | 0.0037 | **0.00743** | **no** |
| CYP2C9 \*2 | −2.50 | 0.0062 | **0.01248** | no |

**Only one allele survives Bonferroni on the ordinal axis, not two.** The audit
cannot both use two-sided reasoning ("clines run in both directions, so don't
pre-commit to a direction") and claim one-sided p-values. It must pick, and the
code has already picked correctly.

*Interesting consequence:* on the **ANI axis**, HapB3 strengthens to z = −2.92,
two-sided p = 0.00349, which *does* clear α = 0.00385. So "two alleles survive
Bonferroni" is recoverable — but only on the ancestry-scored axis, and it has to
be stated as such rather than asserted on the ordinal axis.

### 3.2 The clinical magnitude was overstated by an outside estimate

A literature pass estimated CYP2D6 \*10 at 0.30 in Punjabi and 0.55 in Bengali,
concluding homozygotes triple from 9% to 30%. **Our own pinned data does not
support those frequencies.** Measured rs1065852 in gnomAD v3.1:

| Population | AC/AN | f(\*10) | \*10/\*10 | any \*10 |
|---|---|---|---|---|
| PJL | 20/204 | 0.0980 | 0.96% | 18.7% |
| GIH | 29/202 | 0.1436 | 2.06% | 26.7% |
| ITU | 34/204 | 0.1667 | 2.78% | 30.6% |
| STU | 31/204 | 0.1520 | 2.31% | 28.1% |
| BEB | 51/200 | 0.2550 | 6.50% | 44.5% |
| *pooled* | 165/1014 | *0.1627* | *2.65%* | *30.5%* |

The true spread is 0.098 → 0.255 (2.6×), not 0.30 → 0.55. The clinical
consequence is still substantial but must be quoted from these numbers:

- Homozygote prevalence: **6.50% BEB vs 0.96% PJL — a 6.8× ratio.**
- Using pooled SAS for a Bengali cohort predicts 2.65% homozygotes against an
  actual 6.50%: **3.85 percentage points, or ~39 missed per 1,000 patients.**
- Number needed to screen for one \*10/\*10: **15.4 in BEB vs 37.8** under the
  pooled-SAS assumption — a 2.5× efficiency error.
- In Punjabi patients the same pooled figure **over-predicts** by ~17 per 1,000.

Note the errors run in *opposite directions* at the two ends, which is exactly
what a single super-population number cannot represent. Also note rs1065852
(c.100C>T) tags \*10 but is present on other haplotypes; the audit's own
disambiguation discipline applies, and calling it "\*10 frequency" is shorthand.

---

## 4. The statistical bottleneck: what can and cannot be fixed

### 4.1 The floor, stated precisely

At ~200 alleles per subpopulation, the detectability floor is arithmetic:

| True freq | Expected count | 95% CI (Clopper-Pearson) |
|---|---|---|
| 0.005 | 1.0 | 0.00% – 2.75% |
| 0.010 | 2.0 | 0.12% – 3.57% |
| 0.050 | 10.0 | 2.42% – 9.00% |

Minimum detectable fold-change at 80% power, α = 0.05, per allele: **10.2× at
p=0.005**, 4.1× at p=0.02, 2.0× at p=0.10. To detect a 3-fold difference
(0.005 vs 0.015) at Bonferroni α = 0.0025 with 80% power requires **~1,300–1,500
individuals per subpopulation** (one-sided vs two-sided), against 100 available
— roughly **13–15× underpowered**.

If an allele is unobserved (0/200), the 95% upper bound is 3/200 = **1.5%** by
the rule of three, tightening to ~0.9% under a Jeffreys prior. This is the
platform's existing "not detected in N alleles, upper bound X" discipline and it
remains the correct output.

### 4.2 Route inventory

| Route | Verdict | What it buys |
|---|---|---|
| Empirical Bayes shrinkage (Coram & Tang 2007) | **Do not ship for this** | 30–50% CI narrowing on point estimates; see §4.3 |
| Ancestry-proportion regression | **Already effectively done** | Algebraically the score test we ran in §1.2 |
| Haplotype tagging | **Dead end for HapB3** | rs56038477 and causal rs75017182 are *not* in complete LD (PMID 38129972) |
| Imputation into array cohorts | **Viable, non-CYP2D6 only** | 10–20× effective N; CYP2D6 SVs cannot be imputed |
| Spatial kriging | **Dead end** | Cannot fit a semivariogram from 5 points |
| More data (LASI-DAD / GenomeIndia) | **The real route** | §5 |

### 4.3 Why shrinkage is the wrong tool here — and this is the important one

Empirical Bayes partial pooling is the obvious-looking fix and it should be
rejected, for two reasons:

1. **It was never validated on rare alleles.** Coram & Tang learn the affinity
   parameter from genome-wide *common* variants and state in their own
   discussion that rare alleles may need "a mixture of beta's" rather than the
   fitted family. Our untestable alleles are rare by definition.
2. **It moves the estimate in the wrong direction for our purpose.** Shrinkage
   pulls each subpopulation toward the pooled mean. It improves squared-error on
   point estimates while *reducing* apparent between-population differences. We
   are trying to *detect* between-population differences. Applying shrinkage and
   then testing for clines would bias toward the null while creating an
   appearance of increased precision.

**The honest position: for alleles below ~2% in a 200-allele sample, the pooled
South Asian estimate is the only defensible number, and per-subpopulation values
are statements of faith.** That is what the existing informativeness gate (10
alt observations) already encodes. Keep it; do not paper over it with a model.

---

## 5. The route through the bottleneck

The bottleneck is **data, not statistics**. No method extracts a 3-fold rare
allele difference from 200 alleles. Ranked by obtainability × value:

| Rank | Source | N | Resolution | Status |
|---|---|---|---|---|
| **1** | **LASI-DAD** | **2,762 WGS** | **18 states, 26 languages, ST/SC/OBC** | **Managed access, NIAGADS ng00067. No PGx paper published.** |
| 2 | GenomeIndia | 9,768 WGS | 83 populations | Released; IBDC FeED. **Read S13 first** (§2.3) |
| 3 | Genes & Health | 44,028 WES | Pakistani vs Bangladeshi split | Managed access; has CYP2C19 paper (PMID 37808344) |
| 4 | IndiGenomes | 1,029 WGS | Pooled India | **Open today**, browser + API |
| 5 | Pakistan 6-ethnicity | 467 genotyped | Punjabi/Pathan/Sindhi/Baloch/Seraiki/Urdu | **Published, open** (PMID 33195499) |
| 6 | Sri Lanka WES (Colombo) | 670 WES | Sinhalese/Tamil/Moor | Published frequencies only |

**LASI-DAD is the named route.** It is the only dataset combining (a) WGS,
(b) genuine state-and-community stratification, (c) N large enough to move the
detectability floor, and (d) **no published PGx frequency analysis**, which
makes the pharmacogene panel a first-mover analysis rather than a replication.
It is also already the source of the Kerdoncuff 2025 community-structure finding
we cite, so its resolution is demonstrated rather than assumed.

Application: https://dss.niagads.org/documentation/data-application-and-submission/application-instructions/ (accession ng00067). Requires institutional affiliation.

Additionally, LASI-DAD has been released as an **imputation panel** (2,680 Indian
WGS) reported to improve accuracy over TOPMed by a mean 38% across MAF bins.
That is the mechanism for route 4 in §4.2: impute pharmacogene variants into
larger array-genotyped South Asian cohorts and multiply effective N — valid for
DPYD/CYP2C9/CYP2C19 SNVs, invalid for CYP2D6 structural variants.

### 5.1 What is immediately actionable without any application

Three things can be done today, at zero access cost:

1. **The Pakistan 6-ethnicity data (PMID 33195499) is published and open.** It
   provides a second, independent, non-1000G test of the northwest end.
2. **IndiGenomes is queryable now** and is already a second source in the
   divergence pipeline.
3. **Nahar 2013 is an out-of-sample corroboration already in the literature**
   (§3.2 below) and costs nothing to cite.

---

## 6. Independent corroboration, and one serious complication

### 6.1 Corroboration: Nahar 2013

**Nahar et al., *Pharmacological Reports* 65:187-194 (2013)** genotyped 209
North Indians and 82 South Indians:

- CYP2C9 \*2: **North 0.05 vs South 0.006, p < 0.001** (~8-fold)
- CYP2C9 \*3: North 0.11 vs South 0.09 (not significant)
- VKORC1 −1639A: North 0.19 vs South 0.14 (not significant)

This is an independent cohort, a different genotyping technology, and a
different sampling frame, and it reproduces **both** of our directional results
for this gene: \*2 declines north→south significantly, \*3 does not differ. The
paper further predicts North Indians are at higher risk of over-anticoagulation
on standard warfarin dosing (RR 1.93, p = 0.012).

This is the single most useful citation found in either pass. It converts the
CYP2C9 \*2 cline from an in-sample statistic into a replicated finding — which
matters especially because \*2 fails Bonferroni in our own data.

### 6.2 Complication: PJL is an ethnic sample, not a geographic average

**Ahmed et al. 2020, *Sci Rep* (PMID 33195499)**, n=467 across six Pakistani
ethnicities, CYP2C9 \*2 allele frequency:

| Ethnicity | \*2 | \*3 |
|---|---|---|
| Pathan | 0.032 | 0.032 |
| Punjabi | 0.034 | 0.015 |
| Seraiki | ~0.046 | ~0.073 |
| Urdu-speaking | 0.078 | 0.023 |
| Sindhi | 0.090 | 0.080 |
| **Baloch** | **0.160** | **0.220** |
| *Pakistan overall* | *0.059* | *0.064* |

**Within-Pakistan ethnic variation (0.032 → 0.160, ~5×) is as large as or larger
than the entire NW→SE cline we measured (0.0588 → 0.0200, 2.9×).**

This must be disclosed, and it cuts two ways:

- **Against a naive reading:** "the northwest has high \*2" is too coarse. PJL
  (Punjabi from Lahore) is *one ethnic sample* from the northwest, and its 1000G
  value (0.0588) does not even match this study's Punjabi value (0.034). Baloch
  at 0.160 exceeds every 1000G SAS subpopulation.
- **For the underlying thesis:** it is *more* evidence that a single pooled
  label conceals clinically material variation. It relocates the problem one
  level down — from "SAS hides subpopulations" to "subpopulations hide
  ethnicities" — which is the same finding recursing, and is consistent with
  both Nizamuddin's caste heterogeneity (§2.2) and Kerdoncuff's Vysya result.

The correct framing is therefore **not** that we have measured South Asia's
pharmacogene geography. It is that we have shown a single super-population
number is wrong in a *predictable direction*, and that each additional level of
resolution keeps finding structure. The clinality flag should be read as "this
allele needs better data," never as "this is the Bengali frequency."

---

## 7. Clinical stakes, verified

**CYP2D6 \*10 is the allele to lead with**, on three grounds: strongest cline,
survives Bonferroni on both axes, and most actionable drug pairs.

- CPIC's tamoxifen guideline (PMID 29385237) gives a **Moderate**-strength
  recommendation to consider an aromatase inhibitor for CYP2D6 IMs, and
  explicitly singles out activity score 1.0 **with a \*10 allele present** as
  warranting the same action as AS=0.5. Breast cancer is the most common cancer
  in Indian women, and Indian presentation skews premenopausal, where tamoxifen
  remains first-line.
- \*10 also affects codeine/tramadol (PMID 33387367), TCAs, SSRIs (PMID
  37032427), atomoxetine, and beta-blockers (PMID 38951961).
- NCCN/ASCO and ESMO do **not** endorse CYP2D6 testing for tamoxifen. The
  actionability is genuinely contested, which is the platform's native
  situation — a named uncertainty, not an assertion.

**DPYD HapB3** sits in a sharpened regulatory context. Verified: the **FDA added
a boxed warning to capecitabine and fluorouracil on 2026-02-05**, recommending
DPYD testing before treatment. That follows EMA (2020-04-30) and UK MHRA
(2020-10). **India has no equivalent mandate** — no CDSCO or ICMR requirement —
so this is a live regional disparity, not a hypothetical one.

HapB3's *magnitude* remains contested: Knikman et al. (PMID 37639651) found
HapB3 carriers given the guideline 25% dose reduction had both reduced
effectiveness and still-elevated toxicity. CPIC has acknowledged this without
changing the recommendation. Additionally PMID 38129972 shows rs56038477 and the
causal rs75017182 are **not** in complete LD — which bears directly on our own
panel, since our HapB3 row is keyed on rs56038477.

**CYP2C9 \*2** is the best-corroborated cline (§6.1) with a published warfarin
dosing consequence, but is the weakest statistically of the three.

---

## 8. Honest limitations of this research pass

- **The novelty verdict rests on absence of evidence.** Two passes of literature
  search found no prior art for the predictive claim. That is not proof of
  novelty. A systematic search with a librarian, and reading GenomeIndia S13,
  are both still required.
- **GenomeIndia S13 has now been read in full** (§10), closing what the first
  draft called the largest unresolved risk. What remains unread: the underlying
  Tables S13.1–S13.9 data files, which are described in the narrative but are
  not separately hosted at the medRxiv `DC1/embed/` path (`media-2`…`media-5`
  all 404). Their per-population frequency matrices would allow a direct
  out-of-sample test of the predictive rule and are the reason to file the
  IBDC/FeED application.
- **ρ = 1.000 is partly collinearity, not independent confirmation.** ANI rank
  and geographic rank coincide, so the rescore proves robustness to spacing and
  gives the axis an ancestry interpretation. It cannot separate ancestry from
  geography as causes.
- **Sengupta 2016 splits PJL, GIH and ITU into subgroups** (PJL_1 ANI 0.657 vs
  PJL_2 0.837). I used majority-subgroup values. Using minority values would
  change the ANI scores and was not tested. Also, PJL_1 vs PJL_2 F_ST (0.009)
  exceeds GIH-vs-BEB F_ST (0.0045) — within-population substructure exceeds some
  between-population distances, which is the §6.2 complication in genomic form.
- **13 tests, no pre-registration.** The continental-skew correlation was run
  after seeing trend results. The ANI rescore was run after seeing both. Each
  additional analysis on the same 5×200 alleles compounds this.
- **1000 Genomes subpopulations are samples of convenience**, several collected
  in diaspora (GIH in Houston, ITU and STU in the UK). They are not communities
  and cannot resolve the structure Kerdoncuff 2025 showed matters.
- **rs1065852 is a tag, not the star allele.** \*10 frequencies here are
  rs1065852 frequencies; the variant occurs on other haplotypes.
- **Clinical impact figures in §3.2 are Hardy-Weinberg projections** from allele
  frequencies, not observed diplotype counts, and they ignore all other CYP2D6
  alleles and structural variants. They are order-of-magnitude, not clinical
  estimates.
- Sub-agent research was used for breadth. Where its numbers conflicted with our
  pinned data (the 0.30/0.55 estimate), the pinned data won and the discrepancy
  is documented in §3.2 rather than silently dropped.

---

## 9. What should happen next

1. **Fix the Bonferroni sentence** in `PANEL_CLINALITY_AUDIT_2026-08-16.md` §4
   and its abstract. One-sided p is inconsistent with the shipped two-sided
   function. On the ordinal axis only CYP2D6 \*10 survives; on the ANI axis
   HapB3 also does. State which axis each claim uses.
2. **Correct `POPULATION_DATA_STRATEGY_2026-08-16.md` §7 item 5.** "Super-
   populations hide clines" is prior art (PMID 36855170, quoted in §2.1). Replace
   with the predictive claim from §2.3.
3. **~~Read GenomeIndia S13~~ — DONE (§10).** Descriptive claim is scooped at
   82-population resolution; predictive rule is not. **New highest-value action:
   file the IBDC/FeED application to get Tables S13.1–S13.9, then test the
   predictive rule out-of-sample across their 82 populations.** This now
   outranks LASI-DAD, because it validates the actual contribution rather than
   extending the descriptive one.
4. **Add the ANI rescore as a shipped robustness output**, not a one-off script.
   It closes a named limitation and it is 30 lines of arithmetic on data already
   in hand.
5. **Cite Nahar 2013** wherever the CYP2C9 \*2 cline is claimed. It is
   independent replication and \*2 needs it, since it fails Bonferroni.
6. **Disclose the Pakistan within-ethnicity complication** (§6.2) in the same
   breath as any NW→SE claim. Do not let "PJL" stand for "the northwest."
7. **File the LASI-DAD application** (NIAGADS ng00067). It is the route through
   the bottleneck and it is unfiled.
8. **Do not ship empirical Bayes shrinkage** as a fix for the 7/20 untestable
   alleles. Keep the informativeness gate and the named refusal. §4.3.
9. **Recompute the cohortfit `*2A` 1.41× floor**, still outstanding from the
   panel audit §6.3 and unaffected by this pass.

## 10. GenomeIndia Section S13, read in full


The single largest unresolved risk in §8 of the first draft is now closed. The
supplement was downloaded (`curl`, 38 MB, 215 pp) and extracted with
`pdftotext -layout`; `web_fetch` cannot parse PDFs, which is why two earlier
attempts failed. **Section S13 spans pp. 178–188**, authored by Ankit Mukherjee
(CSIR-IGIB), Chandrika Bhattacharyya (BRIC-NIBMG) and Mohammed Faruq
(CSIR-IGIB). Only one supplement file exists; `media-2` through `media-5` return
404, so the Tables S13.1–S13.9 are described in the narrative but their data
files are not separately hosted at that path.

### 11.1 What S13 actually did

Substantial and directly adjacent work, at far higher population resolution
than we have:

- **9,768 WGS across 82 Indian populations**, grouped into four ethnolinguistic
  categories (Austro-Asiatic, Dravidian, Indo-European, Tibeto-Burman) and
  tribal/non-tribal strata.
- Of 4,245 PharmGKB/PharmVar v6.2 variants, **2,831 found in GI**; 2,339 with
  drug annotations. 287 PGx variants across 31 of 34 VIP genes.
- **317 star alleles across 55 pharmacogenes** via Stargazer, **86 CYP2D6
  haplotypes via Cyrius**, HLA four-digit typing via xHLA.
- Prioritised down to 49 key SNPs and 32 star alleles, then a final **20
  actionable variants**; 4,018 drug–response–population–variant interactions.
- Per-individual burden: **median 4 actionable variants, range 0–9**, highest in
  Indo-European and Dravidian non-tribal groups.
- **Explicit comparison against 1000 Genomes SAS as the reference**, with
  Z-score normalisation to flag populations above the SAS baseline, and Fisher's
  exact tests for inter-population frequency differences.

### 11.2 Why it does not scoop the predictive claim

Four checkable reasons:

1. **No trend test, anywhere in the 215 pages.** Grepping the full text for
   `cochran`, `armitage`, `trend test`, `monotonic`, `clinal` returns **zero
   hits in S13**. Their inter-population statistic is Fisher's exact test —
   an unordered homogeneity test. They test *whether* populations differ; they
   never test whether frequencies vary *along an ordered axis*.
2. **The North–South cline is discussed at length, but never for
   pharmacogenes.** "Cline" appears ~14 times in the supplement, all in
   Section S4 (population structure/PCA, citing Reich 2009 and Basu 2016). S13
   is a separate section by different authors and **never connects the cline to
   PGx frequencies.** The two halves of the predictive claim are both present in
   the same document and are never joined.
3. **No ancestry-skew predictor.** S13 reports SAS/EAS/EUR frequencies
   side-by-side for rare CYP2D6 haplotypes (Table S13.9) — the exact inputs our
   log₂(EAS/EUR) predictor uses — but uses them only descriptively, as
   comparison columns. Nothing predicts within-India direction from them.
4. **Geography enters once, as an ad-hoc hypothesis, not a method.** For VKORC1
   rs9923231 they note higher frequencies at high altitude (0.4143 in
   TB_BPV_1_02 vs 0.0556 in DR_ECP_2_07 against SAS 0.143) and speculate about
   hypoxia adaptation. That is a single-variant environmental observation, not a
   generalisable rule, and altitude is not an ancestry axis.

**Verdict: the descriptive half is comprehensively covered at 82-population
resolution. The predictive rule of §2.3 is not.** Their framing is a
prioritisation catalogue for clinical implementation — "which Indian populations
need which test." Ours is a forecasting rule — "which alleles will show
structure, predictable before you measure it." S13 is now the strongest available
argument that the descriptive claim is *not* our contribution, and the cleanest
demonstration that the predictive one is unoccupied.

### 11.3 Three findings from S13 that bear on our own numbers

**(a) Our DPYD HapB3 pinned value is externally confirmed.** S13 reports
`rs56038477` at **GI 0.0159** against **SAS 0.0166**. Our pinned SAS value is
0.017282 and our 5-subpopulation pooled genome value is 0.016136. Three
independent estimates agreeing to the third decimal is meaningful
corroboration of the row our HapB3 cline rests on.

**(b) A discrepancy worth chasing on DPYD \*2A.** S13 gives `rs3918290` as
**GI 0.0025 vs SAS 0.0075**. Recall the cohortfit fixture correction (panel
audit §6.3) moved pinned SAS \*2A from 0.0005 to **0.0040** after finding an 8×
transcription error, and noted a residual unresolved gnomAD-vs-1000G spread of
0.0040 vs 0.0075–0.0080. **S13's SAS 0.0075 sits at the top of exactly that
band, and its India-only 0.0025 sits below our corrected 0.0040.** So the
India-vs-SAS direction for \*2A is *downward*, which is the opposite of what an
exome-undercount story would predict and consistent with the transcription-error
explanation. This is new external evidence on an open item.

**(c) S13 finds DPYD risk concentrated in specific populations, not clinally.**
`rs56038477` peaks at **0.0867 in population 61 (DR_NGH_1_02, Dravidian tribal)**
and 0.0645 in population 3 (IE_WPL_2_02, Indo-European non-tribal) — against
GI-wide 0.0159. A Dravidian (southern) tribal group carries the *highest* HapB3
frequency in India, whereas our five-subpopulation axis shows HapB3 *decreasing*
toward the southeast (z = −2.68 ordinal, −2.92 ANI).

**This is the §6.2 complication again, and it is now the sharpest version of
it.** A 5.5× enrichment in one southern tribal population does not refute a
NW→SE trend across pooled linguistic strata — endogamous founder effects operate
orthogonally to ancestry gradients, exactly as Nizamuddin's caste data (§2.2) and
Kerdoncuff's Vysya result show. But it does mean the HapB3 cline **must not be
read as "southern Indians carry less HapB3."** It is a statement about pooled
strata, and S13 provides a concrete counterexample population. Any claim about
HapB3 geography has to cite this.

### 11.4 Consequences

1. **The descriptive claim is dead as a contribution.** Do not write "super-
   populations hide clines" or "India needs subpopulation PGx resolution" as
   findings. S13 did it at 82 populations with 9,768 genomes. Cite it as the
   state of the art.
2. **Reframe explicitly against S13.** The contribution is the *predictive*
   rule and the *methodological* results (fold-spread fails its null;
   Cochran-Armitage works; ANI rescoring is invariant). S13 makes the gap
   visible: it has both the cline (S4) and the pharmacogenes (S13) and never
   joins them.
3. **The strongest possible next experiment is now obvious.** Apply the
   predictive rule to GenomeIndia's 82 populations. Our rule was fitted on 5
   populations with ~200 alleles each; theirs is 82 populations with ~9,768
   genomes and *already published ancestry structure*. If log₂(EAS/EUR)
   predicts trend direction across their populations too, the rule is validated
   out-of-sample at 16× the population count. That is a genuine test, and it
   raises the priority of the IBDC/FeED application above LASI-DAD.
4. **Add S13's DPYD numbers to the divergence pipeline** as a third source
   alongside gnomAD and IndiGenomes — it is published, quotable, and
   independently corroborates the HapB3 row.
5. **Disclose the population-61 counterexample** wherever the HapB3 cline
   appears.

---

## 11. Reproducing

```bash
cd project_astra
python scripts/verify_ani_rescore.py    # pure arithmetic, no network
```

Reads the pinned `scripts/sas_clinality_panel.json`. Ruff clean.

The GenomeIndia supplement (§10) is retrieved and read with:

```bash
curl -sL -A "Mozilla/5.0" -o gi_supp.pdf \
  "https://www.medrxiv.org/content/medrxiv/early/2026/03/24/2026.03.20.26348801/DC1/embed/media-1.pdf?download=true"
pdftotext -layout gi_supp.pdf gi_supp.txt   # 215 pp; S13 at pp. 178-188
```
