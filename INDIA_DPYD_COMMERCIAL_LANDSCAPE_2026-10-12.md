# What Indian labs actually sell for DPYD, and where the gap is

Researched 2026-10-12 for the end-of-month expo. Every claim below is either a
retrieved artifact or an explicit "could not verify". Read §5 before using any
of this in a pitch — one widely-repeated number in the Indian literature does
not mean what it appears to mean, and quoting it would be taken apart by any
buyer with a scientific reviewer.

---

## 1. The single most useful finding

**No Indian laboratory publishes a DPYD sample report anywhere on the open
web.** Not MedGenome, Strand, Core Diagnostics, 4baseCare, Mapmygenome,
Anderson, nor any marketplace reseller. US, EU and Australian labs publish
theirs freely — ARUP, Children's Mercy and myDNA all have downloadable DPYD
specimen reports.

So prospective Indian buyers cannot see what they are buying before they buy
it. **Having a specimen report to put in someone's hand at the expo is a
differentiator in itself**, before the content of the report is even argued.

## 2. What the Indian market sells today

| Lab / channel | Price (INR) | Method | TAT |
| --- | ---: | --- | --- |
| DNA Labs India | 5,250 | Sanger | 3–4 d |
| Core Diagnostics (via 1mg) | 7,125 | "PCR" | ~7 d |
| DNA Labs India | 9,828 | PCR | 12–15 working d |
| Healthians (via Bajaj) | 10,929 / 17,333 | — | contradictory |
| MedGenome (via 1mg) | 11,210 | Targeted sequencing | ~18 d |
| Apollo 247 | 18,625 | "PCR or NGS" | contradictory |
| DNA Labs India | 20,000 | NGS | — |
| Strand OncoPGx | not published | NGS | 10 d |

Oncologist-reported typical cost is ₹10,000–15,000, and **government insurance
excludes it**. Two listings contradict themselves on turnaround *on the same
page* (Apollo 247: "within 4 days" vs "7–10 working days"; Bajaj: "288 hours"
vs "within 48 hours"), and one claims reports "include reference ranges",
which is meaningless for a genotype test. The low end of this market is
marketplace boilerplate.

## 3. What their reports contain — and conspicuously do not

Reconstructed from catalogue pages, since no DPYD report is published:

- **No Indian lab's public material mentions an activity score.** Only Indian
  *research* papers use one.
- **No Indian lab publishes a numeric dose reduction.** The only concrete
  strings that exist are marketplace copy: Apollo 247 — heterozygous →
  *"dose reduction or close toxicity monitoring is suggested"*; Core via 1mg —
  *"a doctor may recommend a dose adjustment or an alternative regimen"*.
- **Results are framed by zygosity, not by CPIC phenotype.** Apollo 247 uses
  wild-type / heterozygous / homozygous. Core uses normal / abnormal. MedGenome
  does use Normal–Intermediate–Poor, but only on its *thiopurine* page; its
  DPYD material does not.
- **No lab lists the alleles it did NOT test.** MedGenome's brochure says the
  opposite — "Covers all other alleles present at low frequency as well" —
  without enumerating anything.
- **No lab states an ancestry limitation.** MedGenome alone discusses
  population, and uses it as a selling point rather than a caveat.
- **No lab publishes a transcript ID** (e.g. `NM_000110.4`) for DPYD.

### The opening

A report that states **diplotype → activity score → named CPIC phenotype →
explicit % starting-dose reduction, attributed to CPIC**, and that names the
loci it did not read, would be ahead of every Indian offering that could be
documented. That is what `asl` already emits.

## 4. Population coverage is already a selling axis — and it is half-played

MedGenome is the only lab marketing on coverage, and does it well: a bar chart
of Central/South Asian vs Indian (n=1401) frequencies, plus a direct knock on
competitors — *"Most of the available assays in the market covers \*2A allele
with a frequency of 0.8% but NOT HapB3 allele which is known to occur at
1.97%."*

Two things nobody claims:

- **`c.2279C>T`** — our measured 0.63% in GenomeIndia (n=9,768) and 0.000% in
  Europeans, absent from every commercial platform the 2024 AMP consensus
  surveyed. MedGenome's own brochure lists it under "Partial Activity" but does
  not market it.
- **The HapB3 causal-vs-tag distinction.** MedGenome's brochure lists
  `c.1129-5923C>G` and `c.1236G>A (HapB3)` as separate entries and charts them
  as one merged bar — i.e. it does not separate the causal intronic variant
  from the exonic tag. The AIIMS paper assigns an activity score off the tag
  alone. **The problem our engine fixed is present in the Indian commercial
  material too**, and nobody else is talking about it.

## 5. A correction that must be made before anyone pitches this

An Indian GI-cancer cohort (APJCP 2025, n=66) reports **"48.5% carried an
actionable DPYD variant, dominated by \*9A (43.9%)"**, and this is the single
most quotable India-specific number in the literature.

**Do not use it as stated.** `*9A` is `c.85T>C` / `rs1801265`, and **CPIC
classifies it as Normal function**, at **25.5%** of Central/South Asian
chromosomes — verified against `api.cpicpgx.org` and against our own pinned
table, where it is `*9A rs1801265 G Normal function`. A Normal-function allele
at a quarter of all chromosomes is not a missed actionable finding; it is the
background.

The paper is using "actionable" in a sense CPIC does not share. Repeating it to
a hospital's scientific reviewer invites the response that we do not know the
difference between an allele that is common and an allele that matters — which
would discredit the `c.2279C>T` argument standing next to it, and that one is
real.

Our own codebase already handles this correctly: swarm's
`P1_SAS_DPYD_CONTESTED` flag annotates South Asian patients carrying
`*9A` / `M166V` / `*6`, is deliberately non-blocking, and its own text ends
*"It is not grounds to withhold the standard CPIC answer."* The pitch needs to
match the code.

## 6. Indian clinical evidence worth citing, accurately

- **AIIMS New Delhi, D-TORCH sub-study** (Front Pharmacol 2026, provisionally
  accepted) — germline WES; states plainly that *"routine DPYD genotyping is
  not commonly practiced in India, and information on DPYD polymorphisms in the
  Indian population is scarce"*, and that CPIC phenotype prediction has limits
  in Indian patients. **No poor metabolizers detected.** ⚠️ The paper has an
  internal error — its Table 3 maps `rs1801265` to the `c.1905+1G>A` splice
  change, which is wrong. Flag it if citing.
- **ESMO Asia 2024 Indian pilot** — 151 analysed, any-grade toxicity in 52
  (34.3%), **5 deaths, 3 of them in DPD wild-type patients.** This is a better
  number for us than the \*9A one: it is exactly the residual-risk argument the
  product makes, from an Indian cohort.
- **Oncologist practice survey** — Indian TAT "7 to 10 days in tier-one
  cities"; long waits push oncologists to treat untested in advanced disease;
  oncologists explicitly ask *"whether the test encompasses all DPYD variants
  specific to local ethnicities"*. That question is the sales conversation.

## 7. What could not be verified

Metropolis, Dr Lal PathLabs, SRL/Agilus, Neuberg, Lifecell, Oncquest and
Positive Bioscience all run bot-blocked or JavaScript-only catalogues that
could not be enumerated. **Absence of evidence, not evidence of absence** — any
of them may sell a DPYD test. Tata Memorial's current menu is unknown; the only
evidence is a 2016 study where DPD was tested *reactively*, after a cycle-1
toxicity event.

Search was also US-indexed, so India-geo-ranked pages are underrepresented. The
cheapest way to close all of this: email each lab and ask for a specimen
report.
