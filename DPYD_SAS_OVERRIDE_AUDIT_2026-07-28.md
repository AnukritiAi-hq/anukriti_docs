# DPYD SAS Override Audit — A Named Refusal Whose Cited Evidence Did Not
# Support It (2026-07-28)

> **Scope:** audit and correction of `anukriti-swarm`'s population-aware DPYD
> override (`_apply_population_aware_overrides`, shipped 2026-06-06 in
> `1c38325`), triggered by reading three primary colorectal-cancer DPYD papers
> added to `anukriti_docs/papers/colorectal-cancer-dpyd-5fu/`.
>
> **Outcome:** the override blocked synthesis for South Asian patients on the
> strength of two claims. One (CPIC assigns Normal function) is true. The other
> (South Asian enrichment + established toxicity risk) is refuted by real
> gnomAD data and contested by the papers it cited. The hard block has been
> replaced with a named uncertainty flag. **Behaviour change is live in
> `anukriti-swarm`; `anukriti-pgx-core` is untouched.**
>
> **Repo:** `anukriti-swarm`. Every number below was queried live on
> 2026-07-28 from CPIC's and gnomAD's own APIs, or read directly from the
> papers' own tables. None are estimated, interpolated, or recalled.

---

## 1. What the override did

`core/runtime/runtime.py`, between Stage 4 (sufficiency) and Stage 5
(synthesis):

```python
_SAS_DPYD_REFUSAL_ALLELES: tuple[str, ...] = ("*9A", "M166V")
...
checkpoint["allows_synthesis"] = False
checkpoint["blocking_reason"] = refusal_reason
self._emit(RuntimeEventKind.SAFE_ABSTENTION, ctx,
           payload={"rule": "U4_SAS_DPYD_OVERRIDE", ...})
```

For any SAS patient whose DPYD genotype contained `*9A` or `M166V`, the run
was converted into a refusal citing:

> *"U4: DPYD \*9A assigned Normal function by CPIC (European data). South
> Asian evidence (27% carrier frequency for \*9A in South Indian oncology
> cohorts) shows clinically significant toxicity risk not captured by the
> European 4-variant panel."*

The supporting frequency records (`datasets/pharmfreq/allele_frequencies.py`)
carried `source="literature"`, `version="Hariprakash2018"`, and
`function="normal_function_cpic_sas_discordant"`.

**The override had zero test coverage.** No test in any repo referenced
`U4_SAS_DPYD_OVERRIDE`, `_apply_population_aware_overrides`, or DPYD at all.
That is how the following survived from 2026-06-06 to 2026-07-28 — 52 days —
unchallenged.

---

## 2. What held up

**CPIC does assign both alleles Normal function.** Verified against CPIC's
own live API, the same source `pgx-core` 0.7.0 and 0.7.1 were verified
against:

```bash
curl -s "https://api.cpicpgx.org/v1/allele?genesymbol=eq.DPYD"   # 84 alleles
```

| Allele | CPIC name | CPIC clinical function |
|---|---|---|
| `*9A` | `c.85T>C (*9A)` | **Normal function** |
| `M166V` | `c.496A>G` | **Normal function** |

So the premise "CPIC calls these normal" is correct, and the broader
observation that CPIC's DPYD guideline rests on European cohorts is
independently supported — `ASTRA_FINDING_SLCO1B1_EUR_IS_POPULATION_MAXIMUM_2026-07-10.md`
§7.2 already established DPYD as a confirmed EUR-maximum case, with Kanai
2023 (n=1,364 Japanese CRC patients, PMID 36524458) directly demonstrating
that the CPIC-actionable association fails to transfer to an Asian cohort.

That is a real finding. It is not, however, evidence that *these two specific
alleles* carry South Asian risk.

---

## 3. What did not hold up

### 3.1 Neither allele is enriched in South Asians

Real gnomAD v2.1.1 exome frequencies, queried live via the GraphQL API:

| Allele | SAS | EUR (NFE) | **SAS/EUR** | AFR | EAS | AMR | FIN |
|---|---|---|---|---|---|---|---|
| `*9A` (rs1801265) | 0.2550 | 0.2226 | **1.15** | **0.4131** | 0.0720 | 0.2113 | 0.2932 |
| `M166V` (rs2297595) | 0.0906 | 0.1004 | **0.90** | 0.0334 | 0.0158 | 0.0359 | 0.1788 |

`*9A` is marginally more common in South Asians than Europeans (1.15x — not
enrichment in any meaningful sense), and **AFR is the population maximum at
0.4131**, 62% higher than SAS. For `M166V` the claimed direction is simply
**inverted**: South Asians carry it *less* often than Europeans.

> **A note on the `*9A` numbers, because they are easy to get wrong.** DPYD is
> a minus-strand gene. gnomAD represents rs1801265 as `1-98348885-G-A`, where
> the `*9A` variant allele is the **REF** letter (G), so the variant frequency
> is `1 - AF(A)`, not gnomAD's raw ALT AF. Reading the ALT column directly
> gives 0.745 for SAS and inverts every comparison. This is the same
> transcript-vs-genomic orientation subtlety that `anukriti-api/app/adapters.py`
> already documents and handles for DPYD's other rsIDs.

The withdrawn records were wrong in magnitude as well as direction: `*9A` EUR
was recorded as 0.090 against a real 0.2226 (understated 2.5x) and AFR as
0.050 against a real 0.4131 (**understated 8.3x**).

### 3.2 The frequencies were never real data

The records claimed `source="literature"`, `version="Hariprakash2018"`. Two
problems — and one non-problem worth recording so nobody re-litigates it:

0. **The year is fine.** An earlier pass of this audit asserted the paper was
   "Hariprakash 2017, not 2018." That was wrong, and is withdrawn: PubMed's
   record (PMID 29239269) gives *Pharmacogenomics* 2018 Feb;19(3):227-241,
   epub 14 Dec 2017. The version of record is 2018. The label's year was
   correct; only what it was attached to was not.
1. **The paper does not report the cited numbers.** Its SAS rs1801265 figure is
   0.266 (1000G SAS), ranging 0.208–0.266 across seven datasets — reasonably
   close to the recorded 0.270. But for rs2297595 it reports 0.062 (SAS),
   range 0.062–0.100 across datasets; the record said 0.120, above *every*
   value in the paper. Naushad's Indian cohort (n=2,000) gives 9.0%.
2. **`sample_n=3471` does not correspond to anything.** Hariprakash's
   integrated SAGE cohort is n=3,140, and genotype data for these two variants
   was available for exactly 3,140 individuals.

Separately, the platform's pinned real artifact
`datasets/pharmfreq/gnomad_v2_1_1_frequencies.jsonl` contains 20 DPYD rows —
for `*2A`, HapB3, and `c.2846A>T` — and **no `*9A` or `M166V` rows at all**.
These two alleles never passed through the real BigQuery ingestion; they
existed only as hand-written entries in a module whose own docstring concedes
*"Frequencies are realistic approximations for demonstration."*

### 3.3 The clinical evidence is contested, not established

This is the substantive finding, and the reason the correct fix is a flag
rather than a re-grounded refusal. Three primary papers, three incompatible
answers:

| Paper | Cohort | `*9A` (rs1801265) | `M166V` (rs2297595) |
|---|---|---|---|
| **Hariprakash 2018**<br>*Pharmacogenomics* | n=110 Indian GI-cancer patients (36 colon, 41 rectal) on 5-FU regimens | **Assay failed** — Table 5 marks rs1801265 `NW: Not working` for all genotype rows. No data. | **Associated.** Neuropathy OR 3.66 (p=0.027), hand–foot syndrome OR 5.22 (p=0.011) for CT+TT; HFS OR 7.25 (p=0.024) for grade III+ |
| **Naushad 2021**<br>*J Gene Med* | n=2,000 healthy Indians + 6 pooled Indian toxicity studies | **No association.** OR 1.03 (95% CI 0.69–1.54, p=0.95) | **No association.** OR 1.54 (95% CI 0.76–3.14, p=0.32) |
| **Atasilp 2025**<br>*Cancer Chemother Pharmacol* | n=75 Thai metastatic CRC patients | **Associated** — grade 3–4 neutropenia in 100% (2/2) GG homozygotes from cycle 1 (p<0.001); leukopenia p=0.001; thrombocytopenia p<0.001 | not genotyped |

The override cited Hariprakash for `*9A` — the one allele that paper could not
measure. And the same paper's positive `M166V` finding is contradicted by
Naushad's much larger pooled analysis.

Naushad's own functional data points the same way: expression studies give
C29R (`*9A`) 75% and M166V 72% relative DPD activity, with one isogenic system
showing *significantly higher* activity for M166V. Neither behaves like a
loss-of-function allele.

Atasilp's `*9A` signal is real but rests on **two homozygous patients**, and
the paper's own multivariate analysis found no significant association
surviving adjustment (Table 8). Its stated first limitation is sample size.

**Honest counterweight, so this document does not overcorrect.** Naushad's
pooled design is crude: healthy-cohort allele counts compared against pooled
patient counts across studies with different genotyping platforms and cancer
types, unadjusted. Its OR 158.14 for `*2A` (95% CI 38.07–656.89) is a
sparse-cell artifact, not a credible effect size — Naushad himself walks it
back to 3.79 (95% CI 1.75–8.19) in the head-and-neck subset. The rs1801265
null rests on roughly 130 patients in the ADR arm. So the correct reading is
**not** "these alleles are proven irrelevant." It is: *the evidence is too
thin and too contradictory to support a hard refusal, and the platform was
not saying so.*

### 3.4 The rule id collided with an existing rule

`U4` already means **"KG path bundle supplied but empty"** in
`UncertaintyScoringEngine` (`core/evidence_sufficiency/uncertainty/engine.py:274`,
tested at `tests/unit/test_uncertainty.py:187`). Emitting
`U4_SAS_DPYD_OVERRIDE` made two unrelated conditions indistinguishable to
anything grepping rule ids in an audit trail — directly undermining the
"every refusal cites a rule ID" invariant.

---

## 4. What changed

### `core/runtime/runtime.py`

- `_SAS_DPYD_REFUSAL_ALLELES` → `_SAS_DPYD_CONTESTED_ALLELES` (same two
  alleles; the change is what happens when they are found).
- Rule `U4_SAS_DPYD_OVERRIDE` → **`P1_SAS_DPYD_CONTESTED`** (no collision).
- **No longer mutates `allows_synthesis` or `blocking_reason`.** The Stage 4
  deterministic verdict stands. The hook appends to a new
  `checkpoint["population_uncertainty_flags"]` list instead.
- Emits `UNCERTAINTY_TRANSITION` rather than `SAFE_ABSTENTION`, with
  `allows_synthesis_changed: False` — nothing is being abstained from.
- The reason text now cites all three papers with their real effect sizes and
  the real gnomAD frequencies, and **withdraws the "27% carrier frequency"
  claim** entirely. (That figure was also a category error: 27% was the
  *allele* frequency; carrier frequency in Hariprakash's SAS data is 48% —
  AG 0.40 + GG 0.08.)

### `datasets/pharmfreq/allele_frequencies.py`

Ten records replaced with real, live-queried gnomAD v2.1.1 exome values and
real per-population `sample_n`. `source="gnomAD"`,
`version="v2.1.1_exomes_live_2026-07-28"`, `function="normal_function"`. The
`Hariprakash2018` provenance and the `normal_function_cpic_sas_discordant`
label are gone. The minus-strand REF/ALT subtlety is documented inline.

### `tests/integration/test_population_aware_dpyd.py` (new)

15 tests covering: the flag attaches for four SAS genotypes; it does **not**
block synthesis; a pre-existing legitimate R3 refusal survives untouched; the
event is `UNCERTAINTY_TRANSITION` and not `SAFE_ABSTENTION`; the rule id is
not `U4`; the reason cites all three papers and no longer contains "27%";
scope stays narrow (no flag for non-SAS, for CPIC-actionable `*2A`, or for
other genes); and the frequency records are not SAS-enriched, have AFR as the
`*9A` maximum, and carry real gnomAD provenance.

One test initially failed in a way worth recording: `*1/*9A` is *already*
blocked by rule R3 ("recommendation evidence missing") on its own merits. The
withdrawn override was overwriting that honest, correctly-named refusal — its
own comment said it replaced an already-blocked *"generic reason (R3 etc)"*
because *"our refusal is more informative."* It was substituting an
unsupported claim for a supported one.

---

## 5. Verification

- **Swarm suite: 267 → 282 passed**, 0 failures.
- **All five byte-locked flagship demos are semantically identical.** Raw md5
  differs, but the demos are not run-to-run reproducible in the first place —
  each run emits fresh correlation ids, fresh 12-hex run ids, and millisecond
  timings that also feed the rendered timeline axis labels. Verified by
  normalising exactly those three classes of noise and diffing pre/post output
  across a `git stash` boundary: all five identical. The nondeterminism was
  confirmed independently by running the same demo three times on unchanged
  code and observing the same fields move.
  > Worth flagging as a terminology issue, not a defect:
  > `tests/integration/test_flagship_signatures.py` does not byte-compare demo
  > output — it runs each demo as a subprocess and scrapes distinctive
  > substrings (event counts, verdicts, rule ids), deliberately robust to ANSI
  > codes and timings. That is the right design given the nondeterminism above.
  > But it means the "byte-identical demo signatures session-over-session"
  > invariant as worded in `ANUKRITI_FULL_CONTEXT.md` overstates what is
  > actually enforced, and deserves restating as a *semantic* signature
  > contract.
- **`ruff check`**: the new test file is clean (check and format). `core/runtime/`
  reports the same 4 pre-existing warnings as before this change; none introduced.
- **`ruff format`**: applied to the new test file only. Two remaining format
  hunks (a comprehension at `runtime.py:822`, comment alignment in
  `allele_frequencies.py`) sit in pre-existing code and were deliberately not
  bundled, per CI's own instruction not to mix cleanups with feature work.
  Note that CI hard-gates `tests/` and `core/runtime/` for format, and
  `core/runtime/runtime.py` was *already* failing that gate before this
  change — a separate pre-existing issue.

---

## 6. Separate finding: three real errors in `pgx-core`'s DPYD allele table

Found during this audit, **deliberately not fixed here.** `AGENTS.md` requires
clinical regression review for `anukriti-pgx-core` table changes, and this
audit's scope was the swarm override. Verified against CPIC's live
`/v1/allele` and `/v1/sequence_location` endpoints.

| Table row | Table says | CPIC says that rsID is | Problem |
|---|---|---|---|
| `*10  rs1801266  Decreased function` | `*10`, Decreased | `rs1801266` = **c.703C>T = `*8`**, **No function** | Wrong allele name *and* wrong function |
| `c.1679T>G  rs55971861  No function` | `c.1679T>G`, No function | `rs55971861` = **c.1906A>C**, **Normal function** | Mislabelled; real `c.1679T>G` is `rs55886062` = `*13`, already a separate row. Claims No function for a Normal-function variant |
| `*6  rs1801160  Decreased function` | Decreased | `c.2194G>A (*6)` = **Normal function** | Wrong function |

**Severity: currently latent, not live.** The `function` column is documented
as *"informational, not used by the caller"* (`calling/base.py:211`), and
`DPYD_diplotypes_anukriti_v2024.01.json` contains only 17 entries — none
involving `*6`, `*10`, or `c.1679T>G` — so all three resolve to
`Indeterminate` rather than a wrong phenotype. Confirmed by direct calls.

**But the rsID→name mislabels do surface.** A patient with `rs1801266` gets
diplotype string `*1/*10` when CPIC would call it `*1/*8`, and `rs55971861`
yields `*1/c.1679T>G` — naming a no-function allele — when the real variant is
Normal-function `c.1906A>C`. Those strings reach reports.

For completeness: the apparent REF/ALT "mismatches" against CPIC's genomic
coordinates for `*5`, `*6`, `*12`, `*13`, `c.2846A>T`, HapB3 and `*9A` are
**expected, not bugs** — `pgx-core` uses transcript orientation for this
minus-strand gene, and `anukriti-api/app/adapters.py` documents and handles
the flip.

One more, worth checking against the papers rather than the API: `*4`
(rs1801158) is CPIC **Normal function**, and the table agrees — but Naushad's
pooled Indian data gives it OR 4.40 (95% CI 2.56–7.55, **p<0.0001**), the
second-strongest signal in that analysis after `*2A`. That is a candidate for
the same treatment this audit gave `*9A`/`M166V`: a named uncertainty flag on
an allele where Indian evidence and CPIC disagree — except here the evidence
points *toward* risk rather than away from it.

---

## 7. What this means for the CRC/DPYD focus

The colorectal-cancer → DPYD → 5-FU/capecitabine beachhead survives this
audit intact, and the regulatory tailwind is stronger than the platform's
existing docs claim: in **October 2025 the FDA added a boxed warning** — its
strongest class — to the capecitabine label recommending DPYD testing before
initiation, and advises against use in patients with homozygous or compound
heterozygous variants causing complete DPD deficiency.

But the pitch built on this override needs rewriting. It claimed a validated
population-specific discovery that current guidelines miss. What the platform
actually has, after this audit, is more defensible and more interesting:

> **Which DPYD variants matter in South Asians is an open question in the
> published literature.** Hariprakash 2018 says `M166V`; Naushad 2021 says not
> `M166V` but `*4`/`*6`; Atasilp 2025 says `*9A` on n=2. No existing PGx
> system adjudicates that, and Anukriti now names it as unresolved instead of
> guessing.

That is the honest version, and it is consistent with the platform's own
precedents — the CYP2C9 F-10 table disclosure and the CYP2C9-classifier
negative result both got credibility from documenting a problem rather than a
win.

**Constraint to carry forward:** South Asian *colorectal-specific* DPYD
toxicity evidence is thin. Hariprakash's 77 colon/rectal patients is the
largest CRC slice across these three papers; Naushad's best-powered subset is
head-and-neck; Atasilp is CRC but n=75 and Thai. This argues *for* a
refusal-and-flag product posture, and *against* any external claim that the
South Asian CRC evidence base is deep.

---

## 8. Next steps, none started

1. **[DONE 2026-07-28] Score capecitabine → hand-foot syndrome as a discovery
   candidate.** The 2026-07-25 FAERS run flagged it as a top literature-graph
   gap (PRR 81.6, 5,089 cases, no graph edge) and Hariprakash's Indian CRC
   cohort independently associates HFS with `M166V` (OR 4.64–5.22). Run through
   `score_candidate` + `build_checklist` and scored **MEDIUM** — the top-ranked
   candidate of the three, and the only one with genuine discovery value. The
   contested M166V modifier from §3.3 is carried into the record as
   counter-evidence rather than resolved. See
   `project_astra/docs/20-faers-gap-candidates-scored-2026-07-28.md`, script
   `project_astra/scripts/score_faers_gap_candidates.py`, test
   `project_astra/tests/test_score_faers_gap_candidates.py`. **Awaiting human
   review**, which is now the actual bottleneck rather than engineering.
2. **Open a `pgx-core` issue for the three table errors in §6**, with the
   clinical regression review `AGENTS.md` requires. The `*10`/`rs1801266`
   mislabel is the one that reaches report strings today.
3. **Evaluate `*4`/rs1801158 for a `P1`-class flag** (§6, final paragraph) —
   an allele where Indian pooled data suggests risk that CPIC's Normal-function
   assignment does not carry. Deliberately not done as part of this audit:
   Naushad's `*4` evidence comes from the same unadjusted cross-study
   healthy-vs-patient design as its null results, and swapping one
   under-evidenced refusal for another would repeat the mistake this audit
   corrected. Needs a properly-powered source first.
4. **Build the fluoropyrimidine trial workflow.** DPYD has had a clinical-action
   tier since `pgx-core` 0.5.0, but `trial/workflows` still covers only
   clopidogrel, warfarin, efavirenz, tacrolimus and isoniazid — no
   5-FU/capecitabine arm exists for the CRO cohort-vetting pitch.
   `project_astra/docs/18` already named this bridge as unbuilt.
5. **Audit the remaining hand-written frequency approximations.** This audit
   found fabricated provenance on the two records it happened to check. The
   module docstring admits the whole file is approximate, and `*9A`/`M166V`
   were absent from the real pinned artifact — so the question "which other
   records claim a source they do not have?" is open and now has a precedent
   for how to answer it.

---

## 9. Files changed

| File | Change |
|---|---|
| `anukriti-swarm/core/runtime/runtime.py` | Hard block → named uncertainty flag; rule renamed; reason text re-grounded |
| `anukriti-swarm/datasets/pharmfreq/allele_frequencies.py` | 10 DPYD records replaced with real live gnomAD v2.1.1 values + provenance |
| `anukriti-swarm/tests/integration/test_population_aware_dpyd.py` | **New** — 15 regression tests where there were previously none |
| `anukriti_docs/papers/colorectal-cancer-dpyd-5fu/` | Folder + 3 PDFs renamed to the `papers/README.md` convention |

## 10. Sources

- **Hariprakash JM, Vellarikkal SK, Keechilat P, et al.** "Pharmacogenetic
  landscape of DPYD variants in south Asian populations by integration of
  genome-scale data." *Pharmacogenomics* 2018 Feb;19(3):227-241 (epub 14 Dec
  2017). PMID [29239269](https://pubmed.ncbi.nlm.nih.gov/29239269/). DOI
  [10.2217/pgs-2017-0101](https://doi.org/10.2217/pgs-2017-0101).
- **Naushad SM, Hussain T, Alrokayan S, Kutala VK.** "Pharmacogenetic
  profiling of dihydropyrimidine dehydrogenase (DPYD) variants in the Indian
  population." *J Gene Med* 2021 Jan;23(1):e3289 (epub 20 Nov 2020). PMID
  [33105068](https://pubmed.ncbi.nlm.nih.gov/33105068/). DOI
  [10.1002/jgm.3289](https://doi.org/10.1002/jgm.3289). *(The accepted
  manuscript filed in `papers/` is dated 2020; the version of record is 2021,
  and 2021 is the year used throughout this document and in the code
  comments.)*
- **Atasilp C, Vanwong N, Yodwongjane P, et al.** "Influence of DPYD gene
  polymorphisms on 5-Fluorouracil toxicities in Thai colorectal cancer
  patients." *Cancer Chemother Pharmacol* 2025;95(1):2 (epub 9 Dec 2024).
  PMID [39652193](https://pubmed.ncbi.nlm.nih.gov/39652193/). DOI
  [10.1007/s00280-024-04722-z](https://doi.org/10.1007/s00280-024-04722-z).
- **CPIC live API** — `api.cpicpgx.org/v1/allele?genesymbol=eq.DPYD` (84
  alleles) and `/v1/sequence_location?genesymbol=eq.DPYD`, queried 2026-07-28.
- **gnomAD v2.1.1 exomes** — GraphQL API at `gnomad.broadinstitute.org/api`,
  variants `1-98348885-G-A` (rs1801265) and `1-98165091-T-C` (rs2297595),
  queried 2026-07-28.
- **FDA** — "Safety labeling update for capecitabine and fluorouracil (5-FU)
  on risks associated with dihydropyrimidine dehydrogenase (DPD) deficiency"
  (boxed warning added October 2025).
- **Kanai et al. 2023** — PMID 36524458, via
  `ASTRA_FINDING_SLCO1B1_EUR_IS_POPULATION_MAXIMUM_2026-07-10.md` §7.2.
