import html

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sklearn.metrics import roc_curve

import ui

ui.setup_page("nav_results", "pages/2_Results.py")
t = ui.t
ui.page_title(t("res_title"), t("res_lede"))

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
ui.section(t("res_cmp_title"), t("res_cmp_lede"))
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
st.html(f'<p class="nh-takeaway">{html.escape(t("res_cmp_take", auc=f"{best.roc_auc:.2f}", model=NAMES[best.model]))}</p>'
        f'<div class="nh-table-wrap"><table class="nh-table"><thead><tr><th scope="col">Model</th>{head}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>'
        f'<p class="nh-note">{html.escape(t("res_cmp_note"))}</p>')

# ---------------------------------------------------------------- trade-off
ui.spacer()
ui.section(t("res_trade_title"), t("res_trade_lede"))
models = [m for m in NAMES if m in set(oof.model)]
c1, c2 = st.columns([1, 1.6], gap="large")
with c1:
    model = st.selectbox(t("res_model"), models, format_func=NAMES.get, key="res_model")
d = oof[(oof.model == model) & (oof.repeat == 0)]
y, p = d["label"].to_numpy(), d["proba"].to_numpy()
default = float(np.round(d["threshold"].median(), 2))
with c2:
    thr = st.slider(t("res_threshold"), 0.0, 1.0, default, 0.01, key=f"res_thr_{model}", help=t("res_threshold_help"))

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
fpr, tpr, _ = roc_curve(y, p)
auc = float(np.trapezoid(tpr, fpr))
ppv = tp / max(tp + fp, 1)
cards = [("refer", "card_sens", f"{sens:.0%}", "card_sens_sub"), ("normal", "card_spec", f"{spec:.0%}", "card_spec_sub"),
         ("", "card_ppv", f"{round(ppv * 100)}", "card_ppv_sub"), ("", "card_auc", f"{auc:.2f}", "card_auc_sub")]
st.html('<div class="nh-cards">' + "".join(
    f'<div class="nh-card {cls}"><p class="nh-card-label">{html.escape(t(label))}</p><p class="nh-card-num">{val}</p>'
    f'<p class="nh-card-sub">{html.escape(t(sub))}</p></div>' for cls, label, val, sub in cards) + '</div>')
legend = [("caught", caught), ("missed", n_an - caught), ("sent", false_ref), ("cleared", 100 - n_an - false_ref)]
st.html(
    f'<p class="nh-takeaway">{html.escape(t("grid_take", n_an=n_an, caught=caught, missed=n_an - caught, healthy=100 - n_an, sent=false_ref))}</p>'
    f'<div class="nh-grid-wrap"><div class="nh-kids" role="img" aria-label="{html.escape(t("grid_take", n_an=n_an, caught=caught, missed=n_an - caught, healthy=100 - n_an, sent=false_ref))}">{grid}</div>'
    '<ul class="nh-legend">' + "".join(f'<li><span class="nh-kid {k}"></span>{html.escape(t("legend_" + k, n=v))}</li>'
                                       for k, v in legend) + '</ul></div>'
    f'<p class="nh-note">{html.escape(t("grid_note", sens=f"{sens:.0%}", spec=f"{spec:.0%}", thr=f"{thr:.2f}"))}</p>')

ui.spacer(small=True)
left, right = st.columns(2, gap="large")
with left:
    tk = ui.tokens()
    fig = go.Figure()
    fig.add_scatter(x=[0, 1], y=[0, 1], mode="lines", line=dict(color=tk["muted"], dash="dot"), name="Chance",
                    hoverinfo="skip")
    fig.add_scatter(x=fpr, y=tpr, mode="lines", line=dict(color=tk["text"], width=2.5), name=f"ROC (AUC {auc:.2f})")
    fig.add_scatter(x=[1 - spec], y=[sens], mode="markers", marker=dict(color=tk["refer"], size=14,
                    line=dict(color=tk["surface"], width=2)), name="This threshold")
    fig.update_layout(xaxis_title="Healthy children sent for a test (1 − specificity)",
                      yaxis_title="Anaemic children caught (sensitivity)", xaxis_range=[0, 1], yaxis_range=[0, 1.02])
    ui.chart(fig, t("roc_take", auc=f"{auc:.2f}", pct=f"{auc:.0%}"), height=420, key="res_roc")
with right:
    z = [[tp, fn], [fp, tn]]
    text = [[f"{tp}<br>caught", f"{fn}<br>missed"], [f"{fp}<br>sent for a test", f"{tn}<br>cleared"]]
    fig = go.Figure(go.Heatmap(z=[[1, 0.25], [0.25, 1]], x=["Refer", "Normal"], y=["Anaemic", "Healthy"], text=text,
                               texttemplate="%{text}", textfont=dict(size=18, color=tk["text"]), showscale=False, hoverinfo="skip",
                               colorscale=[[0, tk["surface"]], [1, tk["cell"]]], xgap=4, ygap=4))
    fig.update_yaxes(autorange="reversed", title="Truth (lab Hb)", showline=False, ticks="")
    fig.update_xaxes(title="Model says", side="top", showline=False, ticks="")
    ui.chart(fig, t("cm_take", n=len(y), fn=fn),
             height=420, key="res_cm")

ui.footer()
