import gzip
import html
import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy.stats import spearmanr

import ui

ui.setup_page("Insights", "pages/3_Insights.py")
ui.page_title("Insights", "What the data looks like, how the three body sites compare, what clustering finds, and "
                          "what the protocol search learned.")

SITE_STYLE = {"eye": (ui.INK, "solid", "Eye (CP-AnemiC, Hb labels)"), "palm": (ui.SLATE, "solid", "Palm (folder labels)"),
              "nail": ("#8C95A6", "dash", "Nail (folder labels)"),
              "eye_extra": ("#B4BBC8", "dot", "Eye, Ghana extra (secondary)")}
FEATURE_WORDS = {"lab_a_med": "redness (a*)", "lab_L_med": "lightness (L*)", "erythema_index_med": "erythema index",
                 "chrom_r_med": "red share", "a_over_L_med": "redness per lightness (a*/L*)", "R_med": "red channel",
                 "hsv_s_med": "saturation", "lab_b_med": "yellowness (b*)", "chrom_g_med": "green share",
                 "hsv_h_med": "hue"}
tab_data, tab_sites, tab_clusters, tab_search = st.tabs(["Data", "Eye vs palm vs nail", "Clusters", "Search"])


def table_html(df: pd.DataFrame, num_cols: tuple[str, ...] = ()) -> str:
    head = "".join(f'<th scope="col">{html.escape(c)}</th>' for c in df.columns)
    body = "".join("<tr>" + "".join(
        f'<td{" class=nh-numcell" if c in num_cols else ""}>{html.escape(str(v))}</td>' for c, v in r.items()) + "</tr>"
        for _, r in df.iterrows())
    return f'<div class="nh-table-wrap"><table class="nh-table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


# ================================================================= Data
with tab_data:
    df = ui.read_csv("features_cp_anemic.csv")
    if df is None:
        ui.missing("features_cp_anemic.csv", "extract_features")
    else:
        ui.section("The eye data", f"CP-AnemiC primary set: {len(df)} quality-clean conjunctiva photos of children "
                                   "aged 6–59 months in Ghana, each with a lab Hb value.")
        left, right = st.columns(2, gap="large")
        with left:
            order = ["normal", "mild", "moderate", "severe"]
            counts = df.severity.value_counts().reindex(order, fill_value=0)
            colours = [ui.CLEAR, ui.STRIP_STOPS[2], ui.STRIP_STOPS[3], ui.STRIP_STOPS[4]]
            fig = go.Figure(go.Bar(x=[o.capitalize() for o in order], y=counts.values, marker_color=colours,
                                   text=counts.values, textposition="outside", cliponaxis=False))
            fig.update_layout(yaxis_title="Children", showlegend=False)
            n_an = int((df.label == 1).sum())
            ui.chart(fig, f"{n_an} of {len(df)} children ({n_an / len(df):.0%}) are anaemic (Hb below 11 g/dL), so the "
                          "classes are fairly balanced; most anaemia is mild or moderate.", height=360, key="eda_balance")
        with right:
            fig = go.Figure()
            for lab, name in ((0, "Not anaemic"), (1, "Anaemic")):
                fig.add_histogram(x=df.hb[df.label == lab], name=name, marker_color=ui.class_color(bool(lab)),
                                  xbins=dict(start=4, end=15.5, size=0.5), opacity=0.9)
            fig.add_vline(x=11, line=dict(color=ui.INK, width=2), annotation_text="WHO cut-off 11 g/dL",
                          annotation_position="top")
            fig.update_layout(barmode="stack", xaxis_title="Lab Hb, g/dL", yaxis_title="Children")
            ui.chart(fig, f"Hb runs from {df.hb.min():.1f} to {df.hb.max():.1f} g/dL; many children sit close to the "
                          "cut-off, which is where colour screening is hardest.", height=360, key="eda_hb")

        ui.spacer(small=True)
        feats = [f for f in FEATURE_WORDS if f in df.columns]
        rho = {f: spearmanr(df[f], df.hb)[0] for f in feats}
        best = max(rho, key=lambda f: abs(rho[f]))
        left, right = st.columns([1, 1], gap="large")
        with left:
            feat = st.selectbox("Feature", feats, index=feats.index(best), format_func=FEATURE_WORDS.get,
                                key="eda_feat")
            r = rho[feat]
            fig = go.Figure()
            for lab, name in ((0, "Not anaemic"), (1, "Anaemic")):
                s = df[df.label == lab]
                fig.add_scatter(x=s[feat], y=s.hb, mode="markers", name=name,
                                marker=dict(color=ui.class_color(bool(lab)), size=8, opacity=0.75,
                                            line=dict(color="white", width=0.5)))
            fig.add_hline(y=11, line=dict(color=ui.INK, width=1, dash="dot"))
            fig.update_layout(xaxis_title=FEATURE_WORDS[feat].capitalize(), yaxis_title="Lab Hb, g/dL")
            strength = "weak" if abs(r) < 0.3 else "moderate" if abs(r) < 0.5 else "strong"
            ui.chart(fig, f"{FEATURE_WORDS[feat].capitalize()} has a {strength} link with Hb (Spearman ρ = {r:+.2f}): "
                          "the classes overlap a lot, so no single colour number separates them.", height=400,
                     key="eda_scatter")
        with right:
            pairs = [(f, f"gw_{f}") for f in feats if f"gw_{f}" in df.columns]
            raw = [abs(spearmanr(df[a], df.hb)[0]) for a, _ in pairs]
            gw = [abs(spearmanr(df[b], df.hb)[0]) for _, b in pairs]
            names = [FEATURE_WORDS[a] for a, _ in pairs]
            o = np.argsort(raw)
            fig = go.Figure()
            fig.add_bar(y=[names[i] for i in o], x=[raw[i] for i in o], orientation="h", name="Raw colour",
                        marker_color=ui.INK)
            fig.add_bar(y=[names[i] for i in o], x=[gw[i] for i in o], orientation="h",
                        name="Grey-world corrected", marker_color="#B4BBC8")
            fig.update_layout(barmode="group", xaxis_title="Strength of link with Hb, |Spearman ρ|",
                              margin=dict(l=190))
            weaker = sum(g < r_ for g, r_ in zip(gw, raw))
            drops = sorted(range(len(pairs)), key=lambda i: gw[i] - raw[i])[:2]
            named = " and ".join(f"{names[i]} ({raw[i]:.2f} to {gw[i]:.2f})" for i in drops)
            ui.chart(fig, f"Grey-world lighting correction weakens the link with Hb for {weaker} of {len(pairs)} "
                          f"features, most for {named}: it removes redness along with the light cast, so the model "
                          "keeps raw colour.",
                     height=400, key="eda_gw")


# ================================================================= Sites
with tab_sites:
    sites = ui.read_result("sites.json")
    curves = ui.read_csv("results/sites/curves.csv")
    if sites is None or curves is None:
        ui.missing("results/sites.json", "compare_sites")
    else:
        ui.section("Eye vs palm vs nail", "Each site has its own children and labels: eye uses lab Hb, palm and nail "
                                          "use folder labels from file names (about 3% label noise). Not a fair "
                                          "head-to-head.")
        t = pd.DataFrame(sites["table"])
        t["site"] = t.site.map(lambda s: SITE_STYLE[s][2])
        show = t[["site", "n_images", "pct_anaemic", "roc_auc", "sensitivity", "specificity"]].rename(columns={
            "site": "Site", "n_images": "Images", "pct_anaemic": "Anaemic", "roc_auc": "ROC-AUC [95% CI]",
            "sensitivity": "Sensitivity", "specificity": "Specificity"})
        auc = {r["site"]: float(r["roc_auc"].split()[0]) for r in sites["table"]}
        st.html(f'<p class="nh-takeaway">With all their data, palm ({auc["palm"]:.2f}) edges the eye ({auc["eye"]:.2f}) '
                f'and nail is weakest ({auc["nail"]:.2f}), but palm and nail have more than twice as many photos.</p>'
                + table_html(show, ("Images",)))
        ui.spacer(small=True)
        left, right = st.columns(2, gap="large")
        eq = curves[curves.n_target == 220].groupby("site").roc_auc
        with left:
            m, lo, hi = eq.mean(), eq.quantile(0.025), eq.quantile(0.975)
            order = [s for s in ("eye", "palm", "nail", "eye_extra") if s in m.index]
            fig = go.Figure(go.Bar(
                x=[f"{SITE_STYLE[s][2].split(' (')[0]}<br><b>{m[s]:.2f}</b>" for s in order], y=[m[s] for s in order],
                marker_color=[SITE_STYLE[s][0] for s in order],
                error_y=dict(type="data", symmetric=False, array=[hi[s] - m[s] for s in order],
                             arrayminus=[m[s] - lo[s] for s in order], color=ui.SLATE)))
            fig.add_hline(y=0.5, line=dict(color=ui.LIGHT["line"], dash="dot"))
            fig.update_layout(yaxis_title="ROC-AUC", yaxis_range=[0.4, 1], showlegend=False)
            extra = (f" The secondary Ghana eye set scores {m['eye_extra']:.2f}, but with folder labels and 66% "
                     "anaemic it is not comparable." if "eye_extra" in m.index else "")
            ui.chart(fig, f"At the same 220 photos each, the CP-AnemiC eye ({m['eye']:.2f}) beats palm ({m['palm']:.2f}) "
                          f"and nail ({m['nail']:.2f}): palm's lead above comes from having more data.{extra}", height=380,
                     key="site_equal")
        with right:
            g = curves.groupby(["site", "n_target"]).roc_auc
            mean, q_lo, q_hi = g.mean(), g.quantile(0.1), g.quantile(0.9)
            fig = go.Figure()
            for s in ("eye", "palm", "nail", "eye_extra"):
                if s not in mean.index.get_level_values(0):
                    continue
                colour, dash, name = SITE_STYLE[s]
                x = mean[s].index.to_numpy()
                fig.add_scatter(x=np.r_[x, x[::-1]], y=np.r_[q_hi[s].values, q_lo[s].values[::-1]], fill="toself", mode="lines",
                                fillcolor="rgba(91,100,117,0.10)", line=dict(width=0), hoverinfo="skip",
                                showlegend=False)
                fig.add_scatter(x=x, y=mean[s].values, mode="lines+markers", name=name.split(" (")[0],
                                line=dict(color=colour, dash=dash, width=2.5), marker=dict(size=7))
            fig.update_layout(xaxis_title="Training photos (subsampled by child)", yaxis_title="ROC-AUC")
            ui.chart(fig, "Every site is still improving at its largest size, so more photos would help all three.",
                     height=380, key="site_curves")
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
        ui.section("K-means pallor groups", f"K-means on {len(cl['features'])} scaled colour features of the "
                                            f"{eye['n']} eye photos, without labels. Then we check whether the "
                                            "groups line up with anaemia.")
        scan = pd.DataFrame(eye["scan"])
        scan = scan[scan.kind == "sklearn"]
        left, right = st.columns(2, gap="large")
        with left:
            fig = go.Figure(go.Scatter(x=scan.k, y=scan.sse, mode="lines+markers", line=dict(color=ui.INK, width=2.5),
                                       marker=dict(size=8)))
            fig.add_vline(x=eye["k_elbow"], line=dict(color=ui.SLATE, dash="dot"),
                          annotation_text=f"elbow, k = {eye['k_elbow']}")
            fig.update_layout(xaxis_title="Number of clusters k", yaxis_title="Within-cluster error (SSE)")
            ui.chart(fig, f"The error curve bends at k = {eye['k_elbow']}, so we keep {eye['k_chosen']} groups.",
                     height=340, key="cl_elbow")
        with right:
            fig = go.Figure(go.Scatter(x=scan.k, y=scan.silhouette, mode="lines+markers",
                                       line=dict(color=ui.SLATE, width=2.5), marker=dict(size=8)))
            fig.update_layout(xaxis_title="Number of clusters k", yaxis_title="Silhouette")
            ui.chart(fig, f"Silhouette peaks at k = {eye['k_silhouette']} and stays low: the colours form a "
                          "continuum, not clean islands.", height=340, key="cl_sil")

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
        differ = (f"Mean Hb does differ between the groups ({p_txt}): {hi_g['pct_anaemic']:.0%} anaemic in the "
                  f"{hi_g['name'].lower()} group vs {lo_g['pct_anaemic']:.0%} in the {lo_g['name'].lower()} group."
                  if p_hb < 0.05 else f"Mean Hb does not differ clearly between the groups ({p_txt}).")
        purity = (f" But no group is clean: severity purity {sup['purity']:.2f} equals the majority baseline "
                  f"{sup['majority_baseline']:.2f}, so clusters alone cannot screen."
                  if sup["purity"] <= sup["majority_baseline"] + 0.01 else
                  f" Severity purity {sup['purity']:.2f} vs majority baseline {sup['majority_baseline']:.2f}.")
        st.html(f'<p class="nh-takeaway">{html.escape(differ + purity)}</p><div class="nh-centroids">{tiles}</div>')
        ui.note("Swatches are the cluster centres (median tissue colour), ordered by mean Hb.")
        ui.spacer(small=True)
        rows = []
        for site in ("palm", "nail"):
            b = cl[site]["by_k"]["5"]
            rows.append({"Site": site.capitalize(), "Photos": cl[site]["n"], "Purity": f"{float(b['purity']):.2f}",
                         "Majority baseline": f"{float(b['majority_baseline']):.2f}",
                         "p (vs shuffled labels)": f"{float(b['purity_p_value']):.3f}"})
        beat = [r["Site"].lower() for r in rows if float(r["p (vs shuffled labels)"]) < 0.05]
        miss = [r["Site"].lower() for r in rows if r["Site"].lower() not in beat]
        txt = ("With folder labels, the same 5-group K-means beats the majority baseline on "
               + (" and ".join(beat) if beat else "neither site")
               + (f" but not on {' or '.join(miss)}" if beat and miss else "") + ", and only by a few points.")
        st.html(f'<p class="nh-takeaway">{html.escape(txt)}</p>' + table_html(pd.DataFrame(rows), ("Photos",)))


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
        ui.section("Cheapest screening protocol", "Search over site plus up to 3 colour features. Score = specificity "
                                                  "at 80% sensitivity, minus a cost per photo and per feature.")
        t = pd.DataFrame(se["table"])
        opt = t.best_objective.max()
        show = pd.DataFrame({
            "Algorithm": t.algorithm.map(ALGO), "Best score": t.best_objective.map("{:.3f}".format),
            "Gap to optimum": t.gap_to_optimum.map("{:.3f}".format), "Best protocol": t.best_state,
            "Evaluations": t.evaluations.map("{:,}".format), "Runtime (s)": t.runtime_s.map("{:.1f}".format),
            "Found optimum (10 seeds)": t.optimum_hit_rate_10_seeds.map(lambda v: "" if pd.isna(v) else f"{v:.0%}")})
        fast = t[t.gap_to_optimum == 0].sort_values("evaluations").iloc[0]
        st.html(f'<p class="nh-takeaway">Exhaustive BFS checks {int(t.loc[t.algorithm == "bfs", "evaluations"].iloc[0]):,} '
                f'protocols to find the best ({opt:.3f}); {ALGO[fast.algorithm]} finds the same protocol in a run of '
                f'{int(fast.evaluations):,} evaluations.</p>' + table_html(show, ("Evaluations", "Runtime (s)")))

        ui.spacer(small=True)
        left, right = st.columns([1.3, 1], gap="large")
        with left:
            fig = go.Figure()
            shades = {"hill_climbing": ui.SLATE, "simulated_annealing": "#8C95A6", "local_beam": ui.INK,
                      "genetic": "#B4BBC8", "astar": ui.INK}
            dashes = {"astar": "dot", "genetic": "dash"}
            for algo in shades:
                ev = convergence(algo)
                if ev is None:
                    continue
                fig.add_scatter(x=ev["eval"] + 1, y=ev.best_objective, mode="lines", line_shape="hv",
                                name=ALGO[algo], line=dict(color=shades[algo], width=2.5, dash=dashes.get(algo)))
            fig.add_hline(y=opt, line=dict(color=ui.HAEM, width=1.5, dash="dot"), annotation_text="optimum (BFS)",
                          annotation_position="bottom right")
            fig.update_layout(xaxis_type="log", xaxis_title="Protocols evaluated (log scale)",
                              yaxis_title="Best score so far")
            n_bfs = int(t.loc[t.algorithm == "bfs", "evaluations"].iloc[0])
            hit = convergence("local_beam")
            hit = hit[hit.best_objective >= opt - 1e-9]
            msg = (f"Local beam reaches the exhaustive optimum after {int(hit['eval'].iloc[0]) + 1:,} evaluations, "
                   f"{(int(hit['eval'].iloc[0]) + 1) / n_bfs:.0%} of BFS's {n_bfs:,}" if len(hit) else
                   "Local beam does not reach the exhaustive optimum on this seed")
            ui.chart(fig, msg + "; hill climbing, annealing and the genetic algorithm stop slightly below it.",
                     height=400, key="search_conv")
        with right:
            n = se["nested"]["summary"]
            fig = go.Figure(go.Bar(x=["Search score<br>(inner folds)", "Honest score<br>(held-out folds)"],
                                   y=[n["inner_metric"], n["outer_metric"]], marker_color=[ui.SLATE, ui.INK],
                                   text=[f"{n['inner_metric']:.2f}", f"{n['outer_metric']:.2f}"],
                                   textposition="outside", cliponaxis=False, width=0.5))
            fig.update_layout(yaxis_title="Specificity at 80% sensitivity", yaxis_range=[0, 0.65], showlegend=False)
            ui.chart(fig, f"Rerun inside each training fold and scored on held-out children, the winning protocol "
                          f"drops from {n['inner_metric']:.2f} to {n['outer_metric']:.2f}: picking the best of "
                          "thousands flatters the score.", height=400, key="search_nested")
        ui.note(f"Honest re-evaluation: 5 grouped outer folds; the full {ALGO[se['nested']['algo']]} search reruns "
                f"inside each. Held-out ROC-AUC {n['outer_roc_auc']:.2f}, sensitivity {n['outer_sensitivity']:.0%}, "
                f"specificity {n['outer_specificity']:.0%}. Sites chosen per fold: "
                + ", ".join(f"{k} {v} of 5" for k, v in n["sites_chosen"].items()) + ".")

ui.footer()
