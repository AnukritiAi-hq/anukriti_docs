# 01 — Andrea Gaedigk (PharmVar / Children's Mercy KC) — Implementer alignment + South Asian PGx pointers

> **Thread status:** ✅ initial exchange resolved; follow-ups identified.
> **First contact:** 2026-05-15 (Friday, 6:26 PM IST)
> **Last exchange:** 2026-05-16 09:08 IST
> **Counterparty email:** `agaedigk@cmh.edu`
> **My side:** Abhimanyu R B `<abhimanyurbsa@gmail.com>`

---

## Why this matters

Anukriti's deterministic engine is built against PharmVar star
allele nomenclature across 13 pharmacogenes. PharmVar is the
scientific ground truth for our `pgx-core/anukriti_pgx_core/calling/`
module and the pinned phenotype tables in
`anukriti_pgx_core/phenotype/tables/`. Of the 24 source files
that reference PharmVar in `anukriti-pgx-core`, the heaviest
dependency is `calling/base.py` (17 references). Drift from
PharmVar is, definitionally, a correctness regression.

Andrea Gaedigk is one of the senior stewards of PharmVar and a
co-author on the 2025 StarTRAC-CYP2D6 paper that shaped how our
CYP2D6 caller handles allele-specific read phasing.

This was the first formal scientific outreach from Anukriti to a
nomenclature-registry steward.

---

## Outcomes (TL;DR for next session)

1. **No formal "implementer registry" exists at PharmVar today** —
   they are *exploring options* but cannot acknowledge third-party
   tools formally because PharmVar is a free resource and tracking
   would be difficult.

2. **Action: register a PharmVar account** to receive email
   notifications on database releases. This is the canonical
   mechanism for staying aligned with updates.
   - URL: <https://www.pharmvar.org>
   - Terms & conditions: <https://www.pharmvar.org/terms-and-conditions>

3. **Action: integrate the PharmVar API** for programmatic
   retrieval.
   - API documentation: <https://www.pharmvar.org/documentation>
   - This replaces ad-hoc JSON downloads with versioned, audit-able
     API calls and complements `scripts/cpic_audit.py` in
     `anukriti-pgx-core`.

4. **Action: cite PharmVar publications formally**, not just the
   website. Andrea explicitly noted: *"citations are measurable
   while website mentions are rather difficult to track."* This is
   a low-cost, high-trust signal we should land everywhere we
   reference PharmVar.

5. **South Asian PGx data is genuinely sparse at the source level.**
   Andrea: *"There is unfortunately not much info for the Indian
   subcontinent."* This is independent confirmation of the data-gap
   thesis underpinning Anukriti's positioning. **Use as citeable
   third-party validation in the strategy doc.**

6. **Follow-up contacts handed off:**
   - **Chonlaphat Sukasem** (Mahidol University, Thailand) —
     `chonlaphat.suk@mahidol.ac.th` — Thai PGx work
   - **Martin Kennedy** (University of Otago, NZ) —
     `martin.kennedy@otago.ac.nz` — Native New Zealander PGx work
   - **Andrew Somogyi** (University of Adelaide, Australia) —
     `andrew.somogyi@adelaide.edu.au` — flagged by Andrea as
     someone "who may be able to direct to other people";
     **prioritize for South Asian-focused pointers**

---

## Action items

- [ ] **A** — Create a PharmVar account; subscribe to release notifications
- [ ] **B** — Integrate the PharmVar API into `anukriti-pgx-core`
      (likely a new module under `anukriti_pgx_core/registries/`
      that wraps the API and feeds `scripts/cpic_audit.py`)
- [ ] **C** — Add formal PharmVar citations everywhere the engine
      references the registry: README files, `pyproject.toml`,
      LaTeX papers (`anukriti.tex`,
      `anukriti_extended_abstract.tex`), and any
      academic-positioning docs in `anukriti-pgx-core`
- [ ] **D** — Reach out to Andrew Somogyi first (highest-priority
      pointer per Andrea's framing); then Sukasem and Kennedy in
      parallel as adjacent-region anchors
- [ ] **E** — Update `IDEA_REFINEMENT_AND_PHASING_2026-05-14.md`
      Phase C contact list with Andrea Gaedigk + the 3 referrals
      (Sukasem, Kennedy, Somogyi)

---

## Full correspondence (verbatim, chronological)

### 1 — Outbound, 2026-05-15 6:26 PM IST

**From:** Abhimanyu R B `<abhimanyurbsa@gmail.com>`
**To:** Andrea Gaedigk `<agaedigk@cmh.edu>`
**Subject:** Implementing PharmVar star allele nomenclature in a deterministic PGx engine - a question

> Hi Dr. Gaedigk,
>
> Your 2025 StarTRAC-CYP2D6 paper directly shaped how we handle
> allele-specific read phasing in our CYP2D6 caller. I wanted to
> reach out because PharmVar's nomenclature is the scientific
> ground truth our entire engine is built against.
>
> I'm Abhimanyu, building Anukriti — a deterministic
> pharmacogenomics inference platform. We implement PharmVar star
> allele nomenclature across 13 pharmacogenes (CYP2D6, CYP2C19,
> CYP2C9, CYP3A5, DPYD, SLCO1B1 and others) with CPIC-governed
> phenotype calls, population-aware reasoning across 5
> super-populations, and a named-refusal taxonomy — when evidence
> for a specific ancestry-gene-drug combination is insufficient,
> we return a named refusal with a rule ID rather than a
> confidence-degraded answer.
>
> My question: does PharmVar have a formal pathway for third-party
> tools that implement your nomenclature to be acknowledged or
> listed as implementers? Even informal guidance on how to stay
> aligned with PharmVar updates as we scale would be enormously
> helpful.
>
> Would you be open to a brief exchange over email?
>
> Best,
> Abhimanyu R B

---

### 2 — Inbound, 2026-05-15 7:58 PM IST

**From:** Gaedigk, Andrea `<agaedigk@cmh.edu>`
**To:** Abhimanyu R B

> Abhimanyu,
>
> We are glad to hear that PharmVar is a useful resource.
>
> If you have a PharmVar account, you have the option to receive
> an email notification when a new database version is released.
> Otherwise, please be aware of our user terms and conditions
> (<https://www.pharmvar.org/terms-and-conditions>). Data can be
> retrieved via API (<https://www.pharmvar.org/documentation>). We
> also ask users to cite our publications in addition to our
> website as citations are measurable while website mentions are
> rather difficult to track.
>
> We are currently not having a formal pathway to acknowledge
> third party users/implementers as PharmVar is a free resource
> making this difficult to track. We are exploring options though.
>
> Thank you
> Andrea

(CMH boilerplate confidentiality footer omitted.)

---

### 3 — Outbound, 2026-05-15 10:22 PM IST

**From:** Abhimanyu R B
**To:** Andrea Gaedigk

> Hi Andrea,
>
> Thank you so much for the quick response — this is exactly what
> I needed.
>
> I'll set up the API integration and register for version
> notifications right away. We'll make sure to cite your
> publications formally in everything we publish.
>
> One small ask: as someone at the center of the PGx nomenclature
> ecosystem, is there anyone you'd suggest I speak with —
> particularly around population-specific allele characterization
> for South Asian genomes? That's our biggest data gap right now
> and I want to make sure we're building on the right foundations.
>
> Thank you again,
> Abhimanyu

---

### 4 — Inbound, 2026-05-15 11:56 PM IST

**From:** Gaedigk, Andrea
**To:** Abhimanyu R B

> Abhimanyu,
>
> We are rarely receiving submissions from this part of the world.
> You may want to contact the senior authors on papers who have
> published on the genes of interest.
>
> If you are interested in Thai you may want to contact c. Sukasem
> at `chonlaphat.suk@mahidol.ac.th`.
>
> Martin Kennedy has done some work as well — is native New
> Zealanders — `martin.kennedy@otago.ac.nz`.
>
> Andrew Somogyi may be able to direct to other people —
> `andrew.somogyi@adelaide.edu.au`.
>
> There is unfortunately not much info for the Indian subcontinent.

---

### 5 — Outbound, 2026-05-16 09:08 AM IST

**From:** Abhimanyu R B
**To:** Andrea Gaedigk

> Hi Andrea,
>
> This is incredibly helpful — thank you for taking the time.
>
> Your 2023 pharmacoequity review framed something we'd been
> building toward intuitively but hadn't articulated as clearly —
> the idea that allele characterization gaps in underrepresented
> populations aren't just data problems, they're equity problems
> with clinical consequences. That's essentially the founding
> premise of Anukriti.
>
> The gap in South Asian data being as sparse as it is at the
> source level is actually important validation for why we're
> building this. I'll reach out to Dr. Sukasem, Dr. Kennedy, and
> Dr. Somogyi right away — particularly Dr. Somogyi if he can
> point toward South Asian-focused work.
>
> Really appreciate your generosity here.

---

## Why each takeaway matters

### "No formal implementer registry"

We were hoping for an "Anukriti is a PharmVar-aligned implementer"
listing as a credibility marker. PharmVar's answer is: not today.
**Pivot:** the formal-citation requirement plus the API-driven
audit pipeline becomes our *de facto* alignment claim. We can say
truthfully:

> *Anukriti pulls allele definitions from PharmVar via the
> documented API on every release notification, audits divergences
> via `scripts/cpic_audit.py`, and cites PharmVar publications in
> every academic and product surface.*

That is a stronger statement than "listed in a registry" anyway —
it's an active, audit-able discipline.

### "Citations are measurable, website mentions are not"

Specific, actionable, and easy to land. Every README, every
`pyproject.toml`, every paper, every product surface that
references PharmVar should cite the canonical PharmVar
publications, not just the URL. Concrete next session: sweep all
PharmVar mentions across `anukriti-pgx-core`,
`anukriti-swarm`, `anukriti`, and `anukriti_docs` and add formal
citations. Track via grep:

```bash
grep -rE "pharmvar\.org|PharmVar" \
  anukriti-pgx-core/ anukriti-swarm/ anukriti/ anukriti_docs/ \
  --include="*.md" --include="*.py" --include="*.toml" --include="*.tex"
```

Canonical PharmVar publications to cite (need to confirm exact
references on next pass; pulling from memory):

  - Gaedigk et al., *Clinical Pharmacology & Therapeutics*, 2018 —
    "The Pharmacogene Variation (PharmVar) Consortium: Incorporation
    of the Human Cytochrome P450 (CYP) Allele Nomenclature Database"
  - Gaedigk et al., 2021 — PharmVar update paper
  - StarTRAC-CYP2D6, 2025 — Gaedigk et al.

### "Not much info for the Indian subcontinent"

This is **the most strategically valuable line in the thread.** A
senior PharmVar steward, with a global view of submissions,
confirms the data sparsity Anukriti is built to address.

This belongs in:
  - `anukriti-pgx-core/docs/strategy.md` Moat section, as a
    third-party validation quote (with attribution + permission
    consideration)
  - `anukriti_docs/IDEA_REFINEMENT_AND_PHASING_2026-05-14.md`
    Sharpened-thesis section as supporting evidence
  - The next pre-seed pitch revision in `investor-outbound/`

**Permission note:** Andrea's email is private correspondence.
Before quoting verbatim in any external doc (pitch deck,
strategy.md, paper), I should send a one-line ask:

> *"Would you be comfortable with me citing your observation that
> '[quote]' in our strategy/pitch documents, with attribution? Happy
> to share the framing for review first."*

Internal docs (this file, IDEA_REFINEMENT) can paraphrase or quote
freely — they're git-private to the AnukritiAi-hq org.

### Three referrals — prioritization

| Contact | Why prioritize | Risk |
|---|---|---|
| **Andrew Somogyi** (Adelaide) | Andrea explicitly framed him as a *connector* ("may be able to direct to other people"). The highest expected-value contact — a connector compounds. | None obvious; cold outreach |
| **Chonlaphat Sukasem** (Mahidol) | Thai PGx is adjacent-region; Thai populations share some Southeast Asian admixture with Indian sub-populations. Useful for triangulating the architecture but not directly Indian. | Lower priority for the South-Asian-data ask specifically |
| **Martin Kennedy** (Otago) | Native New Zealander PGx is geographically distant but is a model for population-specific allele characterization done at scale by a small group. | Useful as a *methodological* reference, not a data partner |

**Order of outreach:** Somogyi → Sukasem → Kennedy. Lead with
the connector. Each cold-email should reference Andrea Gaedigk's
introduction explicitly to leverage social proof.

---

## Updates / follow-ups (append-only)

*(nothing yet — this thread is fresh as of 2026-05-16)*
