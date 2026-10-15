# Has the API ever been used in patient care? — evidence, 2026-10-15

Checked because several documents assert "not used in patient care" and
"no clinical claim", and nobody had verified either. A claim that happens
to be true but has never been checked is not evidence, and a reviewer who
asks "how do you know?" is entitled to an answer.

**Short answer: supported for the last 30 days, and not verifiable before
that from this source.**

## Method

Azure Log Analytics, workspace `17803ecf…ba16` (`anukriti-env`), table
`ContainerAppConsoleLogs_CL`, container app `anukriti-api` in
`anukriti-rg`. Queried as `tech@anukritiai.com`, read-only.

## What the logs show

| | |
|---|---|
| retention actually present | **2026-09-15 to 2026-10-15 only** — 30 days |
| total console log lines | 368 |
| total HTTP requests seen | ~230 |

Request paths, in order of volume: `/page-views` (119), `/robots.txt`
(20), `/asl/dpyd/panels` (17), `/health` (11), `/` (10), `/api-keys` (8),
`/asl/dpyd/interpret` (6), `/population/frequency` (6),
`/llm-context/interpret` (5), `/benchmarks` (4), then single-digit counts
on `/genomes/index`, `/runs/from-samples`, `/projects`, `/vcf/extract`,
`/samples/1000g`, `/openapi.json`.

**Every sample identifier that appears in any request is a public 1000
Genomes accession:**

`HG00096`, `HG00099`, `HG03006`, `HG03046`, `HG03700`, `NA18525`.

Zero identifiers outside the `HG`/`NA` public reference namespace. No
patient identifier of any kind appears in 90 days of queried range (the
query asked for 90; the data only goes back 30).

## What this supports

- **"Not used in patient care"** — supported for 2026-09-15 to
  2026-10-15. The volume is development and demo traffic, and every
  genomic input is a public reference sample.
- **"A deployed research API"** — accurate. The service is live.

## What this does NOT support, and must not be stretched into

- **Any claim about the period before 2026-09-15.** The logs do not
  reach it. The honest phrasing is *"log retention covers 30 days; over
  that window every request used public 1000 Genomes samples and no
  patient identifier appears"* — not *"the API has never processed
  patient data."* The second sentence is not something this evidence can
  carry.
- **Proof of absence.** Console logging depends on what the application
  chooses to log. A request that the app did not log would not appear
  here. This is corroboration, not an audit trail.
- **"Live production system"** in any sense implying clinical
  deployment. No hospital or pilot appears in this traffic.

## Related finding, not the question asked

All six container apps in this subscription have `external: true`,
including **`cohortfit`**, which is separately recorded as having no
authentication. That is an open exposure independent of this check and it
is not addressed here.

## To extend the window

Container Apps console logs expire from the default workspace. If the
pre-September period matters — for a funder correction, a CRO diligence
pack or a regulator — the places to look are the Azure Activity Log,
any diagnostic settings archiving to storage, and the ingress/front-door
logs if they were enabled. None of those was checked today.
