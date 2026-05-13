# `.env` Scrub & Credential Rotation Playbook

> **Security-critical, time-sensitive.** Executed against the
> `anukriti` product repo (`https://github.com/Abm32/Synthatrial.git`).
> Do not share the repo publicly, demo it to an investor, or onboard
> an external contributor until this playbook is complete.
>
> Version: 2026-05-12 · Owner: founding engineer · Estimated time:
> 2-3 hours for the scrub, 1-2 hours for rotation across providers
> (parallelizable).

---

## Why this exists

A pre-flight audit of the `anukriti` product repo history found:

```
Repo:           https://github.com/Abm32/Synthatrial.git
Branch where:   refs/remotes/origin/v2
Commits:        92288df, 7ec8233, 4e3b035
```

Three commits in history contain `.env` blobs. The current `.env` is
properly gitignored (and not tracked in any current ref), but the
**blobs are still reachable via the reflog and `refs/remotes/origin/v2`**.
Anyone with clone access to the repo can `git cat-file -p <blob>` and
read the values.

Exposed key names extracted from the blobs (values redacted here —
see the pre-flight audit output for the actual blob contents you're
about to shred):

| # | Key | Provider | Rotation path |
|---|---|---|---|
| 1 | `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` | AWS IAM | AWS console → IAM → Users → Access keys → Deactivate + create new |
| 2 | `AWS_ACCOUNT_ID` | AWS | Account IDs are not secret but should not be in public history |
| 3 | `ANTHROPIC_API_KEY` | Anthropic | [console.anthropic.com](https://console.anthropic.com) → Settings → API Keys → Revoke + create new |
| 4 | `GOOGLE_API_KEY` | Google (Gemini) | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) → Delete + create new |
| 5 | `OPENAI_API_KEY` | OpenAI | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) → Revoke + create new |
| 6 | `PINECONE_API_KEY` | Pinecone | Pinecone console → API Keys → Delete + create new |
| 7 | `PINECONE_ENV` / `PINECONE_INDEX` | Pinecone | Configuration, not secret, but review if it leaks internal topology |

**Total provider rotations required: 5** (AWS, Anthropic, Google,
OpenAI, Pinecone).

The other environment variables in the blobs (`LLM_BACKEND`,
`BEDROCK_REGION`, `TITAN_EMBED_MODEL`, etc.) are configuration, not
secrets — no rotation needed, but they still get scrubbed from
history as part of the full `.env` removal.

---

## Safety considerations before you start

Read these before running any command.

1. **This rewrites history on a public remote.** Every collaborator
   with a clone will need to re-clone or hard-reset after the force
   push. You are the sole founding engineer today, so this is less
   disruptive than in a team — but if anyone has open PRs or
   branches, coordinate before proceeding.
2. **Rotate credentials FIRST, scrub SECOND.** If you scrub first
   and a key is already exposed in a cached GitHub mirror, a search
   engine crawl, or a fork, the key is compromised before you
   revoke it. Rotation is the authoritative fix; scrub is the
   hygiene step that prevents future exposure.
3. **Backup before you mutate.** `git push origin --force` with a
   bad BFG run can destroy history. The playbook includes a full
   repo-mirror backup as step 3.
4. **Do this offline first, verify, then push.** Never run BFG on
   a live remote. Clone a mirror, run the scrub locally, verify
   the blobs are gone, then force-push.

---

## Step 0 — Pre-flight check (5 min)

Confirm the findings still hold exactly as audited on 2026-05-12.

```bash
cd /home/abhimanyu/Desktop/SynthaTrial-repo/anukriti

# Confirm .env is NOT in current working tree
git ls-files .env
# expect: empty output

# Confirm .env IS in history
git log --all --oneline -- .env
# expect 3 commits: 92288df, 7ec8233, 4e3b035 on refs/remotes/origin/v2

# Confirm which branches contain these commits
for c in 92288df 7ec8233 4e3b035; do
  echo "=== $c ==="
  git branch --all --contains "$c" 2>/dev/null
done

# Repo size (so you know what's being rewritten)
du -sh .git
# expect: roughly 4.5M
```

If any of these checks produce different output than documented,
**stop and re-audit** before proceeding. The playbook assumes the
2026-05-12 findings.

---

## Step 1 — Rotate credentials FIRST (30-60 min, parallelizable)

Do this in the order below. Each action is idempotent (creating a
new key doesn't disable the old one; revoking the old one is a
separate deliberate action).

### 1.1 AWS IAM

Target keys: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`.

```bash
# Identify the IAM user owning the exposed key
aws iam list-access-keys --user-name <your-iam-user>

# Create the replacement
aws iam create-access-key --user-name <your-iam-user>
# -> save the new AccessKeyId + SecretAccessKey into your secrets store
#    (AWS Secrets Manager, 1Password, or GPG-encrypted local file)

# Deactivate the old one (don't delete yet — gives you rollback window)
aws iam update-access-key \
  --user-name <your-iam-user> \
  --access-key-id <old-key-id> \
  --status Inactive

# After 48h of confirmed operation on the new key, DELETE the old key
aws iam delete-access-key \
  --user-name <your-iam-user> \
  --access-key-id <old-key-id>
```

Also: check CloudTrail for any anomalous activity on the old key.

```bash
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=AccessKeyId,AttributeValue=<old-key-id> \
  --max-items 50
```

### 1.2 Anthropic

- Sign in to [console.anthropic.com](https://console.anthropic.com).
- Settings → API Keys → Revoke the exposed key.
- Create new key; store in secrets manager.
- Scan Anthropic usage logs for anomalies on the revoked key.

### 1.3 Google / Gemini

- Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
  or the Google Cloud Console if it's a cloud-scoped key.
- Delete the exposed key; create a new one.
- If this is a Google Cloud key, check IAM audit logs for usage.

### 1.4 OpenAI

- [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
  → Revoke the exposed key.
- Create new; store in secrets manager.
- Review billing dashboard for anomalous usage before revoking.

### 1.5 Pinecone

- Pinecone console → API Keys → Delete exposed key.
- Create new; store in secrets manager.
- Review the index's access logs if available.

### 1.6 Update local `.env` with new values

```bash
# Current .env should already be gitignored (confirmed in step 0)
# Replace exposed values with new ones
${EDITOR:-nano} /home/abhimanyu/Desktop/SynthaTrial-repo/anukriti/.env

# Verify nothing is staged
cd /home/abhimanyu/Desktop/SynthaTrial-repo/anukriti
git status
# expect: `.env` should NOT appear as staged or untracked-but-ignored
#         if it appears, double-check `.gitignore` contains `^.env$`

# Sanity-check the app starts with new credentials
# (run whatever the product's smoke test is, e.g.)
python -m pytest tests/smoke -x
```

### 1.7 Document the rotation event

Append to `anukriti/docs/security/ROTATION_LOG.md` (create the file
if it doesn't exist):

```markdown
## 2026-05-12 — Full credential rotation (post-audit)

Reason: `.env` blob found in git history on refs/remotes/origin/v2
in commits 92288df, 7ec8233, 4e3b035. BFG scrub executed same day.

Providers rotated:
- AWS IAM (access key pair)
- Anthropic
- Google / Gemini
- OpenAI
- Pinecone

Old keys: deactivated (not yet deleted; 48h rollback window).
New keys: stored in {secrets manager of choice}.
Next review: 2026-05-14 — delete old keys if no incidents.
```

---

## Step 2 — Prepare for the scrub (15 min)

### 2.1 Install BFG

Mac:
```bash
brew install bfg
```

Linux (manual):
```bash
mkdir -p ~/bin
curl -L https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar \
  -o ~/bin/bfg.jar
alias bfg='java -jar ~/bin/bfg.jar'
# (add to ~/.zshrc or ~/.bashrc if persistent)
```

Verify:
```bash
bfg --version
# expect: bfg 1.14.0 or similar
```

### 2.2 Confirm no open PRs or active branches you'd break

```bash
cd /home/abhimanyu/Desktop/SynthaTrial-repo/anukriti
git branch -a
gh pr list --repo Abm32/Synthatrial --state open 2>/dev/null || \
  echo "install gh CLI or check github.com/Abm32/Synthatrial/pulls manually"
```

If there are open PRs from collaborators, **pause this playbook**
and coordinate with them — force-pushing over their branches will
destroy their work.

---

## Step 3 — Backup the repo (10 min)

**Do not skip this.** A mirror clone is your parachute if BFG
misbehaves.

```bash
cd /tmp
git clone --mirror https://github.com/Abm32/Synthatrial.git \
  Synthatrial-backup-$(date +%Y%m%d).git

# Verify the backup
ls -la Synthatrial-backup-*.git
du -sh Synthatrial-backup-*.git

# Keep this around for at least 30 days after the scrub
```

If anything goes wrong in steps 4-6, you can restore via:
```bash
cd Synthatrial-backup-*.git
git push --mirror https://github.com/Abm32/Synthatrial.git
```

---

## Step 4 — Run BFG on a fresh mirror (15 min)

BFG requires a bare mirror clone, not your working tree.

```bash
cd /tmp
git clone --mirror https://github.com/Abm32/Synthatrial.git \
  Synthatrial-scrub.git
cd Synthatrial-scrub.git
```

### 4.1 Scrub `.env` from all history

```bash
# Option A (preferred): delete the file entirely from all history
bfg --delete-files .env

# BFG will print a report. Expected output:
# - "Cleaning commits" count roughly matching your commit count
# - "Updating 3 Refs" (main, v2, HEAD or similar)
# - "Protected commits" = HEAD (BFG doesn't touch the current HEAD
#   unless you use --no-blob-protection; since .env isn't in HEAD,
#   this is fine)
```

### 4.2 (Belt-and-suspenders) also scrub by blob content

If there's any chance a value was pasted into a non-`.env` file in
history, use BFG's text-replacement mode:

```bash
# Create a file with the sensitive values, one per line
cat > /tmp/sensitive-strings.txt <<'EOF'
<paste-old-aws-access-key-id-here>
<paste-old-aws-secret-access-key-here>
<paste-old-anthropic-key-here>
<paste-old-google-key-here>
<paste-old-openai-key-here>
<paste-old-pinecone-key-here>
EOF

# Run BFG in text-replace mode (all occurrences in all blobs → ***REMOVED***)
bfg --replace-text /tmp/sensitive-strings.txt

# IMPORTANT: shred the sensitive-strings.txt file afterwards
shred -u /tmp/sensitive-strings.txt
```

### 4.3 Expire old refs + aggressive GC

```bash
# In the same Synthatrial-scrub.git directory
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Check the repo shrank (sanity signal that blobs were purged)
du -sh .
```

### 4.4 Verify `.env` blobs are gone

```bash
# No commits should touch .env anywhere in history
git log --all --oneline -- .env
# expect: empty output

# No blob in any ref should match .env content
git rev-list --all --objects | grep -E '\.env$' || echo "OK: no .env in any tree"

# The three originally-offending commits should still exist
# but with .env removed from their trees
for c in 92288df 7ec8233 4e3b035; do
  echo "=== $c ==="
  git show --stat "$c" 2>/dev/null | grep -E '(\.env|changed)'
done
# expect: the commits still exist, but their stats show no .env touched
#         (BFG rewrote them; commit SHAs will have changed — see below)
```

**Commit SHAs will change.** This is expected — BFG rewrites history,
so `92288df` becomes some new SHA with `.env` removed from its tree.
All downstream commits reparented.

---

## Step 5 — Force-push (15 min) ⚠️ HIGH RISK

This is the point of no return. Before running:

- [ ] Rotation completed for all 5 providers (step 1)
- [ ] Backup mirror clone exists at `/tmp/Synthatrial-backup-*.git`
- [ ] No open PRs from collaborators (step 2.2)
- [ ] BFG dry-run verified no `.env` remains (step 4.4)

```bash
cd /tmp/Synthatrial-scrub.git

# This pushes ALL refs (branches + tags) with --mirror
git push --mirror https://github.com/Abm32/Synthatrial.git
```

If the push fails with "remote rejected" on protected branches:

1. Go to [github.com/Abm32/Synthatrial/settings/branches](https://github.com/Abm32/Synthatrial/settings/branches).
2. Temporarily disable branch protection on `main` and `v2`.
3. Retry the push.
4. Re-enable branch protection immediately after.

Do not leave branch protection disabled.

---

## Step 6 — Verify the remote (10 min)

### 6.1 Confirm `.env` is gone from remote history

```bash
# Clone fresh (not your existing working tree — it still has old history)
cd /tmp
git clone https://github.com/Abm32/Synthatrial.git Synthatrial-verify
cd Synthatrial-verify
git log --all --oneline -- .env
# expect: empty output
```

### 6.2 Re-sync your local working tree

Your existing working tree at `/home/abhimanyu/.../anukriti` still
has the old history. Re-sync it:

```bash
cd /home/abhimanyu/Desktop/SynthaTrial-repo/anukriti

# Save any uncommitted work
git stash push -m "pre-scrub-resync"

# Fetch the rewritten history
git fetch origin --prune

# Hard reset each local branch to the new remote state
git checkout clinical-grade-pgx
git reset --hard origin/clinical-grade-pgx

# If you have other local branches that tracked v2 or main, reset them too
# git checkout main && git reset --hard origin/main
# git checkout v2 && git reset --hard origin/v2

# Restore stashed work if any
git stash pop || true  # may conflict; resolve manually
```

### 6.3 Alert any cached integrations

- GitHub Actions may have cached the old history — re-run latest
  workflow to ensure CI passes against the rewritten tree.
- If anyone else has clones, tell them:
  > *"Force-pushed security rewrite on `Abm32/Synthatrial`. Please
  > `git fetch --all && git reset --hard origin/<your-branch>` or
  > re-clone. Any local history-based work needs to be re-applied
  > manually."*

---

## Step 7 — Post-scrub hygiene (ongoing)

### 7.1 GitHub secret scanning

- Enable GitHub secret scanning on `Abm32/Synthatrial` if not already:
  [github.com/Abm32/Synthatrial/settings/security_analysis](https://github.com/Abm32/Synthatrial/settings/security_analysis).
- It won't find the scrubbed secrets, but will catch any future
  accidents at commit time.

### 7.2 Install pre-commit hooks

```bash
cd /home/abhimanyu/Desktop/SynthaTrial-repo/anukriti
pip install detect-secrets
detect-secrets scan > .secrets.baseline

# Add to pre-commit
cat > .pre-commit-config.yaml <<'EOF'
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
        exclude: package.lock.json
EOF

pip install pre-commit
pre-commit install
```

Now every commit locally is scanned for secrets before it lands.

### 7.3 Document secret management

Create `anukriti/docs/security/SECRETS_MANAGEMENT.md`:

```markdown
# Secrets Management

- Never commit secrets to git. `.env` is gitignored.
- Local development: use `.env.example` as the template; copy to
  `.env` and fill in locally. `.env` is git-ignored at line 1 of
  `.gitignore`.
- Production: secrets live in AWS Secrets Manager (or 1Password
  if non-AWS). Loaded at runtime via IAM role, not env var.
- Rotation cadence: every 90 days, or immediately on exposure.
- Rotation log: `docs/security/ROTATION_LOG.md`.
- If you discover an exposed secret, follow
  `docs/security/BFG_SCRUB_PLAYBOOK.md` (a copy of this playbook).
```

### 7.4 After 48 hours, delete the old (now deactivated) AWS keys

```bash
aws iam delete-access-key \
  --user-name <your-iam-user> \
  --access-key-id <old-key-id>
```

### 7.5 After 30 days, delete the backup mirror

```bash
shred -u /tmp/Synthatrial-backup-*.git 2>/dev/null || \
  rm -rf /tmp/Synthatrial-backup-*.git
```

---

## Rollback plan

If anything breaks irrecoverably between step 5 and step 7:

```bash
# Re-disable branch protection on main + v2 via GitHub UI
cd /tmp/Synthatrial-backup-*.git
git push --mirror --force https://github.com/Abm32/Synthatrial.git
# Re-enable branch protection
```

This restores the remote to exactly the pre-scrub state. Your
credentials are still rotated, so the exposure is still mitigated —
you're just buying time to try the scrub again more carefully.

---

## Checklist (print or copy into a tracking issue)

### Rotation (step 1)
- [ ] AWS IAM: new key created, old key deactivated
- [ ] Anthropic: revoked + replaced
- [ ] Google / Gemini: revoked + replaced
- [ ] OpenAI: revoked + replaced
- [ ] Pinecone: revoked + replaced
- [ ] Local `.env` updated with new values
- [ ] `docs/security/ROTATION_LOG.md` entry added
- [ ] App smoke test passes against new credentials

### Scrub (steps 2-6)
- [ ] BFG installed and verified
- [ ] No open collaborator PRs blocking the rewrite
- [ ] Backup mirror at `/tmp/Synthatrial-backup-*.git`
- [ ] BFG `--delete-files .env` ran cleanly
- [ ] BFG `--replace-text` ran cleanly (belt-and-suspenders)
- [ ] `git log --all -- .env` returns empty on the scrubbed clone
- [ ] Force-push succeeded
- [ ] Fresh verification clone confirms `.env` gone from remote
- [ ] Local working tree hard-reset to new remote state

### Hygiene (step 7)
- [ ] GitHub secret scanning enabled
- [ ] `detect-secrets` pre-commit hook installed
- [ ] `docs/security/SECRETS_MANAGEMENT.md` created
- [ ] Calendar reminder set for 48h (delete deactivated AWS keys)
- [ ] Calendar reminder set for 30d (delete backup mirror)
- [ ] Calendar reminder set for 90d (next rotation cycle)

---

## Why this matters in context

Per `anukriti_docs/PLATFORM_ANALYSIS_2026-05-11.md §5`:

> *"One Twitter thread about a leaked key in git history wipes out
> years of built credibility. Fix this week."*

And per §6 Week 0:

> *"BFG `.env` scrub + rotate every previously committed credential.
> Before ANY public push, investor deck, hackathon demo URL share."*

The hackathon submission includes a public demo URL. The investor
outbound plan includes repo links. Both depend on this playbook
completing *before* the next external communication that exposes the
Synthatrial repo.

This is the single highest-ROI 3-hour block in the next 30 days.
Do it now.
