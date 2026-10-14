# Context of use: source reproduction and the oncology pilot

Recorded 6 September 2026. Status: research configuration; partner-specific
fields below remain unconfirmed. No partner participant dataset was supplied
for this execution.

## Immediate experiment

**Question:** can an immutable published 5-FU simulation be executed in a pinned
runtime with the intended regimen, quantities and units preserved?

| Field | Frozen reproduction selection |
|---|---|
| Model | Marok 2024, DOI [10.1002/cpt.3181](https://doi.org/10.1002/cpt.3181) |
| Source repository | [Pinned project files](https://github.com/Clinical-Pharmacy-Saarland-University/5-FU-PBPK-Model/tree/e4ba27100d17336a53c3465b873e224afa90624a) |
| Source file | `5-FU_constant_rate_infusions.pksim5` |
| Simulation name | `FU_86_G01_IV_C_Circ` |
| Source simulation ID | `oN3eNDMrFkaMF6-4L8aGVA` |
| Publication comparator | Figure 3b; Grem 2001 constant-infusion arm |
| Study identifier | [PMID 11822758](https://pubmed.ncbi.nlm.nih.gov/11822758/), DOI `10.1023/a:1013185125186` |
| Administration | IV constant infusion, 5,250 mg/m² over 72 hours |
| Derived rate | 1,750 mg/m²/day = 72.9166667 mg/m²/hour; total absolute dose depends on the source individual's BSA |
| First output | Peripheral venous plasma 5-FU concentration versus elapsed time |
| Comparisons | Unmodified source cached results, independently rerun results where available, and the publication's curve |
| Parameter changes | None for the source-reproduction comparison |

The original study administered PALA and leucovorin with 5-FU. Its abstract
reports 27 participants and consecutive fixed/variable infusion cycles in 17;
these are study-level counts, not the size of every plotted PK subset.
[Grem 2001](https://pubmed.ncbi.nlm.nih.gov/11822758/)

The paper's Figure 3b constant arm has 16 participants; Figure 3c has ten.
Figure 3b starts at 08:00 and uses DPD amplitude 0.124 and phase parameter
1,285 minutes. Preserve the source clock origin and formula rather than
interpreting that parameter as a wall-clock timestamp.
[Marok 2024, Figure 3 and Results](https://doi.org/10.1002/cpt.3181)

This source regimen must not be relabeled FOLFOX, FOLFIRI or a 46-hour infusion.
Executing its 5-FU model does not establish whether all original co-medication
effects are mechanistically represented.

## Proposed first partner study

**Question:** after qualification and calibration, does adding mechanistically
generated patients improve a prespecified exposure-prediction task on independent
real oncology measurements?

Planning scope is adults receiving systemic IV infusional 5-FU. A 46-hour
infusion is a candidate, not an accepted protocol. The next partner record must
resolve the following before local calibration or claims of clinical relevance:

| Required field | Current state | Responsible role |
|---|---|---|
| Country, institution, recruitment frame and subpopulations | Unspecified | Clinical partner / principal investigator |
| Regimen, cancer setting, cycle number and inclusion/exclusion criteria | Adult infusional 5-FU candidate; exact regimen unconfirmed | Oncologist |
| Bolus component, infusion dose/rate/duration, actual interruptions and pump type | Unspecified | Oncology pharmacist / infusion team |
| Baseline and longitudinal organ-function/covariate dictionary | Unspecified | Clinical pharmacologist / data steward |
| Germline assay, assembly, panel coverage, phase and copy-number capability | Unspecified | Molecular laboratory |
| PK specimen matrix, timing, stabilization, assay units, LLOQ and quality controls | Unspecified | Bioanalytical laboratory |
| DPD/uracil measurements and collection/preanalytic metadata | Availability unconfirmed | Clinical pharmacologist / laboratory |
| Access agreement, participant consent and derivative-data permissions | Not obtained in this execution | Institutional data steward |
| Real-data fitting/calibration/test cohorts and recruitment boundaries | Not assigned | Statistician / investigator |
| Minimum useful improvement and precision/sample-size calculation | To prespecify before looking at the final test outcomes | Statistician / investigator |

The first research endpoint is a concentration-time or regimen-specific exposure
quantity with a documented measurement model. AUC windows must follow the chosen
study. Do not equate AUC over a full infusion, AUC over the observation window,
and concentration multiplied by infusion duration without checking assumptions.

Drug recommendations remain the responsibility of the versioned clinical PGx
core and the treating team. This qualification neither changes clinical tables
nor treats enzyme activity scores as fractional human clearance. Toxicity,
tumor response, survival, capecitabine and pediatric predictions remain outside
this first reproduction experiment.
