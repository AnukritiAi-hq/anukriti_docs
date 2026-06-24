# CYP2C9 Classifier — Study Notes & Clean Stop (2026-06-23)

> **What this file is:** a plain-language record of the CYP2C9 model-training
> work, written so anyone — even a complete beginner — can understand what we
> tried, what happened, and what to do next. Captured at the end of the day on
> **2026-06-23**. Resume with: *"continue CYP2C9 — do the tomorrow-morning list."*
>
> **Status tonight:** CLEAN STOP. Nothing pushed. Nothing made public.
> 3 commits sit on the local branch, waiting for review tomorrow.

---

## Part 1 — Explain it like I'm six

Imagine a gene called **CYP2C9**. A gene is like a tiny instruction card inside
your body. This particular card tells your body how to break down certain
medicines (like the blood-thinner warfarin). Some people have a **typo** in
their card. A typo can make the card work:

- **normally** (no problem),
- a little **slower** (we call this *decreased function*), or
- **not at all** (we call this *no function*).

If a doctor knows which kind of typo you have, they can pick the right medicine
dose. So we wanted to build a **guessing machine** (a "classifier" — a kind of
computer model) that looks at a typo and guesses: *normal, slower, or not at all?*

We tried twice. Here is the simple story of both tries.

### Try #1 (we call it "v1") — the machine cheated by accident

We gave the machine some lab measurements (called **MAVE scores** — numbers from
a lab experiment) and asked it to guess the answer.

The problem: **we made the answers OUT OF the same lab numbers we gave it.**
That's like giving a kid a math test where the answer is secretly written on the
back of the question. Of course they get 100%! The machine scored almost perfect
(99.8% right) — but only because it was reading its own cheat-sheet. This is
called **circularity**. A perfect score that means nothing.

We proved it was cheating: when we **hid** the cheat-sheet for 4 known answers
("leave-anchors-out"), the machine got all 4 **wrong**. So v1 is not a real
predictor. We wrote that down honestly.

### Try #2 (we call it "v2") — we took the cheat-sheet away

This time we **removed** the lab numbers the machine was secretly using, and
instead gave it an **independent clue** called **AlphaMissense** (a separate tool
that scores how damaging a typo probably is, based on protein shape — it does not
peek at our answers).

Two things happened:

1. **The cheating stopped.** The score dropped from a fake 99.8% to a believable
   **88%**. That drop is GOOD — it means the score is now honest.

2. **But the machine still failed the real test.** When we tested it on 6 typos
   where doctors already KNOW the true answer (the "clinical" test), it got only
   **1 out of 6 right (17%)**. That's basically guessing.

### Why did it still fail? (the big lesson)

Here's the key idea, and it's the whole point of this work:

> **The lab numbers (MAVE) and what doctors actually see (CPIC clinical) do NOT
> agree for CYP2C9.**

The lab says one thing; real patients show another. So even with a perfect,
honest machine and a great independent clue, you **cannot** learn the right
answer if the answers you trained on were the *wrong kind of answer* to begin
with.

It's like trying to learn which fruits are sweet by tasting plastic fruit. No
matter how smart you are, plastic apples won't teach you about real apples. The
problem isn't your tongue (the features) or your brain (the model) — it's that
you were given **plastic fruit (the wrong labels)**.

**The bottleneck is the LABEL DEFINITION — not the features, not the model.**

And there's a silver lining worth remembering: the independent clue
(AlphaMissense) actually **does** separate the classes nicely *where we have it*
(see the table in Part 3). The clue is good. We just can't use it on enough of
the typos, and the answers we trained against were the wrong kind.

---

## Part 2 — The honest one-paragraph conclusion (for the paper)

> CYP2C9 MAVE-derived labels do not generalize to CPIC clinical phenotype. After
> removing circular features (the MAVE CLICK/VAMP scores the labels were
> thresholded from), cross-validation AUC drops from v1's hollow 0.998 to a
> believable ~0.88, but held-out clinical accuracy is **1/6 (17%)**. The
> functional-assay (MAVE) scores diverge from clinical phenotype at the testable
> CPIC anchors. This demonstrates that MAVE data alone is insufficient for
> CYP2C9 pharmacogenomic classification and motivates clinically-labeled
> training data. AlphaMissense is discriminative where available; the blocker is
> coverage (SNV-only) and, more fundamentally, label definition.

---

## Part 3 — The actual numbers (verified against the result files)

### v1 — MAVE-trained scaffold (circular). `cv_metrics_cyp2c9_v1.json`
- Training rows: **8,050** (normal 4,244 · decreased 2,108 · no_function 1,698).
- Features (circular): `click_score, vamp_score, click_sd, vamp_sd, aa_position,
  cyp2c9_domain, has_both`.
- 5-fold CV: rf acc **0.998**, xgb 0.996, lgbm 0.994 — **HOLLOW** (reproduces its
  own labels).
- CPIC anchor validation: **4/4 correct** (\*2, \*3, \*6, \*11) — but only via the
  **500× upweight**. Leave-anchors-out → all 4 WRONG (memorized, not learned).

### v2 — non-circular, AlphaMissense-featured (honest negative). `cv_metrics_v2.json`
- Removed `click_score` + `vamp_score`. New feature set: `am_genomic_score,
  cadd_phred, click_sd, vamp_sd, aa_position, cyp2c9_domain, has_both`.
- AlphaMissense coverage on the MAVE library: **31.3%** (structural limit — 67.5%
  of MAVE variants are multi-nucleotide AA changes that AlphaMissense cannot score
  by design). The >85% coverage gate **cannot be met by any query method**.
- Trained on the SNV-reachable subset: **2,514 rows** (after clinical holdout
  removed; normal 1,551 · decreased 617 · no_function 346).

**Table A — 5-fold CV on the SNV subset (non-circular):**

| model | acc | F1 no_function | F1 decreased | F1 normal | AUC (macro OvR) |
|-------|-----|----------------|--------------|-----------|-----------------|
| rf    | 0.734 | 0.666 | 0.522 | 0.839 | 0.870 |
| xgb   | 0.755 | 0.715 | 0.551 | 0.849 | 0.886 |
| lgbm  | 0.750 | 0.697 | 0.545 | 0.847 | 0.882 |

> Note: the XGB accuracy was quoted as 0.717 in conversation; the recorded file
> value is **0.755**. Use the file value (0.755) — it is the source of truth.

**Table B — held-out clinical alleles vs CPIC truth: 1/6 = 17% (HONEST NEGATIVE):**

| allele | hgvs_pro | CPIC truth | predicted | tier | correct? |
|--------|----------|------------|-----------|------|----------|
| \*2  | p.Arg144Cys | decreased | normal | MEDIUM | ❌ |
| \*6  | p.Arg150His | no_function | normal | HIGH | ❌ |
| \*28 | p.Ile331Val | decreased | normal | HIGH | ❌ |
| **\*11** | **p.Arg335Trp** | **decreased** | **decreased** | **LOW** | **✅ (the one correct call)** |
| \*3  | p.Ile359Leu | no_function | normal | MEDIUM | ❌ |
| \*14 | p.Pro489Ser | decreased | no_function | HIGH | ❌ |

> ⚠️ **Correction to remember:** the single correct allele is **\*11**, NOT \*28.
> An earlier conversational restatement mixed these up (it marked \*28 correct and
> \*11 "unclear"). The result file is clear: **\*11 ✅, \*28 ❌.** Fix this in
> `V2_STATUS.md` tomorrow.

**AlphaMissense class separation (genomic-coordinate-corrected),
`am_class_separation_genomic.csv` — the silver lining:**

| class | n | mean AM | median AM |
|-------|---|---------|-----------|
| no_function | 349 | 0.648 | 0.712 |
| decreased_function | 619 | 0.438 | 0.408 |
| normal_function | 1,552 | 0.213 | 0.149 |

Monotonic 0.21 → 0.44 → 0.65. **AlphaMissense IS discriminative where present —
coverage is the only blocker, not feature quality.**

---

## Part 4 — Exactly where the code/state is tonight (verified)

- **Repo:** `anukriti` (`github.com/Abm32/Synthatrial.git`)
- **Branch:** `clinical-grade-pgx`
- **Position:** `ahead 3` of `origin/clinical-grade-pgx`. **NOT pushed.** No remote
  branch contains HEAD.
- **Commit chain (full SHAs — verified):**
  - `75d3a6304cdf5c7e3f292f3a7aab5362c20747dc` — v1 (MAVE-trained, CLICK-primary)
  - `23b5d9530139f67f1a384ebb5fde3f5d4da77062` — v2 attempt via protein-HGVS (72.6% sentinel → STOP)
  - `61a0dd6119644e075146451f382207a54e73060a` — **v2 genomic AM + SNV-subset experiment (HEAD)**
- **Correction:** HEAD was quoted as `61a0dd5` in conversation. The real SHA is
  **`61a0dd6`**. Use `61a0dd6`.
- **Untracked file (not in any commit):**
  `ml/dpyd-classifier/results/scaria_variant_rankings_v5exp_raw.csv` — decide
  tomorrow whether it belongs in a DPYD commit.
- **Files that exist and are ready (for tomorrow's HF push, AFTER review):**
  `ml/cyp2c9-classifier/models/{rf,xgb,lgbm}_cyp2c9_v1_model.pkl` +
  `..._v2_model.pkl` (6 files), `results/am_class_separation_genomic.csv`,
  `data/cyp2c9_clinical_holdout.csv`, `V2_STATUS.md`, `src/enrich_am_genomic.py`,
  `src/enrich_vep_cyp2c9.py`.

### Security note (read before any HF push)
- `HF_TOKEN` is **not set** in the environment; a cached token file exists at
  `~/.cache/huggingface/token`.
- The 2026-06-18 session flagged the prior HF token `hf_…GByTJ` as **leaked in
  plaintext — rotate, HIGH priority.** Do **not** push with the old token. Rotate
  first (see tomorrow's step 5).

---

## Part 5 — Tomorrow morning, in order (DO NOT skip the order)

Nothing here was done tonight. This is the to-do list for next session.

1. **Fix `V2_STATUS.md`:**
   - Mark **\*11** as the one correct held-out call (NOT \*28).
   - Fix the commit SHA to **`61a0dd6`** wherever it's referenced.
2. **Decide on the untracked DPYD file**
   `ml/dpyd-classifier/results/scaria_variant_rankings_v5exp_raw.csv` — stage into
   a DPYD commit if it belongs, otherwise remove/ignore it. Don't leave it dangling.
3. **Fix the HF README citation** — change the Zenodo line to say it is a
   **project-level artifact** (`10.5281/zenodo.20727790` is the **CYP2D6
   long-read** deposit, not a CYP2C9-specific record). Do not imply it is "this
   model's record."
4. **Draft validation-paper §2.9** — "CYP2C9 MAVE ↔ CPIC divergence": the table of
   4 testable anchors + the conclusion that label definition (not features) is the
   bottleneck.
5. **Rotate the HF token FIRST** — at huggingface.co/settings/tokens: revoke the
   old leaked token, generate a new one, `export HF_TOKEN=...`. Confirm it works
   before any upload.
6. **Only after steps 1–5:** `git push origin clinical-grade-pgx` (the 3 commits)
   **and** create + push the HF repo `abhimanyu12/cyp2c9-classifier` (v1 + v2
   models + honest README). Report the HF repo URL when done.

> Gate: **no `git push` and no HuggingFace push until steps 1–5 are complete and
> reviewed.** Tonight is a clean stop.

---

## Part 6 — One-line summary to carry forward

> CYP2C9 v2 fixed the circularity (AUC 0.998 → 0.88) but still fails clinically
> (17%) because **MAVE labels ≠ CPIC clinical phenotype**. The fix is not more
> features — it is **clinically-labeled training data**. AlphaMissense is a good
> independent signal but is SNV-only (31.3% coverage). Clean stop 2026-06-23;
> push + HuggingFace deferred to tomorrow after token rotation and doc fixes.
