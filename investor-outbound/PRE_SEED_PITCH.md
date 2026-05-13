# Anukriti — Pre-Seed Investor Pitch

> **A short, defensible pitch grounded in verifiable facts from the
> repos.** Every claim in the canonical 2-paragraph pitch can be
> checked against a specific artifact in the platform within 60 seconds.
>
> Version: 2026-05-12 · Use this for intro emails, warm-intro replies,
> angel conversations, and the first line of any deck. For the CRO
> product pitch, see [`CRO_ONE_PAGER.md`](CRO_ONE_PAGER.md).

---

## Guiding principle

A pre-seed investor reads the first two paragraphs. If they don't
see (a) a specific problem, (b) a specific artifact that already
ships, and (c) a specific next unlock — they stop reading. So that's
what the canonical pitch does.

---

## Canonical pitch (2 paragraphs — use this)

Most of what the field calls "AI bias in healthcare" is actually
**data-access bias**. Pharmacogenomic evidence is structurally
Eurocentric, and a bigger model trained on the same evidence just
produces *confident* wrong answers for non-European populations —
14% of South Asians can't activate clopidogrel, a common
post-heart-attack drug, yet it's prescribed at the same rate as in
Europeans. Anukriti is the deterministic, population-aware reasoning
infrastructure that fixes this at the architecture layer, not the
model layer: 18 closed-enum scope firewalls, 31 deterministic
sufficiency rules, provenance required on every evidence edge, and
named refusals with rule IDs when evidence for a specific ancestry
is thin. It's the opposite of a hallucinating healthcare chatbot —
the LLM is gated behind 4 forbidden actions that raise at runtime,
and the reasoning core has a byte-identical regression contract
across 638 tests.

We have the hard part: a PyPI-published library
([`anukriti-pgx-core==0.2.1`](https://pypi.org/project/anukriti-pgx-core/)),
a live product with FHIR R5 + 21 CFR Part 11 audit trails, AWS AI
Competition Finalist placement, a SAMANWAYA'26 conference abstract,
and an Agents Assemble 2026 hackathon submission. The architecture
is genuinely differentiated — it's shaped from day one for
federated, controlled-access genomic data (H3Africa DBAC,
GenomeIndia FeED, All of Us Workbench), which competitors building
"ingest everything" platforms will have to rebuild into months from
now. The next 90 days are about closing the external-validation
loop: a PharmCAT concordance report on GeT-RM + 1000 Genomes, three
documented CRO evaluation pilots, and one clinical advisor signed.
We believe this is the right moment to build in the space as we
continue validating the technical and clinical direction with
domain experts — and as we shape the next phase, having the right
strategic partners and early believers around us would be
meaningfully valuable.

---

## Why every line is defensible

| Claim | Where it's verifiable |
|---|---|
| "14% of South Asians can't activate clopidogrel" | CPIC allele-frequency tables; `anukriti/data/population_frequencies.json` |
| "18 closed-enum scope firewalls" | `anukriti-swarm/core/evidence_sufficiency/` + `interoperability/`; listed in `anukriti_docs/PLATFORM_ANALYSIS_2026-05-11.md §2` |
| "31 deterministic sufficiency rules" | 12 (R1-R12) + 10 (V1-V10) + 9 (U1-U9) = 31; `anukriti-swarm/.anukriti-project-context.md` |
| "Byte-identical regression contract across 638 tests" | 51 pgx-core + 234 swarm + 353 product biomedical = 638 |
| "PyPI-published library" | `pip install anukriti-pgx-core==0.2.1` |
| "FHIR R5 + 21 CFR Part 11 audit trails" | `anukriti/src/audit_trail.py` (commit `2670915`); `anukriti-swarm/hackathon/fhir/` |
| "AWS AI Competition Finalist" | Cited in `anukriti/README.md` + `anukriti/.kiro/steering/product.md` |
| "Agents Assemble 2026 hackathon submission" | `anukriti-swarm/hackathon/` with 25MB rendered demo video |
| "H3Africa / GenomeIndia / All of Us" strategy | `anukriti-pgx-core/docs/research-partnerships.md` |
| "4 forbidden LLM actions raise at runtime" | `GenerativeBoundary` in the narrative layer; commits in swarm session log |

If a reviewer checks any line above and finds it off, the claim is
wrong, not the reviewer — fix the claim, not the doc.

---

## Shorter variants

### One-paragraph version (for LinkedIn messages or DM replies)

Anukriti is a deterministic, population-aware pharmacogenomic
reasoning platform that flags drug-risk for non-European populations
where the evidence is structurally thin — e.g. the 14% of South
Asians who can't activate clopidogrel. The reasoning core is
CPIC-pinned, LLM-free in the safety path, and ships with named
refusals (rule IDs) when evidence is insufficient for a specific
ancestry. Published on PyPI, AWS AI Competition Finalist, Agents
Assemble 2026 hackathon entry. Opening conversations with early
believers as we close the external-validation loop over the next
90 days.

### One-line version (for subject lines or elevator intros)

Deterministic, population-aware pharmacogenomic risk reasoning —
with named refusals when the evidence is thin. PyPI-published,
AWS AI Competition Finalist.

### Technical one-liner (for engineer-angel conversations)

Closed-enum scope firewalls at 18 module boundaries, 31
deterministic sufficiency rules, provenance required on every KG
edge, and `GenerativeBoundary` with 4 forbidden LLM actions that
raise at runtime — shipped as a PyPI library plus a FHIR R5 / 21 CFR
Part 11 product.

---

## The ask (how to frame "support would help")

**Do not say:** "We need funding to keep building."

**Do say (from the canonical pitch, final sentence):**

> *"We believe this is the right moment to build in the space as we
> continue validating the technical and clinical direction with
> domain experts — and as we shape the next phase, having the right
> strategic partners and early believers around us would be
> meaningfully valuable."*

Why this works:

- **"Strategic partners and early believers"** is specific, not needy.
- **"Shape the next phase"** signals you're not asking for survival
  capital; you're asking for conviction capital.
- **"Validating with domain experts"** signals humility about what
  you don't know yet, which is exactly what a pre-seed investor wants
  to hear from a first-time founder in a regulated domain.
- The sentence makes no dollar ask. That's correct at this stage —
  the first conversation is about fit, not check size.

---

## What investors will ask (and how to answer)

### "What's your wedge?"

> CRO pre-trial cohort stratification via our `/trial/export`
> endpoint. FHIR-native, deterministic, population-aware, with
> named refusals on thin evidence. We're targeting 20 CRO
> bioinformatics teams for evaluation pilots in the next 30 days.
> The broader vision — infrastructure for evidence-governed drug
> safety reasoning — is a 3-5 year buildout on top of that beachhead.

### "What's the moat in 2 years?"

> Three things, in priority order: (1) architectural discipline that
> competitors building "ingest everything" platforms will take 6-12
> months to rebuild — closed-enum scope firewall, evidence
> sufficiency gate, provenance chain, byte-identical regression
> contract; (2) controlled-access data relationships compounding
> from day one — H3Africa DBAC, GenomeIndia FeED, All of Us
> Workbench — each is a 3-18 month relationship we start building
> now; (3) a growing corpus of named refusal patterns and
> population-specific bias detectors that encode domain expertise
> as code.

### "What's your evidence of pull?"

> Real but early. AWS AI Competition Finalist, SAMANWAYA'26
> abstract submitted, Agents Assemble 2026 hackathon submission,
> PyPI package published. Not yet: signed CRO pilots, advisors, or
> data-partnership agreements. That's what the next 90 days are
> about. I'm not here to pitch you revenue that doesn't exist yet.

### "What's your regulatory posture?"

> Research-use-only today, with 21 CFR Part 11 audit trail
> infrastructure already shipped. SaMD vs IVDR is a deliberate
> decision I haven't made — both have different product
> implications, and I'd rather pick well than pick fast. I'm talking
> to regulatory counsel as part of the next phase. Architectural
> Decision Record 0002 in the pgx-core repo explicitly rejects the
> "clinical decision support" positioning we'd need to defend
> either pathway today.

### "Who's on the team?"

> One founder visible right now — me. Finding a biomedical
> co-founder with CPIC-committee adjacency is an explicit next
> phase, and I'd rather find the right person than hire around the
> gap. A clinical advisory board is the other near-term add:
> pharmacist + clinical pharmacologist + cardiologist, South-Asian
> patient-base preferred given the wedge story.

### "What's the 18-month plan?"

> Three stages. **Months 1-3:** external validation loop — PharmCAT
> concordance, 3 CRO pilots scoped, 1 clinical advisor, file first
> Tier-2 data-partnership application. **Months 4-9:** first paid
> pilot, first Tier-2 data integration live, pre-seed close (if
> raising), co-founder search live. **Months 10-18:** first
> commercial contracts, regulatory pathway decision, second repo of
> moat (simulation layer or H3Africa integration depending on
> partnership trajectory).

### "What do you need from an early investor right now?"

> Conviction, and three specific things money alone doesn't buy:
> (1) warm intros to CRO bioinformatics leads, (2) one domain
> advisor at the clinical-pharmacologist level, (3) a co-founder
> search network. I'll take capital when the external-validation
> loop closes in 60-90 days; the right investor before that is
> someone who wants to watch the loop close in real time.

---

## What NOT to say

These phrasings show up in early-founder decks and read as red flags
to experienced investors. Avoid all of them:

- ❌ *"We can replace clinical trials."* (No computational approach
  can. Don't overclaim.)
- ❌ *"The TAM is $30B."* (Even if the 2M-ADR, $30B figure is right,
  your addressable market at pre-seed is << 1% of that. Quote the
  wedge market, not the TAM.)
- ❌ *"We're raising $X to hire a team of Y."* (Pre-seed isn't
  formula-driven. Lead with traction, not spend plan.)
- ❌ *"We're the only ones doing this."* (Healthcare AI is crowded.
  Claim architectural discipline instead.)
- ❌ *"AI-first healthcare platform."* (Triggers the commoditizing
  competitive set. Claim "infrastructure," per ADR-0002.)
- ❌ *"Revolutionary," "game-changing," "disruptive."* (These are
  filler; delete on sight.)
- ❌ *"We need support."* (Use the canonical final sentence instead.)

---

## Source documents this pitch draws from

- `anukriti_docs/PLATFORM_ANALYSIS_2026-05-11.md` — the honest
  business + technical read this pitch is built on
- `anukriti-pgx-core/PLATFORM.md` — canonical three-repo map
- `anukriti-pgx-core/docs/strategy.md` — moat and data-tier strategy
- `anukriti-pgx-core/docs/adr/0002-positioning-as-infrastructure.md`
  — the "infrastructure, not AI model" framing decision
- `anukriti-swarm/.anukriti-project-context.md` — session-by-session
  build history with the specific metrics used in the pitch

If any line in this pitch stops being true (e.g. competition status
shifts, test counts change materially), update this file in the
same commit that made the change true. Pitches that drift from the
repos are the fastest path to a credibility loss in diligence.

---

*Sharpen in real conversations. The canonical 2-paragraph pitch is
a starting point, not a script. Paragraph 1 should stay stable;
paragraph 2 should drift with each quarter's real milestones.*
