# Session Resume — 2026-06-18

> DPYD ML classifier: v2 retrain → v3 VEP/AlphaMissense annotation →
> Hugging Face model backup. Successor to `SESSION_RESUME_2026-06-14.md`.
> Resume with: "continue from SESSION_RESUME_2026-06-18.md".

---

## TL;DR

| # | Workstream | Result |
|---|---|---|
| 1 | Classifier **v2** | +Offer 2014 + PharmVar, SMOTE, domain feats → `decreased_function` F1 **0.0 → 0.66** |
| 2 | Classifier **v3** | +VEP/AlphaMissense annotations → AM a live feature (imp 0→0.01); **0/25 Scaria class changes** (root-caused) |
| 3 | HF backup | All 3 versions + model card pushed to **huggingface.co/abhimanyu12/dpyd-classifier** |

All on the **`clinical-grade-pgx`** branch of the `anukriti` repo (pushed to origin).
GCS artifacts under `gs://anukriti-ml-artifacts/dpyd-classifier/` retained.

---

## 1. Classifier v2 — class imbalance fixed (commit `43a520f`)

The v1 baseline could not predict `decreased_function` (4 examples, F1=0.0).

- **Data:** training set 273 → **392 rows**. Merged 37 Offer et al. 2014
  functional-assay rows (6 `increased_function` dropped, out of 3-class scope)
  + 82 PharmVar alleles with non-empty `functional_class`.
  `decreased_function` count **4 → 23**.
- **Features:** `aa_position` (0 sentinel), `domain_encoded`
  (I=1/II_III=2/IV=3/V=4/splice·intronic=5/unknown=0), `activity_pct`
  (-1 sentinel).
- **Imbalance:** RF+LGBM `class_weight="balanced"`; XGB balanced per-sample
  weights (the multiclass analog of `scale_pos_weight`, which is binary-only and
  a no-op under `multi:softprob`); **SMOTE on the train fold only**;
  `MIN_PER_CLASS` guard 5 → 3.
- **Result (5-fold CV):** acc ~0.90, macro AUC ~0.96, `decreased_function`
  F1 **rf 0.63 · xgb 0.66 · lgbm 0.60** (was 0.0). Artifacts → `gs://…/v2/`.

## 2. Classifier v3 — VEP/AlphaMissense annotation (commit `88f01b2`)

Goal: close the "sentinel gap" so the 25 Scaria (novel Indian DPYD) variants
get real protein-level features instead of sentinels.

- **`ml/annotate_variants_vep.py`** — Ensembl VEP REST per-variant (canonical
  transcript) → `aa_position`, domain bucket, AlphaMissense, CADD, SIFT,
  PolyPhen, `vep_consequence`. Lazy AlphaMissense **Zenodo fallback**
  (stream-filter to the DPYD locus) for any missense variant VEP misses.
- **`ml/data/scaria_variants_annotated.csv`** — 25 variants. **20/25 have real
  AlphaMissense** (all missense); 5 do not (4 splice/intronic + 1 frameshift
  `c.1970delC` — AlphaMissense scores missense only, so −1 is correct, not a gap).
  `c.704G>A` AM = **0.9285** (>0.564 ✓).
- **`ml/data/alphamissense_dpyd.tsv`** — DPYD-locus AlphaMissense table
  (validated: all 20 missense scores match VEP exactly).
- **Training set annotated too** (the actual fix): the 21 missense ClinVar/CPIC
  rows got real AM (+CADD/SIFT/PolyPhen). This gave AM real variance in training
  → importance **0.0 → 0.0104** (model now uses it). v1/v2 had it constant.
- **Retrain v3:** 392 rows, 32 features, acc ~0.90, AUC ~0.96, `decreased` F1
  0.60–0.63. Artifacts → `gs://…/v3/`.

### Honest outcome — success metric NOT met
**0/25 Scaria variants changed class**; all stay `no_function` at prob 0.87–0.94.
Root cause (diagnosed, not a bug): predictions are dominated by
`clnsig_norm_likely_pathogenic` (~16%) and `activity_pct` (~15%), both **sentinels
for every Scaria variant**. AM's learned weight (~1%) can't overcome that margin.
`c.704G>A` was already `no_function`, so higher AM reinforces rather than changes it.

`cv_metrics_v3.json` `evidence_caveat` records the **two-tier recommendation**:
for novel population-discovery variants (no ClinVar significance / measured
activity), **use the raw AlphaMissense score directly**, not the classifier.

> Deferred (separate model-design question, not a patch): dropping
> `activity_pct` / `clnsig_norm` so the model must rely on populated biological
> features. Not pursued.

## 3. Hugging Face backup

- **Repo:** https://huggingface.co/abhimanyu12/dpyd-classifier (public, model).
  > Requested namespace `abhimanyurb` was not writable by the available token
  > (account `abhimanyu12`, no orgs); published under `abhimanyu12`. Rename/
  > transfer in HF settings if `abhimanyurb` is wanted.
- **Layout:** `v1/` `v2/` `v3/` (each = rf/xgb/lgbm `.pkl` + `results/`),
  plus shared `src/`, `data/`, `run.sh`, `requirements.txt`, and the model card
  `README.md`. v1 came from the GCS **bucket root** (no `v1/` folder there);
  reorganized into a clean `v1/` for HF.
- **Source:** downloaded from GCS via `gcloud storage cp` (`gsutil` not
  installed). **GCS copies retained** — both stores hold all three versions.

---

## State / artifacts

| Where | What |
|---|---|
| `anukriti` repo, `clinical-grade-pgx` (pushed) | v2 `43a520f`, v3 `88f01b2` |
| `anukriti_docs`, `main` | `DPYD_ML_CLASSIFIER_SCAFFOLDING.md` (v2 section), this resume |
| `gs://anukriti-ml-artifacts/dpyd-classifier/` | root=v1, `v2/`, `v3/` |
| huggingface.co/abhimanyu12/dpyd-classifier | v1/v2/v3 + model card |
| local `dpyd_models_backup/` | the reorganized upload tree (untracked) |

## Follow-ups
1. **Rotate the HF token** — it was shared in plaintext this session.
2. Verify the model-card Zenodo DOI (`10.5281/zenodo.20727790`) resolves before
   relying on it publicly.
3. Update `DPYD_ML_CLASSIFIER_SCAFFOLDING.md` with a v3 section (currently only
   through v2).
4. If a class change on novel variants is truly wanted, evaluate the deferred
   feature-set redesign (drop sentinels-dominant features).
