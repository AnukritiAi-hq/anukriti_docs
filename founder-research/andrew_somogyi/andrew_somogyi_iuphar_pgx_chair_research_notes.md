# Andrew Somogyi — Research Conversation Notes
Role: Professor of Pharmacology, Adelaide University | Chair, IUPHAR Pharmacogenetics, Drug Metabolism and Transport Committee
Date: May 16–18, 2026
Platform: Email (`andrew.somogyi@adelaide.edu.au`)
Referred by: Dr. Andrea Gaedigk (PharmVar)

## Key Insights

### Why this conversation matters

Prof. Somogyi sits in two structurally important positions:

1. **Chair, IUPHAR Pharmacogenetics, Drug Metabolism and Transport
   Committee** — global view of the PGx-research landscape across
   committees, working groups, and active funding lines.
2. **Senior PGx investigator at Adelaide** — Asia-Pacific
   visibility, especially for South Asia and Oceania.

He was referred by Andrea Gaedigk specifically as a *connector*
("may be able to direct to other people") — and the conversation
delivered exactly that: 2 named contacts in 2 South Asian countries,
plus first-hand answers to three operational questions about
Asia-Pacific PGx trial workflow that are hard to find in the
literature.

### South Asia is genuinely sparse — confirmed at the IUPHAR level

Of 7 South Asian countries (Bangladesh, Bhutan, India, Maldives,
Nepal, Pakistan, Sri Lanka), Prof. Somogyi could name **only two
contacts in two countries**. He explicitly stated he does not know
of researchers in Bangladesh, Maldives, Nepal, Pakistan, or Sri
Lanka.

This is now the **second independent senior steward** (after
Andrea Gaedigk at PharmVar) to confirm the South Asian PGx data
gap at the source layer. The data sparsity is structural, not a
discovery problem on Anukriti's side.

### Three direct, citeable answers on PGx trial operations

These are the kind of ground-truth statements Anukriti can build
roadmap and product-format decisions on. Captured verbatim
because they are operationally actionable:

| Question | Somogyi's answer |
|---|---|
| **Output format trial teams consume** | *"Mostly processed diplotype tables plus function or activity (e.g. poor metaboliser)."* |
| **Eurocentric panel pitfalls** | Some panels are now global and incorporate variants rare in Europeans but more common in some jurisdictions (CYP2C19, CYP2C9, VKORC1, HLAs). |
| **Min sample size for ancestry-specific allele freq** | No fixed number — depends on variant frequency. Guess: *"several hundred, but even in Bhutan there are 3 different populations."* |
| **CRO PGx pre-trial vs post-hoc** | *"Used to be the latter but now that PGx is very mainstream it's more at the pre-trial stage."* (caveat: "don't hold me to it") |
| **HLA caution** | HLAs causing life-threatening reactions are *"very ancestry specific and with frequencies that vary very widely — one needs to be quite careful in terms of what HLA test for which drug."* |

### Population taxonomy gap — Huddart et al. 2019

Prof. Somogyi closed by sharing the **Huddart et al. 2019**
*Clinical Pharmacology & Therapeutics* paper (saved at
`anukriti_docs/papers/Huddart_et_al-2019-Clinical_Pharmacology_&_Therapeutics.pdf`,
attached on May 18). The paper introduces the **PharmGKB
population grouping system**, which is a refinement of the 1000
Genomes superpopulation codes Anukriti currently uses.

**Where Anukriti and PharmGKB taxonomy differ:**

| Anukriti (1000G superpop) | PharmGKB (Huddart 2019) |
|---|---|
| AFR (single bucket) | **SSA** (Sub-Saharan African) + **AAC** (African-American/Afro-Caribbean) — split |
| — (no equivalent) | **NEA** (Near Eastern) — separate category |
| EUR / EAS / SAS / AMR | Aligned (with PharmGKB-specific naming) |

**Why this matters operationally — the CYP2C9*8 case:** warfarin
dosing algorithms built on `*2`/`*3` systematically miss CYP2C9*8,
the most common reduced-function allele in Sub-Saharan populations.
Without an SSA/AAC split, this drift is **invisible** to the model.
This is the exact class of failure Anukriti's named-refusal system
exists to surface (rules R1, R2, U2, U3 fire when ancestry-specific
evidence is insufficient, rather than silently extrapolating).

## Important Observations

- **Two senior stewards now confirm sparsity.** Andrea Gaedigk
  (PharmVar) and Andrew Somogyi (IUPHAR) — independently. This
  pattern is now strong enough to cite as third-party validation
  in strategy and pitch documents.
- **CRO pre-trial PGx is becoming mainstream.** Somogyi's
  qualified guess is that PGx stratification is shifting from
  post-hoc analysis to pre-trial — *but he hedges*. We should not
  cite him as a definitive source on this; treat it as a
  directional signal that warrants confirmation from a CRO
  bioinformatician contact.
- **Sample-size guidance is more nuanced than headline numbers.**
  "Several hundred" is the floor, but variant frequency drives the
  real answer. For Anukriti's named-refusal taxonomy, this
  validates rule R7 (ALLELE MISSING → REQUEST_MORE) and U2
  (missing non-conflict facet → HIGH uncertainty) — we should
  *not* declare a fixed n_min threshold; we should refuse on
  structured evidence absence instead.
- **Sub-population granularity is real even at small-country
  scale.** The "Bhutan has 3 populations" remark generalizes — no
  single ancestry label is monolithic. This already aligns with
  Anukriti's GIH/ITU/PJL sub-population support; the question is
  whether the taxonomy needs more refinement post-Huddart.

## Recommendations He Gave

### South Asian PGx contacts

| Contact | Country | Email | Status / Stage |
|---|---|---|---|
| **Uppugunduri S Chakradhara Rao** | India | `rao@cansearch.ch` (alt) / `uscrao@jipmer.ac.in` | Senior; published South Asian PGx work |
| **Kezang** | Bhutan | `kezangtshe07@gmail.com` (Jigme Dorji Wangchuck National Referral Hospital, Thimphu) | Junior; PhD applicant at Adelaide, pharmacogenomics |

Per the May 18 follow-up, Abhimanyu has already reached out to
both. Track replies.

### Open gaps Somogyi could not fill

He explicitly does not know researchers in: **Bangladesh,
Maldives, Nepal, Pakistan, Sri Lanka**. These are open
discovery targets — likely require senior-author search on
gene-of-interest publications (per Andrea Gaedigk's general
principle).

## Interpretation for Anukriti

### Action items

1. **Output format alignment — confirmed, no change needed.**
   Anukriti's current output (PM/IM/NM/RM/UM phenotype calls plus
   activity scores via `anukriti-pgx-core` Layer 2) **already
   matches** what Somogyi describes trial teams consuming. Document
   this as a validated design decision in
   `anukriti_docs/THREE_REPO_INTEGRATION_DEEP_DIVE.md`.

2. **Population-taxonomy decision — needs an explicit ADR.**
   Anukriti uses 1000G superpop codes (AFR/AMR/EAS/EUR/SAS).
   Huddart 2019 / PharmGKB uses a refined system (SSA/AAC split,
   NEA added). Three options:

   - (a) **Adopt PharmGKB grouping** — more clinically faithful,
     surfaces SSA/AAC drift; cost is rewriting `anukriti-swarm/
     core/models/population_*.py` enums and the demo signatures
     for `cohort_demo`.
   - (b) **Stay on 1000G, document the divergence explicitly** —
     low cost; honest about what we cannot resolve; named-refusal
     fires on the cases where the difference matters anyway.
   - (c) **Hybrid** — keep 1000G as the entry-point taxonomy, add
     a PharmGKB-grouping mapping layer in the KG, surface the
     more refined view in evidence-sufficiency rules.

   This deserves a written ADR. Likely landing site:
   `anukriti-pgx-core/docs/adr/0003-population-taxonomy-and-pharmgkb-alignment.md`
   (continuing the existing ADR series).

3. **HLA caller scope refinement.** Somogyi explicitly cautioned
   that HLAs need ancestry-specific test selection. The current
   Anukriti flagship covers HLA-B*57:01 (abacavir) and the
   `anukriti-rapid-agent` demo flags HLA-B*15:02 (carbamazepine,
   EAS). But the broader HLA layer is still in the shim per
   `anukriti-pgx-core/PROJECT_CONTEXT.md` D8 — this conversation
   reinforces that any future HLA expansion must be paired with
   an explicit ancestry-coverage table per HLA-drug pair, not a
   generic caller. Do not generalize the HLA layer without that
   per-pair coverage map.

4. **CYP2C9*8 + AAC/SSA case study.** Add this as a worked example
   in `anukriti_docs/EVIDENCE_SUFFICIENCY_LAYER_DEEP_DIVE.md` — it
   is the canonical "Eurocentric panel silently misses common
   variant" case, and Somogyi's referral makes it citeable.

5. **Citation discipline.** Add Huddart et al. 2019 to the
   citations list everywhere we document the population taxonomy
   choice. Specifically:

   - `anukriti-pgx-core/PROJECT_CONTEXT.md` Coverage / D-decision section
   - `anukriti-swarm/architecture/evidence-sufficiency.md`
   - The new ADR-0003 above
   - `anukriti-pgx-core/docs/strategy.md` Moat section

6. **Update the IUPHAR / PharmVar narrative.** With both Andrea
   Gaedigk (PharmVar) and Andrew Somogyi (IUPHAR Chair) confirming
   South Asian sparsity at the source level, the strategy doc can
   now cite **two independent senior stewards** rather than one.
   Update `anukriti-pgx-core/docs/strategy.md` accordingly.

### Strategic-quote candidates (permission gate)

The most quotable lines in the conversation, ranked by signal:

| Quote | Signal | Permission gate? |
|---|---|---|
| "I do not know of researchers in Bangladesh, the Maldives, Nepal, Pakistan, or Sri Lanka." | Independent confirmation of South Asian sparsity | **Yes — get permission before external use.** Internal docs can cite freely. |
| "Some panels are now global panels and incorporate variants that may be rare in Europeans but more common in some jurisdictions (e.g. CYP2C19, CYP2C9, VKORC1, HLAs)." | Confirms population-as-first-class-input thesis | **Yes — get permission before external use.** |
| "Mostly processed diplotype tables plus function or activity (e.g. poor metaboliser)." | Confirms output format — matches Anukriti's | Internal use safe. External — paraphrase rather than quote unless permission obtained. |
| "Now that PGx is very mainstream it's more at the pre-trial stage. But don't hold me to it." | Useful directional signal — but the hedge means **do not cite as a fact**. Paraphrase only. | Treat as background, not a quote. |

Same permission-gate principle as the Andrea Gaedigk conversation:
internal docs (this file, PROJECT_CONTEXT, IDEA_REFINEMENT,
investor-outbound drafts at the `AnukritiAi-hq` org level) can
quote and cite freely. Anything that goes external — public
website, published deck, paper, blog post — sends a one-line
permission ask first:

> *"Would you be comfortable with me citing your observation that
> '[quote]' in our [strategy doc / pitch / paper], with attribution?
> Happy to share the framing for review first."*

## Follow-Up Leads

In priority order:

1. **Uppugunduri S Chakradhara Rao** (India, JIPMER + cansearch)
   — direct South Asian PGx researcher; primary lead. Outreach
   already sent May 18.
2. **Kezang** (Bhutan, JDWNRH) — junior but strategically
   placed; if his PhD lands at Adelaide it creates a long-term
   collaboration channel via Somogyi himself. Outreach already
   sent May 18.
3. **CRO bioinformatician contact** — to confirm or refute
   Somogyi's hedged "PGx is mainstream pre-trial now" claim.
   Open discovery target.
4. **Senior-author search** — Bangladesh, Maldives, Nepal,
   Pakistan, Sri Lanka. Per Andrea Gaedigk's general principle:
   read recent papers on CYP2C19 / CYP2D6 / HLA-B in those
   populations and cold-email senior authors.
5. **Huddart et al. 2019 senior author** — if a population-
   taxonomy ADR moves toward PharmGKB alignment, that author is
   a natural reviewer/sounding-board.

## Linked Platform Context

This conversation feeds into:

- **`anukriti-pgx-core/PROJECT_CONTEXT.md`** — Coverage / D-decision
  log; population taxonomy will get a new D-decision row.
- **`anukriti-pgx-core/docs/strategy.md`** — Moat section now has
  *two* senior-steward citations (Gaedigk + Somogyi).
- **`anukriti-pgx-core/docs/research-partnerships.md`** — add
  Adelaide / IUPHAR PGx Committee as a partnership-pipeline
  candidate; add Rao + Kezang as warm leads under "South Asian
  PGx network."
- **`anukriti-pgx-core/docs/adr/`** — new ADR-0003 candidate on
  population taxonomy choice (1000G vs PharmGKB).
- **`anukriti_docs/papers/Huddart_et_al-2019-Clinical_Pharmacology_&_Therapeutics.pdf`** —
  source for the PharmGKB grouping system, attached by Somogyi
  May 18.
- **`anukriti_docs/EVIDENCE_SUFFICIENCY_LAYER_DEEP_DIVE.md`** —
  CYP2C9*8 + AAC/SSA worked example.
- **`anukriti_docs/IDEA_REFINEMENT_AND_PHASING_2026-05-14.md`** —
  Outreach contact list: add Somogyi as completed (referral
  source), add Rao + Kezang as pending replies.
- **`anukriti_docs/founder-research/andrea_gaedigk/`** — upstream
  conversation; this one is a direct continuation of her
  referral.
