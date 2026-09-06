# Component research: a DPYD/DPD/5-FU synthetic-patient engine

Research date: 6 September 2026. This report updates the earlier general PGx
proposal for the current oncology collaboration. Proposed engineering decisions
are distinguished from published results. The complete source catalog and
documented API surfaces are in [the evidence register](EVIDENCE_REGISTER.md).

## 1. Founder populations: reuse reference information, quantify local uncertainty

The public IGSR high-coverage collection provides a practical GRCh38 starting
point with phased SNV/INDEL/SV resources. Its 3,202 participants include 698 related
individuals added to the original 2,504; family structure matters for validation.
The previously executed prototype used the older b37 chromosome 19 panel and
does not establish DPYD-region performance. [IGSR collection](https://internationalgenome.org/data-portal/data-collections/1000genomes_30x/),
[relatedness documentation](https://www.internationalgenome.org/faq/which-datasets-include-related-individuals/).

For Bhutan, a Himalayan study includes 87 genomes across 16 populations, including
six Bhutanese populations. Its population structure is more informative than
assigning a generic South/East Asian mixture from geography. Individual data
access and permitted derivatives still need confirmation. The 443-sample Bhutan
PGx study concerns selected CYP markers, not a DPYD reference or 5-FU outcome
cohort. [Himalayan study](https://doi.org/10.1016/j.cub.2025.06.048),
[Bhutan PGx study](https://pubmed.ncbi.nlm.nih.gov/32004143/).

**Implementation decision:** begin with public DPYD-region references and the
partner oncology population as the first evaluation target. Add local founder
data when accessible. Fit subgroup mixtures and uncertainty from appropriate
development data. Compare local calibration against plain pooling: the archived
experiment found that pooling beat the proposed calibration on average.

Generate an outer ensemble of plausible population models and inner patient
cohorts within each. The variability between outer models represents unresolved
population knowledge; generating more inner patients only reduces simulation
noise. Use clinical task relevance to prioritize new samples or assays. These
are proposed statistical design choices, not a demonstrated Bhutan model.

## 2. Inherited genomes: established simulators plus DPYD-specific representation

HAPNEST demonstrates biobank-scale common-variant synthesis, including a released
1,008,000-person dataset. Its trait simulations are controlled model outputs.
It is a useful scaling comparator; its common-variant emphasis leaves rare
DPYD variants and structural events to be evaluated separately. [HAPNEST](https://doi.org/10.1093/bioinformatics/btad535).

Ped-sim is the direct match to computational parent–child inheritance. Its
sex-specific maps and crossover-interference model support realistic IBD
experiments. Its documented defaults add missingness/error and unphase output,
so truth generation needs explicit flags. [Ped-sim paper](https://doi.org/10.1371/journal.pgen.1007979),
[implementation](https://github.com/williamslab/ped-sim/blob/master/README.md).

Haptools provides a useful reference-based admixture/breakpoint workflow.
SimHumanity provides later whole-genome demographic experiments spanning
autosomes, X/Y and mitochondria; those models carry simplifications including
within-subpopulation panmixia and omitted PAR recombination. Neither supplies
DPD activity or adult oncology physiology. [Haptools documentation](https://haptools.readthedocs.io/en/stable/commands/simgenotype.html),
[SimHumanity](https://doi.org/10.47248/hpgg2505040006).

**Implementation decision:** adopt Ped-sim for pedigrees and qualify one
map-based population generator alongside the pooled-copy baseline. Defer
whole-genome demographic simulation until the DPYD exposure workflow works.
Do not make artificial uniqueness the primary quality target.

DPYD needs explicit phase and assay provenance. HapB3's causal intronic
rs75017182 and synonymous proxy rs56038477 are not perfectly linked. Keeping
them distinct permits causal-only, proxy-only, cis/trans and untested states.
A blanket recombination prohibition across the entire large gene would create
an artificial population model. [HapB3 study](https://doi.org/10.1111/cts.13699),
[genotyping consensus](https://doi.org/10.1016/j.jmoldx.2024.05.015).

Structural variants also matter: a Finnish DPYD exon 4 deletion study provides
an example of locally enriched variation that a short list of SNPs can miss.
Its population frequency is not a prior for Bhutan or Indian oncology patients.
Represent exon/gene deletions and copy number from the start, then qualify their
inheritance and interpretation with explicit truth cases. [Deletion study](https://doi.org/10.1111/bcpt.70011).

## 3. Adult physiology: use PK-Sim's conditional anatomy, then fit oncology context

PK-Sim's population machinery conditions anatomy and physiology on demographic
characteristics and applies consistency criteria. Its age-range sampling does
not automatically reproduce an oncology cohort's age distribution. The documented
individual-transfer workflow also warns against overwriting formula-derived
parameters. [Population documentation](https://docs.open-systems-pharmacology.org/v12/working-with-pk-sim/pk-sim-documentation/pk-sim-creating-populations),
[individual workflow](https://www.open-systems-pharmacology.org/OSPSuite-R/articles/create-individual.html).

The documented standard ontogeny list contains CYP/UGT examples but no DPD
entry. The expression documentation distinguishes absolute reference abundance
from relative organ expression; its spatial expression database is not a
circadian model. [Individual/ontogeny documentation](https://www.open-systems-pharmacology.org/OSPSuite-R/articles/create-individual.html),
[expression profiles](https://docs.open-systems-pharmacology.org/working-with-pk-sim/pk-sim-documentation/pk-sim-expression-profile).

**Implementation decision:** start with adults; keep genetic ancestry separate
from the physiology prior. Fit local joint age/body-size, disease, organ-function
and co-medication distributions around the qualified OSP physiology generator.
Do not assign generic CYP ontogeny to DPD. Simulate multiple adult states for a
genome without claiming to reconstruct that person's life history from DNA.

## 4. DPYD function: direct experimental evidence is the most useful bridge

Offer 2014 evaluated 80 DPYD variants in a mammalian expression system. The local
CSV contains 43 rows, so it is an incomplete extraction. Reconcile it with
Supplementary Table S2 and retain assay normalization rather than using the local
file as a complete truth set. [Offer study](https://pubmed.ncbi.nlm.nih.gov/24648345/).

Hishinuma 2022 tested 41 Japanese-population variants plus 3 controls, reporting
5-FU kinetic measurements in Table 4. There are consequential disagreements:
D949V intrinsic clearance was 186.01% of wild type in that assay, whereas Offer
reported roughly 59% relative activity; these endpoints and assay conditions
differ. Retain study-specific results and uncertainty. Neither value is a
measured percentage of a patient's hepatic clearance. [Kinetic study](https://doi.org/10.3389/fphar.2022.930470),
[Offer](https://pubmed.ncbi.nlm.nih.gov/24648345/).

Sudo 2026 adds seven rare variants with activity, abundance, dimerization and
selected patient PBMC evidence. Some toxicity-associated variants retained
substantial measured activity, reinforcing the separation between molecular
activity and clinical outcomes. [Sudo study](https://doi.org/10.1155/jcpt/3886738).

Amorosi's CYP2C9 work supplies a scalable experimental precedent: 6,142 activity
measurements and 6,370 abundance measurements, plus orthogonal validation for
selected variants. Reuse the paired-endpoint/validation approach; CYP2C9 scores
are not DPD scores. We did not locate a near-saturation DPYD activity dataset
equivalent to that CYP2C9 resource in this search. [CYP2C9 study](https://pubmed.ncbi.nlm.nih.gov/34314704/).

**Implementation decision:** create a molecular evidence registry, then a
probabilistic assay-to-human bridge. Keep splicing, protein abundance, catalytic
kinetics, dimer effects, PBMC activity and human clearance separate. Include
assay-system effects and unknowns. Use measured human exposure to calibrate the
bridge; use new functional assays to reduce specific uncertainties.

Human PK provides a limited anchor: a study of 30 DPYD*2A heterozygotes and 18
controls estimated approximately 40% lower Vmax in carriers using a saturable
model. This supports variant-group calibration, not a universal genotype-to-Vmax
formula. [Van Kuilenburg study](https://pubmed.ncbi.nlm.nih.gov/22339448/).

The current core's categorical activity score remains a clinical interpretation
record. Its causal/proxy provenance is valuable, but it does not itself provide
a quantitative organ-capacity model. Historic classifier metrics are also
insufficient: legacy code used label proxies; v4/v5 removed those inputs, while
v5 still requires a label-source audit before reuse. These are findings from
the local files listed in the evidence register.

## 5. Drug response: a direct published 5-FU model exists

The principal candidate is Marok 2024's PK-Sim/MoBi 9.1 model of 5-FU, uracil and
their metabolites. It includes saturable enzyme kinetics and circadian scenarios;
the publication separates model development/evaluation data. Its chronotherapy
results are simulated research findings. The four actual project files are
publicly visible, including constant infusion and injection models. Supplementary
parameter extraction, local execution and model-file license confirmation remain
implementation tasks. [Paper](https://doi.org/10.1002/cpt.3181),
[model files](https://github.com/Clinical-Pharmacy-Saarland-University/5-FU-PBPK-Model).

**Implementation decision:** reproduce the constant-infusion model before
altering DPD or local physiology. Use Python orchestration and a documented
OSPSuite-R worker. Current candidate 12.4.3 requires R ≥4.4 and the .NET runtime;
compatibility with 9.1 model files must be measured. Older desktop-install
instructions are superseded by the ≥12.1 bundled-dependency workflow.
[Tagged requirements](https://github.com/Open-Systems-Pharmacology/OSPSuite-R/blob/v12.4.3/DESCRIPTION),
[installation correction](https://www.open-systems-pharmacology.org/OSPSuite-R/articles/PKSim-installation.html).

Briki 2026's individual-data meta-analysis, 726 patients/2,332 concentrations,
offers a conventional population-PK comparator with saturable and linear
elimination. Model code/covariance availability is not yet confirmed.
Mielke 2025 offers a numerical comparator but excluded the relevant DPYD-deficient
group. Neither can be treated as an independently validated toxicity-label
generator. [Briki](https://pubmed.ncbi.nlm.nih.gov/42283826/),
[Mielke](https://pmc.ncbi.nlm.nih.gov/articles/PMC12114802/).

Capecitabine requires its own activation/absorption/renal and adherence model.
A published PBPK study exists, but executable files were not verified in this
pass. Clopidogrel remains a useful integration precedent; the direct 5-FU model
now takes priority. [Capecitabine study](https://pubmed.ncbi.nlm.nih.gov/37610618/),
[clopidogrel model](https://github.com/Open-Systems-Pharmacology/Clopidogrel-Model).

## 6. Real observations: define what “works” means before fitting

IATDMCT guidance provides regimen-specific 5-FU TDM context. A 2025 prospective
study supplies a practical 46-hour infusion measurement template with LC-MS/MS,
sample handling and cycle-level follow-up. Use those methods to design the data
sheet, rather than automatically adopting a published dosing algorithm.
[TDM guidance](https://pubmed.ncbi.nlm.nih.gov/29923599/),
[prospective study](https://doi.org/10.1200/PO-25-00062).

Uracil requires particular care. De With's 955-person study found limited
predictive usefulness and center variation; Maillard documented preanalytic and
repeat-classification variability. Alpe2U found an exposure tradeoff under its
phenotyping strategy. EMA separately warns that renal impairment can confound
uracil interpretation. These sources motivate a measurement model and a
controlled laboratory substudy, not abandonment of phenotype research.
[De With](https://pubmed.ncbi.nlm.nih.gov/35397172/),
[Maillard](https://pubmed.ncbi.nlm.nih.gov/36104927/),
[Alpe2U](https://pubmed.ncbi.nlm.nih.gov/40466468/),
[EMA](https://www.ema.europa.eu/en/medicines/dhpc/5-fluorouracil).

**Implementation decision:** evaluate exposure before clinical toxicity. Separate
pretreatment prediction from prediction updated using a measured drug level.
Hold out people/families/sites and all their cycles. Compare synthetic augmentation
with real-only, reference-transfer and conventional modeling baselines. Preserve
regimen-specific target definitions and report calibration, uncertainty and
negative transfer. The companion validation protocol defines the full design.

## Current guidance and corrections to inherited assumptions

The official 9 July 2026 CPIC notice announces a future causal-HapB3 allele value
of 0.75 while keeping the current database at 0.5 until guideline publication.
Do not silently pre-apply it or generalize it to other variants. Check again when
implementation starts. [CPIC notice](https://blog.clinpgx.org/cpic-comment-on-pending-dpyd-guideline-update/).

Current FDA wording recommends DPYD testing before capecitabine/5-FU unless
immediate treatment is necessary; older “consider testing” summaries are stale.
EMA guidance should also be described at its actual scope, without claiming one
identical legal mandate across all countries. These references establish the
clinical context; this plan does not change prescribing tables.
[FDA update](https://www.fda.gov/drugs/resources-information-approved-drugs/safety-labeling-update-capecitabine-and-fluorouracil-5-fu-risks-associated-dihydropyrimidine),
[EMA recommendation](https://www.ema.europa.eu/en/news/ema-recommendations-dpd-testing-prior-treatment-fluorouracil-capecitabine-tegafur-and-flucytosine).

The research contribution to test is a combination of locally calibrated
founders, allele-aware inheritance, quantified DPD evidence, adult physiology
and measured-exposure validation. Novelty and clinical benefit are not established
by this plan. The completed regional benchmark remains useful evidence that
generation is feasible and that simpler baselines deserve serious comparison.
