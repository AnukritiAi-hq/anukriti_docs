# ASTRA Finding: G6PD's Pinned gnomAD Artifact Tracks Zero East/Southeast
# Asian-Relevant Variants — A Real Data-Completeness Gap, Not a
# Transferability Nuance (2026-07-10)

> **Scope:** this document reports a structurally different, and more
> directly actionable, finding than the session's three prior confirmed
> cases (SLCO1B1, DPYD, CYP2C9) and its one negative result (CYP3A5). Those
> four were all about whether an evidence base *transfers* well to a
> population where a *tracked* variant is rare. This finding is upstream
> of that question entirely: for G6PD, the platform's pinned gnomAD
> artifact does not track the variants that are actually clinically
> relevant in East/Southeast Asian populations at all — it tracks two
> variants (A-, Mediterranean) that happen to be genuinely rare there,
> while the real, well-documented, clinically significant EAS-prevalent
> G6PD variants (Canton, Kaiping, Mahidol, and others) are absent from the
> dataset entirely, in every population row. This produces a real, checkable
> false-negative risk for any consumer of this platform's G6PD population
> data, and one such consumer already exists in this codebase today.
>
> **Repo:** `project_astra`. This finding required no new code to surface —
> it was found by direct inspection of the already-pinned gnomAD artifact
> and the already-existing `mechanistic_prior.py` G6PD/rasburicase entry.
> A regression test locking in the exact tracked-allele gap is added as
> part of this same commit.

---

## 1. How this was found

Following up on the CYP3A5 mirror-image negative result's own named next
steps, this session checked G6PD — a real, well-known pharmacogene (drug-
induced hemolysis risk for primaquine/tafenoquine antimalarial therapy and
rasburicase, both CPIC-guideline-actionable) with an extreme AFR-max/
EAS-min ratio in this platform's own gnomAD data (§1 of the companion
mirror-image document: AFR 0.116, EAS ≈0.000, an effectively infinite
ratio).

**The literature check immediately surfaced something that did not match
the platform's own numbers.** A real, independent, geostatistical
prevalence-mapping study (PLOS Medicine, *"G6PD Deficiency Prevalence and
Estimates of Affected Populations in Malaria Endemic Countries"*) states
that **the majority (67.5%, median estimate) of G6PD-deficient individuals
globally are from Asian countries**, not Africa — directly contradicting
what a naive reading of this platform's own "EAS≈0" number would suggest.
This prompted checking *which specific G6PD variants* are actually
prevalent in East/Southeast Asia, rather than assuming the platform's
tracked allele set was complete.

## 2. What the platform's pinned artifact actually tracks — verified by
## direct inspection

```
G6PD A-            AFR: 0.115672   AMR: 0.004011   EAS: 0.0        SAS: 0.000367   EUR: 0.000183
G6PD Mediterranean AFR: 0.000228   AMR: 0.0        EAS: 0.0        SAS: 0.017350   EUR: 0.000770
```

**Exactly two G6PD variants are tracked, in every population row, with no
others present anywhere in the file**: `A-` (the well-known sub-Saharan
African-prevalent variant) and `Mediterranean` (prevalent in the
Mediterranean basin, Middle East, and parts of South Asia — consistent
with its non-zero SAS frequency above). Both are real, well-established
G6PD-deficiency-causing variants. Neither is expected to be common in East
or Southeast Asia, and the data correctly shows they are not (EAS = 0.0
for both) — **the zero itself is not wrong**. The problem is what a reader
would reasonably but incorrectly infer from it.

## 3. What is missing — verified against real, independent literature

A real, well-documented set of G6PD-deficiency-causing variants is
specific to, or heavily concentrated in, East and Southeast Asian
populations and is **absent from this platform's tracked set entirely**:

| Variant | Documented prevalence | Source |
|---|---|---|
| G6PD Canton (c.1376G>T) | ~42% of G6PD-deficient alleles in a Malaysian Chinese neonate cohort; "most common" variant, >63% combined with Kaiping, in a 1,756-case Guangdong Province, China cohort | PMID 16329560, PMID 30077011 |
| G6PD Kaiping (c.1388G>A) | ~39% of the same Malaysian Chinese cohort; second-most-common in the Guangdong cohort | PMID 16329560, PMID 30077011 |
| G6PD Mahidol (c.487G>A) | The dominant variant in Southeast Asia specifically; independently confirmed under recent positive selection (malaria resistance) over the past ~1,500 years in Southeast Asian populations | PMID 20007901 |
| G6PD Gaohe, Viangchan, Chinese-5, and others | Each independently documented as recurrent, real, named variants across multiple Chinese/Southeast Asian cohort studies | PMID 17018380, PMID 11499668 |

**These are not obscure or marginal variants.** In the Guangdong cohort
alone (a real, published, 1,756-case series), Canton and Kaiping together
account for **more than 63% of all G6PD-deficient individuals studied** —
a higher single-cohort concentration than either A- or Mediterranean's own
role in their respective best-characterized populations. This is not a
case of the platform tracking the "main" variant and missing minor,
rare ones — it is tracking zero of the variants that actually explain the
majority of G6PD deficiency in a population this platform's own data
implies has none.

## 4. Why this is a different, more concrete class of finding than
## SLCO1B1/DPYD/CYP2C9

Those three findings were about **evidentiary transferability**: real
foundational research existed, characterized a real mechanism, in a
population where the tracked variant happens to be common, and that
mechanism (or its exact clinical utility) was independently shown to
transfer poorly elsewhere. The variant itself was correctly and
completely represented in the data; the *clinical conclusion* was what
didn't generalize.

**This G6PD finding is different in kind: the data itself is
incomplete for the population in question, not merely non-generalizing.**
A researcher or downstream tool reading this platform's G6PD/EAS number
would not conclude "the evidence doesn't transfer to EAS" — they would
likely conclude **"G6PD deficiency is rare/absent in EAS,"** which is
false. Real G6PD deficiency prevalence in parts of Southeast Asia and
southern China is substantial (the PLOS Medicine estimate above; the
cohort studies cited report meaningful case counts in single hospital
systems) — it is simply carried by different, untracked variants.

## 5. This has a real, live downstream consumer today — not a
## hypothetical risk

Checked directly against the codebase: `astra/discovery_engine/
mechanistic_prior.py` already contains a real, existing entry:

```python
("G6PD", "RASBURICASE"): (
    MechanismClass.TARGET,
    "CPIC:rasburicase-G6PD",
    "recombinant_enzyme",
),
```

This is the platform's real, CPIC-cited mechanistic prior for
rasburicase-induced hemolysis risk in G6PD-deficient patients — the exact
clinical scenario CPIC's own guideline addresses (Relling et al., PMID
24787449: *"Rasburicase is contraindicated in G6PD-deficient patients due
to the risk of AHA [acute hemolytic anemia]..."*). If this entry were ever
composed with this platform's own G6PD gnomAD population data (following
the same `compare_two_populations` pattern already used for SLCO1B1,
CYP2C9, and every other gene in this session), **the resulting EAS
fold-enrichment would read as ≈0 or undefined (division by zero, per
`compare_two_populations`'s own `REFUSAL_REASON_ZERO_EUR_FREQUENCY`-style
handling) — not because G6PD deficiency is actually rare in East Asian
rasburicase recipients, but because the platform is not tracking the
variants that would show otherwise.** This is a real, structural risk to
any future composition of this specific mechanistic-prior entry with
population data, named now before such a composition is built, not after.

## 6. What this does and does not mean

**Does not mean:**
- This is not a claim that gnomAD itself lacks this data. gnomAD v2.1.1
  almost certainly has *some* East/Southeast Asian G6PD variant coverage
  in its full dataset — this finding is about what was carried into this
  platform's own **pinned, extracted artifact** (`anukriti-swarm/
  datasets/pharmfreq/gnomad_v2_1_1_frequencies.jsonl`), not gnomAD's
  underlying completeness. Whether Canton/Kaiping/Mahidol are present in
  gnomAD's raw data and simply were not selected during this artifact's
  original extraction, versus genuinely absent from gnomAD's own variant
  catalog, was not checked in this pass — a real, concrete next step (see
  §7).
- This is not a claim that any of this session's other findings (SLCO1B1,
  DPYD, CYP2C9, CYP3A5) have the same kind of gap — each of those was
  checked and the tracked variant *is* the clinically relevant one for the
  comparison being made; only G6PD was found to have this specific,
  different failure mode.

**Does mean:**
- Any current or future use of this platform's G6PD population-frequency
  data for East or Southeast Asian populations should be treated as
  **uninformative, not as evidence of low risk** — a "named refusal,
  never a confident wrong answer" case, matching this platform's own
  house discipline (`resolve/`'s "never auto-write unresolved" rule,
  applied here to a data-completeness problem rather than an entity-
  resolution one).
- This is a concrete, scoped, and verifiable data-engineering task for a
  future session: identify whether Canton/Kaiping/Mahidol (and other
  EAS-prevalent variants) exist in gnomAD's own v2.1.1 release, and if so,
  add them to the pinned artifact using the same extraction process that
  produced the existing rows.

## 7. What a further pass should check next

1. **Check gnomAD v2.1.1's own public data directly** (not this
   platform's extracted artifact) for Canton (rs72554664), Kaiping
   (rs72554665), and Mahidol (rs137852328) frequency data in the EAS
   population. If present, this becomes a concrete, scoped data-pipeline
   fix (re-extract with these variants included) rather than a
   fundamental gnomAD limitation. Not checked in this pass — named as the
   literal next action, not vague future work.
2. **Audit every other gene in the pinned artifact for the same failure
   mode** — this session checked G6PD because its extreme AFR/EAS ratio
   made the omission suspicious enough to investigate, but the same
   "tracks the wrong variant for a given population" problem could
   exist, undetected, in any of the other 10 genes. A systematic check
   (comparing this platform's tracked allele lists against each gene's
   own CPIC/PharmGKB-documented population-relevant variant list) would
   be more rigorous than the case-by-case discovery this session used.
3. **If/when this platform ever composes the G6PD/rasburicase
   mechanistic prior with real population data** (following the
   SLCO1B1/CYP2C9 composition pattern), that composition script should
   explicitly check for and refuse on this named gap, not silently
   report a near-zero EAS fold-enrichment as if it were a real finding.

## 8. Honest limitations, on the record

- **Whether Canton/Kaiping/Mahidol exist in gnomAD v2.1.1's own release
  was not directly verified against gnomAD itself in this pass** — the
  claim is that they are absent from this platform's *extracted, pinned*
  artifact, verified by direct inspection of the actual file; whether the
  root cause is an extraction-time omission or a genuine gnomAd v2.1.1
  coverage gap is the open question named in §7, item 1.
- **This document's frequency claims for Canton/Kaiping/Mahidol come from
  clinical cohort studies (hospital-based case series in China/Malaysia),
  not from gnomAD population-frequency data directly** — cohort-based
  variant-share-among-cases percentages (e.g. "63% of deficient
  individuals") are a different statistic from a population-wide allele
  frequency, and should not be conflated with one. Named precisely to
  avoid the exact category error this session's own SLCO1B1/DPYD
  documents have been careful to avoid elsewhere (disproportionality vs.
  population frequency vs. cohort composition are three different
  numbers).
- **No new PRR, no new FAERS query was computed.** This is a literature
  and data-artifact audit, zero new network calls to any platform system,
  zero new GCP cost.

## 9. Reproduction

```bash
cd project_astra

# Confirm G6PD's tracked alleles directly:
python3 -c "
from astra.discovery_engine import population_signal as ps
recs = ps.load_gnomad_records()
alleles = sorted({r['allele'] for r in recs if ps._norm_gene(r['gene']) == 'G6PD'})
print('G6PD alleles tracked in the pinned artifact:', alleles)
"
# Expect: ['A-', 'Mediterranean'] -- and nothing else.

# Confirm the live mechanistic-prior entry this gap would affect:
python3 -c "
from astra.discovery_engine import mechanistic_prior as mp
print(mp.lookup('G6PD', 'RASBURICASE'))
"

python3 -m pytest tests/test_g6pd_gnomad_coverage_gap.py -v
```

Literature PMIDs named throughout for independent re-verification:
16329560, 30077011, 17018380, 11499668, 20007901, 24787449.
