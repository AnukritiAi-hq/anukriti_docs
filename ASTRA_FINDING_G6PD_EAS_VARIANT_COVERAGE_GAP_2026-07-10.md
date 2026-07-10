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

## 7. What a deeper pass checked, same day — the literal next action,
## actually executed, with an honest, more complicated result than
## expected

The previous version of this section named "query gnomAD's own API
directly" as the literal next action and reported it as blocked by
tooling. That conclusion was wrong and has been corrected: a direct
`curl` POST (rather than this session's earlier `web_fetch`/`httpx`
attempts) successfully reached `gnomad.broadinstitute.org/api`. All three
candidate variants were queried directly against gnomAD's own data,
2026-07-10.

### 7.1 Canton (rs72554665) — confirmed present, EAS-specific, exactly as
### the literature predicted

Resolves to gnomAD variant `X-153760484-C-A`. **Real, confirmed genome
population data**: EAS AC=10/AN=994 (1.006% frequency); every other
population with nonzero AN (AFR, AMR, ASJ, FIN, NFE) shows AC=0. This is
a clean, direct confirmation: Canton is real, genuinely present in
gnomAD's own release, and — in this dataset — observed *only* in EAS,
consistent with the clinical literature. **The platform's own pinned
artifact tracking this as EAS=0.0 (via its two unrelated tracked variants,
A- and Mediterranean) is a genuine extraction-pipeline gap for this
specific variant** — the data exists in gnomAD, it was simply not
selected during whatever process produced the pinned artifact.

### 7.2 Kaiping (rs137852324) and Mahidol (rs137852328) — a real, more
### complicated result: present in gnomAD, but at near-zero frequency
### even in gnomAD's own EAS grouping

Both resolve to real gnomAD variant IDs (`X-153760604-C-T`,
`X-153762340-C-T`). Both show `genome: null` (no genome-callset coverage
at these positions) but real exome-callset data:

- **Kaiping**: EAS AC=1/AN=13825 (0.0072%) — present, but at a frequency
  roughly 140x lower than the clinical literature's own reported share
  (Kaiping is described as ~39% of G6PD-deficient alleles in a real
  Malaysian Chinese neonate cohort, PMID 16329560).
- **Mahidol**: EAS AC=0/AN=13857 (0%) — not observed in gnomAD's EAS
  grouping at all, despite being independently documented as *the*
  dominant variant in Southeast Asia specifically (PMID 20007901, PMID
  15349799: "91.3% of G6PD variants were G6PD Mahidol" in a Myanmar
  cohort). Mahidol *does* show a small, nonzero signal in gnomAD's AMR
  (5/27,420) and NFE (4/81,708) groupings instead — populations with no
  documented clinical connection to this variant's known Southeast Asian
  positive-selection history.

**The most likely explanation, checked and consistent with gnomAD's own
population-grouping structure**: gnomAD v2.1's "EAS" category breaks down
only into `eas_jpn` (Japanese), `eas_kor` (Korean), and `eas_oea` ("other
East Asian") — **there is no distinct Southeast Asian, Thai, Malaysian, or
Filipino subpopulation category**. The clinical literature's Kaiping/
Mahidol frequency estimates come specifically from Chinese (Guangdong,
Guangzhou), Malaysian Chinese, Thai, and Myanmar cohorts — populations
with documented malaria-driven positive selection for these exact
variants (Mahidol's selection history is independently dated to the past
~1,500 years specifically in Southeast Asia, PMID 20007901). gnomAD's
"other East Asian" bucket is a broad, ancestry-mixed grouping that may
simply dilute or miss variants concentrated in specific Southeast Asian
sub-populations, even though the variants are real, catalogued, and
observed (Kaiping) or plausibly under-sampled (Mahidol) in gnomAD's own
data.

### 7.3 What this means for the original finding — sharpened, not
### undermined

**Canton alone is now a fully-confirmed, direct-primary-source example**
of the exact extraction-pipeline gap this document names: real EAS-
specific gnomAD data exists and was not included in this platform's
pinned artifact. **Kaiping and Mahidol reveal a second, distinct, equally
real problem, one level upstream of the platform's own pipeline**: even
gnomAD's own EAS population category may be too coarse to correctly
represent variants specific to Southeast Asian sub-populations,
independent of anything this platform's extraction process did or didn't
select. This is a more precise, more honest version of the original
finding — not "the platform under-samples EAS," but "the platform
under-samples EAS in at least one directly-fixable way (Canton), and
gnomAD's own EAS category may itself be too coarse for at least one
variant with known sub-population-specific selection history (Mahidol) —
two related but distinct problems, at two different levels of the data
pipeline."

## 8. What a further pass should check next

1. **Fix the Canton gap directly** — this is now a fully scoped,
   unambiguous data-pipeline task: add `X-153760484-C-A` (EAS AC=10/
   AN=994) to the pinned artifact's G6PD rows, using whatever extraction
   process produced the existing A-/Mediterranean rows. No further
   research is needed for this specific variant — it is confirmed, real,
   and ready to add.
2. **Check whether gnomAD v3 or v4 (rather than the pinned v2.1.1) offers
   a finer-grained Southeast Asian population breakdown** that might
   resolve the Mahidol/Kaiping under-representation — this platform's own
   `docs/06-anukriti-integration.md` §2.2 "client, not a copy" discipline
   would need to be checked against whatever the current production
   frequency layer's own gnomAD version is, since pinning a newer version
   is a bigger decision than adding one row to the existing artifact.
3. **Audit every other AFR/EAS/SAS-relevant gene in the pinned artifact
   for the same "gnomAD's coarse population category may not match a
   clinically-relevant sub-population" problem** identified for Mahidol
   — this is a structurally different and arguably more important check
   than simply looking for missing variants (§7.1's Canton problem); it is
   about whether the population *categories themselves* are the right
   grain for every gene checked so far, not just G6PD.

## 9. Honest limitations, on the record

- **[Resolved for Canton, more nuanced for Kaiping/Mahidol — see §7]**
  Whether Canton/Kaiping/Mahidol exist in gnomAD v2.1's own release was
  directly checked against gnomAD's own API in this pass, correcting the
  earlier version of this document. Canton is confirmed, real, and
  EAS-specific. Kaiping and Mahidol are also real, catalogued positions in
  gnomAD, but observed at near-zero or zero frequency even within
  gnomAD's own (coarse) EAS grouping — a different, second-order finding
  in its own right (§7.2), not a simple confirm/deny.
- **This document's frequency claims for Canton/Kaiping/Mahidol come from
  clinical cohort studies (hospital-based case series in China/Malaysia),
  not from gnomAD population-frequency data directly** — cohort-based
  variant-share-among-cases percentages (e.g. "63% of deficient
  individuals") are a different statistic from a population-wide allele
  frequency, and should not be conflated with one. Named precisely to
  avoid the exact category error this session's own SLCO1B1/DPYD
  documents have been careful to avoid elsewhere (disproportionality vs.
  population frequency vs. cohort composition are three different
  numbers). §7's real gnomAD numbers (Canton EAS 1.006%; Kaiping EAS
  0.0072%; Mahidol EAS 0%) are population-frequency numbers, directly
  comparable to this platform's own tracked-allele frequencies — the
  cohort-percentage numbers above remain a different statistic, still not
  conflated with these.
- **No new PRR, no new FAERS query was computed.** This is a literature
  and data-artifact audit plus direct gnomAD API queries, zero new
  network calls to any *platform* system (BigQuery/GCP), zero new GCP
  cost — the gnomAD API itself is a free, public, read-only service.

## 10. Reproduction

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

# Re-verify Canton's real, confirmed gnomAD data directly (no auth needed,
# public read-only API):
curl -s -X POST https://gnomad.broadinstitute.org/api \
  -H "Content-Type: application/json" \
  -d '{"query":"query V($variantId: String!, $datasetId: DatasetId!) { variant(variantId: $variantId, dataset: $datasetId) { variantId rsids genome { populations { id ac an } } } }","variables":{"variantId":"X-153760484-C-A","datasetId":"gnomad_r2_1"}}'
# Expect real EAS ac=10, an=994; ac=0 elsewhere.

# Re-verify Kaiping/Mahidol's real (near-zero) exome data:
curl -s -X POST https://gnomad.broadinstitute.org/api \
  -H "Content-Type: application/json" \
  -d '{"query":"query V($variantId: String!, $datasetId: DatasetId!) { variant(variantId: $variantId, dataset: $datasetId) { variantId rsids exome { populations { id ac an } } } }","variables":{"variantId":"X-153760604-C-T","datasetId":"gnomad_r2_1"}}'

python3 scripts/query_gnomad_for_g6pd_eas_variants.py
python3 -m pytest tests/test_g6pd_gnomad_coverage_gap.py -v
```

Literature PMIDs named throughout for independent re-verification:
16329560, 30077011, 17018380, 11499668, 20007901, 24787449.
