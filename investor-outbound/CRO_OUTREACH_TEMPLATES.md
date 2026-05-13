# CRO Outreach — Email & LinkedIn Templates

> **Practical outbound templates for 20-CRO pipeline from
> `PLATFORM_ANALYSIS_2026-05-11.md §6 Weeks 3-4`.**
>
> Pair these with [`CRO_ONE_PAGER.md`](CRO_ONE_PAGER.md) — the one-pager
> is the artifact, these are the openers. Keep the cadence to 5
> outbound/week per template-A; A/B test subject lines sparingly.

---

## Guiding principles

1. **Named person, not a list.** If you can't name the CRO's lead
   bioinformatician or a specific trial team, do the research first.
   Generic "Dear Sir/Madam" gets filtered.
2. **One artifact per email.** Do not attach a deck + one-pager + repo
   link + demo URL in the first message. Pick one.
3. **One ask per email.** A 20-minute call. Not "a call or a demo or
   feedback or intro to colleagues." One.
4. **Lead with their problem, not our architecture.** Closed-enum
   scope firewalls are interesting to engineers, not trial ops.
5. **No hype adjectives.** Every claim in the first email must be
   falsifiable within 60 seconds of them clicking the demo link.
6. **Log every outreach in [`founder-research/`](../founder-research/).**
   One subfolder per contact. Preserve raw transcripts.

---

## Tier reference (who to send which template to)

| Role at the CRO | Primary pain | Best template |
|---|---|---|
| Head of Bioinformatics / Genomics | Stratification tooling gaps, scale | Template A |
| Clinical Pharmacologist | Evidence-base gaps by ancestry, dosing logic | Template B |
| Pharmacovigilance / Drug Safety Lead | Post-hoc ADR surveillance tied to genotype | Template C |
| Trial Operations / Enrollment | Diversity-of-enrollment commitments, FDA Diversity Action Plans | Template D |
| Regulatory Affairs | RUO vs SaMD positioning, audit trail requirements | Template E |

---

## Template A — Head of Bioinformatics / Genomics (PRIMARY)

**Subject:** Population-aware PGx stratification for {CRO name} trials — 20 min?

Hi {First name},

I lead [Anukriti](https://anukriti.abhimanyurb.com), a
pharmacogenomics reasoning platform focused on trial stratification
across non-European ancestries. We published the deterministic core
on PyPI ([`anukriti-pgx-core==0.2.1`](https://pypi.org/project/anukriti-pgx-core/));
the full platform was an AWS AI Competition Finalist this cycle.

I noticed {CRO name} runs trials in {therapeutic area / geography
that includes non-EUR enrollment} — which is where current CPIC
dosing logic starts producing systematic under-warning for
population-specific PGx risk. CYP2C19 is the canonical example:
14% of South Asians are poor metabolizers and can't activate
clopidogrel, roughly 7× the European rate, yet stratification
tooling typically applies Eurocentric defaults silently.

We built the opposite posture. The core reasoning is deterministic
(no LLM in the safety path), outputs are FHIR R5 with 21 CFR Part 11
audit trails, and when evidence for a specific ancestry is thin the
system refuses with a named rule ID rather than synthesizing a
confident wrong answer.

Would a 20-minute walkthrough be useful? I'd demo the
`/trial/export` endpoint against a population shape similar to your
typical enrollment mix. If there's no fit I'll say so on the call
and not take more of your time.

Here's the one-pager: {link to CRO_ONE_PAGER.md hosted or PDF}

Best,
Abhimanyu
{phone or Calendly link}

*[Anukriti on GitHub](https://github.com/AnukritiAi-hq) ·
[PyPI](https://pypi.org/project/anukriti-pgx-core/) ·
[Live demo](https://anukriti.abhimanyurb.com)*

---

## Template B — Clinical Pharmacologist

**Subject:** Evidence-sufficiency gating for PGx recommendations across ancestries

Hi {First name},

Your work on {specific paper / talk / trial} is directly adjacent to
what I'm building — a PGx reasoning platform where evidence density
per ancestry is a first-class runtime property, not a footnote.

Concretely: instead of emitting a CPIC recommendation uniformly
across populations, the system checks 6 evidence facets (allele,
phenotype, CPIC, population, recommendation, conflict-free) and
names a specific bias pattern when evidence for the target ancestry
is thin — `EUROCENTRIC_IMBALANCE`, `ANCESTRY_SCARCITY`, or
`UNSUPPORTED_EXTRAPOLATION`. The refusal cites the rule ID so a
regulatory reviewer can trace why.

I'd value 20 minutes of your thinking on where current PGx
recommendation tooling gets this wrong in practice — trial vs
clinical — and whether the named-refusal posture actually helps or
just adds friction.

Happy to run the demo against a specific drug-gene-ancestry case
you've seen go sideways.

One-pager: {link}

Best,
Abhimanyu

---

## Template C — Pharmacovigilance / Drug Safety

**Subject:** Connecting post-hoc ADR signals to pre-trial PGx stratification

Hi {First name},

Short version: I've built a pre-trial pharmacogenomic risk
stratification tool and I'm trying to understand how it would
(or wouldn't) integrate with what pharmacovigilance teams already
do post-hoc.

Specifically:

- The platform emits FHIR R5 `DetectedIssue` + `ClinicalImpression`
  + `Provenance` resources per subject, with CPIC-pinned
  recommendations and evidence-sufficiency verdicts.
- When an ADR surfaces in post-trial surveillance, the provenance
  chain lets you trace back to whether the genotype group was
  flagged, abstained on, or missed at enrollment.

Does that kind of traceability interact with your workflow, or is
it solving a problem you don't have? 20-minute call would genuinely
help me calibrate.

Best,
Abhimanyu

---

## Template D — Trial Operations / Enrollment

**Subject:** FDA Diversity Action Plans + PGx stratification tooling

Hi {First name},

FDA's Diversity Action Plan guidance (2024) puts enrollment
diversity on CROs in a new way — but the stratification tooling
most teams use still applies Eurocentric dosing logic uniformly,
which produces the "diverse enrollment, Eurocentric analysis"
failure pattern.

I built a tool that flags this at the cohort-design stage:
deterministic PGx stratification with explicit
population-coverage facets, FHIR R5 output, and named refusals when
evidence for a specific ancestry is thin.

Would 20 minutes be useful to walk through a cohort shape similar
to what {CRO name} typically enrolls? Nothing to sell — I'm in the
evaluation-pilot phase and looking for trial-ops feedback on
whether the output schema actually fits real enrollment ops.

Best,
Abhimanyu

---

## Template E — Regulatory Affairs

**Subject:** RUO pharmacogenomic reasoning tool + 21 CFR Part 11 audit trail

Hi {First name},

Quick note. I've built a pharmacogenomic reasoning platform
positioned deliberately as research-use-only today — with
21 CFR Part 11 audit trail metadata (RFC 3161 timestamping,
user/timestamp/system-version/hash on every trial export) built
in from the start.

I'm trying to calibrate the regulatory posture before committing to
a SaMD or IVDR pathway. 20-minute call would help me understand
what a regulatory team at {CRO name} would need from this kind of
tool to be useful vs what would trigger "we can't touch this until
it's FDA-cleared."

Best,
Abhimanyu

---

## Follow-up cadence

Most outbound gets one reply or none. Structured cadence:

- **Day 0:** Send initial template.
- **Day 4:** One-line follow-up — "Bumping this; happy to send a
  5-min Loom if easier than a call."
- **Day 11:** Second follow-up with *different* value — "In case it's
  relevant: {one recent artifact, e.g. PharmCAT concordance report
  once that lands}."
- **Day 25:** Final follow-up — "Last nudge; if no fit I'll stop
  here and reach out again in 6 months when {specific milestone} ships."

Do not follow up a fourth time. Move on.

---

## What to do with every reply (even rejections)

Log it under [`anukriti_docs/founder-research/{person_slug}/`](../founder-research/).
Structure per the folder convention:

```
founder-research/<person_slug>/
├── <person_slug>_<role>_research_notes.md   # distilled takeaways
└── raw_conversation.md                       # verbatim transcript
```

Rejections are as valuable as positive replies — they tell you which
framing isn't working. If 5 CROs reject the same opener for the same
reason, that's a signal to rewrite the template, not push harder.

---

## Metrics to track (simple spreadsheet or markdown table)

| Contact | CRO | Role | Template | Sent | Reply | Call | Pilot | Outcome |
|---|---|---|---|---|---|---|---|---|
| ... | ... | ... | A/B/C/D/E | YYYY-MM-DD | Y/N | Y/N | Y/N | {notes} |

Target for the first 4-week push: **20 sent · ≥5 replies · ≥3 calls ·
≥1 pilot scoped.** Those are realistic cold-outbound numbers; adjust
only if your network produces warm intros.

---

## When to stop outbound and rewrite

- 20 sent, 0 replies → the opener is wrong. Rewrite template A.
- 20 sent, 5 replies, 0 calls booked → the CTA is wrong. Switch from
  "20 min call" to "5-min Loom" or "async Q&A."
- 5 calls, 0 pilots scoped → the pilot offer is wrong or the fit
  isn't there. Review the call notes in `founder-research/` and
  diagnose which signal keeps coming back.

The data lives in `founder-research/`. Mine it honestly.

---

*Templates are starting points, not scripts. Personalize paragraph 1
and paragraph 3 of every email with something specific to the
recipient — a recent paper, trial, or public comment. Generic
personalization ("I've been following your work!") reads worse than
no personalization at all.*
