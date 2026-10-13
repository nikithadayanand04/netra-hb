import argparse
import json
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from sklearn.model_selection import StratifiedGroupKFold

import config
from netra.search import ALGORITHMS, FUSION, STOCHASTIC, Evaluator, SiteData, nested_search, photo_cost, resub_upper, run_search
from scripts.compare_sites import COLS, SITES, pair_frame

RESULTS = config.OUT_DIR / "results"
SEARCH_DIR = RESULTS / "search"
FIG_DIR = config.OUT_DIR / "figures" / "search"
SURFACE, INK, INK_2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
COLOUR = dict(zip(ALGORITHMS, ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]))
N_SEEDS = 10   # stochastic algorithms: robustness over seeds SEED .. SEED + N_SEEDS - 1
WEIGHTS = (0.0, 0.01, 0.02, 0.05, 0.1)


# ---------- data: each site its own dataset; palm/nail/fusion share linked groups ----------
def linked_groups(palm: pd.DataFrame, nail: pd.DataFrame, pairs: pd.DataFrame) -> dict[str, str]:
    """Palm and nail cv_groups joined through every fused pair: one 'super-group' per connected component, so a
    palm image, its paired nail image and the fused row always land in the same fold."""
    ids, names = pd.factorize(pd.concat([palm["cv_group"], nail["cv_group"]]).astype(str))
    lookup = {n: i for i, n in enumerate(names)}
    a = [lookup[g] for g in pairs["cv_group_palm"].astype(str)]
    b = [lookup[g] for g in pairs["cv_group_nail"].astype(str)]
    adj = coo_matrix((np.ones(len(a)), (a, b)), shape=(len(names),) * 2)
    comp = connected_components(adj, directed=False)[1]
    return {n: f"link:{comp[i]}" for i, n in enumerate(names)}


def load_sites(shift: int = 0) -> tuple[dict[str, SiteData], dict[str, pd.DataFrame]]:
    frames = {s: pd.read_csv(SITES[s]["csv"]).reset_index(drop=True) for s in ("eye", "palm", "nail")}
    pairs = pair_frame(shift)
    link = linked_groups(frames["palm"], frames["nail"], pairs)
    frames[FUSION] = pairs
    out = {}
    for s, df in frames.items():
        if s == FUSION:
            X = df[[f"{c}_palm" for c in COLS] + [f"{c}_nail" for c in COLS]].to_numpy(float)
            g = df["cv_group_palm"].astype(str).map(link).to_numpy()
            names = [f"palm:{c}" for c in COLS] + [f"nail:{c}" for c in COLS]
        else:
            X, names = df[COLS].to_numpy(float), list(COLS)
            g = df["cv_group"].astype(str).map(link).fillna(df["cv_group"].astype(str)).to_numpy()
        out[s] = SiteData(X, df["label"].to_numpy(), g, names)
    return out, frames


def outer_folds(sites: dict[str, SiteData]) -> dict[str, np.ndarray]:
    """1 x 5 grouped outer split. Eye alone; palm + nail rows split together by super-group, fused rows follow."""
    cv = StratifiedGroupKFold(n_splits=config.SEARCH_OUTER_FOLDS, shuffle=True, random_state=config.SEED)
    out = {"eye": np.full(len(sites["eye"].y), -1)}
    for k, (_, te) in enumerate(cv.split(sites["eye"].X, sites["eye"].y, sites["eye"].groups)):
        out["eye"][te] = k
    g = np.concatenate([sites["palm"].groups, sites["nail"].groups])
    y = np.concatenate([sites["palm"].y, sites["nail"].y])
    fold_of = {}
    for k, (_, te) in enumerate(cv.split(np.zeros(len(y)), y, g)):
        fold_of.update(dict.fromkeys(g[te], k))
    for s in ("palm", "nail", FUSION):
        out[s] = np.array([fold_of[x] for x in sites[s].groups])
    return out


# ---------- 1. compare all algorithms on the full data ----------
def run_compare() -> None:
    sites, _ = load_sites()
    print(f"  metric {config.SEARCH_METRIC}, states (<= {config.SEARCH_MAX_FEATURES} features): "
          + ", ".join(f"{s} n={len(d.y)} ({d.y.mean():.0%} anaemic) {len(d.names)} feats" for s, d in sites.items()),
          flush=True)
    rows = []
    for algo in ALGORITHMS:
        res, ev = run_search(algo, sites)
        (RESULTS / f"search_trace_{algo}.json").write_text(json.dumps({"meta": res, **ev.trace()}))
        rows.append(res)
        print(f"  {algo:<20} best {res['best_objective']:.4f} ({res['best_site']}: {', '.join(res['best_features'])})"
              f"  metric {res['best_metric']:.3f}  evals {res['evaluations']}  requests {res['requests']}  "
              f"{res['runtime_s']:.1f}s", flush=True)
    opt = rows[0]["best_objective"]
    for r in rows:
        if r["algo"] in STOCHASTIC:
            runs = [r] + [run_search(r["algo"], sites, seed=config.SEED + i)[0] for i in range(1, N_SEEDS)]
            best = np.array([x["best_objective"] for x in runs])
            r["seeds"] = {"n": N_SEEDS, "hit_rate": float(np.mean(best >= opt - 1e-9)), "mean_best": float(best.mean()),
                          "worst_best": float(best.min()), "mean_evaluations": float(np.mean([x["evaluations"] for x in runs]))}
            print(f"  {r['algo']:<20} over {N_SEEDS} seeds: optimum found {r['seeds']['hit_rate']:.0%}, mean best "
                  f"{best.mean():.4f}, worst {best.min():.4f}, mean evals {r['seeds']['mean_evaluations']:.0f}", flush=True)
    (SEARCH_DIR / "compare.json").write_text(json.dumps(rows, indent=2))


def winner(rows: list[dict]) -> dict:
    top = max(r["best_objective"] for r in rows)
    return min((r for r in rows if r["best_objective"] >= top - 1e-9), key=lambda r: r["evaluations"])


# ---------- 2. checks on the exhaustive table: weight sensitivity, A* admissibility, fusion shift control ----------
def run_checks() -> None:
    bfs = json.loads((RESULTS / "search_trace_bfs.json").read_text())
    tab = pd.DataFrame(bfs["evaluations"], columns=bfs["columns"])
    tab["features"] = [[bfs["feature_names"][s][i] for i in f] for s, f in zip(tab["site"], tab["features"])]
    tab["n_feat"] = tab["features"].str.len()
    out = {"cost_weight_sensitivity": [], "per_site_best": {}, "astar_admissibility": {}, "fusion_shift_control": {}}
    for w in WEIGHTS:
        obj = tab["metric"] - w * tab["site"].map(photo_cost) - config.FEATURE_COST * tab["n_feat"]
        b = tab.loc[obj.idxmax()]
        out["cost_weight_sensitivity"].append({"photo_cost_weight": w, "site": b["site"], "features": b["features"],
                                               "metric": b["metric"], "objective": float(obj.max())})
    sites, _ = load_sites()
    for s, d in tab.groupby("site"):
        b = d.loc[d["objective"].idxmax()]
        ub = resub_upper(sites[s], config.SEARCH_METRIC)
        out["per_site_best"][s] = {"features": b["features"], "metric": b["metric"], "objective": b["objective"]}
        out["astar_admissibility"][s] = {"upper_bound": ub, "max_cv_metric": float(d["metric"].max()),
                                         "admissible": bool(ub >= d["metric"].max())}
    best_fusion = (FUSION, tuple(sites[FUSION].names.index(f) for f in out["per_site_best"][FUSION]["features"]))
    for shift in config.FUSION_SHIFTS:
        sh, _ = load_sites(shift)
        ev = Evaluator({FUSION: sh[FUSION]})
        out["fusion_shift_control"][str(shift)] = {"n_pairs": int(len(sh[FUSION].y)),
                                                   "metric": ev.metric_of(best_fusion)}
    (SEARCH_DIR / "checks.json").write_text(json.dumps(out, indent=2, default=str))
    for r in out["cost_weight_sensitivity"]:
        print(f"  photo weight {r['photo_cost_weight']:.2f}: {r['site']} {r['features']} metric {r['metric']:.3f}")
    for s, a in out["astar_admissibility"].items():
        print(f"  A* bound {s:<10} {a['upper_bound']:.3f} >= max CV metric {a['max_cv_metric']:.3f}: {a['admissible']}")
    print("  best fusion state under shift control: " + ", ".join(
        f"{int(k):+d} -> {v['metric']:.3f}" for k, v in out["fusion_shift_control"].items()))


# ---------- 3. honest re-evaluation of the winning algorithm ----------
def run_nested() -> None:
    rows = json.loads((SEARCH_DIR / "compare.json").read_text())
    algo = winner(rows)["algo"]
    sites, _ = load_sites()
    outer = outer_folds(sites)
    folds = nested_search(algo, sites, outer)
    for f in folds:
        print(f"  fold {f['fold']}: {f['site']} {f['features']}  inner {f['inner_metric']:.3f} -> outer "
              f"{f['outer_metric']:.3f}  (sens {f['outer_sensitivity']:.2f} spec {f['outer_specificity']:.2f} "
              f"AUC {f['outer_roc_auc']:.3f}, n={f['n_test']})", flush=True)
    per_site = {}
    for s in sites:      # control: the same nested search restricted to one site, to see if the site choice holds
        f = nested_search(algo, {s: sites[s]}, {s: outer[s]})
        per_site[s] = {k: float(np.mean([x[k] for x in f])) for k in
                       ("inner_metric", "outer_metric", "outer_objective", "outer_roc_auc", "outer_sensitivity",
                        "outer_specificity")}
        per_site[s]["outer_metric_sd"] = float(np.std([x["outer_metric"] for x in f], ddof=1))
        per_site[s]["features_per_fold"] = [x["features"] for x in f]
        print(f"  {s}-only: inner {per_site[s]['inner_metric']:.3f} -> outer {per_site[s]['outer_metric']:.3f} "
              f"(sd {per_site[s]['outer_metric_sd']:.3f}), outer objective {per_site[s]['outer_objective']:.3f}, "
              f"AUC {per_site[s]['outer_roc_auc']:.3f}", flush=True)
    (SEARCH_DIR / "nested.json").write_text(json.dumps({"algo": algo, "folds": folds, "per_site": per_site}, indent=2))


# ---------- 4. table, figures, search.json ----------
def _style(ax) -> None:
    ax.set_facecolor(SURFACE)
    ax.grid(color=GRID, lw=0.6)
    ax.tick_params(labelsize=7, colors=INK_2, length=0)
    for side in ax.spines.values():
        side.set_visible(False)


def _best_curve(algo: str) -> np.ndarray:
    tr = json.loads((RESULTS / f"search_trace_{algo}.json").read_text())
    return np.array([[r[0] + 1, r[5]] for r in tr["evaluations"]])


def plot_convergence(path) -> None:
    curves = {a: _best_curve(a) for a in ALGORITHMS}
    opt = curves["bfs"][-1, 1]
    lo = np.floor(min(c[0, 1] for c in curves.values()) * 20) / 20
    fig, axes = plt.subplots(2, 4, figsize=(10, 4.8), dpi=200, facecolor=SURFACE, sharex=True, sharey=True)
    for ax, algo in zip(axes.flat, ALGORITHMS):
        _style(ax)
        for other, c in curves.items():
            if other != algo:
                ax.step(c[:, 0], c[:, 1], where="post", color=GRID, lw=1)
        c = curves[algo]
        ax.axhline(opt, color=INK_2, lw=1, ls=(0, (1, 2)))
        ax.step(c[:, 0], c[:, 1], where="post", color=COLOUR[algo], lw=2)
        ax.plot(c[-1, 0], c[-1, 1], "o", ms=6, color=COLOUR[algo], mec=SURFACE, mew=2)
        ax.annotate(f"{c[-1, 1]:.3f} @ {int(c[-1, 0]):,}", (c[-1, 0], c[-1, 1]), xytext=(-4, -12),
                    textcoords="offset points", ha="right", fontsize=6.5, color=INK)
        ax.set_title(algo.replace("_", " "), loc="left", fontsize=8, color=INK)
        ax.set_xscale("log")
        ax.set_ylim(lo, opt + 0.03)
    for ax in axes[1]:
        ax.set_xlabel("model evaluations (log)", fontsize=7, color=INK_2)
    for ax in axes[:, 0]:
        ax.set_ylabel("best objective so far", fontsize=7, color=INK_2)
    fig.suptitle(f"Convergence ({_metric_label()} - cost). Dotted: exhaustive optimum {opt:.3f}; grey: the other "
                 "algorithms; dot: algorithm stopped", x=0.01, ha="left", fontsize=8, color=INK)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)


def plot_nested(nested: dict, path) -> None:
    folds = nested["folds"]
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(10, 3.6), dpi=200, facecolor=SURFACE, sharey=True,
                                  gridspec_kw={"width_ratios": [5, 4]})
    pts = [(f"fold {f['fold'] + 1}\n{f['site']}, {len(f['features'])} feat", f["inner_metric"], f["outer_metric"])
           for f in folds]
    pts2 = [(f"{s} only", v["inner_metric"], v["outer_metric"]) for s, v in nested["per_site"].items()]
    for a, rows, title in ((ax, pts, f"{nested['algo'].replace('_', ' ')} over all sites, per outer fold"),
                           (ax2, pts2, "same search restricted to one site (mean of 5 outer folds)")):
        _style(a)
        x = np.arange(len(rows))
        for i, (_, inner, outer) in enumerate(rows):
            a.plot([i, i], [outer, inner], color=GRID, lw=2, zorder=1)
            a.annotate(f"{outer - inner:+.2f}", (i, (inner + outer) / 2), xytext=(5, 0), textcoords="offset points",
                       fontsize=6.5, color=INK_2, va="center")
        a.plot(x, [r[1] for r in rows], "o", ms=8, color=COLOUR[nested["algo"]], mec=SURFACE, mew=2,
               label="search score (inner CV, in-sample)")
        a.plot(x, [r[2] for r in rows], "o", ms=8, color=INK_2, mec=SURFACE, mew=2, label="held-out outer fold")
        a.set_xticks(x, [r[0] for r in rows])
        a.set_xlim(-0.5, len(rows) - 0.5)
        a.set_title(title, loc="left", fontsize=8, color=INK)
    ax.set_ylabel(_metric_label(), fontsize=8, color=INK_2)
    ax.set_ylim(0, 0.62)
    ax.legend(fontsize=7, frameon=False, loc="lower left")
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)


def _metric_label() -> str:
    return (f"specificity at sensitivity >= {config.SENS_FLOOR:.0%}" if config.SEARCH_METRIC == "spec_at_sens"
            else "ROC-AUC")


def run_report() -> None:
    rows = json.loads((SEARCH_DIR / "compare.json").read_text())
    checks = json.loads((SEARCH_DIR / "checks.json").read_text())
    nested = json.loads((SEARCH_DIR / "nested.json").read_text())
    opt = next(r for r in rows if r["algo"] == "bfs")["best_objective"]
    tab = pd.DataFrame([{"algorithm": r["algo"], "best_objective": round(r["best_objective"], 4),
                         "gap_to_optimum": round(opt - r["best_objective"], 4),
                         "best_state": f"{r['best_site']}: {', '.join(r['best_features'])}",
                         "metric": round(r["best_metric"], 3), "evaluations": r["evaluations"],
                         "requests": r["requests"], "runtime_s": round(r["runtime_s"], 1),
                         f"optimum_hit_rate_{N_SEEDS}_seeds": r.get("seeds", {}).get("hit_rate", 1.0 if
                                                         r["best_objective"] >= opt - 1e-9 else 0.0),
                         f"mean_best_{N_SEEDS}_seeds": round(r.get("seeds", {}).get("mean_best", r["best_objective"]), 4)}
                        for r in rows])
    tab.to_csv(RESULTS / "search_table.csv", index=False)
    plot_convergence(FIG_DIR / "convergence.png")
    plot_nested(nested, FIG_DIR / "nested_optimism.png")
    f = nested["folds"]
    summary = {k: float(np.mean([x[k] for x in f])) for k in
               ("inner_metric", "outer_metric", "outer_roc_auc", "outer_sensitivity", "outer_specificity")}
    summary["optimism"] = summary["inner_metric"] - summary["outer_metric"]
    summary["sites_chosen"] = pd.Series([x["site"] for x in f]).value_counts().to_dict()
    out = {"meta": {
        "objective": f"{_metric_label()} (pooled out-of-fold, logistic regression, {config.SEARCH_FOLDS}-fold "
                     f"StratifiedGroupKFold seed {config.SEED}) - {config.PHOTO_COST_WEIGHT} x photo cost "
                     f"{config.PHOTO_COST} (fusion = sum) - {config.FEATURE_COST} x n_features",
        "space": f"site in eye/palm/nail/{FUSION}, 1..{config.SEARCH_MAX_FEATURES} of the site's features "
                 f"({len(COLS)} per single site, {2 * len(COLS)} for fusion)",
        "data": "eye = CP-AnemiC primary (Hb labels, WHO < 11); palm, nail = Ghana (folder labels); palm+nail = "
                "EXPLORATORY simulated fusion pairing palm n with nail n (child identity undocumented). Sites are "
                "different children and label sources, so site choice mixes body site with dataset.",
        "groups": "eye: cv_group; palm/nail/fusion: palm and nail cv_groups merged through fused pairs",
        "evaluations": "distinct states fitted (fresh cache per algorithm); requests = objective calls incl. cache hits",
        "search_score_is_optimistic": "the threshold for the sensitivity floor is read off the same out-of-fold "
                                      "predictions, and the best of thousands of states is reported; see nested"},
        "table": tab.to_dict("records"), "winner": winner(rows)["algo"], "checks": checks,
        "nested": {"algo": nested["algo"], "summary": summary, "folds": f, "per_site_restricted": nested["per_site"],
                   "note": f"1 x {config.SEARCH_OUTER_FOLDS} grouped outer CV; inside each training fold the whole "
                           "search reruns (inner 3-fold CV); the chosen protocol is refit on the training fold, its "
                           "threshold set on inner out-of-fold predictions for the sensitivity floor, then scored on "
                           "the held-out fold. outer_metric uses the same definition as the search score."},
        "figures": {k: str((FIG_DIR / f"{k}.png").relative_to(config.ROOT)) for k in ("convergence", "nested_optimism")},
        "traces": {a: f"outputs/results/search_trace_{a}.json" for a in ALGORITHMS}}
    (RESULTS / "search.json").write_text(json.dumps(out, indent=2, default=str))
    print(tab.to_string(index=False))
    print(f"\nnested ({nested['algo']}): inner {summary['inner_metric']:.3f} -> outer {summary['outer_metric']:.3f} "
          f"(optimism {summary['optimism']:+.3f}); outer AUC {summary['outer_roc_auc']:.3f}, sens "
          f"{summary['outer_sensitivity']:.3f}, spec {summary['outer_specificity']:.3f}; sites {summary['sites_chosen']}")
    for s, v in nested["per_site"].items():
        print(f"  {s}-only search: inner {v['inner_metric']:.3f} -> outer {v['outer_metric']:.3f} "
              f"(objective {v['outer_objective']:.3f}, AUC {v['outer_roc_auc']:.3f})")


STAGES = {"compare": run_compare, "checks": run_checks, "nested": run_nested, "report": run_report}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("stages", nargs="*", help=f"any of {list(STAGES)}; default all")
    args = ap.parse_args()
    if bad := set(args.stages) - set(STAGES):
        ap.error(f"unknown stages {bad}")
    SEARCH_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    for st in args.stages or list(STAGES):
        print(f"[{st}]", flush=True)
        STAGES[st]()
    print(f"total {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
