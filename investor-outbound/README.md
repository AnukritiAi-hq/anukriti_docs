# Investor Outbound — Anukriti

> **Four artifacts, one execution order.**
>
> Created: 2026-05-12 · Response to the investor-readiness audit.
> Every doc here is grounded in verifiable facts from the three
> repos — if a claim in any of these stops being true, fix the
> claim in the same commit that made it untrue.

---

## What's in this folder

| # | File | Purpose | Audience |
|---|---|---|---|
| 1 | [`BFG_SCRUB_PLAYBOOK.md`](BFG_SCRUB_PLAYBOOK.md) | Rotate credentials + scrub `.env` blobs from git history before any external share | Founder (execute personally) |
| 2 | [`CRO_ONE_PAGER.md`](CRO_ONE_PAGER.md) | Positioning brief for CRO bioinformatics / clinical / regulatory leads | CRO technical evaluators |
| 3 | [`CRO_OUTREACH_TEMPLATES.md`](CRO_OUTREACH_TEMPLATES.md) | Email + LinkedIn templates, tiered by role + follow-up cadence + metrics | Founder (outbound operator) |
| 4 | [`PRE_SEED_PITCH.md`](PRE_SEED_PITCH.md) | Canonical 2-paragraph pitch + shorter variants + Q&A prep | Pre-seed investors, angels, warm-intro replies |

---

## Execution order (this order matters)

### Week 0 — before ANY external outreach

1. **Execute [`BFG_SCRUB_PLAYBOOK.md`](BFG_SCRUB_PLAYBOOK.md) in full.**
   The playbook rotates 5 provider credentials (AWS, Anthropic,
   Google, OpenAI, Pinecone) and scrubs `.env` blobs from the
   `Abm32/Synthatrial` repo history. Until this completes, *do not*:
   - Share the Synthatrial repo URL in any email, deck, or demo
   - Publish or promote the landing page to anyone who'd click through
   - Submit the hackathon with a public repo link
   - Reply to any investor intro with a repo link attached

   This is a 2-3 hour block and it's the single highest-ROI
   security/credibility action available. Do it first.

### Week 1 — set up outbound infrastructure

2. **Host [`CRO_ONE_PAGER.md`](CRO_ONE_PAGER.md)** as a link-able artifact.
   Options: commit to `anukriti_docs` repo (currently public), publish
   as a Notion page, or export to PDF under `anukriti.abhimanyurb.com/cro`.
   Pick one canonical URL; the outreach templates reference it.

3. **Populate paragraph 2 of [`PRE_SEED_PITCH.md`](PRE_SEED_PITCH.md)**
   with current-month milestones. The canonical pitch is a template;
   it should drift quarter-over-quarter with real progress.

4. **Identify 20 target CROs.** Per
   `anukriti_docs/PLATFORM_ANALYSIS_2026-05-11.md §6 action 7`:
   - Tier 1 (large): ICON, IQVIA, Parexel, Syneos, PRA, Covance/LabCorp
   - Tier 2 (mid-market, PGx-adjacent): ~14 others, research by therapeutic
     area (cardiology, oncology, psychiatry all have high PGx overlap)
   - For each: find the named bioinformatics lead + clinical pharmacologist
     via LinkedIn / published papers / conference programs
   - Log the list in `founder-research/cro_targets.md`

### Weeks 2-5 — outbound cadence

5. **Send 5 outbound per week** using
   [`CRO_OUTREACH_TEMPLATES.md`](CRO_OUTREACH_TEMPLATES.md) Template A.
   Customize paragraph 1 + paragraph 3 of each email with something
   specific to the recipient. Generic personalization reads worse
   than none.

6. **Log every reply** — positive or negative — in
   [`../founder-research/`](../founder-research/) under the established
   folder convention. Rejections are as valuable as positive replies
   because they tell you which opener isn't working.

7. **Parallel track: investor conversations.** Use
   [`PRE_SEED_PITCH.md`](PRE_SEED_PITCH.md) canonical 2-paragraph
   version in email intros. Do not book an investor call until
   you can answer *"what's your evidence of pull?"* with at least
   one real CRO conversation logged.

### Weeks 4-8 — close the loop

8. **PharmCAT concordance run** (separate workstream, `CLINICAL_GRADE_ROADMAP.md`
   CP-5). When the report lands, update the CRO one-pager's
   "Honest disclaimers" section to reflect the new data, and send it
   as the Day-11 follow-up artifact in the outreach cadence.

9. **First advisor conversation.** Per `PLATFORM_ANALYSIS §6 action 11` —
   one practicing pharmacist, clinical pharmacologist, or cardiologist.
   Reference them in paragraph 2 of the pre-seed pitch once they
   formally join.

10. **One Tier-2 data partnership application filed.** All of Us
    Researcher Workbench via an academic partner is fastest; see
    `anukriti-pgx-core/docs/research-partnerships.md` for the
    application path.

---

## What "done" looks like in 90 days

| Metric | Current (2026-05-12) | 90-day target |
|---|---|---|
| Credentials rotated + `.env` scrubbed | 0 / 5 providers | 5 / 5, scrub complete |
| CROs contacted | 0 | 20+ |
| CRO replies | 0 | ≥5 |
| CRO calls booked | 0 | ≥3 |
| CRO pilots scoped (no fee, synthetic data) | 0 | ≥1 |
| Advisors signed | 0 | 1 (clinical pharmacologist level) |
| Data-partnership applications filed | 0 | 1 (All of Us via academic partner) |
| PharmCAT concordance report published | Framework only | Published under `docs/validation/` |
| Founder-research entries | 1 (student) | ≥6 (expert-level) |
| Investor conversations | 0 | 3-5 (angels / domain-specific VCs) |

Hit these and the audit moves from *"worth staying close to"* to
*"writing a first check."* Miss these and the answer is still
*"worth staying close to,"* which is fine — that's what pre-seed
conviction-building looks like at this stage.

---

## Operating principles for these artifacts

1. **Every claim is falsifiable in 60 seconds.** A reviewer who
   clicks any link, runs any command, or reads any file cited here
   should be able to verify the claim on the spot.
2. **Pitches drift, pitch principles don't.** The 2-paragraph
   canonical pitch in `PRE_SEED_PITCH.md` has a stable paragraph 1
   (problem + architecture) and a drifting paragraph 2 (current
   proof points + current ask). Update paragraph 2 monthly; leave
   paragraph 1 alone unless the fundamentals change.
3. **Outbound is a measured activity.** Track the metrics table in
   `CRO_OUTREACH_TEMPLATES.md`. If 20 sent produces 0 replies,
   rewrite the template — don't push harder.
4. **Rejection is data.** Every "no" gets logged in
   `founder-research/` with the reason. The reasons compound into
   a clearer wedge faster than any amount of strategic planning.
5. **Hygiene before traction.** The `.env` scrub is not optional.
   A single leaked key referenced in a public demo undoes all
   the credibility the architecture has earned.

---

## Cross-references

- `anukriti_docs/PLATFORM_ANALYSIS_2026-05-11.md` — the honest audit
  these artifacts implement
- `anukriti_docs/founder-research/` — discovery conversation archive
  (where CRO outreach logs land)
- `anukriti-pgx-core/PLATFORM.md` — canonical three-repo map
- `anukriti-pgx-core/docs/strategy.md` — moat and data-tier strategy
- `anukriti-pgx-core/docs/adr/0002-positioning-as-infrastructure.md` —
  the "infrastructure, not AI model" framing decision
- `anukriti/CLINICAL_GRADE_ROADMAP.md` — CP-1..CP-6 tactical plan
  (where PharmCAT concordance lives)

---

*These four artifacts are the mechanical-execution layer under the
strategic analysis in `PLATFORM_ANALYSIS_2026-05-11.md`. The strategy
doc tells you what to do; these docs are how you actually do each
piece. Update both when either drifts.*
