# Indian Oncology PGx — the detection layer, re-derived from current sources
# (2026-08-17)

> **What this document is.** A re-derivation of the Indian oncology
> pharmacogenomics problem from the current literature, a solution, and the
> architecture that implements it. Written after the research, and after the code
> — every capability described below is running, tested, and committed as of this
> date. Nothing here is a proposal awaiting implementation except where §7 says
> so explicitly.
>
> **Relationship to the existing documents.** It does not supersede
> `ONCOLOGY_SOLUTION_AND_ARCHITECTURE_2026-08-16.md` (the problem derivation,
> nineteen sections, five research passes) or
> `ONCOLOGY_HEAD_AND_NECK_REFRAME_2026-08-17.md` (the population correction: the
> largest Indian fluoropyrimidine exposure is head and neck cancer on induction
> TPF, not colorectal on CAPOX). Both stand and are not restated.
>
> **What it adds** is a correction to the *layer* those documents located the
> problem in. They treat Indian DPYD PGx as an **interpretation** problem — the
> right genotype with its uncertainty stripped off. That framing is right about
> the failure mode and wrong about where the failure now lives. The binding
> constraint is one layer down, in **detection and representation**, and it was
> in our own engine.

---

## 1. The finding, in one paragraph

An Indian DPYD panel's most common actionable result is not measured. It is
**inferred from a benign variant sitting next to the real one**, and CPIC
requires that inference to be disclosed in the test report. `HapB3` is 60.5% of
all actionable DPYD allele frequency in CPIC's Central/South Asian data and
**76.9% of everything our engine could call**, and our engine called it from
`rs56038477` — a synonymous, functionally silent exonic tag SNP — while the
causal intronic variant `rs75017182` appeared **nowhere in the package**. The
engine therefore could not make CPIC's mandated disclosure, could not accept a
result from a laboratory that genotyped the functional variant, and could not
implement the change CPIC has already announced for fall 2026. Separately, four
actionable alleles with nonzero Central/South Asian frequency were uncallable —
21.3% of the actionable total, including `c.2279C>T`, which is **one of the three
intermediate-metabolizer variants actually found in the only Indian NGS DPYD
study**. All of this is now fixed, and the fix is a provenance change: not one
CPIC value moved.

---

## 2. The problem, in the layer it actually lives in

### 2.1 What the prior documents established, and where it stops

The 08-16 derivation is intact: an Indian DPYD panel returns "Normal
Metabolizer" for the overwhelming majority of patients, most of whom carry
*something*, and D-TORCH — now peer-reviewed as Baskarane et al.,
*Front Pharmacol* 2026;17:1732128, published 20 February 2026 — states the
consequence in its own words:

> 35 out of 50 patients in our cohort, classified as normal metabolizer
> phenotype as per the CPIC guidelines, still developed grade 2 or 3 toxicity,
> emphasizing the limitation of CPIC-based phenotype prediction and dose
> adjustment in the Indian population.

Its Table 4 confirms the variant axis carries no information in that cohort:
grade ≥2 toxicity 63.6% in variant carriers against 55.6% in wild-type,
OR 0.71 (95% CI 0.26–1.98), p=0.612; Firth-adjusted OR for DPYD variant status
0.52 (0.16–1.51), p=0.23. The four variants Indians most commonly carry —
`*9A` (n=25), `*6` (n=13), `*5` (n=12), `M166V` (n=7) — are all CPIC "normal
function".

That is a real and correctly-described problem. But it is a problem about what
to *say* around a correct call. **This document is about whether the call itself
is what we think it is**, and that question turned out to have a worse answer.

### 2.2 The measurement, computed rather than asserted

Every actionable (No or Decreased function) DPYD allele CPIC publishes with a
nonzero Central/South Asian frequency, read live from
`api.cpicpgx.org/v1/allele?genesymbol=eq.DPYD`:

| allele | freq | % of actionable | callable before this work |
|---|---|---|---|
| `HapB3` (`c.1129-5923C>G, c.1236G>A`) | 0.019658 | **60.5%** | yes — **via the benign tag SNP only** |
| `c.2279C>T` | 0.006030 | **18.6%** | **no** |
| `*2A` (`c.1905+1G>A`) | 0.005076 | 15.6% | yes |
| `c.2639G>T` | 0.000700 | 2.2% | **no** |
| `c.2846A>T` | 0.000640 | 2.0% | yes |
| `c.1475C>T` | 0.000200 | 0.6% | **no** |
| `*8` (`c.703C>T`) | 0.000200 | 0.6% | yes |
| **total** | **0.032505** | | **78.7% callable** |

Two numbers follow, and they are the problem:

- **21.3% of actionable Central/South Asian DPYD allele frequency was
  uncallable.** Those alleles returned `Indeterminate` — downstream,
  indistinguishable from a genuinely unresolvable genotype.
- **76.9% of everything the engine *could* call was `HapB3`, and it was called
  from a variant with no functional consequence.**

Under Hardy-Weinberg, P(at least one actionable allele) = 0.0640, so
**93.6% of Indian patients have no actionable DPYD allele at all**. (The prior
documents' 95.0% used an earlier allele set; 93.6% is the value from the
computation above, and both should not be quoted interchangeably.)

### 2.3 Why the tag SNP is not the allele

`HapB3` is defined by two variants:

- **`c.1129-5923C>G` (`rs75017182`), intron 10 — the causal variant.** It creates
  a cryptic splice site. Carriers show ~30% less correctly-spliced mRNA and ~35%
  lower enzyme activity (Nie et al., PMID 28295243, n=3,950 Mayo Clinic Biobank).
- **`c.1236G>A` (`rs56038477`), exon 11 — a benign synonymous variant**
  (p.Glu412=). It does nothing. It is genotyped because a common exonic SNP is
  far cheaper to type than a deep intronic site.

They were assumed to be in perfect linkage disequilibrium. **They are not.** In
*All of Us* WGS (n=245,394), 14 of 6,265 tag carriers lacked the causal variant —
LD 0.9985, 0.223% of tag carriers (Turner/Haidar et al., *Clin Transl Sci*
2024;17(1):e13699, PMID 38129972). Independently replicated at 1 of 46 in a
Spanish cohort (*Int J Mol Sci* 2025;26:8136, titled, pointedly, "A Call to
Revise European Pharmacogenetic Guidelines"). The 2024 paper's conclusion:

> *DPYD* genotyping should include the functional variant c.1129-5923C>G, and
> not the c.1236G>A proxy, to accurately predict DPD activity.

So a tag-only positive can be a **false positive**, and the cost of acting on one
is a 50% fluoropyrimidine dose reduction — in curative-intent treatment, in a
disease where India presents late and the intent is often the only chance.

### 2.4 The requirement we were violating

CPIC does not leave this to inference. From the fluoropyrimidines guideline page,
verbatim:

> if only c.1236G>A is tested or results are available for, it should be clearly
> stated in the test report that "decreased function" was inferred by detecting
> the exonic tag SNP, and disclose that in rare cases, the causal decreased
> function variant c.1129-5923C>G may not be present despite having this tag SNP.

CPIC also states it "updated the allele definition and functionality tables to
include the c.1129-5923C>G SNP separately as this is likely the causal variant
leading to decreased function" — and it does: the API publishes **two** alleles,
`c.1129-5923C>G, c.1236G>A (HapB3)` (id 778378) and `c.1129-5923C>G` alone
(id 3942828), both Decreased function, both activity value 0.5.

Our engine had **one** row, keyed on the tag. Observed on the public API at
0.8.2:

```
infer("DPYD","*1","HapB3")           -> Intermediate Metabolizer  REDUCE_50PCT
infer("DPYD","*1","c.1129-5923C>G")  -> Indeterminate             action=''
```

Three consequences, each verified by running the code:

1. **`asl` could not emit CPIC's required sentence.** Not because it was
   unwilling — because the engine never told it which locus produced the call.
   The distinction did not exist in the data model.
2. **A laboratory that genotyped the functional variant had its result
   rejected.** Mayo Clinic's own DPYD panel tests `rs75017182`, not the tag. Our
   engine returned `Indeterminate` for the better assay.
3. **The announced CPIC update was unimplementable.** On 2026-07-09 CPIC
   announced that `c.1129-5923C>G` moves to activity value **0.75** (heterozygote
   activity score 1.75; cycle 1 at 75% of intended dose, with escalation in later
   cycles guided by tolerability), and stated that the change is **specific to
   that variant** and "should not be applied to other variants which may have
   previously shared the same allele value". An engine that cannot distinguish
   the causal allele from its tag cannot apply a change scoped to the causal
   allele. That is the majority of Indian panel-positive patients.

### 2.5 The allele the only Indian study found, that we could not call

D-TORCH's three intermediate metabolizers were `rs56038477` (the HapB3 tag),
`rs3918290` (`*2A`), and **`rs112766203` (`c.2279C>T`)**. We could call the first
two. For the third, CPIC's diplotype API publishes
`c.2279C>T/Reference -> Intermediate Metabolizer`, and our engine returned
`Indeterminate`. It is 18.6% of actionable Central/South Asian allele frequency —
the second most common actionable DPYD allele in this population.

One of the three actionable patients in the only Indian NGS DPYD study would have
come back unresolvable.

### 2.6 What is honestly ours to claim, and what is not

The temptation here is to say Indians are more affected by the LD breakdown. **We
must not, and the data says otherwise.** Suarez-Kurtz (*Clin Transl Sci*
2024;17(4):e13805, PMID 38634417) states it plainly: LD was **perfect** in the
African/African American, Admixed American/Latino, East Asian, Middle Eastern
**and South Asian** cohorts, and "the *All-of-Us* data suggest that this
recommendation applies mainly, if not exclusively, to individuals of European
ancestry." Thirteen of the fourteen discordant participants were European.

The argument that does hold has three parts, and only three:

1. **CPIC requires the disclosure regardless of ancestry.** It is a reporting
   requirement on the pinned source of truth, not a population claim. We were
   violating it.
2. **Nobody has measured this LD in an Indian cohort.** The South Asian
   *All of Us* subsample is not an Indian clinical cohort, and the rate here is
   therefore *unmeasured*, not known to be zero.
3. **India is a high-HapB3 population where the tag is the standard assay.**
   Central/South Asian HapB3 frequency (0.0197) is close to European (0.0237),
   and Indian labs run the four-variant PCR panel, which reaches HapB3 through
   the tag. The exposure to this particular inference is large here precisely
   because the allele is common and the cheap assay is the norm.

There is also a published precedent for the architectural move: the Brazilian
national panel **replaced** CPIC target SNP `rs55886062` with `rs115232898`
(`c.557A>G`) because the former was never detected in Brazilians. That is
population-specific **panel composition**, not reclassification — the same
distinction this work rests on.

---

## 3. The solution

One sentence: **make the engine say which variant it actually saw, and make the
report say what that means.**

Three properties make this the right intervention rather than a defensible-looking
one:

- **It implements a CPIC requirement we were violating.** It is not a novel
  clinical assertion. The strongest sentence in the report is a quotation.
- **It is not a reclassification.** CPIC assigns Decreased function to the
  haplotype, to the causal variant alone, and by inference to the tag. All three
  keep that word. Not one activity value, phenotype or clinical action moved. This
  is what keeps the work out of the failure class of the `*6` incident, where a
  defensible clinical judgement was written into a pinned table as if it were
  CPIC's and survived four releases undeclared.
- **It is the precondition for the fall-2026 update.** The 0.75 value applies
  only to the causal allele. Without separating it from its tag, the update is
  not implementable at all.

### 3.1 What ships

**Engine (`anukriti-pgx-core` 0.9.0)**

`DPYDCaller` is now haplotype-aware, using the same longest-match-first
resolution `TPMTCaller` already used for `*3A`/`*3B`/`*3C`. `HapB3` is defined by
both its loci and claims them before either single-locus label can, so one
chromosome's evidence is never counted twice.

`Diplotype` gains **`hapb3_basis`**, with five values:

| value | meaning |
|---|---|
| `"haplotype"` | both loci read and variant-positive — the full CPIC definition |
| `"causal"` | the functional variant `c.1129-5923C>G` was observed |
| `"tag_only"` | only the benign tag SNP was read; the causal locus was **not tested** |
| `"tag_without_causal"` | tag positive, causal locus tested and **absent** — the LD-breakdown case |
| `""` | no HapB3-family allele was called |

The last two are kept separate deliberately. Collapsing them would repeat the
NOT_TESTED-versus-ABSENT error the whole platform refuses to make: one means "we
did not look", the other means "we looked and it contradicts the inference".

The panel goes **13 → 18 alleles**, adding the causal variant, the tag as a label
in its own right, and `c.2279C>T` / `c.2639G>T` / `c.1475C>T`. Diplotype coverage
goes **105 → 190**. Callable share of actionable Central/South Asian allele
frequency goes **78.7% → 100%**.

**Report (`asl`)**

`interpret.hapb3_disclosure(basis)` returns CPIC's sentence, quoted, with two
distinct rule IDs:

- **`P5_DPYD_HAPB3_TAG_SNP_BASIS`** — the causal variant was never tested. States
  that decreased function was inferred from the tag, gives the LD figures with
  their PMIDs, notes that the observed discordance was almost entirely European
  and that no Indian cohort has been measured, and says that testing the causal
  variant directly resolves it.
- **`P5_DPYD_HAPB3_TAG_WITHOUT_CAUSAL`** — the causal variant was tested and is
  absent. States that this is the documented LD-breakdown genotype, that it is
  therefore the one most likely to be a false positive, that CPIC's
  recommendation is nonetheless unchanged, and that a 50% reduction in
  curative-intent treatment is the cost of acting on a false positive.

`interpret.require_hapb3_capable_engine()` refuses to interpret at all on an
engine older than 0.9.0. There, `hapb3_basis` is simply absent and
`getattr(result, "hapb3_basis", "")` would return `""` — which `asl` reads as *no
HapB3 allele was called*. A tag-only patient would get CPIC's 50% reduction with
the disclosure **silently missing**, which is exactly the falsely-reassuring
failure this package exists to prevent. Refusing loudly beats degrading quietly.

---

## 4. Architecture

### 4.1 Placement

Nothing moved. The capability landed in the layers that already owned these
concerns, which is the main thing to say about it.

```
CPIC live API ─┬─(regen_dpyd_tables.py --check, gated in CI)──▶ pinned tables
               └─(cpic_live drift tests)

anukriti-pgx-core 0.9.0          ← WHICH VARIANT WAS SEEN  (detection layer)
  DPYDCaller: longest-match-first over multi-locus definitions
  Diplotype.hapb3_basis: haplotype | causal | tag_only | tag_without_causal | ""
        │
        ├──▶ asl                 ← WHAT THAT MEANS  (disclosure layer)
        │      interpret.hapb3_disclosure()  -> CPIC's sentence, quoted
        │      interpret.require_hapb3_capable_engine()  -> refuse, never degrade
        │      interpret.assayed_variant_name()  -> name the locus actually read
        │      pipeline -> P5_* flags alongside CPIC's call, never instead of it
        │        │
        │        └──▶ anukriti-api  POST /asl/dpyd/interpret  (authenticated)
        │                 │
        │                 └──▶ anukriti-main  hapb3_basis on the client contract
        │
        ├──▶ anukriti-swarm       (unchanged; 287 tests pass against 0.9.0)
        └──▶ cohortfit            (unchanged behaviour; count assertion relaxed)
```

The invariant holds throughout: **the deterministic layer decides, the
disclosure layer explains, and neither overrides CPIC.**

### 4.2 The three design rules that did the work

**Rule 1 — provenance is a field, not a re-derivation.**
`asl` does not infer the basis from the assay. It reads `hapb3_basis` off the
engine's own record. The engine knows what loci it matched; recomputing that
downstream would create two implementations of one fact, and they would drift.
Same reason there is no strand-translation table in the API adapter.

**Rule 2 — the display name is the locus read; the lookup key is CPIC's allele.**
CPIC's allele name for the tag SNP is the compound
`"c.1129-5923C>G, c.1236G>A (HapB3)"` — it *names the causal variant*. Using that
as the display name for a tag-only result produced a report that contradicted
itself (§5, defect 1). So the evidence lookup keeps CPIC's compound name — it is
the row carrying the function, activity value and frequency — while anything
describing *what the assay read* uses `interpret.assayed_variant_name()`.

**Rule 3 — a version floor is enforced in code, not documented in a comment.**
The pin in `pyproject.toml` is a floor with a stated reason, and
`require_hapb3_capable_engine()` makes it real. A pin can be edited by anyone
resolving a dependency conflict; a raised exception cannot be edited by accident.

### 4.3 Guards added, so this class cannot recur

- **`tests/test_dpyd_hapb3_provenance.py`** (16 tests). The load-bearing one
  asserts the phenotype, action and evidence level are **identical across every
  basis**. If it ever fails, the change has stopped being provenance and started
  being reclassification.
- **A locus-count invariant.** A row whose `rsid` and `alt` columns disagree in
  length would be skipped silently by the caller (it zips the two lists), so a
  defining locus could vanish with no error.
- **The live CPIC drift check now handles multi-locus rows**, and verifies the
  tag's function against the haplotype row it inherits from rather than letting
  it match nothing.
- **`tests/test_hapb3_disclosure.py`** (14 tests) in `asl`, including one that
  asserts the assay inventory never claims the causal variant was tested when it
  was not.
- **`test_no_rsid_alias_table_is_reintroduced`** in `anukriti-api`, alongside the
  existing strand-flip guard.

---

## 5. What the walkthrough exposed

The capability was built, then a real patient was walked through it: 54-year-old
man, locally advanced oral cavity SCC, technically unresectable, for induction
docetaxel/cisplatin/5-FU — the commonest Indian fluoropyrimidine setting — whose
lab ran the four-variant PCR panel and found HapB3 heterozygous **at the tag
SNP**. It is now `asl demo --panel tag_only`.

Seven defects, none of them in a genotype call. All fixed and pinned by test.

| # | Where | What was wrong |
|---|---|---|
| 1 | `asl` report | Claimed the causal variant **was tested** when it was not. CPIC's compound allele name names it, so the assay inventory printed it as tested while the untested list below said it had never been assayed. **The same report asserted both.** |
| 2 | `asl` residual | Same problem in the `Found:` line. |
| 3 | `asl` flag | Quoted "77.5%" without naming its denominator. It is 77.5% of the four guideline-panel variants (0.025375) and 60.5% of all actionable CPIC DPYD alleles (0.032505). Both are now stated. |
| 4 | `anukriti-api` | `_RSID_ALIAS` rewrote `rs75017182 → rs56038477`, **destroying the exact distinction this work creates** — and it carried a wrong REF/ALT (`G>A` instead of CPIC's `G>C`) to make the substitution line up. Removed. |
| 5 | `anukriti-main` | "First marker present wins, then break" ignored the causal locus whenever the tag was present, so a lab reporting the functional variant had its stronger result discarded. |
| 6 | `anukriti-main` | **Pre-existing.** `g3 === "TT"` labelled `D949V-hom`, but `c.2846A>T` is plus-strand REF=T ALT=A — so `TT` is homozygous **reference**. Essentially every patient had `D949V-hom` printed in their star-allele string. The activity score was never affected; the displayed text was, and that is what a clinician reads. |
| 7 | `asl`, `cohortfit` | Hardcoded counts ("12 further loci", `== 105` diplotypes) that had to be edited on every engine bump. Now derived and a floor respectively. |

Defect 4 is the one worth dwelling on. The alias was added for a good reason —
the frontend sent one rsID, the engine indexed the other — and it was justified
in a comment saying "both rsIDs identify the same haplotype". That was the
consensus position until 2024. It became false, and the code kept enforcing it.
An adapter that reconciles two identifiers is invisible once written, and it was
silently undoing, at the API boundary, the distinction the engine had just been
taught to make.

Defect 6 is the other kind: nobody introduced it in this session, and it had
been printing a variant call for a variant the patient did not have. It surfaced
only because a test asserted on the star-allele string for a homozygous-reference
patient, which nothing had previously done.

---

## 6. Verification

Every suite run against the local 0.9.0 engine:

| repo | result |
|---|---|
| `anukriti-pgx-core` | **380 passed / 5 skipped**, plus **5 `cpic_live`** drift tests against the live CPIC API |
| `asl` | **168 passed** (was 152), evidence tables byte-clean vs CPIC |
| `anukriti-api` | **174 passed / 1 skipped** |
| `cohortfit` | **241 passed / 1 skipped** |
| `anukriti-swarm` | **287 passed**, unchanged by this work |
| `anukriti-main` | **88 passed** (was 84) |

Mechanical regression review, 1,991 genotype cases across 12 genes, old engine
0.8.1 installed in a separate venv:

```
SAFETY_FIX 64   NOMENCLATURE 18   SAME 1909
drug axis:  ACTION_GAINED 35   SAME 70
```

Zero `NEWLY_INDETERMINATE`, zero `OVER_RESTRICTION_FIX`, zero
`PHENOTYPE_CHANGE`, zero `ACTION_LOST`. **Nothing became more permissive.**

The 64 safety fixes are compound heterozygotes whose second allele was
previously invisible:

```
*5 + c.2279C>T het   ['*1/*5', 'Normal Metabolizer']
                  ->  ['*5/c.2279C>T', 'Intermediate Metabolizer']
```

That is the falsely-reassuring direction — an actionable carrier reported Normal
Metabolizer on a standard dose — and every target phenotype is CPIC's own
`generesult`, copied verbatim.

The 18 nomenclature changes are the intended one: tag-only samples now resolve to
`c.1236G>A` rather than `HapB3`, phenotype and action unchanged. **Consumers that
string-match `"HapB3"` had to be updated**, which is how defects 4 and 5 were
found.

Behaviour table, engine and frontend independently agreeing:

| genotype | basis | diplotype | phenotype |
|---|---|---|---|
| tag CT, causal not assayed | `tag_only` | `*1/c.1236G>A` | Intermediate Metabolizer |
| tag CT, causal GG | `tag_without_causal` | `*1/c.1236G>A` | Intermediate Metabolizer |
| causal GC only | `causal` | `*1/c.1129-5923C>G` | Intermediate Metabolizer |
| both het | `haplotype` | `*1/HapB3` | Intermediate Metabolizer |
| all reference | `""` | `*1/*1` | Normal Metabolizer |

The phenotype column is constant by design. That is the whole point.

---

## 7. What is not done

- **0.9.0 is not on PyPI.** Consumers install the engine from a local checkout.
  Publishing it is the immediate next step; nothing has been pushed to any
  origin.
- **The `anukriti` sandbox and `anukriti-validation-iwpc` are still pinned
  `==0.7.3`** and have missed both the TPMT genotype-inversion fix and NUDT15.
- **CPIC's announced 0.75 for the causal allele is not pre-applied**, and should
  not be until the fall-2026 guideline publishes. The `P4` flag says so.
- **No Indian cohort has measured this LD.** The concrete, answerable question
  this work creates is: *in Indian patients positive for `c.1236G>A`, what
  fraction lack `c.1129-5923C>G`?* It needs one PCR assay added to an existing
  workflow, and it is a better ask of a site than "give us your data".
- **UGT1A1 remains absent**, and the 08-17 recommendation stands: build the
  caller, defer the recommendation, because CPIC publishes no UGT1A1-irinotecan
  guideline and presenting DPWG advice in CPIC's voice is the `*6` error again.
- **The ledger still has no cycle dimension**, which the 08-17 document
  identified as the highest-value near-term capability: a report arriving after
  cycle 1 can only change cycles 2–3, and that is where the 70%→10% mucositis
  reduction was observed.
- **No clinician has reviewed any of this.** Research tool, not a diagnostic
  device.

---

## 8. Limitations of this document

- **The engine coverage figures are CPIC's frequencies, not Indian
  measurements.** "Central/South Asian" is CPIC's reference population; it is not
  an Indian clinical cohort, and the platform's own clinality work shows
  within-South-Asian variation of ~3× for some alleles.
- **The observed LD breakdown is European** (§2.6). Every claim here is scoped
  accordingly.
- **`c.2279C>T`'s Indian evidence is one patient** in one 76-patient exploratory
  sub-study. Its inclusion rests on CPIC's actionable classification and nonzero
  CPIC frequency, not on that observation.
- **CPIC publishes no frequency for the causal-alone allele** (all populations
  null for id 3942828). The engine does not invent one.
- **Longest-match resolution is an unphased inference, not phase
  determination.** A laboratory reporting phase should be believed over it.
- **The 93.6% figure supersedes 95.0% only for the allele set computed here.**
  Both appear in platform documents; they are not interchangeable, and the
  command is recorded so either can be reproduced.
- **The walkthrough patient is synthetic.** He is built from published Indian
  regimen, site and assay patterns, not from a real record.

---

## 9. The through-line

The platform's running list of incidents now reads:

| incident | genotype wrong? | what was actually wrong |
|---|---|---|
| 0.7.2 DPYD strand | yes | tests encoded the same wrong convention as the table |
| 0.7.2 `*6` function | no | a defensible judgement in a pinned table, with nothing recording why |
| 0.8.1 TPMT inversion | yes | fixtures agreed with the wrong ALT base |
| `pip install asl` | no | every test passed; the wheel shipped no data |
| 0.8.2 `5-FU` | no | docstring described resolution the code lacked; a contraindication vanished |
| `asl` TPF rate | no | a correct principle applied to only one of its two axes |
| **0.9.0 HapB3 tag** | **no** | **the call was right, and we could not say what it rested on** |
| **`_RSID_ALIAS`** | **no** | **an adapter enforcing a consensus that had since been refuted** |
| **`D949V-hom`** | **no** | **a reference base printed as a variant call for years** |

Seven of nine are in the "genotype was right" column. The engine has been
hardened against calling the wrong allele; what remains are the failures where
the allele is right and something around it is wrong — a vanished action, a
borrowed rate, a comparator that does not describe the patient, and now a
*provenance* that was never recorded.

The new entry adds one thing the earlier ones did not. The `*6` and `5-FU`
defects were cases where the code disagreed with its own documentation. This one
was a case where the code agreed with the *field's* documentation, and the field
changed its mind in 2024 — CPIC updated its tables, published a second allele,
and wrote a reporting requirement, and our engine went on doing the reasonable
thing from 2018. Pinning a source of truth is not the same as tracking it. The
drift check compares values we already carry; it cannot tell us that the source
has started publishing a distinction we never modelled.

*The failure is rarely the wrong answer. It is the right answer with its
provenance — or its uncertainty, or its safety annotation — stripped off.*
