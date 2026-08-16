# Indian Oncology PGx — Corrected Problem, Solution, and Architecture
# (2026-08-16, supersedes ONCOLOGY_PROBLEM_AND_ARCHITECTURE_2026-08-16.md)

> **Why this document replaces the earlier one.** The 08:29 document
> (`ONCOLOGY_PROBLEM_AND_ARCHITECTURE_2026-08-16.md`) was written from two
> research passes. A third and fourth pass, plus direct queries against CPIC's
> live API, **falsified four of its load-bearing claims and strengthened three
> others**. The architecture changes as a result: the central data artifact it
> proposed to hand-author is already published machine-readable by CPIC.
>
> Corrections are listed in §1 before anything is built on them. Every number
> here is either computed locally (and the command is stated) or carries a PMID.
> Unverified items are marked **UNVERIFIED** inline, not relegated to a footnote.

---

## 0. The finding in one paragraph

For an Indian patient, a guideline-conformant DPYD test reports **"Normal
Metabolizer — proceed at full dose" for 95.0% of patients** (computed from
CPIC's own Central/South Asian allele frequencies under Hardy-Weinberg), and
that result is **falsely reassuring**. The four DPYD alleles Indians actually
carry sum to **52.9% allele frequency — 20.9× the actionable panel's 2.5%** —
and all four are classified "Normal function" by CPIC. **77.8% of Indian
patients carry at least one of them**; the only Indian NGS cohort observed 71%
(54/76, D-TORCH), which is independent corroboration of that arithmetic. The
gap is not sequencing capacity, cost, or policy. It is that **the interpretation
layer converts "we found nothing on our list" into "this patient is normal", and
destroys the distinction on the way.** CPIC itself says the test cannot do that.
The conversion is a software behaviour, and it is fixable in software.

---

## 1. Corrections to the 08:29 document

Listed first because the rest of this document depends on them.

### C1 — CPIC already publishes machine-readable evidence provenance (**decisive**)

The 08:29 document's §4.2 proposed a hand-authored
`DPYD_allele_evidence_v2026.08.tsv` carrying `basis`, `cohort_n`,
`cohort_ancestry`, `pmids`. **A hand-authored evidence table is the wrong
design, because CPIC's live API already exposes most of it.**

Verified by direct query on 2026-08-16:

```
curl -s "https://api.cpicpgx.org/v1/allele?genesymbol=eq.DPYD"
```

Every allele row carries:

| Field | Content | Example (`*6`) |
|---|---|---|
| `clinicalfunctionalstatus` | the phenotype-driving call | `Normal function` |
| `functionalstatus` | **biochemical** status, may differ | `Normal function` |
| `activityvalue` | activity score contribution | `1.0` |
| `strength` | `Definitive`/`Strong`/`Moderate`/`Limited` | `Moderate` |
| `findings` | **encodes assay type and substrate** | `5-fluorouracil (in vitro)` |
| `citations` | PMIDs | `["23328581"]` |
| `frequency` | per-population, incl. `Central/South Asian` | `0.09506` |

Across DPYD's **84 alleles**: `strength` is populated for 83 (Limited 62,
Moderate 15, Strong 6, null 1); `findings` is populated for **all 84**; and
`functionalstatus` differs from `clinicalfunctionalstatus` for **0** of them.

**Consequences for the design:**

1. The evidence layer is **generated, not authored** — same discipline
   `pgx-core` 0.7.2 now applies to the DPYD allele table itself
   (`scripts/regen_dpyd_tables.py`, with `--check` gated in CI).
2. `findings` is the field that distinguishes in-vitro from in-vivo evidence.
   It is free text, so parsing it is a **classification with a fallback**, never
   a silent guess — an unrecognised `findings` string must degrade to
   `basis=unclassified`, not to `in_vitro`.
3. What CPIC does **not** publish, and therefore what remains genuinely ours:
   cohort N, cohort ancestry, and any flag for in-vitro/clinical disagreement.
   Those three fields are the real delta, and they are small.
4. **The competitive risk is now explicit:** CPIC could add ancestry and N to
   its API at any time. The moat is not the evidence table. It is §3.2 and §3.3.

### C2 — The "one lab's HEK293T assays" claim is wrong for `*9A`

The 08:29 document §1.5 stated all four Indian-prevalent alleles rest primarily
on Offer 2013/2014 recombinant HEK293T assays. CPIC's own metadata contradicts
this for the most common one:

| Allele | CSA freq | `strength` | `findings` | Citation |
|---|---|---|---|---|
| `*9A` c.85T>C | **0.25526** | **Strong** | **`Dihydrouracil (in vivo)`** | **18452418** |
| `*6` c.2194G>A | 0.09506 | Moderate | `5-fluorouracil (in vitro)` | 23328581 (Offer 2013) |
| `*5` c.1627A>G | 0.09373 | Strong | `5-fluorouracil (in vitro)` | 23328581 (Offer 2013) |
| M166V c.496A>G | 0.08517 | Moderate | `5-fluorouracil (in vitro)` | 24648345 (Offer 2014) |

PMID 18452418 is **He/Zhang 2008**, *J Clin Pharm Ther* 33:307-314 — n=142
**Chinese** cancer patients, plasma DPD activity measured directly, finding **no
correlation** between `*9A` and DPD activity. So `*9A`'s "Normal function" call
rests on an *in-vivo* study in an East Asian population, not on in-vitro work.

**This is a better argument than the one it replaces, not a worse one.** The
objection is no longer "the evidence is in-vitro"; it is **"the evidence is
in a different population, and the effect is now known to be
haplotype-dependent"** (C4). It also means the report must state the evidence
type *per allele from CPIC's own field* rather than asserting a blanket claim
we would have to defend.

### C3 — The scale of the mismatch is computable from CPIC alone

Computed from the `frequency` field above under Hardy-Weinberg:

| Quantity | Value |
|---|---|
| Actionable panel allele frequency, CSA (`*2A` + `*13` + c.2846A>T + HapB3) | **0.02538** |
| ⤷ `*13` alone, CSA | **0.00000** (zero) |
| P(no actionable allele) = (1 − 0.02538)² | **0.94989 → 95.0% report "Normal"** |
| The four "Normal function" alleles Indians carry, summed | **0.52921** |
| Ratio | **20.9×** |
| P(carries ≥1 of those four) = 1 − (1 − 0.52921)² | **0.7784 → 77.8%** |
| D-TORCH **observed** carrier rate (n=76, AIIMS) | **71.1% (54/76)** |

The last two rows are the strongest single result in this document: an
expectation derived purely from **CPIC's own published frequencies** lands
within 7 points of what the only Indian NGS cohort measured. The problem is not
a claim requiring Indian data to establish — **it is derivable from the
guideline's own reference tables**, and Indian data confirms it.

For contrast, the same panel in Europeans: `*13` is present (0.00056) and
c.2846A>T is 5.8× more frequent (0.00374 vs 0.00064). The panel was built where
its variants exist.

### C4 — The Indian evidence base is larger than 76 patients, but mostly toxicity-selected

> **⚠ Materially qualified by C12 (§10). Read both.** Two of the five studies
> below tested *only* patients who had already developed grade 3+ toxicity, so
> the pooled figure below cannot support a prevalence or association claim. The
> defensible statement is **~451 patients across two centres genotyped without
> toxicity selection** — and of those two, the methodologically stronger one
> found **no** association.

The 08:29 document called this its own biggest weakness ("the entire problem
statement rests substantially on one small study"). That was too pessimistic
about the volume, but its caution about strength was warranted.

| Study | PMID / ref | Centre | n | Variants tested | Toxicity data |
|---|---|---|---|---|---|
| Patil 2016 | 28032083 | Tata Memorial | 12 | rs1801160, rs1801265, rs2297595 | yes (grade 3 selected) |
| Sahu 2016 | 27284470 | Tata Memorial | 22 | rs1801265, rs2297595, rs1801160 | yes (grade 3 selected) |
| Varma 2020 | 32966231 | JIPMER | 145 | `*9A` + 5-FU PK (LC-MS/MS) | yes |
| **Pavithran 2021** | ASCO *JCO* 39:e15517 | **Amrita, Kochi** | **375** | `*2A`, `*13`, c.2846A>T, **c.496A>G** | **yes** |
| D-TORCH / Baskarane 2026 | *Front Pharmacol* 17:1732128 | AIIMS Delhi | 76 | WES (all DPYD) | yes |
| Patil 2019 | *Clin Oncol* 31:732-733 | Tata Memorial | 1064 | rs1801160, rs1801159 | **no** — genotype only |

**Pavithran 2021 is the most important find of this research pass.** n=375 South
Indian patients, 5× D-TORCH. 47/375 (12.5%) were variant-positive; of those,
**32 (68.8%) carried c.496A>G / rs2297595 — a CPIC *normal-function* allele** —
and **35/47 had grade II-III toxicity even after dose reduction**, where the
dose reduction was **pre-emptive and activity-score-guided** (C11). Verified
against the primary abstract.

**But it is abstract-only, its headline statistic is ambiguous, and D-TORCH
contradicts its central allele finding** — rs2297595 appeared in 7/76 D-TORCH
patients with no toxicity signal, and D-TORCH found no association overall
(OR 0.71, p=0.612). See C11 and C12. **c.496A>G is contested, not established**,
and `asl` must present it that way.

Genotype-only evidence adds 1064 more patients (Patil 2019, 27.2% carrying
rs1801160/rs1801159), useful for frequency but silent on outcome.

Separately, and unaffected by the selection bias: both Tata Memorial studies
report that **cycle-2 dose reduction cut grade 3–4 mucositis from 70% to 10%
(p=0.02, Patil 2016) and 71% to 24% (p=0.016, Sahu 2016)**, with diarrhoea
88% → 36% (p=0.006). That is a dose-response observation rather than a
genotype-prediction one.

### C5 — The residual-risk statement is a CPIC quotation, not our novel claim

This is the single most valuable correction for regulatory posture. The CPIC
DPYD guideline (Amstutz 2018, PMID 29152729) states **verbatim**:

> "By combining the DPYD variants c.1905+1G>A, c.2846A>T, c.1679T>G,
> c.1129–5923C>G, **20–30% of early-onset 5-fluorouracil toxicities can be
> explained.**"

> "**patients without a DPYD decreased/no function variant may still experience
> severe toxicity** due to other genetic, environmental or other factors."

> "**a genetic test investigating only selected decreased/no function variants
> does not fully rule out DPD defects.**"

So the product's core safety message is **CPIC's own text**, displayed. We are
not asserting something against the guideline; we are refusing to discard a
caveat the guideline already publishes. Under CDSCO that is squarely
"informs clinical management"; under FDA's 21st Century Cures §520(o)(1)(E) it
supports the non-device CDS position (§6).

**Three quantities the 08:29 document conflated, now separated:**

| Quantity | Value | Source |
|---|---|---|
| (a) clinical **sensitivity** of the 4-variant panel for grade ≥3 | **3.5%–21.6%** across 9 studies; **7.1%** most representative (Lunenburg 2018, 4 variants) | Ontario HTA, PMID 34484488 / PMC8382304 |
| (b) **attributable fraction** for **early-onset** toxicity | **20–30%** | CPIC quote above, citing Froehlich 2015 (PMID 24923815) |
| (c) toxicity **reduction** from genotype-guided dosing | different quantity again; Ontario HTA rates it **very low** certainty | ibid. |

The Ontario HTA computed **no pooled sensitivity** — only a range. Specificity
is 95–100%. Using (b) where (a) is meant overstates the panel roughly threefold.

**The number that actually belongs in a patient report** is neither: it is the
grade ≥3 toxicity rate *among wild-type patients*.

| Study | Wild-type grade ≥3 | Setting |
|---|---|---|
| Henricks 2018, PMID 30348537 | **231/1018 = 22.7%** | prospective, systemic chemo |
| Lunenburg 2018, PMID 30361102 | **105/771 = 13.6%** | includes chemoradiation (lower FP dose) |
| Ontario HTA range, 7 studies | **8.2%–41.5%** | mixed regimens |

**The regimen determines which denominator applies.** A report that prints one
number without the regimen is wrong; this is a design constraint, not a caveat
(§4.4, `residual`).

### C6 — Gentile 2016 is weaker than the 08:29 document implied

Verified: PMID 26216193, Gentile et al., *Pharmacogenomics J* 2016;16(4):320-325.

- It is an **ex-vivo 5-FU degradation-rate (5-FUDR) assay in patient PBMCs**,
  n≈94 Italian patients. **Not clinical toxicity.**
- The "Hap7" claim (rs1801160 + rs1801265 + rs2297595 reduces 5-FUDR comparably
  to rs3918290) **is real**, but it is a *degradation-rate* claim, not an
  equivalent-toxicity-risk claim. The 08:29 document blurred that.
- **Not replicated clinically.** Kanai 2022 (PMID 36524458), n=1364 Japanese
  GWAS: **no** toxicity association for rs1801265 — in fact OR 0.53 for
  neutropenia, *trending protective*, p=0.054. TOSCA (Ruzzo 2017) also null for
  these variants individually.
- **Partially supported mechanistically** by Hamzic 2021 (PMID 33491253),
  n=1382 across four European cohorts, plasma UH₂/U ratios: the effects of
  c.85T>C and c.496A>G on DPD activity are **haplotype-dependent**.

So the haplotype flag survives, but its wording must change: it is an
**ex-vivo/phenotype signal with a haplotype-dependence mechanism and an explicit
clinical non-replication note**. Never "comparable risk to `*2A`".

Also corrected: **Hariprakash 2018** (PMID 29239269) is population-genomics/
in-silico on ~3000 South Asians (validated in 110 Indian patients for
*frequencies*, not toxicity), and **Naushad 2021** (PMID 33105068) is a
2000-subject array + in-silico study. Neither is a clinical toxicity study. The
08:29 document described a "three-way clinical dispute" over `*9A` that, on
inspection, is not clinical on two of its three sides.

### C7 — Regulatory position verified; one correction

- **`CDSCO/MD/GD/MDSW/01/2026` is real**: "Guidance Document on Medical Device
  Software under MDR 2017", draft 21 Oct 2025, **final 21 Jul 2026**. Its
  classification matrix is (software function × condition seriousness):
  *informs* + serious = **Class A**; *informs* + critical = **Class B**;
  *drives* + serious = Class B; *treatment/diagnosis* + serious = Class C.
  Our Class A/B read was right — **but even Class A requires registration under
  Chapter IIIB of MDR 2017.** It is not exempt. The 08:29 document implied
  otherwise.
- **DPDP Act 2023**: Rules notified **13 Nov 2025**, full enforcement
  **13 May 2027**. No special category for genetic/health data (unlike GDPR),
  but explicit consent is mandatory, breach notification is 72h, there is no
  blanket localisation requirement, s.17(2)(b) provides a research exemption,
  and truly anonymised data is out of scope.
- **ICMR 2017**: IEC approval required **per site**; Ch.9 requires specific
  consent for genetic research; Ch.10 governs biobanking.
- **ABDM/FHIR**: confirmed — the NRCeS India FHIR IG has **no pharmacogenomics
  or genomics profile**. Generic `DiagnosticReport`/`Observation` only.
- **NCG correction**: Pramesh et al., *Bull WHO* 2025;103(5):337-342
  (PMID 40342845, PMC12057217) describes NCG **commissioning six new EMR
  products** (17 bids, 13 shortlisted, 216 requirements, silver/gold/platinum
  tiers, 20+ centres supported). The 08:29 document said "NCG-vetted existing
  products" — that is an overstatement.
- **KCDO's Chemotherapy Management Platform exists** (iF Design Award, 26 Feb
  2026) and is **KCDO's own tool** — therefore a **channel, not a competitor**.
  The concrete entry mechanism is the **Digital Health Solutions Library**
  (`ncgindia.org/digitalhealthsolutionlibrary`), which openly invites vendors.

### C8 — The utilisation figure remains unpublished

Exhaustive search confirms **no Indian fluoropyrimidine utilisation study
exists**. The 250,000–350,000/yr figure stays labelled **author-derived
arithmetic**. Anchors that *are* published: ICMR NCRP 2022 (PMID 36510887) total
1,461,427 incident cancers; breast 221,757; oral cavity + pharynx 198,438;
oesophagus 55,572; stomach 52,706; colorectal ~64,863 (GLOBOCAN 2022).
DPYD testing in India costs **₹5,000–35,000** and is **not covered by PM-JAY or
any state scheme**.

### C9 — Wedge choice re-tested and upheld, with a caveat

DPYD stays first, on volume (~150–200k exposed/yr vs ~15–20k paediatric ALL,
roughly 10×) **and** because the interpretation defect is documented. But the
honest framing is sharper than the 08:29 document's:

- **NUDT15/thiopurines in paediatric ALL is more severe per patient** and is an
  **access** problem, not an interpretation one: CPIC Level A, all
  recommendations "Strong", carrier rate 9–17% in Indian cohorts,
  ICiCLe-ALL-14 (n=2505) treatment-related mortality **8% overall** with
  induction TRM 3.5–5% against <1% in high-income countries.
- **UGT1A1** is a genuine interpretation trap we should note but not lead with:
  `*28` runs ~35% allele frequency in Indians (*higher* than East Asians) while
  `*6` is essentially **absent** — so East-Asian-derived algorithms that weight
  `*6` are simply wrong for India. CPIC Level B; weakest Indian evidence.

### C10 — Competitive position: the moat is not the evidence table

No product does all of: per-allele evidence provenance surfaced to the
clinician, in-vitro/clinical disagreement flags, an explicit residual-risk
statement, and an outcome registry. PharmCAT, OneOme, GeneSight, Genomind,
Sequence2Script and Epic's Genomics module all report phenotype + recommendation
with **no** evidence provenance and **no** residual risk. Translational Software
("provenance" = guideline-source traceability and content versioning) and
SignalPGx (launched Aug 2026) are closest in philosophy. Coriell's PhAESIS
(2013) is prior art for PGx evidence scoring, but as a research tool.

**No PGx outcome registry is open to Indian sites** — U-PGx/PREPARE is EU-only,
IGNITE and eMERGE are US-only, and PvPI does not link genotype to ADR reports.

Given C1, the defensible moat is **the residual-risk computation (§3.2) and the
outcome ledger (§3.3)** — not the evidence table.

---

## 2. The problem, restated precisely

### 2.1 What happens to an Indian patient today

1. Oncologist prescribes capecitabine or 5-FU. In most Indian centres, **no
   DPYD test is ordered** — there is no CDSCO or ICMR mandate, and the test
   costs ₹5,000–35,000 out of pocket (C8).
2. If a test *is* ordered, it is a PCR panel of the four CPIC variants — the
   variants defined where they exist, which is Europe.
3. **95.0% of the time it returns "Normal Metabolizer — standard dose"** (C3).
4. That patient nonetheless has a **13.6%–22.7% chance of grade ≥3 toxicity**
   depending on regimen (C5), and a **77.8% chance of carrying at least one
   DPYD allele CPIC calls "Normal function"** whose evidence base is either
   in-vitro, or in-vivo in a different population, or haplotype-dependent (C2,
   C4, C6).
5. The report says none of this. The word "Normal" arrives with its uncertainty
   stripped off.

### 2.2 The failure is a conversion, and it is nameable

```
  what the assay established        what the report says
  ─────────────────────────────     ────────────────────────
  "none of these 4 variants          "Normal Metabolizer"
   were detected"                    "proceed at standard dose"
                              ⇒
  ┌─ information silently discarded in that arrow ─────────────┐
  │ • which variants were actually tested (vs not tested)      │
  │ • that the panel's sensitivity is 3.5–21.6%                │
  │ • that 13.6–22.7% of wild-type patients still toxify       │
  │ • that CPIC itself says this does not rule out DPD defect  │
  │ • that the alleles this patient DOES carry rest on         │
  │   evidence from other populations                          │
  └────────────────────────────────────────────────────────────┘
```

Every item in that box is **published, citable, and machine-readable**. None of
it requires new science. It requires not throwing it away.

### 2.3 Which parts are ours to fix

| Barrier | Nature | Ours? |
|---|---|---|
| Test costs ₹5,000–35,000, not reimbursed | policy/economics | no |
| No CDSCO/ICMR mandate | policy | no |
| Lab capacity, turnaround | infrastructure | no |
| **Panel-negative reported as an all-clear** | **interpretation** | **yes** |
| **Evidence basis discarded before the clinician sees it** | **interpretation** | **yes** |
| **NOT_TESTED indistinguishable from absent** | **interpretation** | **yes** |
| **No genotype→outcome data to correct the calls** | **data capture** | **yes** |

Four of seven. We should not pretend about the other three.

---

## 3. The solution

**Name:** *Anukriti Oncology Safety Ledger* (`asl`).

**One sentence:** It reports what a pharmacogenomic result **can and cannot rule
out for this patient's population, with the provenance and strength of every
allele-function call attached** — and it captures the toxicity outcome
afterwards, so the calls can eventually be corrected with evidence rather than
asserted.

Three capabilities, in ascending order of defensibility.

### 3.1 Capability A — Evidence-attributed interpretation (generated, not authored)

Instead of `Normal Metabolizer — standard dose`, the report carries the CPIC call
**plus** four things CPIC publishes but no product surfaces:

1. **Per-allele provenance, generated from CPIC.** For each allele found, the
   `strength`, the `findings` string (which encodes assay type and substrate),
   and the citation PMIDs — read from the API, never retyped. For `*9A`:
   *"Normal function per CPIC (activity 1.0). Evidence strength: Strong. Basis:
   dihydrouracil, in vivo (CPIC `findings`). Citation: PMID 18452418 — He/Zhang
   2008, n=142 Chinese cancer patients, plasma DPD activity, no correlation with
   `*9A` found."*
2. **Population context, from CPIC's own `frequency` field.** `*9A` is at
   **0.25526 in Central/South Asian** — the most common DPYD allele in this
   population — against an actionable panel summing to **0.02538**.
3. **A named conflict flag** where in-vitro and clinical evidence diverge, e.g.
   `P2_DPYD_STAR6_INVITRO_CLINICAL_CONFLICT` for `*6` (CPIC: Normal function,
   Moderate, in-vitro; against Del Re 2019 n=1254 OR 1.7 p<0.001, PETACC-8
   n=1545, TOSCA, Li 2014 n=946). **This is the field CPIC does not publish**,
   and it is one of only three that are genuinely ours (C1).
4. **A haplotype flag, correctly hedged.** If `*9A` + `*6` + M166V co-occur:
   cite Gentile 2016 as an **ex-vivo PBMC degradation-rate** finding, note
   Hamzic 2021's haplotype-dependence mechanism, **and state the clinical
   non-replication** (Kanai 2022, n=1364, no association; TOSCA null). Phase is
   unknown from unphased data, so this is a flag, never a call (C6).

The clinical action stays CPIC's, attributed to CPIC. What changes is that the
oncologist can see **how much the word "Normal" is worth for this patient**.

### 3.2 Capability B — The residual-risk computation (first real moat)

This is what no PGx product does. It emits, for a panel-negative result, a
statement of what remains unexcluded — assembled from published numbers, keyed
to the patient's actual regimen:

> **No actionable variant detected** among the four tested (`*2A`, `*13`,
> c.2846A>T, HapB3).
>
> This does **not** exclude severe toxicity risk. CPIC states that "patients
> without a DPYD decreased/no function variant may still experience severe
> toxicity" and that such a test "does not fully rule out DPD defects"
> (Amstutz 2018, PMID 29152729).
>
> In prospective cohorts on **systemic fluoropyrimidine chemotherapy**,
> **22.7% (231/1018)** of patients without these variants still experienced
> grade ≥3 toxicity (Henricks 2018, PMID 30348537). *[Regimen-matched: this
> patient is on CAPOX, systemic.]*
>
> The panel's clinical sensitivity for grade ≥3 toxicity is **3.5–21.6%**
> (Ontario HTA 2021, PMID 34484488).
>
> **Population note.** In CPIC's Central/South Asian reference data, the four
> tested variants sum to 2.5% allele frequency, while four alleles CPIC
> classifies "Normal function" sum to 52.9%. This patient carries **`*9A`/`*9A`
> and `*6`/`*1`**. See per-allele evidence above.

Four design rules make this defensible rather than alarming:

- **Regimen-keyed denominators.** 22.7% (systemic) and 13.6% (chemoradiation)
  are different populations. The report picks by regimen or **refuses** to
  quote a rate (C5).
- **Interval, never point estimate**, wherever the literature gives a range.
- **Quote CPIC for the qualitative claim** so the novel-assertion surface is
  as small as possible (C5).
- **No code path returns "no risk".** Enforced by property test (§5.4).

### 3.3 Capability C — The outcome ledger (second real moat, and the compounding one)

No genotype→outcome registry is open to Indian sites (C10). So `asl` records,
per consented patient, append-only:

```
anonymised_id · cancer_type · regimen + drug · assay method
· exact rsIDs TESTED (not just those found) · genotype per rsID
· starting dose mg/m² · BSA · CTCAE grade + type + onset cycle
· dose modifications · cycles received · outcome timestamp
```

`rsIDs TESTED` is the field that makes the dataset scientifically usable and is
exactly what published Indian studies omit — it is why Patil 2019's 1064
patients cannot answer the question their genotypes were collected for.

**Where it goes.** At sufficient N, published, then submitted to **CPIC's PCEP
reassessment process** (Tibben 2025, PMID 41175864; SOP at cpicpgx.org;
requires published literature; tiers Definitive/Strong/Moderate/Limited; 70%
consensus vote), to **PharmVar** for haplotype registration (needs ~2kb upstream
+ 250bp downstream sequence), and to **ClinPGx/PharmGKB**, which accepts primary
data submissions. **PvPI is not a route** — it has no genotype field and handles
individual ICSRs, not registries (C7).

That is the honest path to changing the call for `*6` or c.496A>G **in the
guideline itself**, which is a far larger outcome than changing it in our table —
and, per the 0.7.2 release, changing it in our table unilaterally is precisely
what we now forbid ourselves.

### 3.4 Why this is defensible

- **Not scoopable by a lab.** MedGenome, Strand, Mapmygenome and the rest sell
  assays. This is the interpretation layer above the assay, and it gets *more*
  valuable as sequencing gets cheaper.
- **Not GenomeIndia.** GenomeIndia is a population *catalogue* with **no patient
  outcomes**. Frequency tells you how many people carry an allele; it can never
  tell you what the allele does.
- **Not Navya.** Navya decides *what* treatment. This is *how safely to dose it*.
  Adjacent — therefore a plausible channel.
- **Fits the platform invariant exactly.** Deterministic layer decides, LLM
  narrates, refusals are named. Adding provenance and residual risk makes the
  system *more* deterministic, not less.
- **Regulatory posture is quotation, not assertion** (C5), which is what keeps
  it "informs clinical management" (§6).

---

## 4. Architecture

### 4.1 Placement

`asl` is a **new repo** and the **sixth consumer** of `pgx-core`, structured like
`cohortfit` — the closest precedent: pure engine, thin API, pinned fixtures,
provenance validated at load, one network-touching script kept separate.

```
                  ┌────────────────────────────────────────────┐
                  │ anukriti-pgx-core ==0.7.2  (exact pin)     │
                  │ CPIC truth, 13 genes, zero runtime deps    │
                  │ DPYD tables GENERATED from CPIC + CI drift │
                  └──────────────────┬─────────────────────────┘
                                     │
   ┌──────────────┬──────────────────┼───────────────┬──────────────────┐
   │              │                  │               │                  │
┌──▼─────────┐ ┌──▼───────────┐ ┌────▼────────┐ ┌────▼──────┐ ┌─────────▼──────┐
│anukriti-api│ │anukriti-swarm│ │  asl  (NEW) │ │ cohortfit │ │ anukriti,      │
│14 routers  │ │named refusals│ │  Oncology   │ │  cohort   │ │ validation-iwpc│
│            │◄┤P1_/P2_ rules │◄┤Safety Ledger│ │  fit      │ │  (sandboxes)   │
└──┬─────────┘ └──────────────┘ └────┬────────┘ └───────────┘ └────────────────┘
   │                                 │
┌──▼──────────┐            ┌─────────▼───────────────────────────┐
│anukriti-main│            │ evidence/  (generated from CPIC API)│
│  Vercel     │            │ ledger/    (append-only, consented) │
└─────────────┘            └─────────────────────────────────────┘
```

**`asl` does not fork the engine and does not re-derive a phenotype.** It calls
`pgx-core` for the diplotype and phenotype and treats the answer as final. Its
value is entirely in what it attaches around that answer.

### 4.2 The evidence layer is generated, not authored (C1)

The 0.7.2 release established the pattern; `asl` reuses it verbatim.

```
scripts/regen_evidence_tables.py          # the ONLY network-touching code
    reads   api.cpicpgx.org/v1/allele?genesymbol=eq.<GENE>
    writes  asl/data/evidence/<GENE>_evidence.json
    --check regenerates in memory, diffs, exits 1 on drift   ← gated in CI
```

Generated, copied verbatim, **never edited**:

| Field | CPIC source |
|---|---|
| `clinical_function` | `clinicalfunctionalstatus` |
| `biochemical_function` | `functionalstatus` |
| `activity_value` | `activityvalue` |
| `evidence_strength` | `strength` |
| `findings_raw` | `findings` |
| `citations` | `citations` |
| `frequency_by_population` | `frequency` |

Derived, with an explicit fallback:

| Field | Derivation | Fallback |
|---|---|---|
| `basis` | classify `findings_raw` → `in_vitro` / `ex_vivo` / `in_vivo` | **`unclassified`** on any unrecognised string — never `in_vitro` |

Hand-maintained, and **only these three** (C1):

| Field | Why it cannot be generated |
|---|---|
| `cohort_n` | CPIC publishes citations, not cohort sizes |
| `cohort_ancestry` | not in the API |
| `conflict` | requires reading the contradicting literature |

Two invariants, both enforced as tests:

- **The generated columns are byte-identical to CPIC or CI fails.** This is how
  the `*6` class of defect — an undeclared one-word deviation from pinned truth —
  becomes impossible rather than merely discouraged.
- **The hand-maintained columns never feed a phenotype.** Display and flag
  metadata only; phenotype calling is byte-identical with and without them,
  asserted by test.

### 4.3 Modules

| Module | Responsibility | Refuses when |
|---|---|---|
| `models` | Types encoding the boundary: `AssayResult`, `TestedPanel`, `EvidenceRecord`, `ResidualRisk`, `LedgerEntry`. Extraction and adjudication split as *types*, per `cohortfit/models.py`. | — |
| `assay` | **What was actually tested.** A variant the panel never assayed is `NOT_TESTED`, never `absent`. This distinction is the product. | the assay's variant list is unstated |
| `interpret` | Only call site into `pgx-core`. Diplotype → phenotype. Never overrides, never re-derives. | engine returns `Indeterminate` and a definitive read was requested |
| `evidence` | Loads generated tables; attaches provenance per allele found. | a row lacks `citations` or `evidence_strength`; file drifted from CPIC |
| `residual` | The §3.2 computation. Regimen-keyed denominators, intervals not points. | regimen unknown → refuses to quote a toxicity rate |
| `population` | Attaches CPIC `frequency` for the patient's population. | population unstated → omits; **never defaults to European** |
| `conflict` | Emits named uncertainties (`P2_DPYD_STAR6_INVITRO_CLINICAL_CONFLICT`). | — |
| `haplotype` | Gentile-2016 co-occurrence flag with mandatory non-replication note; always `phase_unknown` on unphased data. | phase claimed without phased input |
| `ledger` | Append-only outcome capture. Anonymised IDs only. Schema-validated. | any PHI-shaped field present; `rsids_tested` missing |
| `report` | Clinician-facing PDF/HTML. Every claim carries a rule ID and a PMID. | any claim lacks a citation |
| `narrate` | **The only LLM call.** Deterministic record → prose. Cannot alter a call, a grade, or a number; validated against the record before display. | record is thin, or output contains a number absent from the record |
| `api` | FastAPI. `POST /interpret`, `POST /ledger`, `GET /evidence/{gene}`, `GET /health`. | unauthenticated — auth mandatory from commit one |

### 4.4 Data flow and where each refusal fires

```
lab result (PCR panel / NGS VCF)  +  regimen  +  population
   │
   ├─ assay.parse ──────────▶ which rsIDs TESTED? which FOUND?
   │                          ▲ REFUSE: panel of unstated content
   │                            → "cannot interpret a panel whose
   │                               variant list is unknown"
   │
   ├─ interpret ────────────▶ pgx-core 0.7.2: diplotype → phenotype
   │                          (CPIC, unmodified, attributed to CPIC)
   │
   ├─ evidence.attach ──────▶ strength + findings + citations per allele
   │                          ▲ REFUSE: generated table drifted from CPIC
   │                          ▲ REFUSE: allele row missing citations
   │
   ├─ population.attach ────▶ CPIC frequency for this population
   │                          ▲ OMIT (never default to European)
   │
   ├─ conflict.scan ────────▶ P2_DPYD_STAR6_INVITRO_CLINICAL_CONFLICT
   ├─ haplotype.scan ───────▶ Gentile flag + non-replication note,
   │                          phase_unknown
   │
   ├─ residual.compute ─────▶ regimen-keyed wild-type rate + CPIC quote
   │                          ▲ REFUSE: regimen unknown → no rate quoted
   │                          ▲ STRUCTURALLY IMPOSSIBLE: no code path
   │                            returns "no risk" / "low risk"
   │
   ├─ report.render ────────▶ deterministic; rule ID + PMID per claim
   ├─ narrate ──────────────▶ LLM prose, validated against the record
   │
   └─ [weeks later] ledger.record ─▶ CTCAE outcome
                                     → the dataset that fixes the calls
```

### 4.5 Deployment and integration, grounded in what Indian centres run

- **Year 1: standalone.** Web app, manual entry or CSV, PDF out. Not a
  compromise — ABDM has **no pharmacogenomics FHIR profile at all** (C7), so
  there is nothing to integrate against.
- **Year 2+: FHIR** via generic `DiagnosticReport`/`Observation` against the
  **six NCG-commissioned** oncology EMR products (C7 — commissioned, not vetted),
  reaching 20+ early-adopter centres.
- **Channel: NCG/KCDO first**, via the **Digital Health Solutions Library**,
  which openly invites vendor registration. KCDO's Chemotherapy Management
  Platform is **their own tool → a channel, not a competitor** (C7).
  **Navya second** — adjacent, not competing.
- **Deploy as `cohortfit` does:** container on Azure Container Apps. **Unlike
  `cohortfit`, authentication is mandatory from commit one** — `cohortfit` serves
  pinned public fixtures; `asl` touches patient data. (`cohortfit`'s own missing
  auth is a live open item on the platform list, and a caution, not a precedent.)
- **PHI never leaves the site.** Anonymised IDs only. Under DPDP, truly
  anonymised data is out of scope, but the *act of collecting and anonymising* is
  processing and requires consent (C7).
- **IEC approval per site** before any ledger entry (ICMR 2017 Ch.9/Ch.10).

### 4.6 Build order

| Phase | Deliverable | Gate |
|---|---|---|
| **0** ✅ | `pgx-core` 0.7.2 — DPYD strand fix, CPIC-generated tables, drift CI | **done**: 203 passed; tables byte-equal to CPIC; DPYD-only regression confirmed across 30 call points in 10 genes; 5 consumers bumped |
| 1 | `regen_evidence_tables.py` + generated DPYD evidence table | `--check` byte-equal in CI; every row has citations + strength or the loader fails |
| 2 | `assay` + `residual` — NOT_TESTED/absent split, no-all-clear guarantee | **property test: no input produces an all-clear**; regimen-unknown refuses to quote a rate |
| 3 | `interpret` + `conflict` + `haplotype` + `population`, report, CLI | phenotypes byte-identical to `pgx-core` alone on the 1000G fixture |
| 4 | `ledger` + API + auth | schema validation; no PHI fields accepted; `rsids_tested` mandatory |
| 5 | `narrate` | output validated against record; refuses on thin record |
| 6 | **MCC retrospective**, ~400–500 PCR-tested patients | the four-quadrant table: PCR± × toxicity± |

**Phase 6 is the go/no-go, and it is a real one.** If panel-negative patients at
MCC show *no* excess toxicity, the premise weakens and paediatric ALL / NUDT15
becomes the better first target (C9).

---

## 5. A real patient, walked end to end

The design is only as good as what it does for one person. This section walks a
concrete case through every stage, using **actual engine output** (executed, not
imagined) and **actual CPIC values**. It exposed three defects; all three are
recorded in §5.6 and two change the design.

### 5.1 The patient

> **Mrs. L.**, 52, Malayali, Thrissur district, Kerala. Stage III colon
> adenocarcinoma, R0 resection. Oncologist plans **adjuvant CAPOX** —
> capecitabine 1000 mg/m² twice daily, days 1–14, plus oxaliplatin, 8 cycles.
> BSA 1.52 m². She pays out of pocket; her family sells nothing yet, but a
> hospitalisation would change that.
>
> Because the centre has begun pre-emptive testing, a **4-variant DPYD PCR
> panel** is ordered: `*2A`, `*13`, c.2846A>T, HapB3. Cost ₹8,500,
> not reimbursed (C8). Turnaround 6 days.
>
> **Result: all four negative.**

### 5.2 What she gets today

Executed against `pgx-core` 0.7.2 with all four panel loci homozygous-reference:

```
diplotype = *1/*1
phenotype = Normal Metabolizer
action    = STANDARD
```

The lab report says, in effect: **"DPYD: Normal Metabolizer. No dose adjustment
required."** She starts full-dose capecitabine.

**What that report does not say**, all of it published:

- Her chance of grade ≥3 toxicity on this regimen is still **22.7%**
  (231/1018, Henricks 2018, systemic chemotherapy — the regimen-matched
  denominator, PMID 30348537).
- The panel's clinical sensitivity for grade ≥3 toxicity is **3.5–21.6%**
  (Ontario HTA, PMID 34484488).
- **`*13` has frequency 0.00000 in CPIC's Central/South Asian data.** One of the
  four variants she paid to have tested cannot be found in her population.
- CPIC itself states this test "does not fully rule out DPD defects"
  (PMID 29152729).
- **77.8%** of patients in her population carry ≥1 DPYD allele CPIC calls
  "Normal function" (computed, C3) — and hers was not looked for.

### 5.3 What she actually carries

Suppose the centre also ran research WES (as D-TORCH did). Executed:

```
input:  *9A homozygous, *6 heterozygous, M166V heterozygous
        (plus all four panel loci hom-ref)
output: diplotype = *6/*9A
        phenotype = Normal Metabolizer
        action    = STANDARD
```

Her CPIC evidence, read from the live API — not retyped:

| Allele | Copies | CPIC function | Strength | `findings` | Citation | CSA freq |
|---|---|---|---|---|---|---|
| `*9A` c.85T>C | **2** | Normal | Strong | `Dihydrouracil (in vivo)` | 18452418 | **0.25526** |
| `*6` c.2194G>A | 1 | Normal | **Moderate** | `5-fluorouracil (in vitro)` | 23328581 | 0.09506 |
| M166V c.496A>G | 1 | Normal | **Moderate** | `5-fluorouracil (in vitro)` | 24648345 | 0.08517 |

She carries **four** variant alleles across three loci, every one of which CPIC
calls "Normal function", and she is **exactly the Gentile-2016 three-SNP
combination** (`*9A` + `*6` + M166V). She is also, in composition, the modal
patient of the Indian cohorts: `*9A`, `*6` and `*5` were the three most frequent
variants in D-TORCH (n=25, 13, 12 of 76).

### 5.4 What `asl` reports instead

```
DPYD — CAPOX (capecitabine + oxaliplatin), systemic
────────────────────────────────────────────────────────────────────
CPIC CALL (unmodified, attributed)
  Diplotype   *6/*9A            Phenotype  Normal Metabolizer
  CPIC recommendation: standard starting dose.
  Source: CPIC DPYD guideline, Amstutz 2018 (PMID 29152729),
          via anukriti-pgx-core 0.7.2, table DPYD_diplotypes_anukriti_v2024.01

⚠ TESTED vs NOT TESTED                              [rule ASL-ASSAY-01]
  Tested & negative : *2A, *13, c.2846A>T, HapB3
  NOT TESTED        : *4, *5, *8, *10, *12, c.1906A>C
                      → absence NOT established for these
  Note: *13 has allele frequency 0.00000 in CPIC's Central/South Asian
        reference data. This locus is uninformative in this population.

⚠ EVIDENCE BASIS OF EACH "NORMAL" CALL              [rule ASL-EVID-01]
  *9A ×2   Normal (activity 1.0) · strength Strong · in vivo
           (dihydrouracil) · PMID 18452418 — He/Zhang 2008, n=142
           CHINESE cancer patients; no correlation with DPD activity found.
           Frequency in Central/South Asian: 0.25526 (most common DPYD
           allele in this population).
  *6  ×1   Normal (activity 1.0) · strength Moderate · in vitro (5-FU)
           · PMID 23328581 (Offer 2013, HEK293T recombinant).
  M166V ×1 Normal (activity 1.0) · strength Moderate · in vitro (5-FU)
           · PMID 24648345 (Offer 2014, HEK293T recombinant).

⚠ P2_DPYD_STAR6_INVITRO_CLINICAL_CONFLICT           [rule ASL-CONF-01]
  CPIC assigns *6 Normal function on in-vitro evidence (strength:
  Moderate). Clinical cohorts totalling >3,000 patients associate it
  with severe toxicity: Del Re 2019 n=1254 OR 1.7 p<0.001 (PMID
  30723313); PETACC-8 n=1545; TOSCA (Ruzzo 2017); Li 2014 meta-analysis
  n=946. CPIC has not revised the call. This is a DISAGREEMENT IN THE
  LITERATURE, not a revised phenotype — the call above stands.

⚠ P3_DPYD_GENTILE_HAPLOTYPE_COOCCURRENCE  phase_unknown  [ASL-HAP-01]
  This patient carries all three of rs1801265 + rs1801160 + rs2297595.
  Gentile 2016 (PMID 26216193) reported that this combination reduces
  5-FU degradation rate comparably to *2A — but that is an EX VIVO PBMC
  degradation assay (n≈94, Italian), NOT clinical toxicity.
  NOT REPLICATED CLINICALLY: Kanai 2022 (PMID 36524458), n=1364
  Japanese, found NO toxicity association for rs1801265 (neutropenia
  OR 0.53, p=0.054, trending protective); TOSCA null individually.
  MECHANISM PARTIALLY SUPPORTED: Hamzic 2021 (PMID 33491253), n=1382,
  four European cohorts — effects of c.85T>C and c.496A>G on DPD
  activity are HAPLOTYPE-DEPENDENT.
  Phase cannot be determined from unphased genotypes. This is a FLAG.

⚠ RESIDUAL RISK — NOT AN ALL-CLEAR                  [rule ASL-RESID-01]
  No actionable variant detected among the four tested. This does NOT
  exclude severe toxicity risk.
  CPIC: "patients without a DPYD decreased/no function variant may still
  experience severe toxicity due to other genetic, environmental or
  other factors"; such a test "does not fully rule out DPD defects."
  (PMID 29152729)
  Regimen-matched rate — SYSTEMIC fluoropyrimidine chemotherapy:
    22.7% (231/1018) of patients without these variants experienced
    grade ≥3 toxicity (Henricks 2018, PMID 30348537).
    [Chemoradiation figure 13.6% NOT used: this patient is on systemic
     CAPOX. Denominator selected by regimen.]
  Panel clinical sensitivity for grade ≥3: 3.5–21.6% (Ontario HTA 2021,
  PMID 34484488). Specificity 95–100%.
  Population context: in CPIC's Central/South Asian data the four tested
  variants sum to 0.02538 allele frequency; four alleles CPIC classifies
  "Normal function" sum to 0.52921 (20.9×).

WHAT THIS REPORT DOES NOT DO
  It does not recommend a dose. The CPIC recommendation above is CPIC's.
  It does not override CPIC. It does not claim this patient is at
  elevated risk — no such finding is established. It reports what is
  known, what is not, and on what evidence.
```

**Clinically, what changes for Mrs. L.?** Not her dose — `asl` does not set
doses, and there is no evidence base to justify reducing hers. What changes is
that her oncologist knows a "Normal" result carries a **22.7% residual risk on
this regimen**, that six DPYD alleles were never tested, that `*13` was
uninformative in her population, and that she sits on a flagged
haplotype whose evidence is ex-vivo and clinically unreplicated. That supports
**closer monitoring in cycles 1–2** — which is where early-onset DPD toxicity
presents, and which costs nothing.

### 5.5 Then the ledger closes the loop

Cycle 2, day 9: grade 3 diarrhoea, grade 2 mucositis, hospitalised 4 days,
capecitabine reduced 25%. She recovers and completes 6 of 8 cycles.

```json
{
  "anonymised_id": "MCC-2026-0417",
  "cancer_type": "colon adenocarcinoma, stage III",
  "regimen": "CAPOX adjuvant", "drug": "capecitabine",
  "assay_method": "4-variant PCR panel + research WES",
  "rsids_tested": ["rs3918290","rs55886062","rs67376798","rs56038477",
                   "rs1801265","rs1801160","rs2297595","rs1801159"],
  "genotypes": {"rs1801265":"1/1","rs1801160":"0/1","rs2297595":"0/1",
                "rs3918290":"0/0","rs55886062":"0/0","rs67376798":"0/0",
                "rs56038477":"0/0","rs1801159":"0/0"},
  "cpic_phenotype_at_time_of_dosing": "Normal Metabolizer",
  "pgx_core_version": "0.7.2",
  "starting_dose_mg_m2": 1000, "bsa_m2": 1.52,
  "ctcae": [{"term":"diarrhoea","grade":3,"onset_cycle":2},
            {"term":"mucositis","grade":2,"onset_cycle":2}],
  "dose_modifications": [{"cycle":3,"change":"-25%"}],
  "cycles_received": 6, "hospitalised_days": 4
}
```

`rsids_tested` is the field that makes this scientifically usable, and it is
exactly what published Indian studies omit — it is why Patil 2019's 1064
genotyped patients cannot answer the question their genotypes were collected
for (C4). One row proves nothing. **400 rows is a paper, and a submission to
CPIC's PCEP process** (C7, §3.3).

### 5.6 Three defects the walkthrough exposed

**Defect 1 — the engine silently drops alleles when >2 copies are detected.
Real, verified, and not an edge case for Indian patients. FIXED in `pgx-core`
0.7.3 (tagged, all five consumers bumped).** Executed against 0.7.2:

| Input | Copies detected | 0.7.2 output |
|---|---|---|
| `*9A` hom | 2 | `*9A/*9A` ✓ |
| `*9A` het + `*6` het | 2 | `*6/*9A` ✓ |
| **`*9A` hom + `*6` het** | **3** | **`*6/*9A`** — one copy dropped, silently |
| **`*9A` hom + `*6` het + M166V het** | **4** | **`*6/*9A`** — two dropped, silently |

A diploid genome has two DPYD chromosomes, so >2 copies means the input is
inconsistent, unphased across a haplotype, or a genotyping artifact. Whatever the
cause, **the caller must not resolve it by quietly discarding alleles.** In
Europeans this is rare. In Indians it is *expected*: `*9A` 0.25526, `*6` 0.09506,
M166V 0.08517.

**Resolution (0.7.3):** `Diplotype` gains `copies_detected` and `overspecified`
(`copies_detected > 2`), plus a `total_allele_copies()` helper. The truncation is
retained for backwards compatibility but is no longer invisible, and the full
allele set remains recoverable from `alleles_detected` / `allele_counts`.
Additive — verified across 48 call points in 11 genes against `v0.7.2`, no
diplotype or phenotype value changed. **`asl`'s `interpret` module must check
`overspecified` and refuse** rather than paper over it, and `report` must list
every detected allele rather than the two that sorted first.

This is the same failure class as 0.7.2 — a defensible-looking simplification
that destroys information without recording that it did.

**Defect 2 — "Normal Metabolizer" with `activity_score = -1.0`.** The engine
returns a sentinel because DPYD resolves via the named-diplotype table rather
than an activity-score sum. Harmless internally, but **a report must never print
`-1.0` next to a phenotype**. `asl`'s `report` module suppresses the sentinel and
prints CPIC's per-allele `activityvalue` instead. Test required.

**Defect 3 — the design had no way to say "this locus is uninformative here".**
`*13` at frequency 0.00000 in Central/South Asian means Mrs. L. paid for a test
of a variant that does not occur in her population. Neither the 08:29 document
nor my §4 draft had a mechanism for this; §5.4's report shows it under
`ASL-ASSAY-01`. *Action:* add `population.uninformative_loci` to §4.3 —
computed, not asserted, straight from CPIC's `frequency` field.

---

## 6. What it refuses to do

Each is a failure mode we can name, and each is enforced by a test rather than by
convention.

1. **It does not recommend doses.** CPIC's recommendation is displayed as CPIC's.
   Crossing this line makes it *drive* clinical management — Class B/C under
   CDSCO — and abandons the evidence-layer position (C7).
2. **It does not invent an Indian activity score.** No population-specific
   activity values until the ledger supports them. This is the `U4_SAS_DPYD_OVERRIDE`
   lesson: a hand-written frequency claim citing a real paper ran live for 52
   days (`DPYD_SAS_OVERRIDE_AUDIT_2026-07-28.md`).
3. **It does not override CPIC.** Where evidence disagrees, it emits a *named
   uncertainty alongside* the CPIC call, never instead of it. **This is now
   enforced in the engine too**, by the 0.7.2 CPIC-drift CI job — the `*6`
   deviation is exactly what that job exists to catch.
4. **It does not emit an all-clear.** No code path returns "no risk" or "low
   risk". Property test, not convention.
5. **It does not treat NOT_TESTED as absent.** A 4-variant panel that never
   assayed `*6` reports `*6` as untested.
6. **It does not quote a toxicity rate without a regimen.** 22.7% (systemic) and
   13.6% (chemoradiation) are different populations; picking wrongly misleads in
   both directions (C5).
7. **It does not claim a Bengali or Malayali frequency.** CPIC's
   `Central/South Asian` is the finest granularity the data supports. Per
   `CLINALITY_DEEP_RESEARCH_2026-08-16.md`, sub-population estimates are not
   trustworthy at available N — within-Pakistan `*2` variation (Baloch 0.160 vs
   Pathan 0.032) is as large as the whole NW→SE cline.
8. **It does not let the LLM touch a number.** Narration only, validated against
   the record.
9. **It does not accept PHI.**
10. **It does not resolve an over-specified genotype by dropping alleles**
    (§5.6, Defect 1).

### Regulatory posture, stated plainly

| Jurisdiction | Likely class | Basis |
|---|---|---|
| **India (CDSCO)** | **Class A**, possibly B | *informs* clinical management + serious condition. Even Class A **requires registration under Chapter IIIB** of MDR 2017 — not exempt (C7). |
| **US (FDA)** | likely **non-device CDS** | 21st Century Cures §520(o)(1)(E): displays guideline information, supports an HCP, **and enables independent review of the basis** — which is precisely what §3.1 does. The evidence-provenance display is not decoration; it is the regulatory argument. |
| **EU (MDR)** | **Class IIa** minimum | Rule 11 has no display-only exclusion. |

The strongest single regulatory fact is C5: **the residual-risk statement quotes
CPIC.** We are not asserting a novel clinical claim; we are declining to discard
a caveat the guideline publishes.

---

## 7. Limitations of this analysis

- **The 250,000–350,000/yr utilisation figure is author-derived arithmetic, not
  published.** Exhaustively confirmed (C8). It must be labelled wherever used.
- **D-TORCH is n=76, single-centre, 29% of its parent cohort**, and its Table 4
  headers are swapped (corrected in the 08:29 document §1.4: 55.6% of variant
  carriers vs 63.6% of wild-type had grade ≥2 toxicity — so variant status
  carried *no* information in that cohort). It remains the only Indian NGS
  cohort. **But the problem statement no longer rests on it** — C3 derives the
  same conclusion from CPIC's own frequencies, and C4 adds ~554 more patients
  across three further centres.
- **Pavithran 2021 (n=375) is an ASCO abstract**, not a full paper. Its
  c.496A>G finding is the strongest Indian corroboration available and it is
  abstract-grade evidence. Flagged; must be cited as such.
- **`*6` reclassification is a reading of the literature, not a guideline
  position.** CPIC has not moved. We surface the conflict; we do not resolve it.
- **Gentile 2016's Hap7 claim is ex-vivo and clinically unreplicated** (C6).
  Wherever it appears it must carry the Kanai 2022 null.
- **Plasma uracil phenotyping is the strongest population-agnostic
  alternative** — it measures enzyme activity, not genotype, and would capture
  *all* causes of reduced DPD activity regardless of ancestry, which is exactly
  the class of patient a European-derived genotype panel misses in India. **See
  C13 (§10): my original reasons for rejecting it were partly wrong.** CMC
  Vellore *does* have a validated LC-MS/MS assay and has published Indian
  uracil/DHU data (n=100 healthy adults, DOI 10.2217/pme-2022-0042). The
  defensible reason to reject it is that a 955-patient, 17-centre Dutch study
  **failed to validate the 16 ng/mL threshold at all** (de With 2022, PMID
  35397172: OR 0.997, p=0.71), because the assay degrades within ~47 minutes at
  room temperature — and no one has characterised those kinetics at Indian
  ambient temperatures of 30–35 °C. **This remains a real gap in a genotype-only
  approach**, and a single Indian centre with on-site LC-MS/MS could test it.
  Note also that **CPIC is genotype-only**, so a phenotyping product would have
  no guideline to attribute to, worsening the §6 posture.
- **No validated multi-gene fluoropyrimidine toxicity score exists** in any
  guideline. TYMS/MTHFR/CDA have real effect sizes (Loganayagam 2013: TYMS
  3'UTR del/del OR 3.08; MTHFR 1298CC OR 9.99 for HFS) but adding them to
  clinical variables moved AUC only 0.72 → 0.74. We must not imply a polygenic
  score is available.
- **UNVERIFIED:** whether any NCG treatment guideline mentions DPYD or PGx at
  all. Searched, found nothing, absence not proven (C7).
- **UNVERIFIED:** the exact content of KCDO's Chemotherapy Management Platform
  beyond its existence and its iF Design Award.
- **CPIC may close part of the gap.** If CPIC adds cohort N and ancestry to its
  API, two of the three genuinely-ours evidence fields disappear. This is why
  the moat is §3.2 and §3.3 (C1, C10).
- Research breadth came from sub-agents. **Where their claims conflicted with
  what I verified myself, the local verification won and the conflict is
  recorded** — most importantly C1, where a sub-agent reported that CPIC's
  evidence metadata is Excel-only and not in the API. Direct query disproved
  that, and it was the single most design-relevant finding of the day.

---

## 8. Immediate next actions

1. **`pgx-core` 0.7.3 shipped** — §5.6 Defect 1 is fixed: over-specified
   genotypes now carry `copies_detected` and `overspecified` instead of being
   silently truncated. Tagged, additive (48 call points, 11 genes, no value
   changes), all five consumers bumped. **Remaining work:** `asl`'s `interpret`
   must consume the flag and refuse, and `report` must list every detected
   allele.
2. **Scope `asl` Phases 0–2.** Phase 0 is done (0.7.2 + 0.7.3 shipped, five
   consumers bumped). Phase 1 is `regen_evidence_tables.py`, a near-copy of
   `regen_dpyd_tables.py`.
3. **Correct the 08:29 document** or supersede it explicitly — it currently
   asserts C1, C2, C4, C5 and C6 incorrectly. This file is the replacement;
   add a pointer at the top of the old one.
4. **Correct `DPYD_ONCOLOGY_DEEP_DIVE.md`** — still asserts the refuted 27%
   South Indian `*9A` claim and describes `U4` as a live feature.
5. **Obtain the Pavithran 2021 full text or contact the authors.** n=375 with
   c.496A>G tracking toxicity is the most valuable Indian data point available
   and it is currently abstract-grade.
6. **Register on the NCG Digital Health Solutions Library** — the concrete,
   published entry mechanism (C7).
7. **Reactivate MCC for the Phase 6 retrospective.** Genuine go/no-go.
8. **Ask MCC whether any Indian lab offers plasma uracil LC-MS/MS.** If yes,
   §7 requires revisiting before building.

---

## 9. The through-line

The platform's method is to audit its own claims and publish the negative
result. This document does it twice over: **four of the 08:29 document's
load-bearing claims were wrong**, and the engine underneath it was inverting
homozygous DPYD calls while every test passed.

Both failures share one shape. The strand defect survived four releases because
the tests were written in the same wrong convention as the table — self-consistent,
and therefore invisible. The `*6` deviation survived because a defensible clinical
judgement was written directly into a data table with nothing recording why. And
the clinical problem this product addresses is the same shape again: a
guideline-conformant test converts "we found nothing on our list" into "this
patient is normal", and the conversion is invisible because the report that would
have shown it is the report that discarded it.

*The failure is rarely the wrong answer. It is the right answer with its
uncertainty stripped off.* That is true of `pgx-core` 0.7.1, of the 08:29
document, and of every "Normal Metabolizer" printed for an Indian patient on
fluoropyrimidines.

---

## 10. Research pass 3 — four corrections to this document

Written after §1–§9. Two of these qualify claims made above; recorded here rather
than silently edited, per the platform's own method.

### C11 — Pavithran 2021 verified exactly, but D-TORCH contradicts it

Retrieved from the primary abstract (Pavithran K, Ariyannur P, Jayamohanan H,
Philip A, Jose WM, Soman S. *J Clin Oncol* 2021;39(15_suppl):e15517,
DOI 10.1200/JCO.2021.39.15_suppl.e15517). **Every number in C4 is confirmed
verbatim**, and two details strengthen it:

- **Dose reduction was pre-emptive, not reactive.** "Variants were assessed prior
  to the initiation of the chemotherapy and dose was modified based on the
  activity score." So the 35/47 with grade II–III toxicity occurred *despite*
  prospective genotype-guided dose modification.
- Cancer types: GI, breast, head and neck, treated 2019–2020. Adverse events:
  HFS 18/47, diarrhoea 15/47, neutropenia 25/47, febrile neutropenia 4, no
  mortality.

**But three caveats that must travel with it:**

1. **No full paper exists.** Searched 2021–2026; the ASCO abstract is the only
   publication. It is ~350 words and was never peer-reviewed in full.
2. **The "74.5%, p=0.002" statistic is ambiguous.** The abstract reads
   "DPYD mutation had significant association with presence of severe adverse
   reaction (74.5%, p-value. 0.002)" — 74.5% could be a chi-square statistic, a
   proportion of carriers with toxicity, or a sensitivity. Without the full paper
   this cannot be resolved. **We must not quote 74.5% as if its meaning were
   established.**
3. **D-TORCH contradicts the c.496A>G finding.** Baskarane 2026 found rs2297595
   in 7/76 patients with **no toxicity signal**, and found no association between
   DPYD variant status and toxicity overall (OR 0.71, 95% CI 0.26–1.98, p=0.612).
   D-TORCH is smaller but methodologically stronger: prospective, WES-based, and
   **unbiased with respect to toxicity selection**.

### C12 — The Indian evidence base is weaker than C4 implied: severe ascertainment bias

This is the correction that matters most. **Two of the five studies I counted in
C4 tested only patients who had already developed grade 3+ toxicity:**

| Study | Design | Effect on the estimate |
|---|---|---|
| Patil 2016 (TMH, head/neck) | 34 received TPF; **only the 12 with grade 3+ toxicity were tested**; 11/12 variant-positive | inflates variant–toxicity association enormously |
| Sahu 2016 (TMH, GI) | 506 received capecitabine; **only the 28 meeting grade 3/4 criteria were tested**; 22 positive | ibid.; the honest denominator is 22/506 = 4.3% |
| Pavithran 2021 (Amrita) | **all 375 genotyped pre-treatment** | unbiased, but abstract-only |
| D-TORCH 2026 (AIIMS) | **all 76 sequenced**, unselected | unbiased, strongest method, **found no association** |
| Varma 2020 (JIPMER) | n≈145, PK-focused | primary source inaccessible; unverified |

So the correct statement is **not** "~630 patients across four-plus centres".
It is: **~451 patients across two centres were genotyped without toxicity
selection (Pavithran 375 + D-TORCH 76); the remainder is toxicity-selected and
cannot support a prevalence or association claim.** And of those two unbiased
studies, **the better-conducted one found no association.**

Both Tata Memorial studies do, however, contain something useful and separate
from the association question: **dose reduction in cycle 2 reduced grade 3–4
mucositis from 70% to 10% (p=0.02, Patil 2016) and from 71% to 24% (p=0.016,
Sahu 2016), with diarrhoea 88% → 36% (p=0.006).** That is a
dose-response observation, not a genotype-prediction one, and it is not
undermined by the selection bias.

**Consequence for the product.** The residual-risk framing (§3.2) is
*unaffected* — it rests on CPIC's own text, the Ontario HTA, and the wild-type
toxicity rates from Henricks and Lunenburg, none of which are Indian. What is
weakened is any claim that specific normal-function alleles *predict* Indian
toxicity. **`asl` must therefore present c.496A>G and `*6` as contested, with
the contradiction stated in both directions** — Pavithran positive, D-TORCH
null — rather than as evidence of elevated risk. That is what the
`P2_..._CONFLICT` mechanism is for, and this is now its most important use.

### C13 — Uracil phenotyping: my stated reasons for rejecting it were wrong; the correct reason is stronger

§7 claimed no Indian lab offers plasma uracil phenotyping and that the 16 ng/mL
threshold is unvalidated outside French cohorts. **The first is largely wrong and
the second is right but incomplete.**

- **CMC Vellore has a validated LC-MS/MS assay and published Indian data.**
  Sivamani P, Eriyat V, Mathew SK, et al., *Personalized Medicine*
  2023;20(1):39-53, DOI 10.2217/pme-2022-0042 — plasma uracil, dihydrouracil and
  DHU/U ratio in **n=100 healthy Indians**, correlated with DPYD genotype.
  Participants with functional variants had significantly lower DHU/U ratios.
  It is a research assay rather than an orderable clinical service, but **the
  capability exists in India** and my §7 wording overstated its absence.
- **The threshold has never been validated against toxicity in any Asian or
  South Asian population.** Confirmed. Derived in French cohorts
  (Boisdron-Celle 2007, n=252), supported at one Dutch centre
  (Meulendijks 2017, n=550: U>16 ng/mL OR 5.3 for severe toxicity, sensitivity
  18%, PPV 35%).

**The far better reason to reject it — which §7 did not state:**

> **A rigorous Dutch multicentre study failed to validate the threshold at all.**
> de With et al., *Clin Pharmacol Ther* 2022;112(1):62-68 (PMID 35397172),
> **n=955 across 17 centres**: median uracil varied from 7.59 to 16.30 ng/mL
> *between centres* in wild-type patients (p<0.001); **no** correlation with PBMC
> DPD activity (R²<0.01); **no** association with severe toxicity (p=0.73); at
> the 16 ng/mL cutoff **OR 0.997, p=0.71** — null. The authors "urge that robust
> clinical validation should first be performed before pretreatment plasma
> uracil levels are used in clinical practice."

And the mechanism of that failure is pre-analytical, which matters
disproportionately in India. Thomas/Maillard et al., *Br J Clin Pharmacol*
2023;89(2):762-772 (PMID 36104927), 14 laboratories: **uracil in whole blood
rises +21% within 1.5 h at room temperature** (uridine phosphorylase converts
uridine to uracil, and inhibiting DPD does not stop it); only **47 minutes**
keeps 95% of samples within ±20%; at +4 °C the window extends to 5 h. In 573
correctly double-sampled patients, intra-occasion CV was 22.4% and **17%
received a discordant phenotype from their two samples** — rising to **33.8%**
under non-compliant handling. EDTA tubes read ~14.2% higher than lithium
heparin, enough on its own to cross the threshold. Renal impairment produces
false positives (Gaible 2021, PMID 34515833).

**Restated rejection, which is now defensible:** the assay is exquisitely
sensitive to a pre-analytical window of under an hour at ambient temperature.
Published stability data are at ~21 °C; **no study characterises the kinetics at
Indian ambient temperatures of 30–35 °C**, where degradation would be faster.
Indian oncology patients are frequently referred from peripheral centres, so
draw-to-centrifugation routinely exceeds an hour without a cold chain. If 17
climate-controlled Dutch hospitals could not make this reproducible, a
multicentre Indian deployment will not.

**What we must nonetheless concede, and §7 should say so:** phenotyping captures
*all* causes of reduced DPD activity regardless of ancestry — transcriptional,
post-transcriptional, and rare or novel variants — which is precisely the class
of patient a European-derived genotype panel misses in India. **That is a real
gap in a genotype-only approach.** The honest position is that uracil
phenotyping is scientifically better in principle and impractical in Indian
logistics today, and that a single Indian centre with on-site LC-MS/MS and a
strict fasting/ice/30-minute protocol could test the proposition. CMC Vellore is
the obvious partner. Also note: **CPIC is genotype-only** — it makes no
phenotype-based dosing recommendation — so a phenotyping product would have no
guideline to attribute to, which changes the regulatory posture in §6 unfavourably.

### C14 — Indian policy assertion survived a deliberate attempt to refute it

An adversarial search for any 2025–2026 CDSCO, ICMR, MoHFW, NMC or NCG document
recommending pharmacogenomic testing before chemotherapy **found nothing**.
Checked: CDSCO Oncology SEC minutes (29 Jul 2025) — no mention of PGx; NCG
guidelines and Choosing Wisely India — no mention; PM-JAY HBP 2.0 package master
— no genetic testing code; Union Budget 2025-26 cancer allocation — no mention.
GenomeIndia (20,000 samples collected, 9,768 genotyped) has **no clinical
implementation programme**. The Tata Institute for Genetics and Society scoping
review (PMID 40700148) identifies 24 PGx-actionable genes and concludes that "an
overarching need exists to establish and regulate" actionable PGx in Indian
practice — which documents the absence rather than filling it.

So the gap is real, and the strategic implication is unchanged: there is no
mandate to comply with and no reimbursement to attach to. Adoption has to come
through clinical usefulness at a partner site, not policy.

### NUDT15 second workflow — what pass 3 established

For when DPYD is done, the CPIC position is now current and citable:

- **CPIC thiopurine guideline 2025 update**: Maillard M et al.,
  *Clin Pharmacol Ther* 2026 Jan 31;119(4):916-927, PMID **41618934**,
  DOI 10.1002/cpt.70209. Recommendations reorganised **by drug**; a new
  **compound intermediate metabolizer** phenotype (TPMT IM + NUDT15 IM) at
  **20–50%** of standard starting dose; `*4` and `*9` reclassified to no
  function; `*5` to decreased function. All recommendations **Strong**.
- NUDT15 `*3` (rs116855232) in Central/South Asian: **7–8%**; Central Asian
  NUDT15 deficiency overall **13.6%**. Indian paediatric ALL cohorts:
  9–10.7% (Khera 2019, PGIMER, PMID 30474703, OR 4.01 p=0.002 for adverse
  events) and 16.7% (ICMR-NICHDR, Frontiers 2025). Homozygotes tolerate **8%**
  of standard mercaptopurine dose; heterozygotes 63% (Yang 2015, PMID 25624441).
- **A subtlety a software layer must get right — and which pass 7 corrected.**
  ICiCLe-ALL-14 uses **60 mg/m²/day** 6-MP in maintenance, not the 75 mg/m²/day
  CPIC references. This document originally called that a
  guideline-to-local-protocol mismatch that `asl` should surface. **That was a
  misreading of CPIC**, corrected in §16 C25: the recommendation is explicitly
  dose-conditional — "*if* starting dose is ≥ 75 mg/m²/day… **if starting dose is
  already below standard starting dose, dose reduction might not be necessary**"
  — and CPIC states that standard starting doses vary by geographic region. At
  ICiCLe's dose CPIC's guidance is that a reduction may be unnecessary, so there
  is no gap to surface. Indian data showing NUDT15-variant carriers reaching only
  ~0.50 dose intensity versus 0.79 in wild-type (p<0.0001) remains a real
  finding about *reactive* dose reduction; it is not evidence of a guideline
  defect.
- ICiCLe-ALL-14 does not specify NUDT15 or TPMT testing; adjustments are
  reactive. **No Indian centre tests NUDT15 routinely as standard of care.**
  MPGx-INDALL (PMID 41843828, NCT05512169, protocol published Jan 2026) is the
  implementation pathway to watch.

### Net effect of pass 3 on the plan

**The product thesis is unchanged and slightly better founded**, because the
residual-risk argument never depended on Indian association data — it rests on
CPIC's own caveat and on non-Indian wild-type toxicity rates (§3.2, C5).

**What changed is the confidence with which we may speak about specific
alleles.** c.496A>G and `*6` are *contested*, with Pavithran positive and D-TORCH
null, and the toxicity-selected studies cannot arbitrate. §3.1's conflict flag is
therefore not a nice-to-have; it is the only honest way to present them.

**And the go/no-go got sharper.** If the two unbiased Indian studies disagree,
then Phase 6 — the MCC retrospective, ~400–500 PCR-tested patients with
toxicity follow-up — is not a confirmation exercise but the tie-breaker.

---

## 11. Adversarial audit of `asl` — seven further defects, all fixed

Written after the package was built and its 72 tests passed. The method was not
to re-read the code but to **drive patient-shaped inputs through the pipeline and
inspect what came out** — the same technique that found the strand defect in
`pgx-core` 0.7.1, where every test passed because the tests shared the table's
wrong convention.

All seven are the same failure class as §5.6 and as the clinical problem itself:
**a defensible-looking default that converts "we do not know" into "nothing
found", without recording that it did.** Every one produced a *confident, clean,
plausible report* rather than an error.

| # | Defect | Behaviour before | Now |
|---|---|---|---|
| 4 | Unknown population key | `"South Asian"` (not a CPIC key) silently suppressed **every** frequency line and the entire uninformative-locus section, while the header still printed the population — a report that looked population-aware and was population-blind | refused, with the six valid keys listed |
| 5 | Nothing tested | an assay whose every locus was `NOT_TESTED` returned `*1/*1` **"Normal Metabolizer"** from zero observations | refused before the engine is called |
| 6 | Wrong gene | `gene="CYP2D6"` was accepted and run through the DPYD caller, yielding a DPYD diplotype from another gene's loci | refused |
| 7 | Unlabelled found allele | an allele with no CPIC label reached the diplotype and appeared **nowhere** in the evidence section — a finding with its provenance stripped off | refused |
| 8 | Duplicated locus | two readings of one rsID: the second silently overwrote the first, and the losing genotype vanished from the record entirely | refused in `AssayResult.__post_init__` |
| 9 | Off-panel genotype | a CSV recording `*6` het, interpreted against `cpic4`, marked the locus `NOT_TESTED` and reported `*1/*1` — **the observed variant disappeared** | refused; choose a panel that covers it |
| 10 | **Blank CSV cell** | an empty `rs1801265` cell defaulted to `hom_ref`, so the locus was printed under **"Tested & negative"** — the patient was told absence was established at a position nobody read | blank ⇒ no-call ⇒ `NOT_TESTED`; the default is **removed**, so an unstated locus is an error |

Defect 10 is the most serious, and it is worth being precise about why: it is the
exact defect the package was written to prevent, reintroduced one layer below the
type system that prevents it. `models.py` makes `NOT_TESTED` and `ABSENT`
unconflatable *as types* — and then the CSV reader collapsed them anyway, because
`genotypes.get(rsid, Zygosity.HOM_REF)` is an entirely reasonable line of code.
**A type-level guarantee is only as strong as the boundary that constructs the
types.** The fix is not a validation check but the removal of the default:
`_assay` now requires an explicit entry for every panel locus and refuses
otherwise.

Two consequences follow the fix outward:

- **The panel name now degrades with the data.** When loci return no call the
  report reads `"... (4 of 8 loci returned a call)"`, because the panel name is
  what the report attributes its conclusions to and it must not claim coverage
  the data did not deliver.
- **`quadrant` excludes no-call patients rather than counting them negative.**
  Counting them as negative would inflate the panel-negative/grade≥3 cell — the
  single cell the MCC retrospective exists to measure — **in the direction that
  flatters our own thesis.** That this bias was self-serving and unnoticed is the
  point.

**Verification.** 83 tests pass (72 → 83; 11 added, one per defect plus the
no-call and quadrant-bias properties). `ruff` reports no new findings attributable
to these changes beyond one stylistic `UP033` matching the file's existing
`lru_cache` convention. The `pgx-core` pin is untouched at `0.7.3` — every fix is
in `asl`, and none alters a phenotype, an activity score or a CPIC call.

### What this says about the method

Nine defects have now been found in this work: two in `pgx-core` (§5.6, and the
`*6` deviation in §8 of the 08:29 document) and seven in `asl`. **None was found
by a failing test.** Every one was found by asking what the code would print for
a specific patient and then looking at the output. The test suite grew *after*
each finding, which is the correct order — a test can only encode a failure mode
someone has already imagined.

The through-line of §9 holds one level deeper than stated there. It is not merely
that a guideline-conformant report strips uncertainty off a correct answer. It is
that **every layer does this, including the layer built to stop it.** `asl` exists
because a lab report converts "not on our list" into "normal"; `asl` itself
converted "blank cell" into "negative". The defence is not a better type system,
a longer refusal list, or more tests. It is the discipline of driving real inputs
through and reading the output as a patient would.

---

## 12. Research pass 4 — the problem re-derived from current sources (2026-08-16, 17:45)

The prior passes were reviewed rather than re-run. This pass went back to the
literature and to CDSCO directly, on the principle that a problem statement should
be re-tested against current sources rather than trusted because it is written
down. **The problem statement survives and is now better sourced. One claim in
§11's own fix was wrong and is corrected here.**

### C15 — D-TORCH is now a peer-reviewed paper, not a preprint

The single most-cited source in this whole analysis has been published:
**Baskarane, Divakar, … Batra. *Front Pharmacol* 17:1732128, 20 February 2026,
doi 10.3389/fphar.2026.1732128.** Received 25 Oct 2025, accepted 19 Jan 2026.
Editor Luis Abel Quiñones; reviewers Jacqz-Aigrain and Afolabi. Open access CC-BY.
Every earlier document treats it as abstract- or preprint-grade. **It is now
citable as a peer-reviewed primary source, and the ~554-patient supporting base
in C4 can be dropped to a supporting role.**

Reading the published tables directly settles two internal questions:

- **The Table 4 header swap is real and is in the published version.** The header
  reads `Variant (n = 22)` / `Wild-type (n = 54)`, but the cohort is 54 variant
  carriers and 22 wild-type — the labels are transposed. The body text gives the
  correct orientation: **66.7% (36/54) of variant carriers vs 63.6% (14/22) of
  wild-type had grade 2–3 toxicity.** Our earlier reading (55.6% vs 63.6%) was
  taking the `Overall toxicity ≥ grade 2` row, which is a different endpoint from
  the "grade 2 or 3" figure in the text. **Both readings agree on the conclusion
  and it is the conclusion that matters: variant status carried no useful
  information.** All Firth-adjusted ORs are null (any ≥grade 2: OR 0.52,
  95% CI 0.16–1.51, p = 0.23), and *no covariate at all* was significant.
- **The headline number is confirmed exactly, and it is the right number.**
  "35 out of 50 patients … classified as normal metabolizer phenotype as per the
  CPIC guidelines, still developed grade 2 or 3 toxicity" — **70%**, the authors'
  own words, and they draw our conclusion for us: *"emphasizing the limitation of
  CPIC-based phenotype prediction and dose adjustment in the Indian population."*

### C16 — The strongest formulation of the problem is now a published quotation

D-TORCH cites White 2021 (PMID 34916829) for a sentence that states our thesis
more precisely than any of our own prose:

> "The DPYD activity score, validated in the Caucasian population, remains
> unverified in other ethnic groups, potentially explaining toxicity differences
> among CPIC-classified normal metabolizers."

This matters for the §6 regulatory posture. **The claim that the activity score is
unvalidated for Indians is not ours; it is published, peer-reviewed, and cited
approvingly by the only Indian NGS cohort.** We are surfacing a limitation the
field has already stated, which is exactly the "enables independent review of the
basis" position that keeps this a non-device CDS argument in the US and an
evidence-display product under CDSCO.

### C17 — Chan 2024 corrects §11's own fix (**a defect in my defect fix**)

Chan, Zhang & Pirmohamed, *Br J Cancer* 131:498–514 (2024), PMID 38886557 — a
PRISMA systematic review of 32 studies, 1,313 non-European patients, 53 DPYD
variants across 5 ethnic groups including South Asian. Two findings bear directly
on code I wrote earlier today:

1. **`*13` was found in a Tunisian patient with severe toxicity although its
   Middle Eastern reference frequency is 0%.** `*2A` was found in 14 Chinese, 1
   Thai and Japanese patients although its East Asian reference frequency is 0%.
2. Therefore **a 0.00000 CPIC frequency is an absence of observation in a
   reference panel, not proof of absence in the population.**

§11's `ASL-POP-01` section printed: *"this locus cannot return a positive result
in this population."* **That is an overclaim, and it is the same failure class as
everything else in this document, inverted.** Where the clinical problem is
missing data presented as reassurance, my fix presented missing data as
*impossibility* — and it would have licensed a clinician to dismiss a positive
`*13` call as an assay error. In a country whose population structure is poorly
covered by reference panels, that is the wrong direction to be wrong in.

**Fixed.** The section is now `LOCI WITH VERY LOW EXPECTED YIELD HERE`, states that
a zero reference frequency is an absence of observation rather than proof of
absence, cites Chan 2024, and ends: *"A positive call at this locus must still be
acted on."* Pinned by `test_zero_frequency_is_low_yield_not_impossibility`, which
asserts the phrase "cannot return a positive" is **absent** from every report.

### C18 — Two things the fresh pass did not find

- **CDSCO.** Searched current CDSCO output directly. The SEC (Oncology) minutes
  through 2026 (13th/26 of 06.05.2026, 15th/26, 18th/26 of 08.07.2026, 21.07.2026)
  are **entirely clinical-trial approvals** — protocol permissions, sample-size
  and site conditions, "All PIs shall be Medical Oncologist". **No PGx or DPYD
  item appears in any of them.** This is consistent with C7's UNVERIFIED status on
  Indian guideline coverage: still no evidence Indian regulators or the NCG have
  addressed pre-treatment DPYD testing. Absence of evidence, not proof of absence
  — but it is now a *searched* absence, twice.
- **No newer Indian cohort exists.** D-TORCH (n=76) remains the only Indian
  NGS-based DPYD study. Pavithran 2021 (n=375) is still an ASCO abstract, and
  D-TORCH's discussion confirms our C11 reading: Pavithran's `c.496A>G`/`*2A`
  findings come from cohorts **selected for grade-3 toxicity**, which D-TORCH
  names explicitly as the reason its own unselected cohort disagrees. **The
  ascertainment-bias problem (C12) is now corroborated by the authors of the one
  unbiased study.**

### What pass 4 changes about the plan

Nothing in the architecture. The problem is more firmly established, one
overclaim in the engine is removed, and the go/no-go is unchanged: **two
unbiased-vs-selected Indian data sources disagree about `c.496A>G` and `*6`, and
only the MCC retrospective can arbitrate.** What did change is the *citation
posture* — the two load-bearing claims (activity score unvalidated outside
Caucasians; 70% of CPIC-normal Indian patients toxify anyway) are now both direct
quotations from peer-reviewed papers rather than our own inferences. That is the
strongest position this analysis has been in, and it was reached by re-checking
rather than by adding.

**Verification:** 84 tests pass (83 → 84). `pgx-core` pin unchanged at 0.7.3.

---

## 13. Audit round 2 — the variant-positive patient (2026-08-16, 22:40)

Every earlier pass, and every test in §11, walked the **panel-negative** patient
through the report. That is the patient the package was designed around, so that
is the path that was already correct. This round walked a *carrier* through
instead — and the four-quadrant table through a spreadsheet that a site would
plausibly hand over. **Five defects, all fixed, all now pinned by tests that
fail against the previous code.** 86 → 107 tests.

### D1 — A Poor Metabolizer was shown the wild-type toxicity rate (**the serious one**)

`residual.compute()` keyed the quoted grade ≥3 rate on the **regimen alone**. A
`*2A/*2A` Poor Metabolizer on systemic chemotherapy therefore received:

> Regimen-matched rate (systemic): **22.7% (231/1018)** of patients without an
> actionable DPYD variant experienced grade ≥3 toxicity.

Henricks 2018 and Lunenburg 2018 both measure that rate among patients **without**
an actionable variant. This patient is the opposite of that group. The line was
literally true and situationally false, and it failed in the **reassuring**
direction for the one patient in the whole workflow who should be reassured
least — someone CPIC says to give no fluoropyrimidine at all. It is the
package's own thesis — *a number stripped of the population it was measured in*
— reproduced inside the tool built to prevent it, and it survived three prior
adversarial passes because every one of them tested a negative panel.

**Fix.** A found allele that CPIC does not call *normal function* now withholds
the rate and says why. The function call is read from the pinned CPIC evidence
table, so the set cannot drift from CPIC. `ResidualRisk` carries
`applies_to_this_patient`, and the report prints `RATE WITHHELD — DOES NOT APPLY
TO THIS PATIENT`.

**The over-correction was also avoided, deliberately.** A `*9A` or `*6` carrier
*keeps* the rate, because CPIC calls those alleles normal function and the
published cohorts defined their comparison group by the absence of an
**actionable** variant, not of any variant. Withholding it there would have
stripped the one number a panel-negative Indian patient's report exists to
deliver — which is the entire product. Pinned in both directions:
`test_wildtype_rate_is_withheld_from_a_carrier` (8 parametrisations) and
`test_wildtype_rate_is_kept_for_a_normal_function_carrier`.

A second-order version of the same error was then found *in the fix*: the
withholding message quoted "22.7% systemic … 13.6% chemoradiation" while
explaining that neither applied. A number on the page is read whatever the
sentence around it says. The figures were removed and replaced with PMIDs, and
the test asserts `"22.7"` is absent from the residual section.

### D2 — "No variant was found among the loci tested" on a panel that mostly failed

With three of four CPIC loci returning no call, the report said *"No variant was
found among the loci tested"* — one locus of reassurance rendered in the language
of four. The panel *name* was correctly annotated `(1 of 4 loci returned a call)`
by the CLI, but the residual section's own sentence contradicted it, and the
sentence is the one a clinician reads. Now: *"No variant was found at the 1 locus
that returned a call"*, plus an explicit count of loci not assayed.

### D3 — The CPIC recommendation never named the drug

`interpret.call_engine` hardcoded `action_for("DPYD", phenotype, "capecitabine")`
and the report rendered a bare `CPIC action : AVOID`. A patient on infusional
5-FU got a recommendation labelled for a drug they were not taking — invisibly,
because the drug appeared nowhere in the output. Added a closed `Drug` enum
(`capecitabine`, `fluorouracil`), threaded through `AssayResult` and the CLI
(`--drug`, plus a `drug` CSV column), and the report now prints `AVOID (for
capecitabine)`.

### D4 — A blank clinical action would have rendered as an empty line

`action_for` **never raises** — it is on the hot phenotype path, so an
unrecognised phenotype/drug pair returns `""` by design. Rendered, that is
`CPIC action :` followed by nothing, which reads as *nothing to do*. Exhaustive
search over all 13 pinned loci in every 1- and 2-locus zygosity combination found
no input that reaches it today (all reachable phenotypes are Normal/Intermediate/
Poor), so this is a latent defect rather than a live one — but it is exactly the
kind that activates when a fourteenth allele or a third drug is added. Now
refused explicitly.

### D5 — The PHI scan did not look inside containers, and unreadable genotypes counted as positive

Two ledger defects, both found by supplying the kind of row a site actually
produces rather than the tidy row the tests used.

- **`_reject_phi` only pattern-checked top-level strings.** `as_dict()` renders
  `toxicity` as a list of dicts and `dose_modifications` as a list of strings —
  which are precisely the **free-text prose fields**, and therefore precisely
  where a phone number or a date of birth actually arrives. A toxicity term of
  `"mucositis, patient called on 9876543210"` was accepted and written to the
  JSONL. Now recursive through lists, tuples and nested mappings, with the
  offending path named (`toxicity[0].term`).
- **`quadrant()` treated any token outside a 4-item literal set as a variant.**
  So `"0|0"` — legal VCF phased wild-type — counted as panel-**POSITIVE**, and so
  did an empty string. Both directions are wrong, and the first moves patients
  *out of* the panel-negative cell the retrospective exists to measure. Now
  wild-type and variant tokens are both enumerated, and anything else is a third
  state: `excluded_unreadable_genotype`, reported rather than absorbed.

### What this round says about the method

The §11 audit asked "what inputs produce a confidently wrong report?" and found
seven. It found none of these five, because it varied the *input shape* while
holding the *patient type* fixed. Four of the five defects here are invisible to
any panel-negative test case, and the fifth needs a spreadsheet rather than a
constructor call. **The generalisable lesson is that an adversarial pass inherits
the blind spot of whatever example it is built around** — and this package's
founding example is the reassured negative patient, so the carrier was
systematically untested. The next pass should start from the ledger and the
NUDT15 path, which have had no adversarial attention at all.

**Verification:** 107 tests pass (86 → 107), `ruff check` clean, `pgx-core` pin
unchanged at 0.7.3. Each new test was confirmed to fail against the pre-fix
behaviour before being accepted.

---

## 14. Research pass 5 — the sources re-tested, and one finding that changes a number (2026-08-16, 23:10)

Pass 4 established the citation posture. This pass went looking for anything that
would change the analysis rather than confirm it. **One finding is material, one
Indian source is new, and the two negative results are worth their own lines.**

### C19 — CPIC has announced a change to HapB3, and it lands on 77.5% of what an Indian panel can find (**material**)

CPIC published a pre-guideline notice on **9 July 2026** (Whirl-Carrillo,
`blog.clinpgx.org`, "CPIC Comment on Pending DPYD Guideline Update"):

> "c.1129-5923C>G, the minor allele at rs75017182 and causal allele associated
> with the 'HapB3' haplotype, will be assigned an allele value of **0.75**. For a
> heterozygous carrier, this corresponds to an activity score of 1.75. For these
> patients, the recommendation is to **initiate treatment at 75% of the intended
> dose in cycle 1**" — with escalation toward standard dosing if tolerated. Full
> guideline expected **fall 2026**.

Today CPIC's value is 0.5, activity score 1.5, Intermediate Metabolizer,
`REDUCE_50PCT`. So a HapB3 heterozygote's dose recommendation is moving from
**50% of standard to 75% of standard** — a substantial relaxation.

**Why this lands harder here than anywhere else.** Computed from CPIC's own
Central/South Asian table:

| actionable allele | CPIC Central/South Asian frequency |
|---|---|
| **HapB3** | **0.019658** |
| `*2A` | 0.005076 |
| c.2846A>T | 0.000640 |
| `*13` | 0.000000 |
| total | 0.025380 |

**HapB3 is 77.5% of the entire actionable allele frequency in this population.**
A guideline-conformant DPYD panel in India is, to a first approximation, a HapB3
test. So a change to HapB3's recommendation changes what *most* Indian
panel-positive patients are told — and it changes it in the direction of **less**
dose reduction.

That is worth stating plainly because it cuts against the natural reading of this
whole document. Our thesis is that the panel **over-reassures the negatives**.
This finding says that for the small minority who test positive, the same panel
has been **over-restricting** them — 50% when the evidence now supports 75%.
Both are the same underlying defect: a European-derived activity score applied
without regard to what it was measured on. The asymmetry is not in our favour or
against it; it is simply that a single number was doing two jobs.

**A gap in our own guard, and the fix.** `scripts/regen_evidence_tables.py
--check` cannot detect this. CPIC states explicitly that the allele value "will
remain at AV=0.5 until then" — so the API returns 0.5, the pinned table says 0.5,
the drift check passes, and the fact that the recommendation is about to move is
invisible to every automated guard we have. Verified: the check passes right now.

**This is a third defect class**, distinct from both prior ones:

| | signal | guard |
|---|---|---|
| 0.7.2 `*6` | we silently deviated from CPIC | `--check` drift guard |
| literature conflict | published evidence disputes CPIC | `P2`/`P3` conflict flags |
| **pending change** | **CPIC disputes its own published value, in advance** | **nothing — until now** |

Fixed as `P4_DPYD_HAPB3_CPIC_UPDATE_PENDING`: a new
`pending_guideline_changes` block in `DPYD_conflicts.json`, a
`pending_change_flags()` emitter, and a report section that prints **both** values
each labelled as what it is — "CPIC's value TODAY (used above)" and "CPIC's
ANNOUNCED value (not applied)".

`asl` deliberately **does not pre-apply the announced value.** Dosing on a
pre-publication blog comment would be an undeclared deviation from the pinned
source of truth — the `*6` failure class pointed the other way. Pinned by
`test_the_announced_value_is_not_applied_to_the_phenotype`, which asserts the
phenotype is still Intermediate Metabolizer, the action still `REDUCE_50PCT`, and
the recorded activity value still `0.5`. The flag is notice, never a
recalculation.

### C20 — A new Indian NUDT15 source, and it is ICMR's own

**Joseph GT, Swain SK, … Rishi B, Misra A. *Front Pharmacol* 16:1714797,
8 December 2025**, from **ICMR-NICHDR** with AIIMS and Safdarjung. Validates a
tetra-primer ARMS-PCR assay for NUDT15 c.415C>T + TPMT`*3C` in 61 Indian
paediatric ALL patients: NUDT15 variants in **16.7%** (9 het, 1 hom), TPMT`*3C`
in 3.3%, no double mutants; 98.4% accuracy vs Sanger (sensitivity 90.9%,
specificity 100%); **>70% cheaper than sequencing**, one working day, needs only a
thermal cycler and gel rig.

Three things this changes:

1. **The NUDT15 wedge is an access problem, and someone has just solved the
   access part.** Pass 3 called NUDT15 "a bigger problem but an access problem,
   not an interpretation one." That is now sharper: an ICMR institute has built
   and validated the cheap assay. The remaining gap is not the test.
2. **It corroborates the ICiCLe dose-intensity mismatch exactly.** NUDT15
   carriers achieved median 6-MP dose intensity **0.50 vs 0.79** wild-type
   (p<0.0001) against a planned 60 mg/m²/day — i.e. ~30 mg/m²/day reached
   reactively, after toxicity, without any genotype being known in advance. Pass
   3 predicted this figure; it is now sourced to the paper it came from.
3. **A caution about its own framing.** The paper's headline selling point is
   *in silico* prioritisation (SIFT/PolyPhen-2/PROVEAN/Meta-SNP/SNPs&GO) of
   variants that were **already known to be the actionable ones**. Computational
   pathogenicity scores agreeing with an established clinical call is not
   independent validation of anything, and the two-variant panel omits NUDT15
   `*2`/`*6` and TPMT `*3A`/`*3B` — which the authors state. **The assay result
   is solid; the in-silico framing around it is decorative.** If we ever cite
   this, cite the 16.7% and the dose-intensity finding, not the SIFT scores.

### C21 — Two negative results, both searched rather than assumed

- **No CPIC DPYD guideline supersedes Amstutz 2018.** The 2017 update (PMID
  29152729) remains the published guideline; the update is *in development*, and
  the only public artifact is the July 2026 comment in C19. Our pinned citation
  is correct.
- **No Indian mandate has appeared.** Searched ICMR and NCG output again. ICMR's
  current public calls are unrelated (diagnostics kits, CAR-2026 grants); NCG's
  visible 2025-26 activity is the **EMR initiative** (PMC12057217), not PGx. This
  is now a *thrice*-searched absence. It also slightly strengthens the C20 point:
  ICMR is funding PGx **assay development** while issuing no testing
  recommendation, which is the gap `asl` sits in.

### What pass 5 changes about the plan

**The architecture is unchanged.** The problem statement is unchanged. What
changed is one engine behaviour and one honest qualification:

1. **`P4` is now a permanent capability, not a one-off.** Any allele whose CPIC
   value is announced-but-unpublished gets a flag. There will be more of these
   when the full guideline lands in fall 2026 — which is now a **scheduled
   clinical-regression review**, not a surprise. Add it to the open items.
2. **The "panel over-reassures" claim needs its counterpart stated.** For the
   ~5% who test positive in this population, the same European-derived activity
   score has been over-restricting them, and CPIC is about to say so. A document
   that only ever argues in the reassuring-direction is doing advocacy. Both
   directions are the same defect.
3. **NUDT15 remains second, but for a better-stated reason.** Not "it's only an
   access problem" — rather, the access problem now has a validated ICMR-built
   solution, so the marginal contribution of an interpretation layer there is
   smaller than for DPYD, where the interpretation defect is the whole problem.

**Verification:** 111 tests pass (107 → 111). `ruff` clean. `--check` still
passes against live CPIC, which is precisely the point of C19. `pgx-core` pin
unchanged at 0.7.3.

---

## 15. Research pass 6 — the ledger's premise tested, and it holds for a reason we had wrong (2026-08-17, 00:30)

Every prior pass tested the *problem*. This one tested the **plan** — specifically
Capability C, the outcome ledger, whose entire value rests on an untested
assumption: that evidence collected in India could actually change CPIC's call.
If that route does not exist, the ledger is a filing cabinet.

**It exists, it has a working precedent, and the DPYD-specific detail is the
opposite of what we assumed.**

### C22 — The reassessment route is real, and there is a precedent for our exact play

CPIC's allele-function framework is now published in full: **Tibben BM, Gaedigk
A, … Caudle KE, *Am J Hum Genet* 2025;112(12):2842–2859, PMID 41175864.** The
mechanism, in CPIC's own words:

> "Reassessment of allele clinical function status is triggered when CPIC becomes
> aware of or receives **an inquiry which cites published literature** supportive
> of evidence against an allele function assignment and the evidence was not
> already assessed by experts."

Then a staff member circulates an interim evidence table to the whole PCEP, and a
new assignment requires **70% consensus**. Anyone may submit; the contact route is
a public form.

**The precedent is close to exact.** From CPIC's statin guideline page:

> "October 2025: **In response to a CPIC member inquiry**, the SLCO1B1
> pharmacogene curation expert panel was convened to reassess allele function
> assignments for **select alleles with elevated frequencies in underrepresented
> populations** and emerging evidence linking them to statin-induced myotoxicity."

That is our argument, for a different gene, already accepted as grounds for
convening a panel. The ledger's premise is validated — with one hard constraint
we already had right: **it requires published literature.** A JSONL file is not
an input to this process; a paper derived from it is. The ledger is therefore
correctly scoped as a route to a publication, not a submission.

### C23 — CPIC *already lowered* the DPYD bar, which inverts our reading of "Normal function"

This is the finding that changes an argument. The framework paper documents that
the evidence threshold is **gene-specific and modifiable**, and gives DPYD as its
worked example:

> "experts may modify this threshold based on the severity of the phenotype and
> relative risk to the patient, such as for *DPYD*… In practice, this type of
> modification has been made for DPYD, for which DPYD intermediate and poor
> metabolizers are at an increased risk of severe or fatal fluoropyrimidine
> toxicity. In this example, **the threshold of evidence for clinical
> actionability was modified to call an allele clinical function for decreased or
> no function alleles in the setting of limited data.**"

The logic is explicit type-II-error avoidance: CPIC weighs "acting on a genotype
which may not have been actionable" against "not acting on one which should have
been", and for DPYD deliberately errs toward **calling an allele actionable on
limited data**.

**Every earlier pass in this document implicitly assumed the opposite** — that
`*9A`, `*6`, `*5` and c.496A>G sit at "Normal function" because CPIC's bar is
high and the Indian-relevant evidence had not cleared it. That reading is wrong,
and the correct one is stronger for the field and weaker for us:

- **Stronger for CPIC.** These four alleles are called Normal *against a
  deliberately lowered bar*. `*9A` and `*5` carry **Strong** evidence, `*6` and
  c.496A>G **Moderate**. CPIC was already leaning toward actionability and still
  did not call them. That is a more considered position than "not yet assessed",
  and any document of ours implying neglect was unfair.
- **Weaker for the "just add the alleles" instinct.** §1's third rejected
  solution — a panel asserting the opposite of CPIC — is now rejected on firmer
  ground. It is not that CPIC has not looked; it is that CPIC looked with a
  thumb on the scale in our direction and still said no.
- **And it sharpens what would actually move the call.** Not more frequency data,
  and not another in-vitro assay. A type-II argument is already priced in, so
  what remains is **clinical outcome data in this population** — precisely and
  only what the MCC retrospective would produce. The go/no-go was already the
  go/no-go; this makes it the *sole* lever.

Nothing in the engine changes. What changes is that `asl` should stop implying
the Normal-function calls are under-examined, because they are not.

### C24 — Two negative results from the same pass

- **No biochemical/clinical divergence exists in DPYD.** CPIC publishes an
  optional `Allele Biochemical Functional Status` that can differ from clinical
  function (`CYP2C9*3` is the canonical case: no function clinically, decreased
  biochemically). We already ingest the field. Checked all 84 DPYD rows carrying
  it: **zero differ from clinical function.** So there is nothing to surface, and
  the report is right not to render a column that would be identical throughout.
  Worth having checked rather than assumed — it was a plausible place for a
  hidden signal about the Indian alleles, and it is empty.
- **No Indian genotype–outcome registry has appeared.** Searched again. What
  exists is a *scoping review* cataloguing actionable variants for Indian practice
  (Kulkarni et al., Tata Institute for Genetics and Society, PMC12286129 — 24
  genes, 57 drugs) and the IPGx registry, which is **US**. The ledger's founding
  premise — that no such registry is open to Indian sites — survives a fourth
  search.

### Engine work in the same session: the ledger's own adversarial pass

`CONTRIBUTING.md` named the ledger as the untested blind spot. Driving
site-shaped rows through it found **eight defects**, and two are severe:

| | defect | why it matters |
|---|---|---|
| **L1** | a patient entered twice was **counted twice, in contradictory cells** | appending a corrected row is how a site edits a log; the append-only design *causes* this |
| **L5** | a `*2A/*2A` homozygote could be recorded as "Normal Metabolizer" | the two columns then came from different sources, and the row poisons the exact analysis the ledger exists for |
| L2 | unreadable genotype tokens accepted at entry | silently excluded from every later analysis; nobody finds out |
| L3 | free-text phenotype accepted | makes the column unanalysable |
| L4 | blank `engine_version` accepted | row cannot be reanalysed when CPIC's tables move — and they are moving |
| L6 | negative cycles, zero and 99 m² BSA accepted | dose-intensity denominators; corrupt quietly rather than loudly |
| L7 | toxicity at cycle 99 of a 2-cycle course | transcription slip between adjacent columns |
| L8 | bare `KeyError` for a missing ID | told a site nothing |

Fixed with `latest_per_patient()` (later rows supersede; the superseded count is
**reported**, not silently applied), entry-time validation, and the same
supersede logic in the CLI, which reads a flat CSV and had the problem
independently. PHI checking moved to run **first**, so a leak is refused whether
or not the rest of the row is well-formed. 114 → 140 tests.

### What pass 6 changes about the plan

1. **The ledger is validated as a mechanism** and correctly scoped: it feeds a
   publication, which feeds a CPIC inquiry, which may convene a PCEP. Not a
   direct submission. The SLCO1B1 precedent is the one to cite when the time
   comes.
2. **Drop any framing that CPIC has under-examined the Indian alleles.** It has
   examined them against a threshold it deliberately lowered for this gene. Our
   position is narrower and more defensible than we had been stating: the
   evidence CPIC weighed is not from this population, and only outcome data can
   change that.
3. **The MCC retrospective is now the single lever, not one of several.** Neither
   frequency data nor in-vitro work can move a call that already has a
   type-II-error thumb on the scale.

---

## 16. Research pass 7 — the NUDT15 workflow tested, and it does *not* inherit the DPYD thesis (2026-08-17, 00:55)

The engine gap is fixed (`pgx-core` 0.8.0 adds `NUDT15Caller`), so this pass
tested what a NUDT15 workflow would actually rest on. **Three of the four
findings cut against our own prior reasoning.** Read the CPIC 2025 thiopurine
guideline directly (Maillard et al., *Clin Pharmacol Ther* 2026;119(4):916–927,
PMID 41618934).

### C25 — The ICiCLe dose mismatch pass 3 flagged is **not** a mismatch. CPIC already addressed it.

Pass 3 wrote that ICiCLe-ALL-14's 60 mg/m²/day 6-MP against CPIC's 75 mg/m²/day
reference is "exactly the kind of guideline-to-local-protocol mismatch `asl`
exists to surface." CPIC's actual recommendation, verbatim:

> "Initiate therapy with decreased starting doses (30–80% of standard starting
> dose) **if starting dose is ≥ 75 mg/m²/day** (for malignancy)… **If starting
> dose is already below standard starting dose, dose reduction might not be
> necessary.**"

ICiCLe's 60 mg/m²/day is below 75, so CPIC's guidance at the Indian protocol dose
is explicitly *that a reduction may not be needed*. There is no gap for a software
layer to surface. CPIC even states the general principle: "because the level of
thiopurine tolerance is related to genetic ancestry, **the standard starting doses
can vary by geographic regions**."

**Pass 3 read a conditional as an oversight.** The recommendation is
dose-conditional by construction, and we had quoted only the unconditional half.
That is the same error class this document keeps finding — a claim with its
qualifier stripped — committed by us, about CPIC, in the direction of
manufacturing a problem.

### C26 — CPIC explicitly asserts cross-ancestry robustness for NUDT15/TPMT, which DPYD does not have

This is the finding that limits the second workflow, and it is a direct
contrast with the gene this whole document is about:

| | DPYD | NUDT15 / TPMT |
|---|---|---|
| published position on ancestry | activity score "validated in the Caucasian population, remains **unverified** in other ethnic groups" (White 2021, PMID 34916829, cited approvingly by D-TORCH) | "given the **robustness of the genotype–phenotype associations** for both TPMT and NUDT15 **across diverse populations**… the recommendations are **not limited to any specific ancestry group**" |
| Indian outcome data | two sources, disagreeing | consistent with East Asian; no contradicting Indian cohort found |

So **the `asl` thesis does not transfer.** For DPYD, the interpretation layer is
applying a score its own authors say is unvalidated here. For NUDT15, CPIC
asserts the opposite, and the variant that carries the Indian signal —
`*3`/rs116855232 — is the *most* studied variant in the gene, with CPIC calling
its evidence "the strongest evidence for clinical implementation."

That confirms, on stronger grounds than pass 3 had, that **NUDT15 is an access
problem and not an interpretation one.** It also means a NUDT15 workflow in `asl`
would be a *thinner* product: correct calling and provenance, but no
residual-risk argument of the kind DPYD supports, because the guideline's own
population caveat is absent.

### C27 — But CPIC hands us the exact structural analogue of the DPYD caveat

One sentence in "Other Considerations" is directly usable:

> "If test results are available for only one gene (*TPMT* or *NUDT15*, but not
> both), prescribing recommendations based on that gene's results may be
> implemented, with the caveat that the other gene's results are missing and may
> have important implications, with **up to 10–15% of patients having actionable
> variants in the nontested gene**."

This is the thiopurine equivalent of "a genetic test investigating only selected
variants does not fully rule out DPD defects" — a **guideline-published residual
risk with a number attached**, for the single most likely real-world scenario in
India, where the ICMR-validated ARMS-PCR assay reads NUDT15 c.415C>T and TPMT`*3C`
and nothing else. And CPIC adds a second one: a rare variant outside the test
design means "the patient being assigned a 'wild‐type' (`*1`) genotype **by
default**" — our founding defect, stated by the guideline.

So the second workflow's honest shape is now clear: **not** "CPIC is wrong for
Indians", but "this panel tested one of two genes, here is what that leaves
open, quantified by CPIC."

### C28 — A newly-actionable allele is not callable, and that is now on the record

The 2025 update **reassigned `*4` and `*9` as clinically actionable** ("the
accumulation of preclinical and clinical data associating some rare variants with
thiopurine toxicity motivated their re-assignment"). Of those two:

- `*4` (rs147390019) **is** callable in 0.8.0.
- `*9` is defined by a `GAGTCG(2)` indel and is **not** callable — `pgx-core`
  matches single plus-strand bases from a VCF.

`*9`'s Central/South Asian frequency is 0.000495, so the practical impact is
small, but the honest statement is that a *newly actionable* allele is outside the
caller's reach, and it is recorded in the generated table header rather than left
to be discovered. Indel-aware matching is the fix and is not attempted here.

### Open item found and not closed

The guideline carries a **correction notice** (*Clin Pharmacol Ther*, 28 April
2026). Not yet read. Any figure quoted from PMID 41618934 should be checked
against it before it reaches a clinical report — the 30–80% and 20–50% ranges
above are from the original.

### What pass 7 changes about the plan

1. **Remove the ICiCLe "mismatch" from the plan.** It was our misreading. What
   remains true and useful is narrower: an Indian protocol starting below CPIC's
   reference dose is a case where CPIC says a reduction may be unnecessary, and a
   tool should say *that* rather than invent a conflict.
2. **The NUDT15 workflow is demoted in ambition, not dropped.** It becomes a
   correct-calling-plus-coverage product built on C27's single-gene caveat, not a
   population-interpretation argument. Which is honest: nobody has shown CPIC
   wrong for NUDT15 in Indians, and CPIC has affirmatively argued it is right.
3. **DPYD's uniqueness is now established by contrast rather than asserted.** The
   reason this platform started with DPYD is that DPYD is the gene where the
   guideline's own authors say the score is unvalidated outside Europeans. That is
   not true of the second gene we looked at, which is a meaningful check on
   generalising the thesis.

**Verification:** `pgx-core` 235 tests pass, 2 `cpic_live` pass, NUDT15 drift
check clean. `asl` unchanged at 140 tests and still pinned to 0.7.3 — 0.8.0 is not
on PyPI, and `AGENTS.md` requires clinical regression review before a consumer
adopts a new engine version.

---

## 17. The TPMT defect — found by fixing something else (2026-08-17, 01:20)

Pass 7 left one open item: read the correction notice to the CPIC 2025 thiopurine
guideline before quoting figures from it. Doing that led somewhere unexpected.

### The correction itself is minor, and we had already handled it

CPIC corrected **Table 1** of the guideline (*Clin Pharmacol Ther*, 13 May 2026,
doi 10.1002/cpt.70298): one no-function allele plus one decreased-function allele
is an **Intermediate Metabolizer**, not a *Possible* Intermediate Metabolizer as
printed. Therapeutic recommendations are identical for both, so the clinical
effect is nil.

None of the figures quoted in §16 came from Table 1, so nothing in this document
needed changing. And the NUDT15 tables generated yesterday came from the live
API, which is post-correction — verified. **The generate-don't-transcribe rule
absorbed a guideline correction without anyone acting on it**, which is the first
time that discipline has paid off observably rather than argumentatively.

### But checking it exposed a genotype-inverting defect in TPMT

While confirming the correction was reflected, I diffed the hand-authored TPMT
tables — the last thiopurine artifacts not generated from CPIC — against the live
API. **Three independent defects, and the whole suite passed throughout.**

**1. Six wrong ALT bases, one inverting.** The `*3A` row was
`rs1800460` / `alt='C'`, but CPIC's `chromosomelocation` is `g.18138997C>T`, so
`C` is the **reference** base:

| sample | called | truth |
|---|---|---|
| homozygous **reference** | `*3A/*3A` **Poor Metabolizer** | `*1/*1` Normal |
| `*3A` heterozygote | `*1/*3A` | `*1/*3A` (correct by luck) |
| `*3A` **homozygote** | `*1/*1` **Normal Metabolizer** | `*3A/*3A` Poor |

A healthy patient was told to avoid thiopurines; a true poor metabolizer was
cleared for full dose. `*4` and `*8` carried the same inversion, and `*7`, `*23`,
`*38` pointed at the wrong rsID entirely.

**This is the DPYD strand defect, exactly.** Same mechanism (cDNA vs plus-strand
genomic notation), same gene family of consequence, same reason it survived: the
**test fixtures encoded the same wrong convention** (`ref="G", alt="C"` at
rs1800460), so table and test were wrong *together* and agreed. The DPYD write-up
in 0.7.2 named this failure mode explicitly — "a wrong convention that is
self-consistent across code and fixtures is invisible to tests written in it" —
and it was sitting in the next gene over the entire time.

**2. Four allele-function divergences from CPIC**, the 0.7.2 `*6` failure class
again, none recorded as a deliberate judgement: `*8` No→**Decreased** (as *No
function*, `*1/*8` computes Intermediate where CPIC publishes **Normal** —
over-restricting), `*23` Decreased→**No**, `*24` Decreased→**Uncertain**, and
`*3D` asserting a function **CPIC does not publish at all**.

**3. Coverage: 17 of CPIC's 1225 diplotypes**, leaving **66 caller-reachable
diplotypes with no phenotype**. A `*6` heterozygote — a no-function allele —
returned `Indeterminate` where CPIC publishes *Intermediate Metabolizer*. Every
one of the 17 rows was *correct*, which is why nothing failed. The defect was
coverage, and coverage defects are invisible to tests written against the covered
rows.

### And a fourth problem the fix itself exposed

Generating the table correctly made `*3A` heterozygotes resolve to `*3A/*3B` —
Poor instead of Intermediate. CPIC defines `*3A` by **two** loci
(`rs1800460:T` + `rs1142345:C`) and `*3B`/`*3C` by one each — *the same two loci*.
Single-rsID matching, which is the library-wide pattern, cannot distinguish a
`*3A` heterozygote from a `*3B`/`*3C` compound heterozygote.

`TPMTCaller` is now haplotype-aware: longest-match-first with copy consumption, so
a two-locus haplotype claims its loci before either subset. **Stated honestly as
an unphased inference, not a phase determination** — one copy at each locus is
genuinely ambiguous, and `*3A` is selected because it is far the commoner haplotype
(European 0.0338 vs `*3B` 0.0028) *and* because it is the non-over-restricting
reading. A phased laboratory result should override it.

### What this says about the method, and about `asl`

Three things worth recording:

1. **`asl` was never affected.** Its TPMT evidence table was generated from CPIC
   from the start, so it carries `*8` as *Decreased function* and `*24` as
   *Uncertain* — correct, while the engine underneath it was wrong. The
   generated-not-authored rule protected the layer that adopted it.
2. **The defect was found by pursuing an unrelated open item.** Nobody audits TPMT
   for its own sake; it is not the wedge gene. It surfaced because reading a
   correction notice required checking whether our tables reflected it.
3. **A published post-mortem does not prevent recurrence in a sibling.** 0.7.2
   documented this exact failure mode in detail, and the next gene had it. The
   generalisable fix is not "be careful with strands" — it is that **every
   allele table must be generated, and every ALT checked against CPIC's own
   notation rather than against our fixtures**, which is now a `cpic_live` test.

Shipped as `pgx-core` **0.8.1**. 235 → 252 tests, `cpic_live` 2 → 5, both drift
checks clean. Consumer pins remain at 0.7.3 — neither 0.8.0 nor 0.8.1 is on PyPI,
and `AGENTS.md` requires clinical regression review before adoption. **That review
now has a specific reason to happen: the TPMT correction is a patient-safety fix,
not a feature.**

---

## 18. Engine decisions taken: the regression review, and two absent safety nets (2026-08-17, 01:45)

The standing blocker was that `AGENTS.md` requires clinical regression review
before a consumer adopts a new engine, and no such review had been done for
0.8.0/0.8.1. Taking that decision as engine maintainer rather than deferring it.

### The review, and why it had to be mechanical

`scripts/regression_review.py` enumerates every callable allele of all 12
star-allele genes in three zygosity states, plus every within-gene compound
heterozygote whose loci do not collide — **1,901 genotype cases** — calls each on
both engine versions, and classifies every difference by **clinical direction**
rather than by "did the output change".

| class | n |
|---|---|
| `SAME` | 917 |
| **`SAFETY_FIX`** (was permissive → now restrictive) | **572** |
| `NEWLY_RESOLVED` (was Indeterminate → now called) | 221 |
| `NEW_GENE` (NUDT15) | 133 |
| `NEWLY_INDETERMINATE` | 20 |
| `PHENOTYPE_CHANGE` (lateral) | 20 |
| `NOMENCLATURE` | 17 |
| `OVER_RESTRICTION_FIX` | 1 |

**The decisive line: every difference is in TPMT.** The other eleven genes are
bit-identical across all 1,901 cases, so **DPYD — the only gene any consumer
calls in anger — is untouched**. That converts adoption from a judgement call into
a bounded one.

The `OVER_RESTRICTION_FIX` is the headline: TPMT `*4` **homozygous reference** went
from `*4/*4` "Poor Metabolizer, avoid thiopurines" to `*1/*1` Normal. A patient
with no TPMT variant at all was being contraindicated.

The 20 `NEWLY_INDETERMINATE` cases were adjudicated individually rather than
waved through: all involve `*9`/`*12`/`*30`/`*32`/`*40`, all **Uncertain
function**, and CPIC's own diplotype table returns `Indeterminate` for them. 0.7.3
was failing to *detect* these alleles and reporting "Normal Metabolizer" — so this
class **removes a false reassurance**. All five are 0.0 frequency in
Central/South Asian, so Indian impact is nil regardless.

**Verdict: approved.** Recorded in
`anukriti-pgx-core/docs/REGRESSION_REVIEW_0.7.3_to_0.8.1.md`.

### Two safety nets that were not there — and both produced *passing* results

This is the part worth remembering.

**1. The first review run was vacuous and looked fine.** It reported
"old engine: 0.7.3, new engine: 0.7.3 — SAME: 1901". Two independent causes,
either sufficient:

- **0.8.0 shipped with its version string out of sync.** `pyproject.toml` said
  0.8.0; `version.py` still said 0.7.3. Every `PhenotypeInference` carries
  `pgx_core_version`, so for a day the engine was **misreporting which version
  produced a call** — the audit trail the three version planes exist for.
- **`python -c` prepends the CWD to `sys.path`**, so the *old* interpreter,
  invoked from the repo root, imported the local source instead of its own
  installed package. Both engines were the same code.

A review that cannot distinguish the versions is worse than no review, because it
produces a green tick. Now: `-I` isolation, a hard refusal if both interpreters
self-report the same version, and `tests/test_version_consistency.py`.

**2. `anukriti-api` CI had not passed since 21 July — four weeks.** Not for any
code reason: `anukriti-chemistry==0.1.0` is a hard dependency that was never
published, so `pip install .` failed before a single test ran. I only found it
because my own pin bump turned CI red and I checked the history to confirm the
cause was mine. It was not.

The metadata was wrong about the code: `_chemistry_context` already wraps the
import and returns `{"available": false, "reason": "…not installed"}` rather than
fabricating, which is correct for a narration-only input. Optional in code,
mandatory in metadata. Now an extra, and CI is green for the first time since July.

**A suite that cannot install is not a failing suite — it is an absent one**, and
it reports as a failure indistinguishable from a real one, which is how it
survived a month.

### The pin decision, made and then reversed on evidence

I bumped all four verifiable consumers to `==0.8.1` after re-running each suite
against the new engine: `asl` 140, `anukriti-api` 184, `anukriti-swarm` 287,
`cohortfit` 241 — all pass, no code changes needed. Then **reverted every one**,
because 0.8.1 is not on PyPI: its publish job waits on a protected-environment
approval only an admin can grant. An exact pin to an unpublished version does not
merely redden CI, it **breaks `pip install` for anyone cloning the repo** — a
worse failure than running one release behind. Each pin now carries a comment
saying it is reviewed, approved, and held pending publication.

`anukriti` (sandbox) and `anukriti-validation-iwpc` were **left at 0.7.3
deliberately**: no runnable environment here, and bumping a pin whose suite you
have not executed is asserting a review you did not perform.

### The one action I did not take

`v0.8.0` and `v0.8.1` are tagged and pushed; the PyPI publish jobs are queued
behind an admin approval on a protected environment. That gate is the correct
control for an irreversible public artifact and I did not attempt to route around
it. **It is the only outstanding item**, and the pin bump is a one-line change per
consumer once it clears.

### Method note

Every defect in this session was found by pursuing something else: the TPMT
inversion came from reading a correction notice; the version desync came from
running the review; the four-week CI outage came from checking whether I had
broken CI. None would have been found by looking for them. The transferable part
is that **the checks which fail silently are the dangerous ones** — a wrong
answer announces itself, a vacuous review and an uninstallable suite do not.
