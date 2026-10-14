# 5-FU / DPYD engine — current capability and worldwide tool landscape

> **As of:** 13 September 2026  
> **Status:** canonical current-state assessment for the Anukriti 5-FU/DPYD workstream  
> **Scope:** `anukriti-pgx-core`, `anukriti-swarm`, `anukriti-api`, `anukriti-main`, `asl`, `anukriti-stack`, related validation artifacts, and comparable tools worldwide  
> **Safety boundary:** research and engineering assessment, not medical advice or a prescribing protocol

## Executive answer

**Anukriti does not currently predict an individual patient's probability of 5-FU toxicity and does not calculate that patient's exact dose.** It currently implements a deterministic, CPIC-faithful **DPYD genotype → phenotype → starting-action** workflow:

| DPYD phenotype | Current core action |
|---|---|
| Normal metabolizer | `STANDARD` |
| Intermediate metabolizer | `REDUCE_50PCT` |
| Poor metabolizer | `AVOID` |

This is a real and clinically relevant capability, but it must be named precisely: **genotype-guided starting-dose support**, not a toxicity-prediction model and not a personalized dose calculator.

The platform also provides evidence sufficiency, population-context annotations, assay-scope disclosures, residual-risk reporting, and an outcome ledger. Those layers do not turn the starting-action rule into a patient-specific risk probability or an exact dose.

The closest executable software peer is **PharmCAT**. Most other things described as “DPYD tools” are actually one of four different products: a guideline, a laboratory assay, a pretreatment DPD phenotype test, or a post-dose 5-FU therapeutic-drug-monitoring system. Genuine multivariable toxicity models remain research-stage.

---

## 1. Keep three capabilities separate

These three functions are not interchangeable:

### A. Genotype-guided starting-dose support

Input: assayed DPYD variants or a diplotype.  
Output: activity/phenotype class and guideline action such as standard dose, reduce the starting dose, or avoid.

This is what Anukriti currently implements. CPIC, DPWG, PharmCAT, CancerCalc, and many laboratory reports operate in or supply this category.

### B. Exact or adaptive dose calculation

Input: a protocol dose plus patient and/or measured pharmacokinetic data.  
Output: an actual dose, often in mg/m² or total mg, or a next-cycle percentage adjustment.

A post-dose 5-FU TDM workflow such as My5-FU/MyCare can support this for continuous-infusion 5-FU after a plasma measurement. Anukriti does not currently do this.

### C. Individual toxicity-risk prediction

Input: genotype plus clinical covariates such as age, sex, BMI/BSA, renal function, regimen, administration schedule, co-treatment and prior toxicity.  
Output: a calibrated probability for a defined endpoint and time horizon, for example grade 4–5 toxicity within 12 weeks.

Anukriti does not currently do this. Published models such as FUSAFE are research models, not established worldwide clinical software products.

Any comparison that calls A, B and C the same “toxicity predictor” is misleading.

---

## 2. What the current Anukriti stack actually does

### 2.1 `anukriti-pgx-core==0.9.0`: deterministic truth layer

Relevant implementation:

- `anukriti_pgx_core/calling/genes/dpyd.py`
- `anukriti_pgx_core/phenotype/engine.py`
- `anukriti_pgx_core/phenotype/clinical_action.py`
- `anukriti_pgx_core/phenotype/tables/DPYD_CLINICAL_ACTIONS_v2024.01.json`
- `tests/test_clinical_action.py`
- `tests/test_drug_synonyms.py`
- `tests/test_dpyd_hapb3_provenance.py`
- `tests/test_dpyd_table_integrity.py`

The core can:

1. Convert supported per-rsID VCF-style calls into a DPYD diplotype.
2. Resolve the pinned CPIC phenotype.
3. Attach CPIC evidence level for fluorouracil/capecitabine.
4. Map the phenotype to `AVOID`, `REDUCE_50PCT`, or `STANDARD`.
5. Resolve clinical spellings including `fluorouracil`, `5-fluorouracil`, and `5-FU`.
6. Preserve HapB3 provenance instead of treating its causal and tag variants as interchangeable:
   - `rs75017182`: causal deep-intronic variant;
   - `rs56038477`: exonic tag;
   - `haplotype`, `causal`, `tag_only`, or `tag_without_causal` basis.
7. Refuse or remain indeterminate when the genotype cannot be resolved safely.

The core does **not** accept or model:

- age, weight, BSA or performance status;
- renal or hepatic function;
- cancer type, regimen or administration schedule;
- protocol dose in mg/m²;
- cycle number or prior-cycle toxicity;
- plasma uracil, DHU/uracil ratio or leukocyte DPD activity;
- plasma 5-FU concentration or AUC;
- an individual toxicity endpoint or probability.

The text “50% starting dose” is a pinned guideline action. It is not the result of patient-specific dose arithmetic.

### 2.2 `anukriti-swarm`: evidence governance and narration

Swarm contributes:

- CPIC evidence retrieval;
- graph context and citation provenance;
- evidence coverage and sufficiency decisions;
- population-frequency context;
- named uncertainty such as `P1_SAS_DPYD_CONTESTED`;
- optional grounded narration.

The South Asian DPYD flag is an annotation. It does not change `allows_synthesis`, reclassify an allele, or assert that a patient has elevated toxicity risk. Swarm's model schema explicitly describes dose calculation as future work.

Swarm therefore improves the auditability and honesty of category A; it does not implement category B or C.

### 2.3 `anukriti-api`: workflow transport

The API supports fluorouracil and capecitabine workflows, including structured SNP input, sample workflows and a DPYD PCR-ingestion path. It returns fields such as:

```json
{
  "diplotype": "*1/*2A",
  "phenotype": "Intermediate Metabolizer",
  "evidence_level": "A",
  "clinical_action": "REDUCE_50PCT"
}
```

`POST /runs/from-pcr` is useful for laboratories that already have DPYD calls. It does not accept the covariates required for an individual risk model or exact dose calculation.

The authenticated ASL routes accept panel content, per-locus zygosity, regimen category, population key and drug. They do not accept BSA, protocol dose, renal function or TDM measurements for prediction.

### 2.4 `anukriti-main`: two DPYD surfaces

- `MtbReportCard.jsx` displays the fixed CPIC action.
- `/tools/dpyd-asl` displays assay scope, evidence and residual risk.

A significant safety debt remains: `src/lib/pgxRules.js` contains a parallel browser-side DPYD interpreter. The browser should ultimately display core/API output rather than maintain an independent clinical rule implementation.

### 2.5 `asl`: residual-risk ledger, not a predictor

ASL explicitly does not recommend doses or override CPIC. It adds:

- tested versus not-tested semantics;
- SNV-only/CNV assay limitations;
- per-allele evidence attribution;
- named conflicts and pending changes;
- regimen-gated published comparator rates;
- an append-only toxicity-outcome ledger.

For example, `22.7% (231/1018)` is a published systemic-chemotherapy rate among patients **without** an actionable variant. It is not the current patient's predicted probability. ASL withholds that number from an actionable carrier because the comparator does not apply.

The ledger can store starting dose, BSA, cycles, modifications and CTCAE events. Those fields support future retrospective validation; they are not currently inputs to a fitted risk or dose model.

### 2.6 `anukriti-stack`: deployment gap

`Dockerfile.api` installs API and Swarm requirements and therefore obtains the pinned core, but it does not copy/install `asl` or add `asl/src` to `PYTHONPATH`. The checked-in image consequently exposes ASL routes that return 503 when ASL is unavailable.

### 2.7 Validation performed for this assessment

Focused local validation on 13 September 2026:

| Surface | Result |
|---|---:|
| pgx-core clinical action, aliases, HapB3 and table integrity | 189 passed |
| frontend DPYD/MTB/ASL tests | 65 passed |
| Swarm DPYD population/evidence tests | 23 passed |
| complete ASL suite | 175 passed |
| API against checked-out core 0.9.0 | 57 passed, 1 stale count assertion |

The one API failure expected nine untested loci while the expanded 0.9.0 surface now reports thirteen; the safety behavior itself passed.

A more serious environment issue was found: the default local API Python environment imported `anukriti-pgx-core 0.7.0` even though manifests pin 0.9.0. That stale environment reproduced dangerous strand/HapB3 failures and caused ASL to refuse execution. Forcing the checked-out 0.9.0 source removed those clinical failures. Startup and CI should verify the imported package version and path, not merely trust the requirements file.

### 2.8 Validation claim that is justified—and the one that is not

Justified:

> The deterministic engine is regression-tested to reproduce its pinned DPYD/CPIC calling and starting-action rules.

Not justified:

> The engine prospectively predicts an individual patient's toxicity or optimal dose.

No completed prospective or external patient-outcome validation of such a model exists because such a model is not currently implemented. The proposed MCC retrospective cohort remains a data/collaboration plan, not an ingested or completed validation study.

---

## 3. Worldwide landscape by function

## 3.1 Guidelines and regulatory pathways: sources, not competing engines

| System | Geography | What it provides | What it is not |
|---|---|---|---|
| **CPIC** | International/US-led consortium | DPYD activity/phenotype and fluoropyrimidine dosing recommendations | Not an individual toxicity model or hosted patient engine |
| **DPWG/KNMP** | Netherlands | Independent DPYD–fluoropyrimidine guideline logic | Not a patient-level probability model |
| **ClinPGx/PharmGKB** | International knowledge resource | Curated gene, allele, guideline and label annotations | Not itself a dosing service |
| **EMA** | European Union | Recommends pretreatment DPD genotype and/or phenotype testing; complete deficiency is a contraindication; TDM may improve continuous-infusion outcomes | Does not prescribe one universal software implementation |
| **France HAS/INCa/ANSM pathway** | France | Pretreatment plasma uracil phenotyping with strict preanalytics and thresholds; dose/avoid decisions consider uracilemia and clinical factors | Not a genotype-only pathway |
| **NHS pathway** | United Kingdom | Nationally commissioned pretreatment DPYD testing | The commonly deployed panel is not a complete non-European variant screen |
| **eviQ/MBS** | Australia | Regimen guidance; DPYD genotyping listed on the Medicare Benefits Schedule from November 2025 | Not a toxicity-prediction application |

Primary references:

- [CPIC/NCBI dosing table, updated May 2026](https://www.ncbi.nlm.nih.gov/books/NBK395610/table/fluorouracil.T.the_cpic_recommended_dosi/)
- [DPWG guideline, PMID 31745289](https://pubmed.ncbi.nlm.nih.gov/31745289/)
- [EMA DPD testing recommendation, 30 April 2020](https://www.ema.europa.eu/en/news/ema-recommendations-dpd-testing-prior-treatment-fluorouracil-capecitabine-tegafur-flucytosine)
- [France HAS/INCa uracilemia recommendation, 18 December 2018](https://www.has-sante.fr/jcms/c_2892234/en/des-recommandations-pour-prevenir-certaines-toxicites-severes-des-chimiotherapies-par-fluoropyrimidines?userLang=en)

## 3.2 Direct software comparables

### PharmCAT 3.4.0 — closest direct peer

PharmCAT processes VCF input, calls pharmacogene genotypes/diplotypes, derives phenotype and reports CPIC, ClinPGx-annotated DPWG and FDA-label guidance. Its DPYD implementation:

- uses CPIC definition/function data;
- uses the two lowest-function variants when unphased;
- prioritizes the causal HapB3 intronic variant when available;
- can fall back to the exonic tag with a warning;
- reports CPIC and DPWG recommendations.

This is the correct primary software benchmark for Anukriti.

Sources:

- [PharmCAT home and current release](https://pharmcat.org/)
- [PharmCAT DPYD special handling](https://pharmcat.org/methods/Gene-Definition-Exceptions/#dpyd)
- [PharmCAT changelog](https://pharmcat.org/changelog/)

### CancerCalc DPYD activity-score calculator — narrower web tool

CancerCalc provides a manual web activity-score calculator based on CPIC and warns that common panels miss rare variants and that normal genotype results do not eliminate severe toxicity. It is useful as a clinician-facing lookup, but it is not a VCF pipeline, evidence-governance platform or individual toxicity model.

Source: [CancerCalc DPYD activity-score calculator](https://cancercalc.com/dpyd_score.php)

### Direct comparison

| Capability | Anukriti current stack | PharmCAT 3.4.0 | CancerCalc |
|---|---|---|---|
| Variant input | Structured rsID/PCR and VCF-oriented adapters; named diplotype paths | VCF/genomic pipeline | Manual allele selection |
| DPYD phenotype/action | CPIC-pinned | CPIC plus DPWG/FDA report paths | CPIC activity-score display |
| HapB3 causal/tag handling | Explicit basis states retained in core | Causal priority, tag fallback and warnings | Depends on manual selection |
| Population context | Frequency/evidence annotations; never changes CPIC action | Frequency-analysis tooling exists, but recommendation remains guideline-based | Descriptive frequencies |
| Exact mg/m² dose calculation | No | No | No |
| Individual toxicity probability | No | No | No |
| Assay-scope/residual-risk ledger | ASL implements this, but stack packaging is incomplete | Report warnings; no Anukriti-style outcomes ledger identified | General caution text |
| Clinical validation of a prediction model | Not applicable/not done | Not a toxicity model | Not a toxicity model |

A fair concordance study must hold the input loci and genome build constant. A tool cannot recover a variant that the upstream assay did not measure.

## 3.3 Laboratory and health-system implementations

Laboratory tests determine what evidence reaches an engine. They should not be scored as if they were software risk models.

| Example | Geography | Verified scope or behavior | Interpretation |
|---|---|---|---|
| **BC Cancer implementation** | Canada | Six-variant qPCR: the four common European-derived variants plus African-relevant c.557A>G and South-Asian-relevant c.2279C>T; report included predicted activity score and dosing table | Strong example of expanding assay scope for a diverse population; still guideline starting-dose support |
| **Mayo Clinic Laboratories** | US | Offers common-variant genotyping and a separate full-sequencing option according to its oncology therapeutics catalog | Assay service, not a toxicity probability engine |
| **Expanded commercial panels** | Multiple | Some products test beyond four variants; exact scope and regulatory status vary by product and jurisdiction | Verify the current package insert before comparison; do not assume every commercial panel is four-variant |

BC Cancer's pilot also illustrates the residual problem: severe toxicity occurred in some dose-reduced carriers and in variant-negative patients. Its authors state that six-variant genotyping cannot capture every deficient patient.

Source: [BC Cancer implementation, PMID 37745065](https://pmc.ncbi.nlm.nih.gov/articles/PMC10515725/)

## 3.4 Pretreatment DPD phenotyping

EMA allows genotype and/or phenotype testing. France specifically selected pretreatment plasma uracil measurement as the primary method, with strict sample handling and threshold-based interpretation.

This approach is less tied to which DPYD variants are on a panel and is therefore relevant to ancestry coverage. It is not automatically superior: uracil measurements have important preanalytical constraints and threshold/transferability concerns.

Useful sources:

- [France HAS recommendation](https://www.has-sante.fr/jcms/c_2892234/en/des-recommandations-pour-prevenir-certaines-toxicites-severes-des-chimiotherapies-par-fluoropyrimidines?userLang=en)
- [Pretreatment uracil caution study, PMID 35397172](https://pubmed.ncbi.nlm.nih.gov/35397172/)

Anukriti currently records phenotyping/TDM as recommended follow-up text but does not accept or calculate from uracil, DHU/uracil or DPD enzyme activity.

## 3.5 Post-dose 5-FU therapeutic drug monitoring

**My5-FU/MyCare 5-FU** is a real precision-dosing comparator in category B, not category A. It is a CE-marked plasma assay for patients receiving continuous-infusion 5-FU. The measured concentration is converted to AUC and combined with a validated adjustment algorithm for later doses.

It:

- measures actual drug exposure after dosing;
- supports next-cycle pharmacokinetic adjustment;
- applies to continuous-infusion 5-FU;
- does not replace pretreatment DPYD/DPD assessment;
- is not a capecitabine genotype predictor.

Sources:

- [NICE My5-FU technology description](https://www.nice.org.uk/guidance/HTG360/chapter/4-the-diagnostic-tests)
- [Thermo Fisher/Saladax MyCare portfolio](https://www.thermofisher.com/us/en/home/clinical/diagnostic-testing/clinical-chemistry-drug-toxicology-testing/saladax.html)

The long-term clinically useful architecture is complementary:

```text
pretreatment genotype/phenotype safety gate
    → starting action
    → measured 5-FU exposure/TDM where applicable
    → cycle-specific adjustment and toxicity monitoring
```

## 3.6 Genuine toxicity-prediction models

### FUSAFE

FUSAFE is the strongest clearly described multivariable research comparator found in this review. It combined:

- age;
- sex;
- BMI;
- fluoropyrimidine administration schedule;
- concomitant anticancer drugs;
- selected DPYD variants.

The primary endpoint was grade 4–5 haematological or digestive toxicity within 12 weeks. The dataset was restricted to Caucasian patients without DPD-guided dose adjustment. Although the fitted model's apparent AUC was about 0.75, the internal-external overfitting-corrected average AUC was about **0.62**, with substantial between-study variation. The paper presents a research model and explicitly calls for further confirmation; it is not a generally deployed clinical calculator.

Source: [FUSAFE IPD meta-analysis, PMID 38225422](https://pmc.ncbi.nlm.nih.gov/articles/PMC10912560/)

### Other research directions

Published work includes:

- capecitabine nomograms in DPYD-wild-type patients;
- rare-variant burden models;
- multigene burden analyses;
- sequencing-based life-threatening-toxicity models;
- clinical-covariate studies involving renal function, age and BSA.

These are valuable design inputs, but no model identified in this review has the combination needed to call it an established worldwide individual-risk tool: reproducible implementation, prospective external validation, calibration across populations and regimens, clinical deployment, and a governed dose-adjustment pathway.

---

## 4. Is the field Eurocentric?

### Precise answer

**The standard four-variant panel and much of the outcome evidence used to validate it are European-derived. That panel under-detects relevant risk in some non-European populations. The entire worldwide field is not uniformly Eurocentric.**

Evidence supporting the first statement:

- The 2024 non-European systematic review states that the four variants routinely tested in the UK/EU are more prominent in Europeans and that the key clinical-utility studies were conducted in European populations.
- The review identified 53 variants across non-European patients and highlighted c.557A>G in people of African ancestry, which was not in the UK panel.
- Japanese and other East Asian studies identify different rare-variant patterns and weak transferability of the common European panel.
- FUSAFE explicitly selected Caucasian cohorts.

Evidence against the blanket statement:

- EMA permits phenotype and/or genotype testing.
- France uses genotype-independent uracil phenotyping.
- BC Cancer deliberately added African- and South-Asian-relevant variants.
- Some laboratories offer expanded panels or sequencing.
- Post-dose 5-FU TDM measures exposure rather than ancestry-specific allele coverage.

Recommended wording:

> The standard four-variant DPYD panel and much of its clinical evidence are European-derived and can under-detect risk in non-European populations. Variant coverage, phenotype testing, sequencing and outcome validation must be evaluated for the population and regimen being served.

Avoid:

> Every worldwide DPYD tool is Eurocentric.

Also avoid claiming that Anukriti has already solved ancestry-specific toxicity prediction. Its population layer currently annotates evidence and frequency; it does not have a validated South-Asian risk model or authority to override CPIC.

Source: [Chan, Zhang and Pirmohamed 2024 systematic review](https://www.nature.com/articles/s41416-024-02754-z)

---

## 5. What Anukriti's defensible differentiation is today

Defensible now:

1. Deterministic and versioned DPYD rule execution.
2. Explicit HapB3 causal/tag provenance.
3. Named evidence and population uncertainty without silently overriding CPIC.
4. Assay-scope semantics: tested, not tested, no call, SNV-only and CNV limitation.
5. Regimen-gated residual-risk disclosures rather than an all-clear.
6. PCR ingestion and cohort-level audit artifacts.
7. An append-only structure for collecting genotype, dose and toxicity outcomes.

Not defensible yet:

1. “Anukriti predicts whether this patient will develop toxicity.”
2. “Anukriti calculates the right 5-FU dose for this patient.”
3. “Anukriti is clinically validated in Indian patients.”
4. “Anukriti catches all variants missed by commercial tools.”
5. “Anukriti is the only population-aware DPYD tool.”
6. “All competing tools use only the European four-variant panel.”
7. “A normal Anukriti/CPIC call means low toxicity risk.”

The present differentiation is principally **governance, provenance, assay honesty and the path to collecting local outcomes**, not a proven superior toxicity model.

---

## 6. What must be built for the stated target

Target claim:

> Given this patient, cancer regimen and measured biology, estimate a calibrated toxicity risk and support a validated starting and adaptive dose.

Minimum data:

- exact assay content and DPYD genotype, including CNV/deletion capability;
- cancer type, regimen, administration schedule and protocol dose;
- age, sex, BSA/BMI, performance status, renal and hepatic function;
- concomitant anticancer drugs and relevant comedications;
- per-cycle delivered dose, modifications and delays;
- CTCAE toxicity type, grade and onset cycle;
- hospitalization/discontinuation and efficacy outcomes where permitted;
- pretreatment uracil/DHU or DPD activity where available;
- 5-FU AUC/TDM for continuous-infusion workflows where available.

Minimum engineering components:

1. **Single-source deterministic gateway.** Remove browser and narration-side re-derivations; core/API owns the clinical call.
2. **Assay/phenotype adapter.** Add governed inputs for uracil, DHU/uracil, DPD activity and method/preanalytics.
3. **Calibrated toxicity model.** Define endpoint and horizon first; develop and validate with outcome-linked cohorts.
4. **Dose-individualization module.** Separately compute protocol/BSA dose and later TDM/tolerance adjustments; do not hide this inside pgx-core.
5. **Prospective and external validation.** Include calibration, decision-curve/utility analysis and subgroup performance—not only AUC.
6. **Regulatory and clinical governance.** Exact dose recommendation is a materially higher-risk claim than displaying a guideline action.

The MCC retrospective is the nearest possible first dataset. Until it is governed, transferred, cleaned, analyzed and externally validated, it remains a plan rather than evidence of model performance.

---

## 7. Immediate engineering priorities

1. Hard-fail API startup when the imported core version/path is not the approved 0.9.0 build.
2. Package ASL into `anukriti-stack/Dockerfile.api` and add an integration smoke test that cannot skip.
3. Remove or retire the independent DPYD decision implementation in `anukriti-main/src/lib/pgxRules.js`.
4. Remove DPYD phenotype re-derivation from Swarm narration; narrate the core record instead.
5. Fix the stale API assertion for the expanded 0.9.0 not-tested locus set.
6. Run a controlled Anukriti-versus-PharmCAT DPYD concordance benchmark with identical loci/build/input.
7. Define the first prediction endpoint before model work—for example, grade ≥3 toxicity during cycles 1–2 on a specified regimen family.
8. Treat TDM integration as complementary to genotype, not as a competitor or afterthought.

---

## 8. Source-quality notes

- Product scope and regulatory status change. Verify current package inserts and jurisdiction before procurement or claims.
- CPIC announced a HapB3-specific activity-value update in July 2026, but Anukriti correctly does not pre-apply an unpublished table change. Recheck the published guideline and run clinical regression review before changing the pin.
- This report deliberately excludes unsupported market-size, revenue, superiority and “only tool” claims.
- It also excludes exact claims about commercial panels where an official current test definition could not be verified.
- Guideline concordance, assay analytical validation, model discrimination, calibration, clinical utility and regulatory clearance are different evidence levels.

## Bottom line

Today, Anukriti is best described as:

> **A deterministic, evidence-governed DPYD genotype-to-CPIC starting-action system with population and residual-risk disclosures.**

It is not yet:

> **A validated individual 5-FU toxicity-prediction engine or personalized dose calculator.**

The worldwide landscape shows mature guideline implementation, laboratory screening, phenotype testing and 5-FU TDM, but no universally adopted multivariable toxicity predictor. Anukriti's opportunity is real, but it lies in joining these layers with local outcome evidence and prospective validation—not in relabeling the current categorical rule as prediction.
