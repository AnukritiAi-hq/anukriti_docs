# 08a — Treating Everyone Fairly

> Different customers have different needs. "Equal treatment" doesn't
> mean "the same cake for everyone." It means "the same honest care
> for everyone."

---

## The Story

Anu's bakery has customers from all over town.

Some customers love chili-chocolate cupcakes. Some can't even smell
chili. Some are allergic to peanuts. Some are dairy-free. Some are
from the next neighborhood over and mostly want plain vanilla.

Anu thinks about what "treating everyone equally" means at her
bakery. Three different ideas:

**Idea 1: "Give everyone the same cupcake."**

Sounds equal. But if Anu always bakes the chocolate-chili cupcake
her most common customers love, the peanut-allergic customer gets
sick, the dairy-free customer gets sick, and the person who can't
handle spice gets a sad afternoon.

*This isn't fairness. This is just stubbornness.*

**Idea 2: "Do the same careful work for every customer."**

Anu has a checklist she follows for every order, no matter who
ordered it:

- Ask about allergies
- Ask about preferences
- Check the recipe for ingredients
- Check if she has a tested recipe for that combination
- If something looks risky, say so

Every customer gets the **same checklist**. Not the same cupcake
— the same *quality of care*.

*This is real fairness.*

**Idea 3: "Pretend I can make anything for anyone with the same
confidence."**

What if Anu says "yes, I can make a nut-free, dairy-free,
egg-free, gluten-free, sugar-free rainbow cake" — but she's
never actually done it, and she doesn't have safe ingredients,
and she's just guessing?

*This is also bad. It pretends confidence that isn't there.*

Anu picks **Idea 2**. Same checklist for everyone. Sometimes
that means a honest "I can't make that safely for you today,
come back next week when I've sourced nut-free equipment." That
honest "no" is **better than** a confident fake "yes" that
sends a customer to the hospital.

Our AI system makes the same choice.

---

## What this means for computers

Our system is asked questions about drugs and patients every day.
The patients come from all different backgrounds — South Asian,
East Asian, European, African, Latino.

Most published medical research was done on European patients. If
we **treated everyone the same way** (Idea 1), we'd just apply
European-derived recommendations to everyone. That's the problem
we exist to solve, not our goal.

Instead, we do Idea 2:

1. **Same pipeline** for every patient, regardless of ancestry.
2. **Checks** for whether we have evidence specifically for this
   patient's ancestry.
3. **Honest downgrades or refusals** when the evidence is thin.

Sometimes our answer for one population is a confident "do this,
here's the citation." For another population in a similar
situation, our answer might be "the evidence is thin for this
ancestry — recommendation downgraded." That's not us being
unfair. That's us being honest.

**A confident answer for one population and a downgraded answer
for another is not unequal treatment. It's equal *rigor* with
unequal *confidence*, and the unequal confidence is what
honesty looks like.**

---

## What we built

Five concrete things in the code make this work. Each one is a
specific file.

### 1. Population is a "thing" in our knowledge graph

`knowledge_graph/schema.py`

Remember the knowledge graph from [Module 08](08-walking-a-map.md)?
It has 10 kinds of "things" (nodes). **`POPULATION`** is one of
those kinds — just like `GENE` and `DRUG`. Not a label attached
to other things. A thing of its own.

Arrows from alleles to populations carry numbers — the actual
frequency. CYP2C19 \*2 → South Asian has weight 0.36. That's
not a label, that's math.

When the walker walks, the weights multiply. The same gene+drug
combo produces a **different path weight** for different
populations. The bigger the weight, the more our system says
"yes, this ancestry really does matter here."

### 2. When looking things up, we look through population-shaped glasses

`retrieval/multi_strategy/biomedical_retriever.py`

When we search for evidence, we re-rank the results by how
well they match the patient's population.

A paper that mentions "South Asian cohort" jumps to the top
when we're answering about a SAS patient. A paper that only
talks about "European cohort" gets pushed down. A paper that
doesn't mention any population stays in the middle.

**Same papers, different top of the list.** For the EUR patient,
the European paper is at the top. For the SAS patient, the
Gujarati-cohort paper is at the top.

### 3. "Do we have ancestry evidence?" is one of 6 required checks

`core/evidence_sufficiency/coverage/claim_coverage.py`

Before we give an answer, we check 6 things called **facets**.
One of them is `POPULATION`: *"Do we have evidence specifically
for this patient's ancestry?"*

- If yes → mark as COVERED
- If sort of → mark as UNCERTAIN
- If no → mark as MISSING

If it's MISSING or UNCERTAIN, rules fire:

- R5 (MISSING) → **ESCALATE** (get more input)
- R9 (UNCERTAIN) → **DOWNGRADE** (answer with a caveat)

We literally **refuse to ignore** whether we have ancestry-
specific evidence. It's not a maybe. It's one of the 6
mandatory facets.

### 4. We have a bias detector with real numbers

`core/evidence_sufficiency/uncertainty/bias_detector.py`

The `PopulationEvidenceBiasDetector` checks for three specific
unfair patterns, each with a number, not a vibe:

- **EUROCENTRIC_IMBALANCE** — if the patient isn't European but
  all our evidence is from European cohorts, flag it.
- **ANCESTRY_SCARCITY** — if we have less than half the data
  for this ancestry compared to our best-represented one,
  flag it.
- **UNSUPPORTED_EXTRAPOLATION** — if we don't have ancestry
  data at all and we're being asked about that population,
  flag it.

These aren't "maybe the model is biased." These are specific
checks that fire specific flags.

### 5. Our refusal is a feature, not an error

`demos/evidence_sufficiency_demo.py`

One canonical test: *"Codeine + CYP2D6 + African ancestry —
recommendation?"*

This genuinely has thin evidence in the medical literature for
African populations. A general AI would answer confidently
anyway (usually derived from implicit European priors).

Our system **refuses**. The output has:

```
decision:      DOWNGRADE
verdict:       UNCERTAIN
uncertainty:   HIGH
bias_findings: [ANCESTRY_SCARCITY]
```

And — crucially — it **names the rule that made it refuse**. R9
fired because POPULATION was UNCERTAIN. V7 fired. U3 and U5
fired. The bias detector flagged `ANCESTRY_SCARCITY`.

A reviewer can audit this refusal. They can see which specific
check failed. They can decide whether our caution was warranted.
**Compare that to a confident answer that might be wrong — which
one do you trust more?**

---

## The three honest gaps

If we're going to talk about fairness, we have to say where
**we're not fair enough yet**. Three places:

### Gap 1: We only have 5 population "buckets"

We have EUR, EAS, SAS, AFR, AMR. That's five buckets for all
8 billion people on Earth.

A Gujarati patient and a Bengali patient both get classified as
"SAS" in our system. Clinically, their allele frequencies can
differ. But our knowledge graph doesn't distinguish them yet.

We have a **slot** in the schema (`NodeKind.ANCESTRY`) where
sub-populations can live, but it's empty today. We didn't want
to add fake sub-population data just to look thorough. When
the published evidence justifies it, sub-populations go in.

### Gap 2: Mixed ancestry doesn't fit anywhere

Many people have parents from different populations. Our 5-bucket
system forces them into one bucket — usually whichever one the
clinician guesses.

The honest answer would be a mixture vector ("this patient is
40% EUR, 30% AMR, 20% AFR, 10% EAS"), and then we'd blend the
reasoning proportionally. We don't do this yet. It's a real
research project, not a small change.

### Gap 3: We say "the evidence is thin" — we don't fix the thin evidence

When our bias detector fires `ANCESTRY_SCARCITY`, what does it
actually do? It **downgrades our answer**. It tells the user:
"the evidence is thin here, so we're not confident."

That's honest, but it's not helpful. The patient still needs a
decision. "We can't help you" is not a clinically useful answer.

Fixing this requires either:

1. More diverse cohort data in medicine at large (an
   upstream-research problem, not something our code can fix)
2. New reasoning modes that use related populations as a
   cautious prior (real research)

We don't do either yet. We name the problem. We don't solve it.
Future work.

---

## So are we really treating everyone equally?

Let's ask the question three ways:

- **Same pipeline for everyone?** ✅ Yes. Every run goes through
  the same 5 stages, 6 facets, 4 verification engines, same
  boundary.
- **Same confidence for everyone?** ❌ No, and on purpose. If
  the evidence for one population is strong and for another is
  weak, the confidence should be different. Forcing equal
  confidence would be lying.
- **Same clinical usefulness for everyone?** ❌ No — and this is
  the hard honest truth. A patient in an under-studied
  population will get a less actionable answer from our system
  than a patient in a well-studied one.

That last point could be the answer to "are you being unfair?"
Our response: **the unfairness is in the medical evidence base,
not in our reasoning.** Other systems make that unfairness
invisible. We make it visible. We name the rule that fired. We
cite the specific bias we detected. We refuse to paper over it.

That's what "population-aware" means in our system.

---

## Try it yourself

Run the demo:

```bash
python -m demos.evidence_sufficiency_demo
```

You'll see three scenarios:

| Scenario | Outcome |
|----------|---------|
| Clopidogrel + CYP2C19 + South Asian | ✓ SUFFICIENT (strong evidence for SAS) |
| Carbamazepine + HLA-B\*15:02 + East Asian | ✓ SUFFICIENT (strong EAS evidence) |
| Codeine + CYP2D6 + African ancestry | ✗ DOWNGRADE (thin AFR evidence) |

The first two are confident answers. The third is an honest
refusal with a named rule.

**All three used the same pipeline. All three were handled with
the same rigor. The different outcomes reflect different
evidence realities.** That's the feature.

---

## The grown-up version

> The platform's population-awareness is built from 5 code-level
> mechanisms and 3 documented gaps. Mechanisms:
>
> 1. **KG first-class `NodeKind.POPULATION`** with weighted
>    `HIGHER_FREQUENCY_IN` edges (10-value closed enum
>    `NodeKind`; 7-value closed `EdgeKind`)
> 2. **`PopulationAwareRetriever`** — signed-boost re-ranker
>    with word-boundary regex for 3-letter super-population
>    codes
> 3. **Population as one of 6 `ClaimEvidenceFacet` values** in
>    the sufficiency layer, with R-rules R5 (MISSING → ESCALATE)
>    and R9 (UNCERTAIN → DOWNGRADE)
> 4. **`PopulationEvidenceBiasDetector`** — 3 closed `BiasKind`
>    values with concrete numeric thresholds (Eurocentric
>    imbalance, ancestry scarcity, unsupported extrapolation)
> 5. **Honest refusal contract** — every abstention cites the
>    specific rule ID that fired (R1..R12, V1..V10, U1..U9) plus
>    any bias findings, persisted in `EvidenceSufficiencyTrace`
>
> Gaps:
>
> - **Sub-populations unseeded** — `NodeKind.ANCESTRY` is a
>   populated extension point with zero seed nodes
> - **5-bucket closed `SuperPopulation` enum** excludes mixed
>   ancestry; categorical-only, no mixture vector today
> - **Named not fixed** — `ANCESTRY_SCARCITY` triggers a
>   DOWNGRADE; no fallback reasoning mode uses related-population
>   priors
>
> Epistemic posture: equal reasoning rigor, unequal confidence
> proportional to actual evidence density, named refusals with
> auditable rule IDs. The unfairness is in the upstream evidence
> base (Eurocentric cohort bias in medical research), not in our
> reasoning process. We make the unfairness *visible* where
> other systems make it *invisible*.
>
> The engineering-depth version of this section is in
> [`../docs/08-population-awareness.md`](../docs/08-population-awareness.md)
> under "What 'population-aware' actually means here."

---

## What you learned

Before this module: "treating every population equally" sounded
like a slogan without a mechanism.

Now: fairness means **equal reasoning rigor, honest confidence
differences, named refusals**. Our system doesn't pretend to
know what it doesn't know. It's not the same cake for every
customer — it's the same careful checklist for every customer,
with honest "I can't safely make that" answers when the
ingredients aren't there.

That's what population-aware drug risk prediction actually
looks like in code.

---

Back to: [Module 08 — Walking a Map](08-walking-a-map.md) · [Module
09 — Using Tools](09-using-tools.md)

Cross-course: this module's engineering-depth version lives at
[`../docs/08-population-awareness.md`](../docs/08-population-awareness.md).
