# Malabar Cancer Centre — institutional profile from MCC's own published reports

**Compiled:** 2026-10-17
**Compiled by:** Claude Code, from primary sources only (MCC annual reports 2017-18 through 2024-25)
**Status:** Research note. Nothing here has been confirmed with MCC. Not for external use.

---

## Why this document exists

Before today, everything this workspace recorded about MCC traced to a **single discovery
call on 2026-05-27** (`raw_conversation.md`). A sweep of all ~17 repos found no patient
volume, no catchment, no case-mix, **zero** mentions of HBCR / NCDIR / ICMR in connection
with MCC, and nothing at all about MCC's data systems.

MCC publishes a detailed annual report every year and has done since 2012-13. Thirteen are
online. Nobody had read them.

The driving question: **where does a fluoropyrimidine order get placed at MCC, and what data
do they hold?** It was explicitly excluded from the June visit pack
(`mcc-visit/03_structured_ask.md:75` — "❌ Any change to their current clinical workflow
during the pilot"), so it has never been asked.

---

## Sources

All annual reports are public PDFs on the Kerala Health Department portal. MCC's own site
(`mcc.kerala.gov.in`) returned **HTTP 503 on every attempt** on 2026-10-17; the health-portal
mirror worked.

| Year | URL |
|---|---|
| **2024-25** | https://health.kerala.gov.in/assets/backend/uploads/Galleryitem/1776518056130087995.pdf |
| **2023-24** | https://health.kerala.gov.in/assets/backend/uploads/Galleryitem/1776077751876500736.pdf |
| **2022-23** | https://health.kerala.gov.in/assets/backend/uploads/Galleryitem/1776518050573804646.pdf |
| 2021-22 | https://health.kerala.gov.in/assets/backend/uploads/Galleryitem/17701009581544886730.pdf |
| 2020-21 | https://health.kerala.gov.in/assets/backend/uploads/Galleryitem/1770100975520025180.pdf |
| 2019-20 | https://health.kerala.gov.in/assets/backend/uploads/Galleryitem/17701009961919859084.pdf |
| 2018-19 | https://health.kerala.gov.in/assets/backend/uploads/Galleryitem/1770101008261781313.pdf |
| 2017-18 | https://health.kerala.gov.in/assets/backend/uploads/Galleryitem/17701010521115717848.pdf |
| 2016-17 | https://health.kerala.gov.in/assets/backend/uploads/Galleryitem/1776077743442312434.pdf |
| 2015-16 | https://health.kerala.gov.in/assets/backend/uploads/Galleryitem/17701010621109689826.pdf |
| 2014-15 | https://health.kerala.gov.in/assets/backend/uploads/Galleryitem/17701010721869045979.pdf |
| 2013-14 | https://health.kerala.gov.in/assets/backend/uploads/Galleryitem/17701010811273204438.pdf |
| 2012-13 | https://health.kerala.gov.in/assets/backend/uploads/Galleryitem/17760777351316909051.pdf |

Index page: `https://health.kerala.gov.in/publicationdetails/` (Annual Reports → Malabar
Cancer Centre). Secondary, weaker: [UICC profile](https://www.uicc.org/membership/malabar-cancer-centre),
[Wikipedia](https://en.wikipedia.org/wiki/Malabar_Cancer_Centre,_Thalassery).

Reports read in full for this note: 2017-18, 2021-22, 2022-23, 2023-24, 2024-25.
**The 2024-25 report is current** — this profile is not stale.

---

## 1. The institution

- **Malabar Cancer Centre, Post Graduate Institute of Oncology Sciences and Research**,
  Moozhikkara P.O., Thalassery, Kannur district, Kerala — 670103.
- Autonomous centre under the Government of Kerala, Health & Family Welfare Department.
  Affiliated to Kerala University of Health Sciences.
- Started 2000, inaugurated 2001, transferred to Health Department 2008, declared a Post
  Graduate Institute June 2022.
- Tertiary cancer centre for northern Kerala. Catchment: Kannur, Kasaragod, Mahe primarily;
  Wikipedia adds neighbouring Karnataka and Tamil Nadu.
- NABH accredited 2020, **re-accredited 2024**, plus **NABH Digital Health Standards — Silver
  Level, 2024** (see §4 — this matters).
- DNB/DrNB training including a seat in **Gastrointestinal Oncology**.
- Robotic surgical system installed in 2024-25.

### Volume trend

| Measure | 2017-18 | 2021-22 | 2022-23 | 2023-24 | 2024-25 |
|---|---:|---:|---:|---:|---:|
| Total new registrations | 6,723 | 8,306 | 7,795 | 7,748 | **8,214** |
| Follow-up visits | 63,278 | — | 85,802 | 102,576 | **113,791** |
| Total patient visits | 72,621 | — | 93,597 | 110,324 | **120,205** |
| Inpatients | 4,621 | — | 5,566 | 5,865 | **6,406** |
| Deaths | — | — | 135 | 152 | 187 |
| Major surgeries | 1,198 | — | 2,047 | 2,130 | **2,396** |
| Endoscopies | 2,516 | — | 2,000 | 2,317 | 2,354 |
| **Day chemotherapy administered** | — | 17,132 | 17,906 | 18,546 | **22,513** |

Day chemotherapy is up **31% in three years**. That is the denominator any fluoropyrimidine
argument rests on.

---

## 2. What kind of cancer patients they have

**Source: Hospital Based Cancer Registry Report 2022, published inside the 2024-25 annual
report. Total registered 2022: 6,059 cancer patients — Male 3,130 (51.7%), Female 2,929 (48.3%).**

### HBCR annual series (published as a chart, 2010-2022)

| 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2,254 | 2,580 | 3,143 | 3,824 | 4,042 | 3,926 | 3,924 | 4,627 | 5,195 | 5,207 | 5,459 | 6,174 | 6,059 |

(2021: 6,174 — M 3,153 / F 3,021, per the 2023-24 report.)

### Ten leading sites, 2022 — Males (n = 3,130)

Percentages are published; counts marked ~ are derived by me (% × 3,130).

| Rank | Site (ICD-10) | % | Count |
|---:|---|---:|---:|
| 1 | Lung etc. (C33-34) | 17.0 | **533** (published) |
| 2 | **Stomach (C16)** | 6.1 | **190** (published) |
| 3 | Mouth (C03-06) | 6.0 | ~188 |
| 4 | Liver (C22) | 5.9 | ~185 |
| 5 | **Rectum (C19-20)** | 5.2 | ~163 |
| 6 | Non-Hodgkin lymphoma (C82-85, C96) | 5.2 | ~163 |
| 7 | Prostate (C61) | 4.4 | ~138 |
| 8 | Larynx (C32) | 4.1 | ~128 |
| 9 | Tongue (C01-02) | 4.0 | ~125 |
| 10 | **Colon (C18)** | 3.8 | ~119 |

Oesophagus dropped out of the male top ten in 2022 (it was 3.5% in 2020), so it is <3.8%, i.e. <~119.

### Ten leading sites, 2022 — Females (n = 2,929)

| Rank | Site (ICD-10) | % | Count |
|---:|---|---:|---:|
| 1 | **Breast (C50)** | 29.2 | **856** (published) |
| 2 | Thyroid (C73) | 8.6 | **253** (published) |
| 3 | Cervix uteri (C53) | 5.8 | ~170 |
| 4 | Ovary etc. (C56) | 5.8 | ~170 |
| 5 | Corpus uteri (C54) | 5.8 | ~170 |
| 6 | **Rectum (C19-20)** | 4.3 | ~126 |
| 7 | Lung etc. (C33-34) | 4.1 | ~120 |
| 8 | **Colon (C18)** | 3.9 | ~114 |
| 9 | Non-Hodgkin lymphoma (C82-85, C96) | 3.7 | ~108 |
| 10 | Mouth (C03-06) | 2.9 | ~85 |

### For comparison — the 2020 registry (n = 5,459; M 2,879 / F 2,580)

Males: Lung 18.9, Mouth 6.8, NHL 5.6, Stomach 5.6, Tongue 5.5, Rectum 5.1, Liver 4.6,
Prostate 4.6, Larynx 4.1, Oesophagus 3.5. *(Colon below cutoff.)*
Females: Breast 30.7, Cervix 7.4, Ovary 6.5, Corpus uteri 4.8, Lung 4.5, NHL 4.0, Mouth 3.5,
Thyroid 3.3, Rectum 3.2, Colon 2.9.

Both colon and rectum are in **both** sexes' top ten by 2022, which they were not in 2020.
Female thyroid also jumped 3.3% → 8.6%.

### Leading sites by age band (2020 registry)

| Band | Males | Females |
|---|---|---|
| 0-14 | Lymphoid leukaemia 27.2, Myeloid leukaemia 16.0, Brain/CNS 14.8, Bone 6.2, NHL 6.2 | Lymphoid leukaemia 28.6, Myeloid leukaemia 14.3, Brain/CNS 10.7, Eye 8.9, Bone 8.9 |
| 15-34 | Lymphoid leukaemia 14.1, Myeloid leukaemia 12.8, NHL 12.1, Bone 10.1, Brain/CNS 8.7 | Breast 22.0, Thyroid 11.9, Bone 11.0, Brain/CNS 6.4, NHL 6.4 |
| 35-64 | Lung 16.2, Tongue 8.6, Mouth 8.0, NHL 7.2, Stomach 5.7 | Breast 38.9, Cervix 7.8, Ovary 7.7, Corpus uteri 5.3, Lung 4.0 |

### Fluoropyrimidine-relevant burden, 2022 — DERIVED

My arithmetic on published percentages, not an MCC figure.

| Group | Annual cases | Relevance |
|---|---:|---|
| **Colorectal** (M rectum ~163 + M colon ~119 + F rectum ~126 + F colon ~114) | **~522** | Core 5-FU / capecitabine indication |
| Stomach (M 190 published; F below cutoff, <~85) | ~190-275 | 5-FU-based regimens standard |
| Oesophagus (below cutoff both sexes) | <~200 | 5-FU-based chemoradiation |
| **GI subtotal** | **~700-900** | |
| Breast (female) | 856 | Capecitabine in a *subset* only |

Corroborated in prose: Medical Oncology's listed spectrum leads "Breast cancer,
**Gastrointestinal cancers**, Lung cancer, Head and Neck cancers…"; Surgical Oncology performs
"major resections of cancer involving **colorectum, stomach, esophagus**"; 258 colonoscopies
(2022-23); they publish on microsatellite instability in colorectal cancer.

---

## 3. 🔴 DPYD testing at MCC — it exists, and it is scaling

**DPYD is a listed, routine molecular test at MCC.** Volumes by year, from the Cytogenetics
and Molecular Oncology tables:

| Year | DPYD tests | Day chemo sessions |
|---|---:|---:|
| 2022-23 | **2** | 17,906 |
| 2023-24 | **8** | 18,546 |
| 2024-25 | **19 or 276 — see below** | 22,513 |

### ⚠️ The 2024-25 report gives two different numbers

The same PDF contains two molecular-test tables that disagree, and not only on DPYD:

| Test | "Profile at a glance" table (p. ~18) | Molecular Oncology Division table (p. 63) |
|---|---:|---:|
| **DPYD mutation** | **276** | **19** |
| BCR-ABL quantitative | 381 | 383 |
| EGFR | 112 | 29 |
| AML panel | 520 | 68 |
| ALL panel | 280 | 45 |
| Myeloma panel | 300 | 62 |
| MPN panel | 328 | 41 |
| **Table total** | **2,463** | **843** |

The institutional table is ~3× the divisional one throughout. Plausible explanations: the
profile table aggregates Genetics *and* Molecular Oncology divisions, or counts assays/samples
while the division counts patients. **Unresolved. Do not quote either figure externally until
MCC confirms which is which.** In 2023-24 the two tables agreed (8 and 8), which makes the
2024-25 divergence more notable, not less.

### What it means either way

- **If 19:** DPYD is tested in roughly **3-4% of colorectal patients alone**, and under 1% of
  the plausible fluoropyrimidine-exposed population. The assay is on the menu, the lab runs
  it, the LIMS reports it — and it is essentially never ordered. That is exactly the failure
  mode in the implementation literature (~70% of sites globally rely on the clinician
  remembering — Dana-Farber PMID 38608224, PGRN PMID 41456101), with a **local, published,
  Indian number** instead of a foreign citation.
- **If 276:** uptake is already **~50% of colorectal** or ~30% of all GI, and MCC is one of
  the most DPYD-active centres in India. That is a *different* and arguably better story —
  a real pre-emptive testing programme to measure, not a gap to fill.

**Either way the trajectory 2 → 8 → (19 or 276) is a rising line, and MCC is doing this
without anyone asking them to.** The question of which number is right changes what Anukriti
would even be offering, so it is the single highest-value question to resolve.

### Other molecular capability (2024-25)

BCR-ABL quant 381/383, ALL panel, AML panel, MPN panel, myeloma panel, EGFR, JAK2, PML-RARα,
and FISH for BCR-ABL, PML-RARα, HER2, SS18, ALK, ROS, EWSR, triple-hit, FOX01, chimerism.
Oncopathology issued 12,886 reports in 2024-25 (556 flow cytometry, 1,142 frozen sections).
Cancer Genetics Clinic — claimed first in Kerala.

---

## 4. 🟡 IT systems — can an order-time trigger exist here?

### The trajectory is documented and fast

- **2014** — e-Hospital (HMIS) first implemented.
- **2017-18** — Phase-I complete, Phase-II in progress. Lab equipment interfaced. Virtual
  Tumour Board with the National Cancer Grid. Medical Records still *scanning* paper
  "towards digitisation". "Template based chemotherapy delivery in medical oncology (solid
  tumor division) was introduced."
- **2022** — MOCDOC LIMS implemented; analyzers interfaced with e-Hospital for automatic
  report generation across "Biochemistry, Pathology, Microbiology, **Molecular, Genetics**,
  blood bank".
- **2022-23** — Surgical Oncology: "all cases are documented online and the department is
  ready to proceed further **as the rest of the departments and services catch up**."
- **July 2023** — "E-Hospital software: User role-based access control guideline, Ver. 1.0".
- **2024** — **NABH Digital Health Standards, Silver Level accreditation.**

### The 2024-25 director's statement (quoted in part)

The report states that through the support of the **National Cancer Grid**, MCC "has initiated
its journey to become a paperless and queue less hospital through comprehensive digital
solution for the entire hospital and it includes **electronic medical records incorporated
hospital management system**."

### 🔴 The finding that most changes the order-time-trigger question

> **Dr. Chandran K Nair** (Professor, Medical Oncology, MCC) "was appointed by **National
> Cancer Grid as the chair for the committee for preparing a complete Medical oncology module
> in future EMR to be implemented across NCG centers in India**."
> — 2024-25 annual report, Medical Oncology, Awards & Recognitions

The person chairing the design of the **national chemotherapy EMR module** for the National
Cancer Grid works at MCC, in the department that would place the fluoropyrimidine order.

This reframes the whole question. The order-time trigger does not need a bespoke MCC
integration — the relevant surface is the NCG medical-oncology EMR module, and its chair is
already our prospective partner's colleague. It also means the module **does not exist yet**
("future EMR"), so this is design-stage, not retrofit.

### Software inventory, 2024-25

e-Hospital@NIC (HMIS) · eBloodbank (NIC) · e-office · MOCDOC LIMS · PACS interfaced with
e-Hospital · ePalliative · Online Examination System · HR/Payroll · **File Movement Tracking
Software "for tracking the movement of patient physical file across different divisions"** ·
OPPAM WhatsApp grievance system · IntraMCC.

### What is still UNKNOWN

**Whether chemotherapy is prescribed/ordered inside e-Hospital today, or written on paper
while e-Hospital carries registration, billing, labs and records.**

Evidence pulls both ways: NABH Digital Health Silver and an "EMR-incorporated HMS" ambition
on one side; a live **physical-file tracking system** and a *future* NCG oncology EMR on the
other. "Paperless" is described as a journey *initiated*, not completed.

**This cannot be settled from published documents. It needs one question to MCC.**

---

## 5. People

| Person | Role (from the reports) |
|---|---|
| Director | named in the annual reports |
| **the MCC Molecular Oncology lead** | **Assistant Professor; Division In Charge, Molecular Oncology Division**. Our contact. Co-author on the draft paper. |
| Second Molecular Oncology academic | Assistant Professor, Molecular Oncology. Projects on biomarkers for early colon cancer detection. |
| **Dr. Chandran K Nair** | **Professor, Medical Oncology. NCG chair for the national Medical Oncology EMR module.** |
| Two further Medical Oncology academics | Assistant Professors, Medical Oncology |
| Registry lead and biostatistician | Registry & Epidemiology |

The Molecular Oncology division is a **small lab**: two academic staff and three technical staff.

`01_pilot_lead_record.json:5` still says "confirm full name" for the MCC Molecular Oncology lead and `:8` has his email
as "TBD". Both are now answerable: he is the MCC Molecular Oncology lead, Assistant Professor and
Division In Charge of Molecular Oncology.

---

## 6. Data and governance assets

- **Hospital Based Cancer Registry** — started 2011 under ICMR's National Cancer Registry
  Programme; NCDIR/ICMR funded; uses HBCR-DM-SOR tooling; annual reports published at least
  for 2015, 2020, 2021, 2022. Collects "patient demographic information, cancer
  identification, diagnostic procedures, cancer-directed treatment, and **survival**."
- **Malabar Population Based Cancer Registry** — launched 2014 (Kannur, Kasaragod, Mahe),
  **expanded 2018** to add Kozhikode, Malappuram, Wayanad, Thrissur, Palakkad. Reports for
  2014-2017, and a 2015-2018 PBCR report in the 2023-24 annual report with district-level
  leading-site tables for Kannur and Kasaragod.
- **Patterns of Care and Survival** studies with NCRP (breast, cervix, head & neck) — 1,729 /
  413 / 2,623 patients followed 2013-2015 with periodic health-status monitoring.
- Registry staff publish in *Cancer Research, Statistics and Treatment*.

**Implication:** MCC is an experienced ICMR registry site with existing longitudinal
follow-up machinery and existing data-governance practice — a materially better partner
profile than this workspace had assumed.

---

## 7. Relationship status — unchanged, and weaker than it reads elsewhere

- **MoU: NOT signed.** `mcc-visit/05_data_sharing_mou_outline.md:3` calls itself "A skeleton,
  not a legal instrument"; signature block blank (lines 91-92).
  `EVIDENCE_FOR_THE_PITCH_2026-10-12.md:190`: *"There is no active MoU… No MCC patient data
  has ever been processed."*
- **Visit: no evidence it happened.** `06_audit_log_entry.json:8` still reads "Visit date:
  TBD". Git log for `anukriti_docs/mcc-visit/` shows only the two June prep-pack commits
  (`620217c`, `f5b9887`) and nothing after. Lead status still `"discovery_scheduled"`.
- **IEC: no file in this workspace records any IEC detail.** The registration number
  `EC/NEW/INST/2020/796` and the **membership-term expiry of 28-Oct-2026** come from *project
  memory* (written 2026-10-11), **not** from any repo file, and are **not re-verified**.
  Verify against the DHR/CDSCO registry or ask MCC before planning around that date.
  `05_data_sharing_mou_outline.md:51-52` lists MCC IEC approval as an unmet prerequisite.
- **"400-500 DPYD-tested patients" is explicitly unverified** —
  `anukriti/src/benchmark/fluoropyrimidine_registry.json:228-237`: `"approximately 400-500
  discussed, not verified"`, `"No governed transfer completed"`, blockers include
  `exact_panel_unverified`. **The published service figures (2, 8, 19/276) do not obviously
  reconcile with 400-500**; that cohort is most likely a research study, not the service line,
  but this has never been established. The 7 rsIDs were never recorded.
- Also unresolved: `READINESS_PCR_COHORT_2026-10-12.md` assesses a **4-variant** CPIC panel for
  an unnamed "they", against the **7-polymorphism** panel in the MCC call notes. Different
  partner, or changed panel? Resolve before quoting either.
- ⚠️ **Live liability:** the published Zenodo paper describes a retrospective cohort as
  "prospective" and calls it a "validation". It carries a DOI, is citable, and
  **the MCC Molecular Oncology lead is a co-author and has not been told**
  (`EVIDENCE_FOR_THE_PITCH_2026-10-12.md:201-205`).

---

## 8. What to do with this

### Questions only MCC can answer, in priority order

1. **Is the 2024-25 DPYD figure 19 or 276?** It decides whether MCC has a gap or a programme,
   and therefore what Anukriti is offering them.
2. **Is chemotherapy ordered in e-Hospital today, or on paper?** Everything about an
   order-time trigger depends on it, and it has never been asked.
3. What are the **7 rsIDs** on the DPYD panel, and how does the 400-500 cohort relate to the
   2/8/19 service counts?
4. **Has the IEC been reconstituted?** Current membership term?
5. Is there an HBCR extract for colorectal/GI patients with treatment and toxicity fields?

### The National Cancer Grid route

Dr. Chandran K Nair chairs the NCG committee designing the medical-oncology module of a
future EMR for NCG centres across India. If a DPYD order-time check belongs anywhere, it
belongs in that module's design — not in a bespoke integration at one hospital. Worth
understanding before any integration work is scoped. **Do not approach NCG; this is noted as
intelligence, not a plan.**

### Claims discipline

Nothing here supports "active MOU", "live production system", "clinical validation", or any
claim that MCC data has been used. **No MCC data has ever been received.** The standing hold
on external claims is unaffected.

What this *does* support, once the 19-vs-276 question is settled: a specific, published,
local, Indian figure for DPYD testing against a measured fluoropyrimidine-exposed population
at a real centre — which is a far stronger foundation than any claim currently in the funder
documents.
