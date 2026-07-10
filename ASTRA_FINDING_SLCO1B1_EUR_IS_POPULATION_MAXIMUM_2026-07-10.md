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

## 5. Honest limitations, on the record

- **n=1 gene, n=1 allele.** This is SLCO1B1\*5 only. A single confirmed
  finding for one variant is not evidence of a general pattern across PGx
  variants — it would be a real overclaim to generalize "EUR-derived PGx
  evidence is systematically built on the population with the highest risk
  allele frequency" from this one case. That broader claim, if true, would
  be a significant one, but this document does not make it — see §6 for
  what would be required to check it properly.
- **gnomAD population labels (AFR/AMR/EAS/SAS/EUR) are broad continental
  groupings**, not fine-grained ancestry or ethnicity — the same
  granularity limitation every other gnomAD-based finding on this platform
  already carries (docs/02's own entity-resolution discussion of ambiguous
  population labels applies here too).
- **This does not check whether CPIC's foundational cohorts (SEARCH trial
  and successors) were literally EUR-predominant** — that is a real,
  separate, checkable historical-cohort-composition question this document
  does not attempt to answer; it infers plausibility from the allele
  frequency pattern and general knowledge of the field's history, not from
  auditing the SEARCH trial's actual reported ancestry composition. Named
  as a real gap, not smoothed over.
- **No new PRR, no new FAERS query, no new biological claim was made.**
  This is a re-composition of an existing, tested capability
  (`compare_two_populations`) against real data it had simply never been
  run against before. Zero new network calls, zero new GCP cost.

## 6. What a deeper research pass would need to check next

Presented as concrete, checkable next steps, not vague future work:

1. **Does the same EUR-maximum pattern hold for other CPIC-tier PGx
   variants the platform already has gnomAD data for** (CYP2C9\*2/\*3,
   CYP2C19\*2/\*3, CYP2D6 alleles)? If EUR is *not* the maximum for most
   other variants, this SLCO1B1 finding is a real but isolated curiosity.
   If EUR *is* disproportionately often the maximum across several
   independent PGx variants, that would be a genuinely stronger, more
   general finding worth its own careful write-up — but this has not been
   checked and should not be assumed either way.
2. **Audit the actual ancestry composition of the CPIC statin guideline's
   cited foundational studies** (the 2008 SEARCH GWAS and the papers PCIC's
   2021 guideline itself cites) directly, rather than inferring cohort
   composition from allele frequency alone. This is a literature-audit
   task, not a code task.
3. **Extend this same comparison to the two other genes/pairs this
   platform's mechanistic-prior table cites** for completeness, even though
   their mechanisms were not the ones triggering this specific finding —
   CYP2C19 (omeprazole, refused on signal grounds but allele-enriched in
   SAS at 2.22x — worth knowing its AFR/AMR/EAS picture too) and CYP2C9
   (ibuprofen — mechanism not rejected the way aspirin's was; ibuprofen sits
   in CPIC's recommendation tier, unlike aspirin).

## 7. Reproduction

```bash
cd project_astra
python3 scripts/extend_population_comparison_afr_amr_eas.py
python3 -m pytest tests/test_extend_population_comparison_afr_amr_eas.py -v
python3 -m pytest -q   # 497 passed
ruff check astra scripts tests   # All checks passed
```
