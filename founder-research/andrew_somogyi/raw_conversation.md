# Andrew Somogyi — Raw Conversation
Role: Professor of Pharmacology, Adelaide University | Chair, IUPHAR Pharmacogenetics, Drug Metabolism and Transport Committee
Date: May 16–18, 2026
Platform: Email (`andrew.somogyi@adelaide.edu.au` ↔ `abhimanyurbsa@gmail.com`)
Referred by: Dr. Andrea Gaedigk (PharmVar)

---

## Initial Outreach

### Abhimanyu — Saturday, May 16, 9:28 AM IST
**Subject:** Population pharmacogenomics in Asia-Pacific - referred by Dr. Andrea Gaedigk

Hi Professor Somogyi,

Dr. Andrea Gaedigk at PharmVar suggested you might be able to point
me toward researchers working on South Asian pharmacogenomics — she
mentioned you have a broad view of the Asia-Pacific PGx landscape.

I'm Abhimanyu, building Anukriti — a deterministic pharmacogenomics
inference platform focused on underrepresented populations. We
implement CPIC guidelines and PharmVar nomenclature across 13
pharmacogenes and 38 gene-drug pairs, with population-aware
reasoning and a named-refusal taxonomy: when evidence for a
specific ancestry-gene-drug combination is insufficient, we flag it
explicitly rather than returning a Eurocentric approximation. South
Asian allele characterization is our most critical current gap.

Your 2022 paper on population pharmacogenomics across ten
pharmacokinetic genes — and your conference presentation on
precision medicine challenges in the Oceania region — suggest you
have exactly the cross-regional perspective I'm looking for.

My ask is straightforward: is there anyone you know who is actively
working on pharmacogenomic allele characterization for Indian or
South Asian populations specifically? We've connected with Dr.
Sivasubbu at IGIB on the IndiGen dataset, but the South Asian PGx
researcher network seems small and we want to make sure we're not
missing key people.

Best,
Abhimanyu R B
Founder, Anukriti
anukritiai.com

---

### Andrew — Sunday, May 17, 11:46 AM IST

Dear Abhimanyu R B,

Thank you for your enquiry.

The South Asia countries are Bangladesh, Bhutan, India, the
Maldives, Nepal, Pakistan, and Sri Lanka. If that is correct, then
I know of only the following who might be in a position to assist:

**India:**
- Uppugunduri S Chakradhara Rao
- alternate E-mail: `rao (at) cansearch.ch`, `uscrao@jipmer.ac.in`

**Bhutan:**
- `kezangtshe07@gmail.com` (Jigme Dorji Wangchuck National Referral
  Hospital, Changzamtog Thimphu Bhutan 11001)
- Kezang is relatively junior as he has applied to Adelaide
  University to enrol for a PhD in pharmacogenomics.

I do not know of researchers in Bangladesh, the Maldives, Nepal,
Pakistan, or Sri Lanka.

Regards,
Andrew Somogyi

*(Signature: Andrew Somogyi, PhC, DHP, MSc, PhD, FFPMANZCA, FBPhS,
FASCEPT — Professor, Discipline of Pharmacology, School of Pharmacy
and Biomedical Science, College of Health, Adelaide University.
Chair: IUPHAR Pharmacogenetics, Drug Metabolism and Transport
Committee.)*

---

## Follow-Up — Trial Pipeline Format & Population Granularity

### Abhimanyu — Sunday, May 17, 12:17 PM IST

Hi Prof. Somogyi,

Thank you — I've reached out to both Prof. Rao and Kezang today. I
really appreciate you taking the time to map out who's working in
this space.

Your observation that the South Asian PGx network is sparse is
itself a useful signal for us — it confirms that the data gap we're
trying to address is real and largely uncharted.

Since you have such a broad view of the Asia-Pacific PGx landscape,
I'd love your perspective on a few things we're working through:

1. In current clinical trial pipelines that incorporate PGx, what
   genomic data formats are teams actually submitting: raw VCF,
   processed diplotype tables, or something else? We want to make
   sure our output format matches what trial teams can actually
   consume.
2. When comparing allele frequencies across populations for a
   multi-ancestry trial cohort, what are the key constraints or
   pitfalls to watch out for — particularly when reference panels
   are Eurocentric?
3. Is there a minimum viable sample size you'd consider
   statistically meaningful for estimating allele frequencies in a
   population like Bhutan or a specific Indian sub-population?

Any perspective you can share would be genuinely useful as we build
out the South Asian layer of the platform.

Best,
Abhimanyu R B
Founder, AnukritiAI
anukritiai.com

---

### Andrew — Monday, May 18, 5:41 AM IST

Dear Abhimanyu R B,

To answer your questions — see below.

Regards,
Andrew Somogyi

> **Q1 — current trial-pipeline formats:**
> *"It is mostly processed diplotype tables plus function or
> activity (e.g. poor metaboliser)."*

> **Q2 — pitfalls when reference panels are Eurocentric:**
> *"Some panels are now global panels and incorporate variants that
> may be rare in Europeans but more common in some jurisdictions
> (e.g. CYP2C19, CYP2C9, VKORC1, HLAs)."*

> **Q3 — minimum viable sample size for ancestry-specific allele
> frequency:**
> *"No — as it depends on the frequency of the variant being
> tested. As a guess several hundred, but even in Bhutan there are
> 3 different populations."*

---

## Follow-Up — Pre-Trial vs Post-Hoc PGx Stratification

### Abhimanyu — Monday, May 18, 8:13 AM IST

Dear Prof. Somogyi,

Thank you — these are exactly the kind of ground-truth answers that
are hard to find in the literature.

A few quick takeaways from our end:

- Our current output already matches what you described: we produce
  metabolizer phenotype calls (PM/IM/NM/RM/UM) with activity
  scores, so we're aligned with what trial teams actually consume.
- The panel selection point is well taken. Our gene coverage
  already includes CYP2C19, CYP2C9, VKORC1, and HLA-B*57:01. Your
  note about variants that are rare in Europeans but common in a
  specific jurisdiction is exactly why we treat population as a
  first-class input rather than metadata.
- The sub-population granularity point resonates strongly. We've
  already learned not to treat "South Asian" as monolithic; we
  support GIH, ITU, and PJL sub-populations, and your Bhutan
  example is a good reminder that even small countries have
  internal structure we need to respect.

One more question if I may: In your experience, are CROs running
Asia-Pacific trials currently incorporating PGx stratification at
the pre-trial stage, or is it still mostly post-hoc analysis?

Warm regards,
Abhimanyu R B

---

### Andrew — Monday, May 18, 10:03 AM IST

Dear Abhimanyu R B,

The HLAs that can cause life threatening drug reactions can be very
ancestry specific and with frequencies that vary very widely — so
one needs to be quite careful in terms of what HLA test for which
drug.

To answer your Q —

> *"Are CROs running Asia-Pacific trials currently incorporating
> PGx stratification at the pre-trial stage, or is it still mostly
> post-hoc analysis?"*
>
> *"I don't know but I suspect it used to be the latter but now
> that PGx is very mainstream it's more at the pre-trial stage. But
> don't hold me to it."*

Regards,
Andrew

---

### Andrew — Monday, May 18, 10:47 AM IST (with attachment)

This might be of interest:

Regards,
Andrew

> 📎 **Attachment:** Huddart et al. 2019, *Clinical Pharmacology &
> Therapeutics*. Local copy:
> [`anukriti_docs/papers/Huddart_et_al-2019-Clinical_Pharmacology_&_Therapeutics.pdf`](../../papers/Huddart_et_al-2019-Clinical_Pharmacology_&_Therapeutics.pdf)
> (PharmGKB population grouping system; introduces SSA/AAC split,
> Near Eastern category; CYP2C9*8 example for Sub-Saharan
> populations).

---

## Closing

### Abhimanyu — Monday, May 18, 2:35 PM IST

Dear Prof. Somogyi,

Thank you for sharing this. The Huddart et al. paper is directly
relevant to a design decision we've been working through.

We currently use 1000 Genomes superpopulation codes (AFR, AMR, EAS,
EUR, SAS) as our population taxonomy. The PharmGKB grouping system
is more refined in a few important ways, particularly the SSA/AAC
split and the addition of Near Eastern. We'll need to document
explicitly where Anukriti aligns with it and where we deliberately
differ.

The CYP2C9*8 example in the paper illustrates why this matters.
Warfarin dosing algorithms built on *2 and *3 systematically miss
the most common reduced-function allele in Sub-Saharan populations.
Our named-refusal system is designed to flag exactly this kind of
Eurocentric gap rather than silently returning a biased
approximation.

I really appreciate you pointing us to this.

Warm regards,
Abhimanyu R B
