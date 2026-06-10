# Data-Sharing / MOU Outline — MCC × Anukriti

> A **skeleton**, not a legal instrument. Hand to MCC's PI / administration /
> ethics committee as the basis for a formal agreement. Have it reviewed by
> qualified legal counsel and MCC's IRB/ethics committee before signing.
> Anukriti does not provide legal advice.

---

## 1. Parties

- **Malabar Cancer Centre (MCC)** — Thalassery, Kannur, Kerala. Lead clinical
  institution; data custodian; owner of clinical interpretation.
- **Anukriti** (Abhimanyu R B / entity TBD) — analytical engine provider;
  data processor for the defined analysis only.

## 2. Purpose & scope

- Joint **retrospective research analysis** of MCC's existing DPYD-genotyped
  oncology cohort (~400–500 patients) and associated fluoropyrimidine toxicity
  outcomes.
- Objectives: (a) genotype→toxicity concordance mapping; (b) identification of
  panel-negative, toxicity-positive cases; (c) assessment of South-Asian
  candidate-variant relevance; (d) a joint publication.
- **Out of scope:** any clinical/prescribing use; any individual patient care
  decision; any tumour-efficacy analysis; any use beyond this study.

## 3. Data shared by MCC (de-identified only)

- Anonymized per-patient rows: cancer type, fluoropyrimidine drug, DPYD assay
  method, variants tested (rsID/cDNA), genotypes, toxicity grade/type/timing,
  and (preferred) dose/cycle data. See `03_structured_ask.md` Tier 1.
- **Explicitly excluded:** names, MRNs, contact details, dates of birth, or any
  direct/indirect identifier; raw sequence files.
- **De-identification** performed by MCC **before** transfer. Anukriti receives
  no key linking IDs to identities.

## 4. Data handling, security, residency

- Transfer over an **encrypted, access-controlled** channel agreed by both
  parties.
- Storage: encrypted at rest; access limited to named project personnel.
- **Residency:** to be agreed — Indian data-residency preference noted; confirm
  acceptable storage region before transfer.
- Anukriti processes data **only** for the stated purpose; **no onward sharing**
  with third parties; **no model-training** use without separate written consent.
- Compliance posture: alignment with India's **DPDP Act 2023** principles and
  MCC's IRB conditions; research-use-only.

## 5. Ethics & regulatory

- MCC to confirm **IRB / institutional ethics committee** approval (or exemption
  for retrospective de-identified analysis) covers this use.
- Research-use-only; **not** a medical device; no clinical claims;
  outputs are research artifacts.

## 6. IP, ownership, publication

- MCC **retains ownership** of its clinical data and clinical interpretation.
- Anukriti **retains ownership** of its engine, pipeline, and rule tables.
- **Analysis outputs** (concordance tables, variant assessments) are **jointly
  owned** for the purpose of publication.
- **Publication:** joint, with agreed authorship; MCC = clinical lead and cohort
  context; Anukriti = analytical pipeline, audit trail, population-evidence
  stratification. Neither party publishes the joint analysis unilaterally.

## 7. Term, termination, data deletion

- **Term:** duration of the study (Phase 1–3) unless extended in writing.
- Either party may terminate with written notice.
- On termination/completion, Anukriti **deletes** MCC-provided data within an
  agreed window and confirms deletion in writing (subject to legal retention of
  audit logs that contain no PHI).

## 8. Phases (mirrors the collaboration framing)

1. **Phase 1:** MCC sends anonymized PCR + toxicity spreadsheet → Anukriti runs
   deterministic classification → joint review of discordant cases. (~4–6 wks.)
2. **Phase 2:** Focus on PCR-negative / toxicity-positive patients; map
   out-of-panel variants via existing NGS, or propose targeted sequencing on
   that subset + matched controls only.
3. **Phase 3:** Joint publication.

## 9. Liability & disclaimers

- Research collaboration; **no warranty** of clinical accuracy; tool does not
  prescribe; no liability for clinical decisions (which remain MCC's).

## 10. Signatures

- For MCC: __________________________ (name / title / date)
- For Anukriti: ______________________ (name / title / date)

---

**Next step after the visit:** capture MCC's exact 7-variant panel and the
panel-negative-toxicity count (see `03_structured_ask.md`), then route this
outline to legal/ethics for a formal agreement.
