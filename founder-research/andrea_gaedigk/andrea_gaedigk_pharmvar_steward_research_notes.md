# Andrea Gaedigk — Research Conversation Notes
Role: Senior PharmVar Steward | Children's Mercy Kansas City
Date: May 15–16, 2026
Platform: Email (`agaedigk@cmh.edu`)

## Key Insights

### Why this conversation matters

PharmVar is the canonical star-allele nomenclature registry —
the scientific ground truth that `anukriti-pgx-core` is built
against. Of the 24 source files in pgx-core that reference
PharmVar, the heaviest dependency is `calling/base.py` (17
references). Drift from PharmVar is, definitionally, a
correctness regression.

Andrea Gaedigk is one of the senior stewards of PharmVar and a
co-author on the 2025 StarTRAC-CYP2D6 paper that shaped how the
CYP2D6 caller handles allele-specific read phasing. This is the
first formal scientific outreach from Anukriti to a
nomenclature-registry steward.

### How PharmVar engages with implementers today

- **No formal "implementer registry" exists.** PharmVar cannot
  acknowledge third-party tools because it is a free resource and
  tracking would be difficult. They are *exploring options*, but
  not today.
- **Two official integration channels:**
  1. PharmVar account → email notification on each database
     release. <https://www.pharmvar.org>
  2. Programmatic data retrieval via documented API.
     <https://www.pharmvar.org/documentation>
- **Citation matters more than mention.** Andrea's exact words:
  *"citations are measurable while website mentions are rather
  difficult to track."* This is a low-cost, high-trust signal
  Anukriti should land everywhere.
- **User terms & conditions** govern any reuse:
  <https://www.pharmvar.org/terms-and-conditions>

### Independent validation of the South-Asian data gap

Asked who to talk to for South Asian PGx, Andrea responded:

> *"We are rarely receiving submissions from this part of the
> world… There is unfortunately not much info for the Indian
> subcontinent."*

A senior PharmVar steward, with global view of submissions,
confirms the data sparsity Anukriti is built to address. This
is **strategically valuable** as third-party validation of the
moat thesis.

## Important Observations

- PharmVar's lack of a formal implementer registry is *not* a
  rejection — it's a structural reality of being a free
  resource. The right Anukriti pivot is to make our alignment
  audit-able instead of registry-listed: API-driven pull on every
  release, formal citation across all surfaces, divergence audits
  via `scripts/cpic_audit.py`.
- The South-Asian data gap is genuine, not a perception problem.
  Confirmed by the steward at the source layer. Anukriti's
  constraint is structural, not a marketing claim.
- Andrea was responsive within ~90 minutes on the first reply and
  ~90 minutes on the second. Cold outreach to PGx-registry
  stewards is more open-door than expected if the framing is
  technical and specific.

## Recommendations She Gave

Three contacts handed off — all senior authors with
population-specific PGx work, in order of perceived value:

| Contact | Affiliation | Email | Why |
|---|---|---|---|
| **Andrew Somogyi** | University of Adelaide | `andrew.somogyi@adelaide.edu.au` | Andrea framed him as a connector who *"may be able to direct to other people"* — highest expected value |
| **Chonlaphat Sukasem** | Mahidol University, Thailand | `chonlaphat.suk@mahidol.ac.th` | Thai PGx work; adjacent-region for SE Asian admixture |
| **Martin Kennedy** | University of Otago, NZ | `martin.kennedy@otago.ac.nz` | Native New Zealander PGx; methodological reference for under-represented-population work at small-team scale |

Andrea's general principle when no direct match exists:
*"contact the senior authors on papers who have published on the
genes of interest."* — sound advice that generalizes beyond
this conversation.

## Interpretation for Anukriti

### Pivot — alignment claim restructured

Anukriti can no longer say "we are a listed PharmVar implementer"
(none exists). Stronger replacement, achievable today:

> *"Anukriti pulls allele definitions from PharmVar via the
> documented API on every release notification, audits divergences
> via `scripts/cpic_audit.py`, and cites PharmVar publications in
> every academic and product surface."*

That is an active, audit-able discipline — better than a registry
listing.

### Concrete action items

1. **Register a PharmVar account** to receive release notifications.
2. **Wire the PharmVar API into `anukriti-pgx-core`** — likely a
   new module under `anukriti_pgx_core/registries/` that wraps the
   API and feeds `scripts/cpic_audit.py`. This complements the
   existing CPIC audit pipeline.
3. **Citation sweep**: every PharmVar mention across
   `anukriti-pgx-core`, `anukriti-swarm`, `anukriti`, and
   `anukriti_docs` gains a formal publication citation, not just a
   URL. Track via:
   ```bash
   grep -rE "pharmvar\.org|PharmVar" \
     anukriti-pgx-core/ anukriti-swarm/ anukriti/ anukriti_docs/ \
     --include="*.md" --include="*.py" --include="*.toml" \
     --include="*.tex"
   ```
   Canonical PharmVar citations to confirm and use:
   - Gaedigk et al., *Clin Pharmacol Ther*, 2018 — "The Pharmacogene
     Variation (PharmVar) Consortium: Incorporation of the Human
     Cytochrome P450 (CYP) Allele Nomenclature Database"
   - Gaedigk et al., 2021 — PharmVar update paper
   - StarTRAC-CYP2D6, 2025 — Gaedigk et al.
4. **Strategic-quote use** — Andrea's *"not much info for the
   Indian subcontinent"* line is citeable third-party validation
   for the data-gap thesis. Belongs in:
   - `anukriti-pgx-core/docs/strategy.md` Moat section
   - `anukriti_docs/IDEA_REFINEMENT_AND_PHASING_2026-05-14.md`
     sharpened-thesis section
   - Next pre-seed pitch revision in `investor-outbound/`

   **Permission gate:** before quoting verbatim externally, send a
   one-line ask to Andrea:
   > *"Would you be comfortable with me citing your observation
   > that '[quote]' in our strategy/pitch documents, with
   > attribution? Happy to share the framing for review first."*

   Internal docs (this file, IDEA_REFINEMENT) can paraphrase or
   quote freely — they're git-private to the `AnukritiAi-hq` org.

## Follow-Up Leads

In priority order:

1. **Andrew Somogyi** (Adelaide) — connector framing; lead with
   Andrea's referral as social proof
2. **Chonlaphat Sukasem** (Mahidol) — adjacent-region triangulation
3. **Martin Kennedy** (Otago) — methodological reference

Each cold-email should reference Andrea's introduction explicitly
in the opening line.

## Linked platform context

- Updated `IDEA_REFINEMENT_AND_PHASING_2026-05-14.md` Part 8
  (Outreach contact list) — added Status column; new rows for
  Gaedigk, Somogyi, Sukasem, Kennedy
- `anukriti-pgx-core/anukriti_pgx_core/calling/base.py` and 23
  other source files reference PharmVar — these are the touch
  points the API-integration work in action item 2 will plug into
- `anukriti-pgx-core/scripts/cpic_audit.py` (commit `c13fa67`) is
  the analogous audit tool for CPIC; the planned PharmVar audit
  follows the same pattern