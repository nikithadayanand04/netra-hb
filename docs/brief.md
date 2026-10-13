# Netra-Hb — Final Project Brief

## 1. Context
- Course: IS353IA Artificial Intelligence and Machine Learning (Semester V, CSE, RVCE), Lab Part-B
- Team: 2 students, same batch
- Domain: Health Care (allowed Part-B domains: Agriculture, Health Care, Manufacturing, Automobiles, Process Control/Automation; Indian scenarios preferred)
- Part-B must show: (1) data cleansing and pre-processing, (2) complete EDA, (3) algorithm selection and model building, (4) evaluation with proper metrics, (a) prediction/classification results, (b) a GUI demo
- Experiential Learning evaluation: case study (10), program-specific requirements (10), video/presentation/demo (10), designing and modelling (10); Phase 2 is an exhibition with a working demo

## 2. Problem statement
Anaemia affects a majority of Indian women and children. Confirming it needs a finger-prick and Hb test strips, which ASHA workers often run short of. Clinicians already judge anaemia by the pallor of the inner eyelid (conjunctiva), palms and nail beds, but by eye this is subjective. Netra-Hb turns phone photos of these sites into an objective, needle-free "Refer for Hb test / Normal" screening decision using classical, explainable ML.

**Title:** Netra-Hb: Multi-Site, Lighting-Robust Anaemia Screening from Smartphone Photos Using Classical Machine Learning

## 3. Objectives
1. Build a cleansed, patient-level colour-feature dataset from eye, palm and nail images with lab Hb labels.
2. Compare syllabus classifiers for anaemic vs normal screening under heavy class imbalance.
3. Identify which body site (eye / palm / nail / fusion) screens best on Indian data.
4. Use search (hill climbing / GA) to find the cheapest photo protocol meeting a sensitivity floor.
5. Test generalisation across datasets, comparing raw vs normalised features (grey-world now; sclera normalisation is future work because no available image shows the sclera).
6. Deliver a Streamlit screening app for the exhibition.

## 4. Datasets
| Role | Dataset | Details | Access |
|---|---|---|---|
| **Planned primary (access pending)** | Non-Invasive Anemia Screening Using Conjunctiva, Palm and Nail-Bed Images (IEEE DataPort, Aug 2026, DOI 10.21227/n7km-nr64) | 1,485 Indian adults, Manav Rachna (Faridabad) blood donation camp; L/R conjunctiva, L/R palm, up to 10 nail images per person; lab Hb 6.0–18.7 g/dL; 166 anaemic / 1,318 non-anaemic (WHO Hb < 12); Patient_Info.csv keyed by patient ID (P001…) | IEEE DataPort subscription (IEEE Society members / institutional) |
| **External test (access pending)** | Eyes-defy-anemia (IEEE DataPort) | 218 eye photos: 95 India (Chennai) + 123 Italy (Bari); hand-segmented palpebral, forniceal, forniceal_palpebral PNGs (1067×800); lab Hb, age, sex in xlsx | IEEE DataPort subscription |
| **Eye, in use** | CP-AnemiC (Mendeley, DOI 10.17632/m53vz6b7fx.1) | Published as 710 children 6–59 months, Ghana; the release we have holds 251 segmented conjunctiva images with Hb (no age/sex); 220 quality-clean images (93 anaemic at WHO Hb < 11) are the primary eye set | Free |
| **Palm and nail, in use** | Ghana palm and fingernail sets (Mendeley, same group) | Children ≤5 y; ~4,260 files each, ~88% rotated/exact copies. After keeping base-named originals and merging re-crops: palm 522 images / 501 groups, nail 530 / 514. **No Hb**: labels come from file names (folder labels), which agree with WHO Hb labels on 97.3% of the CP-AnemiC overlap. Palm and nail pair only by file number (exploratory) | Free |
| Eye, secondary only | Ghana conjunctiva set (Mendeley, same group) | Contains 220 of the 251 CP-AnemiC images; the 274 non-CP originals (`eye_extra`) are a folder-label secondary analysis, never pooled with CP-AnemiC | Free |
| Optional (nail/palm) | Peru multimodal dataset | 909 young adults; fingertip/palm videos, nail photos; age, sex, Hb | See paper |

**Plan:** Eye models run on CP-AnemiC (Hb labels) and palm/nail models on the Ghana sets (folder labels) now; the site comparison reports each site with its label source and an equal-sample-size comparison, since the sites come from different children and datasets. Switch to MREI (one cohort, all three sites, lab Hb) when access arrives; keep Eyes-defy-anemia untouched as the external test.

**Sclera:** none of the available images shows the sclera (all are pre-segmented conjunctiva, palm or nail crops), so sclera normalisation is future work, to be tested on MREI or Eyes-defy-anemia; grey-world normalisation is used meanwhile.

WHO Hb cut-offs (g/dL): children 6–59 months < 11; 5–11 y < 11.5; 12–14 y < 12; non-pregnant women ≥15 y < 12; men ≥15 y < 13. Use sex/age-specific cut-offs where metadata exists. Severity (adults): mild 11–11.9 (women) / 11–12.9 (men), moderate 8–10.9, severe < 8.

## 5. Novelty
1. **Which body site works best for an ASHA worker?** Eye vs palm vs nail vs fusion with classical ML (open question noted in a 2025 rural-Gujarat study protocol). Now: CP-AnemiC eye vs Ghana palm/nail, at full and equal sample size with learning curves, plus exploratory palm+nail fusion with a ±1 file-number shift control; on Indian data once MREI arrives.
2. **Sclera as a built-in white reference (future work: needs MREI / Eyes-defy images, as no current data shows the sclera).** The sclera is melanin-free; normalise eyelid colour by sclera colour from the same photo for lighting- and skin-tone-robust features without deep learning. Positioning: the Bari group published sclera *segmentation* on Eyes-defy-anemia; we use the sclera for *normalisation* and test cross-dataset transfer. Fallback if the sclera isn't visible: grey-world normalisation.
3. **Cheapest screening protocol.** Hill climbing / GA over site+feature subsets: maximise sensitivity-weighted score minus photo/time cost (syllabus Units I–II).
4. **Generalisation.** Train MREI (Faridabad), test Eyes-defy India (Chennai), Italy, CP-AnemiC; raw vs normalised.

## 6. Method (syllabus mapping)
- **Features per region:** mean/median R, G, B; LAB (L*, a*, b*); HSV; erythema index; a*/L*; R/G; region ÷ sclera ratios (eye). Aggregate per patient (mean over L/R eyes, palms, up to 10 nails).
- **Feature budget:** ≤ ~15 features (≈10 anaemic cases per feature with 166 positives).
- **Classifiers (Units III–IV):** Decision Tree, KNN, Naive Bayes, Logistic Regression, Bagging, Boosting, Random Forest.
- **Clustering (Unit V):** K-means / bisecting K-means pallor groups; validity via silhouette, SSE, and agreement with true Hb bands.
- **Search (Units I–II):** hill climbing / GA for site+feature selection; threshold tuning for the sensitivity floor.
- **Secondary:** Hb regression to output a severity band (caveated; few severe cases).
- **Performance strategy (syllabus-only):** tune hyperparameters inside nested grouped CV; GA/hill-climbing feature selection; class weights / SMOTE inside folds; tune bagging, boosting and random forest; soft-voting ensemble of the best syllabus models; decision-threshold tuning to the sensitivity floor; probability calibration; modality fusion (eye + palm + nail).

## 6a. Syllabus coverage map (IS353IA)
| Unit | Syllabus topic | Where it appears in Netra-Hb |
|---|---|---|
| I | Intelligent agents, rationality, environment | Report framing: the screening app as an agent (percepts = photos, action = refer/normal, performance measure = sensitivity at a cost) |
| I | Uninformed search (BFS, DFS, IDDFS) | Baseline exhaustive search over small site/feature subsets, compared against local search |
| II | Local search: hill climbing, simulated annealing, local beam, genetic algorithms | Feature selection and cheapest-protocol optimiser; compare all four on the same objective |
| II | A* / heuristics | Optional: A* over protocol subsets with photo-cost path cost and an optimistic sensitivity heuristic |
| II | Adversarial search (minimax, alpha-beta) | Not applicable to this problem (covered in Part-A labs) |
| III | Decision tree: attribute test conditions, Gini/entropy/gain ratio, induction | Decision tree classifier; compare split criteria; visualise the tree as an explainable screening rule |
| III | Overfitting, model selection, validation set, model complexity, statistical bounds | Depth/pruning curves (train vs validation), nested grouped CV, 95% CIs on metrics |
| IV | Nearest neighbour classifiers | KNN with k and distance tuning, scaling effects |
| IV | Naive Bayes | Gaussian NB on colour features; check the independence assumption via the correlation heatmap |
| IV | Logistic regression | LR coefficients as interpretable pallor weights |
| IV | Ensembles: bagging, boosting, random forest | Tuned bagging, boosting, RF; soft-voting ensemble |
| V | K-means, bisecting K-means, strengths/weaknesses | Pallor clusters on colour features |
| V | Cluster evaluation: cohesion/separation (SSE, silhouette), proximity matrix, number of clusters, supervised measures | Elbow + silhouette for k; sorted proximity-matrix plot; purity/entropy against true Hb bands |

**From scratch (Part-A rule "no direct APIs", applied for extra credit):** implement Logistic Regression, Naive Bayes, KNN and K-means in NumPy, display all model parameters, and verify outputs against scikit-learn.

## 7. Part-B checklist
- **Cleansing:** drop blurred/over-exposed images; mask specular glare (near-white pixels); handle missing modalities; derive sex/age-specific labels; check duplicate images.
- **EDA:** Hb distribution by dataset/sex/age; class balance; colour feature vs Hb scatter; per-site separability; histograms before/after normalisation; correlation heatmap.
- **Evaluation rules:**
  - Stratified, patient-grouped 5-fold CV (all images of one patient in the same fold) with 95% CIs
  - Report sensitivity, specificity, ROC-AUC, PR-AUC, F1, confusion matrix; never accuracy alone (all-normal baseline ≈ 89%)
  - SMOTE / class weights only inside training folds
  - No colour augmentation (brightness/hue jitter destroys the pallor signal)
  - Cross-dataset results table (raw vs grey-world normalised; sclera-normalised once data allows)
  - Site comparison: always state each site's dataset and label source (Hb vs folder label)
- **Target:** sensitivity ≥ 80% with specificity ~70–80%, framed as screening ("Refer for Hb test"), not diagnosis.
- **GUI (Streamlit, custom-themed, exhibition-grade):**
  - Screening flow: camera capture or upload for eye, palm and nail; click-to-select ROI and sclera on the image; animated risk gauge; severity band; "Refer for Hb test / Normal" card; top contributing features in plain language.
  - Live lighting demo: side-by-side raw vs sclera-normalised colour patches and how the prediction changes.
  - Model lab: pick a classifier, adjust the decision threshold with a slider, and watch sensitivity, specificity, confusion matrix and ROC point update live.
  - Insights: interactive EDA (Hb distributions, feature vs Hb), K-means pallor clusters, body-site comparison, cross-dataset results.
  - Protocol optimiser: animate the hill-climbing/GA search converging on the cheapest photo protocol.
  - Stack: Streamlit + Plotly + streamlit-image-coordinates + custom CSS theme; responsive; sample patients preloaded for a smooth demo.

## 8. Work split
- **Person A:** ROI and sclera extraction, colour features, normalisation, cleansing, EDA, K-means.
- **Person B:** classifiers, grouped CV, cross-dataset experiments, protocol search, Streamlit GUI.
- **Shared:** report, presentation, demo video.

## 9. Milestones
1. Week 1: IEEE DataPort access requested; CP-AnemiC downloaded; feature-extraction script working.
2. Week 2: EDA and baseline classifiers on CP-AnemiC.
3. Week 3: MREI features (all sites), grouped CV, site comparison.
4. Week 4: sclera normalisation, cross-dataset tests, protocol search.
5. Week 5: Streamlit GUI, report, slides, demo video.

## 10. Risks
- IEEE DataPort access delay: develop on CP-AnemiC first.
- Heavy imbalance (11% anaemic): sensitivity-focused metrics, threshold tuning.
- No sclera in any currently available image; MREI eye photos may not show enough sclera either: inspect ~10 samples; fall back to grey-world.
- Ghana palm/nail labels are folder labels without Hb (~3% disagreement with WHO Hb labels measured on the CP overlap), and per-child linkage across sites is undocumented: palm/nail results and fusion are reported as such.
- Eye (CP-AnemiC) and palm/nail (Ghana) come from different children, so site differences mix body site with dataset effects until MREI.
- Blood-donor population skews toward healthy adults; Eyes-defy and CP-AnemiC differ in age and device. State as limitations.

## 11. References
- MREI multimodal dataset: https://ieee-dataport.org/documents/dataset-non-invasive-anemia-screening-using-conjunctiva-palm-and-nail-bed-images-0
- Eyes-defy-anemia: https://ieee-dataport.org/documents/eyes-defy-anemia
- CP-AnemiC: https://data.mendeley.com/datasets/m53vz6b7fx
- Ghana fingernail dataset: https://data.mendeley.com/datasets/2xx4j3kjg2 (palm and conjunctiva sets are by the same group on Mendeley)
- Peru multimodal dataset: https://revistas.unsm.edu.pe/index.php/rcsi/article/download/955/1462/5044
- Bari sclera segmentation (BSPC): https://ricerca.uniba.it/retrieve/81e3cc44-517a-4bb3-b8f8-dc4a067338a3/1-s2.0-S1746809422009430-main.pdf
- Illumination-robust conjunctival preprocessing (iJOE 2025): https://online-journals.org/index.php/i-joe/article/view/54439
- Multi-modal anaemia screening protocol, rural India (medRxiv 2025): https://www.medrxiv.org/content/10.1101/2025.04.10.25325591.full.pdf
- Smartphone conjunctiva anaemia detection (HIR 2025): https://pmc.ncbi.nlm.nih.gov/articles/PMC11854623
