# Panel-Wide Clinality Audit — the Fold-Spread Metric Does Not Work, the
# Trend Test Does, and CYP2C9 \*2 Is Not the Strongest Case (2026-08-16)

> **Closes:** named next step #1 of
> `CYP2C9_STAR2_SAS_FREQUENCY_AUDIT_2026-08-16.md` §7 and decision item 2 of
> `POPULATION_DATA_STRATEGY_2026-08-16.md` §7 — *"Per-allele clinality is a
> computable property, not a footnote … Proposed as `clinality_index` on the
> frequency record."*
>
> **It is now computed for the whole panel, and the result corrects the
> proposal that requested it.**
>
> Three findings, in descending order of consequence:
>
> 1. **`clinality_index` as specified — a max/min fold-spread against a 1.5×
>    threshold — flags 69% of the testable panel and does not survive a
>    sampling-noise null.** CYP2C9 \*2's own 2.94× spread has an empirical
>    p of 0.33 against a null in which all five subpopulations share one
>    frequency. The metric measures rarity, not geography.
> 2. **The audit's reasoning was right even though its metric was wrong.** It
>    rested its case on the monotonic NW→SE *ordering*, not the spread. Tested
>    properly as a trend, CYP2C9 \*2 gives z = −2.50, p = 0.0062. The ordering
>    was the evidence; the fold-ratio was never doing the work.
> 3. **CYP2C9 \*2 is not the platform's strongest cline.** CYP2D6 \*10
>    (z = +3.91, p = 0.00005) and DPYD HapB3 (z = −2.68, p = 0.0037) both beat
>    it and both survive Bonferroni correction across 13 tests, which \*2
>    (p = 0.0062 vs α = 0.0038) does not.
>
> Every number below is from a live gnomAD query executed 2026-08-16, or
> computed from those queries by `scripts/query_sas_clinality_panel.py`. No
> number is recalled or interpolated.

---

## 1. What was measured

The pinned artifact the platform actually serves from
(`anukriti-swarm/datasets/pharmfreq/gnomad_v2_1_1_frequencies.jsonl`) carries
24 unique gene/allele/rsID triples, 20 of which have a South Asian frequency.
Each of the 20 rsIDs was queried against gnomAD v3.1 for all five 1000 Genomes
South Asian subpopulations **inside a single genome callset**, so there is no
exome/genome or release-version confound — the confound that misled the
2026-07-21 IndiGenomes pilot.

All 20 resolved. Two required disambiguation (§6.1).

## 2. 35% of the panel cannot be tested at all

Each 1000 Genomes South Asian subpopulation contributes ~200 alleles. An
allele observed a handful of times across all five produces a fold-ratio driven
entirely by whether one chromosome happened to be sampled: 1/204 against 0/200
is an infinite ratio and means nothing.

Applying a floor of 10 total alt observations across the five cells:

| Verdict | Count | Alleles |
|---|---|---|
| **Informative** | 13/20 | CYP2B6 \*6 · CYP2C19 \*2 · CYP2C19 \*3 · CYP2C9 \*2 · CYP2C9 \*3 · CYP2D6 \*4 · CYP2D6 \*10 · DPYD HapB3 · NAT2 \*5 · NAT2 \*6 · NAT2 \*7 · SLCO1B1 \*5 · TPMT \*3C |
| **Uninformative** | 7/20 | CYP2D6 \*17 (0 obs) · TPMT \*2 (0) · G6PD A− (0) · DPYD c.2846A>T (1) · G6PD Mediterranean (3) · TPMT \*3B (4) · DPYD \*2A (7) |

**This is itself a finding.** Two of the four CPIC DPYD panel variants — \*2A
and c.2846A>T — sit in the uninformative set. The platform's flagship
gene-drug pair is precisely where subpopulation resolution is unavailable at
1000 Genomes sample sizes, so a `clinality_index` on a DPYD frequency record
would be a named refusal, not a number. That is the honest output, but it
means clinality cannot inform the DPYD work that motivated it.

## 3. The proposed metric fails its own null test

For each informative allele, a Monte Carlo null (20,000 trials) drew five
binomial samples at the pooled SAS frequency using the real per-cell ANs, then
asked how often chance alone produces a fold-spread at least as wide as
observed.

| Gene | Allele | Observed spread | Null median | Null p95 | Empirical p | Verdict |
|---|---|---|---|---|---|---|
| DPYD | HapB3 | ∞ | 3.47× | 7.14× | 0.127 | marginal |
| TPMT | \*3C | 5.10× | 3.92× | 7.07× | 0.374 | noise |
| CYP2C19 | \*3 | 4.04× | 3.96× | 6.06× | 0.619 | noise |
| SLCO1B1 | \*5 | 3.47× | 2.23× | 4.90× | 0.146 | marginal |
| **CYP2C9** | **\*2** | **2.94×** | **2.38×** | **5.50×** | **0.327** | **noise** |
| CYP2D6 | \*10 | 2.60× | 1.44× | 1.89× | **0.001** | **SIGNAL** |
| CYP2D6 | \*4 | 1.89× | 1.59× | 2.29× | 0.194 | noise |
| NAT2 | \*7 | 1.56× | 1.84× | 3.03× | 0.761 | noise |
| NAT2 | \*5 | 1.53× | 1.24× | 1.45× | **0.018** | **SIGNAL** |
| NAT2 | \*6 | 1.48× | 1.24× | 1.44× | **0.029** | **SIGNAL** |
| CYP2C9 | \*3 | 1.44× | 1.59× | 2.30× | 0.727 | noise |
| CYP2C19 | \*2 | 1.28× | 1.24× | 1.44× | 0.359 | noise |
| CYP2B6 | \*6 | 1.17× | 1.22× | 1.42× | 0.737 | noise |

An exact 5×2 chi-square homogeneity test agrees independently: CYP2C9 \*2
gives χ² = 7.24, df = 4, **p = 0.124**.

Three consequences:

- **A fixed 1.5× threshold is not a threshold.** It flags 9/13 = 69% of the
  informative panel. A rule that fires on two-thirds of its inputs is not
  discriminating between them.
- **The threshold is frequency-dependent, not allele-dependent.** The null
  median for a rare allele is already 3–4×, and for a common allele ~1.2×. A
  single cut-off applied across both compares each allele against the wrong
  reference. Note the ranking inverts almost perfectly with frequency: the
  four alleles with pinned SAS ≥ 0.32 occupy the four lowest spreads.
- **NAT2 \*6 illustrates the trap.** At 1.48× it falls *below* the 1.5×
  threshold and would be reported FLAT, yet its empirical p is 0.029 — it is
  one of only three alleles whose spread beats its own null. The threshold
  gets it exactly backwards.

## 4. The trend test is the metric that works

The 2026-08-16 audit did not actually rest on the fold-ratio. It said:

> *"The **ordering** is what this audit relies on, and the monotonic NW→SE
> trend across five independent samples plus agreement with the independently
> published cline (PMID 36855170) is stronger evidence than any single cell.
> **A formal test of trend was not run.**"*

That test has now been run. Cochran-Armitage, subpopulations scored 0–4 along
the NW→SE axis (PJL, GIH, ITU, STU, BEB):

| Gene | Allele | z | one-sided p | Direction | Bonferroni (α=0.0038) |
|---|---|---|---|---|---|
| **CYP2D6** | **\*10** | **+3.91** | **0.00005** | increasing toward Bengal | **survives** |
| **DPYD** | **HapB3** | **−2.68** | **0.0037** | decreasing toward Bengal | **survives** |
| CYP2C9 | \*2 | −2.50 | 0.0062 | decreasing | fails |
| NAT2 | \*5 | −1.72 | 0.043 | decreasing | fails |
| CYP2D6 | \*4 | +1.64 | 0.050 | — | fails |
| NAT2 | \*6 | −1.20 | 0.116 | — | — |
| NAT2 | \*7 | +1.37 | 0.085 | — | — |
| CYP2C19 | \*2 | +0.70 | 0.241 | — | — |
| SLCO1B1 | \*5 | +0.70 | 0.241 | — | — |
| CYP2C19 | \*3 | +0.66 | 0.256 | — | — |
| TPMT | \*3C | +0.55 | 0.290 | — | — |
| CYP2C9 | \*3 | −0.17 | 0.432 | — | — |
| CYP2B6 | \*6 | −0.01 | 0.496 | — | — |

The trend test separates the panel where the spread metric could not: 4 of 13
reach nominal significance against 9 of 13 flagged by the 1.5× rule, and the
ranking is no longer an artifact of allele frequency. CYP2C9 \*2's monotonic
ordering — the one property the audit named — is 1 of 13 informative alleles
(chance for five distinct values is 1/120).

**The audit's evidence was sound and its metric was not.** Both things are
true, and the proposal that came out of it specified the metric rather than
the evidence.

## 5. Why the clines exist: they track continental ancestry

A trend that reflects real population structure should be predictable from
something independent. South Asia's northwest carries more West Eurasian
ancestry and its southeast more East Asian, so an allele's within-SAS
direction should follow its continental EUR↔EAS skew — a quantity already in
the pinned artifact and never used to compute the trend.

Prediction: EUR-skewed alleles decrease NW→SE (z<0); EAS-skewed alleles
increase (z>0).

| Gene | Allele | EUR | EAS | log₂(EAS/EUR) | trend z | predicted? |
|---|---|---|---|---|---|---|
| CYP2C19 | \*3 | 0.00025 | 0.06362 | +7.96 | +0.66 | yes |
| NAT2 | \*7 | 0.02499 | 0.15479 | +2.63 | +1.37 | yes |
| CYP2D6 | \*10 | 0.21657 | 0.57708 | +1.41 | +3.91 | yes |
| CYP2C19 | \*2 | 0.14721 | 0.30740 | +1.06 | +0.70 | yes |
| NAT2 | \*6 | 0.28861 | 0.25754 | −0.16 | −1.20 | yes |
| SLCO1B1 | \*5 | 0.15654 | 0.12599 | −0.31 | +0.70 | **no** |
| CYP2B6 | \*6 | 0.24194 | 0.19133 | −0.34 | −0.01 | yes |
| CYP2C9 | \*3 | 0.06846 | 0.03368 | −1.02 | −0.17 | yes |
| TPMT | \*3C | 0.04291 | 0.01462 | −1.55 | +0.55 | **no** |
| NAT2 | \*5 | 0.45441 | 0.03841 | −3.56 | −1.72 | yes |
| CYP2D6 | \*4 | 0.19689 | 0.00309 | −5.99 | +1.64 | **no** |
| DPYD | HapB3 | 0.02111 | 0.00011 | −7.47 | −2.68 | yes |
| CYP2C9 | \*2 | 0.12756 | 0.00044 | −8.16 | −2.50 | yes |

**10 of 13 directions agree** (binomial p = 0.046 against a coin flip), and
Pearson r(log₂ EAS/EUR, trend z) = **0.554** (t = 2.21, df = 11). **All four
alleles with a significant trend are in the agreeing set.**

This is the mechanistic account the CYP2C9 \*2 audit inferred but could not
test with one allele: the NW→SE gradient is an ancestry gradient, and an
allele's position on it is predictable in advance from its continental skew.
It also reproduces the published pattern for \*2 (PMID 36855170) without being
fitted to it.

CYP2D6 \*4 is the informative disagreement — strongly EUR-skewed
(log₂ = −5.99) yet trending *upward* toward Bengal (z = +1.64). Worth a look:
\*4 is a splice variant and CYP2D6 is the platform's structural-variant gene,
so a hybrid/CNV background is a candidate explanation. Not investigated here.

## 6. Corrections to existing artifacts

### 6.1 Two rsIDs are multi-allelic and the naive query returns nothing

`rs1057910` (CYP2C9 \*3) and `rs28371706` (CYP2D6 \*17) both fail with
*"Multiple variants found, query using variant ID to select one."* Resolved by
scanning the gene's full variant list and disambiguating on population
signature:

- `rs1057910` → **`10-94981296-A-C`**, not `A-G`. The `A-G` alt is a global
  singleton (1/152,146); `A-C` gives SAS 0.1138 against the pinned 0.1096.
- `rs28371706` → **`22-42129770-G-A`**, not `G-T`. `G-A` gives AFR 0.1808
  against the pinned AFR 0.1854. The `G-T` alt gives AFR 0.00002, which would
  invert \*17's defining population signature — it is an African-enriched
  allele.

Anything querying the panel by rsID alone silently drops these two.

### 6.2 The max-frequency-wins dedup rule is correct — now measured, not assumed

The pinned artifact has **20 duplicated `(gene, allele, population)` keys**
across four alleles (CYP2B6 \*6, CYP2C9 \*3, CYP2D6 \*17, DPYD \*2A) from two
ingestion passes never deduplicated upstream. `population_signal.py` and
`allele_frequencies.py` both resolve this by keeping the higher frequency,
documented as a reasonable inference.

**All 20 max-wins values were checked against live gnomAD v2.1.1 exomes and
match to six decimal places.** Including the four where the discarded row is
not near-zero and the rule looked like a judgement call (CYP2D6 \*17 AMR/EUR/
SAS, DPYD \*2A AMR). The heuristic is now verified.

Taking the *last* row instead — the obvious naive choice, and the one this
audit's own first pass made — reads CYP2B6 \*6 SAS as 0.000033 rather than
0.389354, an **11,800-fold understatement**. Recorded because the error was
made here and caught by cross-checking against the live API rather than by
reading the code.

### 6.3 A stale claim in five cohortfit documents

`cohortfit/docs/PITCH.md` (judge-facing), `docs/METHOD.md`, `docs/FINDINGS.md`,
`docs/SLIDES.md` and `README.md` all still describe the `*2A` discrepancy as an
**exome-capture artifact** with SAS pinned at 0.0005, and count a "`*2A` exome
undercount, up to 1.41× at-risk" among the stacked underestimate floors.

The cohortfit fixture's own `known_discrepancies` block, updated 2026-08-08 and
committed 2026-08-16, supersedes all five: it was a **transcription error** —
the pinned 0.0005 used c.2846A>T's allele count (45) over c.2846A>T's joint AN
(91,074). Corrected to 0.0040, which sits inside the published band rather than
6–16× below it. The fixture records this explicitly:

> *"The earlier 0.0005 was a transcription error, not an exome-capture
> artifact… The 8× error is fixed; the residual gnomAD/1000G disagreement is
> genuine and is shown rather than resolved."*

`PITCH.md` line 124 is the one that matters: it answers the question "any
number you don't trust?" with a number and a mechanism that are both now
wrong. The residual gnomAD-vs-1000G spread (0.0040 vs 0.0075–0.0080) is real
and is what the sensitivity range describes, so the honest answer is still
available — it is just a different one, and the 1.41× floor should be
recomputed or dropped rather than restated.

**Not fixed here.** Correcting judge-facing pitch material and the derived
floor arithmetic is a cohortfit change with its own test surface, and doing it
inside a project_astra research pass would bury it.

## 7. What should change

1. **Do not ship `clinality_index` as a bare fold-spread with a fixed
   threshold.** It flags 69% of the testable panel, ranks by rarity, and
   misclassifies NAT2 \*6 in the direction that matters. Ship the
   Cochran-Armitage z and its p instead — same input data, one extra line of
   arithmetic, and it discriminates.
2. **Require the informativeness gate first.** Below ~10 alt observations
   across the five cells, emit a named refusal rather than a ratio. This is
   7/20 of the panel, including two of the four CPIC DPYD variants.
3. **Correct the record on CYP2C9 \*2.** It is a real cline (p = 0.0062) but it
   is the *third* strongest on the panel and does not survive multiple-testing
   correction across 13 alleles. The strategy doc's "2.9-fold spread, wider
   than the cross-source gap" framing should become "a significant NW→SE trend,
   one of four, and not the strongest."
4. **CYP2D6 \*10 is the finding to lead with.** z = +3.91, p = 0.00005,
   survives Bonferroni, 165 alt observations, and it is an *increasing* cline
   toward Bengal — the opposite direction from \*2, which makes the ancestry
   mechanism visible rather than looking like a single anecdote. CYP2D6 also
   has more actionable CPIC drug pairs than CYP2C9.
5. **The generalisable claim is stronger than the one currently drafted.** Not
   "super-populations hide clines" (true but unfalsifiable as stated) but:
   *an allele's within-super-population gradient is predictable in advance from
   its continental ancestry skew* (r = 0.554, 10/13 directions). That is a
   testable rule which tells you which alleles need subpopulation resolution
   before querying for it.

## 8. Honest limitations

- **~200 alleles per subpopulation cell.** Every conclusion here is limited by
  that. The trend test is better powered than the spread metric because it uses
  the ordering, but it cannot manufacture precision that is not in the data.
- **The NW→SE scoring is ordinal and hand-assigned** (0,1,2,3,4 for PJL, GIH,
  ITU, STU, BEB). It encodes a geographic prior. A different defensible
  ordering — by measured ANI/ASI ancestry proportion rather than by longitude —
  might give different z values. This should be checked against Moorjani 2013 /
  Narasimhan 2019 ancestry estimates, and is the specific question to put to
  CCMB (Dr. Thangaraj) per the strategy doc's §6.3 priority 3.
- **13 tests, no pre-registration.** Bonferroni is reported and only 2 of 4
  nominal hits survive it. The continental-skew correlation (§5) is a genuine
  out-of-sample check on direction, but it was run after seeing the trend
  results.
- **1000 Genomes subpopulations are not communities.** PJL/GIH/ITU/STU/BEB are
  five samples of convenience, several collected in diaspora (GIH in Houston,
  ITU and STU in the UK). They cannot resolve the community-level structure
  Kerdoncuff 2025 showed matters (BCHE L307P 0.28% overall vs 5.3% in
  Telangana Vysya). GenomeIndia's 83–99 population groups remain the only
  route to that, and the FeED application is still unfiled.
- **Chi-square with low expected cell counts.** Three alleles (DPYD HapB3,
  TPMT \*3C, CYP2C19 \*3) have a minimum expected cell below 5, so their
  χ² p-values are unreliable. The Monte Carlo null does not have this problem
  and is the one relied on; both are reported.
- **HGDP could not validate the axis.** The 8 HGDP South/Central Asian groups
  with usable ANs (Pathan, Sindhi, Balochi, Brahui, Makrani, Burusho, Kalash,
  Hazara) are all northwest — Pakistan and Afghanistan — with ~40 alleles each.
  They cannot test a NW→SE gradient because they are all at one end of it.

## 9. Reproducing

```bash
cd project_astra
python scripts/query_sas_clinality_panel.py     # live gnomAD, ~20 queries
# writes scripts/sas_clinality_panel.json
```

The script is the only network-touching code involved.
`astra/discovery_engine/frequency_divergence.py` stays pure and consumes frozen
numbers, per that package's discipline.
