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
