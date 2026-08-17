# Indian Oncology PGx — the head-and-neck reframe, and what it changes
# (2026-08-17)

> **Relationship to the existing documents.** This does not supersede
> `ONCOLOGY_SOLUTION_AND_ARCHITECTURE_2026-08-16.md`. That document's core
> derivation stands and is not restated: an Indian DPYD panel reports "Normal
> Metabolizer" for **95.0%** of patients while **77.8%** carry at least one
> CPIC-"normal function" allele, computed from CPIC's own Central/South Asian
> frequencies and corroborated by D-TORCH's observed 71.1%.
>
> What this document adds is a **correction to the patient population that
> derivation was aimed at**, one development that postdates every doc in the
> repo, and two defects found by testing the engine against the vocabulary and
> regimens of the setting it claims to serve. Both defects are fixed; both fixes
> are verified by running code, and every number below is either computed here
> with the command stated, or carries a PMID.

---

## 1. The finding, in one paragraph

The 08-16 documents framed the problem correctly but aimed it at the wrong
patient. They reason about `CAPOX`, colorectal cancer, and capecitabine — the
population the *European* evidence base was built on. **India's largest
fluoropyrimidine-exposed group is head and neck cancer on induction TPF**, and
that regimen delivers 5-FU at **750 mg/m²/day by continuous infusion for five
days** alongside two other cytotoxics. Its observed grade ≥3 toxicity in Indian
routine practice is roughly **threefold** the rate `asl` was quoting to such a
patient, because TPF had no bucket in the `Regimen` enum and silently inherited
the Dutch colorectal one. Separately, a patient whose drug was written **`5-FU`**
— the ordinary Indian spelling — lost their CPIC recommendation entirely: a true
Poor Metabolizer's `AVOID` became an empty string. Neither defect involved a
wrong genotype. Both are the same failure the platform already names: *the right
answer with its uncertainty stripped off*, and this time with the safety
annotation stripped off too.

---

## 2. Why head and neck, not colorectal

From ICMR-NCDIR's National Cancer Registry Programme (Sathishkumar et al., *Indian
J Med Res* 2023;156(4-5):598-607, PMID 36510887 — 1,461,427 incident cases in
2022, projected 1.57 M by 2025):

| Site group | Cases, 2022 |
|---|---|
| Digestive system (all, incl. oesophagus 55,572 / stomach 52,706) | 288,054 |
| Breast | 221,757 |
| **Oral cavity and pharynx** | **198,438** |
| ⤷ tongue (a separate row) | 56,456 |
| ⤷ larynx | 32,040 |
| Lung and bronchus | 103,371 |

The male leading sites are **lung (10.6%), mouth (8.4%), prostate, tongue
(5.9%), stomach**. Oral cavity + pharynx + tongue + larynx together are on the
order of **~230,000 cases a year**, and locally advanced presentation is the
norm rather than the exception — the Tata Memorial series below describes
induction chemotherapy given largely for *technically unresectable* disease.

**Why this matters more than the raw count.** Colorectal patients in India
receive capecitabine-based regimens broadly comparable to the Dutch cohorts that
produced the published toxicity rates. Head and neck patients on TPF do not:
same drug, different exposure, different toxicity profile. So the population
where India's fluoropyrimidine burden is *largest* is also the population where
the European comparator is *least* transferable. That is not a coincidence
worth glossing — it is the reason a European-derived report misleads hardest
exactly where it is needed most.

### The Indian TPF evidence

**Patil et al. 2016**, *J Community Support Oncol* 14(10):412-419
(doi 10.12788/jcso.0292) — n=58, Tata Memorial, explicitly **routine practice,
non-trial**, CTCAE 4.03, monitored daily to at least day 8:

| Toxicity (cumulative, grade ≥3 unless stated) | Rate |
|---|---|
| Neutropenia | **56.9%** |
| Febrile neutropenia | **20.7%** (12/58) |
| Anaemia | 12.1% |
| Thrombocytopenia | 5.2% |
| Mucositis (all grades, cumulative incidence) | **67.2%** |
| Diarrhoea (all grades, cumulative incidence) | **74.1%** |

The authors' own conclusion: *"The incidence of TPF-related toxicity in Indian
patients in routine practice is high, and the toxicities differ substantially
from the toxicities seen in trial settings."* No induction mortality in this
series, and all 58 completed both planned cycles.

**Patil et al. 2016**, *South Asian J Cancer* 5(4):182-185, PMID 28032083 — the
DPD-specific companion. n=34 on TPF (5-FU 750 mg/m²/day D1-D5 CIV, docetaxel
75 mg/m², cisplatin 75 mg/m²); 12 selected for DPD testing on *toxicity*
criteria; **11 positive → a 32.4% floor (95% CI 19.1-49.3)** against a stated
Caucasian comparator of 3-5%. After 50% 5-FU reduction at cycle 2, grade 3-4
mucositis fell **70% → 10%** (p=0.0198) with no loss of response (27.3% vs 39.1%,
p=0.70).

Two details from that paper matter for design more than the prevalence figure:

- **Testing was reactive, not pre-emptive** — triggered by cycle-1 toxicity.
- **The blocker was logistics, not cost alone.** Testing was outsourced to a
  commercial laboratory with a **10-14 day turnaround**, and the authors state
  plainly that this "hampers our ability to do DPD upfront" because their
  indication is often unresectable disease where waiting is not an option.

That is an ascertainment-biased sample and cannot support a prevalence claim —
the same caveat C12 already applies to the Indian evidence base. It is used here
only for what it does establish: the regimen, the dose, the direction of the
dose-response, and the turnaround constraint.

---

## 3. What postdates every document in this repo

**FDA safety labeling update, 2026-02-05** — capecitabine and fluorouracil now
carry a **boxed warning** for DPD deficiency. The labeling:

- advises **DPYD testing prior to initiating** capecitabine or 5-FU, *unless
  immediate treatment is necessary*;
- **recommends against use** in patients with homozygous or compound
  heterozygous DPYD variants causing complete DPD deficiency, stating **no dose
  has been proven safe** in complete deficiency.

Sources: FDA drug-safety communication 2026-02-05; ASCO policy notice; ONS
2026-02; Medscape 2026a10003v0; approved label `040333Orig1s034lbl.pdf`.

**Three consequences, stated precisely.**

1. **It does not change the Indian access picture.** This is FDA, not CDSCO.
   `asl`'s "no Indian mandate exists" limitation stands unaltered and should not
   be quietly upgraded.
2. **It strengthens the product's regulatory posture rather than the reverse.**
   The core safety message moves further toward *displaying a regulator's and a
   guideline's own text* and further from novel assertion — which is the basis of
   both the CDSCO "informs clinical management" position and the FDA §520(o)(1)(E)
   non-device CDS argument.
3. **The "unless immediate treatment is necessary" clause is the Indian clause.**
   It is precisely the Tata Memorial situation: unresectable disease, treatment
   that cannot wait 10-14 days for an outsourced result. A design that assumes
   pre-treatment genotyping will be available is designing for a different
   country. See §6.

---

## 4. Defect A — a Poor Metabolizer's `AVOID` lost to drug spelling

**Found by asking which drug names an Indian oncology unit actually writes.**
Not by auditing the resolver, which had a passing test suite and a docstring
describing behaviour it did not have.

Observed on the public API, `anukriti-pgx-core` 0.8.1:

```
infer("DPYD","*2A","*2A", drug="fluorouracil")   -> Poor Metabolizer  AVOID  A
infer("DPYD","*2A","*2A", drug="5-fluorouracil") -> Poor Metabolizer  ''     ''
infer("DPYD","*2A","*2A", drug="5-FU")           -> Poor Metabolizer  ''     ''
```

The pinned tables are keyed `DPYD__fluorouracil` and `DPYD__capecitabine`. Both
`clinical_action._normalise_drug` and `recommendation_level._normalise_drug`
lowercased, swapped underscores and spaces for hyphens, and stopped. So the two
ordinary clinical spellings missed the lookup.

**The phenotype was correct in every case. Only the action vanished.** A patient
CPIC says to contraindicate was shown no recommendation at all, on the basis of
an orthographic difference. That is the falsely-reassuring direction.

`5-FU` is not an exotic form. It is how the Indian literature cited throughout
this document writes the drug, and CPIC itself titles its own decision-support
artifact `5-Fluorouracil_CDS_Flow_Chart.jpg` for the row its API returns as
`{"name": "fluorouracil", "rxnormid": "4492"}`.

**Both module docstrings already claimed the synonyms resolved.** Documented
behaviour that did not exist — the third instance of the same class, after the
0.7.2 `*6` deviation and the 0.8.1 TPMT inversion: the description and the table
agreed with each other and not with reality.

### Blast radius, checked rather than assumed

- **`cohortfit` was exposed.** Its `_DRUG_TO_GENE` already maps `5-fu` → DPYD, so
  `resolve_gene("5-FU")` returned `"DPYD"` and `level_for` then returned `''`,
  making `cpic_level` `None` (`rules.py:108`, `audit.py:144`). A trial protocol
  written with "5-FU" was audited as though the gene-drug pair carried no CPIC
  evidence — a silent NO_SIGNAL on the finding that tool exists to produce.
- **`asl` was protected by construction, not by luck.** Its `Drug` enum is closed
  to `capecitabine`/`fluorouracil`, so no synonym could reach the engine. The
  closed enum did its job. It is also why the defect was invisible from the
  product that cares most about this drug.

### The fix, and why it is a table and not a matcher

New `anukriti_pgx_core/phenotype/drug_synonyms.py`, shared by both resolvers so
the fix cannot drift between them. Resolution is an **explicit table, never fuzzy
matching**: allowing an unrelated drug to resolve to one that *has* a
recommendation is a worse failure than returning nothing.

`docetaxel` and `cisplatin` are in the negative test set deliberately — they
arrive alongside 5-FU in TPF, and neither may inherit its DPYD action. Brand
names (`Xeloda`) and regimen acronyms (`TPF`, `FOLFOX`, `CAPOX`) are out of
scope: brand-to-generic mapping is a registry's job and jurisdiction-specific,
and a regimen is not a drug.

Four invariants are pinned by test, each closing a way this fix could itself
become a defect: every alias target exists in the shipped tables (otherwise
resolution succeeds and the lookup still returns nothing — the same silent
failure in a new place); no alias is ambiguous; none shadows a canonical name;
every key is already normalised.

### Verification — and a blind spot in the review itself

`scripts/regression_review.py` reported **`SAME: 1901`**. It was right and
useless: the sweep **never passes `drug=`**, so `clinical_action` and
`evidence_level` are absent from it entirely. A review that reports no change on
a drug-resolution fix is the same shape as the vacuous first 0.8.1 review —
green because it was not looking.

The script now diffs a drug axis too (105 cases: 7 consumer-relevant DPYD
genotypes × 15 spellings), classifying `ACTION_GAINED` / `ACTION_LOST` /
`ACTION_CHANGED` and printing a REVIEW REQUIRED banner if any action is lost.

```
old engine: 0.8.1   new engine: 0.8.2
genotype axis: SAME 1901
drug axis:     SAME 70   ACTION_GAINED 35   ACTION_LOST 0   PHENOTYPE_CHANGED 0
```

Nothing became more permissive; two `AVOID` contraindications were recovered per
previously-broken spelling. Recorded in
`anukriti-pgx-core/docs/REGRESSION_REVIEW_0.8.1_to_0.8.2.md`.

---

## 5. Defect B — the Indian majority was shown a Dutch rate

`asl`'s `Regimen` enum had `SYSTEMIC`, `CHEMORADIATION`, `UNKNOWN`. Induction TPF
has no correct bucket, so it went in `SYSTEMIC`. Verified by running the package:

```
regimen=SYSTEMIC  ->  quoted_rate '22.7% (231/1018)'
                      applies_to_this_patient True
                      source Henricks 2018, PMID 30348537
```

Henricks 2018 is **Dutch, mixed-tumour, and predominantly capecitabine or
lower-dose infusional 5-FU** (1,181 enrolled, 1,103 evaluable, 85 heterozygous
carriers, 1,018 wild-type; 231/1018 = 22.7% grade ≥3 — arithmetic checked). It is
an excellent number for the patient it describes. It is the wrong number for a
patient receiving 750 mg/m²/day × 5 days plus docetaxel and cisplatin, where
observed rates are ~3× higher (§2).

**`asl` refusal 11 already forbade exactly this** — quoting a comparison group's
rate to a patient outside that group. It was implemented on the **variant** axis
only: a carrier is excluded from the wild-type rate, correctly. Nobody had
applied the same reasoning to the **regimen** axis. The principle was right and
its coverage was partial.

### The fix, and the choice not to invent a number

`Regimen` gains `INDUCTION_TPF`, and `residual.compute()` is restructured so a
regimen with no published comparator **refuses** rather than falling through to
`SYSTEMIC`'s rate.

The tempting fix — quote the Patil figures instead — would repeat the same error
in the opposite direction. **Those are whole-cohort rates, not rates among
panel-negative patients.** They are not a wild-type comparator and cannot be
substituted for one. So the refusal states what is observed on the regimen,
labels it `WHOLE-COHORT`, says explicitly that it is *not* a substitute
comparator, and quotes no figure as one:

```
RATE WITHHELD:
  No wild-type toxicity rate is quoted because none has been published for
  this regimen. Induction docetaxel/cisplatin/5-FU delivers 5-FU at 750
  mg/m2/day by continuous infusion on days 1-5 alongside two other
  cytotoxics, which is not the exposure in either cohort that produced the
  22.7% and 13.6% figures ... Those are WHOLE-COHORT rates, not rates among
  panel-negative patients, so they are not a substitute comparator either
  and no figure is quoted as one here.
```

A missing comparator is reported as missing. That is the honest output, and
"there is no number for you yet, here is why" is more useful to a treating
oncologist than a confident number measured in Utrecht.

Pinned by three new tests, including one that iterates the whole `Regimen` enum
so **adding a member without either a matched rate or a refusal fails the
suite** — the enum can no longer grow a silent default.

---

## 6. What the research says to build next, in priority order

### 6.1 The turnaround constraint is the real product requirement

Patil 2016 could not test upfront because results took 10-14 days, and the FDA's
own carve-out is "unless immediate treatment is necessary". Both point at the
same design requirement, and it is **not** an interpretation requirement:

> A report that arrives after cycle 1 cannot change cycle 1. It can only change
> cycles 2-3 — which is precisely where the 70%→10% mucositis reduction was
> observed.

So the highest-value near-term capability is not a better first-cycle
prediction. It is **making the cycle-2 decision defensible**: capture the
cycle-1 toxicity that actually occurred, alongside genotype and regimen, and
report what that combination does and does not establish. `asl`'s ledger is
already the right shape for this; what it lacks is the *cycle* dimension.

This also reframes the ledger's value. Reactive testing is usually described as
a compromise. In this population it is closer to the observed standard of care,
and the ledger is the only artifact that would let anyone measure whether it
works.

### 6.2 UGT1A1 is a genuine coverage gap, and should not be rushed

The engine has 14 gene callers and **no UGT1A1**, which appears only in
`CPIC_RECOMMENDATION_LEVELS`. Irinotecan is standard in colorectal and small-cell
lung disease, and Indian `*28` frequencies are high — het 43.1%, hom 15.7%
(PMID 33728696, n=102, though this is a single SCLC cohort and should not be
quoted as a national figure).

**But there is no CPIC guideline for UGT1A1-irinotecan.** DPWG has one (70%
starting dose for `*28` homozygotes; no reduction for intermediate
metabolizers). The whole architecture rests on CPIC being the pinned source of
truth, and adding a gene whose recommendation comes from a *different* body is
exactly the kind of undeclared source-mixing that produced the `*6` incident.

Recommendation: **build the caller, defer the recommendation.** A UGT1A1
phenotype with declared DPWG provenance and an explicit "CPIC publishes no
guideline for this pair" statement is honest. Silently presenting DPWG advice in
CPIC's voice is not.

### 6.3 Do not add an Indian TPF rate until one exists

The correct fix for §5 is a wild-type-stratified grade ≥3 rate for induction TPF
in an Indian cohort. No such figure is published. That is a **Phase 6
retrospective output**, and it is now a concrete, answerable question with a
named comparator gap — which is a better ask of a site than "give us your data".

---

## 7. Limitations of this document

- **The regimen reframe is an exposure argument, not an outcome study.** No
  published cohort stratifies TPF toxicity by DPYD panel status in Indians. The
  claim made here is narrow: the published comparators do not describe this
  exposure, therefore they must not be quoted for it. The claim *not* made is
  that DPYD explains the excess.
- **Both Indian TPF sources are single-centre (Tata Memorial) and one is
  toxicity-selected.** The 32.4% DPD figure is a floor in a biased sample and is
  used here only for regimen, dose and direction.
- **The 5-FU spelling defect was found by inspection, not by a systematic sweep.**
  Other drug-name and free-text axes have not been audited the same way. The
  extended review script now makes that audit cheap; it has not been run
  exhaustively.
- **`5-fluoruracil`** (single transposition) is in the synonym table as a
  convenience. It is a misspelling, not a published synonym, and is the one entry
  with no citable provenance.
- **The FDA labeling change is verified from FDA/ASCO/ONS communications and the
  label PDF filename.** The full label text was not read line by line.
- **Nothing here has been reviewed by a clinician.** The engine and package
  remain a research tool, not a diagnostic device.

---

## 8. The through-line, once more

Four sessions of this platform's history now share one shape, and this one adds
two more instances:

| Incident | Genotype wrong? | What was actually wrong |
|---|---|---|
| 0.7.2 DPYD strand | yes | tests encoded the same wrong convention as the table |
| 0.7.2 `*6` function | no | a defensible judgement written into a table with nothing recording why |
| 0.8.1 TPMT inversion | yes | fixtures agreed with the wrong ALT base |
| `pip install asl` | no | every test passed; the wheel shipped no data |
| **0.8.2 `5-FU`** | **no** | **docstring described resolution the code lacked; a contraindication vanished** |
| **`asl` TPF rate** | **no** | **a correct principle applied to only one of its two axes** |

The two new entries are both in the "genotype was right" column, and that is the
point. The engine has been hardened against calling the wrong allele. What
remains are the failures where the allele is right and the *annotation around it*
is wrong or missing — a vanished action, a borrowed rate, a comparator that does
not describe the patient.

And the review that was supposed to catch this could not see the axis it was
reviewing. Which is the most transferable lesson of the day, and one the 0.8.1
document had already written down: **the checks that fail silently are the
dangerous ones.** A wrong answer announces itself. A green review of a field
nobody probed does not.

*The failure is rarely the wrong answer. It is the right answer with its
uncertainty — or its safety annotation — stripped off.*
