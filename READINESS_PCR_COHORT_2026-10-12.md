# Can we take their PCR data today?

The ask, as relayed: *they have PCR data for 5-FU / DPYD patients, and want
toxicity findings, more variants found, risks flagged, and the right dosage.*

Assessed 2026-10-12 by running their scenario, not by reading the code.

**Short answer: the engine is ready, the deployment is not, and one of the
four asks needs correcting before anyone promises it.**

---

## 1. What works, verified today

Run against `fixtures/cohort_template.csv`, which is PCR-shaped — one row per
patient, rsID columns, blanks for untested loci.

### Cohort retrospective

```
Four-quadrant table — panel: CPIC 4-variant DPYD panel
n = 8 patients with a readable toxicity grade

                         grade >=3    grade <3
panel POSITIVE                   2           0
panel NEGATIVE                   3           3

3/6 (50.0%) of panel-NEGATIVE patients had grade >=3 toxicity.
  Published comparators:
    22.7% (231/1018) systemic chemotherapy   Henricks 2018, PMID 30348537
```

That is the analysis a site retrospective exists to produce, and it runs on
the data they already have.

### Per-patient interpretation

```
ANSWER    DPYD Normal Metabolizer — normal DPD activity predicted from
          the loci that were read
DOSE      CPIC: "Use label-recommended dosage and administration."
COVERAGE  0 found · 4 read, no variant · 15 NOT assayed — of 19 loci
```

Flags fired for that patient: `ASL-ASSAY-01` (tested vs not tested),
`ASL-POP-01` (low-yield loci), `P7_DPYD_ANCESTRY_PANEL_MISMATCH`,
`P6_DPYD_CNV_NOT_INTERROGATED`, `P8_DPYD_MONITORING_UNCONDITIONAL`.

### Input handling

Reads CSV, TSV and XLSX. Accepts the vocabulary a laboratory actually writes —
`Wild type`, `Not detected`, `Heterozygous`, `Homozygous mutant`. Column
headers may be rsIDs, CPIC cDNA names, star alleles or `HapB3`.

**Refuses `Detected`.** It states presence without copy number, and for a
no-function allele that is the difference between a 50% reduction and a
contraindication.

**Refuses to widen the panel silently:**

> genotype supplied for rs112766203 (c.2279C>T), which panel 'cpic4' does not
> cover. asl will not drop an observed genotype, and it will not silently
> widen the panel its conclusions are attributed to.

---

## 2. The ask that needs correcting: "finding out more variants"

**From a four-variant PCR, we cannot find more variants. The data does not
contain them.** No software can. If that is what they are expecting, the
expectation has to be reset before a sale, not after.

What we actually do is better framed and still valuable — we name *exactly*
what their panel could not see, and what it is worth in their population:

```
P7_DPYD_ANCESTRY_PANEL_MISMATCH
  This panel was derived from European data, and this patient's recorded
  population is Central/South Asian. 3 allele(s) that matter in
  non-European ancestry were not assayed.

    c.2279C>T  (rs112766203) — 0.63% in GenomeIndia (n=9,768) and 0.000%
                 in Europeans; AMP/ACMG 2024 Tier 1, absent from every
                 commercial platform that consensus surveyed
    c.557A>G   (rs115232898) — AMP/ACMG 2024 Tier 1; strong evidence in
                 African ancestry; not in the UK NHS panel
    c.868A>G   (rs146356975) — AMP/ACMG 2024 Tier 1
```

And if they **send wider data**, the engine calls it. Same patient, same
genotype, wider panel:

| panel | result |
| --- | --- |
| `cpic4` | cannot accept the locus at all |
| `amp_tier1` | `*1/c.2279C>T` · **Intermediate Metabolizer** · reduce starting dose by 50% |

The engine calls **33 alleles** across **19 loci** as of 0.11.0, up from 18
and 13. So the honest pitch is: *we cannot find what your assay did not
measure — we tell you precisely what it missed, and we call everything the
moment you widen it.*

---

## 3. The blocker

**Nothing we have built is deployed.**

```
live revision   anukriti-api:git-bab8bc2-b5ab95-fd8601-4b0b0d
created         2026-10-11T04:30:10
built from      api commit bab8bc2, which pinned anukriti-pgx-core==0.9.0
```

`origin/main` now pins **0.11.0**. Production is two engine versions and one
day behind, and the gap includes every clinically material change:

- the HapB3 `tag_without_causal` withdrawal
- function-ordered truncation (22 phenotype disagreements with PyPGx, all in
  the less-conservative direction, now 0)
- the panel widening 18 → 33 alleles
- `/asl/dpyd/panels` being public at all — **on the live deployment the DPYD
  tool still cannot load its own input fields**
- `hapb3_basis` in the API response, so CPIC's mandated disclosure can render
- the ancestry and monitoring flags
- the `/asl/dpyd/interpret` 500

A demo against the live URL today shows a broken tool. A demo against a local
build shows the product. **That difference is a deploy, and it has not
happened.**

See `anukriti-stack/docs/RELEASE_0.11.0_PREFLIGHT.md` — note in particular
that the image tag does **not** record the installed engine version, so after
deploying, the tag will not confirm whether 0.11.0 actually landed. Probe B in
that document is the only reliable check.

---

## 4. Gaps between "works" and "finished product"

| gap | state | matters because |
| --- | --- | --- |
| **Batch via UI or API** | CLI only | They said patient**s**. `/asl/dpyd/interpret` is one patient per call; the UI form is one patient. A site with 200 PCR results has no path that is not a terminal. |
| **Signatory in the UI** | CLI `--signatory` only | An Indian laboratory report needs a named signatory with a post-graduate pathology qualification (Supreme Court, Dec 2017). The field exists in `asl`; the web form never asks for it. |
| **PDF export** | browser print only | Print CSS is written and tested; **nobody has hit Cmd-P on a real printer.** |
| **Responsive layout** | unverified | The browser would not resize in testing. Narrow-width fixes were made from reading markup, not from looking at a phone. |
| **Structured payload** | not built | Research requirement E22/E23: ship a PDF *and* a structured payload flattening to a discrete phenotype label, because Epic's Genomics Module gives an activity score no CDS function. |
| **Order-time trigger** | not built | Named the single highest-value feature in implementation studies; 70% of sites rely on clinicians remembering. Needs EHR integration. |

---

## 5. Verdict

**For a retrospective on PCR data they already hold — ready now**, via the
CLI. The quadrant analysis and the per-patient reports both run today, and the
coverage and ancestry disclosures are the product's actual argument.

**For a live clinical tool they can open in a browser — not ready**, because
it is not deployed, and because batch and signatory are missing from the web
path.

**For "find us more variants in this PCR data" — not possible**, by anyone,
and the pitch should say so plainly and pivot to what we do instead. That
pivot is strong: no Indian lab publishes a specimen report, none publishes an
activity score or a numeric dose reduction, and none states which alleles it
did not test. We do all four.

### Shortest path to a demo that holds up

1. Deploy 0.11.0 and run Probe B from the preflight.
2. Add a batch endpoint — `asl.importer` already reads their file format.
3. Add the signatory field to the web form.
4. Print it on paper and look at it.

1 and 4 are hours. 2 and 3 are small. None of them is research.
