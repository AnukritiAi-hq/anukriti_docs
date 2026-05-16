# Session Resume — 2026-05-16

> Pause point captured at end of 2026-05-16 09:00 IST session.
> Successor to `SESSION_RESUME_2026-05-14.md` (now in git history).
> Resume tomorrow with: "continue from SESSION_RESUME_2026-05-16.md".

This file is the single resume point for the four Phase-A/B tasks
tracked in `IDEA_REFINEMENT_AND_PHASING_2026-05-14.md`. Two are
**now landed and pushed**, one is **in progress at session end**, one
is still **blocked on credential rotation**.

---

## What landed this session (all pushed)

8 commits across 4 repos. All flagship demos byte-identical to the
session-15 baseline. `pytest -q` = 244/244 on `anukriti-swarm`.

| Repo | HEAD | Commits added |
|------|------|---------------|
| `anukriti` (`clinical-grade-pgx`) | `a7e43dd` | A4 README citations + .gitignore JAR protection; PharmCAT Docker timeout fix |
| `anukriti-pgx-core` (`main`) | `c13fa67` | A4 PLATFORM.md + strategy.md citations; `scripts/cpic_audit.py` |
| `anukriti-swarm` (`main`) | `89a5c7e` | A4 README citations + `.dockerignore`; B6 flagship BCHE ACT 4; `hackathon/` scaffolding |
| `anukriti_docs` (`main`) | `168e1fc` | `IDEA_REFINEMENT_AND_PHASING_2026-05-14.md` + `SESSION_RESUME_2026-05-14.md` |

### Commit detail

**anukriti** (2 commits):
- `6b9d85f` docs(README): cite Martin 2017 + CPIC 2022 + Kerdoncuff 2025; gitignore JAR binaries
- `a7e43dd` fix(benchmark): bump PharmCAT Docker timeout 120s → 300s for cold-start

**anukriti-pgx-core** (2 commits):
- `7e55964` docs: anchor positioning claims in Martin 2017, CPIC 2022, Kerdoncuff 2025
- `c13fa67` feat(scripts): add cpic_audit.py — passive diff helper for CPIC provenance audits

**anukriti-swarm** (3 commits):
- `6d7577b` docs(README): cite CPIC 2022 + Martin 2017 + Kerdoncuff 2025; ignore hackathon/ in image
- `74c866c` feat(demos/flagship): add ACT 4 — BCHE L307P / succinylcholine / Vysya wedge
- `89a5c7e` feat(hackathon): commit BYO-agent skill docs + Remotion video source

**anukriti_docs** (1 commit):
- `168e1fc` docs: add 2026-05-14 idea refinement + session resume

### Triage decisions, for the record

- `anukriti/tools/pharmcat/pharmcat-2.15.4-all.jar` — **kept on disk, blocked from git** by new `.gitignore` rules (`tools/pharmcat/*.jar`, `tools/**/*.jar`, `*.jar`). The 31MB binary regenerates from PharmCAT releases per the validation runner.
- `anukriti-swarm/hackathon/byo_agents/` — committed as real BYO-agent deployment configuration for the Prompt Opinion + MCP submission flow.
- `anukriti-swarm/hackathon/video/` — Remotion source committed; binary media (`public/audio/`, `public/clips/`, `public/voiceover/`, ~9MB of `.mp3`/`.mp4`) excluded via new `.gitignore` rules. They regenerate from `scripts/generate-voiceover.mjs` + screen-record source clips.
- `anukriti-swarm/hackathon/sharp,fhir,mcp_server,tests` — only `.pyc` cache remains; covered by existing `__pycache__/` rule. No-op.
- `anukriti-pgx-core/scripts/cpic_audit.py` — committed (passive diff helper, 401 LOC, --help works, design-invariants documented).

---

## ✅ Task 1 — A4: Citation pass on positioning docs (DONE + PUSHED)

Was DONE-not-pushed in the 05-14 session. Now pushed across all 3 repos
(anukriti README, anukriti-pgx-core PLATFORM.md + docs/strategy.md,
anukriti-swarm README). All citations use reference-style markdown
footnotes; refs match definitions; no broken links.

---

## ✅ Task 2 — B6-narrative: BCHE/Vysya ACT 4 in flagship demo (DONE + PUSHED)

Was DONE-not-pushed in the 05-14 session. Now pushed.

Verified at session end:
- 244/244 pytest pass.
- showcase JSON export = 1961 bytes (byte-identical regression contract held).
- safety_demo = 1 delivered / 4 blocked / 4/4 adversarial matched.
- interoperability_demo = 24 envelopes / 24 provenance / 6 scope-rejected.
- evaluation_demo = 54/61 suite · 4/4 stress · 3/3 ancestry.
- evidence_sufficiency_demo + abstention_demo: expected signatures.
- unified_demo = 41 RuntimeEvents.
- flagship.py renders ACT 4 with all required strings (BCHE, Vysya,
  Telangana, succinylcholine, 0.28%, 5.3%, gnomAD/blind).

`flagship.py` is **not** in the byte-locked 7, so extending it is safe.

---

## ⏳ Task 3 — A2: PharmCAT concordance run (IN-PROGRESS at session end; bug fixed)

**Status:** smoke test for sample `HG00096` was kicked off twice in
this session. Two findings:

### Finding 1 — PharmCAT Docker subprocess timeout was 120s (FIXED)

Smoke test v1 surfaced a real bug: `run_pharmcat_docker()` in
`src/benchmark/pharmcat_comparison.py` had `timeout=120`. On the very
first invocation Docker extracts a ~4GB image and PharmCAT warms up a
JVM, easily exceeding 120s on a single-core extraction. v1 produced:

```
ERROR: PharmCAT timed out after 120 seconds
WARNING: PharmCAT returned no results
Result: 0/6 concordant
```

The `0/6 concordant` was an artefact of PharmCAT never producing
output, not a real disagreement — Anukriti's caller side worked fine
(CYP2C19 *2/*4 PM, etc.).

**Fix landed in commit `a7e43dd` on `clinical-grade-pgx` (pushed):**
`timeout=300`, with comment explaining the cold-start pattern, and
matching update to the failure-message string.

### Finding 2 — outer wall-clock budget hit during variant extraction (SUBSTANTIVE)

Smoke test v2 (with the Docker timeout fix) kicked off at ~09:48 IST,
hit the outer `timeout 600` wall clock at ~09:58, and was killed mid-
extraction of UGT1A1 variants from `ALL.chr2.phase3_*.vcf.gz`
(a 1.2GB VCF). UGT1A1 extraction had not completed when the budget
expired. **No PharmCAT comparison produced.**

The previous JSON at
`docs/validation/pharmcat_concordance_smoketest.json` (timestamp
09:37) is from v1 and is stale — it carries the `0/6` artefact, not
a real concordance signal.

### Resume actions next session

1. **Run the smoke test with a longer outer budget and watch the log
   live, not in background:**

   ```bash
   cd /home/abhimanyu/Desktop/SynthaTrial-repo/anukriti
   source venv-baseline/bin/activate
   timeout 1800 python scripts/run_pharmcat_comparison.py \
       --sample-ids HG00096 \
       --output docs/validation/pharmcat_concordance_smoketest.json \
       2>&1 | tee docs/validation/pharmcat_concordance_smoketest_v3.log
   ```

   30 minutes is plenty for one sample assuming v2's slowness is
   chr2 extraction overhead, not a deadlock.

2. **If extraction is still the bottleneck**, profile
   `extract_sample_variants()` in
   `src/benchmark/pharmcat_comparison.py`. Two suspects:

   - The function may be doing naive line iteration over the entire
     1.2GB chr2 VCF instead of using tabix region-extraction
     (`tabix VCF chr2:START-END` or `bcftools view -r`).
   - The `pyliftover==0.4.1` step may be re-loading chain files per
     variant.

   First check: `grep -n "open\|tabix\|bcftools" src/benchmark/pharmcat_comparison.py`
   in the variant-extraction code path.

3. **If extraction is fast and PharmCAT is the bottleneck (warm)**,
   the 300s docker timeout might still be tight on a slow machine.
   Bump to 600s in a follow-up.

4. **Once smoke test produces a real comparison JSON**, scale to 10
   GeT-RM samples (per existing `--samples 10` flag and the
   `DEFAULT_SAMPLES` list in `scripts/run_pharmcat_comparison.py`):

   ```bash
   timeout 3600 python scripts/run_pharmcat_comparison.py \
       --samples 10 \
       --output docs/validation/PHARMCAT_CONCORDANCE_v1.json \
       --latex \
       2>&1 | tee docs/validation/PHARMCAT_CONCORDANCE_v1.log
   ```

5. **Write `anukriti/docs/validation/PHARMCAT_COMPARISON.md`** per
   the prior session-resume specification (methodology paragraph,
   summary tables, per-gene breakdown, honest discordance discussion,
   reproducibility commands, Zack 2026 evaluation framing).

6. **Wire it in:**
   - `api.py` line 1308 already references this path; confirm.
   - `tests/test_expanded_validation.py` expects this reference;
     run after writing.
   - Update `anukriti/CLINICAL_GRADE_ROADMAP.md` CP-5 PARTIAL → DONE.
   - Update `anukriti_docs/IDEA_REFINEMENT_AND_PHASING_2026-05-14.md`
     Phase A2 row open → done.

### Background-process state at session end

The v2 process (PID 20640) **has terminated** (timeout 600s fired).
The PID file at `/tmp/pharmcat_smoke.pid` still points to it but
`ps -p $(cat /tmp/pharmcat_smoke.pid)` will show nothing.

The PharmCAT image (`pgkb/pharmcat:latest`) is now warm — next run
should be faster on the Docker side at least.

### Known risks / failure modes (carried from 05-14)

- **PharmCAT no-call** if liftover misses a definition position —
  reference-backfill mitigates but isn't 100%.
- **CYP2D6 will likely show low concordance** — Anukriti's CYP2D6
  caller doesn't handle CNVs (Cyrius wrapper is open work).
  **Document honestly in the report; don't hide.**
- **Repo size**: do **not** commit the JAR or VCFs. `.gitignore`
  now hard-blocks `*.jar`; existing rules block `*.vcf*`.

---

## 🛑 Task 4 — A1: `.env` BFG / filter-repo scrub (BLOCKED)

**Unchanged from 05-14.** Still waiting on credential rotation.

Confirmed scope:
- 3 commits on 2026-03-08 contain `.env` (`4e3b035`, `7ec8233`, `92288df`)
- 4 remote branches affected: `clinical-grade-pgx`, `main`,
  `solana-anukriti`, `v2`
- Repo is private on GitHub (`Abm32/Synthatrial`)
- 6 credential types exposed: OpenAI, Pinecone, Google, Anthropic,
  AWS access key + secret
- Current `.env` on disk has the **same key prefixes** as the
  historical leak — strong indication keys still not rotated

**DO NOT execute history rewrite until founder confirms rotation.**

Full resume steps in `SESSION_RESUME_2026-05-14.md` (the previous
session-resume; now committed in `anukriti_docs`).

---

## Status snapshot at end of session

| Task | State at start | State at end | Action |
|------|----------------|--------------|--------|
| A4 — Citations | DONE-not-pushed | ✅ DONE + PUSHED | landed across 3 repos in 4 commits |
| B6 — BCHE wedge act | DONE-not-pushed | ✅ DONE + PUSHED | landed in `anukriti-swarm` |
| A2 — PharmCAT concordance | infra ready | ⏳ Docker timeout fixed and pushed; v2 smoke test hit outer wall-clock budget mid-extraction | next session: bump outer timeout, profile `extract_sample_variants` |
| A1 — `.env` scrub | blocked | 🛑 still blocked | waiting on key rotation |

**Repos updated:**

- `anukriti` (2 commits pushed to `clinical-grade-pgx`: README + JAR-block; PharmCAT timeout fix)
- `anukriti-pgx-core` (2 commits pushed to `main`)
- `anukriti-swarm` (3 commits pushed to `main`)
- `anukriti_docs` (1 commit pushed to `main`; this session-resume to follow)

---

## Tomorrow's first action

Run the smoke test in the foreground with a longer wall-clock budget
and watch the log live — the variant-extraction step on chr2 is the
current suspected slow point:

```bash
cd /home/abhimanyu/Desktop/SynthaTrial-repo/anukriti
source venv-baseline/bin/activate
timeout 1800 python scripts/run_pharmcat_comparison.py \
    --sample-ids HG00096 \
    --output docs/validation/pharmcat_concordance_smoketest.json \
    2>&1 | tee docs/validation/pharmcat_concordance_smoketest_v3.log
```

If still slow on chr2 / UGT1A1 extraction, profile
`extract_sample_variants()` per Task 3 resume notes above.

---

## Quick verification command (re-run before resuming)

```bash
cd /home/abhimanyu/Desktop/SynthaTrial-repo/anukriti-swarm
source venv/bin/activate
python -m pytest --override-ini='addopts=' -q --no-header 2>&1 | tail -3
# Expected: 244 passed
timeout 30 python -m demos.showcase 2>&1 | grep "JSON export"
# Expected: JSON export: 1961 bytes
```
