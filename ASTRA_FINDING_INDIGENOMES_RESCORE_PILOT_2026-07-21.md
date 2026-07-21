# ASTRA Finding: IndiGenomes Re-Score Pilot — SAS Proxy Holds for 2/3 Risk
# Alleles, Real 34% Discrepancy Found on CYP2C9 *2 (2026-07-21)

> **Scope:** direct follow-up to `project_astra/docs/18-research-discovery-
> context-2026-07-21.md`'s named next step #1 — re-score the platform's
> existing discovery candidates (docs/17) against an India-specific
> frequency source instead of the pinned gnomAD-SAS proxy. Real data only;
> no numbers in this document are estimated or interpolated.
>
> **Repo:** `project_astra`. Script:
> `scripts/query_indigenomes_for_candidate_risk_alleles.py`. Test:
> `tests/test_query_indigenomes_for_candidate_risk_alleles.py` (5 passed).

---

## 1. What was queried, and how

The two candidates in `docs/17-discovery-candidates-2026-07-08.md`
(CYP2C9↔aspirin, SLCO1B1↔atorvastatin) rest on three risk alleles the
platform's pinned `gnomad_v2_1_1_frequencies.jsonl` artifact tracks:
CYP2C9 \*2 (rs1799853), CYP2C9 \*3 (rs1057910), SLCO1B1 \*5 (rs4149056).
This pilot re-queried each against **IndiGenomes** (CSIR-IGIB/CCMB, 1029
Indian genomes, PMID 33095885) — a real, India-only cohort, finer-grained
than gnomAD's pooled "SAS" super-population (which spans India, Pakistan,
Bangladesh, Sri Lanka, Nepal).

**IndiGenomes has no documented public API.** The real endpoint was found
by fetching the site's own AngularJS controller (`js/angularHtml.js`) and
reading its `$http` call directly, not by guessing:

```
POST https://clingen.igib.res.in/indigen/data.php
Content-Type: application/x-www-form-urlencoded
Body: {"Name": "<rsid>"}          # JSON string, despite the header
```

All three rsIDs resolved to real records with genuine cohort-level
AC/AN/AF (`Info` field, e.g. `AC=105;AF=0.051;AN=2048;...`), confirmed by
direct `curl` POST, 2026-07-21.

**GenomeAsia100K was also attempted and is not reachable from this
environment.** `curl -v https://browser.genomeasia100k.org/` resolves DNS
(182.71.223.36) but every connection attempt on :443 times out (confirmed
twice, 20s timeout each; the in-session browser tool's own fetch failed
with `ECONNREFUSED` against the same host). Named as a network refusal,
not a claim that GenomeAsia100K's own service is down — re-attempt from a
different network path before concluding anything further about it.

---

## 2. The real numbers

| Allele | rsID | IndiGenomes real AF (AC/AN) | Pinned gnomAD v2.1.1 SAS | Relative difference |
|---|---|---|---|---|
| SLCO1B1 \*5 | rs4149056 | 0.0513 (105/2048) | 0.0505 | **1.6%** |
| CYP2C9 \*3 | rs1057910 | 0.1093 (224/2050) | 0.1096 | **0.3%** |
| CYP2C9 \*2 | rs1799853 | 0.0307 (63/2050) | 0.0467 | **34.2%** |

Two of three risk alleles are **near-identical** between the real Indian
cohort and the platform's pinned SAS proxy — a genuine, real confirmation
that the SAS proxy is not badly wrong for SLCO1B1↔atorvastatin (the
MODERATE-tier candidate) or for CYP2C9 \*3.

**CYP2C9 \*2 shows a real, non-trivial discrepancy.** The pinned gnomAD
v2.1.1 SAS figure (0.0467) is 52% higher than the real IndiGenomes value
(0.0307). This is not explained away by "SAS is a coarser grouping than
India-only": IndiGenomes' own bundled annotation columns for this exact
variant carry gnomAD **v3** SAS = 0.0359 and 1000 Genomes SAS = 0.0348 —
both already closer to the real Indian cohort than the platform's pinned
**v2.1.1** figure. The discrepancy looks concentrated in the specific
pinned v2.1.1 extraction the platform serves from, not in a genuine
population-granularity difference.

---

## 3. What this does and does not change

- **Does not change either human-reviewed evidence tier.** CYP2C9↔aspirin
  was ruled INSUFFICIENT on mechanism-plausibility grounds (CPIC issues no
  aspirin-specific recommendation; aspirin's GI-bleed mechanism is COX-1
  acetylation, independent of CYP2C9) — a frequency correction on CYP2C9
  \*2 does not touch that verdict. SLCO1B1↔atorvastatin's MODERATE tier is,
  if anything, reinforced: its one supporting risk allele (SLCO1B1 \*5) is
  the one that checks out cleanly against real Indian-cohort data.
- **Does open a real, separate, checkable question**: is the platform's
  pinned `gnomad_v2_1_1_frequencies.jsonl` artifact's CYP2C9 \*2 SAS row
  accurate? Three independent sources (IndiGenomes real cohort, gnomAD v3,
  1000 Genomes) now converge on ~0.031–0.036, all below the pinned
  artifact's 0.0467. Not investigated further by this pilot — a
  re-extraction or re-pin audit of that one row is the concrete next step,
  in the same spirit as the CYP2C9 F-10 phenotype-table fix already on
  record for `anukriti-pgx-core`.

---

## 4. Honest limitations

- IndiGenomes N (~1024–1025 individuals) is far smaller than gnomAD's SAS
  grouping. A 34% discrepancy at this sample size is suggestive on its
  own; the convergence with gnomAD-v3-SAS and 1000G-SAS independently
  (both smaller-N sources than gnomAD v2.1.1 SAS too, yet agreeing with
  each other and with IndiGenomes) is what makes "pinned-artifact issue"
  the more likely read than sampling noise — not proof.
- IndiGenomes is a single pooled India-wide frequency, not stratified by
  state/community. This is a real resolution improvement over "SAS" but
  is not the sub-population granularity the Kerdoncuff/Vysya-BCHE finding
  showed can matter (0.28% overall vs. 5.3% in one specific community).
- This pilot did not modify `population_signal.py`, `scoring.py`, or any
  stored `ScoredCandidate` — it is evidence for a human decision on
  whether to (a) add IndiGenomes as a second, queryable frequency source
  and (b) audit the pinned gnomAD v2.1.1 artifact's CYP2C9 \*2 row,
  consistent with `validation_gate.py`'s "no automatic pass/fail logic"
  discipline.

## Next step

Two concrete, scoped follow-ups, neither started:

1. Audit the pinned `gnomad_v2_1_1_frequencies.jsonl` CYP2C9 \*2/SAS row
   against gnomAD's own live API directly (the same live-query pattern
   `query_gnomad_for_g6pd_eas_variants.py` already established) to
   determine whether this is an extraction bug or a real, if surprising,
   v2.1.1-specific value.
2. Re-attempt GenomeAsia100K from a network path that can actually reach
   `browser.genomeasia100k.org` — this pilot's refusal is a real network
   constraint of this session's environment, not evidence about
   GenomeAsia100K itself.
