import html

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sklearn.metrics import roc_curve

import ui

ui.setup_page("Results", "pages/2_Results.py")
ui.page_title("Results", "Eye model on 220 children with lab Hb (CP-AnemiC), tested with 5 x 5 repeated, "
                         "patient-grouped cross-validation. Every number comes from children the model did not see.")

NAMES = {"soft_vote_top3": "Soft vote of top 3 (final)", "random_forest": "Random forest", "adaboost": "AdaBoost",
         "gradient_boosting": "Gradient boosting", "bagging": "Bagging", "knn": "KNN", "logreg": "Logistic regression",
         "gaussian_nb": "Naive Bayes", "decision_tree": "Decision tree"}
METRICS = [("sensitivity", "Sensitivity"), ("specificity", "Specificity"), ("roc_auc", "ROC-AUC"),
           ("pr_auc", "PR-AUC"), ("f1", "F1")]

table = ui.read_csv("results/tuned_table.csv")
oof = ui.read_csv("results/oof_tuned.csv")
if table is None or oof is None:
    ui.missing("results/tuned_table.csv and oof_tuned.csv", "tune_models")
    ui.footer()
    st.stop()

# ---------------------------------------------------------------- comparison table
ui.section("Model comparison", "Tuned inside each training fold, calibrated, with the threshold set for at least "
                               "80% sensitivity on inner folds. Mean over 25 held-out folds, 95% corrected interval.")
after = table[(table.stage == "after") & table.model.isin(NAMES)].copy()
after["order"] = after.model.map(list(NAMES).index)
rows = []
for _, r in after.sort_values("order").iterrows():
    cells = "".join(f'<td><span class="nh-num">{r[m]:.2f}</span><span class="nh-ci">{r[m + "_ci"]}</span></td>'
                    for m, _ in METRICS)
    cls = ' class="nh-row-final"' if r.model == "soft_vote_top3" else ""
    rows.append(f"<tr{cls}><th scope=\"row\">{html.escape(NAMES[r.model])}</th>{cells}</tr>")
head = "".join(f'<th scope="col">{label}</th>' for _, label in METRICS)
best = after.loc[after.roc_auc.idxmax()]
st.html(f'<p class="nh-takeaway">No model is far ahead: the best ROC-AUC is {best.roc_auc:.2f} '
        f'({html.escape(NAMES[best.model])}), and the intervals overlap.</p>'
        f'<div class="nh-table-wrap"><table class="nh-table"><thead><tr><th scope="col">Model</th>{head}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>'
        '<p class="nh-note">Small figure under each number: 95% interval over folds. Accuracy is not shown on '
        'purpose: with 42% anaemic it hides the trade-off below.</p>')

# ---------------------------------------------------------------- trade-off
ui.spacer()
ui.section("How sure is it?", "Pick a model and move the threshold. Higher thresholds send fewer healthy children "
                              "for a test, and miss more anaemic ones.")
models = [m for m in NAMES if m in set(oof.model)]
c1, c2 = st.columns([1, 1.6], gap="large")
with c1:
    model = st.selectbox("Model", models, format_func=NAMES.get, key="res_model")
d = oof[(oof.model == model) & (oof.repeat == 0)]
y, p = d["label"].to_numpy(), d["proba"].to_numpy()
default = float(np.round(d["threshold"].median(), 2))
with c2:
    thr = st.slider("Threshold", 0.0, 1.0, default, 0.01, key=f"res_thr_{model}",
                    help="Refer when the model's chance is at or above this. The default is the median of the "
                         "thresholds the model learned inside its training folds.")

pred = p >= thr
tp, fn = int((pred & (y == 1)).sum()), int((~pred & (y == 1)).sum())
fp, tn = int((pred & (y == 0)).sum()), int((~pred & (y == 0)).sum())
sens, spec = tp / max(tp + fn, 1), tn / max(tn + fp, 1)

n_an = round(100 * y.mean())
caught = round(n_an * sens)
false_ref = round((100 - n_an) * (1 - spec))
cells = (["caught"] * caught + ["missed"] * (n_an - caught) + ["sent"] * false_ref
         + ["cleared"] * (100 - n_an - false_ref))
grid = "".join(f'<span class="nh-kid {c}"></span>' for c in cells)
st.html(
    f'<p class="nh-takeaway">Out of 100 children screened: {n_an} anaemic, {caught} caught, {n_an - caught} missed; '
    f'{100 - n_an} healthy, {false_ref} sent for a test they didn\'t need.</p>'
    f'<div class="nh-grid-wrap"><div class="nh-kids" role="img" aria-label="100 children: {caught} anaemic caught, '
    f'{n_an - caught} missed, {false_ref} healthy sent for a test, {100 - n_an - false_ref} healthy cleared">{grid}</div>'
    '<ul class="nh-legend">'
    f'<li><span class="nh-kid caught"></span>Anaemic, referred ({caught})</li>'
    f'<li><span class="nh-kid missed"></span>Anaemic, missed ({n_an - caught})</li>'
    f'<li><span class="nh-kid sent"></span>Healthy, sent for a test ({false_ref})</li>'
    f'<li><span class="nh-kid cleared"></span>Healthy, cleared ({100 - n_an - false_ref})</li></ul></div>'
    f'<p class="nh-note">Sensitivity {sens:.0%}, specificity {spec:.0%} at threshold {thr:.2f}, from the first '
    'repeat\'s pooled out-of-fold predictions (220 children), scaled to 100.</p>')

ui.spacer(small=True)
left, right = st.columns(2, gap="large")
with left:
    fpr, tpr, _ = roc_curve(y, p)
    auc = float(np.trapezoid(tpr, fpr))
    fig = go.Figure()
    fig.add_scatter(x=[0, 1], y=[0, 1], mode="lines", line=dict(color=ui.LIGHT["line"], dash="dot"), name="Chance",
                    hoverinfo="skip")
    fig.add_scatter(x=fpr, y=tpr, mode="lines", line=dict(color=ui.INK, width=2.5), name=f"ROC (AUC {auc:.2f})")
    fig.add_scatter(x=[1 - spec], y=[sens], mode="markers", marker=dict(color=ui.HAEM, size=14,
                    line=dict(color="white", width=2)), name="This threshold")
    fig.update_layout(xaxis_title="Healthy children sent for a test (1 − specificity)",
                      yaxis_title="Anaemic children caught (sensitivity)", xaxis_range=[0, 1], yaxis_range=[0, 1.02])
    ui.chart(fig, f"The red dot is this threshold on the full trade-off curve; AUC {auc:.2f} means an anaemic child "
                  f"outscores a healthy one {auc:.0%} of the time.", height=420, key="res_roc")
with right:
    z = [[tp, fn], [fp, tn]]
    text = [[f"{tp}<br>caught", f"{fn}<br>missed"], [f"{fp}<br>sent for a test", f"{tn}<br>cleared"]]
    fig = go.Figure(go.Heatmap(z=[[1, 0.25], [0.25, 1]], x=["Refer", "Normal"], y=["Anaemic", "Healthy"], text=text,
                               texttemplate="%{text}", textfont=dict(size=18), showscale=False, hoverinfo="skip",
                               colorscale=[[0, "#FFFFFF"], [1, "#E4E8EE"]], xgap=4, ygap=4))
    fig.update_yaxes(autorange="reversed", title="Truth (lab Hb)", showline=False, ticks="")
    fig.update_xaxes(title="Model says", side="top", showline=False, ticks="")
    ui.chart(fig, f"Counts for all {len(y)} children at this threshold: {fn} anaemic children would be missed.",
             height=420, key="res_cm")

ui.footer()
