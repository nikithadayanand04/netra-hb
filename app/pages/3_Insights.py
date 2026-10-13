import gzip
import html
import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy.stats import spearmanr

import art
import ui

ui.setup_page("nav_insights", "pages/3_Insights.py")
t = ui.t
tk = ui.tokens()
m = ui.mode()
ui.page_title(t("ins_title"), t("ins_lede"))

SERIES = tk["series"]   # strong to faint neutral series colours for the active mode
SITE_STYLE = {"eye": (SERIES[0], "solid", "Eye (CP-AnemiC, Hb labels)"), "palm": (SERIES[1], "solid", "Palm (folder labels)"),
              "nail": (SERIES[2], "dash", "Nail (folder labels)"),
              "eye_extra": (SERIES[3], "dot", "Eye, Ghana extra (secondary)")}
FEATURES = ["lab_a_med", "lab_L_med", "erythema_index_med", "chrom_r_med", "a_over_L_med", "R_med", "hsv_s_med",
            "lab_b_med", "chrom_g_med", "hsv_h_med"]
CLUSTER_KEY = {"Pink": "cl_pink", "Pale": "cl_pale", "Very pale": "cl_very_pale", "Red": "cl_red",
               "Intermediate": "cl_intermediate"}


def first_hit(algo: str, target: float) -> int | None:
    """Evaluation index at which a search first reached the target score (from its saved trace)."""
    path = ui.RESULTS_DIR / f"search_trace_{algo}.json.gz"
    if not path.exists():
        return None
    tr = json.loads(gzip.decompress(path.read_bytes()))
    ev = pd.DataFrame(tr["evaluations"], columns=tr["columns"])
    hit = ev[ev.best_objective >= target - 1e-9]
    return int(hit["eval"].min()) + 1 if len(hit) else None


def findings() -> None:
    """Four findings; every number is read from outputs/results, nothing is typed in."""
    cards = []
    curves = ui.read_csv("results/sites/curves.csv")
    if curves is not None:
        eq = curves[curves.n_target == 220].groupby("site").roc_auc.mean()
        cards.append(("sites", (eq["eye"], eq["palm"], eq["nail"]), "f_sites_title",
                      t("f_sites", eye=f"{eq['eye']:.2f}", palm=f"{eq['palm']:.2f}", nail=f"{eq['nail']:.2f}")))
    base, se = ui.read_result("baselines.json"), ui.read_result("search.json")
    if base is not None and se is not None:
        def best(exp: str) -> float:
            return max(v["fold_mean"]["roc_auc"]["value"] for k, v in base["experiments"][exp]["models"].items()
                       if not k.startswith(("all_normal", "scratch")))
        before, after = best("secondary_all"), best("primary")
        n = se["nested"]["summary"]
        cards.append(("honest", (before, after, n["inner_metric"], n["outer_metric"]), "f_honest_title",
                      t("f_honest", q_before=f"{before:.2f}", q_after=f"{after:.2f}", s_before=f"{n['inner_metric']:.2f}",
                        s_after=f"{n['outer_metric']:.2f}")))
    sg = ui.read_result("safeguards.json")
    if sg is not None:
        cards.append(("safeguards", (), "f_safe_title", t("f_safe", fp=f"{sg['makeup']['pixels_wrongly_removed']:.2%}")))
    if se is not None:
        tab = pd.DataFrame(se["table"])
        n_bfs = int(tab.loc[tab.algorithm == "bfs", "evaluations"].iloc[0])
        hit = first_hit("local_beam", tab.best_objective.max())
        if hit:
            cards.append(("search", (n_bfs, hit), "f_search_title", t("f_search", beam=f"{hit:,}", bfs=f"{n_bfs:,}")))
    body = "".join(f'<li class="nh-find-card">{art.img(art.finding(name, m, vals))}<h3>{html.escape(t(title))}</h3>'
                   f'<p>{html.escape(text)}</p></li>' for name, vals, title, text in cards)
    st.html(f'<section class="nh-found"><h2 class="nh-section-title">{html.escape(t("found_title"))}</h2>'
            f'<ul class="nh-find">{body}</ul></section>')


findings()
ui.spacer(small=True)
tab_data, tab_sites, tab_clusters, tab_search = st.tabs([t("tab_data"), t("tab_sites"), t("tab_clusters"), t("tab_search")])


def feat(f: str) -> str:
    return t("feat_" + f)


def table_html(df: pd.DataFrame, num_cols: tuple[str, ...] = ()) -> str:
    head = "".join(f'<th scope="col">{html.escape(c)}</th>' for c in df.columns)
    body = "".join("<tr>" + "".join(
        f'<td{" class=nh-numcell" if c in num_cols else ""}>{html.escape(str(v))}</td>' for c, v in r.items()) + "</tr>"
        for _, r in df.iterrows())
    return f'<div class="nh-table-wrap"><table class="nh-table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def header_art(name: str) -> str:
    return art.img(art.header(name, m))


# ================================================================= Data
with tab_data:
    df = ui.read_csv("features_cp_anemic.csv")
    if df is None:
        ui.missing("features_cp_anemic.csv", "extract_features")
    else:
        ui.section(t("data_title"), t("data_lede", n=len(df)), header_art("data"))
        left, right = st.columns(2, gap="large")
        with left:
            order = ["normal", "mild", "moderate", "severe"]
            counts = df.severity.value_counts().reindex(order, fill_value=0)
            # severity reads as more intense red: darker on light, brighter on dark (the deep strip reds vanish on dark)
            colours = ([tk["normal"], "#9E6070", "#C24161", "#EA6A88"] if ui.is_dark() else
                       [tk["normal"], ui.STRIP_STOPS[2], ui.STRIP_STOPS[3], ui.STRIP_STOPS[4]])
            fig = go.Figure(go.Bar(x=[o.capitalize() for o in order], y=counts.values, marker_color=colours,
                                   text=counts.values, textposition="outside", cliponaxis=False,
                                   textfont=dict(color=tk["text"])))
            fig.update_layout(yaxis_title="Children", showlegend=False)
            n_an = int((df.label == 1).sum())
            ui.chart(fig, t("t_balance", n_an=n_an, n=len(df), pct=f"{n_an / len(df):.0%}"), height=360, key="eda_balance")
        with right:
            fig = go.Figure()
            for lab, name in ((0, "Not anaemic"), (1, "Anaemic")):
                fig.add_histogram(x=df.hb[df.label == lab], name=name, marker_color=ui.class_color(bool(lab)),
                                  xbins=dict(start=4, end=15.5, size=0.5), opacity=0.9)
            fig.add_vline(x=11, line=dict(color=tk["text"], width=2), annotation_text="WHO cut-off 11 g/dL",
                          annotation_position="top")
            fig.update_layout(barmode="stack", xaxis_title="Lab Hb, g/dL", yaxis_title="Children")
            ui.chart(fig, t("t_hb", lo=f"{df.hb.min():.1f}", hi=f"{df.hb.max():.1f}"), height=360, key="eda_hb")

        ui.spacer(small=True)
        feats = [f for f in FEATURES if f in df.columns]
        rho = {f: spearmanr(df[f], df.hb)[0] for f in feats}
        best = max(rho, key=lambda f: abs(rho[f]))
        left, right = st.columns([1, 1], gap="large")
        with left:
            f_sel = st.selectbox("Feature", feats, index=feats.index(best), format_func=feat, key="eda_feat")
            r = rho[f_sel]
            fig = go.Figure()
            for lab, name in ((0, "Not anaemic"), (1, "Anaemic")):
                s = df[df.label == lab]
                fig.add_scatter(x=s[f_sel], y=s.hb, mode="markers", name=name,
                                marker=dict(color=ui.class_color(bool(lab)), size=8, opacity=0.8,
                                            line=dict(color=tk["surface"], width=0.5)))
            fig.add_hline(y=11, line=dict(color=tk["text"], width=1, dash="dot"))
            fig.update_layout(xaxis_title=feat(f_sel).capitalize(), yaxis_title="Lab Hb, g/dL")
            strength = "weak" if abs(r) < 0.3 else "moderate" if abs(r) < 0.5 else "strong"
            ui.chart(fig, t("t_scatter", feat=feat(f_sel).capitalize(), strength=t("strength_" + strength), r=f"{r:+.2f}"),
                     height=400, key="eda_scatter")
        with right:
            pairs = [(f, f"gw_{f}") for f in feats if f"gw_{f}" in df.columns]
            raw = [abs(spearmanr(df[a], df.hb)[0]) for a, _ in pairs]
            gw = [abs(spearmanr(df[b], df.hb)[0]) for _, b in pairs]
            names = [feat(a) for a, _ in pairs]
            o = np.argsort(raw)
            fig = go.Figure()
            fig.add_bar(y=[names[i] for i in o], x=[raw[i] for i in o], orientation="h", name="Raw colour",
                        marker_color=SERIES[0])
            fig.add_bar(y=[names[i] for i in o], x=[gw[i] for i in o], orientation="h",
                        name="Grey-world corrected", marker_color=SERIES[3])
            fig.update_layout(barmode="group", xaxis_title="Strength of link with Hb, |Spearman ρ|", margin=dict(l=200))
            weaker = sum(g < r_ for g, r_ in zip(gw, raw))
            drops = sorted(range(len(pairs)), key=lambda i: gw[i] - raw[i])[:2]
            named = t("and").join(f"{names[i]} ({raw[i]:.2f} → {gw[i]:.2f})" for i in drops)
            ui.chart(fig, t("t_gw", weaker=weaker, n=len(pairs), named=named), height=400, key="eda_gw")


# ================================================================= Sites
with tab_sites:
    sites = ui.read_result("sites.json")
    curves = ui.read_csv("results/sites/curves.csv")
    if sites is None or curves is None:
        ui.missing("results/sites.json", "compare_sites")
    else:
        ui.section(t("sites_title"), t("sites_lede"), header_art("sites"))
        tab = pd.DataFrame(sites["table"])
        tab["site"] = tab.site.map(lambda s: SITE_STYLE[s][2])
        show = tab[["site", "n_images", "pct_anaemic", "roc_auc", "sensitivity", "specificity"]].rename(columns={
            "site": "Site", "n_images": "Images", "pct_anaemic": "Anaemic", "roc_auc": "ROC-AUC [95% CI]",
            "sensitivity": "Sensitivity", "specificity": "Specificity"})
        auc = {r["site"]: float(r["roc_auc"].split()[0]) for r in sites["table"]}
        ranked = sorted(("eye", "palm", "nail"), key=lambda s: -auc[s])
        names = {s: t("site_" + s).lower() for s in ranked}
        st.html(f'<p class="nh-takeaway">{html.escape(t("t_sites_table", first=names[ranked[0]], first_auc=f"{auc[ranked[0]]:.2f}", second=names[ranked[1]], second_auc=f"{auc[ranked[1]]:.2f}", third=names[ranked[2]], third_auc=f"{auc[ranked[2]]:.2f}"))}</p>'
                + table_html(show, ("Images",)))
        ui.spacer(small=True)
        left, right = st.columns(2, gap="large")
        eq = curves[curves.n_target == 220].groupby("site").roc_auc
        with left:
            mean, lo, hi = eq.mean(), eq.quantile(0.025), eq.quantile(0.975)
            order = [s for s in ("eye", "palm", "nail", "eye_extra") if s in mean.index]
            fig = go.Figure(go.Bar(
                x=[f"{SITE_STYLE[s][2].split(' (')[0]}<br><b>{mean[s]:.2f}</b>" for s in order], y=[mean[s] for s in order],
                marker_color=[SITE_STYLE[s][0] for s in order],
                error_y=dict(type="data", symmetric=False, array=[hi[s] - mean[s] for s in order],
                             arrayminus=[mean[s] - lo[s] for s in order], color=tk["muted"])))
            fig.add_hline(y=0.5, line=dict(color=tk["muted"], dash="dot"))
            fig.update_layout(yaxis_title="ROC-AUC", yaxis_range=[0.4, 1], showlegend=False)
            extra = t("t_equal_extra", v=f"{mean['eye_extra']:.2f}") if "eye_extra" in mean.index else ""
            ui.chart(fig, t("t_equal", eye=f"{mean['eye']:.2f}", palm=f"{mean['palm']:.2f}", nail=f"{mean['nail']:.2f}") + extra,
                     height=380, key="site_equal")
        with right:
            g = curves.groupby(["site", "n_target"]).roc_auc
            mean, q_lo, q_hi = g.mean(), g.quantile(0.1), g.quantile(0.9)
            fig = go.Figure()
            band = "rgba(154,163,181,0.14)" if ui.is_dark() else "rgba(91,100,117,0.10)"
            for s in ("eye", "palm", "nail", "eye_extra"):
                if s not in mean.index.get_level_values(0):
                    continue
                colour, dash, name = SITE_STYLE[s]
                x = mean[s].index.to_numpy()
                fig.add_scatter(x=np.r_[x, x[::-1]], y=np.r_[q_hi[s].values, q_lo[s].values[::-1]], fill="toself",
                                mode="lines", fillcolor=band, line=dict(width=0), hoverinfo="skip", showlegend=False)
                fig.add_scatter(x=x, y=mean[s].values, mode="lines+markers", name=name.split(" (")[0],
                                line=dict(color=colour, dash=dash, width=2.5), marker=dict(size=7, color=colour))
            fig.update_layout(xaxis_title="Training photos (subsampled by child)", yaxis_title="ROC-AUC")
            ui.chart(fig, t("t_curves"), height=380, key="site_curves")
        ui.note("Equal-size and learning-curve numbers use one fixed, untuned random forest per site so only the data "
                "changes. Bands: 10th to 90th percentile over 10 subsamples.")


# ================================================================= Clusters
def centroid_rgb(c: dict) -> tuple[int, int, int]:
    r = c["R_med"]
    g = r * c["chrom_g_med"] / c["chrom_r_med"]
    return tuple(int(np.clip(v, 0, 255)) for v in (r, g, c["B_med"]))


with tab_clusters:
    cl = ui.read_result("clustering.json")
    if cl is None:
        ui.missing("results/clustering.json", "the clustering notebook (notebooks/02_clustering.ipynb)")
    else:
        eye = cl["eye"]
        ui.section(t("clusters_title"), t("clusters_lede", k=len(cl["features"]), n=eye["n"]), header_art("clusters"))
        scan = pd.DataFrame(eye["scan"])
        scan = scan[scan.kind == "sklearn"]
        left, right = st.columns(2, gap="large")
        with left:
            fig = go.Figure(go.Scatter(x=scan.k, y=scan.sse, mode="lines+markers",
                                       line=dict(color=SERIES[0], width=2.5), marker=dict(size=8, color=SERIES[0])))
            fig.add_vline(x=eye["k_elbow"], line=dict(color=tk["muted"], dash="dot"),
                          annotation_text=f"elbow, k = {eye['k_elbow']}")
            fig.update_layout(xaxis_title="Number of clusters k", yaxis_title="Within-cluster error (SSE)")
            ui.chart(fig, t("t_elbow", k=eye["k_elbow"]), height=340, key="cl_elbow")
        with right:
            fig = go.Figure(go.Scatter(x=scan.k, y=scan.silhouette, mode="lines+markers",
                                       line=dict(color=SERIES[1], width=2.5), marker=dict(size=8, color=SERIES[1])))
            fig.update_layout(xaxis_title="Number of clusters k", yaxis_title="Silhouette")
            ui.chart(fig, t("t_sil", k=eye["k_silhouette"]), height=340, key="cl_sil")

        ui.spacer(small=True)
        groups = sorted(eye["clusters"][str(eye["k_chosen"])], key=lambda c: c["mean_hb"])
        tiles = "".join(
            f'<div class="nh-centroid"><span class="nh-centroid-swatch" style="background:rgb{centroid_rgb(c["centroid"])}">'
            f'</span><p class="nh-centroid-name">{html.escape(c["name"])}</p>'
            f'<p class="nh-centroid-meta">{c["n"]} children<br>mean Hb {c["mean_hb"]:.1f} g/dL<br>'
            f'{c["pct_anaemic"]:.0%} anaemic</p></div>' for c in groups)
        sup = next(s for s in eye["supervised"] if s["k"] == eye["k_chosen"])
        hi_g, lo_g = max(groups, key=lambda c: c["pct_anaemic"]), min(groups, key=lambda c: c["pct_anaemic"])
        p_hb = sup["kruskal_hb_p"]
        p_txt = "p < 0.001" if p_hb < 0.001 else f"p = {p_hb:.3f}"
        differ = (t("t_cl_differ", p=p_txt, hi_pct=f"{hi_g['pct_anaemic']:.0%}", hi_name=t(CLUSTER_KEY[hi_g["name"]]),
                    lo_pct=f"{lo_g['pct_anaemic']:.0%}", lo_name=t(CLUSTER_KEY[lo_g["name"]]))
                  if p_hb < 0.05 else t("t_cl_nodiffer", p=p_txt))
        same = sup["purity"] <= sup["majority_baseline"] + 0.01
        purity = t("t_cl_purity_same" if same else "t_cl_purity", pur=f"{sup['purity']:.2f}",
                   base=f"{sup['majority_baseline']:.2f}")
        st.html(f'<p class="nh-takeaway">{html.escape(differ + purity)}</p><div class="nh-centroids">{tiles}</div>')
        ui.note("Swatches are the cluster centres (median tissue colour), ordered by mean Hb.")
        ui.spacer(small=True)
        rows = []
        for site in ("palm", "nail"):
            b = cl[site]["by_k"]["5"]
            rows.append({"Site": site.capitalize(), "Photos": cl[site]["n"], "Purity": f"{float(b['purity']):.2f}",
                         "Majority baseline": f"{float(b['majority_baseline']):.2f}",
                         "p (vs shuffled labels)": f"{float(b['purity_p_value']):.3f}"})
        beat = [t("site_" + r["Site"].lower()).lower() for r in rows if float(r["p (vs shuffled labels)"]) < 0.05]
        miss = [t("site_" + r["Site"].lower()).lower() for r in rows if float(r["p (vs shuffled labels)"]) >= 0.05]
        where = (t("t_cl_sites_but", beat=t("and").join(beat), miss=t("and").join(miss)) if beat and miss
                 else t("and").join(beat) if beat else t("t_cl_sites_none"))
        st.html(f'<p class="nh-takeaway">{html.escape(t("t_cl_sites", beat=where))}</p>'
                + table_html(pd.DataFrame(rows), ("Photos",)))


# ================================================================= Search
ALGO = {"bfs": "BFS", "iddfs": "IDDFS", "hill_climbing": "Hill climbing", "simulated_annealing": "Simulated annealing",
        "local_beam": "Local beam", "genetic": "Genetic algorithm", "astar": "A*", "astar_resub": "A* (resubstitution)"}


@st.cache_data(show_spinner=False)
def convergence(algo: str) -> pd.DataFrame | None:
    path = ui.RESULTS_DIR / f"search_trace_{algo}.json.gz"
    if not path.exists():
        return None
    tr = json.loads(gzip.decompress(path.read_bytes()))
    ev = pd.DataFrame(tr["evaluations"], columns=tr["columns"])
    return ev[["eval", "best_objective"]].sort_values("eval")


with tab_search:
    se = ui.read_result("search.json")
    if se is None:
        ui.missing("results/search.json", "run_search")
    else:
        ui.section(t("search_title"), t("search_lede"), header_art("search"))
        st_ = pd.DataFrame(se["table"])
        opt = st_.best_objective.max()
        show = pd.DataFrame({
            "Algorithm": st_.algorithm.map(ALGO), "Best score": st_.best_objective.map("{:.3f}".format),
            "Gap to optimum": st_.gap_to_optimum.map("{:.3f}".format), "Best protocol": st_.best_state,
            "Evaluations": st_.evaluations.map("{:,}".format), "Runtime (s)": st_.runtime_s.map("{:.1f}".format),
            "Found optimum (10 seeds)": st_.optimum_hit_rate_10_seeds.map(lambda v: "" if pd.isna(v) else f"{v:.0%}")})
        fast = st_[st_.gap_to_optimum == 0].sort_values("evaluations").iloc[0]
        n_bfs = int(st_.loc[st_.algorithm == "bfs", "evaluations"].iloc[0])
        st.html(f'<p class="nh-takeaway">{html.escape(t("t_search_table", n=f"{n_bfs:,}", opt=f"{opt:.3f}", algo=ALGO[fast.algorithm], evals=f"{int(fast.evaluations):,}"))}</p>'
                + table_html(show, ("Evaluations", "Runtime (s)")))

        ui.spacer(small=True)
        left, right = st.columns([1.3, 1], gap="large")
        with left:
            fig = go.Figure()
            shades = {"hill_climbing": SERIES[1], "simulated_annealing": SERIES[2], "local_beam": SERIES[0],
                      "genetic": SERIES[3], "astar": SERIES[0]}
            dashes = {"astar": "dot", "genetic": "dash"}
            for algo in shades:
                ev = convergence(algo)
                if ev is None:
                    continue
                fig.add_scatter(x=ev["eval"] + 1, y=ev.best_objective, mode="lines", line_shape="hv",
                                name=ALGO[algo], line=dict(color=shades[algo], width=2.5, dash=dashes.get(algo)))
            fig.add_hline(y=opt, line=dict(color=tk["muted"], width=1.5, dash="dot"), annotation_text="optimum (BFS)",
                          annotation_position="bottom right")
            fig.update_layout(xaxis_type="log", xaxis_title="Protocols evaluated (log scale)", yaxis_title="Best score so far")
            hit = convergence("local_beam")
            hit = hit[hit.best_objective >= opt - 1e-9]
            if len(hit):
                n_hit = int(hit["eval"].iloc[0]) + 1
                msg = t("t_conv", n=f"{n_hit:,}", pct=f"{n_hit / n_bfs:.0%}", bfs=f"{n_bfs:,}")
            else:
                msg = t("t_conv_none")
            ui.chart(fig, msg, height=400, key="search_conv")
        with right:
            n = se["nested"]["summary"]
            fig = go.Figure(go.Bar(x=["Search score<br>(inner folds)", "Honest score<br>(held-out folds)"],
                                   y=[n["inner_metric"], n["outer_metric"]], marker_color=[SERIES[2], SERIES[0]],
                                   text=[f"{n['inner_metric']:.2f}", f"{n['outer_metric']:.2f}"],
                                   textposition="outside", cliponaxis=False, width=0.5, textfont=dict(color=tk["text"])))
            fig.update_layout(yaxis_title="Specificity at 80% sensitivity", yaxis_range=[0, 0.65], showlegend=False)
            ui.chart(fig, t("t_nested", inner=f"{n['inner_metric']:.2f}", outer=f"{n['outer_metric']:.2f}"), height=400,
                     key="search_nested")
        ui.note(f"Honest re-evaluation: 5 grouped outer folds; the full {ALGO[se['nested']['algo']]} search reruns "
                f"inside each. Held-out ROC-AUC {n['outer_roc_auc']:.2f}, sensitivity {n['outer_sensitivity']:.0%}, "
                f"specificity {n['outer_specificity']:.0%}. Sites chosen per fold: "
                + ", ".join(f"{k} {v} of 5" for k, v in n["sites_chosen"].items()) + ".")

ui.footer()
