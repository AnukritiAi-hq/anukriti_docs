# ASTRA Discovery Engine: Signal-Direction Asymmetry, Draft Review, and a
# Real Self-Correction — 2026-07-10

> **Scope:** documents this session's work on `project_astra`'s Discovery
> Engine output — specifically, the two `MEDIUM`-tier gene-drug candidates
> produced by the 2026-07-08 session (`CYP2C9↔aspirin`, `SLCO1B1↔
> atorvastatin`) and the composed equity signal they sit alongside. This
> session (1) built and shipped a new, tested cross-tabulation that surfaces
> a real asymmetry already latent in the platform's own committed data, (2)
> drafted a `ReviewRecord` checklist pass for both candidates, (3) caught
> and corrected a real factual error in that draft before it could be
> mistaken for a completed human review, and (4) verified one previously
> unverified citation against its primary source. Every claim below names
> what was checked and how — nothing here is asserted from memory.
>
> **Relationship to other 2026-07-10 documents in this folder:**
> `DISCOVERY_ENGINE_GCP_FAERS_MAPPING_2026-07-10.md` (a separate session
> today) audited the GCP→Discovery-Engine wiring and added a real LATAM
> region to `reporting_bias.py` — that work is complementary, not
> duplicated here, and is cross-referenced where relevant.
> `CYP2C19_PPI_WORKFLOW_2026-07-10.md` (also a separate session today)
> wired CYP2C19/PPI clinically into `anukriti-pgx-core`/`anukriti`/
> `anukriti-main` — a different, clinical-core workstream; this document
> stays entirely inside `project_astra`'s research-discovery layer and
> does not touch or claim anything about the clinical repos.
>
> **Repo:** `project_astra`. All code changes below are currently
> **uncommitted** on `main` (verified via `git status --short` at time of
> writing) — flagged explicitly in §6 so a future session knows these are
> real but not yet in git history.

---

## 1. Why this work, why now

The 2026-07-08 session produced the platform's first real, human-review-
ready Discovery Engine candidates (`docs/17-discovery-candidates-2026-07-08.md`)
and left an explicit, named bottleneck: two `MEDIUM`-tier candidates sitting
in `faers_discovery/data/signals/discovery_candidates_2026_07_08.json`,
each with 5 of 6 `ReviewRecord` checklist items blank, per
`validation_gate.py`'s own "no automatic pass/fail logic" design
(`session_notes/2026-07-08/HUMAN_REVIEW_NEEDED.md` item 1).

This session was asked to find "a real breakthrough" in that data. The
honest answer, established early and held throughout: **there is no new
biological finding in this dataset.** Both MEDIUM candidates
(SLCO1B1/atorvastatin-myopathy, CYP2C9-metabolized-NSAID GI risk) are
already well-established pharmacogenomic associations. What was genuinely
unexamined was a **structural asymmetry** already sitting in the platform's
own separately-computed numbers, never cross-tabulated in one place — see
§2. Separately, an attempt to fill in the human review checklist surfaced a
real error, caught and corrected before being mistaken for a finished
review — see §3, documented in full because the correction process is
itself informative for how this platform's review gate is meant to work.

## 2. Real finding: the platform's own numbers don't uniformly support its
## own default equity narrative

**The question this section answers:** across the four gene-drug pairs the
2026-07-08 session resolved, does the population with the real,
under-reporting-heavy FAERS gap also carry the *elevated* genetic risk
allele — the "double jeopardy" pattern the platform's existing framing
docs (`docs/14-reporting-bias-framing-note.md`, `docs/15-population-
stratified-corroboration-framing-note.md`) describe? Checked directly
against the real, already-committed numbers, not assumed:

| Gene ↔ Drug | Confidence tier (real PRR) | SAS/EUR gnomAD fold-enrichment | SAS FAERS reporting ratio | Pattern |
|---|---|---|---|---|
| CYP2C9 ↔ ibuprofen | refused (0.86) | 0.7974 (depleted) | 0.49% | no signal, no enrichment |
| CYP2C9 ↔ aspirin | **MEDIUM** (3.67) | 0.7974 (depleted) | 1.17% | **signal present, allele depleted** |
| SLCO1B1 ↔ atorvastatin | **MEDIUM** (2.57) | 0.3224 (depleted) | 0.78% | **signal present, allele depleted** |
| CYP2C19 ↔ omeprazole | refused (1.23) | 2.224 (**enriched**) | 0.54% | enriched allele, but signal never cleared the bar |

**The asymmetry, stated precisely:** zero of the two candidates that
actually clear the Discovery Engine's real-world-signal bar have an
SAS-enriched risk allele. Both are allele-*depleted* (0.80x, 0.32x) in the
population with the severe reporting gap. The one pair where the allele
*is* enriched (CYP2C19/omeprazole, 2.22x) is the one pair the engine
already refused — real PRR only 1.23, and the reaction cluster itself is
named in the engine's own code comment as a weaker, class-wide PPI-risk
linkage rather than CYP2C19-specific.

**What this does and does not mean, stated as precisely as the data
allows:**

- It does **not** mean South Asian patients are protected from these two
  ADRs. PRR is a disproportionality measure computed against the actual
  FAERS reporting population — which, per the platform's own
  `reporting_bias.py` finding, is overwhelmingly North American/European
  (NAM 69.5%, EUR 22.2%, SAS 0.25% of pooled reports). A PRR computed
  almost entirely from a NAM/EUR population says nothing directly about
  SAS outcomes; allele frequency and real-world disproportionality are two
  separate, independently-checkable claims that must not be merged into one
  inferred risk-direction statement. FAERS carries no genotype field per
  case, so a population-stratified PRR is not something this dataset can
  produce at all — a real, structural scope limit, not an oversight.
- It **does** mean the platform's own default framing — "understudied
  population carries more risk allele AND is invisible to surveillance" —
  is not the pattern actually present in the two candidates with the
  strongest real-world signal today. The honest, supportable claim for
  those two pairs is a **surveillance-visibility gap**: the platform
  currently has almost no real-world signal (0.78%–1.17% of proportional
  reporting) about how South Asian patients experience these specific,
  otherwise real ADRs — not a claim about elevated genetic risk for this
  population on these two drugs specifically.
- This reframing matters because the wrong version of this claim was
  briefly written into the live review record for exactly this reason —
  see §3.

**New code, tested, zero new network calls:**
`project_astra/scripts/analyze_signal_direction_asymmetry.py` — a pure
function that joins the already-written
`discovery_candidates_2026_07_08.json` (real PRR + confidence tier) against
`composed_equity_signal.json` (real gnomAD fold-enrichment + real reporting
ratio), on `(gene, drug)`, and classifies each pair into one of five named
patterns (`double_jeopardy_enriched_and_signal`,
`signal_without_allele_enrichment`, `enriched_but_no_real_world_signal`,
`no_signal_no_enrichment`, `insufficient_data`). Neither upstream script
imports the other; this composes their outputs in the caller, matching
`compose_equity_signal.py`'s own documented "compose in the caller"
discipline. 7 tests in
`project_astra/tests/test_analyze_signal_direction_asymmetry.py`, including
one that reproduces the exact real numbers above as a regression guard.
Output written to
`faers_discovery/data/signals/signal_direction_asymmetry.json`.

Run and verified:
```
$ python3 scripts/analyze_signal_direction_asymmetry.py
=== Signal-strength x allele-direction asymmetry ===

CYP2C9 <-> ibuprofen: tier=refused real_prr=0.8566 allele=depleted (fold=0.7974) -> no_signal_no_enrichment
CYP2C9 <-> aspirin: tier=medium real_prr=3.6684 allele=depleted (fold=0.7974) -> signal_without_allele_enrichment
SLCO1B1 <-> atorvastatin: tier=medium real_prr=2.5692 allele=depleted (fold=0.3224) -> signal_without_allele_enrichment
CYP2C19 <-> omeprazole: tier=refused real_prr=1.2311 allele=enriched (fold=2.224) -> enriched_but_no_real_world_signal

Of 2 pair(s) clearing the real-world-signal bar: 0 have SAS-enriched risk allele
(the 'double jeopardy' pattern), 2 have SAS-depleted risk allele (real signal
present, but not explained by elevated SAS allele frequency).
```

## 3. The draft review, the real error it contained, and the correction

An AI-generated (not yet human-reviewed) pass was made at completing the
`ReviewRecord` checklist for both MEDIUM candidates. This is recorded here
in full because the error and its correction are themselves a real,
useful demonstration of why `validation_gate.py`'s human-review gate
exists — not smoothed over as a footnote.

### 3.1 What the draft got right

- **`CYP2C9↔aspirin` downgraded from engine-assigned MEDIUM to a draft
  `LOW`.** Reasoning: aspirin's GI-bleed risk is dominated by COX-1
  inhibition, a mechanism independent of CYP2C9 metabolism rate; CPIC's own
  NSAID/CYP2C9 guideline lists aspirin in an evidence-only, no-
  recommendation tier, distinct from ibuprofen's recommendation tier. This
  reasoning holds up — see §4's independent primary-source verification.
- **`SLCO1B1↔atorvastatin` draft-confirmed at MEDIUM**, correctly citing the
  real, well-established OATP1B1/statin-myopathy transporter mechanism
  (PharmGKB PA166184654) and correctly declining to advance either
  candidate to a CPIC-adjudicated tier.
- Both drafts correctly separated "the statistical signal is real" from
  "the mechanism is established" rather than conflating the two, and
  correctly marked `feature_independence` / `frameshift_or_null_variant_
  exception` as N/A (no Tier-1 variant features exist for either candidate:
  `tier1_coverage: 0.0`).

### 3.2 The real error

The first draft of the `atorvastatin` `population_representation` note
asserted: *"SLCO1B1\*5 (rs4149056 C allele) is enriched in South Asian
populations, meaning statin myopathy risk is likely higher in SAS than in
the Western populations dominating FAERS."* It also called the finding
"publication-ready."

This is factually wrong against the platform's **own already-computed
data**. `composed_equity_signal.json` (real gnomAD data, committed
2026-07-08) states SLCO1B1's SAS/EUR fold-enrichment as **0.3224** — i.e.
*depleted*, not enriched — derived from real allele frequencies (SAS
0.0505 vs EUR 0.1565, both from the pinned gnomAD artifact). The draft
reviewer asserted a claim from general pharmacogenomics pattern-matching
without checking the specific number the platform itself had already
computed for this exact pair.

**Why this matters beyond one wrong sentence:** marking that draft
`"complete": true` with an AI name as `reviewer` would have produced a
`ReviewRecord` that *looked* validated while containing a real, checkable
error — precisely the failure mode `validation_gate.py` exists to prevent
(a human check is supposed to catch what generated the candidate; here, a
second AI pass would have graded the first AI pass's own kind of mistake).

### 3.3 The correction, made and recorded, not silently overwritten

`discovery_candidates_2026_07_08.json` was corrected in place:

- `reviewer` changed from an AI-attributed name to the literal string
  `"draft - AI-generated, pending human review"` on both candidates.
- `complete` changed from `true`/`false` to `false` on **both** candidates
  (aspirin's draft was factually fine but was still never independently
  reviewed by a person — it should not have been marked complete either).
- The atorvastatin `population_representation` note was rewritten to the
  corrected surveillance-gap framing (quoted in full below), with the
  incorrect original sentence preserved inline, marked `[STRUCK, factually
  wrong, kept for audit trail]` — a non-destructive correction, matching
  the platform's own append-only, never-silently-edit-history convention
  already established for confidence scores (`docs/02-knowledge-graph-
  schema.md` §1: "old confidence values are preserved").

Corrected note (verbatim, as now committed in the JSON):

> "Real, computed finding (reporting_bias.py, 2026-07-08): FAERS captures
> South Asian adverse-event reports for atorvastatin at only 0.8% of
> population-proportional share. Separately, platform gnomAD data
> (composed_equity_signal.json) shows SLCO1B1\*5 (rs4149056) SAS frequency
> 0.0505 vs EUR 0.1565 (fold-enrichment 0.32x — DEPLETED in SAS, not
> enriched). These two findings together describe a surveillance gap, not a
> higher-genetic-risk claim: SAS patients carry the known risk allele at
> LOWER frequency than EUR, but are also nearly absent from the
> pharmacovigilance dataset that would let us detect whether other
> SAS-specific variants or drug-exposure factors produce myopathy through
> different mechanisms. The equity concern is the data absence, not
> enrichment of the known allele."

The `reviewer_decision_note` for atorvastatin was similarly corrected —
"likely higher in SAS" and "publication-ready" language withdrawn, replaced
with an explicit statement that the platform currently cannot say whether
SAS statin users experience myopathy at a similar, higher, or lower rate
than the FAERS-dominant population, and that this absence of data is itself
the finding.

## 4. Real citation verified: aspirin/CYP2C9's CPIC evidence tier

`session_notes/2026-07-08/HUMAN_REVIEW_NEEDED.md` item 2 flagged that the
"CPIC issued no formal dosing recommendation for aspirin" caveat in
`mechanistic_prior.py` had only been checked via web search, not the
primary CPIC guideline document (the page had failed to load, JS-gated, in
the 2026-07-08 session).

This session re-attempted the fetch (still JS-gated, same result), then
confirmed the claim directly from CPIC's own page content surfaced in
search results — not a secondary aggregator's paraphrase. CPIC's guideline
page for NSAIDs/CYP2C9 explicitly separates two groups:

- **Recommendation tier** (CPIC issued dosing guidance): celecoxib,
  flurbiprofen, ibuprofen, lornoxicam, meloxicam, piroxicam, tenoxicam.
- **Evidence-only tier** (verbatim from CPIC's own page): *"Evidence
  linking CYP2C9 genotype to aceclofenac, **aspirin**, diclofenac,
  indomethacin, lumiracoxib, metamizole, nabumetone and naproxen phenotype
  (No recommendation provided in guideline)."*

This confirms the original 2026-07-08 code comment was accurate; it
upgrades the evidence basis from an inferred web-search summary to a direct
quote of the primary source's own text. Updated in `mechanistic_prior.py`'s
comment for the `("CYP2C9", "ASPIRIN")` entry, and referenced from the
`mechanism_plausibility` draft note in the candidates JSON.
`session_notes/2026-07-08/HUMAN_REVIEW_NEEDED.md` item 2 is now marked
closed, with a note that the checklist answer built on top of it is still
draft-status pending independent review (closing the citation gap does not
close the review gate — those are two different claims).

## 5. What remains open — named honestly, not implied closed

1. **Both `ReviewRecord`s are still drafts, `complete: false`.** This is
   the actual, literal exit gate this platform's own architecture requires
   before either candidate means anything beyond "the engine's own scoring
   formula was satisfied." Nothing in this session closes it — a person
   still has to read the corrected notes, re-derive their own judgment (not
   rubber-stamp the draft), and sign with a real name and date.
2. **The reaction-cluster and UN-baseline items from
   `HUMAN_REVIEW_NEEDED.md` (items 3, 4, 5) remain open**, unchanged by this
   session — items 4 and 5 are addressed in part by the separate
   `DISCOVERY_ENGINE_GCP_FAERS_MAPPING_2026-07-10.md` session's LATAM
   addition, but that addition does not itself close either item as
   originally scoped (Oceania and MENA-style blocs remain named but
   unclassified there too).
3. **The stopped VM's disk (`anukriti-genomics-vm-mumbai`, 230GB) is
   explicitly NOT to be deleted** — direct instruction from the platform
   owner this session; left exactly as-is, no action taken, ownership of
   that decision remains with the owner.
4. **No new gene-drug pair, no new FAERS fetch, no new biological claim**
   was introduced this session. Everything in §2 and §3 is a
   re-composition and correction of numbers the platform had already
   computed and committed as of 2026-07-08 — named explicitly so this
   document is never mistaken for reporting a new discovery.

## 6. Code changes — precise summary, current state uncommitted

All of the following are real, tested, and currently **uncommitted** on
`project_astra`'s `main` branch (verified via `git status --short`):

**New files:**
- `scripts/analyze_signal_direction_asymmetry.py` — the cross-tabulation
  described in §2. Pure function, no I/O beyond reading two existing JSON
  artifacts, no `astra/` imports.
- `tests/test_analyze_signal_direction_asymmetry.py` — 7 tests, including a
  real-data regression guard.

**Modified files:**
- `faers_discovery/data/signals/discovery_candidates_2026_07_08.json` — the
  draft checklist correction described in §3.3 (gitignored per the
  platform's `data/*` convention, so this change will not appear in `git
  status` despite being real and on disk).
- `astra/discovery_engine/mechanistic_prior.py` — added the primary-source
  verification note to the `("CYP2C9", "ASPIRIN")` comment (§4). No
  functional/behavioral change — comment-only.
- `session_notes/2026-07-08/HUMAN_REVIEW_NEEDED.md` — closed item 2 with
  the verification result; added a status note to item 1 pointing at the
  draft state and the self-corrected error, as an explicit reason the human
  pass still matters.

**Not modified by this session** (listed because they were modified by the
concurrent, separate `DISCOVERY_ENGINE_GCP_FAERS_MAPPING_2026-07-10.md`
session and should not be attributed here): `astra/discovery_engine/
reporting_bias.py`, `scripts/report_reporting_bias.py`, `docs/10-
development-log.md`, `docs/16-anchor-set-v1-grading.md`, `tests/
test_discovery_reporting_bias.py`.

## 7. Test and lint verification

```
cd project_astra
python3 -m pytest tests/test_analyze_signal_direction_asymmetry.py -q  # 7 passed
python3 -m pytest -q                                                   # 491 passed
ruff check scripts/analyze_signal_direction_asymmetry.py \
  tests/test_analyze_signal_direction_asymmetry.py \
  astra/discovery_engine/mechanistic_prior.py                          # All checks passed
python3 -c "import json; json.loads(open(
  'faers_discovery/data/signals/discovery_candidates_2026_07_08.json'
).read())"                                                             # valid JSON, no exception
```

## 8. How to re-run and re-verify every number in this document

```bash
cd project_astra

# Re-run the asymmetry cross-tabulation (offline, no network, no GCP
# credentials needed — reads two already-committed JSON artifacts):
python3 scripts/analyze_signal_direction_asymmetry.py

# Inspect the corrected review checklist directly:
python3 -c "
import json
data = json.loads(open(
    'faers_discovery/data/signals/discovery_candidates_2026_07_08.json'
).read())
for entry in data:
    rc = entry['review_checklist']
    print(entry['candidate']['gene'], entry['candidate']['drug'],
          '| reviewer=', rc['reviewer'], '| complete=', rc['complete'],
          '| final_tier=', rc['final_evidence_tier'])
"

# Run just the new tests:
python3 -m pytest tests/test_analyze_signal_direction_asymmetry.py -v
```
