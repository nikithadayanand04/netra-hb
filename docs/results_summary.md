# Netra-Hb results summary

Every headline number, with the file it comes from (all paths under `outputs/`). Regenerated from a clean state on
2026-10-14 by running the README pipeline in order; all 87 tracked headline numbers were identical to the previous run.
Eye results use lab Hb (WHO < 11 g/dL); palm and nail use Ghana folder labels (file names, ~3% label noise). Eye and
palm/nail are different children, so site differences mix body site with dataset, label source and prevalence.
CV = 5 repeats x 5 folds `StratifiedGroupKFold`, mean over 25 folds [95% Nadeau-Bengio corrected interval].

## Datasets

| Item | Value | Source |
|---|---|---|
| CP-AnemiC images → after hard drops → primary (quality-clean) | 251 → 247 → **220** (93 anaemic, 42%) | `cleaning_log.csv`, `results/final.json` (`meta.n`, `meta.n_anaemic`) |
| Eye severity (primary) | 127 normal, 38 mild, 47 moderate, 8 severe | `features_cp_anemic.csv` |
| Ghana palm: originals → kept / CV groups | 524 → 522 / 501 (301 anaemic) | `results/ghana_data.json` |
| Ghana nail: originals → kept / CV groups | 533 → 530 / 514 (310 anaemic) | `results/ghana_data.json` |
| Ghana eye, secondary (not in CP-AnemiC) | 274 images / 263 groups (182 anaemic) | `results/ghana_data.json` |
| Folder label vs WHO Hb label agreement | 97.3% (214 of 220) | `results/ghana_data.json` (`label_agreement`) |
| Model inputs | 23 candidate colour features → 14 after label-free pruning; final model uses 14 (≤ 15) | `results/final.json` (`final.features`) |

## Eye models (CP-AnemiC primary, n = 220)

Tuned inside each training fold, calibrated, threshold for inner sensitivity ≥ 0.80. Source: `results/tuned_table.csv`
(stage `after`); untuned defaults at threshold 0.5 in `results/baselines_table.csv`.

| Model | ROC-AUC | Sensitivity | Specificity | PR-AUC |
|---|---|---|---|---|
| **Soft vote of top 3 (final: KNN, AdaBoost, RF)** | **0.76 [0.65–0.86]** | **0.79 [0.63–0.95]** | **0.59 [0.44–0.73]** | **0.69 [0.57–0.82]** |
| AdaBoost | 0.75 [0.66–0.85] | 0.81 [0.65–0.98] | 0.52 [0.38–0.66] | 0.70 [0.59–0.80] |
| Random forest | 0.75 [0.63–0.86] | 0.80 [0.65–0.95] | 0.54 [0.40–0.68] | 0.69 [0.55–0.82] |
| Bagging | 0.74 [0.63–0.86] | 0.79 [0.64–0.95] | 0.53 [0.40–0.66] | 0.69 [0.56–0.83] |
| Gradient boosting | 0.74 [0.62–0.85] | 0.84 [0.69–0.98] | 0.48 [0.34–0.62] | 0.69 [0.56–0.82] |
| KNN | 0.73 [0.64–0.83] | 0.76 [0.61–0.92] | 0.60 [0.45–0.76] | 0.64 [0.54–0.75] |
| Decision tree | 0.62 [0.51–0.73] | 0.86 [0.71–1.00] | 0.29 [0.03–0.54] | 0.54 [0.42–0.65] |
| Logistic regression | 0.61 [0.51–0.70] | 0.78 [0.64–0.91] | 0.34 [0.23–0.46] | 0.57 [0.45–0.68] |
| Naive Bayes | 0.57 [0.45–0.70] | 0.79 [0.62–0.95] | 0.29 [0.19–0.39] | 0.53 [0.41–0.64] |
| Untuned random forest (t = 0.5) | 0.72 [0.60–0.83] | 0.57 [0.43–0.71] | 0.71 [0.57–0.85] | 0.66 [0.54–0.79] |
| Untuned logistic regression (t = 0.5) | 0.62 [0.53–0.71] | 0.61 [0.51–0.72] | 0.55 [0.43–0.67] | 0.58 [0.47–0.69] |
| All-normal dummy | 0.50 | 0.00 | 1.00 | 0.42 |

Final model F1 0.67 [0.58–0.76], deployed threshold 0.360 (`results/final.json`). Highest ROC-AUC anywhere is 0.86
(secondary Ghana eye), below the 0.95 leakage alarm.

## Body sites

Source: `results/sites.json` (`table`, `fusion`), `results/sites/curves.csv`.

| Site | n images | ROC-AUC (tuned, all data) | Sensitivity | Specificity | ROC-AUC at n = 220 (fixed RF) |
|---|---|---|---|---|---|
| Eye (CP-AnemiC, Hb) | 220 | 0.76 [0.65–0.86] | 0.79 | 0.59 | 0.72 [0.70–0.74] |
| Palm (folder labels) | 522 | 0.80 [0.74–0.85] | 0.83 | 0.60 | 0.68 [0.61–0.71] |
| Nail (folder labels) | 530 | 0.72 [0.67–0.78] | 0.80 | 0.48 | 0.63 [0.49–0.69] |
| Eye, Ghana secondary (folder labels, 66% anaemic) | 274 | 0.86 [0.80–0.92] | 0.81 | 0.74 | 0.82 [0.78–0.86] |
| Palm + nail fusion, exploratory (508 pairs) | — | 0.80 (shift 0); 0.79 / 0.80 at shifts −1 / +1 | — | — | — |

Shifted pairs score the same as matched pairs, so the fusion gain is not evidence that two photos of one child help.
Acquisition-only models (tissue area + glare) score 0.45–0.51 on the Ghana sets (`results/sites/checks.json`).

## Clustering (K-means, Unit V)

Source: `results/clustering.json`.

| Item | Value |
|---|---|
| Eye: k by elbow / silhouette / chosen | 5 / 2 / 5 (14 scaled features, n = 220) |
| Eye k = 5 groups (n, mean Hb, % anaemic) | Pink 38, 10.2, 63%; Pale 58, 10.7, 57%; Very pale 48, 11.0, 38%; Red 19, 11.2, 32%; Intermediate 57, 12.0, 21% |
| Eye k = 5 Hb difference | Kruskal–Wallis p = 0.0007; entropy 1.42 vs null 1.50 bits (p < 0.001); ARI with severity 0.04 |
| Eye k = 5 severity purity | 0.58 = majority baseline (p = 1.0); binary purity 0.66 |
| Palm k = 5 purity (n = 501) | 0.61 vs baseline 0.57, p = 0.001 |
| Nail k = 5 purity (n = 514) | 0.58 = baseline 0.58, p = 1.0 |

## Cheapest screening protocol (search)

Objective: specificity at sensitivity ≥ 0.80 (3-fold grouped CV logistic regression) − 0.02 × photo cost − 0.005 ×
features. Source: `results/search.json` (`table`, `nested`), `results/search_table.csv`, `results/search_trace_*.json.gz`.

| Algorithm | Best score | Best protocol | Evaluations | Optimum found (10 seeds) |
|---|---|---|---|---|
| BFS / IDDFS / A* (admissible) | 0.437 | eye: R_med, hsv_s_med, chrom_r_p90 (specificity 0.51) | 22,402 | 100% |
| Local beam | 0.437 | same; first reached at evaluation 957 of a 1,321-evaluation run | 1,321 | 90% |
| Hill climbing | 0.413 | eye: G_med, lab_L_med, chrom_r_p90 | 1,785 | 70% |
| Simulated annealing | 0.405 | eye: chrom_r_med, lab_L_med, chrom_r_p90 | 907 | 70% |
| Genetic algorithm | 0.413 | eye: G_med, lab_L_med, chrom_r_p90 | 446 | 30% |
| A* (inadmissible, resubstitution) | 0.402 | eye: R_med, chrom_r_p90 | 16,321 | 0% |
| **Honest nested re-evaluation (local beam, 1 × 5 outer)** | inner 0.50 → held-out **0.31** | held-out ROC-AUC 0.60, sensitivity 0.70, specificity 0.46; eye chosen 5 of 5 | — | — |
| Held-out score restricted to one site (after cost) | nail 0.33, palm 0.28, palm+nail 0.24, eye 0.22 | fold SD up to 0.14 | — | — |

## Screen page models and safeguards

Source: `results/screen_models.json` (built by `scripts.build_screen_models`), `results/safeguards.json`
(`scripts.check_safeguards`), `app/samples/samples.json`.

| Item | Value |
|---|---|
| Eye bundle | the final model above; threshold 0.360; colour-to-Hb map error ±1.50 g/dL (cross-validated MAE) |
| Palm / nail bundles (same procedure, folder labels) | out-of-fold ROC-AUC 0.79 / 0.71 (1 × 5 grouped); thresholds 0.506 / 0.495 |
| Makeup / lash filter (V < 0.30 and S < 0.40) | removes 0.06% of real CP eyelid pixels (max 1.9% in one image); 0 of 220 images over the 15% warning |
| Rejected skin-tone rule (Lab a* < 15) | would wrongly remove 9.0% of real eyelid pixels (limit was 5%) |
| KNN unfamiliar-photo thresholds (k = 5, 95th percentile) | eye 3.09, palm 2.12, nail 2.28 |
| KNN check on the eye refer sample: flagged | cool webcam cast (3.63), warm indoor light (4.89), nail refer sample offered as an eye (4.45) |
| KNN check: missed | washed out (2.42), box half skin (1.50), palm refer / normal samples (1.94 / 2.14), nail normal sample (1.38) |
| Demo samples (out-of-fold scores) | eye 81% refer / 12% normal; palm 66% / 28%; nail 74% / 20%; all correct |

The KNN check is photo-dependent: it catches strong colour casts but not wrong-site photos in general. Results are
"Low confidence" when it fires or the age band is outside 6–59 months (all training data is children under 5).
