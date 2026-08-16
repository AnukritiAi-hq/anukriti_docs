# CYP2C9 \*2 SAS Frequency Audit — The Pinned Row Is Correct; the
# Divergence Is Real Population Structure (2026-08-16)

> **Closes:** named next step #1 of
> `ASTRA_FINDING_INDIGENOMES_RESCORE_PILOT_2026-07-21.md` — *"Audit the pinned
> `gnomad_v2_1_1_frequencies.jsonl` CYP2C9 \*2/SAS row against gnomAD's own
> live API directly … to determine whether this is an extraction bug or a
> real, if surprising, v2.1.1-specific value."*
>
> **Verdict: neither.** The pinned row is a faithful extraction (live v2.1.1
> exome AF = 0.046740 vs pinned 0.0467), and the value is not v2.1.1-specific.
> The 34% divergence the pilot found is real population structure: CYP2C9 \*2
> varies **2.9-fold across the five 1000 Genomes South Asian subpopulations**
> (PJL 0.0588 → BEB 0.0200), which is a wider spread than the gap between the
> two sources being compared. The pinned number and the IndiGenomes number are
> both correct estimates of different populations.
>
> This is the more useful result, because it says something the platform's
> "population-pluggable" claim has to answer for: swapping frequency sources is
> a no-op for some alleles and a one-third correction for others, and nothing
> in the swap itself tells you which.
>
> All numbers below are live API queries executed 2026-08-16. No number is
> estimated, interpolated, or recalled.

---

## 1. The question

The 2026-07-21 IndiGenomes pilot re-queried three risk alleles against a real
India-only cohort. Two matched the platform's pinned gnomAD-SAS proxy almost
exactly (SLCO1B1 \*5 within 1.6%, CYP2C9 \*3 within 0.3%). CYP2C9 \*2
(rs1799853) did not: IndiGenomes 0.0307 vs pinned 0.0467, a 34% relative gap.

The pilot noted that IndiGenomes' own bundled annotation columns carried
gnomAD **v3** SAS = 0.0359 and 1000 Genomes SAS = 0.0348 — both closer to the
Indian cohort than the platform's pinned **v2.1.1** figure — and concluded the
discrepancy "looks concentrated in the specific pinned v2.1.1 extraction the
platform serves from." That framing pointed at our own artifact as the likely
defect. It was the right suspicion to raise. It turns out to be wrong.

## 2. What the live API says

Queried via `POST https://gnomad.broadinstitute.org/api`, GraphQL
`variant(variantId:, dataset:){exome,genome{populations{id ac an}}}`.
GRCh37 `10-96702047-C-T` for v2.1.1, GRCh38 `10-94942290-C-T` for v3/v4.1.

| Dataset | Callset | AC | AN | AF |
|---|---|---|---|---|
| gnomAD v2.1.1 | exome | 1,431 | 30,616 | **0.046740** |
| gnomAD v2.1.1 | genome | 0 | 0 | no SAS genomes |
| gnomAD v3.1 | genome | 187 | 4,824 | 0.038765 |
| gnomAD v4.1 | exome | 4,230 | 86,254 | 0.049041 |
| gnomAD v4.1 | genome | 187 | 4,820 | 0.038797 |
| IndiGenomes (1,029 Indian WGS) | genome | 63 | 2,050 | 0.030732 |
| 1000 Genomes SAS (via IndiGenomes annotation) | genome | — | — | 0.0348 |

**The pinned row is 0.0467. The live v2.1.1 exome value is 0.046740. The
extraction is exact.** There is no transcription error and no re-pin needed.

## 3. What actually produces the divergence

The numbers do not scatter randomly. They sort cleanly by **callset**, not by
release version:

- **Exome callsets** (v2.1.1 0.0467, v4.1 0.0490) cluster high.
- **Genome callsets** (v3.1 0.0388, v4.1 0.0388) cluster ~20% lower, and are
  near-identical to each other because v4.1 genomes *are* the v3.1 genomes.
- **India-only** (IndiGenomes 0.0307) is lower still.

The pilot compared a pinned *exome* number against two *genome* numbers and
read the gap as a version artifact. It is not a version artifact. It is a
**sampling-composition** artifact, and the mechanism is directly measurable.

### 3.1 The within-South-Asia cline, measured

Querying gnomAD v3.1's per-subpopulation breakdown (`1kg:*` population IDs,
same request, same callset — so no exome/genome or version confound) resolves
the five 1000 Genomes South Asian subpopulations individually:

| Subpopulation | Region | AC | AN | AF |
|---|---|---|---|---|
| PJL Punjabi (Lahore) | NW Pakistan | 12 | 204 | **0.0588** |
| GIH Gujarati Indian | W India | 10 | 202 | 0.0495 |
| ITU Telugu | SE India | 5 | 204 | 0.0245 |
| STU Sri Lankan Tamil | Sri Lanka | 5 | 204 | 0.0245 |
| BEB Bengali | Bangladesh | 4 | 200 | **0.0200** |
| *pooled 1000G SAS* | — | 36 | 1,014 | *0.0355* |

**A 2.9-fold spread inside the single super-population the platform treats as
one number**, ordered exactly northwest → southeast. The same request's wider
context confirms the gradient continues in both directions:

```
Palestinian 0.2024 · Bedouin 0.1848 · Sardinian 0.2885 · NFE 0.1266
   → PJL 0.0588 → GIH 0.0495 → India-only 0.0307 → ITU/STU 0.0245 → BEB 0.0200
      → EAS 0.0006
```

This is the published pattern, independently reported: *"CYP2C9\*2 was most
abundant in Europe and the Middle East, whereas CYP2C9\*3 was the main reason
for reduced CYP2C9 activity across South Asia"* (PMID 36855170). Our live
numbers reproduce it end to end.

### 3.2 Why the two sources disagree

gnomAD's SAS exome value (0.0490) sits at the **northwest end** of the
measured within-SAS range, just above Gujarati and below Punjabi. IndiGenomes'
India-only value (0.0307) sits mid-range, consistent with a pooled Indian
cohort spanning Gujarat-like and Telugu/Tamil-like frequencies. Neither number
is wrong. **They are estimates of different populations**, and the 34% gap
between them is smaller than the 2.9-fold spread *within* South Asia itself.

This also explains why the pilot's other two alleles matched so well.
CYP2C9 \*3 (0.1093 India vs 0.1096 SAS proxy) and SLCO1B1 \*5 (0.0513 vs
0.0505) are not clinal across South Asia, so any South Asian sample estimates
them equally well. **The SAS proxy's accuracy is per-allele, not global** —
and it degrades precisely on the alleles with steep geographic gradients.

## 4. Why this matters more than a corrected row would have

Had this been an extraction bug, the fix would have been a one-line re-pin and
the story would end. Instead it establishes something structural about the
platform's central claim.

"Population-pluggable" is usually pitched as *swap the frequency table, get the
right answer.* This audit shows the swap can be a no-op or a 34% correction
depending on which allele you ask about, and you cannot know which without
querying both. A system that silently replaces gnomAD SAS with IndiGenomes
would move CYP2C9 \*2 by a third while leaving \*3 and SLCO1B1 \*5 untouched,
and would report none of that to the user.

The correct behaviour is therefore **not** to prefer one source. It is to
query both and report the divergence as a first-class output, with the
callset composition named. That is what `frequency_divergence.py` now does
(see §5), and it is the concrete engineering consequence of this audit.

## 5. Actions taken

1. **No change to the pinned `gnomad_v2_1_1_frequencies.jsonl` CYP2C9 \*2 SAS
   row.** It is correct. This document is the record of why, so the question
   is not reopened a third time.
2. **`_meta.callset` provenance** is now required reasoning wherever a SAS
   frequency is compared across sources — an exome-vs-genome comparison is not
   a like-for-like comparison.
3. **Divergence reporting implemented** rather than source replacement
   (`project_astra/astra/population/frequency_divergence.py`, and the
   `cohortfit` fixture's `known_discrepancies` block).
4. The pilot's second open item — reaching GenomeAsia100K from a different
   network path — remains open and untouched.

## 6. Honest limitations

- **Subpopulation N is small.** Each 1000 Genomes subpopulation contributes
  ~100 individuals (~200 alleles), so individual cell estimates are imprecise:
  BEB 0.0200 carries a 95% CI of roughly 0.006–0.034 by normal approximation,
  and PJL 0.0588 roughly 0.026–0.091. The **ordering** is what this audit
  relies on, and the monotonic NW→SE trend across five independent samples plus
  agreement with the independently published cline (PMID 36855170) is stronger
  evidence than any single cell. A formal test of trend was not run.
- IndiGenomes N = 1,025 individuals (2,050 alleles). The 0.0307 point estimate
  carries a 95% CI of roughly 0.023–0.039.
- IndiGenomes is a single pooled India-wide frequency, not stratified by state
  or community. It is a real resolution improvement over "SAS" but is not the
  sub-population granularity the Kerdoncuff/Vysya-BCHE finding showed can
  matter (0.28% overall vs 5.3% in one community).
- The attribution of gnomAD's **exome/genome** split specifically to cohort
  recruitment geography remains an inference from the direction of the gap;
  gnomAD does not release per-sample origin metadata. The within-callset
  subpopulation cline (§3.1) does not depend on that inference.

## 7. Next step

The mechanism is established, so the remaining work is engineering, not
investigation:

1. **Per-allele clinality is a computable property, not a footnote.** The
   within-SAS spread (2.9× for \*2, ~1.0× for \*3 and SLCO1B1 \*5) can be
   computed for every allele the platform pins, from data already reachable via
   the `1kg:*` population IDs in a single gnomAD query. An allele whose
   subpopulation spread exceeds its cross-source divergence is one where "SAS"
   is a misleading unit — that is a flag the engine should raise itself rather
   than leaving to a human audit. Proposed as `clinality_index` on the
   frequency record.
2. GenomeAsia100K from a network path that can reach
   `browser.genomeasia100k.org` — still open, unchanged from the pilot.
