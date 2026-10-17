# What we can say, what we cannot, and the numbers to say it with

Compiled 2026-10-12 for the end-of-month expo. Claims are marked **[S]**
sourced, **[I]** inference, **[GAP]** looked for and not found.

---

## 1. The one sentence to stop using

> ~~"Studies show clinicians misread 'Normal Metabolizer' as an all-clear."~~

**[GAP] No such study exists.** Structured Europe PMC searches for
`"normal metabolizer" AND (misinterpret* OR reassur* OR misunderstand*)` return
**zero hits**. The clinician-comprehension literature for pharmacogenomics has
not been written; what exists measures *patients*, not prescribers.

If a buyer's scientific reviewer checks that sentence, it does not survive. And
it does not need to, because the claim is **very strong as a clinical fact** —
which is where it should live instead.

### Say this instead

**[S] The regulator says it outright.** EMA-authored Direct Healthcare
Professional Communication for capecitabine:

> "Despite negative test results for DPD deficiency, severe toxicity may still
> occur."

**[S] The FDA label says the panel is incomplete** — of its own DPYD variant
table: *"This is not a complete listing of all DPYD variants that may result in
DPD deficiency."* The label also instructs monitoring **unconditional on
genotype**.

**[S] NCCN** (Colon Cancer v5.2025): *"No FDA-authorized test is currently
available. Existing laboratory-developed tests vary in terms of both the
accuracy of results and the specific variants the tests detect."*

## 2. The numbers

| Finding | Number | Source |
| --- | --- | --- |
| Grade ≥3 toxicity in DPYD **wild-type**, prospective, n=1018 | **23%** (231/1018) vs 39% in carriers | Henricks, Lancet Oncol 2018, PMID 30348537 |
| Grade ≥3 in wild-type adults ≥65, n=311 | **23.2%**, and **no patient characteristic predicted it on multivariate analysis** | Brokaar, Fundam Clin Pharmacol 2025, PMID 39969252 |
| Severe toxicity unexplained by the four tested variants | ~23% | Knikman (Alpe2U), Eur J Cancer 2025, PMID 40466468 |
| Sensitivity of DPYD genotyping for grade 3–4 toxicity | **12%** · specificity 97.9% · **NPV 92.8%** | Ragia, Front Pharmacol 2023, PMID 37781702 |
| Four-variant panel generally | specificity 99–100%, **sensitivity 1–12%** | ibid. and allied reviews |

**The cleanest line for a buyer [I]:** *a negative DPYD result has a negative
predictive value around 93% and a sensitivity around 12% — it rules in, it does
not rule out.*

**The sharpest finding is Brokaar:** in DPYD wild-type patients, **nothing
identified a low-risk subgroup.** There is no all-clear available to give.

**[S] Express it as a natural frequency, not a percentage.** Gigerenzer et al.
(Psychol Sci Public Interest 2007;8(2):53–96) — absolute risks, explicit
reference class, natural frequencies. For us: **"about 1 in 4 patients with a
normal DPYD result still has a severe reaction"**, not "NPV 92.8%". Carry the
counterweight: a 2016 *Medical Decision Making* paper (DOI
10.1177/0272989X16640785) urges caution about promoting natural frequencies as
universally best.

## 3. Our own Indian number is sound — quote the authors, not the arithmetic

The lede claim (*"70% of normal metabolizers still developed grade 2–3
toxicity"*) **is supported**, from the D-TORCH/AIIMS whole-exome cohort, in the
authors' own words:

> "35 out of 50 patients classified as normal metabolizer phenotype as per the
> CPIC guidelines still developed grade 2 or 3 toxicity, emphasizing the
> limitation of CPIC-based phenotype prediction and dose adjustment in the
> Indian population."

Three disciplines when using it:

1. **It is grade 2–3, not grade ≥3.** Henricks' 23% is grade ≥3. Do not put the
   two numbers side by side as if they measured the same thing.
2. **n=50 normal metabolizers.** Small. Say so before someone else does.
3. **The paper has at least two known internal errors** — our own reading found
   Table 4's column headers swapped (propagated into the abstract), and a
   separate review found Table 3 mapping `rs1801265` to the `c.1905+1G>A`
   splice change, which is wrong. **Quote the authors' sentence; do not re-derive
   numbers from its tables.**

## 4. Ancestry — the strongest version of our argument

**[S]** Chan, Zhang & Pirmohamed, *Br J Cancer* 2024, PMID 38886557 — 32
studies, 53 variants, 5 ancestry groups. Of the four European panel variants,
**only `c.1905+1G>A` also appears in South Asian, East Asian and Middle Eastern
toxicity cases.** `c.557A>G` has relatively strong evidence in African ancestry
and is **not in the UK panel**.

**[S]** NHS Race and Health Observatory (July 2024): the four tested variants
are *"found primarily in people with White European ancestry"* and the
programme *"has the potential to worsen health and race inequalities."*

That is a national health service saying our thesis, about its own programme.
It is better evidence than anything we generated.

## 5. Colour and accessibility — what is actually normative

**[S] WCAG 2.2 SC 1.4.1 Use of Color (Level A)** — colour is never the *only*
visual means of conveying information. And from the Understanding document:
where content depends on telling two colours apart, *"an additional visual
indicator will be required **regardless of the contrast ratio** between those
colors."* **Passing contrast does not exempt you from 1.4.1.**

**[S] SC 1.4.3 (AA)** text ≥ 4.5:1 · **SC 1.4.11 (AA)** UI components ≥ 3:1.

**[GAP] There is no experimental study showing red/amber/green improves or
degrades accuracy in a clinical *result* display.** The entire healthcare
colour-coding debate concerns physical medication labels and vials. Anyone
claiming "studies show traffic lights work in clinical software" is asserting.

**[S]** ISMP's position is *"colour cannot be the primary safeguard"*, not
"never use colour". **[S]** Red/green deficiency affects **upwards of 8% of
men**. **[GAP]** No prevalence study among practising physicians, and no study
measuring errors from colour-coded clinical software.

**Our position, which the evidence supports:** use colour, never *only* colour,
and never let colour carry the number.

### Procurement

- **[S] EU** — EN 301 549, functionally WCAG 2.1 AA, cited by procurement law.
- **[S] US** — Revised Section 508 incorporates WCAG 2.0 A and AA.
- **[S] India** — **GIGW 3.0 requires WCAG 2.1 AA**, aligned to the RPwD Act
  2016. **[GAP]** No evidence Indian *private* hospital procurement asks for
  accessibility conformance at all.
- **[I]** In India WCAG conformance is a differentiator you volunteer, not a
  gate you must clear — unless selling into a government hospital or an
  ABDM-linked programme, where GIGW/RPwD give it legal weight.
- ⚠️ **UK DTAC** reportedly references WCAG 2.2 AA from 6 April 2026, but the
  NHS England page did not resolve during research and the detail comes from
  third-party summaries. **Verify before claiming DTAC conformance.**

## 6. There is something to put in the gap

**[S]** Alpe2U (Knikman, Eur J Cancer 2025): among 612 patients, 22 were DPYD
wild-type with pre-treatment **uracil > 16 ng/mL**; a 50% dose reduction cut
grade ≥3 toxicity from **43% (historical full-dose) to 20%**.

Carry the caveat honestly: **n=22**; 5-FU exposure in the reduced group was
markedly lower (177 vs 381 ng·h/mL); and **no correlation was found between
uracil level and DPD enzyme activity**. This intervention risks under-dosing.

## 7. Attention budget — the one usable number

**[S]** Nurmi et al., BMC Med Inform Decis Mak 2017;17:67 — physicians given
PGx case vignettes searched ~8 minutes per case but **"spent less than 30 s
reviewing specific content"**, and wanted *"clinically meaningful descriptions
of test interpretations"*.

It measures information-seeking, not accuracy, and it is the closest thing to
an attention budget for a PGx artefact that exists. **[GAP]** There is no
direct measurement of how long a clinician spends on a PGx report.

**[I]** Design to be correct in under 30 seconds of reading. That is what the
answer band is for.

## 8. Three things for the first slide

1. **"Despite negative test results for DPD deficiency, severe toxicity may
   still occur."** — the EMA, not us.
2. **About 1 in 4 patients with a normal DPYD result still has a severe
   reaction**, and in wild-type patients *nothing* identifies a low-risk
   subgroup (Henricks 2018; Brokaar 2025).
3. **Only one of the four European panel variants appears in South Asian
   toxicity cases**, and the NHS's own race-equity body says the programme
   *"has the potential to worsen health and race inequalities."*

None of those three is our claim. All three are someone else's, and that is
what makes them usable.

---

# Addendum, 2026-10-15 — claims withdrawn, and what replaces them

Added after an audit of everything currently published or sent. **Nothing
in an application, deck, abstract or email may contradict this section.**
Check text against this list before it goes to a funder, an investor, a
reviewer or a journal.

## 9. Withdrawn — do not use, in any document

| Claim | Why it is dead | Use instead |
| --- | --- | --- |
| *"99 of 467 (21%) had INR outside target — empirical confirmation the dose was wrong"* | Wrong twice. Only **416** of the 467 had a recorded INR, so it is 23.8%. And the comparator from the same table runs **the other way**: the flagged subgroup is 23.8% out of range against **40.8%** for the rest of the high-risk group. No comparator was ever reported. **[S]** `IWPC_VALIDATION_DEEP_DIVE.md` Q5 | The monotonic dose gradient, 45.8 → 21.6 mg/wk across risk tiers. Real, reproducible, needs no outcome claim. |
| *"IWPC validated"*, *"clinical validation (5,700 patients)"* | IWPC is a **public retrospective cohort** (Klein, NEJM 2009). Not our patients, not our cohort, not a validation. Letting "5,700 patients" sit next to any partnership line implies a clinical collaboration that does not exist. | *"a retrospective consistency check on the public IWPC warfarin cohort"* |
| *"Active MOU with MCC"*, *"live clinical validation partnership"* | **There is no active MoU.** `mcc-visit/05_data_sharing_mou_outline.md` is an outline. **No MCC patient data has ever been processed.** | *"a research relationship with MCC; a data-sharing MoU is drafted and not executed"* |
| *"phenotype concordance 1.000"* | Hides its denominator. | *"100.00% agreement with PyPGx on 2,038 comparable 1000 Genomes samples of 2,504 — 466 excluded as uncallable."* PyPGx is a second implementation, **not a truth set**. |
| *"ground truth already validated against clinical reference standards"* | Unsupported. This is the line a benchmark reviewer tests hardest. | Name the actual reference set and its limits: GeT-RM is 33 cell lines, 6 South Asian, and the engine is **handed** consensus genotypes rather than detecting them. |
| *"South Asian override, validated against GenomeIndia"* | The `*9A` override was **withdrawn 2026-10-14** — CPIC classifies `*9A` as **Normal function**. The claim describes a feature that no longer exists. | Nothing. Delete it. |
| *"13 clinical validations"*, *"150+ benchmark samples"* | Flagged unverified in July, still unverified, and not reproducible from any file. | Unusable until someone re-derives them. Not "corrected" — **withdrawn**. |
| *"live production system"* (where it reads as clinical deployment) | `anukriti-api` is live **infrastructure**. No hospital or pilot is known to use it, and the Azure logs have **not** been checked. | *"a deployed research API"*. Do not imply clinical use until the logs are checked. |
| *"FHIR R5 + 21 CFR Part 11 audit trails"*, *"RFC 3161 timestamping"* | `audit_trail.py` POSTs JSON instead of a DER-encoded `TimeStampReq`, never parses or stores a token, and marks records timestamped on any HTTP 200. **No conformance assessment has been done.** | *"a SHA-256 payload hash, an append-only record and a versioned citation trail"* — provenance, **not** regulatory conformance. The two must never share a sentence. |
| *"the four variants Europe mandates screening for"* | The **EMA names zero DPYD variants** in its own text. The four come from national bodies. (The EMA 2020 requirement to test for **DPD deficiency** before fluoropyrimidines is real — that is a different claim and it is fine.) | *"the four variants routinely tested in the UK and EU"* |

## 10. The published artefact that needs fixing first

**The Zenodo paper describes a retrospective cohort as "prospective" and
calls it a "validation."** It carries a DOI, so it is citable and
permanent, and it is the only item here a third party can cite against us
indefinitely. **the MCC Molecular Oncology lead is a co-author and has not been told.** He
hears before any new version goes up — that is a courtesy owed to a
co-author, and it is also the only way the correction reads as ours
rather than as something we were caught at.

## 11. The lead claim — unchanged and stronger than anything withdrawn

**[S] The CPIC-4 panel covers 78.1% of the South Asian actionable DPYD
burden against 98.7% European**, driven by `c.2279C>T`, effectively absent
in Europeans. Measured and independently verified.

Carry its limitation in the same breath, because a reviewer finds it
anyway: the 1000 Genomes South Asian panel is **4/5 non-India diaspora**,
and rates diverge from GenomeIndia by up to 6x. A GenomeIndia comparator
is wired in. **Donor reweighting was refused** — it would manufacture a
population we did not sequence.

## 12. What we found ourselves — usable, and better than a clean record

A clean record invites one check. A published list of our own corrections
survives all of them.

- A **diplotype truncation defect** was reporting **HapB3 homozygotes as
  Normal Metabolizers on a standard fluoropyrimidine dose** — the engine
  was under-calling toxicity. Found in-project and fixed. 22 of 2,008
  comparable 1KGP samples corrected; **9 of 449 South Asian (2.0%)**.
- A **panel widening** took GeT-RM silent false negatives from **8 to 0**.
  State the honest yield: **none of the 8 is South Asian**, and the
  measured Indian yield is 2 of 15 alleles at 0.0205% and 0.0051%.
- `0.7.2` shipped a **strand defect** that stored the REF base as the
  variant allele. Found and fixed in-project.
- A **release-governance policy, a per-version release log and a CI gate**
  that fails the build if a release ships unlabelled while its clinical
  review is unsigned — `anukriti-pgx-core/docs/RELEASE_GOVERNANCE.md`.

**[S] CYP2C19 South Asian figures 36% / 14% are empirically correct** —
only the citation attached to them was wrong.

## 13. The honest state of the HapB3 withdrawal

0.11.0 **removes a dose reduction** when the HapB3 tag is present and the
causal variant is genotyped as reference. Measured in **5,008 1000 Genomes
chromosomes: it fires 0 times.**

**Do not say "it never fires."** At the published 0.223% discordance rate
the expected count among 48 tag carriers is **0.107** — a zero here cannot
distinguish 0% from the published rate. The honest statement is a **bound,
not a rate**: no more than ~6% of HapB3 carriers, and only ~16% in South
Asians, who contribute 19 tag chromosomes in the whole cohort. **No Indian
cohort measures it at all.**

Both halves travel together: it will rarely fire in Indian patients, **and**
the evidence that it is safe in them is correspondingly thin.
