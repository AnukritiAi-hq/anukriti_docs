# Ramya Krishnan — Research Conversation Notes
Role: Researcher | Microbiology background
Date: May 19, 2026
Platform: (founder-led validation conversation)
Conducted by: Atul Alexander (team member, AnukritiAI)

## Key Insights

### 1. Pharmacogenomic Screening Is Still Not Routine in Indian Trials
The standard Indian pre-trial workflow remains:

1. Preclinical studies
2. In vitro testing
3. Animal studies (toxicity + pharmacokinetics)
4. Phased clinical trials

PGx screening is **not yet a mandatory step** in most Indian trials.
Exceptions: targeted therapies and oncology contexts.

This **directly validates the gap Anukriti is targeting** — genomic
compatibility is not systematically checked before most trials, so a
deterministic, ancestry-aware screening layer is solving a real,
unaddressed problem in the Indian trial pipeline.

### 2. Sequencing-Platform Variability Is Real
VCF reliability depends on the sequencing platform. Per-platform
error profiles cited:

- **Illumina** — short reads, high base accuracy, strong for SNP detection
- **Nanopore** — long reads, useful for repetitive/structural regions, higher raw error rate
- **PacBio** — long reads with good accuracy, more expensive

Implication for Anukriti: downstream interpretation must be
**platform-aware**. A VCF row from Nanopore is not interchangeable
with a VCF row from Illumina at the same locus, and the pgx-core
deterministic engine should eventually surface (or at minimum
document) what the trusted-input contract is per platform.

### 3. Reinforces the Deterministic-Interpretation Thesis
Where sequencing-platform variability exists, **purely generative
interpretation is a liability**. The conversation reinforces the
core Anukriti invariant: medical facts come from deterministic
code pinned to CPIC guidelines; LLMs only narrate.

### 4. Microbiome as a Future Expansion Direction
Ramya — leaning on her microbiology background — was firm that
**gut microbiota can influence drug metabolism in ways genomics
alone won't capture**. Specifically called out:

- Drug activation
- Drug degradation
- Bioavailability
- Toxicity profiles

This is a **non-genomic axis of variability** that sits outside
pgx-core's current scope firewall. Worth tracking as a future
expansion vector — *not* as an immediate roadmap item, because:

- It would breach the closed-enum scope firewall (the platform
  is deliberately pharmacogenomic-only for now).
- The evidence base for microbiome-mediated PK/PD is still
  immature compared to CPIC's pinned PGx tables.
- Stage-1 (public + aggregate genomic data) and Stage-2
  (controlled-access ancestry-rich datasets) priorities should
  land first.

But it's a real future moat: *population-aware + microbiome-aware*
drug safety is a defensible second layer once the first one is
shipped at scale.

### 5. Limitation Acknowledged
Ramya explicitly declined to comment on Indian regulatory
guidelines for genomic compatibility checks pre-trial. That
question stays open and is a candidate for the next outreach
target — likely a regulatory affairs specialist or a CDSCO-
adjacent contact.

## Interpretation for Anukriti

| Platform doc | Update warranted? | Notes |
|---|---|---|
| `anukriti-pgx-core/docs/strategy.md` | **Maybe** | Microbiome-aware PK/PD as a Tier-2/Tier-3 future moat — worth a paragraph in the "what we are NOT yet" section, with this conversation cited. |
| `anukriti-pgx-core/docs/research-partnerships.md` | **No new entry yet** | Microbiome datasets aren't a current partnership target. Revisit if/when the platform decides to expand the scope firewall. |
| `anukriti_docs/IDEA_REFINEMENT_AND_PHASING_2026-05-14.md` | **Maybe** | Could add microbiome as a Phase-D / long-horizon item. Don't promote it above Phase A/B/C work. |
| `anukriti/CLINICAL_GRADE_ROADMAP.md` | **Yes** | "Sequencing-platform variability" is concrete enough to deserve a CP-7-style item: clarify what input platforms the engine trusts, and what guardrails fire when an unknown/heterogeneous source is detected. |

The PGx-screening-not-routine and microbiome-as-future-axis points
are the two most actionable. The platform-variability point is
the most operationally pressing for the immediate roadmap.

## Follow-Up Leads

Open questions surfaced by this conversation:

- **Indian regulatory landscape (CDSCO + ICMR)** — does any
  guideline currently *encourage* (even if not mandate) PGx
  screening for specific drug classes? Need a regulatory affairs
  contact to close this.
- **CRO / sponsor practice** — when targeted-therapy or oncology
  trials *do* use PGx screening in India, what tools and
  guidelines do they actually run? Worth an outreach to a CRO
  bioinformatician or oncology trial coordinator.
- **Microbiome-PGx interaction studies** — is there current
  Indian or South Asian literature on, e.g., gut microbiota
  modulating CYP-metabolized drug PK? Survey before any roadmap
  commitment.

## Linked Platform Context

This conversation feeds into:

- `anukriti_docs/PLATFORM_ANALYSIS_2026-05-11.md` — gap-validation
  evidence for the trial-stratification wedge.
- `anukriti-pgx-core/docs/strategy.md` — corroborates the moat
  thesis (deterministic + ancestry-aware + future microbiome
  layer).
- `anukriti/CLINICAL_GRADE_ROADMAP.md` — sequencing-platform
  variability is a candidate new CP-item for Week 4+ scope.
