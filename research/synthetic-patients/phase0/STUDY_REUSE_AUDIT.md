# Study reuse and reproduction comparisons

Checked 6 September 2026. This audit prevents the source model's development
data from later becoming an apparently independent evaluation cohort.

## What the publication establishes

Marok reports 41 5-FU studies/777 patients and ten uracil studies/104 volunteers,
with 16 training and 89 test profiles overall. Study allocation is described
in supplementary tables S2.1, S3.1 and S4.1; the complete supplement was not
retrieved in this execution. Circadian phase parameters were estimated for
profiles lacking timing/activity information. Consequently a paper's “test”
designation alone does not establish that every parameter was fixed before
observing that profile. [Marok 2024, Methods and Results](https://doi.org/10.1002/cpt.3181)

For Anukriti, the selected Grem case is **source reproduction with a
study-adapted circadian parameter**. It is not an independent prediction of a
new oncology patient. The exact source train/test allocation remains
`unverified_supplement` until the source table is read.

## Concrete overlap identified

| Relationship | Evidence | Required evaluation treatment |
|---|---|---|
| Grem constant and variable infusion cycles | Same underlying study/cohort; paired consecutive cycles described in the [primary study](https://pubmed.ncbi.nlm.nih.gov/11822758/) | One study/cohort group across splits; repeated cycles from the same person stay together |
| Constant and chronomodulated project databases | Both store 48 observation records; Grem records and additional observations appear in both projects | Deduplicate by study, cohort, analyte, person/group, regimen and collection occasion; file boundaries are not split boundaries |
| Noncircadian and circadian simulations in the constant project | Both variants are stored for several source scenarios | Model variants are comparisons on the same data, not new real participants |
| Source figures and embedded observed arrays | Both derive from source clinical reports/digitization | Treat as the same observation source unless provenance proves otherwise |
| Later comparator models | Full cohort-level inclusion lists/covariance assets have not yet been reconciled | Keep overlap status unknown until the included studies and recruitment dates are mapped |

The complete included-study inventory remains pending supplement retrieval.
Do not convert abbreviated simulation names into DOI/cohort identities by
guessing. Reproduction may proceed on the identified case while that inventory
is completed.

## Required numerical comparisons

Use three explicitly separated comparisons:

1. **Source execution:** run unchanged source content and compare with its saved
   numerical results. Record output path, unit, time vector, model checksum,
   runtime/native-solver identity and failure behavior. Saved results provide a
   regression reference; they are not an independent experiment.
2. **Version migration:** convert a copy to the candidate runtime, preserve the
   source file, then compare concentrations and derived exposure to the source
   reference on the same time grid. Record parameter/formula/observer changes
   and tolerances before calling migration equivalent.
3. **Published observations:** compare against the source observed profile using
   the specified analyte, matrix and observation window. This checks source
   reproduction, with study fitting disclosed. New clinical evaluation requires
   the separate [validation protocol](../VALIDATION_PROTOCOL.md).

The selected embedded observed repository is `Grem, 2001 - 5-FU`, ID
`0e19b8c8-2eb7-4dd4-835e-a113496ccefc`. The source database links it to
`FU_86_G01_IV_C_Circ`; it contains ten time/concentration observations plus
arithmetic SD. Its stored times use minutes although the display unit is hours.
The observation interval is approximately 24.649–51.391 hours after the source
simulation origin. A comparison over this interval must not be labeled AUC
over the full 72-hour infusion.

Use the source runtime's quantity metadata and conversion rules. For 5-FU,
the mass conversion implied by molecular weight 130.08 g/mol is
`mg/L = µmol/L × 0.13008`. Verify the molecular weight against the selected
model compound. This conversion is not a change to concentration predictions.

Figure 3b provides a graphical sanity check: the post-initial-transient model
curve is approximately 5.4–6.7 µmol/L. These visually estimated bounds are not
an exact numerical golden file or acceptance threshold. Prefer saved source
results and source observed values over measurements taken from a raster figure.

## Completing P0.8

After obtaining the supplement, create one row per source profile with DOI,
study/cohort identifier, population, sample count definition, route, dose,
duration, sex/demographics, analyte, fitting/evaluation role, fitted individual
parameters, and any repeated-participant relationship. Preserve both the
publication's role and Anukriti's stricter independent-evaluation eligibility.

Resolve comparator overlap against Briki 2026, Mielke 2025 and candidate partner
cohorts. Record unavailable original code, NONMEM control streams, covariance,
residual models and digitized observations individually. Avoid treating an
unavailable asset as a zero-uncertainty model parameter.
