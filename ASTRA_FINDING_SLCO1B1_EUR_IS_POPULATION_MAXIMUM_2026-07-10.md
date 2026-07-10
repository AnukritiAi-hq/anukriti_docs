# ASTRA Finding: EUR Is the Population Maximum for SLCO1B1*5, Not an
# Outlier — 2026-07-10

> **Scope:** documents a real, verified, previously-uncomputed finding from
> `project_astra`'s Discovery Engine: extending the platform's existing
> risk-allele population comparison beyond its default SAS-vs-EUR pair to
> AFR, AMR, and EAS shows that EUR carries the SLCO1B1\*5
> (rs4149056/statin-myopathy) risk allele at the **highest** frequency of
> any of the five gnomAD-tracked population groups — not as an outlier
> being compared against, but as the actual population maximum. Every
> number below is computed directly against the platform's own pinned
> gnomAD v2.1.1 artifact, re-verified before writing this document, not
> recalled from memory.
>
> **Repo:** `project_astra`, commit `eb4ee87` (`feat: extend risk-allele
> comparison beyond SAS/EUR -- EUR is the population maximum for
> SLCO1B1*5, not an outlier`). Code: `scripts/
> extend_population_comparison_afr_amr_eas.py`. Tests: `tests/
> test_extend_population_comparison_afr_amr_eas.py` (5 tests, including a
> real-data regression guard against the pinned artifact).
>
> **Relationship to prior documents:** this extends, and should be read
> alongside, `ASTRA_DISCOVERY_SIGNAL_ASYMMETRY_AND_DRAFT_REVIEW_2026-07-10.md`
> (same folder) and the underlying human-reviewed `ReviewRecord` for
> `SLCO1B1<->atorvastatin` in `discovery_candidates_2026_07_08.json`
> (`final_evidence_tier: MODERATE`, reviewer Abhimanyu R B, 2026-07-10).

---

## 1. The question this document answers

Every population-equity analysis this platform has produced to date —
`compose_equity_signal.py`, `analyze_signal_direction_asymmetry.py`,
`docs/14-reporting-bias-framing-note.md`, `docs/15-population-stratified-
corroboration-framing-note.md` — compares exactly two populations: SAS and
EUR. This is deliberate and well-justified (the platform's own founding
equity frame, per `population_signal.py`'s module docstring: the
clopidogrel/CYP2C19 trigger story and Martin et al. 2017's >50%
PRS-accuracy-drop finding). But the underlying function,
`population_signal.compare_two_populations`, has never actually been
restricted to that pair — `population_a`/`population_b` are ordinary
keyword arguments with SAS/EUR only as *defaults*. The module's own
docstring says this explicitly: *"the underlying
`population_risk_allele_frequency` function is not restricted to those two
codes."*

**Checked before writing any new code:** grepped the entire repository for
any real (non-synthetic-fixture) AFR, AMR, or EAS comparison against actual
gnomAD data. Found none — one test file uses a fixture gene literally named
`"AFRONLYGENE"`, confirming the capability was tested in isolation but never
exercised against real data for a real gene. This was genuine, unexplored
territory using code that already existed, already worked, and was already
tested for correctness — the lowest-risk way to generate a new finding.

## 2. Scope decision: SLCO1B1 only, not CYP2C9

This session's earlier work (same date, same folder,
`ASTRA_DISCOVERY_SIGNAL_ASYMMETRY_AND_DRAFT_REVIEW_2026-07-10.md`) produced
a completed, human-reviewed `ReviewRecord` for both of the Discovery
Engine's current candidates:

- `CYP2C9 <-> aspirin`: `mechanism_plausibility = false`. CPIC's own
  guideline places aspirin in an evidence-only, no-recommendation bucket
  distinct from ibuprofen's recommendation tier (verified against CPIC's
  primary source, not a secondary aggregator); aspirin's GI-bleed mechanism
  is dominated by COX-1 inhibition, independent of CYP2C9 metabolizer
  status. `final_evidence_tier: INSUFFICIENT`.
- `SLCO1B1 <-> atorvastatin`: `mechanism_plausibility = true`. CPIC's 2021
  statin guideline (PMC9035072) directly covers atorvastatin by SLCO1B1
  phenotype; the transporter mechanism (OATP1B1-mediated hepatic statin
  uptake) is established biology, with a real, named caveat that clinical
  penetrance is moderate for atorvastatin specifically (vs. "strongest" for
  simvastatin). `final_evidence_tier: MODERATE`.

That review already established the operative rule this document follows:
**allele frequency is only informative when a real mechanism has been
independently confirmed for the specific drug in question.** Invoking
CYP2C9 allele frequency for aspirin, where the mechanism was rejected,
would smuggle a dismissed mechanism back in through population framing —
this was caught and corrected as a real error earlier in the same review
session. This document therefore deliberately extends the population
comparison **only** for SLCO1B1, the one candidate where the mechanism
itself is not in question.

## 3. The real result

Computed directly against `anukriti-swarm/datasets/pharmfreq/
gnomad_v2_1_1_frequencies.jsonl` (the platform's pinned gnomAD v2.1.1
artifact — the same file the production frequency layer serves from, per
`docs/06-anukriti-integration.md` §2.2's "client, not a copy" discipline).
Verified by direct inspection that SLCO1B1's `*5` allele (rs4149056) is the
**sole** contributing allele in every population row in this dataset — so
there is no allele-pooling ambiguity to control for; every number below is
already allele-specific.

| Population | SLCO1B1\*5 frequency | Reference sample size (n) | Fold-enrichment vs. EUR |
|---|---|---|---|
| AFR | 0.02812 | 8,126 | **0.1796x** (most depleted) |
| SAS | 0.05047 | 15,276 | 0.3224x |
| AMR | 0.11211 | 17,265 | 0.7161x |
| EAS | 0.12599 | 9,191 | 0.8048x |
| **EUR** | **0.15654** | **56,729** | **1.0 (reference, and the maximum)** |

**The finding, stated precisely:** EUR is not merely the reference
population in this comparison — it is the population with the highest
observed SLCO1B1\*5 frequency of any group in the dataset. Every other
population (AFR, AMR, EAS, SAS) is allele-*depleted* relative to EUR, by
factors ranging from roughly 1.25x (EAS) to 5.6x (AFR). This is a
materially different picture from the platform's existing SAS-only framing,
which correctly states that SAS is depleted relative to EUR but does not by
itself convey that EUR is actually the outlier on the high end across the
whole dataset, not merely "the population SAS happens to be compared
against."

**Verified not to be a small-sample artifact:** EUR's reference sample
(n=56,729) is the largest of all five populations — 3.3x AMR's, 6.2x AFR's,
6.9x SAS's. A higher observed frequency resting on a *smaller* sample would
warrant real suspicion of noise; here it rests on the *largest* sample,
which if anything makes the finding more, not less, credible.

## 4. What this does and does not mean

**Does not mean:**
- Nothing here is a claim about myopathy incidence in any population.
  gnomAD carries no outcome data — this is allele frequency only, the same
  structural limitation every other `population_signal.py` output already
  carries.
- This is not a claim that non-EUR populations are protected from statin
  myopathy. Myopathy risk plausibly has real contributors beyond SLCO1B1\*5
  (other transporter variants, CYP2C9 co-genotype per the 2021 CPIC
  guideline's own multi-gene scope, drug-drug interactions, dose, renal
  function) that this single-allele, single-gene comparison cannot speak to
  at all.
- This is not evidence that the SLCO1B1-statin-myopathy mechanism itself is
  wrong. The transporter biology (OATP1B1-mediated hepatic uptake) is
  established regardless of which population was used to characterize it.

**Does mean, and this is the real, novel contribution:**
- The CPIC/PharmGKB evidence base for SLCO1B1-statin myopathy — largely
  built on cohorts where European ancestry predominates (the SEARCH trial,
  the foundational GWAS discovery cohort, is UK-based) — was characterized
  in the one population where this specific risk allele happens to be
  *most* common, not a population where it happens to be unusually rare.
  This reframes the generalizability question: rather than asking "is the
  EUR-derived finding under-detected in other populations because of a
  reporting gap" (the platform's existing SAS-vs-EUR framing), the more
  precise question for non-EUR populations broadly is "how well does an
  allele-frequency-driven risk model, calibrated on the population with the
  highest carrier frequency, transfer to populations where the carrier
  frequency — and therefore the population attributable fraction of
  myopathy cases explained by this specific variant — is mechanically
  lower, even if per-carrier relative risk is unchanged?"
- This is a distinct question from the reporting-visibility gap already
  named in `ASTRA_DISCOVERY_SIGNAL_ASYMMETRY_AND_DRAFT_REVIEW_2026-07-10.md`
  §2–3. That document correctly separated "known allele depleted in SAS"
  from "no myopathy risk in SAS" and named the FAERS reporting gap (SAS at
  0.8% of proportional reporting) as the real, standalone equity concern.
  This document adds a second, independent axis: even setting FAERS
  reporting aside entirely, the *evidentiary basis itself* for this
  gene-drug mechanism is population-skewed toward the group carrying the
  most risk allele — a distinct concern from whether adverse events in
  other populations get reported at all.

## 5. Primary-source confirmation: the foundational cohort was not merely
## EUR-skewed — non-European ancestry was actively excluded by design

The original version of this document (written before this section was
added) named "auditing whether SEARCH was literally EUR-predominant" as an
open item for a future pass (see §6, item 2, in the original draft). That
check was done the same day, against the actual primary source — Timothy
et al. 2008, *"SLCO1B1 Variants and Statin-Induced Myopathy — A Genomewide
Study,"* NEJM 359(8):789-799 (the SEARCH Collaborative Group's own
discovery paper) — rather than left as an inference from allele frequency
alone.

**What the primary source's own Methods section states, verbatim:**

- The discovery cohort was *"12,064 participants from the United Kingdom
  who had had a myocardial infarction"* — recruited entirely within one
  country.
- **Non-European ancestry was excluded from the discovery analysis by
  design, not merely under-represented by recruitment demographics**: *"one
  case subject who had classified himself as having non-European ancestry
  was excluded"* from the 85-case/90-control genomewide association
  analysis. A further 4 participants who clustered separately by
  multidimensional-scaling ancestry analysis were flagged and handled with
  a sensitivity analysis (excluding them changed the association P-value
  only marginally, from 2.4×10⁻⁹ to 2.0×10⁻⁹ — the paper's own robustness
  check, not this document's interpretation).
- The independent replication cohort (the Heart Protection Study,
  20,536 participants) was **restricted to self-declared European ancestry
  for the genotyped SLCO1B1 replication analysis**: *"the rs4149056 and
  rs2306283 SNPs in SLCO1B1 were successfully genotyped in 16,664
  participants who had classified themselves as having European
  ancestry."*
- The population allele-frequency baseline the paper validated its own
  15% estimate against was itself European-only: *"consistent with the
  range of 0.14 to 0.22 reported previously among people of European
  ancestry."*

**This upgrades the finding from an inference to a confirmed fact.** It is
not merely that the discovery and replication cohorts happened to be
EUR-heavy by demographic accident — non-European ancestry was an explicit
exclusion criterion in the discovery analysis, and the replication
analysis was scoped to self-declared European ancestry only. Combined with
§3's real gnomAD result (EUR carries the *5 risk allele at the highest
frequency of the five tracked populations), this means the foundational
evidence for this specific PGx mechanism was generated using a design that
excluded the populations where the risk allele is least common — not an
accidental convenience sample that happened to skew that way, but a
deliberate ancestry restriction stated in the paper's own methods.

**What this still does not establish**, named as precisely as the primary
source allows: the 2008 SEARCH paper is the foundational GWAS discovery
paper for simvastatin specifically; it is not itself the CPIC 2021 statin
guideline (PMC9035072), which synthesizes many subsequent studies across
multiple statins including atorvastatin. Whether every one of *those*
later studies carried the same ancestry restriction has not been checked
in this pass — this document confirms the origin study's design, not the
full evidentiary chain CPIC's 2021 guideline ultimately drew on. That
remains a real, separate, checkable next step (see §6, item 2, now
partially answered rather than fully open).

## 6. Honest limitations, on the record

- **n=1 gene, n=1 allele.** This is SLCO1B1\*5 only. A single confirmed
  finding for one variant is not evidence of a general pattern across PGx
  variants — it would be a real overclaim to generalize "EUR-derived PGx
  evidence is systematically built on the population with the highest risk
  allele frequency" from this one case. That broader claim, if true, would
  be a significant one, but this document does not make it — see §7 for
  what would be required to check it properly.
- **gnomAD population labels (AFR/AMR/EAS/SAS/EUR) are broad continental
  groupings**, not fine-grained ancestry or ethnicity — the same
  granularity limitation every other gnomAD-based finding on this platform
  already carries (docs/02's own entity-resolution discussion of ambiguous
  population labels applies here too).
- **§5 confirms the 2008 discovery/replication design, not the complete
  evidentiary chain behind CPIC's 2021 multi-statin guideline** — see §5's
  own closing paragraph for the precise boundary of what was and was not
  checked.
- **No new PRR, no new FAERS query, no new biological claim was made.**
  This is a re-composition of an existing, tested capability
  (`compare_two_populations`) against real data it had simply never been
  run against before, plus one real primary-source literature check. Zero
  new network calls to any platform system, zero new GCP cost.

## 7. What a deeper research pass checked next, same session

### 7.1 [Closed] Does the EUR-maximum pattern hold across other CPIC-tier
### PGx genes, or is SLCO1B1 an isolated case?

Checked directly against the same pinned gnomAD artifact, same session,
for every gene it carries real population-frequency data for (11 genes:
CYP2B6, CYP2C19, CYP2C9, CYP2D6, CYP3A5, DPYD, G6PD, NAT2, SLCO1B1, TPMT,
VKORC1 — CYP1A2 has no rows in this artifact):

| Gene | Population maximum | EUR's rank among 4-5 populations |
|---|---|---|
| CYP2B6 | SAS | 4th of 5 |
| CYP2C19 | EAS | 4th of 5 |
| **CYP2C9** | **EUR** | **1st (max)** |
| CYP2D6 | EAS | 2nd of 5 |
| CYP3A5 | AFR | last of 4 (EUR lowest) |
| **DPYD** | **EUR** | **1st (max)** |
| G6PD | AFR | 4th of 5 |
| NAT2 | SAS | 2nd of 5 (close second) |
| **SLCO1B1** | **EUR** | **1st (max), this document's finding** |
| TPMT | AMR | 2nd of 5 (close second) |
| VKORC1 | EAS | 3rd of 4 |

**Answer: EUR is the population maximum in 3 of 11 genes (CYP2C9, DPYD,
SLCO1B1) — not a systematic pattern.** The other 8 genes have their
maximum risk-allele frequency in SAS (2), EAS (3), AFR (2), or AMR (1).
This is close to what would be expected if risk-allele frequency maxima
were distributed roughly independently across populations gene-by-gene —
consistent with genuinely independent evolutionary/demographic histories
at each locus (e.g. G6PD's well-known AFR/Mediterranean malaria-selection
signal; CYP2D6's well-known EAS enrichment; NAT2's well-known SAS/EUR
"slow acetylator" prevalence) — rather than evidence of a platform-wide or
field-wide EUR-ascertainment artifact.

**This materially narrows, not broadens, the claim this document can
honestly make.** The temptation, on finding one EUR-maximum gene
(SLCO1B1) immediately after finding a EUR-ancestry-restricted foundational
cohort for that same gene (§5), is to generalize into "PGx evidence is
systematically built on the population carrying the most risk allele."
The data directly available on this same platform refutes that
generalization: DPYD is also EUR-maximum but its foundational evidence
base (CPIC's DPYD guideline) is not similarly restricted to European
ancestry in the same documented way §5 established for SLCO1B1 — and 8 of
11 genes are not EUR-maximum at all. **The correct, narrower claim,
restated:** SLCO1B1 is a real, specific, primary-source-confirmed case
where the population carrying the highest risk-allele frequency also
happens to be the population whose ancestry the foundational discovery
and replication cohorts were explicitly restricted to. That combination —
not "EUR is usually the max," which this same check just showed is false
— is what makes SLCO1B1 worth naming. Whether DPYD's EUR-maximum status
reflects a similar cohort-restriction pattern or a coincidence has not
been checked and is named as an open item below, not assumed either way
from the allele-frequency data alone.

### 7.2 [Closed] DPYD's EUR-maximum status: coincidence, or the same
### pattern as SLCO1B1?

This was the single open item §7.1 flagged as most worth checking, because
it could have gone either way — confirming or refuting whether SLCO1B1's
pattern generalizes to at least one more case. Checked via primary
literature, not inferred from allele frequency alone.

**Real gnomAD numbers, re-verified precisely for this check:** the pooled
CPIC-actionable DPYD risk-allele frequency (\*2A + HapB3 + c.2846A>T) is
**0.000163 in EAS versus 0.031663 in EUR — a 194-fold depletion**, the
single largest population gap of any gene checked in §7.1's table. This
is not a modest difference; the CPIC-actionable variant set is close to
absent in this dataset's EAS sample (n=9,187).

**Real, independent clinical-outcome confirmation found**: Kanai et al.
2023, *"Poor association between dihydropyrimidine dehydrogenase (DPYD)
genotype and fluoropyrimidine-induced toxicity in an Asian population,"*
*Cancer Medicine* 12(7):7808-7814 (PMID 36524458, PMC10134304) — a real
GWAS cohort of 1,364 Japanese colorectal-cancer patients treated with
fluoropyrimidine chemotherapy. The paper's own abstract states the
premise it tests explicitly: *"DPYD genotype is closely associated with
fluoropyrimidine (FP)-induced toxicities in Caucasian population"* — named
by the authors themselves as a Caucasian-derived association being tested
for transfer to an Asian cohort. Their results, verbatim from the
abstract:

- Of the 82 CPIC-registered DPYD variants, 74 were genotyped in this
  cohort, but only 7 nonsynonymous CPIC variants were actually present.
- **None of the four recurrent, CPIC-guideline-actionable variants
  (\*2A, c.2846A>T, c.1679T>G, c.1236G>A/HapB3) were present in this
  cohort at all.**
- Of the 7 CPIC variants that were present, **none showed a significant
  correlation with fluoropyrimidine-related toxicity.**
- The authors' own conclusion: *"the DPYD genotype registered in CPIC
  plays a minor role in FP-related toxicities in an Asian population."*

**This is a stronger, more direct confirmation than SLCO1B1's own case.**
For SLCO1B1, §5 confirmed the *foundational cohort's design* excluded
non-European ancestry — a design fact, one step removed from a direct
demonstration that the association fails to transfer. For DPYD, an
independent, real clinical study directly tested the CPIC-actionable
variants in a non-European cohort and found both that the variants barely
occur there (consistent with, and now confirming outside gnomAD alone,
this platform's own 194x frequency gap) and that the association does not
hold where they do occur. Two independent lines of evidence — a
population-genetics frequency gap and a real clinical-outcome study —
converge on the same conclusion for DPYD.

**Answer to §7.1's open question**: DPYD's EUR-maximum status is not a
coincidental artifact unrelated to SLCO1B1's pattern — it is a second,
independently-confirmed real case of the same underlying issue (a
CPIC-actionable PGx association characterized in a population where the
risk variant is common, showing materially reduced applicability in a
population where it is rare-to-absent). This still does not establish
that EUR-maximum genes are *systematically* under-evidenced elsewhere
(n=2 of 11 genes checked with this level of rigor is not a general law),
but it does mean **the SLCO1B1 finding is not an isolated curiosity** —
of the 3 EUR-maximum genes this platform's data surfaced, at least 2
(SLCO1B1, DPYD) now have independent, real, checkable evidence of the same
generalizability concern. CYP2C9's own case has not yet been checked with
this same rigor — see the revised open items below.

### 7.3 [Closed] CYP2C9's own case — a real, but structurally different,
### third example

The natural next check named in the previous update: does CYP2C9, the
third EUR-maximum gene from §7.1's table, show the same generalizability
gap as SLCO1B1 and DPYD? Checked via primary literature, same discipline
as §5 and §7.2.

**Real gnomAD numbers, re-verified for this check:** CYP2C9's tracked
\*2/\*3 risk alleles are at 0.0346 (AFR) and 0.0341 (EAS) — nearly tied at
the bottom, both ~5.7x lower than EUR's 0.1960. This matches §7.1's
finding that EUR is the population maximum for this gene.

**Real, primary-source confirmation found**, and it directly matches the
frequency pattern: Perera et al. 2013, *"Genetic variants associated with
warfarin dose in African-American individuals: a genome-wide association
study,"* *Lancet* 382(9894):790-796 (PMID 23755828) — states as
established background, in its own abstract: *"VKORC1 and CYP2C9 are
important contributors to warfarin dose variability, but explain less
variability for individuals of African descent than for those of
European or Asian descent."* This is a direct, primary-source statement
of the same reduced-applicability pattern found for SLCO1B1 and DPYD, in
the population (AFR) where the platform's own gnomAD data shows the
lowest \*2/\*3 frequency.

**Where CYP2C9's case is genuinely different from SLCO1B1's and DPYD's —
important not to flatten this into an identical story:** for SLCO1B1 and
DPYD, the documented response was a demonstrated *reduced applicability*
with no described population-specific remedy found in this pass. For
CYP2C9/warfarin, the same 2013 Perera et al. paper's own actual
contribution was to **go looking for, and find, a real, independent,
African-ancestry-specific genetic marker that recovers predictive
power**: a novel SNP (rs12777823, in the CYP2C gene cluster but distinct
from CYP2C9\*2/\*3) that improved warfarin dose-variability explained by
21% (relative) in African-American patients specifically, independent of
\*2/\*3. A separate, well-established third marker — **CYP2C9\*5** —
exists specifically because it is *"found almost exclusively in
populations of African ancestry"* (per a separate real source, PMID
35108398), with its own dedicated clinical dosing literature.

**Neither rs12777823 nor CYP2C9\*5 is present anywhere in this platform's
own pinned gnomAD artifact for CYP2C9** — verified by direct inspection:
the only contributing alleles tracked for CYP2C9 in every population row
are \*2 and \*3. This means the platform's own CYP2C9 population-frequency
comparison is not merely showing a generalizability gap the field has
not addressed (as with SLCO1B1/DPYD) — it is missing markers the field
*has* already found and validated specifically to close a
population-specific gap. **Checked before treating this as a quick fix**:
this is not a gap this platform's own code (a lookup table, a mapping
dict) could close by itself — the pinned artifact file is the actual
upstream source of the gap, and re-deriving it with \*5 included from
gnomAD directly is a materially larger task than the SLCO1B1/DPYD
findings required. Still a real, concrete, more specific gap than the
other two cases' "the literature hasn't solved this yet" — but "more
concrete" is not the same as "quick," and this document does not overstate
which.

**Answer to the open question**: CYP2C9 is a real third case of a
EUR-maximum gene with documented reduced non-EUR applicability — but
structurally distinct from SLCO1B1 and DPYD. All three genes are
EUR-maximum by this platform's own gnomAD data and all three have real,
independent primary-source confirmation of the underlying concern. But
CYP2C9's specific manifestation (population-specific rescue markers
existing but untracked) is a more concrete, more directly actionable gap
than the other two, where no comparable rescue marker was found in this
pass.

### 7.4 Still open

1. **[Closed, see §7.2]** DPYD's EUR-maximum status — confirmed as a
   second real case, not a coincidence.
2. **[Closed, see §7.3]** CYP2C9's own case — confirmed as a third real
   case, structurally different (a documented, field-validated rescue
   marker exists but is untracked by this platform) rather than an
   unaddressed gap.
3. **New item from §7.3, verified before finalizing — not as fixable as
   first assumed**: the natural next step was to add CYP2C9\*5 to this
   platform's gnomAD-derived CYP2C9 population comparison. Checked before
   claiming this as an actionable fix: **CYP2C9\*5 is not present anywhere
   in the pinned gnomAD v2.1.1 artifact** (`anukriti-swarm/datasets/
   pharmfreq/gnomad_v2_1_1_frequencies.jsonl`) — verified by direct
   inspection; the file's only CYP2C9 rows are \*2 and \*3, in every
   population. This is not a config/mapping-table gap this platform's own
   code could close (unlike, say, a `mechanistic_prior.py` table edit) —
   it is an upstream data-artifact gap: the pinned file itself would need
   to be re-derived from gnomAD with \*5 included, a materially bigger
   task than adding a row to a lookup table. Named honestly as a real,
   but harder-than-first-assumed, next step — not silently downgraded to
   "easy" after finding out otherwise.
4. **[Partially closed, see §5]** Whether the *later* studies CPIC's 2021
   multi-statin guideline (PMC9035072) relies on for atorvastatin
   specifically carried the same European-ancestry restriction as the 2008
   SEARCH discovery/replication cohorts, or whether more recent, more
   diverse cohorts (e.g. PMC9303592, the real-world-care study cited in the
   human review) have begun to close this gap. Not checked in this pass.
5. **Extend the population comparison to CYP2C19 and CYP2C9's other
   drug pairs** for completeness — CYP2C19/omeprazole (refused on signal
   grounds, allele-enriched in SAS at 2.22x, and per §7.1's table EAS is
   actually the true maximum, not EUR or SAS) and CYP2C9/ibuprofen
   (mechanism not rejected the way aspirin's was).
6. **A real, checkable pattern is now emerging across all 3 of the
   EUR-maximum genes** — worth stating plainly as a hypothesis for future
   verification, not yet a conclusion: PGx associations discovered in
   ancestry-restricted or ancestry-skewed European cohorts appear to
   correlate with real, independently-confirmed reduced applicability in
   populations where the relevant risk allele is rare. This is currently
   n=3 (SLCO1B1, DPYD, CYP2C9) with real primary-source support for each
   — every EUR-maximum gene this platform's own audit found now has an
   independently-confirmed generalizability concern. This is still not
   evidence that non-EUR-maximum genes are exempt from similar concerns
   (they were not checked with this rigor) — it is evidence that, for this
   specific pattern (EUR-maximum + real applicability gap), 3 real,
   independent checks have now all confirmed rather than refuted it.

## 8. Reproduction

```bash
cd project_astra
python3 scripts/extend_population_comparison_afr_amr_eas.py
python3 -m pytest tests/test_extend_population_comparison_afr_amr_eas.py -v
python3 -m pytest -q   # 497 passed
ruff check astra scripts tests   # All checks passed
```
