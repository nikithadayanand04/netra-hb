# Netra-Hb

Needle-free anaemia screening from smartphone photos of the conjunctiva, palm and nail bed, using classical (non-deep) machine learning.

RVCE IS353IA Artificial Intelligence and Machine Learning, Lab Part-B (Health Care domain), 2-person team.

> **Screening aid, not a diagnosis.** Netra-Hb outputs "Refer for Hb test" or "Normal". It is a research and coursework prototype, has not been clinically validated, and must not be used to make treatment decisions. A positive or negative result should always be confirmed with a laboratory or point-of-care haemoglobin test.

## Problem

Anaemia affects a majority of Indian women and young children. Confirming it needs a finger-prick and Hb test strips, which community health workers (ASHAs) often run short of. Clinicians already judge anaemia by the pallor of the inner eyelid, palms and nail beds, but by eye this is subjective. Netra-Hb turns colour measurements from phone photos of these sites into an objective, explainable referral decision.

## Approach

Every learned step (scaling, SMOTE, feature pruning, threshold, calibration) is fitted inside the training fold. Evaluation is repeated stratified, patient-grouped cross-validation (5 repeats x 5 folds, `StratifiedGroupKFold`), and the headline is the mean over 25 folds with a 95% Nadeau-Bengio corrected interval. Sensitivity, specificity, ROC-AUC, PR-AUC and F1 are reported, never accuracy alone. No colour augmentation is used, because it would destroy the pallor signal.

| IS353IA unit | Topic | Where it is used |
|---|---|---|
| I | Intelligent agents | The screening app framed as an agent: percepts = photos, action = refer / normal |
| I | BFS, IDDFS | Exhaustive search over small protocols (site + up to 3 features): ground truth for the search comparison |
| II | Hill climbing, simulated annealing, local beam, genetic algorithm | "Cheapest screening protocol" optimiser, all on the same objective |
| II | A* | Protocol search with photo + feature cost as path cost and an admissible heuristic |
| III | Decision tree, overfitting, model selection | Gini vs entropy trees, depth curves, nested grouped CV, corrected CIs |
| IV | KNN, Naive Bayes, logistic regression, bagging, boosting, random forest | Classifier comparison and a tuned soft-voting ensemble |
| V | K-means, bisecting K-means, cluster validity | Pallor clusters with elbow, silhouette, proximity matrix, purity against Hb bands |

Features are colour statistics of the masked tissue (median and percentiles of RGB, chromaticity, CIELAB, HSV, erythema index, a*/L*), with specular glare and background removed. The final model uses at most ~15 features. Logistic regression, Naive Bayes, KNN and K-means are also implemented from scratch in NumPy (`src/netra/scratch/`) and tested against scikit-learn.

## Datasets

**Data is not included in this repository.** Download each dataset yourself, respect its licence, and place it under `data/` as shown. The paths are set in `config.py`.

| Role | Dataset | Labels | Link |
|---|---|---|---|
| Eye (in use) | CP-AnemiC: conjunctiva images of children 6-59 months, Ghana | Lab Hb, WHO cut-off < 11 g/dL | Mendeley Data, DOI [10.17632/m53vz6b7fx.1](https://doi.org/10.17632/m53vz6b7fx.1) |
| Nail (in use) | *Detection of Anemia using Colour of the Fingernails Image Datasets from Ghana* | Folder (file-name) labels, no Hb | [data.mendeley.com/datasets/2xx4j3kjg2](https://data.mendeley.com/datasets/2xx4j3kjg2) |
| Palm (in use) | *Anemia Detection using Palpable Palm Image Datasets from Ghana* (same group) | Folder labels, no Hb | Search the title on [Mendeley Data](https://data.mendeley.com) |
| Eye, secondary only | *Application of Machine Learning in Detecting Iron Deficiency Anemia Using Conjunctiva image Dataset from Ghana* (same group) | Folder labels | Search the title on Mendeley Data |
| Planned primary (access pending) | Non-Invasive Anemia Screening Using Conjunctiva, Palm and Nail-Bed Images (Indian adults, Faridabad) | Lab Hb | IEEE DataPort, DOI [10.21227/n7km-nr64](https://doi.org/10.21227/n7km-nr64) |
| Planned external test (access pending) | Eyes-defy-anemia (India + Italy) | Lab Hb | [IEEE DataPort](https://ieee-dataport.org/documents/eyes-defy-anemia) |

Expected layout:

```
data/
  cp_anemic/
    All Categories/                 # the 251 segmented conjunctiva images
    Cp-Anaemic Dataset.xlsx         # Hb per image
  ghana_palm/Anemia Detection using Palpable Palm Image Datasets from Ghana/Palm.rar
  ghana_nail/Detection of Anemia using Colour of the Fingernails Image Datasets from Ghana/Fingernails.rar
  ghana_eye/Application of Machine Learning in Detecting Iron Deficiency Anemia Using  Conjunctiva image Dataset from Ghana/
```

Note the double space in the Ghana conjunctiva folder name: it matches the download. `scripts.extract_ghana` unpacks the two RAR files with `bsdtar`, which ships with macOS. On Linux, install `libarchive-tools`.

Data caveats that shape every result:

- **Ghana palm and nail sets have no Hb.** Their labels come from file names. On the CP-AnemiC images that also appear in the Ghana eye set, these folder labels agree with WHO Hb labels 97.3% of the time (label-noise estimate ~3%). Results on these sets are marked "folder labels".
- **About 88% of Ghana files are rotated or exact copies.** Only base-named originals are used. Rotation- and mirror-invariant duplicate re-crops share a CV group, and duplicates with conflicting labels are dropped.
- **The Ghana eye set largely contains CP-AnemiC** (220 of its images). Its remaining images are a secondary, folder-label analysis only, never pooled with CP-AnemiC.
- **Eye cannot be linked to palm or nail,** because they come from different children. Palm and nail can be paired only by file number, since child identity is not documented. Palm + nail fusion is therefore exploratory and always reported with a ±1 file-number shift control.
- **No image shows the sclera,** so sclera-based colour normalisation is future work. Grey-world normalisation is the fallback.

## Setup

Python 3.11.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

## How to run

Run the scripts from the repository root, in this order. Each step writes CSVs, JSON results and figures to `outputs/`.

| Step | Command | What it does |
|---|---|---|
| 1 | `python -m scripts.extract_features` | CP-AnemiC: WHO labels, masking, quality flags, duplicate check, colour features -> `outputs/features_cp_anemic*.csv` |
| 2 | `python -m scripts.prune_features` | Label-free redundancy pruning; prints the feature list stored as `MODEL_FEATURES` in `config.py` |
| 3 | `python -m scripts.train_baselines` | All syllabus classifiers + from-scratch versions, 5x5 grouped CV -> `outputs/results/baselines.json` |
| 4 | `python -m scripts.tune_models` | Nested tuning, threshold for the sensitivity floor, soft vote of the top 3 -> `outputs/results/final.json`, `outputs/models/final.joblib` |
| 5 | `python -m scripts.extract_ghana` | Unpacks the Ghana sets, keeps originals, groups duplicates, extracts features |
| 6 | `python -m scripts.compare_sites` | Eye vs palm vs nail, equal-n learning curves, palm+nail fusion with the shift control -> `outputs/results/sites.json` |
| 7 | `python -m scripts.run_search` | Cheapest-protocol search: 8 search algorithms compared, plus a nested honest re-evaluation -> `outputs/results/search.json`, `search_trace_<algo>.json.gz` (~5 min) |
| 8 | `python -m scripts.build_screen_models` | Screen-page bundles per site (eye = P6 model; palm, nail = same procedure on folder labels) with out-of-fold scores for the uncertainty band -> `outputs/models/screen_<site>.joblib` (~4 min) |
| 9 | `python -m scripts.make_samples` | The 6 demo patients in `app/samples/` (one refer and one normal per site, each correct out-of-fold) |

`compare_sites` and `run_search` accept stage names to run part of the pipeline, for example `python -m scripts.run_search report`. Optional extras: `scripts.inspect_images` (sample image grid) and `scripts.plot_scratch_logreg` (from-scratch loss curve). The notebooks `notebooks/01_eda.ipynb` (EDA) and `notebooks/02_clustering.ipynb` (K-means, Unit V) import from `src/netra`.

Search traces load with:

```python
from netra.search import load_trace
t = load_trace("simulated_annealing")   # meta, summary, feature_names, columns, evaluations, steps
```

**App:** the Streamlit screening app (`streamlit run app/Home.py`) is not built yet. `app/` is a placeholder.

## Key results

All numbers are from repeated grouped cross-validation on small datasets. Eye results use Hb labels; palm and nail results use folder labels. Eye and palm/nail come from different children and datasets, so differences between sites mix body site with dataset, label source and prevalence. No external test has been run yet.

**Eye (CP-AnemiC, n = 220, 93 anaemic, WHO Hb < 11 g/dL).** 5x5 grouped CV, mean over 25 folds [95% corrected CI]:

| Model | Sensitivity | Specificity | ROC-AUC | PR-AUC |
|---|---|---|---|---|
| Logistic regression (untuned) | 0.61 [0.51-0.72] | 0.55 [0.43-0.67] | 0.62 [0.53-0.71] | 0.58 [0.47-0.69] |
| Random forest (untuned) | 0.57 [0.43-0.71] | 0.71 [0.57-0.85] | 0.72 [0.60-0.83] | 0.66 [0.54-0.79] |
| **Tuned soft vote of top 3, threshold for sensitivity ≥ 0.80** | **0.79 [0.63-0.95]** | **0.59 [0.44-0.73]** | **0.76 [0.65-0.86]** | **0.69 [0.57-0.82]** |

**Body site comparison** (same tuned procedure per site, ROC-AUC [95% corrected CI]):

| Site | Data | n images | ROC-AUC |
|---|---|---|---|
| Eye | CP-AnemiC, Hb labels | 220 | 0.76 [0.65-0.86] |
| Palm | Ghana, folder labels | 522 | 0.80 [0.74-0.85] |
| Nail | Ghana, folder labels | 530 | 0.72 [0.67-0.78] |
| Palm + nail fusion (exploratory, fixed random forest per site) | paired by file number | 508 pairs | 0.80 at shift 0; 0.79 and 0.80 at shifts -1 and +1 |

The fusion gain does not depend on correct pairing (shifted pairs score the same), so it is no evidence that two photos of the same child help.

**Cheapest screening protocol** (objective = specificity at sensitivity ≥ 0.80 from 3-fold grouped CV logistic regression, minus 0.02 x photo cost (eye 3, palm 1, nail 1) and 0.005 per feature):

- Exhaustive search finds an eye protocol (3 features, specificity 0.51) as the in-sample optimum. Local beam search reaches it with 1,321 of 22,402 evaluations (9 of 10 seeds). Hill climbing and simulated annealing reach it in 7 of 10 seeds, the genetic algorithm in 3 of 10. A* with a provably admissible heuristic cannot prune and evaluates everything. A tighter, inadmissible heuristic misses the optimum.
- **Search optimism is large.** Rerunning the search inside the training folds of a 1x5 outer CV, the in-sample score of 0.50 falls to 0.31 on held-out folds, with sensitivity 0.70, below the 0.80 target. The chosen features change every fold.
- Restricted to one site, the honest held-out scores (after cost) are nail 0.33, palm 0.28, palm+nail 0.24 and eye 0.22. Eye's in-sample win is mostly selection optimism on the smallest dataset. Fold-to-fold spread is large (SD up to 0.14).

**Overall:** at sensitivity ≈ 0.8, specificity is around 0.45-0.6, so many healthy children would be referred. This is a screening aid to prioritise Hb testing, not a replacement for it.

## Project structure

```
config.py             paths, thresholds, seeds, costs (edit here, not in code)
src/netra/            library: labels, masks, features, normalise, cleaning, ghana, models, tuning,
                      evaluate, clustering, search, scratch/ (NumPy LogReg, NB, KNN, K-means)
scripts/              command-line entry points (python -m scripts.<name>)
notebooks/            EDA and clustering notebooks
tests/                pytest suite
outputs/results/      JSON/CSV results and search traces (tracked)
outputs/figures/      figures (tracked)
outputs/models/       saved models (not tracked)
app/                  Streamlit app (to be built)
docs/brief.md         full project brief
data/                 datasets (not tracked, see Datasets)
```

## Acknowledgements

Images and labels come from the CP-AnemiC and Ghana conjunctiva, palm and fingernail datasets published on Mendeley Data. Please cite those datasets when using this work. A few sample crops appear in `outputs/figures/samples.png` and the notebooks for illustration.
