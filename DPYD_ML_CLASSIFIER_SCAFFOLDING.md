# DPYD Variant Pathogenicity Classifier — Baseline (scaffolding)

> **Purpose:** the ML layer of Anukriti's hybrid architecture — a baseline
> classifier that ranks DPYD variants **outside CPIC's deterministic scope** by
> predicted functional impact (novel / VUS tail). The deterministic engine
> (`anukriti-pgx-core`) stays the source of truth for CPIC-assigned variants;
> this model only triages the rest.
>
> **Status (2026-06-17):** SCAFFOLDING COMPLETE — **not trained.** Data pulled,
> pipeline written + syntax-checked + feature-eng smoke-tested. Training is
> invoked explicitly (`run.sh`), never during scaffolding, and **not** on a
> Vertex AI Workbench (avoids idle-instance billing).
>
> **Mandatory model label on any output:** *baseline classifier,
> AF + categorical features only* (SIFT / PolyPhen / CADD / conservation were
> deliberately dropped — they require dbNSFP, which is not staged).

---

## 0. Where it lives

| | |
|---|---|
| Code + local data | `anukriti/ml/dpyd-classifier/` (research repo) |
| GCS bucket | `gs://anukriti-ml-artifacts/` (created `asia-south1`, uniform access, public-access-prevention) |
| GCS prefix | `gs://anukriti-ml-artifacts/dpyd-classifier/` |
| GCP project | `project-885b39bc-9a80-45bf-bfd` (account `anukritihq@gmail.com`) |
| Compute | local **or** short-lived Cloud Run job — **NOT** Vertex Workbench |

> This is a **GCP** workload (Vertex/GCS), distinct from the AWS/Azure
> footprint elsewhere in the platform. AWS account `403732031450` is unrelated.

---

## 1. What is staged (real, provenanced)

| File | Source | Notes |
|---|---|---|
| `data/clinvar_dpyd.tsv` | ClinVar VCF (GRCh38), remote **tabix** over chr1:97,078,987–98,386,615, filtered `GENEINFO~DPYD` | **596 variants** (no full-VCF download; pysam range requests over the `.tbi`) |
| `data/cpic_dpyd_function.csv` | **CPIC v2024.01**, from the repo-pinned `anukriti-pgx-core` allele table | **13 alleles** → ground-truth labels: 4 no / 4 normal / 4 decreased / 1 unknown |
| `data/gnomad_dpyd_sas.csv` | gnomAD v4 GraphQL, **per-variant** query | scaffolding sample (cap 120: 80 in gnomAD, 40 absent); full pull at run time |
| `data/training_data.csv` | feature-eng join (smoke-test output) | 273 labeled rows |
| `data/inference_set.csv` | feature-eng join (smoke-test output) | 323 VUS/unknown rows |

### Provenance decisions
- **CPIC label source:** the official CPIC `DPYD_allele_functionality` xlsx URL
  was not resolvable (CPIC migrated to ClinPGx; the 2023 `files.cpicpgx.org`
  path 404s). The repo-pinned, version-stamped
  `anukriti-pgx-core/.../calling/data/dpyd/DPYD_alleles_anukriti_v2024.01.tsv`
  is the authoritative label source and is preferred anyway.
- **gnomAD access:** the GraphQL **region** query over the ~1.3 Mb DPYD span
  returns HTTP 502 (gateway timeout). The **per-variant** query by
  `variant_id` (`1-{pos}-{ref}-{alt}`, GRCh38, `dataset: gnomad_r4`) is
  reliable; South Asian population id = `sas`; prefer `genome.af` then
  `exome.af`. The full run iterates all ~595 ClinVar variant_ids.

---

## 2. Pipeline (code written, not run)

```
src/fetch_gnomad.py  per-variant gnomAD SAS/global AF (full, uncapped: --cap 0)
src/features.py      join ClinVar+gnomAD+CPIC -> training_data.csv + inference_set.csv
src/train.py         RF + XGBoost + LightGBM · stratified 5-fold CV ·
                     per-class F1 + macro OvR AUC-ROC · persists models + cv_metrics.json
src/infer.py         rank a candidate list across all 3 models (+ agreement, coverage gaps)
src/gcs_io.py        gcloud-storage upload helper (no gsutil)
run.sh               full orchestrator (EXPLICIT run only)
requirements.txt     pinned ML stack (sklearn 1.5.1, xgboost 2.1.1, lightgbm 4.5.0, ...)
```

### Labels (3-class)
`normal_function / decreased_function / no_function`
- Primary: CPIC allele function (joined on rsID).
- Fallback: ClinVar `CLNSIG` (pathogenic/likely_pathogenic → `no_function`;
  benign/likely_benign → `normal_function`). ClinVar **cannot** express
  "decreased" — that class is essentially CPIC-only.
- VUS / conflicting / uncertain / not_provided → **excluded from training**,
  retained in the inference set.

### Features (baseline scope)
`gnomad_global_af`, `gnomad_sas_af`, `log10_*` of each, `in_gnomad`,
`sas_enriched`, `is_indel`, one-hot `consequence` (from ClinVar MC), one-hot
`clnsig_norm`. **No SIFT/PolyPhen/CADD/conservation.**

---

## 3. Honest caveats (do NOT strip these from any report)

1. **Tiny ground truth.** CPIC assigns ~13 DPYD alleles. With 3 classes and
   AF+categorical features only, 5-fold CV is **indicative, not validating**.
   `train.py` enforces an evidence-thin guard (`MIN_PER_CLASS=5`) that **refuses
   to emit CV metrics silently** (exit 2 unless `--force`) and stamps
   `cv_metrics.json` with `"evidence_caveat": "small-N (illustrative)"`.
2. **Class imbalance surfaced at feature-build time:** of 273 labeled rows
   (14 CPIC + 259 ClinVar fallback), `decreased_function` has only **4**
   examples — the guard will trigger.
3. **No functional-prediction features** (dropped by request).
4. **Scaria et al. (2025) variant list is UNRESOLVED — blocks Steps 5 & 7.**
   The retrieval recipe `"DPYD[gene] AND Indian[title]"` does not return that
   paper's variant set, and the rsIDs were "to be resolved." `src/infer.py` is
   wired + shape-tested but needs a **real** `data/scaria_variants.csv`
   (column `rsid`, optionally `variant_id`). **No variant list was fabricated.**

---

## 4. Deliberately NOT done (and why)

- **Training** — out of scope for scaffolding; run explicitly via `run.sh`.
- **Vertex AI Workbench** — not created; persistent notebooks are the classic
  idle-bill source. Use local or Cloud Run.
- **$50 budget alert** — requires a **billing-account ID** + the
  `billingbudgets` API; an alert notifies, it does not cap spend. Pending the
  billing account ID.
- **Full gnomAD pull** — deferred to `run.sh` (`fetch_gnomad --cap 0`).

---

## 5. How to run (later, explicitly)

```bash
cd anukriti/ml/dpyd-classifier
pip install -r requirements.txt
BUCKET=gs://anukriti-ml-artifacts/dpyd-classifier ./run.sh
# Step-5 ranking runs only if data/scaria_variants.csv (a REAL list) is present.
```

Outputs a training run will add to the bucket:
`training_data.csv`, `models/{rf,xgb,lgbm}_model.pkl`,
`results/cv_metrics.json`, `results/scaria_variant_rankings.csv`.

---

## 6. To unblock the full task

1. Provide the **Scaria et al. 2025 variant list** (DOI / supplementary CSV /
   rsIDs) → drop as `data/scaria_variants.csv`.
2. Provide the **GCP billing-account ID** → set the $50 budget alert.
3. (Optional) Stage **dbNSFP** → add SIFT/PolyPhen/CADD/conservation and
   re-label the model beyond "baseline".

---

## Companion docs

- `DPYD_ONCOLOGY_DEEP_DIVE.md` · `DPYD_COMPETITIVE_LANDSCAPE.md` — domain context.
- `DETECTION_ROADMAP.md` — where the ML/novel-variant layer sits in the roadmap.
- `anukriti/ml/dpyd-classifier/README.md` — the in-repo copy of this scope.
