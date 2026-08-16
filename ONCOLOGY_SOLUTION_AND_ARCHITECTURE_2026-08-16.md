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

### C4 — The Indian evidence base is ~630 patients across 4+ centres, not 76 from 1

The 08:29 document called this its own biggest weakness ("the entire problem
statement rests substantially on one small study"). That was too pessimistic.

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
and **35/47 had grade II-III toxicity even after dose reduction** (χ², p=0.002).

That is **independent Indian corroboration, at 5× the n, that a CPIC
normal-function allele tracks severe toxicity.** The problem statement no longer
rests on one 76-patient study whose tables we had to correct ourselves.

Genotype-only evidence adds 1064 more patients (Patil 2019, 27.2% carrying
rs1801160/rs1801159), useful for frequency but silent on outcome.

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
Real, verified, and not an edge case for Indian patients.** Executed:

| Input | Copies detected | Engine output |
|---|---|---|
| `*9A` hom | 2 | `*9A/*9A` ✓ |
| `*9A` het + `*6` het | 2 | `*6/*9A` ✓ |
| **`*9A` hom + `*6` het** | **3** | **`*6/*9A`** — one copy dropped, silently |
| **`*9A` hom + `*6` het + M166V het** | **4** | **`*6/*9A`** — two dropped, silently |

A diploid genome has two DPYD chromosomes, so >2 copies means the input is
inconsistent, unphased across a haplotype, or a genotyping artifact. Whatever the
cause, **the caller must not resolve it by quietly discarding alleles.** In
Europeans this is rare. In Indians it is *expected*: `*9A` 0.25526, `*6` 0.09506,
M166V 0.08517 — P(≥3 copies across these three loci) is not small.

*Action:* file against `pgx-core` for 0.7.3 — emit an
`OVERSPECIFIED_GENOTYPE` signal (or `Indeterminate` with the full detected
allele list preserved) rather than truncating. **`asl` must not paper over this**:
`interpret` refuses when detected copies exceed 2 and surfaces the full list.
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
  alternative** — it measures enzyme activity, not genotype, and would sidestep
  this entire problem. Not proposed because no Indian lab offers it and the
  16 ng/mL threshold is unvalidated outside French cohorts. **If a partner site
  has LC-MS/MS, this ranking should be revisited**, and that would be a better
  outcome than our product.
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

1. **File `pgx-core` 0.7.3** for §5.6 Defect 1 — over-specified genotypes must
   not silently drop alleles. Highest priority: it is the same failure class as
   the 0.7.2 strand defect and it disproportionately affects Indian patients.
2. **Scope `asl` Phases 0–2.** Phase 0 is done (0.7.2 shipped, five consumers
   bumped). Phase 1 is `regen_evidence_tables.py`, which is a near-copy of
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
