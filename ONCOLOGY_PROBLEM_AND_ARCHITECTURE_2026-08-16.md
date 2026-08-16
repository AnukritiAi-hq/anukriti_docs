# Indian Oncology PGx — The Exact Problem, the Solution, and the Architecture
# (2026-08-16)

> **⚠ SUPERSEDED — read `ONCOLOGY_SOLUTION_AND_ARCHITECTURE_2026-08-16.md` instead.**
>
> Two further research passes and direct queries against CPIC's live API
> **falsified four load-bearing claims in this document**. It is kept for the
> audit trail, not as guidance. Specifically wrong here:
>
> - **§4.2** proposes a hand-authored evidence table. CPIC's API **already
>   publishes** `strength`, `findings` (assay type), `citations` and
>   per-population `frequency` per allele. The evidence layer must be
>   *generated*, as `pgx-core` 0.7.2 now generates the DPYD tables themselves.
> - **§1.5** states all four Indian-prevalent alleles rest on Offer 2013/2014
>   HEK293T assays. `*9A` does not: CPIC cites PMID 18452418 (He/Zhang 2008),
>   an *in-vivo* plasma DPD activity study in 142 **Chinese** patients,
>   at strength **Strong**.
> - **§7** calls the Indian evidence base "76 patients from one centre". It is
>   **~630 across four-plus centres**, and the strongest single study is
>   **Pavithran 2021, n=375** (Amrita Kochi), where 32/47 variant-positive
>   patients carried c.496A>G — a CPIC *normal-function* allele — and 35/47
>   had grade II-III toxicity despite dose reduction (p=0.002).
> - **§3.1/§5** conflate panel **sensitivity** (3.5–21.6%, Ontario HTA
>   PMID 34484488) with the **attributable fraction for early-onset toxicity**
>   (20–30%, which is CPIC's own figure). Also: the residual-risk statement is
>   **a CPIC quotation**, not a novel claim — which materially changes the
>   regulatory argument.
> - **§4.5** says NCG "vetted" ABDM-compliant EMR products. NCG **commissioned
>   six new ones** (Pramesh et al., *Bull WHO* 2025;103(5):337-342).
> - **§8** describes the `*6` defect as the engine's only DPYD problem. The real
>   defect was far larger: the allele table's `alt` column was inverting
>   homozygous calls. Fixed and released as `pgx-core` **0.7.2**.
>
> Still correct and carried forward: the problem framing, the three rejected
> solutions (§2), the `U4` precedent, the CDSCO Class A/B reasoning, and the
> D-TORCH Table 4 correction in §1.4.

---

> **Method.** Two research passes (8 parallel investigations) plus four
> verifications run locally: the GenomeIndia supplement read directly, the
> D-TORCH paper read in full, CPIC's live allele API queried, and our own
> `pgx-core` DPYD table diffed against it.
>
> **Reading order.** §1 is the problem. §2 is why the obvious alternatives are
> wrong. §3 is the solution. §4 is the architecture. §5 is what it refuses to do.
> §8 is a defect in our own engine that this research uncovered.
>
> Every number is cited or computed here. Unverified items are marked.

---

## 0. The finding in one paragraph

For an Indian patient, a DPYD test comes back **"Normal Metabolizer — proceed at
full dose" about 96% of the time**, and that result is **falsely reassuring**: in
the only Indian NGS cohort, **55% of CPIC-classified normal metabolizers still
developed grade 2–3 toxicity.** The reason is not that the test is run badly. It
is that the four DPYD variants Indians actually carry are all classified "normal
function" by CPIC, and those classifications rest on **one laboratory's
recombinant-enzyme assays in HEK293T cells** — while for one of them (`*6`)
**more than 3,000 patients of published clinical evidence points the other way.**
The gap is not sequencing capacity, cost, or policy. It is that **the
interpretation layer converts "we found nothing on our list" into "this patient
is normal," and destroys the distinction on the way.** That conversion is a
software behaviour, and it is fixable in software.

---

## 1. The problem, quantified

### 1.1 Scale

| Quantity | Value | Source |
|---|---|---|
| New cancer cases, India | 14,61,427 (2022) | ICMR NCRP, PMID 36510887 |
| Fluoropyrimidine-eligible cancers (breast, oral, colorectal, stomach, oesophagus) | ~500,000/yr | GLOBOCAN 2022 India |
| Receiving 5-FU/capecitabine | **~250,000–350,000/yr (estimate)** | derived; **no Indian utilisation study exists** |
| Grade ≥3 toxicity rate | 10–30% | D-TORCH background; global |
| Treatment-related mortality | 0.5–1% | ibid. |
| **Implied deaths/yr, India** | **~1,500–3,000** | derived from the two rows above |

India has the world's highest oral-cancer burden (143,759 lip/oral cases in
2022), and TPF induction — docetaxel + cisplatin + **5-FU** — is standard for
locally advanced disease. So the exposed population is larger and differently
composed than in Europe.

**Flagged as unverified:** the 250–350k figure is my arithmetic on incidence ×
plausible treatment fractions. No published Indian utilisation study exists.
This number must be labelled an estimate wherever used.

### 1.2 The regulatory asymmetry is now stark

| Authority | Position | Date |
|---|---|---|
| EMA | DPD testing recommended pre-fluoropyrimidine | 2020-04-30 |
| UK MHRA / NHS England | Testing before initiation | 2020-10 |
| **US FDA** | **Boxed warning on capecitabine + 5-FU; test for DPYD before initiating** | **2026-02-05** (verified) |
| **India (CDSCO / ICMR)** | **No mandate, no recommendation, no guideline** | as of 2026-08 |

### 1.3 What actually happens when you do test an Indian patient

The **D-TORCH** study (Baskarane et al., *Front Pharmacol* 17:1732128, 20 Feb
2026; AIIMS New Delhi) is the first NGS-based DPYD study from India. I read it
in full. n=76 whole-exome-sequenced capecitabine patients:

- **54/76 (71%) carried at least one DPYD variant.**
- **Only 3/76 (3.9%) were actionable** under CPIC (intermediate metabolizer).
  **Zero poor metabolizers.**
- The four most frequent variants were **rs1801265 (`*9A`, n=25), rs1801160
  (`*6`, n=13), rs1801159 (`*5`, n=12), rs2297595 (M166V, n=7)** — every one of
  them **"normal function" under CPIC, requiring no dose change.**
- Only **1 patient** carried `*2A`, the workhorse of the European panel.
- **Among the 50 normal metabolizers, 35 (70%) developed grade 2–3 toxicity.**

The authors' own conclusion: *"35 out of 50 patients classified as normal
metabolizer phenotype as per the CPIC guidelines still developed grade 2 or 3
toxicity, emphasizing the limitation of CPIC-based phenotype prediction and dose
adjustment in the Indian population."*

### 1.4 A correction to D-TORCH, found while reading it

**The paper's Table 4 column headers are swapped, and the abstract propagates
the error.** Table 4 is labelled `Variant (n = 22)` and `Wild-type (n = 54)`,
but the text states three times that 54 patients carried variants and 22 were
wild-type. Only one assignment reproduces the paper's own reported odds ratio:

| Assignment | Variant carriers | Wild-type | OR | Matches paper's OR 0.71? |
|---|---|---|---|---|
| Table 4 headers as printed | 14/22 (63.6%) | 30/54 (55.6%) | 1.40 | no |
| Results-text narrative | 36/54 (66.7%) | 14/22 (63.6%) | 1.14 | no |
| **Headers swapped** | **30/54 (55.6%)** | **14/22 (63.6%)** | **0.71** | **yes** |

So the correct reading is **55.6% of variant carriers and 63.6% of wild-type
patients** had grade ≥2 toxicity. The abstract's *"Grade 2 toxicity occurred in
63.6% of variant carriers and 55.6% of wild-type"* is **inverted**, and the
Results narrative's "66.7% (36 patients)" is inconsistent with both.

**This does not weaken the finding — it strengthens the core point.** On the
corrected reading, wild-type patients had *numerically more* toxicity than
variant carriers. DPYD variant status, as currently interpreted, carries
**no useful information** about toxicity risk in this cohort.

Wherever we cite D-TORCH we must cite the corrected numbers and say why.

### 1.5 The root cause: what "normal function" actually rests on

This is the crux, and it is checkable. I queried **CPIC's live API** on
2026-08-16 (`api.cpicpgx.org/v1/allele?genesymbol=eq.DPYD`, 84 alleles):

| Variant | rsID | CPIC clinical function | Activity value |
|---|---|---|---|
| c.85T>C (`*9A`) | rs1801265 | Normal function | 1.0 |
| c.1627A>G (`*5`) | rs1801159 | Normal function | 1.0 |
| **c.2194G>A (`*6`)** | **rs1801160** | **Normal function** | **1.0** |
| c.496A>G (M166V) | rs2297595 | Normal function | 1.0 |
| c.1905+1G>A (`*2A`) | rs3918290 | No function | 0.0 |
| c.2846A>T | rs67376798 | Decreased function | 0.5 |
| HapB3 | rs56038477 | Decreased function | 0.5 |

The evidence under each "normal" call:

- **All four rest primarily on Offer et al. 2013/2014** (*Cancer Res* 73:1958,
  PMID 23328581; 74:2545, PMID 24648345) — **recombinant enzyme activity in
  HEK293T cells.** Not patient outcomes. One laboratory, one assay system.
  `*9A` and M166V were reported *hyperactive* (M166V at 120% of wild-type).
- **`*6` is the one where clinical evidence contradicts the call**, and the
  contradiction is large:
  - **Del Re 2019** (*Pharmacogenomics J* 19:556, PMID 30723313), n=1254:
    c.2194G>A associated with grade ≥3 ADRs, OR 1.7, p<0.001; concludes it
    *"should be evaluated pre-emptively."*
  - **PETACC-8** secondary analysis (Boige 2016, *JAMA Oncol*), n=1545:
    significant association with severe toxicity on FOLFOX4.
  - **TOSCA** (Ruzzo 2017, *Br J Cancer*): significant for time to neutropenia.
  - **Meta-analysis** (Li 2014), 946 CRC patients: bone-marrow suppression
    p<0.001.
  - **Gentile 2016** (PMID 26216193): a three-SNP haplotype of
    **rs1801160 + rs1801265 + rs2297595** — i.e. exactly the three most common
    variants in the Indian cohort — produces a decrease in 5-FU degradation
    *"comparable to that caused by the splice site variant rs3918290"*, the most
    severe loss-of-function allele known.
- **The activity score system itself is unvalidated outside Europeans.** It
  derives from Meulendijks 2015 (PMID 26603945), whose eligibility criteria
  specify **Caucasian patients**. White et al. 2021 (PMID 34916829) reviews the
  ethnic-diversity problem directly.

**So the mechanism of the false reassurance is precise and nameable:** a
population is genotyped for variants defined in another population, scored with
an activity system validated in that other population, using function calls
derived from one in-vitro assay — and the output is a single reassuring word,
"Normal," with none of that context attached.

### 1.6 Why software, and not money or policy

| Barrier | Nature | Software-addressable? |
|---|---|---|
| Test cost ₹13,000–35,000, not reimbursed | money/policy | no |
| 8-day turnaround | logistics | partly (order at biopsy, not at prescription) |
| No CDSCO/ICMR mandate | policy | no |
| Lab capacity | infrastructure | no |
| **"Normal" reported without its evidence basis** | **interpretation** | **yes** |
| **No genotype→outcome data to fix the calls** | **data capture** | **yes** |
| **Panel-negative ≠ low-risk conflation** | **interpretation** | **yes** |

The last three are ours. The first four are not, and we should not pretend
otherwise.

---

## 2. Three tempting solutions that are wrong

**(a) Build an "Indian DPYD activity score."** This is the trap. We do not have
the data — the minimum viable dataset is 500–800 prospectively phenotyped
patients, and the total published Indian NGS evidence is **76 patients from one
centre**. Inventing population-specific activity values from in-silico
predictions would be **precisely the failure this platform already committed and
audited**: the `U4_SAS_DPYD_OVERRIDE` incident, where a hand-written "27%
carrier frequency" citing a real paper ran live for 52 days
(`DPYD_SAS_OVERRIDE_AUDIT_2026-07-28.md`). Doing it again with an activity score
would be the same error in a larger costume.

**(b) Recommend doses.** Under CDSCO's 2026 guidance
(`CDSCO/MD/GD/MDSW/01/2026`), software that *drives* clinical management for a
serious condition is a **Class C medical device** requiring central licensing and
probably clinical investigation. Software that *informs* clinical management is
Class A/B. Dose recommendation crosses that line; evidence presentation does not.

**(c) Expand the panel and call it population-aware.** Adding `*9A`/`*6`/M166V as
*actionable* would be asserting the opposite of CPIC on evidence that is
genuinely contested — three-way contested, in the case of `*9A`
(Hariprakash 2018 vs Naushad 2021 vs Atasilp 2025). The platform's own
resolution of that dispute was to **downgrade a refusal to a named uncertainty
rather than flip to the opposite assertion.** That precedent binds here.

---

## 3. The solution: an evidence-provenance and outcome-capture layer

**Name:** *Anukriti Oncology Safety Ledger* (working name, `asl`).

**One sentence:** It takes a DPYD result and reports **what the result can and
cannot rule out for this patient's population, with the provenance of every
function call attached** — and it captures the toxicity outcome afterwards, so
the calls can eventually be corrected with evidence instead of asserted.

It does two things, and they compound.

### 3.1 Capability A — Evidence-tiered interpretation (replaces "Normal")

Instead of emitting `Normal Metabolizer — standard dose`, it emits the CPIC call
**plus four things CPIC does not carry**:

1. **Provenance of the function call.** For each variant found: what the
   assignment rests on (in-vitro recombinant assay / clinical outcome cohort /
   both), the N, and the ancestry of the cohort. `*6` reads: *"Normal function
   per CPIC (activity 1.0). Basis: recombinant enzyme assay, HEK293T (Offer
   2013, PMID 23328581). Contradicted by clinical cohorts totalling >3,000
   patients (Del Re 2019 n=1254 OR 1.7 p<0.001; PETACC-8 n=1545; Li 2014
   meta-analysis n=946)."*
2. **A named conflict flag** where in-vitro and clinical evidence disagree —
   the existing named-uncertainty mechanism, e.g.
   `P2_DPYD_STAR6_INVITRO_CLINICAL_CONFLICT`.
3. **A haplotype flag.** If `*9A` + `*6` + M166V co-occur, cite Gentile 2016
   (PMID 26216193) and state that this combination has been reported to reduce
   5-FU degradation comparably to `*2A`. **Phase unknown from unphased data —
   so this is a flag, never a call.**
4. **A residual-risk statement instead of an all-clear.** *"No actionable
   variant on the CPIC panel. This excludes approximately 20–30% of severe
   toxicity risk (the panel's published sensitivity). In the only Indian NGS
   cohort, 55% of normal metabolizers experienced grade ≥2 toxicity
   (D-TORCH, n=76, corrected). Panel-negative is not low-risk."*

The clinical action stays CPIC's. What changes is that **the oncologist can see
how much the "normal" is worth.**

### 3.2 Capability B — The outcome ledger (the part that compounds)

The reason nobody can fix the function calls is that **no Indian
genotype→outcome registry exists**, and no international one exists to join —
U-PGx is European-only; there is no DPYD outcomes registry to mirror. India
would have to create one, and the required N (500–800 for OR≥1.8 at ≥5% variant
frequency) is achievable across a handful of NCG centres but not one.

So the ledger records, per patient, the minimum viable schema:

`anonymised_id · cancer_type · drug + regimen · assay method + exact variants
tested (rsIDs) · genotype per variant · starting dose mg/m² · BSA · CTCAE grade
+ type + onset cycle · dose modifications · cycles received`

This is **the same Tier-1 ask already drafted for Malabar Cancer Centre**
(`mcc-visit/03_structured_ask.md`), whose central question is already the right
one: *"How many of your patients had Grade 3+ toxicity while testing negative on
all panel variants?"* The ledger makes that question answerable continuously and
across sites rather than once in a spreadsheet.

At sufficient N, this is submittable to **CPIC's allele-function reassessment
process** (SOP, PMID 41175864) and to **PharmVar** for haplotype registration.
That is the honest route to changing the call for `*6` in the guideline itself —
which is a far larger outcome than changing it in our own table.

### 3.3 Why this is defensible

- **It cannot be scooped by a lab.** OneOme, Helix, MedGenome and the rest sell
  assays. This is the interpretation and evidence layer above the assay, and it
  gets *more* valuable as testing gets cheaper.
- **It is not what GenomeIndia did.** GenomeIndia S13 (read in full, §7 of
  `CLINALITY_DEEP_RESEARCH_2026-08-16.md`) is a population *catalogue*: 9,768
  genomes, 82 populations, per-population frequencies, Fisher's exact tests. It
  has **no patient outcomes at all.** Frequency tells you how many people carry
  an allele; it can never tell you what the allele does.
- **It is not Navya.** Navya (450+ NCG oncologists) decides *what* treatment.
  This is *how safely to dose it*. Adjacent, not competing — and therefore a
  plausible channel.
- **It fits the platform invariant exactly.** The deterministic layer decides;
  the LLM narrates; refusals are named. Adding provenance and a residual-risk
  statement is *more* deterministic, not less.
- **It stays Class A/B** under CDSCO by informing rather than driving.

---

## 4. Architecture

### 4.1 Placement

```
                    ┌──────────────────────────────────────────┐
                    │  anukriti-pgx-core  (v0.7.2 → 0.8.0)     │
                    │  CPIC truth. Zero runtime deps.          │
                    │  NEW: evidence provenance per allele     │
                    └────────────────────┬─────────────────────┘
                                         │ pinned ==
       ┌─────────────────────────────────┼─────────────────────────────┐
       │                                 │                             │
┌──────▼─────────┐            ┌──────────▼──────────┐      ┌───────────▼────────┐
│ anukriti-swarm │            │  asl  (NEW)         │      │ project_astra      │
│ named refusals │◀──flags────│  Oncology Safety    │      │ research side      │
│ P1_/P2_ rules  │            │  Ledger             │      │ (firewalled)       │
└────────────────┘            └──────────┬──────────┘      └────────────────────┘
                                         │
                              ┌──────────▼──────────┐
                              │ anukriti-api        │
                              │ POST /runs/from-pcr │  ← already exists
                              └──────────┬──────────┘
                                         │
                              ┌──────────▼──────────┐
                              │ clinic-facing web   │
                              │ report + ledger UI  │
                              └─────────────────────┘
```

`asl` is a **new repo**, a fifth consumer of `pgx-core`, structured like
`cohortfit` (which is the closest precedent: pure engine + thin API + pinned
fixtures + provenance contract).

### 4.2 New concept in pgx-core: the evidence record

`pgx-core` currently carries `function` per allele and nothing about *why*. The
addition is a sibling table — **additive, no behaviour change**, so it cannot
alter any existing call:

```
DPYD_allele_evidence_v2026.08.tsv
allele  rsid       cpic_function     activity  basis        cohort_n  cohort_ancestry  pmids                  conflict
*6      rs1801160  Normal function   1.0       in_vitro     0         n/a              23328581               clinical_contradicts
*9A     rs1801265  Normal function   1.0       in_vitro     0         n/a              23328581,33491253      haplotype_dependent
M166V   rs2297595  Normal function   1.0       in_vitro     0         n/a              24648345               none
*2A     rs3918290  No function       0.0       both         7365      european         26603945,29152729      none
```

Two hard rules, both enforced as tests:

- **The `cpic_function` column is copied from CPIC, never edited.** A CI job
  diffs it against `api.cpicpgx.org` and fails on drift. This is how the `*6`
  defect in §8 gets caught mechanically rather than by audit.
- **`conflict` and `basis` are additive metadata.** They never feed the activity
  score. Phenotype calling is byte-identical before and after.

### 4.3 `asl` modules

Mirrors the `cohortfit` discipline — pure functions, pinned fixtures,
provenance validated at load, one network-touching script kept separate:

| Module | Responsibility |
|---|---|
| `models` | Types encoding the boundary: `AssayResult`, `EvidenceTier`, `ResidualRisk`, `LedgerEntry`. Extraction/adjudication split as types, per `cohortfit/models.py`. |
| `assay` | What was actually tested. **A panel that never tested a variant is `NOT_TESTED`, never `absent`.** This distinction is the whole product. |
| `interpret` | Only call site into `pgx-core`. Diplotype → phenotype. Never overrides. |
| `evidence` | Loads the evidence table; attaches provenance to each variant. Hard-fails on a row lacking `pmids` + `basis` + `cohort_ancestry`. |
| `residual` | Computes what the panel cannot exclude: published panel sensitivity (20–30%), variants not on this assay, population-specific rate where a citation exists. Emits an interval and a refusal, never a point estimate. |
| `haplotype` | Gentile-2016 co-occurrence flag. Emits `phase_unknown` always, on unphased data. |
| `conflict` | Emits named uncertainties, e.g. `P2_DPYD_STAR6_INVITRO_CLINICAL_CONFLICT`. |
| `ledger` | Outcome capture: append-only, anonymised-ID only, CTCAE-graded. Schema-validated. |
| `report` | Clinician-facing PDF/HTML. Deterministic. Every claim carries a rule ID and PMID. |
| `narrate` | **The only LLM call.** Turns the deterministic record into prose. Cannot alter a call, a grade, or a number. Output validated against the record before display. |
| `api` | FastAPI. `POST /interpret`, `POST /ledger`, `GET /evidence/{gene}`, `GET /health`. |

### 4.4 The data flow, and where refusals fire

```
lab result (PCR panel / NGS VCF)
   │
   ├─ assay.parse ─────────▶ which rsIDs were TESTED? which found?
   │                          ▲ REFUSE if the assay's variant list is unstated
   │                            → "cannot interpret a panel of unknown content"
   │
   ├─ interpret ───────────▶ pgx-core: diplotype → phenotype + activity score
   │                          (CPIC, unmodified)
   │
   ├─ evidence.attach ─────▶ provenance per variant found
   │                          ▲ REFUSE if any variant lacks an evidence row
   │
   ├─ conflict.scan ───────▶ P2_DPYD_STAR6_INVITRO_CLINICAL_CONFLICT
   ├─ haplotype.scan ──────▶ Gentile co-occurrence, phase_unknown
   │
   ├─ residual.compute ────▶ "excludes ~20–30% of risk; panel-negative ≠ low-risk"
   │                          ▲ REFUSE to emit an all-clear. Structurally impossible:
   │                            there is no code path that returns "no risk".
   │
   ├─ report.render ───────▶ deterministic clinical report
   ├─ narrate ─────────────▶ LLM prose, validated against the record
   │
   └─ [weeks later] ledger.record ──▶ CTCAE outcome → the dataset that fixes the calls
```

### 4.5 Deployment, integration, and the constraints that shape them

Grounded in what Indian cancer centres actually run:

- **Year 1: standalone.** Web app, manual entry or CSV, PDF out. No EMR
  integration. This is not a compromise — most centres have no FHIR surface, and
  ABDM has **no pharmacogenomic FHIR profile at all**.
- **Year 2+: FHIR** against the 6 NCG-vetted, ABDM-compliant EMR products
  (Pramesh et al., *Bull WHO* 2025;103(5):337-342) — 20+ early-adopter centres.
- **Channel: NCG-KCDO first.** 360+ centres, ~850,000 new cases/year, an active
  Digital Health Solutions Library, and an existing chemotherapy-management
  platform. **Navya second** — adjacent, not competing.
- **Deploy as `cohortfit` already does:** container on Azure Container Apps.
  **Unlike cohortfit, authentication is mandatory from commit one** — this
  handles patient data, where cohortfit handled only pinned public fixtures.
- **PHI never leaves the site.** Anonymised IDs only, per the MCC MoU outline.

### 4.6 Build order

| Phase | Deliverable | Gate to pass |
|---|---|---|
| 0 | Fix the `*6` defect (§8); add CPIC-drift CI check | `pgx-core` 0.7.2, clinical regression reviewed |
| 1 | `evidence` table for DPYD's 9 panel-relevant alleles | Every row has PMID + basis + ancestry, or the loader fails |
| 2 | `assay` + `residual` — the NOT_TESTED/absent distinction and the no-all-clear guarantee | Property test: no input produces an all-clear |
| 3 | `interpret` + `conflict` + `haplotype`, report, CLI | Byte-identical phenotypes vs `pgx-core` alone on the 1000G fixture |
| 4 | `ledger` + API + auth | Schema validation; no PHI fields accepted |
| 5 | `narrate` | Output validated against record; refuses when record is thin |
| 6 | MCC retrospective run on their ~400–500 PCR-tested patients | The four-quadrant table: PCR± × toxicity± |

Phase 6 is the one that matters. It is already scoped, the site is already
warm (Dr. Deepak Roshan V G, co-author, MoU outline drafted), and it converts
this from architecture into a finding.

---

## 5. What it refuses to do

Stated as hard constraints, because each is a failure mode we can name:

1. **It does not recommend doses.** CPIC's recommendation is displayed as
   CPIC's. Crossing this makes it a Class C device and abandons the
   evidence-layer position.
2. **It does not invent an Indian activity score.** No population-specific
   activity values until the ledger supports them. This is the `U4` lesson.
3. **It does not override CPIC.** Where we disagree, we emit a *named
   uncertainty* alongside the CPIC call — never instead of it.
4. **It does not emit an all-clear.** There is no code path returning "no risk."
   Enforced by property test, not by convention.
5. **It does not treat NOT_TESTED as absent.** A 7-variant PCR panel that did
   not test `*6` reports `*6` as untested.
6. **It does not claim a Bengali or Punjabi frequency.** Per
   `CLINALITY_DEEP_RESEARCH_2026-08-16.md` §6.2 and GenomeIndia's population-61
   counterexample, sub-population numbers here are not trustworthy at the
   available N. Clinality flags mean "needs better data."
7. **It does not let the LLM touch a number.** Narration only, validated.
8. **It does not accept PHI.**

---

## 6. Honest assessment of the wedge

**The counterargument deserves stating plainly: paediatric ALL may be the bigger
problem.** NUDT15 rs116855232 is at **7.89% in GenomeIndia** (verified verbatim
from the supplement: *"GI: 0.0789, Indigen: 0.08, 1KGP3-SAS: 0.0674"*) with
**0.2083 in one Austro-Asiatic tribal population** — roughly **twice** the
actionable DPYD rate, on a **CPIC Level A, uncontroversial** guideline, in
children where treatment-related mortality in India runs ~8% against <2% in
high-income countries. GenomeIndia's own S13 says this *"warrants targeted
intervention for specific pharmacotherapy in a population-specific manner."*

**I still recommend DPYD first, for four reasons:**

1. **The architecture is the product, and DPYD is where it is provable.** The
   thing being built is an evidence-provenance layer. DPYD is the gene where the
   provenance defect is documented, quantified, and published (D-TORCH). NUDT15
   has the opposite problem — the guideline is *right*, it is simply not being
   followed. That is an access problem, not an interpretation problem, and
   software is the wrong tool for it.
2. **We already have the engine, the workflow, and the site.** DPYD is live in
   `pgx-core`, validated 7/7 against Ho 2025, wired through the API's
   `from-pcr` path, and MCC is a warm site with ~400–500 tested patients and
   toxicity follow-up.
3. **Regulatory tailwind.** The FDA boxed warning (2026-02-05) makes this the
   moment India's gap is most visible.
4. **NUDT15 is the second workflow, not a different product.** The same evidence
   layer serves it — and the same argument applies, since European TPMT-only
   testing misses the gene that actually matters in India (TPMT ~4.6% vs NUDT15
   ~16.5% pooled South Asian).

**What would change my mind:** if MCC's retrospective shows *no* excess
panel-negative toxicity, the premise weakens and paediatric ALL becomes the
better first target. Phase 6 is therefore a genuine go/no-go, not a
confirmation exercise.

---

## 7. Limitations of this analysis

- **The ~250–350k patient estimate is mine, not published.** Must always be
  labelled as such.
- **D-TORCH is n=76, single-centre, and 29% of its parent cohort** — the authors
  call it exploratory and hypothesis-generating. It is the best Indian NGS
  evidence and it is thin. The entire problem statement rests substantially on
  one small study whose own tables I had to correct.
- **The 20–30% panel sensitivity figure** comes from a review (MDPI
  *Pharmaceutics* 2021;13(12):2036) reported via research pass, not read
  primary. **Must be read before it ships in a clinical report.**
- **`*6` reclassification is my reading of the literature, not a guideline
  position.** CPIC has not moved. We surface the conflict; we do not resolve it.
- **Plasma-uracil phenotyping is the strongest population-agnostic alternative**
  (measures enzyme activity, not genotype) and I am *not* proposing it, because
  no Indian lab offers it and its 16 ng/mL threshold is unvalidated outside
  French cohorts. If a partner site has LC-MS/MS, this ranking should be
  revisited.
- **No validated multi-gene fluoropyrimidine toxicity score exists** in any
  guideline. TYMS/MTHFR/CDA have real effect sizes (Loganayagam 2013: TYMS
  3'UTR del/del OR 3.08; MTHFR 1298CC OR 9.99 for HFS in capecitabine) but
  adding them to clinical variables moved AUC only 0.72 → 0.74. We must not
  imply a polygenic score is available.
- **Unverified:** KCDO's "Chemotherapy Management Platform" capabilities (won an
  iF Design Award 2026, no public product documentation). Could be competitor or
  channel. Highest-value unknown in §4.5.
- **Unverified:** whether any NCG guideline mentions DPYD or PGx at all. Found
  nothing; absence not proven.
- Research breadth came from sub-agents. Where their numbers conflicted with
  primary sources I read myself (the 0.30/0.55 CYP2D6 estimate; the D-TORCH
  toxicity percentages), the primary source won and the discrepancy is recorded.

---

## 8. A defect in our own engine, found by this research

Diffing `pgx-core`'s DPYD table against CPIC's live API on 2026-08-16 — 9
panel-relevant alleles — gives **8 matches and one mismatch**:

| Allele | rsID | anukriti-pgx-core | CPIC live | |
|---|---|---|---|---|
| `*6` | rs1801160 | **Decreased function** | **Normal function** | **MISMATCH** |
| `*2A`, `*4`, `*5`, `*9A`, `*13`, c.2846A>T, HapB3, M166V | — | — | — | match |

This was already on the platform's open-items list from 2026-08-08 as an error
to fix. **The research changes its character.** Our `*6` = Decreased is
*defensible on the clinical evidence* — Del Re 2019, PETACC-8, TOSCA and the Li
meta-analysis all support it, and it is arguably ahead of CPIC.

**It is still a defect, and it must be fixed, for a reason that matters more than
being right:** it is an **undeclared deviation from the pinned source of truth.**
The platform's central claim is that CPIC is copied, not edited. A silent
one-word difference in a TSV — with no provenance, no rule ID, no flag — is the
same class of failure as the 52-day `U4` incident: a defensible clinical
intuition written directly into a data table with nothing recording why.

**The fix is not to change the word back and lose the insight.** It is:

1. Set `cpic_function` = `Normal function` for `*6`, matching CPIC exactly.
2. Record the clinical contradiction in the **evidence table** with its four
   PMIDs and cohort sizes.
3. Emit `P2_DPYD_STAR6_INVITRO_CLINICAL_CONFLICT` as a named uncertainty.
4. Add the CPIC-drift CI check so the next such deviation fails a build instead
   of surviving to an audit.

**This is the entire thesis in miniature, inside our own repository.** The
disagreement with CPIC was real and evidence-backed; the failure was that it was
invisible. That is exactly what `asl` exists to prevent — for `*6`, and for
every patient whose "Normal" carries more uncertainty than the word admits.

---

## 9. Immediate next actions

1. **Fix `*6`** per §8, with clinical regression review → `pgx-core` 0.7.2.
   Also still open from the 08-08 list: `*10` mapped to `rs1801266` (which is
   `*8`), and the duplicate `c.1679T>G` row.
2. **Add the CPIC-drift CI check.** Cheap, mechanical, prevents recurrence.
3. **Read the panel-sensitivity primary source** before the 20–30% figure ships.
4. **Correct `DPYD_ONCOLOGY_DEEP_DIVE.md`** — it still asserts the refuted "27%
   South Indian `*9A`" claim and describes `U4` as a live feature.
5. **Re-cite D-TORCH correctly** wherever used, with the §1.4 correction.
6. **Scope `asl` Phase 0–2.**
7. **Reactivate MCC** for the Phase 6 retrospective. This is the go/no-go.
