# Population Data Strategy — Is "Build on European Data, Plug In Populations"
# the Right Architecture? (2026-08-16)

> **Purpose.** Decide the platform's population-data strategy before the next
> build cycle, and record the evidence for the decision. Answers four
> questions asked directly:
>
> 1. Is population-plugging the solution — build the engine on available
>    European data, then make it work for any population by plugging in that
>    population's data?
> 2. What are the limitations, and how can they be overcome?
> 3. Is collecting Indian mouse strain data a viable alternative?
> 4. How do we approach Indian researchers to solve the data problem?
>
> **Every number in this document is from a live query or a cited paper.**
> Where a claim is inference rather than measurement, it says so.

---

## 0. Answers up front

| Question | Answer |
|---|---|
| Population-plugging? | **Yes as architecture, no as a claim.** The plumbing is right and already built. "Swap the table, get the right answer" is false and we can now prove it. |
| Biggest limitation | Frequency substitution is **per-allele, not global.** For CYP2C9 \*2 the source swap moves 34%; for \*3 and SLCO1B1 \*5, under 2%. Nothing in the swap reveals which case you're in. |
| Mitigation | Report divergence and **clinality** as first-class engine outputs instead of silently preferring a source. Detailed in §3. |
| Indian mice? | **No.** Killed on orthology grounds — no 1:1 mapping for the key genes, no star alleles, no CPIC. §4. |
| Better approach | Human data is already sufficient and mostly open. Four datasets we are not yet using, one of which (GenomeIndia, 10,174 genomes) is **released and applicable now.** §5. |
| Researcher outreach | Lead with a finding, not a request. We have three findings that make credible openers, and an existing warm-intro chain. §6. |

---

## 1. What "population-plugging" actually means, and whether it holds

The proposition: build the deterministic engine once against whatever data
exists (largely European), keep population allele frequency in a swappable
layer, and gain any new population by plugging in its frequency table without
touching engine logic.

**The architectural half is correct and already shipped.** In this platform:

- `anukriti-pgx-core` (13 genes, CPIC-pinned) contains **no** population
  frequency data at all. Diplotype → phenotype is a pinned CPIC table lookup.
  It is population-independent by construction, which is why plugging works.
- `anukriti-swarm/datasets/pharmfreq/` holds frequency records as a separate
  dataclass layer (`AlleleFrequencyRecord`: gene, allele, population,
  frequency, sample_n, source, version, function).
- `cohortfit/src/cohortfit/frequencies.py` enforces a **provenance contract**
  on every plugged-in table: any non-`*1` allele lacking an rsID,
  `alt_observed`, `total_alleles`, or `source` raises `FixtureError`, and
  populations must sum to 1.0. It additionally hard-fails on suspicious
  round numbers (`_SUSPICIOUS_FREQUENCIES = {0.27, 0.05}`) — the literal
  DPYD incident (§2) encoded as a permanent test.

That third component is the genuinely defensible piece, and it is worth being
precise about why: **swappable frequency backends are not novel.** PharmFreq
(IKP Stuttgart) aggregates PGx frequencies from ~6M individuals across 137
countries and 415 alleles from 1,200+ studies. PharmCAT has already been run
across UK Biobank biogeographic groups to produce per-group allele, diplotype,
and phenotype frequencies (PMID 37757824). A paper claiming "pluggable
population modules" as its contribution would not survive review.

**The claim half is false**, and this is the substantive finding of this
document.

### 1.1 The measurement that breaks the naive claim

Re-scoring three risk alleles against IndiGenomes (1,029 Indian WGS) versus
the platform's pinned gnomAD-SAS proxy (`ASTRA_FINDING_INDIGENOMES_RESCORE_PILOT_2026-07-21.md`):

| Allele | India-only (IndiGenomes) | gnomAD SAS proxy | Divergence |
|---|---|---|---|
| SLCO1B1 \*5 (rs4149056) | 0.0513 | 0.0505 | 1.6% |
| CYP2C9 \*3 (rs1057910) | 0.1093 | 0.1096 | 0.3% |
| CYP2C9 \*2 (rs1799853) | 0.0307 | 0.0467 | **34.2%** |

Two of three alleles: the European-derived infrastructure's South Asian proxy
is essentially exact. One allele: it is off by a third. **Same gene for two of
them.** A blanket source swap would have silently moved one number by 34% and
left the others alone, reporting none of it.

### 1.2 Why — and the number that matters most

Auditing that discrepancy against gnomAD's live API on 2026-08-16
(`CYP2C9_STAR2_SAS_FREQUENCY_AUDIT_2026-08-16.md`) established that the pinned
row is **exactly right** (live v2.1.1 exome AF 0.046740 vs pinned 0.0467).
Not an extraction bug. The divergence is real population structure.

Querying the five 1000 Genomes South Asian subpopulations *within a single
callset* (gnomAD v3.1 `1kg:*` IDs — no version or exome/genome confound):

| Subpopulation | Region | AF |
|---|---|---|
| PJL Punjabi (Lahore) | NW Pakistan | **0.0588** |
| GIH Gujarati | W India | 0.0495 |
| ITU Telugu | SE India | 0.0245 |
| STU Sri Lankan Tamil | Sri Lanka | 0.0245 |
| BEB Bengali | Bangladesh | **0.0200** |

**CYP2C9 \*2 varies 2.9-fold inside the single super-population the platform
treats as one number — a wider spread than the 34% cross-source gap that
triggered the investigation.** The ordering is monotonic northwest to
southeast, and the gradient continues in both directions in the same query
(Sardinian 0.2885, Palestinian 0.2024, NFE 0.1266 → SAS → EAS 0.0006). This
reproduces the independently published pattern: \*2 is "most abundant in
Europe and the Middle East, whereas CYP2C9\*3 was the main reason for reduced
CYP2C9 activity across South Asia" (PMID 36855170).

So: \*3 and SLCO1B1 \*5 matched across sources because **they are not clinal**.
\*2 diverged because it sits on one of the steepest gradients in the actionable
PGx panel.

> **The finding, stated once:** *the accuracy of a population proxy is a
> property of the allele, not of the population.* "Is gnomAD SAS good enough
> for India?" has no single answer. It has one answer per allele, and the
> answer is computable in advance from data already in hand.

---

## 2. The prior incident that makes this credible

We have already shipped the failure mode this document is designed to prevent,
and caught it ourselves (`DPYD_SAS_OVERRIDE_AUDIT_2026-07-28.md`).

`U4_SAS_DPYD_OVERRIDE` shipped in `anukriti-swarm` on 2026-06-06 and ran live
for **52 days**. It blocked clinical synthesis for South Asian patients
carrying DPYD \*9A or M166V, justified as "27% carrier frequency … clinically
significant toxicity risk," citing Hariprakash 2018.

- The paper is real and correctly cited.
- **The frequency was hand-written.** The pinned frequency artifact contained
  no rows for either allele.
- Real gnomAD v2.1.1 **inverts the direction**: M166V SAS 0.0906 < EUR 0.1004
  (ratio 0.90); \*9A SAS 0.2550 vs EUR 0.2226 (ratio 1.15 — not enrichment;
  AFR 0.4131 is the population maximum).
- The clinical literature is genuinely contested: Hariprakash 2018 found M166V
  associated with hand-foot syndrome (OR 5.22, p=0.011, n=110) but its \*9A
  assay failed outright; Naushad 2021 pooled Indian data found no association
  for either (\*9A OR 1.03, p=0.95; M166V OR 1.54, p=0.32); Atasilp 2025 found
  a \*9A association on n=2 homozygotes that did not survive its own
  multivariate analysis.

Resolution: the refusal was **downgraded to a named uncertainty**
(`P1_SAS_DPYD_CONTESTED`) rather than flipped to the opposite assertion, on
the grounds that blocking on contested evidence is the same class of error as
CPIC asserting a EUR-derived call everywhere.

This is the strongest asset the platform has, and it is worth naming why:
**a citation can be real, correctly formatted, and not support the number
attached to it.** No linter, type checker, or test suite catches that — it is
a truth defect wearing correct syntax. It is also exactly what a
population-plugging architecture invites, because plugging makes it cheap to
introduce a number and expensive to verify it.

### 2.1 Outstanding correction required

`anukriti_docs/DPYD_PARTNERSHIP_PITCH.md` still carries the refuted claim in
four places — line 17 ("DPYD \*9A carrier frequency in South Indians **27%**"),
line 20 ("1 in 4 South Indian patients"), line 87, line 108. **This document is
partner-facing.** It must be corrected before any further outreach; see §6.4.

---

## 3. Limitations of population-plugging, and the mitigation for each

| # | Limitation | Concrete evidence | Mitigation |
|---|---|---|---|
| L1 | Substitution accuracy is per-allele | \*2 34% vs \*3 0.3% (§1.1) | **Divergence reporting**: query all available sources, report the spread per allele rather than picking one. |
| L2 | Super-populations hide clines | 2.9× within SAS (§1.2) | **`clinality_index`** on each frequency record: within-super-population spread, computed from `1kg:*` subpop IDs in one query. Flag any allele whose internal spread exceeds its cross-source divergence — "SAS" is a misleading unit for that allele. |
| L3 | Pooled national cohorts still hide community structure | Kerdoncuff 2025 (*Cell* 188(13):3389-3404): BCHE L307P at 0.28% overall in India but **5.3% in Telangana Vysya**; LASI-DAD n=2,762 carries ~24M SNVs + ~2.2M indels absent from gnomAD/1000G | Do not claim community-level resolution from IndiGenomes (single pooled India-wide frequency). State the resolution ceiling of each source explicitly in its provenance record. |
| L4 | Hand-written numbers enter through the plug point | The 52-day incident (§2) | Already mitigated: `frequencies.py` rejects any allele lacking rsID + `alt_observed` + `total_alleles` + `source`, and hard-fails on round-number sentinels. Keep this as the non-negotiable contract on every new source. |
| L5 | Callset composition is not like-for-like | v2.1.1 exome 0.0467 vs v3.1 genome 0.0388 for the same allele | Require `callset` in provenance. An exome-vs-genome comparison is not a version comparison — the 2026-07-21 pilot was misled by exactly this. |
| L6 | Frequencies are not function | CYP2C9 MAVE study: single-assay MAVE labels disagree with CPIC clinical phenotype at **all four** testable anchors (\*2, \*3, \*6, \*11); v2 model scored 1/6 on held-out clinical alleles | Documented negative result. Frequency plugging tells you *how many* people carry an allele, never *what it does*. Function stays CPIC-pinned; the ML tier only ranks the non-CPIC tail. |
| L7 | Small-N sources give imprecise estimates | IndiGenomes 0.0307 has 95% CI ≈ 0.023–0.039; each 1000G subpop ~200 alleles | Propagate CI, don't just plug point estimates. Report the interval where N is small rather than implying precision. |
| L8 | Structural variants don't plug at all | AFR (NA19317) and EAS (NA18545) CYP2D6 SV truth cells have no usable public long-read data — verified absent from both accessible ENA projects and HPRC Release 2 | Genuine public-data gap, not a pending rerun. Disclose as a limitation; SV capability is validated on EUR ×2 + SAS ×1 only. |

**The synthesis of L1–L2 is the paper's contribution.** Not "we made
frequencies swappable" (prior art), but: *frequency substitution has a
measurable, per-allele error structure, and a system that swaps sources without
reporting it is making an unstated claim.* That is a statement about
population-aware infrastructure that nobody has published, and we can support
it with our own measurements plus our own shipped failure.

---

## 4. Indian mouse models — verdict: no

Assessed because it was raised as a possible route to Indian-specific data.
It does not work for pharmacogenomics, on structural grounds rather than
practical ones.

**4.1 No 1:1 orthology for the key genes.** Human *CYP2D6* is one gene; the
mouse *Cyp2d* cluster has nine. Human *CYP2C* has four; mouse *Cyp2c* has
~15. Human star alleles (\*4, \*5, \*10, \*68 hybrids) have no mouse
counterpart to map onto. The primary literature is unambiguous: *"because of
the differences in the multiplicity and substrate specificity of CYP2D family
members among species, it is difficult to predict pathways of human
CYP2D6-dependent drug metabolism on the basis of animal studies"* (PMID
21989258); *"animal models are inadequate for preclinical pharmacological
evaluation of CYP2D6 substrates because of marked species differences in CYP2D
isoforms"* (PMID 11723233).

**4.2 The variant catalogue is human.** Mouse *Dpyd* exists as a 1:1 ortholog,
but DPYD \*2A, \*13, c.2846A>T, and HapB3 are human variants. Strain-to-strain
*Dpyd* variation in mice does not correspond to them. There is no PharmVar for
mice.

**4.3 No clinical framework.** CPIC issues guidelines for humans. There is no
mouse activity-score system, no mouse metabolizer phenotype bins, no mouse
dosing recommendation. The platform's entire output contract — diplotype →
phenotype → CPIC-graded recommendation with provenance — has no mouse analogue.

**4.4 Immune-mediated PGx is impossible in mice.** Mice have the H-2 complex,
not HLA. HLA-B\*15:02 (carbamazepine SJS) and HLA-B\*57:01 (abacavir
hypersensitivity) cannot be modelled.

**4.5 Being fair to what mice do offer.** Humanized *CYP2D6* transgenic mice
are real and useful — they model extensive vs poor metabolizer phenotypes
(PMID 15237854), human CYP2D6 is functional in mouse brain in vivo (PMID
32189192), and a humanized poor-metabolizer model was profiled as recently as
2024 (PMID 39265705). Collaborative Cross panels support genuine
pharmacogenetic QTL mapping. **But these model the enzyme, not the
population.** A humanized mouse carries one human transgene; it can tell you
what CYP2D6 does, never what fraction of Gujaratis carry \*4. Indian-origin
mouse strains would yield Indian *mouse* variation, which has no mapping to
human allele frequencies. Indian pharmacology labs (IISc, CCMB, NIN Hyderabad)
use standard C57BL/6J, BALB/c, and Swiss Albino for this reason.

**4.6 Cost of the mistake.** Pursuing it would mean abandoning CPIC-pinning —
the single property that makes the platform auditable — in exchange for data
that cannot answer a dosing question. If wet-lab validation is wanted later,
the correct routes are human liver chimeric mice repopulated with South Asian
donor hepatocytes, or iPSC-derived hepatic organoids from South Asian
individuals. Neither is needed for the product or the paper.

---

## 5. The data landscape — what we are not yet using

Verified 2026-08-16. Corrects three claims from an earlier internal research
pass that were wrong.

| Dataset | South Asian / Indian content | Access | Status here |
|---|---|---|---|
| gnomAD v2.1.1 exomes | SAS AN 30,616 at rs1799853 | Open | **In use** (pinned) |
| gnomAD v4.1 | SAS exome AN 86,254; genome AN 4,820 | Open | Partly — cohortfit DPYD requeried 2026-08-08 |
| gnomAD v3.1 `1kg:*` / `hgdp:*` | 5 SAS subpops + 13 HGDP South/Central Asian groups | Open | **New this session** — the clinality measurement (§1.2) |
| 1000 Genomes Phase 3 | 489 SAS (GIH, PJL, BEB, STU, ITU) | Open | In use |
| CSIR-IndiGen / IndiGenomes | 1,029 Indian WGS | Open, undocumented POST API | Queried in the pilot; **not yet a first-class source** → §7 |
| **GenomeIndia** | **10,174 WGS sequenced; 9,768 analysed, 83–99 population groups, 44M variants absent from gnomAD/1000G/GenomeAsia** | **Released** — IBDC, FeED protocol under BIOTECH-PRIDE, approved researchers in India and abroad | **Not applied for. Highest-value action available.** |
| Genes & Health | **44,028 British Pakistani/Bangladeshi whole exomes + longitudinal EHR linkage** | Published, managed access | **Not used. Overlooked entirely until now.** |
| GenomeAsia 100K | 598 South Asian WGS | Open/query | Unreachable from this network (confirmed twice) |
| LASI-DAD (Kerdoncuff 2025) | n=2,762; ~24M SNVs absent from gnomAD | Published | Cited, not queried |

### 5.1 Three corrections to the earlier research pass

1. **"GenomeIndia data release pending" — false.** It is released. 10,174
   genomes sequenced, archived at IBDC, accessible to approved researchers via
   FeED. The flagship preprint (medRxiv 2026.03.20.26348801) has a dedicated
   pharmacogenomic-variants supplementary section (S13) and a
   Eurocentricity-of-polygenic-scores section (S14). This is an application to
   file today, not a future event.
2. **"Plug in IndiGen — the single biggest upgrade available today" — already
   done and the conclusion was the opposite.** The 2026-07-21 pilot ran it. Two
   of three alleles moved by under 2%. Wholesale replacement would be close to
   a no-op that discards the divergence signal (§1.1).
3. **"Nobody has published this architecture" — false.** PharmFreq and the
   PharmCAT/UK Biobank work are direct prior art (§1). Our own frequency module
   is named `pharmfreq` after it.

**Also missed entirely:** Genes & Health. 44,028 South Asian exomes with EHR
linkage, and an existing CYP2C19 paper on that cohort (PMID 37808344) reporting
57% intermediate-or-poor metabolizers with a clopidogrel recurrent-MI
association — which is the published version of this platform's own trigger
story. It should be cited in the paper regardless of whether we obtain access.

---

## 6. Reaching out to Indian researchers

### 6.1 Principle

Lead with a finding, not a request. Every group listed below receives data
requests constantly. What they do not receive is a specific, checkable
measurement about their own domain plus an offer of reciprocal value.

**We have three openers that qualify:**

- **The clinality finding** (§1.2) — CYP2C9 \*2 varies 2.9× across South Asian
  subpopulations; the "SAS" super-population is a misleading unit for clinal
  alleles. Directly relevant to anyone doing Indian PGx frequency work.
- **The 52-day self-audit** (§2) — a shipped safety rule justified by a
  fabricated frequency, caught and corrected in public. Establishes that we
  audit ourselves, which is the credibility currency that matters most.
- **The CYP2C9 MAVE negative result** — functional-assay labels diverge from
  CPIC clinical phenotype at all four testable anchors. Saves anyone
  considering that approach several months.

### 6.2 Existing warm chains (use these first)

The platform already has real relationships documented in
`anukriti_docs/founder-research/`:

- **Dr. Andrea Gaedigk** (Children's Mercy Kansas City, PharmVar steward) —
  consulted on star-allele nomenclature. PharmVar is the authority on allele
  definitions; the clinality finding is squarely her domain.
- **Dr. Andrew Somogyi** (IUPHAR PGx chair) — reached *via Gaedigk's referral*,
  on population pharmacogenomics in Asia-Pacific. The chain works; use it.
- **Dr. Deepak Roshan V G** (Malabar Cancer Centre, Molecular Biology) —
  co-author on the paper draft, clinical input on DPYD oncology and MTB output.
  MoU outline already drafted (`mcc-visit/05_data_sharing_mou_outline.md`).

### 6.3 Priority targets

| Priority | Target | Why them | The ask |
|---|---|---|---|
| 1 | **IBDC / GenomeIndia** (DBT) | 10,174 Indian genomes, 99 population groups — the only source with the community-level resolution L3 requires | Formal FeED data-access proposal. Not a collaboration ask; a documented application. |
| 2 | **CSIR-IGIB** (IndiGenomes authors, PMID 33095885) | Own the cohort we already queried; their undocumented API is our second source | Co-authorship-grade offer: we contribute the divergence + clinality analysis across their cohort vs gnomAD for the full actionable panel. They get an analysis they have not published; we get sanctioned access and provenance we can cite. |
| 3 | **CCMB Hyderabad** (Dr. K. Thangaraj) | Co-author on both foundational Indian population-structure papers (Moorjani 2013, Narasimhan 2019) *and* GenomeIndia | Population-structure review of the clinality method. He is the right person to say whether NW→SE ordering reflects ANI/ASI gradients. |
| 4 | **BRIC-NIBMG Kolkata** (Dr. Analabha Basu) | Lead author on GenomeIndia flagship study design + allele frequency spectrum sections | Direct: does GenomeIndia's own S13 PGx section report per-population-group frequencies for CPIC alleles? If yes, that is the L3 mitigation. |
| 5 | **MCC Kannur** (Dr. Roshan) — existing | Prospective clinical validation site; DPYD/5-FU need already identified | Advance the drafted MoU to a retrospective genotype-phenotype cohort. This is the dataset that fixes L6 (real clinical labels, not assay surrogates). |
| 6 | **Genes & Health** (QMUL, van Heel) | 44,028 South Asian exomes + EHR; published clopidogrel/CYP2C19 outcome data | Managed-access application. Their cohort is British South Asian — a *third* point on the clinality gradient, and diaspora vs subcontinental comparison is itself a finding. |

### 6.4 Preconditions before sending anything

1. **Correct `DPYD_PARTNERSHIP_PITCH.md`** (§2.1). Sending a partner-facing
   document containing a claim our own audit refuted is the single worst
   outcome available here. The corrected version is *stronger*: "we found and
   fixed this ourselves in 52 days" beats an inflated frequency.
2. Pin every number in outreach material to a queryable source with a date.
3. Offer reciprocity explicitly — analysis, tooling, or co-authorship — rather
   than requesting data for an unnamed benefit.
4. Do not overclaim novelty. Cite PharmFreq and the PharmCAT/UKB work as prior
   art; our contribution is the error structure, not the plumbing.

---

## 7. Decision

**Adopt population-plugging as architecture. Reject "swap the table, get the
right answer" as a claim. Ship divergence reporting so the difference is
visible.**

Concretely:

1. IndiGenomes becomes a **second queryable source**, not a replacement, with
   per-allele divergence reported against gnomAD SAS.
2. `clinality_index` on frequency records — within-super-population spread from
   `1kg:*` subpopulations, computed for every pinned allele.
3. Both feed the existing named-refusal discipline: an allele whose clinality
   exceeds a threshold gets a named uncertainty flag, not a silent number.
4. GenomeIndia FeED application filed; Genes & Health cited now, applied for
   next.
5. Mice: closed. No further work.
6. Paper reframed around the error structure of population substitution, with
   the 52-day incident and the CYP2C9 MAVE negative result as the honesty
   spine, and the CYP2D6/DPYD/warfarin validation as the methods spine.

**What this is not.** It is not a claim that European-derived infrastructure
serves Indian patients adequately. It is the opposite: the infrastructure is
adequate for ~2 of 3 actionable alleles by measurement, badly wrong for clinal
ones, and the only honest system is one that says which is which per allele.
That is a smaller claim than "population-pluggable" and a defensible one.
