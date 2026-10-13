import html

import streamlit as st

import art
import ui

ui.setup_page("nav_about", "pages/4_About.py")
m = ui.mode()
ui.page_title(ui.t("about_title"), ui.t("about_lede"), art.img(art.header("about", m)))


def prose(*paras: str) -> None:
    st.html('<div class="nh-prose">' + "".join(f"<p>{p}</p>" for p in paras) + "</div>")


ui.section("The problem")
prose("Anaemia affects a majority of Indian women and young children. Confirming it needs a finger-prick and Hb "
      "test strips, which community health workers (ASHAs) often run short of. Health workers already judge pallor by eye, from the inner "
      "eyelid, palm and nail bed, but that judgement is subjective.",
      "Netra-Hb asks whether colour measured from a phone photo of those sites can tell a health worker whom to "
      "refer for a blood Hb test. It is a screening aid: it decides who gets a test, never the diagnosis.")

ui.spacer(small=True)
ui.section("Datasets")
DATA = [
    ("Eye (primary)", "CP-AnemiC: conjunctiva photos of children aged 6–59 months, Ghana. 220 quality-clean images "
                      "with lab Hb; 93 anaemic at the WHO cut-off of 11 g/dL.",
     "Mendeley Data, doi:10.17632/m53vz6b7fx.1", "https://doi.org/10.17632/m53vz6b7fx.1"),
    ("Nail", "Detection of Anemia using Colour of the Fingernails Image Datasets from Ghana. Children 5 years and "
             "under; 530 original images after removing rotated copies. Labels from file names, no Hb.",
     "Mendeley Data, 2xx4j3kjg2", "https://data.mendeley.com/datasets/2xx4j3kjg2"),
    ("Palm", "Anemia Detection using Palpable Palm Image Datasets from Ghana (same group). 522 original images. "
             "Labels from file names, no Hb.", "Mendeley Data (search the title)", "https://data.mendeley.com"),
    ("Eye, secondary", "Application of Machine Learning in Detecting Iron Deficiency Anemia Using Conjunctiva Image "
                       "Dataset from Ghana (same group). It contains 220 of the CP-AnemiC images; only its other 274 "
                       "images are used, as a separate folder-label analysis.",
     "Mendeley Data (search the title)", "https://data.mendeley.com"),
]
rows = "".join(f'<tr><th scope="row">{html.escape(a)}</th><td>{html.escape(b)}</td>'
               f'<td><a href="{u}" target="_blank" rel="noopener">{html.escape(c)}</a></td></tr>' for a, b, c, u in DATA)
st.html(f'<div class="nh-table-wrap"><table class="nh-table nh-table-text"><thead><tr><th scope="col">Site</th>'
        f'<th scope="col">Dataset</th><th scope="col">Source</th></tr></thead><tbody>{rows}</tbody></table></div>'
        '<p class="nh-note">File-name ("folder") labels agree with WHO Hb labels on 97.3% of the images the Ghana and '
        'CP-AnemiC sets share, so about 3% label noise. About 88% of the Ghana files are rotated or exact copies; only '
        'originals are used, and near-duplicate re-crops share a cross-validation group. Indian adult data (IEEE '
        'DataPort) is pending, so nothing here has been tested on Indian patients yet.</p>')

ui.spacer(small=True)
ui.section("Method")
prose("Each photo is masked to the tissue, with glare, background and (for the eye) dark makeup or lash pixels "
      "removed. From the remaining pixels we compute 23 colour statistics: medians and percentiles of RGB, "
      "chromaticity, CIELAB, HSV, the erythema index and a*/L*. A label-free redundancy filter, fitted inside each "
      "training fold, keeps at most 15.",
      "Evaluation is repeated, stratified, patient-grouped cross-validation: 5 repeats × 5 folds. Everything that "
      "learns from data (scaling, SMOTE, feature pruning, calibration, the threshold) is fitted inside the training "
      "fold only. The headline is the mean over 25 held-out folds with a 95% corrected interval. The threshold is "
      "chosen for at least 80% sensitivity, because a missed anaemic child costs more than an extra blood test.")
UNITS = [
    ("I", "Intelligent agents; BFS, IDDFS", "The screener as an agent; exhaustive protocol search as ground truth"),
    ("II", "Hill climbing, simulated annealing, local beam, genetic algorithm, A*",
     "Cheapest screening protocol search (Insights, Search)"),
    ("III", "Decision trees, overfitting, model selection", "Gini vs entropy trees, depth curves, nested grouped CV"),
    ("IV", "KNN, Naive Bayes, logistic regression, bagging, boosting, random forest",
     "Classifier comparison and the final soft-voting ensemble (Results); KNN unfamiliar-photo check (Screen)"),
    ("V", "K-means, cluster validity", "Pallor clusters with elbow, silhouette and purity (Insights, Clusters)"),
]
PIPELINE = [("photo", "Photo", "eyelid, palm or nail"), ("mask", "Mask", "tissue only; glare and makeup removed"),
            ("features", "Colour features", "23 statistics, at most 15 kept"),
            ("model", "Model", "soft vote of KNN, AdaBoost, random forest"),
            ("threshold", "Threshold", "set for 80% sensitivity"), ("result", "Result", "Refer for Hb test or Normal")]
arrow = ui.icon("arrow", "nh-pipe-arrow")
steps = arrow.join(f'<div class="nh-pipe-step">{art.img(art.pipeline_node(k, m))}<b>{html.escape(name)}</b>'
                   f'<span>{html.escape(sub)}</span></div>' for k, name, sub in PIPELINE)
st.html(f'<h3 class="nh-sub">{html.escape(ui.t("pipeline_title"))}</h3>'
        f'<p class="nh-takeaway">{html.escape(ui.t("t_pipeline"))}</p><div class="nh-pipeline" role="list">{steps}</div>')
ui.spacer(small=True)
units = "".join(f'<div class="nh-unit"><p class="nh-unit-n">Unit {u}</p><p class="nh-unit-topic">{html.escape(topic)}</p>'
                f'<p class="nh-unit-where">{html.escape(where)}</p></div>' for u, topic, where in UNITS)
st.html(f'<h3 class="nh-sub">{html.escape(ui.t("units_title"))}</h3><p class="nh-takeaway">{html.escape(ui.t("t_units"))}</p>'
        f'<div class="nh-units">{units}</div>'
        '<p class="nh-note">Logistic regression, Naive Bayes, KNN and K-means are also written from scratch in NumPy and '
        'tested against scikit-learn.</p>')

ui.spacer(small=True)
ui.section("Honest results")
final = ui.read_result("final.json")
if final is None:
    ui.missing("results/final.json", "tune_models")
else:
    fm = final["headline"]["fold_mean"]

    def ci(m: str) -> str:
        v = fm[m]
        return f"{v['value']:.2f} (95% interval {v['ci_low']:.2f} to {min(v['ci_high'], 1):.2f})"

    prose(f"The final eye model (a soft vote of KNN, AdaBoost and random forest) reaches ROC-AUC {ci('roc_auc')}, "
          f"sensitivity {ci('sensitivity')} and specificity {ci('specificity')}.",
          "In plain terms: it catches about four in five anaemic children but also sends about four in ten healthy "
          "children for a blood test they did not need. That is a useful pre-filter, not a replacement for the test. "
          "The intervals are wide because 220 children is a small sample.",
          "Palm and nail look similar on their own data, but they use different children and folder labels, so they "
          "are not a fair comparison with the eye (see Insights).")

ui.spacer(small=True)
ui.known_limits()
ui.spacer(small=True)
st.html('<aside class="nh-disclaimer"><h4>Not a diagnosis</h4><p>Netra-Hb is a student research prototype and a '
        'screening aid for health workers. It does not diagnose anaemia or measure haemoglobin. Every "Refer" and '
        'every concern must be confirmed with a blood Hb test.</p></aside>')
ui.footer()
