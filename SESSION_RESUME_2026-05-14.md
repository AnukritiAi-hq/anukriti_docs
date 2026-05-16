# Session Resume — 2026-05-14 → 2026-05-15

> Pause point captured at 22:14 IST 2026-05-14.
> Resume tomorrow with: "continue from SESSION_RESUME_2026-05-14.md".

This file is the single resume point for the four Phase-A/B tasks I
started executing in the 2026-05-14 session. Two are landed and
verified, two are open. The full strategic plan they execute against
lives in
[`IDEA_REFINEMENT_AND_PHASING_2026-05-14.md`](IDEA_REFINEMENT_AND_PHASING_2026-05-14.md).

---

## ✅ Task 1 — A4: Citation pass on positioning docs (DONE)

Modified 4 docs to anchor every claim in published literature (Martin
2017, Kerdoncuff 2025, Moorjani 2013, Narasimhan 2019, Zack 2026,
Poplin 2018, CPIC 2022). Reference-style markdown footnotes; all
refs match definitions; no code or regression touched.

| File | Change |
|------|--------|
| `anukriti-pgx-core/docs/strategy.md` | +92 lines, 3 inline cites + 7-paper References |
| `anukriti-pgx-core/PLATFORM.md` | +45 lines, 3 inline cites + References |
| `anukriti/README.md` | +30 lines, 2 inline cites + References before License |
| `anukriti-swarm/README.md` | +36 lines, opening claim cited, BCHE/Vysya bullet added, References |

**Verification:** footnote refs match definitions across all four
files; no broken links.

---

## ✅ Task 2 — B6-narrative: BCHE/Vysya ACT in flagship demo (DONE)

Added ACT 4 (Succinylcholine + BCHE L307P + Vysya/Telangana) to
`anukriti-swarm/demos/flagship.py`. Narrative-only, no new pipeline
path. Uses LASI-DAD prevalence stats from Kerdoncuff 2025:

- ~5.3% Vysya in Telangana
- ~0.9% Telangana regional
- 0.28% all-India
- **0% gnomAD** (variant invisible to every existing PGx system)

ACT 4 also surfaces Anukriti's planned **variant-novelty layer**
(Phase B4): the four-state `VARIANT_NOVELTY` machine
(`IN_GNOMAD` / `IN_1000G_ONLY` / `NOVEL_TO_REFERENCE` /
`POPULATION_PRIVATE`), the new `R13 ESCALATE` rule, and the
founder-effect facet `B3` — with an honest "pending B1/B2/B6-full"
note where the architecture isn't there yet.

Updated module docstring, opening banner, and the conclusion's
"THE INSIGHT" bullets (added a 4th bullet for the BCHE wedge).

**Verification:**

- ✓ `flagship.py` runs cleanly with ACT 4 rendered.
- ✓ 244/244 pytest pass (matches session-15 baseline).
- ✓ `showcase` JSON export = 1961 bytes (byte-identical regression
  contract held).
- ✓ `safety_demo` = 1 delivered / 4 blocked / 4/4 adversarial
  matched (byte-identical).
- ✓ `evidence_sufficiency_demo`, `evidence_sufficiency_abstention_demo`,
  `unified_demo` all produce expected signatures.
- `flagship.py` is **not** in the byte-locked 7 (showcase,
  safety_demo, interoperability_demo, evaluation_demo,
  evidence_sufficiency_demo, evidence_sufficiency_abstention_demo,
  unified_demo), so extending it is safe.

---

## ⏳ Task 3 — A2: PharmCAT concordance run end-to-end (NEXT)

**Status:** infrastructure investigated and confirmed ready;
smoke-test invocation interrupted before completion. **Resume with a
single-sample smoke test, then scale to 10 samples.**

### What's already in place (no work needed)

- PharmCAT JAR at
  `anukriti/tools/pharmcat/pharmcat-2.15.4-all.jar`
- Java 21 installed (PharmCAT requires ≥17)
- Docker image `pgkb/pharmcat:latest` already pulled (~4 GB)
- `pyliftover==0.4.1` available in `venv-baseline`
- 1000 Genomes Phase-3 VCFs in `anukriti/data/genomes/` for chr
  1, 2, 6, 10, 11, 12, 16, 19, 22 (covers all priority genes)
- Comprehensive comparison module:
  `anukriti/src/benchmark/pharmcat_comparison.py`
  - `extract_sample_variants()` — pull per-sample PGx variants from
    1000G VCFs
  - `create_grch38_vcf()` — liftover 37→38 + reference-backfill at
    PharmCAT definition positions
  - `run_pharmcat_docker()` — Docker-based PharmCAT runner
  - `parse_pharmcat_phenotypes()` — phenotype JSON parser
  - `run_anukriti_on_variants()` — Anukriti caller wrapper
  - `compare_results()` — concordance comparator
  - `PharmCATComparisonResult.summary_table()` /
    `.generate_latex_table()` / `.to_dict()` — output formatters
- CLI runner:
  `anukriti/scripts/run_pharmcat_comparison.py` (default 5 samples,
  10 GeT-RM samples in `DEFAULT_SAMPLES`, 7 genes in
  `COMPARISON_GENES`).
- GeT-RM truth set in `anukriti/src/benchmark/getrm_truth.py` for
  CYP2C19, CYP2C9, TPMT, DPYD, SLCO1B1.

### Resume steps

1. **Smoke test (1 sample, ~5 minutes expected):**

   ```bash
   cd /home/abhimanyu/Desktop/SynthaTrial-repo/anukriti
   source venv-baseline/bin/activate
   timeout 600 python scripts/run_pharmcat_comparison.py \
       --sample-ids HG00096 \
       --output docs/validation/pharmcat_concordance_smoketest.json \
       2>&1 | tee docs/validation/pharmcat_concordance_smoketest.log
   ```

   Expected output: per-gene Anukriti-vs-PharmCAT concordance for
   HG00096 (EUR). Watch for:
   - PharmCAT image start-up time on first run (can be 2–3 min)
   - Liftover warnings (some rsIDs may fail liftover — non-fatal)
   - Output JSON written to `docs/validation/`
   - **PharmCAT first-invocation overhead** is the most likely
     reason yesterday's smoke test was cancelled.

2. **If smoke test passes, scale to 10 GeT-RM samples:**

   ```bash
   timeout 1800 python scripts/run_pharmcat_comparison.py \
       --samples 10 \
       --output docs/validation/PHARMCAT_CONCORDANCE_v1.json \
       --latex \
       2>&1 | tee docs/validation/PHARMCAT_CONCORDANCE_v1.log
   ```

3. **Write the report.** Create
   `anukriti/docs/validation/PHARMCAT_COMPARISON.md` with:
   - One-paragraph methodology (samples used, genes compared,
     PharmCAT version, Anukriti pgx-core==0.2.1).
   - Summary table (markdown + LaTeX from `--latex`).
   - Per-gene concordance breakdown.
   - Honest discordance discussion (any gene <95% gets a
     paragraph naming the failure mode).
   - Reproducibility command block (the two commands above).
   - Cite Zack 2026 evaluation protocol as the methodological
     framing (the 24-recommendation blinded-eval pattern is
     planned as A3 follow-on).

4. **Wire it into existing surfaces:**
   - `api.py` already references `docs/validation/PHARMCAT_COMPARISON.md`
     (line 1308). Confirm the link resolves after the report lands.
   - `tests/test_expanded_validation.py` already expects
     `pharmcat_comparison_reference: docs/validation/PHARMCAT_COMPARISON.md`.
     Run that test post-write to confirm.
   - Update `anukriti/CLINICAL_GRADE_ROADMAP.md` CP-5 from
     "PARTIAL" → "DONE" with link to the report.
   - Update `anukriti_docs/IDEA_REFINEMENT_AND_PHASING_2026-05-14.md`
     Phase A2 row from open → done.

### Known risks / failure modes to watch

- **PharmCAT no-call on a gene** if liftover misses a definition
  position. Reference-backfill in `create_grch38_vcf()` is supposed
  to mitigate this but isn't 100%. If a gene shows "Unknown/Unknown"
  for many samples, that's the diagnostic.
- **Anukriti calls on genes that are not in `vcf_processor.CYP_GENE_LOCATIONS`
  for the chosen build.** Defaults to GRCh37 — confirm before run.
- **CYP2D6 will likely show low concordance** because Anukriti's
  CYP2D6 caller doesn't handle CNVs (Cyrius wrapper is open work).
  This is expected and should be documented honestly in the report,
  not hidden.
- **Docker daemon must be running** (`docker info` checked yesterday;
  re-confirm tomorrow with `docker info | head -5`).
- **Repo size**: do **not** commit the JAR or VCFs. Both are already
  in `.gitignore` (verify before commit).

### Time estimate

- Smoke test: ~10 min (incl. PharmCAT first-run startup)
- 10-sample run: ~30–60 min
- Report writeup: ~1–2 hours
- Roadmap doc updates: ~30 min

**Total: half a focused session.**

---

## ⏳ Task 4 — A1: `.env` BFG / filter-repo scrub + force-push (BLOCKED)

**Status:** investigated; **paused waiting on credential rotation**.
DO NOT execute history rewrite until rotation is confirmed.

### Confirmed scope

- Only `anukriti/` (Synthatrial) is affected. `anukriti-swarm` and
  `anukriti-pgx-core` are clean.
- Three commits on **2026-03-08** contain `.env`:
  - `4e3b035` — added (2200 B)
  - `7ec8233` — modified (2308 B)
  - `92288df` — deleted (0 B; commit message says "fix credential
    exposure" but git history still holds the contents)
- All three commits are on **4 remote branches** on `origin`:
  `clinical-grade-pgx`, `main`, `solana-anukriti`, `v2`.
- Repo is currently **PRIVATE** on GitHub
  (`Abm32/Synthatrial`, confirmed via `gh` CLI, last push
  2026-05-11). Reduces (but does not eliminate) blast radius —
  collaborators, prior-public-mirror caches, and forks could still
  hold the data.
- Exposed credential types: `OPENAI_API_KEY`, `PINECONE_API_KEY`,
  `GOOGLE_API_KEY`, `ANTHROPIC_API_KEY`, `AWS_ACCESS_KEY_ID`,
  `AWS_SECRET_ACCESS_KEY`.
- Current `.env` on disk has the **same key prefixes** as the
  historical leak — strong indication keys have not yet been
  rotated. **CONFIRM with founder before history rewrite.**
- `.gitignore` (line 1: `.env`) correctly blocks `.env` going
  forward.

### Resume steps (only after key rotation is confirmed)

1. **Pre-flight checks (founder must confirm):**
   - [ ] OpenAI key rotated in OpenAI console
   - [ ] Anthropic key rotated in Anthropic console
   - [ ] Google API key rotated in Google Cloud
   - [ ] Pinecone API key rotated in Pinecone console
   - [ ] AWS access key + secret deactivated in IAM and replaced
     (and any IAM access-key history audited for unexpected use)
   - [ ] Local `.env` updated with new keys
   - [ ] All collaborators notified of upcoming force-push
   - [ ] Latest backup of repo taken

2. **Backup the repo locally before any rewrite:**

   ```bash
   cd /home/abhimanyu/Desktop/SynthaTrial-repo
   cp -a anukriti anukriti.pre-scrub-backup-$(date +%Y%m%d)
   cd anukriti
   git fetch --all
   ```

3. **Run `git filter-repo` to remove `.env` from all history:**

   ```bash
   pip install git-filter-repo  # if not already on PATH
   cd anukriti
   git filter-repo --invert-paths --path .env --force
   # Note: filter-repo removes the origin remote by design.
   git remote add origin https://github.com/Abm32/Synthatrial.git
   ```

4. **Verify scrub:**

   ```bash
   git log --all --oneline -- .env
   # Expected: empty output. If any commits show, scrub failed.
   git rev-list --all | xargs -I{} git show {}:.env 2>/dev/null | head -5
   # Expected: empty. Confirms .env is not retrievable from any commit.
   ```

5. **Force-push all 4 branches:**

   ```bash
   for br in clinical-grade-pgx main solana-anukriti v2; do
     git push origin "$br" --force
   done
   ```

   (If `git filter-repo` reordered branches, re-checkout each one
   first.)

6. **Notify all collaborators to re-clone.** A fresh clone is
   required; existing local clones will have stale history that
   re-introduces the secrets if they push.

7. **Document the incident** in
   `anukriti/docs/regulatory/SECURITY_INCIDENT_2026-03-08.md`:
   timeline, scope, rotation actions taken, revocation
   confirmation. Even on a private repo this is the right
   discipline.

8. **Update CLINICAL_GRADE_ROADMAP.md** CP-6 from "open" → "done"
   with link to the incident doc.

### Why this is destructive

- Force-push rewrites public refs; collaborators with stale clones
  will see their pushes rejected and may accidentally restore the
  bad history if they push without re-cloning.
- `git filter-repo` removes the `origin` remote on completion (by
  design, to force the operator to think before re-pushing). Re-add
  intentionally.
- The other three remotes (`docker`, `feat/pgx_triggers`,
  `feature/slco1b1-statin-module`, `fix/diploid-genotype-dosage`)
  on origin **also need scrub** — confirm whether `.env` ever
  landed on those branches before declaring done. Initial check
  with `git log --all -- .env` showed only the 3 commits; verify
  again after fetch.

---

## Status snapshot at end of session

| Task | State | Estimated remaining work |
|------|-------|--------------------------|
| A4 — Citations | ✅ done | — |
| B6-narrative — BCHE wedge act | ✅ done | — |
| A2 — PharmCAT concordance | ⏳ infra ready, runner exists, **next up** | half a session |
| A1 — `.env` scrub | 🛑 blocked on key rotation | 1 day after rotation |

**Modified files this session:**

- `anukriti-pgx-core/PLATFORM.md`
- `anukriti-pgx-core/docs/strategy.md`
- `anukriti/README.md`
- `anukriti-swarm/README.md`
- `anukriti-swarm/demos/flagship.py`

No commits pushed yet — leaving the founder to choose commit boundaries.

**Quick verification command (re-run tomorrow before resuming):**

```bash
cd /home/abhimanyu/Desktop/SynthaTrial-repo/anukriti-swarm
source venv/bin/activate
python -m pytest --override-ini='addopts=' -q --no-header 2>&1 | tail -3
# Expected: 244 passed
timeout 30 python -m demos.showcase 2>&1 | grep "JSON export"
# Expected: JSON export: 1961 bytes
```

---

## Tomorrow's first action

Run the A2 smoke test:

```bash
cd /home/abhimanyu/Desktop/SynthaTrial-repo/anukriti
source venv-baseline/bin/activate
timeout 600 python scripts/run_pharmcat_comparison.py \
    --sample-ids HG00096 \
    --output docs/validation/pharmcat_concordance_smoketest.json \
    2>&1 | tee docs/validation/pharmcat_concordance_smoketest.log
```

Then proceed per the A2 resume steps above.
