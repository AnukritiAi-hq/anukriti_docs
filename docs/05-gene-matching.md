# Module 05 — Gene Matching

> Prerequisites: [03 Core Concepts](03-core-concepts.md), [04 Architecture](04-architecture.md)

---

## The question we're answering

How does VCF data actually become a phenotype? What happens
inside the gene callers, step by step, with the running example
of Priya's *CYP2C19 \*2/\*2* case?

---

## The pipeline, end-to-end

```
VCF                                     Star alleles
─────────────────────────────────▶      ─────────────────────────────▶     Phenotype

rs4244285:  GT=1/1  (both ALT=A)         CYP2C19 *1 = reference           Poor Metabolizer
rs4986893:  GT=0/0  (both REF=G)         CYP2C19 *2 = rs4244285 ALT        activity: 0.0
rs28399504: GT=0/0  (both REF)           CYP2C19 *3 = rs4986893 ALT
...                                      CYP2C19 *17 = rs12248560 ALT      CPIC table: 2022.1

                    │                                  │
                    ▼                                  ▼
          GeneCaller.call()               PhenotypeEngine.infer()
          (Layer 1)                       (Layer 2)
```

Two layers, two classes, two files. Let's walk each one.

---

## Layer 1 — `GeneCaller`

Source file: `anukriti_pgx_core/calling/cyp2c19_caller.py` (each gene
has its own caller).

The abstract base class is `GeneCaller` (in `calling/base.py`). Every
CYP caller inherits from it. The signature:

```python
class GeneCaller(ABC):
    wildtype_allele: ClassVar[str] = "*1"

    @abstractmethod
    def call(
        self,
        variants: Mapping[str, VCFVariant],
    ) -> Diplotype:
        """Translate a VCF variant map into a star-allele diplotype."""
```

Input: a dict keyed by rsID, mapping to `VCFVariant` records (each
`VCFVariant` has `.ref`, `.alt`, `.gt` — the three columns we need
from a VCF row).

Output: a `Diplotype` frozen dataclass:

```python
@dataclass(frozen=True)
class Diplotype:
    gene: str              # "CYP2C19"
    allele_1: str          # "*2"
    allele_2: str          # "*2"
    variant_source: str    # "vcf" or "legacy_str"
```

Inside `call()`, the CYP2C19 caller does:

1. **Look up the star-allele definition table** — a JSON file listing
   which rsIDs define each star allele. Example:
   ```json
   "*2": { "rs4244285": "A" },
   "*3": { "rs4986893": "A" },
   "*17": { "rs12248560": "T" }
   ```
2. **Check each variant in the input.** For each rsID in the
   definition table, read the genotype from the VCF. Determine
   whether *this position* matches each candidate star allele.
3. **Combine the results.** If both copies match `*2` at rs4244285,
   the diplotype is `*2/*2`. If one copy matches `*2` and the other
   doesn't match any defined star, the other defaults to `*1`
   (wildtype).
4. **Return an ordered diplotype.** Star alleles are sorted by the
   canonical numeric-suffix order (`*2/*17`, not `*17/*2`).

### Priya's worked example

Her VCF has:
```
rs4244285:  GT=1/1  REF=G  ALT=A    ← both copies are ALT=A
rs4986893:  GT=0/0  REF=G  ALT=A    ← both copies are REF=G
rs12248560: GT=0/0  REF=C  ALT=T    ← both copies are REF=C
```

The caller reads the star-allele table:
- `*2` requires `rs4244285: A` — matched on both copies ✓
- `*3` requires `rs4986893: A` — not matched
- `*17` requires `rs12248560: T` — not matched

Both copies of the gene match `*2`. Result:

```python
Diplotype(
    gene="CYP2C19",
    allele_1="*2",
    allele_2="*2",
    variant_source="vcf",
)
```

---

## Layer 2 — `PhenotypeEngine`

Source: `anukriti_pgx_core/phenotype/engine.py`.

The phenotype engine is a pure function over diplotypes. Its API:

```python
class PhenotypeEngine:
    def infer(
        self,
        gene: str,
        allele_1: str,
        allele_2: str,
    ) -> PhenotypeInference:
        ...
```

Output is a `PhenotypeInference` frozen dataclass with:

```python
@dataclass(frozen=True)
class PhenotypeInference:
    gene: str                      # "CYP2C19"
    diplotype: str                 # "*2/*2"
    phenotype: str                 # "Poor Metabolizer"
    activity_score: float | None   # 0.0 or None if named-table only
    cpic_table_version: str        # "2022.1"
    inference_path: str            # "named_diplotype" or "activity_score"
```

### The two inference paths

The engine tries these **in order**:

1. **Named-diplotype table.** Is the input diplotype explicitly
   listed in the CPIC guideline table? If yes, use that.
2. **Activity-score calculation.** Sum the two alleles' activity
   scores, bin the result into a phenotype range.

Named-diplotype wins when present, because CPIC sometimes explicitly
assigns a phenotype that would be wrong under the additive model.

### Why named-diplotype can differ from additive

Priya's case (*2/*2) has activity 0.0 + 0.0 = 0.0 → PM under both
systems. Easy. But consider `*2/*17`:

- Additive: 0.0 (*2) + 1.5 (*17) = 1.5 → NM
- Named table (CPIC 2022 Table 2): explicitly IM

Why the difference? Loss-of-function dominates. Having a working
copy isn't enough if the other copy is making broken protein that
interferes. The science is messy; the table captures the
peer-reviewed consensus; the engine respects the table.

### Priya's phenotype inference

Input: `gene="CYP2C19", allele_1="*2", allele_2="*2"`.

The engine:
1. Looks up named-diplotype table for CYP2C19 — finds entry for
   `*2/*2` → `"Poor Metabolizer"`.
2. Also computes activity score (0.0) for consistency checking.
3. Returns:

```python
PhenotypeInference(
    gene="CYP2C19",
    diplotype="*2/*2",
    phenotype="Poor Metabolizer",
    activity_score=0.0,
    cpic_table_version="2022.1",
    inference_path="named_diplotype",
)
```

---

## From phenotype to recommendation

Layer 3 (future work — see `anukriti-pgx-core/PROJECT_CONTEXT.md`
§F-5) will make this a library-native API. Today the drug
recommendation lookup lives in the product layer (anukriti) and the
research layer (swarm), reading from in-tree CPIC JSON files.

For Priya, the lookup goes:

```
gene=CYP2C19, phenotype=PM, drug=clopidogrel
                      │
                      ▼
       CPIC 2022 clopidogrel guideline
                      │
                      ▼
    "Avoid clopidogrel. Use prasugrel or ticagrelor
     as an alternative antiplatelet agent.
     Recommendation: Strong. Evidence: High."
     Citations: PMID:34032273
```

That's the output. Structured record with:
- `recommendation_text` — the advice, verbatim from CPIC
- `strength` — "Strong" / "Moderate" / "Optional"
- `evidence_level` — "High" / "Moderate" / "Low"
- `citation_pmids` — PubMed IDs
- `cpic_guideline_version` — "2022.1"

None of this is inferred. All of it is looked up.

---

## Gene callers beyond CYP — the GenotypeCaller pattern

Not every pharmacogene uses star alleles. Some (VKORC1, SLCO1B1)
are defined by a single rsID's genotype directly:

- **VKORC1** is often reduced to `rs9923231` with three states: GG
  (warfarin-sensitive), GA (intermediate), AA (resistant).
- **SLCO1B1** is defined by `rs4149056` with TT (normal), TC
  (intermediate), CC (decreased function).

For these genes, pgx-core has a separate abstract base class
`GenotypeCaller` (in `calling/genotype_base.py`) with:

```python
class GenotypeCaller(ABC):
    @abstractmethod
    def call(self, variants: Mapping[str, VCFVariant]) -> Genotype:
        ...

    @abstractmethod
    def call_from_genotype_str(self, gt: str) -> Genotype:
        """Legacy path: caller is given a pre-resolved genotype string like 'TT'."""
```

Two caller patterns, one library. Why not one super-generic base
class? See `anukriti-pgx-core/PROJECT_CONTEXT.md` §D7 — the abstract
surface wider than these two patterns isn't worth it for today's
13 genes.

---

## The regression contract

Every change to a caller must preserve the byte-identical downstream
outputs we pinned in Module 02. Specifically:

- Swarm's `tests/test_star_allele_regression.py` has 12 cases pinned
  by gene + diplotype + expected phenotype. All must pass.
- Swarm's `showcase` demo produces a JSON export of exactly 1961
  bytes. One byte off is a failure.
- Anukriti's 353-test biomedical suite must still be 353/1 (the 1
  is an unrelated pre-existing gene-count assertion).

Why so strict? Because pgx-core is shared between the clinical
product and the research platform. A silent call-change in pgx-core
would ship to production the next time anukriti bumps its pin,
potentially changing a drug recommendation for a real trial. The
byte-identical regression is the brake.

If a call actually needs to change (e.g. CPIC issues a new
guideline), the change is explicit:

1. Add a new CPIC table file (`CYP2C19_named_diplotypes_v2024.1.json`).
2. Pin the new file in the engine.
3. Update the regression tests to expect the new calls.
4. Bump pgx-core to a new minor version.
5. Downstream consumers review before bumping their pin.

No silent behavior changes.

---

## Known gaps (deliberate deferrals)

From `anukriti-pgx-core/PROJECT_CONTEXT.md` §F-4:

- **CYP2D6 CNV path** (hybrid alleles *36/*69, tandem resolution,
  gene deletion). Copy-number calls require a different input
  contract than the star-allele pattern — deferred.
- **NAT2 multi-rsID haplotypes** (e.g. *5B defined by 2 rsIDs) —
  currently skipped in the basic caller; a multi-rsID haplotype
  handler is future work.
- **CYP2B6 *7 multi-rsID** — same class of gap.

These aren't bugs; they're scoped-out features. The library's
regression contract will catch anyone who accidentally claims one
is supported.

---

## Summary

You now know:

- **Two layers:** `GeneCaller` (VCF → diplotype) and `PhenotypeEngine`
  (diplotype → phenotype), both in pgx-core.
- **Named-diplotype beats additive** where CPIC has an explicit
  table entry.
- **Priya's *2/*2 → PM** via named-table lookup, activity score 0.0.
- **Recommendations are looked up, not inferred** — from pinned CPIC
  guideline tables.
- **Two caller patterns:** `GeneCaller` (star allele) and
  `GenotypeCaller` (single rsID), matching the biology.
- **Byte-identical regression contract** prevents silent behavior
  changes from shipping downstream.

Next: [Module 06 — Why Deterministic](06-why-deterministic.md). We
unpack the safety argument behind all of this.
