# Anukriti — Pre-Trial Pharmacogenomic Risk Stratification for CROs

> **One-page positioning brief for CRO bioinformatics, clinical operations,
> and pharmacovigilance leads.**
>
> Version: 2026-05-12 · Audience: CRO technical leads evaluating
> population-aware PGx tooling for trial stratification · Contact:
> [abhimanyu@anukriti.ai](mailto:abhimanyu@anukriti.ai) ·
> Live demo: [anukriti.abhimanyurb.com](https://anukriti.abhimanyurb.com)

---

## What we do, in one sentence

Deterministic, CPIC-pinned, population-aware pharmacogenomic reasoning
that flags which genotype groups in a proposed trial population are at
elevated adverse-event risk — **with named refusals when the evidence
for a specific ancestry is thin.**

## The problem we solve for CROs

CPIC guidelines are authoritative but calibrated against predominantly
European-ancestry cohorts. When a trial enrolls across ancestries, the
same dosing logic produces systematically under-warned risk for
populations with different allele frequencies — e.g. **14% of South
Asians are CYP2C19 poor metabolizers** who can't activate clopidogrel,
roughly 7× the European rate. Current trial stratification tooling
either ignores this or applies Eurocentric defaults with confidence.

Anukriti makes the stratification step **auditable, population-aware,
and honest about what it doesn't know.**

## What you get

- **`/trial/export` endpoint** — deterministic cohort rows with
  genotype, inferred phenotype, CPIC-pinned recommendation, and an
  explicit `evidence_sufficiency` verdict (`sufficient` / `downgrade` /
  `escalate` / `abstain` / `block`) per subject.
- **FHIR R5 output** — `DetectedIssue` + `ClinicalImpression` +
  `Provenance` resources, not a custom JSON schema to integrate against.
- **21 CFR Part 11 audit trail** — RFC 3161 timestamping,
  append-only audit log, user/timestamp/system-version/hash metadata
  on every export.
- **Byte-identical regression contract** — CPIC table updates are
  versioned, deliberate events. No silent biomedical drift between
  runs of the same dataset.
- **Named refusals with rule IDs** — when evidence for a specific
  ancestry is insufficient, the system abstains and names the rule
  (R1–R12, V1–V10, U1–U9, or one of 3 population bias patterns).
  Your regulatory team sees exactly why a subject wasn't classified.

## Why this is defensible (not a wrapper around an LLM)

The reasoning core is deterministic — **no LLM in the safety path.**
The architecture enforces scope at the type boundary:

- **18 closed-enum scope firewalls** across modules — drift into
  "generic healthcare assistant" territory requires a visible code
  change, never runtime config
- **31 deterministic sufficiency rules** (12-rule decision engine +
  10-rule set-level verifier + 9-rule uncertainty scorer)
- **Pharmacogenomic knowledge graph** with provenance required on
  every edge — every claim traces back to a specific CPIC rule and
  source
- **4 verification engines** — shape, existence, truth, chain — gate
  every output

The LLM layer exists only for *narrative synthesis* of already-verified
outputs, behind a `GenerativeBoundary` where 4 specific LLM actions
(`infer_phenotype`, `override_recommendation`, `bypass_verification`,
`fabricate_claim`) raise at runtime rather than log.

## Proof points we can show you today

| Artifact | State |
|---|---|
| Live demo | [anukriti.abhimanyurb.com](https://anukriti.abhimanyurb.com) |
| Published library | [PyPI: `anukriti-pgx-core==0.2.1`](https://pypi.org/project/anukriti-pgx-core/) |
| Test coverage | 51 pgx-core tests · 234 swarm tests · 353 product biomedical tests |
| Runtime (deterministic path) | < 2 ms end-to-end |
| Runtime (full FHIR path) | < 30 ms end-to-end |
| Gene panel | 13 genes, 11 star-allele + 2 single-rsID |
| Populations | AFR / AMR / EAS / EUR / SAS — 325 allele-frequency records across all 13 genes (gnomAD v4.0) |
| Guideline pinning | CPIC 2022 + 2019, 29 provenance manifest entries |
| External validation | AWS AI Competition Finalist · SAMANWAYA'26 conference abstract submitted · Agents Assemble 2026 hackathon submission |

## What we do NOT claim

- We do **not** replace clinical trials — this is pre-trial risk
  reasoning, not a trial substitute.
- We are **not** a clinical decision-support system. Outputs are
  research artifacts; clinicians make clinical decisions.
- We do **not** own the datasets. We respect controlled-access tiers
  (H3Africa DBAC, GenomeIndia FeED, All of Us Workbench) and the
  architecture is built for federated evaluation inside those
  environments.
- We do **not** predict outcomes for sub-populations with no data.
  When evidence is thin, the system names the bias pattern
  (`EUROCENTRIC_IMBALANCE`, `ANCESTRY_SCARCITY`,
  `UNSUPPORTED_EXTRAPOLATION`) and abstains.

This is the posture a CRO regulatory team wants from a tool touching
trial stratification.

## Current stage and engagement model

Anukriti is a deliberate, small founding-engineering-stage project.
We're opening conversations with 5–10 CRO bioinformatics teams for
**structured evaluation pilots** — no fee, no commitment. You give us
a de-identified or synthetic cohort shape; we produce a stratification
report + the sufficiency trace; you tell us what would need to change
for it to be useful inside your trial-ops workflow.

What we're specifically looking to learn:

1. Which fields in `/trial/export` map to your existing
   stratification schema, and what's missing
2. Which ancestries in your typical enrollment mix produce the most
   `ABSTAIN` or `ESCALATE` signals, and whether that matches your
   regulatory team's existing concerns
3. What the integration path looks like for your FHIR-native systems
   (or what custom format we'd need)

No data leaves your environment in the pilot; we run against a shape
specification you provide.

## Honest disclaimers

- **PharmCAT end-to-end concordance report not yet published.**
  Integration framework is shipped (`src/pharmcat_integration.py`);
  end-to-end run on GeT-RM + 1000 Genomes samples is in-flight.
  Target: ≥95% concordance on common alleles. We'll share the full
  table when it lands; we're happy to run it against sample IDs you
  specify.
- **CYP2D6 CNV calling is heuristic-only today.** Cyrius wrapper is
  on the roadmap. If your trials depend on *5 deletion or xN
  duplication calling, we'll say so upfront.
- **Research-use-only today.** SaMD / IVDR pathway is a deliberate
  decision we haven't made yet; the RUO disclaimer is correct for
  current scope.

## What happens next

1. **Reply to this email** with a 20-minute intro slot.
2. We walk through the live demo against a population shape similar
   to your trial mix.
3. If the fit is real, we scope a two-week evaluation pilot on
   synthetic or de-identified data.

Typical time from first email to useful pilot output: 3–4 weeks.

---

*This one-pager is a living document. If anything above doesn't match
what you see in the demo or the repos, that's a bug — tell us and
we'll fix the claim, not the doc.*
