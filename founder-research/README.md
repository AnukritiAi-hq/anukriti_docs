# Founder Research — Customer & Domain Discovery Archive

> Living archive of founder-led idea validation conversations. Each
> subfolder is one person; each person has two files — distilled
> research notes and the raw conversation transcript.

## Why this exists

Early-stage founder research produces two kinds of value:

1. **Insights you act on** — the distilled lessons, patterns, and
   leads that shape product direction. These belong in
   `<person>_research_notes.md`.
2. **Source material you go back to** — the verbatim conversation
   itself, useful for reviewing outreach quality, understanding
   response patterns, extracting future insights, training future
   AI agents / workflows, and preserving nuance. This belongs in
   `raw_conversation.md`.

Saving both keeps the reasoning trail intact. Notes without raw
transcripts lose context; transcripts without notes lose the
*takeaway*. We want both.

## Folder convention

```
founder-research/
├── README.md                       (this file)
└── <person_slug>/
    ├── <person_slug>_<role>_research_notes.md
    └── raw_conversation.md
```

Where:

- `<person_slug>` = lowercase `first_last` (ASCII, no accents).
- `<role>` = short descriptor like `bpharm_student`, `cra`,
  `clinical_pharmacologist`, `pharmacovigilance_lead`, etc.
- The notes file opens with role, date, and platform.
- The raw file preserves timestamps and message boundaries verbatim.

## What gets added here

- Domain expert conversations (clinicians, pharmacologists, CRAs,
  regulators, etc.)
- Scientific-authority and registry-steward conversations
  (CPIC / PharmVar / PharmGKB / data-custodian PIs) — the people
  who shape the *evidence base* Anukriti consumes
- Customer discovery calls (CRO bioinformaticians, healthcare-AI
  platform leads, research-hospital ops)
- Peer / student conversations that surface real-world workflow
  details not in the literature
- Advisor / investor context-building chats with non-obvious takeaways

Not everything needs both files — if a conversation was too short to
distill, the raw file alone is fine. If the insights came from a
group call with no verbatim record, a notes-only entry is fine. The
default is **both**, because you rarely regret keeping the source.

## Linked platform context

Insights from this archive feed into:

- `anukriti_docs/PLATFORM_ANALYSIS_2026-05-11.md` — cross-repo
  strategic read (business posture, gap list)
- `anukriti-pgx-core/docs/strategy.md` — moat + data-tier strategy
- `anukriti-pgx-core/docs/research-partnerships.md` — institutional
  partnership pipeline
- `anukriti/CLINICAL_GRADE_ROADMAP.md` — product tactical execution

When a conversation changes the platform direction, cross-reference
the relevant doc in the notes file so future-you can trace the chain.
